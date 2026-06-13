#!/usr/bin/env python3
"""Run a focused live Ingest boundary probe and render a preview-window report.

This is a local diagnostic helper for inspecting the live Ingest prompt/runtime
contract over a short source region. It does not run Digest, settlement, judge,
or evidence-catalog promotion.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

DEFAULT_RUN_ID = "ingest_live_v16_token_preview_to_old_unit13_20260613"
DEFAULT_ANALYSIS_ID = "live_v16_token_preview_to_old_unit13"
DEFAULT_JOB_ID = "bgjob_ingest_live_v16_token_preview_to_old_unit13_20260613"
DEFAULT_SOURCE_RUN_ID = "attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5"
DEFAULT_SEGMENT_ID = "xidaduo_private_zh__segment_1"
DEFAULT_PROFILE_ID = "dataset_review_high_trust"
DEFAULT_STOP_PARAGRAPH = 57
DEFAULT_STOP_CHAR_OFFSET = 11


def _load_backend_env() -> None:
    env_path = BACKEND_ROOT / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    os.environ.setdefault("LLM_TARGETS_PATH", "config/llm_targets.local.json")
    os.environ.setdefault("LLM_PROFILE_BINDINGS_PATH", "config/llm_profile_bindings.local.json")


_load_backend_env()

from src.attentional_v2.prompts import ATTENTIONAL_V2_PROMPTS  # noqa: E402
from src.attentional_v2.prompts.ingest import render_ingest_prompt_xml  # noqa: E402
from src.attentional_v2.runner import (  # noqa: E402
    _build_ingest_boundary_preparation,
    prepare_next_source_unit_for_read,
)
from src.attentional_v2.schemas import (  # noqa: E402
    build_default_reader_policy,
    build_empty_active_attention,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_reaction_records,
    build_empty_reflective_frames,
)
from src.attentional_v2.source_spans import (  # noqa: E402
    cursor_less_than,
    first_cursor_for_chapter,
    normalize_cursor_for_chapter,
)
from src.iterator_reader.llm_utils import ReaderLLMError  # noqa: E402
from src.reading_runtime.llm_gateway import (  # noqa: E402
    LLMInvocationOverrides,
    eval_trace_context,
    llm_invocation_scope,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_root(run_id: str, analysis_id: str) -> Path:
    return BACKEND_ROOT / "eval" / "runs" / "attentional_v2" / run_id / "analysis" / analysis_id


def _load_existing_ok_units(analysis_root: Path) -> list[dict[str, object]]:
    """Load the leading successful checkpoint units for a focused probe resume."""
    results_path = analysis_root / "raw" / "results.json"
    if not results_path.exists():
        return []
    try:
        raw = json.loads(results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []
    units: list[dict[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            break
        if item.get("status") != "ok":
            break
        end_cursor = item.get("end_cursor")
        if not isinstance(end_cursor, Mapping) or not end_cursor:
            break
        units.append(dict(item))
    return units


def _source_root(source_run_id: str) -> Path:
    return BACKEND_ROOT / "eval" / "runs" / "attentional_v2" / source_run_id / "outputs"


def _load_segment(source_run_id: str, segment_id: str) -> dict[str, object]:
    public_dir = _source_root(source_run_id) / segment_id / "attentional_v2" / "public"
    manifest = _json_load(public_dir / "book_manifest.json")
    document = _json_load(public_dir / "book_document.json")
    chapters = [chapter for chapter in document.get("chapters", []) if isinstance(chapter, dict)]
    if not chapters:
        raise RuntimeError(f"No chapter found for {segment_id} in {public_dir}")
    return {
        "segment_id": segment_id,
        "book_title": _clean_text(manifest.get("book")) or segment_id,
        "author": _clean_text(manifest.get("author")) or "Unknown",
        "manifest": manifest,
        "chapter": chapters[0],
    }


def _cursor_str(cursor: Mapping[str, object] | None) -> str:
    if not isinstance(cursor, Mapping):
        return "-"
    return f"P{cursor.get('paragraph_index')}@{cursor.get('char_offset')}"


def _target_cursor(chapter: Mapping[str, object], paragraph_index: int, char_offset: int) -> dict[str, object]:
    return {
        "chapter_id": int(chapter.get("id") or 0),
        "chapter_ref": _clean_text(chapter.get("ref") or chapter.get("title") or "Full Content"),
        "paragraph_index": int(paragraph_index),
        "char_offset": max(0, int(char_offset)),
    }


def _trim_units_to_target(units: list[dict[str, object]], target: Mapping[str, object]) -> list[dict[str, object]]:
    trimmed: list[dict[str, object]] = []
    for unit in units:
        trimmed.append(unit)
        end_cursor = unit.get("end_cursor")
        if isinstance(end_cursor, Mapping) and not cursor_less_than(end_cursor, target):
            break
    return trimmed


def _fenced(text: object, lang: str = "") -> str:
    body = str(text or "")
    fence = "````" if "```" in body else "```"
    return f"{fence}{lang}\n{body}\n{fence}"


def _source_span(unit: Mapping[str, object]) -> dict[str, object]:
    span = unit.get("source_span")
    return dict(span) if isinstance(span, Mapping) else {}


def _end_cursor_from_prepared(prepared: Mapping[str, object]) -> dict[str, object] | None:
    selected = prepared.get("selected_source_unit")
    if not isinstance(selected, Mapping):
        return None
    span = selected.get("source_span")
    if not isinstance(span, Mapping):
        return None
    end_cursor = span.get("end_cursor")
    return dict(end_cursor) if isinstance(end_cursor, Mapping) else None


def _span_str(span: Mapping[str, object]) -> str:
    start = span.get("start_cursor") if isinstance(span.get("start_cursor"), Mapping) else {}
    end = span.get("end_cursor") if isinstance(span.get("end_cursor"), Mapping) else {}
    return f"{_cursor_str(start)} -> {_cursor_str(end)}"


def _paragraph_text_length(chapter: Mapping[str, object], paragraph_index: int) -> int:
    for paragraph in chapter.get("paragraphs", []):
        if not isinstance(paragraph, Mapping):
            continue
        if int(paragraph.get("paragraph_index", 0) or 0) == paragraph_index:
            return len(str(paragraph.get("text", "") or ""))
    return 0


def _ends_mid_paragraph(chapter: Mapping[str, object], span: Mapping[str, object]) -> bool:
    end = span.get("end_cursor") if isinstance(span.get("end_cursor"), Mapping) else {}
    if not isinstance(end, Mapping):
        return False
    paragraph_index = int(end.get("paragraph_index", 0) or 0)
    char_offset = int(end.get("char_offset", 0) or 0)
    return char_offset < _paragraph_text_length(chapter, paragraph_index)


def _preview_prompt_char_count(
    *,
    segment: Mapping[str, object],
    current_view_position: Mapping[str, object],
    current_view_content: Mapping[str, object],
) -> int:
    prompt = render_ingest_prompt_xml(
        book_title=_clean_text(segment.get("book_title")),
        author=_clean_text(segment.get("author")),
        current_view_position=dict(current_view_position),
        current_view_content=dict(current_view_content),
    )
    return len(prompt.rendered_text)


def _state_bundle() -> dict[str, dict[str, object]]:
    return {
        "local_buffer": build_empty_local_buffer(),
        "local_continuity": build_empty_local_continuity(),
        "continuation_capsule": {},
        "active_attention": build_empty_active_attention(),
        "reflective_frames": build_empty_reflective_frames(),
        "reaction_records": build_empty_reaction_records(),
    }


def _run_one_unit(
    *,
    segment: Mapping[str, object],
    cursor: Mapping[str, object],
    analysis_root: Path,
    profile_id: str,
    max_output_tokens: int,
    timeout_seconds: int,
    retry_attempts: int,
    unit_index: int,
) -> tuple[dict[str, object], dict[str, object] | None]:
    chapter = dict(segment["chapter"]) if isinstance(segment.get("chapter"), Mapping) else {}
    reader_policy = build_default_reader_policy()
    prep = _build_ingest_boundary_preparation(
        current_chapter=chapter,
        current_cursor=dict(cursor),
        reader_policy=reader_policy,
    )
    current_view_position = dict(prep.get("current_view_position", {}))
    current_view_content = dict(prep.get("current_view_content", {}))
    preview = dict(prep.get("preview", {}))
    prompt_char_count = _preview_prompt_char_count(
        segment=segment,
        current_view_position=current_view_position,
        current_view_content=current_view_content,
    )
    started = time.perf_counter()
    started_at = _now()
    state = _state_bundle()
    trace_context = eval_trace_context(
        analysis_root,
        eval_target="ingest_live_focus_probe",
        stage="ingest_focus_probe",
        node=f"unit_{unit_index:03d}",
        extra={
            "segment_id": _clean_text(segment.get("segment_id")),
            "unit_index": unit_index,
        },
    )
    overrides = LLMInvocationOverrides(
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
        retry_attempts=retry_attempts,
        max_concurrency=1,
    )
    with llm_invocation_scope(
        profile_id=profile_id,
        trace_context=trace_context,
        overrides=overrides,
        required_stable_concurrency=1,
    ):
        prepared = prepare_next_source_unit_for_read(
            current_chapter=chapter,
            current_cursor=dict(cursor),
            local_buffer=state["local_buffer"],  # type: ignore[arg-type]
            continuation_capsule=state["continuation_capsule"],
            active_attention=state["active_attention"],  # type: ignore[arg-type]
            reflective_frames=state["reflective_frames"],  # type: ignore[arg-type]
            reaction_records=state["reaction_records"],  # type: ignore[arg-type]
            local_continuity=state["local_continuity"],  # type: ignore[arg-type]
            reader_policy=reader_policy,
            output_language="zh",
            output_dir=analysis_root,
            book_title=_clean_text(segment.get("book_title")),
            author=_clean_text(segment.get("author")),
            book_id=_clean_text(segment.get("segment_id")),
        )
    duration_seconds = round(time.perf_counter() - started, 3)
    selected = dict(prepared.get("selected_source_unit", {})) if isinstance(prepared.get("selected_source_unit"), Mapping) else {}
    unitize_decision = (
        dict(prepared.get("unitize_decision", {}))
        if isinstance(prepared.get("unitize_decision"), Mapping)
        else {}
    )
    span = _source_span(selected)
    result = {
        "unit_index": unit_index,
        "status": "ok",
        "started_at": started_at,
        "finished_at": _now(),
        "duration_seconds": duration_seconds,
        "start_cursor": dict(cursor),
        "end_cursor": _end_cursor_from_prepared(prepared) or {},
        "prompt_char_count": prompt_char_count,
        "preview": {
            "preview_start_cursor": preview.get("preview_start_cursor"),
            "preview_end_cursor": preview.get("preview_end_cursor"),
            "char_count": preview.get("char_count"),
            "paragraph_count": preview.get("paragraph_count"),
            "truncated": preview.get("truncated"),
            "preview_end_reason": preview.get("preview_end_reason"),
            "estimated_token_count": preview.get("estimated_token_count"),
            "preview_token_estimator": preview.get("preview_token_estimator"),
            "paragraph_slices": preview.get("paragraph_slices"),
            "source_text": preview.get("source_text"),
        },
        "selected_source_unit": selected,
        "selected_mid_paragraph": _ends_mid_paragraph(chapter, span),
        "unitize_decision": unitize_decision,
        "ingest_trace": prepared.get("ingest_trace") if isinstance(prepared.get("ingest_trace"), list) else [],
        "memory_recalls": prepared.get("memory_recalls") if isinstance(prepared.get("memory_recalls"), list) else [],
        "memory_recalls_status": prepared.get("memory_recalls_status"),
        "unit_memory_retrieval": prepared.get("unit_memory_retrieval")
        if isinstance(prepared.get("unit_memory_retrieval"), Mapping)
        else {},
    }
    return result, _end_cursor_from_prepared(prepared)


def _error_result(
    *,
    unit_index: int,
    cursor: Mapping[str, object],
    exc: BaseException,
    prompt_char_count: int = 0,
    preview: Mapping[str, object] | None = None,
) -> dict[str, object]:
    problem_code = _clean_text(getattr(exc, "problem_code", ""))
    return {
        "unit_index": unit_index,
        "status": "fatal_llm_error" if problem_code else "fatal_error",
        "problem_code": problem_code,
        "error": str(exc),
        "started_at": _now(),
        "finished_at": _now(),
        "start_cursor": dict(cursor),
        "prompt_char_count": prompt_char_count,
        "preview": dict(preview or {}),
    }


def _run_sequence(args: argparse.Namespace) -> dict[str, object]:
    analysis_root = _run_root(args.run_id, args.analysis_id)
    segment = _load_segment(args.source_run_id, args.segment_id)
    chapter = dict(segment["chapter"]) if isinstance(segment.get("chapter"), Mapping) else {}
    target = _target_cursor(chapter, args.stop_paragraph, args.stop_char_offset)
    cursor = first_cursor_for_chapter(chapter)
    unit_limit = max(1, int(args.smoke_units if args.run_mode == "smoke" else args.max_units))
    units: list[dict[str, object]] = []
    if args.resume_existing:
        units = _trim_units_to_target(_load_existing_ok_units(analysis_root), target)
        if units:
            last_end_cursor = units[-1].get("end_cursor")
            if isinstance(last_end_cursor, Mapping):
                cursor = normalize_cursor_for_chapter(chapter, last_end_cursor)
                print(
                    f"[resume] accepted_units={len(units)} cursor={_cursor_str(cursor)}",
                    flush=True,
                )
    started_at = _now()
    stop_reason = "unit_limit"
    complete = False
    if units and not cursor_less_than(cursor, target):
        stop_reason = "target_reached"
        complete = True
    for unit_index in range(len(units) + 1, unit_limit + 1):
        if complete:
            break
        cursor = normalize_cursor_for_chapter(chapter, cursor)
        print(f"[unit-start] {args.segment_id} #{unit_index} cursor={_cursor_str(cursor)}", flush=True)
        try:
            unit, next_cursor = _run_one_unit(
                segment=segment,
                cursor=cursor,
                analysis_root=analysis_root,
                profile_id=args.profile_id,
                max_output_tokens=args.max_output_tokens,
                timeout_seconds=args.timeout_seconds,
                retry_attempts=args.retry_attempts,
                unit_index=unit_index,
            )
        except ReaderLLMError as exc:
            unit = _error_result(unit_index=unit_index, cursor=cursor, exc=exc)
            units.append(unit)
            stop_reason = _clean_text(getattr(exc, "problem_code", "")) or "reader_llm_error"
            print(f"[unit-error] #{unit_index} problem={stop_reason} error={exc}", flush=True)
            break
        except Exception as exc:  # noqa: BLE001
            unit = _error_result(unit_index=unit_index, cursor=cursor, exc=exc)
            units.append(unit)
            stop_reason = "exception"
            print(f"[unit-error] #{unit_index} error={exc}", flush=True)
            break
        units.append(unit)
        selected = unit.get("selected_source_unit") if isinstance(unit.get("selected_source_unit"), Mapping) else {}
        print(
            f"[unit-done] #{unit_index} status={unit.get('status')} span={_span_str(_source_span(selected))} "
            f"preview_tokens={(unit.get('preview') or {}).get('estimated_token_count') if isinstance(unit.get('preview'), Mapping) else '-'}",
            flush=True,
        )
        if not next_cursor:
            stop_reason = "missing_end_cursor"
            break
        if not cursor_less_than(cursor, next_cursor):
            stop_reason = "non_advancing_cursor"
            break
        cursor = next_cursor
        if not cursor_less_than(cursor, target):
            stop_reason = "target_reached"
            complete = True
            break
    else:
        if args.run_mode == "smoke":
            stop_reason = "smoke_unit_limit"
        else:
            stop_reason = "max_units"
    if args.run_mode == "smoke" and units and units[-1].get("status") == "ok":
        complete = False
        stop_reason = "smoke_ok"
    return {
        "run_id": args.run_id,
        "analysis_id": args.analysis_id,
        "job_id": args.job_id,
        "source_run_id": args.source_run_id,
        "segment_id": args.segment_id,
        "book_title": segment.get("book_title"),
        "author": segment.get("author"),
        "profile_id": args.profile_id,
        "prompt_version": ATTENTIONAL_V2_PROMPTS.ingest_version,
        "promptset_version": ATTENTIONAL_V2_PROMPTS.promptset_version,
        "started_at": started_at,
        "finished_at": _now(),
        "run_mode": args.run_mode,
        "resume_existing": bool(args.resume_existing),
        "stop_target_cursor": target,
        "stop_reason": stop_reason,
        "complete": complete,
        "unit_count": len(units),
        "units": units,
        "llm_trace_standard": str((analysis_root / "llm_traces" / "standard.jsonl").relative_to(BACKEND_ROOT)),
    }


def _partition_table(partitions: list[dict[str, object]]) -> list[str]:
    if not partitions:
        return ["- preview_partition: none"]
    lines = [
        "| # | title | status | end_paragraph_n | end_at |",
        "|---:|---|---|---:|---|",
    ]
    for index, item in enumerate(partitions, start=1):
        lines.append(
            f"| {index} | {_clean_text(item.get('title'))} | `{_clean_text(item.get('status'))}` | "
            f"`{_clean_text(item.get('end_paragraph_n'))}` | `{_clean_text(item.get('end_at'))}` |"
        )
    return lines


def _audit_table(partitions: list[dict[str, object]]) -> list[str]:
    if not partitions:
        return ["- preview_partition_audit: none"]
    lines = [
        "| # | title | resolution | span | status |",
        "|---:|---|---|---|---|",
    ]
    for index, item in enumerate(partitions, start=1):
        source_span = item.get("source_span") if isinstance(item.get("source_span"), Mapping) else {}
        resolution = item.get("resolution") if isinstance(item.get("resolution"), Mapping) else {}
        lines.append(
            f"| {index} | {_clean_text(item.get('title'))} | "
            f"`{_clean_text(resolution.get('status') if isinstance(resolution, Mapping) else '')}` | "
            f"`{_span_str(source_span)}` | `{_clean_text(item.get('status'))}` |"
        )
    return lines


def _preview_slices_table(slices: list[dict[str, object]]) -> list[str]:
    lines = [
        "| n | role | start_char | end_char | chars | text preview |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for item in slices:
        text = str(item.get("text", "") or "")
        preview = _clean_text(text[:120])
        if len(text) > 120:
            preview += "..."
        lines.append(
            f"| {item.get('paragraph_index')} | `{_clean_text(item.get('text_role'))}` | "
            f"{item.get('start_char', '')} | {item.get('end_char', '')} | {len(text)} | {preview} |"
        )
    return lines


def _recall_lines(recalls: list[dict[str, object]]) -> list[str]:
    if not recalls:
        return ["- memory_recalls: none"]
    lines = ["- memory_recalls:"]
    for recall in recalls:
        lines.append(
            f"  - `{_clean_text(recall.get('recall_id'))}`: {_clean_text(recall.get('recall_text'))} "
            f"(`basis={_clean_text(recall.get('basis'))}`)"
        )
    return lines


def _unit_markdown(chapter: Mapping[str, object], unit: Mapping[str, object]) -> list[str]:
    selected = unit.get("selected_source_unit") if isinstance(unit.get("selected_source_unit"), Mapping) else {}
    selected = dict(selected) if isinstance(selected, Mapping) else {}
    span = _source_span(selected)
    decision = unit.get("unitize_decision") if isinstance(unit.get("unitize_decision"), Mapping) else {}
    decision = dict(decision) if isinstance(decision, Mapping) else {}
    preview = unit.get("preview") if isinstance(unit.get("preview"), Mapping) else {}
    preview = dict(preview) if isinstance(preview, Mapping) else {}
    resolution = decision.get("resolution") if isinstance(decision.get("resolution"), Mapping) else {}
    partitions = [dict(item) for item in decision.get("preview_partition", []) if isinstance(item, Mapping)] if isinstance(decision.get("preview_partition"), list) else []
    audit = [dict(item) for item in decision.get("preview_partition_audit", []) if isinstance(item, Mapping)] if isinstance(decision.get("preview_partition_audit"), list) else []
    selected_mid = _ends_mid_paragraph(chapter, span)
    lines = [
        f"## Unit {int(unit.get('unit_index', 0) or 0):03d}",
        "",
        "### Status And Boundary",
        "",
        f"- status: `{unit.get('status')}`",
        f"- problem_code: `{unit.get('problem_code', '')}`",
        f"- start cursor: `{_cursor_str(unit.get('start_cursor') if isinstance(unit.get('start_cursor'), Mapping) else {})}`",
        f"- selected span: `{_span_str(span)}`",
        f"- source_span_id: `{_clean_text(selected.get('source_span_id'))}`",
        f"- selected chars: `{selected.get('char_count', '')}`",
        f"- selected paragraphs: `{selected.get('paragraph_count', '')}`",
        f"- selected mid_paragraph: `{selected_mid}`",
        f"- resolution: `{_clean_text(resolution.get('status') if isinstance(resolution, Mapping) else '')}` / "
        f"`{_clean_text(resolution.get('method') if isinstance(resolution, Mapping) else '')}`",
        f"- prompt_char_count: `{unit.get('prompt_char_count', '')}`",
        f"- duration_seconds: `{unit.get('duration_seconds', '')}`",
        f"- preview_partition_count: `{len(partitions)}`",
        f"- preview_partition_audit_status: `{_clean_text(decision.get('preview_partition_audit_status'))}`",
        f"- reason: {_clean_text(decision.get('reason')) or '-'}",
    ]
    recalls = [dict(item) for item in unit.get("memory_recalls", []) if isinstance(item, Mapping)] if isinstance(unit.get("memory_recalls"), list) else []
    lines.extend(_recall_lines(recalls))
    if unit.get("error"):
        lines.extend(["", "Error:", "", _fenced(unit.get("error"))])
    lines.extend(
        [
            "",
            "### Preview Window",
            "",
            f"- preview span: `{_cursor_str(preview.get('preview_start_cursor') if isinstance(preview.get('preview_start_cursor'), Mapping) else {})} -> "
            f"{_cursor_str(preview.get('preview_end_cursor') if isinstance(preview.get('preview_end_cursor'), Mapping) else {})}`",
            f"- preview chars: `{preview.get('char_count', '')}`",
            f"- preview estimated tokens: `{preview.get('estimated_token_count', '')}`",
            f"- preview token estimator: `{_clean_text(preview.get('preview_token_estimator'))}`",
            f"- preview paragraphs: `{preview.get('paragraph_count', '')}`",
            f"- truncated: `{preview.get('truncated', '')}`",
            f"- preview_end_reason: `{_clean_text(preview.get('preview_end_reason'))}`",
            "",
            "#### Preview Partition",
            "",
        ]
    )
    lines.extend(_partition_table(partitions))
    lines.extend(["", "#### Preview Partition Audit", ""])
    lines.extend(_audit_table(audit))
    slices = [dict(item) for item in preview.get("paragraph_slices", []) if isinstance(item, Mapping)] if isinstance(preview.get("paragraph_slices"), list) else []
    lines.extend(["", "#### Preview Paragraph Slices", ""])
    if slices:
        lines.extend(_preview_slices_table(slices))
    else:
        lines.append("- none")
    lines.extend(["", "#### Preview Source Text", "", _fenced(preview.get("source_text", "")), ""])
    lines.extend(["### Selected Source Unit", "", _fenced(selected.get("source_text", "")), ""])
    return lines


def _write_report(sequence: Mapping[str, object], analysis_root: Path) -> Path:
    segment_id = _clean_text(sequence.get("segment_id"))
    report_dir = analysis_root / "preview_window_review" / "segments" / segment_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{sequence.get('analysis_id')}_preview_units.md"
    segment = _load_segment(_clean_text(sequence.get("source_run_id")), segment_id)
    chapter = dict(segment["chapter"]) if isinstance(segment.get("chapter"), Mapping) else {}
    units = [dict(item) for item in sequence.get("units", []) if isinstance(item, Mapping)] if isinstance(sequence.get("units"), list) else []
    lines = [
        f"# {segment_id} - {sequence.get('analysis_id')} - Preview Window Review",
        "",
        f"- run_id: `{sequence.get('run_id')}`",
        f"- source_run_id: `{sequence.get('source_run_id')}`",
        f"- profile_id: `{sequence.get('profile_id')}`",
        f"- complete: `{sequence.get('complete')}`",
        f"- stop_reason: `{sequence.get('stop_reason')}`",
        f"- unit_count: `{sequence.get('unit_count')}`",
        f"- prompt: `{sequence.get('prompt_version')}` / promptset `{sequence.get('promptset_version')}`",
        f"- stop target: old Unit 013 end `{_cursor_str(sequence.get('stop_target_cursor') if isinstance(sequence.get('stop_target_cursor'), Mapping) else {})}`",
        f"- llm trace: `{sequence.get('llm_trace_standard')}`",
        "- scope: local diagnostic only; no Digest, settlement, judge, evidence catalog update, or historical v15 rerun.",
        "",
        "Each unit includes the full runtime preview visible from the cursor under the current token-bounded preview policy, plus the resolved selected source unit. Later `preview_partition[]` entries are audit/planning metadata only.",
        "",
        "## Summary",
        "",
        "| Unit | Status | Span | Selected chars | Preview tokens | Preview end | Partition count |",
        "|---:|---|---|---:|---:|---|---:|",
    ]
    for unit in units:
        selected = unit.get("selected_source_unit") if isinstance(unit.get("selected_source_unit"), Mapping) else {}
        preview = unit.get("preview") if isinstance(unit.get("preview"), Mapping) else {}
        decision = unit.get("unitize_decision") if isinstance(unit.get("unitize_decision"), Mapping) else {}
        partitions = decision.get("preview_partition") if isinstance(decision, Mapping) else []
        lines.append(
            f"| {unit.get('unit_index')} | `{unit.get('status')}` | `{_span_str(_source_span(selected if isinstance(selected, Mapping) else {}))}` | "
            f"{selected.get('char_count', '') if isinstance(selected, Mapping) else ''} | "
            f"{preview.get('estimated_token_count', '') if isinstance(preview, Mapping) else ''} | "
            f"`{_clean_text(preview.get('preview_end_reason') if isinstance(preview, Mapping) else '')}` | "
            f"{len(partitions) if isinstance(partitions, list) else 0} |"
        )
    lines.append("")
    for unit in units:
        lines.extend(_unit_markdown(chapter, unit))
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def _write_outputs(sequence: Mapping[str, object], analysis_root: Path) -> Path:
    report_path = _write_report(sequence, analysis_root)
    _json_dump(analysis_root / "raw" / "results.json", sequence.get("units", []))
    summary_rows = []
    for unit in sequence.get("units", []):
        if not isinstance(unit, Mapping):
            continue
        selected = unit.get("selected_source_unit") if isinstance(unit.get("selected_source_unit"), Mapping) else {}
        preview = unit.get("preview") if isinstance(unit.get("preview"), Mapping) else {}
        summary_rows.append(
            {
                "unit_index": unit.get("unit_index"),
                "status": unit.get("status"),
                "span": _span_str(_source_span(selected if isinstance(selected, Mapping) else {})),
                "selected_char_count": selected.get("char_count") if isinstance(selected, Mapping) else None,
                "preview_char_count": preview.get("char_count") if isinstance(preview, Mapping) else None,
                "preview_estimated_token_count": preview.get("estimated_token_count") if isinstance(preview, Mapping) else None,
                "preview_end_reason": preview.get("preview_end_reason") if isinstance(preview, Mapping) else None,
                "prompt_char_count": unit.get("prompt_char_count"),
                "duration_seconds": unit.get("duration_seconds"),
            }
        )
    _json_dump(analysis_root / "raw" / "summary_rows.json", summary_rows)
    meta = {key: value for key, value in sequence.items() if key != "units"}
    meta["report_path"] = str(report_path.relative_to(BACKEND_ROOT))
    meta["raw_results_path"] = str((analysis_root / "raw" / "results.json").relative_to(BACKEND_ROOT))
    _json_dump(analysis_root / "run_meta.json", meta)
    return report_path


def _status_payload(
    sequence: Mapping[str, object] | None,
    *,
    args: argparse.Namespace,
    status: str,
    report_path: Path | None = None,
    error: str = "",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "run_id": args.run_id,
        "analysis_id": args.analysis_id,
        "job_id": args.job_id,
        "status": status,
        "updated_at": _now(),
        "mode": args.run_mode,
    }
    if sequence is not None:
        payload.update(
            {
                "complete": bool(sequence.get("complete")),
                "stop_reason": sequence.get("stop_reason"),
                "unit_count": sequence.get("unit_count"),
                "prompt_version": sequence.get("prompt_version"),
                "promptset_version": sequence.get("promptset_version"),
            }
        )
    if report_path is not None:
        payload["report_path"] = str(report_path.relative_to(BACKEND_ROOT))
    if error:
        payload["error"] = error
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--analysis-id", default=DEFAULT_ANALYSIS_ID)
    parser.add_argument("--job-id", default=DEFAULT_JOB_ID)
    parser.add_argument("--source-run-id", default=DEFAULT_SOURCE_RUN_ID)
    parser.add_argument("--segment-id", default=DEFAULT_SEGMENT_ID)
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--run-mode", choices=["smoke", "full"], default="full")
    parser.add_argument("--smoke-units", type=int, default=1)
    parser.add_argument("--max-units", type=int, default=80)
    parser.add_argument("--stop-paragraph", type=int, default=DEFAULT_STOP_PARAGRAPH)
    parser.add_argument("--stop-char-offset", type=int, default=DEFAULT_STOP_CHAR_OFFSET)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--retry-attempts", type=int, default=3)
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help="Continue from the leading successful units in raw/results.json.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analysis_root = _run_root(args.run_id, args.analysis_id)
    status_file = analysis_root / "status.json"
    _json_dump(status_file, _status_payload(None, args=args, status="running"))
    try:
        sequence = _run_sequence(args)
        report_path = _write_outputs(sequence, analysis_root)
        terminal_status = "completed"
        if sequence.get("units"):
            last = sequence["units"][-1]  # type: ignore[index]
            if isinstance(last, Mapping) and str(last.get("status") or "").startswith("fatal"):
                terminal_status = "failed"
        _json_dump(status_file, _status_payload(sequence, args=args, status=terminal_status, report_path=report_path))
        print(f"[report] {report_path}", flush=True)
        return 0 if terminal_status == "completed" else 1
    except Exception as exc:  # noqa: BLE001
        _json_dump(status_file, _status_payload(None, args=args, status="failed", error=str(exc)))
        print(f"[failed] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
