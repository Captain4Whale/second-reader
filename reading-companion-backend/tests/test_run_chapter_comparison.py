"""Tests for chapter-comparison orchestration and case isolation."""

from __future__ import annotations

import json
from pathlib import Path
from contextlib import nullcontext
from typing import Any

import pytest

from eval.attentional_v2 import run_chapter_comparison as chapter_comparison


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
            "dataset_id": "demo_dataset",
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
                "language_track": "en",
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


def _judgment(score_keys: tuple[str, ...]) -> dict[str, Any]:
    return {
        "winner": "tie",
        "confidence": "low",
        "scores": {
            "attentional_v2": {key: 0 for key in score_keys},
            "iterator_v1": {key: 0 for key in score_keys},
        },
        "reason": "judge_disabled",
    }


def _case_result(case: chapter_comparison.ChapterCase) -> dict[str, Any]:
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
                "mechanism_label": "Attentional V2",
                "output_dir": f"/tmp/{case.chapter_case_id}/attentional_v2",
                "bundle_summary": {},
            },
            "iterator_v1": {
                "mechanism_label": "Iterator V1",
                "output_dir": f"/tmp/{case.chapter_case_id}/iterator_v1",
                "bundle_summary": {},
            },
        },
        "scope_results": {
            chapter_comparison.LOCAL_IMPACT: {
                "judgment": _judgment(
                    (
                        "text_groundedness",
                        "focus_selectivity",
                        "source_anchoring",
                        "meaningful_curiosity",
                        "local_step_quality",
                    )
                )
            },
            chapter_comparison.SYSTEM_REGRESSION: {
                "judgment": _judgment(
                    (
                        "coherent_accumulation",
                        "callback_quality",
                        "chapter_arc_clarity",
                        "memory_carryover",
                        "product_fit",
                    )
                )
            },
        },
    }






def test_build_judge_bundle_summary_substantive_filters_operational_events() -> None:
    summary = {
        "reaction_count": 1,
        "attention_event_count": 3,
        "reactions": [{"type": "discern", "content": "Reasoned move."}],
        "attention_events": [
            {"kind": "parse", "message": "Parsing..."},
            {"kind": "thought", "message": "Substantive thought."},
            {"kind": "transition", "message": "Transition."},
        ],
    }

    filtered = chapter_comparison._build_judge_bundle_summary(
        summary,
        judge_evidence_mode="substantive",
    )

    assert filtered["attention_event_count"] == 1
    assert filtered["attention_events"] == [{"kind": "thought", "message": "Substantive thought."}]
    assert filtered["reactions"] == summary["reactions"]


def test_judge_scope_uses_substantive_bundle_summary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}

    def fake_invoke_json(_system_prompt: str, user_prompt: str, _default: object) -> dict[str, Any]:
        captured["user_prompt"] = user_prompt
        return {
            "winner": "tie",
            "confidence": "low",
            "scores": {
                "attentional_v2": {
                    "text_groundedness": 3,
                    "focus_selectivity": 3,
                    "source_anchoring": 3,
                    "meaningful_curiosity": 3,
                    "local_step_quality": 3,
                },
                "iterator_v1": {
                    "text_groundedness": 3,
                    "focus_selectivity": 3,
                    "source_anchoring": 3,
                    "meaningful_curiosity": 3,
                    "local_step_quality": 3,
                },
            },
            "reason": "Tie.",
        }

    monkeypatch.setattr(chapter_comparison, "invoke_json", fake_invoke_json)
    monkeypatch.setattr(chapter_comparison, "llm_invocation_scope", lambda **kwargs: nullcontext())

    case = chapter_comparison.ChapterCase(
        chapter_case_id="case_a",
        source_id="source_a",
        book_title="Book A",
        author="Author A",
        language_track="en",
        type_tags=["narrative_reflective"],
        role_tags=["narrative_reflective"],
        output_dir="output/book-a",
        chapter_id=1,
        chapter_title="Chapter 1",
        sentence_count=10,
        paragraph_count=2,
        candidate_position_bucket="middle",
        candidate_score=5.0,
        selection_status="selected_v2",
        selection_priority=1,
        selection_role="narrative_reflective",
        dataset_id="demo_dataset",
        dataset_version="1",
    )
    attentional = {
        "bundle_summary": {
            "reaction_count": 1,
            "attention_event_count": 2,
            "reactions": [{"type": "discern", "content": "Attentional reading."}],
            "attention_events": [
                {"kind": "thought", "message": "Attentional thought."},
                {"kind": "parse", "message": "Should disappear."},
            ],
        }
    }
    iterator = {
        "bundle_summary": {
            "reaction_count": 1,
            "attention_event_count": 2,
            "reactions": [{"type": "discern", "content": "Iterator reading."}],
            "attention_events": [
                {"kind": "parse", "message": "Should disappear too."},
                {"kind": "thought", "message": "Iterator thought."},
            ],
        }
    }

    judgment = chapter_comparison._judge_scope(
        scope=chapter_comparison.LOCAL_IMPACT,
        case=case,
        attentional=attentional,
        iterator=iterator,
        run_root=tmp_path,
        judge_mode="llm",
        judge_evidence_mode="substantive",
    )

    assert judgment["winner"] == "tie"
    assert "Should disappear" not in captured["user_prompt"]
    assert "Attentional thought." in captured["user_prompt"]
    assert "Iterator thought." in captured["user_prompt"]
