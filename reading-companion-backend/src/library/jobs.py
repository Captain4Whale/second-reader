"""Background job helpers for uploaded sequential deep-read runs."""

from __future__ import annotations

import hashlib
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .catalog import find_book_id_by_source, source_asset_path
from .runtime_truth import (
    effective_resume_available,
    iter_orphan_active_runs,
    latest_job_for_book,
)
from .storage import (
    job_file,
    job_log_file,
    load_json as load_job_json,
    save_json as save_job_json,
    timestamp,
    upload_file,
)
from src.config import (
    get_backend_boot_id,
    get_backend_run_mode,
    get_backend_version,
    get_reader_resume_compat_version,
)
from src.reading_runtime import default_mechanism_key
from src.reading_runtime.artifacts import existing_runtime_shell_file
from src.reading_runtime.background_job_registry import (
    PRODUCT_RUNTIME_DOMAIN,
    list_job_records,
    load_job_record,
    migrate_product_shadow_jobs,
    save_job_record,
)
from src.reading_runtime.job_lease import (
    JobLeaseConflict,
    JobLeaseGrant,
    acquire_job_lease,
    fence_job_lease,
    guard_job_lease_snapshot,
    heartbeat_job_lease,
    job_lease_is_valid,
    lease_environment,
    load_job_lease,
    process_birth_identity,
    release_job_lease,
    sanitized_lease_metadata,
)
from src.reading_runtime.provisioning import ensure_book_assets, ensure_output_dir, inspect_book
from src.reading_runtime.sequential_state import (
    append_activity_event,
    append_deduped_activity_event,
    build_run_state,
    build_minimal_book_manifest,
    reset_activity,
    write_book_manifest,
    write_run_state,
)
from src.iterator_reader.storage import (
    clear_iterator_private_artifacts,
    chapter_qa_file,
    book_id_from_output_dir,
    existing_activity_file,
    existing_book_manifest_file,
    existing_chapter_markdown_file,
    existing_chapter_result_file,
    existing_parse_state_file,
    existing_run_state_file,
    existing_structure_file,
    legacy_activity_file,
    legacy_book_manifest_file,
    legacy_run_state_file,
    load_json as load_structure_json,
    load_json as load_runtime_json,
    runtime_dir,
    run_history_job_file,
    run_history_job_log_file,
    run_history_summary_file,
    run_history_trace_file,
    save_structure,
)


AUTO_RESUME_LIMIT = 1
ACTIVE_JOB_STATUSES = {"queued", "parsing_structure", "deep_reading", "chapter_note_generation"}
TERMINAL_JOB_STATUSES = {"completed", "error"}
MIN_SUPPORTED_PYTHON = (3, 11)
ACTIVE_RUNTIME_STALE_SECONDS = 45
WORKER_TERMINATION_TIMEOUT_SECONDS = 5.0
WORKER_TERMINATION_POLL_SECONDS = 0.05


def _job_record(
    *,
    job_id: str,
    status: str,
    upload_path: Path,
    job_kind: str,
    mechanism_key: str | None = None,
    language: str = "auto",
    intent: str | None = None,
    resume_count: int = 0,
    auto_resume_count: int = 0,
    book_id: str | None = None,
    memory_retrieval_mode: str | None = None,
    pid: int | None = None,
    run_attempt_id: str | None = None,
    lease: dict[str, object] | None = None,
    error: str | None = None,
    created_at: str | None = None,
) -> dict:
    """Build one persisted job record."""
    now = timestamp()
    return {
        "job_id": job_id,
        "status": status,
        "job_kind": job_kind,
        "mechanism_key": str(mechanism_key or "").strip() or None,
        "upload_path": str(upload_path),
        "book_id": book_id,
        "memory_retrieval_mode": str(memory_retrieval_mode or "").strip() or None,
        "language": language,
        "intent": intent,
        "resume_count": int(resume_count),
        "auto_resume_count": int(auto_resume_count),
        "pid": pid,
        "run_attempt_id": str(run_attempt_id or "").strip() or None,
        "lease": dict(lease or {}),
        "boot_id": get_backend_boot_id(),
        "backend_version": get_backend_version(),
        "resume_compat_version": get_reader_resume_compat_version(),
        "python_executable": sys.executable,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "created_at": created_at or now,
        "updated_at": now,
        "error": error,
    }


def _normalize_record(record: dict) -> dict:
    """Backfill defaults for older job records."""
    status = str(record.get("status", "queued") or "queued")
    job_kind = str(record.get("job_kind", "") or "").strip()
    if not job_kind:
        job_kind = "parse" if status in {"queued", "parsing_structure", "ready"} else "read"
    lease = dict(record.get("lease", {})) if isinstance(record.get("lease"), dict) else {}
    lease.pop("token", None)
    return {
        **record,
        "job_kind": job_kind,
        "mechanism_key": str(record.get("mechanism_key", "") or "").strip() or None,
        "language": str(record.get("language", "auto") or "auto"),
        "intent": str(record.get("intent", "") or "") or None,
        "memory_retrieval_mode": str(record.get("memory_retrieval_mode", "") or "").strip() or None,
        "resume_count": int(record.get("resume_count", 0) or 0),
        "auto_resume_count": int(record.get("auto_resume_count", 0) or 0),
        "run_attempt_id": str(record.get("run_attempt_id", "") or "").strip() or None,
        "lease": lease,
        "boot_id": str(record.get("boot_id", "") or "") or None,
        "backend_version": str(record.get("backend_version", "") or "") or None,
        "resume_compat_version": _resume_compat_version(record.get("resume_compat_version")),
    }


def _process_running(pid: int | None) -> bool:
    """Return whether a subprocess still appears alive."""
    if not pid:
        return False
    try:
        waited_pid, _status = os.waitpid(int(pid), os.WNOHANG)
        if waited_pid == int(pid):
            return False
    except ChildProcessError:
        pass
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        # Permission errors, EINTR, and other probe failures do not prove that
        # the process exited. Resume/fencing must fail closed in that case.
        return True


def _python_runtime_issue() -> str | None:
    """Return a user-facing runtime issue when the current interpreter is unsupported."""
    if sys.version_info < MIN_SUPPORTED_PYTHON:
        return (
            "Background jobs require Python "
            f"{MIN_SUPPORTED_PYTHON[0]}.{MIN_SUPPORTED_PYTHON[1]}+ but the backend is running under "
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} "
            f"({sys.executable})."
        )
    return None


def _resume_compat_version(value: object) -> int | None:
    """Normalize one persisted resume-compat marker."""
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _run_state_resume_compat(run_state: dict | None) -> int | None:
    """Return the resume-compat version recorded in runtime artifacts."""
    return _resume_compat_version((run_state or {}).get("resume_compat_version"))


def _record_resume_compat(record: dict) -> int | None:
    """Return the resume-compat version recorded in the job record."""
    return _resume_compat_version(record.get("resume_compat_version"))


def _resume_compatible(*, record: dict, run_state: dict | None, parse_state: dict | None = None) -> bool:
    """Return whether persisted job/runtime artifacts can be safely resumed."""
    expected = get_reader_resume_compat_version()
    if _record_resume_compat(record) != expected:
        return False

    known_state_versions: list[int | None] = []
    if run_state is not None:
        known_state_versions.append(_run_state_resume_compat(run_state))
    if parse_state is not None:
        known_state_versions.append(_resume_compat_version(parse_state.get("resume_compat_version")))
    if not known_state_versions:
        return True
    return all(version == expected for version in known_state_versions)


def _is_dev_boot_mismatch(record: dict) -> bool:
    """Return whether a job belongs to an older development backend boot."""
    if get_backend_run_mode() != "dev":
        return False
    recorded_boot_id = str(record.get("boot_id", "") or "").strip()
    if not recorded_boot_id:
        return False
    return recorded_boot_id != get_backend_boot_id()


