"""Tests for the managed-catalog private-library supplement wiring."""

from __future__ import annotations

import json
from pathlib import Path

from eval.attentional_v2.build_private_library_supplement import (
    build_private_library_splits,
    load_private_library_source_items,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def test_load_private_library_source_items_uses_catalog_paths_and_manifest_fallbacks(tmp_path: Path) -> None:
    root = tmp_path
    source_path = root / "state" / "library_sources" / "en" / "private" / "fooled_by_randomness.epub"
    _write(source_path, "demo")

    catalog_path = root / "state" / "dataset_build" / "source_catalog.json"
    _write_json(
        catalog_path,
        {
            "records": [
                {
                    "source_id": "fooled_by_randomness_private_en",
                    "title": "Fooled by Randomness",
                    "author": "Nassim Nicholas Taleb",
                    "language": "en",
                    "visibility": "private",
                    "origin": "manual_library_inbox",
                    "relative_local_path": "state/library_sources/en/private/fooled_by_randomness.epub",
                    "original_filename": "Fooled by Randomness.epub",
                    "selection_priority": 9999,
                    "type_tags": [],
                    "role_tags": [],
                    "notes": [],
                    "ingest_batch_ids": ["catalog_batch_a"],
                    "acquisition": {
                        "kind": "manual_library_inbox",
                        "ingest_batch_id": "catalog_batch_a",
                    },
                }
            ]
        },
    )

    tracked_manifest_path = root / "eval" / "manifests" / "source_books" / "attentional_v2_private_library_screen_v2.json"
    _write_json(
        tracked_manifest_path,
        {
            "books": [
                {
                    "source_id": "fooled_by_randomness_private_en",
                    "selection_priority": 6,
                    "type_tags": ["psychology_decision", "modern_nonfiction"],
                    "role_tags": ["argumentative", "reference_heavy"],
                    "notes": ["Legacy private source retained."],
                    "acquisition_batch_id": "legacy_private_downloads_v1",
                }
            ]
        },
    )

    items = load_private_library_source_items(
        root=root,
        catalog_path=catalog_path,
        tracked_manifest_path=tracked_manifest_path,
    )

    assert len(items) == 1
    item = items[0]
    spec = item["spec"]
    assert spec.source_id == "fooled_by_randomness_private_en"
    assert spec.promoted_local_path == "en/private/fooled_by_randomness.epub"
    assert spec.selection_priority == 6
    assert spec.type_tags == ["psychology_decision", "modern_nonfiction"]
    assert spec.role_tags == ["argumentative", "reference_heavy"]
    assert spec.notes == ["Legacy private source retained."]
    assert item["source_path"] == source_path
    assert item["acquisition_batch_id"] == "legacy_private_downloads_v1"


def test_load_private_library_source_items_prefers_explicit_catalog_metadata_and_filters_non_private(tmp_path: Path) -> None:
    root = tmp_path
    private_source = root / "state" / "library_sources" / "zh" / "private" / "case_a.epub"
    public_source = root / "state" / "library_sources" / "en" / "case_b.epub"
    _write(private_source, "a")
    _write(public_source, "b")

    catalog_path = root / "state" / "dataset_build" / "source_catalog.json"
    _write_json(
        catalog_path,
        {
            "records": [
                {
                    "source_id": "case_a_private_zh",
                    "title": "案例A",
                    "author": "作者A",
                    "language": "zh",
                    "visibility": "private",
                    "origin": "manual_library_inbox",
                    "relative_local_path": "state/library_sources/zh/private/case_a.epub",
                    "selection_priority": 3,
                    "type_tags": ["history"],
                    "role_tags": ["argumentative"],
                    "notes": ["Catalog metadata wins."],
                    "original_filename": "case_a.epub",
                },
                {
                    "source_id": "case_b_public_en",
                    "title": "Case B",
                    "author": "Author B",
                    "language": "en",
                    "visibility": "public",
                    "origin": "manual_library_inbox",
                    "relative_local_path": "state/library_sources/en/case_b.epub",
                    "selection_priority": 1,
                    "type_tags": ["business"],
                    "role_tags": ["expository"],
                    "notes": ["Should be ignored by the private-library builder."],
                    "original_filename": "case_b.epub",
                },
            ]
        },
    )

    items = load_private_library_source_items(root=root, catalog_path=catalog_path, tracked_manifest_path=root / "missing.json")

    assert len(items) == 1
    spec = items[0]["spec"]
    assert spec.source_id == "case_a_private_zh"
    assert spec.selection_priority == 3
    assert spec.type_tags == ["history"]
    assert spec.role_tags == ["argumentative"]
    assert spec.notes == ["Catalog metadata wins."]


def test_build_private_library_splits_adds_dynamic_batch_groups() -> None:
    source_records = [
        {
            "source_id": "legacy_en",
            "language": "en",
            "corpus_lane": "chapter_corpus_eligible",
            "acquisition_batch_id": "legacy_private_downloads_v1",
        },
        {
            "source_id": "new_zh",
            "language": "zh",
            "corpus_lane": "excerpt_only",
            "acquisition_batch_id": "batch_20260330",
        },
        {
            "source_id": "reject_en",
            "language": "en",
            "corpus_lane": "reject",
            "acquisition_batch_id": "",
        },
    ]

    splits = build_private_library_splits(source_records)

    assert splits["all_private_library_sources"] == {
        "en": ["legacy_en", "reject_en"],
        "zh": ["new_zh"],
    }
    assert splits["chapter_corpus_eligible"]["en"] == ["legacy_en"]
    assert splits["excerpt_only"]["zh"] == ["new_zh"]
    assert splits["reject_this_pass"]["en"] == ["reject_en"]
    assert splits["legacy_private_downloads_v1"]["en"] == ["legacy_en"]
    assert splits["batch_20260330"]["zh"] == ["new_zh"]
