"""Internal state-ownership and packetization helpers for live prompt inputs."""

from __future__ import annotations

from .schemas import (
    ActiveFocusDigest,
    AnchorBankDigest,
    AnchorMemoryState,
    CarryForwardContext,
    CarryForwardRef,
    LocalBufferState,
    MoveHistoryState,
    NavigationContext,
    ReactionRecordsState,
    ReflectiveFrameDigest,
    ReflectiveItem,
    ReflectiveSummariesState,
    TriggerState,
    WorkingPressureState,
    WorkingStateDigest,
)


STATE_PACKET_VERSION = "attentional_v2.state_packet.v1"


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
