from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import traceback

import pytest

from src.annotation_pack._generated_models import (
    AnnotationPackDocument as GeneratedAnnotationPackDocument,
)
from src.annotation_pack.anchors import AnchorBuilder
from src.annotation_pack.builder import (
    AnnotationPackBuildError,
    AnnotationPackBuilder,
    CreatorInput,
    DeterministicIdFactory,
    GeneratorInput,
    ProvenanceInput,
)
from src.annotation_pack.drafts import (
    AnnotationDraft,
    ResolvedAnnotationDraft,
    SourceCoordinate,
    SourceRange,
)
from src.annotation_pack.identity import (
    PublicationIdentityBuilder,
    PublicationIdentityResult,
)
from src.annotation_pack.ids import (
    annotation_id,
    default_creator_id,
    default_generator_id,
    pack_id,
    track_id,
)
from src.annotation_pack.schema import pack_validator
from src.annotation_pack.serialization import canonical_json_bytes, semantic_digest
from src.annotation_pack.validation import validate_pack
from src.parsers import parse_ebook
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_runtime.source_normalization import normalize_book_document_source
from tests.annotation_pack.epub_factory import (
    FixtureChapter,
    FixtureMetadata,
    build_epub_bytes,
)


UTC = timezone.utc
GENERATED_AT = datetime(2026, 8, 23, 10, 0, 0, tzinfo=UTC)
CREATED_AT = datetime(
    2026,
    8,
    23,
    18,
    30,
    0,
    tzinfo=timezone(timedelta(hours=8)),
)
INPUT_DIGEST = "7" * 64
SOURCE_RECORD_DIGEST = "8" * 64


@dataclass(frozen=True, slots=True)
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class _SwitchMapping(Mapping[str, object]):
    def __init__(self, *views: dict[str, object]) -> None:
        self._views = views
        self.item_reads = 0

    def __getitem__(self, key: str) -> object:
        return self._views[0][key]

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._views[0])

    def __len__(self) -> int:
        return len(self._views[0])

    def items(self):  # type: ignore[no-untyped-def]
        index = min(self.item_reads, len(self._views) - 1)
        self.item_reads += 1
        return self._views[index].items()


class _ExplosiveMapping(Mapping[str, object]):
    def __getitem__(self, key: str) -> object:
        raise KeyError(key)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(())

    def __len__(self) -> int:
        return 0

    def items(self):  # type: ignore[no-untyped-def]
        raise RuntimeError("/Users/alice/private-producer-state.json")


def _publication(
    tmp_path: Path,
    *,
    chapters: tuple[FixtureChapter, ...] | None = None,
) -> PublicationIdentityResult:
    output_dir = tmp_path / "book"
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(
        build_epub_bytes() if chapters is None else build_epub_bytes(chapters=chapters)
    )
    metadata = FixtureMetadata()
    canonical = build_book_document_from_chapters(
        list(parse_ebook(str(source))),
        title=metadata.title,
        author=", ".join(metadata.creators),
        book_language=metadata.language,
        output_language="en",
        source_file="_assets/source.epub",
    )
    persisted, _diagnostics = normalize_book_document_source(
        canonical,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    return PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=persisted,
    )


def _paragraph_text(
    publication: PublicationIdentityResult,
    *,
    chapter_id: int,
    paragraph_index: int,
) -> str:
    for chapter in publication.rebuilt_book_document["chapters"]:
        if chapter["id"] != chapter_id:
            continue
        for paragraph in chapter["paragraphs"]:
            if paragraph["paragraph_index"] == paragraph_index:
                return str(paragraph["text"])
    raise AssertionError("fixture paragraph is missing")


