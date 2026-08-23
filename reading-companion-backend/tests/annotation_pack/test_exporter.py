from __future__ import annotations

import ast
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unicodedata
import zipfile

import pytest

import src.annotation_pack.exporter as exporter_module
from src.annotation_pack.builder import CreatorInput
from src.annotation_pack.drafts import (
    ResolvedAnchor,
    ResolvedAnnotationDraft,
)
from src.annotation_pack.exporter import (
    ExportPolicy,
    MAX_BOOK_DOCUMENT_BYTES,
    export_annotation_pack,
    inspect_annotation_pack,
    publication_revision_id,
    resolve_book_output_dir,
    second_reader_input_snapshot_digest,
    track_slug,
)
from src.annotation_pack.ids import default_creator_id
from src.annotation_pack.identity import PublicationIdentityError
from src.annotation_pack.serialization import canonical_json_bytes, semantic_digest
from src.attentional_v2.storage import reaction_records_file
from src.parsers import parse_ebook
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_core.storage import book_document_file
from src.reading_runtime.artifacts import existing_run_state_file
from src.reading_runtime.job_lease import (
    JobLeaseGrant,
    acquire_job_lease,
    release_job_lease,
)
from src.reading_runtime.source_normalization import normalize_book_document_source
from tests.annotation_pack.epub_factory import FixtureMetadata, build_epub_bytes


NOW = datetime(2026, 8, 23, 12, 34, 56, tzinfo=timezone.utc)
BACKEND = Path(__file__).resolve().parents[2]
CREATOR = CreatorInput(
    id=default_creator_id(),
    type="Software",
    name="Second Reader",
)


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _write_source_and_document(output_dir: Path) -> dict[str, object]:
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(build_epub_bytes())
    metadata = FixtureMetadata()
    canonical = build_book_document_from_chapters(
        list(parse_ebook(str(source))),
        title=metadata.title,
        author=", ".join(metadata.creators),
        book_language=metadata.language,
        output_language="en",
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        canonical,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    path = book_document_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(normalized))
    return normalized


def _paragraph(document: dict[str, object], chapter_id: int, paragraph_index: int) -> str:
    for chapter in document["chapters"]:  # type: ignore[index,union-attr]
        if chapter["id"] != chapter_id:
            continue
        for paragraph in chapter["paragraphs"]:
            if paragraph["paragraph_index"] == paragraph_index:
                return paragraph["text"]
    raise AssertionError("fixture paragraph missing")


def _row(
    *,
    kind: str,
    chapter_id: int,
    paragraph_index: int,
    text: str,
    needle: str,
    created_at: str,
    body: str = "",
) -> dict[str, object]:
    start = text.index(needle)
    end = start + len(needle)
    cursor_start = {
        "chapter_id": chapter_id,
        "chapter_ref": "Fixture chapter",
        "paragraph_index": paragraph_index,
        "char_offset": start,
    }
    cursor_end = {**cursor_start, "char_offset": end}
    return {
        "reaction_id": f"private-{kind}",
        "chapter_id": chapter_id,
        "chapter_ref": "Fixture chapter",
        "emitted_at_source_span_id": "private-source-span",
        "record_source": "read_surface",
        "type": "association" if kind == "note" else "highlight",
        "compat_family": "association" if kind == "note" else "highlight",
        "marginalia_kind": kind,
        "thought": body,
        "source_quote": needle,
        "primary_source_ref": {
            "source_span_id": "private-source-span",
            "source_span": {
                "start_cursor": cursor_start,
                "end_cursor": cursor_end,
            },
            "quote": needle,
            "role": "reaction_anchor",
            "resolution": {
                "status": "matched",
                "method": "exact_text",
                "match_count": 1,
            },
        },
        "related_source_refs": [],
        "reconsolidation_record_id": "",
        "supersedes_reaction_id": "",
        "compatibility_section_ref": "private-section",
        "prior_link": None,
        "outside_link": None,
        "search_intent": None,
        "search_query": "",
        "search_results": [],
        "created_at": created_at,
    }


def _ledger(document: dict[str, object]) -> dict[str, object]:
    first = _paragraph(document, 1, 3)
    second = _paragraph(document, 1, 4)
    return {
        "schema_version": 1,
        "mechanism_version": "attentional_v2-phase9",
        "updated_at": "2026-08-23T12:00:00Z",
        "records": [
            _row(
                kind="highlight",
                chapter_id=1,
                paragraph_index=3,
                text=first,
                needle="durable idea",
                created_at="2026-08-23T12:01:02Z",
            ),
            _row(
                kind="note",
                chapter_id=1,
                paragraph_index=4,
                text=second,
                needle="better question",
                body="A return can change the question.",
                created_at="2026-08-23T12:02:03.999999Z",
            ),
        ],
    }


def _fixture(
    tmp_path: Path,
    *,
    stage: str = "completed",
    records: list[dict[str, object]] | None = None,
) -> tuple[Path, Path, Path, dict[str, object]]:
    runtime_root = tmp_path / "runtime"
    output_root = runtime_root / "output"
    output_dir = output_root / "book-1"
    output_dir.mkdir(parents=True)
    document = _write_source_and_document(output_dir)
    ledger = _ledger(document)
    if records is not None:
        ledger["records"] = records
    ledger_path = reaction_records_file(output_dir)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_bytes(_json_bytes(ledger))
    run_path = existing_run_state_file(output_dir)
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_bytes(_json_bytes({"stage": stage}))
    return runtime_root, output_root, output_dir, ledger


def _export(
    runtime_root: Path,
    output_root: Path,
    output_dir: Path,
    **policy_values: object,
):  # type: ignore[no-untyped-def]
    values = dict(policy_values)
    deliverables = values.pop("deliverables", "json")
    return export_annotation_pack(
        output_dir=output_dir,
        output_root=output_root,
        runtime_root=runtime_root,
        track_key="second-reader-agent",
        creator=CREATOR,
        generated_at=NOW,
        policy=ExportPolicy(deliverables=deliverables, **values),  # type: ignore[arg-type]
    )


def _resolved(index: int, digest: str) -> ResolvedAnnotationDraft:
    return ResolvedAnnotationDraft(
        kind="highlight",
        body_text=None,
        created_at=NOW,
        target=ResolvedAnchor(
            anchor_id="urn:uuid:8d3a79e9-b894-5bac-ab6c-3629d7af23d4",
            href="Text/chapter.xhtml",
            exact="x",
            target={},
            findings=(),
        ),
        source_record_index=index,
        source_record_digest=digest,
    )


