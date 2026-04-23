from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import run_long_span_vnext as runner
from src.attentional_v2.benchmark_probes import (
    is_memory_quality_probe_export_complete,
    load_memory_quality_probe_export,
    persist_due_memory_quality_probe_snapshots,
)
from src.attentional_v2.schemas import (
    build_empty_anchor_bank,
    build_empty_concept_registry,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_move_history,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
    build_empty_working_state,
)
from src.attentional_v2.storage import initialize_artifact_tree, memory_quality_probe_export_file


def _window() -> runner.ReadingWindow:
    return runner.ReadingWindow(
        segment_id="segment_a",
        source_id="source_a",
        book_title="Book A",
        author="Author A",
        language_track="en",
        start_sentence_id="c1-s1",
        end_sentence_id="c1-s5",
        source_chapter_ids=[1],
        chapter_titles=["Chapter 1"],
        target_note_count=20,
        covered_note_count=20,
        termination_reason="chapter_end_after_target_notes",
        segment_source_path="segment_sources/segment_a.txt",
    )


def _book_document() -> dict[str, object]:
    return {
        "metadata": {"book": "Book A"},
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "paragraphs": [
                    {"paragraph_index": 1, "text": "Alpha. Beta."},
                    {"paragraph_index": 2, "text": "Gamma. Delta."},
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "paragraph_index": 1,
                        "text": "Alpha.",
                        "locator": {"paragraph_index": 1, "char_end": 6},
                    },
                    {
                        "sentence_id": "c1-s2",
                        "paragraph_index": 1,
                        "text": "Beta.",
                        "locator": {"paragraph_index": 1, "char_end": 12},
                    },
                    {
                        "sentence_id": "c1-s3",
                        "paragraph_index": 2,
                        "text": "Gamma.",
                        "locator": {"paragraph_index": 2, "char_end": 6},
                    },
                    {
                        "sentence_id": "c1-s4",
                        "paragraph_index": 2,
                        "text": "Delta.",
                        "locator": {"paragraph_index": 2, "char_end": 13},
                    },
                ],
            }
        ],
    }


