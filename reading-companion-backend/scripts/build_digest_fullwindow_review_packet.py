#!/usr/bin/env python3
"""Build the five-book Digest v24 full-window human review packet.

This script is intentionally artifact-only: it does not call an LLM, does not
change prompts, and does not re-run the smoke harness. It merges existing
Ingest/Digest/runtime audit artifacts into a detailed review packet for human
inspection.
"""

from __future__ import annotations

import argparse
import concurrent.futures
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = BACKEND_ROOT / "eval" / "runs" / "attentional_v2"

PRIMARY_RUN_ID = "digest_marginalia_v24_5book_parallel_fullwindow_20260704"
PRIMARY_ANALYSIS_ID = "digest_marginalia_v24_5book_parallel_fullwindow"
PRIMARY_ANALYSIS_ROOT = RUN_ROOT / PRIMARY_RUN_ID / "analysis" / PRIMARY_ANALYSIS_ID
REVIEW_PACKET_ROOT = PRIMARY_ANALYSIS_ROOT / "review_packet"

EXPECTED_TOTALS = {
    "unit_count": 246,
    "marginalia_count": 460,
    "marginalia_kind_counts": {"highlight": 355, "note": 105},
    "retrieval_rows": 247,
    "selection_rows": 246,
    "quality_flag_counts": {"possibly_generic": 6, "quote_too_broad": 33},
}


@dataclass(frozen=True)
class RunSource:
    key: str
    run_id: str
    analysis_id: str

    @property
    def analysis_root(self) -> Path:
        return RUN_ROOT / self.run_id / "analysis" / self.analysis_id


@dataclass(frozen=True)
class SegmentSource:
    segment_id: str
    expected_units: int
    final_source_key: str
    title_hint: str


RUN_SOURCES = [
    RunSource("primary", PRIMARY_RUN_ID, PRIMARY_ANALYSIS_ID),
    RunSource(
        "nawaer_retry1",
        "digest_marginalia_v24_nawaer_fullwindow_retry1_20260705",
        "digest_marginalia_v24_nawaer_fullwindow_retry1",
    ),
    RunSource(
        "xidaduo_continue1",
        "digest_marginalia_v24_xidaduo_fullwindow_continue1_20260705",
        "digest_marginalia_v24_xidaduo_fullwindow_continue1",
    ),
    RunSource(
        "xidaduo_continue2",
        "digest_marginalia_v24_xidaduo_fullwindow_continue2_20260705",
        "digest_marginalia_v24_xidaduo_fullwindow_continue2",
    ),
]

RUN_SOURCE_BY_KEY = {source.key: source for source in RUN_SOURCES}

SEGMENT_SOURCES = [
    SegmentSource(
        "huochu_shengming_de_yiyi_private_zh__segment_1",
        56,
        "primary",
        "活出生命的意义",
    ),
    SegmentSource(
        "mangge_zhi_dao_private_zh__segment_1",
        93,
        "primary",
        "芒格之道",
    ),
    SegmentSource(
        "value_of_others_private_en__segment_1",
        23,
        "primary",
        "The Value of Others",
    ),
    SegmentSource(
        "nawaer_baodian_private_zh__segment_1",
        10,
        "nawaer_retry1",
        "纳瓦尔宝典",
    ),
    SegmentSource(
        "xidaduo_private_zh__segment_1",
        64,
        "xidaduo_continue2",
        "悉达多",
    ),
]

