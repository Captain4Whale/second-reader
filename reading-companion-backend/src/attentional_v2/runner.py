"""Reading Runner integration for the attentional_v2 mechanism."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

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
from .nodes import (
    navigate_choose_next_unit_act,
    read_unit,
)
from .observability import (
    maybe_capture_memory_quality_probe,
    memory_quality_probe_observability_settings,
    record_read,
    record_settlement,
    record_unitization,
)
from .read_context import build_carry_forward_context
from .resume import persist_reading_position, resume_from_checkpoint, write_full_checkpoint
from .skills.source_skills import resolve_visible_sentence_range
from .source_spans import (
    build_paragraph_offset_preview,
    chapter_end_cursor,
    cursor_at_or_after_chapter_end,
    cursor_less_than,
    fallback_end_cursor_for_preview,
    first_cursor_for_chapter,
    normalize_cursor_for_chapter,
    readable_paragraphs,
    resolve_end_anchor_text,
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
    ConceptRegistryState,
    DetourNeed,
    KnowledgeActivationsState,
    LocalBufferState,
    LocalContinuityState,
    NavigateActResult,
    NavigateActTraceEntry,
    NavigateNextUnitResult,
    ReactionRecordsState,
    ReaderPolicy,
    ReflectiveFramesState,
    ThreadTraceState,
    UnitizeDecision,
    ReadUnitResult,
    ActiveAttention,
    build_empty_continuation_capsule,
    build_empty_concept_registry,
    build_default_reader_policy,
    build_empty_knowledge_activations,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_reaction_records,
    build_empty_reconsolidation_records,
    build_empty_recent_reading_memory,
    build_empty_reflective_frames,
    build_empty_resume_metadata,
    build_empty_thread_trace,
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
    apply_concept_registry_operations,
    apply_recent_reading_memory_operations,
    apply_thread_trace_operations,
    close_local_meaning_unit,
    apply_active_attention_operations,
)
from .state_migration import normalize_active_tension_state
from .state_projection import build_navigation_context
from .storage import (
    chapter_result_compatibility_file,
    checkpoints_dir,
    concept_registry_file,
    continuation_capsule_file,
    initialize_artifact_tree,
    knowledge_activations_file,
    load_json,
    local_buffer_file,
    local_continuity_file,
    memory_quality_probe_export_file,
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
    thread_trace_file,
    read_audit_file,
    unitization_audit_file,
    active_attention_file,
)
from .survey import write_book_survey_artifacts
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
    """Deprecated after DEC-103/DEC-104: project a cursor for legacy detour skills."""

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


def _local_continuity_detour_trace(local_continuity: LocalContinuityState) -> list[dict[str, object]]:
    """Deprecated after DEC-103/DEC-104: historical detour trace reader."""

    if not isinstance(local_continuity.get("detour_trace"), list):
        local_continuity["detour_trace"] = []
    return [
        dict(item)
        for item in local_continuity.get("detour_trace", [])
        if isinstance(item, dict)
    ]


def _compact_detour_trace_entry(entry: dict[str, object]) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: compact one historical detour trace entry."""

    compact: dict[str, object] = {
        "detour_id": _clean_text(entry.get("detour_id")),
        "origin_cursor": dict(entry.get("origin_cursor", {})) if isinstance(entry.get("origin_cursor"), dict) else {},
        "origin_target_hint": _clean_text(entry.get("origin_target_hint")),
        "status": _clean_text(entry.get("status")),
    }
    for key in (
        "open_reason",
        "defer_reason",
        "resolve_reason",
        "abandon_reason",
        "restore_mainline_reason",
        "last_navigation_decision",
        "last_navigation_reason",
    ):
        value = _clean_text(entry.get(key))
        if value:
            compact[key] = value
    return compact


def _compact_detour_trace(local_continuity: LocalContinuityState, *, limit: int = 4) -> list[dict[str, object]]:
    """Deprecated after DEC-103/DEC-104: compact historical detour lifecycle trace."""

    return [
        _compact_detour_trace_entry(entry)
        for entry in _local_continuity_detour_trace(local_continuity)
    ][-limit:]


def _active_detour_need(local_continuity: LocalContinuityState) -> DetourNeed | None:
    """Deprecated after DEC-103/DEC-104: live runs no longer activate detours."""

    active_detour_need = local_continuity.get("active_detour_need")
    if not isinstance(active_detour_need, dict):
        return None
    if _clean_text(active_detour_need.get("status")).lower() != "open":
        return None
    return dict(active_detour_need)  # type: ignore[return-value]


def _sync_active_detour_from_trace(local_continuity: LocalContinuityState) -> LocalContinuityState:
    """Deprecated after DEC-103/DEC-104: historical detour compatibility only."""

    trace = _local_continuity_detour_trace(local_continuity)
    for entry in reversed(trace):
        if _clean_text(entry.get("status")).lower() != "open":
            continue
        local_continuity["active_detour_id"] = _clean_text(entry.get("detour_id"))
        local_continuity["active_detour_need"] = {
            "reason": _clean_text(entry.get("open_reason")),
            "target_hint": _clean_text(entry.get("origin_target_hint")),
            "status": "open",
        }
        local_continuity["detour_trace"] = trace
        return local_continuity
    local_continuity["active_detour_id"] = ""
    local_continuity["active_detour_need"] = None
    local_continuity["detour_trace"] = trace
    return local_continuity


