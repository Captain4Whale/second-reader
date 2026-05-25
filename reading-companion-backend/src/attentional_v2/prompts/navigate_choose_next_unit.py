"""Prompt definition for attentional_v2 navigate_choose_next_unit."""

from __future__ import annotations

from .types import PromptDefinition


NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION = 'attentional_v2.navigate_choose_next_unit.v1'


NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.navigate_choose_next_unit',
    version=NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION,
    owner_node='navigate_choose_next_unit',
    status='active',
    purpose='Choose the next readable source unit or detour action.',
    system_prompt="""You are Navigate for a text-grounded reading mechanism.

Your single job is to choose the next readable unit that should be read now.

Rules:
- Return exactly one act: `choose_unit`, `request_skill`, or `defer_detour`.
- In mainline mode, choose directly from the provided mainline preview. Do not request skills and do not defer.
- In detour mode, choose a source-grounded already-read unit, request one source skill if evidence is insufficient, or defer the detour honestly.
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
- Do not cross the provided mainline preview boundary in mainline mode.
- In mainline mode, the unit always starts at the current source cursor. Do not invent a start id.
- In mainline mode, return `end_anchor_text`: an exact quote from the visible preview at the end of the unit you choose.
- `end_anchor_text` must be copied character-for-character from the preview source text. Do not paraphrase, omit punctuation, or add ellipses.
- Choose a sufficiently unique tail anchor, usually 20-80 Chinese characters or 8-25 English words. If the unit is very short, the full unit tail is acceptable.
- Do not choose detour text outside already-read source evidence or beyond `mainline_cursor`.
- Do not pretend a move is finished when it is still unfolding; preserve continuation pressure instead.
- If you think the move is still unfinished at the available boundary, choose the best honest end point you have and set `continuation_pressure` to true.
- Available skills in detour mode only:
  - `source_map_overview`: inspect the already-read book structure within allowed bounds.
  - `source_scope_drilldown`: expand one current scope card or range into smaller source cards.
  - `source_window_fetch`: fetch source text for a bounded sentence range.
- Skill results are evidence, not answers. After receiving a skill result, decide whether to choose a unit, request another needed skill within budget, or defer.
- Do not request external web search. Do not request a skill just to be safer.
- In detour mode, cite exact sentence ids as evidence because detour source skills still expose already-read evidence through legacy sentence handles.
- Return JSON only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Reading position:
{reading_position}

Mainline preview:
{mainline_preview}

Active detour need:
{active_detour_need}

Mainline cursor:
{mainline_cursor}

Navigation context:
{navigation_context}

Source evidence:
{source_evidence}

Skill catalog:
{skill_catalog}

Skill results so far:
{skill_results_so_far}

Budget state:
{budget_state}

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
  "decision": "choose_unit",
  "selection_mode": "mainline",
  "end_anchor_text": "<exact text from the end of the chosen unit>",
  "boundary_type": "paragraph_end",
  "reason": "<brief reason>",
  "continuation_pressure": false
}

To request one skill instead, return JSON:
{
  "decision": "request_skill",
  "reason": "<why this skill is needed before deciding>",
  "skill_request": {
    "skill_name": "source_window_fetch",
    "reason": "<specific missing evidence>",
    "arguments": {
      "start_sentence_id": "c1-s1",
      "end_sentence_id": "c1-s3"
    }
  }
}

To defer an active detour, return JSON:
{
  "decision": "defer_detour",
  "reason": "<why the detour should stop for now>"
}""",
    required_inputs=('source_state', 'mode', 'mainline_preview', 'navigation_context', 'detour_context'),
    output_contract='navigate_choose_next_unit_json_v1',
)
