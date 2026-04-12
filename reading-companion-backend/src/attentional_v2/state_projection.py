"""Internal state-ownership and packetization helpers for live prompt inputs."""

from __future__ import annotations

from .schemas import (
    ActiveFocusDigest,
    AnchorBankDigest,
    AnchorMemoryState,
    CarryForwardContext,
    CarryForwardRef,
    ConceptDigestItem,
    LocalBufferState,
    MoveHistoryState,
    NavigationContext,
    ReactionRecordsState,
    ReflectiveFrameDigest,
    ReflectiveItem,
    ReflectiveSummariesState,
    ThreadDigestItem,
    TriggerState,
    WorkingPressureState,
    WorkingStateDigest,
)


STATE_PACKET_VERSION = "attentional_v2.state_packet.v1"
_CONCEPT_DIGEST_LIMIT = 3
_THREAD_DIGEST_LIMIT = 3
_DIGEST_QUOTE_LIMIT = 2


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


def _anchor_inventory(anchor_memory: AnchorMemoryState) -> tuple[dict[str, dict[str, object]], dict[str, int]]:
    """Return an anchor lookup plus a simple recency index."""

    anchor_lookup: dict[str, dict[str, object]] = {}
    anchor_order: dict[str, int] = {}
    for index, anchor in enumerate(anchor_memory.get("anchor_records", [])):
        if not isinstance(anchor, dict):
            continue
        anchor_id = clean_text(anchor.get("anchor_id"))
        if not anchor_id:
            continue
        anchor_lookup[anchor_id] = dict(anchor)
        anchor_order[anchor_id] = index
    return anchor_lookup, anchor_order


def _anchor_recency(anchor_id: str, anchor_order: dict[str, int]) -> int:
    """Return one comparable recency score for an anchor id."""

    return int(anchor_order.get(clean_text(anchor_id), -1))


def _sort_anchor_ids(anchor_ids: list[str], anchor_order: dict[str, int]) -> list[str]:
    """Sort anchor ids by recency while keeping deterministic tie-breaks."""

    return sorted(
        _dedupe_ids(anchor_ids),
        key=lambda anchor_id: (-_anchor_recency(anchor_id, anchor_order), anchor_id),
    )


def _sample_quotes(
    anchor_ids: list[str],
    *,
    anchor_lookup: dict[str, dict[str, object]],
    limit: int = _DIGEST_QUOTE_LIMIT,
) -> list[str]:
    """Collect a small quote sample for one digest entry."""

    quotes: list[str] = []
    for anchor_id in anchor_ids:
        quote = clean_text(anchor_lookup.get(anchor_id, {}).get("quote"))
        if quote and quote not in quotes:
            quotes.append(quote)
        if len(quotes) >= limit:
            break
    return quotes


def _build_working_state_digest(
    working_pressure: WorkingPressureState,
    *,
    refs: list[CarryForwardRef],
) -> WorkingStateDigest:
    """Build the prompt-facing digest of the current hot working state."""

    hot_items: list[dict[str, object]] = []
    bucket_records: dict[str, list[dict[str, object]]] = {
        "local_questions": [],
        "local_tensions": [],
        "local_hypotheses": [],
        "local_motifs": [],
    }
    for bucket in ("local_questions", "local_tensions", "local_hypotheses", "local_motifs"):
        for item in working_pressure.get(bucket, []):
            if not isinstance(item, dict):
                continue
            item_id = clean_text(item.get("item_id"))
            if not item_id:
                continue
            ref_id = f"pressure:{item_id}"
            record = {
                "ref_id": ref_id,
                "item_id": item_id,
                "bucket": bucket,
                "kind": clean_text(item.get("kind")),
                "statement": clean_text(item.get("statement")),
                "status": clean_text(item.get("status")),
                "support_anchor_ids": list(item.get("support_anchor_ids", []))
                if isinstance(item.get("support_anchor_ids"), list)
                else [],
            }
            bucket_records[bucket].append(record)
            if len(hot_items) < 4:
                hot_items.append(record)
            _append_ref(
                refs,
                {
                    "ref_id": ref_id,
                    "kind": "working_pressure",
                    "item_id": item_id,
                    "summary": clean_text(item.get("statement")) or clean_text(item.get("kind")),
                },
            )
            if len(bucket_records[bucket]) >= 3:
                break
    return {
        "gate_state": clean_text(working_pressure.get("gate_state")),
        "pressure_snapshot": dict(working_pressure.get("pressure_snapshot", {}))
        if isinstance(working_pressure.get("pressure_snapshot"), dict)
        else {},
        "hot_items": hot_items,
        "open_questions": bucket_records["local_questions"],
        "live_tensions": bucket_records["local_tensions"],
        "live_hypotheses": bucket_records["local_hypotheses"],
        "live_motifs": bucket_records["local_motifs"],
    }


