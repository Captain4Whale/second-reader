"""Verified EPUB XHTML resource text indexing for Annotation Pack anchors.

The index in this module is deliberately built from an already-open verified
EPUB handle.  It never resolves or reopens a local pathname.  Public target
hrefs therefore stay bound to the exact file bytes used for publication
identity while malformed or parser-incoherent resources remain explicitly
unverifiable instead of receiving a best-effort plaintext fallback.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import re
from types import MappingProxyType
from typing import Any, BinaryIO, Final
import xml.etree.ElementTree as ET
import zipfile

from src.annotation_pack.epub_source import VerifiedEpubSource, normalize_epub_href


RESOURCE_TEXT_NORMALIZATION_VERSION: Final = "sr-epub-resource-text-v1"
MAX_RESOURCE_XML_BYTES: Final = 16 * 1024 * 1024
MAX_RESOURCE_XML_ELEMENTS: Final = 100_000
MAX_RESOURCE_XML_DEPTH: Final = 256
MAX_RESOURCE_XML_MARKUP_DELIMITERS: Final = MAX_RESOURCE_XML_ELEMENTS
MAX_RESOURCE_TEXT_TRAVERSAL_CODEPOINTS: Final = 32 * 1024 * 1024
MAX_RESOURCE_BLOCKS: Final = 100_000
MAX_RESOURCE_TEXT_CODEPOINTS: Final = 16 * 1024 * 1024

_BLOCK_TAGS: Final = frozenset(
    {
        "p",
        "li",
        "blockquote",
        "caption",
        "div",
        "figcaption",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }
)
_HEADING_TAGS: Final = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_XML_DECLARATION_TOKEN: Final = re.compile(
    rb"<!\s*(?:DOCTYPE|ENTITY)\b",
    re.IGNORECASE,
)
_SAFE_HTML5_DOCTYPE_PROLOG: Final = re.compile(
    rb"\A(?:\xef\xbb\xbf)?[ \t\r\n]*"
    rb"(?:<\?xml\b[^>]*\?>[ \t\r\n]*)?"
    rb"(?P<doctype><!DOCTYPE[ \t\r\n]+html[ \t\r\n]*>)",
    re.IGNORECASE,
)
_WHITE_SPACE_RUN: Final = re.compile(r"\s+")


class EpubResourceIndexError(ValueError):
    """A stable failure to consume the already-verified EPUB handle."""

    __slots__ = ("code", "message")

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class EpubManifestIndex:
    """Safe EPUB-internal manifest membership for anchor resolution."""

    opf_path: str
    manifest_hrefs: frozenset[str]
    text_resource_hrefs: frozenset[str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "manifest_hrefs", frozenset(self.manifest_hrefs))
        object.__setattr__(
            self,
            "text_resource_hrefs",
            frozenset(self.text_resource_hrefs),
        )


@dataclass(frozen=True, slots=True)
class EpubResourceIndex:
    """Immutable exact-resource text and BookDocument paragraph coordinates.

    ``resource_texts`` intentionally stays out of ``repr`` so routine logging
    cannot copy book prose.  Every range is a Python Unicode code-point,
    end-exclusive interval into the corresponding resource text.
    """

    manifest: EpubManifestIndex
    resource_texts: Mapping[str, str] = field(repr=False)
    paragraph_ranges: Mapping[tuple[int, int], tuple[str, int, int]] = field(
        repr=False
    )
    unverifiable_hrefs: frozenset[str]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "resource_texts",
            MappingProxyType(dict(self.resource_texts)),
        )
        object.__setattr__(
            self,
            "paragraph_ranges",
            MappingProxyType(dict(self.paragraph_ranges)),
        )
        object.__setattr__(
            self,
            "unverifiable_hrefs",
            frozenset(self.unverifiable_hrefs),
        )

    @property
    def opf_path(self) -> str:
        """Compatibility view of the nested verified manifest."""

        return self.manifest.opf_path

    @property
    def manifest_hrefs(self) -> frozenset[str]:
        """Compatibility view of all verified manifest hrefs."""

        return self.manifest.manifest_hrefs

    @property
    def text_resource_hrefs(self) -> frozenset[str]:
        """Compatibility view of verified XHTML/HTML manifest hrefs."""

        return self.manifest.text_resource_hrefs


@dataclass(frozen=True, slots=True)
class _ResourceBlock:
    text: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class _XmlStructure:
    duplicate_container_ids: frozenset[int]


def build_epub_manifest_index(source: VerifiedEpubSource) -> EpubManifestIndex:
    """Project the verified OPF manifest without retaining a local path."""

    return EpubManifestIndex(
        opf_path=source.opf_path,
        manifest_hrefs=frozenset(item.href for item in source.manifest_items),
        text_resource_hrefs=frozenset(
            item.href
            for item in source.manifest_items
            if item.media_type in {"application/xhtml+xml", "text/html"}
        ),
    )


def build_epub_resource_index(
    *,
    source: VerifiedEpubSource,
    source_handle: BinaryIO,
    rebuilt_book_document: Mapping[str, Any],
    manifest: EpubManifestIndex | None = None,
) -> EpubResourceIndex:
    """Build exact logical resource streams from one verified open handle.

    XML parse failures and exact BookDocument/block mismatches are represented
    in ``unverifiable_hrefs``.  No regex or plaintext recovery is attempted.
    Failure to consume the supplied EPUB handle itself is a stable hard error,
    because it violates the caller's verified-handle boundary.
    """

    expected_manifest = build_epub_manifest_index(source)
    if manifest is not None and manifest != expected_manifest:
        raise EpubResourceIndexError(
            "invalid_epub_manifest_index",
            "The supplied EPUB manifest index does not match the verified source.",
        )
    manifest_index = manifest or expected_manifest
    resource_texts: dict[str, str] = {}
    blocks_by_href: dict[str, tuple[_ResourceBlock, ...]] = {}
    unverifiable_hrefs: set[str] = set()

    try:
        source_handle.seek(0)
        with zipfile.ZipFile(source_handle, mode="r") as archive:
            for item in source.manifest_items:
                if item.href not in manifest_index.text_resource_hrefs:
                    continue
                parsed = _read_resource_blocks(archive, item.archive_path)
                if parsed is None:
                    unverifiable_hrefs.add(item.href)
                    continue
                resource_text, blocks = parsed
                resource_texts[item.href] = resource_text
                blocks_by_href[item.href] = blocks
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
        raise EpubResourceIndexError(
            "verified_epub_handle_unavailable",
            "The verified EPUB handle could not be consumed for resource indexing.",
        ) from exc

    paragraph_ranges = _map_book_document_paragraphs(
        rebuilt_book_document,
        manifest=manifest_index,
        blocks_by_href=blocks_by_href,
        unverifiable_hrefs=unverifiable_hrefs,
    )
    if unverifiable_hrefs:
        paragraph_ranges = {
            key: value
            for key, value in paragraph_ranges.items()
            if value[0] not in unverifiable_hrefs
        }
    return EpubResourceIndex(
        manifest=manifest_index,
        resource_texts=resource_texts,
        paragraph_ranges=paragraph_ranges,
        unverifiable_hrefs=frozenset(unverifiable_hrefs),
    )


def _read_resource_blocks(
    archive: zipfile.ZipFile,
    archive_path: str,
) -> tuple[str, tuple[_ResourceBlock, ...]] | None:
    try:
        info = archive.getinfo(archive_path)
        if info.is_dir() or info.file_size > MAX_RESOURCE_XML_BYTES:
            return None
        with archive.open(info, mode="r") as member:
            content = member.read(MAX_RESOURCE_XML_BYTES + 1)
    except (KeyError, OSError, RuntimeError, ValueError, zipfile.BadZipFile):
        return None
    if len(content) > MAX_RESOURCE_XML_BYTES:
        return None
    return _resource_text_and_blocks(content)


def _resource_text_and_blocks(
    content: bytes,
) -> tuple[str, tuple[_ResourceBlock, ...]] | None:
    if (
        b"\x00" in content
        or _has_unsafe_resource_declaration(content)
        or content.count(b"<") > MAX_RESOURCE_XML_MARKUP_DELIMITERS
    ):
        return None
    try:
        content.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None
    try:
        root = ET.fromstring(content)
    except (ET.ParseError, LookupError, UnicodeError, ValueError):
        return None
    if not isinstance(root.tag, str) or _local_name(root.tag) != "html":
        return None
    structure = _bounded_xml_structure(root)
    if structure is None:
        return None

    texts: list[str] = []
    text_codepoints = 0
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        tag = _local_name(element.tag)
        if tag not in _BLOCK_TAGS:
            continue
        if id(element) in structure.duplicate_container_ids:
            continue
        text = _normalize_block_text("".join(element.itertext()))
        if not text:
            continue
        texts.append(text)
        text_codepoints += len(text)
        if (
            len(texts) > MAX_RESOURCE_BLOCKS
            or text_codepoints > MAX_RESOURCE_TEXT_CODEPOINTS
        ):
            return None

    stream_parts: list[str] = []
    blocks: list[_ResourceBlock] = []
    cursor = 0
    for index, text in enumerate(texts):
        if index:
            stream_parts.append("\n\n")
            cursor += 2
        start = cursor
        stream_parts.append(text)
        cursor += len(text)
        blocks.append(_ResourceBlock(text=text, start=start, end=cursor))
    return "".join(stream_parts), tuple(blocks)


def _has_unsafe_resource_declaration(content: bytes) -> bool:
    """Allow only one canonical simple HTML5 doctype in the XML prolog.

    EPUB XHTML commonly includes ``<!DOCTYPE html>``.  That declaration has no
    external or internal subset and is safe for the bounded ElementTree parse
    below.  Every other DOCTYPE/ENTITY token remains fail-closed, including
    SYSTEM, PUBLIC, internal subsets, duplicate declarations, and declarations
    placed outside the initial XML prolog.
    """

    declarations = tuple(_XML_DECLARATION_TOKEN.finditer(content))
    if not declarations:
        return False
    safe_prolog = _SAFE_HTML5_DOCTYPE_PROLOG.match(content)
    if safe_prolog is None or len(declarations) != 1:
        return True
    return declarations[0].start() != safe_prolog.start("doctype")


def _map_book_document_paragraphs(
    document: Mapping[str, Any],
    *,
    manifest: EpubManifestIndex,
    blocks_by_href: Mapping[str, tuple[_ResourceBlock, ...]],
    unverifiable_hrefs: set[str],
) -> dict[tuple[int, int], tuple[str, int, int]]:
    ranges: dict[tuple[int, int], tuple[str, int, int]] = {}
    chapters = document.get("chapters")
    if not _is_mapping_sequence(chapters):
        raise EpubResourceIndexError(
            "invalid_rebuilt_book_document",
            "The rebuilt BookDocument chapter collection is invalid.",
        )

    for chapter in chapters:
        chapter_id = chapter.get("id")
        if isinstance(chapter_id, bool) or not isinstance(chapter_id, int):
            raise EpubResourceIndexError(
                "invalid_rebuilt_book_document",
                "The rebuilt BookDocument chapter identity is invalid.",
            )
        chapter_href = _canonical_document_href(chapter.get("href"))
        paragraphs = chapter.get("paragraphs")
        if not _is_mapping_sequence(paragraphs):
            raise EpubResourceIndexError(
                "invalid_rebuilt_book_document",
                "The rebuilt BookDocument paragraph collection is invalid.",
            )

        records_by_href: dict[str, list[tuple[tuple[int, int], str]]] = {}
        for paragraph in paragraphs:
            paragraph_index = paragraph.get("paragraph_index")
            text = paragraph.get("text")
            if (
                isinstance(paragraph_index, bool)
                or not isinstance(paragraph_index, int)
                or not isinstance(text, str)
            ):
                raise EpubResourceIndexError(
                    "invalid_rebuilt_book_document",
                    "The rebuilt BookDocument paragraph coordinate is invalid.",
                )
            href = _canonical_document_href(paragraph.get("href")) or chapter_href
            if href is None or href not in manifest.text_resource_hrefs:
                continue
            records_by_href.setdefault(href, []).append(
                ((chapter_id, paragraph_index), text)
            )

        for href, records in records_by_href.items():
            blocks = blocks_by_href.get(href)
            keys = tuple(key for key, _text in records)
            if (
                blocks is None
                or len(records) != len(blocks)
                or len(set(keys)) != len(keys)
                or any(
                    paragraph_text != block.text
                    for (_key, paragraph_text), block in zip(
                        records,
                        blocks,
                        strict=True,
                    )
                )
            ):
                unverifiable_hrefs.add(href)
                continue
            for (key, _paragraph_text), block in zip(records, blocks, strict=True):
                existing = ranges.get(key)
                value = (href, block.start, block.end)
                if existing is not None and existing != value:
                    unverifiable_hrefs.add(href)
                    unverifiable_hrefs.add(existing[0])
                    continue
                ranges[key] = value
    return ranges


def _canonical_document_href(value: object) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise EpubResourceIndexError(
            "invalid_rebuilt_book_document",
            "The rebuilt BookDocument resource href is invalid.",
        )
    try:
        return normalize_epub_href(value)
    except ValueError as exc:
        raise EpubResourceIndexError(
            "invalid_rebuilt_book_document",
            "The rebuilt BookDocument resource href is invalid.",
        ) from exc


def _bounded_xml_structure(root: ET.Element) -> _XmlStructure | None:
    """Precompute exact duplicate containers under a hard traversal budget.

    The reverse pass is linear in tree size.  Before any ``itertext`` call, the
    second pass sums descendant text lengths for every block that v1 would
    actually emit.  This prevents nested included blocks from multiplying a
    small XHTML resource into unbounded repeated descendant traversal.
    """

    elements: list[ET.Element] = []
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        elements.append(element)
        if (
            len(elements) > MAX_RESOURCE_XML_ELEMENTS
            or depth > MAX_RESOURCE_XML_DEPTH
        ):
            return None
        children = list(element)
        stack.extend((child, depth + 1) for child in reversed(children))

    subtree_codepoints: dict[int, int] = {}
    subtree_has_text: dict[int, bool] = {}
    direct_has_text: dict[int, bool] = {}
    for element in reversed(elements):
        codepoints = len(element.text or "")
        has_direct_text = _contains_non_whitespace(element.text)
        has_subtree_text = has_direct_text
        for child in list(element):
            codepoints += subtree_codepoints[id(child)] + len(child.tail or "")
            has_subtree_text = (
                has_subtree_text
                or subtree_has_text[id(child)]
                or _contains_non_whitespace(child.tail)
            )
            has_direct_text = has_direct_text or _contains_non_whitespace(child.tail)
        subtree_codepoints[id(element)] = codepoints
        subtree_has_text[id(element)] = has_subtree_text
        direct_has_text[id(element)] = has_direct_text

    duplicate_container_ids: set[int] = set()
    traversal_codepoints = 0
    for element in elements:
        if not isinstance(element.tag, str):
            continue
        tag = _local_name(element.tag)
        if tag not in _BLOCK_TAGS:
            continue
        has_textual_block_child = any(
            isinstance(child.tag, str)
            and _local_name(child.tag) in _BLOCK_TAGS
            and subtree_has_text[id(child)]
            for child in list(element)
        )
        duplicate_container = bool(
            tag not in _HEADING_TAGS
            and subtree_has_text[id(element)]
            and has_textual_block_child
            and not direct_has_text[id(element)]
        )
        if duplicate_container:
            duplicate_container_ids.add(id(element))
            continue
        traversal_codepoints += subtree_codepoints[id(element)]
        if traversal_codepoints > MAX_RESOURCE_TEXT_TRAVERSAL_CODEPOINTS:
            return None
    return _XmlStructure(
        duplicate_container_ids=frozenset(duplicate_container_ids),
    )


def _contains_non_whitespace(value: str | None) -> bool:
    return bool(value and _WHITE_SPACE_RUN.fullmatch(value) is None)


def _normalize_block_text(value: str) -> str:
    return _WHITE_SPACE_RUN.sub(" ", value).strip()


def _local_name(tag: str) -> str:
    value = tag.rsplit("}", 1)[-1] if "}" in tag else tag.rsplit(":", 1)[-1]
    return value.casefold()


def _is_mapping_sequence(value: object) -> bool:
    return bool(
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
        and all(isinstance(item, Mapping) for item in value)
    )


__all__ = [
    "MAX_RESOURCE_BLOCKS",
    "MAX_RESOURCE_TEXT_CODEPOINTS",
    "MAX_RESOURCE_TEXT_TRAVERSAL_CODEPOINTS",
    "MAX_RESOURCE_XML_BYTES",
    "MAX_RESOURCE_XML_DEPTH",
    "MAX_RESOURCE_XML_ELEMENTS",
    "MAX_RESOURCE_XML_MARKUP_DELIMITERS",
    "RESOURCE_TEXT_NORMALIZATION_VERSION",
    "EpubManifestIndex",
    "EpubResourceIndex",
    "EpubResourceIndexError",
    "build_epub_manifest_index",
    "build_epub_resource_index",
]
