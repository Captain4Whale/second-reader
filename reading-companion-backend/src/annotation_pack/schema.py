"""Offline access to the canonical Annotation Pack contract resources."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from importlib import resources
import json
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker


SPEC_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"
ANNOTATION_PACK_SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/"
    "annotation-pack.schema.json"
)
PUBLICATION_POINTER_SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/"
    "publication-pointer.schema.json"
)
VALIDATION_REPORT_SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/"
    "validation-report.schema.json"
)
ANNOTATION_CONTEXT_SHA256 = (
    "eb72eb498c4bb70360ed57d6f97a85ead6985b9c88921124dfb27e37f3400f70"
)
ANNOTATION_NAMESPACE = (
    "https://captain4whale.github.io/second-reader/ns/annotation-pack#"
)
_RESOURCE_PACKAGE = f"{__package__}.resources"
_CONTEXT_FILE = "second-reader-annotation-context.jsonld"
_SCHEMA_FILES = {
    ANNOTATION_PACK_SCHEMA_ID: "annotation-pack.schema.json",
    PUBLICATION_POINTER_SCHEMA_ID: "publication-pointer.schema.json",
    VALIDATION_REPORT_SCHEMA_ID: "validation-report.schema.json",
}
_FINDING_SEVERITY_RANK = {
    "fatal": 0,
    "error": 1,
    "skipped": 2,
    "warning": 3,
}


@lru_cache(maxsize=len(_SCHEMA_FILES) + 1)
def _load_resource_bytes(filename: str) -> bytes:
    """Read an immutable packaged resource in directories and ZIP imports."""

    return resources.files(_RESOURCE_PACKAGE).joinpath(filename).read_bytes()


def _schema_filename(schema_id: str) -> str:
    try:
        return _SCHEMA_FILES[schema_id]
    except KeyError as exc:
        raise ValueError(f"unsupported Annotation Pack schema id: {schema_id}") from exc


def load_schema(schema_id: str = ANNOTATION_PACK_SCHEMA_ID) -> Mapping[str, Any]:
    """Load a fresh schema document from committed offline package bytes.

    Returning a fresh JSON object keeps caller mutation from weakening validators
    created elsewhere in the same process.
    """

    filename = _schema_filename(schema_id)
    document = json.loads(_load_resource_bytes(filename))
    if document.get("$id") != schema_id:
        raise ValueError(f"runtime schema id mismatch: {filename}")
    return document


def load_context() -> Mapping[str, Any]:
    """Load and integrity-check the pinned offline JSON-LD context."""

    content = _load_resource_bytes(_CONTEXT_FILE)
    actual_digest = hashlib.sha256(content).hexdigest()
    if actual_digest != ANNOTATION_CONTEXT_SHA256:
        raise ValueError(
            "runtime Annotation Pack context digest mismatch: "
            f"expected {ANNOTATION_CONTEXT_SHA256}, found {actual_digest}"
        )
    document = json.loads(content)
    expected_context = {
        "@protected": True,
        "sr": {"@id": ANNOTATION_NAMESPACE, "@prefix": True},
    }
    if document != {"@context": expected_context}:
        raise ValueError("runtime Annotation Pack context mapping mismatch")
    return document


def pack_validator() -> Draft202012Validator:
    """Return an isolated Pack validator with real IRI/date-time checks."""

    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def annotation_validator() -> Draft202012Validator:
    """Return a local validator for the contract's Annotation item examples."""

    pack_schema = load_schema()
    item_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": pack_schema["$defs"],
        "$ref": "#/$defs/annotation",
    }
    return Draft202012Validator(item_schema, format_checker=FormatChecker())


def auxiliary_validator(schema_id: str) -> Draft202012Validator:
    if schema_id == ANNOTATION_PACK_SCHEMA_ID:
        raise ValueError("use pack_validator() for the Pack wire schema")
    schema = load_schema(schema_id)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validation_report_finding_sort_key(
    finding: Mapping[str, Any],
) -> tuple[int, str, int, str, str, str, str]:
    """Return the protocol-defined deterministic finding order key."""

    return (
        _FINDING_SEVERITY_RANK[str(finding["severity"])],
        str(finding["code"]),
        finding.get("source_record_index")
        if finding.get("source_record_index") is not None
        else -1,
        str(finding.get("json_pointer") or ""),
        str(finding.get("annotation_id") or ""),
        str(finding.get("source_record_digest") or ""),
        str(finding["message"]),
    )
