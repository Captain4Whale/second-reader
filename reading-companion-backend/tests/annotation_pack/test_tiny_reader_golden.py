"""Tracked public-safe EPUB and full Annotation Pack golden acceptance."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

from src.annotation_pack.anchors import AnchorBuilder
from src.annotation_pack.builder import CreatorInput
from src.annotation_pack.drafts import AnnotationDraft, SourceCoordinate, SourceRange
from src.annotation_pack.epub_source import verify_epub_source
from src.annotation_pack.exporter import (
    ExportPolicy,
    export_annotation_pack,
    inspect_annotation_pack,
)
from src.annotation_pack.identity import (
    PublicationIdentityBuilder,
    PublicationIdentityError,
)
from src.annotation_pack.ids import default_creator_id
from src.annotation_pack.packaging import (
    ANNOTATIONS_ENTRY_NAME,
    DETACHED_ANNOTATIONS_MEDIA_TYPE,
    validate_detached_annotations,
)
from src.parsers import parse_ebook, parse_epub_stream
from src.reading_core.epub_document import build_book_document_from_chapters
from src.reading_product import CompletionEvidence, ReadingProductStore
from src.reading_product.serialization import load_document_bytes
from src.reading_runtime.source_normalization import normalize_book_document_source


BACKEND = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny-reader"
PRODUCER = FIXTURE / "producer"
GOLDEN = FIXTURE / "golden"
SOURCE = FIXTURE / "source.epub"
BUILD_SCRIPT = FIXTURE / "build_fixture.py"
DIGESTS = json.loads((GOLDEN / "digests.json").read_text(encoding="utf-8"))
GENERATED_AT = datetime(2026, 8, 24, 0, 0, 0, tzinfo=timezone.utc)
EXPECTED_EPUB_MEMBERS = (
    "mimetype",
    "META-INF/container.xml",
    "EPUB/package.opf",
    "EPUB/nav.xhtml",
    "EPUB/Text/first-return.xhtml",
    "EPUB/Text/returning-light.xhtml",
)
EXPECTED_HREFS = {
    "Text/first-return.xhtml",
    "Text/returning-light.xhtml",
}


def _materialize(tmp_path: Path) -> tuple[Path, Path, Path]:
    runtime_root = tmp_path.resolve() / "runtime"
    output_root = runtime_root / "output"
    output_dir = output_root / "tiny-reader"
    shutil.copytree(PRODUCER, output_dir)
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(SOURCE.read_bytes())
    return runtime_root, output_root, output_dir


def test_tiny_reader_producer_fixture_is_complete_product_only() -> None:
    assert (PRODUCER / "public" / "reading-products" / "current.json").is_file()
    assert not any(path.is_file() for path in (PRODUCER / "_runtime").rglob("*"))
    assert not any(path.is_file() for path in (PRODUCER / "_mechanisms").rglob("*"))


def _export(runtime_root: Path, output_root: Path, output_dir: Path):  # type: ignore[no-untyped-def]
    return export_annotation_pack(
        output_dir=output_dir,
        output_root=output_root,
        runtime_root=runtime_root,
        track_key="second-reader-agent",
        track_name="Second Reader",
        creator=CreatorInput(
            id=default_creator_id(),
            type="Software",
            name="Second Reader",
        ),
        generated_at=GENERATED_AT,
        policy=ExportPolicy(deliverables="detached"),
    )


def _parsed_document(source_bytes: bytes) -> dict[str, object]:
    with BytesIO(source_bytes) as handle:
        chapters = list(parse_epub_stream(handle))
    document = build_book_document_from_chapters(
        chapters,
        title="Tiny Reader: Returning Light",
        author="Second Reader Fixture Authors",
        book_language="en",
        output_language="en",
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        document,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    return dict(normalized)


def _synthetic_fragment_epub() -> bytes:
    """Build a true EPUB3 whose nav projects one spine resource twice."""

    entries = (
        ("mimetype", b"application/epub+zip"),
        (
            "META-INF/container.xml",
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<container version="1.0" '
            b'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            b'<rootfiles><rootfile full-path="EPUB/package.opf" '
            b'media-type="application/oebps-package+xml"/></rootfiles>'
            b"</container>\n",
        ),
        (
            "EPUB/package.opf",
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<package xmlns="http://www.idpf.org/2007/opf" '
            b'xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0" '
            b'unique-identifier="publication-id"><metadata>'
            b'<dc:identifier id="publication-id">'
            b"urn:uuid:6624ddc2-40c8-4e6d-b17d-cfe3dcb456f0"
            b"</dc:identifier><dc:title>Fragment Projection</dc:title>"
            b"<dc:creator>Second Reader Fixture Authors</dc:creator>"
            b"<dc:language>en</dc:language>"
            b'<meta property="dcterms:modified">2026-08-24T00:00:00Z</meta>'
            b"</metadata><manifest>"
            b'<item id="nav" href="nav.xhtml" '
            b'media-type="application/xhtml+xml" properties="nav"/>'
            b'<item id="shared" href="Text/shared.xhtml" '
            b'media-type="application/xhtml+xml"/>'
            b'</manifest><spine><itemref idref="shared"/></spine></package>\n',
        ),
        (
            "EPUB/nav.xhtml",
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<html xmlns="http://www.w3.org/1999/xhtml" '
            b'xmlns:epub="http://www.idpf.org/2007/ops"><head>'
            b"<title>Contents</title></head><body>"
            b'<nav epub:type="toc"><ol>'
            b'<li><a href="Text/shared.xhtml#first">First fragment</a></li>'
            b'<li><a href="Text/shared.xhtml#second">Second fragment</a></li>'
            b"</ol></nav></body></html>\n",
        ),
        (
            "EPUB/Text/shared.xhtml",
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<html xmlns="http://www.w3.org/1999/xhtml"><head>'
            b"<title>Shared resource</title></head><body>"
            b'<h1 id="first">First fragment</h1>'
            b"<p>Shared fixture body returns.</p>"
            b'<h2 id="second">Second fragment</h2>'
            b"<p>The same resource carries both entries.</p>"
            b"</body></html>\n",
        ),
    )
    output = BytesIO()
    with zipfile.ZipFile(output, mode="w", allowZip64=False) as archive:
        for name, content in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            info.flag_bits = 0
            archive.writestr(info, content)
    return output.getvalue()


def _paragraphs(document: dict[str, object], chapter_id: int) -> list[dict[str, object]]:
    for chapter in document["chapters"]:  # type: ignore[index,union-attr]
        if chapter["id"] == chapter_id:
            return chapter["paragraphs"]
    raise AssertionError("fixture chapter is missing")


def _selector(target: dict[str, object], selector_type: str) -> dict[str, object]:
    matches = [
        selector
        for selector in target["selector"]  # type: ignore[index,union-attr]
        if selector["type"] == selector_type
    ]
    assert len(matches) == 1
    return matches[0]


def _assert_anchor_round_trip(
    *,
    item: dict[str, object],
    publication,  # type: ignore[no-untyped-def]
) -> None:
    target = item["target"]
    assert isinstance(target, dict)
    href = target["source"]
    assert href in publication.epub_index.manifest.text_resource_hrefs
    assert len(target["selector"]) == 2
    assert [selector["type"] for selector in target["selector"]] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]
    quote = _selector(target, "TextQuoteSelector")
    position = _selector(target, "TextPositionSelector")
    start = position["start"]
    end = position["end"]
    assert isinstance(start, int) and isinstance(end, int)
    assert 0 <= start < end
    resource = publication.epub_index.resource_texts[href]
    assert resource[start:end] == quote["exact"]
    if "prefix" in quote:
        assert quote["prefix"] == resource[max(0, start - 64) : start]
    if "suffix" in quote:
        assert quote["suffix"] == resource[end : end + 64]


def test_tiny_reader_builder_reproduces_every_tracked_generated_byte() -> None:
    completed = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--check"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "verified 10 deterministic Tiny Reader fixture files" in completed.stdout


def test_tiny_reader_is_true_deterministic_epub3_and_real_parsed_document(
    tmp_path: Path,
) -> None:
    source_bytes = SOURCE.read_bytes()
    assert len(source_bytes) == DIGESTS["source_epub"]["bytes"] == 3158
    expected_source_sha256 = (
        "1325ba2f76406fb22a1bb0f02edd735983cc150f64cc4af5bb00fbf6d873f7a7"
    )
    assert DIGESTS["source_epub"]["sha256"] == expected_source_sha256
    assert hashlib.sha256(source_bytes).hexdigest() == expected_source_sha256
    assert len(source_bytes) > 36

    with zipfile.ZipFile(BytesIO(source_bytes), mode="r") as archive:
        members = archive.infolist()
        assert tuple(member.filename for member in members) == EXPECTED_EPUB_MEMBERS
        assert archive.read("mimetype") == b"application/epub+zip"
        assert archive.comment == b""
        for member in members:
            assert member.date_time == (1980, 1, 1, 0, 0, 0)
            assert member.create_system == 3
            assert (member.external_attr >> 16) == 0o100644
            assert member.compress_type == zipfile.ZIP_STORED
            assert member.flag_bits == 0
            assert member.extra == b""
            assert member.comment == b""

    committed_document = json.loads(
        (PRODUCER / "public" / "book_document.json").read_bytes()
    )
    assert _parsed_document(source_bytes) == committed_document
    with SOURCE.open("rb") as source_handle:
        assert parse_epub_stream(source_handle) == parse_ebook(str(SOURCE))
    assert len(committed_document["chapters"]) == 2
    assert {
        chapter["href"] for chapter in committed_document["chapters"]
    } == EXPECTED_HREFS
    first, second = committed_document["chapters"]
    assert first["spine_index"] == 0
    assert all(
        paragraph["start_cfi"] is None and paragraph["end_cfi"] is None
        for paragraph in first["paragraphs"]
    )
    assert second["spine_index"] == 1
    assert any(paragraph["start_cfi"] for paragraph in second["paragraphs"])

    _runtime_root, _output_root, output_dir = _materialize(tmp_path)
    verified = verify_epub_source(output_dir)
    assert verified.sha256 == DIGESTS["source_epub"]["sha256"]
    assert verified.metadata.title == "Tiny Reader: Returning Light"
    assert verified.metadata.creators == ("Second Reader Fixture Authors",)
    assert verified.metadata.language == "en"
    assert verified.spine_item_ids == ("first", "second")
    assert EXPECTED_HREFS <= set(verified.manifest_by_href)


def test_tiny_reader_real_export_matches_goldens_and_every_anchor_round_trips(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir = _materialize(tmp_path)
    document = json.loads((PRODUCER / "public" / "book_document.json").read_bytes())

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "published"
    assert result.revision_id == DIGESTS["pack"]["revision_id"]
    assert result.annotations_json is not None
    assert result.detached_package is not None
    assert result.validation_report is not None
    assert result.current_pointer is not None
    annotations_bytes = result.annotations_json.read_bytes()
    package_bytes = result.detached_package.read_bytes()
    report_bytes = result.validation_report.read_bytes()
    assert annotations_bytes == (GOLDEN / "annotations.json").read_bytes()
    assert package_bytes == (GOLDEN / "tiny-reader.annotations").read_bytes()
    assert report_bytes == (GOLDEN / "validation-report.json").read_bytes()
    assert result.current_pointer.read_bytes() == (GOLDEN / "current.json").read_bytes()
    assert result.detached_package.name == DIGESTS["pack"][
        "published_package_filename"
    ]

    repeated = _export(runtime_root, output_root, output_dir)
    assert repeated.status == "unchanged"
    assert repeated.revision_id == result.revision_id
    assert repeated.annotations_json == result.annotations_json
    assert repeated.detached_package == result.detached_package

    pack = json.loads(annotations_bytes)
    assert len(pack["items"]) == 2
    by_motivation = {item["motivation"]: item for item in pack["items"]}
    assert set(by_motivation) == {"highlighting", "commenting"}
    assert "body" not in by_motivation["highlighting"]
    assert by_motivation["commenting"]["body"] == {
        "type": "TextualBody",
        "value": "Returning reveals the reader as part of the annotation.",
    }
    assert {item["target"]["source"] for item in pack["items"]} == EXPECTED_HREFS
    assert all(
        "sr:EpubCfiSelector"
        not in {selector["type"] for selector in item["target"]["selector"]}
        for item in pack["items"]
    )

    publication = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=document,
    )
    for item in pack["items"]:
        _assert_anchor_round_trip(
            item=item,
            publication=publication,
        )
    package = validate_detached_annotations(
        package_bytes,
        expected_annotations_json=annotations_bytes,
    )
    assert package.validation.publishable
    assert package.annotations_json == annotations_bytes
    assert package.package_sha256 == DIGESTS["golden"]["tiny-reader.annotations"][
        "sha256"
    ]
    assert DETACHED_ANNOTATIONS_MEDIA_TYPE == (
        'application/zip;profile="https://www.w3.org/TR/epub-anno-10/"'
    )
    with zipfile.ZipFile(BytesIO(package_bytes), mode="r") as archive:
        assert archive.namelist() == [ANNOTATIONS_ENTRY_NAME]
        assert archive.read(ANNOTATIONS_ENTRY_NAME) == annotations_bytes

    inspection = inspect_annotation_pack(GOLDEN / "tiny-reader.annotations")
    assert inspection.valid
    assert dict(inspection.item_counts) == {
        "total": 2,
        "highlight": 1,
        "note": 1,
    }
    assert inspection.anchor_capabilities == (
        "TextQuoteSelector",
        "TextPositionSelector",
    )

    report = json.loads(report_bytes)
    pointer = json.loads(result.current_pointer.read_bytes())
    assert report["status"] == "valid"
    assert report["counts"] == {
        "input": 2,
        "exported": 2,
        "skipped": 0,
        "warnings": 0,
        "errors": 0,
    }
    assert pointer["annotations_json_sha256"] == hashlib.sha256(
        annotations_bytes
    ).hexdigest()
    assert pointer["detached_package_sha256"] == hashlib.sha256(
        package_bytes
    ).hexdigest()
    assert pointer["validation_report_sha256"] == hashlib.sha256(
        report_bytes
    ).hexdigest()

    public_payload = (
        annotations_bytes
        + package.annotations_json
        + report_bytes
        + result.current_pointer.read_bytes()
    ).lower()
    for private_sentinel in (
        b"fixture-internal-highlight",
        b"fixture-internal-note",
        b"fixture-internal-1",
        b"fixture-internal-2",
        b"reaction_records",
        b"attentional_v2",
        b"_mechanisms",
        b"source.epub",
        b"agent understanding",
        b"memory",
        b"selection reason",
        b"prompt",
        b"reasoning",
        b"runtime trace",
        b"audit",
        b"job",
        b"progress",
        b"feedback",
        b"rating",
        b"download",
        b"rank",
        b"compat",
        b"/users/",
        b"/home/",
        b"/private/",
        b"file://",
    ):
        assert private_sentinel not in public_payload
    assert str(output_dir).lower().encode() not in public_payload


def test_tiny_reader_default_export_rejects_product_source_identity_mismatch(
    tmp_path: Path,
) -> None:
    runtime_root, output_root, output_dir = _materialize(tmp_path)
    document = json.loads((PRODUCER / "public" / "book_document.json").read_bytes())
    current = json.loads(
        (output_dir / "public" / "reading-products" / "current.json").read_bytes()
    )
    original = load_document_bytes(
        (
            output_dir
            / "public"
            / "reading-products"
            / str(current["reading_product"])
        ).read_bytes()
    )
    wrong_digest = "f" * 64
    store = ReadingProductStore.create(
        output_dir,
        epub_sha256=wrong_digest,
        book_document=document,
        reading_id="urn:uuid:1273fa35-5bad-4a72-94a6-531a7f70351a",
        started_at=original.started_at,
    )
    for unit in original.units:
        store.commit_unit(
            unit,
            book_document=document,
            epub_sha256=wrong_digest,
        )
    store.finalize(
        book_document=document,
        epub_sha256=wrong_digest,
        completion=CompletionEvidence(
            scope="whole_book",
            chapter_number=None,
            scheduled_chapter_ids=(1, 2),
            completed_chapter_ids=(1, 2),
            reading_plan_complete=True,
        ),
        completed_at=original.completed_at,
    )

    result = _export(runtime_root, output_root, output_dir)

    assert result.status == "failed"
    assert [finding.code for finding in result.validation.findings] == [
        "reading_product_source_mismatch"
    ]


def test_tiny_reader_committed_json_and_package_validate_and_inspect_offline() -> None:
    validate = subprocess.run(
        [
            sys.executable,
            str(BACKEND / "scripts" / "validate_annotation_pack.py"),
            str(GOLDEN / "annotations.json"),
            str(GOLDEN / "tiny-reader.annotations"),
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    inspect = subprocess.run(
        [
            sys.executable,
            str(BACKEND / "scripts" / "inspect_annotation_pack.py"),
            str(GOLDEN / "tiny-reader.annotations"),
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert validate.returncode == 0, validate.stderr
    validations = [json.loads(line) for line in validate.stdout.splitlines()]
    assert len(validations) == 2
    assert all(result["status"] == "valid" for result in validations)
    assert all(result["counts"]["exported"] == 2 for result in validations)
    assert inspect.returncode == 0, inspect.stderr
    summary = json.loads(inspect.stdout)
    assert summary["valid"] is True
    assert summary["item_counts"] == {"highlight": 1, "note": 1, "total": 2}
    assert summary["anchor_capabilities"] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]
    safe_output = (validate.stdout + inspect.stdout).encode()
    assert b"durable idea" not in safe_output
    assert b"reader who met them again" not in safe_output
    assert b"Returning reveals" not in safe_output
    assert str(FIXTURE).encode() not in safe_output


def test_true_fragment_nav_epub_exposes_duplicate_spine_zero_projection(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path.resolve() / "fragment-output"
    source = output_dir / "_assets" / "source.epub"
    source.parent.mkdir(parents=True)
    source.write_bytes(_synthetic_fragment_epub())
    with source.open("rb") as handle:
        raw_chapters = list(parse_epub_stream(handle))
    assert [chapter["href"] for chapter in raw_chapters] == [
        "Text/shared.xhtml",
        "Text/shared.xhtml",
    ]
    assert [chapter["item_id"] for chapter in raw_chapters] == ["shared", "shared"]
    assert [chapter["spine_index"] for chapter in raw_chapters] == [0, 0]

    document = build_book_document_from_chapters(
        raw_chapters,
        title="Fragment Projection",
        author="Second Reader Fixture Authors",
        book_language="en",
        output_language="en",
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        document,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    assert [chapter["spine_index"] for chapter in normalized["chapters"]] == [0, 0]
    assert all(
        paragraph["spine_index"] == -1
        and paragraph["start_cfi"] is None
        and paragraph["end_cfi"] is None
        for chapter in normalized["chapters"]
        for paragraph in chapter["paragraphs"]
    )

    publication = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=normalized,
    )
    assert publication.epub_index.paragraph_ranges[(1, 2)] == (
        publication.epub_index.paragraph_ranges[(2, 2)]
    )
    quote = "fixture body"
    paragraph_text = normalized["chapters"][0]["paragraphs"][1]["text"]
    start = paragraph_text.index(quote)
    resolved = AnchorBuilder().resolve(
        draft=AnnotationDraft(
            kind="highlight",
            source_range=SourceRange(
                start=SourceCoordinate(1, 2, start),
                end=SourceCoordinate(1, 2, start + len(quote)),
            ),
            source_quote=quote,
            body_text=None,
            created_at=GENERATED_AT,
            source_record_index=0,
            source_record_digest="1" * 64,
        ),
        publication=publication,
    )
    assert [finding.code for finding in resolved.target.findings] == [
        "duplicate_resource_chapter_projection"
    ]
    assert len(resolved.target.target["selector"]) == 2


def test_optional_source_sparsity_uses_text_position_but_href_is_required(
    tmp_path: Path,
) -> None:
    _runtime_root, _output_root, output_dir = _materialize(tmp_path)
    document = json.loads((PRODUCER / "public" / "book_document.json").read_bytes())
    sparse = deepcopy(document)
    optional_paragraph_keys = {
        "start_cfi",
        "end_cfi",
        "html_id",
        "html_class",
        "epub_type",
        "role",
        "ancestor_tags",
        "ancestor_html_ids",
        "ancestor_html_classes",
        "ancestor_epub_types",
        "ancestor_roles",
        "inline_anchor_ids",
        "inline_anchor_hrefs",
        "inline_anchor_texts",
        "source_normalization",
    }
    for chapter in sparse["chapters"]:
        chapter.pop("sentences", None)
        for paragraph in chapter["paragraphs"]:
            for key in optional_paragraph_keys:
                paragraph.pop(key, None)

    publication = PublicationIdentityBuilder().build(
        output_dir=output_dir,
        persisted_book_document=sparse,
    )
    paragraph = _paragraphs(sparse, 1)[2]
    quote = "durable idea"
    start = paragraph["text"].index(quote)
    draft = AnnotationDraft(
        kind="highlight",
        source_range=SourceRange(
            start=SourceCoordinate(1, 3, start),
            end=SourceCoordinate(1, 3, start + len(quote)),
        ),
        source_quote=quote,
        body_text=None,
        created_at=GENERATED_AT,
        source_record_index=0,
        source_record_digest="1" * 64,
    )
    resolved = AnchorBuilder().resolve(draft=draft, publication=publication)
    assert [selector["type"] for selector in resolved.target.target["selector"]] == [
        "TextQuoteSelector",
        "TextPositionSelector",
    ]
    assert resolved.target.findings == ()

    missing_required_href = deepcopy(sparse)
    missing_required_href["chapters"][0]["paragraphs"][2].pop("href")
    with pytest.raises(PublicationIdentityError) as raised:
        PublicationIdentityBuilder().build(
            output_dir=output_dir,
            persisted_book_document=missing_required_href,
        )

    assert raised.value.code == "publication_substrate_mismatch"
    assert raised.value.json_pointer == "/chapters/0/paragraphs/2/href"
