from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.attentional_v2 import runner as runner_module
from src.attentional_v2.product_output import build_and_commit_product_unit
from src.attentional_v2.resume import resume_from_checkpoint, write_full_checkpoint
from src.attentional_v2.source_spans import source_span_id, source_unit_from_span
from src.attentional_v2.storage import (
    initialize_artifact_tree,
    reaction_records_file,
    unit_span_ledger_file,
)
from src.reading_product import ReadingProductStore, ReadingProductValidationError
from src.reading_runtime.provisioning import ProvisionedBook
from src.reading_runtime.artifacts import runtime_shell_file
from src.reading_runtime.shell_state import load_runtime_shell, save_runtime_shell


EPUB_SHA256 = "a" * 64
PARAGRAPH_TEXT = "echo echo unique note"


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Runtime Fixture",
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
                "reference": "Chapter 1",
                "href": "Text/one.xhtml",
                "item_id": "one",
                "spine_index": 0,
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": PARAGRAPH_TEXT,
                        "href": "Text/one.xhtml",
                        "text_role": "body",
                    }
                ],
            }
        ],
    }


def _source_span() -> dict[str, object]:
    return {
        "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Chapter 1",
            "paragraph_index": 1,
            "char_offset": 0,
        },
        "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Chapter 1",
            "paragraph_index": 1,
            "char_offset": len(PARAGRAPH_TEXT),
        },
    }


def _source_unit(book_document: dict[str, object]) -> dict[str, object]:
    chapter = book_document["chapters"][0]  # type: ignore[index]
    return source_unit_from_span(chapter=chapter, source_span=_source_span())  # type: ignore[arg-type]


def _digest() -> dict[str, object]:
    return {
        "understanding": "Repeated language gives way to one distinct claim.",
        "reading_impression": "The unique phrase becomes the useful margin.",
        "marginalia": [
            {"kind": "highlight", "source_quote": "echo"},
            {"kind": "highlight", "source_quote": "absent"},
            {"kind": "highlight", "source_quote": " unique "},
            {
                "kind": "note",
                "source_quote": "note",
                "content": "Keep the note grounded in its exact word.",
            },
        ],
    }


def test_product_adapter_skips_bad_marginalia_without_blocking_unit(
    tmp_path: Path,
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at="2026-08-29T01:00:00Z",
    )

    unit, findings, status = build_and_commit_product_unit(
        store=store,
        source_unit=_source_unit(book),
        digest_result=_digest(),  # type: ignore[arg-type]
        book_document=book,
        epub_sha256=EPUB_SHA256,
    )

    assert status == "committed"
    assert [finding.code for finding in findings] == [
        "ambiguous_source_quote",
        "unresolved_source_quote",
    ]
    assert [item.marginalia_id for item in unit.marginalia] == [
        "u000001-m003",
        "u000001-m004",
    ]
    assert unit.marginalia[0].source_quote == " unique "
    assert PARAGRAPH_TEXT[
        unit.marginalia[0].source_range.start.char_offset :
        unit.marginalia[0].source_range.end.char_offset
    ] == " unique "

    retried, retry_findings, retry_status = build_and_commit_product_unit(
        store=store,
        source_unit=_source_unit(book),
        digest_result=_digest(),  # type: ignore[arg-type]
        book_document=book,
        epub_sha256=EPUB_SHA256,
    )
    assert retry_status == "unchanged"
    assert retried == unit
    assert retry_findings == findings
    assert store.load_units() == (unit,)


@pytest.mark.parametrize(
    "understanding,response",
    [("", "response"), ("understanding", "")],
)
def test_product_adapter_rejects_empty_core_semantics_before_commit(
    tmp_path: Path,
    understanding: str,
    response: str,
) -> None:
    book = _book_document()
    store = ReadingProductStore.create(
        tmp_path,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at="2026-08-29T01:00:00Z",
    )

    with pytest.raises(ReadingProductValidationError):
        build_and_commit_product_unit(
            store=store,
            source_unit=_source_unit(book),
            digest_result={
                "understanding": understanding,
                "reading_impression": response,
                "marginalia": [],
            },  # type: ignore[arg-type]
            book_document=book,
            epub_sha256=EPUB_SHA256,
        )

    assert store.load_units() == ()
    assert store.next_sequence_index() == 1


