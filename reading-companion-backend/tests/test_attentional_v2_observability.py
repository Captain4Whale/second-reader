from __future__ import annotations

import json
from pathlib import Path

from src.attentional_v2.observability import record_read, record_settlement
from src.attentional_v2.storage import read_audit_file, settlement_audit_file


def test_record_settlement_writes_compact_state_deltas(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_settlement(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unit_sentence_ids=["c1-s1", "c1-s2"],
        focal_sentence_id="c1-s2",
        memory_uptake_ops=[
            {
                "operation_type": "append",
                "target_store": "active_attention",
                "target_store_emitted": "active_attention",
                "effective_target_store": "active_attention",
                "target_key": "hot-2",
                "payload": {
                    "source_refs": [
                        {"resolution": {"status": "matched"}},
                        {"resolution": {"status": "fallback_unit_span"}},
                    ]
                },
            },
            {
                "operation_type": "update",
                "target_store": "concept_registry",
                "target_store_emitted": "concept_registry",
                "effective_target_store": "concept_registry",
                "item_id": "concept-1",
            },
        ],
        before_active_attention={
            "active_items": [
                {"item_id": "hot-1", "statement": "old"},
                {"item_id": "hot-removed", "statement": "drop"},
            ]
        },
        after_active_attention={
            "active_items": [
                {"item_id": "hot-1", "statement": "updated"},
                {"item_id": "hot-2", "statement": "new"},
            ]
        },
        before_concept_registry={"entries": []},
        after_concept_registry={"entries": [{"concept_key": "concept-1", "summary": "new"}]},
        before_thread_trace={"entries": [{"thread_key": "thread-1", "summary": "old"}]},
        after_thread_trace={"entries": [{"thread_key": "thread-1", "summary": "updated"}]},
        before_reaction_records={"records": [{"reaction_id": "reaction-1", "thought": "old"}]},
        after_reaction_records={
            "records": [
                {"reaction_id": "reaction-1", "thought": "old"},
                {"reaction_id": "reaction-2", "thought": "new"},
            ]
        },
        emitted_reaction_ids=["reaction-2"],
    )

    audit_line = json.loads(settlement_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["memory_uptake_op_count"] == 2
    assert audit_line["memory_uptake_ops_by_target_store"] == {"active_attention": 1, "concept_registry": 1}
    assert audit_line["memory_uptake_op_outcomes"][0] == {
        "operation_index": 0,
        "operation_type": "append",
        "target_store_emitted": "active_attention",
        "effective_target_store": "active_attention",
        "target_key": "hot-2",
        "item_id": "hot-2",
        "source_ref_count": 2,
        "source_ref_resolution_statuses": ["matched", "fallback_unit_span"],
        "compatibility_warnings": [],
        "target_id": "hot-2",
        "outcome": "accepted_observed",
        "outcome_basis": "audit_observed_inferred_from_compact_state_delta",
    }
    assert audit_line["memory_uptake_op_outcomes"][1]["outcome"] == "accepted_observed"
    assert audit_line["memory_uptake_op_outcomes"][1]["target_id"] == "concept-1"
    assert audit_line["state_deltas"]["active_attention"] == {
        "before_count": 2,
        "after_count": 2,
        "added_ids": ["hot-2"],
        "updated_ids": ["hot-1"],
        "removed_ids": ["hot-removed"],
    }
    assert audit_line["state_deltas"]["concept_registry"]["added_ids"] == ["concept-1"]
    assert audit_line["state_deltas"]["thread_trace"]["updated_ids"] == ["thread-1"]
    assert "anchor_bank" not in audit_line["state_deltas"]
    assert audit_line["state_deltas"]["reaction_records"]["added_ids"] == ["reaction-2"]
    assert audit_line["state_deltas"]["reaction_records"]["emitted_reaction_ids"] == ["reaction-2"]


def test_record_read_writes_memory_uptake_op_contracts(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"boundary_type": "paragraph_end"},
        carry_forward_context={},
        read_result={
            "reading_impression": "A hinge appears.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [
                {
                    "op": "append",
                    "target_store": "active_attention",
                    "target_store_emitted": "",
                    "effective_target_store": "active_attention",
                    "target_key": "hot-1",
                    "compatibility_warnings": ["missing_target_store_defaulted"],
                    "payload": {
                        "source_refs": [
                            {"resolution": {"status": "matched"}},
                            {"resolution": {"status": "matched"}},
                            {"resolution": {"status": "ambiguous_first_match"}},
                        ]
                    },
                }
            ],
            "memory_uptake_admission_events": [
                {
                    "operation_index": 0,
                    "admission_status": "accepted",
                    "operation_type_emitted": "append",
                    "operation_type_normalized": "append",
                    "target_store_emitted": "",
                    "effective_target_store": "active_attention",
                    "target_key": "hot-1",
                    "item_id": "hot-1",
                    "compatibility_warnings": ["missing_target_store_defaulted"],
                    "drop_reason": "",
                    "target_store_supported": True,
                    "operation_store_policy": "supported",
                    "policy_warnings": [],
                },
                {
                    "operation_index": 1,
                    "admission_status": "dropped_unknown_operation",
                    "operation_type_emitted": "invent",
                    "operation_type_normalized": "invent",
                    "target_store_emitted": "concept_registry",
                    "effective_target_store": "concept_registry",
                    "target_key": "concept-1",
                    "item_id": "concept-1",
                    "compatibility_warnings": [],
                    "drop_reason": "unknown_operation_type",
                },
            ],
        },
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["memory_uptake_ops"][0]["target_store"] == "active_attention"
    assert audit_line["memory_uptake_op_count"] == 1
    assert audit_line["memory_uptake_ops_by_target_store"] == {"active_attention": 1}
    assert audit_line["memory_uptake_op_contracts"] == [
        {
            "operation_index": 0,
            "operation_type": "append",
            "target_store_emitted": "",
            "effective_target_store": "active_attention",
            "target_key": "hot-1",
            "item_id": "hot-1",
            "source_ref_count": 3,
            "source_ref_resolution_statuses": ["matched", "ambiguous_first_match"],
            "compatibility_warnings": ["missing_target_store_defaulted"],
        }
    ]
    assert audit_line["memory_uptake_admission_events"] == [
        {
            "operation_index": 0,
            "admission_status": "accepted",
            "operation_type_emitted": "append",
            "operation_type_normalized": "append",
            "target_store_emitted": "",
            "effective_target_store": "active_attention",
            "target_key": "hot-1",
            "item_id": "hot-1",
            "compatibility_warnings": ["missing_target_store_defaulted"],
            "drop_reason": "",
            "target_store_supported": True,
            "operation_store_policy": "supported",
            "policy_warnings": [],
        },
        {
            "operation_index": 1,
            "admission_status": "dropped_unknown_operation",
            "operation_type_emitted": "invent",
            "operation_type_normalized": "invent",
            "target_store_emitted": "concept_registry",
            "effective_target_store": "concept_registry",
            "target_key": "concept-1",
            "item_id": "concept-1",
            "compatibility_warnings": [],
            "drop_reason": "unknown_operation_type",
        },
    ]
    assert "supplemental_retrieval" not in audit_line
    assert "navigation_trace" not in audit_line


def test_record_read_writes_compact_navigation(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"boundary_type": "paragraph_end"},
        carry_forward_context={},
        read_result={
            "reading_impression": "A mainline unit lands.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "memory_uptake_admission_events": [],
        },
        navigation_trace=[
            {
                "decision": "choose_unit",
                "selection_mode": "mainline",
                "reason": "The next source unit is ready.",
                "budget_state": {"mode": "mainline", "act_index": 1},
                "continuity_cost": "not_assessed",
                "extra_marker": "ignored",
            },
        ],
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["memory_uptake_ops"] == []
    assert audit_line["memory_uptake_op_count"] == 0
    assert audit_line["memory_uptake_ops_by_target_store"] == {}
    assert audit_line["navigation_trace"][0]["decision"] == "choose_unit"
    assert audit_line["navigation_trace"][0]["selection_mode"] == "mainline"
    assert set(audit_line["navigation_trace"][0]) == {
        "decision",
        "selection_mode",
        "reason",
        "budget_state",
        "continuity_cost",
    }


def test_record_read_writes_source_context_retrieval_audit(tmp_path: Path) -> None:
    """Source-context retrieval audit keeps compact availability metadata."""

    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"boundary_type": "paragraph_end"},
        carry_forward_context={},
        context_request={"kind": "source_context", "reason": "Need exact wording."},
        supplemental_context={
            "kind": "source_context",
            "reason": "Need exact wording.",
            "retrieval_intent": "source_calibration",
            "result_boundary": "source_refs_and_excerpts",
            "result_groups": ["source_refs", "excerpts", "refs"],
            "retrieval_events": [
                {
                    "kind": "source_context",
                    "retrieval_intent": "source_calibration",
                    "result_boundary": "source_refs_and_excerpts",
                    "result_groups": ["source_refs", "excerpts", "refs"],
                }
            ],
            "source_refs": [{"source_span_id": "src:c1:p1", "quote": "Alpha sentence."}],
            "excerpts": [{"ref_id": "source:alpha", "source_span_id": "src:c1:p1", "text": "Alpha sentence."}],
            "refs": [{"ref_id": "source:alpha", "kind": "source", "source_span_id": "src:c1:p1"}],
        },
        supplemental_satisfied=True,
        supplemental_steps=[{"kind": "source_context", "status": "resolved"}],
        read_result={
            "reading_impression": "A hinge appears.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "memory_uptake_admission_events": [],
        },
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["context_request"]["kind"] == "source_context"
    assert audit_line["supplemental_ref_ids"] == ["source:alpha"]
    assert audit_line["supplemental_satisfied"] is True
    assert audit_line["supplemental_steps"] == [{"kind": "source_context", "status": "resolved"}]
    assert audit_line["memory_uptake_ops"] == []
    supplemental_retrieval = audit_line["supplemental_retrieval"]
    assert supplemental_retrieval["retrieval_intent"] == "source_calibration"
    assert supplemental_retrieval["result_boundary"] == "source_refs_and_excerpts"
    assert supplemental_retrieval["result_groups"] == ["source_refs", "excerpts", "refs"]
    assert supplemental_retrieval["forwarded_result_groups"] == ["source_refs", "excerpts", "refs"]
    assert supplemental_retrieval["not_forwarded_result_groups"] == []
    assert supplemental_retrieval["supplemental_refs_returned"] == {"count": 2, "ref_ids": ["source:alpha", "src:c1:p1"]}
    assert supplemental_retrieval["supplemental_refs_forwarded_to_prompt"] == {
        "count": 2,
        "ref_ids": ["source:alpha", "src:c1:p1"],
    }
    assert supplemental_retrieval["source_refs_available"] == {"count": 2, "ref_ids": ["source:alpha", "src:c1:p1"]}
    assert supplemental_retrieval["memory_refs_available"] == {"count": 0, "ref_ids": []}
    assert supplemental_retrieval["visible_trace_refs_available"] == {"count": 0, "ref_ids": []}
    assert supplemental_retrieval["utilization_observed"] is False
    assert supplemental_retrieval["utilization_basis"] == "not_claimed_by_read_output"


