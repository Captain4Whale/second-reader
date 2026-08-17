from __future__ import annotations

from contextlib import contextmanager

from src.reading_runtime import llm_telemetry


def test_telemetry_disabled_is_a_noop(monkeypatch):
    monkeypatch.delenv("READING_OBSERVABILITY_OTLP_ENABLED", raising=False)
    with llm_telemetry.telemetry_span("reading.test", span_kind="CHAIN") as span:
        assert span.trace_id == ""
        assert span.span_id == ""
    assert llm_telemetry.telemetry_status()["enabled"] is False


def test_safe_attributes_reject_content_and_credentials():
    safe = llm_telemetry._safe_attributes(
        {
            "reading.job.id": "job-1",
            "llm.model_name": "example-model",
            "llm.token_count.prompt": 123,
            "gen_ai.usage.input_tokens": 123,
            "llm.prompt": "secret prompt",
            "reading.source_text": "copyrighted text",
            "llm.response_text": "generated text",
            "http.authorization": "Bearer secret",
            "reading.lease_token": "secret",
            "reading.metadata": {"raw": "not scalar"},
        }
    )
    assert safe == {
        "reading.job.id": "job-1",
        "llm.model_name": "example-model",
        "llm.token_count.prompt": 123,
        "gen_ai.usage.input_tokens": 123,
    }


def test_resource_allowlist_ignores_generic_otel_resource_environment(monkeypatch):
    captured: dict[str, str] = {}

    for name in (
        "OTEL_SERVICE_NAME",
        "BACKEND_VERSION",
        "READING_COMPANION_RUN_ATTEMPT_ID",
        "APP_ENVIRONMENT",
    ):
        monkeypatch.delenv(name, raising=False)

    class FakeResource:
        def __init__(self, *, attributes):
            captured.update(attributes)

        @classmethod
        def create(cls, _attributes):  # pragma: no cover - regression guard
            raise AssertionError("Resource.create would merge OTEL_RESOURCE_ATTRIBUTES")

    monkeypatch.setenv(
        "OTEL_RESOURCE_ATTRIBUTES",
        "future.payload=secret,process.command_args=private-book.epub",
    )

    llm_telemetry._build_resource(FakeResource, pid=123)

    assert captured == {
        "service.namespace": "reading-companion",
        "service.name": "reading-companion-backend",
        "service.version": "development",
        "service.instance.id": "pid-123",
        "deployment.environment.name": "development",
    }
    assert "future.payload" not in captured
    assert "process.command_args" not in captured


def test_span_manager_failure_never_escapes(monkeypatch):
    class BrokenManager:
        def __enter__(self):
            raise RuntimeError("collector unavailable")

        def __exit__(self, *_args):
            raise RuntimeError("collector unavailable")

    class BrokenTracer:
        def start_as_current_span(self, *_args, **_kwargs):
            return BrokenManager()

    monkeypatch.setattr(llm_telemetry, "_initialize", lambda: BrokenTracer())
    with llm_telemetry.telemetry_span("reading.test", span_kind="LLM") as span:
        assert span.trace_id == ""
        assert span.span_id == ""


def test_active_span_records_only_safe_attributes(monkeypatch):
    recorded: dict[str, object] = {}

    class FakeContext:
        is_valid = True
        trace_id = 1
        span_id = 2

    class FakeSpan:
        def get_span_context(self):
            return FakeContext()

        def set_attribute(self, key, value):
            recorded[key] = value

    @contextmanager
    def fake_manager():
        yield FakeSpan()

    class FakeTracer:
        def start_as_current_span(self, _name, *, attributes):
            recorded.update(attributes)
            return fake_manager()

    monkeypatch.setattr(llm_telemetry, "_initialize", lambda: FakeTracer())
    with llm_telemetry.telemetry_span(
        "reading.test",
        span_kind="LLM",
        attributes={"reading.job.id": "job-1", "llm.prompt": "secret"},
    ) as span:
        span.set_attributes(
            {
                "reading.unit.id": "u1",
                "reading.stage.id": "phase4",
                "reading.node.id": "digest",
                "reading.source_text": "secret",
            }
        )
        assert llm_telemetry.current_telemetry_span() is span
        assert span.trace_id == "00000000000000000000000000000001"
        assert span.span_id == "0000000000000002"

    assert recorded["openinference.span.kind"] == "LLM"
    assert recorded["reading.job.id"] == "job-1"
    assert recorded["reading.unit.id"] == "u1"
    assert recorded["reading.stage.id"] == "phase4"
    assert recorded["reading.node.id"] == "digest"
    assert "llm.prompt" not in recorded
    assert "reading.source_text" not in recorded
    assert llm_telemetry.current_telemetry_span() is None


def test_monitored_exporter_counts_failed_batch_without_raising(monkeypatch):
    monkeypatch.setattr(llm_telemetry, "_DETECTED_FAILURE_COUNT", 0)
    monkeypatch.setattr(llm_telemetry, "_FAILED_EXPORT_SPAN_COUNT", 0)

    class RejectingExporter:
        def export(self, _spans):
            return "failure"

        def shutdown(self):
            return None

        def force_flush(self, timeout_millis=30_000):
            del timeout_millis
            return True

    exporter = llm_telemetry._FailureRecordingSpanExporter(
        RejectingExporter(),
        success_result="success",
        failure_result="failure",
    )

    assert exporter.export((object(), object(), object())) == "failure"
    status = llm_telemetry.telemetry_status()
    assert status["detected_failure_count"] == 1
    assert status["failed_export_span_count"] == 3


def test_shutdown_flushes_the_captured_provider_before_clearing_it(monkeypatch):
    calls: list[str] = []

    class FakeProvider:
        def force_flush(self, *, timeout_millis):
            calls.append(f"flush:{timeout_millis}")
            return True

        def shutdown(self):
            calls.append("shutdown")

    monkeypatch.setattr(llm_telemetry, "_PROVIDER", FakeProvider())
    monkeypatch.setattr(llm_telemetry, "_TRACER", object())

    llm_telemetry.shutdown_telemetry()

    assert calls == ["flush:5000", "shutdown"]
    assert llm_telemetry._PROVIDER is None
    assert llm_telemetry._TRACER is None


def test_telemetry_decorator_preserves_return_and_exception(monkeypatch):
    monkeypatch.setattr(llm_telemetry, "_initialize", lambda: None)

    @llm_telemetry.telemetry_traced("reading.call", span_kind="CHAIN")
    def add(left: int, right: int) -> int:
        return left + right

    @llm_telemetry.telemetry_traced("reading.call", span_kind="CHAIN")
    def fail() -> None:
        raise ValueError("expected")

    assert add(2, 3) == 5
    try:
        fail()
    except ValueError as exc:
        assert str(exc) == "expected"
    else:  # pragma: no cover - assertion guard
        raise AssertionError("decorated exception was swallowed")
