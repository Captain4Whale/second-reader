"""Tests for prompt ownership boundaries and compatibility shims."""

from __future__ import annotations

from pathlib import Path

import src.prompts.templates as templates
from src.iterator_reader.prompts import ITERATOR_V1_PROMPTS
from src.prompts.capabilities.book_analysis import BOOK_ANALYSIS_PROMPTS
from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT
from src.reading_core.runtime_contracts import ParseRequest, ReadRequest
import src.reading_mechanisms.iterator_v1 as iterator_v1_module


def test_production_code_no_longer_imports_templates_shim():
    """Production iterator and mechanism code should not depend on the compatibility shim."""
    backend_root = Path(__file__).resolve().parents[1]
    source_roots = [
        backend_root / "src" / "iterator_reader",
        backend_root / "src" / "reading_mechanisms",
    ]
    forbidden = "src.prompts.templates"

    for root in source_roots:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert forbidden not in text, f"{path} still imports the deprecated prompt shim"


def test_templates_shim_re_exports_current_prompt_families():
    """Compatibility imports should still resolve during the migration window."""
    assert templates.READER_EXPRESS_SYSTEM == ITERATOR_V1_PROMPTS.reader_express_system
    assert templates.BOOK_ANALYSIS_QUERY_PROMPT == BOOK_ANALYSIS_PROMPTS.query_prompt
    assert templates.LANGUAGE_OUTPUT_CONTRACT == LANGUAGE_OUTPUT_CONTRACT
    assert "No reliable quote recalled" in templates.QUOTE_EXPANSION_GENERATE_SYSTEM


def test_iterator_mechanism_parse_uses_iterator_prompt_bundle(monkeypatch, tmp_path):
    """The mechanism adapter should select the iterator-owned prompt set explicitly."""
    captured: dict[str, object] = {}

    def fake_parse_book(book_path, language_mode="auto", continue_mode=False, prompt_set=ITERATOR_V1_PROMPTS):
        captured["prompt_set"] = prompt_set
        return {"book": "Demo", "author": "Author", "chapters": []}, tmp_path

    monkeypatch.setattr(iterator_v1_module, "iterator_parse_book", fake_parse_book)
    monkeypatch.setattr(
        iterator_v1_module,
        "load_book_document",
        lambda _path: {
            "metadata": {"title": "Demo", "author": "Author", "book_language": "en", "output_language": "en"},
            "chapters": [],
        },
    )

    result = iterator_v1_module.IteratorV1Mechanism().parse_book(
        ParseRequest(book_path=tmp_path / "demo.epub")
    )

    assert captured["prompt_set"] is ITERATOR_V1_PROMPTS
    assert result.mechanism.key == "iterator_v1"


def test_iterator_mechanism_read_uses_iterator_and_book_analysis_prompt_bundles(monkeypatch, tmp_path):
    """The mechanism adapter should own both mechanism and capability prompt routing."""
    captured: dict[str, object] = {}

    def fake_read_book(
        book_path,
        chapter_number=None,
        continue_mode=False,
        user_intent=None,
        language_mode="auto",
        read_mode="sequential",
        skill_profile="balanced",
        budget_policy=None,
        analysis_policy=None,
        prompt_set=ITERATOR_V1_PROMPTS,
        book_analysis_prompt_set=BOOK_ANALYSIS_PROMPTS,
    ):
        captured["prompt_set"] = prompt_set
        captured["book_analysis_prompt_set"] = book_analysis_prompt_set
        return {"book": "Demo", "author": "Author", "chapters": []}, tmp_path, False

    monkeypatch.setattr(iterator_v1_module, "iterator_read_book", fake_read_book)
    monkeypatch.setattr(
        iterator_v1_module,
        "load_book_document",
        lambda _path: {
            "metadata": {"title": "Demo", "author": "Author", "book_language": "en", "output_language": "en"},
            "chapters": [],
        },
    )

    result = iterator_v1_module.IteratorV1Mechanism().read_book(
        ReadRequest(book_path=tmp_path / "demo.epub")
    )

    assert captured["prompt_set"] is ITERATOR_V1_PROMPTS
    assert captured["book_analysis_prompt_set"] is BOOK_ANALYSIS_PROMPTS
    assert result.mechanism.key == "iterator_v1"

