"""Stable taxonomy helpers for offline reader evaluation."""

from __future__ import annotations

import re


DIRECT_QUALITY = "direct_quality"
LOCAL_IMPACT = "local_impact"
SYSTEM_REGRESSION = "system_regression"
_SCOPE_VALUES = {
    DIRECT_QUALITY,
    LOCAL_IMPACT,
    SYSTEM_REGRESSION,
}

DETERMINISTIC_METRICS = "deterministic_metrics"
PAIRWISE_JUDGE = "pairwise_judge"
RUBRIC_JUDGE = "rubric_judge"
HUMAN_SPOT_CHECK = "human_spot_check"
_METHOD_VALUES = {
    DETERMINISTIC_METRICS,
    PAIRWISE_JUDGE,
    RUBRIC_JUDGE,
    HUMAN_SPOT_CHECK,
}

TARGET_SUBSEGMENT_SEGMENTATION = "subsegment_segmentation"

_TARGET_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def validate_target_slug(value: object) -> str:
    """Validate one evaluation target slug without freezing the whole target space."""
    target = str(value).strip()
    if not target or not _TARGET_RE.fullmatch(target):
        raise ValueError(f"invalid evaluation target slug: {value!r}")
    return target


def normalize_scope(value: object) -> str:
    """Normalize one stable scope value."""
    scope = str(value).strip().lower()
    if scope not in _SCOPE_VALUES:
        raise ValueError(f"invalid evaluation scope: {value!r}")
    return scope


def normalize_scopes(values: list[object] | tuple[object, ...]) -> list[str]:
    """Normalize scopes while preserving order and uniqueness."""
    normalized: list[str] = []
    for value in values:
        scope = normalize_scope(value)
        if scope not in normalized:
            normalized.append(scope)
    return normalized


def normalize_method(value: object) -> str:
    """Normalize one stable method value."""
    method = str(value).strip().lower()
    if method not in _METHOD_VALUES:
        raise ValueError(f"invalid evaluation method: {value!r}")
    return method


def normalize_methods(values: list[object] | tuple[object, ...]) -> list[str]:
    """Normalize methods while preserving order and uniqueness."""
    normalized: list[str] = []
    for value in values:
        method = normalize_method(value)
        if method not in normalized:
            normalized.append(method)
    return normalized


def scope_heading(scope: object) -> str:
    """Render one stable, reader-facing heading for a scope."""
    normalized = normalize_scope(scope)
    if normalized == DIRECT_QUALITY:
        return "Direct Quality"
    if normalized == LOCAL_IMPACT:
        return "Local Impact"
    return "System Regression"
