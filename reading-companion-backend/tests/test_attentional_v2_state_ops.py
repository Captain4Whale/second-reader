"""Tests for attentional_v2 pure state-operation helpers."""

from __future__ import annotations

from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_knowledge_activations,
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_reconsolidation_records,
    build_empty_reflective_summaries,
    build_empty_active_attention,
)
from src.attentional_v2.state_ops import (
    append_reaction_record,
    append_reconsolidation_record,
    apply_active_attention_operations,
    apply_concept_registry_operations,
    apply_thread_trace_operations,
    close_local_meaning_unit,
    push_local_buffer_sentence,
    replace_policy_section,
    supersede_reflective_item,
    upsert_knowledge_activation,
    upsert_reflective_item,
)


def _source_ref(quote: str = "People want things from other people.") -> dict[str, object]:
    """Return one paragraph-offset source ref fixture."""

    return {
        "source_span_id": "src:c1:p1@0-p1@36",
        "source_span": {
            "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
            "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 36},
        },
        "quote": quote,
        "role": "support",
    }


def _find(items: list[dict[str, object]], key: str, value: str) -> dict[str, object]:
    """Return one item by stable key for lifecycle-boundary assertions."""

    for item in items:
        if item.get(key) == value:
            return item
    raise AssertionError(f"missing {key}={value}")


def test_apply_active_attention_operations_handles_append_update_close_link_and_drop():
    """Active-attention helpers should update tagged active_items without legacy bucket side effects."""

    state = build_empty_active_attention()
    state = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "append",
                "target_store": "active_attention",
                "item_id": "m-1",
                "reason": "motif became active",
                "payload": {
                    "attention_tags": ["motif"],
                    "question_from": "The chapter introduces value as a recurring problem.",
                    "driving_question": "How will value narrow as the chapter develops?",
                    "answer_boundary": "Later source distinguishes value from broad social wanting.",
                    "working_answer": "",
                    "source_refs": [_source_ref()],
                },
            }
        ],
    )

    state = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "update",
                "target_store": "active_attention",
                "item_id": "m-1",
                "payload": {
                    "working_answer": "Value is becoming a social exchange problem.",
                    "answer_source_refs": [_source_ref("Value is mediated by other people.")],
                    "linked_concept_keys": ["concept:value"],
                    "linked_thread_keys": ["thread:value"],
                },
            },
            {
                "operation_type": "close",
                "target_store": "active_attention",
                "item_id": "m-1",
                "payload": {},
            },
        ],
    )

    dropped = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "drop",
                "target_store": "active_attention",
                "item_id": "m-1",
                "reason": "motif cooled below the hot layer",
                "payload": {},
            }
        ],
    )

    assert state["active_items"][0]["item_id"] == "m-1"
    assert state["active_items"][0]["attention_tags"] == ["motif"]
    assert state["active_items"][0]["question_from"] == "The chapter introduces value as a recurring problem."
    assert state["active_items"][0]["driving_question"] == "How will value narrow as the chapter develops?"
    assert state["active_items"][0]["answer_boundary"] == "Later source distinguishes value from broad social wanting."
    assert state["active_items"][0]["working_answer"] == "Value is becoming a social exchange problem."
    assert state["active_items"][0]["status"] == "closed"
    assert state["active_items"][0]["linked_concept_keys"] == ["concept:value"]
    assert state["active_items"][0]["linked_thread_keys"] == ["thread:value"]
    assert state["active_items"][0]["source_refs"][0]["source_span_id"] == "src:c1:p1@0-p1@36"
    assert state["active_items"][0]["answer_source_refs"][0]["quote"] == "Value is mediated by other people."
    assert "bucket" not in state["active_items"][0]
    assert "kind" not in state["active_items"][0]
    assert dropped["active_items"] == []


