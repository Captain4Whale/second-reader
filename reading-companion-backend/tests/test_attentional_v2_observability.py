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

    assert audit_line["memory_uptake_op_count"] == 1
    assert audit_line["memory_uptake_ops_by_target_store"] == {"active_attention": 1}
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
    assert audit_line["state_deltas"]["active_attention"] == {
        "before_count": 2,
        "after_count": 2,
        "added_ids": ["hot-2"],
        "updated_ids": ["hot-1"],
        "removed_ids": ["hot-removed"],
    }
    assert "anchor_bank" not in audit_line["state_deltas"]
    assert audit_line["state_deltas"]["reaction_records"]["added_ids"] == ["reaction-2"]
    assert audit_line["state_deltas"]["reaction_records"]["emitted_reaction_ids"] == ["reaction-2"]


def test_record_read_writes_memory_uptake_op_contracts(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"reason": "test boundary"},
        carry_forward_context={},
        digest_result={
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
                    "target_store_emitted": "unsupported_store",
                    "effective_target_store": "unsupported_store",
                    "target_key": "ignored-1",
                    "item_id": "ignored-1",
                    "compatibility_warnings": [],
                    "drop_reason": "unknown_operation_type",
                },
            ],
        },
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["digest_result"]["reading_impression"] == "A hinge appears."
    assert audit_line["digest_result"]["memory_uptake_ops"][0]["target_store"] == "active_attention"
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
            "target_store_emitted": "unsupported_store",
            "effective_target_store": "unsupported_store",
            "target_key": "ignored-1",
            "item_id": "ignored-1",
            "compatibility_warnings": [],
            "drop_reason": "unknown_operation_type",
        },
    ]
    assert "ingest_trace" not in audit_line


def test_record_read_writes_compact_ingest_trace(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_read(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unitize_decision={"reason": "test boundary"},
        carry_forward_context={},
        digest_result={
            "reading_impression": "A mainline unit lands.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "memory_uptake_admission_events": [],
        },
        ingest_trace=[
            {
                "reason": "The next source unit is ready.",
                "continuity_cost": "not_assessed",
                "extra_marker": "ignored",
            },
        ],
    )

    audit_line = json.loads(read_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert audit_line["digest_result"] == {
        "reading_impression": "A mainline unit lands.",
        "surfaced_reactions": [],
        "memory_uptake_ops": [],
        "memory_uptake_admission_events": [],
    }
    assert audit_line["memory_uptake_ops"] == []
    assert audit_line["memory_uptake_op_count"] == 0
    assert audit_line["memory_uptake_ops_by_target_store"] == {}
    assert set(audit_line["ingest_trace"][0]) == {
        "reason",
        "continuity_cost",
    }


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
        before_reaction_records={"records": []},
        after_reaction_records={"records": []},
    )

    audit_line = json.loads(settlement_audit_file(output_dir).read_text(encoding="utf-8").strip())

    assert [item["outcome"] for item in audit_line["memory_uptake_op_outcomes"]] == ["unclassified", "unclassified"]
