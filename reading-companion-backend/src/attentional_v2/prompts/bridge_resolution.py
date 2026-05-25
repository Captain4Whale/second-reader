"""Prompt definition for attentional_v2 bridge_resolution."""

from __future__ import annotations

from .types import PromptDefinition


BRIDGE_RESOLUTION_PROMPT_VERSION = 'attentional_v2.bridge_resolution.v5'


BRIDGE_RESOLUTION_PROMPT = PromptDefinition(
    prompt_id='attentional_v2.bridge_resolution',
    version=BRIDGE_RESOLUTION_PROMPT_VERSION,
    owner_node='bridge_resolution',
    status='active',
    purpose='Judge whether the current reading moment should bridge to earlier source material.',
    system_prompt="""You are the bridge-resolution node for a text-grounded reading mechanism.

Your job is to judge whether the current reading moment should bridge to earlier source material from a deterministic candidate set.

Rules:
- Choose a real earlier source anchor or decline to bridge.
- A real bridge must name one specific earlier target, one current quote, and the relation between them.
- When the current span explicitly says `earlier`, `前面`, `前文`, or a comparable backward cue, resolve that cue against the candidate set directly instead of answering with generic structure talk.
- Generic chapter-level callback talk does not count as a bridge.
- If a backward cue is present but no supplied candidate can honestly support it, decline plainly instead of softening the miss into a thematic summary.
- If you cannot point to a concrete earlier target from the supplied set with clear attribution, decline honestly.
- Do not invent targets outside the supplied candidate set.
- Search is rare and must stay separate from ordinary prior-knowledge use.
- Prefer no search unless interpretation is materially blocked by an identity-critical reference or obscure allusion.
- Return JSON only.""",
    user_prompt_template="""Structural frame:
{structural_frame}

Current local span:
{current_span}

Active attention:
{active_attention}

Relevant anchors:
{anchor_bank_context}

Live activations:
{activation_context}

Deterministic candidate set:
{candidate_set}

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
  "decision": "decline",
  "reason": "<brief reason>",
  "primary_bridge": {
    "target_anchor_id": "",
    "target_sentence_id": "",
    "relation_type": "echo",
    "why_now": ""
  },
  "primary_attribution": {
    "target_quote": "<short quote from the earlier source target or empty>",
    "current_quote": "<short quote from the current span that creates the bridge pressure or empty>",
    "relation_explanation": "<how the current quote turns back to the earlier target or empty>"
  },
  "supporting_bridges": [],
  "activation_updates": [],
  "state_operations": [],
  "knowledge_use_mode": "book_grounded_only",
  "search_policy_mode": "no_search",
  "search_trigger": "none",
  "search_query": ""
}""",
    required_inputs=('active_need', 'candidate_evidence', 'current_context'),
    output_contract='bridge_resolution_json_v1',
)
