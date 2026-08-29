"""Canonical package-relative EPUB resource href normalization."""

from __future__ import annotations

import re
from urllib.parse import quote, unquote_to_bytes, urlsplit
import unicodedata


_INVALID_PERCENT_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
_UNICODE_WHITE_SPACE = frozenset(
    {
        *range(0x0009, 0x000E),
        0x0020,
        0x0085,
        0x00A0,
        0x1680,
        *range(0x2000, 0x200B),
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }
)


class EpubHrefError(ValueError):
    """Raised when an href is not a canonical safe package-local reference."""


def normalize_epub_href(href: str) -> str:
    """Return the frozen canonical OPF-relative resource href spelling."""

    if not isinstance(href, str) or not href or href != _strip_white_space(href):
        raise EpubHrefError("unsafe EPUB resource href")
    try:
        parsed = urlsplit(href)
    except ValueError:
        raise EpubHrefError("unsafe EPUB resource href") from None
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or href.startswith("/")
        or "\\" in href
        or "\x00" in href
        or any(unicodedata.category(character) == "Cc" for character in href)
        or "//" in parsed.path
        or _WINDOWS_DRIVE.match(parsed.path)
    ):
        raise EpubHrefError("unsafe EPUB resource href")
    raw_parts = parsed.path.split("/")
    while raw_parts and raw_parts[0] == ".":
        raw_parts.pop(0)
    if not raw_parts:
        raise EpubHrefError("unsafe EPUB resource href")
    decoded_parts = tuple(_decode_segment(part) for part in raw_parts)
    return "/".join(
        quote(
            part,
            safe="-._~!$&'()*+,;=@" if index == 0 else "-._~!$&'()*+,;=:@",
        )
        for index, part in enumerate(decoded_parts)
    )


def _decode_segment(segment: str) -> str:
    if _INVALID_PERCENT_ESCAPE.search(segment):
        raise EpubHrefError("unsafe EPUB resource href")
    try:
        decoded = unquote_to_bytes(segment).decode("utf-8", errors="strict")
    except (UnicodeDecodeError, ValueError):
        raise EpubHrefError("unsafe EPUB resource href") from None
    if (
        not decoded
        or decoded in {".", ".."}
        or "/" in decoded
        or "\\" in decoded
        or "\x00" in decoded
        or any(unicodedata.category(character) == "Cc" for character in decoded)
    ):
        raise EpubHrefError("unsafe EPUB resource href")
    normalized = unicodedata.normalize("NFC", decoded)
    if decoded != normalized:
        raise EpubHrefError("EPUB href must use canonical NFC Unicode")
    return normalized


def _strip_white_space(value: str) -> str:
    start = 0
    end = len(value)
    while start < end and ord(value[start]) in _UNICODE_WHITE_SPACE:
        start += 1
    while end > start and ord(value[end - 1]) in _UNICODE_WHITE_SPACE:
        end -= 1
    return value[start:end]


__all__ = ["EpubHrefError", "normalize_epub_href"]
