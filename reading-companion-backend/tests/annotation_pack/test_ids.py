from __future__ import annotations

from uuid import NAMESPACE_DNS, NAMESPACE_URL, UUID, uuid3, uuid4, uuid5

import pytest

from src.annotation_pack.ids import (
    ANCHOR_NAMESPACE,
    ANNOTATION_NAMESPACE,
    CREATOR_CONTRACT_MAJOR,
    CREATOR_NAMESPACE,
    DEFAULT_SPEC_MAJOR,
    EDITION_NAMESPACE,
    FILE_NAMESPACE,
    GENERATOR_CONTRACT_MAJOR,
    GENERATOR_NAMESPACE,
    PACK_NAMESPACE,
    TRACK_NAMESPACE,
    WORK_NAMESPACE,
    asserted_work_id,
    default_creator_id,
    default_generator_id,
    edition_id,
    file_id,
    pack_id,
    provisional_work_id,
    track_id,
    uuid5_urn,
)


UUID_NAMESPACE_ROOT = (
    "https://captain4whale.github.io/second-reader/ns/annotation-pack/uuid"
)
SHA_A = "a" * 64
SHA_B = "b" * 64

ASSERTED_WORK_VECTOR = "urn:uuid:3b4892bf-906d-5ce7-abb6-eddf81499d3f"
PROVISIONAL_WORK_VECTOR = "urn:uuid:a532f7fa-7ee6-55da-bea9-c07af08f837d"
EDITION_VECTOR = "urn:uuid:f0cc26f5-6a19-5bb6-a067-77098eeb9f08"
FILE_VECTOR = "urn:uuid:ff29774b-4cf0-5351-ac15-9dd1c2274258"
CREATOR_VECTOR = "urn:uuid:c8d82077-7433-5fe9-9075-01f3e3100656"
GENERATOR_VECTOR = "urn:uuid:7da1165a-bf3f-5d18-b2a3-89feb37e9c4e"
TRACK_VECTOR = "urn:uuid:b922476c-c729-51c8-b969-847f87e32b4b"
PACK_VECTOR = "urn:uuid:d52bc66a-c561-5664-b0d0-ccf38ad520bc"


def test_namespace_uuid_literals_match_the_immutable_iri_vectors() -> None:
    expected = {
        "work": (WORK_NAMESPACE, "e818f38e-2894-5910-a94f-afec1212f840"),
        "edition": (EDITION_NAMESPACE, "82f700a5-7f2d-5c1d-902c-7ff9fe327044"),
        "file": (FILE_NAMESPACE, "9755ee25-0dad-51a9-a36d-63589e35707c"),
        "track": (TRACK_NAMESPACE, "011c6a5f-2255-5b98-b86a-8f1a55548652"),
        "pack": (PACK_NAMESPACE, "15a1b369-656b-55cb-bfa1-55a529a1f39e"),
        "anchor": (ANCHOR_NAMESPACE, "3a26c857-f475-506c-a16a-219763fd1ce9"),
        "annotation": (
            ANNOTATION_NAMESPACE,
            "ab5c7848-4a52-5b43-a01b-f76dbce62959",
        ),
        "creator": (CREATOR_NAMESPACE, "e0d4d5df-e315-5db3-9667-3f89a814f602"),
        "generator": (
            GENERATOR_NAMESPACE,
            "dc17bd39-4e7c-574f-9aa0-87d4fe7e927b",
        ),
    }

    for kind, (actual, literal) in expected.items():
        assert str(actual) == literal
        assert actual == uuid5(NAMESPACE_URL, f"{UUID_NAMESPACE_ROOT}/{kind}/v0")
        assert actual.version == 5


def test_uuid5_urn_is_lowercase_canonical_and_rejects_invalid_arguments() -> None:
    result = uuid5_urn(WORK_NAMESPACE, "work\0example")

    assert result == "urn:uuid:72dec445-0667-5b35-a773-1c2e55d2a024"
    assert result == result.lower()
    assert UUID(result).version == 5
    with pytest.raises(TypeError, match="namespace"):
        uuid5_urn("not-a-uuid", "work")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="canonical_name"):
        uuid5_urn(WORK_NAMESPACE, b"work")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="empty"):
        uuid5_urn(WORK_NAMESPACE, "")


def test_all_v0_id_factories_match_hard_coded_vectors() -> None:
    asserted = asserted_work_id(
        [
            ("work-uri", "https://example.org/works/cafe"),
            ("work-uri", "urn:example:work:42"),
        ]
    )
    provisional = provisional_work_id(
        "  Cafe\u0301\r\nReader  ",
        [" Alice\u00a0Example ", "Bob"],
    )
    edition = edition_id(SHA_A)
    exact_file = file_id(SHA_B)
    creator = default_creator_id()
    generator = default_generator_id()
    track = track_id(edition, creator, "second-reader-agent")
    pack = pack_id(edition, track)

    assert asserted == ASSERTED_WORK_VECTOR
    assert provisional == PROVISIONAL_WORK_VECTOR
    assert edition == EDITION_VECTOR
    assert exact_file == FILE_VECTOR
    assert creator == CREATOR_VECTOR
    assert generator == GENERATOR_VECTOR
    assert track == TRACK_VECTOR
    assert pack == PACK_VECTOR
    assert CREATOR_CONTRACT_MAJOR == 0
    assert GENERATOR_CONTRACT_MAJOR == 0
    assert DEFAULT_SPEC_MAJOR == 0


