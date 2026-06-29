from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import analyze_marginalia_note_precision_recall as module
from eval.attentional_v2 import run_user_level_selective_comparison as matching


def _cursor(paragraph: int, offset: int) -> dict[str, object]:
    return {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "paragraph_index": paragraph,
        "char_offset": offset,
    }


def _unit(index: int, status: str, start: tuple[int, int], end: tuple[int, int]) -> dict[str, object]:
    return {
        "unit_index": index,
        "status": status,
        "source_span": {
            "start_cursor": _cursor(*start),
            "end_cursor": _cursor(*end),
        },
    }


def _slice(
    *,
    paragraph: int = 1,
    start: int = 0,
    end: int = 10,
    text: str = "Alpha note",
) -> dict[str, object]:
    return {
        "coordinate_system": "segment_source_v1",
        "segment_id": "source_a__segment_1",
        "source_id": "source_a",
        "paragraph_index": paragraph,
        "char_start": start,
        "char_end": end,
        "text": text,
    }


def _note_case(
    note_id: str = "note_1",
    *,
    source_slice: dict[str, object] | None = None,
    source_span_text: str = "Alpha note",
) -> matching.NoteCase:
    return matching.NoteCase(
        note_case_id=f"source_a__{note_id}",
        segment_id="source_a__segment_1",
        source_id="source_a",
        book_title="Book",
        author="Author",
        language_track="en",
        note_id=note_id,
        note_text=source_span_text,
        note_comment="",
        source_span_text=source_span_text,
        source_sentence_ids=["c1-s1"],
        source_span_coordinate_system="segment_source_v1",
        source_span_slices=[dict(source_slice or _slice(text=source_span_text, end=len(source_span_text)))],
        chapter_id=1,
        chapter_title="Chapter 1",
        section_label="Section",
        raw_locator="1",
        provenance={},
    )


def _source_ref(
    *,
    paragraph: int = 1,
    start: int = 0,
    end: int = 10,
    quote: str = "Alpha note",
) -> dict[str, object]:
    return {
        "source_span_id": f"src:c1:p{paragraph}@{start}-p{paragraph}@{end}",
        "source_span": {
            "start_cursor": _cursor(paragraph, start),
            "end_cursor": _cursor(paragraph, end),
        },
        "quote": quote,
        "role": "reaction_anchor",
        "resolution": {"status": "matched", "method": "exact_text", "match_count": 1},
    }


def _reaction_record(
    reaction_id: str = "r1",
    *,
    paragraph: int = 1,
    start: int = 0,
    end: int = 10,
    quote: str = "Alpha note",
) -> dict[str, object]:
    return {
        "reaction_id": reaction_id,
        "type": "highlight",
        "compatibility_section_ref": "1.1",
        "source_quote": quote,
        "thought": "",
        "primary_source_ref": _source_ref(paragraph=paragraph, start=start, end=end, quote=quote),
    }


