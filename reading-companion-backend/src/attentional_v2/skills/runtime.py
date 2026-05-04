"""Skill runtime for attentional_v2 book-local source skills."""

from __future__ import annotations

import re

from src.reading_core import BookDocument
from src.reading_core.runtime_contracts import SharedRunCursor

from ..schemas import AnchorBankState
from .schemas import SkillRequest, SkillResult
from .source_skills import (
    build_source_map_overview,
    drilldown_source_scope,
    fetch_source_window,
    range_from_skill_arguments,
    resolve_anchor,
    resolve_visible_sentence_range,
)


_KNOWN_SKILLS = {
    "source_map_overview",
    "source_scope_drilldown",
    "source_window_fetch",
    "anchor_resolve",
}


def _clean_text(value: object) -> str:
    """Normalize one free-text value."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def _safe_int(value: object, default: int = 0) -> int:
    """Return one bounded integer argument."""

    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _error_result(skill_name: str, error: str) -> SkillResult:
    """Build one structured skill error."""

    return {
        "skill_name": skill_name,
        "status": "error",
        "result": {},
        "provenance": {
            "source": "book_substrate",
            "bounded_by_mainline_cursor": True,
        },
        "error": error,
    }


def _ok_result(skill_name: str, result: dict[str, object]) -> SkillResult:
    """Build one structured skill success."""

    return {
        "skill_name": skill_name,
        "status": "ok",
        "result": result,
        "provenance": {
            "source": "book_substrate",
            "bounded_by_mainline_cursor": True,
        },
    }


def execute_skill_request(
    skill_request: SkillRequest | dict[str, object],
    *,
    document: BookDocument,
    survey_map: dict[str, object],
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    mainline_cursor: SharedRunCursor,
    anchor_bank: AnchorBankState,
    current_scope: dict[str, object] | None = None,
) -> SkillResult:
    """Execute one bounded Navigate-requested source skill."""

    if not isinstance(skill_request, dict):
        return _error_result("", "skill_request_must_be_object")
    skill_name = _clean_text(skill_request.get("skill_name"))
    if skill_name not in _KNOWN_SKILLS:
        return _error_result(skill_name, "unknown_skill")
    raw_arguments = skill_request.get("arguments")
    arguments = dict(raw_arguments) if isinstance(raw_arguments, dict) else {}

    if skill_name == "source_map_overview":
        return _ok_result(
            skill_name,
            build_source_map_overview(
                document=document,
                survey_map=survey_map,
                mainline_cursor=mainline_cursor,
            ),
        )

    if skill_name == "source_scope_drilldown":
        start_sentence_id, end_sentence_id = range_from_skill_arguments(arguments, current_scope=current_scope)
        if not start_sentence_id or not end_sentence_id:
            return _error_result(skill_name, "range_required")
        chapter, selected_sentences, error = resolve_visible_sentence_range(
            sentence_lookup=sentence_lookup,
            chapter_lookup=chapter_lookup,
            mainline_cursor=mainline_cursor,
            start_sentence_id=start_sentence_id,
            end_sentence_id=end_sentence_id,
        )
        if error or chapter is None:
            return _error_result(skill_name, error or "range_resolution_failed")
        next_scope = drilldown_source_scope(
            current_scope=current_scope or {},
            selected_sentences=selected_sentences,
            chapter=chapter,
        )
        if next_scope is None or not next_scope.get("cards"):
            return _error_result(skill_name, "scope_cannot_drilldown")
        return _ok_result(skill_name, next_scope)

    if skill_name == "source_window_fetch":
        start_sentence_id, end_sentence_id = range_from_skill_arguments(arguments, current_scope=current_scope)
        if not start_sentence_id or not end_sentence_id:
            return _error_result(skill_name, "range_required")
        result, error = fetch_source_window(
            sentence_lookup=sentence_lookup,
            chapter_lookup=chapter_lookup,
            mainline_cursor=mainline_cursor,
            start_sentence_id=start_sentence_id,
            end_sentence_id=end_sentence_id,
            context_before=_safe_int(arguments.get("context_before")),
            context_after=_safe_int(arguments.get("context_after")),
        )
        if error:
            return _error_result(skill_name, error)
        return _ok_result(skill_name, result)

    if skill_name == "anchor_resolve":
        result, error = resolve_anchor(
            anchor_bank=anchor_bank,
            sentence_lookup=sentence_lookup,
            chapter_lookup=chapter_lookup,
            mainline_cursor=mainline_cursor,
            anchor_id=_clean_text(arguments.get("anchor_id")),
            sentence_id=_clean_text(arguments.get("sentence_id")),
            ref_id=_clean_text(arguments.get("ref_id")),
        )
        if error:
            return _error_result(skill_name, error)
        return _ok_result(skill_name, result)

    return _error_result(skill_name, "unhandled_skill")
