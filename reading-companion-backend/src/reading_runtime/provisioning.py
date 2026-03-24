"""Shared canonical provisioning helpers for backend reading mechanisms."""

from __future__ import annotations

from dataclasses import dataclass
import re
import shutil
from pathlib import Path

from src.iterator_reader.language import detect_book_language, resolve_output_language
from src.iterator_reader.parse import (
    _extract_epub_cover,
    _load_or_build_book_document,
    extract_book_metadata,
    extract_plain_text,
)
from src.parsers import parse_ebook
from src.reading_core import BookDocument

from . import artifacts as runtime_artifacts


@dataclass(frozen=True)
class ProvisionedBook:
    """Shared canonical provisioning result for one book source."""

    book_path: Path
    title: str
    author: str
    book_language: str
    output_language: str
    output_dir: Path
    raw_chapters: list[dict[str, object]] | None = None
    book_document: BookDocument | None = None


def slugify(value: str) -> str:
    """Create a stable directory slug from book metadata."""

    cleaned = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
    cleaned = re.sub(r"[-\s]+", "-", cleaned)
    return cleaned or "book"


def resolve_output_dir(
    book_path: Path,
    book_title: str,
    book_language: str,
    output_language: str,
) -> Path:
    """Resolve the output directory for one canonical book substrate."""

    slug = slugify(book_title or book_path.stem)
    if output_language != book_language:
        slug = f"{slug}-{output_language}"
    return Path("output") / slug


def ensure_output_dir(path: Path) -> None:
    """Create one output directory when needed."""

    path.mkdir(parents=True, exist_ok=True)


def ensure_source_asset(book_path: Path, output_dir: Path) -> Path:
    """Copy the source EPUB into the shared asset directory when needed."""

    destination = runtime_artifacts.source_asset_file(output_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.stat().st_mtime < book_path.stat().st_mtime:
        shutil.copy2(book_path, destination)
    return destination


def ensure_book_assets(book_path: Path, output_dir: Path) -> None:
    """Ensure shared frontend-facing source assets exist for one book."""

    ensure_source_asset(book_path, output_dir)
    if book_path.suffix.lower() == ".epub":
        _extract_epub_cover(book_path, output_dir)


def inspect_book(
    book_path: Path,
    *,
    language_mode: str = "auto",
    sample_text: str = "",
) -> ProvisionedBook:
    """Inspect one book source without forcing canonical parse generation."""

    title, author = extract_book_metadata(book_path)
    book_language = detect_book_language(book_path, sample_text=sample_text)
    output_language = resolve_output_language(language_mode, book_language)
    output_dir = resolve_output_dir(book_path, title, book_language, output_language)
    return ProvisionedBook(
        book_path=book_path,
        title=title,
        author=author,
        book_language=book_language,
        output_language=output_language,
        output_dir=output_dir,
    )


def ensure_canonical_parse(
    book_path: Path,
    *,
    language_mode: str = "auto",
) -> ProvisionedBook:
    """Ensure the shared parsed-book substrate and canonical assets exist."""

    raw_chapters = parse_ebook(str(book_path))
    sample_text = "\n".join(extract_plain_text(chapter.get("content", ""))[:300] for chapter in raw_chapters[:3])
    provisioned = inspect_book(
        book_path,
        language_mode=language_mode,
        sample_text=sample_text,
    )
    ensure_output_dir(provisioned.output_dir)
    ensure_book_assets(book_path, provisioned.output_dir)
    book_document = _load_or_build_book_document(
        book_path,
        output_dir=provisioned.output_dir,
        title=provisioned.title,
        author=provisioned.author,
        book_language=provisioned.book_language,
        output_language=provisioned.output_language,
        raw_chapters=raw_chapters,
    )
    return ProvisionedBook(
        book_path=book_path,
        title=provisioned.title,
        author=provisioned.author,
        book_language=provisioned.book_language,
        output_language=provisioned.output_language,
        output_dir=provisioned.output_dir,
        raw_chapters=raw_chapters,
        book_document=book_document,
    )
