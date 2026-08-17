from __future__ import annotations

import asyncio
import contextvars
import contextlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage

from src.reading_runtime.llm_pricing import (
    DEFAULT_PRICING_CATALOG_PATH,
    PricingCatalog,
    PricingCatalogError,
    estimate_usage_cost,
    load_pricing_catalog,
)
from src.reading_runtime.llm_usage import NormalizedUsage, normalize_provider_usage
from src.reading_runtime import observation_context as observation_context_module
from src.reading_runtime import observation_ledger as observation_ledger_module
from src.reading_runtime import observability as observability_module
from src.reading_runtime.observation_context import (
    chapter_observation_scope,
    current_observation_context,
    reading_cycle_scope,
    run_observation_scope,
)
from src.reading_runtime.observation_ledger import (
    ObservationLedgerReadError,
    append_observation_event,
    deterministic_event_id,
    load_observation_events,
    observation_ledger_diagnostics,
    observation_ledger_file,
)
from src.reading_runtime.observation_metrics import aggregate_observation_metrics, write_observation_reports
from src.reading_runtime.observability import record_llm_attempt, record_llm_call
from src.reading_runtime.llm_telemetry import TelemetrySpan


class _Response:
    def __init__(self, *, usage_metadata=None, response_metadata=None):
        self.usage_metadata = usage_metadata
        self.response_metadata = response_metadata


def test_normalize_provider_usage_covers_common_shapes_and_invalid_metadata() -> None:
    langchain = normalize_provider_usage(
        _Response(
            usage_metadata={
                "input_tokens": 100,
                "output_tokens": 20,
                "input_token_details": {"cache_read": 10, "cache_creation": 5},
                "output_token_details": {"reasoning": 7},
            }
        )
    )
    assert langchain.status == "complete"
    assert langchain.total_tokens == 120
    assert langchain.cache_read_input_tokens == 10
    assert langchain.cache_write_input_tokens == 5
    assert langchain.uncached_input_tokens == 85
    assert langchain.reasoning_tokens == 7
    assert langchain.billable_output_tokens == 20

    openai = normalize_provider_usage(
        _Response(
            response_metadata={
                "token_usage": {
                    "prompt_tokens": 30,
                    "completion_tokens": 8,
                    "total_tokens": 38,
                    "prompt_tokens_details": {"cached_tokens": 6},
                    "completion_tokens_details": {"reasoning_tokens": 3},
                }
            }
        )
    )
    assert openai.source == "response_metadata.token_usage"
    assert openai.cache_read_input_tokens == 6
    assert openai.reasoning_tokens == 3

    anthropic = normalize_provider_usage(
        _Response(
            response_metadata={
                "model_provider": "anthropic",
                "usage": {
                    "input_tokens": 25,
                    "cache_read_input_tokens": 10,
                    "cache_creation_input_tokens": 5,
                    "output_tokens": 8,
                },
            }
        )
    )
    assert anthropic.provider_family == "anthropic"
    assert anthropic.input_tokens == 25
    assert anthropic.uncached_input_tokens == 25
    assert anthropic.cache_read_input_tokens == 10
    assert anthropic.cache_write_input_tokens == 5
    assert anthropic.total_tokens == 48

    google = normalize_provider_usage(
        {
            "usage": {
                "prompt_token_count": 40,
                "candidates_token_count": 9,
                "total_token_count": 51,
                "cached_content_token_count": 4,
                "thoughts_token_count": 2,
            }
        }
    )
    assert google.status == "complete"
    assert google.uncached_input_tokens == 36
    assert google.reasoning_tokens == 2
    assert google.billable_output_tokens == 11

    invalid = normalize_provider_usage({"usage": {"input_tokens": "not-a-count", "output_tokens": 2}})
    assert invalid.status == "invalid"
    assert invalid.invalid_fields == ("input_tokens",)
    contradictory = normalize_provider_usage(
        {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "total_tokens": 120,
                "prompt_tokens_details": {"cached_tokens": 200},
            }
        }
    )
    assert contradictory.status == "invalid"
    assert contradictory.uncached_input_tokens is None
    assert contradictory.invalid_fields == (
        "cache_input_tokens_exceed_input_tokens",
    )
    assert normalize_provider_usage({"content": "no usage"}).status == "unavailable"


