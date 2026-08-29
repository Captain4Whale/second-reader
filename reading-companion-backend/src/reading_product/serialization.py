"""Strict wire conversion and canonical serialization for Reading Product v1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from typing import Any, cast

from src.reading_core.canonical_json import canonical_json_bytes
from src.reading_core.source_ranges import (
    source_range_from_wire,
    source_range_to_wire,
)

from .models import (
    ProductFinding,
    ProductMarginalia,
    ProductUnit,
    ReadingProductDocument,
    SourceIdentity,
)


def source_identity_to_wire(source: SourceIdentity) -> dict[str, str]:
    return {
        "epub_sha256": source.epub_sha256,
        "book_document_substrate_sha256": source.book_document_substrate_sha256,
    }


def marginalia_to_wire(value: ProductMarginalia) -> dict[str, object]:
    result: dict[str, object] = {
        "marginalia_id": value.marginalia_id,
        "kind": value.kind,
        "source_range": source_range_to_wire(value.source_range),
        "source_quote": value.source_quote,
    }
    if value.body_text is not None:
        result["body_text"] = value.body_text
    return result


def unit_to_wire(value: ProductUnit) -> dict[str, object]:
    return {
        "unit_id": value.unit_id,
        "sequence_index": value.sequence_index,
        "source_range": source_range_to_wire(value.source_range),
        "settled_at": value.settled_at,
        "understanding": value.understanding,
        "response": value.response,
        "marginalia": [marginalia_to_wire(item) for item in value.marginalia],
    }


def document_to_wire(value: ReadingProductDocument) -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": value.schema_version,
        "reading_id": value.reading_id,
        "status": value.status,
        "source": source_identity_to_wire(value.source),
        "started_at": value.started_at,
        "units": [unit_to_wire(unit) for unit in value.units],
    }
    if value.completed_at is not None:
        result["completed_at"] = value.completed_at
    return result


def finding_to_wire(value: ProductFinding) -> dict[str, object]:
    result: dict[str, object] = {
        "code": value.code,
        "severity": value.severity,
        "message": value.message,
    }
    for key in ("unit_id", "marginalia_id", "json_pointer"):
        item = getattr(value, key)
        if item is not None:
            result[key] = item
    return result


def product_unit_from_wire(value: object) -> ProductUnit:
    mapping = _mapping(value, "unit")
    _exact_keys(
        mapping,
        required={
            "unit_id",
            "sequence_index",
            "source_range",
            "settled_at",
            "understanding",
            "response",
            "marginalia",
        },
    )
    marginalia = _sequence(mapping["marginalia"], "marginalia")
    return ProductUnit(
        unit_id=_exact_string(mapping["unit_id"], "unit_id"),
        sequence_index=_exact_integer(mapping["sequence_index"], "sequence_index"),
        source_range=source_range_from_wire(mapping["source_range"]),
        settled_at=_exact_string(mapping["settled_at"], "settled_at"),
        understanding=_exact_string(mapping["understanding"], "understanding"),
        response=_exact_string(mapping["response"], "response"),
        marginalia=tuple(_marginalia_from_wire(item) for item in marginalia),
    )


def document_from_wire(value: object) -> ReadingProductDocument:
    mapping = _mapping(value, "Reading Product")
    _exact_keys(
        mapping,
        required={
            "schema_version",
            "reading_id",
            "status",
            "source",
            "started_at",
            "units",
        },
        optional={"completed_at"},
    )
    source = _mapping(mapping["source"], "source")
    _exact_keys(
        source,
        required={"epub_sha256", "book_document_substrate_sha256"},
    )
    units = _sequence(mapping["units"], "units")
    status = _exact_string(mapping["status"], "status")
    if status not in {"partial", "complete"}:
        raise ValueError("invalid Reading Product status")
    return ReadingProductDocument(
        schema_version=_exact_string(mapping["schema_version"], "schema_version"),
        reading_id=_exact_string(mapping["reading_id"], "reading_id"),
        status=cast(Any, status),
        source=SourceIdentity(
            epub_sha256=_exact_string(source["epub_sha256"], "epub_sha256"),
            book_document_substrate_sha256=_exact_string(
                source["book_document_substrate_sha256"],
                "book_document_substrate_sha256",
            ),
        ),
        started_at=_exact_string(mapping["started_at"], "started_at"),
        completed_at=(
            _exact_string(mapping["completed_at"], "completed_at")
            if "completed_at" in mapping
            else None
        ),
        units=tuple(product_unit_from_wire(item) for item in units),
    )


def serialize_document(
    value: ReadingProductDocument,
    *,
    book_document: Mapping[str, object] | None = None,
) -> bytes:
    from .validation import validate_document

    validate_document(value, book_document=book_document)
    return canonical_json_bytes(document_to_wire(value))


def load_document_bytes(content: bytes) -> ReadingProductDocument:
    try:
        raw = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Reading Product JSON is invalid") from None
    return document_from_wire(raw)


def _marginalia_from_wire(value: object) -> ProductMarginalia:
    mapping = _mapping(value, "marginalia")
    _exact_keys(
        mapping,
        required={"marginalia_id", "kind", "source_range", "source_quote"},
        optional={"body_text"},
    )
    kind = _exact_string(mapping["kind"], "kind")
    if kind not in {"highlight", "note"}:
        raise ValueError("invalid marginalia kind")
    return ProductMarginalia(
        marginalia_id=_exact_string(mapping["marginalia_id"], "marginalia_id"),
        kind=cast(Any, kind),
        source_range=source_range_from_wire(mapping["source_range"]),
        source_quote=_exact_string(mapping["source_quote"], "source_quote"),
        body_text=(
            _exact_string(mapping["body_text"], "body_text")
            if "body_text" in mapping
            else None
        ),
    )


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{name} must be an object")
    return value


def _sequence(value: object, name: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{name} must be an array")
    return value


def _exact_keys(
    value: Mapping[str, object],
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    allowed = required | (optional or set())
    if set(value) - allowed or required - set(value):
        raise ValueError("object fields do not match Reading Product v1")


def _exact_string(value: object, name: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} must be a string")
    return value


def _exact_integer(value: object, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return value


__all__ = [
    "document_from_wire",
    "document_to_wire",
    "finding_to_wire",
    "load_document_bytes",
    "marginalia_to_wire",
    "product_unit_from_wire",
    "serialize_document",
    "source_identity_to_wire",
    "unit_to_wire",
]
