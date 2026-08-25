from __future__ import annotations

from io import BytesIO
import json
import os
from pathlib import Path
import stat
import struct
import zipfile

import pytest

from src.annotation_pack.packaging import (
    ANNOTATIONS_ENTRY_NAME,
    DETACHED_ANNOTATIONS_MEDIA_TYPE,
    MAX_ANNOTATIONS_ENTRY_BYTES,
    MAX_DETACHED_PACKAGE_BYTES,
    MAX_PACKAGE_BYTES,
    PACKAGE_COMPRESSION_LEVEL,
    PACKAGE_TIMESTAMP,
    PackageError,
    build_detached_annotations,
    package_detached_annotations,
    read_detached_annotations,
    validate_detached_annotations,
)
import src.annotation_pack.packaging as packaging_module
from src.annotation_pack.schema import pack_validator
from src.annotation_pack.serialization import canonical_json_bytes


_REGULAR_ATTR = (stat.S_IFREG | 0o644) << 16
_LOCAL_FLAGS_OFFSET = 6
_LOCAL_METHOD_OFFSET = 8
_LOCAL_CRC_OFFSET = 14
_LOCAL_COMPRESSED_SIZE_OFFSET = 18
_LOCAL_UNCOMPRESSED_SIZE_OFFSET = 22
_LOCAL_NAME_OFFSET = 30
_CENTRAL_FLAGS_OFFSET = 8
_CENTRAL_METHOD_OFFSET = 10
_CENTRAL_MODIFIED_TIME_OFFSET = 12
_CENTRAL_CRC_OFFSET = 16
_CENTRAL_COMPRESSED_SIZE_OFFSET = 20
_CENTRAL_UNCOMPRESSED_SIZE_OFFSET = 24
_CENTRAL_EXTERNAL_ATTR_OFFSET = 38
_CENTRAL_NAME_OFFSET = 46
_EOCD_DISK_OFFSET = 4
_EOCD_TOTAL_ENTRIES_OFFSET = 10
_EOCD_CENTRAL_OFFSET_OFFSET = 16
_MINIMAL_PACK_EXAMPLE = (
    Path(__file__).resolve().parents[3]
    / "contract"
    / "annotation-pack"
    / "v0"
    / "examples"
    / "minimal-pack.json"
)


def _valid_pack() -> dict[str, object]:
    return json.loads(_MINIMAL_PACK_EXAMPLE.read_text(encoding="utf-8"))


def _pack_bytes() -> bytes:
    return canonical_json_bytes(_valid_pack())


def _zip_bytes(
    entries: tuple[tuple[str, bytes], ...],
    *,
    compression: int = zipfile.ZIP_DEFLATED,
    compresslevel: int = PACKAGE_COMPRESSION_LEVEL,
    archive_comment: bytes = b"",
    entry_extra: bytes = b"",
    entry_comment: bytes = b"",
    external_attr: int = _REGULAR_ATTR,
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=compression,
        compresslevel=compresslevel,
        allowZip64=False,
        strict_timestamps=True,
    ) as archive:
        archive.comment = archive_comment
        for name, content in entries:
            info = zipfile.ZipInfo(name, date_time=PACKAGE_TIMESTAMP)
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.flag_bits = 0
            info.compress_type = compression
            info.internal_attr = 0
            info.external_attr = external_attr
            info.extra = entry_extra
            info.comment = entry_comment
            archive.writestr(
                info,
                content,
                compress_type=compression,
                compresslevel=compresslevel,
            )
    return buffer.getvalue()


def _replace_u16(payload: bytes, offset: int, value: int) -> bytes:
    changed = bytearray(payload)
    struct.pack_into("<H", changed, offset, value)
    return bytes(changed)


def _replace_u32(payload: bytes, offset: int, value: int) -> bytes:
    changed = bytearray(payload)
    struct.pack_into("<I", changed, offset, value)
    return bytes(changed)


def _central_offset(payload: bytes) -> int:
    return payload.index(b"PK\x01\x02")


def _eocd_offset(payload: bytes) -> int:
    return payload.rindex(b"PK\x05\x06")


