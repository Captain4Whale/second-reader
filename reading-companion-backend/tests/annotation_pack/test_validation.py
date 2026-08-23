from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from src.annotation_pack.drafts import ValidationFinding
from src.annotation_pack.ids import (
    anchor_id,
    annotation_id,
    edition_id,
    file_id,
    pack_id,
    provisional_work_id,
    track_id,
)
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
    serialize_validation_report,
    validate_pack,
    validation_report_wire,
)


ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "contract/annotation-pack/v0/examples/minimal-pack.json"
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


class _SwitchMapping(Mapping[str, object]):
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


def _valid_pack() -> dict[str, object]:
    pack = json.loads(EXAMPLE.read_text())
    about = pack["about"]
    work = about["sr:work"]
    edition = about["sr:edition"]
    file_identity = about["sr:file"]

    work["id"] = provisional_work_id(about["dc:title"], about["dc:creator"])
    edition["id"] = edition_id(edition["sr:contentFingerprint"]["sr:value"])
    file_identity["id"] = file_id(file_identity["sr:sha256"])
    about["dc:identifier"] = [work["id"], edition["id"], file_identity["id"]]

    track = pack["sr:track"]
    track["id"] = track_id(edition["id"], track["creator"]["id"], track["sr:key"])
    pack["id"] = pack_id(edition["id"], track["id"])
    for item in pack["items"]:
        target = item["target"]
        quote = target["selector"][0]
        paragraph = target["selector"][1]
        start = paragraph["sr:start"]
        end = paragraph["sr:end"]
        chapter_digest = target["sr:chapter"]["sr:fingerprint"]["sr:value"]
        target["sr:anchorId"] = anchor_id(
            edition["id"],
            target["source"],
            chapter_digest,
            start_chapter_id=start["sr:chapterId"],
            start_paragraph_index=start["sr:paragraphIndex"],
            start_char_offset=start["sr:charOffset"],
            end_chapter_id=end["sr:chapterId"],
            end_paragraph_index=end["sr:paragraphIndex"],
            end_char_offset=end["sr:charOffset"],
            quote_sha256=hashlib.sha256(quote["exact"].encode()).hexdigest(),
        )
        body_sha = None
        if item["sr:kind"] == "note":
            body_sha = hashlib.sha256(item["body"]["value"].encode()).hexdigest()
        item["id"] = annotation_id(
            track["id"], item["sr:kind"], target["sr:anchorId"], body_sha
        )
    pack["items"].sort(key=lambda item: item["id"])
    _refresh_digest(pack)
    return pack


def _refresh_digest(pack: dict[str, object]) -> None:
    pack["sr:semanticDigest"]["sr:value"] = semantic_digest(pack)


def _refresh_item_identities(pack: dict[str, object]) -> None:
    edition_id_value = pack["about"]["sr:edition"]["id"]
    track_id_value = pack["sr:track"]["id"]
    for item in pack["items"]:
        target = item["target"]
        quote = target["selector"][0]
        paragraph = target["selector"][1]
        start = paragraph["sr:start"]
        end = paragraph["sr:end"]
        chapter_digest = target["sr:chapter"]["sr:fingerprint"]["sr:value"]
        target["sr:anchorId"] = anchor_id(
            edition_id_value,
            target["source"],
            chapter_digest,
            start_chapter_id=start["sr:chapterId"],
            start_paragraph_index=start["sr:paragraphIndex"],
            start_char_offset=start["sr:charOffset"],
            end_chapter_id=end["sr:chapterId"],
            end_paragraph_index=end["sr:paragraphIndex"],
            end_char_offset=end["sr:charOffset"],
            quote_sha256=hashlib.sha256(quote["exact"].encode()).hexdigest(),
        )
        body_sha = None
        if item["sr:kind"] == "note":
            body_sha = hashlib.sha256(item["body"]["value"].encode()).hexdigest()
        item["id"] = annotation_id(
            track_id_value,
            item["sr:kind"],
            target["sr:anchorId"],
            body_sha,
        )
    pack["items"].sort(key=lambda item: item["id"])
    _refresh_digest(pack)


def _codes(result: object) -> list[str]:
    return [finding.code for finding in result.findings]


def _first_item(pack: dict[str, object]) -> dict[str, object]:
    return pack["items"][0]


def test_valid_pack_and_frozen_pre_artifact_result() -> None:
    result = validate_pack(_valid_pack())

    assert result.status == "valid"
    assert result.publishable
    assert (result.input_count, result.exported_count) == (2, 2)
    assert result.findings == ()
    with pytest.raises(FrozenInstanceError):
        result.status = "failed"
    assert not hasattr(result, "annotations_json_sha256")


