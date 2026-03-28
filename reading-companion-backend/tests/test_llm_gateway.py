"""Tests for the shared backend LLM gateway and registry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from src.iterator_reader import llm_utils
from src.reading_runtime import artifacts as runtime_artifacts
from src.reading_runtime.llm_gateway import (
    CONTRACT_ADAPTERS,
    JsonlTraceSink,
    ReaderLLMError,
    clear_llm_gateway_runtime_state,
    eval_trace_context,
    get_llm_profile_stable_concurrency,
    get_llm_provider_stable_concurrency,
    invoke_json,
    llm_invocation_scope,
    runtime_trace_context,
)
from src.reading_runtime.llm_registry import (
    DEFAULT_DATASET_REVIEW_PROFILE_ID,
    DEFAULT_EVAL_JUDGE_PROFILE_ID,
    DEFAULT_RUNTIME_PROFILE_ID,
    LLMRegistryError,
    clear_llm_registry_cache,
    get_llm_profile,
    get_llm_registry,
)


@dataclass
class _FakeResponse:
    content: str


class _RecordingAdapter:
    def __init__(self, behavior: dict[str, str] | None = None, *, response_content: str | None = None):
        self.behavior = behavior or {}
        self.response_content = response_content or '{"ok": true}'
        self.calls: list[dict[str, Any]] = []

    def invoke(
        self,
        messages: list[Any],
        *,
        provider: Any,
        profile: Any,
        api_key: str,
        timeout_seconds: int,
    ) -> Any:
        self.calls.append(
            {
                "provider_id": provider.provider_id,
                "contract": provider.contract,
                "model": profile.model,
                "api_key": api_key,
                "timeout_seconds": timeout_seconds,
                "message_count": len(messages),
            }
        )
        action = self.behavior.get(api_key, "ok")
        if action == "auth_error":
            raise RuntimeError("invalid api key")
        if action == "timeout":
            raise RuntimeError("timed out")
        payload = self.response_content.replace("__API_KEY__", api_key)
        return _FakeResponse(payload)


class _SleepingRecordingAdapter(_RecordingAdapter):
    def __init__(self, delay_seconds: float):
        super().__init__()
        self.delay_seconds = delay_seconds
        self._lock = threading.Lock()
        self.active_calls = 0
        self.max_active_calls = 0

    def invoke(
        self,
        messages: list[Any],
        *,
        provider: Any,
        profile: Any,
        api_key: str,
        timeout_seconds: int,
    ) -> Any:
        with self._lock:
            self.active_calls += 1
            self.max_active_calls = max(self.max_active_calls, self.active_calls)
        try:
            time.sleep(self.delay_seconds)
            return super().invoke(
                messages,
                provider=provider,
                profile=profile,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
            )
        finally:
            with self._lock:
                self.active_calls -= 1


class _SequencedRecordingAdapter(_RecordingAdapter):
    def __init__(self, actions: list[str], *, response_content: str | None = None):
        super().__init__(response_content=response_content)
        self._actions = list(actions)

    def invoke(
        self,
        messages: list[Any],
        *,
        provider: Any,
        profile: Any,
        api_key: str,
        timeout_seconds: int,
    ) -> Any:
        self.calls.append(
            {
                "provider_id": provider.provider_id,
                "contract": provider.contract,
                "model": profile.model,
                "api_key": api_key,
                "timeout_seconds": timeout_seconds,
                "message_count": len(messages),
            }
        )
        action = self._actions.pop(0) if self._actions else "ok"
        if action == "quota":
            raise RuntimeError("429 rate limit")
        if action == "auth_error":
            raise RuntimeError("invalid api key")
        if action == "timeout":
            raise RuntimeError("timed out")
        payload = self.response_content.replace("__API_KEY__", api_key)
        return _FakeResponse(payload)


@pytest.fixture(autouse=True)
def _clear_registry_and_env(monkeypatch: pytest.MonkeyPatch):
    for key in [
        "LLM_TARGETS_JSON",
        "LLM_TARGETS_PATH",
        "LLM_PROFILE_BINDINGS_JSON",
        "LLM_PROFILE_BINDINGS_PATH",
        "LLM_REGISTRY_JSON",
        "LLM_REGISTRY_PATH",
        "LLM_PROVIDER_CONTRACT",
        "LLM_BASE_URL",
        "LLM_API_KEY",
        "LLM_MODEL",
        "LLM_DATASET_REVIEW_MODEL",
        "LLM_EVAL_JUDGE_MODEL",
        "BACKEND_RUNTIME_ROOT",
        "PRIMARY_KEY",
        "SECONDARY_KEY",
        "POOL_A",
        "POOL_B",
        "ANTHROPIC_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
    clear_llm_gateway_runtime_state()
    clear_llm_registry_cache()
    yield
    clear_llm_gateway_runtime_state()
    clear_llm_registry_cache()


def _set_registry(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setenv("LLM_REGISTRY_JSON", json.dumps(payload))
    clear_llm_registry_cache()


def _set_targets_and_bindings(
    monkeypatch: pytest.MonkeyPatch,
    *,
    targets: dict[str, Any],
    bindings: dict[str, Any],
) -> None:
    monkeypatch.setenv("LLM_TARGETS_JSON", json.dumps(targets))
    monkeypatch.setenv("LLM_PROFILE_BINDINGS_JSON", json.dumps(bindings))
    clear_llm_registry_cache()


def _set_targets_and_bindings_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    targets: dict[str, Any],
    bindings: dict[str, Any],
) -> tuple[Path, Path]:
    targets_path = tmp_path / "llm_targets.local.json"
    bindings_path = tmp_path / "llm_profile_bindings.local.json"
    targets_path.write_text(json.dumps(targets), encoding="utf-8")
    bindings_path.write_text(json.dumps(bindings), encoding="utf-8")
    monkeypatch.setenv("LLM_TARGETS_PATH", str(targets_path))
    monkeypatch.setenv("LLM_PROFILE_BINDINGS_PATH", str(bindings_path))
    clear_llm_registry_cache()
    return targets_path, bindings_path


def _required_bindings(
    runtime_target_id: str,
    *,
    dataset_target_id: str | None = None,
    eval_target_id: str | None = None,
) -> dict[str, Any]:
    return {
        "profiles": [
            {
                "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                "target_id": runtime_target_id,
            },
            {
                "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                "target_id": dataset_target_id or runtime_target_id,
            },
            {
                "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                "target_id": eval_target_id or dataset_target_id or runtime_target_id,
            },
        ]
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_registry_parses_target_bindings_and_direct_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "env-secret")
    _set_targets_and_bindings(
        monkeypatch,
        targets={
            "targets": [
                {
                    "target_id": "minimax_runtime",
                    "contract": "anthropic",
                    "base_url": "https://api.minimaxi.com/anthropic",
                    "model": "MiniMax-M2.5-highspeed",
                    "credentials": [
                        {"credential_id": "primary", "api_key": "direct-secret"},
                        {"credential_id": "secondary_env", "api_key_env": "PRIMARY_KEY"},
                    ],
                    "timeout_seconds": 95,
                    "retry_attempts": 4,
                    "max_concurrency": 7,
                }
            ]
        },
        bindings={
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "target_id": "minimax_runtime",
                    "temperature": 0.1,
                    "max_tokens": 2048,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "target_id": "minimax_runtime",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "target_id": "minimax_runtime",
                },
            ]
        },
    )

    registry = get_llm_registry()
    provider = registry.get_provider("minimax_runtime")
    runtime_profile = get_llm_profile(DEFAULT_RUNTIME_PROFILE_ID)

    assert registry.source == "env:LLM_TARGETS_JSON+LLM_PROFILE_BINDINGS_JSON"
    assert provider.base_url == "https://api.minimaxi.com/anthropic"
    assert provider.resolved_key_pool() == [
        {"slot_id": "primary", "api_key": "direct-secret"},
        {"slot_id": "secondary_env", "api_key": "env-secret"},
    ]
    assert runtime_profile.provider_id == "minimax_runtime"
    assert runtime_profile.model == "MiniMax-M2.5-highspeed"
    assert runtime_profile.temperature == 0.1
    assert runtime_profile.max_tokens == 2048


def test_profile_binding_requires_target_id(monkeypatch: pytest.MonkeyPatch):
    _set_targets_and_bindings(
        monkeypatch,
        targets={
            "targets": [
                {
                    "target_id": "minimax_runtime",
                    "contract": "anthropic",
                    "base_url": "https://api.minimaxi.com/anthropic",
                    "model": "MiniMax-M2.5-highspeed",
                    "credentials": [{"credential_id": "primary", "api_key": "secret"}],
                }
            ]
        },
        bindings={
            "profiles": [
                {"profile_id": DEFAULT_RUNTIME_PROFILE_ID},
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "target_id": "minimax_runtime",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "target_id": "minimax_runtime",
                },
            ]
        },
    )

    with pytest.raises(LLMRegistryError, match="Profile runtime_reader_default is missing target_id."):
        get_llm_registry()


@pytest.mark.parametrize(
    ("targets", "bindings", "expected_error"),
    [
        (
            {
                "targets": [
                    {
                        "target_id": "shared_target",
                        "contract": "anthropic",
                        "base_url": "https://api.minimaxi.com/anthropic",
                        "model": "MiniMax-M2.5-highspeed",
                        "credentials": [{"credential_id": "primary", "api_key": "one"}],
                    },
                    {
                        "target_id": "shared_target",
                        "contract": "anthropic",
                        "base_url": "https://api.minimaxi.com/anthropic",
                        "model": "MiniMax-M2.5-highspeed",
                        "credentials": [{"credential_id": "secondary", "api_key": "two"}],
                    },
                ]
            },
            _required_bindings("shared_target"),
            "LLM targets payload reuses target_id shared_target.",
        ),
        (
            {
                "targets": [
                    {
                        "target_id": "minimax_runtime",
                        "contract": "anthropic",
                        "base_url": "https://api.minimaxi.com/anthropic",
                        "model": "MiniMax-M2.5-highspeed",
                        "credentials": [
                            {"credential_id": "primary", "api_key": "one"},
                            {"credential_id": "primary", "api_key": "two"},
                        ],
                    }
                ]
            },
            _required_bindings("minimax_runtime"),
            "Target minimax_runtime reuses credential_id primary.",
        ),
        (
            {
                "targets": [
                    {
                        "target_id": "minimax_runtime",
                        "contract": "anthropic",
                        "base_url": "https://api.minimaxi.com/anthropic",
                        "model": "MiniMax-M2.5-highspeed",
                        "credentials": [{"credential_id": "primary", "api_key": "one"}],
                    }
                ]
            },
            {
                "profiles": [
                    {
                        "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                        "target_id": "minimax_runtime",
                    },
                    {
                        "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                        "target_id": "minimax_runtime",
                    },
                    {
                        "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                        "target_id": "minimax_runtime",
                    },
                    {
                        "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                        "target_id": "minimax_runtime",
                    },
                ]
            },
            "LLM profile bindings payload reuses profile_id runtime_reader_default.",
        ),
    ],
)
def test_target_binding_rejects_identifier_collisions(
    monkeypatch: pytest.MonkeyPatch,
    targets: dict[str, Any],
    bindings: dict[str, Any],
    expected_error: str,
):
    _set_targets_and_bindings(
        monkeypatch,
        targets=targets,
        bindings=bindings,
    )

    with pytest.raises(LLMRegistryError, match=expected_error):
        get_llm_registry()


@pytest.mark.parametrize(
    ("field_to_remove", "expected_error"),
    [
        ("contract", "Target minimax_runtime is missing contract."),
        ("base_url", "Target minimax_runtime is missing base_url."),
        ("model", "Target minimax_runtime is missing model."),
        ("credentials", "Target minimax_runtime must define at least one credential."),
    ],
)
def test_target_binding_requires_complete_target_fields(
    monkeypatch: pytest.MonkeyPatch,
    field_to_remove: str,
    expected_error: str,
):
    target = {
        "target_id": "minimax_runtime",
        "contract": "anthropic",
        "base_url": "https://api.minimaxi.com/anthropic",
        "model": "MiniMax-M2.5-highspeed",
        "credentials": [{"credential_id": "primary", "api_key": "secret"}],
    }
    if field_to_remove == "credentials":
        target["credentials"] = []
    else:
        target.pop(field_to_remove)

    _set_targets_and_bindings(
        monkeypatch,
        targets={"targets": [target]},
        bindings=_required_bindings("minimax_runtime"),
    )

    with pytest.raises(LLMRegistryError, match=expected_error):
        get_llm_registry()


def test_same_target_pooled_credentials_failover_uses_credential_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _set_targets_and_bindings(
        monkeypatch,
        targets={
            "targets": [
                {
                    "target_id": "minimax_runtime",
                    "contract": "anthropic",
                    "base_url": "https://api.minimaxi.com/anthropic",
                    "model": "MiniMax-M2.5-highspeed",
                    "credentials": [
                        {"credential_id": "primary", "api_key": "bad-key"},
                        {"credential_id": "secondary", "api_key": "good-key"},
                    ],
                    "retry_attempts": 1,
                    "max_concurrency": 2,
                }
            ]
        },
        bindings=_required_bindings("minimax_runtime"),
    )
    adapter = _RecordingAdapter(
        {"bad-key": "auth_error", "good-key": "ok"},
        response_content='{"ok": true, "api_key": "__API_KEY__"}',
    )
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    output_dir = tmp_path / "output" / "target-first-demo"
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(output_dir, mechanism_key="iterator_v1"),
    ):
        payload = invoke_json("system", "user", {})

    standard_rows = _read_jsonl(runtime_artifacts.llm_standard_trace_file(output_dir))

    assert payload == {"ok": True, "api_key": "good-key"}
    assert [call["api_key"] for call in adapter.calls] == ["bad-key", "good-key"]
    assert standard_rows[-1]["fallback"]["key_slots_tried"] == ["primary", "secondary"]
    assert standard_rows[-1]["key_slot_id"] == "secondary"


def test_mixed_target_bindings_support_different_contracts_and_models(monkeypatch: pytest.MonkeyPatch):
    _set_targets_and_bindings(
        monkeypatch,
        targets={
            "targets": [
                {
                    "target_id": "minimax_runtime",
                    "contract": "anthropic",
                    "base_url": "https://api.minimaxi.com/anthropic",
                    "model": "MiniMax-M2.5-highspeed",
                    "credentials": [{"credential_id": "primary", "api_key": "runtime-key"}],
                },
                {
                    "target_id": "gemini_judge",
                    "contract": "google_genai",
                    "base_url": "https://generativelanguage.googleapis.com",
                    "model": "gemini-3.1-pro",
                    "credentials": [{"credential_id": "judge", "api_key": "judge-key"}],
                },
            ]
        },
        bindings=_required_bindings(
            "minimax_runtime",
            dataset_target_id="gemini_judge",
            eval_target_id="gemini_judge",
        ),
    )

    registry = get_llm_registry()
    runtime_profile = get_llm_profile(DEFAULT_RUNTIME_PROFILE_ID)
    dataset_profile = get_llm_profile(DEFAULT_DATASET_REVIEW_PROFILE_ID)

    assert registry.get_provider("minimax_runtime").contract == "anthropic"
    assert registry.get_provider("gemini_judge").contract == "google_genai"
    assert runtime_profile.provider_id == "minimax_runtime"
    assert runtime_profile.model == "MiniMax-M2.5-highspeed"
    assert dataset_profile.provider_id == "gemini_judge"
    assert dataset_profile.model == "gemini-3.1-pro"


def test_target_binding_path_loader_smoke_invokes_gateway(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    targets_path, bindings_path = _set_targets_and_bindings_path(
        monkeypatch,
        tmp_path,
        targets={
            "targets": [
                {
                    "target_id": "minimax_runtime",
                    "contract": "anthropic",
                    "base_url": "https://api.minimaxi.com/anthropic",
                    "model": "MiniMax-M2.5-highspeed",
                    "credentials": [{"credential_id": "primary", "api_key": "path-key"}],
                }
            ]
        },
        bindings=_required_bindings("minimax_runtime"),
    )
    adapter = _RecordingAdapter(response_content='{"ok": true, "api_key": "__API_KEY__"}')
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    registry = get_llm_registry()
    with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
        payload = invoke_json("system", "user", {})

    assert payload == {"ok": True, "api_key": "path-key"}
    assert str(targets_path) in registry.source
    assert str(bindings_path) in registry.source
    assert adapter.calls[0]["model"] == "MiniMax-M2.5-highspeed"


def test_registry_path_backward_compatibility_still_loads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "secret-a")
    registry_path = tmp_path / "llm_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "providers": [
                    {
                        "provider_id": "anthropic_primary",
                        "contract": "anthropic",
                        "api_key_env": "PRIMARY_KEY",
                        "supported_models": ["claude-opus-4-6"],
                    }
                ],
                "profiles": [
                    {
                        "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                        "provider_id": "anthropic_primary",
                        "model": "claude-opus-4-6",
                    },
                    {
                        "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                        "provider_id": "anthropic_primary",
                        "model": "claude-opus-4-6",
                    },
                    {
                        "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                        "provider_id": "anthropic_primary",
                        "model": "claude-opus-4-6",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LLM_REGISTRY_PATH", str(registry_path))
    clear_llm_registry_cache()

    registry = get_llm_registry()

    assert registry.source == str(registry_path)
    assert registry.get_provider("anthropic_primary").resolved_key_pool() == [
        {"slot_id": "PRIMARY_KEY", "api_key": "secret-a"}
    ]


def test_legacy_env_fallback_registry_still_loads(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LLM_PROVIDER_CONTRACT", "anthropic")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.minimaxi.com/anthropic")
    monkeypatch.setenv("LLM_API_KEY", "legacy-key")
    monkeypatch.setenv("LLM_MODEL", "MiniMax-M2.5-highspeed")
    monkeypatch.setenv("LLM_DATASET_REVIEW_MODEL", "MiniMax-M2.5-highspeed")
    monkeypatch.setenv("LLM_EVAL_JUDGE_MODEL", "MiniMax-M2.5-highspeed")
    clear_llm_registry_cache()

    registry = get_llm_registry()
    runtime_profile = get_llm_profile(DEFAULT_RUNTIME_PROFILE_ID)

    assert registry.source == "legacy_env"
    assert registry.get_provider("legacy_default").resolved_key_pool() == [
        {"slot_id": "LLM_API_KEY", "api_key": "legacy-key"}
    ]
    assert runtime_profile.model == "MiniMax-M2.5-highspeed"


def test_registry_parses_structured_profiles_and_env_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "secret-a")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "timeout_seconds": 90,
                    "retry_attempts": 2,
                    "max_concurrency": 3,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "max_concurrency": 1,
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "timeout_seconds": 120,
                },
            ],
        },
    )

    registry = get_llm_registry()
    provider = registry.get_provider("anthropic_primary")
    runtime_profile = get_llm_profile(DEFAULT_RUNTIME_PROFILE_ID)

    assert registry.source == "env:LLM_REGISTRY_JSON"
    assert provider.resolved_key_pool() == [{"slot_id": "PRIMARY_KEY", "api_key": "secret-a"}]
    assert runtime_profile.model == "claude-opus-4-6"
    assert runtime_profile.provider_id == "anthropic_primary"
    assert provider.quota_cooldown_base_seconds == 10
    assert provider.quota_cooldown_max_seconds == 60
    assert provider.quota_state_ttl_seconds == 120
    assert runtime_profile.quota_retry_attempts == 2
    assert runtime_profile.quota_wait_budget_seconds == 25


def test_registry_parses_explicit_quota_retry_fields(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "secret-a")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "quota_cooldown_base_seconds": 7,
                    "quota_cooldown_max_seconds": 21,
                    "quota_state_ttl_seconds": 45,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "quota_retry_attempts": 4,
                    "quota_wait_budget_seconds": 30,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "quota_retry_attempts": 8,
                    "quota_wait_budget_seconds": 240,
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "quota_retry_attempts": 9,
                    "quota_wait_budget_seconds": 300,
                },
            ],
        },
    )

    provider = get_llm_registry().get_provider("anthropic_primary")
    runtime_profile = get_llm_profile(DEFAULT_RUNTIME_PROFILE_ID)
    review_profile = get_llm_profile(DEFAULT_DATASET_REVIEW_PROFILE_ID)

    assert provider.quota_cooldown_base_seconds == 7
    assert provider.quota_cooldown_max_seconds == 21
    assert provider.quota_state_ttl_seconds == 45
    assert runtime_profile.quota_retry_attempts == 4
    assert runtime_profile.quota_wait_budget_seconds == 30
    assert review_profile.quota_retry_attempts == 8
    assert review_profile.quota_wait_budget_seconds == 240


def test_registry_rejects_missing_required_profiles(monkeypatch: pytest.MonkeyPatch):
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                }
            ],
        },
    )

    with pytest.raises(LLMRegistryError, match="missing required profile"):
        get_llm_registry()


def test_same_model_key_failover_succeeds_and_emits_runtime_trace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POOL_A", "bad-key")
    monkeypatch.setenv("POOL_B", "good-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "key_pool_envs": ["POOL_A", "POOL_B"],
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "max_concurrency": 2,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                },
            ],
        },
    )
    adapter = _RecordingAdapter(
        {"bad-key": "auth_error", "good-key": "ok"},
        response_content='{"ok": true, "api_key": "__API_KEY__"}',
    )
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    output_dir = tmp_path / "output" / "demo"
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(
            output_dir,
            mechanism_key="iterator_v1",
            debug_enabled=True,
            stage="read",
            node="think",
        ),
    ):
        payload = invoke_json("system", "user", {})

    standard_rows = _read_jsonl(runtime_artifacts.llm_standard_trace_file(output_dir))
    debug_rows = _read_jsonl(runtime_artifacts.llm_debug_trace_file(output_dir, "iterator_v1"))

    assert payload == {"ok": True, "api_key": "good-key"}
    assert [call["api_key"] for call in adapter.calls] == ["bad-key", "good-key"]
    assert standard_rows[-1]["status"] == "ok"
    assert standard_rows[-1]["fallback"]["used_failover"] is True
    assert standard_rows[-1]["fallback"]["key_slots_tried"] == ["POOL_A", "POOL_B"]
    assert debug_rows[-1]["response_excerpt"]


def test_cross_model_fallback_is_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POOL_A", "good-key")
    monkeypatch.setenv("POOL_B", "other-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "key_pool_envs": ["POOL_A"],
                    "supported_models": ["claude-opus-4-6"],
                },
                {
                    "provider_id": "gemini_backup",
                    "contract": "google_genai",
                    "key_pool_envs": ["POOL_B"],
                    "supported_models": ["gemini-3.1-pro"],
                },
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "fallback_provider_ids": ["gemini_backup"],
                    "allow_cross_provider_failover": True,
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", _RecordingAdapter())
    monkeypatch.setitem(CONTRACT_ADAPTERS, "google_genai", _RecordingAdapter())

    with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
        with pytest.raises(LLMRegistryError, match="cannot use fallback provider"):
            invoke_json("system", "user", {})


def test_eval_trace_context_writes_eval_run_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "judge-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    adapter = _RecordingAdapter()
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    run_dir = tmp_path / "eval-run"
    with llm_invocation_scope(
        profile_id=DEFAULT_EVAL_JUDGE_PROFILE_ID,
        trace_context=eval_trace_context(
            run_dir,
            eval_target="packet_review:demo",
            stage="adjudication",
            node="final",
        ),
    ):
        payload = invoke_json("system", "user", {})

    standard_rows = _read_jsonl(run_dir / "llm_traces" / "standard.jsonl")
    assert payload["ok"] is True
    assert adapter.calls[0]["api_key"] == "judge-key"
    assert standard_rows[-1]["eval_target"] == "packet_review:demo"
    assert standard_rows[-1]["stage"] == "adjudication"
    assert standard_rows[-1]["node"] == "final"


def test_legacy_wrapper_uses_shared_gateway(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LLM_PROVIDER_CONTRACT", "anthropic")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("LLM_API_KEY", "legacy-key")
    monkeypatch.setenv("LLM_MODEL", "claude-opus-4-6")
    clear_llm_registry_cache()
    adapter = _RecordingAdapter()
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    payload = llm_utils.invoke_json("system", "user", {})

    assert payload["ok"] is True
    assert adapter.calls[0]["api_key"] == "legacy-key"
    assert adapter.calls[0]["model"] == "claude-opus-4-6"


def test_attentional_node_uses_shared_runtime_trace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from src.attentional_v2.nodes import zoom_read
    from src.attentional_v2.schemas import (
        build_default_reader_policy,
        build_empty_anchor_memory,
        build_empty_knowledge_activations,
        build_empty_working_pressure,
    )

    monkeypatch.setenv("PRIMARY_KEY", "runtime-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    adapter = _RecordingAdapter(response_content='{"local_interpretation": "Focused on the hinge."}')
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    output_dir = tmp_path / "output" / "attn-demo"
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(output_dir, mechanism_key="attentional_v2"),
    ):
        result = zoom_read(
            focal_sentence={"sentence_id": "s1", "text": "Alpha hinge line.", "text_role": "body"},
            local_context_sentences=[],
            working_pressure=build_empty_working_pressure(),
            anchor_memory=build_empty_anchor_memory(),
            knowledge_activations=build_empty_knowledge_activations(),
            reader_policy=build_default_reader_policy(),
            output_language="en",
            output_dir=output_dir,
        )

    standard_rows = _read_jsonl(runtime_artifacts.llm_standard_trace_file(output_dir))
    assert result["local_interpretation"] == "Focused on the hinge."
    assert standard_rows[-1]["mechanism_key"] == "attentional_v2"
    assert standard_rows[-1]["stage"] == "phase4"
    assert standard_rows[-1]["node"] == "zoom_read"


def test_iterator_parse_node_uses_shared_runtime_trace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from src.iterator_reader.parse import segment_chapter_semantically

    monkeypatch.setenv("PRIMARY_KEY", "runtime-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    adapter = _RecordingAdapter(
        response_content=json.dumps(
            {
                "segments": [
                    {
                        "paragraph_start": 1,
                        "paragraph_end": 2,
                        "summary": "Keeps the two short paragraphs together.",
                    }
                ]
            }
        )
    )
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    output_dir = tmp_path / "output" / "iterator-demo"
    with llm_invocation_scope(
        profile_id=DEFAULT_RUNTIME_PROFILE_ID,
        trace_context=runtime_trace_context(output_dir, mechanism_key="iterator_v1"),
    ):
        segments = segment_chapter_semantically(
            1,
            "Chapter 1",
            "Alpha.\n\nBeta.",
            "en",
            paragraphs=["Alpha.", "Beta."],
        )

    standard_rows = _read_jsonl(runtime_artifacts.llm_standard_trace_file(output_dir))
    assert len(segments) == 1
    assert standard_rows[-1]["mechanism_key"] == "iterator_v1"
    assert standard_rows[-1]["stage"] == "parse"
    assert standard_rows[-1]["node"] == "semantic_segmentation"


def test_same_key_parallelism_allows_multiple_inflight_calls(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "same-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "initial_max_concurrency": 6,
                    "probe_max_concurrency": 12,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
            ],
        },
    )
    adapter = _SleepingRecordingAdapter(delay_seconds=0.1)
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    results: list[dict[str, Any]] = []

    def _invoke() -> None:
        with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
            results.append(invoke_json("system", "user", {}))

    first = threading.Thread(target=_invoke)
    second = threading.Thread(target=_invoke)
    first.start()
    second.start()
    first.join()
    second.join()

    assert len(results) == 2
    assert adapter.max_active_calls >= 2


def test_provider_backoff_reduces_stable_limit_after_timeout_pressure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PRIMARY_KEY", "timing-key")
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "initial_max_concurrency": 6,
                    "probe_max_concurrency": 12,
                    "min_stable_concurrency": 2,
                    "backoff_window_seconds": 30,
                    "recover_window_seconds": 30,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "max_concurrency": 12,
                    "default_burst_concurrency": 12,
                },
            ],
        },
    )
    adapter = _RecordingAdapter({"timing-key": "timeout"})
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
        with pytest.raises(ReaderLLMError):
            invoke_json("system", "user", {})
        with pytest.raises(ReaderLLMError):
            invoke_json("system", "user", {})

    assert get_llm_provider_stable_concurrency("anthropic_primary") == 5
    assert get_llm_profile_stable_concurrency(DEFAULT_RUNTIME_PROFILE_ID) == 5


def test_eval_profile_waits_through_shared_quota_cooldown_and_emits_trace_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("PRIMARY_KEY", "quota-key")
    monkeypatch.setenv("BACKEND_RUNTIME_ROOT", str(tmp_path))
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "quota_cooldown_base_seconds": 1,
                    "quota_cooldown_max_seconds": 1,
                    "quota_state_ttl_seconds": 30,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "quota_retry_attempts": 2,
                    "quota_wait_budget_seconds": 5,
                },
            ],
        },
    )
    adapter = _SequencedRecordingAdapter(
        ["quota", "ok"],
        response_content='{"ok": true, "mode": "judge"}',
    )
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    run_dir = tmp_path / "eval-run"
    started = time.monotonic()
    with llm_invocation_scope(
        profile_id=DEFAULT_EVAL_JUDGE_PROFILE_ID,
        trace_context=eval_trace_context(run_dir, eval_target="quota:judge", debug_enabled=True),
    ):
        payload = invoke_json("system", "user", {})
    elapsed = time.monotonic() - started

    standard_rows = _read_jsonl(run_dir / "llm_traces" / "standard.jsonl")
    debug_rows = _read_jsonl(run_dir / "llm_traces" / "debug.jsonl")

    assert payload == {"ok": True, "mode": "judge"}
    assert len(adapter.calls) == 2
    assert elapsed >= 0.9
    assert standard_rows[-1]["quota_retry_attempt_count"] == 1
    assert standard_rows[-1]["quota_wait_ms_total"] >= 900
    assert debug_rows[-1]["attempts"][1]["shared_quota_cooldown_honored"] is True
    assert debug_rows[-1]["attempts"][1]["quota_wait_ms_before_attempt"] >= 900


def test_runtime_profile_fails_when_quota_wait_budget_is_too_small(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("PRIMARY_KEY", "quota-key")
    monkeypatch.setenv("BACKEND_RUNTIME_ROOT", str(tmp_path))
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "quota_cooldown_base_seconds": 1,
                    "quota_cooldown_max_seconds": 1,
                    "quota_state_ttl_seconds": 30,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "quota_retry_attempts": 2,
                    "quota_wait_budget_seconds": 0,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    adapter = _SequencedRecordingAdapter(["quota", "ok"])
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
        with pytest.raises(ReaderLLMError, match="quota cooldown remains active"):
            invoke_json("system", "user", {})

    assert len(adapter.calls) == 1


def test_non_quota_retries_do_not_expand_after_quota_recovery_round(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("PRIMARY_KEY", "quota-key")
    monkeypatch.setenv("BACKEND_RUNTIME_ROOT", str(tmp_path))
    _set_registry(
        monkeypatch,
        {
            "providers": [
                {
                    "provider_id": "anthropic_primary",
                    "contract": "anthropic",
                    "api_key_env": "PRIMARY_KEY",
                    "supported_models": ["claude-opus-4-6"],
                    "retry_attempts": 1,
                    "quota_cooldown_base_seconds": 1,
                    "quota_cooldown_max_seconds": 1,
                    "quota_state_ttl_seconds": 30,
                }
            ],
            "profiles": [
                {
                    "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                    "retry_attempts": 1,
                    "quota_retry_attempts": 2,
                    "quota_wait_budget_seconds": 5,
                },
                {
                    "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
                {
                    "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                    "provider_id": "anthropic_primary",
                    "model": "claude-opus-4-6",
                },
            ],
        },
    )
    adapter = _SequencedRecordingAdapter(["quota", "timeout", "ok"])
    monkeypatch.setitem(CONTRACT_ADAPTERS, "anthropic", adapter)

    with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
        with pytest.raises(ReaderLLMError):
            invoke_json("system", "user", {})

    assert len(adapter.calls) == 2


def test_quota_cooldown_state_is_shared_across_processes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    backend_root = Path(__file__).resolve().parents[1]
    fake_module_dir = tmp_path / "fake_modules"
    fake_module_dir.mkdir(parents=True)
    fake_module_path = fake_module_dir / "langchain_anthropic.py"
    fake_module_path.write_text(
        textwrap.dedent(
            """
            import json
            import os
            import time
            from pathlib import Path


            class _FakeResponse:
                def __init__(self, content):
                    self.content = content


            class ChatAnthropic:
                def __init__(self, **kwargs):
                    self.kwargs = kwargs

                def invoke(self, messages):
                    log_path = Path(os.environ["FAKE_LANGCHAIN_LOG_PATH"])
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                    with log_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps({"ts": time.time(), "mode": os.environ.get("FAKE_LANGCHAIN_MODE", "ok")}) + "\\n")
                    if os.environ.get("FAKE_LANGCHAIN_MODE", "ok") == "quota":
                        raise RuntimeError("429 rate limit")
                    return _FakeResponse('{"ok": true}')
            """
        ),
        encoding="utf-8",
    )

    script = textwrap.dedent(
        """
        import json
        import time

        from src.reading_runtime.llm_gateway import invoke_json, llm_invocation_scope
        from src.reading_runtime.llm_registry import DEFAULT_RUNTIME_PROFILE_ID

        started = time.monotonic()
        try:
            with llm_invocation_scope(profile_id=DEFAULT_RUNTIME_PROFILE_ID):
                payload = invoke_json("system", "user", {})
            print(json.dumps({"ok": True, "elapsed": time.monotonic() - started, "payload": payload}))
        except Exception as exc:
            print(json.dumps({"ok": False, "elapsed": time.monotonic() - started, "error": str(exc), "problem_code": getattr(exc, "problem_code", None)}))
            raise
        """
    )

    registry_payload = {
        "providers": [
            {
                "provider_id": "anthropic_primary",
                "contract": "anthropic",
                "api_key_env": "PRIMARY_KEY",
                "supported_models": ["claude-opus-4-6"],
                "retry_attempts": 1,
                "quota_cooldown_base_seconds": 1,
                "quota_cooldown_max_seconds": 1,
                "quota_state_ttl_seconds": 30,
            }
        ],
        "profiles": [
            {
                "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
                "provider_id": "anthropic_primary",
                "model": "claude-opus-4-6",
                "quota_retry_attempts": 1,
                "quota_wait_budget_seconds": 0,
            },
            {
                "profile_id": DEFAULT_DATASET_REVIEW_PROFILE_ID,
                "provider_id": "anthropic_primary",
                "model": "claude-opus-4-6",
            },
            {
                "profile_id": DEFAULT_EVAL_JUDGE_PROFILE_ID,
                "provider_id": "anthropic_primary",
                "model": "claude-opus-4-6",
            },
        ],
    }

    base_env = os.environ.copy()
    base_env.update(
        {
            "BACKEND_RUNTIME_ROOT": str(tmp_path / "runtime-root"),
            "LLM_REGISTRY_JSON": json.dumps(registry_payload),
            "PRIMARY_KEY": "quota-key",
            "FAKE_LANGCHAIN_LOG_PATH": str(tmp_path / "fake-provider.log"),
            "PYTHONPATH": os.pathsep.join([str(fake_module_dir), base_env.get("PYTHONPATH", "")]).strip(os.pathsep),
        }
    )

    first_env = dict(base_env)
    first_env["FAKE_LANGCHAIN_MODE"] = "quota"
    first = subprocess.run(
        [sys.executable, "-c", script],
        cwd=backend_root,
        capture_output=True,
        text=True,
        env=first_env,
    )
    first_payload = json.loads(first.stdout.strip().splitlines()[-1])

    assert first.returncode != 0
    assert first_payload["ok"] is False
    assert first_payload["problem_code"] == "llm_quota"

    second_registry = dict(registry_payload)
    second_registry["profiles"] = [
        {
            "profile_id": DEFAULT_RUNTIME_PROFILE_ID,
            "provider_id": "anthropic_primary",
            "model": "claude-opus-4-6",
            "quota_retry_attempts": 1,
            "quota_wait_budget_seconds": 5,
        },
        *registry_payload["profiles"][1:],
    ]
    second_env = dict(base_env)
    second_env["LLM_REGISTRY_JSON"] = json.dumps(second_registry)
    second_env["FAKE_LANGCHAIN_MODE"] = "ok"
    second = subprocess.run(
        [sys.executable, "-c", script],
        cwd=backend_root,
        capture_output=True,
        text=True,
        env=second_env,
        check=True,
    )
    second_payload = json.loads(second.stdout.strip().splitlines()[-1])

    assert second_payload["ok"] is True
    assert second_payload["elapsed"] >= 0.5
