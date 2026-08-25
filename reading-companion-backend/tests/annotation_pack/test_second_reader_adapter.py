from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import traceback

import pytest

from src.annotation_pack.drafts import (
    AnnotationDraft,
    ProducerAdapterError,
    ValidationFinding,
)
from src.annotation_pack.producers import second_reader as adapter_module
from src.annotation_pack.producers.second_reader import (
    MAX_REACTION_LEDGER_BYTES,
    MAX_REACTION_LEDGER_JSON_DEPTH,
    MAX_REACTION_LEDGER_JSON_NODES,
    MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS,
    MAX_REACTION_RECORDS,
    MAX_REACTION_RECORD_CANONICAL_BYTES,
    REACTION_LEDGER_HASH_CHUNK_BYTES,
    SecondReaderProducerAdapter,
)
from src.attentional_v2.storage import reaction_records_file


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "current-reaction-records.json"
)


def _fixture_document() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _write_payload(output_dir: Path, payload: bytes) -> Path:
    path = reaction_records_file(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def _write_document(output_dir: Path, document: object) -> Path:
    return _write_payload(
        output_dir,
        json.dumps(
            document,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8"),
    )


def _load(output_dir: Path):  # type: ignore[no-untyped-def]
    return SecondReaderProducerAdapter().load_drafts(output_dir=output_dir)


def _record_digest(row: object) -> str:
    encoded = json.dumps(
        row,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    return hashlib.sha256(encoded).hexdigest()


def _public_draft_view(draft):  # type: ignore[no-untyped-def]
    return (
        draft.kind,
        draft.source_range,
        draft.source_quote,
        draft.body_text,
        draft.created_at,
        draft.source_record_index,
    )


def test_adapter_defensive_limits_are_protocol_locked() -> None:
    assert MAX_REACTION_LEDGER_BYTES == 16 * 1024 * 1024
    assert MAX_REACTION_RECORDS == 2_000
    assert MAX_REACTION_LEDGER_JSON_DEPTH == 64
    assert MAX_REACTION_LEDGER_JSON_NODES == 100_000
    assert MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS == 64 * 1024
    assert MAX_REACTION_RECORD_CANONICAL_BYTES == 128 * 1024
    assert REACTION_LEDGER_HASH_CHUNK_BYTES == 1024 * 1024


def test_neutral_draft_contract_does_not_embed_one_mechanism_version() -> None:
    names = {field.name for field in fields(AnnotationDraft)}

    assert {
        "kind",
        "source_range",
        "source_quote",
        "body_text",
        "created_at",
    }.issubset(names)
    assert {
        "mechanism_version",
        "record_source",
        "prompt",
        "memory",
    }.isdisjoint(names)


def test_adapter_loads_sanitized_current_highlight_and_note_fixture(
    tmp_path: Path,
) -> None:
    payload = FIXTURE.read_bytes()
    document = _fixture_document()
    _write_payload(tmp_path, payload)

    result = _load(tmp_path)

    assert result.input_count == 2
    assert result.reaction_ledger_sha256 == hashlib.sha256(payload).hexdigest()
    assert result.accepted_record_digests == tuple(
        _record_digest(row) for row in document["records"]
    )
    assert result.findings == ()
    assert [draft.kind for draft in result.drafts] == ["highlight", "note"]
    assert result.drafts[0].body_text is None
    assert result.drafts[1].body_text == (
        "The question redirects attention to what changes on return."
    )
    assert result.drafts[1].source_range.start.paragraph_index == 2
    assert result.drafts[1].source_range.end.paragraph_index == 3
    assert result.drafts[0].created_at == datetime(
        2026, 8, 23, 9, 1, 2, tzinfo=timezone.utc
    )
    assert result.drafts[1].created_at == datetime(
        2026, 8, 23, 9, 2, 3, tzinfo=timezone.utc
    )

    rendered = repr(result)
    for private_value in (
        "private-highlight-id",
        "private-note-id",
        "private-reconsolidation-id",
        "private-prior-id",
        "compatibility-only query",
        "section-private-1",
    ):
        assert private_value not in rendered


def test_adapter_accepts_minimal_current_native_highlight_and_note_rows(
    tmp_path: Path,
) -> None:
    document = _fixture_document()
    minimal_rows = []
    for original in document["records"]:
        primary_ref = original["primary_source_ref"]
        source_span = primary_ref["source_span"]
        row = {
            "record_source": original["record_source"],
            "marginalia_kind": original["marginalia_kind"],
            "source_quote": original["source_quote"],
            "primary_source_ref": {
                "source_span": {
                    "start_cursor": {
                        key: source_span["start_cursor"][key]
                        for key in ("chapter_id", "paragraph_index", "char_offset")
                    },
                    "end_cursor": {
                        key: source_span["end_cursor"][key]
                        for key in ("chapter_id", "paragraph_index", "char_offset")
                    },
                },
                "quote": primary_ref["quote"],
                "resolution": primary_ref["resolution"],
            },
            "created_at": original["created_at"],
        }
        if original["marginalia_kind"] == "note":
            row["thought"] = original["thought"]
        minimal_rows.append(row)
    document["records"] = minimal_rows
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert result.findings == ()
    assert [draft.kind for draft in result.drafts] == ["highlight", "note"]
    assert result.drafts[0].body_text is None
    assert result.drafts[1].body_text == (
        "The question redirects attention to what changes on return."
    )
    assert result.drafts[0].source_range.start.chapter_id == 1
    assert result.drafts[1].source_range.end.paragraph_index == 3


def test_note_kind_uses_native_discriminator_and_ignores_compat_values(
    tmp_path: Path,
) -> None:
    original = _fixture_document()
    changed = deepcopy(original)
    note = changed["records"][1]
    note["type"] = "highlight"
    note["compat_family"] = "highlight"
    note["reaction_id"] = "/Users/alice/private-reaction-id"
    note["prior_link"] = {"arbitrary": [1, 2, 3]}
    note["search_results"] = [{"score": 0.25}]

    _write_document(tmp_path / "original", original)
    _write_document(tmp_path / "changed", changed)
    original_result = _load(tmp_path / "original")
    changed_result = _load(tmp_path / "changed")

    assert changed_result.drafts[1].kind == "note"
    assert _public_draft_view(changed_result.drafts[1]) == _public_draft_view(
        original_result.drafts[1]
    )
    assert (
        changed_result.accepted_record_digests[1]
        != original_result.accepted_record_digests[1]
    )
    assert "/Users/alice" not in repr(changed_result)


def test_known_private_and_compatibility_fields_are_ignored_even_when_opaque(
    tmp_path: Path,
) -> None:
    original = _fixture_document()
    changed = deepcopy(original)
    changed_row = changed["records"][0]
    changed_row["chapter_id"] = {"private": "row chapter id"}
    changed_row["chapter_ref"] = ["private row chapter ref"]
    primary_ref = changed_row["primary_source_ref"]
    primary_ref["source_span_id"] = {"private": "source span id"}
    primary_ref["role"] = ["private role"]
    span = primary_ref["source_span"]
    span["start_cursor"]["chapter_ref"] = {"private": "start ref"}
    span["end_cursor"]["chapter_ref"] = ["private end ref"]

    _write_document(tmp_path / "original", original)
    _write_document(tmp_path / "changed", changed)
    original_result = _load(tmp_path / "original")
    changed_result = _load(tmp_path / "changed")

    assert changed_result.findings == ()
    assert _public_draft_view(changed_result.drafts[0]) == _public_draft_view(
        original_result.drafts[0]
    )
    assert "private row chapter ref" not in repr(changed_result)


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda row: row.pop("marginalia_kind"), "unsupported_legacy_record"),
        (lambda row: row.update(marginalia_kind="bookmark"), "unsupported_kind"),
        (lambda row: row.update(marginalia_kind=[]), "unsupported_kind"),
        (lambda row: row.update(record_source="legacy_builder"), "unsupported_legacy_record"),
        (lambda row: row.update(record_source=[]), "unsupported_legacy_record"),
        (lambda row: row.update(thought="fabricated note"), "highlight_body_present"),
        (lambda row: row.update(thought=None), "highlight_body_present"),
        (lambda row: row.update(created_at="2026-08-23T09:01:02+00:00"), "invalid_annotation_timestamp"),
        (lambda row: row["primary_source_ref"]["resolution"].update(status="fallback_unit_span"), "unresolved_source_quote"),
        (lambda row: row["primary_source_ref"]["resolution"].update(status=[]), "unresolved_source_quote"),
        (lambda row: row["primary_source_ref"]["resolution"].update(status="ambiguous_first_match", match_count=2), "ambiguous_source_quote"),
        (lambda row: row.update(source_quote="different quote"), "unresolved_source_quote"),
        (lambda row: row["primary_source_ref"].update(quote=[]), "unresolved_source_quote"),
        (lambda row: row.update(private_extension="not current"), "unsupported_legacy_record"),
        (lambda row: row["primary_source_ref"].update(private_extension="not current"), "unsupported_legacy_record"),
        (lambda row: row["primary_source_ref"]["source_span"].update(private_extension="not current"), "malformed_source_span"),
        (lambda row: row["primary_source_ref"]["source_span"]["start_cursor"].update(private_extension="not current"), "malformed_source_span"),
        (lambda row: row["primary_source_ref"]["source_span"]["start_cursor"].update(char_offset=True), "malformed_source_span"),
        (lambda row: row["primary_source_ref"]["source_span"]["end_cursor"].update(chapter_id=2), "malformed_source_span"),
    ],
)
def test_adapter_rejects_non_current_or_invalid_rows_without_repair(
    tmp_path: Path,
    mutation,  # type: ignore[no-untyped-def]
    code: str,
) -> None:
    document = _fixture_document()
    document["records"] = [document["records"][0]]
    mutation(document["records"][0])
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert result.input_count == 1
    assert result.drafts == ()
    assert result.accepted_record_digests == ()
    assert len(result.findings) == 1
    assert result.findings[0].code == code
    assert result.findings[0].severity == "error"
    assert result.findings[0].source_record_index == 0
    assert result.findings[0].source_record_digest == _record_digest(
        document["records"][0]
    )


