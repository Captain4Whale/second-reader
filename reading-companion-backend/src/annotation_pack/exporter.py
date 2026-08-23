"""Explicit, crash-safe publication orchestration for Annotation Pack v0.

The exporter can publish canonical development JSON or the complete detached
deliverable set.  It is not part of the normal reading runner and it does not
expose arbitrary producer paths.  All producer-specific knowledge remains
behind the ``SecondReaderProducerAdapter`` boundary.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import suppress
import ctypes
from dataclasses import dataclass
from datetime import datetime
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from types import MappingProxyType
from typing import Any, Callable, Literal, NoReturn, Protocol, cast
import unicodedata
from uuid import UUID, uuid4

from src.annotation_pack.anchors import AnchorBuilder, AnchorResolutionError
from src.annotation_pack.builder import (
    AnnotationPackBuildError,
    AnnotationPackBuilder,
    AnnotationPackDocument,
    Clock,
    CreatorInput,
    DeterministicIdFactory,
    GeneratorInput,
    ProvenanceInput,
    SystemClock,
)
from src.annotation_pack.drafts import (
    ProducerAdapterError,
    ProducerDraftResult,
    ResolvedAnnotationDraft,
    ValidationFinding,
)
from src.annotation_pack.epub_source import (
    EpubSourceError,
    verify_epub_source,
)
from src.annotation_pack.identity import (
    PublicationIdentityBuilder,
    PublicationIdentityError,
    PublicationIdentityResult,
)
from src.annotation_pack.ids import default_generator_id, track_id as derive_track_id
from src.annotation_pack.packaging import (
    MAX_DETACHED_PACKAGE_BYTES,
    PackageError,
    build_detached_annotations,
    validate_detached_annotations,
)
from src.annotation_pack.producers.second_reader import (
    ADAPTER_VERSION,
    SecondReaderProducerAdapter,
)
from src.annotation_pack.schema import (
    PUBLICATION_POINTER_SCHEMA_ID,
    VALIDATION_REPORT_SCHEMA_ID,
    auxiliary_validator,
)
from src.annotation_pack.serialization import canonical_json_bytes, serialize_pack
from src.annotation_pack.validation import (
    ERROR_CATALOG,
    VALIDATION_REPORT_SCHEMA_VERSION,
    VALIDATOR_VERSION,
    ValidationContext,
    ValidationReport,
    ValidationResult,
    finalize_validation_report,
    make_validation_failure,
    make_validation_finding,
    serialize_validation_report,
    validate_pack,
)
from src.config import get_backend_runtime_root
from src.reading_core.storage import book_document_file
from src.reading_runtime.artifacts import (
    annotation_pack_annotations_file,
    annotation_pack_current_pointer_file,
    annotation_pack_detached_file,
    annotation_pack_last_failed_report_file,
    annotation_pack_revision_dir,
    annotation_pack_revisions_dir,
    annotation_pack_track_dir,
    annotation_pack_validation_report_file,
    existing_run_state_file,
)
from src.reading_runtime.job_lease import (
    JobLeaseConflict,
    JobLeaseReadError,
    guard_book_writer_exclusion,
)


ExportStatus = Literal["published", "degraded", "unchanged", "failed"]
Deliverables = Literal["json", "detached"]

MAX_BOOK_DOCUMENT_BYTES = 512 * 1024 * 1024
MAX_ANNOTATIONS_JSON_BYTES = 16 * 1024 * 1024
MAX_VALIDATION_REPORT_BYTES = 4 * 1024 * 1024
MAX_PUBLICATION_POINTER_BYTES = 64 * 1024
MAX_RUN_STATE_BYTES = 1024 * 1024
MAX_BOOK_DOCUMENT_JSON_DEPTH = 128
MAX_BOOK_DOCUMENT_JSON_NODES = 10_000_000
MAX_AUXILIARY_JSON_DEPTH = 64
MAX_AUXILIARY_JSON_NODES = 100_000
FILE_HASH_CHUNK_BYTES = 1024 * 1024

PUBLICATION_POINTER_SCHEMA_VERSION = "annotation-pack-publication-pointer/0.1"
INPUT_SNAPSHOT_HEADER = b"SECOND-READER-INPUT-SNAPSHOT-V1\n"
REVISION_HEADER = b"SECOND-READER-ANNOTATION-PUBLICATION-REVISION-V1\n"
SECOND_READER_PRODUCER_ID = "urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a"
GENERATOR_NAME = "Second Reader Annotation Pack Exporter"
GENERATOR_VERSION = "0.1.0"

_TRACK_KEY = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z", re.ASCII)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_UUID5_URN = re.compile(
    r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z",
    re.ASCII,
)
_RUN_STAGES = frozenset(
    {"ready", "parsing_structure", "deep_reading", "completed", "paused", "error"}
)
_INSPECTOR_CAPABILITY_ORDER = (
    "TextQuoteSelector",
    "sr:ParagraphCharSelector",
    "sr:EpubCfiSelector",
    "epubcfi",
)


@dataclass(frozen=True, slots=True)
class ExportPolicy:
    deliverables: Deliverables = "detached"
    allow_partial: bool = False
    allow_skips: bool = False
    allow_empty: bool = False
    force_regenerate: bool = False


@dataclass(frozen=True, slots=True)
class ExportResult:
    status: ExportStatus
    pack: AnnotationPackDocument | None
    annotations_json: Path | None
    detached_package: Path | None
    validation: ValidationResult
    validation_report: Path | None
    current_pointer: Path | None
    revision_id: str | None


@dataclass(frozen=True, slots=True)
class InspectionResult:
    valid: bool
    pack_id: str | None
    track_id: str | None
    semantic_digest: str | None
    item_counts: Mapping[str, int]
    anchor_capabilities: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]


@dataclass(frozen=True, slots=True)
class _FileSnapshot:
    device: int
    inode: int
    mode: int
    byte_length: int
    mtime_ns: int
    ctime_ns: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> _FileSnapshot:
        return cls(
            device=value.st_dev,
            inode=value.st_ino,
            mode=value.st_mode,
            byte_length=value.st_size,
            mtime_ns=value.st_mtime_ns,
            ctime_ns=value.st_ctime_ns,
        )


@dataclass(frozen=True, slots=True)
class _FileIdentity:
    device: int
    inode: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> _FileIdentity:
        return cls(device=value.st_dev, inode=value.st_ino)


@dataclass(frozen=True, slots=True)
class _JsonSnapshot:
    value: Mapping[str, Any]
    content: bytes
    sha256: str
    file: _FileSnapshot


@dataclass(frozen=True, slots=True)
class _BinarySnapshot:
    content: bytes
    sha256: str
    file: _FileSnapshot


@dataclass(frozen=True, slots=True)
class _CurrentPublication:
    pointer_path: Path
    track_root: Path
    revisions_root: Path
    revision_dir: Path
    annotations_path: Path
    package_path: Path | None
    report_path: Path
    revision_id: str
    document: Mapping[str, Any]
    validation: ValidationResult
    report: ValidationReport
    pointer_snapshot: _JsonSnapshot
    annotations_snapshot: _JsonSnapshot
    package_snapshot: _BinarySnapshot | None
    report_snapshot: _JsonSnapshot
    expected_files: frozenset[str]
    track_descriptor: int
    revisions_descriptor: int
    revision_descriptor: int


@dataclass(frozen=True, slots=True)
class _PriorPointer:
    content: bytes | None
    sha256: str | None
    file: _FileSnapshot | None


@dataclass(frozen=True, slots=True)
class _FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class _ExportFailure(RuntimeError):
    __slots__ = ("code", "validation")

    def __init__(
        self,
        code: str,
        *,
        validation: ValidationResult | None = None,
    ) -> None:
        self.code = code
        self.validation = validation
        super().__init__(code)


class _WriterExclusion(Protocol):
    def assert_current(self) -> None: ...


class _DuplicateJsonKey(ValueError):
    pass


def _immutable_json(*_args: object, **_kwargs: object) -> NoReturn:
    raise TypeError("inspection/publication document is immutable")


class _FrozenJsonDict(dict[str, Any]):
    __setitem__ = _immutable_json
    __delitem__ = _immutable_json
    clear = _immutable_json
    pop = _immutable_json
    popitem = _immutable_json
    setdefault = _immutable_json
    update = _immutable_json
    __ior__ = _immutable_json


class _FrozenJsonList(list[Any]):
    __setitem__ = _immutable_json
    __delitem__ = _immutable_json
    __iadd__ = _immutable_json
    __imul__ = _immutable_json
    append = _immutable_json
    clear = _immutable_json
    extend = _immutable_json
    insert = _immutable_json
    pop = _immutable_json
    remove = _immutable_json
    reverse = _immutable_json
    sort = _immutable_json


def resolve_book_output_dir(
    *,
    book_id: str | None = None,
    book_output_dir: Path | None = None,
    output_root: Path | None = None,
) -> Path:
    """Resolve one existing, regular direct child of the configured output root."""

    if (book_id is None) == (book_output_dir is None):
        raise ValueError("exactly one book location must be supplied")
    root_input = output_root or (get_backend_runtime_root() / "output")
    if not isinstance(root_input, Path):
        raise TypeError("output_root must be a Path")
    root = _existing_real_directory(root_input)

    if book_id is not None:
        if not _safe_book_child_name(book_id):
            raise ValueError("book id is not a safe direct-child name")
        assert isinstance(book_id, str)
        requested_name = book_id
    else:
        if not isinstance(book_output_dir, Path):
            raise TypeError("book_output_dir must be a Path")
        if ".." in book_output_dir.parts:
            raise ValueError("book output path contains traversal")
        candidate_input = book_output_dir
        if not candidate_input.is_absolute():
            candidate_input = Path.cwd() / candidate_input
        try:
            candidate_input = Path(os.path.abspath(os.fspath(candidate_input)))
        except (OSError, TypeError, ValueError):
            raise ValueError("book output path is invalid") from None
        if candidate_input.parent != root:
            raise ValueError("book output path must be a direct output-root child")
        requested_name = candidate_input.name

    if not _safe_book_child_name(requested_name):
        raise ValueError("book output directory name is unsafe")
    return _exact_output_child_directory(root, requested_name)


def second_reader_input_snapshot_digest(
    *,
    source_epub_sha256: str,
    book_document_sha256: str,
    substrate_sha256: str,
    reaction_ledger_sha256: str,
    resolved_records: Sequence[ResolvedAnnotationDraft],
) -> str:
    """Hash the frozen E/B/S/L/R producer snapshot framing."""

    digests = (
        _digest_value(source_epub_sha256, "source_epub_sha256"),
        _digest_value(book_document_sha256, "book_document_sha256"),
        _digest_value(substrate_sha256, "substrate_sha256"),
        _digest_value(reaction_ledger_sha256, "reaction_ledger_sha256"),
    )
    if not isinstance(resolved_records, Sequence) or isinstance(
        resolved_records, (str, bytes, bytearray)
    ):
        raise TypeError("resolved_records must be a sequence")
    try:
        records = tuple(resolved_records)
    except Exception:
        raise ValueError("resolved records could not be snapshotted") from None
    framed_records: list[tuple[int, str]] = []
    for record in records:
        if type(record) is not ResolvedAnnotationDraft:
            raise TypeError("resolved_records contains an invalid record")
        index = record.source_record_index
        digest = record.source_record_digest
        if type(index) is not int or index < 0:
            raise ValueError("resolved record index is invalid")
        framed_records.append((index, _digest_value(digest, "source_record_digest")))
    framed_records.sort(key=lambda item: (item[0], item[1]))

    stream = bytearray(INPUT_SNAPSHOT_HEADER)
    for tag, value in zip(("E", "B", "S", "L"), digests, strict=True):
        stream.extend(_digest_frame(tag, value))
    for _index, digest in framed_records:
        stream.extend(_digest_frame("R", digest))
    return hashlib.sha256(stream).hexdigest()


def publication_revision_id(
    *,
    annotations_json_sha256: str,
    package_sha256: str | None,
    validation_report_sha256: str,
) -> str:
    """Return the immutable revision id for one complete deliverable set."""

    annotations_digest = _digest_value(
        annotations_json_sha256, "annotations_json_sha256"
    )
    report_digest = _digest_value(
        validation_report_sha256, "validation_report_sha256"
    )
    if package_sha256 is None:
        package_digest = ""
    else:
        package_digest = _digest_value(package_sha256, "package_sha256")
    stream = bytearray(REVISION_HEADER)
    stream.extend(_revision_frame("J", annotations_digest))
    stream.extend(_revision_frame("P", package_digest))
    stream.extend(_revision_frame("R", report_digest))
    return hashlib.sha256(stream).hexdigest()


def track_slug(track_key: str, track_id: str) -> str:
    """Return the safe path slug for one logical Annotation Track."""

    if type(track_key) is not str or _TRACK_KEY.fullmatch(track_key) is None:
        raise ValueError("track key is invalid")
    if type(track_id) is not str or _UUID5_URN.fullmatch(track_id) is None:
        raise ValueError("track id is not a canonical UUIDv5 URN")
    identifier = UUID(track_id.removeprefix("urn:uuid:"))
    return f"{track_key}-{identifier.hex[:12]}"


def export_annotation_pack(
    *,
    output_dir: Path,
    track_key: str,
    creator: CreatorInput,
    policy: ExportPolicy = ExportPolicy(),
    generated_at: datetime | None = None,
    output_root: Path | None = None,
    runtime_root: Path | None = None,
    track_name: str | None = None,
) -> ExportResult:
    """Build, validate, and atomically publish one explicit deliverable set."""

    try:
        if not isinstance(output_dir, Path):
            raise TypeError("output_dir must be a Path")
        resolved_output = resolve_book_output_dir(
            book_output_dir=output_dir,
            output_root=output_root,
        )
    except (OSError, TypeError, ValueError):
        return _early_failed_result("output_path_invalid")

    if type(policy) is not ExportPolicy or not _valid_policy(policy):
        return _early_failed_result("export_configuration_invalid")
    if type(track_key) is not str or _TRACK_KEY.fullmatch(track_key) is None:
        return _early_failed_result("export_configuration_invalid")
    if type(creator) is not CreatorInput:
        return _early_failed_result("export_configuration_invalid")
    if generated_at is not None and type(generated_at) is not datetime:
        return _early_failed_result("invalid_generated_timestamp")
    if runtime_root is not None and not isinstance(runtime_root, Path):
        return _early_failed_result("export_configuration_invalid")

    lease_root = runtime_root or get_backend_runtime_root()
    try:
        # This is intentionally the first stateful/read-side operation after
        # pure configuration/path validation.  The guard remains held through
        # the final pointer fsync.
        with guard_book_writer_exclusion(
            resolved_output.name,
            root=lease_root,
        ) as writer_exclusion:
            return _export_under_writer_guard(
                output_dir=resolved_output,
                track_key=track_key,
                creator=creator,
                policy=policy,
                generated_at=generated_at,
                track_name=track_name,
                writer_exclusion=writer_exclusion,
            )
    except (JobLeaseConflict, JobLeaseReadError):
        return _early_failed_result("active_writer_present")
    except Exception:
        # Guard conflicts use the typed branch above.  An exception escaping
        # the guarded exporter is an internal failure, never lease evidence.
        return _early_failed_result("export_internal_error")


def inspect_annotation_pack(source: Path) -> InspectionResult:
    """Inspect one JSON or detached Pack without returning text or local paths."""

    empty_counts = MappingProxyType({"total": 0, "highlight": 0, "note": 0})
    if not isinstance(source, Path):
        validation = make_validation_failure("schema_validation_failed")
        return InspectionResult(
            valid=False,
            pack_id=None,
            track_id=None,
            semantic_digest=None,
            item_counts=empty_counts,
            anchor_capabilities=(),
            findings=validation.findings,
        )
    try:
        if source.suffix == ".annotations":
            package = validate_detached_annotations(source)
            document = package.document
            validation = package.validation
        elif source.suffix == ".json":
            snapshot = _read_json_snapshot(
                source,
                maximum_bytes=MAX_ANNOTATIONS_JSON_BYTES,
                unavailable_code="schema_validation_failed",
                invalid_code="schema_validation_failed",
                limit_code="document_limit_exceeded",
                mutation_code="schema_validation_failed",
                maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
                maximum_nodes=MAX_AUXILIARY_JSON_NODES,
            )
            if canonical_json_bytes(snapshot.value) != snapshot.content:
                raise _ExportFailure("schema_validation_failed")
            document = snapshot.value
            validation = validate_pack(
                document,
                context=ValidationContext(allow_empty=True),
            )
        else:
            raise _ExportFailure("schema_validation_failed")
    except PackageError:
        validation = make_validation_failure("package_entry_invalid")
        return InspectionResult(
            valid=False,
            pack_id=None,
            track_id=None,
            semantic_digest=None,
            item_counts=empty_counts,
            anchor_capabilities=(),
            findings=validation.findings,
        )
    except _ExportFailure as exc:
        validation = make_validation_failure(exc.code)
        return InspectionResult(
            valid=False,
            pack_id=None,
            track_id=None,
            semantic_digest=None,
            item_counts=empty_counts,
            anchor_capabilities=(),
            findings=validation.findings,
        )
    except Exception:
        validation = make_validation_failure("schema_validation_failed")
        return InspectionResult(
            valid=False,
            pack_id=None,
            track_id=None,
            semantic_digest=None,
            item_counts=empty_counts,
            anchor_capabilities=(),
            findings=validation.findings,
        )

    counts = _inspection_counts(document)
    capabilities = _inspection_capabilities(document) if validation.publishable else ()
    track_identifier = _nested_string(document, "sr:track", "id")
    return InspectionResult(
        valid=validation.publishable,
        pack_id=validation.pack_id,
        track_id=track_identifier if _UUID5_URN.fullmatch(track_identifier or "") else None,
        semantic_digest=validation.semantic_digest,
        item_counts=MappingProxyType(counts),
        anchor_capabilities=capabilities,
        findings=validation.findings,
    )


def _export_under_writer_guard(
    *,
    output_dir: Path,
    track_key: str,
    creator: CreatorInput,
    policy: ExportPolicy,
    generated_at: datetime | None,
    track_name: str | None,
    writer_exclusion: _WriterExclusion,
) -> ExportResult:
    known_track_slug: str | None = None
    input_count = 0
    pack_identity: tuple[str | None, str | None, str | None] = (None, None, None)
    try:
        run_stage = _load_run_stage(output_dir)
        if run_stage in {"parsing_structure", "deep_reading"}:
            raise _ExportFailure("run_state_not_exportable")
        if run_stage in {"paused", "error"} and not policy.allow_partial:
            raise _ExportFailure("run_state_not_exportable")

        adapter = SecondReaderProducerAdapter()
        producer_snapshot = adapter.load_drafts(output_dir=output_dir)
        input_count = producer_snapshot.input_count
        _require_exportable_run_state(
            run_stage,
            input_count=input_count,
            policy=policy,
        )

        book_snapshot = _read_json_snapshot(
            book_document_file(output_dir),
            maximum_bytes=MAX_BOOK_DOCUMENT_BYTES,
            unavailable_code="book_document_unavailable",
            invalid_code="book_document_invalid_json",
            limit_code="book_document_limit_exceeded",
            mutation_code="input_changed_during_export",
            maximum_depth=MAX_BOOK_DOCUMENT_JSON_DEPTH,
            maximum_nodes=MAX_BOOK_DOCUMENT_JSON_NODES,
        )
        verified_source = verify_epub_source(output_dir)
        publication = PublicationIdentityBuilder().build_verified(
            verified_source=verified_source,
            persisted_book_document=book_snapshot.value,
        )

        track_identifier = _track_identifier(
            publication=publication,
            creator=creator,
            track_key=track_key,
        )
        known_track_slug = track_slug(track_key, track_identifier)

        resolved, findings = _resolve_records(
            producer_snapshot=producer_snapshot,
            publication=publication,
            allow_skips=policy.allow_skips,
        )
        findings = (*_identity_findings(publication), *findings)

        snapshot_digest = second_reader_input_snapshot_digest(
            source_epub_sha256=verified_source.sha256,
            book_document_sha256=book_snapshot.sha256,
            substrate_sha256=publication.substrate_sha256,
            reaction_ledger_sha256=producer_snapshot.reaction_ledger_sha256,
            resolved_records=resolved,
        )
        clock: Clock = (
            _FixedClock(generated_at) if generated_at is not None else SystemClock()
        )
        pack = AnnotationPackBuilder(
            id_factory=DeterministicIdFactory(),
            clock=clock,
        ).build(
            publication=publication,
            track_key=track_key,
            track_name=track_name,
            creator=creator,
            annotations=resolved,
            generator=GeneratorInput(
                id=default_generator_id(),
                name=GENERATOR_NAME,
                version=GENERATOR_VERSION,
            ),
            provenance=ProvenanceInput(
                producer=SECOND_READER_PRODUCER_ID,
                adapter_version=ADAPTER_VERSION,
                input_snapshot_digest=snapshot_digest,
            ),
        )
        validation_context = ValidationContext(
            input_count=producer_snapshot.input_count,
            findings=tuple(findings),
            # ``allow_empty`` covers a genuinely empty current track.  It does
            # not make a non-empty input publishable when every row was
            # explicitly skipped.
            allow_empty=policy.allow_empty
            and not (
                producer_snapshot.input_count > 0
                and not resolved
                and any(finding.severity == "skipped" for finding in findings)
            ),
        )
        validation = validate_pack(pack, context=validation_context)
        pack_identity = (
            validation.pack_id,
            validation.semantic_digest,
            validation.input_snapshot_digest,
        )
        if not validation.publishable:
            raise _ExportFailure("schema_validation_failed", validation=validation)

        annotations_bytes = serialize_pack(pack)
        if len(annotations_bytes) > MAX_ANNOTATIONS_JSON_BYTES:
            raise _ExportFailure("document_limit_exceeded")
        annotations_digest = hashlib.sha256(annotations_bytes).hexdigest()

        # Snapshot equality is checked after every expensive pure operation and
        # immediately before current-pointer inspection/publication.
        _assert_file_unchanged(
            book_document_file(output_dir),
            expected_digest=book_snapshot.sha256,
            expected_snapshot=book_snapshot.file,
            maximum_bytes=MAX_BOOK_DOCUMENT_BYTES,
            unavailable_code="input_changed_during_export",
        )
        second_producer_snapshot = adapter.load_drafts(output_dir=output_dir)
        if second_producer_snapshot != producer_snapshot:
            raise _ExportFailure("input_changed_during_export")
        verified_source.assert_unchanged()
        final_run_stage = _load_run_stage(output_dir)
        _require_exportable_run_state(
            final_run_stage,
            input_count=producer_snapshot.input_count,
            policy=policy,
        )

        def assert_reversible_boundary() -> None:
            _assert_writer_exclusion_current(writer_exclusion)
            _assert_file_unchanged(
                book_document_file(output_dir),
                expected_digest=book_snapshot.sha256,
                expected_snapshot=book_snapshot.file,
                maximum_bytes=MAX_BOOK_DOCUMENT_BYTES,
                unavailable_code="input_changed_during_export",
            )
            if adapter.load_drafts(output_dir=output_dir) != producer_snapshot:
                raise _ExportFailure("input_changed_during_export")
            verified_source.assert_unchanged()
            latest_run_stage = _load_run_stage(output_dir)
            _require_exportable_run_state(
                latest_run_stage,
                input_count=producer_snapshot.input_count,
                policy=policy,
            )

        current = _load_current_publication(
            output_dir=output_dir,
            track_slug_value=known_track_slug,
            expected_track_id=track_identifier,
        )
        publication_annotations_bytes = annotations_bytes
        publication_annotations_digest = annotations_digest
        publication_pack = pack
        publication_validation = validation
        # ``json`` is a minimum deliverable requirement, not a request to
        # retract an already-published package.  Force still rebuilds from the
        # fresh candidate, while publication remains monotonic once a track has
        # a detached deliverable.
        effective_deliverables: Deliverables = (
            "detached"
            if current is not None and current.package_path is not None
            else policy.deliverables
        )
        try:
            if current is not None and not policy.force_regenerate:
                current_semantic = _nested_string(
                    current.document, "sr:semanticDigest", "sr:value"
                )
                current_snapshot_digest = _nested_string(
                    current.document,
                    "sr:provenance",
                    "sr:inputSnapshotDigest",
                    "sr:value",
                )
                current_with_fresh_context = validate_pack(
                    current.document,
                    context=validation_context,
                )
                if (
                    current_semantic == validation.semantic_digest
                    and current_snapshot_digest == validation.input_snapshot_digest
                    and _validation_equivalent(current_with_fresh_context, validation)
                    and _report_matches_validation(current.report, validation)
                ):
                    # The neutral worker guard excludes product writers, but a
                    # local/external process can still replace any publication
                    # path.  Reassert the complete selected revision after the
                    # final semantic validation and immediately before exposing
                    # it as unchanged.
                    if (
                        policy.deliverables == "json"
                        or current.package_path is not None
                    ):
                        assert_reversible_boundary()
                        _assert_current_publication_unchanged(current)
                        return ExportResult(
                            status="unchanged",
                            pack=_freeze_current_pack(current.document),
                            annotations_json=current.annotations_path,
                            detached_package=current.package_path,
                            validation=current_with_fresh_context,
                            validation_report=current.report_path,
                            current_pointer=current.pointer_path,
                            revision_id=current.revision_id,
                        )

                    # Byte-preserving JSON-only -> detached upgrade.  The old
                    # revision remains immutable; the exact already-published
                    # JSON bytes are packaged into a new complete revision and
                    # validated again with the current validator.
                    _assert_current_publication_unchanged(current)
                    publication_annotations_bytes = current.annotations_snapshot.content
                    publication_annotations_digest = current.annotations_snapshot.sha256
                    publication_pack = _freeze_current_pack(current.document)
                    publication_validation = current_with_fresh_context
        finally:
            if current is not None:
                _close_current_publication(current)

        package_bytes: bytes | None = None
        package_digest: str | None = None
        if effective_deliverables == "detached":
            try:
                packaged = build_detached_annotations(publication_annotations_bytes)
            except PackageError:
                raise _ExportFailure("package_entry_invalid") from None
            if packaged.annotations_json_sha256 != publication_annotations_digest:
                raise _ExportFailure("package_entry_invalid")
            package_bytes = packaged.package_bytes
            package_digest = packaged.sha256

        report = finalize_validation_report(
            publication_validation,
            annotations_json_sha256=publication_annotations_digest,
            package_sha256=package_digest,
        )
        report_bytes = serialize_validation_report(report)
        if len(report_bytes) > MAX_VALIDATION_REPORT_BYTES:
            raise _ExportFailure("validation_report_invalid")
        report_digest = hashlib.sha256(report_bytes).hexdigest()
        revision_id = publication_revision_id(
            annotations_json_sha256=publication_annotations_digest,
            package_sha256=package_digest,
            validation_report_sha256=report_digest,
        )
        annotations_path, package_path, report_path, pointer_path = _publish_json_revision(
            output_dir=output_dir,
            track_slug_value=known_track_slug,
            track_identifier=track_identifier,
            revision_id=revision_id,
            semantic_digest=cast(str, publication_validation.semantic_digest),
            annotations_bytes=publication_annotations_bytes,
            annotations_sha256=publication_annotations_digest,
            package_bytes=package_bytes,
            package_sha256=package_digest,
            report_bytes=report_bytes,
            report_sha256=report_digest,
            assert_reversible_boundary=assert_reversible_boundary,
        )
        return ExportResult(
            status=(
                "degraded"
                if publication_validation.status == "degraded"
                else "published"
            ),
            pack=publication_pack,
            annotations_json=annotations_path,
            detached_package=package_path,
            validation=publication_validation,
            validation_report=report_path,
            current_pointer=pointer_path,
            revision_id=revision_id,
        )
    except ProducerAdapterError as exc:
        validation = make_validation_failure(exc.code, input_count=input_count)
    except (EpubSourceError, PublicationIdentityError) as exc:
        code = _fatal_catalog_code(
            exc.code,
            fallback="publication_identity_missing",
        )
        validation = make_validation_failure(code, input_count=input_count)
    except AnnotationPackBuildError as exc:
        code = _builder_failure_code(exc.code)
        validation = make_validation_failure(
            code,
            input_count=input_count,
            pack_id=pack_identity[0],
            semantic_digest=pack_identity[1],
            input_snapshot_digest=pack_identity[2],
        )
    except _ExportFailure as exc:
        validation = exc.validation or make_validation_failure(
            exc.code,
            input_count=input_count,
            pack_id=pack_identity[0],
            semantic_digest=pack_identity[1],
            input_snapshot_digest=pack_identity[2],
        )
    except (OSError, TypeError, ValueError):
        validation = make_validation_failure(
            "publication_write_failed" if known_track_slug else "export_configuration_invalid",
            input_count=input_count,
            pack_id=pack_identity[0],
            semantic_digest=pack_identity[1],
            input_snapshot_digest=pack_identity[2],
        )
    except Exception:
        validation = make_validation_failure(
            "export_internal_error",
            input_count=input_count,
            pack_id=pack_identity[0],
            semantic_digest=pack_identity[1],
            input_snapshot_digest=pack_identity[2],
        )

    failed_report = _try_write_failed_report(
        output_dir=output_dir,
        track_slug_value=known_track_slug,
        validation=validation,
    )
    return ExportResult(
        status="failed",
        pack=None,
        annotations_json=None,
        detached_package=None,
        validation=validation,
        validation_report=failed_report,
        current_pointer=None,
        revision_id=None,
    )


def _load_run_stage(output_dir: Path) -> str:
    snapshot = _read_json_snapshot(
        existing_run_state_file(output_dir),
        maximum_bytes=MAX_RUN_STATE_BYTES,
        unavailable_code="run_state_not_exportable",
        invalid_code="run_state_not_exportable",
        limit_code="run_state_not_exportable",
        mutation_code="run_state_not_exportable",
        maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
        maximum_nodes=MAX_AUXILIARY_JSON_NODES,
    )
    stage = snapshot.value.get("stage")
    if type(stage) is not str or stage not in _RUN_STAGES:
        raise _ExportFailure("run_state_not_exportable")
    return stage


def _require_exportable_run_state(
    stage: str,
    *,
    input_count: int,
    policy: ExportPolicy,
) -> None:
    empty = input_count == 0
    if stage == "completed":
        return
    if stage in {"paused", "error"}:
        if not policy.allow_partial:
            raise _ExportFailure("run_state_not_exportable")
        return
    if stage == "ready":
        if not empty or not policy.allow_empty:
            raise _ExportFailure("run_state_not_exportable")
        return
    raise _ExportFailure("run_state_not_exportable")


def _resolve_records(
    *,
    producer_snapshot: ProducerDraftResult,
    publication: PublicationIdentityResult,
    allow_skips: bool,
) -> tuple[tuple[ResolvedAnnotationDraft, ...], tuple[ValidationFinding, ...]]:
    findings: list[ValidationFinding] = [
        _policy_finding(finding, allow_skips=allow_skips)
        for finding in producer_snapshot.findings
    ]
    resolved: list[ResolvedAnnotationDraft] = []
    anchor_builder = AnchorBuilder()
    for draft in producer_snapshot.drafts:
        try:
            record = anchor_builder.resolve(draft=draft, publication=publication)
        except AnchorResolutionError as exc:
            findings.append(_policy_finding(exc.finding, allow_skips=allow_skips))
            continue
        resolved.append(record)
        findings.extend(record.target.findings)
    resolved.sort(key=lambda item: (item.source_record_index, item.source_record_digest))
    return tuple(resolved), tuple(findings)


def _policy_finding(
    finding: ValidationFinding,
    *,
    allow_skips: bool,
) -> ValidationFinding:
    severity: Literal["error", "skipped"] = "skipped" if allow_skips else "error"
    return make_validation_finding(
        finding.code,
        severity,
        source_record_index=finding.source_record_index,
        json_pointer=finding.json_pointer,
        annotation_id=finding.annotation_id,
        source_record_digest=finding.source_record_digest,
    )


def _identity_findings(
    publication: PublicationIdentityResult,
) -> tuple[ValidationFinding, ...]:
    converted: list[ValidationFinding] = []
    for finding in publication.findings:
        if finding.code not in ERROR_CATALOG:
            raise _ExportFailure("publication_identity_missing")
        try:
            converted.append(
                make_validation_finding(
                    finding.code,
                    "warning",
                    json_pointer=finding.json_pointer,
                )
            )
        except ValueError:
            raise _ExportFailure("publication_identity_missing") from None
    return tuple(converted)


def _track_identifier(
    *,
    publication: PublicationIdentityResult,
    creator: CreatorInput,
    track_key: str,
) -> str:
    edition = publication.wire.get("sr:edition")
    if not isinstance(edition, Mapping) or type(edition.get("id")) is not str:
        raise _ExportFailure("publication_identity_missing")
    try:
        return derive_track_id(str(edition["id"]), creator.id, track_key)
    except (TypeError, ValueError):
        raise _ExportFailure("export_configuration_invalid") from None


def _load_current_publication(
    *,
    output_dir: Path,
    track_slug_value: str,
    expected_track_id: str,
) -> _CurrentPublication | None:
    track_root = annotation_pack_track_dir(output_dir, track_slug_value)
    revisions_root = annotation_pack_revisions_dir(output_dir, track_slug_value)
    pointer_path = annotation_pack_current_pointer_file(output_dir, track_slug_value)
    track_descriptor = -1
    revisions_descriptor = -1
    revision_descriptor = -1
    try:
        try:
            track_descriptor = _open_directory_nofollow(
                track_root,
                failure_code="publication_pointer_invalid",
            )
        except _ExportFailure:
            try:
                os.lstat(track_root)
            except FileNotFoundError:
                return None
            except OSError:
                pass
            raise
        try:
            os.stat(
                pointer_path.name,
                dir_fd=track_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            os.close(track_descriptor)
            return None

        pointer_snapshot = _read_json_snapshot_at(
            track_descriptor,
            pointer_path.name,
            maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
            unavailable_code="publication_pointer_invalid",
            invalid_code="publication_pointer_invalid",
            limit_code="publication_pointer_invalid",
            mutation_code="publication_pointer_invalid",
            maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
            maximum_nodes=MAX_AUXILIARY_JSON_NODES,
        )
        if canonical_json_bytes(pointer_snapshot.value) != pointer_snapshot.content:
            raise _ExportFailure("publication_pointer_invalid")
        if tuple(
            auxiliary_validator(PUBLICATION_POINTER_SCHEMA_ID).iter_errors(
                pointer_snapshot.value
            )
        ):
            raise _ExportFailure("publication_pointer_invalid")

        pointer = pointer_snapshot.value
        if pointer.get("track_id") != expected_track_id:
            raise _ExportFailure("publication_pointer_invalid")
        revision = pointer.get("revision_id")
        if type(revision) is not str or _SHA256.fullmatch(revision) is None:
            raise _ExportFailure("publication_pointer_invalid")
        expected_annotations_relative = f"revisions/{revision}/annotations.json"
        expected_report_relative = f"revisions/{revision}/validation-report.json"
        if (
            pointer.get("annotations_json") != expected_annotations_relative
            or pointer.get("validation_report") != expected_report_relative
        ):
            raise _ExportFailure("publication_pointer_invalid")
        has_package = "detached_package" in pointer
        if has_package:
            expected_package_relative = (
                f"revisions/{revision}/{track_slug_value}.annotations"
            )
            if pointer.get("detached_package") != expected_package_relative:
                raise _ExportFailure("publication_pointer_invalid")
        elif "detached_package_sha256" in pointer:
            raise _ExportFailure("publication_pointer_invalid")

        revisions_descriptor = _open_child_directory(
            track_descriptor,
            revisions_root.name,
        )
        revision_descriptor = _open_child_directory(
            revisions_descriptor,
            revision,
        )
        expected_files = frozenset(
            {
                "annotations.json",
                "validation-report.json",
                *({f"{track_slug_value}.annotations"} if has_package else set()),
            }
        )
        if frozenset(os.listdir(revision_descriptor)) != expected_files:
            raise _ExportFailure("publication_pointer_invalid")

        revision_dir = annotation_pack_revision_dir(
            output_dir,
            track_slug_value,
            revision,
        )
        annotations_path = annotation_pack_annotations_file(
            output_dir,
            track_slug_value,
            revision,
        )
        report_path = annotation_pack_validation_report_file(
            output_dir,
            track_slug_value,
            revision,
        )
        annotations_snapshot = _read_json_snapshot_at(
            revision_descriptor,
            annotations_path.name,
            maximum_bytes=MAX_ANNOTATIONS_JSON_BYTES,
            unavailable_code="publication_pointer_invalid",
            invalid_code="publication_pointer_invalid",
            limit_code="publication_pointer_invalid",
            mutation_code="publication_pointer_invalid",
            maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
            maximum_nodes=MAX_AUXILIARY_JSON_NODES,
        )
        if canonical_json_bytes(annotations_snapshot.value) != annotations_snapshot.content:
            raise _ExportFailure("publication_pointer_invalid")
        if pointer.get("annotations_json_sha256") != annotations_snapshot.sha256:
            raise _ExportFailure("publication_pointer_invalid")

        package_path: Path | None = None
        package_snapshot: _BinarySnapshot | None = None
        if has_package:
            package_path = annotation_pack_detached_file(
                output_dir,
                track_slug_value,
                revision,
            )
            try:
                package_content, package_sha256, package_file = _read_regular_bytes_at(
                    revision_descriptor,
                    package_path.name,
                    maximum_bytes=MAX_DETACHED_PACKAGE_BYTES,
                )
            except OSError:
                raise _ExportFailure("publication_pointer_invalid") from None
            if pointer.get("detached_package_sha256") != package_sha256:
                raise _ExportFailure("publication_pointer_invalid")
            try:
                validated_package = validate_detached_annotations(
                    package_content,
                    expected_annotations_json=annotations_snapshot.content,
                )
            except PackageError:
                raise _ExportFailure("package_entry_invalid") from None
            if (
                validated_package.package_sha256 != package_sha256
                or validated_package.annotations_json_sha256
                != annotations_snapshot.sha256
            ):
                raise _ExportFailure("package_entry_invalid")
            package_snapshot = _BinarySnapshot(
                content=package_content,
                sha256=package_sha256,
                file=package_file,
            )

        report_snapshot = _read_json_snapshot_at(
            revision_descriptor,
            report_path.name,
            maximum_bytes=MAX_VALIDATION_REPORT_BYTES,
            unavailable_code="validation_report_invalid",
            invalid_code="validation_report_invalid",
            limit_code="validation_report_invalid",
            mutation_code="validation_report_invalid",
            maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
            maximum_nodes=MAX_AUXILIARY_JSON_NODES,
        )
        if pointer.get("validation_report_sha256") != report_snapshot.sha256:
            raise _ExportFailure("publication_pointer_invalid")
        report = _validated_report(report_snapshot.value, report_snapshot.content)
        if (
            report.annotations_json_sha256 != annotations_snapshot.sha256
            or report.package_sha256
            != (package_snapshot.sha256 if package_snapshot is not None else None)
        ):
            raise _ExportFailure("validation_report_invalid")

        recomputed_revision = publication_revision_id(
            annotations_json_sha256=annotations_snapshot.sha256,
            package_sha256=(
                package_snapshot.sha256 if package_snapshot is not None else None
            ),
            validation_report_sha256=report_snapshot.sha256,
        )
        if recomputed_revision != revision:
            raise _ExportFailure("publication_pointer_invalid")

        report_context = ValidationContext(
            input_count=report.input_count,
            findings=_upstream_report_findings(report.findings),
            allow_empty=report.exported_count == 0
            and any(
                finding.code == "empty_track" and finding.severity == "warning"
                for finding in report.findings
            ),
        )
        current_validation = validate_pack(
            annotations_snapshot.value,
            context=report_context,
        )
        expected_report = finalize_validation_report(
            current_validation,
            annotations_json_sha256=annotations_snapshot.sha256,
            package_sha256=(
                package_snapshot.sha256 if package_snapshot is not None else None
            ),
        )
        if serialize_validation_report(expected_report) != report_snapshot.content:
            raise _ExportFailure("validation_report_invalid")
        semantic = _nested_string(
            annotations_snapshot.value,
            "sr:semanticDigest",
            "sr:value",
        )
        track_identifier = _nested_string(
            annotations_snapshot.value,
            "sr:track",
            "id",
        )
        if (
            pointer.get("semantic_digest") != semantic
            or report.semantic_digest != semantic
            or track_identifier != expected_track_id
            or report.pack_id != annotations_snapshot.value.get("id")
        ):
            raise _ExportFailure("publication_pointer_invalid")
        current = _CurrentPublication(
            pointer_path=pointer_path,
            track_root=track_root,
            revisions_root=revisions_root,
            revision_dir=revision_dir,
            annotations_path=annotations_path,
            package_path=package_path,
            report_path=report_path,
            revision_id=revision,
            document=annotations_snapshot.value,
            validation=current_validation,
            report=report,
            pointer_snapshot=pointer_snapshot,
            annotations_snapshot=annotations_snapshot,
            package_snapshot=package_snapshot,
            report_snapshot=report_snapshot,
            expected_files=expected_files,
            track_descriptor=track_descriptor,
            revisions_descriptor=revisions_descriptor,
            revision_descriptor=revision_descriptor,
        )
        _assert_current_publication_unchanged(current)
        return current
    except _ExportFailure:
        for descriptor in (
            revision_descriptor,
            revisions_descriptor,
            track_descriptor,
        ):
            if descriptor >= 0:
                with suppress(OSError):
                    os.close(descriptor)
        raise
    except (OSError, TypeError, ValueError):
        for descriptor in (
            revision_descriptor,
            revisions_descriptor,
            track_descriptor,
        ):
            if descriptor >= 0:
                with suppress(OSError):
                    os.close(descriptor)
        raise _ExportFailure("publication_pointer_invalid") from None


def _assert_current_publication_unchanged(current: _CurrentPublication) -> None:
    """Reassert every byte and path selected by one current pointer snapshot."""

    _assert_file_unchanged_at(
        current.revision_descriptor,
        current.annotations_path.name,
        expected_digest=current.annotations_snapshot.sha256,
        expected_snapshot=current.annotations_snapshot.file,
        maximum_bytes=MAX_ANNOTATIONS_JSON_BYTES,
        unavailable_code="publication_pointer_invalid",
    )
    _assert_file_unchanged_at(
        current.revision_descriptor,
        current.report_path.name,
        expected_digest=current.report_snapshot.sha256,
        expected_snapshot=current.report_snapshot.file,
        maximum_bytes=MAX_VALIDATION_REPORT_BYTES,
        unavailable_code="validation_report_invalid",
    )
    expected_revision_files = {
        current.annotations_path.name: current.annotations_snapshot.content,
        current.report_path.name: current.report_snapshot.content,
    }
    if current.package_path is not None and current.package_snapshot is not None:
        _assert_file_unchanged_at(
            current.revision_descriptor,
            current.package_path.name,
            expected_digest=current.package_snapshot.sha256,
            expected_snapshot=current.package_snapshot.file,
            maximum_bytes=MAX_DETACHED_PACKAGE_BYTES,
            unavailable_code="package_entry_invalid",
        )
        expected_revision_files[current.package_path.name] = (
            current.package_snapshot.content
        )
    elif current.package_path is not None or current.package_snapshot is not None:
        raise _ExportFailure("publication_pointer_invalid")
    try:
        names = frozenset(os.listdir(current.revision_descriptor))
    except OSError:
        raise _ExportFailure("publication_pointer_invalid") from None
    if (
        names != current.expected_files
        or not _revision_is_frozen_at(
            current.revision_descriptor,
            expected_revision_files,
        )
        or not _named_directory_matches(
            current.track_descriptor,
            current.revisions_root.name,
            current.revisions_descriptor,
        )
        or not _named_directory_matches(
            current.revisions_descriptor,
            current.revision_id,
            current.revision_descriptor,
        )
        or not _directory_path_matches(
            current.track_root,
            current.track_descriptor,
        )
    ):
        raise _ExportFailure("publication_pointer_invalid")
    # Pointer last: immediately after this succeeds it still selects the exact
    # complete immutable revision that was just reasserted.
    _assert_file_unchanged_at(
        current.track_descriptor,
        current.pointer_path.name,
        expected_digest=current.pointer_snapshot.sha256,
        expected_snapshot=current.pointer_snapshot.file,
        maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
        unavailable_code="publication_pointer_invalid",
    )


def _close_current_publication(current: _CurrentPublication) -> None:
    for descriptor in (
        current.revision_descriptor,
        current.revisions_descriptor,
        current.track_descriptor,
    ):
        with suppress(OSError):
            os.close(descriptor)


def _validated_report(
    document: Mapping[str, Any],
    content: bytes,
) -> ValidationReport:
    if canonical_json_bytes(document) != content:
        raise _ExportFailure("validation_report_invalid")
    if tuple(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(document)):
        raise _ExportFailure("validation_report_invalid")
    if (
        document.get("schema_version") != VALIDATION_REPORT_SCHEMA_VERSION
        or document.get("validator_version") != VALIDATOR_VERSION
        or document.get("status") not in {"valid", "degraded"}
    ):
        raise _ExportFailure("validation_report_invalid")
    counts = document.get("counts")
    raw_findings = document.get("findings")
    if not isinstance(counts, Mapping) or not isinstance(raw_findings, list):
        raise _ExportFailure("validation_report_invalid")
    findings: list[ValidationFinding] = []
    try:
        for raw in raw_findings:
            if not isinstance(raw, Mapping):
                raise ValueError
            finding = make_validation_finding(
                cast(str, raw.get("code")),
                cast(Any, raw.get("severity")),
                source_record_index=cast(int | None, raw.get("source_record_index")),
                source_record_digest=cast(str | None, raw.get("source_record_digest")),
                json_pointer=cast(str | None, raw.get("json_pointer")),
                annotation_id=cast(str | None, raw.get("annotation_id")),
            )
            if raw.get("message") != finding.message:
                raise ValueError
            findings.append(finding)
        report = ValidationReport(
            schema_version=cast(str, document["schema_version"]),
            validator_version=cast(str, document["validator_version"]),
            status=cast(Any, document["status"]),
            pack_id=cast(str | None, document.get("pack_id")),
            semantic_digest=cast(str | None, document.get("semantic_digest")),
            input_snapshot_digest=cast(
                str | None, document.get("input_snapshot_digest")
            ),
            annotations_json_sha256=cast(
                str | None, document.get("annotations_json_sha256")
            ),
            package_sha256=cast(str | None, document.get("package_sha256")),
            input_count=cast(int, counts["input"]),
            exported_count=cast(int, counts["exported"]),
            skipped_count=cast(int, counts["skipped"]),
            warning_count=cast(int, counts["warnings"]),
            error_count=cast(int, counts["errors"]),
            findings=tuple(findings),
        )
        if serialize_validation_report(report) != content:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise _ExportFailure("validation_report_invalid") from None
    return report


def _upstream_report_findings(
    findings: tuple[ValidationFinding, ...],
) -> tuple[ValidationFinding, ...]:
    """Recover only producer/source findings from a published report.

    Intrinsic validator findings (for example ``empty_track`` and
    ``body_looks_like_source_copy``) are recomputed from the Pack.  Reinjecting
    them would make the report context a second source of semantic truth.
    """

    upstream_warning_codes = {
        "cfi_unverified",
        "quote_not_unique_in_resource",
        "duplicate_resource_chapter_projection",
        "invalid_persisted_metadata_fallback",
        "invalid_publication_metadata",
        "publication_metadata_mismatch",
        "invalid_publication_language",
    }
    return tuple(
        finding
        for finding in findings
        if finding.severity == "skipped" or finding.code in upstream_warning_codes
    )


def _publish_json_revision(
    *,
    output_dir: Path,
    track_slug_value: str,
    track_identifier: str,
    revision_id: str,
    semantic_digest: str,
    annotations_bytes: bytes,
    annotations_sha256: str,
    package_bytes: bytes | None,
    package_sha256: str | None,
    report_bytes: bytes,
    report_sha256: str,
    assert_reversible_boundary: Callable[[], None],
) -> tuple[Path, Path | None, Path, Path]:
    if (package_bytes is None) != (package_sha256 is None):
        raise _ExportFailure("package_entry_invalid")
    if package_bytes is not None and (
        len(package_bytes) > MAX_DETACHED_PACKAGE_BYTES
        or hashlib.sha256(package_bytes).hexdigest() != package_sha256
    ):
        raise _ExportFailure("package_entry_invalid")
    package_name = (
        f"{track_slug_value}.annotations" if package_bytes is not None else None
    )
    track_root = annotation_pack_track_dir(output_dir, track_slug_value)
    revisions_root = annotation_pack_revisions_dir(output_dir, track_slug_value)
    expected_files = {
        "annotations.json": annotations_bytes,
        "validation-report.json": report_bytes,
    }
    if package_name is not None and package_bytes is not None:
        expected_files[package_name] = package_bytes
    _ensure_directory_chain(output_dir, revisions_root)
    track_descriptor = _open_directory_nofollow(
        track_root,
        failure_code="publication_write_failed",
    )
    revisions_descriptor = -1
    temp_descriptor = -1
    final_descriptor = -1
    selected_descriptor = -1
    temp_name = f".tmp-{uuid4().hex}"
    temp_exists = False
    try:
        revisions_descriptor = _open_child_directory(
            track_descriptor,
            revisions_root.name,
        )
        os.mkdir(temp_name, 0o755, dir_fd=revisions_descriptor)
        temp_exists = True
        temp_descriptor = _open_child_directory(revisions_descriptor, temp_name)
        _write_exclusive_file_at(
            temp_descriptor,
            "annotations.json",
            annotations_bytes,
        )
        _write_exclusive_file_at(
            temp_descriptor,
            "validation-report.json",
            report_bytes,
        )
        if package_name is not None and package_bytes is not None:
            _write_exclusive_file_at(
                temp_descriptor,
                package_name,
                package_bytes,
            )
        os.fsync(temp_descriptor)

        try:
            final_descriptor = _open_child_directory(
                revisions_descriptor,
                revision_id,
            )
        except FileNotFoundError:
            destination_exists = False
        except OSError:
            raise _ExportFailure("publication_write_failed") from None
        else:
            destination_exists = True

        if destination_exists:
            if (
                not _revision_matches_at(final_descriptor, expected_files)
                or not _revision_is_frozen_at(final_descriptor, expected_files)
            ):
                raise _ExportFailure("publication_write_failed")
            _remove_owned_temp_revision_at(
                revisions_descriptor,
                temp_name,
                temp_descriptor,
                allowed_names=frozenset(expected_files),
            )
            temp_exists = False
            os.close(temp_descriptor)
            temp_descriptor = -1
        else:
            _freeze_revision_at(temp_descriptor, expected_files)
            try:
                _rename_directory_noreplace_at(
                    revisions_descriptor,
                    temp_name,
                    revision_id,
                )
            except FileExistsError:
                final_descriptor = _open_child_directory(
                    revisions_descriptor,
                    revision_id,
                )
                if (
                    not _revision_matches_at(final_descriptor, expected_files)
                    or not _revision_is_frozen_at(final_descriptor, expected_files)
                ):
                    raise _ExportFailure("publication_write_failed") from None
                _thaw_owned_temp_revision_at(temp_descriptor)
                _remove_owned_temp_revision_at(
                    revisions_descriptor,
                    temp_name,
                    temp_descriptor,
                    allowed_names=frozenset(expected_files),
                )
                temp_exists = False
                os.close(temp_descriptor)
                temp_descriptor = -1
            else:
                temp_exists = False
                final_descriptor = temp_descriptor
                temp_descriptor = -1

        os.fsync(revisions_descriptor)
        _fsync_directory(revisions_root)
        # The final immutable name is the source of truth for the pointer, not
        # the temp directory we wrote.  Re-open it after rename/reuse and the
        # revisions-root durability barrier so a corrupt or externally changed
        # destination is never selected by current.json.
        selected_descriptor = _open_child_directory(
            revisions_descriptor,
            revision_id,
        )
        if (
            not _same_directory(final_descriptor, selected_descriptor)
            or not _revision_matches_at(selected_descriptor, expected_files)
            or not _revision_is_frozen_at(selected_descriptor, expected_files)
            or not _directory_path_matches(track_root, track_descriptor)
            or not _directory_path_matches(revisions_root, revisions_descriptor)
        ):
            raise _ExportFailure("publication_write_failed")

        pointer = {
            "schema_version": PUBLICATION_POINTER_SCHEMA_VERSION,
            "track_id": track_identifier,
            "revision_id": revision_id,
            "semantic_digest": semantic_digest,
            "annotations_json": f"revisions/{revision_id}/annotations.json",
            "annotations_json_sha256": annotations_sha256,
            "validation_report": f"revisions/{revision_id}/validation-report.json",
            "validation_report_sha256": report_sha256,
        }
        if package_name is not None and package_sha256 is not None:
            pointer["detached_package"] = (
                f"revisions/{revision_id}/{package_name}"
            )
            pointer["detached_package_sha256"] = package_sha256
        if tuple(auxiliary_validator(PUBLICATION_POINTER_SCHEMA_ID).iter_errors(pointer)):
            raise _ExportFailure("publication_write_failed")
        pointer_bytes = canonical_json_bytes(pointer)
        if len(pointer_bytes) > MAX_PUBLICATION_POINTER_BYTES:
            raise _ExportFailure("publication_write_failed")
        pointer_path = annotation_pack_current_pointer_file(
            output_dir, track_slug_value
        )
        prior_pointer = _capture_prior_pointer_at(
            track_descriptor,
            pointer_path.name,
        )
        assert_reversible_boundary()
        candidate_identity = _atomic_replace_file_at(
            track_descriptor,
            pointer_path.name,
            pointer_bytes,
        )
        _fsync_directory(track_root)
        revision_invalid_after_switch = (
            not _directory_path_matches(track_root, track_descriptor)
            or not _directory_path_matches(
                revisions_root,
                revisions_descriptor,
            )
            or not _named_directory_matches(
                revisions_descriptor,
                revision_id,
                selected_descriptor,
            )
            or not _revision_matches_at(selected_descriptor, expected_files)
            or not _revision_is_frozen_at(
                selected_descriptor,
                expected_files,
            )
            or not _regular_file_matches_at(
                track_descriptor,
                pointer_path.name,
                expected_content=pointer_bytes,
                expected_identity=candidate_identity,
                maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
            )
        )
        if revision_invalid_after_switch:
            _rollback_pointer_if_candidate(
                track_descriptor,
                pointer_path.name,
                candidate_content=pointer_bytes,
                candidate_identity=candidate_identity,
                prior=prior_pointer,
            )
            raise _ExportFailure("publication_write_failed")
        return (
            annotation_pack_annotations_file(
                output_dir, track_slug_value, revision_id
            ),
            (
                annotation_pack_detached_file(
                    output_dir,
                    track_slug_value,
                    revision_id,
                )
                if package_name is not None
                else None
            ),
            annotation_pack_validation_report_file(
                output_dir, track_slug_value, revision_id
            ),
            pointer_path,
        )
    except _ExportFailure:
        raise
    except OSError:
        raise _ExportFailure("publication_write_failed") from None
    finally:
        if temp_exists and revisions_descriptor >= 0:
            with suppress(OSError):
                if temp_descriptor >= 0:
                    _thaw_owned_temp_revision_at(temp_descriptor)
                _remove_owned_temp_revision_at(
                    revisions_descriptor,
                    temp_name,
                    temp_descriptor if temp_descriptor >= 0 else None,
                    allowed_names=frozenset(expected_files),
                )
        for descriptor in (
            selected_descriptor,
            final_descriptor,
            temp_descriptor,
            revisions_descriptor,
            track_descriptor,
        ):
            if descriptor >= 0:
                with suppress(OSError):
                    os.close(descriptor)


def _revision_matches_at(
    directory_descriptor: int,
    expected: Mapping[str, bytes],
) -> bool:
    try:
        status = os.fstat(directory_descriptor)
        if not stat.S_ISDIR(status.st_mode):
            return False
        if set(os.listdir(directory_descriptor)) != set(expected):
            return False
        for name, content in expected.items():
            payload, digest, _snapshot = _read_regular_bytes_at(
                directory_descriptor,
                name,
                maximum_bytes=max(len(content), 1),
            )
            if digest != hashlib.sha256(content).hexdigest() or payload != content:
                return False
    except OSError:
        return False
    return True


def _freeze_revision_at(
    directory_descriptor: int,
    expected: Mapping[str, bytes],
) -> None:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise _ExportFailure("publication_write_failed")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow
    try:
        for name in expected:
            descriptor = os.open(name, flags, dir_fd=directory_descriptor)
            try:
                status = os.fstat(descriptor)
                if not stat.S_ISREG(status.st_mode):
                    raise OSError("revision entry is not regular")
                os.fchmod(descriptor, 0o444)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        os.fchmod(directory_descriptor, 0o555)
        os.fsync(directory_descriptor)
    except OSError:
        raise _ExportFailure("publication_write_failed") from None


def _thaw_owned_temp_revision_at(directory_descriptor: int) -> None:
    os.fchmod(directory_descriptor, 0o755)
    os.fsync(directory_descriptor)


def _revision_is_frozen_at(
    directory_descriptor: int,
    expected: Mapping[str, bytes],
) -> bool:
    try:
        directory_status = os.fstat(directory_descriptor)
        if (
            not stat.S_ISDIR(directory_status.st_mode)
            or directory_status.st_mode & 0o222
        ):
            return False
        for name in expected:
            status = os.stat(
                name,
                dir_fd=directory_descriptor,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(status.st_mode) or status.st_mode & 0o222:
                return False
    except OSError:
        return False
    return True


def _try_write_failed_report(
    *,
    output_dir: Path,
    track_slug_value: str | None,
    validation: ValidationResult,
) -> Path | None:
    if track_slug_value is None:
        return None
    try:
        report = finalize_validation_report(
            validation,
            annotations_json_sha256=None,
            package_sha256=None,
        )
        content = serialize_validation_report(report)
        if len(content) > MAX_VALIDATION_REPORT_BYTES:
            return None
        track_root = annotation_pack_track_dir(output_dir, track_slug_value)
        _ensure_directory_chain(output_dir, track_root)
        destination = annotation_pack_last_failed_report_file(
            output_dir, track_slug_value
        )
        track_descriptor = _open_directory_nofollow(
            track_root,
            failure_code="publication_write_failed",
        )
        try:
            _atomic_replace_file_at(track_descriptor, destination.name, content)
            _fsync_directory(track_root)
            if not _directory_path_matches(track_root, track_descriptor):
                return None
        finally:
            os.close(track_descriptor)
        return destination
    except Exception:
        return None


def _atomic_replace_file_at(
    directory_descriptor: int,
    destination_name: str,
    content: bytes,
) -> _FileIdentity:
    if not _safe_publication_leaf(destination_name):
        raise _ExportFailure("publication_write_failed")
    temporary_name = f".{destination_name}.tmp-{uuid4().hex}"
    try:
        identity = _write_exclusive_file_at(
            directory_descriptor,
            temporary_name,
            content,
        )
        os.replace(
            temporary_name,
            destination_name,
            src_dir_fd=directory_descriptor,
            dst_dir_fd=directory_descriptor,
        )
        os.fsync(directory_descriptor)
        return identity
    except OSError:
        with suppress(OSError):
            os.unlink(temporary_name, dir_fd=directory_descriptor)
        raise _ExportFailure("publication_write_failed") from None


def _capture_prior_pointer_at(
    directory_descriptor: int,
    name: str,
) -> _PriorPointer:
    try:
        os.stat(
            name,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return _PriorPointer(content=None, sha256=None, file=None)
    except OSError:
        raise _ExportFailure("publication_write_failed") from None
    snapshot = _read_json_snapshot_at(
        directory_descriptor,
        name,
        maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
        unavailable_code="publication_write_failed",
        invalid_code="publication_write_failed",
        limit_code="publication_write_failed",
        mutation_code="publication_write_failed",
        maximum_depth=MAX_AUXILIARY_JSON_DEPTH,
        maximum_nodes=MAX_AUXILIARY_JSON_NODES,
    )
    if (
        canonical_json_bytes(snapshot.value) != snapshot.content
        or tuple(
            auxiliary_validator(PUBLICATION_POINTER_SCHEMA_ID).iter_errors(
                snapshot.value
            )
        )
    ):
        raise _ExportFailure("publication_write_failed")
    return _PriorPointer(
        content=snapshot.content,
        sha256=snapshot.sha256,
        file=snapshot.file,
    )


def _rollback_pointer_if_candidate(
    directory_descriptor: int,
    name: str,
    *,
    candidate_content: bytes,
    candidate_identity: _FileIdentity,
    prior: _PriorPointer,
) -> bool:
    candidate_digest = hashlib.sha256(candidate_content).hexdigest()

    def candidate_is_current() -> bool:
        try:
            content, digest, snapshot = _read_regular_bytes_at(
                directory_descriptor,
                name,
                maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
            )
        except OSError:
            return False
        return (
            content == candidate_content
            and digest == candidate_digest
            and _FileIdentity(
                device=snapshot.device,
                inode=snapshot.inode,
            )
            == candidate_identity
        )

    if not candidate_is_current():
        return False
    if prior.content is None:
        try:
            if not candidate_is_current():
                return False
            os.unlink(name, dir_fd=directory_descriptor)
            os.fsync(directory_descriptor)
        except OSError:
            return False
        return True

    temporary_name = f".{name}.rollback-{uuid4().hex}"
    try:
        _write_exclusive_file_at(
            directory_descriptor,
            temporary_name,
            prior.content,
        )
        if not candidate_is_current():
            return False
        os.replace(
            temporary_name,
            name,
            src_dir_fd=directory_descriptor,
            dst_dir_fd=directory_descriptor,
        )
        os.fsync(directory_descriptor)
        restored, digest, _snapshot = _read_regular_bytes_at(
            directory_descriptor,
            name,
            maximum_bytes=MAX_PUBLICATION_POINTER_BYTES,
        )
        return restored == prior.content and digest == prior.sha256
    except OSError:
        return False
    finally:
        with suppress(OSError):
            os.unlink(temporary_name, dir_fd=directory_descriptor)


def _regular_file_matches_at(
    directory_descriptor: int,
    name: str,
    *,
    expected_content: bytes,
    expected_identity: _FileIdentity,
    maximum_bytes: int,
) -> bool:
    try:
        content, digest, snapshot = _read_regular_bytes_at(
            directory_descriptor,
            name,
            maximum_bytes=maximum_bytes,
        )
    except OSError:
        return False
    return (
        content == expected_content
        and digest == hashlib.sha256(expected_content).hexdigest()
        and _FileIdentity(device=snapshot.device, inode=snapshot.inode)
        == expected_identity
    )


def _write_exclusive_file_at(
    directory_descriptor: int,
    name: str,
    content: bytes,
) -> _FileIdentity:
    if not _safe_publication_leaf(name):
        raise _ExportFailure("publication_write_failed")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise _ExportFailure("publication_write_failed")
    descriptor = os.open(
        name,
        flags | nofollow,
        0o644,
        dir_fd=directory_descriptor,
    )
    try:
        view = memoryview(content)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OSError("short publication write")
            written += count
        os.fsync(descriptor)
        return _FileIdentity.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)


def _ensure_directory_chain(root: Path, destination: Path) -> None:
    descriptor = _open_or_create_directory_chain(root, destination)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _open_or_create_directory_chain(root: Path, destination: Path) -> int:
    try:
        root_value = Path(os.path.abspath(os.fspath(root)))
        destination_value = Path(os.path.abspath(os.fspath(destination)))
        relative = destination_value.relative_to(root_value)
    except (OSError, TypeError, ValueError):
        raise _ExportFailure("publication_write_failed") from None
    descriptor = _open_directory_nofollow(
        root_value,
        failure_code="publication_write_failed",
    )
    try:
        for component in relative.parts:
            if not _safe_publication_leaf(component):
                raise _ExportFailure("publication_write_failed")
            created = False
            try:
                os.mkdir(component, 0o755, dir_fd=descriptor)
                created = True
            except FileExistsError:
                pass
            child = _open_child_directory(descriptor, component)
            if created:
                os.fsync(child)
                os.fsync(descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _remove_owned_temp_revision_at(
    revisions_descriptor: int,
    name: str,
    descriptor: int | None = None,
    *,
    allowed_names: frozenset[str],
) -> None:
    if not name.startswith(".tmp-") or not _safe_publication_leaf(name):
        raise OSError("refusing to remove an unowned revision")
    owned_descriptor = descriptor
    close_owned = False
    if owned_descriptor is None:
        owned_descriptor = _open_child_directory(revisions_descriptor, name)
        close_owned = True
    try:
        entries = set(os.listdir(owned_descriptor))
        if not entries <= allowed_names:
            raise OSError("temporary revision contains an unowned entry")
        for entry in entries:
            os.unlink(entry, dir_fd=owned_descriptor)
    finally:
        if close_owned:
            os.close(owned_descriptor)
    os.rmdir(name, dir_fd=revisions_descriptor)


def _rename_directory_noreplace_at(
    directory_descriptor: int,
    source_name: str,
    destination_name: str,
) -> None:
    """Atomically rename within one pinned directory without replacement."""

    if not _safe_publication_leaf(source_name) or not _safe_publication_leaf(
        destination_name
    ):
        raise _ExportFailure("publication_write_failed")
    library = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source_name)
    destination_bytes = os.fsencode(destination_name)
    result: int
    if sys.platform == "darwin":
        try:
            renameatx_np = library.renameatx_np
        except AttributeError:
            raise _ExportFailure("publication_write_failed") from None
        renameatx_np.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameatx_np.restype = ctypes.c_int
        result = int(
            renameatx_np(
                directory_descriptor,
                source_bytes,
                directory_descriptor,
                destination_bytes,
                0x00000004,
            )
        )
    elif sys.platform.startswith("linux"):
        try:
            renameat2 = library.renameat2
        except AttributeError:
            raise _ExportFailure("publication_write_failed") from None
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        result = int(
            renameat2(
                directory_descriptor,
                source_bytes,
                directory_descriptor,
                destination_bytes,
                1,
            )
        )
    else:
        raise _ExportFailure("publication_write_failed")
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
        raise FileExistsError(error_number, "publication revision already exists")
    raise OSError(error_number, "publication revision rename failed")


def _open_child_directory(parent_descriptor: int, name: str) -> int:
    if not _safe_publication_leaf(name):
        raise OSError("unsafe directory name")
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        raise OSError("safe directory open unavailable")
    return os.open(
        name,
        os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory,
        dir_fd=parent_descriptor,
    )


def _open_directory_nofollow(path: Path, *, failure_code: str) -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None or not isinstance(path, Path):
        raise _ExportFailure(failure_code)
    descriptor = -1
    try:
        components = tuple(
            component
            for component in os.path.abspath(os.fspath(path)).split(os.sep)
            if component
        )
        descriptor = os.open(
            os.sep,
            os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory,
        )
        for component in components:
            child = os.open(
                component,
                os.O_RDONLY
                | os.O_CLOEXEC
                | os.O_NONBLOCK
                | nofollow
                | directory,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except OSError:
        if descriptor >= 0:
            with suppress(OSError):
                os.close(descriptor)
        raise _ExportFailure(failure_code) from None


def _same_directory(left_descriptor: int, right_descriptor: int) -> bool:
    try:
        left = os.fstat(left_descriptor)
        right = os.fstat(right_descriptor)
    except OSError:
        return False
    return (
        stat.S_ISDIR(left.st_mode)
        and stat.S_ISDIR(right.st_mode)
        and (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)
    )


def _directory_path_matches(path: Path, descriptor: int) -> bool:
    try:
        reopened = _open_directory_nofollow(
            path,
            failure_code="publication_write_failed",
        )
    except _ExportFailure:
        return False
    try:
        return _same_directory(reopened, descriptor)
    finally:
        os.close(reopened)


def _named_directory_matches(
    parent_descriptor: int,
    name: str,
    expected_descriptor: int,
) -> bool:
    try:
        reopened = _open_child_directory(parent_descriptor, name)
    except OSError:
        return False
    try:
        return _same_directory(reopened, expected_descriptor)
    finally:
        os.close(reopened)


def _safe_publication_leaf(value: object) -> bool:
    return (
        type(value) is str
        and value not in {"", ".", ".."}
        and "/" not in value
        and "\\" not in value
        and not any(unicodedata.category(character) == "Cc" for character in value)
    )


def _read_regular_bytes_at(
    parent_descriptor: int,
    name: str,
    *,
    maximum_bytes: int,
) -> tuple[bytes, str, _FileSnapshot]:
    if not _safe_publication_leaf(name):
        raise OSError("unsafe file name")
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise OSError("safe file open unavailable")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow
    descriptor = os.open(name, flags, dir_fd=parent_descriptor)
    try:
        before = os.fstat(descriptor)
        before_path = os.stat(
            name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        snapshot = _FileSnapshot.from_stat(before)
        if (
            not stat.S_ISREG(before.st_mode)
            or _FileSnapshot.from_stat(before_path) != snapshot
            or before.st_size > maximum_bytes
        ):
            raise OSError("publication file is unsafe")
        chunks: list[bytes] = []
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(descriptor, FILE_HASH_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > maximum_bytes:
                raise OSError("publication file exceeds limit")
            chunks.append(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        after_path = os.stat(
            name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        reopened = os.open(name, flags, dir_fd=parent_descriptor)
        try:
            reopened_snapshot = _FileSnapshot.from_stat(os.fstat(reopened))
        finally:
            os.close(reopened)
        if (
            _FileSnapshot.from_stat(after) != snapshot
            or _FileSnapshot.from_stat(after_path) != snapshot
            or reopened_snapshot != snapshot
            or total != snapshot.byte_length
        ):
            raise OSError("publication file changed during read")
        return b"".join(chunks), digest.hexdigest(), snapshot
    finally:
        os.close(descriptor)


def _read_json_snapshot_at(
    parent_descriptor: int,
    name: str,
    *,
    maximum_bytes: int,
    unavailable_code: str,
    invalid_code: str,
    limit_code: str,
    mutation_code: str,
    maximum_depth: int,
    maximum_nodes: int,
) -> _JsonSnapshot:
    del mutation_code
    try:
        content, digest, snapshot = _read_regular_bytes_at(
            parent_descriptor,
            name,
            maximum_bytes=maximum_bytes,
        )
    except OSError:
        raise _ExportFailure(unavailable_code) from None
    if content.startswith(b"\xef\xbb\xbf"):
        raise _ExportFailure(invalid_code)
    try:
        text = content.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except RecursionError:
        raise _ExportFailure(limit_code) from None
    except (UnicodeDecodeError, ValueError):
        raise _ExportFailure(invalid_code) from None
    if not isinstance(value, dict):
        raise _ExportFailure(invalid_code)
    _enforce_json_shape_limits(
        value,
        maximum_depth=maximum_depth,
        maximum_nodes=maximum_nodes,
        limit_code=limit_code,
    )
    return _JsonSnapshot(
        value=value,
        content=content,
        sha256=digest,
        file=snapshot,
    )


def _assert_file_unchanged_at(
    parent_descriptor: int,
    name: str,
    *,
    expected_digest: str,
    expected_snapshot: _FileSnapshot,
    maximum_bytes: int,
    unavailable_code: str,
) -> None:
    try:
        _content, digest, snapshot = _read_regular_bytes_at(
            parent_descriptor,
            name,
            maximum_bytes=maximum_bytes,
        )
    except OSError:
        raise _ExportFailure(unavailable_code) from None
    if snapshot != expected_snapshot or digest != expected_digest:
        raise _ExportFailure(unavailable_code)


def _fsync_directory(path: Path) -> None:
    descriptor = _open_directory_nofollow(
        path,
        failure_code="publication_write_failed",
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_json_snapshot(
    path: Path,
    *,
    maximum_bytes: int,
    unavailable_code: str,
    invalid_code: str,
    limit_code: str,
    mutation_code: str,
    maximum_depth: int,
    maximum_nodes: int,
) -> _JsonSnapshot:
    content, digest, snapshot = _read_regular_bytes(
        path,
        maximum_bytes=maximum_bytes,
        unavailable_code=unavailable_code,
        limit_code=limit_code,
        mutation_code=mutation_code,
    )
    if content.startswith(b"\xef\xbb\xbf"):
        raise _ExportFailure(invalid_code)
    try:
        text = content.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except RecursionError:
        raise _ExportFailure(limit_code) from None
    except (UnicodeDecodeError, ValueError):
        raise _ExportFailure(invalid_code) from None
    if not isinstance(value, dict):
        raise _ExportFailure(invalid_code)
    _enforce_json_shape_limits(
        value,
        maximum_depth=maximum_depth,
        maximum_nodes=maximum_nodes,
        limit_code=limit_code,
    )
    return _JsonSnapshot(
        value=value,
        content=content,
        sha256=digest,
        file=snapshot,
    )


def _read_regular_bytes(
    path: Path,
    *,
    maximum_bytes: int,
    unavailable_code: str,
    limit_code: str,
    mutation_code: str,
) -> tuple[bytes, str, _FileSnapshot]:
    descriptor, parent_descriptor, leaf = _open_regular_nofollow(
        path, failure_code=unavailable_code
    )
    try:
        try:
            before = os.fstat(descriptor)
            before_path = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        except OSError:
            raise _ExportFailure(unavailable_code) from None
        before_snapshot = _FileSnapshot.from_stat(before)
        if not stat.S_ISREG(before.st_mode) or _FileSnapshot.from_stat(before_path) != before_snapshot:
            raise _ExportFailure(unavailable_code)
        if before.st_size > maximum_bytes:
            raise _ExportFailure(limit_code)
        chunks: list[bytes] = []
        digest = hashlib.sha256()
        total = 0
        while True:
            try:
                chunk = os.read(descriptor, FILE_HASH_CHUNK_BYTES)
            except InterruptedError:
                continue
            except OSError:
                raise _ExportFailure(unavailable_code) from None
            if not chunk:
                break
            total += len(chunk)
            if total > maximum_bytes:
                raise _ExportFailure(limit_code)
            chunks.append(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        after_path = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        reopened, reopened_parent, _ = _open_regular_nofollow(
            path, failure_code=mutation_code
        )
        try:
            reopened_snapshot = _FileSnapshot.from_stat(os.fstat(reopened))
        finally:
            os.close(reopened)
            os.close(reopened_parent)
        after_snapshot = _FileSnapshot.from_stat(after)
        if (
            before_snapshot != after_snapshot
            or after_snapshot != _FileSnapshot.from_stat(after_path)
            or after_snapshot != reopened_snapshot
            or total != after.st_size
        ):
            raise _ExportFailure(mutation_code)
        return b"".join(chunks), digest.hexdigest(), after_snapshot
    except _ExportFailure:
        raise
    except OSError:
        raise _ExportFailure(mutation_code) from None
    finally:
        os.close(descriptor)
        os.close(parent_descriptor)


def _assert_file_unchanged(
    path: Path,
    *,
    expected_digest: str,
    expected_snapshot: _FileSnapshot,
    maximum_bytes: int,
    unavailable_code: str,
) -> None:
    descriptor, parent_descriptor, leaf = _open_regular_nofollow(
        path, failure_code=unavailable_code
    )
    try:
        before = os.fstat(descriptor)
        before_snapshot = _FileSnapshot.from_stat(before)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum_bytes:
            raise _ExportFailure(unavailable_code)
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(descriptor, FILE_HASH_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > maximum_bytes:
                raise _ExportFailure(unavailable_code)
            digest.update(chunk)
        after = os.fstat(descriptor)
        path_stat = os.stat(leaf, dir_fd=parent_descriptor, follow_symlinks=False)
        reopened, reopened_parent, _ = _open_regular_nofollow(
            path, failure_code=unavailable_code
        )
        try:
            reopened_snapshot = _FileSnapshot.from_stat(os.fstat(reopened))
        finally:
            os.close(reopened)
            os.close(reopened_parent)
        if (
            before_snapshot != expected_snapshot
            or _FileSnapshot.from_stat(after) != expected_snapshot
            or _FileSnapshot.from_stat(path_stat) != expected_snapshot
            or reopened_snapshot != expected_snapshot
            or total != expected_snapshot.byte_length
            or digest.hexdigest() != expected_digest
        ):
            raise _ExportFailure(unavailable_code)
    except _ExportFailure:
        raise
    except OSError:
        raise _ExportFailure(unavailable_code) from None
    finally:
        os.close(descriptor)
        os.close(parent_descriptor)


def _open_regular_nofollow(
    path: Path,
    *,
    failure_code: str,
) -> tuple[int, int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None or not isinstance(path, Path):
        raise _ExportFailure(failure_code)
    try:
        absolute = os.path.abspath(os.fspath(path))
    except (OSError, TypeError, ValueError):
        raise _ExportFailure(failure_code) from None
    components = tuple(part for part in absolute.split(os.sep) if part)
    if not components:
        raise _ExportFailure(failure_code)
    directory_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory
    try:
        current = os.open(os.sep, directory_flags)
    except OSError:
        raise _ExportFailure(failure_code) from None
    try:
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
            except OSError:
                raise _ExportFailure(failure_code) from None
            os.close(current)
            current = child
        try:
            descriptor = os.open(
                components[-1],
                os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow,
                dir_fd=current,
            )
        except OSError:
            raise _ExportFailure(failure_code) from None
        return descriptor, current, components[-1]
    except BaseException:
        with suppress(OSError):
            os.close(current)
        raise


def _enforce_json_shape_limits(
    value: object,
    *,
    maximum_depth: int,
    maximum_nodes: int,
    limit_code: str,
) -> None:
    nodes = 0
    stack: list[tuple[object, int]] = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > maximum_nodes or depth > maximum_depth:
            raise _ExportFailure(limit_code)
        if isinstance(current, dict):
            stack.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> NoReturn:
    raise ValueError("non-finite JSON number")


def _inspection_counts(document: Mapping[str, Any]) -> dict[str, int]:
    counts = {"total": 0, "highlight": 0, "note": 0}
    items = document.get("items")
    if not isinstance(items, list):
        return counts
    counts["total"] = len(items)
    for item in items:
        if not isinstance(item, Mapping):
            continue
        kind = item.get("sr:kind")
        if kind in {"highlight", "note"}:
            counts[cast(str, kind)] += 1
    return counts


def _inspection_capabilities(document: Mapping[str, Any]) -> tuple[str, ...]:
    found: set[str] = set()
    items = document.get("items")
    if not isinstance(items, list):
        return ()
    for item in items:
        if not isinstance(item, Mapping):
            continue
        target = item.get("target")
        selectors = target.get("selector") if isinstance(target, Mapping) else None
        if not isinstance(selectors, list):
            continue
        for selector in selectors:
            if not isinstance(selector, Mapping):
                continue
            selector_type = selector.get("type")
            if selector_type in {"TextQuoteSelector", "sr:ParagraphCharSelector"}:
                found.add(cast(str, selector_type))
            elif selector_type == "sr:EpubCfiSelector":
                found.add("sr:EpubCfiSelector")
                found.add("epubcfi")
    return tuple(value for value in _INSPECTOR_CAPABILITY_ORDER if value in found)


def _validation_equivalent(left: ValidationResult, right: ValidationResult) -> bool:
    return left == right


def _report_matches_validation(
    report: ValidationReport,
    validation: ValidationResult,
) -> bool:
    return (
        report.status == validation.status
        and report.pack_id == validation.pack_id
        and report.semantic_digest == validation.semantic_digest
        and report.input_snapshot_digest == validation.input_snapshot_digest
        and report.input_count == validation.input_count
        and report.exported_count == validation.exported_count
        and report.skipped_count == validation.skipped_count
        and report.warning_count == validation.warning_count
        and report.error_count == validation.error_count
        and report.findings == validation.findings
    )


def _early_failed_result(code: str) -> ExportResult:
    validation = make_validation_failure(code)
    return ExportResult(
        status="failed",
        pack=None,
        annotations_json=None,
        detached_package=None,
        validation=validation,
        validation_report=None,
        current_pointer=None,
        revision_id=None,
    )


def _valid_policy(policy: ExportPolicy) -> bool:
    return (
        type(policy.deliverables) is str
        and policy.deliverables in {"json", "detached"}
        and type(policy.allow_partial) is bool
        and type(policy.allow_skips) is bool
        and type(policy.allow_empty) is bool
        and type(policy.force_regenerate) is bool
    )


def _builder_failure_code(code: str) -> str:
    if code in {"duplicate_annotation_id", "duplicate_pack_or_track_id_semantics"}:
        return code
    if code == "invalid_datetime":
        return "invalid_generated_timestamp"
    return "export_configuration_invalid"


def _assert_writer_exclusion_current(exclusion: _WriterExclusion) -> None:
    try:
        exclusion.assert_current()
    except (JobLeaseConflict, JobLeaseReadError):
        raise _ExportFailure("active_writer_present") from None


def _fatal_catalog_code(code: object, *, fallback: str) -> str:
    """Return ``code`` only when the common catalog permits fatal use."""

    if type(code) is str and code in ERROR_CATALOG:
        try:
            make_validation_finding(code, "fatal")
        except ValueError:
            pass
        else:
            return code
    return fallback


def _digest_value(value: object, field: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _digest_frame(tag: str, value: str) -> bytes:
    return f"{tag}:64:{value}\n".encode("ascii")


def _revision_frame(tag: str, value: str) -> bytes:
    return f"{tag}:{len(value)}:{value}\n".encode("ascii")


def _nested_string(document: Mapping[str, Any], *keys: str) -> str | None:
    value: object = document
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value if type(value) is str else None


def _existing_real_directory(path: Path) -> Path:
    try:
        status = os.lstat(path)
        resolved = path.resolve(strict=True)
        resolved_status = os.lstat(resolved)
    except OSError:
        raise ValueError("directory is unavailable") from None
    if (
        stat.S_ISLNK(status.st_mode)
        or not stat.S_ISDIR(status.st_mode)
        or not stat.S_ISDIR(resolved_status.st_mode)
    ):
        raise ValueError("directory is not a regular directory")
    return resolved


def _exact_output_child_directory(root: Path, requested_name: str) -> Path:
    """Return one direct child only when its stored spelling is exact."""

    root_descriptor = -1
    child_descriptor = -1
    try:
        root_descriptor = _open_directory_nofollow(
            root,
            failure_code="output_path_invalid",
        )
        names = os.listdir(root_descriptor)
        if names.count(requested_name) != 1:
            raise ValueError("book output directory spelling is not canonical")
        child_descriptor = _open_child_directory(root_descriptor, requested_name)
        candidate = root / requested_name
        if (
            not _directory_path_matches(root, root_descriptor)
            or not _named_directory_matches(
                root_descriptor,
                requested_name,
                child_descriptor,
            )
            or not _directory_path_matches(candidate, child_descriptor)
            or os.listdir(root_descriptor).count(requested_name) != 1
        ):
            raise ValueError("book output directory changed during resolution")
        return candidate
    except ValueError:
        raise
    except (_ExportFailure, OSError):
        raise ValueError("book output directory is unavailable") from None
    finally:
        if child_descriptor >= 0:
            with suppress(OSError):
                os.close(child_descriptor)
        if root_descriptor >= 0:
            with suppress(OSError):
                os.close(root_descriptor)


def _safe_book_child_name(value: object) -> bool:
    if type(value) is not str or not value or value in {".", ".."}:
        return False
    if Path(value).name != value or "/" in value or "\\" in value:
        return False
    return not any(unicodedata.category(character) == "Cc" for character in value)


def _freeze_current_pack(document: Mapping[str, Any]) -> AnnotationPackDocument:
    def freeze(value: object) -> object:
        if isinstance(value, Mapping):
            return _FrozenJsonDict({str(key): freeze(child) for key, child in value.items()})
        if isinstance(value, list):
            return _FrozenJsonList(freeze(child) for child in value)
        return value

    return AnnotationPackDocument(
        {str(key): freeze(value) for key, value in document.items()}
    )


__all__ = [
    "ExportPolicy",
    "ExportResult",
    "InspectionResult",
    "MAX_BOOK_DOCUMENT_BYTES",
    "export_annotation_pack",
    "inspect_annotation_pack",
    "publication_revision_id",
    "resolve_book_output_dir",
    "second_reader_input_snapshot_digest",
    "track_slug",
]
