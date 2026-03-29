"""Filesystem helpers for Iterator-Reader outputs."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from src.reading_runtime import artifacts as runtime_artifacts
from src.reading_runtime.output_dir_overrides import get_output_dir_override

from .models import BookStructure, StructureChapter


ITERATOR_V1_MECHANISM_KEY = "iterator_v1"


def slugify(value: str) -> str:
    """Create a stable directory slug from book metadata."""
    cleaned = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
    cleaned = re.sub(r"[-\s]+", "-", cleaned)
    return cleaned or "book"


def infer_chapter_number(title: str) -> int | None:
    """Infer a human-facing chapter number from a chapter title."""
    normalized = (title or "").strip()
    patterns = (
        r"^chapter\s+(\d+)\b",
        r"^第\s*(\d+)\s*章\b",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def chapter_reference(chapter: StructureChapter) -> str:
    """Return the human-facing chapter reference used in logs and lookup."""
    number = chapter.get("chapter_number")
    if number is None:
        number = infer_chapter_number(chapter.get("title", ""))
    if number is not None:
        return f"Chapter {number}"
    return chapter.get("title", f'Section {chapter.get("id", "")}')


def chapter_anchor_prefix(chapter: StructureChapter) -> str:
    """Return a stable human-readable anchor prefix for non-numbered chapters."""
    title = str(chapter.get("title", "") or "").strip()
    if title:
        normalized = re.sub(r"\s+", " ", title)
        cleaned = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE).strip()
        tokens = [token for token in cleaned.split() if token]
        if tokens:
            prefix = "_".join(tokens[:3]).strip("_")
            if prefix:
                return prefix[:40]
    return f'Part{int(chapter.get("id", 0))}'


def segment_reference(chapter: StructureChapter, segment_id: str) -> str:
    """Render a user-facing segment anchor aligned with chapter numbering rules."""
    raw_id = str(segment_id or "").strip()
    if "." not in raw_id:
        return raw_id
    _raw_prefix, suffix = raw_id.split(".", 1)

    number = chapter.get("chapter_number")
    if number is None:
        number = infer_chapter_number(chapter.get("title", ""))
    if number is not None:
        return f"{number}.{suffix}"
    return f"{chapter_anchor_prefix(chapter)}.{suffix}"


def chapter_output_name(chapter: StructureChapter) -> str:
    """Stable markdown filename for one chapter."""
    number = chapter.get("chapter_number")
    if number is None:
        number = infer_chapter_number(chapter.get("title", ""))
    if number is not None:
        return f"ch{number:02d}_deep_read.md"

    title_slug = slugify(chapter.get("title", "")) or "section"
    return f'part{chapter.get("id", 0):02d}_{title_slug}_deep_read.md'


def display_segment_id(chapter: StructureChapter, segment_id: str) -> str:
    """Render a user-facing segment id aligned with the visible chapter number."""
    return segment_reference(chapter, segment_id)


def resolve_output_dir(
    book_path: Path,
    book_title: str,
    book_language: str,
    output_language: str,
) -> Path:
    """Resolve the output directory for a given book."""
    override = get_output_dir_override()
    if override is not None:
        return override
    slug = slugify(book_title or book_path.stem)
    if output_language != book_language:
        slug = f"{slug}-{output_language}"
    return Path("output") / slug


def book_id_from_output_dir(output_dir: Path) -> str:
    """Derive the stable book id from the output directory name."""
    return runtime_artifacts.book_id_from_output_dir(output_dir)


def ensure_output_dir(path: Path) -> None:
    """Create output directory if missing."""
    path.mkdir(parents=True, exist_ok=True)


def public_dir(output_dir: Path) -> Path:
    """Directory storing user-visible stable artifacts."""
    return runtime_artifacts.public_dir(output_dir)


def public_chapters_dir(output_dir: Path) -> Path:
    """Directory storing public per-chapter artifacts."""
    return runtime_artifacts.public_chapters_dir(output_dir)


def internal_dir(output_dir: Path) -> Path:
    """Directory storing iterator_v1-private diagnostics and analysis artifacts."""

    return runtime_artifacts.mechanism_internal_dir(output_dir, ITERATOR_V1_MECHANISM_KEY)


def internal_qa_dir(output_dir: Path) -> Path:
    """Directory storing iterator_v1 chapter-level QA sidecars."""

    return runtime_artifacts.mechanism_internal_qa_dir(output_dir, ITERATOR_V1_MECHANISM_KEY)


def internal_diagnostics_dir(output_dir: Path) -> Path:
    """Directory storing iterator_v1 parse/backfill diagnostics."""

    return runtime_artifacts.mechanism_internal_diagnostics_dir(output_dir, ITERATOR_V1_MECHANISM_KEY)


def structure_file(output_dir: Path) -> Path:
    """Path to iterator_v1 structure.json inside an output directory."""

    return runtime_artifacts.mechanism_derived_dir(output_dir, ITERATOR_V1_MECHANISM_KEY) / "structure.json"


def structure_markdown_file(output_dir: Path) -> Path:
    """Path to iterator_v1 structure.md inside an output directory."""

    return runtime_artifacts.mechanism_derived_dir(output_dir, ITERATOR_V1_MECHANISM_KEY) / "structure.md"


def legacy_structure_file(output_dir: Path) -> Path:
    """Legacy flat structure.json path."""
    return output_dir / "structure.json"


def legacy_structure_markdown_file(output_dir: Path) -> Path:
    """Legacy flat structure.md path."""
    return output_dir / "structure.md"


def assets_dir(output_dir: Path) -> Path:
    """Directory storing frontend-accessible source assets."""
    return runtime_artifacts.assets_dir(output_dir)


def source_asset_file(output_dir: Path) -> Path:
    """Path to the copied source EPUB asset."""
    return runtime_artifacts.source_asset_file(output_dir)


def cover_asset_file(output_dir: Path, extension: str = ".jpg") -> Path:
    """Path to the copied cover image asset."""
    return runtime_artifacts.cover_asset_file(output_dir, extension)


def existing_cover_asset_file(output_dir: Path) -> Path | None:
    """Return the first persisted cover image asset if present."""
    return runtime_artifacts.existing_cover_asset_file(output_dir)


def ensure_source_asset(book_path: Path, output_dir: Path) -> Path:
    """Copy the source EPUB into the output asset directory when needed."""
    destination = source_asset_file(output_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.stat().st_mtime < book_path.stat().st_mtime:
        shutil.copy2(book_path, destination)
    return destination


def relative_asset_path(output_dir: Path, asset_path: Path) -> str:
    """Return an output-dir-relative asset path for persisted artifacts."""
    return str(asset_path.relative_to(output_dir))


def relative_output_path(output_dir: Path, path: Path) -> str:
    """Return an output-dir-relative path for a persisted artifact."""
    return str(path.relative_to(output_dir))


def chapter_markdown_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Stable markdown filepath for one chapter."""
    return public_chapters_dir(output_dir) / chapter_output_name(chapter)


