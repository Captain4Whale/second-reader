"""Strict, producer-neutral verification of source EPUB publications.

This module deliberately does not parse book prose.  It establishes the safe
file/archive/OPF boundary that identity and anchor code can build on without
trusting a runtime manifest, ZIP member name, or OPF href a second time.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import ipaddress
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
from types import MappingProxyType
from typing import Any, BinaryIO, Final
from urllib.parse import SplitResult, quote, unquote_to_bytes, urlsplit
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import zlib


DEFAULT_SOURCE_ASSET: Final = "_assets/source.epub"
EPUB_MEDIA_TYPE: Final = "application/epub+zip"
OPF_MEDIA_TYPE: Final = "application/oebps-package+xml"
HASH_CHUNK_BYTES: Final = 1024 * 1024
MAX_EPUB_BYTES: Final = 512 * 1024 * 1024
MAX_ZIP_ENTRIES: Final = 10_000
MAX_ZIP_ENTRY_BYTES: Final = 64 * 1024 * 1024
MAX_ZIP_TOTAL_BYTES: Final = 256 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO: Final = 1_000.0
MAX_XML_BYTES: Final = 2 * 1024 * 1024

_CONTAINER_PATH: Final = "META-INF/container.xml"
_CONTAINER_NAMESPACE: Final = "urn:oasis:names:tc:opendocument:xmlns:container"
_OPF_NAMESPACE: Final = "http://www.idpf.org/2007/opf"
_DC_NAMESPACE: Final = "http://purl.org/dc/elements/1.1/"
_FORBIDDEN_XML_DECLARATION = re.compile(rb"<!\s*(?:DOCTYPE|ENTITY)\b", re.I)
_INVALID_PERCENT_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
_MEDIA_TYPE = re.compile(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+\Z")
_SAFE_DECLARATION_TOKEN = re.compile(r"[A-Za-z0-9:._-]{1,128}\Z")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
_OPF_IDENTIFIER_MAX_LENGTH: Final = 2048
_MAX_PUBLIC_SCAN_DECODE_ROUNDS: Final = 4
_SAFE_PUBLICATION_URI_SCHEMES: Final = frozenset({"doi", "http", "https", "urn"})
_URN_URI = re.compile(
    r"urn:(?P<nid>[A-Za-z0-9](?:[A-Za-z0-9-]{0,30}[A-Za-z0-9])):"
    r"(?P<nss>.+)\Z",
    re.I,
)
_UNICODE_WHITE_SPACE: Final = frozenset(
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
_SECRET_PARAMETER = re.compile(
    r"(?<![A-Za-z0-9_])(?:access[_-]?token|api[_-]?key|auth(?:orization)?|"
    r"credential|jwt|key|password|private[_-]?key|secret|sig(?:nature)?|token)=",
    re.I,
)
_PRIVATE_PATH_FRAGMENT = re.compile(
    r"(?:^|[\s\"'=:(])(?:/(?:Users|home|etc|root|tmp|private|Volumes|var/folders)(?:/|$)|"
    r"[A-Za-z]:[\\/]|\\\\|~[\\/])",
    re.I,
)
_ABSOLUTE_POSIX_FRAGMENT = re.compile(
    r"(?<![A-Za-z0-9._~%/-])/(?![/\s])"
    r"(?:[^\s/\"']+)(?:/[^\s/\"']*)*"
)
_ABSOLUTE_WINDOWS_FRAGMENT = re.compile(
    r"(?<![A-Za-z0-9._~%/\\-])(?:[A-Za-z]:[\\/]|\\\\)(?!\s)"
)
_HOME_PATH_FRAGMENT = re.compile(r"(?<![A-Za-z0-9._~%/\\-])~[\\/](?!\s)")
_RELATIVE_LOCAL_PATH_FRAGMENT = re.compile(
    r"(?<![A-Za-z0-9._~%/\\-])(?:\.\.?[\\/]|_assets/|"
    r"(?:[^/\s?#()\[\]{}]+/)+[^/\s?#()\[\]{}]+\."
    r"(?:db|epub|json|log|md|opf|pickle|pkl|sqlite3?|txt|xml|xhtml?))"
    r"(?=$|[\s?#)\]}>;,])",
    re.I,
)
_FILE_URI_FRAGMENT = re.compile(r"(?<![A-Za-z0-9._~%+/-])file:", re.I)
_URI_CREDENTIALS = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/\s]+@")
_LOCAL_ARTIFACT_PATH_FRAGMENT = re.compile(
    r"(?:^|[\\/])[^\\/?#]+\.(?:db|log|pickle|pkl|sqlite3?)(?:$|[?#])",
    re.I,
)
_LEGACY_NUMERIC_HOST = re.compile(r"(?=.*[0-9])[0-9A-Fa-f.xX]+\Z")
_ZIP_LOCAL_HEADER = struct.Struct("<4s5H3L2H")
_ZIP_LOCAL_SIGNATURE: Final = b"PK\x03\x04"
_ZIP_ENCRYPTION_FLAGS: Final = (1 << 0) | (1 << 6) | (1 << 13)
_ZIP_SUPPORTED_METHODS: Final = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})


class EpubSourceError(ValueError):
    """A stable, sanitized source-verification failure."""

    __slots__ = ("code", "message")

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class EpubSourceWarning:
    """A deterministic, publication-safe metadata warning."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PublicationIdentifier:
    """One normalized edition/publication identifier from verified OPF data."""

    scheme: str
    value: str


@dataclass(frozen=True, slots=True)
class OpfIdentifier:
    """A normalized OPF identifier before public classification."""

    identifier_id: str | None
    value: str
    declared_scheme: str | None
    is_unique: bool


@dataclass(frozen=True, slots=True)
class EpubMetadata:
    """Sanitized descriptive and identifier metadata from the package document."""

    title: str
    creators: tuple[str, ...]
    language: str | None
    unique_identifier: str | None
    identifiers: tuple[OpfIdentifier, ...]
    publication_identifiers: tuple[PublicationIdentifier, ...]
    warnings: tuple[EpubSourceWarning, ...]


@dataclass(frozen=True, slots=True)
class ResolvedOpfHref:
    """Canonical OPF-relative href and the ZIP member it addresses."""

    href: str
    archive_path: str


@dataclass(frozen=True, slots=True)
class EpubManifestItem:
    """One locally resolved, present OPF manifest item."""

    item_id: str
    href: str
    archive_path: str
    media_type: str
    properties: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _FileSnapshot:
    device: int
    inode: int
    mode: int
    byte_length: int
    mtime_ns: int
    ctime_ns: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> _FileSnapshot:
        return cls(
            device=value.st_dev,
            inode=value.st_ino,
            mode=value.st_mode,
            byte_length=value.st_size,
            mtime_ns=value.st_mtime_ns,
            ctime_ns=value.st_ctime_ns,
        )


