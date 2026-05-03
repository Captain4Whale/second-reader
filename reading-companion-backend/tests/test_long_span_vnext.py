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
    build_empty_active_attention,
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


def _window_b() -> runner.ReadingWindow:
    return runner.ReadingWindow(
        segment_id="segment_b",
        source_id="source_b",
        book_title="Book B",
        author="Author B",
        language_track="en",
        start_sentence_id="c2-s1",
        end_sentence_id="c2-s5",
        source_chapter_ids=[2],
        chapter_titles=["Chapter 2"],
        target_note_count=20,
        covered_note_count=20,
        termination_reason="chapter_end_after_target_notes",
        segment_source_path="segment_sources/segment_b.txt",
    )


def _write_dataset(dataset_dir: Path, windows: list[runner.ReadingWindow], source_text_by_segment: dict[str, str]) -> None:
    (dataset_dir / "segment_sources").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "manifest.json").write_text(json.dumps({"segments_file": "segments.jsonl"}), encoding="utf-8")
    with (dataset_dir / "segments.jsonl").open("w", encoding="utf-8") as handle:
        for window in windows:
            handle.write(json.dumps(runner.asdict(window), ensure_ascii=False) + "\n")
            (dataset_dir / window.segment_source_path).write_text(
                source_text_by_segment.get(window.segment_id, "Alpha. Beta."),
                encoding="utf-8",
            )