def test_active_attention_text_fields_preserve_by_default_and_allow_explicit_clear():
    """Live-question text fields should distinguish omitted values from explicit replacement."""

    state = build_empty_active_attention()
    state = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "create",
                "target_store": "active_attention",
                "item_id": "q-1",
                "payload": {
                    "question_from": "A bomb is placed under the table.",
                    "driving_question": "When will the bomb explode?",
                    "answer_boundary": "A later passage reveals the timer, detonation, or disarming outcome.",
                    "working_answer": "No timing clue yet.",
                },
            }
        ],
    )
    state = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "update",
                "target_store": "active_attention",
                "item_id": "q-1",
                "payload": {"working_answer": ""},
            }
        ],
    )

    item = _find(state["active_items"], "item_id", "q-1")
    assert item["question_from"] == "A bomb is placed under the table."
    assert item["driving_question"] == "When will the bomb explode?"
    assert item["answer_boundary"] == "A later passage reveals the timer, detonation, or disarming outcome."
    assert item["working_answer"] == ""


def test_active_attention_lifecycle_states_preserve_items_until_explicit_drop():
    """Cooling, closing, and answered states are lifecycle states; only drop removes active items."""

    state = {
        "active_items": [
            {
                "item_id": "cooling-question",
                "attention_tags": ["question"],
                "statement": "This question is cooling but still part of lineage.",
                "source_refs": [_source_ref("Cooling question.")],
                "linked_concept_keys": ["concept:question"],
                "status": "active",
            },
            {
                "item_id": "closing-thread",
                "attention_tags": ["thread"],
                "statement": "This thread can close without disappearing.",
                "source_refs": [_source_ref("Closing thread.")],
                "linked_thread_keys": ["thread:closing"],
                "status": "active",
            },
        ]
    }

    cooled = apply_active_attention_operations(
        state,
        [
            {
                "operation_type": "cool",
                "target_store": "active_attention",
                "item_id": "cooling-question",
                "payload": {},
            }
        ],
    )
    cooled_item = _find(cooled["active_items"], "item_id", "cooling-question")
    assert cooled_item["status"] == "cooling"
    assert cooled_item["statement"] == "This question is cooling but still part of lineage."
    assert cooled_item["source_refs"][0]["source_span_id"] == "src:c1:p1@0-p1@36"
    assert cooled_item["linked_concept_keys"] == ["concept:question"]

    resolved = apply_active_attention_operations(
        cooled,
        [
            {
                "operation_type": "resolve",
                "target_store": "active_attention",
                "item_id": "cooling-question",
                "payload": {},
            },
            {
                "operation_type": "close",
                "target_store": "active_attention",
                "item_id": "closing-thread",
                "payload": {},
            },
        ],
    )
    resolved_item = _find(resolved["active_items"], "item_id", "cooling-question")
    closed_item = _find(resolved["active_items"], "item_id", "closing-thread")
    assert resolved_item["status"] == "answered"
    assert resolved_item["source_refs"][0]["quote"] == "Cooling question."
    assert closed_item["status"] == "closed"
    assert closed_item["linked_thread_keys"] == ["thread:closing"]

    dropped = apply_active_attention_operations(
        resolved,
        [
            {
                "operation_type": "drop",
                "target_store": "active_attention",
                "item_id": "cooling-question",
                "payload": {},
            }
        ],
    )

    assert [item["item_id"] for item in dropped["active_items"]] == ["closing-thread"]
    assert _find(dropped["active_items"], "item_id", "closing-thread")["status"] == "closed"


def test_state_ops_already_apply_resolve_operations():
    """Resolve behavior is store-specific: active questions become answered."""

    active_state = {
        "active_items": [
            {
                "item_id": "hot-question",
                "statement": "A live question.",
                "status": "active",
            }
        ]
    }
    active_state = apply_active_attention_operations(
        active_state,
        [
            {
                "operation_type": "resolve",
                "target_store": "active_attention",
                "item_id": "hot-question",
                "payload": {},
            }
        ],
    )

    concept_state = apply_concept_registry_operations(
        {"entries": [{"concept_key": "concept-question", "status": "active", "summary": "old"}]},
        [
            {
                "operation_type": "resolve",
                "target_store": "concept_registry",
                "item_id": "concept-question",
                "payload": {"status": "resolved"},
            }
        ],
    )
    thread_state = apply_thread_trace_operations(
        {"entries": [{"thread_key": "thread-question", "status": "active", "summary": "old"}]},
        [
            {
                "operation_type": "resolve",
                "target_store": "thread_trace",
                "item_id": "thread-question",
                "payload": {"status": "resolved"},
            }
        ],
    )

    assert active_state["active_items"][0]["status"] == "answered"
    assert concept_state["entries"][0]["status"] == "resolved"
    assert thread_state["entries"][0]["status"] == "resolved"


