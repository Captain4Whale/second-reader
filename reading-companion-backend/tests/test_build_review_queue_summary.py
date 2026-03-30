"""Tests for stable review queue summary writes."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import build_review_queue_summary as module


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_main_preserves_existing_generated_at_when_queue_is_unchanged(tmp_path: Path, monkeypatch) -> None:
    pending_root = tmp_path / "eval" / "review_packets" / "pending"
    pending_root.mkdir(parents=True, exist_ok=True)
    output_json = tmp_path / "eval" / "review_packets" / "review_queue_summary.json"
    output_md = tmp_path / "eval" / "review_packets" / "review_queue_summary.md"

    _write_json(
        output_json,
        {
            "generated_at": "2026-03-30T05:40:41.826004Z",
            "active_packet_count": 0,
            "packets": [],
        },
    )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(
        "# Review Queue Summary\n\nGenerated: `2026-03-30T05:40:41.826004Z`\n\nActive packets: `0`\n\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(module, "PENDING_ROOT", pending_root)
    monkeypatch.setattr(module, "OUTPUT_JSON", output_json)
    monkeypatch.setattr(module, "OUTPUT_MD", output_md)

    assert module.main() == 0

    summary = json.loads(output_json.read_text(encoding="utf-8"))
    assert summary["generated_at"] == "2026-03-30T05:40:41.826004Z"
    assert summary["active_packet_count"] == 0
    assert summary["packets"] == []
    assert "Generated: `2026-03-30T05:40:41.826004Z`" in output_md.read_text(encoding="utf-8")


def test_main_refreshes_generated_at_when_queue_state_changes(tmp_path: Path, monkeypatch) -> None:
    pending_root = tmp_path / "eval" / "review_packets" / "pending"
    packet_dir = pending_root / "packet_demo"
    packet_dir.mkdir(parents=True, exist_ok=True)
    output_json = tmp_path / "eval" / "review_packets" / "review_queue_summary.json"
    output_md = tmp_path / "eval" / "review_packets" / "review_queue_summary.md"
    runs_root = tmp_path / "eval" / "runs" / "attentional_v2" / "case_audits"
    runs_root.mkdir(parents=True, exist_ok=True)

    _write_json(
        output_json,
        {
            "generated_at": "2026-03-30T05:40:41.826004Z",
            "active_packet_count": 0,
            "packets": [],
        },
    )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(
        "# Review Queue Summary\n\nGenerated: `2026-03-30T05:40:41.826004Z`\n\nActive packets: `0`\n\n",
        encoding="utf-8",
    )
    _write_json(
        packet_dir / "packet_manifest.json",
        {
            "packet_id": "packet_demo",
            "created_at": "2026-03-30T12:00:00Z",
            "dataset_id": "demo_dataset",
            "family": "excerpt_cases",
            "storage_mode": "local-only",
            "case_count": 2,
            "selection_filters": {"statuses": ["needs_revision"]},
        },
    )

    monkeypatch.setattr(module, "PENDING_ROOT", pending_root)
    monkeypatch.setattr(module, "RUNS_ROOT", runs_root)
    monkeypatch.setattr(module, "OUTPUT_JSON", output_json)
    monkeypatch.setattr(module, "OUTPUT_MD", output_md)

    assert module.main() == 0

    summary = json.loads(output_json.read_text(encoding="utf-8"))
    assert summary["generated_at"] != "2026-03-30T05:40:41.826004Z"
    assert summary["active_packet_count"] == 1
    assert summary["packets"][0]["packet_id"] == "packet_demo"
