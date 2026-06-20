"""Phase 6 slow-cycle reasoning, durable reaction truth, and compatibility projection."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from src.iterator_reader.language import language_name
from src.iterator_reader.llm_utils import LLMTraceContext, invoke_structured_output, llm_invocation_scope
from src.reading_core.book_document import BookChapter, ParagraphRecord

from .knowledge import apply_activation_operations
from .llm_calls import (
    _clean_text,
    _json_block,
    _normalize_reaction_candidate,
    _normalize_state_operations,
    _render_prompt,
    _structural_frame,
    _write_prompt_manifest,
)
from .llm_output_tools import (
    CHAPTER_CONSOLIDATION_RESULT_TOOL,
    RECONSOLIDATION_RESULT_TOOL,
    REFLECTIVE_PROMOTION_RESULT_TOOL,
    require_mapping_fields,
)
from .prompts import ATTENTIONAL_V2_PROMPTS
from .schemas import (
    AnchorRecord,
    AnchoredReactionRecord,
    ChapterConsolidationResult,
    KnowledgeActivationsState,
    OutsideLink,
    PriorLink,
    ReactionAnchor,
    ReactionCandidate,
    ReactionRecordsState,
    ReaderPolicy,
    ReconsolidationRecord,
    ReconsolidationRecordsState,
    ReconsolidationResult,
    ReflectiveItem,
    ReflectivePromotionCandidate,
    ReflectivePromotionResult,
    ReflectiveFramesState,
    SearchIntent,
    SlowCycleAuditEnvelope,
    SurfacedReaction,
    ActiveAttentionItem,
    ActiveAttention,
    SourceRef,
)
from .state_ops import (
    append_reaction_record,
    append_reconsolidation_record,
    apply_active_attention_operations,
    supersede_reflective_item,
    upsert_reflective_item,
)
from .state_migration import normalize_active_tension_item, normalize_active_tension_state
from .storage import append_jsonl, chapter_result_compatibility_file, save_json, slow_cycle_audit_file
from .source_spans import dedupe_source_refs, source_ref_from_span


_FEATURED_PRIORITY = {
    "highlight": 0,
    "discern": 1,
    "association": 2,
    "retrospect": 3,
    "curious": 4,
}
_REFLECTIVE_BUCKETS = {
    "chapter_understandings",
    "book_level_frames",
    "durable_definitions",
    "stabilized_motifs",
    "resolved_questions_of_record",
    "chapter_end_notes",
}
_COMPAT_FAMILIES = {"highlight", "discern", "association", "retrospect", "curious", "silent"}
_SLOW_CYCLE_AUDIT_SCHEMA = "attentional_v2.slow_cycle_audit.v1"


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_ref_evidence(source_refs: object) -> tuple[int, list[str], str]:
    """Return compact SourceRef evidence metadata without copying refs."""

    if not isinstance(source_refs, list):
        return 0, [], "missing_source_refs"
    statuses: list[str] = []
    for source_ref in source_refs:
        if not isinstance(source_ref, Mapping):
            continue
        resolution = source_ref.get("resolution")
        status = _clean_text(resolution.get("status")) if isinstance(resolution, Mapping) else ""
        statuses.append(status or "not_assessed")
    if not statuses:
        return 0, [], "missing_source_refs"
    compact_statuses = list(dict.fromkeys(statuses))
    if any(status != "not_assessed" for status in compact_statuses):
        return len(statuses), compact_statuses, "source_refs_present"
    return len(statuses), compact_statuses, "not_assessed"


def _has_live_question_fields(item: Mapping[str, object]) -> bool:
    """Return whether a carry-forward item uses the current ActiveTension schema."""

    return any(
        _clean_text(item.get(field))
        for field in (
            "tension_from",
            "tension_focus",
            "working_interpretation",
        )
    )


def _merge_unique_texts(*values: object) -> list[str]:
    """Merge string lists while preserving order."""

    ordered: list[str] = []
    seen: set[str] = set()
    for raw in values:
        if not isinstance(raw, list):
            continue
        for item in raw:
            text = _clean_text(item)
            if not text or text in seen:
                continue
            seen.add(text)
            ordered.append(text)
    return ordered


def _with_source_ref_evidence(
    envelope: SlowCycleAuditEnvelope,
    source_refs: object,
) -> SlowCycleAuditEnvelope:
    """Attach compact SourceRef evidence metadata to one audit envelope."""

    source_ref_count, statuses, evidence_status = _source_ref_evidence(source_refs)
    envelope["source_ref_count"] = source_ref_count
    envelope["source_ref_resolution_statuses"] = statuses
    envelope["promotion_evidence_status"] = evidence_status
    return envelope


def _promotion_audit_envelope(
    *,
    chapter_ref: str,
    candidate: ReflectivePromotionCandidate,
    result: ReflectivePromotionResult,
) -> SlowCycleAuditEnvelope:
    """Build audit-only candidate/settlement evidence for one promotion decision."""

    reflective_item = result.get("reflective_item") if isinstance(result.get("reflective_item"), Mapping) else None
    promoted = str(result.get("decision", "") or "") == "promote" and reflective_item is not None
    evidence_source_refs = reflective_item.get("source_refs") if promoted and reflective_item is not None else candidate.get("source_refs")
    envelope: SlowCycleAuditEnvelope = {
        "trigger_type": "chapter_end",
        "chapter_ref": chapter_ref,
        "candidate_type": "reflective_promotion",
        "candidate_id": _clean_text(candidate.get("candidate_id")),
        "target_bucket": _clean_text(result.get("target_bucket") or candidate.get("target_bucket")),
        "settlement_decision": "promoted" if promoted else "withheld",
        "settlement_reason": _clean_text(result.get("reason")),
        "supersede_bucket": _clean_text(result.get("supersede_bucket")),
        "supersede_item_id": _clean_text(result.get("supersede_item_id")),
    }
    if promoted and reflective_item is not None:
        envelope["settled_item_id"] = _clean_text(reflective_item.get("item_id"))
    else:
        envelope["withhold_promotion_reason"] = _clean_text(result.get("reason")) or "not_assessed"
    return _with_source_ref_evidence(envelope, evidence_source_refs)


def _carry_forward_audit_envelopes(
    *,
    chapter_ref: str,
    post_cooling_active_attention: ActiveAttention,
    carry_forward: list[ActiveAttentionItem],
) -> list[SlowCycleAuditEnvelope]:
    """Build audit-only carried/not-carried evidence without changing carry behavior."""

    envelopes: list[SlowCycleAuditEnvelope] = []
    active_items_by_id = {
        _clean_text(item.get("item_id")): item
        for item in post_cooling_active_attention.get("active_items", [])
        if isinstance(item, Mapping) and _clean_text(item.get("item_id"))
    }
    carried_ids: set[str] = set()
    for item in carry_forward:
        item_id = _clean_text(item.get("item_id"))
        if item_id:
            carried_ids.add(item_id)
        existing_item = active_items_by_id.get(item_id, {})
        if not existing_item and not _has_live_question_fields(item):
            envelope = {
                "trigger_type": "chapter_end",
                "chapter_ref": chapter_ref,
                "candidate_type": "cross_chapter_carry_forward",
                "candidate_id": item_id,
                "settlement_decision": "rejected",
                "settlement_reason": "missing_live_question_fields",
                "not_carried_reason": "missing_live_question_fields",
            }
            envelopes.append(_with_source_ref_evidence(envelope, item.get("source_refs")))
            continue
        envelope: SlowCycleAuditEnvelope = {
            "trigger_type": "chapter_end",
            "chapter_ref": chapter_ref,
            "candidate_type": "cross_chapter_carry_forward",
            "candidate_id": item_id,
            "settlement_decision": "carried",
            "carry_forward_reason": "selected_by_chapter_consolidation",
            "settlement_reason": _clean_text(item.get("status")) or "selected_by_chapter_consolidation",
        }
        audit_source_refs = dedupe_source_refs(
            [
                *(existing_item.get("source_refs", []) if isinstance(existing_item.get("source_refs"), list) else []),
                *(item.get("source_refs", []) if isinstance(item.get("source_refs"), list) else []),
            ]
        )
        envelopes.append(_with_source_ref_evidence(envelope, audit_source_refs))

    for item_id, item in active_items_by_id.items():
        if item_id in carried_ids:
            continue
        envelope = {
            "trigger_type": "chapter_end",
            "chapter_ref": chapter_ref,
            "candidate_type": "cross_chapter_carry_forward",
            "candidate_id": item_id,
            "settlement_decision": "not_carried",
            "not_carried_reason": "not_selected_by_chapter_consolidation",
            "settlement_reason": "not_selected_by_chapter_consolidation",
        }
        envelopes.append(_with_source_ref_evidence(envelope, item.get("source_refs")))
    return envelopes


def _knowledge_update_audit_envelopes(
    *,
    chapter_ref: str,
    operations: list[dict[str, object]],
) -> list[SlowCycleAuditEnvelope]:
    """Build compact warrant/context envelopes for knowledge activation operations."""

    envelopes: list[SlowCycleAuditEnvelope] = []
    for index, operation in enumerate(operations):
        if not isinstance(operation, Mapping):
            continue
        payload = operation.get("payload")
        payload = payload if isinstance(payload, Mapping) else {}
        source_refs = []
        trigger_source_ref = payload.get("trigger_source_ref")
        if isinstance(trigger_source_ref, Mapping):
            source_refs.append(trigger_source_ref)
        if isinstance(payload.get("source_refs"), list):
            source_refs.extend(item for item in payload.get("source_refs", []) if isinstance(item, Mapping))
        envelope: SlowCycleAuditEnvelope = {
            "trigger_type": "chapter_end",
            "chapter_ref": chapter_ref,
            "candidate_type": "knowledge_activation_update",
            "candidate_id": _clean_text(operation.get("item_id") or payload.get("activation_id")) or f"knowledge_activation_update:{index}",
            "target_bucket": "knowledge_activations",
            "settlement_decision": "warrant_context_update_observed",
            "settlement_reason": _clean_text(operation.get("reason")) or "not_assessed",
            "promotion_evidence_status": "warrant_context_not_source_truth",
        }
        evidence = _with_source_ref_evidence(envelope, source_refs)
        evidence["promotion_evidence_status"] = "warrant_context_not_source_truth"
        envelopes.append(evidence)
    return envelopes


def _optional_reaction_audit_envelope(
    *,
    chapter_ref: str,
    reaction_record: AnchoredReactionRecord,
) -> SlowCycleAuditEnvelope:
    """Build compact visible-trace evidence for a chapter-end reaction."""

    envelope: SlowCycleAuditEnvelope = {
        "trigger_type": "chapter_end",
        "chapter_ref": chapter_ref,
        "candidate_type": "optional_chapter_reaction",
        "candidate_id": _clean_text(reaction_record.get("reaction_id")),
        "settled_item_id": _clean_text(reaction_record.get("reaction_id")),
        "settlement_decision": "visible_trace_appended",
        "settlement_reason": "visible_trace_not_semantic_memory",
        "promotion_evidence_status": "visible_trace_not_semantic_memory",
    }
    evidence = _with_source_ref_evidence(envelope, [reaction_record.get("primary_source_ref")])
    evidence["promotion_evidence_status"] = "visible_trace_not_semantic_memory"
    return evidence


def _record_slow_cycle_audit(
    output_dir: Path | None,
    *,
    chapter_ref: str,
    envelopes: list[SlowCycleAuditEnvelope],
) -> None:
    """Persist one compact slow-cycle audit row when evidence exists."""

    if output_dir is None or not envelopes:
        return
    append_jsonl(
        slow_cycle_audit_file(output_dir),
        {
            "recorded_at": _timestamp(),
            "audit_schema": _SLOW_CYCLE_AUDIT_SCHEMA,
            "trigger_type": "chapter_end",
            "chapter_ref": chapter_ref,
            "candidate_count": len(envelopes),
            "envelopes": envelopes,
        },
    )


def build_reaction_anchor(anchor: AnchorRecord | dict[str, object]) -> ReactionAnchor:
    """Project one retained anchor into the embedded durable-reaction anchor shape."""

    locator = anchor.get("locator")
    return {
        "anchor_id": _clean_text(anchor.get("anchor_id")),
        "sentence_start_id": _clean_text(anchor.get("sentence_start_id")),
        "sentence_end_id": _clean_text(anchor.get("sentence_end_id") or anchor.get("sentence_start_id")),
        "quote": _clean_text(anchor.get("quote")),
        "locator": dict(locator) if isinstance(locator, dict) else {},
    }


def build_reaction_source_ref(value: SourceRef | dict[str, object]) -> SourceRef:
    """Project a source ref into the embedded durable-reaction source-ref shape."""

    if not isinstance(value, dict):
        return source_ref_from_span({}, quote="", role="reaction_anchor")
    source_span = value.get("source_span")
    return source_ref_from_span(
        source_span if isinstance(source_span, Mapping) else {},
        quote=_clean_text(value.get("quote")),
        role=_clean_text(value.get("role")) or "reaction_anchor",
        resolution=value.get("resolution") if isinstance(value.get("resolution"), Mapping) else None,
    )


def _source_ref_from_legacy_anchor(anchor: AnchorRecord | dict[str, object]) -> SourceRef:
    """Best-effort adapter for old tests and historical callers."""

    locator = anchor.get("locator")
    source_span = locator.get("source_span") if isinstance(locator, Mapping) else {}
    return source_ref_from_span(
        source_span if isinstance(source_span, Mapping) else {},
        quote=_clean_text(anchor.get("quote")),
        role="reaction_anchor",
        resolution={"status": "legacy_anchor_projection"},
    )


def _copy_prior_link(value: object) -> PriorLink | None:
    """Normalize one surfaced prior-link payload when present."""

    if not isinstance(value, Mapping):
        return None
    ref_ids = [_clean_text(item) for item in value.get("ref_ids", []) if _clean_text(item)]
    relation = _clean_text(value.get("relation"))
    note = _clean_text(value.get("note"))
    if not (ref_ids or relation or note):
        return None
    payload: PriorLink = {}
    if ref_ids:
        payload["ref_ids"] = ref_ids
    if relation:
        payload["relation"] = relation
    if note:
        payload["note"] = note
    return payload


def _copy_outside_link(value: object) -> OutsideLink | None:
    """Normalize one surfaced outside-link payload when present."""

    if not isinstance(value, Mapping):
        return None
    kind = _clean_text(value.get("kind"))
    label = _clean_text(value.get("label"))
    note = _clean_text(value.get("note"))
    if not (kind or label or note):
        return None
    payload: OutsideLink = {}
    if kind:
        payload["kind"] = kind
    if label:
        payload["label"] = label
    if note:
        payload["note"] = note
    return payload


def _copy_search_intent(value: object) -> SearchIntent | None:
    """Normalize one surfaced search-intent payload when present."""

    if not isinstance(value, Mapping):
        return None
    query = _clean_text(value.get("query"))
    rationale = _clean_text(value.get("rationale"))
    if not (query or rationale):
        return None
    payload: SearchIntent = {}
    if query:
        payload["query"] = query
    if rationale:
        payload["rationale"] = rationale
    return payload


def _surfaced_reaction_from_candidate(reaction: ReactionCandidate) -> SurfacedReaction | None:
    """Project one legacy reaction candidate into the surfaced-reaction truth shape."""

    content = _clean_text(reaction.get("content"))
    source_quote = _clean_text(reaction.get("source_quote") or reaction.get("anchor_quote"))
    if not (content and source_quote):
        return None
    return {
        "source_quote": source_quote,
        "content": content,
        "prior_link": None,
        "outside_link": None,
        "search_intent": _legacy_search_intent_from_candidate(reaction),
    }


def compat_reaction_family(payload: Mapping[str, object]) -> str:
    """Derive the legacy family label from one native persisted reaction shape."""

    if _copy_search_intent(payload.get("search_intent")) is not None:
        return "curious"
    if _copy_prior_link(payload.get("prior_link")) is not None:
        return "retrospect"
    if _copy_outside_link(payload.get("outside_link")) is not None:
        return "association"

    compat_family = _clean_text(payload.get("compat_family"))
    if compat_family == "silent":
        return "silent"
    if compat_family in _COMPAT_FAMILIES and compat_family != "silent":
        return compat_family

    explicit_type = _clean_text(payload.get("type"))
    if explicit_type == "silent":
        return "silent"
    if explicit_type in _COMPAT_FAMILIES and explicit_type != "silent":
        return explicit_type

    thought = _clean_text(payload.get("thought")) or _clean_text(payload.get("content"))
    source_quote = _clean_text(payload.get("source_quote") or payload.get("anchor_quote"))
    if thought and len(thought) <= max(120, len(source_quote) + 60):
        return "highlight"
    if thought:
        return "discern"
    return "highlight"


def compat_search_query(payload: Mapping[str, object]) -> str:
    """Project the legacy search-query sidecar from native surfaced fields."""

    search_intent = _copy_search_intent(payload.get("search_intent"))
    if search_intent is not None:
        return _clean_text(search_intent.get("query"))
    return _clean_text(payload.get("search_query"))


def _legacy_search_intent_from_candidate(reaction: ReactionCandidate) -> SearchIntent | None:
    """Project a legacy curious payload into the native surfaced search-intent shape."""

    query = _clean_text(reaction.get("search_query"))
    if not query:
        return None
    return {
        "query": query,
        "rationale": "",
    }


def derive_reaction_id(
    *,
    chapter_ref: str,
    emitted_at_source_span_id: str,
    reaction_type: str,
    ordinal: int | None = None,
) -> str:
    """Build a deterministic durable-reaction id from chapter, source span, and type."""

    parts = [
        "rx",
        _clean_text(chapter_ref).replace(" ", "_") or "chapter",
        _clean_text(emitted_at_source_span_id) or "source",
        _clean_text(reaction_type) or "reaction",
    ]
    if ordinal is not None and ordinal > 0:
        parts.append(str(int(ordinal)))
    return ":".join(parts)


def derive_reconsolidation_record_id(
    *,
    prior_reaction_id: str,
    later_sentence_id: str,
) -> str:
    """Build a deterministic reconsolidation-record id."""

    return f"rc:{_clean_text(prior_reaction_id)}:{_clean_text(later_sentence_id)}"


def build_reaction_record(
    *,
    reaction: ReactionCandidate,
    primary_source_ref: SourceRef | dict[str, object] | None = None,
    related_source_refs: list[SourceRef | dict[str, object]] | None = None,
    primary_anchor: AnchorRecord | dict[str, object] | None = None,
    related_anchors: list[AnchorRecord | dict[str, object]] | None = None,
    chapter_id: int,
    chapter_ref: str,
    emitted_at_source_span_id: str = "",
    emitted_at_sentence_id: str = "",
    reaction_id: str | None = None,
    reconsolidation_record_id: str | None = None,
    supersedes_reaction_id: str | None = None,
    compatibility_section_ref: str | None = None,
    created_at: str | None = None,
    ordinal: int | None = None,
    record_source: str = "legacy_builder",
) -> AnchoredReactionRecord:
    """Compatibility adapter from legacy candidates into the surfaced-native record builder."""

    surfaced_reaction = _surfaced_reaction_from_candidate(reaction)
    if surfaced_reaction is None:
        raise ValueError("legacy reaction candidate must contain anchor_quote and content")
    record = build_reaction_record_from_surfaced_reaction(
        reaction=surfaced_reaction,
        primary_source_ref=primary_source_ref,
        related_source_refs=related_source_refs,
        primary_anchor=primary_anchor,
        related_anchors=related_anchors,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        emitted_at_source_span_id=emitted_at_source_span_id or emitted_at_sentence_id,
        reaction_id=reaction_id,
        reconsolidation_record_id=reconsolidation_record_id,
        supersedes_reaction_id=supersedes_reaction_id,
        compatibility_section_ref=compatibility_section_ref,
        created_at=created_at,
        ordinal=ordinal,
        compat_family_override=_clean_text(reaction.get("type")),
    )
    if record is None:
        raise ValueError("legacy reaction candidate could not be converted into a surfaced reaction")
    record["record_source"] = _clean_text(record_source) or "legacy_candidate_adapter"
    record["search_results"] = [
        dict(item)
        for item in reaction.get("search_results", [])
        if isinstance(item, dict)
    ] if isinstance(reaction.get("search_results"), list) else []
    record["search_query"] = compat_search_query({"search_intent": record.get("search_intent"), "search_query": reaction.get("search_query")})
    return record


def build_reaction_record_from_surfaced_reaction(
    *,
    reaction: SurfacedReaction,
    primary_source_ref: SourceRef | dict[str, object] | None = None,
    related_source_refs: list[SourceRef | dict[str, object]] | None = None,
    primary_anchor: AnchorRecord | dict[str, object] | None = None,
    related_anchors: list[AnchorRecord | dict[str, object]] | None = None,
    chapter_id: int,
    chapter_ref: str,
    emitted_at_source_span_id: str = "",
    emitted_at_sentence_id: str = "",
    reaction_id: str | None = None,
    reconsolidation_record_id: str | None = None,
    supersedes_reaction_id: str | None = None,
    compatibility_section_ref: str | None = None,
    created_at: str | None = None,
    ordinal: int | None = None,
    compat_family_override: str | None = None,
) -> AnchoredReactionRecord | None:
    """Build one native persisted reaction record directly from Digest-owned surfaced output."""

    thought = _clean_text(reaction.get("content"))
    if not thought:
        return None

    normalized_primary_source_ref = (
        build_reaction_source_ref(primary_source_ref)
        if isinstance(primary_source_ref, dict)
        else _source_ref_from_legacy_anchor(primary_anchor or {})
    )
    normalized_related = [
        build_reaction_source_ref(ref)
        for ref in (related_source_refs or [])
        if isinstance(ref, dict)
    ]
    if not normalized_related and related_anchors:
        normalized_related = [_source_ref_from_legacy_anchor(anchor) for anchor in related_anchors if isinstance(anchor, dict)]
    prior_link = _copy_prior_link(reaction.get("prior_link"))
    outside_link = _copy_outside_link(reaction.get("outside_link"))
    search_intent = _copy_search_intent(reaction.get("search_intent"))
    override_family = _clean_text(compat_family_override)
    if override_family not in _COMPAT_FAMILIES:
        override_family = ""
    compat_family = override_family or compat_reaction_family(
        {
            "content": thought,
            "source_quote": _clean_text(reaction.get("source_quote") or reaction.get("anchor_quote"))
            or _clean_text(normalized_primary_source_ref.get("quote")),
            "prior_link": prior_link,
            "outside_link": outside_link,
            "search_intent": search_intent,
        }
    )

    return {
        "reaction_id": reaction_id
        or derive_reaction_id(
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=emitted_at_source_span_id or emitted_at_sentence_id,
            reaction_type=compat_family,
            ordinal=ordinal,
        ),
        "chapter_id": int(chapter_id),
        "chapter_ref": _clean_text(chapter_ref),
        "emitted_at_source_span_id": _clean_text(emitted_at_source_span_id or emitted_at_sentence_id),
        "record_source": "read_surface",
        "type": compat_family,  # type: ignore[typeddict-item]
        "compat_family": compat_family,  # type: ignore[typeddict-item]
        "thought": thought,
        "source_quote": _clean_text(reaction.get("source_quote") or reaction.get("anchor_quote"))
        or _clean_text(normalized_primary_source_ref.get("quote")),
        "primary_source_ref": normalized_primary_source_ref,
        "related_source_refs": normalized_related,
        "reconsolidation_record_id": _clean_text(reconsolidation_record_id),
        "supersedes_reaction_id": _clean_text(supersedes_reaction_id),
        "compatibility_section_ref": _clean_text(compatibility_section_ref),
        "prior_link": prior_link,
        "outside_link": outside_link,
        "search_intent": search_intent,
        "search_query": compat_search_query({"search_intent": search_intent}),
        "search_results": [],
        "created_at": created_at or _timestamp(),
    }


def reaction_records_for_chapter(
    state: ReactionRecordsState,
    *,
    chapter_ref: str,
) -> list[AnchoredReactionRecord]:
    """Return one chapter's durable visible reactions in persisted order."""

    return [
        dict(record)
        for record in state.get("records", [])
        if isinstance(record, dict) and _clean_text(record.get("chapter_ref")) == _clean_text(chapter_ref)
    ]


