"""Append-only local fact ledger for runtime observability events."""

from __future__ import annotations

import json
import hashlib
import os
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

try:  # pragma: no cover - the backend's supported runtimes are POSIX.
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


OBSERVATION_EVENT_SCHEMA_VERSION = 1
OBSERVATION_LEDGER_FILENAME = "events.jsonl"
_PROCESS_WRITE_LOCK = threading.Lock()
_PROCESS_DIAGNOSTICS_LOCK = threading.Lock()
_PROCESS_WRITE_FAILURES: dict[str, int] = {}
_PROCESS_PENDING_WRITE_FAILURES: dict[str, dict[str, Any]] = {}


@dataclass(frozen=True)
class ObservationRecordResult:
    """Best-effort result returned by observation record helpers."""

    event: dict[str, Any]
    ledger_path: Path | None
    written: bool
    error: str | None = None


class ObservationLedgerReadError(OSError):
    """Raised when an existing ledger cannot be read safely."""


def _safe_job_id(job_id: str) -> str:
    value = str(job_id or "").strip()
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("job_id must be a non-empty path-safe identifier")
    return value


def observation_dir(output_dir: Path | str, job_id: str) -> Path:
    """Return the canonical observability directory for one product job."""

    return Path(output_dir) / "_history" / "runs" / _safe_job_id(job_id) / "observability"


def observation_ledger_file(output_dir: Path | str, job_id: str) -> Path:
    """Return the canonical append-only JSONL ledger path for one product job."""

    return observation_dir(output_dir, job_id) / OBSERVATION_LEDGER_FILENAME


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _diagnostic_key(path: Path) -> str:
    return str(path.expanduser().absolute())


def _record_write_failure(
    path: Path | None,
    *,
    event: Mapping[str, object] | None = None,
    error: BaseException | None = None,
) -> None:
    if path is None:
        return
    key = _diagnostic_key(path)
    with _PROCESS_DIAGNOSTICS_LOCK:
        total = _PROCESS_WRITE_FAILURES.get(key, 0) + 1
        _PROCESS_WRITE_FAILURES[key] = total
        pending = _PROCESS_PENDING_WRITE_FAILURES.setdefault(
            key,
            {
                "failure_count": 0,
                "total_failure_count": total,
                "event_context": {},
                "last_error_type": None,
            },
        )
        pending["failure_count"] = int(pending.get("failure_count", 0) or 0) + 1
        pending["total_failure_count"] = total
        if error is not None:
            pending["last_error_type"] = type(error).__name__
        context_fields = {
            key: value
            for key in (
                "job_id",
                "job_kind",
                "run_id",
                "run_attempt_id",
                "book_id",
                "mechanism_key",
                "chapter_id",
                "reading_cycle_id",
                "unit_id",
                "stage",
                "node",
            )
            if event is not None and (value := event.get(key)) is not None
        }
        if context_fields:
            pending["event_context"] = context_fields


def observation_ledger_diagnostics(ledger_path: Path | str) -> dict[str, int]:
    """Return process-local failures that could not be represented in the ledger itself."""

    key = _diagnostic_key(Path(ledger_path))
    with _PROCESS_DIAGNOSTICS_LOCK:
        return {"write_failure_count": _PROCESS_WRITE_FAILURES.get(key, 0)}


def _pending_failure_event(path: Path) -> dict[str, Any] | None:
    key = _diagnostic_key(path)
    with _PROCESS_DIAGNOSTICS_LOCK:
        pending = _PROCESS_PENDING_WRITE_FAILURES.get(key)
        if not pending:
            return None
        failure_count = int(pending.get("failure_count", 0) or 0)
        total_failure_count = int(pending.get("total_failure_count", 0) or 0)
        context = dict(pending.get("event_context") or {})
        last_error_type = str(pending.get("last_error_type") or "observation_write_error")
    return prepare_observation_event(
        {
            **context,
            "event_id": deterministic_event_id(
                "ledger_write_failed",
                _diagnostic_key(path),
                total_failure_count,
            ),
            "event_kind": "ledger_write_failed",
            "status": "error",
            "failure_count": failure_count,
            "total_failure_count": total_failure_count,
            "error_type": last_error_type,
            "recovered": True,
        }
    )


def _clear_pending_failure_event(path: Path, *, total_failure_count: int) -> None:
    key = _diagnostic_key(path)
    with _PROCESS_DIAGNOSTICS_LOCK:
        pending = _PROCESS_PENDING_WRITE_FAILURES.get(key)
        if pending and int(pending.get("total_failure_count", 0) or 0) == total_failure_count:
            _PROCESS_PENDING_WRITE_FAILURES.pop(key, None)


