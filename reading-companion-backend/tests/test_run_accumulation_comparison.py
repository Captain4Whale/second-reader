from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from eval.attentional_v2 import run_accumulation_comparison as accumulation_comparison


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _bootstrap_window_dataset(tmp_path: Path) -> Path:
    dataset_dir = tmp_path / "windows"
    _write_json(
        dataset_dir / "manifest.json",
        {
            "dataset_id": "demo_windows",
            "family": "window_cases",
            "version": "1",
            "primary_file": "windows.jsonl",
        },
    )
    _write_jsonl(
        dataset_dir / "windows.jsonl",
        [
            {
                "window_case_id": "window_a",
                "source_id": "source_a",
                "book_title": "Book A",
                "author": "Author A",
                "output_language": "en",
                "benchmark_line": "demo",
                "window_kind": "single_chapter",
                "chapter_case_ids": ["source_a__1"],
                "chapter_ids": ["1"],
                "chapter_numbers": [1],
                "chapter_titles": ["Chapter 1"],
                "sentence_count": 12,
                "selection_group_id": "window_a",
                "selection_group_label": "Window A",
                "cross_chapter_window": {},
            }
        ],
    )
    return dataset_dir


def _bootstrap_probe_dataset(tmp_path: Path) -> Path:
    dataset_dir = tmp_path / "probes"
    _write_json(
        dataset_dir / "manifest.json",
        {
            "dataset_id": "demo_probes",
            "family": "accumulation_probes",
            "version": "1",
            "primary_file": "probes.jsonl",
        },
    )
    _write_jsonl(
        dataset_dir / "probes.jsonl",
        [
            {
                "probe_id": "probe_a",
                "window_case_id": "window_a",
                "source_id": "source_a",
                "book_title": "Book A",
                "author": "Author A",
                "output_language": "en",
                "probe_type": "carryforward",
                "selection_reason": "Test",
                "judge_focus": "Test",
                "note_provenance": [],
                "anchor_refs": [
                    {
                        "anchor_id": "a1",
                        "anchor_kind": "early",
                        "chapter_id": 1,
                        "start_sentence_id": "c1-s1",
                        "end_sentence_id": "c1-s2",
                        "excerpt_text": "Alpha hinge line. Then the argument turns.",
                    },
                    {
                        "anchor_id": "a2",
                        "anchor_kind": "late",
                        "chapter_id": 1,
                        "start_sentence_id": "c1-s3",
                        "end_sentence_id": "c1-s4",
                        "excerpt_text": "Later the hinge returns with force.",
                    },
                ],
            }
        ],
    )
    return dataset_dir


def _bootstrap_source_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "sources.json"
    _write_json(
        manifest,
        {
            "books": [
                {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"},
            ]
        },
    )
    return manifest


def _bootstrap_formal_manifest(
    tmp_path: Path,
    *,
    window_dataset: Path | None = None,
    probe_dataset: Path | None = None,
    source_manifest: Path | None = None,
    probe_ids: list[str],
) -> Path:
    resolved_window_dataset = window_dataset or (tmp_path / "windows")
    resolved_probe_dataset = probe_dataset or (tmp_path / "probes")
    resolved_source_manifest = source_manifest or (tmp_path / "sources.json")
    manifest = tmp_path / "formal_manifest.json"
    _write_json(
        manifest,
        {
            "source_refs": {
                "window_case_datasets": [str(resolved_window_dataset.resolve())],
                "accumulation_probe_datasets": [str(resolved_probe_dataset.resolve())],
                "source_manifests": [str(resolved_source_manifest.resolve())],
            },
            "splits": {
                "accumulation_probes_frozen_draft": {"all": probe_ids},
                "insight_and_clarification_subset_frozen_draft": {"all": probe_ids},
            },
        },
    )
    return manifest


def _book_document() -> dict[str, Any]:
    return {
        "metadata": {
            "book": "Book A",
            "author": "Author A",
            "book_language": "en",
            "output_language": "en",
            "source_file": "demo.epub",
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "level": 1,
                "sentences": [
                    {"sentence_id": "c1-s1", "paragraph_index": 1, "text": "Alpha hinge line."},
                    {"sentence_id": "c1-s2", "paragraph_index": 2, "text": "Then the argument turns."},
                    {"sentence_id": "c1-s3", "paragraph_index": 3, "text": "Later the hinge returns."},
                    {"sentence_id": "c1-s4", "paragraph_index": 4, "text": "The late section sharpens the claim."},
                ],
            }
        ],
    }


def _window_case(window_case_id: str = "window_a") -> accumulation_comparison.WindowCase:
    return accumulation_comparison.WindowCase(
        window_case_id=window_case_id,
        source_id="source_a",
        book_title="Book A",
        author="Author A",
        output_language="en",
        benchmark_line="demo",
        window_kind="single_chapter",
        chapter_case_ids=["source_a__1"],
        chapter_ids=["1"],
        chapter_numbers=[1],
        chapter_titles=["Chapter 1"],
        sentence_count=12,
        selection_group_id=window_case_id,
        selection_group_label="Window A",
        cross_chapter_window={},
    )


def _probe(probe_id: str = "probe_a", window_case_id: str = "window_a") -> accumulation_comparison.Probe:
    return accumulation_comparison.Probe(
        probe_id=probe_id,
        window_case_id=window_case_id,
        source_id="source_a",
        book_title="Book A",
        author="Author A",
        output_language="en",
        probe_type="carryforward",
        anchor_refs=[],
        selection_reason="Test",
        judge_focus="Test",
        note_provenance=[],
    )


