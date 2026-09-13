"""Read-only source reconstruction and lossless human review for one-book Digest probes."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
import hashlib
import html
import json
from pathlib import Path
from typing import Any

from src.reading_core.book_document_identity import book_document_substrate_digest


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _coordinate(value: Mapping[str, Any]) -> tuple[int, int, int]:
    fields = tuple(
        value[key] for key in ("chapter_id", "paragraph_index", "char_offset")
    )
    if any(type(item) is not int for item in fields):
        raise ValueError("Source coordinates must contain integers")
    return fields  # type: ignore[return-value]


def prepare_source(baseline_output: Path) -> dict[str, Any]:
    """Recover complete paragraphs from matching settled Product and private Unit ranges.

    This deliberately requires full readable coverage of every historically read chapter.
    It does not reparse, classify source text, mutate the baseline, or import model code.
    """
    document = _load(baseline_output / "public/book_document.json")
    publication_root = baseline_output / "public/reading-products"
    pointer = _load(publication_root / "current.json")
    product_path = (publication_root / pointer["reading_product"]).resolve()
    if not product_path.is_relative_to(publication_root.resolve()):
        raise ValueError("Reading Product pointer escapes its publication directory")
    product_bytes = product_path.read_bytes()
    product_sha256 = hashlib.sha256(product_bytes).hexdigest()
    if product_sha256 != pointer["reading_product_sha256"]:
        raise ValueError("Published Reading Product hash mismatch")
    product = json.loads(product_bytes)
    if product.get("status") != "complete":
        raise ValueError("Historical Reading Product must be complete")
    if product.get("reading_id") != pointer.get("reading_id"):
        raise ValueError("Reading Product pointer identity mismatch")
    if (
        book_document_substrate_digest(document)
        != product["source"]["book_document_substrate_sha256"]
    ):
        raise ValueError("Historical BookDocument substrate hash mismatch")
    ledger_path = (
        baseline_output / "_mechanisms/attentional_v2/runtime/unit_span_ledger.jsonl"
    )
    ledger = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    units = product["units"]
    if not units or len(units) != len(ledger):
        raise ValueError(
            "Historical Unit ledger and Product counts differ or are empty"
        )

    chapters = {chapter["id"]: chapter for chapter in document["chapters"]}
    if len(chapters) != len(document["chapters"]):
        raise ValueError("Duplicate BookDocument chapter ID")
    chapter_order = {chapter_id: order for order, chapter_id in enumerate(chapters)}
    coverage: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    touched_chapters: set[int] = set()
    previous_end: tuple[int, int, int] | None = None
    for index, (unit, record) in enumerate(zip(units, ledger), start=1):
        if unit["sequence_index"] != index or record["sequence_index"] != index:
            raise ValueError("Historical Unit sequence gap")
        if unit["unit_id"] != record["unit_id"] or unit["unit_id"] != f"u{index:06d}":
            raise ValueError("Historical Unit ID mismatch")
        start = _coordinate(unit["source_range"]["start"])
        end = _coordinate(unit["source_range"]["end"])
        if start != _coordinate(record["start_cursor"]) or end != _coordinate(
            record["end_cursor"]
        ):
            raise ValueError("Historical Product and Unit ledger source ranges differ")
        chapter_id, first_paragraph, first_offset = start
        if chapter_id != end[0] or chapter_id not in chapters or start[1:] >= end[1:]:
            raise ValueError("Invalid historical Unit range")
        ordered_start = (chapter_order[chapter_id], first_paragraph, first_offset)
        ordered_end = (chapter_order[chapter_id], end[1], end[2])
        if previous_end is not None and ordered_start < previous_end:
            raise ValueError("Historical Unit overlap or source order reversal")
        previous_end = ordered_end
        touched_chapters.add(chapter_id)
        paragraphs = chapters[chapter_id]["paragraphs"]
        by_index = {paragraph["paragraph_index"]: paragraph for paragraph in paragraphs}
        if len(by_index) != len(paragraphs):
            raise ValueError("Duplicate BookDocument paragraph index")
        for paragraph_index, offset in (
            (first_paragraph, first_offset),
            (end[1], end[2]),
        ):
            paragraph = by_index.get(paragraph_index)
            if paragraph is None or paragraph.get("text_role") == "auxiliary":
                raise ValueError("Unit boundary is not a readable source paragraph")
            if not 0 <= offset <= len(paragraph["text"]):
                raise ValueError("Unit boundary exceeds source paragraph")
        characters = 0
        slices = 0
        for paragraph in paragraphs:
            paragraph_index = paragraph["paragraph_index"]
            text = paragraph["text"]
            if paragraph.get("text_role") == "auxiliary" or not text.strip():
                continue
            if not first_paragraph <= paragraph_index <= end[1]:
                continue
            left = first_offset if paragraph_index == first_paragraph else 0
            right = end[2] if paragraph_index == end[1] else len(text)
            if left < right:
                coverage[chapter_id, paragraph_index].append((left, right))
                characters += right - left
                slices += 1
        if characters != record["char_count"] or slices != record["paragraph_count"]:
            raise ValueError("Historical Unit character or paragraph count mismatch")

    paragraphs_out: list[dict[str, Any]] = []
    global_offset = 0
    for chapter in document["chapters"]:
        if chapter["id"] not in touched_chapters:
            continue
        for paragraph in chapter["paragraphs"]:
            text = paragraph["text"]
            if paragraph.get("text_role") == "auxiliary" or not text.strip():
                continue
            key = (chapter["id"], paragraph["paragraph_index"])
            cursor = 0
            for left, right in sorted(coverage.get(key, [])):
                if left != cursor:
                    raise ValueError(
                        f"Historical paragraph coverage gap or overlap at {key}"
                    )
                cursor = right
            if cursor != len(text):
                raise ValueError(f"Historical paragraph coverage gap at {key}")
            if paragraphs_out:
                global_offset += 2
            paragraphs_out.append(
                {
                    "global_paragraph_index": len(paragraphs_out) + 1,
                    "start": global_offset,
                    "end": global_offset + len(text),
                    "chapter_id": chapter["id"],
                    "chapter_title": chapter["title"],
                    "paragraph_index": paragraph["paragraph_index"],
                    "text_role": paragraph.get("text_role", "body"),
                    "text": text,
                }
            )
            global_offset += len(text)
    source_text = "\n\n".join(paragraph["text"] for paragraph in paragraphs_out)
    return {
        "source_text": source_text,
        "paragraph_slices": [
            {
                "paragraph_index": paragraph["global_paragraph_index"],
                "text": paragraph["text"],
            }
            for paragraph in paragraphs_out
        ],
        "paragraphs": paragraphs_out,
        "historical_product": product,
        "metrics": {
            "unit_count": len(units),
            "paragraph_count": len(paragraphs_out),
            "content_characters": sum(
                len(paragraph["text"]) for paragraph in paragraphs_out
            ),
            "source_characters": len(source_text),
            "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "reading_product_sha256": product_sha256,
            "chapter_ids": [
                chapter_id for chapter_id in chapters if chapter_id in touched_chapters
            ],
            "text_role_counts": dict(
                Counter(paragraph["text_role"] for paragraph in paragraphs_out)
            ),
            "historical_marginalia_count": sum(
                len(unit["marginalia"]) for unit in units
            ),
        },
    }


def _position(
    source: dict[str, Any], offset: int, *, end: bool = False
) -> dict[str, Any] | None:
    for paragraph in source["paragraphs"]:
        inside = (
            paragraph["start"] < offset <= paragraph["end"]
            if end
            else paragraph["start"] <= offset < paragraph["end"]
        )
        if inside:
            return {
                "chapter_id": paragraph["chapter_id"],
                "chapter_title": paragraph["chapter_title"],
                "paragraph_index": paragraph["paragraph_index"],
                "char_offset": offset - paragraph["start"],
            }
    return None


def _candidate(source: dict[str, Any], start: int, end: int) -> dict[str, Any]:
    return {
        "global_start": start,
        "global_end": end,
        "start": _position(source, start),
        "end": _position(source, end, end=True),
    }


def review_payload(payload: object, source: dict[str, Any]) -> dict[str, Any]:
    """Retain every raw item; exact matches are candidates, never silently selected anchors."""
    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return {
            "items": [],
            "validation_errors": ["payload must be an object"],
            "counts": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "highlights": 0,
                "notes": 0,
                "uniquely_located": 0,
                "ambiguous": 0,
                "unlocated": 0,
            },
        }
    for field in ("understanding", "response"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            errors.append(f"{field} must be a non-empty string")
    raw_items = payload.get("marginalia")
    if not isinstance(raw_items, list):
        errors.append("marginalia must be an array")
        raw_items = []
    items: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items, start=1):
        item_errors: list[str] = []
        candidates: list[dict[str, Any]] = []
        if not isinstance(raw, Mapping):
            item_errors.append("item must be an object")
        else:
            kind = raw.get("kind")
            content = raw.get("content")
            if kind not in ("highlight", "note"):
                item_errors.append("kind must be highlight or note")
            if content is not None and not isinstance(content, str):
                item_errors.append("content must be a string or null")
            if kind == "note" and (not isinstance(content, str) or not content.strip()):
                item_errors.append("note content must be non-empty")
            if kind == "highlight":
                if content not in (None, ""):
                    item_errors.append("highlight content must be empty")
                reason = raw.get("selection_reason")
                if not isinstance(reason, str) or not reason.strip():
                    item_errors.append(
                        "highlight private selection_reason must be non-empty"
                    )
            if raw.get("selection_reason") is not None and not isinstance(
                raw["selection_reason"], str
            ):
                item_errors.append("selection_reason must be a string or null")
            quote = raw.get("source_quote")
            if not isinstance(quote, str) or not quote.strip():
                item_errors.append("source_quote must be a non-empty string")
            else:
                offset = 0
                while (match := source["source_text"].find(quote, offset)) >= 0:
                    candidates.append(_candidate(source, match, match + len(quote)))
                    offset = match + 1
                if not candidates:
                    item_errors.append("source_quote has no exact match")
                elif len(candidates) > 1:
                    item_errors.append(
                        "source_quote has multiple exact locations; no location selected"
                    )
                if any(
                    candidate["start"] is None or candidate["end"] is None
                    for candidate in candidates
                ):
                    item_errors.append(
                        "source_quote boundary falls outside a source paragraph"
                    )
        items.append(
            {
                "original_index": index,
                "raw": raw,
                "candidates": candidates,
                "validation_errors": item_errors,
            }
        )
    # Ambiguous items sort by their earliest candidate solely for review, not anchor acceptance.
    items.sort(
        key=lambda item: (
            item["candidates"][0]["global_start"]
            if item["candidates"]
            else float("inf"),
            item["original_index"],
        )
    )
    counts = {
        "total": len(items),
        "valid": sum(not item["validation_errors"] for item in items),
        "invalid": sum(bool(item["validation_errors"]) for item in items),
        "highlights": sum(
            isinstance(item["raw"], Mapping) and item["raw"].get("kind") == "highlight"
            for item in items
        ),
        "notes": sum(
            isinstance(item["raw"], Mapping) and item["raw"].get("kind") == "note"
            for item in items
        ),
        "uniquely_located": sum(len(item["candidates"]) == 1 for item in items),
        "ambiguous": sum(len(item["candidates"]) > 1 for item in items),
        "unlocated": sum(not item["candidates"] for item in items),
    }
    return {"items": items, "validation_errors": errors, "counts": counts}


def _quoted(value: object) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return (
        "\n".join("> " + html.escape(line) for line in text.splitlines()) or "> （空）"
    )


def _location(candidate: Mapping[str, Any]) -> str:
    def point(value: object) -> str:
        if not isinstance(value, Mapping):
            return "段落分隔符"
        return f"第 {value['chapter_id']} 章《{value['chapter_title']}》p{value['paragraph_index']}@{value['char_offset']}"

    return f"{point(candidate['start'])} → {point(candidate['end'])}"


def render_review(payload: object, review: dict[str, Any], title: str) -> str:
    """Render annotations first and U/R separately; invalid raw output remains inspectable."""
    counts = review["counts"]
    lines = [
        f"# {title}",
        "",
        f"原始条目 {counts['total']}；Highlight {counts['highlights']}；Note {counts['notes']}。",
        f"通过本地格式与唯一定位检查 {counts['valid']}；待核查 {counts['invalid']}（含定位歧义 {counts['ambiguous']}）。",
        "这只是格式与原文定位检查，不是批注质量评分。按原文顺序呈现；歧义项按最早候选位置排序，但不选定该位置。",
        "",
    ]
    for error in review["validation_errors"]:
        lines.extend([f"- 顶层检查：{error}", ""])
    for number, item in enumerate(review["items"], start=1):
        raw = item["raw"]
        kind = raw.get("kind", "无效类型") if isinstance(raw, Mapping) else "无效条目"
        flag = " · 待核查" if item["validation_errors"] else ""
        lines.extend(
            [f"## {number}. {kind}（原输出 #{item['original_index']}）{flag}", ""]
        )
        for candidate_index, candidate in enumerate(item["candidates"], start=1):
            lines.extend([f"位置候选 {candidate_index}：{_location(candidate)}", ""])
        if isinstance(raw, Mapping):
            lines.extend(["原文：", "", _quoted(raw.get("source_quote")), ""])
            if raw.get("content") not in (None, ""):
                label = (
                    "批注："
                    if kind == "note"
                    else "原始 content（与 Highlight 契约冲突，保留核查）："
                )
                lines.extend([label, "", _quoted(raw["content"]), ""])
            if raw.get("selection_reason") not in (None, ""):
                lines.extend(
                    [
                        "私有选择理由（辅助审查，不是读者批注）：",
                        "",
                        _quoted(raw["selection_reason"]),
                        "",
                    ]
                )
        for error in item["validation_errors"]:
            lines.extend([f"- 检查：{error}", ""])
        if item["validation_errors"]:
            lines.extend(
                [
                    "原始条目完整保留：",
                    "",
                    _quoted(json.dumps(raw, ensure_ascii=False, indent=2)),
                    "",
                ]
            )
    lines.extend(
        [
            "## 辅助材料：Understanding / Response",
            "",
            "以下内容与原文定位批注分开呈现，不计入批注条数。",
            "",
        ]
    )
    if isinstance(payload, Mapping):
        for field in ("understanding", "response"):
            lines.extend([f"### {field}", "", _quoted(payload.get(field)), ""])
        if not isinstance(payload.get("marginalia"), list):
            lines.extend(
                [
                    "### 无效 marginalia 原始值",
                    "",
                    _quoted(payload.get("marginalia")),
                    "",
                ]
            )
    else:
        lines.extend(["原始输出：", "", _quoted(payload), ""])
    return "\n".join(lines).rstrip() + "\n"


def render_historical_reference(source: dict[str, Any]) -> str:
    """Render settled historical marks using their canonical coordinates, including U/R."""
    product = source["historical_product"]
    marks = [(unit, mark) for unit in product["units"] for mark in unit["marginalia"]]
    titles = {
        paragraph["chapter_id"]: paragraph["chapter_title"]
        for paragraph in source["paragraphs"]
    }
    marks.sort(
        key=lambda pair: (
            *_coordinate(pair[1]["source_range"]["start"]),
            pair[1]["marginalia_id"],
        )
    )
    counts = Counter(mark["kind"] for _, mark in marks)
    lines = [
        "# 历史分段阅读批注参考",
        "",
        f"{len(product['units'])} 个已完成 Unit；{len(marks)} 条批注（Highlight {counts['highlight']}，Note {counts['note']}）。",
        "本文件复用既有 Reading Product，不重新生成，也不把历史结果当作人工质量标准。位置采用已结算坐标。",
        "",
    ]
    for index, (unit, mark) in enumerate(marks, start=1):
        location = {
            side: {
                **mark["source_range"][side],
                "chapter_title": titles[mark["source_range"][side]["chapter_id"]],
            }
            for side in ("start", "end")
        }
        lines.extend(
            [
                f"## {index}. {mark['kind']} · {mark['marginalia_id']}",
                "",
                _location(location),
                "",
                "原文：",
                "",
                _quoted(mark["source_quote"]),
                "",
            ]
        )
        if mark["kind"] == "note":
            lines.extend(["批注：", "", _quoted(mark["body_text"]), ""])
    lines.extend(
        [
            "## 辅助材料：各 Unit 的 Understanding / Response",
            "",
            "这些材料不计入批注条数；历史 Product 不保存私有 selection_reason。",
            "",
        ]
    )
    for unit in product["units"]:
        lines.extend(
            [
                f"### {unit['unit_id']}",
                "",
                "Understanding：",
                "",
                _quoted(unit["understanding"]),
                "",
                "Response：",
                "",
                _quoted(unit["response"]),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
