"""Tests for the shared sentence-layer helpers."""

from __future__ import annotations

from src.reading_core.sentences import build_sentence_records, split_text_into_sentence_spans


def test_split_text_into_sentence_spans_handles_mixed_english_and_cjk_punctuation():
    """Sentence spans should split on both whitespace-delimited and CJK terminal marks."""

    spans = split_text_into_sentence_spans('Alpha opens. "Beta follows?" 然后继续。最后一句！')

    assert [span["text"] for span in spans] == [
        "Alpha opens.",
        '"Beta follows?"',
        "然后继续。",
        "最后一句！",
    ]
    assert spans[1]["char_start"] == 13
    assert spans[1]["char_end"] == 28


def test_build_sentence_records_skips_auxiliary_but_preserves_heading_and_body_order():
    """Sentence records should preserve chapter-local order over non-auxiliary text blocks."""

    records = build_sentence_records(
        [
            {
                "text": "CHAPTER 1",
                "paragraph_index": 1,
                "text_role": "chapter_heading",
                "href": "chapter-1.xhtml",
                "start_cfi": "epubcfi(/6/4[chapter-1]!/4/2)",
                "end_cfi": "epubcfi(/6/4[chapter-1]!/4/2)",
            },
            {
                "text": "People want things from other people. This is why the market matters.",
                "paragraph_index": 2,
                "text_role": "body",
                "href": "chapter-1.xhtml",
                "start_cfi": "epubcfi(/6/4[chapter-1]!/4/4)",
                "end_cfi": "epubcfi(/6/4[chapter-1]!/4/4)",
            },
            {
                "text": "Illustration credit",
                "paragraph_index": 3,
                "text_role": "auxiliary",
                "href": "chapter-1.xhtml",
                "start_cfi": "epubcfi(/6/4[chapter-1]!/4/6)",
                "end_cfi": "epubcfi(/6/4[chapter-1]!/4/6)",
            },
        ],
        chapter_id=1,
    )

    assert [record["sentence_id"] for record in records] == ["c1-s1", "c1-s2", "c1-s3"]
    assert [record["text"] for record in records] == [
        "CHAPTER 1",
        "People want things from other people.",
        "This is why the market matters.",
    ]
    assert [record["text_role"] for record in records] == [
        "chapter_heading",
        "body",
        "body",
    ]
    assert records[1]["locator"]["paragraph_index"] == 2
    assert records[2]["locator"]["char_start"] > records[1]["locator"]["char_end"]
