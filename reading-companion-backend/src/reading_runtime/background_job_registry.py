"""Durable registry for long-running eval and dataset background jobs."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REGISTRY_VERSION = 1
ACTIVE_JOBS_FILE = "active_jobs.json"
ACTIVE_JOBS_SUMMARY_FILE = "active_jobs.md"
HISTORY_JOBS_FILE = "history_jobs.jsonl"
VALID_JOB_STATUSES = {"registered", "running", "completed", "failed", "abandoned"}
TERMINAL_JOB_STATUSES = {"completed", "failed", "abandoned"}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _state_dir(root: Path | None = None) -> Path:
    return (root or Path.cwd()) / "state"


def job_registry_dir(root: Path | None = None) -> Path:
    return _state_dir(root) / "job_registry"


def active_jobs_file(root: Path | None = None) -> Path:
    return job_registry_dir(root) / ACTIVE_JOBS_FILE


def active_jobs_summary_file(root: Path | None = None) -> Path:
    return job_registry_dir(root) / ACTIVE_JOBS_SUMMARY_FILE


def history_jobs_file(root: Path | None = None) -> Path:
    return job_registry_dir(root) / HISTORY_JOBS_FILE


def process_is_alive(pid: int | None) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def generate_job_id(prefix: str = "bgjob") -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"


def _empty_registry() -> dict[str, Any]:
    now = _timestamp()
    return {"version": REGISTRY_VERSION, "updated_at": now, "jobs": []}


def _ensure_registry_dir(root: Path | None = None) -> Path:
    path = job_registry_dir(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _dedupe_strings(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in items:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _normalize_optional_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text


def _normalize_optional_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_status(value: str | None, *, default: str) -> str:
    candidate = str(value or default).strip().lower()
    if candidate not in VALID_JOB_STATUSES:
        raise ValueError(f"Unsupported background job status: {candidate}")
    return candidate


def load_active_registry(root: Path | None = None) -> dict[str, Any]:
    path = active_jobs_file(root)
    if not path.exists():
        return _empty_registry()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON at {path}")
    jobs = payload.get("jobs", [])
    if not isinstance(jobs, list):
        raise ValueError(f"Expected jobs list at {path}")
    payload["version"] = int(payload.get("version", REGISTRY_VERSION) or REGISTRY_VERSION)
    payload["jobs"] = [dict(item) for item in jobs if isinstance(item, dict)]
    payload["updated_at"] = str(payload.get("updated_at", _timestamp()))
    return payload


def save_active_registry(payload: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    _ensure_registry_dir(root)
    normalized = dict(payload)
    normalized["version"] = REGISTRY_VERSION
    normalized["updated_at"] = _timestamp()
    normalized["jobs"] = [dict(item) for item in normalized.get("jobs", []) if isinstance(item, dict)]
    active_jobs_file(root).write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return normalized


def list_active_jobs(root: Path | None = None) -> list[dict[str, Any]]:
    return load_active_registry(root).get("jobs", [])


def get_active_job(job_id: str, root: Path | None = None) -> dict[str, Any] | None:
    for item in list_active_jobs(root):
        if str(item.get("job_id", "")) == job_id:
            return item
    return None


def _merge_job_fields(existing: dict[str, Any] | None, updates: dict[str, Any], *, create: bool) -> dict[str, Any]:
    record = dict(existing or {})
    now = _timestamp()
    if create:
        record["created_at"] = now
    elif "created_at" not in record:
        record["created_at"] = now

    for key, value in updates.items():
        if value is None:
            continue
        if key in {"expected_outputs"}:
            record[key] = _dedupe_strings(value if isinstance(value, list) else [str(value)])
        elif key in {"pid"}:
            record[key] = int(value) if value not in {"", None} else None
        elif key in {"latest_observation"}:
            record[key] = value if isinstance(value, dict) else {}
        else:
            record[key] = value

    required = ("job_id", "task_ref", "lane", "purpose", "command", "cwd")
    missing = [field for field in required if not str(record.get(field, "")).strip()]
    if missing:
        raise ValueError(f"Missing required background job fields: {', '.join(missing)}")

    record["job_id"] = str(record["job_id"]).strip()
    record["task_ref"] = str(record["task_ref"]).strip()
    record["lane"] = str(record["lane"]).strip()
    record["purpose"] = str(record["purpose"]).strip()
    record["command"] = str(record["command"]).strip()
    record["cwd"] = str(record["cwd"]).strip()
    record["status"] = _normalize_status(record.get("status"), default="registered" if create else str(record.get("status", "registered")))
    record["run_dir"] = _normalize_optional_path(record.get("run_dir"))
    record["status_file"] = _normalize_optional_path(record.get("status_file"))
    record["log_file"] = _normalize_optional_path(record.get("log_file"))
    record["check_command"] = _normalize_optional_text(record.get("check_command"))
    record["next_check_hint"] = _normalize_optional_text(record.get("next_check_hint"))
    record["decision_if_success"] = _normalize_optional_text(record.get("decision_if_success"))
    record["decision_if_failure"] = _normalize_optional_text(record.get("decision_if_failure"))
    record["notes"] = _normalize_optional_text(record.get("notes"))
    record["expected_outputs"] = _dedupe_strings(record.get("expected_outputs", []))
    record["updated_at"] = now
    return record


def upsert_background_job(
    *,
    job_id: str | None = None,
    root: Path | None = None,
    task_ref: str | None = None,
    lane: str | None = None,
    purpose: str | None = None,
    command: str | None = None,
    cwd: str | Path | None = None,
    pid: int | None = None,
    run_dir: str | Path | None = None,
    status_file: str | Path | None = None,
    log_file: str | Path | None = None,
    expected_outputs: list[str] | None = None,
    check_command: str | None = None,
    next_check_hint: str | None = None,
    decision_if_success: str | None = None,
    decision_if_failure: str | None = None,
    status: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    registry = load_active_registry(root)
    target_id = str(job_id).strip() if job_id else generate_job_id()
    existing_index = next((index for index, item in enumerate(registry["jobs"]) if str(item.get("job_id", "")) == target_id), None)
    existing = registry["jobs"][existing_index] if existing_index is not None else None

    updates = {
        "job_id": target_id,
        "task_ref": task_ref if task_ref is not None else (existing or {}).get("task_ref"),
        "lane": lane if lane is not None else (existing or {}).get("lane"),
        "purpose": purpose if purpose is not None else (existing or {}).get("purpose"),
        "command": command if command is not None else (existing or {}).get("command"),
        "cwd": str(cwd) if cwd is not None else (existing or {}).get("cwd"),
        "pid": pid if pid is not None else (existing or {}).get("pid"),
        "run_dir": str(run_dir) if run_dir is not None else (existing or {}).get("run_dir"),
        "status_file": str(status_file) if status_file is not None else (existing or {}).get("status_file"),
        "log_file": str(log_file) if log_file is not None else (existing or {}).get("log_file"),
        "expected_outputs": expected_outputs if expected_outputs is not None else (existing or {}).get("expected_outputs", []),
        "check_command": check_command if check_command is not None else (existing or {}).get("check_command"),
        "next_check_hint": next_check_hint if next_check_hint is not None else (existing or {}).get("next_check_hint"),
        "decision_if_success": decision_if_success if decision_if_success is not None else (existing or {}).get("decision_if_success"),
        "decision_if_failure": decision_if_failure if decision_if_failure is not None else (existing or {}).get("decision_if_failure"),
        "status": status if status is not None else (existing or {}).get("status", "registered"),
        "notes": notes if notes is not None else (existing or {}).get("notes"),
        "latest_observation": (existing or {}).get("latest_observation", {}),
    }

    record = _merge_job_fields(existing, updates, create=existing is None)
    if existing_index is None:
        registry["jobs"].append(record)
    else:
        registry["jobs"][existing_index] = record
    normalized_registry = save_active_registry(registry, root)
    write_active_jobs_summary(root, normalized_registry["jobs"])
    return record


def append_history_entry(record: dict[str, Any], root: Path | None = None) -> None:
    _ensure_registry_dir(root)
    entry = {"archived_at": _timestamp(), "job": record}
    with history_jobs_file(root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def archive_background_job(job_id: str, *, root: Path | None = None, archive_reason: str | None = None) -> dict[str, Any]:
    registry = load_active_registry(root)
    remaining: list[dict[str, Any]] = []
    archived: dict[str, Any] | None = None
    for item in registry["jobs"]:
        if str(item.get("job_id", "")) == job_id:
            archived = dict(item)
            archived["archived_at"] = _timestamp()
            archived["archive_reason"] = _normalize_optional_text(archive_reason)
            continue
        remaining.append(item)
    if archived is None:
        raise KeyError(f"Background job not found: {job_id}")
    append_history_entry(archived, root)
    registry["jobs"] = remaining
    normalized_registry = save_active_registry(registry, root)
    write_active_jobs_summary(root, normalized_registry["jobs"])
    return archived


def _load_status_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _run_check_command(command: str, cwd: str) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd or None,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    return {
        "exit_code": int(completed.returncode),
        "stdout": stdout[-4000:],
        "stderr": stderr[-4000:],
        "ok": completed.returncode == 0,
    }


def inspect_background_job(record: dict[str, Any], *, run_check_command: bool = False) -> dict[str, Any]:
    pid = record.get("pid")
    pid_alive = process_is_alive(pid if isinstance(pid, int) else None)

    status_file_path = Path(record["status_file"]) if str(record.get("status_file", "")).strip() else None
    status_payload: dict[str, Any] = {}
    status_file_status = ""
    if status_file_path and status_file_path.exists():
        status_payload = _load_status_payload(status_file_path)
        status_file_status = str(status_payload.get("status", "")).strip().lower()

    expected_output_entries: list[dict[str, Any]] = []
    for path_text in record.get("expected_outputs", []):
        output_path = Path(path_text)
        expected_output_entries.append({"path": str(output_path), "exists": output_path.exists()})

    check_result: dict[str, Any] = {}
    if run_check_command and str(record.get("check_command", "")).strip():
        check_result = _run_check_command(str(record["check_command"]), str(record["cwd"]))

    effective_status = str(record.get("status", "registered")).strip().lower()
    if status_file_status == "completed":
        effective_status = "completed"
    elif status_file_status in {"failed", "error", "incomplete"}:
        effective_status = "failed"
    elif effective_status in TERMINAL_JOB_STATUSES:
        effective_status = effective_status
    elif pid_alive:
        effective_status = "running"
    elif effective_status == "registered":
        effective_status = "registered"
    else:
        effective_status = "abandoned"

    return {
        "job_id": str(record.get("job_id", "")),
        "status": effective_status,
        "pid_alive": pid_alive,
        "status_file_exists": bool(status_file_path and status_file_path.exists()),
        "status_file_status": status_file_status,
        "status_payload": status_payload,
        "expected_outputs": expected_output_entries,
        "check_result": check_result,
        "checked_at": _timestamp(),
    }


def refresh_background_jobs(
    *,
    root: Path | None = None,
    job_ids: Iterable[str] | None = None,
    run_check_commands: bool = False,
    archive_terminal: bool = False,
) -> list[dict[str, Any]]:
    registry = load_active_registry(root)
    selected_ids = {str(job_id) for job_id in job_ids} if job_ids else None
    refreshed: list[dict[str, Any]] = []
    updated_jobs: list[dict[str, Any]] = []

    for item in registry["jobs"]:
        if selected_ids is not None and str(item.get("job_id", "")) not in selected_ids:
            updated_jobs.append(item)
            continue
        observation = inspect_background_job(item, run_check_command=run_check_commands)
        updated = dict(item)
        updated["status"] = observation["status"]
        updated["last_checked_at"] = observation["checked_at"]
        updated["latest_observation"] = observation
        updated["updated_at"] = _timestamp()
        refreshed.append(updated)
        if archive_terminal and observation["status"] in TERMINAL_JOB_STATUSES:
            archived = dict(updated)
            archived["archive_reason"] = "archived_by_checker"
            archived["archived_at"] = _timestamp()
            append_history_entry(archived, root)
            continue
        updated_jobs.append(updated)

    registry["jobs"] = updated_jobs
    normalized_registry = save_active_registry(registry, root)
    write_active_jobs_summary(root, normalized_registry["jobs"])
    return refreshed


def render_active_jobs_markdown(jobs: list[dict[str, Any]]) -> str:
    lines = ["# Active Background Jobs", "", f"Last updated: `{_timestamp()}`", ""]
    if not jobs:
        lines.append("- No active background jobs are currently registered.")
        return "\n".join(lines) + "\n"

    for job in jobs:
        observation = job.get("latest_observation", {}) if isinstance(job.get("latest_observation"), dict) else {}
        lines.append(f"## `{job.get('job_id', '')}`")
        lines.append(f"- Status: `{job.get('status', '')}`")
        lines.append(f"- Task ref: `{job.get('task_ref', '')}`")
        lines.append(f"- Lane: `{job.get('lane', '')}`")
        lines.append(f"- Purpose: {job.get('purpose', '')}")
        lines.append(f"- Command: `{job.get('command', '')}`")
        lines.append(f"- CWD: `{job.get('cwd', '')}`")
        if str(job.get("pid", "")).strip():
            lines.append(f"- PID: `{job.get('pid')}`")
        if str(job.get("run_dir", "")).strip():
            lines.append(f"- Run dir: `{job.get('run_dir', '')}`")
        if str(job.get("status_file", "")).strip():
            lines.append(f"- Status file: `{job.get('status_file', '')}`")
        if str(job.get("log_file", "")).strip():
            lines.append(f"- Log file: `{job.get('log_file', '')}`")
        if job.get("expected_outputs"):
            lines.append("- Expected outputs:")
            for path_text in job["expected_outputs"]:
                lines.append(f"  - `{path_text}`")
        if str(job.get("check_command", "")).strip():
            lines.append(f"- Check command: `{job.get('check_command', '')}`")
        if str(job.get("next_check_hint", "")).strip():
            lines.append(f"- Next check hint: {job.get('next_check_hint', '')}")
        if str(job.get("decision_if_success", "")).strip():
            lines.append(f"- If success: {job.get('decision_if_success', '')}")
        if str(job.get("decision_if_failure", "")).strip():
            lines.append(f"- If failure: {job.get('decision_if_failure', '')}")
        if observation:
            lines.append("- Latest observation:")
            lines.append(f"  - checked_at: `{observation.get('checked_at', '')}`")
            lines.append(f"  - pid_alive: `{observation.get('pid_alive', False)}`")
            if observation.get("status_file_status"):
                lines.append(f"  - status_file_status: `{observation.get('status_file_status', '')}`")
            outputs = observation.get("expected_outputs", [])
            if isinstance(outputs, list) and outputs:
                existing = sum(1 for item in outputs if isinstance(item, dict) and item.get("exists"))
                lines.append(f"  - expected_outputs_present: `{existing}/{len(outputs)}`")
            check_result = observation.get("check_result", {})
            if isinstance(check_result, dict) and check_result:
                lines.append(f"  - check_command_exit_code: `{check_result.get('exit_code')}`")
        lines.append("")
    return "\n".join(lines)


def write_active_jobs_summary(root: Path | None = None, jobs: list[dict[str, Any]] | None = None) -> Path:
    _ensure_registry_dir(root)
    payload = jobs if jobs is not None else list_active_jobs(root)
    path = active_jobs_summary_file(root)
    path.write_text(render_active_jobs_markdown(payload), encoding="utf-8")
    return path
