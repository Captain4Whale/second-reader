from __future__ import annotations

import json

from eval.attentional_v2 import run_digest_marginalia_live_smoke as smoke_runner
from eval.attentional_v2.run_digest_marginalia_live_smoke import (
    DEFAULT_FOCUSED_SEGMENTS,
    _hard_failures,
    _direct_probes_for_set,
    _llm_call_overrides,
    _load_dataset_segment,
    _partial_failures,
    _summarize_marginalia,
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
    assert default_args.unit_recovery_attempts == 1
    assert list(explicit_args.segment_id or DEFAULT_FOCUSED_SEGMENTS) == ["xidaduo_private_zh__segment_1"]
    assert explicit_args.segment_workers == 5


def test_unit_recovery_timeout_escalates_with_cap():
    assert _unit_recovery_timeout_seconds(120) == 180
    assert _unit_recovery_timeout_seconds(260) == 300


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

    def fake_run_segment_units(**kwargs):
        segment_id = kwargs["segment_id"]
        seen.append(segment_id)
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
    )

    assert set(seen) == {"segment_a", "segment_b", "segment_c"}
    assert [result["segment_id"] for result in results] == ["segment_b", "segment_a", "segment_c"]


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
            "recovered_units": [{"unit_index": 1}],
            "partial_failures": [
                {
                    "unit_index": 3,
                    "problem_code": "llm_timeout",
                    "final_cursor": {"paragraph_index": 9, "char_offset": 0},
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