def test_input_snapshot_and_revision_framing_fixed_vectors() -> None:
    records = (_resolved(9, "5" * 64), _resolved(2, "6" * 64))
    stream = (
        b"SECOND-READER-INPUT-SNAPSHOT-V1\n"
        + b"E:64:" + b"1" * 64 + b"\n"
        + b"B:64:" + b"2" * 64 + b"\n"
        + b"S:64:" + b"3" * 64 + b"\n"
        + b"L:64:" + b"4" * 64 + b"\n"
        + b"R:64:" + b"6" * 64 + b"\n"
        + b"R:64:" + b"5" * 64 + b"\n"
    )
    assert second_reader_input_snapshot_digest(
        source_epub_sha256="1" * 64,
        book_document_sha256="2" * 64,
        substrate_sha256="3" * 64,
        reaction_ledger_sha256="4" * 64,
        resolved_records=records,
    ) == hashlib.sha256(stream).hexdigest()

    revision_stream = (
        b"SECOND-READER-ANNOTATION-PUBLICATION-REVISION-V1\n"
        + b"J:64:" + b"a" * 64 + b"\n"
        + b"P:0:\n"
        + b"R:64:" + b"b" * 64 + b"\n"
    )
    assert publication_revision_id(
        annotations_json_sha256="a" * 64,
        package_sha256=None,
        validation_report_sha256="b" * 64,
    ) == hashlib.sha256(revision_stream).hexdigest()


def test_resolve_book_output_dir_requires_safe_direct_real_child(tmp_path: Path) -> None:
    root = tmp_path / "output"
    book = root / "book-1"
    book.mkdir(parents=True)
    assert resolve_book_output_dir(book_id="book-1", output_root=root) == book
    assert resolve_book_output_dir(book_output_dir=book, output_root=root) == book
    with pytest.raises(ValueError):
        resolve_book_output_dir(book_id="../book-1", output_root=root)
    nested = book / "nested"
    nested.mkdir()
    with pytest.raises(ValueError):
        resolve_book_output_dir(book_output_dir=nested, output_root=root)
    alias = root / "alias"
    alias.symlink_to(book, target_is_directory=True)
    with pytest.raises(ValueError):
        resolve_book_output_dir(book_output_dir=alias, output_root=root)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS path alias behavior")
def test_resolve_book_output_dir_rejects_case_alias_spelling_on_macos(
    tmp_path: Path,
) -> None:
    root = tmp_path / "output"
    book = root / "book-a"
    book.mkdir(parents=True)
    alias = root / "BOOK-A"
    if not alias.exists() or not alias.samefile(book):
        pytest.skip("test volume is case-sensitive")

    with pytest.raises(ValueError, match="spelling is not canonical"):
        resolve_book_output_dir(book_id=alias.name, output_root=root)
    with pytest.raises(ValueError, match="spelling is not canonical"):
        resolve_book_output_dir(book_output_dir=alias, output_root=root)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS path alias behavior")
def test_resolve_book_output_dir_rejects_normalization_alias_on_macos(
    tmp_path: Path,
) -> None:
    root = tmp_path / "output"
    stored_name = unicodedata.normalize("NFD", "café-book")
    alias_name = unicodedata.normalize("NFC", stored_name)
    (root / stored_name).mkdir(parents=True)
    if alias_name in os.listdir(root) or not (root / alias_name).exists():
        pytest.skip("test volume does not expose a normalization alias")

    with pytest.raises(ValueError, match="spelling is not canonical"):
        resolve_book_output_dir(book_id=alias_name, output_root=root)


def test_json_export_publishes_immutable_revision_then_is_unchanged(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)

    assert first.status == "published"
    assert first.validation.status == "valid"
    assert first.annotations_json is not None and first.annotations_json.is_file()
    assert first.validation_report is not None and first.validation_report.is_file()
    assert first.current_pointer is not None and first.current_pointer.is_file()
    assert first.revision_id is not None
    assert first.detached_package is None
    assert output_dir / "public" / "annotation-packs" in first.annotations_json.parents
    assert canonical_json_bytes(json.loads(first.annotations_json.read_bytes())) == (
        first.annotations_json.read_bytes()
    )

    first_pointer = first.current_pointer.read_bytes()
    second = _export(runtime_root, output_root, output_dir)
    assert second.status == "unchanged"
    assert second.revision_id == first.revision_id
    assert second.current_pointer.read_bytes() == first_pointer
    assert len(list(first.annotations_json.parents[1].iterdir())) == 1
    assert canonical_json_bytes(second.pack) == second.annotations_json.read_bytes()


