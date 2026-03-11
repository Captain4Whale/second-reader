"""Tests for parse-stage structure generation."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from src.iterator_reader import parse as parse_module
from src.iterator_reader.storage import book_manifest_file, cover_asset_file, save_json


def test_build_structure_persists_semantic_segments(tmp_path, monkeypatch):
    """build_structure should write structure.json with semantic segments."""
    book_path = tmp_path / "demo.epub"
    book_path.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(parse_module, "extract_book_metadata", lambda _: ("Demo Book", "Tester"))
    monkeypatch.setattr(parse_module, "detect_book_language", lambda *_args, **_kwargs: "en")
    monkeypatch.setattr(
        parse_module,
        "parse_ebook",
        lambda _: [
            {
                "title": "Chapter One",
                "content": "<p>Alpha</p><p>Beta</p>",
                "level": 1,
                "start_page": None,
                "end_page": None,
            }
        ],
    )
    monkeypatch.setattr(
        parse_module,
        "segment_chapter_semantically",
        lambda *args, **kwargs: [
            {
                "id": "1.1",
                "summary": "作者提出第一个判断",
                "tokens": 12,
                "text": kwargs["chapter_text"],
                "paragraph_start": 1,
                "paragraph_end": 1,
                "status": "pending",
            }
        ],
    )
    monkeypatch.setattr(
        parse_module,
        "resolve_output_dir",
        lambda *_args, **_kwargs: tmp_path / "output" / "demo-book",
    )

    structure, output_dir = parse_module.build_structure(book_path, language_mode="auto")

    assert structure["book"] == "Demo Book"
    assert structure["author"] == "Tester"
    assert structure["book_language"] == "en"
    assert structure["output_language"] == "en"
    assert structure["chapters"][0]["segments"][0]["summary"] == "作者提出第一个判断"

    saved = json.loads((output_dir / "structure.json").read_text(encoding="utf-8"))
    assert saved["chapters"][0]["status"] == "pending"
    assert saved["chapters"][0]["segments"][0]["id"] == "1.1"
    assert saved["chapters"][0]["segments"][0]["segment_ref"] == "Chapter_One.1"
    assert "locator" not in saved["chapters"][0]["segments"][0]
    assert saved["chapters"][0]["segments"][0]["paragraph_locators"][0]["start_cfi"] is None
    assert "Alpha" in saved["chapters"][0]["segments"][0]["paragraph_locators"][0]["text"]
    assert (output_dir / "_assets" / "source.epub").exists()

    structure_md = (output_dir / "structure.md").read_text(encoding="utf-8")
    assert "# Structure Overview: Demo Book" in structure_md
    assert "## Chapter One" in structure_md
    assert "### Section 1: 作者提出第一个判断" in structure_md


def test_build_structure_infers_human_chapter_number(tmp_path, monkeypatch):
    """Numeric chapter titles should get a human-facing chapter number."""
    book_path = tmp_path / "demo.epub"
    book_path.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(parse_module, "extract_book_metadata", lambda _: ("Demo Book", "Tester"))
    monkeypatch.setattr(parse_module, "detect_book_language", lambda *_args, **_kwargs: "en")
    monkeypatch.setattr(
        parse_module,
        "parse_ebook",
        lambda _: [
            {
                "title": "Chapter 10",
                "content": "<p>Alpha</p><p>Beta</p>",
                "level": 1,
                "start_page": None,
                "end_page": None,
            }
        ],
    )
    monkeypatch.setattr(
        parse_module,
        "segment_chapter_semantically",
        lambda *args, **kwargs: [
            {
                "id": "1.1",
                "summary": "A segment",
                "tokens": 12,
                "text": kwargs["chapter_text"],
                "paragraph_start": 1,
                "paragraph_end": 1,
                "status": "pending",
            }
        ],
    )
    monkeypatch.setattr(
        parse_module,
        "resolve_output_dir",
        lambda *_args, **_kwargs: tmp_path / "output" / "demo-book",
    )

    structure, _output_dir = parse_module.build_structure(book_path, language_mode="auto")

    assert structure["chapters"][0]["chapter_number"] == 10
    assert structure["chapters"][0]["segments"][0]["segment_ref"] == "10.1"


def test_upgrade_structure_metadata_backfills_segment_ref(tmp_path):
    """Legacy structures without segment_ref should be upgraded in-place."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)
    structure = {
        "book": "Demo Book",
        "author": "Tester",
        "book_language": "en",
        "output_language": "en",
        "source_file": "demo.epub",
        "output_dir": str(output_dir),
        "chapters": [
            {
                "id": 6,
                "title": "Prologue",
                "status": "pending",
                "level": 1,
                "segments": [
                    {
                        "id": "6.1",
                        "summary": "A segment",
                        "tokens": 10,
                        "text": "Alpha",
                        "paragraph_start": 1,
                        "paragraph_end": 1,
                        "status": "pending",
                    }
                ],
            }
        ],
    }

    changed = parse_module._upgrade_structure_metadata(structure, output_dir)

    assert changed is True
    assert structure["chapters"][0]["segments"][0]["segment_ref"] == "Prologue.1"
    assert structure["chapters"][0]["segments"][0]["paragraph_locators"] == []