def _apply_detour_need(
    local_continuity: LocalContinuityState,
    detour_need: DetourNeed | None,
) -> LocalContinuityState:
    """Deprecated after DEC-103/DEC-104: live reads ignore detour needs."""

    if not isinstance(detour_need, dict):
        return local_continuity
    status = _clean_text(detour_need.get("status")).lower() or "open"
    if status not in {"open", "resolved", "abandoned"}:
        status = "open"
    trace = _local_continuity_detour_trace(local_continuity)
    if status == "open":
        origin_cursor = (
            dict(local_continuity.get("mainline_cursor", {}))
            if isinstance(local_continuity.get("mainline_cursor"), dict)
            else {}
        )
        origin_chapter_id = origin_cursor.get("chapter_id")
        origin_sentence_id = _clean_text(origin_cursor.get("sentence_id"))
        detour_id = f"detour:{int(origin_chapter_id or 0)}:{origin_sentence_id or 'chapter'}:{len(trace) + 1}"
        trace.append(
            {
                "detour_id": detour_id,
                "origin_cursor": origin_cursor,
                "origin_target_hint": _clean_text(detour_need.get("target_hint")),
                "status": "open",
                "open_reason": _clean_text(detour_need.get("reason")),
            }
        )
        local_continuity["detour_trace"] = trace
        local_continuity["active_detour_id"] = detour_id
        local_continuity["active_detour_need"] = {
            "reason": _clean_text(detour_need.get("reason")),
            "target_hint": _clean_text(detour_need.get("target_hint")),
            "status": "open",
        }
        return local_continuity

    active_detour_id = _clean_text(local_continuity.get("active_detour_id"))
    for entry in trace:
        if _clean_text(entry.get("detour_id")) != active_detour_id:
            continue
        entry["status"] = status
        reason = _clean_text(detour_need.get("reason"))
        defer_reason = _clean_text(detour_need.get("defer_reason"))
        if status == "resolved":
            entry["resolve_reason"] = reason
            entry["restore_mainline_reason"] = (
                _clean_text(detour_need.get("restore_mainline_reason"))
                or reason
                or "detour_resolved"
            )
        if status == "abandoned":
            entry["abandon_reason"] = reason
            entry["defer_reason"] = defer_reason or reason
        last_navigation_decision = _clean_text(detour_need.get("last_navigation_decision"))
        if last_navigation_decision:
            entry["last_navigation_decision"] = last_navigation_decision
        last_navigation_reason = _clean_text(detour_need.get("last_navigation_reason"))
        if last_navigation_reason:
            entry["last_navigation_reason"] = last_navigation_reason
        break
    local_continuity["detour_trace"] = trace
    return _sync_active_detour_from_trace(local_continuity)


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
        "concept_registry": lambda: build_empty_concept_registry(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
        "thread_trace": lambda: build_empty_thread_trace(mechanism_version=ATTENTIONAL_V2_MECHANISM_VERSION),
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
        "reflective_summaries": runtime_dir(output_dir) / "reflective_summaries.json",
    }
    new_state_paths = {
        "active_attention": active_attention_file(output_dir),
        "recent_reading_memory": recent_reading_memory_file(output_dir),
        "concept_registry": concept_registry_file(output_dir),
        "thread_trace": thread_trace_file(output_dir),
        "reflective_frames": reflective_frames_file(output_dir),
    }
    loaded_new = {name: load_json(path) for name, path in new_state_paths.items() if path.exists()}
    if not loaded_new and any(path.exists() for path in legacy_paths.values()):
        raise RuntimeError(
            "Pre-Phase C.3 attentional_v2 runtime state is no longer supported; rerun from a new-format state directory."
        )
    for name in ("active_attention", "recent_reading_memory", "concept_registry", "thread_trace", "reflective_frames"):
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
    save_json(concept_registry_file(output_dir), bundle["concept_registry"])
    save_json(thread_trace_file(output_dir), bundle["thread_trace"])
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
        concept_registry_file(output_dir),
        thread_trace_file(output_dir),
        local_buffer_file(output_dir),
        local_continuity_file(output_dir),
        continuation_capsule_file(output_dir),
        reflective_frames_file(output_dir),
        knowledge_activations_file(output_dir),
        reaction_records_file(output_dir),
        reconsolidation_records_file(output_dir),
        resume_metadata_file(output_dir),
        read_audit_file(output_dir),
        settlement_audit_file(output_dir),
        unitization_audit_file(output_dir),
        memory_quality_probe_export_file(output_dir),
        runtime_artifacts.runtime_shell_file(output_dir),
        runtime_artifacts.run_state_file(output_dir),
        runtime_artifacts.parse_state_file(output_dir),
        runtime_dir(output_dir) / "anchor_bank.json",
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


def _build_detour_navigation_packet(
    *,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
    continuation_capsule: dict[str, object],
    local_continuity: LocalContinuityState,
) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: historical detour-search packet builder."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[],
        local_buffer=local_buffer,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        continuation_capsule=continuation_capsule,
    )
    refs = [
        dict(ref)
        for ref in carry_forward_context.get("refs", [])
        if isinstance(ref, dict) and _clean_text(ref.get("kind")) in {"source", "concept", "thread", "reaction"}
    ][:8]
    detour_trace_summary = _compact_detour_trace(local_continuity)
    return {
        "packet_version": _clean_text(carry_forward_context.get("packet_version")),
        "mainline_cursor": dict(local_continuity.get("mainline_cursor", {}))
        if isinstance(local_continuity.get("mainline_cursor"), dict)
        else {},
        "active_detour_id": _clean_text(local_continuity.get("active_detour_id")),
        "active_detour_need": dict(local_continuity.get("active_detour_need", {}))
        if isinstance(local_continuity.get("active_detour_need"), dict)
        else {},
        "detour_trace": detour_trace_summary,
        "active_attention": {
            "active_items": [
                dict(item)
                for item in carry_forward_context.get("active_attention_digest", {}).get("active_items", [])
                if isinstance(item, dict)
            ][:6]
            if isinstance(carry_forward_context.get("active_attention_digest"), dict)
            else [],
        },
        "recent_reading_memory": dict(carry_forward_context.get("recent_reading_memory", {}))
        if isinstance(carry_forward_context.get("recent_reading_memory"), dict)
        else {"active_entries": [], "active_entry_count": 0},
        "concept_digest": [
            dict(item)
            for item in carry_forward_context.get("concept_digest", [])
            if isinstance(item, dict)
        ][:3],
        "thread_digest": [
            dict(item)
            for item in carry_forward_context.get("thread_digest", [])
            if isinstance(item, dict)
        ][:3],
        "reflective_digest": dict(carry_forward_context.get("chapter_reflective_frame", {}))
        if isinstance(carry_forward_context.get("chapter_reflective_frame"), dict)
        else {},
        "anchor_handles": refs,
    }


def _build_detour_read_context(local_continuity: LocalContinuityState) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: live reads no longer receive detour context."""

    return {
        "active_detour_need": dict(local_continuity.get("active_detour_need", {}))
        if isinstance(local_continuity.get("active_detour_need"), dict)
        else {},
        "mainline_background": {
            "mainline_cursor": dict(local_continuity.get("mainline_cursor", {}))
            if isinstance(local_continuity.get("mainline_cursor"), dict)
            else {},
        },
        "detour_trace_summary": _compact_detour_trace(local_continuity),
    }


def _skill_result_trace(skill_result: dict[str, object]) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: summarize legacy source-skill results."""

    result = skill_result.get("result") if isinstance(skill_result, dict) else {}
    result_summary: dict[str, object] = {}
    if isinstance(result, dict):
        cards = result.get("cards")
        sentences = result.get("sentences")
        if isinstance(cards, list):
            result_summary["card_count"] = len(cards)
            result_summary["cards"] = [
                {
                    "card_id": _clean_text(card.get("card_id")),
                    "start_sentence_id": _clean_text(card.get("start_sentence_id")),
                    "end_sentence_id": _clean_text(card.get("end_sentence_id")),
                }
                for card in cards[:5]
                if isinstance(card, dict)
            ]
        if isinstance(sentences, list):
            result_summary["sentence_count"] = len(sentences)
            result_summary["start_sentence_id"] = _clean_text(result.get("start_sentence_id"))
            result_summary["end_sentence_id"] = _clean_text(result.get("end_sentence_id"))
    return {
        "skill_name": _clean_text(skill_result.get("skill_name")) if isinstance(skill_result, dict) else "",
        "status": _clean_text(skill_result.get("status")) if isinstance(skill_result, dict) else "error",
        "error": _clean_text(skill_result.get("error")) if isinstance(skill_result, dict) else "",
        "result_summary": result_summary,
        "provenance": dict(skill_result.get("provenance", {})) if isinstance(skill_result.get("provenance"), dict) else {},
    }


