"""Tests for attentional_v2 pure state-operation helpers."""

from __future__ import annotations

from src.attentional_v2.schemas import (
    build_default_reader_policy,
    build_empty_local_buffer,
    build_empty_reaction_records,
    build_empty_recent_reading_memory,
)
from src.attentional_v2.state_ops import (
    append_reaction_record,
    apply_recent_reading_memory_operations,
    close_local_meaning_unit,
    push_local_buffer_sentence,
    replace_policy_section,
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




def test_apply_recent_reading_memory_operations_appends_unit_level_entries_only():
    """Recent Reading Memory is append-only before consolidation and uses unit-level provenance."""

    state = build_empty_recent_reading_memory()
    next_state = apply_recent_reading_memory_operations(
        state,
        [
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "reason": "This should not be persisted as part of the memory entry.",
                "payload": {
                    "memory_text": "The prisoners begin adapting to camp shock through a staged psychological response.",
                    "source_refs": [{"source_span_id": "should-not-be-carried"}],
                },
            },
            {
                "op": "update",
                "target_store": "recent_reading_memory",
                "payload": {"memory_text": "Updates are ignored before consolidation."},
            },
        ],
        source_unit_span_id="unit:c1:p45@0-p61@120",
        created_at_unit_index=7,
    )

    assert next_state is not state
    assert len(next_state["entries"]) == 1
    entry = next_state["entries"][0]
    assert "kind" not in entry
    assert entry["entry_id"] == "recent:c1:u0007:m1"
    assert entry["source_unit_span_id"] == "unit:c1:p45@0-p61@120"
    assert entry["memory_text"] == "The prisoners begin adapting to camp shock through a staged psychological response."
    assert entry["status"] == "active"
    assert entry["created_at_unit_index"] == 7
    assert entry["archived_by_consolidation_id"] is None
    assert entry["token_estimate"]["estimator"] == "tiktoken_o200k_base_v1"

    source_span_state = apply_recent_reading_memory_operations(
        build_empty_recent_reading_memory(),
        [
            {
                "op": "append",
                "target_store": "recent_reading_memory",
                "payload": {"memory_text": "A source-span id also preserves the chapter token."},
            }
        ],
        source_unit_span_id="src:c2:p3@0-p3@40",
        created_at_unit_index=2,
    )
    assert source_span_state["entries"][0]["entry_id"] == "recent:c2:u0002:m1"












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
    policy = replace_policy_section(
        build_default_reader_policy(),
        section="resume",
        payload={"checkpoint_summary_required": True, "cold_resume_target_sentences": 3},
    )

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
    assert policy["resume"]["cold_resume_target_sentences"] == 3
    assert [record["reaction_id"] for record in reaction_state["records"]] == ["rx-1", "rx-2"]
    assert reaction_state["records"][0]["thought"] == "The later sentence changes the frame."
