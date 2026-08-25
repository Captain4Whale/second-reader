from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, BinaryIO

import pytest
from jsonschema import Draft202012Validator, FormatChecker

import src.annotation_pack.identity as identity_module
from src.annotation_pack.epub_source import EpubSourceError
from src.annotation_pack.identity import (
    ChapterFingerprint,
    EpubManifestIndex,
    Fingerprint,
    PublicationIdentityBuilder,
    PublicationIdentityError,
    book_content_fingerprint,
    book_content_fingerprint_stream,
    book_document_substrate_stream,
    chapter_fingerprints,
    compare_book_document_substrates,
    normalize_fingerprint_text,
    project_book_document_substrate,
)
from src.annotation_pack.schema import load_schema
from src.parsers import parse_ebook, parse_epub_stream
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_runtime.source_normalization import normalize_book_document_source
from tests.annotation_pack.epub_factory import (
    DEFAULT_CHAPTERS,
    FixtureChapter,
    FixtureMetadata,
    FixtureZipEntry,
    build_epub_bytes,
    fixture_entries,
    repack_epub,
)


def _fingerprint_vector_document() -> dict[str, Any]:
    return {
        "metadata": {
            "book": "Ignored metadata",
            "output_language": "en",
            "source_file": "/private/ignored.epub",
        },
        "chapters": [
            {
                "id": 9,
                "title": "  Cafe\u0301\r\n  Start  ",
                "href": "Text/one.xhtml",
                "paragraphs": [
                    {"paragraph_index": 1, "text": "  Alpha\tbeta\r\n"},
                    {
                        "paragraph_index": 2,
                        "text": "\u00a0",
                        "text_role": "auxiliary",
                    },
                    {
                        "paragraph_index": 3,
                        "text": "e\u0301 and\u2003space",
                        "start_cfi": "ignored",
                    },
                ],
            },
            {
                "id": 2,
                "title": "第二章",
                "href": "Text/two.xhtml",
                "paragraphs": [
                    {"paragraph_index": 1, "text": "行一\r行二"},
                ],
            },
        ],
    }


def _substrate_document() -> dict[str, Any]:
    return {
        "metadata": {"source_file": "/not/in/the/projection.epub"},
        "chapters": [
            {
                "id": 1,
                "chapter_number": None,
                "title": "T",
                "href": "Text/a.xhtml",
                "item_id": "",
                "spine_index": 0,
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "A",
                        "href": "Text/a.xhtml",
                        "text_role": "body",
                    }
                ],
            }
        ],
    }


def test_text_fingerprint_has_fixed_stream_and_digest_vectors() -> None:
    document = _fingerprint_vector_document()
    expected_stream = (
        "SECOND-READER-BOOK-DOCUMENT-TEXT-V1\n"
        "C:11:Café Start\n"
        "P:10:Alpha beta\n"
        "P:0:\n"
        "P:12:é and space\n"
        "E\n"
        "C:9:第二章\n"
        "P:13:行一 行二\n"
        "E\n"
    ).encode()

    assert book_content_fingerprint_stream(document) == expected_stream
    assert book_content_fingerprint(document).value == (
        "39593b4116a1bf902151f2da7d94606cdf00f7f552ade2ef37d11d1f1118e6cc"
    )

    chapters = chapter_fingerprints(document)
    assert [item.fingerprint.value for item in chapters] == [
        "6cee6639f28d40551e756abc20c9ca31581edf3afd431cad02e9c61f08b00a74",
        "39cb848f093238deb96373ada05ea05e4d13b9b06c9ad83c00d16b8e9543cfce",
    ]
    assert chapters[0].resource_hrefs == ("Text/one.xhtml",)


def test_white_space_table_is_frozen_instead_of_runtime_whitespace() -> None:
    assert normalize_fingerprint_text("a\u0085\u00a0\u202fb") == "a b"
    assert normalize_fingerprint_text("a\u200bb") == "a\u200bb"
    assert normalize_fingerprint_text("a\u001cb") == "a\u001cb"


