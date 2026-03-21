"""Public runtime entrypoints for pluggable backend reading mechanisms."""

from __future__ import annotations

from pathlib import Path

from src.iterator_reader.models import (
    BookAnalysisPolicy,
    BookStructure,
    BudgetPolicy,
    ReadMode,
    SkillProfileName,
)
from src.reading_mechanisms import register_builtin_mechanisms

from .mechanisms import (
    ReadingMechanism,
    available_mechanism_keys,
    default_mechanism_key,
    get_mechanism,
    register_mechanism,
)


register_builtin_mechanisms()


def parse_book(
    book_path: Path,
    *,
    language_mode: str = "auto",
    continue_mode: bool = False,
    mechanism: str | None = None,
) -> tuple[BookStructure, Path]:
    """Parse one book through the selected backend reading mechanism."""

    return get_mechanism(mechanism).parse_book(
        book_path,
        language_mode=language_mode,
        continue_mode=continue_mode,
    )


def read_book(
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
    mechanism: str | None = None,
) -> tuple[BookStructure, Path, bool]:
    """Read one book through the selected backend reading mechanism."""

    return get_mechanism(mechanism).read_book(
        book_path,
        chapter_number=chapter_number,
        continue_mode=continue_mode,
        user_intent=user_intent,
        language_mode=language_mode,
        read_mode=read_mode,
        skill_profile=skill_profile,
        budget_policy=budget_policy,
        analysis_policy=analysis_policy,
    )


__all__ = [
    "ReadingMechanism",
    "available_mechanism_keys",
    "default_mechanism_key",
    "get_mechanism",
    "parse_book",
    "read_book",
    "register_mechanism",
]