@dataclass(frozen=True, slots=True)
class VerifiedEpubSource:
    """Immutable result of strict source, ZIP, container, and OPF verification."""

    source_path: Path = field(repr=False, compare=False)
    _output_dir: Path = field(repr=False, compare=False)
    relative_path: str
    sha256: str
    byte_length: int
    opf_path: str
    metadata: EpubMetadata
    manifest_items: tuple[EpubManifestItem, ...]
    spine_item_ids: tuple[str, ...]
    archive_entries: tuple[str, ...]
    _snapshot: _FileSnapshot = field(repr=False, compare=False)

    @property
    def manifest_by_id(self) -> Mapping[str, EpubManifestItem]:
        return MappingProxyType({item.item_id: item for item in self.manifest_items})

    @property
    def manifest_by_href(self) -> Mapping[str, EpubManifestItem]:
        return MappingProxyType({item.href: item for item in self.manifest_items})

    @property
    def manifest_by_archive_path(self) -> Mapping[str, EpubManifestItem]:
        return MappingProxyType(
            {item.archive_path: item for item in self.manifest_items}
        )

    def assert_unchanged(self) -> None:
        """Re-hash the source before publication and fail closed on any drift."""

        digest, byte_length, snapshot, source_path = _fingerprint_source_reference(
            self._output_dir,
            self.relative_path,
            failure_code="input_changed_during_export",
        )
        if (
            digest != self.sha256
            or byte_length != self.byte_length
            or snapshot != self._snapshot
            or source_path != self.source_path
        ):
            raise EpubSourceError(
                "input_changed_during_export",
                "The verified source EPUB changed before publication.",
            )

    @contextmanager
    def open_verified(self) -> Iterator[BinaryIO]:
        """Yield the verified file handle and revalidate that same handle on exit.

        Consumers that parse source bytes must use this handle instead of
        reopening ``source_path``.  This binds parsing to the verified inode and
        prevents a transient path swap from mixing one file identity with
        another file's parsed content.
        """

        _root, source_path, descriptor, before_open = _open_source_reference(
            self._output_dir,
            self.relative_path,
            failure_code="input_changed_during_export",
        )
        try:
            with os.fdopen(descriptor, "rb") as handle:
                descriptor = -1
                before_digest, before_length = _stream_file_hash(
                    handle,
                    failure_code="input_changed_during_export",
                )
                before_parse = _FileSnapshot.from_stat(os.fstat(handle.fileno()))
                if (
                    source_path != self.source_path
                    or before_open != self._snapshot
                    or before_parse != self._snapshot
                    or before_digest != self.sha256
                    or before_length != self.byte_length
                ):
                    raise _input_changed_error()
                handle.seek(0)
                try:
                    yield handle
                finally:
                    try:
                        handle.seek(0)
                        after_digest, after_length = _stream_file_hash(
                            handle,
                            failure_code="input_changed_during_export",
                        )
                        after_parse = _FileSnapshot.from_stat(os.fstat(handle.fileno()))
                    except (OSError, ValueError):
                        raise _input_changed_error() from None
                    if (
                        after_parse != self._snapshot
                        or after_digest != self.sha256
                        or after_length != self.byte_length
                    ):
                        raise _input_changed_error()
                    (
                        _after_root,
                        after_path,
                        after_descriptor,
                        after_path_snapshot,
                    ) = _open_source_reference(
                        self._output_dir,
                        self.relative_path,
                        failure_code="input_changed_during_export",
                    )
                    try:
                        if (
                            after_path != self.source_path
                            or after_path_snapshot != self._snapshot
                        ):
                            raise _input_changed_error()
                    finally:
                        os.close(after_descriptor)
        except EpubSourceError:
            raise
        except OSError:
            raise _input_changed_error() from None
        finally:
            if descriptor >= 0:
                os.close(descriptor)


def _source_error(message: str) -> EpubSourceError:
    return EpubSourceError("source_asset_missing_or_not_epub", message)


def _input_changed_error() -> EpubSourceError:
    return EpubSourceError(
        "input_changed_during_export",
        "The source EPUB changed while it was being verified.",
    )


def _normalize_text(value: str | None) -> str:
    source = unicodedata.normalize("NFC", str(value or ""))
    normalized: list[str] = []
    in_white_space = False
    for character in source:
        if ord(character) in _UNICODE_WHITE_SPACE:
            if not in_white_space:
                normalized.append(" ")
            in_white_space = True
        else:
            normalized.append(character)
            in_white_space = False
    return "".join(normalized).strip(" ")


def _strip_frozen_white_space(value: str) -> str:
    start = 0
    end = len(value)
    while start < end and ord(value[start]) in _UNICODE_WHITE_SPACE:
        start += 1
    while end > start and ord(value[end - 1]) in _UNICODE_WHITE_SPACE:
        end -= 1
    return value[start:end]


def _has_unsafe_unicode_control(value: str) -> bool:
    return any(
        unicodedata.category(character) in {"Cc", "Cf", "Cs"}
        for character in value
    )


def _safe_opf_id(value: str | None) -> bool:
    return bool(
        value
        and len(value) <= 256
        and value not in {".", ".."}
        and not any(
            ord(character) in _UNICODE_WHITE_SPACE
            or character in "/\\?#\x00"
            or ord(character) < 0x20
            or ord(character) == 0x7F
            for character in value
        )
        and not _has_unsafe_unicode_control(value)
        and not _WINDOWS_DRIVE.match(value)
    )


def _safe_relative_reference(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != _strip_frozen_white_space(value)
    ):
        raise _source_error("Source asset reference must be a safe relative EPUB path.")
    if value != unicodedata.normalize("NFC", value):
        raise _source_error("Source asset reference must use canonical NFC Unicode.")
    if (
        "\x00" in value
        or any(unicodedata.category(character) == "Cc" for character in value)
        or "\\" in value
        or "?" in value
        or "#" in value
        or value.startswith("/")
        or _WINDOWS_DRIVE.match(value)
        or _urlsplit(value).scheme
    ):
        raise _source_error("Source asset reference must be a safe relative EPUB path.")
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise _source_error("Source asset reference must be a safe relative EPUB path.")
    parts = PurePosixPath(value).parts
    if not parts:
        raise _source_error("Source asset reference must be a safe relative EPUB path.")
    normalized = "/".join(parts)
    if not normalized.lower().endswith(".epub"):
        raise _source_error("Source asset must identify an EPUB file.")
    return normalized


def _manifest_source_reference(
    manifest: Mapping[str, Any] | None,
    explicit_reference: str | None,
) -> str:
    if explicit_reference is not None:
        return _safe_relative_reference(explicit_reference)
    if manifest is None:
        return DEFAULT_SOURCE_ASSET
    if not isinstance(manifest, Mapping):
        raise _source_error("Source asset declaration is malformed.")
    source_asset = manifest.get("source_asset")
    if source_asset is None:
        return DEFAULT_SOURCE_ASSET
    if not isinstance(source_asset, Mapping):
        raise _source_error("Source asset declaration is malformed.")
    reference = source_asset.get("file", DEFAULT_SOURCE_ASSET)
    return _safe_relative_reference(reference)


