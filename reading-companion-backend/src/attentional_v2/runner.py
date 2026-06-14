"""Reading Runner integration for the attentional_v2 mechanism."""

from __future__ import annotations

import shutil
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from src.reading_core import BookDocument
from src.reading_core.storage import book_document_file, save_book_document
from src.reading_core.runtime_contracts import MechanismInfo, ParseRequest, ParseResult, ReadRequest, ReadResult, SharedRunCursor
from src.reading_runtime import artifacts as runtime_artifacts
from src.reading_runtime.llm_registry import DEFAULT_RUNTIME_PROFILE_ID
from src.reading_runtime.provisioning import ProvisionedBook, ensure_canonical_parse
from src.reading_runtime.sequential_state import (
    append_activity_event,
    build_book_manifest_from_document,
    build_run_state,
    chapter_reference,
    reset_activity,
    write_book_manifest,
    write_parse_progress,
    write_run_state,
)
from src.reading_runtime.shell_state import load_runtime_shell, save_runtime_shell
from src.iterator_reader.llm_utils import ReaderLLMError, llm_invocation_scope, runtime_trace_context

from .evaluation import build_normalized_eval_bundle, persist_normalized_eval_bundle
from .intake import process_sentence_intake  # noqa: F401 - legacy monkeypatch seam for older tests
from .llm_calls import (
    ingest as _call_ingest,
    digest as _call_digest,
)
from .llm_output_tools import validate_ingest_unit_memory_tool_args
from .observability import (
    maybe_capture_memory_quality_probe,
    memory_quality_probe_observability_settings,
    record_read,
    record_settlement,
    record_unitization,
)
from .resume import persist_reading_position, resume_from_checkpoint, write_full_checkpoint
from .source_spans import (
    build_paragraph_offset_preview,
    chapter_end_cursor,
    cursor_at_or_after_chapter_end,
    cursor_less_than,
    fallback_end_cursor_for_preview,
    first_cursor_for_chapter,
    normalize_cursor_for_chapter,
    readable_paragraphs,
    resolve_ingest_unit_boundary,
    resolve_preview_partition_audit,
    source_locus_from_unit,
    source_ref_from_span,
    source_ref_from_unit,
    source_span_id,
    source_unit_from_span,
)
from .schemas import (
    ATTENTIONAL_V2_MECHANISM_VERSION,
    ATTENTIONAL_V2_POLICY_VERSION,
    AnchoredReactionRecord,
    KnowledgeActivationsState,
    LocalBufferState,
    LocalContinuityState,
    IngestBoundaryResult,
    IngestTraceEntry,
    MemoryRetrievalMode,
    PreparedSourceUnit,
    ReactionRecordsState,
    ReaderPolicy,
    ReflectiveFramesState,
    UnitizeDecision,
    DigestResult,
    ActiveAttention,
    build_empty_continuation_capsule,
    build_default_reader_policy,
    build_empty_knowledge_activations,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_reaction_records,
    build_empty_reconsolidation_records,
    build_empty_recent_reading_memory,
    build_empty_reflective_frames,
    build_empty_resume_metadata,
    build_empty_active_attention,
    RecentReadingMemoryState,
)
from .slow_cycle import (
    build_reaction_record_from_surfaced_reaction,
    compat_reaction_family,
    project_chapter_result_compatibility,
    reaction_records_for_chapter,
    run_phase6_chapter_cycle,
)
from .state_ops import (
    append_reaction_record,
    apply_recent_reading_memory_operations,
    close_local_meaning_unit,
    apply_active_attention_operations,
)
from .state_migration import normalize_active_tension_state
from .state_projection import build_carry_forward_context
from .memory_tokens import estimate_tokens, token_estimate_payload, tokens_from_estimate
from .storage import (
    chapter_result_compatibility_file,
    checkpoints_dir,
    continuation_capsule_file,
    initialize_artifact_tree,
    knowledge_activations_file,
    load_json,
    local_buffer_file,
    local_continuity_file,
    memory_quality_probe_export_file,
    memory_retrieval_config_file,
    normalized_eval_bundle_file,
    reaction_records_file,
    recent_reading_memory_file,
    reader_policy_file,
    reconsolidation_records_file,
    reflective_frames_file,
    resume_metadata_file,
    runtime_dir,
    save_json,
    settlement_audit_file,
    survey_map_file,
    read_audit_file,
    unit_memory_retrieval_trace_file,
    unit_memory_sqlite_file,
    unitization_audit_file,
    active_attention_file,
)
from .survey import write_book_survey_artifacts
from .unit_memory import (
    UnitMemoryIndex,
    build_unit_memory_entry,
    fallback_query_from_source_unit,
    normalize_unit_memory_recalls,
    record_unit_memory_retrieval_trace,
    resolve_memory_retrieval_config,
)
from .unit_span_ledger import append_unit_span_record, latest_unit_span, next_unit_sequence_index


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Return one normalized string."""

    return str(value or "").strip()


def _chapter_ref(chapter: dict[str, object]) -> str:
    """Return the stable chapter reference for one book-document chapter."""

    return chapter_reference(chapter)


def _chapter_matches_request(chapter: dict[str, object], requested_number: int) -> bool:
    """Return whether one chapter matches a requested chapter number."""

    chapter_id = int(chapter.get("id", 0) or 0)
    chapter_number = int(chapter.get("chapter_number", 0) or 0)
    return requested_number in {chapter_id, chapter_number}


def _shared_cursor_for_sentence(
    *,
    chapter_id: int | None,
    chapter_ref: str,
    sentence: dict[str, object] | None,
) -> SharedRunCursor:
    """Build one shared cursor for a concrete sentence position."""

    if not isinstance(sentence, dict):
        return {
            "position_kind": "chapter",
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
        }
    sentence_id = _clean_text(sentence.get("sentence_id"))
    if not sentence_id:
        return {
            "position_kind": "chapter",
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
        }
    return {
        "position_kind": "sentence",
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "sentence_id": sentence_id,
    }


def _shared_cursor_for_source_cursor(
    cursor: dict[str, object] | None,
) -> SharedRunCursor:
    """Build one shared cursor for a paragraph-offset source position."""

    if not isinstance(cursor, dict):
        return {
            "position_kind": "chapter",
            "chapter_id": None,
            "chapter_ref": "",
        }
    return {
        "position_kind": "span",
        "chapter_id": int(cursor.get("chapter_id", 0) or 0) or None,
        "chapter_ref": _clean_text(cursor.get("chapter_ref")),
        "paragraph_index": int(cursor.get("paragraph_index", 0) or 0),
        "char_offset": int(cursor.get("char_offset", 0) or 0),
        "span_start_cursor": dict(cursor),
        "span_end_cursor": dict(cursor),
    }


def _shared_cursor_for_source_span(source_span: dict[str, object] | None) -> SharedRunCursor:
    """Build one shared cursor for an accepted paragraph-offset source span."""

    if not isinstance(source_span, dict):
        return _shared_cursor_for_source_cursor(None)
    start = source_span.get("start_cursor")
    end = source_span.get("end_cursor")
    if not isinstance(start, dict):
        return _shared_cursor_for_source_cursor(None)
    cursor = _shared_cursor_for_source_cursor(end if isinstance(end, dict) else start)
    cursor["span_start_cursor"] = dict(start)
    if isinstance(end, dict):
        cursor["span_end_cursor"] = dict(end)
    return cursor


def _compat_sentence_cursor_for_source_cursor(
    *,
    chapter: dict[str, object],
    source_cursor: dict[str, object],
    fallback_cursor: dict[str, object],
) -> dict[str, object]:
    """Project a paragraph-offset cursor back to the nearest sentence cursor."""

    if _clean_text(fallback_cursor.get("sentence_id")):
        return dict(fallback_cursor)
    sentences = [dict(sentence) for sentence in chapter.get("sentences", []) if isinstance(sentence, dict)]
    selected: dict[str, object] | None = None
    cursor_paragraph = int(source_cursor.get("paragraph_index", 0) or 0)
    cursor_offset = int(source_cursor.get("char_offset", 0) or 0)
    for sentence in sentences:
        locator = sentence.get("locator")
        paragraph_index = 0
        char_end = 0
        if isinstance(locator, dict):
            paragraph_index = int(locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0)
            char_end = int(locator.get("char_end", 0) or 0)
        if paragraph_index < cursor_paragraph or (paragraph_index == cursor_paragraph and char_end <= cursor_offset):
            selected = sentence
            continue
        break
    if selected is None and sentences:
        selected = sentences[0]
    return dict(
        _shared_cursor_for_sentence(
            chapter_id=int(chapter.get("id", 0) or 0),
            chapter_ref=_chapter_ref(chapter),
            sentence=selected,
        )
    )


def _chapter_statuses(document: BookDocument, output_dir: Path) -> dict[int, str]:
    """Return current attentional chapter statuses from persisted compatibility payloads."""

    statuses: dict[int, str] = {}
    for chapter in document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id <= 0:
            continue
        result_path = chapter_result_compatibility_file(output_dir, chapter_id)
        statuses[chapter_id] = "done" if result_path.exists() else "pending"
    return statuses


def _survey_chapter_zone_index(survey_map: dict[str, object]) -> dict[int, str]:
    """Return the chapter-id to zone index from one persisted survey map."""

    index: dict[int, str] = {}
    for entry in survey_map.get("chapter_map", []):
        if not isinstance(entry, dict):
            continue
        chapter_id = int(entry.get("chapter_id", 0) or 0)
        chapter_zone = _clean_text(entry.get("chapter_zone"))
        if chapter_id <= 0 or not chapter_zone:
            continue
        index[chapter_id] = chapter_zone
    return index


def _reading_plan_from_survey(document: BookDocument, survey_map: dict[str, object]) -> dict[str, object]:
    """Return one validated reading plan from the survey artifact or a conservative fallback."""

    chapter_ids = [
        int(chapter.get("id", 0) or 0)
        for chapter in document.get("chapters", [])
        if isinstance(chapter, dict) and int(chapter.get("id", 0) or 0) > 0
    ]
    plan = survey_map.get("reading_plan", {})
    if not isinstance(plan, dict):
        plan = {}
    allowed_ids = set(chapter_ids)

    def _validated_ids(raw_value: object) -> list[int]:
        values = raw_value if isinstance(raw_value, list) else []
        ordered: list[int] = []
        for item in values:
            chapter_id = int(item or 0)
            if chapter_id <= 0 or chapter_id not in allowed_ids or chapter_id in ordered:
                continue
            ordered.append(chapter_id)
        return ordered

    mainline_chapter_ids = _validated_ids(plan.get("mainline_chapter_ids"))
    deferred_chapter_ids = [
        chapter_id
        for chapter_id in _validated_ids(plan.get("deferred_chapter_ids"))
        if chapter_id not in mainline_chapter_ids
    ]
    zone_index = _survey_chapter_zone_index(survey_map)
    auxiliary_chapter_ids = [
        chapter_id
        for chapter_id in chapter_ids
        if zone_index.get(chapter_id) == "auxiliary"
        and chapter_id not in mainline_chapter_ids
        and chapter_id not in deferred_chapter_ids
    ]

    if not mainline_chapter_ids:
        fallback_ids = [
            chapter_id
            for chapter_id in chapter_ids
            if chapter_id not in auxiliary_chapter_ids
        ]
        if fallback_ids:
            mainline_chapter_ids = fallback_ids
            deferred_chapter_ids = []
        else:
            mainline_chapter_ids = chapter_ids
            auxiliary_chapter_ids = []

    return {
        "mode": _clean_text(plan.get("mode")) or "body_first",
        "mainline_chapter_ids": mainline_chapter_ids,
        "deferred_chapter_ids": deferred_chapter_ids,
        "auxiliary_chapter_ids": auxiliary_chapter_ids,
    }


def _scheduled_chapter_ids(document: BookDocument, survey_map: dict[str, object]) -> list[int]:
    """Return the ordered readable chapter ids for one body-first run."""

    plan = _reading_plan_from_survey(document, survey_map)
    queue = [
        int(chapter_id)
        for chapter_id in [*plan.get("mainline_chapter_ids", []), *plan.get("deferred_chapter_ids", [])]
        if int(chapter_id) > 0
    ]
    return list(dict.fromkeys(queue))


def _apply_reading_plan_statuses(
    chapter_statuses: dict[int, str],
    *,
    document: BookDocument,
    survey_map: dict[str, object],
    chapter_number: int | None,
) -> dict[int, str]:
    """Mark default-skipped auxiliary chapters as completed for body-first scheduling."""

    if chapter_number is not None:
        return chapter_statuses
    plan = _reading_plan_from_survey(document, survey_map)
    for chapter_id in plan.get("auxiliary_chapter_ids", []):
        if int(chapter_id) > 0:
            chapter_statuses[int(chapter_id)] = "done"
    return chapter_statuses


def _reading_queue_stage_for_chapter(chapter_id: int, *, survey_map: dict[str, object]) -> str:
    """Return the current queue stage label for one scheduled chapter."""

    plan = survey_map.get("reading_plan", {})
    deferred_ids = plan.get("deferred_chapter_ids", []) if isinstance(plan, dict) else []
    if int(chapter_id) in {int(item or 0) for item in deferred_ids if int(item or 0) > 0}:
        return "deferred_support"
    return "mainline"


def _completed_scheduled_chapters(chapter_statuses: dict[int, str], *, scheduled_chapter_ids: list[int]) -> int:
    """Return the count of scheduled chapters already marked complete."""

    scheduled_set = {int(chapter_id) for chapter_id in scheduled_chapter_ids if int(chapter_id) > 0}
    return len(
        [
            chapter_id
            for chapter_id, status in chapter_statuses.items()
            if int(chapter_id) in scheduled_set and status == "done"
        ]
    )


def _audit_window_max_units(request: ReadRequest) -> int:
    """Return the optional audit-only unit cap for one read invocation."""

    raw_value = dict(request.mechanism_config or {}).get("audit_window_max_units", 0)
    try:
        value = int(raw_value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, value)


def _persist_partial_chapter_projections(
    *,
    output_dir: Path,
    chapter_lookup: dict[int, dict[str, object]],
    touched_chapter_ids: set[int],
    reaction_records: ReactionRecordsState,
    output_language: str,
    chapter_statuses: dict[int, str],
) -> dict[int, str]:
    """Persist compatibility payloads for chapters touched by a partial audit run."""

    if not touched_chapter_ids:
        return chapter_statuses
    book_id = runtime_artifacts.book_id_from_output_dir(output_dir)
    for chapter_id in sorted(int(item) for item in touched_chapter_ids if int(item) > 0):
        chapter = chapter_lookup.get(chapter_id)
        if not isinstance(chapter, dict):
            continue
        project_chapter_result_compatibility(
            book_id=book_id,
            chapter=chapter,
            reaction_records=reaction_records,
            output_language=output_language,
            output_dir=output_dir,
            persist=True,
        )
        chapter_statuses[chapter_id] = "done"
    return chapter_statuses


def _chapter_result_relative_paths(document: BookDocument, output_dir: Path) -> dict[int, str]:
    """Return manifest-relative compatibility result paths for ready chapters."""

    paths: dict[int, str] = {}
    for chapter in document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id <= 0:
            continue
        result_path = chapter_result_compatibility_file(output_dir, chapter_id)
        if result_path.exists():
            paths[chapter_id] = str(result_path.relative_to(output_dir))
    return paths


def _write_manifest(
    output_dir: Path,
    document: BookDocument,
    *,
    chapter_statuses: dict[int, str] | None = None,
) -> dict[str, object]:
    """Persist one shared book manifest for attentional outputs."""

    manifest = build_book_manifest_from_document(
        output_dir,
        document,
        chapter_statuses=chapter_statuses or _chapter_statuses(document, output_dir),
        chapter_result_relative_paths=_chapter_result_relative_paths(document, output_dir),
    )
    return write_book_manifest(output_dir, manifest)


def _artifact_summary(
    provisioned: ProvisionedBook,
    book_document: BookDocument,
    *,
    artifact_tree: dict[str, object],
    survey_summary: dict[str, object],
) -> dict[str, object]:
    """Build the attentional parse/read artifact summary returned through runtime contracts."""

    chapters = [
        {
            "id": int(chapter.get("id", 0) or 0),
            "title": _clean_text(chapter.get("title")),
            "reference": _chapter_ref(chapter),
            "chapter_number": chapter.get("chapter_number"),
            "sentence_count": len(chapter.get("sentences", [])) if isinstance(chapter.get("sentences"), list) else 0,
            "status": "done"
            if chapter_result_compatibility_file(provisioned.output_dir, int(chapter.get("id", 0) or 0)).exists()
            else "pending",
        }
        for chapter in book_document.get("chapters", [])
        if isinstance(chapter, dict)
    ]
    return {
        "book": provisioned.title,
        "author": provisioned.author,
        "book_language": provisioned.book_language,
        "output_language": provisioned.output_language,
        "source_file": str(provisioned.book_path),
        "output_dir": str(provisioned.output_dir),
        "chapter_count": len(chapters),
        "chapters": chapters,
        "artifact_map": artifact_tree.get("artifact_map", {}),
        "survey_status": survey_summary.get("survey_map", {}).get("status", "ready"),
    }


def _default_builder(name: str) -> Callable[[], dict[str, object]]:
    """Return a builder for one runtime-state artifact."""

    builders: dict[str, Callable[[], dict[str, object]]] = {
        "local_buffer": lambda: build_empty_local_buffer(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "local_continuity": lambda: build_empty_local_continuity(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "continuation_capsule": lambda: build_empty_continuation_capsule(
            mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION,
        ),
        "active_attention": lambda: build_empty_active_attention(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "recent_reading_memory": lambda: build_empty_recent_reading_memory(
            mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION
        ),
        "reflective_frames": lambda: build_empty_reflective_frames(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "knowledge_activations": lambda: build_empty_knowledge_activations(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "reaction_records": lambda: build_empty_reaction_records(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "reconsolidation_records": lambda: build_empty_reconsolidation_records(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "reader_policy": lambda: build_default_reader_policy(
            mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION,
            policy_version=ATTENTIONAL_V2_POLICY_VERSION,
        ),
        "resume_metadata": lambda: build_empty_resume_metadata(
            mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION,
            policy_version=ATTENTIONAL_V2_POLICY_VERSION,
        ),
    }
    return builders[name]


def _load_or_default(path: Path, builder: Callable[[], dict[str, object]]) -> dict[str, object]:
    """Load one JSON artifact or return its default shape."""

    if path.exists():
        return load_json(path)
    return builder()


def _load_runtime_bundle(output_dir: Path) -> dict[str, dict[str, object]]:
    """Load the attentional runtime bundle from persisted artifacts."""

    legacy_route_paths = (
        runtime_dir(output_dir) / "route_history.json",
        runtime_dir(output_dir) / "move_history.json",
    )
    if any(path.exists() for path in legacy_route_paths):
        raise RuntimeError(
            "Pre-forward-settlement attentional_v2 route state is no longer supported; rerun from a fresh runtime directory."
        )
    bundle = {
        "local_buffer": _load_or_default(local_buffer_file(output_dir), _default_builder("local_buffer")),
        "local_continuity": _load_or_default(local_continuity_file(output_dir), _default_builder("local_continuity")),
        "continuation_capsule": _load_or_default(continuation_capsule_file(output_dir), _default_builder("continuation_capsule")),
        "knowledge_activations": _load_or_default(
            knowledge_activations_file(output_dir),
            _default_builder("knowledge_activations"),
        ),
        "reaction_records": _load_or_default(reaction_records_file(output_dir), _default_builder("reaction_records")),
        "reconsolidation_records": _load_or_default(
            reconsolidation_records_file(output_dir),
            _default_builder("reconsolidation_records"),
        ),
        "reader_policy": _load_or_default(reader_policy_file(output_dir), _default_builder("reader_policy")),
        "resume_metadata": _load_or_default(resume_metadata_file(output_dir), _default_builder("resume_metadata")),
    }
    legacy_paths = {
        "legacy_hot_state": runtime_dir(output_dir) / ("working_" + "pressure.json"),
        "anchor_memory": runtime_dir(output_dir) / "anchor_memory.json",
        "anchor_bank": runtime_dir(output_dir) / "anchor_bank.json",
        "retired_object_memory": runtime_dir(output_dir) / ("concept_" + "registry.json"),
        "retired_line_memory": runtime_dir(output_dir) / ("thread_" + "trace.json"),
        "reflective_summaries": runtime_dir(output_dir) / "reflective_summaries.json",
    }
    new_state_paths = {
        "active_attention": active_attention_file(output_dir),
        "recent_reading_memory": recent_reading_memory_file(output_dir),
        "reflective_frames": reflective_frames_file(output_dir),
    }
    loaded_new = {name: load_json(path) for name, path in new_state_paths.items() if path.exists()}
    if not loaded_new and any(path.exists() for path in legacy_paths.values()):
        raise RuntimeError(
            "Pre-Phase C.3 attentional_v2 runtime state is no longer supported; rerun from a new-format state directory."
        )
    for name in ("active_attention", "recent_reading_memory", "reflective_frames"):
        bundle[name] = loaded_new.get(name) or _default_builder(name)()
    bundle["active_attention"] = normalize_active_tension_state(bundle["active_attention"])
    return bundle


def _save_runtime_bundle(output_dir: Path, bundle: dict[str, dict[str, object]]) -> None:
    """Persist the attentional runtime bundle."""

    save_json(local_buffer_file(output_dir), bundle["local_buffer"])
    save_json(local_continuity_file(output_dir), bundle["local_continuity"])
    save_json(continuation_capsule_file(output_dir), bundle["continuation_capsule"])
    save_json(active_attention_file(output_dir), normalize_active_tension_state(bundle["active_attention"]))
    save_json(recent_reading_memory_file(output_dir), bundle["recent_reading_memory"])
    save_json(reflective_frames_file(output_dir), bundle["reflective_frames"])
    save_json(knowledge_activations_file(output_dir), bundle["knowledge_activations"])
    save_json(reaction_records_file(output_dir), bundle["reaction_records"])
    save_json(reconsolidation_records_file(output_dir), bundle["reconsolidation_records"])
    save_json(reader_policy_file(output_dir), bundle["reader_policy"])
    save_json(resume_metadata_file(output_dir), bundle["resume_metadata"])


def _compatibility_section_ref(chapter_id: int, sentence: dict[str, object]) -> str:
    """Return the current section-ref sidecar for one sentence anchor."""

    locator = sentence.get("locator")
    paragraph_index = 0
    if isinstance(locator, dict):
        paragraph_index = int(locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0)
    if paragraph_index <= 0:
        paragraph_index = int(sentence.get("paragraph_index", 0) or 0)
    return f"{chapter_id}.{max(1, paragraph_index)}"


def _span_sentences(local_buffer: LocalBufferState) -> list[dict[str, object]]:
    """Return the current meaning-unit span from the rolling local buffer."""

    recent_sentences = [dict(item) for item in local_buffer.get("recent_sentences", []) if isinstance(item, dict)]
    open_ids = [str(item or "") for item in local_buffer.get("open_meaning_unit_sentence_ids", []) if str(item or "")]
    if not open_ids:
        return recent_sentences[-1:] if recent_sentences else []
    open_set = set(open_ids)
    span = [sentence for sentence in recent_sentences if _clean_text(sentence.get("sentence_id")) in open_set]
    return span or recent_sentences[-1:]


def _reading_locus(chapter_id: int, chapter_ref: str, sentence: dict[str, object], local_buffer: LocalBufferState) -> dict[str, object]:
    """Build the additive public reading-locus payload for live activity."""

    locus: dict[str, object] = {
        "kind": "span" if local_buffer.get("open_meaning_unit_sentence_ids") else "sentence",
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "sentence_start_id": _clean_text(local_buffer.get("open_meaning_unit_sentence_ids", [sentence.get("sentence_id")])[0] if local_buffer.get("open_meaning_unit_sentence_ids") else sentence.get("sentence_id")),
        "sentence_end_id": _clean_text(sentence.get("sentence_id")),
        "excerpt": _clean_text(sentence.get("text"))[:220],
    }
    locator = sentence.get("locator")
    if isinstance(locator, dict):
        locus["locator"] = dict(locator)
    return locus


def _current_activity(
    *,
    chapter_id: int,
    chapter_ref: str,
    sentence: dict[str, object],
    local_buffer: LocalBufferState,
    active_reaction_id: str | None = None,
) -> dict[str, object]:
    """Build the shared current-reading-activity snapshot."""

    activity: dict[str, object] = {
        "phase": "reading",
        "updated_at": _timestamp(),
        "segment_ref": _compatibility_section_ref(chapter_id, sentence),
        "current_excerpt": _clean_text(sentence.get("text"))[:220],
        "reading_locus": _reading_locus(chapter_id, chapter_ref, sentence, local_buffer),
        "reconstructed_hot_state": bool(local_buffer.get("is_reconstructed")),
        "last_resume_kind": local_buffer.get("last_resume_kind"),
    }
    if active_reaction_id:
        activity["active_reaction_id"] = active_reaction_id
    return activity


def _compatibility_section_ref_for_source(chapter_id: int, source_unit: dict[str, object]) -> str:
    """Return the paragraph-based compatibility segment ref for one source unit."""

    source_span = source_unit.get("source_span")
    if isinstance(source_span, dict) and isinstance(source_span.get("start_cursor"), dict):
        paragraph_index = int(source_span["start_cursor"].get("paragraph_index", 0) or 0)
        if paragraph_index > 0:
            return f"{chapter_id}.{paragraph_index}"
    return f"{chapter_id}.1"


def _current_activity_from_source_unit(
    *,
    chapter_id: int,
    chapter_ref: str,
    source_unit: dict[str, object],
    local_buffer: LocalBufferState,
    active_reaction_id: str | None = None,
) -> dict[str, object]:
    """Build the shared current-reading-activity snapshot for a source span."""

    activity: dict[str, object] = {
        "phase": "reading",
        "updated_at": _timestamp(),
        "segment_ref": _compatibility_section_ref_for_source(chapter_id, source_unit),
        "current_excerpt": _clean_text(source_unit.get("source_text"))[:220],
        "reading_locus": {
            **source_locus_from_unit(source_unit),
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
        },
        "reconstructed_hot_state": bool(local_buffer.get("is_reconstructed")),
        "last_resume_kind": local_buffer.get("last_resume_kind"),
    }
    if active_reaction_id:
        activity["active_reaction_id"] = active_reaction_id
    return activity


def _update_shell_phase(output_dir: Path, *, status: str, phase: str) -> None:
    """Update the thin shared runtime shell status/phase."""

    shell_path = runtime_artifacts.runtime_shell_file(output_dir)
    shell = load_runtime_shell(shell_path)
    shell["status"] = status
    shell["phase"] = phase
    shell["updated_at"] = _timestamp()
    save_runtime_shell(shell_path, shell)


def _reset_live_runtime(output_dir: Path) -> None:
    """Clear live attentional runtime artifacts for one fresh full rerun."""

    for path in (
        active_attention_file(output_dir),
        recent_reading_memory_file(output_dir),
        local_buffer_file(output_dir),
        local_continuity_file(output_dir),
        continuation_capsule_file(output_dir),
        reflective_frames_file(output_dir),
        knowledge_activations_file(output_dir),
        reaction_records_file(output_dir),
        reconsolidation_records_file(output_dir),
        resume_metadata_file(output_dir),
        memory_retrieval_config_file(output_dir),
        read_audit_file(output_dir),
        settlement_audit_file(output_dir),
        unitization_audit_file(output_dir),
        unit_memory_retrieval_trace_file(output_dir),
        unit_memory_sqlite_file(output_dir),
        memory_quality_probe_export_file(output_dir),
        runtime_artifacts.runtime_shell_file(output_dir),
        runtime_artifacts.run_state_file(output_dir),
        runtime_artifacts.parse_state_file(output_dir),
        runtime_dir(output_dir) / "anchor_bank.json",
        runtime_dir(output_dir) / ("concept_" + "registry.json"),
        runtime_dir(output_dir) / ("thread_" + "trace.json"),
        runtime_dir(output_dir) / "route_history.json",
        runtime_dir(output_dir) / "move_history.json",
    ):
        path.unlink(missing_ok=True)
    shutil.rmtree(checkpoints_dir(output_dir), ignore_errors=True)
    shutil.rmtree(runtime_artifacts.checkpoint_summaries_dir(output_dir), ignore_errors=True)
    shutil.rmtree(chapter_result_compatibility_file(output_dir, 1).parent, ignore_errors=True)
    shutil.rmtree(normalized_eval_bundle_file(output_dir).parent, ignore_errors=True)
    reset_activity(output_dir)


def _chapter_selection(
    document: BookDocument,
    output_dir: Path,
    *,
    survey_map: dict[str, object],
    chapter_number: int | None,
    continue_mode: bool,
    resume_chapter_id: int | None,
) -> list[dict[str, object]]:
    """Select chapters for the current Reading Runner invocation."""

    chapters = [dict(chapter) for chapter in document.get("chapters", []) if isinstance(chapter, dict)]
    if chapter_number is not None:
        selected = [chapter for chapter in chapters if _chapter_matches_request(chapter, chapter_number)]
        if not selected:
            raise ValueError(f"Chapter {chapter_number} was not found in the parsed book.")
        return selected

    queue_ids = _scheduled_chapter_ids(document, survey_map)
    chapter_lookup = {
        int(chapter.get("id", 0) or 0): chapter
        for chapter in chapters
        if int(chapter.get("id", 0) or 0) > 0
    }
    queued_chapters = [
        dict(chapter_lookup[chapter_id])
        for chapter_id in queue_ids
        if chapter_id in chapter_lookup
    ]

    if not continue_mode:
        return queued_chapters or chapters

    remaining = [
        chapter
        for chapter in (queued_chapters or chapters)
        if not chapter_result_compatibility_file(output_dir, int(chapter.get("id", 0) or 0)).exists()
    ]
    if resume_chapter_id and any(int(chapter.get("id", 0) or 0) == int(resume_chapter_id) for chapter in remaining):
        start_index = next(
            index
            for index, chapter in enumerate(remaining)
            if int(chapter.get("id", 0) or 0) == int(resume_chapter_id)
        )
        remaining = [*remaining[start_index:], *remaining[:start_index]]
    return remaining


def _chapter_start_index(chapter: dict[str, object], current_sentence_id: str) -> int:
    """Return the first unread sentence index for one continued chapter."""

    if not current_sentence_id:
        return 0
    sentences = chapter.get("sentences", [])
    for index, sentence in enumerate(sentences):
        if isinstance(sentence, dict) and _clean_text(sentence.get("sentence_id")) == current_sentence_id:
            return index + 1
    return 0


def _chapter_start_source_cursor(
    *,
    chapter: dict[str, object],
    local_continuity: LocalContinuityState,
    output_dir: Path,
    continue_mode: bool,
) -> dict[str, object]:
    """Return the source cursor where mainline reading should start."""

    if continue_mode:
        cursor = local_continuity.get("mainline_cursor")
        if isinstance(cursor, dict):
            end_cursor = cursor.get("span_end_cursor")
            if isinstance(end_cursor, dict) and int(end_cursor.get("chapter_id", 0) or 0) == int(chapter.get("id", 0) or 0):
                return normalize_cursor_for_chapter(chapter, end_cursor)
            if int(cursor.get("chapter_id", 0) or 0) == int(chapter.get("id", 0) or 0) and cursor.get("paragraph_index") is not None:
                return normalize_cursor_for_chapter(chapter, cursor)
        latest = latest_unit_span(output_dir)
        if isinstance(latest, dict) and int(latest.get("chapter_id", 0) or 0) == int(chapter.get("id", 0) or 0):
            end_cursor = latest.get("end_cursor")
            if isinstance(end_cursor, dict):
                return normalize_cursor_for_chapter(chapter, end_cursor)
    return first_cursor_for_chapter(chapter)


def _sentence_id(sentence: dict[str, object]) -> str:
    """Return the normalized sentence id for one sentence-like mapping."""

    return _clean_text(sentence.get("sentence_id"))


def _sentence_paragraph_index(sentence: dict[str, object]) -> int:
    """Return the best-effort paragraph index for one sentence-like mapping."""

    locator = sentence.get("locator")
    raw_value: object = None
    if isinstance(locator, dict):
        raw_value = locator.get("paragraph_index") or locator.get("paragraph_start")
    if raw_value is None:
        raw_value = sentence.get("paragraph_index")
    try:
        return max(0, int(raw_value or 0))
    except (TypeError, ValueError):
        return 0


def _ordered_sentence_ids(chapters: list[dict[str, object]]) -> list[str]:
    """Return the stable sentence order across one selected chapter sequence."""

    ordered: list[str] = []
    for chapter in chapters:
        if not isinstance(chapter, dict):
            continue
        for sentence in chapter.get("sentences", []):
            if not isinstance(sentence, dict):
                continue
            sentence_id = _sentence_id(sentence)
            if sentence_id:
                ordered.append(sentence_id)
    return ordered


def _resolve_unit_sentences(
    sentences: list[dict[str, object]],
    *,
    unitize_decision: UnitizeDecision,
) -> list[dict[str, object]]:
    """Return the exact chosen coverage unit from the chapter sentence list."""

    start_id = _clean_text(unitize_decision.get("start_sentence_id"))
    end_id = _clean_text(unitize_decision.get("end_sentence_id"))
    if not start_id or not end_id:
        return []

    start_index = next((index for index, sentence in enumerate(sentences) if _sentence_id(sentence) == start_id), -1)
    end_index = next((index for index, sentence in enumerate(sentences) if _sentence_id(sentence) == end_id), -1)
    if start_index < 0 or end_index < start_index:
        return []
    return [dict(sentence) for sentence in sentences[start_index : end_index + 1]]


def _compat_unit_sentences_for_source_span(
    chapter: dict[str, object],
    source_span: dict[str, object],
) -> list[dict[str, object]]:
    """Return overlapping sentence records for legacy consumers only."""

    start = source_span.get("start_cursor")
    end = source_span.get("end_cursor")
    if not isinstance(start, dict) or not isinstance(end, dict):
        return []
    start_paragraph = int(start.get("paragraph_index", 0) or 0)
    start_offset = int(start.get("char_offset", 0) or 0)
    end_paragraph = int(end.get("paragraph_index", 0) or 0)
    end_offset = int(end.get("char_offset", 0) or 0)
    selected: list[dict[str, object]] = []
    for sentence in chapter.get("sentences", []):
        if not isinstance(sentence, dict):
            continue
        locator = sentence.get("locator")
        if not isinstance(locator, dict):
            continue
        paragraph_index = int(locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0)
        char_start = int(locator.get("char_start", 0) or 0)
        char_end = int(locator.get("char_end", 0) or 0)
        if paragraph_index < start_paragraph or paragraph_index > end_paragraph:
            continue
        if paragraph_index == start_paragraph and char_end <= start_offset:
            continue
        if paragraph_index == end_paragraph and char_start >= end_offset:
            continue
        selected.append(dict(sentence))
    return selected


def _build_sentence_lookup(
    document: BookDocument,
) -> tuple[dict[str, dict[str, object]], dict[int, dict[str, object]]]:
    """Build sentence and chapter lookup tables from the shared book document."""

    sentence_lookup: dict[str, dict[str, object]] = {}
    chapter_lookup: dict[int, dict[str, object]] = {}
    for raw_chapter in document.get("chapters", []):
        if not isinstance(raw_chapter, dict):
            continue
        chapter = dict(raw_chapter)
        chapter_id = int(chapter.get("id", 0) or 0)
        if chapter_id <= 0:
            continue
        chapter_lookup[chapter_id] = chapter
        chapter_ref = _chapter_ref(chapter)
        for index, sentence in enumerate(chapter.get("sentences", [])):
            if not isinstance(sentence, dict):
                continue
            sentence_id = _sentence_id(sentence)
            if not sentence_id:
                continue
            sentence_lookup[sentence_id] = {
                "chapter_id": chapter_id,
                "chapter_ref": chapter_ref,
                "sentence_index": index,
                "sentence": dict(sentence),
            }
    return sentence_lookup, chapter_lookup


def _current_view_content_packet(preview: dict[str, object]) -> dict[str, object]:
    """Build the paragraph-offset source preview packet for Ingest."""

    return {
        "preview_start_cursor": dict(preview.get("preview_start_cursor", {}))
        if isinstance(preview.get("preview_start_cursor"), dict)
        else {},
        "preview_end_cursor": dict(preview.get("preview_end_cursor", {}))
        if isinstance(preview.get("preview_end_cursor"), dict)
        else {},
        "source_text": str(preview.get("source_text", "") or ""),
        "paragraph_slices": [
            {
                "paragraph_index": item.get("paragraph_index"),
                "text_role": _clean_text(item.get("text_role")),
                "start_char": item.get("start_char"),
                "end_char": item.get("end_char"),
                "text": str(item.get("text", "") or ""),
            }
            for item in preview.get("paragraph_slices", [])
            if isinstance(item, dict)
        ],
        "truncated": bool(preview.get("truncated")),
        "char_count": int(preview.get("char_count", 0) or 0),
        "paragraph_count": int(preview.get("paragraph_count", 0) or 0),
        "preview_end_reason": _clean_text(preview.get("preview_end_reason")),
        "estimated_token_count": int(preview.get("estimated_token_count", 0) or 0),
        "preview_token_estimator": _clean_text(preview.get("preview_token_estimator")),
    }


def _build_ingest_boundary_preparation(
    *,
    current_chapter: dict[str, object],
    current_cursor: dict[str, object],
    reader_policy: ReaderPolicy,
) -> dict[str, object]:
    """Prepare the runtime packet consumed by the Ingest LLM boundary call."""

    source_cursor = normalize_cursor_for_chapter(current_chapter, current_cursor)
    preview = build_paragraph_offset_preview(
        chapter=current_chapter,
        current_cursor=source_cursor,
        reader_policy=reader_policy,
    )
    current_chapter_id = int(current_chapter.get("id", 0) or 0)
    current_chapter_ref = _chapter_ref(current_chapter)
    chapter_title = _clean_text(current_chapter.get("title"))
    return {
        "chapter_id": current_chapter_id,
        "chapter_ref": current_chapter_ref,
        "chapter_title": chapter_title,
        "source_cursor": dict(source_cursor),
        "preview": dict(preview),
        "current_view_content": _current_view_content_packet(dict(preview)),
        "current_view_position": {
            "current_chapter_id": current_chapter_id,
            "current_chapter_ref": current_chapter_ref,
            "chapter_title": chapter_title,
            "current_cursor": dict(source_cursor),
            "retry": False,
        },
    }


def _ingest_trace_entry(
    boundary_result: IngestBoundaryResult,
    *,
    error: str = "",
) -> IngestTraceEntry:
    """Return a compact Ingest boundary trace entry."""

    entry: IngestTraceEntry = {
        "reason": _clean_text(boundary_result.get("reason")),
        "unit": dict(boundary_result.get("unit", {})) if isinstance(boundary_result.get("unit"), dict) else {},
        "preview_partition": [
            dict(item)
            for item in boundary_result.get("preview_partition", [])
            if isinstance(item, dict)
        ]
        if isinstance(boundary_result.get("preview_partition"), list)
        else [],
        "preview_partition_audit": [
            dict(item)
            for item in boundary_result.get("preview_partition_audit", [])
            if isinstance(item, dict)
        ]
        if isinstance(boundary_result.get("preview_partition_audit"), list)
        else [],
        "preview_partition_audit_status": _clean_text(boundary_result.get("preview_partition_audit_status")),
        "end_anchor_text": _clean_text(boundary_result.get("end_anchor_text")),
        "memory_recalls": [
            dict(item)
            for item in boundary_result.get("memory_recalls", [])
            if isinstance(item, dict)
        ]
        if isinstance(boundary_result.get("memory_recalls"), list)
        else [],
        "memory_recalls_status": _clean_text(boundary_result.get("memory_recalls_status")) or "missing",
        "tool_loop_status": _clean_text(boundary_result.get("tool_loop_status")),
        "tool_result_summary": dict(boundary_result.get("tool_result_summary", {}))
        if isinstance(boundary_result.get("tool_result_summary"), dict)
        else {},
        "source_span_id": _clean_text(boundary_result.get("source_span_id")),
        "resolution": dict(boundary_result.get("resolution", {})) if isinstance(boundary_result.get("resolution"), dict) else {},
    }
    if error:
        entry["error"] = error
    return entry


def _compact_ingest_trace(ingest_trace: object) -> list[dict[str, object]]:
    """Return compact boundary trace entries safe for read-audit persistence."""

    if not isinstance(ingest_trace, list):
        return []
    compact_entries: list[dict[str, object]] = []
    for item in ingest_trace:
        if not isinstance(item, dict):
            continue
        entry: dict[str, object] = {}
        for key in (
            "reason",
            "unit",
            "preview_partition",
            "preview_partition_audit",
            "preview_partition_audit_status",
            "end_anchor_text",
            "memory_recalls",
            "memory_recalls_status",
            "tool_loop_status",
            "tool_result_summary",
            "source_span_id",
            "resolution",
            "error",
        ):
            value = item.get(key)
            if isinstance(value, dict):
                entry[key] = dict(value)
            elif isinstance(value, str):
                cleaned = _clean_text(value)
                if cleaned:
                    entry[key] = cleaned
            elif value not in (None, "", [], {}):
                entry[key] = value
        if entry:
            compact_entries.append(entry)
    return compact_entries


def _source_span_position(source_span_id: str) -> tuple[int, int]:
    """Return paragraph/start position from a compact source span id."""

    match = re.search(r":p(\d+)@", str(source_span_id or ""))
    paragraph_index = int(match.group(1)) if match else 0
    chapter_match = re.search(r"src:c(\d+):", str(source_span_id or ""))
    chapter_id = int(chapter_match.group(1)) if chapter_match else 0
    return chapter_id, paragraph_index


def _reading_memory_prefix(*, source_span_id: str, unit_index: int, include_chapter: bool = False) -> str:
    chapter_id, paragraph_index = _source_span_position(source_span_id)
    if include_chapter and chapter_id:
        return f"C{chapter_id} P{paragraph_index} U{unit_index}: "
    return f"P{paragraph_index} U{unit_index}: "


def _line_token_count(prefix: str, text: str, stored_estimate: object) -> int:
    stored_tokens = tokens_from_estimate(stored_estimate)
    return stored_tokens + estimate_tokens(prefix) if stored_tokens else estimate_tokens(f"{prefix}{text}")


def _reading_memory_line(*, prefix: str, text: str, token_estimate: object, origin: str, unit_id: str = "", source_span_id: str = "", unit_index: int = 0) -> dict[str, object]:
    return {
        "text": f"{prefix}{text}",
        "memory_text": text,
        "prefix": prefix.strip(),
        "origin": origin,
        "unit_id": unit_id,
        "source_span_id": source_span_id,
        "unit_index": unit_index,
        "estimated_tokens": _line_token_count(prefix, text, token_estimate),
    }


def _hot_reading_memory_lines(
    recent_reading_memory: RecentReadingMemoryState,
    *,
    chapter_id: int,
    budget_tokens: int = 5000,
) -> tuple[list[dict[str, object]], set[str], list[dict[str, object]]]:
    """Return current-chapter recent Understanding lines under budget."""

    lines: list[dict[str, object]] = []
    suppressed: list[dict[str, object]] = []
    used_tokens = 0
    entries = [
        dict(item)
        for item in recent_reading_memory.get("entries", [])
        if isinstance(item, dict) and _clean_text(item.get("status")) == "active"
    ]
    entries.sort(key=lambda item: int(item.get("created_at_unit_index", 0) or 0), reverse=True)
    for entry in entries:
        source_span_id = _clean_text(entry.get("source_unit_span_id"))
        entry_chapter_id, _paragraph = _source_span_position(source_span_id)
        if entry_chapter_id and entry_chapter_id != int(chapter_id):
            continue
        memory_text = _clean_text(entry.get("memory_text"))
        if not memory_text:
            continue
        unit_index = int(entry.get("created_at_unit_index", 0) or 0)
        prefix = _reading_memory_prefix(source_span_id=source_span_id, unit_index=unit_index)
        line = _reading_memory_line(
            prefix=prefix,
            text=memory_text,
            token_estimate=entry.get("token_estimate"),
            origin="hot",
            unit_id=_clean_text(entry.get("entry_id")),
            source_span_id=source_span_id,
            unit_index=unit_index,
        )
        line_tokens = int(line.get("estimated_tokens", 0) or 0)
        if used_tokens + line_tokens > budget_tokens:
            suppressed.append({"source_span_id": source_span_id, "reason": "hot_budget_exceeded"})
            continue
        lines.append(line)
        used_tokens += line_tokens
    return lines, {str(item.get("source_span_id")) for item in lines if item.get("source_span_id")}, suppressed


def _prompt_visible_hot_source_span_ids(
    recent_reading_memory: RecentReadingMemoryState | None,
    *,
    chapter_id: int,
) -> set[str]:
    """Return only hot memory spans that would already enter Digest ReadingMemory."""

    if not isinstance(recent_reading_memory, dict):
        return set()
    _lines, hot_span_ids, _suppressed = _hot_reading_memory_lines(
        recent_reading_memory,
        chapter_id=chapter_id,
    )
    return set(hot_span_ids)


def _retrieved_reading_memory_lines(
    unit_memory_retrieval: dict[str, object] | None,
    *,
    excluded_source_span_ids: set[str],
    budget_tokens: int = 10000,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return runtime-selected long-distance Understanding lines under budget."""

    if not isinstance(unit_memory_retrieval, dict):
        return [], []
    lines: list[dict[str, object]] = []
    suppressed: list[dict[str, object]] = []
    used_tokens = 0
    selected_units = unit_memory_retrieval.get("selected_units", [])
    if not isinstance(selected_units, list):
        return [], []
    for item in selected_units:
        if not isinstance(item, dict):
            continue
        entry = item.get("entry")
        if not isinstance(entry, dict):
            suppressed.append({"unit_id": _clean_text(item.get("unit_id")), "reason": "candidate_missing_entry"})
            continue
        source_span_id = _clean_text(entry.get("source_span_id"))
        unit_id = _clean_text(entry.get("unit_id"))
        if source_span_id in excluded_source_span_ids:
            suppressed.append({"unit_id": unit_id, "source_span_id": source_span_id, "reason": "dedupe_hot_memory"})
            continue
        digest = entry.get("digest")
        digest = dict(digest) if isinstance(digest, dict) else {}
        understanding = digest.get("understanding")
        if not isinstance(understanding, dict):
            suppressed.append({"unit_id": unit_id, "source_span_id": source_span_id, "reason": "candidate_missing_understanding"})
            continue
        memory_text = _clean_text(understanding.get("content"))
        if not memory_text:
            suppressed.append({"unit_id": unit_id, "source_span_id": source_span_id, "reason": "candidate_not_renderable_empty_understanding"})
            continue
        unit_index = int(entry.get("unit_index", item.get("unit_index", 0)) or 0)
        prefix = _reading_memory_prefix(source_span_id=source_span_id, unit_index=unit_index)
        line = _reading_memory_line(
            prefix=prefix,
            text=memory_text,
            token_estimate=understanding.get("token_estimate") or token_estimate_payload(memory_text),
            origin="retrieved",
            unit_id=unit_id,
            source_span_id=source_span_id,
            unit_index=unit_index,
        )
        line["matched_recalls"] = list(item.get("matched_recalls", [])) if isinstance(item.get("matched_recalls"), list) else []
        line_tokens = int(line.get("estimated_tokens", 0) or 0)
        if used_tokens + line_tokens > budget_tokens:
            suppressed.append({"unit_id": unit_id, "source_span_id": source_span_id, "reason": "retrieved_budget_exceeded"})
            continue
        lines.append(line)
        excluded_source_span_ids.add(source_span_id)
        used_tokens += line_tokens
    return lines, suppressed


