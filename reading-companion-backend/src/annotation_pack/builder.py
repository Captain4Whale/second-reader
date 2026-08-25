"""Pure, producer-neutral construction of Annotation Pack v0 documents.

The builder maps already-resolved annotations into the canonical wire shape. It
does not read producer artifacts, resolve anchors, validate external EPUB bytes,
repair invalid drafts, or write files.  Cross-document and publication-policy
checks remain the responsibility of the semantic validator and exporter.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any, Literal, Protocol, cast
import unicodedata

from src.annotation_pack.drafts import ResolvedAnchor, ResolvedAnnotationDraft
from src.annotation_pack.identity import PublicationIdentityResult
from src.annotation_pack.ids import (
    DEFAULT_GENERATOR_IRI,
    annotation_id as derive_annotation_id,
    pack_id as derive_pack_id,
)
from src.annotation_pack.serialization import (
    canonical_json_bytes,
    validate_json_value,
)


ANNOTATION_CONTEXT = "https://www.w3.org/ns/epub-anno.jsonld"
INPUT_SNAPSHOT_ALGORITHM_VERSION = "sr-second-reader-input-snapshot-v1"

_TRACK_KEY = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_ABSOLUTE_IRI = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SEMVER = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\Z"
)

CreatorType = Literal["Software", "Person", "Organization"]

__all__ = [
    "ANNOTATION_CONTEXT",
    "INPUT_SNAPSHOT_ALGORITHM_VERSION",
    "AnnotationPackBuildError",
    "AnnotationPackBuilder",
    "AnnotationPackDocument",
    "Clock",
    "CreatorInput",
    "CreatorType",
    "DeterministicIdFactory",
    "GeneratorInput",
    "ProvenanceInput",
    "SystemClock",
]


@dataclass(frozen=True, slots=True)
class CreatorInput:
    """Stable public creator identity for one annotation track."""

    id: str
    type: CreatorType
    name: str


@dataclass(frozen=True, slots=True)
class GeneratorInput:
    """Public identity and build version of the serializer application."""

    id: str
    name: str
    version: str


@dataclass(frozen=True, slots=True)
class ProvenanceInput:
    """Sanitized producer snapshot provenance accepted by the generic builder."""

    producer: str
    adapter_version: str
    input_snapshot_digest: str
    input_snapshot_algorithm_version: str = INPUT_SNAPSHOT_ALGORITHM_VERSION


class Clock(Protocol):
    """Injectable serialization clock used only for top-level ``generated``."""

    def now(self) -> datetime: ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """UTC wall clock for production export orchestration."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc).replace(microsecond=0)


@dataclass(frozen=True, slots=True)
class DeterministicIdFactory:
    """Injectable facade over the immutable Annotation Pack v0 UUID functions."""

    def pack_id(self, epub_sha256: str, generator_id: str) -> str:
        return derive_pack_id(epub_sha256, generator_id)

    def annotation_id(
        self,
        epub_sha256: str,
        href: str,
        start: int,
        end: int,
        motivation: Literal["highlighting", "commenting"],
        body: str | None,
    ) -> str:
        return derive_annotation_id(
            epub_sha256,
            href,
            start,
            end,
            motivation,
            body,
        )


class AnnotationPackBuildError(ValueError):
    """Stable, sanitized rejection of invalid builder input."""

    __slots__ = ("code",)

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _immutable_collection(*_args: object, **_kwargs: object) -> None:
    raise TypeError("annotation pack document is immutable")


class _FrozenDict(dict[str, Any]):
    __setitem__ = _immutable_collection
    __delitem__ = _immutable_collection
    clear = _immutable_collection
    pop = _immutable_collection
    popitem = _immutable_collection
    setdefault = _immutable_collection
    update = _immutable_collection
    __ior__ = _immutable_collection

    def __deepcopy__(self, _memo: dict[int, object]) -> _FrozenDict:
        return self


class _FrozenList(list[Any]):
    __setitem__ = _immutable_collection
    __delitem__ = _immutable_collection
    __iadd__ = _immutable_collection
    __imul__ = _immutable_collection
    append = _immutable_collection
    clear = _immutable_collection
    extend = _immutable_collection
    insert = _immutable_collection
    pop = _immutable_collection
    remove = _immutable_collection
    reverse = _immutable_collection
    sort = _immutable_collection

    def __deepcopy__(self, _memo: dict[int, object]) -> _FrozenList:
        return self


class AnnotationPackDocument(_FrozenDict):
    """Deeply immutable JSON-compatible canonical Pack mapping."""


