"""Strict schema and semantic validation for Reading Product Output v1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from functools import lru_cache
from importlib import resources
import re
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker

from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_core.source_ranges import (
    SourceCoordinate,
    SourceRangeValidationError,
    validate_book_document_source_range,
)

from .models import (
    CompletionEvidence,
    ProductFinding,
    ProductMarginalia,
    ProductUnit,
    ReadingProductDocument,
    SourceIdentity,
)
from .serialization import document_to_wire


SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/reading-product/v1/"
    "reading-product-output.schema.json"
)
POINTER_SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/reading-product/v1/"
    "publication-pointer.schema.json"
)
REPORT_SCHEMA_ID = (
    "https://captain4whale.github.io/second-reader/schema/reading-product/v1/"
    "validation-report.schema.json"
)
VALIDATOR_VERSION = "1.0.0"
MAX_TEXT_CODE_POINTS = 262_144
MAX_BODY_CODE_POINTS = 16_384
MAX_QUOTE_CODE_POINTS = 1_024

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_UNIT_ID = re.compile(r"u([0-9]{6})\Z", re.ASCII)
_MARGINALIA_ID = re.compile(r"(u[0-9]{6})-m([0-9]{3})\Z", re.ASCII)
_UTC_SECONDS = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z",
    re.ASCII,
)


class ReadingProductValidationError(ValueError):
    """One stable, sanitized validation failure."""

    __slots__ = ("code", "json_pointer", "finding")

    def __init__(
        self,
        code: str,
        message: str,
        *,
        json_pointer: str | None = None,
        unit_id: str | None = None,
        marginalia_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.json_pointer = json_pointer
        self.finding = ProductFinding(
            code=code,
            severity="error",
            message=message,
            unit_id=unit_id,
            marginalia_id=marginalia_id,
            json_pointer=json_pointer,
        )


_SCHEMA_FILES = {
    SCHEMA_ID: "reading-product-output.schema.json",
    POINTER_SCHEMA_ID: "publication-pointer.schema.json",
    REPORT_SCHEMA_ID: "validation-report.schema.json",
}


@lru_cache(maxsize=len(_SCHEMA_FILES))
def load_schema(schema_id: str = SCHEMA_ID) -> Mapping[str, Any]:
    import json

    try:
        filename = _SCHEMA_FILES[schema_id]
    except KeyError:
        raise ValueError("unsupported Reading Product schema id") from None
    content = (
        resources.files("src.reading_product.resources")
        .joinpath(filename)
        .read_bytes()
    )
    value = json.loads(content)
    if not isinstance(value, Mapping) or value.get("$id") != schema_id:
        raise RuntimeError("Reading Product runtime schema copy is invalid")
    return value


def schema_validator() -> Draft202012Validator:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def auxiliary_validator(schema_id: str) -> Draft202012Validator:
    if schema_id == SCHEMA_ID:
        raise ValueError("use schema_validator for the Reading Product wire")
    schema = load_schema(schema_id)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def parse_utc_seconds(value: str) -> datetime:
    if type(value) is not str or _UTC_SECONDS.fullmatch(value) is None:
        _fail("invalid_timestamp", "timestamp must be second-precision UTC Z")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        _fail("invalid_timestamp", "timestamp is not a valid UTC date-time")
    return parsed


def validate_source_identity(
    source: SourceIdentity,
    *,
    book_document: Mapping[str, object] | None = None,
) -> None:
    if not isinstance(source, SourceIdentity):
        _fail("invalid_source_identity", "source identity is malformed")
    if _SHA256.fullmatch(source.epub_sha256) is None or _SHA256.fullmatch(
        source.book_document_substrate_sha256
    ) is None:
        _fail("invalid_source_identity", "source identity digests are invalid")
    if book_document is not None:
        try:
            actual = book_document_substrate_digest(book_document)
        except Exception:
            _fail(
                "invalid_book_document",
                "canonical BookDocument could not be fingerprinted",
            )
        if actual != source.book_document_substrate_sha256:
            _fail(
                "source_identity_mismatch",
                "canonical BookDocument does not match the Reading Product source",
            )


def validate_unit(
    unit: ProductUnit,
    *,
    book_document: Mapping[str, object],
) -> None:
    if not isinstance(unit, ProductUnit):
        _fail("invalid_unit", "Reading Product Unit is malformed")
    match = _UNIT_ID.fullmatch(unit.unit_id) if type(unit.unit_id) is str else None
    if match is None or type(unit.sequence_index) is not int:
        _fail("invalid_unit_identity", "Unit identity is invalid")
    if not 1 <= unit.sequence_index <= 999_999:
        _fail("invalid_unit_identity", "Unit sequence is out of range")
    if unit.unit_id != f"u{unit.sequence_index:06d}":
        _fail("invalid_unit_identity", "Unit id does not match its sequence")
    parse_utc_seconds(unit.settled_at)
    _non_blank(unit.understanding, "understanding", MAX_TEXT_CODE_POINTS)
    _non_blank(unit.response, "response", MAX_TEXT_CODE_POINTS)
    try:
        validate_book_document_source_range(
            book_document,
            unit.source_range,
            require_single_resource=False,
        )
    except SourceRangeValidationError as exc:
        _fail(exc.code, str(exc), unit_id=unit.unit_id, json_pointer="/source_range")
    if len(unit.marginalia) > 999:
        _fail("too_many_marginalia", "Unit has too many marginalia")
    seen_ids: set[str] = set()
    seen_semantics: set[tuple[object, ...]] = set()
    prior_ordinal = 0
    for item in unit.marginalia:
        _validate_marginalia(
            item,
            unit=unit,
            book_document=book_document,
        )
        if item.marginalia_id in seen_ids:
            _fail(
                "duplicate_marginalia",
                "Marginalia ids must be unique",
                unit_id=unit.unit_id,
                marginalia_id=item.marginalia_id,
            )
        seen_ids.add(item.marginalia_id)
        ordinal = int(_MARGINALIA_ID.fullmatch(item.marginalia_id).group(2))  # type: ignore[union-attr]
        if ordinal <= prior_ordinal:
            _fail(
                "marginalia_order_invalid",
                "Marginalia ids must preserve candidate order",
                unit_id=unit.unit_id,
                marginalia_id=item.marginalia_id,
            )
        prior_ordinal = ordinal
        semantic = (
            item.kind,
            item.source_range,
            item.source_quote,
            item.body_text,
        )
        if semantic in seen_semantics:
            _fail(
                "duplicate_marginalia",
                "Semantic duplicate marginalia are not allowed",
                unit_id=unit.unit_id,
                marginalia_id=item.marginalia_id,
            )
        seen_semantics.add(semantic)


def validate_document(
    document: ReadingProductDocument,
    *,
    book_document: Mapping[str, object] | None = None,
) -> None:
    if not isinstance(document, ReadingProductDocument):
        _fail("invalid_reading_product", "Reading Product document is malformed")
    if document.schema_version != "reading-product-output/1.0":
        _fail("unsupported_schema_version", "Reading Product schema version is unsupported")
    _validate_reading_id(document.reading_id)
    if document.status not in {"partial", "complete"}:
        _fail("invalid_status", "Reading Product status is invalid")
    validate_source_identity(document.source, book_document=book_document)
    started_at = parse_utc_seconds(document.started_at)
    if document.status == "partial" and document.completed_at is not None:
        _fail("invalid_completion_state", "partial Reading Product cannot be completed")
    if document.status == "complete":
        if document.completed_at is None:
            _fail("invalid_completion_state", "complete Reading Product needs completed_at")
        if not document.units:
            _fail("empty_complete_product", "complete Reading Product needs at least one Unit")
    completed_at = (
        parse_utc_seconds(document.completed_at)
        if document.completed_at is not None
        else None
    )
    if completed_at is not None and completed_at < started_at:
        _fail("invalid_completion_state", "completed_at precedes started_at")
    if len(document.units) > 999_999:
        _fail("too_many_units", "Reading Product has too many Units")

    prior_units: list[ProductUnit] = []
    prior_settled = started_at
    for expected_sequence, unit in enumerate(document.units, start=1):
        if unit.sequence_index != expected_sequence:
            _fail("unit_sequence_gap", "Unit sequence must be contiguous")
        settled_at = parse_utc_seconds(unit.settled_at)
        if settled_at < prior_settled:
            _fail("unit_time_order_invalid", "Unit settlement times must be monotonic")
        if completed_at is not None and settled_at > completed_at:
            _fail("invalid_completion_state", "Unit settled after product completion")
        prior_settled = settled_at
        if book_document is not None:
            validate_unit(unit, book_document=book_document)
            if any(not _units_disjoint(previous, unit) for previous in prior_units):
                _fail("unit_range_overlap", "Product Unit ranges overlap or regress")
        prior_units.append(unit)

    wire = document_to_wire(document)
    errors = sorted(schema_validator().iter_errors(wire), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        pointer = "".join(f"/{part}" for part in first.absolute_path) or ""
        _fail(
            "schema_validation_failed",
            "Reading Product failed the strict v1 schema",
            json_pointer=pointer,
        )


def validate_completion_evidence(
    evidence: CompletionEvidence,
    *,
    units: Sequence[ProductUnit],
) -> None:
    if not isinstance(evidence, CompletionEvidence):
        _fail("invalid_completion_evidence", "completion evidence is malformed")
    if evidence.scope != "whole_book" or evidence.chapter_number is not None:
        _fail(
            "incomplete_reading_scope",
            "only an unbounded whole-book run can be finalized",
        )
    if not evidence.reading_plan_complete:
        _fail("reading_plan_incomplete", "approved reading plan is incomplete")
    if evidence.audit_window_stop_reason:
        _fail("audit_window_stopped", "audit window stopped before whole-book completion")
    scheduled = _strict_chapter_ids(evidence.scheduled_chapter_ids)
    completed = _strict_chapter_ids(evidence.completed_chapter_ids)
    if not scheduled or scheduled != completed:
        _fail(
            "scheduled_chapters_incomplete",
            "scheduled and completed chapters do not prove whole-book completion",
        )
    represented = {unit.source_range.start.chapter_id for unit in units}
    if not scheduled.issubset(represented):
        _fail("scheduled_chapters_missing", "one or more scheduled chapters have no Unit")


def _validate_marginalia(
    item: ProductMarginalia,
    *,
    unit: ProductUnit,
    book_document: Mapping[str, object],
) -> None:
    if not isinstance(item, ProductMarginalia):
        _fail("invalid_marginalia", "Marginalia is malformed", unit_id=unit.unit_id)
    match = (
        _MARGINALIA_ID.fullmatch(item.marginalia_id)
        if type(item.marginalia_id) is str
        else None
    )
    if match is None or match.group(1) != unit.unit_id or int(match.group(2)) < 1:
        _fail(
            "invalid_marginalia_identity",
            "Marginalia id is invalid for its Unit",
            unit_id=unit.unit_id,
        )
    _non_blank(item.source_quote, "source_quote", MAX_QUOTE_CODE_POINTS)
    if item.kind == "highlight":
        if item.body_text is not None:
            _fail(
                "invalid_marginalia_body",
                "Highlight must not contain body_text",
                unit_id=unit.unit_id,
                marginalia_id=item.marginalia_id,
            )
    elif item.kind == "note":
        _non_blank(item.body_text, "body_text", MAX_BODY_CODE_POINTS)
    else:
        _fail(
            "invalid_marginalia_kind",
            "Marginalia kind is invalid",
            unit_id=unit.unit_id,
            marginalia_id=item.marginalia_id,
        )
    try:
        validate_book_document_source_range(
            book_document,
            item.source_range,
            expected_quote=item.source_quote,
            within=unit.source_range,
            require_single_resource=True,
            maximum_quote_code_points=MAX_QUOTE_CODE_POINTS,
        )
    except SourceRangeValidationError as exc:
        _fail(
            exc.code,
            str(exc),
            unit_id=unit.unit_id,
            marginalia_id=item.marginalia_id,
            json_pointer="/source_range",
        )


def _validate_reading_id(value: str) -> None:
    if type(value) is not str or not value.startswith("urn:uuid:"):
        _fail("invalid_reading_id", "reading_id must be a UUIDv4 URN")
    try:
        parsed = UUID(value.removeprefix("urn:uuid:"))
    except (ValueError, AttributeError):
        _fail("invalid_reading_id", "reading_id must be a UUIDv4 URN")
    if parsed.version != 4 or value != f"urn:uuid:{parsed}":
        _fail("invalid_reading_id", "reading_id must be a lowercase UUIDv4 URN")


def _non_blank(value: object, field: str, maximum: int) -> str:
    if type(value) is not str or not value or not value.strip() or len(value) > maximum:
        _fail("invalid_text_field", f"{field} must be non-blank and within its limit")
    return value


def _strict_chapter_ids(values: object) -> set[int]:
    if not isinstance(values, tuple) or any(
        type(value) is not int or value < 1 for value in values
    ):
        _fail("invalid_completion_evidence", "chapter id evidence is invalid")
    if len(values) != len(set(values)):
        _fail("invalid_completion_evidence", "chapter id evidence has duplicates")
    return set(values)


def _units_disjoint(left: ProductUnit, right: ProductUnit) -> bool:
    """Allow reading-plan order while forbidding actual source intersection."""

    if left.source_range.start.chapter_id != right.source_range.start.chapter_id:
        return True
    left_start = _paragraph_coordinate_key(left.source_range.start)
    left_end = _paragraph_coordinate_key(left.source_range.end)
    right_start = _paragraph_coordinate_key(right.source_range.start)
    right_end = _paragraph_coordinate_key(right.source_range.end)
    return left_end <= right_start or right_end <= left_start


def _paragraph_coordinate_key(value: SourceCoordinate) -> tuple[int, int]:
    return value.paragraph_index, value.char_offset


def _fail(
    code: str,
    message: str,
    *,
    json_pointer: str | None = None,
    unit_id: str | None = None,
    marginalia_id: str | None = None,
) -> Any:
    raise ReadingProductValidationError(
        code,
        message,
        json_pointer=json_pointer,
        unit_id=unit_id,
        marginalia_id=marginalia_id,
    )


__all__ = [
    "MAX_BODY_CODE_POINTS",
    "MAX_QUOTE_CODE_POINTS",
    "MAX_TEXT_CODE_POINTS",
    "POINTER_SCHEMA_ID",
    "REPORT_SCHEMA_ID",
    "ReadingProductValidationError",
    "SCHEMA_ID",
    "VALIDATOR_VERSION",
    "parse_utc_seconds",
    "auxiliary_validator",
    "load_schema",
    "schema_validator",
    "validate_completion_evidence",
    "validate_document",
    "validate_source_identity",
    "validate_unit",
]
