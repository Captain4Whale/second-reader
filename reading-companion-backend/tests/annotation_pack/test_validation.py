from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from src.annotation_pack.drafts import ValidationFinding
from src.annotation_pack.ids import annotation_id, pack_id
from src.annotation_pack.schema import (
    VALIDATION_REPORT_SCHEMA_ID,
    auxiliary_validator,
)
from src.annotation_pack.serialization import (
    CanonicalJsonError,
    canonical_json_bytes,
    semantic_digest,
    serialize_pack,
)
from src.annotation_pack.validation import (
    ERROR_CATALOG,
    FUTURE_PIPELINE_CODES,
    PACK_VALIDATOR_CODES,
    UPSTREAM_VALIDATION_CODES,
    ValidationContext,
    ValidationReport,
    ValidationResult,
    finalize_validation_report,
    make_validation_failure,
    make_validation_finding,
    serialize_validation_report,
    validate_pack,
    validation_report_wire,
)


ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "contract/annotation-pack/v0/examples/minimal-pack.json"
REPORT_SCHEMA = (
    ROOT / "contract/annotation-pack/v0/schema/validation-report.schema.json"
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64
PRODUCER = "urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a"
ADAPTER_VERSION = "0.1.0"
OTHER_UUID = "urn:uuid:00000000-0000-5000-8000-000000000000"


class _SwitchMapping(Mapping[str, object]):
    """Expose a different view on each ``items()`` read."""

    def __init__(self, *views: dict[str, object]) -> None:
        self._views = views
        self.item_reads = 0

    def __getitem__(self, key: str) -> object:
        return self._views[0][key]

    def __iter__(self):
        return iter(self._views[0])

    def __len__(self) -> int:
        return len(self._views[0])

    def items(self):
        index = min(self.item_reads, len(self._views) - 1)
        self.item_reads += 1
        return self._views[index].items()


class _ExplosiveMapping(Mapping[str, object]):
    def __getitem__(self, key: str) -> object:
        raise RuntimeError(f"PRIVATE /Users/alice/{key}")

    def __iter__(self):
        return iter(("private",))

    def __len__(self) -> int:
        return 1

    def items(self):
        raise RuntimeError("PRIVATE /Users/alice/annotation-pack.json")


def _valid_pack() -> dict[str, Any]:
    pack: dict[str, Any] = json.loads(EXAMPLE.read_text())
    _refresh_ids(pack)
    return pack


def _epub_sha256(pack: Mapping[str, Any]) -> str:
    nih = pack["about"]["dc:identifier"][0]
    assert isinstance(nih, str)
    return nih.removeprefix("nih:sha-256;")


def _refresh_ids(pack: dict[str, Any]) -> None:
    epub_sha256 = _epub_sha256(pack)
    pack["id"] = pack_id(epub_sha256, pack["generator"]["id"])
    for item in pack["items"]:
        position = item["target"]["selector"][1]
        body = item.get("body")
        body_value = body["value"] if item["motivation"] == "commenting" else None
        item["id"] = annotation_id(
            epub_sha256,
            item["target"]["source"],
            position["start"],
            position["end"],
            item["motivation"],
            body_value,
        )
    pack["items"].sort(key=lambda item: item["id"])


def _codes(result: ValidationResult) -> list[str]:
    return [finding.code for finding in result.findings]


def _item(pack: dict[str, Any], motivation: str) -> dict[str, Any]:
    return next(item for item in pack["items"] if item["motivation"] == motivation)


def _context(
    *,
    input_count: int = 2,
    findings: tuple[ValidationFinding, ...] = (),
    allow_empty: bool = False,
) -> ValidationContext:
    return ValidationContext(
        input_count=input_count,
        findings=findings,
        allow_empty=allow_empty,
        input_snapshot_digest=DIGEST_A,
        producer=PRODUCER,
        adapter_version=ADAPTER_VERSION,
    )


def test_valid_minimal_pack_has_internal_identity_and_no_public_internal_fields() -> (
    None
):
    pack = _valid_pack()
    result = validate_pack(pack, context=_context())
    encoded = canonical_json_bytes(pack)

    assert result.status == "valid"
    assert result.publishable
    assert (result.input_count, result.exported_count) == (2, 2)
    assert result.findings == ()
    assert result.pack_id == pack_id(_epub_sha256(pack), pack["generator"]["id"])
    assert result.semantic_digest == semantic_digest(pack)
    assert result.input_snapshot_digest == DIGEST_A
    assert result.producer == PRODUCER
    assert result.adapter_version == ADAPTER_VERSION
    assert b'"sr:' not in encoded
    for internal_key in (
        b'"semantic_digest"',
        b'"input_snapshot_digest"',
        b'"producer"',
        b'"adapter_version"',
    ):
        assert internal_key not in encoded
    assert not hasattr(result, "annotations_json_sha256")
    with pytest.raises(FrozenInstanceError):
        result.status = "failed"  # type: ignore[misc]


def test_empty_policy_is_explicit_and_warning_does_not_degrade() -> None:
    pack = _valid_pack()
    pack["items"] = []

    rejected = validate_pack(pack, context=_context(input_count=0))
    accepted = validate_pack(
        pack,
        context=_context(input_count=0, allow_empty=True),
    )

    assert rejected.status == "failed"
    assert _codes(rejected) == ["empty_track"]
    assert accepted.status == "valid"
    assert accepted.warning_count == 1
    assert _codes(accepted) == ["empty_track"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda pack: pack.__setitem__("generated", "yesterday"),
            "invalid_generated_timestamp",
        ),
        (lambda pack: pack.pop("about"), "publication_identity_missing"),
        (
            lambda pack: _item(pack, "highlighting").__setitem__(
                "created", "2026-08-25T00:00:00+00:00"
            ),
            "invalid_annotation_timestamp",
        ),
        (
            lambda pack: _item(pack, "highlighting").__setitem__(
                "motivation", "bookmarking"
            ),
            "unsupported_kind",
        ),
        (
            lambda pack: pack.__setitem__("type", "AnnotationPage"),
            "schema_validation_failed",
        ),
    ],
)
def test_schema_failures_use_stable_sanitized_codes(mutate, expected: str) -> None:
    pack = _valid_pack()
    mutate(pack)

    result = validate_pack(pack)

    assert result.status == "failed"
    assert expected in _codes(result)
    assert all("yesterday" not in finding.message for finding in result.findings)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda pack: pack.__setitem__("sr:semanticDigest", {"sr:value": DIGEST_A}),
        lambda pack: pack.__setitem__("sr:track", {"id": OTHER_UUID}),
        lambda pack: pack["about"].__setitem__("sr:work", {"id": OTHER_UUID}),
        lambda pack: _item(pack, "highlighting").__setitem__("sr:kind", "highlight"),
        lambda pack: _item(pack, "highlighting").__setitem__(
            "creator", {"id": OTHER_UUID}
        ),
        lambda pack: _item(pack, "highlighting")["target"].__setitem__(
            "type", "SpecificResource"
        ),
        lambda pack: _item(pack, "highlighting")["target"].__setitem__(
            "sr:anchorId", OTHER_UUID
        ),
        lambda pack: _item(pack, "commenting")["body"].__setitem__(
            "format", "text/plain"
        ),
        lambda pack: pack.__setitem__(
            "@context",
            [
                "https://www.w3.org/ns/epub-anno.jsonld",
                {"sr": "https://captain4whale.github.io/second-reader/ns#"},
            ],
        ),
        lambda pack: _item(pack, "highlighting")["target"]["selector"].__setitem__(
            1,
            {
                "type": "ParagraphCharSelector",
                "sr:start": {"sr:paragraphIndex": 0, "sr:charOffset": 19},
                "sr:end": {"sr:paragraphIndex": 0, "sr:charOffset": 56},
            },
        ),
        lambda pack: _item(pack, "highlighting")["target"]["selector"].append(
            {"type": "EPUBCFISelector", "value": "epubcfi(/6/2)"}
        ),
    ],
)
def test_old_heavy_wire_and_every_sr_field_are_rejected(mutate) -> None:
    pack = _valid_pack()
    mutate(pack)

    result = validate_pack(pack)

    assert result.status == "failed"
    assert not result.publishable
    assert any(
        code in _codes(result)
        for code in {
            "schema_validation_failed",
            "publication_identity_missing",
            "note_body_missing",
        }
    )


