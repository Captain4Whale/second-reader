"""Pure state-operation helpers for attentional_v2 runtime state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from .schemas import (
    AnchoredReactionRecord,
    LocalBufferSentence,
    LocalBufferState,
    ReactionRecordsState,
    ReaderPolicy,
    RecentReadingMemoryEntry,
    RecentReadingMemoryState,
    StateOperation,
)
from .memory_tokens import token_estimate_payload


ReflectiveBucket = Literal[
    "chapter_understandings",
    "book_level_frames",
    "durable_definitions",
    "stabilized_motifs",
    "resolved_questions_of_record",
    "chapter_end_notes",
]


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _touch_state(state: dict[str, object]) -> dict[str, object]:
    """Return one shallow-copied state with an updated timestamp."""

    next_state = dict(state)
    next_state["updated_at"] = _timestamp()
    return next_state


def _compact_text(value: object) -> str:
    """Return a compact text representation for legacy alias payloads."""

    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        parts: list[str] = []
        for key, nested_value in value.items():
            nested_text = _compact_text(nested_value)
            if nested_text:
                parts.append(f"{key}: {nested_text}")
        return "; ".join(parts)
    if isinstance(value, list):
        return "; ".join(text for text in (_compact_text(item) for item in value) if text)
    return str(value or "").strip()


def _recent_memory_entries(state: RecentReadingMemoryState) -> list[RecentReadingMemoryEntry]:
    """Return normalized recent-reading-memory entries."""

    return [dict(item) for item in state.get("entries", []) if isinstance(item, dict)]  # type: ignore[return-value]


def _chapter_token_from_unit_span_id(source_unit_span_id: str) -> str:
    """Return a compact chapter token from a unit span id when present."""

    parts = str(source_unit_span_id or "").split(":")
    if len(parts) >= 2 and parts[0] in {"unit", "src"} and parts[1]:
        return parts[1]
    return "c0"


def apply_recent_reading_memory_operations(
    state: RecentReadingMemoryState,
    operations: list[StateOperation],
    *,
    source_unit_span_id: str,
    created_at_unit_index: int,
) -> RecentReadingMemoryState:
    """Append Recent Reading Memory entries produced by one completed Digest unit."""

    entries = _recent_memory_entries(state)
    touched = False
    appended_for_unit = 0
    chapter_token = _chapter_token_from_unit_span_id(source_unit_span_id)
    unit_index = max(0, int(created_at_unit_index or 0))

    for operation in operations:
        if str(operation.get("target_store", "") or "") != "recent_reading_memory":
            continue
        operation_type = (
            str(operation.get("op", "") or operation.get("operation_type", "") or "")
            .strip()
            .lower()
            .replace("-", "_")
        )
        if operation_type != "append":
            continue
        payload = operation.get("payload")
        if not isinstance(payload, dict):
            continue
        memory_text = _compact_text(payload.get("memory_text"))
        if not memory_text:
            continue
        appended_for_unit += 1
        entry_id = f"recent:{chapter_token}:u{unit_index:04d}:m{appended_for_unit}"
        entry: RecentReadingMemoryEntry = {
            "entry_id": entry_id,
            "source_unit_span_id": str(source_unit_span_id or "").strip(),
            "memory_text": memory_text,
            "token_estimate": token_estimate_payload(memory_text),
            "status": "active",
            "created_at_unit_index": unit_index,
            "archived_by_consolidation_id": None,
        }
        entries.append(entry)
        touched = True

    if not touched:
        return state
    next_state = _touch_state(state)
    next_state["entries"] = entries
    return next_state  # type: ignore[return-value]


def push_local_buffer_sentence(
    state: LocalBufferState,
    sentence: LocalBufferSentence,
    *,
    window_size: int = 6,
) -> LocalBufferState:
    """Append one seen sentence to the rolling local buffer."""

    next_state = _touch_state(state)
    sentence_id = str(sentence.get("sentence_id", "") or "")
    recent = [dict(item) for item in state.get("recent_sentences", [])]
    recent.append(dict(sentence))
    if window_size > 0:
        recent = recent[-window_size:]
    seen_sentence_ids = [*state.get("seen_sentence_ids", [])]
    if sentence_id and sentence_id not in seen_sentence_ids:
        seen_sentence_ids.append(sentence_id)
    open_ids = [*state.get("open_meaning_unit_sentence_ids", [])]
    if sentence_id and sentence_id not in open_ids:
        open_ids.append(sentence_id)
    next_state["current_sentence_id"] = sentence_id
    next_state["current_sentence_index"] = int(sentence.get("sentence_index", 0) or 0)
    next_state["recent_sentences"] = recent
    next_state["seen_sentence_ids"] = seen_sentence_ids
    next_state["open_meaning_unit_sentence_ids"] = open_ids
    return next_state  # type: ignore[return-value]


def close_local_meaning_unit(state: LocalBufferState) -> LocalBufferState:
    """Close the current open meaning-unit span without dropping seen history."""

    next_state = _touch_state(state)
    recent_meaning_units = [
        [str(sentence_id or "") for sentence_id in unit if str(sentence_id or "")]
        for unit in state.get("recent_meaning_units", [])
        if isinstance(unit, list)
    ]
    current_unit = [sentence_id for sentence_id in state.get("open_meaning_unit_sentence_ids", []) if str(sentence_id or "")]
    if current_unit:
        recent_meaning_units.append(current_unit)
        recent_meaning_units = recent_meaning_units[-6:]
    next_state["last_meaning_unit_closed_at_sentence_id"] = str(state.get("current_sentence_id", "") or "")
    next_state["recent_meaning_units"] = recent_meaning_units
    next_state["open_meaning_unit_sentence_ids"] = []
    return next_state  # type: ignore[return-value]


def append_reaction_record(
    state: ReactionRecordsState,
    record: AnchoredReactionRecord,
) -> ReactionRecordsState:
    """Append one durable anchored reaction in occurrence order."""

    next_state = _touch_state(state)
    next_state["records"] = [*state.get("records", []), dict(record)]
    return next_state  # type: ignore[return-value]


def replace_policy_section(
    policy: ReaderPolicy,
    *,
    section: Literal["knowledge", "search", "bridge", "resume", "logging"],
    payload: dict[str, object],
) -> ReaderPolicy:
    """Replace one reader-policy section while preserving other policy data."""

    next_policy = _touch_state(policy)
    next_policy[section] = dict(payload)
    return next_policy  # type: ignore[return-value]
