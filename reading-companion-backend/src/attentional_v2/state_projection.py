"""Internal state-ownership and packetization helpers for live prompt inputs."""

from __future__ import annotations

from .schemas import (
    ATTENTIONAL_V2_SCHEMA_VERSION,
    ActiveFocusDigest,
    AnchorMemoryState,
    CarryForwardContext,
    CarryForwardRef,
    ContinuationCapsule,
    LocalBufferState,
    ReactionRecordsState,
    ReflectiveFrameDigest,
    ReflectiveFramesState,
    ReflectiveItem,
    ReflectiveSummariesState,
    RecentReadingMemoryDigest,
    RecentReadingMemoryState,
    SourceRef,
    ActiveAttention,
    ActiveAttentionDigest,
    build_empty_active_attention,
    build_empty_recent_reading_memory,
)
from .source_spans import dedupe_source_refs
from .state_migration import migrate_reflective_summaries_to_frames, normalize_active_tension_state


STATE_PACKET_VERSION = "attentional_v2.state_packet.v1"
_DIGEST_QUOTE_LIMIT = 2
_LINEAGE_ONLY_STATUSES = {
    "answered",
    "closed",
    "resolved",
    "superseded",
    "invalidated",
    "rejected",
    "dropped",
    "retired",
}
_OPEN_ACTIVE_ATTENTION_STATUSES = {"", "active", "cooling", "open"}
_ACTIVE_TENSION_SOFT_LIMIT = 6


def clean_text(value: object) -> str:
    """Normalize one free-text value."""

    return str(value or "").strip()


def matching_chapter_items(items: list[ReflectiveItem], *, chapter_ref: str, limit: int) -> list[dict[str, object]]:
    """Return chapter-matching reflective items with a bounded fallback."""

    matching = [
        dict(item)
        for item in items
        if isinstance(item, dict) and clean_text(item.get("chapter_ref")) == clean_text(chapter_ref)
    ]
    if matching:
        return matching[:limit]
    return [dict(item) for item in items[:limit] if isinstance(item, dict)]


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


def _sample_quotes(source_refs: list[SourceRef], *, limit: int = _DIGEST_QUOTE_LIMIT) -> list[str]:
    """Collect a small quote sample from inline source refs."""

    quotes: list[str] = []
    for source_ref in source_refs:
        quote = clean_text(source_ref.get("quote"))
        if quote and quote not in quotes:
            quotes.append(quote)
        if len(quotes) >= limit:
            break
    return quotes


def _active_attention_items(active_attention: ActiveAttention) -> list[dict[str, object]]:
    """Return the active-items view over the current active attention."""

    active_items = [dict(item) for item in active_attention.get("active_items", []) if isinstance(item, dict)]
    return active_items


def _item_tags(item: dict[str, object]) -> list[str]:
    """Return clean lightweight attention tags for one active-attention item."""

    raw_tags = item.get("attention_tags")
    if not isinstance(raw_tags, list):
        return []
    tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in raw_tags:
        tag = clean_text(raw_tag)
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def _projection_markers(*, status: object = "", source_refs: list[SourceRef]) -> dict[str, object]:
    """Return prompt-facing support markers without changing durable state."""

    status_text = clean_text(status).lower()
    support_status = "source_backed" if source_refs else "source_ref_missing"
    if status_text in _LINEAGE_ONLY_STATUSES:
        return {
            "projection_role": "lineage_only",
            "support_status": support_status,
            "current_support": False,
            "lineage_only": True,
            "projection_warning": "lineage_only_not_current_support",
        }
    return {
        "projection_role": "current_support",
        "support_status": support_status,
        "current_support": True,
        "lineage_only": False,
        "projection_warning": "" if source_refs else "source_ref_missing",
    }


def _with_projection_markers(record: dict[str, object], *, status: object = "") -> dict[str, object]:
    """Copy one memory projection record and add compact support markers."""

    source_refs = _source_refs(record.get("source_refs"))
    marked = dict(record)
    marked.update(_projection_markers(status=status, source_refs=source_refs))
    return marked


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


