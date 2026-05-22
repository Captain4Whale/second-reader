"""Paragraph-offset source-span helpers for attentional_v2 mainline reading."""

from __future__ import annotations

import re
from typing import Mapping, TypedDict

from .schemas import ReaderPolicy, SourceRef


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


_NORMALIZED_CHAR_MAP = {
    "“": '"',
    "”": '"',
    "„": '"',
    "＂": '"',
    "‘": "'",
    "’": "'",
    "‚": "'",
    "，": ",",
    "、": ",",
    "；": ";",
    "：": ":",
    "。": ".",
    "！": "!",
    "？": "?",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "—": "-",
    "–": "-",
    "－": "-",
    "…": "...",
}


def _normalized_text_with_map(text: str) -> tuple[str, list[int]]:
    """Normalize quote text while preserving normalized-char -> source-char mapping."""

    normalized: list[str] = []
    source_indexes: list[int] = []
    previous_space = False
    for index, char in enumerate(text):
        if char.isspace():
            if normalized and not previous_space:
                normalized.append(" ")
                source_indexes.append(index)
                previous_space = True
            continue
        mapped = _NORMALIZED_CHAR_MAP.get(char, char)
        for mapped_char in mapped:
            normalized.append(mapped_char)
            source_indexes.append(index)
        previous_space = False
    if normalized and normalized[-1] == " ":
        normalized.pop()
        source_indexes.pop()
    return "".join(normalized), source_indexes


def _find_all(text: str, needle: str, *, start: int = 0) -> list[int]:
    matches: list[int] = []
    if not needle:
        return matches
    cursor = max(0, start)
    while True:
        index = text.find(needle, cursor)
        if index < 0:
            return matches
        matches.append(index)
        cursor = index + max(1, len(needle))


def _quote_fragments(quote: str) -> list[str]:
    parts = re.split(r"[\n\r。！？!?；;]+", quote)
    return [part.strip() for part in parts if len(part.strip()) >= 4]


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


def source_ref_from_span(
    source_span: Mapping[str, object] | None,
    *,
    quote: str = "",
    role: str = "support",
    resolution: Mapping[str, object] | None = None,
) -> SourceRef:
    """Build one inline source ref from an already known paragraph-offset span."""

    span = dict(source_span) if isinstance(source_span, Mapping) else {}
    source_ref: SourceRef = {
        "source_span_id": source_span_id(span),
        "source_span": span,
        "quote": str(quote or ""),
        "role": _clean_text(role) or "support",
    }
    if isinstance(resolution, Mapping):
        source_ref["resolution"] = dict(resolution)
    return source_ref


def _source_unit_flat_slices(source_unit: Mapping[str, object]) -> list[dict[str, object]]:
    """Return unit paragraph slices with flat offsets matching source_text."""

    flat_slices: list[dict[str, object]] = []
    flat_cursor = 0
    for item in source_unit.get("paragraph_slices", []):
        if not isinstance(item, Mapping):
            continue
        text = str(item.get("text", "") or "")
        if flat_slices:
            flat_cursor += 2
        flat_start = flat_cursor
        flat_cursor += len(text)
        flat_slices.append(
            {
                **dict(item),
                "flat_start": flat_start,
                "flat_end": flat_cursor,
            }
        )
    return flat_slices


def _cursor_from_source_unit_flat_offset(
    source_unit: Mapping[str, object],
    flat_offset: int,
) -> SourceCursor:
    source_span = source_unit.get("source_span")
    span = source_span if isinstance(source_span, Mapping) else {}
    start = span.get("start_cursor")
    end = span.get("end_cursor")
    if not isinstance(start, Mapping):
        return {}
    chapter_id = _int(start.get("chapter_id") or (end.get("chapter_id") if isinstance(end, Mapping) else 0))
    chapter_ref = _clean_text(start.get("chapter_ref") or (end.get("chapter_ref") if isinstance(end, Mapping) else ""))
    for item in _source_unit_flat_slices(source_unit):
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
    if isinstance(end, Mapping):
        return dict(end)  # type: ignore[return-value]
    return dict(start)  # type: ignore[return-value]


