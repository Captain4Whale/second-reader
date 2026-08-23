from __future__ import annotations

from dataclasses import replace
import hashlib
from io import BytesIO
from pathlib import Path
import re
import traceback
import warnings
import zipfile

import pytest

import src.annotation_pack.epub_source as epub_source_module
from src.annotation_pack.epub_source import (
    DEFAULT_SOURCE_ASSET,
    EpubSourceError,
    PublicationIdentifier,
    classify_isbn,
    is_public_display_metadata,
    normalize_epub_href,
    normalize_opf_relative_href,
    verify_epub_source,
)
from tests.annotation_pack.epub_factory import (
    DEFAULT_CHAPTERS,
    FixtureIdentifier,
    FixtureMetadata,
    FixtureZipEntry,
    build_epub_bytes,
    fixture_entries,
    repack_epub,
    replace_epub_entries,
)


def _write_source(
    tmp_path: Path,
    content: bytes | None = None,
    *,
    relative_path: str = DEFAULT_SOURCE_ASSET,
) -> tuple[Path, Path, bytes]:
    output_dir = tmp_path / "book-output"
    source_path = output_dir.joinpath(*relative_path.split("/"))
    source_path.parent.mkdir(parents=True)
    epub_bytes = content if content is not None else build_epub_bytes()
    source_path.write_bytes(epub_bytes)
    return output_dir, source_path, epub_bytes


def _replace_member(content: bytes, name: str, data: bytes) -> bytes:
    return replace_epub_entries(content, (FixtureZipEntry(name, data),))


def _member_bytes(content: bytes, name: str) -> bytes:
    with zipfile.ZipFile(BytesIO(content), mode="r") as archive:
        return archive.read(name)


def _assert_source_error(
    expected_message_fragment: str,
    call: object,
) -> EpubSourceError:
    with pytest.raises(EpubSourceError) as raised:
        call()  # type: ignore[operator]
    assert raised.value.code == "source_asset_missing_or_not_epub"
    assert expected_message_fragment in raised.value.message
    return raised.value


def test_factory_and_verification_are_byte_and_hash_deterministic(
    tmp_path: Path,
) -> None:
    first = build_epub_bytes()
    second = build_epub_bytes()
    assert first == second

    output_dir, _, content = _write_source(tmp_path, first)
    verified = verify_epub_source(output_dir)
    assert verified.sha256 == hashlib.sha256(content).hexdigest()
    assert verified.byte_length == len(content)
    assert verified.relative_path == DEFAULT_SOURCE_ASSET
    assert verified.opf_path == "EPUB/package.opf"
    assert verified.spine_item_ids == ("chapter-one", "chapter-two")
    assert tuple(item.href for item in verified.manifest_items) == (
        "Text/chapter-01.xhtml",
        "Text/chapter-02.xhtml",
    )
    assert verified.manifest_by_id["chapter-one"].archive_path == (
        "EPUB/Text/chapter-01.xhtml"
    )
    assert str(tmp_path) not in repr(verified)


def test_repack_changes_file_identity_without_changing_opf_identity(
    tmp_path: Path,
) -> None:
    original = build_epub_bytes()
    repacked = repack_epub(original)
    assert repacked != original

    first_dir, _, _ = _write_source(tmp_path / "first", original)
    second_dir, _, _ = _write_source(tmp_path / "second", repacked)
    first = verify_epub_source(first_dir)
    second = verify_epub_source(second_dir)
    assert first.sha256 != second.sha256
    assert first.metadata == second.metadata
    assert first.manifest_items == second.manifest_items


def test_manifest_source_asset_override_and_default(tmp_path: Path) -> None:
    output_dir, _, _ = _write_source(
        tmp_path,
        relative_path="assets/the-book.epub",
    )
    verified = verify_epub_source(
        output_dir,
        {"source_asset": {"file": "assets/the-book.epub"}},
    )
    assert verified.relative_path == "assets/the-book.epub"


@pytest.mark.parametrize(
    "reference",
    [
        "/tmp/source.epub",
        "../source.epub",
        "_assets/../source.epub",
        "_assets\\source.epub",
        "C:/source.epub",
        "file:source.epub",
        "_assets/source.epub?token=secret",
        "_assets/source.epub#fragment",
        "_assets/source.epub\x00ignored",
        "_assets/source.txt",
        " ./source.epub",
        "./_assets/source.epub",
        "_assets/./source.epub",
        "_assets//source.epub",
        "_assets/source.epub/",
    ],
)
def test_manifest_source_reference_rejects_unsafe_paths(
    tmp_path: Path,
    reference: str,
) -> None:
    output_dir, _, _ = _write_source(tmp_path)
    error = _assert_source_error(
        "Source asset",
        lambda: verify_epub_source(
            output_dir,
            {"source_asset": {"file": reference}},
        ),
    )
    assert str(tmp_path) not in str(error)
    assert "token=secret" not in str(error)


