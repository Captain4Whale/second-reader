"""Shared helpers for rebuilding normalized bundles from completed reading outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.attentional_v2.evaluation import build_normalized_eval_bundle as build_attentional_v2_normalized_eval_bundle
from src.iterator_reader.storage import load_json as load_iterator_json


def run_state_status(output_dir: Path) -> str:
    run_state_path = output_dir / "_runtime" / "run_state.json"
    if not run_state_path.exists():
        return ""
    payload = load_iterator_json(run_state_path)
    return str(payload.get("status") or payload.get("stage") or "")


def rebuild_normalized_bundle_from_completed_output(
    *,
    mechanism_key: str,
    source_output_dir: Path,
    segment_id: str,
) -> dict[str, Any]:
    """Rebuild one normalized eval bundle from an existing completed reading output."""

    if mechanism_key in {"iterator_v1", "both"}:
        raise ValueError(f"{mechanism_key} 已退役；历史实现请查看 tag pre-cleanup-2026-11")
    if not source_output_dir.exists():
        raise FileNotFoundError(f"reuse output dir does not exist: {source_output_dir}")
    status = run_state_status(source_output_dir)
    if status != "completed":
        raise RuntimeError(f"reuse output dir is not completed: {source_output_dir} status={status or 'missing'}")

    if mechanism_key == "attentional_v2":
        bundle = build_attentional_v2_normalized_eval_bundle(source_output_dir)
        mechanism_label = "Attentional V2 Ingest/Digest"
    else:
        raise ValueError(f"unsupported mechanism for reuse output: {mechanism_key}")

    return {
        "mechanism_label": mechanism_label,
        "normalized_eval_bundle": bundle,
    }
