"""Ebook parsing module for EPUB, MOBI, and PDF formats."""

from __future__ import annotations

import os
import posixpath
import re
from pathlib import Path
from typing import Any, BinaryIO, Optional, TypedDict
from urllib.parse import unquote

import ebooklib
from ebooklib import epub
from pymupdf import Document as PdfDocument

try:
    import mobi
except ImportError:
    mobi = None


class Chapter(TypedDict, total=False):
    """Parsed ebook chapter"""
    title: str
    content: str
    level: int  # TOC hierarchy level (1 for main chapters, 2 for subchapters)
    start_page: Optional[int]  # For PDF
    end_page: Optional[int]    # For PDF
    item_id: str
    href: str
    spine_index: int


def parse_ebook(file_path: str) -> list[Chapter]:
    """Parse an ebook file and extract chapter structure and content.

    Args:
        file_path: Path to the ebook file

    Returns:
        List of Chapter dicts with title, content, level, and page info

    Raises:
        ValueError: If the file format is not supported
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".epub":
        return _parse_epub(file_path)
    elif ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".mobi" or ext == ".azw":
        return _parse_mobi(file_path)
    elif ext == ".txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported ebook format: {ext}")


def _parse_epub(file_path: str) -> list[Chapter]:
    """Parse EPUB reading-order resources and their navigation labels."""
    book = epub.read_epub(file_path)
    return _chapters_from_epub_book(book)


def parse_epub_stream(source: BinaryIO) -> list[Chapter]:
    """Parse EPUB chapters from one already-open, seekable binary handle."""

    source.seek(0)
    book = epub.read_epub(source)
    return _chapters_from_epub_book(book)


def _chapters_from_epub_book(book: Any) -> list[Chapter]:
    """Read each XHTML resource once, in the publication's spine order."""
    # ebooklib resolves EPUB3 nav links, but leaves NCX links relative to the NCX.
    base = ""
    if not any(isinstance(item, epub.EpubNav) for item in book.get_items()):
        ncx = next(book.get_items_of_type(ebooklib.ITEM_NAVIGATION), None)
        if ncx is not None:
            base = posixpath.dirname(ncx.get_name())

    labels = {}
    for href, title, level in _toc_labels(book.toc):
        path, separator, _fragment = href.partition("#")
        if path:
            name = posixpath.normpath(posixpath.join(base, unquote(path)))
            # Prefer a resource-level label over a link to a heading inside it.
            if name not in labels or (labels[name][2] and not separator):
                labels[name] = (title, level, bool(separator))

    documents = {item.get_id(): item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)}
    spine = list(book.spine)
    if not book.toc or not spine:
        # Preserve the manifest fallback for books without navigation, including
        # old EPUBs whose incomplete spine omits otherwise readable documents.
        listed = {item_id for item_id, _ in spine}
        spine.extend((item_id, "yes") for item_id in documents if item_id not in listed)
    chapters = []
    seen = set()
    for index, (item_id, linear) in enumerate(spine):
        item = documents.get(item_id)
        if item is None or isinstance(item, epub.EpubNav):
            continue
        href = item.get_name()
        name = posixpath.normpath(href)
        if name in seen or (linear == "no" and name not in labels):
            continue
        seen.add(name)
        content = item.get_content().decode("utf-8", errors="ignore")
        title, level, _ = labels.get(name, ("", 1, False))
        if not title:
            match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
            title = match.group(1).strip() if match else posixpath.basename(href)
        chapters.append({
            "title": title,
            "content": content,
            "level": level,
            "start_page": None,
            "end_page": None,
            "item_id": item_id,
            "href": href,
            "spine_index": index,
        })
    return chapters


def _toc_labels(toc, level=1):
    """Yield labels from ebooklib's nested links and (section, children) pairs."""
    for entry in toc:
        if isinstance(entry, list):
            yield from _toc_labels(entry, level + 1)
            continue
        children = ()
        if isinstance(entry, tuple):
            entry, children = entry
        href = getattr(entry, "href", None)
        if isinstance(href, str):
            yield href, entry.title, level
        yield from _toc_labels(children, level + 1)


