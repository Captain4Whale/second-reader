"""Producer-neutral publication fingerprints and substrate coherence checks."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from types import MappingProxyType
from typing import Any, BinaryIO, Literal, cast
import unicodedata

from src.annotation_pack.epub_source import (
    DEFAULT_SOURCE_ASSET,
    EPUB_MEDIA_TYPE,
    EpubSourceError,
    EpubSourceWarning,
    VerifiedEpubSource,
    is_public_display_metadata,
    normalize_epub_href,
    verify_epub_source,
)
from src.annotation_pack.epub_resources import (
    EpubManifestIndex,
    EpubResourceIndex,
    EpubResourceIndexError,
    build_epub_manifest_index,
    build_epub_resource_index,
)
from src.parsers import parse_epub_stream
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_runtime.source_normalization import normalize_book_document_source


CONTENT_FINGERPRINT_VERSION = "sr-book-document-text-v1"
CHAPTER_FINGERPRINT_VERSION = "sr-book-document-chapter-v1"
SUBSTRATE_FINGERPRINT_VERSION = "sr-book-document-substrate-v1"

__all__ = [
    "CHAPTER_FINGERPRINT_VERSION",
    "CONTENT_FINGERPRINT_VERSION",
    "SUBSTRATE_FINGERPRINT_VERSION",
    "ChapterFingerprint",
    "EpubManifestIndex",
    "EpubResourceIndex",
    "Fingerprint",
    "IdentityFinding",
    "PublicationIdentityBuilder",
    "PublicationIdentityError",
    "PublicationIdentityResult",
    "SubstrateComparison",
    "book_content_fingerprint",
    "book_content_fingerprint_stream",
    "book_document_substrate_stream",
    "chapter_fingerprint_stream",
    "chapter_fingerprints",
    "compare_book_document_substrates",
    "fingerprint_frame",
    "normalize_fingerprint_text",
    "project_book_document_substrate",
]

_CONTENT_HEADER = b"SECOND-READER-BOOK-DOCUMENT-TEXT-V1\n"
_CHAPTER_HEADER = b"SECOND-READER-BOOK-DOCUMENT-CHAPTER-V1\n"
_SUBSTRATE_HEADER = b"SECOND-READER-BOOK-DOCUMENT-SUBSTRATE-V1\n"
_TEXT_ROLES = {"chapter_heading", "section_heading", "body", "auxiliary"}
_LANGUAGE_TAG = re.compile(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*\Z")
_UNICODE_WHITE_SPACE = frozenset(
    {
        *range(0x0009, 0x000E),
        0x0020,
        0x0085,
        0x00A0,
        0x1680,
        *range(0x2000, 0x200B),
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }
)
_MISSING = object()
_UNSAFE_OPF_DISPLAY_METADATA_POINTERS = {
    "An OPF title value was excluded because it is not safe for public metadata.": (
        "/about/dc:title"
    ),
    "An OPF creator value was excluded because it is not safe for public metadata.": (
        "/about/dc:creator"
    ),
    "An OPF language value was excluded because it is not safe for public metadata.": (
        "/about/dc:language"
    ),
}


def _immutable_collection(*_args: object, **_kwargs: object) -> None:
    raise TypeError("publication identity result is immutable")


class _FrozenDict(dict[str, Any]):
    """A JSON-compatible dict whose normal mutation surface is disabled."""

    __setitem__ = _immutable_collection
    __delitem__ = _immutable_collection
    clear = _immutable_collection
    pop = _immutable_collection
    popitem = _immutable_collection
    setdefault = _immutable_collection
    update = _immutable_collection
    __ior__ = _immutable_collection

    def __deepcopy__(self, _memo: dict[int, object]) -> _FrozenDict:
        return self


class _FrozenList(list[Any]):
    """A JSON-compatible list whose normal mutation surface is disabled."""

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

    def __deepcopy__(self, _memo: dict[int, object]) -> _FrozenList:
        return self


class PublicationIdentityError(ValueError):
    """Stable, sanitized publication-identity failure."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        json_pointer: str | None = None,
        rebuilt_field_sha256: str | None = None,
        persisted_field_sha256: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.json_pointer = json_pointer
        self.rebuilt_field_sha256 = rebuilt_field_sha256
        self.persisted_field_sha256 = persisted_field_sha256


