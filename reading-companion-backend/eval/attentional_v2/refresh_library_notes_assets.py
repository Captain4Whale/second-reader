#!/usr/bin/env python3
"""Refresh parsing + alignment for already-registered managed notes assets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.attentional_v2.library_notes import (  # noqa: E402
    LibraryNotesPaths,
    load_notes_catalog,
    refresh_registered_notes_asset,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Backend root that owns state/library_notes.")
    parser.add_argument(
        "--source-catalog",
        default="",
        help="Optional source catalog path. Defaults to state/dataset_build/source_catalog.json under --root.",
    )
    parser.add_argument(
        "--notes-id",
        action="append",
        default=[],
        help="Specific managed notes asset id to refresh. Repeatable.",
    )
    parser.add_argument(
        "--linked-source-id",
        action="append",
        default=[],
        help="Refresh every managed notes asset linked to this source id. Repeatable.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Refresh all registered managed notes assets.",
    )
    return parser


def _selected_notes_ids(*, paths: LibraryNotesPaths, notes_ids: list[str], linked_source_ids: list[str], refresh_all: bool) -> list[str]:
    catalog = load_notes_catalog(paths.notes_catalog_json_path)
    assets = [item for item in catalog.get("assets", []) if isinstance(item, dict)]
    selected = {str(item).strip() for item in notes_ids if str(item).strip()}
    wanted_sources = {str(item).strip() for item in linked_source_ids if str(item).strip()}
    if refresh_all or wanted_sources:
        for asset in assets:
            notes_id = str(asset.get("notes_id") or "").strip()
            linked_source_id = str(asset.get("linked_source_id") or "").strip()
            if refresh_all or linked_source_id in wanted_sources:
                if notes_id:
                    selected.add(notes_id)
    return sorted(selected)


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).expanduser().resolve()
    paths = LibraryNotesPaths.from_root(root)
    source_catalog_path = (
        Path(args.source_catalog).expanduser().resolve()
        if str(args.source_catalog).strip()
        else root / "state" / "dataset_build" / "source_catalog.json"
    )
    selected_notes_ids = _selected_notes_ids(
        paths=paths,
        notes_ids=list(args.notes_id),
        linked_source_ids=list(args.linked_source_id),
        refresh_all=bool(args.all),
    )
    if not selected_notes_ids:
        raise SystemExit("No managed notes assets selected. Use --notes-id, --linked-source-id, or --all.")

    results = []
    for notes_id in selected_notes_ids:
        refreshed = refresh_registered_notes_asset(
            paths,
            notes_id=notes_id,
            source_catalog_path=source_catalog_path,
        )
        asset = refreshed["asset"]
        refresh_summary = refreshed["refresh_summary"]
        results.append(
            {
                "notes_id": asset["notes_id"],
                "linked_source_id": asset["linked_source_id"],
                "aligned_entry_count": asset["aligned_entry_count"],
                "unresolved_entry_count": asset["unresolved_entry_count"],
                "entry_count": asset["entry_count"],
                "changed_entry_count": refresh_summary["changed_entry_count"],
                "changed_entries": refresh_summary["changed_entries"],
            }
        )

    payload = {
        "refreshed_asset_count": len(results),
        "results": results,
        "notes_catalog_json": str(paths.notes_catalog_json_path),
        "notes_catalog_md": str(paths.notes_catalog_md_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
