"""Deterministic product-path acceptance test for runtime observability."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.attentional_v2.evaluation import normalized_eval_bundle_file
from src.attentional_v2.storage import ATTENTIONAL_V2_MECHANISM_KEY
from src.attentional_v2 import runner as runner_module
from src.reading_core.runtime_contracts import ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_runtime.llm_gateway import CONTRACT_ADAPTERS, clear_llm_gateway_runtime_state
from src.reading_runtime.llm_registry import (
    DEFAULT_DATASET_REVIEW_PROFILE_ID,
    DEFAULT_EVAL_JUDGE_PROFILE_ID,
    DEFAULT_RUNTIME_PROFILE_ID,
    clear_llm_registry_cache,
)
from src.reading_runtime.provisioning import ProvisionedBook


def _fixture_epub() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "e2e_runtime" / "sample-upload.epub"


def _provisioned_fixture_book() -> ProvisionedBook:
    book_document = {
        "metadata": {
            "book": "Observability Fixture",
            "author": "Test Suite",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Alpha sentence. Beta sentence.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:30",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Alpha sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 15,
                        },
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Beta sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 16,
                            "char_end": 30,
                        },
                    },
                ],
            }
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Observability Fixture",
        author="Test Suite",
        book_language="en",
        output_language="en",
        output_dir=Path("output/observability-fixture"),
        raw_chapters=None,
        book_document=book_document,
    )


@dataclass
class _UsageResponse:
    content: str
    usage_metadata: dict[str, Any]
    response_metadata: dict[str, Any]


class _DeterministicReadingAdapter:
    """Return deterministic valid outputs for every model node in the product read."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def invoke(
        self,
        messages: list[Any],
        *,
        provider: Any,
        profile: Any,
        api_key: str,
        timeout_seconds: int,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        invocation_options: dict[str, Any] | None = None,
    ) -> _UsageResponse:
        message_blob = "\n".join(str(getattr(message, "content", "")) for message in messages)
        del messages, api_key, timeout_seconds, tool_choice, invocation_options
        contract_blob = json.dumps(tools or (), ensure_ascii=False) + message_blob
        if "submit_survey_chapter_zone_result" in contract_blob:
            node = "survey"
        elif "submit_ingest_result" in contract_blob:
            node = "ingest"
        elif "submit_chapter_consolidation_result" in contract_blob:
            node = "chapter_consolidation"
        else:
            node = "digest"
        self.calls.append(
            {
                "node": node,
                "provider_id": provider.provider_id,
                "model": profile.model,
            }
        )
        if node == "survey":
            payload = {
                "zone": "main_body",
                "confidence": "high",
                "reason": "The fixture chapter contains the book's main prose.",
            }
        elif node == "ingest":
            payload: dict[str, Any] = {
                "unit": {"end_paragraph_n": "1", "end_at": "Beta sentence."},
                "preview_partition": [
                    {
                        "title": "Fixture paragraph",
                        "end_paragraph_n": "1",
                        "end_at": "Beta sentence.",
                        "status": "complete",
                    }
                ],
                "reason": "Read the complete compact fixture paragraph.",
            }
        elif node == "digest":
            payload = {
                "understanding": "Alpha develops into Beta as one compact progression.",
                "response": "The second sentence completes the first sentence's movement.",
                "marginalia": [],
            }
        else:
            payload = {
                "chapter_ref": "Chapter 1",
                "backward_sweep": [],
                "cooling_operations": [],
                "promotion_candidates": [],
                "knowledge_activation_updates": [],
                "cross_chapter_carry_forward": [],
                "chapter_summary_note": "The fixture chapter is complete.",
            }
        return _UsageResponse(
            content=json.dumps(payload),
            usage_metadata={
                "input_tokens": 1_000,
                "output_tokens": 100,
                "total_tokens": 1_100,
                "input_token_details": {"cache_read": 200},
                "output_token_details": {"reasoning": 20},
            },
            response_metadata={"model_provider": "openai", "finish_reason": "stop"},
        )


def _configure_priced_runtime_target(monkeypatch) -> None:
    target_id = "opencode_deepseek_v4_flash"
    monkeypatch.setenv(
        "LLM_TARGETS_JSON",
        json.dumps(
            {
                "targets": [
                    {
                        "target_id": target_id,
                        "contract": "openai_compatible",
                        "base_url": "https://opencode.ai/zen/go/v1",
                        "model": "deepseek-v4-flash",
                        "credentials": [{"credential_id": "test", "api_key": "not-sent"}],
                        "provider_options": {
                            "response_format": {"type": "json_object"},
                            "thinking": {"type": "enabled"},
                        },
                    }
                ]
            }
        ),
    )
    monkeypatch.setenv(
        "LLM_PROFILE_BINDINGS_JSON",
        json.dumps(
            {
                "profiles": [
                    {"profile_id": profile_id, "target_id": target_id}
                    for profile_id in (
                        DEFAULT_RUNTIME_PROFILE_ID,
                        DEFAULT_DATASET_REVIEW_PROFILE_ID,
                        DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    )
                ]
            }
        ),
    )
    monkeypatch.setenv("READING_OBSERVABILITY_OTLP_ENABLED", "0")
    clear_llm_registry_cache()
    clear_llm_gateway_runtime_state()


