"""Strict default adapter from complete Reading Product v1 to Pack drafts.

The adapter reads only the public complete-product pointer and its immutable
revision.  It deliberately never consults run state, mechanism-private
reaction records, audit, prompts, or memory.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
from importlib import resources
import json
import os
from pathlib import Path
import re
import stat
from typing import NoReturn

from jsonschema import Draft202012Validator, FormatChecker

from src.annotation_pack.drafts import (
    AnnotationDraft,
    ProducerAdapterError,
    ProducerDraftResult,
)
from src.reading_core.canonical_json import canonical_json_bytes
from src.reading_product.serialization import (
    load_document_bytes,
    marginalia_to_wire,
)
from src.reading_product.validation import validate_document


ADAPTER_VERSION = "1.0.0"
PRODUCER_FORMAT = "reading-product-v1"

MAX_POINTER_BYTES = 64 * 1024
MAX_PRODUCT_BYTES = 128 * 1024 * 1024
MAX_REPORT_BYTES = 4 * 1024 * 1024
READ_CHUNK_BYTES = 1024 * 1024

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_PRODUCT_RELATIVE = re.compile(
    r"revisions/([0-9a-f]{64})/reading-product\.json\Z", re.ASCII
)
_REPORT_RELATIVE = re.compile(
    r"revisions/([0-9a-f]{64})/validation-report\.json\Z", re.ASCII
)


class _DuplicateJsonKey(ValueError):
    pass


class ReadingProductProducerAdapter:
    """Load one stable, complete Reading Product into neutral Pack drafts."""

    def load_drafts(self, *, output_dir: Path) -> ProducerDraftResult:
        root = output_dir / "public" / "reading-products"
        pointer_path = root / "current.json"
        pointer_bytes, _pointer_digest = _read_stable_file(
            pointer_path,
            maximum_bytes=MAX_POINTER_BYTES,
            unavailable_code="reading_product_unavailable",
        )
        pointer = _strict_json_object(pointer_bytes)
        _validate_auxiliary(pointer, "publication-pointer.schema.json")

        revision_id = pointer.get("revision_id")
        product_relative = pointer.get("reading_product")
        report_relative = pointer.get("validation_report")
        product_match = (
            _PRODUCT_RELATIVE.fullmatch(product_relative)
            if type(product_relative) is str
            else None
        )
        report_match = (
            _REPORT_RELATIVE.fullmatch(report_relative)
            if type(report_relative) is str
            else None
        )
        if (
            type(revision_id) is not str
            or _SHA256.fullmatch(revision_id) is None
            or product_match is None
            or report_match is None
            or product_match.group(1) != revision_id
            or report_match.group(1) != revision_id
        ):
            _fail("reading_product_schema_unsupported")

        product_path = root / product_relative
        report_path = root / report_relative
        product_bytes, product_digest = _read_stable_file(
            product_path,
            maximum_bytes=MAX_PRODUCT_BYTES,
            unavailable_code="reading_product_unavailable",
        )
        report_bytes, report_digest = _read_stable_file(
            report_path,
            maximum_bytes=MAX_REPORT_BYTES,
            unavailable_code="reading_product_unavailable",
        )
        if (
            pointer.get("reading_product_sha256") != product_digest
            or product_digest != revision_id
            or pointer.get("validation_report_sha256") != report_digest
        ):
            _fail("reading_product_schema_unsupported")

        product_object = _strict_json_object(product_bytes)
        if canonical_json_bytes(product_object) != product_bytes:
            _fail("reading_product_schema_unsupported")
        try:
            document = load_document_bytes(product_bytes)
            validate_document(document)
        except Exception:
            _fail("reading_product_schema_unsupported")
        if document.status != "complete":
            _fail("reading_product_not_complete")
        if document.reading_id != pointer.get("reading_id"):
            _fail("reading_product_schema_unsupported")

        report = _strict_json_object(report_bytes)
        if canonical_json_bytes(report) != report_bytes:
            _fail("reading_product_schema_unsupported")
        _validate_auxiliary(report, "validation-report.schema.json")
        if (
            report.get("status") != "valid"
            or report.get("reading_id") != document.reading_id
            or report.get("reading_product_sha256") != product_digest
            or report.get("source")
            != {
                "epub_sha256": document.source.epub_sha256,
                "book_document_substrate_sha256": (
                    document.source.book_document_substrate_sha256
                ),
            }
        ):
            _fail("reading_product_schema_unsupported")

        # Re-read the atomic pointer after both immutable companions.  A switch
        # during the snapshot invalidates the operation instead of mixing
        # revisions.
        final_pointer_bytes, _ = _read_stable_file(
            pointer_path,
            maximum_bytes=MAX_POINTER_BYTES,
            unavailable_code="input_changed_during_export",
        )
        if final_pointer_bytes != pointer_bytes:
            _fail("input_changed_during_export")

        drafts: list[AnnotationDraft] = []
        accepted_digests: list[str] = []
        index = 0
        for unit in document.units:
            created_at = datetime.strptime(
                unit.settled_at, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            for marginalia in unit.marginalia:
                record_bytes = canonical_json_bytes(
                    {
                        "unit_id": unit.unit_id,
                        "settled_at": unit.settled_at,
                        "marginalia": marginalia_to_wire(marginalia),
                    }
                )
                record_digest = hashlib.sha256(record_bytes).hexdigest()
                drafts.append(
                    AnnotationDraft(
                        kind=marginalia.kind,
                        source_range=marginalia.source_range,
                        source_quote=marginalia.source_quote,
                        body_text=marginalia.body_text,
                        created_at=created_at,
                        source_record_index=index,
                        source_record_digest=record_digest,
                    )
                )
                accepted_digests.append(record_digest)
                index += 1

        return ProducerDraftResult(
            drafts=tuple(drafts),
            # Historical constructor spelling; see ProducerDraftResult.
            reaction_ledger_sha256=product_digest,
            accepted_record_digests=tuple(accepted_digests),
            findings=(),
            input_count=index,
            source_epub_sha256=document.source.epub_sha256,
            book_document_substrate_sha256=(
                document.source.book_document_substrate_sha256
            ),
            producer_reading_id=document.reading_id,
        )


def _validate_auxiliary(value: Mapping[str, object], filename: str) -> None:
    try:
        content = (
            resources.files("src.reading_product.resources")
            .joinpath(filename)
            .read_bytes()
        )
        schema = json.loads(content)
        Draft202012Validator.check_schema(schema)
        errors = tuple(
            Draft202012Validator(
                schema, format_checker=FormatChecker()
            ).iter_errors(value)
        )
    except Exception:
        _fail("reading_product_schema_unsupported")
    if errors:
        _fail("reading_product_schema_unsupported")


def _strict_json_object(content: bytes) -> Mapping[str, object]:
    if content.startswith(b"\xef\xbb\xbf"):
        _fail("reading_product_invalid_json")
    try:
        text = content.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except Exception:
        _fail("reading_product_invalid_json")
    if not isinstance(value, Mapping):
        _fail("reading_product_invalid_json")
    return value


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(key)
        result[key] = value
    return result


def _reject_constant(_value: str) -> NoReturn:
    raise ValueError("non-finite JSON constant")


def _read_stable_file(
    path: Path,
    *,
    maximum_bytes: int,
    unavailable_code: str,
) -> tuple[bytes, str]:
    descriptor = -1
    parent_descriptor = -1
    try:
        descriptor, parent_descriptor, leaf_name = _open_nofollow(
            path, failure_code=unavailable_code
        )
        before = os.fstat(descriptor)
        path_before = os.stat(
            leaf_name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            not stat.S_ISREG(before.st_mode)
            or _stat_identity(before) != _stat_identity(path_before)
        ):
            _fail(unavailable_code)
        if before.st_size > maximum_bytes:
            _fail("reading_product_limit_exceeded")
        chunks: list[bytes] = []
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(descriptor, READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > maximum_bytes:
                _fail("reading_product_limit_exceeded")
            chunks.append(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        path_after = os.stat(
            leaf_name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            total != before.st_size
            or _stat_identity(before) != _stat_identity(after)
            or _stat_identity(after) != _stat_identity(path_after)
        ):
            _fail("input_changed_during_export")
        return b"".join(chunks), digest.hexdigest()
    except ProducerAdapterError:
        raise
    except (OSError, TypeError, ValueError):
        _fail(unavailable_code)
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if parent_descriptor >= 0:
            try:
                os.close(parent_descriptor)
            except OSError:
                pass


def _open_nofollow(
    path: Path, *, failure_code: str
) -> tuple[int, int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        _fail(failure_code)
    try:
        absolute = os.path.abspath(os.fspath(path))
    except (OSError, TypeError, ValueError):
        _fail(failure_code)
    components = tuple(part for part in absolute.split(os.sep) if part)
    if not components:
        _fail(failure_code)
    directory_flags = (
        os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow | directory
    )
    try:
        current = os.open(os.sep, directory_flags)
    except (OSError, TypeError, ValueError):
        _fail(failure_code)
    try:
        for component in components[:-1]:
            child = os.open(component, directory_flags, dir_fd=current)
            os.close(current)
            current = child
        file_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | nofollow
        descriptor = os.open(components[-1], file_flags, dir_fd=current)
        return descriptor, current, components[-1]
    except (OSError, TypeError, ValueError):
        try:
            os.close(current)
        except OSError:
            pass
        _fail(failure_code)


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _fail(code: str) -> NoReturn:
    raise ProducerAdapterError(code)


__all__ = ["ADAPTER_VERSION", "PRODUCER_FORMAT", "ReadingProductProducerAdapter"]
