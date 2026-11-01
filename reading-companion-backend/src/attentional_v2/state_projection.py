"""Internal state-ownership and packetization helpers for live prompt inputs."""

from __future__ import annotations

from .schemas import (
    ATTENTIONAL_V2_SCHEMA_VERSION,
    CarryForwardContext,
    CarryForwardRef,
    ContinuationCapsule,
    LocalBufferState,
    ReactionRecordsState,
    RecentReadingMemoryDigest,
    RecentReadingMemoryState,
    SourceRef,
    build_empty_recent_reading_memory,
)
from .source_spans import dedupe_source_refs


STATE_PACKET_VERSION = "attentional_v2.state_packet.v1"


def clean_text(value: object) -> str:
    """Normalize one free-text value."""

    return str(value or "").strip()


def _append_ref(refs: list[CarryForwardRef], ref: CarryForwardRef) -> None:
    """Append one ref if its id is present and not already emitted."""

    ref_id = clean_text(ref.get("ref_id"))
    if not ref_id or any(clean_text(existing.get("ref_id")) == ref_id for existing in refs):
        return
    refs.append(ref)


def _dedupe_ids(values: list[str]) -> list[str]:
    """Return one order-preserving de-duplicated id list."""

    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        clean_value = clean_text(value)
        if not clean_value or clean_value in seen:
            continue
        seen.add(clean_value)
        ordered.append(clean_value)
    return ordered


def _source_refs(value: object) -> list[SourceRef]:
    """Return normalized inline source refs from one state field."""

    return dedupe_source_refs(value)








def _with_visible_trace_markers(record: dict[str, object]) -> dict[str, object]:
    """Copy one visible reaction projection with non-semantic-memory markers."""

    marked = dict(record)
    marked.update(
        {
            "projection_role": "visible_trace",
            "support_status": "visible_trace",
            "visible_trace_support": True,
            "current_support": False,
            "projection_warning": "visible_trace_not_semantic_memory",
        }
    )
    return marked


def _build_recent_reading_memory_digest(
    recent_reading_memory: RecentReadingMemoryState,
) -> RecentReadingMemoryDigest:
    """Build the prompt-facing active recent reading memory packet."""

    active_entries: list[dict[str, object]] = []
    for entry in recent_reading_memory.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if clean_text(entry.get("status")).lower() != "active":
            continue
        entry_id = clean_text(entry.get("entry_id"))
        memory_text = clean_text(entry.get("memory_text"))
        if not entry_id or not memory_text:
            continue
        active_entries.append(
            {
                "entry_id": entry_id,
                "memory_text": memory_text,
                "source_unit_span_id": clean_text(entry.get("source_unit_span_id")),
                "created_at_unit_index": int(entry.get("created_at_unit_index", 0) or 0),
            }
        )
    return {
        "active_entries": active_entries,
        "active_entry_count": len(active_entries),
    }


def _status_by_key(entries: list[object], key_name: str) -> dict[str, str]:
    """Return source-state status by entry key for prompt-facing marker calculation."""

    statuses: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = clean_text(entry.get(key_name))
        if key:
            statuses[key] = clean_text(entry.get("status"))
    return statuses


def _build_recent_reactions(
    reaction_records: ReactionRecordsState,
    *,
    refs: list[CarryForwardRef],
) -> list[dict[str, object]]:
    """Build a bounded recent-reactions digest."""

    recent_reactions: list[dict[str, object]] = []
    for record in list(reaction_records.get("records", []))[-3:]:
        if not isinstance(record, dict):
            continue
        reaction_id = clean_text(record.get("reaction_id"))
        if not reaction_id:
            continue
        primary_source_ref = (
            dict(record.get("primary_source_ref", {}))
            if isinstance(record.get("primary_source_ref"), dict)
            else {}
        )
        ref_id = f"reaction:{reaction_id}"
        reaction_record = {
            "ref_id": ref_id,
            "reaction_id": reaction_id,
            "type": clean_text(record.get("type")),
            "thought": clean_text(record.get("thought")),
            "emitted_at_source_span_id": clean_text(record.get("emitted_at_source_span_id")),
            "primary_source_ref": primary_source_ref,
            "source_quote": clean_text(record.get("source_quote") or primary_source_ref.get("quote")),
        }
        recent_reactions.append(reaction_record)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "reaction",
                "item_id": reaction_id,
                "summary": clean_text(record.get("thought")) or clean_text(record.get("type")),
                "reaction_id": reaction_id,
                "source_span_id": clean_text(primary_source_ref.get("source_span_id")),
                "source_ref": primary_source_ref,
            },
        )
    return recent_reactions