def chapter_result_name(chapter: StructureChapter) -> str:
    """Stable JSON companion filename for one chapter."""
    return Path(chapter_output_name(chapter)).with_suffix(".json").name


def chapter_result_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Stable JSON companion filepath for one chapter."""
    return public_chapters_dir(output_dir) / chapter_result_name(chapter)


def legacy_chapter_markdown_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Legacy flat markdown path for one chapter."""
    return output_dir / chapter_output_name(chapter)


def legacy_chapter_result_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Legacy flat JSON path for one chapter."""
    return output_dir / chapter_result_name(chapter)


def segment_checkpoint_dir(output_dir: Path) -> Path:
    """Directory storing iterator_v1 segment-level checkpoints."""

    return runtime_artifacts.mechanism_runtime_dir(output_dir, ITERATOR_V1_MECHANISM_KEY) / "checkpoints"


def segment_checkpoint_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Path to one chapter's segment checkpoint file."""
    return segment_checkpoint_dir(output_dir) / f"{chapter_output_name(chapter)}.segments.json"


def analysis_dir(output_dir: Path) -> Path:
    """Directory storing iterator_v1 book-analysis intermediate artifacts."""

    return runtime_artifacts.mechanism_internal_analysis_dir(output_dir, ITERATOR_V1_MECHANISM_KEY)


def book_analysis_file(output_dir: Path) -> Path:
    """Path to iterator_v1 book-analysis markdown report."""

    return analysis_dir(output_dir) / "book_analysis.md"


def book_manifest_file(output_dir: Path) -> Path:
    """Path to the frontend-facing book manifest JSON."""
    return runtime_artifacts.book_manifest_file(output_dir)


def run_state_file(output_dir: Path) -> Path:
    """Path to the frontend-facing sequential run state JSON."""
    return runtime_artifacts.run_state_file(output_dir)


def activity_file(output_dir: Path) -> Path:
    """Path to the frontend-facing sequential activity stream JSONL."""
    return runtime_artifacts.activity_file(output_dir)