def test_tracked_pricing_catalog_matches_subscription_and_estimates_usage_value() -> None:
    catalog = PricingCatalog.load(DEFAULT_PRICING_CATALOG_PATH)
    rule = catalog.match(
        provider_id="opencode_deepseek_v4_flash",
        target_id="opencode_deepseek_v4_flash",
        model="deepseek-v4-flash",
        at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )
    assert rule is not None
    assert rule.billing_model == "subscription"
    assert rule.input_per_million == Decimal("0.14")
    assert rule.output_per_million == Decimal("0.28")
    assert rule.cache_read_input_per_million == Decimal("0.0028")
    assert rule.cache_write_input_per_million is None
    assert rule.cache_write_pricing_applicable is False
    assert rule.actual_billed_cost is None
    snapshot = rule.snapshot(catalog_version=catalog.catalog_version)
    assert snapshot["source"]["url"] == "https://opencode.ai/docs/go/"
    assert str(snapshot["snapshot_hash"]).startswith("sha256:")

    estimate = estimate_usage_cost(
        NormalizedUsage(
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            total_tokens=2_000_000,
            cache_read_input_tokens=100_000,
            cache_write_input_tokens=0,
            uncached_input_tokens=900_000,
            billable_output_tokens=1_000_000,
            status="complete",
            source="test",
        ),
        rule,
    )
    assert estimate.status == "complete"
    assert estimate.billing_model == "subscription"
    assert estimate.estimated_usage_value_usd == Decimal("0.40628")
    assert estimate.actual_billed_cost is None

    unavailable_cache_write = estimate_usage_cost(
        NormalizedUsage(
            input_tokens=20,
            output_tokens=5,
            total_tokens=25,
            cache_read_input_tokens=0,
            cache_write_input_tokens=10,
            uncached_input_tokens=10,
            billable_output_tokens=5,
            status="complete",
            source="test",
        ),
        rule,
    )
    assert unavailable_cache_write.status == "unpriced_cache_write"
    assert unavailable_cache_write.estimated_usage_value_usd is None

    omitted_non_applicable_cache_category = estimate_usage_cost(
        NormalizedUsage(
            input_tokens=20,
            output_tokens=5,
            total_tokens=25,
            cache_read_input_tokens=0,
            cache_write_input_tokens=None,
            uncached_input_tokens=20,
            billable_output_tokens=5,
            status="complete",
            source="test",
        ),
        rule,
    )
    assert omitted_non_applicable_cache_category.status == "complete"
    assert omitted_non_applicable_cache_category.estimated_usage_value_usd == Decimal(
        "0.0000042"
    )

    assert catalog.match(
        target_id="opencode_deepseek_v4_flash",
        model="deepseek-v4-flash",
        at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    ) is None
    with pytest.raises(PricingCatalogError, match="schema_version"):
        PricingCatalog.from_mapping({"schema_version": 2, "catalog_version": "future", "entries": []})
    non_usd = json.loads(DEFAULT_PRICING_CATALOG_PATH.read_text(encoding="utf-8"))
    non_usd["currency"] = "EUR"
    with pytest.raises(PricingCatalogError, match="only supports USD"):
        PricingCatalog.from_mapping(non_usd)


def test_openai_langchain_usage_without_cache_write_still_has_reference_value() -> None:
    response = AIMessage(
        content="{}",
        usage_metadata={
            "input_tokens": 1_000,
            "output_tokens": 100,
            "total_tokens": 1_100,
            "input_token_details": {"cache_read": 200},
        },
        response_metadata={"model_provider": "openai"},
    )
    usage = normalize_provider_usage(response, provider_family="openai_compatible")
    rule = PricingCatalog.load(DEFAULT_PRICING_CATALOG_PATH).match(
        provider_id="openai_compatible",
        target_id="opencode_deepseek_v4_flash",
        model="deepseek-v4-flash",
        at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )

    estimate = estimate_usage_cost(usage, rule)

    assert usage.cache_write_input_tokens is None
    assert usage.uncached_input_tokens == 800
    assert estimate.status == "complete"
    assert estimate.estimated_usage_value_usd == Decimal("0.00014056")


def test_local_pricing_catalog_completely_overrides_tracked_snapshot(tmp_path: Path) -> None:
    tracked = json.loads(DEFAULT_PRICING_CATALOG_PATH.read_text(encoding="utf-8"))
    local = json.loads(DEFAULT_PRICING_CATALOG_PATH.read_text(encoding="utf-8"))
    tracked["catalog_version"] = "tracked"
    local["catalog_version"] = "local"
    local["entries"][0]["rates_per_million"]["input"] = "9.99"
    tracked_path = tmp_path / "llm_pricing.json"
    local_path = tmp_path / "llm_pricing.local.json"
    tracked_path.write_text(json.dumps(tracked), encoding="utf-8")
    local_path.write_text(json.dumps(local), encoding="utf-8")

    catalog = load_pricing_catalog(tracked_path, local_override_path=local_path)

    assert catalog.catalog_version == "local"
    assert catalog.rules[0].input_per_million == Decimal("9.99")


