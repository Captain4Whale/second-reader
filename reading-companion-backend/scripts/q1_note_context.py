"""Read-only, exact-source context packaging for Note review. Never reparses a book."""

from copy import deepcopy
from hashlib import sha256
import json
import posixpath
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from scripts.q1_note_form import require
from src.reading_core.book_document_identity import book_document_substrate_digest


def fingerprint(value):
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


class UnreliableNotesError(ValueError):
    """Ambiguous/conflicting source resolution requires owner review, never guessing."""


class BookSource:
    def __init__(self, root):
        root = Path(root)
        raw = (root / "public/book_document.json").read_bytes()
        self.doc = json.loads(raw)
        self.epub_raw = (root / "_assets/source.epub").read_bytes()
        self.epub_sha256 = sha256(self.epub_raw).hexdigest()
        self.substrate_sha256 = book_document_substrate_digest(self.doc)
        self.document_sha256 = sha256(raw).hexdigest()
        self.xml = {}
        # Parse the same bytes whose identity is checked; no source writes.
        import io

        with ZipFile(io.BytesIO(self.epub_raw)) as archive:
            for name in archive.namelist():
                if name.lower().endswith((".html", ".xhtml", ".htm")):
                    try:
                        self.xml[name] = ET.fromstring(archive.read(name))
                    except ET.ParseError:
                        self.xml[name] = None

    def notes(self, paragraphs):
        """Only verified numeric note links with reciprocal backlinks become resolved notes."""
        result, seen = [], set()
        for p, visible in paragraphs:
            resources = [
                name
                for name in self.xml
                if name == p["href"] or name.endswith("/" + p["href"])
            ]
            if len(resources) > 1:
                raise UnreliableNotesError("原文资源匹配不唯一，请确认：" + p["href"])
            source_root = self.xml.get(resources[0]) if resources else None
            if source_root is None:
                continue
            # BookDocument arrays are independently deduplicated and cannot be zipped.
            # Resolve the exact source block, then read each real HTML anchor atomically.
            blocks = [
                e
                for e in source_root.iter()
                if e.tag.rsplit("}", 1)[-1] in ("p", "li", "blockquote")
                and " ".join("".join(e.itertext()).split()) == p["text"]
            ]
            if len(blocks) != 1:
                continue  # Not resolved: do not invent marker-to-target associations.
            for anchor in blocks[0].iter():
                if anchor.tag.rsplit("}", 1)[-1] != "a":
                    continue
                href, marker = (
                    anchor.get("href", ""),
                    "".join(anchor.itertext()).strip(),
                )
                if (
                    not re.fullmatch(r"\s*(?:\[\d+\]|\d+|[①-⑳])\s*", marker or "")
                    or marker not in visible
                ):
                    continue
                link = urlsplit(unquote(href))
                if link.scheme or not link.fragment:
                    continue
                resource = (
                    posixpath.normpath(
                        posixpath.join(posixpath.dirname(p["href"]), link.path)
                    )
                    if link.path
                    else p["href"]
                )
                identity = resource + "#" + link.fragment
                if identity in seen:
                    continue
                seen.add(identity)
                note = dict(
                    id=fingerprint(identity),
                    marker=marker,
                    status="unresolved",
                    text="",
                    source_ref=identity,
                )
                matches = [
                    name
                    for name in self.xml
                    if name == resource or name.endswith("/" + resource)
                ]
                if len(matches) > 1:
                    raise UnreliableNotesError(
                        "原书注释资源匹配不唯一，请确认：" + identity
                    )
                root = self.xml.get(matches[0]) if matches else None
                if root is not None:
                    targets = [e for e in root.iter() if e.get("id") == link.fragment]
                    if len(targets) > 1:
                        raise UnreliableNotesError(
                            "原书注释目标 ID 重复，请确认：" + identity
                        )
                    if targets:
                        parents = {e: parent for parent in root.iter() for e in parent}
                        target = targets[0]
                        container = target
                        while container in parents and container.tag.rsplit("}", 1)[
                            -1
                        ] not in ("p", "li", "aside"):
                            container = parents[container]
                        backlinks = [e.get("href", "") for e in container.iter()]
                        source_id = anchor.get("id")
                        reciprocal = False
                        for back in backlinks:
                            back_url = urlsplit(unquote(back))
                            back_resource = (
                                posixpath.normpath(
                                    posixpath.join(
                                        posixpath.dirname(resource), back_url.path
                                    )
                                )
                                if back_url.path
                                else resource
                            )
                            reciprocal |= bool(
                                source_id
                                and back_url.fragment == source_id
                                and back_resource == p["href"]
                            )
                        content = " ".join("".join(container.itertext()).split())
                        if (
                            reciprocal
                            and p["text"].count(marker) == 1
                            and container.tag.rsplit("}", 1)[-1] in ("p", "li", "aside")
                            and len(content) > len(marker)
                        ):
                            note.update(status="resolved", text=content)
                result.append(note)
        # No recognizable link is not proof that this edition has no original notes.
        return dict(
            status="resolved"
            if result and all(n["status"] == "resolved" for n in result)
            else "unresolved",
            items=result,
        )


