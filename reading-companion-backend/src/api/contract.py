"""Public API contract helpers for ids, routes, and reaction taxonomy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REACTION_TYPES = ("highlight", "association", "discern", "retrospect", "curious")
REACTION_FILTERS = ["all", "highlight", "association", "discern", "retrospect", "curious"]
MARK_TYPES = ("resonance", "blindspot", "bookmark")

CANONICAL_ROUTES = {
    "landing": "/",
    "books": "/books",
    "book": "/books/:id",
    "chapter": "/books/:id/chapters/:chapterId",
    "marks": "/marks",
}

COMPAT_ROUTES = [
    "/bookshelf",
    "/book/:bookId",
    "/book/:bookId/chapter/:chapterId",
    "/books/:id/analysis",
    "/analysis/:bookId",
    "/bookshelf/marks",
]

LANDING_STRATEGY = {
    "owner": "frontend_static",
    "display_card_count": 5,
    "preview_source": "api",
    "preview_fallback_source": "frontend_static",
}

PUBLIC_CONTRACT_SPEC = {
    "reaction_types": list(REACTION_TYPES),
    "mark_types": list(MARK_TYPES),
    "canonical_routes": dict(CANONICAL_ROUTES),
    "compat_routes": list(COMPAT_ROUTES),
    "landing_strategy": dict(LANDING_STRATEGY),
}

_REACTION_TO_API = {
    "highlight": "highlight",
    "association": "association",
    "discern": "discern",
    "retrospect": "retrospect",
    "curious": "curious",
    "connect_back": "retrospect",
    "critique": "discern",
    "curiosity": "curious",
}

_REACTION_TO_INTERNAL = {
    "highlight": "highlight",
    "association": "association",
    "discern": "discern",
    "retrospect": "retrospect",
    "curious": "curious",
    "connect_back": "retrospect",
    "critique": "discern",
    "curiosity": "curious",
}

_MARK_TO_API = {
    "resonance": "resonance",
    "blindspot": "blindspot",
    "bookmark": "bookmark",
    "known": "resonance",
}


def _safe_api_int(namespace: str, value: str) -> int:
    digest = hashlib.sha1(f"{namespace}:{value}".encode("utf-8")).hexdigest()
    return int(digest[:13], 16)


def to_api_reaction_type(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    return _REACTION_TO_API.get(normalized, "association")


def to_internal_reaction_type(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    return _REACTION_TO_INTERNAL.get(normalized, normalized or "association")


def to_api_mark_type(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    return _MARK_TO_API.get(normalized, "bookmark")


def to_internal_mark_type(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    return _MARK_TO_API.get(normalized, normalized or "bookmark")


def to_api_book_id(book_id: str) -> int:
    return _safe_api_int("book", str(book_id))


def to_api_reaction_id(*, book_id: str, reaction_id: str) -> int:
    return _safe_api_int("reaction", f"{book_id}:{reaction_id}")


def to_api_mark_id(*, book_id: str, reaction_id: str) -> int:
    return _safe_api_int("mark", f"{book_id}:{reaction_id}")


def canonical_book_path(book_id: int) -> str:
    return f"/books/{book_id}"


def canonical_analysis_path(book_id: int) -> str:
    return f"/books/{book_id}/analysis"


def canonical_chapter_path(book_id: int, chapter_id: int) -> str:
    return f"/books/{book_id}/chapters/{chapter_id}"


def output_root(root: Path) -> Path:
    return root / "output"


def _manifest_paths(root: Path) -> list[Path]:
    """Return canonical and legacy manifest paths without duplicate book dirs."""
    manifest_paths = sorted(output_root(root).glob("*/public/book_manifest.json"))
    manifest_paths.extend(sorted(output_root(root).glob("*/book_manifest.json")))
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in manifest_paths:
        output_dir = path.parent.parent if path.parent.name == "public" else path.parent
        if output_dir in seen:
            continue
        seen.add(output_dir)
        unique_paths.append(path)
    return unique_paths


def _manifest_book_ids(root: Path) -> list[str]:
    book_ids: list[str] = []
    for manifest_path in _manifest_paths(root):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        output_dir = manifest_path.parent.parent if manifest_path.parent.name == "public" else manifest_path.parent
        book_ids.append(str(payload.get("book_id", output_dir.name)))
    return book_ids


def resolve_book_id(book_ref: int | str, *, root: Path) -> str:
    raw = str(book_ref).strip()
    if not raw:
        raise FileNotFoundError(book_ref)
    if not raw.isdigit():
        return raw

    target = int(raw)
    for internal_book_id in _manifest_book_ids(root):
        if to_api_book_id(internal_book_id) == target:
            return internal_book_id
    raise FileNotFoundError(book_ref)


def _candidate_book_ids(root: Path, *, internal_book_id: str | None = None) -> list[str]:
    if internal_book_id:
        return [internal_book_id]
    return _manifest_book_ids(root)


def _chapter_result_paths(book_dir: Path) -> list[Path]:
    """Return canonical and legacy chapter result paths for one book."""
    result_paths = sorted((book_dir / "public" / "chapters").glob("*_deep_read.json"))
    result_paths.extend(sorted(book_dir.glob("*_deep_read.json")))
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in result_paths:
        if path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)
    return unique_paths


def _iter_internal_reactions(root: Path, *, internal_book_id: str | None = None) -> list[tuple[str, str]]:
    reactions: list[tuple[str, str]] = []
    for book_id in _candidate_book_ids(root, internal_book_id=internal_book_id):
        book_dir = output_root(root) / book_id
        for path in _chapter_result_paths(book_dir):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for section in payload.get("sections", []):
                if not isinstance(section, dict):
                    continue
                for reaction in section.get("reactions", []):
                    if not isinstance(reaction, dict):
                        continue
                    internal_reaction_id = str(reaction.get("reaction_id", "")).strip()
                    if not internal_reaction_id:
                        continue
                    reactions.append((book_id, internal_reaction_id))
    return reactions


def resolve_reaction_id(
    reaction_ref: int | str,
    *,
    root: Path,
    internal_book_id: str | None = None,
) -> str:
    raw = str(reaction_ref).strip()
    if not raw:
        raise FileNotFoundError(reaction_ref)
    if not raw.isdigit():
        return raw

    target = int(raw)
    for book_id, internal_reaction_id in _iter_internal_reactions(root, internal_book_id=internal_book_id):
        if to_api_reaction_id(book_id=book_id, reaction_id=internal_reaction_id) == target:
            return internal_reaction_id
    raise FileNotFoundError(reaction_ref)


def resolve_mark_id(
    mark_ref: int | str,
    *,
    root: Path,
    internal_book_id: str | None = None,
) -> tuple[str, str]:
    raw = str(mark_ref).strip()
    if not raw:
        raise FileNotFoundError(mark_ref)

    target = int(raw) if raw.isdigit() else None
    for book_id, internal_reaction_id in _iter_internal_reactions(root, internal_book_id=internal_book_id):
        if raw.isdigit():
            if to_api_mark_id(book_id=book_id, reaction_id=internal_reaction_id) == target:
                return book_id, internal_reaction_id
            continue
        if f"{book_id}:{internal_reaction_id}" == raw:
            return book_id, internal_reaction_id
    raise FileNotFoundError(mark_ref)
