"""Crash-safe Unit ledger and immutable Reading Product publication."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
from typing import Literal
from uuid import UUID, uuid4

from src.reading_core.canonical_json import canonical_json_bytes

from .builder import build_source_identity
from .models import (
    CommitResult,
    CompletionEvidence,
    FinalizeResult,
    ProductFinding,
    ProductUnit,
    ReadingProductDocument,
    SourceIdentity,
    UnitBuildResult,
    utc_seconds,
)
from .serialization import (
    finding_to_wire,
    product_unit_from_wire,
    serialize_document,
    source_identity_to_wire,
    unit_to_wire,
)
from .validation import (
    POINTER_SCHEMA_ID,
    REPORT_SCHEMA_ID,
    VALIDATOR_VERSION,
    ReadingProductValidationError,
    auxiliary_validator,
    parse_utc_seconds,
    validate_completion_evidence,
    validate_document,
    validate_source_identity,
    validate_unit,
)


_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_SCHEMA_SQL = """
CREATE TABLE metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
) STRICT;
CREATE TABLE units (
    sequence_index INTEGER PRIMARY KEY NOT NULL,
    unit_id TEXT UNIQUE NOT NULL,
    canonical_json BLOB NOT NULL,
    canonical_sha256 TEXT NOT NULL,
    findings_json BLOB NOT NULL,
    findings_sha256 TEXT NOT NULL,
    rejected_marginalia INTEGER NOT NULL CHECK (rejected_marginalia >= 0)
) STRICT;
"""


class ReadingProductStoreError(RuntimeError):
    __slots__ = ("code",)

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class ReadingProductProjectionError(ReadingProductStoreError):
    """The ledger commit succeeded but its derived JSON projection failed."""

    committed = True


@dataclass(frozen=True, slots=True)
class _Metadata:
    reading_id: str
    source: SourceIdentity
    started_at: str
    status: Literal["partial", "sealing", "complete"]
    sealing_completed_at: str | None
    completed_at: str | None
    revision_id: str | None


class ReadingProductStore:
    """One explicitly selected Reading Product reading revision."""

    def __init__(self, output_dir: Path, reading_id: str) -> None:
        self.output_dir = _exact_path(output_dir)
        self.reading_id = _validated_reading_id(reading_id)
        self.runtime_dir = runtime_reading_product_dir(output_dir, reading_id)
        self.ledger_path = self.runtime_dir / "ledger.sqlite3"
        self.partial_snapshot_path = self.runtime_dir / "reading-product.partial.json"
        self._lock_path = self.runtime_dir / ".writer.lock"

    @classmethod
    def create(
        cls,
        output_dir: Path,
        *,
        epub_sha256: str,
        book_document: Mapping[str, object],
        started_at: datetime | str | None = None,
        reading_id: str | None = None,
    ) -> ReadingProductStore:
        output = _exact_path(output_dir)
        identity = build_source_identity(epub_sha256, book_document)
        canonical_started = utc_seconds(started_at)
        identifier = _validated_reading_id(
            reading_id or f"urn:uuid:{uuid4()}"
        )
        store = cls(output, identifier)
        runtime_root = output / "_runtime" / "reading-products"
        runtime_root.mkdir(parents=True, exist_ok=True)
        try:
            store.runtime_dir.mkdir(mode=0o700)
        except FileExistsError:
            raise ReadingProductStoreError(
                "reading_revision_exists", "Reading Product revision already exists"
            ) from None
        try:
            connection = sqlite3.connect(store.ledger_path, timeout=30)
            try:
                _configure_connection(connection)
                connection.executescript(_SCHEMA_SQL)
                rows = {
                    "schema_version": "reading-product-store/1.0",
                    "reading_id": identifier,
                    "epub_sha256": identity.epub_sha256,
                    "book_document_substrate_sha256": identity.book_document_substrate_sha256,
                    "started_at": canonical_started,
                    "status": "partial",
                }
                connection.executemany(
                    "INSERT INTO metadata(key, value) VALUES (?, ?)", rows.items()
                )
                connection.commit()
            finally:
                connection.close()
            store._write_partial_snapshot(book_document=book_document)
        except Exception:
            shutil.rmtree(store.runtime_dir, ignore_errors=True)
            raise
        return store

    @classmethod
    def open(cls, output_dir: Path, reading_id: str) -> ReadingProductStore:
        store = cls(output_dir, reading_id)
        if not store.ledger_path.is_file():
            raise ReadingProductStoreError(
                "reading_revision_missing", "Reading Product revision does not exist"
            )
        metadata = store._metadata()
        if metadata.reading_id != store.reading_id:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Reading Product revision identity is inconsistent"
            )
        return store

    @property
    def source(self) -> SourceIdentity:
        return self._metadata().source

    @property
    def started_at(self) -> str:
        return self._metadata().started_at

    def next_sequence_index(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(sequence_index), 0) + 1 FROM units"
            ).fetchone()
        value = int(row[0])
        if value > 999_999:
            raise ReadingProductStoreError(
                "unit_sequence_exhausted", "Reading Product Unit sequence is exhausted"
            )
        return value

    def latest_unit(self) -> ProductUnit | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT canonical_json, canonical_sha256 FROM units "
                "ORDER BY sequence_index DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        content = bytes(row[0])
        _verify_canonical_blob(content, expected_sha256=str(row[1]))
        return product_unit_from_wire(_strict_json_loads(content))

    def load_units(self) -> tuple[ProductUnit, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT canonical_json, canonical_sha256 FROM units ORDER BY sequence_index"
            ).fetchall()
        result: list[ProductUnit] = []
        for content_value, digest_value in rows:
            try:
                content = bytes(content_value)
                _verify_canonical_blob(content, expected_sha256=str(digest_value))
                raw = _strict_json_loads(content)
                result.append(product_unit_from_wire(raw))
            except Exception:
                raise ReadingProductStoreError(
                    "reading_revision_corrupt", "Stored Product Unit is invalid"
                ) from None
        return tuple(result)

    def snapshot(
        self,
        *,
        book_document: Mapping[str, object] | None = None,
    ) -> ReadingProductDocument:
        metadata = self._metadata()
        status: Literal["partial", "complete"] = (
            "complete" if metadata.status == "complete" else "partial"
        )
        document = ReadingProductDocument(
            reading_id=metadata.reading_id,
            status=status,
            source=metadata.source,
            started_at=metadata.started_at,
            completed_at=metadata.completed_at if status == "complete" else None,
            units=self.load_units(),
        )
        validate_document(document, book_document=book_document)
        return document

    def commit_unit(
        self,
        unit: ProductUnit | UnitBuildResult,
        *,
        book_document: Mapping[str, object],
        epub_sha256: str,
        findings: Sequence[ProductFinding] = (),
    ) -> CommitResult:
        build_result = unit if isinstance(unit, UnitBuildResult) else None
        product_unit = build_result.unit if build_result is not None else unit
        if build_result is not None and findings:
            raise TypeError("findings must not be supplied with UnitBuildResult")
        safe_findings = build_result.findings if build_result is not None else tuple(findings)
        if any(not isinstance(finding, ProductFinding) for finding in safe_findings):
            raise TypeError("findings must contain ProductFinding values")
        with self._writer_lock():
            metadata = self._metadata()
            self._assert_source(metadata.source, book_document, epub_sha256)
            validate_unit(product_unit, book_document=book_document)
            unit_bytes = canonical_json_bytes(unit_to_wire(product_unit))
            unit_digest = hashlib.sha256(unit_bytes).hexdigest()
            finding_bytes = canonical_json_bytes(
                [finding_to_wire(finding) for finding in safe_findings]
            )
            finding_digest = hashlib.sha256(finding_bytes).hexdigest()
            rejected_count = sum(
                finding.severity == "skipped" for finding in safe_findings
            )
            if metadata.status != "partial":
                raise ReadingProductStoreError(
                    "reading_revision_sealed", "Reading Product revision is not writable"
                )
            prior_units = self.load_units()
            existing = self._existing_unit(product_unit)
            if existing is not None:
                if existing == (
                    unit_digest,
                    unit_bytes,
                    finding_digest,
                    finding_bytes,
                ):
                    try:
                        snapshot = self._write_partial_snapshot(
                            book_document=book_document
                        )
                    except Exception as exc:
                        raise ReadingProductProjectionError(
                            "partial_projection_failed",
                            "Committed Product Unit projection could not be rebuilt",
                        ) from exc
                    return CommitResult(
                        status="unchanged",
                        unit=product_unit,
                        snapshot=snapshot,
                        projection_path=self.partial_snapshot_path,
                    )
                raise ReadingProductStoreError(
                    "unit_commit_conflict", "Unit id or sequence conflicts with stored bytes"
                )
            expected = len(prior_units) + 1
            if product_unit.sequence_index != expected:
                raise ReadingProductStoreError(
                    "unit_sequence_gap", "Product Unit sequence must be contiguous"
                )
            candidate_snapshot = ReadingProductDocument(
                reading_id=metadata.reading_id,
                status="partial",
                source=metadata.source,
                started_at=metadata.started_at,
                units=(*prior_units, product_unit),
            )
            validate_document(candidate_snapshot, book_document=book_document)
            try:
                with self._connect() as connection:
                    connection.execute("BEGIN IMMEDIATE")
                    current_status = _metadata_value(connection, "status")
                    if current_status != "partial":
                        raise ReadingProductStoreError(
                            "reading_revision_sealed",
                            "Reading Product revision is not writable",
                        )
                    connection.execute(
                        """
                        INSERT INTO units(
                            sequence_index, unit_id, canonical_json, canonical_sha256,
                            findings_json, findings_sha256, rejected_marginalia
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            product_unit.sequence_index,
                            product_unit.unit_id,
                            unit_bytes,
                            unit_digest,
                            finding_bytes,
                            finding_digest,
                            rejected_count,
                        ),
                    )
                    connection.commit()
            except sqlite3.IntegrityError:
                raise ReadingProductStoreError(
                    "unit_commit_conflict", "Unit id or sequence conflicts with stored bytes"
                ) from None
            try:
                snapshot = self._write_partial_snapshot(book_document=book_document)
            except Exception as exc:
                raise ReadingProductProjectionError(
                    "partial_projection_failed",
                    "Product Unit committed but its projection could not be rebuilt",
                ) from exc
            return CommitResult(
                status="committed",
                unit=product_unit,
                snapshot=snapshot,
                projection_path=self.partial_snapshot_path,
            )

    def finalize(
        self,
        *,
        book_document: Mapping[str, object],
        epub_sha256: str,
        completion: CompletionEvidence,
        completed_at: datetime | str | None = None,
    ) -> FinalizeResult:
        with self._writer_lock():
            metadata = self._metadata()
            self._assert_source(metadata.source, book_document, epub_sha256)
            units = self.load_units()
            validate_completion_evidence(completion, units=units)
            if not units:
                raise ReadingProductValidationError(
                    "empty_complete_product",
                    "complete Reading Product needs at least one Unit",
                )
            if metadata.status == "complete":
                return self._verify_finalized(metadata, book_document=book_document)

            requested_completed = (
                utc_seconds(completed_at)
                if completed_at is not None
                else metadata.sealing_completed_at or utc_seconds()
            )
            if (
                metadata.sealing_completed_at is not None
                and requested_completed != metadata.sealing_completed_at
            ):
                raise ReadingProductStoreError(
                    "finalization_conflict", "Finalization timestamp changed during retry"
                )
            parse_utc_seconds(requested_completed)
            document = ReadingProductDocument(
                reading_id=metadata.reading_id,
                status="complete",
                source=metadata.source,
                started_at=metadata.started_at,
                completed_at=requested_completed,
                units=units,
            )
            product_bytes = serialize_document(document, book_document=book_document)
            revision_id = hashlib.sha256(product_bytes).hexdigest()

            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                status = _metadata_value(connection, "status")
                if status not in {"partial", "sealing"}:
                    raise ReadingProductStoreError(
                        "reading_revision_corrupt", "Reading Product state changed unexpectedly"
                    )
                _set_metadata(connection, "status", "sealing")
                _set_metadata(connection, "sealing_completed_at", requested_completed)
                connection.commit()

            findings, rejected_count = self._load_findings()
            report = _validation_report(
                document=document,
                revision_id=revision_id,
                findings=findings,
                rejected_count=rejected_count,
            )
            _validate_auxiliary_document(report, REPORT_SCHEMA_ID)
            report_bytes = canonical_json_bytes(report)
            document_path, report_path = self._publish_revision(
                revision_id=revision_id,
                product_bytes=product_bytes,
                report_bytes=report_bytes,
            )
            pointer_path = self._publish_pointer(
                revision_id=revision_id,
                product_bytes=product_bytes,
                report_bytes=report_bytes,
            )
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                _set_metadata(connection, "status", "complete")
                _set_metadata(connection, "completed_at", requested_completed)
                _set_metadata(connection, "revision_id", revision_id)
                connection.commit()
            return FinalizeResult(
                status="published",
                revision_id=revision_id,
                document_path=document_path,
                report_path=report_path,
                current_pointer_path=pointer_path,
            )

    def _verify_finalized(
        self,
        metadata: _Metadata,
        *,
        book_document: Mapping[str, object],
    ) -> FinalizeResult:
        if metadata.revision_id is None or metadata.completed_at is None:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Completed revision metadata is incomplete"
            )
        document = self.snapshot(book_document=book_document)
        content = serialize_document(document, book_document=book_document)
        if hashlib.sha256(content).hexdigest() != metadata.revision_id:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Completed revision digest is inconsistent"
            )
        revision_dir = public_reading_product_revision_dir(
            self.output_dir, metadata.revision_id
        )
        document_path = revision_dir / "reading-product.json"
        report_path = revision_dir / "validation-report.json"
        pointer_path = public_reading_product_current_file(self.output_dir)
        if not document_path.is_file() or document_path.read_bytes() != content:
            raise ReadingProductStoreError(
                "immutable_revision_changed", "Published Reading Product bytes changed"
            )
        if not report_path.is_file() or not pointer_path.is_file():
            raise ReadingProductStoreError(
                "immutable_revision_changed", "Published revision companions are missing"
            )
        findings, rejected_count = self._load_findings()
        expected_report = _validation_report(
            document=document,
            revision_id=metadata.revision_id,
            findings=findings,
            rejected_count=rejected_count,
        )
        _validate_auxiliary_document(expected_report, REPORT_SCHEMA_ID)
        expected_report_bytes = canonical_json_bytes(expected_report)
        if report_path.read_bytes() != expected_report_bytes:
            raise ReadingProductStoreError(
                "immutable_revision_changed", "Published validation report bytes changed"
            )
        pointer_content = pointer_path.read_bytes()
        pointer = _verify_canonical_blob(pointer_content)
        _validate_auxiliary_document(pointer, POINTER_SCHEMA_ID)
        expected_pointer = _publication_pointer(
            reading_id=self.reading_id,
            revision_id=metadata.revision_id,
            product_bytes=content,
            report_bytes=expected_report_bytes,
        )
        if pointer != expected_pointer:
            raise ReadingProductStoreError(
                "current_pointer_changed", "Current pointer no longer selects this revision"
            )
        return FinalizeResult(
            status="unchanged",
            revision_id=metadata.revision_id,
            document_path=document_path,
            report_path=report_path,
            current_pointer_path=pointer_path,
        )

    def _write_partial_snapshot(
        self, *, book_document: Mapping[str, object]
    ) -> ReadingProductDocument:
        snapshot = self.snapshot(book_document=book_document)
        if snapshot.status != "partial":
            raise ReadingProductStoreError(
                "reading_revision_sealed", "Completed product has no partial projection"
            )
        _atomic_replace(self.partial_snapshot_path, serialize_document(snapshot, book_document=book_document))
        return snapshot

    def _publish_revision(
        self,
        *,
        revision_id: str,
        product_bytes: bytes,
        report_bytes: bytes,
    ) -> tuple[Path, Path]:
        revisions = self.output_dir / "public" / "reading-products" / "revisions"
        revisions.mkdir(parents=True, exist_ok=True)
        final = revisions / revision_id
        expected = {
            "reading-product.json": product_bytes,
            "validation-report.json": report_bytes,
        }
        if final.exists():
            _verify_revision_directory(final, expected)
            return final / "reading-product.json", final / "validation-report.json"
        temporary = revisions / f".tmp-{revision_id}-{uuid4().hex}"
        temporary.mkdir(mode=0o700)
        try:
            for name, content in expected.items():
                _write_new_file(temporary / name, content)
            _fsync_directory(temporary)
            try:
                os.replace(temporary, final)
            except OSError:
                if final.exists():
                    _verify_revision_directory(final, expected)
                else:
                    raise
            _fsync_directory(revisions)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
        _verify_revision_directory(final, expected)
        return final / "reading-product.json", final / "validation-report.json"

    def _publish_pointer(
        self,
        *,
        revision_id: str,
        product_bytes: bytes,
        report_bytes: bytes,
    ) -> Path:
        pointer = _publication_pointer(
            reading_id=self.reading_id,
            revision_id=revision_id,
            product_bytes=product_bytes,
            report_bytes=report_bytes,
        )
        _validate_auxiliary_document(pointer, POINTER_SCHEMA_ID)
        path = public_reading_product_current_file(self.output_dir)
        _atomic_replace(path, canonical_json_bytes(pointer))
        return path

    def _existing_unit(
        self, unit: ProductUnit
    ) -> tuple[str, bytes, str, bytes] | None:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sequence_index, unit_id, canonical_sha256, canonical_json,
                       findings_sha256, findings_json
                FROM units WHERE sequence_index = ? OR unit_id = ?
                """,
                (unit.sequence_index, unit.unit_id),
            ).fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Stored Unit identities are inconsistent"
            )
        row = rows[0]
        if row[0] != unit.sequence_index or row[1] != unit.unit_id:
            raise ReadingProductStoreError(
                "unit_commit_conflict", "Unit id or sequence conflicts with stored bytes"
            )
        return str(row[2]), bytes(row[3]), str(row[4]), bytes(row[5])

    def _load_findings(self) -> tuple[tuple[ProductFinding, ...], int]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT findings_json, findings_sha256, rejected_marginalia "
                "FROM units ORDER BY sequence_index"
            ).fetchall()
        findings: list[ProductFinding] = []
        rejected = 0
        for content, digest, count in rows:
            rejected += int(count)
            try:
                finding_content = bytes(content)
                _verify_canonical_blob(
                    finding_content, expected_sha256=str(digest)
                )
                raw = _strict_json_loads(finding_content)
                if not isinstance(raw, list):
                    raise ValueError("findings root is not an array")
                if int(count) != sum(
                    isinstance(item, Mapping) and item.get("severity") == "skipped"
                    for item in raw
                ):
                    raise ValueError("rejected count does not match findings")
                for item in raw:
                    findings.append(_finding_from_wire(item))
            except Exception:
                raise ReadingProductStoreError(
                    "reading_revision_corrupt", "Stored validation findings are invalid"
                ) from None
        return tuple(findings), rejected

    def _assert_source(
        self,
        source: SourceIdentity,
        book_document: Mapping[str, object],
        epub_sha256: str,
    ) -> None:
        validate_source_identity(source, book_document=book_document)
        if type(epub_sha256) is not str or epub_sha256 != source.epub_sha256:
            raise ReadingProductValidationError(
                "source_identity_mismatch",
                "current EPUB bytes do not match the Reading Product source",
            )

    def _metadata(self) -> _Metadata:
        try:
            with self._connect() as connection:
                rows = dict(connection.execute("SELECT key, value FROM metadata"))
        except sqlite3.DatabaseError:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Reading Product ledger is unreadable"
            ) from None
        required = {
            "schema_version",
            "reading_id",
            "epub_sha256",
            "book_document_substrate_sha256",
            "started_at",
            "status",
        }
        if required - rows.keys() or rows.get("schema_version") != "reading-product-store/1.0":
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Reading Product ledger metadata is invalid"
            )
        status = rows["status"]
        if status not in {"partial", "sealing", "complete"}:
            raise ReadingProductStoreError(
                "reading_revision_corrupt", "Reading Product ledger status is invalid"
            )
        source = SourceIdentity(
            epub_sha256=rows["epub_sha256"],
            book_document_substrate_sha256=rows[
                "book_document_substrate_sha256"
            ],
        )
        validate_source_identity(source)
        parse_utc_seconds(rows["started_at"])
        return _Metadata(
            reading_id=_validated_reading_id(rows["reading_id"]),
            source=source,
            started_at=rows["started_at"],
            status=status,  # type: ignore[arg-type]
            sealing_completed_at=rows.get("sealing_completed_at"),
            completed_at=rows.get("completed_at"),
            revision_id=rows.get("revision_id"),
        )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.ledger_path, timeout=30)
        try:
            _configure_connection(connection)
            yield connection
        finally:
            connection.close()

    @contextmanager
    def _writer_lock(self) -> Iterator[None]:
        descriptor = os.open(self._lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)


def runtime_reading_product_dir(output_dir: Path, reading_id: str) -> Path:
    identifier = _validated_reading_id(reading_id).removeprefix("urn:uuid:")
    return _exact_path(output_dir) / "_runtime" / "reading-products" / identifier


def public_reading_product_revision_dir(output_dir: Path, revision_id: str) -> Path:
    if type(revision_id) is not str or _SHA256.fullmatch(revision_id) is None:
        raise ValueError("Reading Product revision id is invalid")
    return (
        _exact_path(output_dir)
        / "public"
        / "reading-products"
        / "revisions"
        / revision_id
    )


def public_reading_product_current_file(output_dir: Path) -> Path:
    return _exact_path(output_dir) / "public" / "reading-products" / "current.json"


def _validation_report(
    *,
    document: ReadingProductDocument,
    revision_id: str,
    findings: Sequence[ProductFinding],
    rejected_count: int,
) -> dict[str, object]:
    marginalia_count = sum(len(unit.marginalia) for unit in document.units)
    ordered = sorted(
        findings,
        key=lambda finding: (
            finding.unit_id or "",
            finding.marginalia_id or "",
            finding.code,
            finding.json_pointer or "",
        ),
    )
    return {
        "schema_version": "reading-product-validation-report/1.0",
        "validator_version": VALIDATOR_VERSION,
        "status": "valid",
        "reading_id": document.reading_id,
        "reading_product_sha256": revision_id,
        "source": source_identity_to_wire(document.source),
        "counts": {
            "units": len(document.units),
            "marginalia": marginalia_count,
            "rejected_marginalia": rejected_count,
            "errors": 0,
        },
        "findings": [finding_to_wire(finding) for finding in ordered],
    }


def _publication_pointer(
    *,
    reading_id: str,
    revision_id: str,
    product_bytes: bytes,
    report_bytes: bytes,
) -> dict[str, object]:
    return {
        "schema_version": "reading-product-publication-pointer/1.0",
        "reading_id": reading_id,
        "revision_id": revision_id,
        "reading_product": f"revisions/{revision_id}/reading-product.json",
        "reading_product_sha256": hashlib.sha256(product_bytes).hexdigest(),
        "validation_report": f"revisions/{revision_id}/validation-report.json",
        "validation_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
    }


def _validate_auxiliary_document(value: object, schema_id: str) -> None:
    errors = sorted(
        auxiliary_validator(schema_id).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ReadingProductStoreError(
            "auxiliary_validation_failed",
            "Reading Product publication companion failed strict validation",
        )


def _finding_from_wire(value: object) -> ProductFinding:
    if not isinstance(value, Mapping):
        raise ValueError("finding must be an object")
    allowed = {
        "code",
        "severity",
        "message",
        "unit_id",
        "marginalia_id",
        "json_pointer",
    }
    if set(value) - allowed or not {"code", "severity", "message"}.issubset(value):
        raise ValueError("finding fields are invalid")
    severity = value["severity"]
    if severity not in {"error", "warning", "skipped"}:
        raise ValueError("finding severity is invalid")
    return ProductFinding(
        code=str(value["code"]),
        severity=severity,  # type: ignore[arg-type]
        message=str(value["message"]),
        unit_id=str(value["unit_id"]) if "unit_id" in value else None,
        marginalia_id=(
            str(value["marginalia_id"]) if "marginalia_id" in value else None
        ),
        json_pointer=(
            str(value["json_pointer"]) if "json_pointer" in value else None
        ),
    )


def _strict_json_loads(content: bytes) -> object:
    class _DuplicateKey(ValueError):
        pass

    def pairs(values: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in values:
            if key in result:
                raise _DuplicateKey(key)
            result[key] = value
        return result

    try:
        return json.loads(content, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, _DuplicateKey):
        raise ReadingProductStoreError(
            "reading_revision_corrupt", "Stored JSON is not strict valid JSON"
        ) from None


def _verify_canonical_blob(
    content: bytes,
    *,
    expected_sha256: str | None = None,
) -> object:
    if expected_sha256 is not None and (
        _SHA256.fullmatch(expected_sha256) is None
        or hashlib.sha256(content).hexdigest() != expected_sha256
    ):
        raise ReadingProductStoreError(
            "reading_revision_corrupt", "Stored JSON digest is inconsistent"
        )
    value = _strict_json_loads(content)
    if canonical_json_bytes(value) != content:
        raise ReadingProductStoreError(
            "reading_revision_corrupt", "Stored JSON bytes are not canonical"
        )
    return value


def _configure_connection(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=30000")


def _metadata_value(connection: sqlite3.Connection, key: str) -> str:
    row = connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
    if row is None:
        raise ReadingProductStoreError(
            "reading_revision_corrupt", "Reading Product metadata is missing"
        )
    return str(row[0])


def _set_metadata(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT INTO metadata(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def _validated_reading_id(value: str) -> str:
    if type(value) is not str or not value.startswith("urn:uuid:"):
        raise ValueError("reading_id must be a UUIDv4 URN")
    try:
        parsed = UUID(value.removeprefix("urn:uuid:"))
    except ValueError:
        raise ValueError("reading_id must be a UUIDv4 URN") from None
    if parsed.version != 4 or value != f"urn:uuid:{parsed}":
        raise ValueError("reading_id must be a lowercase UUIDv4 URN")
    return value


def _exact_path(value: Path) -> Path:
    if type(value) is not Path and not isinstance(value, Path):
        raise TypeError("output_dir must be a pathlib.Path")
    return value


def _write_new_file(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        offset = 0
        while offset < len(content):
            offset += os.write(descriptor, content[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_replace(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.tmp-{uuid4().hex}"
    try:
        _write_new_file(temporary, content)
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _verify_revision_directory(directory: Path, expected: Mapping[str, bytes]) -> None:
    try:
        if stat.S_ISLNK(directory.lstat().st_mode) or not directory.is_dir():
            raise ReadingProductStoreError(
                "immutable_revision_changed", "Revision path is not a safe directory"
            )
        names = {entry.name for entry in directory.iterdir()}
        if names != set(expected):
            raise ReadingProductStoreError(
                "immutable_revision_changed", "Revision file set changed"
            )
        for name, content in expected.items():
            path = directory / name
            if stat.S_ISLNK(path.lstat().st_mode) or not path.is_file():
                raise ReadingProductStoreError(
                    "immutable_revision_changed", "Revision file is not regular"
                )
            if path.read_bytes() != content:
                raise ReadingProductStoreError(
                    "immutable_revision_changed", "Revision bytes changed"
                )
    except FileNotFoundError:
        raise ReadingProductStoreError(
            "immutable_revision_changed", "Revision disappeared during verification"
        ) from None


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


__all__ = [
    "ReadingProductProjectionError",
    "ReadingProductStore",
    "ReadingProductStoreError",
    "public_reading_product_current_file",
    "public_reading_product_revision_dir",
    "runtime_reading_product_dir",
]
