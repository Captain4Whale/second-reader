"""Phase 8 observability helpers for standard vs debug persistence."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

from src.reading_core.runtime_contracts import ObservabilityMode, RuntimeArtifactRefs
from src.reading_runtime import artifacts as runtime_artifacts

from .benchmark_probes import (
    memory_quality_probe_settings as _memory_quality_probe_settings,
    persist_due_memory_quality_probe_snapshots,
)
from .schemas import (
    ActiveAttention,
    CarryForwardContext,
    ConceptRegistryState,
    ContextRequest,
    FullCheckpointState,
    LocalBufferState,
    LocalContinuityState,
    ReactionRecordsState,
    ReaderPolicy,
    ReflectiveFramesState,
    ThreadTraceState,
    UnitizeDecision,
)
from .state_projection import build_supplemental_selective_carry, context_ref_ids
from .storage import append_jsonl, event_stream_file, read_audit_file, settlement_audit_file, unitization_audit_file

_MISSING_TARGET_STORE_WARNING = "missing_target_store_defaulted"
_SETTLED_STORE_ID_KEYS = {
    "active_attention": "item_id",
    "concept_registry": "concept_key",
    "thread_trace": "thread_key",
}
_OUTCOME_BASIS = "audit_observed_inferred_from_compact_state_delta"


def _timestamp() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    """Return one normalized string."""

    return str(value or "").strip()


def _logging_policy(reader_policy: Mapping[str, object] | None) -> Mapping[str, object]:
    """Return the logging policy subsection when available."""

    if not isinstance(reader_policy, Mapping):
        return {}
    logging = reader_policy.get("logging")
    return logging if isinstance(logging, Mapping) else {}


def observability_mode(reader_policy: Mapping[str, object] | None) -> ObservabilityMode:
    """Return the effective observability mode for one run."""

    mode = _clean_text(_logging_policy(reader_policy).get("observability_mode"))
    return "debug" if mode == "debug" else "standard"


def debug_event_stream_enabled(reader_policy: Mapping[str, object] | None) -> bool:
    """Whether debug-only event diagnostics should be emitted."""

    logging = _logging_policy(reader_policy)
    return observability_mode(reader_policy) == "debug" or bool(logging.get("debug_event_stream", False))


def debug_checkpoint_diagnostics_enabled(reader_policy: Mapping[str, object] | None) -> bool:
    """Whether richer checkpoint diagnostics should be emitted in debug mode."""

    logging = _logging_policy(reader_policy)
    return observability_mode(reader_policy) == "debug" or bool(logging.get("debug_checkpoint_diagnostics", False))


def standard_event_stream_enabled(reader_policy: Mapping[str, object] | None) -> bool:
    """Whether the shared standard activity stream should be emitted."""

    return bool(_logging_policy(reader_policy).get("event_stream", True))


def _append_shared_jsonl(path: Path, payload: object) -> None:
    """Append one JSONL line to a shared runtime file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False))
        file.write("\n")


def record_unitization(
    output_dir: Path | None,
    *,
    chapter_id: int,
    chapter_ref: str,
    unitize_decision: UnitizeDecision,
) -> None:
    """Append one mechanism-private unitization audit record."""

    if output_dir is None:
        return
    append_jsonl(
        unitization_audit_file(output_dir),
        {
            "recorded_at": _timestamp(),
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
            "unitize_decision": dict(unitize_decision),
        },
    )


def _normalized_operations(value: object) -> list[dict[str, object]]:
    """Return normalized operation dictionaries for audit persistence."""

    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _memory_uptake_ops(read_result: Mapping[str, object]) -> list[dict[str, object]]:
    """Return normalized read memory operations for audit persistence."""

    return _normalized_operations(read_result.get("memory_uptake_ops"))


def _memory_uptake_admission_events(read_result: Mapping[str, object]) -> list[dict[str, object]]:
    """Return audit-only admission metadata for read memory operations."""

    return _normalized_operations(read_result.get("memory_uptake_admission_events"))


def _memory_uptake_ops_by_target_store(memory_uptake_ops: list[dict[str, object]]) -> dict[str, int]:
    """Count read memory operations by their declared target store."""

    counts: Counter[str] = Counter()
    for operation in memory_uptake_ops:
        target_store = _clean_text(operation.get("target_store")) or "unspecified"
        counts[target_store] += 1
    return dict(sorted(counts.items()))


