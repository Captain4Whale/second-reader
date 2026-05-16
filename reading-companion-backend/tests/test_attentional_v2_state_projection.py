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


def _find(items: list[dict[str, object]], key: str, value: str) -> dict[str, object]:
    for item in items:
        if item.get(key) == value:
            return item
    raise AssertionError(f"missing {key}={value}")


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
        },
        {
            "item_id": "question-closed",
            "attention_tags": ["question"],
            "statement": "This earlier question is resolved but still useful as lineage.",
            "source_refs": [_source_ref("Resolved sentence.")],
            "status": "resolved",
        },
        {
            "item_id": "question-cooling",
            "attention_tags": ["question"],
            "statement": "This question is cooling but remains current support.",
            "source_refs": [_source_ref("Cooling sentence.")],
            "status": "cooling",
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
        },
        {
            "concept_key": "z-resolved-promise",
            "concept_type": "motif",
            "summary": "An older promise reading has been resolved.",
            "source_refs": [_source_ref("Resolved promise.")],
            "status": "resolved",
        },
        {
            "concept_key": "unanchored",
            "concept_type": "motif",
            "summary": "This projected concept lacks source refs.",
            "source_refs": [],
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
        },
        {
            "thread_key": "thread:no-source",
            "thread_type": "trace_link",
            "summary": "This thread still lacks source refs and should stay filtered out.",
            "source_refs": [],
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
        },
        {
            "item_id": "frame-missing-source",
            "statement": "This frame is projected but needs source-ref warning.",
            "chapter_ref": "Chapter 1",
            "confidence_band": "working",
            "source_refs": [],
        }
    ]
    reflective_frames["book_level_frames"] = [
        {
            "item_id": "frame-superseded",
            "statement": "This older frame is lineage, not current support.",
            "chapter_ref": "Chapter 1",
            "confidence_band": "working",
            "source_refs": [_source_ref("Superseded frame.")],
            "status": "superseded",
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
    assert packet["active_attention_digest"]["active_items"][0]["projection_role"] == "current_support"
    assert packet["active_attention_digest"]["active_items"][0]["support_status"] == "source_backed"
    assert packet["active_attention_digest"]["active_items"][0]["current_support"] is True
    assert packet["active_attention_digest"]["active_items"][0]["lineage_only"] is False
    assert packet["active_attention_digest"]["active_items"][0]["projection_warning"] == ""
    closed_attention = _find(packet["active_attention_digest"]["active_items"], "item_id", "question-closed")
    assert closed_attention["projection_role"] == "lineage_only"
    assert closed_attention["current_support"] is False
    assert closed_attention["lineage_only"] is True
    assert closed_attention["projection_warning"] == "lineage_only_not_current_support"
    cooling_attention = _find(packet["active_attention_digest"]["active_items"], "item_id", "question-cooling")
    assert cooling_attention["projection_role"] == "current_support"
    assert cooling_attention["current_support"] is True
    assert cooling_attention["lineage_only"] is False
    assert cooling_attention["projection_warning"] == ""
    assert packet["active_attention_digest"]["hot_items"][0]["projection_role"] == "current_support"
    assert packet["chapter_reflective_frame"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert packet["chapter_reflective_frame"]["chapter_frames"][0]["projection_role"] == "current_support"
    missing_frame = _find(packet["chapter_reflective_frame"]["chapter_frames"], "item_id", "frame-missing-source")
    assert missing_frame["support_status"] == "source_ref_missing"
    assert missing_frame["projection_warning"] == "source_ref_missing"
    superseded_frame = packet["chapter_reflective_frame"]["book_frames"][0]
    assert superseded_frame["item_id"] == "frame-superseded"
    assert superseded_frame["projection_role"] == "lineage_only"
    assert superseded_frame["current_support"] is False
    assert superseded_frame["lineage_only"] is True
    assert superseded_frame["projection_warning"] == "lineage_only_not_current_support"
    assert packet["session_continuity_capsule"]["recent_sentence_ids"] == ["c1-s1"]
    assert "recent_routes" not in packet["active_focus_digest"]
    assert packet["concept_digest"][0]["concept_key"] == "promise"
    assert packet["concept_digest"][0]["concept_type"] == "motif"
    assert packet["concept_digest"][0]["projection_role"] == "current_support"
    assert packet["concept_digest"][0]["support_status"] == "source_backed"
    resolved_concept = _find(packet["concept_digest"], "concept_key", "z-resolved-promise")
    assert resolved_concept["projection_role"] == "lineage_only"
    assert resolved_concept["current_support"] is False
    missing_concept = _find(packet["concept_digest"], "concept_key", "unanchored")
    assert missing_concept["support_status"] == "source_ref_missing"
    assert missing_concept["projection_warning"] == "source_ref_missing"
    assert packet["thread_digest"][0]["thread_type"] in {"trace_link", "open_reference"}
    thread = _find(packet["thread_digest"], "thread_key", "thread:promise")
    assert thread["projection_role"] == "current_support"
    assert thread["support_status"] == "source_backed"
    assert all(item["thread_key"] != "thread:no-source" for item in packet["thread_digest"])
    assert any(ref["kind"] == "concept" for ref in packet["refs"])
    assert any(ref["kind"] == "thread" for ref in packet["refs"])

    assert packet["reflective_digest"][0]["item_id"] == "frame-1"
    assert packet["reflective_digest"][0]["projection_role"] == "current_support"
    assert packet["source_ref_digest"][0]["source_span_id"] == "src:c1:p1@0-p1@15"
    assert packet["continuity_digest"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert packet["continuity_digest"]["recent_reactions"][0]["projection_role"] == "visible_trace"
    assert packet["continuity_digest"]["recent_reactions"][0]["visible_trace_support"] is True
    assert packet["continuity_digest"]["recent_reactions"][0]["current_support"] is False
    assert (
        packet["continuity_digest"]["recent_reactions"][0]["projection_warning"]
        == "visible_trace_not_semantic_memory"
    )
    assert packet["active_focus_digest"]["recent_reactions"][0]["projection_role"] == "visible_trace"
    assert packet["refs"]
    assert "knowledge_activations" not in packet

    persisted_active = packet["continuation_capsule"]["active_attention_digest"]["active_items"][0]
    persisted_concept = packet["continuation_capsule"]["concept_digest"][0]
    persisted_reaction = packet["continuation_capsule"]["session_continuity_capsule"]["recent_reactions"][0]
    assert "projection_role" not in persisted_active
    assert "projection_role" not in persisted_concept
    assert "projection_role" not in persisted_reaction


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
    assert prompt_packet["active_attention"]["active_items"][0]["projection_role"] == "current_support"
    assert prompt_packet["concept_digest"][0]["concept_key"] == "promise"
    assert prompt_packet["concept_digest"][0]["support_status"] == "source_backed"
    assert prompt_packet["thread_digest"][0]["thread_key"]
    assert prompt_packet["thread_digest"][0]["projection_role"] == "current_support"
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["projection_role"] == "current_support"
    assert prompt_packet["selective_carry"]["earlier_excerpts"][0]["ref_id"] == "lookback:sentence:c1-s1"
    assert prompt_packet["selective_carry"]["supporting_refs"][0]["ref_id"] == "lookback:sentence:c1-s1"
    assert "refs" not in prompt_packet
    assert "anchor_bank_digest" not in prompt_packet
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["projection_role"] == "visible_trace"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["visible_trace_support"] is True
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["current_support"] is False
    assert "knowledge_activations" not in prompt_packet


def test_build_read_prompt_packet_exposes_retrieval_contract_without_full_active_recall_objects():
    """The prompt packet should expose retrieval contract metadata without full memory objects."""

    carry_forward = build_carry_forward_context(
        chapter_ref="Chapter 1",
        current_unit_sentence_ids=["c1-s2"],
        local_buffer=build_empty_local_buffer(),
        active_attention=build_empty_active_attention(),
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=build_empty_reaction_records(),
    )

    prompt_packet = build_read_prompt_packet(
        carry_forward_context=carry_forward,
        supplemental_context={
            "kind": "active_recall",
            "reason": "Need prior memory.",
            "retrieval_intent": "memory_recovery",
            "result_boundary": "settled_memory_refs_and_visible_trace_refs",
            "result_groups": ["concepts", "threads", "reactions", "refs"],
            "retrieval_events": [
                {
                    "kind": "active_recall",
                    "retrieval_intent": "memory_recovery",
                    "result_boundary": "settled_memory_refs_and_visible_trace_refs",
                    "result_groups": ["concepts", "threads", "reactions", "refs"],
                }
            ],
            "concepts": [{"concept_key": "promise", "summary": "A promise remains active."}],
            "threads": [{"thread_key": "thread:promise", "summary": "The opener keeps returning."}],
            "reactions": [
                {
                    "reaction_id": "reaction-1",
                    "thought": "The first line already carries pressure.",
                    "result_role": "visible_trace",
                    "semantic_memory": False,
                }
            ],
            "refs": [
                {"ref_id": "concept:promise", "kind": "concept", "summary": "A promise remains active."},
                {
                    "ref_id": "reaction:reaction-1",
                    "kind": "reaction",
                    "summary": "The first line already carries pressure.",
                    "result_role": "visible_trace",
                    "semantic_memory": False,
                },
            ],
            "knowledge_activations": [{"activation_id": "knowledge-1"}],
        },
    )

    selective_carry = prompt_packet["selective_carry"]
    assert selective_carry["supporting_refs"][0]["ref_id"] == "concept:promise"
    retrieval_context = selective_carry["retrieval_context"]
    assert retrieval_context["retrieval_intent"] == "memory_recovery"
    assert retrieval_context["result_boundary"] == "settled_memory_refs_and_visible_trace_refs"
    assert retrieval_context["result_groups"] == ["concepts", "threads", "reactions", "refs"]
    assert retrieval_context["retrieval_events"][0]["kind"] == "active_recall"
    assert retrieval_context["forwarded_result_groups"] == ["refs"]
    assert retrieval_context["not_forwarded_result_groups"] == ["concepts", "threads", "reactions"]
    assert retrieval_context["active_recall_full_objects_forwarded"] is False
    assert "concepts" not in selective_carry
    assert "threads" not in selective_carry
    assert "reactions" not in selective_carry
    assert "knowledge_activations" not in selective_carry
    assert "knowledge_activations" not in retrieval_context
    assert "knowledge_activations" not in prompt_packet


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