def _target_locator_from_source_ref(source_ref: SourceRef | dict[str, object]) -> dict[str, object] | None:
    """Project one source ref into the current target-locator shape when EPUB CFI is available."""

    locator = source_ref.get("locator")
    if not isinstance(locator, dict):
        return None
    href = _clean_text(locator.get("href"))
    match_text = _clean_text(source_ref.get("quote"))
    if not href or not match_text:
        return None
    return {
        "href": href,
        "start_cfi": locator.get("start_cfi"),
        "end_cfi": locator.get("end_cfi"),
        "match_text": match_text,
        "match_mode": "exact",
    }


def _compatibility_section_ref(
    record: AnchoredReactionRecord | dict[str, object],
    *,
    chapter_id: int,
) -> str:
    """Resolve the current temporary section-ref compatibility sidecar."""

    explicit = _clean_text(record.get("compatibility_section_ref"))
    if explicit:
        return explicit
    primary_source_ref = record.get("primary_source_ref")
    if isinstance(primary_source_ref, dict):
        source_span = primary_source_ref.get("source_span")
        if isinstance(source_span, dict):
            start = source_span.get("start_cursor")
            if isinstance(start, dict):
                paragraph_index = int(start.get("paragraph_index", 0) or 0)
                if paragraph_index > 0:
                    return f"{int(chapter_id)}.{paragraph_index}"
    return f"{int(chapter_id)}.1"