def _parse_timestamp(value: object) -> datetime | None:
    """Parse one UTC timestamp when available."""
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _seconds_since(value: object) -> float | None:
    """Return age in seconds for one persisted timestamp."""
    parsed = _parse_timestamp(value)
    if parsed is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())


def _activity_context(run_state: dict | None) -> dict[str, object]:
    """Extract the recent reading location from run_state."""
    state = run_state or {}
    return {
        "chapter_id": int(state.get("current_chapter_id", 0) or 0) or None,
        "chapter_ref": str(state.get("current_chapter_ref", "") or "") or None,
        "segment_ref": str(state.get("current_segment_ref", "") or "") or None,
    }


def _runtime_stalled_message(run_state: dict | None, *, stale_seconds: float) -> str:
    """Build one operator-facing stalled-runtime summary."""
    state = run_state or {}
    segment_ref = str(state.get("current_segment_ref", "") or "").strip()
    chapter_ref = str(state.get("current_chapter_ref", "") or "").strip()
    target = segment_ref or chapter_ref or "the current section"
    return f"Runtime activity stalled for {int(round(stale_seconds))}s while reading {target}."


def _status_from_run_state(run_state: dict | None, *, running: bool) -> tuple[str, str | None]:
    """Map run_state into the public job status vocabulary."""
    if not run_state:
        return ("parsing_structure" if running else "queued"), None

    stage = str(run_state.get("stage", "")).strip()
    error = str(run_state.get("error", "") or "") or None
    if stage == "parsing_structure":
        return "parsing_structure", error
    if stage == "deep_reading":
        return "deep_reading", error
    if stage == "completed":
        return "completed", error
    if stage == "paused":
        return "paused", error
    if stage == "error":
        return "error", error
    if stage == "ready":
        return ("parsing_structure" if running else "ready"), error
    return ("parsing_structure" if running else "queued"), error


def create_upload_job(root: Path | None = None) -> tuple[str, Path]:
    """Allocate a job id and upload path."""
    job_id = uuid.uuid4().hex[:12]
    return job_id, upload_file(job_id, root)


def save_job(record: dict, root: Path | None = None) -> dict:
    """Persist one job record."""
    normalized = _normalize_record(record)
    normalized["updated_at"] = timestamp()
    save_job_json(job_file(str(normalized["job_id"]), root), normalized)
    canonical_payload = {
        **normalized,
        "domain": PRODUCT_RUNTIME_DOMAIN,
        "lane": "product_runtime",
        "phase": str(normalized.get("status", "")),
        "show_in_active_views": False,
        "log_file": str(job_log_file(str(normalized["job_id"]), root)),
        "purpose": str(
            normalized.get("purpose")
            or ("Sequential deep reading job" if str(normalized.get("job_kind", "read")) == "read" else "Structure parse job")
        ),
        "cwd": str(root or Path.cwd()),
    }
    book_id = str(normalized.get("book_id", "") or "").strip()
    if book_id:
        canonical_payload["run_dir"] = str(_book_output_dir(book_id, root))
    save_job_record(canonical_payload, root=root)
    return normalized


def load_job(job_id: str, root: Path | None = None) -> dict:
    """Load one job record."""
    try:
        return _normalize_record(load_job_record(job_id, root=root))
    except FileNotFoundError:
        return _normalize_record(load_job_json(job_file(job_id, root)))


def _normalized_mechanism_key(value: object) -> str | None:
    """Return one cleaned mechanism key or None."""

    cleaned = str(value or "").strip()
    return cleaned or None


def _resolved_mechanism_key(value: object) -> str | None:
    """Resolve one mechanism key while omitting the current default from CLI flags."""

    mechanism_key = _normalized_mechanism_key(value)
    if mechanism_key == default_mechanism_key():
        return None
    return mechanism_key


def _worker_mechanism_key(value: object) -> str:
    """Resolve the concrete mechanism identity exported to one worker."""

    return _normalized_mechanism_key(value) or default_mechanism_key()


def _source_lease_key(upload_path: Path, *, language: str = "auto") -> str:
    """Resolve the eventual output identity, with a content key as last resort.

    The canonical book id is derived from the output directory, so two EPUBs
    with different bytes but the same title must still fence each other.  A
    content digest is only used when lightweight inspection itself is not
    possible (for example in narrow launcher tests or damaged input).
    """

    try:
        provisioned = inspect_book(upload_path, language_mode=language, sample_text="")
    except Exception:
        provisioned = None
    if provisioned is not None:
        resolved_book_id = str(book_id_from_output_dir(provisioned.output_dir) or "").strip()
        if resolved_book_id:
            return resolved_book_id

    digest = hashlib.sha256()
    with upload_path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return f"source-sha256:{digest.hexdigest()}"


def _acquire_worker_lease(
    *,
    job_id: str,
    job_kind: str,
    mechanism_key: str | None,
    book_id: str | None,
    exclusivity_key: str | None = None,
    root: Path | None,
    confirmed_stopped_attempt: tuple[str, str, int] | None = None,
) -> JobLeaseGrant:
    """Acquire one process lease with neutral job correlation metadata."""

    normalized_book_id = str(book_id or "").strip()
    normalized_exclusivity_key = str(exclusivity_key or normalized_book_id).strip()
    grant = acquire_job_lease(
        job_id,
        root=root or Path.cwd(),
        book_id=normalized_exclusivity_key,
        job_kind=job_kind,
        mechanism_key=_worker_mechanism_key(mechanism_key),
        enforce_book_exclusivity=bool(normalized_exclusivity_key),
        confirmed_stopped_attempt=confirmed_stopped_attempt,
    )
    if grant.book_id == normalized_book_id:
        return grant
    # The sidecar keeps the content-derived lock key, while the worker sees
    # only the real product book id (or lets observation derive it from output).
    return JobLeaseGrant(
        job_id=grant.job_id,
        run_attempt_id=grant.run_attempt_id,
        generation=grant.generation,
        token=grant.token,
        root=grant.root,
        book_id=normalized_book_id,
        job_kind=grant.job_kind,
        mechanism_key=grant.mechanism_key,
    )


def _worker_environment(grant: JobLeaseGrant) -> dict[str, str]:
    """Return an inherited environment carrying the private worker grant."""

    environment = os.environ.copy()
    environment.update(lease_environment(grant))
    return environment


def _terminate_and_reap_spawned_process(process: subprocess.Popen) -> None:
    """Stop the exact child returned by Popen and wait until it is reaped."""

    if process.poll() is None:
        try:
            process.terminate()
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=WORKER_TERMINATION_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        process.wait(timeout=WORKER_TERMINATION_TIMEOUT_SECONDS)


def _record_lease_identity(record: dict) -> tuple[str | None, int | None]:
    run_attempt_id = str(record.get("run_attempt_id", "") or "").strip() or None
    lease = record.get("lease", {}) if isinstance(record.get("lease"), dict) else {}
    raw_generation = lease.get("generation")
    try:
        generation = int(raw_generation) if raw_generation not in {None, ""} else None
    except (TypeError, ValueError):
        generation = None
    return run_attempt_id, generation


def _save_job_if_lease_snapshot_matches(
    record: dict,
    *,
    expected_run_attempt_id: str | None,
    expected_generation: int | None,
    root: Path | None = None,
) -> dict | None:
    """Persist only while the sidecar still represents the loaded generation."""

    job_id = str(record.get("job_id", "") or "").strip()
    if not job_id:
        raise ValueError("A job id is required for lease-aware persistence.")
    with guard_job_lease_snapshot(
        job_id,
        root=root,
        expected_run_attempt_id=expected_run_attempt_id,
        expected_generation=expected_generation,
    ) as matches:
        if not matches:
            return None
        return save_job(record, root)