def test_nested_scopes_record_stable_events_and_restore_copy_safe_context(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("READING_OBSERVABILITY_OTLP_ENABLED", "0")
    output_dir = tmp_path / "output" / "book-a"
    assert current_observation_context() is None

    with run_observation_scope(
        output_dir,
        "job-a",
        book_id="book-a",
        mechanism_key="attentional_v2",
        job_kind="sequential_read",
        stage="read",
    ) as run:
        assert run.context.run_attempt_id is not None
        assert run.context.run_attempt_id.startswith("run-attempt-")
        assert run.start_result is not None and run.start_result.written
        with chapter_observation_scope("chapter-1", chapter_index=0):
            with reading_cycle_scope("cycle-1") as cycle:
                context_before_selection = contextvars.copy_context()
                selected = cycle.select_unit("unit-1", 1_000_000, 0)
                assert selected.unit_id == "unit-1"
                assert context_before_selection.run(current_observation_context).unit_id is None
                attempt = record_llm_attempt(
                    call_id="call-1",
                    attempt_index=1,
                    status="ok",
                    usage={
                        "input_tokens": 1_000_000,
                        "output_tokens": 1_000_000,
                            "total_tokens": 2_000_000,
                            "cache_read_input_tokens": 100_000,
                            "cache_write_input_tokens": 0,
                        },
                        provider_id="opencode_deepseek_v4_flash",
                        provider_contract="openai_compatible",
                    target_id="opencode_deepseek_v4_flash",
                    model="deepseek-v4-flash",
                    node="digest",
                    started_at="2026-08-16T01:00:00Z",
                    duration_ms=1000,
                    quota_wait_ms=100,
                    provider_gate_wait_ms=50,
                    profile_gate_wait_ms=50,
                    otel_trace_id="1" * 32,
                    otel_span_id="2" * 16,
                    otel_parent_span_id="3" * 16,
                )
                assert attempt.written
                first_call = record_llm_call(
                    call_id="call-1",
                    status="ok",
                    attempt_count=1,
                    duration_ms=1000,
                    quota_wait_ms_total=100,
                    node="digest",
                )
                duplicate_call = record_llm_call(
                    call_id="call-1",
                    status="ok",
                    attempt_count=1,
                    duration_ms=1000,
                    quota_wait_ms_total=100,
                    node="digest",
                )
                assert first_call.event["event_id"] == duplicate_call.event["event_id"]
                assert cycle.settle("completed").written
            assert current_observation_context().chapter_id == "chapter-1"
        assert current_observation_context().job_id == "job-a"
    assert current_observation_context() is None

    ledger_path = observation_ledger_file(output_dir, "job-a")
    events, malformed = load_observation_events(ledger_path)
    assert malformed == 0
    kinds = [event["event_kind"] for event in events]
    assert kinds == [
        "run_attempt_started",
        "chapter_started",
        "reading_cycle_started",
        "unit_selected",
        "llm_provider_attempt_finished",
        "llm_logical_call_finished",
        "llm_logical_call_finished",
        "unit_settled",
        "chapter_finished",
        "run_attempt_finished",
    ]
    attempt_event = next(
        event
        for event in events
        if event["event_kind"] == "llm_provider_attempt_finished"
    )
    assert attempt_event["job_kind"] == "sequential_read"
    assert attempt_event["stage"] == "read"
    assert attempt_event["unit_id"] == "unit-1"
    assert attempt_event["usage"]["uncached_input_tokens"] == 900_000
    assert attempt_event["usage"]["billable_output_tokens"] == 1_000_000
    assert attempt_event["pricing"]["snapshot_hash"].startswith("sha256:")
    assert attempt_event["cost"]["billing_model"] == "subscription"
    assert attempt_event["cost"]["estimated_usage_value_usd"] == "0.40628"
    assert attempt_event["cost"]["actual_billed_cost"] is None
    assert attempt_event["otel"] == {
        "trace_id": "1" * 32,
        "span_id": "2" * 16,
        "parent_span_id": "3" * 16,
    }

    summary = aggregate_observation_metrics(events)
    assert summary["event_count"] == 9
    assert summary["duplicate_event_count"] == 1
    assert summary["attempt_count"] == 1
    assert summary["call_count"] == 1
    assert summary["unit_attempt_count"] == 1
    assert summary["source_char_count"] == 1_000_000
    assert summary["estimated_usage_value_usd"] == "0.40628"
    assert summary["cost_status_counts"] == {"complete": 1}
    assert summary["actual_billed_cost"] is None
    assert str(summary["combined_wait_share"]).startswith("0.166666")
    assert summary["call_quota_wait_ms"] == "100"
    assert summary["by_node"]["digest"]["logical_call_count"] == 1
    assert summary["by_unit"]["chapter-1/unit-1"]["accepted_source_chars"] == 1_000_000

    report = write_observation_reports(ledger_path)
    assert report.json_written and report.markdown_written and report.data_quality_written
    assert report.errors == ()
    assert json.loads(report.json_path.read_text(encoding="utf-8"))["duplicate_event_count"] == 1
    assert json.loads(report.data_quality_path.read_text(encoding="utf-8"))["usage_coverage"] == "1"
    assert "Missing usage or cost remains unknown" in report.markdown_path.read_text(encoding="utf-8")
    assert "## By chapter" in report.markdown_path.read_text(encoding="utf-8")
    assert "digest" in report.markdown_path.read_text(encoding="utf-8")


def test_ledger_is_concurrent_append_only_and_failures_are_best_effort(tmp_path: Path) -> None:
    path = tmp_path / "observability" / "events.jsonl"

    def append(index: int) -> bool:
        result = append_observation_event(
            path,
            {
                "event_id": deterministic_event_id("probe", index),
                "event_kind": "probe",
                "index": index,
            },
        )
        return result.written

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(pool.map(append, range(100)))
    events, malformed = load_observation_events(path)
    assert malformed == 0
    assert {event["index"] for event in events} == set(range(100))

    blocker = tmp_path / "not-a-directory"
    blocker.write_text("block", encoding="utf-8")
    failed = append_observation_event(blocker / "events.jsonl", {"event_kind": "probe"})
    assert failed.written is False
    assert failed.error is not None
    assert observation_ledger_diagnostics(blocker / "events.jsonl")["write_failure_count"] == 1

    no_scope = record_llm_call(call_id="outside", status="ok", attempt_count=0)
    assert no_scope.written is False
    assert no_scope.error is None

    bad_json_target = tmp_path / "json-is-directory"
    bad_json_target.mkdir()
    report = write_observation_reports(
        path,
        json_path=bad_json_target,
        markdown_path=tmp_path / "still-written.md",
    )
    assert report.json_written is False
    assert report.markdown_written is True
    assert len(report.errors) == 1
    quality = json.loads(report.data_quality_path.read_text(encoding="utf-8"))
    assert quality["report_write_failure_count"] == 1
    assert quality["report_write_failure_components"] == ["metrics"]


def test_ledger_read_error_is_explicit_and_does_not_look_like_one_malformed_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = tmp_path / "observability" / "events.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text('{"event_kind":"probe"}\n', encoding="utf-8")
    original_read_text = Path.read_text

    def unreadable(path: Path, *args, **kwargs):
        if path == ledger:
            raise OSError("simulated ledger outage")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable)

    with pytest.raises(ObservationLedgerReadError):
        load_observation_events(ledger)
    report = write_observation_reports(ledger)

    assert report.errors == ("ledger_read:OSError",)
    assert report.summary["malformed_line_count"] == 0
    assert report.summary["data_quality"]["ledger_read_error_count"] == 1
    assert report.summary["data_quality"]["ledger_read_error_type"] == "OSError"
    assert report.json_written and report.markdown_written and report.data_quality_written
    markdown = report.markdown_path.read_text(encoding="utf-8")
    assert "## Data unavailable" in markdown
    assert "could not be read (OSError)" in markdown
    assert "Accepted source characters: 0" not in markdown


