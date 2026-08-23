"""Neutral EPUB-to-BookDocument extraction and compatibility tests."""

from __future__ import annotations

from src.iterator_reader import parse as iterator_parse
from src.iterator_reader import storage as iterator_storage
from src.parsers import ebook_parser
from src.reading_core import epub_document


def _raw_chapters() -> list[dict[str, object]]:
    return [
        {
            "title": "Chapter 7",
            "content": """
<html xmlns="http://www.w3.org/1999/xhtml">
  <body>
    <h1>CHAPTER 7</h1>
    <p id="opening">Alpha opens the chapter.</p>
    <p>Beta extends the argument.</p>
  </body>
</html>
""",
            "level": 2,
            "item_id": "chapter-7",
            "href": "text/chapter-7.xhtml",
            "spine_index": 1,
        },
        {
            "title": "Copyright",
            "content": "<p>Copyright notice.</p>",
            "level": 1,
            "item_id": "copyright",
            "href": "text/copyright.xhtml",
            "spine_index": 0,
        },
    ]


def test_iterator_parser_reexports_one_neutral_implementation() -> None:
    assert iterator_parse.build_book_document_from_chapters is (
        epub_document.build_book_document_from_chapters
    )
    assert iterator_parse._build_book_document is (
        epub_document.build_book_document_from_chapters
    )
    assert iterator_storage.infer_chapter_number is epub_document.infer_chapter_number
    assert iterator_parse.infer_chapter_number is epub_document.infer_chapter_number

    compatibility_names = (
        "SKIP_TITLES",
        "LOW_VALUE_SEGMENT_KEYWORDS",
        "BLOCK_TAGS",
        "HEADING_TAGS",
        "CHAPTER_LABEL_PATTERNS",
        "AUXILIARY_KEYWORDS",
        "extract_plain_text",
        "split_into_paragraphs",
        "_normalize_block_text",
        "_local_tag",
        "_element_attr",
        "_heading_level_for_tag",
        "_direct_text_content",
        "_has_textual_block_children",
        "_bounded_unique",
        "_split_class_tokens",
        "_inline_anchor_metadata",
        "_ancestor_context_for_child",
        "_looks_like_sentence",
        "_upper_ratio",
        "_looks_like_chapter_label",
        "_looks_like_auxiliary_text",
        "_looks_like_heading_text",
        "_cfi_for_element",
        "_extract_epub_paragraph_records",
        "_paragraph_records",
        "_classify_paragraph_records",
        "_chapter_heading_block",
        "_segment_locator_from_records",
        "_should_skip_chapter",
    )
    for name in compatibility_names:
        assert getattr(iterator_parse, name) is getattr(epub_document, name)


def test_build_book_document_is_no_write_and_preserves_shape(tmp_path) -> None:
    source_file = str(tmp_path / "original source.epub")
    before = tuple(tmp_path.rglob("*"))

    document = epub_document.build_book_document_from_chapters(
        _raw_chapters(),
        title="Fixture Book",
        author="Fixture Author",
        book_language="en",
        output_language="zh",
        source_file=source_file,
    )

    assert tuple(tmp_path.rglob("*")) == before
    assert document["metadata"] == {
        "book": "Fixture Book",
        "author": "Fixture Author",
        "book_language": "en",
        "output_language": "zh",
        "source_file": source_file,
    }
    assert len(document["chapters"]) == 1
    chapter = document["chapters"][0]
    assert {
        "id": chapter["id"],
        "title": chapter["title"],
        "chapter_number": chapter["chapter_number"],
        "level": chapter["level"],
        "item_id": chapter["item_id"],
        "href": chapter["href"],
        "spine_index": chapter["spine_index"],
    } == {
        "id": 1,
        "title": "Chapter 7",
        "chapter_number": 7,
        "level": 2,
        "item_id": "chapter-7",
        "href": "text/chapter-7.xhtml",
        "spine_index": 1,
    }
    assert [record["text"] for record in chapter["paragraphs"]] == [
        "CHAPTER 7",
        "Alpha opens the chapter.",
        "Beta extends the argument.",
    ]
    assert [record["text_role"] for record in chapter["paragraphs"]] == [
        "chapter_heading",
        "body",
        "body",
    ]
    assert chapter["chapter_heading"] == {
        "title": "CHAPTER 7",
        "text": "CHAPTER 7",
        "locator": {
            "href": "text/chapter-7.xhtml",
            "start_cfi": "epubcfi(/6/4[chapter-7]!/4/2/2)",
            "end_cfi": "epubcfi(/6/4[chapter-7]!/4/2/2)",
            "paragraph_start": 1,
            "paragraph_end": 1,
        },
    }
    assert [record["sentence_id"] for record in chapter["sentences"]] == [
        "c1-s1",
        "c1-s2",
        "c1-s3",
    ]


def test_spine_zero_legacy_behavior_is_observed_without_repair() -> None:
    raw = _raw_chapters()[0]
    raw["spine_index"] = 0
    document = epub_document.build_book_document_from_chapters(
        [raw],
        title="Fixture Book",
        author="Fixture Author",
        book_language="en",
        output_language="en",
        source_file="_assets/source.epub",
    )

    chapter = document["chapters"][0]
    assert chapter["spine_index"] == 0
    # Existing paragraph extraction uses ``int(value or -1)``.  Slice 2 must
    # preserve that behavior while moving the implementation; it does not claim
    # that optional CFI generation for spine item zero has been repaired.
    assert [paragraph["spine_index"] for paragraph in chapter["paragraphs"]] == [
        -1,
        -1,
        -1,
    ]
    assert all(
        paragraph["start_cfi"] is None and paragraph["end_cfi"] is None
        for paragraph in chapter["paragraphs"]
    )


def test_fragment_toc_duplicate_behavior_is_observed_without_repair() -> None:
    class TocLink:
        def __init__(self, title: str, href: str) -> None:
            self.title = title
            self.href = href

    class EpubItem:
        def get_name(self) -> str:
            return "Text/shared.xhtml"

        def get_id(self) -> str:
            return "shared"

        def get_content(self) -> bytes:
            return b"<html><body><p>Shared chapter body.</p></body></html>"

    chapters = ebook_parser._extract_epub_chapters_from_toc(
        [
            TocLink("First Fragment", "Text/shared.xhtml#first"),
            TocLink("Second Fragment", "Text/shared.xhtml#second"),
        ],
        {"shared": EpubItem()},
        {"shared": 0},
    )

    # The existing parser creates two chapter rows over the same XHTML.  Slice 2
    # observes this segmentation debt and fingerprints the canonical output; it
    # does not silently merge chapters or change normal reading behavior.
    assert [chapter["title"] for chapter in chapters] == [
        "First Fragment",
        "Second Fragment",
    ]
    assert [chapter["href"] for chapter in chapters] == [
        "Text/shared.xhtml",
        "Text/shared.xhtml",
    ]