def _navigate_skill_catalog() -> list[dict[str, object]]:
    """Deprecated after DEC-103/DEC-104: source skills are not on the live path."""

    return [
        {
            "skill_name": "source_map_overview",
            "purpose": "Inspect already-read chapter cards within the mainline boundary.",
            "arguments": {},
        },
        {
            "skill_name": "source_scope_drilldown",
            "purpose": "Expand a current source card or sentence range into smaller source cards.",
            "arguments": {"card_id": "optional", "start_sentence_id": "optional", "end_sentence_id": "optional"},
        },
        {
            "skill_name": "source_window_fetch",
            "purpose": "Fetch visible source text for a bounded sentence range.",
            "arguments": {"card_id": "optional", "start_sentence_id": "optional", "end_sentence_id": "optional"},
        },
    ]


def _mainline_cursor_from_continuity(local_continuity: LocalContinuityState) -> dict[str, object]:
    """Return the active mainline cursor packet."""

    return (
        dict(local_continuity.get("mainline_cursor", {}))
        if isinstance(local_continuity.get("mainline_cursor"), dict)
        else {}
    )


def _mainline_preview_packet(
    *,
    current_sentence: dict[str, object],
    preview_sentences: list[dict[str, object]],
    preview_range: dict[str, object],
) -> dict[str, object]:
    """Build the source preview packet for one Navigate act."""

    return {
        "current_sentence": {
            "sentence_id": _sentence_id(current_sentence),
            "text": _clean_text(current_sentence.get("text")),
            "text_role": _clean_text(current_sentence.get("text_role")),
            "paragraph_index": _sentence_paragraph_index(current_sentence),
        },
        "preview_range": dict(preview_range),
        "preview_sentences": [
            {
                "sentence_id": _sentence_id(sentence),
                "text": _clean_text(sentence.get("text")),
                "text_role": _clean_text(sentence.get("text_role")),
                "paragraph_index": _sentence_paragraph_index(sentence),
            }
            for sentence in preview_sentences
        ],
    }


def _mainline_source_preview_packet(preview: dict[str, object]) -> dict[str, object]:
    """Build the paragraph-offset source preview packet for Navigate."""

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
    }


def _skill_results_prompt_summary(skill_results: list[dict[str, object]]) -> list[dict[str, object]]:
    """Deprecated after DEC-103/DEC-104: summarize legacy source-skill prompt evidence."""

    summary: list[dict[str, object]] = []
    for skill_result in skill_results[-3:]:
        if not isinstance(skill_result, dict):
            continue
        result = skill_result.get("result")
        compact_result: dict[str, object] = {}
        if isinstance(result, dict):
            if isinstance(result.get("cards"), list):
                compact_result["scope_kind"] = _clean_text(result.get("scope_kind"))
                compact_result["reason"] = _clean_text(result.get("reason"))
                compact_result["cards"] = [
                    {
                        "card_id": _clean_text(card.get("card_id")),
                        "label": _clean_text(card.get("label")),
                        "summary": _clean_text(card.get("summary")),
                        "start_sentence_id": _clean_text(card.get("start_sentence_id")),
                        "end_sentence_id": _clean_text(card.get("end_sentence_id")),
                    }
                    for card in result.get("cards", [])[:8]
                    if isinstance(card, dict)
                ]
            if isinstance(result.get("sentences"), list):
                compact_result["chapter_id"] = result.get("chapter_id")
                compact_result["chapter_ref"] = _clean_text(result.get("chapter_ref"))
                compact_result["start_sentence_id"] = _clean_text(result.get("start_sentence_id"))
                compact_result["end_sentence_id"] = _clean_text(result.get("end_sentence_id"))
                compact_result["sentences"] = [
                    {
                        "sentence_id": _clean_text(sentence.get("sentence_id")),
                        "text": _clean_text(sentence.get("text")),
                        "text_role": _clean_text(sentence.get("text_role")),
                        "paragraph_index": sentence.get("paragraph_index"),
                    }
                    for sentence in result.get("sentences", [])[:24]
                    if isinstance(sentence, dict)
                ]
            if isinstance(result.get("source_window"), dict):
                compact_result["source_window"] = result.get("source_window")
        summary.append(
            {
                "skill_name": _clean_text(skill_result.get("skill_name")),
                "status": _clean_text(skill_result.get("status")),
                "error": _clean_text(skill_result.get("error")),
                "result": compact_result,
                "provenance": dict(skill_result.get("provenance", {})) if isinstance(skill_result.get("provenance"), dict) else {},
            }
        )
    return summary


def _latest_scope_from_skill_results(skill_results: list[dict[str, object]]) -> dict[str, object] | None:
    """Deprecated after DEC-103/DEC-104: inspect legacy source-skill scope results."""

    for skill_result in reversed(skill_results):
        result = skill_result.get("result") if isinstance(skill_result, dict) else None
        if isinstance(result, dict) and isinstance(result.get("cards"), list):
            return dict(result)
    return None


def _allowed_detour_sentence_ids(skill_results: list[dict[str, object]]) -> set[str]:
    """Deprecated after DEC-103/DEC-104: return legacy detour-evidence sentence ids."""

    allowed: set[str] = set()
    for skill_result in skill_results:
        result = skill_result.get("result") if isinstance(skill_result, dict) else None
        if not isinstance(result, dict):
            continue
        cards = result.get("cards")
        if isinstance(cards, list):
            for card in cards:
                if not isinstance(card, dict):
                    continue
                for key in ("start_sentence_id", "end_sentence_id"):
                    sentence_id = _clean_text(card.get(key))
                    if sentence_id:
                        allowed.add(sentence_id)
        sentences = result.get("sentences")
        if isinstance(sentences, list):
            for sentence in sentences:
                if not isinstance(sentence, dict):
                    continue
                sentence_id = _clean_text(sentence.get("sentence_id"))
                if sentence_id:
                    allowed.add(sentence_id)
        source_window = result.get("source_window")
        if isinstance(source_window, dict):
            for key in ("start_sentence_id", "end_sentence_id"):
                sentence_id = _clean_text(source_window.get(key))
                if sentence_id:
                    allowed.add(sentence_id)
            for sentence in source_window.get("sentences", []):
                if isinstance(sentence, dict) and _clean_text(sentence.get("sentence_id")):
                    allowed.add(_clean_text(sentence.get("sentence_id")))
    return allowed


def _detour_available_sentences(skill_results: list[dict[str, object]]) -> list[dict[str, object]]:
    """Deprecated after DEC-103/DEC-104: return fetched source text for legacy detour guardrails."""

    for skill_result in reversed(skill_results):
        result = skill_result.get("result") if isinstance(skill_result, dict) else None
        if not isinstance(result, dict):
            continue
        sentences = result.get("sentences")
        if isinstance(sentences, list) and sentences:
            return [dict(sentence) for sentence in sentences if isinstance(sentence, dict)]
        source_window = result.get("source_window")
        if isinstance(source_window, dict) and isinstance(source_window.get("sentences"), list):
            return [dict(sentence) for sentence in source_window.get("sentences", []) if isinstance(sentence, dict)]
    return []