def _operation_payload(operation: Mapping[str, object]) -> Mapping[str, object]:
    """Return one operation payload as a mapping."""

    payload = operation.get("payload")
    return payload if isinstance(payload, Mapping) else {}


def _operation_type(operation: Mapping[str, object]) -> str:
    """Return the normalized operation type used for audit only."""

    return _clean_text(operation.get("op") or operation.get("operation_type")).lower().replace("-", "_")


def _target_store_emitted(operation: Mapping[str, object]) -> str:
    """Return the target store emitted by the source op before compatibility defaults."""

    if "target_store_emitted" in operation:
        return _clean_text(operation.get("target_store_emitted"))
    return _clean_text(operation.get("target_store"))


def _effective_target_store(operation: Mapping[str, object]) -> str:
    """Return the target store used by the current runtime after compatibility defaults."""

    return _clean_text(operation.get("effective_target_store")) or _clean_text(operation.get("target_store")) or "active_attention"


def _compatibility_warnings(operation: Mapping[str, object]) -> list[str]:
    """Return additive compatibility warnings for one memory op."""

    warnings: list[str] = []
    raw_warnings = operation.get("compatibility_warnings")
    if isinstance(raw_warnings, list):
        warnings.extend(_clean_text(item) for item in raw_warnings if _clean_text(item))
    if (
        not _target_store_emitted(operation)
        and _effective_target_store(operation) == "active_attention"
        and _MISSING_TARGET_STORE_WARNING not in warnings
    ):
        warnings.append(_MISSING_TARGET_STORE_WARNING)
    return warnings


def _source_ref_summary(operation: Mapping[str, object]) -> tuple[int, list[str]]:
    """Return source-ref count and resolution statuses for audit rows."""

    source_refs = _operation_payload(operation).get("source_refs")
    if not isinstance(source_refs, list):
        return 0, []
    count = 0
    statuses: list[str] = []
    for source_ref in source_refs:
        if not isinstance(source_ref, Mapping):
            continue
        count += 1
        resolution = source_ref.get("resolution")
        status = _clean_text(resolution.get("status")) if isinstance(resolution, Mapping) else ""
        if status and status not in statuses:
            statuses.append(status)
    return count, statuses


def _operation_target_identifier(operation: Mapping[str, object], effective_target_store: str) -> str:
    """Return the id that compact state deltas can observe for one operation."""

    payload = _operation_payload(operation)
    explicit_id = _clean_text(operation.get("target_key") or operation.get("item_id"))
    if explicit_id:
        return explicit_id
    if effective_target_store == "concept_registry":
        return _clean_text(payload.get("concept_key"))
    if effective_target_store == "thread_trace":
        return _clean_text(payload.get("thread_key"))
    return _clean_text(payload.get("item_id"))


def _memory_uptake_op_contract(operation: Mapping[str, object], operation_index: int) -> dict[str, object]:
    """Build additive audit-contract metadata for one memory uptake operation."""

    source_ref_count, source_ref_resolution_statuses = _source_ref_summary(operation)
    target_key = _clean_text(operation.get("target_key") or operation.get("item_id"))
    item_id = _clean_text(operation.get("item_id") or operation.get("target_key"))
    return {
        "operation_index": operation_index,
        "operation_type": _operation_type(operation),
        "target_store_emitted": _target_store_emitted(operation),
        "effective_target_store": _effective_target_store(operation),
        "target_key": target_key,
        "item_id": item_id,
        "source_ref_count": source_ref_count,
        "source_ref_resolution_statuses": source_ref_resolution_statuses,
        "compatibility_warnings": _compatibility_warnings(operation),
    }


