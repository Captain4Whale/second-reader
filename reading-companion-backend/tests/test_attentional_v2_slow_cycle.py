"""Tests for attentional_v2 Phase 6 slow-cycle helpers."""

from __future__ import annotations

import json

from src.attentional_v2 import slow_cycle as slow_cycle_module
from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_concept_registry,
    build_empty_knowledge_activations,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
    build_empty_active_attention,
)
from src.attentional_v2.slow_cycle import (
    apply_reconsolidation,
    build_reaction_record,
    build_reaction_record_from_surfaced_reaction,
    compat_reaction_family,
    compat_search_query,
    project_chapter_result_compatibility,
    reconsolidation,
    run_phase6_chapter_cycle,
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


def test_reflective_item_default_provenance_uses_active_attention_item():
    """Slow-cycle defaults should use the current hot-state term, not old local-hypothesis buckets."""

    item = slow_cycle_module._normalize_reflective_item(
        {"statement": "The opening social frame now feels durable."},
        chapter_ref="Chapter 1",
    )

    assert item is not None
    assert item["promoted_from"] == "active_attention_item"


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


def test_reconsolidation_appends_later_reaction_without_mutating_earlier_one(monkeypatch):
    """Reconsolidation should append a linked later reaction instead of rewriting the earlier reaction."""

    earlier_reaction = build_reaction_record(
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
    )

    monkeypatch.setattr(
        slow_cycle_module,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "decision": "reconsolidate",
            "reason": "The later sentence materially narrows the earlier claim.",
            "reconsolidation_record": {
                "change_kind": "tightened",
                "what_changed": "Value is now framed as narrower than the opening suggested.",
                "rationale": "The later sentence rules out the broader reading.",
            },
            "later_reaction": {
                "type": "discern",
                "source_quote": "Later the author narrows what counts as value.",
                "content": "The later sentence makes the earlier claim narrower than it first appeared.",
                "related_source_quotes": ["Markets begin as relations among people."],
                "search_query": "",
                "search_results": [],
            },
            "state_updates": [],
        },
    )

    result = reconsolidation(
        earlier_reaction=earlier_reaction,
        earlier_anchor_context=[earlier_reaction["primary_source_ref"]],
        later_source_ref=_source_ref("Later the author narrows what counts as value.", 2),
        current_understanding_snapshot={"chapter_frame": "value is being narrowed"},
        policy_snapshot=build_default_reader_policy(),
        output_language="en",
        chapter_id=1,
        chapter_ref="Chapter 1",
    )

    next_reactions, next_reconsolidations = apply_reconsolidation(
        build_empty_reaction_records(),
        {"schema_version": 1, "mechanism_version": "attentional_v2-phase8", "updated_at": "now", "records": []},
        result,
    )

    assert result["decision"] == "reconsolidate"
    assert result["reconsolidation_record"]["prior_reaction_id"] == earlier_reaction["reaction_id"]
    assert result["later_reaction"]["supersedes_reaction_id"] == earlier_reaction["reaction_id"]
    assert earlier_reaction["thought"] == "The opening sentence grounds value in social relation."
    assert next_reactions["records"][0]["reaction_id"] == result["later_reaction"]["reaction_id"]
    assert next_reconsolidations["records"][0]["new_reaction_id"] == result["later_reaction"]["reaction_id"]