def _resolve_source_path(output_dir: Path, reference: str) -> tuple[Path, Path]:
    try:
        root = output_dir.resolve(strict=True)
    except (OSError, RuntimeError):
        raise _source_error("Book output directory is unavailable.") from None
    if not root.is_dir():
        raise _source_error("Book output directory is unavailable.")

    candidate = root.joinpath(*PurePosixPath(reference).parts)
    current = candidate
    while current != root:
        try:
            if current.is_symlink():
                raise _source_error(
                    "Source EPUB is missing or is not a non-symlink regular file."
                )
        except OSError:
            raise _source_error(
                "Source EPUB is missing or is not a non-symlink regular file."
            ) from None
        current = current.parent

    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        ) from None
    if not resolved.is_relative_to(root):
        raise _source_error("Source asset reference escapes the book output directory.")

    try:
        source_stat = candidate.stat(follow_symlinks=False)
    except OSError:
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        ) from None
    if not stat.S_ISREG(source_stat.st_mode):
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        )
    return root, resolved


def _snapshot_path(path: Path, *, failure_code: str) -> _FileSnapshot:
    try:
        value = path.stat(follow_symlinks=False)
    except OSError:
        if failure_code == "input_changed_during_export":
            raise _input_changed_error() from None
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        ) from None
    if not stat.S_ISREG(value.st_mode):
        if failure_code == "input_changed_during_export":
            raise _input_changed_error()
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        )
    return _FileSnapshot.from_stat(value)


def _stream_file_hash(
    handle: BinaryIO,
    *,
    failure_code: str = "source_asset_missing_or_not_epub",
) -> tuple[str, int]:
    digest = hashlib.sha256()
    byte_length = 0
    while chunk := handle.read(HASH_CHUNK_BYTES):
        byte_length += len(chunk)
        if byte_length > MAX_EPUB_BYTES:
            if failure_code == "input_changed_during_export":
                raise _input_changed_error()
            raise _source_error("Source EPUB exceeds the verification size limit.")
        digest.update(chunk)
    return digest.hexdigest(), byte_length


def _regular_file_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    return flags


def _open_contained_source_descriptor(
    root: Path,
    reference: str,
    *,
    failure_code: str,
) -> int:
    parts = PurePosixPath(reference).parts
    descriptor: int | None = None
    directory_descriptors: list[int] = []
    try:
        if os.open in os.supports_dir_fd and hasattr(os, "O_DIRECTORY"):
            directory_flags = os.O_RDONLY | os.O_DIRECTORY
            if hasattr(os, "O_CLOEXEC"):
                directory_flags |= os.O_CLOEXEC
            if hasattr(os, "O_NOFOLLOW"):
                directory_flags |= os.O_NOFOLLOW
            parent_descriptor = os.open(root, directory_flags)
            directory_descriptors.append(parent_descriptor)
            for component in parts[:-1]:
                parent_descriptor = os.open(
                    component,
                    directory_flags,
                    dir_fd=parent_descriptor,
                )
                directory_descriptors.append(parent_descriptor)
            descriptor = os.open(
                parts[-1],
                _regular_file_flags(),
                dir_fd=parent_descriptor,
            )
        else:
            descriptor = os.open(
                root.joinpath(*parts),
                _regular_file_flags(),
            )
        opened_snapshot = _FileSnapshot.from_stat(os.fstat(descriptor))
        if not stat.S_ISREG(opened_snapshot.mode):
            raise OSError("not a regular file")
        return descriptor
    except OSError:
        if descriptor is not None:
            os.close(descriptor)
        if failure_code == "input_changed_during_export":
            raise _input_changed_error() from None
        raise _source_error(
            "Source EPUB is missing or is not a non-symlink regular file."
        ) from None
    finally:
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def _open_source_reference(
    output_dir: Path,
    reference: str,
    *,
    failure_code: str,
) -> tuple[Path, Path, int, _FileSnapshot]:
    try:
        root, source_path = _resolve_source_path(output_dir, reference)
    except EpubSourceError:
        if failure_code == "input_changed_during_export":
            raise _input_changed_error() from None
        raise
    descriptor = _open_contained_source_descriptor(
        root,
        reference,
        failure_code=failure_code,
    )
    try:
        snapshot = _FileSnapshot.from_stat(os.fstat(descriptor))
        path_snapshot = _snapshot_path(source_path, failure_code=failure_code)
        if snapshot != path_snapshot:
            raise _input_changed_error()
        if snapshot.byte_length > MAX_EPUB_BYTES:
            if failure_code == "input_changed_during_export":
                raise _input_changed_error()
            raise _source_error("Source EPUB exceeds the verification size limit.")
    except EpubSourceError:
        os.close(descriptor)
        raise
    except OSError:
        os.close(descriptor)
        if failure_code == "input_changed_during_export":
            raise _input_changed_error() from None
        raise _source_error("Source EPUB could not be opened safely.") from None
    return root, source_path, descriptor, snapshot


def _fingerprint_source_reference(
    output_dir: Path,
    reference: str,
    *,
    failure_code: str = "source_asset_missing_or_not_epub",
) -> tuple[str, int, _FileSnapshot, Path]:
    _root, source_path, descriptor, before_open = _open_source_reference(
        output_dir,
        reference,
        failure_code=failure_code,
    )
    try:
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            digest, byte_length = _stream_file_hash(
                handle,
                failure_code="input_changed_during_export",
            )
        after_open = _FileSnapshot.from_stat(os.fstat(descriptor))
        try:
            _after_root, after_path = _resolve_source_path(output_dir, reference)
        except EpubSourceError:
            raise _input_changed_error() from None
        after_path_snapshot = _snapshot_path(
            after_path,
            failure_code="input_changed_during_export",
        )
    except EpubSourceError:
        raise
    except OSError:
        if failure_code == "input_changed_during_export":
            raise _input_changed_error() from None
        raise _source_error("Source EPUB could not be read safely.") from None
    finally:
        os.close(descriptor)

    if (
        before_open != after_open
        or after_open != after_path_snapshot
        or after_path != source_path
        or byte_length != after_open.byte_length
    ):
        raise _input_changed_error()
    return digest, byte_length, after_open, source_path


def _decode_href_segment(segment: str) -> str:
    if _INVALID_PERCENT_ESCAPE.search(segment):
        raise _source_error("OPF manifest contains an unsafe resource href.")
    try:
        decoded = unquote_to_bytes(segment).decode("utf-8", errors="strict")
    except (UnicodeDecodeError, ValueError):
        raise _source_error("OPF manifest contains an unsafe resource href.") from None
    if (
        not decoded
        or decoded in {".", ".."}
        or "/" in decoded
        or "\\" in decoded
        or "\x00" in decoded
        or any(unicodedata.category(character) == "Cc" for character in decoded)
    ):
        raise _source_error("OPF manifest contains an unsafe resource href.")
    normalized = unicodedata.normalize("NFC", decoded)
    if decoded != normalized:
        raise _source_error("EPUB href must use canonical NFC Unicode.")
    return normalized