def _build_digest_reading_memory(
    *,
    recent_reading_memory: RecentReadingMemoryState,
    chapter_id: int,
    unit_memory_retrieval: dict[str, object] | None,
) -> dict[str, object]:
    """Build unified prompt-facing ReadingMemory lines for Digest."""

    hot_lines, hot_span_ids, hot_suppressed = _hot_reading_memory_lines(
        recent_reading_memory,
        chapter_id=chapter_id,
    )
    retrieved_lines, retrieved_suppressed = _retrieved_reading_memory_lines(
        unit_memory_retrieval,
        excluded_source_span_ids=set(hot_span_ids),
    )
    all_lines = [*hot_lines, *retrieved_lines]
    all_lines.sort(key=lambda item: int(item.get("unit_index", 0) or 0), reverse=True)
    total_tokens = sum(int(item.get("estimated_tokens", 0) or 0) for item in all_lines)
    return {
        "lines": [str(item.get("text", "")) for item in all_lines if _clean_text(item.get("text"))],
        "line_records": all_lines,
        "estimated_tokens": total_tokens,
        "hot_line_count": len(hot_lines),
        "retrieved_line_count": len(retrieved_lines),
        "suppressed": [*hot_suppressed, *retrieved_suppressed],
        "budget": {
            "hot_tokens": 5000,
            "retrieved_tokens": 10000,
            "total_tokens": 15000,
            "estimator": "tiktoken_o200k_base_v1",
        },
    }