def test_minimal_v0_has_only_strict_mode() -> None:
    with pytest.raises(ValueError, match="strict"):
        validate_pack(_valid_pack(), mode="compatible")  # type: ignore[arg-type]


def test_safe_core_pointer_is_preserved_and_hostile_context_pointer_is_removed() -> (
    None
):
    pack = _valid_pack()
    pack["generated"] = "not-a-timestamp"
    generated = next(
        finding
        for finding in validate_pack(pack).findings
        if finding.code == "invalid_generated_timestamp"
    )
    assert generated.json_pointer == "/generated"

    hostile = ValidationFinding(
        code="invalid_publication_metadata",
        severity="warning",
        message="PRIVATE /Users/alice/book.epub",
        json_pointer="/Users/alice/private.json",
    )
    sanitized = validate_pack(
        _valid_pack(),
        context=_context(findings=(hostile,)),
    )
    warning = next(
        finding
        for finding in sanitized.findings
        if finding.code == "invalid_publication_metadata"
    )
    assert warning.message == "Publication metadata was invalid and was omitted."
    assert warning.json_pointer is None
    assert "validation_context_invalid" in _codes(sanitized)


def test_highlight_and_note_body_rules_are_closed() -> None:
    highlight_pack = _valid_pack()
    _item(highlight_pack, "highlighting")["body"] = {
        "type": "TextualBody",
        "value": "must not exist",
    }
    assert "highlight_body_present" in _codes(validate_pack(highlight_pack))

    missing_note = _valid_pack()
    _item(missing_note, "commenting").pop("body")
    assert "note_body_missing" in _codes(validate_pack(missing_note))

    empty_note = _valid_pack()
    _item(empty_note, "commenting")["body"]["value"] = ""
    assert "note_body_missing" in _codes(validate_pack(empty_note))

    whitespace_note = _valid_pack()
    _item(whitespace_note, "commenting")["body"]["value"] = "   "
    assert "note_body_missing" in _codes(
        validate_pack(whitespace_note, verify_ids=False)
    )