def _normalize_archive_member_path(
    value: object,
    *,
    purpose: str,
    allow_reserved_filename_chars: bool = False,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != _strip_frozen_white_space(value)
    ):
        raise _source_error(f"{purpose} must be a safe relative archive path.")
    if value != unicodedata.normalize("NFC", value):
        raise _source_error(f"{purpose} must use canonical NFC Unicode.")
    if (
        "\x00" in value
        or any(unicodedata.category(character) == "Cc" for character in value)
        or "\\" in value
        or (not allow_reserved_filename_chars and ("?" in value or "#" in value))
        or value.startswith("/")
        or _WINDOWS_DRIVE.match(value)
        or (not allow_reserved_filename_chars and _urlsplit(value).scheme)
        or "//" in value
    ):
        raise _source_error(f"{purpose} must be a safe relative archive path.")
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise _source_error(f"{purpose} must be a safe relative archive path.")
    parts = PurePosixPath(value).parts
    if not parts:
        raise _source_error(f"{purpose} must be a safe relative archive path.")
    return "/".join(parts)


def _urlsplit(value: str) -> SplitResult:
    try:
        return urlsplit(value)
    except ValueError:
        raise _source_error("EPUB path or identifier syntax is invalid.") from None


def normalize_epub_href(href: str) -> str:
    """Canonicalize one package-local OPF-relative href for stable comparison.

    A fragment is a position within the same resource and is intentionally
    stripped.  Query, scheme, authority, absolute paths, backslashes, empty or
    dot segments, encoded separators, and encoded traversal remain invalid.
    UTF-8 percent escapes are decoded and then emitted with canonical escaping.
    """

    if not isinstance(href, str) or not href or href != _strip_frozen_white_space(href):
        raise _source_error("OPF manifest contains an unsafe resource href.")
    parsed = _urlsplit(href)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or href.startswith("/")
        or "\\" in href
        or "\x00" in href
        or any(unicodedata.category(character) == "Cc" for character in href)
        or "//" in parsed.path
        or _WINDOWS_DRIVE.match(parsed.path)
    ):
        raise _source_error("OPF manifest contains an unsafe resource href.")
    raw_parts = parsed.path.split("/")
    while raw_parts and raw_parts[0] == ".":
        raw_parts.pop(0)
    if not raw_parts:
        raise _source_error("OPF manifest contains an unsafe resource href.")
    decoded_parts = tuple(_decode_href_segment(part) for part in raw_parts)
    return "/".join(
        quote(
            part,
            safe="-._~!$&'()*+,;=@" if index == 0 else "-._~!$&'()*+,;=:@",
        )
        for index, part in enumerate(decoded_parts)
    )


def normalize_opf_relative_href(opf_path: str, href: str) -> ResolvedOpfHref:
    """Validate and resolve one local OPF href without path normalization tricks."""

    safe_opf_path = _normalize_archive_member_path(
        opf_path,
        purpose="OPF rootfile path",
    )
    if not isinstance(href, str) or "#" in href:
        raise _source_error("OPF manifest contains an unsafe resource href.")
    href_value = normalize_epub_href(href)
    decoded_parts = tuple(_decode_href_segment(part) for part in href_value.split("/"))
    base_parts = PurePosixPath(safe_opf_path).parent.parts
    archive_path = "/".join((*base_parts, *decoded_parts))
    archive_path = _normalize_archive_member_path(
        archive_path,
        purpose="Resolved OPF resource path",
        allow_reserved_filename_chars=True,
    )
    return ResolvedOpfHref(href=href_value, archive_path=archive_path)


def _zip_entry_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0xFFFF


def _validate_local_zip_header(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
) -> int:
    handle = archive.fp
    if handle is None or info.header_offset < 0:
        raise _source_error("Source EPUB archive has an invalid local file header.")
    try:
        handle.seek(info.header_offset)
        header = handle.read(_ZIP_LOCAL_HEADER.size)
        if len(header) != _ZIP_LOCAL_HEADER.size:
            raise _source_error(
                "Source EPUB archive has a truncated local file header."
            )
        (
            signature,
            _version_needed,
            local_flags,
            local_method,
            _modified_time,
            _modified_date,
            local_crc,
            local_compressed_size,
            local_file_size,
            filename_length,
            extra_length,
        ) = _ZIP_LOCAL_HEADER.unpack(header)
        if signature != _ZIP_LOCAL_SIGNATURE:
            raise _source_error("Source EPUB archive has an invalid local file header.")
        raw_filename = handle.read(filename_length)
        raw_extra = handle.read(extra_length)
    except EpubSourceError:
        raise
    except (OSError, struct.error):
        raise _source_error(
            "Source EPUB archive has an unreadable local file header."
        ) from None
    if len(raw_filename) != filename_length or len(raw_extra) != extra_length:
        raise _source_error("Source EPUB archive has a truncated local file header.")
    encoding = "utf-8" if local_flags & 0x800 else "cp437"
    try:
        local_filename = raw_filename.decode(encoding, errors="strict")
    except UnicodeDecodeError:
        raise _source_error(
            "Source EPUB archive has an invalid local entry name."
        ) from None
    if not local_flags & 0x800 and not local_filename.isascii():
        raise _source_error(
            "Source EPUB non-ASCII entry names must use UTF-8 ZIP encoding."
        )
    if (local_flags | info.flag_bits) & _ZIP_ENCRYPTION_FLAGS:
        raise _source_error("Source EPUB archive contains an encrypted entry.")
    if (
        local_flags != info.flag_bits
        or local_method != info.compress_type
        or local_filename != info.filename
    ):
        raise _source_error(
            "Source EPUB local and central directory metadata do not match."
        )
    uses_data_descriptor = bool(local_flags & 0x08)
    if uses_data_descriptor:
        if local_crc not in {0, info.CRC}:
            raise _source_error(
                "Source EPUB local and central directory metadata do not match."
            )
        if local_compressed_size not in {0, info.compress_size}:
            raise _source_error(
                "Source EPUB local and central directory metadata do not match."
            )
        if local_file_size not in {0, info.file_size}:
            raise _source_error(
                "Source EPUB local and central directory metadata do not match."
            )
    elif (
        local_crc != info.CRC
        or local_compressed_size != info.compress_size
        or local_file_size != info.file_size
    ):
        raise _source_error(
            "Source EPUB local and central directory metadata do not match."
        )
    return extra_length