def _build_reflective_frame_digest(
    reflective_summaries: ReflectiveSummariesState,
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
            [item for item in reflective_summaries.get(bucket, []) if isinstance(item, dict)],
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
                "support_anchor_ids": list(item.get("support_anchor_ids", []))
                if isinstance(item.get("support_anchor_ids"), list)
                else [],
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


def _build_anchor_bank_digest(
    anchor_memory: AnchorMemoryState,
    *,
    refs: list[CarryForwardRef],
) -> AnchorBankDigest:
    """Build the bounded anchor-bank packet from persisted anchor memory."""

    active_anchors: list[dict[str, object]] = []
    for anchor in list(anchor_memory.get("anchor_records", []))[-4:]:
        if not isinstance(anchor, dict):
            continue
        anchor_id = clean_text(anchor.get("anchor_id"))
        if not anchor_id:
            continue
        ref_id = f"anchor:{anchor_id}"
        record = {
            "ref_id": ref_id,
            "anchor_id": anchor_id,
            "quote": clean_text(anchor.get("quote")),
            "anchor_kind": clean_text(anchor.get("anchor_kind")),
            "status": clean_text(anchor.get("status")),
            "sentence_start_id": clean_text(anchor.get("sentence_start_id")),
            "sentence_end_id": clean_text(anchor.get("sentence_end_id")),
            "why_it_mattered": clean_text(anchor.get("why_it_mattered")),
        }
        active_anchors.append(record)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "anchor",
                "item_id": anchor_id,
                "summary": clean_text(anchor.get("quote")) or clean_text(anchor.get("why_it_mattered")),
                "anchor_id": anchor_id,
                "sentence_id": clean_text(anchor.get("sentence_end_id") or anchor.get("sentence_start_id")),
            },
        )
    return {"active_anchors": active_anchors}


def _build_concept_digest(
    anchor_memory: AnchorMemoryState,
    *,
    refs: list[CarryForwardRef],
) -> list[ConceptDigestItem]:
    """Build a small concept digest from current motif and unresolved-reference indexes."""

    anchor_lookup, anchor_order = _anchor_inventory(anchor_memory)
    motif_index = {
        clean_text(key).lower(): _sort_anchor_ids(list(value), anchor_order)
        for key, value in anchor_memory.get("motif_index", {}).items()
        if clean_text(key)
    }
    unresolved_index = {
        clean_text(key).lower(): _sort_anchor_ids(list(value), anchor_order)
        for key, value in anchor_memory.get("unresolved_reference_index", {}).items()
        if clean_text(key)
    }
    keys = sorted(
        {key for key in [*motif_index.keys(), *unresolved_index.keys()] if key},
        key=lambda key: (
            -(2 if key in motif_index and key in unresolved_index else 1 if key in motif_index else 0),
            -max(
                [_anchor_recency(anchor_id, anchor_order) for anchor_id in [*motif_index.get(key, []), *unresolved_index.get(key, [])]]
                or [-1]
            ),
            key,
        ),
    )

    digest: list[ConceptDigestItem] = []
    for concept_key in keys[:_CONCEPT_DIGEST_LIMIT]:
        linked_anchor_ids = _sort_anchor_ids(
            [*motif_index.get(concept_key, []), *unresolved_index.get(concept_key, [])],
            anchor_order,
        )
        if not linked_anchor_ids:
            continue
        in_motif = concept_key in motif_index
        in_unresolved = concept_key in unresolved_index
        if in_motif and in_unresolved:
            concept_type = "motif_and_unresolved_reference"
            rationale = "This concept recurs in retained anchors and still carries unresolved pressure."
        elif in_unresolved:
            concept_type = "unresolved_reference"
            rationale = "This concept remains unresolved across retained anchors and may need renewed attention."
        else:
            concept_type = "motif"
            rationale = "This concept recurs across retained anchors and remains part of the active local field."
        ref_id = f"concept:{concept_key}"
        item: ConceptDigestItem = {
            "ref_id": ref_id,
            "concept_key": concept_key,
            "concept_type": concept_type,
            "linked_anchor_ids": linked_anchor_ids[:4],
            "sample_quotes": _sample_quotes(linked_anchor_ids, anchor_lookup=anchor_lookup),
            "rationale": rationale,
        }
        digest.append(item)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "concept",
                "item_id": concept_key,
                "summary": rationale,
                "anchor_id": linked_anchor_ids[0],
            },
        )
    return digest


