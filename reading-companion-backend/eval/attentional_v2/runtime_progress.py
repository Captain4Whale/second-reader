"""Lightweight runtime progress heartbeats for long-running eval mechanisms."""

from __future__ import annotations

import contextlib
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


def _read_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_last_jsonl_payload(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            file_size = handle.tell()
            if file_size <= 0:
                return None
            chunk_size = min(4096, file_size)
            buffer = b""
            position = file_size
            while position > 0:
                position = max(0, position - chunk_size)
                handle.seek(position)
                buffer = handle.read(file_size - position) + buffer
                lines = [line.strip() for line in buffer.splitlines() if line.strip()]
                if lines:
                    try:
                        payload = json.loads(lines[-1].decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        return None
                    return payload if isinstance(payload, dict) else None
                if position == 0:
                    break
    except OSError:
        return None
    return None


@dataclass(frozen=True)
class RuntimeProgressSnapshot:
    phase: str
    segment_ref: str
    run_state_updated_at: str
    last_llm_node: str
    last_llm_completed_at: str
    last_llm_duration_ms: int
    last_activity_type: str
    last_activity_segment_ref: str
    last_activity_timestamp: str

    def to_message(self, *, mechanism_key: str) -> str:
        parts = [f"[mechanism-heartbeat] {mechanism_key}"]
        if self.phase:
            parts.append(f"phase={self.phase}")
        if self.segment_ref:
            parts.append(f"segment={self.segment_ref}")
        if self.last_llm_node:
            parts.append(f"last_llm={self.last_llm_node}")
        if self.last_llm_completed_at:
            parts.append(f"llm_completed_at={self.last_llm_completed_at}")
        if self.last_llm_duration_ms > 0:
            parts.append(f"llm_duration_ms={self.last_llm_duration_ms}")
        if self.last_activity_type:
            activity = self.last_activity_type
            if self.last_activity_segment_ref:
                activity = f"{activity}@{self.last_activity_segment_ref}"
            parts.append(f"last_activity={activity}")
        if self.last_activity_timestamp:
            parts.append(f"activity_at={self.last_activity_timestamp}")
        if self.run_state_updated_at:
            parts.append(f"run_state_updated_at={self.run_state_updated_at}")
        return " ".join(parts)


def load_runtime_progress_snapshot(runtime_dir: Path) -> RuntimeProgressSnapshot | None:
    run_state = _read_json(runtime_dir / "run_state.json") or {}
    current_activity = run_state.get("current_reading_activity")
    activity_payload = current_activity if isinstance(current_activity, dict) else {}
    llm_payload = _read_last_jsonl_payload(runtime_dir / "llm_standard.jsonl") or {}
    last_activity_payload = _read_last_jsonl_payload(runtime_dir / "activity.jsonl") or {}
    phase = str(activity_payload.get("phase") or run_state.get("current_phase_step") or "").strip()
    segment_ref = str(activity_payload.get("segment_ref") or run_state.get("current_segment_ref") or "").strip()
    run_state_updated_at = str(run_state.get("updated_at") or "").strip()
    last_llm_node = str(llm_payload.get("node") or "").strip()
    last_llm_completed_at = str(llm_payload.get("completed_at") or "").strip()
    try:
        last_llm_duration_ms = int(llm_payload.get("duration_ms", 0) or 0)
    except (TypeError, ValueError):
        last_llm_duration_ms = 0
    last_activity_type = str(last_activity_payload.get("type") or "").strip()
    last_activity_segment_ref = str(last_activity_payload.get("segment_ref") or "").strip()
    last_activity_timestamp = str(last_activity_payload.get("timestamp") or "").strip()
    if not any(
        (
            phase,
            segment_ref,
            run_state_updated_at,
            last_llm_node,
            last_llm_completed_at,
            last_activity_type,
            last_activity_timestamp,
        )
    ):
        return None
    return RuntimeProgressSnapshot(
        phase=phase,
        segment_ref=segment_ref,
        run_state_updated_at=run_state_updated_at,
        last_llm_node=last_llm_node,
        last_llm_completed_at=last_llm_completed_at,
        last_llm_duration_ms=last_llm_duration_ms,
        last_activity_type=last_activity_type,
        last_activity_segment_ref=last_activity_segment_ref,
        last_activity_timestamp=last_activity_timestamp,
    )


class RuntimeProgressHeartbeat:
    """Emit low-frequency progress messages while a mechanism read is in flight."""

    def __init__(
        self,
        *,
        runtime_dir: Path,
        mechanism_key: str,
        emit: Callable[[str], None],
        poll_seconds: float = 20.0,
        repeat_seconds: float = 60.0,
    ) -> None:
        self.runtime_dir = runtime_dir
        self.mechanism_key = mechanism_key
        self.emit = emit
        self.poll_seconds = max(1.0, float(poll_seconds))
        self.repeat_seconds = max(self.poll_seconds, float(repeat_seconds))
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_message = ""
        self._last_emitted_at = 0.0

    def __enter__(self) -> "RuntimeProgressHeartbeat":
        self._thread = threading.Thread(target=self._loop, name=f"runtime-heartbeat-{self.mechanism_key}", daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        while not self._stop_event.wait(self.poll_seconds):
            snapshot = load_runtime_progress_snapshot(self.runtime_dir)
            if snapshot is None:
                continue
            message = snapshot.to_message(mechanism_key=self.mechanism_key)
            now = time.monotonic()
            if message != self._last_message or (now - self._last_emitted_at) >= self.repeat_seconds:
                self.emit(message)
                self._last_message = message
                self._last_emitted_at = now


@contextlib.contextmanager
def runtime_progress_heartbeat(
    *,
    runtime_dir: Path,
    mechanism_key: str,
    emit: Callable[[str], None],
    poll_seconds: float = 20.0,
    repeat_seconds: float = 60.0,
):
    heartbeat = RuntimeProgressHeartbeat(
        runtime_dir=runtime_dir,
        mechanism_key=mechanism_key,
        emit=emit,
        poll_seconds=poll_seconds,
        repeat_seconds=repeat_seconds,
    )
    with heartbeat:
        yield heartbeat