def _lease_for_record(record: dict, root: Path | None = None) -> tuple[dict[str, object], bool]:
    """Return the current sidecar and whether it still owns this record."""

    run_attempt_id, generation = _record_lease_identity(record)
    if not run_attempt_id or generation is None:
        return {}, False
    job_id = str(record.get("job_id", "") or "").strip()
    if not job_id:
        return {}, False
    payload = load_job_lease(job_id, root=root)
    matches = (
        str(payload.get("run_attempt_id", "") or "") == run_attempt_id
        and int(payload.get("generation", 0) or 0) == generation
    )
    return payload, bool(matches and job_lease_is_valid(payload))


def _released_lease_owner_is_stopped(payload: dict[str, object]) -> bool:
    """Confirm a newer released attempt has no matching live PID incarnation."""

    if str(payload.get("state", "") or "") != "released":
        return False
    owner_pid = int(payload.get("owner_pid", 0) or 0) or None
    if owner_pid is None or not _process_running(owner_pid):
        return True
    expected_identity = str(payload.get("owner_birth_identity", "") or "").strip()
    actual_identity = process_birth_identity(owner_pid)
    return bool(expected_identity and actual_identity and expected_identity != actual_identity)


def _fence_and_terminate(
    record: dict,
    root: Path | None = None,
    *,
    timeout_seconds: float | None = None,
) -> tuple[dict[str, object], bool]:
    """Fence one attempt, signal its PIDs, and wait for confirmed exit."""

    job_id = str(record.get("job_id", "") or "").strip()
    run_attempt_id, generation = _record_lease_identity(record)
    lease_payload: dict[str, object] = {}
    if job_id and run_attempt_id and generation is not None:
        lease_payload = fence_job_lease(
            job_id,
            root=root,
            expected_run_attempt_id=run_attempt_id,
            expected_generation=generation,
        )
        if lease_payload and (
            str(lease_payload.get("run_attempt_id", "") or "") != run_attempt_id
            or int(lease_payload.get("generation", 0) or 0) != generation
        ):
            lease_generation = int(lease_payload.get("generation", 0) or 0)
            if lease_generation > generation and _released_lease_owner_is_stopped(lease_payload):
                # A failed newer resume may have cleaned up and released its
                # exact child before its registry update became durable.  It is
                # safe to reconcile that terminal generation, but never to
                # signal or replace a newer owner that may still be alive.
                return lease_payload, True
            raise JobLeaseConflict(f"Job '{job_id}' acquired a newer worker lease before termination.")
    pids = {
        int(record.get("pid", 0) or 0),
        int(lease_payload.get("owner_pid", 0) or 0),
    }
    managed_lease = bool(run_attempt_id and generation is not None)
    record_lease = record.get("lease", {}) if isinstance(record.get("lease"), dict) else {}
    expected_birth_identity = str(
        lease_payload.get("owner_birth_identity")
        or record_lease.get("owner_birth_identity")
        or ""
    ).strip()
    signaled_pids: set[int] = set()
    unverified_live_owner = False
    for pid in pids:
        if not pid or not _process_running(pid):
            continue
        if not managed_lease:
            # Legacy records contain only an integer PID. Without a fencing
            # generation and birth identity, a reused PID cannot safely
            # authorize SIGTERM of an unrelated process.
            unverified_live_owner = True
            continue
        actual_birth_identity = process_birth_identity(pid)
        if not expected_birth_identity or actual_birth_identity is None:
            unverified_live_owner = True
            continue
        if actual_birth_identity != expected_birth_identity:
            # The recorded PID was reused after the worker exited.  Never
            # signal an unrelated process just because the integer matches.
            continue
        immediate_birth_identity = process_birth_identity(pid)
        if immediate_birth_identity is None:
            # A probe failure does not authorize signaling a bare PID.
            unverified_live_owner = True
            continue
        if immediate_birth_identity != expected_birth_identity:
            # Re-check immediately before SIGTERM to narrow the check/use
            # window when the old process exits during fencing.
            continue
        _terminate_process(pid)
        signaled_pids.add(pid)
    if unverified_live_owner:
        return lease_payload, False
    wait_budget = WORKER_TERMINATION_TIMEOUT_SECONDS if timeout_seconds is None else timeout_seconds
    deadline = time.monotonic() + max(0.0, float(wait_budget))
    while any(_process_running(pid) for pid in signaled_pids):
        if time.monotonic() >= deadline:
            return lease_payload, False
        time.sleep(WORKER_TERMINATION_POLL_SECONDS)
    return lease_payload, True


def _worker_liveness(
    record: dict,
    root: Path | None = None,
) -> tuple[bool, int | None, dict[str, object], bool]:
    """Resolve process truth with lease fencing while preserving legacy PID behavior."""

    recorded_pid = int(record.get("pid", 0) or 0) or None
    run_attempt_id, generation = _record_lease_identity(record)
    if not run_attempt_id or generation is None:
        return _process_running(recorded_pid), recorded_pid, {}, False

    lease_payload, lease_fresh = _lease_for_record(record, root)
    lease_matches = (
        str(lease_payload.get("run_attempt_id", "") or "") == run_attempt_id
        and int(lease_payload.get("generation", 0) or 0) == generation
    )
    lease_pid = int(lease_payload.get("owner_pid", 0) or 0) or None if lease_matches else None
    candidate_pid = lease_pid or recorded_pid
    candidate_running = _process_running(candidate_pid)
    if candidate_running:
        record_lease = record.get("lease", {}) if isinstance(record.get("lease"), dict) else {}
        expected_birth_identity = str(
            lease_payload.get("owner_birth_identity")
            or record_lease.get("owner_birth_identity")
            or ""
        ).strip()
        actual_birth_identity = process_birth_identity(candidate_pid)
        if expected_birth_identity and actual_birth_identity and expected_birth_identity != actual_birth_identity:
            candidate_running = False
    if lease_fresh:
        if candidate_pid is None and str(lease_payload.get("state", "") or "") == "starting":
            return True, None, lease_payload, True
        if candidate_pid is not None and candidate_running:
            return True, candidate_pid, lease_payload, True
    return candidate_running, candidate_pid, lease_payload if lease_matches else {}, False


def _job_command(record: dict, *, continue_mode: bool, mechanism_key: str | None = None) -> list[str]:
    """Build the CLI command for one persisted job record."""
    upload_path = Path(str(record.get("upload_path", "")))
    language = str(record.get("language", "auto") or "auto")
    intent = str(record.get("intent", "") or "") or None
    memory_retrieval_mode = str(record.get("memory_retrieval_mode", "") or "").strip()
    job_kind = str(record.get("job_kind", "read") or "read")
    selected_mechanism = _resolved_mechanism_key(mechanism_key or record.get("mechanism_key"))

    if job_kind == "parse":
        command = [
            sys.executable,
            "main.py",
            "parse",
            str(upload_path),
            "--language",
            language,
        ]
        if continue_mode:
            command.append("--continue")
        if selected_mechanism:
            command.extend(["--mechanism", selected_mechanism])
        return command

    command = [
        sys.executable,
        "main.py",
        "read",
        str(upload_path),
        "--mode",
        "sequential",
        "--language",
        language,
    ]
    if continue_mode:
        command.append("--continue")
    if intent:
        command.extend(["--intent", intent])
    if memory_retrieval_mode:
        command.extend(["--memory-retrieval-mode", memory_retrieval_mode])
    if selected_mechanism:
        command.extend(["--mechanism", selected_mechanism])
    return command


