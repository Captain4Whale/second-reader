from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from src.annotation_pack import exporter as exporter_module
from src.annotation_pack.drafts import ProducerDraftResult
from src.annotation_pack.drafts import ProducerAdapterError
from src.annotation_pack.producers.reading_product import (
    ReadingProductProducerAdapter,
)
from src.attentional_v2.product_compatibility import (
    project_reading_product_compatibility,
)
from src.reading_core import SourceCoordinate, SourceRange
from src.reading_core.canonical_json import canonical_json_bytes
from src.reading_product import (
    CompletionEvidence,
    MarginaliaCandidate,
    ReadingProductStore,
    build_product_unit,
)


EPUB_SHA256 = "a" * 64
READING_ID = "urn:uuid:fe504634-59e4-44f5-9792-c0b1d7c08670"


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Product Consumer Fixture",
            "author": "Second Reader",
            "book_language": "en",
            "output_language": "en",
            "source_file": "_assets/source.epub",
        },
        "chapters": [
            {
                "id": 1,
                "chapter_number": 1,
                "title": "Return",
                "reference": "Chapter 1",
                "href": "Text/return.xhtml",
                "item_id": "return",
                "spine_index": 0,
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "A durable idea is worth returning to.",
                        "href": "Text/return.xhtml",
                        "text_role": "body",
                    },
                    {
                        "paragraph_index": 2,
                        "text": "Return with a better question.",
                        "href": "Text/return.xhtml",
                        "text_role": "body",
                    },
                ],
            }
        ],
    }


def _range(paragraph_index: int, start: int, end: int) -> SourceRange:
    return SourceRange(
        start=SourceCoordinate(1, paragraph_index, start),
        end=SourceCoordinate(1, paragraph_index, end),
    )


