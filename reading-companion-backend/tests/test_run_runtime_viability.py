"""Tests for runtime-viability orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from eval.attentional_v2 import run_runtime_viability as runtime_viability


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _bootstrap_dataset(tmp_path: Path) -> tuple[Path, Path, list[str]]:
    dataset_dir = tmp_path / "dataset"
    _write_json(
        dataset_dir / "manifest.json",
        {
            "dataset_id": "demo_runtime_dataset",
            "version": "1",
            "primary_file": "chapters.jsonl",
        },
    )
    _write_jsonl(
        dataset_dir / "chapters.jsonl",
        [
            {
                "chapter_case_id": "case_a",
                "source_id": "source_a",
                "book_title": "Book A",
                "author": "Author A",
                "language_track": "en",
                "type_tags": ["narrative_reflective"],
                "role_tags": ["narrative_reflective"],
                "output_dir": "output/book-a",
                "chapter_id": 10,
                "chapter_title": "Chapter 10",
                "sentence_count": 50,
                "paragraph_count": 8,
                "candidate_position_bucket": "middle",
                "candidate_score": 6.5,
                "selection_status": "selected_v2",
                "selection_priority": 4,
                "selection_role": "narrative_reflective",
            },
            {
                "chapter_case_id": "case_b",
                "source_id": "source_b",
                "book_title": "Book B",
                "author": "Author B",
                "language_track": "zh",
                "type_tags": ["reference_heavy"],
                "role_tags": ["reference_heavy"],
                "output_dir": "output/book-b",
                "chapter_id": 11,
                "chapter_title": "Chapter 11",
                "sentence_count": 70,
                "paragraph_count": 9,
                "candidate_position_bucket": "middle",
                "candidate_score": 6.2,
                "selection_status": "selected_v2",
                "selection_priority": 5,
                "selection_role": "reference_heavy",
            },
        ],
    )
    source_manifest = tmp_path / "source_manifest.json"
    _write_json(
        source_manifest,
        {
            "books": [
                {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"},
                {"source_id": "source_b", "relative_local_path": "state/library_sources/source_b.epub"},
            ]
        },
    )
    return dataset_dir, source_manifest, ["case_a", "case_b"]


def _case_result(case: runtime_viability.ChapterCase) -> dict[str, Any]:
    return {
        "chapter_case_id": case.chapter_case_id,
        "language_track": case.language_track,
        "selection_role": case.selection_role,
        "book_title": case.book_title,
        "author": case.author,
        "source_id": case.source_id,
        "chapter_id": case.chapter_id,
        "chapter_title": case.chapter_title,
        "mechanisms": {
            "attentional_v2": {
                "mechanism_key": "attentional_v2",
                "mechanism_label": "Attentional V2",
                "output_dir": f"/tmp/{case.chapter_case_id}/attentional_v2",
                "success": True,
                "error": "",
                "duration_seconds": 1.25,
                "reaction_count": 3,
                "attention_event_count": 4,
                "run_snapshot": {
                    "status": "completed",
                    "resume_available": True,
                    "last_checkpoint_at": "2026-04-01T00:00:00Z",
                    "completed_chapters": 1,
                    "total_chapters": 1,
                },
                "integrity_summary": {
                    "passed": True,
                    "check_count": 4,
                    "failure_count": 0,
                    "warning_count": 0,
                },
                "latency_metadata": {},
                "cost_metadata": {},
            },
            "iterator_v1": {
                "mechanism_key": "iterator_v1",
                "mechanism_label": "Iterator V1",
                "output_dir": f"/tmp/{case.chapter_case_id}/iterator_v1",
                "success": True,
                "error": "",
                "duration_seconds": 0.95,
                "reaction_count": 2,
                "attention_event_count": 3,
                "run_snapshot": {
                    "status": "completed",
                    "resume_available": True,
                    "last_checkpoint_at": "2026-04-01T00:00:00Z",
                    "completed_chapters": 1,
                    "total_chapters": 1,
                },
                "integrity_summary": {},
                "latency_metadata": {},
                "cost_metadata": {},
            },
        },
    }


def test_run_benchmark_uses_case_subprocess_for_parallel_case_workers(monkeypatch, tmp_path: Path) -> None:
    dataset_dir, source_manifest, case_ids = _bootstrap_dataset(tmp_path)
    monkeypatch.setattr(runtime_viability, "resolve_worker_policy", lambda **_kwargs: SimpleNamespace(worker_count=2))
    dispatched: list[str] = []

    def fake_run_case_subprocess(case: runtime_viability.ChapterCase, *, source: dict[str, Any], run_root: Path) -> dict[str, Any]:
        assert source["source_id"] == case.source_id
        assert run_root.parent == tmp_path / "runs"
        dispatched.append(case.chapter_case_id)
        return _case_result(case)

    monkeypatch.setattr(runtime_viability, "_run_case_subprocess", fake_run_case_subprocess)
    monkeypatch.setattr(
        runtime_viability,
        "_evaluate_case",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("_evaluate_case should not run in-process")),
    )

    summary = runtime_viability.run_benchmark(
        dataset_dirs=[dataset_dir],
        source_manifest_path=source_manifest,
        runs_root=tmp_path / "runs",
        run_id="demo_runtime_parallel",
        case_ids=case_ids,
        case_workers=2,
    )

    assert set(dispatched) == set(case_ids)
    run_root = Path(summary["run_root"])
    assert (run_root / "cases" / "case_a.json").exists()
    assert (run_root / "cases" / "case_b.json").exists()
    assert (run_root / "summary" / "aggregate.json").exists()
    assert (run_root / "summary" / "report.md").exists()


def test_run_benchmark_keeps_single_worker_case_eval_in_process(monkeypatch, tmp_path: Path) -> None:
    dataset_dir, source_manifest, case_ids = _bootstrap_dataset(tmp_path)
    monkeypatch.setattr(runtime_viability, "resolve_worker_policy", lambda **_kwargs: SimpleNamespace(worker_count=1))
    evaluated: list[str] = []

    def fake_evaluate_case(case: runtime_viability.ChapterCase, *, source: dict[str, Any], run_root: Path) -> dict[str, Any]:
        assert source["source_id"] == case.source_id
        assert run_root.parent == tmp_path / "runs"
        evaluated.append(case.chapter_case_id)
        return _case_result(case)

    monkeypatch.setattr(runtime_viability, "_evaluate_case", fake_evaluate_case)
    monkeypatch.setattr(
        runtime_viability,
        "_run_case_subprocess",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("_run_case_subprocess should not be used")),
    )

    summary = runtime_viability.run_benchmark(
        dataset_dirs=[dataset_dir],
        source_manifest_path=source_manifest,
        runs_root=tmp_path / "runs",
        run_id="demo_runtime_serial",
        case_ids=case_ids,
        case_workers=1,
    )

    assert evaluated == case_ids
    run_root = Path(summary["run_root"])
    assert (run_root / "cases" / "case_a.json").exists()
    assert (run_root / "cases" / "case_b.json").exists()


def test_aggregate_reports_success_and_integrity_counts(tmp_path: Path) -> None:
    _, _, _ = _bootstrap_dataset(tmp_path)
    case_a = runtime_viability.ChapterCase(
        chapter_case_id="case_a",
        source_id="source_a",
        book_title="Book A",
        author="Author A",
        language_track="en",
        type_tags=["narrative_reflective"],
        role_tags=["narrative_reflective"],
        output_dir="output/book-a",
        chapter_id=10,
        chapter_title="Chapter 10",
        sentence_count=50,
        paragraph_count=8,
        candidate_position_bucket="middle",
        candidate_score=6.5,
        selection_status="selected_v2",
        selection_priority=4,
        selection_role="narrative_reflective",
        dataset_id="demo_dataset",
        dataset_version="1",
    )
    case_b = runtime_viability.ChapterCase(
        chapter_case_id="case_b",
        source_id="source_b",
        book_title="Book B",
        author="Author B",
        language_track="zh",
        type_tags=["reference_heavy"],
        role_tags=["reference_heavy"],
        output_dir="output/book-b",
        chapter_id=11,
        chapter_title="Chapter 11",
        sentence_count=70,
        paragraph_count=9,
        candidate_position_bucket="middle",
        candidate_score=6.2,
        selection_status="selected_v2",
        selection_priority=5,
        selection_role="reference_heavy",
        dataset_id="demo_dataset",
        dataset_version="1",
    )

    aggregate = runtime_viability._aggregate([_case_result(case_a), _case_result(case_b)])

    assert aggregate["case_count"] == 2
    assert aggregate["mechanism_summaries"]["attentional_v2"]["success_count"] == 2
    assert aggregate["mechanism_summaries"]["attentional_v2"]["integrity_failures"] == 0
    assert aggregate["mechanism_summaries"]["iterator_v1"]["success_rate"] == 1.0