def test_pricing_catalog_failure_is_recorded_without_escaping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        observability_module,
        "load_default_pricing_catalog",
        lambda: (_ for _ in ()).throw(PricingCatalogError("broken catalog")),
    )

    with run_observation_scope(tmp_path / "book", "job-pricing-failure"):
        result = record_llm_attempt(
            call_id="call-pricing-failure",
            attempt_index=1,
            status="success",
            usage=NormalizedUsage(
                input_tokens=10,
                output_tokens=2,
                total_tokens=12,
                uncached_input_tokens=10,
                billable_output_tokens=2,
                status="complete",
                source="test",
            ),
            target_id="target",
            model="model",
        )

    assert result.written is True
    assert result.event["cost"]["status"] == "pricing_error"


def test_metrics_union_lease_intervals_and_keep_partial_cost_breakdowns() -> None:
    events = [
        {
            "event_id": "run-a-start",
            "event_kind": "run_attempt_started",
            "run_attempt_id": "a",
            "active_interval_started_at": "2026-08-16T00:00:00Z",
            "observed_at": "2026-08-16T00:01:00Z",
        },
        {
            "event_id": "run-a-finish",
            "event_kind": "run_attempt_finished",
            "run_attempt_id": "a",
            "active_interval_started_at": "2026-08-16T00:00:00Z",
            "observed_at": "2026-08-16T00:10:00Z",
        },
        {
            "event_id": "run-b-start",
            "event_kind": "run_attempt_started",
            "run_attempt_id": "b",
            "active_interval_started_at": "2026-08-16T00:08:00Z",
            "observed_at": "2026-08-16T00:08:30Z",
        },
        {
            "event_id": "run-b-finish",
            "event_kind": "run_attempt_finished",
            "run_attempt_id": "b",
            "active_interval_started_at": "2026-08-16T00:08:00Z",
            "observed_at": "2026-08-16T00:15:00Z",
        },
        {
            "event_id": "unit",
            "event_kind": "unit_settled",
            "status": "accepted",
            "chapter_id": "1",
            "unit_id": "u1",
            "source_char_count": 10_000,
            "duration_ms": 500,
            "stage": "read",
        },
        {
            "event_id": "attempt",
            "event_kind": "llm_provider_attempt_finished",
            "call_id": "call",
            "attempt_index": 1,
            "status": "ok",
            "chapter_id": "1",
            "unit_id": "u1",
            "stage": "read",
            "node": "digest",
            "model": "model-a",
            "target_id": "target-a",
            "usage": {
                "status": "complete",
                "input_tokens": 100,
                "output_tokens": 20,
                "total_tokens": 120,
            },
            "cost": {
                "estimated_usage_value_usd": "0.01",
                "actual_billed_cost": None,
                "billing_model": "subscription",
            },
        },
        {
            "event_id": "call",
            "event_kind": "llm_logical_call_finished",
            "call_id": "call",
            "attempt_count": 1,
            "status": "ok",
            "chapter_id": "1",
            "unit_id": "u1",
            "stage": "read",
            "node": "digest",
            "model": "model-a",
            "target_id": "target-a",
        },
    ]

    summary = aggregate_observation_metrics(events)

    assert summary["elapsed_seconds"] == "900.0"
    assert summary["active_seconds"] == "900.0"
    assert summary["logical_calls_per_accepted_unit"] == "1"
    assert summary["total_tokens_per_10000_chars"] == "120"
    assert summary["by_chapter"]["1"]["logical_call_count"] == 1
    assert summary["by_unit"]["1/u1"]["estimated_usage_value_usd"] == "0.01"


