#!/usr/bin/env python3
"""Run a focused multi-book validation of Source Normalization v1.1."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import shutil
import sys
import traceback
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reading_core.runtime_contracts import ParseRequest  # noqa: E402
from src.reading_core.storage import book_document_file  # noqa: E402
from src.reading_runtime import parse_book  # noqa: E402
from src.reading_runtime.output_dir_overrides import override_output_dir  # noqa: E402
from src.reading_runtime.source_normalization import SOURCE_NORMALIZATION_VERSION  # noqa: E402


RUN_ID = "source_normalization_v1_1_multibook_validation_20260613"
DEFAULT_RUN_DIR = ROOT / "state" / "source_normalization_probe" / RUN_ID
DEFAULT_SMOKE_BOOKS = ["zh/beiying_public_v2.epub"]
DEFAULT_SUITE_BOOKS = [
    "zh/xidaduo.epub",
    "zh/nawaer_baodian.epub",
    "zh/mangge_zhi_dao.epub",
    "zh/huochu_shengming_de_yiyi.epub",
    "zh/jinghua_yuan_25377.epub",
    "zh/rulin_waishi_24032.epub",
    "en/pride_and_prejudice_1342.epub",
    "en/moby_dick_2701.epub",
    "en/the_varieties_of_religious_experience_public_v2.epub",
    "en/private/the_almanack_of_naval_ravikant.epub",
]

HIGH_RISK_TEXT_LIMIT = 300
MAX_SAMPLE_ITEMS = 20


@dataclass(frozen=True)
class BookTask:
    """One source-normalization validation target."""

    source_ref: str
    path: Path
    output_dir: Path


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_id(source_ref: str) -> str:
    return (
        source_ref.replace("/", "__")
        .replace("\\", "__")
        .replace(" ", "_")
        .replace(".epub", "")
        .replace(".", "_")
    )


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _text(value: object) -> str:
    return str(value or "").strip()


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _paragraphs(document: Mapping[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    chapters = document.get("chapters", [])
    if not isinstance(chapters, list):
        return rows
    for chapter in chapters:
        if not isinstance(chapter, Mapping):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        chapter_title = _text(chapter.get("title"))
        for paragraph in chapter.get("paragraphs", []):
            if not isinstance(paragraph, Mapping):
                continue
            row = dict(paragraph)
            row["_chapter_id"] = chapter_id
            row["_chapter_title"] = chapter_title
            rows.append(row)
    return rows


def _normalization_metadata(paragraph: Mapping[str, object]) -> dict[str, object]:
    metadata = paragraph.get("source_normalization")
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def _evidence(paragraph: Mapping[str, object]) -> dict[str, object]:
    evidence = _normalization_metadata(paragraph).get("evidence")
    return dict(evidence) if isinstance(evidence, Mapping) else {}


def _signals(paragraph: Mapping[str, object]) -> list[str]:
    return _string_list(_evidence(paragraph).get("signals"))


def _compact_paragraph(paragraph: Mapping[str, object]) -> dict[str, object]:
    metadata = _normalization_metadata(paragraph)
    evidence = _evidence(paragraph)
    text = _text(paragraph.get("text"))
    return {
        "chapter_id": paragraph.get("_chapter_id"),
        "chapter_title": paragraph.get("_chapter_title"),
        "paragraph_index": paragraph.get("paragraph_index"),
        "text_role": paragraph.get("text_role"),
        "normalized_role": metadata.get("normalized_role"),
        "kind": metadata.get("kind"),
        "method": metadata.get("method"),
        "reason_code": metadata.get("reason_code"),
        "confidence": metadata.get("confidence"),
        "signals": evidence.get("signals"),
        "ancestor_tags": paragraph.get("ancestor_tags"),
        "ancestor_html_classes": paragraph.get("ancestor_html_classes"),
        "inline_anchor_ids": paragraph.get("inline_anchor_ids"),
        "inline_anchor_hrefs": paragraph.get("inline_anchor_hrefs"),
        "text_len": len(text),
        "text": text[:500],
    }


def _starts_like_quote_or_dialogue(text: str) -> bool:
    return bool(text) and text[0] in {'"', "'", "“", "‘", "「", "『", "《", "（", "("}


def _starts_like_note_definition(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("[") or stripped.startswith("［") or stripped.startswith("(") or stripped.startswith("（")


def _looks_like_numbered_body(text: str) -> bool:
    stripped = text.lstrip()
    if len(stripped) < 12:
        return False
    return bool(stripped[:4].replace(".", "").replace("、", "").strip()[:1].isdigit())


def _risk_samples(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    long_auxiliary: list[dict[str, object]] = []
    protected_form_auxiliary: list[dict[str, object]] = []
    unbacked_layout_noise: list[dict[str, object]] = []
    body_aux_marker: list[dict[str, object]] = []
    duplicate_text_candidates: list[dict[str, object]] = []
    numbered_body: list[dict[str, object]] = []

    text_counter: Counter[str] = Counter(_text(row.get("text")) for row in rows if len(_text(row.get("text"))) >= 20)
    duplicate_texts = {text for text, count in text_counter.items() if count > 1}

    for row in rows:
        text = _text(row.get("text"))
        text_role = _text(row.get("text_role")) or "body"
        metadata = _normalization_metadata(row)
        normalized_role = _text(metadata.get("normalized_role"))
        kind = _text(metadata.get("kind"))
        reason_code = _text(metadata.get("reason_code"))
        signals = set(_signals(row))
        ancestor_tags = set(_string_list(row.get("ancestor_tags")))
        ancestor_classes = set(_string_list(row.get("ancestor_html_classes")))

        if text_role == "auxiliary" and len(text) >= HIGH_RISK_TEXT_LIMIT:
            long_auxiliary.append(_compact_paragraph(row))
        if text_role == "auxiliary" and (
            "literary_container" in signals
            or "blockquote" in ancestor_tags
            or {"poem", "poetry", "verse", "stanza", "letter"}.intersection(ancestor_classes)
            or _starts_like_quote_or_dialogue(text)
        ):
            protected_form_auxiliary.append(_compact_paragraph(row))
        if text_role == "auxiliary" and normalized_role == "layout_noise" and not {
            "short_layout_noise_candidate",
            "duplicate_heading_candidate",
        }.intersection(signals):
            unbacked_layout_noise.append(_compact_paragraph(row))
        if text_role != "auxiliary" and {
            "html_auxiliary_marker",
            "inline_note_definition_anchor",
            "linked_note_definition",
            "reference_like",
        }.intersection(signals):
            body_aux_marker.append(_compact_paragraph(row))
        if text in duplicate_texts:
            duplicate_text_candidates.append(_compact_paragraph(row))
        if text_role != "auxiliary" and _starts_like_note_definition(text) and (
            "note" in kind.lower() or "note" in reason_code.lower() or "html_auxiliary_marker" in signals
        ):
            body_aux_marker.append(_compact_paragraph(row))
        if text_role != "auxiliary" and _looks_like_numbered_body(text):
            numbered_body.append(_compact_paragraph(row))

    return {
        "long_auxiliary": long_auxiliary[:MAX_SAMPLE_ITEMS],
        "protected_form_auxiliary": protected_form_auxiliary[:MAX_SAMPLE_ITEMS],
        "unbacked_layout_noise": unbacked_layout_noise[:MAX_SAMPLE_ITEMS],
        "body_aux_marker": body_aux_marker[:MAX_SAMPLE_ITEMS],
        "duplicate_text_candidates": duplicate_text_candidates[:MAX_SAMPLE_ITEMS],
        "numbered_body": numbered_body[:MAX_SAMPLE_ITEMS],
    }


def _known_xidaduo_checks(source_ref: str, rows: list[dict[str, object]]) -> dict[str, bool] | None:
    if source_ref != "zh/xidaduo.epub":
        return None
    c3_notes = [
        row for row in rows
        if int(row.get("_chapter_id", 0) or 0) == 3 and _text(row.get("text")).startswith("[")
    ]
    c4_magadha = [
        row for row in rows
        if int(row.get("_chapter_id", 0) or 0) == 4 and "Magadha" in _text(row.get("text"))
    ]
    c8_poem = [
        row for row in rows
        if int(row.get("_chapter_id", 0) or 0) == 8
        and any(token in _text(row.get("text")) for token in ["多茵", "麦褐色的沙门", "莲花盛放", "扪心示敬", "迦摩罗含笑", "献祭诸神", "献身美丽"])
    ]
    duplicate_poem_exclusions = [
        row for row in rows
        if int(row.get("_chapter_id", 0) or 0) == 8
        and (
            _text(_normalization_metadata(row).get("kind")) == "duplicate_poem_line"
            or _text(_normalization_metadata(row).get("reason_code")) == "duplicate_poem_line"
        )
    ]
    return {
        "c3_notes_auxiliary": bool(c3_notes) and all(_text(row.get("text_role")) == "auxiliary" for row in c3_notes),
        "c4_magadha_auxiliary": bool(c4_magadha) and all(_text(row.get("text_role")) == "auxiliary" for row in c4_magadha),
        "c8_poem_lines_body": bool(c8_poem) and all(_text(row.get("text_role")) == "body" for row in c8_poem),
        "c8_no_duplicate_poem_line_exclusions": not duplicate_poem_exclusions,
    }


def _status_from_analysis(
    *,
    diagnostics: Mapping[str, object],
    risk_samples: Mapping[str, list[dict[str, object]]],
    known_checks: Mapping[str, bool] | None,
) -> str:
    source_diag = diagnostics.get("source_normalization")
    source_diag = source_diag if isinstance(source_diag, Mapping) else {}
    if source_diag.get("status") == "degraded":
        return "failed"
    if known_checks and not all(bool(value) for value in known_checks.values()):
        return "failed"
    critical_keys = ["protected_form_auxiliary", "unbacked_layout_noise"]
    if any(risk_samples.get(key) for key in critical_keys):
        return "needs_review"
    return "passed"


def _render_table(items: list[dict[str, object]], *, limit: int = 8) -> list[str]:
    if not items:
        return ["_None._"]
    lines = ["| Chapter | P | Role | Normalized | Reason | Signals | Text |", "| --- | ---: | --- | --- | --- | --- | --- |"]
    for item in items[:limit]:
        text = _text(item.get("text")).replace("|", "\\|").replace("\n", " ")
        if len(text) > 140:
            text = f"{text[:137]}..."
        signals = ", ".join(_string_list(item.get("signals")))[:120]
        lines.append(
            "| "
            f"{item.get('chapter_id')} {str(item.get('chapter_title') or '')[:18]} | "
            f"{item.get('paragraph_index')} | "
            f"{item.get('text_role')} | "
            f"{item.get('normalized_role')}/{item.get('kind')} | "
            f"{item.get('reason_code')} | "
            f"{signals} | "
            f"{text} |"
        )
    return lines


def _write_book_review(
    *,
    task: BookTask,
    output_dir: Path,
    result: Mapping[str, object],
    risk_samples: Mapping[str, list[dict[str, object]]],
) -> None:
    lines = [
        f"# Source Normalization V1.1 Review: `{task.source_ref}`",
        "",
        f"- Status: `{result.get('status')}`",
        f"- Source: `{task.path}`",
        f"- Output dir: `{output_dir}`",
        f"- Source Normalization: `{SOURCE_NORMALIZATION_VERSION}`",
        f"- Duration seconds: `{result.get('duration_seconds')}`",
        "",
        "## Counts",
        "",
        f"- text_role: `{result.get('text_role_counts')}`",
        f"- normalized_role: `{result.get('normalized_role_counts')}`",
        f"- method: `{result.get('method_counts')}`",
        f"- reason_code top: `{result.get('reason_code_counts')}`",
        f"- signal top: `{result.get('signal_counts')}`",
    ]
    known = result.get("known_xidaduo_checks")
    if isinstance(known, Mapping):
        lines.extend(["", "## Known Siddhartha Checks", ""])
        for key, value in known.items():
            lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Risk Samples", ""])
    for key, items in risk_samples.items():
        lines.extend([f"### `{key}`", "", *_render_table(items), ""])
    (output_dir / "source_normalization_v1_1_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _analyze_output(task: BookTask, output_dir: Path, *, started_at: datetime) -> dict[str, object]:
    document_path = book_document_file(output_dir)
    document = _load_json(document_path)
    rows = _paragraphs(document)
    diagnostics = _load_json(output_dir / "_mechanisms" / "iterator_v1" / "internal" / "diagnostics" / "parse.json")
    risk_samples = _risk_samples(rows)
    known_checks = _known_xidaduo_checks(task.source_ref, rows)

    text_role_counts = Counter(_text(row.get("text_role")) or "body" for row in rows)
    normalized_role_counts = Counter(_text(_normalization_metadata(row).get("normalized_role")) for row in rows)
    method_counts = Counter(_text(_normalization_metadata(row).get("method")) for row in rows)
    reason_code_counts = Counter(_text(_normalization_metadata(row).get("reason_code")) for row in rows)
    signal_counts: Counter[str] = Counter()
    for row in rows:
        signal_counts.update(_signals(row))
    status = _status_from_analysis(
        diagnostics=diagnostics,
        risk_samples=risk_samples,
        known_checks=known_checks,
    )
    completed_at = datetime.now(timezone.utc)
    result: dict[str, object] = {
        "source_ref": task.source_ref,
        "source_path": str(task.path),
        "output_dir": str(output_dir),
        "status": status,
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round((completed_at - started_at).total_seconds(), 3),
        "chapter_count": len(document.get("chapters", [])) if isinstance(document.get("chapters"), list) else 0,
        "paragraph_count": len(rows),
        "text_role_counts": dict(sorted(text_role_counts.items())),
        "normalized_role_counts": dict(sorted(normalized_role_counts.items())),
        "method_counts": dict(sorted(method_counts.items())),
        "reason_code_counts": dict(reason_code_counts.most_common(20)),
        "signal_counts": dict(signal_counts.most_common(20)),
        "risk_counts": {key: len(items) for key, items in risk_samples.items()},
        "known_xidaduo_checks": known_checks,
        "diagnostics_status": (diagnostics.get("source_normalization") or {}).get("status")
        if isinstance(diagnostics.get("source_normalization"), Mapping)
        else None,
    }
    _write_json(output_dir / "source_normalization_v1_1_result.json", result)
    _write_book_review(task=task, output_dir=output_dir, result=result, risk_samples=risk_samples)
    return result


def _run_one_book(task: BookTask, *, retry: int, clean: bool) -> dict[str, object]:
    attempts: list[dict[str, object]] = []
    for attempt in range(1, retry + 2):
        started_at = datetime.now(timezone.utc)
        try:
            if clean and task.output_dir.exists():
                shutil.rmtree(task.output_dir)
            task.output_dir.mkdir(parents=True, exist_ok=True)
            with override_output_dir(task.output_dir):
                parse_book(
                    ParseRequest(
                        book_path=task.path,
                        language_mode="auto",
                        mechanism_key="attentional_v2",
                    )
                )
            result = _analyze_output(task, task.output_dir, started_at=started_at)
            result["attempt"] = attempt
            result["attempts"] = attempts
            return result
        except Exception as exc:  # pragma: no cover - exercised by live validation failures
            attempts.append(
                {
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback_tail": traceback.format_exc().splitlines()[-12:],
                }
            )
            if attempt > retry:
                completed_at = datetime.now(timezone.utc)
                result = {
                    "source_ref": task.source_ref,
                    "source_path": str(task.path),
                    "output_dir": str(task.output_dir),
                    "status": "failed",
                    "started_at": started_at.isoformat().replace("+00:00", "Z"),
                    "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
                    "duration_seconds": round((completed_at - started_at).total_seconds(), 3),
                    "attempt": attempt,
                    "attempts": attempts,
                }
                _write_json(task.output_dir / "source_normalization_v1_1_result.json", result)
                return result
    raise AssertionError("unreachable")


def _book_tasks(source_refs: Iterable[str], run_dir: Path) -> list[BookTask]:
    tasks: list[BookTask] = []
    root = ROOT / "state" / "library_sources"
    for source_ref in source_refs:
        path = root / source_ref
        if not path.exists():
            raise FileNotFoundError(f"Missing source book: {path}")
        tasks.append(BookTask(source_ref=source_ref, path=path, output_dir=run_dir / "books" / _safe_id(source_ref)))
    return tasks


def _suite_outcome(results: list[dict[str, object]]) -> str:
    if any(result.get("status") == "failed" for result in results):
        return "failed"
    if any(result.get("status") == "needs_review" for result in results):
        return "needs_review"
    return "passed"


def _write_aggregate_report(run_dir: Path, results: list[dict[str, object]], *, mode: str) -> None:
    lines = [
        f"# Source Normalization V1.1 Multibook Validation",
        "",
        f"- Mode: `{mode}`",
        f"- Run dir: `{run_dir}`",
        f"- Source Normalization: `{SOURCE_NORMALIZATION_VERSION}`",
        f"- Suite outcome: `{_suite_outcome(results)}`",
        f"- Generated at: `{_timestamp()}`",
        "",
        "## Book Outcomes",
        "",
        "| Source | Status | Paragraphs | Text roles | Normalized roles | Risk counts | Review |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for result in results:
        review = Path(_text(result.get("output_dir"))) / "source_normalization_v1_1_review.md"
        review_ref = review.relative_to(run_dir) if review.exists() else ""
        lines.append(
            "| "
            f"`{result.get('source_ref')}` | "
            f"`{result.get('status')}` | "
            f"{result.get('paragraph_count', '')} | "
            f"`{result.get('text_role_counts', {})}` | "
            f"`{result.get('normalized_role_counts', {})}` | "
            f"`{result.get('risk_counts', {})}` | "
            f"`{review_ref}` |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Grouping",
            "",
            "- Chinese fiction / poetry: `zh/xidaduo.epub`, `zh/jinghua_yuan_25377.epub`, `zh/rulin_waishi_24032.epub`.",
            "- Chinese nonfiction / numbered-short-form: `zh/nawaer_baodian.epub`, `zh/mangge_zhi_dao.epub`, `zh/huochu_shengming_de_yiyi.epub`.",
            "- English fiction / nonfiction: `en/pride_and_prejudice_1342.epub`, `en/moby_dick_2701.epub`, `en/the_varieties_of_religious_experience_public_v2.epub`, `en/private/the_almanack_of_naval_ravikant.epub`.",
            "",
            "## Aggregate Recommendation",
            "",
        ]
    )
    outcome = _suite_outcome(results)
    if outcome == "passed":
        lines.append("No automatic critical failures were detected. Review sampled `needs_review` surfaces before treating this as broad coverage evidence.")
    elif outcome == "needs_review":
        lines.append("At least one book has high-risk samples. Inspect per-book reports before widening rollout.")
    else:
        lines.append("At least one book failed parse/normalization. Investigate failure artifacts before rollout.")
    (run_dir / "aggregate_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_suite_status(
    run_dir: Path,
    *,
    mode: str,
    status: str,
    results: list[dict[str, object]] | None = None,
    error: str | None = None,
) -> None:
    payload: dict[str, object] = {
        "run_id": RUN_ID,
        "mode": mode,
        "status": status,
        "updated_at": _timestamp(),
        "source_normalization_version": SOURCE_NORMALIZATION_VERSION,
        "results": results or [],
    }
    if results is not None:
        payload["outcome"] = _suite_outcome(results)
    if error:
        payload["error"] = error
    _write_json(run_dir / "status.json", payload)


def run_validation(
    *,
    mode: str,
    run_dir: Path,
    source_refs: list[str],
    workers: int,
    retry: int,
    clean: bool,
) -> int:
    run_dir.mkdir(parents=True, exist_ok=True)
    _update_suite_status(run_dir, mode=mode, status="running", results=[])
    tasks = _book_tasks(source_refs, run_dir)
    results: list[dict[str, object]] = []
    try:
        if workers <= 1 or len(tasks) <= 1:
            for task in tasks:
                result = _run_one_book(task, retry=retry, clean=clean)
                results.append(result)
                _update_suite_status(run_dir, mode=mode, status="running", results=results)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(_run_one_book, task, retry=retry, clean=clean): task
                    for task in tasks
                }
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
                    results.sort(key=lambda item: source_refs.index(_text(item.get("source_ref"))) if _text(item.get("source_ref")) in source_refs else 999)
                    _update_suite_status(run_dir, mode=mode, status="running", results=results)
        _write_json(run_dir / "results.json", {"run_id": RUN_ID, "mode": mode, "results": results})
        _write_aggregate_report(run_dir, results, mode=mode)
        outcome = _suite_outcome(results)
        final_status = "failed" if outcome == "failed" else "completed"
        _update_suite_status(run_dir, mode=mode, status=final_status, results=results)
        return 0 if final_status == "completed" else 1
    except Exception as exc:  # pragma: no cover - live validation failure path
        _update_suite_status(run_dir, mode=mode, status="failed", results=results, error=f"{type(exc).__name__}: {exc}")
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["smoke", "suite"], default="suite")
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--retry", type=int, default=1)
    parser.add_argument("--book", action="append", default=None, help="Source ref under state/library_sources. Repeatable.")
    parser.add_argument("--no-clean", action="store_true", help="Reuse existing per-book output dirs if present.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_dir = Path(args.run_dir).resolve()
    if args.book:
        source_refs = list(args.book)
    elif args.mode == "smoke":
        source_refs = list(DEFAULT_SMOKE_BOOKS)
    else:
        source_refs = list(DEFAULT_SUITE_BOOKS)
    return run_validation(
        mode=args.mode,
        run_dir=run_dir,
        source_refs=source_refs,
        workers=max(1, int(args.workers)),
        retry=max(0, int(args.retry)),
        clean=not bool(args.no_clean),
    )


if __name__ == "__main__":
    raise SystemExit(main())
