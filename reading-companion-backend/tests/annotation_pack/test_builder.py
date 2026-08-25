from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import traceback

import pytest

from src.annotation_pack.anchors import AnchorBuilder
from src.annotation_pack.builder import (
    ANNOTATION_CONTEXT,
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
    DEFAULT_GENERATOR_IRI,
    annotation_id,
    default_creator_id,
    default_generator_id,
    pack_id,
)
from src.annotation_pack.schema import pack_validator
from src.annotation_pack.serialization import canonical_json_bytes
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


def _generator(
    *,
    generator_id: str | None = None,
    name: str = "Second Reader Annotation Pack Exporter",
    version: str = "0.1.0",
) -> GeneratorInput:
    return GeneratorInput(
        id=generator_id or default_generator_id(),
        name=name,
        version=version,
    )


def _provenance(
    *,
    producer: str = "urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a",
    adapter_version: str = "0.1.0",
    digest: str = INPUT_DIGEST,
) -> ProvenanceInput:
    return ProvenanceInput(
        producer=producer,
        adapter_version=adapter_version,
        input_snapshot_digest=digest,
    )


def _builder(*, generated_at: datetime = GENERATED_AT) -> AnnotationPackBuilder:
    return AnnotationPackBuilder(
        id_factory=DeterministicIdFactory(),
        clock=FixedClock(generated_at),
    )


def _build(
    publication: PublicationIdentityResult,
    annotations: Sequence[ResolvedAnnotationDraft],
    *,
    track_key: str = "second-reader-agent",
    track_name: str | None = "Second Reader",
    creator: CreatorInput | None = None,
    generator: GeneratorInput | None = None,
    provenance: ProvenanceInput | None = None,
    generated_at: datetime = GENERATED_AT,
):  # type: ignore[no-untyped-def]
    return _builder(generated_at=generated_at).build(
        publication=publication,
        track_key=track_key,
        track_name=track_name,
        creator=creator or _creator(),
        annotations=annotations,
        generator=generator or _generator(),
        provenance=provenance or _provenance(),
    )


def _schema_errors(pack: object) -> list[str]:
    return [error.message for error in pack_validator().iter_errors(pack)]


def _all_object_keys(value: object) -> set[str]:
    keys: set[str] = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            keys.update(current)
            stack.extend(current.values())
        elif isinstance(current, (list, tuple)):
            stack.extend(current)
    return keys


def _item_by_motivation(pack: Mapping[str, object], motivation: str):  # type: ignore[no-untyped-def]
    return next(
        item
        for item in pack["items"]  # type: ignore[union-attr]
        if item["motivation"] == motivation
    )