def _parse_pdf(file_path: str) -> list[Chapter]:
    """Parse PDF file and extract chapters from outline/TOC."""
    doc = PdfDocument(file_path)
    chapters = []

    # Try to get outline (TOC)
    outline = doc.outline

    if outline:
        chapters = _extract_pdf_chapters_from_outline(doc, outline, level=1)
    else:
        # Fallback: split by pages (group every ~10 pages as a chapter)
        total_pages = len(doc)
        pages_per_chapter = max(1, total_pages // 10)

        for i in range(0, total_pages, pages_per_chapter):
            end_page = min(i + pages_per_chapter, total_pages)
            content = ""

            for page_num in range(i, end_page):
                page = doc[page_num]
                content += page.get_text() + "\n"

            chapters.append({
                "title": f"Pages {i + 1}-{end_page}",
                "content": content,
                "level": 1,
                "start_page": i + 1,
                "end_page": end_page,
            })

    # If still no chapters, include full content
    if not chapters:
        full_content = "\n".join([page.get_text() for page in doc])
        chapters.append({
            "title": "Full Content",
            "content": full_content,
            "level": 1,
            "start_page": 1,
            "end_page": len(doc),
        })

    return chapters


def _extract_pdf_chapters_from_outline(doc: PdfDocument, outline, level=1) -> list[Chapter]:
    """Recursively extract chapters from PDF outline."""
    chapters = []

    for item in outline:
        if isinstance(item, list):
            # Nested outline
            chapters.extend(_extract_pdf_chapters_from_outline(doc, item, level + 1))
        else:
            # (title, destination)
            title = item.title
            dest = item.dest

            # Get page number from destination
            start_page = None
            end_page = None

            try:
                if dest:
                    if isinstance(dest, str):
                        # Named destination
                        page = doc.load_bookmark(dest)
                    else:
                        page = doc[dest] if dest else None

                    if page:
                        start_page = page.number + 1  # 0-indexed to 1-indexed
                        end_page = start_page
            except Exception:
                pass

            # Extract content for this chapter
            content = ""
            if start_page:
                for page_num in range(start_page - 1, min(start_page, len(doc))):
                    content += doc[page_num].get_text() + "\n"

            chapters.append({
                "title": title,
                "content": content,
                "level": level,
                "start_page": start_page,
                "end_page": end_page,
            })

    return chapters


def _parse_mobi(file_path: str) -> list[Chapter]:
    """Parse MOBI/AZW file and extract chapter structure."""
    if mobi is None:
        raise ValueError("mobi library not available. Install with: pip install mobi")

    # Extract MOBI to a temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the MOBI file
        headers = mobi.parse(file_path)

        # Get the full content
        content = ""

        # Try to get the full text
        if hasattr(headers, 'text'):
            content = headers.text
        else:
            # Use mobi to extract content
            name = mobi.extract(file_path, tmpdir)
            if name:
                # Try to read the extracted HTML
                html_file = os.path.join(tmpdir, name, 'mobi7', 'mobi7.html')
                if os.path.exists(html_file):
                    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    # Try other HTML files
                    for root, dirs, files in os.walk(tmpdir):
                        for f in files:
                            if f.endswith('.html'):
                                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                                    content += fp.read() + "\n"

        # Try to extract chapters from NCX (table of contents)
        chapters = []

        # Get Kindle-specific metadata
        if hasattr(headers, 'ncx'):
            try:
                ncx_data = headers.ncx
                # Parse NCX structure
                import xml.etree.ElementTree as ET
                root = ET.fromstring(ncx_data)
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

                for nav_point in root.findall('.//ncx:navPoint', ns):
                    nav_label = nav_point.find('ncx:navLabel/ncx:text', ns)
                    if nav_label is not None and nav_label.text:
                        title = nav_label.text.strip()
                        # Get content src
                        content_src = nav_point.find('ncx:content', ns)
                        if content_src is not None:
                            src = content_src.get('src', '')

                        # Try to find matching content
                        chapter_content = _extract_chapter_from_mobi_content(content, src)

                        chapters.append({
                            "title": title,
                            "content": chapter_content,
                            "level": int(nav_point.get('playOrder', '1')[:1]) if nav_point.get('playOrder') else 1,
                            "start_page": None,
                            "end_page": None,
                        })
            except Exception:
                pass

        # Fallback: if no chapters extracted, use the full content
        if not chapters:
            chapters.append({
                "title": "Full Content",
                "content": content,
                "level": 1,
                "start_page": None,
                "end_page": None,
            })

        return chapters


def _extract_chapter_from_mobi_content(full_content: str, src: str) -> str:
    """Extract a specific chapter from MOBI content based on src reference."""
    if not src:
        return full_content

    # Try to find the matching section in content
    # This is a simplified approach - in reality, MOBI content is more complex
    import re

    # Try to match the src to an HTML element ID or name
    src_id = src.split('#')[-1] if '#' in src else os.path.basename(src)

    # Look for the matching element
    pattern = rf'<[^>]*id=["\']?{re.escape(src_id)}["\']?[^>]*>(.*?)</[^>]+>'
    match = re.search(pattern, full_content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1)

    return full_content


def _parse_txt(file_path: str) -> list[Chapter]:
    """Parse plain text file - returns single chapter with full content."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    return [{
        "title": "Full Content",
        "content": content,
        "level": 1,
        "start_page": None,
        "end_page": None,
    }]
