"""Tests for attentional_v2 Digest-contract helpers."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from src.attentional_v2 import llm_calls as llm_calls_module
from src.attentional_v2 import runner as runner_module
from src.attentional_v2.llm_calls import digest
from src.attentional_v2.schemas import (
    build_empty_knowledge_activations,
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_recent_reading_memory,
    build_empty_reflective_summaries,
    build_empty_active_attention,
)
from src.attentional_v2.state_projection import build_carry_forward_context
from src.attentional_v2.state_migration import migrate_reflective_summaries_to_frames
from src.attentional_v2.storage import read_audit_file
from src.iterator_reader.llm_utils import ReaderLLMError
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Demo Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Alpha sentence. Beta sentence.",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Alpha sentence.",
                        "text_role": "body",
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Beta sentence.",
                        "text_role": "body",
                    },
                ],
            }
        ],
    }


def test_digest_projects_compact_packet_and_returns_f1_surface_contract(tmp_path, monkeypatch):
    """Digest should render XML context and return the live Digest fields."""

    output_dir = tmp_path / "output" / "demo-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)
    captured: dict[str, str] = {}

    def fake_structured_output(_system: str, prompt: str, **_kwargs) -> object:
        captured["prompt"] = prompt
        return SimpleNamespace(payload={
            "response": "The second sentence sharpens the first one.",
            "marginalia": [
                {
                    "source_quote": "Beta sentence.",
                    "content": "This is where the move becomes visible.",
                    "prior_link": {
                        "ref_ids": ["anchor:a-1", "source:sentence:c1-s1"],
                        "relation": "callback",
                        "note": "The earlier anchor clarifies the shift.",
                    },
                }
            ],
            "understanding": "The second sentence sharpens the first one.",
        })

    monkeypatch.setattr(llm_calls_module, "invoke_structured_output", fake_structured_output)

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [
        {
            "sentence_id": "c1-s1",
            "sentence_index": 1,
            "paragraph_index": 1,
            "text": "Alpha sentence.",
            "text_role": "body",
        }
    ]
    local_buffer["recent_meaning_units"] = [["c1-s1"]]

    active_attention = build_empty_active_attention()
    active_attention["active_items"] = [
        {
            "item_id": "question-1",
            "attention_tags": ["question"],
            "tension_from": "Alpha sentence creates a turn.",
            "tension_focus": "Why the chapter turns here remains alive in attention.",
            "working_interpretation": "",
            "support_anchor_ids": [],
            "status": "open",
        }
    ]

    reflective_summaries = build_empty_reflective_summaries()
    reflective_summaries["chapter_understandings"] = [
        {
            "item_id": "frame-1",
            "statement": "The chapter is opening a practical dilemma.",
            "chapter_ref": "Chapter 1",
            "confidence_band": "working",
            "support_anchor_ids": ["a-1"],
        }
    ]
    reflective_frames = migrate_reflective_summaries_to_frames(reflective_summaries)

    reaction_records = build_empty_reaction_records()
    reaction_records["records"] = [
        {
            "reaction_id": "reaction-1",
            "type": "highlight",
            "thought": "The first line already carries pressure.",
            "emitted_at_sentence_id": "c1-s1",
        "primary_anchor": {"anchor_id": "a-1", "quote": "Alpha sentence."},
        }
    ]

    carry_forward = build_carry_forward_context(
        chapter_ref="Chapter 1",
        current_unit_sentence_ids=["c1-s2"],
        local_buffer=local_buffer,
        active_attention=active_attention,
        reflective_frames=reflective_frames,
        reflective_summaries=reflective_summaries,
        reaction_records=reaction_records,
    )

    result = digest(
        current_unit_sentences=[
            {
                "sentence_id": "c1-s2",
                "sentence_index": 2,
                "paragraph_index": 1,
                "text": "Beta sentence.",
                "text_role": "body",
            }
        ],
        carry_forward_context=carry_forward,
        output_language="en",
        output_dir=output_dir,
        book_title="Demo Book",
        author="Tester",
        chapter_title="Chapter 1",
    )

    manifest = json.loads(
        (output_dir / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "digest.json").read_text(
            encoding="utf-8"
        )
    )

    assert "<ReaderRole>" in captured["prompt"]
    assert "<Instruction>" in captured["prompt"]
    assert "<ReadingMemory>" in captured["prompt"]
    assert "<ReadingState>" not in captured["prompt"]
    assert "The previous unit" not in captured["prompt"]
    assert "Alpha sentence." not in captured["prompt"]
    assert "\"active_tensions\"" not in captured["prompt"]
    assert "\"earlier_excerpts\"" not in captured["prompt"]
    assert "\"refs\": [" not in captured["prompt"]
    assert manifest["node_name"] == "digest"
    assert manifest["prompt_version"] == "attentional_v2.digest.v24"
    assert result["understanding"] == "The second sentence sharpens the first one."
    assert result["reading_impression"] == "The second sentence sharpens the first one."
    assert result["surfaced_reactions"][0]["source_quote"] == "Beta sentence."
    assert "prior_link" not in result["surfaced_reactions"][0]
    assert result["memory_uptake_ops"][0]["target_store"] == "recent_reading_memory"


def test_run_digest_for_source_unit_reads_once_without_accepting_unit_audit(tmp_path, monkeypatch):
    """Digest alone is an attempt; Product admission owns accepted-read audit."""

    output_dir = tmp_path / "output" / "demo-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)
    book_document = _book_document()
    chapter = book_document["chapters"][0]
    reflective_frames = migrate_reflective_summaries_to_frames(build_empty_reflective_summaries())
    calls: list[dict[str, object]] = []

    def fake_digest(**kwargs):
        calls.append(
            {
                "unit_sentence_ids": [sentence["sentence_id"] for sentence in kwargs["current_unit_sentences"]],
            }
        )
        return {
            "understanding": "The unit becomes legible immediately.",
            "reading_impression": "The unit becomes legible immediately.",
            "surfaced_reactions": [
                {
                    "source_quote": "Beta sentence.",
                    "content": "The bridge is clear without a second pass.",
                }
            ],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "recent_reading_memory",
                    "payload": {
                        "kind": "event_or_situation",
                        "memory_text": "The Beta sentence makes the bridge legible.",
                    },
                }
            ],
        }

    monkeypatch.setattr(runner_module, "_call_digest", fake_digest)

    digest_result, llm_fallbacks = runner_module._run_digest_for_source_unit(
        chapter=chapter,
        chosen_unit_sentences=[chapter["sentences"][1]],
        unitize_decision={
            "start_sentence_id": "c1-s2",
            "end_sentence_id": "c1-s2",
            "preview_range": {"start_sentence_id": "c1-s2", "end_sentence_id": "c1-s2"},
            "evidence_sentence_ids": ["c1-s2"],
            "reason": "phase-f1-test",
        },
        local_buffer=build_empty_local_buffer(),
        continuation_capsule={},
        active_attention=build_empty_active_attention(),
        recent_reading_memory=build_empty_recent_reading_memory(),
        reflective_frames=reflective_frames,
        knowledge_activations=build_empty_knowledge_activations(),
        reaction_records=build_empty_reaction_records(),
        output_language="en",
        output_dir=output_dir,
        book_title="Demo Book",
        author="Tester",
        chapter_id=1,
        chapter_ref="Chapter 1",
    )

    assert llm_fallbacks == []
    assert len(calls) == 1
    assert digest_result["understanding"] == "The unit becomes legible immediately."
    assert digest_result["surfaced_reactions"][0]["source_quote"] == "Beta sentence."
    assert digest_result["memory_uptake_ops"][0]["op"] == "append"
    assert not read_audit_file(output_dir).exists()


def test_run_digest_for_source_unit_propagates_llm_error_without_empty_audit(tmp_path, monkeypatch):
    """Digest failures should reach unit recovery instead of settling empty reads."""

    output_dir = tmp_path / "output" / "demo-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)
    book_document = _book_document()
    chapter = book_document["chapters"][0]
    reflective_frames = migrate_reflective_summaries_to_frames(build_empty_reflective_summaries())

    def fake_digest(**_kwargs):
        raise ReaderLLMError("Connection error.", problem_code="network_blocked")

    monkeypatch.setattr(runner_module, "_call_digest", fake_digest)

    with pytest.raises(ReaderLLMError) as exc_info:
        runner_module._run_digest_for_source_unit(
            chapter=chapter,
            chosen_unit_sentences=[chapter["sentences"][1]],
            unitize_decision={
                "start_sentence_id": "c1-s2",
                "end_sentence_id": "c1-s2",
                "preview_range": {"start_sentence_id": "c1-s2", "end_sentence_id": "c1-s2"},
                "evidence_sentence_ids": ["c1-s2"],
                "reason": "phase-f1-test",
            },
            local_buffer=build_empty_local_buffer(),
            continuation_capsule={},
            active_attention=build_empty_active_attention(),
            recent_reading_memory=build_empty_recent_reading_memory(),
            reflective_frames=reflective_frames,
            knowledge_activations=build_empty_knowledge_activations(),
            reaction_records=build_empty_reaction_records(),
            output_language="en",
            output_dir=output_dir,
            book_title="Demo Book",
            author="Tester",
            chapter_id=1,
            chapter_ref="Chapter 1",
        )

    assert exc_info.value.problem_code == "network_blocked"
    assert not read_audit_file(output_dir).exists()