def _build_thread_digest(
    anchor_memory: AnchorMemoryState,
    *,
    refs: list[CarryForwardRef],
) -> list[ThreadDigestItem]:
    """Build a small thread digest from current trace and unresolved-reference indexes."""

    anchor_lookup, anchor_order = _anchor_inventory(anchor_memory)
    candidates: list[tuple[int, str, ThreadDigestItem]] = []

    for source_anchor_id, target_anchor_ids in anchor_memory.get("trace_links", {}).items():
        clean_source = clean_text(source_anchor_id)
        linked_anchor_ids = _sort_anchor_ids(list(target_anchor_ids), anchor_order)
        if not clean_source or not linked_anchor_ids:
            continue
        recency = max([_anchor_recency(clean_source, anchor_order), *[_anchor_recency(anchor_id, anchor_order) for anchor_id in linked_anchor_ids]])
        item: ThreadDigestItem = {
            "ref_id": f"thread:trace:{clean_source}",
            "thread_key": f"trace:{clean_source}",
            "thread_type": "trace_link",
            "source_anchor_id": clean_source,
            "linked_anchor_ids": linked_anchor_ids[:4],
            "sample_quotes": _sample_quotes([clean_source, *linked_anchor_ids], anchor_lookup=anchor_lookup, limit=3),
            "rationale": "This thread already has retained trace links across earlier and later anchors.",
        }
        candidates.append((recency, clean_source, item))

    for unresolved_key, anchor_ids in anchor_memory.get("unresolved_reference_index", {}).items():
        clean_key = clean_text(unresolved_key).lower()
        linked_anchor_ids = _sort_anchor_ids(list(anchor_ids), anchor_order)
        if not clean_key or not linked_anchor_ids:
            continue
        source_anchor_id = linked_anchor_ids[0]
        recency = max([_anchor_recency(anchor_id, anchor_order) for anchor_id in linked_anchor_ids] or [-1])
        item = {
            "ref_id": f"thread:open:{clean_key}",
            "thread_key": clean_key,
            "thread_type": "open_reference",
            "source_anchor_id": source_anchor_id,
            "linked_anchor_ids": linked_anchor_ids[:4],
            "sample_quotes": _sample_quotes(linked_anchor_ids, anchor_lookup=anchor_lookup),
            "rationale": "This unresolved line is still open across retained anchors and may need explicit follow-through.",
        }
        candidates.append((recency, clean_key, item))

    candidates.sort(key=lambda item: (-item[0], item[1]))

    digest: list[ThreadDigestItem] = []
    seen_ref_ids: set[str] = set()
    for _recency, _sort_key, item in candidates:
        ref_id = clean_text(item.get("ref_id"))
        if not ref_id or ref_id in seen_ref_ids:
            continue
        seen_ref_ids.add(ref_id)
        digest.append(item)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "thread",
                "item_id": clean_text(item.get("thread_key")),
                "summary": clean_text(item.get("rationale")),
                "anchor_id": clean_text(item.get("source_anchor_id")),
            },
        )
        if len(digest) >= _THREAD_DIGEST_LIMIT:
            break
    return digest


