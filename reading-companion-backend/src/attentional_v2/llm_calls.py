"""LLM calls for the attentional_v2 reading mechanism."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from src.iterator_reader.language import language_name
from src.iterator_reader.llm_utils import LLMTraceContext, ReaderLLMError, invoke_json, llm_invocation_scope

from .prompts import (
    ATTENTIONAL_V2_PROMPTS,
    DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
    render_ingest_prompt_xml,
    render_digest_prompt_xml,
)
from .state_projection import build_digest_prompt_packet
from .schemas import (
    AnchorBankState,
    AnchorMemoryState,
    BridgeCandidate,
    CarryForwardContext,
    KnowledgeActivationsState,
    MemoryUptakeAdmissionEvent,
    IngestBoundaryResult,
    OutsideLink,
    PreviewRange,
    PriorLink,
    ReactionCandidate,
    ReactionType,
    DigestResult,
    SearchIntent,
    StateOperation,
    SurfacedReaction,
    UnitizeBoundaryType,
    UnitizeDecision,
)
from .storage import prompt_manifest_file, save_json


_REACTION_TYPES: set[ReactionType] = {
    "highlight",
    "association",
    "curious",
    "discern",
    "retrospect",
    "silent",
}
_OUTSIDE_LINK_KINDS = {"work", "person", "concept", "history", "analogy", "other"}
_UNITIZE_BOUNDARY_TYPES: set[UnitizeBoundaryType] = {
    "paragraph_end",
    "intra_paragraph_semantic_close",
    "cross_paragraph_continuation",
    "section_end",
    "budget_cap",
}
_STATE_OPERATION_TYPES = {
    "append",
    "update",
    "close",
    "link",
    "create",
    "cool",
    "drop",
    "retain_anchor",
    "link_anchors",
    "promote",
    "supersede",
    "reactivate",
    "resolve",
}
_VISIBLE_INTERNAL_REFERENCE_PATTERNS = (
    re.compile(r"\bc\d+-s\d+(?:-\d+)?(?:-c\d+-s\d+(?:-\d+)?)?\b", re.IGNORECASE),
    re.compile(r"\b(?:anchor|thread|concept|reaction|move|ref|source):[A-Za-z0-9._:@-]+\b", re.IGNORECASE),
)
def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Normalize one free-text value."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def _contains_internal_reference_markup(text: str) -> bool:
    """Return whether one visible string leaks internal runtime handles."""

    cleaned = _clean_text(text)
    if not cleaned:
        return False
    return any(pattern.search(cleaned) for pattern in _VISIBLE_INTERNAL_REFERENCE_PATTERNS)


def _anchor_context(anchor_memory: AnchorMemoryState | AnchorBankState, *, limit: int = 4) -> list[dict[str, object]]:
    """Build a compact anchor context packet."""

    context: list[dict[str, object]] = []
    for anchor in anchor_memory.get("anchor_records", [])[:limit]:
        if not isinstance(anchor, dict):
            continue
        context.append(
            {
                "anchor_id": str(anchor.get("anchor_id", "") or ""),
                "quote": str(anchor.get("quote", "") or ""),
                "anchor_kind": str(anchor.get("anchor_kind", "") or ""),
                "status": str(anchor.get("status", "") or ""),
            }
        )
    return context


def _activation_context(activations: KnowledgeActivationsState, *, limit: int = 4) -> list[dict[str, object]]:
    """Build a compact activation context packet."""

    context: list[dict[str, object]] = []
    for activation in activations.get("activations", [])[:limit]:
        if not isinstance(activation, dict):
            continue
        context.append(
            {
                "activation_id": str(activation.get("activation_id", "") or ""),
                "source_candidate": str(activation.get("source_candidate", "") or ""),
                "reading_warrant": str(activation.get("reading_warrant", "") or ""),
                "status": str(activation.get("status", "") or ""),
            }
        )
    return context


def _find_sentence_for_anchor_quote(
    sentences: list[dict[str, object]],
    *,
    anchor_quote: str,
) -> dict[str, object] | None:
    """Return the first sentence that contains the current local anchor quote."""

    cleaned_anchor = _clean_text(anchor_quote)
    if not cleaned_anchor:
        return None
    for sentence in sentences:
        text = _clean_text(sentence.get("text"))
        if cleaned_anchor and cleaned_anchor in text:
            return sentence
    return None


def _quotes_share_local_focus(left: str, right: str) -> bool:
    """Return whether two compact quotes clearly point at the same local hinge."""

    cleaned_left = _clean_text(left)
    cleaned_right = _clean_text(right)
    if not cleaned_left or not cleaned_right:
        return False
    return cleaned_left in cleaned_right or cleaned_right in cleaned_left


def _write_prompt_manifest(
    output_dir: Path | None,
    *,
    node_name: str,
    prompt_version: str,
    system_prompt: str,
    user_prompt: str,
    promptset_version: str,
    prompt_assembly: dict[str, object] | None = None,
) -> None:
    """Persist one LLM-call prompt manifest when an output directory is available."""

    if output_dir is None:
        return
    save_json(
        prompt_manifest_file(output_dir, node_name),
        {
            "node_name": node_name,
            "prompt_version": prompt_version,
            "promptset_version": promptset_version,
            "generated_at": _timestamp(),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            **({"prompt_assembly": prompt_assembly} if prompt_assembly else {}),
        },
    )


def _json_block(value: object) -> str:
    """Render one stable JSON block for legacy-format non-Digest prompts."""

    return json.dumps(value, ensure_ascii=False, indent=2)


def _render_prompt(template: str, **replacements: str) -> str:
    """Render one prompt template without treating JSON braces as format fields."""

    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def _structural_frame(
    *,
    book_title: str,
    author: str,
    chapter_title: str,
    output_language: str,
) -> dict[str, object]:
    """Build the small shared structural frame used by non-Digest prompt templates."""

    return {
        "book_title": book_title,
        "author": author,
        "chapter_title": chapter_title,
        "output_language": output_language,
    }


def _sentence_id(sentence: dict[str, object]) -> str:
    """Return the normalized sentence id for one sentence-like mapping."""

    return _clean_text(sentence.get("sentence_id"))


def _sentence_paragraph_index(sentence: dict[str, object]) -> int:
    """Return the best-effort paragraph index for one sentence-like mapping."""

    locator = sentence.get("locator")
    if isinstance(locator, dict):
        paragraph_index = int(locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0)
        if paragraph_index > 0:
            return paragraph_index
    return int(sentence.get("paragraph_index", 0) or 0)


def _sentences_by_paragraph(
    sentences: list[dict[str, object]],
) -> list[tuple[int, list[dict[str, object]]]]:
    """Return ordered paragraph buckets for one chapter sentence list."""

    paragraphs: list[tuple[int, list[dict[str, object]]]] = []
    for sentence in sentences:
        paragraph_index = _sentence_paragraph_index(sentence)
        if paragraphs and paragraphs[-1][0] == paragraph_index:
            paragraphs[-1][1].append(sentence)
            continue
        paragraphs.append((paragraph_index, [sentence]))
    return paragraphs


def build_unitize_preview(
    *,
    chapter_sentences: list[dict[str, object]],
    current_sentence_id: str,
) -> tuple[list[dict[str, object]], PreviewRange]:
    """Return the fixed Phase A preview window for unitization.

    Phase A preview is intentionally narrow:
    - current paragraph remainder
    - plus the next paragraph in the same section only

    Since the canonical substrate does not expose stable section ids, "same section"
    is approximated conservatively by refusing to cross into a heading paragraph.
    """

    ordered = [dict(sentence) for sentence in chapter_sentences if isinstance(sentence, dict)]
    if not ordered:
        return [], {"start_sentence_id": "", "end_sentence_id": ""}

    current_index = next(
        (index for index, sentence in enumerate(ordered) if _sentence_id(sentence) == _clean_text(current_sentence_id)),
        -1,
    )
    if current_index < 0:
        return [], {"start_sentence_id": "", "end_sentence_id": ""}

    paragraphs = _sentences_by_paragraph(ordered)
    current_paragraph_position = next(
        (index for index, (_paragraph_index, bucket) in enumerate(paragraphs) if any(_sentence_id(item) == _clean_text(current_sentence_id) for item in bucket)),
        -1,
    )
    if current_paragraph_position < 0:
        return [], {"start_sentence_id": "", "end_sentence_id": ""}

    current_paragraph = paragraphs[current_paragraph_position][1]
    current_offset = next(
        (index for index, sentence in enumerate(current_paragraph) if _sentence_id(sentence) == _clean_text(current_sentence_id)),
        0,
    )
    preview_sentences = [dict(sentence) for sentence in current_paragraph[current_offset:]]

    if current_paragraph_position + 1 < len(paragraphs):
        next_paragraph = paragraphs[current_paragraph_position + 1][1]
        next_is_heading = any(
            _clean_text(sentence.get("text_role")) in {"section_heading", "chapter_heading"}
            for sentence in next_paragraph
        )
        if not next_is_heading:
            preview_sentences.extend(dict(sentence) for sentence in next_paragraph)

    if not preview_sentences:
        preview_sentences = [dict(ordered[current_index])]

    return preview_sentences, {
        "start_sentence_id": _sentence_id(preview_sentences[0]),
        "end_sentence_id": _sentence_id(preview_sentences[-1]),
    }


def _normalize_unitize_boundary_type(value: object) -> UnitizeBoundaryType:
    """Normalize one unitize boundary type with a conservative fallback."""

    normalized = _clean_text(value).lower().replace("-", "_")
    if normalized in _UNITIZE_BOUNDARY_TYPES:
        return normalized  # type: ignore[return-value]
    return "paragraph_end"


_MISSING_TARGET_STORE_WARNING = "missing_target_store_defaulted"
_UNSUPPORTED_TARGET_STORE_WARNING = "unsupported_target_store"
_UNSUPPORTED_OPERATION_STORE_WARNING = "unsupported_operation_for_target_store"
_MEMORY_UPTAKE_TARGET_STORES = {"active_attention", "recent_reading_memory", "concept_registry", "thread_trace"}
_MEMORY_UPTAKE_OPERATION_STORE_POLICY = {
    "recent_reading_memory": {"append"},
    "active_attention": {
        "append",
        "create",
        "update",
        "reactivate",
        "cool",
        "close",
        "resolve",
        "link",
        "link_anchors",
        "drop",
    },
    "concept_registry": {"append", "create", "update", "link", "close", "resolve", "drop", "reactivate"},
    "thread_trace": {"append", "create", "update", "link", "close", "resolve", "drop", "reactivate"},
}


def _memory_uptake_store_policy(
    operation_type: str,
    effective_target_store: str,
) -> tuple[bool, str, list[str]]:
    """Return conservative Digest-path admission policy metadata."""

    if effective_target_store not in _MEMORY_UPTAKE_TARGET_STORES:
        return False, _UNSUPPORTED_TARGET_STORE_WARNING, [_UNSUPPORTED_TARGET_STORE_WARNING]
    if operation_type not in _MEMORY_UPTAKE_OPERATION_STORE_POLICY.get(effective_target_store, set()):
        return True, _UNSUPPORTED_OPERATION_STORE_WARNING, [_UNSUPPORTED_OPERATION_STORE_WARNING]
    return True, "supported", []


def _memory_uptake_admission_event(
    *,
    operation_index: int,
    admission_status: str,
    operation_type_emitted: str = "",
    operation_type_normalized: str = "",
    target_store_emitted: str = "",
    effective_target_store: str = "",
    target_key: str = "",
    item_id: str = "",
    compatibility_warnings: list[str] | None = None,
    drop_reason: str = "",
    target_store_supported: bool | None = None,
    operation_store_policy: str = "",
    policy_warnings: list[str] | None = None,
) -> MemoryUptakeAdmissionEvent:
    """Build compact audit metadata for Digest-output operation admission."""

    event: MemoryUptakeAdmissionEvent = {
        "operation_index": operation_index,
        "admission_status": admission_status,  # type: ignore[typeddict-item]
        "operation_type_emitted": operation_type_emitted,
        "operation_type_normalized": operation_type_normalized,
        "target_store_emitted": target_store_emitted,
        "effective_target_store": effective_target_store,
        "target_key": target_key,
        "item_id": item_id,
        "compatibility_warnings": list(compatibility_warnings or []),
        "drop_reason": drop_reason,
    }
    if target_store_supported is not None:
        event["target_store_supported"] = target_store_supported
    if operation_store_policy:
        event["operation_store_policy"] = operation_store_policy  # type: ignore[typeddict-item]
        event["policy_warnings"] = list(policy_warnings or [])
    return event


def _normalize_state_operations_with_admission(
    value: object,
    *,
    enforce_read_store_policy: bool = False,
) -> tuple[list[StateOperation], list[MemoryUptakeAdmissionEvent]]:
    """Normalize explicit state operations and capture audit-only admission events."""

    operations: list[StateOperation] = []
    admission_events: list[MemoryUptakeAdmissionEvent] = []
    if not isinstance(value, list):
        return operations, admission_events
    for operation_index, item in enumerate(value):
        if not isinstance(item, dict):
            admission_events.append(
                _memory_uptake_admission_event(
                    operation_index=operation_index,
                    admission_status="dropped_malformed_operation",
                    drop_reason="operation_not_object",
                )
            )
            continue
        payload = item.get("payload")
        target_key = _clean_text(item.get("target_key") or item.get("item_id"))
        target_store_emitted = _clean_text(item.get("target_store"))
        effective_target_store = target_store_emitted or "active_attention"
        compatibility_warnings: list[str] = []
        if not target_store_emitted:
            compatibility_warnings.append(_MISSING_TARGET_STORE_WARNING)
        operation_type_emitted = _clean_text(item.get("op") or item.get("operation_type"))
        operation_type = operation_type_emitted.lower().replace("-", "_")
        if not operation_type:
            admission_events.append(
                _memory_uptake_admission_event(
                    operation_index=operation_index,
                    admission_status="dropped_malformed_operation",
                    operation_type_emitted=operation_type_emitted,
                    operation_type_normalized=operation_type,
                    target_store_emitted=target_store_emitted,
                    effective_target_store=effective_target_store,
                    target_key=target_key,
                    item_id=target_key,
                    compatibility_warnings=compatibility_warnings,
                    drop_reason="missing_operation_type",
                )
            )
            continue
        if operation_type not in _STATE_OPERATION_TYPES:
            admission_events.append(
                _memory_uptake_admission_event(
                    operation_index=operation_index,
                    admission_status="dropped_unknown_operation",
                    operation_type_emitted=operation_type_emitted,
                    operation_type_normalized=operation_type,
                    target_store_emitted=target_store_emitted,
                    effective_target_store=effective_target_store,
                    target_key=target_key,
                    item_id=target_key,
                    compatibility_warnings=compatibility_warnings,
                    drop_reason="unknown_operation_type",
                )
            )
            continue
        target_store_supported, operation_store_policy, policy_warnings = _memory_uptake_store_policy(
            operation_type,
            effective_target_store,
        )
        compatibility_warnings.extend(policy_warnings)
        if enforce_read_store_policy and operation_store_policy != "supported":
            drop_status = (
                "dropped_unsupported_target_store"
                if operation_store_policy == _UNSUPPORTED_TARGET_STORE_WARNING
                else "dropped_unsupported_operation_for_target_store"
            )
            admission_events.append(
                _memory_uptake_admission_event(
                    operation_index=operation_index,
                    admission_status=drop_status,
                    operation_type_emitted=operation_type_emitted,
                    operation_type_normalized=operation_type,
                    target_store_emitted=target_store_emitted,
                    effective_target_store=effective_target_store,
                    target_key=target_key,
                    item_id=target_key,
                    compatibility_warnings=compatibility_warnings,
                    drop_reason=operation_store_policy,
                    target_store_supported=target_store_supported,
                    operation_store_policy=operation_store_policy,
                    policy_warnings=policy_warnings,
                )
            )
            continue
        operation: StateOperation = {
            "op": operation_type,  # type: ignore[typeddict-item]
            "operation_type": operation_type,  # type: ignore[typeddict-item]
            "target_store": effective_target_store,
            "target_store_emitted": target_store_emitted,
            "effective_target_store": effective_target_store,
            "target_key": target_key,
            "item_id": target_key,
            "compatibility_warnings": compatibility_warnings,
            "payload": dict(payload) if isinstance(payload, dict) else {},
        }
        if effective_target_store != "recent_reading_memory":
            operation["reason"] = _clean_text(item.get("reason"))
        operations.append(operation)
        admission_events.append(
            _memory_uptake_admission_event(
                operation_index=operation_index,
                admission_status="accepted",
                operation_type_emitted=operation_type_emitted,
                operation_type_normalized=operation_type,
                target_store_emitted=target_store_emitted,
                effective_target_store=effective_target_store,
                target_key=target_key,
                item_id=target_key,
                compatibility_warnings=compatibility_warnings,
                target_store_supported=target_store_supported,
                operation_store_policy=operation_store_policy,
                policy_warnings=policy_warnings,
            )
        )
    return operations, admission_events


def _normalize_state_operations(value: object) -> list[StateOperation]:
    """Normalize a list of explicit state operations."""

    operations, _admission_events = _normalize_state_operations_with_admission(value)
    return operations


def _normalize_bridge_candidate(value: object) -> BridgeCandidate | None:
    """Normalize one optional bridge candidate."""

    if not isinstance(value, dict):
        return None
    target_anchor_id = _clean_text(value.get("target_anchor_id"))
    target_sentence_id = _clean_text(value.get("target_sentence_id"))
    quote = _clean_text(value.get("quote"))
    if not any([target_anchor_id, target_sentence_id, quote]):
        return None
    relation_type = _clean_text(value.get("relation_type")) or "echo"
    raw_score = value.get("score")
    try:
        score = float(raw_score) if raw_score is not None else 0.0
    except (TypeError, ValueError):
        score = 0.0
    return {
        "candidate_kind": _clean_text(value.get("candidate_kind")) or "llm_hint",
        "target_anchor_id": target_anchor_id,
        "target_sentence_id": target_sentence_id,
        "retrieval_channel": _clean_text(value.get("retrieval_channel")) or "llm_hint",
        "relation_type": relation_type,
        "score": score,
        "why_now": _clean_text(value.get("why_now")),
        "quote": quote,
    }


def _normalize_bridge_candidates(value: object) -> list[BridgeCandidate]:
    """Normalize a list of bridge candidates."""

    candidates: list[BridgeCandidate] = []
    if not isinstance(value, list):
        return candidates
    for item in value:
        candidate = _normalize_bridge_candidate(item)
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _normalize_reaction_candidate(value: object) -> ReactionCandidate | None:
    """Normalize one optional anchored reaction payload."""

    if not isinstance(value, dict):
        return None
    reaction_type = _clean_text(value.get("type")).lower()
    if reaction_type not in _REACTION_TYPES:
        return None
    source_quote = _clean_text(value.get("source_quote") or value.get("anchor_quote"))
    content = _clean_text(value.get("content"))
    if reaction_type != "silent" and (not source_quote or not content):
        return None
    related_source_quotes = [
        _clean_text(item)
        for item in value.get("related_source_quotes", value.get("related_anchor_quotes", []))
        if _clean_text(item)
    ] if isinstance(value.get("related_source_quotes", value.get("related_anchor_quotes", [])), list) else []
    search_results = [dict(item) for item in value.get("search_results", []) if isinstance(item, dict)] if isinstance(value.get("search_results"), list) else []
    return {
        "type": reaction_type,  # type: ignore[typeddict-item]
        "source_quote": source_quote,
        "content": content,
        "related_source_quotes": related_source_quotes,
        "search_query": _clean_text(value.get("search_query")),
        "search_results": search_results,
    }


def _normalize_prior_link(
    value: object,
    *,
    allowed_ref_ids: set[str],
) -> PriorLink | None:
    """Normalize one explicit surfaced prior-link packet."""

    if not isinstance(value, dict):
        return None
    ref_ids = [
        ref_id
        for ref_id in (
            _clean_text(item)
            for item in value.get("ref_ids", [])
            if isinstance(value.get("ref_ids"), list)
        )
        if ref_id and (not allowed_ref_ids or ref_id in allowed_ref_ids)
    ]
    relation = _clean_text(value.get("relation"))
    note = _clean_text(value.get("note"))
    if not ref_ids:
        return None
    return {
        "ref_ids": ref_ids[:4],
        "relation": relation,
        "note": note,
    }


def _normalize_outside_link(value: object) -> OutsideLink | None:
    """Normalize one explicit surfaced outside-reference packet."""

    if not isinstance(value, dict):
        return None
    kind = _clean_text(value.get("kind")).lower()
    label = _clean_text(value.get("label"))
    note = _clean_text(value.get("note"))
    if not label:
        return None
    if kind not in _OUTSIDE_LINK_KINDS:
        kind = "other"
    return {
        "kind": kind,
        "label": label,
        "note": note,
    }


def _normalize_search_intent(value: object) -> SearchIntent | None:
    """Normalize one explicit surfaced search-intent packet."""

    if not isinstance(value, dict):
        return None
    query = _clean_text(value.get("query"))
    rationale = _clean_text(value.get("rationale"))
    if not query:
        return None
    return {
        "query": query,
        "rationale": rationale,
    }


def _normalize_surfaced_reaction(
    value: object,
    *,
    current_unit_texts: list[str],
    allowed_ref_ids: set[str],
) -> SurfacedReaction | None:
    """Normalize one surfaced Digest-owned reaction."""

    if not isinstance(value, dict):
        return None
    source_quote = _clean_text(value.get("source_quote") or value.get("anchor_quote"))
    content = _clean_text(value.get("content"))
    if not source_quote or not content:
        return None
    if current_unit_texts and not any(source_quote in text for text in current_unit_texts):
        return None
    if _contains_internal_reference_markup(content):
        return None
    return {
        "source_quote": source_quote,
        "content": content,
        "prior_link": _normalize_prior_link(value.get("prior_link"), allowed_ref_ids=allowed_ref_ids),
        "outside_link": _normalize_outside_link(value.get("outside_link")),
        "search_intent": _normalize_search_intent(value.get("search_intent")),
    }


def _normalize_surfaced_reactions(
    value: object,
    *,
    current_unit_texts: list[str],
    allowed_ref_ids: set[str],
) -> list[SurfacedReaction]:
    """Normalize the surfaced reactions emitted directly by Digest."""

    reactions: list[SurfacedReaction] = []
    if not isinstance(value, list):
        return reactions
    for item in value:
        normalized = _normalize_surfaced_reaction(
            item,
            current_unit_texts=current_unit_texts,
            allowed_ref_ids=allowed_ref_ids,
        )
        if normalized is not None:
            reactions.append(normalized)
    return reactions


def _normalize_ingest_boundary_result(
    value: object,
) -> IngestBoundaryResult:
    """Normalize one Ingest boundary result."""

    if not isinstance(value, dict):
        return {
            "reason": "ingest_empty_source_anchor",
            "end_anchor_text": "",
            "boundary_type": "paragraph_end",
        }
    return {
        "reason": _clean_text(value.get("reason")),
        "end_anchor_text": _clean_text(value.get("end_anchor_text")),
        "boundary_type": _normalize_unitize_boundary_type(value.get("boundary_type")),
    }


def ingest(
    *,
    current_view_position: dict[str, object],
    current_view_content: dict[str, object],
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
) -> IngestBoundaryResult:
    """Run the Ingest LLM boundary call."""

    prompts = ATTENTIONAL_V2_PROMPTS
    prompt_assembly = render_ingest_prompt_xml(
        book_title=book_title,
        author=author,
        current_view_position=current_view_position,
        current_view_content=current_view_content,
    )
    user_prompt = prompt_assembly.rendered_text
    _write_prompt_manifest(
        output_dir,
        node_name="ingest",
        prompt_version=prompts.ingest_version,
        system_prompt=prompts.ingest_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
        prompt_assembly={
            "spec_id": prompt_assembly.spec_id,
            "owner_node": prompt_assembly.owner_node,
            "output_contract": prompt_assembly.output_contract,
            "rendered_blocks": list(prompt_assembly.rendered_blocks),
            "used_fragment_ids": list(prompt_assembly.used_fragment_ids),
            "used_slot_names": list(prompt_assembly.used_slot_names),
        },
    )

    try:
        with llm_invocation_scope(trace_context=LLMTraceContext(stage="phase4", node="ingest")):
            payload = invoke_json(prompts.ingest_system, user_prompt, default={})
        return _normalize_ingest_boundary_result(
            payload,
        )
    except ReaderLLMError:
        return {
            "reason": "ingest_llm_error",
            "end_anchor_text": "",
            "boundary_type": "paragraph_end",
        }


def _route_targets_from_ref_ids(
    supporting_ref_ids: list[str],
) -> tuple[str, str]:
    """Extract one best-effort route target from supporting context refs."""

    target_anchor_id = ""
    target_sentence_id = ""
    for ref_id in supporting_ref_ids:
        cleaned = _clean_text(ref_id)
        if cleaned.startswith("anchor:") and not target_anchor_id:
            target_anchor_id = cleaned.split("anchor:", 1)[1]
        elif cleaned.startswith("source:anchor:") and not target_anchor_id:
            target_anchor_id = cleaned.split("source:anchor:", 1)[1]
        elif cleaned.startswith("source:sentence:") and not target_sentence_id:
            target_sentence_id = cleaned.split("source:sentence:", 1)[1]
        elif cleaned.startswith("sentence:") and not target_sentence_id:
            target_sentence_id = cleaned.split("sentence:", 1)[1]
    return target_anchor_id, target_sentence_id


def _recent_reading_memory_output_to_ops(value: object) -> list[dict[str, object]]:
    """Convert target XML Digest output into current runtime memory ops."""

    if not isinstance(value, list):
        return []
    operations: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        memory_text = _clean_text(item.get("memory_text"))
        if not memory_text:
            continue
        kind = _clean_text(item.get("kind")) or "other"
        operations.append(
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "payload": {
                    "kind": kind,
                    "memory_text": memory_text,
                },
            }
        )
    return operations


def _digest_memory_ops_from_payload(payload: object) -> object:
    """Return runtime memory ops converted from Digest's XML output."""

    if not isinstance(payload, dict):
        return None
    return _recent_reading_memory_output_to_ops(payload.get("recent_reading_memory"))