def test_empty_policy_is_explicit_and_warning_does_not_degrade() -> None:
    pack = _valid_pack()
    pack["items"] = []
    _refresh_digest(pack)

    rejected = validate_pack(pack)
    accepted = validate_pack(pack, context=ValidationContext(allow_empty=True))

    assert rejected.status == "failed"
    assert _codes(rejected) == ["empty_track"]
    assert accepted.status == "valid"
    assert accepted.warning_count == 1
    assert _codes(accepted) == ["empty_track"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda pack: pack.__setitem__("sr:schemaVersion", "0.2.0"),
            "schema_version_unsupported",
        ),
        (
            lambda pack: pack.__setitem__("generated", "2026-08-23T00:00:00+00:00"),
            "invalid_generated_timestamp",
        ),
        (lambda pack: pack.pop("about"), "publication_identity_missing"),
        (
            lambda pack: _first_item(pack).__setitem__("sr:kind", "bookmark"),
            "unsupported_kind",
        ),
        (
            lambda pack: _first_item(pack).__setitem__("created", "yesterday"),
            "invalid_annotation_timestamp",
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


def test_safe_core_json_pointers_are_preserved_and_private_segments_are_removed() -> (
    None
):
    pack = _valid_pack()
    pack["generated"] = "not-a-timestamp"
    result = validate_pack(pack)
    generated = next(
        finding
        for finding in result.findings
        if finding.code == "invalid_generated_timestamp"
    )
    assert generated.json_pointer == "/generated"

    hostile = ValidationFinding(
        code="cfi_unverified",
        severity="warning",
        message="ignored caller text",
        json_pointer="/Users/alice/private.json",
    )
    sanitized = validate_pack(
        _valid_pack(),
        context=ValidationContext(findings=(hostile,)),
    )
    warning = next(
        finding for finding in sanitized.findings if finding.code == "cfi_unverified"
    )
    assert warning.json_pointer is None
    assert "validation_context_invalid" in _codes(sanitized)


def test_highlight_and_note_body_schema_errors_are_specific() -> None:
    highlight_pack = _valid_pack()
    highlight = next(
        item for item in highlight_pack["items"] if item["sr:kind"] == "highlight"
    )
    highlight["body"] = {
        "type": "TextualBody",
        "value": "private",
        "format": "text/plain",
    }
    note_pack = _valid_pack()
    note = next(item for item in note_pack["items"] if item["sr:kind"] == "note")
    note.pop("body")

    assert "highlight_body_present" in _codes(validate_pack(highlight_pack))
    assert "note_body_missing" in _codes(validate_pack(note_pack))


@pytest.mark.parametrize("identity", ["work", "edition", "file", "track", "pack"])
def test_id_recomputation_detects_identity_tampering(identity: str) -> None:
    pack = _valid_pack()
    replacement = "urn:uuid:00000000-0000-5000-8000-000000000000"
    if identity in {"work", "edition", "file"}:
        pack["about"][f"sr:{identity}"]["id"] = replacement
        pack["about"]["dc:identifier"][
            {"work": 0, "edition": 1, "file": 2}[identity]
        ] = replacement
    elif identity == "track":
        pack["sr:track"]["id"] = replacement
    else:
        pack["id"] = replacement
    _refresh_digest(pack)

    result = validate_pack(pack)

    expected = (
        "publication_identity_missing"
        if identity in {"work", "edition", "file"}
        else "duplicate_pack_or_track_id_semantics"
    )
    assert expected in _codes(result)


def test_verify_ids_false_only_disables_id_recomputation() -> None:
    pack = _valid_pack()
    pack["id"] = "urn:uuid:00000000-0000-5000-8000-000000000000"
    _refresh_digest(pack)

    assert validate_pack(pack).status == "failed"
    assert validate_pack(pack, verify_ids=False).status == "valid"


def test_semantic_digest_creator_sort_and_chapter_coherence() -> None:
    digest_pack = _valid_pack()
    digest_pack["sr:semanticDigest"]["sr:value"] = "0" * 64
    assert "semantic_digest_mismatch" in _codes(validate_pack(digest_pack))

    creator_pack = _valid_pack()
    _first_item(creator_pack)["creator"]["name"] = "Other"
    _refresh_digest(creator_pack)
    assert "creator_mismatch" in _codes(validate_pack(creator_pack))

    order_pack = _valid_pack()
    order_pack["items"].reverse()
    _refresh_digest(order_pack)
    assert "item_order_invalid" in _codes(validate_pack(order_pack))

    chapter_pack = _valid_pack()
    _first_item(chapter_pack)["target"]["sr:chapter"]["name"] = "Wrong"
    _refresh_digest(chapter_pack)
    assert "chapter_context_mismatch" in _codes(validate_pack(chapter_pack))


def test_dc_identifier_must_contain_work_edition_and_file_ids() -> None:
    pack = _valid_pack()
    pack["about"]["dc:identifier"][0] = "urn:uuid:00000000-0000-5000-8000-000000000000"
    _refresh_digest(pack)

    assert "publication_identity_missing" in _codes(validate_pack(pack))


@pytest.mark.parametrize(
    ("container_path", "field", "value"),
    [
        ((), "sr:chapterId", 1),
        (("generator",), "sr:chapterId", 1),
        (("items", 0), "sr:provenance", {}),
        (("about",), "sr:kind", "note"),
        (("generator",), "dc:title", "Wrong location"),
    ],
)
def test_known_core_curies_are_rejected_outside_their_canonical_subschema(
    container_path: tuple[object, ...],
    field: str,
    value: object,
) -> None:
    pack = _valid_pack()
    container: object = pack
    for part in container_path:
        container = container[part]
    container[field] = value
    _refresh_digest(pack)

    result = validate_pack(pack, mode="compatible")

    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)