class AnnotationPackBuilder:
    """Build a complete schema-shaped v0 Pack from resolved neutral inputs."""

    def __init__(
        self,
        *,
        id_factory: DeterministicIdFactory,
        clock: Clock,
    ) -> None:
        self._id_factory = id_factory
        self._clock = clock

    def build(
        self,
        *,
        publication: PublicationIdentityResult,
        track_key: str,
        track_name: str | None,
        creator: CreatorInput,
        annotations: Sequence[ResolvedAnnotationDraft],
        generator: GeneratorInput,
        provenance: ProvenanceInput,
    ) -> AnnotationPackDocument:
        """Construct one exact-EPUB AnnotationSet without I/O or source access."""

        if not isinstance(publication, PublicationIdentityResult):
            raise TypeError("publication must be a PublicationIdentityResult")
        if not isinstance(creator, CreatorInput):
            raise TypeError("creator must be a CreatorInput")
        if not isinstance(generator, GeneratorInput):
            raise TypeError("generator must be a GeneratorInput")
        if not isinstance(provenance, ProvenanceInput):
            raise TypeError("provenance must be a ProvenanceInput")
        if not isinstance(annotations, Sequence) or isinstance(
            annotations,
            (str, bytes, bytearray),
        ):
            raise TypeError("annotations must be a sequence of resolved drafts")
        # Snapshot the caller-owned sequence exactly once.  Custom Sequence
        # implementations are part of the declared API, but their accessors
        # may fail or expose producer-private details in exception text.
        try:
            annotation_snapshot = tuple(annotations)
        except Exception:
            raise AnnotationPackBuildError(
                "invalid_annotations_sequence",
                "annotations could not be read as a stable sequence",
            ) from None

        publication_wire = _publication_wire_snapshot(publication)
        # These values still select and describe the exporter's local lane, but
        # minimal v0 deliberately does not expose them in the public Pack.
        _track_key_value(track_key)
        _optional_nfc_text(
            track_name,
            field="track_name",
            maximum=128,
        )
        _creator_wire(creator)
        generator_wire = _generator_wire(generator)
        _validate_provenance(provenance)
        epub_sha256 = publication.file_sha256
        if not isinstance(epub_sha256, str) or _SHA256.fullmatch(epub_sha256) is None:
            raise AnnotationPackBuildError(
                "missing_publication_identity",
                "exact EPUB identity is missing",
            )

        try:
            pack_identifier = self._id_factory.pack_id(
                epub_sha256,
                generator_wire["id"],
            )
        except (TypeError, ValueError) as exc:
            raise AnnotationPackBuildError(
                "invalid_identity_input",
                "publication or generator identity input is invalid",
            ) from exc

        item_documents: list[dict[str, Any]] = []
        seen_annotation_ids: set[str] = set()
        for draft in annotation_snapshot:
            item = self._annotation_wire(
                draft=draft,
                epub_sha256=epub_sha256,
            )
            item_id = cast(str, item["id"])
            if item_id in seen_annotation_ids:
                raise AnnotationPackBuildError(
                    "duplicate_annotation_id",
                    "annotations contain a semantic duplicate",
                )
            seen_annotation_ids.add(item_id)
            item_documents.append(item)
        item_documents.sort(key=lambda item: cast(str, item["id"]).encode("utf-8"))

        pack: dict[str, Any] = {
            "@context": ANNOTATION_CONTEXT,
            "id": pack_identifier,
            "type": "AnnotationSet",
            "generator": generator_wire,
            "generated": _utc_seconds(self._clock.now(), field="generated"),
            "about": publication_wire,
            "items": item_documents,
        }
        try:
            validate_json_value(pack)
        except (TypeError, ValueError) as exc:
            raise AnnotationPackBuildError(
                "invalid_json_value",
                "builder input cannot be represented as canonical JSON",
            ) from exc
        return _freeze_pack(pack)

    def _annotation_wire(
        self,
        *,
        draft: ResolvedAnnotationDraft,
        epub_sha256: str,
    ) -> dict[str, Any]:
        if not isinstance(draft, ResolvedAnnotationDraft):
            raise TypeError("each annotation must be a ResolvedAnnotationDraft")
        try:
            kind = draft.kind
            body_text = draft.body_text
            created_at = draft.created_at
            resolved_anchor = draft.target
        except Exception:
            raise AnnotationPackBuildError(
                "invalid_annotation_input",
                "resolved annotation input could not be read safely",
            ) from None
        if not isinstance(resolved_anchor, ResolvedAnchor):
            raise TypeError("resolved annotation target must be a ResolvedAnchor")
        try:
            target_source = resolved_anchor.target
        except Exception:
            raise AnnotationPackBuildError(
                "invalid_json_value",
                "annotation target could not be snapshotted safely",
            ) from None
        target_wire = _detached_json_object(
            target_source,
            code="invalid_json_value",
            message="annotation target could not be snapshotted safely",
        )
        if (
            target_wire.get("source") != resolved_anchor.href
            or not isinstance(resolved_anchor.start, int)
            or isinstance(resolved_anchor.start, bool)
            or not isinstance(resolved_anchor.end, int)
            or isinstance(resolved_anchor.end, bool)
            or resolved_anchor.start < 0
            or resolved_anchor.start >= resolved_anchor.end
        ):
            raise AnnotationPackBuildError(
                "invalid_identity_input",
                "annotation target identity input is invalid",
            )

        if kind == "highlight":
            if body_text not in (None, ""):
                raise AnnotationPackBuildError(
                    "invalid_highlight_body",
                    "highlight annotations must not contain a body",
                )
            motivation = "highlighting"
            normalized_body = None
        elif kind == "note":
            motivation = "commenting"
            normalized_body = _nfc_text(
                body_text,
                field="note body",
                maximum=16384,
            )
        else:
            raise AnnotationPackBuildError(
                "invalid_annotation_kind",
                "annotation kind must be highlight or note",
            )

        try:
            item_identifier = self._id_factory.annotation_id(
                epub_sha256,
                resolved_anchor.href,
                resolved_anchor.start,
                resolved_anchor.end,
                motivation,
                normalized_body,
            )
        except (TypeError, ValueError) as exc:
            raise AnnotationPackBuildError(
                "invalid_identity_input",
                "annotation identity input is invalid",
            ) from exc

        item: dict[str, Any] = {
            "id": item_identifier,
            "type": "Annotation",
            "motivation": motivation,
            "created": _utc_seconds(created_at, field="created_at"),
            "target": target_wire,
        }
        if normalized_body is not None:
            item["body"] = {
                "type": "TextualBody",
                "value": normalized_body,
            }
        return item