def _launch_subprocess_job(
    *,
    upload_path: Path,
    command: list[str],
    job_kind: str,
    mechanism_key: str | None = None,
    language: str = "auto",
    intent: str | None = None,
    memory_retrieval_mode: str | None = None,
    root: Path | None = None,
    job_id: str | None = None,
    initial_status: str = "queued",
    book_id: str | None = None,
    resume_count: int = 0,
    confirmed_stopped_attempt: tuple[str, str, int] | None = None,
) -> dict:
    """Start a detached subprocess and persist the tracking record."""
    resolved_job_id = job_id or upload_path.stem
    runtime_issue = _python_runtime_issue()
    lease_grant = (
        None
        if runtime_issue
        else _acquire_worker_lease(
            job_id=resolved_job_id,
            job_kind=job_kind,
            mechanism_key=mechanism_key,
            book_id=book_id,
            exclusivity_key=(
                None
                if str(book_id or "").strip()
                else _source_lease_key(upload_path, language=language)
            ),
            root=root,
            confirmed_stopped_attempt=confirmed_stopped_attempt,
        )
    )
    process: subprocess.Popen | None = None
    try:
        lease_payload = load_job_lease(resolved_job_id, root=root) if lease_grant is not None else {}
        record = _job_record(
            job_id=resolved_job_id,
            status="error" if runtime_issue else initial_status,
            upload_path=upload_path,
            job_kind=job_kind,
            mechanism_key=mechanism_key,
            language=language,
            intent=intent,
            memory_retrieval_mode=memory_retrieval_mode,
            book_id=book_id,
            resume_count=resume_count,
            run_attempt_id=lease_grant.run_attempt_id if lease_grant is not None else None,
            lease=sanitized_lease_metadata(lease_payload),
            error=runtime_issue,
        )
        record["command"] = " ".join(command)
        record["cwd"] = str(root or Path.cwd())
        saved_record = save_job(record, root)
        if runtime_issue:
            if book_id:
                append_deduped_activity_event(
                    _book_output_dir(book_id, root),
                    {
                        "type": "runtime_environment_error",
                        "message": "Background job started under unsupported Python runtime.",
                        "details": {
                            "reason": runtime_issue,
                            "python_executable": sys.executable,
                            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                        },
                    },
                )
            return saved_record

        log_path = job_log_file(resolved_job_id, root)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("ab") as log:
            process = subprocess.Popen(
                command,
                cwd=str(root or Path.cwd()),
                stdout=log,
                stderr=subprocess.STDOUT,
                env=_worker_environment(lease_grant),
            )
        lease_payload = heartbeat_job_lease(lease_grant, owner_pid=process.pid)
        launched_record = _job_record(
            job_id=resolved_job_id,
            status=initial_status,
            upload_path=upload_path,
            job_kind=job_kind,
            mechanism_key=mechanism_key,
            language=language,
            intent=intent,
            memory_retrieval_mode=memory_retrieval_mode,
            book_id=book_id,
            resume_count=resume_count,
            pid=process.pid,
            run_attempt_id=lease_grant.run_attempt_id,
            lease=sanitized_lease_metadata(lease_payload),
            created_at=str(record["created_at"]),
        )
        launched_record["command"] = " ".join(command)
        launched_record["cwd"] = str(root or Path.cwd())
        return save_job(launched_record, root)
    except Exception:
        if process is not None:
            _terminate_and_reap_spawned_process(process)
        if lease_grant is not None:
            release_job_lease(lease_grant)
        raise


def launch_sequential_job(
    upload_path: Path,
    *,
    mechanism_key: str | None = None,
    language: str = "auto",
    intent: str | None = None,
    memory_retrieval_mode: str | None = None,
    root: Path | None = None,
    book_id: str | None = None,
) -> dict:
    """Start a sequential read as a detached subprocess and persist the job."""
    command = [
        sys.executable,
        "main.py",
        "read",
        str(upload_path),
        "--mode",
        "sequential",
        "--language",
        language,
    ]
    if _resolved_mechanism_key(mechanism_key):
        command.extend(["--mechanism", str(mechanism_key)])
    if intent:
        command.extend(["--intent", intent])
    if memory_retrieval_mode:
        command.extend(["--memory-retrieval-mode", memory_retrieval_mode])

    return _launch_subprocess_job(
        upload_path=upload_path,
        command=command,
        job_kind="read",
        mechanism_key=mechanism_key,
        language=language,
        intent=intent,
        memory_retrieval_mode=memory_retrieval_mode,
        root=root,
        initial_status="queued",
        book_id=book_id,
    )


def launch_parse_job(
    upload_path: Path,
    *,
    mechanism_key: str | None = None,
    language: str = "auto",
    memory_retrieval_mode: str | None = None,
    root: Path | None = None,
    book_id: str | None = None,
) -> dict:
    """Start a structure-only parse job and persist the job record."""
    command = [
        sys.executable,
        "main.py",
        "parse",
        str(upload_path),
        "--language",
        language,
    ]
    if _resolved_mechanism_key(mechanism_key):
        command.extend(["--mechanism", str(mechanism_key)])
    return _launch_subprocess_job(
        upload_path=upload_path,
        command=command,
        job_kind="parse",
        mechanism_key=mechanism_key,
        language=language,
        memory_retrieval_mode=memory_retrieval_mode,
        root=root,
        initial_status="queued",
        book_id=book_id,
    )


def provision_uploaded_book(
    upload_path: Path,
    *,
    mechanism_key: str | None = None,
    language: str = "auto",
    root: Path | None = None,
) -> str | None:
    """Create a minimal book shell so uploads can resolve a book id immediately."""
    try:
        provisioned = inspect_book(upload_path, language_mode=language, sample_text="")
        output_dir = provisioned.output_dir
        book_id = book_id_from_output_dir(output_dir)
        manifest_path = existing_book_manifest_file(output_dir)
        if manifest_path.exists():
            return book_id

        ensure_output_dir(output_dir)
        ensure_book_assets(upload_path, output_dir)

        manifest = build_minimal_book_manifest(
            output_dir,
            book_title=provisioned.title,
            author=provisioned.author,
            book_language=provisioned.book_language,
            output_language=provisioned.output_language,
            source_file=str(upload_path),
            chapters=[],
        )
        write_book_manifest(output_dir, manifest)
        write_run_state(
            output_dir,
            build_run_state(
                book_title=provisioned.title,
                stage="ready",
                total_chapters=0,
                completed_chapters=0,
            ),
        )
        append_activity_event(
            output_dir,
            {
                "type": "upload_received",
                "message": "文件已上传，正在解析书籍结构。",
            },
        )
        return book_id
    except Exception:
        return None


def launch_existing_book_read_job(
    book_id: str,
    *,
    mechanism_key: str | None = None,
    language: str = "auto",
    intent: str | None = None,
    memory_retrieval_mode: str | None = None,
    root: Path | None = None,
) -> dict:
    """Start the active sequential deep-reading workflow for an existing uploaded book."""
    source_path = source_asset_path(book_id, root=root)
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    command = [
        sys.executable,
        "main.py",
        "read",
        str(source_path),
        "--mode",
        "sequential",
        "--language",
        language,
    ]
    if _resolved_mechanism_key(mechanism_key):
        command.extend(["--mechanism", str(mechanism_key)])
    if intent:
        command.extend(["--intent", intent])
    if memory_retrieval_mode:
        command.extend(["--memory-retrieval-mode", memory_retrieval_mode])

    return _launch_subprocess_job(
        upload_path=source_path,
        command=command,
        job_kind="read",
        mechanism_key=mechanism_key,
        language=language,
        intent=intent,
        memory_retrieval_mode=memory_retrieval_mode,
        root=root,
        job_id=uuid.uuid4().hex[:12],
        initial_status="queued",
        book_id=book_id,
    )


