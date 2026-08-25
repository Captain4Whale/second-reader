from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from types import MappingProxyType

import pytest

from src.annotation_pack.ids import (
    DEFAULT_GENERATOR_IRI,
    annotation_id,
    pack_id,
)
from src.annotation_pack.serialization import (
    CANONICALIZATION,
    CanonicalJsonError,
    MAX_SAFE_JSON_INTEGER,
    canonical_json_bytes,
    semantic_digest,
    semantic_projection,
    serialize_pack,
    validate_json_value,
)


CANONICAL_VECTOR = {
    "😀": "astral",
    "é": "caf\u00e9",
    "a": (3, 2, 1),
    "A": MappingProxyType({"α": None, "z": False}),
}
CANONICAL_BYTES_VECTOR = (
    '{"A":{"z":false,"α":null},"a":[3,2,1],"é":"café","😀":"astral"}\n'.encode()
)
CANONICAL_SHA256_VECTOR = "cb268d4d52d5159659d4ddabe23d0aa00a5aef94070e18600359b327d6f2454e"

EPUB_SHA256 = "a" * 64
NOTE_BODY = "Return deliberately."


def _items() -> list[dict[str, object]]:
    highlight_target = {
        "source": "Text/chapter.xhtml",
        "selector": [
            {
                "type": "TextQuoteSelector",
                "exact": "second",
                "prefix": "first ",
            },
            {"type": "TextPositionSelector", "start": 6, "end": 12},
        ],
    }
    note_target = {
        "source": "Text/chapter.xhtml",
        "selector": [
            {
                "type": "TextQuoteSelector",
                "exact": "first",
                "suffix": " second",
            },
            {"type": "TextPositionSelector", "start": 0, "end": 5},
        ],
    }
    return [
        {
            "id": annotation_id(
                EPUB_SHA256,
                "Text/chapter.xhtml",
                6,
                12,
                "highlighting",
            ),
            "type": "Annotation",
            "created": "2026-08-23T12:35:00Z",
            "motivation": "highlighting",
            "target": highlight_target,
        },
        {
            "id": annotation_id(
                EPUB_SHA256,
                "Text/chapter.xhtml",
                0,
                5,
                "commenting",
                NOTE_BODY,
            ),
            "type": "Annotation",
            "created": "2026-08-23T12:36:00Z",
            "motivation": "commenting",
            "body": {"type": "TextualBody", "value": NOTE_BODY},
            "target": note_target,
        },
    ]


def _pack(*, reverse_items: bool = False) -> dict[str, object]:
    items = sorted(_items(), key=lambda item: str(item["id"]))
    if reverse_items:
        items.reverse()
    return {
        "@context": "https://www.w3.org/ns/epub-anno.jsonld",
        "id": pack_id(EPUB_SHA256, DEFAULT_GENERATOR_IRI),
        "type": "AnnotationSet",
        "generator": {
            "id": DEFAULT_GENERATOR_IRI,
            "type": "Software",
            "name": "Second Reader Annotation Pack Exporter",
        },
        "generated": "2026-08-23T12:34:56Z",
        "about": {
            "dc:identifier": [f"nih:sha-256;{EPUB_SHA256}"],
            "dc:format": "application/epub+zip",
            "dc:title": "Tiny Reader",
            "dc:creator": ["Fixture Author"],
        },
        "items": items,
    }


class _ExplosiveMapping(Mapping[str, object]):
    def __getitem__(self, key: str) -> object:
        raise KeyError(key)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(())

    def __len__(self) -> int:
        return 0

    def items(self):  # type: ignore[no-untyped-def]
        raise RuntimeError("/Users/alice/private-pack.json")


