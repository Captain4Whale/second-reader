"""Tests for supplemental retrieval-context contract helpers."""

from __future__ import annotations

from src.attentional_v2.read_context import merge_supplemental_contexts, resolve_context_request
from src.attentional_v2.schemas import (
    build_empty_concept_registry,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
)


def _book_document() -> dict[str, object]:
    return {
        "chapters": [
            {
                "id": 1,
                "reference": "Chapter 1",
                "title": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text_role": "body",
                        "text": "Alpha sentence. Beta sentence.",
                    }
                ],
            }
        ]
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


def _empty_carry_forward() -> dict[str, object]:
    return {
        "refs": [],
        "concept_digest": [],
        "thread_digest": [],
    }


def test_look_back_emits_source_calibration_retrieval_contract():
    """look_back should stay source-bound and expose compact retrieval intent."""

    carry_forward = _empty_carry_forward()
    carry_forward["refs"] = [{"ref_id": "source:alpha", "source_ref": _source_ref()}]

    resolved = resolve_context_request(
        context_request={
            "kind": "look_back",
            "reason": "Need the earlier exact wording.",
            "source_ref_ids": ["source:alpha"],
        },
        carry_forward_context=carry_forward,  # type: ignore[arg-type]
        book_document=_book_document(),  # type: ignore[arg-type]
        chapter_ref="Chapter 1",
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=build_empty_reaction_records(),
    )

    assert resolved is not None
    assert resolved["kind"] == "look_back"
    assert resolved["retrieval_intent"] == "source_calibration"
    assert resolved["result_boundary"] == "source_refs_and_excerpts"
    assert resolved["result_groups"] == ["source_refs", "excerpts", "refs"]
    assert resolved["retrieval_events"] == [
        {
            "kind": "look_back",
            "retrieval_intent": "source_calibration",
            "result_boundary": "source_refs_and_excerpts",
            "result_groups": ["source_refs", "excerpts", "refs"],
        }
    ]
    assert resolved["source_refs"]
    assert resolved["excerpts"][0]["text"] == "Alpha sentence."
    assert resolved["refs"][0]["kind"] == "source"
    assert "concepts" not in resolved
    assert "threads" not in resolved
    assert "reactions" not in resolved


def test_active_recall_emits_memory_recovery_contract_and_visible_trace_reactions():
    """active_recall should label memory recovery without making reactions semantic memory."""

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
    reaction_records = build_empty_reaction_records()
    reaction_records["records"] = [
        {
            "reaction_id": "reaction-1",
            "type": "highlight",
            "thought": "The first line already carries pressure.",
            "primary_source_ref": _source_ref(),
            "source_quote": "Alpha sentence.",
        }
    ]

    resolved = resolve_context_request(
        context_request={"kind": "active_recall", "reason": "Need prior memory."},
        carry_forward_context=_empty_carry_forward(),  # type: ignore[arg-type]
        book_document=_book_document(),  # type: ignore[arg-type]
        chapter_ref="Chapter 1",
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=reaction_records,
    )

    assert resolved is not None
    assert resolved["kind"] == "active_recall"
    assert resolved["retrieval_intent"] == "memory_recovery"
    assert resolved["result_boundary"] == "settled_memory_refs_and_visible_trace_refs"
    assert resolved["result_groups"] == ["concepts", "threads", "reactions", "refs"]
    assert resolved["retrieval_events"] == [
        {
            "kind": "active_recall",
            "retrieval_intent": "memory_recovery",
            "result_boundary": "settled_memory_refs_and_visible_trace_refs",
            "result_groups": ["concepts", "threads", "reactions", "refs"],
        }
    ]
    assert resolved["concepts"][0]["concept_key"] == "promise"
    assert resolved["threads"][0]["thread_key"] == "thread:promise"
    assert resolved["reactions"][0]["result_role"] == "visible_trace"
    assert resolved["reactions"][0]["semantic_memory"] is False
    reaction_ref = next(ref for ref in resolved["refs"] if ref["kind"] == "reaction")
    assert reaction_ref["result_role"] == "visible_trace"
    assert reaction_ref["semantic_memory"] is False


def test_active_recall_result_groups_only_include_non_empty_groups():
    """Sparse active_recall results should not advertise absent groups."""

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

    resolved = resolve_context_request(
        context_request={"kind": "active_recall", "reason": "Need prior memory."},
        carry_forward_context=_empty_carry_forward(),  # type: ignore[arg-type]
        book_document=_book_document(),  # type: ignore[arg-type]
        chapter_ref="Chapter 1",
        concept_registry=concept_registry,
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        reaction_records=build_empty_reaction_records(),
    )

    assert resolved is not None
    assert resolved["retrieval_intent"] == "memory_recovery"
    assert resolved["result_boundary"] == "settled_memory_refs_and_visible_trace_refs"
    assert resolved["result_groups"] == ["concepts", "refs"]
    assert resolved["retrieval_events"] == [
        {
            "kind": "active_recall",
            "retrieval_intent": "memory_recovery",
            "result_boundary": "settled_memory_refs_and_visible_trace_refs",
            "result_groups": ["concepts", "refs"],
        }
    ]
    assert resolved["concepts"]
    assert resolved["refs"]
    assert resolved["threads"] == []
    assert resolved["reactions"] == []


def test_merge_supplemental_contexts_preserves_retrieval_events_and_result_groups():
    """Merged supplemental bundles should preserve per-request retrieval boundaries."""

    look_back = {
        "kind": "look_back",
        "reason": "Need the earlier line.",
        "retrieval_intent": "source_calibration",
        "result_boundary": "source_refs_and_excerpts",
        "result_groups": ["source_refs", "excerpts", "refs"],
        "retrieval_events": [
            {
                "kind": "look_back",
                "retrieval_intent": "source_calibration",
                "result_boundary": "source_refs_and_excerpts",
                "result_groups": ["source_refs", "excerpts", "refs"],
            }
        ],
        "refs": [{"ref_id": "source:alpha", "kind": "source"}],
        "excerpts": [{"ref_id": "source:alpha", "text": "Alpha sentence."}],
    }
    active_recall = {
        "kind": "active_recall",
        "reason": "Need prior memory.",
        "retrieval_intent": "memory_recovery",
        "result_boundary": "settled_memory_refs_and_visible_trace_refs",
        "result_groups": ["concepts", "refs"],
        "retrieval_events": [
            {
                "kind": "active_recall",
                "retrieval_intent": "memory_recovery",
                "result_boundary": "settled_memory_refs_and_visible_trace_refs",
                "result_groups": ["concepts", "refs"],
            }
        ],
        "refs": [{"ref_id": "concept:promise", "kind": "concept"}],
        "concepts": [{"concept_key": "promise"}],
    }

    merged = merge_supplemental_contexts(look_back, active_recall)

    assert merged is not None
    assert merged["kind"] == "supplemental_bundle"
    assert merged["retrieval_intent"] == "mixed"
    assert merged["result_boundary"] == "supplemental_bundle"
    assert merged["result_groups"] == ["source_refs", "excerpts", "refs", "concepts"]
    assert [event["kind"] for event in merged["retrieval_events"]] == ["look_back", "active_recall"]
    assert [ref["ref_id"] for ref in merged["refs"]] == ["source:alpha", "concept:promise"]