def test_builder_emits_exact_minimal_annotation_set_and_deterministic_ids(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
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

    pack = _build(publication, (note, highlight))

    assert _schema_errors(pack) == []
    assert set(pack) == {
        "@context",
        "id",
        "type",
        "generator",
        "generated",
        "about",
        "items",
    }
    assert pack["@context"] == ANNOTATION_CONTEXT
    assert pack["type"] == "AnnotationSet"
    assert pack["id"] == pack_id(publication.file_sha256, DEFAULT_GENERATOR_IRI)
    assert pack["generator"] == {
        "id": DEFAULT_GENERATOR_IRI,
        "type": "Software",
        "name": "Second Reader Annotation Pack Exporter",
    }
    assert pack["generated"] == "2026-08-23T10:00:00Z"
    assert pack["about"] == {
        "dc:identifier": [f"nih:sha-256;{publication.file_sha256}"],
        "dc:format": "application/epub+zip",
        "dc:title": FixtureMetadata().title,
        "dc:creator": ["Second Reader Fixture Authors"],
    }
    assert [item["id"] for item in pack["items"]] == sorted(
        item["id"] for item in pack["items"]
    )

    highlight_item = _item_by_motivation(pack, "highlighting")
    note_item = _item_by_motivation(pack, "commenting")
    assert set(highlight_item) == {
        "id",
        "type",
        "motivation",
        "created",
        "target",
    }
    assert "body" not in highlight_item
    assert note_item["body"] == {
        "type": "TextualBody",
        "value": "  Caf\u00e9: return deliberately.  ",
    }
    assert note_item["created"] == "2026-08-23T10:30:00Z"

    for draft, item in ((highlight, highlight_item), (note, note_item)):
        target = item["target"]
        assert set(target) == {"source", "selector"}
        assert [selector["type"] for selector in target["selector"]] == [
            "TextQuoteSelector",
            "TextPositionSelector",
        ]
        quote, position = target["selector"]
        assert quote["exact"] == draft.target.exact
        assert set(quote).issubset({"type", "exact", "prefix", "suffix"})
        assert position == {
            "type": "TextPositionSelector",
            "start": draft.target.start,
            "end": draft.target.end,
        }
        resource_text = publication.epub_index.resource_texts[target["source"]]
        assert resource_text[position["start"] : position["end"]] == quote["exact"]
        body = item.get("body", {}).get("value")
        assert item["id"] == annotation_id(
            publication.file_sha256,
            draft.target.href,
            draft.target.start,
            draft.target.end,
            item["motivation"],
            body,
        )

    keys = _all_object_keys(pack)
    assert all(not key.startswith("sr:") for key in keys)
    encoded = canonical_json_bytes(pack)
    assert encoded == canonical_json_bytes(pack)
    assert encoded.endswith(b"\n")
    assert b'"sr:' not in encoded


def test_internal_track_creator_and_provenance_inputs_do_not_change_public_pack(
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
    baseline = _build(publication, (highlight,))
    changed = _build(
        publication,
        (highlight,),
        track_key="another-internal-lane",
        track_name="Another Internal Lane",
        creator=_creator(
            creator_type="Organization",
            creator_id="https://example.org/private/creator",
            name="Internal Creator",
        ),
        provenance=_provenance(
            producer="https://example.org/private/producer",
            adapter_version="9.8.7",
            digest="a" * 64,
        ),
    )

    assert canonical_json_bytes(changed) == canonical_json_bytes(baseline)
    encoded = canonical_json_bytes(changed).decode()
    for private_value in (
        "another-internal-lane",
        "Another Internal Lane",
        "Internal Creator",
        "private/creator",
        "private/producer",
        "9.8.7",
        "a" * 64,
    ):
        assert private_value not in encoded


def test_builder_is_deterministic_across_input_order_and_generation_time(
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
    assert first["about"] == second["about"]


def test_builder_allows_schema_valid_empty_pack_without_export_policy(
    tmp_path: Path,
) -> None:
    pack = _build(_publication(tmp_path), ())

    assert pack["items"] == []
    assert _schema_errors(pack) == []


def test_builder_output_is_deeply_immutable_and_excludes_diagnostics(
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
    assert "provenance" not in encoded.lower()
    assert "semanticDigest" not in encoded
    assert "track" not in encoded.lower()


def test_builder_does_not_write_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    assert _schema_errors(_build(publication, (highlight,))) == []


def test_builder_snapshots_custom_sequence_once(tmp_path: Path) -> None:
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
    pack = _build(publication, annotations)

    assert annotations.iterations == 1
    assert len(pack["items"]) == 1


def test_builder_sanitizes_custom_sequence_failure(tmp_path: Path) -> None:
    publication = _publication(tmp_path)

    class ExplosiveList(list[ResolvedAnnotationDraft]):
        def __iter__(self):  # type: ignore[no-untyped-def]
            raise RuntimeError("/Users/private/producer-ledger.jsonl")

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, ExplosiveList())

    assert caught.value.code == "invalid_annotations_sequence"
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
    publication_switch = _SwitchMapping(publication_wire, changed_publication_wire)

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
    assert pack["about"]["dc:title"] == publication_wire["dc:title"]
    assert pack["items"][0]["target"]["source"] == target_wire["source"]


@pytest.mark.parametrize("boundary", ["publication", "target"])
def test_builder_sanitizes_hostile_mapping_failure(
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
        highlight = replace(
            highlight,
            target=replace(highlight.target, target=_ExplosiveMapping()),
        )

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
def test_builder_enforces_highlight_and_note_body_rules(
    tmp_path: Path,
    kind: str,
    body_text: str | None,
    code: str,
) -> None:
    publication = _publication(tmp_path)
    valid = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    invalid = replace(valid, kind=kind, body_text=body_text)  # type: ignore[arg-type]

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (invalid,))

    assert caught.value.code == code


def test_builder_rejects_note_body_limits_and_invalid_unicode(tmp_path: Path) -> None:
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
def test_builder_rejects_non_serializable_annotation_timestamps(
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


def test_builder_rejects_invalid_clock_and_nonfixed_generator(tmp_path: Path) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )

    with pytest.raises(AnnotationPackBuildError) as clock_error:
        _build(
            publication,
            (highlight,),
            generated_at=datetime(2026, 8, 23, 10, 0, 0),
        )
    assert clock_error.value.code == "invalid_datetime"

    for generator in (
        _generator(generator_id="https://example.org/other-generator"),
        _generator(name="Other Generator"),
        _generator(version="v1"),
    ):
        with pytest.raises(AnnotationPackBuildError):
            _build(publication, (highlight,), generator=generator)


def test_builder_rejects_semantic_duplicate_annotations(tmp_path: Path) -> None:
    publication = _publication(tmp_path)
    highlight = _resolved(
        publication,
        kind="highlight",
        paragraph_index=3,
        needle="durable idea",
        body_text=None,
    )
    duplicate_with_other_time = replace(
        highlight,
        created_at=datetime(2027, 1, 1, tzinfo=UTC),
    )

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(publication, (highlight, duplicate_with_other_time))

    assert caught.value.code == "duplicate_annotation_id"


def test_builder_rejects_missing_exact_epub_identity(tmp_path: Path) -> None:
    publication = _publication(tmp_path)

    with pytest.raises(AnnotationPackBuildError) as caught:
        _build(replace(publication, file_sha256="A" * 64), ())

    assert caught.value.code == "missing_publication_identity"


def test_builder_preserves_source_code_points_and_normalizes_only_note_body(
    tmp_path: Path,
) -> None:
    publication = _publication(
        tmp_path,
        chapters=(
            FixtureChapter(
                item_id="chapter-one",
                href="Text/chapter-01.xhtml",
                title="Decomposed Source",
                paragraphs=("A Cafe\u0301 returns.",),
            ),
        ),
    )
    note = _resolved(
        publication,
        kind="note",
        paragraph_index=2,
        needle="Cafe\u0301",
        body_text="Cafe\u0301",
    )

    item = _build(publication, (note,))["items"][0]

    assert item["target"]["selector"][0]["exact"] == "Cafe\u0301"
    assert item["body"]["value"] == "Caf\u00e9"