REVIEW_NOTES = {
    "huochu_shengming_de_yiyi_private_zh__segment_1": {
        "overall": [
            "Huochu is a positive long-form continuity sample: 56 units reached chapter_end, all accepted units have matched source spans, and later units show long-distance Unit Memory entering ReadingMemory.",
            "Ingest segmentation is mostly natural: short or long units usually track local semantic closure rather than mechanical paragraph counts.",
            "Understanding / Response often carry the book's continuing themes, but memory influence should be treated as an interpretive judgment from trace + output continuity, not as a mechanically provable causal claim.",
            "Marginalia risk is low but not zero: only one possibly_generic and one quote_too_broad flag surfaced in the merged audit.",
        ],
        "examples": [
            "Unit 13 / src:c1:p51@0-p61@87 is the main caveat: it is above_hard_max and has empty Digest output despite a natural boundary arc around first-stage reaction and second-stage apathy.",
            "Unit 41 / src:c1:p163@0-p167@349 retrieves u000006/u000002/u000001 and then moves into inner freedom versus environmental determination, giving a strong continuity sample.",
            "Unit 50 / src:c1:p206@0-p212@142 retrieves six earlier units and uses the prior meaning/hope frame while Frankl speaks to prisoners about past, future, sacrifice, and responsibility.",
        ],
        "caveats": [
            "ReadingMemory inclusion is trace-proven; actual Digest use is judged from output continuity.",
            "The two audit flags are small in count but useful for targeted manual review.",
        ],
    },
    "mangge_zhi_dao_private_zh__segment_1": {
        "overall": [
            "Mangge is a complete non-linear speech-collection sample: 93 units reached chapter_end with matched unit spans and no segment-level partial failure.",
            "Ingest handles the anthology shape well by grouping year headings, editor notes, financial context, appendices, and Q&A themes into local semantic blocks.",
            "Long-distance memory is present but selective: 14 recall attempts produced 7 units with retrieved memory lines reaching ReadingMemory; most other continuity is hot memory or no recall.",
            "Understanding / Response preserve cross-speech themes such as savings-and-loan risk, regulation, Freddie Mac, and risk arbitrage rather than treating each paragraph as isolated.",
            "Marginalia risk is modest: 156 items, 5 total audit flags, mostly possibly_generic notes plus one quote_too_broad highlight.",
        ],
        "examples": [
            "Unit 14 / src:c1:p86@0-p92@146 naturally handles the 1988 heading, editor note, financial background, and Salomon setup.",
            "Unit 62 / src:c1:p403@0-p410@131 recalls prior savings-and-loan logic and retrieves multiple early units before Digest contrasts banks/FDIC with S&Ls/FSLIC.",
            "Unit 38 / src:c1:p250@0-p256@223 captures the practical philosophy of comparing present alternatives rather than predicting, while also showing one quote_too_broad and one possibly_generic flag.",
        ],
        "caveats": [
            "Mangge had recovered units during provider recovery, but the segment itself completed cleanly.",
            "The primary full-window run was partial overall; do not attribute other books' provider failures to this segment.",
        ],
    },
    "value_of_others_private_en__segment_1": {
        "overall": [
            "Value of Others is a complete short-window English sample: 23 units reached chapter_end with 58 Marginalia items.",
            "Long-distance Unit Memory is effectively absent because the 20-unit recent-neighbor exclusion and minimum retrievable horizon block all non-empty recalls from producing retrieved lines.",
            "Hot memory still supports continuity: ReadingMemory hot lines grow through the chapter and Digest keeps carrying value transaction, nested games, covert calculator, desire, and valuation-algorithm concepts.",
            "Understanding / Response are generally not isolated summaries; later units continue the conceptual chain about unconscious value computation and desire correction.",
            "The main Marginalia risk is quote span width: 29 quote_too_broad flags, concentrated in this English concept-book segment.",
        ],
        "examples": [
            "Unit 13 / src:c1:p49@0-p51@635 has a recall suppressed by retrieval horizon but still uses 12 hot lines to continue goal hierarchy and choice inference.",
            "Unit 16 / src:c1:p60@0-p65@1416 recalls husband/covert-calculator material, receives 15 hot lines, and connects value coefficient, emotion, desire, and approach-avoidance conflict.",
            "Unit 21 / src:c1:p83@0-p85@825 receives 20 hot lines and continues the awareness-alone-is-insufficient and better-data-corrects-algorithm thread.",
        ],
        "caveats": [
            "This segment validates hot memory continuity, not long-distance retrieval quality.",
            "The quote_too_broad concentration may partly reflect long English conceptual sentences, but it still needs human span review.",
        ],
    },
    "nawaer_baodian_private_zh__segment_1": {
        "overall": [
            "Nawaer retry1 cleanly fills the primary run's provider failure: 10 units reached chapter_end after primary unit 1 stopped with network_blocked / RemoteProtocolError.",
            "This is a short hot-memory sample, not a long-distance retrieval proof: retrieved_line_count is 0 throughout, while hot memory accumulates across the chapter.",
            "Understanding / Response preserve the wealth-building concept chain from wealth vs money through equity, specific knowledge, accountability, leverage, productization, and scale.",
            "Marginalia is strongly highlight-only: all 26 items are highlights and there are no notes, which is natural for aphoristic text but still a visible channel-diversity limitation.",
        ],
        "examples": [
            "Unit 5 / src:c1:p54@0-p59@25 recalls permissioned versus permissionless leverage, but retrieval is horizon-suppressed; Digest still links capital/labor to code/media through hot memory.",
            "Unit 7 / src:c1:p85@0-p88@72 uses 6 hot lines and compresses self-specificity, accountability, specific knowledge, and productization into a continuous formula.",
            "Unit 6 / src:c1:p60@0-p84@10 shows the highlight-only pattern clearly: strong conceptual continuity, 5 highlights, but no note-bearing Marginalia.",
        ],
        "caveats": [
            "Only 10 units and several below soft-min units; do not generalize this as cross-chapter or long-distance retrieval evidence.",
            "The zero-note output should be called out as a Marginalia diversity concern rather than a contract failure.",
        ],
    },
    "xidaduo_private_zh__segment_1": {
        "overall": [
            "Xidaduo continue2 is the final cumulative evidence source: the runtime ledger contains 64 accepted units to chapter_end even though the continue2 raw runner summary only counts the 19 newly added units.",
            "Long-distance retrieval reaches Digest ReadingMemory repeatedly, especially in the later narrative around Vasudeva, Kamala, the son, the river, and Om.",
            "Understanding / Response show strong narrative continuity across character arcs and recurring father-son / departure-return motifs.",
            "Retrieval quality is useful but not perfectly precise; continuity appears supported by hot memory, current source text, and selected long-distance retrieval together.",
            "Marginalia flags are low for the final continuation, but flags do not prove there are no missed notes or over-elevated highlights.",
        ],
        "examples": [
            "Unit 46 / src:c1:p396@0-p401@80 reprocesses the continue1 failure position; ReadingMemory retrieves 6 units and Digest captures Vasudeva's listening, the river, Om, and co-living invitation.",
            "Unit 58 / src:c1:p473@0-p478@141 tracks the son's departure and Vasudeva's advice to release him, connecting Siddhartha's fatherhood to his own earlier departure.",
            "Unit 61 / src:c1:p491@0-p496@304 succeeds after a network recovery and connects father, reflection in the river, son, repetition of suffering, and Vasudeva's farewell.",
        ],
        "caveats": [
            "The extra retrieval row is the preserved continue1 invalid_recall_tool_args event, not an accepted Digest unit.",
            "A later spiritual elevation unit with zero Marginalia may indicate conservative selection or a missed note, but not a hard failure.",
        ],
    },
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = _load_json(path)
    return value if isinstance(value, dict) else {}


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _table_text(value: Any) -> str:
    text = _clean_text(value)
    return text.replace("|", "\\|")


def _short(value: Any, limit: int = 220) -> str:
    text = _clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _cursor_str(cursor: Any) -> str:
    if not isinstance(cursor, dict):
        return "-"
    paragraph = cursor.get("paragraph_index", "?")
    offset = cursor.get("char_offset", "?")
    return f"P{paragraph}@{offset}"


def _span_str(span: Any) -> str:
    if not isinstance(span, dict):
        return "-"
    return f"{_cursor_str(span.get('start_cursor'))} -> {_cursor_str(span.get('end_cursor'))}"


def _code_block(text: Any, language: str = "text") -> list[str]:
    return [f"```{language}", str(text or "").strip(), "```"]


def _details_block(summary: str, body_lines: list[str]) -> list[str]:
    return [
        f"<details><summary>{summary}</summary>",
        "",
        *body_lines,
        "",
        "</details>",
    ]


def _runtime_dir(analysis_root: Path, segment_id: str) -> Path:
    return analysis_root / "runtime" / segment_id / "_mechanisms" / "attentional_v2" / "runtime"


def _public_dir(analysis_root: Path, segment_id: str) -> Path:
    return analysis_root / "runtime" / segment_id / "public"


def _runner_units_path(analysis_root: Path) -> Path:
    return analysis_root / "raw" / "runner_units.json"


def _summary_path(analysis_root: Path) -> Path:
    return analysis_root / "raw" / "summary.json"


def _status_path(analysis_root: Path) -> Path:
    return analysis_root / "status.json"


def _load_runner_segments(analysis_root: Path) -> list[dict[str, Any]]:
    path = _runner_units_path(analysis_root)
    if not path.exists():
        return []
    value = _load_json(path)
    return value if isinstance(value, list) else []


def _runner_segment_for(analysis_root: Path, segment_id: str) -> dict[str, Any]:
    for segment in _load_runner_segments(analysis_root):
        if isinstance(segment, dict) and segment.get("segment_id") == segment_id:
            return segment
    return {}


def _extract_understanding_from_read_row(row: dict[str, Any]) -> str:
    for op in row.get("memory_uptake_ops") or []:
        if not isinstance(op, dict):
            continue
        payload = op.get("payload")
        if isinstance(payload, dict):
            text = _clean_text(payload.get("memory_text"))
            if text:
                return text
    digest = row.get("digest_result")
    if isinstance(digest, dict):
        for op in digest.get("memory_uptake_ops") or []:
            if not isinstance(op, dict):
                continue
            payload = op.get("payload")
            if isinstance(payload, dict):
                text = _clean_text(payload.get("memory_text"))
                if text:
                    return text
    return ""


def _load_book_paragraphs(public_dir: Path) -> dict[int, dict[int, str]]:
    path = public_dir / "book_document.json"
    if not path.exists():
        return {}
    document = _load_json_dict(path)
    by_chapter: dict[int, dict[int, str]] = {}
    for chapter in document.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id") or chapter.get("chapter_number") or 1)
        paragraphs: dict[int, str] = {}
        for paragraph in chapter.get("paragraphs") or []:
            if not isinstance(paragraph, dict):
                continue
            try:
                index = int(paragraph.get("paragraph_index"))
            except (TypeError, ValueError):
                continue
            paragraphs[index] = str(paragraph.get("text") or "")
        by_chapter[chapter_id] = paragraphs
    return by_chapter


def _source_text_from_document(span: dict[str, Any], paragraphs_by_chapter: dict[int, dict[int, str]]) -> str:
    start = span.get("start_cursor") if isinstance(span.get("start_cursor"), dict) else {}
    end = span.get("end_cursor") if isinstance(span.get("end_cursor"), dict) else {}
    try:
        chapter_id = int(start.get("chapter_id") or end.get("chapter_id") or 1)
        start_p = int(start.get("paragraph_index"))
        start_offset = int(start.get("char_offset") or 0)
        end_p = int(end.get("paragraph_index"))
        end_offset = int(end.get("char_offset") or 0)
    except (TypeError, ValueError):
        return ""
    paragraphs = paragraphs_by_chapter.get(chapter_id, {})
    parts: list[str] = []
    for paragraph_index in range(start_p, end_p + 1):
        text = paragraphs.get(paragraph_index, "")
        if not text:
            continue
        if paragraph_index == start_p and paragraph_index == end_p:
            part = text[start_offset:end_offset]
        elif paragraph_index == start_p:
            part = text[start_offset:]
        elif paragraph_index == end_p:
            part = text[:end_offset]
        else:
            part = text
        if part.strip():
            parts.append(part.strip())
    return "\n\n".join(parts)


def _index_raw_runner_units() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    raw_by_span: dict[str, dict[str, Any]] = {}
    reviews_by_span: dict[str, list[dict[str, Any]]] = {}
    failure_events: list[dict[str, Any]] = []
    for source in RUN_SOURCES:
        analysis_root = source.analysis_root
        summary = _load_json_dict(_summary_path(analysis_root))
        status = _load_json_dict(_status_path(analysis_root))
        for failure in summary.get("partial_failures") or []:
            if isinstance(failure, dict):
                failure_events.append(
                    {
                        "run_id": source.run_id,
                        "event_source": "summary.partial_failures",
                        **failure,
                    }
                )
        for failure in summary.get("hard_failures") or []:
            failure_events.append(
                {
                    "run_id": source.run_id,
                    "event_source": "summary.hard_failures",
                    "failure": failure,
                }
            )
        if status.get("error"):
            failure_events.append(
                {
                    "run_id": source.run_id,
                    "event_source": "status.error",
                    "status": status.get("status"),
                    "error": status.get("error"),
                }
            )
        for segment in _load_runner_segments(analysis_root):
            if not isinstance(segment, dict):
                continue
            segment_id = segment.get("segment_id")
            for unit in segment.get("units") or []:
                if not isinstance(unit, dict):
                    continue
                span_id = _clean_text(unit.get("source_span_id"))
                event = {
                    "run_id": source.run_id,
                    "segment_id": segment_id,
                    "unit_index": unit.get("unit_index"),
                    "source_span_id": span_id,
                    "status": unit.get("status"),
                    "problem_code": unit.get("problem_code"),
                    "error": unit.get("error"),
                    "start_cursor": unit.get("start_cursor"),
                    "final_cursor": unit.get("final_cursor") or unit.get("end_cursor"),
                    "recovery_events": unit.get("recovery_events") or [],
                    "connection_error_kind": unit.get("connection_error_kind"),
                    "provider_error_type": unit.get("provider_error_type"),
                    "provider_error_cause_type": unit.get("provider_error_cause_type"),
                }
                if unit.get("status") != "ok":
                    failure_events.append({**event, "event_source": "raw.runner_units"})
                    continue
                if span_id:
                    raw_by_span[span_id] = {**unit, "_run_id": source.run_id, "_segment_id": segment_id}
                    review = unit.get("marginalia_review")
                    if isinstance(review, list):
                        reviews_by_span[span_id] = [item for item in review if isinstance(item, dict)]
    return raw_by_span, reviews_by_span, failure_events


def _take_retrieval_rows(
    read_rows: list[dict[str, Any]],
    retrieval_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any] | None], list[dict[str, Any]]]:
    by_span: dict[str, deque[tuple[int, dict[str, Any]]]] = defaultdict(deque)
    for index, row in enumerate(retrieval_rows):
        span_id = _clean_text(row.get("accepted_source_span_id") or row.get("source_span_id"))
        if span_id:
            by_span[span_id].append((index, row))
    used: set[int] = set()
    ordinal_cursor = 0
    assigned: list[dict[str, Any] | None] = []
    for ordinal, read_row in enumerate(read_rows):
        span_id = _clean_text(read_row.get("source_span_id"))
        row: dict[str, Any] | None = None
        while span_id and by_span.get(span_id):
            candidate_index, candidate = by_span[span_id].popleft()
            if candidate_index not in used:
                row = candidate
                used.add(candidate_index)
                break
        if row is None:
            while ordinal_cursor < len(retrieval_rows):
                candidate = retrieval_rows[ordinal_cursor]
                candidate_index = ordinal_cursor
                ordinal_cursor += 1
                if candidate_index in used:
                    continue
                candidate_span = _clean_text(candidate.get("accepted_source_span_id") or candidate.get("source_span_id"))
                if (
                    not candidate_span
                    and (
                        _clean_text(candidate.get("query_source")) == "skip_invalid_recalls"
                        or _clean_text(candidate.get("degradation_reason")) == "invalid_recall_tool_args"
                    )
                ):
                    continue
                if candidate_span and candidate_span != span_id:
                    continue
                row = candidate
                used.add(candidate_index)
                break
        if row is None and ordinal < len(retrieval_rows) and ordinal not in used:
            candidate = retrieval_rows[ordinal]
            candidate_span = _clean_text(candidate.get("accepted_source_span_id") or candidate.get("source_span_id"))
            candidate_is_invalid_orphan = (
                not candidate_span
                and (
                    _clean_text(candidate.get("query_source")) == "skip_invalid_recalls"
                    or _clean_text(candidate.get("degradation_reason")) == "invalid_recall_tool_args"
                )
            )
            if not candidate_is_invalid_orphan and (not candidate_span or candidate_span == span_id):
                row = candidate
                used.add(ordinal)
        assigned.append(row)
    leftovers = [row for index, row in enumerate(retrieval_rows) if index not in used]
    return assigned, leftovers


