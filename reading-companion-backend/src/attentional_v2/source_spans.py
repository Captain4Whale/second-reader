"""Paragraph-offset source-span helpers for attentional_v2 mainline reading."""

from __future__ import annotations

from typing import Mapping, TypedDict

from .schemas import ReaderPolicy


class SourceCursor(TypedDict, total=False):
    """Cursor over canonical chapter paragraphs."""

    chapter_id: int
    chapter_ref: str
    paragraph_index: int
    char_offset: int


class SourceSpan(TypedDict, total=False):
    """End-exclusive source range over canonical chapter paragraphs."""

    start_cursor: SourceCursor
    end_cursor: SourceCursor


class PreviewParagraphSlice(TypedDict, total=False):
    """One paragraph slice exposed inside a Navigate preview."""

    paragraph_index: int
    text_role: str
    start_char: int
    end_char: int
    text: str
    flat_start: int
    flat_end: int


class ParagraphOffsetPreview(TypedDict, total=False):
    """Adaptive source preview built from the current paragraph-offset cursor."""

    chapter_id: int
    chapter_ref: str
    preview_start_cursor: SourceCursor
    preview_end_cursor: SourceCursor
    source_text: str
    paragraph_slices: list[PreviewParagraphSlice]
    truncated: bool
    char_count: int
    paragraph_count: int


class AnchorResolution(TypedDict, total=False):
    """Deterministic end-anchor resolution outcome."""

    status: str
    method: str
    end_cursor: SourceCursor
    matched_text: str
    match_count: int
    reason: str


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def readable_paragraphs(chapter: Mapping[str, object]) -> list[dict[str, object]]:
    """Return source-order paragraphs that should enter the mainline reader."""

    paragraphs: list[dict[str, object]] = []
    for raw in chapter.get("paragraphs", []):
        if not isinstance(raw, Mapping):
            continue
        paragraph = dict(raw)
        text = _clean_text(paragraph.get("text"))
        text_role = _clean_text(paragraph.get("text_role")) or "body"
        if not text or text_role == "auxiliary":
            continue
        paragraphs.append(paragraph)
    return paragraphs


def _chapter_id(chapter: Mapping[str, object]) -> int:
    return _int(chapter.get("id"))


def _chapter_ref(chapter: Mapping[str, object]) -> str:
    return _clean_text(chapter.get("reference")) or _clean_text(chapter.get("title")) or str(_chapter_id(chapter))


def _paragraph_index(paragraph: Mapping[str, object]) -> int:
    return _int(paragraph.get("paragraph_index"))


def _paragraph_text(paragraph: Mapping[str, object]) -> str:
    return str(paragraph.get("text", "") or "")


def source_cursor(
    *,
    chapter_id: int,
    chapter_ref: str,
    paragraph_index: int,
    char_offset: int,
) -> SourceCursor:
    """Build one normalized source cursor dictionary."""

    return {
        "chapter_id": int(chapter_id),
        "chapter_ref": _clean_text(chapter_ref),
        "paragraph_index": max(0, int(paragraph_index)),
        "char_offset": max(0, int(char_offset)),
    }


def source_span_id(span: Mapping[str, object] | None) -> str:
    """Return a compact deterministic id for one source span."""

    if not isinstance(span, Mapping):
        return ""
    start = span.get("start_cursor")
    end = span.get("end_cursor")
    if not isinstance(start, Mapping) or not isinstance(end, Mapping):
        return ""
    chapter_id = _int(start.get("chapter_id") or end.get("chapter_id"))
    return (
        f"src:c{chapter_id}:"
        f"p{_int(start.get('paragraph_index'))}@{_int(start.get('char_offset'))}-"
        f"p{_int(end.get('paragraph_index'))}@{_int(end.get('char_offset'))}"
    )


def first_cursor_for_chapter(chapter: Mapping[str, object]) -> SourceCursor:
    """Return the first readable paragraph cursor for one chapter."""

    paragraphs = readable_paragraphs(chapter)
    chapter_id = _chapter_id(chapter)
    chapter_ref = _chapter_ref(chapter)
    if not paragraphs:
        return source_cursor(chapter_id=chapter_id, chapter_ref=chapter_ref, paragraph_index=0, char_offset=0)
    return source_cursor(
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        paragraph_index=_paragraph_index(paragraphs[0]),
        char_offset=0,
    )