def launch_book_analysis_job(
    book_id: str,
    *,
    mechanism_key: str | None = None,
    language: str = "auto",
    intent: str | None = None,
    memory_retrieval_mode: str | None = None,
    root: Path | None = None,
) -> dict:
    """Deprecated compatibility alias for the active existing-book deep-reading launcher."""

    return launch_existing_book_read_job(
        book_id,
        mechanism_key=mechanism_key,
        language=language,
        intent=intent,
        memory_retrieval_mode=memory_retrieval_mode,
        root=root,
    )


def _book_output_dir(book_id: str, root: Path | None = None) -> Path:
    """Resolve one book output directory."""
    return (root or Path.cwd()) / "output" / book_id


def _load_book_run_state(book_id: str, root: Path | None = None) -> dict | None:
    """Read the raw persisted run_state payload for one book."""
    path = existing_run_state_file(_book_output_dir(book_id, root))
    return load_runtime_json(path) if path.exists() else None


def _load_book_parse_state(book_id: str, root: Path | None = None) -> dict | None:
    """Read the raw persisted parse_state payload for one book."""
    path = existing_parse_state_file(_book_output_dir(book_id, root))
    return load_runtime_json(path) if path.exists() else None


def _load_book_runtime_shell(book_id: str, root: Path | None = None) -> dict | None:
    """Read the shared runtime shell payload for one book when available."""

    path = existing_runtime_shell_file(_book_output_dir(book_id, root))
    return load_runtime_json(path) if path.exists() else None


def _legacy_resume_mechanism_key(book_id: str, root: Path | None = None) -> str | None:
    """Infer one legacy mechanism key for old resumable runs that predate shell metadata."""

    output_dir = _book_output_dir(book_id, root)
    if existing_structure_file(output_dir).exists():
        return "iterator_v1"
    return None


def _resume_mechanism_key(record: dict, *, book_id: str | None, root: Path | None = None) -> str | None:
    """Resolve the mechanism key for resume/recovery with shell-first precedence."""

    if book_id:
        runtime_shell = _load_book_runtime_shell(book_id, root)
        if isinstance(runtime_shell, dict):
            mechanism_key = _normalized_mechanism_key(runtime_shell.get("mechanism_key"))
            if mechanism_key:
                return mechanism_key
    mechanism_key = _normalized_mechanism_key(record.get("mechanism_key"))
    if mechanism_key:
        return mechanism_key
    if book_id:
        legacy_mechanism_key = _legacy_resume_mechanism_key(book_id, root)
        if legacy_mechanism_key:
            return legacy_mechanism_key
    return default_mechanism_key()


def _terminate_process(pid: int | None) -> None:
    """Best-effort terminate one stale background worker."""
    if not pid:
        return
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError:
        return


def _clear_live_analysis_artifacts(book_id: str, root: Path | None = None) -> None:
    """Reset live deep-reading artifacts so one fresh run can start cleanly."""
    from src.iterator_reader.frontend_artifacts import (
        build_run_state as build_iterator_run_state,
        write_book_manifest as write_iterator_book_manifest,
    )

    output_dir = _book_output_dir(book_id, root)
    structure_path = existing_structure_file(output_dir)
    manifest_path = existing_book_manifest_file(output_dir)
    legacy_manifest_path = legacy_book_manifest_file(output_dir)
    legacy_run_state_path = legacy_run_state_file(output_dir)
    legacy_activity_path = legacy_activity_file(output_dir)
    preserve_legacy_manifest = legacy_manifest_path.exists()
    preserve_legacy_run_state = legacy_run_state_path.exists()
    preserve_legacy_activity = legacy_activity_path.exists()
    if not structure_path.exists():
        clear_iterator_private_artifacts(output_dir)
        shutil.rmtree(runtime_dir(output_dir), ignore_errors=True)
        return

    structure = load_structure_json(structure_path)
    chapters = list(structure.get("chapters", []))
    for chapter in chapters:
        chapter.pop("output_file", None)
        chapter["status"] = "pending"
        for segment in chapter.get("segments", []):
            if isinstance(segment, dict):
                segment["status"] = "pending"
        existing_chapter_markdown_file(output_dir, chapter).unlink(missing_ok=True)
        existing_chapter_result_file(output_dir, chapter).unlink(missing_ok=True)
        chapter_qa_file(output_dir, chapter).unlink(missing_ok=True)

    shutil.rmtree(runtime_dir(output_dir), ignore_errors=True)
    clear_iterator_private_artifacts(output_dir)
    save_structure(structure_path, structure)
    if manifest_path.exists():
        manifest = write_iterator_book_manifest(output_dir, structure)
        if preserve_legacy_manifest:
            save_job_json(legacy_manifest_path, manifest)
    reset_activity(output_dir)
    run_state = write_run_state(
        output_dir,
        build_iterator_run_state(
            structure,
            stage="ready",
            total_chapters=len(chapters),
            completed_chapters=0,
            current_phase_step=None,
            resume_available=False,
            last_checkpoint_at=None,
        ),
    )
    if preserve_legacy_activity:
        legacy_activity_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_activity_path.write_text("", encoding="utf-8")
    if preserve_legacy_run_state:
        save_job_json(legacy_run_state_path, run_state)


def _current_run_stage(book_id: str, root: Path | None = None) -> str:
    """Read the current runtime stage for one book when available."""
    run_state_path = existing_run_state_file(_book_output_dir(book_id, root))
    if not run_state_path.exists():
        return "parsing_structure"
    return str(load_runtime_json(run_state_path).get("stage", "parsing_structure"))


def _resume_target_status(record: dict, book_id: str | None, root: Path | None = None) -> str:
    """Choose the status that should be resumed for one stalled job."""
    job_kind = str(record.get("job_kind", "read") or "read")
    if job_kind == "parse":
        return "parsing_structure"

    current_status = str(record.get("status", "queued") or "queued")
    if current_status in {"parsing_structure", "ready"}:
        return "parsing_structure"
    if book_id:
        stage = _current_run_stage(book_id, root)
        if stage == "parsing_structure":
            return "parsing_structure"
    return "deep_reading"


def _pause_runtime_state(
    book_id: str,
    *,
    previous_status: str,
    error: str,
    root: Path | None = None,
    latest_job: dict | None = None,
) -> None:
    """Write paused status into the book runtime files."""
    output_dir = _book_output_dir(book_id, root)
    run_state_path = existing_run_state_file(output_dir)
    parse_state_path = existing_parse_state_file(output_dir)
    runtime_shell = _load_book_runtime_shell(book_id, root)
    parse_payload = load_runtime_json(parse_state_path) if parse_state_path.exists() else None
    if run_state_path.exists():
        payload = load_runtime_json(run_state_path)
        payload["stage"] = "paused"
        payload["error"] = error
        payload["resume_available"] = effective_resume_available(
            stage="paused",
            run_state=payload,
            parse_state=parse_payload,
            runtime_shell=runtime_shell,
            latest_job=latest_job,
        )
        payload["updated_at"] = timestamp()
        payload["current_phase_step"] = "等待继续执行"
        payload["last_checkpoint_at"] = payload.get("last_checkpoint_at") or (runtime_shell or {}).get("last_checkpoint_at")
        save_job_json(run_state_path, payload)

    if previous_status == "parsing_structure" and parse_state_path.exists():
        payload = parse_payload or {}
        payload["status"] = "paused"
        payload["error"] = error
        payload["resume_available"] = effective_resume_available(
            stage="paused",
            run_state=load_runtime_json(run_state_path) if run_state_path.exists() else None,
            parse_state=payload,
            runtime_shell=runtime_shell,
            latest_job=latest_job,
        )
        payload["updated_at"] = timestamp()
        save_job_json(parse_state_path, payload)


