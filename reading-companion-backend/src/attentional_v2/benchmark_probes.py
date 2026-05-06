"""Benchmark-only probe exports for long-span memory-quality evaluation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from .schemas import (
    ConceptRegistryState,
    LocalBufferState,
    LocalContinuityState,
    ReactionRecordsState,
    ReflectiveFramesState,
    ThreadTraceState,
    ActiveAttention,
)
from .state_projection import build_carry_forward_context
from .storage import load_json, memory_quality_probe_export_file, save_json


MEMORY_QUALITY_PROBE_EXPORT_SCHEMA_VERSION = 1


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Return one normalized string."""

    return str(value or "").strip()


def memory_quality_probe_settings(mechanism_config: dict[str, object] | None) -> dict[str, object] | None:
    """Return normalized benchmark-only probe settings from mechanism config."""

    raw = dict(mechanism_config or {}).get("memory_quality_probe_export")
    if not isinstance(raw, dict) or not bool(raw.get("enabled")):
        return None
    probe_targets = raw.get("probe_targets")
    if not isinstance(probe_targets, list) or not probe_targets:
        raise ValueError(
            "memory_quality_probe_export now requires explicit probe_targets; "
            "ratio-based Memory Quality probes were retired."
        )
    normalized_targets = [dict(item) for item in probe_targets if isinstance(item, dict)]
    if not normalized_targets:
        raise ValueError("memory_quality_probe_export probe_targets must contain target objects")
    return {
        "enabled": True,
        "segment_id": _clean_text(raw.get("segment_id")),
        "source_id": _clean_text(raw.get("source_id")),
        "book_title": _clean_text(raw.get("book_title")),
        "language_track": _clean_text(raw.get("language_track")),
        "probe_plan_id": _clean_text(raw.get("probe_plan_id")),
        "probe_plan_path": _clean_text(raw.get("probe_plan_path")),
        "probe_selection_method": _clean_text(raw.get("probe_selection_method")),
        "probe_targets": normalized_targets,
    }


def load_memory_quality_probe_export(output_dir: Path) -> dict[str, object]:
    """Load one persisted memory-quality probe export when present."""

    path = memory_quality_probe_export_file(output_dir)
    if not path.exists():
        return {}
    payload = load_json(path)
    return payload if isinstance(payload, dict) else {}


def is_memory_quality_probe_export_complete(output_dir: Path) -> bool:
    """Return whether all configured probe snapshots are already captured."""

    payload = load_memory_quality_probe_export(output_dir)
    probe_targets = payload.get("probe_targets", [])
    if not isinstance(probe_targets, list) or not probe_targets:
        return False
    completed_indexes = {
        int(item.get("probe_index", 0) or 0)
        for item in payload.get("snapshots", [])
        if isinstance(item, dict) and int(item.get("probe_index", 0) or 0) > 0
    }
    target_indexes = {
        int(item.get("probe_index", 0) or 0)
        for item in probe_targets
        if isinstance(item, dict) and int(item.get("probe_index", 0) or 0) > 0
    }
    return bool(target_indexes) and completed_indexes.issuperset(target_indexes)


def _normalize_probe_targets(
    *,
    ordered_sentence_ids: list[str],
    configured_targets: object,
) -> list[dict[str, object]]:
    """Normalize explicit semantic probe targets against the current window sentence ids."""

    total_sentences = len(ordered_sentence_ids)
    if total_sentences <= 0:
        return []
    if not isinstance(configured_targets, list) or not configured_targets:
        raise ValueError(
            "memory_quality_probe_export requires explicit probe_targets; "
            "hard-ratio probe construction is no longer supported."
        )
    sentence_ordinals = {sentence_id: index + 1 for index, sentence_id in enumerate(ordered_sentence_ids)}
    targets: list[dict[str, object]] = []
    previous_ordinal = 0
    for index, raw_target in enumerate(configured_targets, start=1):
        if not isinstance(raw_target, dict):
            raise ValueError(f"invalid memory-quality probe target at index {index}: expected object")
        target_sentence_id = _clean_text(raw_target.get("target_sentence_id"))
        if not target_sentence_id:
            raw_ordinal = raw_target.get("target_sentence_ordinal")
            try:
                target_ordinal = int(raw_ordinal)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"probe target {index} is missing target_sentence_id") from exc
            if target_ordinal < 1 or target_ordinal > total_sentences:
                raise ValueError(f"probe target {index} ordinal is outside the window: {target_ordinal}")
            target_sentence_id = ordered_sentence_ids[target_ordinal - 1]
        if target_sentence_id not in sentence_ordinals:
            raise ValueError(f"probe target {index} sentence is outside the window: {target_sentence_id}")
        target_ordinal = sentence_ordinals[target_sentence_id]
        if target_ordinal <= previous_ordinal:
            raise ValueError("memory-quality probe targets must be in strictly increasing sentence order")
        previous_ordinal = target_ordinal
        target = dict(raw_target)
        target["probe_index"] = int(target.get("probe_index") or index)
        target["target_sentence_id"] = target_sentence_id
        target["target_sentence_ordinal"] = target_ordinal
        targets.append(target)
    return targets


