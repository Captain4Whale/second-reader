"""Copy-safe observation context and nested runtime scopes."""

from __future__ import annotations

import contextvars
import time
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from types import TracebackType
from typing import Any

from .job_lease import current_lease
from .llm_telemetry import (
    TelemetrySpan,
    flush_telemetry,
    telemetry_span,
    telemetry_status,
)
from .observation_ledger import (
    ObservationRecordResult,
    append_observation_event,
    deterministic_event_id,
    observation_ledger_file,
)


OBSERVATION_CONTEXT_SCHEMA_VERSION = 1
_CURRENT_OBSERVATION_CONTEXT: contextvars.ContextVar[ObservationContext | None]


@dataclass(frozen=True)
class ObservationContext:
    """Immutable correlation state copied safely across async contexts."""

    schema_version: int = OBSERVATION_CONTEXT_SCHEMA_VERSION
    ledger_path: str | None = None
    job_id: str | None = None
    job_kind: str | None = None
    run_id: str | None = None
    run_attempt_id: str | None = None
    lease_generation: int | None = None
    active_interval_started_at: str | None = None
    book_id: str | None = None
    mechanism_key: str | None = None
    stage: str | None = None
    node: str | None = None
    chapter_id: str | None = None
    chapter_index: int | None = None
    reading_cycle_id: str | None = None
    unit_id: str | None = None
    unit_index: int | None = None
    source_char_count: int | None = None
    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    settlement_status: str | None = None

    def event_fields(self) -> dict[str, object]:
        fields = {
            "job_id": self.job_id,
            "job_kind": self.job_kind,
            "run_id": self.run_id,
            "run_attempt_id": self.run_attempt_id,
            "lease_generation": self.lease_generation,
            "active_interval_started_at": self.active_interval_started_at,
            "book_id": self.book_id,
            "mechanism_key": self.mechanism_key,
            "stage": self.stage,
            "node": self.node,
            "chapter_id": self.chapter_id,
            "chapter_index": self.chapter_index,
            "reading_cycle_id": self.reading_cycle_id,
            "unit_id": self.unit_id,
            "unit_index": self.unit_index,
            "source_char_count": self.source_char_count,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "settlement_status": self.settlement_status,
        }
        return {key: value for key, value in fields.items() if value is not None and value != ""}


_CURRENT_OBSERVATION_CONTEXT = contextvars.ContextVar("reading_observation_context", default=None)


def current_observation_context() -> ObservationContext | None:
    """Return the current immutable observation context, if one is active."""

    return _CURRENT_OBSERVATION_CONTEXT.get()


def _telemetry_attributes(context: ObservationContext) -> dict[str, object]:
    mappings = {
        "reading.job.id": context.job_id,
        "reading.job.kind": context.job_kind,
        "reading.run.id": context.run_id,
        "reading.run_attempt.id": context.run_attempt_id,
        "reading.lease.generation": context.lease_generation,
        "reading.book.id": context.book_id,
        "reading.mechanism.id": context.mechanism_key,
        "reading.stage.id": context.stage,
        "reading.node.id": context.node,
        "reading.chapter.id": context.chapter_id,
        "reading.chapter.index": context.chapter_index,
        "reading.cycle.id": context.reading_cycle_id,
        "reading.unit.id": context.unit_id,
        "reading.unit.index": context.unit_index,
        "reading.unit.source_char_count": context.source_char_count,
    }
    return {key: value for key, value in mappings.items() if value is not None and value != ""}