def test_concept_registry_lifecycle_is_store_specific_and_non_destructive():
    """Concept lifecycle operations should remain deterministic without mimicking active attention."""

    state = {
        "entries": [
            {
                "concept_key": "concept-preserve",
                "concept_type": "motif",
                "status": "active",
                "summary": "A concept with an existing active status.",
                "source_refs": [_source_ref("Concept preserve.")],
            },
            {
                "concept_key": "concept-close",
                "concept_type": "motif",
                "status": "active",
                "summary": "A concept ready to resolve.",
                "source_refs": [_source_ref("Concept close.")],
                "linked_thread_ids": ["thread:shared"],
            },
            {
                "concept_key": "concept-other",
                "concept_type": "motif",
                "status": "active",
                "summary": "Another concept should remain.",
                "source_refs": [_source_ref("Concept other.")],
            },
        ]
    }

    wrong_store = apply_concept_registry_operations(
        state,
        [
            {
                "operation_type": "resolve",
                "target_store": "thread_trace",
                "item_id": "concept-close",
                "payload": {"status": "resolved"},
            }
        ],
    )
    assert _find(wrong_store["entries"], "concept_key", "concept-close")["status"] == "active"

    preserved = apply_concept_registry_operations(
        wrong_store,
        [
            {
                "operation_type": "close",
                "target_store": "concept_registry",
                "item_id": "concept-preserve",
                "payload": {},
            }
        ],
    )
    assert _find(preserved["entries"], "concept_key", "concept-preserve")["status"] == "active"

    resolved = apply_concept_registry_operations(
        preserved,
        [
            {
                "operation_type": "close",
                "target_store": "concept_registry",
                "item_id": "concept-close",
                "payload": {"status": "resolved", "summary": "Resolved concept."},
            }
        ],
    )
    resolved_concept = _find(resolved["entries"], "concept_key", "concept-close")
    assert resolved_concept["status"] == "resolved"
    assert resolved_concept["summary"] == "Resolved concept."
    assert resolved_concept["source_refs"][0]["quote"] == "Concept close."
    assert resolved_concept["linked_thread_ids"] == ["thread:shared"]

    dropped = apply_concept_registry_operations(
        resolved,
        [
            {
                "operation_type": "drop",
                "target_store": "concept_registry",
                "item_id": "concept-close",
                "payload": {},
            }
        ],
    )
    assert [entry["concept_key"] for entry in dropped["entries"]] == ["concept-preserve", "concept-other"]


def test_concept_registry_maps_legacy_payload_aliases_to_summary():
    """Legacy LLM payload aliases should not create empty concept summaries."""

    state = apply_concept_registry_operations(
        {"entries": []},
        [
            {
                "operation_type": "update",
                "target_store": "concept_registry",
                "item_id": "camp-reaction-stages",
                "payload": {
                    "concept_type": "framework",
                    "definition": "The text introduces a three-stage prisoner-response model.",
                    "source_refs": [_source_ref("three stages")],
                },
            },
            {
                "operation_type": "update",
                "target_store": "concept_registry",
                "item_id": "protective-apathy",
                "payload": {
                    "concept_type": "concept",
                    "framework_extension": {
                        "stage": "second stage",
                        "meaning": "apathy functions as a protective shell",
                    },
                },
            },
        ],
    )

    first = _find(state["entries"], "concept_key", "camp-reaction-stages")
    second = _find(state["entries"], "concept_key", "protective-apathy")
    assert first["summary"] == "The text introduces a three-stage prisoner-response model."
    assert second["summary"] == "stage: second stage; meaning: apathy functions as a protective shell"


