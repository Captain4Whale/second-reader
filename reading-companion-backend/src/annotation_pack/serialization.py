"""Canonical JSON and semantic digest primitives for Annotation Pack v0.

This module deliberately does not validate the Annotation Pack schema or repair
producer data.  Entity builders own normalization and the later semantic
validator owns cross-object invariants.  The only profile-specific projection
here is the internal content digest used by immutable publication reports and
pointers.  That digest is never written into the public Pack.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from src.reading_core.canonical_json import (
    CANONICALIZATION,
    CanonicalJsonError,
    JSONScalar,
    JSONValue,
    MAX_SAFE_JSON_INTEGER,
    canonical_json_bytes,
    plain_json_value,
    validate_json_value,
)

_SEMANTIC_EXCLUDED_FIELDS = frozenset({"generated"})

__all__ = [
    "CANONICALIZATION",
    "CanonicalJsonError",
    "JSONScalar",
    "JSONValue",
    "MAX_SAFE_JSON_INTEGER",
    "canonical_json_bytes",
    "semantic_digest",
    "semantic_projection",
    "serialize_pack",
    "validate_json_value",
]


def semantic_projection(pack: Mapping[str, object]) -> dict[str, JSONValue]:
    """Return the v0 semantic projection without mutating ``pack``.

    Only volatile top-level ``generated`` is excluded.  ``items`` is the only
    array whose order is changed, and is sorted lexicographically by annotation
    ``id``.  All other array orders remain significant.
    """

    if not isinstance(pack, Mapping):
        raise CanonicalJsonError("semantic projection root must be a mapping")
    plain = plain_json_value(pack)
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


def serialize_pack(
    pack: Mapping[str, object] | object,
    *,
    canonicalization: str = CANONICALIZATION,
) -> bytes:
    """Validate and encode a complete Annotation Pack document.

    The local import keeps the lower-level canonical JSON primitives reusable by
    the semantic validator without a module-import cycle.  Empty documents are
    structurally serializable here; whether publishing an empty track is allowed
    remains an explicit exporter policy.
    """

    if canonicalization != CANONICALIZATION:
        raise CanonicalJsonError("unsupported Annotation Pack canonicalization")
    document: object = pack
    if not isinstance(document, Mapping):
        try:
            model_dump = getattr(document, "model_dump", None)
        except Exception:
            raise CanonicalJsonError(
                "Annotation Pack wire model could not be read safely"
            ) from None
        if not callable(model_dump):
            raise CanonicalJsonError("Annotation Pack must be a mapping or wire model")
        try:
            document = model_dump(by_alias=True, exclude_none=True)
        except Exception:
            raise CanonicalJsonError(
                "Annotation Pack wire model could not be read safely"
            ) from None
    if not isinstance(document, Mapping):
        raise CanonicalJsonError("Annotation Pack wire model did not produce an object")

    try:
        snapshot_bytes = canonical_json_bytes(document)
        snapshot = json.loads(snapshot_bytes)
    except Exception:
        raise CanonicalJsonError(
            "Annotation Pack could not be snapshotted safely"
        ) from None
    if not isinstance(snapshot, dict):  # pragma: no cover - Mapping root above
        raise CanonicalJsonError("Annotation Pack snapshot did not produce an object")

    from src.annotation_pack.validation import ValidationContext, validate_pack

    result = validate_pack(
        snapshot,
        context=ValidationContext(allow_empty=True),
    )
    if not result.publishable:
        raise CanonicalJsonError(
            "Annotation Pack failed schema or semantic validation"
        )
    return snapshot_bytes
