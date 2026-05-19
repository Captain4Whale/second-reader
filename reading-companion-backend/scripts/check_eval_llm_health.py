#!/usr/bin/env python3
"""Inspect strict-eval LLM health for one or more run/output directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.attentional_v2.llm_health import summarize_output_llm_health  # noqa: E402


def _has_llm_health_inputs(path: Path) -> bool:
    return (
        (path / "_runtime").exists()
        or any(path.glob("**/llm_standard.jsonl"))
        or any(path.glob("**/standard.jsonl"))
        or any(path.glob("**/activity.jsonl"))
    )


def _candidate_output_dirs(path: Path) -> list[Path]:
    if _has_llm_health_inputs(path):
        return [path]
    outputs_dir = path / "outputs"
    if not outputs_dir.exists():
        return [path]
    candidates = [
        candidate
        for candidate in outputs_dir.glob("*/*")
        if candidate.is_dir() and _has_llm_health_inputs(candidate)
    ]
    return sorted(candidates) or [path]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Run roots or reading output dirs to inspect.")
    parser.add_argument("--max-recent-error-streak", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results = []
    for raw_path in args.paths:
        path = Path(raw_path).expanduser().resolve()
        for output_dir in _candidate_output_dirs(path):
            results.append(
                summarize_output_llm_health(
                    output_dir,
                    max_recent_error_streak=max(1, int(args.max_recent_error_streak)),
                )
            )
    failed = [item for item in results if item.get("status") != "ok"]
    payload = {
        "status": "failed" if failed else "ok",
        "checked_count": len(results),
        "failed_count": len(failed),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
