"""Provider-neutral token-usage normalization for LLM responses."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


_INPUT_KEYS = ("input_tokens", "prompt_tokens", "prompt_token_count")
_OUTPUT_KEYS = ("output_tokens", "completion_tokens", "candidates_token_count")
_TOTAL_KEYS = ("total_tokens", "total_token_count")
_CACHE_READ_KEYS = (
    "cache_read_input_tokens",
    "cache_read_tokens",
    "cached_tokens",
    "cached_content_token_count",
)
_CACHE_WRITE_KEYS = (
    "cache_creation_input_tokens",
    "cache_write_input_tokens",
    "cache_creation_tokens",
)
_REASONING_KEYS = ("reasoning_tokens", "thoughts_token_count")


@dataclass(frozen=True)
class NormalizedUsage:
    """Normalized token counts; missing provider facts remain ``None``."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    cache_write_input_tokens: int | None = None
    uncached_input_tokens: int | None = None
    reasoning_tokens: int | None = None
    billable_output_tokens: int | None = None
    status: str = "unavailable"
    source: str = "unavailable"
    provider_family: str = "unknown"
    invalid_fields: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "cache_write_input_tokens": self.cache_write_input_tokens,
            "uncached_input_tokens": self.uncached_input_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "billable_output_tokens": self.billable_output_tokens,
            "status": self.status,
            "source": self.source,
            "provider_family": self.provider_family,
            "invalid_fields": list(self.invalid_fields),
        }


def _as_mapping(value: object) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _attribute(value: object, name: str) -> object | None:
    try:
        return getattr(value, name)
    except (AttributeError, TypeError):
        return None


def _nonnegative_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None
    if not decimal_value.is_finite() or decimal_value < 0 or decimal_value != decimal_value.to_integral_value():
        return None
    return int(decimal_value)


