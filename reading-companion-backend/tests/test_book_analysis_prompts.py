"""Regression tests for the book-analysis capability prompt family."""

from __future__ import annotations

from src.prompts.capabilities.book_analysis import (
    BOOK_ANALYSIS_PROMPTS,
    BOOK_ANALYSIS_QUERY_PROMPT,
    BOOK_ANALYSIS_SKIM_PROMPT,
    BOOK_ANALYSIS_SYNTHESIS_PROMPT,
)


def test_book_analysis_prompts_use_neutral_placeholders_and_query_language_policy():
    """Skim/query templates should avoid fixed-language examples while keeping retrieval flexibility."""
    assert "<skim_summary_1_to_3_sentences>" in BOOK_ANALYSIS_SKIM_PROMPT
    assert "<claim_1>" in BOOK_ANALYSIS_SKIM_PROMPT
    assert "<deep_read_reason>" in BOOK_ANALYSIS_SKIM_PROMPT
    assert "检索词语言策略" in BOOK_ANALYSIS_QUERY_PROMPT
    assert "不受输出语言硬约束" in BOOK_ANALYSIS_QUERY_PROMPT


def test_book_analysis_prompts_include_language_contract():
    """Book-analysis generation prompts should embed the shared language contract."""
    prompts = [
        BOOK_ANALYSIS_SKIM_PROMPT,
        BOOK_ANALYSIS_SYNTHESIS_PROMPT,
    ]
    for prompt in prompts:
        assert "输出语言契约" in prompt
        assert "原文引用字段（如 anchor_quote、书中直接引文）保持原文语言，不翻译" in prompt
        assert "搜索命中字段（title/snippet/url）保持原样，不翻译、不改写" in prompt


def test_book_analysis_prompt_bundle_carries_shared_fragments():
    """The capability bundle should explicitly expose the shared fragment dependencies."""
    assert "summary/reason/note/content/reflection" in BOOK_ANALYSIS_PROMPTS.language_output_contract
    assert "`queries` 只追求检索有效性" in BOOK_ANALYSIS_PROMPTS.query_language_policy