def _is_open_active_attention_item(item: dict[str, object]) -> bool:
    """Return whether an active-attention item is still an open reading question."""

    return clean_text(item.get("status")).lower() in _OPEN_ACTIVE_ATTENTION_STATUSES


def _has_live_question_fields(item: dict[str, object]) -> bool:
    """Return whether an item uses the ActiveTension schema rather than sidecars only."""

    return any(
        clean_text(item.get(key))
        for key in (
            "tension_from",
            "tension_focus",
            "working_interpretation",
        )
    )


def _active_tension_prompt_items(active_attention_digest: ActiveAttentionDigest) -> list[dict[str, object]]:
    """Project all open ActiveTension items into the narrow Digest prompt shape."""

    prompt_items: list[dict[str, object]] = []
    for item in active_attention_digest.get("active_items", []):
        if not isinstance(item, dict):
            continue
        item_id = clean_text(item.get("item_id"))
        if not item_id or not _is_open_active_attention_item(item) or not _has_live_question_fields(item):
            continue
        prompt_items.append(
            {
                "item_id": item_id,
                "tension_from": clean_text(item.get("tension_from")),
                "tension_focus": clean_text(item.get("tension_focus")),
                "working_interpretation": clean_text(item.get("working_interpretation")),
            }
        )
    return prompt_items


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
                "kind": clean_text(entry.get("kind")) or "other",
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


def _reflective_status_by_item_id(reflective_frames: ReflectiveFramesState) -> dict[str, str]:
    """Return reflective item status by item id across all frame buckets."""

    statuses: dict[str, str] = {}
    for bucket in (
        "chapter_understandings",
        "book_level_frames",
        "durable_definitions",
        "stabilized_motifs",
        "resolved_questions_of_record",
        "chapter_end_notes",
    ):
        for item in reflective_frames.get(bucket, []):
            if not isinstance(item, dict):
                continue
            item_id = clean_text(item.get("item_id"))
            if item_id:
                statuses[item_id] = clean_text(item.get("status"))
    return statuses


def _build_active_attention_digest(
    active_attention: ActiveAttention,
    *,
    refs: list[CarryForwardRef],
) -> ActiveAttentionDigest:
    """Build the prompt-facing digest of the current hot active-attention state."""

    active_items = _active_attention_items(normalize_active_tension_state(active_attention))
    hot_items: list[dict[str, object]] = []
    digest_active_items: list[dict[str, object]] = []
    for item in active_items:
        item_id = clean_text(item.get("item_id"))
        if not item_id:
            continue
        ref_id = f"active_attention:{item_id}"
        record = {
            "ref_id": ref_id,
            "item_id": item_id,
            "attention_tags": _item_tags(item),
            "tension_from": clean_text(item.get("tension_from")),
            "tension_focus": clean_text(item.get("tension_focus")),
            "working_interpretation": clean_text(item.get("working_interpretation")),
            "answered_reason": clean_text(item.get("answered_reason")),
            "closed_reason": clean_text(item.get("closed_reason")),
            "status": clean_text(item.get("status")),
            "source_refs": _source_refs(item.get("source_refs"))[:3],
            "development_source_refs": _source_refs(item.get("development_source_refs"))[:3],
            "opened_at_source_span_id": clean_text(item.get("opened_at_source_span_id")),
            "opened_at_source_span": dict(item.get("opened_at_source_span"))
            if isinstance(item.get("opened_at_source_span"), dict)
            else {},
            "opened_at_unit_span_id": clean_text(item.get("opened_at_unit_span_id")),
            "opened_at_unit_span": dict(item.get("opened_at_unit_span"))
            if isinstance(item.get("opened_at_unit_span"), dict)
            else {},
            "answered_at_source_span_id": clean_text(item.get("answered_at_source_span_id")),
            "answered_at_source_span": dict(item.get("answered_at_source_span"))
            if isinstance(item.get("answered_at_source_span"), dict)
            else {},
            "answered_at_unit_span_id": clean_text(item.get("answered_at_unit_span_id")),
            "answered_at_unit_span": dict(item.get("answered_at_unit_span"))
            if isinstance(item.get("answered_at_unit_span"), dict)
            else {},
            "closed_at_source_span_id": clean_text(item.get("closed_at_source_span_id")),
            "closed_at_source_span": dict(item.get("closed_at_source_span"))
            if isinstance(item.get("closed_at_source_span"), dict)
            else {},
            "closed_at_unit_span_id": clean_text(item.get("closed_at_unit_span_id")),
            "closed_at_unit_span": dict(item.get("closed_at_unit_span"))
            if isinstance(item.get("closed_at_unit_span"), dict)
            else {},
        }
        digest_active_items.append(record)
        if _is_open_active_attention_item(record) and len(hot_items) < 4:
            hot_items.append(record)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "active_attention",
                "item_id": item_id,
                "summary": clean_text(item.get("tension_focus"))
                or clean_text(item.get("working_interpretation"))
                or clean_text(item.get("tension_from"))
                or ", ".join(_item_tags(item)),
                "source_span_id": clean_text((_source_refs(item.get("source_refs")) or [{}])[0].get("source_span_id")),
                "source_ref": (_source_refs(item.get("source_refs")) or [{}])[0],
            },
        )
    return {
        "active_items": digest_active_items,
        "hot_items": hot_items,
    }