def test_json_only_revision_upgrades_byte_preservingly_to_detached(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    json_only = _export(runtime_root, output_root, output_dir)
    assert json_only.annotations_json is not None
    assert json_only.validation_report is not None
    assert json_only.revision_id is not None
    old_revision = json_only.annotations_json.parent
    old_contents = {
        child.name: child.read_bytes()
        for child in old_revision.iterdir()
        if child.is_file()
    }
    json_bytes = json_only.annotations_json.read_bytes()

    detached = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert detached.status == "published"
    assert detached.revision_id is not None
    assert detached.revision_id != json_only.revision_id
    assert detached.annotations_json is not None
    assert detached.annotations_json.read_bytes() == json_bytes
    assert detached.detached_package is not None
    assert detached.detached_package.name == (
        f"{detached.current_pointer.parent.name}.annotations"
    )
    with zipfile.ZipFile(detached.detached_package) as archive:
        assert archive.namelist() == ["annotations.json"]
        assert archive.read("annotations.json") == json_bytes
    pointer = json.loads(detached.current_pointer.read_bytes())
    assert pointer["detached_package"].endswith(detached.detached_package.name)
    assert pointer["detached_package_sha256"] == hashlib.sha256(
        detached.detached_package.read_bytes()
    ).hexdigest()
    report = json.loads(detached.validation_report.read_bytes())
    assert report["package_sha256"] == pointer["detached_package_sha256"]
    assert {
        child.name: child.read_bytes()
        for child in old_revision.iterdir()
        if child.is_file()
    } == old_contents

    repeated = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert repeated.status == "unchanged"
    assert repeated.revision_id == detached.revision_id
    assert repeated.detached_package == detached.detached_package


def test_json_request_accepts_current_detached_superset_as_unchanged(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    detached = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    requested_json = _export(runtime_root, output_root, output_dir)

    assert detached.status == "published"
    assert requested_json.status == "unchanged"
    assert requested_json.revision_id == detached.revision_id
    assert requested_json.detached_package == detached.detached_package


def test_package_build_failure_preserves_json_only_current(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.annotation_pack.packaging import PackageError

    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    json_only = _export(runtime_root, output_root, output_dir)
    assert json_only.current_pointer is not None
    old_pointer = json_only.current_pointer.read_bytes()
    old_revision = json_only.annotations_json.parent
    old_files = {
        child.name: child.read_bytes()
        for child in old_revision.iterdir()
        if child.is_file()
    }

    def fail_package(_annotations_json: bytes) -> None:
        raise PackageError()

    monkeypatch.setattr(exporter_module, "build_detached_annotations", fail_package)
    failed = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert failed.status == "failed"
    assert failed.validation.findings[0].code == "package_entry_invalid"
    assert json_only.current_pointer.read_bytes() == old_pointer
    assert {
        child.name: child.read_bytes()
        for child in old_revision.iterdir()
        if child.is_file()
    } == old_files


def test_package_write_failure_preserves_current_and_cleans_owned_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    json_only = _export(runtime_root, output_root, output_dir)
    assert json_only.current_pointer is not None
    old_pointer = json_only.current_pointer.read_bytes()
    original_write = exporter_module._write_exclusive_file_at

    def fail_package_write(
        directory_descriptor: int,
        name: str,
        content: bytes,
    ) -> exporter_module._FileIdentity:
        if name.endswith(".annotations"):
            raise OSError("simulated package write failure")
        return original_write(directory_descriptor, name, content)

    monkeypatch.setattr(
        exporter_module,
        "_write_exclusive_file_at",
        fail_package_write,
    )
    failed = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert failed.status == "failed"
    assert failed.validation.findings[0].code == "publication_write_failed"
    assert json_only.current_pointer.read_bytes() == old_pointer
    revisions = json_only.annotations_json.parents[1]
    assert not [child for child in revisions.iterdir() if child.name.startswith(".tmp-")]


def test_force_regenerate_reuses_identical_immutable_revision(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    forced = _export(
        runtime_root,
        output_root,
        output_dir,
        force_regenerate=True,
    )
    assert forced.status == "published"
    assert forced.revision_id == first.revision_id


def test_force_json_request_does_not_retract_existing_detached_deliverable(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    detached = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    forced = _export(
        runtime_root,
        output_root,
        output_dir,
        force_regenerate=True,
    )

    assert detached.status == "published"
    assert forced.status == "published"
    assert forced.detached_package is not None
    pointer = json.loads(forced.current_pointer.read_bytes())
    assert pointer["detached_package"].endswith(forced.detached_package.name)


@pytest.mark.parametrize(
    ("stage", "policy", "expected"),
    [
        ("completed", {}, "published"),
        ("paused", {}, "failed"),
        ("paused", {"allow_partial": True}, "published"),
        ("error", {}, "failed"),
        ("error", {"allow_partial": True}, "published"),
        ("ready", {}, "failed"),
        ("ready", {"allow_empty": True}, "failed"),
        ("parsing_structure", {"allow_partial": True}, "failed"),
        ("deep_reading", {"allow_partial": True}, "failed"),
    ],
)
def test_run_state_matrix_for_nonempty_ledger(
    tmp_path: Path,
    stage: str,
    policy: dict[str, bool],
    expected: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(
        tmp_path, stage=stage
    )
    result = _export(runtime_root, output_root, output_dir, **policy)
    assert result.status == expected
    if expected == "failed":
        assert result.validation.findings[0].code == "run_state_not_exportable"


@pytest.mark.parametrize(
    ("stage", "policy", "expected"),
    [
        ("completed", {}, "failed"),
        ("completed", {"allow_empty": True}, "published"),
        ("paused", {"allow_partial": True}, "failed"),
        ("paused", {"allow_partial": True, "allow_empty": True}, "published"),
        ("ready", {}, "failed"),
        ("ready", {"allow_empty": True}, "published"),
    ],
)
def test_run_state_matrix_for_empty_ledger(
    tmp_path: Path,
    stage: str,
    policy: dict[str, bool],
    expected: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(
        tmp_path, stage=stage, records=[]
    )
    result = _export(runtime_root, output_root, output_dir, **policy)
    assert result.status == expected


@pytest.mark.parametrize("state_kind", ["missing", "unknown"])
def test_missing_or_unknown_run_state_fails_closed_with_real_guard(
    tmp_path: Path,
    state_kind: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    state_path = existing_run_state_file(output_dir)
    if state_kind == "missing":
        state_path.unlink()
    else:
        state_path.write_bytes(_json_bytes({"stage": "future-stage"}))

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert [finding.code for finding in result.validation.findings] == [
        "run_state_not_exportable"
    ]


def test_strict_row_error_fails_and_allow_skips_publishes_degraded(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    broken = deepcopy(ledger)
    broken["records"][0]["primary_source_ref"]["resolution"]["match_count"] = 2  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(broken))

    strict = _export(runtime_root, output_root, output_dir)
    assert strict.status == "failed"
    assert any(finding.code == "ambiguous_source_quote" for finding in strict.validation.findings)
    assert strict.validation_report is not None
    assert strict.validation_report.name == "last-failed-validation-report.json"
    assert strict.validation_report.is_file()

    degraded = _export(
        runtime_root,
        output_root,
        output_dir,
        allow_skips=True,
    )
    assert degraded.status == "degraded"
    assert degraded.validation.exported_count == 1
    assert degraded.validation.skipped_count == 1


def test_default_export_publishes_detached_revision(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    result = export_annotation_pack(
        output_dir=output_dir,
        output_root=output_root,
        runtime_root=runtime_root,
        track_key="second-reader-agent",
        creator=CREATOR,
    )
    assert result.status == "published"
    assert result.detached_package is not None
    assert result.detached_package.is_file()
    assert result.annotations_json is not None
    with zipfile.ZipFile(result.detached_package) as archive:
        assert archive.namelist() == ["annotations.json"]
        assert archive.read("annotations.json") == result.annotations_json.read_bytes()


def test_active_writer_precedes_run_state_and_deliverable_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(
        tmp_path, stage="unknown"
    )

    @contextmanager
    def conflict(*_args: object, **_kwargs: object):  # type: ignore[no-untyped-def]
        raise exporter_module.JobLeaseConflict("private lease detail")
        yield

    monkeypatch.setattr(exporter_module, "guard_book_writer_exclusion", conflict)
    result = export_annotation_pack(
        output_dir=output_dir,
        output_root=output_root,
        runtime_root=runtime_root,
        track_key="second-reader-agent",
        creator=CREATOR,
    )
    assert [finding.code for finding in result.validation.findings] == [
        "active_writer_present"
    ]
    assert "private lease detail" not in repr(result)


def test_actual_active_worker_lease_blocks_export(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    grant = acquire_job_lease(
        "active-reading-job",
        root=runtime_root,
        book_id=output_dir.name,
        job_kind="deep-reading",
        mechanism_key="attentional_v2",
        enforce_book_exclusivity=True,
    )
    try:
        result = _export(runtime_root, output_root, output_dir)
    finally:
        release_job_lease(grant)

    assert result.status == "failed"
    assert [finding.code for finding in result.validation.findings] == [
        "active_writer_present"
    ]
    assert not (output_dir / "public" / "annotation-packs").exists()


def test_writer_exclusion_is_held_through_revision_and_pointer_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_publish = exporter_module._publish_json_revision
    attempted = threading.Event()
    acquired = threading.Event()
    future: Future[JobLeaseGrant] | None = None

    def acquire_concurrently() -> JobLeaseGrant:
        attempted.set()
        grant = acquire_job_lease(
            "concurrent-reading-job",
            root=runtime_root,
            book_id=output_dir.name,
            job_kind="deep-reading",
            mechanism_key="attentional_v2",
            enforce_book_exclusivity=True,
        )
        acquired.set()
        return grant

    with ThreadPoolExecutor(max_workers=1) as executor:

        def publish_while_contended(**values: object):  # type: ignore[no-untyped-def]
            nonlocal future
            future = executor.submit(acquire_concurrently)
            assert attempted.wait(timeout=1)
            assert not acquired.wait(timeout=0.1)
            return original_publish(**values)

        monkeypatch.setattr(
            exporter_module,
            "_publish_json_revision",
            publish_while_contended,
        )
        result = _export(runtime_root, output_root, output_dir)
        assert result.status == "published"
        assert future is not None
        grant = future.result(timeout=2)

    release_job_lease(grant)


def test_writer_exclusion_is_reasserted_immediately_before_pointer_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    old_pointer = first.current_pointer.read_bytes()
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "new snapshot"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
    original_capture = exporter_module._capture_prior_pointer_at
    swapped = False

    def capture_then_swap_leases(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal swapped
        prior = original_capture(*args, **kwargs)
        leases = runtime_root / "state" / "job_registry" / "leases"
        parked = leases.with_name("leases-parked-before-pointer")
        leases.rename(parked)
        leases.mkdir()
        swapped = True
        return prior

    monkeypatch.setattr(
        exporter_module,
        "_capture_prior_pointer_at",
        capture_then_swap_leases,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert swapped
    assert result.status == "failed"
    assert result.validation.findings[0].code == "active_writer_present"
    assert first.current_pointer.read_bytes() == old_pointer


def test_persistent_leases_swap_after_committed_pointer_does_not_flip_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_publish = exporter_module._publish_json_revision
    swapped = False

    def publish_then_swap_leases(**values: object):  # type: ignore[no-untyped-def]
        nonlocal swapped
        published = original_publish(**values)
        leases = runtime_root / "state" / "job_registry" / "leases"
        parked = leases.with_name("leases-parked-after-pointer")
        leases.rename(parked)
        leases.mkdir()
        swapped = True
        return published

    monkeypatch.setattr(
        exporter_module,
        "_publish_json_revision",
        publish_then_swap_leases,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert swapped
    assert result.status == "published"
    assert result.current_pointer is not None
    assert result.current_pointer.is_file()


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"\xef\xbb\xbf{}", "book_document_invalid_json"),
        (b'{"chapters":[],"chapters":[]}', "book_document_invalid_json"),
        (b'{"value":NaN}', "book_document_invalid_json"),
    ],
)
def test_book_document_strict_json_failures_are_sanitized(
    tmp_path: Path,
    payload: bytes,
    code: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    book_document_file(output_dir).write_bytes(payload)
    result = _export(runtime_root, output_root, output_dir)
    assert result.status == "failed"
    assert result.validation.findings[0].code == code
    assert str(output_dir) not in repr(result)


def test_book_document_symlink_and_limit_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original = book_document_file(output_dir)
    real = output_dir / "real-book-document.json"
    original.rename(real)
    original.symlink_to(real)
    result = _export(runtime_root, output_root, output_dir)
    assert result.validation.findings[0].code == "book_document_unavailable"

    original.unlink()
    original.write_bytes(real.read_bytes())
    monkeypatch.setattr(exporter_module, "MAX_BOOK_DOCUMENT_BYTES", 8)
    limited = _export(runtime_root, output_root, output_dir)
    assert limited.validation.findings[0].code == "book_document_limit_exceeded"
    assert MAX_BOOK_DOCUMENT_BYTES == 512 * 1024 * 1024


def test_corrupt_current_pointer_is_fatal_and_preserves_old_bytes(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    corrupt = b'{"schema_version":"private/path"}\n'
    first.current_pointer.write_bytes(corrupt)

    second = _export(runtime_root, output_root, output_dir)
    assert second.status == "failed"
    assert second.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == corrupt
    assert first.annotations_json is not None and first.annotations_json.is_file()


@pytest.mark.parametrize("corruption", ["path", "digest"])
def test_current_pointer_path_or_declared_digest_mismatch_is_fatal(
    tmp_path: Path,
    corruption: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    pointer = json.loads(first.current_pointer.read_bytes())
    if corruption == "path":
        pointer["annotations_json"] = (
            f"revisions/{pointer['revision_id']}/validation-report.json"
        )
    else:
        pointer["annotations_json_sha256"] = "0" * 64
    corrupted = canonical_json_bytes(pointer)
    first.current_pointer.write_bytes(corrupted)

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == corrupted


def test_current_pointer_cannot_declare_a_missing_detached_package(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    pointer = json.loads(first.current_pointer.read_bytes())
    pointer["detached_package"] = (
        f"revisions/{pointer['revision_id']}/{first.current_pointer.parent.name}.annotations"
    )
    pointer["detached_package_sha256"] = "0" * 64
    declared = canonical_json_bytes(pointer)
    first.current_pointer.write_bytes(declared)

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == declared


@pytest.mark.parametrize("corruption", ["path", "digest", "missing_pair"])
def test_packaged_pointer_path_digest_and_pair_are_revalidated(
    tmp_path: Path,
    corruption: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.current_pointer is not None
    pointer = json.loads(first.current_pointer.read_bytes())
    if corruption == "path":
        pointer["detached_package"] = (
            f"revisions/{pointer['revision_id']}/other.annotations"
        )
    elif corruption == "digest":
        pointer["detached_package_sha256"] = "0" * 64
    else:
        del pointer["detached_package_sha256"]
    corrupted = canonical_json_bytes(pointer)
    first.current_pointer.write_bytes(corrupted)

    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == corrupted


def test_packaged_report_must_bind_the_exact_package_digest(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.current_pointer is not None
    assert first.validation_report is not None
    report = json.loads(first.validation_report.read_bytes())
    report["package_sha256"] = "f" * 64
    report_bytes = canonical_json_bytes(report)
    first.validation_report.chmod(0o644)
    first.validation_report.write_bytes(report_bytes)
    pointer = json.loads(first.current_pointer.read_bytes())
    pointer["validation_report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    first.current_pointer.write_bytes(canonical_json_bytes(pointer))

    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert result.status == "failed"
    assert result.validation.findings[0].code == "validation_report_invalid"


def test_packaged_entry_bytes_must_equal_sibling_annotations_json(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.current_pointer is not None
    assert first.detached_package is not None
    corrupted_package = first.detached_package.read_bytes() + b"trailing-junk"
    first.detached_package.chmod(0o644)
    first.detached_package.write_bytes(corrupted_package)
    pointer = json.loads(first.current_pointer.read_bytes())
    pointer["detached_package_sha256"] = hashlib.sha256(
        corrupted_package
    ).hexdigest()
    first.current_pointer.write_bytes(canonical_json_bytes(pointer))

    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert result.status == "failed"
    assert result.validation.findings[0].code == "package_entry_invalid"


@pytest.mark.parametrize(
    ("target", "validation_call", "expected_code"),
    [
        ("annotations", 2, "publication_pointer_invalid"),
        ("report", 2, "validation_report_invalid"),
        ("pointer", 3, "publication_pointer_invalid"),
    ],
)
def test_current_artifacts_are_reasserted_after_late_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    validation_call: int,
    expected_code: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.annotations_json is not None
    assert first.validation_report is not None
    assert first.current_pointer is not None
    paths = {
        "annotations": first.annotations_json,
        "report": first.validation_report,
        "pointer": first.current_pointer,
    }
    original_validate = exporter_module.validate_pack
    calls = 0

    def validate_then_replace(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        result = original_validate(*args, **kwargs)
        if calls == validation_call:
            path = paths[target]
            if target != "pointer":
                # Immutable revisions reject ordinary writes.  Explicitly
                # chmod here to model a hostile same-UID actor and exercise
                # the final descriptor-pinned reassertion too.
                path.chmod(0o644)
            path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(exporter_module, "validate_pack", validate_then_replace)
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == expected_code
    assert result.status != "unchanged"


def test_current_package_is_reasserted_after_late_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.detached_package is not None
    original_validate = exporter_module.validate_pack
    calls = 0

    def validate_then_mutate_package(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        result = original_validate(*args, **kwargs)
        if calls == 2:
            first.detached_package.chmod(0o644)
            first.detached_package.write_bytes(
                first.detached_package.read_bytes() + b"late-mutation"
            )
        return result

    monkeypatch.setattr(
        exporter_module,
        "validate_pack",
        validate_then_mutate_package,
    )
    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert result.status == "failed"
    assert result.validation.findings[0].code == "package_entry_invalid"


def test_current_revision_symlink_to_fifo_fails_without_following_or_blocking(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.annotations_json is not None
    assert first.current_pointer is not None
    pointer_bytes = first.current_pointer.read_bytes()
    revision_dir = first.annotations_json.parent
    parked = revision_dir.parent / f"parked-{revision_dir.name}"
    revision_dir.rename(parked)
    fifo = tmp_path / "blocked-revision-fifo"
    os.mkfifo(fifo)
    revision_dir.symlink_to(fifo)

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == pointer_bytes


def test_writable_current_revision_is_not_accepted_as_unchanged(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.annotations_json is not None
    assert first.current_pointer is not None
    pointer_bytes = first.current_pointer.read_bytes()
    first.annotations_json.parent.chmod(0o755)

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_pointer_invalid"
    assert first.current_pointer.read_bytes() == pointer_bytes


def test_same_semantics_but_changed_ignored_ledger_payload_gets_new_revision(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "ignored compatibility change"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))

    second = _export(runtime_root, output_root, output_dir)
    assert second.status == "published"
    assert second.validation.semantic_digest == first.validation.semantic_digest
    assert second.validation.input_snapshot_digest != first.validation.input_snapshot_digest
    assert second.revision_id != first.revision_id


@pytest.mark.parametrize("target", ["book-document", "ledger", "source-epub"])
def test_input_mutation_between_build_and_publication_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    original_serialize = exporter_module.serialize_pack

    def serialize_then_mutate(pack: object) -> bytes:
        content = original_serialize(pack)
        if target == "book-document":
            path = book_document_file(output_dir)
            path.write_bytes(path.read_bytes() + b" ")
        elif target == "ledger":
            changed = deepcopy(ledger)
            changed["records"][0]["search_query"] = "concurrent mutation"  # type: ignore[index]
            reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
        else:
            source = output_dir / "_assets" / "source.epub"
            source.write_bytes(source.read_bytes() + b"\n")
        return content

    monkeypatch.setattr(exporter_module, "serialize_pack", serialize_then_mutate)
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert [finding.code for finding in result.validation.findings] == [
        "input_changed_during_export"
    ]
    assert result.validation_report is not None
    assert result.validation_report.is_file()
    assert result.current_pointer is None


@pytest.mark.parametrize("changed_stage", ["paused", "deep_reading"])
def test_run_state_is_rechecked_after_input_snapshot_before_noop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changed_stage: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    old_pointer = first.current_pointer.read_bytes()
    original_load = exporter_module.SecondReaderProducerAdapter.load_drafts
    calls = 0

    def load_then_change_stage(self: object, **kwargs: object):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        result = original_load(self, **kwargs)
        if calls == 2:
            existing_run_state_file(output_dir).write_bytes(
                _json_bytes({"stage": changed_stage})
            )
        return result

    monkeypatch.setattr(
        exporter_module.SecondReaderProducerAdapter,
        "load_drafts",
        load_then_change_stage,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "run_state_not_exportable"
    assert first.current_pointer.read_bytes() == old_pointer
    assert result.validation_report is not None
    assert result.validation_report.is_file()


def test_run_state_is_rechecked_at_noop_last_reversible_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    old_pointer = first.current_pointer.read_bytes()
    original_load_current = exporter_module._load_current_publication

    def load_current_then_pause(**values: object):  # type: ignore[no-untyped-def]
        current = original_load_current(**values)
        existing_run_state_file(output_dir).write_bytes(
            _json_bytes({"stage": "paused"})
        )
        return current

    monkeypatch.setattr(
        exporter_module,
        "_load_current_publication",
        load_current_then_pause,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "run_state_not_exportable"
    assert first.current_pointer.read_bytes() == old_pointer
    assert result.validation_report is not None
    assert result.validation_report.is_file()


def test_run_state_is_rechecked_immediately_before_pointer_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    old_pointer = first.current_pointer.read_bytes()
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "new snapshot"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
    original_capture = exporter_module._capture_prior_pointer_at

    def capture_then_activate(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        prior = original_capture(*args, **kwargs)
        existing_run_state_file(output_dir).write_bytes(
            _json_bytes({"stage": "deep_reading"})
        )
        return prior

    monkeypatch.setattr(
        exporter_module,
        "_capture_prior_pointer_at",
        capture_then_activate,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "run_state_not_exportable"
    assert first.current_pointer.read_bytes() == old_pointer


def test_inspector_returns_only_fixed_summary_fields(tmp_path: Path) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    exported = _export(runtime_root, output_root, output_dir)
    assert exported.annotations_json is not None
    result = inspect_annotation_pack(exported.annotations_json)
    assert result.valid
    assert dict(result.item_counts) == {"total": 2, "highlight": 1, "note": 1}
    assert result.anchor_capabilities == (
        "TextQuoteSelector",
        "sr:ParagraphCharSelector",
    )
    rendered = repr(result)
    assert "durable idea" not in rendered
    assert "A return can change" not in rendered
    assert str(output_dir) not in rendered


def test_inspector_reports_verified_cfi_without_claiming_fragment_selector(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    exported = _export(runtime_root, output_root, output_dir)
    assert exported.annotations_json is not None
    document = json.loads(exported.annotations_json.read_bytes())
    document["items"][0]["target"]["selector"].append(
        {
            "type": "sr:EpubCfiSelector",
            "value": "epubcfi(/6/4!/4/2,/1:1,/1:2)",
            "sr:verification": "quote-round-trip",
        }
    )
    document["sr:semanticDigest"]["sr:value"] = semantic_digest(document)
    source = tmp_path / "verified-cfi-pack.json"
    source.write_bytes(canonical_json_bytes(document))

    result = inspect_annotation_pack(source)

    assert result.valid
    assert result.anchor_capabilities == (
        "TextQuoteSelector",
        "sr:ParagraphCharSelector",
        "sr:EpubCfiSelector",
        "epubcfi",
    )
    assert "FragmentSelector" not in result.anchor_capabilities


def test_publication_crash_before_pointer_replace_preserves_old_pointer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    old_pointer = first.current_pointer.read_bytes()
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "different snapshot"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
    original_replace = os.replace

    def fail_pointer_replace(source: object, destination: object) -> None:
        if Path(destination).name == "current.json":
            raise OSError("simulated crash")
        original_replace(source, destination)

    monkeypatch.setattr(exporter_module.os, "replace", fail_pointer_replace)
    failed = _export(runtime_root, output_root, output_dir)
    assert failed.status == "failed"
    assert failed.validation.findings[0].code == "publication_write_failed"
    assert first.current_pointer.read_bytes() == old_pointer


def test_revision_is_reverified_after_rename_before_pointer_switch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_fsync_directory = exporter_module._fsync_directory
    mutated = False

    def mutate_after_revision_root_fsync(path: Path) -> None:
        nonlocal mutated
        original_fsync_directory(path)
        if mutated or path.name != "revisions":
            return
        revisions = [
            child
            for child in path.iterdir()
            if child.is_dir() and not child.name.startswith(".tmp-")
        ]
        if not revisions:
            return
        annotations = revisions[0] / "annotations.json"
        annotations.chmod(0o644)
        annotations.write_bytes(annotations.read_bytes() + b" ")
        mutated = True

    monkeypatch.setattr(
        exporter_module,
        "_fsync_directory",
        mutate_after_revision_root_fsync,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert mutated
    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert not list(
        (output_dir / "public" / "annotation-packs").glob("*/current.json")
    )


def test_revision_is_read_only_before_current_pointer_switch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_replace = exporter_module._atomic_replace_file_at
    ordinary_write_blocked = False

    def verify_frozen_then_replace(
        directory_descriptor: int,
        destination_name: str,
        content: bytes,
    ) -> exporter_module._FileIdentity:
        nonlocal ordinary_write_blocked
        if destination_name == "current.json":
            pointer = json.loads(content)
            annotations = (
                output_dir
                / "public"
                / "annotation-packs"
                / next(
                    path.name
                    for path in (output_dir / "public" / "annotation-packs").iterdir()
                    if path.is_dir()
                )
                / pointer["annotations_json"]
            )
            try:
                annotations.write_bytes(annotations.read_bytes() + b" ")
            except PermissionError:
                ordinary_write_blocked = True
        return original_replace(directory_descriptor, destination_name, content)

    monkeypatch.setattr(
        exporter_module,
        "_atomic_replace_file_at",
        verify_frozen_then_replace,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert ordinary_write_blocked
    assert result.status == "published"
    assert result.annotations_json is not None
    assert result.annotations_json.stat().st_mode & 0o222 == 0
    assert result.annotations_json.parent.stat().st_mode & 0o222 == 0


def test_post_switch_revision_corruption_rolls_pointer_back_with_cas(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(runtime_root, output_root, output_dir)
    assert first.current_pointer is not None
    assert first.annotations_json is not None
    old_pointer = first.current_pointer.read_bytes()
    old_annotations = first.annotations_json.read_bytes()
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "new publication snapshot"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
    original_replace = exporter_module._atomic_replace_file_at
    corrupted = False

    def replace_then_corrupt_candidate(
        directory_descriptor: int,
        destination_name: str,
        content: bytes,
    ) -> exporter_module._FileIdentity:
        nonlocal corrupted
        snapshot = original_replace(directory_descriptor, destination_name, content)
        if destination_name == "current.json":
            pointer = json.loads(content)
            track_root = first.current_pointer.parent
            annotations = track_root / pointer["annotations_json"]
            annotations.chmod(0o644)
            annotations.write_bytes(annotations.read_bytes() + b" ")
            corrupted = True
        return snapshot

    monkeypatch.setattr(
        exporter_module,
        "_atomic_replace_file_at",
        replace_then_corrupt_candidate,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert corrupted
    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert first.current_pointer.read_bytes() == old_pointer
    assert first.annotations_json.read_bytes() == old_annotations


def test_post_switch_package_corruption_rolls_pointer_back_with_cas(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.current_pointer is not None
    assert first.detached_package is not None
    old_pointer = first.current_pointer.read_bytes()
    old_package = first.detached_package.read_bytes()
    changed = deepcopy(ledger)
    changed["records"][0]["search_query"] = "new detached snapshot"  # type: ignore[index]
    reaction_records_file(output_dir).write_bytes(_json_bytes(changed))
    original_replace = exporter_module._atomic_replace_file_at
    corrupted = False

    def replace_then_corrupt_package(
        directory_descriptor: int,
        destination_name: str,
        content: bytes,
    ) -> exporter_module._FileIdentity:
        nonlocal corrupted
        snapshot = original_replace(directory_descriptor, destination_name, content)
        if destination_name == "current.json":
            pointer = json.loads(content)
            package = first.current_pointer.parent / pointer["detached_package"]
            package.chmod(0o644)
            package.write_bytes(package.read_bytes() + b"corrupt")
            corrupted = True
        return snapshot

    monkeypatch.setattr(
        exporter_module,
        "_atomic_replace_file_at",
        replace_then_corrupt_package,
    )
    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert corrupted
    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert first.current_pointer.read_bytes() == old_pointer
    assert first.detached_package.read_bytes() == old_package


def test_post_switch_third_party_pointer_is_detected_but_never_overwritten(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_fsync_directory = exporter_module._fsync_directory
    third_party_pointer: bytes | None = None

    def replace_pointer_after_switch(path: Path) -> None:
        nonlocal third_party_pointer
        original_fsync_directory(path)
        current = path / "current.json"
        if (
            third_party_pointer is None
            and path.name.startswith("second-reader-agent-")
            and current.is_file()
        ):
            document = json.loads(current.read_bytes())
            document["semantic_digest"] = "f" * 64
            third_party_pointer = canonical_json_bytes(document)
            current.write_bytes(third_party_pointer)

    monkeypatch.setattr(
        exporter_module,
        "_fsync_directory",
        replace_pointer_after_switch,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert third_party_pointer is not None
    current_paths = list(
        (output_dir / "public" / "annotation-packs").glob("*/current.json")
    )
    assert len(current_paths) == 1
    assert current_paths[0].read_bytes() == third_party_pointer


def test_revisions_path_symlink_swap_cannot_redirect_publication_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    outside = tmp_path / "outside-publication-target"
    outside.mkdir()
    original_ensure = exporter_module._ensure_directory_chain
    swapped = False

    def ensure_then_swap(root: Path, destination: Path) -> None:
        nonlocal swapped
        original_ensure(root, destination)
        if swapped or destination.name != "revisions":
            return
        parked = destination.parent / "parked-revisions"
        destination.rename(parked)
        destination.symlink_to(outside, target_is_directory=True)
        swapped = True

    monkeypatch.setattr(
        exporter_module,
        "_ensure_directory_chain",
        ensure_then_swap,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert swapped
    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert list(outside.iterdir()) == []
    assert not list(
        (output_dir / "public" / "annotation-packs").glob("*/current.json")
    )


def test_fsync_failure_after_pointer_replace_leaves_complete_current_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    original_fsync_directory = exporter_module._fsync_directory
    failed_after_switch = False

    def fail_once_after_pointer_switch(path: Path) -> None:
        nonlocal failed_after_switch
        if (
            not failed_after_switch
            and path.name.startswith("second-reader-agent-")
            and (path / "current.json").is_file()
        ):
            failed_after_switch = True
            raise OSError("simulated post-switch fsync failure")
        original_fsync_directory(path)

    monkeypatch.setattr(
        exporter_module,
        "_fsync_directory",
        fail_once_after_pointer_switch,
    )
    failed = _export(runtime_root, output_root, output_dir)

    assert failed.status == "failed"
    assert failed.validation.findings[0].code == "publication_write_failed"
    assert failed.validation_report is not None
    assert failed.validation_report.is_file()
    current_paths = list(
        (output_dir / "public" / "annotation-packs").glob("*/current.json")
    )
    assert len(current_paths) == 1
    pointer = json.loads(current_paths[0].read_bytes())
    selected = current_paths[0].parent / pointer["annotations_json"]
    assert selected.is_file()

    monkeypatch.setattr(
        exporter_module,
        "_fsync_directory",
        original_fsync_directory,
    )
    repeated = _export(runtime_root, output_root, output_dir)
    assert repeated.status == "unchanged"
    assert repeated.revision_id == pointer["revision_id"]


def test_track_slug_is_stable_and_safe() -> None:
    value = track_slug(
        "second-reader-agent",
        "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa",
    )
    assert value == "second-reader-agent-04ace96340ef"
    with pytest.raises(ValueError):
        track_slug("../private", "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa")


def test_unicode_and_long_existing_book_ids_are_safe_direct_children(
    tmp_path: Path,
) -> None:
    root = tmp_path / "output"
    unicode_book = root / "南腔北調集"
    long_book = root / ("可" * 90)
    unicode_book.mkdir(parents=True)
    long_book.mkdir()
    assert resolve_book_output_dir(book_id="南腔北調集", output_root=root) == unicode_book
    assert resolve_book_output_dir(book_output_dir=long_book, output_root=root) == long_book
    control_book = root / "unsafe\u0085book"
    control_book.mkdir()
    with pytest.raises(ValueError):
        resolve_book_output_dir(book_id=control_book.name, output_root=root)


def test_nonempty_input_cannot_publish_when_every_row_is_skipped(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, ledger = _fixture(tmp_path)
    broken = deepcopy(ledger)
    for row in broken["records"]:  # type: ignore[union-attr]
        row["primary_source_ref"]["resolution"]["match_count"] = 2
    reaction_records_file(output_dir).write_bytes(_json_bytes(broken))
    result = _export(
        runtime_root,
        output_root,
        output_dir,
        allow_skips=True,
        allow_empty=True,
    )
    assert result.status == "failed"
    assert any(
        finding.code == "empty_track" and finding.severity == "fatal"
        for finding in result.validation.findings
    )


def test_repeat_empty_publication_is_unchanged_without_duplicate_findings(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(
        tmp_path, records=[]
    )
    first = _export(runtime_root, output_root, output_dir, allow_empty=True)
    second = _export(runtime_root, output_root, output_dir, allow_empty=True)
    assert first.status == "published"
    assert second.status == "unchanged"
    assert [finding.code for finding in second.validation.findings] == ["empty_track"]


def test_existing_empty_revision_directory_is_never_replaced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    expected_revision = "e" * 64
    def fixed_revision(**_kwargs: object) -> str:
        return expected_revision

    monkeypatch.setattr(exporter_module, "publication_revision_id", fixed_revision)
    # Intercept the pinned no-replace syscall and create an empty colliding
    # destination through that same revisions dirfd just before rename.
    def collide(
        directory_descriptor: int,
        _source_name: str,
        destination_name: str,
    ) -> None:
        os.mkdir(destination_name, dir_fd=directory_descriptor)
        raise FileExistsError

    monkeypatch.setattr(
        exporter_module,
        "_rename_directory_noreplace_at",
        collide,
    )
    result = _export(runtime_root, output_root, output_dir)
    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    revisions = list((output_dir / "public" / "annotation-packs").glob("*/revisions/*"))
    assert len(revisions) == 1
    assert revisions[0].name == expected_revision
    assert list(revisions[0].iterdir()) == []


@pytest.mark.parametrize("corruption", ["content", "writable"])
def test_existing_detached_revision_must_match_and_remain_frozen(
    tmp_path: Path,
    corruption: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    first = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )
    assert first.current_pointer is not None
    assert first.detached_package is not None
    first.current_pointer.unlink()
    first.detached_package.chmod(0o644)
    if corruption == "content":
        first.detached_package.write_bytes(
            first.detached_package.read_bytes() + b"conflict"
        )

    result = _export(
        runtime_root,
        output_root,
        output_dir,
        deliverables="detached",
    )

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_write_failed"
    assert not first.current_pointer.exists()


def test_unexpected_guarded_export_failure_is_not_reported_as_active_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)

    def fail_internally(**_kwargs: object):  # type: ignore[no-untyped-def]
        raise RuntimeError("private internal detail")

    monkeypatch.setattr(exporter_module, "_export_under_writer_guard", fail_internally)
    result = _export(runtime_root, output_root, output_dir)
    assert result.validation.findings[0].code == "export_internal_error"
    assert "private internal detail" not in repr(result)


def test_warning_only_identity_exception_is_mapped_to_safe_fatal_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)

    def fail_identity(*_args: object, **_kwargs: object) -> None:
        raise PublicationIdentityError(
            "invalid_publication_metadata",
            "private publication title",
        )

    monkeypatch.setattr(
        exporter_module.PublicationIdentityBuilder,
        "build_verified",
        fail_identity,
    )
    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert result.validation.findings[0].code == "publication_identity_missing"
    assert "private publication title" not in repr(result)


def test_exporter_has_no_normal_runner_or_direct_mechanism_import() -> None:
    source = Path(exporter_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)

    assert not any(
        module == "src.library.runtime_truth"
        or module.startswith("src.attentional_v2")
        or module.startswith("src.reading_mechanisms")
        or module.endswith(".runner")
        for module in imported
    )


@pytest.mark.parametrize(
    ("constant", "expected_code"),
    [
        ("MAX_ANNOTATIONS_JSON_BYTES", "document_limit_exceeded"),
        ("MAX_VALIDATION_REPORT_BYTES", "validation_report_invalid"),
        ("MAX_PUBLICATION_POINTER_BYTES", "publication_write_failed"),
    ],
)
def test_export_never_publishes_an_artifact_larger_than_its_reader_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    constant: str,
    expected_code: str,
) -> None:
    runtime_root, output_root, output_dir, _ledger_value = _fixture(tmp_path)
    monkeypatch.setattr(exporter_module, constant, 1)
    result = _export(runtime_root, output_root, output_dir)
    assert result.status == "failed"
    assert result.validation.findings[0].code == expected_code
    assert result.current_pointer is None


def test_real_clis_upgrade_validate_and_inspect_detached_safe_fixture(
    tmp_path: Path,
) -> None:
    runtime_root, _output_root, output_dir, _ledger_value = _fixture(tmp_path)
    environment = {**os.environ, "BACKEND_RUNTIME_ROOT": str(runtime_root)}
    export_command = [
        sys.executable,
        str(BACKEND / "scripts" / "export_annotation_pack.py"),
        "--book-id",
        output_dir.name,
        "--track-key",
        "second-reader-agent",
        "--track-name",
        "Second Reader",
        "--creator-type",
        CREATOR.type,
        "--creator-id",
        CREATOR.id,
        "--creator-name",
        CREATOR.name,
        "--deliverables",
        "json",
    ]

    first = subprocess.run(
        export_command,
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert first.returncode == 0
    assert first.stderr == ""
    first_summary = json.loads(first.stdout)
    assert first_summary["status"] == "published"

    current_paths = list(
        (output_dir / "public" / "annotation-packs").glob("*/current.json")
    )
    assert len(current_paths) == 1
    pointer = json.loads(current_paths[0].read_bytes())
    annotations_path = current_paths[0].parent / pointer["annotations_json"]
    assert annotations_path.is_file()
    json_only_bytes = annotations_path.read_bytes()

    repeated = subprocess.run(
        export_command,
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert repeated.returncode == 0
    assert repeated.stderr == ""
    assert json.loads(repeated.stdout)["status"] == "unchanged"

    detached_command = [*export_command[:-1], "detached"]
    upgraded = subprocess.run(
        detached_command,
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert upgraded.returncode == 0
    assert upgraded.stderr == ""
    assert json.loads(upgraded.stdout)["status"] == "published"

    detached_repeat = subprocess.run(
        detached_command,
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert detached_repeat.returncode == 0
    assert detached_repeat.stderr == ""
    assert json.loads(detached_repeat.stdout)["status"] == "unchanged"

    pointer = json.loads(current_paths[0].read_bytes())
    annotations_path = current_paths[0].parent / pointer["annotations_json"]
    detached_path = current_paths[0].parent / pointer["detached_package"]
    assert annotations_path.read_bytes() == json_only_bytes
    assert detached_path.is_file()
    with zipfile.ZipFile(detached_path) as archive:
        assert archive.namelist() == ["annotations.json"]
        assert archive.read("annotations.json") == json_only_bytes

    validated = subprocess.run(
        [
            sys.executable,
            str(BACKEND / "scripts" / "validate_annotation_pack.py"),
            str(detached_path),
        ],
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    inspected = subprocess.run(
        [
            sys.executable,
            str(BACKEND / "scripts" / "inspect_annotation_pack.py"),
            str(detached_path),
        ],
        cwd=BACKEND,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert validated.returncode == 0
    assert validated.stderr == ""
    assert json.loads(validated.stdout)["status"] == "valid"
    assert inspected.returncode == 0
    assert inspected.stderr == ""
    assert json.loads(inspected.stdout)["valid"] is True

    public_output = "".join(
        (
            first.stdout,
            first.stderr,
            repeated.stdout,
            repeated.stderr,
            upgraded.stdout,
            upgraded.stderr,
            detached_repeat.stdout,
            detached_repeat.stderr,
            validated.stdout,
            validated.stderr,
            inspected.stdout,
            inspected.stderr,
        )
    )
    assert str(tmp_path) not in public_output
    assert "private-" not in public_output
    assert "durable idea" not in public_output
    assert "A return can change the question" not in public_output