def _compact_reading_memory_line_record(record: object) -> dict[str, object]:
    if not isinstance(record, dict):
        return {}
    compact: dict[str, object] = {
        "origin": _clean_text(record.get("origin")),
        "unit_id": _clean_text(record.get("unit_id")),
        "source_span_id": _clean_text(record.get("source_span_id")),
        "unit_index": int(record.get("unit_index", 0) or 0),
        "estimated_tokens": int(record.get("estimated_tokens", 0) or 0),
    }
    matched_recalls = record.get("matched_recalls")
    if isinstance(matched_recalls, list):
        compact["matched_recalls"] = [str(item) for item in matched_recalls if str(item or "").strip()]
    return compact


def _current_view_source_texts(current_view_content: Mapping[str, object]) -> list[str]:
    slices = current_view_content.get("paragraph_slices")
    if not isinstance(slices, list):
        return []
    texts: list[str] = []
    for item in slices:
        if isinstance(item, Mapping):
            text = _clean_text(item.get("text"))
            if text:
                texts.append(text)
    return texts


def _current_view_visible_paragraph_ns(current_view_content: Mapping[str, object]) -> list[str]:
    slices = current_view_content.get("paragraph_slices")
    if not isinstance(slices, list):
        return []
    paragraph_ns: list[str] = []
    for item in slices:
        if isinstance(item, Mapping):
            paragraph_n = _clean_text(item.get("paragraph_index"))
            if paragraph_n:
                paragraph_ns.append(paragraph_n)
    return paragraph_ns


