"""Shared sequential artifact builders for multi-mechanism backend runs."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

from src.config import get_backend_version, get_reader_resume_compat_version
from src.reading_core.book_document import BookChapter, BookDocument

from . import artifacts as runtime_artifacts


RunStage = Literal["ready", "parsing_structure", "deep_reading", "completed", "paused", "error"]
ParseStatus = Literal["parsing_structure", "ready", "paused", "error"]
ChapterStatus = Literal["pending", "in_progress", "done"]

_CHAPTER_LABEL_PATTERNS = (
    r"^chapter\s+(\d+)\b",
    r"^第\s*(\d+)\s*章\b",
)
_SEGMENT_PROGRESS_THOUGHT_PREFIXES = ("🔗", "⚡", "💡", "✍️")
_SEGMENT_PROGRESS_SEARCH_PREFIXES = ("🔎", "🔍")


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Return one normalized string."""

    return str(value or "").strip()


def infer_chapter_number(title: str) -> int | None:
    """Infer a human-facing chapter number from a chapter title."""

    normalized = _clean_text(title)
    for pattern in _CHAPTER_LABEL_PATTERNS:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def chapter_reference(chapter: Mapping[str, object]) -> str:
    """Return the user-facing chapter reference for any mechanism."""

    number = chapter.get("chapter_number")
    if number is None:
        number = infer_chapter_number(_clean_text(chapter.get("title")))
    if number is not None:
        return f"Chapter {int(number)}"
    title = _clean_text(chapter.get("title"))
    return title or f"Chapter {int(chapter.get('id', 0) or 0)}"


def _source_asset_payload(output_dir: Path) -> dict[str, str]:
    """Return the shared source-asset payload."""

    return {
        "format": "epub",
        "file": str(runtime_artifacts.source_asset_file(output_dir).relative_to(output_dir)),
    }


def _chapter_metrics_from_result_path(path: Path | None) -> dict[str, int]:
    """Load compact chapter metrics when a compatibility result exists."""

    if path is None or not path.exists():
        return {
            "segment_count": 0,
            "visible_reaction_count": 0,
            "reaction_type_diversity": 0,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "segment_count": 0,
            "visible_reaction_count": 0,
            "reaction_type_diversity": 0,
        }
    sections = payload.get("sections", [])
    return {
        "segment_count": len(sections) if isinstance(sections, list) else 0,
        "visible_reaction_count": int(payload.get("visible_reaction_count", 0) or 0),
        "reaction_type_diversity": int(payload.get("reaction_type_diversity", 0) or 0),
    }


