"""Best-effort OpenTelemetry export for runtime observability.

The runtime ledger is the durable source of truth.  This module is deliberately
optional and non-throwing so a missing dependency or collector can never change
reader behaviour or cause another provider call.
"""

from __future__ import annotations

import atexit
import contextlib
import functools
import os
import socket
import threading
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Mapping, ParamSpec, TypeVar
from urllib.parse import urlparse


_TRUTHY = {"1", "true", "yes", "on"}
_INIT_LOCK = threading.Lock()
_STATE_PID: int | None = None
_TRACER: Any | None = None
_PROVIDER: Any | None = None
_INITIALIZATION_ERROR = ""
_DETECTED_FAILURE_COUNT = 0
_FAILED_EXPORT_SPAN_COUNT = 0
_SHUTDOWN_REGISTERED = False
_CURRENT_SPAN: ContextVar[TelemetrySpan | None]
_SAFE_ATTRIBUTE_KEYS = frozenset(
    {
        "error.type",
        "gen_ai.operation.name",
        "gen_ai.provider.name",
        "gen_ai.request.model",
        "gen_ai.usage.input_tokens",
        "gen_ai.usage.output_tokens",
        "llm.attempt.count",
        "llm.attempt.id",
        "llm.attempt.index",
        "llm.billing.model",
        "llm.call.id",
        "llm.cost.actual_billed_cost_usd",
        "llm.cost.estimated_usage_value_usd",
        "llm.input_messages.count",
        "llm.model_name",
        "llm.profile.id",
        "llm.provider.id",
        "llm.quota_wait_ms_total",
        "llm.retry.count",
        "llm.target.id",
        "llm.token_count.cache_read",
        "llm.token_count.cache_write",
        "llm.token_count.completion",
        "llm.token_count.prompt",
        "llm.token_count.reasoning",
        "llm.token_count.total",
        "llm.usage.status",
        "openinference.span.kind",
        "reading.book.id",
        "reading.chapter.id",
        "reading.chapter.index",
        "reading.cycle.id",
        "reading.job.id",
        "reading.job.kind",
        "reading.lease.generation",
        "reading.mechanism.id",
        "reading.node.id",
        "reading.run.id",
        "reading.run_attempt.id",
        "reading.stage.id",
        "reading.status",
        "reading.unit.id",
        "reading.unit.index",
        "reading.unit.source_char_count",
    }
)


def _enabled() -> bool:
    return os.environ.get("READING_OBSERVABILITY_OTLP_ENABLED", "0").strip().lower() in _TRUTHY


def _record_failure(*, failed_export_span_count: int = 0) -> None:
    global _DETECTED_FAILURE_COUNT, _FAILED_EXPORT_SPAN_COUNT
    with _INIT_LOCK:
        _DETECTED_FAILURE_COUNT += 1
        _FAILED_EXPORT_SPAN_COUNT += max(0, int(failed_export_span_count))


