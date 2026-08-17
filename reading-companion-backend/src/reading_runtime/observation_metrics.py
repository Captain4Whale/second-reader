"""Deterministic metrics aggregation and derived observability reports."""

from __future__ import annotations

import json
import math
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping

from .llm_pricing import decimal_string
from .observation_ledger import (
    ObservationLedgerReadError,
    flush_observation_ledger_diagnostics,
    load_observation_events,
    observation_ledger_diagnostics,
)


OBSERVATION_METRICS_SCHEMA_VERSION = 1
_SUCCESS_STATUSES = {"accepted", "completed", "ok", "success"}


def _decimal(value: object) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        normalized = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None
    if not normalized.is_finite() or normalized < 0:
        return None
    return normalized


def _integer(value: object) -> int | None:
    normalized = _decimal(value)
    if normalized is None or normalized != normalized.to_integral_value():
        return None
    return int(normalized)


def _nested(event: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = event.get(key)
    return value if isinstance(value, Mapping) else {}


def _sum_known(values: Iterable[object]) -> tuple[Decimal | None, int]:
    total = Decimal("0")
    known = 0
    for value in values:
        normalized = _decimal(value)
        if normalized is None:
            continue
        total += normalized
        known += 1
    return (total if known else None), known


def _ratio(numerator: int | Decimal, denominator: int | Decimal) -> str | None:
    if denominator <= 0:
        return None
    return decimal_string(Decimal(numerator) / Decimal(denominator))


def _parse_timestamp(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _percentile(values: Iterable[object], percentile: int) -> str | None:
    normalized = sorted(value for raw in values if (value := _decimal(raw)) is not None)
    if not normalized:
        return None
    rank = max(0, min(len(normalized) - 1, math.ceil((percentile / 100) * len(normalized)) - 1))
    return decimal_string(normalized[rank])


def _per_ten_thousand(value: object, source_chars: int) -> str | None:
    normalized = _decimal(value)
    if normalized is None or source_chars <= 0:
        return None
    return decimal_string(normalized * Decimal("10000") / Decimal(source_chars))


def _attempt_bucket(events: list[Mapping[str, Any]]) -> dict[str, object]:
    usage_rows = [_nested(event, "usage") for event in events]
    aggregatable_usage_rows = [
        usage for usage in usage_rows if usage.get("status") in {"complete", "partial"}
    ]
    input_total, input_known = _sum_known(
        usage.get("input_tokens") for usage in aggregatable_usage_rows
    )
    output_total, output_known = _sum_known(
        usage.get("output_tokens") for usage in aggregatable_usage_rows
    )
    total_total, total_known = _sum_known(
        usage.get("total_tokens") for usage in aggregatable_usage_rows
    )
    cache_read_total, cache_read_known = _sum_known(
        usage.get("cache_read_input_tokens") for usage in aggregatable_usage_rows
    )
    cache_write_total, cache_write_known = _sum_known(
        usage.get("cache_write_input_tokens") for usage in aggregatable_usage_rows
    )
    reasoning_total, reasoning_known = _sum_known(
        usage.get("reasoning_tokens") for usage in aggregatable_usage_rows
    )
    estimated_total, estimated_known = _sum_known(
        _nested(event, "cost").get("estimated_usage_value_usd") for event in events
    )
    actual_total, actual_known = _sum_known(_nested(event, "cost").get("actual_billed_cost") for event in events)
    duration_total, duration_known = _sum_known(event.get("duration_ms") for event in events)
    quota_wait_total, quota_wait_known = _sum_known(event.get("quota_wait_ms") for event in events)
    provider_wait_total, provider_wait_known = _sum_known(event.get("provider_gate_wait_ms") for event in events)
    profile_wait_total, profile_wait_known = _sum_known(event.get("profile_gate_wait_ms") for event in events)
    combined_wait = sum(
        (value or Decimal("0") for value in (quota_wait_total, provider_wait_total, profile_wait_total)),
        Decimal("0"),
    )
    wait_denominator = (duration_total or Decimal("0")) + combined_wait
    wait_share = combined_wait / wait_denominator if wait_denominator > 0 else None
    cost_status_counts = Counter(
        str(_nested(event, "cost").get("status") or "unavailable") for event in events
    )
    return {
        "attempt_count": len(events),
        "success_count": sum(1 for event in events if str(event.get("status") or "").lower() in _SUCCESS_STATUSES),
        "error_count": sum(1 for event in events if str(event.get("status") or "").lower() not in _SUCCESS_STATUSES),
        "input_tokens": decimal_string(input_total),
        "input_tokens_known_count": input_known,
        "output_tokens": decimal_string(output_total),
        "output_tokens_known_count": output_known,
        "total_tokens": decimal_string(total_total),
        "total_tokens_known_count": total_known,
        "cache_read_input_tokens": decimal_string(cache_read_total),
        "cache_read_known_count": cache_read_known,
        "cache_write_input_tokens": decimal_string(cache_write_total),
        "cache_write_known_count": cache_write_known,
        "reasoning_tokens": decimal_string(reasoning_total),
        "reasoning_known_count": reasoning_known,
        "usage_complete_count": sum(1 for usage in usage_rows if usage.get("status") == "complete"),
        "usage_partial_count": sum(1 for usage in usage_rows if usage.get("status") == "partial"),
        "usage_invalid_count": sum(1 for usage in usage_rows if usage.get("status") == "invalid"),
        "usage_unavailable_count": sum(1 for usage in usage_rows if usage.get("status") == "unavailable"),
        "estimated_usage_value_usd": decimal_string(estimated_total),
        "estimated_usage_value_known_count": estimated_known,
        "actual_billed_cost": decimal_string(actual_total),
        "actual_billed_cost_known_count": actual_known,
        "cost_status_counts": dict(sorted(cost_status_counts.items())),
        "attempt_duration_ms": decimal_string(duration_total),
        "attempt_duration_known_count": duration_known,
        "quota_wait_ms": decimal_string(quota_wait_total),
        "quota_wait_known_count": quota_wait_known,
        "provider_gate_wait_ms": decimal_string(provider_wait_total),
        "provider_gate_wait_known_count": provider_wait_known,
        "profile_gate_wait_ms": decimal_string(profile_wait_total),
        "profile_gate_wait_known_count": profile_wait_known,
        "combined_wait_share": decimal_string(wait_share),
    }


def _call_key(event: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(event.get("job_id") or ""),
        str(event.get("run_attempt_id") or ""),
        str(event.get("call_id") or ""),
    )


def _physical_attempt_identity(event: Mapping[str, Any]) -> str:
    """Return the strongest durable identity available for one provider attempt."""

    attempt_id = str(event.get("attempt_id") or "").strip()
    if attempt_id:
        return f"attempt_id:{attempt_id}"
    attempt_index = _integer(event.get("attempt_index"))
    if attempt_index is not None:
        return f"attempt_index:{attempt_index}"
    event_id = str(event.get("event_id") or "").strip()
    if event_id:
        return f"event_id:{event_id}"
    # Product ledger rows always receive event_id.  This conservative fallback
    # keeps malformed ad-hoc evidence distinct instead of claiming a match.
    return f"anonymous:{id(event)}"


def _attempt_accounting(
    attempts: list[Mapping[str, Any]],
    calls: list[Mapping[str, Any]],
    starts: list[Mapping[str, Any]] | None = None,
) -> dict[str, int]:
    """Reconcile durable logical-call claims with observed provider attempts."""

    start_rows = list(starts or [])
    claimed_by_call: dict[tuple[str, str, str], int] = defaultdict(int)
    started_by_call: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    finished_by_call: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for call in calls:
        key = _call_key(call)
        claimed_by_call[key] += _integer(call.get("attempt_count")) or 0
    for attempt in attempts:
        finished_by_call[_call_key(attempt)].add(_physical_attempt_identity(attempt))
    for started in start_rows:
        started_by_call[_call_key(started)].add(_physical_attempt_identity(started))
    keys = set(claimed_by_call) | set(started_by_call) | set(finished_by_call)
    physical_evidence = {
        key: started_by_call.get(key, set()) | finished_by_call.get(key, set())
        for key in keys
    }
    expected_by_call = {
        key: max(claimed_by_call.get(key, 0), len(physical_evidence.get(key, set())))
        for key in keys
    }
    expected = sum(expected_by_call.values())
    observed = sum(len(values) for values in finished_by_call.values())
    accounted = expected
    missing = sum(
        max(0, expected_by_call.get(key, 0) - len(finished_by_call.get(key, set())))
        for key in keys
    )
    unexpected = sum(
        max(
            0,
            len(finished_by_call.get(key, set()))
            - max(claimed_by_call.get(key, 0), len(started_by_call.get(key, set()))),
        )
        for key in keys
    )
    matched = sum(
        min(expected_by_call.get(key, 0), len(finished_by_call.get(key, set())))
        for key in keys
    )
    started_ids = {
        (*key, attempt_id) for key, values in started_by_call.items() for attempt_id in values
    }
    finished_ids = {
        (*key, attempt_id) for key, values in finished_by_call.items() for attempt_id in values
    }
    return {
        "started_physical_attempt_count": len(started_ids),
        "expected_physical_attempt_count": expected,
        "observed_physical_attempt_count": observed,
        "accounted_physical_attempt_count": accounted,
        "matched_physical_attempt_count": matched,
        "missing_physical_attempt_count": missing,
        "unexpected_physical_attempt_count": unexpected,
        "started_without_finish_count": len(started_ids - finished_ids),
        "finished_without_start_count": len(finished_ids - started_ids),
    }


def _unit_correlation_key(event: Mapping[str, Any]) -> tuple[str, str, str, str] | None:
    cycle_id = str(event.get("reading_cycle_id") or "").strip()
    if not cycle_id:
        return None
    return (
        str(event.get("job_id") or ""),
        str(event.get("run_attempt_id") or ""),
        str(event.get("chapter_id") or ""),
        cycle_id,
    )


def _backfill_selected_unit_correlations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Join pre-selection Ingest calls to the selected unit without timestamp inference."""

    selected_by_cycle: dict[tuple[str, str, str, str], dict[str, object]] = {}
    ambiguous_cycles: set[tuple[str, str, str, str]] = set()
    for event in rows:
        if event.get("event_kind") != "unit_selected":
            continue
        key = _unit_correlation_key(event)
        unit_id = str(event.get("unit_id") or "").strip()
        if key is None or not unit_id:
            continue
        selected = {
            "unit_id": unit_id,
            "unit_index": event.get("unit_index"),
            "source_char_count": event.get("source_char_count"),
        }
        previous = selected_by_cycle.get(key)
        if previous is not None and previous != selected:
            ambiguous_cycles.add(key)
            selected_by_cycle.pop(key, None)
        elif key not in ambiguous_cycles:
            selected_by_cycle[key] = selected

    resolved: list[dict[str, Any]] = []
    for event in rows:
        copied = dict(event)
        key = _unit_correlation_key(copied)
        if copied.get("unit_id") is None and key is not None and key in selected_by_cycle:
            for field, value in selected_by_cycle[key].items():
                if value is not None:
                    copied[field] = value
            copied["unit_correlation_source"] = "unit_selected_event"
        resolved.append(copied)
    return resolved


def _dimension_bucket(
    attempts: list[Mapping[str, Any]],
    calls: list[Mapping[str, Any]],
    cycles: list[Mapping[str, Any]] | None = None,
    starts: list[Mapping[str, Any]] | None = None,
    include_logical_attempt_claims: bool = True,
) -> dict[str, object]:
    """Aggregate one model/target/stage/chapter/unit slice with consistent semantics."""

    cycle_rows = list(cycles or [])
    accepted_cycles = [
        event for event in cycle_rows if str(event.get("status") or "").lower() in _SUCCESS_STATUSES
    ]
    source_chars = sum(_integer(event.get("source_char_count")) or 0 for event in accepted_cycles)
    bucket = _attempt_bucket(attempts)
    accounting = _attempt_accounting(
        attempts,
        calls if include_logical_attempt_claims else [],
        starts,
    )
    physical_call_keys = {
        _call_key(event) for event in [*attempts, *(starts or [])]
    }
    retry_count = (
        sum(max(0, (_integer(event.get("attempt_count")) or 0) - 1) for event in calls)
        if include_logical_attempt_claims
        else max(
            0,
            accounting["expected_physical_attempt_count"] - len(physical_call_keys),
        )
    )
    bucket.update(
        {
            **accounting,
            "logical_call_count": len(calls),
            "logical_call_success_count": sum(
                1 for event in calls if str(event.get("status") or "").lower() in _SUCCESS_STATUSES
            ),
            "logical_call_error_count": sum(
                1 for event in calls if str(event.get("status") or "").lower() not in _SUCCESS_STATUSES
            ),
            "physical_attempts_per_logical_call": _ratio(len(attempts), len(calls)),
            "expected_attempts_per_logical_call": _ratio(
                accounting["expected_physical_attempt_count"], len(calls)
            ),
            "retry_count": retry_count,
            "accepted_unit_count": len(accepted_cycles),
            "accepted_source_chars": source_chars,
            "unit_duration_ms_p50": _percentile(
                (event.get("duration_ms") for event in accepted_cycles), 50
            ),
            "unit_duration_ms_p95": _percentile(
                (event.get("duration_ms") for event in accepted_cycles), 95
            ),
            "input_tokens_per_10000_chars": _per_ten_thousand(
                bucket.get("input_tokens"), source_chars
            ),
            "output_tokens_per_10000_chars": _per_ten_thousand(
                bucket.get("output_tokens"), source_chars
            ),
            "total_tokens_per_10000_chars": _per_ten_thousand(
                bucket.get("total_tokens"), source_chars
            ),
            "estimated_usage_value_usd_per_10000_chars": _per_ten_thousand(
                bucket.get("estimated_usage_value_usd"), source_chars
            ),
        }
    )
    return bucket


def _active_interval_summary(
    run_starts: list[Mapping[str, Any]],
    run_finishes: list[Mapping[str, Any]],
) -> tuple[Decimal | None, int, list[datetime]]:
    """Return the union of finished lease/run intervals and all elapsed-time endpoints."""

    starts_by_attempt = {
        str(event.get("run_attempt_id") or ""): event
        for event in run_starts
        if str(event.get("run_attempt_id") or "")
    }
    intervals: list[tuple[datetime, datetime]] = []
    elapsed_points: list[datetime] = []
    for event in run_starts:
        started = _parse_timestamp(event.get("active_interval_started_at")) or _parse_timestamp(
            event.get("observed_at")
        )
        if started is not None:
            elapsed_points.append(started)
    for event in run_finishes:
        finished = _parse_timestamp(event.get("observed_at"))
        start_event = starts_by_attempt.get(str(event.get("run_attempt_id") or ""), {})
        started = _parse_timestamp(event.get("active_interval_started_at")) or _parse_timestamp(
            start_event.get("active_interval_started_at")
        ) or _parse_timestamp(start_event.get("observed_at"))
        if finished is not None:
            elapsed_points.append(finished)
        if started is not None and finished is not None and finished >= started:
            intervals.append((started, finished))
    if not intervals:
        return None, 0, elapsed_points
    intervals.sort(key=lambda item: item[0])
    merged: list[tuple[datetime, datetime]] = []
    for started, finished in intervals:
        if not merged or started > merged[-1][1]:
            merged.append((started, finished))
            continue
        previous_start, previous_finish = merged[-1]
        merged[-1] = (previous_start, max(previous_finish, finished))
    total = sum(
        (Decimal(str((finished - started).total_seconds())) for started, finished in merged),
        Decimal("0"),
    )
    return total, len(intervals), elapsed_points


def aggregate_observation_metrics(
    events: Iterable[Mapping[str, Any]],
    *,
    malformed_line_count: int = 0,
) -> dict[str, object]:
    """Aggregate immutable facts without treating missing usage/cost as zero."""

    supplied_rows = [dict(event) for event in events]
    rows: list[dict[str, Any]] = []
    seen_event_ids: set[str] = set()
    duplicate_event_count = 0
    for event in supplied_rows:
        event_id = str(event.get("event_id") or "").strip()
        if event_id and event_id in seen_event_ids:
            duplicate_event_count += 1
            continue
        if event_id:
            seen_event_ids.add(event_id)
        rows.append(event)
    rows = _backfill_selected_unit_correlations(rows)
    attempts = [
        event
        for event in rows
        if event.get("event_kind") == "llm_provider_attempt_finished"
    ]
    attempt_starts = [
        event
        for event in rows
        if event.get("event_kind") == "llm_provider_attempt_started"
    ]
    calls = [
        event
        for event in rows
        if event.get("event_kind") == "llm_logical_call_finished"
    ]
    cycle_events = [event for event in rows if event.get("event_kind") == "unit_settled"]
    accepted_cycles = [
        event for event in cycle_events if str(event.get("status") or "").lower() in _SUCCESS_STATUSES
    ]
    run_starts = [event for event in rows if event.get("event_kind") == "run_attempt_started"]
    run_finishes = [event for event in rows if event.get("event_kind") == "run_attempt_finished"]
    aggregate = _attempt_bucket(attempts)
    call_quota_wait_total, call_quota_wait_known = _sum_known(event.get("quota_wait_ms_total") for event in calls)
    accepted_source_chars = sum(_integer(event.get("source_char_count")) or 0 for event in accepted_cycles)
    active_seconds, active_known_count, observed_times = _active_interval_summary(
        run_starts,
        run_finishes,
    )
    provider_ms = _decimal(aggregate.get("attempt_duration_ms"))
    elapsed_seconds = (
        Decimal(str((max(observed_times) - min(observed_times)).total_seconds()))
        if len(observed_times) >= 2
        else None
    )
    provider_seconds = provider_ms / Decimal("1000") if provider_ms is not None else None
    chars_per_active_minute = (
        Decimal(accepted_source_chars) * Decimal("60") / active_seconds
        if active_seconds is not None and active_seconds > 0
        else None
    )
    active_minutes_per_ten_thousand_chars = (
        active_seconds / Decimal("60") * Decimal("10000") / Decimal(accepted_source_chars)
        if active_seconds is not None and accepted_source_chars > 0
        else None
    )
    attempt_count = len(attempts)
    accounting = _attempt_accounting(attempts, calls, attempt_starts)
    accounted_attempt_count = accounting["accounted_physical_attempt_count"]
    calls_by_key = {_call_key(event): event for event in calls}
    expected_by_key = {
        _call_key(event): _integer(event.get("attempt_count")) or 0 for event in calls
    }
    observed_by_key: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for event in attempts:
        observed_by_key[_call_key(event)].append(event)
    started_by_key: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for event in attempt_starts:
        started_by_key[_call_key(event)].append(event)
    correlation_rows_by_key: dict[
        tuple[str, str, str], list[Mapping[str, Any]]
    ] = defaultdict(list)
    canonical_finished_rows: list[Mapping[str, Any]] = []
    for key in set(observed_by_key) | set(started_by_key):
        finished_by_identity = {
            _physical_attempt_identity(event): event
            for event in observed_by_key.get(key, [])
        }
        started_by_identity = {
            _physical_attempt_identity(event): event
            for event in started_by_key.get(key, [])
        }
        canonical_finished_rows.extend(finished_by_identity.values())
        correlation_rows_by_key[key].extend(finished_by_identity.values())
        correlation_rows_by_key[key].extend(
            event
            for attempt_id, event in started_by_identity.items()
            if attempt_id not in finished_by_identity
        )
    usage_complete_count = sum(
        1
        for event in canonical_finished_rows
        if _nested(event, "usage").get("status") == "complete"
    )
    estimated_known_count = sum(
        1
        for event in canonical_finished_rows
        if _decimal(_nested(event, "cost").get("estimated_usage_value_usd")) is not None
    )
    accounting_keys = set(expected_by_key) | set(observed_by_key) | set(started_by_key)
    unit_scoped_keys = {
        key
        for key in accounting_keys
        if bool(calls_by_key.get(key, {}).get("unit_id"))
        or any(
            bool(event.get("unit_id"))
            for event in correlation_rows_by_key.get(key, [])
        )
    }
    unit_scope_eligible_attempt_count = sum(
        max(
            expected_by_key.get(key, 0),
            len(correlation_rows_by_key.get(key, [])),
        )
        for key in unit_scoped_keys
    )
    chapter_correlated_attempt_count = sum(
        1
        for events_for_call in correlation_rows_by_key.values()
        for event in events_for_call
        if event.get("chapter_id") is not None
    )
    unit_correlated_attempt_count = sum(
        1
        for key in unit_scoped_keys
        for event in correlation_rows_by_key.get(key, [])
        if event.get("unit_id") is not None
    )
    chapter_unit_correlated_attempt_count = sum(
        1
        for key in unit_scoped_keys
        for event in correlation_rows_by_key.get(key, [])
        if event.get("chapter_id") is not None and event.get("unit_id") is not None
    )
    stage_appropriate_correlated_attempt_count = sum(
        1
        for key in accounting_keys
        for event in correlation_rows_by_key.get(key, [])
        if event.get("chapter_id") is not None
        and (key not in unit_scoped_keys or event.get("unit_id") is not None)
    )
    pricing_snapshots: dict[str, Mapping[str, Any]] = {}
    for event in attempts:
        pricing = _nested(event, "pricing")
        snapshot_hash = str(pricing.get("snapshot_hash") or "").strip()
        if snapshot_hash:
            pricing_snapshots[snapshot_hash] = pricing

    attempts_by_call: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    calls_by_id = {str(event.get("call_id") or ""): event for event in calls}
    for event in attempts:
        attempts_by_call[str(event.get("call_id") or "")].append(event)
    retry_waste_attempts: list[Mapping[str, Any]] = []
    for call_id, call_attempts in attempts_by_call.items():
        ordered = sorted(call_attempts, key=lambda event: _integer(event.get("attempt_index")) or 0)
        call_status = str(calls_by_id.get(call_id, {}).get("status") or "").lower()
        retry_waste_attempts.extend(ordered[:-1] if call_status in _SUCCESS_STATUSES else ordered)
    retry_waste = _attempt_bucket(retry_waste_attempts)

    aggregate.update(
        {
            **accounting,
            "schema_version": OBSERVATION_METRICS_SCHEMA_VERSION,
            "event_count": len(rows),
            "malformed_line_count": max(0, int(malformed_line_count)),
            "duplicate_event_count": duplicate_event_count,
            "call_count": len(calls),
            "call_success_count": sum(1 for event in calls if str(event.get("status") or "").lower() in _SUCCESS_STATUSES),
            "call_error_count": sum(1 for event in calls if str(event.get("status") or "").lower() not in _SUCCESS_STATUSES),
            "retry_count": sum(max(0, (_integer(event.get("attempt_count")) or 0) - 1) for event in calls),
            "retry_amplification": _ratio(
                accounting["expected_physical_attempt_count"], len(calls)
            ),
            "physical_attempts_per_logical_call": _ratio(attempt_count, len(calls)),
            "logical_calls_per_accepted_unit": _ratio(len(calls), len(accepted_cycles)),
            "retry_waste": retry_waste,
            "call_quota_wait_ms": decimal_string(call_quota_wait_total),
            "call_quota_wait_known_count": call_quota_wait_known,
            "unit_attempt_count": len(cycle_events),
            "accepted_unit_count": len(accepted_cycles),
            "accepted_source_chars": accepted_source_chars,
            "source_char_count": accepted_source_chars,
            "elapsed_seconds": decimal_string(elapsed_seconds),
            "active_seconds": decimal_string(active_seconds),
            "active_interval_known_count": active_known_count,
            "provider_seconds": decimal_string(provider_seconds),
            "chars_per_active_minute": decimal_string(chars_per_active_minute),
            "active_minutes_per_10000_chars": decimal_string(active_minutes_per_ten_thousand_chars),
            "input_tokens_per_10000_chars": _per_ten_thousand(
                aggregate.get("input_tokens"), accepted_source_chars
            ),
            "output_tokens_per_10000_chars": _per_ten_thousand(
                aggregate.get("output_tokens"), accepted_source_chars
            ),
            "total_tokens_per_10000_chars": _per_ten_thousand(
                aggregate.get("total_tokens"), accepted_source_chars
            ),
            "estimated_usage_value_usd_per_10000_chars": _per_ten_thousand(
                aggregate.get("estimated_usage_value_usd"), accepted_source_chars
            ),
            "known_estimated_usage_value_usd": aggregate.get("estimated_usage_value_usd"),
            "call_duration_ms_p50": _percentile((event.get("duration_ms") for event in calls), 50),
            "call_duration_ms_p95": _percentile((event.get("duration_ms") for event in calls), 95),
            "unit_duration_ms_p50": _percentile((event.get("duration_ms") for event in accepted_cycles), 50),
            "unit_duration_ms_p95": _percentile((event.get("duration_ms") for event in accepted_cycles), 95),
            "status_counts": dict(sorted(Counter(str(event.get("status") or "unknown") for event in rows).items())),
            "billing_model_counts": dict(
                sorted(Counter(str(_nested(event, "cost").get("billing_model") or "unknown") for event in attempts).items())
            ),
            "pricing_snapshots": [dict(value) for _, value in sorted(pricing_snapshots.items())],
            "data_quality": {
                "usage_coverage": _ratio(usage_complete_count, accounted_attempt_count),
                "pricing_coverage": _ratio(estimated_known_count, accounted_attempt_count),
                "physical_attempt_accounting_coverage": _ratio(
                    accounting["matched_physical_attempt_count"],
                    accounting["expected_physical_attempt_count"],
                ),
                "provider_attempt_finish_coverage": _ratio(
                    accounting["started_physical_attempt_count"]
                    - accounting["started_without_finish_count"],
                    accounting["started_physical_attempt_count"],
                ),
                "stage_appropriate_correlation_coverage": _ratio(
                    stage_appropriate_correlated_attempt_count,
                    accounted_attempt_count,
                ),
                "chapter_unit_correlation_coverage": _ratio(
                    chapter_unit_correlated_attempt_count,
                    unit_scope_eligible_attempt_count,
                ),
                "chapter_correlation_coverage": _ratio(
                    chapter_correlated_attempt_count,
                    accounted_attempt_count,
                ),
                "unit_correlation_coverage": _ratio(
                    unit_correlated_attempt_count,
                    unit_scope_eligible_attempt_count,
                ),
                "chapter_scope_eligible_attempt_count": accounted_attempt_count,
                "unit_scope_eligible_attempt_count": unit_scope_eligible_attempt_count,
                "chapter_only_attempt_count": (
                    accounted_attempt_count - unit_scope_eligible_attempt_count
                ),
                "non_unit_eligible_attempt_count": (
                    accounted_attempt_count - unit_scope_eligible_attempt_count
                ),
                "unknown_usage_count": accounted_attempt_count - usage_complete_count,
                "usage_unknown_attempt_count": accounted_attempt_count
                - usage_complete_count,
                "unknown_pricing_count": accounted_attempt_count - estimated_known_count,
                "usage_value_unknown_attempt_count": accounted_attempt_count
                - estimated_known_count,
                "uncorrelated_attempt_count": (
                    accounted_attempt_count - stage_appropriate_correlated_attempt_count
                ),
                "uncorrelated_chapter_attempt_count": (
                    accounted_attempt_count - chapter_correlated_attempt_count
                ),
                "uncorrelated_unit_attempt_count": (
                    unit_scope_eligible_attempt_count
                    - chapter_unit_correlated_attempt_count
                ),
                "missing_physical_attempt_count": accounting[
                    "missing_physical_attempt_count"
                ],
                "unexpected_physical_attempt_count": accounting[
                    "unexpected_physical_attempt_count"
                ],
                "started_without_finish_count": accounting[
                    "started_without_finish_count"
                ],
                "finished_without_start_count": accounting[
                    "finished_without_start_count"
                ],
                "malformed_ledger_line_count": max(0, int(malformed_line_count)),
                "duplicate_event_count": duplicate_event_count,
                "ledger_write_failure_count": sum(
                    _integer(event.get("failure_count")) or 1
                    for event in rows
                    if event.get("event_kind") == "ledger_write_failed"
                ),
                "report_generation_failure_count": sum(
                    1
                    for event in rows
                    if event.get("event_kind") == "observation_report_failed"
                ),
                "telemetry_export_failure_count": sum(
                    _integer(event.get("detected_failure_count")) or 1
                    for event in rows
                    if event.get("event_kind") == "telemetry_export_failed"
                ),
                "telemetry_failed_export_span_count": sum(
                    _integer(event.get("failed_export_span_count")) or 0
                    for event in rows
                    if event.get("event_kind") == "telemetry_export_failed"
                ),
            },
            "metric_definitions": {
                "accepted_source_chars": "Normalized source characters from successfully settled units, deduplicated by event_id.",
                "elapsed_seconds": "Wall time from the earliest run-attempt start event to the latest finish event.",
                "active_seconds": "Union of completed run-attempt intervals; managed intervals begin at lease acquisition and direct runs begin at observation start.",
                "estimated_usage_value_usd": "Known token usage valued with the immutable matched pricing snapshots; not an invoice.",
            },
        }
    )
    def _unit_key(event: Mapping[str, Any]) -> str:
        chapter_id = str(event.get("chapter_id") or "unavailable")
        unit_id = str(event.get("unit_id") or "unavailable")
        return f"{chapter_id}/{unit_id}"

    def _group(
        source: list[Mapping[str, Any]],
        key_name: str,
        *,
        unit_key: bool = False,
    ) -> dict[str, list[Mapping[str, Any]]]:
        grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for event in source:
            key = _unit_key(event) if unit_key else str(event.get(key_name) or "unavailable")
            grouped[key].append(event)
        return grouped

    def _build_breakdown(
        attempt_groups: Mapping[str, list[Mapping[str, Any]]],
        call_groups: Mapping[str, list[Mapping[str, Any]]],
        cycle_groups: Mapping[str, list[Mapping[str, Any]]] | None = None,
        start_groups: Mapping[str, list[Mapping[str, Any]]] | None = None,
        include_logical_attempt_claims: bool = True,
    ) -> dict[str, object]:
        cycle_groups = cycle_groups or {}
        start_groups = start_groups or {}
        keys = sorted(
            set(attempt_groups) | set(call_groups) | set(cycle_groups) | set(start_groups)
        )
        return {
            key: _dimension_bucket(
                list(attempt_groups.get(key, [])),
                list(call_groups.get(key, [])),
                list(cycle_groups.get(key, [])),
                list(start_groups.get(key, [])),
                include_logical_attempt_claims=include_logical_attempt_claims,
            )
            for key in keys
        }

    aggregate["by_model"] = _build_breakdown(
        _group(attempts, "model"),
        _group(calls, "model"),
        start_groups=_group(attempt_starts, "model"),
        include_logical_attempt_claims=False,
    )
    aggregate["by_target"] = _build_breakdown(
        _group(attempts, "target_id"),
        _group(calls, "target_id"),
        start_groups=_group(attempt_starts, "target_id"),
        include_logical_attempt_claims=False,
    )
    aggregate["by_stage"] = _build_breakdown(
        _group(attempts, "stage"),
        _group(calls, "stage"),
        _group(cycle_events, "stage"),
        _group(attempt_starts, "stage"),
    )
    aggregate["by_node"] = _build_breakdown(
        _group(attempts, "node"),
        _group(calls, "node"),
        start_groups=_group(attempt_starts, "node"),
    )
    aggregate["by_chapter"] = _build_breakdown(
        _group(attempts, "chapter_id"),
        _group(calls, "chapter_id"),
        _group(cycle_events, "chapter_id"),
        _group(attempt_starts, "chapter_id"),
    )
    aggregate["by_unit"] = _build_breakdown(
        _group(attempts, "unit_id", unit_key=True),
        _group(calls, "unit_id", unit_key=True),
        _group(cycle_events, "unit_id", unit_key=True),
        _group(attempt_starts, "unit_id", unit_key=True),
    )
    return aggregate


def _markdown_value(value: object) -> str:
    text = str(value if value is not None else "unknown").replace("|", "\\|").replace("\n", " ")
    return text or "unknown"


def _render_breakdown_table(
    title: str,
    dimension_label: str,
    payload: object,
    *,
    include_chars: bool = False,
) -> list[str]:
    rows = payload if isinstance(payload, Mapping) else {}
    lines = [f"## {title}", ""]
    if not rows:
        return [*lines, "No observed rows.", ""]
    headers = [
        dimension_label,
        "logical calls",
        "physical attempts",
        "attempts / call",
        "input tokens",
        "output tokens",
        "known est. USD",
    ]
    if include_chars:
        headers.extend(["accepted units", "accepted chars"])
    lines.extend(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
    )
    for key, raw_bucket in sorted(rows.items(), key=lambda item: str(item[0])):
        bucket = raw_bucket if isinstance(raw_bucket, Mapping) else {}
        values = [
            key,
            bucket.get("logical_call_count", 0),
            bucket.get("attempt_count", 0),
            bucket.get("physical_attempts_per_logical_call"),
            bucket.get("input_tokens"),
            bucket.get("output_tokens"),
            bucket.get("estimated_usage_value_usd"),
        ]
        if include_chars:
            values.extend(
                [
                    bucket.get("accepted_unit_count", 0),
                    bucket.get("accepted_source_chars", 0),
                ]
            )
        lines.append("| " + " | ".join(_markdown_value(value) for value in values) + " |")
    lines.append("")
    return lines


def render_observation_markdown(summary: Mapping[str, object]) -> str:
    """Render a compact, deterministic operator report."""

    data_quality = _nested(summary, "data_quality")
    if int(data_quality.get("ledger_read_error_count", 0) or 0) > 0:
        error_type = str(data_quality.get("ledger_read_error_type") or "unknown")
        return "\n".join(
            [
                "# Runtime Observability Report",
                "",
                "## Data unavailable",
                "",
                f"> The canonical observation ledger could not be read ({error_type}).",
                "> Event-derived metrics and breakdowns are unavailable; no zero below should be interpreted as an observed result.",
                "",
                "Inspect `data_quality.json`, restore ledger access, and rebuild this report.",
                "",
            ]
        )

    lines = [
        "# Runtime Observability Report",
        "",
        "## Primary efficiency indicators",
        "",
        f"- Accepted source characters: {summary.get('accepted_source_chars', 0)}",
        f"- Elapsed / active / provider seconds: {summary.get('elapsed_seconds') or 'unknown'} / {summary.get('active_seconds') or 'unknown'} / {summary.get('provider_seconds') or 'unknown'}",
        f"- Characters per active minute: {summary.get('chars_per_active_minute') or 'unknown'}",
        f"- Active minutes per 10,000 characters: {summary.get('active_minutes_per_10000_chars') or 'unknown'}",
        f"- Total tokens per 10,000 characters: {summary.get('total_tokens_per_10000_chars') or 'unknown'}",
        f"- Estimated usage value per 10,000 characters (USD): {summary.get('estimated_usage_value_usd_per_10000_chars') or 'unknown'}",
        "",
        "## Coverage",
        "",
        f"- Events: {summary.get('event_count', 0)}",
        f"- Malformed ledger lines: {summary.get('malformed_line_count', 0)}",
        f"- Logical LLM calls: {summary.get('call_count', 0)}",
        f"- Physical LLM attempts observed / expected / missing: {summary.get('observed_physical_attempt_count', summary.get('attempt_count', 0))} / {summary.get('expected_physical_attempt_count', 0)} / {summary.get('missing_physical_attempt_count', 0)}",
        f"- Provider attempts started / finished / started-without-finish: {summary.get('started_physical_attempt_count', 0)} / {summary.get('observed_physical_attempt_count', 0)} / {data_quality.get('started_without_finish_count', 0)}",
        f"- Usage complete / partial / invalid / unavailable: {summary.get('usage_complete_count', 0)} / {summary.get('usage_partial_count', 0)} / {summary.get('usage_invalid_count', 0)} / {summary.get('usage_unavailable_count', 0)}",
        f"- Usage / pricing / stage-appropriate correlation coverage: {data_quality.get('usage_coverage') or 'unknown'} / {data_quality.get('pricing_coverage') or 'unknown'} / {data_quality.get('stage_appropriate_correlation_coverage') or 'unknown'}",
        f"- Chapter / unit-scoped correlation coverage: {data_quality.get('chapter_correlation_coverage') or 'unknown'} / {data_quality.get('unit_correlation_coverage') or 'not-applicable'}",
        f"- Provider attempt finish coverage: {data_quality.get('provider_attempt_finish_coverage') or 'not-applicable'}",
        "",
        "## Usage and cost",
        "",
        f"- Input tokens: {summary.get('input_tokens', 0)}",
        f"- Output tokens: {summary.get('output_tokens', 0)}",
        f"- Total tokens: {summary.get('total_tokens', 0)}",
        f"- Estimated usage value (USD): {summary.get('estimated_usage_value_usd') if summary.get('estimated_usage_value_usd') is not None else 'unknown'}",
        f"- Actual billed cost: {summary.get('actual_billed_cost') if summary.get('actual_billed_cost') is not None else 'unknown'}",
        f"- Combined quota/gate wait share: {summary.get('combined_wait_share') if summary.get('combined_wait_share') is not None else 'unknown'}",
        f"- Retry amplification: {summary.get('retry_amplification') or 'unknown'}",
        f"- Logical calls per accepted unit: {summary.get('logical_calls_per_accepted_unit') or 'unknown'}",
        f"- LLM call p50 / p95 ms: {summary.get('call_duration_ms_p50') or 'unknown'} / {summary.get('call_duration_ms_p95') or 'unknown'}",
        f"- Unit p50 / p95 ms: {summary.get('unit_duration_ms_p50') or 'unknown'} / {summary.get('unit_duration_ms_p95') or 'unknown'}",
        "",
        "The estimated usage value is the known covered portion only, not an invoice or a complete-book total when pricing coverage is below 1.",
        "Missing usage or cost remains unknown and is never coerced to zero.",
        "",
    ]
    lines.extend(_render_breakdown_table("By chapter", "chapter", summary.get("by_chapter"), include_chars=True))
    lines.extend(_render_breakdown_table("By unit", "chapter / unit", summary.get("by_unit"), include_chars=True))
    lines.extend(_render_breakdown_table("By stage", "stage", summary.get("by_stage")))
    lines.extend(_render_breakdown_table("By node", "node", summary.get("by_node")))
    lines.extend(_render_breakdown_table("By model", "model", summary.get("by_model")))
    lines.extend(_render_breakdown_table("By target", "target", summary.get("by_target")))
    return "\n".join(lines)


@dataclass(frozen=True)
class ObservationReportResult:
    summary: dict[str, object]
    json_path: Path
    markdown_path: Path
    data_quality_path: Path
    json_written: bool
    markdown_written: bool
    data_quality_written: bool
    errors: tuple[str, ...]


def _atomic_write_text(path: Path, content: str) -> None:
    """Replace one derived report atomically so readers never see partial JSON/Markdown."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_observation_reports(
    ledger_path: Path | str,
    *,
    json_path: Path | str | None = None,
    markdown_path: Path | str | None = None,
    data_quality_path: Path | str | None = None,
) -> ObservationReportResult:
    """Write derived JSON/Markdown reports; failures are returned, not raised."""

    ledger = Path(ledger_path)
    resolved_json = Path(json_path) if json_path is not None else ledger.parent / "metrics.json"
    resolved_markdown = Path(markdown_path) if markdown_path is not None else ledger.parent / "report.md"
    resolved_data_quality = (
        Path(data_quality_path) if data_quality_path is not None else ledger.parent / "data_quality.json"
    )
    errors: list[str] = []
    flush_observation_ledger_diagnostics(ledger)
    ledger_read_error_type: str | None = None
    try:
        events, malformed = load_observation_events(ledger)
    except ObservationLedgerReadError as exc:
        events, malformed = [], 0
        ledger_read_error_type = type(exc.__cause__ or exc).__name__
        errors.append(f"ledger_read:{ledger_read_error_type}")
    summary = aggregate_observation_metrics(events, malformed_line_count=malformed)
    ledger_diagnostics = observation_ledger_diagnostics(ledger)
    data_quality = dict(summary.get("data_quality", {}))
    data_quality["ledger_write_failure_count"] = max(
        int(data_quality.get("ledger_write_failure_count", 0) or 0),
        int(ledger_diagnostics.get("write_failure_count", 0) or 0),
    )
    data_quality["ledger_read_error_count"] = 1 if ledger_read_error_type else 0
    data_quality["ledger_read_error_type"] = ledger_read_error_type
    summary["data_quality"] = data_quality
    json_written = False
    markdown_written = False
    data_quality_written = False

    try:
        _atomic_write_text(resolved_markdown, render_observation_markdown(summary))
        markdown_written = True
    except Exception as exc:
        errors.append(f"markdown:{type(exc).__name__}: {exc}")

    report_write_errors = [
        error.split(":", 1)[0]
        for error in errors
        if error.startswith(("markdown:", "metrics:", "data_quality:"))
    ]
    data_quality["report_write_failure_count"] = len(report_write_errors)
    data_quality["report_write_failure_components"] = report_write_errors
    summary["data_quality"] = data_quality
    try:
        _atomic_write_text(
            resolved_json,
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        json_written = True
    except Exception as exc:
        errors.append(f"metrics:{type(exc).__name__}: {exc}")

    report_write_errors = [
        error.split(":", 1)[0]
        for error in errors
        if error.startswith(("markdown:", "metrics:", "data_quality:"))
    ]
    data_quality["report_write_failure_count"] = len(report_write_errors)
    data_quality["report_write_failure_components"] = report_write_errors
    summary["data_quality"] = data_quality
    try:
        _atomic_write_text(
            resolved_data_quality,
            json.dumps(summary.get("data_quality", {}), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        data_quality_written = True
    except Exception as exc:
        errors.append(f"data_quality:{type(exc).__name__}: {exc}")

    report_write_errors = [
        error.split(":", 1)[0]
        for error in errors
        if error.startswith(("markdown:", "metrics:", "data_quality:"))
    ]
    data_quality["report_write_failure_count"] = len(report_write_errors)
    data_quality["report_write_failure_components"] = report_write_errors
    summary["data_quality"] = data_quality
    return ObservationReportResult(
        summary=summary,
        json_path=resolved_json,
        markdown_path=resolved_markdown,
        data_quality_path=resolved_data_quality,
        json_written=json_written,
        markdown_written=markdown_written,
        data_quality_written=data_quality_written,
        errors=tuple(errors),
    )


__all__ = [
    "OBSERVATION_METRICS_SCHEMA_VERSION",
    "ObservationReportResult",
    "aggregate_observation_metrics",
    "render_observation_markdown",
    "write_observation_reports",
]