def _assert_package_error(source: bytes | Path) -> None:
    with pytest.raises(PackageError) as caught:
        validate_detached_annotations(source)
    assert caught.value.code == "package_entry_invalid"
    assert str(caught.value) == "The detached Annotation Pack is invalid."


def test_builder_is_byte_reproducible_and_returns_exact_digests() -> None:
    annotations_json = _pack_bytes()

    first = build_detached_annotations(annotations_json)
    second = build_detached_annotations(annotations_json)

    assert first == second
    assert first.package_bytes == second.package_bytes
    assert first.byte_length == len(first.package_bytes)
    assert len(first.sha256) == 64
    assert len(first.annotations_json_sha256) == 64
    assert annotations_json.decode("utf-8") not in repr(first)


def test_generated_zip_has_one_fixed_root_entry_and_no_companions() -> None:
    result = build_detached_annotations(_pack_bytes())

    with zipfile.ZipFile(BytesIO(result.package_bytes), mode="r") as archive:
        assert archive.namelist() == [ANNOTATIONS_ENTRY_NAME]
        assert archive.comment == b""
        info = archive.infolist()[0]
        assert info.date_time == PACKAGE_TIMESTAMP
        assert info.compress_type == zipfile.ZIP_DEFLATED
        assert info.create_system == 3
        assert info.create_version == 20
        assert info.extract_version == 20
        assert info.flag_bits == 0
        assert info.external_attr == _REGULAR_ATTR
        assert info.internal_attr == 0
        assert info.extra == b""
        assert info.comment == b""
        assert archive.read(info) == _pack_bytes()


def test_media_type_is_the_exact_pinned_detached_profile() -> None:
    assert DETACHED_ANNOTATIONS_MEDIA_TYPE == (
        'application/zip;profile="https://www.w3.org/TR/epub-anno-10/"'
    )
    assert MAX_DETACHED_PACKAGE_BYTES == MAX_PACKAGE_BYTES == 8 * 1024 * 1024


def test_validate_and_read_return_schema_compatible_detached_document() -> None:
    annotations_json = _pack_bytes()
    package = build_detached_annotations(annotations_json).package_bytes

    validated = validate_detached_annotations(
        package,
        expected_annotations_json=annotations_json,
    )

    assert validated.annotations_json == annotations_json
    assert validated.validation.status == "valid"
    assert validated.validation.publishable
    assert isinstance(validated.document, dict)
    assert isinstance(validated.document["items"], list)
    assert list(pack_validator().iter_errors(validated.document)) == []
    assert read_detached_annotations(package) == annotations_json
    assert annotations_json.decode("utf-8") not in repr(validated)
    validated.document["id"] = "changed"
    assert read_detached_annotations(package) == annotations_json


def test_explicit_empty_pack_remains_semantically_valid_at_package_layer() -> None:
    pack = _valid_pack()
    pack["items"] = []
    annotations_json = canonical_json_bytes(pack)

    validated = validate_detached_annotations(
        build_detached_annotations(annotations_json).package_bytes
    )

    assert validated.validation.status == "valid"
    assert [finding.code for finding in validated.validation.findings] == [
        "empty_track"
    ]