def parse_state_file(output_dir: Path) -> Path:
    """Path to parse-stage checkpoint metadata."""
    return runtime_artifacts.parse_state_file(output_dir)


def reader_memory_file(output_dir: Path) -> Path:
    """Path to the iterator_v1 reader memory snapshot."""

    return runtime_artifacts.mechanism_runtime_dir(output_dir, ITERATOR_V1_MECHANISM_KEY) / "reader_memory.json"


def runtime_dir(output_dir: Path) -> Path:
    """Directory storing current live runtime state."""
    return runtime_artifacts.runtime_dir(output_dir)


def history_dir(output_dir: Path) -> Path:
    """Directory storing archived run summaries."""
    return runtime_artifacts.history_dir(output_dir)


def history_runs_dir(output_dir: Path) -> Path:
    """Directory storing archived runs keyed by job id."""
    return runtime_artifacts.history_runs_dir(output_dir)


def plan_state_file(output_dir: Path) -> Path:
    """Path to iterator_v1 persisted planning state."""

    return runtime_artifacts.mechanism_runtime_dir(output_dir, ITERATOR_V1_MECHANISM_KEY) / "plan_state.json"


def legacy_plan_state_file(output_dir: Path) -> Path:
    """Legacy flat planning state path."""
    return output_dir / "plan_state.json"


def legacy_run_trace_file(output_dir: Path) -> Path:
    """Legacy flat run-trace path."""
    return output_dir / "run_trace.jsonl"


def run_history_dir(output_dir: Path, run_id: str) -> Path:
    """Directory for one archived run."""
    return runtime_artifacts.run_history_dir(output_dir, run_id)


def run_history_summary_file(output_dir: Path, run_id: str) -> Path:
    """Path to one archived run summary."""
    return runtime_artifacts.run_history_summary_file(output_dir, run_id)


def run_history_trace_file(output_dir: Path, run_id: str) -> Path:
    """Path to one archived run trace JSONL."""
    return runtime_artifacts.run_history_trace_file(output_dir, run_id)


def run_history_job_file(output_dir: Path, run_id: str) -> Path:
    """Path to one archived job record."""
    return runtime_artifacts.run_history_job_file(output_dir, run_id)


def run_history_job_log_file(output_dir: Path, run_id: str) -> Path:
    """Path to one archived job log."""
    return runtime_artifacts.run_history_job_log_file(output_dir, run_id)


def normalized_eval_bundle_file(output_dir: Path) -> Path:
    """Path to iterator_v1 normalized eval export."""

    return runtime_artifacts.mechanism_export_file(output_dir, ITERATOR_V1_MECHANISM_KEY, "normalized_eval_bundle.json")


def parse_diagnostics_file(output_dir: Path) -> Path:
    """Path to parse-stage diagnostics."""
    return internal_diagnostics_dir(output_dir) / "parse.json"


def locator_backfill_diagnostics_file(output_dir: Path) -> Path:
    """Path to locator-backfill diagnostics."""
    return internal_diagnostics_dir(output_dir) / "locator_backfill.json"


def chapter_qa_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Path to one chapter QA sidecar."""
    return internal_qa_dir(output_dir) / chapter_result_name(chapter)


def legacy_book_analysis_file(output_dir: Path) -> Path:
    """Legacy flat book-analysis markdown path."""
    return output_dir / "book_analysis.md"


def legacy_book_manifest_file(output_dir: Path) -> Path:
    """Legacy flat manifest path."""
    return runtime_artifacts.legacy_book_manifest_file(output_dir)


def legacy_run_state_file(output_dir: Path) -> Path:
    """Legacy flat run-state path."""
    return runtime_artifacts.legacy_run_state_file(output_dir)


def legacy_activity_file(output_dir: Path) -> Path:
    """Legacy flat activity-stream path."""
    return runtime_artifacts.legacy_activity_file(output_dir)


def legacy_segment_checkpoint_dir(output_dir: Path) -> Path:
    """Legacy checkpoint directory path."""
    return output_dir / "_checkpoints"


def legacy_segment_checkpoint_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Legacy chapter checkpoint path."""
    return legacy_segment_checkpoint_dir(output_dir) / f"{chapter_output_name(chapter)}.segments.json"


def legacy_analysis_dir(output_dir: Path) -> Path:
    """Legacy analysis directory path."""
    return output_dir / "_analysis"


def current_shared_internal_dir(output_dir: Path) -> Path:
    """Current pre-namespaced internal artifact directory kept for compatibility."""

    return output_dir / "_internal"