def _mark_active_attention_digest(active_attention_digest: ActiveAttentionDigest) -> ActiveAttentionDigest:
    """Add prompt-facing support markers to active-attention digest copies."""

    active_items = [
        _with_projection_markers(item, status=item.get("status"))
        for item in active_attention_digest.get("active_items", [])
        if isinstance(item, dict)
    ]
    active_by_ref_id = {
        clean_text(item.get("ref_id")): item
        for item in active_items
        if clean_text(item.get("ref_id"))
    }
    hot_items: list[dict[str, object]] = []
    for item in active_attention_digest.get("hot_items", []):
        if not isinstance(item, dict):
            continue
        ref_id = clean_text(item.get("ref_id"))
        hot_items.append(
            dict(active_by_ref_id.get(ref_id, _with_projection_markers(item, status=item.get("status"))))
        )
    return {
        "active_items": active_items,
        "hot_items": hot_items,
    }


def _build_reflective_frame_digest(
    reflective_frames: ReflectiveFramesState,
    *,
    chapter_ref: str,
    refs: list[CarryForwardRef],
) -> ReflectiveFrameDigest:
    """Build the bounded reflective-frame packet for the current chapter/book."""

    chapter_frames: list[dict[str, object]] = []
    book_frames: list[dict[str, object]] = []
    durable_definitions: list[dict[str, object]] = []
    for bucket, limit, target in (
        ("chapter_understandings", 2, chapter_frames),
        ("book_level_frames", 1, book_frames),
        ("durable_definitions", 1, durable_definitions),
    ):
        selected = matching_chapter_items(
            [item for item in reflective_frames.get(bucket, []) if isinstance(item, dict)],
            chapter_ref=chapter_ref,
            limit=limit,
        )
        for item in selected:
            item_id = clean_text(item.get("item_id"))
            if not item_id:
                continue
            ref_id = f"reflective:{item_id}"
            record = {
                "ref_id": ref_id,
                "item_id": item_id,
                "bucket": bucket,
                "statement": clean_text(item.get("statement")),
                "chapter_ref": clean_text(item.get("chapter_ref")),
                "confidence_band": clean_text(item.get("confidence_band")),
                "source_refs": _source_refs(item.get("source_refs"))[:3],
            }
            target.append(record)
            _append_ref(
                refs,
                {
                    "ref_id": ref_id,
                    "kind": "reflective",
                    "item_id": item_id,
                    "summary": clean_text(item.get("statement")),
                },
            )
    return {
        "chapter_frames": chapter_frames,
        "book_frames": book_frames,
        "durable_definitions": durable_definitions,
    }


