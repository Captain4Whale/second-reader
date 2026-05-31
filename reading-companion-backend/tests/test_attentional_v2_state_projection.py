"""Tests for attentional_v2 Phase C.1 state packetization helpers."""

from __future__ import annotations

from src.attentional_v2.schemas import (
    build_empty_concept_registry,
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_recent_reading_memory,
    build_empty_reflective_frames,
    build_empty_thread_trace,
    build_empty_active_attention,
)
from src.attentional_v2.state_projection import (
    STATE_PACKET_VERSION,
    build_carry_forward_context,
    build_read_prompt_packet,
    build_supplemental_selective_carry,
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
            "kind": "event_or_situation",
            "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
            "status": "active",
            "created_at_unit_index": 1,
            "archived_by_consolidation_id": None,
        },
        {
            "entry_id": "recent:c1:u0000:m1",
            "source_unit_span_id": "unit:c1:p0@0-p0@10",
            "kind": "background",
            "memory_text": "Archived material should not enter Read.",
            "status": "archived",
            "created_at_unit_index": 0,
            "archived_by_consolidation_id": "consolidation:c1:batch1",
        },
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
        recent_reading_memory=recent_reading_memory,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
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
            "kind": "event_or_situation",
            "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
            "status": "active",
            "created_at_unit_index": 1,
            "archived_by_consolidation_id": None,
        },
        {
            "entry_id": "recent:c1:u0000:m1",
            "source_unit_span_id": "unit:c1:p0@0-p0@10",
            "kind": "background",
            "memory_text": "Archived material should not enter Read.",
            "status": "archived",
            "created_at_unit_index": 0,
            "archived_by_consolidation_id": "consolidation:c1:batch1",
        },
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
        recent_reading_memory=recent_reading_memory,
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
                    "ref_id": "source:sentence:c1-s1",
                    "kind": "source_excerpt",
                    "item_id": "c1-s1",
                    "summary": "Alpha sentence.",
                    "sentence_id": "c1-s1",
                }
            ],
            "excerpts": [
                {
                    "ref_id": "source:sentence:c1-s1",
                    "source_kind": "sentence",
                    "sentence_ids": ["c1-s1"],
                    "chapter_ref": "Chapter 1",
                    "excerpt_text": "Alpha sentence.",
                }
            ],
        },
    )

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
                "kind": "event_or_situation",
                "memory_text": "The opener introduces a practical dilemma that the next unit can build on.",
                "source_unit_span_id": "unit:c1:p1@0-p1@15",
                "created_at_unit_index": 1,
            }
        ],
        "active_entry_count": 1,
    }
    assert prompt_packet["concept_digest"][0]["concept_key"] == "promise"
    assert prompt_packet["concept_digest"][0]["support_status"] == "source_backed"
    assert prompt_packet["thread_digest"][0]["thread_key"]
    assert prompt_packet["thread_digest"][0]["projection_role"] == "current_support"
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["item_id"] == "frame-1"
    assert prompt_packet["reflective_digest"]["chapter_frames"][0]["projection_role"] == "current_support"
    assert prompt_packet["selective_carry"]["earlier_excerpts"][0]["ref_id"] == "source:sentence:c1-s1"
    assert prompt_packet["selective_carry"]["supporting_refs"][0]["ref_id"] == "source:sentence:c1-s1"
    assert "refs" not in prompt_packet
    assert "anchor_bank_digest" not in prompt_packet
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["reaction_id"] == "reaction-1"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["projection_role"] == "visible_trace"
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["visible_trace_support"] is True
    assert prompt_packet["local_continuity"]["recent_reactions"][0]["current_support"] is False
    assert "knowledge_activations" not in prompt_packet


