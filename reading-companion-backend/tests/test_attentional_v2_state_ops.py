"""Tests for attentional_v2 pure state-operation helpers."""

from __future__ import annotations

from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_anchor_memory,
    build_empty_knowledge_activations,
    build_empty_move_history,
    build_empty_reconsolidation_records,
    build_empty_reflective_summaries,
    build_empty_working_pressure,
)
from src.attentional_v2.state_ops import (
    append_anchor_relation,
    append_move,
    append_reconsolidation_record,
    replace_policy_section,
    replace_pressure_bucket,
    set_gate_state,
    upsert_anchor_record,
    upsert_knowledge_activation,
    upsert_reflective_item,
)


def test_working_pressure_helpers_replace_bucket_and_gate_state():
    """Working-pressure helpers should return updated copies instead of mutating input."""

    state = build_empty_working_pressure()

    next_state = replace_pressure_bucket(
        set_gate_state(state, "watch"),
        bucket="local_questions",
        items=[
            {
                "item_id": "q-1",
                "kind": "question",
                "statement": "Why does the author make this turn now?",
                "support_anchor_ids": ["a-1"],
                "status": "open",
            }
        ],
    )

    assert state["gate_state"] == "quiet"
    assert state["local_questions"] == []
    assert next_state["gate_state"] == "watch"
    assert next_state["local_questions"][0]["item_id"] == "q-1"


def test_anchor_and_activation_helpers_upsert_by_id():
    """Anchor and activation helpers should replace existing items when ids match."""

    anchor_state = build_empty_anchor_memory()
    anchor_state = upsert_anchor_record(
        anchor_state,
        {
            "anchor_id": "a-1",
            "sentence_start_id": "c1-s2",
            "sentence_end_id": "c1-s2",
            "quote": "People want things from other people.",
            "locator": {"paragraph_index": 2, "paragraph_start": 2, "paragraph_end": 2, "char_start": 0, "char_end": 36},
            "anchor_kind": "claim",
            "why_it_mattered": "sets the social frame",
            "status": "active",
        },
    )
    anchor_state = upsert_anchor_record(
        anchor_state,
        {
            "anchor_id": "a-1",
            "sentence_start_id": "c1-s2",
            "sentence_end_id": "c1-s2",
            "quote": "People want things from other people.",
            "locator": {"paragraph_index": 2, "paragraph_start": 2, "paragraph_end": 2, "char_start": 0, "char_end": 36},
            "anchor_kind": "claim",
            "why_it_mattered": "reframed as exchange pressure",
            "status": "active",
        },
    )
    anchor_state = append_anchor_relation(
        anchor_state,
        {
            "relation_id": "rel-1",
            "relation_type": "support",
            "source_anchor_id": "a-1",
            "target_anchor_id": "a-2",
            "rationale": "sets up the later claim",
        },
    )

    activation_state = build_empty_knowledge_activations()
    activation_state = upsert_knowledge_activation(
        activation_state,
        {
            "activation_id": "k-1",
            "trigger_anchor_id": "a-1",
            "activation_type": "prior_frame",
            "source_candidate": "exchange theory",
            "recognition_confidence": "plausible",
            "reading_warrant": "author is defining a social market",
            "role_assessment": "background lens",
            "evidence_hints": ["market", "value"],
            "evidence_rationale": "direct lexical overlap",
            "support_anchor_ids": ["a-1"],
            "conflict_anchor_ids": [],
            "introduced_at_sentence_id": "c1-s2",
            "last_touched_sentence_id": "c1-s2",
            "status": "plausible",
        },
    )
    activation_state = upsert_knowledge_activation(
        activation_state,
        {
            "activation_id": "k-1",
            "trigger_anchor_id": "a-1",
            "activation_type": "prior_frame",
            "source_candidate": "exchange theory",
            "recognition_confidence": "strong",
            "reading_warrant": "author is explicitly defining a market relation",
            "role_assessment": "active lens",
            "evidence_hints": ["market", "value"],
            "evidence_rationale": "stronger later confirmation",
            "support_anchor_ids": ["a-1"],
            "conflict_anchor_ids": [],
            "introduced_at_sentence_id": "c1-s2",
            "last_touched_sentence_id": "c1-s3",
            "status": "strong",
        },
    )

    assert len(anchor_state["anchor_records"]) == 1
    assert anchor_state["anchor_records"][0]["why_it_mattered"] == "reframed as exchange pressure"
    assert anchor_state["anchor_relations"][0]["relation_id"] == "rel-1"
    assert len(activation_state["activations"]) == 1
    assert activation_state["activations"][0]["status"] == "strong"


def test_reflective_move_reconsolidation_and_policy_helpers_append_cleanly():
    """The helper layer should support the remaining Phase 1 state stores."""

    reflective_state = upsert_reflective_item(
        build_empty_reflective_summaries(),
        bucket="chapter_understandings",
        item={
            "item_id": "r-1",
            "statement": "Value is mediated by other people.",
            "support_anchor_ids": ["a-1"],
            "confidence_band": "working",
            "promoted_from": "local_hypothesis",
            "status": "active",
        },
    )
    move_state = append_move(
        build_empty_move_history(),
        {
            "move_id": "m-1",
            "move_type": "bridge",
            "reason": "motif recurs after a new example",
            "source_sentence_id": "c1-s4",
            "target_anchor_id": "a-1",
            "target_sentence_id": "c1-s2",
            "created_at": "2026-03-23T00:00:00Z",
        },
    )
    reconsolidation_state = append_reconsolidation_record(
        build_empty_reconsolidation_records(),
        {
            "record_id": "rc-1",
            "prior_reaction_id": "rx-1",
            "new_reaction_id": "rx-2",
            "rationale": "later sentence tightened the earlier claim",
            "created_at": "2026-03-23T00:01:00Z",
        },
    )
    policy = replace_policy_section(
        build_default_reader_policy(),
        section="resume",
        payload={"checkpoint_summary_required": True, "reentry_window_sentences": 3},
    )

    assert reflective_state["chapter_understandings"][0]["item_id"] == "r-1"
    assert move_state["moves"][0]["move_type"] == "bridge"
    assert reconsolidation_state["records"][0]["record_id"] == "rc-1"
    assert policy["resume"]["reentry_window_sentences"] == 3
