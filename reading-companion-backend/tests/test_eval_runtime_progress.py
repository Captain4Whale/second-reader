"""Tests for eval runtime progress heartbeat snapshots."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2.runtime_progress import load_runtime_progress_snapshot


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_load_runtime_progress_snapshot_reads_run_state_and_latest_llm(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    _write_json(
        runtime_dir / "run_state.json",
        {
            "current_phase_step": "reading",
            "current_segment_ref": "14.16",
            "updated_at": "2026-04-03T09:20:32Z",
            "current_reading_activity": {
                "phase": "reading",
                "segment_ref": "14.16",
            },
        },
    )
    _write_jsonl(
        runtime_dir / "llm_standard.jsonl",
        [
            {"node": "controller_decision", "completed_at": "2026-04-03T09:20:01Z", "duration_ms": 12000},
            {"node": "reaction_emission", "completed_at": "2026-04-03T09:20:21Z", "duration_ms": 18000},
        ],
    )
    _write_jsonl(
        runtime_dir / "activity.jsonl",
        [
            {"type": "reaction_emitted", "segment_ref": "14.15", "timestamp": "2026-04-03T09:20:12Z"},
            {"type": "reaction_emitted", "segment_ref": "14.16", "timestamp": "2026-04-03T09:20:25Z"},
        ],
    )

    snapshot = load_runtime_progress_snapshot(runtime_dir)

    assert snapshot is not None
    assert snapshot.phase == "reading"
    assert snapshot.segment_ref == "14.16"
    assert snapshot.last_llm_node == "reaction_emission"
    assert snapshot.last_llm_completed_at == "2026-04-03T09:20:21Z"
    assert snapshot.last_activity_type == "reaction_emitted"
    assert snapshot.last_activity_segment_ref == "14.16"
    assert "segment=14.16" in snapshot.to_message(mechanism_key="attentional_v2")
