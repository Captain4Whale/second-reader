#!/usr/bin/env python3
"""Backfill frontend-facing artifacts for legacy output directories."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.iterator_reader.frontend_artifacts import (  # noqa: E402
    append_activity_event,
    build_run_state,
    build_chapter_qa_artifact,
    reset_activity,
    write_book_manifest,
    write_run_state,
)
from src.iterator_reader.parse import _extract_epub_cover, hydrate_legacy_epub_locators  # noqa: E402
from src.iterator_reader.storage import (  # noqa: E402
    activity_file,
    analysis_dir,
    book_manifest_file,
    book_analysis_file,
    chapter_markdown_file,
    chapter_qa_file,
    chapter_result_file,
    chapter_reference,
    ensure_source_asset,
    existing_activity_file,
    existing_book_manifest_file,
    existing_structure_file,
    internal_diagnostics_dir,
    legacy_activity_file,
    legacy_analysis_dir,
    legacy_book_analysis_file,
    legacy_book_manifest_file,
    legacy_chapter_markdown_file,
    legacy_chapter_result_file,
    legacy_plan_state_file,
    legacy_run_state_file,
    legacy_segment_checkpoint_dir,
    plan_state_file,
    run_state_file,
    save_json,
    structure_file,
    structure_markdown_file,
    segment_checkpoint_dir,
)


def _load_structure(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _move_path(source: Path, destination: Path) -> bool:
    """Move one legacy file or directory into its canonical location."""
    if not source.exists():
        return False
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.rename(destination)
    return True


def _copytree_if_missing(source: Path, destination: Path) -> bool:
    """Copy a legacy directory into its canonical location when missing."""
    if not source.exists() or destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return True


def _clean_public_reactions(payload: dict, structure: dict, output_dir: Path) -> tuple[bool, dict[str, dict]]:
    """Strip non-user-visible reactions and capture internal QA sidecars."""
    changed = False
    qa_sidecars: dict[str, dict] = {}
    chapters_by_id = {
        int(chapter.get("id", 0)): chapter
        for chapter in structure.get("chapters", [])
        if isinstance(chapter, dict)
    }

    for chapter in structure.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        result_path = chapter_result_file(output_dir, chapter)
        if not result_path.exists():
            legacy_path = legacy_chapter_result_file(output_dir, chapter)
            if not legacy_path.exists():
                continue
            payload = json.loads(legacy_path.read_text(encoding="utf-8"))
        else:
            payload = json.loads(result_path.read_text(encoding="utf-8"))

        chapter_reflection = payload.get("chapter_reflection", {})
        qa_payload = build_chapter_qa_artifact(
            chapter=chapter,
            chapter_reflection=chapter_reflection if isinstance(chapter_reflection, dict) else {},
            output_language=str(payload.get("output_language", structure.get("output_language", "en"))),
        )

        removed_reaction_ids: set[str] = set()
        chapter_changed = False
        for section in payload.get("sections", []):
            if not isinstance(section, dict):
                continue
            reactions = []
            for reaction in section.get("reactions", []):
                if not isinstance(reaction, dict):
                    continue
                anchor_quote = str(reaction.get("anchor_quote", "") or "").strip()
                content = str(reaction.get("content", "") or "").strip()
                if content.startswith("Chapter-end addendum:") or content.startswith("章末回看补记："):
                    removed_reaction_ids.add(str(reaction.get("reaction_id", "")))
                    chapter_changed = True
                    continue
                if str(reaction.get("type", "")) != "silent" and not anchor_quote:
                    removed_reaction_ids.add(str(reaction.get("reaction_id", "")))
                    chapter_changed = True
                    continue
                reactions.append(reaction)
            if section.get("reactions") != reactions:
                section["reactions"] = reactions
                chapter_changed = True

        if removed_reaction_ids:
            featured = [
                item
                for item in payload.get("featured_reactions", [])
                if isinstance(item, dict) and str(item.get("reaction_id", "")) not in removed_reaction_ids
            ]
            if payload.get("featured_reactions") != featured:
                payload["featured_reactions"] = featured
                chapter_changed = True

        reaction_counts: dict[str, int] = {}
        visible_count = 0
        kept_section_count = 0
        skipped_section_count = 0
        for section in payload.get("sections", []):
            if not isinstance(section, dict):
                continue
            if str(section.get("verdict", "")) == "skip":
                skipped_section_count += 1
            else:
                kept_section_count += 1
            for reaction in section.get("reactions", []):
                if not isinstance(reaction, dict):
                    continue
                reaction_type = str(reaction.get("type", "") or "")
                reaction_counts[reaction_type] = reaction_counts.get(reaction_type, 0) + 1
                visible_count += 1

        if payload.get("chapter_reflection") != {}:
            payload["chapter_reflection"] = {}
            chapter_changed = True
        if payload.get("visible_reaction_count") != visible_count:
            payload["visible_reaction_count"] = visible_count
            chapter_changed = True
        if payload.get("reaction_type_diversity") != len(reaction_counts):
            payload["reaction_type_diversity"] = len(reaction_counts)
            chapter_changed = True
        if "high_signal_reaction_count" in payload:
            payload.pop("high_signal_reaction_count", None)
            chapter_changed = True
        ui_summary = {
            "kept_section_count": kept_section_count,
            "skipped_section_count": skipped_section_count,
            "reaction_counts": dict(sorted(reaction_counts.items())),
        }
        if payload.get("ui_summary") != ui_summary:
            payload["ui_summary"] = ui_summary
            chapter_changed = True

        if chapter_changed:
            save_json(result_path, payload)
            changed = True
        if any(qa_payload.get(key) for key in ("chapter_insights", "segment_quality_flags", "segment_repairs", "reaction_repairs")):
            save_json(chapter_qa_file(output_dir, chapter), qa_payload)
            qa_sidecars[str(chapter.get("id", ""))] = qa_payload

    return changed, qa_sidecars


def _migrate_layout(output_dir: Path, structure: dict) -> list[str]:
    """Move legacy flat artifacts into the canonical directory layout."""
    changes: list[str] = []
    if _move_path(legacy_book_manifest_file(output_dir), book_manifest_file(output_dir)):
        changes.append("manifest_layout")
    if _move_path(legacy_run_state_file(output_dir), run_state_file(output_dir)):
        changes.append("run_state_layout")
    if _move_path(legacy_activity_file(output_dir), activity_file(output_dir)):
        changes.append("activity_layout")
    if _move_path(legacy_plan_state_file(output_dir), plan_state_file(output_dir)):
        changes.append("plan_state_layout")
    if _move_path(legacy_book_analysis_file(output_dir), book_analysis_file(output_dir)):
        changes.append("book_analysis_layout")
    if _copytree_if_missing(legacy_analysis_dir(output_dir), analysis_dir(output_dir)):
        changes.append("analysis_layout")
    if _copytree_if_missing(legacy_segment_checkpoint_dir(output_dir), segment_checkpoint_dir(output_dir)):
        changes.append("checkpoint_layout")
    for chapter in structure.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        if _move_path(legacy_chapter_markdown_file(output_dir, chapter), chapter_markdown_file(output_dir, chapter)):
            changes.append(f'chapter_markdown:{chapter.get("id", "")}')
        if _move_path(legacy_chapter_result_file(output_dir, chapter), chapter_result_file(output_dir, chapter)):
            changes.append(f'chapter_result:{chapter.get("id", "")}')
    return changes


def _infer_run_state(structure: dict) -> dict:
    chapters = list(structure.get("chapters", []))
    total = len(chapters)
    completed = sum(1 for chapter in chapters if str(chapter.get("status", "")).strip() == "done")
    current = next((chapter for chapter in chapters if str(chapter.get("status", "")).strip() == "in_progress"), None)
    if current is None and 0 < completed < total:
        current = next((chapter for chapter in chapters if str(chapter.get("status", "")).strip() != "done"), None)

    if total > 0 and completed == total:
        stage = "completed"
    elif current is not None:
        stage = "deep_reading"
    else:
        stage = "ready"

    return build_run_state(
        structure,
        stage=stage,
        total_chapters=total,
        completed_chapters=completed,
        current_chapter_id=(int(current.get("id", 0)) if current is not None else None),
        current_chapter_ref=(chapter_reference(current) if current is not None else None),
    )


def _ensure_assets(output_dir: Path, structure: dict) -> list[str]:
    changes: list[str] = []
    source_file = str(structure.get("source_file", "") or "").strip()
    if not source_file:
        return changes

    source_path = Path(source_file)
    if not source_path.exists():
        return changes

    asset_path = ensure_source_asset(source_path, output_dir)
    if asset_path.exists():
        changes.append("source_asset")

    if source_path.suffix.lower() == ".epub":
        cover_path = _extract_epub_cover(source_path, output_dir)
        if cover_path is not None and cover_path.exists():
            changes.append("cover_asset")
        changes.extend(hydrate_legacy_epub_locators(output_dir, structure, source_path))

    return changes


def backfill_output_dir(output_dir: Path) -> list[str]:
    changes: list[str] = []
    structure_path = existing_structure_file(output_dir)
    if not structure_path.exists():
        return changes

    structure = _load_structure(structure_path)
    if structure_path != structure_file(output_dir):
        save_json(structure_file(output_dir), structure)
        changes.append("structure_layout")

    changes.extend(_migrate_layout(output_dir, structure))
    changes.extend(_ensure_assets(output_dir, structure))
    public_cleaned, qa_sidecars = _clean_public_reactions({}, structure, output_dir)
    if public_cleaned:
        changes.append("public_cleanup")
    if qa_sidecars:
        changes.append("qa_sidecars")

    manifest_path = book_manifest_file(output_dir)
    if not manifest_path.exists():
        write_book_manifest(output_dir, structure)
        changes.append("book_manifest")

    state_path = run_state_file(output_dir)
    if not state_path.exists():
        write_run_state(output_dir, _infer_run_state(structure))
        changes.append("run_state")

    stream_path = activity_file(output_dir)
    if not stream_path.exists():
        reset_activity(output_dir)
        append_activity_event(
            output_dir,
            {
                "type": "structure_ready",
                "message": "Legacy artifacts were backfilled for workspace runtime compatibility.",
            },
        )
        changes.append("activity")

    diagnostics_dir = internal_diagnostics_dir(output_dir)
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        diagnostics_dir / "locator_backfill.json",
        {
            "updated_at": _infer_run_state(structure).get("updated_at"),
            "changes": changes,
            "qa_sidecar_count": len(qa_sidecars),
        },
    )

    return changes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill legacy frontend-facing output artifacts.")
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Backend runtime root that contains output/ and state/ directories.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime_root = Path(args.root).resolve()
    output_root = runtime_root / "output"
    if not output_root.exists():
        print(f"No output directory found at {output_root}.")
        return 0

    touched = 0
    structure_paths = sorted(output_root.glob("*/public/structure.json"))
    structure_paths.extend(sorted(output_root.glob("*/structure.json")))
    seen_output_dirs: set[Path] = set()
    for structure_path in structure_paths:
        output_dir = structure_path.parent.parent if structure_path.parent.name == "public" else structure_path.parent
        if output_dir in seen_output_dirs:
            continue
        seen_output_dirs.add(output_dir)
        changes = backfill_output_dir(output_dir)
        if not changes:
            continue
        touched += 1
        print(f"{output_dir.name}: {', '.join(changes)}")

    if touched == 0:
        print("No legacy output backfill needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