def _retrieve_unit_memory_for_prepared_source_unit(
    *,
    output_dir: Path,
    book_id: str,
    prepared_source_unit: PreparedSourceUnit,
    recent_reading_memory: RecentReadingMemoryState,
    memory_retrieval_config: dict[str, object],
) -> dict[str, object]:
    """Run Unit Memory retrieval between Ingest boundary acceptance and Digest."""

    existing = prepared_source_unit.get("unit_memory_retrieval")
    existing_trace = (
        dict(existing.get("trace", {}))
        if isinstance(existing, dict) and isinstance(existing.get("trace"), dict)
        else {}
    )
    existing_degradation = _clean_text(existing_trace.get("degradation_reason"))
    if isinstance(existing, dict) and existing.get("trace") and existing_degradation != "boundary_unresolved":
        return dict(existing)

    selected_source_unit = (
        dict(prepared_source_unit.get("selected_source_unit", {}))
        if isinstance(prepared_source_unit.get("selected_source_unit"), dict)
        else {}
    )
    recalls = normalize_unit_memory_recalls(prepared_source_unit.get("memory_recalls"))
    ingest_trace = prepared_source_unit.get("ingest_trace")
    selected_trace = ingest_trace[-1] if isinstance(ingest_trace, list) and ingest_trace else {}
    recalls_status = _clean_text(prepared_source_unit.get("memory_recalls_status"))
    if not recalls_status and isinstance(selected_trace, dict):
        recalls_status = _clean_text(selected_trace.get("memory_recalls_status"))
    excluded_hot_span_ids = _prompt_visible_hot_source_span_ids(
        recent_reading_memory,
        chapter_id=int(prepared_source_unit.get("chapter_id", 0) or 0),
    )
    if not recalls:
        if recalls_status in {"missing", "malformed", "malformed_payload"}:
            fallback_query = fallback_query_from_source_unit(selected_source_unit)
            fallback_text = _clean_text(fallback_query.get("query_text")) if isinstance(fallback_query, dict) else ""
            if fallback_text:
                fallback_recalls = [
                    {
                        "recall_id": "runtime_fallback",
                        "recall_text": fallback_text,
                        "basis": "runtime_source_text_fallback",
                    }
                ]
                try:
                    return UnitMemoryIndex(output_dir, config=memory_retrieval_config).retrieve_for_recalls(
                        book_id=book_id,
                        recalls=fallback_recalls,
                        query_source="runtime_source_text_fallback",
                        current_unit_index=next_unit_sequence_index(output_dir),
                        excluded_source_unit_span_ids=set(excluded_hot_span_ids),
                        accepted_source_span_id=_clean_text(selected_source_unit.get("source_span_id")),
                        accepted_unit_id=_clean_text(selected_source_unit.get("unit_id")),
                    )
                except Exception as exc:  # pragma: no cover - defensive non-blocking guard
                    trace = {
                        "recorded_at": _timestamp(),
                        "event_type": "unit_memory_retrieval",
                        "book_id": book_id,
                        "recalls": fallback_recalls,
                        "query_source": "runtime_source_text_fallback",
                        "mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
                        "effective_mode": "text_only",
                        "degradation_reason": f"fallback_retrieval_failed:{type(exc).__name__}",
                        "candidate_counts": {"recall_count": 1},
                        "selected_units": [],
                    }
                    record_unit_memory_retrieval_trace(output_dir, trace)
                    return {"recalls": fallback_recalls, "query_source": "runtime_source_text_fallback", "selected_units": [], "trace": trace}
            trace = {
                "recorded_at": _timestamp(),
                "event_type": "unit_memory_retrieval",
                "book_id": book_id,
                "recalls": [],
                "query_source": "skip_unusable_fallback",
                "mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
                "effective_mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
                "degradation_reason": f"{recalls_status}_recalls_without_source_text",
                "candidate_counts": {},
                "selected_units": [],
            }
            record_unit_memory_retrieval_trace(output_dir, trace)
            return {"recalls": [], "query_source": "skip_unusable_fallback", "selected_units": [], "trace": trace}
        trace = {
            "recorded_at": _timestamp(),
            "event_type": "unit_memory_retrieval",
            "book_id": book_id,
            "recalls": [],
            "query_source": "skip_empty_recalls",
            "mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
            "effective_mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
            "degradation_reason": "no_recall",
            "candidate_counts": {},
            "selected_units": [],
        }
        record_unit_memory_retrieval_trace(output_dir, trace)
        return {"recalls": [], "query_source": "skip_empty_recalls", "selected_units": [], "trace": trace}
    try:
        return UnitMemoryIndex(output_dir, config=memory_retrieval_config).retrieve_for_recalls(
            book_id=book_id,
            recalls=recalls,
            query_source="ingest_recalls",
            current_unit_index=next_unit_sequence_index(output_dir),
            excluded_source_unit_span_ids=set(excluded_hot_span_ids),
            accepted_source_span_id=_clean_text(selected_source_unit.get("source_span_id")),
            accepted_unit_id=_clean_text(selected_source_unit.get("unit_id")),
        )
    except Exception as exc:  # pragma: no cover - defensive non-blocking guard
        trace = {
            "recorded_at": _timestamp(),
            "event_type": "unit_memory_retrieval",
            "book_id": book_id,
            "recalls": [dict(item) for item in recalls],
            "query_source": "ingest_recalls",
            "mode": _clean_text(memory_retrieval_config.get("mode")) or "hybrid",
            "effective_mode": "text_only",
            "degradation_reason": f"retrieval_failed:{type(exc).__name__}",
            "candidate_counts": {},
            "selected_units": [],
        }
        record_unit_memory_retrieval_trace(output_dir, trace)
        return {"recalls": [dict(item) for item in recalls], "query_source": "ingest_recalls", "selected_units": [], "trace": trace}


def _resolve_ingest_boundary(
    *,
    chapter: dict[str, object],
    start_cursor: dict[str, object],
    preview: dict[str, object],
    boundary_result: IngestBoundaryResult,
    retry_boundary_result: IngestBoundaryResult | None = None,
) -> tuple[dict[str, object], UnitizeDecision]:
    """Resolve Ingest's unit-boundary object into an accepted unit span."""

    selected_result = dict(retry_boundary_result or boundary_result)
    unit = dict(selected_result.get("unit", {})) if isinstance(selected_result.get("unit"), dict) else {}
    preview_partition = [
        dict(item)
        for item in selected_result.get("preview_partition", [])
        if isinstance(item, dict)
    ] if isinstance(selected_result.get("preview_partition"), list) else []
    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit=unit,
    )
    if _clean_text(resolution.get("status")) == "matched":
        end_cursor = dict(resolution.get("end_cursor", {}))
    else:
        end_cursor = fallback_end_cursor_for_preview(preview)
        resolution = {
            **dict(resolution),
            "status": "fallback",
            "method": _clean_text(resolution.get("method")) or "fallback_current_paragraph_or_preview",
            "end_cursor": end_cursor,
            "fallback_reason": _clean_text(resolution.get("status")) or "unresolved_anchor",
        }

    if not cursor_less_than(start_cursor, end_cursor):
        preview_end = preview.get("preview_end_cursor")
        end_cursor = dict(preview_end) if isinstance(preview_end, dict) else dict(start_cursor)
        resolution = {
            **dict(resolution),
            "status": "fallback",
            "method": "fallback_preview_end",
            "end_cursor": end_cursor,
            "fallback_reason": "resolved_end_cursor_did_not_advance",
        }

    source_span = {
        "start_cursor": dict(start_cursor),
        "end_cursor": dict(end_cursor),
    }
    source_unit = source_unit_from_span(chapter=chapter, source_span=source_span)
    source_id = source_span_id(source_span)
    end_anchor_text = _clean_text(resolution.get("matched_text"))
    if not end_anchor_text:
        end_anchor_text = _clean_text(unit.get("end_at"))
    preview_partition_audit_result = resolve_preview_partition_audit(
        preview=preview,
        start_cursor=start_cursor,
        preview_partition=preview_partition,
    ) if preview_partition else {"status": "missing", "partitions": []}
    preview_partition_audit = [
        dict(item)
        for item in preview_partition_audit_result.get("partitions", [])
        if isinstance(item, dict)
    ] if isinstance(preview_partition_audit_result.get("partitions"), list) else []
    unitize_decision: UnitizeDecision = {
        "unit": unit,
        "preview_partition": preview_partition,
        "preview_partition_audit": preview_partition_audit,
        "preview_partition_audit_status": _clean_text(preview_partition_audit_result.get("status")) or "missing",
        "end_anchor_text": end_anchor_text,
        "source_span": source_span,
        "source_span_id": source_id,
        "preview_range": {
            "start_cursor": dict(preview.get("preview_start_cursor", {}))
            if isinstance(preview.get("preview_start_cursor"), dict)
            else {},
            "end_cursor": dict(preview.get("preview_end_cursor", {}))
            if isinstance(preview.get("preview_end_cursor"), dict)
            else {},
            "preview_end_reason": _clean_text(preview.get("preview_end_reason")),
            "estimated_token_count": int(preview.get("estimated_token_count", 0) or 0),
            "preview_token_estimator": _clean_text(preview.get("preview_token_estimator")),
        },
        "reason": _clean_text(selected_result.get("reason")),
        "resolution": resolution,
    }
    source_unit["unitize_decision"] = dict(unitize_decision)
    return source_unit, unitize_decision