def test_standalone_path_wrapper_creates_new_file_and_reopens_it(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "second-reader.annotations"
    annotations_json = _pack_bytes()

    result = package_detached_annotations(annotations_json, destination)

    assert destination.read_bytes() == result.package_bytes
    assert read_detached_annotations(destination) == annotations_json


def test_standalone_path_wrapper_never_overwrites_existing_file(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "second-reader.annotations"
    destination.write_bytes(b"sentinel")

    with pytest.raises(PackageError):
        package_detached_annotations(_pack_bytes(), destination)

    assert destination.read_bytes() == b"sentinel"


def test_standalone_path_wrapper_cleans_partial_write_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "partial.annotations"
    original_write = packaging_module.os.write
    writes = 0

    def partial_then_fail(descriptor: int, content: object) -> int:
        nonlocal writes
        writes += 1
        if writes == 1:
            return original_write(descriptor, memoryview(content)[:32])
        raise OSError("simulated write failure")

    monkeypatch.setattr(packaging_module.os, "write", partial_then_fail)

    with pytest.raises(PackageError):
        package_detached_annotations(_pack_bytes(), destination)

    assert writes == 2
    assert not destination.exists()


def test_standalone_path_wrapper_cleans_file_fsync_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "fsync.annotations"
    original_fsync = packaging_module.os.fsync
    failed = False

    def fail_first_regular_fsync(descriptor: int) -> None:
        nonlocal failed
        if not failed and stat.S_ISREG(os.fstat(descriptor).st_mode):
            failed = True
            raise OSError("simulated fsync failure")
        original_fsync(descriptor)

    monkeypatch.setattr(packaging_module.os, "fsync", fail_first_regular_fsync)

    with pytest.raises(PackageError):
        package_detached_annotations(_pack_bytes(), destination)

    assert failed
    assert not destination.exists()


def test_standalone_path_wrapper_cleans_post_write_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "invalid-after-write.annotations"
    original_validate = packaging_module.validate_detached_annotations

    def fail_path_validation(source, **kwargs):
        if source == destination:
            raise PackageError()
        return original_validate(source, **kwargs)

    monkeypatch.setattr(
        packaging_module,
        "validate_detached_annotations",
        fail_path_validation,
    )

    with pytest.raises(PackageError):
        package_detached_annotations(_pack_bytes(), destination)

    assert not destination.exists()


def test_post_write_third_party_replacement_is_never_unlinked_or_overwritten(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "replaced.annotations"
    displaced_created = tmp_path / "created-by-packager.annotations"
    third_party_content = b"third-party replacement must survive"
    original_validate = packaging_module.validate_detached_annotations
    replaced = False

    def replace_before_path_validation(source, **kwargs):
        nonlocal replaced
        if source == destination:
            replaced = True
            destination.rename(displaced_created)
            destination.write_bytes(third_party_content)
            raise PackageError()
        return original_validate(source, **kwargs)

    monkeypatch.setattr(
        packaging_module,
        "validate_detached_annotations",
        replace_before_path_validation,
    )

    with pytest.raises(PackageError):
        package_detached_annotations(_pack_bytes(), destination)

    assert replaced
    assert destination.read_bytes() == third_party_content
    assert read_detached_annotations(displaced_created) == _pack_bytes()


@pytest.mark.parametrize(
    "destination_name,reproducible",
    [("not-a-package.zip", True), ("pack.annotations", False)],
)
def test_standalone_path_wrapper_rejects_noncanonical_requests(
    tmp_path: Path,
    destination_name: str,
    reproducible: bool,
) -> None:
    destination = tmp_path / destination_name

    with pytest.raises(PackageError):
        package_detached_annotations(
            _pack_bytes(),
            destination,
            reproducible=reproducible,
        )

    assert not destination.exists()


@pytest.mark.parametrize(
    "name",
    [
        "pack.json",
        "/annotations.json",
        "../annotations.json",
        "nested/annotations.json",
        r"nested\annotations.json",
        "C:/annotations.json",
    ],
)
def test_wrong_root_absolute_windows_and_traversal_entries_are_rejected(
    name: str,
) -> None:
    _assert_package_error(_zip_bytes(((name, _pack_bytes()),)))


@pytest.mark.parametrize(
    "extra_name",
    ["source.epub", "validation-report.json", "manifest.json", "asset.txt"],
)
def test_extra_epub_report_manifest_and_asset_entries_are_rejected(
    extra_name: str,
) -> None:
    _assert_package_error(
        _zip_bytes(
            (
                (ANNOTATIONS_ENTRY_NAME, _pack_bytes()),
                (extra_name, b"not allowed"),
            )
        )
    )


def test_duplicate_root_entries_are_rejected() -> None:
    with pytest.warns(UserWarning, match="Duplicate name"):
        package = _zip_bytes(
            (
                (ANNOTATIONS_ENTRY_NAME, _pack_bytes()),
                (ANNOTATIONS_ENTRY_NAME, _pack_bytes()),
            )
        )

    _assert_package_error(package)


def test_empty_archive_and_nul_truncated_root_are_rejected() -> None:
    _assert_package_error(_zip_bytes(()))
    package = bytearray(build_detached_annotations(_pack_bytes()).package_bytes)
    central = _central_offset(package)
    package[_LOCAL_NAME_OFFSET] = 0
    package[central + _CENTRAL_NAME_OFFSET] = 0
    _assert_package_error(bytes(package))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"compression": zipfile.ZIP_STORED},
        {"archive_comment": b"comment"},
        {"entry_extra": b"\x99\x99\x00\x00"},
        {"entry_comment": b"comment"},
        {"external_attr": (stat.S_IFLNK | 0o777) << 16},
        {"external_attr": (stat.S_IFDIR | 0o755) << 16},
    ],
)
def test_noncanonical_method_comments_extra_and_nonregular_modes_are_rejected(
    kwargs: dict[str, object],
) -> None:
    _assert_package_error(
        _zip_bytes(((ANNOTATIONS_ENTRY_NAME, _pack_bytes()),), **kwargs)
    )