def test_source_file_and_parent_symlinks_are_rejected(tmp_path: Path) -> None:
    actual_dir, actual_path, _ = _write_source(tmp_path / "actual")
    output_dir = tmp_path / "linked-output"
    (output_dir / "_assets").mkdir(parents=True)
    (output_dir / "_assets" / "source.epub").symlink_to(actual_path)
    _assert_source_error(
        "non-symlink regular file",
        lambda: verify_epub_source(output_dir),
    )

    output_dir_2 = tmp_path / "linked-parent-output"
    output_dir_2.mkdir()
    (output_dir_2 / "_assets").symlink_to(actual_dir / "_assets")
    _assert_source_error(
        "non-symlink regular file",
        lambda: verify_epub_source(output_dir_2),
    )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"not a zip", "ZIP magic"),
        (build_epub_bytes(omit_entries=("mimetype",)), "root mimetype"),
        (
            build_epub_bytes(
                replace_entries=(FixtureZipEntry("mimetype", b"text/plain"),)
            ),
            "invalid content",
        ),
        (
            build_epub_bytes(omit_entries=("META-INF/container.xml",)),
            "container.xml",
        ),
        (
            build_epub_bytes(omit_entries=("EPUB/package.opf",)),
            "OPF package document",
        ),
        (
            build_epub_bytes(
                omit_entries=("EPUB/Text/chapter-02.xhtml",),
            ),
            "missing local resource",
        ),
    ],
)
def test_missing_or_corrupt_epub_components_fail_closed(
    tmp_path: Path,
    content: bytes,
    message: str,
) -> None:
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error(message, lambda: verify_epub_source(output_dir))


def test_mimetype_must_be_first_and_stored(tmp_path: Path) -> None:
    compressed_mimetype = build_epub_bytes(
        replace_entries=(
            FixtureZipEntry(
                "mimetype",
                b"application/epub+zip",
                compression=zipfile.ZIP_DEFLATED,
            ),
        )
    )
    output_dir, _, _ = _write_source(tmp_path / "compressed", compressed_mimetype)
    _assert_source_error(
        "stored without compression",
        lambda: verify_epub_source(output_dir),
    )

    normal = build_epub_bytes(
        entry_order=(
            "META-INF/container.xml",
            "mimetype",
            "EPUB/package.opf",
            "EPUB/Text/chapter-01.xhtml",
            "EPUB/Text/chapter-02.xhtml",
        )
    )
    output_dir, _, _ = _write_source(tmp_path / "not-first", normal)
    _assert_source_error("must begin", lambda: verify_epub_source(output_dir))


def test_xml_doctype_and_entity_declarations_are_rejected(tmp_path: Path) -> None:
    unsafe_container = (
        b'<?xml version="1.0"?>\n'
        b'<!DOCTYPE container [<!ENTITY leak SYSTEM "file:///etc/passwd">]>\n'
        b'<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        b'<rootfiles><rootfile full-path="EPUB/package.opf" '
        b'media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    content = _replace_member(
        build_epub_bytes(),
        "META-INF/container.xml",
        unsafe_container,
    )
    output_dir, _, _ = _write_source(tmp_path, content)
    error = _assert_source_error(
        "forbidden XML declaration",
        lambda: verify_epub_source(output_dir),
    )
    assert "/etc/passwd" not in str(error)


def test_container_requires_exact_namespace_structure_and_media_type(
    tmp_path: Path,
) -> None:
    base = build_epub_bytes()
    wrong_media = _member_bytes(base, "META-INF/container.xml").replace(
        b"application/oebps-package+xml",
        b"text/plain",
    )
    content = _replace_member(base, "META-INF/container.xml", wrong_media)
    output_dir, _, _ = _write_source(tmp_path / "wrong-media", content)
    _assert_source_error("required media type", lambda: verify_epub_source(output_dir))

    nested_rootfile = (
        b'<?xml version="1.0"?>'
        b'<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" '
        b'xmlns:evil="https://evil.invalid/">'
        b"<rootfiles><evil:wrapper>"
        b'<rootfile full-path="EPUB/package.opf" '
        b'media-type="application/oebps-package+xml"/>'
        b"</evil:wrapper></rootfiles></container>"
    )
    content = _replace_member(base, "META-INF/container.xml", nested_rootfile)
    output_dir, _, _ = _write_source(tmp_path / "nested", content)
    _assert_source_error("rootfile", lambda: verify_epub_source(output_dir))

    namespaced_attribute = (
        b'<?xml version="1.0"?>'
        b'<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" '
        b'xmlns:evil="https://evil.invalid/">'
        b'<rootfiles><rootfile evil:full-path="EPUB/package.opf" '
        b'media-type="application/oebps-package+xml"/>'
        b"</rootfiles></container>"
    )
    content = _replace_member(base, "META-INF/container.xml", namespaced_attribute)
    output_dir, _, _ = _write_source(tmp_path / "evil-attribute", content)
    _assert_source_error("rootfile path", lambda: verify_epub_source(output_dir))


@pytest.mark.parametrize("element_name", ["metadata", "manifest", "spine"])
def test_opf_core_elements_must_use_the_exact_opf_namespace(
    tmp_path: Path,
    element_name: str,
) -> None:
    base = build_epub_bytes()
    opf = _member_bytes(base, "EPUB/package.opf")
    opf = opf.replace(
        b'<package xmlns="http://www.idpf.org/2007/opf"',
        (
            b'<package xmlns="http://www.idpf.org/2007/opf" '
            b'xmlns:evil="https://evil.invalid/"'
        ),
    )
    opf = opf.replace(
        f"<{element_name}>".encode(),
        f"<evil:{element_name}>".encode(),
    ).replace(
        f"</{element_name}>".encode(),
        f"</evil:{element_name}>".encode(),
    )
    content = _replace_member(base, "EPUB/package.opf", opf)
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error(
        "metadata" if element_name == "metadata" else element_name,
        lambda: verify_epub_source(output_dir),
    )