class ObservationScope:
    """Context manager handle shared by run, chapter, and reading-cycle scopes."""

    def __init__(
        self,
        *,
        scope_kind: str,
        span_name: str,
        context: ObservationContext,
        enabled: bool = True,
    ) -> None:
        self.scope_kind = scope_kind
        self._span_name = span_name
        self._context = context
        self._enabled = enabled
        self._token: contextvars.Token[ObservationContext | None] | None = None
        self._telemetry_manager: Any | None = None
        self._telemetry_span = TelemetrySpan()
        self._entered = False
        self._settled = False
        self._started_monotonic = 0.0
        self._settle_result: ObservationRecordResult | None = None
        self._start_result: ObservationRecordResult | None = None
        self._report_result: Any | None = None
        self._telemetry_failure_baseline = 0
        self._telemetry_failed_export_span_baseline = 0
        self._telemetry_exit_result = False

    def __enter__(self) -> "ObservationScope":
        if self._entered:
            raise RuntimeError("observation scope cannot be entered twice")
        if not self._enabled:
            self._entered = True
            return self
        parent = current_observation_context()
        parent_span_id = parent.span_id if parent is not None else None
        if self.scope_kind == "run":
            telemetry_before = telemetry_status()
            self._telemetry_failure_baseline = int(
                telemetry_before.get("detected_failure_count", 0) or 0
            )
            self._telemetry_failed_export_span_baseline = int(
                telemetry_before.get("failed_export_span_count", 0) or 0
            )
        self._telemetry_manager = telemetry_span(
            self._span_name,
            span_kind="CHAIN",
            attributes=_telemetry_attributes(self._context),
        )
        self._telemetry_span = self._telemetry_manager.__enter__()
        self._context = replace(
            self._context,
            trace_id=self._telemetry_span.trace_id or (parent.trace_id if parent else None),
            span_id=self._telemetry_span.span_id or None,
            parent_span_id=parent_span_id,
        )
        self._token = _CURRENT_OBSERVATION_CONTEXT.set(self._context)
        self._started_monotonic = time.monotonic()
        self._entered = True
        started_kind = {
            "run": "run_attempt_started",
            "chapter": "chapter_started",
            "reading_cycle": "reading_cycle_started",
        }[self.scope_kind]
        self._start_result = self._append_lifecycle_event(started_kind, status="started", duration_ms=None)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if not self._entered:
            return False
        if not self._enabled:
            if not self._settled:
                self.settle("error" if exc_type is not None else "completed")
            self._entered = False
            return False
        if self._token is None:
            return False
        if not self._settled:
            status = "error" if exc_type is not None else "completed"
            self.settle(status, error_type=exc_type.__name__ if exc_type else None)
        if self.scope_kind == "run":
            # End the root span and drain the batch before taking the run-local
            # exporter snapshot. This lets asynchronous HTTP export failures
            # appear in the canonical data-quality event for this run.
            if self._telemetry_manager is not None:
                try:
                    self._telemetry_exit_result = bool(
                        self._telemetry_manager.__exit__(exc_type, exc, traceback)
                    )
                except Exception:
                    self._telemetry_exit_result = False
                self._telemetry_manager = None
            flush_telemetry(timeout_millis=5_000)
            telemetry = telemetry_status()
            failure_count = max(
                0,
                int(telemetry.get("detected_failure_count", 0) or 0)
                - self._telemetry_failure_baseline,
            )
            failed_export_span_count = max(
                0,
                int(telemetry.get("failed_export_span_count", 0) or 0)
                - self._telemetry_failed_export_span_baseline,
            )
            if telemetry.get("enabled") and failure_count > 0:
                append_observation_event(
                    self._context.ledger_path,
                    {
                        **self._context.event_fields(),
                        "event_id": self._event_identity(
                            "telemetry_export_failed",
                            telemetry.get("initialization_error"),
                        ),
                        "event_kind": "telemetry_export_failed",
                        "status": "error",
                        "error_type": str(telemetry.get("initialization_error") or "detected_export_failure"),
                        "detected_failure_count": failure_count,
                        "failed_export_span_count": failed_export_span_count,
                    },
                )
            try:
                from .observation_metrics import write_observation_reports

                self._report_result = write_observation_reports(self._context.ledger_path or "")
                if self._report_result.errors:
                    append_observation_event(
                        self._context.ledger_path,
                        {
                            **self._context.event_fields(),
                            "event_id": self._event_identity(
                                "observation_report_failed",
                                tuple(self._report_result.errors),
                            ),
                            "event_kind": "observation_report_failed",
                            "status": "error",
                            "error_components": [
                                str(error).split(":", 1)[0]
                                for error in self._report_result.errors
                            ],
                        },
                    )
            except Exception as exc:
                self._report_result = None
                append_observation_event(
                    self._context.ledger_path,
                    {
                        **self._context.event_fields(),
                        "event_id": self._event_identity(
                            "observation_report_failed",
                            type(exc).__name__,
                        ),
                        "event_kind": "observation_report_failed",
                        "status": "error",
                        "error_components": [type(exc).__name__],
                    },
                )
        _CURRENT_OBSERVATION_CONTEXT.reset(self._token)
        self._entered = False
        if self._telemetry_manager is None:
            return self._telemetry_exit_result
        return bool(self._telemetry_manager.__exit__(exc_type, exc, traceback))

    @property
    def context(self) -> ObservationContext:
        return self._context

    @property
    def settle_result(self) -> ObservationRecordResult | None:
        return self._settle_result

    @property
    def start_result(self) -> ObservationRecordResult | None:
        return self._start_result

    @property
    def report_result(self) -> Any | None:
        return self._report_result

    def _event_identity(self, event_kind: str, *extra: object) -> str:
        return deterministic_event_id(
            event_kind,
            self._context.job_id,
            self._context.run_attempt_id,
            self._context.stage,
            self._context.node,
            self._context.chapter_id,
            self._context.reading_cycle_id,
            *extra,
        )

    def _append_lifecycle_event(
        self,
        event_kind: str,
        *,
        status: str,
        duration_ms: int | None,
        error_type: str | None = None,
        identity_extra: tuple[object, ...] = (),
    ) -> ObservationRecordResult:
        event: dict[str, object] = {
            **self._context.event_fields(),
            "event_id": self._event_identity(event_kind, *identity_extra),
            "event_kind": event_kind,
            "status": status,
        }
        if duration_ms is not None:
            event["duration_ms"] = duration_ms
        if error_type:
            event["error_type"] = error_type
        return append_observation_event(self._context.ledger_path, event)

    def select_unit(self, unit_id: str, source_char_count: int, unit_index: int) -> ObservationContext:
        """Select one unit without mutating context inherited by prior copies."""

        if not self._entered:
            raise RuntimeError("select_unit requires an active observation scope")
        if not self._enabled:
            return self._context
        normalized_unit_id = str(unit_id or "").strip()
        if not normalized_unit_id:
            raise ValueError("unit_id is required")
        if int(source_char_count) < 0 or int(unit_index) < 0:
            raise ValueError("source_char_count and unit_index must be non-negative")
        current = current_observation_context() or self._context
        self._context = replace(
            current,
            unit_id=normalized_unit_id,
            source_char_count=int(source_char_count),
            unit_index=int(unit_index),
        )
        _CURRENT_OBSERVATION_CONTEXT.set(self._context)
        self._telemetry_span.set_attributes(_telemetry_attributes(self._context))
        append_observation_event(
            self._context.ledger_path,
            {
                **self._context.event_fields(),
                "event_id": self._event_identity("unit_selected", normalized_unit_id, int(unit_index)),
                "event_kind": "unit_selected",
                "status": "selected",
            },
        )
        return self._context

    def settle(self, status: str, *, error_type: str | None = None) -> ObservationRecordResult:
        """Finalize the scope once; ledger/telemetry failures stay best effort."""

        if not self._entered:
            raise RuntimeError("settle requires an active observation scope")
        if self._settled and self._settle_result is not None:
            return self._settle_result
        if not self._enabled:
            self._settle_result = ObservationRecordResult(event={}, ledger_path=None, written=False)
            self._settled = True
            return self._settle_result
        normalized_status = str(status or "").strip().lower()
        if not normalized_status:
            raise ValueError("settlement status is required")
        current = current_observation_context() or self._context
        self._context = replace(current, settlement_status=normalized_status)
        _CURRENT_OBSERVATION_CONTEXT.set(self._context)
        self._telemetry_span.set_attributes({"reading.status": normalized_status})
        self._telemetry_span.set_status(normalized_status, error_type=error_type or "")
        duration_ms = max(0, int(round((time.monotonic() - self._started_monotonic) * 1000)))
        event_kind = {
            "run": "run_attempt_finished",
            "chapter": "chapter_finished",
            "reading_cycle": "unit_settled",
        }[self.scope_kind]
        self._settle_result = self._append_lifecycle_event(
            event_kind,
            status=normalized_status,
            duration_ms=duration_ms,
            error_type=str(error_type) if error_type else None,
        )
        self._settled = True
        return self._settle_result


