from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from zipfile import ZipFile

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from src.annotation_pack._generated_models import AnnotationPackDocument
from src.annotation_pack.schema import (
    ANNOTATION_PACK_SCHEMA_ID,
    PUBLICATION_POINTER_SCHEMA_ID,
    SCHEMA_VERSION,
    SPEC_VERSION,
    VALIDATION_REPORT_SCHEMA_ID,
    annotation_validator,
    auxiliary_validator,
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
PAGES_SCRIPT = WORKSPACE_ROOT / "scripts" / "build_annotation_pack_pages.py"
PAGES_WORKFLOW = WORKSPACE_ROOT / ".github" / "workflows" / "annotation-pack-pages.yml"
PAGES_ROOT = Path("schema") / "annotation-pack" / "v0"

EPUB_CONTEXT = "https://www.w3.org/ns/epub-anno.jsonld"
GENERATOR = {
    "id": "https://github.com/Captain4Whale/second-reader",
    "type": "Software",
    "name": "Second Reader Annotation Pack Exporter",
}
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
PACK_ID = "urn:uuid:31f414c4-32f3-50d6-85e1-9382e47c6390"
TRACK_ID = "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa"
PRODUCER_ID = "urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _minimal_pack() -> dict[str, Any]:
    return _read_json(EXAMPLE_ROOT / "minimal-pack.json")


def _highlight() -> dict[str, Any]:
    return _read_json(EXAMPLE_ROOT / "highlight.annotation.json")


def _note() -> dict[str, Any]:
    return _read_json(EXAMPLE_ROOT / "note.annotation.json")


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


def _walk_mappings(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        mappings = [value]
        for child in value.values():
            mappings.extend(_walk_mappings(child))
        return mappings
    if isinstance(value, list):
        mappings: list[dict[str, Any]] = []
        for child in value:
            mappings.extend(_walk_mappings(child))
        return mappings
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
        "producer": None if failed else PRODUCER_ID,
        "adapter_version": None if failed else "0.1.0",
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
                    "message": (
                        "Source record is not supported by this adapter version."
                    ),
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


def test_schema_ids_context_and_local_versions_are_stable() -> None:
    pack_schema = load_schema()
    assert pack_schema["$id"] == ANNOTATION_PACK_SCHEMA_ID
    assert (
        load_schema(PUBLICATION_POINTER_SCHEMA_ID)["$id"]
        == PUBLICATION_POINTER_SCHEMA_ID
    )
    assert (
        load_schema(VALIDATION_REPORT_SCHEMA_ID)["$id"] == VALIDATION_REPORT_SCHEMA_ID
    )
    assert pack_schema["properties"]["@context"] == {"const": EPUB_CONTEXT}
    assert SPEC_VERSION == SCHEMA_VERSION == "0.1.0"
    assert CONTRACT_ROOT.name == "v0"


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
    assert "RFC 6920, Naming Things with Hashes" in baseline
    assert "aligned" in baseline
    assert "never described as EPUB-WD conformant" in baseline


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


def test_committed_example_ids_and_item_order_match_v0_framing() -> None:
    highlight = _highlight()
    note = _note()
    pack = _minimal_pack()
    assert pack["id"] == "urn:uuid:d012c503-1480-55d5-8490-cc9e984f95ba"
    assert highlight["id"] == "urn:uuid:9ec4a27a-b863-57fd-a1fc-8dcc77cc29a1"
    assert note["id"] == "urn:uuid:c5b912cb-2487-508c-a6b1-8cb35835ab6c"
    assert pack["items"] == [highlight, note]
    assert [item["id"] for item in pack["items"]] == sorted(
        [highlight["id"], note["id"]]
    )


def test_minimal_pack_targets_are_jointly_realizable_resource_slices() -> None:
    pack = _minimal_pack()
    resources = {
        "Text/chapter-01.xhtml": (
            "The reader paused. "
            "A durable idea is worth returning to."
            " Then the argument moved on."
        ),
        "Text/chapter-02.xhtml": (
            "Do not merely repeat. "
            "Return with a better question."
            " The page may answer differently."
        ),
    }

    for item in pack["items"]:
        target = item["target"]
        quote, position = target["selector"]
        resource = resources[target["source"]]
        start = position["start"]
        end = position["end"]
        assert resource[start:end] == quote["exact"]
        assert resource[:start].endswith(quote["prefix"])
        assert resource[end:].startswith(quote["suffix"])


def test_pack_schema_and_examples_contain_zero_custom_vocabulary() -> None:
    documents = [
        _read_json(SCHEMA_ROOT / "annotation-pack.schema.json"),
        *(_read_json(path) for path in sorted(EXAMPLE_ROOT.glob("*.json"))),
    ]
    for document in documents:
        serialized = json.dumps(document, ensure_ascii=False)
        assert '"sr:' not in serialized
        assert (
            "captain4whale.github.io/second-reader/ns/annotation-pack" not in serialized
        )
        assert not any(
            key.startswith("sr:")
            for mapping in _walk_mappings(document)
            for key in mapping
        )
    assert not any(path.is_file() for path in (CONTRACT_ROOT / "context").glob("**/*"))


def test_pack_schema_has_strict_object_whitelists_and_no_extension_escape() -> None:
    schema = _read_json(SCHEMA_ROOT / "annotation-pack.schema.json")
    assert "patternProperties" not in json.dumps(schema)
    for name in (
        "generator",
        "publication",
        "annotation",
        "textualBody",
        "annotationTarget",
        "textQuoteSelector",
        "textPositionSelector",
    ):
        assert schema["$defs"][name]["additionalProperties"] is False
    assert schema["additionalProperties"] is False


@pytest.mark.parametrize(
    "field",
    ["@context", "id", "type", "generator", "generated", "about", "items"],
)
def test_every_pack_required_field_is_enforced(field: str) -> None:
    document = _minimal_pack()
    del document[field]
    _assert_invalid(pack_validator(), document)


def test_context_and_generator_are_exact_and_immutable() -> None:
    document = _minimal_pack()
    assert document["generator"] == GENERATOR

    for bad_context in ([EPUB_CONTEXT], f"{EPUB_CONTEXT}#", None):
        candidate = _minimal_pack()
        candidate["@context"] = bad_context
        _assert_invalid(pack_validator(), candidate)

    for field, replacement in (
        ("id", "https://example.org/exporter"),
        ("type", "Organization"),
        ("name", "Second Reader"),
    ):
        candidate = _minimal_pack()
        candidate["generator"][field] = replacement
        _assert_invalid(pack_validator(), candidate)

    candidate = _minimal_pack()
    candidate["generator"]["version"] = "0.1.0"
    _assert_invalid(pack_validator(), candidate)


def test_publication_metadata_is_minimal_and_exact_file_bound() -> None:
    validator = pack_validator()
    about = _minimal_pack()["about"]
    assert set(about) == {"dc:identifier", "dc:format", "dc:title", "dc:creator"}

    for field in ("dc:identifier", "dc:format", "dc:title"):
        candidate = _minimal_pack()
        del candidate["about"][field]
        _assert_invalid(validator, candidate)

    without_creator = _minimal_pack()
    del without_creator["about"]["dc:creator"]
    validator.validate(without_creator)

    for identifier in (
        [],
        [f"nih:sha-256;{HEX_A}", f"nih:sha-256;{HEX_B}"],
        [f"nih:sha-256:{HEX_A}"],
        [f"nih:sha-256;{HEX_A.upper()}"],
        [f"urn:sha256:{HEX_A}"],
    ):
        candidate = _minimal_pack()
        candidate["about"]["dc:identifier"] = identifier
        _assert_invalid(validator, candidate)

    for creators in ([], [""], ["One", "One"]):
        candidate = _minimal_pack()
        candidate["about"]["dc:creator"] = creators
        _assert_invalid(validator, candidate)

    candidate = _minimal_pack()
    candidate["about"]["dc:language"] = "en"
    _assert_invalid(validator, candidate)


@pytest.mark.parametrize("field", ["id", "type", "motivation", "created", "target"])
def test_every_annotation_required_field_is_enforced(field: str) -> None:
    annotation = _highlight()
    del annotation[field]
    _assert_invalid(annotation_validator(), annotation)


def test_highlight_and_note_body_conditionals_are_enforced() -> None:
    validator = annotation_validator()

    highlight = _highlight()
    highlight["body"] = {"type": "TextualBody", "value": "Not allowed."}
    _assert_invalid(validator, highlight)

    note = _note()
    del note["body"]
    _assert_invalid(validator, note)

    for mutation in (
        {"type": "TextualBody", "value": ""},
        {"type": "TextualBody", "value": "A note.", "format": "text/plain"},
        {"type": "Text", "value": "A note."},
    ):
        candidate = _note()
        candidate["body"] = mutation
        _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["motivation"] = "bookmarking"
    _assert_invalid(validator, candidate)


def test_target_is_exactly_quote_then_position() -> None:
    validator = annotation_validator()
    target = _highlight()["target"]
    assert set(target) == {"source", "selector"}
    assert [selector["type"] for selector in target["selector"]] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]

    without_context = _highlight()
    quote = without_context["target"]["selector"][0]
    del quote["prefix"]
    del quote["suffix"]
    validator.validate(without_context)

    reversed_selectors = _highlight()
    reversed_selectors["target"]["selector"].reverse()
    _assert_invalid(validator, reversed_selectors)

    for selector_count in (1, 3):
        candidate = _highlight()
        selectors = candidate["target"]["selector"]
        candidate["target"]["selector"] = (
            selectors[:selector_count]
            if selector_count == 1
            else [*selectors, selectors[0]]
        )
        _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["type"] = "SpecificResource"
    _assert_invalid(validator, candidate)


def test_quote_and_text_position_structural_constraints_are_enforced() -> None:
    validator = annotation_validator()

    candidate = _highlight()
    candidate["target"]["selector"][0]["exact"] = ""
    _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["selector"][0]["normalization"] = "private"
    _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["selector"][0]["prefix"] = ""
    _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["selector"][1]["start"] = -1
    _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["selector"][1]["end"] = 0
    _assert_invalid(validator, candidate)

    candidate = _highlight()
    candidate["target"]["selector"][1]["coordinateSystem"] = "paragraph"
    _assert_invalid(validator, candidate)

    # JSON Schema owns shape only; the semantic validator owns start < end and
    # exact source-resource round trips.
    structurally_valid = _highlight()
    structurally_valid["target"]["selector"][1].update({"start": 9, "end": 8})
    validator.validate(structurally_valid)


@pytest.mark.parametrize(
    "source",
    [
        "https://example.org/chapter.xhtml",
        "/Text/chapter.xhtml",
        "../Text/chapter.xhtml",
        "Text/../chapter.xhtml",
        "Text/chapter.xhtml#frag",
        "Text/chapter.xhtml?token=secret",
        "Text\\chapter.xhtml",
        "Text/chapter one.xhtml",
    ],
)
def test_target_source_is_a_safe_relative_epub_href(source: str) -> None:
    candidate = _highlight()
    candidate["target"]["source"] = source
    _assert_invalid(annotation_validator(), candidate)


def test_uuid_dates_and_root_extras_are_strict() -> None:
    uuid_v4 = "urn:uuid:31f414c4-32f3-40d6-85e1-9382e47c6390"

    candidate = _minimal_pack()
    candidate["id"] = uuid_v4
    _assert_invalid(pack_validator(), candidate)

    candidate = _minimal_pack()
    candidate["items"][0]["id"] = uuid_v4
    _assert_invalid(pack_validator(), candidate)

    candidate = _minimal_pack()
    candidate["generated"] = "2026-08-25T00:00:00+00:00"
    _assert_invalid(pack_validator(), candidate)

    candidate = _minimal_pack()
    candidate["items"][0]["created"] = "2026-08-25T00:00:00.000Z"
    _assert_invalid(pack_validator(), candidate)

    candidate = _minimal_pack()
    candidate["private_state"] = "must not pass"
    _assert_invalid(pack_validator(), candidate)


@pytest.mark.parametrize(
    ("path", "field", "value"),
    [
        (("items", 0), "creator", {"type": "Software", "name": "Private"}),
        (("items", 0), "sr:kind", "highlight"),
        (("items", 0), "confidence", 0.9),
        (("items", 0, "target"), "sr:anchorId", PACK_ID),
        (("items", 0, "target"), "chapter", {"id": 1}),
    ],
)
def test_legacy_and_private_annotation_fields_are_rejected(
    path: tuple[str | int, ...], field: str, value: Any
) -> None:
    document = _minimal_pack()
    candidate: Any = document
    for part in path:
        candidate = candidate[part]
    candidate[field] = value
    _assert_invalid(pack_validator(), document)


def test_generated_binding_round_trip_is_strict_but_schema_remains_canonical() -> None:
    document = _minimal_pack()
    model = AnnotationPackDocument.model_validate(document)
    dumped = model.model_dump(mode="json", by_alias=True, exclude_none=True)
    assert dumped == document
    pack_validator().validate(dumped)

    with pytest.raises(ValidationError):
        AnnotationPackDocument.model_validate({**document, "sr:private": True})

    # Code generation cannot encode the highlighting/commenting conditional,
    # so callers must still use the canonical schema validator.
    invalid_highlight = _minimal_pack()
    highlight_item = next(
        item
        for item in invalid_highlight["items"]
        if item["motivation"] == "highlighting"
    )
    highlight_item["body"] = {
        "type": "TextualBody",
        "value": "Forbidden on a Highlight.",
    }
    AnnotationPackDocument.model_validate(invalid_highlight)
    _assert_invalid(pack_validator(), invalid_highlight)


def test_runtime_schema_copies_are_exact_and_context_free() -> None:
    canonical_schemas = sorted(SCHEMA_ROOT.glob("*.json"))
    assert {path.name for path in canonical_schemas} == {
        "annotation-pack.schema.json",
        "publication-pointer.schema.json",
        "validation-report.schema.json",
    }
    assert {path.name for path in RUNTIME_ROOT.glob("*.json")} == {
        path.name for path in canonical_schemas
    }
    for canonical in canonical_schemas:
        assert (RUNTIME_ROOT / canonical.name).read_bytes() == canonical.read_bytes()
    assert not list(RUNTIME_ROOT.glob("*context*"))


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
            "from src.annotation_pack.schema import load_schema",
            "assert load_schema()['type'] == 'object'",
            "assert load_schema()['properties']['@context']['const'].startswith('https://www.w3.org/')",
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


def test_generated_header_names_schema_digest_and_fixed_tools() -> None:
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
        assert not {"@context", "about", "items", "generator", "target"} & set(
            schema["properties"]
        )
        serialized = json.dumps(schema)
        assert "annotation-pack.schema.json" not in serialized
        assert '"sr:' not in serialized


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


def test_validation_report_status_adapter_and_artifact_conditionals() -> None:
    validator = auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID)
    validator.validate(_report(status="valid", packaged=False))
    validator.validate(_report(status="valid", packaged=True))
    validator.validate(_report(status="degraded", packaged=False))
    validator.validate(_report(status="failed", packaged=False))

    for field in ("producer", "adapter_version"):
        missing = _report(status="valid")
        del missing[field]
        _assert_invalid(validator, missing)

        null_publishable = _report(status="valid")
        null_publishable[field] = None
        _assert_invalid(validator, null_publishable)

    relative_producer = _report(status="valid")
    relative_producer["producer"] = "second-reader"
    _assert_invalid(validator, relative_producer)

    bad_adapter = _report(status="valid")
    bad_adapter["adapter_version"] = "v0.1"
    _assert_invalid(validator, bad_adapter)

    half_published = _report(status="valid")
    half_published["annotations_json_sha256"] = None
    _assert_invalid(validator, half_published)

    orphan_package_digest = _report(status="failed", packaged=True)
    assert orphan_package_digest["annotations_json_sha256"] is None
    _assert_invalid(validator, orphan_package_digest)

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
    ] == ["fatal", "error", "warning"]