def _accept_ingest_boundary(
    *,
    chapter: dict[str, object],
    start_cursor: dict[str, object],
    preview: dict[str, object],
    boundary_result: IngestBoundaryResult,
    retry_boundary_result: IngestBoundaryResult | None = None,
) -> tuple[dict[str, object], UnitizeDecision, list[IngestTraceEntry]]:
    """Accept an Ingest boundary result as a runtime source unit."""

    selected_source_unit, unitize_decision = _resolve_ingest_boundary(
        chapter=chapter,
        start_cursor=start_cursor,
        preview=preview,
        boundary_result=boundary_result,
        retry_boundary_result=retry_boundary_result,
    )
    selected_boundary = retry_boundary_result if retry_boundary_result is not None else boundary_result
    selected_boundary["end_anchor_text"] = _clean_text(unitize_decision.get("end_anchor_text"))
    selected_boundary["source_span_id"] = _clean_text(unitize_decision.get("source_span_id"))
    selected_boundary["source_span"] = dict(unitize_decision.get("source_span", {}))
    selected_boundary["resolution"] = dict(unitize_decision.get("resolution", {}))
    selected_boundary["preview_partition_audit"] = [
        dict(item)
        for item in unitize_decision.get("preview_partition_audit", [])
        if isinstance(item, dict)
    ] if isinstance(unitize_decision.get("preview_partition_audit"), list) else []
    selected_boundary["preview_partition_audit_status"] = _clean_text(
        unitize_decision.get("preview_partition_audit_status")
    )
    ingest_trace = [_ingest_trace_entry(boundary_result)]
    if retry_boundary_result is not None:
        ingest_trace.append(_ingest_trace_entry(retry_boundary_result))
    return selected_source_unit, unitize_decision, ingest_trace


def prepare_next_source_unit_for_read(
    *,
    current_chapter: dict[str, object],
    current_cursor: dict[str, object],
    local_buffer: LocalBufferState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
    local_continuity: LocalContinuityState,
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path | None,
    book_title: str,
    author: str,
    book_id: str = "",
    memory_retrieval_config: dict[str, object] | None = None,
) -> PreparedSourceUnit:
    """Prepare the next forward source unit that should be read."""

    preparation = _build_ingest_boundary_preparation(
        current_chapter=current_chapter,
        current_cursor=current_cursor,
        reader_policy=reader_policy,
    )
    preview = dict(preparation.get("preview", {})) if isinstance(preparation.get("preview"), dict) else {}
    source_cursor = dict(preparation.get("source_cursor", {})) if isinstance(preparation.get("source_cursor"), dict) else {}
    chapter_id = int(preparation.get("chapter_id", 0) or 0)
    chapter_ref = _clean_text(preparation.get("chapter_ref"))
    current_view_position = (
        dict(preparation.get("current_view_position", {}))
        if isinstance(preparation.get("current_view_position"), dict)
        else {}
    )
    current_view_content = (
        dict(preparation.get("current_view_content", {}))
        if isinstance(preparation.get("current_view_content"), dict)
        else {}
    )
    current_source_texts = _current_view_source_texts(current_view_content)
    current_visible_paragraph_ns = _current_view_visible_paragraph_ns(current_view_content)
    tool_retrieval_results: list[dict[str, object]] = []

    def _unit_memory_tool_handler(args: Mapping[str, object]) -> Mapping[str, object]:
        preflight_errors = validate_ingest_unit_memory_tool_args(
            dict(args),
            current_source_texts=current_source_texts,
            current_visible_paragraph_ns=current_visible_paragraph_ns,
        )
        if preflight_errors:
            return {
                "status": "contract_violation",
                "effective_mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "retrieval_summary": {"recall_count": 0, "candidate_unit_count": 0, "selected_unit_count": 0},
                "degradation_reason": "; ".join(preflight_errors),
            }
        recalls = normalize_unit_memory_recalls(args.get("memory_recalls"))
        tool_call_id = _clean_text(args.get("_tool_call_id"))
        if not recalls:
            return {
                "status": "no_recall",
                "effective_mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "retrieval_summary": {"recall_count": 0, "candidate_unit_count": 0, "selected_unit_count": 0},
                "degradation_reason": "",
            }
        unit_for_tool = dict(args.get("unit", {})) if isinstance(args.get("unit"), Mapping) else {}
        resolution_for_tool = resolve_ingest_unit_boundary(
            preview=preview,
            unit=unit_for_tool,
        )
        if _clean_text(resolution_for_tool.get("status")) != "matched":
            trace = {
                "recorded_at": _timestamp(),
                "event_type": "unit_memory_retrieval",
                "book_id": book_id,
                "recalls": [dict(item) for item in recalls],
                "query_source": "tool_boundary_unresolved",
                "tool_call_id": tool_call_id,
                "mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "effective_mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "degradation_reason": "boundary_unresolved",
                "boundary_resolution": dict(resolution_for_tool),
                "candidate_counts": {},
                "selected_units": [],
            }
            if output_dir is not None:
                record_unit_memory_retrieval_trace(output_dir, trace)
            result = {"recalls": [dict(item) for item in recalls], "selected_units": [], "trace": trace}
            tool_retrieval_results.append(result)
            return {
                "status": "boundary_unresolved",
                "effective_mode": trace["effective_mode"],
                "boundary_resolution": dict(resolution_for_tool),
                "retrieval_summary": {"recall_count": len(recalls), "candidate_unit_count": 0, "selected_unit_count": 0},
                "degradation_reason": "boundary_unresolved",
            }
        if output_dir is None or not book_id:
            return {
                "status": "degraded",
                "effective_mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "boundary_resolution": dict(resolution_for_tool),
                "retrieval_summary": {"recall_count": len(recalls), "candidate_unit_count": 0, "selected_unit_count": 0},
                "degradation_reason": "missing_runtime_retrieval_context",
            }
        tool_source_span_id = ""
        if isinstance(resolution_for_tool.get("end_cursor"), dict):
            tool_source_span_id = source_span_id(
                {
                    "start_cursor": dict(source_cursor),
                    "end_cursor": dict(resolution_for_tool.get("end_cursor", {})),
                }
            )
        try:
            retrieval_result = UnitMemoryIndex(output_dir, config=memory_retrieval_config or {}).retrieve_for_recalls(
                book_id=book_id,
                recalls=recalls,
                query_source="tool_retrieve_unit_memory",
                current_unit_index=next_unit_sequence_index(output_dir),
                excluded_source_unit_span_ids=_prompt_visible_hot_source_span_ids(
                    recent_reading_memory,
                    chapter_id=chapter_id,
                ),
                tool_call_id=tool_call_id,
                accepted_source_span_id=tool_source_span_id,
            )
        except Exception as exc:  # pragma: no cover - defensive tool guard
            trace = {
                "recorded_at": _timestamp(),
                "event_type": "unit_memory_retrieval",
                "book_id": book_id,
                "recalls": [dict(item) for item in recalls],
                "query_source": "tool_retrieve_unit_memory",
                "tool_call_id": tool_call_id,
                "mode": _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
                "effective_mode": "text_only",
                "degradation_reason": f"retrieval_failed:{type(exc).__name__}",
                "boundary_resolution": dict(resolution_for_tool),
                "candidate_counts": {},
                "selected_units": [],
            }
            record_unit_memory_retrieval_trace(output_dir, trace)
            retrieval_result = {"recalls": [dict(item) for item in recalls], "selected_units": [], "trace": trace}
        retrieval_result = dict(retrieval_result)
        retrieval_result["boundary_resolution"] = dict(resolution_for_tool)
        tool_retrieval_results.append(retrieval_result)
        trace = dict(retrieval_result.get("trace", {})) if isinstance(retrieval_result.get("trace"), dict) else {}
        candidate_counts = trace.get("candidate_counts") if isinstance(trace.get("candidate_counts"), dict) else {}
        selected_units = retrieval_result.get("selected_units", [])
        selected_count = len(selected_units) if isinstance(selected_units, list) else 0
        degradation_reason = _clean_text(retrieval_result.get("degradation_reason") or trace.get("degradation_reason"))
        return {
            "status": "ok" if selected_count else "no_match",
            "effective_mode": _clean_text(retrieval_result.get("effective_mode")) or _clean_text((memory_retrieval_config or {}).get("mode")) or "hybrid",
            "boundary_resolution": dict(resolution_for_tool),
            "retrieval_summary": {
                "recall_count": len(recalls),
                "candidate_unit_count": int(candidate_counts.get("candidate_units", 0) or 0),
                "selected_unit_count": selected_count,
            },
            "degradation_reason": degradation_reason,
        }

    boundary_result = _call_ingest(
        current_view_position=current_view_position,
        current_view_content=current_view_content,
        output_dir=output_dir,
        book_title=book_title,
        author=author,
        unit_memory_tool_handler=_unit_memory_tool_handler,
    )
    resolution = resolve_ingest_unit_boundary(
        preview=preview,
        unit=dict(boundary_result.get("unit", {})) if isinstance(boundary_result.get("unit"), dict) else {},
    )
    retry_boundary_result: IngestBoundaryResult | None = None
    if _clean_text(resolution.get("status")) != "matched":
        retry_position = dict(current_view_position)
        retry_position.update(
            {
                "retry": True,
                "previous_unit": dict(boundary_result.get("unit", {}))
                if isinstance(boundary_result.get("unit"), dict)
                else {},
                "previous_resolution": dict(resolution),
                "retry_instruction": (
                    "Return a visible unit boundary object: set unit.end_paragraph_n to a visible Paragraph n "
                    "and unit.end_at to paragraph_end or a longer unique exact tail quote inside that paragraph. "
                    "Also return preview_partition as the whole visible preview map, with preview_partition[0] "
                    "matching the corrected unit boundary exactly."
                ),
            }
        )
        retry_boundary_result = _call_ingest(
            current_view_position={
                **retry_position,
            },
            current_view_content=current_view_content,
            output_dir=output_dir,
            book_title=book_title,
            author=author,
            unit_memory_tool_handler=_unit_memory_tool_handler,
        )
    selected_source_unit, unitize_decision, ingest_trace = _accept_ingest_boundary(
        chapter=current_chapter,
        start_cursor=dict(source_cursor),
        preview=dict(preview),
        boundary_result=boundary_result,
        retry_boundary_result=retry_boundary_result,
    )
    compat_selected_sentences = _compat_unit_sentences_for_source_span(
        current_chapter,
        dict(unitize_decision.get("source_span", {})) if isinstance(unitize_decision.get("source_span"), dict) else {},
    )
    selected_boundary = retry_boundary_result if retry_boundary_result is not None else boundary_result
    memory_recalls = normalize_unit_memory_recalls(selected_boundary.get("memory_recalls"))
    memory_recalls_status = _clean_text(selected_boundary.get("memory_recalls_status")) or "missing"
    unit_memory_retrieval = (
        dict(tool_retrieval_results[-1])
        if tool_retrieval_results and _clean_text(selected_boundary.get("tool_loop_status")) == "tool_called"
        else {}
    )
    return {
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "selected_unit_sentences": compat_selected_sentences,
        "selected_source_unit": selected_source_unit,
        "preview": dict(preview),
        "unitize_decision": unitize_decision,  # type: ignore[typeddict-item]
        "ingest_trace": ingest_trace,
        "memory_recalls": memory_recalls,
        "memory_recalls_status": memory_recalls_status,
        "unit_memory_retrieval": unit_memory_retrieval,
    }


def _source_ref_from_surfaced_reaction(
    *,
    surfaced_reaction: dict[str, object] | None,
    source_unit: dict[str, object] | None = None,
    reading_impression: str = "",
) -> dict[str, object]:
    """Build one deterministic source ref from a Digest-owned surfaced reaction."""

    source_quote = _clean_text((surfaced_reaction or {}).get("source_quote") or (surfaced_reaction or {}).get("anchor_quote"))
    if isinstance(source_unit, dict) and source_unit:
        return source_ref_from_unit(source_unit, quote=source_quote, role="reaction_anchor")
    return source_ref_from_span(
        {},
        quote=source_quote or _clean_text(reading_impression),
        role="reaction_anchor",
        resolution={"status": "missing_source_unit"},
    )