@dataclass(frozen=True, slots=True)
class Fingerprint:
    algorithm_version: str
    value: str
    algorithm: str = "sha256"


@dataclass(frozen=True, slots=True)
class ChapterFingerprint:
    chapter_id: int
    order: int
    title: str
    resource_hrefs: tuple[str, ...]
    fingerprint: Fingerprint


@dataclass(frozen=True, slots=True)
class SubstrateComparison:
    digest: str
    projection: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class IdentityFinding:
    """One sanitized, deterministic publication-identity warning."""

    code: str
    message: str
    json_pointer: str | None = None
    severity: Literal["warning"] = "warning"


@dataclass(frozen=True, slots=True)
class PublicationIdentityResult:
    """Publication identity plus safe in-memory inputs for later slices."""

    wire: Mapping[str, object]
    rebuilt_book_document: Mapping[str, Any] = field(repr=False)
    epub_index: EpubResourceIndex
    file_sha256: str
    content_sha256: str
    substrate_sha256: str
    chapter_fingerprints: Mapping[int, str]
    findings: tuple[IdentityFinding, ...]


class PublicationIdentityBuilder:
    """Build minimal exact-file identity from one strictly verified EPUB."""

    def build(
        self,
        *,
        output_dir: Path,
        persisted_book_document: Mapping[str, Any],
        manifest: Mapping[str, Any] | None = None,
        source_asset_file: str | None = None,
    ) -> PublicationIdentityResult:
        """Verify a book output's source asset and build its public identity."""

        verified = verify_epub_source(
            output_dir,
            manifest,
            source_asset_file=source_asset_file,
        )
        return self.build_verified(
            verified_source=verified,
            persisted_book_document=persisted_book_document,
        )

    def build_verified(
        self,
        *,
        verified_source: VerifiedEpubSource,
        persisted_book_document: Mapping[str, Any],
    ) -> PublicationIdentityResult:
        """Build identity from an already verified, builder-private source handle."""
        persisted_metadata = _book_metadata(persisted_book_document)
        title, creators, language, findings = _publication_metadata(
            verified_source,
            persisted_metadata,
        )
        manifest_index = build_epub_manifest_index(verified_source)
        try:
            with verified_source.open_verified() as source_handle:
                rebuilt = _rebuild_book_document(
                    verified_source,
                    source_handle=source_handle,
                    title=title,
                    creators=creators,
                    language=language,
                    persisted_metadata=persisted_metadata,
                )
                href_resolver = _manifest_href_resolver(verified_source)
                rebuilt = _canonicalize_book_document_hrefs(rebuilt, href_resolver)
                persisted_for_comparison = _canonicalize_book_document_hrefs(
                    persisted_book_document,
                    href_resolver,
                )
                substrate = compare_book_document_substrates(
                    rebuilt,
                    persisted_for_comparison,
                )
                content = book_content_fingerprint(rebuilt)
                chapters = chapter_fingerprints(rebuilt)
                for chapter in chapters:
                    if chapter.title and not is_public_display_metadata(chapter.title):
                        raise PublicationIdentityError(
                            "invalid_publication_metadata",
                            "canonical chapter title is not eligible for publication identity",
                            json_pointer=f"/chapters/{chapter.order - 1}/title",
                        )
                _require_chapter_resources_in_manifest(chapters, manifest_index)
                epub_index = build_epub_resource_index(
                    source=verified_source,
                    source_handle=source_handle,
                    rebuilt_book_document=rebuilt,
                    manifest=manifest_index,
                )
        except EpubResourceIndexError as exc:
            raise PublicationIdentityError(
                "source_asset_missing_or_not_epub",
                "verified source EPUB could not be indexed for exact resource text",
            ) from exc

        wire: dict[str, object] = {
            "dc:format": EPUB_MEDIA_TYPE,
            "dc:title": title,
            "dc:identifier": [f"nih:sha-256;{verified_source.sha256}"],
        }
        if creators:
            wire["dc:creator"] = list(creators)

        verified_source.assert_unchanged()
        return PublicationIdentityResult(
            wire=cast(Mapping[str, object], _freeze_json(wire)),
            rebuilt_book_document=cast(Mapping[str, Any], _freeze_json(rebuilt)),
            epub_index=epub_index,
            file_sha256=verified_source.sha256,
            content_sha256=content.value,
            substrate_sha256=substrate.digest,
            chapter_fingerprints=MappingProxyType(
                {chapter.chapter_id: chapter.fingerprint.value for chapter in chapters}
            ),
            findings=findings,
        )


