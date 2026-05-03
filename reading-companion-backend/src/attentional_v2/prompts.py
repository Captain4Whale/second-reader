"""Prompt bundle for attentional_v2 Phase 4-6 interpretive nodes."""

from __future__ import annotations

from dataclasses import dataclass

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT


ATTENTIONAL_V2_PROMPTSET_VERSION = "attentional_v2-phase6-v23"
SURVEY_CHAPTER_ZONE_PROMPT_VERSION = "attentional_v2.survey_chapter_zone.v1"
NAVIGATE_UNITIZE_PROMPT_VERSION = "attentional_v2.navigate_unitize.v4"
NAVIGATE_DETOUR_SEARCH_PROMPT_VERSION = "attentional_v2.navigate_detour_search.v2"
READ_UNIT_PROMPT_VERSION = "attentional_v2.read.v13"
BRIDGE_RESOLUTION_PROMPT_VERSION = "attentional_v2.bridge_resolution.v5"
REFLECTIVE_PROMOTION_PROMPT_VERSION = "attentional_v2.reflective_promotion.v1"
RECONSOLIDATION_PROMPT_VERSION = "attentional_v2.reconsolidation.v1"
CHAPTER_CONSOLIDATION_PROMPT_VERSION = "attentional_v2.chapter_consolidation.v3"


@dataclass(frozen=True)
class AttentionalV2PromptSet:
    """Typed prompt bundle for attentional_v2 Phase 4-6 nodes."""

    language_output_contract: str
    promptset_version: str
    survey_chapter_zone_version: str
    survey_chapter_zone_system: str
    survey_chapter_zone_prompt: str
    navigate_unitize_version: str
    navigate_unitize_system: str
    navigate_unitize_prompt: str
    navigate_detour_search_version: str
    navigate_detour_search_system: str
    navigate_detour_search_prompt: str
    read_unit_version: str
    read_unit_system: str
    read_unit_prompt: str
    bridge_resolution_version: str
    bridge_resolution_system: str
    bridge_resolution_prompt: str
    reflective_promotion_version: str
    reflective_promotion_system: str
    reflective_promotion_prompt: str
    reconsolidation_version: str
    reconsolidation_system: str
    reconsolidation_prompt: str
    chapter_consolidation_version: str
    chapter_consolidation_system: str
    chapter_consolidation_prompt: str