def _validate_zip_entries(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = archive.infolist()
    if len(infos) > MAX_ZIP_ENTRIES:
        raise _source_error("Source EPUB archive exceeds the entry-count limit.")

    indexed: dict[str, zipfile.ZipInfo] = {}
    local_extra_lengths: dict[int, int] = {}
    total_size = 0
    for info in infos:
        local_extra_lengths[info.header_offset] = _validate_local_zip_header(
            archive,
            info,
        )
        name = _normalize_archive_member_path(
            info.filename.rstrip("/") if info.is_dir() else info.filename,
            purpose="EPUB ZIP entry",
            allow_reserved_filename_chars=True,
        )
        canonical_name = f"{name}/" if info.is_dir() else name
        if canonical_name != info.filename:
            raise _source_error(
                "Source EPUB archive contains a noncanonical entry name."
            )
        if canonical_name in indexed:
            raise _source_error("Source EPUB archive contains a duplicate entry name.")

        mode = _zip_entry_mode(info)
        if stat.S_ISLNK(mode):
            raise _source_error("Source EPUB archive contains a symbolic-link entry.")
        file_type = stat.S_IFMT(mode)
        if file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise _source_error("Source EPUB archive contains a special-file entry.")
        if file_type and info.is_dir() != (file_type == stat.S_IFDIR):
            raise _source_error(
                "Source EPUB archive entry name and file type do not agree."
            )
        if info.flag_bits & _ZIP_ENCRYPTION_FLAGS:
            raise _source_error("Source EPUB archive contains an encrypted entry.")
        if info.compress_type not in _ZIP_SUPPORTED_METHODS:
            raise _source_error(
                "Source EPUB archive contains an unsupported compression method."
            )
        if info.file_size > MAX_ZIP_ENTRY_BYTES:
            raise _source_error("Source EPUB archive contains an oversized entry.")
        total_size += info.file_size
        if total_size > MAX_ZIP_TOTAL_BYTES:
            raise _source_error("Source EPUB archive exceeds the expanded-size limit.")
        if info.file_size:
            if info.compress_size == 0:
                raise _source_error(
                    "Source EPUB archive contains an unsafe compression ratio."
                )
            ratio = info.file_size / info.compress_size
            if ratio > MAX_ZIP_COMPRESSION_RATIO:
                raise _source_error(
                    "Source EPUB archive contains an unsafe compression ratio."
                )
        indexed[canonical_name] = info

    if not infos or infos[0].filename != "mimetype":
        raise _source_error("Source EPUB must begin with a root mimetype entry.")
    mimetype_info = indexed.get("mimetype")
    if mimetype_info is None or mimetype_info.is_dir():
        raise _source_error("Source EPUB is missing its root mimetype entry.")
    if (
        mimetype_info.header_offset != 0
        or local_extra_lengths.get(mimetype_info.header_offset) != 0
    ):
        raise _source_error(
            "Source EPUB mimetype must be the first physical entry with no extra field."
        )
    if mimetype_info.compress_type != zipfile.ZIP_STORED:
        raise _source_error(
            "Source EPUB mimetype entry must be stored without compression."
        )
    try:
        mimetype = archive.read(mimetype_info)
    except (OSError, RuntimeError, zipfile.BadZipFile):
        raise _source_error("Source EPUB mimetype entry is unreadable.") from None
    if mimetype != EPUB_MEDIA_TYPE.encode("ascii"):
        raise _source_error("Source EPUB mimetype entry has invalid content.")

    try:
        broken_entry = archive.testzip()
    except (OSError, RuntimeError, zipfile.BadZipFile, zlib.error):
        raise _source_error(
            "Source EPUB archive contains an unreadable entry."
        ) from None
    if broken_entry is not None:
        raise _source_error("Source EPUB archive contains an unreadable entry.")
    return indexed


def _read_archive_member(
    archive: zipfile.ZipFile,
    entries: Mapping[str, zipfile.ZipInfo],
    name: str,
    *,
    purpose: str,
    limit: int,
) -> bytes:
    info = entries.get(name)
    if info is None or info.is_dir():
        raise _source_error(f"Source EPUB is missing {purpose}.")
    if info.file_size > limit:
        raise _source_error(f"Source EPUB {purpose} exceeds the parsing size limit.")
    try:
        return archive.read(info)
    except (OSError, RuntimeError, zipfile.BadZipFile):
        raise _source_error(f"Source EPUB {purpose} is unreadable.") from None


def _parse_safe_xml(content: bytes, *, purpose: str) -> ET.Element:
    if len(content) > MAX_XML_BYTES:
        raise _source_error(f"Source EPUB {purpose} exceeds the XML size limit.")
    if b"\x00" in content or _FORBIDDEN_XML_DECLARATION.search(content):
        raise _source_error(
            f"Source EPUB {purpose} contains a forbidden XML declaration."
        )
    try:
        return ET.fromstring(content)
    except ET.ParseError:
        raise _source_error(f"Source EPUB {purpose} is malformed XML.") from None


def _local_name(tag: object) -> str:
    value = str(tag)
    return value.rsplit("}", 1)[-1] if "}" in value else value.rsplit(":", 1)[-1]


def _expanded_name(tag: object) -> tuple[str | None, str]:
    value = str(tag)
    if value.startswith("{") and "}" in value:
        namespace, local_name = value[1:].split("}", 1)
        return namespace, local_name
    return None, _local_name(value)


def _namespace_children(
    element: ET.Element,
    namespace: str,
    local_name: str,
) -> tuple[ET.Element, ...]:
    return tuple(
        child
        for child in element
        if _expanded_name(child.tag) == (namespace, local_name)
    )


def _first_namespace_child(
    element: ET.Element,
    namespace: str,
    local_name: str,
) -> ET.Element | None:
    return next(iter(_namespace_children(element, namespace, local_name)), None)


def _dc_children(element: ET.Element, local_name: str) -> tuple[ET.Element, ...]:
    return _namespace_children(element, _DC_NAMESPACE, local_name)


def _attribute(
    element: ET.Element,
    local_name: str,
    *,
    allowed_namespaces: tuple[str | None, ...] = (None,),
) -> str | None:
    for key, value in element.attrib.items():
        namespace, attribute_name = _expanded_name(key)
        if attribute_name == local_name and namespace in allowed_namespaces:
            normalized = _strip_frozen_white_space(str(value))
            return normalized or None
    return None


def _container_rootfile(container_root: ET.Element) -> str:
    if _expanded_name(container_root.tag) != (_CONTAINER_NAMESPACE, "container"):
        raise _source_error("Source EPUB container root element is invalid.")
    rootfiles = _first_namespace_child(
        container_root,
        _CONTAINER_NAMESPACE,
        "rootfiles",
    )
    if rootfiles is None:
        raise _source_error("Source EPUB container has no rootfiles element.")
    candidates = _namespace_children(
        rootfiles,
        _CONTAINER_NAMESPACE,
        "rootfile",
    )
    if not candidates:
        raise _source_error("Source EPUB container does not declare an OPF rootfile.")
    preferred = tuple(
        element
        for element in candidates
        if (_attribute(element, "media-type") or "") == OPF_MEDIA_TYPE
    )
    if not preferred:
        raise _source_error(
            "Source EPUB container has no OPF rootfile with the required media type."
        )
    rootfile = preferred[0]
    return _normalize_archive_member_path(
        _attribute(rootfile, "full-path"),
        purpose="OPF rootfile path",
    )


def _identifier_declarations(metadata: ET.Element) -> dict[str, set[str]]:
    declarations: dict[str, set[str]] = {}
    for meta in _namespace_children(metadata, _OPF_NAMESPACE, "meta"):
        refines = _attribute(meta, "refines") or ""
        if not refines.startswith("#") or len(refines) == 1:
            continue
        property_name = (_attribute(meta, "property") or "").casefold()
        if property_name not in {"identifier-type", "scheme"}:
            continue
        value = _normalize_text(meta.text).casefold()
        if value and _SAFE_DECLARATION_TOKEN.fullmatch(value):
            declarations.setdefault(refines[1:], set()).add(value)
    return declarations


def _looks_like_isbn_declaration(values: set[str]) -> bool:
    return any(
        value in {"isbn", "isbn-10", "isbn-13", "02", "15"} or value.endswith(":isbn")
        for value in values
    )


def _declared_isbn_schemes(values: set[str], value: str) -> set[str]:
    normalized = _normalize_text(value)
    schemes: set[str] = set()
    if values.intersection({"isbn-10", "02"}) or re.match(
        r"^(?:urn:)?isbn-10(?::| +)",
        normalized,
        re.I,
    ):
        schemes.add("isbn-10")
    if values.intersection({"isbn-13", "15"}) or re.match(
        r"^(?:urn:)?isbn-13(?::| +)",
        normalized,
        re.I,
    ):
        schemes.add("isbn-13")
    return schemes


def _isbn_payload(value: str) -> str:
    normalized = _normalize_text(value)
    normalized = re.sub(
        r"^(?:urn:)?isbn(?:-1[03])?(?::| +)",
        "",
        normalized,
        flags=re.I,
    )
    return normalized.replace("-", "").replace(" ", "").upper()


def _looks_like_isbn_value(value: str) -> bool:
    payload = _isbn_payload(value)
    return bool(
        re.fullmatch(r"[0-9]{9}[0-9X]", payload)
        or re.fullmatch(r"97[89][0-9]{10}", payload)
    )


def _valid_isbn_10(value: str) -> bool:
    if re.fullmatch(r"[0-9]{9}[0-9X]", value) is None:
        return False
    digits = [10 if char == "X" else int(char) for char in value]
    return sum((10 - index) * digit for index, digit in enumerate(digits)) % 11 == 0


def _valid_isbn_13(value: str) -> bool:
    if re.fullmatch(r"97[89][0-9]{10}", value) is None:
        return False
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(value[:12])
    )
    return (10 - total % 10) % 10 == int(value[-1])