def _navigate_trace_entry(
    act_result: NavigateActResult,
    *,
    budget_state: dict[str, object],
    skill_result: dict[str, object] | None = None,
    error: str = "",
) -> NavigateActTraceEntry:
    """Return compact Navigate trace, preserving deprecated skill fields only as compatibility."""

    entry: NavigateActTraceEntry = {
        "decision": _clean_text(act_result.get("decision")),  # type: ignore[typeddict-item]
        "selection_mode": _clean_text(act_result.get("selection_mode")),  # type: ignore[typeddict-item]
        "reason": _clean_text(act_result.get("reason")),
        "end_anchor_text": _clean_text(act_result.get("end_anchor_text")),
        "start_sentence_id": _clean_text(act_result.get("start_sentence_id")),
        "end_sentence_id": _clean_text(act_result.get("end_sentence_id")),
        "source_span_id": _clean_text(act_result.get("source_span_id")),
        "resolution": dict(act_result.get("resolution", {})) if isinstance(act_result.get("resolution"), dict) else {},
        "budget_state": dict(budget_state),
    }
    if isinstance(act_result.get("skill_request"), dict):
        entry["skill_request"] = dict(act_result["skill_request"])
    if isinstance(skill_result, dict):
        entry["skill_result"] = _skill_result_trace(skill_result)
    if error:
        entry["error"] = error
    return entry


_PLANNING_SUPPORT_MARKER_KEYS = (
    "source_scent",
    "detour_value",
    "continuity_cost",
    "active_recall_needed",
    "look_back_needed",
    "support_signal_reason",
    "budget_stop_reason",
)


def _navigation_budget_stop_reason(entry: dict[str, object]) -> str:
    """Return deterministic budget stop evidence, if the trace entry has it."""

    error = _clean_text(entry.get("error"))
    if error == "navigate_skill_budget_exhausted":
        return error
    reason = _clean_text(entry.get("reason"))
    if reason == "navigate_choose_next_unit_budget_exhausted":
        return reason
    return ""


def _safe_int(value: object) -> int:
    """Return an int for compact audit math, or zero when the value is not numeric."""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def _navigation_planning_support_markers(entry: dict[str, object]) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: preserve legacy detour/source-skill audit markers."""

    decision = _clean_text(entry.get("decision"))
    selection_mode = _clean_text(entry.get("selection_mode"))
    if selection_mode != "detour" and decision not in {"request_skill", "defer_detour"} and not entry.get("error"):
        return {}

    skill_request = entry.get("skill_request") if isinstance(entry.get("skill_request"), dict) else {}
    skill_result = entry.get("skill_result") if isinstance(entry.get("skill_result"), dict) else {}
    budget_state = entry.get("budget_state") if isinstance(entry.get("budget_state"), dict) else {}
    has_source_reference = bool(
        _clean_text(entry.get("source_span_id"))
        or _clean_text(entry.get("start_sentence_id"))
        or _clean_text(entry.get("end_sentence_id"))
    )
    has_skill_evidence = bool(skill_result)
    budget_stop_reason = _navigation_budget_stop_reason(entry)

    source_scent = "not_assessed"
    if has_source_reference or has_skill_evidence:
        source_scent = "present"
    elif skill_request:
        source_scent = "requested"

    detour_value = "not_assessed"
    if decision == "request_skill":
        detour_value = "source_support_requested"
    elif decision == "choose_unit" and has_source_reference:
        detour_value = "source_support_available"

    continuity_cost = "not_assessed"
    if budget_stop_reason:
        continuity_cost = "budget_stop"
    elif _safe_int(budget_state.get("act_index")) > 1 or _safe_int(budget_state.get("skill_requests_used")) > 0:
        continuity_cost = "budget_used"

    support_signal_reason = "not_assessed"
    if budget_stop_reason:
        support_signal_reason = "budget_stop"
    elif skill_request:
        support_signal_reason = "source_skill_requested"
    elif decision == "choose_unit" and has_source_reference:
        support_signal_reason = "source_evidence_available"
    elif decision == "defer_detour":
        support_signal_reason = _clean_text(entry.get("reason")) or "detour_deferred"

    markers: dict[str, object] = {
        "source_scent": source_scent,
        "detour_value": detour_value,
        "continuity_cost": continuity_cost,
        "active_recall_needed": False,
        "look_back_needed": bool(skill_request or has_skill_evidence),
        "support_signal_reason": support_signal_reason,
    }
    if budget_stop_reason:
        markers["budget_stop_reason"] = budget_stop_reason
    return markers


def _compact_navigation_trace(navigate_trace: object) -> list[dict[str, object]]:
    """Return compact navigation trace entries safe for read-audit persistence."""

    if not isinstance(navigate_trace, list):
        return []
    compact_entries: list[dict[str, object]] = []
    for item in navigate_trace:
        if not isinstance(item, dict):
            continue
        entry: dict[str, object] = {}
        for key in (
            "decision",
            "selection_mode",
            "reason",
            "end_anchor_text",
            "start_sentence_id",
            "end_sentence_id",
            "source_span_id",
            "resolution",
            "skill_request",
            "skill_result",
            "error",
            "budget_state",
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
            entry.update(_navigation_planning_support_markers(entry))
            compact_entries.append(entry)
    return compact_entries


def _detour_planning_support_markers(
    *,
    selection_result: NavigateNextUnitResult,
    navigation_trace: list[dict[str, object]],
) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: return audit-only markers for legacy detour evidence."""

    selection_mode = _clean_text(selection_result.get("selection_mode"))
    if selection_mode not in {"detour", "deferred"}:
        return {}
    markers = {
        key: value
        for key, value in (navigation_trace[-1] if navigation_trace else {}).items()
        if key in _PLANNING_SUPPORT_MARKER_KEYS
    }
    defer_reason = _clean_text(selection_result.get("defer_reason"))
    if defer_reason == "navigate_choose_next_unit_budget_exhausted":
        markers["budget_stop_reason"] = defer_reason
        markers["continuity_cost"] = "budget_stop"
        markers["support_signal_reason"] = "budget_stop"
    return {
        "source_scent": markers.get("source_scent", "not_assessed"),
        "detour_value": markers.get("detour_value", "not_assessed"),
        "continuity_cost": markers.get("continuity_cost", "not_assessed"),
        "active_recall_needed": bool(markers.get("active_recall_needed", False)),
        "look_back_needed": bool(markers.get("look_back_needed", False)),
        "support_signal_reason": markers.get("support_signal_reason", "not_assessed"),
        **({"budget_stop_reason": markers["budget_stop_reason"]} if _clean_text(markers.get("budget_stop_reason")) else {}),
    }