def digest(
    *,
    carry_forward_context: CarryForwardContext,
    output_language: str,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
) -> DigestResult:
    """Run the Digest LLM call for one accepted source unit."""

    prompts = ATTENTIONAL_V2_PROMPTS
    sentence_unit = [dict(sentence) for sentence in (current_unit_sentences or []) if isinstance(sentence, dict)]
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    if source_unit:
        current_unit_texts = [str(source_unit.get("source_text", "") or "")]
    else:
        current_unit_texts = [
            _clean_text(sentence.get("text"))
            for sentence in sentence_unit
            if _clean_text(sentence.get("text"))
        ]
    prompt_packet = build_digest_prompt_packet(
        carry_forward_context=carry_forward_context,
    )
    assembly_result = render_digest_prompt_xml(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language_name=language_name(output_language),
        recent_reading_memory=prompt_packet.get("recent_reading_memory")
        if isinstance(prompt_packet.get("recent_reading_memory"), dict)
        else None,
        current_unit_source=source_unit,
        current_unit_sentences=sentence_unit,
    )
    system_prompt = DIGEST_XML_TRANSPORT_SYSTEM_PROMPT
    user_prompt = assembly_result.rendered_text
    prompt_assembly_metadata: dict[str, object] = {
        "spec_id": assembly_result.spec_id,
        "owner_node": assembly_result.owner_node,
        "output_contract": assembly_result.output_contract,
        "rendered_blocks": list(assembly_result.rendered_blocks),
        "used_fragment_ids": list(assembly_result.used_fragment_ids),
        "used_slot_names": list(assembly_result.used_slot_names),
    }
    _write_prompt_manifest(
        output_dir,
        node_name="digest",
        prompt_version=prompts.digest_version,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
        prompt_assembly=prompt_assembly_metadata,
    )
    with llm_invocation_scope(trace_context=LLMTraceContext(stage="phase4", node="digest")):
        payload = invoke_json(system_prompt, user_prompt, default={})

    allowed_ref_ids = {
        _clean_text(ref.get("ref_id"))
        for ref in carry_forward_context.get("refs", [])
        if isinstance(ref, dict) and _clean_text(ref.get("ref_id"))
    }

    surfaced_reactions = _normalize_surfaced_reactions(
        payload.get("surfaced_reactions") if isinstance(payload, dict) else None,
        current_unit_texts=current_unit_texts,
        allowed_ref_ids=allowed_ref_ids,
    )
    reading_impression = _clean_text(payload.get("reading_impression")) if isinstance(payload, dict) else ""
    raw_memory_ops = _digest_memory_ops_from_payload(payload)
    memory_uptake_ops, memory_uptake_admission_events = _normalize_state_operations_with_admission(
        raw_memory_ops,
        enforce_read_store_policy=True,
    )
    result: DigestResult = {
        "reading_impression": reading_impression,
        "surfaced_reactions": surfaced_reactions,
        "memory_uptake_ops": memory_uptake_ops,
        "memory_uptake_admission_events": memory_uptake_admission_events,
    }
    return result
