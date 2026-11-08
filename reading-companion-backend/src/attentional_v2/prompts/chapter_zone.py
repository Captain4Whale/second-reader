"""Prompt definition for attentional_v2 chapter_zone."""

from __future__ import annotations

from src.prompts.releases import prompt_text

from .types import PromptDefinition


CHAPTER_ZONE_PROMPT_VERSION = 'attentional_v2.chapter_zone.v2'


CHAPTER_ZONE_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.chapter_zone',
    version=CHAPTER_ZONE_PROMPT_VERSION,
    owner_node='chapter_zone',
    status='active',
    purpose='Classify one chapter functional role in the book-level reading order.',
    system_prompt=prompt_text('chapter_zone', CHAPTER_ZONE_PROMPT_VERSION.rsplit('.', 1)[1], 'system_prompt'),
    user_prompt_template=prompt_text('chapter_zone', CHAPTER_ZONE_PROMPT_VERSION.rsplit('.', 1)[1], 'user_prompt_template'),
    required_inputs=('book_frame', 'chapter_sample', 'neighbor_titles', 'heuristic_hint'),
    output_contract='chapter_zone_json_v1',
)