def current_shared_internal_qa_dir(output_dir: Path) -> Path:
    """Current pre-namespaced QA directory kept for compatibility."""

    return current_shared_internal_dir(output_dir) / "qa" / "chapters"


def current_shared_internal_diagnostics_dir(output_dir: Path) -> Path:
    """Current pre-namespaced diagnostics directory kept for compatibility."""

    return current_shared_internal_dir(output_dir) / "diagnostics"


def current_shared_analysis_dir(output_dir: Path) -> Path:
    """Current pre-namespaced analysis directory kept for compatibility."""

    return current_shared_internal_dir(output_dir) / "analysis"


def current_shared_structure_file(output_dir: Path) -> Path:
    """Current pre-namespaced structure.json location kept for compatibility."""

    return public_dir(output_dir) / "structure.json"


def current_shared_structure_markdown_file(output_dir: Path) -> Path:
    """Current pre-namespaced structure.md location kept for compatibility."""

    return public_dir(output_dir) / "structure.md"


def current_shared_reader_memory_file(output_dir: Path) -> Path:
    """Current pre-namespaced reader memory location kept for compatibility."""

    return runtime_dir(output_dir) / "reader_memory.json"


def current_shared_segment_checkpoint_dir(output_dir: Path) -> Path:
    """Current pre-namespaced checkpoint directory kept for compatibility."""

    return runtime_dir(output_dir) / "checkpoints"


def current_shared_plan_state_file(output_dir: Path) -> Path:
    """Current pre-namespaced plan state location kept for compatibility."""

    return runtime_dir(output_dir) / "plan_state.json"


def current_shared_book_analysis_file(output_dir: Path) -> Path:
    """Current pre-namespaced book analysis report kept for compatibility."""

    return public_dir(output_dir) / "book_analysis.md"


def legacy_reader_memory_file(output_dir: Path) -> Path:
    """Legacy flat reader-memory path."""

    return output_dir / "reader_memory.json"


def resolve_output_relative_file(output_dir: Path, relative_path: str | None, *, fallback: Path | None = None) -> Path:
    """Resolve a manifest-relative artifact path with legacy fallback support."""
    return runtime_artifacts.resolve_output_relative_file(output_dir, relative_path, fallback=fallback)


def existing_structure_file(output_dir: Path) -> Path:
    """Return the existing structure.json path with legacy fallback."""
    return runtime_artifacts.first_existing_path(
        structure_file(output_dir),
        current_shared_structure_file(output_dir),
        legacy_structure_file(output_dir),
    ) or structure_file(output_dir)


def existing_structure_markdown_file(output_dir: Path) -> Path:
    """Return the existing structure.md path with legacy fallback."""
    return runtime_artifacts.first_existing_path(
        structure_markdown_file(output_dir),
        current_shared_structure_markdown_file(output_dir),
        legacy_structure_markdown_file(output_dir),
    ) or structure_markdown_file(output_dir)


def existing_book_manifest_file(output_dir: Path) -> Path:
    """Return the existing manifest path with legacy fallback."""
    return runtime_artifacts.existing_book_manifest_file(output_dir)


def existing_run_state_file(output_dir: Path) -> Path:
    """Return the existing run-state path with legacy fallback."""
    return runtime_artifacts.existing_run_state_file(output_dir)


def existing_activity_file(output_dir: Path) -> Path:
    """Return the existing activity stream path with legacy fallback."""
    return runtime_artifacts.existing_activity_file(output_dir)


def existing_parse_state_file(output_dir: Path) -> Path:
    """Return the existing parse-state path."""
    return runtime_artifacts.existing_parse_state_file(output_dir)


def existing_reader_memory_file(output_dir: Path) -> Path:
    """Return the existing reader-memory path."""
    return runtime_artifacts.first_existing_path(
        reader_memory_file(output_dir),
        current_shared_reader_memory_file(output_dir),
        legacy_reader_memory_file(output_dir),
    ) or reader_memory_file(output_dir)


def existing_plan_state_file(output_dir: Path) -> Path:
    """Return the existing iterator_v1 plan-state path with compatibility fallback."""

    return runtime_artifacts.first_existing_path(
        plan_state_file(output_dir),
        current_shared_plan_state_file(output_dir),
        legacy_plan_state_file(output_dir),
    ) or plan_state_file(output_dir)


