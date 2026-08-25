from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import pytest

from src.annotation_pack.ids import (
    ANNOTATION_NAMESPACE,
    DEFAULT_GENERATOR_IRI,
    PACK_NAMESPACE,
    annotation_id,
    default_generator_id,
    pack_id,
    uuid5_urn,
)


UUID_NAMESPACE_ROOT = (
    "https://captain4whale.github.io/second-reader/ns/annotation-pack/uuid"
)
EPUB_SHA256 = "a" * 64
OTHER_EPUB_SHA256 = "b" * 64
HREF = "Text/chapter.xhtml"

PACK_VECTOR = "urn:uuid:678c7dce-46a0-5fcf-8c02-cbf05ce80849"
HIGHLIGHT_VECTOR = "urn:uuid:aaeff35c-7967-53b2-9635-6caa06bef15f"
NOTE_VECTOR = "urn:uuid:47add2e2-cf51-51ae-bf53-c2861a893eee"


def test_public_namespace_literals_match_the_immutable_iri_vectors() -> None:
    expected = {
        "pack": (PACK_NAMESPACE, "15a1b369-656b-55cb-bfa1-55a529a1f39e"),
        "annotation": (
            ANNOTATION_NAMESPACE,
            "ab5c7848-4a52-5b43-a01b-f76dbce62959",
        ),
    }

    for kind, (actual, literal) in expected.items():
        assert str(actual) == literal
        assert actual == uuid5(NAMESPACE_URL, f"{UUID_NAMESPACE_ROOT}/{kind}/v0")
        assert actual.version == 5


def test_uuid5_urn_is_lowercase_canonical_and_rejects_invalid_arguments() -> None:
    namespace = uuid4()
    result = uuid5_urn(namespace, "minimal\0v0")

    assert result == uuid5(namespace, "minimal\0v0").urn
    assert result == result.lower()
    assert UUID(result).version == 5
    with pytest.raises(TypeError, match="namespace"):
        uuid5_urn("not-a-uuid", "minimal")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="canonical_name"):
        uuid5_urn(namespace, b"minimal")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="empty"):
        uuid5_urn(namespace, "")


def test_minimal_v0_public_ids_match_fixed_framing_vectors() -> None:
    generator = default_generator_id()
    pack = pack_id(EPUB_SHA256)
    highlight = annotation_id(
        EPUB_SHA256,
        HREF,
        2,
        14,
        "highlighting",
    )
    note = annotation_id(
        EPUB_SHA256,
        HREF,
        2,
        14,
        "commenting",
        "A note.",
    )

    assert generator == DEFAULT_GENERATOR_IRI
    assert pack == PACK_VECTOR
    assert highlight == HIGHLIGHT_VECTOR
    assert note == NOTE_VECTOR
    assert (
        pack
        == uuid5(
            PACK_NAMESPACE,
            "\0".join(("annotation-pack", "v0", EPUB_SHA256, DEFAULT_GENERATOR_IRI)),
        ).urn
    )
    assert (
        highlight
        == uuid5(
            ANNOTATION_NAMESPACE,
            "\0".join(
                (
                    "annotation",
                    "v0",
                    EPUB_SHA256,
                    HREF,
                    "2",
                    "14",
                    "highlighting",
                    "",
                )
            ),
        ).urn
    )
    assert (
        note
        == uuid5(
            ANNOTATION_NAMESPACE,
            "\0".join(
                (
                    "annotation",
                    "v0",
                    EPUB_SHA256,
                    HREF,
                    "2",
                    "14",
                    "commenting",
                    "A note.",
                )
            ),
        ).urn
    )


def test_exact_epub_byte_change_changes_pack_and_annotation_ids() -> None:
    assert pack_id(EPUB_SHA256) != pack_id(OTHER_EPUB_SHA256)
    assert annotation_id(EPUB_SHA256, HREF, 2, 14, "highlighting") != annotation_id(
        OTHER_EPUB_SHA256, HREF, 2, 14, "highlighting"
    )
    assert annotation_id(
        EPUB_SHA256, HREF, 2, 14, "commenting", "A note."
    ) != annotation_id(OTHER_EPUB_SHA256, HREF, 2, 14, "commenting", "A note.")


