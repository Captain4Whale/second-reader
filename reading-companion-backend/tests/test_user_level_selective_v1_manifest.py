"""Tests for the note-aligned user-level selective benchmark builder."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from eval.attentional_v2 import user_level_selective_v1 as module
from src.reading_runtime.output_dir_overrides import get_output_dir_override


def _sentence(sentence_id: str, paragraph_index: int, text: str) -> dict[str, object]:
    return {
        "sentence_id": sentence_id,
        "sentence_index": int(sentence_id.rsplit("-s", 1)[-1]),
        "sentence_in_paragraph": 1,
        "paragraph_index": paragraph_index,
        "text": text,
        "text_role": "body",
        "locator": {
            "paragraph_index": paragraph_index,
            "paragraph_start": paragraph_index,
            "paragraph_end": paragraph_index,
            "char_start": 0,
            "char_end": len(text),
        },
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


def test_find_body_start_index_skips_preface_like_material() -> None:
    chapters = [
        _chapter(4, "关于本书的重要说明 DISCLAIMER", 40),
        _chapter(5, "推荐序一 财富与幸福源自选择", 37),
        _chapter(6, "序 PROLOGUE", 48),
        _chapter(7, "埃里克的笔记（关于这本书）", 39),
        _chapter(8, "纳瓦尔·拉维坎特经历表", 15),
        _chapter(10, "纳瓦尔亲述", 50),
    ]

    body_start_index = module._find_body_start_index(
        chapters=chapters,
        language_track="zh",
        book_title_value="纳瓦尔宝典",
    )

    assert body_start_index == 5


def test_find_body_start_index_respects_source_override() -> None:
    chapters = [
        _chapter(4, "关于本书的重要说明 DISCLAIMER", 40),
        _chapter(5, "推荐序一 财富与幸福源自选择", 37),
        _chapter(6, "推荐序二 一场反直觉的精神瑜伽", 60),
        _chapter(7, "序 PROLOGUE", 48),
        _chapter(8, "埃里克的笔记（关于这本书）", 39),
        _chapter(9, "纳瓦尔·拉维坎特经历表", 15),
        _chapter(10, "纳瓦尔亲述", 50),
        _chapter(11, "第一部分 财富 PART ONE WEALTH", 3),
        _chapter(12, "第一章 积累财富", 2),
        _chapter(13, "认识财富创造的原理", 168),
    ]

    body_start_index = module._find_body_start_index(
        chapters=chapters,
        language_track="zh",
        book_title_value="纳瓦尔宝典",
        source_id="nawaer_baodian_private_zh",
    )

    assert body_start_index == 9


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
            note_text="Chapter 1 line 4.",
            note_comment="",
            raw_locator="1",
            section_label="Section 1",
            source_chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s4",
            end_sentence_id="c2-s4",
            sentence_ids=("c2-s4",),
            aligned_text="Chapter 1 line 4.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="note_2",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Chapter 1 line 8.",
            note_comment="",
            raw_locator="2",
            section_label="Section 1",
            source_chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s8",
            end_sentence_id="c2-s8",
            sentence_ids=("c2-s8",),
            aligned_text="Chapter 1 line 8.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="note_3",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Chapter 1 line 12.",
            note_comment="",
            raw_locator="3",
            section_label="Section 1",
            source_chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s12",
            end_sentence_id="c2-s12",
            sentence_ids=("c2-s12",),
            aligned_text="Chapter 1 line 12.",
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
    assert "parse_mode" not in dataset_manifest
    assert "source_filter" not in dataset_manifest
    assert not (dataset_dir / "candidate_validation_report.json").exists()
    assert len(segments) == 1
    assert segments[0]["termination_reason"] == "chapter_end_after_target_notes"
    assert segments[0]["source_chapter_ids"] == [2]
    assert len(note_cases) == 3
    assert [row["note_id"] for row in note_cases] == ["note_1", "note_2", "note_3"]
    assert all(row["source_span_coordinate_system"] == "segment_source_v1" for row in note_cases)
    assert all(row["source_span_slices"] for row in note_cases)
    assert note_cases[0]["source_span_text"] == "Chapter 1 line 4."
    assert all(row["source_chapter_id"] == 2 for row in note_cases)
    assert all(row["provenance"]["notes_id"] == "notes_a" for row in note_cases)
    assert (dataset_dir / "segment_sources" / "source_a__segment_1.txt").exists()


def test_build_user_level_selective_v1_source_filter_builds_only_requested_source(tmp_path: Path, monkeypatch) -> None:
    dataset_dir = tmp_path / "dataset"
    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("source_a", "source_b"))
    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {
            "assets": [
                {"linked_source_id": "source_a", "notes_id": "notes_a", "aligned_entry_count": 2},
                {"linked_source_id": "source_b", "notes_id": "notes_b", "aligned_entry_count": 2},
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

    def fake_notes(*, notes_id: str, source_id: str) -> list[module.AlignedNote]:
        return [
            module.AlignedNote(
                note_id=f"{source_id}_note_1",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 4.",
                note_comment="",
                raw_locator="1",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s4",
                end_sentence_id="c2-s4",
                sentence_ids=("c2-s4",),
                aligned_text="Chapter 1 line 4.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
            module.AlignedNote(
                note_id=f"{source_id}_note_2",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 8.",
                note_comment="",
                raw_locator="2",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s8",
                end_sentence_id="c2-s8",
                sentence_ids=("c2-s8",),
                aligned_text="Chapter 1 line 8.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
        ]

    monkeypatch.setattr(module, "_load_aligned_notes", fake_notes)
    document = {
        "metadata": {"book": "Book", "author": "Author", "book_language": "en", "output_language": "en"},
        "chapters": [_chapter(1, "Contents", 5), _chapter(2, "Chapter 1", 24)],
    }
    calls: list[str] = []

    def fake_ensure(path: Path) -> SimpleNamespace:
        calls.append(path.name)
        return SimpleNamespace(
            book_document=document,
            title="Book",
            author="Author",
            output_language="en",
            output_dir=tmp_path / "canonical" / path.stem,
        )

    monkeypatch.setattr(module, "ensure_canonical_parse", fake_ensure)

    payload = module.build_user_level_selective_v1(
        dataset_dir=dataset_dir,
        split_manifest_path=None,
        source_ids=("source_b",),
        target_note_count=2,
        hard_sentence_cap=50,
    )

    segments = [json.loads(line) for line in (dataset_dir / "segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    dataset_manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    assert calls == ["source_b.epub"]
    assert [row["source_id"] for row in segments] == ["source_b"]
    assert dataset_manifest["registered_source_ids"] == ["source_b"]
    assert dataset_manifest["source_filter"] == ["source_b"]
    assert payload["quota_status"]["reading_segments"]["registered_sources"] == 1


def test_build_user_level_selective_v1_fresh_parse_output_root_uses_isolated_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dataset_dir = tmp_path / "dataset"
    fresh_root = tmp_path / "fresh_parse"
    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("source_a",))
    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {"assets": [{"linked_source_id": "source_a", "notes_id": "notes_a", "aligned_entry_count": 2}]},
    )
    monkeypatch.setattr(
        module,
        "_load_source_index",
        lambda: {"source_a": {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"}},
    )
    monkeypatch.setattr(
        module,
        "_load_aligned_notes",
        lambda *, notes_id, source_id: [
            module.AlignedNote(
                note_id="note_1",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 4.",
                note_comment="",
                raw_locator="1",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s4",
                end_sentence_id="c2-s4",
                sentence_ids=("c2-s4",),
                aligned_text="Chapter 1 line 4.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
            module.AlignedNote(
                note_id="note_2",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 8.",
                note_comment="",
                raw_locator="2",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s8",
                end_sentence_id="c2-s8",
                sentence_ids=("c2-s8",),
                aligned_text="Chapter 1 line 8.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
        ],
    )
    document = {
        "metadata": {"book": "Book A", "author": "Author A", "book_language": "en", "output_language": "en"},
        "chapters": [_chapter(1, "Contents", 5), _chapter(2, "Chapter 1", 24)],
    }
    observed_overrides: list[Path | None] = []

    def fake_ensure(_path: Path) -> SimpleNamespace:
        observed_overrides.append(get_output_dir_override())
        return SimpleNamespace(
            book_document=document,
            title="Book A",
            author="Author A",
            output_language="en",
            output_dir=get_output_dir_override(),
        )

    monkeypatch.setattr(module, "ensure_canonical_parse", fake_ensure)

    module.build_user_level_selective_v1(
        dataset_dir=dataset_dir,
        split_manifest_path=None,
        source_ids=("source_a",),
        fresh_parse_output_root=fresh_root,
        target_note_count=2,
        hard_sentence_cap=50,
    )

    dataset_manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    assert observed_overrides == [fresh_root.resolve() / "source_a"]
    assert dataset_manifest["parse_mode"] == "fresh_isolated"
    assert dataset_manifest["fresh_parse_output_root"] == module._relative_to_root(fresh_root.resolve())
    assert dataset_manifest["source_parse_outputs"] == {
        "source_a": module._relative_to_root(fresh_root.resolve() / "source_a")
    }
    assert (dataset_dir / "candidate_validation_report.json").exists()


def test_build_user_level_selective_v1_default_parse_does_not_set_output_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dataset_dir = tmp_path / "dataset"
    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("source_a",))
    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {"assets": [{"linked_source_id": "source_a", "notes_id": "notes_a", "aligned_entry_count": 2}]},
    )
    monkeypatch.setattr(
        module,
        "_load_source_index",
        lambda: {"source_a": {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"}},
    )
    monkeypatch.setattr(
        module,
        "_load_aligned_notes",
        lambda *, notes_id, source_id: [
            module.AlignedNote(
                note_id="note_1",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 4.",
                note_comment="",
                raw_locator="1",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s4",
                end_sentence_id="c2-s4",
                sentence_ids=("c2-s4",),
                aligned_text="Chapter 1 line 4.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
            module.AlignedNote(
                note_id="note_2",
                notes_id=notes_id,
                source_id=source_id,
                note_text="Chapter 1 line 8.",
                note_comment="",
                raw_locator="2",
                section_label="Section 1",
                source_chapter_id=2,
                chapter_title="Chapter 1",
                start_sentence_id="c2-s8",
                end_sentence_id="c2-s8",
                sentence_ids=("c2-s8",),
                aligned_text="Chapter 1 line 8.",
                alignment_match_type="exact",
                alignment_score=1.0,
            ),
        ],
    )
    document = {
        "metadata": {"book": "Book A", "author": "Author A", "book_language": "en", "output_language": "en"},
        "chapters": [_chapter(1, "Contents", 5), _chapter(2, "Chapter 1", 24)],
    }
    observed_overrides: list[Path | None] = []

    def fake_ensure(_path: Path) -> SimpleNamespace:
        observed_overrides.append(get_output_dir_override())
        return SimpleNamespace(
            book_document=document,
            title="Book A",
            author="Author A",
            output_language="en",
            output_dir=tmp_path / "canonical",
        )

    monkeypatch.setattr(module, "ensure_canonical_parse", fake_ensure)

    module.build_user_level_selective_v1(
        dataset_dir=dataset_dir,
        split_manifest_path=None,
        source_ids=("source_a",),
        target_note_count=2,
        hard_sentence_cap=50,
    )

    dataset_manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    assert observed_overrides == [None]
    assert dataset_manifest["parse_mode"] == "canonical_existing"
    assert dataset_manifest["fresh_parse_output_root"] == ""


def test_note_source_span_relocates_exact_quote_when_old_sentence_ids_drift() -> None:
    flat_sentences = [
        {
            **_sentence("c8-s350", 10, "恰如悉达多有了目标并下定决心。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
        {
            **_sentence("c8-s351", 10, "悉达多什么都不做，他等待、思考、斋戒。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
        {
            **_sentence("c8-s352", 10, "他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
        {
            **_sentence("c8-s358", 11, "目标会指引他，因为他禁止任何干扰目标的事情进入他的灵魂。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
        {
            **_sentence("c8-s359", 11, "这是悉达多做沙门时学到的。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
        {
            **_sentence("c8-s360", 11, "愚人们称其为魔法。"),
            "chapter_id": 8,
            "chapter_title": "迦摩罗",
        },
    ]
    rendered, segment_sentence_spans, segment_paragraph_texts = module._render_segment_source(
        flat_sentences=flat_sentences,
        start_position=0,
        end_position=len(flat_sentences) - 1,
        language_track="zh",
    )
    assert "恰如悉达多有了目标并下定决心。" in rendered
    sentence_index = {str(sentence["sentence_id"]): index for index, sentence in enumerate(flat_sentences)}
    note = module.AlignedNote(
        note_id="note_1",
        notes_id="notes_x",
        source_id="xidaduo_private_zh",
        note_text="恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。",
        note_comment="",
        raw_locator="迦摩罗",
        section_label="迦摩罗",
        source_chapter_id=8,
        chapter_title="迦摩罗",
        start_sentence_id="c8-s358",
        end_sentence_id="c8-s360",
        sentence_ids=("c8-s358", "c8-s360"),
        aligned_text="",
        alignment_match_type="exact",
        alignment_score=100.0,
    )

    source_span_text, source_sentence_ids, slices = module._note_source_span(
        note=note,
        flat_sentences=flat_sentences,
        sentence_index=sentence_index,
        language_track="zh",
        segment_sentence_spans=segment_sentence_spans,
        segment_paragraph_texts=segment_paragraph_texts,
        segment_id="xidaduo_private_zh__segment_1",
    )

    assert source_sentence_ids == ["c8-s350", "c8-s351", "c8-s352"]
    assert source_span_text == note.note_text
    assert slices[0]["matched_source_text_kind"] == "note_text_relocated_by_text"


def test_first_slice_key_preserves_zero_char_start() -> None:
    row = {
        "source_span_slices": [
            {
                "paragraph_index": 143,
                "char_start": 0,
                "char_end": 55,
            }
        ]
    }

    assert module._first_slice_key(row) == (143, 0, 55)


def test_build_user_level_selective_v1_applies_nawaer_body_start_override(tmp_path: Path, monkeypatch) -> None:
    dataset_dir = tmp_path / "dataset"
    manifest_path = tmp_path / "manifest.json"

    monkeypatch.setattr(module, "DATASET_DIR", dataset_dir)
    monkeypatch.setattr(module, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("nawaer_baodian_private_zh",))
    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {
            "assets": [
                {
                    "linked_source_id": "nawaer_baodian_private_zh",
                    "notes_id": "notes_nawaer",
                    "aligned_entry_count": 2,
                }
            ]
        },
    )
    monkeypatch.setattr(
        module,
        "_load_source_index",
        lambda: {
            "nawaer_baodian_private_zh": {
                "source_id": "nawaer_baodian_private_zh",
                "relative_local_path": "state/library_sources/nawaer.epub",
            }
        },
    )

    aligned_notes = [
        module.AlignedNote(
            note_id="preface_note",
            notes_id="notes_nawaer",
            source_id="nawaer_baodian_private_zh",
            note_text="Preface line 4.",
            note_comment="",
            raw_locator="preface",
            section_label="推荐序二",
            source_chapter_id=6,
            chapter_title="推荐序二 一场反直觉的精神瑜伽",
            start_sentence_id="c6-s4",
            end_sentence_id="c6-s4",
            sentence_ids=("c6-s4",),
            aligned_text="Preface line 4.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="body_note",
            notes_id="notes_nawaer",
            source_id="nawaer_baodian_private_zh",
            note_text="认识财富创造的原理 line 4.",
            note_comment="",
            raw_locator="body",
            section_label="认识财富创造的原理",
            source_chapter_id=13,
            chapter_title="认识财富创造的原理",
            start_sentence_id="c13-s4",
            end_sentence_id="c13-s4",
            sentence_ids=("c13-s4",),
            aligned_text="认识财富创造的原理 line 4.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
    ]
    monkeypatch.setattr(module, "_load_aligned_notes", lambda *, notes_id, source_id: aligned_notes)

    document = {
        "metadata": {
            "book": "纳瓦尔宝典",
            "author": "作者",
            "book_language": "zh",
            "output_language": "zh",
        },
        "chapters": [
            _chapter(4, "关于本书的重要说明 DISCLAIMER", 40),
            _chapter(5, "推荐序一 财富与幸福源自选择", 37),
            _chapter(6, "推荐序二 一场反直觉的精神瑜伽", 60),
            _chapter(7, "序 PROLOGUE", 48),
            _chapter(8, "埃里克的笔记（关于这本书）", 39),
            _chapter(9, "纳瓦尔·拉维坎特经历表", 15),
            _chapter(10, "纳瓦尔亲述", 50),
            _chapter(11, "第一部分 财富 PART ONE WEALTH", 3),
            _chapter(12, "第一章 积累财富", 2),
            _chapter(13, "认识财富创造的原理", 24),
        ],
    }
    monkeypatch.setattr(
        module,
        "ensure_canonical_parse",
        lambda _path: SimpleNamespace(
            book_document=document,
            title="纳瓦尔宝典",
            author="作者",
            output_language="zh",
        ),
    )

    module.build_user_level_selective_v1(target_note_count=1, hard_sentence_cap=50)

    segments = [json.loads(line) for line in (dataset_dir / "segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    note_cases = [
        json.loads(line)
        for line in (dataset_dir / "note_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    segment_source_text = (dataset_dir / "segment_sources" / "nawaer_baodian_private_zh__segment_1.txt").read_text(
        encoding="utf-8"
    )

    assert len(segments) == 1
    assert segments[0]["start_sentence_id"] == "c13-s1"
    assert len(note_cases) == 1
    assert note_cases[0]["note_id"] == "body_note"
    assert note_cases[0]["source_span_text"] == "认识财富创造的原理 line 4."
    assert note_cases[0]["source_span_slices"]
    assert segment_source_text.startswith("认识财富创造的原理")


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
        source_chapter_id=2,
        chapter_title="Chapter 1",
        start_sentence_id="c2-s2",
        end_sentence_id="c2-s2",
        sentence_ids=("c2-s2",),
        aligned_text="Highlight one.",
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


def test_build_user_level_selective_v1_supports_custom_dataset_dir_without_writing_split_manifest(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dataset_dir = tmp_path / "dataset_alt"
    manifest_path = tmp_path / "should_not_exist.json"

    monkeypatch.setattr(module, "REGISTERED_NOTES_SOURCE_IDS", ("source_a",))
    monkeypatch.setattr(
        module,
        "_load_notes_catalog",
        lambda: {
            "assets": [
                {"linked_source_id": "source_a", "notes_id": "notes_a", "aligned_entry_count": 2},
            ]
        },
    )
    monkeypatch.setattr(
        module,
        "_load_source_index",
        lambda: {
            "source_a": {"source_id": "source_a", "relative_local_path": "state/library_sources/source_a.epub"},
        },
    )
    aligned_notes = [
        module.AlignedNote(
            note_id="note_1",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Chapter 1 line 4.",
            note_comment="",
            raw_locator="1",
            section_label="Section 1",
            source_chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s4",
            end_sentence_id="c2-s4",
            sentence_ids=("c2-s4",),
            aligned_text="Chapter 1 line 4.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
        module.AlignedNote(
            note_id="note_2",
            notes_id="notes_a",
            source_id="source_a",
            note_text="Chapter 1 line 8.",
            note_comment="",
            raw_locator="2",
            section_label="Section 1",
            source_chapter_id=2,
            chapter_title="Chapter 1",
            start_sentence_id="c2-s8",
            end_sentence_id="c2-s8",
            sentence_ids=("c2-s8",),
            aligned_text="Chapter 1 line 8.",
            alignment_match_type="exact",
            alignment_score=1.0,
        ),
    ]
    monkeypatch.setattr(
        module,
        "_load_aligned_notes",
        lambda *, notes_id, source_id: aligned_notes,
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

    module.build_user_level_selective_v1(
        dataset_dir=dataset_dir,
        dataset_id="custom_dataset",
        dataset_version="custom-version",
        split_manifest_path=None,
        target_note_count=2,
        hard_sentence_cap=50,
    )

    dataset_manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    assert dataset_manifest["dataset_id"] == "custom_dataset"
    assert dataset_manifest["version"] == "custom-version"
    assert not manifest_path.exists()
