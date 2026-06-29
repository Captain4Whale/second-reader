"""Analyze Marginalia precision/recall against user note cases for a smoke run."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager, nullcontext
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import signal
from typing import Any

from eval.attentional_v2 import run_user_level_selective_comparison as matching


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ID = "digest_marginalia_v19_5book_parallel_20units_20260621"
DEFAULT_ANALYSIS_ID = "digest_marginalia_v19_5book_parallel_20units"
DEFAULT_SEGMENT_IDS = (
    "xidaduo_private_zh__segment_1",
    "mangge_zhi_dao_private_zh__segment_1",
    "value_of_others_private_en__segment_1",
)


@dataclass(frozen=True)
class CoverageRange:
    segment_id: str
    start_paragraph: int
    start_offset: int
    end_paragraph: int
    end_offset: int
    successful_unit_count: int
    first_unit_index: int
    last_unit_index: int
    start_label: str
    end_label: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _cursor_label(paragraph: int, offset: int) -> str:
    return f"P{paragraph}@{offset}"


def _unit_cursor(unit: dict[str, Any], key: str) -> dict[str, Any] | None:
    source_span = unit.get("source_span")
    if not isinstance(source_span, dict):
        return None
    cursor = source_span.get(key)
    return cursor if isinstance(cursor, dict) else None


def _int(value: object) -> int:
    return int(value or 0)


def coverage_from_successful_units(segment_result: dict[str, Any]) -> CoverageRange | None:
    ok_units = [
        unit
        for unit in segment_result.get("units", [])
        if isinstance(unit, dict)
        and unit.get("status") == "ok"
        and isinstance(unit.get("source_span"), dict)
    ]
    if not ok_units:
        return None
    first = ok_units[0]
    last = ok_units[-1]
    start_cursor = _unit_cursor(first, "start_cursor")
    end_cursor = _unit_cursor(last, "end_cursor")
    if start_cursor is None or end_cursor is None:
        return None
    start_paragraph = _int(start_cursor.get("paragraph_index"))
    start_offset = _int(start_cursor.get("char_offset"))
    end_paragraph = _int(end_cursor.get("paragraph_index"))
    end_offset = _int(end_cursor.get("char_offset"))
    return CoverageRange(
        segment_id=str(segment_result.get("segment_id") or ""),
        start_paragraph=start_paragraph,
        start_offset=start_offset,
        end_paragraph=end_paragraph,
        end_offset=end_offset,
        successful_unit_count=len(ok_units),
        first_unit_index=_int(first.get("unit_index")),
        last_unit_index=_int(last.get("unit_index")),
        start_label=_cursor_label(start_paragraph, start_offset),
        end_label=_cursor_label(end_paragraph, end_offset),
    )


def slice_within_coverage(source_slice: dict[str, Any], coverage: CoverageRange) -> bool:
    paragraph = _int(source_slice.get("paragraph_index"))
    char_start = _int(source_slice.get("char_start"))
    char_end = _int(source_slice.get("char_end"))
    if paragraph <= 0 or char_end <= char_start:
        return False
    after_start = paragraph > coverage.start_paragraph or (
        paragraph == coverage.start_paragraph and char_start >= coverage.start_offset
    )
    before_end = paragraph < coverage.end_paragraph or (
        paragraph == coverage.end_paragraph and char_end <= coverage.end_offset
    )
    return after_start and before_end


def slices_within_coverage(source_slices: list[dict[str, Any]], coverage: CoverageRange) -> bool:
    return bool(source_slices) and all(slice_within_coverage(source_slice, coverage) for source_slice in source_slices)


def _note_cases_in_coverage(note_cases: list[matching.NoteCase], coverage: CoverageRange) -> list[matching.NoteCase]:
    return [
        note_case
        for note_case in note_cases
        if note_case.segment_id == coverage.segment_id
        and slices_within_coverage(note_case.source_span_slices, coverage)
    ]


def _note_case_unique_key(note_case: matching.NoteCase) -> tuple[object, ...]:
    slices: list[tuple[object, ...]] = []
    for item in note_case.source_span_slices:
        slices.append(
            (
                item.get("coordinate_system") or note_case.source_span_coordinate_system,
                item.get("segment_id") or note_case.segment_id,
                item.get("source_id") or note_case.source_id,
                _int(item.get("paragraph_index")),
                _int(item.get("char_start")),
                _int(item.get("char_end")),
            )
        )
    if slices:
        return tuple(slices)
    return (note_case.segment_id, note_case.note_case_id)


def _dedupe_note_cases_for_analysis(
    note_cases: list[matching.NoteCase],
) -> tuple[list[matching.NoteCase], dict[str, Any], dict[str, list[str]]]:
    groups: dict[tuple[object, ...], list[matching.NoteCase]] = {}
    order: list[tuple[object, ...]] = []
    for note_case in note_cases:
        key = _note_case_unique_key(note_case)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(note_case)

    deduped: list[matching.NoteCase] = []
    aliases_by_id: dict[str, list[str]] = {}
    duplicate_groups: list[dict[str, Any]] = []
    for key in order:
        group = groups[key]
        canonical = group[0]
        aliases = [item.note_case_id for item in group[1:]]
        deduped.append(canonical)
        if aliases:
            aliases_by_id[canonical.note_case_id] = aliases
            duplicate_groups.append(
                {
                    "canonical_note_case_id": canonical.note_case_id,
                    "duplicate_note_case_ids": aliases,
                    "duplicate_note_case_count": len(group) - 1,
                }
            )

    diagnostics = {
        "raw_note_case_count": len(note_cases),
        "unique_note_case_count": len(deduped),
        "duplicate_note_case_count": len(note_cases) - len(deduped),
        "duplicate_note_case_group_count": len(duplicate_groups),
        "duplicate_note_case_groups": duplicate_groups[:20],
    }
    return deduped, diagnostics, aliases_by_id


def reaction_record_to_bundle_reaction(record: dict[str, Any]) -> dict[str, Any]:
    source_quote = matching._clean_text(record.get("source_quote"))
    thought = matching._clean_text(record.get("thought")) or matching._clean_text(record.get("content"))
    return {
        "reaction_id": matching._clean_text(record.get("reaction_id")),
        "type": matching._clean_text(record.get("type")),
        "section_ref": matching._clean_text(record.get("compatibility_section_ref")),
        "anchor_quote": source_quote,
        "source_quote": source_quote,
        "content": thought,
        "target_locator": record.get("target_locator"),
        "primary_source_ref": record.get("primary_source_ref"),
    }


def _reaction_records_path(runtime_root: Path, segment_id: str) -> Path:
    return runtime_root / segment_id / "_mechanisms" / "attentional_v2" / "runtime" / "reaction_records.json"


def _eligible_reactions(
    *,
    runtime_root: Path,
    segment_id: str,
    source_id: str,
    coverage: CoverageRange,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = _reaction_records_path(runtime_root, segment_id)
    if not path.exists():
        return [], {"missing_reaction_records": str(path)}
    payload = _load_json(path)
    reactions: list[dict[str, Any]] = []
    skipped = Counter()
    for record in payload.get("records", []):
        if not isinstance(record, dict):
            continue
        reaction = reaction_record_to_bundle_reaction(record)
        if not reaction["reaction_id"]:
            skipped["missing_reaction_id"] += 1
            continue
        source_slices, source_span_resolution = matching._reaction_source_span(
            reaction,
            segment_id=segment_id,
            source_id=source_id,
        )
        if not source_slices:
            skipped["unlocatable"] += 1
            continue
        if not slices_within_coverage(source_slices, coverage):
            skipped["outside_coverage"] += 1
            continue
        reaction["source_span_slices"] = source_slices
        reaction["source_span_resolution"] = source_span_resolution
        reactions.append(reaction)
    return reactions, dict(skipped)


def _matched_reaction_ids(note_result: dict[str, Any]) -> set[str]:
    if not note_result.get("counts_for_recall"):
        return set()
    best = note_result.get("best_reaction")
    if not isinstance(best, dict):
        return set()
    ids = {
        matching._clean_text(item)
        for item in best.get("duplicate_reaction_ids", [])
        if matching._clean_text(item)
    }
    if not ids and matching._clean_text(best.get("reaction_id")):
        ids.add(matching._clean_text(best.get("reaction_id")))
    return ids


def _reaction_brief(reaction: dict[str, Any]) -> dict[str, Any]:
    return {
        "reaction_id": reaction.get("reaction_id"),
        "type": reaction.get("type"),
        "source_quote": matching._clean_text(reaction.get("source_quote") or reaction.get("anchor_quote")),
        "content": matching._clean_text(reaction.get("content")),
        "source_span_slices": reaction.get("source_span_slices", []),
        "source_span_resolution": reaction.get("source_span_resolution", ""),
    }


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


@contextmanager
def _temporary_judge_wrapper(wrapper):
    original = matching._judge_candidate_reaction
    matching._judge_candidate_reaction = wrapper
    try:
        yield
    finally:
        matching._judge_candidate_reaction = original


@contextmanager
def _alarm_timeout(seconds: int):
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _raise_timeout(_signum, _frame):
        raise TimeoutError(f"judge_timeout_{seconds}s")

    old_handler = signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def _judge_cache_key(*, note_case: matching.NoteCase, reaction: dict[str, Any]) -> str:
    return "|".join(
        [
            note_case.note_case_id,
            matching._clean_text(reaction.get("reaction_id")),
            matching._clean_text(reaction.get("overlap_relation")),
            str(reaction.get("overlap_coverage", "")),
        ]
    )


def _load_judge_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = _load_json(path)
    return {str(key): dict(value) for key, value in dict(payload).items() if isinstance(value, dict)}


def _make_cached_timeout_judge(*, cache_path: Path, timeout_seconds: int):
    original = matching._judge_candidate_reaction
    cache = _load_judge_cache(cache_path)

    def _write_cache() -> None:
        _write_json(cache_path, cache)

    def _wrapped(**kwargs):
        note_case = kwargs.get("note_case")
        reaction = kwargs.get("reaction")
        if not isinstance(note_case, matching.NoteCase) or not isinstance(reaction, dict):
            return original(**kwargs)
        key = _judge_cache_key(note_case=note_case, reaction=reaction)
        if key in cache:
            return dict(cache[key])
        try:
            with _alarm_timeout(timeout_seconds):
                result = original(**kwargs)
        except TimeoutError:
            result = matching._default_judgment(
                label="miss",
                reason=f"judge_timeout_{timeout_seconds}s",
            )
        cache[key] = dict(result)
        _write_cache()
        return result

    return _wrapped


def evaluate_segment(
    *,
    segment_result: dict[str, Any],
    dataset_note_cases: list[matching.NoteCase],
    runtime_root: Path,
    run_root: Path,
    judge_mode: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    coverage = coverage_from_successful_units(segment_result)
    if coverage is None:
        return {
            "segment_id": segment_result.get("segment_id"),
            "status": "no_successful_units",
            "coverage": None,
            "note_case_count": 0,
            "model_marginalia_count": 0,
            "matched_note_case_count": 0,
            "matched_model_marginalia_count": 0,
            "recall": None,
            "precision": None,
        }, []

    segment_id = coverage.segment_id
    source_id = str(segment_result.get("source_id") or "")
    raw_note_cases = _note_cases_in_coverage(dataset_note_cases, coverage)
    note_cases, note_case_deduplication, note_aliases_by_id = _dedupe_note_cases_for_analysis(raw_note_cases)
    eligible_reactions, reaction_diagnostics = _eligible_reactions(
        runtime_root=runtime_root,
        segment_id=segment_id,
        source_id=source_id,
        coverage=coverage,
    )
    mechanism_payload = {
        "status": "completed",
        "normalized_eval_bundle": {"reactions": eligible_reactions},
    }
    note_rows: list[dict[str, Any]] = []
    matched_note_ids: set[str] = set()
    matched_reaction_ids: set[str] = set()
    label_counts: Counter[str] = Counter()
    for note_case in note_cases:
        result = matching.evaluate_note_case_for_mechanism(
            note_case=note_case,
            mechanism_payload=mechanism_payload,
            mechanism_key="attentional_v2",
            run_root=run_root,
            judge_mode=judge_mode,
        )
        label = str(result.get("label") or "miss")
        label_counts[label] += 1
        note_match_reaction_ids = _matched_reaction_ids(result)
        if result.get("counts_for_recall"):
            matched_note_ids.add(note_case.note_case_id)
            matched_reaction_ids.update(note_match_reaction_ids)
        best = result.get("best_reaction") if isinstance(result.get("best_reaction"), dict) else {}
        note_rows.append(
            {
                "segment_id": segment_id,
                "note_case_id": note_case.note_case_id,
                "note_text": note_case.note_text,
                "source_span_text": note_case.source_span_text,
                "source_span_slices": note_case.source_span_slices,
                "duplicate_note_case_aliases": note_aliases_by_id.get(note_case.note_case_id, []),
                "label": label,
                "counts_for_recall": bool(result.get("counts_for_recall")),
                "matched_reaction_ids": sorted(note_match_reaction_ids),
                "best_reaction_id": best.get("reaction_id"),
                "best_reaction_quote": best.get("anchor_quote"),
                "best_reaction_content": best.get("content"),
                "overlap_relation": best.get("overlap_relation"),
                "overlap_coverage": best.get("overlap_coverage"),
                "judgment": result.get("judgment"),
                "span_candidate_count": result.get("span_candidate_count", 0),
            }
        )

    reaction_by_id = {str(reaction["reaction_id"]): reaction for reaction in eligible_reactions}
    false_positive_ids = sorted(set(reaction_by_id) - matched_reaction_ids)
    false_negative_rows = [row for row in note_rows if not row["counts_for_recall"]]
    summary = {
        "segment_id": segment_id,
        "book_title": segment_result.get("book_title"),
        "source_id": source_id,
        "status": segment_result.get("status"),
        "stop_reason": segment_result.get("stop_reason"),
        "coverage": asdict(coverage),
        "note_case_count": len(note_cases),
        "raw_note_case_count": len(raw_note_cases),
        "duplicate_note_case_count": len(raw_note_cases) - len(note_cases),
        "note_case_deduplication": note_case_deduplication,
        "model_marginalia_count": len(eligible_reactions),
        "matched_note_case_count": len(matched_note_ids),
        "matched_model_marginalia_count": len(matched_reaction_ids),
        "false_negative_count": len(false_negative_rows),
        "false_positive_count": len(false_positive_ids),
        "recall": _rate(len(matched_note_ids), len(note_cases)),
        "precision": _rate(len(matched_reaction_ids), len(eligible_reactions)),
        "label_counts": dict(label_counts),
        "reaction_diagnostics": reaction_diagnostics,
        "matched_reaction_ids": sorted(matched_reaction_ids),
        "false_positive_examples": [_reaction_brief(reaction_by_id[item]) for item in false_positive_ids[:8]],
        "false_negative_examples": false_negative_rows[:8],
    }
    return summary, note_rows


def _aggregate(segment_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    note_case_count = sum(int(item.get("note_case_count", 0) or 0) for item in segment_summaries)
    raw_note_case_count = sum(int(item.get("raw_note_case_count", item.get("note_case_count", 0)) or 0) for item in segment_summaries)
    duplicate_note_case_count = sum(int(item.get("duplicate_note_case_count", 0) or 0) for item in segment_summaries)
    model_marginalia_count = sum(int(item.get("model_marginalia_count", 0) or 0) for item in segment_summaries)
    matched_note_case_count = sum(int(item.get("matched_note_case_count", 0) or 0) for item in segment_summaries)
    matched_model_marginalia_count = sum(int(item.get("matched_model_marginalia_count", 0) or 0) for item in segment_summaries)
    labels = Counter()
    for item in segment_summaries:
        labels.update(item.get("label_counts") or {})
    return {
        "note_case_count": note_case_count,
        "raw_note_case_count": raw_note_case_count,
        "duplicate_note_case_count": duplicate_note_case_count,
        "model_marginalia_count": model_marginalia_count,
        "matched_note_case_count": matched_note_case_count,
        "matched_model_marginalia_count": matched_model_marginalia_count,
        "false_negative_count": note_case_count - matched_note_case_count,
        "false_positive_count": model_marginalia_count - matched_model_marginalia_count,
        "recall": _rate(matched_note_case_count, note_case_count),
        "precision": _rate(matched_model_marginalia_count, model_marginalia_count),
        "label_counts": dict(labels),
    }


def _excluded_segment_summary(segment_result: dict[str, Any]) -> dict[str, Any]:
    coverage = coverage_from_successful_units(segment_result)
    return {
        "segment_id": segment_result.get("segment_id"),
        "book_title": segment_result.get("book_title"),
        "status": segment_result.get("status"),
        "stop_reason": segment_result.get("stop_reason"),
        "successful_unit_count": coverage.successful_unit_count if coverage else 0,
        "coverage": asdict(coverage) if coverage else None,
    }


def render_report(summary: dict[str, Any], note_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Marginalia Note Precision / Recall",
        "",
        "## Summary",
        f"- run_id: `{summary['run_id']}`",
        f"- judge_mode: `{summary['judge_mode']}`",
        f"- segments: `{', '.join(summary['segment_ids'])}`",
        f"- note cases in covered windows: `{summary['aggregate']['note_case_count']}`",
        f"- raw note cases before unique-span folding: `{summary['aggregate'].get('raw_note_case_count', summary['aggregate']['note_case_count'])}`",
        f"- duplicate note cases folded: `{summary['aggregate'].get('duplicate_note_case_count', 0)}`",
        f"- model Marginalia in covered windows: `{summary['aggregate']['model_marginalia_count']}`",
        f"- matched note cases: `{summary['aggregate']['matched_note_case_count']}`",
        f"- matched model Marginalia: `{summary['aggregate']['matched_model_marginalia_count']}`",
        f"- recall: `{summary['aggregate']['recall']}`",
        f"- precision: `{summary['aggregate']['precision']}`",
        f"- labels: `{json.dumps(summary['aggregate']['label_counts'], ensure_ascii=False)}`",
        "",
        "## Segment Results",
        "",
        "| Segment | Book | Units | Coverage | Notes | Raw Notes | Duplicates Folded | Marginalia | TP Notes | TP Marginalia | Recall | Precision |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summary["segments"]:
        coverage = item.get("coverage") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item['segment_id']}`",
                    str(item.get("book_title") or ""),
                    str(coverage.get("successful_unit_count", 0)),
                    f"`{coverage.get('start_label')} -> {coverage.get('end_label')}`",
                    str(item.get("note_case_count", 0)),
                    str(item.get("raw_note_case_count", item.get("note_case_count", 0))),
                    str(item.get("duplicate_note_case_count", 0)),
                    str(item.get("model_marginalia_count", 0)),
                    str(item.get("matched_note_case_count", 0)),
                    str(item.get("matched_model_marginalia_count", 0)),
                    str(item.get("recall")),
                    str(item.get("precision")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Matched Examples", ""])
    matched = [row for row in note_rows if row.get("counts_for_recall")]
    for row in matched[:12]:
        lines.extend(
            [
                f"### `{row['segment_id']}` / `{row['note_case_id']}`",
                f"- label: `{row['label']}`",
                f"- reaction_ids: `{json.dumps(row['matched_reaction_ids'], ensure_ascii=False)}`",
                f"- duplicate aliases folded: `{json.dumps(row.get('duplicate_note_case_aliases') or [], ensure_ascii=False)}`",
                f"- human note: {json.dumps(row['source_span_text'], ensure_ascii=False)}",
                f"- model quote: {json.dumps(row.get('best_reaction_quote'), ensure_ascii=False)}",
                f"- model content: {json.dumps(row.get('best_reaction_content'), ensure_ascii=False)}",
                "",
            ]
        )
    lines.extend(["## False Negative Examples", ""])
    misses = [row for row in note_rows if not row.get("counts_for_recall")]
    for row in misses[:12]:
        reason = row.get("judgment", {}).get("reason") if isinstance(row.get("judgment"), dict) else ""
        lines.extend(
            [
                f"### `{row['segment_id']}` / `{row['note_case_id']}`",
                f"- label: `{row['label']}`",
                f"- duplicate aliases folded: `{json.dumps(row.get('duplicate_note_case_aliases') or [], ensure_ascii=False)}`",
                f"- reason: {json.dumps(reason, ensure_ascii=False)}",
                f"- human note: {json.dumps(row['source_span_text'], ensure_ascii=False)}",
                f"- best model quote: {json.dumps(row.get('best_reaction_quote'), ensure_ascii=False)}",
                "",
            ]
        )
    lines.extend(["## False Positive Examples", ""])
    for segment in summary["segments"]:
        examples = segment.get("false_positive_examples") or []
        if not examples:
            continue
        lines.append(f"### `{segment['segment_id']}`")
        for reaction in examples[:5]:
            lines.append(
                f"- `{reaction['reaction_id']}` quote={json.dumps(reaction['source_quote'], ensure_ascii=False)}"
            )
        lines.append("")
    excluded = summary.get("excluded_segments") or []
    if excluded:
        lines.extend(["## Excluded Partial Segments", ""])
        for item in excluded:
            coverage = item.get("coverage") or {}
            lines.append(
                f"- `{item['segment_id']}`: status=`{item.get('status')}`, stop_reason=`{item.get('stop_reason')}`, "
                f"successful_units=`{item.get('successful_unit_count')}`, "
                f"coverage=`{coverage.get('start_label')} -> {coverage.get('end_label')}`"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def analyze(
    *,
    run_id: str,
    analysis_id: str,
    dataset_dir: Path,
    segment_ids: tuple[str, ...],
    judge_mode: str,
    judge_timeout_seconds: int,
) -> dict[str, Any]:
    analysis_root = ROOT / "eval" / "runs" / "attentional_v2" / run_id / "analysis" / analysis_id
    raw_units_path = analysis_root / "raw" / "runner_units.json"
    runtime_root = analysis_root / "runtime"
    output_root = analysis_root / "note_precision_recall"
    runner_segments = _load_json(raw_units_path)
    if not isinstance(runner_segments, list):
        raise ValueError(f"expected list runner_units at {raw_units_path}")
    note_cases = matching._load_note_cases(dataset_dir)
    by_segment = {str(item.get("segment_id")): item for item in runner_segments if isinstance(item, dict)}
    segment_summaries: list[dict[str, Any]] = []
    all_note_rows: list[dict[str, Any]] = []
    judge_context = (
        _temporary_judge_wrapper(
            _make_cached_timeout_judge(
                cache_path=output_root / "judge_cache.json",
                timeout_seconds=judge_timeout_seconds,
            )
        )
        if judge_mode == "llm"
        else nullcontext()
    )
    with judge_context:
        for segment_id in segment_ids:
            if segment_id not in by_segment:
                raise ValueError(f"run has no segment_id {segment_id}")
            segment_summary, note_rows = evaluate_segment(
                segment_result=by_segment[segment_id],
                dataset_note_cases=note_cases,
                runtime_root=runtime_root,
                run_root=output_root,
                judge_mode=judge_mode,
            )
            segment_summaries.append(segment_summary)
            all_note_rows.extend(note_rows)
    excluded = [
        _excluded_segment_summary(segment_result)
        for segment_id, segment_result in sorted(by_segment.items())
        if segment_id not in set(segment_ids)
    ]
    summary = {
        "run_id": run_id,
        "analysis_id": analysis_id,
        "dataset_dir": str(dataset_dir),
        "judge_mode": judge_mode,
        "judge_timeout_seconds": judge_timeout_seconds if judge_mode == "llm" else None,
        "segment_ids": list(segment_ids),
        "aggregate": _aggregate(segment_summaries),
        "segments": segment_summaries,
        "excluded_segments": excluded,
        "artifacts": {
            "summary": str(output_root / "summary.json"),
            "matches": str(output_root / "matches.jsonl"),
            "report": str(output_root / "report.md"),
        },
    }
    _write_json(output_root / "summary.json", summary)
    _write_jsonl(output_root / "matches.jsonl", all_note_rows)
    (output_root / "report.md").write_text(render_report(summary, all_note_rows), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--analysis-id", default=DEFAULT_ANALYSIS_ID)
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=matching._resolve_dataset_dir(matching.MANIFEST_PATH),
    )
    parser.add_argument("--segment-id", action="append", dest="segment_ids")
    parser.add_argument("--judge-mode", choices=matching.JUDGE_MODE_VALUES, default="llm")
    parser.add_argument("--judge-timeout-seconds", type=int, default=45)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    segment_ids = tuple(args.segment_ids or DEFAULT_SEGMENT_IDS)
    summary = analyze(
        run_id=args.run_id,
        analysis_id=args.analysis_id,
        dataset_dir=args.dataset_dir.resolve(),
        segment_ids=segment_ids,
        judge_mode=args.judge_mode,
        judge_timeout_seconds=args.judge_timeout_seconds,
    )
    print(json.dumps(summary["aggregate"], ensure_ascii=False, indent=2))
    print(summary["artifacts"]["report"])


if __name__ == "__main__":
    main()
