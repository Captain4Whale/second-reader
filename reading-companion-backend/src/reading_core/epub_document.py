"""Deterministic, no-write construction of the canonical EPUB book substrate."""

from __future__ import annotations

import re
from xml.etree import ElementTree as ET

from .book_document import BookDocument, BookMetadata, ChapterHeadingBlock
from .sentences import build_sentence_records


SKIP_TITLES = {
    "title page",
    "copyright",
    "contents",
    "dedication",
    "acknowledgments",
}

LOW_VALUE_SEGMENT_KEYWORDS = {
    "zh": [
        "注释",
        "参考文献",
        "延伸阅读",
        "版权信息",
        "图片来源",
        "网站标记",
        "网站地址",
        "出处说明",
        "元信息",
    ],
    "en": [
        "footnotes",
        "references",
        "endnotes",
        "citation",
        "citations",
        "source attribution",
        "source information",
        "image attribution",
        "painting reference",
        "website url",
        "closing metadata",
        "publication info",
        "publication details",
    ],
}

BLOCK_TAGS = {
    "p",
    "li",
    "blockquote",
    "caption",
    "div",
    "figcaption",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
CHAPTER_LABEL_PATTERNS = (
    r"^chapter\s+[0-9ivxlcdm]+\b",
    r"^part\s+[0-9ivxlcdm]+\b",
    r"^book\s+[0-9ivxlcdm]+\b",
    r"^第\s*[0-9一二三四五六七八九十百千万]+\s*[章节卷部篇]\b",
    r"^[ivxlcdm]+\b$",
)
AUXILIARY_KEYWORDS = (
    "oceanofpdf",
    "national gallery",
    "oil on canvas",
    "illustration",
    "frontispiece",
    "cover art",
    "source:",
)


def extract_plain_text(content: str) -> str:
    """Normalize HTML-ish chapter content to plain text."""
    if not content:
        return ""
    if "<" in content and ">" in content:
        content = re.sub(
            r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", content, flags=re.IGNORECASE
        )
        content = re.sub(r"<[^>]+>", "\n", content)
    content = re.sub(r"\r\n?", "\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r"[ \t]+", " ", content)
    return content.strip()


def split_into_paragraphs(text: str) -> list[str]:
    """Split normalized chapter text into readable paragraphs."""
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(paragraphs) >= 2:
        return paragraphs

    sentences = re.split(r"(?<=[.!?。！？])\s+", text)
    grouped: list[str] = []
    buffer: list[str] = []
    for sentence in sentences:
        if not sentence.strip():
            continue
        buffer.append(sentence.strip())
        if len(buffer) >= 3:
            grouped.append(" ".join(buffer))
            buffer = []
    if buffer:
        grouped.append(" ".join(buffer))
    return grouped or [text.strip()]


def infer_chapter_number(title: str) -> int | None:
    """Infer a human-facing chapter number from a chapter title."""
    normalized = (title or "").strip()
    patterns = (
        r"^chapter\s+(\d+)\b",
        r"^第\s*(\d+)\s*章\b",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _normalize_block_text(text: str) -> str:
    """Normalize one paragraph-sized text block."""
    cleaned = re.sub(r"\s+", " ", text or "")
    return cleaned.strip()


def _local_tag(tag: str) -> str:
    """Return an XML tag without its namespace prefix."""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _element_attr(element: ET.Element, name: str) -> str:
    """Return a source element attribute regardless of XML namespace prefixing."""

    for key, value in element.attrib.items():
        local_name = key.rsplit("}", 1)[-1] if "}" in key else key
        if key == name or local_name == name:
            return str(value or "").strip()
    return ""


def _heading_level_for_tag(tag: str) -> int | None:
    """Return the numeric heading level for one block tag."""
    if tag in HEADING_TAGS:
        return int(tag[1])
    return None


def _direct_text_content(element: ET.Element) -> str:
    """Return text owned directly by one element, excluding descendant blocks."""
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in list(element):
        tail = getattr(child, "tail", None)
        if tail:
            parts.append(tail)
    return _normalize_block_text(" ".join(parts))


def _has_textual_block_children(element: ET.Element) -> bool:
    """Return whether one element wraps child block elements with text."""
    for child in list(element):
        if not isinstance(child.tag, str):
            continue
        if _local_tag(str(child.tag)) not in BLOCK_TAGS:
            continue
        if _normalize_block_text("".join(child.itertext())):
            return True
    return False


def _bounded_unique(items: list[str], *, limit: int = 8) -> list[str]:
    """Return compact, order-preserving, non-empty unique strings."""

    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = _normalize_block_text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def _split_class_tokens(value: str) -> list[str]:
    """Return normalized HTML class tokens."""

    return [token.strip() for token in re.split(r"\s+", value or "") if token.strip()]


def _inline_anchor_metadata(
    element: ET.Element, *, limit: int = 6
) -> dict[str, list[str]]:
    """Return compact metadata for anchors contained inside one source block."""

    ids: list[str] = []
    hrefs: list[str] = []
    texts: list[str] = []
    for descendant in element.iter():
        if (
            not isinstance(descendant.tag, str)
            or _local_tag(str(descendant.tag)) != "a"
        ):
            continue
        ids.append(_element_attr(descendant, "id"))
        hrefs.append(_element_attr(descendant, "href"))
        texts.append(_normalize_block_text("".join(descendant.itertext())))
    return {
        "inline_anchor_ids": _bounded_unique(ids, limit=limit),
        "inline_anchor_hrefs": _bounded_unique(hrefs, limit=limit),
        "inline_anchor_texts": _bounded_unique(texts, limit=limit),
    }


def _ancestor_context_for_child(
    element: ET.Element,
    current_context: dict[str, list[str]],
    *,
    limit: int = 12,
) -> dict[str, list[str]]:
    """Return the source-structure context that descendants inherit from this element."""

    tag = _local_tag(str(element.tag))
    html_id = _element_attr(element, "id")
    html_class = _element_attr(element, "class")
    epub_type = _element_attr(element, "type")
    role = _element_attr(element, "role")
    return {
        "ancestor_tags": _bounded_unique(
            [
                *current_context.get("ancestor_tags", []),
                *([] if tag in {"html", "body"} else [tag]),
            ],
            limit=limit,
        ),
        "ancestor_html_ids": _bounded_unique(
            [*current_context.get("ancestor_html_ids", []), html_id], limit=limit
        ),
        "ancestor_html_classes": _bounded_unique(
            [
                *current_context.get("ancestor_html_classes", []),
                *_split_class_tokens(html_class),
            ],
            limit=limit,
        ),
        "ancestor_epub_types": _bounded_unique(
            [*current_context.get("ancestor_epub_types", []), epub_type],
            limit=limit,
        ),
        "ancestor_roles": _bounded_unique(
            [*current_context.get("ancestor_roles", []), role], limit=limit
        ),
    }


def _looks_like_sentence(text: str) -> bool:
    """Heuristic: return whether one text block behaves like running prose."""
    normalized = _normalize_block_text(text)
    if not normalized:
        return False
    if re.search(r"[.!?。！？][\"'”’]?\s*$", normalized):
        return True
    if len(normalized.split()) >= 18 and "," in normalized:
        return True
    return False


def _upper_ratio(text: str) -> float:
    """Return the uppercase ratio for alphabetic characters in one string."""
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for char in letters if char.isupper()) / len(letters)


def _looks_like_chapter_label(text: str) -> bool:
    """Return whether one text block looks like a chapter/part label."""
    normalized = _normalize_block_text(text)
    lowered = normalized.lower()
    return any(
        re.match(pattern, lowered, flags=re.IGNORECASE)
        for pattern in CHAPTER_LABEL_PATTERNS
    )


def _looks_like_auxiliary_text(text: str, *, at_chapter_start: bool) -> bool:
    """Return whether one block is likely metadata/citation noise, not body text."""
    normalized = _normalize_block_text(text)
    lowered = normalized.lower()
    if not normalized:
        return False
    if re.search(r"https?://|www\.|[a-z0-9.-]+\.(com|org|net|edu|gov|pdf)\b", lowered):
        return True
    if at_chapter_start and any(keyword in lowered for keyword in AUXILIARY_KEYWORDS):
        return True
    if (
        at_chapter_start
        and "[" in normalized
        and "]" in normalized
        and re.search(r"\b\d{3,4}(?:/\d{2,4})?\b", normalized)
    ):
        return True
    return False


def _looks_like_heading_text(
    text: str, *, block_tag: str, at_chapter_start: bool
) -> bool:
    """Return whether one block behaves like heading text."""
    normalized = _normalize_block_text(text)
    if not normalized:
        return False
    if block_tag in HEADING_TAGS:
        return True
    if _looks_like_chapter_label(normalized):
        return True
    if len(normalized) > 140:
        return False
    if _looks_like_sentence(normalized):
        return False
    words = normalized.split()
    if len(words) > (18 if at_chapter_start else 14):
        return False
    if _upper_ratio(normalized) >= 0.45:
        return True
    alpha_words = [word for word in words if re.search(r"[A-Za-z]", word)]
    if alpha_words and all(
        word[:1].isupper() or word.isupper() for word in alpha_words
    ):
        return True
    if (
        not at_chapter_start
        and normalized[:1].isupper()
        and len(words) <= 6
        and not re.search(r"[,;:，；：]", normalized)
    ):
        return True
    return at_chapter_start and len(words) <= 6


def _cfi_for_element(
    spine_index: int, item_id: str, path_steps: list[int]
) -> str | None:
    """Build a lightweight EPUB CFI for one XHTML element path."""
    if spine_index < 0:
        return None
    spine_step = 2 * (spine_index + 1)
    item_suffix = f"[{item_id}]" if item_id else ""
    element_path = "/4" + "".join(f"/{step}" for step in path_steps)
    return f"epubcfi(/6/{spine_step}{item_suffix}!{element_path})"


def _extract_epub_paragraph_records(
    content: str,
    *,
    href: str,
    item_id: str,
    spine_index: int,
) -> list[dict[str, object]]:
    """Extract paragraph-sized blocks with lightweight EPUB locators."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    records: list[dict[str, object]] = []

    empty_context: dict[str, list[str]] = {
        "ancestor_tags": [],
        "ancestor_html_ids": [],
        "ancestor_html_classes": [],
        "ancestor_epub_types": [],
        "ancestor_roles": [],
    }

    def walk(
        element: ET.Element,
        path_steps: list[int],
        ancestor_context: dict[str, list[str]],
    ) -> None:
        tag = _local_tag(str(element.tag))
        text = _normalize_block_text("".join(element.itertext()))
        own_text = _direct_text_content(element)
        duplicate_container = (
            tag not in HEADING_TAGS
            and text
            and _has_textual_block_children(element)
            and not own_text
        )
        if tag in BLOCK_TAGS and text and not duplicate_container:
            cfi = _cfi_for_element(spine_index, item_id, path_steps)
            records.append(
                {
                    "text": text,
                    "href": href,
                    "start_cfi": cfi,
                    "end_cfi": cfi,
                    "paragraph_index": len(records) + 1,
                    "block_tag": tag,
                    "heading_level": _heading_level_for_tag(tag),
                    "item_id": item_id,
                    "spine_index": spine_index,
                    "html_id": _element_attr(element, "id"),
                    "html_class": _element_attr(element, "class"),
                    "epub_type": _element_attr(element, "type"),
                    "role": _element_attr(element, "role"),
                    **ancestor_context,
                    **_inline_anchor_metadata(element),
                }
            )

        child_context = _ancestor_context_for_child(element, ancestor_context)
        children = [child for child in list(element) if isinstance(child.tag, str)]
        for index, child in enumerate(children, start=1):
            walk(child, [*path_steps, index * 2], child_context)

    walk(root, [], empty_context)
    return records


def _paragraph_records(chapter: dict[str, object]) -> list[dict[str, object]]:
    """Return paragraph records with optional EPUB locator metadata."""
    content = str(chapter.get("content", "") or "")
    href = str(chapter.get("href", "") or "")
    item_id = str(chapter.get("item_id", "") or "")
    spine_index = int(chapter.get("spine_index", -1) or -1)

    if href:
        records = _extract_epub_paragraph_records(
            content,
            href=href,
            item_id=item_id,
            spine_index=spine_index,
        )
        if records:
            return records

    return [
        {
            "text": paragraph,
            "href": href,
            "start_cfi": None,
            "end_cfi": None,
            "paragraph_index": index,
            "block_tag": "p",
            "heading_level": None,
            "html_id": "",
            "html_class": "",
            "epub_type": "",
            "role": "",
            "ancestor_tags": [],
            "ancestor_html_ids": [],
            "ancestor_html_classes": [],
            "ancestor_epub_types": [],
            "ancestor_roles": [],
            "inline_anchor_ids": [],
            "inline_anchor_hrefs": [],
            "inline_anchor_texts": [],
        }
        for index, paragraph in enumerate(
            split_into_paragraphs(extract_plain_text(content)), start=1
        )
    ]


def _classify_paragraph_records(
    records: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Classify chapter text blocks into structure-aware roles."""
    classified: list[dict[str, object]] = []
    body_seen = False
    for record in records:
        text = str(record.get("text", "") or "")
        block_tag = str(record.get("block_tag", "p") or "p")
        at_chapter_start = not body_seen
        text_role = "body"
        if _looks_like_auxiliary_text(text, at_chapter_start=at_chapter_start):
            text_role = "auxiliary"
        elif at_chapter_start and _looks_like_heading_text(
            text, block_tag=block_tag, at_chapter_start=True
        ):
            text_role = "chapter_heading"
        elif not at_chapter_start and _looks_like_heading_text(
            text, block_tag=block_tag, at_chapter_start=False
        ):
            text_role = "section_heading"
        else:
            body_seen = True

        classified.append(
            {
                **record,
                "block_tag": block_tag,
                "heading_level": record.get("heading_level"),
                "text_role": text_role,
            }
        )
    return classified


def _segment_locator_from_records(
    records: list[dict[str, object]],
) -> dict[str, object] | None:
    """Collapse paragraph records into one segment-level locator."""
    if not records:
        return None

    first = records[0]
    last = records[-1]
    href = str(first.get("href", "") or last.get("href", ""))
    if not href:
        return None

    return {
        "href": href,
        "start_cfi": first.get("start_cfi"),
        "end_cfi": last.get("end_cfi"),
        "paragraph_start": int(first.get("paragraph_index", 0) or 0),
        "paragraph_end": int(last.get("paragraph_index", 0) or 0),
    }


def _chapter_heading_block(
    records: list[dict[str, object]],
) -> ChapterHeadingBlock | None:
    """Collapse leading chapter heading records into one structured block."""
    heading_records = [
        record
        for record in records
        if str(record.get("text_role", "")) == "chapter_heading"
        and str(record.get("text", "")).strip()
    ]
    if not heading_records:
        return None

    texts = [
        str(record.get("text", "")).strip()
        for record in heading_records
        if str(record.get("text", "")).strip()
    ]
    if not texts:
        return None

    remaining = list(texts)
    payload: ChapterHeadingBlock = {
        "text": "\n".join(texts),
        "title": remaining[0],
    }
    if remaining and _looks_like_chapter_label(remaining[0]):
        payload["label"] = remaining.pop(0)
    if remaining:
        payload["title"] = remaining.pop(0)
    elif payload.get("label"):
        payload["title"] = str(payload["label"])
        payload.pop("label", None)

    subtitle = " / ".join(item for item in remaining if item)
    if subtitle:
        payload["subtitle"] = subtitle

    locator = _segment_locator_from_records(heading_records)
    if locator:
        payload["locator"] = locator  # type: ignore[typeddict-item]
    return payload


def _should_skip_chapter(title: str, text: str) -> bool:
    """Skip obvious front matter that should not enter deep reading."""
    normalized_title = title.strip().lower()
    if normalized_title in SKIP_TITLES:
        return True
    if normalized_title == "contents":
        return True
    if len(text.strip()) < 120 and normalized_title in {"title page", "copyright"}:
        return True
    return False


def build_book_document_from_chapters(
    raw_chapters: list[dict[str, object]],
    *,
    title: str,
    author: str,
    book_language: str,
    output_language: str,
    source_file: str,
) -> BookDocument:
    """Build a canonical BookDocument without filesystem writes, normalization, or LLM calls."""

    metadata: BookMetadata = {
        "book": title,
        "author": author,
        "book_language": book_language,
        "output_language": output_language,
        "source_file": source_file,
    }
    chapters: list[dict[str, object]] = []
    for chapter_index, raw_chapter in enumerate(raw_chapters, start=1):
        paragraph_records = _classify_paragraph_records(_paragraph_records(raw_chapter))
        chapter_text = "\n\n".join(
            str(record.get("text", ""))
            for record in paragraph_records
            if str(record.get("text_role", "body")) != "auxiliary"
        )
        if not chapter_text.strip():
            continue

        chapter_title = str(
            raw_chapter.get("title", f"Chapter {chapter_index}")
            or f"Chapter {chapter_index}"
        )
        if _should_skip_chapter(chapter_title, chapter_text):
            print(f"[skip] {chapter_title}", flush=True)
            continue

        chapter_payload: dict[str, object] = {
            "id": chapter_index,
            "title": chapter_title,
            "chapter_number": infer_chapter_number(chapter_title),
            "level": int(raw_chapter.get("level", 1) or 1),
            "paragraphs": paragraph_records,
            "sentences": build_sentence_records(
                paragraph_records, chapter_id=chapter_index
            ),
        }
        chapter_heading = _chapter_heading_block(paragraph_records)
        if chapter_heading:
            chapter_payload["chapter_heading"] = chapter_heading
        item_id = str(raw_chapter.get("item_id", "") or "")
        href = str(raw_chapter.get("href", "") or "")
        spine_index = raw_chapter.get("spine_index")
        if item_id:
            chapter_payload["item_id"] = item_id
        if href:
            chapter_payload["href"] = href
        if spine_index is not None:
            chapter_payload["spine_index"] = int(spine_index)
        chapters.append(chapter_payload)

    return {
        "metadata": metadata,
        "chapters": chapters,  # type: ignore[typeddict-item]
    }