def _selection_rows_by_span(
    read_rows: list[dict[str, Any]],
    selection_rows: list[dict[str, Any]],
) -> list[dict[str, Any] | None]:
    by_span: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
    for row in selection_rows:
        span_id = _clean_text(row.get("source_span_id"))
        if span_id:
            by_span[span_id].append(row)
    assigned: list[dict[str, Any] | None] = []
    for ordinal, read_row in enumerate(read_rows):
        span_id = _clean_text(read_row.get("source_span_id"))
        if span_id and by_span.get(span_id):
            assigned.append(by_span[span_id].popleft())
        elif ordinal < len(selection_rows):
            assigned.append(selection_rows[ordinal])
        else:
            assigned.append(None)
    return assigned


def _classify_memory(retrieval: dict[str, Any] | None, selection: dict[str, Any] | None) -> list[str]:
    tags: list[str] = []
    recalls = retrieval.get("recalls") if isinstance(retrieval, dict) else []
    has_recalls = bool(recalls)
    retrieved_count = int(selection.get("retrieved_line_count") or 0) if isinstance(selection, dict) else 0
    hot_count = int(selection.get("hot_line_count") or 0) if isinstance(selection, dict) else 0
    selected_units = retrieval.get("selected_units") if isinstance(retrieval, dict) else []
    degradation = _clean_text(retrieval.get("degradation_reason")) if isinstance(retrieval, dict) else ""
    suppressed = []
    if isinstance(retrieval, dict) and isinstance(retrieval.get("suppressed_units"), list):
        suppressed.extend(retrieval.get("suppressed_units") or [])
    if isinstance(selection, dict) and isinstance(selection.get("suppressed"), list):
        suppressed.extend(selection.get("suppressed") or [])
    if retrieved_count > 0:
        tags.append("long-distance-retrieved")
    elif has_recalls and (selected_units or suppressed or degradation not in {"", "none", "no_recall"}):
        tags.append("retrieval-suppressed")
    elif hot_count > 0:
        tags.append("hot-memory-only")
    else:
        tags.append("no-recall")
    if has_recalls:
        tags.append("model-recall-intent")
    if suppressed:
        tags.append("has-suppression")
    return tags


