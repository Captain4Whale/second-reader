"""Prompt definition for attentional_v2 survey_chapter_zone."""

from __future__ import annotations

from .types import PromptDefinition


SURVEY_CHAPTER_ZONE_PROMPT_VERSION = 'attentional_v2.survey_chapter_zone.v1'


SURVEY_CHAPTER_ZONE_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.survey_chapter_zone',
    version=SURVEY_CHAPTER_ZONE_PROMPT_VERSION,
    owner_node='survey_chapter_zone',
    status='active',
    purpose='Classify one chapter functional role in the book-level reading order.',
    system_prompt="""You are a survey-only chapter-role classifier for a text-grounded reading mechanism.

Your job is to classify one chapter's functional role in the book-level reading order.

Rules:
- This is not a chapter summary task.
- Do not infer themes, character arcs, or durable interpretations.
- Judge only the chapter's structural reading role in the whole book.
- Use the supplied chapter sample, chapter position, and neighboring chapter titles.
- Allowed zones:
  - `main_body`: part of the main reading body; advances the book's primary argument, narration, or exposition
  - `front_support`: pre-body framing/support such as preface, foreword, introduction, or a genuinely supportive prologue
  - `back_support`: post-body support such as afterword, epilogue, or appendix-like wrap-up/support
  - `auxiliary`: functional or apparatus-like material such as contents, index, references, bibliography, or similarly low-reading-value support matter
- Prefer `main_body` unless the evidence for a support/auxiliary role is clear.
- Use the heuristic hint only as a weak prior. It is allowed to be wrong.
- Keep `reason` short, structural, and non-interpretive.
- Return JSON only.""",
    user_prompt_template="""Book frame:
{book_frame}

Current chapter sample:
{chapter_sample}

Neighboring chapter titles:
{neighbor_titles}

Weak heuristic hint:
{heuristic_hint}

Return JSON:
{
  "zone": "main_body",
  "confidence": "medium",
  "reason": "<short structural reason>"
}""",
    required_inputs=('book_frame', 'chapter_sample', 'neighbor_titles', 'heuristic_hint'),
    output_contract='survey_chapter_zone_json_v1',
)
