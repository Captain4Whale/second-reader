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
