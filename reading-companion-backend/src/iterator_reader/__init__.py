"""Shared source parsing entry points retained for current runtime."""

from .parse import ensure_structure_for_book, parse_book

__all__ = [
    "ensure_structure_for_book",
    "parse_book",
]