def normalize_fingerprint_text(value: object) -> str:
    """Apply the frozen Unicode normalization used by v0 text fingerprints."""

    text = unicodedata.normalize("NFC", str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized: list[str] = []
    in_white_space = False
    for character in text:
        if ord(character) in _UNICODE_WHITE_SPACE:
            if not in_white_space:
                normalized.append(" ")
            in_white_space = True
        else:
            normalized.append(character)
            in_white_space = False
    return "".join(normalized).strip(" ")


def fingerprint_frame(tag: str, value: object) -> bytes:
    """Encode one normalized length-prefixed text fingerprint field."""

    if not tag or not tag.isascii() or any(character in tag for character in ":\r\n"):
        raise ValueError("fingerprint frame tag must be non-empty safe ASCII")
    payload = normalize_fingerprint_text(value).encode("utf-8")
    return (
        tag.encode("ascii")
        + b":"
        + str(len(payload)).encode("ascii")
        + b":"
        + payload
        + b"\n"
    )


def book_content_fingerprint_stream(document: Mapping[str, object]) -> bytes:
    """Return the exact `sr-book-document-text-v1` byte stream."""

    stream = bytearray(_CONTENT_HEADER)
    for chapter in _mapping_sequence(document.get("chapters"), pointer="/chapters"):
        stream.extend(fingerprint_frame("C", _optional_text(chapter, "title")))
        for paragraph in _mapping_sequence(
            chapter.get("paragraphs"),
            pointer="/chapters/*/paragraphs",
        ):
            stream.extend(fingerprint_frame("P", _required_text(paragraph, "text")))
        stream.extend(b"E\n")
    return bytes(stream)


def book_content_fingerprint(document: Mapping[str, object]) -> Fingerprint:
    stream = book_content_fingerprint_stream(document)
    return Fingerprint(
        algorithm_version=CONTENT_FINGERPRINT_VERSION,
        value=hashlib.sha256(stream).hexdigest(),
    )


def chapter_fingerprint_stream(chapter: Mapping[str, object]) -> bytes:
    """Return the exact `sr-book-document-chapter-v1` byte stream."""

    stream = bytearray(_CHAPTER_HEADER)
    stream.extend(fingerprint_frame("C", _optional_text(chapter, "title")))
    for paragraph in _mapping_sequence(
        chapter.get("paragraphs"),
        pointer="/chapter/paragraphs",
    ):
        stream.extend(fingerprint_frame("P", _required_text(paragraph, "text")))
    stream.extend(b"E\n")
    return bytes(stream)


def chapter_fingerprints(
    document: Mapping[str, object],
) -> tuple[ChapterFingerprint, ...]:
    """Fingerprint every chapter and retain first-seen manifest-relative hrefs."""

    chapters = _mapping_sequence(document.get("chapters"), pointer="/chapters")
    if not chapters:
        raise PublicationIdentityError(
            "publication_has_no_chapters",
            "verified publication must contain at least one canonical chapter",
        )
    result: list[ChapterFingerprint] = []
    chapter_ids: set[int] = set()
    for order, chapter in enumerate(chapters, start=1):
        chapter_id = _required_int(chapter, "id")
        if chapter_id in chapter_ids:
            raise PublicationIdentityError(
                "duplicate_chapter_id",
                "canonical chapter ids must be unique",
                json_pointer=f"/chapters/{order - 1}/id",
            )
        chapter_ids.add(chapter_id)
        stream = chapter_fingerprint_stream(chapter)
        title = _optional_text(chapter, "title")
        if len(title) > 512:
            raise PublicationIdentityError(
                "invalid_publication_metadata",
                "canonical chapter title exceeds the v0 limit",
                json_pointer=f"/chapters/{order - 1}/title",
            )
        result.append(
            ChapterFingerprint(
                chapter_id=chapter_id,
                order=order,
                title=title,
                resource_hrefs=_chapter_resource_hrefs(chapter),
                fingerprint=Fingerprint(
                    algorithm_version=CHAPTER_FINGERPRINT_VERSION,
                    value=hashlib.sha256(stream).hexdigest(),
                ),
            )
        )
    return tuple(result)


def project_book_document_substrate(
    document: Mapping[str, object],
) -> dict[str, object]:
    """Build the exact field-level `sr-book-document-substrate-v1` projection."""

    chapters = _mapping_sequence(document.get("chapters"), pointer="/chapters")
    projected_chapters: list[dict[str, object]] = []
    for chapter_order, chapter in enumerate(chapters, start=1):
        paragraphs = _mapping_sequence(
            chapter.get("paragraphs"),
            pointer=f"/chapters/{chapter_order - 1}/paragraphs",
        )
        projected_paragraphs: list[dict[str, object]] = []
        for paragraph_order, paragraph in enumerate(paragraphs, start=1):
            text = _required_text(paragraph, "text")
            text_role = paragraph.get("text_role")
            if text_role is None:
                text_role = "body"
            if not isinstance(text_role, str) or text_role not in _TEXT_ROLES:
                raise PublicationIdentityError(
                    "invalid_book_document_text_role",
                    "canonical paragraph text_role is invalid",
                    json_pointer=(
                        f"/chapters/{chapter_order - 1}/paragraphs/"
                        f"{paragraph_order - 1}/text_role"
                    ),
                )
            projected_paragraphs.append(
                {
                    "list_order": paragraph_order,
                    "paragraph_index": _required_int(paragraph, "paragraph_index"),
                    "text": text,
                    "href": _optional_normalized_href(paragraph, "href"),
                    "text_role": text_role,
                    "readable": bool(text) and text_role != "auxiliary",
                }
            )
        projected_chapters.append(
            {
                "list_order": chapter_order,
                "id": _required_int(chapter, "id"),
                "chapter_number": _optional_int(chapter, "chapter_number"),
                "title": _required_text(chapter, "title"),
                "href": _optional_normalized_href(chapter, "href"),
                "item_id": _optional_exact_text(chapter, "item_id"),
                "spine_index": _optional_int(chapter, "spine_index"),
                "paragraphs": projected_paragraphs,
            }
        )
    return {"chapters": projected_chapters}


def book_document_substrate_stream(projection: Mapping[str, object]) -> bytes:
    """Encode a substrate projection with frozen typed length frames."""

    chapters = _mapping_sequence(projection.get("chapters"), pointer="/chapters")
    stream = bytearray(_SUBSTRATE_HEADER)
    stream.extend(_typed_frame("chapterCount", len(chapters)))
    for chapter in chapters:
        stream.extend(_typed_frame("chapter.listOrder", chapter["list_order"]))
        stream.extend(_typed_frame("chapter.id", chapter["id"]))
        stream.extend(_typed_frame("chapter.chapterNumber", chapter["chapter_number"]))
        stream.extend(_typed_frame("chapter.title", chapter["title"]))
        stream.extend(_typed_frame("chapter.href", chapter["href"]))
        stream.extend(_typed_frame("chapter.itemId", chapter["item_id"]))
        stream.extend(_typed_frame("chapter.spineIndex", chapter["spine_index"]))
        paragraphs = _mapping_sequence(
            chapter.get("paragraphs"),
            pointer="/chapters/*/paragraphs",
        )
        stream.extend(_typed_frame("chapter.paragraphCount", len(paragraphs)))
        for paragraph in paragraphs:
            stream.extend(_typed_frame("paragraph.listOrder", paragraph["list_order"]))
            stream.extend(
                _typed_frame("paragraph.paragraphIndex", paragraph["paragraph_index"])
            )
            stream.extend(_typed_frame("paragraph.text", paragraph["text"]))
            stream.extend(_typed_frame("paragraph.href", paragraph["href"]))
            stream.extend(_typed_frame("paragraph.textRole", paragraph["text_role"]))
            stream.extend(_typed_frame("paragraph.readable", paragraph["readable"]))
    return bytes(stream)


def compare_book_document_substrates(
    rebuilt: Mapping[str, object],
    persisted: Mapping[str, object],
) -> SubstrateComparison:
    """Fail closed on the first field mismatch without exposing field values."""

    rebuilt_projection = project_book_document_substrate(rebuilt)
    persisted_projection = project_book_document_substrate(persisted)
    difference = _first_difference(rebuilt_projection, persisted_projection)
    if difference is not None:
        pointer, rebuilt_value, persisted_value = difference
        raise PublicationIdentityError(
            "publication_substrate_mismatch",
            "persisted BookDocument does not match the verified source EPUB",
            json_pointer=pointer,
            rebuilt_field_sha256=_field_digest(rebuilt_value),
            persisted_field_sha256=_field_digest(persisted_value),
        )
    stream = book_document_substrate_stream(rebuilt_projection)
    return SubstrateComparison(
        digest=hashlib.sha256(stream).hexdigest(),
        projection=rebuilt_projection,
    )


def _book_metadata(document: Mapping[str, Any]) -> Mapping[str, object]:
    metadata = document.get("metadata")
    if not isinstance(metadata, Mapping):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            "canonical BookDocument metadata must be an object",
            json_pointer="/metadata",
        )
    return metadata