def test_metrics_reconcile_missing_attempts_before_claiming_full_coverage() -> None:
    events = [
        {
            "event_id": "attempt-1",
            "event_kind": "llm_provider_attempt_finished",
            "job_id": "job",
            "run_attempt_id": "run",
            "call_id": "call",
            "chapter_id": "1",
            "reading_cycle_id": "cycle",
            "unit_id": "u1",
            "usage": {"status": "complete", "input_tokens": 10, "output_tokens": 2},
            "cost": {"estimated_usage_value_usd": "0.001"},
        },
        {
            "event_id": "call-1",
            "event_kind": "llm_logical_call_finished",
            "job_id": "job",
            "run_attempt_id": "run",
            "call_id": "call",
            "chapter_id": "1",
            "reading_cycle_id": "cycle",
            "unit_id": "u1",
            "attempt_count": 2,
            "status": "ok",
        },
    ]

    summary = aggregate_observation_metrics(events)

    assert summary["observed_physical_attempt_count"] == 1
    assert summary["expected_physical_attempt_count"] == 2
    assert summary["accounted_physical_attempt_count"] == 2
    assert summary["missing_physical_attempt_count"] == 1
    assert summary["data_quality"]["physical_attempt_accounting_coverage"] == "0.5"
    assert summary["data_quality"]["usage_coverage"] == "0.5"
    assert summary["data_quality"]["pricing_coverage"] == "0.5"
    assert summary["data_quality"]["unknown_usage_count"] == 1
    assert summary["data_quality"]["usage_unknown_attempt_count"] == 1
    assert summary["data_quality"]["unknown_pricing_count"] == 1
    assert summary["data_quality"]["usage_value_unknown_attempt_count"] == 1


def test_metrics_reconcile_mismatched_start_and_finish_attempt_identities() -> None:
    shared = {
        "job_id": "job",
        "run_attempt_id": "run",
        "call_id": "call",
        "chapter_id": "1",
        "unit_id": "u1",
        "stage": "phase4",
        "node": "digest",
    }
    summary = aggregate_observation_metrics(
        [
            {
                **shared,
                "event_id": "started-a",
                "event_kind": "llm_provider_attempt_started",
                "attempt_id": "attempt-a",
            },
            {
                **shared,
                "event_id": "finished-b",
                "event_kind": "llm_provider_attempt_finished",
                "attempt_id": "attempt-b",
                "usage": {"status": "complete", "input_tokens": 10, "output_tokens": 2},
                "cost": {"estimated_usage_value_usd": "0.001"},
            },
            {
                **shared,
                "event_id": "logical-call",
                "event_kind": "llm_logical_call_finished",
                "attempt_count": 1,
                "status": "ok",
            },
        ]
    )

    assert summary["expected_physical_attempt_count"] == 2
    assert summary["accounted_physical_attempt_count"] == 2
    assert summary["observed_physical_attempt_count"] == 1
    assert summary["missing_physical_attempt_count"] == 1
    assert summary["data_quality"]["started_without_finish_count"] == 1
    assert summary["data_quality"]["finished_without_start_count"] == 1
    assert summary["data_quality"]["usage_coverage"] == "0.5"
    assert summary["data_quality"]["pricing_coverage"] == "0.5"
    assert summary["data_quality"]["chapter_correlation_coverage"] == "1"
    assert summary["data_quality"]["stage_appropriate_correlation_coverage"] == "1"
    assert summary["data_quality"]["uncorrelated_attempt_count"] == 0