def test_source_quote_and_context_preserve_non_nfc_code_points() -> None:
    pack = _valid_pack()
    highlight = _item(pack, "highlighting")
    quote = highlight["target"]["selector"][0]
    position = highlight["target"]["selector"][1]
    exact = "Cafe\u0301"
    quote["exact"] = exact
    quote["prefix"] = "Before Cafe\u0301"
    quote["suffix"] = "Cafe\u0301 after"
    position["start"] = 10
    position["end"] = 10 + len(exact)
    _refresh_ids(pack)

    result = validate_pack(pack, context=_context())

    assert result.status == "valid"
    assert result.publishable
    assert exact != "Caf\u00e9"


def test_pack_and_annotation_ids_are_recomputed_from_minimal_semantics() -> None:
    pack_tamper = _valid_pack()
    pack_tamper["id"] = OTHER_UUID
    assert "duplicate_pack_or_track_id_semantics" in _codes(validate_pack(pack_tamper))

    annotation_tamper = _valid_pack()
    annotation_tamper["items"][0]["id"] = OTHER_UUID
    annotation_tamper["items"].sort(key=lambda item: item["id"])
    assert "duplicate_annotation_id" in _codes(validate_pack(annotation_tamper))

    file_tamper = _valid_pack()
    file_tamper["about"]["dc:identifier"] = [f"nih:sha-256;{'d' * 64}"]
    result = validate_pack(file_tamper)
    assert "duplicate_pack_or_track_id_semantics" in _codes(result)
    assert "duplicate_annotation_id" in _codes(result)


def test_verify_ids_false_disables_only_identity_recomputation() -> None:
    pack = _valid_pack()
    pack["id"] = OTHER_UUID
    pack["items"][0]["id"] = OTHER_UUID
    pack["items"].sort(key=lambda item: item["id"])

    assert validate_pack(pack).status == "failed"
    assert validate_pack(pack, verify_ids=False).status == "valid"

    pack["items"].reverse()
    result = validate_pack(pack, verify_ids=False)
    assert result.status == "failed"
    assert "item_order_invalid" in _codes(result)


def test_items_must_be_sorted_and_semantic_duplicates_are_rejected() -> None:
    unordered = _valid_pack()
    unordered["items"].reverse()
    assert "item_order_invalid" in _codes(validate_pack(unordered))

    duplicate = _valid_pack()
    copied = deepcopy(duplicate["items"][0])
    copied["id"] = OTHER_UUID
    duplicate["items"].append(copied)
    duplicate["items"].sort(key=lambda item: item["id"])
    result = validate_pack(duplicate, verify_ids=False)
    assert "duplicate_annotation_id" in _codes(result)