def _write_test_epub(
    path: Path,
    *,
    manifest_items: list[str],
    metadata_block: str = "",
    guide_block: str = "",
    extra_docs: dict[str, str] | None = None,
    image_payloads: dict[str, bytes] | None = None,
) -> None:
    image_payloads = image_payloads or {}
    extra_docs = extra_docs or {}
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OEBPS/content.opf",
            f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Demo</dc:title>
    <dc:creator>Tester</dc:creator>
    {metadata_block}
  </metadata>
  <manifest>
    {' '.join(manifest_items)}
  </manifest>
  <spine>
    <itemref idref="cover-page"/>
  </spine>
  {guide_block}
</package>
""",
        )
        archive.writestr(
            "OEBPS/cover.xhtml",
            """<html xmlns="http://www.w3.org/1999/xhtml"><body><p>fallback</p></body></html>""",
        )
        for doc_path, content in extra_docs.items():
            archive.writestr(doc_path, content)
        for image_path, payload in image_payloads.items():
            archive.writestr(image_path, payload)


def test_extract_epub_cover_supports_epub3_meta_cover_reference(tmp_path):
    """EPUB 3 meta name=cover should resolve even when filenames omit 'cover'."""
    epub_path = tmp_path / "meta-cover.epub"
    output_dir = tmp_path / "output"
    _write_test_epub(
        epub_path,
        metadata_block='<meta name="cover" content="image_rsrc1NC.jpg"/>',
        manifest_items=[
            '<item id="image_rsrc1NC.jpg" href="image_rsrc1NC.jpg" media-type="image/jpeg"/>',
            '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>',
        ],
        image_payloads={"OEBPS/image_rsrc1NC.jpg": b"meta-cover"},
    )

    cover_path = parse_module._extract_epub_cover(epub_path, output_dir)

    assert cover_path == output_dir / "_assets" / "cover.jpg"
    assert cover_path is not None
    assert cover_path.read_bytes() == b"meta-cover"


def test_extract_epub_cover_supports_manifest_cover_image_property(tmp_path):
    """Manifest items flagged as cover-image should be selected."""
    epub_path = tmp_path / "cover-property.epub"
    output_dir = tmp_path / "output"
    _write_test_epub(
        epub_path,
        manifest_items=[
            '<item id="img-1" href="images/front.png" media-type="image/png" properties="cover-image"/>',
            '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>',
        ],
        image_payloads={"OEBPS/images/front.png": b"cover-property"},
    )

    cover_path = parse_module._extract_epub_cover(epub_path, output_dir)

    assert cover_path == output_dir / "_assets" / "cover.png"
    assert cover_path is not None
    assert cover_path.read_bytes() == b"cover-property"


def test_extract_epub_cover_supports_guide_page_svg_image(tmp_path):
    """Guide cover pages with svg:image href should resolve to the underlying asset."""
    epub_path = tmp_path / "guide-cover.epub"
    output_dir = tmp_path / "output"
    _write_test_epub(
        epub_path,
        manifest_items=[
            '<item id="image-1" href="images/front.jpg" media-type="image/jpeg"/>',
            '<item id="cover-page" href="pages/cover.xhtml" media-type="application/xhtml+xml"/>',
        ],
        guide_block='<guide><reference type="cover" title="Cover" href="pages/cover.xhtml"/></guide>',
        extra_docs={
            "OEBPS/pages/cover.xhtml": """