def _detour_trace_evidence(
    *,
    selection_result: NavigateNextUnitResult,
    local_continuity: LocalContinuityState,
) -> dict[str, object]:
    """Deprecated after DEC-103/DEC-104: new live reads do not emit detour evidence."""

    selection_mode = _clean_text(selection_result.get("selection_mode"))
    if selection_mode not in {"detour", "deferred"}:
        return {}
    evidence: dict[str, object] = {
        "selection_mode": selection_mode,
        "active_detour_id": _clean_text(local_continuity.get("active_detour_id")),
        "detour_trace_summary": _compact_detour_trace(local_continuity),
    }
    if isinstance(local_continuity.get("active_detour_need"), dict):
        evidence["active_detour_need"] = dict(local_continuity["active_detour_need"])
    defer_reason = _clean_text(selection_result.get("defer_reason"))
    if defer_reason:
        evidence["defer_reason"] = defer_reason
    evidence.update(
        _detour_planning_support_markers(
            selection_result=selection_result,
            navigation_trace=_compact_navigation_trace(selection_result.get("navigate_trace")),
        )
    )
    return evidence


def _resolve_detour_act_region(
    *,
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    mainline_cursor: dict[str, object],
    act_result: NavigateActResult,
    reader_policy: ReaderPolicy,
) -> tuple[dict[str, object], list[dict[str, object]], UnitizeDecision] | None:
    """Deprecated after DEC-103/DEC-104: live Navigate no longer lands detour units."""

    start_sentence_id = _clean_text(act_result.get("start_sentence_id"))
    end_sentence_id = _clean_text(act_result.get("end_sentence_id"))
    chapter, selected_sentences, error = resolve_visible_sentence_range(
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        mainline_cursor=mainline_cursor,  # type: ignore[arg-type]
        start_sentence_id=start_sentence_id,
        end_sentence_id=end_sentence_id,
    )
    if error or not isinstance(chapter, dict) or not selected_sentences:
        return None
    max_sentences = int(reader_policy.get("unitize", {}).get("max_coverage_unit_sentences", 12) or 12)
    if max_sentences <= 0:
        max_sentences = 12
    capped = [dict(sentence) for sentence in selected_sentences[:max_sentences]]
    boundary_type = _clean_text(act_result.get("boundary_type")) or "paragraph_end"
    if len(selected_sentences) > max_sentences:
        boundary_type = "budget_cap"
    unitize_decision: UnitizeDecision = {
        "start_sentence_id": _sentence_id(capped[0]),
        "end_sentence_id": _sentence_id(capped[-1]),
        "preview_range": {
            "start_sentence_id": _sentence_id(selected_sentences[0]),
            "end_sentence_id": _sentence_id(selected_sentences[-1]),
        },
        "boundary_type": boundary_type,  # type: ignore[typeddict-item]
        "evidence_sentence_ids": [_sentence_id(sentence) for sentence in capped if _sentence_id(sentence)],
        "reason": _clean_text(act_result.get("reason")),
        "continuation_pressure": bool(act_result.get("continuation_pressure")) or len(selected_sentences) > max_sentences,
    }
    return chapter, capped, unitize_decision


def _resolve_mainline_source_unit(
    *,
    chapter: dict[str, object],
    start_cursor: dict[str, object],
    preview: dict[str, object],
    act_result: NavigateActResult,
    retry_act_result: NavigateActResult | None = None,
) -> tuple[dict[str, object], UnitizeDecision]:
    """Resolve Navigate's source-text tail anchor into an accepted unit span."""

    selected_result = dict(retry_act_result or act_result)
    legacy_end_sentence_id = _clean_text(selected_result.get("end_sentence_id"))
    if legacy_end_sentence_id:
        legacy_sentences = [
            dict(sentence)
            for sentence in chapter.get("sentences", [])
            if isinstance(sentence, dict)
        ]
        end_sentence = next((sentence for sentence in legacy_sentences if _sentence_id(sentence) == legacy_end_sentence_id), None)
        locator = end_sentence.get("locator") if isinstance(end_sentence, dict) else None
        if isinstance(locator, dict):
            end_cursor = {
                "chapter_id": int(chapter.get("id", 0) or 0),
                "chapter_ref": _chapter_ref(chapter),
                "paragraph_index": int(locator.get("paragraph_index", 0) or locator.get("paragraph_start", 0) or 0),
                "char_offset": int(locator.get("char_end", 0) or 0),
            }
            source_span = {
                "start_cursor": dict(start_cursor),
                "end_cursor": end_cursor,
            }
            source_unit = source_unit_from_span(chapter=chapter, source_span=source_span)
            source_id = source_span_id(source_span)
            resolution = {
                "status": "matched",
                "method": "legacy_sentence_compat",
                "end_cursor": end_cursor,
                "end_sentence_id": legacy_end_sentence_id,
            }
            unitize_decision: UnitizeDecision = {
                "end_anchor_text": _clean_text(selected_result.get("end_anchor_text")),
                "source_span": source_span,
                "source_span_id": source_id,
                "preview_range": {
                    "start_cursor": dict(preview.get("preview_start_cursor", {}))
                    if isinstance(preview.get("preview_start_cursor"), dict)
                    else {},
                    "end_cursor": dict(preview.get("preview_end_cursor", {}))
                    if isinstance(preview.get("preview_end_cursor"), dict)
                    else {},
                },
                "boundary_type": _clean_text(selected_result.get("boundary_type")) or "paragraph_end",  # type: ignore[typeddict-item]
                "reason": _clean_text(selected_result.get("reason")),
                "continuation_pressure": bool(selected_result.get("continuation_pressure")),
                "resolution": resolution,
                "start_sentence_id": _clean_text(selected_result.get("start_sentence_id")),
                "end_sentence_id": legacy_end_sentence_id,
                "evidence_sentence_ids": [
                    _clean_text(item)
                    for item in selected_result.get("evidence_sentence_ids", [])
                    if _clean_text(item)
                ] if isinstance(selected_result.get("evidence_sentence_ids"), list) else [],
            }
            source_unit["unitize_decision"] = dict(unitize_decision)
            return source_unit, unitize_decision

    end_anchor_text = _clean_text(selected_result.get("end_anchor_text"))
    resolution = resolve_end_anchor_text(
        preview=preview,
        end_anchor_text=end_anchor_text,
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
    unitize_decision: UnitizeDecision = {
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
        },
        "boundary_type": _clean_text(selected_result.get("boundary_type")) or "paragraph_end",  # type: ignore[typeddict-item]
        "reason": _clean_text(selected_result.get("reason")),
        "continuation_pressure": bool(selected_result.get("continuation_pressure")),
        "resolution": resolution,
    }
    source_unit["unitize_decision"] = dict(unitize_decision)
    return source_unit, unitize_decision


