"""Tests for attentional_v2 Phase C.1 state packetization helpers."""

from __future__ import annotations

from src.attentional_v2.schemas import (
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_recent_reading_memory,
    build_empty_reflective_frames,
    build_empty_active_attention,
)
from src.attentional_v2.state_projection import (
    STATE_PACKET_VERSION,
    build_carry_forward_context,
    build_digest_prompt_packet,
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
            "tension_from": "The opener introduces a practical dilemma.",
            "tension_focus": "Why does the chapter turn here?",
            "working_interpretation": "",
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
            "tension_from": "A still-open transition has not fully settled.",
            "tension_focus": "How will the transition resolve?",
            "working_interpretation": "The chapter is starting to answer it.",
            "source_refs": [_source_ref("Cooling sentence.")],
            "status": "cooling",
        }
    ]
    recent_reading_memory = build_empty_recent_reading_memory()
    recent_reading_memory["entries"] = [
        {
            "entry_id": "recent:c1:u0001:m1",
            "source_unit_span_id": "unit:c1:p1@0-p1@15",
            "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
            "status": "active",
            "created_at_unit_index": 1,
            "archived_by_consolidation_id": None,
        },
        {
            "entry_id": "recent:c1:u0000:m1",
            "source_unit_span_id": "unit:c1:p0@0-p0@10",
            "memory_text": "Archived material should not enter Digest.",
            "status": "archived",
            "created_at_unit_index": 0,
            "archived_by_consolidation_id": "consolidation:c1:batch1",
        },
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
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )

    assert packet["packet_version"] == STATE_PACKET_VERSION
    assert packet["active_attention_digest"]["active_items"][0]["item_id"] == "question-1"
    assert packet["active_attention_digest"]["active_items"][0]["attention_tags"] == ["question"]
    assert packet["active_attention_digest"]["active_items"][0]["tension_from"] == (
        "The opener introduces a practical dilemma."
    )
    assert packet["active_attention_digest"]["active_items"][0]["tension_focus"] == "Why does the chapter turn here?"
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
    persisted_reaction = packet["continuation_capsule"]["session_continuity_capsule"]["recent_reactions"][0]
    assert "projection_role" not in persisted_active
    assert "projection_role" not in persisted_reaction


def test_build_digest_prompt_packet_projects_compact_carry_forward_context():
    """The Digest prompt packet should expose compact digests and omit full state baggage."""

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [_sentence("c1-s1", "Alpha sentence.")]
    local_buffer["recent_meaning_units"] = [["c1-s1"]]

    active_attention = build_empty_active_attention()
    active_attention["active_items"] = [
        {
            "item_id": "question-1",
            "attention_tags": ["question"],
            "tension_from": "The opener introduces a practical dilemma.",
            "tension_focus": "Why does the chapter turn here?",
            "working_interpretation": "",
            "source_refs": [_source_ref()],
            "status": "open",
        }
    ]
    recent_reading_memory = build_empty_recent_reading_memory()
    recent_reading_memory["entries"] = [
        {
            "entry_id": "recent:c1:u0001:m1",
            "source_unit_span_id": "unit:c1:p1@0-p1@15",
            "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
            "status": "active",
            "created_at_unit_index": 1,
            "archived_by_consolidation_id": None,
        },
        {
            "entry_id": "recent:c1:u0000:m1",
            "source_unit_span_id": "unit:c1:p0@0-p0@10",
            "memory_text": "Archived material should not enter Digest.",
            "status": "archived",
            "created_at_unit_index": 0,
            "archived_by_consolidation_id": "consolidation:c1:batch1",
        },
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
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )

    prompt_packet = build_digest_prompt_packet(carry_forward_context=carry_forward)

    assert prompt_packet["packet_version"] == STATE_PACKET_VERSION
    assert prompt_packet["active_attention"]["active_tensions"] == [
        {
            "item_id": "question-1",
            "tension_from": "The opener introduces a practical dilemma.",
            "tension_focus": "Why does the chapter turn here?",
            "working_interpretation": "",
        }
    ]
    assert prompt_packet["active_attention"]["open_tension_count"] == 1
    assert prompt_packet["active_attention"]["projection_warning"] == ""
    assert prompt_packet["recent_reading_memory"] == {
        "active_entries": [
            {
                "entry_id": "recent:c1:u0001:m1",
                "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
                "source_unit_span_id": "unit:c1:p1@0-p1@15",
                "created_at_unit_index": 1,
            }
        ],
        "active_entry_count": 1,
    }
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["projection_role"] == "current_support"
    assert "selective_carry" not in prompt_packet
    assert "refs" not in prompt_packet
    assert "anchor_bank_digest" not in prompt_packet
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["projection_role"] == "visible_trace"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["visible_trace_support"] is True
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["current_support"] is False
    assert "knowledge_activations" not in prompt_packet


def test_read_prompt_packet_includes_all_open_questions_without_runtime_fields():
    """Digest prompt context should carry all open ActiveTensions, not the first six digest records."""

    active_items = [
        {
            "item_id": f"question-{index}",
            "tension_from": f"source trigger {index}",
            "tension_focus": f"what lingers with tension {index}",
            "working_interpretation": "",
            "status": "open",
            "source_refs": [_source_ref(f"Question {index}.")],
            "development_source_refs": [_source_ref(f"Answer {index}.")],
            "projection_role": "current_support",
        }
        for index in range(7)
    ]
    active_items.append(
        {
            "item_id": "question-answered",
            "tension_from": "answered source",
            "tension_focus": "answered tension",
            "working_interpretation": "answered",
            "status": "answered",
        }
    )

    prompt_packet = build_digest_prompt_packet(
        carry_forward_context={
            "packet_version": STATE_PACKET_VERSION,
            "active_attention_digest": {"active_items": active_items},
        }
    )

    active_tensions = prompt_packet["active_attention"]["active_tensions"]
    assert len(active_tensions) == 7
    assert [item["item_id"] for item in active_tensions] == [f"question-{index}" for index in range(7)]
    assert "question-answered" not in {item["item_id"] for item in active_tensions}
    assert prompt_packet["active_attention"]["projection_warning"] == "open_active_tension_count_exceeds_soft_limit"
    assert set(active_tensions[0]) == {
        "item_id",
        "tension_from",
        "tension_focus",
        "working_interpretation",
    }