def _build_session_continuity_capsule(
    local_buffer: LocalBufferState,
    *,
    excluded_sentence_ids: set[str],
    recent_reactions: list[dict[str, object]],
) -> dict[str, object]:
    """Build a cheap always-carried continuity capsule."""

    recent_sentence_ids = [
        clean_text(sentence.get("sentence_id"))
        for sentence in local_buffer.get("recent_sentences", [])
        if isinstance(sentence, dict)
        and clean_text(sentence.get("sentence_id"))
        and clean_text(sentence.get("sentence_id")) not in excluded_sentence_ids
    ][-6:]
    recent_meaning_units = [
        [sentence_id for sentence_id in unit if clean_text(sentence_id) and clean_text(sentence_id) not in excluded_sentence_ids]
        for unit in local_buffer.get("recent_meaning_units", [])
        if isinstance(unit, list)
    ][-2:]
    return {
        "recent_sentence_ids": recent_sentence_ids,
        "recent_meaning_units": recent_meaning_units,
        "recent_reactions": recent_reactions,
    }


def build_continuation_capsule(
    *,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    recent_reading_memory_digest: RecentReadingMemoryDigest,
    session_continuity_capsule: dict[str, object],
    refs: list[CarryForwardRef],
    mechanism_version: str,
) -> ContinuationCapsule:
    """Build one persisted continuity capsule from the current live digests."""

    return {
        "schema_version": ATTENTIONAL_V2_SCHEMA_VERSION,
        "mechanism_version": mechanism_version,
        "updated_at": clean_text(local_buffer.get("updated_at")),
        "chapter_ref": clean_text(chapter_ref),
        "current_sentence_id": clean_text(local_buffer.get("current_sentence_id")),
        "session_continuity_capsule": dict(session_continuity_capsule),
        "recent_reading_memory": dict(recent_reading_memory_digest),
        "refs": [dict(ref) for ref in refs if isinstance(ref, dict)],
    }


def build_carry_forward_context(
    *,
    chapter_ref: str,
    current_unit_sentence_ids: list[str],
    local_buffer: LocalBufferState,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    reaction_records: ReactionRecordsState,
    continuation_capsule: ContinuationCapsule | None = None,
) -> CarryForwardContext:
    """Build the bounded carry-forward context packet from current persisted state."""

    primary_recent_reading_memory = dict(recent_reading_memory) if isinstance(recent_reading_memory, dict) else build_empty_recent_reading_memory()
    excluded_sentence_ids = {clean_text(item) for item in current_unit_sentence_ids if clean_text(item)}
    refs: list[CarryForwardRef] = []
    recent_reading_memory_digest = _build_recent_reading_memory_digest(primary_recent_reading_memory)
    recent_reactions = _build_recent_reactions(reaction_records, refs=refs)
    session = _build_session_continuity_capsule(local_buffer, excluded_sentence_ids=excluded_sentence_ids, recent_reactions=recent_reactions)
    capsule = dict(continuation_capsule) if continuation_capsule else build_continuation_capsule(
        chapter_ref=chapter_ref, local_buffer=local_buffer,
        recent_reading_memory_digest=recent_reading_memory_digest,
        session_continuity_capsule=session, refs=refs,
        mechanism_version=clean_text(local_buffer.get("mechanism_version")),
    )
    marked_session = _build_session_continuity_capsule(local_buffer, excluded_sentence_ids=excluded_sentence_ids,
        recent_reactions=[_with_visible_trace_markers(item) for item in recent_reactions])
    return {
        "packet_version": STATE_PACKET_VERSION, "continuation_capsule": capsule,
        "session_continuity_capsule": marked_session, "recent_reading_memory": recent_reading_memory_digest,
        "source_ref_digest": [dict(ref.get("source_ref", {})) for ref in refs if isinstance(ref.get("source_ref"), dict)][:8],
        "continuity_digest": marked_session, "refs": refs,
    }


def build_digest_prompt_packet(
    *,
    carry_forward_context: CarryForwardContext,
) -> dict[str, object]:
    """Project persisted state into the narrow Digest prompt view."""
    return {
        "packet_version": clean_text(carry_forward_context.get("packet_version")) or STATE_PACKET_VERSION,
        "local_continuity": dict(carry_forward_context.get("session_continuity_capsule", {})),
        "recent_reading_memory": dict(carry_forward_context.get("recent_reading_memory", {})),
    }


def context_ref_ids(*contexts: dict[str, object] | None) -> set[str]:
    """Return all declared reference ids from one or more context packets."""

    ref_ids: set[str] = set()
    for context in contexts:
        if not isinstance(context, dict):
            continue
        for ref in context.get("refs", []):
            if isinstance(ref, dict) and clean_text(ref.get("ref_id")):
                ref_ids.add(clean_text(ref.get("ref_id")))
        if isinstance(context.get("excerpts"), list):
            for excerpt in context.get("excerpts", []):
                if isinstance(excerpt, dict) and clean_text(excerpt.get("ref_id")):
                    ref_ids.add(clean_text(excerpt.get("ref_id")))
    return ref_ids