def _abandon_dev_run(record: dict, *, book_id: str | None, run_state: dict | None, root: Path | None = None) -> dict:
    """Mark one cross-boot development run as abandoned instead of resuming it."""
    normalized = _normalize_record(record)
    fenced_lease, stopped = _fence_and_terminate(normalized, root)
    message = "Detected an unfinished reader from an older development boot; start a fresh run instead of resuming it."
    if not stopped:
        message = f"{message} The previous worker did not exit after termination was requested."
    if book_id:
        _pause_runtime_state(
            book_id,
            previous_status=_resume_target_status(normalized, book_id, root),
            error=message,
            root=root,
            latest_job=normalized,
        )
        append_deduped_activity_event(
            _book_output_dir(book_id, root),
            {
                "type": "dev_run_abandoned",
                "message": "Reader from an older development session was abandoned after a backend restart.",
                **_activity_context(run_state),
                "details": {
                    "job_id": str(normalized.get("job_id", "")),
                    "boot_id": normalized.get("boot_id"),
                },
            },
        )
    return save_job(
        {
            **normalized,
            "status": "paused" if book_id else "error",
            "book_id": book_id,
            "pid": None if stopped else normalized.get("pid"),
            "lease": sanitized_lease_metadata(fenced_lease) or normalized.get("lease", {}),
            "error": message,
        },
        root,
    )


def _fresh_rerun_after_incompatibility(record: dict, *, book_id: str | None, root: Path | None = None) -> dict:
    """Archive one incompatible run, reset live artifacts, and launch a fresh job."""
    normalized = _normalize_record(record)
    resolved_book_id = str(book_id or normalized.get("book_id", "") or "").strip() or None
    mechanism_key = _resume_mechanism_key(normalized, book_id=resolved_book_id, root=root)
    reason = "Detected an incompatible resume checkpoint; clearing live analysis artifacts and starting a fresh run."
    fenced_lease, stopped = _fence_and_terminate(normalized, root)
    if not stopped:
        return save_job(
            {
                **normalized,
                "status": "paused",
                "book_id": resolved_book_id,
                "lease": sanitized_lease_metadata(fenced_lease) or normalized.get("lease", {}),
                "error": f"{reason} The previous worker did not exit, so no replacement was launched.",
            },
            root,
        )
    archived_job = save_job(
        {
            **normalized,
            "status": "error",
            "book_id": resolved_book_id,
            "pid": None,
            "lease": sanitized_lease_metadata(fenced_lease) or normalized.get("lease", {}),
            "error": reason,
        },
        root,
    )
    if resolved_book_id:
        _archive_run_artifacts(book_id=resolved_book_id, job=archived_job, root=root)
        _clear_live_analysis_artifacts(resolved_book_id, root)

    fresh_record = _launch_subprocess_job(
        upload_path=Path(str(normalized.get("upload_path", ""))),
        command=_job_command(normalized, continue_mode=False, mechanism_key=mechanism_key),
        job_kind=str(normalized.get("job_kind", "read") or "read"),
        mechanism_key=mechanism_key,
        language=str(normalized.get("language", "auto") or "auto"),
        intent=normalized.get("intent"),
        memory_retrieval_mode=normalized.get("memory_retrieval_mode"),
        root=root,
        job_id=uuid.uuid4().hex[:12],
        initial_status="queued",
        book_id=resolved_book_id,
        confirmed_stopped_attempt=(
            str(normalized.get("job_id", "")),
            str(normalized.get("run_attempt_id", "")),
            int((normalized.get("lease", {}) or {}).get("generation", 0) or 0),
        )
        if normalized.get("run_attempt_id")
        and int((normalized.get("lease", {}) or {}).get("generation", 0) or 0) > 0
        else None,
    )
    if resolved_book_id:
        append_activity_event(
            _book_output_dir(resolved_book_id, root),
            {
                "type": "resume_incompatible",
                "message": "Detected an incompatible checkpoint from an older reader runtime; restarting this analysis from scratch.",
                "details": {
                    "previous_job_id": str(normalized.get("job_id", "")),
                    "resume_compat_version": _record_resume_compat(normalized),
                    "current_resume_compat_version": get_reader_resume_compat_version(),
                },
            },
        )
        append_activity_event(
            _book_output_dir(resolved_book_id, root),
            {
                "type": "fresh_rerun_started",
                "message": "Started a fresh analysis run after discarding incompatible live runtime artifacts.",
                "details": {
                    "job_id": str(fresh_record.get("job_id", "")),
                },
            },
        )
    return fresh_record


def _resume_supported(record: dict) -> bool:
    """Return whether one job has enough context to resume."""
    upload_path = Path(str(record.get("upload_path", "") or ""))
    return upload_path.exists()


def _resume_job(record: dict, root: Path | None = None, *, automatic: bool) -> dict:
    """Resume one stopped parse/read subprocess in place."""
    normalized = _normalize_record(record)
    book_id = str(normalized.get("book_id", "") or "") or find_book_id_by_source(Path(str(normalized.get("upload_path", ""))), root=root)
    target_status = _resume_target_status(normalized, book_id, root)
    mechanism_key = _resume_mechanism_key(normalized, book_id=book_id, root=root)
    command = _job_command(normalized, continue_mode=True, mechanism_key=mechanism_key)
    process_alive, _active_pid, _lease_payload, _lease_fresh = _worker_liveness(normalized, root)
    if process_alive and automatic:
        raise RuntimeError("The previous worker is still alive; automatic resume was not started.")
    fenced_lease, stopped = _fence_and_terminate(normalized, root)
    if not stopped:
        message = "The previous worker did not exit after termination was requested; resume was not started."
        save_job(
            {
                **normalized,
                "status": "paused",
                "book_id": book_id,
                "lease": sanitized_lease_metadata(fenced_lease) or normalized.get("lease", {}),
                "error": message,
            },
            root,
        )
        raise RuntimeError(message)
    lease_grant = _acquire_worker_lease(
        job_id=str(normalized.get("job_id", "")),
        job_kind=str(normalized.get("job_kind", "read") or "read"),
        mechanism_key=mechanism_key,
        book_id=book_id,
        exclusivity_key=(
            None
            if str(book_id or "").strip()
            else _source_lease_key(
                Path(str(normalized.get("upload_path", ""))),
                language=str(normalized.get("language", "auto") or "auto"),
            )
        ),
        root=root,
        confirmed_stopped_attempt=(
            str(normalized.get("job_id", "")),
            str(normalized.get("run_attempt_id", "")),
            int((normalized.get("lease", {}) or {}).get("generation", 0) or 0),
        )
        if normalized.get("run_attempt_id")
        and int((normalized.get("lease", {}) or {}).get("generation", 0) or 0) > 0
        else None,
    )
    process: subprocess.Popen | None = None
    try:
        log_path = job_log_file(str(normalized.get("job_id", "")), root)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("ab") as log:
            banner = f"\n[{timestamp()}] resume {'auto' if automatic else 'manual'} -> {target_status}\n"
            log.write(banner.encode("utf-8"))
            process = subprocess.Popen(
                command,
                cwd=str(root or Path.cwd()),
                stdout=log,
                stderr=subprocess.STDOUT,
                env=_worker_environment(lease_grant),
            )
        lease_payload = heartbeat_job_lease(lease_grant, owner_pid=process.pid)
        if book_id:
            append_activity_event(
                _book_output_dir(book_id, root),
                {
                    "type": "resume_detected",
                    "message": ("检测到中断，已自动继续执行。" if automatic else "已继续执行，系统将从最近 checkpoint 恢复。"),
                },
            )

        return save_job(
            _job_record(
                job_id=str(normalized.get("job_id", "")),
                status=target_status,
                upload_path=Path(str(normalized.get("upload_path", ""))),
                job_kind=str(normalized.get("job_kind", "read")),
                mechanism_key=mechanism_key,
                language=str(normalized.get("language", "auto")),
                intent=normalized.get("intent"),
                memory_retrieval_mode=normalized.get("memory_retrieval_mode"),
                resume_count=int(normalized.get("resume_count", 0)) + 1,
                auto_resume_count=int(normalized.get("auto_resume_count", 0) or 0) + (1 if automatic else 0),
                book_id=book_id,
                pid=process.pid,
                run_attempt_id=lease_grant.run_attempt_id,
                lease=sanitized_lease_metadata(lease_payload),
                error=None,
                created_at=str(normalized.get("created_at", timestamp())),
            ),
            root,
        )
    except Exception as exc:
        if process is not None:
            _terminate_and_reap_spawned_process(process)
        released_lease = release_job_lease(lease_grant)
        try:
            _save_job_if_lease_snapshot_matches(
                {
                    **normalized,
                    "status": "paused",
                    "book_id": book_id,
                    "pid": None,
                    "run_attempt_id": lease_grant.run_attempt_id,
                    "lease": sanitized_lease_metadata(released_lease),
                    "error": f"Resume attempt failed before completion: {exc}",
                },
                expected_run_attempt_id=lease_grant.run_attempt_id,
                expected_generation=lease_grant.generation,
                root=root,
            )
        except Exception:
            # Preserve the launch error. A later resume may reconcile the newer
            # released sidecar after confirming that its exact owner is gone.
            pass
        raise


