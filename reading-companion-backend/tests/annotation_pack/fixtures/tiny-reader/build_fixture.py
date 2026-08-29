#!/usr/bin/env python3
"""Rebuild the tracked public-safe Tiny Reader EPUB and Annotation Pack goldens."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Final, Mapping
import zipfile


FIXTURE_ROOT: Final = Path(__file__).resolve().parent
BACKEND_ROOT: Final = FIXTURE_ROOT.parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.annotation_pack.builder import CreatorInput  # noqa: E402
from src.annotation_pack.exporter import ExportPolicy, export_annotation_pack  # noqa: E402
from src.annotation_pack.ids import default_creator_id  # noqa: E402
from src.parsers import parse_epub_stream  # noqa: E402
from src.reading_core.epub_document import (  # noqa: E402
    build_book_document_from_chapters,
)
from src.reading_core import SourceCoordinate, SourceRange  # noqa: E402
from src.reading_product import (  # noqa: E402
    CompletionEvidence,
    MarginaliaCandidate,
    ReadingProductStore,
    build_product_unit,
)
from src.reading_runtime.source_normalization import (  # noqa: E402
    normalize_book_document_source,
)


FIXTURE_FORMAT: Final = "annotation-pack-tiny-reader-reading-product-v1"
GENERATED_AT: Final = datetime(2026, 8, 24, 0, 0, 0, tzinfo=timezone.utc)
ZIP_TIMESTAMP: Final = (1980, 1, 1, 0, 0, 0)
TITLE: Final = "Tiny Reader: Returning Light"
CREATOR_NAME: Final = "Second Reader Fixture Authors"
LANGUAGE: Final = "en"
OPF_IDENTIFIER: Final = "urn:uuid:9424821f-f844-4ad4-82b4-c6a01c74aa17"
TRACK_KEY: Final = "second-reader-agent"
TRACK_NAME: Final = "Second Reader"
GOLDEN_PACKAGE_NAME: Final = "tiny-reader.annotations"

FIRST_HREF: Final = "Text/first-return.xhtml"
SECOND_HREF: Final = "Text/returning-light.xhtml"
FIRST_HEADING: Final = "First Return"
SECOND_HEADING: Final = "Returning Light"
FIRST_PARAGRAPHS: Final = (
    "The reader paused before the margin.",
    "A durable idea is worth returning to.",
    "A quiet mark can wait without closing the question.",
)
SECOND_PARAGRAPHS: Final = (
    "Morning light crossed the notes without changing their words.",
    "What changed was the reader who met them again.",
    "The page stayed still while attention found a different path.",
)
HIGHLIGHT_QUOTE: Final = "durable idea"
NOTE_QUOTE: Final = "reader who met them again"
NOTE_BODY: Final = "Returning reveals the reader as part of the annotation."
READING_ID: Final = "urn:uuid:b385225f-578c-4d75-ab38-d228849feab9"


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _xhtml(title: str, paragraphs: tuple[str, ...]) -> bytes:
    body = "\n".join(f"    <p>{paragraph}</p>" for paragraph in paragraphs)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">\n'
        "  <head>\n"
        f"    <title>{title}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{title}</h1>\n"
        f"{body}\n"
        "  </body>\n"
        "</html>\n"
    ).encode("utf-8")


def _epub_entries() -> tuple[tuple[str, bytes], ...]:
    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        "  <rootfiles>\n"
        '    <rootfile full-path="EPUB/package.opf" '
        'media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n"
        "</container>\n"
    ).encode("utf-8")
    package = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf"\n'
        '         xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        '         version="3.0"\n'
        '         unique-identifier="publication-id">\n'
        "  <metadata>\n"
        f'    <dc:identifier id="publication-id">{OPF_IDENTIFIER}</dc:identifier>\n'
        f"    <dc:title>{TITLE}</dc:title>\n"
        f"    <dc:creator>{CREATOR_NAME}</dc:creator>\n"
        f"    <dc:language>{LANGUAGE}</dc:language>\n"
        '    <meta property="dcterms:modified">2026-08-24T00:00:00Z</meta>\n'
        "  </metadata>\n"
        "  <manifest>\n"
        '    <item id="nav" href="nav.xhtml" '
        'media-type="application/xhtml+xml" properties="nav"/>\n'
        f'    <item id="first" href="{FIRST_HREF}" '
        'media-type="application/xhtml+xml"/>\n'
        f'    <item id="second" href="{SECOND_HREF}" '
        'media-type="application/xhtml+xml"/>\n'
        "  </manifest>\n"
        "  <spine>\n"
        '    <itemref idref="first"/>\n'
        '    <itemref idref="second"/>\n'
        "  </spine>\n"
        "</package>\n"
    ).encode("utf-8")
    navigation = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">\n'
        "  <head><title>Contents</title></head>\n"
        "  <body>\n"
        '    <nav epub:type="toc">\n'
        "      <h1>Contents</h1>\n"
        "      <ol>\n"
        f'        <li><a href="{FIRST_HREF}">{FIRST_HEADING}</a></li>\n'
        f'        <li><a href="{SECOND_HREF}">{SECOND_HEADING}</a></li>\n'
        "      </ol>\n"
        "    </nav>\n"
        "  </body>\n"
        "</html>\n"
    ).encode("utf-8")
    return (
        ("mimetype", b"application/epub+zip"),
        ("META-INF/container.xml", container),
        ("EPUB/package.opf", package),
        ("EPUB/nav.xhtml", navigation),
        (f"EPUB/{FIRST_HREF}", _xhtml(FIRST_HEADING, FIRST_PARAGRAPHS)),
        (f"EPUB/{SECOND_HREF}", _xhtml(SECOND_HEADING, SECOND_PARAGRAPHS)),
    )


def build_source_epub() -> bytes:
    """Return one deterministic EPUB 3 byte stream with fixed ZIP metadata."""

    output = BytesIO()
    with zipfile.ZipFile(output, mode="w", allowZip64=False) as archive:
        for name, content in _epub_entries():
            info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            info.flag_bits = 0
            archive.writestr(info, content)
    return output.getvalue()


def build_book_document(source_epub: bytes) -> dict[str, object]:
    """Parse the exact EPUB through the production neutral BookDocument path."""

    with BytesIO(source_epub) as source_handle:
        chapters = list(parse_epub_stream(source_handle))
    document = build_book_document_from_chapters(
        chapters,
        title=TITLE,
        author=CREATOR_NAME,
        book_language=LANGUAGE,
        output_language=LANGUAGE,
        source_file="_assets/source.epub",
    )
    normalized, _diagnostics = normalize_book_document_source(
        document,
        output_dir=None,
        diagnostics_path=None,
        classifier=None,
    )
    return dict(normalized)


def _paragraph(
    document: Mapping[str, object],
    *,
    chapter_id: int,
    paragraph_index: int,
) -> str:
    chapters = document.get("chapters")
    if not isinstance(chapters, list):
        raise RuntimeError("generated BookDocument has no chapters")
    for chapter in chapters:
        if not isinstance(chapter, dict) or chapter.get("id") != chapter_id:
            continue
        paragraphs = chapter.get("paragraphs")
        if not isinstance(paragraphs, list):
            break
        for paragraph in paragraphs:
            if (
                isinstance(paragraph, dict)
                and paragraph.get("paragraph_index") == paragraph_index
                and isinstance(paragraph.get("text"), str)
            ):
                return str(paragraph["text"])
    raise RuntimeError("generated BookDocument paragraph is missing")


def _range(
    chapter_id: int, paragraph_index: int, start: int, end: int
) -> SourceRange:
    return SourceRange(
        start=SourceCoordinate(chapter_id, paragraph_index, start),
        end=SourceCoordinate(chapter_id, paragraph_index, end),
    )


def build_reading_product(
    *,
    output_dir: Path,
    source_epub: bytes,
    document: Mapping[str, object],
) -> None:
    """Publish the deterministic complete product used by the Pack fixture."""

    source_sha256 = _sha256(source_epub)
    store = ReadingProductStore.create(
        output_dir,
        epub_sha256=source_sha256,
        book_document=document,
        reading_id=READING_ID,
        started_at="2026-08-24T00:00:30Z",
    )
    first = _paragraph(document, chapter_id=1, paragraph_index=3)
    second = _paragraph(document, chapter_id=2, paragraph_index=3)
    highlight_start = first.index(HIGHLIGHT_QUOTE)
    note_start = second.index(NOTE_QUOTE)
    units = (
        build_product_unit(
            unit_id="u000001",
            sequence_index=1,
            source_range=_range(1, 3, 0, len(first)),
            settled_at="2026-08-24T00:01:02Z",
            understanding="The first return treats a durable idea as worth revisiting.",
            response="The mark can remain open without closing the reader's question.",
            marginalia_candidates=(
                MarginaliaCandidate(
                    kind="highlight",
                    source_range=_range(
                        1,
                        3,
                        highlight_start,
                        highlight_start + len(HIGHLIGHT_QUOTE),
                    ),
                    source_quote=HIGHLIGHT_QUOTE,
                ),
            ),
            book_document=document,
        ),
        build_product_unit(
            unit_id="u000002",
            sequence_index=2,
            source_range=_range(2, 3, 0, len(second)),
            settled_at="2026-08-24T00:02:03Z",
            understanding="Returning reveals that the reader also changes between encounters.",
            response="The same words can support a different path of attention.",
            marginalia_candidates=(
                MarginaliaCandidate(
                    kind="note",
                    source_range=_range(
                        2,
                        3,
                        note_start,
                        note_start + len(NOTE_QUOTE),
                    ),
                    source_quote=NOTE_QUOTE,
                    body_text=NOTE_BODY,
                ),
            ),
            book_document=document,
        ),
    )
    for unit in units:
        store.commit_unit(
            unit,
            book_document=document,
            epub_sha256=source_sha256,
        )
    store.finalize(
        book_document=document,
        epub_sha256=source_sha256,
        completion=CompletionEvidence(
            scope="whole_book",
            chapter_number=None,
            scheduled_chapter_ids=(1, 2),
            completed_chapter_ids=(1, 2),
            reading_plan_complete=True,
        ),
        completed_at="2026-08-24T00:02:04Z",
    )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def render_fixture() -> dict[str, bytes]:
    """Render every generated tracked byte without mutating the checkout."""

    source_epub = build_source_epub()
    document = build_book_document(source_epub)
    producer_files = {
        "producer/public/book_document.json": _json_bytes(document),
    }

    with tempfile.TemporaryDirectory(prefix="tiny-reader-annotation-pack-") as raw:
        runtime_root = Path(raw).resolve() / "runtime"
        output_root = runtime_root / "output"
        output_dir = output_root / "tiny-reader"
        (output_dir / "_assets").mkdir(parents=True)
        (output_dir / "_assets" / "source.epub").write_bytes(source_epub)
        for relative, content in producer_files.items():
            target = output_dir / relative.removeprefix("producer/")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        build_reading_product(
            output_dir=output_dir,
            source_epub=source_epub,
            document=document,
        )
        product_root = output_dir / "public" / "reading-products"
        for path in sorted(product_root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(output_dir).as_posix()
                producer_files[f"producer/{relative}"] = path.read_bytes()

        # The Pack proof deliberately runs after all private runtime state is
        # removed.  Only BookDocument, EPUB, and the complete public Product
        # remain as inputs.
        shutil.rmtree(output_dir / "_runtime")

        result = export_annotation_pack(
            output_dir=output_dir,
            output_root=output_root,
            runtime_root=runtime_root,
            track_key=TRACK_KEY,
            track_name=TRACK_NAME,
            creator=CreatorInput(
                id=default_creator_id(),
                type="Software",
                name="Second Reader",
            ),
            generated_at=GENERATED_AT,
            policy=ExportPolicy(deliverables="detached"),
        )
        if result.status != "published":
            codes = [finding.code for finding in result.validation.findings]
            raise RuntimeError(f"fixture export failed: {result.status} {codes}")
        required = (
            result.annotations_json,
            result.detached_package,
            result.validation_report,
            result.current_pointer,
        )
        if any(path is None for path in required) or result.revision_id is None:
            raise RuntimeError("fixture export omitted a required detached artifact")
        assert result.annotations_json is not None
        assert result.detached_package is not None
        assert result.validation_report is not None
        assert result.current_pointer is not None
        annotations_json = result.annotations_json.read_bytes()
        detached_package = result.detached_package.read_bytes()
        validation_report = result.validation_report.read_bytes()
        current_pointer = result.current_pointer.read_bytes()
        pack = json.loads(annotations_json)
        pointer = json.loads(current_pointer)
        report = json.loads(validation_report)
        track_slug = result.current_pointer.parent.name

    files = {
        "source.epub": source_epub,
        **producer_files,
        "golden/annotations.json": annotations_json,
        f"golden/{GOLDEN_PACKAGE_NAME}": detached_package,
        "golden/validation-report.json": validation_report,
        "golden/current.json": current_pointer,
    }
    digests = {
        "format": FIXTURE_FORMAT,
        "generated_at": GENERATED_AT.isoformat().replace("+00:00", "Z"),
        "source_epub": {
            "bytes": len(source_epub),
            "sha256": _sha256(source_epub),
        },
        "producer": {
            relative.removeprefix("producer/"): {
                "bytes": len(content),
                "sha256": _sha256(content),
            }
            for relative, content in sorted(producer_files.items())
        },
        "golden": {
            "annotations.json": {
                "bytes": len(annotations_json),
                "sha256": _sha256(annotations_json),
            },
            GOLDEN_PACKAGE_NAME: {
                "bytes": len(detached_package),
                "sha256": _sha256(detached_package),
            },
            "validation-report.json": {
                "bytes": len(validation_report),
                "sha256": _sha256(validation_report),
            },
            "current.json": {
                "bytes": len(current_pointer),
                "sha256": _sha256(current_pointer),
            },
        },
        "pack": {
            "annotation_count": len(pack["items"]),
            "input_snapshot_sha256": report["input_snapshot_digest"],
            "revision_id": result.revision_id,
            "semantic_sha256": report["semantic_digest"],
            "producer": report["producer"],
            "adapter_version": report["adapter_version"],
            "track_slug": track_slug,
            "published_package_filename": Path(pointer["detached_package"]).name,
        },
    }
    files["golden/digests.json"] = _json_bytes(digests)
    return files


def _generated_checkout_files() -> set[str]:
    result = {"source.epub"} if (FIXTURE_ROOT / "source.epub").is_file() else set()
    for directory in ("producer", "golden"):
        root = FIXTURE_ROOT / directory
        if not root.exists():
            continue
        result.update(
            path.relative_to(FIXTURE_ROOT).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        )
    return result


def check_fixture(rendered: Mapping[str, bytes]) -> None:
    expected = set(rendered)
    actual = _generated_checkout_files()
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SystemExit(f"generated fixture file set drift: missing={missing} extra={extra}")
    drifted = [
        relative
        for relative, content in sorted(rendered.items())
        if (FIXTURE_ROOT / relative).read_bytes() != content
    ]
    if drifted:
        raise SystemExit(f"generated fixture byte drift: {drifted}")

    source_epub = rendered["source.epub"]
    source_sha256 = _sha256(source_epub)
    readme = (FIXTURE_ROOT / "README.md").read_text(encoding="utf-8")
    if str(len(source_epub)) not in readme or source_sha256 not in readme:
        raise SystemExit(
            "fixture README provenance drift: source byte length or SHA-256 is stale"
        )


def write_fixture(rendered: Mapping[str, bytes]) -> None:
    for relative, content in sorted(rendered.items()):
        target = FIXTURE_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="compare a fresh offline rebuild with every tracked generated byte",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="write the deterministic source, producer, and golden files",
    )
    arguments = parser.parse_args()
    rendered = render_fixture()
    if arguments.write:
        write_fixture(rendered)
        print(f"wrote {len(rendered)} deterministic Tiny Reader fixture files")
        return 0
    check_fixture(rendered)
    print(f"verified {len(rendered)} deterministic Tiny Reader fixture files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
