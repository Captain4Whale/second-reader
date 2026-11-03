#!/usr/bin/env python3
"""Print a chapter pilot's review packet, with coordinates verified against the original EPUB."""

import argparse
from dataclasses import asdict, replace
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.annotation_pack.anchors import AnchorBuilder
from src.annotation_pack.drafts import AnnotationDraft
from src.annotation_pack.identity import PublicationIdentityBuilder
from src.reading_core.source_ranges import (
    SourceRange,
    validate_book_document_source_range,
)
from src.reading_product.serialization import load_document_bytes
from src.reading_product.validation import validate_document


def _original_range(span, chapter_id):
    return SourceRange(
        replace(span.start, chapter_id=chapter_id),
        replace(span.end, chapter_id=chapter_id),
    )


def build_packet(product_path, pilot_dir, original_dir):
    product = load_document_bytes(product_path.read_bytes())
    book_document = Path("public/book_document.json")
    pilot = json.loads((pilot_dir / book_document).read_bytes())
    original = json.loads((original_dir / book_document).read_bytes())
    validate_document(product, book_document=pilot)
    if (
        product.source.epub_sha256
        != sha256((pilot_dir / "_assets/source.epub").read_bytes()).hexdigest()
    ):
        raise ValueError("Pilot EPUB digest differs from Reading Product source")
    (chapter_id,) = {u.source_range.start.chapter_id for u in product.units}
    (chapter,) = [c for c in pilot["chapters"] if c["id"] == chapter_id]
    (source,) = [c for c in original["chapters"] if c["href"] == chapter["href"]]
    if [p["text"] for p in chapter["paragraphs"]] != [
        p["text"] for p in source["paragraphs"]
    ]:
        raise ValueError("Pilot and original chapter paragraphs do not match")
    publication = PublicationIdentityBuilder().build(
        output_dir=original_dir, persisted_book_document=original
    )
    units = []
    for unit in product.units:
        span = _original_range(unit.source_range, source["id"])
        original_text = validate_book_document_source_range(original, span).quote
        marks = []
        for mark in unit.marginalia:
            original_span = _original_range(mark.source_range, source["id"])
            validate_book_document_source_range(
                original, original_span, expected_quote=mark.source_quote, within=span
            )
            draft = AnnotationDraft(
                kind=mark.kind,
                source_range=original_span,
                source_quote=mark.source_quote,
                body_text=mark.body_text,
                created_at=datetime.fromisoformat(unit.settled_at),
                source_record_index=len(marks),
                source_record_digest=sha256(mark.marginalia_id.encode()).hexdigest(),
            )
            anchor = (
                AnchorBuilder().resolve(draft=draft, publication=publication).target
            )
            marks.append(
                {
                    "unit_id": unit.unit_id,
                    "marginalia_id": mark.marginalia_id,
                    "kind": mark.kind,
                    "source_quote": mark.source_quote,
                    "body_text": mark.body_text,
                    "original_source_range": asdict(original_span),
                    "epub_target": dict(anchor.target),
                    "anchor_warnings": [finding.code for finding in anchor.findings],
                }
            )
        units.append(
            {
                "unit_id": unit.unit_id,
                "sequence_index": unit.sequence_index,
                "original_source_range": asdict(span),
                "source_text": original_text,
                "understanding": unit.understanding,
                "response": unit.response,
                "marginalia": marks,
            }
        )
    return {
        "reading_id": product.reading_id,
        "pilot_source": asdict(product.source),
        "original_epub_sha256": publication.file_sha256,
        "original_chapter_id": source["id"],
        "original_href": source["href"],
        "chapter_title": source["title"],
        "units": units,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product", type=Path)
    parser.add_argument("pilot_output", type=Path)
    parser.add_argument("original_output", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            build_packet(args.product, args.pilot_output, args.original_output),
            ensure_ascii=False,
            indent=2,
        )
    )