def _paragraph_locator(paragraph: ParagraphRecord | dict[str, object]) -> dict[str, object] | None:
    """Project one canonical paragraph into the current section-locator shape."""

    href = _clean_text(paragraph.get("href"))
    paragraph_index = int(paragraph.get("paragraph_index", 0) or 0)
    if not href or paragraph_index <= 0:
        return None
    return {
        "href": href,
        "start_cfi": paragraph.get("start_cfi"),
        "end_cfi": paragraph.get("end_cfi"),
        "paragraph_start": paragraph_index,
        "paragraph_end": paragraph_index,
    }


def _section_summary(record: AnchoredReactionRecord | dict[str, object], paragraph_index: int | None = None) -> str:
    """Build one compact temporary section summary for compatibility payloads."""

    thought = _clean_text(record.get("thought"))
    if thought:
        return thought[:160]
    if paragraph_index and paragraph_index > 0:
        return f"Anchored reactions around paragraph {paragraph_index}."
    return "Anchored reactions."


def project_chapter_result_compatibility(
    *,
    book_id: str,
    chapter: BookChapter | dict[str, object],
    reaction_records: list[AnchoredReactionRecord] | ReactionRecordsState,
    output_language: str,
    output_dir: Path | None = None,
    persist: bool = False,
) -> dict[str, object]:
    """Project mechanism-authored reactions into the current chapter_result-compatible shape."""

    chapter_id = int(chapter.get("id", 0) or 0)
    chapter_ref = _clean_text(chapter.get("reference") or chapter.get("chapter_ref") or f"Chapter {chapter_id}")
    chapter_title = _clean_text(chapter.get("title"))
    chapter_heading = dict(chapter.get("chapter_heading", {})) if isinstance(chapter.get("chapter_heading"), dict) else None
    paragraphs = [
        dict(paragraph)
        for paragraph in chapter.get("paragraphs", [])
        if isinstance(paragraph, dict)
    ]
    paragraphs_by_index = {
        int(paragraph.get("paragraph_index", 0) or 0): paragraph
        for paragraph in paragraphs
        if int(paragraph.get("paragraph_index", 0) or 0) > 0
    }

    records = (
        [dict(item) for item in reaction_records.get("records", []) if isinstance(item, dict)]
        if isinstance(reaction_records, dict) and "records" in reaction_records
        else [dict(item) for item in reaction_records if isinstance(item, dict)]
    )
    records = [
        record
        for record in records
        if _clean_text(record.get("chapter_ref")) == chapter_ref and compat_reaction_family(record) != "silent"
    ]

    section_groups: dict[str, dict[str, object]] = {}
    reaction_counts: Counter[str] = Counter()
    featured_candidates: list[dict[str, object]] = []

    for record in records:
        primary_source_ref = record.get("primary_source_ref")
        if not isinstance(primary_source_ref, dict):
            continue
        section_ref = _compatibility_section_ref(record, chapter_id=chapter_id)
        paragraph_index = 0
        source_span = primary_source_ref.get("source_span")
        if isinstance(source_span, dict) and isinstance(source_span.get("start_cursor"), dict):
            paragraph_index = int(source_span["start_cursor"].get("paragraph_index", 0) or 0)
        paragraph = paragraphs_by_index.get(paragraph_index, {})
        section = section_groups.get(section_ref)
        if section is None:
            section = {
                "segment_id": f"compat:{section_ref}",
                "segment_ref": section_ref,
                "summary": _section_summary(record, paragraph_index=paragraph_index or None),
                "original_text": _clean_text(paragraph.get("text")),
                "verdict": "keep",
                "quality_status": "kept",
                "reflection_summary": "",
                "reflection_reason_codes": [],
                "marginalia": [],
                "reactions": [],
            }
            paragraph_locator = _paragraph_locator(paragraph)
            if paragraph_locator is not None:
                section["locator"] = paragraph_locator
            section_groups[section_ref] = section

        target_locator = _target_locator_from_source_ref(primary_source_ref)
        reaction_type = compat_reaction_family(record)
        reaction_card = {
            "reaction_id": _clean_text(record.get("reaction_id")),
            "type": reaction_type,
            "source_quote": _clean_text(record.get("source_quote") or primary_source_ref.get("quote")),
            "content": _clean_text(record.get("thought")),
            "search_query": compat_search_query(record),
            "search_results": [
                dict(item)
                for item in record.get("search_results", [])
                if isinstance(item, dict)
            ]
            if isinstance(record.get("search_results"), list)
            else [],
            "primary_source_ref": build_reaction_source_ref(primary_source_ref),
            "related_source_refs": [
                build_reaction_source_ref(source_ref)
                for source_ref in record.get("related_source_refs", [])
                if isinstance(source_ref, dict)
            ]
            if isinstance(record.get("related_source_refs"), list)
            else [],
            "supersedes_reaction_id": _clean_text(record.get("supersedes_reaction_id")) or None,
        }
        if target_locator is not None:
            reaction_card["target_locator"] = target_locator
        section["marginalia"].append(reaction_card)
        section["reactions"].append(reaction_card)
        reaction_counts[reaction_type] += 1
        featured_candidates.append(
            {
                "reaction_id": _clean_text(record.get("reaction_id")),
                "type": reaction_type,
                "segment_ref": section_ref,
                "source_quote": _clean_text(record.get("source_quote") or primary_source_ref.get("quote")),
                "content": _clean_text(record.get("thought")),
                "target_locator": target_locator or {},
                "primary_source_ref": build_reaction_source_ref(primary_source_ref),
                "related_source_refs": [
                    build_reaction_source_ref(source_ref)
                    for source_ref in record.get("related_source_refs", [])
                    if isinstance(source_ref, dict)
                ]
                if isinstance(record.get("related_source_refs"), list)
                else [],
                "supersedes_reaction_id": _clean_text(record.get("supersedes_reaction_id")) or None,
            }
        )

    sections = sorted(section_groups.values(), key=lambda item: str(item.get("segment_ref", "")))
    featured = sorted(
        featured_candidates,
        key=lambda item: (
            _FEATURED_PRIORITY.get(str(item.get("type", "")), 99),
            str(item.get("segment_ref", "")),
            str(item.get("reaction_id", "")),
        ),
    )[:3]
    payload = {
        "book_id": book_id,
        "chapter": {
            "id": chapter_id,
            "title": chapter_title,
            "reference": chapter_ref,
            "status": "completed",
        },
        "chapter_heading": chapter_heading,
        "output_language": output_language,
        "generated_at": _timestamp(),
        "sections": sections,
        "chapter_reflection": {},
        "featured_marginalia": featured,
        "featured_reactions": featured,
        "visible_marginalia_count": sum(len(section.get("marginalia", section.get("reactions", []))) for section in sections),
        "visible_reaction_count": sum(len(section.get("reactions", [])) for section in sections),
        "marginalia_type_diversity": len(reaction_counts),
        "reaction_type_diversity": len(reaction_counts),
        "ui_summary": {
            "kept_section_count": len(sections),
            "skipped_section_count": 0,
            "marginalia_counts": dict(sorted(reaction_counts.items())),
            "reaction_counts": dict(sorted(reaction_counts.items())),
        },
    }
    if persist and output_dir is not None:
        save_json(chapter_result_compatibility_file(output_dir, chapter_id), payload)
    return payload