def test_safe_alternate_deflate_stream_is_not_bound_to_local_zlib_bytes() -> None:
    official = build_detached_annotations(_pack_bytes()).package_bytes
    level_one = _zip_bytes(
        ((ANNOTATIONS_ENTRY_NAME, _pack_bytes()),),
        compresslevel=1,
    )
    assert level_one != official

    assert read_detached_annotations(level_one) == _pack_bytes()


@pytest.mark.parametrize(
    "local_flag,central_flag",
    [
        (0x0001, 0x0001),
        (0x0001, 0),
        (0, 0x0001),
        (0x0008, 0x0008),
        (0x0008, 0),
        (0, 0x0008),
        (0x0040, 0x0040),
        (0x0800, 0x0800),
    ],
)
def test_encryption_descriptor_strong_encryption_and_flag_drift_are_rejected(
    local_flag: int,
    central_flag: int,
) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    changed = _replace_u16(package, _LOCAL_FLAGS_OFFSET, local_flag)
    changed = _replace_u16(
        changed,
        central + _CENTRAL_FLAGS_OFFSET,
        central_flag,
    )

    _assert_package_error(changed)


def test_local_and_central_filename_mismatch_is_rejected() -> None:
    changed = bytearray(build_detached_annotations(_pack_bytes()).package_bytes)
    changed[_LOCAL_NAME_OFFSET] = ord("A")

    _assert_package_error(bytes(changed))


@pytest.mark.parametrize(
    "local_offset,central_offset",
    [
        (_LOCAL_METHOD_OFFSET, _CENTRAL_METHOD_OFFSET),
        (_LOCAL_CRC_OFFSET, _CENTRAL_CRC_OFFSET),
        (_LOCAL_COMPRESSED_SIZE_OFFSET, _CENTRAL_COMPRESSED_SIZE_OFFSET),
        (_LOCAL_UNCOMPRESSED_SIZE_OFFSET, _CENTRAL_UNCOMPRESSED_SIZE_OFFSET),
    ],
)
def test_local_central_method_crc_and_size_disagreement_is_rejected(
    local_offset: int,
    central_offset: int,
) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    if local_offset == _LOCAL_METHOD_OFFSET:
        changed = _replace_u16(package, local_offset, zipfile.ZIP_STORED)
    else:
        changed = _replace_u32(package, local_offset, 1)
    assert changed != package
    assert central_offset >= 0

    _assert_package_error(changed)


def test_central_metadata_drift_is_rejected_before_decompression() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    changed = _replace_u32(
        package,
        central + _CENTRAL_EXTERNAL_ATTR_OFFSET,
        (stat.S_IFLNK | 0o777) << 16,
    )

    _assert_package_error(changed)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda package, central: _replace_u16(package, central + 4, 20),
        lambda package, central: _replace_u32(
            package,
            central + _CENTRAL_EXTERNAL_ATTR_OFFSET,
            0o644 << 16,
        ),
        lambda package, central: _replace_u32(
            package,
            central + _CENTRAL_EXTERNAL_ATTR_OFFSET,
            (stat.S_IFREG | 0o666) << 16,
        ),
        lambda package, central: _replace_u16(
            _replace_u16(package, 10, 1),
            central + _CENTRAL_MODIFIED_TIME_OFFSET,
            1,
        ),
        lambda package, central: _replace_u16(
            _replace_u16(package, _LOCAL_METHOD_OFFSET, 99),
            central + _CENTRAL_METHOD_OFFSET,
            99,
        ),
    ],
)
def test_dos_creator_missing_type_writable_mode_time_and_aes_are_rejected(
    mutate,
) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    _assert_package_error(mutate(package, _central_offset(package)))


