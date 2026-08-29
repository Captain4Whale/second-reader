"""Producer-neutral Annotation Pack draft and anchor domain types.

These immutable records form the boundary between mechanism-specific adapters
and the generic publication pipeline.  They intentionally contain no runtime
paths, prompt state, or mechanism-private reaction objects.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from src.reading_core.source_ranges import SourceCoordinate, SourceRange


FindingSeverity = Literal["fatal", "error", "warning", "skipped"]
AnnotationKind = Literal["highlight", "note"]


@dataclass(frozen=True, slots=True)
class AnnotationDraft:
    """One producer-neutral Highlight or Note candidate.

    Mechanism adapters own the kind, exact shared-source range/quote, and
    conditional Note body. Runtime settlement owns ``created_at``. Record
    index/digest fields are private export controls, never public Pack data.
    """

    kind: AnnotationKind
    source_range: SourceRange
    source_quote: str
    body_text: str | None
    created_at: datetime
    source_record_index: int
    source_record_digest: str


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One sanitized machine-readable validation or resolution finding."""

    code: str
    severity: FindingSeverity
    message: str
    source_record_index: int | None = None
    json_pointer: str | None = None
    annotation_id: str | None = None
    source_record_digest: str | None = None


class ProducerAdapterError(ValueError):
    """One sanitized, pack-level producer snapshot failure."""

    __slots__ = ("code", "finding")

    def __init__(self, code: str) -> None:
        if type(code) is not str:
            raise TypeError("producer adapter errors require one safe fatal code")
        # Local import avoids the module cycle: validation owns the message
        # catalog, while ValidationFinding's neutral shape lives here.
        from src.annotation_pack.validation import make_validation_finding

        finding = make_validation_finding(code, "fatal")
        self.code = finding.code
        self.finding = finding
        super().__init__(finding.message)


@dataclass(frozen=True, slots=True)
class ProducerDraftResult:
    """Neutral drafts and exact controls from one stable producer snapshot.

    ``reaction_ledger_sha256`` retains its historical constructor spelling so
    the explicit phase9 legacy adapter remains source-compatible.  New code
    must use ``producer_snapshot_sha256``; for Reading Product v1 the stored
    digest is the canonical complete-product digest selected by its public
    pointer, not a private reaction-ledger digest.
    """

    drafts: tuple[AnnotationDraft, ...]
    reaction_ledger_sha256: str
    accepted_record_digests: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]
    input_count: int
    source_epub_sha256: str | None = None
    book_document_substrate_sha256: str | None = None
    producer_reading_id: str | None = None

    @property
    def producer_snapshot_sha256(self) -> str:
        return self.reaction_ledger_sha256


@dataclass(frozen=True, slots=True)
class ResolvedAnchor:
    """A canonical, exact-source-backed annotation target."""

    href: str
    exact: str
    start: int
    end: int
    target: Mapping[str, Any]
    findings: tuple[ValidationFinding, ...]


@dataclass(frozen=True, slots=True)
class ResolvedAnnotationDraft:
    """A neutral draft whose source range has passed strict anchor resolution."""

    kind: AnnotationKind
    body_text: str | None
    created_at: datetime
    target: ResolvedAnchor
    source_record_index: int
    source_record_digest: str


__all__ = [
    "AnnotationDraft",
    "AnnotationKind",
    "FindingSeverity",
    "ProducerAdapterError",
    "ProducerDraftResult",
    "ResolvedAnchor",
    "ResolvedAnnotationDraft",
    "SourceCoordinate",
    "SourceRange",
    "ValidationFinding",
]