def _publication_wire_snapshot(
    publication: PublicationIdentityResult,
) -> dict[str, Any]:
    try:
        wire = publication.wire
    except Exception:
        raise AnnotationPackBuildError(
            "invalid_json_value",
            "publication identity could not be snapshotted safely",
        ) from None
    if not isinstance(wire, Mapping):
        raise AnnotationPackBuildError(
            "missing_publication_identity",
            "publication identity wire object is missing",
        )
    return _detached_json_object(
        wire,
        code="invalid_json_value",
        message="publication identity could not be snapshotted safely",
    )


def _detached_json_object(
    value: object,
    *,
    code: str,
    message: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AnnotationPackBuildError(code, message)
    try:
        snapshot = json.loads(canonical_json_bytes(value))
    except Exception:
        raise AnnotationPackBuildError(code, message) from None
    if not isinstance(snapshot, dict):  # pragma: no cover - Mapping root above
        raise AnnotationPackBuildError(code, message)
    return snapshot


def _creator_wire(creator: CreatorInput) -> dict[str, str]:
    try:
        creator_id_input = creator.id
        creator_type = creator.type
        creator_name = creator.name
    except Exception:
        raise AnnotationPackBuildError(
            "invalid_creator",
            "creator input could not be read safely",
        ) from None
    creator_id = _absolute_iri(creator_id_input, field="creator.id")
    if not isinstance(creator_type, str) or creator_type not in (
        "Software",
        "Person",
        "Organization",
    ):
        raise AnnotationPackBuildError(
            "invalid_creator",
            "creator type is not supported",
        )
    name = _nfc_text(creator_name, field="creator.name", maximum=256)
    return {"id": creator_id, "type": creator_type, "name": name}


def _generator_wire(generator: GeneratorInput) -> dict[str, str]:
    try:
        generator_id = generator.id
        generator_name = generator.name
        generator_version = generator.version
    except Exception:
        raise AnnotationPackBuildError(
            "invalid_generator",
            "generator input could not be read safely",
        ) from None
    normalized_id = _absolute_iri(generator_id, field="generator.id")
    normalized_name = _nfc_text(
        generator_name, field="generator.name", maximum=256
    )
    _semver(generator_version, field="generator.version")
    if normalized_id != DEFAULT_GENERATOR_IRI or normalized_name != (
        "Second Reader Annotation Pack Exporter"
    ):
        raise AnnotationPackBuildError(
            "invalid_generator",
            "generator identity is not the fixed minimal-v0 software identity",
        )
    return {
        "id": normalized_id,
        "type": "Software",
        "name": normalized_name,
    }


def _validate_provenance(provenance: ProvenanceInput) -> None:
    try:
        producer = provenance.producer
        adapter_version = provenance.adapter_version
        digest = provenance.input_snapshot_digest
        algorithm_version = provenance.input_snapshot_algorithm_version
    except Exception:
        raise AnnotationPackBuildError(
            "invalid_provenance",
            "provenance input could not be read safely",
        ) from None
    if algorithm_version != INPUT_SNAPSHOT_ALGORITHM_VERSION:
        raise AnnotationPackBuildError(
            "invalid_provenance",
            "input snapshot algorithm version is not supported by Pack v0",
        )
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise AnnotationPackBuildError(
            "invalid_provenance",
            "input snapshot digest must be lowercase SHA-256",
        )
    _absolute_iri(producer, field="producer")
    _semver(adapter_version, field="adapter_version")


def _track_key_value(value: str) -> str:
    if not isinstance(value, str) or _TRACK_KEY.fullmatch(value) is None:
        raise AnnotationPackBuildError(
            "invalid_track",
            "track key must match the v0 safe-key grammar",
        )
    return value


def _nfc_text(value: object, *, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise AnnotationPackBuildError(
            "invalid_text_value",
            f"{field} must be a string",
        )
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > maximum:
        raise AnnotationPackBuildError(
            "invalid_text_value",
            f"{field} is outside the v0 code-point limits",
        )
    try:
        normalized.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise AnnotationPackBuildError(
            "invalid_text_value",
            f"{field} must be valid UTF-8 text",
        ) from exc
    return normalized


def _optional_nfc_text(
    value: str | None,
    *,
    field: str,
    maximum: int,
) -> str | None:
    if value is None:
        return None
    return _nfc_text(value, field=field, maximum=maximum)


def _absolute_iri(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise AnnotationPackBuildError(
            "invalid_iri",
            f"{field} must be an absolute IRI",
        )
    if value != unicodedata.normalize("NFC", value):
        raise AnnotationPackBuildError(
            "invalid_iri",
            f"{field} must already be NFC-normalized",
        )
    if _ABSOLUTE_IRI.match(value) is None or any(
        character.isspace() or unicodedata.category(character) in {"Cc", "Cs"}
        for character in value
    ):
        raise AnnotationPackBuildError(
            "invalid_iri",
            f"{field} must be a canonical absolute IRI",
        )
    return value


def _semver(value: object, *, field: str) -> str:
    if not isinstance(value, str) or _SEMVER.fullmatch(value) is None:
        raise AnnotationPackBuildError(
            "invalid_version",
            f"{field} must be semantic version text",
        )
    return value


def _utc_seconds(value: object, *, field: str) -> str:
    if not isinstance(value, datetime):
        raise AnnotationPackBuildError(
            "invalid_datetime",
            f"{field} must be a timezone-aware datetime",
        )
    try:
        offset = value.utcoffset()
    except (OverflowError, ValueError) as exc:
        raise AnnotationPackBuildError(
            "invalid_datetime",
            f"{field} has an invalid timezone",
        ) from exc
    if offset is None:
        raise AnnotationPackBuildError(
            "invalid_datetime",
            f"{field} must be timezone-aware",
        )
    try:
        converted = value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as exc:
        raise AnnotationPackBuildError(
            "invalid_datetime",
            f"{field} has an invalid timezone",
        ) from exc
    if converted.microsecond != 0:
        raise AnnotationPackBuildError(
            "invalid_datetime",
            f"{field} must have exact second precision",
        )
    return (
        f"{converted.year:04d}-{converted.month:02d}-{converted.day:02d}T"
        f"{converted.hour:02d}:{converted.minute:02d}:{converted.second:02d}Z"
    )


def _freeze_pack(value: Mapping[str, Any]) -> AnnotationPackDocument:
    frozen = {
        key: _freeze_json(child)
        for key, child in value.items()
    }
    return AnnotationPackDocument(frozen)


def _freeze_json(value: object) -> Any:
    if isinstance(value, Mapping):
        return _FrozenDict(
            {
                key: _freeze_json(child)
                for key, child in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return _FrozenList([_freeze_json(child) for child in value])
    return value
