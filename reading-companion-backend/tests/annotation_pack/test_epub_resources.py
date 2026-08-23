from __future__ import annotations

from contextlib import AbstractContextManager
from copy import deepcopy
from pathlib import Path
from typing import BinaryIO

import pytest

import src.annotation_pack.epub_resources as epub_resources_module
from src.annotation_pack.epub_resources import (
    EpubManifestIndex,
    EpubResourceIndex,
    RESOURCE_TEXT_NORMALIZATION_VERSION,
    build_epub_manifest_index,
    build_epub_resource_index,
)
from src.annotation_pack.epub_source import VerifiedEpubSource, verify_epub_source
from src.annotation_pack.identity import PublicationIdentityBuilder
from src.parsers import parse_ebook
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_runtime.source_normalization import normalize_book_document_source
from tests.annotation_pack.epub_factory import (
    DEFAULT_CHAPTERS,
    FixtureChapter,
    FixtureZipEntry,
    build_epub_bytes,
    fixture_entries,
)


def _write_source(output_dir: Path, content: bytes) -> Path:
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    return source


def _persisted_document(source: Path) -> dict[str, object]:
    canonical = build_book_document_from_chapters(
        list(parse_ebook(str(source))),
        title="The Returning Question",
        author="Second Reader Fixture Authors",
        book_language="en",
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


def test_identity_builds_fixed_resource_text_and_paragraph_range_vectors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes())
    persisted = _persisted_document(source)
    open_calls = 0
    original_open_verified = VerifiedEpubSource.open_verified

    def tracked_open_verified(
        self: VerifiedEpubSource,
    ) -> AbstractContextManager[BinaryIO]:
        nonlocal open_calls
        open_calls += 1
        return original_open_verified(self)

    monkeypatch.setattr(VerifiedEpubSource, "open_verified", tracked_open_verified)
    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )

    assert open_calls == 1
    assert isinstance(result.epub_index, EpubResourceIndex)
    assert RESOURCE_TEXT_NORMALIZATION_VERSION == "sr-epub-resource-text-v1"
    chapter_one_text = (
        "A Small Beginning\n\n"
        "The reader paused before the margin.\n\n"
        "A durable idea is worth returning to.\n\n"
        "Return with a better question, and the page may answer differently."
    )
    chapter_two_text = (
        "The Question Returns\n\n"
        "Morning light crossed the notes without changing their words.\n\n"
        "What changed was the reader who met them again."
    )
    assert dict(result.epub_index.resource_texts) == {
        "Text/chapter-01.xhtml": chapter_one_text,
        "Text/chapter-02.xhtml": chapter_two_text,
    }
    assert dict(result.epub_index.paragraph_ranges) == {
        (1, 1): ("Text/chapter-01.xhtml", 0, 17),
        (1, 2): ("Text/chapter-01.xhtml", 19, 55),
        (1, 3): ("Text/chapter-01.xhtml", 57, 94),
        (1, 4): ("Text/chapter-01.xhtml", 96, 163),
        (2, 1): ("Text/chapter-02.xhtml", 0, 20),
        (2, 2): ("Text/chapter-02.xhtml", 22, 83),
        (2, 3): ("Text/chapter-02.xhtml", 85, 132),
    }
    assert result.epub_index.unverifiable_hrefs == frozenset()

    for chapter in result.rebuilt_book_document["chapters"]:  # type: ignore[index]
        chapter_id = chapter["id"]
        for paragraph in chapter["paragraphs"]:
            href, start, end = result.epub_index.paragraph_ranges[
                (chapter_id, paragraph["paragraph_index"])
            ]
            assert result.epub_index.resource_texts[href][start:end] == paragraph["text"]


def test_resource_text_uses_python_whitespace_without_nfc_and_skips_duplicate_containers(
    tmp_path: Path,
) -> None:
    chapter = FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="Structured text",
        paragraphs=("fixture placeholder",),
    )
    xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Safe</title></head>'
        "<body><div><p>Cafe\u0301\tline\n break</p>"
        "<blockquote><p>Nested\u2003leaf</p></blockquote></div></body></html>"
    ).encode()
    content = build_epub_bytes(
        chapters=(chapter,),
        replace_entries=(
            FixtureZipEntry("EPUB/Text/chapter-01.xhtml", xhtml),
        ),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, content)
    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=_persisted_document(source),
    )

    resource_text = result.epub_index.resource_texts["Text/chapter-01.xhtml"]
    assert resource_text == "Cafe\u0301 line break\n\nNested leaf"
    assert "Caf\u00e9" not in resource_text
    assert len(result.epub_index.paragraph_ranges) == 2
    assert result.epub_index.unverifiable_hrefs == frozenset()


