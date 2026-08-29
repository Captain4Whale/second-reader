"""Shared, deterministic JSON encoding for durable reading artifacts.

The format is intentionally the byte-for-byte ``sr-canonical-json-v1``
primitive first shipped by Annotation Pack v0.  Keeping it in ``reading_core``
lets producer-neutral product artifacts and Annotation Pack use one frozen
implementation without making the shared reading layer depend on a consumer.
"""

from __future__ import annotations

from collections.abc import Mapping
import json
from typing import TypeAlias


JSONScalar: TypeAlias = None | bool | int | str
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

CANONICALIZATION = "sr-canonical-json-v1"
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1


class CanonicalJsonError(ValueError):
    """Raised when a value cannot be represented by the canonical primitive."""


def validate_json_value(value: object) -> None:
    """Reject values outside the strict interoperable JSON domain."""

    _to_plain_json(value, path="$", active=set())


def canonical_json_bytes(value: object) -> bytes:
    """Encode one value as exact ``sr-canonical-json-v1`` bytes."""

    plain = _to_plain_json(value, path="$", active=set())
    try:
        encoded = json.dumps(
            plain,
            allow_nan=False,
            check_circular=True,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, UnicodeEncodeError) as exc:
        raise CanonicalJsonError("value cannot be encoded as canonical JSON") from exc
    return encoded + b"\n"


def plain_json_value(value: object) -> JSONValue:
    """Return a detached, strict JSON-shaped snapshot of ``value``."""

    return _to_plain_json(value, path="$", active=set())


def _to_plain_json(value: object, *, path: str, active: set[int]) -> JSONValue:
    if value is None or isinstance(value, (bool, int, str)):
        if isinstance(value, str):
            _require_utf8(value, path)
        if (
            isinstance(value, int)
            and not isinstance(value, bool)
            and abs(value) > MAX_SAFE_JSON_INTEGER
        ):
            raise CanonicalJsonError(
                f"{path} integer is outside the v0 interoperable range"
            )
        return value
    if isinstance(value, float):
        raise CanonicalJsonError(f"{path} must not contain floating-point numbers")

    if isinstance(value, Mapping):
        return _mapping_to_plain_json(value, path=path, active=active)
    if isinstance(value, (list, tuple)):
        return _sequence_to_plain_json(value, path=path, active=active)

    raise CanonicalJsonError(
        f"{path} has non-JSON value type {type(value).__name__}"
    )


def _mapping_to_plain_json(
    value: Mapping[object, object],
    *,
    path: str,
    active: set[int],
) -> dict[str, JSONValue]:
    identity = id(value)
    if identity in active:
        raise CanonicalJsonError(f"{path} contains a circular reference")
    active.add(identity)
    try:
        result: dict[str, JSONValue] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise CanonicalJsonError(f"{path} contains a non-string object key")
            _require_utf8(key, f"{path} object key")
            result[key] = _to_plain_json(
                child,
                path=_child_path(path, key),
                active=active,
            )
        return result
    finally:
        active.remove(identity)


def _sequence_to_plain_json(
    value: list[object] | tuple[object, ...],
    *,
    path: str,
    active: set[int],
) -> list[JSONValue]:
    identity = id(value)
    if identity in active:
        raise CanonicalJsonError(f"{path} contains a circular reference")
    active.add(identity)
    try:
        return [
            _to_plain_json(child, path=f"{path}[{index}]", active=active)
            for index, child in enumerate(value)
        ]
    finally:
        active.remove(identity)


def _require_utf8(value: str, path: str) -> None:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalJsonError(f"{path} contains an invalid Unicode surrogate") from exc


def _child_path(parent: str, key: str) -> str:
    if key.isidentifier():
        return f"{parent}.{key}"
    return f"{parent}[{key!r}]"


__all__ = [
    "CANONICALIZATION",
    "CanonicalJsonError",
    "JSONScalar",
    "JSONValue",
    "MAX_SAFE_JSON_INTEGER",
    "canonical_json_bytes",
    "plain_json_value",
    "validate_json_value",
]