def _publication_metadata(
    source: VerifiedEpubSource,
    persisted_metadata: Mapping[str, object],
) -> tuple[str, tuple[str, ...], str | None, tuple[IdentityFinding, ...]]:
    findings = [
        _identity_finding_from_source_warning(warning)
        for warning in source.metadata.warnings
    ]
    persisted_title = _normalized_metadata_value(persisted_metadata.get("book"))
    if persisted_title and not _is_public_display_metadata(persisted_title):
        persisted_title = ""
        findings.append(
            IdentityFinding(
                code="invalid_persisted_metadata_fallback",
                message=(
                    "Persisted BookDocument title was not eligible for public "
                    "metadata fallback."
                ),
                json_pointer="/metadata/book",
            )
        )
    source_title = _normalized_metadata_value(source.metadata.title)
    if source_title and not _is_public_display_metadata(source_title):
        source_title = ""
        findings.append(
            IdentityFinding(
                code="invalid_publication_metadata",
                message=(
                    "Verified OPF title was not eligible for public publication "
                    "metadata."
                ),
                json_pointer="/about/dc:title",
            )
        )
    title = source_title or persisted_title
    if not title:
        raise PublicationIdentityError(
            "publication_identity_missing",
            "verified publication has no usable title",
            json_pointer="/about/dc:title",
        )
    if len(title) > 1024:
        raise PublicationIdentityError(
            "invalid_publication_metadata",
            "verified publication title exceeds the v0 limit",
            json_pointer="/about/dc:title",
        )
    if persisted_title and persisted_title != title:
        findings.append(
            IdentityFinding(
                code="publication_metadata_mismatch",
                message=(
                    "Verified OPF title differs from persisted BookDocument metadata; "
                    "the verified OPF value was used."
                ),
                json_pointer="/about/dc:title",
            )
        )

    normalized_source_creators = tuple(
        normalized
        for creator in source.metadata.creators
        if (normalized := _normalized_metadata_value(creator))
    )
    unsafe_source_creator = any(
        not _is_public_display_metadata(creator)
        for creator in normalized_source_creators
    )
    creators = tuple(
        dict.fromkeys(
            creator
            for creator in normalized_source_creators
            if _is_public_display_metadata(creator)
        )
    )
    if unsafe_source_creator:
        findings.append(
            IdentityFinding(
                code="invalid_publication_metadata",
                message=(
                    "One or more verified OPF creators were omitted because they "
                    "were not eligible for public publication metadata."
                ),
                json_pointer="/about/dc:creator",
            )
        )
    persisted_creator = _normalized_metadata_value(persisted_metadata.get("author"))
    if persisted_creator and not _is_public_display_metadata(persisted_creator):
        persisted_creator = ""
        findings.append(
            IdentityFinding(
                code="invalid_persisted_metadata_fallback",
                message=(
                    "Persisted BookDocument author was not eligible for public "
                    "metadata fallback."
                ),
                json_pointer="/metadata/author",
            )
        )
    if not creators and persisted_creator:
        creators = (persisted_creator,)
    if any(len(creator) > 512 for creator in creators):
        raise PublicationIdentityError(
            "invalid_publication_metadata",
            "verified publication creator exceeds the v0 limit",
            json_pointer="/about/dc:creator",
        )
    if (
        persisted_creator
        and creators
        and persisted_creator not in creators
        and persisted_creator != ", ".join(creators)
    ):
        findings.append(
            IdentityFinding(
                code="publication_metadata_mismatch",
                message=(
                    "Verified OPF creators differ from persisted BookDocument metadata; "
                    "the verified OPF values were used."
                ),
                json_pointer="/about/dc:creator",
            )
        )

    raw_language = _normalized_metadata_value(source.metadata.language)
    persisted_language = _safe_language_value(persisted_metadata.get("book_language"))
    language: str | None
    if raw_language and _LANGUAGE_TAG.fullmatch(raw_language):
        language = raw_language
        if persisted_language and persisted_language != raw_language:
            findings.append(
                IdentityFinding(
                    code="publication_metadata_mismatch",
                    message=(
                        "Verified OPF language differs from persisted BookDocument "
                        "metadata; the verified OPF value was used."
                    ),
                    json_pointer="/about/dc:language",
                )
            )
    else:
        language = persisted_language or None
        if raw_language:
            findings.append(
                IdentityFinding(
                    code="invalid_publication_language",
                    message=(
                        "Verified OPF language was omitted because it is not a v0 "
                        "language tag."
                    ),
                    json_pointer="/about/dc:language",
                )
            )
    return title, creators, language, tuple(findings)