@pytest.mark.parametrize(
    "unsafe_xhtml",
    [
        b"<html><body><p>Broken",
        (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE html [<!ENTITY private SYSTEM "file:///etc/passwd">]>'
            b"<html><body><p>&private;</p></body></html>"
        ),
        b"<svg xmlns=\"http://www.w3.org/2000/svg\"><text>Wrong root</text></svg>",
    ],
)
def test_unsafe_resource_xml_is_unverifiable_without_plaintext_fallback(
    tmp_path: Path,
    unsafe_xhtml: bytes,
) -> None:
    content = build_epub_bytes(
        replace_entries=(
            FixtureZipEntry("EPUB/Text/chapter-01.xhtml", unsafe_xhtml),
        ),
    )
    output_dir = tmp_path / "book"
    _write_source(output_dir, content)
    verified = verify_epub_source(output_dir)
    book_document = {
        "chapters": [
            {
                "id": 1,
                "href": "Text/chapter-01.xhtml",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "href": "Text/chapter-01.xhtml",
                        "text": "Broken",
                    }
                ],
            }
        ]
    }

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document=book_document,
        )

    assert "Text/chapter-01.xhtml" in index.unverifiable_hrefs
    assert "Text/chapter-01.xhtml" not in index.resource_texts
    assert (1, 1) not in index.paragraph_ranges
    assert "/etc/passwd" not in repr(index)


def test_exact_resource_parse_with_book_document_mismatch_is_unverifiable(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    _write_source(output_dir, build_epub_bytes())
    verified = verify_epub_source(output_dir)
    mismatched = {
        "chapters": [
            {
                "id": 1,
                "href": "Text/chapter-01.xhtml",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "href": "Text/chapter-01.xhtml",
                        "text": "A Small Beginning",
                    },
                    {
                        "paragraph_index": 2,
                        "href": "Text/chapter-01.xhtml",
                        "text": "Not the exact second resource block.",
                    },
                ],
            }
        ]
    }

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document=mismatched,
        )

    assert "Text/chapter-01.xhtml" in index.resource_texts
    assert index.unverifiable_hrefs == frozenset({"Text/chapter-01.xhtml"})
    assert index.paragraph_ranges == {}


@pytest.mark.parametrize("nested_tag", ["div", "span"])
def test_resource_xml_depth_gate_runs_before_descendant_text_traversal(
    tmp_path: Path,
    nested_tag: str,
) -> None:
    depth = epub_resources_module.MAX_RESOURCE_XML_DEPTH + 1
    xhtml = (
        "<html><body>"
        + f"<{nested_tag}>" * depth
        + "<p>Bounded text</p>"
        + f"</{nested_tag}>" * depth
        + "</body></html>"
    ).encode()
    content = build_epub_bytes(
        replace_entries=(
            FixtureZipEntry("EPUB/Text/chapter-01.xhtml", xhtml),
        ),
    )
    output_dir = tmp_path / f"book-{nested_tag}"
    _write_source(output_dir, content)
    verified = verify_epub_source(output_dir)
    document = {
        "chapters": [
            {
                "id": 1,
                "href": "Text/chapter-01.xhtml",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "href": "Text/chapter-01.xhtml",
                        "text": "Bounded text",
                    }
                ],
            }
        ]
    }

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document=document,
        )

    assert index.unverifiable_hrefs == frozenset({"Text/chapter-01.xhtml"})
    assert "Text/chapter-01.xhtml" not in index.resource_texts