def test_content_fingerprint_ignores_non_content_fields_but_not_structure() -> None:
    document = _fingerprint_vector_document()
    baseline = book_content_fingerprint(document).value

    irrelevant = deepcopy(document)
    irrelevant["metadata"]["source_file"] = "/another/private/path.epub"
    irrelevant["chapters"][0]["href"] = "Elsewhere.xhtml"
    irrelevant["chapters"][0]["paragraphs"][0]["start_cfi"] = "changed"
    assert book_content_fingerprint(irrelevant).value == baseline

    reordered = deepcopy(document)
    reordered["chapters"].reverse()
    assert book_content_fingerprint(reordered).value != baseline

    resegmented = deepcopy(document)
    first = resegmented["chapters"][0]["paragraphs"]
    first[:] = [{"paragraph_index": 1, "text": "Alpha beta é and space"}]
    assert book_content_fingerprint(resegmented).value != baseline


def test_substrate_typed_frame_and_digest_are_fixed() -> None:
    projection = project_book_document_substrate(_substrate_document())
    expected_stream = (
        b"SECOND-READER-BOOK-DOCUMENT-SUBSTRATE-V1\n"
        b"chapterCount:i:1:1\n"
        b"chapter.listOrder:i:1:1\n"
        b"chapter.id:i:1:1\n"
        b"chapter.chapterNumber:n:0:\n"
        b"chapter.title:s:1:T\n"
        b"chapter.href:s:12:Text/a.xhtml\n"
        b"chapter.itemId:s:0:\n"
        b"chapter.spineIndex:i:1:0\n"
        b"chapter.paragraphCount:i:1:1\n"
        b"paragraph.listOrder:i:1:1\n"
        b"paragraph.paragraphIndex:i:1:1\n"
        b"paragraph.text:s:1:A\n"
        b"paragraph.href:s:12:Text/a.xhtml\n"
        b"paragraph.textRole:s:4:body\n"
        b"paragraph.readable:b:1:1\n"
    )
    assert book_document_substrate_stream(projection) == expected_stream
    comparison = compare_book_document_substrates(
        _substrate_document(),
        _substrate_document(),
    )
    assert comparison.digest == (
        "41be7c745f6bb6d17b1021ad2d1e9e4d63810008de4cf3dde8e9774896274c8c"
    )


def test_substrate_mismatch_is_field_level_and_sanitized() -> None:
    rebuilt = _substrate_document()
    rebuilt["chapters"][0]["paragraphs"][0]["text"] = "A B"
    persisted = deepcopy(rebuilt)
    persisted["chapters"][0]["paragraphs"][0]["text"] = "A\u00a0B"
    assert (
        book_content_fingerprint(rebuilt).value
        == book_content_fingerprint(persisted).value
    )

    with pytest.raises(PublicationIdentityError) as raised:
        compare_book_document_substrates(rebuilt, persisted)

    error = raised.value
    assert error.code == "publication_substrate_mismatch"
    assert error.json_pointer == "/chapters/0/paragraphs/0/text"
    assert len(error.rebuilt_field_sha256 or "") == 64
    assert len(error.persisted_field_sha256 or "") == 64
    assert "A B" not in str(error)
    assert "private" not in str(error)


def test_substrate_distinguishes_missing_null_and_explicit_empty() -> None:
    rebuilt = _substrate_document()
    del rebuilt["chapters"][0]["item_id"]
    persisted = _substrate_document()

    with pytest.raises(PublicationIdentityError) as raised:
        compare_book_document_substrates(rebuilt, persisted)
    assert raised.value.json_pointer == "/chapters/0/item_id"


def test_empty_or_duplicate_chapter_identity_is_rejected() -> None:
    with pytest.raises(PublicationIdentityError, match="at least one"):
        chapter_fingerprints({"chapters": []})

    duplicate = _substrate_document()
    duplicate["chapters"].append(deepcopy(duplicate["chapters"][0]))
    with pytest.raises(PublicationIdentityError) as raised:
        chapter_fingerprints(duplicate)
    assert raised.value.code == "duplicate_chapter_id"

    long_title = _substrate_document()
    long_title["chapters"][0]["title"] = "x" * 513
    with pytest.raises(PublicationIdentityError) as raised:
        chapter_fingerprints(long_title)
    assert raised.value.code == "invalid_publication_metadata"
    assert raised.value.json_pointer == "/chapters/0/title"