def test_old_primary_anchor_shape_is_not_upgraded(tmp_path: Path) -> None:
    document = _fixture_document()
    row = document["records"][0]
    row["primary_anchor"] = row.pop("primary_source_ref")
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert [finding.code for finding in result.findings] == [
        "unsupported_legacy_record"
    ]
    assert result.drafts[0].kind == "note"


def test_mixed_ledger_counts_all_rows_but_only_digests_accepted_drafts(
    tmp_path: Path,
) -> None:
    document = _fixture_document()
    document["records"][0].pop("marginalia_kind")
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert result.input_count == 2
    assert len(result.drafts) == 1
    assert result.drafts[0].source_record_index == 1
    assert result.accepted_record_digests == (
        _record_digest(document["records"][1]),
    )
    assert [finding.code for finding in result.findings] == [
        "unsupported_legacy_record"
    ]


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-08-23T09:01:02Z",
        "2026-08-23T09:01:02.1Z",
        "2026-08-23T09:01:02.123456Z",
    ],
)
def test_timestamp_accepts_zero_to_six_fraction_digits_and_truncates(
    tmp_path: Path,
    timestamp: str,
) -> None:
    document = _fixture_document()
    document["records"] = [document["records"][0]]
    document["records"][0]["created_at"] = timestamp
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert result.findings == ()
    assert result.drafts[0].created_at == datetime(
        2026, 8, 23, 9, 1, 2, tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-08-23T09:01:02",
        "2026-08-23T09:01:02+00:00",
        "2026-08-23T09:01:02.1234567Z",
        "2026-08-23t09:01:02z",
    ],
)
def test_timestamp_rejects_non_z_naive_and_overprecision(
    tmp_path: Path,
    timestamp: str,
) -> None:
    document = _fixture_document()
    document["records"] = [document["records"][0]]
    document["records"][0]["created_at"] = timestamp
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert [finding.code for finding in result.findings] == [
        "invalid_annotation_timestamp"
    ]


