"""Pure state-operation helpers for attentional_v2 runtime state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from .schemas import (
    AnchoredReactionRecord,
    AnchorBankState,
    AnchorMemoryState,
    AnchorRecord,
    AnchorRelation,
    KnowledgeActivation,
    KnowledgeActivationsState,
    LocalBufferSentence,
    LocalBufferState,
    ReactionRecordsState,
    ReaderPolicy,
    ReconsolidationRecord,
    ReconsolidationRecordsState,
    RecentReadingMemoryEntry,
    RecentReadingMemoryState,
    ReflectiveItem,
    ReflectiveFramesState,
    ReflectiveSummariesState,
    SourceRef,
    ActiveAttentionItem,
    ActiveAttention,
    StateOperation,
)
from .memory_tokens import token_estimate_payload
from .source_spans import dedupe_source_refs
from .state_migration import normalize_active_tension_state


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


def _remove_by_id(items: list[dict[str, object]], item_id: str, *, id_key: str) -> list[dict[str, object]]:
    """Return one list with the selected id removed."""

    selected = str(item_id or "")
    if not selected:
        return list(items)
    return [item for item in items if str(item.get(id_key, "") or "") != selected]


def _active_attention_items(state: ActiveAttention) -> list[ActiveAttentionItem]:
    """Return the normalized active-items view over active attention."""

    normalized_state = normalize_active_tension_state(state)
    active_items = [dict(item) for item in normalized_state.get("active_items", []) if isinstance(item, dict)]
    return active_items  # type: ignore[return-value]


def _with_active_items(
    state: ActiveAttention,
    *,
    active_items: list[ActiveAttentionItem],
) -> ActiveAttention:
    """Return one state copy with normalized active items."""

    next_state = dict(state)
    next_state["active_items"] = [dict(item) for item in active_items]
    return next_state  # type: ignore[return-value]


def _merge_unique_ids(*values: object) -> list[str]:
    """Return one stable de-duplicated list of linked ids."""

    ordered: list[str] = []
    seen: set[str] = set()
    for raw in values:
        if not isinstance(raw, list):
            continue
        for item in raw:
            clean = str(item or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            ordered.append(clean)
    return ordered


def _merge_source_refs(*values: object) -> list[SourceRef]:
    """Merge inline source refs while preserving stable order."""

    merged: list[dict[str, object]] = []
    for raw in values:
        if isinstance(raw, list):
            merged.extend(dict(item) for item in raw if isinstance(item, dict))
    return dedupe_source_refs(merged)


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


def _merge_text_field(existing: dict[str, object], payload: dict[str, object], key: str) -> str:
    """Return payload text when explicitly provided, otherwise preserve existing text."""

    if key in payload:
        return str(payload.get(key) or "").strip()
    return str(existing.get(key) or "").strip()


def _merge_dict_field(existing: dict[str, object], payload: dict[str, object], key: str) -> dict[str, object]:
    """Return payload dict when explicitly provided, otherwise preserve existing dict."""

    if isinstance(payload.get(key), dict):
        return dict(payload[key])  # type: ignore[index]
    if isinstance(existing.get(key), dict):
        return dict(existing[key])  # type: ignore[index]
    return {}


def _normalize_active_tension_payload(payload: dict[str, object]) -> dict[str, object]:
    """Map legacy read-output fields to the current ActiveTension payload shape."""

    normalized = dict(payload)
    if "tension_from" not in normalized and str(normalized.get("question_from") or "").strip():
        normalized["tension_from"] = normalized.get("question_from")
    if "tension_focus" not in normalized:
        for legacy_key in ("driving_question", "statement", "answer_boundary"):
            if str(normalized.get(legacy_key) or "").strip():
                normalized["tension_focus"] = normalized.get(legacy_key)
                break
    if "working_interpretation" not in normalized and "working_answer" in normalized:
        normalized["working_interpretation"] = normalized.get("working_answer")
    if "development_source_refs" not in normalized and "answer_source_refs" in normalized:
        normalized["development_source_refs"] = normalized.get("answer_source_refs")
    for legacy_key in (
        "question_from",
        "driving_question",
        "working_answer",
        "answer_source_refs",
        "statement",
        "answer_boundary",
    ):
        normalized.pop(legacy_key, None)
    return normalized


def _merge_active_item(
    existing: dict[str, object],
    payload: dict[str, object],
    *,
    item_id: str,
) -> ActiveAttentionItem:
    """Merge one active-item payload on top of an existing entry."""

    normalized_existing_items = normalize_active_tension_state({"active_items": [existing]}).get("active_items", [])
    existing = dict(normalized_existing_items[0]) if normalized_existing_items else {}
    payload = _normalize_active_tension_payload(payload)

    merged: ActiveAttentionItem = {
        "item_id": item_id,
        "attention_tags": _merge_unique_ids(existing.get("attention_tags"), payload.get("attention_tags")),
        "tension_from": _merge_text_field(existing, payload, "tension_from"),
        "tension_focus": _merge_text_field(existing, payload, "tension_focus"),
        "working_interpretation": _merge_text_field(existing, payload, "working_interpretation"),
        "answered_reason": _merge_text_field(existing, payload, "answered_reason"),
        "closed_reason": _merge_text_field(existing, payload, "closed_reason"),
        "source_refs": _merge_source_refs(existing.get("source_refs"), payload.get("source_refs")),
        "development_source_refs": _merge_source_refs(
            existing.get("development_source_refs"),
            payload.get("development_source_refs"),
        ),
        "opened_at_source_span_id": _merge_text_field(existing, payload, "opened_at_source_span_id"),
        "opened_at_source_span": _merge_dict_field(existing, payload, "opened_at_source_span"),
        "opened_at_unit_span_id": _merge_text_field(existing, payload, "opened_at_unit_span_id"),
        "opened_at_unit_span": _merge_dict_field(existing, payload, "opened_at_unit_span"),
        "answered_at_source_span_id": _merge_text_field(existing, payload, "answered_at_source_span_id"),
        "answered_at_source_span": _merge_dict_field(existing, payload, "answered_at_source_span"),
        "answered_at_unit_span_id": _merge_text_field(existing, payload, "answered_at_unit_span_id"),
        "answered_at_unit_span": _merge_dict_field(existing, payload, "answered_at_unit_span"),
        "closed_at_source_span_id": _merge_text_field(existing, payload, "closed_at_source_span_id"),
        "closed_at_source_span": _merge_dict_field(existing, payload, "closed_at_source_span"),
        "closed_at_unit_span_id": _merge_text_field(existing, payload, "closed_at_unit_span_id"),
        "closed_at_unit_span": _merge_dict_field(existing, payload, "closed_at_unit_span"),
        "status": str(payload.get("status", "") or existing.get("status", "") or "").strip(),
    }
    return merged


def _apply_active_attention_operations(
    state: ActiveAttention,
    operations: list[StateOperation],
    *,
    allowed_target_stores: set[str],
) -> ActiveAttention:
    """Apply explicit active-attention mutations from node outputs."""

    normalized_state = normalize_active_tension_state(state)
    next_state = dict(normalized_state)
    active_items = [dict(item) for item in _active_attention_items(normalized_state)]
    touched = False
    for operation in operations:
        if str(operation.get("target_store", "") or "") not in allowed_target_stores:
            continue
        payload = operation.get("payload")
        if not isinstance(payload, dict):
            continue
        item_id = str(operation.get("target_key", "") or operation.get("item_id", "") or payload.get("item_id", "") or "").strip()
        if not item_id:
            continue
        operation_type = str(operation.get("op", "") or operation.get("operation_type", "") or "").strip().lower().replace("-", "_")
        existing = next((dict(item) for item in active_items if str(item.get("item_id", "") or "").strip() == item_id), {})

        if operation_type in {"append", "create", "update", "reactivate", "cool"}:
            merged_item = _merge_active_item(existing, payload, item_id=item_id)
            if operation_type in {"append", "create"} and not merged_item.get("status"):
                merged_item["status"] = "open"
            if operation_type == "update" and not merged_item.get("status"):
                merged_item["status"] = "open"
            if operation_type == "reactivate" and not payload.get("status"):
                merged_item["status"] = "open"
            if operation_type == "cool" and not payload.get("status"):
                merged_item["status"] = "cooling"
            active_items = _upsert_by_id(active_items, merged_item, id_key="item_id")
            touched = True
            continue

        if operation_type in {"close", "resolve"}:
            if not existing:
                continue
            merged_item = _merge_active_item(existing, payload, item_id=item_id)
            if not payload.get("status"):
                merged_item["status"] = "answered" if operation_type == "resolve" else "closed"
            active_items = _upsert_by_id(active_items, merged_item, id_key="item_id")
            touched = True
            continue

        if operation_type in {"link", "link_anchors"}:
            if not existing and not payload:
                continue
            merged_item = _merge_active_item(existing, payload, item_id=item_id)
            active_items = _upsert_by_id(active_items, merged_item, id_key="item_id")
            touched = True
            continue

        if operation_type == "drop":
            active_items = _remove_by_id(active_items, item_id, id_key="item_id")
            touched = True

    if not touched:
        return state

    next_state["updated_at"] = _timestamp()
    return _with_active_items(next_state, active_items=active_items)


def apply_active_attention_operations(
    state: ActiveAttention,
    operations: list[StateOperation],
) -> ActiveAttention:
    """Apply explicit active-attention mutations from internal settlement operations."""

    return _apply_active_attention_operations(
        state,
        operations,
        allowed_target_stores={"active_attention"},
    )  # type: ignore[return-value]


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


def upsert_anchor_record(
    state: AnchorMemoryState | AnchorBankState,
    anchor: AnchorRecord,
) -> AnchorMemoryState | AnchorBankState:
    """Upsert one anchor record by anchor id."""

    next_state = _touch_state(state)
    anchors = [dict(item) for item in state.get("anchor_records", [])]
    next_state["anchor_records"] = _upsert_by_id(anchors, dict(anchor), id_key="anchor_id")
    return next_state  # type: ignore[return-value]


def append_anchor_relation(
    state: AnchorMemoryState | AnchorBankState,
    relation: AnchorRelation,
) -> AnchorMemoryState | AnchorBankState:
    """Append or replace one anchor relation by relation id."""

    next_state = _touch_state(state)
    relations = [dict(item) for item in state.get("anchor_relations", [])]
    next_state["anchor_relations"] = _upsert_by_id(relations, dict(relation), id_key="relation_id")
    return next_state  # type: ignore[return-value]


def _apply_anchor_bank_operations(
    state: AnchorMemoryState | AnchorBankState,
    operations: list[StateOperation],
    *,
    allowed_target_stores: set[str],
) -> AnchorMemoryState | AnchorBankState:
    """Apply explicit anchor-memory mutations from read/bridge outputs."""

    next_state = state
    for operation in operations:
        if str(operation.get("target_store", "") or "") not in allowed_target_stores:
            continue
        payload = operation.get("payload")
        if not isinstance(payload, dict):
            continue
        operation_type = str(operation.get("operation_type", "") or "")

        if operation_type in {"append", "create", "update", "retain_anchor"}:
            anchor_id = str(operation.get("item_id", "") or payload.get("anchor_id", "") or "")
            sentence_start_id = str(payload.get("sentence_start_id", "") or "")
            sentence_end_id = str(payload.get("sentence_end_id", "") or sentence_start_id or "")
            quote = str(payload.get("quote", "") or "")
            if not any((anchor_id, sentence_start_id, quote)):
                continue
            anchor: AnchorRecord = {
                "anchor_id": anchor_id or f"anchor:{sentence_start_id}:{sentence_end_id}",
                "sentence_start_id": sentence_start_id,
                "sentence_end_id": sentence_end_id,
                "quote": quote,
                "locator": dict(payload.get("locator", {})) if isinstance(payload.get("locator"), dict) else {},
                "anchor_kind": str(payload.get("anchor_kind", "") or "unit_evidence"),
                "why_it_mattered": str(payload.get("why_it_mattered", "") or str(operation.get("reason", "") or "")),
                "status": str(payload.get("status", "") or "active"),
                "linked_reaction_ids": list(payload.get("linked_reaction_ids", []))
                if isinstance(payload.get("linked_reaction_ids"), list)
                else [],
                "linked_activation_ids": list(payload.get("linked_activation_ids", []))
                if isinstance(payload.get("linked_activation_ids"), list)
                else [],
            }
            next_state = upsert_anchor_record(next_state, anchor)
            continue

        if operation_type in {"link", "link_anchors"}:
            relation_id = str(operation.get("item_id", "") or payload.get("relation_id", "") or "")
            source_anchor_id = str(payload.get("source_anchor_id", "") or "")
            target_anchor_id = str(payload.get("target_anchor_id", "") or "")
            if not source_anchor_id or not target_anchor_id:
                continue
            relation: AnchorRelation = {
                "relation_id": relation_id or f"relation:{source_anchor_id}:{target_anchor_id}",
                "relation_type": str(payload.get("relation_type", "") or "echo"),
                "source_anchor_id": source_anchor_id,
                "target_anchor_id": target_anchor_id,
                "rationale": str(payload.get("rationale", "") or str(operation.get("reason", "") or "")),
            }
            next_state = append_anchor_relation(next_state, relation)
            continue

        if operation_type in {"close", "resolve"}:
            anchor_id = str(operation.get("item_id", "") or payload.get("anchor_id", "") or "")
            if not anchor_id:
                continue
            existing_anchor = next(
                (
                    dict(anchor)
                    for anchor in next_state.get("anchor_records", [])
                    if isinstance(anchor, dict) and str(anchor.get("anchor_id", "") or "") == anchor_id
                ),
                None,
            )
            if existing_anchor is None:
                continue
            existing_anchor["status"] = str(payload.get("status", "") or ("resolved" if operation_type == "resolve" else "closed"))
            next_state = upsert_anchor_record(next_state, existing_anchor)

    return next_state


def apply_anchor_memory_operations(
    state: AnchorMemoryState,
    operations: list[StateOperation],
) -> AnchorMemoryState:
    """Apply explicit anchor-memory mutations from read/bridge outputs."""

    return _apply_anchor_bank_operations(
        state,
        operations,
        allowed_target_stores={"anchor_memory"},
    )  # type: ignore[return-value]


def apply_anchor_bank_operations(
    state: AnchorBankState,
    operations: list[StateOperation],
) -> AnchorBankState:
    """Apply explicit anchor-bank mutations from read outputs."""

    return _apply_anchor_bank_operations(
        state,
        operations,
        allowed_target_stores={"anchor_bank"},
    )  # type: ignore[return-value]


def upsert_reflective_item(
    state: ReflectiveSummariesState | ReflectiveFramesState,
    *,
    bucket: ReflectiveBucket,
    item: ReflectiveItem,
) -> ReflectiveSummariesState | ReflectiveFramesState:
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


def append_reaction_record(
    state: ReactionRecordsState,
    record: AnchoredReactionRecord,
) -> ReactionRecordsState:
    """Append one durable anchored reaction in occurrence order."""

    next_state = _touch_state(state)
    next_state["records"] = [*state.get("records", []), dict(record)]
    return next_state  # type: ignore[return-value]


def append_reconsolidation_record(
    state: ReconsolidationRecordsState,
    record: ReconsolidationRecord,
) -> ReconsolidationRecordsState:
    """Append one reconsolidation record in occurrence order."""

    next_state = _touch_state(state)
    next_state["records"] = [*state.get("records", []), dict(record)]
    return next_state  # type: ignore[return-value]


def supersede_reflective_item(
    state: ReflectiveSummariesState,
    *,
    bucket: ReflectiveBucket,
    item_id: str,
    superseded_by_item_id: str,
) -> ReflectiveSummariesState:
    """Mark one reflective item as superseded without mutating its statement."""

    selected_item_id = str(item_id or "")
    if not selected_item_id:
        return state

    bucket_items = [dict(existing) for existing in state.get(bucket, [])]
    touched = False
    next_bucket: list[dict[str, object]] = []
    for item in bucket_items:
        if str(item.get("item_id", "") or "") == selected_item_id:
            next_bucket.append(
                {
                    **item,
                    "status": "superseded",
                    "superseded_by_item_id": str(superseded_by_item_id or ""),
                }
            )
            touched = True
        else:
            next_bucket.append(item)

    if not touched:
        return state

    next_state = _touch_state(state)
    next_state[bucket] = next_bucket
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
