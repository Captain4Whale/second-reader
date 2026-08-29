#!/usr/bin/env python3
"""Validate the canonical Reading Product v1 contract without network access."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract" / "reading-product" / "v1"
SCHEMAS = CONTRACT / "schema"
EXAMPLES = CONTRACT / "examples"
WIRE_SCHEMA = SCHEMAS / "reading-product-output.schema.json"
RUNTIME_SCHEMA = (
    ROOT
    / "reading-companion-backend"
    / "src"
    / "reading_product"
    / "resources"
    / "reading-product-output.schema.json"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path.relative_to(ROOT)}")
    return value


def _validator(schema: Mapping[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _coordinate_key(value: Mapping[str, Any]) -> tuple[int, int, int]:
    return (
        int(value["chapter_id"]),
        int(value["paragraph_index"]),
        int(value["char_offset"]),
    )


def _range_key(value: Mapping[str, Any]) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    return _coordinate_key(value["start"]), _coordinate_key(value["end"])


def _require_valid_range(value: Mapping[str, Any], *, label: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    start, end = _range_key(value)
    if start[0] != end[0]:
        raise ValueError(f"{label} crosses chapters")
    if start >= end:
        raise ValueError(f"{label} is empty or reversed")
    return start, end


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_semantics(document: Mapping[str, Any]) -> None:
    """Check invariants that JSON Schema cannot compare across fields."""

    units = document["units"]
    started_at = _parse_time(str(document["started_at"]))
    completed_at = (
        _parse_time(str(document["completed_at"]))
        if document["status"] == "complete"
        else None
    )
    if completed_at is not None and completed_at < started_at:
        raise ValueError("completed_at precedes started_at")

    prior_unit_end: tuple[int, int, int] | None = None
    seen_unit_ranges: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()
    for expected_sequence, unit in enumerate(units, start=1):
        if unit["sequence_index"] != expected_sequence:
            raise ValueError("Unit sequence_index is not contiguous and one-based")
        expected_unit_id = f"u{expected_sequence:06d}"
        if unit["unit_id"] != expected_unit_id:
            raise ValueError("unit_id does not match sequence_index")
        unit_start, unit_end = _require_valid_range(
            unit["source_range"], label=expected_unit_id
        )
        unit_range = unit_start, unit_end
        if unit_range in seen_unit_ranges:
            raise ValueError("duplicate Unit source range")
        seen_unit_ranges.add(unit_range)
        if prior_unit_end is not None and unit_start < prior_unit_end:
            raise ValueError("Unit ranges overlap or are not in source order")
        prior_unit_end = unit_end

        settled_at = _parse_time(str(unit["settled_at"]))
        if settled_at < started_at:
            raise ValueError("Unit settled_at precedes started_at")
        if completed_at is not None and settled_at > completed_at:
            raise ValueError("Unit settled_at follows completed_at")

        seen_semantics: set[tuple[Any, ...]] = set()
        for expected_item, item in enumerate(unit["marginalia"], start=1):
            expected_item_id = f"{expected_unit_id}-m{expected_item:03d}"
            if item["marginalia_id"] != expected_item_id:
                raise ValueError("marginalia_id is not contiguous within its Unit")
            item_start, item_end = _require_valid_range(
                item["source_range"], label=expected_item_id
            )
            if item_start < unit_start or item_end > unit_end:
                raise ValueError("Marginalia range is outside its Unit")
            semantic_key = (
                item["kind"],
                item_start,
                item_end,
                item["source_quote"],
                item.get("body_text"),
            )
            if semantic_key in seen_semantics:
                raise ValueError("duplicate Marginalia semantics within one Unit")
            seen_semantics.add(semantic_key)


def _expect_schema_failure(
    validator: Draft202012Validator, document: Mapping[str, Any], *, label: str
) -> None:
    try:
        validator.validate(document)
    except ValidationError:
        return
    raise AssertionError(f"negative schema case unexpectedly passed: {label}")


def _expect_semantic_failure(document: Mapping[str, Any], *, label: str) -> None:
    try:
        validate_semantics(document)
    except ValueError:
        return
    raise AssertionError(f"negative semantic case unexpectedly passed: {label}")


def _check_negative_cases(
    validator: Draft202012Validator, complete: dict[str, Any], partial: dict[str, Any]
) -> None:
    case = deepcopy(complete)
    case["provider"] = "private"
    _expect_schema_failure(validator, case, label="private root field")

    case = deepcopy(partial)
    case["completed_at"] = "2026-08-29T01:02:00Z"
    _expect_schema_failure(validator, case, label="partial completed_at")

    case = deepcopy(complete)
    del case["completed_at"]
    _expect_schema_failure(validator, case, label="complete without completed_at")

    case = deepcopy(complete)
    case["units"][0]["marginalia"][0]["body_text"] = "not allowed"
    _expect_schema_failure(validator, case, label="Highlight body")

    case = deepcopy(complete)
    del case["units"][1]["marginalia"][0]["body_text"]
    _expect_schema_failure(validator, case, label="Note without body")

    case = deepcopy(complete)
    case["units"][0]["understanding"] = "  \n  "
    _expect_schema_failure(validator, case, label="blank understanding")

    case = deepcopy(complete)
    case["reading_id"] = "urn:uuid:d012c503-1480-55d5-8490-cc9e984f95ba"
    _expect_schema_failure(validator, case, label="non-v4 reading_id")

    case = deepcopy(complete)
    case["units"][0]["marginalia"][0]["source_quote"] = "x" * 1025
    _expect_schema_failure(validator, case, label="Pack-ineligible source quote")

    case = deepcopy(complete)
    case["units"][1]["sequence_index"] = 3
    _expect_semantic_failure(case, label="Unit sequence gap")

    case = deepcopy(complete)
    case["units"][1]["source_range"] = deepcopy(case["units"][0]["source_range"])
    _expect_semantic_failure(case, label="overlapping Units")

    case = deepcopy(complete)
    case["units"][0]["marginalia"][0]["source_range"]["end"]["paragraph_index"] = 3
    _expect_semantic_failure(case, label="Marginalia outside Unit")

    case = deepcopy(complete)
    duplicate = deepcopy(case["units"][0]["marginalia"][0])
    duplicate["marginalia_id"] = "u000001-m002"
    case["units"][0]["marginalia"].append(duplicate)
    _expect_semantic_failure(case, label="duplicate Marginalia semantics")


def _check_auxiliary_schemas() -> None:
    pointer_schema = _load(SCHEMAS / "publication-pointer.schema.json")
    report_schema = _load(SCHEMAS / "validation-report.schema.json")
    for schema in (pointer_schema, report_schema):
        Draft202012Validator.check_schema(schema)

    digest = "a" * 64
    reading_id = "urn:uuid:1f44d3e4-3518-4e16-8fb1-53dcff7aa8d4"
    _validator(pointer_schema).validate(
        {
            "schema_version": "reading-product-publication-pointer/1.0",
            "reading_id": reading_id,
            "revision_id": digest,
            "reading_product": f"revisions/{digest}/reading-product.json",
            "reading_product_sha256": digest,
            "validation_report": f"revisions/{digest}/validation-report.json",
            "validation_report_sha256": "b" * 64,
        }
    )
    _validator(report_schema).validate(
        {
            "schema_version": "reading-product-validation-report/1.0",
            "validator_version": "1.0.0",
            "status": "valid",
            "reading_id": reading_id,
            "reading_product_sha256": digest,
            "source": {
                "epub_sha256": "c" * 64,
                "book_document_substrate_sha256": "d" * 64,
            },
            "counts": {
                "units": 2,
                "marginalia": 2,
                "rejected_marginalia": 0,
                "errors": 0,
            },
            "findings": [],
        }
    )


def main() -> int:
    schema = _load(WIRE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = _validator(schema)

    examples: dict[str, dict[str, Any]] = {}
    for path in sorted(EXAMPLES.glob("*.json")):
        document = _load(path)
        validator.validate(document)
        validate_semantics(document)
        examples[path.name] = document
    expected_examples = {
        "complete-reading-product.json",
        "partial-reading-product.json",
    }
    if set(examples) != expected_examples:
        raise ValueError(
            f"Reading Product example allowlist mismatch: {sorted(examples)}"
        )

    _check_negative_cases(
        validator,
        examples["complete-reading-product.json"],
        examples["partial-reading-product.json"],
    )
    _check_auxiliary_schemas()

    if not RUNTIME_SCHEMA.is_file():
        raise ValueError(
            "missing checked runtime schema copy: "
            f"{RUNTIME_SCHEMA.relative_to(ROOT)}"
        )
    if RUNTIME_SCHEMA.read_bytes() != WIRE_SCHEMA.read_bytes():
        raise ValueError("Reading Product runtime schema copy differs from authority")

    print(
        "Reading Product v1 contract is valid: "
        f"schemas=3 examples={len(examples)} negative_cases=12 runtime_copy=ok"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
