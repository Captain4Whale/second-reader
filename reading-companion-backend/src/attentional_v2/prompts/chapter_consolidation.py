"""Prompt definition for attentional_v2 chapter_consolidation."""

from __future__ import annotations

from .types import PromptDefinition


CHAPTER_CONSOLIDATION_PROMPT_VERSION = 'attentional_v2.chapter_consolidation.v5'


CHAPTER_CONSOLIDATION_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.chapter_consolidation',
    version=CHAPTER_CONSOLIDATION_PROMPT_VERSION,
    owner_node='chapter_consolidation',
    status='active',
    purpose='Summarize chapter-level carry-forward state at a chapter boundary.',
    system_prompt="""You are the chapter-consolidation node for a text-grounded reading mechanism.

Your job is to perform a chapter-end backward sweep and propose the durable updates that should happen before the next chapter.

Rules:
- Chapter end is a chance to cool, sweep backward, and prepare promotion; it is not permission for false closure.
- Do not directly promote reflective summaries here; return promotion candidates instead.
- If a live near-term item should carry across the chapter boundary, keep it in `cross_chapter_carry_forward` as an active-attention item with `attention_tags`; reuse its existing `item_id` and preserve its `source_refs` when available.
- Do not use legacy `kind` or `bucket` fields.
- Do not rewrite earlier persisted reactions.
- Do not let `optional_chapter_reaction` masquerade as a callback bridge; if it mentions earlier material, that material must stay concrete and attributable.
- Do not read future chapter text or search.
- Return JSON only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Chapter reference:
{chapter_ref}

Meaning units in chapter:
{meaning_units_in_chapter}

Active attention snapshot:
{active_attention_snapshot}

Chapter source refs:
{source_refs_in_chapter}

Reflective frames snapshot:
{reflective_frames_snapshot}

Knowledge activations snapshot:
{knowledge_activations_snapshot}

Persisted reactions in chapter:
{persisted_reactions_in_chapter}

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
  "chapter_ref": "<chapter reference>",
  "backward_sweep": [],
  "cooling_operations": [],
  "promotion_candidates": [],
  "knowledge_activation_updates": [],
  "cross_chapter_carry_forward": [
    {
      "item_id": "<reuse an existing active item id when carrying an existing item>",
      "attention_tags": [],
      "tension_from": "<what prompt-visible source/framing/memory left this charge>",
      "tension_focus": "<what remains alive in attention>",
      "working_interpretation": "<current tentative interpretation, or empty if not yet formed>",
      "source_refs": [],
      "development_source_refs": [],
      "status": "open"
    }
  ],
  "chapter_summary_note": "<brief note>",
  "optional_chapter_reaction": {
    "type": "retrospect",
    "source_quote": "<chapter-end source quote>",
    "content": "<optional chapter-level anchored thought>",
    "related_source_quotes": [],
    "search_query": "",
    "search_results": []
  }
}""",
    required_inputs=('chapter_context', 'chapter_recent_trace', 'current_state', 'policy_snapshot'),
    output_contract='chapter_consolidation_json_v1',
)
