from __future__ import annotations

import json

from src.attentional_v2.source_spans import (
    build_paragraph_offset_preview,
    first_cursor_for_chapter,
    resolve_end_anchor_text,
    resolve_ingest_unit_boundary,
    resolve_preview_partition_audit,
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


def test_default_preview_uses_token_budget_not_paragraph_count() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": index, "text": f"Paragraph {index}.", "text_role": "body"}
            for index in range(1, 20)
        ],
    }

    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
    )

    assert preview["paragraph_count"] == 19
    assert preview["paragraph_slices"][-1]["paragraph_index"] == 19
    assert preview["preview_end_cursor"]["paragraph_index"] == 19
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "source_tail"
    assert preview["estimated_token_count"] > 0
    assert preview["preview_token_estimator"] == "tiktoken_o200k_base_v1_paragraph_xml_v1"


def test_preview_stops_at_target_max_after_soft_min_is_satisfied() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": index, "text": "汉" * 50, "text_role": "body"}
            for index in range(1, 20)
        ],
    }

    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={
            "unitize": {
                "preview_soft_min_tokens": 80,
                "preview_target_max_tokens": 140,
                "preview_hard_max_tokens": 220,
            }
        },
    )

    assert preview["paragraph_count"] == 1
    assert preview["estimated_token_count"] >= 80
    assert preview["estimated_token_count"] <= 140
    assert preview["preview_end_cursor"] == {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "paragraph_index": 1,
        "char_offset": 50,
    }
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "target_max"


def test_preview_stops_at_hard_max_before_candidate_paragraph_would_exceed_it() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": index, "text": "汉" * 80, "text_role": "body"}
            for index in range(1, 5)
        ],
    }

    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={
            "unitize": {
                "preview_soft_min_tokens": 80,
                "preview_target_max_tokens": 140,
                "preview_hard_max_tokens": 220,
            }
        },
    )

    assert preview["paragraph_count"] == 1
    assert preview["char_count"] == 80
    assert preview["source_text"] == "汉" * 80
    assert preview["preview_end_cursor"] == {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "paragraph_index": 1,
        "char_offset": 80,
    }
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "hard_max"
    assert preview["estimated_token_count"] <= 220


def test_preview_truncates_current_paragraph_at_hard_token_max() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "汉" * 8000, "text_role": "body"},
            {"paragraph_index": 2, "text": "Next paragraph.", "text_role": "body"},
        ],
    }

    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
    )

    assert preview["paragraph_count"] == 1
    assert 0 < preview["char_count"] < 8000
    assert preview["source_text"] == "汉" * int(preview["char_count"])
    assert preview["preview_end_cursor"] == {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "paragraph_index": 1,
        "char_offset": preview["char_count"],
    }
    assert preview["truncated"] is True
    assert preview["preview_end_reason"] == "hard_max"
    assert preview["estimated_token_count"] <= 2600


def test_preview_ignores_deprecated_max_lookahead_and_char_limits() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 10, "max_lookahead_paragraphs": 1}},
    )

    assert preview["paragraph_count"] == 3
    assert preview["preview_end_cursor"]["paragraph_index"] == 3
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "source_tail"


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
    assert preview["preview_end_reason"] == "source_tail"


def test_preview_soft_min_takes_priority_over_target_max() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": index, "text": "汉" * 30, "text_role": "body"}
            for index in range(1, 10)
        ],
    }
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=first_cursor_for_chapter(chapter),
        reader_policy={
            "unitize": {
                "preview_soft_min_tokens": 100,
                "preview_target_max_tokens": 120,
                "preview_hard_max_tokens": 220,
            }
        },
    )

    assert preview["paragraph_count"] == 2
    assert preview["estimated_token_count"] > 120
    assert preview["estimated_token_count"] <= 220
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "target_max"