def test_product_store_replays_private_progress_and_checkpoint_identity(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "output" / "runtime-fixture"
    initialize_artifact_tree(output_dir)
    book = _book_document()
    store = ReadingProductStore.create(
        output_dir,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at="2026-08-29T01:00:00Z",
    )
    unit, _findings, _status = build_and_commit_product_unit(
        store=store,
        source_unit=_source_unit(book),
        digest_result=_digest(),  # type: ignore[arg-type]
        book_document=book,
        epub_sha256=EPUB_SHA256,
    )

    bundle = runner_module._load_runtime_bundle(output_dir)
    replayed = runner_module._reconcile_reading_product_progress(
        output_dir=output_dir,
        store=store,
        book_document=book,  # type: ignore[arg-type]
        bundle=bundle,
    )

    ledger_rows = [
        json.loads(line)
        for line in unit_span_ledger_file(output_dir).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reactions = json.loads(reaction_records_file(output_dir).read_text(encoding="utf-8"))
    shell = load_runtime_shell(runtime_shell_file(output_dir))
    assert [row["unit_id"] for row in ledger_rows] == [unit.unit_id]
    assert [row["reaction_id"] for row in reactions["records"]] == [
        item.marginalia_id for item in unit.marginalia
    ]
    assert {row["created_at"] for row in reactions["records"]} == {unit.settled_at}
    expected_product_reactions = [dict(row) for row in reactions["records"]]
    assert shell["reading_id"] == store.reading_id
    assert shell["last_product_unit_id"] == unit.unit_id
    assert shell["last_product_unit_sequence"] == 1
    assert shell["cursor"]["span_end_cursor"]["char_offset"] == len(PARAGRAPH_TEXT)

    # Replaying the same product truth is idempotent and does not duplicate projections.
    runner_module._reconcile_reading_product_progress(
        output_dir=output_dir,
        store=store,
        book_document=book,  # type: ignore[arg-type]
        bundle=replayed,
    )
    assert len(unit_span_ledger_file(output_dir).read_text(encoding="utf-8").splitlines()) == 1
    reactions = json.loads(reaction_records_file(output_dir).read_text(encoding="utf-8"))
    assert len(reactions["records"]) == len(unit.marginalia)

    # Product replay repairs drifted and extra read-surface records while
    # preserving an explicitly non-product internal record.
    drifted = dict(expected_product_reactions[0])
    drifted["thought"] = "stale private text"
    extra = dict(expected_product_reactions[0])
    extra["reaction_id"] = "rx-private-extra"
    internal = {
        "reaction_id": "internal-reconsolidation-1",
        "record_source": "reconsolidation",
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
    }
    reaction_records_file(output_dir).write_text(
        json.dumps(
            {
                **reactions,
                "records": [drifted, expected_product_reactions[1], extra, internal],
            }
        ),
        encoding="utf-8",
    )
    runner_module._reconcile_reading_product_progress(
        output_dir=output_dir,
        store=store,
        book_document=book,  # type: ignore[arg-type]
        bundle=runner_module._load_runtime_bundle(output_dir),
    )
    repaired = json.loads(reaction_records_file(output_dir).read_text(encoding="utf-8"))
    assert repaired["records"] == [*expected_product_reactions, internal]

    checkpoint = write_full_checkpoint(
        output_dir,
        checkpoint_id="after-product-unit",
        checkpoint_reason="unit_test",
    )
    assert checkpoint["reading_id"] == store.reading_id
    assert checkpoint["last_product_unit_id"] == unit.unit_id
    assert checkpoint["last_product_unit_sequence"] == 1

    # A lost thin-shell marker can be recovered from the full checkpoint before
    # the Product Store is reopened by the runner.
    shell = load_runtime_shell(runtime_shell_file(output_dir))
    shell.pop("reading_id", None)
    shell.pop("last_product_unit_id", None)
    shell.pop("last_product_unit_sequence", None)
    save_runtime_shell(runtime_shell_file(output_dir), shell)
    resumed = resume_from_checkpoint(
        output_dir,
        book_document=book,  # type: ignore[arg-type]
        requested_resume_kind="warm_resume",
    )
    assert resumed["reading_id"] == store.reading_id
    assert resumed["last_product_unit_id"] == unit.unit_id
    assert resumed["last_product_unit_sequence"] == 1


@pytest.mark.parametrize(
    ("divergence", "message"),
    [
        ("ahead", "ahead of Reading Product truth"),
        ("wrong_id", "conflicts with Reading Product truth"),
        ("wrong_span", "conflicts with Reading Product truth"),
    ],
)
def test_product_reconcile_fails_closed_on_private_unit_span_divergence(
    tmp_path: Path,
    divergence: str,
    message: str,
) -> None:
    output_dir = tmp_path / "output" / "runtime-fixture"
    initialize_artifact_tree(output_dir)
    book = _book_document()
    store = ReadingProductStore.create(
        output_dir,
        epub_sha256=EPUB_SHA256,
        book_document=book,
        started_at="2026-08-29T01:00:00Z",
    )
    build_and_commit_product_unit(
        store=store,
        source_unit=_source_unit(book),
        digest_result=_digest(),  # type: ignore[arg-type]
        book_document=book,
        epub_sha256=EPUB_SHA256,
    )
    record = {
        "unit_id": "u000001",
        "sequence_index": 1,
        "source_span_id": source_span_id(_source_span()),
    }
    if divergence == "ahead":
        record.update(unit_id="u000002", sequence_index=2)
    elif divergence == "wrong_id":
        record["unit_id"] = "u999999"
    else:
        record["source_span_id"] = "src:c1:p1@1-p1@2"
    unit_span_ledger_file(output_dir).write_text(
        json.dumps(record) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match=message):
        runner_module._reconcile_reading_product_progress(
            output_dir=output_dir,
            store=store,
            book_document=book,  # type: ignore[arg-type]
            bundle=runner_module._load_runtime_bundle(output_dir),
        )

    shell = load_runtime_shell(runtime_shell_file(output_dir))
    assert shell["cursor"].get("span_end_cursor") is None


def test_fresh_runtime_open_creates_a_new_product_revision(tmp_path: Path) -> None:
    output_dir = tmp_path / "output" / "runtime-fixture"
    initialize_artifact_tree(output_dir)
    source_file = tmp_path / "source.epub"
    source_file.write_bytes(b"stable offline EPUB fixture")
    book = _book_document()
    provisioned = ProvisionedBook(
        book_path=source_file,
        title="Runtime Fixture",
        author="Reader",
        book_language="en",
        output_language="en",
        output_dir=output_dir,
        raw_chapters=None,
        book_document=book,  # type: ignore[arg-type]
    )

    first = runner_module._open_reading_product_store(
        provisioned=provisioned,
        continue_mode=False,
    )
    second = runner_module._open_reading_product_store(
        provisioned=provisioned,
        continue_mode=False,
    )

    assert first.reading_id != second.reading_id
    assert first.ledger_path.exists()
    assert second.ledger_path.exists()
    assert ReadingProductStore.open(output_dir, first.reading_id).reading_id == first.reading_id
    assert load_runtime_shell(runtime_shell_file(output_dir))["reading_id"] == second.reading_id