def test_same_target_with_different_motivation_and_body_is_not_a_duplicate() -> None:
    pack = _valid_pack()
    highlight = deepcopy(_item(pack, "highlighting"))
    highlight["motivation"] = "commenting"
    highlight["body"] = {"type": "TextualBody", "value": "A distinct note."}
    highlight["created"] = "2026-07-03T08:32:00Z"
    pack["items"].append(highlight)
    _refresh_ids(pack)

    result = validate_pack(pack)

    assert result.status == "valid"
    assert result.exported_count == 3


@pytest.mark.parametrize(
    "source",
    [
        "Text/%63hapter-01.xhtml",
        "Text/./chapter-01.xhtml",
    ],
)
def test_target_href_must_be_a_canonical_relative_epub_href(source: str) -> None:
    pack = _valid_pack()
    _item(pack, "highlighting")["target"]["source"] = source
    _refresh_ids(pack)

    result = validate_pack(pack)

    assert "target_href_not_in_manifest" in _codes(result)


@pytest.mark.parametrize(
    "source",
    [
        "/Text/chapter-01.xhtml",
        "../Text/chapter-01.xhtml",
        "Text/chapter-01.xhtml?download=1",
        "Text/chapter-01.xhtml#fragment",
        "Text\\chapter-01.xhtml",
        "https://example.org/chapter.xhtml",
    ],
)
def test_schema_rejects_unsafe_target_href_spellings(source: str) -> None:
    pack = _valid_pack()
    _item(pack, "highlighting")["target"]["source"] = source

    result = validate_pack(pack, verify_ids=False)

    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)


def test_text_position_is_code_point_end_exclusive_and_exact_length_checked() -> None:
    pack = _valid_pack()
    annotation = _item(pack, "highlighting")
    quote, position = annotation["target"]["selector"]
    quote["exact"] = "A😀文"
    position["start"] = 5
    position["end"] = 8
    _refresh_ids(pack)
    assert validate_pack(pack).status == "valid"

    quote["exact"] = "A😀文!"
    result = validate_pack(pack)
    assert "unresolved_source_quote" in _codes(result)


@pytest.mark.parametrize(("start", "end"), [(20, 20), (21, 20)])
def test_empty_or_reversed_text_position_is_rejected(start: int, end: int) -> None:
    pack = _valid_pack()
    position = _item(pack, "highlighting")["target"]["selector"][1]
    position.update(start=start, end=end)

    result = validate_pack(pack, verify_ids=False)

    assert "malformed_source_span" in _codes(result)


@pytest.mark.parametrize(
    ("field", "value"),
    [("start", -1), ("start", True), ("end", False)],
)
def test_position_schema_rejects_negative_and_boolean_coordinates(
    field: str,
    value: object,
) -> None:
    pack = _valid_pack()
    _item(pack, "highlighting")["target"]["selector"][1][field] = value

    result = validate_pack(pack, verify_ids=False)

    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)


def test_quote_context_is_optional_but_selector_order_is_fixed() -> None:
    optional = _valid_pack()
    quote = _item(optional, "highlighting")["target"]["selector"][0]
    quote.pop("prefix")
    quote.pop("suffix")
    assert validate_pack(optional).status == "valid"

    reversed_selectors = _valid_pack()
    _item(reversed_selectors, "highlighting")["target"]["selector"].reverse()
    result = validate_pack(reversed_selectors, verify_ids=False)
    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)


@pytest.mark.parametrize("length", [0, 1025])
def test_quote_exact_is_nonempty_and_bounded(length: int) -> None:
    pack = _valid_pack()
    annotation = _item(pack, "highlighting")
    annotation["target"]["selector"][0]["exact"] = "x" * length
    annotation["target"]["selector"][1].update(start=0, end=max(1, length))

    result = validate_pack(pack, verify_ids=False)

    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)