def _normalize_reflective_item(value: object, *, chapter_ref: str) -> ReflectiveItem | None:
    """Normalize one reflective item payload."""

    if not isinstance(value, dict):
        return None
    statement = _clean_text(value.get("statement"))
    if not statement:
        return None
    return {
        "item_id": _clean_text(value.get("item_id")),
        "statement": statement,
        "source_refs": [
            build_reaction_source_ref(item)
            for item in value.get("source_refs", [])
            if isinstance(item, dict)
        ]
        if isinstance(value.get("source_refs"), list)
        else [],
        "confidence_band": _clean_text(value.get("confidence_band")) or "working",
        "promoted_from": _clean_text(value.get("promoted_from")) or "active_attention_item",
        "status": _clean_text(value.get("status")) or "active",
        "chapter_ref": chapter_ref,
    }


def _normalize_reflective_promotion_candidate(value: object) -> ReflectivePromotionCandidate | None:
    """Normalize one promotion-candidate payload."""

    if not isinstance(value, dict):
        return None
    statement = _clean_text(value.get("statement"))
    if not statement:
        return None
    target_bucket = _clean_text(value.get("target_bucket")) or "chapter_understandings"
    if target_bucket not in _REFLECTIVE_BUCKETS:
        target_bucket = "chapter_understandings"
    return {
        "candidate_id": _clean_text(value.get("candidate_id")),
        "statement": statement,
        "source_refs": [
            build_reaction_source_ref(item)
            for item in value.get("source_refs", [])
            if isinstance(item, dict)
        ]
        if isinstance(value.get("source_refs"), list)
        else [],
        "promoted_from": _clean_text(value.get("promoted_from")) or "chapter_sweep",
        "target_bucket": target_bucket,
        "rationale": _clean_text(value.get("rationale")),
    }


