"""Tests for attentional_v2 Phase C.1 state packetization helpers."""

from __future__ import annotations

from src.attentional_v2 import nodes as nodes_module
from src.attentional_v2.nodes import navigate_choose_next_unit_act
from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_concept_registry,
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
    build_empty_active_attention,
)
from src.attentional_v2.state_projection import (
    STATE_PACKET_VERSION,
    build_carry_forward_context,
    build_navigation_context,
    build_read_prompt_packet,
)


def _sentence(sentence_id: str, text: str, *, sentence_index: int = 1) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": sentence_index,
        "paragraph_index": 1,
        "text": text,
        "text_role": "body",
    }


def _source_ref(quote: str = "Alpha sentence.") -> dict[str, object]:
    return {
        "source_span_id": "src:c1:p1@0-p1@15",
        "source_span": {
            "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
            "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 15},
        },
        "quote": quote,
        "role": "support",
    }


def test_build_carry_forward_context_exposes_phase_c1_packet_shape():
    """Carry-forward packetization should expose bounded current state layers."""

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [_sentence("c1-s1", "Alpha sentence.")]
    local_buffer["recent_meaning_units"] = [["c1-s1"]]

    active_attention = build_empty_active_attention()
    active_attention["active_items"] = [
        {
            "item_id": "question-1",
            "attention_tags": ["question"],
            "statement": "Why does the chapter turn here?",
            "source_refs": [_source_ref()],
            "status": "open",
        }
    ]

    concept_registry = build_empty_concept_registry()
    concept_registry["entries"] = [
        {
            "concept_key": "promise",
            "concept_type": "motif",
            "summary": "A promise is still hanging open.",
            "source_refs": [_source_ref()],
            "status": "active",
        }
    ]
    thread_trace = build_empty_thread_trace()
    thread_trace["entries"] = [
        {
            "thread_key": "thread:promise",
            "thread_type": "open_reference",
            "summary": "The later promise turns back toward the opener.",
            "source_refs": [_source_ref()],
            "status": "active",
        }
    ]

    reflective_frames = build_empty_reflective_frames()
    reflective_frames["chapter_understandings"] = [
        {
            "item_id": "frame-1",
            "statement": "The chapter is opening a practical dilemma.",
            "chapter_ref": "Chapter 1",
            "confidence_band": "working",
            "source_refs": [_source_ref()],
        }
    ]

    reaction_records = build_empty_reaction_records()
    reaction_records["records"] = [
        {
            "reaction_id": "reaction-1",
            "type": "highlight",
            "thought": "The first line already carries pressure.",
            "emitted_at_source_span_id": "src:c1:p1@0-p1@15",
            "source_quote": "Alpha sentence.",
            "primary_source_ref": _source_ref(),
        }
    ]

    packet = build_carry_forward_context(
        chapter_ref="Chapter 1",
        current_unit_sentence_ids=["c1-s2"],
        local_buffer=local_buffer,
        active_attention=active_attention,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )

    assert packet["packet_version"] == STATE_PACKET_VERSION
    assert packet["active_attention_digest"]["active_items"][0]["item_id"] == "question-1"
    assert packet["active_attention_digest"]["active_items"][0]["attention_tags"] == ["question"]
    assert packet["chapter_reflective_frame"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert packet["session_continuity_capsule"]["recent_sentence_ids"] == ["c1-s1"]
    assert "recent_routes" not in packet["active_focus_digest"]
    assert packet["concept_digest"][0]["concept_key"] == "promise"
    assert packet["concept_digest"][0]["concept_type"] == "motif"
    assert packet["thread_digest"][0]["thread_type"] in {"trace_link", "open_reference"}
    assert any(ref["kind"] == "concept" for ref in packet["refs"])
    assert any(ref["kind"] == "thread" for ref in packet["refs"])

    assert packet["reflective_digest"][0]["item_id"] == "frame-1"
    assert packet["source_ref_digest"][0]["source_span_id"] == "src:c1:p1@0-p1@15"
    assert packet["continuity_digest"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert packet["refs"]


def test_build_navigation_context_exposes_state_packet_without_watch_metadata():
    """Navigation packetization should stay bounded without reviving watch-state heuristics."""

    packet = build_navigation_context(
        chapter_ref="Chapter 1",
        current_sentence_id="c1-s2",
        local_buffer=build_empty_local_buffer(),
        active_attention=build_empty_active_attention(),
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=build_empty_reaction_records(),
    )

    assert packet["packet_version"] == STATE_PACKET_VERSION
    assert "active_attention_digest" in packet
    assert "concept_digest" in packet
    assert "thread_digest" in packet
    assert "source_ref_digest" in packet
    assert "anchor_bank_digest" not in packet
    assert "watch_state" not in packet


def test_build_read_prompt_packet_projects_compact_always_carry_and_selective_carry():
    """The read prompt packet should expose compact digests and omit full state baggage."""

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [_sentence("c1-s1", "Alpha sentence.")]
    local_buffer["recent_meaning_units"] = [["c1-s1"]]

    active_attention = build_empty_active_attention()
    active_attention["active_items"] = [
        {
            "item_id": "question-1",
            "attention_tags": ["question"],
            "statement": "Why does the chapter turn here?",
            "source_refs": [_source_ref()],
            "status": "open",
        }
    ]

    concept_registry = build_empty_concept_registry()
    concept_registry["entries"] = [
        {
            "concept_key": "promise",
            "concept_type": "motif",
            "summary": "A promise remains active.",
            "source_refs": [_source_ref()],
            "status": "active",
        }
    ]
    thread_trace = build_empty_thread_trace()
    thread_trace["entries"] = [
        {
            "thread_key": "thread:promise",
            "thread_type": "trace_link",
            "summary": "The opener keeps returning.",
            "source_refs": [_source_ref()],
            "status": "active",
        }
    ]

    reflective_frames = build_empty_reflective_frames()
    reflective_frames["chapter_understandings"] = [
        {
            "item_id": "frame-1",
            "statement": "The chapter is opening a practical dilemma.",
            "chapter_ref": "Chapter 1",
            "confidence_band": "working",
            "source_refs": [_source_ref()],
        }
    ]

    reaction_records = build_empty_reaction_records()
    reaction_records["records"] = [
        {
            "reaction_id": "reaction-1",
            "type": "highlight",
            "thought": "The first line already carries pressure.",
            "emitted_at_source_span_id": "src:c1:p1@0-p1@15",
            "source_quote": "Alpha sentence.",
            "primary_source_ref": _source_ref(),
        }
    ]

    carry_forward = build_carry_forward_context(
        chapter_ref="Chapter 1",
        current_unit_sentence_ids=["c1-s2"],
        local_buffer=local_buffer,
        active_attention=active_attention,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )

    prompt_packet = build_read_prompt_packet(
        carry_forward_context=carry_forward,
        supplemental_context={
            "refs": [
                {
                    "ref_id": "lookback:sentence:c1-s1",
                    "kind": "look_back_excerpt",
                    "item_id": "c1-s1",
                    "summary": "Alpha sentence.",
                    "sentence_id": "c1-s1",
                }
            ],
            "excerpts": [
                {
                    "ref_id": "lookback:sentence:c1-s1",
                    "source_kind": "sentence",
                    "sentence_ids": ["c1-s1"],
                    "chapter_ref": "Chapter 1",
                    "excerpt_text": "Alpha sentence.",
                }
            ],
        },
    )

    assert prompt_packet["packet_version"] == STATE_PACKET_VERSION
    assert prompt_packet["active_attention"]["active_items"][0]["item_id"] == "question-1"
    assert prompt_packet["concept_digest"][0]["concept_key"] == "promise"
    assert prompt_packet["thread_digest"][0]["thread_key"]
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert prompt_packet["selective_carry"]["earlier_excerpts"][0]["ref_id"] == "lookback:sentence:c1-s1"
    assert prompt_packet["selective_carry"]["supporting_refs"][0]["ref_id"] == "lookback:sentence:c1-s1"
    assert "refs" not in prompt_packet
    assert "anchor_bank_digest" not in prompt_packet
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["reaction_id"] == "reaction-1"


def test_navigate_choose_next_unit_prompt_receives_navigation_context(monkeypatch):
    """Navigate.choose_next_unit should render the navigation packet into its prompt."""

    captured: dict[str, str] = {}

    def fake_invoke_json(_system: str, prompt: str, default: object) -> object:
        captured["prompt"] = prompt
        return default

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    navigate_choose_next_unit_act(
        reading_position={"mode": "mainline", "current_sentence_id": "c1-s1"},
        mainline_preview={
            "current_sentence": _sentence("c1-s1", "Alpha sentence."),
            "preview_range": {"start_sentence_id": "c1-s1", "end_sentence_id": "c1-s1"},
            "preview_sentences": [_sentence("c1-s1", "Alpha sentence.")],
        },
        active_detour_need=None,
        mainline_cursor={},
        navigation_context={
            "packet_version": STATE_PACKET_VERSION,
            "continuation_capsule": {"chapter_ref": "Chapter 1"},
            "session_continuity_capsule": {"recent_sentence_ids": ["c1-s0"]},
            "active_attention_digest": {"active_items": []},
            "chapter_reflective_frame": {"chapter_frames": []},
            "active_focus_digest": {"recent_reactions": []},
            "concept_digest": [{"concept_key": "promise"}],
            "thread_digest": [{"thread_key": "trace:a-1"}],
            "source_ref_digest": [],
            "refs": [],
        },
        source_evidence={},
        skill_catalog=[],
        skill_results_so_far=[],
        budget_state={"skills_allowed": False},
        reader_policy=build_default_reader_policy(),
        output_language="en",
        available_sentences=[_sentence("c1-s1", "Alpha sentence.")],
        allowed_sentence_ids={"c1-s1"},
        default_selection_mode="mainline",
        skills_allowed=False,
    )

    assert "Navigation context" in captured["prompt"]
    assert STATE_PACKET_VERSION in captured["prompt"]
    assert "\"continuation_capsule\"" in captured["prompt"]
    assert "\"concept_key\": \"promise\"" in captured["prompt"]
