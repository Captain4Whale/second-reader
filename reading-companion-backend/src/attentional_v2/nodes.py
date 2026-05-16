"""Phase 4 interpretive nodes for attentional_v2."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from src.iterator_reader.language import language_name
from src.iterator_reader.llm_utils import LLMTraceContext, ReaderLLMError, invoke_json, llm_invocation_scope

from .prompts import ATTENTIONAL_V2_PROMPTS
from .skills.schemas import SkillRequest
from .state_projection import build_read_prompt_packet
from .schemas import (
    AnchorBankState,
    AnchorMemoryState,
    BridgeCandidate,
    CarryForwardContext,
    DetourNeed,
    KnowledgeActivationsState,
    MemoryUptakeAdmissionEvent,
    NavigationContext,
    NavigateActResult,
    OutsideLink,
    PreviewRange,
    PriorLink,
    ReactionCandidate,
    ReactionType,
    ReadUnitResult,
    ReaderPolicy,
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
_DETOUR_STATUSES = {"open", "resolved", "abandoned"}
_NAVIGATE_ACT_DECISIONS = {"choose_unit", "request_skill", "defer_detour"}
_NAVIGATE_SELECTION_MODES = {"mainline", "detour"}
_LEXICAL_CONTENT_RE = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")
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


def _json_block(value: object) -> str:
    """Render one prompt context block as stable JSON."""

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
    """Build the shared structural frame for node prompts."""

    return {
        "book_title": book_title,
        "author": author,
        "chapter_title": chapter_title,
        "output_language": output_language,
    }


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
) -> None:
    """Persist one node-level prompt manifest when an output directory is available."""

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
        },
    )


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


def _current_paragraph_end_sentence_id(preview_sentences: list[dict[str, object]]) -> str:
    """Return the sentence id at the end of the current paragraph preview slice."""

    if not preview_sentences:
        return ""
    first_paragraph_index = _sentence_paragraph_index(preview_sentences[0])
    current_paragraph = [
        sentence
        for sentence in preview_sentences
        if _sentence_paragraph_index(sentence) == first_paragraph_index
    ]
    if not current_paragraph:
        return _sentence_id(preview_sentences[-1])
    return _sentence_id(current_paragraph[-1])


def _paragraph_sentences_from_preview(
    preview_sentences: list[dict[str, object]],
) -> list[list[dict[str, object]]]:
    """Return ordered paragraph buckets from one preview slice."""

    return [bucket for _paragraph_index, bucket in _sentences_by_paragraph(preview_sentences)]


def _is_heading_paragraph(paragraph_sentences: list[dict[str, object]]) -> bool:
    """Return whether one preview paragraph is entirely heading-like."""

    if not paragraph_sentences:
        return False
    roles = {_clean_text(sentence.get("text_role")) for sentence in paragraph_sentences}
    return bool(roles) and roles.issubset({"chapter_heading", "section_heading"})


def _has_body_sentence(paragraph_sentences: list[dict[str, object]]) -> bool:
    """Return whether one preview paragraph contains body text."""

    return any(_clean_text(sentence.get("text_role")) == "body" for sentence in paragraph_sentences)


def _normalize_unitize_boundary_type(value: object) -> UnitizeBoundaryType:
    """Normalize one unitize boundary type with a conservative fallback."""

    normalized = _clean_text(value).lower().replace("-", "_")
    if normalized in _UNITIZE_BOUNDARY_TYPES:
        return normalized  # type: ignore[return-value]
    return "paragraph_end"


def _is_pure_non_lexical_boundary_residue(sentence: dict[str, object]) -> bool:
    """Return true only for standalone symbol/divider residue with no lexical content."""

    text = _clean_text(sentence.get("text"))
    return bool(text) and _LEXICAL_CONTENT_RE.search(text) is None


def _apply_unitize_guardrail(
    decision: UnitizeDecision,
    *,
    preview_sentences: list[dict[str, object]],
    reader_policy: ReaderPolicy,
) -> UnitizeDecision:
    """Clamp a semantic unitize choice to Phase A's emergency sentence ceiling."""

    if not preview_sentences:
        return decision
    max_sentences = int(reader_policy.get("unitize", {}).get("max_coverage_unit_sentences", 12) or 12)
    if max_sentences <= 0:
        max_sentences = 12

    preview_ids = [_sentence_id(sentence) for sentence in preview_sentences if _sentence_id(sentence)]
    preview_start = preview_ids[0]
    preview_end = preview_ids[-1]
    chosen_start = _clean_text(decision.get("start_sentence_id")) or preview_start
    chosen_end = _clean_text(decision.get("end_sentence_id")) or _current_paragraph_end_sentence_id(preview_sentences) or preview_end
    if chosen_start not in preview_ids:
        chosen_start = preview_start
    if chosen_end not in preview_ids:
        chosen_end = _current_paragraph_end_sentence_id(preview_sentences) or preview_end

    start_index = preview_ids.index(chosen_start)
    end_index = preview_ids.index(chosen_end)
    if start_index > 0 and not all(
        _is_pure_non_lexical_boundary_residue(sentence)
        for sentence in preview_sentences[:start_index]
    ):
        chosen_start = preview_start
        start_index = 0
    if end_index < start_index:
        chosen_start = preview_start
        start_index = 0

    if end_index - start_index + 1 > max_sentences:
        bounded_end = preview_sentences[start_index + max_sentences - 1]
        bounded_ids = preview_ids[start_index : start_index + max_sentences]
        return {
            **decision,
            "start_sentence_id": chosen_start,
            "end_sentence_id": _sentence_id(bounded_end),
            "preview_range": {
                "start_sentence_id": preview_start,
                "end_sentence_id": preview_end,
            },
            "boundary_type": "budget_cap",
            "evidence_sentence_ids": bounded_ids,
            "continuation_pressure": True,
            "reason": _clean_text(decision.get("reason")) or "unitize_budget_cap",
        }

    evidence_sentence_ids = [
        sentence_id
        for sentence_id in decision.get("evidence_sentence_ids", [])
        if sentence_id in preview_ids[start_index : end_index + 1]
    ]
    if not evidence_sentence_ids or evidence_sentence_ids[0] != chosen_start:
        evidence_sentence_ids = preview_ids[start_index : end_index + 1]
    return {
        **decision,
        "start_sentence_id": chosen_start,
        "end_sentence_id": chosen_end,
        "preview_range": {
            "start_sentence_id": preview_start,
            "end_sentence_id": preview_end,
        },
        "boundary_type": _normalize_unitize_boundary_type(decision.get("boundary_type")),
        "evidence_sentence_ids": evidence_sentence_ids,
        "continuation_pressure": bool(decision.get("continuation_pressure")),
        "reason": _clean_text(decision.get("reason")),
    }


