"""Run metadata remains useful on success/failure without leaking provider secrets."""

import json
import socket
from types import SimpleNamespace

import pytest

from src.attentional_v2.observability import run_configuration_scope
from src.attentional_v2.storage import runtime_dir, event_stream_file
from src.reading_runtime.llm_gateway import _sampling_record, clear_llm_gateway_runtime_state
from src.reading_runtime.llm_registry import clear_llm_registry_cache
from tests.cleanup_probe import product_probe


def test_offline_eval_configuration_links_real_gateway_plan_and_retrieval(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("configuration evidence forbids networking")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    try:
        result = product_probe(tmp_path, monkeypatch, evaluation=True)
    finally:
        clear_llm_gateway_runtime_state()
        clear_llm_registry_cache()
    config = result["run_configuration"]
    assert len(config["code_commit"]) == 40
    assert isinstance(config["code_dirty"], bool)
    assert len(config["chapter_plan_fingerprint"]) == 64
    assert len(config["classification_calls"]) == 2
    assert {row["node"] for row in config["model_calls"]} == {"ingest", "digest"}
    for row in config["model_calls"] + config["classification_calls"]:
        assert row["provider_id"] == "cpa_codex_local"
        assert row["model"] == "gpt-5.6-luna"
        assert row["sampling"]["temperature"] == 0.2
        assert row["prompt_version"] == config["prompt_versions"][row["node"]]
        assert row["code_commit"] == config["code_commit"]
    assert config["retrieval"]["mode"] == "text_only"
    assert config["retrieval"]["strict_retrieval"] is True
    assert config["retrieval"]["query_degradation_count"] == 0
    assert config["retrieval"]["ollama_model_id"] == "qwen3-embedding:0.6b"


def test_failed_invocation_keeps_configuration_receipt(tmp_path):
    with pytest.raises(RuntimeError, match="fixture failure"):
        with run_configuration_scope(tmp_path, stage="read"):
            raise RuntimeError("fixture failure")
    config = json.loads((runtime_dir(tmp_path) / "run_configuration.json").read_text())
    assert config["status"] == "failed"
    assert len(config["code_commit"]) == 40
    events = [json.loads(line) for line in event_stream_file(tmp_path).read_text().splitlines()]
    assert events[-1]["event_type"] == "run_configuration"
    assert events[-1]["status"] == "failed"


def test_sampling_receipt_records_overrides_without_arbitrary_options():
    provider = SimpleNamespace(provider_options={"top_p": 0.9, "extra_body": {"reasoning_effort": "medium", "api_key": "test-only-sentinel"}})
    profile = SimpleNamespace(temperature=0.2, max_output_tokens=4096, provider_options={"top_p": 0.8})
    result = _sampling_record(provider, profile, {"seed": 17, "extra_headers": {"Authorization": "test-only-sentinel"}})
    assert result == {"temperature": 0.2, "max_output_tokens": 4096, "top_p": 0.8, "seed": 17, "reasoning_effort": "medium"}
    assert "sentinel" not in json.dumps(result)