def test_phase8_envelope_is_fatal_and_not_migrated(tmp_path: Path) -> None:
    document = _fixture_document()
    document["mechanism_version"] = "attentional_v2-phase8"
    _write_document(tmp_path, document)

    with pytest.raises(ProducerAdapterError) as caught:
        _load(tmp_path)

    assert caught.value.code == "reaction_ledger_schema_unsupported"
    assert caught.value.finding.severity == "fatal"


def test_note_body_is_nfc_normalized_before_the_code_point_limit(
    tmp_path: Path,
) -> None:
    document = _fixture_document()
    note = document["records"][1]
    note["thought"] = "e\u0301" * 9_000
    document["records"] = [note]
    _write_document(tmp_path, document)

    result = _load(tmp_path)

    assert result.findings == ()
    assert result.drafts[0].body_text == "\u00e9" * 9_000
    assert len(result.drafts[0].body_text) == 9_000


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"\xef\xbb\xbf{}", "reaction_ledger_invalid_json"),
        (
            b'{"schema_version":1,"schema_version":1}',
            "reaction_ledger_invalid_json",
        ),
        (b'{"value":NaN}', "reaction_ledger_invalid_json"),
        (b"\xff", "reaction_ledger_invalid_json"),
    ],
)
def test_strict_json_rejects_bom_duplicate_keys_nan_and_invalid_utf8(
    tmp_path: Path,
    payload: bytes,
    code: str,
) -> None:
    _write_payload(tmp_path, payload)

    with pytest.raises(ProducerAdapterError) as caught:
        _load(tmp_path)

    assert caught.value.code == code
    assert caught.value.finding.severity == "fatal"
    assert caught.value.__cause__ is None