def source_ref_from_unit(
    source_unit: Mapping[str, object] | None,
    *,
    quote: str = "",
    role: str = "support",
) -> SourceRef:
    """Resolve one unit-local quote into an inline paragraph-offset source ref."""

    if not isinstance(source_unit, Mapping):
        return source_ref_from_span({}, quote=quote, role=role, resolution={"status": "missing_source_unit"})
    source_span = source_unit.get("source_span")
    unit_span = dict(source_span) if isinstance(source_span, Mapping) else {}
    unit_text = str(source_unit.get("source_text", "") or "")
    clean_quote = str(quote or "").strip()
    if not clean_quote:
        return source_ref_from_span(
            unit_span,
            quote=unit_text,
            role=role,
            resolution={"status": "fallback_unit_span", "method": "missing_quote"},
        )

    def _ref_from_offsets(
        start_offset: int,
        end_offset: int,
        *,
        status: str,
        method: str,
        resolution_extra: Mapping[str, object] | None = None,
    ) -> SourceRef:
        quote_span = {
            "start_cursor": _cursor_from_source_unit_flat_offset(source_unit, start_offset),
            "end_cursor": _cursor_from_source_unit_flat_offset(source_unit, end_offset),
        }
        resolution: dict[str, object] = {"status": status, "method": method}
        if resolution_extra:
            resolution.update(dict(resolution_extra))
        return source_ref_from_span(quote_span, quote=clean_quote, role=role, resolution=resolution)

    matches = _find_all(unit_text, clean_quote)
    if matches:
        status = "matched" if len(matches) == 1 else "ambiguous_first_match"
        return _ref_from_offsets(
            matches[0],
            matches[0] + len(clean_quote),
            status=status,
            method="exact_text",
            resolution_extra={"match_count": len(matches)},
        )

    normalized_unit_text, normalized_unit_map = _normalized_text_with_map(unit_text)
    normalized_quote, normalized_quote_map = _normalized_text_with_map(clean_quote)
    normalized_matches = _find_all(normalized_unit_text, normalized_quote)
    if normalized_matches and normalized_quote_map:
        normalized_start = normalized_matches[0]
        normalized_end = normalized_start + len(normalized_quote) - 1
        start_offset = normalized_unit_map[normalized_start]
        end_offset = normalized_unit_map[normalized_end] + 1
        status = "matched" if len(normalized_matches) == 1 else "ambiguous_first_match"
        return _ref_from_offsets(
            start_offset,
            end_offset,
            status=status,
            method="normalized_exact_text",
            resolution_extra={"match_count": len(normalized_matches)},
        )

    fragments = _quote_fragments(clean_quote)
    if len(fragments) >= 2:
        fragment_matches: list[tuple[int, int, str]] = []
        search_start = 0
        for fragment in fragments:
            normalized_fragment, normalized_fragment_map = _normalized_text_with_map(fragment)
            if not (normalized_fragment and normalized_fragment_map):
                fragment_matches = []
                break
            fragment_match_indexes = _find_all(normalized_unit_text, normalized_fragment, start=search_start)
            if not fragment_match_indexes:
                fragment_matches = []
                break
            fragment_start = fragment_match_indexes[0]
            fragment_end = fragment_start + len(normalized_fragment) - 1
            fragment_matches.append((normalized_unit_map[fragment_start], normalized_unit_map[fragment_end] + 1, fragment))
            search_start = fragment_end + 1
        if len(fragment_matches) == len(fragments):
            return _ref_from_offsets(
                fragment_matches[0][0],
                fragment_matches[-1][1],
                status="ordered_fragment_match",
                method="ordered_fragment_text",
                resolution_extra={
                    "fragment_count": len(fragment_matches),
                    "matched_fragments": [item[2] for item in fragment_matches],
                },
            )

    return source_ref_from_span(
        unit_span,
        quote=clean_quote,
        role=role,
        resolution={"status": "fallback_unit_span", "method": "quote_not_found", "match_count": 0},
    )


def dedupe_source_refs(source_refs: object) -> list[SourceRef]:
    """Return order-preserving de-duplicated inline source refs."""

    if not isinstance(source_refs, list):
        return []
    deduped: list[SourceRef] = []
    seen: set[tuple[str, str, str]] = set()
    for item in source_refs:
        if not isinstance(item, Mapping):
            continue
        ref = source_ref_from_span(
            item.get("source_span") if isinstance(item.get("source_span"), Mapping) else {},
            quote=str(item.get("quote", "") or ""),
            role=str(item.get("role", "") or "support"),
            resolution=item.get("resolution") if isinstance(item.get("resolution"), Mapping) else None,
        )
        key = (_clean_text(ref.get("source_span_id")), _clean_text(ref.get("role")), _clean_text(ref.get("quote")))
        if not key[0] or key in seen:
            continue
        seen.add(key)
        deduped.append(ref)
    return deduped


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