def _normalize_memory_uptake_ops_source_refs(
    memory_uptake_ops: object,
    *,
    source_unit: dict[str, object] | None,
) -> list[dict[str, object]]:
    """Resolve Digest-proposed source quotes into inline source refs before settlement."""

    if not isinstance(memory_uptake_ops, list):
        return []
    normalized: list[dict[str, object]] = []

    def _unit_span() -> dict[str, object]:
        source_span = source_unit.get("source_span") if isinstance(source_unit, dict) else {}
        return dict(source_span) if isinstance(source_span, dict) else {}

    def _unit_span_id() -> str:
        if not isinstance(source_unit, dict):
            return ""
        return _clean_text(source_unit.get("source_span_id")) or source_span_id(_unit_span())

    def _first_ref_span(refs: object) -> tuple[str, dict[str, object]]:
        if not isinstance(refs, list):
            return "", {}
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            ref_span = ref.get("source_span")
            span = dict(ref_span) if isinstance(ref_span, dict) else {}
            span_id = _clean_text(ref.get("source_span_id")) or source_span_id(span)
            if span_id or span:
                return span_id, span
        return "", {}

    for item in memory_uptake_ops:
        if not isinstance(item, dict):
            continue
        operation = dict(item)
        payload = dict(operation.get("payload", {})) if isinstance(operation.get("payload"), dict) else {}
        operation_type = _clean_text(operation.get("op") or operation.get("operation_type")).lower().replace("-", "_")
        target_store = _clean_text(operation.get("target_store") or operation.get("effective_target_store"))
        if target_store == "active_attention":
            if "tension_from" not in payload and _clean_text(payload.get("question_from")):
                payload["tension_from"] = _clean_text(payload.get("question_from"))
            if "tension_focus" not in payload:
                for legacy_key in ("driving_question", "statement", "answer_boundary"):
                    if _clean_text(payload.get(legacy_key)):
                        payload["tension_focus"] = _clean_text(payload.get(legacy_key))
                        break
            if "working_interpretation" not in payload and "working_answer" in payload:
                payload["working_interpretation"] = _clean_text(payload.get("working_answer"))
            for legacy_key in (
                "question_from",
                "driving_question",
                "working_answer",
                "answer_source_refs",
                "statement",
                "answer_boundary",
            ):
                payload.pop(legacy_key, None)

        source_quote = _clean_text(payload.get("source_quote") or payload.get("quote") or payload.get("evidence_quote"))
        source_role = _clean_text(payload.get("source_role")) or "support"
        if target_store == "recent_reading_memory":
            for recent_memory_source_key in (
                "source_refs",
                "development_source_refs",
                "answer_source_refs",
                "source_quote",
                "quote",
                "evidence_quote",
                "source_role",
                "development_source_quote",
                "answer_source_quote",
                "development_source_role",
                "answer_source_role",
            ):
                payload.pop(recent_memory_source_key, None)
            operation["payload"] = payload
            normalized.append(operation)
            continue
        if isinstance(source_unit, dict) and source_unit and source_quote:
            payload["source_refs"] = [source_ref_from_unit(source_unit, quote=source_quote, role=source_role)]
        elif "source_refs" in payload:
            payload.pop("source_refs", None)
        development_source_quote = _clean_text(payload.get("development_source_quote") or payload.get("answer_source_quote"))
        development_source_role = (
            _clean_text(payload.get("development_source_role") or payload.get("answer_source_role"))
            or "development_support"
        )
        if isinstance(source_unit, dict) and source_unit and development_source_quote:
            payload["development_source_refs"] = [
                source_ref_from_unit(source_unit, quote=development_source_quote, role=development_source_role)
            ]
        else:
            payload.pop("development_source_refs", None)
        payload.pop("answer_source_refs", None)
        if target_store == "active_attention":
            unit_span = _unit_span()
            unit_span_id = _unit_span_id()
            if operation_type in {"append", "create", "reactivate"}:
                source_span_ref_id, source_span_ref = _first_ref_span(payload.get("source_refs"))
                payload.setdefault("opened_at_source_span_id", source_span_ref_id or unit_span_id)
                payload.setdefault("opened_at_source_span", source_span_ref or unit_span)
                payload.setdefault("opened_at_unit_span_id", unit_span_id)
                payload.setdefault("opened_at_unit_span", unit_span)
            if operation_type == "resolve":
                if not _clean_text(payload.get("answered_reason")):
                    payload["answered_reason"] = _clean_text(operation.get("reason"))
                answer_span_ref_id, answer_span_ref = _first_ref_span(payload.get("development_source_refs"))
                source_span_ref_id, source_span_ref = _first_ref_span(payload.get("source_refs"))
                payload.setdefault("answered_at_source_span_id", answer_span_ref_id or source_span_ref_id or unit_span_id)
                payload.setdefault("answered_at_source_span", answer_span_ref or source_span_ref or unit_span)
                payload.setdefault("answered_at_unit_span_id", unit_span_id)
                payload.setdefault("answered_at_unit_span", unit_span)
            if operation_type == "close":
                if not _clean_text(payload.get("closed_reason")):
                    payload["closed_reason"] = _clean_text(operation.get("reason"))
                source_span_ref_id, source_span_ref = _first_ref_span(payload.get("source_refs"))
                payload.setdefault("closed_at_source_span_id", source_span_ref_id or unit_span_id)
                payload.setdefault("closed_at_source_span", source_span_ref or unit_span)
                payload.setdefault("closed_at_unit_span_id", unit_span_id)
                payload.setdefault("closed_at_unit_span", unit_span)
        operation["payload"] = payload
        normalized.append(operation)
    return normalized


def _persist_surfaced_reactions(
    *,
    digest_result: DigestResult,
    chosen_unit_sentences: list[dict[str, object]],
    focal_sentence: dict[str, object],
    chapter_id: int,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    reaction_records: ReactionRecordsState,
    output_dir: Path,
    source_unit: dict[str, object] | None = None,
) -> tuple[ReactionRecordsState, list[AnchoredReactionRecord], dict[str, object] | None]:
    """Persist Digest-owned surfaced reactions through one canonical builder path."""

    emitted_reactions: list[AnchoredReactionRecord] = []
    current_source_ref = None
    surfaced_reactions = [
        dict(item)
        for item in digest_result.get("surfaced_reactions", [])
        if isinstance(item, dict)
    ]
    chapter_reaction_count = len(reaction_records_for_chapter(reaction_records, chapter_ref=chapter_ref))
    for index, surfaced_reaction in enumerate(surfaced_reactions, start=1):
        current_source_ref = _source_ref_from_surfaced_reaction(
            surfaced_reaction=surfaced_reaction,
            source_unit=source_unit,
            reading_impression=_clean_text(digest_result.get("reading_impression")),
        )
        emitted_at = _clean_text(source_unit.get("source_span_id")) if isinstance(source_unit, dict) else ""
        emitted_reaction = build_reaction_record_from_surfaced_reaction(
            reaction=surfaced_reaction,
            primary_source_ref=current_source_ref,
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            emitted_at_source_span_id=emitted_at or _sentence_id(focal_sentence),
            compatibility_section_ref=_compatibility_section_ref_for_source(chapter_id, source_unit)
            if isinstance(source_unit, dict) and source_unit
            else _compatibility_section_ref(chapter_id, focal_sentence),
            ordinal=chapter_reaction_count + index,
        )
        if emitted_reaction is None:
            continue
        reaction_records = append_reaction_record(reaction_records, emitted_reaction)
        emitted_reactions.append(emitted_reaction)
        append_activity_event(
            output_dir,
            {
                "type": "reaction_emitted",
                "stream": "mindstream",
                "kind": "thought",
                "visibility": "default",
                "message": _clean_text(emitted_reaction.get("thought")),
                "chapter_id": chapter_id,
                "chapter_ref": chapter_ref,
                "segment_ref": _compatibility_section_ref_for_source(chapter_id, source_unit)
                if isinstance(source_unit, dict) and source_unit
                else _compatibility_section_ref(chapter_id, focal_sentence),
                "source_quote": _clean_text(emitted_reaction.get("source_quote")),
                "reading_locus": {
                    **source_locus_from_unit(source_unit),
                    "chapter_id": chapter_id,
                    "chapter_ref": chapter_ref,
                }
                if isinstance(source_unit, dict) and source_unit
                else _reading_locus(chapter_id, chapter_ref, focal_sentence, local_buffer),
                "active_reaction_id": _clean_text(emitted_reaction.get("reaction_id")),
                "reaction_types": [compat_reaction_family(emitted_reaction)],
                "current_excerpt": _clean_text(source_unit.get("source_text") if isinstance(source_unit, dict) else focal_sentence.get("text"))[:220],
            },
        )
    return reaction_records, emitted_reactions, current_source_ref


