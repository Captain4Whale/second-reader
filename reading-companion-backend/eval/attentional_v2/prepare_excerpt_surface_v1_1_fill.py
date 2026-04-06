"""Prepare the narrow chapter-22 fill dataset for excerpt surface v1.1.

This script codifies the approved one-case repair path for
`nawaer_baodian_private_zh__22` by taking the earlier `revise` decision on the
anchored-reaction seed, applying the adjudicator's sharpened focus, and writing
one tiny local dataset that can be re-reviewed cleanly.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from .corpus_builder import ROOT, dataset_manifest, write_json, write_jsonl


SOURCE_PACKET_ID = "human_notes_guided_dataset_v1_excerpt_zh_first_review_20260404"
SOURCE_CASE_ID = "nawaer_baodian_private_zh__22__anchored_reaction_selectivity__seed_1"
TARGET_CASE_ID = "nawaer_baodian_private_zh__22__anchored_reaction_selectivity__fill_1"
DEFAULT_RUN_ID = "excerpt_surface_v1_1_fill_chapter22_20260406"
DATASET_ID = "attentional_v2_excerpt_surface_v1_1_fill_zh_chapter22_20260406"
DATASET_DIR = ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / DATASET_ID
SUMMARY_JSON_NAME = "excerpt_surface_v1_1_fill_chapter22_summary.json"
SUMMARY_MD_NAME = "excerpt_surface_v1_1_fill_chapter22_summary.md"
PACKET_DIR = ROOT / "eval" / "review_packets" / "archive" / SOURCE_PACKET_ID
SOURCE_DATASET_DIR = (
    ROOT
    / "state"
    / "eval_local_datasets"
    / "excerpt_cases"
    / "attentional_v2_human_notes_guided_dataset_v1_excerpt_zh__scratch__human_notes_guided_dataset_v1_20260404"
)


def _relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON at {path}")
    return payload


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object row in {path}")
        rows.append(payload)
    return rows


def _source_row() -> dict[str, Any]:
    rows = _load_jsonl(PACKET_DIR / "cases.source.jsonl")
    for row in rows:
        if str(row.get("case_id", "")).strip() == SOURCE_CASE_ID:
            return row
    raise ValueError(f"Source case not found in review packet: {SOURCE_CASE_ID}")


def _review_payload() -> dict[str, Any]:
    case_path = (
        PACKET_DIR
        / "llm_review_runs"
        / "llm_review__20260404-062446__5dbcf06c0498"
        / "cases"
        / f"{SOURCE_CASE_ID}.json"
    )
    return _load_json(case_path)


def _prepared_row() -> dict[str, Any]:
    row = deepcopy(_source_row())
    review_payload = _review_payload()
    normalized_review = dict(review_payload.get("normalized_review") or {})
    revised_selection_reason = str(normalized_review.get("review__revised_selection_reason", "")).strip()
    revised_judge_focus = str(normalized_review.get("review__revised_judge_focus", "")).strip()

    row["case_id"] = TARGET_CASE_ID
    row["case_title"] = "纳瓦尔宝典 / 如何获得运气 / anchored_reaction_selectivity / v1.1 fill"
    row["curation_status"] = "excerpt_surface_v1_1_fill_candidate_v1"
    row["selection_mode"] = "chapter_wide_fill"
    row["selection_reason"] = revised_selection_reason or str(row.get("selection_reason", ""))
    row["judge_focus"] = revised_judge_focus or str(row.get("judge_focus", ""))
    row["benchmark_status"] = "unset"
    row["review_status"] = "builder_curated"
    row["review_history"] = []

    for key in (
        "review_latest",
        "human_review_latest",
        "llm_review_latest",
        "review_origin",
        "review_policy",
        "llm_review_decision",
        "human_review_decision",
        "human_review_notes",
        "human_review_problem_types",
        "metadata_sync",
        "review_suggested_bucket",
        "freeze_metadata",
    ):
        row.pop(key, None)

    row["notes"] = (
        str(row.get("notes", "")).strip()
        + " Prepared as the approved excerpt surface v1.1 narrow fill repair for chapter 22 with the adjudicator-sharpened anchored-reaction focus."
    ).strip()
    row["excerpt_surface_fill_metadata"] = {
        "fill_mode": "narrow_repair",
        "fill_version": "v1.1",
        "derived_from_case_id": SOURCE_CASE_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "source_review_action": str(normalized_review.get("review__action", "")).strip(),
        "source_review_problem_types": list(normalized_review.get("review__problem_types", []) or []),
    }
    return row


def _summary_payload(*, run_id: str) -> dict[str, Any]:
    row = _prepared_row()
    return {
        "run_id": run_id,
        "dataset_id": DATASET_ID,
        "dataset_path": _relative_to_root(DATASET_DIR),
        "source_case_id": SOURCE_CASE_ID,
        "prepared_case_id": TARGET_CASE_ID,
        "target_profile_id": str(row.get("target_profile_id", "")),
        "chapter_case_id": f"{row['source_id']}__{row['chapter_id']}",
        "selection_mode": str(row.get("selection_mode", "")),
        "source_packet_id": SOURCE_PACKET_ID,
    }


def _summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Excerpt Surface V1.1 Chapter-22 Fill Prep",
            "",
            f"- Run id: `{summary['run_id']}`",
            f"- Dataset id: `{summary['dataset_id']}`",
            f"- Prepared case id: `{summary['prepared_case_id']}`",
            f"- Source case id: `{summary['source_case_id']}`",
            f"- Chapter case id: `{summary['chapter_case_id']}`",
            "- Purpose: re-review the earlier chapter-22 anchored-reaction candidate after applying the adjudicator-sharpened focus.",
            "",
        ]
    )


def write_fill_dataset(*, run_id: str = DEFAULT_RUN_ID, overwrite: bool = True) -> dict[str, Any]:
    if DATASET_DIR.exists() and overwrite:
        for child in DATASET_DIR.iterdir():
            if child.is_file():
                child.unlink()
    elif DATASET_DIR.exists():
        raise FileExistsError(f"Target dataset already exists: {DATASET_DIR}")

    source_manifest = _load_json(SOURCE_DATASET_DIR / "manifest.json")
    row = _prepared_row()
    dataset_manifest_payload = {
        **dataset_manifest(
            dataset_id=DATASET_ID,
            family="excerpt_cases",
            language_track="zh",
            description="Excerpt surface v1.1 narrow chapter-22 fill candidate for re-review.",
            primary_file="cases.jsonl",
            source_manifest_refs=list(source_manifest.get("source_manifest_refs", []) or []),
            split_refs=[_relative_to_root(ROOT / "eval" / "manifests" / "splits" / "attentional_v2_excerpt_surface_v1_1_draft.json")],
            storage_mode="local-only",
        ),
        "dataset_build_artifact_refs": [
            _relative_to_root(
                ROOT / "state" / "dataset_build" / "build_runs" / run_id / SUMMARY_JSON_NAME
            )
        ],
        "fill_scope": {
            "surface": "excerpt_surface_v1_1",
            "chapter_case_id": "nawaer_baodian_private_zh__22",
            "mode": "narrow_repair",
        },
        "freeze_counts": {
            "row_count": 1,
            "primary_count": 1,
        },
    }
    write_json(DATASET_DIR / "manifest.json", dataset_manifest_payload)
    write_jsonl(DATASET_DIR / "cases.jsonl", [row])

    build_run_root = ROOT / "state" / "dataset_build" / "build_runs" / run_id
    summary_payload = _summary_payload(run_id=run_id)
    write_json(build_run_root / SUMMARY_JSON_NAME, summary_payload)
    (build_run_root / SUMMARY_MD_NAME).write_text(_summary_markdown(summary_payload), encoding="utf-8")
    return {
        "dataset_id": DATASET_ID,
        "dataset_path": _relative_to_root(DATASET_DIR),
        "prepared_case_id": TARGET_CASE_ID,
        "summary_json_path": _relative_to_root(build_run_root / SUMMARY_JSON_NAME),
        "summary_md_path": _relative_to_root(build_run_root / SUMMARY_MD_NAME),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            write_fill_dataset(
                run_id=str(args.run_id).strip() or DEFAULT_RUN_ID,
                overwrite=not bool(args.no_overwrite),
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