def _can_auto_resume(record: dict) -> bool:
    """Return whether one stalled job should be auto-resumed."""
    return _resume_supported(record) and int(record.get("auto_resume_count", 0) or 0) < AUTO_RESUME_LIMIT


def read_job_log_tail(job_id: str, root: Path | None = None, *, line_limit: int = 120) -> list[str]:
    """Return the trailing lines from one job log file."""
    log_path = job_log_file(job_id, root)
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-line_limit:]


def analysis_log_payload(book_id: str, root: Path | None = None, *, line_limit: int = 120) -> dict:
    """Return the latest analysis log snapshot for one book."""
    migrate_product_shadow_jobs(root)
    record = latest_job_for_book(book_id, root=root)
    if not record:
        return {
            "job_id": None,
            "available": False,
            "updated_at": None,
            "lines": [],
        }
    return {
        "job_id": str(record.get("job_id", "")),
        "available": True,
        "updated_at": str(record.get("updated_at", "")),
        "lines": read_job_log_tail(str(record.get("job_id", "")), root=root, line_limit=line_limit),
    }


def resume_job_for_book(
    book_id: str,
    root: Path | None = None,
    *,
    memory_retrieval_mode: str | None = None,
) -> dict:
    """Resume the latest paused or failed job for one book."""
    migrate_product_shadow_jobs(root)
    record = latest_job_for_book(book_id, root=root)
    if record is None:
        raise FileNotFoundError(book_id)
    running, active_pid, lease_payload, lease_fresh = _worker_liveness(record, root)
    lease_managed = all(value is not None for value in _record_lease_identity(record))
    if running and (lease_fresh or not lease_managed):
        return save_job(
            {
                **record,
                "book_id": book_id,
                "pid": active_pid or record.get("pid"),
                "lease": sanitized_lease_metadata(lease_payload) or record.get("lease", {}),
                "memory_retrieval_mode": memory_retrieval_mode or record.get("memory_retrieval_mode"),
            },
            root,
        )
    run_state = _load_book_run_state(book_id, root)
    parse_state = _load_book_parse_state(book_id, root)
    if _is_dev_boot_mismatch(record):
        raise RuntimeError("This analysis belongs to an older development boot. Start a fresh run instead of resuming it.")
    if get_backend_run_mode() in {"demo", "prod"} and not _resume_compatible(
        record=record,
        run_state=run_state,
        parse_state=parse_state,
    ):
        return _fresh_rerun_after_incompatibility(
            {**record, "memory_retrieval_mode": memory_retrieval_mode or record.get("memory_retrieval_mode")},
            book_id=book_id,
            root=root,
        )
    if not _resume_supported(record):
        raise RuntimeError("No resumable checkpoint is available for this book.")
    return _resume_job(
        {**record, "book_id": book_id, "memory_retrieval_mode": memory_retrieval_mode or record.get("memory_retrieval_mode")},
        root,
        automatic=False,
    )


def recover_unfinished_jobs(root: Path | None = None) -> None:
    """Refresh unfinished jobs on startup so resumable work is relaunched."""
    migrate_product_shadow_jobs(root)
    for record in list_job_records(root, include_archived=True):
        if str(record.get("domain", "") or PRODUCT_RUNTIME_DOMAIN) != PRODUCT_RUNTIME_DOMAIN:
            continue
        status = str(record.get("status", "queued") or "queued")
        if status in ACTIVE_JOB_STATUSES:
            refresh_job(str(record.get("job_id", "")), root=root)
    for book_id, run_state, projection in iter_orphan_active_runs(root):
        stale_seconds = projection.stale_seconds or ACTIVE_RUNTIME_STALE_SECONDS
        error = _runtime_stalled_message(run_state, stale_seconds=stale_seconds)
        _pause_runtime_state(
            book_id,
            previous_status=str(run_state.get("stage", "deep_reading") or "deep_reading"),
            error=error,
            root=root,
            latest_job=projection.latest_job,
        )
        append_deduped_activity_event(
            _book_output_dir(book_id, root),
            {
                "type": "runtime_stalled",
                "message": error,
                **_activity_context(run_state),
                "details": {
                    "stale_seconds": int(round(stale_seconds)),
                    "source": "startup_orphan_reconcile",
                },
            },
        )
        append_deduped_activity_event(
            _book_output_dir(book_id, root),
            {
                "type": "job_paused_by_runtime_guard",
                "message": "Reader paused because an orphaned live runtime snapshot became stale.",
                **_activity_context(run_state),
                "details": {
                    "resume_available": effective_resume_available(
                        stage="paused",
                        run_state=_load_book_run_state(book_id, root),
                        parse_state=_load_book_parse_state(book_id, root),
                        runtime_shell=_load_book_runtime_shell(book_id, root),
                        latest_job=projection.latest_job,
                    ),
                    "status_reason": "runtime_stale",
                    "source": "startup_orphan_reconcile",
                },
            },
        )


