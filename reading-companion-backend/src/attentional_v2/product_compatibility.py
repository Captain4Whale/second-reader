"""Legacy chapter/UI projection derived only from Reading Product facts.

This module is intentionally a compatibility consumer.  It is the sole place
where a product ``note`` is presented as the older UI ``association`` family;
the Reading Product and Annotation Pack contracts keep the native Note kind.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from src.reading_product.models import ReadingProductDocument
from src.reading_product.validation import validate_document

from .product_output import mechanism_span_from_source_range
from .slow_cycle import (
    build_reaction_record_from_surfaced_reaction,
    project_chapter_result_compatibility,
)
from .source_spans import source_ref_from_span


def project_reading_product_compatibility(
    *,
    reading_product: ReadingProductDocument,
    book_document: Mapping[str, object],
    book_id: str,
    output_language: str,
    output_dir: Path | None = None,
    persist: bool = False,
    chapter_ids: Sequence[int] | None = None,
) -> dict[int, dict[str, object]]:
    """Build current chapter-result payloads without private runtime ledgers."""

    validate_document(reading_product, book_document=book_document)
    all_chapters = {
        int(chapter.get("id", 0) or 0): dict(chapter)
        for chapter in book_document.get("chapters", [])
        if isinstance(chapter, Mapping) and int(chapter.get("id", 0) or 0) > 0
    }
    selected_ids = (
        set(all_chapters)
        if chapter_ids is None
        else {int(chapter_id) for chapter_id in chapter_ids}
    )
    if not selected_ids.issubset(all_chapters):
        raise ValueError("compatibility projection requested an unknown chapter")
    chapters = {
        chapter_id: all_chapters[chapter_id] for chapter_id in selected_ids
    }
    records_by_chapter: dict[int, list[dict[str, object]]] = {
        chapter_id: [] for chapter_id in chapters
    }
    for unit in reading_product.units:
        for item in unit.marginalia:
            chapter_id = item.source_range.start.chapter_id
            if chapter_id not in selected_ids:
                continue
            chapter = all_chapters[chapter_id]
            chapter_ref = str(
                chapter.get("reference")
                or chapter.get("chapter_ref")
                or chapter.get("title")
                or f"Chapter {chapter_id}"
            ).strip()
            source_span = mechanism_span_from_source_range(
                item.source_range,
                chapter_ref=chapter_ref,
            )
            source_ref = source_ref_from_span(
                source_span,
                quote=item.source_quote,
                role="reaction_anchor",
                resolution={
                    "status": "matched",
                    "method": "exact_product_range",
                    "match_count": 1,
                },
            )
            record = build_reaction_record_from_surfaced_reaction(
                reaction={
                    "kind": item.kind,
                    "source_quote": item.source_quote,
                    "content": item.body_text or "",
                },
                primary_source_ref=source_ref,
                chapter_id=chapter_id,
                chapter_ref=chapter_ref,
                emitted_at_source_span_id=str(
                    source_ref.get("source_span_id", "")
                ),
                reaction_id=item.marginalia_id,
                compatibility_section_ref=(
                    f"{chapter_id}.{item.source_range.start.paragraph_index}"
                ),
                created_at=unit.settled_at,
            )
            if record is None:  # Product validation makes this unreachable.
                raise ValueError("Reading Product marginalia could not be projected")
            records_by_chapter[chapter_id].append(dict(record))

    if persist and output_dir is None:
        raise ValueError("persist=True requires output_dir")
    return {
        chapter_id: project_chapter_result_compatibility(
            book_id=book_id,
            chapter=chapter,
            reaction_records=records_by_chapter[chapter_id],
            output_language=output_language,
            output_dir=output_dir,
            persist=persist,
        )
        for chapter_id, chapter in sorted(chapters.items())
    }


__all__ = ["project_reading_product_compatibility"]
