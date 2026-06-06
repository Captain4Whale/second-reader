from __future__ import annotations

import json

from src.attentional_v2.source_spans import (
    build_paragraph_offset_preview,
    first_cursor_for_chapter,
    resolve_end_anchor_text,
    source_ref_from_unit,
    source_unit_from_span,
)
from src.attentional_v2.storage import initialize_artifact_tree, unit_span_ledger_file
from src.attentional_v2.unit_span_ledger import append_unit_span_record


def _chapter() -> dict[str, object]:
    return {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "Alpha " * 20, "text_role": "body"},
            {"paragraph_index": 2, "text": "Beta bridge.", "text_role": "body"},
            {"paragraph_index": 3, "text": "Gamma closing.", "text_role": "body"},
        ],
    }


def test_preview_keeps_long_current_paragraph_only() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 20, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    assert preview["paragraph_count"] == 1
    assert preview["preview_end_cursor"]["paragraph_index"] == 1
    assert preview["truncated"] is False


def test_preview_appends_following_paragraphs_when_current_remainder_is_short() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 5},
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    assert preview["paragraph_count"] == 2
    assert preview["paragraph_slices"][0]["text"] == "bridge."
    assert preview["preview_end_cursor"]["paragraph_index"] == 3


def test_preview_truncates_at_hard_max_with_end_exclusive_cursor() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=first_cursor_for_chapter(chapter),
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 10, "max_lookahead_paragraphs": 4}},
    )

    assert preview["source_text"] == "Alpha Alph"
    assert preview["preview_end_cursor"]["char_offset"] == 10
    assert preview["truncated"] is True


def test_resolver_maps_end_anchor_to_paragraph_offset_cursor() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    resolution = resolve_end_anchor_text(preview=preview, end_anchor_text="Beta bridge.")

    assert resolution["status"] == "matched"
    assert resolution["end_cursor"]["paragraph_index"] == 2
    assert resolution["end_cursor"]["char_offset"] == len("Beta bridge.")


def test_resolver_matches_anchor_with_equivalent_quote_marks() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "”", "text_role": "body"},
            {"paragraph_index": 2, "text": "“看！”悉达多轻声对乔文达道，“此人就是佛陀。”", "text_role": "body"},
        ],
    }
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 1},
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    resolution = resolve_end_anchor_text(
        preview=preview,
        end_anchor_text='"看！"悉达多轻声对乔文达道，"此人就是佛陀。"',
    )

    assert resolution["status"] == "matched"
    assert resolution["method"] == "normalized_exact_text"
    assert resolution["normalization"] == "quote_equivalence"
    assert resolution["matched_text"] == "“看！”悉达多轻声对乔文达道，“此人就是佛陀。”"
    assert resolution["end_cursor"]["paragraph_index"] == 2
    assert resolution["end_cursor"]["char_offset"] == len("“看！”悉达多轻声对乔文达道，“此人就是佛陀。”")


def test_resolver_includes_adjacent_trailing_closing_quote() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "“在水面行走并不是我的追求。”", "text_role": "body"},
        ],
    }
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 20, "preview_hard_max_chars": 100, "max_lookahead_paragraphs": 1}},
    )

    resolution = resolve_end_anchor_text(
        preview=preview,
        end_anchor_text="在水面行走并不是我的追求。",
    )

    assert resolution["status"] == "matched"
    assert resolution["method"] == "exact_text"
    assert resolution["matched_text"] == "在水面行走并不是我的追求。”"
    assert resolution["end_cursor_extension"] == {
        "kind": "trailing_closing_punctuation",
        "text": "”",
    }
    assert resolution["end_cursor"]["char_offset"] == len("“在水面行走并不是我的追求。”")


def test_resolver_reports_ambiguous_and_missing_anchor() -> None:
    preview = {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "preview_start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        "preview_end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 10},
        "source_text": "echo echo",
        "paragraph_slices": [{"paragraph_index": 1, "start_char": 0, "end_char": 9, "flat_start": 0, "flat_end": 9}],
    }

    assert resolve_end_anchor_text(preview=preview, end_anchor_text="echo")["status"] == "ambiguous"
    assert resolve_end_anchor_text(preview=preview, end_anchor_text="missing")["status"] == "not_found"