def refresh_job(job_id: str, root: Path | None = None) -> dict:
    """Refresh one job record from process state and sequential artifacts."""
    record = load_job(job_id, root)
    upload_path = Path(str(record.get("upload_path", "")))
    running, pid, lease_payload, lease_fresh = _worker_liveness(record, root)
    process_alive = running
    lease_managed = all(value is not None for value in _record_lease_identity(record))
    lease_heartbeat_lost = bool(lease_managed and process_alive and not lease_fresh)
    book_id = str(record.get("book_id", "") or "") or find_book_id_by_source(upload_path, root=root)
    error = str(record.get("error", "") or "") or None
    status = str(record.get("status", "queued") or "queued")
    run_state: dict | None = None
    parse_state: dict | None = None
    run_mode = get_backend_run_mode()

    if book_id:
        run_state = _load_book_run_state(book_id, root) or {}
        parse_state = _load_book_parse_state(book_id, root)
        status, state_error = _status_from_run_state(run_state, running=running)
        error = state_error or error
    elif running:
        status = "parsing_structure"

    if status in ACTIVE_JOB_STATUSES and _is_dev_boot_mismatch(record):
        return _abandon_dev_run(record, book_id=book_id, run_state=run_state, root=root)

    if status in ACTIVE_JOB_STATUSES and run_mode in {"demo", "prod"} and not _resume_compatible(
        record=record,
        run_state=run_state,
        parse_state=parse_state,
    ):
        return _fresh_rerun_after_incompatibility(record, book_id=book_id, root=root)

    if lease_heartbeat_lost:
        running = False
        status = "paused"
        error = "Worker lease heartbeat expired while the background process was still alive."
        lease_metadata = sanitized_lease_metadata(lease_payload)
        lease_metadata["status_reason"] = "heartbeat_lost"
        lease_payload = {**lease_payload, "status_reason": "heartbeat_lost"}
        if book_id:
            _pause_runtime_state(
                book_id,
                previous_status=_resume_target_status(record, book_id, root),
                error=error,
                root=root,
                latest_job={**record, "book_id": book_id, "status": "paused", "lease": lease_metadata},
            )
            append_deduped_activity_event(
                _book_output_dir(book_id, root),
                {
                    "type": "job_lease_heartbeat_lost",
                    "message": "Reader paused because its worker lease heartbeat expired; the existing process was left untouched.",
                    **_activity_context(run_state),
                    "details": {
                        "job_id": job_id,
                        "run_attempt_id": record.get("run_attempt_id"),
                        "lease_generation": (record.get("lease", {}) or {}).get("generation"),
                        "status_reason": "heartbeat_lost",
                    },
                },
            )

    stale_seconds = _seconds_since((run_state or {}).get("updated_at"))
    runtime_stalled = (
        bool(running)
        and not lease_fresh
        and status in {"parsing_structure", "deep_reading", "ready"}
        and stale_seconds is not None
        and stale_seconds >= ACTIVE_RUNTIME_STALE_SECONDS
    )
    if runtime_stalled:
        running = False
        status = "paused" if book_id else "error"
        error = _runtime_stalled_message(run_state, stale_seconds=stale_seconds)
        if book_id:
            _pause_runtime_state(
                book_id,
                previous_status=_resume_target_status(record, book_id, root),
                error=error,
                root=root,
                latest_job={**record, "book_id": book_id, "status": "paused"},
            )
            append_deduped_activity_event(
                _book_output_dir(book_id, root),
                {
                    "type": "runtime_stalled",
                    "message": error,
                    **_activity_context(run_state),
                    "details": {
                        "stale_seconds": int(round(stale_seconds)),
                        "job_id": job_id,
                    },
                },
            )
            append_deduped_activity_event(
                _book_output_dir(book_id, root),
                {
                    "type": "job_paused_by_runtime_guard",
                    "message": "Reader paused because live runtime updates stopped arriving.",
                    **_activity_context(run_state),
                    "details": {
                        "job_id": job_id,
                        "resume_available": effective_resume_available(
                            stage="paused",
                            run_state=_load_book_run_state(book_id, root),
                            parse_state=_load_book_parse_state(book_id, root),
                            runtime_shell=_load_book_runtime_shell(book_id, root),
                            latest_job={**record, "book_id": book_id, "status": "paused"},
                        ),
                        "status_reason": "runtime_stale",
                    },
                },
            )
            if run_mode in {"demo", "prod"} and not process_alive and _can_auto_resume(record):
                return _resume_job({**record, "book_id": book_id}, root, automatic=True)

    if not running and status not in {"completed", "error", "ready", "paused"}:
        if not process_alive and _can_auto_resume(record):
            return _resume_job({**record, "book_id": book_id}, root, automatic=True)

        if book_id:
            status = "paused"
            error = error or "任务已停止，等待继续执行。"
            _pause_runtime_state(
                book_id,
                previous_status=_resume_target_status(record, book_id, root),
                error=error,
                root=root,
                latest_job={**record, "book_id": book_id, "status": "paused"},
            )
            append_deduped_activity_event(
                _book_output_dir(book_id, root),
                {
                    "type": "job_paused_by_runtime_guard",
                    "message": f"Reader paused because the background job stopped unexpectedly: {error}",
                    **_activity_context(run_state),
                    "details": {
                        "job_id": job_id,
                        "resume_available": effective_resume_available(
                            stage="paused",
                            run_state=_load_book_run_state(book_id, root),
                            parse_state=_load_book_parse_state(book_id, root),
                            runtime_shell=_load_book_runtime_shell(book_id, root),
                            latest_job={**record, "book_id": book_id, "status": "paused"},
                        ),
                        "status_reason": "runtime_interrupted",
                    },
                },
            )
        else:
            status = "error"
            error = error or "Job exited before producing readable artifacts."

    refreshed = _job_record(
        job_id=job_id,
        status=status,
        upload_path=upload_path,
        job_kind=str(record.get("job_kind", "read")),
        mechanism_key=_resume_mechanism_key(record, book_id=book_id, root=root) if book_id else _normalized_mechanism_key(record.get("mechanism_key")),
        language=str(record.get("language", "auto")),
        intent=record.get("intent"),
        memory_retrieval_mode=record.get("memory_retrieval_mode"),
        resume_count=int(record.get("resume_count", 0) or 0),
        auto_resume_count=int(record.get("auto_resume_count", 0) or 0),
        book_id=book_id,
        pid=pid if process_alive else None,
        run_attempt_id=record.get("run_attempt_id"),
        lease=(
            {**sanitized_lease_metadata(lease_payload), "status_reason": "heartbeat_lost"}
            if lease_heartbeat_lost
            else sanitized_lease_metadata(lease_payload) or record.get("lease", {})
        ),
        error=error,
        created_at=str(record.get("created_at", timestamp())),
    )
    expected_run_attempt_id, expected_generation = _record_lease_identity(record)
    saved = _save_job_if_lease_snapshot_matches(
        refreshed,
        expected_run_attempt_id=expected_run_attempt_id,
        expected_generation=expected_generation,
        root=root,
    )
    if saved is None:
        # A resume/acquire advanced the sidecar after this refresh loaded its
        # snapshot.  Do not overwrite that owner with stale PID/generation data.
        return load_job(job_id, root)
    if book_id and status in {"completed", "error"}:
        _archive_run_artifacts(book_id=book_id, job=saved, root=root)
    return saved


def _archive_run_artifacts(*, book_id: str, job: dict, root: Path | None = None) -> None:
    """Mirror terminal job artifacts into the book-scoped history tree."""
    output_dir = (root or Path.cwd()) / "output" / book_id
    summary_payload = {
        "job_id": str(job.get("job_id", "")),
        "status": str(job.get("status", "")),
        "book_id": book_id,
        "created_at": str(job.get("created_at", "")),
        "updated_at": str(job.get("updated_at", "")),
        "error": job.get("error"),
    }
    save_job_json(run_history_summary_file(output_dir, str(job.get("job_id", ""))), summary_payload)
    save_job_json(run_history_job_file(output_dir, str(job.get("job_id", ""))), job)

    activity_path = existing_activity_file(output_dir)
    history_trace_path = run_history_trace_file(output_dir, str(job.get("job_id", "")))
    history_trace_path.parent.mkdir(parents=True, exist_ok=True)
    if activity_path.exists():
        shutil.copy2(activity_path, history_trace_path)
    else:
        history_trace_path.write_text("", encoding="utf-8")

    source_log = job_log_file(str(job.get("job_id", "")), root)
    history_log = run_history_job_log_file(output_dir, str(job.get("job_id", "")))
    history_log.parent.mkdir(parents=True, exist_ok=True)
    if source_log.exists():
        shutil.copy2(source_log, history_log)
    else:
        history_log.write_text("", encoding="utf-8")