def test_run_phase6_chapter_cycle_applies_cooling_promotion_and_optional_reaction(tmp_path, monkeypatch):
    """The Phase 6 chapter cycle should cool pressure, promote reflective meaning, and persist a chapter reaction."""

    output_dir = tmp_path / "output" / "demo-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)

    def fake_invoke_json(system_prompt: str, _prompt: str, default: object) -> object:
        if "chapter-consolidation node" in system_prompt:
            return {
                "chapter_ref": "Chapter 1",
                "backward_sweep": [
                    {
                        "source_ref_id": "src:c1:p1@0-p1@40",
                        "why": "the opening line became the chapter spine",
                    }
                ],
                "cooling_operations": [
                    {
                        "operation_type": "drop",
                        "target_store": "active_attention",
                        "item_id": "h-1",
                        "reason": "local heat ends with the chapter",
                        "payload": {},
                    }
                ],
                "promotion_candidates": [
                    {
                        "candidate_id": "pc-1",
                        "statement": "The chapter frames value as social before narrowing it.",
                        "source_refs": [
                            _source_ref("Markets begin as relations among people.", 1, role="support"),
                            _source_ref("Later the author narrows what counts as value.", 2, role="support"),
                        ],
                        "promoted_from": "chapter_sweep",
                        "target_bucket": "chapter_understandings",
                        "rationale": "It survived the backward sweep and chapter-end check.",
                    }
                ],
                "knowledge_activation_updates": [],
                "cross_chapter_carry_forward": [
                    {
                        "item_id": "q-1",
                        "attention_tags": ["question"],
                        "statement": "How narrow will the later book make value?",
                        "source_refs": [_source_ref("Later the author narrows what counts as value.", 2, role="support")],
                        "status": "open",
                    }
                ],
                "chapter_summary_note": "The chapter narrows its own opening frame.",
                "optional_chapter_reaction": {
                    "type": "retrospect",
                    "source_quote": "Later the author narrows what counts as value.",
                    "content": "By chapter end, the opening social frame has been deliberately narrowed.",
                    "related_source_quotes": ["Markets begin as relations among people."],
                    "search_query": "",
                    "search_results": [],
                },
            }
        if "reflective-promotion node" in system_prompt:
            return {
                "decision": "promote",
                "reason": "The statement is chapter-durable and well supported.",
                "target_bucket": "chapter_understandings",
                "reflective_item": {
                    "item_id": "ru-1",
                    "statement": "The chapter frames value as social before narrowing it.",
                    "source_refs": [
                        _source_ref("Markets begin as relations among people.", 1, role="support"),
                        _source_ref("Later the author narrows what counts as value.", 2, role="support"),
                    ],
                    "confidence_band": "stable",
                    "promoted_from": "chapter_sweep",
                    "status": "active",
                },
                "supersede_bucket": "",
                "supersede_item_id": "",
                "state_operations": [],
                "chapter_ref": "Chapter 1",
            }
        return default

    monkeypatch.setattr(slow_cycle_module, "invoke_json", fake_invoke_json)

    result = run_phase6_chapter_cycle(
        book_id="demo-book",
        chapter=_chapter(),
        meaning_units_in_chapter=[
            {"unit_id": "u-1", "source_span_id": "src:c1:p1@0-p1@40", "summary": "social opening"},
            {"unit_id": "u-2", "source_span_id": "src:c1:p2@0-p2@46", "summary": "narrowing turn"},
        ],
        chapter_end_source_ref=_source_ref("Later the author narrows what counts as value.", 2),
        active_attention={
            **build_empty_active_attention(),
            "active_items": [
                {
                    "item_id": "h-1",
                    "attention_tags": ["interpretation"],
                    "statement": "Value is purely social.",
                    "source_refs": [_source_ref("Markets begin as relations among people.", 1, role="support")],
                    "status": "active",
                }
            ],
        },
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        knowledge_activations=build_empty_knowledge_activations(),
        reaction_records=build_empty_reaction_records(),
        reader_policy=build_default_reader_policy(),
        output_language="en",
        output_dir=output_dir,
        persist_compatibility_projection=True,
        book_title="Demo Book",
        author="Tester",
    )

    chapter_manifest = json.loads(
        (output_dir / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "chapter_consolidation.json").read_text(
            encoding="utf-8"
        )
    )
    promotion_manifest = json.loads(
        (output_dir / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "reflective_promotion.json").read_text(
            encoding="utf-8"
        )
    )

    assert result["chapter_consolidation"]["chapter_summary_note"] == "The chapter narrows its own opening frame."
    assert [item["item_id"] for item in result["active_attention"]["active_items"]] == ["q-1"]
    assert result["active_attention"]["active_items"][0]["attention_tags"] == ["question"]
    assert result["reflective_frames"]["chapter_understandings"][0]["item_id"] == "ru-1"
    assert result["reaction_records"]["records"][0]["type"] == "retrospect"
    assert result["compatibility_payload"]["visible_reaction_count"] == 1
    assert chapter_manifest["prompt_version"] == "attentional_v2.chapter_consolidation.v3"
    assert promotion_manifest["prompt_version"] == "attentional_v2.reflective_promotion.v1"
