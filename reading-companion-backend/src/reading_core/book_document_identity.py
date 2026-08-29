"""Frozen identity projection for the canonical BookDocument substrate."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json

from .epub_href import EpubHrefError, normalize_epub_href


SUBSTRATE_FINGERPRINT_VERSION = "sr-book-document-substrate-v1"
_SUBSTRATE_HEADER = b"SECOND-READER-BOOK-DOCUMENT-SUBSTRATE-V1\n"
_TEXT_ROLES = {"chapter_heading", "section_heading", "body", "auxiliary"}
_MISSING = object()


class BookDocumentIdentityError(ValueError):
    """Stable sanitized BookDocument identity/projection failure."""

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
class SubstrateComparison:
    digest: str
    projection: Mapping[str, object]


def project_book_document_substrate(
    document: Mapping[str, object],
) -> dict[str, object]:
    """Build the exact field-level v1 substrate projection."""

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
                raise BookDocumentIdentityError(
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
            chapter.get("paragraphs"), pointer="/chapters/*/paragraphs"
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


def book_document_substrate_digest(document: Mapping[str, object]) -> str:
    projection = project_book_document_substrate(document)
    return hashlib.sha256(book_document_substrate_stream(projection)).hexdigest()


def compare_book_document_substrates(
    rebuilt: Mapping[str, object], persisted: Mapping[str, object]
) -> SubstrateComparison:
    """Fail closed on the first field mismatch without exposing field values."""

    rebuilt_projection = project_book_document_substrate(rebuilt)
    persisted_projection = project_book_document_substrate(persisted)
    difference = _first_difference(rebuilt_projection, persisted_projection)
    if difference is not None:
        pointer, rebuilt_value, persisted_value = difference
        raise BookDocumentIdentityError(
            "publication_substrate_mismatch",
            "persisted BookDocument does not match the verified source EPUB",
            json_pointer=pointer,
            rebuilt_field_sha256=_field_digest(rebuilt_value),
            persisted_field_sha256=_field_digest(persisted_value),
        )
    stream = book_document_substrate_stream(rebuilt_projection)
    return SubstrateComparison(
        digest=hashlib.sha256(stream).hexdigest(), projection=rebuilt_projection
    )


def _optional_normalized_href(
    document: Mapping[str, object], key: str
) -> str | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if not isinstance(value, str):
        raise BookDocumentIdentityError(
            "invalid_book_document_href",
            "canonical BookDocument href must be a string or null",
        )
    if value == "":
        return ""
    try:
        return normalize_epub_href(value)
    except EpubHrefError as exc:
        raise BookDocumentIdentityError(
            "invalid_book_document_href",
            "canonical BookDocument href must be a safe OPF-relative resource href",
        ) from exc


def _optional_exact_text(document: Mapping[str, object], key: str) -> str | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if not isinstance(value, str):
        raise BookDocumentIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be a string or null",
        )
    return value


def _required_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key, _MISSING)
    if not isinstance(value, str):
        raise BookDocumentIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be a string",
        )
    return value


def _required_int(document: Mapping[str, object], key: str) -> int:
    value = document.get(key, _MISSING)
    if isinstance(value, bool) or not isinstance(value, int):
        raise BookDocumentIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be an integer",
        )
    return value


def _optional_int(document: Mapping[str, object], key: str) -> int | None:
    value = document.get(key, _MISSING)
    if value is _MISSING or value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise BookDocumentIdentityError(
            "invalid_book_document_field",
            f"canonical BookDocument {key} must be an integer or null",
        )
    return value


def _mapping_sequence(value: object, *, pointer: str) -> list[Mapping[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise BookDocumentIdentityError(
            "invalid_book_document_field",
            "canonical BookDocument collection must be an array",
            json_pointer=pointer,
        )
    result: list[Mapping[str, object]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise BookDocumentIdentityError(
                "invalid_book_document_field",
                "canonical BookDocument array item must be an object",
                json_pointer=f"{pointer}/{index}",
            )
        result.append(item)
    return result


def _typed_frame(tag: str, value: object) -> bytes:
    if not tag or not tag.isascii() or any(character in tag for character in ":\r\n"):
        raise ValueError("substrate frame tag must be non-empty safe ASCII")
    if value is None:
        marker, payload = b"n", b""
    elif isinstance(value, bool):
        marker, payload = b"b", b"1" if value else b"0"
    elif isinstance(value, int):
        marker, payload = b"i", str(value).encode("ascii")
    elif isinstance(value, str):
        marker, payload = b"s", value.encode("utf-8")
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


def _first_difference(
    rebuilt: object, persisted: object, pointer: str = ""
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
                rebuilt[key], persisted[key], child_pointer  # type: ignore[index]
            )
            if difference is not None:
                return difference
        return None
    if isinstance(rebuilt, list):
        if len(rebuilt) != len(persisted):  # type: ignore[arg-type]
            return pointer or "", rebuilt, persisted
        for index, value in enumerate(rebuilt):
            difference = _first_difference(
                value, persisted[index], f"{pointer}/{index}"  # type: ignore[index]
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
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _escape_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


__all__ = [
    "BookDocumentIdentityError",
    "SUBSTRATE_FINGERPRINT_VERSION",
    "SubstrateComparison",
    "book_document_substrate_digest",
    "book_document_substrate_stream",
    "compare_book_document_substrates",
    "project_book_document_substrate",
]