def test_canonical_json_matches_fixed_utf8_key_order_bytes_and_sha_vector() -> None:
    encoded = canonical_json_bytes(CANONICAL_VECTOR)

    assert CANONICALIZATION == "sr-canonical-json-v1"
    assert encoded == CANONICAL_BYTES_VECTOR
    assert hashlib.sha256(encoded).hexdigest() == CANONICAL_SHA256_VECTOR
    assert not encoded.startswith(b"\xef\xbb\xbf")
    assert encoded.endswith(b"\n")
    assert not encoded.endswith(b"\n\n")


def test_canonical_json_preserves_array_and_string_content_without_normalization() -> None:
    value = {
        "decomposed": "Cafe\u0301\r\n",
        "array": ("z", "a", "z"),
        "escaped": "line\nquote\"slash\\",
    }

    assert canonical_json_bytes(value) == (
        '{"array":["z","a","z"],"decomposed":"Café\\r\\n",'
        '"escaped":"line\\nquote\\\"slash\\\\"}\n'
    ).encode()


def test_canonical_json_freezes_code_point_order_and_string_escapes() -> None:
    value = {
        "\U00010000": "astral",
        "\ue000": "bmp-private-use",
        "controls": "\x00\b\t\n\f\r\x1f/\u2028\u2029",
    }

    assert canonical_json_bytes(value) == (
        '{"controls":"\\u0000\\b\\t\\n\\f\\r\\u001f/\u2028\u2029",'
        '"\ue000":"bmp-private-use","\U00010000":"astral"}\n'
    ).encode()


def test_canonical_json_accepts_only_interoperable_integers() -> None:
    assert canonical_json_bytes(
        {"maximum": MAX_SAFE_JSON_INTEGER, "minimum": -MAX_SAFE_JSON_INTEGER}
    ) == b'{"maximum":9007199254740991,"minimum":-9007199254740991}\n'

    for invalid in (
        MAX_SAFE_JSON_INTEGER + 1,
        -MAX_SAFE_JSON_INTEGER - 1,
        0.0,
        -0.0,
        1.25,
    ):
        with pytest.raises(CanonicalJsonError):
            canonical_json_bytes(invalid)


def test_mapping_proxy_tuple_and_repeated_encoding_are_supported() -> None:
    frozen = MappingProxyType(
        {
            "outer": (
                MappingProxyType({"b": 2, "a": 1}),
                True,
                None,
            )
        }
    )

    validate_json_value(frozen)
    first = canonical_json_bytes(frozen)
    second = canonical_json_bytes(frozen)

    assert first == b'{"outer":[{"a":1,"b":2},true,null]}\n'
    assert first == second


@pytest.mark.parametrize(
    "invalid",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        1.5,
        b"bytes",
        Decimal("1.5"),
        datetime(2026, 8, 23),
        {"unordered"},
        frozenset({"unordered"}),
        object(),
        {1: "non-string-key"},
        {"surrogate": "\ud800"},
    ],
)
def test_non_json_values_are_rejected(invalid: object) -> None:
    with pytest.raises(CanonicalJsonError):
        validate_json_value(invalid)
    with pytest.raises(CanonicalJsonError):
        canonical_json_bytes(invalid)


def test_circular_containers_are_rejected() -> None:
    cyclic_list: list[object] = []
    cyclic_list.append(cyclic_list)
    cyclic_dict: dict[str, object] = {}
    cyclic_dict["self"] = cyclic_dict

    with pytest.raises(CanonicalJsonError, match="circular"):
        canonical_json_bytes(cyclic_list)
    with pytest.raises(CanonicalJsonError, match="circular"):
        canonical_json_bytes(cyclic_dict)


def test_minimal_pack_canonical_bytes_have_no_custom_public_vocabulary() -> None:
    pack = _pack()

    first = canonical_json_bytes(pack)
    second = canonical_json_bytes(pack)

    assert first == second
    assert json.loads(first) == pack
    assert first.startswith(b'{"@context":"https://www.w3.org/ns/epub-anno.jsonld"')
    assert first.endswith(b"\n")
    assert b'"sr:' not in first
    assert b'"creator"' not in first
    assert b'"format":"text/plain"' not in first
    assert b'"semanticDigest"' not in first
    assert b'"provenance"' not in first.lower()