def _identity_finding_from_source_warning(
    warning: EpubSourceWarning,
) -> IdentityFinding:
    """Translate verifier warnings into the identity layer's public vocabulary."""

    if warning.code == "unsafe_opf_display_metadata":
        return IdentityFinding(
            code="invalid_publication_metadata",
            message=warning.message,
            json_pointer=_UNSAFE_OPF_DISPLAY_METADATA_POINTERS.get(warning.message),
        )
    return IdentityFinding(code=warning.code, message=warning.message)


def _rebuild_book_document(
    source: VerifiedEpubSource,
    *,
    source_handle: BinaryIO,
    title: str,
    creators: tuple[str, ...],
    language: str | None,
    persisted_metadata: Mapping[str, object],
) -> Mapping[str, Any]:
    try:
        raw_chapters = parse_epub_stream(source_handle)
        book_language = language or _safe_language_value(
            persisted_metadata.get("book_language")
        )
        output_language = _safe_language_value(
            persisted_metadata.get("output_language")
        )
        canonical = build_book_document_from_chapters(
            list(raw_chapters),
            title=title,
            author=", ".join(creators),
            book_language=book_language or "und",
            output_language=output_language or book_language or "und",
            source_file=source.relative_path or DEFAULT_SOURCE_ASSET,
        )
        normalized, _diagnostics = normalize_book_document_source(
            canonical,
            output_dir=None,
            diagnostics_path=None,
            mechanism_key="annotation_pack_identity",
            classifier=None,
        )
    except (EpubSourceError, PublicationIdentityError):
        raise
    except Exception as exc:
        raise PublicationIdentityError(
            "source_asset_missing_or_not_epub",
            "verified source EPUB could not be parsed into a canonical BookDocument",
        ) from exc
    return normalized


