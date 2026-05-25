"""Prompt definition for attentional_v2 reflective_promotion."""

from __future__ import annotations

from .types import PromptDefinition


REFLECTIVE_PROMOTION_PROMPT_VERSION = 'attentional_v2.reflective_promotion.v1'


REFLECTIVE_PROMOTION_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.reflective_promotion',
    version=REFLECTIVE_PROMOTION_PROMPT_VERSION,
    owner_node='reflective_promotion',
    status='active',
    purpose='Promote recent trace material into reflective memory candidates.',
    system_prompt="""You are the reflective-promotion node for a text-grounded reading mechanism.

Your job is to decide whether a candidate understanding has earned promotion into durable reflective summaries.

Rules:
- Promote only when the candidate is source-supported and durable enough to matter beyond the immediate local moment.
- Do not silently overwrite older reflective meaning.
- If the new item replaces an older reflective item, supersede it explicitly.
- Return JSON only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Chapter reference:
{chapter_ref}

Promotion candidate:
{candidate}

Current reflective state:
{current_reflective_state}

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
  "decision": "withhold",
  "reason": "<brief reason>",
  "target_bucket": "chapter_understandings",
  "reflective_item": {
    "item_id": "<optional stable id>",
    "statement": "<durable reflective statement>",
    "source_refs": [],
    "confidence_band": "working",
    "promoted_from": "chapter_sweep",
    "status": "active"
  },
  "supersede_bucket": "",
  "supersede_item_id": "",
  "state_operations": []
}""",
    required_inputs=('recent_trace', 'existing_frames', 'policy_snapshot'),
    output_contract='reflective_promotion_json_v1',
)