def _window_result(window_case_id: str = "window_a") -> dict[str, Any]:
    base_bundle = {
        "reactions": [
            {
                "type": "discern",
                "section_ref": "1.1",
                "anchor_quote": "Alpha hinge line.",
                "content": "Early hinge noted.",
            },
            {
                "type": "return",
                "section_ref": "1.3",
                "anchor_quote": "Later the hinge returns.",
                "content": "Late hinge reuse noted.",
            },
        ],
        "attention_events": [
            {
                "kind": "thought",
                "phase": "thinking",
                "section_ref": "1.1",
                "message": "Early hinge matters.",
                "current_excerpt": "Alpha hinge line.",
            },
            {
                "kind": "thought",
                "phase": "thinking",
                "section_ref": "1.3",
                "message": "The later turn carries the earlier hinge forward.",
                "current_excerpt": "Later the hinge returns.",
            },
        ],
        "chapters": [{"chapter_id": 1, "chapter_ref": "Chapter 1"}],
        "memory_summaries": ["Memory"],
    }
    return {
        "window_case_id": window_case_id,
        "source_id": "source_a",
        "output_language": "en",
        "book_title": "Book A",
        "author": "Author A",
        "chapter_case_ids": ["source_a__1"],
        "mechanisms": {
            "attentional_v2": {
                "status": "completed",
                "mechanism_key": "attentional_v2",
                "mechanism_label": "Attentional V2",
                "output_dir": "/tmp/window_a/attentional_v2",
                "normalized_eval_bundle": base_bundle,
                "bundle_summary": {},
                "error": "",
            },
            "iterator_v1": {
                "status": "completed",
                "mechanism_key": "iterator_v1",
                "mechanism_label": "Iterator V1",
                "output_dir": "/tmp/window_a/iterator_v1",
                "normalized_eval_bundle": base_bundle,
                "bundle_summary": {},
                "error": "",
            },
        },
    }








def test_existing_bundle_payload_recovers_from_completed_unit_payload(tmp_path: Path) -> None:
    run_root = tmp_path / "runs" / "acc_recover_demo"
    _write_json(
        run_root / "shards" / "seed" / "units" / "window_a.json",
        _window_result(),
    )

    recovered = accumulation_comparison._existing_bundle_payload(
        run_root,
        window_case_id="window_a",
        mechanism_key="attentional_v2",
    )

    assert recovered is not None
    assert (run_root / "shards" / "seed" / "bundles" / "attentional_v2" / "window_a.json").exists()
    assert recovered[1]["status"] == "completed"
    assert recovered[1]["normalized_eval_bundle"]["reactions"]


def test_existing_bundle_payload_does_not_promote_raw_output_dir_without_completed_window(tmp_path: Path) -> None:
    run_root = tmp_path / "runs" / "acc_no_raw_output_recover_demo"
    output_dir = run_root / "shards" / "seed" / "outputs" / "window_a" / "iterator_v1"
    _write_json(
        output_dir / "_mechanisms" / "iterator_v1" / "exports" / "normalized_eval_bundle.json",
        {
            "mechanism_key": "iterator_v1",
            "mechanism_label": "Iterator V1",
            "reactions": [{"content": "Partial chapter export only"}],
            "attention_events": [],
            "chapters": [{"chapter_id": 1, "chapter_ref": "Chapter 1"}],
            "memory_summaries": [],
        },
    )

    recovered = accumulation_comparison._existing_bundle_payload(
        run_root,
        window_case_id="window_a",
        mechanism_key="iterator_v1",
    )

    assert recovered is None






def test_judge_target_retries_once_after_schema_invalid_payload(monkeypatch, tmp_path: Path) -> None:
    probe = _probe()
    window = _window_case()
    mechanisms = {
        "status": "completed",
        "local_evidence": {"evidence": "demo"},
    }
    payloads = iter(
        [
            {"winner": "attentional_v2"},
            {
                "winner": "attentional_v2",
                "confidence": "high",
                "scores": {
                    "attentional_v2": {key: 4 for key in accumulation_comparison.INSIGHT_SCORE_KEYS},
                    "iterator_v1": {key: 2 for key in accumulation_comparison.INSIGHT_SCORE_KEYS},
                },
                "reason": "fresh_rejudge",
            },
        ]
    )
    user_prompts: list[str] = []

    monkeypatch.setattr(accumulation_comparison, "llm_invocation_scope", lambda **_kwargs: nullcontext())
    monkeypatch.setattr(accumulation_comparison, "eval_trace_context", lambda *_args, **_kwargs: None)

    def fake_invoke_json(system_prompt: str, user_prompt: str, default: Any, *, profile_id: str | None = None) -> Any:
        user_prompts.append(user_prompt)
        return next(payloads)

    monkeypatch.setattr(accumulation_comparison, "invoke_json", fake_invoke_json)

    judgment = accumulation_comparison._judge_target(
        target_name="insight_and_clarification",
        probe=probe,
        window=window,
        attentional=mechanisms,
        iterator=mechanisms,
        run_root=tmp_path / "run",
        judge_mode="llm",
        shard_id="main",
    )

    assert len(user_prompts) == 2
    assert "Reminder: return exactly one JSON object matching the requested schema." in user_prompts[1]
    assert judgment["winner"] == "attentional_v2"
    assert judgment["reason"] == "fresh_rejudge"
