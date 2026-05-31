"""Internal state-ownership and packetization helpers for live prompt inputs."""

from __future__ import annotations

from .schemas import (
    ATTENTIONAL_V2_SCHEMA_VERSION,
    ActiveFocusDigest,
    AnchorMemoryState,
    CarryForwardContext,
    CarryForwardRef,
    ContinuationCapsule,
    ConceptRegistryState,
    ConceptDigestItem,
    LocalBufferState,
    NavigationContext,
    ReactionRecordsState,
    ReflectiveFrameDigest,
    ReflectiveFramesState,
    ReflectiveItem,
    ReflectiveSummariesState,
    RecentReadingMemoryDigest,
    RecentReadingMemoryState,
    RehydrationEntry,
    SourceRef,
    ThreadTraceState,
    ThreadDigestItem,
    ActiveAttention,
    ActiveAttentionDigest,
    build_empty_active_attention,
    build_empty_recent_reading_memory,
)
from .source_spans import dedupe_source_refs
from .state_migration import migrate_reflective_summaries_to_frames, normalize_active_tension_state


STATE_PACKET_VERSION = "attentional_v2.state_packet.v1"
_CONCEPT_DIGEST_LIMIT = 3
_THREAD_DIGEST_LIMIT = 3
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
    """Project all open ActiveTension items into the narrow Read-node prompt shape."""

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
            "linked_concept_keys": list(item.get("linked_concept_keys", []))
            if isinstance(item.get("linked_concept_keys"), list)
            else [],
            "linked_thread_keys": list(item.get("linked_thread_keys", []))
            if isinstance(item.get("linked_thread_keys"), list)
            else [],
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


def _build_concept_digest(
    concept_registry: ConceptRegistryState,
    *,
    refs: list[CarryForwardRef],
) -> list[ConceptDigestItem]:
    """Build a small concept digest from the new concept registry."""

    entries = [
        dict(entry)
        for entry in concept_registry.get("entries", [])
        if isinstance(entry, dict) and clean_text(entry.get("concept_key"))
    ]
    entries.sort(
        key=lambda entry: (
            -len(_source_refs(entry.get("source_refs"))),
            clean_text(entry.get("status")) != "open",
            clean_text(entry.get("concept_key")),
        )
    )
    digest: list[ConceptDigestItem] = []
    for entry in entries[:_CONCEPT_DIGEST_LIMIT]:
        concept_key = clean_text(entry.get("concept_key"))
        source_refs = _source_refs(entry.get("source_refs"))
        ref_id = f"concept:{concept_key}"
        item: ConceptDigestItem = {
            "ref_id": ref_id,
            "concept_key": concept_key,
            "concept_type": clean_text(entry.get("concept_type")),
            "source_refs": source_refs[:4],
            "sample_quotes": _sample_quotes(source_refs),
            "rationale": clean_text(entry.get("summary")),
        }
        digest.append(item)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "concept",
                "item_id": concept_key,
                "summary": clean_text(entry.get("summary")) or clean_text(entry.get("concept_type")),
                "source_span_id": clean_text((source_refs or [{}])[0].get("source_span_id")),
                "source_ref": (source_refs or [{}])[0],
            },
        )
    return digest


def _mark_concept_digest(
    concept_digest: list[ConceptDigestItem],
    *,
    status_by_concept_key: dict[str, str],
) -> list[dict[str, object]]:
    """Add prompt-facing support markers to concept digest copies."""

    return [
        _with_projection_markers(item, status=status_by_concept_key.get(clean_text(item.get("concept_key")), ""))
        for item in concept_digest
        if isinstance(item, dict)
    ]


