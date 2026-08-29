"""Strict BookDocument paragraph/character source-range primitives.

Coordinates are Unicode-code-point offsets into canonical BookDocument
paragraph text.  Starts are inclusive, ends exclusive, and paragraph indexes
are one-based.  This module deliberately knows nothing about any reading
mechanism or downstream annotation format.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any, cast
from urllib.parse import urlsplit
import unicodedata

import regex


@dataclass(frozen=True, slots=True)
class SourceCoordinate:
    chapter_id: int
    paragraph_index: int
    char_offset: int


@dataclass(frozen=True, slots=True)
class SourceRange:
    start: SourceCoordinate
    end: SourceCoordinate


@dataclass(frozen=True, slots=True)
class ResolvedSourceRange:
    """A range verified against one canonical BookDocument snapshot."""

    source_range: SourceRange
    quote: str
    href: str
    chapter: Mapping[str, object]
    covered_paragraphs: tuple[Mapping[str, object], ...]
    readable_paragraphs: tuple[Mapping[str, object], ...]


class SourceRangeValidationError(ValueError):
    """Stable source validation failure safe to persist as a finding."""

    __slots__ = ("code",)

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def source_coordinate_to_wire(value: SourceCoordinate) -> dict[str, int]:
    _validate_coordinate_shape(value)
    return {
        "chapter_id": value.chapter_id,
        "paragraph_index": value.paragraph_index,
        "char_offset": value.char_offset,
    }


def source_range_to_wire(value: SourceRange) -> dict[str, object]:
    return {
        "start": source_coordinate_to_wire(value.start),
        "end": source_coordinate_to_wire(value.end),
    }


def source_coordinate_from_wire(value: object) -> SourceCoordinate:
    if not isinstance(value, Mapping) or set(value) != {
        "chapter_id",
        "paragraph_index",
        "char_offset",
    }:
        _fail("malformed_source_span", "source coordinate is malformed")
    coordinate = SourceCoordinate(
        chapter_id=cast(Any, value)["chapter_id"],
        paragraph_index=cast(Any, value)["paragraph_index"],
        char_offset=cast(Any, value)["char_offset"],
    )
    _validate_coordinate_shape(coordinate)
    return coordinate


def source_range_from_wire(value: object) -> SourceRange:
    if not isinstance(value, Mapping) or set(value) != {"start", "end"}:
        _fail("malformed_source_span", "source range is malformed")
    result = SourceRange(
        start=source_coordinate_from_wire(value["start"]),
        end=source_coordinate_from_wire(value["end"]),
    )
    _validate_range_shape(result)
    return result


def source_range_contains(outer: SourceRange, inner: SourceRange) -> bool:
    """Return whether ``inner`` is wholly contained by ``outer``."""

    _validate_range_shape(outer)
    _validate_range_shape(inner)
    if outer.start.chapter_id != inner.start.chapter_id:
        return False
    return _coordinate_order(outer.start) <= _coordinate_order(
        inner.start
    ) and _coordinate_order(inner.end) <= _coordinate_order(outer.end)


def validate_book_document_source_range(
    book_document: Mapping[str, object],
    source_range: SourceRange,
    *,
    expected_quote: str | None = None,
    within: SourceRange | None = None,
    require_single_resource: bool = True,
    normalize_href: Callable[[str], str] | None = None,
    maximum_quote_code_points: int | None = None,
) -> ResolvedSourceRange:
    """Resolve and validate a strict canonical BookDocument range.

    Non-empty readable endpoints, extended-grapheme boundaries, quote
    round-trip, optional containment, and single-resource coherence are checked.
    Auxiliary and empty paragraphs inside a span are omitted from the canonical
    quote; readable pieces are joined using the frozen ``"\n\n"`` separator.
    """

    if not isinstance(book_document, Mapping):
        _fail("malformed_book_document", "canonical BookDocument is malformed")
    _validate_range_shape(source_range)
    if within is not None and not source_range_contains(within, source_range):
        _fail("source_range_outside_unit", "source range is outside its Unit")

    chapter = _resolve_chapter(book_document, source_range.start.chapter_id)
    paragraphs, positions = _resolve_paragraphs(chapter)
    start_position = _require_position(positions, source_range.start.paragraph_index)
    end_position = _require_position(positions, source_range.end.paragraph_index)
    if start_position > end_position:
        _fail("malformed_source_span", "source range order is invalid")

    start_paragraph = paragraphs[start_position]
    end_paragraph = paragraphs[end_position]
    start_text = _paragraph_text(start_paragraph)
    end_text = _paragraph_text(end_paragraph)
    _validate_offset(source_range.start.char_offset, start_text)
    _validate_offset(source_range.end.char_offset, end_text)
    if (
        start_position == end_position
        and source_range.start.char_offset >= source_range.end.char_offset
    ):
        _fail("malformed_source_span", "source range must be non-empty")
    if not _is_grapheme_boundary(start_text, source_range.start.char_offset) or not (
        _is_grapheme_boundary(end_text, source_range.end.char_offset)
    ):
        _fail(
            "grapheme_boundary_split",
            "source range splits an extended grapheme cluster",
        )

    covered = paragraphs[start_position : end_position + 1]
    readable = [paragraph for paragraph in covered if _is_readable(paragraph)]
    if (
        not readable
        or readable[0] is not start_paragraph
        or readable[-1] is not end_paragraph
    ):
        _fail(
            "malformed_source_span",
            "source range endpoints must reference readable paragraphs",
        )

    href = ""
    if require_single_resource:
        href = _single_href(
            [paragraph for paragraph in covered if _paragraph_text(paragraph)],
            normalize_href=normalize_href or _normalize_relative_href,
        )
    quote = _reconstruct_quote(readable, source_range)
    if not quote:
        _fail("unresolved_source_quote", "source range resolves to an empty quote")
    if expected_quote is not None:
        if not isinstance(expected_quote, str) or not expected_quote:
            _fail("unresolved_source_quote", "source quote is missing")
        if (
            maximum_quote_code_points is not None
            and len(expected_quote) > maximum_quote_code_points
        ):
            _fail("source_quote_too_long", "source quote exceeds the code-point limit")
        if expected_quote != quote:
            _fail(
                "unresolved_source_quote",
                "source quote does not match the canonical BookDocument range",
            )
    elif maximum_quote_code_points is not None and len(quote) > maximum_quote_code_points:
        _fail("source_quote_too_long", "source quote exceeds the code-point limit")

    return ResolvedSourceRange(
        source_range=source_range,
        quote=quote,
        href=href,
        chapter=chapter,
        covered_paragraphs=tuple(covered),
        readable_paragraphs=tuple(readable),
    )


def _validate_range_shape(value: object) -> SourceRange:
    if not isinstance(value, SourceRange):
        _fail("malformed_source_span", "source range is malformed")
    _validate_coordinate_shape(value.start)
    _validate_coordinate_shape(value.end)
    if value.start.chapter_id != value.end.chapter_id:
        _fail("malformed_source_span", "source range crosses chapters")
    if _coordinate_order(value.start) > _coordinate_order(value.end):
        _fail("malformed_source_span", "source range order is invalid")
    return value


def _validate_coordinate_shape(value: object) -> SourceCoordinate:
    if not isinstance(value, SourceCoordinate):
        _fail("malformed_source_span", "source coordinate is malformed")
    if any(
        isinstance(field, bool) or not isinstance(field, int)
        for field in (value.chapter_id, value.paragraph_index, value.char_offset)
    ):
        _fail("malformed_source_span", "source coordinates must be integers")
    if value.chapter_id < 1 or value.paragraph_index < 1 or value.char_offset < 0:
        _fail("malformed_source_span", "source coordinates are out of range")
    return value


def _coordinate_order(value: SourceCoordinate) -> tuple[int, int]:
    return value.paragraph_index, value.char_offset


def _resolve_chapter(
    document: Mapping[str, object], chapter_id: int
) -> Mapping[str, object]:
    raw = document.get("chapters")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        _fail("malformed_book_document", "canonical chapter collection is invalid")
    found: Mapping[str, object] | None = None
    seen: set[int] = set()
    for chapter in raw:
        if not isinstance(chapter, Mapping):
            _fail("malformed_book_document", "canonical chapter entry is invalid")
        candidate = chapter.get("id")
        if isinstance(candidate, bool) or not isinstance(candidate, int):
            _fail("malformed_book_document", "canonical chapter id is invalid")
        if candidate in seen:
            _fail("malformed_book_document", "canonical chapter ids are not unique")
        seen.add(candidate)
        if candidate == chapter_id:
            found = chapter
    if found is None:
        _fail("malformed_source_span", "source chapter does not exist")
    return found


def _resolve_paragraphs(
    chapter: Mapping[str, object],
) -> tuple[list[Mapping[str, object]], dict[int, int]]:
    raw = chapter.get("paragraphs")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        _fail("malformed_book_document", "canonical paragraph collection is invalid")
    paragraphs: list[Mapping[str, object]] = []
    positions: dict[int, int] = {}
    for position, paragraph in enumerate(raw):
        if not isinstance(paragraph, Mapping):
            _fail("malformed_book_document", "canonical paragraph entry is invalid")
        index = paragraph.get("paragraph_index")
        if isinstance(index, bool) or not isinstance(index, int) or index < 1:
            _fail("malformed_book_document", "canonical paragraph index is invalid")
        if index in positions:
            _fail("malformed_book_document", "paragraph indexes are not unique")
        _paragraph_text(paragraph)
        positions[index] = position
        paragraphs.append(paragraph)
    return paragraphs, positions


def _require_position(positions: Mapping[int, int], paragraph_index: int) -> int:
    position = positions.get(paragraph_index)
    if position is None:
        _fail("malformed_source_span", "source paragraph does not exist")
    return position


def _paragraph_text(paragraph: Mapping[str, object]) -> str:
    value = paragraph.get("text")
    if not isinstance(value, str):
        _fail("malformed_book_document", "canonical paragraph text is invalid")
    return value


def _is_readable(paragraph: Mapping[str, object]) -> bool:
    text = paragraph.get("text")
    role = paragraph.get("text_role", "body")
    return isinstance(text, str) and bool(text) and role != "auxiliary"


def _validate_offset(offset: int, text: str) -> None:
    if offset > len(text):
        _fail("malformed_source_span", "source offset exceeds paragraph text")


def _is_grapheme_boundary(text: str, offset: int) -> bool:
    if offset in {0, len(text)}:
        return True
    return any(match.start() == offset for match in regex.finditer(r"\X", text))


def _single_href(
    paragraphs: Sequence[Mapping[str, object]],
    *,
    normalize_href: Callable[[str], str],
) -> str:
    hrefs: set[str] = set()
    for paragraph in paragraphs:
        value = paragraph.get("href")
        if not isinstance(value, str) or not value:
            _fail("cross_resource_span", "source paragraph has no resource href")
        try:
            normalized = normalize_href(value)
        except Exception:
            _fail("cross_resource_span", "source paragraph href is invalid")
        if normalized != value:
            _fail("cross_resource_span", "source paragraph href is not canonical")
        hrefs.add(normalized)
    if len(hrefs) != 1:
        _fail("cross_resource_span", "source range crosses EPUB resources")
    return next(iter(hrefs))


def _normalize_relative_href(value: str) -> str:
    if not value or value != value.strip() or "\\" in value or "\x00" in value:
        raise ValueError("unsafe href")
    parsed = urlsplit(value)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or value.startswith("/")
        or _WINDOWS_DRIVE.match(value)
        or "//" in value
        or any(unicodedata.category(character) == "Cc" for character in value)
    ):
        raise ValueError("unsafe href")
    parts = value.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("unsafe href")
    return value


def _reconstruct_quote(
    paragraphs: Sequence[Mapping[str, object]], source_range: SourceRange
) -> str:
    pieces: list[str] = []
    for paragraph in paragraphs:
        text = _paragraph_text(paragraph)
        index = cast(int, paragraph.get("paragraph_index"))
        start = (
            source_range.start.char_offset
            if index == source_range.start.paragraph_index
            else 0
        )
        end = (
            source_range.end.char_offset
            if index == source_range.end.paragraph_index
            else len(text)
        )
        piece = text[start:end]
        if piece:
            pieces.append(piece)
    return "\n\n".join(pieces)


def _fail(code: str, message: str) -> Any:
    raise SourceRangeValidationError(code, message)


__all__ = [
    "ResolvedSourceRange",
    "SourceCoordinate",
    "SourceRange",
    "SourceRangeValidationError",
    "source_coordinate_from_wire",
    "source_coordinate_to_wire",
    "source_range_contains",
    "source_range_from_wire",
    "source_range_to_wire",
    "validate_book_document_source_range",
]
