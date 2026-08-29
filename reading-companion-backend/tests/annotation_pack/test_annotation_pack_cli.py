from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import os
import sys
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


BACKEND = Path(__file__).resolve().parents[2]
WORKSPACE = BACKEND.parent
EXAMPLES = WORKSPACE / "contract/annotation-pack/v0/examples"


def _load_script(filename: str) -> Any:
    module_name = f"_annotation_pack_cli_test_{filename.replace('.', '_')}"
    specification = importlib.util.spec_from_file_location(
        module_name,
        BACKEND / "scripts" / filename,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[module_name] = module
    specification.loader.exec_module(module)
    return module


VALIDATE_CLI = _load_script("validate_annotation_pack.py")
EXPORT_CLI = _load_script("export_annotation_pack.py")
INSPECT_CLI = _load_script("inspect_annotation_pack.py")

PACK_ID = "urn:uuid:31f414c4-32f3-50d6-85e1-9382e47c6390"
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64
PRIVATE_TEXT = "/Users/alice/private/reaction-secret-note.txt"


def _summary(stream: str) -> dict[str, Any]:
    lines = stream.splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


def _valid_pack() -> dict[str, Any]:
    return json.loads((EXAMPLES / "minimal-pack.json").read_text(encoding="utf-8"))


def _export_args(*, deliverables: str | None = "json") -> list[str]:
    values = [
        "--book-id",
        "safe-book-id",
        "--track-key",
        "second-reader-agent",
        "--track-name",
        "Second Reader",
        "--creator-type",
        "Software",
        "--creator-id",
        "urn:uuid:c8d82077-7433-5fe9-9075-01f3e3100656",
        "--creator-name",
        "Second Reader",
        "--allow-partial",
        "--allow-skips",
        "--allow-empty",
        "--force-regenerate",
    ]
    if deliverables is not None:
        values.extend(("--deliverables", deliverables))
    return values


class _FakePolicy:
    def __init__(self, **values: object) -> None:
        self.__dict__.update(values)


def _validation(*, failed: bool = False) -> SimpleNamespace:
    finding = SimpleNamespace(
        code=(
            "deliverable_not_implemented" if failed else "quote_not_unique_in_resource"
        ),
        severity="fatal" if failed else "warning",
        source_record_index=None if failed else 3,
        source_record_digest=None if failed else DIGEST_C,
        message=PRIVATE_TEXT,
        json_pointer=PRIVATE_TEXT,
        annotation_id="urn:uuid:reaction-private",
    )
    return SimpleNamespace(
        status="failed" if failed else "valid",
        pack_id=None if failed else PACK_ID,
        semantic_digest=None if failed else DIGEST_A,
        input_snapshot_digest=None if failed else DIGEST_B,
        input_count=2,
        exported_count=0 if failed else 2,
        skipped_count=2 if failed else 0,
        warning_count=0 if failed else 1,
        error_count=1 if failed else 0,
        findings=(finding,),
    )


def _fake_exporter(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[ModuleType, dict[str, Any]]:
    module = ModuleType("src.annotation_pack.exporter")
    calls: dict[str, Any] = {}

    def resolve_book_output_dir(**values: object) -> Path:
        calls["resolve"] = values
        return Path("/isolated/output/safe-book-id")

    def export_annotation_pack(**values: object) -> SimpleNamespace:
        calls["export"] = values
        policy = values["policy"]
        return SimpleNamespace(
            status="published",
            pack=None,
            annotations_json=None,
            detached_package=(
                Path("/isolated/public/pack.annotations")
                if policy.deliverables == "detached"
                else None
            ),
            validation=_validation(),
            validation_report=None,
            current_pointer=None,
            revision_id=DIGEST_C,
        )

    module.ExportPolicy = _FakePolicy
    module.resolve_book_output_dir = resolve_book_output_dir
    module.export_annotation_pack = export_annotation_pack
    monkeypatch.setitem(sys.modules, "src.annotation_pack.exporter", module)
    return module, calls


def test_export_cli_json_success_and_independent_policy_flags(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _module, calls = _fake_exporter(monkeypatch)

    assert EXPORT_CLI.main(_export_args()) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    summary = _summary(captured.out)
    assert summary == {
        "counts": {
            "errors": 0,
            "exported": 2,
            "input": 2,
            "skipped": 0,
            "warnings": 1,
        },
        "findings": [
            {
                "code": "quote_not_unique_in_resource",
                "severity": "warning",
                "source_record_digest": DIGEST_C,
                "source_record_index": 3,
            }
        ],
        "input_snapshot_digest": DIGEST_B,
        "pack_id": PACK_ID,
        "revision_id": DIGEST_C,
        "semantic_digest": DIGEST_A,
        "status": "published",
    }
    assert PRIVATE_TEXT not in captured.out
    assert calls["resolve"] == {
        "book_id": "safe-book-id",
        "book_output_dir": None,
    }
    assert calls["export"]["track_name"] == "Second Reader"
    assert calls["export"]["producer_format"] == "reading-product-v1"
    policy = calls["export"]["policy"]
    assert policy.deliverables == "json"
    assert policy.allow_partial is True
    assert policy.allow_skips is True
    assert policy.allow_empty is True
    assert policy.force_regenerate is True


def test_export_cli_detached_succeeds_without_downgrade(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _module, calls = _fake_exporter(monkeypatch)

    assert EXPORT_CLI.main(_export_args(deliverables="detached")) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    summary = _summary(captured.out)
    assert summary["status"] == "published"
    assert calls["export"]["policy"].deliverables == "detached"
    assert PRIVATE_TEXT not in captured.out


def test_export_cli_defaults_to_detached(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _module, calls = _fake_exporter(monkeypatch)

    assert EXPORT_CLI.main(_export_args(deliverables=None)) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert _summary(captured.out)["status"] == "published"
    assert calls["export"]["policy"].deliverables == "detached"


def test_export_summary_never_reads_legacy_public_digest_or_provenance() -> None:
    validation = _validation()
    validation.semantic_digest = None
    validation.input_snapshot_digest = None
    result = SimpleNamespace(
        status="published",
        pack={
            "id": PACK_ID,
            "sr:semanticDigest": {"sr:value": DIGEST_A},
            "sr:provenance": {
                "sr:inputSnapshotDigest": {"sr:value": DIGEST_B},
            },
        },
        validation=validation,
        revision_id=DIGEST_C,
    )

    summary = EXPORT_CLI._result_summary(result)

    assert summary["pack_id"] == PACK_ID
    assert summary["semantic_digest"] is None
    assert summary["input_snapshot_digest"] is None


def test_export_cli_unexpected_error_is_fixed_and_private_safe(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = ModuleType("src.annotation_pack.exporter")
    module.ExportPolicy = _FakePolicy
    module.resolve_book_output_dir = lambda **_kwargs: (_ for _ in ()).throw(
        RuntimeError(PRIVATE_TEXT)
    )
    module.export_annotation_pack = lambda **_kwargs: None
    monkeypatch.setitem(sys.modules, "src.annotation_pack.exporter", module)

    assert EXPORT_CLI.main(_export_args()) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert _summary(captured.err)["findings"][0]["code"] == (
        "unexpected_internal_error"
    )
    assert PRIVATE_TEXT not in captured.err


def test_export_cli_expected_path_rejection_has_fixed_code(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = ModuleType("src.annotation_pack.exporter")
    module.ExportPolicy = _FakePolicy
    module.resolve_book_output_dir = lambda **_kwargs: (_ for _ in ()).throw(
        ValueError(PRIVATE_TEXT)
    )
    module.export_annotation_pack = lambda **_kwargs: None
    monkeypatch.setitem(sys.modules, "src.annotation_pack.exporter", module)

    assert EXPORT_CLI.main(_export_args()) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert _summary(captured.err)["findings"][0]["code"] == "output_path_invalid"
    assert PRIVATE_TEXT not in captured.err


def test_cli_finding_sanitizers_accept_only_catalog_codes() -> None:
    hostile = SimpleNamespace(
        code="users_alice_private_secret",
        severity="warning",
        source_record_index=1,
        source_record_digest=DIGEST_A,
    )

    for module in (EXPORT_CLI, INSPECT_CLI, VALIDATE_CLI):
        finding = module._safe_finding(hostile)
        assert finding["code"] == "invalid_finding"
        assert PRIVATE_TEXT not in json.dumps(finding)


def test_export_cli_requires_exactly_one_book_locator() -> None:
    with pytest.raises(SystemExit) as missing:
        EXPORT_CLI.main([])
    assert missing.value.code == 2

    with pytest.raises(SystemExit) as both:
        EXPORT_CLI.main(
            _export_args() + ["--book-output-dir", "/isolated/output/safe-book-id"]
        )
    assert both.value.code == 2


def test_inspect_cli_outputs_only_fixed_safe_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = ModuleType("src.annotation_pack.exporter")

    def inspect_annotation_pack(_source: Path) -> SimpleNamespace:
        return SimpleNamespace(
            valid=True,
            pack_id=PACK_ID,
            track_id=None,
            semantic_digest=DIGEST_A,
            item_counts={"total": 2, "highlight": 1, "note": 1},
            anchor_capabilities=(
                "TextPositionSelector",
                "TextQuoteSelector",
            ),
            findings=(
                SimpleNamespace(
                    code="quote_not_unique_in_resource",
                    severity="warning",
                    source_record_index=None,
                    source_record_digest=None,
                    message=PRIVATE_TEXT,
                    json_pointer=PRIVATE_TEXT,
                ),
            ),
        )

    module.inspect_annotation_pack = inspect_annotation_pack
    monkeypatch.setitem(sys.modules, "src.annotation_pack.exporter", module)
    source = tmp_path / "private-reaction-name.json"

    assert INSPECT_CLI.main([str(source)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    summary = _summary(captured.out)
    assert summary["valid"] is True
    assert summary["item_counts"] == {"highlight": 1, "note": 1, "total": 2}
    assert summary["anchor_capabilities"] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]
    assert summary["track_id"] is None
    assert set(summary["findings"][0]) == {
        "code",
        "severity",
        "source_record_index",
        "source_record_digest",
    }
    assert PRIVATE_TEXT not in captured.out
    assert str(source) not in captured.out


def test_inspect_cli_fails_closed_on_non_protocol_summary_fields(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = ModuleType("src.annotation_pack.exporter")
    module.inspect_annotation_pack = lambda _source: SimpleNamespace(
        valid=True,
        pack_id=PACK_ID,
        track_id=None,
        semantic_digest=DIGEST_A,
        item_counts={"total": 0, "highlight": 0, "note": 0, PRIVATE_TEXT: 1},
        anchor_capabilities=(PRIVATE_TEXT,),
        findings=(),
    )
    monkeypatch.setitem(sys.modules, "src.annotation_pack.exporter", module)

    assert INSPECT_CLI.main([PRIVATE_TEXT]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert _summary(captured.err)["findings"][0]["code"] == (
        "unexpected_internal_error"
    )
    assert PRIVATE_TEXT not in captured.err


def test_inspect_cli_uses_real_safe_inspector_for_canonical_pack(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.serialization import canonical_json_bytes

    source = tmp_path / "annotations.json"
    source.write_bytes(canonical_json_bytes(_valid_pack()))

    assert INSPECT_CLI.main([str(source)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    summary = _summary(captured.out)
    assert summary["valid"] is True
    assert summary["pack_id"] is not None
    assert summary["item_counts"] == {"highlight": 1, "note": 1, "total": 2}
    assert summary["anchor_capabilities"] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]
    assert summary["track_id"] is None
    assert str(source) not in captured.out


def test_validate_and_inspect_clis_accept_independent_detached_package(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.packaging import build_detached_annotations
    from src.annotation_pack.serialization import canonical_json_bytes

    json_bytes = canonical_json_bytes(_valid_pack())
    package = build_detached_annotations(json_bytes)
    source = tmp_path / "public-safe.annotations"
    source.write_bytes(package.package_bytes)
    json_source = tmp_path / "annotations.json"
    json_source.write_bytes(json_bytes)

    assert VALIDATE_CLI.main([str(source)]) == 0
    validation_output = capsys.readouterr()
    assert validation_output.err == ""
    assert _summary(validation_output.out)["status"] == "valid"

    assert VALIDATE_CLI.main(["--schema-only", str(source)]) == 0
    schema_output = capsys.readouterr()
    assert schema_output.err == ""
    assert _summary(schema_output.out)["status"] == "valid"

    assert INSPECT_CLI.main([str(source)]) == 0
    inspection_output = capsys.readouterr()
    assert inspection_output.err == ""
    summary = _summary(inspection_output.out)
    assert summary["valid"] is True
    assert summary["item_counts"] == {"highlight": 1, "note": 1, "total": 2}
    assert str(source) not in inspection_output.out

    assert INSPECT_CLI.main([str(json_source)]) == 0
    json_inspection_output = capsys.readouterr()
    assert json_inspection_output.err == ""
    assert _summary(json_inspection_output.out) == summary


def test_detached_empty_pack_still_requires_validate_cli_allow_empty(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.packaging import build_detached_annotations
    from src.annotation_pack.serialization import canonical_json_bytes

    pack = _valid_pack()
    pack["items"] = []
    source = tmp_path / "empty.annotations"
    source.write_bytes(
        build_detached_annotations(canonical_json_bytes(pack)).package_bytes
    )

    assert VALIDATE_CLI.main([str(source)]) == 1
    rejected = capsys.readouterr()
    assert _summary(rejected.err)["findings"][0]["code"] == "empty_track"

    assert VALIDATE_CLI.main(["--allow-empty", str(source)]) == 0
    accepted = capsys.readouterr()
    assert accepted.err == ""
    assert _summary(accepted.out)["findings"][0]["code"] == "empty_track"


def test_inspect_cli_preserves_safe_invalid_summary_when_counts_include_bad_rows(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.serialization import canonical_json_bytes

    pack = _valid_pack()
    pack["items"][0]["motivation"] = "private-invalid-kind"
    source = tmp_path / "invalid-annotations.json"
    source.write_bytes(canonical_json_bytes(pack))

    assert INSPECT_CLI.main([str(source)]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    summary = _summary(captured.err)
    assert summary["valid"] is False
    assert summary["item_counts"]["total"] == 2
    assert (
        summary["item_counts"]["highlight"] + summary["item_counts"]["note"]
        < summary["item_counts"]["total"]
    )
    assert any(
        finding["code"] in {"schema_validation_failed", "unsupported_kind"}
        for finding in summary["findings"]
    )
    assert "private-invalid-kind" not in captured.err


def test_validate_cli_schema_only_annotation_and_default_semantic_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    annotation = EXAMPLES / "highlight.annotation.json"

    assert VALIDATE_CLI.main(["--schema-only", str(annotation)]) == 0
    schema_output = capsys.readouterr()
    assert schema_output.err == ""
    assert _summary(schema_output.out)["status"] == "valid"

    assert VALIDATE_CLI.main([str(annotation)]) == 1
    semantic_output = capsys.readouterr()
    assert semantic_output.out == ""
    assert _summary(semantic_output.err)["findings"][0]["code"] == (
        "schema_only_required"
    )


def test_validate_cli_default_runs_full_pack_semantics(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.serialization import canonical_json_bytes

    source = tmp_path / "annotations.json"
    pack = _valid_pack()
    source.write_bytes(canonical_json_bytes(pack))

    assert VALIDATE_CLI.main([str(source)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    summary = _summary(captured.out)
    assert summary["mode"] == "semantic"
    assert summary["status"] == "valid"
    assert summary["counts"]["exported"] == 2
    assert summary["semantic_digest"] is not None
    assert len(summary["semantic_digest"]) == 64


def test_validate_cli_rejects_noncanonical_semantic_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "annotations.json"
    source.write_text(json.dumps(_valid_pack()), encoding="utf-8")

    assert VALIDATE_CLI.main([str(source)]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert _summary(captured.err)["findings"][0]["code"] == "noncanonical_json"


def test_validate_cli_empty_semantics_require_explicit_allow_empty(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.annotation_pack.serialization import canonical_json_bytes

    pack = _valid_pack()
    pack["items"] = []
    source = tmp_path / "empty-annotations.json"
    source.write_bytes(canonical_json_bytes(pack))

    assert VALIDATE_CLI.main([str(source)]) == 1
    rejected = capsys.readouterr()
    assert _summary(rejected.err)["findings"][0]["code"] == "empty_track"

    assert VALIDATE_CLI.main(["--allow-empty", str(source)]) == 0
    accepted = capsys.readouterr()
    assert accepted.err == ""
    summary = _summary(accepted.out)
    assert summary["status"] == "valid"
    assert summary["counts"]["warnings"] == 1
    assert summary["findings"][0]["code"] == "empty_track"


def test_validate_cli_schema_only_and_allow_empty_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit) as error:
        VALIDATE_CLI.main(
            [
                "--schema-only",
                "--allow-empty",
                str(EXAMPLES / "minimal-pack.json"),
            ]
        )
    assert error.value.code == 2


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"{", "invalid_json"),
        (b"\xef\xbb\xbf{}", "utf8_bom_forbidden"),
        (b'{"type":"AnnotationSet",\xff}', "invalid_utf8"),
        (
            b'{"type":"AnnotationSet","type":"AnnotationSet"}',
            "duplicate_json_key",
        ),
        (b'{"type":"AnnotationSet","value":NaN}', "nonfinite_json_number"),
        (b'{"type":"AnnotationSet","value":Infinity}', "nonfinite_json_number"),
    ],
)
def test_validate_cli_rejects_unsafe_json_with_fixed_private_safe_codes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    payload: bytes,
    code: str,
) -> None:
    source = tmp_path / "private-reaction-secret.json"
    source.write_bytes(payload)

    assert VALIDATE_CLI.main([str(source)]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert _summary(captured.err)["findings"][0]["code"] == code
    assert str(source) not in captured.err
    assert "reaction-secret" not in captured.err


def test_validate_cli_routes_each_multi_source_summary_to_its_own_stream(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    valid = EXAMPLES / "highlight.annotation.json"
    invalid = tmp_path / "invalid-private.json"
    invalid.write_bytes(b"{")

    assert VALIDATE_CLI.main(["--schema-only", str(valid), str(invalid)]) == 1

    captured = capsys.readouterr()
    assert _summary(captured.out)["status"] == "valid"
    assert _summary(captured.err)["findings"][0]["code"] == "invalid_json"
    assert str(invalid) not in captured.err


def test_validate_cli_rejects_leaf_and_parent_symlinks(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    source = real_parent / "annotations.json"
    source.write_text("{}", encoding="utf-8")
    leaf_link = tmp_path / "leaf-link.json"
    leaf_link.symlink_to(source)
    parent_link = tmp_path / "parent-link"
    parent_link.symlink_to(real_parent, target_is_directory=True)

    for unsafe_source in (leaf_link, parent_link / source.name):
        assert VALIDATE_CLI.main(["--schema-only", str(unsafe_source)]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert _summary(captured.err)["findings"][0]["code"] == ("source_unavailable")
        assert str(unsafe_source) not in captured.err


def test_validate_cli_rejects_pathname_swap_after_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "annotations.json"
    replacement = tmp_path / "replacement.json"
    source.write_text('{"type":"AnnotationSet"}', encoding="utf-8")
    replacement.write_text('{"type":"AnnotationSet"}', encoding="utf-8")
    original_open = VALIDATE_CLI._open_all_components_nofollow
    calls = 0

    def switched_open(path: Path) -> int:
        nonlocal calls
        calls += 1
        return original_open(source if calls == 1 else replacement)

    monkeypatch.setattr(VALIDATE_CLI, "_open_all_components_nofollow", switched_open)

    summary = VALIDATE_CLI.validate_path(source, schema_only=True)

    assert summary["status"] == "failed"
    assert summary["findings"][0]["code"] == "source_changed_during_read"


def test_validate_cli_applies_bounded_json_shape_limits(tmp_path: Path) -> None:
    value: object = "leaf"
    for _ in range(VALIDATE_CLI.MAX_ANNOTATION_PACK_JSON_DEPTH + 1):
        value = {"nested": value}
    source = tmp_path / "too-deep.json"
    source.write_text(json.dumps(value), encoding="utf-8")

    summary = VALIDATE_CLI.validate_path(source, schema_only=True)

    assert summary["status"] == "failed"
    assert summary["findings"][0]["code"] == "document_limit_exceeded"


def test_validate_cli_rejects_oversize_and_nonregular_sources(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    oversize = tmp_path / "oversize.json"
    oversize.write_bytes(b" " * (VALIDATE_CLI.MAX_ANNOTATION_PACK_JSON_BYTES + 1))
    directory = tmp_path / "not-a-file.json"
    directory.mkdir()

    assert VALIDATE_CLI.main([str(oversize)]) == 1
    oversized_output = capsys.readouterr()
    assert _summary(oversized_output.err)["findings"][0]["code"] == ("source_too_large")

    assert VALIDATE_CLI.main([str(directory)]) == 1
    directory_output = capsys.readouterr()
    assert _summary(directory_output.err)["findings"][0]["code"] == (
        "source_not_regular"
    )


def test_validate_cli_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    fifo = tmp_path / "untrusted-input.json"
    os.mkfifo(fifo)

    summary = VALIDATE_CLI.validate_path(fifo)

    assert summary["status"] == "failed"
    assert summary["findings"][0]["code"] == "source_not_regular"


def test_usage_errors_are_exit_two_machine_readable_and_private_safe(
    capsys: pytest.CaptureFixture[str],
) -> None:
    export_args = _export_args()
    export_args[export_args.index("Software")] = PRIVATE_TEXT
    with pytest.raises(SystemExit) as export_error:
        EXPORT_CLI.main(export_args)
    assert export_error.value.code == 2
    export_output = capsys.readouterr()
    assert export_output.out == ""
    assert _summary(export_output.err)["findings"][0]["code"] == "cli_usage_error"
    assert PRIVATE_TEXT not in export_output.err

    with pytest.raises(SystemExit) as validate_error:
        VALIDATE_CLI.main([f"--private-option={PRIVATE_TEXT}"])
    assert validate_error.value.code == 2
    validate_output = capsys.readouterr()
    assert validate_output.out == ""
    assert _summary(validate_output.err)["findings"][0]["code"] == "cli_usage_error"
    assert PRIVATE_TEXT not in validate_output.err

    with pytest.raises(SystemExit) as inspect_error:
        INSPECT_CLI.main([PRIVATE_TEXT, "extra-private-value"])
    assert inspect_error.value.code == 2
    inspect_output = capsys.readouterr()
    assert inspect_output.out == ""
    assert _summary(inspect_output.err)["findings"][0]["code"] == "cli_usage_error"
    assert PRIVATE_TEXT not in inspect_output.err
    assert "extra-private-value" not in inspect_output.err
