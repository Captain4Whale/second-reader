"""Offline guards for the approved one-request whole-book Digest experiment."""

from __future__ import annotations

import copy
import json
import socket
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from eval.attentional_v2 import run_whole_book_digest as runner


def _configs():
    return (
        {
            "targets": [
                {
                    "target_id": runner.TARGET_ID,
                    "contract": "openai_compatible",
                    "base_url": "http://127.0.0.1:1/v1",
                    "model": runner.MODEL,
                    "provider_options": {"reasoning_effort": "medium"},
                    "credentials": [
                        {"credential_id": "test", "api_key_env": "WHOLE_BOOK_TEST_KEY"}
                    ],
                    "retry_attempts": 8,
                }
            ]
        },
        {
            "profiles": [
                {
                    "profile_id": runner.PROFILE_ID,
                    "target_tiers": [
                        {"tier_id": "primary", "target_ids": [runner.TARGET_ID]}
                    ],
                    "retry_attempts": 8,
                    "quota_retry_attempts": 4,
                    "max_output_tokens": 4096,
                }
            ]
        },
    )


def _approved_kwargs():
    return {
        "provider": SimpleNamespace(provider_id=runner.TARGET_ID),
        "profile": SimpleNamespace(
            model=runner.MODEL,
            max_output_tokens=65536,
            temperature=0.2,
            retry_attempts=1,
            quota_retry_attempts=0,
        ),
        "timeout_seconds": 1800,
        "invocation_options": {"reasoning_effort": "medium"},
        "api_key": "test-only-secret-must-not-be-persisted",
    }