def _build_runtime_continuation_capsule(
    *,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
) -> dict[str, object]:
    """Build the persisted continuation capsule from the current live primary state."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[],
        local_buffer=local_buffer,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )
    capsule = carry_forward_context.get("continuation_capsule", {})
    return dict(capsule) if isinstance(capsule, dict) else {}


def _run_digest_for_source_unit(
    *,
    chapter: dict[str, object],
    unitize_decision: UnitizeDecision,
    chosen_unit_sentences: list[dict[str, object]] | None = None,
    current_unit_source: dict[str, object] | None = None,
    local_buffer: LocalBufferState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState,
    reflective_frames: ReflectiveFramesState,
    knowledge_activations: KnowledgeActivationsState,
    reaction_records: ReactionRecordsState,
    output_language: str,
    output_dir: Path | None,
    book_title: str,
    author: str,
    chapter_id: int,
    chapter_ref: str,
    ingest_trace: list[dict[str, object]] | None = None,
    reading_memory_lines: list[str] | None = None,
) -> tuple[DigestResult, list[dict[str, str]]]:
    """Run Digest for the accepted source unit and persist the read-cycle audit."""

    chosen_unit_sentences = [dict(sentence) for sentence in (chosen_unit_sentences or []) if isinstance(sentence, dict)]
    current_unit_source = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else None
    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[
            _clean_text(sentence.get("sentence_id"))
            for sentence in chosen_unit_sentences
            if _clean_text(sentence.get("sentence_id"))
        ],
        local_buffer=local_buffer,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        continuation_capsule=continuation_capsule,
    )
    llm_fallbacks: list[dict[str, str]] = []
    try:
        digest_result = _call_digest(
            current_unit_source=current_unit_source,
            current_unit_sentences=chosen_unit_sentences,
            reading_memory_lines=reading_memory_lines,
            carry_forward_context=carry_forward_context,
            output_language=output_language,
            output_dir=output_dir,
            book_title=book_title,
            author=author,
            chapter_title=_clean_text(chapter.get("title")),
        )
    except ReaderLLMError as exc:
        llm_fallbacks.append({"node": "digest", "problem_code": exc.problem_code})
        digest_result = {
            "reading_impression": "",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
        }
    digest_result["memory_uptake_ops"] = _normalize_memory_uptake_ops_source_refs(
        digest_result.get("memory_uptake_ops", []),
        source_unit=current_unit_source,
    )

    record_read(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        unitize_decision=unitize_decision,
        source_unit=current_unit_source,
        carry_forward_context=carry_forward_context,
        digest_result=digest_result,
        stop_reason="digest_complete",
        llm_fallbacks=llm_fallbacks,
        ingest_trace=ingest_trace,
    )
    return digest_result, llm_fallbacks


def _settle_next_unit(
    *,
    prepared_source_unit: PreparedSourceUnit,
    chapter_lookup: dict[int, dict[str, object]],
    local_buffer: LocalBufferState,
    local_continuity: LocalContinuityState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState,
    reflective_frames: ReflectiveFramesState,
    knowledge_activations: KnowledgeActivationsState,
    reaction_records: ReactionRecordsState,
    reconsolidation_records: dict[str, object],
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path,
    provisioned: ProvisionedBook,
    bundle: dict[str, dict[str, object]],
    memory_retrieval_config: dict[str, object],
    reading_queue_stage: str,
    total_chapters: int,
    completed_chapters: int,
    memory_quality_probe_config: dict[str, object] | None,
    ordered_probe_sentence_ids: list[str],
    meaning_units_in_chapter: list[dict[str, object]] | None,
    already_ingested_sentence_ids: set[str] | None = None,
    capture_memory_probe: bool = False,
) -> dict[str, object]:
    """Read and settle one runtime-prepared source unit."""

    chapter_id = int(prepared_source_unit.get("chapter_id", 0) or 0)
    chapter = chapter_lookup.get(chapter_id)
    if not isinstance(chapter, dict):
        return {
            "local_buffer": local_buffer,
            "local_continuity": local_continuity,
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "reflective_frames": reflective_frames,
            "knowledge_activations": knowledge_activations,
            "reaction_records": reaction_records,
            "reconsolidation_records": reconsolidation_records,
            "bundle": bundle,
            "emitted_reactions": [],
            "current_source_ref": None,
            "focal_sentence": {},
            "units_read_delta": 0,
            "touched_chapter_ids": [],
        }

    chapter_ref = _clean_text(prepared_source_unit.get("chapter_ref")) or _chapter_ref(chapter)
    chosen_unit_sentences = [
        dict(sentence)
        for sentence in prepared_source_unit.get("selected_unit_sentences", [])
        if isinstance(sentence, dict)
    ]
    selected_source_unit = (
        dict(prepared_source_unit.get("selected_source_unit", {}))
        if isinstance(prepared_source_unit.get("selected_source_unit"), dict)
        else {}
    )
    has_selected_source_unit = bool(selected_source_unit)
    if not chosen_unit_sentences and not has_selected_source_unit:
        return {
            "local_buffer": local_buffer,
            "local_continuity": local_continuity,
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "reflective_frames": reflective_frames,
            "knowledge_activations": knowledge_activations,
            "reaction_records": reaction_records,
            "reconsolidation_records": reconsolidation_records,
            "bundle": bundle,
            "emitted_reactions": [],
            "current_source_ref": None,
            "focal_sentence": {},
            "units_read_delta": 0,
            "touched_chapter_ids": [],
        }

    unitize_decision = dict(prepared_source_unit.get("unitize_decision", {}))
    focal_sentence = chosen_unit_sentences[-1] if chosen_unit_sentences else {}
    focal_sentence_id = _sentence_id(focal_sentence) if focal_sentence else ""
    source_span = (
        dict(selected_source_unit.get("source_span", {}))
        if isinstance(selected_source_unit.get("source_span"), dict)
        else {}
    )
    source_id = _clean_text(selected_source_unit.get("source_span_id")) or source_span_id(source_span)
    if has_selected_source_unit:
        chosen_unit_sentences = _compat_unit_sentences_for_source_span(chapter, source_span)
        focal_sentence = chosen_unit_sentences[-1] if chosen_unit_sentences else {}
        focal_sentence_id = _sentence_id(focal_sentence) if focal_sentence else ""
        local_continuity["mainline_cursor"] = _shared_cursor_for_source_span(source_span)
        local_continuity["current_source_span"] = dict(source_span)
        local_continuity["current_source_span_id"] = source_id
    record_unitization(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        unitize_decision=unitize_decision,
    )

    current_activity = (
        _current_activity_from_source_unit(
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            source_unit=selected_source_unit,
            local_buffer=local_buffer,
        )
        if has_selected_source_unit
        else _current_activity(
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            sentence=focal_sentence,
            local_buffer=local_buffer,
        )
    )
    if reading_queue_stage:
        current_activity["reading_queue_stage"] = reading_queue_stage
    position_payload = persist_reading_position(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        source_cursor=dict(source_span.get("end_cursor", {}))
        if has_selected_source_unit and isinstance(source_span.get("end_cursor"), dict)
        else None,
        status="running",
        phase="reading",
    )
    if isinstance(position_payload.get("local_continuity"), dict):
        local_continuity = position_payload["local_continuity"]  # type: ignore[assignment]
        bundle["local_continuity"] = local_continuity
        _save_runtime_bundle(output_dir, bundle)
    write_run_state(
        output_dir,
        build_run_state(
            book_title=provisioned.title,
            stage="deep_reading",
            total_chapters=total_chapters,
            completed_chapters=completed_chapters,
            current_chapter_id=chapter_id,
            current_chapter_ref=chapter_ref,
            current_segment_ref=_compatibility_section_ref_for_source(chapter_id, selected_source_unit)
            if has_selected_source_unit
            else _compatibility_section_ref(chapter_id, focal_sentence),
            current_reading_activity=current_activity,
            current_phase_step="reading",
            resume_available=True,
            last_checkpoint_at=load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("last_checkpoint_at"),
        ),
    )

    unit_memory_retrieval = _retrieve_unit_memory_for_prepared_source_unit(
        output_dir=output_dir,
        book_id=provisioned.output_dir.name,
        prepared_source_unit=prepared_source_unit,
        recent_reading_memory=recent_reading_memory,
        memory_retrieval_config=memory_retrieval_config,
    )
    prepared_source_unit["unit_memory_retrieval"] = unit_memory_retrieval  # type: ignore[typeddict-item]
    reading_memory = _build_digest_reading_memory(
        recent_reading_memory=recent_reading_memory,
        chapter_id=chapter_id,
        unit_memory_retrieval=unit_memory_retrieval,
    )
    unit_memory_retrieval["reading_memory_lines"] = list(reading_memory.get("line_records", []))  # type: ignore[index]
    reading_memory_line_records = (
        list(reading_memory.get("line_records", [])) if isinstance(reading_memory.get("line_records"), list) else []
    )
    rendered_retrieved_units = [
        _compact_reading_memory_line_record(record)
        for record in reading_memory_line_records
        if isinstance(record, dict) and _clean_text(record.get("origin")) == "retrieved"
    ]
    rendered_hot_units = [
        _compact_reading_memory_line_record(record)
        for record in reading_memory_line_records
        if isinstance(record, dict) and _clean_text(record.get("origin")) == "hot"
    ]
    record_unit_memory_retrieval_trace(
        output_dir,
        {
            "recorded_at": _timestamp(),
            "event_type": "unit_memory_reading_memory_selection",
            "book_id": provisioned.output_dir.name,
            "source_span_id": source_id if has_selected_source_unit else "",
            "line_count": len(reading_memory.get("lines", [])) if isinstance(reading_memory.get("lines"), list) else 0,
            "hot_line_count": int(reading_memory.get("hot_line_count", 0) or 0),
            "retrieved_line_count": int(reading_memory.get("retrieved_line_count", 0) or 0),
            "estimated_tokens": int(reading_memory.get("estimated_tokens", 0) or 0),
            "budget": dict(reading_memory.get("budget", {})) if isinstance(reading_memory.get("budget"), dict) else {},
            "suppressed": list(reading_memory.get("suppressed", [])) if isinstance(reading_memory.get("suppressed"), list) else [],
            "rendered_retrieved_units": rendered_retrieved_units,
            "rendered_retrieved_unit_ids": [
                str(item.get("unit_id"))
                for item in rendered_retrieved_units
                if _clean_text(item.get("unit_id"))
            ],
            "rendered_hot_units": rendered_hot_units,
        },
    )

    digest_result, digest_fallbacks = _run_digest_for_source_unit(
        chapter=chapter,
        chosen_unit_sentences=chosen_unit_sentences,
        current_unit_source=selected_source_unit if has_selected_source_unit else None,
        unitize_decision=unitize_decision,  # type: ignore[arg-type]
        local_buffer=local_buffer,
        continuation_capsule=continuation_capsule,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        knowledge_activations=knowledge_activations,
        reaction_records=reaction_records,
        output_language=output_language,
        output_dir=output_dir,
        book_title=provisioned.title,
        author=provisioned.author,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        ingest_trace=_compact_ingest_trace(prepared_source_unit.get("ingest_trace")),
        reading_memory_lines=list(reading_memory.get("lines", [])) if isinstance(reading_memory.get("lines"), list) else [],
    )
    for fallback in digest_fallbacks:
        if not isinstance(fallback, dict):
            continue
        append_activity_event(
            output_dir,
            {
                "type": "llm_fallback",
                "stream": "mindstream",
                "kind": "transition",
                "visibility": "hidden",
                "message": f"Digest fallback for {_clean_text(fallback.get('node')) or 'unknown_node'}.",
                "chapter_id": chapter_id,
                "chapter_ref": chapter_ref,
                "segment_ref": _compatibility_section_ref_for_source(chapter_id, selected_source_unit)
                if has_selected_source_unit
                else _compatibility_section_ref(chapter_id, focal_sentence),
                "reading_locus": {
                    **source_locus_from_unit(selected_source_unit),
                    "chapter_id": chapter_id,
                    "chapter_ref": chapter_ref,
                }
                if has_selected_source_unit
                else _reading_locus(chapter_id, chapter_ref, focal_sentence, local_buffer),
                "current_excerpt": _clean_text(selected_source_unit.get("source_text") if has_selected_source_unit else focal_sentence.get("text"))[:220],
                "problem_code": _clean_text(fallback.get("problem_code")),
            },
        )

    memory_uptake_ops = digest_result.get("memory_uptake_ops", [])
    before_active_attention = active_attention
    before_recent_reading_memory = recent_reading_memory
    before_reaction_records = reaction_records
    active_attention = apply_active_attention_operations(
        active_attention,
        memory_uptake_ops,
    )
    unit_sequence_index = next_unit_sequence_index(output_dir)
    recent_reading_memory = apply_recent_reading_memory_operations(
        recent_reading_memory,
        memory_uptake_ops,
        source_unit_span_id=source_id if has_selected_source_unit else "",
        created_at_unit_index=unit_sequence_index,
    )
    reaction_records, emitted_reactions, current_source_ref = _persist_surfaced_reactions(
        digest_result=digest_result,
        chosen_unit_sentences=chosen_unit_sentences,
        focal_sentence=focal_sentence,
        source_unit=selected_source_unit if has_selected_source_unit else None,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        local_buffer=local_buffer,
        reaction_records=reaction_records,
        output_dir=output_dir,
    )
    record_settlement(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        unit_sentence_ids=[
            _clean_text(item.get("sentence_id")) for item in chosen_unit_sentences if _clean_text(item.get("sentence_id"))
        ],
        focal_sentence_id=focal_sentence_id,
        source_span=source_span if has_selected_source_unit else None,
        source_span_id=source_id if has_selected_source_unit else "",
        memory_uptake_ops=memory_uptake_ops,
        before_active_attention=before_active_attention,
        after_active_attention=active_attention,
        before_recent_reading_memory=before_recent_reading_memory,
        after_recent_reading_memory=recent_reading_memory,
        before_reaction_records=before_reaction_records,
        after_reaction_records=reaction_records,
        emitted_reaction_ids=[_clean_text(item.get("reaction_id")) for item in emitted_reactions],
    )
    if has_selected_source_unit:
        unit_record = append_unit_span_record(
            output_dir,
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            source_unit=selected_source_unit,
            preview=dict(prepared_source_unit.get("preview", {})) if isinstance(prepared_source_unit.get("preview"), dict) else {},
            end_anchor_text=_clean_text(unitize_decision.get("end_anchor_text")),
            resolution=dict(unitize_decision.get("resolution", {})) if isinstance(unitize_decision.get("resolution"), dict) else {},
        )
        selected_source_unit["unit_id"] = _clean_text(unit_record.get("unit_id"))
        selected_source_unit["sequence_index"] = int(unit_record.get("sequence_index", 0) or 0)
        retrieval_mode: MemoryRetrievalMode = (
            "text_only" if _clean_text(memory_retrieval_config.get("mode")) == "text_only" else "hybrid"
        )
        try:
            unit_memory_entry = build_unit_memory_entry(
                book_id=provisioned.output_dir.name,
                chapter_id=chapter_id,
                chapter_ref=chapter_ref,
                source_unit=selected_source_unit,
                digest_result=digest_result,
                memory_retrieval_mode=retrieval_mode,
            )
            UnitMemoryIndex(output_dir, config=memory_retrieval_config).write_entry(
                unit_memory_entry,
                index_vectors=retrieval_mode == "hybrid",
            )
        except Exception as exc:  # pragma: no cover - Unit Memory must not block settlement.
            record_unit_memory_retrieval_trace(
                output_dir,
                {
                    "recorded_at": _timestamp(),
                    "event_type": "unit_memory_write_failed",
                    "book_id": provisioned.output_dir.name,
                    "unit_id": _clean_text(selected_source_unit.get("unit_id")),
                    "degradation_reason": f"unit_memory_write_failed:{type(exc).__name__}",
                },
            )
    if meaning_units_in_chapter is not None:
        meaning_units_in_chapter.append(
            {
                "source_span_id": source_id,
                "source_span": source_span,
                "sentence_ids": [_clean_text(item.get("sentence_id")) for item in chosen_unit_sentences if _clean_text(item.get("sentence_id"))],
                "summary": _clean_text(digest_result.get("reading_impression")),
            }
        )
    local_buffer = close_local_meaning_unit(local_buffer)

    bundle.update(
        {
            "local_buffer": local_buffer,
            "local_continuity": local_continuity,
            "continuation_capsule": _build_runtime_continuation_capsule(
                chapter_ref=chapter_ref,
                local_buffer=local_buffer,
                active_attention=active_attention,
                recent_reading_memory=recent_reading_memory,
                reflective_frames=reflective_frames,
                reaction_records=reaction_records,
            ),
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "reflective_frames": reflective_frames,
            "knowledge_activations": knowledge_activations,
            "reaction_records": reaction_records,
            "reconsolidation_records": reconsolidation_records,
            "reader_policy": reader_policy,
            "resume_metadata": bundle.get("resume_metadata", {}),
        }
    )
    _save_runtime_bundle(output_dir, bundle)
    maybe_capture_memory_quality_probe(
        capture_enabled=capture_memory_probe,
        output_dir=output_dir,
        settings=memory_quality_probe_config,
        ordered_sentence_ids=ordered_probe_sentence_ids,
        actual_sentence_id=focal_sentence_id,
        chapter_ref=chapter_ref,
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        actual_source_span=source_span if has_selected_source_unit else {},
        actual_source_span_id=source_id if has_selected_source_unit else "",
        unit_memory_retrieval=unit_memory_retrieval,
        reading_memory=reading_memory,
    )
    active_refs = {
        "reaction_id": _clean_text(emitted_reactions[-1].get("reaction_id")) if emitted_reactions else "",
        "source_span_id": _clean_text(current_source_ref.get("source_span_id")) if isinstance(current_source_ref, dict) else "",
    }
    persist_reading_position(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        active_artifact_refs={key: value for key, value in active_refs.items() if value},
        source_span=source_span if has_selected_source_unit else None,
        status="running",
        phase="reading",
    )
    return {
        "local_buffer": local_buffer,
        "local_continuity": local_continuity,
        "active_attention": active_attention,
        "recent_reading_memory": recent_reading_memory,
        "reflective_frames": reflective_frames,
        "knowledge_activations": knowledge_activations,
        "reaction_records": reaction_records,
        "reconsolidation_records": reconsolidation_records,
        "bundle": bundle,
        "emitted_reactions": emitted_reactions,
        "current_source_ref": current_source_ref,
        "focal_sentence": focal_sentence,
        "source_cursor": dict(source_span.get("end_cursor", {})) if has_selected_source_unit and isinstance(source_span.get("end_cursor"), dict) else {},
        "source_span": source_span if has_selected_source_unit else {},
        "selected_source_unit": selected_source_unit if has_selected_source_unit else {},
        "units_read_delta": 1,
        "touched_chapter_ids": [chapter_id],
    }


def parse_attentional_v2(request: ParseRequest, mechanism: MechanismInfo) -> ParseResult:
    """Implement the parse-stage entrypoint for attentional_v2."""

    provisioned = ensure_canonical_parse(request.book_path, language_mode=request.language_mode)
    if provisioned.book_document is None:
        raise RuntimeError("Shared canonical parse did not produce book_document.json.")

    save_book_document(book_document_file(provisioned.output_dir), provisioned.book_document)
    created = not runtime_artifacts.book_manifest_file(provisioned.output_dir).exists()
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(
            provisioned.output_dir,
            mechanism_key=mechanism.key,
            stage="parse",
        ),
    ):
        artifact_tree = initialize_artifact_tree(provisioned.output_dir)
        survey_summary = write_book_survey_artifacts(
            provisioned.output_dir,
            provisioned.book_document,
            policy_snapshot=build_default_reader_policy(),
        )
        chapter_ids = [
            int(chapter.get("id", 0) or 0)
            for chapter in provisioned.book_document.get("chapters", [])
            if isinstance(chapter, dict) and int(chapter.get("id", 0) or 0) > 0
        ]
        _write_manifest(
            provisioned.output_dir,
            provisioned.book_document,
            chapter_statuses={chapter_id: "pending" for chapter_id in chapter_ids},
        )
        write_parse_progress(
            provisioned.output_dir,
            book_title=provisioned.title,
            status="ready",
            total_chapters=len(chapter_ids),
            completed_chapters=len(chapter_ids),
            parsed_chapter_ids=chapter_ids,
            sync_run_state=False,
        )
        write_run_state(
            provisioned.output_dir,
            build_run_state(
                book_title=provisioned.title,
                stage="ready",
                total_chapters=len(chapter_ids),
                completed_chapters=0,
                resume_available=False,
            ),
        )
        append_activity_event(
            provisioned.output_dir,
            {
                "type": "structure_ready",
                "message": "Default deep-reading parse is ready; the shared sentence substrate and survey artifacts are available.",
            },
        )
        return ParseResult(
            mechanism=mechanism,
            book_document=provisioned.book_document,
            output_dir=provisioned.output_dir,
            created=created,
            mechanism_artifact=_artifact_summary(
                provisioned,
                provisioned.book_document,
                artifact_tree=artifact_tree,
                survey_summary=survey_summary,
            ),
        )


def run_reading_runner(request: ReadRequest, mechanism: MechanismInfo) -> ReadResult:
    """Run the mechanism-internal Reading Runner loop."""

    if request.task_mode == "book_analysis":
        raise ValueError("attentional_v2 does not support the retired legacy book_analysis mode.")

    provisioned = ensure_canonical_parse(request.book_path, language_mode=request.language_mode)
    if provisioned.book_document is None:
        raise RuntimeError("Shared canonical parse did not produce book_document.json.")

    output_dir = provisioned.output_dir
    save_book_document(book_document_file(output_dir), provisioned.book_document)
    created = not runtime_artifacts.book_manifest_file(output_dir).exists()
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(
            output_dir,
            mechanism_key=mechanism.key,
            stage="read",
        ),
    ):
        if not request.continue_mode:
            _reset_live_runtime(output_dir)
        artifact_tree = initialize_artifact_tree(output_dir)
        survey_summary = write_book_survey_artifacts(
            output_dir,
            provisioned.book_document,
            policy_snapshot=build_default_reader_policy(),
        )
        if not request.continue_mode:
            _write_manifest(output_dir, provisioned.book_document)
        _update_shell_phase(output_dir, status="running", phase="preparing")

        bundle = _load_runtime_bundle(output_dir)
        resume_payload: dict[str, object] | None = None
        if request.continue_mode:
            resume_payload = resume_from_checkpoint(output_dir, book_document=provisioned.book_document)
            bundle = _load_runtime_bundle(output_dir)

        memory_retrieval_config = resolve_memory_retrieval_config(
            output_dir,
            dict(request.mechanism_config or {}),
            continue_mode=bool(request.continue_mode),
        )
        reader_policy: ReaderPolicy = bundle["reader_policy"]  # type: ignore[assignment]
        audit_window_max_units = _audit_window_max_units(request)
        audit_window_units_read = 0
        audit_window_stop_reason = ""
        touched_chapter_ids: set[int] = set()
        local_buffer: LocalBufferState = bundle["local_buffer"]  # type: ignore[assignment]
        local_continuity: LocalContinuityState = bundle["local_continuity"]  # type: ignore[assignment]
        active_attention: ActiveAttention = bundle["active_attention"]  # type: ignore[assignment]
        recent_reading_memory: RecentReadingMemoryState = bundle["recent_reading_memory"]  # type: ignore[assignment]
        reflective_frames: ReflectiveFramesState = bundle["reflective_frames"]  # type: ignore[assignment]
        knowledge_activations: KnowledgeActivationsState = bundle["knowledge_activations"]  # type: ignore[assignment]
        reaction_records: ReactionRecordsState = bundle["reaction_records"]  # type: ignore[assignment]
        reconsolidation_records = bundle["reconsolidation_records"]
        resume_metadata = bundle["resume_metadata"]
        survey_map = load_json(survey_map_file(output_dir)) if survey_map_file(output_dir).exists() else {}
        sentence_lookup, chapter_lookup = _build_sentence_lookup(provisioned.book_document)
        memory_quality_probe_config = memory_quality_probe_observability_settings(dict(request.mechanism_config or {}))

        chapter_statuses = _chapter_statuses(provisioned.book_document, output_dir)
        chapter_statuses = _apply_reading_plan_statuses(
            chapter_statuses,
            document=provisioned.book_document,
            survey_map=survey_map,
            chapter_number=request.chapter_number,
        )
        _write_manifest(output_dir, provisioned.book_document, chapter_statuses=chapter_statuses)
        scheduled_chapter_ids = _scheduled_chapter_ids(provisioned.book_document, survey_map)
        resume_chapter_id = int(resume_payload.get("local_continuity", {}).get("chapter_id", 0) or 0) if isinstance(resume_payload, dict) else None
        chapters = _chapter_selection(
            provisioned.book_document,
            output_dir,
            survey_map=survey_map,
            chapter_number=request.chapter_number,
            continue_mode=request.continue_mode,
            resume_chapter_id=resume_chapter_id,
        )
        if request.chapter_number is not None:
            probe_source_chapters = chapters
        else:
            scheduled_probe_chapter_ids = set(scheduled_chapter_ids)
            probe_source_chapters = [
                dict(chapter)
                for chapter in provisioned.book_document.get("chapters", [])
                if isinstance(chapter, dict) and int(chapter.get("id", 0) or 0) in scheduled_probe_chapter_ids
            ]
        ordered_probe_sentence_ids = _ordered_sentence_ids(probe_source_chapters)

        completed_chapters = _completed_scheduled_chapters(
            chapter_statuses,
            scheduled_chapter_ids=scheduled_chapter_ids,
        )
        total_chapters = len(scheduled_chapter_ids) or len(
            [chapter for chapter in provisioned.book_document.get("chapters", []) if isinstance(chapter, dict)]
        )
        run_started_at = _timestamp()

        for chapter in chapters:
            chapter_id = int(chapter.get("id", 0) or 0)
            chapter_ref = _chapter_ref(chapter)
            reading_queue_stage = ""
            if request.chapter_number is None:
                reading_queue_stage = _reading_queue_stage_for_chapter(chapter_id, survey_map=survey_map)
            if reading_queue_stage:
                local_continuity["reading_queue_stage"] = reading_queue_stage
            else:
                local_continuity["reading_queue_stage"] = ""
            chapter_statuses[chapter_id] = "in_progress"
            _write_manifest(output_dir, provisioned.book_document, chapter_statuses=chapter_statuses)
            write_run_state(
                output_dir,
                build_run_state(
                    book_title=provisioned.title,
                    stage="deep_reading",
                    total_chapters=total_chapters,
                    completed_chapters=completed_chapters,
                    current_chapter_id=chapter_id,
                    current_chapter_ref=chapter_ref,
                    current_phase_step="reading",
                    resume_available=bool(load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("resume_available")),
                    last_checkpoint_at=load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("last_checkpoint_at"),
                ),
            )
            append_activity_event(
                output_dir,
                {
                    "type": "chapter_started",
                    "message": f"Started {chapter_ref}.",
                    "chapter_id": chapter_id,
                    "chapter_ref": chapter_ref,
                },
            )

            meaning_units_in_chapter: list[dict[str, object]] = []
            readable = readable_paragraphs(chapter)
            if not readable:
                chapter_statuses[chapter_id] = "done"
                completed_chapters = _completed_scheduled_chapters(
                    chapter_statuses,
                    scheduled_chapter_ids=scheduled_chapter_ids,
                )
                continue

            cursor = _chapter_start_source_cursor(
                chapter=chapter,
                local_continuity=local_continuity,
                output_dir=output_dir,
                continue_mode=bool(request.continue_mode and resume_chapter_id == chapter_id),
            )
            while not cursor_at_or_after_chapter_end(chapter, cursor):
                local_continuity["mainline_cursor"] = _shared_cursor_for_source_cursor(cursor)
                bundle["local_continuity"] = local_continuity
                prepared_source_unit = prepare_next_source_unit_for_read(
                    current_chapter=chapter,
                    current_cursor=cursor,
                    local_buffer=local_buffer,
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,
                    recent_reading_memory=recent_reading_memory,
                    reflective_frames=reflective_frames,
                    reaction_records=reaction_records,
                    local_continuity=local_continuity,
                    reader_policy=reader_policy,
                    output_language=provisioned.output_language,
                    output_dir=output_dir,
                    book_title=provisioned.title,
                    author=provisioned.author,
                    book_id=provisioned.output_dir.name,
                    memory_retrieval_config=memory_retrieval_config,
                )
                settled_unit = _settle_next_unit(
                    prepared_source_unit=prepared_source_unit,
                    chapter_lookup=chapter_lookup,
                    local_buffer=local_buffer,
                    local_continuity=local_continuity,
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,
                    recent_reading_memory=recent_reading_memory,
                    reflective_frames=reflective_frames,
                    knowledge_activations=knowledge_activations,
                    reaction_records=reaction_records,
                    reconsolidation_records=reconsolidation_records,
                    reader_policy=reader_policy,
                    output_language=provisioned.output_language,
                    output_dir=output_dir,
                    provisioned=provisioned,
                    bundle=bundle,
                    memory_retrieval_config=memory_retrieval_config,
                    reading_queue_stage=reading_queue_stage,
                    total_chapters=total_chapters,
                    completed_chapters=completed_chapters,
                    memory_quality_probe_config=memory_quality_probe_config,
                    ordered_probe_sentence_ids=ordered_probe_sentence_ids,
                    meaning_units_in_chapter=meaning_units_in_chapter,
                    already_ingested_sentence_ids=set(),
                    capture_memory_probe=True,
                )
                local_buffer = settled_unit["local_buffer"]  # type: ignore[assignment]
                local_continuity = settled_unit["local_continuity"]  # type: ignore[assignment]
                active_attention = settled_unit["active_attention"]  # type: ignore[assignment]
                recent_reading_memory = settled_unit["recent_reading_memory"]  # type: ignore[assignment]
                reflective_frames = settled_unit["reflective_frames"]  # type: ignore[assignment]
                knowledge_activations = settled_unit["knowledge_activations"]  # type: ignore[assignment]
                reaction_records = settled_unit["reaction_records"]  # type: ignore[assignment]
                reconsolidation_records = settled_unit["reconsolidation_records"]  # type: ignore[assignment]
                bundle = settled_unit["bundle"]  # type: ignore[assignment]
                touched_chapter_ids.update(int(item) for item in settled_unit.get("touched_chapter_ids", []) if int(item) > 0)
                audit_window_units_read += int(settled_unit.get("units_read_delta", 0) or 0)
                next_cursor = settled_unit.get("source_cursor")
                if isinstance(next_cursor, dict) and cursor_less_than(cursor, next_cursor):
                    cursor = normalize_cursor_for_chapter(chapter, next_cursor)
                else:
                    cursor = chapter_end_cursor(chapter)
                if audit_window_max_units and audit_window_units_read >= audit_window_max_units:
                    audit_window_stop_reason = "audit_window_max_units_reached"
                    break

            if audit_window_stop_reason:
                break

            end_cursor = chapter_end_cursor(chapter)
            end_source_unit = source_unit_from_span(
                chapter=chapter,
                source_span={
                    "start_cursor": dict(end_cursor),
                    "end_cursor": dict(end_cursor),
                },
            )
            last_paragraph = readable[-1] if readable else {}
            chapter_end_source_ref = source_ref_from_span(
                end_source_unit.get("source_span") if isinstance(end_source_unit.get("source_span"), dict) else {},
                quote=_clean_text(last_paragraph.get("text"))[-220:] if isinstance(last_paragraph, dict) else chapter_ref,
                role="chapter_end",
                resolution={"status": "chapter_end"},
            )
            phase6 = run_phase6_chapter_cycle(
                book_id=runtime_artifacts.book_id_from_output_dir(output_dir),
                chapter=chapter,
                meaning_units_in_chapter=meaning_units_in_chapter,
                chapter_end_source_ref=chapter_end_source_ref,
                active_attention=active_attention,
                reflective_frames=reflective_frames,
                knowledge_activations=knowledge_activations,
                reaction_records=reaction_records,
                reader_policy=reader_policy,
                output_language=provisioned.output_language,
                output_dir=output_dir,
                persist_compatibility_projection=True,
                book_title=provisioned.title,
                author=provisioned.author,
            )
            active_attention = phase6["active_attention"]  # type: ignore[assignment]
            reflective_frames = phase6["reflective_frames"]  # type: ignore[assignment]
            knowledge_activations = phase6["knowledge_activations"]  # type: ignore[assignment]
            reaction_records = phase6["reaction_records"]  # type: ignore[assignment]
            bundle.update(
                {
                    "local_buffer": local_buffer,
                    "local_continuity": local_continuity,
                    "continuation_capsule": _build_runtime_continuation_capsule(
                        chapter_ref=chapter_ref,
                        local_buffer=local_buffer,
                        active_attention=active_attention,
                        recent_reading_memory=recent_reading_memory,
                        reflective_frames=reflective_frames,
                        reaction_records=reaction_records,
                    ),
                    "active_attention": active_attention,
                    "recent_reading_memory": recent_reading_memory,
                    "reflective_frames": reflective_frames,
                    "knowledge_activations": knowledge_activations,
                    "reaction_records": reaction_records,
                    "reconsolidation_records": reconsolidation_records,
                    "reader_policy": reader_policy,
                    "resume_metadata": resume_metadata,
                }
            )
            _save_runtime_bundle(output_dir, bundle)
            chapter_statuses[chapter_id] = "done"
            completed_chapters = _completed_scheduled_chapters(
                chapter_statuses,
                scheduled_chapter_ids=scheduled_chapter_ids,
            )
            _write_manifest(output_dir, provisioned.book_document, chapter_statuses=chapter_statuses)
            checkpoint = write_full_checkpoint(
                output_dir,
                checkpoint_id=f"chapter-{chapter_id:03d}",
                checkpoint_reason="chapter_boundary",
            )
            append_activity_event(
                output_dir,
                {
                    "type": "chapter_completed",
                    "message": f"Finished {chapter_ref} with {len(reaction_records_for_chapter(reaction_records, chapter_ref=chapter_ref))} visible reactions.",
                    "chapter_id": chapter_id,
                    "chapter_ref": chapter_ref,
                },
            )
            write_run_state(
                output_dir,
                build_run_state(
                    book_title=provisioned.title,
                    stage="deep_reading",
                    total_chapters=total_chapters,
                    completed_chapters=completed_chapters,
                    current_chapter_id=chapter_id,
                    current_chapter_ref=chapter_ref,
                    current_phase_step="chapter_completed",
                    resume_available=True,
                    last_checkpoint_at=checkpoint.get("created_at"),
                ),
            )
        if audit_window_stop_reason:
            chapter_statuses = _persist_partial_chapter_projections(
                output_dir=output_dir,
                chapter_lookup=chapter_lookup,
                touched_chapter_ids=touched_chapter_ids,
                reaction_records=reaction_records,
                output_language=provisioned.output_language,
                chapter_statuses=chapter_statuses,
            )
            completed_chapters = _completed_scheduled_chapters(
                chapter_statuses,
                scheduled_chapter_ids=scheduled_chapter_ids,
            )
            append_activity_event(
                output_dir,
                {
                    "type": "audit_window_stopped",
                    "message": f"Stopped Reading Runner audit window after {audit_window_units_read} formal units.",
                    "details": {
                        "audit_window_max_units": audit_window_max_units,
                        "formal_units_read": audit_window_units_read,
                        "stop_reason": audit_window_stop_reason,
                        "partial_read": True,
                    },
                },
            )
        _write_manifest(output_dir, provisioned.book_document, chapter_statuses=chapter_statuses)
        _update_shell_phase(output_dir, status="completed", phase="idle")
        write_run_state(
            output_dir,
            build_run_state(
                book_title=provisioned.title,
                stage="completed",
                total_chapters=total_chapters,
                completed_chapters=completed_chapters,
                resume_available=bool(load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("resume_available")),
                last_checkpoint_at=load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("last_checkpoint_at"),
            ),
        )
        append_activity_event(
            output_dir,
            {
                "type": "run_completed",
                "message": "Reading Runner completed sequential reading.",
                "details": {
                    "started_at": run_started_at,
                    "finished_at": _timestamp(),
                },
            },
        )

        normalized_eval_bundle = build_normalized_eval_bundle(
            output_dir,
            config_payload={
                "task_mode": request.task_mode,
                "mechanism_config": dict(request.mechanism_config),
            },
        )
        if bool(dict(request.mechanism_config).get("persist_normalized_eval_bundle")):
            persist_normalized_eval_bundle(
                output_dir,
                config_payload={
                    "task_mode": request.task_mode,
                    "mechanism_config": dict(request.mechanism_config),
                },
            )
        return ReadResult(
            mechanism=mechanism,
            book_document=provisioned.book_document,
            output_dir=output_dir,
            created=created,
            mechanism_artifact=_artifact_summary(
                provisioned,
                provisioned.book_document,
                artifact_tree=artifact_tree,
                survey_summary=survey_summary,
            ),
            normalized_eval_bundle=normalized_eval_bundle,
        )