def _resolved(
    publication: PublicationIdentityResult,
    *,
    kind: str,
    paragraph_index: int,
    needle: str,
    body_text: str | None,
    created_at: datetime = CREATED_AT,
    source_record_index: int = 1,
) -> ResolvedAnnotationDraft:
    text = _paragraph_text(
        publication,
        chapter_id=1,
        paragraph_index=paragraph_index,
    )
    start = text.index(needle)
    draft = AnnotationDraft(
        kind=kind,  # type: ignore[arg-type]
        source_range=SourceRange(
            SourceCoordinate(1, paragraph_index, start),
            SourceCoordinate(1, paragraph_index, start + len(needle)),
        ),
        source_quote=needle,
        body_text=body_text,
        created_at=created_at,
        source_record_index=source_record_index,
        source_record_digest=SOURCE_RECORD_DIGEST,
    )
    return AnchorBuilder().resolve(draft=draft, publication=publication)


def _builder(*, generated_at: datetime = GENERATED_AT) -> AnnotationPackBuilder:
    return AnnotationPackBuilder(
        id_factory=DeterministicIdFactory(),
        clock=FixedClock(generated_at),
    )


def _creator(
    *,
    creator_type: str = "Software",
    creator_id: str | None = None,
    name: str = "Second Reader",
) -> CreatorInput:
    return CreatorInput(
        id=creator_id or default_creator_id(),
        type=creator_type,  # type: ignore[arg-type]
        name=name,
    )


def _generator() -> GeneratorInput:
    return GeneratorInput(
        id=default_generator_id(),
        name="Second Reader Annotation Pack Exporter",
        version="0.1.0",
    )


def _provenance() -> ProvenanceInput:
    return ProvenanceInput(
        producer="urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a",
        adapter_version="0.1.0",
        input_snapshot_digest=INPUT_DIGEST,
    )


def _build(
    publication: PublicationIdentityResult,
    annotations: tuple[ResolvedAnnotationDraft, ...],
    *,
    creator: CreatorInput | None = None,
    track_key: str = "second-reader-agent",
    track_name: str | None = "Second Reader",
    generated_at: datetime = GENERATED_AT,
):
    return _builder(generated_at=generated_at).build(
        publication=publication,
        track_key=track_key,
        track_name=track_name,
        creator=creator or _creator(),
        annotations=annotations,
        generator=_generator(),
        provenance=_provenance(),
    )


def _schema_errors(pack: object) -> list[str]:
    return [error.message for error in pack_validator().iter_errors(pack)]


def test_builder_maps_highlight_note_and_full_publication_to_schema_valid_pack(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text="",
        source_record_index=2,
    )
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=4,
        needle="better question",
        body_text="  Cafe\u0301: return deliberately.  ",
        source_record_index=1,
    )

    pack = _build(
        publication,
        (note, highlight),
        creator=_creator(name="Second Reade\u0301r"),
        track_name="Cafe\u0301 Track",
    )

    assert _schema_errors(pack) == []
    assert pack["type"] == "AnnotationSet"
    assert pack["generated"] == "2026-08-23T10:00:00Z"
    assert pack["about"]["dc:identifier"] == [
        pack["about"]["sr:work"]["id"],
        pack["about"]["sr:edition"]["id"],
        pack["about"]["sr:file"]["id"],
    ]
    assert pack["about"]["dc:creator"] == ["Second Reader Fixture Authors"]
    assert pack["sr:track"]["name"] == "Caf\u00e9 Track"
    assert pack["sr:track"]["creator"]["name"] == "Second Read\u00e9r"
    assert [item["id"] for item in pack["items"]] == sorted(
        item["id"] for item in pack["items"]
    )

    by_kind = {item["sr:kind"]: item for item in pack["items"]}
    assert by_kind["highlight"]["motivation"] == "highlighting"
    assert "body" not in by_kind["highlight"]
    assert by_kind["note"]["motivation"] == "commenting"
    assert by_kind["note"]["body"] == {
        "type": "TextualBody",
        "value": "  Caf\u00e9: return deliberately.  ",
        "format": "text/plain",
    }
    assert by_kind["note"]["created"] == "2026-08-23T10:30:00Z"
    assert all(
        item["creator"] == pack["sr:track"]["creator"]
        for item in pack["items"]
    )

    edition = pack["about"]["sr:edition"]["id"]
    expected_track = track_id(edition, default_creator_id(), "second-reader-agent")
    assert pack["sr:track"]["id"] == expected_track
    assert pack["id"] == pack_id(edition, expected_track)
    expected_note_body_sha = hashlib.sha256(
        "  Caf\u00e9: return deliberately.  ".encode()
    ).hexdigest()
    assert by_kind["highlight"]["id"] == annotation_id(
        expected_track,
        "highlight",
        highlight.target.anchor_id,
    )
    assert by_kind["note"]["id"] == annotation_id(
        expected_track,
        "note",
        note.target.anchor_id,
        expected_note_body_sha,
    )
    assert pack["sr:semanticDigest"]["sr:value"] == semantic_digest(pack)
    assert canonical_json_bytes(pack)
    GeneratedAnnotationPackDocument.model_validate(pack)


