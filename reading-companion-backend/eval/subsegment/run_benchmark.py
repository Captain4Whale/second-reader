"""Run the curated offline benchmark for subsegment planning."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from eval.subsegment.dataset import BenchmarkCase, BenchmarkDataset, load_benchmark_dataset
from eval.subsegment.judge import judge_downstream_pairwise, judge_plan_pairwise
from eval.subsegment.report import build_markdown_report
from src.iterator_reader.policy import chapter_budget, default_budget_policy, resolve_skill_policy, segment_budget
from src.iterator_reader.reader import _estimate_tokens, create_reader_state, run_reader_segment


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = ROOT / "eval" / "datasets" / "subsegment_benchmark_v1"
DEFAULT_RUNS_ROOT = ROOT / "eval" / "runs" / "subsegment"
DEFAULT_REPORTS_ROOT = ROOT / "docs" / "evaluation" / "subsegment"
DEFAULT_USER_INTENT = (
    "Read as a thoughtful co-reader and notice meaningful definitions, turns, causal links, and callbacks."
)
STRATEGIES = ("heuristic_only", "llm_primary")
RUBRIC_SUMMARY = [
    "Plan-level: self-containedness, minimal sufficiency, one primary reading move.",
    "Downstream: reaction focus, source-anchor quality, coverage of meaningful turns/definitions/callbacks, coherence after merge.",
]

JudgeFn = Callable[..., dict[str, Any]]


def _json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _case_to_dict(case: BenchmarkCase) -> dict[str, Any]:
    return asdict(case)


def _build_eval_budget() -> dict[str, Any]:
    policy = default_budget_policy()
    policy["max_search_queries_per_segment"] = 0
    policy["max_search_queries_per_chapter"] = 0
    policy["segment_timeout_seconds"] = 45
    chapter_state = chapter_budget(policy)
    return segment_budget(chapter_state, policy)


def _build_reader_state(case: BenchmarkCase, dataset: BenchmarkDataset, strategy: str) -> dict[str, Any]:
    return create_reader_state(
        chapter_title=case.chapter_title,
        segment_id=case.segment_id,
        segment_summary=case.segment_summary,
        segment_text=case.segment_text,
        memory={},
        output_language=case.output_language,
        user_intent=dataset.default_user_intent or DEFAULT_USER_INTENT,
        skill_policy=resolve_skill_policy("balanced"),
        budget=_build_eval_budget(),
        max_revisions=0,
        segment_ref=case.segment_ref,
        book_title=case.book_title,
        author=case.author,
        chapter_ref=case.chapter_ref,
        chapter_index=case.chapter_index,
        total_chapters=case.total_chapters,
        primary_role=case.primary_role,
        role_tags=case.role_tags,
        role_confidence=case.role_confidence,
        section_heading=case.section_heading,
        nearby_outline=case.nearby_outline,
        subsegment_strategy_override=strategy,  # type: ignore[arg-type]
    )


def _planner_invalid(diagnostics: dict[str, Any]) -> bool:
    failure = str(diagnostics.get("planner_failure_reason", "")).strip()
    return failure in {
        "non_dict_payload",
        "payload_not_dict",
        "missing_units",
        "too_many_units",
        "unit_not_dict",
        "invalid_sentence_bounds",
        "non_contiguous_sentence_coverage",
        "invalid_reading_move",
        "oversized_or_empty_unit",
        "incomplete_sentence_coverage",
    }


def _strategy_result(case: BenchmarkCase, dataset: BenchmarkDataset, strategy: str) -> dict[str, Any]:
    state = _build_reader_state(case, dataset, strategy)
    result: dict[str, Any] = {
        "case_id": case.case_id,
        "strategy": strategy,
        "failed": False,
        "error": "",
        "planner_source": "",
        "subsegments": [],
        "diagnostics": {},
        "rendered": {},
        "metrics": {},
    }
    try:
        rendered, final_state = run_reader_segment(state)
    except Exception as exc:
        result["failed"] = True
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    plan = list(final_state.get("subsegment_plan", []))
    diagnostics = dict(final_state.get("subsegment_plan_diagnostics", {}))
    budget = dict(final_state.get("budget", {}))
    unit_tokens = [_estimate_tokens(str(item.get("text", ""))) for item in plan if str(item.get("text", "")).strip()]
    result["planner_source"] = final_state.get("subsegment_planner_source", "")
    result["subsegments"] = plan
    result["diagnostics"] = diagnostics
    result["rendered"] = rendered
    result["metrics"] = {
        "unit_count": len(plan),
        "avg_unit_tokens": (sum(unit_tokens) / len(unit_tokens)) if unit_tokens else 0.0,
        "fallback_used": final_state.get("subsegment_planner_source") == "fallback",
        "invalid_plan": _planner_invalid(diagnostics),
        "timed_out": bool(budget.get("segment_timed_out", False)),
    }
    return result


def _select_cases(dataset: BenchmarkDataset, *, core_only: bool, limit: int | None) -> list[BenchmarkCase]:
    case_ids = dataset.core_case_ids if core_only else dataset.core_case_ids + dataset.audit_case_ids
    cases = [case for case in dataset.cases if case.case_id in case_ids]
    cases.sort(key=lambda item: case_ids.index(item.case_id))
    if limit is not None:
        return cases[: max(0, int(limit))]
    return cases


def _aggregate(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    def _strategy_cases(name: str) -> list[dict[str, Any]]:
        return [item["strategies"][name] for item in case_results if name in item.get("strategies", {})]

    llm_results = _strategy_cases("llm_primary")
    heuristic_results = _strategy_cases("heuristic_only")
    llm_total = max(1, len(llm_results))
    heuristic_total = max(1, len(heuristic_results))

    return {
        "case_count": len(case_results),
        "core_case_count": sum(1 for item in case_results if item.get("split") == "core"),
        "audit_case_count": sum(1 for item in case_results if item.get("split") == "audit"),
        "llm_fallback_rate": sum(1 for item in llm_results if item.get("metrics", {}).get("fallback_used")) / llm_total,
        "llm_invalid_plan_rate": sum(1 for item in llm_results if item.get("metrics", {}).get("invalid_plan")) / llm_total,
        "llm_failure_rate": sum(
            1 for item in llm_results if item.get("failed") or item.get("metrics", {}).get("timed_out")
        )
        / llm_total,
        "heuristic_failure_rate": sum(
            1 for item in heuristic_results if item.get("failed") or item.get("metrics", {}).get("timed_out")
        )
        / heuristic_total,
        "llm_avg_unit_count": sum(item.get("metrics", {}).get("unit_count", 0) for item in llm_results) / llm_total,
        "heuristic_avg_unit_count": sum(item.get("metrics", {}).get("unit_count", 0) for item in heuristic_results)
        / heuristic_total,
    }


def run_benchmark(
    *,
    dataset_dir: str | Path = DEFAULT_DATASET_DIR,
    runs_root: str | Path = DEFAULT_RUNS_ROOT,
    report_path: str | Path | None = None,
    run_id: str | None = None,
    core_only: bool = False,
    limit: int | None = None,
    judge_mode: str = "llm",
    plan_judge: JudgeFn | None = None,
    downstream_judge: JudgeFn | None = None,
) -> dict[str, Any]:
    """Execute the offline benchmark and return the aggregate summary."""
    dataset = load_benchmark_dataset(dataset_dir)
    cases = _select_cases(dataset, core_only=core_only, limit=limit)
    if not cases:
        raise ValueError("no benchmark cases selected")

    run_name = run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_root = Path(runs_root) / run_name
    runtime_root = run_root / "runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    _json_dump(run_root / "dataset_manifest.json", {
        "dataset_id": dataset.dataset_id,
        "version": dataset.version,
        "selected_case_ids": [case.case_id for case in cases],
        "core_only": core_only,
        "limit": limit,
        "judge_mode": judge_mode,
    })

    effective_plan_judge = plan_judge if plan_judge is not None else judge_plan_pairwise
    effective_downstream_judge = downstream_judge if downstream_judge is not None else judge_downstream_pairwise

    case_results: list[dict[str, Any]] = []
    for case in cases:
        _json_dump(run_root / "inputs" / f"{case.case_id}.json", _case_to_dict(case))
        strategies = {strategy: _strategy_result(case, dataset, strategy) for strategy in STRATEGIES}
        for strategy, payload in strategies.items():
            _json_dump(run_root / "plans" / f"{case.case_id}.{strategy}.json", {
                "case_id": case.case_id,
                "strategy": strategy,
                "planner_source": payload.get("planner_source", ""),
                "diagnostics": payload.get("diagnostics", {}),
                "subsegments": payload.get("subsegments", []),
                "metrics": payload.get("metrics", {}),
                "runtime_root": str(runtime_root),
            })
            _json_dump(run_root / "sections" / f"{case.case_id}.{strategy}.json", payload.get("rendered", {}))

        if judge_mode == "none":
            plan_judgment = {"winner": "tie", "reason": "judge_disabled"}
            downstream_judgment = {"winner": "tie", "reason": "judge_disabled"}
        else:
            plan_judgment = effective_plan_judge(
                segment_text=case.segment_text,
                segment_summary=case.segment_summary,
                left_label="heuristic_only",
                left_units=strategies["heuristic_only"].get("subsegments", []),
                right_label="llm_primary",
                right_units=strategies["llm_primary"].get("subsegments", []),
            )
            downstream_judgment = effective_downstream_judge(
                segment_text=case.segment_text,
                segment_summary=case.segment_summary,
                left_label="heuristic_only",
                left_rendered=strategies["heuristic_only"].get("rendered", {}),
                right_label="llm_primary",
                right_rendered=strategies["llm_primary"].get("rendered", {}),
            )

        _json_dump(run_root / "judge" / f"{case.case_id}.plan.json", plan_judgment)
        _json_dump(run_root / "judge" / f"{case.case_id}.downstream.json", downstream_judgment)

        case_results.append(
            {
                "case_id": case.case_id,
                "split": case.split,
                "segment_ref": case.segment_ref,
                "tags": list(case.tags),
                "strategies": strategies,
                "plan_judgment": plan_judgment,
                "downstream_judgment": downstream_judgment,
            }
        )

    aggregate = _aggregate(case_results)
    aggregate["dataset_case_count"] = len(dataset.cases)
    aggregate["selected_case_ids"] = [case.case_id for case in cases]
    _json_dump(run_root / "summary" / "case_results.json", case_results)
    _json_dump(run_root / "summary" / "aggregate.json", aggregate)

    markdown = build_markdown_report(
        dataset_id=dataset.dataset_id,
        comparison_target="`heuristic_only` vs `llm_primary` on curated subsegment benchmark cases",
        rubric_summary=RUBRIC_SUMMARY,
        aggregate=aggregate,
        case_results=case_results,
    )
    final_report_path = Path(report_path) if report_path is not None else DEFAULT_REPORTS_ROOT / f"{run_name}.md"
    final_report_path.parent.mkdir(parents=True, exist_ok=True)
    final_report_path.write_text(markdown, encoding="utf-8")

    return {
        "run_id": run_name,
        "run_root": str(run_root),
        "report_path": str(final_report_path),
        "aggregate": aggregate,
        "case_results": case_results,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the curated offline benchmark for subsegment planning.")
    parser.add_argument("--dataset-dir", default=str(DEFAULT_DATASET_DIR))
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--report-path", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--judge-mode", choices=["llm", "none"], default="llm")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--core-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    summary = run_benchmark(
        dataset_dir=args.dataset_dir,
        runs_root=args.runs_root,
        report_path=args.report_path or None,
        run_id=args.run_id or None,
        core_only=bool(args.core_only),
        limit=args.limit or None,
        judge_mode=args.judge_mode,
    )
    print(json.dumps(summary["aggregate"], ensure_ascii=False, indent=2))
    print(f"run_root={summary['run_root']}")
    print(f"report_path={summary['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
