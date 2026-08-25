from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import pytest

import src.annotation_pack.anchors as anchors_module
from src.annotation_pack.anchors import (
    AnchorBuilder,
    AnchorResolutionError,
)
from src.annotation_pack.drafts import AnnotationDraft, SourceCoordinate, SourceRange
from src.annotation_pack.epub_resources import EpubResourceIndex
from src.annotation_pack.identity import (
    PublicationIdentityBuilder,
    PublicationIdentityResult,
)
from src.annotation_pack.schema import load_schema
from src.parsers import parse_ebook
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_runtime.source_normalization import normalize_book_document_source
from tests.annotation_pack.epub_factory import (
    DEFAULT_CHAPTERS,
    FixtureChapter,
    FixtureMetadata,
    build_epub_bytes,
)


UTC_NOW = datetime(2026, 8, 23, 8, 0, tzinfo=timezone.utc)
SOURCE_RECORD_DIGEST = "1" * 64


def _write_source(output_dir: Path, content: bytes) -> Path:
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    return source


def _persisted_document(
    source: Path,
    *,
    metadata: FixtureMetadata | None = None,
) -> dict[str, Any]:
    fixture_metadata = metadata or FixtureMetadata()
    canonical = build_book_document_from_chapters(
        list(parse_ebook(str(source))),
        title=fixture_metadata.title,
        author=", ".join(fixture_metadata.creators),
        book_language=fixture_metadata.language,
        output_language="en",
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        canonical,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    return normalized


def _publication(
    tmp_path: Path,
    *,
    chapters: tuple[FixtureChapter, ...] = DEFAULT_CHAPTERS,
) -> PublicationIdentityResult:
    output_dir = tmp_path / "book"
    source = _write_source(output_dir, build_epub_bytes(chapters=chapters))
    return PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=_persisted_document(source),
    )


def _paragraph(
    publication: PublicationIdentityResult,
    chapter_id: int,
    paragraph_index: int,
) -> dict[str, Any]:
    for chapter in publication.rebuilt_book_document["chapters"]:
        if chapter["id"] != chapter_id:
            continue
        for paragraph in chapter["paragraphs"]:
            if paragraph["paragraph_index"] == paragraph_index:
                return dict(paragraph)
    raise AssertionError("fixture paragraph is missing")


def _draft(
    *,
    source_range: SourceRange,
    quote: str,
    source_record_digest: str = SOURCE_RECORD_DIGEST,
) -> AnnotationDraft:
    return AnnotationDraft(
        kind="highlight",
        source_range=source_range,
        source_quote=quote,
        body_text=None,
        created_at=UTC_NOW,
        source_record_index=7,
        source_record_digest=source_record_digest,
    )


def _single_paragraph_draft(
    publication: PublicationIdentityResult,
    *,
    chapter_id: int = 1,
    paragraph_index: int = 3,
    needle: str = "durable idea",
) -> AnnotationDraft:
    text = _paragraph(publication, chapter_id, paragraph_index)["text"]
    start = text.index(needle)
    end = start + len(needle)
    return _draft(
        source_range=SourceRange(
            start=SourceCoordinate(chapter_id, paragraph_index, start),
            end=SourceCoordinate(chapter_id, paragraph_index, end),
        ),
        quote=needle,
    )


def _target_errors(target: object) -> list[str]:
    schema = load_schema()
    validator = Draft202012Validator(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": schema["$defs"],
            "$ref": "#/$defs/annotationTarget",
        },
        format_checker=FormatChecker(),
    )
    return [error.message for error in validator.iter_errors(target)]


def _copy_index(
    publication: PublicationIdentityResult,
    *,
    resource_texts: dict[str, str] | None = None,
    paragraph_ranges: dict[tuple[int, int], tuple[str, int, int]] | None = None,
    unverifiable_hrefs: frozenset[str] | None = None,
) -> EpubResourceIndex:
    original = publication.epub_index
    return EpubResourceIndex(
        manifest=original.manifest,
        resource_texts=(
            dict(original.resource_texts) if resource_texts is None else resource_texts
        ),
        paragraph_ranges=(
            dict(original.paragraph_ranges)
            if paragraph_ranges is None
            else paragraph_ranges
        ),
        unverifiable_hrefs=(
            original.unverifiable_hrefs
            if unverifiable_hrefs is None
            else unverifiable_hrefs
        ),
    )