@pytest.mark.parametrize(
    "mutation",
    [
        lambda document: document.update(schema_version=True),
        lambda document: document.update(schema_version=2),
        lambda document: document.update(mechanism_version="attentional_v2-phase8"),
        lambda document: document.update(updated_at="2026-08-23T09:00:00+00:00"),
        lambda document: document.update(extra={}),
        lambda document: document.pop("updated_at"),
    ],
)
def test_envelope_requires_exact_current_schema_and_key_set(
    tmp_path: Path,
    mutation,  # type: ignore[no-untyped-def]
) -> None:
    document = _fixture_document()
    mutation(document)
    _write_document(tmp_path, document)

    with pytest.raises(ProducerAdapterError) as caught:
        _load(tmp_path)

    assert caught.value.code == "reaction_ledger_schema_unsupported"


def test_adapter_requires_nofollow_regular_file(tmp_path: Path) -> None:
    target_dir = tmp_path / "target"
    target_path = _write_payload(target_dir, FIXTURE.read_bytes())
    link_path = reaction_records_file(tmp_path / "link")
    link_path.parent.mkdir(parents=True)
    link_path.symlink_to(target_path)

    with pytest.raises(ProducerAdapterError) as symlink_error:
        _load(tmp_path / "link")
    assert symlink_error.value.code == "reaction_ledger_unavailable"

    fifo_path = reaction_records_file(tmp_path / "fifo")
    fifo_path.parent.mkdir(parents=True)
    os.mkfifo(fifo_path)
    with pytest.raises(ProducerAdapterError) as fifo_error:
        _load(tmp_path / "fifo")
    assert fifo_error.value.code == "reaction_ledger_unavailable"

    real_parent = tmp_path / "real-parent"
    _write_payload(real_parent / "book", FIXTURE.read_bytes())
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    with pytest.raises(ProducerAdapterError) as parent_error:
        _load(linked_parent / "book")
    assert parent_error.value.code == "reaction_ledger_unavailable"


def test_read_before_after_stat_detects_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_payload(tmp_path, FIXTURE.read_bytes())
    real_fstat = adapter_module.os.fstat
    calls = 0

    class ChangedStat:
        def __init__(self, original):  # type: ignore[no-untyped-def]
            self._original = original

        def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
            if name == "st_mtime_ns":
                return self._original.st_mtime_ns + 1
            return getattr(self._original, name)

    def changed_fstat(descriptor: int):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        result = real_fstat(descriptor)
        return ChangedStat(result) if calls == 2 else result

    monkeypatch.setattr(adapter_module.os, "fstat", changed_fstat)

    with pytest.raises(ProducerAdapterError) as caught:
        _load(tmp_path)

    assert calls == 3
    assert caught.value.code == "input_changed_during_export"


def test_read_rejects_pathname_replacement_even_when_open_fd_is_stable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_path = _write_payload(tmp_path, FIXTURE.read_bytes())
    runtime_dir = ledger_path.parent
    moved_runtime_dir = runtime_dir.with_name("runtime-before-replacement")
    real_read = adapter_module.os.read
    replaced = False

    def replacing_read(descriptor: int, size: int) -> bytes:
        nonlocal replaced
        chunk = real_read(descriptor, size)
        if chunk and not replaced:
            replaced = True
            runtime_dir.rename(moved_runtime_dir)
            runtime_dir.mkdir()
            (runtime_dir / ledger_path.name).write_bytes(FIXTURE.read_bytes())
        return chunk

    monkeypatch.setattr(adapter_module.os, "read", replacing_read)

    with pytest.raises(ProducerAdapterError) as caught:
        _load(tmp_path)

    assert replaced is True
    assert caught.value.code == "input_changed_during_export"


