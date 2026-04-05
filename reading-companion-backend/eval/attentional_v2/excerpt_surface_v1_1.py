"""Compose the excerpt surface v1.1 draft from reviewed frozen datasets.

This module intentionally does not mutate the currently running notes-guided
judged rerun inputs. It builds a fresh local-only excerpt-surface namespace by:

1. reusing reviewed frozen rows from the human-notes-guided and clustered lines
2. applying the current grouped duplicate controls chapter-by-chapter
3. writing fresh local dataset packages plus a tracked draft split manifest

The resulting surface is draft evidence for the next excerpt retune lane. It is
safe to build while the earlier judged rerun is still active because it only
reads the older frozen inputs and writes new output paths.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .corpus_builder import ROOT, dataset_manifest, write_json, write_jsonl
from .question_aligned_case_construction import (
    DEFAULT_CLUSTERED_MIN_ANCHOR_DISTANCE,
    EXCERPT_SURFACE_RETUNE_SELECTION_MODE,
    _clustered_candidate_allowed,
)


MANIFEST_ID = "attentional_v2_excerpt_surface_v1_1_draft"
MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / f"{MANIFEST_ID}.json"
DEFAULT_RUN_ID = "excerpt_surface_v1_1_20260405"
SUMMARY_JSON_NAME = "excerpt_surface_v1_1_summary.json"
SUMMARY_MD_NAME = "excerpt_surface_v1_1_summary.md"

EXCERPT_DATASET_IDS = {
    "en": "attentional_v2_excerpt_surface_v1_1_excerpt_en",
    "zh": "attentional_v2_excerpt_surface_v1_1_excerpt_zh",
}
EXCERPT_DATASET_DIRS = {
    language: ROOT / "state" / "eval_local_datasets" / "excerpt_cases" / dataset_id
    for language, dataset_id in EXCERPT_DATASET_IDS.items()
}

SOURCE_DATASET_SPECS: tuple[dict[str, Any], ...] = (
    {
        "dataset_dir": ROOT
        / "state"
        / "eval_local_datasets"
        / "excerpt_cases"
        / "attentional_v2_human_notes_guided_dataset_v1_excerpt_en_reviewed_cluster_freeze_20260404",
        "origin_line": "human_notes_guided_dataset_v1",
        "dataset_family": "notes_guided_reviewed_freeze",
    },
    {
        "dataset_dir": ROOT
        / "state"
        / "eval_local_datasets"
        / "excerpt_cases"
        / "attentional_v2_human_notes_guided_dataset_v1_excerpt_zh_reviewed_cluster_freeze_complete_20260404",
        "origin_line": "human_notes_guided_dataset_v1",
        "dataset_family": "notes_guided_reviewed_freeze",
    },
    {
        "dataset_dir": ROOT
        / "state"
        / "eval_local_datasets"
        / "excerpt_cases"
        / "attentional_v2_clustered_benchmark_v1_excerpt_en",
        "origin_line": "clustered_benchmark_v1",
        "dataset_family": "clustered_frozen_excerpt",
    },
    {
        "dataset_dir": ROOT
        / "state"
        / "eval_local_datasets"
        / "excerpt_cases"
        / "attentional_v2_clustered_benchmark_v1_excerpt_zh",
        "origin_line": "clustered_benchmark_v1",
        "dataset_family": "clustered_frozen_excerpt",
    },
)

KEPT_CHAPTER_CASE_IDS = (
    "value_of_others_private_en__8",
    "huochu_shengming_de_yiyi_private_zh__8",
    "xidaduo_private_zh__15",
    "nawaer_baodian_private_zh__13",
    "nawaer_baodian_private_zh__22",
)
IMPORTED_CHAPTER_CASE_IDS = (
    "supremacy_private_en__13",
    "meiguoren_de_xingge_private_zh__19",
)
FIXED_CHAPTER_CASE_IDS = (*KEPT_CHAPTER_CASE_IDS, *IMPORTED_CHAPTER_CASE_IDS)
DROPPED_CHAPTER_CASE_IDS = (
    "mangge_zhi_dao_private_zh__18",
    "mangge_zhi_dao_private_zh__26",
    "nawaer_baodian_private_zh__23",
)
FALLBACK_DONOR_CHAPTER_CASE_IDS = (
    "steve_jobs_private_en__17",
    "zouchu_weiyi_zhenliguan_private_zh__14",
)
INSIGHT_TARGET_PROFILE_IDS = {
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
}
ALL_PRESSURE_ORDER = (
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
    "anchored_reaction_selectivity",
)
CHAPTER_TARGET_MIN = 8
CHAPTER_TARGET_MAX = 10
CHAPTER_HARD_CAP = 12
CHAPTER_HONEST_SHORT_FLOOR = 6
PRIMARY_TARGET_RANGE = {"min": 56, "max": 70}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _chapter_case_id_for_row(row: dict[str, Any]) -> str:
    return f"{row['source_id']}__{row['chapter_id']}"


def _language_track_for_row(row: dict[str, Any]) -> str:
    language = str(row.get("output_language") or row.get("language_track") or "").strip()
    if language in {"en", "zh"}:
        return language
    raise ValueError(f"Unsupported language track for row {row.get('case_id', '<unknown>')}: {language!r}")


def _sentence_index(sentence_id: Any) -> int:
    cleaned = str(sentence_id or "").strip()
    if "-s" not in cleaned:
        return 0
    suffix = cleaned.rsplit("-s", 1)[-1]
    return int(suffix) - 1 if suffix.isdigit() else 0


def _row_note_backed(row: dict[str, Any]) -> bool:
    return bool(
        row.get("selection_note_ids")
        or row.get("selection_note_provenance")
        or row.get("selection_notes")
        or str(row.get("selection_group_kind", "")).strip().startswith("notes_guided")
    )


def _row_freeze_role_priority(row: dict[str, Any]) -> int:
    freeze_role = str(row.get("benchmark_freeze_role", "")).strip()
    if freeze_role == "primary":
        return 0
    if freeze_role == "reserve":
        return 1
    case_id = str(row.get("case_id", ""))
    if "__reserve_" in case_id:
        return 2
    return 0


def _row_priority_key(row: dict[str, Any]) -> tuple[int, int, int, float, float, str]:
    benchmark_status = str(row.get("benchmark_status", "")).strip()
    reviewed_priority = 0 if benchmark_status == "reviewed_active" else 1
    return (
        0 if _row_note_backed(row) else 1,
        _row_freeze_role_priority(row),
        reviewed_priority,
        -float(row.get("construction_priority") or 0.0),
        -float(row.get("judgeability_score") or 0.0),
        str(row.get("case_id", "")),
    )


def _candidate_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": str(row["source_id"]),
        "chapter_id": str(row["chapter_id"]),
        "target_profile_ids": [str(row.get("target_profile_id", ""))],
        "excerpt_sentence_ids": list(row.get("excerpt_sentence_ids") or []),
        "anchor_sentence_ids": [str(row.get("anchor_sentence_id", ""))],
        "anchor_sentence_index": _sentence_index(row.get("anchor_sentence_id")),
        "excerpt_start_index": _sentence_index(row.get("start_sentence_id")),
        "excerpt_end_index": _sentence_index(row.get("end_sentence_id")),
    }


def _source_spec_for_chapter_case_id(chapter_case_id: str) -> str:
    if chapter_case_id in KEPT_CHAPTER_CASE_IDS:
        return "keep"
    if chapter_case_id in IMPORTED_CHAPTER_CASE_IDS:
        return "import"
    if chapter_case_id in FALLBACK_DONOR_CHAPTER_CASE_IDS:
        return "fallback_donor"
    if chapter_case_id in DROPPED_CHAPTER_CASE_IDS:
        return "drop"
    return "other"


def _read_source_dataset(dataset_dir: Path, *, origin_line: str, dataset_family: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _load_json(dataset_dir / "manifest.json")
    primary_file = str(manifest.get("primary_file", "")).strip()
    if not primary_file:
        raise ValueError(f"Dataset manifest missing primary_file: {dataset_dir / 'manifest.json'}")
    rows = _load_jsonl(dataset_dir / primary_file)
    annotated_rows: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        copied["_source_dataset_id"] = str(manifest.get("dataset_id", "")).strip()
        copied["_source_dataset_dir"] = _relative_to_root(dataset_dir)
        copied["_origin_line"] = origin_line
        copied["_dataset_family"] = dataset_family
        copied["_chapter_case_id"] = _chapter_case_id_for_row(copied)
        annotated_rows.append(copied)
    return manifest, annotated_rows


def _selected_rows_by_chapter(source_rows: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        chapter_case_id = str(row["_chapter_case_id"])
        if chapter_case_id not in FIXED_CHAPTER_CASE_IDS:
            continue
        grouped[chapter_case_id].append(row)

    selected_rows: dict[str, list[dict[str, Any]]] = {}
    dropped_case_ids: dict[str, list[str]] = {}
    for chapter_case_id in FIXED_CHAPTER_CASE_IDS:
        candidates = sorted(grouped.get(chapter_case_id, []), key=_row_priority_key)
        retained: list[dict[str, Any]] = []
        dropped: list[str] = []
        for row in candidates:
            if len(retained) >= CHAPTER_HARD_CAP:
                dropped.append(str(row["case_id"]))
                continue
            if not _clustered_candidate_allowed(
                candidate=_candidate_from_row(row),
                existing=[_candidate_from_row(item) for item in retained],
                same_profile_anchor_distance=DEFAULT_CLUSTERED_MIN_ANCHOR_DISTANCE,
            ):
                dropped.append(str(row["case_id"]))
                continue
            retained.append(row)
        selected_rows[chapter_case_id] = retained
        dropped_case_ids[chapter_case_id] = dropped
    return selected_rows, dropped_case_ids


def _freeze_rows_for_output(rows: list[dict[str, Any]], *, frozen_at: str) -> list[dict[str, Any]]:
    frozen_rows: list[dict[str, Any]] = []
    for freeze_order, row in enumerate(rows):
        copied = {key: value for key, value in row.items() if not str(key).startswith("_")}
        freeze_metadata = dict(copied.get("freeze_metadata") or {})
        freeze_metadata.update(
            {
                "frozen_from_dataset_id": str(row.get("_source_dataset_id", "")).strip(),
                "frozen_from_dataset_dir": str(row.get("_source_dataset_dir", "")).strip(),
                "frozen_at": frozen_at,
                "benchmark_status_at_freeze": str(copied.get("benchmark_status", "")),
                "review_status_at_freeze": str(copied.get("review_status", "")),
                "freeze_role": "primary",
                "freeze_order": freeze_order,
                "origin_line": str(row.get("_origin_line", "")).strip(),
            }
        )
        copied["freeze_metadata"] = freeze_metadata
        copied["benchmark_freeze_role"] = "primary"
        copied["excerpt_surface_version"] = "v1.1"
        copied["excerpt_surface_origin_line"] = str(row.get("_origin_line", "")).strip()
        copied["excerpt_surface_selection_mode"] = EXCERPT_SURFACE_RETUNE_SELECTION_MODE
        frozen_rows.append(copied)
    return frozen_rows


def _grouped_case_ids_by_pressure(rows: list[dict[str, Any]], *, allowed_pressures: tuple[str, ...]) -> dict[str, list[str]]:
    payload = {pressure: [] for pressure in allowed_pressures}
    for row in rows:
        pressure = str(row.get("target_profile_id", "")).strip()
        if pressure in payload:
            payload[pressure].append(str(row["case_id"]))
    return payload


def _chapter_summary_payload(rows_by_chapter: dict[str, list[dict[str, Any]]], dropped_case_ids: dict[str, list[str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for chapter_case_id in FIXED_CHAPTER_CASE_IDS:
        rows = list(rows_by_chapter.get(chapter_case_id, []))
        pressure_counts = Counter(str(row.get("target_profile_id", "")).strip() for row in rows)
        payload[chapter_case_id] = {
            "chapter_case_id": chapter_case_id,
            "selection_role": _source_spec_for_chapter_case_id(chapter_case_id),
            "origin_lines": sorted({str(row.get("_origin_line", "")).strip() for row in rows if str(row.get("_origin_line", "")).strip()}),
            "selected_case_count": len(rows),
            "selected_case_ids": [str(row["case_id"]) for row in rows],
            "pressure_counts": dict(sorted((key, value) for key, value in pressure_counts.items() if key)),
            "dropped_case_ids": list(dropped_case_ids.get(chapter_case_id, [])),
            "below_floor": len(rows) < CHAPTER_HONEST_SHORT_FLOOR,
            "target_band_status": (
                "below_floor"
                if len(rows) < CHAPTER_HONEST_SHORT_FLOOR
                else "below_target"
                if len(rows) < CHAPTER_TARGET_MIN
                else "in_target_band"
                if len(rows) <= CHAPTER_TARGET_MAX
                else "at_cap"
                if len(rows) == CHAPTER_HARD_CAP
                else "above_target_band"
            ),
        }
    return payload


def _markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Excerpt Surface V1.1 Draft Summary",
        "",
        f"- Built at: `{summary['built_at']}`",
        f"- Run id: `{summary['run_id']}`",
        f"- Manifest: `{summary['manifest_path']}`",
        "",
        "## Chapter Roster",
    ]
    for chapter_case_id in FIXED_CHAPTER_CASE_IDS:
        chapter_summary = summary["chapter_summary"][chapter_case_id]
        lines.append(
            f"- `{chapter_case_id}`: `{chapter_summary['selected_case_count']}` selected, status `{chapter_summary['target_band_status']}`"
        )
    if summary["chapters_below_floor"]:
        lines.extend(
            [
                "",
                "## Honest Shortfalls",
                *[
                    f"- `{chapter_case_id}`: still below floor `{CHAPTER_HONEST_SHORT_FLOOR}` after reuse-only composition"
                    for chapter_case_id in summary["chapters_below_floor"]
                ],
            ]
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- This draft reuses reviewed frozen rows only and does not mutate the currently running notes-guided judged rerun inputs.",
            "- `value_of_others_private_en__8` is deduped back down to unique spans before reuse.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_draft_payloads(*, run_id: str = DEFAULT_RUN_ID) -> dict[str, Any]:
    source_manifests: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    source_manifest_refs: list[str] = []
    split_refs: list[str] = [_relative_to_root(MANIFEST_PATH)]
    for spec in SOURCE_DATASET_SPECS:
        manifest, rows = _read_source_dataset(
            spec["dataset_dir"],
            origin_line=str(spec["origin_line"]),
            dataset_family=str(spec["dataset_family"]),
        )
        source_manifests.append(manifest)
        source_rows.extend(rows)
        for ref in manifest.get("source_manifest_refs", []) or []:
            cleaned = str(ref).strip()
            if cleaned and cleaned not in source_manifest_refs:
                source_manifest_refs.append(cleaned)

    selected_rows_by_chapter, dropped_case_ids = _selected_rows_by_chapter(source_rows)
    chapter_summary = _chapter_summary_payload(selected_rows_by_chapter, dropped_case_ids)

    rows_by_language: dict[str, list[dict[str, Any]]] = {"en": [], "zh": []}
    frozen_at = utc_now()
    for chapter_case_id in FIXED_CHAPTER_CASE_IDS:
        chapter_rows = _freeze_rows_for_output(selected_rows_by_chapter.get(chapter_case_id, []), frozen_at=frozen_at)
        if not chapter_rows:
            continue
        language_track = _language_track_for_row(chapter_rows[0])
        rows_by_language[language_track].extend(chapter_rows)

    for language_track in rows_by_language:
        rows_by_language[language_track].sort(
            key=lambda row: (
                str(row["source_id"]),
                int(row.get("chapter_number", 0) or 0),
                int(row.get("anchor_sentence_index", 0) or 0),
                str(row["case_id"]),
            )
        )

    all_rows = rows_by_language["en"] + rows_by_language["zh"]
    insight_rows = [
        row for row in all_rows if str(row.get("target_profile_id", "")).strip() in INSIGHT_TARGET_PROFILE_IDS
    ]
    chapters_below_floor = [
        chapter_case_id
        for chapter_case_id, payload in chapter_summary.items()
        if bool(payload.get("below_floor"))
    ]

    selected_chapter_units = [
        {
            "chapter_case_id": chapter_case_id,
            "selection_role": _source_spec_for_chapter_case_id(chapter_case_id),
            "origin_lines": chapter_summary[chapter_case_id]["origin_lines"],
        }
        for chapter_case_id in FIXED_CHAPTER_CASE_IDS
    ]
    by_chapter_case_ids = {
        chapter_case_id: [
            str(row["case_id"])
            for row in all_rows
            if _chapter_case_id_for_row(row) == chapter_case_id
        ]
        for chapter_case_id in FIXED_CHAPTER_CASE_IDS
    }
    benchmark_shape = {
        "kind": "excerpt_surface_v1_1",
        "surface_role": "excerpt_surface_eval",
        "chapter_unit_target_total": len(FIXED_CHAPTER_CASE_IDS),
        "excerpt_primary_target_range": dict(PRIMARY_TARGET_RANGE),
        "chapter_primary_target_band": {"min": CHAPTER_TARGET_MIN, "max": CHAPTER_TARGET_MAX},
        "chapter_hard_cap": CHAPTER_HARD_CAP,
        "chapter_honest_short_floor": CHAPTER_HONEST_SHORT_FLOOR,
    }
    manifest_payload = {
        "manifest_id": MANIFEST_ID,
        "description": "Excerpt surface v1.1 draft composed incrementally from reviewed notes-guided and clustered freezes.",
        "targets": [
            "reader_character.selective_legibility",
            "reader_value.insight_and_clarification",
        ],
        "benchmark_shape": benchmark_shape,
        "storage_note": "`state/eval_local_datasets/` remains a storage term only; excerpt-surface semantics live in this manifest and the evaluation docs.",
        "source_origin_rule": "Do not use public/private/manual/agent-downloaded provenance as benchmark strata.",
        "source_refs": {
            "source_manifests": source_manifest_refs,
            "excerpt_case_datasets": [
                _relative_to_root(EXCERPT_DATASET_DIRS["en"]),
                _relative_to_root(EXCERPT_DATASET_DIRS["zh"]),
            ],
        },
        "selected_chapter_units": selected_chapter_units,
        "dropped_chapter_units": list(DROPPED_CHAPTER_CASE_IDS),
        "fallback_donor_chapter_units": list(FALLBACK_DONOR_CHAPTER_CASE_IDS),
        "quota_status": {
            "chapter_units": {
                "target_total": len(FIXED_CHAPTER_CASE_IDS),
                "ready_now": len(FIXED_CHAPTER_CASE_IDS),
                "gap": 0,
            },
            "excerpt_primary": {
                "target_range": dict(PRIMARY_TARGET_RANGE),
                "ready_now": len(all_rows),
                "gap_to_floor": max(PRIMARY_TARGET_RANGE["min"] - len(all_rows), 0),
            },
            "insight_and_clarification_subset": {
                "derived_from_profiles": sorted(INSIGHT_TARGET_PROFILE_IDS),
                "ready_now": len(insight_rows),
                "gap": 0,
            },
            "chapter_floor": {
                "target_min_per_chapter": CHAPTER_HONEST_SHORT_FLOOR,
                "chapters_below_floor": chapters_below_floor,
            },
        },
        "splits": {
            "excerpt_core_primary_frozen_draft": {
                "by_chapter": by_chapter_case_ids,
                "by_pressure": _grouped_case_ids_by_pressure(all_rows, allowed_pressures=ALL_PRESSURE_ORDER),
                "all": [str(row["case_id"]) for row in all_rows],
            },
            "insight_and_clarification_subset_frozen_draft": {
                "by_pressure": _grouped_case_ids_by_pressure(
                    insight_rows,
                    allowed_pressures=("distinction_definition", "tension_reversal", "callback_bridge"),
                ),
                "all": [str(row["case_id"]) for row in insight_rows],
            },
        },
    }
    build_run_root = ROOT / "state" / "dataset_build" / "build_runs" / run_id
    summary_json_path = build_run_root / SUMMARY_JSON_NAME
    summary_md_path = build_run_root / SUMMARY_MD_NAME
    summary_payload = {
        "run_id": run_id,
        "built_at": frozen_at,
        "manifest_id": MANIFEST_ID,
        "manifest_path": _relative_to_root(MANIFEST_PATH),
        "dataset_ids": dict(EXCERPT_DATASET_IDS),
        "selected_chapter_units": selected_chapter_units,
        "chapter_summary": chapter_summary,
        "chapters_below_floor": chapters_below_floor,
        "selected_case_count": len(all_rows),
        "insight_case_count": len(insight_rows),
        "source_dataset_ids": sorted(
            {
                str(row.get("_source_dataset_id", "")).strip()
                for row in source_rows
                if str(row.get("_source_dataset_id", "")).strip()
            }
        ),
    }
    return {
        "manifest_payload": manifest_payload,
        "dataset_rows_by_language": rows_by_language,
        "dataset_manifest_refs": source_manifest_refs,
        "split_refs": split_refs,
        "summary_payload": summary_payload,
        "summary_json_path": summary_json_path,
        "summary_md_path": summary_md_path,
    }


def write_draft_artifacts(*, run_id: str = DEFAULT_RUN_ID, overwrite: bool = True) -> dict[str, Any]:
    payloads = build_draft_payloads(run_id=run_id)
    manifest_payload = payloads["manifest_payload"]
    dataset_rows_by_language = payloads["dataset_rows_by_language"]
    source_manifest_refs = payloads["dataset_manifest_refs"]
    split_refs = payloads["split_refs"]
    summary_payload = payloads["summary_payload"]
    summary_json_path = payloads["summary_json_path"]
    summary_md_path = payloads["summary_md_path"]
    for dataset_dir in EXCERPT_DATASET_DIRS.values():
        if dataset_dir.exists() and not overwrite:
            raise FileExistsError(f"Target dataset already exists: {dataset_dir}")
    for language_track, dataset_dir in EXCERPT_DATASET_DIRS.items():
        if dataset_dir.exists() and overwrite:
            for child in dataset_dir.iterdir():
                if child.is_file():
                    child.unlink()
        dataset_manifest_payload = {
            **dataset_manifest(
                dataset_id=EXCERPT_DATASET_IDS[language_track],
                family="excerpt_cases",
                language_track=language_track,
                description=f"Excerpt surface v1.1 draft excerpt cases ({language_track}).",
                primary_file="cases.jsonl",
                source_manifest_refs=source_manifest_refs,
                split_refs=split_refs,
                storage_mode="local-only",
            ),
            "dataset_build_artifact_refs": [
                _relative_to_root(summary_json_path),
            ],
            "freeze_criteria": {
                "selection_mode": EXCERPT_SURFACE_RETUNE_SELECTION_MODE,
                "chapter_case_ids": list(FIXED_CHAPTER_CASE_IDS),
                "chapter_primary_target_band": {"min": CHAPTER_TARGET_MIN, "max": CHAPTER_TARGET_MAX},
                "chapter_hard_cap": CHAPTER_HARD_CAP,
                "chapter_honest_short_floor": CHAPTER_HONEST_SHORT_FLOOR,
                "duplicate_controls": [
                    "same_span_rejection",
                    "same_anchor_rejection",
                    "same_profile_overlap_rejection",
                    "same_profile_anchor_distance_guard",
                ],
            },
            "freeze_counts": {
                "row_count": len(dataset_rows_by_language[language_track]),
                "primary_count": len(dataset_rows_by_language[language_track]),
            },
        }
        write_json(dataset_dir / "manifest.json", dataset_manifest_payload)
        write_jsonl(dataset_dir / "cases.jsonl", dataset_rows_by_language[language_track])

    write_json(MANIFEST_PATH, manifest_payload)
    write_json(summary_json_path, summary_payload)
    summary_md_path.parent.mkdir(parents=True, exist_ok=True)
    summary_md_path.write_text(_markdown_summary(summary_payload), encoding="utf-8")
    return {
        "manifest_path": _relative_to_root(MANIFEST_PATH),
        "dataset_paths": {language: _relative_to_root(path) for language, path in EXCERPT_DATASET_DIRS.items()},
        "summary_json_path": _relative_to_root(summary_json_path),
        "summary_md_path": _relative_to_root(summary_md_path),
        "selected_case_count": summary_payload["selected_case_count"],
        "insight_case_count": summary_payload["insight_case_count"],
        "chapters_below_floor": summary_payload["chapters_below_floor"],
    }