def test_record_read_writes_sparse_memory_context_retrieval_audit(tmp_path: Path) -> None:
    """Memory-context retrieval audit keeps metadata without forwarding full objects."""

    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"boundary_type": "paragraph_end"},
        carry_forward_context={},
        context_request={"kind": "memory_context", "reason": "Need prior memory."},
        supplemental_context={
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
            "concepts": [{"ref_id": "concept:promise", "concept_key": "promise"}],
            "refs": [{"ref_id": "concept:promise", "kind": "concept", "summary": "A promise remains active."}],
        },
        supplemental_satisfied=True,
        supplemental_steps=[{"kind": "memory_context", "status": "resolved"}],
        read_result={
            "reading_impression": "A hinge appears.",
            "surfaced_reactions": [{"reaction_id": "reaction-1", "thought": "Still not proof of utilization."}],
            "memory_uptake_ops": [],
            "memory_uptake_admission_events": [],
        },
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())
    supplemental_retrieval = audit_line["supplemental_retrieval"]

    assert audit_line["surfaced_reaction_count"] == 1
    assert supplemental_retrieval["retrieval_intent"] == "memory_recovery"
    assert supplemental_retrieval["result_boundary"] == "settled_memory_refs_and_visible_trace_refs"
    assert supplemental_retrieval["result_groups"] == ["concepts", "refs"]
    assert supplemental_retrieval["forwarded_result_groups"] == ["refs"]
    assert supplemental_retrieval["not_forwarded_result_groups"] == ["concepts"]
    assert supplemental_retrieval["supplemental_refs_returned"] == {"count": 1, "ref_ids": ["concept:promise"]}
    assert supplemental_retrieval["supplemental_refs_forwarded_to_prompt"] == {"count": 1, "ref_ids": ["concept:promise"]}
    assert supplemental_retrieval["source_refs_available"] == {"count": 0, "ref_ids": []}
    assert supplemental_retrieval["memory_refs_available"] == {"count": 1, "ref_ids": ["concept:promise"]}
    assert supplemental_retrieval["visible_trace_refs_available"] == {"count": 0, "ref_ids": []}
    assert supplemental_retrieval["utilization_observed"] is False
    assert supplemental_retrieval["utilization_basis"] == "not_claimed_by_read_output"