def _fallback_unitize_decision(preview_sentences: list[dict[str, object]]) -> UnitizeDecision:
    """Return a deterministic paragraph-bounded fallback decision."""

    if not preview_sentences:
        return {
            "start_sentence_id": "",
            "end_sentence_id": "",
            "preview_range": {"start_sentence_id": "", "end_sentence_id": ""},
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [],
            "reason": "unitize_fallback_empty_preview",
            "continuation_pressure": False,
        }
    paragraph_end_sentence_id = _current_paragraph_end_sentence_id(preview_sentences) or _sentence_id(preview_sentences[-1])
    preview_ids = [_sentence_id(sentence) for sentence in preview_sentences if _sentence_id(sentence)]
    fallback_reason = "unitize_fallback_current_paragraph"

    preview_paragraphs = _paragraph_sentences_from_preview(preview_sentences)
    if len(preview_paragraphs) >= 2:
        first_paragraph = preview_paragraphs[0]
        second_paragraph = preview_paragraphs[1]
        if _is_heading_paragraph(first_paragraph) and _has_body_sentence(second_paragraph):
            paragraph_end_sentence_id = _sentence_id(second_paragraph[-1]) or paragraph_end_sentence_id
            fallback_reason = "unitize_fallback_heading_with_body"

    end_index = preview_ids.index(paragraph_end_sentence_id) if paragraph_end_sentence_id in preview_ids else len(preview_ids) - 1
    return {
        "start_sentence_id": _sentence_id(preview_sentences[0]),
        "end_sentence_id": paragraph_end_sentence_id,
        "preview_range": {
            "start_sentence_id": _sentence_id(preview_sentences[0]),
            "end_sentence_id": _sentence_id(preview_sentences[-1]),
        },
        "boundary_type": "paragraph_end",
        "evidence_sentence_ids": preview_ids[: end_index + 1],
        "reason": fallback_reason,
        "continuation_pressure": False,
    }