@pytest.mark.parametrize(
    "name",
    [
        "../escape.xhtml",
        "/absolute.xhtml",
        "C:/windows.xhtml",
        "Text\\windows.xhtml",
        "Text/./dot.xhtml",
    ],
)
def test_unsafe_zip_entry_names_are_rejected(tmp_path: Path, name: str) -> None:
    content = build_epub_bytes(extra_entries=(FixtureZipEntry(name, b"unsafe"),))
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error("archive path", lambda: verify_epub_source(output_dir))


def test_duplicate_and_symlink_zip_entries_are_rejected(tmp_path: Path) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        duplicate = build_epub_bytes(
            extra_entries=(FixtureZipEntry("EPUB/package.opf", b"duplicate"),)
        )
    output_dir, _, _ = _write_source(tmp_path / "duplicate", duplicate)
    _assert_source_error("duplicate entry", lambda: verify_epub_source(output_dir))

    symlink = build_epub_bytes(
        extra_entries=(
            FixtureZipEntry(
                "EPUB/Text/link.xhtml",
                b"chapter-01.xhtml",
                unix_mode=0o120777,
            ),
        )
    )
    output_dir, _, _ = _write_source(tmp_path / "symlink", symlink)
    _assert_source_error("symbolic-link", lambda: verify_epub_source(output_dir))

    fifo = build_epub_bytes(
        extra_entries=(
            FixtureZipEntry(
                "EPUB/special.pipe",
                b"",
                unix_mode=0o010644,
            ),
        )
    )
    output_dir, _, _ = _write_source(tmp_path / "fifo", fifo)
    _assert_source_error("special-file", lambda: verify_epub_source(output_dir))


def test_zip_entry_name_and_unix_file_type_must_agree(tmp_path: Path) -> None:
    base = build_epub_bytes()
    chapter_name = "EPUB/Text/chapter-01.xhtml"
    directory_typed_chapter = replace_epub_entries(
        base,
        (
            FixtureZipEntry(
                chapter_name,
                _member_bytes(base, chapter_name),
                unix_mode=0o040755,
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path / "directory-typed-file",
        directory_typed_chapter,
    )
    _assert_source_error("file type", lambda: verify_epub_source(output_dir))

    regular_typed_directory = build_epub_bytes(
        extra_entries=(FixtureZipEntry("EPUB/fakedir/", b"", unix_mode=0o100644),)
    )
    output_dir, _, _ = _write_source(
        tmp_path / "regular-typed-directory",
        regular_typed_directory,
    )
    _assert_source_error("file type", lambda: verify_epub_source(output_dir))


def _mark_zip_encrypted(content: bytes) -> bytes:
    mutable = bytearray(content)
    signatures_and_offsets = ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8))
    for signature, flag_offset in signatures_and_offsets:
        start = 0
        while (position := content.find(signature, start)) >= 0:
            flags = int.from_bytes(
                mutable[position + flag_offset : position + flag_offset + 2],
                "little",
            )
            mutable[position + flag_offset : position + flag_offset + 2] = (
                flags | 1
            ).to_bytes(2, "little")
            start = position + len(signature)
    return bytes(mutable)


def test_encrypted_zip_entry_is_rejected_before_read(tmp_path: Path) -> None:
    content = _mark_zip_encrypted(build_epub_bytes())
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error("encrypted entry", lambda: verify_epub_source(output_dir))


@pytest.mark.parametrize(
    ("signature", "flag_offset"),
    [(b"PK\x03\x04", 6), (b"PK\x01\x02", 8)],
)
def test_local_or_central_only_encryption_flag_is_rejected(
    tmp_path: Path,
    signature: bytes,
    flag_offset: int,
) -> None:
    content = bytearray(build_epub_bytes())
    position = content.find(signature)
    assert position >= 0
    flags = int.from_bytes(
        content[position + flag_offset : position + flag_offset + 2],
        "little",
    )
    content[position + flag_offset : position + flag_offset + 2] = (flags | 1).to_bytes(
        2, "little"
    )
    output_dir, _, _ = _write_source(tmp_path, bytes(content))
    _assert_source_error("encrypted entry", lambda: verify_epub_source(output_dir))


def _central_directory_records(content: bytes) -> tuple[int, list[bytes], int]:
    eocd_offset = content.rfind(b"PK\x05\x06")
    assert eocd_offset >= 0
    central_offset = int.from_bytes(
        content[eocd_offset + 16 : eocd_offset + 20], "little"
    )
    records: list[bytes] = []
    position = central_offset
    while position < eocd_offset:
        assert content[position : position + 4] == b"PK\x01\x02"
        filename_length = int.from_bytes(
            content[position + 28 : position + 30], "little"
        )
        extra_length = int.from_bytes(content[position + 30 : position + 32], "little")
        comment_length = int.from_bytes(
            content[position + 32 : position + 34], "little"
        )
        end = position + 46 + filename_length + extra_length + comment_length
        records.append(content[position:end])
        position = end
    return central_offset, records, eocd_offset