def test_contract_module_has_no_producer_or_mechanism_dependency() -> None:
    source_root = BACKEND_ROOT / "src" / "annotation_pack"
    forbidden_module_segments = {
        "attentional_v2",
        "iterator_reader",
        "reading_mechanisms",
    }
    for path in sorted(source_root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_modules = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_modules.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        assert not any(
            forbidden in imported.split(".")
            for imported in imported_modules
            for forbidden in forbidden_module_segments
        ), path

    for filename in ("builder.py", "validation.py"):
        path = source_root / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_modules = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_modules.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        assert not any(
            "producers" in imported.split(".") for imported in imported_modules
        ), path


def test_pages_projection_builds_only_allowlisted_authority_bytes(
    tmp_path: Path,
) -> None:
    check = subprocess.run(
        [sys.executable, str(PAGES_SCRIPT), "--check"],
        cwd=WORKSPACE_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert check.returncode == 0, check.stdout

    destination = tmp_path / "_site"
    build = subprocess.run(
        [sys.executable, str(PAGES_SCRIPT), "--output-dir", str(destination)],
        cwd=WORKSPACE_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert build.returncode == 0, build.stdout

    expected_sources = {
        PAGES_ROOT / path.name: path for path in sorted(SCHEMA_ROOT.glob("*.json"))
    }
    expected_sources.update(
        {
            PAGES_ROOT / "examples" / path.name: path
            for path in sorted(EXAMPLE_ROOT.glob("*.json"))
        }
    )
    expected_files = {Path(".nojekyll"), *expected_sources}
    actual_files = {
        path.relative_to(destination)
        for path in destination.rglob("*")
        if path.is_file()
    }
    assert actual_files == expected_files
    assert (destination / ".nojekyll").read_bytes() == b""
    for published, authority in expected_sources.items():
        assert (destination / published).read_bytes() == authority.read_bytes()

    assert not (destination / "ns" / "annotation-pack").exists()
    assert not (destination / PAGES_ROOT / "context").exists()


def test_contract_projection_workflow_validates_without_deploying() -> None:
    workflow = PAGES_WORKFLOW.read_text(encoding="utf-8")
    assert "python scripts/build_annotation_pack_pages.py --check" in workflow
    assert "python scripts/build_contract_pages.py --check" in workflow
    assert "--output-dir _site" not in workflow
    assert "actions/upload-pages-artifact" not in workflow
    assert "actions/configure-pages" not in workflow
    assert "actions/deploy-pages" not in workflow
    assert "pages: write" not in workflow
    assert "id-token: write" not in workflow