def _normalize_reflective_promotion_result(payload: object) -> ReflectivePromotionResult:
    """Normalize one reflective-promotion node payload."""

    if not isinstance(payload, dict):
        return {
            "decision": "withhold",
            "reason": "",
            "target_bucket": "chapter_understandings",
            "reflective_item": None,
            "supersede_bucket": "",
            "supersede_item_id": "",
            "state_operations": [],
        }

    target_bucket = _clean_text(payload.get("target_bucket")) or "chapter_understandings"
    if target_bucket not in _REFLECTIVE_BUCKETS:
        target_bucket = "chapter_understandings"
    decision = _clean_text(payload.get("decision")).lower()
    if decision not in {"promote", "withhold"}:
        decision = "withhold"
    reflective_item = _normalize_reflective_item(payload.get("reflective_item"), chapter_ref=_clean_text(payload.get("chapter_ref")))
    if decision == "promote" and reflective_item is None:
        decision = "withhold"
    supersede_bucket = _clean_text(payload.get("supersede_bucket"))
    if supersede_bucket and supersede_bucket not in _REFLECTIVE_BUCKETS:
        supersede_bucket = ""
    return {
        "decision": decision,  # type: ignore[typeddict-item]
        "reason": _clean_text(payload.get("reason")),
        "target_bucket": target_bucket,
        "reflective_item": reflective_item,
        "supersede_bucket": supersede_bucket,
        "supersede_item_id": _clean_text(payload.get("supersede_item_id")),
        "state_operations": _normalize_state_operations(payload.get("state_operations")),
    }


