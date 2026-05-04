"""Tests for attentional_v2 book-local source skills."""

from __future__ import annotations

from src.attentional_v2.skills.runtime import execute_skill_request
from src.attentional_v2.skills.source_skills import fetch_source_window


def _sentence(sentence_id: str, text: str, *, index: int, paragraph_index: int = 1) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": index,
        "paragraph_index": paragraph_index,
        "text": text,
        "text_role": "body",
    }


def _book_document() -> dict[str, object]:
    return {
        "metadata": {"book": "Skill Book", "author": "Tester"},
        "chapters": [
            {
                "id": 1,
                "title": "Opening",
                "reference": "Chapter 1",
                "sentences": [
                    _sentence("c1-s1", "Opening setup.", index=1, paragraph_index=1),
                    _sentence("c1-s2", "First consequence.", index=2, paragraph_index=1),
                    _sentence("c1-s3", "Hidden future line.", index=3, paragraph_index=2),
                ],
            },
            {
                "id": 2,
                "title": "Later",
                "reference": "Chapter 2",
                "sentences": [
                    _sentence("c2-s1", "Later question.", index=1, paragraph_index=1),
                ],
            },
        ],
    }


def _lookups(document: dict[str, object]) -> tuple[dict[str, dict[str, object]], dict[int, dict[str, object]]]:
    sentence_lookup: dict[str, dict[str, object]] = {}
    chapter_lookup: dict[int, dict[str, object]] = {}
    for chapter in document["chapters"]:
        chapter_id = int(chapter["id"])
        chapter_lookup[chapter_id] = dict(chapter)
        for index, sentence in enumerate(chapter["sentences"]):
            sentence_lookup[str(sentence["sentence_id"])] = {
                "chapter_id": chapter_id,
                "chapter_ref": chapter["reference"],
                "sentence_index": index,
                "sentence": dict(sentence),
            }
    return sentence_lookup, chapter_lookup


def _mainline_cursor() -> dict[str, object]:
    return {
        "position_kind": "sentence",
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "sentence_id": "c1-s3",
        "sentence_index": 3,
    }


def test_source_window_fetch_refuses_future_text():
    """Source fetching should not read at or beyond the mainline cursor."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result, error = fetch_source_window(
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        start_sentence_id="c1-s2",
        end_sentence_id="c1-s3",
    )

    assert result == {}
    assert error == "range_outside_visible_scope"


def test_execute_skill_request_dispatches_source_window_fetch():
    """The skill runtime should dispatch legal source-window requests."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result = execute_skill_request(
        {
            "skill_name": "source_window_fetch",
            "reason": "Need exact source.",
            "arguments": {
                "start_sentence_id": "c1-s1",
                "end_sentence_id": "c1-s2",
            },
        },
        document=document,  # type: ignore[arg-type]
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        anchor_bank={"anchor_records": [], "anchor_relations": []},
        current_scope={},
    )

    assert result["status"] == "ok"
    assert result["skill_name"] == "source_window_fetch"
    assert result["result"]["start_sentence_id"] == "c1-s1"
    assert result["result"]["end_sentence_id"] == "c1-s2"
    assert result["provenance"]["bounded_by_mainline_cursor"] is True


def test_execute_skill_request_reports_unknown_skill():
    """Unknown skills should return structured errors instead of raising."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result = execute_skill_request(
        {"skill_name": "web_search", "reason": "Not supported.", "arguments": {}},
        document=document,  # type: ignore[arg-type]
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        anchor_bank={"anchor_records": [], "anchor_relations": []},
        current_scope={},
    )

    assert result["status"] == "error"
    assert result["error"] == "unknown_skill"


def test_source_map_overview_returns_visible_chapter_cards():
    """Source map overview should expose only already-read chapter scope cards."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result = execute_skill_request(
        {"skill_name": "source_map_overview", "reason": "Need map.", "arguments": {}},
        document=document,  # type: ignore[arg-type]
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        anchor_bank={"anchor_records": [], "anchor_relations": []},
        current_scope={},
    )

    assert result["status"] == "ok"
    assert result["result"]["scope_kind"] == "chapter_cards"
    assert [card["card_id"] for card in result["result"]["cards"]] == ["chapter:1"]
    assert result["result"]["cards"][0]["end_sentence_id"] == "c1-s2"


def test_source_scope_drilldown_expands_current_scope_card():
    """Scope drilldown should reuse current scope ranges and return finer cards."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result = execute_skill_request(
        {
            "skill_name": "source_scope_drilldown",
            "reason": "Need finer scope.",
            "arguments": {"card_id": "chapter:1"},
        },
        document=document,  # type: ignore[arg-type]
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        anchor_bank={"anchor_records": [], "anchor_relations": []},
        current_scope={
            "scope_kind": "chapter_cards",
            "cards": [
                {
                    "card_id": "chapter:1",
                    "start_sentence_id": "c1-s1",
                    "end_sentence_id": "c1-s2",
                }
            ],
        },
    )

    assert result["status"] == "ok"
    assert result["result"]["scope_kind"] == "paragraph_window_cards"
    assert result["result"]["cards"][0]["start_sentence_id"] == "c1-s1"
    assert result["result"]["cards"][0]["end_sentence_id"] == "c1-s2"


def test_anchor_resolve_returns_source_grounded_context():
    """Anchor resolution should return quote plus bounded source context."""

    document = _book_document()
    sentence_lookup, chapter_lookup = _lookups(document)

    result = execute_skill_request(
        {
            "skill_name": "anchor_resolve",
            "reason": "Resolve the earlier anchor.",
            "arguments": {"anchor_id": "anchor:1"},
        },
        document=document,  # type: ignore[arg-type]
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=_mainline_cursor(),  # type: ignore[arg-type]
        anchor_bank={
            "anchor_records": [
                {
                    "anchor_id": "anchor:1",
                    "sentence_start_id": "c1-s1",
                    "sentence_end_id": "c1-s1",
                    "quote": "Opening setup.",
                    "why_it_mattered": "It sets up the later question.",
                }
            ],
            "anchor_relations": [],
        },
        current_scope={},
    )

    assert result["status"] == "ok"
    assert result["result"]["quote"] == "Opening setup."
    assert result["result"]["source_window"]["sentences"][0]["sentence_id"] == "c1-s1"
