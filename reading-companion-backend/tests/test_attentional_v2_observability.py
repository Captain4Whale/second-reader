from __future__ import annotations

import json
from pathlib import Path

from src.attentional_v2.observability import record_settlement
from src.attentional_v2.storage import settlement_audit_file


def test_record_settlement_writes_compact_state_deltas(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    record_settlement(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        unit_sentence_ids=["c1-s1", "c1-s2"],
        focal_sentence_id="c1-s2",
        memory_uptake_ops=[
            {"operation_type": "append", "target_store": "active_attention", "target_key": "hot-2"},
            {"operation_type": "update", "target_store": "concept_registry", "item_id": "concept-1"},
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