@pytest.mark.parametrize(
    "coordinates",
    [
        (999, 1, 0, 999, 1, 1),
        (1, 1, 0, 2, 1, 1),
        (1, 3, 0, 1, 2, 0),
        (1, 2, 8, 1, 2, 7),
        (1, 2, 8, 1, 2, 8),
    ],
)
def test_paragraph_coordinates_match_target_chapter_and_are_strictly_ordered(
    coordinates: tuple[int, int, int, int, int, int],
) -> None:
    pack = _valid_pack()
    target = _first_item(pack)["target"]
    paragraph = target["selector"][1]
    start_chapter, start_paragraph, start_char, end_chapter, end_paragraph, end_char = (
        coordinates
    )
    paragraph["sr:start"] = {
        "sr:chapterId": start_chapter,
        "sr:paragraphIndex": start_paragraph,
        "sr:charOffset": start_char,
    }
    paragraph["sr:end"] = {
        "sr:chapterId": end_chapter,
        "sr:paragraphIndex": end_paragraph,
        "sr:charOffset": end_char,
    }
    _refresh_item_identities(pack)

    assert "chapter_context_mismatch" in _codes(validate_pack(pack))


@pytest.mark.parametrize(
    "unsafe_href",
    [
        "%2e%2e/private.xhtml",
        "Text%2fchapter.xhtml",
        "Text\\chapter.xhtml",
        "./Text/chapter.xhtml",
        "Text/%63hapter.xhtml",
        "Text/e\u0301.xhtml",
    ],
)
def test_target_href_must_be_exact_canonical_epub_href_even_without_public_index(
    unsafe_href: str,
) -> None:
    pack = _valid_pack()
    chapter = pack["about"]["sr:edition"]["sr:chapterFingerprints"][0]
    chapter.pop("sr:resourceHrefs", None)
    _first_item(pack)["target"]["source"] = unsafe_href
    _refresh_item_identities(pack)

    assert {
        "target_href_not_in_manifest",
        "schema_validation_failed",
    } & set(_codes(validate_pack(pack)))


def test_synchronized_unsafe_target_and_publication_hrefs_still_fail() -> None:
    pack = _valid_pack()
    unsafe_href = "%2e%2e/private.xhtml"
    chapter = pack["about"]["sr:edition"]["sr:chapterFingerprints"][0]
    chapter["sr:resourceHrefs"] = [unsafe_href]
    for item in pack["items"]:
        item["target"]["source"] = unsafe_href
    _refresh_item_identities(pack)

    codes = _codes(validate_pack(pack))

    assert "publication_identity_missing" in codes
    assert "target_href_not_in_manifest" in codes


def test_same_anchor_reuse_is_legal_and_optional_cfi_does_not_change_semantics() -> (
    None
):
    pack = _valid_pack()
    highlight = next(item for item in pack["items"] if item["sr:kind"] == "highlight")
    note = next(item for item in pack["items"] if item["sr:kind"] == "note")
    note["target"] = deepcopy(highlight["target"])
    note["target"]["selector"].append(
        {
            "type": "sr:EpubCfiSelector",
            "value": "epubcfi(/6/4!/4/2,/1:1,/1:2)",
            "sr:verification": "quote-round-trip",
        }
    )
    body_sha = hashlib.sha256(note["body"]["value"].encode()).hexdigest()
    note["id"] = annotation_id(
        pack["sr:track"]["id"], "note", note["target"]["sr:anchorId"], body_sha
    )
    pack["items"].sort(key=lambda item: item["id"])
    _refresh_digest(pack)

    assert validate_pack(pack).status == "valid"


@pytest.mark.parametrize(
    ("cfi", "private"),
    [
        ("epubcfi(/6/4!/4/2,/1:1,/1:2)", False),
        ("epubcfi(/6/4[chapter-7]!/4/2/2)", False),
        ("epubcfi(/6/4!/Users/alice/private)", True),
        ("epubcfi(/6/4!/opt/agent/private)", True),
        ("epubcfi(/6/4!/workspace/agent/private)", True),
        ("epubcfi(file:///tmp/private.json)", True),
        ("epubcfi(~/private/book.xhtml)", True),
        ("epubcfi(/6/4!?token=secret)", True),
    ],
)
def test_optional_cfi_has_a_path_aware_privacy_gate(cfi: str, private: bool) -> None:
    pack = _valid_pack()
    _first_item(pack)["target"]["selector"].append(
        {
            "type": "sr:EpubCfiSelector",
            "value": cfi,
            "sr:verification": "quote-round-trip",
        }
    )
    _refresh_digest(pack)

    result = validate_pack(pack)

    assert ("private_field_leakage" in _codes(result)) is private
    if private:
        assert cfi not in " ".join(finding.message for finding in result.findings)
    else:
        assert result.status == "valid"


