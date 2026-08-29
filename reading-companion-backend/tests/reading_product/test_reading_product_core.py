from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from threading import Thread

from jsonschema import Draft202012Validator, FormatChecker
import pytest

from src.reading_core import SourceCoordinate, SourceRange
from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_product import (
    CompletionEvidence,
    MarginaliaCandidate,
    ProductUnit,
    ReadingProductStore,
    ReadingProductValidationError,
    build_product_unit,
    build_source_identity,
)
from src.reading_product.store import (
    ReadingProductProjectionError,
    ReadingProductStoreError,
)


EPUB_SHA256 = "a" * 64
STARTED_AT = datetime(2026, 8, 29, 1, 0, tzinfo=timezone.utc)


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Fixture",
            "author": "Reader",
            "book_language": "en",
            "output_language": "en",
            "source_file": "source.epub",
        },
        "chapters": [
            {
                "id": 1,
                "chapter_number": 1,
                "title": "One",
                "href": "Text/one.xhtml",
                "item_id": "one",
                "spine_index": 0,
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "First idea.",
                        "href": "Text/one.xhtml",
                        "text_role": "body",
                    },
                    {
                        "paragraph_index": 2,
                        "text": "Return with a better question.",
                        "href": "Text/one.xhtml",
                        "text_role": "body",
                    },
                ],
            },
            {
                "id": 2,
                "chapter_number": 2,
                "title": "Two",
                "href": "Text/two.xhtml",
                "item_id": "two",
                "spine_index": 1,
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Second idea.",
                        "href": "Text/two.xhtml",
                        "text_role": "body",
                    }
                ],
            },
        ],
    }


def _range(
    chapter_id: int,
    paragraph_index: int,
    start: int,
    end: int,
) -> SourceRange:
    return SourceRange(
        SourceCoordinate(chapter_id, paragraph_index, start),
        SourceCoordinate(chapter_id, paragraph_index, end),
    )


def _unit_one(book: dict[str, object]):
    quote = "Return with a better question."
    return build_product_unit(
        unit_id="u000001",
        sequence_index=1,
        source_range=SourceRange(
            SourceCoordinate(1, 1, 0),
            SourceCoordinate(1, 2, len(quote)),
        ),
        settled_at=datetime(2026, 8, 29, 1, 1, tzinfo=timezone.utc),
        understanding="The text treats return as deliberate reading.",
        response="A changed question can change the relation to the same words.",
        marginalia_candidates=(
            MarginaliaCandidate(
                kind="highlight",
                source_range=_range(1, 1, 0, len("First idea.")),
                source_quote="First idea.",
            ),
            MarginaliaCandidate(
                kind="highlight",
                source_range=_range(1, 2, 0, len(quote)),
                source_quote=quote,
                rejection_code="ambiguous_first_match",
            ),
            MarginaliaCandidate(
                kind="note",
                source_range=_range(1, 2, 0, len(quote)),
                source_quote=quote,
                body_text="This is a test of rereading, not repetition.",
            ),
        ),
        book_document=book,
    )


def _unit_two(book: dict[str, object]):
    quote = "Second idea."
    return build_product_unit(
        unit_id="u000002",
        sequence_index=2,
        source_range=_range(2, 1, 0, len(quote)),
        settled_at="2026-08-29T01:02:00Z",
        understanding="The second chapter advances the test.",
        response="The response remains grounded in a distinct source range.",
        marginalia_candidates=(),
        book_document=book,
    )


def _completion() -> CompletionEvidence:
    return CompletionEvidence(
        scope="whole_book",
        chapter_number=None,
        scheduled_chapter_ids=(1, 2),
        completed_chapter_ids=(1, 2),
        reading_plan_complete=True,
    )


def test_source_identity_uses_shared_frozen_substrate_digest() -> None:
    book = _book_document()
    identity = build_source_identity(EPUB_SHA256, book)

    assert identity.epub_sha256 == EPUB_SHA256
    assert identity.book_document_substrate_sha256 == book_document_substrate_digest(book)


