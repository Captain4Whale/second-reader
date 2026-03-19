"""Tests for the dedicated subsegment benchmark harness."""

from __future__ import annotations

import json
from pathlib import Path

from eval.subsegment.dataset import load_benchmark_dataset
from eval.subsegment.report import build_markdown_report
from eval.subsegment.run_benchmark import run_benchmark


def _write_dataset(tmp_path: Path) -> Path:
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    (dataset_dir / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": "subsegment_benchmark_test",
                "version": "1",
                "description": "test dataset",
                "default_user_intent": "Read carefully.",
                "case_file": "cases.jsonl",
                "core_case_ids": ["core_case"],
                "audit_case_ids": ["audit_case"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    cases = [
        {
            "case_id": "core_case",
            "split": "core",
            "source": {"kind": "fixture", "path": "fixture.json"},
            "book_title": "Fixture Book",
            "author": "Fixture Author",
            "output_language": "en",
            "chapter_title": "Chapter 1",
            "chapter_ref": "Chapter 1",
            "chapter_index": 1,
            "total_chapters": 1,
            "primary_role": "body",
            "role_tags": [],
            "role_confidence": "medium",
            "section_heading": "",
            "nearby_outline": [],
            "segment_id": "1.1",
            "segment_ref": "1.1",
            "segment_summary": "Core summary",
            "segment_text": "Alpha. Beta.",
            "tags": ["core"],
            "notes": "core case",
        },
        {
            "case_id": "audit_case",
            "split": "audit",
            "source": {"kind": "fixture", "path": "fixture.json"},
            "book_title": "Fixture Book",
            "author": "Fixture Author",
            "output_language": "en",
            "chapter_title": "Chapter 1",
            "chapter_ref": "Chapter 1",
            "chapter_index": 1,
            "total_chapters": 1,
            "primary_role": "body",
            "role_tags": [],
            "role_confidence": "medium",
            "section_heading": "",
            "nearby_outline": [],
            "segment_id": "1.2",
            "segment_ref": "1.2",
            "segment_summary": "Audit summary",
            "segment_text": "Gamma. Delta.",
            "tags": ["audit"],
            "notes": "audit case",
        },
    ]
    (dataset_dir / "cases.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in cases) + "\n",
        encoding="utf-8",
    )
    return dataset_dir


def test_load_benchmark_dataset_reads_manifest_and_cases(tmp_path: Path):
    """The curated benchmark dataset should load split metadata and cases together."""
    dataset = load_benchmark_dataset(_write_dataset(tmp_path))

    assert dataset.dataset_id == "subsegment_benchmark_test"
    assert dataset.core_case_ids == ["core_case"]
    assert dataset.audit_case_ids == ["audit_case"]
    assert [case.case_id for case in dataset.cases] == ["core_case", "audit_case"]


def test_build_markdown_report_summarizes_winners():
    """The checked-in benchmark report should summarize aggregate winners and caveats."""
    markdown = build_markdown_report(
        dataset_id="subsegment_benchmark_test",
        comparison_target="heuristic_only vs llm_primary",
        rubric_summary=["plan quality", "downstream quality"],
        aggregate={
            "case_count": 2,
            "core_case_count": 1,
            "audit_case_count": 1,
            "llm_fallback_rate": 0.5,
            "llm_invalid_plan_rate": 0.0,
            "llm_failure_rate": 0.0,
            "heuristic_avg_unit_count": 2.0,
            "llm_avg_unit_count": 1.5,
        },
        case_results=[
            {
                "case_id": "core_case",
                "segment_ref": "1.1",
                "plan_judgment": {"winner": "llm_primary"},
                "downstream_judgment": {"winner": "llm_primary", "reason": "better focus"},
            },
            {
                "case_id": "audit_case",
                "segment_ref": "1.2",
                "plan_judgment": {"winner": "heuristic_only"},
                "downstream_judgment": {"winner": "tie", "reason": "roughly equal"},
            },
        ],
    )

    assert "# Subsegment Benchmark Report: subsegment_benchmark_test" in markdown
    assert "`llm_primary`: 1" in markdown
    assert "Known Caveats" in markdown


def test_run_benchmark_writes_isolated_artifacts_and_report(tmp_path: Path, monkeypatch):
    """Benchmark runs should write only under eval-local run roots and the chosen report path."""
    dataset_dir = _write_dataset(tmp_path)
    runs_root = tmp_path / "runs"
    report_path = tmp_path / "report.md"

    def fake_run_reader_segment(state, progress=None):  # noqa: ANN001
        strategy = state.get("subsegment_strategy_override") or "llm_primary"
        if strategy == "heuristic_only":
            planner_source = "fallback"
            diagnostics = {
                "strategy_requested": "heuristic_only",
                "planner_status": "forced_heuristic",
                "planner_failure_reason": "strategy_override",
                "validation_status": "not_run",
                "planner_payload": {},
                "materialized_unit_count": 2,
            }
            plan = [
                {"summary": "Heuristic part 1", "text": "Alpha.", "sentence_start": 1, "sentence_end": 1},
                {"summary": "Heuristic part 2", "text": "Beta.", "sentence_start": 2, "sentence_end": 2},
            ]
        else:
            planner_source = "llm"
            diagnostics = {
                "strategy_requested": "llm_primary",
                "planner_attempted": True,
                "planner_status": "ok",
                "planner_failure_reason": "",
                "validation_status": "ok",
                "planner_payload": {"units": []},
                "materialized_unit_count": 1,
            }
            plan = [{"summary": "LLM unit", "text": "Alpha. Beta.", "sentence_start": 1, "sentence_end": 2}]
        final_state = {
            "subsegment_plan": plan,
            "subsegment_planner_source": planner_source,
            "subsegment_plan_diagnostics": diagnostics,
            "budget": {"segment_timed_out": False},
        }
        rendered = {
            "segment_id": state["segment_id"],
            "summary": state["segment_summary"],
            "verdict": "pass",
            "reactions": [
                {
                    "type": "highlight",
                    "anchor_quote": plan[0]["text"],
                    "content": f"note::{strategy}",
                    "search_results": [],
                }
            ],
            "reflection_summary": f"summary::{strategy}",
            "reflection_reason_codes": ["OTHER"],
        }
        return rendered, final_state

    monkeypatch.setattr("eval.subsegment.run_benchmark.run_reader_segment", fake_run_reader_segment)

    summary = run_benchmark(
        dataset_dir=dataset_dir,
        runs_root=runs_root,
        report_path=report_path,
        run_id="test-run",
        judge_mode="llm",
        plan_judge=lambda **_kwargs: {"winner": "llm_primary", "reason": "better plan"},
        downstream_judge=lambda **_kwargs: {"winner": "llm_primary", "reason": "better output"},
    )

    run_root = Path(summary["run_root"])
    assert (run_root / "inputs" / "core_case.json").exists()
    assert (run_root / "plans" / "core_case.llm_primary.json").exists()
    assert (run_root / "sections" / "core_case.heuristic_only.json").exists()
    assert (run_root / "judge" / "core_case.plan.json").exists()
    assert (run_root / "summary" / "aggregate.json").exists()
    assert (run_root / "runtime").exists()
    assert report_path.exists()
    assert not (tmp_path / "output").exists()
    assert not (tmp_path / "state").exists()


def test_run_benchmark_records_invalid_plan_fallback(tmp_path: Path, monkeypatch):
    """The harness should preserve invalid-plan fallback evidence in aggregate artifacts."""
    dataset_dir = _write_dataset(tmp_path)

    def fake_run_reader_segment(state, progress=None):  # noqa: ANN001
        strategy = state.get("subsegment_strategy_override") or "llm_primary"
        diagnostics = {
            "strategy_requested": strategy,
            "planner_attempted": strategy == "llm_primary",
            "planner_status": "ok" if strategy == "llm_primary" else "forced_heuristic",
            "planner_failure_reason": "invalid_reading_move" if strategy == "llm_primary" else "strategy_override",
            "validation_status": "invalid_reading_move" if strategy == "llm_primary" else "not_run",
            "planner_payload": {"units": []},
            "materialized_unit_count": 2,
        }
        final_state = {
            "subsegment_plan": [{"summary": "Fallback", "text": "Alpha."}, {"summary": "Fallback", "text": "Beta."}],
            "subsegment_planner_source": "fallback",
            "subsegment_plan_diagnostics": diagnostics,
            "budget": {"segment_timed_out": False},
        }
        rendered = {
            "segment_id": state["segment_id"],
            "summary": state["segment_summary"],
            "verdict": "pass",
            "reactions": [],
            "reflection_summary": "ok",
            "reflection_reason_codes": ["OTHER"],
        }
        return rendered, final_state

    monkeypatch.setattr("eval.subsegment.run_benchmark.run_reader_segment", fake_run_reader_segment)

    summary = run_benchmark(
        dataset_dir=dataset_dir,
        runs_root=tmp_path / "runs",
        report_path=tmp_path / "report.md",
        run_id="invalid-plan-run",
        judge_mode="none",
    )

    assert summary["aggregate"]["llm_invalid_plan_rate"] == 1.0
