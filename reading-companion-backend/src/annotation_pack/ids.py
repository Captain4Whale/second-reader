"""Deterministic UUIDv5 identities for Annotation Pack v0.

Every public identity is serialized as a canonical lowercase UUID URN.  The
namespace UUIDs and NUL-framed names in this module are protocol material: a
change to either changes identity and therefore requires a new protocol major.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import re
import unicodedata
from uuid import NAMESPACE_URL, RFC_4122, UUID, uuid5


__all__ = [
    "ANCHOR_NAMESPACE",
    "ANNOTATION_NAMESPACE",
    "CREATOR_CONTRACT_MAJOR",
    "CREATOR_NAMESPACE",
    "DEFAULT_SPEC_MAJOR",
    "EDITION_NAMESPACE",
    "FILE_NAMESPACE",
    "GENERATOR_CONTRACT_MAJOR",
    "GENERATOR_NAMESPACE",
    "PACK_NAMESPACE",
    "TRACK_NAMESPACE",
    "WORK_NAMESPACE",
    "anchor_id",
    "asserted_work_id",
    "default_creator_id",
    "default_generator_id",
    "edition_id",
    "file_id",
    "pack_id",
    "provisional_work_id",
    "track_id",
    "uuid5_urn",
]

_UUID_NAMESPACE_ROOT = (
    "https://captain4whale.github.io/second-reader/ns/annotation-pack/uuid"
)


def _audited_namespace(kind: str, expected: str) -> UUID:
    audited = UUID(expected)
    derived = uuid5(NAMESPACE_URL, f"{_UUID_NAMESPACE_ROOT}/{kind}/v0")
    if derived != audited:  # pragma: no cover - guards immutable literals
        raise AssertionError(f"audited {kind} namespace UUID does not match its IRI")
    return audited


# These literals are the audited UUIDv5(NAMESPACE_URL, ``<root>/<kind>/v0``)
# results.  Keep them literal so an accidental namespace-name edit is visible
# as a failing fixed-vector test rather than silently changing every identity.
WORK_NAMESPACE = _audited_namespace("work", "e818f38e-2894-5910-a94f-afec1212f840")
EDITION_NAMESPACE = _audited_namespace(
    "edition", "82f700a5-7f2d-5c1d-902c-7ff9fe327044"
)
FILE_NAMESPACE = _audited_namespace("file", "9755ee25-0dad-51a9-a36d-63589e35707c")
TRACK_NAMESPACE = _audited_namespace("track", "011c6a5f-2255-5b98-b86a-8f1a55548652")
PACK_NAMESPACE = _audited_namespace("pack", "15a1b369-656b-55cb-bfa1-55a529a1f39e")
ANCHOR_NAMESPACE = _audited_namespace("anchor", "3a26c857-f475-506c-a16a-219763fd1ce9")
ANNOTATION_NAMESPACE = _audited_namespace(
    "annotation", "ab5c7848-4a52-5b43-a01b-f76dbce62959"
)
CREATOR_NAMESPACE = _audited_namespace(
    "creator", "e0d4d5df-e315-5db3-9667-3f89a814f602"
)
GENERATOR_NAMESPACE = _audited_namespace(
    "generator", "dc17bd39-4e7c-574f-9aa0-87d4fe7e927b"
)

CONTENT_FINGERPRINT_ALGORITHM_VERSION = "sr-book-document-text-v1"
EPUB_MEDIA_TYPE = "application/epub+zip"
CREATOR_CONTRACT_MAJOR = 0
GENERATOR_CONTRACT_MAJOR = 0
DEFAULT_SPEC_MAJOR = 0

_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_UNICODE_WHITE_SPACE_RE = re.compile(
    "[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a"
    "\u2028\u2029\u202f\u205f\u3000]+"
)


def uuid5_urn(namespace: UUID, canonical_name: str) -> str:
    """Return the canonical lowercase URN for a UUIDv5 name."""

    if not isinstance(namespace, UUID):
        raise TypeError("namespace must be a UUID")
    if not isinstance(canonical_name, str):
        raise TypeError("canonical_name must be a string")
    if not canonical_name:
        raise ValueError("canonical_name must not be empty")
    generated = uuid5(namespace, canonical_name)
    if generated.version != 5 or generated.variant != RFC_4122:  # pragma: no cover
        raise AssertionError("uuid5() returned a non-RFC-4122 UUIDv5")
    return generated.urn


def asserted_work_id(identifiers: Iterable[tuple[str, str]]) -> str:
    """Derive a Work id from an order-independent asserted identifier set."""

    normalized: set[str] = set()
    for position, identifier in enumerate(identifiers):
        if not isinstance(identifier, tuple) or len(identifier) != 2:
            raise TypeError(f"identifiers[{position}] must be a (scheme, value) tuple")
        scheme = _nfc_required(identifier[0], f"identifiers[{position}].scheme")
        value = _nfc_required(identifier[1], f"identifiers[{position}].value")
        normalized.add(f"{scheme}:{value}")
    if not normalized:
        raise ValueError("asserted work identity requires at least one identifier")
    return uuid5_urn(
        WORK_NAMESPACE, _nul_frame("work", "asserted", *sorted(normalized))
    )


def provisional_work_id(title: str, creators: Sequence[str]) -> str:
    """Derive a non-authoritative Work candidate from normalized metadata."""

    normalized_title = _normalize_work_metadata(title, "title")
    normalized_creators = tuple(
        _normalize_work_metadata(creator, f"creators[{position}]")
        for position, creator in enumerate(creators)
    )
    return uuid5_urn(
        WORK_NAMESPACE,
        _nul_frame("work", "provisional", normalized_title, *normalized_creators),
    )


def edition_id(content_sha256: str) -> str:
    """Derive the textual Edition id from its v0 content fingerprint."""

    digest = _lowercase_sha256(content_sha256, "content_sha256")
    return uuid5_urn(
        EDITION_NAMESPACE,
        _nul_frame("edition", CONTENT_FINGERPRINT_ALGORITHM_VERSION, digest),
    )


def file_id(file_sha256: str) -> str:
    """Derive the exact-file id for EPUB bytes."""

    digest = _lowercase_sha256(file_sha256, "file_sha256")
    return uuid5_urn(
        FILE_NAMESPACE,
        _nul_frame("file", EPUB_MEDIA_TYPE, "sha256", digest),
    )


def default_creator_id(
    contract_major: int = CREATOR_CONTRACT_MAJOR,
) -> str:
    """Return the stable id of the default Second Reader software creator."""

    major = _major_token(contract_major, "contract_major")
    return uuid5_urn(
        CREATOR_NAMESPACE,
        _nul_frame("creator", "software", "second-reader-agent", major),
    )


def default_generator_id(
    contract_major: int = GENERATOR_CONTRACT_MAJOR,
) -> str:
    """Return the stable id of the reference Annotation Pack exporter."""

    major = _major_token(contract_major, "contract_major")
    return uuid5_urn(
        GENERATOR_NAMESPACE,
        _nul_frame(
            "generator",
            "software",
            "second-reader-annotation-pack-exporter",
            major,
        ),
    )


def track_id(edition: str, creator: str, track_key: str) -> str:
    """Derive the logical Annotation Track id within an Edition."""

    canonical_edition = _canonical_uuid5_urn(edition, "edition")
    canonical_creator = _canonical_uuid5_urn(creator, "creator")
    canonical_track_key = _nfc_required(track_key, "track_key")
    return uuid5_urn(
        TRACK_NAMESPACE,
        _nul_frame("track", canonical_edition, canonical_creator, canonical_track_key),
    )


def pack_id(
    edition: str,
    track: str,
    spec_major: int = DEFAULT_SPEC_MAJOR,
) -> str:
    """Derive the stable v0 Edition-by-Track container id."""

    major = _major_token(spec_major, "spec_major")
    canonical_edition = _canonical_uuid5_urn(edition, "edition")
    canonical_track = _canonical_uuid5_urn(track, "track")
    return uuid5_urn(
        PACK_NAMESPACE,
        _nul_frame("pack", major, canonical_edition, canonical_track),
    )


def anchor_id(
    edition: str,
    href: str,
    chapter_fingerprint: str,
    *,
    start_chapter_id: int,
    start_paragraph_index: int,
    start_char_offset: int,
    end_chapter_id: int,
    end_paragraph_index: int,
    end_char_offset: int,
    quote_sha256: str,
) -> str:
    """Derive an exact target id from frozen paragraph-char coordinates.

    Each coordinate integer is a separate NUL-framed field.  Optional CFI is
    deliberately absent so adding or omitting a verified locator never changes
    the identity of the required href/quote/paragraph anchor.
    """

    canonical_edition = _canonical_uuid5_urn(edition, "edition")
    canonical_href = _nfc_required(href, "href")
    chapter_digest = _lowercase_sha256(
        chapter_fingerprint,
        "chapter_fingerprint",
    )
    quote_digest = _lowercase_sha256(quote_sha256, "quote_sha256")
    start_chapter = _integer_token(start_chapter_id, "start_chapter_id")
    start_paragraph = _positive_integer_token(
        start_paragraph_index,
        "start_paragraph_index",
    )
    start_offset = _non_negative_integer_token(
        start_char_offset,
        "start_char_offset",
    )
    end_chapter = _integer_token(end_chapter_id, "end_chapter_id")
    end_paragraph = _positive_integer_token(
        end_paragraph_index,
        "end_paragraph_index",
    )
    end_offset = _non_negative_integer_token(end_char_offset, "end_char_offset")
    return uuid5_urn(
        ANCHOR_NAMESPACE,
        _nul_frame(
            "anchor",
            canonical_edition,
            canonical_href,
            chapter_digest,
            start_chapter,
            start_paragraph,
            start_offset,
            end_chapter,
            end_paragraph,
            end_offset,
            quote_digest,
        ),
    )


def _nul_frame(*fields: str) -> str:
    for position, field in enumerate(fields):
        if not isinstance(field, str):
            raise TypeError(f"canonical field {position} must be a string")
        if not field:
            raise ValueError(f"canonical field {position} must not be empty")
        if "\0" in field:
            raise ValueError(f"canonical field {position} must not contain NUL")
    return "\0".join(fields)


def _nfc_required(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if "\0" in value:
        raise ValueError(f"{field} must not contain NUL")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized:
        raise ValueError(f"{field} must not be empty")
    return normalized


def _normalize_work_metadata(value: str, field: str) -> str:
    """Apply the protocol's N(s) normalization to provisional Work metadata."""

    normalized = _nfc_required(value, field).replace("\r\n", "\n").replace("\r", "\n")
    normalized = _UNICODE_WHITE_SPACE_RE.sub(" ", normalized).strip(" ")
    if not normalized:
        raise ValueError(f"{field} must not be empty after normalization")
    return normalized


def _lowercase_sha256(value: str, field: str) -> str:
    candidate = _nfc_required(value, field)
    if not _SHA256_RE.fullmatch(candidate):
        raise ValueError(f"{field} must be exactly 64 lowercase hexadecimal characters")
    return candidate


def _canonical_uuid5_urn(value: str, field: str) -> str:
    candidate = _nfc_required(value, field)
    try:
        parsed = UUID(candidate)
    except ValueError as exc:
        raise ValueError(f"{field} must be a canonical UUID URN") from exc
    if candidate != parsed.urn:
        raise ValueError(f"{field} must be a lowercase canonical UUID URN")
    if parsed.version != 5 or parsed.variant != RFC_4122:
        raise ValueError(f"{field} must be an RFC-4122 UUIDv5 URN")
    return candidate


def _major_token(value: int, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return str(value)


def _integer_token(value: int, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an integer")
    return str(value)


def _non_negative_integer_token(value: int, field: str) -> str:
    token = _integer_token(value, field)
    if value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return token


def _positive_integer_token(value: int, field: str) -> str:
    token = _integer_token(value, field)
    if value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return token