_MISSING_TARGET_STORE_WARNING = "missing_target_store_defaulted"


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
) -> MemoryUptakeAdmissionEvent:
    """Build compact audit metadata for read-output operation admission."""

    return {
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


def _normalize_state_operations_with_admission(
    value: object,
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
        operations.append(
            {
                "op": operation_type,  # type: ignore[typeddict-item]
                "operation_type": operation_type,  # type: ignore[typeddict-item]
                "target_store": effective_target_store,
                "target_store_emitted": target_store_emitted,
                "effective_target_store": effective_target_store,
                "target_key": target_key,
                "item_id": target_key,
                "reason": _clean_text(item.get("reason")),
                "compatibility_warnings": compatibility_warnings,
                "payload": dict(payload) if isinstance(payload, dict) else {},
            }
        )
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
    """Normalize one surfaced read-owned reaction."""

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
    """Normalize the surfaced reactions emitted directly by the read step."""

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


def _normalize_detour_need(value: object) -> DetourNeed | None:
    """Normalize one optional detour-need request."""

    if not isinstance(value, dict):
        return None
    reason = _clean_text(value.get("reason"))
    target_hint = _clean_text(value.get("target_hint"))
    status = _clean_text(value.get("status")).lower().replace("-", "_")
    if status not in _DETOUR_STATUSES:
        status = "open"
    if not any((reason, target_hint)):
        return None
    result: DetourNeed = {
        "reason": reason,
        "target_hint": target_hint,
        "status": status,  # type: ignore[typeddict-item]
    }
    return result


def _normalize_skill_request(value: object) -> SkillRequest | None:
    """Normalize one bounded Navigate-requested skill packet."""

    if not isinstance(value, dict):
        return None
    arguments = value.get("arguments")
    skill_request: SkillRequest = {
        "skill_name": _clean_text(value.get("skill_name")),
        "reason": _clean_text(value.get("reason")),
        "arguments": dict(arguments) if isinstance(arguments, dict) else {},
    }
    if not _clean_text(skill_request.get("skill_name")):
        return None
    return skill_request


def _unitize_decision_from_navigate_act(
    value: object,
    *,
    preview_sentences: list[dict[str, object]],
    reader_policy: ReaderPolicy,
    fallback_reason: str,
) -> UnitizeDecision:
    """Normalize a Navigate choose-unit act into the existing unitize decision shape."""

    fallback = _fallback_unitize_decision(preview_sentences)
    if not isinstance(value, dict):
        return fallback
    start_sentence_id = _clean_text(value.get("start_sentence_id"))
    end_sentence_id = _clean_text(value.get("end_sentence_id"))
    if not start_sentence_id or not end_sentence_id:
        return fallback
    raw_evidence = value.get("evidence_sentence_ids")
    evidence_sentence_ids = [
        _clean_text(item)
        for item in raw_evidence
        if _clean_text(item)
    ] if isinstance(raw_evidence, list) else []
    decision: UnitizeDecision = {
        "start_sentence_id": start_sentence_id,
        "end_sentence_id": end_sentence_id,
        "preview_range": {
            "start_sentence_id": _sentence_id(preview_sentences[0]) if preview_sentences else "",
            "end_sentence_id": _sentence_id(preview_sentences[-1]) if preview_sentences else "",
        },
        "boundary_type": _normalize_unitize_boundary_type(value.get("boundary_type")),
        "evidence_sentence_ids": evidence_sentence_ids,
        "reason": _clean_text(value.get("reason")) or fallback_reason,
        "continuation_pressure": bool(value.get("continuation_pressure")),
    }
    return _apply_unitize_guardrail(
        {
            **fallback,
            **decision,
        },
        preview_sentences=preview_sentences,
        reader_policy=reader_policy,
    )


def _normalize_navigate_act_result(
    value: object,
    *,
    allowed_sentence_ids: set[str],
    available_sentences: list[dict[str, object]],
    reader_policy: ReaderPolicy,
    default_selection_mode: str,
    skills_allowed: bool,
) -> NavigateActResult:
    """Normalize one Navigate.choose_next_unit act result against the current visible space."""

    if default_selection_mode == "mainline":
        if not isinstance(value, dict):
            if available_sentences:
                decision = _unitize_decision_from_navigate_act(
                    {},
                    preview_sentences=available_sentences,
                    reader_policy=reader_policy,
                    fallback_reason="navigate_choose_next_unit_llm_empty_fallback",
                )
                return {
                    "decision": "choose_unit",
                    "selection_mode": "mainline",
                    **decision,
                }
            return {
                "decision": "choose_unit",
                "selection_mode": "mainline",
                "reason": "navigate_choose_next_unit_empty_source_anchor",
                "end_anchor_text": "",
                "boundary_type": "paragraph_end",
                "continuation_pressure": False,
            }
        decision = _clean_text(value.get("decision")).lower().replace("-", "_")
        if decision not in _NAVIGATE_ACT_DECISIONS or decision != "choose_unit":
            decision = "choose_unit"
        if (
            available_sentences
            and _clean_text(value.get("start_sentence_id"))
            and _clean_text(value.get("end_sentence_id"))
        ):
            unitize_decision = _unitize_decision_from_navigate_act(
                value,
                preview_sentences=available_sentences,
                reader_policy=reader_policy,
                fallback_reason="navigate_choose_next_unit_sentence_compat_fallback",
            )
            return {
                "decision": "choose_unit",
                "selection_mode": "mainline",
                **unitize_decision,
            }
        return {
            "decision": "choose_unit",
            "selection_mode": "mainline",
            "reason": _clean_text(value.get("reason")),
            "end_anchor_text": _clean_text(
                value.get("end_anchor_text")
                or value.get("end_after_text")
                or value.get("unit_text_tail")
            ),
            "boundary_type": _normalize_unitize_boundary_type(value.get("boundary_type")),
            "continuation_pressure": bool(value.get("continuation_pressure")),
        }

    if not isinstance(value, dict):
        return {
            "decision": "defer_detour",
            "selection_mode": "detour",
            "reason": "navigate_choose_next_unit_empty_result",
        }

    decision = _clean_text(value.get("decision")).lower().replace("-", "_")
    if decision not in _NAVIGATE_ACT_DECISIONS:
        decision = "choose_unit" if default_selection_mode == "mainline" else "defer_detour"

    selection_mode = _clean_text(value.get("selection_mode")).lower().replace("-", "_") or default_selection_mode
    if selection_mode not in _NAVIGATE_SELECTION_MODES:
        selection_mode = default_selection_mode
    if default_selection_mode == "mainline":
        selection_mode = "mainline"

    if decision == "request_skill":
        if not skills_allowed:
            decision = "defer_detour"
        else:
            skill_request = _normalize_skill_request(value.get("skill_request"))
            if skill_request is None:
                return {
                    "decision": "defer_detour",
                    "selection_mode": "detour",
                    "reason": "skill_request_missing_skill_name",
                }
            return {
                "decision": "request_skill",
                "selection_mode": "detour",
                "reason": _clean_text(value.get("reason")) or _clean_text(skill_request.get("reason")),
                "skill_request": dict(skill_request),
            }

    if decision == "defer_detour":
        return {
            "decision": "defer_detour",
            "selection_mode": "detour",
            "reason": _clean_text(value.get("reason")),
        }

    raw_start_sentence_id = _clean_text(value.get("start_sentence_id"))
    raw_end_sentence_id = _clean_text(value.get("end_sentence_id"))
    if default_selection_mode == "detour" and (
        not raw_start_sentence_id
        or not raw_end_sentence_id
        or raw_start_sentence_id not in allowed_sentence_ids
        or raw_end_sentence_id not in allowed_sentence_ids
    ):
        return {
            "decision": "defer_detour",
            "selection_mode": "detour",
            "reason": "chosen_unit_outside_allowed_source_evidence",
        }

    unitize_decision = _unitize_decision_from_navigate_act(
        value,
        preview_sentences=available_sentences,
        reader_policy=reader_policy,
        fallback_reason="navigate_choose_next_unit_choose_unit_fallback",
    )
    start_sentence_id = _clean_text(unitize_decision.get("start_sentence_id"))
    end_sentence_id = _clean_text(unitize_decision.get("end_sentence_id"))
    if not allowed_sentence_ids or start_sentence_id not in allowed_sentence_ids or end_sentence_id not in allowed_sentence_ids:
        return {
            "decision": "defer_detour",
            "selection_mode": "detour",
            "reason": "chosen_unit_outside_allowed_source_evidence",
        }
    return {
        "decision": "choose_unit",
        "selection_mode": selection_mode,  # type: ignore[typeddict-item]
        **unitize_decision,
    }


def _fallback_read_unit_result(
    *,
    current_unit_sentences: list[dict[str, object]],
    continuation_pressure: bool = False,
    reason: str = "",
) -> ReadUnitResult:
    """Return one conservative fallback read result."""

    return {
        "reading_impression": _clean_text(reason),
        "surfaced_reactions": [],
        "memory_uptake_ops": [],
        "detour_need": None,
    }


def navigate_choose_next_unit_act(
    *,
    reading_position: dict[str, object],
    mainline_preview: dict[str, object],
    active_detour_need: DetourNeed | None,
    mainline_cursor: dict[str, object],
    navigation_context: NavigationContext | dict[str, object] | None = None,
    source_evidence: dict[str, object] | None = None,
    skill_catalog: list[dict[str, object]] | None = None,
    skill_results_so_far: list[dict[str, object]] | None = None,
    budget_state: dict[str, object] | None = None,
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
    available_sentences: list[dict[str, object]] | None = None,
    allowed_sentence_ids: set[str] | None = None,
    default_selection_mode: str = "mainline",
    skills_allowed: bool = False,
) -> NavigateActResult:
    """Run one unified Navigate.choose_next_unit agent act."""

    prompts = ATTENTIONAL_V2_PROMPTS
    structural_frame = _structural_frame(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language=output_language,
    )
    available = [dict(sentence) for sentence in available_sentences or [] if isinstance(sentence, dict)]
    allowed_ids = set(allowed_sentence_ids or {_sentence_id(sentence) for sentence in available if _sentence_id(sentence)})
    user_prompt = _render_prompt(
        prompts.navigate_choose_next_unit_prompt,
        structural_frame=_json_block(structural_frame),
        reading_position=_json_block(reading_position),
        mainline_preview=_json_block(mainline_preview),
        active_detour_need=_json_block(dict(active_detour_need or {})),
        mainline_cursor=_json_block(dict(mainline_cursor or {})),
        navigation_context=_json_block(dict(navigation_context or {})),
        source_evidence=_json_block(dict(source_evidence or {})),
        skill_catalog=_json_block(skill_catalog or []),
        skill_results_so_far=_json_block(skill_results_so_far or []),
        budget_state=_json_block(dict(budget_state or {})),
        policy_snapshot=_json_block(reader_policy),
        output_language_name=language_name(output_language),
    )
    _write_prompt_manifest(
        output_dir,
        node_name="navigate_choose_next_unit",
        prompt_version=prompts.navigate_choose_next_unit_version,
        system_prompt=prompts.navigate_choose_next_unit_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )

    try:
        with llm_invocation_scope(trace_context=LLMTraceContext(stage="phase4", node="navigate_choose_next_unit")):
            payload = invoke_json(prompts.navigate_choose_next_unit_system, user_prompt, default={})
        return _normalize_navigate_act_result(
            payload,
            allowed_sentence_ids=allowed_ids,
            available_sentences=available,
            reader_policy=reader_policy,
            default_selection_mode=default_selection_mode,
            skills_allowed=skills_allowed,
        )
    except ReaderLLMError:
        if default_selection_mode == "mainline":
            if available:
                fallback = _unitize_decision_from_navigate_act(
                    {},
                    preview_sentences=available,
                    reader_policy=reader_policy,
                    fallback_reason="navigate_choose_next_unit_llm_error_fallback",
                )
                return {
                    "decision": "choose_unit",
                    "selection_mode": "mainline",
                    **fallback,
                }
            return {
                "decision": "choose_unit",
                "selection_mode": "mainline",
                "reason": "navigate_choose_next_unit_llm_error",
                "end_anchor_text": "",
                "boundary_type": "paragraph_end",
                "continuation_pressure": False,
            }
        return {
            "decision": "defer_detour",
            "selection_mode": "detour",
            "reason": "navigate_choose_next_unit_llm_error",
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
        elif cleaned.startswith("lookback:anchor:") and not target_anchor_id:
            target_anchor_id = cleaned.split("lookback:anchor:", 1)[1]
        elif cleaned.startswith("lookback:sentence:") and not target_sentence_id:
            target_sentence_id = cleaned.split("lookback:sentence:", 1)[1]
        elif cleaned.startswith("sentence:") and not target_sentence_id:
            target_sentence_id = cleaned.split("sentence:", 1)[1]
    return target_anchor_id, target_sentence_id


def read_unit(
    *,
    carry_forward_context: CarryForwardContext,
    reader_policy: ReaderPolicy,
    output_language: str,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
    supplemental_context: dict[str, object] | None = None,
    detour_context: dict[str, object] | None = None,
    output_dir: Path | None = None,
    book_title: str = "",
    author: str = "",
    chapter_title: str = "",
) -> ReadUnitResult:
    """Run the authoritative formal read for one chosen unit."""

    prompts = ATTENTIONAL_V2_PROMPTS
    sentence_unit = [dict(sentence) for sentence in (current_unit_sentences or []) if isinstance(sentence, dict)]
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    if source_unit:
        current_unit_payload: object = {
            "source_span": dict(source_unit.get("source_span", {}))
            if isinstance(source_unit.get("source_span"), dict)
            else {},
            "source_text": str(source_unit.get("source_text", "") or ""),
            "paragraph_slices": [
                {
                    "paragraph_index": item.get("paragraph_index"),
                    "text_role": _clean_text(item.get("text_role")),
                    "start_char": item.get("start_char"),
                    "end_char": item.get("end_char"),
                    "text": str(item.get("text", "") or ""),
                }
                for item in source_unit.get("paragraph_slices", [])
                if isinstance(item, dict)
            ],
        }
        current_unit_texts = [str(source_unit.get("source_text", "") or "")]
    else:
        current_unit_payload = [
            {
                "sentence_id": _clean_text(sentence.get("sentence_id")),
                "text": _clean_text(sentence.get("text")),
                "text_role": _clean_text(sentence.get("text_role")),
            }
            for sentence in sentence_unit
        ]
        current_unit_texts = [
            _clean_text(sentence.get("text"))
            for sentence in sentence_unit
            if _clean_text(sentence.get("text"))
        ]
    prompt_packet = build_read_prompt_packet(
        carry_forward_context=carry_forward_context,
        supplemental_context=supplemental_context,
        detour_context=detour_context,
    )
    structural_frame = _structural_frame(
        book_title=book_title,
        author=author,
        chapter_title=chapter_title,
        output_language=output_language,
    )
    user_prompt = _render_prompt(
        prompts.read_unit_prompt,
        structural_frame=_json_block(structural_frame),
        current_unit=_json_block(current_unit_payload),
        carry_forward_context=_json_block(prompt_packet),
        supplemental_context=_json_block(dict(prompt_packet.get("selective_carry", {}))),
        policy_snapshot=_json_block(reader_policy),
        output_language_name=language_name(output_language),
    )
    _write_prompt_manifest(
        output_dir,
        node_name="read_unit",
        prompt_version=prompts.read_unit_version,
        system_prompt=prompts.read_unit_system,
        user_prompt=user_prompt,
        promptset_version=prompts.promptset_version,
    )
    with llm_invocation_scope(trace_context=LLMTraceContext(stage="phase4", node="read_unit")):
        payload = invoke_json(prompts.read_unit_system, user_prompt, default={})

    allowed_ref_ids = {
        _clean_text(ref.get("ref_id"))
        for ref in carry_forward_context.get("refs", [])
        if isinstance(ref, dict) and _clean_text(ref.get("ref_id"))
    }
    if isinstance(supplemental_context, dict):
        allowed_ref_ids.update(
            _clean_text(ref.get("ref_id"))
            for ref in supplemental_context.get("refs", [])
            if isinstance(ref, dict) and _clean_text(ref.get("ref_id"))
        )
        allowed_ref_ids.update(
            _clean_text(excerpt.get("ref_id"))
            for excerpt in supplemental_context.get("excerpts", [])
            if isinstance(excerpt, dict) and _clean_text(excerpt.get("ref_id"))
        )

    surfaced_reactions = _normalize_surfaced_reactions(
        payload.get("surfaced_reactions") if isinstance(payload, dict) else None,
        current_unit_texts=current_unit_texts,
        allowed_ref_ids=allowed_ref_ids,
    )
    reading_impression = _clean_text(payload.get("reading_impression")) if isinstance(payload, dict) else ""
    memory_uptake_ops, memory_uptake_admission_events = _normalize_state_operations_with_admission(
        payload.get("memory_uptake_ops") if isinstance(payload, dict) else None
    )
    result: ReadUnitResult = {
        "reading_impression": reading_impression,
        "surfaced_reactions": surfaced_reactions,
        "memory_uptake_ops": memory_uptake_ops,
        "memory_uptake_admission_events": memory_uptake_admission_events,
        "detour_need": _normalize_detour_need(payload.get("detour_need")) if isinstance(payload, dict) else None,
    }
    return result