def point(chapter, paragraph, offset):
    return dict(chapter_id=chapter, paragraph_index=paragraph, char_offset=offset)


def segment(chapter, p, lo, hi, anchor=False):
    return dict(
        text=p["text"][lo:hi],
        anchor=anchor,
        range=dict(
            start=point(chapter["id"], p["paragraph_index"], lo),
            end=point(chapter["id"], p["paragraph_index"], hi),
        ),
    )


def contexts(source, window, mark):
    r, unit = mark["original_source_range"], window["original_source_range"]
    cid = r["end"]["chapter_id"]
    require(
        r["start"]["chapter_id"]
        == cid
        == unit["start"]["chapter_id"]
        == unit["end"]["chapter_id"],
        "不支持跨章锚点，不能猜测观察者边界",
    )
    chapters = source.doc["chapters"]
    ci = next(i for i, c in enumerate(chapters) if c["id"] == cid)
    chapter = chapters[ci]

    def coordinate(x):
        return x["paragraph_index"], x["char_offset"]

    start, cutoff = coordinate(r["start"]), coordinate(r["end"])
    ustart, uend = coordinate(unit["start"]), coordinate(unit["end"])
    require(ustart <= start < uend, "批注不属于此窗口")
    prefix, earlier, within, after, quote, note_parts = [], [], [], [], {}, []
    for c in chapters[:ci]:
        for p in c["paragraphs"]:
            if p.get("text_role") != "auxiliary" and p["text"]:
                earlier.append(
                    {
                        **segment(c, p, 0, len(p["text"])),
                        "chapter_title": c.get("title", ""),
                    }
                )
    for p in chapter["paragraphs"]:
        idx, length = p["paragraph_index"], len(p["text"])
        boundaries = {0, length}
        for pi, off in (start, cutoff, ustart, uend):
            if pi == idx:
                require(0 <= off <= length, "原文坐标越界")
                boundaries.add(off)
        bounds = sorted(boundaries)
        for lo, hi in zip(bounds, bounds[1:]):
            if lo == hi:
                continue
            pos = (idx, lo)
            part = segment(chapter, p, lo, hi, start <= pos < cutoff)
            if start <= pos < cutoff:
                quote[idx] = quote.get(idx, "") + part["text"]
            if pos < ustart:
                if p.get("text_role") != "auxiliary":
                    earlier.append(part)
            elif pos < cutoff:
                prefix.append(part)
            elif pos < uend:
                within.append(part)
            elif p.get("text_role") != "auxiliary":
                after.append(part)
        visible_end = (
            length if idx < cutoff[0] else cutoff[1] if idx == cutoff[0] else 0
        )
        if idx >= ustart[0] and visible_end:
            note_parts.append((p, p["text"][:visible_end]))
    require(
        "\n\n".join(quote.values()) == mark["source_quote"],
        "批注引用与精确原文坐标不一致",
    )
    return dict(
        prefix=prefix,
        earlier=earlier,
        within_unit=within,
        after_unit=after,
        original_notes=source.notes(note_parts),
        observer_cutoff=deepcopy(r["end"]),
    )
