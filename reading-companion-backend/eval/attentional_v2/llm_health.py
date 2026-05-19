"""LLM-health checks for active eval reading outputs.

These helpers are intentionally stricter than product runtime behavior. Product
runs may degrade through recorded fallbacks, but eval runs must not treat those
fallback-backed outputs as valid evidence.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


RETRYABLE_LLM_ERROR_CODES = frozenset({"network_blocked", "llm_timeout"})


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _parse_timestamp(value: object) -> float:
    text = _clean_text(value)
    if not text:
        return 0.0
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return 0.0


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _trace_paths(output_dir: Path) -> list[Path]:
    seen: set[Path] = set()
    paths: list[Path] = []
    for pattern in ("**/llm_standard.jsonl", "**/standard.jsonl"):
        for path in output_dir.glob(pattern):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            paths.append(path)
    return sorted(paths)


def _activity_paths(output_dir: Path) -> list[Path]:
    return sorted(path for path in output_dir.glob("**/activity.jsonl") if path.is_file())


def summarize_output_llm_health(
    output_dir: Path,
    *,
    max_recent_error_streak: int = 3,
) -> dict[str, Any]:
    """Return a compact strict-eval LLM-health summary for one reading output."""

    trace_rows: list[dict[str, Any]] = []
    for path in _trace_paths(output_dir):
        trace_rows.extend(_iter_jsonl(path))

    activity_rows: list[dict[str, Any]] = []
    for path in _activity_paths(output_dir):
        activity_rows.extend(_iter_jsonl(path))

    success_rows = [row for row in trace_rows if _clean_text(row.get("status")).lower() == "ok"]
    error_rows = [row for row in trace_rows if _clean_text(row.get("status")).lower() != "ok"]
    problem_counts = Counter(_clean_text(row.get("problem_code")) for row in error_rows)
    problem_counts.pop("", None)
    fallback_rows = [row for row in activity_rows if _clean_text(row.get("type")) == "llm_fallback"]
    fallback_problem_counts = Counter(_clean_text(row.get("problem_code")) for row in fallback_rows)
    fallback_problem_counts.pop("", None)

    sorted_rows = sorted(
        trace_rows,
        key=lambda row: _parse_timestamp(row.get("completed_at")) or _parse_timestamp(row.get("started_at")),
    )
    recent_error_streak = 0
    for row in reversed(sorted_rows):
        status = _clean_text(row.get("status")).lower()
        problem_code = _clean_text(row.get("problem_code"))
        if status != "ok" and problem_code in RETRYABLE_LLM_ERROR_CODES:
            recent_error_streak += 1
            continue
        break

    errors: list[str] = []
    if fallback_rows:
        errors.append("llm_fallback_events_present")
    if trace_rows and not success_rows:
        errors.append("no_successful_llm_calls")
    if recent_error_streak >= max(1, int(max_recent_error_streak)):
        errors.append("recent_retryable_error_streak")

    return {
        "status": "failed" if errors else "ok",
        "output_dir": str(output_dir),
        "trace_file_count": len(_trace_paths(output_dir)),
        "activity_file_count": len(_activity_paths(output_dir)),
        "trace_count": len(trace_rows),
        "success_count": len(success_rows),
        "error_count": len(error_rows),
        "problem_code_counts": dict(problem_counts),
        "fallback_count": len(fallback_rows),
        "fallback_problem_code_counts": dict(fallback_problem_counts),
        "recent_retryable_error_streak": recent_error_streak,
        "last_success_completed_at": max(
            (_clean_text(row.get("completed_at")) for row in success_rows),
            default="",
        ),
        "last_trace_completed_at": max(
            (_clean_text(row.get("completed_at")) for row in trace_rows),
            default="",
        ),
        "errors": errors,
    }


def assert_eval_output_llm_health(
    output_dir: Path,
    *,
    label: str = "",
    max_recent_error_streak: int = 3,
) -> dict[str, Any]:
    """Raise when one eval reading output is backed by unhealthy LLM traces."""

    summary = summarize_output_llm_health(
        output_dir,
        max_recent_error_streak=max_recent_error_streak,
    )
    if summary["status"] != "ok":
        display_label = label or str(output_dir)
        raise RuntimeError(
            "LLM health check failed for "
            f"{display_label}: {', '.join(summary['errors'])}; "
            f"fallback_count={summary['fallback_count']}; "
            f"success_count={summary['success_count']}; "
            f"error_count={summary['error_count']}; "
            f"recent_retryable_error_streak={summary['recent_retryable_error_streak']}"
        )
    return summary


__all__ = [
    "RETRYABLE_LLM_ERROR_CODES",
    "assert_eval_output_llm_health",
    "summarize_output_llm_health",
]