@pytest.mark.parametrize(
    "private_key",
    ["prompt", "reaction_id", "runtime_trace", "api_key"],
)
def test_private_keys_fail_closed_and_are_never_echoed(private_key: str) -> None:
    pack = _valid_pack()
    pack[private_key] = "PRIVATE /Users/alice/export.json"

    result = validate_pack(pack)
    finding_text = json.dumps([finding.message for finding in result.findings])

    assert "private_field_leakage" in _codes(result)
    assert "/Users/alice" not in finding_text


@pytest.mark.parametrize(
    "private_value",
    [
        "/Users/alice/private/book.epub",
        "file:///tmp/private.json",
        "https://127.0.0.1/private",
        "https://example.org/public?access_token=secret",
    ],
)
def test_private_metadata_values_fail_closed_without_echo(private_value: str) -> None:
    pack = _valid_pack()
    pack["about"]["dc:title"] = private_value

    result = validate_pack(pack)
    finding_text = json.dumps([finding.message for finding in result.findings])

    assert "private_field_leakage" in _codes(result)
    assert private_value not in finding_text


def test_source_quote_path_is_preserved_but_private_note_body_is_rejected() -> None:
    pack = _valid_pack()
    note = _item(pack, "commenting")
    exact = "The text says /Users/alice is only an example."
    note["target"]["selector"][0]["exact"] = exact
    note["target"]["selector"][1].update(start=7, end=7 + len(exact))
    _refresh_ids(pack)

    source_only = validate_pack(pack)

    assert source_only.status == "valid"
    assert "private_field_leakage" not in _codes(source_only)

    private_body = (
        "Leaked /etc/passwd and https://example.org/?token=private-runtime-value."
    )
    note["body"]["value"] = private_body
    _refresh_ids(pack)

    result = validate_pack(pack)
    finding_text = json.dumps([finding.message for finding in result.findings])

    assert result.status == "failed"
    assert "private_field_leakage" in _codes(result)
    assert private_body not in finding_text


def test_target_source_privacy_exemption_never_makes_absolute_href_valid() -> None:
    pack = _valid_pack()
    _item(pack, "highlighting")["target"]["source"] = "/Users/alice/chapter.xhtml"

    result = validate_pack(pack, verify_ids=False)

    assert result.status == "failed"
    assert "private_field_leakage" not in _codes(result)
    assert "schema_validation_failed" in _codes(result)


@pytest.mark.parametrize(("length", "warns"), [(511, False), (512, True)])
def test_large_note_source_copy_warning_is_bounded_and_non_degrading(
    length: int,
    warns: bool,
) -> None:
    pack = _valid_pack()
    note = _item(pack, "commenting")
    copied_text = "x" * length
    note["target"]["selector"][0]["exact"] = copied_text
    note["target"]["selector"][1].update(start=0, end=length)
    note["body"]["value"] = copied_text
    _refresh_ids(pack)

    result = validate_pack(pack)

    assert result.status == "valid"
    assert ("body_looks_like_source_copy" in _codes(result)) is warns


def test_depth_cycle_float_unsafe_integer_and_large_string_fail_closed() -> None:
    deep = _valid_pack()
    value: dict[str, object] = {}
    cursor = value
    for _ in range(70):
        child: dict[str, object] = {}
        cursor["next"] = child
        cursor = child
    deep["unknown"] = value
    assert "document_limit_exceeded" in _codes(validate_pack(deep))

    cycle = _valid_pack()
    cycle["cycle"] = cycle
    assert "schema_validation_failed" in _codes(validate_pack(cycle))

    floating = _valid_pack()
    floating["float"] = 1.5
    assert "schema_validation_failed" in _codes(validate_pack(floating))

    integer = _valid_pack()
    integer["integer"] = 2**53
    assert "schema_validation_failed" in _codes(validate_pack(integer))

    huge = _valid_pack()
    huge["huge"] = "x" * (1024 * 1024 + 1)
    assert "document_limit_exceeded" in _codes(validate_pack(huge))


def test_hostile_mapping_exceptions_are_sanitized() -> None:
    result = validate_pack(_ExplosiveMapping())

    assert result.status == "failed"
    assert _codes(result) == ["schema_validation_failed"]
    assert "/Users/alice" not in json.dumps(
        [finding.message for finding in result.findings]
    )


