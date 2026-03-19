"""Markdown report generation for subsegment benchmark runs."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _winner_counter(items: list[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in items:
        winner = str(item.get(key, "tie")).strip() or "tie"
        counter[winner] += 1
    return counter


def _format_counter(counter: Counter[str]) -> list[str]:
    return [f"- `{label}`: {counter.get(label, 0)}" for label in sorted(counter)]


def build_markdown_report(
    *,
    dataset_id: str,
    comparison_target: str,
    rubric_summary: list[str],
    aggregate: dict[str, Any],
    case_results: list[dict[str, Any]],
) -> str:
    """Build a concise checked-in markdown report for one benchmark run."""
    plan_counter = _winner_counter(
        [item.get("plan_judgment", {}) for item in case_results if isinstance(item.get("plan_judgment"), dict)],
        "winner",
    )
    downstream_counter = _winner_counter(
        [item.get("downstream_judgment", {}) for item in case_results if isinstance(item.get("downstream_judgment"), dict)],
        "winner",
    )

    llm_wins = [
        item for item in case_results if item.get("downstream_judgment", {}).get("winner") == "llm_primary"
    ][:3]
    heuristic_wins = [
        item for item in case_results if item.get("downstream_judgment", {}).get("winner") == "heuristic_only"
    ][:3]

    lines = [
        f"# Subsegment Benchmark Report: {dataset_id}",
        "",
        "## Comparison Target",
        "",
        f"- {comparison_target}",
        "",
        "## Rubric",
        "",
    ]
    lines.extend([f"- {item}" for item in rubric_summary])
    lines.extend(
        [
            "",
            "## Aggregate Findings",
            "",
            f"- Cases evaluated: {aggregate.get('case_count', 0)}",
            f"- Core cases: {aggregate.get('core_case_count', 0)}",
            f"- Audit cases: {aggregate.get('audit_case_count', 0)}",
            f"- `llm_primary` fallback rate: {aggregate.get('llm_fallback_rate', 0.0):.2%}",
            f"- `llm_primary` invalid-plan rate: {aggregate.get('llm_invalid_plan_rate', 0.0):.2%}",
            f"- `llm_primary` timeout/failure rate: {aggregate.get('llm_failure_rate', 0.0):.2%}",
            f"- `heuristic_only` timeout/failure rate: {aggregate.get('heuristic_failure_rate', 0.0):.2%}",
            f"- Average unit count (`heuristic_only`): {aggregate.get('heuristic_avg_unit_count', 0.0):.2f}",
            f"- Average unit count (`llm_primary`): {aggregate.get('llm_avg_unit_count', 0.0):.2f}",
            "",
            "### Plan-Level Pairwise Winners",
            "",
        ]
    )
    lines.extend(_format_counter(plan_counter))
    lines.extend(["", "### Downstream Pairwise Winners", ""])
    lines.extend(_format_counter(downstream_counter))

    lines.extend(["", "## Representative LLM Wins", ""])
    if llm_wins:
        for item in llm_wins:
            lines.append(
                f"- `{item['case_id']}` {item.get('segment_ref', '')}: {item.get('downstream_judgment', {}).get('reason', '')}"
            )
    else:
        lines.append("- None in this run.")

    lines.extend(["", "## Representative Heuristic Wins", ""])
    if heuristic_wins:
        for item in heuristic_wins:
            lines.append(
                f"- `{item['case_id']}` {item.get('segment_ref', '')}: {item.get('downstream_judgment', {}).get('reason', '')}"
            )
    else:
        lines.append("- None in this run.")

    lines.extend(
        [
            "",
            "## Known Caveats",
            "",
            "- This benchmark is intentionally small and curated for attribution, not broad corpus coverage.",
            (
                f"- This run covered {aggregate.get('case_count', 0)} of {aggregate.get('dataset_case_count', aggregate.get('case_count', 0))} "
                "tracked benchmark cases."
            ),
            "- The v1 dataset is dominated by repo-tracked sections from one book plus one fixture sanity case.",
            "- Search is disabled during downstream section runs so the comparison stays focused on subsegment slicing rather than curiosity expansion.",
        ]
    )
    return "\n".join(lines).strip() + "\n"
