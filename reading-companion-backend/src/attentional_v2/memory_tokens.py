"""Token estimation helpers for attentional_v2 ReadingMemory."""

from __future__ import annotations

import re
from typing import Mapping


TOKEN_ESTIMATOR_ID = "tiktoken_o200k_base_v1"
TOKEN_ESTIMATOR_ENCODING = "o200k_base"
TOKEN_ESTIMATOR_FALLBACK_ENCODING = "cl100k_base"
TOKEN_ESTIMATOR_SAFETY_MULTIPLIER = 1.10


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _heuristic_token_count(text: str) -> int:
    if not text:
        return 0
    cjk_count = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    latin_chunks = re.findall(r"[A-Za-z0-9_]+", text)
    punctuation_count = max(0, len(text) - cjk_count - sum(len(chunk) for chunk in latin_chunks))
    return max(1, int(cjk_count * 1.15 + len(latin_chunks) * 1.35 + punctuation_count * 0.25))


def raw_token_count(text: object) -> tuple[int, str, str]:
    """Return an unsafed token count plus estimator metadata."""

    cleaned = _clean_text(text)
    if not cleaned:
        return 0, TOKEN_ESTIMATOR_ENCODING, ""
    try:
        import tiktoken  # type: ignore[import-not-found]

        try:
            encoding = tiktoken.get_encoding(TOKEN_ESTIMATOR_ENCODING)
            encoding_name = TOKEN_ESTIMATOR_ENCODING
        except Exception:
            encoding = tiktoken.get_encoding(TOKEN_ESTIMATOR_FALLBACK_ENCODING)
            encoding_name = TOKEN_ESTIMATOR_FALLBACK_ENCODING
        return len(encoding.encode(cleaned)), encoding_name, ""
    except Exception as exc:  # pragma: no cover - dependency/environment fallback
        return _heuristic_token_count(cleaned), "heuristic_cjk_latin_v1", f"tiktoken_unavailable:{type(exc).__name__}"


def estimate_tokens(text: object) -> int:
    """Return a safed token estimate for prompt-budget accounting."""

    raw_count, _encoding, _degradation = raw_token_count(text)
    if raw_count <= 0:
        return 0
    return max(1, int(raw_count * TOKEN_ESTIMATOR_SAFETY_MULTIPLIER + 0.999))


def token_estimate_payload(text: object) -> dict[str, object]:
    """Return stable token-estimate metadata for one memory text."""

    raw_count, encoding_name, degradation = raw_token_count(text)
    tokens = max(0, int(raw_count * TOKEN_ESTIMATOR_SAFETY_MULTIPLIER + 0.999)) if raw_count else 0
    payload: dict[str, object] = {
        "estimator": TOKEN_ESTIMATOR_ID,
        "encoding": encoding_name,
        "tokens": tokens,
        "raw_tokens": raw_count,
        "safety_multiplier": TOKEN_ESTIMATOR_SAFETY_MULTIPLIER,
    }
    if degradation:
        payload["degradation_reason"] = degradation
    return payload


def tokens_from_estimate(value: object) -> int:
    """Read a stored safed token estimate if available."""

    if not isinstance(value, Mapping):
        return 0
    try:
        return max(0, int(value.get("tokens", 0) or 0))
    except (TypeError, ValueError):
        return 0