def test_resource_xml_element_count_gate_is_enforced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(epub_resources_module, "MAX_RESOURCE_XML_ELEMENTS", 8)
    xhtml = (
        "<html><body>"
        + "".join(f"<span>{index}</span>" for index in range(8))
        + "<p>Bounded text</p></body></html>"
    ).encode()
    content = build_epub_bytes(
        replace_entries=(
            FixtureZipEntry("EPUB/Text/chapter-01.xhtml", xhtml),
        ),
    )
    output_dir = tmp_path / "book"
    _write_source(output_dir, content)
    verified = verify_epub_source(output_dir)

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document={"chapters": []},
        )

    assert index.unverifiable_hrefs == frozenset({"Text/chapter-01.xhtml"})
    assert "Text/chapter-01.xhtml" not in index.resource_texts


@pytest.mark.parametrize(
    ("direct_text", "expected_unverifiable"),
    [("", False), ("x", True)],
)
def test_resource_text_traversal_budget_bounds_nested_included_blocks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    direct_text: str,
    expected_unverifiable: bool,
) -> None:
    monkeypatch.setattr(
        epub_resources_module,
        "MAX_RESOURCE_TEXT_TRAVERSAL_CODEPOINTS",
        100,
    )
    leaf = "y" * 64
    depth = 8
    xhtml = (
        "<html><body>"
        + (f"<div>{direct_text}" * depth)
        + f"<p>{leaf}</p>"
        + ("</div>" * depth)
        + "</body></html>"
    ).encode()
    chapter = FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="Bounded",
        paragraphs=(leaf,),
    )
    content = build_epub_bytes(
        chapters=(chapter,),
        replace_entries=(
            FixtureZipEntry("EPUB/Text/chapter-01.xhtml", xhtml),
        ),
    )
    output_dir = tmp_path / ("included" if direct_text else "duplicate")
    _write_source(output_dir, content)
    verified = verify_epub_source(output_dir)
    document = {
        "chapters": [
            {
                "id": 1,
                "href": "Text/chapter-01.xhtml",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "href": "Text/chapter-01.xhtml",
                        "text": leaf,
                    }
                ],
            }
        ]
    }

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document=document,
        )

    assert ("Text/chapter-01.xhtml" in index.unverifiable_hrefs) is (
        expected_unverifiable
    )
    if not expected_unverifiable:
        assert index.resource_texts["Text/chapter-01.xhtml"] == leaf


def test_raw_markup_gate_rejects_before_element_tree_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chapter = FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="Bounded",
        paragraphs=("Text",),
    )
    content = build_epub_bytes(chapters=(chapter,))
    output_dir = tmp_path / "book"
    _write_source(output_dir, content)
    verified = verify_epub_source(output_dir)
    monkeypatch.setattr(
        epub_resources_module,
        "MAX_RESOURCE_XML_MARKUP_DELIMITERS",
        4,
    )

    def unexpected_parse(_content: bytes) -> object:
        raise AssertionError("ElementTree parse must not run after raw markup gate")

    monkeypatch.setattr(epub_resources_module.ET, "fromstring", unexpected_parse)

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document={"chapters": []},
        )

    assert index.unverifiable_hrefs == frozenset({"Text/chapter-01.xhtml"})


