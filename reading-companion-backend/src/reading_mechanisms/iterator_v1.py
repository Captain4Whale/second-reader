"""Adapter that exposes the current Iterator-Reader as one pluggable mechanism."""

from __future__ import annotations

from pathlib import Path

from src.iterator_reader.iterator import read_book as iterator_read_book
from src.iterator_reader.models import (
    BookAnalysisPolicy,
    BookStructure,
    BudgetPolicy,
    ReadMode,
    SkillProfileName,
)
from src.iterator_reader.parse import parse_book as iterator_parse_book


class IteratorV1Mechanism:
    """Thin adapter over the existing iterator reader implementation."""

    key = "iterator_v1"
    label = "Current Iterator-Reader implementation"

    def parse_book(
        self,
        book_path: Path,
        *,
        language_mode: str = "auto",
        continue_mode: bool = False,
    ) -> tuple[BookStructure, Path]:
        """Delegate parse-side structure generation to the existing implementation."""

        return iterator_parse_book(
            book_path,
            language_mode=language_mode,
            continue_mode=continue_mode,
        )

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
        """Delegate book reading to the current iterator runtime."""

        return iterator_read_book(
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