def reflective_promotion(
    *,
    candidate: ReflectivePromotionCandidate,
    current_reflective_state: ReflectiveFramesState,
    policy_snapshot: ReaderPolicy,
    output_language: str,
    chapter_ref: str,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
) -> ReflectivePromotionResult:
    """Run the reflective-promotion node."""

    prompts = ATTENTIONAL_V2_PROMPTS
    structural_frame = _structural_frame(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language=output_language,
    )
    user_prompt = _render_prompt(
        prompts.reflective_promotion_prompt,
        structural_frame=_json_block(structural_frame),
        candidate=_json_block(candidate),
        current_reflective_state=_json_block(current_reflective_state),
        policy_snapshot=_json_block(policy_snapshot),
        output_language_name=language_name(output_language),
        chapter_ref=chapter_ref,
    )
    _write_prompt_manifest(
        output_dir,
        node_name="reflective_promotion",
        prompt_version=prompts.reflective_promotion_version,
        system_prompt=prompts.reflective_promotion_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )
    with llm_invocation_scope(
        trace_context=LLMTraceContext(stage="phase6", node="reflective_promotion")
    ):
        payload = invoke_structured_output(
            prompts.reflective_promotion_system,
            user_prompt,
            output_tool=REFLECTIVE_PROMOTION_RESULT_TOOL,
            validator=require_mapping_fields("decision", "reason"),
        ).payload
    normalized = _normalize_reflective_promotion_result(payload)
    if normalized.get("reflective_item"):
        normalized["reflective_item"]["chapter_ref"] = chapter_ref
    return normalized


def apply_reflective_promotion(
    state: ReflectiveFramesState,
    result: ReflectivePromotionResult,
) -> ReflectiveFramesState:
    """Apply one normalized reflective-promotion result."""

    if str(result.get("decision", "") or "") != "promote":
        return state

    reflective_item = result.get("reflective_item")
    if not isinstance(reflective_item, dict):
        return state

    next_state = state
    supersede_bucket = _clean_text(result.get("supersede_bucket"))
    supersede_item_id = _clean_text(result.get("supersede_item_id"))
    if supersede_bucket and supersede_item_id:
        next_state = supersede_reflective_item(
            next_state,
            bucket=supersede_bucket,  # type: ignore[arg-type]
            item_id=supersede_item_id,
            superseded_by_item_id=_clean_text(reflective_item.get("item_id")),
        )
    target_bucket = _clean_text(result.get("target_bucket")) or "chapter_understandings"
    if target_bucket not in _REFLECTIVE_BUCKETS:
        target_bucket = "chapter_understandings"
    return upsert_reflective_item(
        next_state,
        bucket=target_bucket,  # type: ignore[arg-type]
        item=reflective_item,
    )


def _normalize_reconsolidation_record(
    payload: object,
    *,
    prior_reaction_id: str,
    new_reaction_id: str,
) -> ReconsolidationRecord | None:
    """Normalize one reconsolidation-record payload."""

    if not isinstance(payload, dict):
        return None
    change_kind = _clean_text(payload.get("change_kind"))
    what_changed = _clean_text(payload.get("what_changed"))
    rationale = _clean_text(payload.get("rationale"))
    if not any([change_kind, what_changed, rationale]):
        return None
    return {
        "record_id": _clean_text(payload.get("record_id")),
        "prior_reaction_id": prior_reaction_id,
        "new_reaction_id": new_reaction_id,
        "change_kind": change_kind or "reframed",
        "what_changed": what_changed,
        "rationale": rationale,
        "created_at": _timestamp(),
    }


def reconsolidation(
    *,
    earlier_reaction: AnchoredReactionRecord,
    earlier_anchor_context: list[dict[str, object]],
    later_source_ref: SourceRef | dict[str, object],
    current_understanding_snapshot: dict[str, object],
    policy_snapshot: ReaderPolicy,
    output_language: str,
    chapter_id: int,
    chapter_ref: str,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
) -> ReconsolidationResult:
    """Run the reconsolidation node for one material later reinterpretation."""

    prompts = ATTENTIONAL_V2_PROMPTS
    structural_frame = _structural_frame(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language=output_language,
    )
    later_source_ref_payload = build_reaction_source_ref(later_source_ref)
    user_prompt = _render_prompt(
        prompts.reconsolidation_prompt,
        structural_frame=_json_block(structural_frame),
        earlier_reaction=_json_block(earlier_reaction),
        earlier_anchor_context=_json_block(earlier_anchor_context),
        later_anchor=_json_block(later_source_ref_payload),
        current_understanding_snapshot=_json_block(current_understanding_snapshot),
        policy_snapshot=_json_block(policy_snapshot),
        output_language_name=language_name(output_language),
    )
    _write_prompt_manifest(
        output_dir,
        node_name="reconsolidation",
        prompt_version=prompts.reconsolidation_version,
        system_prompt=prompts.reconsolidation_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )
    with llm_invocation_scope(
        trace_context=LLMTraceContext(stage="phase6", node="reconsolidation")
    ):
        payload = invoke_structured_output(
            prompts.reconsolidation_system,
            user_prompt,
            output_tool=RECONSOLIDATION_RESULT_TOOL,
            validator=require_mapping_fields("decision", "reason"),
        ).payload
    if not isinstance(payload, dict):
        return {
            "decision": "keep_prior",
            "reason": "",
            "reconsolidation_record": None,
            "later_reaction": None,
            "state_updates": [],
        }

    decision = _clean_text(payload.get("decision")).lower()
    if decision not in {"reconsolidate", "keep_prior"}:
        decision = "keep_prior"

    later_candidate = _normalize_reaction_candidate(payload.get("later_reaction"))
    emitted_at_source_span_id = _clean_text(later_source_ref_payload.get("source_span_id"))
    later_reaction: AnchoredReactionRecord | None = None
    reconsolidation_record: ReconsolidationRecord | None = None
    if decision == "reconsolidate" and later_candidate is not None and emitted_at_source_span_id:
        later_reaction_family = compat_reaction_family(later_candidate)
        new_reaction_id = derive_reaction_id(
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=emitted_at_source_span_id,
            reaction_type=later_reaction_family,
        )
        raw_record = _normalize_reconsolidation_record(
            payload.get("reconsolidation_record"),
            prior_reaction_id=_clean_text(earlier_reaction.get("reaction_id")),
            new_reaction_id=new_reaction_id,
        )
        record_id = (
            _clean_text((raw_record or {}).get("record_id"))
            or derive_reconsolidation_record_id(
                prior_reaction_id=_clean_text(earlier_reaction.get("reaction_id")),
                later_sentence_id=emitted_at_source_span_id,
            )
        )
        later_reaction = build_reaction_record(
            reaction=later_candidate,
            primary_source_ref=later_source_ref_payload,
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=emitted_at_source_span_id,
            reconsolidation_record_id=record_id,
            supersedes_reaction_id=_clean_text(earlier_reaction.get("reaction_id")),
            compatibility_section_ref=_compatibility_section_ref(
                {"primary_source_ref": later_source_ref_payload},
                chapter_id=chapter_id,
            ),
        )
        reconsolidation_record = {
            **(raw_record or {}),
            "record_id": record_id,
            "prior_reaction_id": _clean_text(earlier_reaction.get("reaction_id")),
            "new_reaction_id": _clean_text(later_reaction.get("reaction_id")),
            "change_kind": _clean_text((raw_record or {}).get("change_kind")) or "reframed",
            "what_changed": _clean_text((raw_record or {}).get("what_changed")),
            "rationale": _clean_text((raw_record or {}).get("rationale")),
            "created_at": _timestamp(),
        }
    else:
        decision = "keep_prior"

    return {
        "decision": decision,  # type: ignore[typeddict-item]
        "reason": _clean_text(payload.get("reason")),
        "reconsolidation_record": reconsolidation_record,
        "later_reaction": later_reaction,
        "state_updates": _normalize_state_operations(payload.get("state_updates")),
    }