def test_anchor_collision_and_semantic_duplicate_are_rejected_without_id_checks() -> (
    None
):
    collision = _valid_pack()
    second = collision["items"][1]
    second["target"]["sr:anchorId"] = collision["items"][0]["target"]["sr:anchorId"]
    _refresh_digest(collision)
    assert "duplicate_anchor_semantics" in _codes(
        validate_pack(collision, verify_ids=False)
    )

    duplicate = _valid_pack()
    duplicate["items"].append(deepcopy(duplicate["items"][0]))
    _refresh_digest(duplicate)
    assert "duplicate_annotation_id" in _codes(
        validate_pack(duplicate, verify_ids=False)
    )


def test_strict_and_compatible_declared_extension_policy() -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["items"][0]["ex:confidence"] = {"ex:value": "high"}
    _refresh_digest(pack)

    strict = validate_pack(pack, mode="strict")
    compatible = validate_pack(pack, mode="compatible")

    assert strict.status == "failed"
    assert set(_codes(strict)) == {"unknown_declared_extension"}
    assert compatible.status == "valid"
    assert compatible.warning_count >= 1
    assert set(_codes(compatible)) == {"unknown_declared_extension"}


def test_undeclared_reserved_and_private_namespace_prefixes_are_fatal() -> None:
    undeclared = _valid_pack()
    undeclared["ex:value"] = True
    _refresh_digest(undeclared)
    assert "unknown_extension_prefix" in _codes(
        validate_pack(undeclared, mode="compatible")
    )

    reserved = _valid_pack()
    reserved["@context"][1]["dc"] = "https://example.org/redefined#"
    _refresh_digest(reserved)
    assert "reserved_prefix_redefinition" in _codes(
        validate_pack(reserved, mode="compatible")
    )

    private = _valid_pack()
    private["@context"][1]["ex"] = "https://127.0.0.1/private#"
    _refresh_digest(private)
    assert "unknown_extension_prefix" in _codes(
        validate_pack(private, mode="compatible")
    )


def test_unknown_unprefixed_and_deep_extension_are_rejected() -> None:
    unprefixed = _valid_pack()
    unprefixed["mystery"] = True
    assert "schema_validation_failed" in _codes(validate_pack(unprefixed))

    deep = _valid_pack()
    deep["@context"][1]["ex"] = "https://example.org/annotation#"
    value: dict[str, object] = {}
    cursor = value
    for _ in range(20):
        child: dict[str, object] = {}
        cursor["next"] = child
        cursor = child
    deep["ex:data"] = value
    _refresh_digest(deep)
    assert "extension_limit_exceeded" in _codes(validate_pack(deep, mode="compatible"))


@pytest.mark.parametrize(
    "private_value",
    [
        "/Users/alice/private/book.epub",
        "/srv/private/book.epub",
        "file:///tmp/private.json",
        "https://example.org/public?access_token=secret",
        "https://127.0.0.1/private",
    ],
)
def test_private_metadata_values_are_rejected_without_echo(private_value: str) -> None:
    pack = _valid_pack()
    pack["generator"]["id"] = private_value

    result = validate_pack(pack)
    encoded = json.dumps(
        [
            finding.__dict__ if hasattr(finding, "__dict__") else finding.message
            for finding in result.findings
        ]
    )

    assert "private_field_leakage" in _codes(result)
    assert private_value not in encoded


@pytest.mark.parametrize(
    "private_key",
    [
        "selection_reason",
        "feedback",
        "user_rating",
        "download_url",
        "rank",
        "runtime_trace",
        "ｒｅａｓｏｎｉｎｇ",
        "ｐｒｏｍｐｔ",
        "api_key",
        "access_token",
        "password",
        "secret",
        "credential",
        "authorization",
        "cookie",
        "ａｐｉ＿ｋｅｙ",
    ],
)
def test_private_keys_are_rejected_but_prose_false_positives_are_avoided(
    private_key: str,
) -> None:
    leaked = _valid_pack()
    leaked["@context"][1]["ex"] = "https://example.org/annotation#"
    leaked[f"ex:{private_key}"] = "not reportable"
    assert "private_field_leakage" in _codes(validate_pack(leaked, mode="compatible"))

    prose = _valid_pack()
    note = next(item for item in prose["items"] if item["sr:kind"] == "note")
    note["body"]["value"] = (
        "Ordinary prose may mention reasoning, /etc/passwd, and "
        "https://example.org/?token=fiction without becoming runtime provenance."
    )
    body_sha = hashlib.sha256(note["body"]["value"].encode()).hexdigest()
    note["id"] = annotation_id(
        prose["sr:track"]["id"], "note", note["target"]["sr:anchorId"], body_sha
    )
    prose["items"].sort(key=lambda item: item["id"])
    _refresh_digest(prose)
    assert "private_field_leakage" not in _codes(validate_pack(prose))


def test_body_extension_value_does_not_inherit_prose_privacy_exemption() -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    note = next(item for item in pack["items"] if item["sr:kind"] == "note")
    note["body"]["ex:diagnostic"] = {"value": "/srv/private/book.epub"}
    _refresh_digest(pack)

    assert "private_field_leakage" in _codes(validate_pack(pack, mode="compatible"))


