"""Prompt definition for attentional_v2 reconsolidation."""

from __future__ import annotations

from .types import PromptDefinition


RECONSOLIDATION_PROMPT_VERSION = 'attentional_v2.reconsolidation.v2'


RECONSOLIDATION_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.reconsolidation',
    version=RECONSOLIDATION_PROMPT_VERSION,
    owner_node='reconsolidation',
    status='active',
    purpose='Reconsolidate old memory with recent trace evidence.',
    system_prompt="""You are the reconsolidation node for a text-grounded reading mechanism.

Your job is to decide whether a later reading moment materially changes the meaning of an earlier persisted reaction.

Rules:
- The earlier persisted reaction is immutable.
- Only reconsolidate when the interpretive change is material rather than cosmetic.
- The later thought must stay independently anchored to the later reading moment.
- Do not search, bridge, or choose the next move here.
- Submit the final result through the required submit_reconsolidation_result tool only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Earlier persisted reaction:
{earlier_reaction}

Earlier anchor context:
{earlier_anchor_context}

Later trigger anchor:
{later_anchor}

Current understanding snapshot:
{current_understanding_snapshot}

Policy snapshot:
{policy_snapshot}

Output language contract:
- 解释性文本字段（如 summary/reason/note/content/reflection）必须使用 {output_language_name}
- 原文引用字段（如 anchor_quote、书中直接引文）保持原文语言，不翻译
- 搜索命中字段（title/snippet/url）保持原样，不翻译、不改写
- 专有名词、作品名、机构名、URL 可保留原文
- 如果需要引用语义段编号，只能使用输入中提供的可见锚点，不要生成内部编号

Submit this shape through the required final output tool:
{
  "decision": "keep_prior",
  "reason": "<brief reason>",
  "reconsolidation_record": {
    "record_id": "",
    "change_kind": "reframed",
    "what_changed": "<what materially changed>",
    "rationale": "<why the change matters>"
  },
  "later_reaction": {
    "type": "discern",
    "source_quote": "<later source quote>",
    "content": "<later anchored thought>",
    "related_source_quotes": [],
    "search_query": "",
    "search_results": []
  },
  "state_updates": []
}""",
    required_inputs=('reconsolidation_packet', 'policy_snapshot'),
    output_contract='reconsolidation_json_v1',
)