def _write_reaction_records(runtime_root: Path, records: list[dict[str, object]]) -> None:
    path = (
        runtime_root
        / "source_a__segment_1"
        / "_mechanisms"
        / "attentional_v2"
        / "runtime"
        / "reaction_records.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"records": records}, ensure_ascii=False), encoding="utf-8")


def _segment_result(*, units: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "segment_id": "source_a__segment_1",
        "source_id": "source_a",
        "book_title": "Book",
        "status": "ok",
        "stop_reason": "unit_limit",
        "units": units
        or [
            _unit(1, "ok", (1, 0), (2, 5)),
            _unit(2, "failed", (2, 5), (3, 1)),
            _unit(3, "ok", (2, 5), (3, 8)),
        ],
    }


def test_coverage_from_successful_units_skips_failed_unit() -> None:
    coverage = module.coverage_from_successful_units(_segment_result())

    assert coverage is not None
    assert coverage.successful_unit_count == 2
    assert coverage.start_label == "P1@0"
    assert coverage.end_label == "P3@8"
    assert coverage.last_unit_index == 3


def test_slice_within_coverage_respects_start_and_end_offsets() -> None:
    coverage = module.CoverageRange(
        segment_id="source_a__segment_1",
        start_paragraph=2,
        start_offset=5,
        end_paragraph=3,
        end_offset=8,
        successful_unit_count=1,
        first_unit_index=1,
        last_unit_index=1,
        start_label="P2@5",
        end_label="P3@8",
    )

    assert module.slice_within_coverage(_slice(paragraph=2, start=5, end=7), coverage)
    assert module.slice_within_coverage(_slice(paragraph=3, start=0, end=8), coverage)
    assert not module.slice_within_coverage(_slice(paragraph=2, start=4, end=7), coverage)
    assert not module.slice_within_coverage(_slice(paragraph=3, start=0, end=9), coverage)


def test_reaction_record_to_bundle_reaction_preserves_primary_source_ref() -> None:
    reaction = module.reaction_record_to_bundle_reaction(_reaction_record())
    source_slices, resolution = matching._reaction_source_span(
        reaction,
        segment_id="source_a__segment_1",
        source_id="source_a",
    )

    assert reaction["anchor_quote"] == "Alpha note"
    assert resolution == "matched"
    assert source_slices == [_slice()]


def test_exact_match_counts_for_recall_and_precision(tmp_path: Path) -> None:
    _write_reaction_records(tmp_path, [_reaction_record()])
    summary, rows = module.evaluate_segment(
        segment_result=_segment_result(units=[_unit(1, "ok", (1, 0), (1, 20))]),
        dataset_note_cases=[_note_case()],
        runtime_root=tmp_path,
        run_root=tmp_path / "analysis",
        judge_mode="none",
    )

    assert summary["note_case_count"] == 1
    assert summary["model_marginalia_count"] == 1
    assert summary["matched_note_case_count"] == 1
    assert summary["matched_model_marginalia_count"] == 1
    assert summary["recall"] == 1.0
    assert summary["precision"] == 1.0
    assert rows[0]["label"] == "exact_match"


def test_overlap_focused_hit_counts_when_judge_says_yes(tmp_path: Path, monkeypatch) -> None:
    _write_reaction_records(tmp_path, [_reaction_record(end=20, quote="Alpha note with context")])
    monkeypatch.setattr(
        matching,
        "_judge_candidate_reaction",
        lambda **_kwargs: {"label": "focused_hit", "confidence": "high", "reason": "focused"},
    )

    summary, rows = module.evaluate_segment(
        segment_result=_segment_result(units=[_unit(1, "ok", (1, 0), (1, 30))]),
        dataset_note_cases=[_note_case(source_slice=_slice(start=0, end=10, text="Alpha note"))],
        runtime_root=tmp_path,
        run_root=tmp_path / "analysis",
        judge_mode="llm",
    )

    assert rows[0]["label"] == "focused_hit"
    assert summary["recall"] == 1.0
    assert summary["precision"] == 1.0


def test_incidental_overlap_does_not_count(tmp_path: Path, monkeypatch) -> None:
    _write_reaction_records(tmp_path, [_reaction_record(end=20, quote="Alpha note with context")])
    monkeypatch.setattr(
        matching,
        "_judge_candidate_reaction",
        lambda **_kwargs: {"label": "incidental_cover", "confidence": "medium", "reason": "too broad"},
    )

    summary, rows = module.evaluate_segment(
        segment_result=_segment_result(units=[_unit(1, "ok", (1, 0), (1, 30))]),
        dataset_note_cases=[_note_case(source_slice=_slice(start=0, end=10, text="Alpha note"))],
        runtime_root=tmp_path,
        run_root=tmp_path / "analysis",
        judge_mode="llm",
    )

    assert rows[0]["label"] == "incidental_cover"
    assert summary["matched_note_case_count"] == 0
    assert summary["matched_model_marginalia_count"] == 0
    assert summary["recall"] == 0.0
    assert summary["precision"] == 0.0


def test_precision_dedupes_one_reaction_matching_multiple_notes(tmp_path: Path) -> None:
    _write_reaction_records(tmp_path, [_reaction_record()])
    notes = [
        _note_case("note_1", source_span_text="Alpha note"),
        _note_case("note_2", source_span_text="Alpha note"),
    ]

    summary, rows = module.evaluate_segment(
        segment_result=_segment_result(units=[_unit(1, "ok", (1, 0), (1, 20))]),
        dataset_note_cases=notes,
        runtime_root=tmp_path,
        run_root=tmp_path / "analysis",
        judge_mode="none",
    )

    assert len(rows) == 1
    assert rows[0]["duplicate_note_case_aliases"] == ["source_a__note_2"]
    assert summary["raw_note_case_count"] == 2
    assert summary["note_case_count"] == 1
    assert summary["duplicate_note_case_count"] == 1
    assert summary["matched_note_case_count"] == 1
    assert summary["matched_model_marginalia_count"] == 1
    assert summary["recall"] == 1.0
    assert summary["precision"] == 1.0