def test_scalar_subclasses_are_rejected_without_executing_overrides() -> None:
    private_text = "PRIVATE /Users/alice/export.json"

    class HostileString(str):
        callbacks = 0

        def encode(self, *_args, **_kwargs):
            type(self).callbacks += 1
            raise RuntimeError(private_text)

        def __len__(self) -> int:
            type(self).callbacks += 1
            raise RuntimeError(private_text)

    class HostileInteger(int):
        callbacks = 0

        def __int__(self) -> int:
            type(self).callbacks += 1
            raise RuntimeError(private_text)

        def __lt__(self, _other: object) -> bool:
            type(self).callbacks += 1
            raise RuntimeError(private_text)

    hostile_text = _valid_pack()
    hostile_text["generated"] = HostileString(hostile_text["generated"])
    hostile_integer = _valid_pack()
    _item(hostile_integer, "highlighting")["target"]["selector"][1]["start"] = (
        HostileInteger(19)
    )

    for pack in (hostile_text, hostile_integer):
        result = validate_pack(pack)
        assert result.status == "failed"
        assert "schema_validation_failed" in _codes(result)

    assert HostileString.callbacks == 0
    assert HostileInteger.callbacks == 0


def test_upstream_skip_accounting_is_degraded_and_caller_text_is_sanitized() -> None:
    pack = _valid_pack()
    pack["items"] = pack["items"][:1]
    skipped = ValidationFinding(
        code="ambiguous_source_quote",
        severity="skipped",
        message="PRIVATE /Users/alice/book.epub full quote",
        source_record_index=1,
        source_record_digest=DIGEST_C,
    )

    result = validate_pack(
        pack,
        context=_context(input_count=2, findings=(skipped,)),
    )

    assert result.status == "degraded"
    assert (result.input_count, result.exported_count, result.skipped_count) == (
        2,
        1,
        1,
    )
    assert result.error_count == 0
    finding = next(
        item for item in result.findings if item.code == "ambiguous_source_quote"
    )
    assert finding.message == "The source quote does not resolve uniquely."
    assert "/Users/" not in finding.message


def test_warning_context_stays_valid_and_invalid_accounting_fails() -> None:
    warning = make_validation_finding("invalid_publication_metadata", "warning")
    warned = validate_pack(
        _valid_pack(),
        context=_context(findings=(warning,)),
    )
    assert warned.status == "valid"
    assert warned.warning_count == 1

    invalid = validate_pack(_valid_pack(), context=_context(input_count=3))
    assert invalid.status == "failed"
    assert "validation_context_invalid" in _codes(invalid)


@pytest.mark.parametrize(
    "context",
    [
        ValidationContext(input_count=-1),
        ValidationContext(input_snapshot_digest="A" * 64),
        ValidationContext(producer=PRODUCER),
        ValidationContext(adapter_version=ADAPTER_VERSION),
        ValidationContext(
            producer="file:///tmp/private", adapter_version=ADAPTER_VERSION
        ),
        ValidationContext(producer=PRODUCER, adapter_version="version-one"),
        ValidationContext(allow_empty=1),  # type: ignore[arg-type]
        ValidationContext(findings=[]),  # type: ignore[arg-type]
    ],
)
def test_invalid_validation_context_fails_closed(context: ValidationContext) -> None:
    result = validate_pack(_valid_pack(), context=context)

    assert result.status == "failed"
    assert "validation_context_invalid" in _codes(result)


def test_report_finalization_has_internal_fields_counts_schema_and_canonical_bytes() -> (
    None
):
    pack = _valid_pack()
    result = validate_pack(pack, context=_context())
    report = finalize_validation_report(
        result,
        annotations_json_sha256=DIGEST_B,
        package_sha256=DIGEST_C,
    )
    wire = report.to_wire()

    assert (
        tuple(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(wire)) == ()
    )
    assert set(wire) == {
        "schema_version",
        "validator_version",
        "status",
        "producer",
        "adapter_version",
        "pack_id",
        "semantic_digest",
        "input_snapshot_digest",
        "annotations_json_sha256",
        "package_sha256",
        "counts",
        "findings",
    }
    assert wire["pack_id"] == pack["id"]
    assert wire["semantic_digest"] == semantic_digest(pack)
    assert wire["input_snapshot_digest"] == DIGEST_A
    assert wire["producer"] == PRODUCER
    assert wire["adapter_version"] == ADAPTER_VERSION
    assert wire["annotations_json_sha256"] == DIGEST_B
    assert wire["package_sha256"] == DIGEST_C
    assert wire["counts"] == {
        "input": 2,
        "exported": 2,
        "skipped": 0,
        "warnings": 0,
        "errors": 0,
    }
    assert serialize_validation_report(report) == canonical_json_bytes(wire)
    assert report.canonical_bytes() == serialize_validation_report(report)
    assert report.canonical_bytes().endswith(b"\n")
    with pytest.raises(FrozenInstanceError):
        report.status = "failed"  # type: ignore[misc]