def test_thread_trace_lifecycle_is_store_specific_and_non_destructive():
    """Thread lifecycle operations should remain deterministic within the thread store."""

    state = {
        "entries": [
            {
                "thread_key": "thread-preserve",
                "thread_type": "trace_link",
                "status": "active",
                "summary": "A trace with an existing active status.",
                "source_refs": [_source_ref("Thread preserve.")],
            },
            {
                "thread_key": "thread-close",
                "thread_type": "open_reference",
                "status": "active",
                "summary": "A thread ready to resolve.",
                "source_refs": [_source_ref("Thread close.")],
                "linked_concept_keys": ["concept:shared"],
            },
            {
                "thread_key": "thread-other",
                "thread_type": "trace_link",
                "status": "active",
                "summary": "Another thread should remain.",
                "source_refs": [_source_ref("Thread other.")],
            },
        ]
    }

    wrong_store = apply_thread_trace_operations(
        state,
        [
            {
                "operation_type": "resolve",
                "target_store": "concept_registry",
                "item_id": "thread-close",
                "payload": {"status": "resolved"},
            }
        ],
    )
    assert _find(wrong_store["entries"], "thread_key", "thread-close")["status"] == "active"

    preserved = apply_thread_trace_operations(
        wrong_store,
        [
            {
                "operation_type": "close",
                "target_store": "thread_trace",
                "item_id": "thread-preserve",
                "payload": {},
            }
        ],
    )
    assert _find(preserved["entries"], "thread_key", "thread-preserve")["status"] == "active"

    resolved = apply_thread_trace_operations(
        preserved,
        [
            {
                "operation_type": "close",
                "target_store": "thread_trace",
                "item_id": "thread-close",
                "payload": {"status": "resolved", "summary": "Resolved thread."},
            }
        ],
    )
    resolved_thread = _find(resolved["entries"], "thread_key", "thread-close")
    assert resolved_thread["status"] == "resolved"
    assert resolved_thread["summary"] == "Resolved thread."
    assert resolved_thread["source_refs"][0]["quote"] == "Thread close."
    assert resolved_thread["linked_concept_keys"] == ["concept:shared"]

    dropped = apply_thread_trace_operations(
        resolved,
        [
            {
                "operation_type": "drop",
                "target_store": "thread_trace",
                "item_id": "thread-close",
                "payload": {},
            }
        ],
    )
    assert [entry["thread_key"] for entry in dropped["entries"]] == ["thread-preserve", "thread-other"]


def test_thread_trace_maps_legacy_payload_aliases_to_summary():
    """Legacy thread payload aliases should not create empty thread summaries."""

    state = apply_thread_trace_operations(
        {"entries": []},
        [
            {
                "operation_type": "update",
                "target_store": "thread_trace",
                "item_id": "adaptation-arc",
                "payload": {
                    "thread_type": "development",
                    "current_state": "The first shock is giving way to adaptation.",
                    "source_refs": [_source_ref("adaptation")],
                },
            }
        ],
    )

    thread = _find(state["entries"], "thread_key", "adaptation-arc")
    assert thread["summary"] == "The first shock is giving way to adaptation."


def test_activation_helpers_upsert_source_refs_by_id():
    """Activation helpers should replace existing items while carrying inline source refs."""

    activation_state = build_empty_knowledge_activations()
    activation_state = upsert_knowledge_activation(
        activation_state,
        {
            "activation_id": "k-1",
            "trigger_source_ref": _source_ref(),
            "activation_type": "prior_frame",
            "source_candidate": "exchange theory",
            "recognition_confidence": "plausible",
            "reading_warrant": "author is defining a social market",
            "role_assessment": "background lens",
            "evidence_hints": ["market", "value"],
            "evidence_rationale": "direct lexical overlap",
            "source_refs": [_source_ref()],
            "conflict_source_refs": [],
            "status": "plausible",
        },
    )
    activation_state = upsert_knowledge_activation(
        activation_state,
        {
            "activation_id": "k-1",
            "trigger_source_ref": _source_ref(),
            "activation_type": "prior_frame",
            "source_candidate": "exchange theory",
            "recognition_confidence": "strong",
            "reading_warrant": "author is explicitly defining a market relation",
            "role_assessment": "active lens",
            "evidence_hints": ["market", "value"],
            "evidence_rationale": "stronger later confirmation",
            "source_refs": [_source_ref()],
            "conflict_source_refs": [],
            "status": "strong",
        },
    )

    assert len(activation_state["activations"]) == 1
    assert activation_state["activations"][0]["status"] == "strong"
    assert activation_state["activations"][0]["source_refs"][0]["source_span_id"] == "src:c1:p1@0-p1@36"


