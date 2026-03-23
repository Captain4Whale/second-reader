"""Tests for attentional_v2 knowledge lifecycle and search posture."""

from __future__ import annotations

from src.attentional_v2.knowledge import apply_activation_operations, resolve_search_policy_mode
from src.attentional_v2.schemas import build_default_reader_policy, build_empty_knowledge_activations


def test_resolve_search_policy_mode_keeps_search_rare():
    """Phase 5 search policy should stay conservative even when the model asks for more."""

    policy = build_default_reader_policy()

    assert resolve_search_policy_mode(
        "search_now",
        search_trigger="blocking_allusion",
        reading_can_continue=False,
        reader_policy=policy,
    ) == "search_now"
    assert resolve_search_policy_mode(
        "search_now",
        search_trigger="genuine_curiosity",
        reading_can_continue=False,
        reader_policy=policy,
    ) == "defer_search"
    assert resolve_search_policy_mode(
        "defer_search",
        search_trigger="ornamental_curiosity",
        reader_policy=policy,
    ) == "no_search"


def test_apply_activation_operations_refreshes_knowledge_use_mode():
    """Text-earned live activations should lift knowledge mode without changing the rare-search default."""

    state = build_empty_knowledge_activations()
    policy = build_default_reader_policy()

    state = apply_activation_operations(
        state,
        [
            {
                "operation_type": "create",
                "target_store": "knowledge_activations",
                "item_id": "k-1",
                "reason": "the passage activates a prior frame",
                "payload": {
                    "trigger_anchor_id": "a-1",
                    "activation_type": "prior_frame",
                    "source_candidate": "exchange theory",
                    "recognition_confidence": "plausible",
                    "reading_warrant": "the passage turns on value in relationships",
                    "role_assessment": "active lens",
                    "evidence_hints": ["value", "relationships"],
                    "evidence_rationale": "the lexical frame is text-earned",
                    "support_anchor_ids": ["a-1"],
                    "conflict_anchor_ids": [],
                    "status": "plausible",
                },
            }
        ],
        current_sentence_id="c1-s3",
        reader_policy=policy,
    )

    assert state["knowledge_use_mode"] == "book_grounded_plus_prior_knowledge"
    assert state["search_policy_mode"] == "no_search"
    assert state["activations"][0]["last_touched_sentence_id"] == "c1-s3"

    cooled = apply_activation_operations(
        state,
        [
            {
                "operation_type": "cool",
                "target_store": "knowledge_activations",
                "item_id": "k-1",
                "reason": "the activation no longer deserves active carry",
                "payload": {},
            }
        ],
        current_sentence_id="c1-s4",
        reader_policy=policy,
    )

    assert cooled["activations"][0]["status"] == "weak"
    assert cooled["knowledge_use_mode"] == "book_grounded_only"