def test_field_digest_is_not_a_plaintext_echo() -> None:
    rebuilt = _substrate_document()
    persisted = deepcopy(rebuilt)
    persisted["chapters"][0]["title"] = "Secret title"
    with pytest.raises(PublicationIdentityError) as raised:
        compare_book_document_substrates(rebuilt, persisted)
    assert (
        raised.value.persisted_field_sha256
        == hashlib.sha256(json_string("Secret title")).hexdigest()
    )
    assert "Secret title" not in str(raised.value)


def test_field_digest_handles_lone_surrogate_as_stable_mismatch() -> None:
    rebuilt = _substrate_document()
    persisted = deepcopy(rebuilt)
    persisted["chapters"][0]["paragraphs"][0]["text"] = "\ud800"

    with pytest.raises(PublicationIdentityError) as raised:
        compare_book_document_substrates(rebuilt, persisted)

    assert raised.value.code == "publication_substrate_mismatch"
    assert raised.value.json_pointer == "/chapters/0/paragraphs/0/text"
    assert (
        raised.value.persisted_field_sha256 == hashlib.sha256(b'"\\ud800"').hexdigest()
    )
    assert "\\ud800" not in str(raised.value)


def _write_source(output_dir: Path, content: bytes) -> Path:
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    return source


def _persisted_document(
    source: Path,
    *,
    metadata: FixtureMetadata | None = None,
) -> dict[str, Any]:
    fixture_metadata = metadata or FixtureMetadata()
    canonical = build_book_document_from_chapters(
        list(parse_ebook(str(source))),
        title=fixture_metadata.title,
        author=", ".join(fixture_metadata.creators),
        book_language=fixture_metadata.language,
        output_language="en",
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        canonical,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    return normalized


def _publication_identity_errors(wire: Mapping[str, object]) -> list[str]:
    schema = load_schema()
    validator = Draft202012Validator(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": schema["$defs"],
            "$ref": "#/$defs/publication",
        },
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(wire)]


def test_publication_identity_builder_has_fixed_end_to_end_vectors(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes())
    persisted = _persisted_document(source)
    with source.open("rb") as handle:
        assert parse_epub_stream(handle) == parse_ebook(str(source))
        assert not handle.closed
    before_files = {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob("*")
        if path.is_file()
    }

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )
    after_files = {
        path.relative_to(output_dir).as_posix(): path.read_bytes()
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    assert after_files == before_files

    assert result.file_sha256 == (
        "c838a48a613a357318a8cbc78e352fe46dca5f230793193981cc2277e467ec30"
    )
    assert result.content_sha256 == (
        "04ef1cf1d742df8b636a9021ad460c2fb5b83c1d8ab03c13cfd8a305ed78c78d"
    )
    assert result.substrate_sha256 == (
        "841282461441586c03f59313c0ce516fecffdb57018f9102d6bd3d422a1b72d3"
    )
    assert dict(result.chapter_fingerprints) == {
        1: "1f52e7a21d3245929cd8ff76f949044f239a43203ae6c54f5a26cc00d25b4076",
        2: "44a4c03d3f40503f6997049aed26f625949e014e9f7672fc2740b4d50c3ff3a9",
    }
    assert (
        book_content_fingerprint(result.rebuilt_book_document).value
        == result.content_sha256
    )
    assert {
        chapter.chapter_id: chapter.fingerprint.value
        for chapter in chapter_fingerprints(result.rebuilt_book_document)
    } == dict(result.chapter_fingerprints)
    result_projection = project_book_document_substrate(result.rebuilt_book_document)
    assert (
        hashlib.sha256(book_document_substrate_stream(result_projection)).hexdigest()
        == result.substrate_sha256
    )
    assert result.wire == {
        "dc:format": "application/epub+zip",
        "dc:title": "The Returning Question",
        "dc:identifier": [f"nih:sha-256;{result.file_sha256}"],
        "dc:creator": ["Second Reader Fixture Authors"],
    }
    assert "sr:" not in json.dumps(result.wire, sort_keys=True)
    assert _publication_identity_errors(result.wire) == []

    second = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=deepcopy(persisted),
    )
    assert second.wire == result.wire
    assert second.file_sha256 == result.file_sha256
    assert second.content_sha256 == result.content_sha256
    assert second.substrate_sha256 == result.substrate_sha256

    with pytest.raises(TypeError, match="immutable"):
        result.wire["dc:title"] = "Mutated"  # type: ignore[index]
    with pytest.raises(TypeError, match="immutable"):
        result.wire["dc:identifier"].append("urn:uuid:mutated")  # type: ignore[union-attr]
    with pytest.raises(TypeError, match="immutable"):
        result.rebuilt_book_document["metadata"]["source_file"] = "/tmp/leak"  # type: ignore[index]


