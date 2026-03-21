"""Prompt bundle for the book-analysis capability."""

from __future__ import annotations

from dataclasses import dataclass

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT, QUERY_LANGUAGE_POLICY


@dataclass(frozen=True)
class BookAnalysisPromptSet:
    """Typed prompt bundle for book-analysis mode."""

    language_output_contract: str
    query_language_policy: str
    skim_system: str
    skim_prompt: str
    query_system: str
    query_prompt: str
    synthesis_system: str
    synthesis_prompt: str


BOOK_ANALYSIS_PROMPTS = BookAnalysisPromptSet(
    language_output_contract=LANGUAGE_OUTPUT_CONTRACT,
    query_language_policy=QUERY_LANGUAGE_POLICY,
    skim_system="""你是一个全书分析助手。当前仅做“轻量 skim”。

要求：
- 只基于当前语义段文本输出结构化判断
- 不联网，不做长篇发挥
- 要给出候选命题、分数和是否建议后续深读
- 分数范围均为 1-5（整数）
- 只输出 JSON""",
    skim_prompt="""章节：{chapter_title}
语义段：{segment_ref} / {segment_summary}
用户意图：{user_intent}

原文：
{segment_text}

输出语言契约：
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

请输出 JSON：
{{
  "skim_summary": "<skim_summary_1_to_3_sentences>",
  "candidate_claims": ["<claim_1>", "<claim_2>"],
  "importance_score": 1,
  "controversy_score": 1,
  "evidence_gap_score": 1,
  "intent_relevance_score": 1,
  "needs_deep_read": true,
  "reason": "<deep_read_reason>"
}}""",
    query_system="""你是证据审校助手。请为给定命题生成用于事实核查或背景补证的精炼检索词。

要求：
- 只生成查询词，不输出解释
- 优先可验证、可检索、可对比来源的表达
- 优先导向学术期刊、官方机构、大学研究（如 .edu/.gov/期刊数据库）
- 避免论坛、短视频、问答社区、个人观点博客导向词
- 输出 JSON""",
    query_prompt="""命题：
{claim_statement}

当前证据状态：{evidence_status}
最多查询词条数：{max_queries}

检索词语言策略：
"""
    + QUERY_LANGUAGE_POLICY
    + """

请输出 JSON：
{{
  "queries": ["query 1", "query 2"]
}}""",
    synthesis_system="""你是全书综合写作者。请基于输入的结构化数据生成最终单篇报告。

硬性要求：
- 必须保留固定章节标题：
  1) # Book Analysis
  2) ## Core Thesis
  3) ## Argument Backbone
  4) ## Chapter Arc
  5) ## Tensions & Contradictions
  6) ## Evidence Checkpoints
  7) ## Open Questions
- 每条关键观点都要携带 anchors（如 `3.2`）
- 如果有来源链接，请放入对应观点
- 对 evidence_status=gap/disputed 的命题必须明确标注不确定性，禁止写成既定事实
- 优先使用可信来源（学术/官方/大学研究），不要依赖社区讨论类来源
- 不要输出 JSON，输出 markdown 正文""",
    synthesis_prompt="""用户意图：{user_intent}
输出语言：{output_language_name}

输出语言契约：
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

核心命题卡：
{claim_cards_json}

章节推进线索：
{chapter_arc_json}

深读补充：
{deep_dossiers_json}

证据检查：
{evidence_checks_json}

请按系统要求输出最终 markdown。""",
)

BOOK_ANALYSIS_SKIM_SYSTEM = BOOK_ANALYSIS_PROMPTS.skim_system
BOOK_ANALYSIS_SKIM_PROMPT = BOOK_ANALYSIS_PROMPTS.skim_prompt
BOOK_ANALYSIS_QUERY_SYSTEM = BOOK_ANALYSIS_PROMPTS.query_system
BOOK_ANALYSIS_QUERY_PROMPT = BOOK_ANALYSIS_PROMPTS.query_prompt
BOOK_ANALYSIS_SYNTHESIS_SYSTEM = BOOK_ANALYSIS_PROMPTS.synthesis_system
BOOK_ANALYSIS_SYNTHESIS_PROMPT = BOOK_ANALYSIS_PROMPTS.synthesis_prompt

