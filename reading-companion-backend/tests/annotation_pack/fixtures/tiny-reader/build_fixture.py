#!/usr/bin/env python3
"""Rebuild the tracked public-safe Tiny Reader EPUB and Annotation Pack goldens."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
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
from src.reading_runtime.source_normalization import (  # noqa: E402
    normalize_book_document_source,
)


FIXTURE_FORMAT: Final = "sr-annotation-pack-tiny-reader-golden-v1"
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


def _reaction_row(
    *,
    kind: str,
    chapter_id: int,
    chapter_ref: str,
    paragraph_index: int,
    paragraph_text: str,
    quote: str,
    created_at: str,
    thought: str,
) -> dict[str, object]:
    start = paragraph_text.index(quote)
    end = start + len(quote)
    source_span_id = (
        f"fixture:c{chapter_id}:p{paragraph_index}@{start}-p{paragraph_index}@{end}"
    )
    start_cursor = {
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "paragraph_index": paragraph_index,
        "char_offset": start,
    }
    end_cursor = {**start_cursor, "char_offset": end}
    return {
        "reaction_id": f"fixture-internal-{kind}",
        "chapter_id": chapter_id,
        "chapter_ref": chapter_ref,
        "emitted_at_source_span_id": source_span_id,
        "record_source": "read_surface",
        "type": "association" if kind == "note" else "highlight",
        "compat_family": "association" if kind == "note" else "highlight",
        "marginalia_kind": kind,
        "thought": thought,
        "source_quote": quote,
        "primary_source_ref": {
            "source_span_id": source_span_id,
            "source_span": {
                "start_cursor": start_cursor,
                "end_cursor": end_cursor,
            },
            "quote": quote,
            "role": "reaction_anchor",
            "resolution": {
                "status": "matched",
                "method": "exact_text",
                "match_count": 1,
            },
        },
        "related_source_refs": [],
        "reconsolidation_record_id": "",
        "supersedes_reaction_id": "",
        "compatibility_section_ref": f"fixture-internal-{chapter_id}",
        "prior_link": None,
        "outside_link": None,
        "search_intent": None,
        "search_query": "",
        "search_results": [],
        "created_at": created_at,
    }


def build_reaction_ledger(document: Mapping[str, object]) -> dict[str, object]:
    """Return the exact current native settled Marginalia envelope."""

    first = _paragraph(document, chapter_id=1, paragraph_index=3)
    second = _paragraph(document, chapter_id=2, paragraph_index=3)
    return {
        "schema_version": 1,
        "mechanism_version": "attentional_v2-phase9",
        "updated_at": "2026-08-24T00:02:04Z",
        "records": [
            _reaction_row(
                kind="highlight",
                chapter_id=1,
                chapter_ref=FIRST_HEADING,
                paragraph_index=3,
                paragraph_text=first,
                quote=HIGHLIGHT_QUOTE,
                thought="",
                created_at="2026-08-24T00:01:02Z",
            ),
            _reaction_row(
                kind="note",
                chapter_id=2,
                chapter_ref=SECOND_HEADING,
                paragraph_index=3,
                paragraph_text=second,
                quote=NOTE_QUOTE,
                thought=NOTE_BODY,
                created_at="2026-08-24T00:02:03Z",
            ),
        ],
    }


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def render_fixture() -> dict[str, bytes]:
    """Render every generated tracked byte without mutating the checkout."""

    source_epub = build_source_epub()
    document = build_book_document(source_epub)
    ledger = build_reaction_ledger(document)
    producer_files = {
        "producer/public/book_document.json": _json_bytes(document),
        "producer/_runtime/run_state.json": _json_bytes({"stage": "completed"}),
        "producer/_mechanisms/attentional_v2/runtime/reaction_records.json": (
            _json_bytes(ledger)
        ),
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
            "input_snapshot_sha256": pack["sr:provenance"][
                "sr:inputSnapshotDigest"
            ]["sr:value"],
            "revision_id": result.revision_id,
            "semantic_sha256": pack["sr:semanticDigest"]["sr:value"],
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