@pytest.mark.parametrize(("length", "warns"), [(511, False), (512, True)])
def test_large_note_body_source_copy_warning_is_bounded_and_non_degrading(
    length: int,
    warns: bool,
) -> None:
    pack = _valid_pack()
    note = next(item for item in pack["items"] if item["sr:kind"] == "note")
    copied_text = "x" * length
    note["target"]["selector"][0]["exact"] = copied_text
    note["body"]["value"] = f"prefix-{copied_text}" if warns else copied_text
    _refresh_item_identities(pack)

    result = validate_pack(pack)

    assert result.status == "valid"
    assert ("body_looks_like_source_copy" in _codes(result)) is warns
    if warns:
        finding = next(
            finding
            for finding in result.findings
            if finding.code == "body_looks_like_source_copy"
        )
        assert copied_text not in finding.message


@pytest.mark.parametrize(
    "private_iri",
    [
        "https://127.0.0.1/private",
        "https://[::1]/private",
        "https://[fd00::1]/private",
        "https://service.internal/private",
        "https://2130706433/private",
        "https://127%2e0%2e0%2e1/private",
        "https://127。0。0。1/private",
        "https://localhost。/private",
        "ftp://127.0.0.1/private",
        "ssh://localhost/private",
        "ws://10.0.0.1/private",
        "file%3A%2F%2F%2Fetc%2Fpasswd",
        "urn:example:/Users/alice/private",
        "urn:file:/etc/passwd",
        "source=/Users/alice/private",
        "x(/srv/private/book.epub)",
        "urn:example:C:\\Users\\alice\\private",
    ],
)
def test_compatible_extension_values_reject_encoded_and_private_iris(
    private_iri: str,
) -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:source"] = private_iri
    _refresh_digest(pack)

    result = validate_pack(pack, mode="compatible")

    assert "private_field_leakage" in _codes(result)
    assert private_iri not in " ".join(finding.message for finding in result.findings)


@pytest.mark.parametrize(
    "public_value",
    [
        "urn:example:public:resource",
        "urn:isbn:9780140328721",
        "https://example.org/public/resource",
        "https://[2606:4700:4700::1111]/public/resource",
        "https://例子.测试/public/resource",
        "Ordinary public metadata prose",
    ],
)
def test_compatible_extension_public_values_avoid_privacy_false_positives(
    public_value: str,
) -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:source"] = public_value
    _refresh_digest(pack)

    result = validate_pack(pack, mode="compatible")

    assert result.status == "valid"
    assert "private_field_leakage" not in _codes(result)


@pytest.mark.parametrize(
    "private_prose",
    [
        "See https://127.0.0.1/admin for details.",
        "See https://user:secret@example.org/data for details.",
        "See https%3A%2F%2F10%2E0%2E0%2E1/private for details.",
        "See https://127。0。0。1/private for details.",
        "See ｈｔｔｐｓ：／／localhost／private for details.",
    ],
)
def test_compatible_extension_prose_rejects_embedded_private_authorities(
    private_prose: str,
) -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:description"] = private_prose
    _refresh_digest(pack)

    result = validate_pack(pack, mode="compatible")

    assert "private_field_leakage" in _codes(result)
    assert private_prose not in " ".join(finding.message for finding in result.findings)


@pytest.mark.parametrize(
    "public_prose",
    [
        "Read https://example.org/public/resource, then continue.",
        "Mirror https://[2606:4700:4700::1111]/index for public access.",
        "Read https://例子.测试/public/resource for details.",
    ],
)
def test_compatible_extension_prose_accepts_embedded_public_authorities(
    public_prose: str,
) -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:description"] = public_prose
    _refresh_digest(pack)

    result = validate_pack(pack, mode="compatible")

    assert result.status == "valid"
    assert "private_field_leakage" not in _codes(result)


def test_extra_dc_identifier_must_be_a_safe_public_iri() -> None:
    pack = _valid_pack()
    private_iri = "https://127.0.0.1/private"
    pack["about"]["dc:identifier"].append(private_iri)
    _refresh_digest(pack)

    result = validate_pack(pack)

    assert "private_field_leakage" in _codes(result)
    assert private_iri not in " ".join(finding.message for finding in result.findings)


def test_extra_dc_identifier_accepts_a_legal_public_urn() -> None:
    pack = _valid_pack()
    pack["about"]["dc:identifier"].append("urn:example:public:resource")
    _refresh_digest(pack)

    assert validate_pack(pack).status == "valid"


@pytest.mark.parametrize("marker", ["attentional_v2", "iterator_reader"])
def test_bare_mechanism_markers_are_rejected_in_extension_values(marker: str) -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:producerDetail"] = marker
    _refresh_digest(pack)

    assert "private_field_leakage" in _codes(validate_pack(pack, mode="compatible"))


def test_depth_cycle_float_and_unsafe_integer_fail_closed() -> None:
    deep = _valid_pack()
    value: dict[str, object] = {}
    cursor = value
    for _ in range(70):
        child: dict[str, object] = {}
        cursor["next"] = child
        cursor = child
    deep["nested"] = value
    assert "document_limit_exceeded" in _codes(validate_pack(deep))

    cycle = _valid_pack()
    cycle["cycle"] = cycle
    assert validate_pack(cycle).status == "failed"

    floating = _valid_pack()
    floating["float"] = 1.5
    assert validate_pack(floating).status == "failed"

    integer = _valid_pack()
    integer["integer"] = 2**53
    assert validate_pack(integer).status == "failed"