def test_builder_rejects_bad_marginalia_only_and_preserves_candidate_ordinals() -> None:
    result = _unit_one(_book_document())

    assert [item.marginalia_id for item in result.unit.marginalia] == [
        "u000001-m001",
        "u000001-m003",
    ]
    assert result.unit.marginalia[0].body_text is None
    assert result.unit.marginalia[1].body_text
    assert result.rejected_marginalia_count == 1
    assert result.findings[0].code == "ambiguous_source_quote"


def test_builder_rejects_empty_core_semantics_but_skips_quote_mismatch() -> None:
    book = _book_document()
    with pytest.raises(ReadingProductValidationError, match="understanding"):
        build_product_unit(
            unit_id="u000001",
            sequence_index=1,
            source_range=_range(1, 1, 0, 5),
            settled_at=STARTED_AT,
            understanding=" ",
            response="response",
            marginalia_candidates=(),
            book_document=book,
        )

    result = build_product_unit(
        unit_id="u000001",
        sequence_index=1,
        source_range=_range(1, 1, 0, len("First idea.")),
        settled_at=STARTED_AT,
        understanding="understanding",
        response="response",
        marginalia_candidates=(
            MarginaliaCandidate(
                kind="highlight",
                source_range=_range(1, 1, 0, 5),
                source_quote="wrong",
            ),
        ),
        book_document=book,
    )
    assert result.unit.marginalia == ()
    assert result.findings[0].code == "unresolved_source_quote"


def test_store_commit_is_atomic_idempotent_and_finding_sensitive(tmp_path: Path) -> None:
    book = _book_document()
    built = _unit_one(book)
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )

    committed = store.commit_unit(built, book_document=book, epub_sha256=EPUB_SHA256)
    unchanged = store.commit_unit(built, book_document=book, epub_sha256=EPUB_SHA256)

    assert committed.status == "committed"
    assert unchanged.status == "unchanged"
    assert store.next_sequence_index() == 2
    assert store.latest_unit() == built.unit
    assert store.load_units() == (built.unit,)
    assert json.loads(store.partial_snapshot_path.read_bytes())["status"] == "partial"
    assert store.partial_snapshot_path.read_bytes().endswith(b"\n")

    with pytest.raises(ReadingProductStoreError) as raised:
        store.commit_unit(built.unit, book_document=book, epub_sha256=EPUB_SHA256)
    assert raised.value.code == "unit_commit_conflict"


def test_committed_ledger_survives_projection_failure_and_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import src.reading_product.store as store_module

    book = _book_document()
    built = _unit_one(book)
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    original = store_module._atomic_replace
    monkeypatch.setattr(
        store_module,
        "_atomic_replace",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("crash")),
    )
    with pytest.raises(ReadingProductProjectionError) as raised:
        store.commit_unit(built, book_document=book, epub_sha256=EPUB_SHA256)
    assert raised.value.committed is True
    assert store.latest_unit() == built.unit

    monkeypatch.setattr(store_module, "_atomic_replace", original)
    recovered = ReadingProductStore.open(tmp_path, store.reading_id)
    assert recovered.commit_unit(
        built, book_document=book, epub_sha256=EPUB_SHA256
    ).status == "unchanged"
    assert json.loads(recovered.partial_snapshot_path.read_bytes())["units"]


