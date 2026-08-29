"""Mechanism-neutral Reading Product Output v1 domain records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from src.reading_core.source_ranges import SourceRange


ProductStatus = Literal["partial", "complete"]
MarginaliaKind = Literal["highlight", "note"]
CompletionScope = Literal["whole_book", "chapter", "bounded"]


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    epub_sha256: str
    book_document_substrate_sha256: str


@dataclass(frozen=True, slots=True)
class MarginaliaCandidate:
    """Private admission input; rejection metadata never enters the wire."""

    kind: MarginaliaKind
    source_range: SourceRange
    source_quote: str
    body_text: str | None = None
    rejection_code: str | None = None


@dataclass(frozen=True, slots=True)
class ProductMarginalia:
    marginalia_id: str
    kind: MarginaliaKind
    source_range: SourceRange
    source_quote: str
    body_text: str | None = None


@dataclass(frozen=True, slots=True)
class ProductUnit:
    unit_id: str
    sequence_index: int
    source_range: SourceRange
    settled_at: str
    understanding: str
    response: str
    marginalia: tuple[ProductMarginalia, ...] = ()


@dataclass(frozen=True, slots=True)
class ReadingProductDocument:
    reading_id: str
    status: ProductStatus
    source: SourceIdentity
    started_at: str
    units: tuple[ProductUnit, ...]
    completed_at: str | None = None
    schema_version: str = "reading-product-output/1.0"


@dataclass(frozen=True, slots=True)
class ProductFinding:
    code: str
    severity: Literal["error", "warning", "skipped"]
    message: str
    unit_id: str | None = None
    marginalia_id: str | None = None
    json_pointer: str | None = None


@dataclass(frozen=True, slots=True)
class UnitBuildResult:
    unit: ProductUnit
    findings: tuple[ProductFinding, ...]

    @property
    def rejected_marginalia_count(self) -> int:
        return sum(finding.severity == "skipped" for finding in self.findings)


@dataclass(frozen=True, slots=True)
class CompletionEvidence:
    scope: CompletionScope
    chapter_number: int | None
    scheduled_chapter_ids: tuple[int, ...]
    completed_chapter_ids: tuple[int, ...]
    reading_plan_complete: bool
    audit_window_stop_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CommitResult:
    status: Literal["committed", "unchanged"]
    unit: ProductUnit
    snapshot: ReadingProductDocument
    projection_path: Path


@dataclass(frozen=True, slots=True)
class FinalizeResult:
    status: Literal["published", "unchanged"]
    revision_id: str
    document_path: Path
    report_path: Path
    current_pointer_path: Path


def utc_seconds(value: datetime | str | None = None) -> str:
    """Return the contract's second-precision UTC ``Z`` timestamp."""

    moment: datetime
    if value is None:
        moment = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        moment = value.astimezone(timezone.utc)
    elif isinstance(value, str):
        from .validation import parse_utc_seconds

        parse_utc_seconds(value)
        return value
    else:
        raise TypeError("timestamp must be a datetime, canonical string, or None")
    return moment.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "CommitResult",
    "CompletionEvidence",
    "FinalizeResult",
    "MarginaliaCandidate",
    "MarginaliaKind",
    "ProductFinding",
    "ProductMarginalia",
    "ProductStatus",
    "ProductUnit",
    "ReadingProductDocument",
    "SourceIdentity",
    "UnitBuildResult",
    "utc_seconds",
]