def test_matching_but_false_crc_is_rejected_by_raw_payload_check() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    changed = _replace_u32(package, _LOCAL_CRC_OFFSET, 0)
    changed = _replace_u32(changed, central + _CENTRAL_CRC_OFFSET, 0)

    _assert_package_error(changed)


def test_trailing_bytes_inside_declared_deflate_stream_are_rejected() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    compressed_size = struct.unpack_from("<I", package, _LOCAL_COMPRESSED_SIZE_OFFSET)[
        0
    ]
    changed = package[:central] + b"\x00" + package[central:]
    shifted_central = central + 1
    shifted_eocd = _eocd_offset(changed)
    changed = _replace_u32(
        changed,
        _LOCAL_COMPRESSED_SIZE_OFFSET,
        compressed_size + 1,
    )
    changed = _replace_u32(
        changed,
        shifted_central + _CENTRAL_COMPRESSED_SIZE_OFFSET,
        compressed_size + 1,
    )
    changed = _replace_u32(
        changed,
        shifted_eocd + _EOCD_CENTRAL_OFFSET_OFFSET,
        shifted_central,
    )

    _assert_package_error(changed)


def test_hidden_gap_between_payload_and_central_directory_is_rejected() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    changed = package[:central] + b"hidden" + package[central:]
    shifted_eocd = _eocd_offset(changed)
    changed = _replace_u32(
        changed,
        shifted_eocd + _EOCD_CENTRAL_OFFSET_OFFSET,
        central + len(b"hidden"),
    )

    _assert_package_error(changed)


def test_consistent_but_false_uncompressed_size_is_rejected_after_inflate() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    actual = struct.unpack_from("<I", package, _LOCAL_UNCOMPRESSED_SIZE_OFFSET)[0]
    changed = _replace_u32(package, _LOCAL_UNCOMPRESSED_SIZE_OFFSET, actual + 1)
    changed = _replace_u32(
        changed,
        central + _CENTRAL_UNCOMPRESSED_SIZE_OFFSET,
        actual + 1,
    )

    _assert_package_error(changed)


def test_declared_entry_size_and_compression_ratio_limits_are_rejected() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    central = _central_offset(package)
    oversize = MAX_ANNOTATIONS_ENTRY_BYTES + 1
    changed = _replace_u32(package, _LOCAL_UNCOMPRESSED_SIZE_OFFSET, oversize)
    changed = _replace_u32(
        changed,
        central + _CENTRAL_UNCOMPRESSED_SIZE_OFFSET,
        oversize,
    )
    _assert_package_error(changed)

    compressed_size = struct.unpack_from("<I", package, _LOCAL_COMPRESSED_SIZE_OFFSET)[
        0
    ]
    high_ratio_size = compressed_size * 101
    changed = _replace_u32(package, _LOCAL_UNCOMPRESSED_SIZE_OFFSET, high_ratio_size)
    changed = _replace_u32(
        changed,
        central + _CENTRAL_UNCOMPRESSED_SIZE_OFFSET,
        high_ratio_size,
    )
    _assert_package_error(changed)


def test_package_byte_limit_is_checked_before_zip_parsing() -> None:
    _assert_package_error(b"x" * (MAX_PACKAGE_BYTES + 1))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda package: b"junk" + package,
        lambda package: package + b"junk",
        lambda package: package[:-1],
        lambda package: package[:100] + b"broken" + package[106:],
    ],
)
def test_prepended_trailing_truncated_and_corrupt_archives_are_rejected(mutate) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    _assert_package_error(mutate(package))


def test_multidisk_and_zip64_markers_are_rejected() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    eocd = _eocd_offset(package)

    multidisk = _replace_u16(package, eocd + _EOCD_DISK_OFFSET, 1)
    zip64 = _replace_u16(package, eocd + _EOCD_TOTAL_ENTRIES_OFFSET, 0xFFFF)

    _assert_package_error(multidisk)
    _assert_package_error(zip64)


