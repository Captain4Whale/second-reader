"""Guard source identity/coverage and preserve raw annotations in human review."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from eval.attentional_v2.whole_book_digest_artifacts import (
    prepare_source,
    render_historical_reference,
    render_review,
    review_payload,
)
from src.reading_core.book_document_identity import book_document_substrate_digest


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _point(paragraph: int, offset: int) -> dict:
    return {"chapter_id": 2, "paragraph_index": paragraph, "char_offset": offset}


def _fixture(tmp_path: Path, *, boundary: str | None = None) -> Path:
    document = {
        "chapters": [
            {
                "id": 1,
                "title": "扉页",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "未读取",
                        "text_role": "chapter_heading",
                    }
                ],
            },
            {
                "id": 2,
                "title": "正文",
                "paragraphs": [
                    {"paragraph_index": 1, "text": "甲乙相同。", "text_role": "body"},
                    {"paragraph_index": 2, "text": "旁注", "text_role": "auxiliary"},
                    {"paragraph_index": 3, "text": "相同。丙丁", "text_role": "body"},
                ],
            },
        ]
    }
    first_end = 1 if boundary == "gap" else 3 if boundary == "overlap" else 2
    ranges = [(1, 0, 1, first_end, first_end, 1), (1, 2, 3, 5, 8, 2)]
    units = []
    ledger = []
    for index, (sp, so, ep, eo, chars, paragraphs) in enumerate(ranges, start=1):
        source_range = {"start": _point(sp, so), "end": _point(ep, eo)}
        units.append(
            {
                "unit_id": f"u{index:06d}",
                "sequence_index": index,
                "source_range": source_range,
                "understanding": f"理解{index}",
                "response": f"回应{index}",
                "marginalia": [],
            }
        )
        ledger.append(
            {
                "unit_id": f"u{index:06d}",
                "sequence_index": index,
                "start_cursor": source_range["start"],
                "end_cursor": source_range["end"],
                "char_count": chars,
                "paragraph_count": paragraphs,
            }
        )
    units[1]["marginalia"] = [
        {
            "kind": "note",
            "source_quote": "相同。",
            "body_text": "这是历史批注",
            "marginalia_id": "u000002-m001",
            "source_range": {"start": _point(1, 2), "end": _point(1, 5)},
        },
        {
            "kind": "highlight",
            "source_quote": "相同。",
            "marginalia_id": "u000002-m002",
            "source_range": {"start": _point(3, 0), "end": _point(3, 3)},
        },
    ]
    product = {
        "status": "complete",
        "reading_id": "fixture-reading",
        "units": units,
        "source": {
            "book_document_substrate_sha256": book_document_substrate_digest(document)
        },
    }
    _write(tmp_path / "public/book_document.json", document)
    product_path = (
        tmp_path / "public/reading-products/revisions/test/reading-product.json"
    )
    _write(product_path, product)
    _write(
        tmp_path / "public/reading-products/current.json",
        {
            "reading_id": product["reading_id"],
            "reading_product": "revisions/test/reading-product.json",
            "reading_product_sha256": hashlib.sha256(
                product_path.read_bytes()
            ).hexdigest(),
        },
    )
    ledger_path = tmp_path / "_mechanisms/attentional_v2/runtime/unit_span_ledger.jsonl"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(
        "\n".join(json.dumps(row) for row in ledger), encoding="utf-8"
    )
    return tmp_path


def test_source_rejoins_paragraph_split_by_units_and_keeps_exact_text(
    tmp_path: Path,
) -> None:
    source = prepare_source(_fixture(tmp_path))
    assert source["source_text"] == "甲乙相同。\n\n相同。丙丁"
    assert source["metrics"]["content_characters"] == 10
    assert source["metrics"]["source_characters"] == 12
    assert source["metrics"]["paragraph_count"] == 2
    assert source["metrics"]["historical_marginalia_count"] == 2
    assert [paragraph["paragraph_index"] for paragraph in source["paragraphs"]] == [
        1,
        3,
    ]
    assert [
        paragraph["paragraph_index"] for paragraph in source["paragraph_slices"]
    ] == [1, 2]
    assert [
        (paragraph["start"], paragraph["end"]) for paragraph in source["paragraphs"]
    ] == [(0, 5), (7, 12)]


@pytest.mark.parametrize("boundary", ["gap", "overlap"])
def test_incomplete_or_overlapping_historical_coverage_fails(
    tmp_path: Path, boundary: str
) -> None:
    with pytest.raises(ValueError, match="gap|overlap"):
        prepare_source(_fixture(tmp_path, boundary=boundary))


def test_changed_book_text_fails_substrate_identity(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / "public/book_document.json"
    document = json.loads(path.read_text())
    document["chapters"][1]["paragraphs"][0]["text"] = "修改过的文字"
    _write(path, document)
    with pytest.raises(ValueError, match="substrate hash"):
        prepare_source(root)


def test_disagreeing_private_ledger_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    path = root / "_mechanisms/attentional_v2/runtime/unit_span_ledger.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["end_cursor"]["char_offset"] = 1
    path.write_text("\n".join(json.dumps(row) for row in rows))
    with pytest.raises(ValueError, match="ranges differ"):
        prepare_source(root)


def test_review_keeps_all_repeat_quote_candidates_and_invalid_raw_items(
    tmp_path: Path,
) -> None:
    source = prepare_source(_fixture(tmp_path))
    payload = {
        "understanding": "理解",
        "response": "回应",
        "marginalia": [
            {"kind": "note", "source_quote": "丙丁", "content": "末尾批注"},
            {"kind": "note", "source_quote": "相同。", "content": "有歧义"},
            {"kind": "note", "source_quote": "不存在", "content": "不能丢失"},
            {"kind": "note", "source_quote": "甲乙", "content": 42},
            "非对象原始条目",
            {
                "kind": "highlight",
                "source_quote": "甲乙",
                "selection_reason": "私有理由",
            },
        ],
    }
    before = deepcopy(payload)
    review = review_payload(payload, source)
    assert payload == before
    assert review["counts"] == {
        "total": 6,
        "valid": 2,
        "invalid": 4,
        "highlights": 1,
        "notes": 4,
        "uniquely_located": 3,
        "ambiguous": 1,
        "unlocated": 2,
    }
    ambiguous = next(item for item in review["items"] if item["original_index"] == 2)
    assert [candidate["global_start"] for candidate in ambiguous["candidates"]] == [
        2,
        7,
    ]
    assert [
        candidate["start"]["paragraph_index"] for candidate in ambiguous["candidates"]
    ] == [1, 3]
    assert ambiguous["validation_errors"]
    assert [item["original_index"] for item in review["items"]] == [4, 6, 2, 1, 3, 5]
    markdown = render_review(payload, review, "人工核查")
    for text in (
        "不能丢失",
        "非对象原始条目",
        "42",
        "私有选择理由",
        "私有理由",
        "位置候选 2",
        "Understanding / Response",
    ):
        assert text in markdown
    assert markdown.index("末尾批注") < markdown.index("不能丢失")


def test_exact_matching_does_not_normalize_quotes_and_maps_cross_paragraphs(
    tmp_path: Path,
) -> None:
    source = prepare_source(_fixture(tmp_path))
    payload = {
        "understanding": "理解",
        "response": "回应",
        "marginalia": [
            {"kind": "note", "source_quote": "相同。\n\n相同。", "content": "跨段"},
            {"kind": "note", "source_quote": "相同。 相同。", "content": "换行错误"},
        ],
    }
    review = review_payload(payload, source)
    assert review["counts"]["valid"] == 1
    candidate = review["items"][0]["candidates"][0]
    assert candidate["start"]["paragraph_index"] == 1
    assert candidate["end"]["paragraph_index"] == 3
    assert candidate["end"]["char_offset"] == 3
    assert review["items"][1]["candidates"] == []


@pytest.mark.parametrize(
    "payload",
    ["unparseable raw text", {"understanding": "", "marginalia": {"wrong": "shape"}}],
)
def test_malformed_top_level_output_is_preserved(
    tmp_path: Path, payload: object
) -> None:
    source = prepare_source(_fixture(tmp_path))
    review = review_payload(payload, source)
    assert review["validation_errors"]
    markdown = render_review(payload, review, "失败输出也保留")
    assert ("unparseable raw text" if isinstance(payload, str) else "shape") in markdown


def test_historical_reference_uses_settled_locations_and_separates_ur(
    tmp_path: Path,
) -> None:
    source = prepare_source(_fixture(tmp_path))
    markdown = render_historical_reference(source)
    assert "2 个已完成 Unit；2 条批注（Highlight 1，Note 1）" in markdown
    assert "p1@2" in markdown and "p3@0" in markdown
    assert "这是历史批注" in markdown
    assert markdown.index("这是历史批注") < markdown.index("辅助材料：各 Unit")
    assert "理解1" in markdown and "回应2" in markdown
    assert "不保存私有 selection_reason" in markdown