def build_minimal_book_manifest(
    output_dir: Path,
    *,
    book_title: str,
    author: str,
    book_language: str,
    output_language: str,
    source_file: str,
    chapters: Iterable[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Build a minimal manifest shell before a mechanism has derived chapter outputs."""

    cover_asset = runtime_artifacts.existing_cover_asset_file(output_dir)
    chapter_entries: list[dict[str, object]] = []
    for chapter in chapters or []:
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id <= 0:
            continue
        entry: dict[str, object] = {
            "id": chapter_id,
            "title": _clean_text(chapter.get("title")),
            "reference": chapter_reference(chapter),
            "status": _clean_text(chapter.get("status")) or "pending",
            "segment_count": int(chapter.get("segment_count", 0) or 0),
        }
        chapter_number = chapter.get("chapter_number")
        if chapter_number is not None:
            entry["chapter_number"] = int(chapter_number)
        chapter_heading = chapter.get("chapter_heading")
        if isinstance(chapter_heading, dict):
            entry["chapter_heading"] = dict(chapter_heading)
        result_file = _clean_text(chapter.get("result_file"))
        if result_file:
            entry["result_file"] = result_file
        markdown_file = _clean_text(chapter.get("markdown_file"))
        if markdown_file:
            entry["markdown_file"] = markdown_file
        if chapter.get("visible_reaction_count") is not None:
            entry["visible_reaction_count"] = int(chapter.get("visible_reaction_count", 0) or 0)
        if chapter.get("reaction_type_diversity") is not None:
            entry["reaction_type_diversity"] = int(chapter.get("reaction_type_diversity", 0) or 0)
        chapter_entries.append(entry)

    return {
        "book_id": runtime_artifacts.book_id_from_output_dir(output_dir),
        "book": _clean_text(book_title),
        "author": _clean_text(author) or "Unknown",
        "cover_image_url": str(cover_asset.relative_to(output_dir)) if cover_asset else None,
        "book_language": _clean_text(book_language) or "en",
        "output_language": _clean_text(output_language) or "en",
        "source_file": _clean_text(source_file),
        "source_asset": _source_asset_payload(output_dir),
        "updated_at": _timestamp(),
        "chapters": chapter_entries,
    }


def build_book_manifest_from_document(
    output_dir: Path,
    document: BookDocument,
    *,
    chapter_statuses: Mapping[int, ChapterStatus] | None = None,
    chapter_result_relative_paths: Mapping[int, str] | None = None,
) -> dict[str, object]:
    """Build a frontend-facing manifest from the shared parsed-book substrate."""

    metadata = dict(document.get("metadata", {}))
    chapter_entries: list[dict[str, object]] = []
    status_index = {int(key): value for key, value in (chapter_statuses or {}).items()}
    result_index = {int(key): str(value) for key, value in (chapter_result_relative_paths or {}).items()}
    for chapter in document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id <= 0:
            continue
        result_relative_path = result_index.get(chapter_id, "").strip() or None
        result_path = output_dir / result_relative_path if result_relative_path else None
        metrics = _chapter_metrics_from_result_path(result_path)
        entry: dict[str, object] = {
            "id": chapter_id,
            "title": _clean_text(chapter.get("title")),
            "reference": chapter_reference(chapter),
            "status": status_index.get(chapter_id, "done" if result_path and result_path.exists() else "pending"),
            "segment_count": metrics["segment_count"],
            "visible_reaction_count": metrics["visible_reaction_count"],
            "reaction_type_diversity": metrics["reaction_type_diversity"],
        }
        chapter_number = chapter.get("chapter_number")
        if chapter_number is not None:
            entry["chapter_number"] = int(chapter_number)
        chapter_heading = chapter.get("chapter_heading")
        if isinstance(chapter_heading, dict):
            entry["chapter_heading"] = dict(chapter_heading)
        if result_relative_path:
            entry["result_file"] = result_relative_path
        chapter_entries.append(entry)

    return build_minimal_book_manifest(
        output_dir,
        book_title=_clean_text(metadata.get("book")),
        author=_clean_text(metadata.get("author")),
        book_language=_clean_text(metadata.get("book_language")),
        output_language=_clean_text(metadata.get("output_language")),
        source_file=_clean_text(metadata.get("source_file")),
        chapters=chapter_entries,
    )


def write_book_manifest(output_dir: Path, manifest: Mapping[str, object]) -> dict[str, object]:
    """Persist one shared sequential book manifest."""

    path = runtime_artifacts.book_manifest_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(manifest)
    payload["updated_at"] = _timestamp()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def build_run_state(
    *,
    book_title: str,
    stage: RunStage,
    total_chapters: int,
    completed_chapters: int,
    current_chapter_id: int | None = None,
    current_chapter_ref: str | None = None,
    current_segment_ref: str | None = None,
    current_reading_activity: Mapping[str, object] | None = None,
    eta_seconds: int | None = None,
    current_phase_step: str | None = None,
    resume_available: bool = False,
    last_checkpoint_at: str | None = None,
    error: str | None = None,
) -> dict[str, object]:
    """Construct the shared sequential run-state payload."""

    return {
        "mode": "sequential",
        "stage": stage,
        "backend_version": get_backend_version(),
        "resume_compat_version": get_reader_resume_compat_version(),
        "book": _clean_text(book_title),
        "current_chapter_id": current_chapter_id,
        "current_chapter_ref": current_chapter_ref,
        "current_segment_ref": current_segment_ref,
        "current_reading_activity": dict(current_reading_activity) if current_reading_activity else None,
        "completed_chapters": int(completed_chapters),
        "total_chapters": int(total_chapters),
        "eta_seconds": eta_seconds if eta_seconds is None else max(0, int(eta_seconds)),
        "current_phase_step": current_phase_step,
        "resume_available": bool(resume_available),
        "last_checkpoint_at": last_checkpoint_at,
        "updated_at": _timestamp(),
        "error": error,
    }


def write_run_state(output_dir: Path, payload: Mapping[str, object]) -> dict[str, object]:
    """Persist the shared sequential run-state payload."""

    path = runtime_artifacts.run_state_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamped = dict(payload)
    stamped["updated_at"] = _timestamp()
    path.write_text(json.dumps(stamped, ensure_ascii=False, indent=2), encoding="utf-8")
    return stamped


def write_parse_progress(
    output_dir: Path,
    *,
    book_title: str,
    status: ParseStatus,
    total_chapters: int,
    completed_chapters: int,
    parsed_chapter_ids: list[int],
    inflight_chapter_ids: list[int] | None = None,
    pending_chapter_ids: list[int] | None = None,
    current_chapter_id: int | None = None,
    current_chapter_ref: str | None = None,
    current_step: str | None = None,
    worker_limit: int | None = None,
    last_checkpoint_at: str | None = None,
    error: str | None = None,
    sync_run_state: bool = True,
) -> dict[str, object]:
    """Persist parse-stage progress into shared parse-state and run-state files."""

    resume_available = bool(parsed_chapter_ids) or status in {"paused", "error"}
    normalized_parsed_ids = sorted(int(chapter_id) for chapter_id in parsed_chapter_ids)
    normalized_inflight_ids = sorted(int(chapter_id) for chapter_id in (inflight_chapter_ids or []))
    normalized_pending_ids = sorted(int(chapter_id) for chapter_id in (pending_chapter_ids or []))

    if sync_run_state:
        write_run_state(
            output_dir,
            build_run_state(
                book_title=book_title,
                stage="ready" if status == "ready" else status,
                total_chapters=total_chapters,
                completed_chapters=completed_chapters,
                current_chapter_id=current_chapter_id,
                current_chapter_ref=current_chapter_ref,
                current_phase_step=current_step,
                resume_available=resume_available,
                last_checkpoint_at=last_checkpoint_at,
                error=error,
            ),
        )

    payload = {
        "status": status,
        "backend_version": get_backend_version(),
        "resume_compat_version": get_reader_resume_compat_version(),
        "total_chapters": int(total_chapters),
        "completed_chapters": int(completed_chapters),
        "parsed_chapter_ids": normalized_parsed_ids,
        "segmented_chapter_ids": normalized_parsed_ids,
        "inflight_chapter_ids": normalized_inflight_ids,
        "pending_chapter_ids": normalized_pending_ids,
        "current_chapter_id": current_chapter_id,
        "current_chapter_ref": current_chapter_ref,
        "current_step": current_step,
        "worker_limit": worker_limit,
        "resume_available": resume_available,
        "last_checkpoint_at": last_checkpoint_at,
        "updated_at": _timestamp(),
        "error": error,
    }
    path = runtime_artifacts.parse_state_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def reset_activity(output_dir: Path) -> None:
    """Start a fresh shared activity stream."""

    path = runtime_artifacts.activity_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _progress_defaults_from_message(message: str) -> tuple[str, str, str]:
    """Classify one legacy progress line into stream/kind/visibility defaults."""

    stripped = _clean_text(message)
    if stripped.startswith("📖"):
        return "mindstream", "position", "default"
    if stripped.startswith(_SEGMENT_PROGRESS_THOUGHT_PREFIXES):
        return "mindstream", "thought", "default"
    if stripped.startswith(_SEGMENT_PROGRESS_SEARCH_PREFIXES):
        return "mindstream", "search", "default"
    if stripped.startswith("🤫"):
        return "mindstream", "transition", "collapsed"
    return "mindstream", "transition", "hidden"


def activity_semantics(event: Mapping[str, object]) -> tuple[str, str, str]:
    """Return stable stream/kind/visibility defaults for one activity event."""

    event_type = _clean_text(event.get("type"))
    if event_type == "segment_progress":
        return _progress_defaults_from_message(_clean_text(event.get("message")))
    defaults: dict[str, tuple[str, str, str]] = {
        "upload_received": ("system", "transition", "default"),
        "resume_detected": ("system", "transition", "default"),
        "parse_started": ("system", "parse", "default"),
        "parse_chapter_started": ("system", "parse", "default"),
        "parse_chapter_completed": ("system", "parse", "default"),
        "structure_checkpoint_saved": ("system", "checkpoint", "default"),
        "structure_ready": ("system", "transition", "default"),
        "reader_waiting_for_segments": ("system", "waiting", "default"),
        "runtime_stalled": ("system", "error", "default"),
        "heartbeat_lost": ("system", "error", "default"),
        "llm_timeout_detected": ("system", "error", "default"),
        "search_timeout_detected": ("system", "error", "default"),
        "runtime_environment_error": ("system", "error", "default"),
        "job_paused_by_runtime_guard": ("system", "error", "default"),
        "resume_incompatible": ("system", "error", "default"),
        "fresh_rerun_started": ("system", "transition", "default"),
        "dev_run_abandoned": ("system", "error", "default"),
        "chapter_started": ("mindstream", "transition", "collapsed"),
        "chapter_completed": ("mindstream", "chapter_complete", "default"),
        "run_completed": ("system", "transition", "default"),
        "error": ("system", "error", "default"),
    }
    return defaults.get(event_type, ("system", "transition", "default"))


def normalize_activity_event(event: Mapping[str, object]) -> dict[str, object]:
    """Fill activity semantics so persisted history stays self-describing."""

    payload = dict(event)
    stream, kind, visibility = activity_semantics(payload)
    payload["stream"] = _clean_text(payload.get("stream")) or stream
    payload["kind"] = _clean_text(payload.get("kind")) or kind
    payload["visibility"] = _clean_text(payload.get("visibility")) or visibility
    return payload


def _event_id(payload: Mapping[str, object]) -> str:
    """Return a stable persisted id for one activity event payload."""

    raw = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def append_activity_event(output_dir: Path, event: Mapping[str, object]) -> dict[str, object]:
    """Append one shared activity event."""

    payload = normalize_activity_event(event)
    payload["timestamp"] = _timestamp()
    payload["event_id"] = _clean_text(payload.get("event_id")) or _event_id(payload)
    path = runtime_artifacts.activity_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False))
        file.write("\n")
    return payload


def _load_recent_activity(path: Path, *, limit: int) -> list[dict[str, object]]:
    """Return the trailing activity items from one JSONL file."""

    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[dict[str, object]] = []
    for line in lines[-max(1, limit):]:
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            items.append(payload)
    return items


def _event_timestamp(event: Mapping[str, object]) -> datetime | None:
    """Parse one persisted event timestamp."""

    raw = _clean_text(event.get("timestamp"))
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _same_activity_signature(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    """Compare activity events on the fields that make them operationally identical."""

    fields = (
        "type",
        "message",
        "chapter_id",
        "chapter_ref",
        "segment_id",
        "segment_ref",
        "problem_code",
    )
    return all(_clean_text(left.get(field)) == _clean_text(right.get(field)) for field in fields)


def append_deduped_activity_event(
    output_dir: Path,
    event: Mapping[str, object],
    *,
    dedupe_window_seconds: int = 300,
    history_limit: int = 120,
) -> dict[str, object] | None:
    """Append one event unless a near-identical recent event already exists."""

    candidate = normalize_activity_event(dict(event))
    path = runtime_artifacts.activity_file(output_dir)
    if path.exists():
        try:
            history = _load_recent_activity(path, limit=history_limit)
        except (OSError, json.JSONDecodeError, ValueError):
            history = []
        candidate_timestamp = _event_timestamp({"timestamp": _timestamp()})
        for item in reversed(history):
            if not _same_activity_signature(item, candidate):
                continue
            item_timestamp = _event_timestamp(item)
            if item_timestamp is None or candidate_timestamp is None:
                return None
            age_seconds = (candidate_timestamp - item_timestamp).total_seconds()
            if 0 <= age_seconds <= dedupe_window_seconds:
                return None
    return append_activity_event(output_dir, candidate)