def test_preview_truncates_at_hard_token_max_with_end_exclusive_cursor() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=first_cursor_for_chapter(chapter),
        reader_policy={
            "unitize": {
                "preview_soft_min_tokens": 1,
                "preview_target_max_tokens": 5,
                "preview_hard_max_tokens": 40,
            }
        },
    )

    assert preview["source_text"]
    assert preview["preview_end_cursor"]["char_offset"] < len("Alpha " * 20)
    assert preview["truncated"] is True
    assert preview["preview_end_reason"] == "hard_max"
    assert preview["estimated_token_count"] <= 40


def test_preview_emergency_paragraph_guard_stops_pathological_short_lines() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": index, "text": "x", "text_role": "body"}
            for index in range(1, 20)
        ],
    }

    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={
            "unitize": {
                "preview_soft_min_chars": 1,
                "preview_hard_max_chars": 200,
                "emergency_max_preview_paragraphs": 5,
            }
        },
    )

    assert preview["paragraph_count"] == 5
    assert preview["paragraph_slices"][-1]["paragraph_index"] == 5
    assert preview["truncated"] is False
    assert preview["preview_end_reason"] == "emergency_paragraph_guard"


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


def test_ingest_unit_boundary_resolves_visible_paragraph_end() -> None:
    chapter = _chapter()
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "2", "end_at": "paragraph_end"},
    )

    assert resolution["status"] == "matched"
    assert resolution["method"] == "paragraph_end"
    assert resolution["end_cursor"]["paragraph_index"] == 2
    assert resolution["end_cursor"]["char_offset"] == len("Beta bridge.")
    assert resolution["matched_text"] == "Beta bridge."
    assert resolution["matched_text_is_derived"] is True


def test_ingest_unit_boundary_resolves_paragraph_local_tail_quote() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "Alpha opens. Beta closes. Gamma starts.", "text_role": "body"},
        ],
    }
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 1}},
    )

    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": 1, "end_at": "Beta closes."},
    )

    assert resolution["status"] == "matched"
    assert resolution["method"] == "paragraph_tail_quote"
    assert resolution["matched_text"] == "Beta closes."
    assert resolution["end_cursor"]["char_offset"] == len("Alpha opens. Beta closes.")


def test_ingest_unit_boundary_uses_quote_normalized_paragraph_match() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "“看！”悉达多轻声道，“此人就是佛陀。”", "text_role": "body"},
        ],
    }
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor={"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 1}},
    )

    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "1", "end_at": '"看！"悉达多轻声道，"此人就是佛陀。"'},
    )

    assert resolution["status"] == "matched"
    assert resolution["method"] == "normalized_paragraph_tail_quote"
    assert resolution["normalization"] == "quote_equivalence"
    assert resolution["matched_text"] == "“看！”悉达多轻声道，“此人就是佛陀。”"


def test_ingest_unit_boundary_extends_adjacent_trailing_closer() -> None:
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
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 1}},
    )

    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "1", "end_at": "在水面行走并不是我的追求。"},
    )

    assert resolution["status"] == "matched"
    assert resolution["matched_text"] == "在水面行走并不是我的追求。”"
    assert resolution["end_cursor_extension"] == {
        "kind": "trailing_closing_punctuation",
        "text": "”",
    }


def test_ingest_unit_boundary_reports_ambiguous_missing_and_invisible_boundaries() -> None:
    preview = {
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "preview_start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0},
        "preview_end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 10},
        "source_text": "echo echo",
        "paragraph_slices": [{"paragraph_index": 1, "start_char": 0, "end_char": 9, "text": "echo echo"}],
    }

    assert resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "1", "end_at": "echo"},
    )["status"] == "ambiguous"
    assert resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "1", "end_at": "missing"},
    )["status"] == "not_found"
    assert resolve_ingest_unit_boundary(
        preview=preview,
        unit={"end_paragraph_n": "2", "end_at": "paragraph_end"},
    )["reason"] == "unit.end_paragraph_n does not match a visible Paragraph n"