def _inherited_context(**changes: object) -> ObservationContext:
    parent = current_observation_context() or ObservationContext()
    return replace(parent, **changes)


def run_observation_scope(
    output_dir: Path | str,
    job_id: str,
    *,
    run_id: str | None = None,
    run_attempt_id: str | None = None,
    lease_generation: int | None = None,
    active_interval_started_at: str | None = None,
    book_id: str | None = None,
    mechanism_key: str | None = None,
    job_kind: str | None = None,
    stage: str | None = None,
    node: str | None = None,
) -> ObservationScope:
    """Create the root ``reading.run_attempt`` observation scope."""

    output_path = Path(output_dir)
    normalized_job_id = str(job_id or "").strip()
    normalized_run_attempt_id = str(run_attempt_id or "").strip() or f"run-attempt-{uuid.uuid4().hex}"
    context = ObservationContext(
        ledger_path=str(observation_ledger_file(output_path, normalized_job_id)),
        job_id=normalized_job_id,
        job_kind=str(job_kind or "").strip() or None,
        run_id=str(run_id or normalized_job_id).strip(),
        run_attempt_id=normalized_run_attempt_id,
        lease_generation=int(lease_generation) if lease_generation is not None else None,
        active_interval_started_at=str(active_interval_started_at or "").strip() or None,
        book_id=str(book_id or output_path.name).strip() or None,
        mechanism_key=str(mechanism_key or "").strip() or None,
        stage=str(stage or "").strip() or None,
        node=str(node or "").strip() or None,
    )
    return ObservationScope(scope_kind="run", span_name="reading.run_attempt", context=context)