def test_read_prompt_packet_includes_all_open_questions_without_runtime_fields():
    """Read prompt context should carry all open ActiveTensions, not the first six digest records."""

    active_items = [
        {
            "item_id": f"question-{index}",
            "tension_from": f"source trigger {index}",
            "tension_focus": f"what lingers with tension {index}",
            "working_interpretation": "",
            "status": "open",
            "source_refs": [_source_ref(f"Question {index}.")],
            "development_source_refs": [_source_ref(f"Answer {index}.")],
            "linked_concept_keys": [f"concept:{index}"],
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

    prompt_packet = build_read_prompt_packet(
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


def test_build_read_prompt_packet_exposes_retrieval_contract_without_full_memory_objects():
    """Memory-context retrieval should expose metadata without full objects."""

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

    supplemental_context = {
        "kind": "memory_context",
        "reason": "Need prior memory.",
        "retrieval_intent": "memory_recovery",
        "result_boundary": "settled_memory_refs_and_visible_trace_refs",
        "result_groups": ["concepts", "threads", "reactions", "refs"],
        "retrieval_events": [
            {
                "kind": "memory_context",
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
    }
    prompt_packet = build_read_prompt_packet(
        carry_forward_context=carry_forward,
        supplemental_context=supplemental_context,
    )

    selective_carry = prompt_packet["selective_carry"]
    assert selective_carry == build_supplemental_selective_carry(supplemental_context)
    assert selective_carry["supporting_refs"][0]["ref_id"] == "concept:promise"
    retrieval_context = selective_carry["retrieval_context"]
    assert retrieval_context["retrieval_intent"] == "memory_recovery"
    assert retrieval_context["result_boundary"] == "settled_memory_refs_and_visible_trace_refs"
    assert retrieval_context["result_groups"] == ["concepts", "threads", "reactions", "refs"]
    assert retrieval_context["retrieval_events"][0]["kind"] == "memory_context"
    assert retrieval_context["forwarded_result_groups"] == ["refs"]
    assert retrieval_context["not_forwarded_result_groups"] == ["concepts", "threads", "reactions"]
    assert retrieval_context["full_objects_forwarded"] is False
    assert "concepts" not in selective_carry
    assert "threads" not in selective_carry
    assert "reactions" not in selective_carry
    assert "knowledge_activations" not in selective_carry
    assert "knowledge_activations" not in retrieval_context
    assert "knowledge_activations" not in prompt_packet


def test_build_read_prompt_packet_uses_precise_sparse_retrieval_groups():
    """Memory-context metadata should not list absent groups as not forwarded."""

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

    supplemental_context = {
        "kind": "memory_context",
        "reason": "Need prior memory.",
        "retrieval_intent": "memory_recovery",
        "result_boundary": "settled_memory_refs_and_visible_trace_refs",
        "result_groups": ["concepts", "refs"],
        "retrieval_events": [
            {
                "kind": "memory_context",
                "retrieval_intent": "memory_recovery",
                "result_boundary": "settled_memory_refs_and_visible_trace_refs",
                "result_groups": ["concepts", "refs"],
            }
        ],
        "concepts": [{"concept_key": "promise", "summary": "A promise remains active."}],
        "refs": [
            {"ref_id": "concept:promise", "kind": "concept", "summary": "A promise remains active."},
        ],
        "knowledge_activations": [{"activation_id": "knowledge-1"}],
    }
    prompt_packet = build_read_prompt_packet(
        carry_forward_context=carry_forward,
        supplemental_context=supplemental_context,
    )

    selective_carry = prompt_packet["selective_carry"]
    assert selective_carry == build_supplemental_selective_carry(supplemental_context)
    retrieval_context = selective_carry["retrieval_context"]
    assert retrieval_context["result_groups"] == ["concepts", "refs"]
    assert retrieval_context["forwarded_result_groups"] == ["refs"]
    assert retrieval_context["not_forwarded_result_groups"] == ["concepts"]
    assert "threads" not in retrieval_context["not_forwarded_result_groups"]
    assert "reactions" not in retrieval_context["not_forwarded_result_groups"]
    assert retrieval_context["full_objects_forwarded"] is False
    assert "concepts" not in selective_carry
    assert "threads" not in selective_carry
    assert "reactions" not in selective_carry
    assert "knowledge_activations" not in prompt_packet