def test_internal_semantic_projection_removes_only_generated_and_sorts_items() -> None:
    pack = _pack(reverse_items=True)
    pack["about"]["generated"] = "nested-generated-is-semantic"
    before = canonical_json_bytes(pack)

    projection = semantic_projection(pack)

    assert canonical_json_bytes(pack) == before
    assert "generated" not in projection
    assert projection["generator"] == pack["generator"]
    assert [item["id"] for item in projection["items"]] == sorted(
        item["id"] for item in pack["items"]
    )
    assert projection["about"]["generated"] == "nested-generated-is-semantic"
    note = next(
        item for item in projection["items"] if item["motivation"] == "commenting"
    )
    assert [selector["type"] for selector in note["target"]["selector"]] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]


def test_internal_semantic_digest_ignores_only_generation_time_and_item_order() -> None:
    baseline = _pack()
    baseline_digest = semantic_digest(baseline)

    reordered = _pack(reverse_items=True)
    assert semantic_digest(reordered) == baseline_digest

    changed_time = _pack()
    changed_time["generated"] = "2030-01-01T00:00:00Z"
    assert semantic_digest(changed_time) == baseline_digest

    changed_generator = _pack()
    changed_generator["generator"]["name"] = "Different Generator"
    assert semantic_digest(changed_generator) != baseline_digest

    changed_about = _pack()
    changed_about["about"]["dc:title"] = "Other"
    assert semantic_digest(changed_about) != baseline_digest

    changed_selector_order = _pack()
    changed_selector_order["items"][0]["target"]["selector"].reverse()
    assert semantic_digest(changed_selector_order) != baseline_digest
    assert len(baseline_digest) == 64
    assert baseline_digest == baseline_digest.lower()


@pytest.mark.parametrize(
    "items",
    [
        None,
        {},
        ["not-an-object"],
        [{}],
        [{"id": 7}],
    ],
)
def test_semantic_projection_requires_item_array_with_string_ids(
    items: object,
) -> None:
    pack = _pack()
    pack["items"] = items

    with pytest.raises(CanonicalJsonError, match="items"):
        semantic_projection(pack)


def test_semantic_projection_rejects_non_mapping_root() -> None:
    with pytest.raises(CanonicalJsonError, match="root"):
        semantic_projection([])  # type: ignore[arg-type]


def test_serialize_pack_validates_and_returns_the_same_canonical_snapshot() -> None:
    pack = _pack()

    encoded = serialize_pack(pack)

    assert encoded == canonical_json_bytes(pack)
    assert encoded == serialize_pack(deepcopy(pack))
    assert b'"sr:' not in encoded


def test_serialize_pack_rejects_old_public_fields_and_wrong_canonicalization() -> None:
    old_wire = _pack()
    old_wire["sr:track"] = {"type": "sr:AnnotationTrack"}

    with pytest.raises(CanonicalJsonError, match="schema or semantic"):
        serialize_pack(old_wire)
    with pytest.raises(CanonicalJsonError, match="unsupported"):
        serialize_pack(_pack(), canonicalization="other-canonicalization")


def test_serialize_pack_accepts_wire_model_and_sanitizes_hostile_callers() -> None:
    class WireModel:
        def model_dump(self, **_kwargs: object) -> dict[str, object]:
            return _pack()

    class ExplosiveModel:
        def model_dump(self, **_kwargs: object) -> object:
            raise RuntimeError("/Users/alice/private-wire-model.json")

    assert serialize_pack(WireModel()) == canonical_json_bytes(_pack())

    with pytest.raises(CanonicalJsonError) as model_error:
        serialize_pack(ExplosiveModel())
    assert "/Users/alice" not in str(model_error.value)

    with pytest.raises(CanonicalJsonError) as mapping_error:
        serialize_pack(_ExplosiveMapping())
    assert "/Users/alice" not in str(mapping_error.value)