def apply_reconsolidation(
    reaction_records: ReactionRecordsState,
    reconsolidation_records: ReconsolidationRecordsState,
    result: ReconsolidationResult,
) -> tuple[ReactionRecordsState, ReconsolidationRecordsState]:
    """Persist one normalized reconsolidation result."""

    if str(result.get("decision", "") or "") != "reconsolidate":
        return reaction_records, reconsolidation_records

    later_reaction = result.get("later_reaction")
    reconsolidation_record = result.get("reconsolidation_record")
    if not isinstance(later_reaction, dict) or not isinstance(reconsolidation_record, dict):
        return reaction_records, reconsolidation_records

    return (
        append_reaction_record(reaction_records, later_reaction),
        append_reconsolidation_record(reconsolidation_records, reconsolidation_record),
    )


def _normalize_carry_forward_item(value: object) -> ActiveAttentionItem | None:
    """Normalize one chapter-boundary carry-forward active-attention item."""

    if not isinstance(value, dict):
        return None
    normalized = dict(value)
    if isinstance(value.get("source_refs"), list):
        normalized["source_refs"] = [
            build_reaction_source_ref(item)
            for item in value.get("source_refs", [])
            if isinstance(item, dict)
        ]
    if isinstance(value.get("development_source_refs"), list) or isinstance(value.get("answer_source_refs"), list):
        normalized["development_source_refs"] = [
            build_reaction_source_ref(item)
            for item in [
                *(
                    value.get("development_source_refs", [])
                    if isinstance(value.get("development_source_refs"), list)
                    else []
                ),
                *(
                    value.get("answer_source_refs", [])
                    if isinstance(value.get("answer_source_refs"), list)
                    else []
                ),
            ]
            if isinstance(item, dict)
        ]
    return normalize_active_tension_item(normalized)


def _normalize_chapter_consolidation_result(payload: object) -> ChapterConsolidationResult:
    """Normalize one chapter-consolidation node payload."""

    if not isinstance(payload, dict):
        return {
            "chapter_ref": "",
            "backward_sweep": [],
            "cooling_operations": [],
            "promotion_candidates": [],
            "knowledge_activation_updates": [],
            "cross_chapter_carry_forward": [],
            "chapter_summary_note": "",
            "optional_chapter_reaction": None,
        }

    carry_forward = [
        item
        for item in (_normalize_carry_forward_item(entry) for entry in payload.get("cross_chapter_carry_forward", []))
        if item is not None
    ]
    promotion_candidates = [
        item
        for item in (_normalize_reflective_promotion_candidate(entry) for entry in payload.get("promotion_candidates", []))
        if item is not None
    ]
    return {
        "chapter_ref": _clean_text(payload.get("chapter_ref")),
        "backward_sweep": list(payload.get("backward_sweep", [])) if isinstance(payload.get("backward_sweep"), list) else [],
        "cooling_operations": _normalize_state_operations(payload.get("cooling_operations")),
        "promotion_candidates": promotion_candidates,
        "knowledge_activation_updates": _normalize_state_operations(payload.get("knowledge_activation_updates")),
        "cross_chapter_carry_forward": carry_forward,
        "chapter_summary_note": _clean_text(payload.get("chapter_summary_note")),
        "optional_chapter_reaction": _normalize_reaction_candidate(payload.get("optional_chapter_reaction")),
    }


def chapter_consolidation(
    *,
    chapter_ref: str,
    meaning_units_in_chapter: list[dict[str, object]],
    active_attention_snapshot: ActiveAttention,
    source_refs_in_chapter: list[dict[str, object]],
    reflective_frames_snapshot: ReflectiveFramesState,
    knowledge_activations_snapshot: KnowledgeActivationsState,
    persisted_reactions_in_chapter: list[AnchoredReactionRecord],
    policy_snapshot: ReaderPolicy,
    output_language: str,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
) -> ChapterConsolidationResult:
    """Run the chapter-consolidation node."""

    prompts = ATTENTIONAL_V2_PROMPTS
    structural_frame = _structural_frame(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language=output_language,
    )
    user_prompt = _render_prompt(
        prompts.chapter_consolidation_prompt,
        structural_frame=_json_block(structural_frame),
        chapter_ref=chapter_ref,
        meaning_units_in_chapter=_json_block(meaning_units_in_chapter),
        active_attention_snapshot=_json_block(active_attention_snapshot),
        source_refs_in_chapter=_json_block(source_refs_in_chapter),
        reflective_frames_snapshot=_json_block(reflective_frames_snapshot),
        knowledge_activations_snapshot=_json_block(knowledge_activations_snapshot),
        persisted_reactions_in_chapter=_json_block(persisted_reactions_in_chapter),
        policy_snapshot=_json_block(policy_snapshot),
        output_language_name=language_name(output_language),
    )
    _write_prompt_manifest(
        output_dir,
        node_name="chapter_consolidation",
        prompt_version=prompts.chapter_consolidation_version,
        system_prompt=prompts.chapter_consolidation_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )
    with llm_invocation_scope(
        trace_context=LLMTraceContext(stage="phase6", node="chapter_consolidation")
    ):
        payload = invoke_structured_output(
            prompts.chapter_consolidation_system,
            user_prompt,
            output_tool=CHAPTER_CONSOLIDATION_RESULT_TOOL,
            validator=require_mapping_fields("chapter_ref"),
        ).payload
    normalized = _normalize_chapter_consolidation_result(payload)
    if not normalized.get("chapter_ref"):
        normalized["chapter_ref"] = chapter_ref
    return normalized


