"""Practical recording API for the shared runtime observation ledger."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Mapping

from .llm_pricing import (
    CostEstimate,
    PricingCatalog,
    estimate_usage_cost,
    load_default_pricing_catalog,
)
from .llm_usage import NormalizedUsage, normalize_provider_usage
from .observation_context import current_observation_context
from .observation_ledger import ObservationRecordResult, append_observation_event, deterministic_event_id


def _text(value: object | None) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None


def _timestamp(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return normalized.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return _text(value)


def _datetime_value(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return normalized.astimezone(timezone.utc)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _decimal(value: Decimal | int | str | None) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        normalized = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None
    if not normalized.is_finite() or normalized < 0:
        return None
    return normalized


def _duration(value: Decimal | int | float | str | None) -> int | str | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        normalized = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None
    if not normalized.is_finite() or normalized < 0:
        return None
    integral = normalized.to_integral_value()
    return int(integral) if normalized == integral else format(normalized, "f")


def _context_event_fields() -> tuple[str | None, dict[str, object]]:
    context = current_observation_context()
    if context is None:
        return None, {}
    return context.ledger_path, context.event_fields()


def _usage(
    value: NormalizedUsage | Mapping[str, object] | None,
    response: object | None,
    *,
    provider_family: str | None,
) -> NormalizedUsage:
    if isinstance(value, NormalizedUsage):
        return value
    if value is not None:
        return normalize_provider_usage(value, provider_family=provider_family)
    return normalize_provider_usage(response, provider_family=provider_family)


def record_llm_attempt(
    *,
    call_id: str,
    attempt_index: int,
    status: str,
    attempt_id: str | None = None,
    response: object | None = None,
    usage: NormalizedUsage | Mapping[str, object] | None = None,
    profile_id: str | None = None,
    provider_id: str | None = None,
    provider_contract: str | None = None,
    target_id: str | None = None,
    model: str | None = None,
    stage: str | None = None,
    node: str | None = None,
    started_at: datetime | str | None = None,
    completed_at: datetime | str | None = None,
    duration_ms: Decimal | int | float | str | None = None,
    problem_code: str | None = None,
    billing_model: str | None = None,
    actual_billed_cost: Decimal | int | str | None = None,
    pricing_catalog: PricingCatalog | None = None,
    otel_trace_id: str | None = None,
    otel_span_id: str | None = None,
    otel_parent_span_id: str | None = None,
    quota_wait_ms: Decimal | int | float | str | None = None,
    provider_gate_wait_ms: Decimal | int | float | str | None = None,
    profile_gate_wait_ms: Decimal | int | float | str | None = None,
) -> ObservationRecordResult:
    """Record one physical provider attempt without affecting call semantics."""

    normalized_call_id = str(call_id or "").strip()
    normalized_status = str(status or "").strip().lower()
    try:
        normalized_attempt_index = int(attempt_index)
    except (TypeError, ValueError):
        normalized_attempt_index = -1
    normalized_usage = _usage(usage, response, provider_family=provider_contract)
    catalog: PricingCatalog | None = None
    rule = None
    try:
        catalog = pricing_catalog if pricing_catalog is not None else load_default_pricing_catalog()
        if catalog is not None:
            rule = catalog.match(
                target_id=target_id,
                model=model,
                provider_id=provider_contract or provider_id,
                at=_datetime_value(started_at),
            )
        estimate = estimate_usage_cost(normalized_usage, rule)
    except Exception:
        estimate = CostEstimate("pricing_error", None, "unknown", None, None)
        rule = None
    explicit_actual = _decimal(actual_billed_cost)
    if explicit_actual is not None:
        estimate = replace(estimate, actual_billed_cost=explicit_actual)
    if normalized_billing_model := _text(billing_model):
        estimate = replace(estimate, billing_model=normalized_billing_model.lower())

    ledger_path, context_fields = _context_event_fields()
    normalized_attempt_id = _text(attempt_id) or f"{normalized_call_id}:{normalized_attempt_index}"
    event: dict[str, object] = {
        **context_fields,
        "event_id": deterministic_event_id(
            "llm_provider_attempt_finished",
            context_fields.get("job_id"),
            context_fields.get("run_attempt_id"),
            normalized_call_id,
            normalized_attempt_id,
        ),
        "event_kind": "llm_provider_attempt_finished",
        "call_id": normalized_call_id,
        "attempt_id": normalized_attempt_id,
        "attempt_index": normalized_attempt_index,
        "status": normalized_status or "unknown",
        "profile_id": _text(profile_id),
        "provider_id": _text(provider_id),
        "provider_contract": _text(provider_contract),
        "target_id": _text(target_id),
        "model": _text(model),
        "stage": _text(stage) or context_fields.get("stage"),
        "node": _text(node) or context_fields.get("node"),
        "started_at": _timestamp(started_at),
        "completed_at": _timestamp(completed_at),
        "duration_ms": _duration(duration_ms),
        "problem_code": _text(problem_code),
        "quota_wait_ms": _duration(quota_wait_ms),
        "provider_gate_wait_ms": _duration(provider_gate_wait_ms),
        "profile_gate_wait_ms": _duration(profile_gate_wait_ms),
        "usage": normalized_usage.to_dict(),
        "usage_status": normalized_usage.status,
        "usage_source": normalized_usage.source,
        "pricing": rule.snapshot(catalog_version=catalog.catalog_version) if rule is not None and catalog is not None else None,
        "cost": estimate.to_dict(),
    }
    otel = {
        "trace_id": _text(otel_trace_id),
        "span_id": _text(otel_span_id),
        "parent_span_id": _text(otel_parent_span_id),
    }
    otel = {key: value for key, value in otel.items() if value is not None}
    if otel:
        event["otel"] = otel
    event = {key: value for key, value in event.items() if value is not None}
    return append_observation_event(ledger_path, event)


def record_llm_attempt_started(
    *,
    call_id: str,
    attempt_index: int,
    attempt_id: str,
    profile_id: str | None = None,
    provider_id: str | None = None,
    provider_contract: str | None = None,
    target_id: str | None = None,
    model: str | None = None,
    stage: str | None = None,
    node: str | None = None,
    started_at: datetime | str | None = None,
    otel_trace_id: str | None = None,
    otel_span_id: str | None = None,
    otel_parent_span_id: str | None = None,
) -> ObservationRecordResult:
    """Persist dispatch evidence before an adapter request can be interrupted."""

    ledger_path, context_fields = _context_event_fields()
    normalized_call_id = str(call_id or "").strip()
    normalized_attempt_id = str(attempt_id or "").strip()
    try:
        normalized_attempt_index = int(attempt_index)
    except (TypeError, ValueError):
        normalized_attempt_index = -1
    event: dict[str, object] = {
        **context_fields,
        "event_id": deterministic_event_id(
            "llm_provider_attempt_started",
            context_fields.get("job_id"),
            context_fields.get("run_attempt_id"),
            normalized_call_id,
            normalized_attempt_id,
        ),
        "event_kind": "llm_provider_attempt_started",
        "call_id": normalized_call_id,
        "attempt_id": normalized_attempt_id,
        "attempt_index": normalized_attempt_index,
        "status": "started",
        "profile_id": _text(profile_id),
        "provider_id": _text(provider_id),
        "provider_contract": _text(provider_contract),
        "target_id": _text(target_id),
        "model": _text(model),
        "stage": _text(stage) or context_fields.get("stage"),
        "node": _text(node) or context_fields.get("node"),
        "started_at": _timestamp(started_at),
    }
    otel = {
        "trace_id": _text(otel_trace_id),
        "span_id": _text(otel_span_id),
        "parent_span_id": _text(otel_parent_span_id),
    }
    otel = {key: value for key, value in otel.items() if value is not None}
    if otel:
        event["otel"] = otel
    event = {key: value for key, value in event.items() if value is not None}
    return append_observation_event(ledger_path, event)


def record_llm_call(
    *,
    call_id: str,
    status: str,
    attempt_count: int,
    profile_id: str | None = None,
    target_id: str | None = None,
    model: str | None = None,
    stage: str | None = None,
    node: str | None = None,
    started_at: datetime | str | None = None,
    completed_at: datetime | str | None = None,
    duration_ms: Decimal | int | float | str | None = None,
    problem_code: str | None = None,
    otel_trace_id: str | None = None,
    otel_span_id: str | None = None,
    otel_parent_span_id: str | None = None,
    quota_wait_ms_total: Decimal | int | float | str | None = None,
) -> ObservationRecordResult:
    """Record one logical LLM call after all physical attempts are complete."""

    ledger_path, context_fields = _context_event_fields()
    try:
        normalized_attempt_count = max(0, int(attempt_count))
    except (TypeError, ValueError):
        normalized_attempt_count = 0
    event: dict[str, object] = {
        **context_fields,
        "event_id": deterministic_event_id(
            "llm_logical_call_finished",
            context_fields.get("job_id"),
            context_fields.get("run_attempt_id"),
            str(call_id or "").strip(),
        ),
        "event_kind": "llm_logical_call_finished",
        "call_id": str(call_id or "").strip(),
        "status": str(status or "unknown").strip().lower() or "unknown",
        "attempt_count": normalized_attempt_count,
        "profile_id": _text(profile_id),
        "target_id": _text(target_id),
        "model": _text(model),
        "stage": _text(stage) or context_fields.get("stage"),
        "node": _text(node) or context_fields.get("node"),
        "started_at": _timestamp(started_at),
        "completed_at": _timestamp(completed_at),
        "duration_ms": _duration(duration_ms),
        "problem_code": _text(problem_code),
        "quota_wait_ms_total": _duration(quota_wait_ms_total),
    }
    otel = {
        "trace_id": _text(otel_trace_id),
        "span_id": _text(otel_span_id),
        "parent_span_id": _text(otel_parent_span_id),
    }
    otel = {key: value for key, value in otel.items() if value is not None}
    if otel:
        event["otel"] = otel
    event = {key: value for key, value in event.items() if value is not None}
    return append_observation_event(ledger_path, event)


__all__ = [
    "ObservationRecordResult",
    "record_llm_attempt",
    "record_llm_attempt_started",
    "record_llm_call",
]
