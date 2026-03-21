"""Shared mechanism boundary and registry for backend reading engines."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from src.iterator_reader.models import (
    BookAnalysisPolicy,
    BookStructure,
    BudgetPolicy,
    ReadMode,
    SkillProfileName,
)


@runtime_checkable
class ReadingMechanism(Protocol):
    """Coarse mechanism interface for pluggable backend reading engines."""

    key: str
    label: str

    def parse_book(
        self,
        book_path: Path,
        *,
        language_mode: str = "auto",
        continue_mode: bool = False,
    ) -> tuple[BookStructure, Path]:
        """Build or resume the mechanism's parse-side book structure."""

    def read_book(
        self,
        book_path: Path,
        *,
        chapter_number: int | None = None,
        continue_mode: bool = False,
        user_intent: str | None = None,
        language_mode: str = "auto",
        read_mode: ReadMode = "sequential",
        skill_profile: SkillProfileName = "balanced",
        budget_policy: BudgetPolicy | None = None,
        analysis_policy: BookAnalysisPolicy | None = None,
    ) -> tuple[BookStructure, Path, bool]:
        """Run one mechanism's reading path over a book."""


_MECHANISMS: dict[str, ReadingMechanism] = {}
_DEFAULT_MECHANISM_KEY: str | None = None


def register_mechanism(mechanism: ReadingMechanism, *, default: bool = False) -> None:
    """Register one mechanism implementation under its stable key."""

    global _DEFAULT_MECHANISM_KEY

    key = str(getattr(mechanism, "key", "") or "").strip()
    if not key:
        raise ValueError("Reading mechanisms must define a non-empty key.")

    existing = _MECHANISMS.get(key)
    if existing is not None and existing is not mechanism:
        raise ValueError(f'Reading mechanism "{key}" is already registered.')

    _MECHANISMS[key] = mechanism
    if default or _DEFAULT_MECHANISM_KEY is None:
        _DEFAULT_MECHANISM_KEY = key


def get_mechanism(key: str | None = None) -> ReadingMechanism:
    """Resolve one registered mechanism, falling back to the default."""

    resolved_key = key or _DEFAULT_MECHANISM_KEY
    if resolved_key is None:
        raise RuntimeError("No reading mechanisms have been registered.")
    try:
        return _MECHANISMS[resolved_key]
    except KeyError as exc:
        known = ", ".join(sorted(_MECHANISMS))
        raise ValueError(f'Unknown reading mechanism "{resolved_key}". Known mechanisms: {known}') from exc


def available_mechanism_keys() -> tuple[str, ...]:
    """Return the stable set of registered mechanism keys."""

    return tuple(sorted(_MECHANISMS))


def default_mechanism_key() -> str:
    """Return the current default mechanism key."""

    if _DEFAULT_MECHANISM_KEY is None:
        raise RuntimeError("No default reading mechanism has been registered.")
    return _DEFAULT_MECHANISM_KEY