def test_publication_identity_uses_exact_epub_file_and_minimal_dc_metadata(
    tmp_path: Path,
) -> None:
    builder = PublicationIdentityBuilder()
    base_bytes = build_epub_bytes()
    base_dir = tmp_path / "base"
    base_source = _write_source(base_dir, base_bytes)
    base = builder.build(
        output_dir=base_dir,
        persisted_book_document=_persisted_document(base_source),
    )

    repack_dir = tmp_path / "repack"
    repack_source = _write_source(repack_dir, repack_epub(base_bytes))
    repack = builder.build(
        output_dir=repack_dir,
        persisted_book_document=_persisted_document(repack_source),
    )
    assert repack.file_sha256 != base.file_sha256
    assert repack.content_sha256 == base.content_sha256
    assert repack.wire["dc:identifier"] != base.wire["dc:identifier"]
    assert repack.wire["dc:identifier"] == [f"nih:sha-256;{repack.file_sha256}"]

    metadata = FixtureMetadata(title="The Returning Question, Revised Metadata")
    metadata_dir = tmp_path / "metadata"
    metadata_source = _write_source(
        metadata_dir,
        build_epub_bytes(metadata=metadata),
    )
    metadata_result = builder.build(
        output_dir=metadata_dir,
        persisted_book_document=_persisted_document(
            metadata_source,
            metadata=metadata,
        ),
    )
    assert metadata_result.file_sha256 != base.file_sha256
    assert metadata_result.content_sha256 == base.content_sha256
    assert metadata_result.wire["dc:identifier"] != base.wire["dc:identifier"]
    assert metadata_result.wire["dc:title"] == metadata.title

    changed_chapters = (
        FixtureChapter(
            item_id=DEFAULT_CHAPTERS[0].item_id,
            href=DEFAULT_CHAPTERS[0].href,
            title=DEFAULT_CHAPTERS[0].title,
            paragraphs=(*DEFAULT_CHAPTERS[0].paragraphs, "One new sentence."),
        ),
        DEFAULT_CHAPTERS[1],
    )
    changed_dir = tmp_path / "changed"
    changed_source = _write_source(
        changed_dir,
        build_epub_bytes(chapters=changed_chapters),
    )
    changed = builder.build(
        output_dir=changed_dir,
        persisted_book_document=_persisted_document(changed_source),
    )
    assert changed.content_sha256 != base.content_sha256
    assert changed.wire["dc:identifier"] != base.wire["dc:identifier"]
    for result in (base, repack, metadata_result, changed):
        assert result.wire["dc:identifier"] == [f"nih:sha-256;{result.file_sha256}"]
        assert "sr:" not in json.dumps(result.wire, sort_keys=True)
        assert _publication_identity_errors(result.wire) == []