def test_close_local_meaning_unit_tracks_recent_units():
    """Closing one meaning unit should retain a compact recent unit history for Phase 7 resume."""

    buffer_state = build_empty_local_buffer()
    buffer_state = push_local_buffer_sentence(
        buffer_state,
        {
            "sentence_id": "c1-s1",
            "sentence_index": 1,
            "paragraph_index": 1,
            "text": "Sentence one.",
            "text_role": "body",
        },
    )
    buffer_state = push_local_buffer_sentence(
        buffer_state,
        {
            "sentence_id": "c1-s2",
            "sentence_index": 2,
            "paragraph_index": 1,
            "text": "Sentence two.",
            "text_role": "body",
        },
    )

    closed = close_local_meaning_unit(buffer_state)

    assert closed["open_meaning_unit_sentence_ids"] == []
    assert closed["recent_meaning_units"] == [["c1-s1", "c1-s2"]]
    assert closed["last_meaning_unit_closed_at_sentence_id"] == "c1-s2"


def test_reflective_reaction_reconsolidation_and_policy_helpers_append_cleanly():
    """The helper layer should support the remaining Phase 1 state stores."""

    reflective_state = upsert_reflective_item(
        build_empty_reflective_summaries(),
        bucket="chapter_understandings",
        item={
            "item_id": "r-1",
            "statement": "Value is mediated by other people.",
            "source_refs": [_source_ref()],
            "confidence_band": "working",
            "promoted_from": "active_attention_item",
            "status": "active",
        },
    )
    reaction_state = append_reaction_record(
        build_empty_reaction_records(),
        {
            "reaction_id": "rx-1",
            "chapter_id": 1,
            "chapter_ref": "Chapter 1",
            "emitted_at_source_span_id": "src:c1:p1@0-p1@36",
            "type": "discern",
            "thought": "The later sentence changes the frame.",
            "source_quote": "The frame changes here.",
            "primary_source_ref": _source_ref("The frame changes here."),
            "related_source_refs": [],
            "created_at": "2026-03-23T00:00:30Z",
        },
    )
    reconsolidation_state = append_reconsolidation_record(
        build_empty_reconsolidation_records(),
        {
            "record_id": "rc-1",
            "prior_reaction_id": "rx-1",
            "new_reaction_id": "rx-2",
            "change_kind": "tightened",
            "what_changed": "The later sentence makes the earlier claim narrower.",
            "rationale": "later sentence tightened the earlier claim",
            "created_at": "2026-03-23T00:01:00Z",
        },
    )
    reflective_state = supersede_reflective_item(
        reflective_state,
        bucket="chapter_understandings",
        item_id="r-1",
        superseded_by_item_id="r-2",
    )
    policy = replace_policy_section(
        build_default_reader_policy(),
        section="resume",
        payload={"checkpoint_summary_required": True, "cold_resume_target_sentences": 3},
    )

    assert reflective_state["chapter_understandings"][0]["status"] == "superseded"
    assert reaction_state["records"][0]["reaction_id"] == "rx-1"
    reaction_state = append_reaction_record(
        reaction_state,
        {
            "reaction_id": "rx-2",
            "chapter_id": 1,
            "chapter_ref": "Chapter 1",
            "emitted_at_source_span_id": "src:c1:p1@0-p1@36",
            "type": "question",
            "thought": "The second reaction is appended without rewriting the first.",
            "source_quote": "A second frame appears.",
            "primary_source_ref": _source_ref("A second frame appears."),
            "related_source_refs": [],
            "created_at": "2026-03-23T00:00:45Z",
        },
    )
    assert reconsolidation_state["records"][0]["record_id"] == "rc-1"
    assert policy["resume"]["cold_resume_target_sentences"] == 3
    assert [record["reaction_id"] for record in reaction_state["records"]] == ["rx-1", "rx-2"]
    assert reaction_state["records"][0]["thought"] == "The later sentence changes the frame."
    assert reflective_state["chapter_understandings"][0]["statement"] == "Value is mediated by other people."
    assert reflective_state["chapter_understandings"][0]["superseded_by_item_id"] == "r-2"
