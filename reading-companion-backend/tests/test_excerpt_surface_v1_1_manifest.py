"""Validate the composed excerpt surface v1.1 draft manifest."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import excerpt_surface_v1_1 as module


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / "attentional_v2_excerpt_surface_v1_1_draft.json"


def _load_cases(dataset_dir: Path) -> list[dict[str, object]]:
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    primary_file = dataset_dir / str(manifest["primary_file"])
    return [
        json.loads(line)
        for line in primary_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_selected_rows_by_chapter_dedupes_same_span_reuse(monkeypatch) -> None:
    chapter_case_id = "value_of_others_private_en__8"
    monkeypatch.setattr(module, "FIXED_CHAPTER_CASE_IDS", (chapter_case_id,))

    shared = {
        "source_id": "value_of_others_private_en",
        "chapter_id": "8",
        "chapter_number": 8,
        "target_profile_id": "distinction_definition",
        "benchmark_status": "reviewed_active",
        "review_status": "llm_reviewed",
        "construction_priority": 7.0,
        "judgeability_score": 5.0,
        "excerpt_sentence_ids": ["c8-s43", "c8-s44", "c8-s45"],
        "anchor_sentence_id": "c8-s44",
        "start_sentence_id": "c8-s43",
        "end_sentence_id": "c8-s45",
    }
    rows = [
        {
            **shared,
            "case_id": "value_of_others_private_en__8__distinction_definition__seed_1",
            "_chapter_case_id": chapter_case_id,
            "_origin_line": "human_notes_guided_dataset_v1",
            "_source_dataset_id": "notes_freeze",
            "_source_dataset_dir": "state/eval_local_datasets/excerpt_cases/notes_freeze",
            "selection_group_kind": "notes_guided_cluster",
        },
        {
            **shared,
            "case_id": "value_of_others_private_en__8__distinction_definition__seed_4",
            "_chapter_case_id": chapter_case_id,
            "_origin_line": "human_notes_guided_dataset_v1",
            "_source_dataset_id": "notes_freeze",
            "_source_dataset_dir": "state/eval_local_datasets/excerpt_cases/notes_freeze",
            "selection_group_kind": "notes_guided_cluster",
        },
        {
            **shared,
            "case_id": "value_of_others_private_en__8__tension_reversal__seed_1",
            "target_profile_id": "tension_reversal",
            "excerpt_sentence_ids": ["c8-s201", "c8-s202", "c8-s203"],
            "anchor_sentence_id": "c8-s202",
            "start_sentence_id": "c8-s201",
            "end_sentence_id": "c8-s203",
            "_chapter_case_id": chapter_case_id,
            "_origin_line": "human_notes_guided_dataset_v1",
            "_source_dataset_id": "notes_freeze",
            "_source_dataset_dir": "state/eval_local_datasets/excerpt_cases/notes_freeze",
            "selection_group_kind": "notes_guided_cluster",
        },
    ]

    selected_rows, dropped_case_ids = module._selected_rows_by_chapter(rows)

    assert [row["case_id"] for row in selected_rows[chapter_case_id]] == [
        "value_of_others_private_en__8__distinction_definition__seed_1",
        "value_of_others_private_en__8__tension_reversal__seed_1",
    ]
    assert dropped_case_ids[chapter_case_id] == [
        "value_of_others_private_en__8__distinction_definition__seed_4",
    ]


def test_read_source_dataset_skips_non_reviewed_fill_rows(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "fill_dataset"
    module.write_json(
        dataset_dir / "manifest.json",
        {
            "dataset_id": "fill_dataset",
            "primary_file": "cases.jsonl",
            "source_manifest_refs": [],
        },
    )
    module.write_jsonl(
        dataset_dir / "cases.jsonl",
        [
            {
                "case_id": "nawaer_baodian_private_zh__22__anchored_reaction_selectivity__fill_1",
                "source_id": "nawaer_baodian_private_zh",
                "chapter_id": "22",
                "output_language": "zh",
                "target_profile_id": "anchored_reaction_selectivity",
                "benchmark_status": "needs_revision",
                "review_status": "llm_reviewed",
            }
        ],
    )

    _manifest, rows = module._read_source_dataset(
        dataset_dir,
        origin_line="excerpt_surface_v1_1_fill",
        dataset_family="excerpt_surface_fill_reviewed",
    )

    assert rows == []


def test_excerpt_surface_v1_1_manifest_matches_composed_dataset_counts() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset_dirs = [
        (ROOT / Path(path)).resolve()
        for path in payload["source_refs"]["excerpt_case_datasets"]
    ]
    rows: list[dict[str, object]] = []
    for dataset_dir in dataset_dirs:
        rows.extend(_load_cases(dataset_dir))

    all_ids = [str(row["case_id"]) for row in rows]
    by_chapter = payload["splits"]["excerpt_core_primary_frozen_draft"]["by_chapter"]
    chapter_case_ids = [str(item["chapter_case_id"]) for item in payload["selected_chapter_units"]]

    assert chapter_case_ids == list(module.FIXED_CHAPTER_CASE_IDS)
    assert not any(chapter_case_id in by_chapter for chapter_case_id in module.DROPPED_CHAPTER_CASE_IDS)
    assert len(payload["selected_chapter_units"]) == 7
    assert len(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"]) == len(all_ids)
    assert len(set(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"])) == len(all_ids)
    assert set(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"]) == set(all_ids)
    assert module.PRIMARY_TARGET_RANGE["min"] <= len(all_ids) <= module.PRIMARY_TARGET_RANGE["max"]
    assert len(by_chapter["value_of_others_private_en__8"]) == 8


def test_excerpt_surface_v1_1_manifest_derives_insight_subset_by_profile() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    dataset_dirs = [
        (ROOT / Path(path)).resolve()
        for path in payload["source_refs"]["excerpt_case_datasets"]
    ]
    rows: list[dict[str, object]] = []
    for dataset_dir in dataset_dirs:
        rows.extend(_load_cases(dataset_dir))

    subset_ids = [
        str(row["case_id"])
        for row in rows
        if str(row.get("target_profile_id", "")) in module.INSIGHT_TARGET_PROFILE_IDS
    ]
    manifest_subset_ids = payload["splits"]["insight_and_clarification_subset_frozen_draft"]["all"]

    assert len(set(manifest_subset_ids)) == len(manifest_subset_ids)
    assert set(manifest_subset_ids) == set(subset_ids)
    assert set(manifest_subset_ids).issubset(set(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"]))