def test_invalid_usage_is_not_included_in_token_or_efficiency_totals() -> None:
    summary = aggregate_observation_metrics(
        [
            {
                "event_id": "invalid-attempt",
                "event_kind": "llm_provider_attempt_finished",
                "call_id": "call",
                "attempt_id": "attempt",
                "status": "ok",
                "chapter_id": "1",
                "unit_id": "u1",
                "usage": {
                    "status": "invalid",
                    "input_tokens": 10,
                    "output_tokens": 2,
                    "total_tokens": 5,
                },
                "cost": {"status": "usage_invalid"},
            },
            {
                "event_id": "logical-call",
                "event_kind": "llm_logical_call_finished",
                "call_id": "call",
                "attempt_count": 1,
                "status": "ok",
                "chapter_id": "1",
                "unit_id": "u1",
            },
            {
                "event_id": "unit",
                "event_kind": "unit_settled",
                "status": "accepted",
                "chapter_id": "1",
                "unit_id": "u1",
                "source_char_count": 10_000,
            },
        ]
    )

    assert summary["usage_invalid_count"] == 1
    assert summary["input_tokens"] is None
    assert summary["output_tokens"] is None
    assert summary["total_tokens"] is None
    assert summary["total_tokens_per_10000_chars"] is None
    assert summary["data_quality"]["usage_coverage"] == "0"


def test_model_and_target_breakdowns_do_not_double_count_failover_claims() -> None:
    shared = {
        "job_id": "job",
        "run_attempt_id": "run",
        "call_id": "call",
        "chapter_id": "1",
        "stage": "phase4",
        "node": "digest",
    }
    events: list[dict[str, object]] = []
    for index, (target, model, status) in enumerate(
        (("target-a", "model-a", "error"), ("target-b", "model-b", "ok")),
        start=1,
    ):
        attempt_id = f"attempt-{index}"
        physical = {
            **shared,
            "attempt_id": attempt_id,
            "attempt_index": index,
            "target_id": target,
            "model": model,
        }
        events.extend(
            [
                {
                    **physical,
                    "event_id": f"start-{index}",
                    "event_kind": "llm_provider_attempt_started",
                },
                {
                    **physical,
                    "event_id": f"finish-{index}",
                    "event_kind": "llm_provider_attempt_finished",
                    "status": status,
                    "usage": {"status": "complete", "input_tokens": 1, "output_tokens": 1},
                    "cost": {"estimated_usage_value_usd": "0.001"},
                },
            ]
        )
    events.append(
        {
            **shared,
            "event_id": "logical-call",
            "event_kind": "llm_logical_call_finished",
            "attempt_count": 2,
            "status": "ok",
            "target_id": "target-b",
            "model": "model-b",
        }
    )

    summary = aggregate_observation_metrics(events)

    assert summary["expected_physical_attempt_count"] == 2
    assert summary["observed_physical_attempt_count"] == 2
    assert sum(
        bucket["expected_physical_attempt_count"]
        for bucket in summary["by_target"].values()
    ) == 2
    assert summary["by_target"]["target-a"]["expected_physical_attempt_count"] == 1
    assert summary["by_target"]["target-b"]["expected_physical_attempt_count"] == 1
    assert summary["by_target"]["target-a"]["retry_count"] == 0
    assert summary["by_target"]["target-b"]["retry_count"] == 0
    assert summary["by_model"]["model-a"]["missing_physical_attempt_count"] == 0
    assert summary["by_model"]["model-b"]["missing_physical_attempt_count"] == 0


def test_metrics_treat_started_without_finish_as_unknown_possible_usage() -> None:
    summary = aggregate_observation_metrics(
        [
            {
                "event_id": "started-1",
                "event_kind": "llm_provider_attempt_started",
                "job_id": "job",
                "run_attempt_id": "run",
                "call_id": "call",
                "attempt_id": "attempt",
                "attempt_index": 1,
                "chapter_id": "1",
                "reading_cycle_id": "cycle",
                "unit_id": "u1",
                "stage": "phase4",
                "node": "digest",
            }
        ]
    )

    assert summary["started_physical_attempt_count"] == 1
    assert summary["observed_physical_attempt_count"] == 0
    assert summary["expected_physical_attempt_count"] == 1
    assert summary["missing_physical_attempt_count"] == 1
    assert summary["data_quality"]["started_without_finish_count"] == 1
    assert summary["data_quality"]["provider_attempt_finish_coverage"] == "0"
    assert summary["data_quality"]["usage_coverage"] == "0"
    assert summary["data_quality"]["pricing_coverage"] == "0"
    assert summary["data_quality"]["stage_appropriate_correlation_coverage"] == "1"