def _first_count(payload: Mapping[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        count = _nonnegative_int(payload.get(key))
        if count is not None:
            return count
    return None


def _nested_mapping(payload: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    current: object = payload
    for key in keys:
        mapping = _as_mapping(current)
        if mapping is None:
            return {}
        current = mapping.get(key)
    return _as_mapping(current) or {}


def _invalid_fields(payload: Mapping[str, Any]) -> tuple[str, ...]:
    locations = [
        ("", payload, _INPUT_KEYS + _OUTPUT_KEYS + _TOTAL_KEYS + _CACHE_READ_KEYS + _CACHE_WRITE_KEYS + _REASONING_KEYS),
        ("input_token_details.", _nested_mapping(payload, "input_token_details"), _CACHE_READ_KEYS + _CACHE_WRITE_KEYS + ("cache_read", "cache_creation")),
        ("prompt_tokens_details.", _nested_mapping(payload, "prompt_tokens_details"), _CACHE_READ_KEYS + ("cached_tokens",)),
        ("output_token_details.", _nested_mapping(payload, "output_token_details"), _REASONING_KEYS + ("reasoning",)),
        ("completion_tokens_details.", _nested_mapping(payload, "completion_tokens_details"), _REASONING_KEYS + ("reasoning_tokens",)),
    ]
    invalid: set[str] = set()
    for prefix, mapping, keys in locations:
        for key in keys:
            if key in mapping and _nonnegative_int(mapping.get(key)) is None:
                invalid.add(f"{prefix}{key}")
    return tuple(sorted(invalid))


def _usage_candidates(response: object) -> list[tuple[str, Mapping[str, Any]]]:
    candidates: list[tuple[str, Mapping[str, Any]]] = []
    usage_metadata = _attribute(response, "usage_metadata")
    if usage_metadata is None and isinstance(response, Mapping):
        usage_metadata = response.get("usage_metadata")
    if mapping := _as_mapping(usage_metadata):
        candidates.append(("usage_metadata", mapping))

    response_metadata = _attribute(response, "response_metadata")
    if response_metadata is None and isinstance(response, Mapping):
        response_metadata = response.get("response_metadata")
    if metadata := _as_mapping(response_metadata):
        for key in ("token_usage", "usage", "usage_metadata"):
            if mapping := _as_mapping(metadata.get(key)):
                candidates.append((f"response_metadata.{key}", mapping))

    if isinstance(response, Mapping):
        for key in ("token_usage", "usage"):
            if mapping := _as_mapping(response.get(key)):
                candidates.append((key, mapping))
        candidates.append(("mapping", response))
    return candidates


def _provider_family(payload: Mapping[str, Any], *, source: str, hint: str | None) -> str:
    normalized_hint = str(hint or "").strip().lower()
    if normalized_hint in {"anthropic", "claude"}:
        return "anthropic"
    if normalized_hint in {"google", "google_genai", "gemini"}:
        return "google"
    if normalized_hint in {"openai", "openai_compatible", "azure_openai"}:
        return "openai_compatible"
    if any(key in payload for key in ("prompt_token_count", "candidates_token_count", "thoughts_token_count")):
        return "google"
    if "cache_creation_input_tokens" in payload:
        return "anthropic"
    if any(key in payload for key in ("prompt_tokens", "completion_tokens", "prompt_tokens_details")):
        return "openai_compatible"
    if source == "usage_metadata":
        return "langchain_normalized"
    return "unknown"


def _normalize_mapping(
    payload: Mapping[str, Any],
    *,
    source: str,
    provider_hint: str | None = None,
) -> NormalizedUsage:
    provider_family = _provider_family(payload, source=source, hint=provider_hint)
    input_tokens = _first_count(payload, _INPUT_KEYS)
    output_tokens = _first_count(payload, _OUTPUT_KEYS)
    total_tokens = _first_count(payload, _TOTAL_KEYS)

    input_details = _nested_mapping(payload, "input_token_details")
    prompt_details = _nested_mapping(payload, "prompt_tokens_details")
    output_details = _nested_mapping(payload, "output_token_details")
    completion_details = _nested_mapping(payload, "completion_tokens_details")

    cache_read = _first_count(payload, _CACHE_READ_KEYS)
    if cache_read is None:
        cache_read = _first_count(input_details, _CACHE_READ_KEYS + ("cache_read",))
    if cache_read is None:
        cache_read = _first_count(prompt_details, _CACHE_READ_KEYS + ("cached_tokens",))

    cache_write = _first_count(payload, _CACHE_WRITE_KEYS)
    if cache_write is None:
        cache_write = _first_count(input_details, _CACHE_WRITE_KEYS + ("cache_creation",))

    reasoning = _first_count(payload, _REASONING_KEYS)
    if reasoning is None:
        reasoning = _first_count(output_details, _REASONING_KEYS + ("reasoning",))
    if reasoning is None:
        reasoning = _first_count(completion_details, _REASONING_KEYS + ("reasoning_tokens",))

    invalid_fields = set(_invalid_fields(payload))
    if (
        input_tokens is not None
        and provider_family != "anthropic"
        and (cache_read or 0) + (cache_write or 0) > input_tokens
    ):
        invalid_fields.add("cache_input_tokens_exceed_input_tokens")
    if (
        output_tokens is not None
        and reasoning is not None
        and provider_family in {"openai_compatible", "langchain_normalized"}
        and reasoning > output_tokens
    ):
        invalid_fields.add("reasoning_tokens_exceed_output_tokens")

    known_total_components: int | None = None
    if input_tokens is not None and output_tokens is not None:
        if provider_family == "anthropic" and source != "usage_metadata":
            known_total_components = (
                input_tokens + output_tokens + (cache_read or 0) + (cache_write or 0)
            )
        elif provider_family == "google":
            known_total_components = input_tokens + output_tokens + (reasoning or 0)
        else:
            known_total_components = input_tokens + output_tokens
    if (
        total_tokens is not None
        and known_total_components is not None
        and total_tokens < known_total_components
    ):
        invalid_fields.add("total_tokens_less_than_known_components")

    uncached_input = None
    if input_tokens is not None:
        raw_anthropic_usage = provider_family == "anthropic" and source != "usage_metadata"
        if raw_anthropic_usage:
            uncached_input = input_tokens
        elif provider_family in {"google", "openai_compatible"} and cache_read is not None:
            uncached_input = input_tokens - cache_read - (cache_write or 0)
        elif cache_read is not None and cache_write is not None:
            uncached_input = input_tokens - cache_read - cache_write
    if uncached_input is not None and uncached_input < 0:
        uncached_input = None
    billable_output = output_tokens
    if provider_family == "google" and output_tokens is not None:
        # Gemini's candidates count excludes thoughts, while totalTokenCount
        # explicitly includes them. Missing thought usage is not assumed zero.
        billable_output = output_tokens + reasoning if reasoning is not None else None
    if total_tokens is None and input_tokens is not None and billable_output is not None:
        effective_input = input_tokens
        if provider_family == "anthropic" and source != "usage_metadata":
            if cache_read is not None and cache_write is not None:
                effective_input += cache_read + cache_write
            else:
                effective_input = -1
        if effective_input >= 0:
            total_tokens = effective_input + billable_output
    normalized_invalid_fields = tuple(sorted(invalid_fields))
    known = (input_tokens, output_tokens, total_tokens, cache_read, cache_write, reasoning)
    if normalized_invalid_fields:
        status = "invalid"
    elif all(value is None for value in known):
        status = "unavailable"
    elif input_tokens is not None and output_tokens is not None and total_tokens is not None:
        status = "complete"
    else:
        status = "partial"
    return NormalizedUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cache_read_input_tokens=cache_read,
        cache_write_input_tokens=cache_write,
        uncached_input_tokens=uncached_input,
        reasoning_tokens=reasoning,
        billable_output_tokens=billable_output,
        status=status,
        source=source,
        provider_family=provider_family,
        invalid_fields=normalized_invalid_fields,
    )


def normalize_provider_usage(
    response: object | None,
    *,
    provider_family: str | None = None,
) -> NormalizedUsage:
    """Normalize common LangChain/OpenAI/Anthropic/Google usage shapes."""

    if response is None:
        return NormalizedUsage()
    response_hint = provider_family
    response_metadata = _attribute(response, "response_metadata")
    if response_metadata is None and isinstance(response, Mapping):
        response_metadata = response.get("response_metadata")
    if not response_hint and isinstance(response_metadata, Mapping):
        response_hint = str(response_metadata.get("model_provider") or "").strip() or None
    for source, payload in _usage_candidates(response):
        normalized = _normalize_mapping(payload, source=source, provider_hint=response_hint)
        if normalized.status != "unavailable":
            return normalized
    return NormalizedUsage()


__all__ = ["NormalizedUsage", "normalize_provider_usage"]
