"""Canonical JSON and semantic digest primitives for Annotation Pack v0.

This module deliberately does not validate the Annotation Pack schema or repair
producer data.  Entity builders own normalization and the later semantic
validator owns cross-object invariants.  The only protocol-specific projection
here is the one used to calculate ``sr:semanticDigest``.
"""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import TypeAlias


JSONScalar: TypeAlias = None | bool | int | str
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

CANONICALIZATION = "sr-canonical-json-v1"
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1
_SEMANTIC_EXCLUDED_FIELDS = frozenset(
    {
        "generated",
        "generator",
        "sr:provenance",
        "sr:semanticDigest",
    }
)

__all__ = [
    "CANONICALIZATION",
    "CanonicalJsonError",
    "JSONScalar",
    "JSONValue",
    "MAX_SAFE_JSON_INTEGER",
    "canonical_json_bytes",
    "semantic_digest",
    "semantic_projection",
    "validate_json_value",
]


class CanonicalJsonError(ValueError):
    """Raised when a value cannot be represented by the v0 JSON primitive."""


def validate_json_value(value: object) -> None:
    """Reject values outside the strict JSON domain accepted by v0.

    Immutable JSON-shaped containers are accepted: any :class:`Mapping` with
    string keys and both lists and tuples for arrays.  Unordered containers and
    arbitrary Python objects are rejected rather than coerced.
    """

    _to_plain_json(value, path="$", active=set())


def canonical_json_bytes(value: object) -> bytes:
    """Encode one value as exact ``sr-canonical-json-v1`` bytes.

    Object keys use Python's Unicode-code-point order, arrays retain their input
    order, strings are emitted as supplied, and the byte stream has exactly one
    terminal LF and no BOM.
    """

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


def semantic_projection(pack: Mapping[str, object]) -> dict[str, JSONValue]:
    """Return the v0 semantic projection without mutating ``pack``.

    Four top-level serialization/provenance fields are excluded.  ``items`` is
    the only array whose order is changed, and is sorted lexicographically by
    annotation ``id``.  All other array orders remain significant.
    """

    if not isinstance(pack, Mapping):
        raise CanonicalJsonError("semantic projection root must be a mapping")
    plain = _to_plain_json(pack, path="$", active=set())
    if not isinstance(plain, dict):  # pragma: no cover - narrowed above
        raise AssertionError("mapping normalization did not produce an object")

    for field in _SEMANTIC_EXCLUDED_FIELDS:
        plain.pop(field, None)

    items = plain.get("items")
    if not isinstance(items, list):
        raise CanonicalJsonError("$.items must be an array")

    sortable: list[tuple[str, dict[str, JSONValue]]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise CanonicalJsonError(f"$.items[{index}] must be an object")
        annotation_id = item.get("id")
        if not isinstance(annotation_id, str):
            raise CanonicalJsonError(f"$.items[{index}].id must be a string")
        sortable.append((annotation_id, item))
    plain["items"] = [item for _, item in sorted(sortable, key=lambda pair: pair[0])]
    return plain


def semantic_digest(pack: Mapping[str, object]) -> str:
    """Return the lowercase SHA-256 of the canonical semantic projection."""

    return hashlib.sha256(canonical_json_bytes(semantic_projection(pack))).hexdigest()


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