class RecordingAdapter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def invoke(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        if self.error:
            raise self.error
        return self.response


def _payload():
    return {
        "understanding": "他仍在寻找自己的道路。",
        "response": "这段话将寻找与亲身体验联系起来。",
        "marginalia": [
            {
                "kind": "note",
                "source_quote": "他仍在寻找。",
                "content": "寻找尚未结束。",
            }
        ],
    }


def _response(finish="tool_calls", *, invalid=False):
    raw_args = (
        '{"understanding":' if invalid else json.dumps(_payload(), ensure_ascii=False)
    )
    return AIMessage(
        content="",
        additional_kwargs={
            "tool_calls": [
                {
                    "id": "digest-1",
                    "type": "function",
                    "function": {
                        "name": runner.DIGEST_RESULT_TOOL["name"],
                        "arguments": raw_args,
                    },
                }
            ]
        },
        response_metadata={"finish_reason": finish, "model_name": runner.MODEL},
        usage_metadata={"input_tokens": 111, "output_tokens": 22, "total_tokens": 133},
    )


def test_isolated_config_freezes_budget_without_mutating_inputs():
    targets, bindings = _configs()
    originals = copy.deepcopy((targets, bindings))
    isolated_targets, isolated_bindings = runner.isolated_config(targets, bindings)
    assert (targets, bindings) == originals
    assert [t["target_id"] for t in isolated_targets["targets"]] == [runner.TARGET_ID]
    target = isolated_targets["targets"][0]
    assert target["retry_attempts"] == 1
    assert target["timeout_seconds"] == 1800
    profile = next(
        p for p in isolated_bindings["profiles"] if p["profile_id"] == runner.PROFILE_ID
    )
    assert profile["max_output_tokens"] == 65536
    assert profile["temperature"] == 0.2
    assert profile["retry_attempts"] == 1
    assert profile["quota_retry_attempts"] == 0
    assert profile["quota_wait_budget_seconds"] == 0
    assert profile["target_tiers"] == [
        {
            "tier_id": "primary",
            "target_ids": [runner.TARGET_ID],
            "min_required_stable_concurrency": 1,
        }
    ]


@pytest.mark.parametrize("change", ["model", "reasoning_effort", "inline_credential"])
def test_isolated_config_rejects_unapproved_target(change):
    targets, bindings = _configs()
    target = targets["targets"][0]
    if change == "model":
        target["model"] = "another-model"
    elif change == "reasoning_effort":
        target["provider_options"]["reasoning_effort"] = "high"
    else:
        target["credentials"][0]["api_key"] = "inline-secret"
    with pytest.raises(ValueError):
        runner.isolated_config(targets, bindings)


@pytest.mark.parametrize("failed", [False, True])
def test_single_request_adapter_refuses_second_delegate_call_even_after_failure(
    tmp_path, failed
):
    delegate = RecordingAdapter(
        response="result", error=TimeoutError("timed out") if failed else None
    )
    adapter = runner.SingleRequestAdapter(delegate, tmp_path)
    messages = [HumanMessage(content="完整正文")]
    if failed:
        with pytest.raises(TimeoutError):
            adapter.invoke(messages, **_approved_kwargs())
    else:
        assert adapter.invoke(messages, **_approved_kwargs()) == "result"
    with pytest.raises(RuntimeError, match="Second application request refused"):
        adapter.invoke(messages, **_approved_kwargs())
    assert len(delegate.calls) == adapter.count == 1
    request_text = (tmp_path / "request.json").read_text()
    assert "test-only-secret" not in request_text
    assert json.loads(request_text)["messages"] == [
        {"role": "human", "content": "完整正文"}
    ]


def test_single_request_adapter_rejects_effective_budget_drift_before_call(tmp_path):
    delegate = RecordingAdapter()
    adapter = runner.SingleRequestAdapter(delegate, tmp_path)
    kwargs = _approved_kwargs()
    kwargs["profile"].max_output_tokens = 4096
    with pytest.raises(ValueError, match="approved model/budget"):
        adapter.invoke([], **kwargs)
    assert delegate.calls == []
    assert adapter.count == 0
    assert not (tmp_path / "request.json").exists()


def test_reservation_survives_reentry_and_preserves_original_marker(tmp_path):
    runner.reserve_request(tmp_path)
    marker = (tmp_path / "request.started.json").read_bytes()
    with pytest.raises(FileExistsError):
        runner.reserve_request(tmp_path)
    assert (tmp_path / "request.started.json").read_bytes() == marker


def test_normal_response_omits_private_reasoning_and_preserves_raw_tool_arguments_and_usage():
    response = _response()
    response.content = [
        {"type": "reasoning", "text": "private-thought"},
        {"type": "thinking", "thinking": "private-thought"},
        {"type": "text", "text": "正常输出"},
    ]
    response.additional_kwargs["reasoning_content"] = "private-thought"
    response.response_metadata["reasoning"] = "private-thought"
    raw = runner.normal_response(response)
    assert "private-thought" not in json.dumps(raw)
    assert raw["content"] == [{"type": "text", "text": "正常输出"}]
    assert raw["raw_tool_calls"] == response.additional_kwargs["tool_calls"]
    assert raw["tool_calls"][0]["args"] == _payload()
    assert raw["usage_metadata"] == response.usage_metadata


@pytest.mark.parametrize("finish, invalid", [("length", False), ("tool_calls", True)])
def test_incomplete_response_is_rejected_without_modifying_raw_evidence(
    finish, invalid
):
    raw = runner.normal_response(_response(finish, invalid=invalid))
    before = copy.deepcopy(raw)
    payload, errors = runner.interpret_response(raw, {"source_text": "他仍在寻找。"})
    assert raw == before
    assert errors
    if invalid:
        assert payload is None
        assert any("unparseable" in error for error in errors)
        assert raw["raw_tool_calls"][0]["function"]["arguments"] == '{"understanding":'
    else:
        assert payload == _payload()
        assert any("finish reason: length" in error for error in errors)


def _freeze_small_run(run_dir):
    targets, bindings = runner.isolated_config(*_configs())
    source = {
        "source_text": "他仍在寻找。",
        "paragraphs": [
            {
                "chapter_id": 1,
                "chapter_title": "第一章",
                "paragraph_index": 0,
                "start": 0,
                "end": 6,
                "text": "他仍在寻找。",
            }
        ],
    }
    for name, value in {
        "source.json": source,
        "targets.local.json": targets,
        "bindings.local.json": bindings,
        "prompt.json": {
            "system_prompt": "阅读者",
            "user_prompt": "他仍在寻找。",
            "output_tool": runner.DIGEST_RESULT_TOOL,
        },
    }.items():
        runner.write_json(run_dir / name, value)
    runner.write_json(
        run_dir / "manifest.json",
        {
            "source_sha256": runner.SOURCE_HASH,
            "application_request_limit": 1,
            "artifact_hashes": {
                name: runner.digest_bytes((run_dir / name).read_bytes())
                for name in (
                    "source.json",
                    "targets.local.json",
                    "bindings.local.json",
                    "prompt.json",
                )
            },
        },
    )


def test_frozen_input_change_is_rejected_before_request_reservation(tmp_path):
    _freeze_small_run(tmp_path)
    runner.verify_prepared(tmp_path)
    (tmp_path / "prompt.json").write_text('{"modified":true}')
    with pytest.raises(ValueError, match="Frozen artifact changed: prompt.json"):
        runner.run(tmp_path)
    assert not (tmp_path / "request.started.json").exists()


@pytest.fixture
def isolated_gateway(tmp_path, monkeypatch):
    # Never let this suite contact a provider or touch the real shared cooldown files.
    def deny_network(*args, **kwargs):
        raise AssertionError("Network access forbidden in offline experiment tests")

    monkeypatch.setattr(socket.socket, "connect", deny_network)
    monkeypatch.setattr(socket, "create_connection", deny_network)
    for key in (
        "LLM_TARGETS_JSON",
        "LLM_PROFILE_BINDINGS_JSON",
        "LLM_REGISTRY_JSON",
        "LLM_REGISTRY_PATH",
        "LLM_FORCE_TARGET_ID",
        "LLM_FORCE_TIER_ID",
    ):
        monkeypatch.delenv(key, raising=False)
    # run() sets these itself; register their previous values for fixture restoration.
    monkeypatch.setenv("LLM_TARGETS_PATH", str(tmp_path / "targets.local.json"))
    monkeypatch.setenv(
        "LLM_PROFILE_BINDINGS_PATH", str(tmp_path / "bindings.local.json")
    )
    monkeypatch.setenv("WHOLE_BOOK_TEST_KEY", "fake-key-for-offline-test")
    monkeypatch.setenv("BACKEND_RUNTIME_ROOT", str(tmp_path))
    runner.gateway.clear_llm_gateway_runtime_state()
    runner.clear_llm_registry_cache()
    yield
    runner.gateway.clear_llm_gateway_runtime_state()
    runner.clear_llm_registry_cache()


@pytest.mark.parametrize(
    "outcome", ["complete", "truncated", "invalid_args", "timeout"]
)
def test_real_gateway_keeps_one_attempt_and_terminal_evidence(
    tmp_path, monkeypatch, isolated_gateway, outcome
):
    _freeze_small_run(tmp_path)
    delegate = RecordingAdapter(
        response=_response(
            "length" if outcome == "truncated" else "tool_calls",
            invalid=outcome == "invalid_args",
        ),
        error=TimeoutError("timed out") if outcome == "timeout" else None,
    )
    monkeypatch.setitem(runner.gateway.CONTRACT_ADAPTERS, "openai_compatible", delegate)
    summary = runner.run(tmp_path)
    assert len(delegate.calls) == summary["application_request_count"] == 1
    assert summary["status"] == (
        "review_pending" if outcome == "complete" else "failed"
    )
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "review.md").exists()
    assert runner.gateway.CONTRACT_ADAPTERS["openai_compatible"] is delegate
    request = runner.read_json(tmp_path / "request.json")
    assert request["max_output_tokens"] == 65536
    assert request["messages"][-1]["content"] == "他仍在寻找。"
    if outcome != "timeout":
        raw = runner.read_json(tmp_path / "raw-response.json")
        assert raw["usage_metadata"]["total_tokens"] == 133
        assert (
            raw["raw_tool_calls"] == delegate.response.additional_kwargs["tool_calls"]
        )
        assert (tmp_path / "quote-validation.json").exists()
    else:
        assert not (tmp_path / "raw-response.json").exists()
        assert summary["error"]
    with pytest.raises(ValueError, match="already used/reserved"):
        runner.run(tmp_path)
    assert len(delegate.calls) == 1


