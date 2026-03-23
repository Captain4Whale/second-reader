"""Pure state-operation helpers for attentional_v2 runtime state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from .schemas import (
    AnchorMemoryState,
    AnchorRecord,
    AnchorRelation,
    GateState,
    KnowledgeActivation,
    KnowledgeActivationsState,
    LocalBufferSentence,
    LocalBufferState,
    MoveHistoryState,
    MoveRecord,
    PressureSnapshot,
    ReaderPolicy,
    ReconsolidationRecord,
    ReconsolidationRecordsState,
    ReflectiveItem,
    ReflectiveSummariesState,
    TriggerDecision,
    TriggerSignal,
    TriggerState,
    WorkingPressureItem,
    WorkingPressureState,
)


PressureBucket = Literal["local_hypotheses", "local_questions", "local_tensions", "local_motifs"]
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


def _upsert_by_id(items: list[dict[str, object]], item: dict[str, object], *, id_key: str) -> list[dict[str, object]]:
    """Replace an existing item by id or append it when absent."""

    item_id = str(item.get(id_key, "") or "")
    if not item_id:
        return [*items, item]

    replaced = False
    next_items: list[dict[str, object]] = []
    for existing in items:
        if str(existing.get(id_key, "") or "") == item_id:
            next_items.append(item)
            replaced = True
        else:
            next_items.append(existing)
    if not replaced:
        next_items.append(item)
    return next_items


def set_gate_state(state: WorkingPressureState, gate_state: GateState) -> WorkingPressureState:
    """Set the controller gate state."""

    next_state = _touch_state(state)
    next_state["gate_state"] = gate_state
    return next_state  # type: ignore[return-value]


def replace_pressure_bucket(
    state: WorkingPressureState,
    *,
    bucket: PressureBucket,
    items: list[WorkingPressureItem],
) -> WorkingPressureState:
    """Replace one local-pressure bucket."""

    next_state = _touch_state(state)
    next_state[bucket] = [dict(item) for item in items]
    return next_state  # type: ignore[return-value]


def set_pressure_snapshot(state: WorkingPressureState, snapshot: PressureSnapshot) -> WorkingPressureState:
    """Replace the derived pressure snapshot."""

    next_state = _touch_state(state)
    next_state["pressure_snapshot"] = dict(snapshot)
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
    next_state["last_meaning_unit_closed_at_sentence_id"] = str(state.get("current_sentence_id", "") or "")
    next_state["open_meaning_unit_sentence_ids"] = []
    return next_state  # type: ignore[return-value]


def set_trigger_result(
    state: TriggerState,
    *,
    sentence_id: str,
    output: TriggerDecision,
    gate_state: GateState,
    signals: list[TriggerSignal],
    cadence_counter: int,
    callback_anchor_ids: list[str] | None = None,
) -> TriggerState:
    """Replace the current trigger result."""

    next_state = _touch_state(state)
    next_state["current_sentence_id"] = sentence_id
    next_state["output"] = output
    next_state["gate_state"] = gate_state
    next_state["signals"] = [dict(signal) for signal in signals]
    next_state["cadence_counter"] = cadence_counter
    next_state["callback_anchor_ids"] = list(callback_anchor_ids or [])
    return next_state  # type: ignore[return-value]


def upsert_anchor_record(state: AnchorMemoryState, anchor: AnchorRecord) -> AnchorMemoryState:
    """Upsert one anchor record by anchor id."""

    next_state = _touch_state(state)
    anchors = [dict(item) for item in state.get("anchor_records", [])]
    next_state["anchor_records"] = _upsert_by_id(anchors, dict(anchor), id_key="anchor_id")
    return next_state  # type: ignore[return-value]


def append_anchor_relation(state: AnchorMemoryState, relation: AnchorRelation) -> AnchorMemoryState:
    """Append or replace one anchor relation by relation id."""

    next_state = _touch_state(state)
    relations = [dict(item) for item in state.get("anchor_relations", [])]
    next_state["anchor_relations"] = _upsert_by_id(relations, dict(relation), id_key="relation_id")
    return next_state  # type: ignore[return-value]


def upsert_reflective_item(
    state: ReflectiveSummariesState,
    *,
    bucket: ReflectiveBucket,
    item: ReflectiveItem,
) -> ReflectiveSummariesState:
    """Upsert one reflective summary item inside the selected bucket."""

    next_state = _touch_state(state)
    bucket_items = [dict(existing) for existing in state.get(bucket, [])]
    next_state[bucket] = _upsert_by_id(bucket_items, dict(item), id_key="item_id")
    return next_state  # type: ignore[return-value]


def upsert_knowledge_activation(
    state: KnowledgeActivationsState,
    activation: KnowledgeActivation,
) -> KnowledgeActivationsState:
    """Upsert one activation by activation id."""

    next_state = _touch_state(state)
    activations = [dict(item) for item in state.get("activations", [])]
    next_state["activations"] = _upsert_by_id(activations, dict(activation), id_key="activation_id")
    return next_state  # type: ignore[return-value]


def append_move(state: MoveHistoryState, move: MoveRecord) -> MoveHistoryState:
    """Append one controller move in source order."""

    next_state = _touch_state(state)
    next_state["moves"] = [*state.get("moves", []), dict(move)]
    return next_state  # type: ignore[return-value]


def append_reconsolidation_record(
    state: ReconsolidationRecordsState,
    record: ReconsolidationRecord,
) -> ReconsolidationRecordsState:
    """Append one reconsolidation record in occurrence order."""

    next_state = _touch_state(state)
    next_state["records"] = [*state.get("records", []), dict(record)]
    return next_state  # type: ignore[return-value]


def replace_policy_section(
    policy: ReaderPolicy,
    *,
    section: Literal["gate", "controller", "knowledge", "search", "bridge", "resume", "logging"],
    payload: dict[str, object],
) -> ReaderPolicy:
    """Replace one reader-policy section while preserving other policy data."""

    next_policy = _touch_state(policy)
    next_policy[section] = dict(payload)
    return next_policy  # type: ignore[return-value]