def _build_thread_digest(
    thread_trace: ThreadTraceState,
    *,
    refs: list[CarryForwardRef],
) -> list[ThreadDigestItem]:
    """Build a small thread digest from the new thread trace."""

    candidates: list[tuple[int, str, ThreadDigestItem]] = []

    for entry in thread_trace.get("entries", []):
        if not isinstance(entry, dict):
            continue
        thread_key = clean_text(entry.get("thread_key"))
        source_refs = _source_refs(entry.get("source_refs"))
        if not thread_key or not source_refs:
            continue
        recency = len(source_refs)
        item: ThreadDigestItem = {
            "ref_id": f"thread:{thread_key}",
            "thread_key": thread_key,
            "thread_type": clean_text(entry.get("thread_type")),
            "source_refs": source_refs[:4],
            "sample_quotes": _sample_quotes(source_refs, limit=3),
            "rationale": clean_text(entry.get("summary")),
        }
        candidates.append((recency, thread_key, item))

    candidates.sort(key=lambda item: (-item[0], item[1]))

    digest: list[ThreadDigestItem] = []
    seen_ref_ids: set[str] = set()
    for _recency, _sort_key, item in candidates:
        ref_id = clean_text(item.get("ref_id"))
        if not ref_id or ref_id in seen_ref_ids:
            continue
        seen_ref_ids.add(ref_id)
        digest.append(item)
        item_source_refs = _source_refs(item.get("source_refs"))
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "thread",
                "item_id": clean_text(item.get("thread_key")),
                "summary": clean_text(item.get("rationale")),
                "source_span_id": clean_text((item_source_refs or [{}])[0].get("source_span_id")),
                "source_ref": (item_source_refs or [{}])[0],
            },
        )
        if len(digest) >= _THREAD_DIGEST_LIMIT:
            break
    return digest


def _mark_thread_digest(
    thread_digest: list[ThreadDigestItem],
    *,
    status_by_thread_key: dict[str, str],
) -> list[dict[str, object]]:
    """Add prompt-facing support markers to thread digest copies."""

    return [
        _with_projection_markers(item, status=status_by_thread_key.get(clean_text(item.get("thread_key")), ""))
        for item in thread_digest
        if isinstance(item, dict)
    ]


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


def _build_rehydration_entrypoints(
    *,
    concept_digest: list[ConceptDigestItem],
    thread_digest: list[ThreadDigestItem],
) -> list[RehydrationEntry]:
    """Build bounded rehydration entrypoints from current continuity-bearing digests."""

    entrypoints: list[RehydrationEntry] = []

    for concept in concept_digest[:2]:
        if not isinstance(concept, dict):
            continue
        concept_key = clean_text(concept.get("concept_key"))
        if not concept_key:
            continue
        source_refs = _source_refs(concept.get("source_refs"))
        entrypoints.append(
            {
                "entry_id": f"concept:{concept_key}",
                "concept_key": concept_key,
                "source_span_id": clean_text((source_refs or [{}])[0].get("source_span_id")),
                "source_ref": (source_refs or [{}])[0],
                "why_rehydrate": clean_text(concept.get("rationale")) or concept_key,
            }
        )

    for thread in thread_digest[:2]:
        if not isinstance(thread, dict):
            continue
        thread_key = clean_text(thread.get("thread_key"))
        if not thread_key:
            continue
        source_refs = _source_refs(thread.get("source_refs"))
        entrypoints.append(
            {
                "entry_id": f"thread:{thread_key}",
                "thread_key": thread_key,
                "source_span_id": clean_text((source_refs or [{}])[0].get("source_span_id")),
                "source_ref": (source_refs or [{}])[0],
                "why_rehydrate": clean_text(thread.get("rationale")) or thread_key,
            }
        )

    return entrypoints[:6]


def build_continuation_capsule(
    *,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    active_attention_digest: ActiveAttentionDigest,
    recent_reading_memory_digest: RecentReadingMemoryDigest,
    chapter_reflective_frame: ReflectiveFrameDigest,
    active_focus_digest: ActiveFocusDigest,
    concept_digest: list[ConceptDigestItem],
    thread_digest: list[ThreadDigestItem],
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
        "concept_digest": [dict(item) for item in concept_digest if isinstance(item, dict)],
        "thread_digest": [dict(item) for item in thread_digest if isinstance(item, dict)],
        "refs": [dict(ref) for ref in refs if isinstance(ref, dict)],
        "rehydration_entrypoints": _build_rehydration_entrypoints(
            concept_digest=concept_digest,
            thread_digest=thread_digest,
        ),
    }


