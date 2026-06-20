from __future__ import annotations

import json

from eval.attentional_v2.run_digest_marginalia_live_smoke import (
    _hard_failures,
    _load_dataset_segment,
    _summarize_marginalia,
    build_summary,
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


def test_marginalia_summary_classifies_highlight_and_flags_broad_quote():
    source_text = "Alpha opens. Beta changes the whole argument. Gamma closes."
    summary = _summarize_marginalia(
        [
            {"source_quote": "Beta changes the whole argument.", "content": ""},
            {"source_quote": source_text, "content": "This is important."},
        ],
        source_text=source_text,
    )

    assert summary[0]["kind"] == "highlight_only"
    assert summary[0]["quote_found_in_unit"] is True
    assert summary[1]["kind"] == "note_bearing"
    assert "quote_too_broad" in summary[1]["quality_flags"]
    assert "possibly_generic" in summary[1]["quality_flags"]


def test_summary_treats_no_highlight_only_as_caveat_not_failure():
    direct_results = [
        {
            "status": "ok",
            "probe_id": "probe",
            "output_contract": "digest_understanding_response_marginalia_json_v5",
            "legacy_field_leaks": [],
            "marginalia_review": [
                {
                    "kind": "note_bearing",
                    "quote_found_in_unit": True,
                    "quality_flags": [],
                }
            ],
        }
    ]

    summary = build_summary(
        mode="direct",
        direct_results=direct_results,
        runner_results=[],
        run_id="run",
        analysis_id="analysis",
        job_id="job",
    )

    assert summary["status"] == "pass_with_caveats"
    assert summary["hard_failures"] == []
    assert summary["highlight_only_observed"] is False


def test_hard_failures_catches_legacy_field_leak_and_unresolved_quote():
    failures = _hard_failures(
        [
            {
                "status": "ok",
                "probe_id": "probe",
                "output_contract": "digest_understanding_response_marginalia_json_v5",
                "legacy_field_leaks": ["marginalia[0].search_intent"],
                "marginalia_review": [{"index": 1, "quote_found_in_unit": False}],
            }
        ],
        [],
    )

    assert "legacy_field_leak:probe:marginalia[0].search_intent" in failures
    assert "direct_unresolved_quote:probe:1" in failures