<html xmlns="http://www.w3.org/1999/xhtml">
  <body>
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
      <image xlink:href="../images/front.jpg" />
    </svg>
  </body>
</html>
"""
        },
        image_payloads={"OEBPS/images/front.jpg": b"guide-cover"},
    )

    cover_path = parse_module._extract_epub_cover(epub_path, output_dir)

    assert cover_path == output_dir / "_assets" / "cover.jpg"
    assert cover_path is not None
    assert cover_path.read_bytes() == b"guide-cover"


def test_extract_epub_cover_returns_none_when_no_cover_is_declared(tmp_path):
    """Undeclared non-cover images should not be guessed as the cover."""
    epub_path = tmp_path / "no-cover.epub"
    output_dir = tmp_path / "output"
    _write_test_epub(
        epub_path,
        manifest_items=[
            '<item id="img-1" href="images/photo.jpg" media-type="image/jpeg"/>',
            '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>',
        ],
        image_payloads={"OEBPS/images/photo.jpg": b"not-cover"},
    )

    cover_path = parse_module._extract_epub_cover(epub_path, output_dir)

    assert cover_path is None
    assert not (output_dir / "_assets").exists()


def test_backfill_missing_epub_covers_updates_manifest_and_is_idempotent(tmp_path):
    """Backfill should extract one missing cover and keep the result stable across reruns."""
    runtime_root = tmp_path
    output_dir = runtime_root / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)
    source_epub = output_dir / "_assets" / "source.epub"
    source_epub.parent.mkdir(parents=True, exist_ok=True)

    _write_test_epub(
        source_epub,
        metadata_block='<meta name="cover" content="image_rsrc1NC.jpg"/>',
        manifest_items=[
            '<item id="image_rsrc1NC.jpg" href="image_rsrc1NC.jpg" media-type="image/jpeg"/>',
            '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>',
        ],
        image_payloads={"OEBPS/image_rsrc1NC.jpg": b"backfill-cover"},
    )

    save_json(
        book_manifest_file(output_dir),
        {
            "book_id": "demo-book",
            "book": "Demo",
            "author": "Tester",
            "cover_image_url": None,
            "book_language": "en",
            "output_language": "en",
            "source_file": "",
            "source_asset": {"format": "epub", "file": "_assets/source.epub"},
            "updated_at": "2026-03-11T00:00:00Z",
            "chapters": [],
        },
    )

    first = parse_module.backfill_missing_epub_covers(runtime_root)
    second = parse_module.backfill_missing_epub_covers(runtime_root)
    manifest = json.loads(book_manifest_file(output_dir).read_text(encoding="utf-8"))

    assert first == [{"book_id": "demo-book", "status": "updated", "cover_image_url": "_assets/cover.jpg"}]
    assert second == [{"book_id": "demo-book", "status": "already_present", "cover_image_url": "_assets/cover.jpg"}]
    assert manifest["cover_image_url"] == "_assets/cover.jpg"
    assert cover_asset_file(output_dir).read_bytes() == b"backfill-cover"