def test_publishable_report_requires_artifact_and_internal_report_context() -> None:
    complete = validate_pack(_valid_pack(), context=_context())
    with pytest.raises(ValueError, match="annotations JSON digest"):
        finalize_validation_report(
            complete,
            annotations_json_sha256=None,
            package_sha256=None,
        )

    incomplete = validate_pack(_valid_pack())
    with pytest.raises(ValueError, match="fields are incomplete"):
        finalize_validation_report(
            incomplete,
            annotations_json_sha256=DIGEST_B,
            package_sha256=None,
        )


def test_package_digest_never_exists_without_annotations_json_digest() -> None:
    failed = make_validation_failure("source_asset_missing_or_not_epub", input_count=1)
    with pytest.raises(ValueError, match="package digest requires"):
        finalize_validation_report(
            failed,
            annotations_json_sha256=None,
            package_sha256=DIGEST_C,
        )

    report = finalize_validation_report(
        failed,
        annotations_json_sha256=None,
        package_sha256=None,
    )
    with pytest.raises(ValueError, match="package digest requires"):
        validation_report_wire(replace(report, package_sha256=DIGEST_C))


def test_prepack_failure_can_finalize_a_schema_valid_null_identity_report() -> None:
    result = make_validation_failure("source_asset_missing_or_not_epub", input_count=1)
    report = finalize_validation_report(
        result,
        annotations_json_sha256=None,
        package_sha256=None,
    )

    assert report.status == "failed"
    assert report.pack_id is None
    assert report.semantic_digest is None
    assert report.input_snapshot_digest is None
    assert report.producer is None
    assert report.adapter_version is None
    assert (
        tuple(
            auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(
                report.to_wire()
            )
        )
        == ()
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda result: replace(result, warning_count=0),
        lambda result: replace(result, status="degraded"),
        lambda result: replace(result, semantic_digest="A" * 64),
        lambda result: replace(result, input_snapshot_digest=None),
        lambda result: replace(result, producer=None),
        lambda result: replace(
            result,
            findings=(
                replace(result.findings[0], message="PRIVATE /Users/alice/export"),
            ),
        ),
    ],
)
def test_finalize_rejects_mutated_result_claims(mutate) -> None:
    warning = make_validation_finding("invalid_publication_metadata", "warning")
    result = validate_pack(
        _valid_pack(),
        context=_context(findings=(warning,)),
    )
    forged = mutate(result)

    with pytest.raises(ValueError):
        finalize_validation_report(
            forged,
            annotations_json_sha256=DIGEST_B,
            package_sha256=None,
        )


def test_direct_report_wire_rejects_incoherent_or_forged_claims() -> None:
    result = validate_pack(_valid_pack(), context=_context())
    report = finalize_validation_report(
        result,
        annotations_json_sha256=DIGEST_B,
        package_sha256=None,
    )
    forged_finding = ValidationFinding(
        code="invalid_publication_metadata",
        severity="warning",
        message="PRIVATE /Users/alice/export",
    )

    for forged in (
        replace(report, input_count=3),
        replace(report, producer="file:///tmp/private"),
        replace(report, findings=(forged_finding,), warning_count=1),
    ):
        with pytest.raises(ValueError):
            validation_report_wire(forged)
        with pytest.raises(ValueError):
            serialize_validation_report(forged)