def test_anchor_resolves_minimal_quote_and_position_target(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    draft = _single_paragraph_draft(publication)

    resolved = AnchorBuilder().resolve(draft=draft, publication=publication)

    anchor = resolved.target
    target = anchor.target
    assert anchor.exact == "durable idea"
    assert anchor.href == "Text/chapter-01.xhtml"
    href, paragraph_start, _paragraph_end = publication.epub_index.paragraph_ranges[
        (1, 3)
    ]
    assert href == anchor.href
    assert anchor.start == paragraph_start + 2
    assert anchor.end == paragraph_start + 14
    resource_text = publication.epub_index.resource_texts[anchor.href]
    assert resource_text[anchor.start : anchor.end] == anchor.exact
    assert target["selector"][0] == {
        "type": "TextQuoteSelector",
        "exact": anchor.exact,
        "prefix": resource_text[max(0, anchor.start - 64) : anchor.start],
        "suffix": resource_text[anchor.end : anchor.end + 64],
    }
    assert target["selector"][1] == {
        "type": "TextPositionSelector",
        "start": anchor.start,
        "end": anchor.end,
    }
    assert set(target) == {"source", "selector"}
    assert len(target["selector"]) == 2
    assert "sr:" not in json.dumps(target, sort_keys=True)
    assert _target_errors(target) == []
    assert anchor.findings == ()
    with pytest.raises(TypeError, match="immutable"):
        target["source"] = "Text/other.xhtml"
    with pytest.raises(TypeError, match="immutable"):
        target["selector"].append({})


def test_anchor_cross_paragraph_quote_round_trips_resource_stream(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    first = _paragraph(publication, 1, 2)["text"]
    second = _paragraph(publication, 1, 3)["text"]
    start_offset = first.index("paused")
    end_offset = len("A durable idea")
    quote = first[start_offset:] + "\n\n" + second[:end_offset]
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, start_offset),
            SourceCoordinate(1, 3, end_offset),
        ),
        quote=quote,
    )

    anchor = (
        AnchorBuilder()
        .resolve(
            draft=draft,
            publication=publication,
        )
        .target
    )

    href, first_start, _first_end = publication.epub_index.paragraph_ranges[(1, 2)]
    _href, second_start, _second_end = publication.epub_index.paragraph_ranges[(1, 3)]
    resource = publication.epub_index.resource_texts[href]
    resource_start = first_start + start_offset
    resource_end = second_start + end_offset
    assert resource[resource_start:resource_end] == quote
    assert (anchor.start, anchor.end) == (resource_start, resource_end)
    assert anchor.target["selector"][1] == {
        "type": "TextPositionSelector",
        "start": resource_start,
        "end": resource_end,
    }
    assert (
        anchor.target["selector"][0]["prefix"]
        == resource[max(0, resource_start - 64) : resource_start]
    )
    assert (
        anchor.target["selector"][0]["suffix"]
        == resource[resource_end : resource_end + 64]
    )
    assert "sr:" not in json.dumps(anchor.target, sort_keys=True)
    assert _target_errors(anchor.target) == []


@pytest.mark.parametrize(
    ("source_range", "quote", "code"),
    [
        (
            SourceRange(SourceCoordinate(99, 3, 0), SourceCoordinate(99, 3, 1)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 99, 0), SourceCoordinate(1, 99, 1)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 0), SourceCoordinate(2, 3, 1)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, -1), SourceCoordinate(1, 3, 1)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, True), SourceCoordinate(1, 3, 1)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 999), SourceCoordinate(1, 3, 1000)),
            "x",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 2), SourceCoordinate(1, 3, 2)),
            "",
            "malformed_source_span",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 2), SourceCoordinate(1, 3, 14)),
            "wrong quote",
            "unresolved_source_quote",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 2), SourceCoordinate(1, 3, 14)),
            "x" * 1025,
            "source_quote_too_long",
        ),
        (
            SourceRange(SourceCoordinate(1, 3, 0), SourceCoordinate(1, 2, 1)),
            "x",
            "malformed_source_span",
        ),
    ],
)
def test_anchor_rejects_malformed_or_unresolved_ranges_without_echo(
    tmp_path: Path,
    source_range: SourceRange,
    quote: str,
    code: str,
) -> None:
    publication = _publication(tmp_path)
    draft = _draft(
        source_range=source_range,
        quote=quote,
        source_record_digest="/private/not-a-digest",
    )

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=publication)

    assert raised.value.code == code
    assert raised.value.finding.source_record_index == 7
    assert raised.value.finding.source_record_digest is None
    if len(quote) >= 8:
        assert quote not in str(raised.value)
    assert str(tmp_path) not in str(raised.value)


