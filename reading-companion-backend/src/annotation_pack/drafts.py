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


FindingSeverity = Literal["fatal", "error", "warning", "skipped"]
AnnotationKind = Literal["highlight", "note"]


@dataclass(frozen=True, slots=True)
class SourceCoordinate:
    """One end-exclusive paragraph-local Unicode code-point coordinate."""

    chapter_id: int
    paragraph_index: int
    char_offset: int


@dataclass(frozen=True, slots=True)
class SourceRange:
    """A start/end pair in the canonical BookDocument coordinate system."""

    start: SourceCoordinate
    end: SourceCoordinate


@dataclass(frozen=True, slots=True)
class AnnotationDraft:
    """One producer-neutral Highlight or Note candidate."""

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


@dataclass(frozen=True, slots=True)
class ResolvedAnchor:
    """A canonical, exact-source-backed annotation target."""

    anchor_id: str
    href: str
    exact: str
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
    "ResolvedAnchor",
    "ResolvedAnnotationDraft",
    "SourceCoordinate",
    "SourceRange",
    "ValidationFinding",
]