def _recent_reading_orientation(
    *,
    local_buffer: LocalBufferState,
    local_continuity: LocalContinuityState,
) -> dict[str, object]:
    """Build a tiny orientation block for benchmark-only probe judging."""

    recent_sentence_ids = [
        _clean_text(sentence.get("sentence_id"))
        for sentence in local_buffer.get("recent_sentences", [])
        if isinstance(sentence, dict) and _clean_text(sentence.get("sentence_id"))
    ][-6:]
    recent_meaning_units = [
        {
            "sentence_ids": [
                _clean_text(sentence_id)
                for sentence_id in unit
                if _clean_text(sentence_id)
            ]
        }
        for unit in local_buffer.get("recent_meaning_units", [])
        if isinstance(unit, list)
    ][-2:]
    return {
        "chapter_ref": _clean_text(local_continuity.get("chapter_ref")),
        "current_sentence_id": _clean_text(local_continuity.get("current_sentence_id")),
        "recent_sentence_ids": recent_sentence_ids,
        "recent_meaning_units": recent_meaning_units,
        "reading_queue_stage": _clean_text(local_continuity.get("reading_queue_stage")),
    }


def _build_probe_snapshot(
    *,
    probe_target: dict[str, object],
    window_start_sentence_id: str,
    actual_sentence_id: str,
    actual_sentence_ordinal: int,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    local_continuity: LocalContinuityState,
    active_attention: ActiveAttention,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
) -> dict[str, object]:
    """Build one normalized probe snapshot from the current persisted mechanism state."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[],
        local_buffer=local_buffer,
        active_attention=active_attention,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )
    return {
        "probe_index": int(probe_target.get("probe_index", 0) or 0),
        "estimated_ratio": float(probe_target.get("estimated_ratio", 0.0) or 0.0),
        "rough_position_target": _clean_text(probe_target.get("rough_position_target")),
        "boundary_kind": _clean_text(probe_target.get("boundary_kind")),
        "why_this_probe_point": _clean_text(probe_target.get("why_this_probe_point")),
        "structural_signals_to_check": [
            _clean_text(item)
            for item in probe_target.get("structural_signals_to_check", [])
            if _clean_text(item)
        ]
        if isinstance(probe_target.get("structural_signals_to_check"), list)
        else [],
        "target_sentence_ordinal": int(probe_target.get("target_sentence_ordinal", 0) or 0),
        "target_sentence_id": _clean_text(probe_target.get("target_sentence_id")),
        "captured_at": _timestamp(),
        "capture_sentence_ordinal": actual_sentence_ordinal,
        "capture_sentence_id": actual_sentence_id,
        "coverage": {
            "start_sentence_id": window_start_sentence_id,
            "end_sentence_id": actual_sentence_id,
            "sentence_count": actual_sentence_ordinal,
        },
        "continuity_context": dict(carry_forward_context.get("session_continuity_capsule", {}))
        if isinstance(carry_forward_context.get("session_continuity_capsule"), dict)
        else {},
        "active_attention_digest": dict(carry_forward_context.get("active_attention_digest", {}))
        if isinstance(carry_forward_context.get("active_attention_digest"), dict)
        else {},
        "concept_digest": [
            dict(item)
            for item in carry_forward_context.get("concept_digest", [])
            if isinstance(item, dict)
        ],
        "thread_digest": [
            dict(item)
            for item in carry_forward_context.get("thread_digest", [])
            if isinstance(item, dict)
        ],
        "reflective_digest": dict(carry_forward_context.get("chapter_reflective_frame", {}))
        if isinstance(carry_forward_context.get("chapter_reflective_frame"), dict)
        else {},
        "active_focus_digest": dict(carry_forward_context.get("active_focus_digest", {}))
        if isinstance(carry_forward_context.get("active_focus_digest"), dict)
        else {},
        "source_ref_digest": [
            dict(item)
            for item in carry_forward_context.get("source_ref_digest", [])
            if isinstance(item, dict)
        ],
        "recent_reading_orientation": _recent_reading_orientation(
            local_buffer=local_buffer,
            local_continuity=local_continuity,
        ),
    }


def persist_due_memory_quality_probe_snapshots(
    *,
    output_dir: Path,
    settings: dict[str, object] | None,
    ordered_sentence_ids: list[str],
    actual_sentence_id: str,
    chapter_ref: str,
    local_buffer: LocalBufferState,
    local_continuity: LocalContinuityState,
    active_attention: ActiveAttention,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    reaction_records: ReactionRecordsState,
) -> list[dict[str, object]]:
    """Persist any probe snapshots whose threshold is crossed by this completed read step."""

    if not isinstance(settings, dict) or not bool(settings.get("enabled")):
        return []

    cleaned_sentence_ids = [_clean_text(sentence_id) for sentence_id in ordered_sentence_ids if _clean_text(sentence_id)]
    if not cleaned_sentence_ids:
        return []
    cleaned_actual_sentence_id = _clean_text(actual_sentence_id)
    if not cleaned_actual_sentence_id or cleaned_actual_sentence_id not in cleaned_sentence_ids:
        return []

    export_path = memory_quality_probe_export_file(output_dir)
    payload = load_memory_quality_probe_export(output_dir)
    if not payload:
        payload = {
            "schema_version": MEMORY_QUALITY_PROBE_EXPORT_SCHEMA_VERSION,
            "mechanism_key": "attentional_v2",
            "segment_id": _clean_text(settings.get("segment_id")),
            "source_id": _clean_text(settings.get("source_id")),
            "book_title": _clean_text(settings.get("book_title")),
            "language_track": _clean_text(settings.get("language_track")),
            "total_sentence_count": len(cleaned_sentence_ids),
            "probe_plan_id": _clean_text(settings.get("probe_plan_id")),
            "probe_plan_path": _clean_text(settings.get("probe_plan_path")),
            "probe_selection_method": _clean_text(settings.get("probe_selection_method")),
            "probe_targets": _normalize_probe_targets(
                ordered_sentence_ids=cleaned_sentence_ids,
                configured_targets=settings.get("probe_targets"),
            ),
            "snapshots": [],
            "updated_at": _timestamp(),
        }
    existing_indexes = {
        int(item.get("probe_index", 0) or 0)
        for item in payload.get("snapshots", [])
        if isinstance(item, dict) and int(item.get("probe_index", 0) or 0) > 0
    }
    actual_sentence_ordinal = cleaned_sentence_ids.index(cleaned_actual_sentence_id) + 1
    window_start_sentence_id = cleaned_sentence_ids[0]
    new_snapshots: list[dict[str, object]] = []
    for probe_target in payload.get("probe_targets", []):
        if not isinstance(probe_target, dict):
            continue
        probe_index = int(probe_target.get("probe_index", 0) or 0)
        target_ordinal = int(probe_target.get("target_sentence_ordinal", 0) or 0)
        if probe_index <= 0 or target_ordinal <= 0 or probe_index in existing_indexes:
            continue
        if actual_sentence_ordinal < target_ordinal:
            continue
        snapshot = _build_probe_snapshot(
            probe_target=probe_target,
            window_start_sentence_id=window_start_sentence_id,
            actual_sentence_id=cleaned_actual_sentence_id,
            actual_sentence_ordinal=actual_sentence_ordinal,
            chapter_ref=chapter_ref,
            local_buffer=local_buffer,
            local_continuity=local_continuity,
            active_attention=active_attention,
            concept_registry=concept_registry,
            thread_trace=thread_trace,
            reflective_frames=reflective_frames,
            reaction_records=reaction_records,
        )
        payload.setdefault("snapshots", []).append(snapshot)
        existing_indexes.add(probe_index)
        new_snapshots.append(snapshot)

    if new_snapshots or not export_path.exists():
        payload["updated_at"] = _timestamp()
        save_json(export_path, payload)
    return new_snapshots
