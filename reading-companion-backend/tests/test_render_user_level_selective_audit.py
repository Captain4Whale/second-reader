"""Tests for the human-readable user-level selective audit renderer."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import render_user_level_selective_audit as module


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_render_user_level_selective_audit_outputs_index_and_window_docs(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "dataset"
    output_dir = dataset_dir / "audit_human_readable"

    _write_json(
        dataset_dir / "manifest.json",
        {
            "dataset_id": "demo_user_level_selective",
            "version": "test",
        },
    )
    _write_jsonl(
        dataset_dir / "segments.jsonl",
        [
            {
                "segment_id": "source_a__segment_1",
                "source_id": "source_a",
                "book_title": "Book A",
                "author": "Author A",
                "language_track": "en",
                "start_sentence_id": "c1-s1",
                "end_sentence_id": "c1-s20",
                "chapter_ids": [1],
                "chapter_titles": ["Chapter 1"],
                "termination_reason": "chapter_end_after_target_notes",
                "segment_source_path": "segment_sources/source_a__segment_1.txt",
            },
            {
                "segment_id": "source_b__segment_1",
                "source_id": "source_b",
                "book_title": "Book B",
                "author": "Author B",
                "language_track": "zh",
                "start_sentence_id": "c2-s1",
                "end_sentence_id": "c2-s10",
                "chapter_ids": [2],
                "chapter_titles": ["第二章"],
                "termination_reason": "paragraph_end_after_hard_cap",
                "segment_source_path": "segment_sources/source_b__segment_1.txt",
            },
        ],
    )
    _write_jsonl(
        dataset_dir / "note_cases.jsonl",
        [
            {
                "note_case_id": "source_a__note_2",
                "segment_id": "source_a__segment_1",
                "source_id": "source_a",
                "note_id": "note_2",
                "note_text": "Duplicate note B",
                "note_comment": "",
                "source_span_text": "Shared text",
                "source_span_slices": [
                    {
                        "paragraph_index": 1,
                        "char_start": 5,
                        "char_end": 16,
                        "text": "Shared text",
                    }
                ],
                "chapter_id": 1,
                "chapter_title": "Chapter 1",
                "raw_locator": "p.1",
                "section_label": "Section 1",
            },
            {
                "note_case_id": "source_a__note_1",
                "segment_id": "source_a__segment_1",
                "source_id": "source_a",
                "note_id": "note_1",
                "note_text": "Duplicate note A",
                "note_comment": "",
                "source_span_text": "Shared text",
                "source_span_slices": [
                    {
                        "paragraph_index": 1,
                        "char_start": 5,
                        "char_end": 16,
                        "text": "Shared text",
                    }
                ],
                "chapter_id": 1,
                "chapter_title": "Chapter 1",
                "raw_locator": "p.1",
                "section_label": "Section 1",
            },
            {
                "note_case_id": "source_a__note_3",
                "segment_id": "source_a__segment_1",
                "source_id": "source_a",
                "note_id": "note_3",
                "note_text": "Multi-slice note",
                "note_comment": "keep this note comment",
                "source_span_text": "Part one\n\nPart two",
                "source_span_slices": [
                    {
                        "paragraph_index": 2,
                        "char_start": 0,
                        "char_end": 8,
                        "text": "Part one",
                    },
                    {
                        "paragraph_index": 3,
                        "char_start": 4,
                        "char_end": 12,
                        "text": "Part two",
                    },
                ],
                "chapter_id": 1,
                "chapter_title": "Chapter 1",
                "raw_locator": "p.2",
                "section_label": "Section 2",
            },
            {
                "note_case_id": "source_b__note_1",
                "segment_id": "source_b__segment_1",
                "source_id": "source_b",
                "note_id": "note_b_1",
                "note_text": "Book B note",
                "note_comment": "",
                "source_span_text": "Window B text",
                "source_span_slices": [
                    {
                        "paragraph_index": 4,
                        "char_start": 10,
                        "char_end": 23,
                        "text": "Window B text",
                    }
                ],
                "chapter_id": 2,
                "chapter_title": "第二章",
                "raw_locator": "二",
                "section_label": "第二章",
            },
        ],
    )
    (dataset_dir / "segment_sources").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "segment_sources" / "source_a__segment_1.txt").write_text("segment a", encoding="utf-8")
    (dataset_dir / "segment_sources" / "source_b__segment_1.txt").write_text("segment b", encoding="utf-8")

    summary = module.render_user_level_selective_audit(dataset_dir=dataset_dir)

    assert summary["segment_count"] == 2
    assert summary["note_case_count"] == 4
    assert (output_dir / "index.md").exists()
    assert (output_dir / "windows" / "source_a__segment_1.md").exists()
    assert (output_dir / "windows" / "source_b__segment_1.md").exists()

    index_text = (output_dir / "index.md").read_text(encoding="utf-8")
    assert "source_a__segment_1" in index_text
    assert "source_b__segment_1" in index_text
    assert "windows/source_a__segment_1.md" in index_text
    assert "../segment_sources/source_a__segment_1.txt" in index_text

    window_text = (output_dir / "windows" / "source_a__segment_1.md").read_text(encoding="utf-8")
    assert window_text.index("`source_a__note_1`") < window_text.index("`source_a__note_2`")
    assert window_text.index("`source_a__note_2`") < window_text.index("`source_a__note_3`")
    assert "duplicate_source_span_group: `group_01` (`2` cases share this span)" in window_text
    assert "#### canonical_case_text (`source_span_text`)" in window_text
    assert "```text\nShared text\n```" in window_text
    assert "#### note_comment" in window_text
    assert "keep this note comment" in window_text
    assert "slice 1: paragraph `2`, char `0`-`8`" in window_text
    assert "slice 2: paragraph `3`, char `4`-`12`" in window_text
    assert "../../segment_sources/source_a__segment_1.txt" in window_text
