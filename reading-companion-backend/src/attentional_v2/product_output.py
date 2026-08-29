"""Private adapter from attentional_v2 settlement into Reading Product v1."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Mapping, Sequence, cast

from src.reading_core import SourceCoordinate, SourceRange
from src.reading_product import (
    MarginaliaCandidate,
    ProductFinding,
    ProductUnit,
    ReadingProductStore,
    UnitBuildResult,
    build_product_unit,
)
from src.reading_product.models import MarginaliaKind

from .schemas import DigestResult
from .source_spans import source_ref_from_unit


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def source_range_from_mechanism_span(source_span: Mapping[str, object]) -> SourceRange:
    """Convert the private cursor spelling into the neutral product coordinate."""

    start = source_span.get("start_cursor")
    end = source_span.get("end_cursor")
    if not isinstance(start, Mapping) or not isinstance(end, Mapping):
        raise ValueError("source span must contain start_cursor and end_cursor")

    def coordinate(value: Mapping[str, object]) -> SourceCoordinate:
        return SourceCoordinate(
            chapter_id=int(value.get("chapter_id", 0) or 0),
            paragraph_index=int(value.get("paragraph_index", 0) or 0),
            char_offset=int(value.get("char_offset", 0) or 0),
        )

    return SourceRange(start=coordinate(start), end=coordinate(end))


def mechanism_span_from_source_range(
    source_range: SourceRange,
    *,
    chapter_ref: str,
) -> dict[str, object]:
    """Convert one neutral product range back into the private cursor spelling."""

    def cursor(value: SourceCoordinate) -> dict[str, object]:
        return {
            "chapter_id": value.chapter_id,
            "chapter_ref": chapter_ref,
            "paragraph_index": value.paragraph_index,
            "char_offset": value.char_offset,
        }

    return {
        "start_cursor": cursor(source_range.start),
        "end_cursor": cursor(source_range.end),
    }


def _candidate_from_marginalia(
    item: Mapping[str, object],
    *,
    source_unit: Mapping[str, object],
) -> MarginaliaCandidate:
    raw_quote = item.get("source_quote") or item.get("anchor_quote") or ""
    source_quote = str(raw_quote)
    source_ref = source_ref_from_unit(source_unit, quote=source_quote, role="reaction_anchor")
    resolved_span = source_ref.get("source_span")
    source_span = dict(resolved_span) if isinstance(resolved_span, Mapping) else {}
    resolution = source_ref.get("resolution")
    resolution_map = resolution if isinstance(resolution, Mapping) else {}
    resolution_status = _clean_text(resolution_map.get("status"))
    resolution_method = _clean_text(resolution_map.get("method"))
    rejection_code: str | None = None
    if resolution_status == "ambiguous_first_match":
        rejection_code = "ambiguous_source_quote"
    elif resolution_status != "matched" or resolution_method != "exact_text":
        rejection_code = "unresolved_source_quote"

    unit_span_value = source_unit.get("source_span")
    unit_span = dict(unit_span_value) if isinstance(unit_span_value, Mapping) else {}
    candidate_span = unit_span if rejection_code else source_span
    try:
        candidate_range = source_range_from_mechanism_span(candidate_span)
    except (TypeError, ValueError):
        rejection_code = rejection_code or "unresolved_source_quote"
        candidate_range = source_range_from_mechanism_span(unit_span)

    kind = _clean_text(item.get("kind")).lower()
    return MarginaliaCandidate(
        kind=cast(MarginaliaKind, kind),  # runtime validation owns the literal check
        source_range=candidate_range,
        source_quote=source_quote,
        body_text=_clean_text(item.get("content")) or None,
        rejection_code=rejection_code,
    )


def _settled_at_for_attempt(
    store: ReadingProductStore,
    *,
    source_range: SourceRange,
) -> tuple[str, int, str]:
    """Return an id/time tuple that makes an immediate post-commit retry idempotent."""

    latest = store.latest_unit()
    if latest is not None and latest.source_range == source_range:
        return latest.unit_id, latest.sequence_index, latest.settled_at
    sequence_index = store.next_sequence_index()
    return f"u{sequence_index:06d}", sequence_index, datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def build_and_commit_product_unit(
    *,
    store: ReadingProductStore,
    source_unit: Mapping[str, object],
    digest_result: DigestResult,
    book_document: Mapping[str, object],
    epub_sha256: str,
) -> tuple[ProductUnit, tuple[ProductFinding, ...], str]:
    """Build and atomically commit one accepted Product Unit before private projections."""

    raw_span = source_unit.get("source_span")
    if not isinstance(raw_span, Mapping):
        raise ValueError("selected source unit has no source span")
    source_range = source_range_from_mechanism_span(raw_span)
    unit_id, sequence_index, settled_at = _settled_at_for_attempt(store, source_range=source_range)
    marginalia = digest_result.get("marginalia", digest_result.get("surfaced_reactions", []))
    candidates = tuple(
        _candidate_from_marginalia(item, source_unit=source_unit)
        for item in (marginalia if isinstance(marginalia, Sequence) else [])
        if isinstance(item, Mapping)
    )
    build_result: UnitBuildResult = build_product_unit(
        unit_id=unit_id,
        sequence_index=sequence_index,
        source_range=source_range,
        settled_at=settled_at,
        understanding=_clean_text(digest_result.get("understanding")),
        response=_clean_text(digest_result.get("reading_impression")),
        marginalia_candidates=candidates,
        book_document=book_document,
    )
    commit = store.commit_unit(
        build_result,
        book_document=book_document,
        epub_sha256=epub_sha256,
    )
    return commit.unit, build_result.findings, commit.status


def digest_result_for_committed_unit(
    digest_result: DigestResult,
    unit: ProductUnit,
) -> DigestResult:
    """Keep private memory ops while restricting visible reactions to admitted product items."""

    marginalia = [
        {
            "kind": item.kind,
            "source_quote": item.source_quote,
            "content": item.body_text or "",
            "marginalia_id": item.marginalia_id,
            "settled_at": unit.settled_at,
        }
        for item in unit.marginalia
    ]
    return {
        **digest_result,
        "marginalia": marginalia,
        "surfaced_reactions": marginalia,
    }


def product_finding_rows(findings: Sequence[ProductFinding]) -> list[dict[str, object]]:
    """Return audit-only JSON rows for rejected product candidates."""

    return [
        {key: value for key, value in asdict(finding).items() if value is not None}
        for finding in findings
    ]