def _build_recent_moves(
    move_history: MoveHistoryState,
    *,
    refs: list[CarryForwardRef],
) -> list[dict[str, object]]:
    """Build a bounded recent-moves digest."""

    recent_moves: list[dict[str, object]] = []
    for move in list(move_history.get("moves", []))[-3:]:
        if not isinstance(move, dict):
            continue
        move_id = clean_text(move.get("move_id"))
        if not move_id:
            continue
        ref_id = f"move:{move_id}"
        record = {
            "ref_id": ref_id,
            "move_id": move_id,
            "move_type": clean_text(move.get("move_type")),
            "reason": clean_text(move.get("reason")),
            "source_sentence_id": clean_text(move.get("source_sentence_id")),
            "target_anchor_id": clean_text(move.get("target_anchor_id")),
            "target_sentence_id": clean_text(move.get("target_sentence_id")),
        }
        recent_moves.append(record)
        _append_ref(
            refs,
            {
                "ref_id": ref_id,
                "kind": "move",
                "item_id": move_id,
                "summary": clean_text(move.get("reason")) or clean_text(move.get("move_type")),
                "move_id": move_id,
                "sentence_id": clean_text(move.get("source_sentence_id")),
                "anchor_id": clean_text(move.get("target_anchor_id")),
            },
        )
    return recent_moves


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
        primary_anchor = dict(record.get("primary_anchor", {})) if isinstance(record.get("primary_anchor"), dict) else {}
        ref_id = f"reaction:{reaction_id}"
        reaction_record = {
            "ref_id": ref_id,
            "reaction_id": reaction_id,
            "type": clean_text(record.get("type")),
            "thought": clean_text(record.get("thought")),
            "emitted_at_sentence_id": clean_text(record.get("emitted_at_sentence_id")),
            "primary_anchor_id": clean_text(primary_anchor.get("anchor_id")),
            "primary_anchor_quote": clean_text(primary_anchor.get("quote")),
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
                "sentence_id": clean_text(record.get("emitted_at_sentence_id")),
                "anchor_id": clean_text(primary_anchor.get("anchor_id")),
            },
        )
    return recent_reactions


def _build_session_continuity_capsule(
    local_buffer: LocalBufferState,
    *,
    excluded_sentence_ids: set[str],
    recent_moves: list[dict[str, object]],
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
        "recent_moves": recent_moves,
        "recent_reactions": recent_reactions,
    }


def _build_active_focus_digest(
    working_state_digest: WorkingStateDigest,
    *,
    recent_moves: list[dict[str, object]],
    recent_reactions: list[dict[str, object]],
) -> ActiveFocusDigest:
    """Build a compact digest of currently active focus lines."""

    return {
        "open_questions": [dict(item) for item in working_state_digest.get("open_questions", [])[:3]],
        "live_tensions": [dict(item) for item in working_state_digest.get("live_tensions", [])[:3]],
        "live_hypotheses": [dict(item) for item in working_state_digest.get("live_hypotheses", [])[:2]],
        "recent_moves": [dict(item) for item in recent_moves[:2]],
        "recent_reactions": [dict(item) for item in recent_reactions[:2]],
    }