def test_publication_identity_rejects_stale_document_and_has_no_local_path(
    tmp_path: Path,
) -> None:
    base_dir = tmp_path / "base"
    base_source = _write_source(base_dir, build_epub_bytes())
    persisted = _persisted_document(base_source)
    changed_chapters = (
        FixtureChapter(
            item_id=DEFAULT_CHAPTERS[0].item_id,
            href=DEFAULT_CHAPTERS[0].href,
            title=DEFAULT_CHAPTERS[0].title,
            paragraphs=("Substrate changed.",),
        ),
        DEFAULT_CHAPTERS[1],
    )
    changed_dir = tmp_path / "changed"
    _write_source(changed_dir, build_epub_bytes(chapters=changed_chapters))

    with pytest.raises(PublicationIdentityError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=changed_dir,
            persisted_book_document=persisted,
        )
    assert raised.value.code == "publication_substrate_mismatch"
    assert raised.value.json_pointer is not None

    result = PublicationIdentityBuilder().build(
        output_dir=base_dir,
        persisted_book_document=persisted,
    )
    serialized = json.dumps(
        {
            "wire": result.wire,
            "rebuilt": result.rebuilt_book_document,
            "epub_index": {
                "opf_path": result.epub_index.opf_path,
                "manifest_hrefs": sorted(result.epub_index.manifest_hrefs),
            },
            "findings": [finding.message for finding in result.findings],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    assert str(tmp_path) not in serialized
    assert result.rebuilt_book_document["metadata"]["source_file"] == (
        "_assets/source.epub"
    )


def test_publication_identity_rejects_broken_toc_full_content_fallback(
    tmp_path: Path,
) -> None:
    chapter = DEFAULT_CHAPTERS[0]
    package = b"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         version="2.0" unique-identifier="publication-id">
  <metadata>
    <dc:title>The Returning Question</dc:title>
    <dc:creator>Second Reader Fixture Authors</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="publication-id">urn:uuid:3be917aa-aacc-5eaf-82df-8937c5d9fc73</dc:identifier>
  </metadata>
  <manifest>
    <item id="chapter-one" href="Text/chapter-01.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx"><itemref idref="chapter-one"/></spine>
</package>
"""
    broken_toc = b"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="publication-id"/></head>
  <docTitle><text>The Returning Question</text></docTitle>
  <navMap>
    <navPoint id="broken" playOrder="1">
      <navLabel><text>Missing resource</text></navLabel>
      <content src="Text/missing.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
"""
    content = build_epub_bytes(
        chapters=(chapter,),
        replace_entries=(FixtureZipEntry("EPUB/package.opf", package),),
        extra_entries=(FixtureZipEntry("EPUB/toc.ncx", broken_toc),),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, content)
    persisted = _persisted_document(source)
    assert persisted["chapters"][0].get("href") is None

    with pytest.raises(PublicationIdentityError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=output_dir,
            persisted_book_document=persisted,
        )
    assert raised.value.code == "book_document_resource_missing"
    assert raised.value.json_pointer == "/chapters/0/href"


def test_unsafe_ncx_chapter_title_fails_closed_without_echo(
    tmp_path: Path,
) -> None:
    chapter = DEFAULT_CHAPTERS[0]
    package = b"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         version="2.0" unique-identifier="publication-id">
  <metadata>
    <dc:title>The Returning Question</dc:title>
    <dc:creator>Second Reader Fixture Authors</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="publication-id">urn:uuid:3be917aa-aacc-5eaf-82df-8937c5d9fc73</dc:identifier>
  </metadata>
  <manifest>
    <item id="chapter-one" href="Text/chapter-01.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx"><itemref idref="chapter-one"/></spine>
</package>
"""
    private_title = "/Users/alice/private-notes"
    toc = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="publication-id"/></head>
  <docTitle><text>The Returning Question</text></docTitle>
  <navMap>
    <navPoint id="private-title" playOrder="1">
      <navLabel><text>{private_title}</text></navLabel>
      <content src="Text/chapter-01.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
""".encode()
    content = build_epub_bytes(
        chapters=(chapter,),
        replace_entries=(FixtureZipEntry("EPUB/package.opf", package),),
        extra_entries=(FixtureZipEntry("EPUB/toc.ncx", toc),),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, content)
    persisted = _persisted_document(source)

    with pytest.raises(PublicationIdentityError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=output_dir,
            persisted_book_document=persisted,
        )
    assert raised.value.code == "invalid_publication_metadata"
    assert raised.value.json_pointer == "/chapters/0/title"
    assert private_title not in str(raised.value)


def test_exact_rebuild_wraps_malformed_ncx_title_failure(
    tmp_path: Path,
) -> None:
    chapter = DEFAULT_CHAPTERS[0]
    package = b"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         version="2.0" unique-identifier="publication-id">
  <metadata>
    <dc:title>The Returning Question</dc:title>
    <dc:creator>Second Reader Fixture Authors</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="publication-id">urn:uuid:3be917aa-aacc-5eaf-82df-8937c5d9fc73</dc:identifier>
  </metadata>
  <manifest>
    <item id="chapter-one" href="Text/chapter-01.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx"><itemref idref="chapter-one"/></spine>
</package>
"""
    malformed_title = "Chapter " + ("9" * 5000)
    toc = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="publication-id"/></head>
  <docTitle><text>The Returning Question</text></docTitle>
  <navMap>
    <navPoint id="oversized-number" playOrder="1">
      <navLabel><text>{malformed_title}</text></navLabel>
      <content src="Text/chapter-01.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
""".encode()
    content = build_epub_bytes(
        chapters=(chapter,),
        replace_entries=(FixtureZipEntry("EPUB/package.opf", package),),
        extra_entries=(FixtureZipEntry("EPUB/toc.ncx", toc),),
    )
    output_dir = tmp_path / "book"
    _write_source(output_dir, content)

    with pytest.raises(PublicationIdentityError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=output_dir,
            persisted_book_document=_substrate_document(),
        )

    assert raised.value.code == "source_asset_missing_or_not_epub"
    assert malformed_title not in str(raised.value)


def test_chapter_resource_gate_requires_xhtml_manifest_resource() -> None:
    chapter = ChapterFingerprint(
        chapter_id=1,
        order=1,
        title="Not text",
        resource_hrefs=("Styles/book.css",),
        fingerprint=Fingerprint(
            algorithm_version="sr-book-document-chapter-v1",
            value="0" * 64,
        ),
    )
    manifest = EpubManifestIndex(
        opf_path="EPUB/package.opf",
        manifest_hrefs=frozenset({"Styles/book.css"}),
        text_resource_hrefs=frozenset(),
    )

    with pytest.raises(PublicationIdentityError) as raised:
        identity_module._require_chapter_resources_in_manifest((chapter,), manifest)
    assert raised.value.code == "book_document_resource_not_xhtml"
    assert raised.value.json_pointer == "/chapters/0/href"


@pytest.mark.parametrize(
    ("encoded_name", "archive_name"),
    [("a%23b.xhtml", "a#b.xhtml"), ("a%3Fb.xhtml", "a?b.xhtml")],
)
def test_identity_canonicalizes_parser_decoded_reserved_resource_names(
    tmp_path: Path,
    encoded_name: str,
    archive_name: str,
) -> None:
    base_chapter = DEFAULT_CHAPTERS[0]
    chapter = FixtureChapter(
        item_id=base_chapter.item_id,
        href=f"Text/{encoded_name}",
        title=base_chapter.title,
        paragraphs=base_chapter.paragraphs,
        in_spine=base_chapter.in_spine,
    )
    xhtml = fixture_entries(chapters=(chapter,))[-1].data
    content = build_epub_bytes(
        chapters=(chapter,),
        omit_entries=(f"EPUB/Text/{encoded_name}",),
        extra_entries=(FixtureZipEntry(f"EPUB/Text/{archive_name}", xhtml),),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, content)
    persisted = _persisted_document(source)

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    canonical_href = f"Text/{encoded_name}"
    chapter_document = result.rebuilt_book_document["chapters"][0]
    assert chapter_document["href"] == canonical_href
    assert {paragraph["href"] for paragraph in chapter_document["paragraphs"]} == {
        canonical_href
    }
    assert canonical_href in result.epub_index.text_resource_hrefs
    assert canonical_href in result.epub_index.resource_texts
    assert {
        paragraph_range[0]
        for paragraph_range in result.epub_index.paragraph_ranges.values()
    } == {canonical_href}
    assert "sr:" not in json.dumps(result.wire, sort_keys=True)


def test_manifest_aliases_prefer_opf_relative_hrefs_in_nested_package(
    tmp_path: Path,
) -> None:
    chapters = (
        FixtureChapter(
            item_id="nested-resource",
            href="EPUB/Text/same.xhtml",
            title="Nested resource",
            paragraphs=("The first resource is nested below the package directory.",),
        ),
        FixtureChapter(
            item_id="package-resource",
            href="Text/same.xhtml",
            title="Package resource",
            paragraphs=("The second resource lives beside the package directory.",),
        ),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes(chapters=chapters))
    persisted = _persisted_document(source)
    assert [chapter["href"] for chapter in persisted["chapters"]] == [
        "EPUB/Text/same.xhtml",
        "Text/same.xhtml",
    ]

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    assert [
        chapter["href"] for chapter in result.rebuilt_book_document["chapters"]
    ] == ["EPUB/Text/same.xhtml", "Text/same.xhtml"]
    assert {
        paragraph_range[0]
        for paragraph_range in result.epub_index.paragraph_ranges.values()
    } == {"EPUB/Text/same.xhtml", "Text/same.xhtml"}
    assert {
        "EPUB/Text/same.xhtml",
        "Text/same.xhtml",
    }.issubset(result.epub_index.text_resource_hrefs)
    assert "sr:" not in json.dumps(result.wire, sort_keys=True)


def test_publication_identity_metadata_warnings_use_only_epub_metadata(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes())
    persisted = _persisted_document(source)
    persisted["metadata"]["book"] = "Stale private display title"
    persisted["metadata"]["author"] = "Stale private author"

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )
    assert result.wire == {
        "dc:format": "application/epub+zip",
        "dc:title": "The Returning Question",
        "dc:identifier": [f"nih:sha-256;{result.file_sha256}"],
        "dc:creator": ["Second Reader Fixture Authors"],
    }
    assert [finding.json_pointer for finding in result.findings] == [
        "/about/dc:title",
        "/about/dc:creator",
    ]
    assert "Stale private" not in " ".join(
        finding.message for finding in result.findings
    )
    serialized = json.dumps(result.wire, sort_keys=True)
    assert "sr:" not in serialized
    assert "file:" not in serialized
    assert "private" not in serialized


def test_publication_identity_warns_when_verified_language_differs(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes())
    persisted = _persisted_document(source)
    persisted["metadata"]["book_language"] = "fr"

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    assert set(result.wire) == {
        "dc:format",
        "dc:title",
        "dc:identifier",
        "dc:creator",
    }
    assert "language" not in json.dumps(result.wire, sort_keys=True).lower()
    assert "sr:" not in json.dumps(result.wire, sort_keys=True)
    assert any(
        finding.code == "publication_metadata_mismatch" for finding in result.findings
    )


def test_publication_identity_rechecks_source_after_reparse(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "book"
    original_bytes = build_epub_bytes()
    source = _write_source(output_dir, original_bytes)
    persisted = _persisted_document(source)
    original_parse = identity_module.parse_epub_stream

    def parse_then_replace(handle: BinaryIO) -> list[dict[str, object]]:
        chapters = list(original_parse(handle))
        source.write_bytes(repack_epub(original_bytes))
        return chapters

    monkeypatch.setattr(identity_module, "parse_epub_stream", parse_then_replace)
    with pytest.raises(EpubSourceError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=output_dir,
            persisted_book_document=persisted,
        )
    assert raised.value.code == "input_changed_during_export"
    assert str(tmp_path) not in str(raised.value)


def test_publication_identity_parses_the_verified_handle_during_path_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "book"
    original_bytes = build_epub_bytes()
    source = _write_source(output_dir, original_bytes)
    persisted = _persisted_document(source)
    changed_chapters = (
        FixtureChapter(
            item_id=DEFAULT_CHAPTERS[0].item_id,
            href=DEFAULT_CHAPTERS[0].href,
            title=DEFAULT_CHAPTERS[0].title,
            paragraphs=("Transient replacement content.",),
        ),
        DEFAULT_CHAPTERS[1],
    )
    replacement_dir = output_dir / "_replacement_assets"
    replacement_dir.mkdir(parents=True)
    (replacement_dir / "source.epub").write_bytes(
        build_epub_bytes(chapters=changed_chapters)
    )
    original_assets = output_dir / "_assets"
    parked_assets = output_dir / "_original_assets"
    original_parse = identity_module.parse_epub_stream
    calls = 0

    def parse_during_swap(handle: BinaryIO) -> list[dict[str, object]]:
        nonlocal calls
        calls += 1
        original_assets.rename(parked_assets)
        replacement_dir.rename(original_assets)
        try:
            return list(original_parse(handle))
        finally:
            original_assets.rename(replacement_dir)
            parked_assets.rename(original_assets)

    monkeypatch.setattr(identity_module, "parse_epub_stream", parse_during_swap)
    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    assert calls == 1
    assert result.file_sha256 == hashlib.sha256(original_bytes).hexdigest()
    assert source.read_bytes() == original_bytes


def test_persisted_metadata_fallback_cannot_leak_paths_or_python_repr(
    tmp_path: Path,
) -> None:
    metadata = FixtureMetadata(
        creators=("/Users/private/author-name",),
        language="",
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes(metadata=metadata))
    persisted = _persisted_document(source, metadata=metadata)
    persisted["metadata"].update(
        {
            "author": "Safe Fallback Author",
            "book_language": {"language": "en"},
            "output_language": ["en"],
        }
    )

    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    assert result.wire["dc:creator"] == ["Safe Fallback Author"]
    rebuilt_metadata = result.rebuilt_book_document["metadata"]
    assert rebuilt_metadata["book_language"] == "und"
    assert rebuilt_metadata["output_language"] == "und"
    serialized = json.dumps(
        {"wire": result.wire, "rebuilt": result.rebuilt_book_document},
        ensure_ascii=False,
        sort_keys=True,
    )
    assert "/Users/private" not in serialized
    assert "{'language': 'en'}" not in serialized
    assert "['en']" not in serialized
    assert any(
        finding.code == "invalid_publication_metadata"
        and finding.json_pointer == "/about/dc:creator"
        for finding in result.findings
    )

    no_creator_metadata = FixtureMetadata(creators=())
    no_creator_dir = tmp_path / "no-creator"
    no_creator_source = _write_source(
        no_creator_dir,
        build_epub_bytes(metadata=no_creator_metadata),
    )
    no_creator_persisted = _persisted_document(
        no_creator_source,
        metadata=no_creator_metadata,
    )
    no_creator_persisted["metadata"]["author"] = "By /etc/passwd"
    no_creator = PublicationIdentityBuilder().build(
        output_dir=no_creator_dir,
        persisted_book_document=no_creator_persisted,
    )
    assert "dc:creator" not in no_creator.wire
    assert no_creator.rebuilt_book_document["metadata"]["author"] == ""
    assert any(
        finding.code == "invalid_persisted_metadata_fallback"
        and finding.json_pointer == "/metadata/author"
        for finding in no_creator.findings
    )


@pytest.mark.parametrize(
    "value",
    [
        "By /secret",
        "Path (/secret)",
        "Author:/etc/passwd",
        "By /Volumes/Private/book",
        r"Author:C:\secret",
        r"Path(C:\secret)",
        r"Path(\\server\share)",
        "By ~/secret",
        "Path(~/secret)",
        "Author:file:///etc/passwd",
        "P#file:///etc/passwd",
        "P[~/secret]",
        r"P{C:\secret}",
        r"P[\\server\share]",
        "P[token=sekrit]",
        "Path[runs/alice/session.sqlite]",
        "Path{_assets/source.epub}",
        "Ref(state/uploads/book.json)",
        "Ref#../private/source.epub",
        "note %252FUsers%252Falice%252Fsecret.epub",
        "api_key%253Dsekrit",
        "api_key=sekrit",
        "token=sekrit",
        "By %2FUsers%2Fprivate%2Fauthor",
        "Author\u202eprivate",
    ],
)
def test_public_display_metadata_rejects_embedded_absolute_paths(value: str) -> None:
    assert not identity_module._is_public_display_metadata(value)


@pytest.mark.parametrize(
    "value",
    [
        "AC/DC",
        "Alice / Bob",
        "https://example.org/creators/alice",
    ],
)
def test_public_display_metadata_keeps_nonpath_slashes(value: str) -> None:
    assert identity_module._is_public_display_metadata(value)


def json_string(value: str) -> bytes:
    return ('"' + value + '"').encode()