def chapter_end_cursor(chapter: Mapping[str, object]) -> SourceCursor:
    """Return the end-exclusive cursor at the end of the last readable paragraph."""

    paragraphs = readable_paragraphs(chapter)
    chapter_id = _chapter_id(chapter)
    chapter_ref = _chapter_ref(chapter)
    if not paragraphs:
        return source_cursor(chapter_id=chapter_id, chapter_ref=chapter_ref, paragraph_index=0, char_offset=0)
    last = paragraphs[-1]
    return source_cursor(
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        paragraph_index=_paragraph_index(last),
        char_offset=len(_paragraph_text(last)),
    )


def _paragraph_by_index(chapter: Mapping[str, object]) -> dict[int, dict[str, object]]:
    return {_paragraph_index(paragraph): paragraph for paragraph in readable_paragraphs(chapter)}


def normalize_cursor_for_chapter(
    chapter: Mapping[str, object],
    cursor: Mapping[str, object] | None,
) -> SourceCursor:
    """Clamp a source cursor to the next readable position in a chapter."""

    paragraphs = readable_paragraphs(chapter)
    if not paragraphs:
        return first_cursor_for_chapter(chapter)

    chapter_id = _chapter_id(chapter)
    chapter_ref = _chapter_ref(chapter)
    if not isinstance(cursor, Mapping):
        return first_cursor_for_chapter(chapter)

    requested_index = _int(cursor.get("paragraph_index"), _paragraph_index(paragraphs[0]))
    requested_offset = max(0, _int(cursor.get("char_offset")))
    for paragraph in paragraphs:
        paragraph_index = _paragraph_index(paragraph)
        text_len = len(_paragraph_text(paragraph))
        if paragraph_index < requested_index:
            continue
        if paragraph_index == requested_index:
            if requested_offset < text_len:
                return source_cursor(
                    chapter_id=chapter_id,
                    chapter_ref=chapter_ref,
                    paragraph_index=paragraph_index,
                    char_offset=min(requested_offset, text_len),
                )
            continue
        return source_cursor(
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            paragraph_index=paragraph_index,
            char_offset=0,
        )
    return chapter_end_cursor(chapter)