@pytest.mark.parametrize(
    ("creator_type", "creator_id"),
    [
        ("Software", "urn:example:software:annotator"),
        ("Person", "https://example.org/people/alice"),
        ("Organization", "https://example.org/organizations/reader-lab"),
    ],
)
def test_builder_supports_all_creator_types_and_absolute_iri_ids(
    tmp_path: Path,
    creator_type: str,
    creator_id: str,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    pack = _build(
        publication,
        (highlight,),
        creator=_creator(
            creator_type=creator_type,
            creator_id=creator_id,
            name="Public Creator",
        ),
        track_key="public-track",
    )

    assert _schema_errors(pack) == []
    assert pack["sr:track"]["creator"] == {
        "id": creator_id,
        "type": creator_type,
        "name": "Public Creator",
    }
    assert pack["items"][0]["creator"] == pack["sr:track"]["creator"]


def test_builder_is_deterministic_across_item_order_and_volatile_envelope(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=4,
        needle="better question",
        body_text="Return deliberately.",
    )

    first = _build(publication, (highlight, note))
    second = _build(
        publication,
        (note, highlight),
        generated_at=datetime(2027, 1, 1, tzinfo=UTC),
    )

    assert first["generated"] != second["generated"]
    assert first["id"] == second["id"]
    assert first["items"] == second["items"]
    assert first["sr:semanticDigest"] == second["sr:semanticDigest"]


def test_builder_can_construct_schema_valid_empty_pack_without_policy(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)

    pack = _build(publication, (), track_name=None)

    assert pack["items"] == []
    assert "name" not in pack["sr:track"]
    assert pack["sr:semanticDigest"]["sr:value"] == semantic_digest(pack)
    assert _schema_errors(pack) == []


def test_builder_output_is_deeply_readonly_and_excludes_diagnostics(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    pack = _build(publication, (highlight,))

    with pytest.raises(TypeError, match="immutable"):
        pack["generated"] = "2030-01-01T00:00:00Z"
    with pytest.raises(TypeError, match="immutable"):
        pack["items"].append({})
    with pytest.raises(TypeError, match="immutable"):
        pack["items"][0]["target"]["source"] = "Text/other.xhtml"

    encoded = canonical_json_bytes(pack).decode()
    assert "source_record_index" not in encoded
    assert "source_record_digest" not in encoded
    assert SOURCE_RECORD_DIGEST not in encoded


def test_builder_does_not_write_or_read_producer_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    def fail_write(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("builder attempted a filesystem write")

    monkeypatch.setattr(Path, "write_bytes", fail_write)
    monkeypatch.setattr(Path, "write_text", fail_write)

    pack = _build(publication, (highlight,))

    assert _schema_errors(pack) == []


def test_builder_accepts_custom_sequence_via_one_stable_snapshot(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    class DraftSequence(Sequence[ResolvedAnnotationDraft]):
        def __init__(self, values: tuple[ResolvedAnnotationDraft, ...]) -> None:
            self.values = values
            self.iterations = 0

        def __getitem__(self, index):  # type: ignore[no-untyped-def]
            return self.values[index]

        def __len__(self) -> int:
            return len(self.values)

        def __iter__(self):  # type: ignore[no-untyped-def]
            self.iterations += 1
            return iter(self.values)

    annotations = DraftSequence((highlight,))

    pack = _builder().build(
        publication=publication,
        track_key="safe-track",
        track_name=None,
        creator=_creator(),
        annotations=annotations,
        generator=_generator(),
        provenance=_provenance(),
    )

    assert annotations.iterations == 1
    assert len(pack["items"]) == 1


def test_builder_sanitizes_custom_sequence_read_failure(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)

    class ExplosiveList(list[ResolvedAnnotationDraft]):
        def __iter__(self):  # type: ignore[no-untyped-def]
            raise RuntimeError("/Users/private/producer-ledger.jsonl")

    annotations = ExplosiveList()
    with pytest.raises(AnnotationPackBuildError) as caught:
        _builder().build(
            publication=publication,
            track_key="safe-track",
            track_name=None,
            creator=_creator(),
            annotations=annotations,
            generator=_generator(),
            provenance=_provenance(),
        )

    assert caught.value.code == "invalid_annotations_sequence"
    assert "private" not in str(caught.value)
    assert "producer-ledger" not in str(caught.value)
    formatted = "".join(traceback.format_exception(caught.value))
    assert "private" not in formatted
    assert "producer-ledger" not in formatted


def test_builder_snapshots_publication_and_target_mappings_once(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    publication_wire = json.loads(canonical_json_bytes(publication.wire))
    changed_publication_wire = json.loads(canonical_json_bytes(publication_wire))
    changed_publication_wire["dc:title"] = "/Users/alice/private-title"
    publication_switch = _SwitchMapping(
        publication_wire,
        changed_publication_wire,
    )

    target_wire = json.loads(canonical_json_bytes(highlight.target.target))
    changed_target_wire = json.loads(canonical_json_bytes(target_wire))
    changed_target_wire["source"] = "/Users/alice/private-source.xhtml"
    target_switch = _SwitchMapping(target_wire, changed_target_wire)

    switched_publication = replace(publication, wire=publication_switch)
    switched_anchor = replace(highlight.target, target=target_switch)
    switched_highlight = replace(highlight, target=switched_anchor)

    pack = _build(switched_publication, (switched_highlight,))

    assert publication_switch.item_reads == 1
    assert target_switch.item_reads == 1
    assert pack["sr:semanticDigest"]["sr:value"] == semantic_digest(pack)
    assert validate_pack(pack).status == "valid"


@pytest.mark.parametrize("boundary", ["publication", "target"])
def test_builder_sanitizes_hostile_mapping_snapshot_failure(
    tmp_path: Path,
    boundary: str,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    if boundary == "publication":
        publication = replace(publication, wire=_ExplosiveMapping())
    else:
        hostile_anchor = replace(highlight.target, target=_ExplosiveMapping())
        highlight = replace(highlight, target=hostile_anchor)

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (highlight,))

    assert caught.value.code == "invalid_json_value"
    assert caught.value.__cause__ is None
    formatted = "".join(traceback.format_exception(caught.value))
    assert "/Users/alice" not in formatted
    assert "private-producer-state" not in formatted


@pytest.mark.parametrize(
    ("kind", "body_text", "code"),
    [
        ("highlight", "not allowed", "invalid_highlight_body"),
        ("note", "", "invalid_text_value"),
        ("note", None, "invalid_text_value"),
        ("bookmark", None, "invalid_annotation_kind"),
    ],
)
def test_builder_rejects_invalid_highlight_note_mapping(
    tmp_path: Path,
    kind: str,
    body_text: str | None,
    code: str,
) -> None:
    publication = _publication(tmp_path)
    resolved = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    invalid = replace(resolved, kind=kind, body_text=body_text)  # type: ignore[arg-type]

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (invalid,))

    assert caught.value.code == code


def test_builder_rejects_body_and_metadata_beyond_contract_limits(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=4,
        needle="better question",
        body_text="valid",
    )

    with pytest.raises(AnnotationPackBuildError, match="code-point limits"):
        _build(publication, (replace(note, body_text="x" * 16385),))
    with pytest.raises(AnnotationPackBuildError, match="code-point limits"):
        _build(publication, (note,), creator=_creator(name="x" * 257))
    with pytest.raises(AnnotationPackBuildError, match="safe-key grammar"):
        _build(publication, (note,), track_key="Unsafe Track")
    with pytest.raises(AnnotationPackBuildError, match="code-point limits"):
        _build(publication, (note,), track_name="x" * 129)


def test_builder_rejects_non_utf8_note_body_with_sanitized_error(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=4,
        needle="better question",
        body_text="valid",
    )

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (replace(note, body_text="broken\ud800text"),))

    assert caught.value.code == "invalid_text_value"
    assert "surrogate" not in str(caught.value).lower()


@pytest.mark.parametrize(
    "created_at",
    [
        datetime(2026, 8, 23, 10, 0, 0),
        datetime(2026, 8, 23, 10, 0, 0, 1, tzinfo=UTC),
    ],
)
def test_builder_rejects_non_utc_serializable_created_times(
    tmp_path: Path,
    created_at: datetime,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (replace(highlight, created_at=created_at),))

    assert caught.value.code == "invalid_datetime"


def test_builder_rejects_invalid_clock_creator_generator_and_provenance(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(
            publication,
            (highlight,),
            generated_at=datetime(2026, 8, 23, 10, 0, 0),
        )
    assert caught.value.code == "invalid_datetime"

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(
            publication,
            (highlight,),
            creator=_creator(creator_id="relative/creator"),
        )
    assert caught.value.code == "invalid_iri"

    builder = _builder()
    with pytest.raises(AnnotationPackBuildError) as caught:
        builder.build(
            publication=publication,
            track_key="valid",
            track_name=None,
            creator=_creator(),
            annotations=(highlight,),
            generator=replace(_generator(), version="v1"),
            provenance=_provenance(),
        )
    assert caught.value.code == "invalid_version"

    with pytest.raises(AnnotationPackBuildError) as caught:
        builder.build(
            publication=publication,
            track_key="valid",
            track_name=None,
            creator=_creator(),
            annotations=(highlight,),
            generator=_generator(),
            provenance=replace(_provenance(), input_snapshot_digest="A" * 64),
        )
    assert caught.value.code == "invalid_provenance"


def test_builder_rejects_semantic_duplicate_annotation_ids(tmp_path: Path) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (highlight, highlight))

    assert caught.value.code == "duplicate_annotation_id"


def test_builder_rejects_missing_publication_edition_identity(tmp_path: Path) -> None:
    publication = _publication(tmp_path)
    invalid = replace(publication, wire={})

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(invalid, ())

    assert caught.value.code == "missing_publication_identity"


def test_builder_preserves_source_selector_code_points_while_normalizing_note(
    tmp_path: Path,
) -> None:
    chapters = (
        FixtureChapter(
            item_id="chapter-one",
            href="Text/chapter-01.xhtml",
            title="Decomposed Source",
            paragraphs=("A Cafe\u0301 returns.",),
        ),
    )
    publication = _publication(tmp_path, chapters=chapters)
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=2,
        needle="Cafe\u0301",
        body_text="Cafe\u0301",
    )

    pack = _build(publication, (note,))
    item = pack["items"][0]

    assert item["target"]["selector"][0]["exact"] == "Cafe\u0301"
    assert item["body"]["value"] == "Caf\u00e9"
    assert _schema_errors(pack) == []