def _published_store(output_dir: Path) -> tuple[ReadingProductStore, dict[str, object]]:
    book = _book_document()
    store = ReadingProductStore.create(
        output_dir,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        reading_id=READING_ID,
        started_at=datetime(2026, 8, 29, 1, 0, tzinfo=timezone.utc),
    )
    first = "A durable idea is worth returning to."
    second = "Return with a better question."
    unit_one = build_product_unit(
        unit_id="u000001",
        sequence_index=1,
        source_range=_range(1, 0, len(first)),
        settled_at="2026-08-29T01:01:00Z",
        understanding="The opening treats return as deliberate reading.",
        response="Rereading can test whether an idea remains durable.",
        marginalia_candidates=(
            MarginaliaCandidate(
                kind="highlight",
                source_range=_range(1, 2, 14),
                source_quote=first[2:14],
            ),
        ),
        book_document=book,
    )
    unit_two = build_product_unit(
        unit_id="u000002",
        sequence_index=2,
        source_range=_range(2, 0, len(second)),
        settled_at="2026-08-29T01:02:00Z",
        understanding="The question is part of the act of interpretation.",
        response="A better question changes what rereading can reveal.",
        marginalia_candidates=(
            MarginaliaCandidate(
                kind="note",
                source_range=_range(2, 0, len(second)),
                source_quote=second,
                body_text="This is a test of rereading, not repetition.",
            ),
        ),
        book_document=book,
    )
    store.commit_unit(unit_one, book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(unit_two, book_document=book, epub_sha256=EPUB_SHA256)
    store.finalize(
        book_document=book,
        epub_sha256=EPUB_SHA256,
        completion=CompletionEvidence(
            scope="whole_book",
            chapter_number=None,
            scheduled_chapter_ids=(1,),
            completed_chapter_ids=(1,),
            reading_plan_complete=True,
        ),
        completed_at="2026-08-29T01:03:00Z",
    )
    return store, book


def test_complete_product_adapter_flattens_native_highlight_and_note(
    tmp_path: Path,
) -> None:
    store, _book = _published_store(tmp_path)

    result = ReadingProductProducerAdapter().load_drafts(output_dir=tmp_path)

    assert [draft.kind for draft in result.drafts] == ["highlight", "note"]
    assert result.drafts[0].body_text is None
    assert result.drafts[1].body_text == "This is a test of rereading, not repetition."
    assert result.drafts[0].created_at.isoformat() == "2026-08-29T01:01:00+00:00"
    assert result.source_epub_sha256 == EPUB_SHA256
    assert result.book_document_substrate_sha256 == store.source.book_document_substrate_sha256
    assert result.producer_reading_id == READING_ID
    assert result.input_count == 2
    assert len(set(result.accepted_record_digests)) == 2


def test_product_adapter_rejects_partial_publication_without_legacy_fallback(
    tmp_path: Path,
) -> None:
    _store, _book = _published_store(tmp_path)
    root = tmp_path / "public" / "reading-products"
    old_pointer = json.loads((root / "current.json").read_bytes())
    complete = json.loads((root / str(old_pointer["reading_product"])).read_bytes())
    complete["status"] = "partial"
    complete.pop("completed_at")
    product_bytes = canonical_json_bytes(complete)
    product_digest = hashlib.sha256(product_bytes).hexdigest()
    report = json.loads((root / str(old_pointer["validation_report"])).read_bytes())
    report["reading_product_sha256"] = product_digest
    report_bytes = canonical_json_bytes(report)
    report_digest = hashlib.sha256(report_bytes).hexdigest()
    revision = root / "revisions" / product_digest
    revision.mkdir()
    (revision / "reading-product.json").write_bytes(product_bytes)
    (revision / "validation-report.json").write_bytes(report_bytes)
    pointer = {
        **old_pointer,
        "revision_id": product_digest,
        "reading_product": f"revisions/{product_digest}/reading-product.json",
        "reading_product_sha256": product_digest,
        "validation_report": f"revisions/{product_digest}/validation-report.json",
        "validation_report_sha256": report_digest,
    }
    (root / "current.json").write_bytes(canonical_json_bytes(pointer))

    with pytest.raises(ProducerAdapterError) as caught:
        ReadingProductProducerAdapter().load_drafts(output_dir=tmp_path)

    assert caught.value.code == "reading_product_not_complete"


def test_product_adapter_rejects_symlinked_public_pointer(tmp_path: Path) -> None:
    _published_store(tmp_path)
    pointer = tmp_path / "public" / "reading-products" / "current.json"
    real_pointer = pointer.with_name("saved-pointer.json")
    pointer.rename(real_pointer)
    pointer.symlink_to(real_pointer.name)

    with pytest.raises(ProducerAdapterError) as caught:
        ReadingProductProducerAdapter().load_drafts(output_dir=tmp_path)

    assert caught.value.code == "reading_product_unavailable"


def test_default_export_boundary_requires_product_source_identity() -> None:
    snapshot = ProducerDraftResult(
        drafts=(),
        reaction_ledger_sha256="b" * 64,
        accepted_record_digests=(),
        findings=(),
        input_count=0,
    )

    with pytest.raises(exporter_module._ExportFailure) as caught:
        exporter_module._require_producer_source_identity(
            producer_snapshot=snapshot,
            source_epub_sha256=EPUB_SHA256,
            substrate_sha256="c" * 64,
            required=True,
        )

    assert caught.value.code == "reading_product_source_mismatch"


def test_product_compatibility_does_not_read_private_runtime_artifacts(
    tmp_path: Path,
) -> None:
    store, book = _published_store(tmp_path)
    private = tmp_path / "_mechanisms" / "attentional_v2" / "runtime"
    private.mkdir(parents=True)
    for name in ("reaction_records.json", "read_audit.json", "unit_memory.json"):
        (private / name).write_text("private-invalid-json", encoding="utf-8")

    payloads = project_reading_product_compatibility(
        reading_product=store.snapshot(book_document=book),
        book_document=book,
        book_id="product-consumer-fixture",
        output_language="en",
        output_dir=tmp_path,
        persist=True,
    )

    chapter = payloads[1]
    assert chapter["visible_marginalia_count"] == 2
    assert [item["type"] for item in chapter["featured_marginalia"]] == [
        "highlight",
        "association",
    ]
    assert chapter["featured_marginalia"][0]["reaction_id"] == "u000001-m001"
    assert chapter["featured_marginalia"][1]["reaction_id"] == "u000002-m001"
    assert chapter["featured_marginalia"][1]["content"] == (
        "This is a test of rereading, not repetition."
    )
    compatibility_path = (
        tmp_path
        / "_mechanisms"
        / "attentional_v2"
        / "derived"
        / "chapter_result_compatibility"
        / "chapter-001.json"
    )
    persisted = json.loads(compatibility_path.read_text(encoding="utf-8"))
    assert persisted["visible_reaction_count"] == 2