def test_mimetype_must_be_first_in_physical_local_header_order(
    tmp_path: Path,
) -> None:
    content = build_epub_bytes(
        entry_order=(
            "META-INF/container.xml",
            "mimetype",
            "EPUB/package.opf",
            "EPUB/Text/chapter-01.xhtml",
            "EPUB/Text/chapter-02.xhtml",
        )
    )
    central_offset, records, eocd_offset = _central_directory_records(content)
    records.sort(key=lambda record: not record[46:].startswith(b"mimetype"))
    central_reordered = (
        content[:central_offset] + b"".join(records) + content[eocd_offset:]
    )
    output_dir, _, _ = _write_source(tmp_path, central_reordered)
    _assert_source_error("first physical entry", lambda: verify_epub_source(output_dir))


@pytest.mark.parametrize("compression", [zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA])
def test_non_ocf_zip_compression_methods_are_rejected(
    tmp_path: Path,
    compression: int,
) -> None:
    content = build_epub_bytes(
        extra_entries=(
            FixtureZipEntry(
                "EPUB/unsupported.bin",
                b"unsupported",
                compression=compression,
            ),
        )
    )
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error(
        "unsupported compression method",
        lambda: verify_epub_source(output_dir),
    )


def test_zip_and_opf_hrefs_require_canonical_nfc_unicode(tmp_path: Path) -> None:
    nfd_name = "EPUB/Text/cafe\u0301.xhtml"
    content = build_epub_bytes(
        extra_entries=(FixtureZipEntry(nfd_name, b"not canonical"),)
    )
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error("canonical NFC", lambda: verify_epub_source(output_dir))

    _assert_source_error(
        "canonical NFC",
        lambda: normalize_epub_href("Text/cafe\u0301.xhtml"),
    )


def test_oversize_and_high_ratio_entries_are_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = build_epub_bytes(
        extra_entries=(FixtureZipEntry("EPUB/large.bin", b"x" * 128),)
    )
    output_dir, _, _ = _write_source(tmp_path / "oversize", content)
    monkeypatch.setattr(epub_source_module, "MAX_ZIP_ENTRY_BYTES", 100)
    _assert_source_error("oversized entry", lambda: verify_epub_source(output_dir))

    monkeypatch.setattr(
        epub_source_module,
        "MAX_ZIP_ENTRY_BYTES",
        64 * 1024 * 1024,
    )
    compressed = build_epub_bytes(
        extra_entries=(
            FixtureZipEntry(
                "EPUB/repeated.bin",
                b"0" * (2 * 1024 * 1024),
                compression=zipfile.ZIP_DEFLATED,
            ),
        )
    )
    output_dir, _, _ = _write_source(tmp_path / "ratio", compressed)
    _assert_source_error("compression ratio", lambda: verify_epub_source(output_dir))


@pytest.mark.parametrize(
    "href",
    [
        "../Text/chapter.xhtml",
        "/Text/chapter.xhtml",
        "Text\\chapter.xhtml",
        "https://example.test/chapter.xhtml",
        "Text/chapter.xhtml?download=1",
        "Text/chapter.xhtml#part",
        "Text/%2e%2e/chapter.xhtml",
        "Text/%2Fchapter.xhtml",
        "Text//chapter.xhtml",
    ],
)
def test_opf_relative_href_helper_rejects_nonlocal_or_ambiguous_paths(
    href: str,
) -> None:
    _assert_source_error(
        "unsafe resource href",
        lambda: normalize_opf_relative_href("EPUB/package.opf", href),
    )


def test_opf_relative_href_helper_normalizes_utf8_percent_encoding() -> None:
    resolved = normalize_opf_relative_href(
        "EPUB/package.opf",
        "Text/a%20small%20chapter.xhtml",
    )
    assert resolved.href == "Text/a%20small%20chapter.xhtml"
    assert resolved.archive_path == "EPUB/Text/a small chapter.xhtml"


@pytest.mark.parametrize(
    ("encoded_name", "archive_name"),
    [("a%23b.xhtml", "a#b.xhtml"), ("a%3Fb.xhtml", "a?b.xhtml")],
)
def test_percent_encoded_reserved_filename_is_verified_in_real_epub(
    tmp_path: Path,
    encoded_name: str,
    archive_name: str,
) -> None:
    chapter = replace(
        DEFAULT_CHAPTERS[0],
        href=f"Text/{encoded_name}",
    )
    encoded_archive_path = f"EPUB/Text/{encoded_name}"
    literal_archive_path = f"EPUB/Text/{archive_name}"
    xhtml = fixture_entries(chapters=(chapter,))[-1].data
    content = build_epub_bytes(
        chapters=(chapter,),
        omit_entries=(encoded_archive_path,),
        extra_entries=(FixtureZipEntry(literal_archive_path, xhtml),),
    )
    output_dir, _, _ = _write_source(tmp_path, content)

    verified = verify_epub_source(output_dir)

    assert verified.manifest_items[0].href == f"Text/{encoded_name}"
    assert verified.manifest_items[0].archive_path == literal_archive_path


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Text/chapter.xhtml#section-2", "Text/chapter.xhtml"),
        ("./Text/a small%20chapter.xhtml", "Text/a%20small%20chapter.xhtml"),
        ("Text/caf%C3%A9.xhtml", "Text/caf%C3%A9.xhtml"),
        ("Text/%7Ereader.xhtml", "Text/~reader.xhtml"),
        ("https%3Aevil.xhtml", "https%3Aevil.xhtml"),
        ("a%3Ab/chapter.xhtml", "a%3Ab/chapter.xhtml"),
    ],
)
def test_context_free_epub_href_normalization(source: str, expected: str) -> None:
    assert normalize_epub_href(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "../chapter.xhtml",
        "Text/../chapter.xhtml",
        "Text/chapter.xhtml?download=1",
        "https://example.test/chapter.xhtml",
        "Text/%2fchapter.xhtml",
        "Text\\chapter.xhtml",
        "Text/bad%escape.xhtml",
    ],
)
def test_context_free_epub_href_normalization_rejects_unsafe_values(
    source: str,
) -> None:
    _assert_source_error(
        "unsafe resource href",
        lambda: normalize_epub_href(source),
    )