def test_preflight_rejects_scalar_subclasses_without_executing_overrides() -> None:
    private_text = "PRIVATE /Users/alice/export.json"

    class HostileString(str):
        callbacks = 0

        @classmethod
        def _explode(cls):
            cls.callbacks += 1
            raise RuntimeError(private_text)

        def __len__(self) -> int:
            return type(self)._explode()

        def encode(self, *_args, **_kwargs):
            return type(self)._explode()

        def casefold(self) -> str:
            return type(self)._explode()

        def rsplit(self, *_args, **_kwargs):
            return type(self)._explode()

    class HostileInteger(int):
        callbacks = 0

        @classmethod
        def _explode(cls):
            cls.callbacks += 1
            raise RuntimeError(private_text)

        def __eq__(self, _other: object) -> bool:
            return type(self)._explode()

        def __lt__(self, _other: object) -> bool:
            return type(self)._explode()

        def __int__(self) -> int:
            return type(self)._explode()

    hostile_value = _valid_pack()
    hostile_value["generated"] = HostileString(hostile_value["generated"])

    hostile_key = _valid_pack()
    hostile_key[HostileString("hostile-key")] = True

    hostile_integer = _valid_pack()
    hostile_integer["about"]["sr:file"]["sr:byteLength"] = HostileInteger(4096)

    for pack in (hostile_value, hostile_key, hostile_integer):
        result = validate_pack(pack)
        assert result.status == "failed"
        assert not result.publishable
        assert "schema_validation_failed" in _codes(result)
        assert private_text not in json.dumps(
            [finding.message for finding in result.findings]
        )

    assert HostileString.callbacks == 0
    assert HostileInteger.callbacks == 0


def test_upstream_skips_create_degraded_result_and_messages_are_sanitized() -> None:
    pack = _valid_pack()
    pack["items"] = pack["items"][:1]
    _refresh_digest(pack)
    source_digest = "c" * 64
    context = ValidationContext(
        input_count=2,
        findings=(
            ValidationFinding(
                code="ambiguous_source_quote",
                severity="skipped",
                message="PRIVATE /Users/alice/book.epub full quote",
                source_record_index=7,
                source_record_digest=source_digest,
            ),
        ),
    )

    result = validate_pack(pack, context=context)

    assert result.status == "degraded"
    assert (result.input_count, result.exported_count, result.skipped_count) == (
        2,
        1,
        1,
    )
    assert result.error_count == 0
    assert result.findings[0].message == "The source quote does not resolve uniquely."
    assert "/Users/" not in result.findings[0].message


def test_warning_only_context_stays_valid_and_invalid_accounting_fails() -> None:
    pack = _valid_pack()
    warning = ValidationFinding(
        code="cfi_unverified",
        severity="warning",
        message="unsafe caller text",
    )
    assert (
        validate_pack(
            pack, context=ValidationContext(input_count=2, findings=(warning,))
        ).status
        == "valid"
    )
    invalid = validate_pack(pack, context=ValidationContext(input_count=3))
    assert invalid.status == "failed"
    assert "validation_context_invalid" in _codes(invalid)


def test_report_finalization_schema_counts_and_canonical_bytes() -> None:
    result = validate_pack(_valid_pack())
    report = finalize_validation_report(
        result,
        annotations_json_sha256=DIGEST_A,
        package_sha256=None,
    )
    wire = report.to_wire()
    errors = tuple(auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(wire))

    assert errors == ()
    assert wire["counts"] == {
        "input": 2,
        "exported": 2,
        "skipped": 0,
        "warnings": 0,
        "errors": 0,
    }
    assert wire["annotations_json_sha256"] == DIGEST_A
    assert wire["package_sha256"] is None
    assert serialize_validation_report(report) == report.canonical_bytes()
    assert report.canonical_bytes().endswith(b"\n")


def test_finalize_requires_artifact_digest_and_rejects_mutated_result_claims() -> None:
    result = validate_pack(_valid_pack())
    with pytest.raises(ValueError, match="annotations JSON digest"):
        finalize_validation_report(
            result,
            annotations_json_sha256=None,
            package_sha256=None,
        )
    with pytest.raises(ValueError, match="counts or status"):
        finalize_validation_report(
            replace(result, warning_count=1),
            annotations_json_sha256=DIGEST_A,
            package_sha256=DIGEST_B,
        )


def test_package_digest_never_exists_without_annotations_json_digest() -> None:
    invalid = _valid_pack()
    invalid["sr:semanticDigest"]["sr:value"] = "0" * 64
    result = validate_pack(invalid)

    with pytest.raises(ValueError, match="package digest requires"):
        finalize_validation_report(
            result,
            annotations_json_sha256=None,
            package_sha256=DIGEST_B,
        )

    report = finalize_validation_report(
        result,
        annotations_json_sha256=None,
        package_sha256=None,
    )
    with pytest.raises(ValueError, match="package digest requires"):
        validation_report_wire(replace(report, package_sha256=DIGEST_B))


