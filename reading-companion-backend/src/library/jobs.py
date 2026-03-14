"""Background job helpers for uploaded sequential deep-read runs."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from .catalog import find_book_id_by_source, get_book, source_asset_path
from .storage import job_file, job_log_file, load_json, save_json, timestamp, upload_file
from src.iterator_reader.storage import (
    existing_activity_file,
    existing_run_state_file,
    run_history_job_file,
    run_history_job_log_file,
    run_history_summary_file,
    run_history_trace_file,
)


def _job_record(
    *,
    job_id: str,
    status: str,
    upload_path: Path,
    book_id: str | None = None,
    pid: int | None = None,
    error: str | None = None,
    created_at: str | None = None,
) -> dict:
    """Build one persisted job record."""
    now = timestamp()
    return {
        "job_id": job_id,
        "status": status,
        "upload_path": str(upload_path),
        "book_id": book_id,
        "pid": pid,
        "created_at": created_at or now,
        "updated_at": now,
        "error": error,
    }


def _process_running(pid: int | None) -> bool:
    """Return whether a subprocess still appears alive."""
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def _status_from_run_state(run_state: dict | None, *, running: bool) -> tuple[str, str | None]:
    """Map sequential run_state into the public job status vocabulary."""
    if not run_state:
        return ("parsing_structure" if running else "queued"), None

    stage = str(run_state.get("stage", "")).strip()
    error = str(run_state.get("error", "") or "") or None
    if stage == "deep_reading":
        return "deep_reading", error
    if stage == "completed":
        return "completed", error
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
    record["updated_at"] = timestamp()
    save_json(job_file(str(record["job_id"]), root), record)
    return record


def load_job(job_id: str, root: Path | None = None) -> dict:
    """Load one job record."""
    return load_json(job_file(job_id, root))


def _launch_subprocess_job(
    *,
    upload_path: Path,
    command: list[str],
    root: Path | None = None,
    job_id: str | None = None,
    initial_status: str = "queued",
) -> dict:
    """Start a detached subprocess and persist the tracking record."""
    resolved_job_id = job_id or upload_path.stem
    record = _job_record(job_id=resolved_job_id, status=initial_status, upload_path=upload_path)
    save_job(record, root)

    log_path = job_log_file(resolved_job_id, root)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log:
        process = subprocess.Popen(
            command,
            cwd=str(root or Path.cwd()),
            stdout=log,
            stderr=subprocess.STDOUT,
        )

    return save_job(
        _job_record(
            job_id=resolved_job_id,
            status=initial_status,
            upload_path=upload_path,
            pid=process.pid,
            created_at=str(record["created_at"]),
        ),
        root,
    )


def launch_sequential_job(
    upload_path: Path,
    *,
    language: str = "auto",
    intent: str | None = None,
    root: Path | None = None,
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
    if intent:
        command.extend(["--intent", intent])

    return _launch_subprocess_job(
        upload_path=upload_path,
        command=command,
        root=root,
        initial_status="queued",
    )


def launch_parse_job(
    upload_path: Path,
    *,
    language: str = "auto",
    root: Path | None = None,
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
    return _launch_subprocess_job(
        upload_path=upload_path,
        command=command,
        root=root,
        initial_status="queued",
    )


def launch_book_analysis_job(
    book_id: str,
    *,
    language: str = "auto",
    intent: str | None = None,
    root: Path | None = None,
) -> dict:
    """Start sequential analysis for an existing uploaded book."""
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
    if intent:
        command.extend(["--intent", intent])

    return _launch_subprocess_job(
        upload_path=source_path,
        command=command,
        root=root,
        job_id=uuid.uuid4().hex[:12],
        initial_status="queued",
    )


def refresh_job(job_id: str, root: Path | None = None) -> dict:
    """Refresh one job record from process state and sequential artifacts."""
    record = load_job(job_id, root)
    upload_path = Path(str(record.get("upload_path", "")))
    pid = int(record["pid"]) if record.get("pid") else None
    running = _process_running(pid)
    book_id = find_book_id_by_source(upload_path, root=root)
    error = str(record.get("error", "") or "") or None
    status = str(record.get("status", "queued"))

    if book_id:
        book = get_book(book_id, root=root)
        run_state = book.get("run_state") or {}
        status, state_error = _status_from_run_state(run_state, running=running)
        error = state_error or error
    elif running:
        status = "parsing_structure"

    if not running and status not in {"completed", "error", "ready"}:
        if book_id:
            state_path = existing_run_state_file((root or Path.cwd()) / "output" / book_id)
            if state_path.exists():
                run_state = load_json(state_path)
                status, state_error = _status_from_run_state(run_state, running=False)
                error = state_error or error
        if status not in {"completed", "error"}:
            status = "completed" if book_id else "error"
            if status == "error" and not error:
                error = "Job exited before producing readable artifacts."

    refreshed = _job_record(
        job_id=job_id,
        status=status,
        upload_path=upload_path,
        book_id=book_id,
        pid=pid,
        error=error,
        created_at=str(record.get("created_at", timestamp())),
    )
    saved = save_job(refreshed, root)
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
    save_json(run_history_summary_file(output_dir, str(job.get("job_id", ""))), summary_payload)
    save_json(run_history_job_file(output_dir, str(job.get("job_id", ""))), job)

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