def _memory_uptake_op_contracts(memory_uptake_ops: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return additive contract metadata for read audit rows."""

    return [_memory_uptake_op_contract(operation, index) for index, operation in enumerate(memory_uptake_ops)]


def _id_delta_contains(delta: Mapping[str, object], target_id: str) -> bool:
    """Whether one compact id delta observed the target id."""

    for key in ("added_ids", "updated_ids", "removed_ids"):
        values = delta.get(key)
        if isinstance(values, list) and target_id in {_clean_text(item) for item in values}:
            return True
    return False


def _memory_uptake_op_outcomes(
    memory_uptake_ops: list[dict[str, object]],
    state_deltas: Mapping[str, object],
) -> list[dict[str, object]]:
    """Return audit-observed, non-authoritative per-op settlement outcomes."""

    target_counts: dict[tuple[str, str], int] = {}
    for operation in memory_uptake_ops:
        effective_target_store = _effective_target_store(operation)
        target_id = _operation_target_identifier(operation, effective_target_store)
        if target_id:
            key = (effective_target_store, target_id)
            target_counts[key] = target_counts.get(key, 0) + 1

    outcomes: list[dict[str, object]] = []
    for index, operation in enumerate(memory_uptake_ops):
        contract = _memory_uptake_op_contract(operation, index)
        effective_target_store = _clean_text(contract.get("effective_target_store"))
        target_id = _operation_target_identifier(operation, effective_target_store)
        if effective_target_store not in _SETTLED_STORE_ID_KEYS:
            outcome = "skipped_out_of_scope"
        elif not target_id:
            outcome = "unclassified"
        elif target_counts.get((effective_target_store, target_id), 0) > 1:
            outcome = "unclassified"
        else:
            delta = state_deltas.get(effective_target_store)
            if isinstance(delta, Mapping) and _id_delta_contains(delta, target_id):
                outcome = "accepted_observed"
            elif isinstance(delta, Mapping):
                outcome = "accepted_no_visible_delta"
            else:
                outcome = "unclassified"
        outcomes.append(
            {
                **contract,
                "target_id": target_id,
                "outcome": outcome,
                "outcome_basis": _OUTCOME_BASIS,
            }
        )
    return outcomes


def _items_by_id(items: object, id_key: str) -> dict[str, dict[str, object]]:
    """Return mapping-friendly items keyed by a stable id field."""

    if not isinstance(items, list):
        return {}
    indexed: dict[str, dict[str, object]] = {}
    for item in items:
        if not isinstance(item, Mapping):
            continue
        item_id = _clean_text(item.get(id_key))
        if item_id:
            indexed[item_id] = dict(item)
    return indexed


def _id_delta(before_items: object, after_items: object, *, id_key: str) -> dict[str, object]:
    """Return a compact before/after id diff without persisting full item payloads."""

    before = _items_by_id(before_items, id_key)
    after = _items_by_id(after_items, id_key)
    before_ids = set(before)
    after_ids = set(after)
    return {
        "before_count": len(before),
        "after_count": len(after),
        "added_ids": sorted(after_ids - before_ids),
        "updated_ids": sorted(item_id for item_id in before_ids & after_ids if before[item_id] != after[item_id]),
        "removed_ids": sorted(before_ids - after_ids),
    }


def _dedupe_sorted_ids(values: list[str]) -> list[str]:
    """Return sorted unique ids while dropping empty values."""

    return sorted({_clean_text(value) for value in values if _clean_text(value)})


def _ref_identifier(item: Mapping[str, object]) -> str:
    """Return the compact id for one supplemental ref-like item."""

    return _clean_text(item.get("ref_id")) or _clean_text(item.get("source_span_id"))


def _ref_ids_from_items(items: object) -> list[str]:
    """Collect compact ids from one list of ref-like dictionaries."""

    if not isinstance(items, list):
        return []
    return [
        item_id
        for item in items
        if isinstance(item, Mapping)
        for item_id in [_ref_identifier(item)]
        if item_id
    ]


def _id_summary(ref_ids: list[str]) -> dict[str, object]:
    """Return compact count-plus-id audit metadata."""

    deduped = _dedupe_sorted_ids(ref_ids)
    return {"count": len(deduped), "ref_ids": deduped}


def _supplemental_refs_returned(supplemental_context: Mapping[str, object]) -> dict[str, object]:
    """Return compact ids for refs available from supplemental context."""

    return _id_summary(
        [
            *_ref_ids_from_items(supplemental_context.get("source_refs")),
            *_ref_ids_from_items(supplemental_context.get("excerpts")),
            *_ref_ids_from_items(supplemental_context.get("refs")),
        ]
    )


def _supplemental_refs_forwarded(selective_carry: Mapping[str, object]) -> dict[str, object]:
    """Return compact ids for refs forwarded into the prompt-facing selective carry."""

    return _id_summary(
        [
            *_ref_ids_from_items(selective_carry.get("source_ref_details")),
            *_ref_ids_from_items(selective_carry.get("earlier_excerpts")),
            *_ref_ids_from_items(selective_carry.get("supporting_refs")),
        ]
    )


def _source_refs_available(supplemental_context: Mapping[str, object]) -> dict[str, object]:
    """Return compact source-calibration refs available in supplemental context."""

    source_ref_ids = [
        *_ref_ids_from_items(supplemental_context.get("source_refs")),
        *_ref_ids_from_items(supplemental_context.get("excerpts")),
    ]
    refs = supplemental_context.get("refs")
    if isinstance(refs, list):
        source_ref_ids.extend(
            _ref_identifier(ref)
            for ref in refs
            if isinstance(ref, Mapping) and _clean_text(ref.get("kind")) == "source" and _ref_identifier(ref)
        )
    return _id_summary(source_ref_ids)


def _is_visible_trace_ref(ref: Mapping[str, object]) -> bool:
    """Whether one supplemental ref is visible trace rather than semantic memory."""

    return (
        _clean_text(ref.get("kind")) == "reaction"
        or _clean_text(ref.get("result_role")) == "visible_trace"
        or ref.get("semantic_memory") is False
    )


def _visible_trace_refs_available(supplemental_context: Mapping[str, object]) -> dict[str, object]:
    """Return compact visible-trace refs available in supplemental context."""

    ref_ids: list[str] = []
    refs = supplemental_context.get("refs")
    if isinstance(refs, list):
        ref_ids.extend(
            _ref_identifier(ref)
            for ref in refs
            if isinstance(ref, Mapping) and _is_visible_trace_ref(ref) and _ref_identifier(ref)
        )
    reactions = supplemental_context.get("reactions")
    if isinstance(reactions, list):
        ref_ids.extend(
            _ref_identifier(reaction)
            for reaction in reactions
            if isinstance(reaction, Mapping) and _ref_identifier(reaction)
        )
    return _id_summary(ref_ids)


def _memory_refs_available(supplemental_context: Mapping[str, object]) -> dict[str, object]:
    """Return compact memory refs, excluding source-calibration and visible-trace refs."""

    ref_ids: list[str] = []
    refs = supplemental_context.get("refs")
    if isinstance(refs, list):
        ref_ids.extend(
            _ref_identifier(ref)
            for ref in refs
            if isinstance(ref, Mapping)
            and _clean_text(ref.get("kind")) != "source"
            and not _is_visible_trace_ref(ref)
            and _ref_identifier(ref)
        )
    for key in ("concepts", "threads", "reflective_items"):
        ref_ids.extend(_ref_ids_from_items(supplemental_context.get(key)))
    return _id_summary(ref_ids)


def _supplemental_retrieval_audit(supplemental_context: dict[str, object] | None) -> dict[str, object]:
    """Return compact supplemental retrieval audit metadata when available."""

    if not isinstance(supplemental_context, dict):
        return {}
    selective_carry = build_supplemental_selective_carry(supplemental_context)
    retrieval_context = selective_carry.get("retrieval_context")
    if not isinstance(retrieval_context, Mapping):
        return {}
    return {
        "retrieval_intent": _clean_text(retrieval_context.get("retrieval_intent")),
        "result_boundary": _clean_text(retrieval_context.get("result_boundary")),
        "result_groups": [
            _clean_text(item)
            for item in retrieval_context.get("result_groups", [])
            if _clean_text(item)
        ]
        if isinstance(retrieval_context.get("result_groups"), list)
        else [],
        "retrieval_events": [
            dict(item)
            for item in retrieval_context.get("retrieval_events", [])
            if isinstance(item, Mapping)
        ]
        if isinstance(retrieval_context.get("retrieval_events"), list)
        else [],
        "forwarded_result_groups": [
            _clean_text(item)
            for item in retrieval_context.get("forwarded_result_groups", [])
            if _clean_text(item)
        ]
        if isinstance(retrieval_context.get("forwarded_result_groups"), list)
        else [],
        "not_forwarded_result_groups": [
            _clean_text(item)
            for item in retrieval_context.get("not_forwarded_result_groups", [])
            if _clean_text(item)
        ]
        if isinstance(retrieval_context.get("not_forwarded_result_groups"), list)
        else [],
        "supplemental_refs_returned": _supplemental_refs_returned(supplemental_context),
        "supplemental_refs_forwarded_to_prompt": _supplemental_refs_forwarded(selective_carry),
        "source_refs_available": _source_refs_available(supplemental_context),
        "memory_refs_available": _memory_refs_available(supplemental_context),
        "visible_trace_refs_available": _visible_trace_refs_available(supplemental_context),
        "utilization_observed": False,
        "utilization_basis": "not_claimed_by_read_output",
    }


def record_read(
    output_dir: Path | None,
    *,
    chapter_id: int,
    chapter_ref: str,
    unitize_decision: UnitizeDecision,
    carry_forward_context: CarryForwardContext,
    source_unit: Mapping[str, object] | None = None,
    context_request: ContextRequest | None = None,
    supplemental_context: dict[str, object] | None = None,
    supplemental_satisfied: bool = False,
    supplemental_steps: list[dict[str, object]] | None = None,
    stop_reason: str = "",
    budget_exhausted: bool = False,
    read_result: Mapping[str, object],
    llm_fallbacks: list[dict[str, str]] | None = None,
    navigation_trace: list[dict[str, object]] | None = None,
    detour_trace_evidence: dict[str, object] | None = None,
) -> None:
    """Append one mechanism-private read audit record."""

    if output_dir is None:
        return
    surfaced_reactions = (
        [dict(item) for item in read_result.get("surfaced_reactions", []) if isinstance(item, Mapping)]
        if isinstance(read_result.get("surfaced_reactions"), list)
        else []
    )
    memory_uptake_ops = _memory_uptake_ops(read_result)
    memory_uptake_admission_events = _memory_uptake_admission_events(read_result)
    row = {
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "unitize_decision": dict(unitize_decision),
        "source_span": dict(source_unit.get("source_span", {}))
        if isinstance(source_unit, Mapping) and isinstance(source_unit.get("source_span"), Mapping)
        else {},
        "source_span_id": _clean_text(source_unit.get("source_span_id"))
        if isinstance(source_unit, Mapping)
        else "",
        "unit_char_count": int(source_unit.get("char_count", 0) or 0)
        if isinstance(source_unit, Mapping)
        else 0,
        "unit_paragraph_count": int(source_unit.get("paragraph_count", 0) or 0)
        if isinstance(source_unit, Mapping)
        else 0,
        "carry_forward_ref_ids": sorted(context_ref_ids(carry_forward_context)),
        "context_request": dict(context_request or {}),
        "supplemental_ref_ids": sorted(context_ref_ids(supplemental_context)),
        "supplemental_satisfied": supplemental_satisfied,
        "supplemental_steps": [dict(step) for step in (supplemental_steps or []) if isinstance(step, Mapping)],
        "stop_reason": _clean_text(stop_reason),
        "budget_exhausted": bool(budget_exhausted),
        "reading_impression": _clean_text(read_result.get("reading_impression")),
        "surfaced_reaction_count": len(surfaced_reactions),
        "surfaced_reactions": surfaced_reactions,
        "memory_uptake_ops": memory_uptake_ops,
        "memory_uptake_op_count": len(memory_uptake_ops),
        "memory_uptake_ops_by_target_store": _memory_uptake_ops_by_target_store(memory_uptake_ops),
        "memory_uptake_op_contracts": _memory_uptake_op_contracts(memory_uptake_ops),
        "memory_uptake_admission_events": memory_uptake_admission_events,
        "detour_need": dict(read_result.get("detour_need") or {})
        if isinstance(read_result.get("detour_need"), Mapping)
        else {},
        "llm_fallbacks": [dict(item) for item in (llm_fallbacks or []) if isinstance(item, Mapping)],
    }
    supplemental_retrieval = _supplemental_retrieval_audit(supplemental_context)
    if supplemental_retrieval:
        row["supplemental_retrieval"] = supplemental_retrieval
    compact_navigation_trace = [dict(item) for item in (navigation_trace or []) if isinstance(item, Mapping)]
    if compact_navigation_trace:
        row["navigation_trace"] = compact_navigation_trace
    if isinstance(detour_trace_evidence, Mapping) and detour_trace_evidence:
        row["detour_trace_evidence"] = dict(detour_trace_evidence)
    append_jsonl(read_audit_file(output_dir), row)


def record_settlement(
    output_dir: Path | None,
    *,
    chapter_id: int,
    chapter_ref: str,
    unit_sentence_ids: list[str],
    focal_sentence_id: str,
    memory_uptake_ops: object,
    before_active_attention: ActiveAttention,
    after_active_attention: ActiveAttention,
    before_concept_registry: ConceptRegistryState,
    after_concept_registry: ConceptRegistryState,
    before_thread_trace: ThreadTraceState,
    after_thread_trace: ThreadTraceState,
    before_reaction_records: ReactionRecordsState,
    after_reaction_records: ReactionRecordsState,
    emitted_reaction_ids: list[str] | None = None,
    source_span: Mapping[str, object] | None = None,
    source_span_id: str = "",
) -> None:
    """Append one compact transaction summary for a completed unit settlement."""

    if output_dir is None:
        return
    normalized_ops = _normalized_operations(memory_uptake_ops)
    state_deltas = {
        "active_attention": _id_delta(
            before_active_attention.get("active_items", []),
            after_active_attention.get("active_items", []),
            id_key="item_id",
        ),
        "concept_registry": _id_delta(
            before_concept_registry.get("entries", []),
            after_concept_registry.get("entries", []),
            id_key="concept_key",
        ),
        "thread_trace": _id_delta(
            before_thread_trace.get("entries", []),
            after_thread_trace.get("entries", []),
            id_key="thread_key",
        ),
        "reaction_records": {
            **_id_delta(
                before_reaction_records.get("records", []),
                after_reaction_records.get("records", []),
                id_key="reaction_id",
            ),
            "emitted_reaction_ids": [_clean_text(item) for item in (emitted_reaction_ids or []) if _clean_text(item)],
        },
    }
    append_jsonl(
        settlement_audit_file(output_dir),
        {
            "recorded_at": _timestamp(),
            "chapter_id": chapter_id,
            "chapter_ref": chapter_ref,
            "unit_sentence_ids": [_clean_text(item) for item in unit_sentence_ids if _clean_text(item)],
            "focal_sentence_id": _clean_text(focal_sentence_id),
            "source_span": dict(source_span or {}),
            "source_span_id": _clean_text(source_span_id),
            "memory_uptake_op_count": len(normalized_ops),
            "memory_uptake_ops_by_target_store": _memory_uptake_ops_by_target_store(normalized_ops),
            "memory_uptake_op_outcomes": _memory_uptake_op_outcomes(normalized_ops, state_deltas),
            "state_deltas": state_deltas,
        },
    )


def memory_quality_probe_observability_settings(
    mechanism_config: dict[str, object] | None,
) -> dict[str, object] | None:
    """Return normalized benchmark-only probe settings for observability hooks."""

    return _memory_quality_probe_settings(mechanism_config)


def maybe_capture_memory_quality_probe(
    *,
    capture_enabled: bool,
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
    """Capture benchmark probe snapshots through the runtime observability boundary."""

    if not capture_enabled:
        return []
    return persist_due_memory_quality_probe_snapshots(
        output_dir=output_dir,
        settings=settings,
        ordered_sentence_ids=ordered_sentence_ids,
        actual_sentence_id=actual_sentence_id,
        chapter_ref=chapter_ref,
        local_buffer=local_buffer,
        local_continuity=local_continuity,
        active_attention=active_attention,
        concept_registry=concept_registry,
        thread_trace=thread_trace,
        reflective_frames=reflective_frames,
        reaction_records=reaction_records,
    )


def reading_locus_from_cursor(cursor: Mapping[str, object] | None) -> dict[str, object] | None:
    """Project a shared cursor into the additive public reading-locus shape."""

    if not isinstance(cursor, Mapping):
        return None
    kind = _clean_text(cursor.get("position_kind"))
    if kind not in {"chapter", "sentence", "span"}:
        kind = "chapter"
    locus: dict[str, object] = {"kind": kind}
    chapter_id = cursor.get("chapter_id")
    if isinstance(chapter_id, int):
        locus["chapter_id"] = chapter_id
    chapter_ref = _clean_text(cursor.get("chapter_ref"))
    if chapter_ref:
        locus["chapter_ref"] = chapter_ref
    span_start_cursor = cursor.get("span_start_cursor")
    span_end_cursor = cursor.get("span_end_cursor")
    if isinstance(span_start_cursor, Mapping) or isinstance(span_end_cursor, Mapping) or cursor.get("paragraph_index") is not None:
        locus["kind"] = "source_span" if kind == "span" else "source_cursor"
        if isinstance(span_start_cursor, Mapping):
            locus["start_cursor"] = dict(span_start_cursor)
        else:
            locus["start_cursor"] = {
                "chapter_id": chapter_id,
                "chapter_ref": chapter_ref,
                "paragraph_index": cursor.get("paragraph_index"),
                "char_offset": cursor.get("char_offset"),
            }
        if isinstance(span_end_cursor, Mapping):
            locus["end_cursor"] = dict(span_end_cursor)
        if len(locus) == 1 and kind == "chapter":
            return None
        return locus
    sentence_id = _clean_text(cursor.get("sentence_id"))
    start_id = _clean_text(cursor.get("span_start_sentence_id")) or sentence_id
    end_id = _clean_text(cursor.get("span_end_sentence_id")) or sentence_id or start_id
    if start_id:
        locus["sentence_start_id"] = start_id
    if end_id:
        locus["sentence_end_id"] = end_id
    if len(locus) == 1 and kind == "chapter":
        return None
    return locus


def _checkpoint_state_counts(checkpoint: FullCheckpointState) -> dict[str, int]:
    """Return compact checkpoint counts that are useful for debug forensics."""

    local_buffer = checkpoint.get("local_buffer", {})
    concept_registry = checkpoint.get("concept_registry", {})
    thread_trace = checkpoint.get("thread_trace", {})
    reflective_frames = checkpoint.get("reflective_frames", {}) or checkpoint.get("reflective_summaries", {})
    knowledge_activations = checkpoint.get("knowledge_activations", {})
    reaction_records = checkpoint.get("reaction_records", {})
    reconsolidation_records = checkpoint.get("reconsolidation_records", {})
    return {
        "recent_sentence_count": len(local_buffer.get("recent_sentences", [])),
        "open_meaning_unit_sentence_count": len(local_buffer.get("open_meaning_unit_sentence_ids", [])),
        "concept_count": len(concept_registry.get("entries", [])),
        "thread_count": len(thread_trace.get("entries", [])),
        "reflective_item_count": len(reflective_frames.get("chapter_understandings", [])),
        "activation_count": len(knowledge_activations.get("activations", [])),
        "reaction_count": len(reaction_records.get("records", [])),
        "reconsolidation_count": len(reconsolidation_records.get("records", [])),
    }


def build_checkpoint_activity_event(checkpoint: FullCheckpointState) -> dict[str, object]:
    """Build the standard shared activity event for a checkpoint write."""

    checkpoint_id = _clean_text(checkpoint.get("checkpoint_id")) or "latest"
    created_at = _clean_text(checkpoint.get("created_at")) or _timestamp()
    cursor = checkpoint.get("cursor", {})
    chapter_ref = _clean_text(cursor.get("chapter_ref"))
    message = f"Checkpoint saved in {chapter_ref}." if chapter_ref else "Checkpoint saved."
    active_refs = checkpoint.get("active_artifact_refs", {})
    event: dict[str, object] = {
        "event_id": f"checkpoint:{checkpoint_id}",
        "timestamp": created_at,
        "type": "checkpoint.saved",
        "stream": "system",
        "kind": "checkpoint",
        "visibility": "collapsed",
        "message": message,
        "chapter_id": cursor.get("chapter_id"),
        "chapter_ref": chapter_ref or None,
        "reaction_types": [],
        "visible_reactions": [],
        "featured_reactions": [],
        "visible_reaction_count": len(checkpoint.get("visible_reaction_ids", [])),
        "active_reaction_id": _clean_text(active_refs.get("reaction_id")) or None,
    }
    reading_locus = reading_locus_from_cursor(cursor)
    if reading_locus is not None:
        event["reading_locus"] = reading_locus
    return event


def build_resume_activity_event(
    resume_payload: Mapping[str, object],
    *,
    active_artifact_refs: RuntimeArtifactRefs | None = None,
) -> dict[str, object]:
    """Build the standard shared activity event for resume restoration."""

    effective_resume_kind = _clean_text(resume_payload.get("effective_resume_kind")) or "warm_resume"
    compatibility_status = _clean_text(resume_payload.get("compatibility_status"))
    if compatibility_status == "fallback_to_live_state":
        message = "Resumed from live state after checkpoint compatibility fallback."
    elif effective_resume_kind == "cold_resume":
        message = "Rebuilt recent reading context from the latest checkpoint."
    elif effective_resume_kind == "reconstitution_resume":
        message = "Reconstituted recent reading context from the latest checkpoint."
    else:
        message = "Resumed from the latest checkpoint."
    checkpoint_id = _clean_text(resume_payload.get("checkpoint_id")) or "latest"
    cursor = resume_payload.get("cursor", {})
    chapter_ref = _clean_text(cursor.get("chapter_ref")) if isinstance(cursor, Mapping) else ""
    event: dict[str, object] = {
        "event_id": f"resume:{checkpoint_id}:{effective_resume_kind}",
        "timestamp": _timestamp(),
        "type": "resume.restored",
        "stream": "system",
        "kind": "transition",
        "visibility": "collapsed",
        "message": message,
        "chapter_id": cursor.get("chapter_id") if isinstance(cursor, Mapping) else None,
        "chapter_ref": chapter_ref or None,
        "reaction_types": [],
        "visible_reactions": [],
        "featured_reactions": [],
        "active_reaction_id": _clean_text((active_artifact_refs or {}).get("reaction_id")) or None,
        "reconstructed_hot_state": bool(resume_payload.get("resume_window_sentence_ids")),
        "last_resume_kind": effective_resume_kind,
    }
    reading_locus = reading_locus_from_cursor(cursor if isinstance(cursor, Mapping) else None)
    if reading_locus is not None:
        event["reading_locus"] = reading_locus
    return event


def append_standard_activity_event(
    output_dir: Path,
    event: Mapping[str, object],
    *,
    reader_policy: ReaderPolicy | Mapping[str, object] | None,
) -> None:
    """Append one standard-mode shared activity event when enabled."""

    if not standard_event_stream_enabled(reader_policy):
        return
    _append_shared_jsonl(runtime_artifacts.activity_file(output_dir), dict(event))


def append_debug_event(
    output_dir: Path,
    *,
    event_type: str,
    payload: Mapping[str, object],
    reader_policy: ReaderPolicy | Mapping[str, object] | None,
) -> None:
    """Append one debug-only diagnostics event when enabled."""

    if not debug_event_stream_enabled(reader_policy):
        return
    append_jsonl(
        event_stream_file(output_dir),
        {
            "event_id": f"debug:{_clean_text(event_type)}:{_timestamp()}",
            "timestamp": _timestamp(),
            "event_type": _clean_text(event_type),
            "observability_mode": "debug",
            "payload": dict(payload),
        },
    )


def emit_checkpoint_observability(
    output_dir: Path,
    checkpoint: FullCheckpointState,
    *,
    reader_policy: ReaderPolicy | Mapping[str, object] | None,
) -> None:
    """Emit the standard checkpoint event and optional debug diagnostics."""

    append_standard_activity_event(
        output_dir,
        build_checkpoint_activity_event(checkpoint),
        reader_policy=reader_policy,
    )
    debug_payload: dict[str, object] = {
        "checkpoint_id": _clean_text(checkpoint.get("checkpoint_id")),
        "checkpoint_reason": _clean_text(checkpoint.get("checkpoint_reason")),
        "resume_kind": _clean_text(checkpoint.get("resume_kind")),
        "cursor": dict(checkpoint.get("cursor", {})),
        "active_artifact_refs": dict(checkpoint.get("active_artifact_refs", {})),
        "visible_reaction_ids": list(checkpoint.get("visible_reaction_ids", [])),
    }
    if debug_checkpoint_diagnostics_enabled(reader_policy):
        debug_payload["state_counts"] = _checkpoint_state_counts(checkpoint)
    append_debug_event(
        output_dir,
        event_type="checkpoint.saved",
        payload=debug_payload,
        reader_policy=reader_policy,
    )


def emit_resume_observability(
    output_dir: Path,
    resume_payload: Mapping[str, object],
    *,
    reader_policy: ReaderPolicy | Mapping[str, object] | None,
    active_artifact_refs: RuntimeArtifactRefs | None = None,
) -> None:
    """Emit the standard resume event and optional debug diagnostics."""

    append_standard_activity_event(
        output_dir,
        build_resume_activity_event(resume_payload, active_artifact_refs=active_artifact_refs),
        reader_policy=reader_policy,
    )
    debug_payload: dict[str, object] = {
        "requested_resume_kind": _clean_text(resume_payload.get("requested_resume_kind")),
        "effective_resume_kind": _clean_text(resume_payload.get("effective_resume_kind")),
        "compatibility_status": _clean_text(resume_payload.get("compatibility_status")),
        "compatibility_issues": list(resume_payload.get("compatibility_issues", [])),
        "checkpoint_id": _clean_text(resume_payload.get("checkpoint_id")),
        "resume_window_sentence_ids": list(resume_payload.get("resume_window_sentence_ids", [])),
        "cursor": dict(resume_payload.get("cursor", {})) if isinstance(resume_payload.get("cursor"), Mapping) else {},
        "active_artifact_refs": dict(active_artifact_refs or {}),
    }
    append_debug_event(
        output_dir,
        event_type="resume.restored",
        payload=debug_payload,
        reader_policy=reader_policy,
    )