def _verify_local_collector(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    host = str(parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or host not in {"127.0.0.1", "localhost"}:
        raise ValueError("runtime OTLP endpoint must use HTTP(S) on localhost")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    with socket.create_connection((host, port), timeout=0.5):
        return


def _safe_attributes(attributes: Mapping[str, object] | None) -> dict[str, object]:
    """Keep only explicitly named scalar facts; unknown keys are dropped."""

    safe: dict[str, object] = {}
    for key, value in (attributes or {}).items():
        normalized_key = str(key or "").strip()
        if not normalized_key or normalized_key not in _SAFE_ATTRIBUTE_KEYS or value is None:
            continue
        if isinstance(value, (str, bool, int, float)):
            safe[normalized_key] = value[:512] if isinstance(value, str) else value
            continue
        if isinstance(value, (list, tuple)) and all(isinstance(item, (str, bool, int, float)) for item in value):
            safe[normalized_key] = [item[:512] if isinstance(item, str) else item for item in value]
    return safe


def _resource_attributes(pid: int) -> dict[str, str]:
    """Build the exact resource allowlist without consulting generic OTel env attributes."""

    return {
        "service.namespace": "reading-companion",
        "service.name": os.environ.get(
            "OTEL_SERVICE_NAME",
            "reading-companion-backend",
        ).strip()
        or "reading-companion-backend",
        "service.version": os.environ.get("BACKEND_VERSION", "development").strip()
        or "development",
        "service.instance.id": os.environ.get(
            "READING_COMPANION_RUN_ATTEMPT_ID",
            f"pid-{pid}",
        ).strip()
        or f"pid-{pid}",
        "deployment.environment.name": os.environ.get(
            "APP_ENVIRONMENT",
            "development",
        ).strip()
        or "development",
    }


def _build_resource(resource_type: Any, *, pid: int) -> Any:
    """Construct a resource directly so OTEL_RESOURCE_ATTRIBUTES cannot add fields."""

    return resource_type(attributes=_resource_attributes(pid))


class _FailureRecordingSpanExporter:
    """Wrap one exporter so asynchronous batch failures become local counters."""

    def __init__(self, delegate: Any, *, success_result: Any, failure_result: Any) -> None:
        self._delegate = delegate
        self._success_result = success_result
        self._failure_result = failure_result

    def export(self, spans: Any) -> Any:
        try:
            span_count = len(spans)
        except (TypeError, AttributeError):
            spans = tuple(spans)
            span_count = len(spans)
        try:
            result = self._delegate.export(spans)
        except Exception:
            _record_failure(failed_export_span_count=span_count)
            return self._failure_result
        if result != self._success_result:
            _record_failure(failed_export_span_count=span_count)
        return result

    def shutdown(self) -> None:
        try:
            self._delegate.shutdown()
        except Exception:
            _record_failure()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        try:
            result = self._delegate.force_flush(timeout_millis=timeout_millis)
        except Exception:
            _record_failure()
            return False
        if result is False:
            _record_failure()
            return False
        return True


def _initialize() -> Any | None:
    """Return one process-local tracer, swallowing all optional-export failures."""

    global _STATE_PID, _TRACER, _PROVIDER, _INITIALIZATION_ERROR, _SHUTDOWN_REGISTERED
    global _DETECTED_FAILURE_COUNT, _FAILED_EXPORT_SPAN_COUNT

    if not _enabled():
        return None
    pid = os.getpid()
    if _STATE_PID == pid and (_TRACER is not None or _INITIALIZATION_ERROR):
        return _TRACER
    with _INIT_LOCK:
        if _STATE_PID == pid and (_TRACER is not None or _INITIALIZATION_ERROR):
            return _TRACER
        _STATE_PID = pid
        _TRACER = None
        _PROVIDER = None
        _INITIALIZATION_ERROR = ""
        _DETECTED_FAILURE_COUNT = 0
        _FAILED_EXPORT_SPAN_COUNT = 0
        try:
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace.export import SpanExportResult
            from phoenix.otel import BatchSpanProcessor, HTTPSpanExporter, register

            endpoint = os.environ.get(
                "READING_OBSERVABILITY_OTLP_ENDPOINT",
                "http://127.0.0.1:6006/v1/traces",
            ).strip()
            _verify_local_collector(endpoint)
            project_name = os.environ.get(
                "READING_OBSERVABILITY_PROJECT",
                "reading-companion-runtime",
            ).strip() or "reading-companion-runtime"
            resource = _build_resource(Resource, pid=pid)
            provider = register(
                project_name=project_name,
                endpoint=endpoint,
                protocol="http/protobuf",
                batch=False,
                auto_instrument=False,
                set_global_tracer_provider=False,
                verbose=False,
                resource=resource,
            )
            exporter = _FailureRecordingSpanExporter(
                HTTPSpanExporter(endpoint=endpoint, timeout=5.0),
                success_result=SpanExportResult.SUCCESS,
                failure_result=SpanExportResult.FAILURE,
            )
            provider.add_span_processor(
                BatchSpanProcessor(span_exporter=exporter),
                replace_default_processor=True,
            )
            _PROVIDER = provider
            _TRACER = provider.get_tracer("reading-companion-runtime-observability")
            if not _SHUTDOWN_REGISTERED:
                atexit.register(shutdown_telemetry)
                _SHUTDOWN_REGISTERED = True
        except Exception as exc:  # pragma: no cover - optional dependency/runtime path
            _INITIALIZATION_ERROR = type(exc).__name__
            _DETECTED_FAILURE_COUNT += 1
            _TRACER = None
            _PROVIDER = None
        return _TRACER


@dataclass
class TelemetrySpan:
    """A non-throwing wrapper around an optional OpenTelemetry span context."""

    _manager: Any | None = None
    _span: Any | None = None
    trace_id: str = ""
    span_id: str = ""

    def set_attributes(self, attributes: Mapping[str, object] | None) -> None:
        if self._span is None:
            return
        try:
            for key, value in _safe_attributes(attributes).items():
                self._span.set_attribute(key, value)
        except Exception:
            return

    def set_status(self, status: str, *, error_type: str = "") -> None:
        if self._span is None:
            return
        try:
            self._span.set_attribute("reading.status", str(status or "unknown"))
            if error_type:
                self._span.set_attribute("error.type", str(error_type))
        except Exception:
            return


_CURRENT_SPAN = ContextVar("reading_companion_telemetry_span", default=None)


def current_telemetry_span() -> TelemetrySpan | None:
    """Return the current project-owned span wrapper, if any."""

    return _CURRENT_SPAN.get()


def _span_ids(span: Any | None) -> tuple[str, str]:
    if span is None:
        return "", ""
    try:
        context = span.get_span_context()
        if not context or not context.is_valid:
            return "", ""
        return f"{int(context.trace_id):032x}", f"{int(context.span_id):016x}"
    except Exception:
        return "", ""


@contextlib.contextmanager
def telemetry_span(
    name: str,
    *,
    span_kind: str,
    attributes: Mapping[str, object] | None = None,
) -> Iterator[TelemetrySpan]:
    """Start one manual OpenInference-shaped span when export is enabled."""

    tracer = _initialize()
    if tracer is None:
        yield TelemetrySpan()
        return
    manager: Any | None = None
    span: Any | None = None
    wrapper = TelemetrySpan()
    try:
        span_attributes = _safe_attributes(attributes)
        span_attributes["openinference.span.kind"] = str(span_kind or "CHAIN").upper()
        manager = tracer.start_as_current_span(str(name or "reading.observation"), attributes=span_attributes)
        span = manager.__enter__()
        trace_id, span_id = _span_ids(span)
        wrapper = TelemetrySpan(manager, span, trace_id, span_id)
    except Exception:
        manager = None
        span = None
        wrapper = TelemetrySpan()
        _record_failure(failed_export_span_count=1)
    try:
        token = _CURRENT_SPAN.set(wrapper)
        yield wrapper
    except BaseException as exc:
        wrapper.set_status("error", error_type=type(exc).__name__)
        raise
    finally:
        _CURRENT_SPAN.reset(token)
        if manager is not None:
            try:
                manager.__exit__(None, None, None)
            except Exception:
                _record_failure()


_P = ParamSpec("_P")
_R = TypeVar("_R")


def telemetry_traced(name: str, *, span_kind: str) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorate a synchronous function with one best-effort manual span."""

    def _decorate(function: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(function)
        def _wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            with telemetry_span(name, span_kind=span_kind):
                return function(*args, **kwargs)

        return _wrapped

    return _decorate


def telemetry_status() -> dict[str, object]:
    """Return compact exporter health without exposing endpoints or headers."""

    return {
        "enabled": _enabled(),
        "initialized": _TRACER is not None and _STATE_PID == os.getpid(),
        "initialization_error": _INITIALIZATION_ERROR or None,
        "detected_failure_count": _DETECTED_FAILURE_COUNT,
        "failed_export_span_count": _FAILED_EXPORT_SPAN_COUNT,
    }


def flush_telemetry(*, timeout_millis: int = 5_000) -> bool:
    """Best-effort flush before a run snapshots exporter data quality."""

    provider = _PROVIDER
    if provider is None:
        return True
    try:
        flushed = provider.force_flush(timeout_millis=max(1, int(timeout_millis)))
    except Exception:
        _record_failure()
        return False
    if flushed is False:
        _record_failure()
        return False
    return True


def shutdown_telemetry() -> None:
    """Best-effort flush and shutdown for a process-local batch exporter."""

    global _PROVIDER, _TRACER
    provider = _PROVIDER
    if provider is None:
        _TRACER = None
        return
    try:
        flushed = provider.force_flush(timeout_millis=5_000)
        if flushed is False:
            _record_failure()
    except Exception:
        _record_failure()
    try:
        provider.shutdown()
    except Exception:
        _record_failure()
    finally:
        _PROVIDER = None
        _TRACER = None


__all__ = [
    "TelemetrySpan",
    "current_telemetry_span",
    "flush_telemetry",
    "shutdown_telemetry",
    "telemetry_span",
    "telemetry_status",
    "telemetry_traced",
]