def classify_isbn(value: str) -> PublicationIdentifier | None:
    """Return a normalized ISBN with a valid check digit, otherwise ``None``."""

    normalized = _normalize_text(value)
    payload = _isbn_payload(normalized)
    declared_schemes = _declared_isbn_schemes(set(), normalized)
    if _valid_isbn_10(payload):
        identifier = PublicationIdentifier("isbn-10", payload)
        return (
            identifier
            if not declared_schemes or declared_schemes == {identifier.scheme}
            else None
        )
    if _valid_isbn_13(payload):
        identifier = PublicationIdentifier("isbn-13", payload)
        return (
            identifier
            if not declared_schemes or declared_schemes == {identifier.scheme}
            else None
        )
    return None


def _contains_local_path(value: str) -> bool:
    return bool(
        value.startswith(("/", "\\", "~/", "~\\"))
        or _WINDOWS_DRIVE.match(value)
        or _PRIVATE_PATH_FRAGMENT.search(value)
        or _ABSOLUTE_POSIX_FRAGMENT.search(value)
        or _ABSOLUTE_WINDOWS_FRAGMENT.search(value)
        or _HOME_PATH_FRAGMENT.search(value)
        or _LOCAL_ARTIFACT_PATH_FRAGMENT.search(value)
        or _RELATIVE_LOCAL_PATH_FRAGMENT.search(value)
        or _FILE_URI_FRAGMENT.search(value)
    )


def decode_public_scan_value(value: str) -> str | None:
    """Return bounded recursively percent-decoded NFC text for public gates."""

    current = value
    for _round in range(_MAX_PUBLIC_SCAN_DECODE_ROUNDS):
        try:
            decoded = unquote_to_bytes(current).decode("utf-8", errors="strict")
        except (UnicodeDecodeError, ValueError):
            return None
        if decoded != unicodedata.normalize("NFC", decoded):
            return None
        if decoded == current:
            return decoded
        current = decoded
    return None


def _public_http_host(parsed: SplitResult) -> bool:
    try:
        hostname = parsed.hostname
        _port = parsed.port
    except ValueError:
        return False
    if not hostname:
        return False
    normalized_host = hostname.rstrip(".").casefold()
    if (
        normalized_host == "localhost"
        or normalized_host.endswith(".localhost")
        or normalized_host.endswith(".local")
    ):
        return False
    try:
        address = ipaddress.ip_address(normalized_host)
    except ValueError:
        return _LEGACY_NUMERIC_HOST.fullmatch(normalized_host) is None
    return address.is_global and not address.is_multicast


def _absolute_publication_uri(value: str) -> str | None:
    if (
        "\x00" in value
        or "\\" in value
        or value != _strip_frozen_white_space(value)
        or any(
            ord(character) in _UNICODE_WHITE_SPACE
            or _has_unsafe_unicode_control(character)
            for character in value
        )
        or _contains_local_path(value)
        or _URI_CREDENTIALS.search(value)
    ):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if not parsed.scheme or _WINDOWS_DRIVE.match(value):
        return None
    scheme = parsed.scheme.casefold()
    if scheme not in _SAFE_PUBLICATION_URI_SCHEMES:
        return None
    if scheme == "urn":
        urn_match = _URN_URI.fullmatch(value.split("#", 1)[0])
        if (
            urn_match is None
            or urn_match.group("nid").casefold() == "urn"
            or not urn_match.group("nss")
        ):
            return None
    if scheme == "doi" and not parsed.path:
        return None
    if parsed.username or parsed.password:
        return None
    if scheme in {"http", "https"} and (
        not parsed.netloc or not _public_http_host(parsed)
    ):
        return None
    if _SECRET_PARAMETER.search(value):
        return None
    return value


def _identifier_is_public_safe(value: str) -> bool:
    if (
        not value
        or len(value) > _OPF_IDENTIFIER_MAX_LENGTH
        or value != unicodedata.normalize("NFC", value)
        or _INVALID_PERCENT_ESCAPE.search(value)
        or _has_unsafe_unicode_control(value)
    ):
        return False
    decoded = decode_public_scan_value(value)
    if decoded is None or _has_unsafe_unicode_control(decoded):
        return False
    try:
        parsed = urlsplit(decoded)
    except ValueError:
        return False
    scheme = parsed.scheme.casefold()
    if (
        _contains_local_path(decoded)
        or (scheme not in _SAFE_PUBLICATION_URI_SCHEMES and "/" in decoded)
        or scheme in {"data", "file", "javascript", "vbscript"}
        or parsed.username
        or parsed.password
        or _URI_CREDENTIALS.search(decoded)
        or _SECRET_PARAMETER.search(decoded)
        or (scheme in {"http", "https"} and _absolute_publication_uri(decoded) is None)
    ):
        return False
    return True