def _mark_reflective_frame_digest(
    reflective_frame: ReflectiveFrameDigest,
    *,
    status_by_item_id: dict[str, str],
) -> ReflectiveFrameDigest:
    """Add prompt-facing support markers to reflective-frame digest copies."""

    marked: ReflectiveFrameDigest = {}
    for bucket in ("chapter_frames", "book_frames", "durable_definitions"):
        marked[bucket] = [
            _with_projection_markers(item, status=status_by_item_id.get(clean_text(item.get("item_id")), ""))
            for item in reflective_frame.get(bucket, [])
            if isinstance(item, dict)
        ]
    return marked


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


def _build_active_focus_digest(
    active_attention_digest: ActiveAttentionDigest,
    *,
    recent_reactions: list[dict[str, object]],
) -> ActiveFocusDigest:
    """Build a compact digest of currently active focus lines."""

    return {
        "active_items": [dict(item) for item in active_attention_digest.get("active_items", [])[:4]],
        "recent_reactions": [dict(item) for item in recent_reactions[:2]],
    }


def build_continuation_capsule(
    *,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    active_attention_digest: ActiveAttentionDigest,
    recent_reading_memory_digest: RecentReadingMemoryDigest,
    chapter_reflective_frame: ReflectiveFrameDigest,
    active_focus_digest: ActiveFocusDigest,
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
        "active_attention_digest": dict(active_attention_digest),
        "recent_reading_memory": dict(recent_reading_memory_digest),
        "chapter_reflective_frame": dict(chapter_reflective_frame),
        "active_focus_digest": dict(active_focus_digest),
        "refs": [dict(ref) for ref in refs if isinstance(ref, dict)],
    }


