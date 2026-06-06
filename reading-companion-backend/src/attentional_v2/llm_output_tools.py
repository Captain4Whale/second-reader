"""Final-output tool definitions for attentional_v2 LLM calls."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


UNITIZE_BOUNDARY_TYPES = {
    "paragraph_end",
    "intra_paragraph_semantic_close",
    "cross_paragraph_continuation",
    "section_end",
    "budget_cap",
}


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
    "Submit the final Ingest boundary and prior-reading recall result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "end_anchor_text": {"type": "string"},
            "boundary_type": {"type": "string", "enum": sorted(UNITIZE_BOUNDARY_TYPES)},
            "reason": {"type": "string"},
            "memory_recalls": {
                "type": "array",
                "maxItems": 3,
                "items": _object_schema(
                    {
                        "recall_id": {"type": "string"},
                        "recall_text": {"type": "string"},
                        "basis": {"type": "string", "enum": ["selected_source_unit"]},
                    },
                    required=["recall_id", "recall_text"],
                ),
            },
        },
        required=["end_anchor_text", "boundary_type", "memory_recalls"],
    ),
)


DIGEST_RESULT_TOOL = final_output_tool(
    "submit_digest_result",
    "Submit the final Digest reading result. Use this tool exactly once as the final answer.",
    _object_schema(
        {
            "understanding": {"type": "string"},
            "response": {"type": "string"},
            "annotations": {
                "type": "array",
                "items": _object_schema(
                    {
                        "source_quote": {"type": "string"},
                        "content": {"type": "string"},
                        "prior_link": {"type": "object"},
                        "outside_link": {"type": "object"},
                        "search_intent": {"type": "object"},
                    }
                ),
            },
        },
        required=["understanding", "response", "annotations"],
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


def validate_ingest_result(payload: Mapping[str, Any], tool_results: list[dict[str, Any]] | None = None) -> list[str]:
    errors: list[str] = []
    if not str(payload.get("end_anchor_text") or "").strip():
        errors.append("end_anchor_text must be a non-empty exact source quote")
    if str(payload.get("boundary_type") or "").strip() not in UNITIZE_BOUNDARY_TYPES:
        errors.append("boundary_type must be one of the supported Ingest boundary types")
    recalls = payload.get("memory_recalls")
    if not isinstance(recalls, list):
        errors.append("memory_recalls must be an array")
    elif len(recalls) > 3:
        errors.append("memory_recalls must contain no more than three entries")
    elif recalls and not tool_results:
        errors.append("memory_recalls is non-empty but retrieve_unit_memory was not called")
    if isinstance(recalls, list):
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
    annotations = payload.get("annotations")
    if not isinstance(annotations, list):
        errors.append("annotations must be an array")
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