def product_run_observation_scope(
    output_dir: Path | str,
    *,
    mechanism_key: str,
    stage: str = "read",
) -> ObservationScope:
    """Create a product-run scope from a managed lease or an isolated direct CLI identity."""

    output_path = Path(output_dir)
    lease = current_lease()
    direct_job_id = f"direct-{output_path.name}-{uuid.uuid4().hex}"
    return run_observation_scope(
        output_path,
        lease.job_id if lease is not None else direct_job_id,
        run_id=lease.job_id if lease is not None else direct_job_id,
        run_attempt_id=lease.run_attempt_id if lease is not None else None,
        lease_generation=lease.generation if lease is not None else None,
        active_interval_started_at=lease.acquired_at if lease is not None else None,
        book_id=lease.book_id if lease is not None and lease.book_id else output_path.name,
        mechanism_key=mechanism_key,
        job_kind=lease.job_kind if lease is not None and lease.job_kind else "direct_read",
        stage=stage,
    )


def chapter_observation_scope(
    chapter_id: str,
    *,
    chapter_index: int | None = None,
    stage: str | None = None,
    node: str | None = None,
) -> ObservationScope:
    """Create a nested ``reading.chapter`` observation scope."""

    normalized_chapter_id = str(chapter_id or "").strip()
    if not normalized_chapter_id:
        raise ValueError("chapter_id is required")
    if chapter_index is not None and int(chapter_index) < 0:
        raise ValueError("chapter_index must be non-negative")
    enabled = current_observation_context() is not None
    context = _inherited_context(
        chapter_id=normalized_chapter_id,
        chapter_index=int(chapter_index) if chapter_index is not None else None,
        stage=str(stage or "").strip() or (current_observation_context().stage if enabled else None),
        node=str(node or "").strip() or None,
        reading_cycle_id=None,
        unit_id=None,
        unit_index=None,
        source_char_count=None,
        settlement_status=None,
    )
    return ObservationScope(
        scope_kind="chapter",
        span_name="reading.chapter",
        context=context,
        enabled=enabled,
    )


def reading_cycle_scope(
    cycle_id: str | None = None,
    *,
    stage: str | None = None,
    node: str | None = None,
) -> ObservationScope:
    """Create a nested ``reading.unit_attempt`` scope with a selectable unit."""

    normalized_cycle_id = str(cycle_id or "").strip() or f"cycle-{uuid.uuid4().hex}"
    enabled = current_observation_context() is not None
    context = _inherited_context(
        reading_cycle_id=normalized_cycle_id,
        stage=str(stage or "").strip()
        or (current_observation_context().stage if enabled else None),
        node=str(node or "").strip() or None,
        unit_id=None,
        unit_index=None,
        source_char_count=None,
        settlement_status=None,
    )
    return ObservationScope(
        scope_kind="reading_cycle",
        span_name="reading.unit_attempt",
        context=context,
        enabled=enabled,
    )


__all__ = [
    "OBSERVATION_CONTEXT_SCHEMA_VERSION",
    "ObservationContext",
    "ObservationScope",
    "chapter_observation_scope",
    "current_observation_context",
    "product_run_observation_scope",
    "reading_cycle_scope",
    "run_observation_scope",
]
