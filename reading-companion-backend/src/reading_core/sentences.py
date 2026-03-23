"""Deterministic sentence-layer helpers for the shared parsed-book substrate."""

from __future__ import annotations

from typing import TypedDict

from .book_document import BookDocument, ParagraphRecord, SentenceRecord, TextLocator


_TERMINAL_MARKS = {"。", "！", "？", "!", "?"}
_TRAILING_MARKS = _TERMINAL_MARKS | {".", '"', "'", "”", "’", ")", "]", "}", "）", "】"}


class SentenceSpan(TypedDict):
    """One sentence span within a paragraph-sized text block."""

    char_start: int
    char_end: int
    text: str


def _trim_span(text: str, start: int, end: int) -> SentenceSpan | None:
    """Trim whitespace around one span while preserving character offsets."""

    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if end <= start:
        return None
    return {
        "char_start": start,
        "char_end": end,
        "text": text[start:end],
    }


def split_text_into_sentence_spans(text: str) -> list[SentenceSpan]:
    """Split one text block into stable sentence-like spans."""

    source = text or ""
    spans: list[SentenceSpan] = []
    start = 0
    index = 0
    length = len(source)

    while index < length:
        char = source[index]
        boundary_end: int | None = None
        if char in _TERMINAL_MARKS:
            boundary_end = index + 1
            while boundary_end < length and source[boundary_end] in _TRAILING_MARKS:
                boundary_end += 1
        elif char == ".":
            boundary_end = index + 1
            while boundary_end < length and source[boundary_end] in _TRAILING_MARKS:
                boundary_end += 1
            if boundary_end < length and not source[boundary_end].isspace():
                boundary_end = None

        if boundary_end is None:
            index += 1
            continue

        span = _trim_span(source, start, boundary_end)
        if span is not None:
            spans.append(span)
        start = boundary_end
        index = boundary_end

    tail = _trim_span(source, start, length)
    if tail is not None:
        spans.append(tail)

    return spans


def split_text_into_sentences(text: str) -> list[str]:
    """Split one text block into sentence-like text units only."""

    spans = split_text_into_sentence_spans(text)
    return [span["text"] for span in spans] or [(text or "").strip()]


def _sentence_locator(record: ParagraphRecord, *, char_start: int, char_end: int) -> TextLocator:
    """Build a sentence-level locator grounded in one paragraph record."""

    paragraph_index = int(record.get("paragraph_index", 0) or 0)
    locator: TextLocator = {
        "paragraph_index": paragraph_index,
        "paragraph_start": paragraph_index,
        "paragraph_end": paragraph_index,
        "char_start": char_start,
        "char_end": char_end,
    }
    href = str(record.get("href", "") or "")
    if href:
        locator["href"] = href
    locator["start_cfi"] = record.get("start_cfi")
    locator["end_cfi"] = record.get("end_cfi")
    return locator


def build_sentence_records(
    paragraph_records: list[ParagraphRecord | dict[str, object]],
    *,
    chapter_id: int,
) -> list[SentenceRecord]:
    """Build canonical sentence records from chapter paragraph records."""

    sentences: list[SentenceRecord] = []
    sentence_index = 0

    for raw_record in paragraph_records:
        if not isinstance(raw_record, dict):
            continue
        text = str(raw_record.get("text", "") or "")
        text_role = str(raw_record.get("text_role", "body") or "body")
        if not text.strip() or text_role == "auxiliary":
            continue

        paragraph_index = int(raw_record.get("paragraph_index", 0) or 0)
        spans = split_text_into_sentence_spans(text)
        if not spans:
            fallback = _trim_span(text, 0, len(text))
            spans = [fallback] if fallback is not None else []

        for sentence_in_paragraph, span in enumerate(spans, start=1):
            sentence_index += 1
            sentences.append(
                {
                    "sentence_id": f"c{chapter_id}-s{sentence_index}",
                    "sentence_index": sentence_index,
                    "sentence_in_paragraph": sentence_in_paragraph,
                    "paragraph_index": paragraph_index,
                    "text": span["text"],
                    "text_role": text_role,  # type: ignore[typeddict-item]
                    "locator": _sentence_locator(
                        raw_record,  # type: ignore[arg-type]
                        char_start=span["char_start"],
                        char_end=span["char_end"],
                    ),
                }
            )

    return sentences


def ensure_book_document_sentence_layer(document: BookDocument) -> tuple[BookDocument, bool]:
    """Backfill missing sentence inventories in an existing book document."""

    chapters = document.get("chapters", [])
    upgraded: list[dict[str, object]] = []
    changed = False

    for chapter_index, raw_chapter in enumerate(chapters, start=1):
        if not isinstance(raw_chapter, dict):
            upgraded.append({})
            continue
        chapter = dict(raw_chapter)
        if "sentences" not in chapter and isinstance(chapter.get("paragraphs"), list):
            chapter_id = int(chapter.get("id", chapter_index) or chapter_index)
            chapter["sentences"] = build_sentence_records(
                chapter["paragraphs"],  # type: ignore[arg-type]
                chapter_id=chapter_id,
            )
            changed = True
        upgraded.append(chapter)

    if not changed:
        return document, False

    next_document: BookDocument = {
        "metadata": dict(document.get("metadata", {})),
        "chapters": upgraded,  # type: ignore[typeddict-item]
    }
    return next_document, True