def test_pack_identity_depends_only_on_epub_hash_and_generator() -> None:
    assert pack_id(EPUB_SHA256) == pack_id(
        EPUB_SHA256,
        DEFAULT_GENERATOR_IRI,
    )
    assert pack_id(EPUB_SHA256) != pack_id(
        EPUB_SHA256,
        "https://example.org/software/other-generator",
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("href", annotation_id(EPUB_SHA256, "Text/other.xhtml", 2, 14, "highlighting")),
        ("start", annotation_id(EPUB_SHA256, HREF, 3, 14, "highlighting")),
        ("end", annotation_id(EPUB_SHA256, HREF, 2, 15, "highlighting")),
        (
            "motivation_and_body",
            annotation_id(EPUB_SHA256, HREF, 2, 14, "commenting", "A note."),
        ),
    ],
)
def test_annotation_identity_covers_every_visible_semantic_input(
    mutation: str,
    expected: str,
) -> None:
    baseline = annotation_id(EPUB_SHA256, HREF, 2, 14, "highlighting")

    assert mutation
    assert expected != baseline
    assert annotation_id(
        EPUB_SHA256, HREF, 2, 14, "commenting", "A note."
    ) != annotation_id(EPUB_SHA256, HREF, 2, 14, "commenting", "Another note.")


def test_annotation_motivation_and_body_rules_are_closed() -> None:
    with pytest.raises(ValueError, match="must not include"):
        annotation_id(EPUB_SHA256, HREF, 2, 14, "highlighting", "body")
    with pytest.raises(ValueError, match="requires a body"):
        annotation_id(EPUB_SHA256, HREF, 2, 14, "commenting")
    with pytest.raises(ValueError, match="non-empty NFC"):
        annotation_id(EPUB_SHA256, HREF, 2, 14, "commenting", "   ")
    with pytest.raises(ValueError, match="non-empty NFC"):
        annotation_id(EPUB_SHA256, HREF, 2, 14, "commenting", "Cafe\u0301")
    with pytest.raises(ValueError, match="motivation"):
        annotation_id(EPUB_SHA256, HREF, 2, 14, "bookmarking")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "digest",
    [
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        f"nih:sha-256;{'a' * 64}",
        "sha256:" + "a" * 64,
    ],
)
def test_public_id_factories_require_bare_lowercase_sha256(digest: str) -> None:
    with pytest.raises(ValueError, match="lowercase"):
        pack_id(digest)
    with pytest.raises(ValueError, match="lowercase"):
        annotation_id(digest, HREF, 2, 14, "highlighting")


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (-1, 1),
        (0, 0),
        (2, 1),
        (True, 2),
        (0, False),
    ],
)
def test_annotation_id_rejects_invalid_or_empty_text_positions(
    start: object,
    end: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        annotation_id(
            EPUB_SHA256,
            HREF,
            start,  # type: ignore[arg-type]
            end,  # type: ignore[arg-type]
            "highlighting",
        )


@pytest.mark.parametrize("href", ["", "Text/Cafe\u0301.xhtml", "Text/a\0b.xhtml"])
def test_annotation_id_rejects_noncanonical_or_unsafe_hrefs(href: str) -> None:
    with pytest.raises(ValueError):
        annotation_id(EPUB_SHA256, href, 2, 14, "highlighting")


def test_minimal_v0_major_inputs_cannot_fork_public_identity() -> None:
    assert default_generator_id(0) == DEFAULT_GENERATOR_IRI
    assert pack_id(EPUB_SHA256, spec_major=0) == PACK_VECTOR
    with pytest.raises(ValueError, match="only generator contract major 0"):
        default_generator_id(1)
    with pytest.raises(ValueError, match="only spec major 0"):
        pack_id(EPUB_SHA256, spec_major=1)
    with pytest.raises(TypeError, match="integer"):
        default_generator_id(True)
    with pytest.raises(TypeError, match="integer"):
        pack_id(EPUB_SHA256, spec_major=True)
