"""Build the ROI-first excerpt micro-slice v1 draft manifest.

This micro-slice intentionally reuses the already reviewed human-notes-guided
excerpt freeze. It narrows the judged excerpt surface to two chapter-scoped
units so we can iterate quickly on bounded `attentional_v2` throughput repairs
before paying for another broad full-surface judged rerun.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_ID = "attentional_v2_excerpt_micro_slice_v1_draft"
MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / f"{MANIFEST_ID}.json"
SOURCE_MANIFEST_ID = "attentional_v2_human_notes_guided_excerpt_eval_v1_draft"
SOURCE_MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / f"{SOURCE_MANIFEST_ID}.json"

SELECTED_CHAPTER_CASE_IDS = (
    "nawaer_baodian_private_zh__22",
    "xidaduo_private_zh__15",
)
EXPANSION_CANDIDATE_CHAPTER_CASE_IDS = (
    "supremacy_private_en__13",
)
INSIGHT_TARGET_PROFILE_IDS = {
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
}
PRESSURE_ORDER = (
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
    "anchored_reaction_selectivity",
)
SELECTION_REASONS = {
    "nawaer_baodian_private_zh__22": (
        "High-ROI chapter with only five cases but unusually strong mixed pressure: "
        "one callback bridge, one distinction definition, and three tension reversals. "
        "It already produced the clearest non-placeholder judged evidence in the partial rerun."
    ),
    "xidaduo_private_zh__15": (
        "Dense, non-duplicative chapter with eight reviewed cases and low enough read cost "
        "to serve as the second fast-iteration anchor while throughput repair is underway."
    ),
}


def _relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON at {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _filter_grouped_case_ids(
    grouped_payload: dict[str, Any],
    *,
    allowed_case_ids: set[str],
    allowed_pressures: tuple[str, ...] | None = None,
) -> dict[str, list[str]]:
    if allowed_pressures is None:
        pressure_keys = tuple(str(key) for key in grouped_payload.keys())
    else:
        pressure_keys = allowed_pressures
    return {
        pressure: [
            str(case_id)
            for case_id in grouped_payload.get(pressure, []) or []
            if str(case_id) in allowed_case_ids
        ]
        for pressure in pressure_keys
        if [
            str(case_id)
            for case_id in grouped_payload.get(pressure, []) or []
            if str(case_id) in allowed_case_ids
        ]
    }


def build_manifest_payload() -> dict[str, Any]:
    source_manifest = _load_json(SOURCE_MANIFEST_PATH)
    source_splits = dict(source_manifest.get("splits") or {})
    primary_split = dict(source_splits.get("excerpt_core_primary_frozen_draft") or {})
    insight_split = dict(source_splits.get("insight_and_clarification_subset_frozen_draft") or {})
    source_by_chapter = dict(primary_split.get("by_chapter") or {})

    selected_by_chapter: dict[str, list[str]] = {}
    missing_chapters: list[str] = []
    for chapter_case_id in SELECTED_CHAPTER_CASE_IDS:
        case_ids = [str(case_id) for case_id in source_by_chapter.get(chapter_case_id, []) if str(case_id).strip()]
        if not case_ids:
            missing_chapters.append(chapter_case_id)
            continue
        selected_by_chapter[chapter_case_id] = case_ids
    if missing_chapters:
        raise ValueError(f"Missing chapter rows in source manifest: {', '.join(missing_chapters)}")

    selected_all = [
        case_id
        for chapter_case_id in SELECTED_CHAPTER_CASE_IDS
        for case_id in selected_by_chapter[chapter_case_id]
    ]
    selected_case_id_set = set(selected_all)
    if len(selected_all) != len(selected_case_id_set):
        raise ValueError("Micro-slice selection unexpectedly contains duplicate case ids.")

    insight_all = [
        str(case_id)
        for case_id in insight_split.get("all", []) or []
        if str(case_id) in selected_case_id_set
    ]
    insight_case_id_set = set(insight_all)

    return {
        "manifest_id": MANIFEST_ID,
        "description": (
            "ROI-first excerpt micro-slice v1 draft reused from the reviewed "
            "human-notes-guided excerpt freeze for fast judged iteration and "
            "bounded attentional_v2 throughput repair."
        ),
        "targets": [
            "reader_character.selective_legibility",
            "reader_value.insight_and_clarification",
        ],
        "benchmark_shape": {
            "kind": "excerpt_micro_slice_v1",
            "surface_role": "excerpt_surface_micro_harness",
            "chapter_unit_target_total": len(SELECTED_CHAPTER_CASE_IDS),
            "excerpt_primary_target_total": len(selected_all),
            "insight_and_clarification_target_total": len(insight_all),
            "intended_use": [
                "roi_first_judged_excerpt_iteration",
                "attentional_v2_throughput_repair_validation",
            ],
        },
        "selection_policy": {
            "base_surface_manifest": _relative_to_root(SOURCE_MANIFEST_PATH),
            "selection_rule": (
                "Prefer already reviewed chapter units with dense, non-duplicative case "
                "coverage, clear local pressure, and acceptable read cost."
            ),
            "expansion_rule": (
                "Keep the first slice at two chapters; add supremacy_private_en__13 only "
                "after the initial throughput repair loop if another cross-language check "
                "is needed."
            ),
        },
        "source_origin_rule": "Do not use public/private/manual/agent-downloaded provenance as benchmark strata.",
        "source_refs": dict(source_manifest.get("source_refs") or {}),
        "selected_chapter_units": [
            {
                "chapter_case_id": chapter_case_id,
                "selection_role": "micro_slice_keep",
                "origin_line": "human_notes_guided_dataset_v1",
                "selection_reason": SELECTION_REASONS[chapter_case_id],
            }
            for chapter_case_id in SELECTED_CHAPTER_CASE_IDS
        ],
        "expansion_candidate_chapter_units": list(EXPANSION_CANDIDATE_CHAPTER_CASE_IDS),
        "quota_status": {
            "chapter_units": {
                "target_total": len(SELECTED_CHAPTER_CASE_IDS),
                "ready_now": len(SELECTED_CHAPTER_CASE_IDS),
                "gap": 0,
            },
            "excerpt_primary": {
                "target_total": len(selected_all),
                "ready_now": len(selected_all),
                "gap": 0,
            },
            "insight_and_clarification_subset": {
                "derived_from_profiles": sorted(INSIGHT_TARGET_PROFILE_IDS),
                "target_total": len(insight_all),
                "ready_now": len(insight_all),
                "gap": 0,
            },
        },
        "splits": {
            "excerpt_core_primary_frozen_draft": {
                "by_chapter": selected_by_chapter,
                "by_pressure": _filter_grouped_case_ids(
                    dict(primary_split.get("by_pressure") or {}),
                    allowed_case_ids=selected_case_id_set,
                    allowed_pressures=PRESSURE_ORDER,
                ),
                "all": selected_all,
            },
            "insight_and_clarification_subset_frozen_draft": {
                "by_pressure": _filter_grouped_case_ids(
                    dict(insight_split.get("by_pressure") or {}),
                    allowed_case_ids=insight_case_id_set,
                    allowed_pressures=("distinction_definition", "tension_reversal", "callback_bridge"),
                ),
                "all": insight_all,
            },
        },
    }


def write_manifest() -> dict[str, Any]:
    payload = build_manifest_payload()
    _write_json(MANIFEST_PATH, payload)
    return {
        "manifest_path": _relative_to_root(MANIFEST_PATH),
        "chapter_unit_count": len(payload["selected_chapter_units"]),
        "excerpt_case_count": len(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"]),
        "insight_case_count": len(payload["splits"]["insight_and_clarification_subset_frozen_draft"]["all"]),
    }
