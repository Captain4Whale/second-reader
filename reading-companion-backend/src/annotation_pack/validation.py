"""Pure schema, semantic, extension, and privacy validation for Pack v0.

The validator deliberately operates on the public JSON-shaped document.  It
does not read an EPUB, inspect runtime state, repair producer data, dereference
JSON-LD contexts, or write reports.  Source/export/package failures can enter a
result only through the small, producer-neutral :class:`ValidationContext`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
import ipaddress
import re
from typing import Any, Literal, TypeAlias
import unicodedata
from urllib.parse import urlsplit

from src.annotation_pack.drafts import ValidationFinding
from src.annotation_pack.epub_source import (
    decode_public_scan_value,
    is_public_display_metadata,
    normalize_epub_href,
)
from src.annotation_pack.ids import (
    annotation_id,
    pack_id,
)
from src.annotation_pack.schema import (
    VALIDATION_REPORT_SCHEMA_ID,
    auxiliary_validator,
    load_schema,
    pack_validator,
    validation_report_finding_sort_key,
)
from src.annotation_pack.serialization import (
    CanonicalJsonError,
    canonical_json_bytes,
    semantic_digest,
)


ValidationMode = Literal["strict"]
ValidationStatus = Literal["valid", "degraded", "failed"]
JSONScalar: TypeAlias = None | bool | int | str
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

VALIDATION_RESULT_SCHEMA_VERSION = "annotation-pack-validation-result/0.1"
VALIDATION_REPORT_SCHEMA_VERSION = "annotation-pack-validation-report/0.1"
VALIDATOR_VERSION = "0.1.0"
VALIDATION_REPORT_CANONICALIZATION = "sr-annotation-validation-report-json-v1"

MAX_DOCUMENT_DEPTH = 64
MAX_DOCUMENT_NODES = 100_000
MAX_DOCUMENT_STRING_CODE_POINTS = 16 * 1024 * 1024
MAX_SINGLE_STRING_CODE_POINTS = 1024 * 1024
MAX_SCHEMA_FINDINGS = 256
MAX_EXTENSION_DEPTH = 16
MAX_EXTENSION_NODES = 2048
MAX_EXTENSION_STRING_CODE_POINTS = 65_536

_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_SEMVER_RE = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\Z"
)
_CODE_RE = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")
_UUID5_URN_RE = re.compile(
    r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
)
_JSON_POINTER_RE = re.compile(r"(?:/(?:[^~/]|~0|~1)*)*\Z")
_PREFIX_RE = re.compile(r"[A-Za-z][A-Za-z0-9._-]*\Z")
_CURIE_RE = re.compile(r"(?P<prefix>[A-Za-z][A-Za-z0-9._-]*):[A-Za-z][A-Za-z0-9._-]*\Z")
_WINDOWS_PATH_RE = re.compile(r"(?i)(?:^|[\s\"'])(?:[a-z]:[\\/]|\\\\[^\\/\s]+[\\/])")
_POSIX_PRIVATE_PATH_RE = re.compile(r"(?:^|[\s\"'])/(?!/)[^\s\"']+")
_FILE_SCHEME_RE = re.compile(r"(?i)(?:^|[\s\"'])file\s*:")
_HOME_PATH_RE = re.compile(r"(?:^|[\s\"'])~(?:/|\\)")
_SECRET_QUERY_RE = re.compile(
    r"(?i)[?&](?:access[_-]?token|api[_-]?key|token|secret|password|credential)="
)
_LEGACY_IPV4_HOST_RE = re.compile(
    r"(?:0[xX][0-9A-Fa-f]+|[0-9]+)(?:\.(?:0[xX][0-9A-Fa-f]+|[0-9]+)){0,3}\Z"
)
_DNS_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
_UNICODE_DOT_TRANSLATION = str.maketrans({"\u3002": ".", "\uff0e": ".", "\uff61": "."})
_EMBEDDED_AUTHORITY_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9+.-])"
    r"(?P<scheme>[A-Za-z][A-Za-z0-9+.-]{0,31})://"
    r"(?P<authority>[^\s/?#<>{}\"']{1,512})"
)
_EMBEDDED_URL_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]{0,31}://[^\s<>{}\"']+"
)
_CFI_STEP_RE = re.compile(r"[1-9][0-9]{0,9}\Z")
_CFI_OFFSET_RE = re.compile(r"(?:0|[1-9][0-9]{0,9})\Z")
_CFI_MAX_STEPS = 256
_CFI_MAX_ASSERTION_CODE_POINTS = 256

_FORBIDDEN_KEY_TERMS = frozenset(
    {
        "understanding",
        "selectionreason",
        "prompt",
        "chainofthought",
        "reasoning",
        "readingmemory",
        "recentreadingmemory",
        "unitmemory",
        "settlementaudit",
        "jobstatus",
        "readingprogress",
        "reactionid",
        "compatfamily",
        "download",
        "feedback",
        "rating",
        "rank",
        "runtime",
        "runtimetrace",
        "trace",
        "searchresults",
        "runid",
        "jobid",
        "sourcefile",
        "artifactpath",
        "mechanismkey",
        "auditpointer",
        "apikey",
        "accesstoken",
        "password",
        "secret",
        "credential",
        "authorization",
        "cookie",
        "privatekey",
        "jwt",
    }
)
_FORBIDDEN_VALUE_FRAGMENTS = (
    "/_mechanisms/",
    "/_runtime/",
    "state/library_sources",
    "state/uploads",
    "attentional_v2",
    "iterator_reader",
)
_FORBIDDEN_KEY_TOKENS = frozenset(
    {
        "authorization",
        "cookie",
        "credential",
        "download",
        "feedback",
        "password",
        "prompt",
        "rank",
        "rating",
        "runtime",
        "secret",
        "token",
        "trace",
    }
)
_RESERVED_PREFIXES = frozenset(
    {"dc", "dcterms", "oa", "rdf", "rdfs", "schema", "sr", "xsd"}
)

# Codes emitted from a structurally present Pack by this module.
PACK_VALIDATOR_CODES = frozenset(
    {
        "schema_version_unsupported",
        "schema_validation_failed",
        "document_limit_exceeded",
        "extension_limit_exceeded",
        "unknown_declared_extension",
        "unknown_extension_prefix",
        "reserved_prefix_redefinition",
        "publication_identity_missing",
        "chapter_context_mismatch",
        "duplicate_pack_or_track_id_semantics",
        "duplicate_annotation_id",
        "duplicate_anchor_semantics",
        "semantic_digest_mismatch",
        "creator_mismatch",
        "item_order_invalid",
        "private_field_leakage",
        "invalid_generated_timestamp",
        "unsupported_kind",
        "invalid_annotation_timestamp",
        "highlight_body_present",
        "note_body_missing",
        "body_looks_like_source_copy",
        "empty_track",
        "validation_context_invalid",
    }
)

# Findings that can be produced by the already-separated source/anchor/draft
# stages and safely carried into this pure validator.  Presence in this set does
# not imply that validation.py implements the corresponding source operation.
UPSTREAM_VALIDATION_CODES = frozenset(
    {
        "source_asset_missing_or_not_epub",
        "publication_substrate_mismatch",
        "publication_identity_missing",
        "input_changed_during_export",
        "reaction_ledger_unavailable",
        "reaction_ledger_invalid_json",
        "reaction_ledger_schema_unsupported",
        "reaction_ledger_limit_exceeded",
        "active_writer_present",
        "run_state_not_exportable",
        "unsupported_kind",
        "unsupported_legacy_record",
        "invalid_annotation_timestamp",
        "highlight_body_present",
        "note_body_missing",
        "malformed_source_span",
        "grapheme_boundary_split",
        "cross_resource_span",
        "resource_text_unverifiable",
        "non_contiguous_resource_quote",
        "unresolved_source_quote",
        "ambiguous_source_quote",
        "source_quote_too_long",
        "target_href_not_in_manifest",
        "cfi_unverified",
        "quote_not_unique_in_resource",
        "duplicate_resource_chapter_projection",
        "body_looks_like_source_copy",
        "invalid_persisted_metadata_fallback",
        "invalid_publication_metadata",
        "publication_metadata_mismatch",
        "invalid_publication_language",
    }
)

# Reserved for exporter/publication/package layers.  Keeping them in the common
# catalog prevents ad-hoc spellings while making it explicit that this module
# cannot discover these failures from an in-memory Mapping.
FUTURE_PIPELINE_CODES = frozenset(
    {
        "deliverable_not_implemented",
        "publication_pointer_invalid",
        "validation_report_invalid",
        "package_entry_invalid",
    }
)
EXPORT_PIPELINE_CODES = frozenset(
    {
        "output_path_invalid",
        "book_document_unavailable",
        "book_document_invalid_json",
        "book_document_limit_exceeded",
        "export_configuration_invalid",
        "export_internal_error",
        "publication_write_failed",
    }
)
ERROR_CATALOG = (
    PACK_VALIDATOR_CODES
    | UPSTREAM_VALIDATION_CODES
    | FUTURE_PIPELINE_CODES
    | EXPORT_PIPELINE_CODES
)

_ROW_ERROR_CODES = frozenset(
    {
        "unsupported_kind",
        "unsupported_legacy_record",
        "invalid_annotation_timestamp",
        "highlight_body_present",
        "note_body_missing",
        "malformed_source_span",
        "grapheme_boundary_split",
        "cross_resource_span",
        "resource_text_unverifiable",
        "non_contiguous_resource_quote",
        "unresolved_source_quote",
        "ambiguous_source_quote",
        "source_quote_too_long",
        "target_href_not_in_manifest",
    }
)
_WARNING_CODES = frozenset(
    {
        "cfi_unverified",
        "quote_not_unique_in_resource",
        "duplicate_resource_chapter_projection",
        "unknown_declared_extension",
        "empty_track",
        "body_looks_like_source_copy",
        "invalid_persisted_metadata_fallback",
        "invalid_publication_metadata",
        "publication_metadata_mismatch",
        "invalid_publication_language",
    }
)

_MESSAGES: dict[str, str] = {
    "schema_version_unsupported": "The Annotation Pack schema version is unsupported.",
    "schema_validation_failed": "The Annotation Pack does not satisfy the canonical schema.",
    "document_limit_exceeded": "The Annotation Pack exceeds a validation safety limit.",
    "extension_limit_exceeded": "An extension value exceeds a validation safety limit.",
    "unknown_declared_extension": "An unknown declared extension is present.",
    "unknown_extension_prefix": "An extension prefix is not declared by the protected context.",
    "reserved_prefix_redefinition": "A reserved JSON-LD prefix is redefined.",
    "source_asset_missing_or_not_epub": "The source asset is missing or is not a safe EPUB.",
    "publication_substrate_mismatch": "The persisted and source-rebuilt publication substrates differ.",
    "publication_identity_missing": "The publication identity is missing or inconsistent.",
    "input_changed_during_export": "An input changed during export.",
    "reaction_ledger_unavailable": "The producer reaction ledger is unavailable or unsafe to read.",
    "reaction_ledger_invalid_json": "The producer reaction ledger is not valid strict JSON.",
    "reaction_ledger_schema_unsupported": "The producer reaction ledger schema is unsupported.",
    "reaction_ledger_limit_exceeded": "The producer reaction ledger exceeds a safety limit.",
    "active_writer_present": "An active writer prevents a stable export snapshot.",
    "run_state_not_exportable": "The current run state is not exportable.",
    "output_path_invalid": "The configured book output path is invalid.",
    "book_document_unavailable": "The persisted BookDocument is unavailable or unsafe to read.",
    "book_document_invalid_json": "The persisted BookDocument is not valid strict JSON.",
    "book_document_limit_exceeded": "The persisted BookDocument exceeds a safety limit.",
    "export_configuration_invalid": "The Annotation Pack export configuration is invalid.",
    "export_internal_error": "The Annotation Pack export failed internally.",
    "deliverable_not_implemented": "The requested deliverable is not implemented.",
    "publication_pointer_invalid": "The publication pointer is invalid.",
    "validation_report_invalid": "The validation report is invalid.",
    "publication_write_failed": "The Annotation Pack publication could not be written safely.",
    "duplicate_pack_or_track_id_semantics": "The Pack or track identity does not match its semantics.",
    "duplicate_annotation_id": "An annotation identity is duplicated or inconsistent.",
    "duplicate_anchor_semantics": "An anchor identity is duplicated or inconsistent.",
    "semantic_digest_mismatch": "The semantic digest does not match the canonical semantic projection.",
    "creator_mismatch": "An annotation creator does not equal the track creator.",
    "item_order_invalid": "Annotation items are not sorted by canonical annotation id.",
    "chapter_context_mismatch": "An annotation chapter context does not match the publication identity.",
    "private_field_leakage": "Private runtime or local-path material is present.",
    "invalid_generated_timestamp": "The generated timestamp is not second-precision UTC.",
    "unsupported_kind": "The annotation kind is unsupported.",
    "unsupported_legacy_record": "The source record is not a supported native annotation.",
    "invalid_annotation_timestamp": "The annotation timestamp is invalid.",
    "highlight_body_present": "A Highlight must not contain a body.",
    "note_body_missing": "A Note must contain one valid plain-text body.",
    "malformed_source_span": "The source span is malformed.",
    "grapheme_boundary_split": "The source span splits an extended grapheme cluster.",
    "cross_resource_span": "The source span crosses EPUB resources.",
    "resource_text_unverifiable": "The EPUB resource text cannot be verified safely.",
    "non_contiguous_resource_quote": "The source span is not contiguous in the EPUB resource text.",
    "unresolved_source_quote": "The source quote does not match the canonical source range.",
    "ambiguous_source_quote": "The source quote does not resolve uniquely.",
    "source_quote_too_long": "The source quote exceeds the v0 code-point limit.",
    "target_href_not_in_manifest": "The target resource is not in the verified EPUB manifest.",
    "cfi_unverified": "The optional EPUB CFI was omitted because round-trip verification failed.",
    "quote_not_unique_in_resource": "The source quote occurs more than once in its EPUB resource.",
    "duplicate_resource_chapter_projection": "One EPUB resource projection appears in multiple chapters.",
    "body_looks_like_source_copy": "The Note body appears to reproduce a large source excerpt.",
    "empty_track": "The annotation track contains no items.",
    "package_entry_invalid": "The detached package contains an unsafe or unexpected entry.",
    "validation_context_invalid": "The validation context is internally inconsistent.",
    "invalid_persisted_metadata_fallback": "Persisted publication metadata was not safe to use.",
    "invalid_publication_metadata": "Publication metadata was invalid and was omitted.",
    "publication_metadata_mismatch": "Publication metadata sources did not agree.",
    "invalid_publication_language": "The publication language was invalid and was omitted.",
}


@dataclass(frozen=True, slots=True)
class ValidationContext:
    """Optional upstream accounting and explicit empty-publication policy."""

    input_count: int | None = None
    findings: tuple[ValidationFinding, ...] = ()
    allow_empty: bool = False
    input_snapshot_digest: str | None = None
    producer: str | None = None
    adapter_version: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Pre-artifact validation outcome; intentionally has no byte digests."""

    schema_version: str
    validator_version: str
    status: ValidationStatus
    pack_id: str | None
    semantic_digest: str | None
    input_snapshot_digest: str | None
    producer: str | None
    adapter_version: str | None
    input_count: int
    exported_count: int
    skipped_count: int
    warning_count: int
    error_count: int
    findings: tuple[ValidationFinding, ...]

    @property
    def publishable(self) -> bool:
        return self.status in {"valid", "degraded"}


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Final artifact-digest-aware, immutable validation companion."""

    schema_version: str
    validator_version: str
    status: ValidationStatus
    pack_id: str | None
    semantic_digest: str | None
    input_snapshot_digest: str | None
    producer: str | None
    adapter_version: str | None
    annotations_json_sha256: str | None
    package_sha256: str | None
    input_count: int
    exported_count: int
    skipped_count: int
    warning_count: int
    error_count: int
    findings: tuple[ValidationFinding, ...]

    def to_wire(self) -> dict[str, JSONValue]:
        return validation_report_wire(self)

    def canonical_bytes(self) -> bytes:
        return serialize_validation_report(self)


def validate_pack(
    document: Mapping[str, object],
    *,
    mode: ValidationMode = "strict",
    verify_ids: bool = True,
    context: ValidationContext | None = None,
) -> ValidationResult:
    """Validate one in-memory Pack without network, source, or disk access.

    Minimal v0 has one strict mode.  Every object layer is closed by the
    canonical schema; there is no extension or old-wire compatibility mode.
    """

    if mode != "strict":
        raise ValueError("mode must be 'strict'")
    if not isinstance(verify_ids, bool):
        raise TypeError("verify_ids must be a boolean")
    if context is None:
        context = ValidationContext()
    if type(context) is not ValidationContext:
        raise TypeError("context must be a ValidationContext")

    findings: list[ValidationFinding] = []
    findings.extend(_sanitize_context_findings(context))

    if not isinstance(document, Mapping):
        findings.append(_finding("schema_validation_failed", "fatal"))
        return _result(
            document=None,
            context=context,
            findings=findings,
            exported_count=0,
        )

    preflight, plain = _preflight_document(document)
    findings.extend(preflight)
    if plain is None:
        return _result(
            document=None,
            context=context,
            findings=findings,
            exported_count=0,
        )

    try:
        # Re-encoding only the already detached plain snapshot enforces the
        # interoperable integer/Unicode domain without re-reading caller state.
        canonical_json_bytes(plain)
    except (CanonicalJsonError, UnicodeError):
        findings.append(_finding("schema_validation_failed", "fatal"))
        return _result(
            document=plain,
            context=context,
            findings=findings,
            exported_count=_safe_item_count(plain),
        )

    schema_errors = sorted(
        pack_validator().iter_errors(plain),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            str(error.validator),
            tuple(str(part) for part in error.absolute_schema_path),
        ),
    )
    for error in schema_errors[:MAX_SCHEMA_FINDINGS]:
        findings.append(_schema_finding(error, plain))
    if len(schema_errors) > MAX_SCHEMA_FINDINGS:
        findings.append(_finding("document_limit_exceeded", "fatal"))

    # Cross-object access is intentionally gated by structural validity.  The
    # schema remains the sole wire-shape authority; semantic code does not try
    # to repair or reinterpret malformed objects.
    if not schema_errors:
        findings.extend(_semantic_findings(plain, verify_ids=verify_ids))

    items = plain.get("items")
    exported_count = len(items) if isinstance(items, list) else 0
    if exported_count == 0:
        findings.append(
            _finding(
                "empty_track",
                "warning"
                if type(context.allow_empty) is bool and context.allow_empty
                else "fatal",
                json_pointer="/items",
            )
        )

    return _result(
        document=plain,
        context=context,
        findings=findings,
        exported_count=exported_count,
    )


def finalize_validation_report(
    result: ValidationResult,
    *,
    annotations_json_sha256: str | None,
    package_sha256: str | None,
) -> ValidationReport:
    """Inject final artifact digests exactly once and return a schema-valid report."""

    if type(result) is not ValidationResult:
        raise TypeError("result must be a ValidationResult")
    _validate_result_coherence(result)
    annotations_digest = _optional_digest(
        annotations_json_sha256,
        "annotations_json_sha256",
    )
    package_digest = _optional_digest(package_sha256, "package_sha256")
    if package_digest is not None and annotations_digest is None:
        raise ValueError("package digest requires annotations JSON digest")
    if result.publishable and annotations_digest is None:
        raise ValueError(
            "publishable validation reports require annotations JSON digest"
        )

    report = ValidationReport(
        schema_version=VALIDATION_REPORT_SCHEMA_VERSION,
        validator_version=VALIDATOR_VERSION,
        status=result.status,
        pack_id=result.pack_id,
        semantic_digest=result.semantic_digest,
        input_snapshot_digest=result.input_snapshot_digest,
        producer=result.producer,
        adapter_version=result.adapter_version,
        annotations_json_sha256=annotations_digest,
        package_sha256=package_digest,
        input_count=result.input_count,
        exported_count=result.exported_count,
        skipped_count=result.skipped_count,
        warning_count=result.warning_count,
        error_count=result.error_count,
        findings=result.findings,
    )
    wire = validation_report_wire(report)
    errors = tuple(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(wire))
    if errors:  # pragma: no cover - construction invariant, tested through inputs
        raise ValueError("validation report does not satisfy its canonical schema")
    return report


def validation_report_wire(report: ValidationReport) -> dict[str, JSONValue]:
    """Return a fresh JSON-shaped report object with deterministic findings."""

    if type(report) is not ValidationReport:
        raise TypeError("report must be a ValidationReport")
    _validate_report_coherence(report)
    findings = sorted(report.findings, key=_finding_sort_key)
    return {
        "schema_version": report.schema_version,
        "validator_version": report.validator_version,
        "status": report.status,
        "pack_id": report.pack_id,
        "semantic_digest": report.semantic_digest,
        "input_snapshot_digest": report.input_snapshot_digest,
        "producer": report.producer,
        "adapter_version": report.adapter_version,
        "annotations_json_sha256": report.annotations_json_sha256,
        "package_sha256": report.package_sha256,
        "counts": {
            "input": report.input_count,
            "exported": report.exported_count,
            "skipped": report.skipped_count,
            "warnings": report.warning_count,
            "errors": report.error_count,
        },
        "findings": [_finding_wire(finding) for finding in findings],
    }


def serialize_validation_report(report: ValidationReport) -> bytes:
    """Return exact ``sr-annotation-validation-report-json-v1`` bytes."""

    wire = validation_report_wire(report)
    errors = tuple(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(wire))
    if errors:
        raise ValueError("validation report does not satisfy its canonical schema")
    return canonical_json_bytes(wire)


def _preflight_document(
    document: Mapping[str, object],
) -> tuple[list[ValidationFinding], dict[str, JSONValue] | None]:
    """Create one bounded, privacy-scanned plain snapshot of caller state."""

    findings: list[ValidationFinding] = []
    active: set[int] = set()
    nodes = 0
    total_string_code_points = 0

    class _SnapshotAborted(Exception):
        pass

    def abort(code: str) -> None:
        findings.append(_finding(code, "fatal"))
        raise _SnapshotAborted

    def snapshot(
        value: object,
        *,
        depth: int,
        value_path: tuple[str, ...],
    ) -> JSONValue:
        nonlocal nodes, total_string_code_points
        nodes += 1
        if nodes > MAX_DOCUMENT_NODES or depth > MAX_DOCUMENT_DEPTH:
            abort("document_limit_exceeded")

        if type(value) is str:
            total_string_code_points += len(value)
            if (
                len(value) > MAX_SINGLE_STRING_CODE_POINTS
                or total_string_code_points > MAX_DOCUMENT_STRING_CODE_POINTS
            ):
                abort("document_limit_exceeded")
            try:
                value.encode("utf-8")
            except UnicodeEncodeError:
                abort("schema_validation_failed")
            if (
                _cfi_selector_value_path(value_path) and _cfi_value_looks_private(value)
            ) or (_scan_private_value_at(value_path) and _value_looks_private(value)):
                findings.append(_finding("private_field_leakage", "fatal"))
            return value
        if value is None or type(value) in {bool, int}:
            return value
        if type(value) is float:
            abort("schema_validation_failed")

        if isinstance(value, Mapping):
            identity = id(value)
            if identity in active:
                abort("schema_validation_failed")
            active.add(identity)
            try:
                result: dict[str, JSONValue] = {}
                for key, child in value.items():
                    if type(key) is not str:
                        abort("schema_validation_failed")
                    total_string_code_points += len(key)
                    if total_string_code_points > MAX_DOCUMENT_STRING_CODE_POINTS:
                        abort("document_limit_exceeded")
                    try:
                        key.encode("utf-8")
                    except UnicodeEncodeError:
                        abort("schema_validation_failed")
                    if _key_looks_private(key):
                        findings.append(_finding("private_field_leakage", "fatal"))
                    result[key] = snapshot(
                        child,
                        depth=depth + 1,
                        value_path=(*value_path, key),
                    )
                return result
            finally:
                active.remove(identity)

        if isinstance(value, (list, tuple)):
            identity = id(value)
            if identity in active:
                abort("schema_validation_failed")
            active.add(identity)
            try:
                return [
                    snapshot(
                        child,
                        depth=depth + 1,
                        value_path=(*value_path, str(index)),
                    )
                    for index, child in enumerate(value)
                ]
            finally:
                active.remove(identity)

        abort("schema_validation_failed")

    try:
        plain = snapshot(document, depth=0, value_path=())
    except _SnapshotAborted:
        return _deduplicate_findings(findings), None
    except Exception:
        # Hostile/lazy Mapping exceptions are never reflected into public text.
        findings.append(_finding("schema_validation_failed", "fatal"))
        return _deduplicate_findings(findings), None
    if not isinstance(plain, dict):  # pragma: no cover - root Mapping is copied
        findings.append(_finding("schema_validation_failed", "fatal"))
        return _deduplicate_findings(findings), None
    return _deduplicate_findings(findings), plain


def _extension_findings(
    document: Mapping[str, JSONValue],
    *,
    mode: ValidationMode,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    declared: dict[str, str] = {
        "sr": "https://captain4whale.github.io/second-reader/ns/annotation-pack#"
    }
    context = document.get("@context")
    context_mapping: Mapping[str, object] | None = None
    if (
        isinstance(context, list)
        and len(context) == 2
        and isinstance(context[1], Mapping)
    ):
        context_mapping = context[1]
        for prefix, iri in context_mapping.items():
            if prefix in {"@protected", "sr"}:
                continue
            if not isinstance(prefix, str) or _PREFIX_RE.fullmatch(prefix) is None:
                continue
            if prefix.casefold() in _RESERVED_PREFIXES:
                findings.append(
                    _finding(
                        "reserved_prefix_redefinition",
                        "fatal",
                        json_pointer="/@context/1",
                    )
                )
                continue
            if not isinstance(iri, str) or not _safe_namespace_iri(iri):
                findings.append(
                    _finding(
                        "unknown_extension_prefix",
                        "fatal",
                        json_pointer="/@context/1",
                    )
                )
                continue
            declared[prefix] = iri
            findings.append(
                _finding(
                    "unknown_declared_extension",
                    "fatal" if mode == "strict" else "warning",
                    json_pointer="/@context/1",
                )
            )

    schema_root = _canonical_schema()
    stack: list[tuple[object, str, tuple[Mapping[str, object], ...]]] = [
        (document, "", (schema_root,))
    ]
    while stack:
        value, pointer, schema_nodes = stack.pop()
        expanded_nodes = _expanded_schema_nodes(schema_nodes, root=schema_root)
        if isinstance(value, Mapping):
            allowed_properties: set[str] = set()
            for schema_node in expanded_nodes:
                properties = schema_node.get("properties")
                if isinstance(properties, Mapping):
                    allowed_properties.update(
                        key for key in properties if isinstance(key, str)
                    )
            for key, child in value.items():
                if not isinstance(key, str):
                    continue
                child_pointer = _pointer_child(pointer, key)
                match = _CURIE_RE.fullmatch(key)
                if match is not None:
                    if key in _canonical_core_keys() and key not in allowed_properties:
                        findings.append(
                            _finding(
                                "schema_validation_failed",
                                "fatal",
                                json_pointer=_safe_json_pointer(child_pointer),
                            )
                        )
                    elif key not in _canonical_core_keys():
                        prefix = match.group("prefix")
                        if prefix not in declared:
                            findings.append(
                                _finding(
                                    "unknown_extension_prefix",
                                    "fatal",
                                    json_pointer=_safe_json_pointer(child_pointer),
                                )
                            )
                        else:
                            findings.append(
                                _finding(
                                    "unknown_declared_extension",
                                    "fatal" if mode == "strict" else "warning",
                                    json_pointer=_safe_json_pointer(child_pointer),
                                )
                            )
                            if not _extension_within_limits(child):
                                findings.append(
                                    _finding(
                                        "extension_limit_exceeded",
                                        "fatal",
                                        json_pointer=_safe_json_pointer(child_pointer),
                                    )
                                )
                child_schemas = _object_child_schemas(
                    expanded_nodes,
                    property_name=key,
                )
                stack.append((child, child_pointer, child_schemas))
        elif isinstance(value, list):
            stack.extend(
                (
                    child,
                    _pointer_child(pointer, str(index)),
                    _array_child_schemas(expanded_nodes, index=index),
                )
                for index, child in reversed(tuple(enumerate(value)))
            )
    return _deduplicate_findings(findings)


@lru_cache(maxsize=1)
def _canonical_schema() -> Mapping[str, object]:
    return load_schema()


@lru_cache(maxsize=1)
def _canonical_core_keys() -> frozenset[str]:
    """Derive core CURIE fields from the canonical schema authority."""

    keys: set[str] = set()
    stack: list[object] = [_canonical_schema()]
    while stack:
        value = stack.pop()
        if isinstance(value, Mapping):
            properties = value.get("properties")
            if isinstance(properties, Mapping):
                keys.update(
                    str(key)
                    for key in properties
                    if isinstance(key, str) and _CURIE_RE.fullmatch(key)
                )
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
    return frozenset(keys)


def _expanded_schema_nodes(
    schema_nodes: Sequence[Mapping[str, object]],
    *,
    root: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    stack: list[Mapping[str, object]] = list(schema_nodes)
    expanded: list[Mapping[str, object]] = []
    seen: set[int] = set()
    while stack:
        node = stack.pop()
        identity = id(node)
        if identity in seen:
            continue
        seen.add(identity)
        expanded.append(node)
        reference = node.get("$ref")
        if isinstance(reference, str):
            resolved = _resolve_local_schema_reference(root, reference)
            if resolved is not None:
                stack.append(resolved)
        for keyword in ("allOf", "anyOf", "oneOf"):
            branches = node.get(keyword)
            if isinstance(branches, list):
                stack.extend(
                    branch for branch in branches if isinstance(branch, Mapping)
                )
        for keyword in ("if", "then", "else"):
            branch = node.get(keyword)
            if isinstance(branch, Mapping):
                stack.append(branch)
    return tuple(expanded)


def _resolve_local_schema_reference(
    root: Mapping[str, object],
    reference: str,
) -> Mapping[str, object] | None:
    if not reference.startswith("#/"):
        return None
    value: object = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, Mapping) or part not in value:
            return None
        value = value[part]
    return value if isinstance(value, Mapping) else None


def _object_child_schemas(
    schema_nodes: Sequence[Mapping[str, object]],
    *,
    property_name: str,
) -> tuple[Mapping[str, object], ...]:
    result: list[Mapping[str, object]] = []
    for node in schema_nodes:
        properties = node.get("properties")
        if not isinstance(properties, Mapping):
            continue
        child = properties.get(property_name)
        if isinstance(child, Mapping):
            result.append(child)
    return tuple(result)


def _array_child_schemas(
    schema_nodes: Sequence[Mapping[str, object]],
    *,
    index: int,
) -> tuple[Mapping[str, object], ...]:
    result: list[Mapping[str, object]] = []
    for node in schema_nodes:
        prefix_items = node.get("prefixItems")
        prefix_length = len(prefix_items) if isinstance(prefix_items, list) else 0
        if isinstance(prefix_items, list) and index < prefix_length:
            child = prefix_items[index]
            if isinstance(child, Mapping):
                result.append(child)
            continue
        child = node.get("items")
        if isinstance(child, Mapping):
            result.append(child)
    return tuple(result)


def _extension_within_limits(value: object) -> bool:
    stack: list[tuple[object, int]] = [(value, 0)]
    nodes = 0
    string_code_points = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_EXTENSION_NODES or depth > MAX_EXTENSION_DEPTH:
            return False
        if isinstance(current, str):
            string_code_points += len(current)
            if string_code_points > MAX_EXTENSION_STRING_CODE_POINTS:
                return False
        elif isinstance(current, Mapping):
            for key, child in current.items():
                if isinstance(key, str):
                    string_code_points += len(key)
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
    return string_code_points <= MAX_EXTENSION_STRING_CODE_POINTS


def _schema_finding(error: Any, document: Mapping[str, JSONValue]) -> ValidationFinding:
    path = tuple(error.absolute_path)
    pointer = _safe_json_pointer(_path_pointer(path))
    if not path:
        if error.validator == "required" and "about" not in document:
            return _finding(
                "publication_identity_missing", "fatal", json_pointer="/about"
            )
        if error.validator == "required" and "generated" not in document:
            return _finding(
                "invalid_generated_timestamp", "fatal", json_pointer="/generated"
            )
        return _finding("schema_validation_failed", "fatal", json_pointer=pointer)

    if path[0] == "generated":
        return _finding(
            "invalid_generated_timestamp", "fatal", json_pointer="/generated"
        )
    if path[0] == "about":
        return _finding("publication_identity_missing", "fatal", json_pointer=pointer)
    if path[0] == "items" and len(path) >= 2 and isinstance(path[1], int):
        index = path[1]
        item = _item_at(document, index)
        item_pointer = f"/items/{index}"
        if item is not None:
            motivation = item.get("motivation")
            if motivation not in {"highlighting", "commenting"}:
                return _finding(
                    "unsupported_kind",
                    "error",
                    json_pointer=f"{item_pointer}/motivation",
                )
            if "created" not in item or (len(path) >= 3 and path[2] == "created"):
                return _finding(
                    "invalid_annotation_timestamp",
                    "error",
                    json_pointer=f"{item_pointer}/created",
                )
            if motivation == "highlighting" and "body" in item:
                return _finding(
                    "highlight_body_present",
                    "error",
                    json_pointer=f"{item_pointer}/body",
                )
            if motivation == "commenting" and (
                "body" not in item or (len(path) >= 3 and path[2] == "body")
            ):
                return _finding(
                    "note_body_missing",
                    "error",
                    json_pointer=f"{item_pointer}/body",
                )
        return _finding("schema_validation_failed", "fatal", json_pointer=pointer)
    return _finding("schema_validation_failed", "fatal", json_pointer=pointer)


def _semantic_findings(
    document: Mapping[str, JSONValue],
    *,
    verify_ids: bool,
) -> list[ValidationFinding]:
    about = _mapping(document["about"])
    generator = _mapping(document["generator"])
    items = _list(document["items"])
    findings: list[ValidationFinding] = []

    if not _normalized_metadata(document):
        findings.append(_finding("schema_validation_failed", "fatal"))
    if not _public_iris_are_safe(document):
        findings.append(_finding("private_field_leakage", "fatal"))

    nih = str(_list(about["dc:identifier"])[0])
    epub_sha256 = nih.removeprefix("nih:sha-256;")
    if verify_ids:
        try:
            expected_pack = pack_id(epub_sha256, str(generator["id"]))
            if document["id"] != expected_pack:
                findings.append(
                    _finding("duplicate_pack_or_track_id_semantics", "fatal")
                )
        except (KeyError, TypeError, ValueError):
            findings.append(_finding("duplicate_pack_or_track_id_semantics", "fatal"))

    ids: list[str] = []
    seen_ids: set[str] = set()
    annotation_semantics: set[tuple[str, int, int, str, str]] = set()

    for index, raw_item in enumerate(items):
        item = _mapping(raw_item)
        item_id = str(item["id"])
        ids.append(item_id)
        if item_id in seen_ids:
            findings.append(
                _finding(
                    "duplicate_annotation_id",
                    "fatal",
                    json_pointer=f"/items/{index}/id",
                    annotation_id=item_id,
                )
            )
        seen_ids.add(item_id)

        target = _mapping(item["target"])
        source = str(target["source"])
        if not _canonical_epub_href(source):
            findings.append(
                _finding(
                    "target_href_not_in_manifest",
                    "error",
                    json_pointer=f"/items/{index}/target/source",
                    annotation_id=item_id,
                )
            )
        selectors = _list(target["selector"])
        quote = _mapping(selectors[0])
        position = _mapping(selectors[1])
        exact = str(quote["exact"])
        start = int(position["start"])
        end = int(position["end"])
        if start < 0 or start >= end:
            findings.append(
                _finding(
                    "malformed_source_span",
                    "error",
                    json_pointer=f"/items/{index}/target/selector/1",
                    annotation_id=item_id,
                )
            )
        if end - start != len(exact):
            findings.append(
                _finding(
                    "unresolved_source_quote",
                    "error",
                    json_pointer=f"/items/{index}/target/selector/0/exact",
                    annotation_id=item_id,
                )
            )

        motivation = str(item["motivation"])
        body_value = ""
        body_for_id: str | None = None
        if motivation == "commenting":
            body_value = str(_mapping(item["body"])["value"])
            body_for_id = body_value
            if not body_value.strip():
                findings.append(
                    _finding(
                        "note_body_missing",
                        "error",
                        json_pointer=f"/items/{index}/body/value",
                        annotation_id=item_id,
                    )
                )
            if (
                len(body_value) >= 512
                and len(exact) >= 512
                and (body_value == exact or exact in body_value or body_value in exact)
            ):
                findings.append(
                    _finding(
                        "body_looks_like_source_copy",
                        "warning",
                        json_pointer=f"/items/{index}/body",
                        annotation_id=item_id,
                    )
                )
        semantic_key = (source, start, end, motivation, body_value)
        if semantic_key in annotation_semantics:
            findings.append(
                _finding(
                    "duplicate_annotation_id",
                    "fatal",
                    json_pointer=f"/items/{index}/id",
                    annotation_id=item_id,
                )
            )
        annotation_semantics.add(semantic_key)

        if verify_ids:
            try:
                expected_annotation = annotation_id(
                    epub_sha256,
                    source,
                    start,
                    end,
                    motivation,  # type: ignore[arg-type]
                    body_for_id,
                )
            except (TypeError, ValueError):
                expected_annotation = ""
            if item_id != expected_annotation:
                findings.append(
                    _finding(
                        "duplicate_annotation_id",
                        "fatal",
                        json_pointer=f"/items/{index}/id",
                        annotation_id=item_id,
                    )
                )

    if ids != sorted(ids):
        findings.append(_finding("item_order_invalid", "fatal", json_pointer="/items"))
    return _deduplicate_findings(findings)


def _normalized_metadata(document: Mapping[str, JSONValue]) -> bool:
    about = _mapping(document["about"])
    candidates: list[tuple[str, bool]] = [
        (str(about["dc:title"]), True),
        (str(_mapping(document["generator"])["name"]), False),
    ]
    candidates.extend(
        (str(value), True) for value in _list(about.get("dc:creator", []))
    )
    for item_raw in _list(document["items"]):
        item = _mapping(item_raw)
        if item["motivation"] == "commenting":
            candidates.append((str(_mapping(item["body"])["value"]), False))
    return all(
        value == unicodedata.normalize("NFC", value)
        and (not trim_required or value == value.strip())
        for value, trim_required in candidates
    )


def _public_iris_are_safe(document: Mapping[str, JSONValue]) -> bool:
    about = _mapping(document["about"])
    candidates = [
        str(_mapping(document["generator"])["id"]),
    ]
    candidates.extend(str(value) for value in _list(about["dc:identifier"]))
    return all(_safe_public_iri(value) for value in candidates)


def _sanitize_context_findings(context: ValidationContext) -> list[ValidationFinding]:
    sanitized: list[ValidationFinding] = []
    invalid = False
    input_count = context.input_count
    context_findings = context.findings
    allow_empty = context.allow_empty
    input_snapshot_digest = context.input_snapshot_digest
    producer = context.producer
    adapter_version = context.adapter_version
    if input_count is not None and (type(input_count) is not int or input_count < 0):
        invalid = True
    if type(allow_empty) is not bool or type(context_findings) is not tuple:
        invalid = True
    if input_snapshot_digest is not None and (
        type(input_snapshot_digest) is not str
        or _SHA256_RE.fullmatch(input_snapshot_digest) is None
    ):
        invalid = True
    if producer is not None and (
        type(producer) is not str or not _safe_public_iri(producer)
    ):
        invalid = True
    if adapter_version is not None and (
        type(adapter_version) is not str
        or _SEMVER_RE.fullmatch(adapter_version) is None
    ):
        invalid = True
    if (producer is None) != (adapter_version is None):
        invalid = True

    if type(context_findings) is tuple:
        for finding in context_findings:
            if type(finding) is not ValidationFinding:
                invalid = True
                continue
            code = finding.code
            severity = finding.severity
            message = finding.message
            if (
                type(code) is not str
                or type(severity) is not str
                or type(message) is not str
                or code not in ERROR_CATALOG
                or _CODE_RE.fullmatch(code) is None
            ):
                invalid = True
                continue
            if not _allowed_context_severity(code, severity):
                invalid = True
                continue
            source_index = finding.source_record_index
            if source_index is not None and (
                type(source_index) is not int or source_index < 0
            ):
                invalid = True
                source_index = None
            source_digest = finding.source_record_digest
            if source_digest is not None and (
                type(source_digest) is not str
                or _SHA256_RE.fullmatch(source_digest) is None
            ):
                invalid = True
                source_digest = None
            annotation = finding.annotation_id
            if annotation is not None and (
                type(annotation) is not str
                or _UUID5_URN_RE.fullmatch(annotation) is None
            ):
                invalid = True
                annotation = None
            raw_pointer = finding.json_pointer
            pointer = (
                _safe_json_pointer(raw_pointer)
                if raw_pointer is None or type(raw_pointer) is str
                else None
            )
            if type(raw_pointer) not in {str, type(None)} or pointer != raw_pointer:
                invalid = True
            sanitized.append(
                _finding(
                    code,
                    severity,
                    source_record_index=source_index,
                    source_record_digest=source_digest,
                    json_pointer=pointer,
                    annotation_id=annotation,
                )
            )
    if invalid:
        sanitized.append(_finding("validation_context_invalid", "fatal"))
    return _deduplicate_findings(sanitized)


def _allowed_context_severity(code: str, severity: str) -> bool:
    if code in _ROW_ERROR_CODES:
        return severity in {"error", "skipped"}
    if code in _WARNING_CODES:
        return severity == "warning"
    return severity == "fatal"


def _allowed_result_severity(code: str, severity: str) -> bool:
    if code in _ROW_ERROR_CODES:
        return severity in {"error", "skipped"}
    if code in {"empty_track", "unknown_declared_extension"}:
        return severity in {"fatal", "warning"}
    if code in _WARNING_CODES:
        return severity == "warning"
    return severity == "fatal"


def _result(
    *,
    document: Mapping[str, object] | None,
    context: ValidationContext,
    findings: Sequence[ValidationFinding],
    exported_count: int,
) -> ValidationResult:
    ordered = tuple(sorted(_deduplicate_findings(findings), key=_finding_sort_key))
    skipped_count = sum(finding.severity == "skipped" for finding in ordered)
    warning_count = sum(finding.severity == "warning" for finding in ordered)
    error_count = sum(finding.severity in {"fatal", "error"} for finding in ordered)
    raw_input_count = context.input_count
    input_count = (
        raw_input_count
        if type(raw_input_count) is int
        else exported_count + skipped_count
    )
    minimum_accounted = exported_count + skipped_count
    accounting_invalid = (
        input_count < minimum_accounted
        if error_count
        else input_count != minimum_accounted
    )
    if accounting_invalid:
        ordered = tuple(
            sorted(
                _deduplicate_findings(
                    (*ordered, _finding("validation_context_invalid", "fatal"))
                ),
                key=_finding_sort_key,
            )
        )
        warning_count = sum(finding.severity == "warning" for finding in ordered)
        error_count = sum(finding.severity in {"fatal", "error"} for finding in ordered)
        # Retain the caller's safe non-negative input count for diagnostics, but
        # the fatal finding prevents it from becoming a published report.
        if input_count < 0:
            input_count = minimum_accounted

    if error_count:
        status: ValidationStatus = "failed"
    elif skipped_count:
        status = "degraded"
    else:
        status = "valid"

    pack_value = _safe_nested_string(document, "id")
    try:
        semantic_value = semantic_digest(document) if document is not None else None
    except (CanonicalJsonError, KeyError, TypeError, ValueError):
        semantic_value = None
    input_value = context.input_snapshot_digest
    producer = context.producer
    adapter_version = context.adapter_version
    return ValidationResult(
        schema_version=VALIDATION_RESULT_SCHEMA_VERSION,
        validator_version=VALIDATOR_VERSION,
        status=status,
        pack_id=pack_value if _UUID5_URN_RE.fullmatch(pack_value or "") else None,
        semantic_digest=semantic_value
        if _SHA256_RE.fullmatch(semantic_value or "")
        else None,
        input_snapshot_digest=input_value
        if _SHA256_RE.fullmatch(input_value or "")
        else None,
        producer=(
            producer
            if isinstance(producer, str) and _safe_public_iri(producer)
            else None
        ),
        adapter_version=(
            adapter_version
            if isinstance(adapter_version, str)
            and _SEMVER_RE.fullmatch(adapter_version)
            else None
        ),
        input_count=input_count,
        exported_count=exported_count,
        skipped_count=skipped_count,
        warning_count=warning_count,
        error_count=error_count,
        findings=ordered,
    )


def _validate_result_coherence(result: ValidationResult) -> None:
    if (
        type(result.schema_version) is not str
        or result.schema_version != VALIDATION_RESULT_SCHEMA_VERSION
    ):
        raise ValueError("unsupported ValidationResult schema version")
    if (
        type(result.validator_version) is not str
        or result.validator_version != VALIDATOR_VERSION
    ):
        raise ValueError("ValidationResult validator version is not current")
    if type(result.status) is not str:
        raise ValueError("ValidationResult status is invalid")
    skipped, warnings, errors, status = _validate_findings_coherence(result.findings)
    _validate_count_fields(
        result.input_count,
        result.exported_count,
        result.skipped_count,
        result.warning_count,
        result.error_count,
    )
    accounting_coherent = (
        result.input_count == result.exported_count + result.skipped_count
        if result.publishable
        else result.input_count >= result.exported_count + result.skipped_count
    )
    if (
        result.skipped_count != skipped
        or result.warning_count != warnings
        or result.error_count != errors
        or result.status != status
        or not accounting_coherent
    ):
        raise ValueError("ValidationResult counts or status are inconsistent")
    _validate_optional_identity_fields(
        pack_id=result.pack_id,
        semantic_digest=result.semantic_digest,
        input_snapshot_digest=result.input_snapshot_digest,
    )
    _validate_optional_adapter_fields(
        producer=result.producer,
        adapter_version=result.adapter_version,
    )
    if result.publishable and (
        _UUID5_URN_RE.fullmatch(result.pack_id or "") is None
        or _SHA256_RE.fullmatch(result.semantic_digest or "") is None
    ):
        raise ValueError("publishable ValidationResult identity fields are incomplete")


def _validate_report_coherence(report: ValidationReport) -> None:
    if (
        type(report.schema_version) is not str
        or report.schema_version != VALIDATION_REPORT_SCHEMA_VERSION
    ):
        raise ValueError("unsupported ValidationReport schema version")
    if (
        type(report.validator_version) is not str
        or report.validator_version != VALIDATOR_VERSION
    ):
        raise ValueError("ValidationReport validator version is not current")
    if type(report.status) is not str:
        raise ValueError("ValidationReport status is invalid")
    skipped, warnings, errors, status = _validate_findings_coherence(report.findings)
    _validate_count_fields(
        report.input_count,
        report.exported_count,
        report.skipped_count,
        report.warning_count,
        report.error_count,
    )
    accounting_coherent = (
        report.input_count == report.exported_count + report.skipped_count
        if report.status in {"valid", "degraded"}
        else report.input_count >= report.exported_count + report.skipped_count
    )
    if (
        report.skipped_count != skipped
        or report.warning_count != warnings
        or report.error_count != errors
        or report.status != status
        or not accounting_coherent
    ):
        raise ValueError("ValidationReport counts or status are inconsistent")
    _validate_optional_identity_fields(
        pack_id=report.pack_id,
        semantic_digest=report.semantic_digest,
        input_snapshot_digest=report.input_snapshot_digest,
    )
    _validate_optional_adapter_fields(
        producer=report.producer,
        adapter_version=report.adapter_version,
    )
    _optional_digest(report.annotations_json_sha256, "annotations_json_sha256")
    _optional_digest(report.package_sha256, "package_sha256")
    if report.package_sha256 is not None and report.annotations_json_sha256 is None:
        raise ValueError("package digest requires annotations JSON digest")
    if report.status in {"valid", "degraded"} and (
        report.pack_id is None
        or report.semantic_digest is None
        or report.input_snapshot_digest is None
        or report.producer is None
        or report.adapter_version is None
        or report.annotations_json_sha256 is None
    ):
        raise ValueError("publishable ValidationReport fields are incomplete")


def _validate_findings_coherence(
    findings: object,
) -> tuple[int, int, int, ValidationStatus]:
    if type(findings) is not tuple:
        raise ValueError("validation findings must be a canonical tuple")
    for finding in findings:
        if type(finding) is not ValidationFinding:
            raise ValueError("validation findings contain an invalid entry")
        code = finding.code
        severity = finding.severity
        message = finding.message
        if (
            type(code) is not str
            or type(severity) is not str
            or type(message) is not str
            or code not in ERROR_CATALOG
            or _CODE_RE.fullmatch(code) is None
            or not _allowed_result_severity(code, severity)
            or message != _MESSAGES[code]
        ):
            raise ValueError("validation findings contain invalid code metadata")
        source_index = finding.source_record_index
        if source_index is not None and (
            type(source_index) is not int or source_index < 0
        ):
            raise ValueError("validation findings contain an invalid source index")
        source_digest = finding.source_record_digest
        if source_digest is not None and (
            type(source_digest) is not str
            or _SHA256_RE.fullmatch(source_digest) is None
        ):
            raise ValueError("validation findings contain an invalid source digest")
        annotation = finding.annotation_id
        if annotation is not None and (
            type(annotation) is not str or _UUID5_URN_RE.fullmatch(annotation) is None
        ):
            raise ValueError("validation findings contain an invalid annotation id")
        pointer = finding.json_pointer
        if (
            type(pointer) not in {str, type(None)}
            or _safe_json_pointer(pointer) != pointer
        ):
            raise ValueError("validation findings contain an unsafe JSON pointer")

    ordered = tuple(sorted(_deduplicate_findings(findings), key=_finding_sort_key))
    if findings != ordered:
        raise ValueError("validation findings are not canonical")
    skipped = sum(finding.severity == "skipped" for finding in ordered)
    warnings = sum(finding.severity == "warning" for finding in ordered)
    errors = sum(finding.severity in {"fatal", "error"} for finding in ordered)
    status: ValidationStatus = (
        "failed" if errors else "degraded" if skipped else "valid"
    )
    return skipped, warnings, errors, status


def _validate_count_fields(*counts: object) -> None:
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("validation counts must be non-negative integers")


def _validate_optional_identity_fields(
    *,
    pack_id: object,
    semantic_digest: object,
    input_snapshot_digest: object,
) -> None:
    if pack_id is not None and (
        type(pack_id) is not str or _UUID5_URN_RE.fullmatch(pack_id) is None
    ):
        raise ValueError("validation pack identity is invalid")
    for value in (semantic_digest, input_snapshot_digest):
        if value is not None and (
            type(value) is not str or _SHA256_RE.fullmatch(value) is None
        ):
            raise ValueError("validation digest identity is invalid")


def _validate_optional_adapter_fields(
    *,
    producer: object,
    adapter_version: object,
) -> None:
    if (producer is None) != (adapter_version is None):
        raise ValueError("validation adapter metadata is incomplete")
    if producer is not None and (
        type(producer) is not str or not _safe_public_iri(producer)
    ):
        raise ValueError("validation producer identity is invalid")
    if adapter_version is not None and (
        type(adapter_version) is not str
        or _SEMVER_RE.fullmatch(adapter_version) is None
    ):
        raise ValueError("validation adapter version is invalid")


def _finding(
    code: str,
    severity: Literal["fatal", "error", "warning", "skipped"],
    *,
    source_record_index: int | None = None,
    json_pointer: str | None = None,
    annotation_id: str | None = None,
    source_record_digest: str | None = None,
) -> ValidationFinding:
    return ValidationFinding(
        code=code,
        severity=severity,
        message=_MESSAGES[code],
        source_record_index=source_record_index,
        json_pointer=_safe_json_pointer(json_pointer),
        annotation_id=(
            annotation_id
            if isinstance(annotation_id, str) and _UUID5_URN_RE.fullmatch(annotation_id)
            else None
        ),
        source_record_digest=(
            source_record_digest
            if isinstance(source_record_digest, str)
            and _SHA256_RE.fullmatch(source_record_digest)
            else None
        ),
    )


def make_validation_finding(
    code: str,
    severity: Literal["fatal", "error", "warning", "skipped"],
    *,
    source_record_index: int | None = None,
    json_pointer: str | None = None,
    annotation_id: str | None = None,
    source_record_digest: str | None = None,
) -> ValidationFinding:
    """Build one catalog-owned, context-safe upstream finding."""

    if code not in ERROR_CATALOG or not _allowed_context_severity(code, severity):
        raise ValueError("validation finding code or severity is not context-safe")
    return _finding(
        code,
        severity,
        source_record_index=source_record_index,
        json_pointer=json_pointer,
        annotation_id=annotation_id,
        source_record_digest=source_record_digest,
    )


def make_validation_failure(
    code: str,
    *,
    input_count: int = 0,
    pack_id: str | None = None,
    semantic_digest: str | None = None,
    input_snapshot_digest: str | None = None,
    producer: str | None = None,
    adapter_version: str | None = None,
) -> ValidationResult:
    """Build one deterministic pre-artifact failure from a catalog code.

    Export and inspection preflights often fail before a Pack-shaped mapping
    exists.  Routing those failures through ``validate_pack({})`` would add
    unrelated schema diagnostics and make reports depend on schema traversal
    order.  This narrow factory preserves the same catalog and coherence gates
    as ordinary validation without accepting caller-provided text or findings.
    """

    if type(input_count) is not int or input_count < 0:
        raise ValueError("validation failure input count must be non-negative")
    finding = make_validation_finding(code, "fatal")
    result = ValidationResult(
        schema_version=VALIDATION_RESULT_SCHEMA_VERSION,
        validator_version=VALIDATOR_VERSION,
        status="failed",
        pack_id=pack_id,
        semantic_digest=semantic_digest,
        input_snapshot_digest=input_snapshot_digest,
        producer=producer,
        adapter_version=adapter_version,
        input_count=input_count,
        exported_count=0,
        skipped_count=0,
        warning_count=0,
        error_count=1,
        findings=(finding,),
    )
    _validate_result_coherence(result)
    return result


def _finding_wire(finding: ValidationFinding) -> dict[str, JSONValue]:
    return {
        "code": finding.code,
        "severity": finding.severity,
        "source_record_index": finding.source_record_index,
        "source_record_digest": finding.source_record_digest,
        "json_pointer": finding.json_pointer,
        "annotation_id": finding.annotation_id,
        "message": finding.message,
    }


def _finding_sort_key(
    finding: ValidationFinding,
) -> tuple[int, str, int, str, str, str, str]:
    return validation_report_finding_sort_key(_finding_wire(finding))


def _deduplicate_findings(
    findings: Sequence[ValidationFinding],
) -> list[ValidationFinding]:
    seen: set[tuple[object, ...]] = set()
    result: list[ValidationFinding] = []
    for finding in findings:
        key = (
            finding.code,
            finding.severity,
            finding.source_record_index,
            finding.json_pointer,
            finding.annotation_id,
            finding.source_record_digest,
            finding.message,
        )
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result


def _optional_digest(value: str | None, field: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest or None")
    return value


def _mapping(value: JSONValue) -> Mapping[str, JSONValue]:
    if not isinstance(value, Mapping):  # pragma: no cover - schema-gated
        raise TypeError("schema-gated value is not an object")
    return value


def _list(value: JSONValue) -> list[JSONValue]:
    if not isinstance(value, list):  # pragma: no cover - schema-gated
        raise TypeError("schema-gated value is not an array")
    return value


def _item_at(
    document: Mapping[str, JSONValue],
    index: int,
) -> Mapping[str, JSONValue] | None:
    items = document.get("items")
    if not isinstance(items, list) or index >= len(items):
        return None
    item = items[index]
    return item if isinstance(item, Mapping) else None


def _safe_item_count(document: Mapping[str, object]) -> int:
    items = document.get("items")
    return len(items) if isinstance(items, (list, tuple)) else 0


def _safe_nested_string(
    document: Mapping[str, object] | None,
    *path: str,
) -> str | None:
    value: object = document
    for part in path:
        if not isinstance(value, Mapping):
            return None
        value = value.get(part)
    return value if isinstance(value, str) else None


def _path_pointer(path: Sequence[object]) -> str:
    pointer = ""
    for part in path:
        pointer = _pointer_child(pointer, str(part))
    return pointer


def _pointer_child(pointer: str, part: str) -> str:
    escaped = part.replace("~", "~0").replace("/", "~1")
    return f"{pointer}/{escaped}"


def _safe_json_pointer(pointer: str | None) -> str | None:
    if pointer is None:
        return None
    if (
        not isinstance(pointer, str)
        or len(pointer) > 512
        or _JSON_POINTER_RE.fullmatch(pointer) is None
    ):
        return None
    decoded_segments = [
        segment.replace("~1", "/").replace("~0", "~")
        for segment in pointer.split("/")[1:]
    ]
    if decoded_segments and decoded_segments[0].casefold() in {
        "users",
        "home",
        "etc",
        "root",
        "tmp",
        "private",
        "volumes",
        "srv",
    }:
        return None
    for decoded in decoded_segments:
        if _key_looks_private(decoded) or _value_looks_private(decoded):
            return None
    return pointer


def _key_looks_private(key: str) -> bool:
    local = unicodedata.normalize("NFKC", key.rsplit(":", 1)[-1])
    normalized = "".join(
        character for character in local.casefold() if character.isalnum()
    )
    token_source = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", local)
    tokens = {
        token.casefold() for token in re.split(r"[^A-Za-z0-9]+", token_source) if token
    }
    return normalized in _FORBIDDEN_KEY_TERMS or bool(tokens & _FORBIDDEN_KEY_TOKENS)


def _scan_private_value_at(path: tuple[str, ...]) -> bool:
    """Exclude only source-faithful selector text from private-value scanning.

    Exact/prefix/suffix must preserve the EPUB resource byte semantics even
    when the source prose resembles a path.  Note bodies are producer output,
    so they retain the private-path, secret, mechanism, and local-authority
    scan before anything can be published.
    """

    if (
        len(path) >= 3
        and path[-1] in {"exact", "prefix", "suffix"}
        and path[-3] == "selector"
        and path[-2].isdigit()
    ):
        return False
    if (
        len(path) >= 4
        and path[-1] == "value"
        and path[-3] == "selector"
        and path[-2].isdigit()
        and int(path[-2]) >= 2
    ):
        return False
    if len(path) >= 2 and path[-2:] == ("target", "source"):
        return False
    if len(path) >= 2 and path[-2] == "sr:resourceHrefs" and path[-1].isdigit():
        return False
    return True


def _cfi_selector_value_path(path: tuple[str, ...]) -> bool:
    return bool(
        len(path) >= 4
        and path[-1] == "value"
        and path[-3] == "selector"
        and path[-2].isdigit()
        and int(path[-2]) >= 2
    )


def _cfi_value_looks_private(value: str) -> bool:
    decoded = decode_public_scan_value(value)
    if decoded is None:
        return True
    return not _bounded_epub_cfi(decoded)


def _bounded_epub_cfi(value: str) -> bool:
    """Accept the small numeric-step CFI surface v0 can publish.

    This is deliberately a structural gate, not a list of private directory
    names.  The v0 producer only needs package/content paths, optional bounded
    ID assertions, and the documented three-part range form.  Rejecting every
    non-numeric path step closes arbitrary absolute-path spellings without
    trying to enumerate host directories.
    """

    if (
        len(value) > 2048
        or not value.startswith("epubcfi(")
        or not value.endswith(")")
        or any(unicodedata.category(character) == "Cc" for character in value)
    ):
        return False
    payload = value[len("epubcfi(") : -1]
    components = _cfi_range_components(payload)
    if components is None or len(components) not in {1, 3}:
        return False

    step_count = 0
    for component in components:
        segments = component.split("!")
        if not segments or any(not segment for segment in segments):
            return False
        for segment in segments:
            valid, steps = _bounded_cfi_path(segment)
            if not valid:
                return False
            step_count += steps
            if step_count > _CFI_MAX_STEPS:
                return False
    return True


def _cfi_range_components(payload: str) -> tuple[str, ...] | None:
    if not payload:
        return None
    components: list[str] = []
    start = 0
    in_assertion = False
    escaped = False
    for index, character in enumerate(payload):
        if escaped:
            escaped = False
            continue
        if in_assertion and character == "^":
            escaped = True
            continue
        if character == "[":
            if in_assertion:
                return None
            in_assertion = True
            continue
        if character == "]":
            if not in_assertion:
                return None
            in_assertion = False
            continue
        if character == "," and not in_assertion:
            components.append(payload[start:index])
            start = index + 1
    if in_assertion or escaped:
        return None
    components.append(payload[start:])
    return tuple(components)


def _bounded_cfi_path(value: str) -> tuple[bool, int]:
    index = 0
    steps = 0
    length = len(value)
    while index < length:
        if value[index] != "/":
            return False, steps
        index += 1
        digit_start = index
        while index < length and "0" <= value[index] <= "9":
            index += 1
        if _CFI_STEP_RE.fullmatch(value[digit_start:index]) is None:
            return False, steps
        steps += 1

        if index < length and value[index] == "[":
            assertion_end = _cfi_assertion_end(value, index)
            if assertion_end is None:
                return False, steps
            index = assertion_end

        if index < length and value[index] == ":":
            index += 1
            offset_start = index
            while index < length and "0" <= value[index] <= "9":
                index += 1
            if _CFI_OFFSET_RE.fullmatch(value[offset_start:index]) is None:
                return False, steps
            if index < length and value[index] == "[":
                assertion_end = _cfi_assertion_end(value, index)
                if assertion_end is None:
                    return False, steps
                index = assertion_end
            if index != length:
                return False, steps

        if index < length and value[index] != "/":
            return False, steps
    return steps > 0, steps


def _cfi_assertion_end(value: str, start: int) -> int | None:
    index = start + 1
    code_points = 0
    while index < len(value):
        character = value[index]
        if character == "]":
            return index + 1 if code_points else None
        if character == "^":
            index += 1
            if index >= len(value) or value[index] not in "[](),;=^":
                return None
            code_points += 1
            index += 1
            continue
        if (
            character in "/\\?#@"
            or character in "[()"
            or character.isspace()
            or unicodedata.category(character).startswith("C")
        ):
            return None
        code_points += 1
        if code_points > _CFI_MAX_ASSERTION_CODE_POINTS:
            return None
        index += 1
    return None


def _value_looks_private(value: str) -> bool:
    if not value:
        return False
    decoded = decode_public_scan_value(value)
    if decoded is None:
        return True
    scan_value = unicodedata.normalize("NFKC", decoded)
    lowered = scan_value.casefold().replace("\\", "/")
    try:
        parsed = urlsplit(scan_value)
    except ValueError:
        return True
    embedded_authority_is_private = _embedded_authority_is_private(scan_value)
    display_scan = _EMBEDDED_URL_RE.sub("public-url", scan_value)
    if (not parsed.netloc and not is_public_display_metadata(display_scan)) or any(
        unicodedata.category(character) == "Cc" for character in scan_value
    ):
        return True
    authority_is_private = _uri_authority_is_private(parsed)
    return (
        any(fragment.casefold() in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS)
        or _FILE_SCHEME_RE.search(scan_value) is not None
        or _WINDOWS_PATH_RE.search(scan_value) is not None
        or _POSIX_PRIVATE_PATH_RE.search(scan_value) is not None
        or _HOME_PATH_RE.search(scan_value) is not None
        or _SECRET_QUERY_RE.search(scan_value) is not None
        or authority_is_private
        or embedded_authority_is_private
    )


def _embedded_authority_is_private(value: str) -> bool:
    """Reject unsafe authorities even when a URL is embedded in prose."""

    for match in _EMBEDDED_AUTHORITY_RE.finditer(value):
        scheme = match.group("scheme")
        authority = match.group("authority").rstrip(".,;!?)}")
        if not authority or scheme.casefold() in {"file", "javascript", "data"}:
            return True
        try:
            parsed = urlsplit(f"{scheme}://{authority}")
        except ValueError:
            return True
        if _uri_authority_is_private(parsed):
            return True
    return False


def _safe_namespace_iri(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    scheme = parsed.scheme.casefold()
    if scheme == "urn":
        return bool(parsed.path) and not parsed.query
    if scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    if not _hostname_is_public(parsed.hostname):
        return False
    if _SECRET_QUERY_RE.search(value):
        return False
    return True


def _safe_public_iri(value: str) -> bool:
    decoded = decode_public_scan_value(value)
    if decoded is None:
        return False
    try:
        parsed = urlsplit(decoded)
    except ValueError:
        return False
    scheme = parsed.scheme.casefold()
    if not scheme or scheme in {"data", "file", "javascript"}:
        return False
    if _SECRET_QUERY_RE.search(decoded) or _uri_authority_is_private(parsed):
        return False
    if scheme in {"http", "https"}:
        return bool(parsed.netloc)
    return not _value_looks_private(decoded)


def _uri_authority_is_private(parsed: Any) -> bool:
    if not parsed.netloc:
        return parsed.scheme.casefold() in {"http", "https"}
    try:
        hostname = parsed.hostname
        _port = parsed.port
    except ValueError:
        return True
    return (
        not hostname
        or parsed.username is not None
        or parsed.password is not None
        or not _hostname_is_public(hostname)
    )


def _hostname_is_public(hostname: str) -> bool:
    unicode_candidate = hostname.translate(_UNICODE_DOT_TRANSLATION).rstrip(".")
    if not unicode_candidate or "%" in unicode_candidate:
        return False
    try:
        address = ipaddress.ip_address(unicode_candidate)
    except ValueError:
        address = None
    if address is not None:
        return address.is_global and not address.is_multicast
    try:
        candidate = unicode_candidate.encode("idna").decode("ascii").casefold()
    except UnicodeError:
        return False
    labels = candidate.split(".")
    if (
        not candidate
        or len(candidate) > 253
        or any(_DNS_LABEL_RE.fullmatch(label) is None for label in labels)
    ):
        return False
    if (
        candidate == "localhost"
        or candidate.endswith(".localhost")
        or candidate.endswith(".local")
        or candidate.endswith(".internal")
        or candidate.endswith(".lan")
    ):
        return False
    if _LEGACY_IPV4_HOST_RE.fullmatch(candidate) is None:
        return True
    legacy_address = _parse_legacy_ipv4(candidate)
    return bool(
        legacy_address is not None
        and legacy_address.is_global
        and not legacy_address.is_multicast
    )


def _parse_legacy_ipv4(hostname: str) -> ipaddress.IPv4Address | None:
    parts = hostname.split(".")
    if not 1 <= len(parts) <= 4:
        return None
    values: list[int] = []
    for part in parts:
        try:
            if part.casefold().startswith("0x"):
                value = int(part[2:], 16)
            elif len(part) > 1 and part.startswith("0"):
                value = int(part, 8)
            else:
                value = int(part, 10)
        except ValueError:
            return None
        values.append(value)
    limits = {
        1: (0xFFFFFFFF,),
        2: (0xFF, 0xFFFFFF),
        3: (0xFF, 0xFF, 0xFFFF),
        4: (0xFF, 0xFF, 0xFF, 0xFF),
    }[len(values)]
    if any(value > limit for value, limit in zip(values, limits, strict=True)):
        return None
    if len(values) == 1:
        packed = values[0]
    elif len(values) == 2:
        packed = (values[0] << 24) | values[1]
    elif len(values) == 3:
        packed = (values[0] << 24) | (values[1] << 16) | values[2]
    else:
        packed = (values[0] << 24) | (values[1] << 16) | (values[2] << 8) | values[3]
    return ipaddress.IPv4Address(packed)


def _canonical_epub_href(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return normalize_epub_href(value) == value
    except ValueError:
        return False


__all__ = [
    "ERROR_CATALOG",
    "EXPORT_PIPELINE_CODES",
    "FUTURE_PIPELINE_CODES",
    "PACK_VALIDATOR_CODES",
    "UPSTREAM_VALIDATION_CODES",
    "VALIDATION_REPORT_CANONICALIZATION",
    "VALIDATION_REPORT_SCHEMA_VERSION",
    "VALIDATION_RESULT_SCHEMA_VERSION",
    "VALIDATOR_VERSION",
    "ValidationContext",
    "ValidationReport",
    "ValidationResult",
    "finalize_validation_report",
    "make_validation_finding",
    "make_validation_failure",
    "serialize_validation_report",
    "validate_pack",
    "validation_report_wire",
]
