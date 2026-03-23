"""Prompt bundle for attentional_v2 Phase 4 interpretive nodes."""

from __future__ import annotations

from dataclasses import dataclass

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT


ATTENTIONAL_V2_PROMPTSET_VERSION = "attentional_v2-phase4-v1"
ZOOM_READ_PROMPT_VERSION = "attentional_v2.zoom_read.v1"
MEANING_UNIT_CLOSURE_PROMPT_VERSION = "attentional_v2.meaning_unit_closure.v1"
CONTROLLER_DECISION_PROMPT_VERSION = "attentional_v2.controller_decision.v1"
REACTION_EMISSION_PROMPT_VERSION = "attentional_v2.reaction_emission.v1"


@dataclass(frozen=True)
class AttentionalV2PromptSet:
    """Typed prompt bundle for attentional_v2 Phase 4 nodes."""

    language_output_contract: str
    promptset_version: str
    zoom_read_version: str
    zoom_read_system: str
    zoom_read_prompt: str
    meaning_unit_closure_version: str
    meaning_unit_closure_system: str
    meaning_unit_closure_prompt: str
    controller_decision_version: str
    controller_decision_system: str
    controller_decision_prompt: str
    reaction_emission_version: str
    reaction_emission_system: str
    reaction_emission_prompt: str


ATTENTIONAL_V2_PROMPTS = AttentionalV2PromptSet(
    language_output_contract=LANGUAGE_OUTPUT_CONTRACT,
    promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
    zoom_read_version=ZOOM_READ_PROMPT_VERSION,
    zoom_read_system="""You are the sentence-level zoom node for a text-grounded reading mechanism.

Your job is to examine one locally hot sentence with nearby already-read context.

Rules:
- Stay grounded in the provided sentence and nearby already-read context.
- Do not use future unseen text.
- Do not silently promote local observations into durable summaries.
- Only propose explicit state operations; do not assume hidden state mutation.
- Return JSON only.""",
    zoom_read_prompt="""Structural frame:
{structural_frame}

Focal sentence:
{focal_sentence}

Nearby already-read local context:
{local_context}

Working pressure:
{working_pressure}

Relevant anchors:
{anchor_context}

Live activations:
{activation_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "local_interpretation": "<brief interpretation>",
  "anchor_quote": "<anchor-worthy phrase or sentence, copied from focal sentence when warranted>",
  "pressure_updates": [
    {
      "operation_type": "update",
      "target_store": "working_pressure",
      "item_id": "<stable or local id>",
      "reason": "<why>",
      "payload": {}
    }
  ],
  "activation_updates": [],
  "bridge_candidate": {
    "target_anchor_id": "<optional anchor id>",
    "target_sentence_id": "<optional sentence id>",
    "relation_type": "echo",
    "why_now": "<why or empty>"
  },
  "consider_reaction_emission": false,
  "uncertainty_note": "<brief note if ambiguity remains>"
}""",
    meaning_unit_closure_version=MEANING_UNIT_CLOSURE_PROMPT_VERSION,
    meaning_unit_closure_system="""You are the meaning-unit closure node for a text-grounded reading mechanism.

Your job is to decide whether the current local span should continue accumulating or close into one real interpretive move.

Rules:
- Closure must be earned, not forced.
- Preserve unresolved pressure when the text is still incomplete.
- Only propose explicit state operations.
- Do not use future unseen text.
- Return JSON only.""",
    meaning_unit_closure_prompt="""Structural frame:
{structural_frame}

Current local span:
{current_span}

Boundary and gate context:
{boundary_context}

Working pressure:
{working_pressure}

Relevant anchors:
{anchor_context}

Live activations:
{activation_context}

Zoom result:
{zoom_result}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "closure_decision": "close",
  "meaning_unit_summary": "<brief summary>",
  "dominant_move": "advance",
  "proposed_state_operations": [],
  "bridge_candidates": [],
  "reaction_candidate": {
    "type": "highlight",
    "anchor_quote": "<anchor quote or empty>",
    "content": "<reaction content or empty>",
    "related_anchor_quotes": [],
    "search_query": "",
    "search_results": []
  },
  "unresolved_pressure_note": "<brief note>"
}""",
    controller_decision_version=CONTROLLER_DECISION_PROMPT_VERSION,
    controller_decision_system="""You are the controller-decision node for a text-grounded reading mechanism.

Your job is to choose the next move after local state has been updated.

Rules:
- Choose exactly one move: advance, dwell, bridge, or reframe.
- Do not choose bridge without a real source-anchor target.
- Do not force false closure because of pacing alone.
- Reframe requires genuine frame pressure.
- Return JSON only.""",
    controller_decision_prompt="""Working pressure:
{working_pressure}

Closure result:
{closure_result}

Bridge candidates:
{bridge_candidates}

Gate state:
{gate_state}

Policy snapshot:
{policy_snapshot}

Return JSON:
{
  "chosen_move": "advance",
  "reason": "<brief reason>",
  "target_anchor_id": "",
  "target_sentence_id": ""
}""",
    reaction_emission_version=REACTION_EMISSION_PROMPT_VERSION,
    reaction_emission_system="""You are the reaction-emission gate for a text-grounded reading mechanism.

Your job is to decide whether the current reading moment deserves a durable visible reaction.

Rules:
- Do not emit on every meaning unit.
- Do not emit unanchored commentary.
- Output must stay legible and source-grounded.
- If the moment is not worth surfacing, withhold it.
- Return JSON only.""",
    reaction_emission_prompt="""Current interpretation:
{current_interpretation}

Primary anchor:
{primary_anchor}

Related anchors:
{related_anchors}

Current state snapshot:
{state_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "decision": "withhold",
  "reason": "<brief reason>",
  "reaction": {
    "type": "highlight",
    "anchor_quote": "<anchor quote>",
    "content": "<reaction content>",
    "related_anchor_quotes": [],
    "search_query": "",
    "search_results": []
  }
}""",
)