def test_ledger_and_structure_limits_are_fatal_not_row_skips(
    tmp_path: Path,
) -> None:
    oversized_path = reaction_records_file(tmp_path / "bytes")
    oversized_path.parent.mkdir(parents=True)
    with oversized_path.open("wb") as stream:
        stream.truncate(MAX_REACTION_LEDGER_BYTES + 1)
    with pytest.raises(ProducerAdapterError) as byte_error:
        _load(tmp_path / "bytes")
    assert byte_error.value.code == "reaction_ledger_limit_exceeded"
    assert byte_error.value.finding.severity == "fatal"

    too_many = _fixture_document()
    too_many["records"] = [{} for _ in range(MAX_REACTION_RECORDS + 1)]
    _write_document(tmp_path / "records", too_many)
    with pytest.raises(ProducerAdapterError) as count_error:
        _load(tmp_path / "records")
    assert count_error.value.code == "reaction_ledger_limit_exceeded"

    too_long = _fixture_document()
    too_long["records"][0]["search_query"] = "x" * (
        MAX_REACTION_LEDGER_SINGLE_STRING_CODE_POINTS + 1
    )
    _write_document(tmp_path / "string", too_long)
    with pytest.raises(ProducerAdapterError) as string_error:
        _load(tmp_path / "string")
    assert string_error.value.code == "reaction_ledger_limit_exceeded"

    oversized_row = _fixture_document()
    oversized_row["records"] = [oversized_row["records"][0]]
    oversized_row["records"][0]["search_query"] = "x" * 65_536
    oversized_row["records"][0]["compatibility_section_ref"] = "y" * 65_536
    _write_document(tmp_path / "row", oversized_row)
    with pytest.raises(ProducerAdapterError) as row_error:
        _load(tmp_path / "row")
    assert row_error.value.code == "reaction_ledger_limit_exceeded"

    deep_payload = (
        b'{"value":'
        + (b"[" * MAX_REACTION_LEDGER_JSON_DEPTH)
        + b"0"
        + (b"]" * MAX_REACTION_LEDGER_JSON_DEPTH)
        + b"}"
    )
    _write_payload(tmp_path / "depth", deep_payload)
    with pytest.raises(ProducerAdapterError) as depth_error:
        _load(tmp_path / "depth")
    assert depth_error.value.code == "reaction_ledger_limit_exceeded"

    node_payload = b'{"values":[' + b",".join(
        b"null" for _ in range(MAX_REACTION_LEDGER_JSON_NODES)
    ) + b"]}"
    _write_payload(tmp_path / "nodes", node_payload)
    with pytest.raises(ProducerAdapterError) as node_error:
        _load(tmp_path / "nodes")
    assert node_error.value.code == "reaction_ledger_limit_exceeded"


def test_adapter_errors_and_findings_never_echo_path_or_payload(
    tmp_path: Path,
) -> None:
    private_path = tmp_path / "Users" / "alice" / "private-book-title"
    _write_payload(
        private_path,
        b'{"secret":"DO-NOT-ECHO","secret":"DO-NOT-ECHO"}',
    )

    with pytest.raises(ProducerAdapterError) as caught:
        _load(private_path)

    rendered = "".join(traceback.format_exception(caught.value))
    rendered += repr(caught.value.finding)
    assert str(private_path) not in rendered
    assert "DO-NOT-ECHO" not in rendered
    assert "secret" not in rendered.lower()


def test_producer_adapter_error_rebuilds_catalog_finding_from_safe_code_only() -> None:
    class HostileFinding(ValidationFinding):
        pass

    forged = ValidationFinding(
        code="reaction_ledger_unavailable",
        severity="fatal",
        message="/Users/alice/private-ledger.json",
        json_pointer="/Users/alice/private-ledger.json",
    )
    hostile = HostileFinding(
        code="reaction_ledger_unavailable",
        severity="fatal",
        message="/Users/alice/private-ledger.json",
    )

    for untrusted in (forged, hostile):
        with pytest.raises(TypeError, match="safe fatal code") as caught:
            ProducerAdapterError(untrusted)  # type: ignore[arg-type]
        assert "/Users/alice" not in str(caught.value)

    safe = ProducerAdapterError("reaction_ledger_unavailable")
    rendered = f"{safe!s} {safe!r} {safe.finding!r}"
    assert "/Users/alice" not in rendered
    assert safe.finding.message == (
        "The producer reaction ledger is unavailable or unsafe to read."
    )


def test_adapter_has_one_explicit_mechanism_path_import() -> None:
    source = Path(adapter_module.__file__).read_text(encoding="utf-8")
    imports = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and "attentional_v2" in ast.unparse(node)
    ]

    assert len(imports) == 1
    assert ast.unparse(imports[0]) == (
        "from src.attentional_v2.storage import reaction_records_file"
    )