def test_preview_partition_audit_resolves_ordered_spans() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "Alpha opens. Beta closes.", "text_role": "body"},
            {"paragraph_index": 2, "text": "Gamma starts.", "text_role": "body"},
        ],
    }
    start_cursor = {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0}
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=start_cursor,
        reader_policy={"unitize": {"preview_soft_min_chars": 30, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 2}},
    )

    audit = resolve_preview_partition_audit(
        preview=preview,
        start_cursor=start_cursor,
        preview_partition=[
            {
                "title": "Opening claim",
                "end_paragraph_n": "1",
                "end_at": "Beta closes.",
                "status": "complete",
            },
            {
                "title": "Next move",
                "end_paragraph_n": "2",
                "end_at": "paragraph_end",
                "status": "complete",
            },
        ],
    )

    assert audit["status"] == "ok"
    partitions = audit["partitions"]
    assert partitions[0]["resolution_status"] == "resolved"
    assert partitions[0]["source_span_id"] == "src:c1:p1@0-p1@25"
    assert partitions[1]["source_span_id"] == "src:c1:p1@25-p2@13"


def test_preview_partition_audit_uses_quote_normalization_and_trailing_closer() -> None:
    chapter = {
        "id": 1,
        "title": "Chapter 1",
        "paragraphs": [
            {"paragraph_index": 1, "text": "“在水面行走并不是我的追求。”", "text_role": "body"},
        ],
    }
    start_cursor = {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 1, "char_offset": 0}
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=start_cursor,
        reader_policy={"unitize": {"preview_soft_min_chars": 1, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 1}},
    )

    audit = resolve_preview_partition_audit(
        preview=preview,
        start_cursor=start_cursor,
        preview_partition=[
            {
                "title": "Refused miracle",
                "end_paragraph_n": "1",
                "end_at": '"在水面行走并不是我的追求。',
                "status": "complete",
            }
        ],
    )

    assert audit["status"] == "ok"
    partition = audit["partitions"][0]
    assert partition["resolution_status"] == "resolved"
    assert partition["resolution"]["method"] == "normalized_paragraph_tail_quote"
    assert partition["resolution"]["end_cursor_extension"] == {
        "kind": "trailing_closing_punctuation",
        "text": "”",
    }


def test_preview_partition_audit_marks_later_unresolved_partition_partial() -> None:
    chapter = _chapter()
    start_cursor = {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0}
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=start_cursor,
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    audit = resolve_preview_partition_audit(
        preview=preview,
        start_cursor=start_cursor,
        preview_partition=[
            {"title": "Beta unit", "end_paragraph_n": "2", "end_at": "paragraph_end", "status": "complete"},
            {"title": "Missing quote", "end_paragraph_n": "3", "end_at": "missing", "status": "complete"},
        ],
    )

    assert audit["status"] == "partial"
    assert audit["partitions"][0]["resolution_status"] == "resolved"
    assert audit["partitions"][1]["resolution_status"] == "not_found"


def test_preview_partition_audit_marks_non_advancing_partition_partial() -> None:
    chapter = _chapter()
    start_cursor = {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 2, "char_offset": 0}
    preview = build_paragraph_offset_preview(
        chapter=chapter,
        current_cursor=start_cursor,
        reader_policy={"unitize": {"preview_soft_min_chars": 50, "preview_hard_max_chars": 200, "max_lookahead_paragraphs": 4}},
    )

    audit = resolve_preview_partition_audit(
        preview=preview,
        start_cursor=start_cursor,
        preview_partition=[
            {"title": "Beta unit", "end_paragraph_n": "2", "end_at": "paragraph_end", "status": "complete"},
            {"title": "Duplicate beta boundary", "end_paragraph_n": "2", "end_at": "paragraph_end", "status": "complete"},
        ],
    )

    assert audit["status"] == "partial"
    assert audit["partitions"][1]["resolution_status"] == "non_advancing"


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
    assert record["preview_end_reason"] == "source_tail"
    assert record["preview_estimated_token_count"] > 0
    assert record["preview_token_estimator"] == "tiktoken_o200k_base_v1_paragraph_xml_v1"


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