def _manifest_href_resolver(
    source: VerifiedEpubSource,
) -> Callable[[str], str]:
    """Map parser-decoded ZIP member names back to canonical OPF hrefs."""

    primary_aliases: dict[str, str] = {}
    archive_fallbacks: dict[str, str | None] = {}
    opf_parent = PurePosixPath(source.opf_path).parent
    for item in source.manifest_items:
        try:
            relative_archive_path = (
                PurePosixPath(item.archive_path).relative_to(opf_parent).as_posix()
            )
        except ValueError as exc:  # pragma: no cover - verifier invariant
            raise PublicationIdentityError(
                "invalid_epub_manifest_index",
                "verified OPF manifest resource is outside the package directory",
            ) from exc
        # ebooklib reports OPF-relative names.  It may decode percent-escaped
        # reserved filename characters, so both the canonical href and the
        # decoded OPF-relative archive name are authoritative aliases.
        for alias in {item.href, relative_archive_path}:
            existing = primary_aliases.get(alias)
            if existing is not None and existing != item.href:
                raise PublicationIdentityError(
                    "ambiguous_epub_manifest_alias",
                    "verified OPF manifest contains ambiguous resource aliases",
                )
            primary_aliases[alias] = item.href

        # Some parser versions may expose the full archive member.  Keep that
        # spelling as a lower-priority fallback: in a nested package it can be
        # identical to another item's legitimate OPF-relative href.
        fallback = archive_fallbacks.get(item.archive_path, _MISSING)
        if fallback is _MISSING:
            archive_fallbacks[item.archive_path] = item.href
        elif fallback != item.href:
            archive_fallbacks[item.archive_path] = None

    def resolve(value: str) -> str:
        direct = primary_aliases.get(value)
        if direct is not None:
            return direct
        fallback = archive_fallbacks.get(value)
        if fallback is not None:
            return fallback
        normalized = _normalize_book_href(value)
        direct = primary_aliases.get(normalized)
        if direct is not None:
            return direct
        fallback = archive_fallbacks.get(normalized)
        return fallback if fallback is not None else normalized

    return resolve