def test_validation_trust_boundaries_reject_dataclass_subclasses() -> None:
    valid_result = validate_pack(_valid_pack(), context=_context())
    valid_report = finalize_validation_report(
        valid_result,
        annotations_json_sha256=DIGEST_B,
        package_sha256=None,
    )

    class DynamicContext(ValidationContext):
        pass

    with pytest.raises(TypeError, match="ValidationContext"):
        validate_pack(_valid_pack(), context=DynamicContext())

    class DynamicResult(ValidationResult):
        pass

    result_subclass = DynamicResult(
        **{
            field.name: getattr(valid_result, field.name)
            for field in fields(valid_result)
        }
    )
    with pytest.raises(TypeError, match="ValidationResult"):
        finalize_validation_report(
            result_subclass,
            annotations_json_sha256=DIGEST_B,
            package_sha256=None,
        )

    class DynamicReport(ValidationReport):
        pass

    report_subclass = DynamicReport(
        **{
            field.name: getattr(valid_report, field.name)
            for field in fields(valid_report)
        }
    )
    with pytest.raises(TypeError, match="ValidationReport"):
        validation_report_wire(report_subclass)


def test_validation_and_serialization_snapshot_switching_mapping_once() -> None:
    clean = _valid_pack()
    leaked = deepcopy(clean)
    leaked["about"]["dc:title"] = "/Users/alice/private-export"

    validation_input = _SwitchMapping(clean, leaked)
    assert validate_pack(validation_input).status == "valid"
    assert validation_input.item_reads == 1

    leaked_first = _SwitchMapping(leaked, clean)
    assert "private_field_leakage" in _codes(validate_pack(leaked_first))
    assert leaked_first.item_reads == 1

    serialization_input = _SwitchMapping(clean, leaked)
    serialized = serialize_pack(serialization_input)
    assert serialized == canonical_json_bytes(clean)
    assert b"/Users/alice" not in serialized
    assert serialization_input.item_reads == 1


@pytest.mark.parametrize("failure_kind", ["property", "call"])
def test_serialize_pack_sanitizes_hostile_wire_model_exceptions(
    failure_kind: str,
) -> None:
    private_text = "/Users/alice/private-export.json"

    class HostileProperty:
        @property
        def model_dump(self):
            raise RuntimeError(private_text)

    class HostileCall:
        def model_dump(self, **_kwargs):
            raise RuntimeError(private_text)

    hostile = HostileProperty() if failure_kind == "property" else HostileCall()
    with pytest.raises(CanonicalJsonError) as raised:
        serialize_pack(hostile)

    assert private_text not in str(raised.value)
    assert raised.value.__cause__ is None


def test_serialize_pack_is_a_validation_gate_but_generic_encoder_is_not() -> None:
    valid = _valid_pack()
    assert serialize_pack(valid) == canonical_json_bytes(valid)

    invalid = _valid_pack()
    invalid["sr:semanticDigest"] = {"sr:value": DIGEST_A}
    assert canonical_json_bytes(invalid)
    with pytest.raises(CanonicalJsonError, match="schema or semantic validation"):
        serialize_pack(invalid)

    empty = _valid_pack()
    empty["items"] = []
    assert serialize_pack(empty) == canonical_json_bytes(empty)


def test_error_catalog_and_report_schema_cover_current_pipeline_layers() -> None:
    required = {
        "schema_validation_failed",
        "publication_identity_missing",
        "duplicate_pack_or_track_id_semantics",
        "duplicate_annotation_id",
        "item_order_invalid",
        "private_field_leakage",
        "invalid_generated_timestamp",
        "unsupported_kind",
        "invalid_annotation_timestamp",
        "highlight_body_present",
        "note_body_missing",
        "malformed_source_span",
        "unresolved_source_quote",
        "target_href_not_in_manifest",
        "body_looks_like_source_copy",
        "empty_track",
        "validation_context_invalid",
        "source_asset_missing_or_not_epub",
        "unsupported_legacy_record",
        "package_entry_invalid",
    }
    assert required <= ERROR_CATALOG
    assert {
        "schema_validation_failed",
        "duplicate_pack_or_track_id_semantics",
        "duplicate_annotation_id",
        "item_order_invalid",
        "private_field_leakage",
    } <= PACK_VALIDATOR_CODES
    assert {
        "malformed_source_span",
        "unresolved_source_quote",
        "target_href_not_in_manifest",
        "unsupported_legacy_record",
    } <= UPSTREAM_VALIDATION_CODES
    assert FUTURE_PIPELINE_CODES == {
        "deliverable_not_implemented",
        "publication_pointer_invalid",
        "validation_report_invalid",
        "package_entry_invalid",
    }
    Draft202012Validator.check_schema(json.loads(REPORT_SCHEMA.read_text()))