def test_policy_dependent_fatal_findings_can_finalize_failed_reports() -> None:
    empty = _valid_pack()
    empty["items"] = []
    _refresh_digest(empty)
    empty_result = validate_pack(empty)
    assert (
        finalize_validation_report(
            empty_result,
            annotations_json_sha256=None,
            package_sha256=None,
        ).status
        == "failed"
    )

    extension = _valid_pack()
    extension["@context"][1]["ex"] = "https://example.org/annotation#"
    extension["ex:value"] = True
    _refresh_digest(extension)
    extension_result = validate_pack(extension, mode="strict")
    assert (
        finalize_validation_report(
            extension_result,
            annotations_json_sha256=None,
            package_sha256=None,
        ).status
        == "failed"
    )


def test_finalize_rejects_forged_findings_before_they_reach_report_wire() -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:value"] = True
    _refresh_digest(pack)
    result = validate_pack(pack, mode="compatible")
    finding = result.findings[0]

    for forged in (
        replace(finding, message="PRIVATE /Users/alice/export.json"),
        replace(finding, json_pointer="/Users/alice/export.json"),
    ):
        with pytest.raises(ValueError, match="validation findings"):
            finalize_validation_report(
                replace(result, findings=(forged,)),
                annotations_json_sha256=DIGEST_A,
                package_sha256=None,
            )

    with pytest.raises(ValueError, match="validation findings"):
        finalize_validation_report(
            replace(result, findings=(object(),)),
            annotations_json_sha256=DIGEST_A,
            package_sha256=None,
        )


def test_direct_report_wire_and_serializer_reject_forged_finding() -> None:
    pack = _valid_pack()
    pack["@context"][1]["ex"] = "https://example.org/annotation#"
    pack["ex:value"] = True
    _refresh_digest(pack)
    result = validate_pack(pack, mode="compatible")
    report = finalize_validation_report(
        result,
        annotations_json_sha256=DIGEST_A,
        package_sha256=None,
    )
    forged = replace(
        report,
        findings=(
            replace(
                report.findings[0],
                message="PRIVATE /Users/alice/export.json",
                json_pointer="/Users/alice/export.json",
            ),
        ),
    )

    with pytest.raises(ValueError, match="validation findings"):
        validation_report_wire(forged)
    with pytest.raises(ValueError, match="validation findings"):
        serialize_validation_report(forged)


def test_validation_trust_boundaries_reject_subclass_overrides() -> None:
    private_text = "PRIVATE /Users/alice/export.json"

    class DynamicFinding(ValidationFinding):
        reads = 0

        def __getattribute__(self, name: str):
            if name == "message":
                type(self).reads += 1
                return (
                    "The optional EPUB CFI was omitted because round-trip "
                    "verification failed."
                    if type(self).reads == 1
                    else private_text
                )
            return super().__getattribute__(name)

    dynamic_finding = DynamicFinding(
        code="cfi_unverified",
        severity="warning",
        message="constructor value is never trusted",
    )
    context_result = validate_pack(
        _valid_pack(),
        context=ValidationContext(findings=(dynamic_finding,)),
    )
    assert "validation_context_invalid" in _codes(context_result)
    assert DynamicFinding.reads == 0

    valid_result = validate_pack(_valid_pack())
    with pytest.raises(ValueError, match="validation findings"):
        finalize_validation_report(
            replace(valid_result, findings=(dynamic_finding,)),
            annotations_json_sha256=DIGEST_A,
            package_sha256=None,
        )
    assert DynamicFinding.reads == 0

    valid_report = finalize_validation_report(
        valid_result,
        annotations_json_sha256=DIGEST_A,
        package_sha256=None,
    )
    with pytest.raises(ValueError, match="validation findings"):
        validation_report_wire(replace(valid_report, findings=(dynamic_finding,)))
    assert DynamicFinding.reads == 0

    class DynamicContext(ValidationContext):
        def __getattribute__(self, name: str):
            if name == "findings":
                raise AssertionError(private_text)
            return super().__getattribute__(name)

    with pytest.raises(TypeError, match="ValidationContext"):
        validate_pack(_valid_pack(), context=DynamicContext())

    class DynamicResult(ValidationResult):
        def __getattribute__(self, name: str):
            if name == "status":
                raise AssertionError(private_text)
            return super().__getattribute__(name)

    result_subclass = DynamicResult(
        **{
            field.name: getattr(valid_result, field.name)
            for field in fields(valid_result)
        }
    )
    with pytest.raises(TypeError, match="ValidationResult"):
        finalize_validation_report(
            result_subclass,
            annotations_json_sha256=DIGEST_A,
            package_sha256=None,
        )

    class DynamicReport(ValidationReport):
        def __getattribute__(self, name: str):
            if name == "status":
                raise AssertionError(private_text)
            return super().__getattribute__(name)

    report_subclass = DynamicReport(
        **{
            field.name: getattr(valid_report, field.name)
            for field in fields(valid_report)
        }
    )
    with pytest.raises(TypeError, match="ValidationReport"):
        validation_report_wire(report_subclass)


