"""Final-output tool definitions for attentional_v2 LLM calls."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


def _object_schema(properties: dict[str, Any], *, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
    }


def final_output_tool(name: str, description: str, input_schema: Mapping[str, Any]) -> dict[str, Any]:
    """Build one Anthropic-style final-output tool definition."""

    return {
        "name": name,
        "description": description,
        "input_schema": dict(input_schema),
    }


INGEST_RESULT_TOOL = final_output_tool(
    "submit_ingest_result",
    "Submit the final Ingest unit boundary and preview partition audit map. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "unit": _object_schema(
                {
                    "end_paragraph_n": {"type": ["string", "number"]},
                    "end_at": {"type": "string"},
                },
                required=["end_paragraph_n", "end_at"],
            ),
            "preview_partition": {
                "type": "array",
                "minItems": 1,
                "items": _object_schema(
                    {
                        "title": {"type": "string"},
                        "end_paragraph_n": {"type": ["string", "number"]},
                        "end_at": {"type": "string"},
                        "status": {"type": "string", "enum": ["complete", "open_tail"]},
                    },
                    required=["title", "end_paragraph_n", "end_at", "status"],
                ),
            },
            "reason": {"type": "string"},
        },
        required=["unit", "preview_partition"],
    ),
)


DIGEST_RESULT_TOOL = final_output_tool(
    "submit_digest_result",
    "Submit the final Digest reading result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "understanding": {"type": "string"},
            "response": {"type": "string"},
            "marginalia": {
                "type": "array",
                "items": _object_schema(
                    {
                        "source_quote": {"type": "string"},
                        "content": {"type": ["string", "null"]},
                        "selection_reason": {"type": ["string", "null"]},
                    },
                    required=["source_quote"],
                ),
            },
        },
        required=["understanding", "response", "marginalia"],
    ),
)


BRIDGE_RESOLUTION_RESULT_TOOL = final_output_tool(
    "submit_bridge_resolution_result",
    "Submit the final bridge-resolution result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "decision": {"type": "string", "enum": ["bridge", "decline"]},
            "reason": {"type": "string"},
            "primary_bridge": {"type": "object"},
            "primary_attribution": {"type": "object"},
            "supporting_bridges": {"type": "array", "items": {"type": "object"}},
            "activation_updates": {"type": "array", "items": {"type": "object"}},
            "state_operations": {"type": "array", "items": {"type": "object"}},
            "knowledge_use_mode": {"type": "string"},
            "search_policy_mode": {"type": "string"},
            "search_trigger": {"type": "string"},
            "search_query": {"type": "string"},
        },
        required=["decision", "reason"],
    ),
)


REFLECTIVE_PROMOTION_RESULT_TOOL = final_output_tool(
    "submit_reflective_promotion_result",
    "Submit the final reflective-promotion result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "decision": {"type": "string", "enum": ["promote", "withhold"]},
            "reason": {"type": "string"},
            "target_bucket": {"type": "string"},
            "reflective_item": {"type": "object"},
            "supersede_bucket": {"type": "string"},
            "supersede_item_id": {"type": "string"},
            "state_operations": {"type": "array", "items": {"type": "object"}},
        },
        required=["decision", "reason"],
    ),
)


RECONSOLIDATION_RESULT_TOOL = final_output_tool(
    "submit_reconsolidation_result",
    "Submit the final reconsolidation result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "decision": {"type": "string", "enum": ["reconsolidate", "keep_prior"]},
            "reason": {"type": "string"},
            "reconsolidation_record": {"type": "object"},
            "later_reaction": {"type": "object"},
            "state_updates": {"type": "array", "items": {"type": "object"}},
        },
        required=["decision", "reason"],
    ),
)


CHAPTER_CONSOLIDATION_RESULT_TOOL = final_output_tool(
    "submit_chapter_consolidation_result",
    "Submit the final chapter-consolidation result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "chapter_ref": {"type": "string"},
            "backward_sweep": {"type": "array", "items": {"type": "object"}},
            "cooling_operations": {"type": "array", "items": {"type": "object"}},
            "promotion_candidates": {"type": "array", "items": {"type": "object"}},
            "knowledge_activation_updates": {"type": "array", "items": {"type": "object"}},
            "cross_chapter_carry_forward": {"type": "array", "items": {"type": "object"}},
            "chapter_summary_note": {"type": "string"},
            "optional_chapter_reaction": {"type": "object"},
        },
        required=["chapter_ref"],
    ),
)


SURVEY_CHAPTER_ZONE_RESULT_TOOL = final_output_tool(
    "submit_survey_chapter_zone_result",
    "Submit the final survey chapter-zone classification. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "zone": {"type": "string", "enum": ["main_body", "front_support", "back_support", "auxiliary"]},
            "confidence": {"type": "string"},
            "reason": {"type": "string"},
        },
        required=["zone", "confidence", "reason"],
    ),
)


def _script_counts(text: str) -> tuple[int, int]:
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_count = len(re.findall(r"[A-Za-z]", text))
    return cjk_count, latin_count


def _primary_text_language(texts: list[str]) -> str:
    text = "\n".join(str(item or "") for item in texts)
    cjk_count, latin_count = _script_counts(text)
    if cjk_count >= 20 and cjk_count >= latin_count * 2:
        return "cjk"
    if latin_count >= 40 and latin_count >= cjk_count * 2:
        return "latin"
    return "unknown"


def _recall_language_error(recall_text: str, *, source_language: str, index: int) -> str:
    cjk_count, latin_count = _script_counts(recall_text)
    if source_language == "cjk" and latin_count >= 20 and cjk_count < 4:
        return f"memory_recalls[{index}].recall_text must use the current source text's primary language"
    if source_language == "latin" and cjk_count >= 10 and latin_count < 8:
        return f"memory_recalls[{index}].recall_text must use the current source text's primary language"
    return ""


def validate_ingest_result(
    payload: Mapping[str, Any],
    tool_results: list[dict[str, Any]] | None = None,
    *,
    current_source_texts: list[str] | None = None,
    current_visible_paragraph_ns: list[str] | None = None,
    require_preview_partition: bool = True,
) -> list[str]:
    errors: list[str] = []
    unit = payload.get("unit")
    unit_end_paragraph_n = ""
    unit_end_at = ""
    visible_ns = {str(item or "").strip() for item in current_visible_paragraph_ns or [] if str(item or "").strip()}
    if not isinstance(unit, Mapping):
        errors.append("unit must be an object")
    else:
        unit_end_paragraph_n = str(unit.get("end_paragraph_n") or "").strip()
        unit_end_at = str(unit.get("end_at") or "").strip()
        if not unit_end_paragraph_n:
            errors.append("unit.end_paragraph_n must be non-empty")
        if not unit_end_at:
            errors.append("unit.end_at must be non-empty")
        if visible_ns and unit_end_paragraph_n and unit_end_paragraph_n not in visible_ns:
            errors.append("unit.end_paragraph_n must match a visible Paragraph n")

    preview_partition = payload.get("preview_partition")
    if require_preview_partition and not isinstance(preview_partition, list):
        errors.append("preview_partition must be a non-empty array")
    elif isinstance(preview_partition, list):
        if require_preview_partition and not preview_partition:
            errors.append("preview_partition must be a non-empty array")
        for index, item in enumerate(preview_partition):
            if not isinstance(item, Mapping):
                errors.append(f"preview_partition[{index}] must be an object")
                continue
            title = str(item.get("title") or "").strip()
            end_paragraph_n = str(item.get("end_paragraph_n") or "").strip()
            end_at = str(item.get("end_at") or "").strip()
            status = str(item.get("status") or "").strip()
            if not title:
                errors.append(f"preview_partition[{index}].title must be non-empty")
            if not end_paragraph_n:
                errors.append(f"preview_partition[{index}].end_paragraph_n must be non-empty")
            if not end_at:
                errors.append(f"preview_partition[{index}].end_at must be non-empty")
            if visible_ns and end_paragraph_n and end_paragraph_n not in visible_ns:
                errors.append(f"preview_partition[{index}].end_paragraph_n must match a visible Paragraph n")
            if status not in {"complete", "open_tail"}:
                errors.append(f"preview_partition[{index}].status must be complete or open_tail")
            elif status == "open_tail" and index != len(preview_partition) - 1:
                errors.append("preview_partition open_tail is allowed only on the final partition")
        if preview_partition and isinstance(preview_partition[0], Mapping) and isinstance(unit, Mapping):
            first_end_paragraph_n = str(preview_partition[0].get("end_paragraph_n") or "").strip()
            first_end_at = str(preview_partition[0].get("end_at") or "").strip()
            if unit_end_paragraph_n and unit_end_at and (
                first_end_paragraph_n != unit_end_paragraph_n or first_end_at != unit_end_at
            ):
                errors.append("preview_partition[0] must match unit")

    for tool_result in tool_results or []:
        result = tool_result.get("result") if isinstance(tool_result, Mapping) else None
        if isinstance(result, Mapping) and str(result.get("status") or "").strip() == "contract_violation":
            reason = str(result.get("degradation_reason") or "retrieve_unit_memory tool call contract violation").strip()
            errors.append(reason)
    return errors


def validate_ingest_unit_memory_tool_args(
    payload: Mapping[str, Any],
    *,
    current_source_texts: list[str] | None = None,
    current_visible_paragraph_ns: list[str] | None = None,
) -> list[str]:
    """Validate retrieve_unit_memory action-tool args before runtime retrieval."""

    errors = validate_ingest_result(
        payload,
        tool_results=[],
        current_visible_paragraph_ns=current_visible_paragraph_ns,
        require_preview_partition=False,
    )
    recalls = payload.get("memory_recalls")
    if not isinstance(recalls, list):
        errors.append("memory_recalls must be a non-empty array for retrieve_unit_memory")
        return errors
    if not recalls:
        errors.append("memory_recalls must be a non-empty array for retrieve_unit_memory")
        return errors
    if len(recalls) > 3:
        errors.append("memory_recalls must contain no more than three entries")
    source_language = _primary_text_language(list(current_source_texts or []))
    for index, item in enumerate(recalls):
        if not isinstance(item, Mapping):
            errors.append(f"memory_recalls[{index}] must be an object")
            continue
        if not str(item.get("recall_id") or "").strip():
            errors.append(f"memory_recalls[{index}].recall_id must be non-empty")
        if not str(item.get("recall_text") or "").strip():
            errors.append(f"memory_recalls[{index}].recall_text must be non-empty")
        basis = str(item.get("basis") or "selected_source_unit").strip()
        if basis != "selected_source_unit":
            errors.append(f"memory_recalls[{index}].basis must be selected_source_unit")
        language_error = _recall_language_error(
            str(item.get("recall_text") or ""),
            source_language=source_language,
            index=index,
        )
        if language_error:
            errors.append(language_error)
    return errors


def _is_content_bearing_text(texts: list[str]) -> bool:
    text = "\n".join(str(item or "") for item in texts).strip()
    if not text:
        return False
    return bool(re.search(r"[A-Za-z0-9\u4e00-\u9fff]", text))


def validate_digest_result(payload: Mapping[str, Any], *, current_unit_texts: list[str]) -> list[str]:
    errors: list[str] = []
    understanding = payload.get("understanding")
    if not isinstance(understanding, str):
        errors.append("understanding must be a string")
    marginalia = payload.get("marginalia")
    legacy_annotations = payload.get("annotations")
    marginalia_payload = marginalia if isinstance(marginalia, list) else legacy_annotations
    legacy_audit_reason_by_quote: dict[str, str] = {}
    legacy_marginalia_audit = payload.get("marginalia_audit")
    if isinstance(legacy_marginalia_audit, list):
        for item in legacy_marginalia_audit:
            if not isinstance(item, Mapping):
                continue
            source_quote = str(item.get("source_quote") or "").strip()
            selection_reason = str(item.get("selection_reason") or "").strip()
            if source_quote and selection_reason:
                legacy_audit_reason_by_quote[source_quote] = selection_reason
    if not isinstance(marginalia_payload, list):
        errors.append("marginalia must be an array")
    else:
        for index, item in enumerate(marginalia_payload):
            if not isinstance(item, Mapping):
                errors.append(f"marginalia[{index}] must be an object")
                continue
            source_quote = str(item.get("source_quote") or item.get("anchor_quote") or "").strip()
            if not source_quote:
                errors.append(f"marginalia[{index}].source_quote must be non-empty")
            content = item.get("content")
            if content is not None and not isinstance(content, str):
                errors.append(f"marginalia[{index}].content must be a string or null")
            selection_reason = item.get("selection_reason")
            if selection_reason is not None and not isinstance(selection_reason, str):
                errors.append(f"marginalia[{index}].selection_reason must be a string or null")
            reason_text = str(selection_reason or "").strip()
            if source_quote and not (isinstance(content, str) and content.strip()):
                reason_text = reason_text or legacy_audit_reason_by_quote.get(source_quote, "")
                if not reason_text:
                    errors.append(f"marginalia[{index}].selection_reason must be non-empty for highlight-only")
    response = payload.get("response")
    if not isinstance(response, str):
        errors.append("response must be a string")
    content_required = _is_content_bearing_text(current_unit_texts)
    if content_required:
        if not str(understanding or "").strip():
            errors.append("understanding must be non-empty for content-bearing source text")
        if not str(response or "").strip():
            errors.append("response must be non-empty for content-bearing source text")
    return errors


def require_mapping_fields(*fields: str):
    """Return a small validator requiring top-level fields to exist."""

    def _validator(payload: Mapping[str, Any]) -> list[str]:
        return [f"{field} is required" for field in fields if field not in payload]

    return _validator