def build_carry_forward_context(
    *,
    chapter_ref: str,
    current_unit_sentence_ids: list[str],
    local_buffer: LocalBufferState,
    active_attention: ActiveAttention | None = None,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    concept_registry: ConceptRegistryState | None = None,
    thread_trace: ThreadTraceState | None = None,
    reflective_frames: ReflectiveFramesState | None = None,
    anchor_memory: AnchorMemoryState | None = None,
    reflective_summaries: ReflectiveSummariesState | None = None,
    reaction_records: ReactionRecordsState,
    continuation_capsule: ContinuationCapsule | None = None,
) -> CarryForwardContext:
    """Build the bounded read-context packet from current persisted state."""

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
    primary_concept_registry = dict(concept_registry) if isinstance(concept_registry, dict) else {"entries": []}
    primary_thread_trace = dict(thread_trace) if isinstance(thread_trace, dict) else {"entries": []}
    excluded_sentence_ids = {clean_text(item) for item in current_unit_sentence_ids if clean_text(item)}
    refs: list[CarryForwardRef] = []
    active_attention_digest = _build_active_attention_digest(primary_active_attention, refs=refs)
    recent_reading_memory_digest = _build_recent_reading_memory_digest(primary_recent_reading_memory)
    chapter_reflective_frame = _build_reflective_frame_digest(primary_reflective_frames, chapter_ref=chapter_ref, refs=refs)
    concept_digest = _build_concept_digest(primary_concept_registry, refs=refs)
    thread_digest = _build_thread_digest(primary_thread_trace, refs=refs)
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
            concept_digest=concept_digest,
            thread_digest=thread_digest,
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
    marked_concept_digest = _mark_concept_digest(
        concept_digest,
        status_by_concept_key=_status_by_key(primary_concept_registry.get("entries", []), "concept_key"),
    )
    marked_thread_digest = _mark_thread_digest(
        thread_digest,
        status_by_thread_key=_status_by_key(primary_thread_trace.get("entries", []), "thread_key"),
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
        "concept_digest": marked_concept_digest,
        "thread_digest": marked_thread_digest,
        "reflective_digest": reflective_digest,
        "source_ref_digest": source_ref_digest,
        "continuity_digest": marked_session_continuity_capsule,
        "refs": refs,
    }


def _clean_string_list(value: object) -> list[str]:
    """Return compact string items while preserving input order."""

    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = clean_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _retrieval_events_from_supplemental_context(
    supplemental_context: dict[str, object],
) -> list[dict[str, object]]:
    """Return compact supplemental retrieval events, if available."""

    events = [
        dict(item)
        for item in supplemental_context.get("retrieval_events", [])
        if isinstance(item, dict)
    ]
    if events:
        return events
    retrieval_intent = clean_text(supplemental_context.get("retrieval_intent"))
    result_boundary = clean_text(supplemental_context.get("result_boundary"))
    result_groups = _clean_string_list(supplemental_context.get("result_groups"))
    kind = clean_text(supplemental_context.get("kind"))
    if not any((retrieval_intent, result_boundary, result_groups)):
        return []
    return [
        {
            "kind": kind,
            "retrieval_intent": retrieval_intent,
            "result_boundary": result_boundary,
            "result_groups": result_groups,
        }
    ]


def _result_groups_from_events(events: list[dict[str, object]]) -> list[str]:
    """Return an order-preserving union of retrieval result groups."""

    groups: list[str] = []
    seen: set[str] = set()
    for event in events:
        for group in _clean_string_list(event.get("result_groups")):
            if group in seen:
                continue
            seen.add(group)
            groups.append(group)
    return groups


def _build_retrieval_context_contract(
    *,
    supplemental_context: dict[str, object],
    selective_carry: dict[str, object],
) -> dict[str, object]:
    """Expose compact prompt-facing retrieval contract metadata."""

    events = _retrieval_events_from_supplemental_context(supplemental_context)
    result_groups = _clean_string_list(supplemental_context.get("result_groups")) or _result_groups_from_events(events)
    retrieval_intent = clean_text(supplemental_context.get("retrieval_intent"))
    result_boundary = clean_text(supplemental_context.get("result_boundary"))
    if not any((events, result_groups, retrieval_intent, result_boundary)):
        return {}

    forwarded_groups: list[str] = []
    if selective_carry.get("source_ref_details"):
        forwarded_groups.append("source_refs")
    if selective_carry.get("earlier_excerpts"):
        forwarded_groups.append("excerpts")
    if selective_carry.get("supporting_refs"):
        forwarded_groups.append("refs")
    forwarded_set = set(forwarded_groups)
    not_forwarded_groups = [
        group
        for group in result_groups
        if group not in forwarded_set
    ]

    return {
        "retrieval_intent": retrieval_intent,
        "result_boundary": result_boundary,
        "result_groups": result_groups,
        "retrieval_events": events,
        "forwarded_result_groups": forwarded_groups,
        "not_forwarded_result_groups": not_forwarded_groups,
        "active_recall_full_objects_forwarded": False,
    }