def test_real_openai_adapter_receives_frozen_sdk_options_and_forced_tool(
    tmp_path, monkeypatch, isolated_gateway
):
    _freeze_small_run(tmp_path)
    observed = {"invocations": 0}

    class OfflineChatOpenAI:
        def __init__(self, **kwargs):
            observed["client_kwargs"] = kwargs

        def bind_tools(self, tools, *, tool_choice):
            observed["tools"] = tools
            observed["tool_choice"] = tool_choice
            return self

        def invoke(self, messages):
            observed["invocations"] += 1
            observed["messages"] = messages
            return _response()

    original_import = runner.gateway.importlib.import_module

    def import_with_offline_client(name, *args, **kwargs):
        if name == "langchain_openai":
            return SimpleNamespace(ChatOpenAI=OfflineChatOpenAI)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(
        runner.gateway.importlib, "import_module", import_with_offline_client
    )
    monkeypatch.setitem(
        runner.gateway.CONTRACT_ADAPTERS,
        "openai_compatible",
        runner.gateway.OpenAICompatibleContractAdapter(),
    )
    summary = runner.run(tmp_path)
    assert summary["status"] == "review_pending"
    assert observed["invocations"] == summary["application_request_count"] == 1
    kwargs = observed["client_kwargs"]
    assert kwargs["model"] == runner.MODEL
    assert kwargs["max_tokens"] == 65536
    assert kwargs["temperature"] == 0.2
    assert kwargs["timeout"] == 1800
    assert kwargs["max_retries"] == 0
    assert kwargs["model_kwargs"]["reasoning_effort"] == "medium"
    assert observed["tool_choice"] == {
        "type": "function",
        "function": {"name": runner.DIGEST_RESULT_TOOL["name"]},
    }
    assert (
        observed["tools"][0]["function"]["parameters"]
        == runner.DIGEST_RESULT_TOOL["input_schema"]
    )
    assert observed["messages"][-1].content == "他仍在寻找。"
