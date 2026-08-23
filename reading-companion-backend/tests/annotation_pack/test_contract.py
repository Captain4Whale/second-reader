from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from zipfile import ZipFile

import pytest
from jsonschema import Draft202012Validator

from src.annotation_pack._generated_models import AnnotationPackDocument
from src.annotation_pack.schema import (
    ANNOTATION_CONTEXT_SHA256,
    ANNOTATION_PACK_SCHEMA_ID,
    PUBLICATION_POINTER_SCHEMA_ID,
    SCHEMA_VERSION,
    SPEC_VERSION,
    VALIDATION_REPORT_SCHEMA_ID,
    annotation_validator,
    auxiliary_validator,
    load_context,
    load_schema,
    pack_validator,
    validation_report_finding_sort_key,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = BACKEND_ROOT.parent
CONTRACT_ROOT = WORKSPACE_ROOT / "contract" / "annotation-pack" / "v0"
SCHEMA_ROOT = CONTRACT_ROOT / "schema"
EXAMPLE_ROOT = CONTRACT_ROOT / "examples"
RUNTIME_ROOT = BACKEND_ROOT / "src" / "annotation_pack" / "resources"
GENERATED_MODEL = BACKEND_ROOT / "src" / "annotation_pack" / "_generated_models.py"
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
PACK_ID = "urn:uuid:31f414c4-32f3-50d6-85e1-9382e47c6390"
TRACK_ID = "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _minimal_pack() -> dict[str, Any]:
    return _read_json(EXAMPLE_ROOT / "minimal-pack.json")


def _assert_invalid(validator: Draft202012Validator, document: Any) -> None:
    assert list(validator.iter_errors(document)), document


def _walk_refs(value: Any) -> list[str]:
    if isinstance(value, dict):
        refs = [value["$ref"]] if isinstance(value.get("$ref"), str) else []
        for child in value.values():
            refs.extend(_walk_refs(child))
        return refs
    if isinstance(value, list):
        refs: list[str] = []
        for child in value:
            refs.extend(_walk_refs(child))
        return refs
    return []


def _pointer(*, packaged: bool) -> dict[str, Any]:
    pointer: dict[str, Any] = {
        "schema_version": "annotation-pack-publication-pointer/0.1",
        "track_id": TRACK_ID,
        "revision_id": HEX_A,
        "semantic_digest": HEX_B,
        "annotations_json": f"revisions/{HEX_A}/annotations.json",
        "annotations_json_sha256": HEX_C,
        "validation_report": f"revisions/{HEX_A}/validation-report.json",
        "validation_report_sha256": "d" * 64,
    }
    if packaged:
        pointer.update(
            {
                "detached_package": (
                    f"revisions/{HEX_A}/second-reader-agent-04ace96340ef.annotations"
                ),
                "detached_package_sha256": "e" * 64,
            }
        )
    return pointer


def _report(*, status: str = "valid", packaged: bool = False) -> dict[str, Any]:
    degraded = status == "degraded"
    failed = status == "failed"
    return {
        "schema_version": "annotation-pack-validation-report/0.1",
        "validator_version": "0.1.0",
        "status": status,
        "pack_id": None if failed else PACK_ID,
        "semantic_digest": None if failed else HEX_A,
        "input_snapshot_digest": None if failed else HEX_B,
        "annotations_json_sha256": None if failed else HEX_C,
        "package_sha256": "d" * 64 if packaged else None,
        "counts": {
            "input": 2 if degraded else 1,
            "exported": 1,
            "skipped": 1 if degraded else 0,
            "warnings": 0,
            "errors": 1 if degraded else 0,
        },
        "findings": (
            [
                {
                    "code": "unsupported_legacy_record",
                    "severity": "skipped",
                    "source_record_index": 1,
                    "source_record_digest": "e" * 64,
                    "json_pointer": None,
                    "annotation_id": None,
                    "message": "Source record is not supported by this adapter version.",
                }
            ]
            if degraded
            else []
        ),
    }


def test_all_contract_schemas_are_valid_draft_2020_12() -> None:
    for path in sorted(SCHEMA_ROOT.glob("*.json")):
        schema = _read_json(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_schema_ids_and_pinned_context_are_stable() -> None:
    pack_schema = load_schema()
    assert pack_schema["$id"] == ANNOTATION_PACK_SCHEMA_ID
    assert (
        load_schema(PUBLICATION_POINTER_SCHEMA_ID)["$id"]
        == PUBLICATION_POINTER_SCHEMA_ID
    )
    assert (
        load_schema(VALIDATION_REPORT_SCHEMA_ID)["$id"] == VALIDATION_REPORT_SCHEMA_ID
    )
    context = pack_schema["properties"]["@context"]
    assert (
        context["prefixItems"][0]["const"] == "https://www.w3.org/ns/epub-anno.jsonld"
    )
    assert context["prefixItems"][1]["properties"]["@protected"]["const"] is True
    assert context["prefixItems"][1]["properties"]["sr"]["const"] == (
        "https://captain4whale.github.io/second-reader/ns/annotation-pack#"
    )
    committed_context = _read_json(
        CONTRACT_ROOT / "context" / "second-reader-annotation-context.jsonld"
    )["@context"]
    assert committed_context == {
        "@protected": True,
        "sr": {
            "@id": "https://captain4whale.github.io/second-reader/ns/annotation-pack#",
            "@prefix": True,
        },
    }
    assert not {"value", "language", "start", "end", "title"} & set(committed_context)
    assert load_context()["@context"] == committed_context
    context_bytes = (
        CONTRACT_ROOT / "context" / "second-reader-annotation-context.jsonld"
    ).read_bytes()
    assert hashlib.sha256(context_bytes).hexdigest() == ANNOTATION_CONTEXT_SHA256


def test_python_versions_are_bound_to_the_canonical_schema() -> None:
    pack_schema = load_schema()
    assert SPEC_VERSION == pack_schema["properties"]["sr:specVersion"]["const"]
    assert SCHEMA_VERSION == pack_schema["properties"]["sr:schemaVersion"]["const"]
    assert CONTRACT_ROOT.name == f"v{int(SCHEMA_VERSION.split('.', maxsplit=1)[0])}"


def test_public_schema_mutation_cannot_weaken_a_later_validator() -> None:
    caller_copy = load_schema()
    caller_copy["required"].remove("id")

    document = _minimal_pack()
    del document["id"]
    _assert_invalid(pack_validator(), document)


def test_contract_schemas_have_only_local_references() -> None:
    for path in sorted(SCHEMA_ROOT.glob("*.json")):
        assert all(
            reference.startswith("#/") for reference in _walk_refs(_read_json(path))
        )


def test_standards_baseline_is_dated_and_status_pinned() -> None:
    baseline = (CONTRACT_ROOT / "standards.md").read_text(encoding="utf-8")
    assert "W3C Web Annotation Data Model, Recommendation, 23 February 2017" in baseline
    assert "https://www.w3.org/TR/2017/REC-annotation-model-20170223/" in baseline
    assert "EPUB Annotations 1.0, Working Draft, 21 May 2026" in baseline
    assert "https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/" in baseline
    assert "The EPUB document is a Working Draft, not a Recommendation." in baseline


@pytest.mark.parametrize(
    ("filename", "root_type"),
    [
        ("highlight.annotation.json", "Annotation"),
        ("note.annotation.json", "Annotation"),
        ("minimal-pack.json", "AnnotationSet"),
    ],
)
def test_committed_examples_are_schema_valid(filename: str, root_type: str) -> None:
    document = _read_json(EXAMPLE_ROOT / filename)
    assert document["type"] == root_type
    validator = (
        pack_validator() if root_type == "AnnotationSet" else annotation_validator()
    )
    validator.validate(document)


@pytest.mark.parametrize(
    "field",
    [
        "@context",
        "id",
        "type",
        "generator",
        "generated",
        "about",
        "items",
        "sr:specVersion",
        "sr:schemaVersion",
        "sr:extensionVersion",
        "sr:profile",
        "sr:track",
        "sr:provenance",
        "sr:semanticDigest",
    ],
)
def test_every_pack_required_field_is_enforced(field: str) -> None:
    document = _minimal_pack()
    del document[field]
    _assert_invalid(pack_validator(), document)


def test_highlight_note_and_selector_conditionals_are_enforced() -> None:
    highlight = _read_json(EXAMPLE_ROOT / "highlight.annotation.json")
    highlight["body"] = {
        "type": "TextualBody",
        "value": "Not allowed.",
        "format": "text/plain",
    }
    _assert_invalid(annotation_validator(), highlight)

    note = _read_json(EXAMPLE_ROOT / "note.annotation.json")
    del note["body"]
    _assert_invalid(annotation_validator(), note)

    wrong_kind = _read_json(EXAMPLE_ROOT / "highlight.annotation.json")
    wrong_kind["sr:kind"] = "bookmark"
    _assert_invalid(annotation_validator(), wrong_kind)

    wrong_order = _read_json(EXAMPLE_ROOT / "highlight.annotation.json")
    wrong_order["target"]["selector"].reverse()
    _assert_invalid(annotation_validator(), wrong_order)


def test_uri_datetime_source_and_input_digest_constraints_are_enforced() -> None:
    document = _minimal_pack()
    document["generator"]["id"] = "relative-generator"
    _assert_invalid(pack_validator(), document)

    document = _minimal_pack()
    document["generated"] = "2026-08-23T00:00:00+00:00"
    _assert_invalid(pack_validator(), document)

    document = _minimal_pack()
    document["items"][0]["target"]["source"] = "../private.xhtml"
    _assert_invalid(pack_validator(), document)

    document = _minimal_pack()
    document["sr:provenance"]["sr:inputSnapshotDigest"]["sr:canonicalization"] = (
        "sr-second-reader-input-snapshot-v1"
    )
    _assert_invalid(pack_validator(), document)


def test_absolute_iris_accept_unicode_characters() -> None:
    document = _minimal_pack()
    document["generator"]["id"] = "https://example.org/作者"
    pack_validator().validate(document)


def test_canonical_ids_require_uuid_v5_in_all_contract_documents() -> None:
    uuid_v4 = "urn:uuid:31f414c4-32f3-40d6-85e1-9382e47c6390"

    pack = _minimal_pack()
    pack["id"] = uuid_v4
    _assert_invalid(pack_validator(), pack)

    pointer = _pointer(packaged=False)
    pointer["track_id"] = uuid_v4
    _assert_invalid(auxiliary_validator(PUBLICATION_POINTER_SCHEMA_ID), pointer)

    report = _report(status="valid")
    report["pack_id"] = uuid_v4
    _assert_invalid(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID), report)


def test_edition_content_fingerprint_algorithm_version_is_fixed() -> None:
    document = _minimal_pack()
    document["about"]["sr:edition"]["sr:contentFingerprint"]["sr:algorithmVersion"] = (
        "totally-unsupported-v99"
    )
    _assert_invalid(pack_validator(), document)


def test_unknown_unprefixed_fields_are_rejected() -> None:
    document = _minimal_pack()
    document["private_state"] = "must not pass"
    _assert_invalid(pack_validator(), document)

    document = _minimal_pack()
    document["items"][0]["private_state"] = "must not pass"
    _assert_invalid(pack_validator(), document)


def test_declared_prefixed_extension_survives_generated_alias_round_trip() -> None:
    document = _minimal_pack()
    document["@context"][1]["ex"] = "https://example.invalid/annotation-extension#"
    document["ex:score"] = {"value": 3}
    document["items"][0]["ex:confidence"] = 0.75
    pack_validator().validate(document)

    model = AnnotationPackDocument.model_validate(document)
    dumped = model.model_dump(mode="json", by_alias=True, exclude_none=True)

    assert "@context" in dumped
    assert dumped["ex:score"] == {"value": 3}
    assert dumped["items"][0]["ex:confidence"] == 0.75
    assert "sr:semanticDigest" in dumped
    pack_validator().validate(dumped)


def test_pack_context_requires_a_protected_sr_binding() -> None:
    document = _minimal_pack()
    del document["@context"][1]["@protected"]
    _assert_invalid(pack_validator(), document)


def test_generated_model_does_not_replace_canonical_validation() -> None:
    document = _minimal_pack()
    document["unknown_unprefixed"] = True
    model = AnnotationPackDocument.model_validate(document)
    assert model.model_dump()["unknown_unprefixed"] is True
    _assert_invalid(pack_validator(), document)


def test_runtime_schema_copies_are_byte_identical() -> None:
    for canonical in sorted(SCHEMA_ROOT.glob("*.json")):
        assert (RUNTIME_ROOT / canonical.name).read_bytes() == canonical.read_bytes()

    canonical_context = (
        CONTRACT_ROOT / "context" / "second-reader-annotation-context.jsonld"
    )
    assert (
        RUNTIME_ROOT / canonical_context.name
    ).read_bytes() == canonical_context.read_bytes()


def test_runtime_resources_load_from_a_zip_import(tmp_path: Path) -> None:
    archive = tmp_path / "annotation-pack-runtime.zip"
    package_root = BACKEND_ROOT / "src" / "annotation_pack"
    with ZipFile(archive, "w") as bundle:
        bundle.write(BACKEND_ROOT / "src" / "__init__.py", "src/__init__.py")
        for source in package_root.rglob("*"):
            if source.is_file() and "__pycache__" not in source.parts:
                bundle.write(source, source.relative_to(BACKEND_ROOT))

    probe = "\n".join(
        (
            "import sys",
            f"sys.path.insert(0, {str(archive)!r})",
            "from src.annotation_pack.schema import load_context, load_schema",
            "assert load_schema()['type'] == 'object'",
            "assert load_context()['@context']['sr']['@prefix'] is True",
        )
    )
    completed = subprocess.run(
        [sys.executable, "-I", "-c", probe],
        cwd=tmp_path,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert completed.returncode == 0, completed.stdout


def test_generated_header_names_canonical_schema_digest_and_fixed_tool() -> None:
    digest = hashlib.sha256(
        (SCHEMA_ROOT / "annotation-pack.schema.json").read_bytes()
    ).hexdigest()
    header = GENERATED_MODEL.read_text(encoding="utf-8").splitlines()[0]
    assert f"sha256={digest}" in header
    assert "tool=datamodel-code-generator==0.74.0" in header
    assert "formatter=ruff==0.15.5" in header


def test_generation_is_clean() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/generate_annotation_pack_bindings.py", "--check"],
        cwd=BACKEND_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert completed.returncode == 0, completed.stdout


def test_auxiliary_schemas_do_not_redefine_pack_wire() -> None:
    for schema_id in (PUBLICATION_POINTER_SCHEMA_ID, VALIDATION_REPORT_SCHEMA_ID):
        schema = load_schema(schema_id)
        assert not {"@context", "about", "items", "sr:track"} & set(
            schema["properties"]
        )
        assert "annotation-pack.schema.json" not in json.dumps(schema)


def test_publication_pointer_supports_json_only_and_packaged_revisions() -> None:
    validator = auxiliary_validator(PUBLICATION_POINTER_SCHEMA_ID)
    validator.validate(_pointer(packaged=False))
    validator.validate(_pointer(packaged=True))

    missing_digest = _pointer(packaged=True)
    del missing_digest["detached_package_sha256"]
    _assert_invalid(validator, missing_digest)

    unsafe_path = _pointer(packaged=False)
    unsafe_path["annotations_json"] = f"../revisions/{HEX_A}/annotations.json"
    _assert_invalid(validator, unsafe_path)


def test_validation_report_status_and_artifact_conditionals() -> None:
    validator = auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID)
    validator.validate(_report(status="valid", packaged=False))
    validator.validate(_report(status="valid", packaged=True))
    validator.validate(_report(status="degraded", packaged=False))
    validator.validate(_report(status="failed", packaged=False))

    half_published = _report(status="valid")
    half_published["annotations_json_sha256"] = None
    _assert_invalid(validator, half_published)

    invalid_valid_counts = _report(status="valid")
    invalid_valid_counts["counts"]["errors"] = 1
    _assert_invalid(validator, invalid_valid_counts)


def test_validation_report_finding_sort_is_protocol_deterministic() -> None:
    findings = [
        {
            "code": "z_warning",
            "severity": "warning",
            "source_record_index": None,
            "source_record_digest": None,
            "json_pointer": None,
            "annotation_id": None,
            "message": "Warning.",
        },
        {
            "code": "a_error",
            "severity": "error",
            "source_record_index": 2,
            "source_record_digest": HEX_A,
            "json_pointer": "/items/2",
            "annotation_id": None,
            "message": "Error.",
        },
        {
            "code": "a_fatal",
            "severity": "fatal",
            "source_record_index": None,
            "source_record_digest": None,
            "json_pointer": "",
            "annotation_id": None,
            "message": "Fatal.",
        },
    ]
    assert [
        item["severity"]
        for item in sorted(findings, key=validation_report_finding_sort_key)
    ] == [
        "fatal",
        "error",
        "warning",
    ]


def test_contract_module_has_no_producer_or_mechanism_dependency() -> None:
    source_root = BACKEND_ROOT / "src" / "annotation_pack"
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(source_root.glob("*.py"))
    )
    assert "attentional_v2" not in source
    assert "iterator_reader" not in source
    assert "reading_mechanisms" not in source


def test_pages_projection_builds_exact_authority_bytes() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(WORKSPACE_ROOT / "scripts" / "build_annotation_pack_pages.py"),
            "--check",
        ],
        cwd=WORKSPACE_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert completed.returncode == 0, completed.stdout
