"""Freeze clustered benchmark v1 into final local-only benchmark packages."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any

try:
    from .build_private_library_supplement import (
        CLUSTERED_BENCHMARK_MODE,
        live_build_ids,
        namespaced_build_ids,
    )
    from .corpus_builder import (
        ROOT,
        STATE_LOCAL_DATASET_ROOT,
        dataset_manifest,
        load_json,
        write_json,
        write_jsonl,
    )
except ImportError:  # pragma: no cover - script execution path
    from build_private_library_supplement import (  # type: ignore
        CLUSTERED_BENCHMARK_MODE,
        live_build_ids,
        namespaced_build_ids,
    )
    from corpus_builder import (  # type: ignore
        ROOT,
        STATE_LOCAL_DATASET_ROOT,
        dataset_manifest,
        load_json,
        write_json,
        write_jsonl,
    )


BLOCKING_PROBLEM_TYPES = {
    "wrong_bucket",
    "ambiguous_focus",
    "weak_excerpt",
    "too_easy",
}
INSIGHT_AND_CLARIFICATION_PROFILE_IDS = {
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
}
EXCERPT_PRESSURE_ORDER = (
    "distinction_definition",
    "tension_reversal",
    "callback_bridge",
    "anchored_reaction_selectivity",
)
DEFAULT_SMOKE2_RUN_ID = "clustered_benchmark_v1_smoke2_20260403"
DEFAULT_FREEZE_RUN_ID = "clustered_benchmark_v1_freeze_20260404"
DEFAULT_PRIMARY_TARGET_PER_CHAPTER = 10
DEFAULT_RESERVE_TARGET_PER_CHAPTER = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object row in {path}")
        rows.append(payload)
    return rows


def chapter_case_id_for_row(row: dict[str, Any]) -> str:
    source_id = str(row.get("source_id", "")).strip()
    chapter_id = str(row.get("chapter_id", "")).strip()
    if not source_id or not chapter_id:
        raise ValueError(f"Row missing source_id/chapter_id: {row.get('case_id', '<unknown>')}")
    return f"{source_id}__{chapter_id}"


def language_track_for_chapter_case_id(chapter_case_id: str) -> str:
    value = str(chapter_case_id).strip()
    if "_zh__" in value:
        return "zh"
    if "_en__" in value:
        return "en"
    raise ValueError(f"Could not infer language track from chapter_case_id: {chapter_case_id}")


def problem_types_for_row(row: dict[str, Any]) -> set[str]:
    review = row.get("review_latest")
    if not isinstance(review, dict):
        return set()
    values = review.get("problem_types")
    if not isinstance(values, list):
        return set()
    return {str(value).strip() for value in values if str(value).strip()}


def review_action_for_row(row: dict[str, Any]) -> str:
    review = row.get("review_latest")
    if not isinstance(review, dict):
        return ""
    return str(review.get("action", "")).strip()


def review_notes_for_row(row: dict[str, Any]) -> str:
    review = row.get("review_latest")
    if not isinstance(review, dict):
        return ""
    return str(review.get("notes", "")).strip()


def text_noise_is_negligible(notes: str) -> bool:
    normalized = str(notes or "").strip().lower()
    if not normalized:
        return False
    return "negligible" in normalized or "minor" in normalized


def is_freeze_eligible(row: dict[str, Any]) -> bool:
    if review_action_for_row(row) != "keep":
        return False
    problem_types = problem_types_for_row(row)
    if problem_types & BLOCKING_PROBLEM_TYPES:
        return False
    if "text_noise" in problem_types and not text_noise_is_negligible(review_notes_for_row(row)):
        return False
    return True


def with_source_order(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        copied = dict(row)
        copied["_source_order"] = index
        ordered.append(copied)
    return ordered


def primary_rank_key(row: dict[str, Any]) -> tuple[float, float, int]:
    construction_priority = float(row.get("construction_priority") or 0.0)
    judgeability_score = float(row.get("judgeability_score") or 0.0)
    source_order = int(row.get("_source_order") or 0)
    return (-construction_priority, -judgeability_score, source_order)


def reserve_rank_key(row: dict[str, Any]) -> tuple[int, int]:
    reserve_rank = int(row.get("reserve_rank") or 9999)
    source_order = int(row.get("_source_order") or 0)
    return (reserve_rank, source_order)


@dataclass(frozen=True)
class ChapterFreezeResult:
    chapter_case_id: str
    primary_rows: list[dict[str, Any]]
    promoted_reserve_rows: list[dict[str, Any]]
    reserve_rows: list[dict[str, Any]]
    overflow_primary_rows: list[dict[str, Any]]
    eligible_primary_count: int
    eligible_reserve_count: int
    saturated_shortfall: int

    @property
    def primary_case_ids(self) -> list[str]:
        return [str(row["case_id"]) for row in self.primary_rows]

    @property
    def reserve_case_ids(self) -> list[str]:
        return [str(row["case_id"]) for row in self.reserve_rows]


def freeze_one_chapter(
    *,
    chapter_case_id: str,
    primary_rows: list[dict[str, Any]],
    reserve_rows: list[dict[str, Any]],
    primary_target: int,
    reserve_target: int,
) -> ChapterFreezeResult:
    eligible_primary_rows = sorted((row for row in primary_rows if is_freeze_eligible(row)), key=primary_rank_key)
    selected_primary_rows = list(eligible_primary_rows[:primary_target])
    overflow_primary_rows = list(eligible_primary_rows[primary_target:])

    eligible_reserve_rows = sorted((row for row in reserve_rows if is_freeze_eligible(row)), key=reserve_rank_key)
    promoted_reserve_rows: list[dict[str, Any]] = []
    while len(selected_primary_rows) < primary_target and eligible_reserve_rows:
        promoted_reserve_rows.append(eligible_reserve_rows.pop(0))
        selected_primary_rows.append(promoted_reserve_rows[-1])

    chapter_reserve_rows = list(overflow_primary_rows[:reserve_target])
    if len(chapter_reserve_rows) < reserve_target:
        needed = reserve_target - len(chapter_reserve_rows)
        chapter_reserve_rows.extend(eligible_reserve_rows[:needed])

    saturated_shortfall = max(primary_target - len(selected_primary_rows), 0)
    return ChapterFreezeResult(
        chapter_case_id=chapter_case_id,
        primary_rows=selected_primary_rows,
        promoted_reserve_rows=promoted_reserve_rows,
        reserve_rows=chapter_reserve_rows,
        overflow_primary_rows=overflow_primary_rows,
        eligible_primary_count=len(eligible_primary_rows),
        eligible_reserve_count=len(eligible_reserve_rows) + len(promoted_reserve_rows),
        saturated_shortfall=saturated_shortfall,
    )


def grouped_case_ids_by_pressure(rows: list[dict[str, Any]], *, allowed_pressures: tuple[str, ...]) -> dict[str, list[str]]:
    payload = {pressure: [] for pressure in allowed_pressures}
    for row in rows:
        pressure = str(row.get("target_profile_id", "")).strip()
        if pressure in payload:
            payload[pressure].append(str(row["case_id"]))
    return payload


def build_chapter_core_split(selected_chapter_case_ids: list[str]) -> dict[str, Any]:
    by_language: dict[str, list[str]] = {"en": [], "zh": []}
    for chapter_case_id in selected_chapter_case_ids:
        by_language[language_track_for_chapter_case_id(chapter_case_id)].append(chapter_case_id)
    return {
        "by_language": {key: value for key, value in by_language.items() if value},
        "all": list(selected_chapter_case_ids),
    }


def build_freeze_manifest_payload(
    *,
    selected_chapter_case_ids: list[str],
    chapter_results: dict[str, ChapterFreezeResult],
    excerpt_primary_target_total: int,
    reserve_target_total: int,
) -> dict[str, Any]:
    primary_rows_all: list[dict[str, Any]] = []
    reserve_rows_all: list[dict[str, Any]] = []
    by_chapter_primary: dict[str, list[str]] = {}
    by_chapter_reserve: dict[str, list[str]] = {}
    per_chapter_summary: dict[str, Any] = {}
    for chapter_case_id in selected_chapter_case_ids:
        result = chapter_results[chapter_case_id]
        primary_rows_all.extend(result.primary_rows)
        reserve_rows_all.extend(result.reserve_rows)
        by_chapter_primary[chapter_case_id] = result.primary_case_ids
        by_chapter_reserve[chapter_case_id] = result.reserve_case_ids
        per_chapter_summary[chapter_case_id] = {
            "eligible_primary_count": result.eligible_primary_count,
            "eligible_reserve_count": result.eligible_reserve_count,
            "selected_primary_count": len(result.primary_rows),
            "selected_reserve_count": len(result.reserve_rows),
            "promoted_reserve_case_ids": [str(row["case_id"]) for row in result.promoted_reserve_rows],
            "overflow_primary_case_ids": [str(row["case_id"]) for row in result.overflow_primary_rows],
            "saturated_shortfall": result.saturated_shortfall,
        }

    excerpt_pressure_payload = grouped_case_ids_by_pressure(
        primary_rows_all,
        allowed_pressures=EXCERPT_PRESSURE_ORDER,
    )
    insight_rows_all = [
        row for row in primary_rows_all if str(row.get("target_profile_id", "")).strip() in INSIGHT_AND_CLARIFICATION_PROFILE_IDS
    ]
    insight_pressure_payload = grouped_case_ids_by_pressure(
        insight_rows_all,
        allowed_pressures=("distinction_definition", "tension_reversal", "callback_bridge"),
    )
    return {
        "quota_status": {
            "chapter_core": {
                "target_total": len(selected_chapter_case_ids),
                "ready_now": len(selected_chapter_case_ids),
                "gap": 0,
            },
            "excerpt_primary": {
                "target_total": excerpt_primary_target_total,
                "ready_now": len(primary_rows_all),
                "gap": max(excerpt_primary_target_total - len(primary_rows_all), 0),
            },
            "reserve": {
                "target_total": reserve_target_total,
                "ready_now": len(reserve_rows_all),
                "gap": max(reserve_target_total - len(reserve_rows_all), 0),
            },
        },
        "splits": {
            "chapter_core_frozen_draft": build_chapter_core_split(selected_chapter_case_ids),
            "excerpt_core_primary_frozen_draft": {
                "by_chapter": by_chapter_primary,
                "by_pressure": excerpt_pressure_payload,
                "all": [str(row["case_id"]) for row in primary_rows_all],
            },
            "insight_and_clarification_subset_frozen_draft": {
                "by_pressure": insight_pressure_payload,
                "all": [str(row["case_id"]) for row in insight_rows_all],
            },
            "reserve_target_draft": {
                "by_chapter": by_chapter_reserve,
                "all": [str(row["case_id"]) for row in reserve_rows_all],
            },
        },
        "chapter_freeze_summary": per_chapter_summary,
    }


def relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def update_active_manifest(
    active_manifest: Path,
    *,
    manifest_payload: dict[str, Any],
    freeze_summary_ref: str,
) -> None:
    active_payload = load_json(active_manifest)
    active_payload["quota_status"] = dict(manifest_payload["quota_status"])
    merged_splits = dict(active_payload.get("splits") or {})
    merged_splits.update(dict(manifest_payload["splits"]))
    active_payload["splits"] = merged_splits
    active_payload["freeze_summary_ref"] = freeze_summary_ref
    write_json(active_manifest, active_payload)


def read_dataset_rows(dataset_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_json(dataset_dir / "manifest.json")
    primary_file = str(manifest.get("primary_file", "")).strip()
    if not primary_file:
        raise ValueError(f"Dataset manifest missing primary_file: {dataset_dir / 'manifest.json'}")
    rows = with_source_order(load_jsonl(dataset_dir / primary_file))
    return manifest, rows


def clone_dataset_package(
    *,
    source_dir: Path,
    target_dir: Path,
    dataset_id: str,
    description: str,
    source_manifest_refs: list[str],
    split_refs: list[str],
    overwrite: bool,
) -> dict[str, Any]:
    manifest, rows = read_dataset_rows(source_dir)
    primary_file = str(manifest.get("primary_file", "")).strip()
    if target_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Target dataset already exists: {target_dir}")
        shutil.rmtree(target_dir)
    target_manifest = dict(manifest)
    target_manifest["dataset_id"] = dataset_id
    target_manifest["description"] = description
    target_manifest["derived_from_dataset_id"] = str(manifest.get("dataset_id", "")).strip()
    target_manifest["frozen_at"] = utc_now()
    target_manifest["source_manifest_refs"] = list(source_manifest_refs)
    target_manifest["split_refs"] = list(split_refs)
    cleaned_rows = [{key: value for key, value in row.items() if key != "_source_order"} for row in rows]
    write_json(target_dir / "manifest.json", target_manifest)
    write_jsonl(target_dir / primary_file, cleaned_rows)
    return target_manifest


def freeze_rows_for_output(
    rows: list[dict[str, Any]],
    *,
    source_dataset_id: str,
    frozen_at: str,
    split_role: str,
    chapter_case_id: str,
    freeze_order_offset: int,
) -> list[dict[str, Any]]:
    frozen_rows: list[dict[str, Any]] = []
    for offset, row in enumerate(rows):
        copied = {key: value for key, value in row.items() if key != "_source_order"}
        freeze_metadata = dict(copied.get("freeze_metadata") or {})
        freeze_metadata.update(
            {
                "frozen_from_dataset_id": source_dataset_id,
                "frozen_at": frozen_at,
                "benchmark_status_at_freeze": str(copied.get("benchmark_status", "")),
                "review_status_at_freeze": str(copied.get("review_status", "")),
                "freeze_role": split_role,
                "chapter_case_id": chapter_case_id,
                "freeze_order": freeze_order_offset + offset,
            }
        )
        copied["freeze_metadata"] = freeze_metadata
        copied["benchmark_freeze_role"] = split_role
        frozen_rows.append(copied)
    return frozen_rows


def freeze_excerpt_dataset(
    *,
    language_track: str,
    target_dataset_id: str,
    target_dir: Path,
    primary_source_dataset_ids: list[str],
    reserve_source_dataset_ids: list[str],
    chapter_case_ids: list[str],
    chapter_results: dict[str, ChapterFreezeResult],
    source_manifest_refs: list[str],
    split_refs: list[str],
    dataset_build_artifact_refs: list[str],
    overwrite: bool,
) -> dict[str, Any]:
    if target_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Target dataset already exists: {target_dir}")
        shutil.rmtree(target_dir)

    frozen_at = utc_now()
    frozen_rows: list[dict[str, Any]] = []
    for chapter_case_id in chapter_case_ids:
        chapter_result = chapter_results[chapter_case_id]
        frozen_rows.extend(
            freeze_rows_for_output(
                chapter_result.primary_rows,
                source_dataset_id=primary_source_dataset_ids[0],
                frozen_at=frozen_at,
                split_role="primary",
                chapter_case_id=chapter_case_id,
                freeze_order_offset=len(frozen_rows),
            )
        )
        frozen_rows.extend(
            freeze_rows_for_output(
                chapter_result.reserve_rows,
                source_dataset_id=reserve_source_dataset_ids[0],
                frozen_at=frozen_at,
                split_role="reserve",
                chapter_case_id=chapter_case_id,
                freeze_order_offset=len(frozen_rows),
            )
        )

    manifest = {
        **dataset_manifest(
            dataset_id=target_dataset_id,
            family="excerpt_cases",
            language_track=language_track,
            description=f"Frozen clustered benchmark v1 excerpt cases ({language_track}).",
            primary_file="cases.jsonl",
            source_manifest_refs=source_manifest_refs,
            split_refs=split_refs,
            storage_mode="local-only",
        ),
        "frozen_at": frozen_at,
        "derived_from_dataset_ids": primary_source_dataset_ids + reserve_source_dataset_ids,
        "dataset_build_artifact_refs": list(dataset_build_artifact_refs),
        "freeze_criteria": {
            "review_action": "keep",
            "blocking_problem_types": sorted(BLOCKING_PROBLEM_TYPES),
            "text_noise_requires_negligible_note": True,
            "primary_target_per_chapter": DEFAULT_PRIMARY_TARGET_PER_CHAPTER,
            "reserve_target_per_chapter": DEFAULT_RESERVE_TARGET_PER_CHAPTER,
        },
        "freeze_counts": {
            "row_count": len(frozen_rows),
            "primary_count": sum(1 for row in frozen_rows if row.get("benchmark_freeze_role") == "primary"),
            "reserve_count": sum(1 for row in frozen_rows if row.get("benchmark_freeze_role") == "reserve"),
        },
    }
    write_json(target_dir / "manifest.json", manifest)
    write_jsonl(target_dir / "cases.jsonl", frozen_rows)
    return manifest


def selected_chapter_case_ids_from_manifest(manifest_path: Path) -> list[str]:
    payload = load_json(manifest_path)
    clusters = payload.get("selected_chapter_clusters")
    if not isinstance(clusters, list):
        raise ValueError(f"Manifest missing selected_chapter_clusters: {manifest_path}")
    chapter_case_ids: list[str] = []
    for row in clusters:
        if not isinstance(row, dict):
            continue
        chapter_case_id = str(row.get("chapter_case_id", "")).strip()
        if chapter_case_id:
            chapter_case_ids.append(chapter_case_id)
    return chapter_case_ids


def build_parser() -> argparse.ArgumentParser:
    live_ids = live_build_ids(CLUSTERED_BENCHMARK_MODE)
    scratch_ids = namespaced_build_ids(DEFAULT_SMOKE2_RUN_ID, CLUSTERED_BENCHMARK_MODE)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--active-manifest", default="eval/manifests/splits/attentional_v2_clustered_benchmark_v1_draft.json")
    parser.add_argument("--run-id", default=DEFAULT_FREEZE_RUN_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--primary-dataset-id-en",
        default=scratch_ids.package_ids["excerpt_cases"]["en"],
    )
    parser.add_argument(
        "--primary-dataset-id-zh",
        default=scratch_ids.package_ids["excerpt_cases"]["zh"],
    )
    parser.add_argument(
        "--reserve-dataset-id-en",
        default=f"{live_ids.package_ids['excerpt_cases']['en']}__scratch__clustered_benchmark_v1_smoke2_reserves_20260404",
    )
    parser.add_argument(
        "--reserve-dataset-id-zh",
        default=f"{live_ids.package_ids['excerpt_cases']['zh']}__scratch__clustered_benchmark_v1_smoke2_reserves_20260404",
    )
    return parser


def dataset_root(family: str, dataset_id: str) -> Path:
    return STATE_LOCAL_DATASET_ROOT / family / dataset_id


def tracked_source_manifest_refs() -> list[str]:
    live_ids = live_build_ids(CLUSTERED_BENCHMARK_MODE)
    return [
        f"eval/manifests/source_books/{live_ids.source_manifest_file_stem}.json",
        f"eval/manifests/local_refs/{live_ids.local_refs_manifest_file_stem}.json",
        f"eval/manifests/corpora/{live_ids.corpus_manifest_file_stem}.json",
    ]


def tracked_split_refs(active_manifest: Path) -> list[str]:
    return [relative_to_root(active_manifest)]


def artifact_refs_for_language(language_track: str) -> list[str]:
    run_root = ROOT / "state" / "dataset_build" / "build_runs" / DEFAULT_SMOKE2_RUN_ID
    return [
        relative_to_root(
            run_root / "target_profiles" / "attentional_v2_clustered_benchmark_v1_excerpt_scope__scratch__clustered_benchmark_v1_smoke2_20260403.json"
        ),
        relative_to_root(
            run_root / "adequacy_reports" / "attentional_v2_clustered_benchmark_v1_excerpt_scope__scratch__clustered_benchmark_v1_smoke2_20260403.json"
        ),
        relative_to_root(
            run_root / "opportunity_maps" / f"attentional_v2_clustered_benchmark_v1_excerpt_{language_track}__scratch__clustered_benchmark_v1_smoke2_20260403.jsonl"
        ),
        relative_to_root(
            run_root / "candidate_cases" / f"attentional_v2_clustered_benchmark_v1_excerpt_{language_track}__scratch__clustered_benchmark_v1_smoke2_20260403.jsonl"
        ),
        relative_to_root(
            run_root / "reserve_cases" / f"attentional_v2_clustered_benchmark_v1_excerpt_{language_track}__scratch__clustered_benchmark_v1_smoke2_20260403.jsonl"
        ),
    ]


def write_summary_files(run_id: str, payload: dict[str, Any]) -> tuple[str, str]:
    run_root = ROOT / "state" / "dataset_build" / "build_runs" / run_id
    json_path = run_root / "clustered_benchmark_v1_freeze_summary.json"
    md_path = run_root / "clustered_benchmark_v1_freeze_summary.md"
    write_json(json_path, payload)
    lines = [
        "# Clustered Benchmark V1 Freeze Summary",
        "",
        f"- Frozen at: `{payload['frozen_at']}`",
        f"- Primary ready: `{payload['quota_status']['excerpt_primary']['ready_now']}` / `{payload['quota_status']['excerpt_primary']['target_total']}`",
        f"- Reserve ready: `{payload['quota_status']['reserve']['ready_now']}` / `{payload['quota_status']['reserve']['target_total']}`",
        "",
        "## Chapter Results",
    ]
    for chapter_case_id, summary in payload["chapter_freeze_summary"].items():
        lines.extend(
            [
                f"- `{chapter_case_id}`",
                f"  - selected_primary_count: `{summary['selected_primary_count']}`",
                f"  - selected_reserve_count: `{summary['selected_reserve_count']}`",
                f"  - promoted_reserve_case_ids: `{', '.join(summary['promoted_reserve_case_ids']) or 'none'}`",
                f"  - saturated_shortfall: `{summary['saturated_shortfall']}`",
            ]
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return relative_to_root(json_path), relative_to_root(md_path)


def main() -> int:
    args = build_parser().parse_args()
    active_manifest = (ROOT / args.active_manifest).resolve()
    selected_chapter_case_ids = selected_chapter_case_ids_from_manifest(active_manifest)

    primary_dataset_ids = {
        "en": args.primary_dataset_id_en,
        "zh": args.primary_dataset_id_zh,
    }
    reserve_dataset_ids = {
        "en": args.reserve_dataset_id_en,
        "zh": args.reserve_dataset_id_zh,
    }
    primary_rows_by_language: dict[str, list[dict[str, Any]]] = {}
    reserve_rows_by_language: dict[str, list[dict[str, Any]]] = {}
    for language_track in ("en", "zh"):
        _primary_manifest, primary_rows_by_language[language_track] = read_dataset_rows(
            dataset_root("excerpt_cases", primary_dataset_ids[language_track])
        )
        _reserve_manifest, reserve_rows_by_language[language_track] = read_dataset_rows(
            dataset_root("excerpt_cases", reserve_dataset_ids[language_track])
        )

    chapter_results: dict[str, ChapterFreezeResult] = {}
    for chapter_case_id in selected_chapter_case_ids:
        language_track = language_track_for_chapter_case_id(chapter_case_id)
        chapter_primary_rows = [
            row for row in primary_rows_by_language[language_track] if chapter_case_id_for_row(row) == chapter_case_id
        ]
        chapter_reserve_rows = [
            row for row in reserve_rows_by_language[language_track] if chapter_case_id_for_row(row) == chapter_case_id
        ]
        chapter_results[chapter_case_id] = freeze_one_chapter(
            chapter_case_id=chapter_case_id,
            primary_rows=chapter_primary_rows,
            reserve_rows=chapter_reserve_rows,
            primary_target=DEFAULT_PRIMARY_TARGET_PER_CHAPTER,
            reserve_target=DEFAULT_RESERVE_TARGET_PER_CHAPTER,
        )

    manifest_payload = build_freeze_manifest_payload(
        selected_chapter_case_ids=selected_chapter_case_ids,
        chapter_results=chapter_results,
        excerpt_primary_target_total=len(selected_chapter_case_ids) * DEFAULT_PRIMARY_TARGET_PER_CHAPTER,
        reserve_target_total=len(selected_chapter_case_ids) * DEFAULT_RESERVE_TARGET_PER_CHAPTER,
    )

    live_ids = live_build_ids(CLUSTERED_BENCHMARK_MODE)
    scratch_ids = namespaced_build_ids(DEFAULT_SMOKE2_RUN_ID, CLUSTERED_BENCHMARK_MODE)
    source_manifest_refs = tracked_source_manifest_refs()
    split_refs = tracked_split_refs(active_manifest)

    # Freeze the excerpt datasets that the active benchmark manifest points at.
    freeze_excerpt_dataset(
        language_track="en",
        target_dataset_id=live_ids.package_ids["excerpt_cases"]["en"],
        target_dir=dataset_root("excerpt_cases", live_ids.package_ids["excerpt_cases"]["en"]),
        primary_source_dataset_ids=[primary_dataset_ids["en"]],
        reserve_source_dataset_ids=[reserve_dataset_ids["en"]],
        chapter_case_ids=[chapter for chapter in selected_chapter_case_ids if language_track_for_chapter_case_id(chapter) == "en"],
        chapter_results=chapter_results,
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        dataset_build_artifact_refs=artifact_refs_for_language("en"),
        overwrite=args.overwrite,
    )
    freeze_excerpt_dataset(
        language_track="zh",
        target_dataset_id=live_ids.package_ids["excerpt_cases"]["zh"],
        target_dir=dataset_root("excerpt_cases", live_ids.package_ids["excerpt_cases"]["zh"]),
        primary_source_dataset_ids=[primary_dataset_ids["zh"]],
        reserve_source_dataset_ids=[reserve_dataset_ids["zh"]],
        chapter_case_ids=[chapter for chapter in selected_chapter_case_ids if language_track_for_chapter_case_id(chapter) == "zh"],
        chapter_results=chapter_results,
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        dataset_build_artifact_refs=artifact_refs_for_language("zh"),
        overwrite=args.overwrite,
    )

    # Clone non-excerpt local benchmark packages from the completed smoke2 build.
    clone_dataset_package(
        source_dir=dataset_root("chapter_corpora", scratch_ids.package_ids["chapter_corpora"]["en"]),
        target_dir=dataset_root("chapter_corpora", live_ids.package_ids["chapter_corpora"]["en"]),
        dataset_id=live_ids.package_ids["chapter_corpora"]["en"],
        description="Frozen clustered benchmark v1 chapter core package (en).",
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        overwrite=args.overwrite,
    )
    clone_dataset_package(
        source_dir=dataset_root("chapter_corpora", scratch_ids.package_ids["chapter_corpora"]["zh"]),
        target_dir=dataset_root("chapter_corpora", live_ids.package_ids["chapter_corpora"]["zh"]),
        dataset_id=live_ids.package_ids["chapter_corpora"]["zh"],
        description="Frozen clustered benchmark v1 chapter core package (zh).",
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        overwrite=args.overwrite,
    )
    clone_dataset_package(
        source_dir=dataset_root("runtime_fixtures", scratch_ids.package_ids["runtime_fixtures"]["en"]),
        target_dir=dataset_root("runtime_fixtures", live_ids.package_ids["runtime_fixtures"]["en"]),
        dataset_id=live_ids.package_ids["runtime_fixtures"]["en"],
        description="Frozen clustered benchmark v1 runtime fixture package (en).",
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        overwrite=args.overwrite,
    )
    clone_dataset_package(
        source_dir=dataset_root("runtime_fixtures", scratch_ids.package_ids["runtime_fixtures"]["zh"]),
        target_dir=dataset_root("runtime_fixtures", live_ids.package_ids["runtime_fixtures"]["zh"]),
        dataset_id=live_ids.package_ids["runtime_fixtures"]["zh"],
        description="Frozen clustered benchmark v1 runtime fixture package (zh).",
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        overwrite=args.overwrite,
    )
    clone_dataset_package(
        source_dir=dataset_root("compatibility_fixtures", scratch_ids.package_ids["compatibility_fixtures"]["shared"]),
        target_dir=dataset_root("compatibility_fixtures", live_ids.package_ids["compatibility_fixtures"]["shared"]),
        dataset_id=live_ids.package_ids["compatibility_fixtures"]["shared"],
        description="Frozen clustered benchmark v1 compatibility fixture package.",
        source_manifest_refs=source_manifest_refs,
        split_refs=split_refs,
        overwrite=args.overwrite,
    )

    frozen_at = utc_now()
    summary_payload = {
        "run_id": args.run_id,
        "frozen_at": frozen_at,
        "active_manifest": relative_to_root(active_manifest),
        "source_dataset_ids": {
            "primary": primary_dataset_ids,
            "reserve": reserve_dataset_ids,
        },
        "target_dataset_ids": live_ids.package_ids,
        **manifest_payload,
    }
    summary_json_ref, summary_md_ref = write_summary_files(args.run_id, summary_payload)
    summary_payload["summary_refs"] = {
        "json": summary_json_ref,
        "md": summary_md_ref,
    }
    write_json(ROOT / summary_json_ref, summary_payload)
    update_active_manifest(
        active_manifest,
        manifest_payload=manifest_payload,
        freeze_summary_ref=summary_json_ref,
    )
    print(json.dumps(summary_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