def _marginalia_kind(item: dict[str, Any]) -> str:
    kind = _clean_text(item.get("kind")).lower()
    if kind in {"highlight", "note"}:
        return kind
    return "note" if _clean_text(item.get("content")) else "highlight"


def _quality_flags_for_item(item: dict[str, Any], review_rows: list[dict[str, Any]]) -> list[str]:
    quote = _clean_text(item.get("source_quote"))
    content = _clean_text(item.get("content"))
    kind = _marginalia_kind(item)
    for review in review_rows:
        if (
            _clean_text(review.get("source_quote")) == quote
            and _clean_text(review.get("content")) == content
            and _marginalia_kind(review) == kind
        ):
            flags = review.get("quality_flags")
            return [str(flag) for flag in flags] if isinstance(flags, list) else []
    return []


def _quote_found_for_item(item: dict[str, Any], review_rows: list[dict[str, Any]]) -> str:
    quote = _clean_text(item.get("source_quote"))
    for review in review_rows:
        if _clean_text(review.get("source_quote")) == quote and "quote_found_in_unit" in review:
            return str(review.get("quote_found_in_unit"))
    return ""


def _summarize_retrieval_row(row: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    recalls = row.get("recalls") if isinstance(row.get("recalls"), list) else []
    selected = row.get("selected_units") if isinstance(row.get("selected_units"), list) else []
    suppressed = row.get("suppressed_units") if isinstance(row.get("suppressed_units"), list) else []
    return {
        "query_source": row.get("query_source"),
        "degradation_reason": row.get("degradation_reason"),
        "effective_mode": row.get("effective_mode"),
        "recall_count": len(recalls),
        "recalls": recalls,
        "selected_unit_count": len(selected),
        "selected_units": selected,
        "suppressed_unit_count": len(suppressed),
        "suppressed_units": suppressed,
        "candidate_counts": row.get("candidate_counts") or {},
        "horizon": row.get("horizon") or {},
    }


def _summarize_selection_row(row: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return {
        "line_count": int(row.get("line_count") or 0),
        "hot_line_count": int(row.get("hot_line_count") or 0),
        "retrieved_line_count": int(row.get("retrieved_line_count") or 0),
        "rendered_retrieved_units": row.get("rendered_retrieved_units") or [],
        "rendered_hot_unit_count": len(row.get("rendered_hot_units") or []),
        "suppressed": row.get("suppressed") or [],
        "budget": row.get("budget") or {},
    }


def _build_segment_packet(
    segment: SegmentSource,
    raw_by_span: dict[str, dict[str, Any]],
    reviews_by_span: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    source = RUN_SOURCE_BY_KEY[segment.final_source_key]
    analysis_root = source.analysis_root
    runtime_dir = _runtime_dir(analysis_root, segment.segment_id)
    public_dir = _public_dir(analysis_root, segment.segment_id)
    runner_segment = _runner_segment_for(analysis_root, segment.segment_id)
    read_rows = _jsonl_rows(runtime_dir / "read_audit.jsonl")
    span_rows = _jsonl_rows(runtime_dir / "unit_span_ledger.jsonl")
    trace_rows = _jsonl_rows(runtime_dir / "unit_memory_retrieval_trace.jsonl")
    retrieval_rows = [row for row in trace_rows if row.get("event_type") == "unit_memory_retrieval"]
    selection_rows = [row for row in trace_rows if row.get("event_type") == "unit_memory_reading_memory_selection"]
    assigned_retrieval, orphan_retrieval_rows = _take_retrieval_rows(read_rows, retrieval_rows)
    assigned_selection = _selection_rows_by_span(read_rows, selection_rows)
    span_by_id = {_clean_text(row.get("source_span_id")): row for row in span_rows}
    paragraphs_by_chapter = _load_book_paragraphs(public_dir)
    units: list[dict[str, Any]] = []
    kind_counts: Counter[str] = Counter()
    quality_flags: Counter[str] = Counter()
    query_sources: Counter[str] = Counter()
    degradation_reasons: Counter[str] = Counter()
    memory_tags: Counter[str] = Counter()
    hot_line_total = 0
    retrieved_line_total = 0
    long_distance_examples: list[dict[str, Any]] = []
    suppressed_examples: list[dict[str, Any]] = []
    missing_source_text = 0
    for index, read_row in enumerate(read_rows, start=1):
        span_id = _clean_text(read_row.get("source_span_id"))
        span_row = span_by_id.get(span_id, {})
        raw_unit = raw_by_span.get(span_id, {})
        review_rows = reviews_by_span.get(span_id, [])
        retrieval_row = assigned_retrieval[index - 1] if index - 1 < len(assigned_retrieval) else None
        selection_row = assigned_selection[index - 1] if index - 1 < len(assigned_selection) else None
        retrieval_summary = _summarize_retrieval_row(retrieval_row)
        selection_summary = _summarize_selection_row(selection_row)
        query_sources[_clean_text(retrieval_summary.get("query_source") or "missing")] += 1
        degradation_reasons[_clean_text(retrieval_summary.get("degradation_reason") or "none")] += 1
        hot_line_total += int(selection_summary.get("hot_line_count") or 0)
        retrieved_line_total += int(selection_summary.get("retrieved_line_count") or 0)
        tags = _classify_memory(retrieval_row, selection_row)
        memory_tags.update(tags)
        source_span = read_row.get("source_span") if isinstance(read_row.get("source_span"), dict) else {}
        source_text = _clean_text(raw_unit.get("source_text"))
        if not source_text and source_span:
            source_text = _source_text_from_document(source_span, paragraphs_by_chapter)
        if not source_text:
            missing_source_text += 1
        understanding = _clean_text(raw_unit.get("understanding")) or _extract_understanding_from_read_row(read_row)
        response = _clean_text(read_row.get("reading_impression")) or _clean_text(raw_unit.get("reading_impression"))
        marginalia = [item for item in read_row.get("marginalia") or [] if isinstance(item, dict)]
        marginalia_rows: list[dict[str, Any]] = []
        for item_index, item in enumerate(marginalia, start=1):
            kind = _marginalia_kind(item)
            kind_counts[kind] += 1
            flags = _quality_flags_for_item(item, review_rows)
            quality_flags.update(flags)
            marginalia_rows.append(
                {
                    "index": item_index,
                    "kind": kind,
                    "source_quote": _clean_text(item.get("source_quote")),
                    "content": _clean_text(item.get("content")),
                    "selection_reason": _clean_text(item.get("selection_reason")),
                    "quote_found_in_unit": _quote_found_for_item(item, review_rows),
                    "quality_flags": flags,
                }
            )
        unit = {
            "unit_index": index,
            "unit_id": span_row.get("unit_id"),
            "source_span_id": span_id,
            "source_span": source_span,
            "span": _span_str(source_span),
            "start_cursor": source_span.get("start_cursor") if isinstance(source_span, dict) else {},
            "end_cursor": source_span.get("end_cursor") if isinstance(source_span, dict) else {},
            "stop_reason": read_row.get("stop_reason"),
            "source_text": source_text,
            "unit_char_count": read_row.get("unit_char_count") or span_row.get("char_count"),
            "unit_paragraph_count": read_row.get("unit_paragraph_count") or span_row.get("paragraph_count"),
            "unit_partition_titles": span_row.get("unit_partition_titles") or [],
            "unit_size_status": span_row.get("unit_size_status"),
            "unit_estimated_token_count": span_row.get("unit_estimated_token_count"),
            "preview_estimated_token_count": span_row.get("preview_estimated_token_count"),
            "preview_end_reason": span_row.get("preview_end_reason"),
            "ingest_reason": _clean_text(((read_row.get("ingest_trace") or [{}])[0] or {}).get("reason"))
            if isinstance(read_row.get("ingest_trace"), list)
            else "",
            "preview_partition": ((read_row.get("unitize_decision") or {}).get("preview_partition") or [])
            if isinstance(read_row.get("unitize_decision"), dict)
            else [],
            "preview_partition_audit": ((read_row.get("unitize_decision") or {}).get("preview_partition_audit") or [])
            if isinstance(read_row.get("unitize_decision"), dict)
            else [],
            "retrieval": retrieval_summary,
            "reading_memory_selection": selection_summary,
            "memory_tags": tags,
            "understanding": understanding,
            "response": response,
            "marginalia": marginalia_rows,
            "memory_uptake_ops": read_row.get("memory_uptake_ops") or [],
            "llm_fallbacks": read_row.get("llm_fallbacks") or [],
            "raw_run_id": raw_unit.get("_run_id", source.run_id),
            "recovered": bool(raw_unit.get("recovered")),
            "recovery_events": raw_unit.get("recovery_events") or [],
        }
        if int(selection_summary.get("retrieved_line_count") or 0) > 0 and len(long_distance_examples) < 8:
            long_distance_examples.append(
                {
                    "unit_index": index,
                    "source_span_id": span_id,
                    "recalls": retrieval_summary.get("recalls") or [],
                    "rendered_retrieved_units": selection_summary.get("rendered_retrieved_units") or [],
                    "understanding": understanding,
                    "response": response,
                }
            )
        if ("retrieval-suppressed" in tags or "has-suppression" in tags) and len(suppressed_examples) < 8:
            suppressed_examples.append(
                {
                    "unit_index": index,
                    "source_span_id": span_id,
                    "degradation_reason": retrieval_summary.get("degradation_reason"),
                    "suppressed_units": retrieval_summary.get("suppressed_units") or [],
                    "selection_suppressed": selection_summary.get("suppressed") or [],
                }
            )
        units.append(unit)
    summary = {
        "segment_id": segment.segment_id,
        "title_hint": segment.title_hint,
        "book_title": runner_segment.get("book_title") or segment.title_hint,
        "author": runner_segment.get("author"),
        "final_run_id": source.run_id,
        "final_analysis_root": str(analysis_root.relative_to(BACKEND_ROOT)),
        "status": runner_segment.get("status"),
        "stop_reason": runner_segment.get("stop_reason"),
        "final_cursor": runner_segment.get("final_cursor") or {},
        "expected_units": segment.expected_units,
        "unit_count": len(read_rows),
        "unit_span_ledger_count": len(span_rows),
        "retrieval_rows": len(retrieval_rows),
        "selection_rows": len(selection_rows),
        "orphan_retrieval_rows": len(orphan_retrieval_rows),
        "marginalia_count": sum(kind_counts.values()),
        "marginalia_kind_counts": dict(sorted(kind_counts.items())),
        "quality_flag_counts": dict(sorted(quality_flags.items())),
        "query_source_counts": dict(sorted(query_sources.items())),
        "degradation_reason_counts": dict(sorted(degradation_reasons.items())),
        "memory_tag_counts": dict(sorted(memory_tags.items())),
        "hot_line_total": hot_line_total,
        "retrieved_line_total": retrieved_line_total,
        "missing_source_text_count": missing_source_text,
        "recovered_unit_count": sum(1 for unit in units if unit.get("recovered")),
        "long_distance_examples": long_distance_examples,
        "suppressed_examples": suppressed_examples,
        "orphan_retrieval_row_details": orphan_retrieval_rows,
    }
    return {"summary": summary, "units": units}


def _validate_packets(segment_packets: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    totals = Counter()
    kind_totals: Counter[str] = Counter()
    flag_totals: Counter[str] = Counter()
    for segment in SEGMENT_SOURCES:
        packet = segment_packets.get(segment.segment_id)
        if not packet:
            errors.append(f"missing segment packet: {segment.segment_id}")
            continue
        summary = packet["summary"]
        if summary["unit_count"] != segment.expected_units:
            errors.append(f"{segment.segment_id}: expected {segment.expected_units} units, got {summary['unit_count']}")
        if summary["unit_count"] != summary["unit_span_ledger_count"]:
            errors.append(
                f"{segment.segment_id}: read_audit/unit_span_ledger mismatch "
                f"{summary['unit_count']} vs {summary['unit_span_ledger_count']}"
            )
        if summary.get("stop_reason") != "chapter_end":
            errors.append(f"{segment.segment_id}: stop_reason is {summary.get('stop_reason')!r}, expected chapter_end")
        if summary["selection_rows"] != summary["unit_count"]:
            errors.append(
                f"{segment.segment_id}: selection rows {summary['selection_rows']} != unit count {summary['unit_count']}"
            )
        if segment.segment_id == "xidaduo_private_zh__segment_1":
            if summary["retrieval_rows"] != summary["unit_count"] + 1:
                errors.append(f"{segment.segment_id}: expected one orphan retrieval row")
        elif summary["retrieval_rows"] != summary["unit_count"]:
            errors.append(
                f"{segment.segment_id}: retrieval rows {summary['retrieval_rows']} != unit count {summary['unit_count']}"
            )
        if summary["missing_source_text_count"]:
            errors.append(f"{segment.segment_id}: missing source text for {summary['missing_source_text_count']} units")
        totals["unit_count"] += int(summary["unit_count"])
        totals["marginalia_count"] += int(summary["marginalia_count"])
        totals["retrieval_rows"] += int(summary["retrieval_rows"])
        totals["selection_rows"] += int(summary["selection_rows"])
        kind_totals.update(summary["marginalia_kind_counts"])
        flag_totals.update(summary["quality_flag_counts"])
    for key, expected in EXPECTED_TOTALS.items():
        if key == "marginalia_kind_counts":
            if dict(sorted(kind_totals.items())) != expected:
                errors.append(f"marginalia_kind_counts expected {expected}, got {dict(sorted(kind_totals.items()))}")
        elif key == "quality_flag_counts":
            if dict(sorted(flag_totals.items())) != expected:
                errors.append(f"quality_flag_counts expected {expected}, got {dict(sorted(flag_totals.items()))}")
        elif totals[key] != expected:
            errors.append(f"{key} expected {expected}, got {totals[key]}")
    return errors


def _render_unit(unit: dict[str, Any]) -> list[str]:
    retrieval = unit.get("retrieval") or {}
    selection = unit.get("reading_memory_selection") or {}
    marginalia = unit.get("marginalia") or []
    lines: list[str] = [
        f"### Unit {unit.get('unit_index')} · `{unit.get('source_span_id')}`",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| span | `{unit.get('span')}` |",
        f"| memory tags | `{', '.join(unit.get('memory_tags') or [])}` |",
        f"| stop reason | `{unit.get('stop_reason')}` |",
        f"| unit size | `{unit.get('unit_estimated_token_count')}` tokens / `{unit.get('unit_size_status')}` |",
        f"| preview | `{unit.get('preview_estimated_token_count')}` tokens / `{unit.get('preview_end_reason')}` |",
        f"| recovered | `{unit.get('recovered')}` |",
        f"| marginalia | `{len(marginalia)}` |",
        "",
        "**Ingest Boundary Reason**",
        "",
        _clean_text(unit.get("ingest_reason")) or "_missing_",
        "",
        "**Recall Intent And Retrieval Result**",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| query_source | `{retrieval.get('query_source')}` |",
        f"| degradation | `{retrieval.get('degradation_reason')}` |",
        f"| recall_count | `{retrieval.get('recall_count', 0)}` |",
        f"| selected_unit_count | `{retrieval.get('selected_unit_count', 0)}` |",
        f"| hot / retrieved lines | `{selection.get('hot_line_count', 0)} / {selection.get('retrieved_line_count', 0)}` |",
        f"| rendered hot units | `{selection.get('rendered_hot_unit_count', 0)}` |",
        "",
    ]
    recalls = retrieval.get("recalls") or []
    if recalls:
        lines.extend(["**Model Recall Intents**", ""])
        for recall in recalls:
            if not isinstance(recall, dict):
                continue
            lines.append(
                "- "
                f"`{recall.get('recall_id')}` "
                f"basis=`{recall.get('basis')}`: {_clean_text(recall.get('recall_text'))}"
            )
        lines.append("")
    rendered_retrieved = selection.get("rendered_retrieved_units") or []
    if rendered_retrieved:
        lines.extend(["**Rendered Long-Distance Memory**", ""])
        for item in rendered_retrieved[:8]:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"`{item.get('unit_id')}` / `{item.get('source_span_id')}` "
                f"matched=`{json.dumps(item.get('matched_recalls', []), ensure_ascii=False)}`"
            )
        if len(rendered_retrieved) > 8:
            lines.append(f"- ... {len(rendered_retrieved) - 8} more retrieved units")
        lines.append("")
    suppressed = (retrieval.get("suppressed_units") or []) + (selection.get("suppressed") or [])
    if suppressed:
        lines.extend(["**Suppression / Budget Events**", ""])
        for item in suppressed[:8]:
            if not isinstance(item, dict):
                continue
            lines.append(f"- `{item.get('source_span_id') or item.get('unit_id')}` reason=`{item.get('reason')}`")
        if len(suppressed) > 8:
            lines.append(f"- ... {len(suppressed) - 8} more suppressed rows")
        lines.append("")
    preview_partition = unit.get("preview_partition") or []
    if preview_partition:
        lines.extend(
            _details_block(
                f"Preview partition ({len(preview_partition)} entries)",
                [
                    "| # | title | boundary | status |",
                    "| ---: | --- | --- | --- |",
                    *[
                        f"| {idx} | {_table_text(item.get('title'))} | "
                        f"`P{item.get('end_paragraph_n')} / {item.get('end_at')}` | `{item.get('status')}` |"
                        for idx, item in enumerate(preview_partition)
                        if isinstance(item, dict)
                    ],
                ],
            )
        )
        lines.append("")
    lines.extend(
        _details_block(
            "Selected source text",
            _code_block(unit.get("source_text") or "", "text"),
        )
    )
    lines.extend(["", "**Digest Understanding**", "", unit.get("understanding") or "_missing_", ""])
    lines.extend(["**Response / Reading Impression**", "", unit.get("response") or "_missing_", ""])
    lines.extend(["**Marginalia**", ""])
    if marginalia:
        lines.extend(["| # | kind | quote_found | flags | quote | content | selection_reason |", "| ---: | --- | --- | --- | --- | --- | --- |"])
        for item in marginalia:
            lines.append(
                f"| {item.get('index')} | `{item.get('kind')}` | `{item.get('quote_found_in_unit')}` | "
                f"`{json.dumps(item.get('quality_flags', []), ensure_ascii=False)}` | "
                f"{_table_text(_short(item.get('source_quote'), 180))} | "
                f"{_table_text(_short(item.get('content'), 180))} | "
                f"{_table_text(_short(item.get('selection_reason'), 220))} |"
            )
    else:
        lines.append("- No Marginalia emitted.")
    lines.append("")
    if unit.get("recovery_events"):
        lines.extend(
            _details_block(
                f"Recovery events ({len(unit.get('recovery_events') or [])})",
                _code_block(json.dumps(unit.get("recovery_events"), ensure_ascii=False, indent=2), "json"),
            )
        )
        lines.append("")
    return lines


def _render_book_doc(packet: dict[str, Any]) -> list[str]:
    summary = packet["summary"]
    units = packet["units"]
    notes = REVIEW_NOTES.get(str(summary.get("segment_id")), {})
    lines: list[str] = [
        f"# {summary.get('book_title')} · Digest Full-Window Review",
        "",
        "## Scope",
        "",
        f"- segment_id: `{summary.get('segment_id')}`",
        f"- final_run_id: `{summary.get('final_run_id')}`",
        f"- final_analysis_root: `{summary.get('final_analysis_root')}`",
        f"- status / stop_reason: `{summary.get('status')}` / `{summary.get('stop_reason')}`",
        f"- units: `{summary.get('unit_count')}`",
        f"- final_cursor: `{json.dumps(summary.get('final_cursor', {}), ensure_ascii=False)}`",
        "",
        "## Health Snapshot",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Marginalia | `{summary.get('marginalia_count')}` |",
        f"| Marginalia kinds | `{json.dumps(summary.get('marginalia_kind_counts', {}), ensure_ascii=False)}` |",
        f"| Quality flags | `{json.dumps(summary.get('quality_flag_counts', {}), ensure_ascii=False)}` |",
        f"| Retrieval rows | `{summary.get('retrieval_rows')}` |",
        f"| Selection rows | `{summary.get('selection_rows')}` |",
        f"| Orphan retrieval rows | `{summary.get('orphan_retrieval_rows')}` |",
        f"| Hot / retrieved memory lines | `{summary.get('hot_line_total')} / {summary.get('retrieved_line_total')}` |",
        f"| Recovered units | `{summary.get('recovered_unit_count')}` |",
        "",
        "## Retrieval Interpretation",
        "",
        f"- query_source_counts: `{json.dumps(summary.get('query_source_counts', {}), ensure_ascii=False)}`",
        f"- degradation_reason_counts: `{json.dumps(summary.get('degradation_reason_counts', {}), ensure_ascii=False)}`",
        f"- memory_tag_counts: `{json.dumps(summary.get('memory_tag_counts', {}), ensure_ascii=False)}`",
        "",
    ]
    if notes:
        lines.extend(["## Human Review Notes", ""])
        for item in notes.get("overall", []):
            lines.append(f"- {item}")
        if notes.get("examples"):
            lines.extend(["", "### Notable Examples", ""])
            for item in notes.get("examples", []):
                lines.append(f"- {item}")
        if notes.get("caveats"):
            lines.extend(["", "### Caveats", ""])
            for item in notes.get("caveats", []):
                lines.append(f"- {item}")
        lines.append("")
    if summary.get("retrieved_line_total", 0) > 0:
        lines.append(
            "Long-distance Unit Memory reached Digest ReadingMemory in this book; inspect the examples below "
            "to judge whether Understanding / Response used that continuity naturally."
        )
    else:
        lines.append(
            "No long-distance Unit Memory lines reached Digest ReadingMemory in this book; this mainly validates "
            "hot current-reading memory and recall degradation behavior under the retrieval horizon."
        )
    lines.append("")
    examples = summary.get("long_distance_examples") or []
    if examples:
        lines.extend(["### Long-Distance Retrieval Examples", ""])
        for example in examples[:5]:
            recall_text = "; ".join(_short(item.get("recall_text"), 120) for item in example.get("recalls", []) if isinstance(item, dict))
            retrieved_spans = ", ".join(
                _clean_text(item.get("source_span_id"))
                for item in example.get("rendered_retrieved_units", [])
                if isinstance(item, dict)
            )
            lines.append(
                f"- Unit `{example.get('unit_index')}` `{example.get('source_span_id')}`: "
                f"recall={_short(recall_text, 220)}; retrieved={_short(retrieved_spans, 220)}"
            )
        lines.append("")
    suppressed_examples = summary.get("suppressed_examples") or []
    if suppressed_examples:
        lines.extend(["### Suppression Examples", ""])
        for example in suppressed_examples[:5]:
            lines.append(
                f"- Unit `{example.get('unit_index')}` `{example.get('source_span_id')}`: "
                f"degradation=`{example.get('degradation_reason')}` "
                f"retrieval_suppressed=`{len(example.get('suppressed_units') or [])}` "
                f"selection_suppressed=`{len(example.get('selection_suppressed') or [])}`"
            )
        lines.append("")
    if summary.get("orphan_retrieval_row_details"):
        lines.extend(
            _details_block(
                f"Orphan retrieval rows ({summary.get('orphan_retrieval_rows')})",
                _code_block(json.dumps(summary.get("orphan_retrieval_row_details"), ensure_ascii=False, indent=2), "json"),
            )
        )
        lines.append("")
    lines.extend(["## Units", ""])
    for unit in units:
        lines.extend(_render_unit(unit))
    return lines


def _render_retrieval_summary(segment_packets: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        "# Unit Memory Retrieval Summary",
        "",
        "This report aggregates `unit_memory_retrieval_trace.jsonl` across the final five-book evidence set.",
        "",
        "| Segment | Units | Retrieval rows | Selection rows | Hot lines | Retrieved lines | Memory tags | Degradation reasons |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for segment in SEGMENT_SOURCES:
        summary = segment_packets[segment.segment_id]["summary"]
        lines.append(
            f"| `{segment.segment_id}` | `{summary['unit_count']}` | `{summary['retrieval_rows']}` | "
            f"`{summary['selection_rows']}` | `{summary['hot_line_total']}` | `{summary['retrieved_line_total']}` | "
            f"`{json.dumps(summary['memory_tag_counts'], ensure_ascii=False)}` | "
            f"`{json.dumps(summary['degradation_reason_counts'], ensure_ascii=False)}` |"
        )
    lines.extend(["", "## Examples", ""])
    for segment in SEGMENT_SOURCES:
        summary = segment_packets[segment.segment_id]["summary"]
        lines.append(f"### {summary.get('book_title')} (`{segment.segment_id}`)")
        examples = summary.get("long_distance_examples") or []
        if not examples:
            lines.append("- No rendered long-distance retrieved memory lines.")
            lines.append("")
            continue
        for example in examples[:5]:
            lines.append(f"- Unit `{example.get('unit_index')}` `{example.get('source_span_id')}`")
            for recall in example.get("recalls") or []:
                if isinstance(recall, dict):
                    lines.append(f"  - recall `{recall.get('recall_id')}`: {_clean_text(recall.get('recall_text'))}")
            for item in example.get("rendered_retrieved_units") or []:
                if isinstance(item, dict):
                    lines.append(
                        f"  - retrieved `{item.get('unit_id')}` / `{item.get('source_span_id')}` "
                        f"matched=`{json.dumps(item.get('matched_recalls', []), ensure_ascii=False)}`"
                    )
        lines.append("")
    return lines


def _render_recovery_history(
    run_summaries: dict[str, dict[str, Any]],
    failure_events: list[dict[str, Any]],
    segment_packets: dict[str, dict[str, Any]],
) -> list[str]:
    lines = [
        "# Recovery History",
        "",
        "This file preserves partial and failed evidence instead of hiding it behind the final successful continuation.",
        "",
        "## Run Chain",
        "",
        "| run_id | status | units | marginalia | failures | role |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    role_by_run = {
        PRIMARY_RUN_ID: "primary partial full-window run",
        "digest_marginalia_v24_nawaer_fullwindow_retry1_20260705": "Nawaer retry to chapter_end",
        "digest_marginalia_v24_xidaduo_fullwindow_continue1_20260705": "Xidaduo continuation; preserved llm_contract failure",
        "digest_marginalia_v24_xidaduo_fullwindow_continue2_20260705": "Xidaduo final continuation to chapter_end",
    }
    for source in RUN_SOURCES:
        summary = run_summaries.get(source.run_id, {})
        failures = list(summary.get("hard_failures") or []) + list(summary.get("partial_failures") or [])
        lines.append(
            f"| `{source.run_id}` | `{summary.get('status')}` | `{summary.get('runner_unit_count')}` | "
            f"`{summary.get('marginalia_count')}` | `{len(failures)}` | {role_by_run.get(source.run_id, '')} |"
        )
    lines.extend(["", "## Failure / Partial Events", ""])
    if not failure_events:
        lines.append("- No failure events found.")
    for event in failure_events:
        lines.append(
            "- "
            f"run=`{event.get('run_id')}` source=`{event.get('event_source')}` "
            f"segment=`{event.get('segment_id', '')}` unit=`{event.get('unit_index', '')}` "
            f"problem=`{event.get('problem_code') or event.get('stop_reason') or event.get('failure', '')}` "
            f"connection_kind=`{event.get('connection_error_kind', '')}` "
            f"provider_error=`{event.get('provider_error_type', '')}` "
            f"cursor=`{json.dumps(event.get('final_cursor') or {}, ensure_ascii=False)}`"
        )
    lines.extend(["", "## Final Evidence Sources", ""])
    for segment in SEGMENT_SOURCES:
        summary = segment_packets[segment.segment_id]["summary"]
        lines.append(
            f"- `{segment.segment_id}` uses final_run_id=`{summary.get('final_run_id')}` "
            f"with `{summary.get('unit_count')}` accepted units and stop_reason=`{summary.get('stop_reason')}`."
        )
    return lines


def _render_readme(
    packet_summary: dict[str, Any],
    segment_packets: dict[str, dict[str, Any]],
) -> list[str]:
    lines = [
        "# Digest Marginalia v24 Five-Book Full-Window Review Packet",
        "",
        "## Summary",
        "",
        "This packet is a human-review companion to the original `marginalia_smoke_report.md`. "
        "It preserves the original smoke report and adds detailed Ingest, Digest, Marginalia, "
        "Unit Memory retrieval, and recovery-history surfaces.",
        "",
        f"- generated_at: `{packet_summary.get('generated_at')}`",
        f"- primary_run_id: `{PRIMARY_RUN_ID}`",
        f"- total units: `{packet_summary['totals']['unit_count']}`",
        f"- total Marginalia: `{packet_summary['totals']['marginalia_count']}`",
        f"- Marginalia kinds: `{json.dumps(packet_summary['totals']['marginalia_kind_counts'], ensure_ascii=False)}`",
        f"- retrieval rows / selection rows: `{packet_summary['totals']['retrieval_rows']} / {packet_summary['totals']['selection_rows']}`",
        f"- quality flags: `{json.dumps(packet_summary['totals']['quality_flag_counts'], ensure_ascii=False)}`",
        "",
        "## Overall Judgment",
        "",
        "- The completed packet demonstrates the continuous-reading framework at artifact level: every accepted unit has a selected source span, an Ingest boundary rationale, a Digest output, settlement memory uptake, and a ReadingMemory selection row.",
        "- Long-distance Unit Memory is visibly exercised in the longer books, especially Huochu, Mangge, and Xidaduo. Value of Others and Nawaer are too short under the current retrieval horizon to validate long-distance retrieval, but they still validate hot current-reading memory.",
        "- The final outputs should be judged as diagnostic evidence, not formal product evidence: it shows the mechanism working and gives enough material for human U/R and Marginalia review, but no LLM judge or evidence-catalog promotion was performed.",
        "- The recovery chain matters: the primary full-window run was partial, Nawaer completed via retry1, Xidaduo completed via continue2 after a preserved continue1 `llm_contract` failure.",
        "",
        "## Book Status",
        "",
        "| Book | Segment | Final run | Units | Stop | Marginalia | Retrieved lines | Flags | Doc |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for segment in SEGMENT_SOURCES:
        summary = segment_packets[segment.segment_id]["summary"]
        doc = f"books/{segment.segment_id}.md"
        lines.append(
            f"| {_table_text(summary.get('book_title'))} | `{segment.segment_id}` | `{summary.get('final_run_id')}` | "
            f"`{summary.get('unit_count')}` | `{summary.get('stop_reason')}` | `{summary.get('marginalia_count')}` | "
            f"`{summary.get('retrieved_line_total')}` | `{json.dumps(summary.get('quality_flag_counts', {}), ensure_ascii=False)}` | "
            f"[doc]({doc}) |"
        )
    lines.extend(["", "## Book-Level Human Notes", ""])
    for segment in SEGMENT_SOURCES:
        notes = REVIEW_NOTES.get(segment.segment_id, {})
        first_note = (notes.get("overall") or [""])[0]
        lines.append(f"- `{segment.segment_id}`: {first_note}")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "- `summary.json`: machine-readable aggregate.",
            "- `retrieval_summary.md`: Unit Memory retrieval health and examples.",
            "- `recovery_history.md`: primary / retry / continuation status and preserved failure rows.",
            "- `books/*.md`: per-book, per-unit detailed review documents.",
            "",
            "## Validation Notes",
            "",
        ]
    )
    validation_errors = packet_summary.get("validation_errors") or []
    if validation_errors:
        for error in validation_errors:
            lines.append(f"- ERROR: {error}")
    else:
        lines.append("- All planned structural count checks passed.")
    return lines


def _packet_summary(
    segment_packets: dict[str, dict[str, Any]],
    run_summaries: dict[str, dict[str, Any]],
    validation_errors: list[str],
) -> dict[str, Any]:
    totals = Counter()
    kind_totals: Counter[str] = Counter()
    flag_totals: Counter[str] = Counter()
    query_sources: Counter[str] = Counter()
    degradation_reasons: Counter[str] = Counter()
    memory_tags: Counter[str] = Counter()
    segments: list[dict[str, Any]] = []
    for segment in SEGMENT_SOURCES:
        summary = segment_packets[segment.segment_id]["summary"]
        segments.append(summary)
        for key in ("unit_count", "marginalia_count", "retrieval_rows", "selection_rows", "hot_line_total", "retrieved_line_total"):
            totals[key] += int(summary.get(key) or 0)
        kind_totals.update(summary.get("marginalia_kind_counts") or {})
        flag_totals.update(summary.get("quality_flag_counts") or {})
        query_sources.update(summary.get("query_source_counts") or {})
        degradation_reasons.update(summary.get("degradation_reason_counts") or {})
        memory_tags.update(summary.get("memory_tag_counts") or {})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "primary_run_id": PRIMARY_RUN_ID,
        "analysis_root": str(PRIMARY_ANALYSIS_ROOT.relative_to(BACKEND_ROOT)),
        "review_packet_root": str(REVIEW_PACKET_ROOT.relative_to(BACKEND_ROOT)),
        "totals": {
            "unit_count": totals["unit_count"],
            "marginalia_count": totals["marginalia_count"],
            "marginalia_kind_counts": dict(sorted(kind_totals.items())),
            "quality_flag_counts": dict(sorted(flag_totals.items())),
            "retrieval_rows": totals["retrieval_rows"],
            "selection_rows": totals["selection_rows"],
            "hot_line_total": totals["hot_line_total"],
            "retrieved_line_total": totals["retrieved_line_total"],
            "query_source_counts": dict(sorted(query_sources.items())),
            "degradation_reason_counts": dict(sorted(degradation_reasons.items())),
            "memory_tag_counts": dict(sorted(memory_tags.items())),
        },
        "segments": segments,
        "runs": run_summaries,
        "validation_errors": validation_errors,
    }


def build_packet(segment_workers: int) -> dict[str, Any]:
    raw_by_span, reviews_by_span, failure_events = _index_raw_runner_units()
    run_summaries = {source.run_id: _load_json_dict(_summary_path(source.analysis_root)) for source in RUN_SOURCES}
    segment_packets: dict[str, dict[str, Any]] = {}
    if segment_workers > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=segment_workers) as executor:
            futures = {
                executor.submit(_build_segment_packet, segment, raw_by_span, reviews_by_span): segment.segment_id
                for segment in SEGMENT_SOURCES
            }
            for future in concurrent.futures.as_completed(futures):
                segment_packets[futures[future]] = future.result()
    else:
        for segment in SEGMENT_SOURCES:
            segment_packets[segment.segment_id] = _build_segment_packet(segment, raw_by_span, reviews_by_span)
    validation_errors = _validate_packets(segment_packets)
    summary = _packet_summary(segment_packets, run_summaries, validation_errors)
    _write_json(REVIEW_PACKET_ROOT / "summary.json", summary)
    _write_markdown(REVIEW_PACKET_ROOT / "README.md", _render_readme(summary, segment_packets))
    _write_markdown(REVIEW_PACKET_ROOT / "retrieval_summary.md", _render_retrieval_summary(segment_packets))
    _write_markdown(
        REVIEW_PACKET_ROOT / "recovery_history.md",
        _render_recovery_history(run_summaries, failure_events, segment_packets),
    )
    for segment in SEGMENT_SOURCES:
        packet = segment_packets[segment.segment_id]
        _write_markdown(REVIEW_PACKET_ROOT / "books" / f"{segment.segment_id}.md", _render_book_doc(packet))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--segment-workers", type=int, default=5, help="Parallel workers for per-segment packet assembly.")
    parser.add_argument("--fail-on-validation-error", action="store_true", help="Exit nonzero when planned count checks fail.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_packet(max(1, int(args.segment_workers)))
    print(json.dumps(summary["totals"], ensure_ascii=False, indent=2))
    if args.fail_on_validation_error and summary.get("validation_errors"):
        print(json.dumps(summary["validation_errors"], ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
