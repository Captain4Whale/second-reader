"""Build the active note-aligned user-level selective benchmark package.

This benchmark replaces the old active excerpt-surface pointer. Each source
contributes one continuous reading segment that starts at the opening of body
text and ends once the segment covers at least the target number of aligned
human notes, preserving a complete structural boundary where possible.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from typing import Any
import unicodedata

from eval.attentional_v2.corpus_builder import ROOT, chapter_title, is_front_matter, write_json, write_jsonl
from src.iterator_reader.storage import parse_diagnostics_file
from src.reading_runtime.output_dir_overrides import override_output_dir
from src.reading_runtime.provisioning import ensure_canonical_parse


MANIFEST_ID = "attentional_v2_user_level_selective_v1_draft"
MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / f"{MANIFEST_ID}.json"
DATASET_ID = "attentional_v2_user_level_selective_v1_repaired_20260629_source_norm_v1_2_unique_notes"
DATASET_DIR = ROOT / "state" / "eval_local_datasets" / "user_level_benchmarks" / DATASET_ID
SEGMENTS_FILE = "segments.jsonl"
NOTE_CASES_FILE = "note_cases.jsonl"
SEGMENT_SOURCE_DIRNAME = "segment_sources"
DEFAULT_VERSION = "2026-06-29-source-normalization-v1.2-unique-notes"
DEFAULT_TARGET_NOTE_COUNT = 20
DEFAULT_HARD_SENTENCE_CAP = 350
DEFAULT_CANDIDATE_VALIDATION_REPORT_JSON = "candidate_validation_report.json"
DEFAULT_CANDIDATE_VALIDATION_REPORT_MD = "candidate_validation_report.md"

DEFAULT_NOTES_LOCAL_REF_MANIFEST = (
    ROOT
    / "state"
    / "dataset_build"
    / "build_runs"
    / "human_notes_guided_dataset_v1_20260404"
    / "manifests"
    / "local_refs"
    / "attentional_v2_human_notes_guided_dataset_v1_local_refs__scratch__human_notes_guided_dataset_v1_20260404.json"
)
DEFAULT_NOTES_CATALOG_PATH = ROOT / "state" / "dataset_build" / "library_notes_catalog.json"
REGISTERED_NOTES_SOURCE_IDS = (
    "huochu_shengming_de_yiyi_private_zh",
    "mangge_zhi_dao_private_zh",
    "nawaer_baodian_private_zh",
    "value_of_others_private_en",
    "xidaduo_private_zh",
)
BODY_START_CHAPTER_OVERRIDES = {
    "nawaer_baodian_private_zh": 13,
}
SOURCE_MARKER_CHECKS = {
    "xidaduo_private_zh": {
        "must_be_absent": [
            "Brahmanen",
            "Magadha",
            "[2]Vishnus",
            "[3]Lakschmi",
        ],
        "must_be_present": [
            "婆罗门[1]",
            "摩揭陀[1]",
            "毗湿奴[2]",
            "女神[3]",
        ],
        "known_conservative_residue": [
            "1《爱经》",
        ],
    },
}
FRONT_MATTER_EXTRA_TITLE_PATTERNS_ZH = tuple(
    re.compile(pattern)
    for pattern in (
        r"^书名页$",
        r"^版权页$",
        r"^版权$",
        r"^关于本书的重要说明(?:disclaimer)?$",
        r"^出版说明$",
        r"^出版前言$",
        r"^推荐序.*$",
        r"^前言$",
        r"^导言$",
        r"^导读$",
        r"^编者按$",
        r"^编者说明$",
        r"^编辑说明$",
        r"^作者说明$",
        r"^译者说明$",
        r"^序言$",
        r"^序(?:prologue)?$",
        r"^自序$",
        r"^.*关于这本书.*$",
        r"^.*(?:年表|经历表)$",
        r"^目录$",
    )
)
FRONT_MATTER_EXTRA_TITLE_PATTERNS_EN = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^title page$",
        r"^copyright$",
        r"^contents$",
        r"^table of contents$",
        r"^disclaimer$",
        r"^foreword$",
        r"^preface$",
        r"^prologue$",
        r"^introduction$",
        r"^editor'?s note$",
        r"^author'?s note$",
        r"^about this book$",
        r"^timeline$",
    )
)


@dataclass(frozen=True)
class AlignedNote:
    note_id: str
    notes_id: str
    source_id: str
    note_text: str
    note_comment: str
    raw_locator: str
    section_label: str
    source_chapter_id: int
    chapter_title: str
    start_sentence_id: str
    end_sentence_id: str
    sentence_ids: tuple[str, ...]
    aligned_text: str
    alignment_match_type: str
    alignment_score: float
    duplicate_note_aliases: tuple[str, ...] = ()
    duplicate_note_group_size: int = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_dedupe_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", _clean_text(value))
    normalized = re.sub(r"\s+", " ", normalized, flags=re.UNICODE)
    return normalized.strip().casefold()


def _aligned_note_dedupe_key(note: AlignedNote) -> tuple[object, ...]:
    return (
        note.source_id,
        note.source_chapter_id,
        note.start_sentence_id,
        note.end_sentence_id,
        _normalize_dedupe_text(note.note_text),
        _normalize_dedupe_text(note.aligned_text),
    )


def _dedupe_aligned_notes(notes: list[AlignedNote]) -> tuple[list[AlignedNote], dict[str, Any]]:
    groups: dict[tuple[object, ...], list[AlignedNote]] = {}
    order: list[tuple[object, ...]] = []
    for note in notes:
        key = _aligned_note_dedupe_key(note)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(note)

    deduped: list[AlignedNote] = []
    duplicate_groups: list[dict[str, Any]] = []
    for key in order:
        group = groups[key]
        canonical = group[0]
        aliases = tuple(note.note_id for note in group[1:] if note.note_id)
        if aliases:
            canonical = replace(
                canonical,
                duplicate_note_aliases=aliases,
                duplicate_note_group_size=len(group),
            )
            duplicate_groups.append(
                {
                    "canonical_note_id": canonical.note_id,
                    "duplicate_note_aliases": list(aliases),
                    "duplicate_note_group_size": len(group),
                }
            )
        deduped.append(canonical)

    return deduped, {
        "raw_note_count": len(notes),
        "unique_note_count": len(deduped),
        "duplicate_note_count": len(notes) - len(deduped),
        "duplicate_note_group_count": len(duplicate_groups),
        "duplicate_note_groups": duplicate_groups[:20],
    }


def _normalize_title(value: str) -> str:
    return re.sub(r"\s+", "", _clean_text(value)).casefold()


def _sentence_number(sentence_id: str) -> int:
    suffix = str(sentence_id or "").rsplit("-s", 1)[-1]
    return int(suffix) if suffix.isdigit() else 0


def _relative_to_root(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _join_sentence_texts(sentences: list[dict[str, Any]], *, language_track: str) -> str:
    if not sentences:
        return ""
    separator = " " if language_track == "en" else ""
    return separator.join(_clean_text(sentence.get("text")) for sentence in sentences if _clean_text(sentence.get("text")))


def _normalized_join_separator(left: str, right: str) -> str:
    if not left or not right:
        return ""
    if re.match(r"[\w\u4e00-\u9fff]", left[-1], flags=re.UNICODE) and re.match(
        r"[\w\u4e00-\u9fff]",
        right[0],
        flags=re.UNICODE,
    ):
        return " "
    return ""


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _load_notes_catalog() -> dict[str, Any]:
    return _load_json(DEFAULT_NOTES_CATALOG_PATH)


def _load_source_index() -> dict[str, dict[str, Any]]:
    payload = _load_json(DEFAULT_NOTES_LOCAL_REF_MANIFEST)
    index: dict[str, dict[str, Any]] = {}
    for item in payload.get("source_refs") or []:
        if not isinstance(item, dict):
            continue
        source_id = _clean_text(item.get("source_id"))
        relative_local_path = _clean_text(item.get("relative_local_path"))
        if source_id and relative_local_path:
            index[source_id] = dict(item)
    return index


def _entry_file_path(notes_id: str) -> Path:
    return ROOT / "state" / "library_notes" / "entries" / f"{notes_id}.jsonl"


def _load_aligned_notes(*, notes_id: str, source_id: str) -> list[AlignedNote]:
    path = _entry_file_path(notes_id)
    notes: list[AlignedNote] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if _clean_text(row.get("alignment_status")) != "aligned":
                continue
            if _clean_text(row.get("linked_source_id")) != source_id:
                continue
            matched_span = dict(row.get("matched_sentence_span") or {})
            source_chapter_id = int(_clean_text(row.get("matched_chapter_id")) or matched_span.get("chapter_id") or 0)
            if source_chapter_id <= 0:
                continue
            start_sentence_id = _clean_text(matched_span.get("start_sentence_id"))
            end_sentence_id = _clean_text(matched_span.get("end_sentence_id")) or start_sentence_id
            if not start_sentence_id:
                continue
            notes.append(
                AlignedNote(
                    note_id=_clean_text(row.get("entry_id")),
                    notes_id=notes_id,
                    source_id=source_id,
                    note_text=_clean_text(row.get("quote")),
                    note_comment=_clean_text(row.get("note")),
                    raw_locator=_clean_text(row.get("raw_locator")),
                    section_label=_clean_text(row.get("section_label")),
                    source_chapter_id=source_chapter_id,
                    chapter_title=_clean_text((row.get("alignment") or {}).get("chapter_title")) or _clean_text(row.get("section_label")),
                    start_sentence_id=start_sentence_id,
                    end_sentence_id=end_sentence_id,
                    sentence_ids=tuple(str(item) for item in (row.get("matched_sentence_ids") or []) if _clean_text(item)),
                    aligned_text=_clean_text((row.get("alignment") or {}).get("aligned_text")),
                    alignment_match_type=_clean_text((row.get("alignment") or {}).get("match_type")),
                    alignment_score=float((row.get("alignment") or {}).get("score") or 0.0),
                )
            )
    notes.sort(key=lambda item: (item.source_chapter_id, _sentence_number(item.start_sentence_id), item.note_id))
    return notes


def _title_matches_extra_front_matter(title: str, *, language_track: str) -> bool:
    patterns = FRONT_MATTER_EXTRA_TITLE_PATTERNS_EN if language_track == "en" else FRONT_MATTER_EXTRA_TITLE_PATTERNS_ZH
    normalized = _normalize_title(title)
    return any(pattern.search(normalized) for pattern in patterns)


def _body_start_override_index(*, chapters: list[dict[str, Any]], source_id: str) -> int | None:
    override_chapter_id = BODY_START_CHAPTER_OVERRIDES.get(source_id)
    if override_chapter_id is None:
        return None
    for chapter_index, chapter in enumerate(chapters):
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id == override_chapter_id:
            return chapter_index
    raise ValueError(f"body-start override chapter {override_chapter_id} not found for source {source_id}")


def _find_body_start_index(
    *,
    chapters: list[dict[str, Any]],
    language_track: str,
    book_title_value: str,
    source_id: str | None = None,
) -> int:
    if source_id:
        override_index = _body_start_override_index(chapters=chapters, source_id=source_id)
        if override_index is not None:
            return override_index
    for chapter_index, chapter in enumerate(chapters):
        front_matter, _reason = is_front_matter(
            chapter,
            language=language_track,
            book_title=book_title_value,
            chapter_index=chapter_index,
        )
        title = chapter_title(chapter)
        if front_matter or _title_matches_extra_front_matter(title, language_track=language_track):
            continue
        if len(chapter.get("sentences") or []) < 20:
            continue
        return chapter_index
    return 0


def _flatten_document(
    *,
    chapters: list[dict[str, Any]],
    start_index: int,
    language_track: str,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[tuple[int, int], int], dict[int, int]]:
    flat_sentences: list[dict[str, Any]] = []
    sentence_index: dict[str, int] = {}
    paragraph_end_positions: dict[tuple[int, int], int] = {}
    chapter_end_positions: dict[int, int] = {}
    for chapter in chapters[start_index:]:
        chapter_id = int(chapter.get("id", 0) or 0)
        chapter_name = chapter_title(chapter)
        chapter_sentences = [sentence for sentence in chapter.get("sentences") or [] if isinstance(sentence, dict)]
        current_paragraph_key: tuple[int, int] | None = None
        for sentence in chapter_sentences:
            position = len(flat_sentences)
            sentence_id = _clean_text(sentence.get("sentence_id"))
            paragraph_index = int(sentence.get("paragraph_index", 0) or 0)
            flat_sentences.append(
                {
                    "global_index": position,
                    "chapter_id": chapter_id,
                    "chapter_title": chapter_name,
                    "sentence_id": sentence_id,
                    "paragraph_index": paragraph_index,
                    "text": _clean_text(sentence.get("text")),
                    "text_role": _clean_text(sentence.get("text_role")),
                    "language_track": language_track,
                    "locator": dict(sentence.get("locator") or {}) if isinstance(sentence.get("locator"), dict) else {},
                }
            )
            sentence_index[sentence_id] = position
            paragraph_key = (chapter_id, paragraph_index)
            if current_paragraph_key is not None and paragraph_key != current_paragraph_key:
                paragraph_end_positions[current_paragraph_key] = position - 1
            current_paragraph_key = paragraph_key
        if current_paragraph_key is not None:
            paragraph_end_positions[current_paragraph_key] = len(flat_sentences) - 1
        if chapter_sentences:
            chapter_end_positions[chapter_id] = len(flat_sentences) - 1
    return flat_sentences, sentence_index, paragraph_end_positions, chapter_end_positions


def _normalize_with_offsets(value: str, offsets: list[Any] | None = None) -> tuple[str, list[Any]]:
    raw_offsets = offsets if offsets is not None else [None] * len(value)
    chars: list[tuple[str, Any]] = []
    for character, offset in zip(value, raw_offsets, strict=False):
        normalized = unicodedata.normalize("NFKC", character)
        normalized = normalized.replace("“", '"').replace("”", '"')
        normalized = normalized.replace("’", "'").replace("–", "-").replace("—", "-")
        normalized = normalized.replace("…", "...")
        normalized = normalized.lower()
        for item in normalized:
            chars.append((" " if item.isspace() else item, offset))

    collapsed: list[tuple[str, Any]] = []
    for character, offset in chars:
        if character == " " and (not collapsed or collapsed[-1][0] == " "):
            continue
        collapsed.append((character, offset))
    while collapsed and collapsed[0][0] == " ":
        collapsed.pop(0)
    while collapsed and collapsed[-1][0] == " ":
        collapsed.pop()

    punctuation = set(",.;:!?()\"'")
    filtered: list[tuple[str, Any]] = []
    for index, (character, offset) in enumerate(collapsed):
        if character == " ":
            previous_character = collapsed[index - 1][0] if index > 0 else ""
            next_character = collapsed[index + 1][0] if index + 1 < len(collapsed) else ""
            if previous_character in punctuation or next_character in punctuation:
                continue
        filtered.append((character, offset))
    return "".join(character for character, _offset in filtered), [offset for _character, offset in filtered]


def _render_segment_source(
    *,
    flat_sentences: list[dict[str, Any]],
    start_position: int,
    end_position: int,
    language_track: str,
) -> tuple[str, dict[str, dict[str, Any]], dict[int, str]]:
    lines: list[str] = []
    current_chapter_id: int | None = None
    current_paragraph_key: tuple[int, int] | None = None
    current_paragraph_sentences: list[dict[str, Any]] = []
    segment_paragraph_index = 0
    sentence_spans: dict[str, dict[str, Any]] = {}
    paragraph_texts: dict[int, str] = {}

    def append_blank_line() -> None:
        if lines and lines[-1] != "":
            lines.append("")

    def emit_source_paragraph(sentences: list[dict[str, Any]]) -> None:
        nonlocal segment_paragraph_index
        if not sentences:
            return
        paragraph_text = _join_sentence_texts(sentences, language_track=language_track)
        if not paragraph_text:
            return
        segment_paragraph_index += 1
        paragraph_texts[segment_paragraph_index] = paragraph_text
        search_from = 0
        for sentence in sentences:
            sentence_text = _clean_text(sentence.get("text"))
            if not sentence_text:
                continue
            char_start = paragraph_text.find(sentence_text, search_from)
            if char_start < 0:
                char_start = search_from
            char_end = char_start + len(sentence_text)
            search_from = char_end
            sentence_spans[str(sentence["sentence_id"])] = {
                "paragraph_index": segment_paragraph_index,
                "char_start": char_start,
                "char_end": char_end,
                "source_chapter_id": int(sentence["chapter_id"]),
                "source_paragraph_index": int(sentence["paragraph_index"]),
                "source_locator": dict(sentence.get("locator") or {}),
            }
        lines.append(paragraph_text)

    for sentence in flat_sentences[start_position : end_position + 1]:
        chapter_id = int(sentence["chapter_id"])
        paragraph_key = (chapter_id, int(sentence["paragraph_index"]))
        if current_chapter_id != chapter_id:
            if current_paragraph_sentences:
                emit_source_paragraph(current_paragraph_sentences)
                append_blank_line()
                current_paragraph_sentences = []
            append_blank_line()
            segment_paragraph_index += 1
            chapter_title_text = str(sentence["chapter_title"])
            paragraph_texts[segment_paragraph_index] = chapter_title_text
            lines.append(chapter_title_text)
            append_blank_line()
            current_chapter_id = chapter_id
            current_paragraph_key = None
        if current_paragraph_key is not None and paragraph_key != current_paragraph_key:
            emit_source_paragraph(current_paragraph_sentences)
            append_blank_line()
            current_paragraph_sentences = []
        current_paragraph_key = paragraph_key
        current_paragraph_sentences.append(sentence)
    if current_paragraph_sentences:
        emit_source_paragraph(current_paragraph_sentences)
    return "\n".join(line.rstrip() for line in lines).strip() + "\n", sentence_spans, paragraph_texts


def _note_source_span(
    *,
    note: AlignedNote,
    flat_sentences: list[dict[str, Any]],
    sentence_index: dict[str, int],
    language_track: str,
    segment_sentence_spans: dict[str, dict[str, Any]],
    segment_paragraph_texts: dict[int, str],
    segment_id: str,
) -> tuple[str, list[str], list[dict[str, Any]]]:
    start_index = sentence_index[note.start_sentence_id]
    end_index = sentence_index[note.end_sentence_id]
    span_sentences = flat_sentences[start_index : end_index + 1]
    try:
        return _note_source_span_from_sentences(
            note=note,
            span_sentences=span_sentences,
            language_track=language_track,
            segment_sentence_spans=segment_sentence_spans,
            segment_paragraph_texts=segment_paragraph_texts,
            segment_id=segment_id,
            relocated=False,
        )
    except ValueError:
        relocated = _relocate_note_source_span(
            note=note,
            flat_sentences=flat_sentences,
            language_track=language_track,
            segment_sentence_spans=segment_sentence_spans,
            segment_paragraph_texts=segment_paragraph_texts,
            segment_id=segment_id,
        )
        if relocated is not None:
            return relocated
        raise


def _note_source_span_from_sentences(
    *,
    note: AlignedNote,
    span_sentences: list[dict[str, Any]],
    language_track: str,
    segment_sentence_spans: dict[str, dict[str, Any]],
    segment_paragraph_texts: dict[int, str],
    segment_id: str,
    relocated: bool,
) -> tuple[str, list[str], list[dict[str, Any]]]:
    normalized_parts: list[str] = []
    normalized_offsets: list[tuple[int, int] | None] = []
    previous_normalized = ""
    for sentence in span_sentences:
        sentence_id = str(sentence["sentence_id"])
        segment_span = segment_sentence_spans.get(sentence_id)
        if not segment_span:
            raise ValueError(f"Missing segment-source locator for note {note.note_id} sentence {sentence_id}")
        sentence_text = _clean_text(sentence.get("text"))
        char_start = int(segment_span["char_start"])
        source_offsets = [
            (int(segment_span["paragraph_index"]), char_start + offset)
            for offset in range(len(sentence_text))
        ]
        normalized_sentence, sentence_offsets = _normalize_with_offsets(sentence_text, source_offsets)
        joiner = _normalized_join_separator(previous_normalized, normalized_sentence)
        if joiner:
            normalized_parts.append(joiner)
            normalized_offsets.extend([None] * len(joiner))
        normalized_parts.append(normalized_sentence)
        normalized_offsets.extend(sentence_offsets)
        previous_normalized = normalized_sentence

    normalized_source = "".join(normalized_parts)
    match_text_candidates = [note.note_text]
    if note.aligned_text and note.aligned_text not in match_text_candidates:
        match_text_candidates.append(note.aligned_text)
    match_start = -1
    normalized_note = ""
    matched_source_text_kind = ""
    for match_text in match_text_candidates:
        normalized_candidate, _note_offsets = _normalize_with_offsets(match_text)
        candidate_start = normalized_source.find(normalized_candidate)
        if candidate_start >= 0:
            match_start = candidate_start
            normalized_note = normalized_candidate
            matched_source_text_kind = "note_text" if match_text == note.note_text else "aligned_text"
            if relocated:
                matched_source_text_kind = f"{matched_source_text_kind}_relocated_by_text"
            break
    if match_start < 0:
        raise ValueError(
            f"Aligned note {note.note_id} cannot be mapped to a segment-source char span; "
            f"neither note_text nor aligned_text is an exact normalized substring of the aligned source sentences."
        )
    match_end = match_start + len(normalized_note)
    matched_offsets = [offset for offset in normalized_offsets[match_start:match_end] if offset is not None]
    if not matched_offsets:
        raise ValueError(f"Aligned note {note.note_id} mapped only to separator characters")

    slices: list[dict[str, Any]] = []
    by_paragraph: dict[int, list[int]] = defaultdict(list)
    for paragraph_index, char_offset in matched_offsets:
        by_paragraph[int(paragraph_index)].append(int(char_offset))
    source_sentence_ids = [str(sentence["sentence_id"]) for sentence in span_sentences]
    for paragraph_index in sorted(by_paragraph):
        offsets = by_paragraph[paragraph_index]
        char_start = min(offsets)
        char_end = max(offsets) + 1
        paragraph_text = segment_paragraph_texts.get(paragraph_index, "")
        slices.append(
            {
                "coordinate_system": "segment_source_v1",
                "segment_id": segment_id,
                "source_id": note.source_id,
                "paragraph_index": paragraph_index,
                "char_start": char_start,
                "char_end": char_end,
                "text": paragraph_text[char_start:char_end],
                "source_sentence_ids": source_sentence_ids,
                "matched_source_text_kind": matched_source_text_kind,
            }
        )
    source_span_text = "\n\n".join(slice_payload["text"] for slice_payload in slices if slice_payload["text"])
    return source_span_text, source_sentence_ids, slices


def _relocate_note_source_span(
    *,
    note: AlignedNote,
    flat_sentences: list[dict[str, Any]],
    language_track: str,
    segment_sentence_spans: dict[str, dict[str, Any]],
    segment_paragraph_texts: dict[int, str],
    segment_id: str,
) -> tuple[str, list[str], list[dict[str, Any]]] | None:
    matches: list[tuple[str, list[str], list[dict[str, Any]]]] = []
    current_key: tuple[int, int] | None = None
    current_sentences: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal current_sentences
        if not current_sentences:
            return
        try:
            matches.append(
                _note_source_span_from_sentences(
                    note=note,
                    span_sentences=current_sentences,
                    language_track=language_track,
                    segment_sentence_spans=segment_sentence_spans,
                    segment_paragraph_texts=segment_paragraph_texts,
                    segment_id=segment_id,
                    relocated=True,
                )
            )
        except ValueError:
            pass
        current_sentences = []

    for sentence in flat_sentences:
        if int(sentence.get("chapter_id", 0) or 0) != note.source_chapter_id:
            continue
        sentence_id = _clean_text(sentence.get("sentence_id"))
        if sentence_id not in segment_sentence_spans:
            continue
        key = (int(sentence.get("chapter_id", 0) or 0), int(sentence.get("paragraph_index", 0) or 0))
        if current_key is not None and key != current_key:
            flush()
        current_key = key
        current_sentences.append(sentence)
    flush()

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(
            f"Aligned note {note.note_id} has ambiguous relocated exact matches in chapter {note.source_chapter_id}."
        )
    return None


def _render_segment_text(
    *,
    flat_sentences: list[dict[str, Any]],
    start_position: int,
    end_position: int,
    language_track: str,
) -> str:
    rendered, _sentence_spans, _paragraph_texts = _render_segment_source(
        flat_sentences=flat_sentences,
        start_position=start_position,
        end_position=end_position,
        language_track=language_track,
    )
    return rendered


def _section_end_position(
    *,
    flat_sentences: list[dict[str, Any]],
    threshold_position: int,
    limit_position: int,
    paragraph_end_positions: dict[tuple[int, int], int],
) -> int | None:
    for position in range(threshold_position + 1, min(limit_position, len(flat_sentences) - 1) + 1):
        sentence = flat_sentences[position]
        if _clean_text(sentence.get("text_role")) != "heading":
            continue
        previous = position - 1
        if previous < threshold_position:
            continue
        paragraph_key = (int(flat_sentences[previous]["chapter_id"]), int(flat_sentences[previous]["paragraph_index"]))
        section_end = paragraph_end_positions.get(paragraph_key)
        if section_end is not None and threshold_position <= section_end <= limit_position:
            return section_end
    return None


def _choose_segment_end(
    *,
    target_note: AlignedNote,
    target_note_end_position: int,
    flat_sentences: list[dict[str, Any]],
    chapter_end_positions: dict[int, int],
    paragraph_end_positions: dict[tuple[int, int], int],
    hard_sentence_cap: int,
) -> tuple[int, str]:
    chapter_end = chapter_end_positions[target_note.source_chapter_id]
    additional_sentences = chapter_end - target_note_end_position
    if additional_sentences <= hard_sentence_cap:
        return chapter_end, "chapter_end_after_target_notes"
    limit_position = min(len(flat_sentences) - 1, target_note_end_position + hard_sentence_cap)
    section_end = _section_end_position(
        flat_sentences=flat_sentences,
        threshold_position=target_note_end_position,
        limit_position=limit_position,
        paragraph_end_positions=paragraph_end_positions,
    )
    if section_end is not None:
        return section_end, "section_end_after_hard_cap"
    paragraph_key = (
        int(flat_sentences[limit_position]["chapter_id"]),
        int(flat_sentences[limit_position]["paragraph_index"]),
    )
    paragraph_end = paragraph_end_positions.get(paragraph_key, limit_position)
    if paragraph_end < target_note_end_position:
        paragraph_end = limit_position
    return min(paragraph_end, limit_position), "paragraph_end_after_hard_cap"


def _catalog_asset_by_source_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for asset in catalog.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        source_id = _clean_text(asset.get("linked_source_id"))
        if source_id:
            index[source_id] = dict(asset)
    return index


def _source_output_dir(root: Path, source_id: str) -> Path:
    safe_source_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", source_id).strip("_") or "source"
    return root / safe_source_id


def _load_jsonl_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _source_normalization_diagnostics(parse_output_dir: Path) -> dict[str, Any]:
    diagnostics_path = parse_diagnostics_file(parse_output_dir)
    if not diagnostics_path.exists():
        return {
            "status": "missing",
            "path": _relative_to_root(diagnostics_path),
        }
    payload = _load_json(diagnostics_path)
    source_normalization = payload.get("source_normalization")
    if not isinstance(source_normalization, dict):
        return {
            "status": "missing_source_normalization",
            "path": _relative_to_root(diagnostics_path),
        }
    result = dict(source_normalization)
    result["path"] = _relative_to_root(diagnostics_path)
    return result


def _book_document_path(parse_output_dir: Path) -> Path:
    return parse_output_dir / "public" / "book_document.json"


def _collect_source_normalization_examples(parse_output_dir: Path) -> dict[str, Any]:
    book_document_path = _book_document_path(parse_output_dir)
    if not book_document_path.exists():
        return {
            "book_document_path": _relative_to_root(book_document_path),
            "auxiliary_examples": [],
            "orphan_note_like_candidates": [],
        }
    document = _load_json(book_document_path)
    auxiliary_examples: list[dict[str, Any]] = []
    orphan_candidates: list[dict[str, Any]] = []
    for chapter in document.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        chapter_title_value = _clean_text(chapter.get("title"))
        for paragraph in chapter.get("paragraphs") or []:
            if not isinstance(paragraph, dict):
                continue
            source_normalization = paragraph.get("source_normalization") or {}
            if not isinstance(source_normalization, dict):
                source_normalization = {}
            evidence = source_normalization.get("evidence") or {}
            signals = evidence.get("signals") if isinstance(evidence, dict) else []
            if not isinstance(signals, list):
                signals = []
            record = {
                "chapter_id": chapter_id,
                "chapter_title": chapter_title_value,
                "paragraph_index": int(paragraph.get("paragraph_index", 0) or 0),
                "text_role": _clean_text(paragraph.get("text_role")),
                "normalized_role": _clean_text(source_normalization.get("normalized_role")),
                "method": _clean_text(source_normalization.get("method")),
                "reason_code": _clean_text(source_normalization.get("reason_code")),
                "signals": [str(item) for item in signals],
                "text": _clean_text(paragraph.get("text"))[:240],
            }
            if record["text_role"] == "auxiliary" and len(auxiliary_examples) < 20:
                auxiliary_examples.append(record)
            if "orphan_note_like_candidate" in record["signals"] and len(orphan_candidates) < 20:
                orphan_candidates.append(record)
    return {
        "book_document_path": _relative_to_root(book_document_path),
        "auxiliary_examples": auxiliary_examples,
        "orphan_note_like_candidates": orphan_candidates,
    }


def _slice_int_field(item: dict[str, Any], key: str) -> int:
    value = item.get(key, -1)
    if value is None or value == "":
        return -1
    return int(value)


def _first_slice_key(row: dict[str, Any]) -> tuple[int, int, int] | None:
    slices = row.get("source_span_slices")
    if not isinstance(slices, list):
        return None
    for item in slices:
        if not isinstance(item, dict):
            continue
        return (
            _slice_int_field(item, "paragraph_index"),
            _slice_int_field(item, "char_start"),
            _slice_int_field(item, "char_end"),
        )
    return None


def _note_case_span_key(row: dict[str, Any]) -> tuple[object, ...]:
    slices = row.get("source_span_slices")
    if not isinstance(slices, list) or not slices:
        return (row.get("segment_id"), row.get("note_case_id"))
    parts: list[tuple[object, ...]] = []
    for item in slices:
        if not isinstance(item, dict):
            continue
        parts.append(
            (
                item.get("coordinate_system") or row.get("source_span_coordinate_system") or "segment_source_v1",
                item.get("segment_id") or row.get("segment_id"),
                item.get("source_id") or row.get("source_id"),
                _slice_int_field(item, "paragraph_index"),
                _slice_int_field(item, "char_start"),
                _slice_int_field(item, "char_end"),
            )
        )
    if not parts:
        return (row.get("segment_id"), row.get("note_case_id"))
    return tuple(parts)


def _note_case_aliases(row: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    if _clean_text(row.get("note_id")):
        aliases.append(_clean_text(row.get("note_id")))
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    for alias in provenance.get("duplicate_note_aliases") or []:
        alias_text = _clean_text(alias)
        if alias_text:
            aliases.append(alias_text)
    return aliases


def _dedupe_note_case_rows(note_case_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    groups: dict[tuple[object, ...], list[dict[str, Any]]] = {}
    order: list[tuple[object, ...]] = []
    for row in note_case_rows:
        key = _note_case_span_key(row)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    deduped: list[dict[str, Any]] = []
    duplicate_groups: list[dict[str, Any]] = []
    for key in order:
        group = groups[key]
        canonical = dict(group[0])
        provenance = dict(canonical.get("provenance") or {})
        aliases: list[str] = []
        for duplicate in group:
            aliases.extend(_note_case_aliases(duplicate))
        canonical_id = _clean_text(canonical.get("note_id"))
        alias_ids = []
        seen_aliases = {canonical_id} if canonical_id else set()
        for alias in aliases:
            if alias in seen_aliases:
                continue
            seen_aliases.add(alias)
            alias_ids.append(alias)
        if alias_ids:
            provenance["duplicate_note_aliases"] = alias_ids
            provenance["duplicate_note_group_size"] = len(seen_aliases)
            canonical["provenance"] = provenance
        if len(group) > 1:
            duplicate_groups.append(
                {
                    "canonical_note_case_id": canonical.get("note_case_id"),
                    "duplicate_note_case_ids": [
                        _clean_text(item.get("note_case_id"))
                        for item in group[1:]
                        if _clean_text(item.get("note_case_id"))
                    ],
                    "duplicate_note_aliases": alias_ids,
                    "duplicate_note_group_size": len(seen_aliases),
                }
            )
        deduped.append(canonical)

    return deduped, {
        "raw_note_case_count": len(note_case_rows),
        "unique_note_case_count": len(deduped),
        "duplicate_note_case_count": len(note_case_rows) - len(deduped),
        "duplicate_note_case_group_count": len(duplicate_groups),
        "duplicate_note_case_groups": duplicate_groups[:20],
    }


def _coordinate_remap_summary(dataset_root: Path, baseline_dataset_dir: Path | None) -> dict[str, Any]:
    candidate_rows = _load_jsonl_file(dataset_root / NOTE_CASES_FILE)
    candidate_by_id = {str(row.get("note_case_id") or ""): row for row in candidate_rows}
    candidate_empty = [
        note_case_id
        for note_case_id, row in candidate_by_id.items()
        if not isinstance(row.get("source_span_slices"), list) or not row.get("source_span_slices")
    ]
    summary: dict[str, Any] = {
        "candidate_note_case_count": len(candidate_rows),
        "candidate_empty_source_span_slice_count": len(candidate_empty),
        "candidate_empty_source_span_slice_ids": candidate_empty[:20],
    }
    if baseline_dataset_dir is None or not (baseline_dataset_dir / NOTE_CASES_FILE).exists():
        summary["baseline_status"] = "missing"
        return summary

    baseline_rows = _load_jsonl_file(baseline_dataset_dir / NOTE_CASES_FILE)
    baseline_by_id = {str(row.get("note_case_id") or ""): row for row in baseline_rows}
    changed: list[dict[str, Any]] = []
    unchanged_count = 0
    for note_case_id, candidate in sorted(candidate_by_id.items()):
        baseline = baseline_by_id.get(note_case_id)
        if baseline is None:
            continue
        old_key = _first_slice_key(baseline)
        new_key = _first_slice_key(candidate)
        if old_key == new_key:
            unchanged_count += 1
            continue
        if len(changed) < 30:
            changed.append(
                {
                    "note_case_id": note_case_id,
                    "old_first_slice": old_key,
                    "new_first_slice": new_key,
                    "source_span_text": _clean_text(candidate.get("source_span_text"))[:160],
                }
            )
    summary.update(
        {
            "baseline_status": "loaded",
            "baseline_dataset_dir": _relative_to_root(baseline_dataset_dir),
            "baseline_note_case_count": len(baseline_rows),
            "missing_from_candidate_count": len(set(baseline_by_id) - set(candidate_by_id)),
            "missing_from_baseline_count": len(set(candidate_by_id) - set(baseline_by_id)),
            "unchanged_first_slice_count": unchanged_count,
            "changed_first_slice_count": sum(
                1
                for note_case_id, candidate in candidate_by_id.items()
                if note_case_id in baseline_by_id and _first_slice_key(candidate) != _first_slice_key(baseline_by_id[note_case_id])
            ),
            "changed_first_slice_examples": changed,
        }
    )
    return summary


def _marker_checks_for_segment(dataset_root: Path, segment: dict[str, Any]) -> dict[str, Any]:
    source_id = _clean_text(segment.get("source_id"))
    checks = SOURCE_MARKER_CHECKS.get(source_id)
    source_path = dataset_root / _clean_text(segment.get("segment_source_path"))
    text = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
    if checks is None:
        return {
            "source_id": source_id,
            "segment_id": _clean_text(segment.get("segment_id")),
            "status": "no_known_marker_checks",
        }
    absent_results = {
        marker: text.find(marker)
        for marker in checks.get("must_be_absent", [])
    }
    present_results = {
        marker: text.find(marker)
        for marker in checks.get("must_be_present", [])
    }
    residue_results = {
        marker: text.find(marker)
        for marker in checks.get("known_conservative_residue", [])
    }
    failed_absent = [marker for marker, index in absent_results.items() if index >= 0]
    failed_present = [marker for marker, index in present_results.items() if index < 0]
    return {
        "source_id": source_id,
        "segment_id": _clean_text(segment.get("segment_id")),
        "source_path": _relative_to_root(source_path),
        "status": "pass" if not failed_absent and not failed_present else "fail",
        "must_be_absent": absent_results,
        "must_be_present": present_results,
        "known_conservative_residue": residue_results,
        "failed_absent_markers": failed_absent,
        "failed_present_markers": failed_present,
    }


def _old_canonical_output_violation(source_id: str, parse_output_dir: Path | None) -> bool:
    if parse_output_dir is None:
        return False
    relative = _relative_to_root(parse_output_dir)
    return source_id == "xidaduo_private_zh" and relative == "output/悉达多"


def write_candidate_validation_report(
    *,
    dataset_root: Path,
    source_parse_output_dirs: dict[str, Path],
    baseline_dataset_dir: Path | None,
) -> dict[str, Any]:
    manifest = _load_json(dataset_root / "manifest.json")
    segments = _load_jsonl_file(dataset_root / SEGMENTS_FILE)
    note_cases = _load_jsonl_file(dataset_root / NOTE_CASES_FILE)
    note_cases_by_segment: dict[str, int] = defaultdict(int)
    for note_case in note_cases:
        note_cases_by_segment[_clean_text(note_case.get("segment_id"))] += 1

    parse_sources: dict[str, Any] = {}
    old_output_violations: list[str] = []
    for source_id, parse_output_dir in sorted(source_parse_output_dirs.items()):
        if _old_canonical_output_violation(source_id, parse_output_dir):
            old_output_violations.append(source_id)
        parse_sources[source_id] = {
            "parse_output_dir": _relative_to_root(parse_output_dir),
            "diagnostics": _source_normalization_diagnostics(parse_output_dir),
            **_collect_source_normalization_examples(parse_output_dir),
        }

    marker_checks = [_marker_checks_for_segment(dataset_root, segment) for segment in segments]
    coordinate_remap = _coordinate_remap_summary(dataset_root, baseline_dataset_dir)
    report = {
        "generated_at": utc_now(),
        "dataset_id": manifest.get("dataset_id"),
        "dataset_dir": _relative_to_root(dataset_root),
        "segment_count": len(segments),
        "note_case_count": len(note_cases),
        "note_case_count_by_segment": dict(sorted(note_cases_by_segment.items())),
        "parse_mode": manifest.get("parse_mode", "canonical_existing"),
        "parse_sources": parse_sources,
        "marker_checks": marker_checks,
        "coordinate_remap": coordinate_remap,
        "old_canonical_output_violations": old_output_violations,
        "acceptance_gate_status": "pass"
        if not old_output_violations
        and not any(item.get("status") == "fail" for item in marker_checks)
        and not coordinate_remap.get("candidate_empty_source_span_slice_count")
        else "review_required",
    }
    write_json(dataset_root / DEFAULT_CANDIDATE_VALIDATION_REPORT_JSON, report)
    _write_candidate_validation_markdown(dataset_root / DEFAULT_CANDIDATE_VALIDATION_REPORT_MD, report)
    return report


def _write_candidate_validation_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# User-Level Selective Candidate Validation",
        "",
        f"- generated_at: `{report.get('generated_at')}`",
        f"- dataset_id: `{report.get('dataset_id')}`",
        f"- dataset_dir: `{report.get('dataset_dir')}`",
        f"- parse_mode: `{report.get('parse_mode')}`",
        f"- segment_count: `{report.get('segment_count')}`",
        f"- note_case_count: `{report.get('note_case_count')}`",
        f"- acceptance_gate_status: `{report.get('acceptance_gate_status')}`",
        "",
        "## Marker Checks",
        "",
    ]
    for item in report.get("marker_checks") or []:
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"### `{item.get('segment_id')}`",
                "",
                f"- status: `{item.get('status')}`",
                f"- source_path: `{item.get('source_path', '')}`",
                f"- failed_absent_markers: `{item.get('failed_absent_markers', [])}`",
                f"- failed_present_markers: `{item.get('failed_present_markers', [])}`",
                f"- known_conservative_residue: `{item.get('known_conservative_residue', {})}`",
                "",
            ]
        )
    lines.extend(["## Parse Sources", ""])
    for source_id, source_payload in sorted((report.get("parse_sources") or {}).items()):
        if not isinstance(source_payload, dict):
            continue
        diagnostics = source_payload.get("diagnostics") if isinstance(source_payload.get("diagnostics"), dict) else {}
        lines.extend(
            [
                f"### `{source_id}`",
                "",
                f"- parse_output_dir: `{source_payload.get('parse_output_dir')}`",
                f"- diagnostics_path: `{diagnostics.get('path', '')}`",
                f"- source_normalization_version: `{diagnostics.get('version', '')}`",
                f"- source_normalization_method: `{diagnostics.get('method', '')}`",
                f"- chunk_count: `{diagnostics.get('chunk_count', '')}`",
                f"- classification_count: `{diagnostics.get('classification_count', '')}`",
                f"- applied_exclusion_count: `{diagnostics.get('applied_exclusion_count', '')}`",
                f"- auxiliary_examples: `{len(source_payload.get('auxiliary_examples') or [])}`",
                f"- orphan_note_like_candidates: `{len(source_payload.get('orphan_note_like_candidates') or [])}`",
                "",
            ]
        )
        for example in (source_payload.get("orphan_note_like_candidates") or [])[:5]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"  - orphan candidate C{example.get('chapter_id')} P{example.get('paragraph_index')}: "
                f"{_clean_text(example.get('text'))[:120]}"
            )
        if source_payload.get("orphan_note_like_candidates"):
            lines.append("")
    coordinate_remap = report.get("coordinate_remap") if isinstance(report.get("coordinate_remap"), dict) else {}
    lines.extend(
        [
            "## Coordinate Remap",
            "",
            f"- candidate_note_case_count: `{coordinate_remap.get('candidate_note_case_count')}`",
            f"- candidate_empty_source_span_slice_count: `{coordinate_remap.get('candidate_empty_source_span_slice_count')}`",
            f"- baseline_status: `{coordinate_remap.get('baseline_status')}`",
            f"- baseline_note_case_count: `{coordinate_remap.get('baseline_note_case_count', '')}`",
            f"- changed_first_slice_count: `{coordinate_remap.get('changed_first_slice_count', '')}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_user_level_selective_v1(
    *,
    dataset_dir: Path | None = None,
    dataset_id: str | None = None,
    dataset_version: str | None = None,
    split_manifest_path: Path | None = None,
    target_note_count: int = DEFAULT_TARGET_NOTE_COUNT,
    hard_sentence_cap: int = DEFAULT_HARD_SENTENCE_CAP,
    source_ids: tuple[str, ...] | None = None,
    fresh_parse_output_root: Path | None = None,
    validation_baseline_dataset_dir: Path | None = None,
) -> dict[str, Any]:
    catalog = _load_notes_catalog()
    asset_index = _catalog_asset_by_source_id(catalog)
    source_index = _load_source_index()
    dataset_root = Path(dataset_dir if dataset_dir is not None else DATASET_DIR).resolve()
    resolved_dataset_id = str(dataset_id if dataset_id is not None else DATASET_ID)
    resolved_dataset_version = str(dataset_version if dataset_version is not None else DEFAULT_VERSION)
    resolved_split_manifest_path = (
        Path(split_manifest_path).resolve() if split_manifest_path is not None else MANIFEST_PATH.resolve()
    )

    shutil.rmtree(dataset_root, ignore_errors=True)
    dataset_root.mkdir(parents=True, exist_ok=True)
    segment_sources_dir = dataset_root / SEGMENT_SOURCE_DIRNAME
    segment_sources_dir.mkdir(parents=True, exist_ok=True)

    segments_rows: list[dict[str, Any]] = []
    note_case_rows: list[dict[str, Any]] = []
    selected_source_ids: list[str] = []
    skipped_sources: list[dict[str, str]] = []
    source_deduplication: list[dict[str, Any]] = []
    source_filter = {source_id for source_id in (source_ids or ()) if source_id}
    source_parse_output_dirs: dict[str, Path] = {}
    source_parse_mode = "fresh_isolated" if fresh_parse_output_root is not None else "canonical_existing"
    candidate_metadata_enabled = bool(
        source_filter
        or fresh_parse_output_root is not None
        or validation_baseline_dataset_dir is not None
    )
    selected_registered_source_ids = [
        source_id
        for source_id in REGISTERED_NOTES_SOURCE_IDS
        if not source_filter or source_id in source_filter
    ]
    for unknown_source_id in sorted(source_filter - set(REGISTERED_NOTES_SOURCE_IDS)):
        skipped_sources.append({"source_id": unknown_source_id, "reason": "source_filter_not_registered"})

    for source_id in selected_registered_source_ids:
        asset = asset_index.get(source_id)
        source_record = source_index.get(source_id)
        if asset is None:
            skipped_sources.append({"source_id": source_id, "reason": "missing_notes_asset"})
            continue
        if source_record is None:
            skipped_sources.append({"source_id": source_id, "reason": "missing_source_ref"})
            continue
        aligned_entry_count = int(asset.get("aligned_entry_count", 0) or 0)
        if aligned_entry_count <= 0:
            skipped_sources.append({"source_id": source_id, "reason": "no_aligned_notes"})
            continue

        notes_id = _clean_text(asset.get("notes_id"))
        raw_aligned_notes = _load_aligned_notes(notes_id=notes_id, source_id=source_id)
        aligned_notes, aligned_deduplication = _dedupe_aligned_notes(raw_aligned_notes)
        source_deduplication.append(
            {
                "source_id": source_id,
                "stage": "aligned_note_preselection",
                **aligned_deduplication,
            }
        )
        if len(aligned_notes) < target_note_count:
            skipped_sources.append({"source_id": source_id, "reason": "insufficient_unique_aligned_notes"})
            continue

        book_path = ROOT / _clean_text(source_record["relative_local_path"])
        if fresh_parse_output_root is not None:
            parse_output_dir = _source_output_dir(Path(fresh_parse_output_root).resolve(), source_id)
            shutil.rmtree(parse_output_dir, ignore_errors=True)
            with override_output_dir(parse_output_dir):
                provisioned = ensure_canonical_parse(book_path)
            source_parse_output_dirs[source_id] = parse_output_dir
        else:
            provisioned = ensure_canonical_parse(book_path)
            output_dir = getattr(provisioned, "output_dir", None)
            if isinstance(output_dir, Path):
                source_parse_output_dirs[source_id] = output_dir
        document = provisioned.book_document or {}
        chapters = [chapter for chapter in document.get("chapters") or [] if isinstance(chapter, dict)]
        body_start_index = _find_body_start_index(
            chapters=chapters,
            language_track=provisioned.output_language,
            book_title_value=provisioned.title,
            source_id=source_id,
        )
        flat_sentences, sentence_index, paragraph_end_positions, chapter_end_positions = _flatten_document(
            chapters=chapters,
            start_index=body_start_index,
            language_track=provisioned.output_language,
        )
        if not flat_sentences:
            skipped_sources.append({"source_id": source_id, "reason": "empty_body_segment"})
            continue

        raw_eligible_notes = [
            note
            for note in raw_aligned_notes
            if note.start_sentence_id in sentence_index and note.end_sentence_id in sentence_index
        ]
        eligible_notes = [
            note
            for note in aligned_notes
            if note.start_sentence_id in sentence_index and note.end_sentence_id in sentence_index
        ]
        source_deduplication.append(
            {
                "source_id": source_id,
                "stage": "eligible_after_body_start",
                "raw_note_count": len(raw_eligible_notes),
                "unique_note_count": len(eligible_notes),
                "duplicate_note_count": len(raw_eligible_notes) - len(eligible_notes),
            }
        )
        if len(eligible_notes) < target_note_count:
            skipped_sources.append({"source_id": source_id, "reason": "insufficient_unique_notes_after_body_start"})
            continue

        threshold_note = eligible_notes[target_note_count - 1]
        threshold_position = sentence_index[threshold_note.end_sentence_id]
        segment_end_position, termination_reason = _choose_segment_end(
            target_note=threshold_note,
            target_note_end_position=threshold_position,
            flat_sentences=flat_sentences,
            chapter_end_positions=chapter_end_positions,
            paragraph_end_positions=paragraph_end_positions,
            hard_sentence_cap=hard_sentence_cap,
        )
        segment_notes = [
            note
            for note in eligible_notes
            if sentence_index[note.end_sentence_id] <= segment_end_position
        ]
        raw_segment_notes = [
            note
            for note in raw_eligible_notes
            if sentence_index[note.end_sentence_id] <= segment_end_position
        ]
        segment_start_sentence_id = str(flat_sentences[0]["sentence_id"])
        segment_end_sentence_id = str(flat_sentences[segment_end_position]["sentence_id"])
        covered_source_chapter_ids: list[int] = []
        covered_chapter_titles: list[str] = []
        for sentence in flat_sentences[: segment_end_position + 1]:
            chapter_id = int(sentence["chapter_id"])
            if chapter_id in covered_source_chapter_ids:
                continue
            covered_source_chapter_ids.append(chapter_id)
            covered_chapter_titles.append(str(sentence["chapter_title"]))

        segment_id = f"{source_id}__segment_1"
        segment_source_path = segment_sources_dir / f"{segment_id}.txt"
        segment_source_text, segment_sentence_spans, segment_paragraph_texts = _render_segment_source(
            flat_sentences=flat_sentences,
            start_position=0,
            end_position=segment_end_position,
            language_track=provisioned.output_language,
        )
        segment_source_path.write_text(segment_source_text, encoding="utf-8")

        segments_rows.append(
            {
                "segment_id": segment_id,
                "source_id": source_id,
                "book_title": provisioned.title,
                "author": provisioned.author,
                "language_track": provisioned.output_language,
                "start_sentence_id": segment_start_sentence_id,
                "end_sentence_id": segment_end_sentence_id,
                "source_chapter_ids": covered_source_chapter_ids,
                "chapter_titles": covered_chapter_titles,
                "target_note_count": target_note_count,
                "covered_note_count": len(segment_notes),
                "raw_covered_note_count": len(raw_segment_notes),
                "duplicate_covered_note_count": len(raw_segment_notes) - len(segment_notes),
                "termination_reason": termination_reason,
                "segment_source_path": f"{SEGMENT_SOURCE_DIRNAME}/{segment_id}.txt",
                "source_span_coordinate_system": "segment_source_v1",
            }
        )

        for note in segment_notes:
            source_span_text, source_sentence_ids, source_span_slices = _note_source_span(
                note=note,
                flat_sentences=flat_sentences,
                sentence_index=sentence_index,
                language_track=provisioned.output_language,
                segment_sentence_spans=segment_sentence_spans,
                segment_paragraph_texts=segment_paragraph_texts,
                segment_id=segment_id,
            )
            note_case_rows.append(
                {
                    "note_case_id": f"{source_id}__{note.note_id}",
                    "segment_id": segment_id,
                    "source_id": source_id,
                    "book_title": provisioned.title,
                    "author": provisioned.author,
                    "language_track": provisioned.output_language,
                    "note_id": note.note_id,
                    "note_text": note.note_text,
                    "note_comment": note.note_comment,
                    "source_span_text": source_span_text,
                    "source_sentence_ids": source_sentence_ids,
                    "source_span_coordinate_system": "segment_source_v1",
                    "source_span_slices": source_span_slices,
                    "source_chapter_id": note.source_chapter_id,
                    "chapter_title": note.chapter_title,
                    "section_label": note.section_label,
                    "raw_locator": note.raw_locator,
                    "provenance": {
                        "notes_id": note.notes_id,
                        "entry_file": _relative_to_root(_entry_file_path(note.notes_id)),
                        "alignment_match_type": note.alignment_match_type,
                        "alignment_score": note.alignment_score,
                        "start_sentence_id": note.start_sentence_id,
                        "end_sentence_id": note.end_sentence_id,
                        "source_coordinate_note": "source_span_slices are in the rendered reading segment coordinate system; source_sentence_ids preserve original parsed-book provenance.",
                        "duplicate_note_aliases": list(note.duplicate_note_aliases),
                        "duplicate_note_group_size": note.duplicate_note_group_size,
                    },
                }
            )
        selected_source_ids.append(source_id)

    raw_note_case_count = len(note_case_rows)
    note_case_rows, final_deduplication = _dedupe_note_case_rows(note_case_rows)
    unique_counts_by_segment: dict[str, int] = defaultdict(int)
    for note_case in note_case_rows:
        unique_counts_by_segment[_clean_text(note_case.get("segment_id"))] += 1
    for segment in segments_rows:
        segment_id = _clean_text(segment.get("segment_id"))
        segment["covered_note_count"] = unique_counts_by_segment.get(segment_id, 0)
    raw_covered_note_count = sum(int(row.get("raw_covered_note_count", row.get("covered_note_count", 0)) or 0) for row in segments_rows)
    duplicate_covered_note_count = sum(int(row.get("duplicate_covered_note_count", 0) or 0) for row in segments_rows)

    manifest_payload = {
        "dataset_id": resolved_dataset_id,
        "family": "user_level_note_aligned_benchmark",
        "status": "active",
        "version": resolved_dataset_version,
        "generated_at": utc_now(),
        "description": "Active user-level selective benchmark built directly from aligned human note spans and continuous reading segments.",
        "segments_file": SEGMENTS_FILE,
        "note_cases_file": NOTE_CASES_FILE,
        "registered_source_ids": list(selected_registered_source_ids),
        "eligible_source_ids": selected_source_ids,
        "skipped_sources": skipped_sources,
        "target_note_count": target_note_count,
        "hard_sentence_cap": hard_sentence_cap,
        "segment_count": len(segments_rows),
        "note_case_count": len(note_case_rows),
        "raw_covered_note_count": raw_covered_note_count,
        "duplicate_covered_note_count": duplicate_covered_note_count,
        "raw_note_case_count": raw_note_case_count,
        "duplicate_note_case_count": raw_note_case_count - len(note_case_rows),
        "deduplication": {
            "policy": "unique_source_span_with_raw_export_aliases",
            "target_note_count_basis": "unique_note_cases",
            "aligned_note_stages": source_deduplication,
            "final_note_case_stage": final_deduplication,
        },
        "source_manifest_refs": [
            _relative_to_root(DEFAULT_NOTES_LOCAL_REF_MANIFEST),
        ],
        "notes_catalog_path": _relative_to_root(DEFAULT_NOTES_CATALOG_PATH),
        "supersedes": [
            "eval/manifests/splits/attentional_v2_excerpt_surface_v1_1_draft.json",
            "state/eval_local_datasets/excerpt_cases/attentional_v2_excerpt_surface_v1_1_excerpt_en",
            "state/eval_local_datasets/excerpt_cases/attentional_v2_excerpt_surface_v1_1_excerpt_zh",
        ],
    }
    if candidate_metadata_enabled:
        manifest_payload.update(
            {
                "parse_mode": source_parse_mode,
                "source_filter": sorted(source_filter),
                "fresh_parse_output_root": _relative_to_root(Path(fresh_parse_output_root).resolve()) if fresh_parse_output_root is not None else "",
                "source_parse_outputs": {
                    source_id: _relative_to_root(output_dir)
                    for source_id, output_dir in sorted(source_parse_output_dirs.items())
                },
            }
        )
    write_json(dataset_root / "manifest.json", manifest_payload)
    write_jsonl(dataset_root / SEGMENTS_FILE, segments_rows)
    write_jsonl(dataset_root / NOTE_CASES_FILE, note_case_rows)

    split_payload = {
        "manifest_id": MANIFEST_ID,
        "description": "Active user-level selective benchmark built from note-aligned continuous reading segments.",
        "status": "active",
        "supersedes": [
            "attentional_v2_excerpt_surface_v1_1_draft",
        ],
        "targets": [
            "reader_character.selective_legibility",
        ],
        "benchmark_shape": {
            "kind": "user_level_selective_v1",
            "surface_role": "user_level_note_aligned",
            "reading_segments": len(segments_rows),
            "target_note_count": target_note_count,
            "hard_sentence_cap": hard_sentence_cap,
            "note_case_count": len(note_case_rows),
            "raw_covered_note_count": raw_covered_note_count,
            "duplicate_covered_note_count": duplicate_covered_note_count,
            "raw_note_case_count": raw_note_case_count,
            "duplicate_note_case_count": raw_note_case_count - len(note_case_rows),
        },
        "source_refs": {
            "source_manifests": [
                _relative_to_root(DEFAULT_NOTES_LOCAL_REF_MANIFEST),
            ],
            "notes_catalog": _relative_to_root(DEFAULT_NOTES_CATALOG_PATH),
            "user_level_dataset_roots": [
                _relative_to_root(dataset_root),
            ],
        },
        "selected_segments": [
            {
                "segment_id": row["segment_id"],
                "source_id": row["source_id"],
                "book_title": row["book_title"],
                "language_track": row["language_track"],
                "covered_note_count": row["covered_note_count"],
                "raw_covered_note_count": row.get("raw_covered_note_count", row["covered_note_count"]),
                "duplicate_covered_note_count": row.get("duplicate_covered_note_count", 0),
                "termination_reason": row["termination_reason"],
            }
            for row in segments_rows
        ],
        "skipped_sources": skipped_sources,
        "quota_status": {
            "reading_segments": {
                "registered_sources": len(selected_registered_source_ids),
                "ready_now": len(segments_rows),
                "skipped": len(skipped_sources),
            },
            "note_cases": {
                "ready_now": len(note_case_rows),
                "raw_covered_now": raw_covered_note_count,
                "duplicate_covered_note_count": duplicate_covered_note_count,
                "raw_ready_now": raw_note_case_count,
                "duplicate_note_case_count": raw_note_case_count - len(note_case_rows),
            },
        },
        "splits": {
            "selective_legibility_note_cases_v1": {
                "by_segment": {
                    row["segment_id"]: [
                        case["note_case_id"]
                        for case in note_case_rows
                        if case["segment_id"] == row["segment_id"]
                    ]
                    for row in segments_rows
                },
                "all": [case["note_case_id"] for case in note_case_rows],
            }
        },
    }
    if split_manifest_path is not None:
        write_json(resolved_split_manifest_path, split_payload)
    if candidate_metadata_enabled:
        baseline_dataset_dir = (
            Path(validation_baseline_dataset_dir).resolve()
            if validation_baseline_dataset_dir is not None
            else (Path(DATASET_DIR).resolve() if Path(DATASET_DIR).resolve() != dataset_root else None)
        )
        write_candidate_validation_report(
            dataset_root=dataset_root,
            source_parse_output_dirs=source_parse_output_dirs,
            baseline_dataset_dir=baseline_dataset_dir,
        )
    return split_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=DATASET_DIR)
    parser.add_argument("--dataset-id", default=DATASET_ID)
    parser.add_argument("--dataset-version", default=DEFAULT_VERSION)
    parser.add_argument("--split-manifest-path", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--skip-split-manifest", action="store_true")
    parser.add_argument("--target-note-count", type=int, default=DEFAULT_TARGET_NOTE_COUNT)
    parser.add_argument("--hard-sentence-cap", type=int, default=DEFAULT_HARD_SENTENCE_CAP)
    parser.add_argument("--source-id", action="append", default=None, help="Build only this registered source id; repeatable.")
    parser.add_argument(
        "--fresh-parse-output-root",
        type=Path,
        default=None,
        help="Force fresh per-source parses under this ignored output root.",
    )
    parser.add_argument(
        "--validation-baseline-dataset-dir",
        type=Path,
        default=None,
        help="Optional baseline dataset root for coordinate remap reporting.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_user_level_selective_v1(
        dataset_dir=Path(args.dataset_dir),
        dataset_id=str(args.dataset_id),
        dataset_version=str(args.dataset_version),
        split_manifest_path=None if args.skip_split_manifest else Path(args.split_manifest_path),
        target_note_count=int(args.target_note_count),
        hard_sentence_cap=int(args.hard_sentence_cap),
        source_ids=tuple(str(source_id) for source_id in (args.source_id or [])) or None,
        fresh_parse_output_root=Path(args.fresh_parse_output_root) if args.fresh_parse_output_root else None,
        validation_baseline_dataset_dir=(
            Path(args.validation_baseline_dataset_dir) if args.validation_baseline_dataset_dir else None
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