def _write_reuse_shard(
    *,
    reuse_root: Path,
    dataset_dir: Path,
    window: runner.ReadingWindow,
    mechanism_key: str = "iterator_v1",
) -> Path:
    shard_dir = reuse_root / "shards" / f"{window.source_id}__{mechanism_key}"
    (shard_dir / "meta").mkdir(parents=True, exist_ok=True)
    (shard_dir / "meta" / "selection.json").write_text(
        json.dumps(
            {
                "dataset_dir": str(dataset_dir),
                "segment_ids": [window.segment_id],
                "mechanism_keys": [mechanism_key],
            }
        ),
        encoding="utf-8",
    )
    output_dir = shard_dir / "outputs" / window.segment_id / mechanism_key
    (output_dir / "_runtime").mkdir(parents=True, exist_ok=True)
    (output_dir / "_runtime" / "run_state.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
    return output_dir


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
        active_attention=build_empty_active_attention(),
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
        active_attention=build_empty_active_attention(),
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
        active_attention=build_empty_active_attention(),
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


def test_memory_quality_judge_prompt_defines_score_scale(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, str] = {}

    def _fake_invoke_json(system_prompt, user_prompt, default):
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return {
            "salience_score": 4,
            "mainline_fidelity_score": 3,
            "organization_score": 2,
            "fidelity_score": 5,
            "overall_memory_quality_score": 1,
            "reason": "The snapshot retains useful mainline material with some organization gaps.",
        }

    monkeypatch.setattr(runner, "invoke_json", _fake_invoke_json)

    judgment = runner.judge_memory_quality_probe(
        run_root=tmp_path / "run",
        window=_window(),
        probe_payload={
            "probe_index": 1,
            "read_so_far_source_text": "Alpha.",
            "memory_snapshot": {"items": ["Alpha"]},
            "probe_review_focus": {
                "focus_id": "demo_structural_signal",
                "title": "Demo structure",
                "audit_question": "Does the snapshot retain the source-given structure?",
            },
        },
        judge_mode="llm",
    )

    assert "Higher is better" in captured["system_prompt"]
    assert "1 = poor / absent" in captured["system_prompt"]
    assert "3 = adequate / useful" in captured["system_prompt"]
    assert "5 = excellent" in captured["system_prompt"]
    assert "context, not substitute memory" in captured["system_prompt"]
    assert "source-given structural signals" in captured["system_prompt"]
    assert "stage model, classification, core definition, roadmap, or named distinction" in captured["system_prompt"]
    assert "not as an exact-match gold answer" in captured["system_prompt"]
    assert "Do not copy numbers from the output schema as defaults" in captured["system_prompt"]
    assert "probe_review_focus" in captured["user_prompt"]
    assert runner.MEMORY_QUALITY_JUDGE_CONTRACT in captured["user_prompt"]
    assert judgment["judge_provided_overall_memory_quality_score"] == 1
    assert judgment["overall_memory_quality_score"] == 3.5


def test_memory_quality_review_focus_marks_huochu_probe_one() -> None:
    focus = runner.memory_quality_probe_review_focus(
        segment_id="huochu_shengming_de_yiyi_private_zh__segment_1",
        probe_index=1,
    )

    assert focus
    assert focus["focus_id"] == "huochu_probe1_prisoner_response_three_stages"
    assert "three-stage framework" in focus["source_signal"]
    assert runner.memory_quality_probe_review_focus(
        segment_id="huochu_shengming_de_yiyi_private_zh__segment_1",
        probe_index=2,
    ) is None


def test_memory_quality_report_surfaces_probe_review_focus() -> None:
    focus = runner.memory_quality_probe_review_focus(
        segment_id="huochu_shengming_de_yiyi_private_zh__segment_1",
        probe_index=1,
    )
    assert focus

    report = runner._render_report(
        aggregate={
            "memory_quality": {
                "memory_quality_judge_contract": runner.MEMORY_QUALITY_JUDGE_CONTRACT,
                "average_overall_memory_quality_score": 4.0,
                "probe_count": 1,
                "window_count": 1,
                "windows": [
                    {
                        "book_title": "活出生命的意义",
                        "segment_id": "huochu_shengming_de_yiyi_private_zh__segment_1",
                        "average_overall_memory_quality_score": 4.0,
                        "probe_count": 1,
                    }
                ],
            },
            "reaction_audit": {"mechanisms": {}},
        },
        memory_quality_results=[
            {
                "segment_id": "huochu_shengming_de_yiyi_private_zh__segment_1",
                "probe_index": 1,
                "threshold_ratio": 0.2,
                "overall_memory_quality_score": 4.0,
                "reason": "The snapshot retains a structural frame.",
                "probe_review_focus": focus,
            }
        ],
        reaction_window_summaries=[],
    )

    assert "Structural-signal supplement" in report
    assert "Structural signal to check" in report
    assert "囚徒精神反应三阶段" in report


def test_normalize_memory_quality_judgment_clamps_and_derives_overall() -> None:
    judgment = runner._normalize_memory_quality_judgment(
        {
            "salience_score": 6,
            "mainline_fidelity_score": 0,
            "organization_score": "bad",
            "fidelity_score": 4,
            "overall_memory_quality_score": 5,
            "reason": "mixed",
        }
    )

    assert judgment["salience_score"] == 5
    assert judgment["mainline_fidelity_score"] == 1
    assert judgment["organization_score"] == 1
    assert judgment["fidelity_score"] == 4
    assert judgment["judge_provided_overall_memory_quality_score"] == 5
    assert judgment["overall_memory_quality_score"] == 2.75
    assert judgment["memory_quality_judge_contract"] == runner.MEMORY_QUALITY_JUDGE_CONTRACT


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


def test_ensure_window_output_with_retries_retries_provider_overload(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run"
    window = _window()
    dataset_dir = tmp_path / "dataset"
    output_dir = run_root / "outputs" / window.segment_id / "iterator_v1"
    (output_dir / "_runtime").mkdir(parents=True, exist_ok=True)
    (output_dir / "_runtime" / "run_state.json").write_text(
        json.dumps({"status": "error", "error": "overloaded_error (529)"}),
        encoding="utf-8",
    )
    attempts = {"count": 0}

    def _fake_ensure_window_output(**kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("Error code: 529 - overloaded_error")
        return {
            "status": "completed",
            "mechanism_key": kwargs["mechanism_key"],
            "output_dir": str(output_dir),
            "normalized_eval_bundle": {"reactions": [], "memory_summaries": []},
        }

    monkeypatch.setattr(runner, "ensure_window_output", _fake_ensure_window_output)

    payload = runner.ensure_window_output_with_retries(
        window=window,
        dataset_dir=dataset_dir,
        mechanism_key="iterator_v1",
        run_root=run_root,
        require_probe_export=False,
        max_attempts=2,
        retry_sleep_seconds=0,
    )

    assert attempts["count"] == 2
    assert payload["status"] == "completed"
    assert payload["output_attempt"] == 2


def test_find_reaction_reuse_output_accepts_matching_v1_window(tmp_path: Path, monkeypatch) -> None:
    window = _window()
    current_dataset = tmp_path / "current_dataset"
    reuse_dataset = tmp_path / "reuse_dataset"
    reuse_root = tmp_path / "reuse_run"
    _write_dataset(current_dataset, [window], {window.segment_id: "Alpha. Beta."})
    _write_dataset(reuse_dataset, [window], {window.segment_id: "Alpha. Beta."})
    reuse_output_dir = _write_reuse_shard(reuse_root=reuse_root, dataset_dir=reuse_dataset, window=window)

    monkeypatch.setattr(
        runner,
        "rebuild_normalized_bundle_from_completed_output",
        lambda **_: {
            "mechanism_label": "Current Iterator-Reader implementation",
            "normalized_eval_bundle": {"reactions": [], "memory_summaries": []},
        },
    )

    payload = runner.find_reaction_reuse_output(
        current_dataset_dir=current_dataset,
        window=window,
        mechanism_key="iterator_v1",
        reuse_run_root=reuse_root,
    )

    assert payload is not None
    assert payload["status"] == "completed"
    assert payload["run_mode"] == "reuse_reaction_output"
    assert payload["output_dir"] == str(reuse_output_dir)
    assert payload["reuse_validation"]["reason"] == "matched"


def test_find_reaction_reuse_output_rejects_changed_window_source(tmp_path: Path) -> None:
    window = _window()
    current_dataset = tmp_path / "current_dataset"
    reuse_dataset = tmp_path / "reuse_dataset"
    reuse_root = tmp_path / "reuse_run"
    _write_dataset(current_dataset, [window], {window.segment_id: "Alpha. Beta. Current."})
    _write_dataset(reuse_dataset, [window], {window.segment_id: "Alpha. Beta. Old."})
    _write_reuse_shard(reuse_root=reuse_root, dataset_dir=reuse_dataset, window=window)

    payload = runner.find_reaction_reuse_output(
        current_dataset_dir=current_dataset,
        window=window,
        mechanism_key="iterator_v1",
        reuse_run_root=reuse_root,
    )

    assert payload is not None
    assert payload["status"] == "rejected"
    assert payload["validation"]["reason"] == "source_text_sha256_mismatch"


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
        "ensure_window_output_with_retries",
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
                        "compat_family": "highlight",
                        "section_ref": "1.1",
                        "anchor_quote": "Anchor",
                        "content": "Reaction content",
                        "prior_link": {"ref_ids": ["anchor:a-1"]} if kwargs["mechanism_key"] == "attentional_v2" else None,
                        "outside_link": None,
                        "search_intent": None,
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
    monkeypatch.setattr(runner, "write_llm_usage_summary", lambda *args, **kwargs: None)

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
    assert "Structural-signal supplement" in report
    assert "## Reaction Audit Method" in report
    assert "## Spontaneous Callback" in report
    assert "## False Visible Integration" in report
    rows = [
        json.loads(line)
        for line in (run_root / "summary" / "reaction_audit_results.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    v2_row = next(row for row in rows if row["mechanism_key"] == "attentional_v2")
    assert v2_row["prior_link"] == {"ref_ids": ["anchor:a-1"]}


def test_run_long_span_vnext_memory_quality_rejudge_reuses_source_run(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "rejudge_run"
    source_root = tmp_path / "source_run"
    dataset_dir = tmp_path / "dataset"
    window = _window()
    _write_dataset(dataset_dir, [window], {window.segment_id: "Alpha. Beta."})
    (source_root / "meta").mkdir(parents=True, exist_ok=True)
    (source_root / "meta" / "selected_windows.json").write_text(
        json.dumps(
            {
                "windows": [runner.asdict(window)],
            }
        ),
        encoding="utf-8",
    )

    for mechanism_key in ("attentional_v2", "iterator_v1"):
        output_dir = source_root / "outputs" / window.segment_id / mechanism_key
        (output_dir / "_runtime").mkdir(parents=True, exist_ok=True)
        (output_dir / "_runtime" / "run_state.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        (output_dir / "public").mkdir(parents=True, exist_ok=True)
        (output_dir / "public" / "book_document.json").write_text(json.dumps(_book_document()), encoding="utf-8")
        if mechanism_key == "attentional_v2":
            memory_quality_probe_export_file(output_dir).parent.mkdir(parents=True, exist_ok=True)
            memory_quality_probe_export_file(output_dir).write_text(
                json.dumps(
                    {
                        "probe_targets": [{"probe_index": index} for index in range(1, 6)],
                        "snapshots": [
                            {
                                "probe_index": index,
                                "threshold_ratio": index / 5,
                                "capture_sentence_id": "c1-s2",
                            }
                            for index in range(1, 6)
                        ],
                    }
                ),
                encoding="utf-8",
            )

    source_summary = source_root / "summary"
    source_summary.mkdir(parents=True, exist_ok=True)
    (source_summary / "reaction_audit_results.jsonl").write_text(
        json.dumps(
            {
                "segment_id": window.segment_id,
                "mechanism_key": "attentional_v2",
                "reaction_id": "r1",
                "label": "local_only",
                "reason": "copied",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (source_summary / "reaction_window_summaries.jsonl").write_text(
        json.dumps(
            {
                "segment_id": window.segment_id,
                "source_id": window.source_id,
                "book_title": window.book_title,
                "mechanism_key": "attentional_v2",
                "mechanism_label": "attentional_v2",
                "total_visible_reactions": 1,
                "callback_attempt_count": 0,
                "grounded_callback_count": 0,
                "weak_callback_count": 0,
                "false_visible_integration_count": 0,
                "local_only_count": 1,
                "callback_attempt_rate": 0.0,
                "grounded_callback_rate": 0.0,
                "false_visible_integration_rate": 0.0,
                "false_rate_among_callback_attempts": 0.0,
                "representative_grounded_callbacks": [],
                "representative_false_visible_integrations": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runner, "_resolve_dataset_dir", lambda manifest_path: dataset_dir)
    monkeypatch.setattr(
        runner,
        "rebuild_normalized_bundle_from_completed_output",
        lambda **kwargs: {
            "mechanism_label": kwargs["mechanism_key"],
            "normalized_eval_bundle": {"reactions": [], "memory_summaries": []},
        },
    )
    monkeypatch.setattr(
        runner,
        "ensure_window_output_with_retries",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("rejudge must not read")),
    )
    monkeypatch.setattr(
        runner,
        "audit_window_reactions",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("reaction audit should be copied")),
    )
    monkeypatch.setattr(
        runner,
        "judge_memory_quality_probe",
        lambda **kwargs: {
            "salience_score": 4,
            "mainline_fidelity_score": 4,
            "organization_score": 4,
            "fidelity_score": 4,
            "overall_memory_quality_score": 4.0,
            "reason": "rejudged",
            "memory_quality_judge_contract": runner.MEMORY_QUALITY_JUDGE_CONTRACT,
        },
    )
    monkeypatch.setattr(runner, "write_llm_usage_summary", lambda *args, **kwargs: None)

    aggregate = runner.run_long_span_vnext(
        run_root=run_root,
        manifest_path=tmp_path / "unused.json",
        judge_mode="llm",
        workers=2,
        memory_quality_source_run_root=source_root,
    )

    assert aggregate["memory_quality_judge_contract"] == runner.MEMORY_QUALITY_JUDGE_CONTRACT
    assert aggregate["reaction_audit_source"] == "copied_from_memory_quality_source_run"
    assert aggregate["output_modes"][f"{window.segment_id}:attentional_v2"] == "memory_quality_rejudge_source_output"
    assert (run_root / "summary" / "memory_quality_results.jsonl").exists()
    report = (run_root / "summary" / "report.md").read_text(encoding="utf-8")
    assert "Scoring scale" in report
    assert "Reaction-audit results are copied unchanged" in report


def test_run_long_span_vnext_can_copy_memory_quality_and_rerun_reaction_audit(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "reaction_rejudge_run"
    output_source_root = tmp_path / "output_source_run"
    memory_result_source_root = tmp_path / "memory_result_source_run"
    dataset_dir = tmp_path / "dataset"
    window = _window()
    _write_dataset(dataset_dir, [window], {window.segment_id: "Alpha. Beta."})
    (output_source_root / "meta").mkdir(parents=True, exist_ok=True)
    (output_source_root / "meta" / "selected_windows.json").write_text(
        json.dumps({"windows": [runner.asdict(window)]}),
        encoding="utf-8",
    )

    for mechanism_key in ("attentional_v2", "iterator_v1"):
        output_dir = output_source_root / "outputs" / window.segment_id / mechanism_key
        (output_dir / "_runtime").mkdir(parents=True, exist_ok=True)
        (output_dir / "_runtime" / "run_state.json").write_text(json.dumps({"status": "completed"}), encoding="utf-8")
        (output_dir / "public").mkdir(parents=True, exist_ok=True)
        (output_dir / "public" / "book_document.json").write_text(json.dumps(_book_document()), encoding="utf-8")
        if mechanism_key == "attentional_v2":
            memory_quality_probe_export_file(output_dir).parent.mkdir(parents=True, exist_ok=True)
            memory_quality_probe_export_file(output_dir).write_text(
                json.dumps(
                    {
                        "probe_targets": [{"probe_index": index} for index in range(1, 6)],
                        "snapshots": [
                            {
                                "probe_index": index,
                                "threshold_ratio": index / 5,
                                "capture_sentence_id": "c1-s2",
                            }
                            for index in range(1, 6)
                        ],
                    }
                ),
                encoding="utf-8",
            )

    memory_summary = memory_result_source_root / "summary"
    memory_summary.mkdir(parents=True, exist_ok=True)
    (memory_summary / "memory_quality_results.jsonl").write_text(
        json.dumps(
            {
                "segment_id": window.segment_id,
                "source_id": window.source_id,
                "book_title": window.book_title,
                "mechanism_key": "attentional_v2",
                "probe_index": 1,
                "threshold_ratio": 0.2,
                "capture_sentence_id": "c1-s2",
                "salience_score": 4,
                "mainline_fidelity_score": 4,
                "organization_score": 4,
                "fidelity_score": 4,
                "overall_memory_quality_score": 4,
                "reason": "copied corrected memory quality judgment",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runner, "_resolve_dataset_dir", lambda manifest_path: dataset_dir)
    monkeypatch.setattr(
        runner,
        "rebuild_normalized_bundle_from_completed_output",
        lambda **kwargs: {
            "mechanism_label": kwargs["mechanism_key"],
            "normalized_eval_bundle": {
                "reactions": [
                    {
                        "reaction_id": f"{kwargs['mechanism_key']}-r1",
                        "type": "retrospect",
                        "compat_family": "retrospect",
                        "section_ref": "1.1",
                        "anchor_quote": "Anchor",
                        "content": "This calls back to the earlier Alpha frame.",
                        "prior_link": {"ref_ids": ["anchor:alpha"]} if kwargs["mechanism_key"] == "attentional_v2" else None,
                    }
                ],
                "memory_summaries": [],
            },
        },
    )
    monkeypatch.setattr(
        runner,
        "ensure_window_output_with_retries",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("rejudge must not read")),
    )
    monkeypatch.setattr(
        runner,
        "judge_memory_quality_probe",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("memory quality should be copied")),
    )
    audit_calls: list[str] = []

    def _fake_audit_window_reactions(**kwargs):
        audit_calls.append(kwargs["mechanism_key"])
        return [
            {
                "reaction_id": kwargs["normalized_bundle"]["reactions"][0]["reaction_id"],
                "label": "grounded_callback",
                "reason": "native evidence visible text was re-audited",
            }
        ]

    monkeypatch.setattr(runner, "audit_window_reactions", _fake_audit_window_reactions)
    monkeypatch.setattr(runner, "write_llm_usage_summary", lambda *args, **kwargs: None)

    aggregate = runner.run_long_span_vnext(
        run_root=run_root,
        manifest_path=tmp_path / "unused.json",
        judge_mode="llm",
        workers=2,
        memory_quality_source_run_root=output_source_root,
        memory_quality_results_source_run_root=memory_result_source_root,
        copy_reaction_audit_from_source=False,
    )

    assert set(audit_calls) == {"attentional_v2", "iterator_v1"}
    assert aggregate["memory_quality_source"] == "copied_from_results_source_run"
    assert aggregate["reaction_audit_source"] == "fresh_judge"
    rows = [
        json.loads(line)
        for line in (run_root / "summary" / "reaction_audit_results.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    v2_row = next(row for row in rows if row["mechanism_key"] == "attentional_v2")
    assert v2_row["prior_link"] == {"ref_ids": ["anchor:alpha"]}
    report = (run_root / "summary" / "report.md").read_text(encoding="utf-8")
    assert "Memory Quality judgments are copied unchanged" in report
    assert "## Spontaneous Callback" in report
    assert "## False Visible Integration" in report


def test_reaction_audit_batches_large_windows_with_prior_context(tmp_path: Path, monkeypatch) -> None:
    bundle = {
        "reactions": [
            {
                "reaction_id": f"r{index}",
                "type": "highlight",
                "section_ref": "1.1",
                "anchor_quote": f"Anchor {index}",
                "content": f"Reaction {index}",
            }
            for index in range(1, runner.REACTION_AUDIT_BATCH_SIZE + 2)
        ]
    }
    prompts: list[str] = []

    def _fake_invoke_json(system_prompt, user_prompt, default):
        prompts.append(user_prompt)
        marker = "Current visible reactions to classify:\n"
        current_payload = user_prompt.split(marker, 1)[1].split("\n\nReturn JSON:", 1)[0]
        current_items = json.loads(current_payload)
        return {
            "results": [
                {
                    "reaction_id": item["reaction_id"],
                    "label": "local_only",
                    "reason": "classified in batch",
                }
                for item in current_items
            ]
        }

    monkeypatch.setattr(runner, "invoke_json", _fake_invoke_json)

    labels = runner.audit_window_reactions(
        run_root=tmp_path / "run",
        window=_window(),
        mechanism_key="attentional_v2",
        output_dir=tmp_path / "output",
        normalized_bundle=bundle,
        judge_mode="llm",
    )

    assert len(labels) == runner.REACTION_AUDIT_BATCH_SIZE + 1
    assert len(prompts) == 2
    assert '"reaction_id": "r1"' in prompts[1]
    assert "Earlier visible reactions for callback context" in prompts[1]


def test_reaction_audit_retries_missing_labels_in_small_batches(tmp_path: Path, monkeypatch) -> None:
    bundle = {
        "reactions": [
            {
                "reaction_id": f"r{index}",
                "type": "highlight",
                "section_ref": "1.1",
                "anchor_quote": f"Anchor {index}",
                "content": f"Reaction {index}",
            }
            for index in range(1, 4)
        ]
    }
    prompts: list[str] = []

    def _fake_invoke_json(system_prompt, user_prompt, default):
        prompts.append(user_prompt)
        marker = "Current visible reactions to classify:\n"
        current_payload = user_prompt.split(marker, 1)[1].split("\n\nReturn JSON:", 1)[0]
        current_items = json.loads(current_payload)
        if "Retry stage: missing_retry_1" not in user_prompt:
            current_items = current_items[:-1]
        return {
            "results": [
                {
                    "reaction_id": item["reaction_id"],
                    "label": "local_only",
                    "reason": "classified after retry" if "missing_retry_1" in user_prompt else "classified in primary batch",
                }
                for item in current_items
            ]
        }

    monkeypatch.setattr(runner, "invoke_json", _fake_invoke_json)

    labels = runner.audit_window_reactions(
        run_root=tmp_path / "run",
        window=_window(),
        mechanism_key="attentional_v2",
        output_dir=tmp_path / "output",
        normalized_bundle=bundle,
        judge_mode="llm",
    )

    assert len(labels) == 3
    assert {label["reaction_id"] for label in labels} == {"r1", "r2", "r3"}
    assert all(label["reason"] != "judge_unavailable" for label in labels)
    assert any("Retry stage: missing_retry_1" in prompt for prompt in prompts)
    retry_prompt = next(prompt for prompt in prompts if "Retry stage: missing_retry_1" in prompt)
    retry_current_payload = retry_prompt.split("Current visible reactions to classify:\n", 1)[1].split("\n\nReturn JSON:", 1)[0]
    retry_current_items = json.loads(retry_current_payload)
    assert [item["reaction_id"] for item in retry_current_items] == ["r3"]


def test_run_long_span_vnext_reuses_v1_for_unchanged_windows_only(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run"
    current_dataset = tmp_path / "current_dataset"
    reuse_dataset = tmp_path / "reuse_dataset"
    reuse_root = tmp_path / "reuse_run"
    window_a = _window()
    window_b = _window_b()
    _write_dataset(
        current_dataset,
        [window_a, window_b],
        {
            window_a.segment_id: "Alpha. Beta.",
            window_b.segment_id: "Current Book B.",
        },
    )
    _write_dataset(
        reuse_dataset,
        [window_a, window_b],
        {
            window_a.segment_id: "Alpha. Beta.",
            window_b.segment_id: "Old Book B.",
        },
    )
    _write_reuse_shard(reuse_root=reuse_root, dataset_dir=reuse_dataset, window=window_a)
    _write_reuse_shard(reuse_root=reuse_root, dataset_dir=reuse_dataset, window=window_b)

    monkeypatch.setattr(runner, "_resolve_dataset_dir", lambda manifest_path: current_dataset)
    monkeypatch.setattr(runner, "_load_windows", lambda dataset_dir: [window_a, window_b] if dataset_dir == current_dataset else [window_a, window_b])
    monkeypatch.setattr(
        runner,
        "rebuild_normalized_bundle_from_completed_output",
        lambda **kwargs: {
            "mechanism_label": kwargs["mechanism_key"],
            "normalized_eval_bundle": {
                "reactions": [
                    {
                        "reaction_id": f"{kwargs['mechanism_key']}-{kwargs['segment_id']}-r1",
                        "type": "highlight",
                        "section_ref": "1.1",
                        "anchor_quote": "Anchor",
                        "content": "Reaction content",
                    }
                ],
                "memory_summaries": [],
            },
        },
    )

    fresh_calls: list[tuple[str, str]] = []

    def _fake_ensure_window_output_with_retries(**kwargs):
        window = kwargs["window"]
        mechanism_key = kwargs["mechanism_key"]
        fresh_calls.append((window.segment_id, mechanism_key))
        output_dir = run_root / "outputs" / window.segment_id / mechanism_key
        (output_dir / "public").mkdir(parents=True, exist_ok=True)
        (output_dir / "public" / "book_document.json").write_text(json.dumps(_book_document()), encoding="utf-8")
        if mechanism_key == "attentional_v2":
            memory_quality_probe_export_file(output_dir).parent.mkdir(parents=True, exist_ok=True)
            memory_quality_probe_export_file(output_dir).write_text(
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
        return {
            "status": "completed",
            "mechanism_key": mechanism_key,
            "mechanism_label": mechanism_key,
            "output_dir": str(output_dir),
            "normalized_eval_bundle": {
                "reactions": [
                    {
                        "reaction_id": f"{mechanism_key}-{window.segment_id}-fresh-r1",
                        "type": "highlight",
                        "section_ref": "1.1",
                        "anchor_quote": "Anchor",
                        "content": "Reaction content",
                    }
                ],
                "memory_summaries": [],
            },
            "run_mode": "fresh",
        }

    monkeypatch.setattr(runner, "ensure_window_output_with_retries", _fake_ensure_window_output_with_retries)
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
                "reaction_id": reaction["reaction_id"],
                "label": "local_only",
                "reason": "classified in test",
            }
            for reaction in kwargs["normalized_bundle"].get("reactions", [])
        ],
    )
    monkeypatch.setattr(runner, "write_llm_usage_summary", lambda *args, **kwargs: None)

    aggregate = runner.run_long_span_vnext(
        run_root=run_root,
        manifest_path=tmp_path / "unused.json",
        judge_mode="llm",
        workers=4,
        reaction_reuse_run_root=reuse_root,
    )

    assert ("segment_a", "iterator_v1") not in fresh_calls
    assert ("segment_b", "iterator_v1") in fresh_calls
    assert ("segment_a", "attentional_v2") in fresh_calls
    assert ("segment_b", "attentional_v2") in fresh_calls
    assert aggregate["output_modes"]["segment_a:iterator_v1"] == "reuse_reaction_output"
    assert aggregate["output_modes"]["segment_b:iterator_v1"] == "fresh"
    sourcing = json.loads((run_root / "meta" / "output_sourcing.json").read_text(encoding="utf-8"))
    assert sourcing["fresh_task_count"] == 3