def test_metrics_join_ingest_cycle_to_selected_unit_and_exclude_chapter_only_parse() -> None:
    shared = {
        "job_id": "job",
        "run_attempt_id": "run",
        "chapter_id": "1",
    }
    events = [
        {
            **shared,
            "event_id": "ingest-attempt",
            "event_kind": "llm_provider_attempt_finished",
            "call_id": "ingest",
            "reading_cycle_id": "cycle",
            "stage": "read",
            "node": "ingest",
            "usage": {"status": "complete"},
            "cost": {"estimated_usage_value_usd": "0.001"},
        },
        {
            **shared,
            "event_id": "ingest-call",
            "event_kind": "llm_logical_call_finished",
            "call_id": "ingest",
            "reading_cycle_id": "cycle",
            "stage": "read",
            "node": "ingest",
            "attempt_count": 1,
        },
        {
            **shared,
            "event_id": "selected",
            "event_kind": "unit_selected",
            "reading_cycle_id": "cycle",
            "unit_id": "u000001",
            "unit_index": 1,
            "source_char_count": 100,
        },
        {
            **shared,
            "event_id": "parse-attempt",
            "event_kind": "llm_provider_attempt_finished",
            "call_id": "parse",
            "stage": "parse",
            "node": "semantic_segmentation",
            "usage": {"status": "complete"},
            "cost": {"estimated_usage_value_usd": "0.001"},
        },
        {
            **shared,
            "event_id": "parse-call",
            "event_kind": "llm_logical_call_finished",
            "call_id": "parse",
            "stage": "parse",
            "node": "semantic_segmentation",
            "attempt_count": 1,
        },
    ]

    summary = aggregate_observation_metrics(events)

    assert summary["data_quality"]["stage_appropriate_correlation_coverage"] == "1"
    assert summary["data_quality"]["chapter_correlation_coverage"] == "1"
    assert summary["data_quality"]["unit_correlation_coverage"] == "1"
    assert summary["data_quality"]["unit_scope_eligible_attempt_count"] == 1
    assert summary["data_quality"]["chapter_only_attempt_count"] == 1
    assert summary["by_unit"]["1/u000001"]["attempt_count"] == 1


def test_failed_preselection_ingest_is_cycle_correlated_without_inventing_a_unit() -> None:
    events = [
        {
            "event_id": "ingest-attempt",
            "event_kind": "llm_provider_attempt_finished",
            "job_id": "job",
            "run_attempt_id": "run",
            "call_id": "ingest",
            "chapter_id": "1",
            "reading_cycle_id": "cycle-without-selection",
            "stage": "phase4",
            "node": "ingest",
            "status": "error",
            "usage": {"status": "unavailable"},
            "cost": {"status": "usage_incomplete"},
        },
        {
            "event_id": "ingest-call",
            "event_kind": "llm_logical_call_finished",
            "job_id": "job",
            "run_attempt_id": "run",
            "call_id": "ingest",
            "chapter_id": "1",
            "reading_cycle_id": "cycle-without-selection",
            "stage": "phase4",
            "node": "ingest",
            "attempt_count": 1,
            "status": "error",
        },
    ]

    summary = aggregate_observation_metrics(events)

    assert summary["data_quality"]["stage_appropriate_correlation_coverage"] == "1"
    assert summary["data_quality"]["chapter_correlation_coverage"] == "1"
    assert summary["data_quality"]["unit_correlation_coverage"] is None
    assert summary["data_quality"]["unit_scope_eligible_attempt_count"] == 0
    assert summary["data_quality"]["non_unit_eligible_attempt_count"] == 1


def test_transient_ledger_failure_is_persisted_after_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = observation_ledger_file(tmp_path / "book", "job")
    original_open = os.open
    failed_once = False

    def flaky_open(path, flags, mode=0o777):
        nonlocal failed_once
        if Path(path) == ledger and not failed_once:
            failed_once = True
            raise OSError("transient ledger failure")
        return original_open(path, flags, mode)

    monkeypatch.setattr(os, "open", flaky_open)
    failed = append_observation_event(
        ledger,
        {"event_kind": "first", "job_id": "job", "run_attempt_id": "run"},
    )
    recovered = append_observation_event(
        ledger,
        {"event_kind": "second", "job_id": "job", "run_attempt_id": "run"},
    )

    events, malformed = load_observation_events(ledger)
    assert failed.written is False
    assert recovered.written is True
    assert malformed == 0
    assert [event["event_kind"] for event in events] == ["ledger_write_failed", "second"]
    assert events[0]["failure_count"] == 1
    assert aggregate_observation_metrics(events)["data_quality"][
        "ledger_write_failure_count"
    ] == 1