def test_store_rejects_sequence_gap_source_mutation_and_post_seal_write(
    tmp_path: Path,
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    second = _unit_two(book)
    with pytest.raises(ReadingProductStoreError) as gap:
        store.commit_unit(second, book_document=book, epub_sha256=EPUB_SHA256)
    assert gap.value.code == "unit_sequence_gap"

    mutated = _book_document()
    mutated["chapters"][0]["paragraphs"][0]["text"] = "Changed."  # type: ignore[index]
    with pytest.raises(ReadingProductValidationError) as mismatch:
        store.commit_unit(
            _unit_one(book), book_document=mutated, epub_sha256=EPUB_SHA256
        )
    assert mismatch.value.code == "source_identity_mismatch"


def test_finalize_publishes_schema_valid_immutable_revision_and_pointer(
    tmp_path: Path,
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(_unit_two(book), book_document=book, epub_sha256=EPUB_SHA256)

    result = store.finalize(
        book_document=book,
        epub_sha256=EPUB_SHA256,
        completion=_completion(),
        completed_at="2026-08-29T01:03:00Z",
    )
    unchanged = store.finalize(
        book_document=book,
        epub_sha256=EPUB_SHA256,
        completion=_completion(),
        completed_at="2026-08-29T01:03:00Z",
    )

    assert result.status == "published"
    assert unchanged.status == "unchanged"
    content = result.document_path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == result.revision_id
    wire = json.loads(content)
    schema = json.loads(
        (
            Path(__file__).parents[3]
            / "contract/reading-product/v1/schema/reading-product-output.schema.json"
        ).read_bytes()
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(wire)
    pointer = json.loads(result.current_pointer_path.read_bytes())
    report = json.loads(result.report_path.read_bytes())
    assert pointer["revision_id"] == result.revision_id
    assert report["counts"] == {
        "errors": 0,
        "marginalia": 2,
        "rejected_marginalia": 1,
        "units": 2,
    }
    assert report["findings"][0]["code"] == "ambiguous_source_quote"
    assert store.snapshot(book_document=book).status == "complete"
    with pytest.raises(ReadingProductStoreError) as sealed:
        store.commit_unit(
            _unit_two(book), book_document=book, epub_sha256=EPUB_SHA256
        )
    assert sealed.value.code == "reading_revision_sealed"


@pytest.mark.parametrize(
    "evidence,code",
    [
        (
            CompletionEvidence(
                scope="chapter",
                chapter_number=1,
                scheduled_chapter_ids=(1, 2),
                completed_chapter_ids=(1, 2),
                reading_plan_complete=True,
            ),
            "incomplete_reading_scope",
        ),
        (
            CompletionEvidence(
                scope="whole_book",
                chapter_number=None,
                scheduled_chapter_ids=(1, 2),
                completed_chapter_ids=(1,),
                reading_plan_complete=True,
            ),
            "scheduled_chapters_incomplete",
        ),
        (
            CompletionEvidence(
                scope="whole_book",
                chapter_number=None,
                scheduled_chapter_ids=(1, 2),
                completed_chapter_ids=(1, 2),
                reading_plan_complete=True,
                audit_window_stop_reason="cap",
            ),
            "audit_window_stopped",
        ),
    ],
)
def test_finalize_fails_closed_without_whole_book_evidence(
    tmp_path: Path, evidence: CompletionEvidence, code: str
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(_unit_two(book), book_document=book, epub_sha256=EPUB_SHA256)
    with pytest.raises(ReadingProductValidationError) as raised:
        store.finalize(
            book_document=book,
            epub_sha256=EPUB_SHA256,
            completion=evidence,
        )
    assert raised.value.code == code
    assert not (tmp_path / "public/reading-products/current.json").exists()


def test_concurrent_duplicate_commit_has_one_commit_and_one_unchanged(
    tmp_path: Path,
) -> None:
    book = _book_document()
    built = _unit_one(book)
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    statuses: list[str] = []
    errors: list[BaseException] = []

    def commit() -> None:
        try:
            statuses.append(
                store.commit_unit(
                    built, book_document=book, epub_sha256=EPUB_SHA256
                ).status
            )
        except BaseException as exc:  # pragma: no cover - assertion reports it
            errors.append(exc)

    threads = [Thread(target=commit), Thread(target=commit)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert sorted(statuses) == ["committed", "unchanged"]
    assert len(store.load_units()) == 1


def test_sealing_state_recovers_idempotently_after_publication_crash(
    tmp_path: Path,
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(_unit_two(book), book_document=book, epub_sha256=EPUB_SHA256)
    with sqlite3.connect(store.ledger_path) as connection:
        connection.execute("UPDATE metadata SET value='sealing' WHERE key='status'")
        connection.execute(
            "INSERT INTO metadata(key,value) VALUES "
            "('sealing_completed_at','2026-08-29T01:03:00Z')"
        )

    recovered = ReadingProductStore.open(tmp_path, store.reading_id)
    result = recovered.finalize(
        book_document=book,
        epub_sha256=EPUB_SHA256,
        completion=_completion(),
        completed_at="2026-08-29T01:03:00Z",
    )
    assert result.status == "published"
    assert recovered.snapshot(book_document=book).status == "complete"


def test_store_detects_digest_and_noncanonical_json_corruption(tmp_path: Path) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    with sqlite3.connect(store.ledger_path) as connection:
        connection.execute(
            "UPDATE units SET canonical_sha256 = ? WHERE sequence_index = 1",
            ("b" * 64,),
        )
    with pytest.raises(ReadingProductStoreError) as digest_error:
        store.load_units()
    assert digest_error.value.code == "reading_revision_corrupt"

    content = b'{"unit_id":"u000001","unit_id":"u000001"}\n'
    with sqlite3.connect(store.ledger_path) as connection:
        connection.execute(
            "UPDATE units SET canonical_json = ?, canonical_sha256 = ? "
            "WHERE sequence_index = 1",
            (content, hashlib.sha256(content).hexdigest()),
        )
    with pytest.raises(ReadingProductStoreError) as duplicate_key:
        store.load_units()
    assert duplicate_key.value.code == "reading_revision_corrupt"


@pytest.mark.parametrize("target", ["report", "pointer"])
def test_finalized_companion_tamper_is_detected(tmp_path: Path, target: str) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(_unit_two(book), book_document=book, epub_sha256=EPUB_SHA256)
    result = store.finalize(
        book_document=book,
        epub_sha256=EPUB_SHA256,
        completion=_completion(),
        completed_at="2026-08-29T01:03:00Z",
    )
    path = result.report_path if target == "report" else result.current_pointer_path
    original = path.read_bytes()
    path.write_bytes(
        original.replace(b'"valid"', b'"failed"', 1)
        if target == "report"
        else original.replace(
            b'"reading-product-publication-pointer/1.0"',
            b'"reading-product-publication-pointer/9.0"',
            1,
        )
    )

    with pytest.raises(ReadingProductStoreError):
        store.finalize(
            book_document=book,
            epub_sha256=EPUB_SHA256,
            completion=_completion(),
            completed_at="2026-08-29T01:03:00Z",
        )


def test_current_epub_hash_is_required_for_commit_and_finalize(tmp_path: Path) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    with pytest.raises(ReadingProductValidationError) as commit_mismatch:
        store.commit_unit(_unit_one(book), book_document=book, epub_sha256="b" * 64)
    assert commit_mismatch.value.code == "source_identity_mismatch"

    store.commit_unit(_unit_one(book), book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(_unit_two(book), book_document=book, epub_sha256=EPUB_SHA256)
    with pytest.raises(ReadingProductValidationError) as final_mismatch:
        store.finalize(
            book_document=book,
            epub_sha256="b" * 64,
            completion=_completion(),
        )
    assert final_mismatch.value.code == "source_identity_mismatch"


def test_reading_plan_order_may_cross_chapters_but_ranges_must_not_intersect(
    tmp_path: Path,
) -> None:
    book = _book_document()
    chapter_two = build_product_unit(
        unit_id="u000001",
        sequence_index=1,
        source_range=_range(2, 1, 0, len("Second idea.")),
        settled_at="2026-08-29T01:01:00Z",
        understanding="Main body comes first in the approved plan.",
        response="The plan order is product-significant.",
        marginalia_candidates=(),
        book_document=book,
    )
    deferred_preface = build_product_unit(
        unit_id="u000002",
        sequence_index=2,
        source_range=_range(1, 1, 0, len("First idea.")),
        settled_at="2026-08-29T01:02:00Z",
        understanding="The preface is read later as a deferred target.",
        response="Its source is disjoint even though chapter order regresses.",
        marginalia_candidates=(),
        book_document=book,
    )
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at=STARTED_AT,
    )
    store.commit_unit(chapter_two, book_document=book, epub_sha256=EPUB_SHA256)
    store.commit_unit(deferred_preface, book_document=book, epub_sha256=EPUB_SHA256)
    assert [unit.source_range.start.chapter_id for unit in store.load_units()] == [2, 1]

    overlapping = ProductUnit(
        unit_id="u000003",
        sequence_index=3,
        source_range=_range(1, 1, 2, 8),
        settled_at="2026-08-29T01:03:00Z",
        understanding="This overlaps a prior source range.",
        response="It must be rejected despite a fresh Unit id.",
        marginalia=(),
    )
    with pytest.raises(ReadingProductValidationError) as overlap:
        store.commit_unit(overlapping, book_document=book, epub_sha256=EPUB_SHA256)
    assert overlap.value.code == "unit_range_overlap"