def build_supplemental_selective_carry(
    supplemental_context: dict[str, object] | None,
) -> dict[str, object]:
    """Project supplemental context into the prompt-facing selective-carry shape."""

    selective_carry: dict[str, object] = {}
    if not isinstance(supplemental_context, dict):
        return selective_carry
    if isinstance(supplemental_context.get("excerpts"), list):
        selective_carry["earlier_excerpts"] = [
            dict(item)
            for item in supplemental_context.get("excerpts", [])
            if isinstance(item, dict)
        ][:4]
    if isinstance(supplemental_context.get("source_refs"), list):
        selective_carry["source_ref_details"] = [
            dict(item)
            for item in supplemental_context.get("source_refs", [])
            if isinstance(item, dict)
        ][:4]
    if isinstance(supplemental_context.get("refs"), list):
        selective_carry["supporting_refs"] = [
            dict(item)
            for item in supplemental_context.get("refs", [])
            if isinstance(item, dict)
        ][:6]
    retrieval_context = _build_retrieval_context_contract(
        supplemental_context=supplemental_context,
        selective_carry=selective_carry,
    )
    if retrieval_context:
        selective_carry["retrieval_context"] = retrieval_context
    return selective_carry


def build_read_prompt_packet(
    *,
    carry_forward_context: CarryForwardContext,
    supplemental_context: dict[str, object] | None = None,
    detour_context: dict[str, object] | None = None,
) -> dict[str, object]:
    """Project the persisted state packet into the narrow read-node prompt view."""

    del detour_context
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
        "concept_digest": [
            dict(item)
            for item in carry_forward_context.get("concept_digest", [])
            if isinstance(item, dict)
        ][:3],
        "thread_digest": [
            dict(item)
            for item in carry_forward_context.get("thread_digest", [])
            if isinstance(item, dict)
        ][:3],
        "reflective_digest": dict(carry_forward_context.get("chapter_reflective_frame", {}))
        if isinstance(carry_forward_context.get("chapter_reflective_frame"), dict)
        else {},
    }

    selective_carry = build_supplemental_selective_carry(supplemental_context)
    if selective_carry:
        packet["selective_carry"] = selective_carry
    return packet


def build_navigation_context(
    *,
    chapter_ref: str,
    current_sentence_id: str,
    local_buffer: LocalBufferState,
    active_attention: ActiveAttention | None = None,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    concept_registry: ConceptRegistryState | None = None,
    thread_trace: ThreadTraceState | None = None,
    reflective_frames: ReflectiveFramesState | None = None,
    anchor_memory: AnchorMemoryState | None = None,
    reflective_summaries: ReflectiveSummariesState | None = None,
    reaction_records: ReactionRecordsState,
    continuation_capsule: ContinuationCapsule | None = None,
) -> NavigationContext:
    """Build the bounded navigation packet used by Navigate.unitize."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[current_sentence_id] if current_sentence_id else [],
        local_buffer=local_buffer,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        anchor_memory=anchor_memory,
        reflective_summaries=reflective_summaries,
        reaction_records=reaction_records,
        continuation_capsule=continuation_capsule,
    )
    return {
        "packet_version": STATE_PACKET_VERSION,
        "continuation_capsule": dict(carry_forward_context.get("continuation_capsule", {})),
        "session_continuity_capsule": dict(carry_forward_context.get("session_continuity_capsule", {})),
        "active_attention_digest": dict(carry_forward_context.get("active_attention_digest", {})),
        "recent_reading_memory": dict(carry_forward_context.get("recent_reading_memory", {})),
        "chapter_reflective_frame": dict(carry_forward_context.get("chapter_reflective_frame", {})),
        "active_focus_digest": dict(carry_forward_context.get("active_focus_digest", {})),
        "concept_digest": [dict(item) for item in carry_forward_context.get("concept_digest", []) if isinstance(item, dict)],
        "thread_digest": [dict(item) for item in carry_forward_context.get("thread_digest", []) if isinstance(item, dict)],
        "source_ref_digest": [dict(item) for item in carry_forward_context.get("source_ref_digest", []) if isinstance(item, dict)],
        "refs": [dict(ref) for ref in carry_forward_context.get("refs", []) if isinstance(ref, dict)],
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