def _canonicalize_book_document_hrefs(
    document: Mapping[str, Any],
    resolver: Callable[[str], str],
) -> Mapping[str, Any]:
    """Return a detached BookDocument copy with canonical manifest href aliases."""

    cloned = _clone_json(document)
    if not isinstance(cloned, dict):  # pragma: no cover - Mapping always clones to dict
        raise TypeError("BookDocument clone must be an object")
    chapters = cloned.get("chapters")
    if not isinstance(chapters, list):
        return cloned
    for chapter in chapters:
        if not isinstance(chapter, dict):
            continue
        _canonicalize_href_field(chapter, resolver)
        paragraphs = chapter.get("paragraphs")
        if isinstance(paragraphs, list):
            for paragraph in paragraphs:
                if isinstance(paragraph, dict):
                    _canonicalize_href_field(paragraph, resolver)
        chapter_heading = chapter.get("chapter_heading")
        if isinstance(chapter_heading, dict):
            locator = chapter_heading.get("locator")
            if isinstance(locator, dict):
                _canonicalize_href_field(locator, resolver)
    return cloned


def _canonicalize_href_field(
    document: dict[str, Any],
    resolver: Callable[[str], str],
) -> None:
    value = document.get("href")
    if isinstance(value, str) and value:
        document["href"] = resolver(value)


def _clone_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _clone_json(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clone_json(child) for child in value]
    return value


def _require_chapter_resources_in_manifest(
    chapters: Sequence[ChapterFingerprint],
    manifest: EpubManifestIndex,
) -> None:
    for chapter in chapters:
        if not chapter.resource_hrefs:
            raise PublicationIdentityError(
                "book_document_resource_missing",
                "canonical chapter does not reference a verified OPF manifest resource",
                json_pointer=f"/chapters/{chapter.order - 1}/href",
            )
        for href in chapter.resource_hrefs:
            if href not in manifest.manifest_hrefs:
                raise PublicationIdentityError(
                    "book_document_resource_not_in_manifest",
                    "canonical BookDocument references a resource outside the verified OPF manifest",
                    json_pointer=f"/chapters/{chapter.order - 1}/href",
                )
            if href not in manifest.text_resource_hrefs:
                raise PublicationIdentityError(
                    "book_document_resource_not_xhtml",
                    "canonical chapter references a non-text OPF manifest resource",
                    json_pointer=f"/chapters/{chapter.order - 1}/href",
                )


