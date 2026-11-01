"""Tests for the dedicated subsegment benchmark harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval.common.taxonomy import (
    DETERMINISTIC_METRICS,
    DIRECT_QUALITY,
    LOCAL_IMPACT,
    PAIRWISE_JUDGE,
    TARGET_SUBSEGMENT_SEGMENTATION,
    normalize_method,
    normalize_scope,
    normalize_scopes,
    validate_target_slug,
)
from eval.subsegment.dataset import load_benchmark_dataset
from eval.subsegment.report import build_markdown_report


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


def _direct_plan_result(case_id: str, strategy: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    if strategy == "heuristic_only":
        plan = [
            {"summary": "Heuristic part 1", "text": "Alpha.", "sentence_start": 1, "sentence_end": 1},
            {"summary": "Heuristic part 2", "text": "Beta.", "sentence_start": 2, "sentence_end": 2},
        ]
        planner_source = "fallback"
        diagnostics = {
            "strategy_requested": "heuristic_only",
            "planner_status": "forced_heuristic",
            "planner_failure_reason": "strategy_override",
            "validation_status": "not_run",
            "planner_payload": {},
            "materialized_unit_count": 2,
        }
    else:
        plan = [{"summary": "LLM unit", "text": "Alpha. Beta.", "sentence_start": 1, "sentence_end": 2}]
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
    final_state = {
        "segment_id": case_id,
        "subsegment_plan": plan,
        "subsegment_planner_source": planner_source,
        "subsegment_plan_diagnostics": diagnostics,
        "budget": {"segment_timed_out": False},
    }
    return plan, final_state


def test_validate_target_slug_accepts_snake_case():
    assert validate_target_slug(TARGET_SUBSEGMENT_SEGMENTATION) == TARGET_SUBSEGMENT_SEGMENTATION
    assert normalize_scope(DIRECT_QUALITY) == DIRECT_QUALITY
    assert normalize_method(PAIRWISE_JUDGE) == PAIRWISE_JUDGE
    assert normalize_scopes([DIRECT_QUALITY, LOCAL_IMPACT, DIRECT_QUALITY]) == [DIRECT_QUALITY, LOCAL_IMPACT]


def test_validate_target_slug_rejects_invalid_values():
    with pytest.raises(ValueError):
        validate_target_slug("Subsegment Segmentation")


def test_load_benchmark_dataset_reads_manifest_and_cases(tmp_path: Path):
    """The curated benchmark dataset should load split metadata and cases together."""
    dataset = load_benchmark_dataset(_write_dataset(tmp_path))

    assert dataset.dataset_id == "subsegment_benchmark_test"
    assert dataset.core_case_ids == ["core_case"]
    assert dataset.audit_case_ids == ["audit_case"]
    assert [case.case_id for case in dataset.cases] == ["core_case", "audit_case"]


def test_build_markdown_report_summarizes_scopes():
    """The checked-in benchmark report should expose the taxonomy fields and scope headings."""
    markdown = build_markdown_report(
        dataset_id="subsegment_benchmark_test",
        dataset_version="1",
        target=TARGET_SUBSEGMENT_SEGMENTATION,
        scopes=[DIRECT_QUALITY, LOCAL_IMPACT],
        methods=[DETERMINISTIC_METRICS, PAIRWISE_JUDGE],
        comparison_target="heuristic_only vs llm_primary",
        rubric_summary_by_scope={
            DIRECT_QUALITY: ["direct rubric"],
            LOCAL_IMPACT: ["impact rubric"],
        },
        aggregate={
            "case_count": 2,
            "core_case_count": 1,
            "audit_case_count": 1,
            "dataset_case_count": 2,
            "scope_metrics": {
                DIRECT_QUALITY: {
                    "case_count": 2,
                    "llm_fallback_rate": 0.5,
                    "llm_invalid_plan_rate": 0.0,
                    "llm_failure_rate": 0.0,
                    "heuristic_failure_rate": 0.0,
                    "heuristic_avg_unit_count": 2.0,
                    "llm_avg_unit_count": 1.5,
                },
                LOCAL_IMPACT: {
                    "case_count": 2,
                    "llm_fallback_rate": 0.0,
                    "llm_invalid_plan_rate": 0.0,
                    "llm_failure_rate": 0.0,
                    "heuristic_failure_rate": 0.0,
                    "heuristic_avg_unit_count": 2.0,
                    "llm_avg_unit_count": 1.5,
                },
            },
        },
        case_results=[
            {
                "case_id": "core_case",
                "segment_ref": "1.1",
                "scope_results": {
                    DIRECT_QUALITY: {"judgment": {"winner": "llm_primary", "reason": "better direct quality"}},
                    LOCAL_IMPACT: {"judgment": {"winner": "heuristic_only", "reason": "better local impact"}},
                },
            },
            {
                "case_id": "audit_case",
                "segment_ref": "1.2",
                "scope_results": {
                    DIRECT_QUALITY: {"judgment": {"winner": "heuristic_only", "reason": "better direct quality"}},
                    LOCAL_IMPACT: {"judgment": {"winner": "tie", "reason": "roughly equal"}},
                },
            },
        ],
    )

    assert "Target: `subsegment_segmentation`" in markdown
    assert "Scope: `direct_quality`, `local_impact`" in markdown
    assert "Method: `deterministic_metrics`, `pairwise_judge`" in markdown
    assert "## Direct Quality (subsegment slicing)" in markdown
