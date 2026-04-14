"""Tests for the note-aligned user-level selective benchmark builder."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from eval.attentional_v2 import user_level_selective_v1 as module


def _sentence(sentence_id: str, paragraph_index: int, text: str) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": int(sentence_id.rsplit("-s", 1)[-1]),
        "sentence_in_paragraph": 1,
        "paragraph_index": paragraph_index,
        "text": text,
        "text_role": "body",
    }


def _chapter(chapter_id: int, title: str, sentence_count: int) -> dict[str, object]:
    return {
        "id": chapter_id,
        "title": title,
        "chapter_number": chapter_id,
        "level": 1,
        "sentences": [
            _sentence(f"c{chapter_id}-s{index}", index, f"{title} line {index}.")
            for index in range(1, sentence_count + 1)
        ],
    }


def test_build_user_level_selective_v1_emits_real_note_cases_only(tmp_path: Path, monkeypatch) -> None:
    dataset_dir = tmp_path / "dataset"
    manifest_path = tmp_path / "manifest.json"

    monkeypatch.setattr(module, "DATASET_DIR", dataset_dir)
    monkeypatch.setattr(module, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("source_a", "source_b"))

    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {
            "assets": [
                {"linked_source_id": "source_a", "notes_id": "notes_a", "aligned_entry_count": 3},
                {"linked_source_id": "source_b", "notes_id": "notes_b", "aligned_entry_count": 0},
            ]
        },
    )
    monkeypatch.setattr(
        module,
        "_load_source_index",
        lambda: {
            "source_a": {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"},
            "source_b": {"source_id": "source_b", "relative_local_path": "state/library_sources/source_b.epub"},
        },
    )

    aligned_notes = [
        module.AlignedNote(
            note_id="note_1",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Highlight one.",
            note_comment="",
            raw_locator="1",
            section_label="Section 1",
            chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s4",
            end_sentence_id="c2-s4",
            sentence_ids=("c2-s4",),
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="note_2",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Highlight two.",
            note_comment="",
            raw_locator="2",
            section_label="Section 1",
            chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s8",
            end_sentence_id="c2-s8",
            sentence_ids=("c2-s8",),
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="note_3",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Highlight three.",
            note_comment="",
            raw_locator="3",
            section_label="Section 1",
            chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s12",
            end_sentence_id="c2-s12",
            sentence_ids=("c2-s12",),
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
    ]
    monkeypatch.setattr(
        module,
        "_load_aligned_notes",
        lambda *, notes_id, source_id: aligned_notes if source_id == "source_a" else [],
    )

    document = {
        "metadata": {
            "book": "Book A",
            "author": "Author A",
            "book_language": "en",
            "output_language": "en",
        },
        "chapters": [
            _chapter(1, "Contents", 5),
            _chapter(2, "Chapter 1", 24),
        ],
    }
    monkeypatch.setattr(
        module,
        "ensure_canonical_parse",
        lambda _path: SimpleNamespace(
            book_document=document,
            title="Book A",
            author="Author A",
            output_language="en",
        ),
    )

    payload = module.build_user_level_selective_v1(target_note_count=2, hard_sentence_cap=50)

    dataset_manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    segments = [json.loads(line) for line in (dataset_dir / "segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    note_cases = [
        json.loads(line)
        for line in (dataset_dir / "note_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert payload["manifest_id"] == module.MANIFEST_ID
    assert dataset_manifest["status"] == "active"
    assert dataset_manifest["segment_count"] == 1
    assert dataset_manifest["note_case_count"] == 3
    assert dataset_manifest["eligible_source_ids"] == ["source_a"]
    assert dataset_manifest["skipped_sources"] == [{"source_id": "source_b", "reason": "no_aligned_notes"}]
    assert len(segments) == 1
    assert segments[0]["termination_reason"] == "chapter_end_after_target_notes"
    assert len(note_cases) == 3
    assert [row["note_id"] for row in note_cases] == ["note_1", "note_2", "note_3"]
    assert all(row["provenance"]["notes_id"] == "notes_a" for row in note_cases)
    assert (dataset_dir / "segment_sources" / "source_a__segment_1.txt").exists()


def test_choose_segment_end_falls_back_to_paragraph_when_chapter_tail_exceeds_cap() -> None:
    flat_sentences = [
        {
            "chapter_id": 2,
            "paragraph_index": 1,
            "text_role": "body",
        },
        {
            "chapter_id": 2,
            "paragraph_index": 2,
            "text_role": "body",
        },
        {
            "chapter_id": 2,
            "paragraph_index": 3,
            "text_role": "body",
        },
        {
            "chapter_id": 2,
            "paragraph_index": 4,
            "text_role": "body",
        },
        {
            "chapter_id": 2,
            "paragraph_index": 5,
            "text_role": "body",
        },
        {
            "chapter_id": 2,
            "paragraph_index": 6,
            "text_role": "body",
        },
    ]
    paragraph_end_positions = {(2, index): index - 1 for index in range(1, 7)}
    chapter_end_positions = {2: 5}
    note = module.AlignedNote(
        note_id="note_1",
        notes_id="notes_a",
        source_id="source_a",
        note_text="Highlight one.",
        note_comment="",
        raw_locator="1",
        section_label="Section 1",
        chapter_id=2,
        chapter_title="Chapter 1",
        start_sentence_id="c2-s2",
        end_sentence_id="c2-s2",
        sentence_ids=("c2-s2",),
        alignment_match_type="exact",
        alignment_score=1.0,
    )

    end_position, termination_reason = module._choose_segment_end(
        target_note=note,
        target_note_end_position=1,
        flat_sentences=flat_sentences,
        chapter_end_positions=chapter_end_positions,
        paragraph_end_positions=paragraph_end_positions,
        hard_sentence_cap=2,
    )

    assert end_position == 3
    assert termination_reason == "paragraph_end_after_hard_cap"