def _normalized_metadata_value(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return normalize_fingerprint_text(value)


def _safe_language_value(value: object) -> str:
    normalized = _normalized_metadata_value(value)
    if normalized and _LANGUAGE_TAG.fullmatch(normalized):
        return normalized
    return ""


def _is_public_display_metadata(value: str) -> bool:
    return is_public_display_metadata(value)


def _freeze_json(value: object) -> object:
    if isinstance(value, Mapping):
        return _FrozenDict(
            {str(key): _freeze_json(child) for key, child in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return _FrozenList(_freeze_json(child) for child in value)
    return value


def _typed_frame(tag: str, value: object) -> bytes:
    if not tag or not tag.isascii() or any(character in tag for character in ":\r\n"):
        raise ValueError("substrate frame tag must be non-empty safe ASCII")
    if value is None:
        marker = b"n"
        payload = b""
    elif isinstance(value, bool):
        marker = b"b"
        payload = b"1" if value else b"0"
    elif isinstance(value, int):
        marker = b"i"
        payload = str(value).encode("ascii")
    elif isinstance(value, str):
        marker = b"s"
        payload = value.encode("utf-8")
    else:
        raise TypeError(
            f"unsupported substrate frame value type: {type(value).__name__}"
        )
    return (
        tag.encode("ascii")
        + b":"
        + marker
        + b":"
        + str(len(payload)).encode("ascii")
        + b":"
        + payload
        + b"\n"
    )


def _chapter_resource_hrefs(chapter: Mapping[str, object]) -> tuple[str, ...]:
    hrefs: list[str] = []
    seen: set[str] = set()
    raw_hrefs: list[object] = [chapter.get("href")]
    for paragraph in _mapping_sequence(
        chapter.get("paragraphs"),
        pointer="/chapter/paragraphs",
    ):
        raw_hrefs.append(paragraph.get("href"))
    for raw_href in raw_hrefs:
        if raw_href is None or raw_href == "":
            continue
        if not isinstance(raw_href, str):
            raise PublicationIdentityError(
                "invalid_book_document_href",
                "canonical BookDocument href must be a string",
            )
        href = _normalize_book_href(raw_href)
        if href not in seen:
            seen.add(href)
            hrefs.append(href)
    return tuple(hrefs)


def _optional_normalized_href(document: Mapping[str, object], key: str) -> str | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if not isinstance(value, str):
        raise PublicationIdentityError(
            "invalid_book_document_href",
            "canonical BookDocument href must be a string or null",
        )
    if value == "":
        return ""
    return _normalize_book_href(value)


def _normalize_book_href(value: str) -> str:
    try:
        return normalize_epub_href(value)
    except EpubSourceError as exc:
        raise PublicationIdentityError(
            "invalid_book_document_href",
            "canonical BookDocument href must be a safe OPF-relative resource href",
        ) from exc


def _optional_exact_text(document: Mapping[str, object], key: str) -> str | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if not isinstance(value, str):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be a string or null",
        )
    return value


def _required_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key, _MISSING)
    if not isinstance(value, str):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be a string",
        )
    return value


def _optional_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be a string",
        )
    return value


def _required_int(document: Mapping[str, object], key: str) -> int:
    value = document.get(key, _MISSING)
    if isinstance(value, bool) or not isinstance(value, int):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be an integer",
        )
    return value


def _optional_int(document: Mapping[str, object], key: str) -> int | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be an integer or null",
        )
    return value


def _mapping_sequence(value: object, *, pointer: str) -> list[Mapping[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise PublicationIdentityError(
            "invalid_book_document_field",
            "canonical BookDocument collection must be an array",
            json_pointer=pointer,
        )
    result: list[Mapping[str, object]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise PublicationIdentityError(
                "invalid_book_document_field",
                "canonical BookDocument array item must be an object",
                json_pointer=f"{pointer}/{index}",
            )
        result.append(item)
    return result


def _first_difference(
    rebuilt: object,
    persisted: object,
    pointer: str = "",
) -> tuple[str, object, object] | None:
    if type(rebuilt) is not type(persisted):
        return pointer or "", rebuilt, persisted
    if isinstance(rebuilt, Mapping):
        keys = tuple(rebuilt.keys())
        if keys != tuple(persisted.keys()):  # type: ignore[union-attr]
            return pointer or "", rebuilt, persisted
        for key in keys:
            child_pointer = f"{pointer}/{_escape_pointer_token(str(key))}"
            difference = _first_difference(
                rebuilt[key],
                persisted[key],  # type: ignore[index]
                child_pointer,
            )
            if difference is not None:
                return difference
        return None
    if isinstance(rebuilt, list):
        if len(rebuilt) != len(persisted):  # type: ignore[arg-type]
            return pointer or "", rebuilt, persisted
        for index, value in enumerate(rebuilt):
            difference = _first_difference(
                value,
                persisted[index],  # type: ignore[index]
                f"{pointer}/{index}",
            )
            if difference is not None:
                return difference
        return None
    if rebuilt != persisted:
        return pointer or "", rebuilt, persisted
    return None


def _field_digest(value: object) -> str:
    if value is _MISSING:
        payload = b"<missing>"
    else:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _escape_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")