def test_anchor_rejects_cross_resource_and_nonmanifest_hrefs(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    first = _paragraph(publication, 1, 2)["text"]
    second = _paragraph(publication, 1, 3)["text"]
    start_offset = first.index("paused")
    end_offset = len("A durable idea")
    cross_resource_draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, start_offset),
            SourceCoordinate(1, 3, end_offset),
        ),
        quote=first[start_offset:] + "\n\n" + second[:end_offset],
    )
    document = json.loads(json.dumps(publication.rebuilt_book_document))
    document["chapters"][0]["paragraphs"][2]["href"] = "Text/chapter-02.xhtml"
    cross_resource = replace(publication, rebuilt_book_document=document)

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=cross_resource_draft, publication=cross_resource)
    assert raised.value.code == "cross_resource_span"

    document["chapters"][0]["paragraphs"][2]["href"] = "Text/missing.xhtml"
    not_manifest = replace(publication, rebuilt_book_document=document)
    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(
            draft=_single_paragraph_draft(publication),
            publication=not_manifest,
        )
    assert raised.value.code == "target_href_not_in_manifest"


def test_anchor_rejects_missing_or_unverifiable_resource_mapping(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    draft = _single_paragraph_draft(publication)
    href = "Text/chapter-01.xhtml"
    ranges = dict(publication.epub_index.paragraph_ranges)
    ranges.pop((1, 3))
    missing = replace(
        publication,
        epub_index=_copy_index(publication, paragraph_ranges=ranges),
    )
    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=missing)
    assert raised.value.code == "resource_text_unverifiable"

    unverifiable = replace(
        publication,
        epub_index=_copy_index(
            publication,
            unverifiable_hrefs=frozenset({href}),
        ),
    )
    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=unverifiable)
    assert raised.value.code == "resource_text_unverifiable"


def test_anchor_rejects_bad_resource_range_and_resource_quote(
    tmp_path: Path,
) -> None:
    publication = _publication(tmp_path)
    draft = _single_paragraph_draft(publication)
    href = "Text/chapter-01.xhtml"
    resource_text = publication.epub_index.resource_texts[href]

    ranges = dict(publication.epub_index.paragraph_ranges)
    ranges[(1, 3)] = (href, len(resource_text), len(resource_text) + 1)
    bad_range = replace(
        publication,
        epub_index=_copy_index(publication, paragraph_ranges=ranges),
    )
    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=bad_range)
    assert raised.value.code == "resource_text_unverifiable"

    paragraph_href, paragraph_start, _paragraph_end = (
        publication.epub_index.paragraph_ranges[(1, 3)]
    )
    assert paragraph_href == href
    changed_offset = paragraph_start + 2
    tampered_text = (
        resource_text[:changed_offset]
        + ("X" if resource_text[changed_offset] != "X" else "Y")
        + resource_text[changed_offset + 1 :]
    )
    bad_quote = replace(
        publication,
        epub_index=_copy_index(
            publication,
            resource_texts={
                **publication.epub_index.resource_texts,
                href: tampered_text,
            },
        ),
    )
    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=bad_quote)
    assert raised.value.code == "resource_text_unverifiable"


def test_anchor_rejects_span_that_skips_auxiliary_resource_block(
    tmp_path: Path,
) -> None:
    chapter = FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="Auxiliary middle",
        paragraphs=(
            "Opening body.",
            "https://example.org/reference",
            "Closing body.",
        ),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    first = _paragraph(publication, 1, 2)["text"]
    last = _paragraph(publication, 1, 4)["text"]
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, 0),
            SourceCoordinate(1, 4, len(last)),
        ),
        quote=first + "\n\n" + last,
    )

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=publication)

    assert raised.value.code == "non_contiguous_resource_quote"


