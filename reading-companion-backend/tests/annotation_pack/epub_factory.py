"""Deterministic in-memory EPUB fixtures for Annotation Pack tests.

The prose below is original micro-fixture text.  Tests write returned bytes only
to pytest temporary directories; no generated binary belongs in the repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from io import BytesIO
import posixpath
from typing import Final, Iterable, Sequence
import zipfile


ZIP_TIMESTAMP: Final = (1980, 1, 1, 0, 0, 0)
DEFAULT_OPF_PATH: Final = "EPUB/package.opf"


@dataclass(frozen=True, slots=True)
class FixtureIdentifier:
    value: str
    identifier_id: str
    scheme: str | None = None
    identifier_type: str | None = None


@dataclass(frozen=True, slots=True)
class FixtureMetadata:
    title: str = "The Returning Question"
    creators: tuple[str, ...] = ("Second Reader Fixture Authors",)
    language: str = "en"
    unique_identifier_id: str = "publication-id"
    identifiers: tuple[FixtureIdentifier, ...] = (
        FixtureIdentifier(
            value="urn:uuid:3be917aa-aacc-5eaf-82df-8937c5d9fc73",
            identifier_id="publication-id",
        ),
    )


@dataclass(frozen=True, slots=True)
class FixtureChapter:
    item_id: str
    href: str
    title: str
    paragraphs: tuple[str, ...]
    in_spine: bool = True


@dataclass(frozen=True, slots=True)
class FixtureZipEntry:
    name: str
    data: bytes
    compression: int = zipfile.ZIP_STORED
    unix_mode: int = 0o100644


DEFAULT_CHAPTERS: Final = (
    FixtureChapter(
        item_id="chapter-one",
        href="Text/chapter-01.xhtml",
        title="A Small Beginning",
        paragraphs=(
            "The reader paused before the margin.",
            "A durable idea is worth returning to.",
            "Return with a better question, and the page may answer differently.",
        ),
    ),
    FixtureChapter(
        item_id="chapter-two",
        href="Text/chapter-02.xhtml",
        title="The Question Returns",
        paragraphs=(
            "Morning light crossed the notes without changing their words.",
            "What changed was the reader who met them again.",
        ),
    ),
)


def _xml(value: str) -> str:
    return escape(value, quote=True)


def _xhtml(chapter: FixtureChapter) -> bytes:
    paragraphs = "\n".join(f"    <p>{_xml(text)}</p>" for text in chapter.paragraphs)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" lang="en">\n'
        "  <head>\n"
        f"    <title>{_xml(chapter.title)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{_xml(chapter.title)}</h1>\n"
        f"{paragraphs}\n"
        "  </body>\n"
        "</html>\n"
    ).encode()


def _container(opf_path: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        "  <rootfiles>\n"
        f'    <rootfile full-path="{_xml(opf_path)}" '
        'media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n"
        "</container>\n"
    ).encode()


def _opf(metadata: FixtureMetadata, chapters: Sequence[FixtureChapter]) -> bytes:
    identifiers: list[str] = []
    refinements: list[str] = []
    for identifier in metadata.identifiers:
        scheme = (
            f' opf:scheme="{_xml(identifier.scheme)}"'
            if identifier.scheme is not None
            else ""
        )
        identifiers.append(
            "    <dc:identifier "
            f'id="{_xml(identifier.identifier_id)}"{scheme}>'
            f"{_xml(identifier.value)}</dc:identifier>"
        )
        if identifier.identifier_type is not None:
            refinements.append(
                "    <meta "
                f'refines="#{_xml(identifier.identifier_id)}" '
                'property="identifier-type">'
                f"{_xml(identifier.identifier_type)}</meta>"
            )
    creators = [
        f"    <dc:creator>{_xml(creator)}</dc:creator>" for creator in metadata.creators
    ]
    chapter_items = [
        "    <item "
        f'id="{_xml(chapter.item_id)}" href="{_xml(chapter.href)}" '
        'media-type="application/xhtml+xml"/>'
        for chapter in chapters
    ]
    spine_items = [
        f'    <itemref idref="{_xml(chapter.item_id)}"/>'
        for chapter in chapters
        if chapter.in_spine
    ]
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<package xmlns="http://www.idpf.org/2007/opf"',
        '         xmlns:dc="http://purl.org/dc/elements/1.1/"',
        '         xmlns:opf="http://www.idpf.org/2007/opf"',
        '         version="3.0"',
        f'         unique-identifier="{_xml(metadata.unique_identifier_id)}">',
        "  <metadata>",
        f"    <dc:title>{_xml(metadata.title)}</dc:title>",
        *creators,
        f"    <dc:language>{_xml(metadata.language)}</dc:language>",
        *identifiers,
        *refinements,
        "  </metadata>",
        "  <manifest>",
        *chapter_items,
        "  </manifest>",
        "  <spine>",
        *spine_items,
        "  </spine>",
        "</package>",
        "",
    ]
    return "\n".join(lines).encode()


def _archive_path(opf_path: str, href: str) -> str:
    return posixpath.join(posixpath.dirname(opf_path), href)


def fixture_entries(
    *,
    metadata: FixtureMetadata | None = None,
    chapters: Sequence[FixtureChapter] = DEFAULT_CHAPTERS,
    opf_path: str = DEFAULT_OPF_PATH,
) -> tuple[FixtureZipEntry, ...]:
    """Return the deterministic logical members of the micro EPUB."""

    fixture_metadata = metadata or FixtureMetadata()
    chapter_tuple = tuple(chapters)
    return (
        FixtureZipEntry("mimetype", b"application/epub+zip"),
        FixtureZipEntry("META-INF/container.xml", _container(opf_path)),
        FixtureZipEntry(opf_path, _opf(fixture_metadata, chapter_tuple)),
        *(
            FixtureZipEntry(_archive_path(opf_path, chapter.href), _xhtml(chapter))
            for chapter in chapter_tuple
        ),
    )


def _write_entries(entries: Iterable[FixtureZipEntry]) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, mode="w", allowZip64=False) as archive:
        for entry in entries:
            info = zipfile.ZipInfo(entry.name, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.external_attr = entry.unix_mode << 16
            info.compress_type = entry.compression
            info.flag_bits = 0
            archive.writestr(info, entry.data)
    return output.getvalue()


def build_epub_bytes(
    *,
    metadata: FixtureMetadata | None = None,
    chapters: Sequence[FixtureChapter] = DEFAULT_CHAPTERS,
    opf_path: str = DEFAULT_OPF_PATH,
    replace_entries: Sequence[FixtureZipEntry] = (),
    extra_entries: Sequence[FixtureZipEntry] = (),
    omit_entries: Sequence[str] = (),
    entry_order: Sequence[str] | None = None,
) -> bytes:
    """Build a deterministic, manually framed ZIP_STORED EPUB fixture."""

    entries = list(
        fixture_entries(metadata=metadata, chapters=chapters, opf_path=opf_path)
    )
    replacements = {entry.name: entry for entry in replace_entries}
    entries = [replacements.pop(entry.name, entry) for entry in entries]
    entries.extend(replacements.values())
    entries.extend(extra_entries)
    omitted = set(omit_entries)
    entries = [entry for entry in entries if entry.name not in omitted]

    if entry_order is not None:
        by_name: dict[str, list[FixtureZipEntry]] = {}
        for entry in entries:
            by_name.setdefault(entry.name, []).append(entry)
        ordered: list[FixtureZipEntry] = []
        for name in entry_order:
            ordered.extend(by_name.pop(name, ()))
        for entry in entries:
            if entry in by_name.get(entry.name, ()):
                ordered.append(entry)
                by_name[entry.name].remove(entry)
        entries = ordered
    return _write_entries(entries)


def repack_epub(
    content: bytes,
    *,
    reverse_members: bool = True,
    compression: int = zipfile.ZIP_DEFLATED,
) -> bytes:
    """Repack the same logical EPUB with deterministic but different ZIP bytes."""

    with zipfile.ZipFile(BytesIO(content), mode="r") as source:
        members = [(info.filename, source.read(info)) for info in source.infolist()]
    mimetype = [member for member in members if member[0] == "mimetype"]
    remainder = [member for member in members if member[0] != "mimetype"]
    if reverse_members:
        remainder.reverse()
    entries = [FixtureZipEntry(name, data) for name, data in mimetype]
    entries.extend(
        FixtureZipEntry(name, data, compression=compression) for name, data in remainder
    )
    return _write_entries(entries)


def replace_epub_entries(
    content: bytes,
    replacements: Sequence[FixtureZipEntry],
) -> bytes:
    """Replace named members while preserving every other logical member."""

    replacement_by_name = {entry.name: entry for entry in replacements}
    entries: list[FixtureZipEntry] = []
    with zipfile.ZipFile(BytesIO(content), mode="r") as source:
        for info in source.infolist():
            replacement = replacement_by_name.pop(info.filename, None)
            if replacement is not None:
                entries.append(replacement)
                continue
            entries.append(
                FixtureZipEntry(
                    name=info.filename,
                    data=source.read(info),
                    compression=info.compress_type,
                    unix_mode=(info.external_attr >> 16) & 0xFFFF,
                )
            )
    entries.extend(replacement_by_name.values())
    return _write_entries(entries)


__all__ = [
    "DEFAULT_CHAPTERS",
    "DEFAULT_OPF_PATH",
    "FixtureChapter",
    "FixtureIdentifier",
    "FixtureMetadata",
    "FixtureZipEntry",
    "ZIP_TIMESTAMP",
    "build_epub_bytes",
    "fixture_entries",
    "repack_epub",
    "replace_epub_entries",
]