def test_metadata_is_normalized_and_identifiers_are_classified(tmp_path: Path) -> None:
    metadata = FixtureMetadata(
        title="  The   Returning Question  ",
        creators=("Ada Reader", "Ada Reader", "Bea Margin"),
        language="en-US",
        unique_identifier_id="publication-id",
        identifiers=(
            FixtureIdentifier(
                value="https://publisher.example/editions/returning-question",
                identifier_id="publication-id",
            ),
            FixtureIdentifier(
                value="978-0-306-40615-7",
                identifier_id="isbn-13",
                scheme="ISBN",
            ),
            FixtureIdentifier(
                value="0-306-40615-2",
                identifier_id="isbn-10",
                identifier_type="02",
            ),
            FixtureIdentifier(
                value="https://catalog.example/records/returning-question",
                identifier_id="catalog-uri",
            ),
        ),
    )
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    verified = verify_epub_source(output_dir)
    assert verified.metadata.title == "The Returning Question"
    assert verified.metadata.creators == ("Ada Reader", "Bea Margin")
    assert verified.metadata.language == "en-US"
    assert verified.metadata.unique_identifier == (
        "https://publisher.example/editions/returning-question"
    )
    assert verified.metadata.publication_identifiers == (
        PublicationIdentifier("isbn-10", "0306406152"),
        PublicationIdentifier("isbn-13", "9780306406157"),
        PublicationIdentifier(
            "opf-identifier",
            "https://publisher.example/editions/returning-question",
        ),
        PublicationIdentifier(
            "uri",
            "https://catalog.example/records/returning-question",
        ),
    )
    assert verified.metadata.warnings == ()


def test_invalid_explicit_isbn_is_sanitized_and_excluded(tmp_path: Path) -> None:
    secretish_invalid_value = "978-0-306-40615-8?token=do-not-copy"
    metadata = replace(
        FixtureMetadata(),
        identifiers=(
            FixtureMetadata().identifiers[0],
            FixtureIdentifier(
                value=secretish_invalid_value,
                identifier_id="bad-isbn",
                scheme="ISBN",
            ),
        ),
    )
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    verified = verify_epub_source(output_dir)
    assert all(
        identifier.value != secretish_invalid_value
        for identifier in verified.metadata.publication_identifiers
    )
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )
    assert "token" not in verified.metadata.warnings[0].message
    assert secretish_invalid_value not in repr(verified.metadata.warnings)


def test_specific_isbn_scheme_mismatch_is_excluded(tmp_path: Path) -> None:
    metadata = replace(
        FixtureMetadata(),
        identifiers=(
            FixtureMetadata().identifiers[0],
            FixtureIdentifier(
                value="0-306-40615-2",
                identifier_id="mismatched-isbn",
                identifier_type="15",
            ),
        ),
    )
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    verified = verify_epub_source(output_dir)
    assert PublicationIdentifier("isbn-10", "0306406152") not in (
        verified.metadata.publication_identifiers
    )
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )


@pytest.mark.parametrize(
    "invalid_isbn",
    [
        "ISBN-10 9780306406157",
        "ISBN-13 0306406152",
        "ISBN 9780306406158",
        "9780306406158",
        "0306406153",
    ],
)
def test_metadata_isbn_shaped_invalid_values_are_not_generic_identifiers(
    tmp_path: Path,
    invalid_isbn: str,
) -> None:
    metadata = FixtureMetadata(
        unique_identifier_id="invalid-isbn",
        identifiers=(
            FixtureIdentifier(
                value=invalid_isbn,
                identifier_id="invalid-isbn",
            ),
        ),
    )
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    verified = verify_epub_source(output_dir)
    assert verified.metadata.unique_identifier is None
    assert verified.metadata.identifiers == ()
    assert verified.metadata.publication_identifiers == ()
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )


def test_whitespace_prefixed_valid_isbn_and_conflicting_subtypes(
    tmp_path: Path,
) -> None:
    valid_metadata = FixtureMetadata(
        unique_identifier_id="valid-isbn",
        identifiers=(
            FixtureIdentifier(
                value="ISBN-13 9780306406157",
                identifier_id="valid-isbn",
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path / "valid",
        build_epub_bytes(metadata=valid_metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.publication_identifiers == (
        PublicationIdentifier("isbn-13", "9780306406157"),
    )

    conflicting_metadata = FixtureMetadata(
        unique_identifier_id="conflicting-isbn",
        identifiers=(
            FixtureIdentifier(
                value="0306406152",
                identifier_id="conflicting-isbn",
                scheme="ISBN-10",
                identifier_type="15",
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path / "conflicting",
        build_epub_bytes(metadata=conflicting_metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.publication_identifiers == ()
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )


def test_bare_valid_isbn_and_arbitrary_unique_opf_id_are_classified(
    tmp_path: Path,
) -> None:
    isbn_metadata = FixtureMetadata(
        unique_identifier_id="bare-isbn",
        identifiers=(
            FixtureIdentifier(
                value="9780306406157",
                identifier_id="bare-isbn",
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path / "isbn",
        build_epub_bytes(metadata=isbn_metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.publication_identifiers == (
        PublicationIdentifier("isbn-13", "9780306406157"),
    )

    local_metadata = FixtureMetadata(
        unique_identifier_id="local-id",
        identifiers=(
            FixtureIdentifier(
                value="local-edition-42",
                identifier_id="local-id",
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path / "local",
        build_epub_bytes(metadata=local_metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.publication_identifiers == (
        PublicationIdentifier("opf-identifier", "local-edition-42"),
    )


@pytest.mark.parametrize(
    "unsafe_identifier",
    [
        "/Users/alice/private.epub?token=secret",
        r"C:\Users\alice\private.epub",
        "file:///Users/alice/private.epub",
        "https://publisher.example/book?token=secret",
        "https://publisher.example/book?key=secret",
        "https://alice:secret@publisher.example/book",
        "javascript:alert(1)",
        "data:text/html,unsafe",
        "local:/Users/alice/private-id",
        "prefix /etc/passwd",
        "By /secret",
        "Author:/etc/passwd",
        "urn:local:/home/alice/id",
        "urn:uuid:/Users/alice/private-id",
        "../private/source.epub",
        "_assets/source.epub",
        "http://localhost/private-id",
        "http://127.0.0.1/private-id",
        "http://10.0.0.1/private-id",
        "http://169.254.10.20/private-id",
        "http://100.64.0.1/private-id",
        "http://2130706433/private-id",
        "http://127.1/private-id",
        "http://0177.0.0.1/private-id",
        "http://0x7f000001/private-id",
        "http://foo.localhost/private-id",
        "http://224.0.0.1/private-id",
        "http://[ff02::1]/private-id",
        "https://publisher.example/book#token=secret",
        "urn:example:token=secret",
        "urn:example:work#api_key=secret",
        "urn:example:api_key%253Dsecret",
        "https://publisher.example/book#/Users/alice",
        "https://publisher.example/book#%252FUsers%252Falice",
        "https://publisher.example/book#file:///etc/passwd",
        "https://publisher.example/book#~/secret",
        r"https://publisher.example/book#C:\secret",
        r"https://publisher.example/book#\\server\share",
        "opaque\u0080identifier",
        "opaque\u202eidentifier",
        "x" * 2049,
    ],
)
def test_unsafe_unique_opf_identifier_is_sanitized_and_excluded(
    tmp_path: Path,
    unsafe_identifier: str,
) -> None:
    metadata = FixtureMetadata(
        unique_identifier_id="unsafe-id",
        identifiers=(
            FixtureIdentifier(
                value=unsafe_identifier,
                identifier_id="unsafe-id",
            ),
        ),
    )
    output_dir, _, _ = _write_source(
        tmp_path,
        build_epub_bytes(metadata=metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.unique_identifier is None
    assert verified.metadata.identifiers == ()
    assert verified.metadata.publication_identifiers == ()
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )
    assert unsafe_identifier not in repr(verified.metadata)
    assert "alice" not in verified.metadata.warnings[0].message


@pytest.mark.parametrize(
    "unsafe_identifier",
    [
        "https://publisher.example/book?path=%2FUsers%2Falice%2Fprivate.epub",
        "http://[::1]/private-id",
        "urn:local:/etc/private-id",
    ],
)
def test_unsafe_nonunique_identifier_is_excluded(
    tmp_path: Path,
    unsafe_identifier: str,
) -> None:
    metadata = replace(
        FixtureMetadata(),
        identifiers=(
            *FixtureMetadata().identifiers,
            FixtureIdentifier(
                value=unsafe_identifier,
                identifier_id="unsafe-secondary-id",
            ),
        ),
    )
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    verified = verify_epub_source(output_dir)
    assert all(
        identifier.value != unsafe_identifier
        for identifier in verified.metadata.identifiers
    )
    assert all(
        identifier.value != unsafe_identifier
        for identifier in verified.metadata.publication_identifiers
    )
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "invalid_publication_identifier",
    )
    assert unsafe_identifier not in repr(verified)


def test_unsafe_display_metadata_is_failed_or_sanitized(tmp_path: Path) -> None:
    unsafe_title = "/Users/alice/private.epub?token=secret"
    metadata = replace(FixtureMetadata(), title=unsafe_title)
    output_dir, _, _ = _write_source(
        tmp_path / "title",
        build_epub_bytes(metadata=metadata),
    )
    error = _assert_source_error(
        "title is not safe",
        lambda: verify_epub_source(output_dir),
    )
    assert unsafe_title not in str(error)
    assert "alice" not in str(error)

    unsafe_creator = "file:///Users/alice/author.txt"
    encoded_creator = "file%3A%2F%2F%2FUsers%2Falice%2Fprivate.epub"
    relative_artifact = "runs/alice/session.sqlite"
    bidi_creator = "Alice\u202eprivate"
    unsafe_language = "en?%74oken=secret"
    metadata = replace(
        FixtureMetadata(),
        creators=(
            "Safe Author",
            unsafe_creator,
            encoded_creator,
            relative_artifact,
            bidi_creator,
            "Safe Author",
            "By /secret",
        ),
        language=unsafe_language,
    )
    output_dir, _, _ = _write_source(
        tmp_path / "optional",
        build_epub_bytes(metadata=metadata),
    )
    verified = verify_epub_source(output_dir)
    assert verified.metadata.creators == ("Safe Author",)
    assert verified.metadata.language is None
    assert tuple(warning.code for warning in verified.metadata.warnings) == (
        "unsafe_opf_display_metadata",
        "unsafe_opf_display_metadata",
    )
    assert unsafe_creator not in repr(verified)
    assert encoded_creator not in repr(verified)
    assert relative_artifact not in repr(verified)
    assert bidi_creator not in repr(verified)
    assert unsafe_language not in repr(verified)
    assert "alice" not in repr(verified)


@pytest.mark.parametrize(
    "unsafe_title",
    [
        "file%3A%2F%2F%2FUsers%2Falice%2Fprivate.epub",
        "note %252FUsers%252Falice%252Fsecret.epub",
        "api_key%253Dsekrit",
        "runs/alice/session.sqlite",
        "A title with %74oken=secret",
        "A title with bidi \u202eprivate",
    ],
)
def test_encoded_artifact_secret_and_bidi_titles_fail_closed(
    tmp_path: Path,
    unsafe_title: str,
) -> None:
    metadata = replace(FixtureMetadata(), title=unsafe_title)
    output_dir, _, _ = _write_source(tmp_path, build_epub_bytes(metadata=metadata))
    error = _assert_source_error(
        "title is not safe",
        lambda: verify_epub_source(output_dir),
    )
    assert unsafe_title not in str(error)


def test_metadata_normalization_uses_frozen_unicode_white_space_table() -> None:
    assert epub_source_module._normalize_text(" A\u00a0 B ") == "A B"
    assert epub_source_module._normalize_text("A\u001cB\u200bC") == ("A\u001cB\u200bC")
    assert is_public_display_metadata("100% Human")
    assert not is_public_display_metadata("A\u001cB")
    assert not is_public_display_metadata("A\u200bB")
    assert not is_public_display_metadata("A\ud800B")
    assert not is_public_display_metadata("Author:file:///etc/passwd")
    assert not is_public_display_metadata({"title": "not a string"})


@pytest.mark.parametrize(
    "value",
    ["urn:", "urn::foo", "urn:x:foo", "urn:foo:", "urn:foo:#frag", "doi:"],
)
def test_malformed_publication_uri_is_not_classified_as_uri(value: str) -> None:
    assert epub_source_module._absolute_publication_uri(value) is None


@pytest.mark.parametrize("value", ["urn:foo:bar", "doi:10.1000/example"])
def test_well_formed_non_http_publication_uri_is_classified(value: str) -> None:
    assert epub_source_module._absolute_publication_uri(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "P#file:///etc/passwd",
        "P[~/secret]",
        r"P{C:\secret}",
        r"P[\\server\share]",
        "P[token=secret]",
        "Path[runs/alice/session.sqlite]",
        "Path{_assets/source.epub}",
        "Ref(state/uploads/book.json)",
        "Ref#../private/source.epub",
        "note %252FUsers%252Falice%252Fsecret.epub",
        "api_key%253Dsekrit",
    ],
)
def test_public_display_metadata_rejects_delimited_sensitive_shapes(
    value: str,
) -> None:
    assert not is_public_display_metadata(value)


@pytest.mark.parametrize("delimiter", ["#", "(", "[", "{", "=", ":", ";", " "])
@pytest.mark.parametrize(
    "shape",
    [
        "~/secret",
        r"C:\secret",
        r"\\server\share",
        "file:///etc/passwd",
        "token=secret",
        "runs/alice/session.sqlite",
    ],
)
def test_public_display_metadata_sensitive_shape_boundary_fuzz(
    delimiter: str,
    shape: str,
) -> None:
    assert not is_public_display_metadata(f"Prefix{delimiter}{shape}")


@pytest.mark.parametrize(
    "value",
    [
        "AC/DC",
        "Alice / Bob",
        "https://example.org/creators/alice",
        "https://example.org/books/book.epub",
        "See https://example.org/books/book.epub",
    ],
)
def test_public_display_metadata_keeps_benign_slashes_and_public_urls(
    value: str,
) -> None:
    assert is_public_display_metadata(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0-306-40615-2", PublicationIdentifier("isbn-10", "0306406152")),
        (
            "urn:isbn:978-0-306-40615-7",
            PublicationIdentifier("isbn-13", "9780306406157"),
        ),
        ("0-306-40615-3", None),
        ("978-0-306-40615-8", None),
        ("4006381333931", None),
        ("0000000000000", None),
        ("ISBN-10 9780306406157", None),
        ("ISBN-13 0306406152", None),
    ],
)
def test_isbn_check_digit_validation(
    value: str,
    expected: PublicationIdentifier | None,
) -> None:
    assert classify_isbn(value) == expected


def test_hash_guard_detects_mutation_during_verification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir, source_path, _ = _write_source(tmp_path)
    original = epub_source_module._stream_file_hash

    def mutate_after_hash(
        handle: object,
        *,
        failure_code: str = "source_asset_missing_or_not_epub",
    ) -> tuple[str, int]:
        result = original(  # type: ignore[arg-type]
            handle,
            failure_code=failure_code,
        )
        source_path.write_bytes(source_path.read_bytes() + b"changed")
        return result

    monkeypatch.setattr(epub_source_module, "_stream_file_hash", mutate_after_hash)
    with pytest.raises(EpubSourceError) as raised:
        verify_epub_source(output_dir)
    assert raised.value.code == "input_changed_during_export"
    assert str(tmp_path) not in str(raised.value)


def test_verified_source_recheck_detects_replacement(tmp_path: Path) -> None:
    output_dir, source_path, content = _write_source(tmp_path)
    verified = verify_epub_source(output_dir)
    source_path.write_bytes(repack_epub(content))
    with pytest.raises(EpubSourceError) as raised:
        verified.assert_unchanged()
    assert raised.value.code == "input_changed_during_export"


def test_open_verified_binds_consumers_to_verified_file_handle(
    tmp_path: Path,
) -> None:
    output_dir, _, content = _write_source(tmp_path)
    verified = verify_epub_source(output_dir)
    original_assets = output_dir / "_assets"
    parked_original_assets = output_dir / "_original_assets"
    changed_assets = output_dir / "_changed_assets"
    changed_assets.mkdir()
    (changed_assets / "source.epub").write_bytes(repack_epub(content))

    with verified.open_verified() as handle:
        original_assets.rename(parked_original_assets)
        changed_assets.rename(original_assets)
        try:
            assert handle.read() == content
        finally:
            original_assets.rename(changed_assets)
            parked_original_assets.rename(original_assets)

    assert handle.closed


def test_open_verified_detects_same_inode_mutation_even_if_bytes_are_restored(
    tmp_path: Path,
) -> None:
    output_dir, source_path, content = _write_source(tmp_path)
    verified = verify_epub_source(output_dir)

    with pytest.raises(EpubSourceError) as raised:
        with verified.open_verified() as handle:
            assert handle.read(4) == b"PK\x03\x04"
            source_path.write_bytes(repack_epub(content))
            source_path.write_bytes(content)
    assert raised.value.code == "input_changed_during_export"
    assert str(tmp_path) not in str(raised.value)


def test_opf_metadata_and_manifest_errors_are_sanitized(tmp_path: Path) -> None:
    content = build_epub_bytes()
    malformed = _replace_member(
        content,
        "EPUB/package.opf",
        (
            b'<package xmlns="http://www.idpf.org/2007/opf" '
            b'unique-identifier="publication-id">'
            b"<metadata/><manifest/></package>"
        ),
    )
    output_dir, _, _ = _write_source(tmp_path / "missing-title", malformed)
    _assert_source_error("usable title", lambda: verify_epub_source(output_dir))

    traversal_chapter = replace(
        DEFAULT_CHAPTERS[0],
        href="../outside.xhtml",
    )
    content = build_epub_bytes(
        chapters=(traversal_chapter, DEFAULT_CHAPTERS[1]),
    )
    output_dir, _, _ = _write_source(tmp_path / "traversal", content)
    error = _assert_source_error("archive path", lambda: verify_epub_source(output_dir))
    assert re.search(r"/Users/|/home/", str(error)) is None


@pytest.mark.parametrize(
    ("spine_transform", "message"),
    [
        (
            lambda opf: re.sub(rb"\s*<spine>.*?</spine>", b"", opf, flags=re.S),
            "missing",
        ),
        (
            lambda opf: re.sub(
                rb"<spine>.*?</spine>",
                b"<spine></spine>",
                opf,
                flags=re.S,
            ),
            "empty",
        ),
        (
            lambda opf: opf.replace(
                b'<itemref idref="chapter-one"/>',
                b"<itemref/>",
            ),
            "incomplete itemref",
        ),
    ],
)
def test_opf_requires_a_complete_nonempty_spine(
    tmp_path: Path,
    spine_transform: object,
    message: str,
) -> None:
    base = build_epub_bytes()
    opf = _member_bytes(base, "EPUB/package.opf")
    transformed = spine_transform(opf)  # type: ignore[operator]
    content = _replace_member(base, "EPUB/package.opf", transformed)
    output_dir, _, _ = _write_source(tmp_path, content)
    _assert_source_error(message, lambda: verify_epub_source(output_dir))


def test_error_traceback_does_not_reveal_source_path(tmp_path: Path) -> None:
    output_dir = tmp_path / "private-book-output"
    output_dir.mkdir()
    caught: EpubSourceError | None = None
    try:
        verify_epub_source(output_dir)
    except EpubSourceError as error:
        caught = error
        rendered = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
    else:
        raise AssertionError("missing source EPUB should fail")
    assert str(tmp_path) not in rendered
    assert "private-book-output" not in rendered
    assert caught is not None
    assert caught.__cause__ is None