def test_anchor_rejects_cross_href_hidden_in_auxiliary_paragraph(
    tmp_path: Path,
) -> None:
    chapter = FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="Auxiliary href gate",
        paragraphs=(
            "Opening body.",
            "https://example.org/reference",
            "Closing body.",
        ),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    first = _paragraph(publication, 1, 2)["text"]
    last = _paragraph(publication, 1, 4)["text"]
    quote = first + "\n\n" + last
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, 0),
            SourceCoordinate(1, 4, len(last)),
        ),
        quote=quote,
    )
    document = json.loads(json.dumps(publication.rebuilt_book_document))
    document["chapters"][0]["paragraphs"][2]["href"] = "Text/other.xhtml"
    href = "Text/chapter-01.xhtml"
    resource_texts = {href: quote}
    ranges = {
        (1, 2): (href, 0, len(first)),
        (1, 4): (href, len(first) + 2, len(quote)),
    }
    tampered = replace(
        publication,
        rebuilt_book_document=document,
        epub_index=_copy_index(
            publication,
            resource_texts=resource_texts,
            paragraph_ranges=ranges,
        ),
    )

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=tampered)

    assert raised.value.code == "cross_resource_span"


@pytest.mark.parametrize(
    ("text", "split_offset"),
    [
        ("Cafe\u0301 remains decomposed.", 4),
        ("👩\u200d💻 reads.", 1),
        ("🇨🇳 flag.", 1),
    ],
)
def test_anchor_rejects_extended_grapheme_cluster_splits(
    tmp_path: Path,
    text: str,
    split_offset: int,
) -> None:
    chapter = FixtureChapter(
        item_id="unicode",
        href="Text/unicode.xhtml",
        title="Unicode",
        paragraphs=(text,),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, split_offset),
            SourceCoordinate(1, 2, len(text)),
        ),
        quote=text[split_offset:],
    )

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=publication)

    assert raised.value.code == "grapheme_boundary_split"


def test_anchor_rejects_end_boundary_inside_extended_grapheme_cluster(
    tmp_path: Path,
) -> None:
    text = "Cafe\u0301 remains decomposed."
    chapter = FixtureChapter(
        item_id="unicode-end",
        href="Text/unicode-end.xhtml",
        title="Unicode end",
        paragraphs=(text,),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, 0),
            SourceCoordinate(1, 2, 4),
        ),
        quote=text[:4],
    )

    with pytest.raises(AnchorResolutionError) as raised:
        AnchorBuilder().resolve(draft=draft, publication=publication)

    assert raised.value.code == "grapheme_boundary_split"


def test_anchor_accepts_exact_quote_at_1024_code_point_limit(
    tmp_path: Path,
) -> None:
    text = "x" * 1024
    chapter = FixtureChapter(
        item_id="exact-limit",
        href="Text/exact-limit.xhtml",
        title="Exact limit",
        paragraphs=(text,),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, 0),
            SourceCoordinate(1, 2, len(text)),
        ),
        quote=text,
    )

    anchor = AnchorBuilder().resolve(draft=draft, publication=publication).target

    assert anchor.exact == text
    assert len(anchor.exact) == 1024


def test_repeated_quote_and_duplicate_projection_are_warnings(
    tmp_path: Path,
) -> None:
    repeated = "Repeat exactly."
    chapter = FixtureChapter(
        item_id="repeated",
        href="Text/repeated.xhtml",
        title="Repeated",
        paragraphs=(repeated, repeated),
    )
    publication = _publication(tmp_path, chapters=(chapter,))
    draft = _draft(
        source_range=SourceRange(
            SourceCoordinate(1, 2, 0),
            SourceCoordinate(1, 2, len(repeated)),
        ),
        quote=repeated,
    )
    ranges = dict(publication.epub_index.paragraph_ranges)
    ranges[(99, 2)] = ranges[(1, 2)]
    duplicated = replace(
        publication,
        epub_index=_copy_index(publication, paragraph_ranges=ranges),
    )

    anchor = AnchorBuilder().resolve(draft=draft, publication=duplicated).target

    assert {finding.code for finding in anchor.findings} == {
        "quote_not_unique_in_resource",
        "duplicate_resource_chapter_projection",
    }
    assert all(finding.severity == "warning" for finding in anchor.findings)


def test_quote_uniqueness_scan_stops_after_the_second_occurrence() -> None:
    assert anchors_module._occurrence_count("a" * 1_000_000, "a") == 2


def test_anchor_module_has_no_mechanism_dependency() -> None:
    source = Path(anchors_module.__file__).read_text(encoding="utf-8")
    assert "attentional_v2" not in source
