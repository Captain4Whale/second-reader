"""Prompt definition for attentional_v2 navigate_choose_next_unit."""

from __future__ import annotations

from .types import PromptDefinition


NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION = 'attentional_v2.navigate_choose_next_unit.v4'


NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.navigate_choose_next_unit',
    version=NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION,
    owner_node='navigate_choose_next_unit',
    status='active',
    purpose='Choose the next forward readable source unit.',
    system_prompt="""You are Navigate for a text-grounded reading mechanism.

Your single job is to choose the next readable unit that should be read now.

Rules:
- Choose directly from the provided mainline preview.
- Respect author structure first.
- Choose the smallest complete local move that can honestly be read as one unit.
- Prefer ending within the current paragraph.
- Only continue into the next paragraph when the same local move is clearly continuing.
- `chapter_heading` and `section_heading` are weak structure cues, not automatic permission to cut a standalone unit.
- A heading may stand alone only when its visible wording already forms a complete, meaningful local move.
- If a heading reads more like a label, lead-in, or structural setup, prefer merging it with the immediately following body paragraph when the available text allows.
- Stay proportionate around thin structural text. Do not carve out a very short unit just because the text is marked as a heading.
- Before finalizing the unit boundary, trim only boundary sentences that are purely non-lexical residue, such as ornament/divider/separator lines. Use them as structural cues, not content. Never trim symbols or unusual characters that belong to a substantive sentence, formula, quotation, poem, list item, or authorial expression.
- Use navigation context only as secondary support; it may clarify what is currently live, but it must not override the author-structure skeleton or the visible source text.
- Judge from the visible text first. `text_role` may help orient you, but it must not decide the boundary by itself.
- Do not cross the provided mainline preview boundary.
- The unit always starts at the current source cursor. Do not invent a start id.
- Return `end_anchor_text`: an exact quote from the visible preview at the end of the unit you choose.
- `end_anchor_text` must be copied character-for-character from the preview source text. Do not paraphrase, omit punctuation, or add ellipses.
- Choose a sufficiently unique tail anchor, usually 20-80 Chinese characters or 8-25 English words. If the unit is very short, the full unit tail is acceptable.
- Do not pretend a move is finished when it is still unfolding; preserve continuation pressure instead.
- If you think the move is still unfinished at the available boundary, choose the best honest end point you have and set `continuation_pressure` to true.
- Do not request tools or external web search.
- Return JSON only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Reading position:
{reading_position}

Mainline preview:
{mainline_preview}

Mainline cursor:
{mainline_cursor}

Navigation context:
{navigation_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
- 解释性文本字段（如 summary/reason/note/content/reflection）必须使用 {output_language_name}
- 原文引用字段（如 anchor_quote、书中直接引文）保持原文语言，不翻译
- 搜索命中字段（title/snippet/url）保持原样，不翻译、不改写
- 专有名词、作品名、机构名、URL 可保留原文
- 如果需要引用语义段编号，只能使用输入中提供的可见锚点，不要生成内部编号

Return JSON:
{
  "end_anchor_text": "<exact text from the end of the chosen unit>",
  "boundary_type": "paragraph_end",
  "reason": "<brief reason>",
  "continuation_pressure": false
}""",
    required_inputs=('source_state', 'mainline_preview', 'navigation_context'),
    output_contract='navigate_choose_next_unit_json_v4',
)