def existing_segment_checkpoint_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Return the existing iterator_v1 chapter checkpoint path with compatibility fallback."""

    return runtime_artifacts.first_existing_path(
        segment_checkpoint_file(output_dir, chapter),
        current_shared_segment_checkpoint_dir(output_dir) / f"{chapter_output_name(chapter)}.segments.json",
        legacy_segment_checkpoint_file(output_dir, chapter),
    ) or segment_checkpoint_file(output_dir, chapter)


def existing_book_analysis_file(output_dir: Path) -> Path:
    """Return the existing book-analysis markdown path with legacy fallback."""
    return runtime_artifacts.first_existing_path(
        book_analysis_file(output_dir),
        current_shared_book_analysis_file(output_dir),
        legacy_book_analysis_file(output_dir),
    ) or book_analysis_file(output_dir)


def existing_chapter_markdown_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Return the existing chapter markdown path with legacy fallback."""
    declared = str(chapter.get("output_file", "") or "").strip()
    declared_path = output_dir / declared if declared else None
    return (
        runtime_artifacts.first_existing_path(
            *(path for path in (declared_path, chapter_markdown_file(output_dir, chapter), legacy_chapter_markdown_file(output_dir, chapter)) if path is not None),
        )
        or chapter_markdown_file(output_dir, chapter)
    )


def existing_chapter_result_file(output_dir: Path, chapter: StructureChapter) -> Path:
    """Return the existing chapter result path with legacy fallback."""
    return runtime_artifacts.first_existing_path(
        chapter_result_file(output_dir, chapter),
        legacy_chapter_result_file(output_dir, chapter),
    ) or chapter_result_file(output_dir, chapter)


def analysis_plan_file(output_dir: Path) -> Path:
    """Path to persisted analysis planning payload."""
    return analysis_dir(output_dir) / "analysis_plan.json"


def segment_skim_cards_file(output_dir: Path) -> Path:
    """Path to segment skim cards JSONL."""
    return analysis_dir(output_dir) / "segment_skim_cards.jsonl"


def deep_targets_file(output_dir: Path) -> Path:
    """Path to selected deep targets JSON."""
    return analysis_dir(output_dir) / "deep_targets.json"


def deep_dossiers_file(output_dir: Path) -> Path:
    """Path to deep-read dossier records JSON."""
    return analysis_dir(output_dir) / "deep_dossiers.json"


def evidence_checks_file(output_dir: Path) -> Path:
    """Path to evidence-check records JSONL."""
    return analysis_dir(output_dir) / "evidence_checks.jsonl"


def analysis_trace_file(output_dir: Path) -> Path:
    """Path to book-analysis execution traces JSONL."""
    return analysis_dir(output_dir) / "analysis_trace.jsonl"


def clear_iterator_private_artifacts(output_dir: Path) -> None:
    """Remove iterator_v1-private runtime and analysis artifacts across new and legacy layouts."""

    for path in [
        reader_memory_file(output_dir),
        current_shared_reader_memory_file(output_dir),
        legacy_reader_memory_file(output_dir),
        plan_state_file(output_dir),
        current_shared_plan_state_file(output_dir),
        legacy_plan_state_file(output_dir),
        book_analysis_file(output_dir),
        current_shared_book_analysis_file(output_dir),
        legacy_book_analysis_file(output_dir),
        normalized_eval_bundle_file(output_dir),
    ]:
        path.unlink(missing_ok=True)

    for directory in [
        segment_checkpoint_dir(output_dir),
        current_shared_segment_checkpoint_dir(output_dir),
        legacy_segment_checkpoint_dir(output_dir),
        analysis_dir(output_dir),
        current_shared_analysis_dir(output_dir),
        legacy_analysis_dir(output_dir),
        internal_qa_dir(output_dir),
        current_shared_internal_qa_dir(output_dir),
        internal_diagnostics_dir(output_dir),
        current_shared_internal_diagnostics_dir(output_dir),
    ]:
        shutil.rmtree(directory, ignore_errors=True)


def save_structure(path: Path, structure: BookStructure) -> None:
    """Write structure.json with UTF-8 JSON formatting."""
    runtime_artifacts.ensure_mechanism_manifest_for_artifact_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(structure, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_structure(path: Path) -> BookStructure:
    """Load structure.json from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: object) -> None:
    """Write a generic JSON payload in UTF-8."""
    runtime_artifacts.ensure_mechanism_manifest_for_artifact_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_json(path: Path) -> dict:
    """Load JSON dictionary payload from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, payload: object) -> None:
    """Append one JSON line payload."""
    runtime_artifacts.ensure_mechanism_manifest_for_artifact_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False))
        file.write("\n")