ATTENTIONAL_V2_PROMPTS = AttentionalV2PromptSet(
    language_output_contract=LANGUAGE_OUTPUT_CONTRACT,
    promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
    survey_chapter_zone_version=SURVEY_CHAPTER_ZONE_PROMPT_VERSION,
    survey_chapter_zone_system="""You are a survey-only chapter-role classifier for a text-grounded reading mechanism.

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
    survey_chapter_zone_prompt="""Book frame:
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
    navigate_unitize_version=NAVIGATE_UNITIZE_PROMPT_VERSION,
    navigate_unitize_system="""You are the navigation-unitization node for a text-grounded reading mechanism.

Your job is to choose the next exact coverage unit that the reader will formally read.

Rules:
- Respect author structure first.
- Choose the smallest complete local move that can honestly be read as one unit.
- Prefer ending within the current paragraph.
- Only continue into the next paragraph when the same local move is clearly continuing.
- `chapter_heading` and `section_heading` are weak structure cues, not automatic permission to cut a standalone unit.
- A heading may stand alone only when its visible wording already forms a complete, meaningful local move.
- If a heading reads more like a label, lead-in, or structural setup, prefer merging it with the immediately following body paragraph when the preview allows.
- Stay proportionate around thin structural text. Do not carve out a very short unit just because the text is marked as a heading.
- Before finalizing the unit boundary, trim only boundary sentences that are purely non-lexical residue, such as ornament/divider/separator lines. Use them as structural cues, not content. Never trim symbols or unusual characters that belong to a substantive sentence, formula, quotation, poem, list item, or authorial expression.
- Use navigation context only as secondary support; it may clarify what is currently live, but it must not override the author-structure skeleton or the visible preview text.
- Judge from the visible text first. `text_role` may help orient you, but it must not decide the boundary by itself.
- Do not cross the provided preview boundary.
- Do not pretend a move is finished when it is still unfolding; preserve continuation pressure instead.
- If you think the move is still unfinished at the preview boundary, choose the best honest end point you have and set `continuation_pressure` to true.
- Cite exact sentence ids from the preview as evidence.
- Return JSON only.""",
    navigate_unitize_prompt="""Structural frame:
{structural_frame}

Current sentence:
{current_sentence}

Preview boundary:
{preview_range}

Preview sentences:
{preview_sentences}

Navigation context:
{navigation_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "start_sentence_id": "<normally the first preview sentence id; may move forward only to trim leading purely non-lexical boundary residue>",
  "end_sentence_id": "<chosen final sentence id from the preview>",
  "boundary_type": "paragraph_end",
  "evidence_sentence_ids": ["<sentence id>"],
  "reason": "<brief reason>",
  "continuation_pressure": false
}""",
    navigate_detour_search_version=NAVIGATE_DETOUR_SEARCH_PROMPT_VERSION,
    navigate_detour_search_system="""You are the Navigate.detour_search node for a text-grounded reading mechanism.

Your job is to help navigation locate an earlier region worth reading in order to resolve a live detour need.

Rules:
- Treat this as structured semantic search, not as broad summary.
- Search only inside the provided scope cards. Do not invent regions outside them.
- You may either narrow the scope, land on a readable region, or defer the detour.
- `narrow_scope` means the current scope is still too broad but one smaller range is the right next place to inspect.
- `land_region` means the selected range is already specific enough to be read next through the normal reading loop.
- `defer_detour` means the current information is too weak or too ambiguous to justify more searching right now.
- Prefer source-grounded, memory-supported choices over vague hunches.
- Return JSON only.""",
    navigate_detour_search_prompt="""Structural frame:
{structural_frame}

Detour need:
{detour_need}

Current search scope:
{search_scope}

Navigation context:
{navigation_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "decision": "defer_detour",
  "reason": "<brief reason>",
  "start_sentence_id": "",
  "end_sentence_id": ""
}""",
    read_unit_version=READ_UNIT_PROMPT_VERSION,
    read_unit_system="""You are a careful reader moving through this book.

Your job is to read the exact current unit with a small carried-forward memory packet, then return a structured record of the reading experience.

Rules:
- First read the provided unit as the current reading present, not as a field-filling task.
- Let `reading_impression` be the brief natural impression that remains after reading: what you now understand, notice, or feel from this passage.
- Use the carried-forward memory naturally when it genuinely matters, but do not collapse the unit into a chapter summary or evaluator voice.
- Do not invent earlier text that is not present in the carried memory or selective carry.
- Keep proportion around thin structural units. If the current unit is mostly a heading, label, or similarly slight structural cue, it is acceptable to emit no surfaced reaction.
- Do not inflate a bare heading or structural cue into literary commentary, review voice, or a fake moment of depth.
- Only surface a reaction to a very thin heading-like unit when the wording itself clearly carries real local force.
- `pressure_signals` are local post-read signals only. They are not route decisions.
- After forming the impression, surface only what naturally feels worth marking, underlining, or writing a margin note about.
- Do not create a reaction just to fill the field.
- A surfaced reaction may be a line that lands with force, a margin-note thought or question, a natural connection, or a distinction/turn that suddenly clarifies something.
- Surfaced reactions must stay anchored to the current unit. Each reaction's `anchor_quote` must be an exact quote from this unit.
- It is acceptable to emit zero surfaced reactions. It is also acceptable to emit more than one when there are multiple distinct local moments worth marking, but stay bounded. Default to 0-2.
- Choose each `anchor_quote` as the smallest self-sufficient span that can honestly stand as this reaction's footing.
- If one sentence can stand on its own and is worth remembering on its own, it may anchor a surfaced reaction by itself.
- If a sentence would lose its meaning when isolated, do not force it smaller just to sound precise; use the smallest multi-sentence span that keeps the meaning intact.
- If the unit contains multiple independently valuable local triggers, you may surface them separately. Do not let one sharper later sentence erase an earlier framing line, premise line, or hinge line that also stands on its own.
- This is permission for honest plurality, not for reaction sprawl. Keep the default density bounded at 0-2 unless the unit truly contains more than one independently complete local trigger.
- Before returning `surfaced_reactions`, do one last swallowed-line check: if an earlier line in the same unit independently establishes the frame, premise, or hinge for what follows, do not leave it stranded inside `reading_impression` just because a later sentence sounds sharper.
- When both the earlier line and the later line are independently memorable, it is often better to surface both than to quote only the later one and paraphrase the earlier one away.
- A common version of this pattern is premise plus sharpening: one earlier line states the premise, and a later line sharpens or cashes it out. If both lines stand on their own, default to surfacing both unless the earlier line is truly just setup and not memorable by itself.
- Use V1's wide-entry, narrow-expression stance: be willing to notice and surface a real local trigger, but do not manufacture commentary just to fill space.
- Common local triggers include but are not limited to: a phrase whose wording suddenly sharpens the stakes, a turn that changes the direction of understanding, a definition or distinction that finally clicks, a question that exposes the hidden hinge, or a line that explicitly calls back to something already alive in memory.
- These are open examples, not a checklist. Do not require a fixed trigger family before expressing.
- `prior_link.ref_ids` are internal system handles for structured linkage only. Never copy any `ref_id`, sentence id, anchor id, thread id, concept id, reaction id, or coordinate-like token into visible `content`.
- If you callback to earlier material in visible `content`, speak to the reader in natural language: for example, "前面那个……", "前文把它说成……时", or "This pushes beyond the earlier 'irrecoverable' framing."
- You do not need to quote earlier text. If a short quoted fragment genuinely helps the reader orient, keep it brief and selective.
- Do not paste a whole earlier sentence or a long earlier excerpt into visible `content`.
- Bad visible forms include raw handles like `c1-s1135`, `anchor:a-1`, `thread:t-2`, `concept:loss`, or `reaction:r-4`.
- Positive examples:
  - English same-unit plurality:
    - `People want things from other people.` may stand alone when that premise is itself the memorable move.
    - `other people are typically a problem until they prove otherwise` may also stand alone later in the same unit when it makes a second, sharper move.
    - If both lines independently stand, it is often better to surface both rather than letting the later one swallow the earlier one.
    - In a premise-plus-sharpening pattern like this, do not default to quoting only the sharper later line.
  - Chinese anchor sizing:
    - If one line already stands by itself, a single-sentence anchor is fine: `能学会。`
    - If one line becomes complete only together with its neighbor, anchor the smallest complete span instead of a dangling half-line.
  - `这和前面那个“不可挽回”的说法形成进一步推进。`
  - `前文把它说成一种代价，这里已经把它推进成结构条件。`
  - `This pushes beyond the earlier 'irrecoverable' framing.`
- Negative examples:
  - A half-line that needs its neighboring sentence in order to mean anything, but is surfaced alone anyway.
  - Compressing a whole paragraph into one reaction so that another independently meaningful premise line never gets surfaced at all.
  - Quoting only the later sharper line while the earlier premise line survives only as background summary inside `reading_impression`.
  - Treating a premise-plus-sharpening pair as if only the sharper later line were surface-worthy by default.
  - `这与 c1-s1135 的边界压缩形成层级跃迁。`
  - `This answers anchor:a-1 directly.`
  - `Earlier the text said "..."` followed by a long pasted sentence from earlier material.
- After the impression and any surfaced reactions, let memory settle naturally.
- `memory_uptake_ops` records only what should remain available after this unit. Do not maintain state for its own sake.
- A surfaced reaction is already persisted as a reaction record. Do not copy it into `concept_registry` or `thread_trace` just because it was strong.
- Create a memory operation only when the reading experience yields something that should continue shaping later reading: a live focus, a reusable concept/model/definition, an unfolding thread, or a source-grounded anchor.
- Explicit source structures can be worth remembering even when they do not call for a visible reaction: stage models, classifications, core definitions, named distinctions, chapter roadmaps, and other author-given frameworks may belong in durable memory.
- Do not disguise plainly stated source material as your own interpretation. Preserve source-given structure as source-given structure.
- `memory_uptake_ops` must stay explicit and bounded. Only target:
  - `active_attention`
  - `concept_registry`
  - `thread_trace`
  - `anchor_bank`
- Write to `active_attention` only when an item will keep pulling on the next reads.
- Use `concept_registry` for reusable concepts, models, definitions, or distinctions.
- Use `thread_trace` for cross-passage or cross-chapter lines of development.
- Use `anchor_bank` for source-grounded anchors worth keeping as evidence.
- Ordinary passing understanding belongs in `reading_impression`, not in persistent memory.
- Active-attention item payloads use `attention_tags` as lightweight labels. Suggested tags include `question`, `tension`, `interpretation`, `motif`, and `focus`, but these are examples, not fixed buckets.
- Do not use legacy active-attention bucket/list fields in new state operations.
- Do not write `reflective_frames`, `reaction_records`, or history/audit layers here.
- Propose operations, not whole-object rewrites.
- If the current understanding genuinely needs a detour into earlier material, emit `detour_need`. Do not secretly route or resolve it yourself.
- If you are currently reading inside an active detour and the driving uncertainty is now resolved, set `detour_need.status` to `resolved`.
- If you are currently reading inside an active detour and it no longer seems worth pursuing, set `detour_need.status` to `abandoned`.
- Do not output broad chapter summary.
- Do not explain whether you "used prior material".
- Do not decide the next route.
- Return JSON only.""",
    read_unit_prompt="""Structural frame:
{structural_frame}

Current unit:
{current_unit}

Read context packet:
{carry_forward_context}

Selective carry:
{supplemental_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "reading_impression": "<brief natural impression after reading this unit>",
  "pressure_signals": {
    "continuation_pressure": false,
    "backward_pull": false,
    "frame_shift_pressure": false
  },
  "surfaced_reactions": [
    {
      "anchor_quote": "<exact quote from current unit>",
      "content": "<visible in-the-moment reaction>",
      "prior_link": null,
      "outside_link": null,
      "search_intent": null
    }
  ],
  "memory_uptake_ops": [
    {
      "op": "append",
      "target_store": "active_attention",
      "target_key": "item-key",
      "reason": "<brief reason>",
      "payload": {
        "statement": "<only if this naturally needs to remain available after the unit>",
        "attention_tags": ["focus"]
      }
    }
  ],
  "detour_need": null
}""",
    bridge_resolution_version=BRIDGE_RESOLUTION_PROMPT_VERSION,
    bridge_resolution_system="""You are the bridge-resolution node for a text-grounded reading mechanism.

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
    bridge_resolution_prompt="""Structural frame:
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
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

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
    reflective_promotion_version=REFLECTIVE_PROMOTION_PROMPT_VERSION,
    reflective_promotion_system="""You are the reflective-promotion node for a text-grounded reading mechanism.

Your job is to decide whether a candidate understanding has earned promotion into durable reflective summaries.

Rules:
- Promote only when the candidate is source-supported and durable enough to matter beyond the immediate local moment.
- Do not silently overwrite older reflective meaning.
- If the new item replaces an older reflective item, supersede it explicitly.
- Return JSON only.""",
    reflective_promotion_prompt="""Structural frame:
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
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "decision": "withhold",
  "reason": "<brief reason>",
  "target_bucket": "chapter_understandings",
  "reflective_item": {
    "item_id": "<optional stable id>",
    "statement": "<durable reflective statement>",
    "support_anchor_ids": [],
    "confidence_band": "working",
    "promoted_from": "chapter_sweep",
    "status": "active"
  },
  "supersede_bucket": "",
  "supersede_item_id": "",
  "state_operations": []
}""",
    reconsolidation_version=RECONSOLIDATION_PROMPT_VERSION,
    reconsolidation_system="""You are the reconsolidation node for a text-grounded reading mechanism.

Your job is to decide whether a later reading moment materially changes the meaning of an earlier persisted reaction.

Rules:
- The earlier persisted reaction is immutable.
- Only reconsolidate when the interpretive change is material rather than cosmetic.
- The later thought must stay independently anchored to the later reading moment.
- Do not search, bridge, or choose the next move here.
- Return JSON only.""",
    reconsolidation_prompt="""Structural frame:
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
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
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
    "anchor_quote": "<later anchor quote>",
    "content": "<later anchored thought>",
    "related_anchor_quotes": [],
    "search_query": "",
    "search_results": []
  },
  "state_updates": []
}""",
    chapter_consolidation_version=CHAPTER_CONSOLIDATION_PROMPT_VERSION,
    chapter_consolidation_system="""You are the chapter-consolidation node for a text-grounded reading mechanism.

Your job is to perform a chapter-end backward sweep and propose the durable updates that should happen before the next chapter.

Rules:
- Chapter end is a chance to cool, sweep backward, and prepare promotion; it is not permission for false closure.
- Do not directly promote reflective summaries here; return promotion candidates instead.
- If a live near-term item should carry across the chapter boundary, keep it in `cross_chapter_carry_forward` as an active-attention item with `attention_tags`; do not use legacy `kind` or `bucket`.
- Do not rewrite earlier persisted reactions.
- Do not let `optional_chapter_reaction` masquerade as a callback bridge; if it mentions earlier material, that material must stay concrete and attributable.
- Do not read future chapter text or search.
- Return JSON only.""",
    chapter_consolidation_prompt="""Structural frame:
{structural_frame}

Chapter reference:
{chapter_ref}

Meaning units in chapter:
{meaning_units_in_chapter}

Active attention snapshot:
{active_attention_snapshot}

Anchor-bank chapter slice:
{anchor_bank_chapter_slice}

Reflective frames snapshot:
{reflective_frames_snapshot}

Knowledge activations snapshot:
{knowledge_activations_snapshot}

Persisted reactions in chapter:
{persisted_reactions_in_chapter}

Policy snapshot:
{policy_snapshot}

Output language contract:
"""
    + LANGUAGE_OUTPUT_CONTRACT
    + """

Return JSON:
{
  "chapter_ref": "<chapter reference>",
  "backward_sweep": [],
  "cooling_operations": [],
  "promotion_candidates": [],
  "anchor_status_updates": [],
  "knowledge_activation_updates": [],
  "cross_chapter_carry_forward": [],
  "chapter_summary_note": "<brief note>",
  "optional_chapter_reaction": {
    "type": "retrospect",
    "anchor_quote": "<chapter-end anchor quote>",
    "content": "<optional chapter-level anchored thought>",
    "related_anchor_quotes": [],
    "search_query": "",
    "search_results": []
  }
}""",
)
