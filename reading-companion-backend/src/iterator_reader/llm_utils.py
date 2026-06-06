"""Compatibility wrapper over the shared backend LLM gateway."""

from __future__ import annotations

from typing import Any

from src.reading_runtime.llm_gateway import (
    LLMInvocationOverrides,
    LLMTraceContext,
    ReaderLLMError,
    current_llm_scope,
    eval_trace_context,
    invoke_json as _invoke_json,
    invoke_json_with_tool_loop as _invoke_json_with_tool_loop,
    invoke_structured_output_tool as _invoke_structured_output_tool,
    invoke_text as _invoke_text,
    invoke_tool_loop_with_final_output as _invoke_tool_loop_with_final_output,
    llm_invocation_scope,
    parse_json_payload,
    response_text,
    runtime_trace_context,
)


def invoke_json(system_prompt: str, user_prompt: str, default: Any, *, profile_id: str | None = None) -> Any:
    """Invoke the shared backend LLM gateway and parse a JSON payload."""

    return _invoke_json(system_prompt, user_prompt, default, profile_id=profile_id)


def invoke_json_with_tool_loop(*args: Any, **kwargs: Any) -> Any:
    """Invoke the shared backend LLM gateway with one bounded tool loop."""

    return _invoke_json_with_tool_loop(*args, **kwargs)


def invoke_structured_output_tool(*args: Any, **kwargs: Any) -> Any:
    """Invoke the shared backend LLM gateway with a forced final-output tool."""

    return _invoke_structured_output_tool(*args, **kwargs)


def invoke_tool_loop_with_final_output(*args: Any, **kwargs: Any) -> Any:
    """Invoke action tools, then force a final-output tool."""

    return _invoke_tool_loop_with_final_output(*args, **kwargs)


def invoke_text(system_prompt: str, user_prompt: str, default: str = "", *, profile_id: str | None = None) -> str:
    """Invoke the shared backend LLM gateway and return plain text."""

    return _invoke_text(system_prompt, user_prompt, default, profile_id=profile_id)


__all__ = [
    "LLMInvocationOverrides",
    "LLMTraceContext",
    "ReaderLLMError",
    "current_llm_scope",
    "eval_trace_context",
    "invoke_json",
    "invoke_json_with_tool_loop",
    "invoke_structured_output_tool",
    "invoke_text",
    "invoke_tool_loop_with_final_output",
    "llm_invocation_scope",
    "parse_json_payload",
    "response_text",
    "runtime_trace_context",
]
