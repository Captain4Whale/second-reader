"""Admission builders for mechanism-neutral Reading Product records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re

from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_core.source_ranges import SourceRange

from .models import (
    MarginaliaCandidate,
    ProductFinding,
    ProductMarginalia,
    ProductUnit,
    SourceIdentity,
    UnitBuildResult,
    utc_seconds,
)
from .validation import ReadingProductValidationError, validate_source_identity, validate_unit


_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_SAFE_REJECTION_MESSAGES = {
    "ambiguous_first_match": (
        "ambiguous_source_quote",
        "Marginalia source text was not uniquely resolved.",
    ),
    "ambiguous_source_quote": (
        "ambiguous_source_quote",
        "Marginalia source text was not uniquely resolved.",
    ),
    "unresolved_source_quote": (
        "unresolved_source_quote",
        "Marginalia source text was not resolved exactly.",
    ),
    "fallback_unit_span": (
        "unresolved_source_quote",
        "Marginalia used a fallback Unit span instead of an exact source range.",
    ),
}


def sha256_file(path: Path) -> str:
    """Hash one stable regular file and fail if it changes during the read."""

    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path")
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            if not os.path.isfile(path) or before.st_size < 0:
                raise ValueError("source EPUB must be a regular file")
            digest = hashlib.sha256()
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise ValueError("source EPUB could not be hashed safely") from exc
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError("source EPUB changed while it was hashed")
    return digest.hexdigest()


def build_source_identity(
    epub_sha256: str,
    book_document: Mapping[str, object],
) -> SourceIdentity:
    if type(epub_sha256) is not str or _SHA256.fullmatch(epub_sha256) is None:
        raise ReadingProductValidationError(
            "invalid_source_identity", "EPUB SHA-256 must be lowercase hexadecimal"
        )
    try:
        substrate = book_document_substrate_digest(book_document)
    except Exception:
        raise ReadingProductValidationError(
            "invalid_book_document",
            "canonical BookDocument could not be fingerprinted",
        ) from None
    result = SourceIdentity(
        epub_sha256=epub_sha256,
        book_document_substrate_sha256=substrate,
    )
    validate_source_identity(result, book_document=book_document)
    return result


def build_product_unit(
    *,
    unit_id: str,
    sequence_index: int,
    source_range: SourceRange,
    settled_at: datetime | str,
    understanding: str,
    response: str,
    marginalia_candidates: Sequence[MarginaliaCandidate],
    book_document: Mapping[str, object],
) -> UnitBuildResult:
    """Admit one Unit while rejecting bad Marginalia item-by-item."""

    if not isinstance(marginalia_candidates, Sequence) or isinstance(
        marginalia_candidates, (str, bytes, bytearray)
    ):
        raise TypeError("marginalia_candidates must be a sequence")
    if len(marginalia_candidates) > 999:
        raise ReadingProductValidationError(
            "too_many_marginalia", "Unit has more than 999 marginalia candidates"
        )
    base = ProductUnit(
        unit_id=unit_id,
        sequence_index=sequence_index,
        source_range=source_range,
        settled_at=utc_seconds(settled_at),
        understanding=understanding,
        response=response,
        marginalia=(),
    )
    validate_unit(base, book_document=book_document)

    accepted: list[ProductMarginalia] = []
    findings: list[ProductFinding] = []
    semantics: set[tuple[object, ...]] = set()
    for ordinal, candidate in enumerate(marginalia_candidates, start=1):
        marginalia_id = f"{unit_id}-m{ordinal:03d}"
        if not isinstance(candidate, MarginaliaCandidate):
            findings.append(
                _skipped(
                    "invalid_marginalia",
                    "Marginalia candidate was malformed.",
                    unit_id,
                    marginalia_id,
                )
            )
            continue
        if candidate.rejection_code:
            code, message = _SAFE_REJECTION_MESSAGES.get(
                candidate.rejection_code,
                (
                    "producer_rejected_marginalia",
                    "Marginalia candidate failed producer admission.",
                ),
            )
            findings.append(_skipped(code, message, unit_id, marginalia_id))
            continue
        item = ProductMarginalia(
            marginalia_id=marginalia_id,
            kind=candidate.kind,
            source_range=candidate.source_range,
            source_quote=candidate.source_quote,
            body_text=candidate.body_text,
        )
        semantic = (
            item.kind,
            item.source_range,
            item.source_quote,
            item.body_text,
        )
        if semantic in semantics:
            findings.append(
                _skipped(
                    "duplicate_marginalia",
                    "Semantic duplicate Marginalia was skipped.",
                    unit_id,
                    marginalia_id,
                )
            )
            continue
        candidate_unit = ProductUnit(
            unit_id=base.unit_id,
            sequence_index=base.sequence_index,
            source_range=base.source_range,
            settled_at=base.settled_at,
            understanding=base.understanding,
            response=base.response,
            marginalia=(item,),
        )
        try:
            validate_unit(candidate_unit, book_document=book_document)
        except ReadingProductValidationError as exc:
            findings.append(
                _skipped(
                    exc.code,
                    str(exc),
                    unit_id,
                    marginalia_id,
                    json_pointer=exc.json_pointer,
                )
            )
            continue
        semantics.add(semantic)
        accepted.append(item)

    unit = ProductUnit(
        unit_id=base.unit_id,
        sequence_index=base.sequence_index,
        source_range=base.source_range,
        settled_at=base.settled_at,
        understanding=base.understanding,
        response=base.response,
        marginalia=tuple(accepted),
    )
    validate_unit(unit, book_document=book_document)
    return UnitBuildResult(unit=unit, findings=tuple(findings))


def _skipped(
    code: str,
    message: str,
    unit_id: str,
    marginalia_id: str,
    *,
    json_pointer: str | None = None,
) -> ProductFinding:
    safe_code = code if re.fullmatch(r"[a-z][a-z0-9_]{0,79}", code or "") else "invalid_marginalia"
    safe_message = message if 0 < len(message) <= 512 else "Marginalia candidate was skipped."
    return ProductFinding(
        code=safe_code,
        severity="skipped",
        message=safe_message,
        unit_id=unit_id,
        marginalia_id=marginalia_id,
        json_pointer=json_pointer,
    )


__all__ = ["build_product_unit", "build_source_identity", "sha256_file"]