def test_partial_ledger_write_is_rolled_back_before_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = observation_ledger_file(tmp_path / "book", "job-partial")
    original_write_all = observation_ledger_module._write_all
    failed_once = False

    def partial_then_fail(descriptor: int, encoded: bytes) -> None:
        nonlocal failed_once
        if not failed_once:
            failed_once = True
            prefix_size = max(1, len(encoded) // 2)
            os.write(descriptor, encoded[:prefix_size])
            raise OSError("simulated failure after a short write")
        original_write_all(descriptor, encoded)

    monkeypatch.setattr(observation_ledger_module, "_write_all", partial_then_fail)
    first = append_observation_event(
        ledger,
        {"event_kind": "first", "job_id": "job-partial", "run_attempt_id": "run"},
    )
    second = append_observation_event(
        ledger,
        {"event_kind": "second", "job_id": "job-partial", "run_attempt_id": "run"},
    )

    events, malformed = load_observation_events(ledger)
    assert first.written is False
    assert second.written is True
    assert malformed == 0
    assert [event["event_kind"] for event in events] == ["ledger_write_failed", "second"]
    assert events[0]["failure_count"] == 1


def test_scopes_create_run_chapter_and_unit_chain_spans(tmp_path: Path, monkeypatch) -> None:
    span_names: list[str] = []

    @contextlib.contextmanager
    def fake_telemetry_span(name: str, *, span_kind: str, attributes):
        span_names.append(name)
        index = len(span_names)
        assert span_kind == "CHAIN"
        yield TelemetrySpan(trace_id="a" * 32, span_id=f"{index:016x}")

    monkeypatch.setattr(observation_context_module, "telemetry_span", fake_telemetry_span)
    with run_observation_scope(tmp_path / "book", "job", job_kind="sequential"):
        assert current_observation_context().trace_id == "a" * 32
        with chapter_observation_scope("chapter"):
            assert current_observation_context().parent_span_id == "0000000000000001"
            with reading_cycle_scope("cycle") as cycle:
                cycle.select_unit("unit", 10, 0)
                assert current_observation_context().parent_span_id == "0000000000000002"
    assert span_names == ["reading.run_attempt", "reading.chapter", "reading.unit_attempt"]


def test_nested_scopes_are_noop_without_product_run_context(tmp_path: Path, monkeypatch) -> None:
    span_names: list[str] = []

    @contextlib.contextmanager
    def fake_telemetry_span(name: str, *, span_kind: str, attributes):
        span_names.append(name)
        yield TelemetrySpan()

    monkeypatch.setattr(observation_context_module, "telemetry_span", fake_telemetry_span)
    with chapter_observation_scope("eval-chapter"):
        with reading_cycle_scope("eval-cycle") as cycle:
            cycle.select_unit("eval-unit", 10, 1)
            cycle.settle("accepted")
            assert current_observation_context() is None

    assert span_names == []
    assert not (tmp_path / "events.jsonl").exists()


def test_async_unit_scopes_isolate_context_and_recovery_attempt_ids(tmp_path: Path) -> None:
    output_dir = tmp_path / "output" / "book-async"

    async def _run_units() -> list[tuple[str | None, str | None]]:
        async def _unit(index: int) -> tuple[str | None, str | None]:
            with reading_cycle_scope(f"cycle-{index}") as cycle:
                cycle.select_unit(f"unit-{index}", index * 10, index)
                await asyncio.sleep(0)
                context = current_observation_context()
                cycle.settle("accepted")
                return context.reading_cycle_id, context.unit_id

        return list(await asyncio.gather(_unit(1), _unit(2)))

    with run_observation_scope(output_dir, "job-async", run_attempt_id="attempt-a"):
        with chapter_observation_scope("chapter-a"):
            assert asyncio.run(_run_units()) == [
                ("cycle-1", "unit-1"),
                ("cycle-2", "unit-2"),
            ]
            assert current_observation_context().unit_id is None

    with run_observation_scope(output_dir, "job-async", run_attempt_id="attempt-b"):
        pass

    events, malformed = load_observation_events(observation_ledger_file(output_dir, "job-async"))
    assert malformed == 0
    run_starts = [event for event in events if event["event_kind"] == "run_attempt_started"]
    assert {event["run_attempt_id"] for event in run_starts} == {"attempt-a", "attempt-b"}
    assert len({event["event_id"] for event in run_starts}) == 2
