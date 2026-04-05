"""Validate the ROI-first excerpt micro-slice v1 draft manifest."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2 import excerpt_micro_slice_v1 as module


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / "attentional_v2_excerpt_micro_slice_v1_draft.json"
SOURCE_MANIFEST_PATH = ROOT / "eval" / "manifests" / "splits" / "attentional_v2_human_notes_guided_excerpt_eval_v1_draft.json"


def test_excerpt_micro_slice_manifest_matches_selected_source_rows() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_payload = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))

    selected_ids = payload["splits"]["excerpt_core_primary_frozen_draft"]["all"]
    expected_ids = [
        case_id
        for chapter_case_id in module.SELECTED_CHAPTER_CASE_IDS
        for case_id in source_payload["splits"]["excerpt_core_primary_frozen_draft"]["by_chapter"][chapter_case_id]
    ]

    assert payload["manifest_id"] == module.MANIFEST_ID
    assert [item["chapter_case_id"] for item in payload["selected_chapter_units"]] == list(module.SELECTED_CHAPTER_CASE_IDS)
    assert selected_ids == expected_ids
    assert len(selected_ids) == 13
    assert payload["quota_status"]["excerpt_primary"]["ready_now"] == 13


def test_excerpt_micro_slice_manifest_derives_insight_subset_from_source_subset() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_payload = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))

    selected_case_ids = set(payload["splits"]["excerpt_core_primary_frozen_draft"]["all"])
    expected_subset = [
        case_id
        for case_id in source_payload["splits"]["insight_and_clarification_subset_frozen_draft"]["all"]
        if case_id in selected_case_ids
    ]

    subset_ids = payload["splits"]["insight_and_clarification_subset_frozen_draft"]["all"]

    assert subset_ids == expected_subset
    assert len(subset_ids) == 8
    assert set(subset_ids).issubset(selected_case_ids)
    assert payload["quota_status"]["insight_and_clarification_subset"]["ready_now"] == 8


def test_excerpt_micro_slice_manifest_keeps_source_refs_and_expansion_candidate() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_payload = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert payload["source_refs"] == source_payload["source_refs"]
    assert payload["expansion_candidate_chapter_units"] == list(module.EXPANSION_CANDIDATE_CHAPTER_CASE_IDS)
    assert payload["benchmark_shape"]["surface_role"] == "excerpt_surface_micro_harness"
