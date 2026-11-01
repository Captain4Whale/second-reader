"""Tests for attentional_v2 Phase 6 slow-cycle helpers."""

from __future__ import annotations


from src.attentional_v2.schemas import (
    build_empty_reaction_records,
)
from src.attentional_v2.slow_cycle import (
    build_reaction_record,
    build_reaction_record_from_surfaced_reaction,
    compat_reaction_family,
    compat_search_query,
    project_chapter_result_compatibility,
)
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism


def _chapter() -> dict[str, object]:
    return {
        "id": 1,
        "title": "Opening Frame",
        "reference": "Chapter 1",
        "chapter_heading": {
            "label": "Chapter 1",
            "title": "Opening Frame",
            "subtitle": "",
            "text": "Chapter 1 Opening Frame",
        },
        "paragraphs": [
            {
                "href": "chapter-1.xhtml",
                "start_cfi": "/6/2[chapter1]!/4/2/2",
                "end_cfi": "/6/2[chapter1]!/4/2/10",
                "paragraph_index": 1,
                "text": "Markets begin as relations among people.",
                "text_role": "body",
            },
            {
                "href": "chapter-1.xhtml",
                "start_cfi": "/6/2[chapter1]!/4/4/2",
                "end_cfi": "/6/2[chapter1]!/4/4/12",
                "paragraph_index": 2,
                "text": "Later the author narrows what counts as value.",
                "text_role": "body",
            },
        ],
    }


def _source_ref(quote: str, paragraph_index: int, *, role: str = "primary") -> dict[str, object]:
    return {
        "source_span_id": f"src:c1:p{paragraph_index}@0-p{paragraph_index}@{len(quote)}",
        "source_span": {
            "start_cursor": {
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "paragraph_index": paragraph_index,
                "char_offset": 0,
            },
            "end_cursor": {
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "paragraph_index": paragraph_index,
                "char_offset": len(quote),
            },
        },
        "quote": quote,
        "role": role,
    }








def test_project_chapter_result_compatibility_groups_reactions_by_paragraph(tmp_path):
    """Compatibility projection should preserve original thoughts while filling current chapter-result fields."""

    output_dir = tmp_path / "output" / "demo-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)

    records = build_empty_reaction_records()
    records["records"] = [
        build_reaction_record(
            reaction={
                "type": "highlight",
                "source_quote": "Markets begin as relations among people.",
                "content": "The opening sentence grounds value in social relation.",
                "related_source_quotes": [],
                "search_query": "",
                "search_results": [],
            },
            primary_source_ref=_source_ref("Markets begin as relations among people.", 1),
            chapter_id=1,
            chapter_ref="Chapter 1",
            emitted_at_source_span_id="src:c1:p1@0-p1@40",
        ),
        build_reaction_record(
            reaction={
                "type": "discern",
                "source_quote": "Later the author narrows what counts as value.",
                "content": "The later sentence tightens the frame instead of merely extending it.",
                "related_source_quotes": [],
                "search_query": "",
                "search_results": [],
            },
            primary_source_ref=_source_ref("Later the author narrows what counts as value.", 2),
            chapter_id=1,
            chapter_ref="Chapter 1",
            emitted_at_source_span_id="src:c1:p2@0-p2@46",
        ),
    ]

    payload = project_chapter_result_compatibility(
        book_id="demo-book",
        chapter=_chapter(),
        reaction_records=records,
        output_language="en",
        output_dir=output_dir,
        persist=True,
    )

    compatibility_path = (
        output_dir
        / "_mechanisms"
        / "attentional_v2"
        / "derived"
        / "chapter_result_compatibility"
        / "chapter-001.json"
    )

    assert payload["visible_reaction_count"] == 2
    assert payload["reaction_type_diversity"] == 2
    assert payload["sections"][0]["segment_ref"] == "1.1"
    assert payload["sections"][1]["segment_ref"] == "1.2"
    assert payload["sections"][0]["reactions"][0]["primary_source_ref"]["quote"] == "Markets begin as relations among people."
    assert payload["featured_reactions"][0]["reaction_id"]
    assert payload["featured_reactions"][0]["primary_source_ref"]["source_span_id"] == "src:c1:p1@0-p1@40"
    assert compatibility_path.exists()


def test_build_reaction_record_from_surfaced_reaction_persists_native_surface_fields():
    """Surfaced reactions should persist native surface fields before compat projection."""

    record = build_reaction_record_from_surfaced_reaction(
        reaction={
            "source_quote": "Markets begin as relations among people.",
            "content": "The social framing matters because it sets the book's scale.",
            "prior_link": {
                "ref_ids": ["src:c1:p0@0-p0@12"],
                "relation": "callback",
                "note": "This turns back toward the earlier social claim.",
            },
            "outside_link": None,
            "search_intent": {
                "query": "social marketplace framing",
                "rationale": "Useful follow-up for later comparison.",
            },
        },
        primary_source_ref=_source_ref("Markets begin as relations among people.", 1),
        chapter_id=1,
        chapter_ref="Chapter 1",
        emitted_at_source_span_id="src:c1:p1@0-p1@40",
    )

    assert record is not None
    assert record["record_source"] == "read_surface"
    assert record["thought"] == "The social framing matters because it sets the book's scale."
    assert record["prior_link"]["ref_ids"] == ["src:c1:p0@0-p0@12"]
    assert record["search_intent"]["query"] == "social marketplace framing"
    assert record["compat_family"] == "curious"
    assert compat_reaction_family(record) == "curious"
    assert compat_search_query(record) == "social marketplace framing"




def test_project_chapter_result_compatibility_prefers_native_surface_fields_over_legacy_type():
    """Compatibility projection should derive family labels from native surfaced semantics, not stale legacy type."""

    records = build_empty_reaction_records()
    legacy_shaped = build_reaction_record(
        reaction={
            "type": "highlight",
            "source_quote": "Markets begin as relations among people.",
            "content": "The social framing matters because it sets the book's scale.",
            "related_source_quotes": [],
            "search_query": "",
            "search_results": [],
        },
        primary_source_ref=_source_ref("Markets begin as relations among people.", 1),
        chapter_id=1,
        chapter_ref="Chapter 1",
        emitted_at_source_span_id="src:c1:p1@0-p1@40",
    )
    legacy_shaped["search_intent"] = {
        "query": "social marketplace framing",
        "rationale": "Useful follow-up for later comparison.",
    }
    legacy_shaped["type"] = "highlight"
    records["records"] = [legacy_shaped]

    payload = project_chapter_result_compatibility(
        book_id="demo-book",
        chapter=_chapter(),
        reaction_records=records,
        output_language="en",
    )

    assert payload["featured_reactions"][0]["type"] == "curious"
    assert payload["featured_reactions"][0]["content"] == "The social framing matters because it sets the book's scale."
    assert payload["sections"][0]["reactions"][0]["search_query"] == "social marketplace framing"
