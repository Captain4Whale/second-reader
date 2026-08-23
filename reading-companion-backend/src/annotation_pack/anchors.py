"""Strict BookDocument-to-EPUB anchor resolution for Annotation Pack v0."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import re
from typing import Any, Protocol, cast

import regex

from src.annotation_pack.drafts import (
    AnnotationDraft,
    ResolvedAnchor,
    ResolvedAnnotationDraft,
    SourceCoordinate,
    SourceRange,
    ValidationFinding,
)
from src.annotation_pack.epub_resources import RESOURCE_TEXT_NORMALIZATION_VERSION
from src.annotation_pack.epub_source import EpubSourceError, normalize_epub_href
from src.annotation_pack.identity import (
    CHAPTER_FINGERPRINT_VERSION,
    PublicationIdentityResult,
)
from src.annotation_pack.ids import anchor_id


PARAGRAPH_COORDINATE_SYSTEM = "sr-book-document-paragraph-char-v1"
RESOURCE_TEXT_NORMALIZATION = RESOURCE_TEXT_NORMALIZATION_VERSION
OFFSET_UNIT = "unicode-code-point"
MAX_EXACT_CODE_POINTS = 1024
CONTEXT_CODE_POINTS = 64

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_CFI = re.compile(r"epubcfi\([^\r\n]+\)\Z")


@dataclass(frozen=True, slots=True)
class CfiRoundTrip:
    """One optional CFI proven to resolve to the requested resource slice."""

    value: str
    href: str
    resource_start: int
    resource_end: int


class CfiResolver(Protocol):
    """Protocol for an exact-source CFI implementation supplied by a caller."""

    def resolve(
        self,
        *,
        publication: PublicationIdentityResult,
        source_range: SourceRange,
        href: str,
        exact: str,
        resource_start: int,
        resource_end: int,
    ) -> CfiRoundTrip | None: ...


class AnchorResolutionError(ValueError):
    """Stable annotation-level failure with one sanitized finding."""

    def __init__(self, finding: ValidationFinding) -> None:
        super().__init__(finding.message)
        self.code = finding.code
        self.finding = finding


class AnchorBuilder:
    """Resolve neutral paragraph-char drafts against one verified publication."""

    def __init__(self, *, cfi_resolver: CfiResolver | None = None) -> None:
        self._cfi_resolver = cfi_resolver

    def resolve(
        self,
        *,
        draft: AnnotationDraft,
        publication: PublicationIdentityResult,
    ) -> ResolvedAnnotationDraft:
        """Return an exact href/quote/paragraph/chapter target or fail closed."""

        if not isinstance(draft, AnnotationDraft):
            raise TypeError("draft must be an AnnotationDraft")
        if not isinstance(publication, PublicationIdentityResult):
            raise TypeError("publication must be a PublicationIdentityResult")

        start, end = _validated_source_range(draft)
        chapter, chapter_order = _resolve_chapter(publication, start.chapter_id, draft)
        paragraphs, paragraph_positions = _resolve_paragraphs(chapter, draft)
        start_position = _require_paragraph_position(
            paragraph_positions,
            start.paragraph_index,
            draft,
        )
        end_position = _require_paragraph_position(
            paragraph_positions,
            end.paragraph_index,
            draft,
        )
        if start_position > end_position:
            _fail(draft, "malformed_source_span", "source range order is invalid")

        start_paragraph = paragraphs[start_position]
        end_paragraph = paragraphs[end_position]
        start_text = _paragraph_text(start_paragraph, draft)
        end_text = _paragraph_text(end_paragraph, draft)
        _validate_offset(start.char_offset, start_text, draft)
        _validate_offset(end.char_offset, end_text, draft)
        if start_position == end_position and start.char_offset >= end.char_offset:
            _fail(draft, "malformed_source_span", "source range must be non-empty")
        if not _is_grapheme_boundary(start_text, start.char_offset) or not (
            _is_grapheme_boundary(end_text, end.char_offset)
        ):
            _fail(
                draft,
                "grapheme_boundary_split",
                "source range splits an extended grapheme cluster",
            )

        covered = paragraphs[start_position : end_position + 1]
        readable = [paragraph for paragraph in covered if _is_readable(paragraph)]
        if not readable or readable[0] is not start_paragraph or readable[-1] is not end_paragraph:
            _fail(
                draft,
                "malformed_source_span",
                "source range endpoints must reference readable paragraphs",
            )
        href_participants = [
            paragraph
            for paragraph in covered
            if _paragraph_text(paragraph, draft)
        ]
        href = _single_canonical_href(href_participants, publication, draft)
        reconstructed = _reconstruct_quote(
            readable,
            start=start,
            end=end,
            draft=draft,
        )
        if not isinstance(draft.source_quote, str) or not draft.source_quote:
            _fail(draft, "unresolved_source_quote", "source quote is missing")
        if len(draft.source_quote) > MAX_EXACT_CODE_POINTS:
            _fail(
                draft,
                "source_quote_too_long",
                "source quote exceeds the v0 code-point limit",
            )
        if reconstructed != draft.source_quote:
            _fail(
                draft,
                "unresolved_source_quote",
                "source quote does not match the canonical BookDocument range",
            )

        resource_text, resource_start, resource_end = _resolve_resource_slice(
            publication=publication,
            draft=draft,
            chapter_id=start.chapter_id,
            href=href,
            covered=covered,
            readable=readable,
            start=start,
            end=end,
        )
        exact = draft.source_quote
        prefix = resource_text[max(0, resource_start - CONTEXT_CODE_POINTS) : resource_start]
        suffix = resource_text[
            resource_end : min(len(resource_text), resource_end + CONTEXT_CODE_POINTS)
        ]
        chapter_fingerprint = _chapter_fingerprint(
            publication,
            start.chapter_id,
            draft,
        )
        edition = _edition_id(publication, draft)
        resolved_anchor_id = anchor_id(
            edition,
            href,
            chapter_fingerprint,
            start_chapter_id=start.chapter_id,
            start_paragraph_index=start.paragraph_index,
            start_char_offset=start.char_offset,
            end_chapter_id=end.chapter_id,
            end_paragraph_index=end.paragraph_index,
            end_char_offset=end.char_offset,
            quote_sha256=hashlib.sha256(exact.encode("utf-8")).hexdigest(),
        )

        findings: list[ValidationFinding] = []
        if _occurrence_count(resource_text, exact) > 1:
            findings.append(
                _finding(
                    draft,
                    "quote_not_unique_in_resource",
                    "warning",
                    "source quote occurs more than once in the verified resource",
                    json_pointer="/target/selector/0/exact",
                )
            )
        if _has_duplicate_chapter_projection(
            publication,
            chapter_id=start.chapter_id,
            readable=readable,
        ):
            findings.append(
                _finding(
                    draft,
                    "duplicate_resource_chapter_projection",
                    "warning",
                    "verified resource blocks are projected into multiple chapters",
                    json_pointer="/target/sr:chapter",
                )
            )

        selectors: list[dict[str, object]] = [
            {
                "type": "TextQuoteSelector",
                "exact": exact,
                "prefix": prefix,
                "suffix": suffix,
                "sr:normalization": RESOURCE_TEXT_NORMALIZATION_VERSION,
            },
            {
                "type": "sr:ParagraphCharSelector",
                "sr:coordinateSystem": PARAGRAPH_COORDINATE_SYSTEM,
                "sr:offsetUnit": OFFSET_UNIT,
                "sr:start": _coordinate_wire(start),
                "sr:end": _coordinate_wire(end),
            },
        ]
        cfi_selector, cfi_finding = self._verified_cfi(
            draft=draft,
            publication=publication,
            href=href,
            exact=exact,
            resource_start=resource_start,
            resource_end=resource_end,
        )
        if cfi_selector is not None:
            selectors.append(cfi_selector)
        if cfi_finding is not None:
            findings.append(cfi_finding)

        chapter_context: dict[str, object] = {
            "type": "sr:ChapterContext",
            "sr:chapterId": start.chapter_id,
            "sr:order": chapter_order,
            "sr:fingerprint": {
                "type": "sr:Fingerprint",
                "sr:algorithm": "sha256",
                "sr:algorithmVersion": CHAPTER_FINGERPRINT_VERSION,
                "sr:value": chapter_fingerprint,
            },
        }
        chapter_title = chapter.get("title")
        if isinstance(chapter_title, str) and chapter_title:
            chapter_context["name"] = chapter_title
        target = {
            "type": "SpecificResource",
            "source": href,
            "selector": selectors,
            "sr:anchorId": resolved_anchor_id,
            "sr:chapter": chapter_context,
        }
        resolved_anchor = ResolvedAnchor(
            anchor_id=resolved_anchor_id,
            href=href,
            exact=exact,
            target=cast(Mapping[str, Any], _freeze_json(target)),
            findings=tuple(findings),
        )
        return ResolvedAnnotationDraft(
            kind=draft.kind,
            body_text=draft.body_text,
            created_at=draft.created_at,
            target=resolved_anchor,
            source_record_index=draft.source_record_index,
            source_record_digest=draft.source_record_digest,
        )

    def _verified_cfi(
        self,
        *,
        draft: AnnotationDraft,
        publication: PublicationIdentityResult,
        href: str,
        exact: str,
        resource_start: int,
        resource_end: int,
    ) -> tuple[dict[str, object] | None, ValidationFinding | None]:
        if self._cfi_resolver is None:
            return None, None
        try:
            resolved = self._cfi_resolver.resolve(
                publication=publication,
                source_range=draft.source_range,
                href=href,
                exact=exact,
                resource_start=resource_start,
                resource_end=resource_end,
            )
        except Exception:
            resolved = None
        if (
            not isinstance(resolved, CfiRoundTrip)
            or not isinstance(resolved.value, str)
            or len(resolved.value) > 2048
            or _CFI.fullmatch(resolved.value) is None
            or resolved.href != href
            or isinstance(resolved.resource_start, bool)
            or not isinstance(resolved.resource_start, int)
            or isinstance(resolved.resource_end, bool)
            or not isinstance(resolved.resource_end, int)
            or resolved.resource_start != resource_start
            or resolved.resource_end != resource_end
        ):
            return (
                None,
                _finding(
                    draft,
                    "cfi_unverified",
                    "warning",
                    "optional EPUB CFI did not pass exact quote round-trip verification",
                    json_pointer="/target/selector/2",
                ),
            )
        return (
            {
                "type": "sr:EpubCfiSelector",
                "value": resolved.value,
                "sr:verification": "quote-round-trip",
            },
            None,
        )


def _validated_source_range(
    draft: AnnotationDraft,
) -> tuple[SourceCoordinate, SourceCoordinate]:
    source_range = draft.source_range
    if not isinstance(source_range, SourceRange):
        _fail(draft, "malformed_source_span", "source range is malformed")
    start = source_range.start
    end = source_range.end
    if not isinstance(start, SourceCoordinate) or not isinstance(end, SourceCoordinate):
        _fail(draft, "malformed_source_span", "source coordinates are malformed")
    for coordinate in (start, end):
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (
                coordinate.chapter_id,
                coordinate.paragraph_index,
                coordinate.char_offset,
            )
        ):
            _fail(draft, "malformed_source_span", "source coordinates must be integers")
        if coordinate.paragraph_index < 1 or coordinate.char_offset < 0:
            _fail(draft, "malformed_source_span", "source coordinates are out of range")
    if start.chapter_id != end.chapter_id:
        _fail(draft, "malformed_source_span", "source range crosses chapters")
    return start, end


def _resolve_chapter(
    publication: PublicationIdentityResult,
    chapter_id: int,
    draft: AnnotationDraft,
) -> tuple[Mapping[str, object], int]:
    document = publication.rebuilt_book_document
    raw_chapters = document.get("chapters")
    if not isinstance(raw_chapters, Sequence) or isinstance(
        raw_chapters,
        (str, bytes, bytearray),
    ):
        _fail(draft, "malformed_source_span", "canonical chapter collection is invalid")
    found: tuple[Mapping[str, object], int] | None = None
    seen: set[int] = set()
    for order, chapter in enumerate(raw_chapters, start=1):
        if not isinstance(chapter, Mapping):
            _fail(draft, "malformed_source_span", "canonical chapter entry is invalid")
        candidate = chapter.get("id")
        if isinstance(candidate, bool) or not isinstance(candidate, int):
            _fail(draft, "malformed_source_span", "canonical chapter id is invalid")
        if candidate in seen:
            _fail(draft, "malformed_source_span", "canonical chapter ids are not unique")
        seen.add(candidate)
        if candidate == chapter_id:
            found = (chapter, order)
    if found is None:
        _fail(draft, "malformed_source_span", "source chapter does not exist")
    return found


def _resolve_paragraphs(
    chapter: Mapping[str, object],
    draft: AnnotationDraft,
) -> tuple[list[Mapping[str, object]], dict[int, int]]:
    raw_paragraphs = chapter.get("paragraphs")
    if not isinstance(raw_paragraphs, Sequence) or isinstance(
        raw_paragraphs,
        (str, bytes, bytearray),
    ):
        _fail(draft, "malformed_source_span", "canonical paragraph collection is invalid")
    paragraphs: list[Mapping[str, object]] = []
    positions: dict[int, int] = {}
    for position, paragraph in enumerate(raw_paragraphs):
        if not isinstance(paragraph, Mapping):
            _fail(draft, "malformed_source_span", "canonical paragraph entry is invalid")
        paragraph_index = paragraph.get("paragraph_index")
        if (
            isinstance(paragraph_index, bool)
            or not isinstance(paragraph_index, int)
            or paragraph_index < 1
        ):
            _fail(draft, "malformed_source_span", "canonical paragraph index is invalid")
        if paragraph_index in positions:
            _fail(draft, "malformed_source_span", "paragraph indexes are not unique")
        positions[paragraph_index] = position
        paragraphs.append(paragraph)
    return paragraphs, positions


def _require_paragraph_position(
    positions: Mapping[int, int],
    paragraph_index: int,
    draft: AnnotationDraft,
) -> int:
    position = positions.get(paragraph_index)
    if position is None:
        _fail(draft, "malformed_source_span", "source paragraph does not exist")
    return position


def _paragraph_text(
    paragraph: Mapping[str, object],
    draft: AnnotationDraft,
) -> str:
    value = paragraph.get("text")
    if not isinstance(value, str):
        _fail(draft, "malformed_source_span", "canonical paragraph text is invalid")
    return value


def _is_readable(paragraph: Mapping[str, object]) -> bool:
    text = paragraph.get("text")
    role = paragraph.get("text_role", "body")
    return isinstance(text, str) and bool(text) and role != "auxiliary"


def _validate_offset(offset: int, text: str, draft: AnnotationDraft) -> None:
    if offset > len(text):
        _fail(draft, "malformed_source_span", "source offset exceeds paragraph text")


def _is_grapheme_boundary(text: str, offset: int) -> bool:
    if offset in {0, len(text)}:
        return True
    return any(match.start() == offset for match in regex.finditer(r"\X", text))


def _single_canonical_href(
    paragraphs: Sequence[Mapping[str, object]],
    publication: PublicationIdentityResult,
    draft: AnnotationDraft,
) -> str:
    hrefs: set[str] = set()
    for paragraph in paragraphs:
        value = paragraph.get("href")
        if not isinstance(value, str) or not value:
            _fail(draft, "cross_resource_span", "source paragraph has no resource href")
        try:
            normalized = normalize_epub_href(value)
        except EpubSourceError:
            _fail(draft, "cross_resource_span", "source paragraph href is invalid")
        if normalized != value:
            _fail(draft, "cross_resource_span", "source paragraph href is not canonical")
        hrefs.add(normalized)
    if len(hrefs) != 1:
        _fail(draft, "cross_resource_span", "source range crosses EPUB resources")
    href = next(iter(hrefs))
    manifest = publication.epub_index.manifest
    if href not in manifest.manifest_hrefs or href not in manifest.text_resource_hrefs:
        _fail(
            draft,
            "target_href_not_in_manifest",
            "target href is not an eligible verified manifest resource",
        )
    return href


def _reconstruct_quote(
    paragraphs: Sequence[Mapping[str, object]],
    *,
    start: SourceCoordinate,
    end: SourceCoordinate,
    draft: AnnotationDraft,
) -> str:
    pieces: list[str] = []
    for paragraph in paragraphs:
        text = _paragraph_text(paragraph, draft)
        paragraph_index = cast(int, paragraph.get("paragraph_index"))
        start_char = start.char_offset if paragraph_index == start.paragraph_index else 0
        end_char = end.char_offset if paragraph_index == end.paragraph_index else len(text)
        piece = text[start_char:end_char]
        if piece:
            pieces.append(piece)
    return "\n\n".join(pieces)


def _resolve_resource_slice(
    *,
    publication: PublicationIdentityResult,
    draft: AnnotationDraft,
    chapter_id: int,
    href: str,
    covered: Sequence[Mapping[str, object]],
    readable: Sequence[Mapping[str, object]],
    start: SourceCoordinate,
    end: SourceCoordinate,
) -> tuple[str, int, int]:
    index = publication.epub_index
    if href in index.unverifiable_hrefs:
        _fail(
            draft,
            "resource_text_unverifiable",
            "target resource text could not be verified",
        )
    resource_text = index.resource_texts.get(href)
    if not isinstance(resource_text, str):
        _fail(
            draft,
            "resource_text_unverifiable",
            "target resource text is unavailable",
        )

    block_ranges: dict[int, tuple[str, int, int]] = {}
    for paragraph in readable:
        paragraph_index = cast(int, paragraph.get("paragraph_index"))
        mapping = index.paragraph_ranges.get((chapter_id, paragraph_index))
        if not _valid_resource_range(mapping, resource_text):
            _fail(
                draft,
                "resource_text_unverifiable",
                "source paragraph has no verified resource-text mapping",
            )
        mapped_href, block_start, block_end = mapping
        if mapped_href != href:
            _fail(
                draft,
                "resource_text_unverifiable",
                "source paragraph mapping addresses a different resource",
            )
        if resource_text[block_start:block_end] != _paragraph_text(paragraph, draft):
            _fail(
                draft,
                "resource_text_unverifiable",
                "source paragraph does not match verified resource text",
            )
        block_ranges[paragraph_index] = mapping

    start_mapping = block_ranges[start.paragraph_index]
    end_mapping = block_ranges[end.paragraph_index]
    resource_start = start_mapping[1] + start.char_offset
    resource_end = end_mapping[1] + end.char_offset
    if resource_start >= resource_end or resource_end > len(resource_text):
        _fail(
            draft,
            "resource_text_unverifiable",
            "source range has an invalid verified resource-text mapping",
        )
    if resource_text[resource_start:resource_end] != draft.source_quote:
        skipped_nonempty = any(
            not _is_readable(paragraph)
            and isinstance(paragraph.get("text"), str)
            and bool(paragraph.get("text"))
            for paragraph in covered
        )
        _fail(
            draft,
            (
                "non_contiguous_resource_quote"
                if skipped_nonempty
                else "resource_text_unverifiable"
            ),
            (
                "source range skips text present in the verified resource"
                if skipped_nonempty
                else "source quote is not a continuous verified resource slice"
            ),
        )
    return resource_text, resource_start, resource_end


def _valid_resource_range(
    value: object,
    resource_text: str,
) -> bool:
    return bool(
        isinstance(value, tuple)
        and len(value) == 3
        and isinstance(value[0], str)
        and isinstance(value[1], int)
        and not isinstance(value[1], bool)
        and isinstance(value[2], int)
        and not isinstance(value[2], bool)
        and 0 <= value[1] < value[2] <= len(resource_text)
    )


def _chapter_fingerprint(
    publication: PublicationIdentityResult,
    chapter_id: int,
    draft: AnnotationDraft,
) -> str:
    value = publication.chapter_fingerprints.get(chapter_id)
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail(
            draft,
            "resource_text_unverifiable",
            "chapter fingerprint is unavailable",
        )
    return value


def _edition_id(
    publication: PublicationIdentityResult,
    draft: AnnotationDraft,
) -> str:
    edition = publication.wire.get("sr:edition")
    if not isinstance(edition, Mapping) or not isinstance(edition.get("id"), str):
        _fail(draft, "resource_text_unverifiable", "edition identity is unavailable")
    return cast(str, edition["id"])


def _coordinate_wire(coordinate: SourceCoordinate) -> dict[str, int]:
    return {
        "sr:chapterId": coordinate.chapter_id,
        "sr:paragraphIndex": coordinate.paragraph_index,
        "sr:charOffset": coordinate.char_offset,
    }


def _occurrence_count(haystack: str, needle: str) -> int:
    """Return 0, 1, or 2 where 2 means two-or-more occurrences."""

    count = 0
    cursor = 0
    while needle and count < 2:
        index = haystack.find(needle, cursor)
        if index < 0:
            break
        count += 1
        cursor = index + 1
    return count


def _has_duplicate_chapter_projection(
    publication: PublicationIdentityResult,
    *,
    chapter_id: int,
    readable: Sequence[Mapping[str, object]],
) -> bool:
    ranges = publication.epub_index.paragraph_ranges
    current = {
        ranges.get((chapter_id, cast(int, paragraph.get("paragraph_index"))))
        for paragraph in readable
    }
    current.discard(None)
    return any(
        other_chapter != chapter_id and mapping in current
        for (other_chapter, _paragraph_index), mapping in ranges.items()
    )


def _finding(
    draft: AnnotationDraft,
    code: str,
    severity: str,
    message: str,
    *,
    json_pointer: str | None = None,
) -> ValidationFinding:
    source_index = (
        draft.source_record_index
        if isinstance(draft.source_record_index, int)
        and not isinstance(draft.source_record_index, bool)
        and draft.source_record_index >= 0
        else None
    )
    source_digest = (
        draft.source_record_digest
        if isinstance(draft.source_record_digest, str)
        and _SHA256.fullmatch(draft.source_record_digest)
        else None
    )
    return ValidationFinding(
        code=code,
        severity=cast(Any, severity),
        message=message,
        source_record_index=source_index,
        source_record_digest=source_digest,
        json_pointer=json_pointer,
    )


def _fail(
    draft: AnnotationDraft,
    code: str,
    message: str,
    *,
    json_pointer: str | None = None,
) -> Any:
    raise AnchorResolutionError(
        _finding(
            draft,
            code,
            "error",
            message,
            json_pointer=json_pointer,
        )
    )


def _immutable_collection(*_args: object, **_kwargs: object) -> Any:
    raise TypeError("canonical annotation target is immutable")


class _FrozenDict(dict[str, Any]):
    __setitem__ = _immutable_collection
    __delitem__ = _immutable_collection
    clear = _immutable_collection
    pop = _immutable_collection
    popitem = _immutable_collection
    setdefault = _immutable_collection
    update = _immutable_collection
    __ior__ = _immutable_collection


class _FrozenList(list[Any]):
    __setitem__ = _immutable_collection
    __delitem__ = _immutable_collection
    __iadd__ = _immutable_collection
    __imul__ = _immutable_collection
    append = _immutable_collection
    clear = _immutable_collection
    extend = _immutable_collection
    insert = _immutable_collection
    pop = _immutable_collection
    remove = _immutable_collection
    reverse = _immutable_collection
    sort = _immutable_collection


def _freeze_json(value: object) -> object:
    if isinstance(value, Mapping):
        return _FrozenDict(
            {str(key): _freeze_json(child) for key, child in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return _FrozenList(_freeze_json(child) for child in value)
    return value


__all__ = [
    "CONTEXT_CODE_POINTS",
    "MAX_EXACT_CODE_POINTS",
    "OFFSET_UNIT",
    "PARAGRAPH_COORDINATE_SYSTEM",
    "RESOURCE_TEXT_NORMALIZATION",
    "AnchorBuilder",
    "AnchorResolutionError",
    "CfiResolver",
    "CfiRoundTrip",
]