@pytest.mark.parametrize(
    "annotations_json",
    [
        b"\xef\xbb\xbf{}\n",
        b'{"duplicate":1,"duplicate":2}\n',
        b'{"number":NaN}\n',
        b'{"space": true}\n',
        canonical_json_bytes({"not": "an Annotation Pack"}),
    ],
)
def test_bom_duplicate_nonfinite_noncanonical_and_schema_invalid_json_are_rejected(
    annotations_json: bytes,
) -> None:
    package = _zip_bytes(((ANNOTATIONS_ENTRY_NAME, annotations_json),))

    _assert_package_error(package)


@pytest.mark.parametrize(
    "annotations_json",
    [
        b"\xff\n",
        b'{"float":1.25}\n',
        b'{"integer":9007199254740992}\n',
    ],
)
def test_invalid_utf8_float_and_unsafe_integer_entries_are_rejected(
    annotations_json: bytes,
) -> None:
    _assert_package_error(_zip_bytes(((ANNOTATIONS_ENTRY_NAME, annotations_json),)))


def test_builder_rejects_noncanonical_or_semantically_invalid_json() -> None:
    for annotations_json in (
        b'{"space": true}\n',
        canonical_json_bytes({"not": "a pack"}),
    ):
        with pytest.raises(PackageError):
            build_detached_annotations(annotations_json)


def test_builder_rejects_unreleased_heavy_v0_public_wire() -> None:
    heavy = _valid_pack()
    heavy["sr:specVersion"] = "0.1.0"
    heavy["sr:track"] = {
        "id": "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa",
        "type": "sr:AnnotationTrack",
        "sr:key": "second-reader-agent",
    }
    heavy["about"]["sr:work"] = {  # type: ignore[index]
        "id": "urn:uuid:c34f891e-f715-5663-a556-f1fc6e313345",
        "type": "sr:WorkIdentity",
    }

    with pytest.raises(PackageError):
        build_detached_annotations(canonical_json_bytes(heavy))


def test_expected_entry_bytes_must_match_exactly() -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes

    with pytest.raises(PackageError):
        validate_detached_annotations(
            package,
            expected_annotations_json=_pack_bytes() + b"\n",
        )


def test_path_reader_rejects_leaf_and_parent_symlinks(tmp_path: Path) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    real = tmp_path / "real.annotations"
    real.write_bytes(package)
    leaf_link = tmp_path / "leaf.annotations"
    leaf_link.symlink_to(real)
    _assert_package_error(leaf_link)

    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    (real_parent / "pack.annotations").write_bytes(package)
    parent_link = tmp_path / "linked-parent"
    parent_link.symlink_to(real_parent, target_is_directory=True)
    _assert_package_error(parent_link / "pack.annotations")


def test_path_reader_rejects_nonregular_fifo(tmp_path: Path) -> None:
    fifo = tmp_path / "pipe.annotations"
    os.mkfifo(fifo)

    _assert_package_error(fifo)


def test_path_reader_detects_leaf_replacement_during_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    source = tmp_path / "pack.annotations"
    moved = tmp_path / "old.annotations"
    source.write_bytes(package)
    original_read = packaging_module.os.read
    replaced = False

    def replacing_read(descriptor: int, count: int) -> bytes:
        nonlocal replaced
        chunk = original_read(descriptor, count)
        if chunk and not replaced:
            replaced = True
            source.rename(moved)
            source.write_bytes(package)
        return chunk

    monkeypatch.setattr(packaging_module.os, "read", replacing_read)

    _assert_package_error(source)
    assert replaced


def test_validator_never_uses_disk_extraction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes

    def forbidden(*_args, **_kwargs):
        raise AssertionError("package validation must not extract")

    monkeypatch.setattr(zipfile.ZipFile, "extract", forbidden)
    monkeypatch.setattr(zipfile.ZipFile, "extractall", forbidden)

    assert read_detached_annotations(package) == _pack_bytes()


def test_path_reader_rejects_lexical_parent_traversal(tmp_path: Path) -> None:
    package = build_detached_annotations(_pack_bytes()).package_bytes
    source = tmp_path / "pack.annotations"
    source.write_bytes(package)

    _assert_package_error(tmp_path / "child" / ".." / "pack.annotations")