def deterministic_event_id(event_kind: str, *identity_parts: object) -> str:
    """Build a stable id for one logical fact so retries can be deduplicated."""

    identity = [
        str(event_kind or "").strip(),
        *("" if part is None else str(part).strip() for part in identity_parts),
    ]
    encoded = json.dumps(identity, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return f"evt_{hashlib.sha256(encoded).hexdigest()}"


def _json_default(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return normalized.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Unsupported observation value: {type(value).__name__}")


def prepare_observation_event(event: Mapping[str, object]) -> dict[str, Any]:
    """Copy and version one event without mutating the caller's mapping."""

    payload = dict(event)
    event_kind = str(payload.get("event_kind") or "").strip()
    if not event_kind:
        raise ValueError("observation event_kind is required")
    supplied_version = payload.get("schema_version", OBSERVATION_EVENT_SCHEMA_VERSION)
    if supplied_version != OBSERVATION_EVENT_SCHEMA_VERSION:
        raise ValueError(f"unsupported observation event schema_version: {supplied_version!r}")
    payload["schema_version"] = OBSERVATION_EVENT_SCHEMA_VERSION
    payload["event_kind"] = event_kind
    payload.setdefault("event_id", uuid.uuid4().hex)
    payload.setdefault("observed_at", _utc_now())
    return payload


def _encoded_event(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=_json_default) + "\n"
    ).encode("utf-8")


def _write_all(descriptor: int, encoded: bytes) -> None:
    view = memoryview(encoded)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("observation ledger write made no progress")
        view = view[written:]


def _append_line_locked(descriptor: int, encoded: bytes) -> None:
    """Append one complete JSONL row or restore the preceding file boundary.

    ``os.write`` may report a short write and a later write may fail.  Because
    callers hold both the process lock and the cross-process file lock here,
    truncating back to the pre-row EOF is safe and prevents a recovered
    diagnostic from being concatenated onto an invalid JSON fragment.
    """

    starting_offset = os.lseek(descriptor, 0, os.SEEK_END)
    try:
        _write_all(descriptor, encoded)
    except BaseException:
        try:
            os.ftruncate(descriptor, starting_offset)
            os.lseek(descriptor, 0, os.SEEK_END)
        except OSError:
            # Preserve the original write failure.  A rollback failure is
            # still surfaced through the same durable/process diagnostics.
            pass
        raise


def append_observation_event(
    ledger_path: Path | str | None,
    event: Mapping[str, object],
) -> ObservationRecordResult:
    """Append one event in a single locked record, never mutating existing rows.

    Runtime observability is best effort: serialization and I/O failures are
    returned to callers rather than raised into the reader control flow.
    """

    try:
        payload = prepare_observation_event(event)
    except Exception as exc:
        resolved_path = Path(ledger_path) if ledger_path is not None else None
        _record_write_failure(resolved_path, event=event, error=exc)
        return ObservationRecordResult(
            event=dict(event),
            ledger_path=resolved_path,
            written=False,
            error=f"{type(exc).__name__}: {exc}",
        )
    path = Path(ledger_path) if ledger_path is not None else None
    if path is None:
        return ObservationRecordResult(event=payload, ledger_path=None, written=False)
    try:
        encoded = _encoded_event(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        with _PROCESS_WRITE_LOCK:
            descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                if fcntl is not None:
                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                diagnostic = _pending_failure_event(path)
                if diagnostic is not None:
                    _append_line_locked(descriptor, _encoded_event(diagnostic))
                    _clear_pending_failure_event(
                        path,
                        total_failure_count=int(diagnostic["total_failure_count"]),
                    )
                _append_line_locked(descriptor, encoded)
            finally:
                if fcntl is not None:
                    try:
                        fcntl.flock(descriptor, fcntl.LOCK_UN)
                    except OSError:
                        pass
                os.close(descriptor)
        return ObservationRecordResult(event=payload, ledger_path=path, written=True)
    except Exception as exc:
        _record_write_failure(path, event=payload, error=exc)
        return ObservationRecordResult(
            event=payload,
            ledger_path=path,
            written=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def flush_observation_ledger_diagnostics(ledger_path: Path | str) -> bool:
    """Persist recovered write failures before an offline-rebuildable report.

    A total directory/filesystem outage cannot be represented on that same
    filesystem. In that case the process-local counter remains available to
    the in-process report result and this function returns ``False``.
    """

    path = Path(ledger_path)
    diagnostic = _pending_failure_event(path)
    if diagnostic is None:
        return True
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with _PROCESS_WRITE_LOCK:
            descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                if fcntl is not None:
                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                _append_line_locked(descriptor, _encoded_event(diagnostic))
                _clear_pending_failure_event(
                    path,
                    total_failure_count=int(diagnostic["total_failure_count"]),
                )
            finally:
                if fcntl is not None:
                    try:
                        fcntl.flock(descriptor, fcntl.LOCK_UN)
                    except OSError:
                        pass
                os.close(descriptor)
        return True
    except Exception as exc:
        _record_write_failure(path, event=diagnostic, error=exc)
        return False


def load_observation_events(ledger_path: Path | str) -> tuple[list[dict[str, Any]], int]:
    """Load valid object rows and return their malformed-line count."""

    path = Path(ledger_path)
    if not path.exists():
        return [], 0
    events: list[dict[str, Any]] = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ObservationLedgerReadError(
            f"observation ledger could not be read: {type(exc).__name__}"
        ) from exc
    for line in lines:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(payload, dict):
            malformed += 1
            continue
        events.append(payload)
    return events, malformed


__all__ = [
    "OBSERVATION_EVENT_SCHEMA_VERSION",
    "OBSERVATION_LEDGER_FILENAME",
    "ObservationLedgerReadError",
    "ObservationRecordResult",
    "append_observation_event",
    "deterministic_event_id",
    "flush_observation_ledger_diagnostics",
    "load_observation_events",
    "observation_ledger_diagnostics",
    "observation_dir",
    "observation_ledger_file",
    "prepare_observation_event",
]
