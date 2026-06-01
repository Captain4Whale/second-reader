"""Deterministic migration and legacy-adapter helpers for Phase C.3 state cutover."""

from __future__ import annotations

from .schemas import (
    ATTENTIONAL_V2_MECHANISM_VERSION,
    ATTENTIONAL_V2_SCHEMA_VERSION,
    ActiveAttention,
    ActiveAttentionItem,
    ReflectiveFramesState,
    ReflectiveSummariesState,
    SourceRef,
    build_empty_active_attention,
    build_empty_reflective_frames,
)
from .source_spans import dedupe_source_refs


def _clean_text(value: object) -> str:
    """Return one normalized string value."""

    return str(value or "").strip()


def _source_refs(value: object) -> list[SourceRef]:
    """Return structured SourceRefs only."""

    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]  # type: ignore[list-item]


def _text_from(value: dict[str, object], *keys: str) -> str:
    """Return the first non-empty text value from the candidate keys."""

    for key in keys:
        text = _clean_text(value.get(key))
        if text:
            return text
    return ""


def normalize_active_tension_item(value: object) -> ActiveAttentionItem | None:
    """Convert legacy active-attention fields into the current ActiveTension shape."""

    if not isinstance(value, dict):
        return None
    item_id = _clean_text(value.get("item_id"))
    if not item_id:
        return None
    tension_from = _text_from(value, "tension_from", "question_from")
    tension_focus = _text_from(value, "tension_focus", "driving_question", "statement", "answer_boundary")
    working_interpretation = _text_from(value, "working_interpretation", "working_answer")
    if not any((tension_from, tension_focus, working_interpretation)):
        return None

    attention_tags = [
        _clean_text(item)
        for item in value.get("attention_tags", [])
        if _clean_text(item)
    ] if isinstance(value.get("attention_tags"), list) else []

    item: ActiveAttentionItem = {
        "item_id": item_id,
        "attention_tags": attention_tags,
        "tension_from": tension_from,
        "tension_focus": tension_focus,
        "working_interpretation": working_interpretation,
        "source_refs": dedupe_source_refs(_source_refs(value.get("source_refs"))),
        "development_source_refs": dedupe_source_refs(
            [
                *_source_refs(value.get("development_source_refs")),
                *_source_refs(value.get("answer_source_refs")),
            ]
        ),
        "status": _clean_text(value.get("status")) or "open",
    }
    for field in (
        "answered_reason",
        "closed_reason",
        "opened_at_source_span_id",
        "opened_at_unit_span_id",
        "answered_at_source_span_id",
        "answered_at_unit_span_id",
        "closed_at_source_span_id",
        "closed_at_unit_span_id",
    ):
        text = _clean_text(value.get(field))
        if text:
            item[field] = text  # type: ignore[literal-required]
    for field in (
        "opened_at_source_span",
        "opened_at_unit_span",
        "answered_at_source_span",
        "answered_at_unit_span",
        "closed_at_source_span",
        "closed_at_unit_span",
    ):
        raw = value.get(field)
        if isinstance(raw, dict):
            item[field] = dict(raw)  # type: ignore[literal-required]
    return item


def normalize_active_tension_state(
    active_attention: ActiveAttention | dict[str, object] | None,
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ActiveAttention:
    """Return active_attention with legacy question-only fields migrated away."""

    if not isinstance(active_attention, dict):
        return build_empty_active_attention(mechanism_version=mechanism_version)
    state: ActiveAttention = {
        "schema_version": int(active_attention.get("schema_version", ATTENTIONAL_V2_SCHEMA_VERSION) or ATTENTIONAL_V2_SCHEMA_VERSION),
        "mechanism_version": _clean_text(active_attention.get("mechanism_version")) or mechanism_version,
        "updated_at": _clean_text(active_attention.get("updated_at")),
        "active_items": [],
    }
    if not state["updated_at"]:
        state.pop("updated_at", None)
    raw_items = active_attention.get("active_items", [])
    entries = raw_items if isinstance(raw_items, list) else []
    state["active_items"] = [
        item
        for item in (
            normalize_active_tension_item(entry)
            for entry in entries
        )
        if item is not None
    ]
    return state


def migrate_reflective_summaries_to_frames(
    reflective_summaries: ReflectiveSummariesState | None,
    *,
    mechanism_version: str = ATTENTIONAL_V2_MECHANISM_VERSION,
) -> ReflectiveFramesState:
    """Convert legacy reflective summaries into the new reflective-frames shape."""

    if isinstance(reflective_summaries, dict) and reflective_summaries:
        return dict(reflective_summaries)  # type: ignore[return-value]
    return build_empty_reflective_frames(mechanism_version=mechanism_version)
