from __future__ import annotations

import json

from eval.attentional_v2 import run_digest_marginalia_live_smoke as smoke_runner
from eval.attentional_v2.run_digest_marginalia_live_smoke import (
    DEFAULT_FOCUSED_SEGMENTS,
    _hard_failures,
    _direct_probes_for_set,
    _llm_call_overrides,
    _load_dataset_segment,
    _load_resume_plan,
    _partial_failures,
    _summarize_marginalia,
    _unit_recovery_budget_allows_retry,
    _unit_recovery_delay_for_attempt,
    _unit_recovery_delay_schedule,
    _unit_error_recoverable,
    _unit_recovery_max_elapsed_seconds,
    _unit_recovery_timeout_seconds,
    build_summary,
    build_parser,
    run_focused_segments,
)


def test_dataset_segment_loader_builds_one_chapter_sentence_layer(tmp_path):
    segment_sources = tmp_path / "segment_sources"
    segment_sources.mkdir()
    (segment_sources / "demo.txt").write_text("标题\n\n第一句。第二句！", encoding="utf-8")
    (tmp_path / "segments.jsonl").write_text(
        json.dumps(
            {
                "segment_id": "demo_segment",
                "source_id": "demo_source",
                "book_title": "Demo Book",
                "author": "Author",
                "language_track": "zh",
                "chapter_titles": ["标题"],
                "segment_source_path": "segment_sources/demo.txt",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    segment = _load_dataset_segment(tmp_path, "demo_segment")

    assert segment["book_title"] == "Demo Book"
    chapter = segment["chapter"]
    assert chapter["paragraphs"][0]["text_role"] == "chapter_heading"
    assert chapter["paragraphs"][1]["text_role"] == "body"
    assert [sentence["text"] for sentence in chapter["sentences"]] == ["标题", "第一句。", "第二句！"]


def test_direct_probe_sets_include_classic_public_domain_examples():
    classic = _direct_probes_for_set("classic_public_domain")
    all_probes = _direct_probes_for_set("all")

    assert len(classic) == 8
    assert len(all_probes) > len(classic)
    assert {probe.probe_id for probe in classic} == {
        "classic_zh_su_shi_moonlight",
        "classic_zh_zhuangzi_xiaoyao",
        "classic_zh_lantingji",
        "classic_zh_mencius_well",
        "classic_en_pride_prejudice_opening",
        "classic_en_moby_dick_opening",
        "classic_en_hamlet_soliloquy",
        "classic_en_walden_woods",
    }
    assert {probe.output_language for probe in classic} == {"zh", "en"}


def test_segment_id_append_uses_defaults_only_when_unspecified():
    parser = build_parser()

    default_args = parser.parse_args([])
    explicit_args = parser.parse_args(["--segment-id", "xidaduo_private_zh__segment_1", "--segment-workers", "5"])

    assert default_args.segment_id is None
    assert default_args.segment_workers == 1
    assert default_args.failure_policy == "partial"
    assert default_args.unit_recovery_attempts == 6
    assert default_args.unit_recovery_delay_seconds is None
    assert default_args.unit_recovery_timeout_scale == 1.5
    assert default_args.unit_recovery_max_elapsed_seconds is None
    assert list(explicit_args.segment_id or DEFAULT_FOCUSED_SEGMENTS) == ["xidaduo_private_zh__segment_1"]
    assert explicit_args.segment_workers == 5


def test_unit_recovery_timeout_escalates_with_cap():
    assert _unit_recovery_timeout_seconds(120) == 180
    assert _unit_recovery_timeout_seconds(120, recovery_attempt=2, scale=1.5) == 270
    assert _unit_recovery_timeout_seconds(260) == 300


def test_unit_recovery_delay_schedule_defaults_and_repeats_last_value():
    assert _unit_recovery_delay_schedule(None, failure_policy="partial") == [0, 120, 300, 600, 900, 1200]
    assert _unit_recovery_delay_schedule(None, failure_policy="strict") == [0]
    schedule = _unit_recovery_delay_schedule("0, 5", failure_policy="partial")
    assert schedule == [0, 5]
    assert _unit_recovery_delay_for_attempt(schedule, recovery_attempt=0) == 0
    assert _unit_recovery_delay_for_attempt(schedule, recovery_attempt=1) == 0
    assert _unit_recovery_delay_for_attempt(schedule, recovery_attempt=2) == 5
    assert _unit_recovery_delay_for_attempt(schedule, recovery_attempt=3) == 5


def test_unit_recovery_max_elapsed_defaults_for_long_running_partial_policy():
    assert _unit_recovery_max_elapsed_seconds(None, failure_policy="partial") == 3600
    assert _unit_recovery_max_elapsed_seconds(None, failure_policy="strict") == 0
    assert _unit_recovery_max_elapsed_seconds(90, failure_policy="partial") == 90
    assert _unit_recovery_max_elapsed_seconds(-1, failure_policy="partial") == 0


def test_unit_recovery_budget_allows_retry_until_budget_is_exhausted():
    assert _unit_recovery_budget_allows_retry(elapsed_seconds=3599.9, max_elapsed_seconds=3600) is True
    assert _unit_recovery_budget_allows_retry(elapsed_seconds=3600.0, max_elapsed_seconds=3600) is False
    assert _unit_recovery_budget_allows_retry(elapsed_seconds=999999.0, max_elapsed_seconds=0) is True


def test_unit_recovery_retries_contract_failures_but_not_auth_failures():
    assert _unit_error_recoverable("llm_contract") is True
    assert _unit_error_recoverable("network_blocked") is True
    assert _unit_error_recoverable("exception:ValueError") is True
    assert _unit_error_recoverable("llm_auth") is False


def test_run_segment_units_retries_transient_digest_failure(monkeypatch, tmp_path):
    segment_sources = tmp_path / "segment_sources"
    segment_sources.mkdir()
    (segment_sources / "demo.txt").write_text("标题\n\n第一句。第二句！", encoding="utf-8")
    (tmp_path / "segments.jsonl").write_text(
        json.dumps(
            {
                "segment_id": "demo_segment",
                "source_id": "demo_source",
                "book_title": "Demo Book",
                "author": "Author",
                "language_track": "zh",
                "chapter_titles": ["标题"],
                "segment_source_path": "segment_sources/demo.txt",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    settle_calls = {"count": 0}

    def fake_prepare_next_source_unit_for_read(**_kwargs):
        return {"prepared": True}

    def fake_settle_next_unit(**kwargs):
        settle_calls["count"] += 1
        if settle_calls["count"] == 1:
            raise smoke_runner.ReaderLLMError(
                "Connection error.",
                problem_code="network_blocked",
                details={
                    "provider_call_attempt_count": 3,
                    "connection_error_kind": "remote_protocol_error",
                    "provider_error_type": "APIConnectionError",
                    "provider_error_cause_type": "RemoteProtocolError",
                },
            )
        output_dir = kwargs["output_dir"]
        start_cursor = {"chapter_id": 1, "chapter_ref": "标题", "paragraph_index": 1, "char_offset": 0}
        end_cursor = {"chapter_id": 1, "chapter_ref": "标题", "paragraph_index": 1, "char_offset": 3}
        source_span = {"start_cursor": start_cursor, "end_cursor": end_cursor}
        source_unit = {
            "source_span_id": "src:c1:p1@0-p1@3",
            "source_span": source_span,
            "source_text": "第一句。",
        }
        read_path = smoke_runner.read_audit_file(output_dir)
        read_path.parent.mkdir(parents=True, exist_ok=True)
        read_path.write_text(
            json.dumps(
                {
                    "source_span_id": source_unit["source_span_id"],
                    "source_span": source_span,
                    "understanding": "第一句建立了开场动作。",
                    "reading_impression": "这个开场很短，但清楚。",
                    "marginalia": [],
                    "digest_result": {
                        "understanding": "第一句建立了开场动作。",
                        "reading_impression": "这个开场很短，但清楚。",
                        "marginalia": [],
                        "memory_uptake_ops": [],
                    },
                    "llm_fallbacks": [],
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "local_buffer": kwargs["local_buffer"],
            "local_continuity": kwargs["local_continuity"],
            "active_attention": kwargs["active_attention"],
            "recent_reading_memory": kwargs["recent_reading_memory"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "reconsolidation_records": kwargs["reconsolidation_records"],
            "bundle": kwargs["bundle"],
            "selected_source_unit": source_unit,
            "source_span": source_span,
            "source_cursor": end_cursor,
            "emitted_reactions": [],
        }

    monkeypatch.setattr(smoke_runner, "prepare_next_source_unit_for_read", fake_prepare_next_source_unit_for_read)
    monkeypatch.setattr(smoke_runner, "_settle_next_unit", fake_settle_next_unit)
    monkeypatch.setattr(smoke_runner.time, "sleep", lambda _seconds: None)

    result = smoke_runner.run_segment_units(
        analysis_root=tmp_path / "analysis",
        dataset_root=tmp_path,
        segment_id="demo_segment",
        unit_count=1,
        profile_id="dataset_review_high_trust",
        max_output_tokens=4096,
        timeout_seconds=120,
        retry_attempts=3,
        failure_policy="partial",
        unit_recovery_attempts=1,
        unit_recovery_delay_seconds="0",
    )

    assert settle_calls["count"] == 2
    assert result["status"] == "ok"
    assert result["partial_failures"] == []
    assert result["unit_recovery_attempts"] == 1
    assert result["recovered_units"][0]["unit_index"] == 1
    unit = result["units"][0]
    assert unit["status"] == "ok"
    assert unit["recovered"] is True
    assert unit["unit_recovery_attempts"] == 1
    assert unit["recovery_events"][0]["problem_code"] == "network_blocked"
    assert unit["understanding"] == "第一句建立了开场动作。"


def test_llm_overrides_do_not_force_single_call_concurrency():
    overrides = _llm_call_overrides(
        max_output_tokens=4096,
        timeout_seconds=120,
        retry_attempts=3,
    )

    assert overrides.max_output_tokens == 4096
    assert overrides.timeout_seconds == 120
    assert overrides.retry_attempts == 3
    assert overrides.max_concurrency is None


def test_parallel_focused_segments_preserve_requested_order(monkeypatch, tmp_path):
    seen: list[str] = []
    recovery_kwargs: list[tuple[str, object, object, object]] = []

    def fake_run_segment_units(**kwargs):
        segment_id = kwargs["segment_id"]
        seen.append(segment_id)
        recovery_kwargs.append(
            (
                segment_id,
                kwargs.get("unit_recovery_delay_seconds"),
                kwargs.get("unit_recovery_timeout_scale"),
                kwargs.get("unit_recovery_max_elapsed_seconds"),
            )
        )
        return {
            "segment_id": segment_id,
            "status": "ok",
            "stop_reason": "unit_limit",
            "unit_count": 1,
            "units": [],
            "runtime_artifacts": {},
        }

    monkeypatch.setattr(smoke_runner, "run_segment_units", fake_run_segment_units)

    results = run_focused_segments(
        analysis_root=tmp_path,
        dataset_root=tmp_path,
        segment_ids=["segment_b", "segment_a", "segment_c"],
        unit_count=20,
        profile_id="dataset_review_high_trust",
        max_output_tokens=4096,
        timeout_seconds=120,
        retry_attempts=3,
        segment_workers=3,
        failure_policy="partial",
        unit_recovery_attempts=1,
        unit_recovery_delay_seconds="0,2",
        unit_recovery_timeout_scale=2.0,
        unit_recovery_max_elapsed_seconds=90,
    )

    assert set(seen) == {"segment_a", "segment_b", "segment_c"}
    assert [result["segment_id"] for result in results] == ["segment_b", "segment_a", "segment_c"]
    assert set(recovery_kwargs) == {
        ("segment_a", "0,2", 2.0, 90),
        ("segment_b", "0,2", 2.0, 90),
        ("segment_c", "0,2", 2.0, 90),
    }


def test_resume_plan_computes_remaining_units_and_runtime_dirs(tmp_path):
    analysis_root = tmp_path / "previous" / "analysis"
    runtime_dir = analysis_root / "runtime" / "segment_a"
    runtime_dir.mkdir(parents=True)
    (analysis_root / "raw").mkdir(parents=True)
    (analysis_root / "raw" / "runner_units.json").write_text(
        json.dumps(
            [
                {
                    "segment_id": "segment_a",
                    "status": "partial",
                    "stop_reason": "network_blocked",
                    "unit_count": 7,
                    "final_cursor": {"chapter_id": 1, "paragraph_index": 88, "char_offset": 0},
                    "runtime_artifacts": {"output_dir": str(runtime_dir)},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    plan = _load_resume_plan(
        resume_analysis_root=analysis_root,
        resume_from_run_id="previous_run",
        segment_ids=["segment_a"],
        target_total_units=20,
    )

    segment_plan = plan["segment_a"]
    assert segment_plan["resume_from_run_id"] == "previous_run"
    assert segment_plan["prior_unit_count"] == 7
    assert segment_plan["remaining_units"] == 13
    assert segment_plan["target_total_units"] == 20
    assert segment_plan["start_cursor"] == {"chapter_id": 1, "paragraph_index": 88, "char_offset": 0}
    assert segment_plan["resume_runtime_dir"] == str(runtime_dir)


def test_resume_plan_rejects_missing_segment(tmp_path):
    analysis_root = tmp_path / "previous" / "analysis"
    (analysis_root / "raw").mkdir(parents=True)
    (analysis_root / "raw" / "runner_units.json").write_text("[]\n", encoding="utf-8")

    try:
        _load_resume_plan(
            resume_analysis_root=analysis_root,
            resume_from_run_id="previous_run",
            segment_ids=["segment_a"],
            target_total_units=20,
        )
    except ValueError as exc:
        assert "resume segment not found" in str(exc)
    else:
        raise AssertionError("missing resume segment should fail")


def test_summary_reports_prior_and_combined_resume_units():
    summary = build_summary(
        mode="focused",
        direct_probe_set="calibration",
        direct_results=[],
        runner_results=[
            {
                "segment_id": "segment_a",
                "status": "ok",
                "stop_reason": "unit_limit",
                "unit_count": 13,
                "prior_unit_count": 7,
                "combined_unit_count": 20,
                "target_total_units": 20,
                "resume_from_run_id": "previous_run",
                "units": [],
                "runtime_artifacts": {"read_audit_count": 20, "unit_memory_entry_count": 20},
            }
        ],
        run_id="run",
        analysis_id="analysis",
        job_id="job",
    )

    assert summary["runner_unit_count"] == 13
    assert summary["prior_runner_unit_count"] == 7
    assert summary["combined_runner_unit_count"] == 20
    assert summary["target_total_units"] == [20]
    assert summary["resume_from_run_ids"] == ["previous_run"]


def test_marginalia_summary_classifies_highlight_and_flags_broad_quote():
    source_text = "Alpha opens. Beta changes the whole argument. Gamma closes."
    summary = _summarize_marginalia(
        [
            {
                "kind": "highlight",
                "source_quote": "Beta changes the whole argument.",
                "content": "",
                "selection_reason": "Compact standalone turn with intrinsic force.",
            },
            {"kind": "note", "source_quote": source_text, "content": "This is important."},
        ],
        source_text=source_text,
    )

    assert summary[0]["kind"] == "highlight"
    assert summary[0]["quote_found_in_unit"] is True
    assert summary[0]["selection_reason"] == "Compact standalone turn with intrinsic force."
    assert summary[1]["kind"] == "note"
    assert "quote_too_broad" in summary[1]["quality_flags"]
    assert "possibly_generic" in summary[1]["quality_flags"]


def test_summary_treats_no_highlight_as_caveat_not_failure():
    direct_results = [
        {
            "status": "ok",
            "probe_id": "probe",
            "output_contract": "digest_understanding_response_marginalia_json_v8",
            "legacy_field_leaks": [],
            "marginalia_review": [
                {
                    "kind": "note",
                    "quote_found_in_unit": True,
                    "quality_flags": [],
                }
            ],
        }
    ]

    summary = build_summary(
        mode="direct",
        direct_probe_set="calibration",
        direct_results=direct_results,
        runner_results=[],
        run_id="run",
        analysis_id="analysis",
        job_id="job",
    )

    assert summary["status"] == "pass_with_caveats"
    assert summary["hard_failures"] == []
    assert summary["highlight_observed"] is False
    assert summary["highlight_only_observed"] is False
    assert summary["direct_probe_set"] == "calibration"


def test_summary_treats_transient_segment_stop_as_partial_not_hard_failure():
    runner_results = [
        {
            "segment_id": "nawaer_baodian_private_zh__segment_1",
            "book_title": "纳瓦尔宝典",
            "status": "partial",
            "stop_reason": "llm_timeout",
            "unit_count": 2,
            "final_cursor": {"paragraph_index": 9, "char_offset": 0},
            "unit_recovery_attempts": 1,
            "unit_recovery_delay_schedule": [0, 120, 300],
            "unit_recovery_timeout_scale": 1.5,
            "recovered_units": [{"unit_index": 1}],
            "partial_failures": [
                {
                    "unit_index": 3,
                    "problem_code": "llm_timeout",
                    "final_cursor": {"paragraph_index": 9, "char_offset": 0},
                    "connection_error_kind": "read_error",
                    "unit_recovery_delay_schedule": [0, 120, 300],
                    "unit_recovery_timeout_scale": 1.5,
                }
            ],
            "units": [],
            "runtime_artifacts": {"read_audit_count": 2, "unit_memory_entry_count": 2},
        }
    ]

    summary = build_summary(
        mode="focused",
        direct_probe_set="calibration",
        direct_results=[],
        runner_results=runner_results,
        run_id="run",
        analysis_id="analysis",
        job_id="job",
    )

    assert summary["status"] == "partial"
    assert summary["hard_failures"] == []
    assert summary["partial_segment_count"] == 1
    assert summary["unit_recovery_attempts"] == 1
    assert summary["recovered_unit_count"] == 1
    assert summary["connection_error_kind_counts"] == {"read_error": 1}
    assert summary["unit_recovery_delay_schedules"] == [[0, 120, 300]]
    assert summary["unit_recovery_timeout_scales"] == [1.5]
    assert _partial_failures(runner_results)[0]["segment_id"] == "nawaer_baodian_private_zh__segment_1"


def test_summary_keeps_strict_segment_failure_hard():
    runner_results = [
        {
            "segment_id": "nawaer_baodian_private_zh__segment_1",
            "status": "failed",
            "stop_reason": "llm_timeout",
            "unit_count": 2,
            "units": [],
            "runtime_artifacts": {"read_audit_count": 2, "unit_memory_entry_count": 2},
        }
    ]

    summary = build_summary(
        mode="focused",
        direct_probe_set="calibration",
        direct_results=[],
        runner_results=runner_results,
        run_id="run",
        analysis_id="analysis",
        job_id="job",
        failure_policy="strict",
    )

    assert summary["status"] == "fail"
    assert "runner_failed:nawaer_baodian_private_zh__segment_1:llm_timeout" in summary["hard_failures"]


def test_hard_failures_catches_legacy_field_leak_and_unresolved_quote():
    failures = _hard_failures(
        [
            {
                "status": "ok",
                "probe_id": "probe",
                "output_contract": "digest_understanding_response_marginalia_json_v8",
                "legacy_field_leaks": ["marginalia[0].search_intent"],
                "marginalia_review": [{"index": 1, "quote_found_in_unit": False}],
            }
        ],
        [],
    )

    assert "legacy_field_leak:probe:marginalia[0].search_intent" in failures
    assert "direct_unresolved_quote:probe:1" in failures


def test_hard_failures_catches_runner_llm_fallback_and_empty_content_digest():
    failures = _hard_failures(
        [],
        [
            {
                "segment_id": "demo_segment",
                "status": "ok",
                "stop_reason": "unit_limit",
                "unit_count": 1,
                "runtime_artifacts": {"read_audit_count": 1, "unit_memory_entry_count": 1},
                "units": [
                    {
                        "unit_index": 13,
                        "status": "ok",
                        "source_text": "Content-bearing source text.",
                        "content_bearing_source": True,
                        "understanding": "",
                        "reading_impression": "",
                        "llm_fallbacks": [{"node": "digest", "problem_code": "network_blocked"}],
                        "marginalia_review": [],
                    }
                ],
            }
        ],
    )

    assert "runner_llm_fallback:demo_segment:unit13" in failures
    assert "runner_empty_understanding:demo_segment:unit13" in failures
    assert "runner_empty_response:demo_segment:unit13" in failures