def build_carry_forward_context(
    *,
    chapter_ref: str,
    current_unit_sentence_ids: list[str],
    local_buffer: LocalBufferState,
    working_pressure: WorkingPressureState,
    anchor_memory: AnchorMemoryState,
    reflective_summaries: ReflectiveSummariesState,
    move_history: MoveHistoryState,
    reaction_records: ReactionRecordsState,
) -> CarryForwardContext:
    """Build the bounded read-context packet from current persisted state."""

    excluded_sentence_ids = {clean_text(item) for item in current_unit_sentence_ids if clean_text(item)}
    refs: list[CarryForwardRef] = []
    working_state_digest = _build_working_state_digest(working_pressure, refs=refs)
    chapter_reflective_frame = _build_reflective_frame_digest(reflective_summaries, chapter_ref=chapter_ref, refs=refs)
    concept_digest = _build_concept_digest(anchor_memory, refs=refs)
    thread_digest = _build_thread_digest(anchor_memory, refs=refs)
    anchor_bank_digest = _build_anchor_bank_digest(anchor_memory, refs=refs)
    recent_moves = _build_recent_moves(move_history, refs=refs)
    recent_reactions = _build_recent_reactions(reaction_records, refs=refs)
    session_continuity_capsule = _build_session_continuity_capsule(
        local_buffer,
        excluded_sentence_ids=excluded_sentence_ids,
        recent_moves=recent_moves,
        recent_reactions=recent_reactions,
    )
    active_focus_digest = _build_active_focus_digest(
        working_state_digest,
        recent_moves=recent_moves,
        recent_reactions=recent_reactions,
    )
    reflective_digest = [
        *chapter_reflective_frame.get("chapter_frames", []),
        *chapter_reflective_frame.get("book_frames", []),
        *chapter_reflective_frame.get("durable_definitions", []),
    ]
    anchor_digest = list(anchor_bank_digest.get("active_anchors", []))
    return {
        "packet_version": STATE_PACKET_VERSION,
        "session_continuity_capsule": session_continuity_capsule,
        "working_state_digest": working_state_digest,
        "chapter_reflective_frame": chapter_reflective_frame,
        "active_focus_digest": active_focus_digest,
        "concept_digest": concept_digest,
        "thread_digest": thread_digest,
        "anchor_bank_digest": anchor_bank_digest,
        "working_pressure_digest": {
            "gate_state": working_state_digest.get("gate_state", ""),
            "pressure_snapshot": dict(working_state_digest.get("pressure_snapshot", {})),
            "items": list(working_state_digest.get("hot_items", [])),
        },
        "reflective_digest": reflective_digest,
        "anchor_digest": anchor_digest,
        "continuity_digest": session_continuity_capsule,
        "refs": refs,
    }


def build_navigation_context(
    *,
    chapter_ref: str,
    current_sentence_id: str,
    local_buffer: LocalBufferState,
    trigger_state: TriggerState,
    working_pressure: WorkingPressureState,
    anchor_memory: AnchorMemoryState,
    reflective_summaries: ReflectiveSummariesState,
    move_history: MoveHistoryState,
    reaction_records: ReactionRecordsState,
) -> NavigationContext:
    """Build the bounded navigation packet used by navigate.unitize."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[current_sentence_id] if current_sentence_id else [],
        local_buffer=local_buffer,
        working_pressure=working_pressure,
        anchor_memory=anchor_memory,
        reflective_summaries=reflective_summaries,
        move_history=move_history,
        reaction_records=reaction_records,
    )
    watch_state = {
        "current_sentence_id": clean_text(trigger_state.get("current_sentence_id")),
        "output": clean_text(trigger_state.get("output")),
        "gate_state": clean_text(trigger_state.get("gate_state")),
        "cadence_counter": int(trigger_state.get("cadence_counter", 0) or 0),
        "callback_anchor_ids": [
            clean_text(item)
            for item in trigger_state.get("callback_anchor_ids", [])
            if clean_text(item)
        ][:4]
        if isinstance(trigger_state.get("callback_anchor_ids"), list)
        else [],
        "signals": [
            {
                "signal_kind": clean_text(signal.get("signal_kind")),
                "family": clean_text(signal.get("family")),
                "sentence_id": clean_text(signal.get("sentence_id")),
                "evidence": clean_text(signal.get("evidence")),
                "strength": clean_text(signal.get("strength")),
            }
            for signal in trigger_state.get("signals", [])
            if isinstance(signal, dict)
        ][:4]
        if isinstance(trigger_state.get("signals"), list)
        else [],
    }
    return {
        "packet_version": STATE_PACKET_VERSION,
        "watch_state": watch_state,
        "session_continuity_capsule": dict(carry_forward_context.get("session_continuity_capsule", {})),
        "working_state_digest": dict(carry_forward_context.get("working_state_digest", {})),
        "chapter_reflective_frame": dict(carry_forward_context.get("chapter_reflective_frame", {})),
        "active_focus_digest": dict(carry_forward_context.get("active_focus_digest", {})),
        "concept_digest": [dict(item) for item in carry_forward_context.get("concept_digest", []) if isinstance(item, dict)],
        "thread_digest": [dict(item) for item in carry_forward_context.get("thread_digest", []) if isinstance(item, dict)],
        "anchor_bank_digest": dict(carry_forward_context.get("anchor_bank_digest", {})),
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