def navigate_choose_next_unit(
    *,
    document: BookDocument,
    survey_map: dict[str, object],
    sentence_lookup: dict[str, dict[str, object]],
    chapter_lookup: dict[int, dict[str, object]],
    current_chapter: dict[str, object],
    current_cursor: dict[str, object],
    local_buffer: LocalBufferState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState | None = None,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
    local_continuity: LocalContinuityState,
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path | None,
    book_title: str,
    author: str,
) -> NavigateNextUnitResult:
    """Choose the next forward mainline unit that should be read."""

    recent_reading_memory = recent_reading_memory or build_empty_recent_reading_memory()
    source_cursor = normalize_cursor_for_chapter(current_chapter, current_cursor)
    preview = build_paragraph_offset_preview(
        chapter=current_chapter,
        current_cursor=source_cursor,
        reader_policy=reader_policy,
    )
    current_chapter_id = int(current_chapter.get("id", 0) or 0)
    current_chapter_ref = _chapter_ref(current_chapter)
    mainline_preview = _mainline_source_preview_packet(dict(preview))
    mainline_cursor = _mainline_cursor_from_continuity(local_continuity)

    navigation_context = build_navigation_context(
        chapter_ref=current_chapter_ref,
        current_sentence_id=_clean_text(source_cursor.get("sentence_id")) or _clean_text(local_buffer.get("current_sentence_id")),
        local_buffer=local_buffer,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        continuation_capsule=continuation_capsule,
    )
    budget_state = {
        "mode": "mainline",
        "skills_allowed": False,
        "act_index": 1,
        "max_acts": 1,
        "skill_requests_used": 0,
        "max_skill_requests": 0,
    }
    act_result = navigate_choose_next_unit_act(
        reading_position={
            "mode": "mainline",
            "current_chapter_id": current_chapter_id,
            "current_chapter_ref": current_chapter_ref,
            "current_cursor": dict(source_cursor),
        },
        mainline_preview=mainline_preview,
        active_detour_need=None,
        mainline_cursor=mainline_cursor,
        navigation_context=navigation_context,
        source_evidence={},
        skill_catalog=[],
        skill_results_so_far=[],
        budget_state=budget_state,
        reader_policy=reader_policy,
        output_language=output_language,
        output_dir=output_dir,
        book_title=book_title,
        author=author,
        chapter_title=_clean_text(current_chapter.get("title")),
        available_sentences=[],
        allowed_sentence_ids=set(),
        default_selection_mode="mainline",
        skills_allowed=False,
    )
    resolution = resolve_end_anchor_text(
        preview=preview,
        end_anchor_text=_clean_text(act_result.get("end_anchor_text")),
    )
    retry_result: NavigateActResult | None = None
    if _clean_text(resolution.get("status")) != "matched":
        retry_result = navigate_choose_next_unit_act(
            reading_position={
                "mode": "mainline",
                "current_chapter_id": current_chapter_id,
                "current_chapter_ref": current_chapter_ref,
                "current_cursor": dict(source_cursor),
                "retry": True,
            },
            mainline_preview=mainline_preview,
            active_detour_need=None,
            mainline_cursor=mainline_cursor,
            navigation_context=navigation_context,
            source_evidence={
                "previous_end_anchor_text": _clean_text(act_result.get("end_anchor_text")),
                "previous_resolution": dict(resolution),
                "retry_instruction": "Return a longer, unique end_anchor_text copied exactly from the end of the chosen unit.",
            },
            skill_catalog=[],
            skill_results_so_far=[],
            budget_state={**budget_state, "act_index": 2, "max_acts": 2},
            reader_policy=reader_policy,
            output_language=output_language,
            output_dir=output_dir,
            book_title=book_title,
            author=author,
            chapter_title=_clean_text(current_chapter.get("title")),
            available_sentences=[],
            allowed_sentence_ids=set(),
            default_selection_mode="mainline",
            skills_allowed=False,
        )
    selected_source_unit, unitize_decision = _resolve_mainline_source_unit(
        chapter=current_chapter,
        start_cursor=dict(source_cursor),
        preview=dict(preview),
        act_result=act_result,
        retry_act_result=retry_result,
    )
    compat_selected_sentences = _compat_unit_sentences_for_source_span(
        current_chapter,
        dict(unitize_decision.get("source_span", {})) if isinstance(unitize_decision.get("source_span"), dict) else {},
    )
    trace_target = retry_result if retry_result is not None else act_result
    trace_target["source_span_id"] = _clean_text(unitize_decision.get("source_span_id"))
    trace_target["source_span"] = dict(unitize_decision.get("source_span", {}))
    trace_target["resolution"] = dict(unitize_decision.get("resolution", {}))
    navigate_trace = [_navigate_trace_entry(act_result, budget_state=budget_state)]
    if retry_result is not None:
        navigate_trace.append(_navigate_trace_entry(retry_result, budget_state={**budget_state, "act_index": 2, "max_acts": 2}))
    return {
        "selection_mode": "mainline",
        "chapter_id": current_chapter_id,
        "chapter_ref": current_chapter_ref,
        "selected_unit_sentences": compat_selected_sentences,
        "selected_source_unit": selected_source_unit,
        "preview": dict(preview),
        "unitize_decision": unitize_decision,  # type: ignore[typeddict-item]
        "navigate_trace": navigate_trace,
        "detour_context": None,
    }


def _source_ref_from_surfaced_reaction(
    *,
    surfaced_reaction: dict[str, object] | None,
    source_unit: dict[str, object] | None = None,
    reading_impression: str = "",
) -> dict[str, object]:
    """Build one deterministic source ref from a read-owned surfaced reaction."""

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
    """Resolve read-proposed source quotes into inline source refs before settlement."""

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
    read_result: ReadUnitResult,
    chosen_unit_sentences: list[dict[str, object]],
    focal_sentence: dict[str, object],
    chapter_id: int,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    reaction_records: ReactionRecordsState,
    output_dir: Path,
    source_unit: dict[str, object] | None = None,
) -> tuple[ReactionRecordsState, list[AnchoredReactionRecord], dict[str, object] | None]:
    """Persist read-owned surfaced reactions through one canonical builder path."""

    emitted_reactions: list[AnchoredReactionRecord] = []
    current_source_ref = None
    surfaced_reactions = [
        dict(item)
        for item in read_result.get("surfaced_reactions", [])
        if isinstance(item, dict)
    ]
    chapter_reaction_count = len(reaction_records_for_chapter(reaction_records, chapter_ref=chapter_ref))
    for index, surfaced_reaction in enumerate(surfaced_reactions, start=1):
        current_source_ref = _source_ref_from_surfaced_reaction(
            surfaced_reaction=surfaced_reaction,
            source_unit=source_unit,
            reading_impression=_clean_text(read_result.get("reading_impression")),
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
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
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
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )
    capsule = carry_forward_context.get("continuation_capsule", {})
    return dict(capsule) if isinstance(capsule, dict) else {}


