"""Benchmark-only probe exports for long-span memory-quality evaluation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schemas import (
    AnchorBankState,
    ConceptRegistryState,
    LocalBufferState,
    LocalContinuityState,
    MoveHistoryState,
    ReactionRecordsState,
    ReflectiveFramesState,
    ThreadTraceState,
    WorkingState,
)
from .state_projection import build_carry_forward_context
from .storage import load_json, memory_quality_probe_export_file, save_json


DEFAULT_MEMORY_QUALITY_PROBE_RATIOS = (0.2, 0.4, 0.6, 0.8, 1.0)
MEMORY_QUALITY_PROBE_EXPORT_SCHEMA_VERSION = 1


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Return one normalized string."""

    return str(value or "").strip()


def _normalize_threshold_ratios(raw_ratios: object) -> list[float]:
    """Return a bounded ordered probe-threshold list."""

    if not isinstance(raw_ratios, list):
        return list(DEFAULT_MEMORY_QUALITY_PROBE_RATIOS)
    normalized: list[float] = []
    for item in raw_ratios:
        try:
            ratio = float(item)
        except (TypeError, ValueError):
            continue
        ratio = max(0.0, min(1.0, ratio))
        if ratio <= 0.0:
            continue
        if ratio not in normalized:
            normalized.append(ratio)
    return normalized or list(DEFAULT_MEMORY_QUALITY_PROBE_RATIOS)


def memory_quality_probe_settings(mechanism_config: dict[str, object] | None) -> dict[str, object] | None:
    """Return normalized benchmark-only probe settings from mechanism config."""

    raw = dict(mechanism_config or {}).get("memory_quality_probe_export")
    if not isinstance(raw, dict) or not bool(raw.get("enabled")):
        return None
    return {
        "enabled": True,
        "segment_id": _clean_text(raw.get("segment_id")),
        "source_id": _clean_text(raw.get("source_id")),
        "book_title": _clean_text(raw.get("book_title")),
        "language_track": _clean_text(raw.get("language_track")),
        "threshold_ratios": _normalize_threshold_ratios(raw.get("threshold_ratios")),
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


def _build_probe_targets(
    *,
    ordered_sentence_ids: list[str],
    threshold_ratios: list[float],
) -> list[dict[str, object]]:
    """Build the deterministic sentence-threshold targets for probe capture."""

    total_sentences = len(ordered_sentence_ids)
    if total_sentences <= 0:
        return []
    targets: list[dict[str, object]] = []
    for probe_index, ratio in enumerate(threshold_ratios, start=1):
        target_ordinal = max(1, min(total_sentences, int(round(total_sentences * ratio))))
        target_sentence_id = _clean_text(ordered_sentence_ids[target_ordinal - 1])
        targets.append(
            {
                "probe_index": probe_index,
                "threshold_ratio": ratio,
                "target_sentence_ordinal": target_ordinal,
                "target_sentence_id": target_sentence_id,
            }
        )
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
    working_state: WorkingState,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    anchor_bank: AnchorBankState,
    move_history: MoveHistoryState,
    reaction_records: ReactionRecordsState,
) -> dict[str, object]:
    """Build one normalized probe snapshot from the current persisted V2 state."""

    carry_forward_context = build_carry_forward_context(
        chapter_ref=chapter_ref,
        current_unit_sentence_ids=[],
        local_buffer=local_buffer,
        working_state=working_state,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        anchor_bank=anchor_bank,
        move_history=move_history,
        reaction_records=reaction_records,
    )
    return {
        "probe_index": int(probe_target.get("probe_index", 0) or 0),
        "threshold_ratio": float(probe_target.get("threshold_ratio", 0.0) or 0.0),
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
        "working_state_digest": dict(carry_forward_context.get("working_state_digest", {}))
        if isinstance(carry_forward_context.get("working_state_digest"), dict)
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
        "anchor_bank_digest": dict(carry_forward_context.get("anchor_bank_digest", {}))
        if isinstance(carry_forward_context.get("anchor_bank_digest"), dict)
        else {},
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
    working_state: WorkingState,
    concept_registry: ConceptRegistryState,
    thread_trace: ThreadTraceState,
    reflective_frames: ReflectiveFramesState,
    anchor_bank: AnchorBankState,
    move_history: MoveHistoryState,
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
            "probe_targets": _build_probe_targets(
                ordered_sentence_ids=cleaned_sentence_ids,
                threshold_ratios=[
                    float(item)
                    for item in settings.get("threshold_ratios", DEFAULT_MEMORY_QUALITY_PROBE_RATIOS)
                    if isinstance(item, (int, float))
                ]
                or list(DEFAULT_MEMORY_QUALITY_PROBE_RATIOS),
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
            working_state=working_state,
            concept_registry=concept_registry,
            thread_trace=thread_trace,
            reflective_frames=reflective_frames,
            anchor_bank=anchor_bank,
            move_history=move_history,
            reaction_records=reaction_records,
        )
        payload.setdefault("snapshots", []).append(snapshot)
        existing_indexes.add(probe_index)
        new_snapshots.append(snapshot)

    if new_snapshots or not export_path.exists():
        payload["updated_at"] = _timestamp()
        save_json(export_path, payload)
    return new_snapshots