def test_asserted_work_identifier_set_is_sorted_normalized_and_deduplicated() -> None:
    forward = [
        ("work-uri", "https://example.org/works/Cafe\u0301"),
        ("work-uri", "urn:example:work:42"),
    ]
    reverse_with_duplicate = [
        ("work-uri", "urn:example:work:42"),
        ("work-uri", "https://example.org/works/Caf\u00e9"),
        ("work-uri", "urn:example:work:42"),
    ]

    assert asserted_work_id(forward) == asserted_work_id(reverse_with_duplicate)
    assert asserted_work_id(forward) != asserted_work_id(
        [("work-uri", "https://example.org/works/other")]
    )


def test_provisional_work_normalizes_nfc_newlines_and_unicode_white_space() -> None:
    decomposed = provisional_work_id(
        "  Cafe\u0301\r\nReader\u3000",
        ["Alice\u00a0Example", "Bob"],
    )
    normalized = provisional_work_id("Caf\u00e9 Reader", ["Alice Example", "Bob"])

    assert decomposed == normalized
    assert normalized != provisional_work_id(
        "Caf\u00e9 Reader", ["Bob", "Alice Example"]
    )
    assert normalized != provisional_work_id("Other", ["Alice Example", "Bob"])


def test_edition_and_file_ids_require_canonical_lowercase_sha256() -> None:
    assert edition_id(SHA_A) == EDITION_VECTOR
    assert file_id(SHA_B) == FILE_VECTOR
    assert edition_id(SHA_A) != edition_id(SHA_B)
    assert file_id(SHA_A) != file_id(SHA_B)
    with pytest.raises(ValueError, match="lowercase"):
        edition_id(SHA_A.upper())
    with pytest.raises(ValueError, match="lowercase"):
        file_id(SHA_B.upper())


def test_creator_generator_track_and_pack_change_only_on_identity_inputs() -> None:
    creator = default_creator_id()
    generator = default_generator_id()
    edition = edition_id(SHA_A)
    other_edition = edition_id(SHA_B)
    track = track_id(edition, creator, "Cafe\u0301")

    assert creator == default_creator_id()
    assert creator != default_creator_id(1)
    assert generator == default_generator_id()
    assert generator != default_generator_id(1)
    assert track == track_id(edition, creator, "Caf\u00e9")
    assert track != track_id(edition, creator, "Other")
    assert track != track_id(other_edition, creator, "Caf\u00e9")
    assert track != track_id(edition, generator, "Caf\u00e9")
    assert pack_id(edition, track) == pack_id(edition, track, 0)
    assert pack_id(edition, track) != pack_id(edition, track, 1)
    assert pack_id(edition, track) != pack_id(other_edition, track)


@pytest.mark.parametrize(
    "invalid",
    [
        str(uuid4()),
        uuid4().urn,
        uuid3(NAMESPACE_DNS, "example").urn,
        CREATOR_VECTOR.upper(),
        CREATOR_VECTOR.removeprefix("urn:uuid:"),
        "urn:uuid:not-a-uuid",
    ],
)
def test_dependent_factories_reject_noncanonical_or_non_v5_uuid_inputs(
    invalid: str,
) -> None:
    with pytest.raises(ValueError, match="UUID"):
        track_id(invalid, CREATOR_VECTOR, "track")
    with pytest.raises(ValueError, match="UUID"):
        pack_id(EDITION_VECTOR, invalid)


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: asserted_work_id([]), "at least one"),
        (lambda: asserted_work_id([("", "value")]), "empty"),
        (lambda: asserted_work_id([("work-uri", "bad\0value")]), "NUL"),
        (lambda: provisional_work_id("", []), "empty"),
        (lambda: provisional_work_id("title", [" \u3000"]), "normalization"),
        (lambda: provisional_work_id("title\0bad", []), "NUL"),
        (lambda: track_id(EDITION_VECTOR, CREATOR_VECTOR, ""), "empty"),
        (lambda: track_id(EDITION_VECTOR, CREATOR_VECTOR, "bad\0key"), "NUL"),
    ],
)
def test_required_identity_fields_reject_empty_or_embedded_nul(
    factory: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        factory()  # type: ignore[operator]


@pytest.mark.parametrize("factory", [edition_id, file_id])
@pytest.mark.parametrize("invalid", ["", "a" * 63, "g" * 64, "a" * 64 + "0"])
def test_digest_factories_reject_non_sha256_values(
    factory: object, invalid: str
) -> None:
    with pytest.raises(ValueError, match="empty|64 lowercase hexadecimal"):
        factory(invalid)  # type: ignore[operator]


@pytest.mark.parametrize("factory", [default_creator_id, default_generator_id])
def test_contract_major_must_be_a_non_negative_integer(factory: object) -> None:
    with pytest.raises(TypeError, match="integer"):
        factory("0")  # type: ignore[operator]
    with pytest.raises(TypeError, match="integer"):
        factory(True)  # type: ignore[operator]
    with pytest.raises(ValueError, match="non-negative"):
        factory(-1)  # type: ignore[operator]


def test_pack_spec_major_must_be_a_non_negative_integer() -> None:
    with pytest.raises(TypeError, match="integer"):
        pack_id(EDITION_VECTOR, TRACK_VECTOR, "0")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="non-negative"):
        pack_id(EDITION_VECTOR, TRACK_VECTOR, -1)