def test_product_read_emits_recomputable_cost_and_efficiency_observability(tmp_path, monkeypatch) -> None:
    """A normal product read should produce a complete, priced observation chain."""

    monkeypatch.chdir(tmp_path)
    _configure_priced_runtime_target(monkeypatch)
    monkeypatch.setattr(
        runner_module,
        "ensure_canonical_parse",
        lambda *args, **kwargs: _provisioned_fixture_book(),
    )
    adapter = _DeterministicReadingAdapter()
    monkeypatch.setitem(CONTRACT_ADAPTERS, "openai_compatible", adapter)

    try:
        result = AttentionalV2Mechanism().read_book(
            ReadRequest(
                book_path=_fixture_epub(),
                mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
                mechanism_config={},
            )
        )
    finally:
        clear_llm_gateway_runtime_state()
        clear_llm_registry_cache()

    observability_dirs = list((result.output_dir / "_history" / "runs").glob("*/observability"))
    assert len(observability_dirs) == 1
    observability_dir = observability_dirs[0]
    ledger_path = observability_dir / "events.jsonl"
    metrics_path = observability_dir / "metrics.json"
    report_path = observability_dir / "report.md"
    data_quality_path = observability_dir / "data_quality.json"
    assert all(
        path.is_file()
        for path in (ledger_path, metrics_path, report_path, data_quality_path)
    )

    events = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    event_kinds = [event["event_kind"] for event in events]
    assert event_kinds.count("llm_logical_call_finished") == 4
    assert event_kinds.count("llm_provider_attempt_started") == 4
    assert event_kinds.count("llm_provider_attempt_finished") == 4
    assert "unit_selected" in event_kinds
    assert "unit_settled" in event_kinds
    assert [call["node"] for call in adapter.calls] == [
        "survey",
        "ingest",
        "digest",
        "chapter_consolidation",
    ]

    attempts = [
        event for event in events if event["event_kind"] == "llm_provider_attempt_finished"
    ]
    attempt_starts = [
        event for event in events if event["event_kind"] == "llm_provider_attempt_started"
    ]
    assert {event["attempt_id"] for event in attempt_starts} == {
        event["attempt_id"] for event in attempts
    }
    assert all(event["usage_status"] == "complete" for event in attempts)
    assert all(event["pricing"]["target_id"] == "opencode_deepseek_v4_flash" for event in attempts)
    assert all(event["pricing"]["model"] == "deepseek-v4-flash" for event in attempts)
    assert all(event["cost"]["estimated_usage_value_usd"] == "0.00014056" for event in attempts)
    assert all(event["cost"]["actual_billed_cost"] is None for event in attempts)
    assert all(event.get("chapter_id") == "1" for event in attempts)
    assert {event.get("job_id") for event in attempts} == {events[0]["job_id"]}
    assert {event.get("run_attempt_id") for event in attempts} == {events[0]["run_attempt_id"]}
    assert {event.get("stage") for event in attempts} == {"survey", "phase4", "phase6"}
    assert {event.get("node") for event in attempts} == {
        "chapter_zone_classifier",
        "ingest",
        "digest",
        "chapter_consolidation",
    }
    selected = next(event for event in events if event["event_kind"] == "unit_selected")
    phase4_attempts = [event for event in attempts if event.get("stage") == "phase4"]
    assert all(
        event.get("reading_cycle_id") == selected["reading_cycle_id"]
        for event in phase4_attempts
    )
    assert next(event for event in attempts if event["node"] == "ingest").get("unit_id") is None
    assert next(event for event in attempts if event["node"] == "digest")["unit_id"] == selected["unit_id"]

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    quality = json.loads(data_quality_path.read_text(encoding="utf-8"))
    assert metrics["accepted_source_chars"] == len("Alpha sentence. Beta sentence.")
    assert metrics["accepted_unit_count"] == 1
    assert metrics["call_count"] == 4
    assert metrics["expected_physical_attempt_count"] == 4
    assert metrics["observed_physical_attempt_count"] == 4
    assert metrics["total_tokens"] == "4400"
    assert metrics["estimated_usage_value_usd"] == "0.00056224"
    assert metrics["by_stage"]["survey"]["attempt_count"] == 1
    assert metrics["by_stage"]["phase4"]["attempt_count"] == 2
    assert metrics["by_stage"]["phase4"]["accepted_source_chars"] == 30
    assert metrics["by_stage"]["phase4"]["total_tokens_per_10000_chars"] is not None
    assert metrics["by_stage"]["phase6"]["attempt_count"] == 1
    assert metrics["by_chapter"]["1"]["accepted_source_chars"] == 30
    assert metrics["by_unit"]["1/u000001"]["attempt_count"] == 2
    assert metrics["by_unit"]["1/unavailable"]["attempt_count"] == 2
    assert quality["usage_coverage"] == "1"
    assert quality["pricing_coverage"] == "1"
    assert quality["chapter_correlation_coverage"] == "1"
    assert quality["unit_correlation_coverage"] == "1"
    assert quality["stage_appropriate_correlation_coverage"] == "1"
    assert "Estimated usage value (USD): 0.00056224" in report_path.read_text(encoding="utf-8")
    assert not normalized_eval_bundle_file(result.output_dir).exists()
