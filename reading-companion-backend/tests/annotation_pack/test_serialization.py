from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

import pytest

from src.annotation_pack.serialization import (
    CANONICALIZATION,
    CanonicalJsonError,
    MAX_SAFE_JSON_INTEGER,
    canonical_json_bytes,
    semantic_digest,
    semantic_projection,
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

SEMANTIC_SHA256_VECTOR = "54d24b7f97e8396d096aa4f10a369baf9a9baa5161962ce490ffff70eeb7a2aa"


def _pack() -> dict[str, object]:
    return {
        "@context": (
            "https://www.w3.org/ns/epub-anno.jsonld",
            MappingProxyType(
                {
                    "@protected": True,
                    "sr": "https://captain4whale.github.io/second-reader/ns/annotation-pack#",
                }
            ),
        ),
        "id": "urn:uuid:00000000-0000-5000-8000-000000000001",
        "type": "AnnotationSet",
        "generator": {"id": "generator-a", "sr:version": "1.0.0"},
        "generated": "2026-08-23T12:34:56Z",
        "about": {"id": "edition-a", "dc:title": "Caf\u00e9"},
        "items": (
            MappingProxyType(
                {
                    "id": "urn:uuid:00000000-0000-5000-8000-000000000002",
                    "type": "Annotation",
                    "body": ["first", "second"],
                }
            ),
            MappingProxyType(
                {
                    "id": "urn:uuid:00000000-0000-5000-8000-000000000001",
                    "type": "Annotation",
                    "body": ["kept", "in-order"],
                }
            ),
        ),
        "sr:provenance": {"sr:producer": "second-reader"},
        "sr:semanticDigest": {
            "type": "sr:Digest",
            "sr:algorithm": "sha256",
            "sr:canonicalization": "sr-canonical-json-v1",
            "sr:value": "f" * 64,
        },
        "sr:orderedExtension": ["right", "order"],
    }


def test_canonical_json_matches_fixed_utf8_key_order_bytes_and_sha_vector() -> None:
    encoded = canonical_json_bytes(CANONICAL_VECTOR)

    assert CANONICALIZATION == "sr-canonical-json-v1"
    assert encoded == CANONICAL_BYTES_VECTOR
    assert not encoded.startswith(b"\xef\xbb\xbf")
    assert encoded.endswith(b"\n")
    assert not encoded.endswith(b"\n\n")

    import hashlib

    assert hashlib.sha256(encoded).hexdigest() == CANONICAL_SHA256_VECTOR


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
    ) == (
        '{"maximum":9007199254740991,"minimum":-9007199254740991}\n'
    ).encode()

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


def test_semantic_projection_removes_only_root_nonsemantic_fields_and_sorts_items() -> None:
    pack = _pack()
    pack["about"]["generated"] = "nested-generated-is-semantic"
    pack["about"]["sr:provenance"] = {"nested": "kept"}
    before = canonical_json_bytes(pack)

    projection = semantic_projection(pack)

    assert canonical_json_bytes(pack) == before
    assert set(projection).isdisjoint(
        {"generated", "generator", "sr:provenance", "sr:semanticDigest"}
    )
    assert [item["id"] for item in projection["items"]] == [
        "urn:uuid:00000000-0000-5000-8000-000000000001",
        "urn:uuid:00000000-0000-5000-8000-000000000002",
    ]
    assert projection["items"][0]["body"] == ["kept", "in-order"]
    assert projection["about"]["generated"] == "nested-generated-is-semantic"
    assert projection["about"]["sr:provenance"] == {"nested": "kept"}
    assert projection["sr:orderedExtension"] == ["right", "order"]
    assert isinstance(projection["@context"], list)


def test_semantic_digest_has_fixed_vector_and_ignores_only_declared_fields() -> None:
    pack = _pack()

    assert semantic_digest(pack) == SEMANTIC_SHA256_VECTOR

    reordered_items = _pack()
    reordered_items["items"] = tuple(reversed(reordered_items["items"]))
    assert semantic_digest(reordered_items) == SEMANTIC_SHA256_VECTOR

    changed_nonsemantic = _pack()
    changed_nonsemantic["generated"] = "2030-01-01T00:00:00Z"
    changed_nonsemantic["generator"] = {"id": "generator-b"}
    changed_nonsemantic["sr:provenance"] = {"sr:producer": "other"}
    changed_nonsemantic["sr:semanticDigest"] = {"sr:value": "0" * 64}
    assert semantic_digest(changed_nonsemantic) == SEMANTIC_SHA256_VECTOR

    changed_semantic = _pack()
    changed_semantic["about"]["dc:title"] = "Other"
    assert semantic_digest(changed_semantic) != SEMANTIC_SHA256_VECTOR

    changed_array_order = _pack()
    changed_array_order["sr:orderedExtension"] = ["order", "right"]
    assert semantic_digest(changed_array_order) != SEMANTIC_SHA256_VECTOR


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
def test_semantic_projection_requires_an_item_array_with_string_ids(
    items: object,
) -> None:
    pack = _pack()
    pack["items"] = items

    with pytest.raises(CanonicalJsonError, match="items"):
        semantic_projection(pack)


def test_semantic_projection_rejects_non_mapping_root() -> None:
    with pytest.raises(CanonicalJsonError, match="root"):
        semantic_projection([])  # type: ignore[arg-type]