def _run_read_with_context_loop(
    *,
    chapter: dict[str, object],
    unitize_decision: UnitizeDecision,
    chosen_unit_sentences: list[dict[str, object]] | None = None,
    current_unit_source: dict[str, object] | None = None,
    local_buffer: LocalBufferState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    knowledge_activations: KnowledgeActivationsState,
    reaction_records: ReactionRecordsState,
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path | None,
    book_title: str,
    author: str,
    chapter_id: int,
    chapter_ref: str,
    navigation_trace: list[dict[str, object]] | None = None,
) -> tuple[ReadUnitResult, list[dict[str, str]]]:
    """Run one authoritative read for the chosen unit and persist its private audit."""

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
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        continuation_capsule=continuation_capsule,
    )
    llm_fallbacks: list[dict[str, str]] = []
    try:
        read_result = read_unit(
            current_unit_source=current_unit_source,
            current_unit_sentences=chosen_unit_sentences,
            carry_forward_context=carry_forward_context,
            reader_policy=reader_policy,
        output_language=output_language,
        supplemental_context=None,
        detour_context=None,
            output_dir=output_dir,
            book_title=book_title,
            author=author,
            chapter_title=_clean_text(chapter.get("title")),
        )
    except ReaderLLMError as exc:
        llm_fallbacks.append({"node": "read_unit", "problem_code": exc.problem_code})
        read_result = {
            "reading_impression": "",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "detour_need": None,
        }
    if isinstance(read_result.get("detour_need"), dict):
        read_result["deprecated_detour_need_ignored"] = dict(read_result["detour_need"])  # type: ignore[index]
        read_result["detour_need"] = None
    read_result["memory_uptake_ops"] = _normalize_memory_uptake_ops_source_refs(
        read_result.get("memory_uptake_ops", []),
        source_unit=current_unit_source,
    )

    record_read(
        output_dir,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        unitize_decision=unitize_decision,
        source_unit=current_unit_source,
        carry_forward_context=carry_forward_context,
        read_result=read_result,
        stop_reason="read_complete",
        llm_fallbacks=llm_fallbacks,
        navigation_trace=navigation_trace,
        detour_trace_evidence=None,
    )
    return read_result, llm_fallbacks