def test_record_read_writes_mixed_retrieval_audit_without_semantic_reaction_memory(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"boundary_type": "paragraph_end"},
        carry_forward_context={},
        context_request={"kind": "mixed", "reason": "Need source and memory."},
        supplemental_context={
            "kind": "supplemental_bundle",
            "reason": "Need source and memory.",
            "retrieval_intent": "mixed",
            "result_boundary": "supplemental_bundle",
            "result_groups": ["source_refs", "excerpts", "refs", "concepts", "reactions"],
            "retrieval_events": [
                {
                    "kind": "source_context",
                    "retrieval_intent": "source_calibration",
                    "result_boundary": "source_refs_and_excerpts",
                    "result_groups": ["source_refs", "excerpts", "refs"],
                },
                {
                    "kind": "memory_context",
                    "retrieval_intent": "memory_recovery",
                    "result_boundary": "settled_memory_refs_and_visible_trace_refs",
                    "result_groups": ["concepts", "reactions", "refs"],
                },
            ],
            "source_refs": [{"source_span_id": "src:c1:p1", "quote": "Alpha sentence."}],
            "excerpts": [{"ref_id": "source:alpha", "source_span_id": "src:c1:p1", "text": "Alpha sentence."}],
            "concepts": [{"ref_id": "concept:promise", "concept_key": "promise"}],
            "reactions": [
                {
                    "ref_id": "reaction:reaction-1",
                    "reaction_id": "reaction-1",
                    "result_role": "visible_trace",
                    "semantic_memory": False,
                }
            ],
            "refs": [
                {"ref_id": "source:alpha", "kind": "source", "source_span_id": "src:c1:p1"},
                {"ref_id": "concept:promise", "kind": "concept"},
                {
                    "ref_id": "reaction:reaction-1",
                    "kind": "reaction",
                    "result_role": "visible_trace",
                    "semantic_memory": False,
                },
            ],
        },
        supplemental_satisfied=True,
        read_result={
            "reading_impression": "A hinge appears.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "memory_uptake_admission_events": [],
        },
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())
    supplemental_retrieval = audit_line["supplemental_retrieval"]

    assert [event["kind"] for event in supplemental_retrieval["retrieval_events"]] == ["source_context", "memory_context"]
    assert supplemental_retrieval["retrieval_intent"] == "mixed"
    assert supplemental_retrieval["result_boundary"] == "supplemental_bundle"
    assert supplemental_retrieval["forwarded_result_groups"] == ["source_refs", "excerpts", "refs"]
    assert supplemental_retrieval["not_forwarded_result_groups"] == ["concepts", "reactions"]
    assert supplemental_retrieval["supplemental_refs_returned"] == {
        "count": 4,
        "ref_ids": ["concept:promise", "reaction:reaction-1", "source:alpha", "src:c1:p1"],
    }
    assert supplemental_retrieval["supplemental_refs_forwarded_to_prompt"] == {
        "count": 4,
        "ref_ids": ["concept:promise", "reaction:reaction-1", "source:alpha", "src:c1:p1"],
    }
    assert supplemental_retrieval["source_refs_available"] == {"count": 2, "ref_ids": ["source:alpha", "src:c1:p1"]}
    assert supplemental_retrieval["memory_refs_available"] == {"count": 1, "ref_ids": ["concept:promise"]}
    assert supplemental_retrieval["visible_trace_refs_available"] == {"count": 1, "ref_ids": ["reaction:reaction-1"]}
    assert supplemental_retrieval["utilization_observed"] is False
    assert supplemental_retrieval["utilization_basis"] == "not_claimed_by_read_output"


def test_record_settlement_prefers_unclassified_for_duplicate_target_causality(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_settlement(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unit_sentence_ids=["c1-s1"],
        focal_sentence_id="c1-s1",
        memory_uptake_ops=[
            {"operation_type": "append", "target_store": "active_attention", "target_key": "hot-1"},
            {"operation_type": "update", "target_store": "active_attention", "target_key": "hot-1"},
        ],
        before_active_attention={"active_items": []},
        after_active_attention={"active_items": [{"item_id": "hot-1", "statement": "new"}]},
        before_concept_registry={"entries": []},
        after_concept_registry={"entries": []},
        before_thread_trace={"entries": []},
        after_thread_trace={"entries": []},
        before_reaction_records={"records": []},
        after_reaction_records={"records": []},
    )

    audit_line = json.loads(settlement_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert [item["outcome"] for item in audit_line["memory_uptake_op_outcomes"]] == ["unclassified", "unclassified"]
