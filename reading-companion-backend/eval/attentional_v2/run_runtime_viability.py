"""Run deterministic runtime-viability checks for attentional_v2 vs iterator_v1."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from eval.common.taxonomy import DETERMINISTIC_METRICS, normalize_methods, validate_target_slug
from src.reading_core.runtime_contracts import ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_mechanisms.iterator_v1 import IteratorV1Mechanism
from src.reading_runtime.job_concurrency import resolve_worker_policy, submit_inherited_context
from src.reading_runtime.output_dir_overrides import override_output_dir


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIRS = (
    ROOT / "eval" / "datasets" / "chapter_corpora" / "attentional_v2_chapters_en_v2",
    ROOT / "eval" / "datasets" / "chapter_corpora" / "attentional_v2_chapters_zh_v2",
)
DEFAULT_SOURCE_MANIFEST = ROOT / "eval" / "manifests" / "source_books" / "attentional_v2_public_benchmark_pool_v2.json"
DEFAULT_RUNS_ROOT = ROOT / "eval" / "runs" / "attentional_v2"
DEFAULT_TARGET = validate_target_slug("runtime_viability_gate")
DEFAULT_METHODS = normalize_methods([DETERMINISTIC_METRICS])
DEFAULT_COMPARISON_TARGET = "attentional_v2 vs iterator_v1 runtime viability on balanced chapter cases"
DEFAULT_USER_INTENT = (
    "Read as a thoughtful co-reader and notice meaningful turns, tensions, callbacks, definitions, and chapter-level development."
)
SELECTION_ROLES = ("expository", "argumentative", "narrative_reflective", "reference_heavy")
MECHANISM_KEYS = ("attentional_v2", "iterator_v1")


@dataclass(frozen=True)
class ChapterCase:
    chapter_case_id: str
    source_id: str
    book_title: str
    author: str
    language_track: str
    type_tags: list[str]
    role_tags: list[str]
    output_dir: str
    chapter_id: int
    chapter_title: str
    sentence_count: int
    paragraph_count: int
    candidate_position_bucket: str
    candidate_score: float
    selection_status: str
    selection_priority: int
    selection_role: str
    dataset_id: str
    dataset_version: str


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _jsonl_dump(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_json_payload(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _load_cases(dataset_dir: Path) -> tuple[dict[str, Any], list[ChapterCase]]:
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    rows: list[ChapterCase] = []
    with (dataset_dir / str(manifest["primary_file"])).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            raw = json.loads(line)
            rows.append(
                ChapterCase(
                    chapter_case_id=str(raw["chapter_case_id"]),
                    source_id=str(raw["source_id"]),
                    book_title=str(raw["book_title"]),
                    author=str(raw["author"]),
                    language_track=str(raw["language_track"]),
                    type_tags=[str(item) for item in raw.get("type_tags", [])],
                    role_tags=[str(item) for item in raw.get("role_tags", [])],
                    output_dir=str(raw.get("output_dir", "")),
                    chapter_id=int(raw["chapter_id"]),
                    chapter_title=str(raw.get("chapter_title", "")),
                    sentence_count=int(raw.get("sentence_count", 0) or 0),
                    paragraph_count=int(raw.get("paragraph_count", 0) or 0),
                    candidate_position_bucket=str(raw.get("candidate_position_bucket", "")),
                    candidate_score=float(raw.get("candidate_score", 0.0) or 0.0),
                    selection_status=str(raw.get("selection_status", "")),
                    selection_priority=int(raw.get("selection_priority", 999) or 999),
                    selection_role=str(raw.get("selection_role", "")),
                    dataset_id=str(manifest["dataset_id"]),
                    dataset_version=str(manifest["version"]),
                )
            )
    return manifest, rows


def _load_source_index(manifest_path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        str(item["source_id"]): dict(item)
        for item in payload.get("books", [])
        if isinstance(item, dict) and item.get("source_id")
    }


def _core_case_sort_key(case: ChapterCase) -> tuple[int, int, float, str]:
    return (case.sentence_count, case.selection_priority, -case.candidate_score, case.chapter_case_id)


def _select_core_cases(cases: list[ChapterCase]) -> list[ChapterCase]:
    selected: list[ChapterCase] = []
    by_language_role: dict[tuple[str, str], list[ChapterCase]] = defaultdict(list)
    for case in cases:
        if case.selection_role in SELECTION_ROLES:
            by_language_role[(case.language_track, case.selection_role)].append(case)
    for language in ("en", "zh"):
        for role in SELECTION_ROLES:
            options = sorted(by_language_role.get((language, role), []), key=_core_case_sort_key)
            if not options:
                raise ValueError(f"missing core runtime-viability case for {language}/{role}")
            selected.append(options[0])
    return selected


def _summarize_integrity(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {}
    return {
        "passed": bool(report.get("passed", False)),
        "check_count": int(report.get("check_count", 0) or 0),
        "failure_count": int(report.get("failure_count", 0) or 0),
        "warning_count": int(report.get("warning_count", 0) or 0),
    }


def _run_snapshot_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(bundle.get("run_snapshot") or {})
    return {
        "status": _clean_text(snapshot.get("status")),
        "resume_available": bool(snapshot.get("resume_available")) if snapshot.get("resume_available") is not None else None,
        "last_checkpoint_at": snapshot.get("last_checkpoint_at"),
        "completed_chapters": int(snapshot.get("completed_chapters", 0) or 0),
        "total_chapters": int(snapshot.get("total_chapters", 0) or 0),
    }


def _log_case_progress(case: ChapterCase, message: str) -> None:
    print(f"[runtime case {case.chapter_case_id}] {message}", flush=True)


def _run_mechanism_for_case(
    case: ChapterCase,
    source: dict[str, Any],
    *,
    mechanism_key: str,
    run_root: Path,
) -> dict[str, Any]:
    if mechanism_key == "attentional_v2":
        mechanism = AttentionalV2Mechanism()
    elif mechanism_key == "iterator_v1":
        mechanism = IteratorV1Mechanism()
    else:
        raise ValueError(f"unsupported mechanism: {mechanism_key}")

    book_path = ROOT / str(source["relative_local_path"])
    isolated_output_dir = run_root / "outputs" / case.chapter_case_id / mechanism_key
    _log_case_progress(case, f"[mechanism-start] {mechanism_key}")
    shutil.rmtree(isolated_output_dir, ignore_errors=True)
    isolated_output_dir.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    bundle: dict[str, Any] = {}
    error = ""
    integrity_summary: dict[str, Any] = {}
    mechanism_label = mechanism.label
    output_dir = isolated_output_dir
    success = False
    try:
        with override_output_dir(isolated_output_dir):
            result = mechanism.read_book(
                ReadRequest(
                    book_path=book_path,
                    chapter_number=int(case.chapter_id),
                    continue_mode=False,
                    user_intent=DEFAULT_USER_INTENT,
                    language_mode=case.language_track,
                    task_mode="sequential",
                    mechanism_key=mechanism_key,
                    mechanism_config={"persist_normalized_eval_bundle": True},
                )
            )
        mechanism_label = result.mechanism.label
        output_dir = result.output_dir
        bundle = dict(result.normalized_eval_bundle or {})
        if mechanism_key == "attentional_v2":
            integrity_summary = _summarize_integrity(dict(mechanism.run_mechanism_integrity_checks(output_dir)))
        success = True
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    duration_seconds = round(time.perf_counter() - started, 3)
    snapshot_summary = _run_snapshot_summary(bundle)
    reaction_count = len(bundle.get("reactions") or [])
    attention_event_count = len(bundle.get("attention_events") or [])
    _json_dump(run_root / "bundles" / mechanism_key / f"{case.chapter_case_id}.json", bundle)
    _log_case_progress(case, f"[mechanism-completed] {mechanism_key} success={success}")
    return {
        "mechanism_key": mechanism_key,
        "mechanism_label": mechanism_label,
        "output_dir": str(output_dir),
        "success": success,
        "error": error,
        "duration_seconds": duration_seconds,
        "reaction_count": reaction_count,
        "attention_event_count": attention_event_count,
        "run_snapshot": snapshot_summary,
        "integrity_summary": integrity_summary,
        "latency_metadata": dict(bundle.get("latency_metadata") or {}),
        "cost_metadata": dict(bundle.get("cost_metadata") or {}),
    }


def _evaluate_case(case: ChapterCase, *, source: dict[str, Any], run_root: Path) -> dict[str, Any]:
    _log_case_progress(case, "[case-start]")
    mechanisms = {
        mechanism_key: _run_mechanism_for_case(case, source, mechanism_key=mechanism_key, run_root=run_root)
        for mechanism_key in MECHANISM_KEYS
    }
    _log_case_progress(case, "[case-completed]")
    return {
        "chapter_case_id": case.chapter_case_id,
        "language_track": case.language_track,
        "selection_role": case.selection_role,
        "book_title": case.book_title,
        "author": case.author,
        "source_id": case.source_id,
        "chapter_id": case.chapter_id,
        "chapter_title": case.chapter_title,
        "mechanisms": mechanisms,
    }


def _run_case_worker(payload_path: Path, result_path: Path) -> int:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    case = ChapterCase(**dict(payload["case"]))
    result = _evaluate_case(
        case,
        source=dict(payload["source"]),
        run_root=Path(str(payload["run_root"])),
    )
    _write_json_payload(result_path, result)
    return 0


def _run_case_subprocess(case: ChapterCase, *, source: dict[str, Any], run_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="runtime-viability-case-worker-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        payload_path = temp_dir / "payload.json"
        result_path = temp_dir / "result.json"
        _write_json_payload(
            payload_path,
            {
                "case": asdict(case),
                "source": source,
                "run_root": str(run_root),
            },
        )
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker-payload",
            str(payload_path),
            "--worker-result",
            str(result_path),
        ]
        subprocess.run(command, cwd=str(ROOT), check=True)
        return json.loads(result_path.read_text(encoding="utf-8"))


def _aggregate(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {
        "case_count": len(case_results),
        "mechanism_summaries": {},
    }
    for mechanism_key in MECHANISM_KEYS:
        mechanism_rows = [item["mechanisms"][mechanism_key] for item in case_results]
        success_rows = [item for item in mechanism_rows if bool(item.get("success"))]
        by_language: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for case_result in case_results:
            by_language[str(case_result["language_track"])].append(case_result["mechanisms"][mechanism_key])
        aggregate["mechanism_summaries"][mechanism_key] = {
            "success_count": len(success_rows),
            "failure_count": len(mechanism_rows) - len(success_rows),
            "success_rate": round(len(success_rows) / max(1, len(mechanism_rows)), 3),
            "average_duration_seconds": round(mean(item["duration_seconds"] for item in mechanism_rows), 3) if mechanism_rows else 0.0,
            "average_reaction_count": round(mean(item["reaction_count"] for item in success_rows), 3) if success_rows else 0.0,
            "average_attention_event_count": round(mean(item["attention_event_count"] for item in success_rows), 3) if success_rows else 0.0,
            "average_completed_chapters": round(
                mean(int(item["run_snapshot"].get("completed_chapters", 0) or 0) for item in success_rows),
                3,
            )
            if success_rows
            else 0.0,
            "integrity_failures": sum(
                1
                for item in mechanism_rows
                if int(dict(item.get("integrity_summary") or {}).get("failure_count", 0) or 0) > 0
            ),
            "integrity_warning_cases": sum(
                1
                for item in mechanism_rows
                if int(dict(item.get("integrity_summary") or {}).get("warning_count", 0) or 0) > 0
            ),
            "language_summaries": {
                language: {
                    "success_count": sum(1 for item in items if bool(item.get("success"))),
                    "failure_count": sum(1 for item in items if not bool(item.get("success"))),
                    "average_duration_seconds": round(mean(item["duration_seconds"] for item in items), 3) if items else 0.0,
                }
                for language, items in sorted(by_language.items())
            },
        }
    return aggregate


def _build_markdown_report(*, run_id: str, selected_cases: list[ChapterCase], aggregate: dict[str, Any], case_results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Runtime Viability")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("This report records deterministic runtime-viability evidence for attentional_v2 and iterator_v1 on balanced chapter cases.")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Target: `{DEFAULT_TARGET}`")
    lines.append(f"- Methods: `{', '.join(DEFAULT_METHODS)}`")
    lines.append(f"- Comparison target: {DEFAULT_COMPARISON_TARGET}")
    lines.append("")
    lines.append("## Selected Cases")
    lines.append("")
    for case in selected_cases:
        lines.append(f"- `{case.chapter_case_id}` (`{case.language_track}`, `{case.selection_role}`, `{case.book_title}`)")
    lines.append("")
    lines.append("## Aggregate Findings")
    lines.append("")
    for mechanism_key, summary in aggregate["mechanism_summaries"].items():
        lines.append(f"### `{mechanism_key}`")
        lines.append(f"- Success count: `{summary['success_count']}`")
        lines.append(f"- Failure count: `{summary['failure_count']}`")
        lines.append(f"- Success rate: `{summary['success_rate']}`")
        lines.append(f"- Average duration seconds: `{summary['average_duration_seconds']}`")
        lines.append(f"- Average reaction count: `{summary['average_reaction_count']}`")
        lines.append(f"- Average attention event count: `{summary['average_attention_event_count']}`")
        lines.append(f"- Integrity failures: `{summary['integrity_failures']}`")
        lines.append("")
    lines.append("## Case Highlights")
    lines.append("")
    for case_result in case_results:
        lines.append(f"- `{case_result['chapter_case_id']}`")
        for mechanism_key in MECHANISM_KEYS:
            mechanism = case_result["mechanisms"][mechanism_key]
            lines.append(
                f"  - `{mechanism_key}` success=`{mechanism['success']}` duration_seconds=`{mechanism['duration_seconds']}` error=`{mechanism['error']}`"
            )
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def run_benchmark(
    *,
    dataset_dirs: list[Path],
    source_manifest_path: Path,
    runs_root: Path,
    run_id: str | None = None,
    case_ids: list[str] | None = None,
    case_workers: int | None = None,
) -> dict[str, Any]:
    manifests: list[dict[str, Any]] = []
    all_cases: list[ChapterCase] = []
    for dataset_dir in dataset_dirs:
        manifest, cases = _load_cases(dataset_dir)
        manifests.append(manifest)
        all_cases.extend(cases)
    selected_cases = (
        [case for case in all_cases if case.chapter_case_id in set(case_ids or [])]
        if case_ids
        else _select_core_cases(all_cases)
    )
    if not selected_cases:
        raise ValueError("no runtime-viability cases selected")

    run_name = run_id or datetime.now(timezone.utc).strftime("attentional_v2_runtime_viability_%Y%m%d-%H%M%S")
    run_root = runs_root / run_name
    run_root.mkdir(parents=True, exist_ok=True)
    source_index = _load_source_index(source_manifest_path)

    _json_dump(
        run_root / "dataset_manifest.json",
        {
            "target": DEFAULT_TARGET,
            "methods": DEFAULT_METHODS,
            "comparison_target": DEFAULT_COMPARISON_TARGET,
            "dataset_ids": [manifest["dataset_id"] for manifest in manifests],
            "selected_case_ids": [case.chapter_case_id for case in selected_cases],
            "generated_at": _timestamp(),
        },
    )

    worker_policy = resolve_worker_policy(
        job_kind="runtime_viability",
        profile_id="runtime_reader_default",
        task_count=len(selected_cases),
        per_worker_parallelism=2,
        explicit_max_workers=case_workers if case_workers and case_workers > 0 else None,
    )
    case_runner = _run_case_subprocess if worker_policy.worker_count > 1 else _evaluate_case
    results_by_case_id: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, worker_policy.worker_count), thread_name_prefix="runtime-case") as executor:
        future_to_case = {}
        for index, case in enumerate(selected_cases, start=1):
            print(f"[submitted {index}/{len(selected_cases)}] {case.chapter_case_id}", flush=True)
            future_to_case[
                submit_inherited_context(
                    executor,
                    case_runner,
                    case,
                    source=source_index[case.source_id],
                    run_root=run_root,
                )
            ] = case
        for future in as_completed(future_to_case):
            case = future_to_case[future]
            case_payload = future.result()
            results_by_case_id[case.chapter_case_id] = case_payload
            _json_dump(run_root / "cases" / f"{case.chapter_case_id}.json", case_payload)
            print(f"[completed] {case.chapter_case_id}", flush=True)

    case_results = [results_by_case_id[case.chapter_case_id] for case in selected_cases]
    aggregate = _aggregate(case_results)
    _json_dump(run_root / "summary" / "aggregate.json", aggregate)
    _jsonl_dump(run_root / "summary" / "case_results.jsonl", case_results)
    report_path = run_root / "summary" / "report.md"
    report_path.write_text(
        _build_markdown_report(run_id=run_name, selected_cases=selected_cases, aggregate=aggregate, case_results=case_results),
        encoding="utf-8",
    )
    return {
        "run_id": run_name,
        "run_root": str(run_root),
        "report_path": str(report_path),
        "aggregate": aggregate,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", action="append", default=[], help="Chapter corpus dataset directory.")
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST))
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--case-workers", type=int, default=0)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--case-ids", default="")
    parser.add_argument("--worker-payload", default="", help=argparse.SUPPRESS)
    parser.add_argument("--worker-result", default="", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.worker_payload:
        if not args.worker_result:
            raise ValueError("--worker-result is required when --worker-payload is set")
        return _run_case_worker(Path(args.worker_payload).resolve(), Path(args.worker_result).resolve())
    dataset_dirs = [Path(item).resolve() for item in args.dataset_dir] if args.dataset_dir else list(DEFAULT_DATASET_DIRS)
    case_ids = [item.strip() for item in args.case_id if str(item).strip()]
    if args.case_ids:
        case_ids.extend([item.strip() for item in str(args.case_ids).split(",") if item.strip()])
    summary = run_benchmark(
        dataset_dirs=dataset_dirs,
        source_manifest_path=Path(args.source_manifest).resolve(),
        runs_root=Path(args.runs_root).resolve(),
        run_id=args.run_id or None,
        case_ids=case_ids or None,
        case_workers=args.case_workers or None,
    )
    print(json.dumps(summary["aggregate"], ensure_ascii=False, indent=2))
    print(f"run_root={summary['run_root']}")
    print(f"report_path={summary['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