def is_public_display_metadata(value: object) -> bool:
    """Return whether one normalized display value is safe for public output."""

    if (
        not isinstance(value, str)
        or not value
        or value != unicodedata.normalize("NFC", value)
    ):
        return False
    decoded = decode_public_scan_value(value)
    if decoded is None:
        return False
    return bool(
        not _contains_local_path(decoded)
        and not _URI_CREDENTIALS.search(decoded)
        and not _SECRET_PARAMETER.search(decoded)
        and not _has_unsafe_unicode_control(decoded)
    )


def _append_invalid_identifier_warning(
    warnings: list[EpubSourceWarning],
    *,
    isbn: bool = False,
) -> None:
    warning = EpubSourceWarning(
        code="invalid_publication_identifier",
        message=(
            "An explicitly declared ISBN was excluded because its syntax, "
            "prefix, subtype, or check digit is invalid."
            if isbn
            else "An OPF identifier was excluded because it is not safe for public metadata."
        ),
    )
    if warning not in warnings:
        warnings.append(warning)


def _append_unsafe_display_metadata_warning(
    warnings: list[EpubSourceWarning],
    *,
    field_name: str,
) -> None:
    warning = EpubSourceWarning(
        code="unsafe_opf_display_metadata",
        message=(
            f"An OPF {field_name} value was excluded because it is not safe "
            "for public metadata."
        ),
    )
    if warning not in warnings:
        warnings.append(warning)


def _parse_metadata(package: ET.Element) -> EpubMetadata:
    metadata = _first_namespace_child(package, _OPF_NAMESPACE, "metadata")
    if metadata is None:
        raise _source_error("Source EPUB OPF is missing metadata.")

    warnings: list[EpubSourceWarning] = []
    normalized_titles = tuple(
        normalized
        for element in _dc_children(metadata, "title")
        if (normalized := _normalize_text(element.text))
    )
    titles = tuple(
        value for value in normalized_titles if is_public_display_metadata(value)
    )
    if not titles and normalized_titles:
        raise _source_error("Source EPUB OPF title is not safe for public metadata.")
    if not titles:
        raise _source_error("Source EPUB OPF is missing a usable title.")
    if len(titles) != len(normalized_titles):
        _append_unsafe_display_metadata_warning(warnings, field_name="title")

    normalized_creators = tuple(
        normalized
        for element in _dc_children(metadata, "creator")
        if (normalized := _normalize_text(element.text))
    )
    creators = tuple(
        dict.fromkeys(
            value for value in normalized_creators if is_public_display_metadata(value)
        )
    )
    if len(creators) != len(tuple(dict.fromkeys(normalized_creators))):
        _append_unsafe_display_metadata_warning(warnings, field_name="creator")

    normalized_languages = tuple(
        normalized
        for element in _dc_children(metadata, "language")
        if (normalized := _normalize_text(element.text))
    )
    languages = tuple(
        value for value in normalized_languages if is_public_display_metadata(value)
    )
    if len(languages) != len(normalized_languages):
        _append_unsafe_display_metadata_warning(warnings, field_name="language")

    unique_identifier_id = _attribute(package, "unique-identifier")
    if not _safe_opf_id(unique_identifier_id):
        raise _source_error("Source EPUB OPF unique identifier id is invalid.")
    declarations = _identifier_declarations(metadata)
    raw_identifiers: list[OpfIdentifier] = []
    publication_identifiers: list[PublicationIdentifier] = []
    unique_identifier: str | None = None
    unique_identifier_found = False

    seen_identifier_ids: set[str] = set()
    for element in _dc_children(metadata, "identifier"):
        value = _normalize_text(element.text)
        if not value:
            continue
        identifier_id = _attribute(element, "id")
        if identifier_id is not None and not _safe_opf_id(identifier_id):
            raise _source_error("Source EPUB OPF contains an invalid identifier id.")
        if identifier_id and identifier_id in seen_identifier_ids:
            raise _source_error("Source EPUB OPF contains a duplicate identifier id.")
        if identifier_id:
            seen_identifier_ids.add(identifier_id)
        declared_values = set(declarations.get(identifier_id or "", set()))
        attribute_scheme = _attribute(
            element,
            "scheme",
            allowed_namespaces=(None, _OPF_NAMESPACE),
        )
        if attribute_scheme:
            normalized_scheme = attribute_scheme.casefold()
            if _SAFE_DECLARATION_TOKEN.fullmatch(normalized_scheme):
                declared_values.add(normalized_scheme)
        is_unique = bool(unique_identifier_id and identifier_id == unique_identifier_id)
        if is_unique:
            unique_identifier_found = True

        lowered = value.casefold()
        explicit_isbn = (
            _looks_like_isbn_declaration(declared_values)
            or bool(re.match(r"^(?:urn:)?isbn(?:-1[03])?(?::| +)", lowered))
            or _looks_like_isbn_value(value)
        )
        isbn = classify_isbn(value)
        if explicit_isbn or isbn is not None:
            declared_isbn_schemes = _declared_isbn_schemes(
                declared_values,
                value,
            )
            if isbn is None or (
                declared_isbn_schemes != {isbn.scheme}
                if declared_isbn_schemes
                else False
            ):
                _append_invalid_identifier_warning(warnings, isbn=True)
                continue
            raw_identifiers.append(
                OpfIdentifier(
                    identifier_id=identifier_id,
                    value=value,
                    declared_scheme=(
                        sorted(declared_values)[0] if declared_values else None
                    ),
                    is_unique=is_unique,
                )
            )
            if is_unique:
                unique_identifier = value
            publication_identifiers.append(isbn)
            continue

        if not _identifier_is_public_safe(value):
            _append_invalid_identifier_warning(warnings)
            continue
        raw_identifiers.append(
            OpfIdentifier(
                identifier_id=identifier_id,
                value=value,
                declared_scheme=(
                    sorted(declared_values)[0] if declared_values else None
                ),
                is_unique=is_unique,
            )
        )

        if is_unique:
            unique_identifier = value
            publication_identifiers.append(
                PublicationIdentifier("opf-identifier", value)
            )
        else:
            uri = _absolute_publication_uri(value)
            if uri is not None:
                publication_identifiers.append(PublicationIdentifier("uri", uri))

    deduplicated = tuple(
        sorted(
            set(publication_identifiers),
            key=lambda identifier: (identifier.scheme, identifier.value),
        )
    )
    if not unique_identifier_id or not unique_identifier_found:
        raise _source_error(
            "Source EPUB OPF unique identifier reference is missing or unresolved."
        )
    return EpubMetadata(
        title=titles[0],
        creators=creators,
        language=languages[0] if languages else None,
        unique_identifier=unique_identifier,
        identifiers=tuple(raw_identifiers),
        publication_identifiers=deduplicated,
        warnings=tuple(warnings),
    )


