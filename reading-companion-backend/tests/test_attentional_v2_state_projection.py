"""Tests for attentional_v2 Phase C.1 state packetization helpers."""

from __future__ import annotations

from src.attentional_v2 import nodes as nodes_module
from src.attentional_v2.nodes import navigate_unitize
from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_anchor_memory,
    build_empty_local_buffer,
    build_empty_move_history,
    build_empty_reaction_records,
    build_empty_reflective_summaries,
    build_empty_trigger_state,
    build_empty_working_pressure,
)
from src.attentional_v2.state_projection import STATE_PACKET_VERSION, build_carry_forward_context, build_navigation_context


def _sentence(sentence_id: str, text: str, *, sentence_index: int = 1) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": sentence_index,
        "paragraph_index": 1,
        "text": text,
        "text_role": "body",
    }


def test_build_carry_forward_context_exposes_phase_c1_packet_shape_and_legacy_aliases():
    """Carry-forward packetization should expose the new packet shape without breaking legacy aliases."""

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [_sentence("c1-s1", "Alpha sentence.")]
    local_buffer["recent_meaning_units"] = [["c1-s1"]]

    working_pressure = build_empty_working_pressure()
    working_pressure["gate_state"] = "watch"
    working_pressure["local_questions"] = [
        {
            "item_id": "question-1",
            "bucket": "local_questions",
            "kind": "question",
            "statement": "Why does the chapter turn here?",
            "support_anchor_ids": [],
            "status": "open",
        }
    ]

    anchor_memory = build_empty_anchor_memory()
    anchor_memory["anchor_records"] = [
        {
            "anchor_id": "a-1",
            "sentence_start_id": "c1-s1",
            "sentence_end_id": "c1-s1",
            "quote": "Alpha sentence.",
            "anchor_kind": "unit_evidence",
            "why_it_mattered": "It established the initial line.",
            "status": "active",
            "locator": {},
            "created_at": "2026-04-12T00:00:00Z",
            "updated_at": "2026-04-12T00:00:00Z",
            "times_referenced": 0,
            "source_passage_id": "",
            "tags": [],
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

    move_history = build_empty_move_history()
    move_history["moves"] = [
        {
            "move_id": "move-1",
            "move_type": "advance",
            "reason": "follow the opening claim",
            "source_sentence_id": "c1-s1",
            "target_anchor_id": "",
            "target_sentence_id": "",
        }
    ]

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

    packet = build_carry_forward_context(
        chapter_ref="Chapter 1",
        current_unit_sentence_ids=["c1-s2"],
        local_buffer=local_buffer,
        working_pressure=working_pressure,
        anchor_memory=anchor_memory,
        reflective_summaries=reflective_summaries,
        move_history=move_history,
        reaction_records=reaction_records,
    )

    assert packet["packet_version"] == STATE_PACKET_VERSION
    assert packet["working_state_digest"]["open_questions"][0]["item_id"] == "question-1"
    assert packet["chapter_reflective_frame"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert packet["anchor_bank_digest"]["active_anchors"][0]["anchor_id"] == "a-1"
    assert packet["session_continuity_capsule"]["recent_sentence_ids"] == ["c1-s1"]
    assert packet["active_focus_digest"]["recent_moves"][0]["move_id"] == "move-1"

    assert packet["working_pressure_digest"]["items"][0]["item_id"] == "question-1"
    assert packet["reflective_digest"][0]["item_id"] == "frame-1"
    assert packet["anchor_digest"][0]["anchor_id"] == "a-1"
    assert packet["continuity_digest"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert packet["refs"]


def test_build_navigation_context_wraps_watch_state_and_state_packet():
    """Navigation packetization should combine watch metadata with the bounded state packet."""

    trigger_state = build_empty_trigger_state()
    trigger_state["current_sentence_id"] = "c1-s2"
    trigger_state["output"] = "monitor"
    trigger_state["gate_state"] = "watch"
    trigger_state["cadence_counter"] = 2
    trigger_state["callback_anchor_ids"] = ["a-1"]
    trigger_state["signals"] = [
        {
            "signal_id": "signal-1",
            "signal_kind": "discourse_turn",
            "family": "salience",
            "sentence_id": "c1-s2",
            "evidence": "However",
            "strength": "medium",
        }
    ]

    packet = build_navigation_context(
        chapter_ref="Chapter 1",
        current_sentence_id="c1-s2",
        local_buffer=build_empty_local_buffer(),
        trigger_state=trigger_state,
        working_pressure=build_empty_working_pressure(),
        anchor_memory=build_empty_anchor_memory(),
        reflective_summaries=build_empty_reflective_summaries(),
        move_history=build_empty_move_history(),
        reaction_records=build_empty_reaction_records(),
    )

    assert packet["packet_version"] == STATE_PACKET_VERSION
    assert packet["watch_state"]["output"] == "monitor"
    assert packet["watch_state"]["callback_anchor_ids"] == ["a-1"]
    assert packet["watch_state"]["signals"][0]["signal_kind"] == "discourse_turn"
    assert "working_state_digest" in packet
    assert "anchor_bank_digest" in packet


def test_navigate_unitize_prompt_receives_navigation_context(monkeypatch):
    """navigate_unitize should render the Phase C.1 navigation packet into its prompt."""

    captured: dict[str, str] = {}

    def fake_invoke_json(_system: str, prompt: str, default: object) -> object:
        captured["prompt"] = prompt
        return default

    monkeypatch.setattr(nodes_module, "invoke_json", fake_invoke_json)

    navigate_unitize(
        current_sentence=_sentence("c1-s1", "Alpha sentence."),
        preview_sentences=[_sentence("c1-s1", "Alpha sentence.")],
        navigation_context={
            "packet_version": STATE_PACKET_VERSION,
            "watch_state": {"output": "monitor", "gate_state": "watch", "signals": []},
            "session_continuity_capsule": {"recent_sentence_ids": ["c1-s0"]},
            "working_state_digest": {"open_questions": []},
            "chapter_reflective_frame": {"chapter_frames": []},
            "active_focus_digest": {"recent_moves": []},
            "anchor_bank_digest": {"active_anchors": []},
            "refs": [],
        },
        reader_policy=build_default_reader_policy(),
        output_language="en",
    )

    assert "Navigation context" in captured["prompt"]
    assert STATE_PACKET_VERSION in captured["prompt"]
    assert "\"output\": \"monitor\"" in captured["prompt"]