def apply_cross_chapter_carry_forward(
    active_attention: ActiveAttention,
    carry_forward: list[ActiveAttentionItem],
) -> ActiveAttention:
    """Replace active-attention items while preserving ActiveTension fields and evidence."""

    active_attention = normalize_active_tension_state(active_attention)
    existing_by_id = {
        _clean_text(item.get("item_id")): item
        for item in active_attention.get("active_items", [])
        if isinstance(item, dict) and _clean_text(item.get("item_id"))
    }
    carried_items: list[ActiveAttentionItem] = []
    for item in carry_forward:
        item_id = _clean_text(item.get("item_id"))
        if not item_id:
            continue
        existing = existing_by_id.get(item_id, {})
        if not existing and not _has_live_question_fields(item):
            continue
        carried_item: ActiveAttentionItem = {
            "item_id": item_id,
            "attention_tags": _merge_unique_texts(existing.get("attention_tags"), item.get("attention_tags")),
            "tension_from": _clean_text(item.get("tension_from")) or _clean_text(existing.get("tension_from")),
            "tension_focus": _clean_text(item.get("tension_focus")) or _clean_text(existing.get("tension_focus")),
            "working_interpretation": _clean_text(item.get("working_interpretation")) or _clean_text(existing.get("working_interpretation")),
            "answered_reason": _clean_text(item.get("answered_reason")) or _clean_text(existing.get("answered_reason")),
            "closed_reason": _clean_text(item.get("closed_reason")) or _clean_text(existing.get("closed_reason")),
            "opened_at_source_span_id": _clean_text(item.get("opened_at_source_span_id")) or _clean_text(existing.get("opened_at_source_span_id")),
            "opened_at_unit_span_id": _clean_text(item.get("opened_at_unit_span_id")) or _clean_text(existing.get("opened_at_unit_span_id")),
            "answered_at_source_span_id": _clean_text(item.get("answered_at_source_span_id")) or _clean_text(existing.get("answered_at_source_span_id")),
            "answered_at_unit_span_id": _clean_text(item.get("answered_at_unit_span_id")) or _clean_text(existing.get("answered_at_unit_span_id")),
            "closed_at_source_span_id": _clean_text(item.get("closed_at_source_span_id")) or _clean_text(existing.get("closed_at_source_span_id")),
            "closed_at_unit_span_id": _clean_text(item.get("closed_at_unit_span_id")) or _clean_text(existing.get("closed_at_unit_span_id")),
            "status": _clean_text(item.get("status")) or _clean_text(existing.get("status")) or "open",
        }
        for field in (
            "opened_at_source_span",
            "opened_at_unit_span",
            "answered_at_source_span",
            "answered_at_unit_span",
            "closed_at_source_span",
            "closed_at_unit_span",
        ):
            raw = item.get(field)
            if not isinstance(raw, dict):
                raw = existing.get(field)
            if isinstance(raw, dict):
                carried_item[field] = dict(raw)  # type: ignore[literal-required]
        carried_item["source_refs"] = dedupe_source_refs(
            [
                *(
                    existing.get("source_refs", [])
                    if isinstance(existing.get("source_refs"), list)
                    else []
                ),
                *(
                    item.get("source_refs", [])
                    if isinstance(item.get("source_refs"), list)
                    else []
                ),
            ]
        )
        carried_item["development_source_refs"] = dedupe_source_refs(
            [
                *(
                    existing.get("development_source_refs", [])
                    if isinstance(existing.get("development_source_refs"), list)
                    else []
                ),
                *(
                    item.get("development_source_refs", [])
                    if isinstance(item.get("development_source_refs"), list)
                    else []
                ),
            ]
        )
        carried_items.append(carried_item)

    return {
        **dict(active_attention),
        "updated_at": _timestamp(),
        "active_items": carried_items,
    }


def run_phase6_chapter_cycle(
    *,
    book_id: str,
    chapter: BookChapter | dict[str, object],
    meaning_units_in_chapter: list[dict[str, object]],
    chapter_end_source_ref: SourceRef | dict[str, object],
    active_attention: ActiveAttention,
    reflective_frames: ReflectiveFramesState,
    knowledge_activations: KnowledgeActivationsState,
    reaction_records: ReactionRecordsState,
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path | None = None,
    persist_compatibility_projection: bool = False,
    book_title: str = "",
    author: str = "",
) -> dict[str, object]:
    """Run one chapter-end slow-cycle pass and return updated Phase 6 state."""

    chapter_ref = _clean_text(chapter.get("reference") or chapter.get("chapter_ref") or f"Chapter {int(chapter.get('id', 0) or 0)}")
    chapter_title = _clean_text(chapter.get("title"))
    persisted_reactions = reaction_records_for_chapter(reaction_records, chapter_ref=chapter_ref)
    source_refs_in_chapter = [
        build_reaction_source_ref(record.get("primary_source_ref"))
        for record in persisted_reactions
        if isinstance(record.get("primary_source_ref"), dict)
    ]
    consolidation = chapter_consolidation(
        chapter_ref=chapter_ref,
        meaning_units_in_chapter=meaning_units_in_chapter,
        active_attention_snapshot=active_attention,
        source_refs_in_chapter=source_refs_in_chapter,
        reflective_frames_snapshot=reflective_frames,
        knowledge_activations_snapshot=knowledge_activations,
        persisted_reactions_in_chapter=persisted_reactions,
        policy_snapshot=reader_policy,
        output_language=output_language,
        output_dir=output_dir,
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
    )

    audit_envelopes: list[SlowCycleAuditEnvelope] = []

    post_cooling_active_attention = apply_active_attention_operations(active_attention, consolidation.get("cooling_operations", []))
    audit_envelopes.extend(
        _carry_forward_audit_envelopes(
            chapter_ref=chapter_ref,
            post_cooling_active_attention=post_cooling_active_attention,
            carry_forward=consolidation.get("cross_chapter_carry_forward", []),
        )
    )
    next_active_attention = post_cooling_active_attention
    next_active_attention = apply_cross_chapter_carry_forward(
        next_active_attention,
        consolidation.get("cross_chapter_carry_forward", []),
    )
    chapter_end_ref = build_reaction_source_ref(chapter_end_source_ref)
    end_source_id = _clean_text(chapter_end_ref.get("source_span_id")) or "chapter-end"
    next_knowledge_activations = apply_activation_operations(
        knowledge_activations,
        consolidation.get("knowledge_activation_updates", []),
        current_source_id=end_source_id,
        reader_policy=reader_policy,
    )
    audit_envelopes.extend(
        _knowledge_update_audit_envelopes(
            chapter_ref=chapter_ref,
            operations=consolidation.get("knowledge_activation_updates", []),
        )
    )

    next_reflective_frames = reflective_frames
    promotion_results: list[ReflectivePromotionResult] = []
    for candidate in consolidation.get("promotion_candidates", []):
        promotion_result = reflective_promotion(
            candidate=candidate,
            current_reflective_state=next_reflective_frames,
            policy_snapshot=reader_policy,
            output_language=output_language,
            chapter_ref=chapter_ref,
            output_dir=output_dir,
            book_title=book_title,
            author=author,
            chapter_title=chapter_title,
        )
        promotion_results.append(promotion_result)
        next_reflective_frames = apply_reflective_promotion(next_reflective_frames, promotion_result)
        audit_envelopes.append(
            _promotion_audit_envelope(
                chapter_ref=chapter_ref,
                candidate=candidate,
                result=promotion_result,
            )
        )

    next_reaction_records = reaction_records
    optional_reaction = consolidation.get("optional_chapter_reaction")
    if isinstance(optional_reaction, dict):
        optional_reaction_record = build_reaction_record(
            reaction=optional_reaction,
            primary_source_ref=chapter_end_ref,
            chapter_id=int(chapter.get("id", 0) or 0),
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=end_source_id,
            compatibility_section_ref=_compatibility_section_ref(
                {"primary_source_ref": chapter_end_ref},
                chapter_id=int(chapter.get("id", 0) or 0),
            ),
            ordinal=len(persisted_reactions) + 1,
        )
        next_reaction_records = append_reaction_record(
            next_reaction_records,
            optional_reaction_record,
        )
        audit_envelopes.append(
            _optional_reaction_audit_envelope(
                chapter_ref=chapter_ref,
                reaction_record=optional_reaction_record,
            )
        )

    compatibility_payload = project_chapter_result_compatibility(
        book_id=book_id,
        chapter=chapter,
        reaction_records=next_reaction_records,
        output_language=output_language,
        output_dir=output_dir,
        persist=persist_compatibility_projection,
    )
    _record_slow_cycle_audit(output_dir, chapter_ref=chapter_ref, envelopes=audit_envelopes)

    return {
        "chapter_consolidation": consolidation,
        "promotion_results": promotion_results,
        "active_attention": next_active_attention,
        "reflective_frames": next_reflective_frames,
        "knowledge_activations": next_knowledge_activations,
        "reaction_records": next_reaction_records,
        "compatibility_payload": compatibility_payload,
    }
