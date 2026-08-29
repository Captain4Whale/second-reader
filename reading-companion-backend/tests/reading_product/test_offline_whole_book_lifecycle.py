"""Offline whole-book acceptance for Reading Product v1.

This test intentionally uses the tracked Tiny Reader EPUB and the ordinary
attentional_v2 parse/read entrypoints.  Only model invocation boundaries are
replaced with deterministic values; source selection, Unit settlement, the
Product Store, resume/finalization, compatibility projection, and Annotation
Pack publication all remain production code.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
import json
from types import SimpleNamespace

import pytest

from src.annotation_pack.builder import CreatorInput
from src.annotation_pack.exporter import ExportPolicy, export_annotation_pack
from src.annotation_pack.ids import default_creator_id
from src.annotation_pack.packaging import validate_detached_annotations
from src.attentional_v2 import runner as runner_module
from src.attentional_v2 import slow_cycle as slow_cycle_module
from src.attentional_v2 import survey as survey_module
from src.attentional_v2.storage import (
    ATTENTIONAL_V2_MECHANISM_KEY,
    chapter_result_compatibility_file,
    settlement_audit_file,
)
from src.reading_core import validate_book_document_source_range
from src.reading_core.runtime_contracts import ParseRequest, ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_product import ReadingProductStore
from src.reading_product.serialization import load_document_bytes
from src.reading_runtime.artifacts import runtime_shell_file, source_asset_file
from src.reading_runtime.shell_state import load_runtime_shell


BACKEND = Path(__file__).resolve().parents[2]
TINY_READER_EPUB = (
    BACKEND / "tests" / "annotation_pack" / "fixtures" / "tiny-reader" / "source.epub"
)
PACK_GENERATED_AT = datetime(2026, 8, 29, 0, 0, tzinfo=timezone.utc)


def _deterministic_ingest(**kwargs: object) -> dict[str, object]:
    """Select exactly the first complete visible paragraph slice."""

    preview = kwargs.get("current_view_content")
    assert isinstance(preview, dict)
    slices = [
        dict(item)
        for item in preview.get("paragraph_slices", [])
        if isinstance(item, dict)
    ]
    assert slices
    partition = [
        {
            "title": f"Offline paragraph {item['paragraph_index']}",
            "end_paragraph_n": str(item["paragraph_index"]),
            "end_at": "paragraph_end",
            "status": "complete",
        }
        for item in slices
    ]
    first = partition[0]
    return {
        "unit": {
            "end_paragraph_n": first["end_paragraph_n"],
            "end_at": first["end_at"],
        },
        "preview_partition": partition,
        "reason": "offline_fixture_first_complete_paragraph",
        "memory_recalls": [],
        "memory_recalls_status": "not_requested",
    }


def _deterministic_digest_factory(
    calls: list[str],
):  # type: ignore[no-untyped-def]
    """Return product-rich deterministic Digest results keyed by source text."""

    def digest(**kwargs: object) -> dict[str, object]:
        source = kwargs.get("current_unit_source")
        assert isinstance(source, dict)
        source_text = str(source.get("source_text", ""))
        assert source_text
        calls.append(source_text)

        marginalia: list[dict[str, object]] = []
        if source_text == "The reader paused before the margin.":
            marginalia = [
                {
                    "kind": "highlight",
                    "source_quote": "reader paused",
                }
            ]
        elif source_text == "A durable idea is worth returning to.":
            marginalia = [
                {
                    "kind": "note",
                    "source_quote": "durable idea",
                    "content": "Durability becomes meaningful through return.",
                }
            ]
        elif source_text == "A quiet mark can wait without closing the question.":
            # The invalid first candidate must be rejected without discarding
            # the valid Highlight or the surrounding Product Unit.
            marginalia = [
                {
                    "kind": "note",
                    "source_quote": "text absent from the EPUB",
                    "content": "This invalid anchor belongs only in audit.",
                },
                {
                    "kind": "highlight",
                    "source_quote": "quiet mark",
                },
            ]

        return {
            "understanding": f"Understood the accepted source: {source_text}",
            "reading_impression": f"Responded to the accepted source: {source_text}",
            "marginalia": marginalia,
            "memory_uptake_ops": [],
        }

    return digest


def _deterministic_slow_cycle(
    _system_prompt: str,
    _user_prompt: str,
    **kwargs: object,
) -> SimpleNamespace:
    """Replace only the slow-cycle model boundary, preserving its real logic."""

    output_tool = kwargs.get("output_tool")
    assert isinstance(output_tool, dict)
    assert output_tool.get("name") == "submit_chapter_consolidation_result"
    return SimpleNamespace(
        payload={
            "chapter_ref": "",
            "backward_sweep": [],
            "cooling_operations": [],
            "promotion_candidates": [],
            "knowledge_activation_updates": [],
            "cross_chapter_carry_forward": [],
            "chapter_summary_note": "",
        }
    )


def _load_complete_product(output_dir: Path):  # type: ignore[no-untyped-def]
    root = output_dir / "public" / "reading-products"
    pointer = json.loads((root / "current.json").read_text(encoding="utf-8"))
    return load_document_bytes((root / str(pointer["reading_product"])).read_bytes())


def _export_pack(output_dir: Path, output_root: Path, runtime_root: Path):  # type: ignore[no-untyped-def]
    return export_annotation_pack(
        output_dir=output_dir,
        output_root=output_root,
        runtime_root=runtime_root,
        track_key="offline-whole-book",
        track_name="Offline whole-book acceptance",
        creator=CreatorInput(
            id=default_creator_id(),
            type="Software",
            name="Second Reader",
        ),
        generated_at=PACK_GENERATED_AT,
        policy=ExportPolicy(deliverables="detached"),
    )


def test_real_epub_offline_runner_resume_finalizes_and_exports_pack(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove the real EPUB -> Product -> Pack route without any provider call."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("READING_OBSERVABILITY_OTLP_ENABLED", "0")
    digest_calls: list[str] = []

    # Survey already has an explicit deterministic structural fallback.  Make
    # that path mandatory and fail loudly if its optional model boundary is
    # reached.  Ingest, Digest, and chapter slow-cycle calls are test doubles;
    # no provider/preflight/key path is exercised by this test.
    monkeypatch.setattr(survey_module, "current_llm_scope", lambda: None)
    monkeypatch.setattr(
        runner_module,
        "llm_invocation_scope",
        lambda *_args, **_kwargs: nullcontext(),
    )

    def forbidden_survey_call(*_args: object, **_kwargs: object) -> None:
        pytest.fail("offline acceptance reached the survey model boundary")

    monkeypatch.setattr(
        survey_module,
        "invoke_structured_output",
        forbidden_survey_call,
    )
    monkeypatch.setattr(runner_module, "_call_ingest", _deterministic_ingest)
    monkeypatch.setattr(
        runner_module,
        "_call_digest",
        _deterministic_digest_factory(digest_calls),
    )
    monkeypatch.setattr(
        slow_cycle_module,
        "invoke_structured_output",
        _deterministic_slow_cycle,
    )

    mechanism = AttentionalV2Mechanism()
    parse_result = mechanism.parse_book(
        ParseRequest(
            book_path=TINY_READER_EPUB,
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
        )
    )
    output_dir = parse_result.output_dir.resolve()
    output_root = output_dir.parent
    assert parse_result.book_document["metadata"]["book"] == (  # type: ignore[index]
        "Tiny Reader: Returning Light"
    )
    assert {
        paragraph["href"]
        for chapter in parse_result.book_document["chapters"]
        for paragraph in chapter["paragraphs"]
    } == {
        "Text/first-return.xhtml",
        "Text/returning-light.xhtml",
    }

    original_persist_marginalia = runner_module._persist_marginalia
    crashed = False

    def crash_after_first_product_commit(**_kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal crashed
        if not crashed:
            crashed = True
            raise RuntimeError("offline simulated post-product-commit crash")
        return original_persist_marginalia(**_kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(
        runner_module,
        "_persist_marginalia",
        crash_after_first_product_commit,
    )
    request = ReadRequest(
        book_path=TINY_READER_EPUB,
        mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
        mechanism_config={"memory_retrieval_mode": "text_only"},
    )
    with pytest.raises(
        RuntimeError,
        match="offline simulated post-product-commit crash",
    ):
        mechanism.read_book(request)

    shell = load_runtime_shell(runtime_shell_file(output_dir))
    store = ReadingProductStore.open(output_dir, str(shell["reading_id"]))
    assert len(store.load_units()) == 1
    assert store.snapshot(book_document=parse_result.book_document).status == "partial"
    assert not (output_dir / "public" / "reading-products" / "current.json").exists()
    assert digest_calls == ["First Return"]

    # A changed source asset must fail closed on resume before any second
    # Digest.  Restoring the exact bytes then permits normal product replay.
    source_asset = source_asset_file(output_dir)
    original_source_bytes = source_asset.read_bytes()
    source_asset.write_bytes(original_source_bytes + b"offline-mutation")
    monkeypatch.setattr(
        runner_module, "_persist_marginalia", original_persist_marginalia
    )
    with pytest.raises(RuntimeError, match="source identity no longer matches"):
        mechanism.read_book(
            ReadRequest(
                book_path=TINY_READER_EPUB,
                continue_mode=True,
                mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
                mechanism_config={"memory_retrieval_mode": "text_only"},
            )
        )
    assert digest_calls == ["First Return"]
    source_asset.write_bytes(original_source_bytes)

    completed = mechanism.read_book(
        ReadRequest(
            book_path=TINY_READER_EPUB,
            continue_mode=True,
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={"memory_retrieval_mode": "text_only"},
        )
    )
    assert completed.output_dir.resolve() == output_dir
    shell = load_runtime_shell(runtime_shell_file(output_dir))
    assert shell["status"] == "completed"

    product = _load_complete_product(output_dir)
    assert product.status == "complete"
    assert product.reading_id == store.reading_id
    assert len(product.units) == sum(
        1
        for chapter in completed.book_document["chapters"]
        for paragraph in chapter["paragraphs"]
        if paragraph.get("text") and paragraph.get("text_role") != "auxiliary"
    )
    assert any(not unit.marginalia for unit in product.units)
    marginalia = [item for unit in product.units for item in unit.marginalia]
    assert [item.kind for item in marginalia] == ["highlight", "note", "highlight"]
    assert [item.source_quote for item in marginalia] == [
        "reader paused",
        "durable idea",
        "quiet mark",
    ]
    assert marginalia[0].body_text is None
    assert marginalia[1].body_text == "Durability becomes meaningful through return."
    assert marginalia[2].body_text is None
    assert all(unit.understanding and unit.response for unit in product.units)
    for unit in product.units:
        validate_book_document_source_range(
            completed.book_document,
            unit.source_range,
        )
        for item in unit.marginalia:
            validate_book_document_source_range(
                completed.book_document,
                item.source_range,
                expected_quote=item.source_quote,
                within=unit.source_range,
            )

    audit_rows = [
        json.loads(line)
        for line in settlement_audit_file(output_dir)
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    product_finding_codes = [
        finding["code"]
        for row in audit_rows
        for finding in row["reading_product"]["findings"]
    ]
    assert product_finding_codes == ["unresolved_source_quote"]
    assert "text absent from the EPUB" not in {item.source_quote for item in marginalia}

    # Finalization derives the legacy chapter views from Product Units.
    for chapter_id in (1, 2):
        assert chapter_result_compatibility_file(output_dir, chapter_id).is_file()

    first_export = _export_pack(output_dir, output_root, tmp_path)
    assert first_export.status == "published"
    assert first_export.validation.publishable
    assert first_export.detached_package is not None
    assert first_export.annotations_json is not None
    first_annotations = first_export.annotations_json.read_bytes()
    first_package = first_export.detached_package.read_bytes()
    packaged = validate_detached_annotations(
        first_package,
        expected_annotations_json=first_annotations,
    )
    assert packaged.validation.publishable
    pack = json.loads(first_annotations)
    assert [item["motivation"] for item in pack["items"]] == [
        "highlighting",
        "commenting",
        "highlighting",
    ]
    assert "body" not in pack["items"][0]
    assert pack["items"][1]["body"] == {
        "type": "TextualBody",
        "value": "Durability becomes meaningful through return.",
    }

    second_export = _export_pack(output_dir, output_root, tmp_path)
    assert second_export.status == "unchanged"
    assert second_export.revision_id == first_export.revision_id
    assert second_export.annotations_json is not None
    assert second_export.detached_package is not None
    assert second_export.annotations_json.read_bytes() == first_annotations
    assert second_export.detached_package.read_bytes() == first_package

    # Re-running a completed Product revision is also a no-model, no-new-Unit
    # operation; its public Product and Pack inputs stay byte-identical.
    digest_count = len(digest_calls)
    complete_product_root = output_dir / "public" / "reading-products"
    product_pointer_before = (complete_product_root / "current.json").read_bytes()
    mechanism.read_book(
        ReadRequest(
            book_path=TINY_READER_EPUB,
            continue_mode=True,
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={"memory_retrieval_mode": "text_only"},
        )
    )
    assert len(digest_calls) == digest_count
    assert (
        complete_product_root / "current.json"
    ).read_bytes() == product_pointer_before
    final_export = _export_pack(output_dir, output_root, tmp_path)
    assert final_export.status == "unchanged"
    assert final_export.revision_id == first_export.revision_id
