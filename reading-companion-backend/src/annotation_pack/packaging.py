"""Deterministic and fail-closed detached Annotation Pack packaging.

The v0 detached form is deliberately tiny: one DEFLATED root entry named
``annotations.json``.  This module never extracts archive content to disk and
does not know about any producer, reading mechanism, EPUB, or runtime state.

The byte-oriented builder is the primary publication API.  Exporters can feed
its result into their own pinned-dirfd immutable writer.  A conservative
``Path`` wrapper is retained for standalone callers and only creates a new
file; it never replaces an existing destination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
from typing import NoReturn
import zipfile
import zlib

from src.annotation_pack.serialization import CanonicalJsonError, canonical_json_bytes
from src.annotation_pack.validation import (
    ValidationContext,
    ValidationResult,
    validate_pack,
)


ANNOTATIONS_ENTRY_NAME = "annotations.json"
DETACHED_ANNOTATIONS_MEDIA_TYPE = (
    'application/zip;profile="https://www.w3.org/TR/epub-anno-10/"'
)
MAX_PACKAGE_BYTES = 8 * 1024 * 1024
MAX_DETACHED_PACKAGE_BYTES = MAX_PACKAGE_BYTES
MAX_ANNOTATIONS_ENTRY_BYTES = 16 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
PACKAGE_COMPRESSION_LEVEL = 9
PACKAGE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

_READ_CHUNK_BYTES = 64 * 1024
_ZIP_LOCAL_SIGNATURE = 0x04034B50
_ZIP_CENTRAL_SIGNATURE = 0x02014B50
_ZIP_EOCD_SIGNATURE = 0x06054B50
_ZIP_VERSION = 20
_ZIP_CREATE_SYSTEM = 3
_ZIP_VERSION_MADE_BY = (_ZIP_CREATE_SYSTEM << 8) | _ZIP_VERSION
_ZIP_FLAGS = 0
_ZIP_METHOD = zipfile.ZIP_DEFLATED
_ZIP_DOS_TIME = 0
_ZIP_DOS_DATE = 33
_ZIP_EXTERNAL_ATTR = (stat.S_IFREG | 0o644) << 16
_ZIP_INTERNAL_ATTR = 0
_ZIP64_U16 = 0xFFFF
_ZIP64_U32 = 0xFFFFFFFF
_ENTRY_NAME_BYTES = ANNOTATIONS_ENTRY_NAME.encode("ascii")

_LOCAL_HEADER = struct.Struct("<IHHHHHIIIHH")
_CENTRAL_HEADER = struct.Struct("<IHHHHHHIIIHHHHHII")
_EOCD = struct.Struct("<IHHHHIIH")

_PUBLIC_ERROR_MESSAGE = "The detached Annotation Pack is invalid."


__all__ = [
    "ANNOTATIONS_ENTRY_NAME",
    "DETACHED_ANNOTATIONS_MEDIA_TYPE",
    "MAX_ANNOTATIONS_ENTRY_BYTES",
    "MAX_COMPRESSION_RATIO",
    "MAX_DETACHED_PACKAGE_BYTES",
    "MAX_PACKAGE_BYTES",
    "PACKAGE_COMPRESSION_LEVEL",
    "PACKAGE_TIMESTAMP",
    "PackageError",
    "PackageResult",
    "ValidatedPackage",
    "build_detached_annotations",
    "package_detached_annotations",
    "read_detached_annotations",
    "validate_detached_annotations",
]


class PackageError(ValueError):
    """Sanitized package failure with the stable v0 catalog code."""

    code = "package_entry_invalid"

    def __init__(self) -> None:
        super().__init__(_PUBLIC_ERROR_MESSAGE)


@dataclass(frozen=True, slots=True)
class PackageResult:
    """Deterministic package bytes ready for an immutable publication writer."""

    package_bytes: bytes = field(repr=False)
    sha256: str
    byte_length: int
    annotations_json_sha256: str


@dataclass(frozen=True, slots=True)
class ValidatedPackage:
    """Independently validated package and its canonical JSON payload."""

    package_bytes: bytes = field(repr=False)
    package_sha256: str
    byte_length: int
    annotations_json: bytes = field(repr=False)
    annotations_json_sha256: str
    document: dict[str, object] = field(repr=False)
    validation: ValidationResult


@dataclass(frozen=True, slots=True)
class _Envelope:
    crc32: int
    compressed_size: int
    uncompressed_size: int
    compressed_offset: int
    central_offset: int


@dataclass(frozen=True, slots=True)
class _CreatedFile:
    parent_descriptor: int
    leaf: str
    device: int
    inode: int


def build_detached_annotations(annotations_json: bytes) -> PackageResult:
    """Return the reproducible detached package for canonical Pack JSON bytes.

    Input JSON is independently strict-parsed and semantically validated before
    writing.  The completed ZIP is then reopened through the same public
    package validator, including classic-ZIP topology, bounded raw-DEFLATE,
    CRC, canonical JSON, schema, and semantic checks.  Given the same JSON
    bytes, this function returns the same ZIP bytes.
    """

    canonical, _document, _validation = _validate_annotations_json(annotations_json)
    package_bytes = _build_package_bytes(canonical)
    validated = validate_detached_annotations(
        package_bytes,
        expected_annotations_json=canonical,
    )
    return PackageResult(
        package_bytes=validated.package_bytes,
        sha256=validated.package_sha256,
        byte_length=validated.byte_length,
        annotations_json_sha256=validated.annotations_json_sha256,
    )


def package_detached_annotations(
    annotations_json: bytes,
    destination: Path,
    *,
    reproducible: bool = True,
) -> PackageResult:
    """Create one new ``.annotations`` file without replacing any path.

    Publication code should normally use :func:`build_detached_annotations`
    and its own already-pinned revision writer.  This standalone wrapper keeps
    the design-level ``Path`` API safe: every existing parent component is
    opened without following symlinks and the leaf uses ``O_EXCL``.
    """

    if reproducible is not True:
        _fail()
    if not isinstance(destination, Path):
        _fail()
    if destination.suffix != ".annotations":
        _fail()

    result = build_detached_annotations(annotations_json)
    created = _write_new_file_nofollow(destination, result.package_bytes)
    try:
        validated = validate_detached_annotations(
            destination,
            expected_annotations_json=annotations_json,
        )
        if (
            validated.package_sha256 != result.sha256
            or validated.byte_length != result.byte_length
        ):
            _fail()
        return result
    except BaseException:
        _conditional_cleanup_created(created)
        raise
    finally:
        _close_descriptor(created.parent_descriptor)


def validate_detached_annotations(
    source: bytes | Path,
    *,
    expected_annotations_json: bytes | None = None,
) -> ValidatedPackage:
    """Validate one detached package without extracting content to disk."""

    try:
        package_bytes = _snapshot_package_source(source)
        if expected_annotations_json is not None:
            if type(expected_annotations_json) is not bytes:
                _fail()
            if len(expected_annotations_json) > MAX_ANNOTATIONS_ENTRY_BYTES:
                _fail()

        envelope = _validate_raw_envelope(package_bytes)
        annotations_json = _read_zip_entry(package_bytes, envelope=envelope)
        canonical, document, validation = _validate_annotations_json(annotations_json)
        if canonical != annotations_json:
            _fail()
        if (
            expected_annotations_json is not None
            and annotations_json != expected_annotations_json
        ):
            _fail()

        return ValidatedPackage(
            package_bytes=package_bytes,
            package_sha256=hashlib.sha256(package_bytes).hexdigest(),
            byte_length=len(package_bytes),
            annotations_json=annotations_json,
            annotations_json_sha256=hashlib.sha256(annotations_json).hexdigest(),
            # This is already a detached strict-JSON snapshot.  Keeping its
            # arrays as real lists lets callers hand it directly to the
            # canonical jsonschema validator (which does not classify tuples
            # as JSON arrays).  Mutating it cannot change the validated bytes,
            # digests, or ValidationResult stored beside it.
            document=document,
            validation=validation,
        )
    except PackageError:
        raise
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None


def read_detached_annotations(source: bytes | Path) -> bytes:
    """Return exact canonical entry bytes after complete package validation."""

    return validate_detached_annotations(source).annotations_json


def _build_package_bytes(annotations_json: bytes) -> bytes:
    if type(annotations_json) is not bytes:
        _fail()
    buffer = BytesIO()
    try:
        with zipfile.ZipFile(
            buffer,
            mode="w",
            compression=_ZIP_METHOD,
            compresslevel=PACKAGE_COMPRESSION_LEVEL,
            allowZip64=False,
            strict_timestamps=True,
        ) as archive:
            archive.comment = b""
            info = zipfile.ZipInfo(ANNOTATIONS_ENTRY_NAME, date_time=PACKAGE_TIMESTAMP)
            info.create_system = _ZIP_CREATE_SYSTEM
            info.create_version = _ZIP_VERSION
            info.extract_version = _ZIP_VERSION
            info.flag_bits = _ZIP_FLAGS
            info.compress_type = _ZIP_METHOD
            info.internal_attr = _ZIP_INTERNAL_ATTR
            info.external_attr = _ZIP_EXTERNAL_ATTR
            info.extra = b""
            info.comment = b""
            archive.writestr(
                info,
                annotations_json,
                compress_type=_ZIP_METHOD,
                compresslevel=PACKAGE_COMPRESSION_LEVEL,
            )
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None
    package_bytes = buffer.getvalue()
    if len(package_bytes) > MAX_PACKAGE_BYTES:
        _fail()
    return package_bytes


def _validate_raw_envelope(package_bytes: bytes) -> _Envelope:
    if type(package_bytes) is not bytes:
        _fail()
    size = len(package_bytes)
    if size > MAX_PACKAGE_BYTES or size < _LOCAL_HEADER.size + _EOCD.size:
        _fail()

    eocd_offset = size - _EOCD.size
    try:
        (
            eocd_signature,
            disk_number,
            central_disk,
            disk_entries,
            total_entries,
            central_size,
            central_offset,
            comment_length,
        ) = _EOCD.unpack_from(package_bytes, eocd_offset)
    except struct.error:
        _fail()
    if (
        eocd_signature != _ZIP_EOCD_SIGNATURE
        or disk_number != 0
        or central_disk != 0
        or disk_entries != 1
        or total_entries != 1
        or comment_length != 0
        or disk_entries == _ZIP64_U16
        or total_entries == _ZIP64_U16
        or central_size == _ZIP64_U32
        or central_offset == _ZIP64_U32
        or central_offset + central_size != eocd_offset
    ):
        _fail()
    if central_offset < _LOCAL_HEADER.size or central_size < _CENTRAL_HEADER.size:
        _fail()

    try:
        (
            central_signature,
            version_made_by,
            version_needed,
            flags,
            method,
            modified_time,
            modified_date,
            crc32,
            compressed_size,
            uncompressed_size,
            name_length,
            extra_length,
            entry_comment_length,
            entry_disk,
            internal_attr,
            external_attr,
            local_offset,
        ) = _CENTRAL_HEADER.unpack_from(package_bytes, central_offset)
    except struct.error:
        _fail()
    central_end = (
        central_offset
        + _CENTRAL_HEADER.size
        + name_length
        + extra_length
        + entry_comment_length
    )
    name_start = central_offset + _CENTRAL_HEADER.size
    name_end = name_start + name_length
    if (
        central_signature != _ZIP_CENTRAL_SIGNATURE
        or version_made_by != _ZIP_VERSION_MADE_BY
        or version_needed != _ZIP_VERSION
        or flags != _ZIP_FLAGS
        or method != _ZIP_METHOD
        or modified_time != _ZIP_DOS_TIME
        or modified_date != _ZIP_DOS_DATE
        or name_length != len(_ENTRY_NAME_BYTES)
        or extra_length != 0
        or entry_comment_length != 0
        or entry_disk != 0
        or internal_attr != _ZIP_INTERNAL_ATTR
        or external_attr != _ZIP_EXTERNAL_ATTR
        or local_offset != 0
        or compressed_size in {_ZIP64_U32, 0}
        or uncompressed_size in {_ZIP64_U32, 0}
        or uncompressed_size > MAX_ANNOTATIONS_ENTRY_BYTES
        or central_end != central_offset + central_size
        or package_bytes[name_start:name_end] != _ENTRY_NAME_BYTES
    ):
        _fail()
    if uncompressed_size > compressed_size * MAX_COMPRESSION_RATIO:
        _fail()

    try:
        (
            local_signature,
            local_version_needed,
            local_flags,
            local_method,
            local_modified_time,
            local_modified_date,
            local_crc32,
            local_compressed_size,
            local_uncompressed_size,
            local_name_length,
            local_extra_length,
        ) = _LOCAL_HEADER.unpack_from(package_bytes, 0)
    except struct.error:
        _fail()
    local_name_start = _LOCAL_HEADER.size
    local_name_end = local_name_start + local_name_length
    compressed_offset = local_name_end + local_extra_length
    compressed_data_end = compressed_offset + compressed_size
    if (
        local_signature != _ZIP_LOCAL_SIGNATURE
        or local_version_needed != version_needed
        or local_flags != flags
        or local_method != method
        or local_modified_time != modified_time
        or local_modified_date != modified_date
        or local_crc32 != crc32
        or local_compressed_size != compressed_size
        or local_uncompressed_size != uncompressed_size
        or local_name_length != name_length
        or local_extra_length != 0
        or package_bytes[local_name_start:local_name_end] != _ENTRY_NAME_BYTES
        or compressed_data_end != central_offset
    ):
        _fail()

    return _Envelope(
        crc32=crc32,
        compressed_size=compressed_size,
        uncompressed_size=uncompressed_size,
        compressed_offset=compressed_offset,
        central_offset=central_offset,
    )


def _read_zip_entry(package_bytes: bytes, *, envelope: _Envelope) -> bytes:
    annotations_json = _inflate_entry(package_bytes, envelope=envelope)
    try:
        with zipfile.ZipFile(BytesIO(package_bytes), mode="r", allowZip64=False) as archive:
            infos = archive.infolist()
            if len(infos) != 1 or archive.comment != b"":
                _fail()
            info = infos[0]
            if (
                info.filename != ANNOTATIONS_ENTRY_NAME
                or info.orig_filename != ANNOTATIONS_ENTRY_NAME
                or info.header_offset != 0
                or info.create_system != _ZIP_CREATE_SYSTEM
                or info.create_version != _ZIP_VERSION
                or info.extract_version != _ZIP_VERSION
                or info.flag_bits != _ZIP_FLAGS
                or info.compress_type != _ZIP_METHOD
                or info.date_time != PACKAGE_TIMESTAMP
                or info.CRC != envelope.crc32
                or info.compress_size != envelope.compressed_size
                or info.file_size != envelope.uncompressed_size
                or info.internal_attr != _ZIP_INTERNAL_ATTR
                or info.external_attr != _ZIP_EXTERNAL_ATTR
                or info.extra != b""
                or info.comment != b""
                or info.volume != 0
                or info.is_dir()
                or archive.start_dir != envelope.central_offset
            ):
                _fail()

            with archive.open(info, mode="r") as entry:
                zipfile_bytes = _read_bounded_stream(
                    entry,
                    maximum_bytes=MAX_ANNOTATIONS_ENTRY_BYTES,
                )
            if zipfile_bytes != annotations_json:
                _fail()
            return annotations_json
    except PackageError:
        raise
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None


def _inflate_entry(package_bytes: bytes, *, envelope: _Envelope) -> bytes:
    compressed = package_bytes[
        envelope.compressed_offset : envelope.compressed_offset
        + envelope.compressed_size
    ]
    if len(compressed) != envelope.compressed_size:
        _fail()
    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
    chunks: list[bytes] = []
    total = 0
    try:
        for offset in range(0, len(compressed), _READ_CHUNK_BYTES):
            pending = compressed[offset : offset + _READ_CHUNK_BYTES]
            while pending:
                remaining = MAX_ANNOTATIONS_ENTRY_BYTES + 1 - total
                if remaining <= 0:
                    _fail()
                chunk = decompressor.decompress(pending, remaining)
                total += len(chunk)
                if total > MAX_ANNOTATIONS_ENTRY_BYTES:
                    _fail()
                chunks.append(chunk)
                if decompressor.unused_data:
                    _fail()
                next_pending = decompressor.unconsumed_tail
                if next_pending == pending and not chunk:
                    _fail()
                pending = next_pending
        remaining = MAX_ANNOTATIONS_ENTRY_BYTES + 1 - total
        if remaining <= 0:
            _fail()
        tail = decompressor.flush(remaining)
        total += len(tail)
        if total > MAX_ANNOTATIONS_ENTRY_BYTES:
            _fail()
        chunks.append(tail)
    except PackageError:
        raise
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None
    if (
        not decompressor.eof
        or decompressor.unused_data
        or decompressor.unconsumed_tail
        or total != envelope.uncompressed_size
    ):
        _fail()
    annotations_json = b"".join(chunks)
    if (zlib.crc32(annotations_json) & 0xFFFFFFFF) != envelope.crc32:
        _fail()
    return annotations_json


def _read_bounded_stream(stream: object, *, maximum_bytes: int) -> bytes:
    reader = getattr(stream, "read", None)
    if not callable(reader):
        _fail()
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = reader(_READ_CHUNK_BYTES)
        if type(chunk) is not bytes:
            _fail()
        if not chunk:
            break
        total += len(chunk)
        if total > maximum_bytes:
            _fail()
        chunks.append(chunk)
    return b"".join(chunks)


def _validate_annotations_json(
    annotations_json: bytes,
) -> tuple[bytes, dict[str, object], ValidationResult]:
    if type(annotations_json) is not bytes:
        _fail()
    if not annotations_json or len(annotations_json) > MAX_ANNOTATIONS_ENTRY_BYTES:
        _fail()
    if annotations_json.startswith(b"\xef\xbb\xbf"):
        _fail()
    try:
        text = annotations_json.decode("utf-8", errors="strict")
        document = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None
    if not isinstance(document, dict):
        _fail()
    try:
        canonical = canonical_json_bytes(document)
    except CanonicalJsonError:
        raise PackageError() from None
    if canonical != annotations_json:
        _fail()
    try:
        validation = validate_pack(
            document,
            context=ValidationContext(allow_empty=True),
        )
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None
    if not validation.publishable:
        _fail()
    return canonical, document, validation


def _snapshot_package_source(source: bytes | Path) -> bytes:
    if type(source) is bytes:
        if len(source) > MAX_PACKAGE_BYTES:
            _fail()
        return source
    if not isinstance(source, Path):
        _fail()
    return _read_regular_path_nofollow(source, maximum_bytes=MAX_PACKAGE_BYTES)


def _read_regular_path_nofollow(path: Path, *, maximum_bytes: int) -> bytes:
    descriptor, parent_descriptor, leaf = _open_regular_nofollow(path)
    try:
        before = os.fstat(descriptor)
        before_path = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        before_identity = _stat_identity(before)
        if (
            not stat.S_ISREG(before.st_mode)
            or _stat_identity(before_path) != before_identity
            or before.st_size > maximum_bytes
        ):
            _fail()
        content = _read_descriptor(descriptor, maximum_bytes=maximum_bytes)
        after = os.fstat(descriptor)
        after_path = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        reopened, reopened_parent, _ = _open_regular_nofollow(path)
        try:
            reopened_stat = os.fstat(reopened)
        finally:
            _close_descriptor(reopened)
            _close_descriptor(reopened_parent)
        if (
            before_identity != _stat_identity(after)
            or before_identity != _stat_identity(after_path)
            or before_identity != _stat_identity(reopened_stat)
            or len(content) != before.st_size
        ):
            _fail()
        return content
    except PackageError:
        raise
    except (MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        raise PackageError() from None
    finally:
        _close_descriptor(descriptor)
        _close_descriptor(parent_descriptor)


def _write_new_file_nofollow(path: Path, content: bytes) -> _CreatedFile:
    if not isinstance(path, Path) or type(content) is not bytes:
        _fail()
    parent_descriptor, leaf = _open_parent_nofollow(path)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        _close_descriptor(parent_descriptor)
        _fail()
    descriptor = -1
    created: _CreatedFile | None = None
    keep_parent = False
    try:
        descriptor = os.open(
            leaf,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | os.O_CLOEXEC
            | os.O_NONBLOCK
            | nofollow,
            0o644,
            dir_fd=parent_descriptor,
        )
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            _fail()
        created = _CreatedFile(
            parent_descriptor=parent_descriptor,
            leaf=leaf,
            device=opened_stat.st_dev,
            inode=opened_stat.st_ino,
        )
        view = memoryview(content)
        total = 0
        while total < len(content):
            try:
                written = os.write(descriptor, view[total:])
            except InterruptedError:
                continue
            if written <= 0:
                _fail()
            total += written
        os.fsync(descriptor)
        written_stat = os.fstat(descriptor)
        path_stat = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        if (
            not stat.S_ISREG(written_stat.st_mode)
            or _stat_identity(written_stat) != _stat_identity(path_stat)
            or written_stat.st_size != len(content)
        ):
            _fail()
        os.fsync(parent_descriptor)
        keep_parent = True
        return created
    except BaseException as exc:
        if created is not None:
            _conditional_cleanup_created(created)
        if isinstance(exc, PackageError):
            raise
        if isinstance(exc, (MemoryError, KeyboardInterrupt, SystemExit)):
            raise
        raise PackageError() from None
    finally:
        if descriptor >= 0:
            _close_descriptor(descriptor)
        if not keep_parent:
            _close_descriptor(parent_descriptor)


def _conditional_cleanup_created(created: _CreatedFile) -> bool:
    """Remove only the exact leaf created by the standalone writer.

    The parent descriptor remains pinned across post-write path validation.
    A pathname replacement therefore fails the device/inode comparison and is
    never unlinked or overwritten by cleanup.
    """

    try:
        current = os.stat(
            created.leaf,
            dir_fd=created.parent_descriptor,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino) != (created.device, created.inode)
        ):
            return False
        # Recheck immediately before unlink so ordinary replacement races fail
        # closed.  POSIX has no portable unlink-by-fd primitive; the exact
        # identity check plus pinned parent is the narrow portable boundary.
        current = os.stat(
            created.leaf,
            dir_fd=created.parent_descriptor,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino) != (created.device, created.inode)
        ):
            return False
        os.unlink(created.leaf, dir_fd=created.parent_descriptor)
        try:
            os.fsync(created.parent_descriptor)
        except OSError:
            pass
        return True
    except (OSError, TypeError, ValueError):
        return False


def _open_regular_nofollow(path: Path) -> tuple[int, int, str]:
    parent_descriptor, leaf = _open_parent_nofollow(path)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        _close_descriptor(parent_descriptor)
        _fail()
    try:
        descriptor = os.open(
            leaf,
            os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow,
            dir_fd=parent_descriptor,
        )
    except BaseException:
        _close_descriptor(parent_descriptor)
        raise PackageError() from None
    return descriptor, parent_descriptor, leaf


def _open_parent_nofollow(path: Path) -> tuple[int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None or not isinstance(path, Path):
        _fail()
    if ".." in path.parts or "\x00" in os.fspath(path):
        _fail()
    try:
        absolute = os.path.abspath(os.fspath(path))
    except (OSError, TypeError, ValueError):
        raise PackageError() from None
    components = tuple(part for part in absolute.split(os.sep) if part)
    if not components or any(part in {".", ".."} for part in components):
        _fail()
    directory_flags = (
        os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory
    )
    try:
        current = os.open(os.sep, directory_flags)
    except BaseException:
        raise PackageError() from None
    try:
        for component in components[:-1]:
            child = os.open(component, directory_flags, dir_fd=current)
            _close_descriptor(current)
            current = child
        return current, components[-1]
    except BaseException:
        _close_descriptor(current)
        raise PackageError() from None


def _read_descriptor(descriptor: int, *, maximum_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        try:
            chunk = os.read(descriptor, _READ_CHUNK_BYTES)
        except InterruptedError:
            continue
        if not chunk:
            break
        total += len(chunk)
        if total > maximum_bytes:
            _fail()
        chunks.append(chunk)
    return b"".join(chunks)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail()
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> NoReturn:
    _fail()


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _close_descriptor(descriptor: int) -> None:
    try:
        os.close(descriptor)
    except OSError:
        pass


def _fail() -> NoReturn:
    raise PackageError()