def test_unit_span_ledger_records_core_runtime_fact(tmp_path) -> None:
    output_dir = tmp_path / "out" / "book"
    initialize_artifact_tree(output_dir)
    chapter = _chapter()
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": len("Beta bridge.")},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)
    preview = build_paragraph_offset_preview(chapter=chapter, current_cursor=span["start_cursor"])

    append_unit_span_record(
        output_dir,
        chapter_id=1,
        chapter_ref="Chapter 1",
        source_unit=source_unit,
        preview=preview,
        end_anchor_text="Beta bridge.",
        resolution={"status": "matched", "method": "exact_text"},
    )

    record = json.loads(unit_span_ledger_file(output_dir).read_text(encoding="utf-8").strip())
    assert record["unit_id"] == "u000001"
    assert record["start_cursor"] == span["start_cursor"]
    assert record["end_cursor"] == span["end_cursor"]
    assert record["source_span_id"].startswith("src:c1:p2@0-p2@")


def test_source_ref_from_unit_resolves_single_paragraph_quote() -> None:
    chapter = _chapter()
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 3, "char_offset": len("Gamma closing.")},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)

    source_ref = source_ref_from_unit(source_unit, quote="bridge.", role="reaction_anchor")

    assert source_ref["source_span_id"] == "src:c1:p2@5-p2@12"
    assert source_ref["quote"] == "bridge."
    assert source_ref["role"] == "reaction_anchor"
    assert source_ref["resolution"]["status"] == "matched"


def test_source_ref_from_unit_resolves_cross_paragraph_quote() -> None:
    chapter = _chapter()
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 3, "char_offset": len("Gamma closing.")},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)

    source_ref = source_ref_from_unit(source_unit, quote="bridge.\n\nGamma", role="support")

    assert source_ref["source_span_id"] == "src:c1:p2@5-p3@5"
    assert source_ref["resolution"]["status"] == "matched"


def test_source_ref_from_unit_resolves_normalized_quote() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [{"paragraph_index": 1, "text": "他说：“能学会。”", "text_role": "body"}],
    }
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": len("他说：“能学会。”")},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)

    source_ref = source_ref_from_unit(source_unit, quote='他说:"能学会."', role="support")

    assert source_ref["source_span_id"] == f"src:c1:p1@0-p1@{len('他说：“能学会。”')}"
    assert source_ref["resolution"]["status"] == "matched"
    assert source_ref["resolution"]["method"] == "normalized_exact_text"


def test_source_ref_from_unit_resolves_ordered_fragment_quote() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {
                "paragraph_index": 1,
                "text": "有人夺走死者剩下的土豆泥；有人认为木鞋更好；有人换走死者的上衣；连只拿到细绳的人都会沾沾自喜。",
                "text_role": "body",
            }
        ],
    }
    text = str(chapter["paragraphs"][0]["text"])
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": len(text)},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)

    source_ref = source_ref_from_unit(
        source_unit,
        quote="有人夺走死者剩下的土豆泥；有人换走死者的上衣；连只拿到细绳的人都会沾沾自喜",
        role="answer_support",
    )

    expected_end = text.find("连只拿到细绳的人都会沾沾自喜") + len("连只拿到细绳的人都会沾沾自喜")
    assert source_ref["source_span_id"] == f"src:c1:p1@0-p1@{expected_end}"
    assert source_ref["resolution"]["status"] == "ordered_fragment_match"
    assert source_ref["resolution"]["method"] == "ordered_fragment_text"
    assert source_ref["resolution"]["fragment_count"] == 3


def test_source_ref_from_unit_marks_repeated_quote_and_missing_quote_fallback() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [{"paragraph_index": 1, "text": "echo echo", "text_role": "body"}],
    }
    span = {
        "start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        "end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": len("echo echo")},
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=span)

    repeated = source_ref_from_unit(source_unit, quote="echo", role="support")
    missing = source_ref_from_unit(source_unit, quote="absent", role="support")
    empty = source_ref_from_unit(source_unit, quote="", role="support")

    assert repeated["source_span_id"] == "src:c1:p1@0-p1@4"
    assert repeated["resolution"]["status"] == "ambiguous_first_match"
    assert missing["source_span_id"] == "src:c1:p1@0-p1@9"
    assert missing["resolution"]["method"] == "quote_not_found"
    assert empty["quote"] == "echo echo"
    assert empty["resolution"]["method"] == "missing_quote"