def test_persist_due_memory_quality_probe_snapshots_emits_once_per_threshold(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    initialize_artifact_tree(output_dir)

    local_buffer = build_empty_local_buffer()
    local_buffer["recent_sentences"] = [
        {"sentence_id": "c1-s1"},
        {"sentence_id": "c1-s2"},
        {"sentence_id": "c1-s3"},
        {"sentence_id": "c1-s4"},
    ]
    local_buffer["recent_meaning_units"] = [["c1-s1", "c1-s2"], ["c1-s3", "c1-s4"]]
    local_continuity = build_empty_local_continuity()
    local_continuity["chapter_ref"] = "Chapter 1"
    local_continuity["current_sentence_id"] = "c1-s4"
    local_continuity["reading_queue_stage"] = "mainline"

    settings = {
        "enabled": True,
        "segment_id": "segment_a",
        "source_id": "source_a",
        "book_title": "Book A",
        "language_track": "en",
        "threshold_ratios": [0.2, 0.4, 0.6, 0.8, 1.0],
    }
    ordered_sentence_ids = ["c1-s1", "c1-s2", "c1-s3", "c1-s4", "c1-s5"]

    first = persist_due_memory_quality_probe_snapshots(
        output_dir=output_dir,
        settings=settings,
        ordered_sentence_ids=ordered_sentence_ids,
        actual_sentence_id="c1-s4",
        chapter_ref="Chapter 1",
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        working_state=build_empty_working_state(),
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        anchor_bank=build_empty_anchor_bank(),
        move_history=build_empty_move_history(),
        reaction_records=build_empty_reaction_records(),
    )

    assert len(first) == 4
    payload = load_memory_quality_probe_export(output_dir)
    assert len(payload["snapshots"]) == 4

    second = persist_due_memory_quality_probe_snapshots(
        output_dir=output_dir,
        settings=settings,
        ordered_sentence_ids=ordered_sentence_ids,
        actual_sentence_id="c1-s4",
        chapter_ref="Chapter 1",
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        working_state=build_empty_working_state(),
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        anchor_bank=build_empty_anchor_bank(),
        move_history=build_empty_move_history(),
        reaction_records=build_empty_reaction_records(),
    )
    assert second == []

    final = persist_due_memory_quality_probe_snapshots(
        output_dir=output_dir,
        settings=settings,
        ordered_sentence_ids=ordered_sentence_ids,
        actual_sentence_id="c1-s5",
        chapter_ref="Chapter 1",
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        working_state=build_empty_working_state(),
        concept_registry=build_empty_concept_registry(),
        thread_trace=build_empty_thread_trace(),
        reflective_frames=build_empty_reflective_frames(),
        anchor_bank=build_empty_anchor_bank(),
        move_history=build_empty_move_history(),
        reaction_records=build_empty_reaction_records(),
    )
    assert len(final) == 1
    assert is_memory_quality_probe_export_complete(output_dir)


def test_build_read_so_far_source_text_cuts_at_capture_sentence() -> None:
    source_text = runner.build_read_so_far_source_text(_book_document(), "c1-s3")
    assert "Alpha. Beta." in source_text
    assert "Gamma." in source_text
    assert "Delta." not in source_text


def test_ensure_window_output_reuses_completed_v2_with_probe_export(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run"
    window = _window()
    dataset_dir = tmp_path / "dataset"
    (dataset_dir / "segment_sources").mkdir(parents=True, exist_ok=True)
    (dataset_dir / window.segment_source_path).write_text("demo", encoding="utf-8")

    output_dir = run_root / "outputs" / window.segment_id / "attentional_v2"
    (output_dir / "_runtime").mkdir(parents=True, exist_ok=True)
    (output_dir / "_runtime" / "run_state.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    memory_quality_probe_export_file(output_dir).parent.mkdir(parents=True, exist_ok=True)
    memory_quality_probe_export_file(output_dir).write_text(
        json.dumps(
            {
                "probe_targets": [{"probe_index": index} for index in range(1, 6)],
                "snapshots": [{"probe_index": index} for index in range(1, 6)],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        runner,
        "rebuild_normalized_bundle_from_completed_output",
        lambda **_: {
            "mechanism_label": "Attentional V2 scaffold (Phase 1-8)",
            "normalized_eval_bundle": {"reactions": [], "memory_summaries": []},
        },
    )

    class _ShouldNotRun:
        def read_book(self, request):  # pragma: no cover - guard path
            raise AssertionError("read_book should not run when reuse succeeds")

    monkeypatch.setattr(runner, "_mechanism_for_key", lambda mechanism_key: _ShouldNotRun())

    payload = runner.ensure_window_output(
        window=window,
        dataset_dir=dataset_dir,
        mechanism_key="attentional_v2",
        run_root=run_root,
        require_probe_export=True,
    )

    assert payload["status"] == "completed"
    assert payload["run_mode"] == "reuse_completed"


def test_run_long_span_vnext_writes_separated_memory_and_reaction_outputs(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run"
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    window = _window()
    output_dir_v2 = run_root / "outputs" / window.segment_id / "attentional_v2"
    output_dir_v1 = run_root / "outputs" / window.segment_id / "iterator_v1"
    (output_dir_v2 / "public").mkdir(parents=True, exist_ok=True)
    (output_dir_v1 / "public").mkdir(parents=True, exist_ok=True)
    (output_dir_v2 / "public" / "book_document.json").write_text(json.dumps(_book_document()), encoding="utf-8")
    memory_quality_probe_export_file(output_dir_v2).parent.mkdir(parents=True, exist_ok=True)
    memory_quality_probe_export_file(output_dir_v2).write_text(
        json.dumps(
            {
                "snapshots": [
                    {
                        "probe_index": 1,
                        "threshold_ratio": 0.2,
                        "capture_sentence_id": "c1-s2",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(runner, "_resolve_dataset_dir", lambda manifest_path: dataset_dir)
    monkeypatch.setattr(runner, "_load_windows", lambda dataset_dir: [window])
    monkeypatch.setattr(
        runner,
        "ensure_window_output",
        lambda **kwargs: {
            "status": "completed",
            "mechanism_key": kwargs["mechanism_key"],
            "mechanism_label": kwargs["mechanism_key"],
            "output_dir": str(output_dir_v2 if kwargs["mechanism_key"] == "attentional_v2" else output_dir_v1),
            "normalized_eval_bundle": {
                "reactions": [
                    {
                        "reaction_id": f"{kwargs['mechanism_key']}-r1",
                        "type": "highlight",
                        "section_ref": "1.1",
                        "anchor_quote": "Anchor",
                        "content": "Reaction content",
                    }
                ],
                "memory_summaries": [],
            },
            "run_mode": "reuse_completed",
        },
    )
    monkeypatch.setattr(
        runner,
        "judge_memory_quality_probe",
        lambda **kwargs: {
            "salience_score": 4,
            "mainline_fidelity_score": 4,
            "organization_score": 3,
            "fidelity_score": 4,
            "overall_memory_quality_score": 4,
            "reason": "Retained the mainline clearly.",
        },
    )
    monkeypatch.setattr(
        runner,
        "audit_window_reactions",
        lambda **kwargs: [
            {
                "reaction_id": f"{kwargs['mechanism_key']}-r1",
                "label": "grounded_callback" if kwargs["mechanism_key"] == "attentional_v2" else "local_only",
                "reason": "classified in test",
            }
        ],
    )
    monkeypatch.setattr(runner, "write_llm_usage_summary", lambda run_root: None)

    aggregate = runner.run_long_span_vnext(
        run_root=run_root,
        manifest_path=tmp_path / "unused.json",
        judge_mode="llm",
        workers=2,
    )

    assert aggregate["memory_quality"]["mechanism_key"] == "attentional_v2"
    assert set(aggregate["reaction_audit"]["mechanisms"].keys()) == {"attentional_v2", "iterator_v1"}
    report = (run_root / "summary" / "report.md").read_text(encoding="utf-8")
    assert "## Memory Quality (V2 only)" in report
    assert "## Reaction Audit" in report