def test_resource_index_rejects_a_manifest_not_derived_from_the_verified_source(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    _write_source(output_dir, build_epub_bytes())
    verified = verify_epub_source(output_dir)
    actual = build_epub_manifest_index(verified)
    forged = EpubManifestIndex(
        opf_path=actual.opf_path,
        manifest_hrefs=actual.manifest_hrefs,
        text_resource_hrefs=frozenset(),
    )

    with verified.open_verified() as handle:
        with pytest.raises(
            epub_resources_module.EpubResourceIndexError
        ) as raised:
            build_epub_resource_index(
                source=verified,
                source_handle=handle,
                rebuilt_book_document={"chapters": []},
                manifest=forged,
            )

    assert raised.value.code == "invalid_epub_manifest_index"
    assert str(tmp_path) not in str(raised.value)


def test_resource_index_reads_the_verified_handle_during_path_swap(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    original_bytes = build_epub_bytes()
    source = _write_source(output_dir, original_bytes)
    book_document = _persisted_document(source)
    verified = verify_epub_source(output_dir)

    replacement_chapters = (
        FixtureChapter(
            item_id=DEFAULT_CHAPTERS[0].item_id,
            href=DEFAULT_CHAPTERS[0].href,
            title=DEFAULT_CHAPTERS[0].title,
            paragraphs=("Transient replacement text.",),
        ),
        DEFAULT_CHAPTERS[1],
    )
    replacement_assets = output_dir / "_replacement_assets"
    replacement_assets.mkdir()
    (replacement_assets / "source.epub").write_bytes(
        build_epub_bytes(chapters=replacement_chapters)
    )
    original_assets = output_dir / "_assets"
    parked_assets = output_dir / "_parked_assets"

    with verified.open_verified() as handle:
        original_assets.rename(parked_assets)
        replacement_assets.rename(original_assets)
        try:
            index = build_epub_resource_index(
                source=verified,
                source_handle=handle,
                rebuilt_book_document=book_document,
                manifest=build_epub_manifest_index(verified),
            )
        finally:
            original_assets.rename(replacement_assets)
            parked_assets.rename(original_assets)

    assert "Transient replacement text." not in index.resource_texts[
        "Text/chapter-01.xhtml"
    ]
    assert "A durable idea is worth returning to." in index.resource_texts[
        "Text/chapter-01.xhtml"
    ]
    assert index.unverifiable_hrefs == frozenset()


@pytest.mark.parametrize(
    ("encoded_name", "archive_name"),
    [("a%23b.xhtml", "a#b.xhtml"), ("a%3Fb.xhtml", "a?b.xhtml")],
)
def test_resource_index_keeps_canonical_href_for_reserved_archive_filename(
    tmp_path: Path,
    encoded_name: str,
    archive_name: str,
) -> None:
    base = DEFAULT_CHAPTERS[0]
    chapter = FixtureChapter(
        item_id=base.item_id,
        href=f"Text/{encoded_name}",
        title=base.title,
        paragraphs=base.paragraphs,
    )
    xhtml = fixture_entries(chapters=(chapter,))[-1].data
    content = build_epub_bytes(
        chapters=(chapter,),
        omit_entries=(f"EPUB/Text/{encoded_name}",),
        extra_entries=(FixtureZipEntry(f"EPUB/Text/{archive_name}", xhtml),),
    )
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, content)
    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=_persisted_document(source),
    )

    canonical_href = f"Text/{encoded_name}"
    assert set(result.epub_index.resource_texts) == {canonical_href}
    assert {
        value[0] for value in result.epub_index.paragraph_ranges.values()
    } == {canonical_href}
    assert result.epub_index.unverifiable_hrefs == frozenset()


def test_duplicate_chapter_projection_maps_each_chapter_to_the_same_resource(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes())
    persisted = _persisted_document(source)
    first = deepcopy(persisted["chapters"][0])  # type: ignore[index]
    duplicate = deepcopy(first)
    duplicate["id"] = 99
    duplicate_document = {"chapters": [first, duplicate]}
    verified = verify_epub_source(output_dir)

    with verified.open_verified() as handle:
        index = build_epub_resource_index(
            source=verified,
            source_handle=handle,
            rebuilt_book_document=duplicate_document,
        )

    assert index.paragraph_ranges[(1, 3)] == (
        "Text/chapter-01.xhtml",
        57,
        94,
    )
    assert index.paragraph_ranges[(99, 3)] == (
        "Text/chapter-01.xhtml",
        57,
        94,
    )
    assert index.unverifiable_hrefs == frozenset()


def test_resource_index_is_deeply_read_only_and_repr_hides_prose_and_local_path(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "private-book-location"
    source = _write_source(output_dir, build_epub_bytes())
    result = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=_persisted_document(source),
    )
    index = result.epub_index

    with pytest.raises(TypeError):
        index.resource_texts["Text/chapter-01.xhtml"] = "changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        index.paragraph_ranges[(1, 1)] = ("Text/chapter-01.xhtml", 0, 1)  # type: ignore[index]
    with pytest.raises(AttributeError):
        index.unverifiable_hrefs.add("Text/chapter-01.xhtml")  # type: ignore[attr-defined]

    rendered = repr(index)
    assert "A durable idea is worth returning to." not in rendered
    assert str(tmp_path) not in rendered
    assert "source.epub" not in rendered
    result_rendered = repr(result)
    assert "A durable idea is worth returning to." not in result_rendered
    assert str(tmp_path) not in result_rendered