def _settle_next_unit(
    *,
    selection_result: NavigateNextUnitResult,
    chapter_lookup: dict[int, dict[str, object]],
    local_buffer: LocalBufferState,
    local_continuity: LocalContinuityState,
    continuation_capsule: dict[str, object],
    active_attention: ActiveAttention,
    recent_reading_memory: RecentReadingMemoryState,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    knowledge_activations: KnowledgeActivationsState,
    reaction_records: ReactionRecordsState,
    reconsolidation_records: dict[str, object],
    reader_policy: ReaderPolicy,
    output_language: str,
    output_dir: Path,
    provisioned: ProvisionedBook,
    bundle: dict[str, dict[str, object]],
    reading_queue_stage: str,
    total_chapters: int,
    completed_chapters: int,
    memory_quality_probe_config: dict[str, object] | None,
    ordered_probe_sentence_ids: list[str],
    meaning_units_in_chapter: list[dict[str, object]] | None,
    already_ingested_sentence_ids: set[str] | None = None,
    capture_memory_probe: bool = False,
) -> dict[str, object]:
    """Read and settle one unit selected by Navigator.choose_next_unit."""

    chapter_id = int(selection_result.get("chapter_id", 0) or 0)
    chapter = chapter_lookup.get(chapter_id)
    if not isinstance(chapter, dict):
        return {
            "local_buffer": local_buffer,
            "local_continuity": local_continuity,
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "concept_registry": concept_registry,
            "thread_trace": thread_trace,
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

    chapter_ref = _clean_text(selection_result.get("chapter_ref")) or _chapter_ref(chapter)
    chosen_unit_sentences = [
        dict(sentence)
        for sentence in selection_result.get("selected_unit_sentences", [])
        if isinstance(sentence, dict)
    ]
    selected_source_unit = (
        dict(selection_result.get("selected_source_unit", {}))
        if isinstance(selection_result.get("selected_source_unit"), dict)
        else {}
    )
    is_source_mainline = _clean_text(selection_result.get("selection_mode")) == "mainline" and bool(selected_source_unit)
    if not chosen_unit_sentences and not is_source_mainline:
        return {
            "local_buffer": local_buffer,
            "local_continuity": local_continuity,
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "concept_registry": concept_registry,
            "thread_trace": thread_trace,
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

    unitize_decision = dict(selection_result.get("unitize_decision", {}))
    focal_sentence = chosen_unit_sentences[-1] if chosen_unit_sentences else {}
    focal_sentence_id = _sentence_id(focal_sentence) if focal_sentence else ""
    source_span = (
        dict(selected_source_unit.get("source_span", {}))
        if isinstance(selected_source_unit.get("source_span"), dict)
        else {}
    )
    source_id = _clean_text(selected_source_unit.get("source_span_id")) or source_span_id(source_span)
    if is_source_mainline:
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
        if is_source_mainline
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
        if is_source_mainline and isinstance(source_span.get("end_cursor"), dict)
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
            if is_source_mainline
            else _compatibility_section_ref(chapter_id, focal_sentence),
            current_reading_activity=current_activity,
            current_phase_step="reading",
            resume_available=True,
            last_checkpoint_at=load_runtime_shell(runtime_artifacts.runtime_shell_file(output_dir)).get("last_checkpoint_at"),
        ),
    )

    read_result, read_fallbacks = _run_read_with_context_loop(
        chapter=chapter,
        chosen_unit_sentences=chosen_unit_sentences,
        current_unit_source=selected_source_unit if is_source_mainline else None,
        unitize_decision=unitize_decision,  # type: ignore[arg-type]
        local_buffer=local_buffer,
        continuation_capsule=continuation_capsule,
        active_attention=active_attention,
        recent_reading_memory=recent_reading_memory,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        knowledge_activations=knowledge_activations,
        reaction_records=reaction_records,
        reader_policy=reader_policy,
        output_language=output_language,
        output_dir=output_dir,
        book_title=provisioned.title,
        author=provisioned.author,
        chapter_id=chapter_id,
        chapter_ref=chapter_ref,
        navigation_trace=_compact_navigation_trace(selection_result.get("navigate_trace")),
    )
    for fallback in read_fallbacks:
        if not isinstance(fallback, dict):
            continue
        append_activity_event(
            output_dir,
            {
                "type": "llm_fallback",
                "stream": "mindstream",
                "kind": "transition",
                "visibility": "hidden",
                "message": f"Read fallback for {_clean_text(fallback.get('node')) or 'unknown_node'}.",
                "chapter_id": chapter_id,
                "chapter_ref": chapter_ref,
                "segment_ref": _compatibility_section_ref_for_source(chapter_id, selected_source_unit)
                if is_source_mainline
                else _compatibility_section_ref(chapter_id, focal_sentence),
                "reading_locus": {
                    **source_locus_from_unit(selected_source_unit),
                    "chapter_id": chapter_id,
                    "chapter_ref": chapter_ref,
                }
                if is_source_mainline
                else _reading_locus(chapter_id, chapter_ref, focal_sentence, local_buffer),
                "current_excerpt": _clean_text(selected_source_unit.get("source_text") if is_source_mainline else focal_sentence.get("text"))[:220],
                "problem_code": _clean_text(fallback.get("problem_code")),
            },
        )

    memory_uptake_ops = read_result.get("memory_uptake_ops", [])
    before_active_attention = active_attention
    before_recent_reading_memory = recent_reading_memory
    before_concept_registry = concept_registry
    before_thread_trace = thread_trace
    before_reaction_records = reaction_records
    active_attention = apply_active_attention_operations(
        active_attention,
        memory_uptake_ops,
    )
    unit_sequence_index = next_unit_sequence_index(output_dir)
    recent_reading_memory = apply_recent_reading_memory_operations(
        recent_reading_memory,
        memory_uptake_ops,
        source_unit_span_id=source_id if is_source_mainline else "",
        created_at_unit_index=unit_sequence_index,
    )
    concept_registry = apply_concept_registry_operations(
        concept_registry,
        memory_uptake_ops,
    )
    thread_trace = apply_thread_trace_operations(
        thread_trace,
        memory_uptake_ops,
    )
    reaction_records, emitted_reactions, current_source_ref = _persist_surfaced_reactions(
        read_result=read_result,
        chosen_unit_sentences=chosen_unit_sentences,
        focal_sentence=focal_sentence,
        source_unit=selected_source_unit if is_source_mainline else None,
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
        source_span=source_span if is_source_mainline else None,
        source_span_id=source_id if is_source_mainline else "",
        memory_uptake_ops=memory_uptake_ops,
        before_active_attention=before_active_attention,
        after_active_attention=active_attention,
        before_recent_reading_memory=before_recent_reading_memory,
        after_recent_reading_memory=recent_reading_memory,
        before_concept_registry=before_concept_registry,
        after_concept_registry=concept_registry,
        before_thread_trace=before_thread_trace,
        after_thread_trace=thread_trace,
        before_reaction_records=before_reaction_records,
        after_reaction_records=reaction_records,
        emitted_reaction_ids=[_clean_text(item.get("reaction_id")) for item in emitted_reactions],
    )
    if is_source_mainline:
        unit_record = append_unit_span_record(
            output_dir,
            chapter_id=chapter_id,
            chapter_ref=chapter_ref,
            source_unit=selected_source_unit,
            preview=dict(selection_result.get("preview", {})) if isinstance(selection_result.get("preview"), dict) else {},
            end_anchor_text=_clean_text(unitize_decision.get("end_anchor_text")),
            resolution=dict(unitize_decision.get("resolution", {})) if isinstance(unitize_decision.get("resolution"), dict) else {},
        )
        selected_source_unit["unit_id"] = _clean_text(unit_record.get("unit_id"))
        selected_source_unit["sequence_index"] = int(unit_record.get("sequence_index", 0) or 0)
    if meaning_units_in_chapter is not None:
        meaning_units_in_chapter.append(
            {
                "source_span_id": source_id,
                "source_span": source_span,
                "sentence_ids": [_clean_text(item.get("sentence_id")) for item in chosen_unit_sentences if _clean_text(item.get("sentence_id"))],
                "summary": _clean_text(read_result.get("reading_impression")),
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
                concept_registry=concept_registry,
                thread_trace=thread_trace,
                reflective_frames=reflective_frames,
                reaction_records=reaction_records,
            ),
            "active_attention": active_attention,
            "recent_reading_memory": recent_reading_memory,
            "concept_registry": concept_registry,
            "thread_trace": thread_trace,
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
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
        actual_source_span=source_span if is_source_mainline else {},
        actual_source_span_id=source_id if is_source_mainline else "",
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
        source_span=source_span if is_source_mainline else None,
        status="running",
        phase="reading",
    )
    return {
        "local_buffer": local_buffer,
        "local_continuity": local_continuity,
        "active_attention": active_attention,
        "recent_reading_memory": recent_reading_memory,
        "concept_registry": concept_registry,
        "thread_trace": thread_trace,
        "reflective_frames": reflective_frames,
        "knowledge_activations": knowledge_activations,
        "reaction_records": reaction_records,
        "reconsolidation_records": reconsolidation_records,
        "bundle": bundle,
        "emitted_reactions": emitted_reactions,
        "current_source_ref": current_source_ref,
        "focal_sentence": focal_sentence,
        "source_cursor": dict(source_span.get("end_cursor", {})) if is_source_mainline and isinstance(source_span.get("end_cursor"), dict) else {},
        "source_span": source_span if is_source_mainline else {},
        "selected_source_unit": selected_source_unit if is_source_mainline else {},
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

        reader_policy: ReaderPolicy = bundle["reader_policy"]  # type: ignore[assignment]
        audit_window_max_units = _audit_window_max_units(request)
        audit_window_units_read = 0
        audit_window_stop_reason = ""
        touched_chapter_ids: set[int] = set()
        local_buffer: LocalBufferState = bundle["local_buffer"]  # type: ignore[assignment]
        local_continuity: LocalContinuityState = bundle["local_continuity"]  # type: ignore[assignment]
        active_attention: ActiveAttention = bundle["active_attention"]  # type: ignore[assignment]
        recent_reading_memory: RecentReadingMemoryState = bundle["recent_reading_memory"]  # type: ignore[assignment]
        concept_registry: ConceptRegistryState = bundle["concept_registry"]  # type: ignore[assignment]
        thread_trace: ThreadTraceState = bundle["thread_trace"]  # type: ignore[assignment]
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
                selection_result = navigate_choose_next_unit(
                    document=provisioned.book_document,
                    survey_map=survey_map,
                    sentence_lookup=sentence_lookup,
                    chapter_lookup=chapter_lookup,
                    current_chapter=chapter,
                    current_cursor=cursor,
                    local_buffer=local_buffer,
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,
                    recent_reading_memory=recent_reading_memory,
                    concept_registry=concept_registry,
                    thread_trace=thread_trace,
                    reflective_frames=reflective_frames,
                    reaction_records=reaction_records,
                    local_continuity=local_continuity,
                    reader_policy=reader_policy,
                    output_language=provisioned.output_language,
                    output_dir=output_dir,
                    book_title=provisioned.title,
                    author=provisioned.author,
                )
                settled_unit = _settle_next_unit(
                    selection_result=selection_result,
                    chapter_lookup=chapter_lookup,
                    local_buffer=local_buffer,
                    local_continuity=local_continuity,
                    continuation_capsule=dict(bundle.get("continuation_capsule", {})),
                    active_attention=active_attention,
                    recent_reading_memory=recent_reading_memory,
                    concept_registry=concept_registry,
                    thread_trace=thread_trace,
                    reflective_frames=reflective_frames,
                    knowledge_activations=knowledge_activations,
                    reaction_records=reaction_records,
                    reconsolidation_records=reconsolidation_records,
                    reader_policy=reader_policy,
                    output_language=provisioned.output_language,
                    output_dir=output_dir,
                    provisioned=provisioned,
                    bundle=bundle,
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
                concept_registry = settled_unit["concept_registry"]  # type: ignore[assignment]
                thread_trace = settled_unit["thread_trace"]  # type: ignore[assignment]
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
                concept_registry=concept_registry,
                thread_trace=thread_trace,
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
            concept_registry = phase6["concept_registry"]  # type: ignore[assignment]
            thread_trace = phase6["thread_trace"]  # type: ignore[assignment]
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
                        concept_registry=concept_registry,
                        thread_trace=thread_trace,
                        reflective_frames=reflective_frames,
                        reaction_records=reaction_records,
                    ),
                    "active_attention": active_attention,
                    "recent_reading_memory": recent_reading_memory,
                    "concept_registry": concept_registry,
                    "thread_trace": thread_trace,
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