def build_carry_forward_context(
    *,
    chapter_ref: str,
    current_unit_sentence_ids: list[str],
    local_buffer: LocalBufferState,
    active_attention: ActiveAttention | None = None,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    reflective_frames: ReflectiveFramesState | None = None,
    anchor_memory: AnchorMemoryState | None = None,
    reflective_summaries: ReflectiveSummariesState | None = None,
    reaction_records: ReactionRecordsState,
    continuation_capsule: ContinuationCapsule | None = None,
) -> CarryForwardContext:
    """Build the bounded carry-forward context packet from current persisted state."""

    primary_active_attention = (
        dict(active_attention) if isinstance(active_attention, dict) else build_empty_active_attention()
    )
    primary_recent_reading_memory = (
        dict(recent_reading_memory)
        if isinstance(recent_reading_memory, dict)
        else build_empty_recent_reading_memory()
    )
    primary_reflective_frames = (
        dict(reflective_frames)
        if isinstance(reflective_frames, dict)
        else migrate_reflective_summaries_to_frames(reflective_summaries)
    )
    _ = anchor_memory
    excluded_sentence_ids = {clean_text(item) for item in current_unit_sentence_ids if clean_text(item)}
    refs: list[CarryForwardRef] = []
    active_attention_digest = _build_active_attention_digest(primary_active_attention, refs=refs)
    recent_reading_memory_digest = _build_recent_reading_memory_digest(primary_recent_reading_memory)
    chapter_reflective_frame = _build_reflective_frame_digest(primary_reflective_frames, chapter_ref=chapter_ref, refs=refs)
    recent_reactions = _build_recent_reactions(reaction_records, refs=refs)
    session_continuity_capsule = _build_session_continuity_capsule(
        local_buffer,
        excluded_sentence_ids=excluded_sentence_ids,
        recent_reactions=recent_reactions,
    )
    active_focus_digest = _build_active_focus_digest(
        active_attention_digest,
        recent_reactions=recent_reactions,
    )
    primary_continuation_capsule = (
        dict(continuation_capsule)
        if isinstance(continuation_capsule, dict) and continuation_capsule
        else build_continuation_capsule(
            chapter_ref=chapter_ref,
            local_buffer=local_buffer,
            active_attention_digest=active_attention_digest,
            recent_reading_memory_digest=recent_reading_memory_digest,
            chapter_reflective_frame=chapter_reflective_frame,
            active_focus_digest=active_focus_digest,
            session_continuity_capsule=session_continuity_capsule,
            refs=refs,
            mechanism_version=clean_text(primary_active_attention.get("mechanism_version")),
        )
    )
    marked_active_attention_digest = _mark_active_attention_digest(active_attention_digest)
    marked_chapter_reflective_frame = _mark_reflective_frame_digest(
        chapter_reflective_frame,
        status_by_item_id=_reflective_status_by_item_id(primary_reflective_frames),
    )
    marked_recent_reactions = [
        _with_visible_trace_markers(item)
        for item in recent_reactions
        if isinstance(item, dict)
    ]
    marked_session_continuity_capsule = _build_session_continuity_capsule(
        local_buffer,
        excluded_sentence_ids=excluded_sentence_ids,
        recent_reactions=marked_recent_reactions,
    )
    marked_active_focus_digest = _build_active_focus_digest(
        marked_active_attention_digest,
        recent_reactions=marked_recent_reactions,
    )
    reflective_digest = [
        *marked_chapter_reflective_frame.get("chapter_frames", []),
        *marked_chapter_reflective_frame.get("book_frames", []),
        *marked_chapter_reflective_frame.get("durable_definitions", []),
    ]
    source_ref_digest = [
        dict(ref.get("source_ref", {}))
        for ref in refs
        if isinstance(ref, dict) and isinstance(ref.get("source_ref"), dict)
    ][:8]
    return {
        "packet_version": STATE_PACKET_VERSION,
        "continuation_capsule": primary_continuation_capsule,
        "session_continuity_capsule": marked_session_continuity_capsule,
        "active_attention_digest": marked_active_attention_digest,
        "recent_reading_memory": recent_reading_memory_digest,
        "chapter_reflective_frame": marked_chapter_reflective_frame,
        "active_focus_digest": marked_active_focus_digest,
        "reflective_digest": reflective_digest,
        "source_ref_digest": source_ref_digest,
        "continuity_digest": marked_session_continuity_capsule,
        "refs": refs,
    }


def build_digest_prompt_packet(
    *,
    carry_forward_context: CarryForwardContext,
) -> dict[str, object]:
    """Project persisted state into the narrow Digest prompt view."""
    active_attention_digest = (
        dict(carry_forward_context.get("active_attention_digest", {}))
        if isinstance(carry_forward_context.get("active_attention_digest"), dict)
        else {}
    )
    active_tensions = _active_tension_prompt_items(active_attention_digest)
    active_tension_warning = (
        "open_active_tension_count_exceeds_soft_limit"
        if len(active_tensions) > _ACTIVE_TENSION_SOFT_LIMIT
        else ""
    )
    packet: dict[str, object] = {
        "packet_version": clean_text(carry_forward_context.get("packet_version")) or STATE_PACKET_VERSION,
        "local_continuity": dict(carry_forward_context.get("session_continuity_capsule", {}))
        if isinstance(carry_forward_context.get("session_continuity_capsule"), dict)
        else {},
        "active_attention": {
            "active_tensions": active_tensions,
            "open_tension_count": len(active_tensions),
            "projection_warning": active_tension_warning,
        },
        "recent_reading_memory": dict(carry_forward_context.get("recent_reading_memory", {}))
        if isinstance(carry_forward_context.get("recent_reading_memory"), dict)
        else {"active_entries": [], "active_entry_count": 0},
        "reflective_digest": dict(carry_forward_context.get("chapter_reflective_frame", {}))
        if isinstance(carry_forward_context.get("chapter_reflective_frame"), dict)
        else {},
    }

    return packet


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