def cursor_less_than(a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    """Return whether cursor a precedes cursor b within the same chapter."""

    return (
        _int(a.get("chapter_id")),
        _int(a.get("paragraph_index")),
        _int(a.get("char_offset")),
    ) < (
        _int(b.get("chapter_id")),
        _int(b.get("paragraph_index")),
        _int(b.get("char_offset")),
    )


def cursor_equal(a: Mapping[str, object], b: Mapping[str, object]) -> bool:
    """Return whether two cursors identify the same paragraph-offset location."""

    return (
        _int(a.get("chapter_id")),
        _int(a.get("paragraph_index")),
        _int(a.get("char_offset")),
    ) == (
        _int(b.get("chapter_id")),
        _int(b.get("paragraph_index")),
        _int(b.get("char_offset")),
    )


def cursor_at_or_after_chapter_end(chapter: Mapping[str, object], cursor: Mapping[str, object]) -> bool:
    """Return whether the cursor has reached the chapter end cursor."""

    end = chapter_end_cursor(chapter)
    normalized = normalize_cursor_for_chapter(chapter, cursor)
    return cursor_equal(normalized, end) or not cursor_less_than(normalized, end)


def _unitize_policy(reader_policy: ReaderPolicy | Mapping[str, object] | None) -> Mapping[str, object]:
    if not isinstance(reader_policy, Mapping):
        return {}
    unitize = reader_policy.get("unitize")
    return unitize if isinstance(unitize, Mapping) else {}


def _preview_limits(reader_policy: ReaderPolicy | Mapping[str, object] | None) -> tuple[int, int, int]:
    policy = _unitize_policy(reader_policy)
    soft_min = max(1, _int(policy.get("preview_soft_min_chars"), 1500))
    hard_max = max(soft_min, _int(policy.get("preview_hard_max_chars"), 4000))
    max_lookahead = max(0, _int(policy.get("max_lookahead_paragraphs"), 4))
    return soft_min, hard_max, max_lookahead


def build_paragraph_offset_preview(
    *,
    chapter: Mapping[str, object],
    current_cursor: Mapping[str, object],
    reader_policy: ReaderPolicy | Mapping[str, object] | None = None,
) -> ParagraphOffsetPreview:
    """Build the adaptive source preview visible to Navigate."""

    start_cursor = normalize_cursor_for_chapter(chapter, current_cursor)
    chapter_id = _chapter_id(chapter)
    chapter_ref = _chapter_ref(chapter)
    soft_min, hard_max, max_lookahead = _preview_limits(reader_policy)
    paragraphs = readable_paragraphs(chapter)
    if not paragraphs:
        return {
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
            "preview_start_cursor": start_cursor,
            "preview_end_cursor": start_cursor,
            "source_text": "",
            "paragraph_slices": [],
            "truncated": False,
            "char_count": 0,
            "paragraph_count": 0,
        }

    start_position = next(
        (
            index
            for index, paragraph in enumerate(paragraphs)
            if _paragraph_index(paragraph) == _int(start_cursor.get("paragraph_index"))
        ),
        0,
    )
    slices: list[PreviewParagraphSlice] = []
    pieces: list[str] = []
    content_chars = 0
    flat_cursor = 0
    truncated = False
    included_following = 0

    for paragraph_position in range(start_position, len(paragraphs)):
        if paragraph_position > start_position and included_following >= max_lookahead:
            break
        paragraph = paragraphs[paragraph_position]
        text = _paragraph_text(paragraph)
        paragraph_index = _paragraph_index(paragraph)
        start_char = _int(start_cursor.get("char_offset")) if paragraph_position == start_position else 0
        start_char = min(max(0, start_char), len(text))
        if start_char >= len(text):
            continue
        remaining_budget = hard_max - content_chars
        if remaining_budget <= 0:
            truncated = True
            break
        end_char = min(len(text), start_char + remaining_budget)
        piece = text[start_char:end_char]
        if pieces:
            pieces.append("\n\n")
            flat_cursor += 2
        flat_start = flat_cursor
        pieces.append(piece)
        flat_cursor += len(piece)
        slices.append(
            {
                "paragraph_index": paragraph_index,
                "text_role": _clean_text(paragraph.get("text_role")) or "body",
                "start_char": start_char,
                "end_char": end_char,
                "text": piece,
                "flat_start": flat_start,
                "flat_end": flat_cursor,
            }
        )
        content_chars += len(piece)
        if end_char < len(text):
            truncated = True
            break
        if paragraph_position > start_position:
            included_following += 1
        if content_chars >= soft_min:
            break

    if not slices:
        return {
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
            "preview_start_cursor": start_cursor,
            "preview_end_cursor": start_cursor,
            "source_text": "",
            "paragraph_slices": [],
            "truncated": False,
            "char_count": 0,
            "paragraph_count": 0,
        }

    last_slice = slices[-1]
    end_cursor = source_cursor(
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        paragraph_index=last_slice["paragraph_index"],
        char_offset=last_slice["end_char"],
    )
    return {
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "preview_start_cursor": start_cursor,
        "preview_end_cursor": end_cursor,
        "source_text": "".join(pieces),
        "paragraph_slices": slices,
        "truncated": truncated,
        "char_count": content_chars,
        "paragraph_count": len(slices),
    }


def cursor_from_flat_offset(
    preview: Mapping[str, object],
    flat_offset: int,
) -> SourceCursor:
    """Map a preview-text offset back to a paragraph-offset cursor."""

    chapter_id = _int(preview.get("chapter_id"))
    chapter_ref = _clean_text(preview.get("chapter_ref"))
    slices = [dict(item) for item in preview.get("paragraph_slices", []) if isinstance(item, Mapping)]
    if not slices:
        return dict(preview.get("preview_start_cursor", {}))  # type: ignore[return-value]
    for item in slices:
        flat_start = _int(item.get("flat_start"))
        flat_end = _int(item.get("flat_end"))
        if flat_offset <= flat_end:
            in_slice = max(0, min(flat_offset - flat_start, flat_end - flat_start))
            return source_cursor(
                chapter_id=chapter_id,
                chapter_ref=chapter_ref,
                paragraph_index=_int(item.get("paragraph_index")),
                char_offset=_int(item.get("start_char")) + in_slice,
            )
    last = slices[-1]
    return source_cursor(
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        paragraph_index=_int(last.get("paragraph_index")),
        char_offset=_int(last.get("end_char")),
    )


def resolve_end_anchor_text(
    *,
    preview: Mapping[str, object],
    end_anchor_text: str,
) -> AnchorResolution:
    """Resolve an LLM-selected end anchor into an end cursor."""

    source_text = str(preview.get("source_text", "") or "")
    anchor = str(end_anchor_text or "").strip()
    if not anchor:
        return {"status": "missing_anchor", "method": "exact_text", "reason": "end_anchor_text is empty"}
    matches: list[int] = []
    start = 0
    while True:
        index = source_text.find(anchor, start)
        if index < 0:
            break
        matches.append(index)
        start = index + max(1, len(anchor))
    if not matches:
        return {
            "status": "not_found",
            "method": "exact_text",
            "matched_text": anchor,
            "match_count": 0,
            "reason": "end_anchor_text was not found in preview source_text",
        }
    if len(matches) > 1:
        return {
            "status": "ambiguous",
            "method": "exact_text",
            "matched_text": anchor,
            "match_count": len(matches),
            "reason": "end_anchor_text matched more than once in preview source_text",
        }
    end_cursor = cursor_from_flat_offset(preview, matches[0] + len(anchor))
    return {
        "status": "matched",
        "method": "exact_text",
        "end_cursor": end_cursor,
        "matched_text": anchor,
        "match_count": 1,
    }


def fallback_end_cursor_for_preview(preview: Mapping[str, object]) -> SourceCursor:
    """Return a conservative end cursor for unresolved Navigate output."""

    start = preview.get("preview_start_cursor")
    if not isinstance(start, Mapping):
        return dict(preview.get("preview_end_cursor", {}))  # type: ignore[return-value]
    for item in preview.get("paragraph_slices", []):
        if not isinstance(item, Mapping):
            continue
        if _int(item.get("paragraph_index")) == _int(start.get("paragraph_index")):
            return source_cursor(
                chapter_id=_int(preview.get("chapter_id")),
                chapter_ref=_clean_text(preview.get("chapter_ref")),
                paragraph_index=_int(item.get("paragraph_index")),
                char_offset=_int(item.get("end_char")),
            )
    return dict(preview.get("preview_end_cursor", {}))  # type: ignore[return-value]


def source_unit_from_span(
    *,
    chapter: Mapping[str, object],
    source_span: Mapping[str, object],
) -> dict[str, object]:
    """Return canonical text and paragraph slices for an accepted source span."""

    start = source_span.get("start_cursor")
    end = source_span.get("end_cursor")
    if not isinstance(start, Mapping) or not isinstance(end, Mapping):
        return {"source_span": dict(source_span), "source_text": "", "paragraph_slices": []}
    paragraphs_by_index = _paragraph_by_index(chapter)
    start_index = _int(start.get("paragraph_index"))
    end_index = _int(end.get("paragraph_index"))
    pieces: list[str] = []
    slices: list[dict[str, object]] = []
    for paragraph in readable_paragraphs(chapter):
        paragraph_index = _paragraph_index(paragraph)
        if paragraph_index < start_index or paragraph_index > end_index:
            continue
        text = _paragraph_text(paragraphs_by_index[paragraph_index])
        start_char = _int(start.get("char_offset")) if paragraph_index == start_index else 0
        end_char = _int(end.get("char_offset")) if paragraph_index == end_index else len(text)
        start_char = min(max(0, start_char), len(text))
        end_char = min(max(start_char, end_char), len(text))
        piece = text[start_char:end_char]
        if not piece:
            continue
        pieces.append(piece)
        slices.append(
            {
                "paragraph_index": paragraph_index,
                "text_role": _clean_text(paragraph.get("text_role")) or "body",
                "start_char": start_char,
                "end_char": end_char,
                "text": piece,
            }
        )
    source_text = "\n\n".join(pieces)
    return {
        "source_span": {
            "start_cursor": dict(start),
            "end_cursor": dict(end),
        },
        "source_span_id": source_span_id(source_span),
        "source_text": source_text,
        "paragraph_slices": slices,
        "char_count": sum(len(str(item.get("text", "") or "")) for item in slices),
        "paragraph_count": len(slices),
    }


def source_locus_from_unit(source_unit: Mapping[str, object]) -> dict[str, object]:
    """Return a public/additive reading-locus payload for one source unit."""

    source_span = source_unit.get("source_span")
    return {
        "kind": "source_span",
        "source_span_id": _clean_text(source_unit.get("source_span_id")),
        "source_span": dict(source_span) if isinstance(source_span, Mapping) else {},
        "excerpt": str(source_unit.get("source_text", "") or "")[:220],
    }