def _parse_opf(
    opf_root: ET.Element,
    opf_path: str,
    entries: Mapping[str, zipfile.ZipInfo],
) -> tuple[EpubMetadata, tuple[EpubManifestItem, ...], tuple[str, ...]]:
    if _expanded_name(opf_root.tag) != (_OPF_NAMESPACE, "package"):
        raise _source_error("Source EPUB OPF root element is invalid.")
    metadata = _parse_metadata(opf_root)
    manifest = _first_namespace_child(opf_root, _OPF_NAMESPACE, "manifest")
    if manifest is None:
        raise _source_error("Source EPUB OPF is missing its manifest.")

    items: list[EpubManifestItem] = []
    item_ids: set[str] = set()
    item_hrefs: set[str] = set()
    item_archive_paths: set[str] = set()
    for element in _namespace_children(manifest, _OPF_NAMESPACE, "item"):
        item_id = _attribute(element, "id") or ""
        raw_href = _attribute(element, "href") or ""
        media_type = _attribute(element, "media-type") or ""
        if (
            not _safe_opf_id(item_id)
            or _MEDIA_TYPE.fullmatch(media_type) is None
            or len(media_type) > 127
        ):
            raise _source_error("Source EPUB OPF contains an incomplete manifest item.")
        if item_id in item_ids:
            raise _source_error(
                "Source EPUB OPF contains a duplicate manifest item id."
            )
        resolved = normalize_opf_relative_href(opf_path, raw_href)
        if resolved.href in item_hrefs or resolved.archive_path in item_archive_paths:
            raise _source_error("Source EPUB OPF contains a duplicate resource href.")
        info = entries.get(resolved.archive_path)
        if info is None or info.is_dir():
            raise _source_error("Source EPUB OPF references a missing local resource.")
        raw_properties = (_attribute(element, "properties") or "").split()
        if any(
            _SAFE_DECLARATION_TOKEN.fullmatch(property_name) is None
            for property_name in raw_properties
        ):
            raise _source_error("Source EPUB OPF contains invalid manifest properties.")
        properties = tuple(sorted(set(raw_properties)))
        items.append(
            EpubManifestItem(
                item_id=item_id,
                href=resolved.href,
                archive_path=resolved.archive_path,
                media_type=media_type,
                properties=properties,
            )
        )
        item_ids.add(item_id)
        item_hrefs.add(resolved.href)
        item_archive_paths.add(resolved.archive_path)

    if not items:
        raise _source_error("Source EPUB OPF manifest is empty.")
    spine = _first_namespace_child(opf_root, _OPF_NAMESPACE, "spine")
    if spine is None:
        raise _source_error("Source EPUB OPF is missing its spine.")
    spine_ids_list: list[str] = []
    for element in _namespace_children(spine, _OPF_NAMESPACE, "itemref"):
        item_id = _attribute(element, "idref") or ""
        if not _safe_opf_id(item_id):
            raise _source_error("Source EPUB spine contains an incomplete itemref.")
        spine_ids_list.append(item_id)
    spine_ids = tuple(spine_ids_list)
    if not spine_ids:
        raise _source_error("Source EPUB OPF spine is empty.")
    if any(item_id not in item_ids for item_id in spine_ids):
        raise _source_error("Source EPUB spine references an unknown manifest item.")
    return metadata, tuple(items), spine_ids


def verify_epub_source(
    output_dir: Path,
    manifest: Mapping[str, Any] | None = None,
    *,
    source_asset_file: str | None = None,
) -> VerifiedEpubSource:
    """Resolve and strictly verify one output directory's source EPUB."""

    reference = _manifest_source_reference(manifest, source_asset_file)
    root, source_path, descriptor, snapshot = _open_source_reference(
        Path(output_dir),
        reference,
        failure_code="source_asset_missing_or_not_epub",
    )
    try:
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            digest, byte_length = _stream_file_hash(
                handle,
                failure_code="input_changed_during_export",
            )
            after_hash_snapshot = _FileSnapshot.from_stat(os.fstat(handle.fileno()))
            if after_hash_snapshot != snapshot or byte_length != snapshot.byte_length:
                raise _input_changed_error()
            handle.seek(0)
            if handle.read(4) != b"PK\x03\x04":
                raise _source_error("Source asset does not have EPUB ZIP magic.")
            handle.seek(0)
            with zipfile.ZipFile(handle, mode="r") as archive:
                entries = _validate_zip_entries(archive)
                container_bytes = _read_archive_member(
                    archive,
                    entries,
                    _CONTAINER_PATH,
                    purpose="META-INF/container.xml",
                    limit=MAX_XML_BYTES,
                )
                container_root = _parse_safe_xml(
                    container_bytes,
                    purpose="container document",
                )
                opf_path = _container_rootfile(container_root)
                opf_bytes = _read_archive_member(
                    archive,
                    entries,
                    opf_path,
                    purpose="OPF package document",
                    limit=MAX_XML_BYTES,
                )
                opf_root = _parse_safe_xml(opf_bytes, purpose="OPF package document")
                metadata, items, spine_ids = _parse_opf(
                    opf_root,
                    opf_path,
                    entries,
                )
                archive_entries = tuple(entries)
            after_archive_snapshot = _FileSnapshot.from_stat(os.fstat(handle.fileno()))
            if after_archive_snapshot != snapshot:
                raise _input_changed_error()
            handle.seek(0)
            confirmed_digest, confirmed_length = _stream_file_hash(
                handle,
                failure_code="input_changed_during_export",
            )
            final_snapshot = _FileSnapshot.from_stat(os.fstat(handle.fileno()))
            if (
                final_snapshot != snapshot
                or confirmed_digest != digest
                or confirmed_length != byte_length
            ):
                raise _input_changed_error()
    except EpubSourceError:
        raise
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile):
        raise _source_error(
            "Source asset is not a readable EPUB ZIP archive."
        ) from None
    finally:
        os.close(descriptor)

    try:
        after_root, after_path = _resolve_source_path(root, reference)
    except EpubSourceError:
        raise _input_changed_error() from None
    after_archive = _snapshot_path(
        after_path, failure_code="input_changed_during_export"
    )
    if after_root != root or after_path != source_path or after_archive != snapshot:
        raise _input_changed_error()
    return VerifiedEpubSource(
        source_path=source_path,
        _output_dir=root,
        relative_path=reference,
        sha256=digest,
        byte_length=byte_length,
        opf_path=opf_path,
        metadata=metadata,
        manifest_items=items,
        spine_item_ids=spine_ids,
        archive_entries=archive_entries,
        _snapshot=snapshot,
    )


__all__ = [
    "DEFAULT_SOURCE_ASSET",
    "EPUB_MEDIA_TYPE",
    "EpubManifestItem",
    "EpubMetadata",
    "EpubSourceError",
    "EpubSourceWarning",
    "HASH_CHUNK_BYTES",
    "MAX_EPUB_BYTES",
    "MAX_XML_BYTES",
    "MAX_ZIP_COMPRESSION_RATIO",
    "MAX_ZIP_ENTRIES",
    "MAX_ZIP_ENTRY_BYTES",
    "MAX_ZIP_TOTAL_BYTES",
    "OpfIdentifier",
    "PublicationIdentifier",
    "ResolvedOpfHref",
    "VerifiedEpubSource",
    "classify_isbn",
    "decode_public_scan_value",
    "is_public_display_metadata",
    "normalize_epub_href",
    "normalize_opf_relative_href",
    "verify_epub_source",
]
