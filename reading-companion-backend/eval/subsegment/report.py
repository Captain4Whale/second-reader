"""Markdown report generation for subsegment benchmark runs."""

from __future__ import annotations

from collections import Counter
from typing import Any

from eval.common.taxonomy import DIRECT_QUALITY, LOCAL_IMPACT, scope_heading


def _winner_counter(items: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in items:
        winner = str(item.get("winner", "tie")).strip() or "tie"
        counter[winner] += 1
    return counter


def _format_counter(counter: Counter[str]) -> list[str]:
    return [f"- `{label}`: {counter.get(label, 0)}" for label in sorted(counter)]


def _scope_case_results(case_results: list[dict[str, Any]], scope: str) -> list[dict[str, Any]]:
    return [item for item in case_results if scope in item.get("scope_results", {})]


def _scope_winners(case_results: list[dict[str, Any]], scope: str, winner: str) -> list[dict[str, Any]]:
    return [
        item
        for item in _scope_case_results(case_results, scope)
        if item.get("scope_results", {}).get(scope, {}).get("judgment", {}).get("winner") == winner
    ][:3]


def _scope_clarifier(scope: str) -> str:
    if scope == DIRECT_QUALITY:
        return "subsegment slicing"
    if scope == LOCAL_IMPACT:
        return "section-level carry-through"
    return "reader behavior"


def build_markdown_report(
    *,
    dataset_id: str,
    dataset_version: str,
    target: str,
    scopes: list[str],
    methods: list[str],
    comparison_target: str,
    rubric_summary_by_scope: dict[str, list[str]],
    aggregate: dict[str, Any],
    case_results: list[dict[str, Any]],
) -> str:
    """Build a concise checked-in markdown report for one benchmark run."""
    lines = [
        f"# Subsegment Benchmark Report: {dataset_id}",
        "",
        "## Run Metadata",
        "",
        f"- Target: `{target}`",
        f"- Scope: {', '.join(f'`{scope}`' for scope in scopes)}",
        f"- Method: {', '.join(f'`{method}`' for method in methods)}",
        f"- Dataset version: `{dataset_version}`",
        "",
        "## Comparison Target",
        "",
        f"- {comparison_target}",
        "",
        "## Aggregate Findings",
        "",
        f"- Cases evaluated: {aggregate.get('case_count', 0)}",
        f"- Core cases: {aggregate.get('core_case_count', 0)}",
        f"- Audit cases: {aggregate.get('audit_case_count', 0)}",
        "",
    ]

    scope_metrics = aggregate.get("scope_metrics", {})
    for scope in scopes:
        metrics = scope_metrics.get(scope, {})
        heading = scope_heading(scope)
        lines.extend(
            [
                f"### {heading} ({_scope_clarifier(scope)})",
                "",
                f"- Cases in scope: {metrics.get('case_count', 0)}",
                f"- `llm_primary` fallback rate: {metrics.get('llm_fallback_rate', 0.0):.2%}",
                f"- `llm_primary` invalid-plan rate: {metrics.get('llm_invalid_plan_rate', 0.0):.2%}",
                f"- `llm_primary` failure rate: {metrics.get('llm_failure_rate', 0.0):.2%}",
                f"- `heuristic_only` failure rate: {metrics.get('heuristic_failure_rate', 0.0):.2%}",
                f"- Average unit count (`heuristic_only`): {metrics.get('heuristic_avg_unit_count', 0.0):.2f}",
                f"- Average unit count (`llm_primary`): {metrics.get('llm_avg_unit_count', 0.0):.2f}",
                "",
            ]
        )

    for scope in scopes:
        heading = scope_heading(scope)
        scope_cases = _scope_case_results(case_results, scope)
        winner_counter = _winner_counter(
            [
                item.get("scope_results", {}).get(scope, {}).get("judgment", {})
                for item in scope_cases
                if isinstance(item.get("scope_results", {}).get(scope, {}).get("judgment"), dict)
            ]
        )
        lines.extend(
            [
                f"## {heading} ({_scope_clarifier(scope)})",
                "",
                "### Rubric",
                "",
            ]
        )
        lines.extend([f"- {item}" for item in rubric_summary_by_scope.get(scope, [])])
        lines.extend(["", "### Pairwise Winners", ""])
        lines.extend(_format_counter(winner_counter))

        llm_wins = _scope_winners(case_results, scope, "llm_primary")
        heuristic_wins = _scope_winners(case_results, scope, "heuristic_only")

        lines.extend(["", "### Representative LLM Wins", ""])
        if llm_wins:
            for item in llm_wins:
                judgment = item.get("scope_results", {}).get(scope, {}).get("judgment", {})
                lines.append(f"- `{item['case_id']}` {item.get('segment_ref', '')}: {judgment.get('reason', '')}")
        else:
            lines.append("- None in this run.")

        lines.extend(["", "### Representative Heuristic Wins", ""])
        if heuristic_wins:
            for item in heuristic_wins:
                judgment = item.get("scope_results", {}).get(scope, {}).get("judgment", {})
                lines.append(f"- `{item['case_id']}` {item.get('segment_ref', '')}: {judgment.get('reason', '')}")
        else:
            lines.append("- None in this run.")
        lines.append("")

    lines.extend(
        [
            "## Known Caveats",
            "",
            "- This benchmark is intentionally small and curated for attribution, not broad corpus coverage.",
            (
                f"- This run covered {aggregate.get('case_count', 0)} of "
                f"{aggregate.get('dataset_case_count', aggregate.get('case_count', 0))} tracked benchmark cases."
            ),
            "- The v1 dataset is dominated by repo-tracked sections from one book plus one fixture sanity case.",
        ]
    )
    if LOCAL_IMPACT in scopes:
        lines.append(
            "- Search is disabled during local-impact section runs so the comparison stays focused on subsegment slicing rather than curiosity expansion."
        )
    return "\n".join(lines).strip() + "\n"
