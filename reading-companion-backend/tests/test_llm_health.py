"""Tests for strict eval LLM-health checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval.attentional_v2.llm_health import (
    assert_eval_output_llm_health,
    summarize_output_llm_health,
)


def _append_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_strict_eval_health_passes_for_successful_trace(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    _append_jsonl(
        output_dir / "_runtime" / "llm_standard.jsonl",
        [
            {
                "status": "ok",
                "completed_at": "2026-05-19T00:00:01+00:00",
                "problem_code": "",
            }
        ],
    )

    summary = assert_eval_output_llm_health(output_dir)

    assert summary["status"] == "ok"
    assert summary["success_count"] == 1
    assert summary["fallback_count"] == 0


def test_strict_eval_health_fails_on_product_fallback_activity(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    _append_jsonl(
        output_dir / "_runtime" / "llm_standard.jsonl",
        [
            {
                "status": "ok",
                "completed_at": "2026-05-19T00:00:01+00:00",
                "problem_code": "",
            }
        ],
    )
    _append_jsonl(
        output_dir / "activity.jsonl",
        [{"type": "llm_fallback", "problem_code": "network_blocked"}],
    )

    summary = summarize_output_llm_health(output_dir)

    assert summary["status"] == "failed"
    assert "llm_fallback_events_present" in summary["errors"]
    with pytest.raises(RuntimeError, match="llm_fallback_events_present"):
        assert_eval_output_llm_health(output_dir)


def test_strict_eval_health_fails_on_recent_retryable_error_streak(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    _append_jsonl(
        output_dir / "_runtime" / "llm_standard.jsonl",
        [
            {
                "status": "ok",
                "completed_at": "2026-05-19T00:00:01+00:00",
                "problem_code": "",
            },
            {
                "status": "error",
                "completed_at": "2026-05-19T00:00:02+00:00",
                "problem_code": "network_blocked",
            },
            {
                "status": "error",
                "completed_at": "2026-05-19T00:00:03+00:00",
                "problem_code": "llm_timeout",
            },
            {
                "status": "error",
                "completed_at": "2026-05-19T00:00:04+00:00",
                "problem_code": "llm_timeout",
            },
        ],
    )

    summary = summarize_output_llm_health(output_dir)

    assert summary["status"] == "failed"
    assert summary["recent_retryable_error_streak"] == 3
    assert "recent_retryable_error_streak" in summary["errors"]