def test_validation_finding_scalar_subclasses_are_never_executed() -> None:
    class HostileString(str):
        operations = 0

        def __eq__(self, other: object) -> bool:
            type(self).operations += 1
            raise AssertionError("PRIVATE /Users/alice/export.json")

        def __hash__(self) -> int:
            type(self).operations += 1
            raise AssertionError("PRIVATE /Users/alice/export.json")

    class HostileInteger(int):
        operations = 0

        def __lt__(self, other: object) -> bool:
            type(self).operations += 1
            raise AssertionError("PRIVATE /Users/alice/export.json")

    warning = ValidationFinding(
        code="cfi_unverified",
        severity="warning",
        message="The optional EPUB CFI was omitted because round-trip verification failed.",
    )
    hostile_fields: tuple[tuple[str, object], ...] = (
        ("code", HostileString("cfi_unverified")),
        ("severity", HostileString("warning")),
        ("message", HostileString(warning.message)),
        ("json_pointer", HostileString("/items/0")),
        (
            "annotation_id",
            HostileString("urn:uuid:95fc5c02-f70a-50a8-b245-3adfd92cc89a"),
        ),
        ("source_record_digest", HostileString(DIGEST_A)),
        ("source_record_index", HostileInteger(0)),
    )

    valid_result = validate_pack(_valid_pack())
    for field_name, hostile_value in hostile_fields:
        finding = replace(warning, **{field_name: hostile_value})
        context_result = validate_pack(
            _valid_pack(),
            context=ValidationContext(findings=(finding,)),
        )
        assert "validation_context_invalid" in _codes(context_result)
        with pytest.raises(ValueError, match="validation findings"):
            finalize_validation_report(
                replace(valid_result, findings=(finding,)),
                annotations_json_sha256=DIGEST_A,
                package_sha256=None,
            )

    assert HostileString.operations == 0
    assert HostileInteger.operations == 0


def test_failed_result_with_safe_extra_input_accounting_can_be_finalized() -> None:
    result = validate_pack(_valid_pack(), context=ValidationContext(input_count=3))
    assert result.status == "failed"

    report = finalize_validation_report(
        result,
        annotations_json_sha256=None,
        package_sha256=None,
    )

    assert report.status == "failed"
    assert report.input_count == 3
    assert (
        tuple(
            auxiliary_validator(VALIDATION_REPORT_SCHEMA_ID).iter_errors(
                report.to_wire()
            )
        )
        == ()
    )


def test_generic_schema_invalid_pack_can_finalize_a_failed_report() -> None:
    pack = _valid_pack()
    _first_item(pack)["motivation"] = "bookmarking"
    _refresh_digest(pack)
    result = validate_pack(pack)

    assert result.status == "failed"
    assert "schema_validation_failed" in _codes(result)
    assert (
        finalize_validation_report(
            result,
            annotations_json_sha256=None,
            package_sha256=None,
        ).status
        == "failed"
    )


def test_validation_and_serialization_read_a_switching_mapping_only_once() -> None:
    clean = _valid_pack()
    leaked = deepcopy(clean)
    leaked["generator"]["name"] = "/Users/alice/private-export"

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
    invalid["sr:semanticDigest"]["sr:value"] = "0" * 64
    assert canonical_json_bytes(invalid)
    with pytest.raises(CanonicalJsonError, match="schema or semantic validation"):
        serialize_pack(invalid)

    empty = _valid_pack()
    empty["items"] = []
    _refresh_digest(empty)
    assert serialize_pack(empty) == canonical_json_bytes(empty)


def test_error_catalog_distinguishes_pack_upstream_and_future_layers() -> None:
    required = {
        "schema_version_unsupported",
        "source_asset_missing_or_not_epub",
        "publication_substrate_mismatch",
        "publication_identity_missing",
        "input_changed_during_export",
        "active_writer_present",
        "run_state_not_exportable",
        "deliverable_not_implemented",
        "publication_pointer_invalid",
        "validation_report_invalid",
        "duplicate_pack_or_track_id_semantics",
        "duplicate_annotation_id",
        "duplicate_anchor_semantics",
        "private_field_leakage",
        "invalid_generated_timestamp",
        "unsupported_kind",
        "unsupported_legacy_record",
        "invalid_annotation_timestamp",
        "highlight_body_present",
        "note_body_missing",
        "malformed_source_span",
        "grapheme_boundary_split",
        "cross_resource_span",
        "resource_text_unverifiable",
        "non_contiguous_resource_quote",
        "unresolved_source_quote",
        "ambiguous_source_quote",
        "source_quote_too_long",
        "target_href_not_in_manifest",
        "cfi_unverified",
        "quote_not_unique_in_resource",
        "unknown_declared_extension",
        "empty_track",
        "package_entry_invalid",
    }
    assert required <= ERROR_CATALOG
    assert "schema_version_unsupported" in PACK_VALIDATOR_CODES
    assert "malformed_source_span" in UPSTREAM_VALIDATION_CODES
    assert FUTURE_PIPELINE_CODES == {
        "deliverable_not_implemented",
        "publication_pointer_invalid",
        "validation_report_invalid",
        "package_entry_invalid",
    }
    Draft202012Validator.check_schema(
        json.loads(
            (
                ROOT
                / "contract/annotation-pack/v0/schema/validation-report.schema.json"
            ).read_text()
        )
    )
