"""Prompt definition for attentional_v2 digest."""

from __future__ import annotations

from collections.abc import Mapping
import json

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT

from .assembly import (
    PromptFragment,
    PromptFragmentRegistry,
    PromptTemplateNode,
    render_prompt_template_xml,
)
from .assembler import PromptAssembler, PromptAssemblyResult, PromptAssemblySpec
from .reader_role import READER_ROLE_FRAGMENT
from .types import PromptDefinition


DIGEST_PROMPT_VERSION = "attentional_v2.digest.v1"
DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.digest.xml.v1"
DIGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v45"
DIGEST_XML_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Digest prompt in the user message. Return JSON only."


# These fragments are a lossless management split of the Digest-specific system prompt.
# Do not edit fragment boundaries unless the reconstructed system prompt remains intentional.
DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS = (
    READER_ROLE_FRAGMENT,
    PromptFragment(
        fragment_id='digest.instruction',
        text="""Your job is to read the exact current unit with a small carried-forward memory packet, then return a structured record of the reading experience.

Rules:
- First read the provided unit as the current reading present, not as a field-filling task.""",
    ),
    PromptFragment(
        fragment_id='digest.reading_impression_policy',
        text="""- Let `reading_impression` be the brief natural impression that remains after reading: what you now understand, notice, or feel from this passage.
- Use the carried-forward memory naturally when it genuinely matters, but do not collapse the unit into a chapter summary or evaluator voice.
- Do not invent earlier text that is not present in the carried memory or selective carry.""",
    ),
    PromptFragment(
        fragment_id='digest.surfaced_reaction_policy',
        text="""- Keep proportion around thin structural units. If the current unit is mostly a heading, label, or similarly slight structural cue, it is acceptable to emit no surfaced reaction.
- Do not inflate a bare heading or structural cue into literary commentary, review voice, or a fake moment of depth.
- Only surface a reaction to a very thin heading-like unit when the wording itself clearly carries real local force.
- After forming the impression, surface only what naturally feels worth marking, underlining, or writing a margin note about.
- Do not create a reaction just to fill the field.
- A surfaced reaction may be a line that lands with force, a margin-note thought or question, a natural connection, or a distinction/turn that suddenly clarifies something.
- Surfaced reactions must stay anchored to the current unit. Each reaction's `source_quote` must be an exact quote from this unit.
- It is acceptable to emit zero surfaced reactions. It is also acceptable to emit more than one when there are multiple distinct local moments worth marking, but stay bounded. Default to 0-2.
- Choose each `source_quote` as the smallest self-sufficient span that can honestly stand as this reaction's footing.
- If one sentence can stand on its own and is worth remembering on its own, it may anchor a surfaced reaction by itself.
- If a sentence would lose its meaning when isolated, do not force it smaller just to sound precise; use the smallest multi-sentence span that keeps the meaning intact.
- If the unit contains multiple independently valuable local triggers, you may surface them separately. Do not let one sharper later sentence erase an earlier framing line, premise line, or hinge line that also stands on its own.
- This is permission for honest plurality, not for reaction sprawl. Keep the default density bounded at 0-2 unless the unit truly contains more than one independently complete local trigger.
- Before returning `surfaced_reactions`, do one last swallowed-line check: if an earlier line in the same unit independently establishes the frame, premise, or hinge for what follows, do not leave it stranded inside `reading_impression` just because a later sentence sounds sharper.
- When both the earlier line and the later line are independently memorable, it is often better to surface both than to quote only the later one and paraphrase the earlier one away.
- A common version of this pattern is premise plus sharpening: one earlier line states the premise, and a later line sharpens or cashes it out. If both lines stand on their own, default to surfacing both unless the earlier line is truly just setup and not memorable by itself.
- Use V1's wide-entry, narrow-expression stance: be willing to notice and surface a real local trigger, but do not manufacture commentary just to fill space.
- Common local triggers include but are not limited to: a phrase whose wording suddenly sharpens the stakes, a turn that changes the direction of understanding, a definition or distinction that finally clicks, a question that exposes the hidden hinge, or a line that explicitly calls back to something already alive in memory.
- These are open examples, not a checklist. Do not require a fixed trigger family before expressing.""",
    ),
    PromptFragment(
        fragment_id='digest.reaction_anchor_and_callback_policy',
        text="""- `prior_link.ref_ids` are internal system handles for structured linkage only. Never copy any `ref_id`, sentence id, source span id, thread id, concept id, reaction id, or coordinate-like token into visible `content`.
- If you callback to earlier material in visible `content`, speak to the reader in natural language: for example, "前面那个……", "前文把它说成……时", or "This pushes beyond the earlier 'irrecoverable' framing."
- You do not need to quote earlier text. If a short quoted fragment genuinely helps the reader orient, keep it brief and selective.
- Do not paste a whole earlier sentence or a long earlier excerpt into visible `content`.
- Bad visible forms include raw handles like `c1-s1135`, `source:src:c1:p1@0-p1@12`, `thread:t-2`, `concept:loss`, or `reaction:r-4`.
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
  - `This answers source:src:c1:p1@0-p1@12 directly.`
  - `Earlier the text said "..."` followed by a long pasted sentence from earlier material.""",
    ),
    PromptFragment(
        fragment_id='digest.memory_general_policy',
        text="""- After the impression and any surfaced reactions, maintain memory deliberately.
- `memory_uptake_ops` records only what should remain available after this unit. Do not maintain state for its own sake.
- A surfaced reaction is already persisted as a reaction record. Do not copy it into `concept_registry` or `thread_trace` just because it was strong.""",
    ),
    PromptFragment(
        fragment_id='digest.recent_reading_memory_policy',
        text="""- First maintain Recent Reading Memory: after reading this unit, write one Recent Reading Memory entry for your future self unless the unit is empty or purely structural.
- Assume the exact source text of this unit may not be shown again in the next Digest step. Record what you now understand from this unit that should remain available for coherent continued reading.
- Write Recent Reading Memory as source-established content first, not essay-like analysis.
- First record what the source directly establishes for future reading: who or what appears, what happened, what the author claims, what distinction / stage / example is introduced, what condition or consequence is stated, or what writing position / evidence boundary / reader-orientation is declared.
- Add interpretation only when it is needed to preserve source-established meaning. Do not start from your theory of the passage.
- Record what the source establishes, shows, says, names, contrasts, changes, withholds, or explicitly frames.
- Compress meaning, not wording. Do not copy the whole passage. Do not write a visible reaction. Do not predict whether something will matter later. Do not import outside knowledge.
- Keep the memory complete enough for future reading; do not make it artificially short.
- Before writing Recent Reading Memory, orient yourself with the prompt-visible reading context. Treat the provided context as what you already carry from the reading so far.
- Use that context to understand the current unit as part of the unfolding book.
- But write the memory for the current unit itself: record what this unit newly establishes, develops, specifies, contrasts, changes, or makes memorable.
- Do not turn the entry into a recap of the context.
- Do not force every entry to mention prior memory or framing.
- Only mention a connection to prior context when it helps make the current unit's meaning clear.
- The entry should answer: "What should my future self remember from this unit, given the reading context I already carried into it?" not "What can I say again about the prior context?"
- Write Recent Reading Memory so your future self can understand it from the memory packet, not from the vanished source unit.
- Be context-resolvable, not standalone exhaustive.
- Write Recent Reading Memory as natural memory sentences or a short paragraph, not as a heading followed by explanation.
- Do not default to `<label>: <explanation>` or `<abstract name>: <explanation>` style.
- Use a colon only when the source itself names a term, stage, framework, or quoted source term such as `Transfer` / `Selection`.
- If a person, concept, thread, or situation is already stable in the prompt-visible concept/thread context, use its stable name and only record what changed or was newly learned.
- If something is newly introduced in this unit, name or describe it clearly enough for a later Digest step to understand.
- Avoid bare pronouns or vague references such as "he", "this", "that", or "the above situation" unless the referent is explicit in the same entry or stable in concept/thread context.
- Capture new events, claims, explanations, facts, changes in a person/situation/argument/relationship/emotional state, definitions, distinctions, causal links, stages, examples, source-explicit tensions, images, source-explicit unresolved lines, author stance, evidence boundaries, reader-orientation notes, or updates to earlier context.
- Do not over-explain the hidden mechanism behind the passage.
- Do not turn a concrete scene into an abstract theory unless the source itself names or strongly frames it that way.
- Prefer source-facing phrasing such as "the text says", "the text shows", "the text names", or "the text contrasts" when useful.
- Avoid unsupported analytic upgrades such as "the essence is", "this proves", "this is an operation mechanism", or "the passage actively trains" unless the unit explicitly supports that wording.
- Avoid abstract upgrades such as "psychological pressure weapon", "inner subject process", "systemic refusal", or "moral judgment is abandoned" unless the source itself directly establishes that abstraction. Prefer the concrete source memory first: for example, "the guards identify prisoners by number and never ask their names" before any theory about dehumanization.
- Author-facing or method-facing units still count as meaningful content. If the unit declares the author's witness position, evidence boundary, writing method, intended reader, or what the book will / will not explain, remember that as source-established content instead of treating it as empty structure.
- If the unit mostly elaborates something already known, write the memory as the current best understanding rather than duplicating fragments.
- Usually write one Recent Reading Memory entry for this unit. Split into multiple entries only when the unit contains distinct meanings that a future reader would naturally remember and use separately. Do not split by sentence or paragraph, and do not create many small note fragments.
- Recent Reading Memory entries are grounded in the current source unit as a whole. You do not need exact source quotes for them; the runner owns `source_unit_span_id`.
- Recent Reading Memory append operations do not need an operation-level `reason`. The `memory_text` is the content to keep; do not spend attention justifying why you wrote it.""",
    ),
    PromptFragment(
        fragment_id='digest.durable_memory_policy',
        text="""- Create other memory operations only when the reading experience yields something that should continue shaping later reading: an open tension, a reusable concept/model/definition, or an unfolding thread.
- Explicit source structures can be worth remembering even when they do not call for a visible reaction: stage models, classifications, core definitions, source-named distinctions, chapter roadmaps, and other author-given frameworks may belong in durable memory.
- Do not disguise plainly stated source material as your own interpretation. Preserve source-given structure as source-given structure.
- `memory_uptake_ops` must stay explicit and bounded. Only target:
  - `recent_reading_memory`
  - `active_attention`
  - `concept_registry`
  - `thread_trace`
- Do not target `concept_digest`, `thread_digest`, `active_focus_digest`, or report/projection fields. Digests are prompt projections, not writable memory stores.""",
    ),
    PromptFragment(
        fragment_id='digest.active_tension_policy',
        text="""- `active_attention` stores ActiveTension: points that still hang in the reader's attention after a unit, not recent memory and not a summary cache.
- After reading this unit, pause as a reader.
- Notice what still holds your attention after the unit is over.
- It may be a question, suspense, an unusual character, a striking image, a beautiful scene, a strange event, an emotional pressure, a recurring pattern, or a claim that has not yet settled.
- Do not require yourself to know whether it will matter later.
- You only need to judge whether it still feels alive in your reading attention right now.
- Prompt-visible context includes the current source unit, book or chapter framing shown in this prompt, and existing memory state shown in the Digest context packet.
- Do not import outside knowledge about the book, author, or later chapters unless that information is present in this prompt.
- Record an ActiveTension when something remains alive in attention after the unit: it is not fully digested as a stable fact, summary, or concept yet.
- Do not record every important statement.
- Do not record ordinary facts just because they are useful.
- Use ActiveTension for points that still have readerly charge: curiosity, beauty, unease, surprise, suspense, unresolved meaning, emotional force, or a vivid image/person/event that lingers.
- An ActiveTension does not have to be phrased as a question, does not have to wait for an answer, and does not require you to predict whether it will shape later reading.
- Good ActiveTensions feel like something a reader naturally carries after the visible reading context:
  - narrative suspense: a bomb is placed on the table, so the reader carries that possible explosion as live tension.
  - argument promise: the author poses a problem or claim, so the reader carries how it may be developed.
  - image or beauty: a landscape or image is unusually vivid and keeps resonating even if it does not ask a question.
  - character or strange event: a person or event feels distinctive, unsettling, or memorable enough to linger.
  - `活出生命的意义`: visible title/framing plus current text about prisoner adaptation, emotional numbness, and meaning can create a reading pull; keep the basis honest in `tension_from`.
- Do not create an ActiveTension merely because the passage is important. Importance alone belongs in `reading_impression`, `concept_registry`, or `thread_trace`; ActiveTension requires readerly charge.
- ActiveTension create payloads must use `tension_from`, `tension_focus`, and `working_interpretation`; do not create new `statement`-only or question-only active-attention items.
- `tension_from` says what prompt-visible source, framing, or memory left this charge.
- `tension_focus` says what remains alive in attention; it may be a question, tension, image, beauty, character trait, unusual event, emotional pressure, pattern, or watchpoint.
- `working_interpretation` says the current tentative interpretation, if one has formed. It may be empty for a newly opened tension.
- Before creating new ActiveTensions, inspect existing `active_tensions` in the Digest context packet. For each one, ask whether this unit advances, corrects, reverses, weakens, answers, or makes it irrelevant. Emit an `update`, `resolve`, `close`, or `drop` operation for that existing `item_id` when appropriate.
- Use `create` / `append` when this unit leaves a still-live ActiveTension that has not yet settled into an ordinary fact, stable concept, summary, or reaction.
- Use `update` / `reactivate` when this unit changes the current interpretation, reshapes what the reader is tracking, or rekindles an older ActiveTension.
- Use `resolve` only when this unit gives a direct, make-sense answer that satisfies the carried forward-pull so the reader no longer needs to carry it as open. A resolve payload must include `answered_reason`, `working_interpretation`, and an exact `development_source_quote`.
- The `answered_reason` must explain why the cited evidence directly satisfies the forward-pull. If the evidence is only a precondition, setup, clue, partial explanation, or reframing, do not resolve; use `update` with the better `working_interpretation` and keep the item open.
- If you cannot explain why the tension is settled with current prompt-visible evidence, do not resolve it.
- Use `close` when the tension no longer remains alive in attention, but not because it was fully answered or settled. A close payload must include `closed_reason`.
- If an interpretation becomes durable, write the durable content to `concept_registry` or `thread_trace`, add `derived_from_active_attention_ids` on that downstream concept/thread entry, and close or resolve the ActiveTension. Do not use `promote` as an active-attention operation.
- Do not create an ActiveTension when the current unit raises and fully digests it locally.
- Do not store stable concepts, definitions, chapter summaries, or surfaced reactions in `active_attention`.
- Use `concept_registry` for reusable concepts, models, definitions, or distinctions.
- Use `thread_trace` for cross-passage or cross-chapter lines of development.""",
    ),
    PromptFragment(
        fragment_id='digest.source_grounding_policy',
        text="""- When an operation needs current-source evidence, add `source_quote` and optionally `source_role` inside the payload. The quote must be a short exact contiguous span copied from the current unit: no ellipses, no stitched fragments, no paraphrase, no translation. The runner will resolve it to paragraph + char-offset `source_refs`; never invent source coordinates yourself.
- If the basis is title/framing/prior memory rather than a current-source phrase, explain that basis in `tension_from` and omit `source_quote`.
- When an operation develops or settles an ActiveTension, add `development_source_quote` and optionally `development_source_role`; use the same short exact contiguous quote rule. The runner will resolve it to `development_source_refs`; never invent source coordinates yourself.
- Ordinary passing understanding belongs in `reading_impression`, not in persistent memory.
- ActiveTension item payloads may still use `attention_tags` as lightweight labels, but the ActiveTension fields are authoritative.
- Do not use legacy active-attention bucket/list fields in new state operations.
- Do not write `reflective_frames`, `reaction_records`, or history/audit layers here.""",
    ),
    PromptFragment(
        fragment_id='digest.output_behavior_policy',
        text="""- Do not output broad chapter summary.
- Do not explain whether you "used prior material".
- Do not decide or name the next route. After this read, the runner will settle the unit and advance normally.
- Return JSON only.""",
    ),
)


def _fragment_by_id(fragment_id: str) -> PromptFragment:
    """Return one Digest prompt fragment from the lossless prompt inventory."""

    for fragment in DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS:
        if fragment.fragment_id == fragment_id:
            return fragment
    raise KeyError(f"Unknown Digest fragment id: {fragment_id}")


def _target_source_grounding_text() -> str:
    """Return the source-grounding text for the live Digest XML context.

    The live fragment still contains deprecated ActiveTension-specific source
    guidance because the XML Digest contract keeps only the shared quote /
    SourceRef boundary.
    """

    live_text = _fragment_by_id("digest.source_grounding_policy").text
    excluded_markers = (
        "title/framing/prior memory",
        "ActiveTension",
        "legacy active-attention",
        "reflective_frames",
    )
    return "\n".join(
        line
        for line in live_text.splitlines()
        if not any(marker in line for marker in excluded_markers)
    )


DIGEST_TARGET_MEMORY_BOUNDARY_FRAGMENT = PromptFragment(
    fragment_id="digest.memory_general_policy",
    text="""- After the impression and any surfaced reactions, maintain Recent Reading Memory deliberately.
- The target Digest contract writes Recent Reading Memory directly in `recent_reading_memory`.
- Do not maintain state for its own sake.
- Do not copy surfaced reactions into memory just because they were strong.""",
)


DIGEST_CONTEXT_USE_GUIDE_FRAGMENT = PromptFragment(
    fragment_id="digest.context_use_guide",
    text="""- Treat BookInfo as orientation for stable book identity, not as source text.
- Treat ReadingState as carried understanding from prior reading. Use it to read continuously, but do not let it override the current source unit.
- Treat CurrentFocus as the immediate reading task: path, position, object, and intent.
- Treat CurrentFocus/ReadingObject as the source text to read now.
- Treat OutputContract as the required response shape and output discipline.""",
)


DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        READER_ROLE_FRAGMENT,
        _fragment_by_id("digest.instruction"),
        DIGEST_CONTEXT_USE_GUIDE_FRAGMENT,
        _fragment_by_id("digest.reading_impression_policy"),
        _fragment_by_id("digest.surfaced_reaction_policy"),
        _fragment_by_id("digest.reaction_anchor_and_callback_policy"),
        DIGEST_TARGET_MEMORY_BOUNDARY_FRAGMENT,
        _fragment_by_id("digest.recent_reading_memory_policy"),
        PromptFragment(
            fragment_id="digest.source_grounding_policy",
            text=_target_source_grounding_text(),
        ),
        _fragment_by_id("digest.output_behavior_policy"),
    ]
)


DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReaderRole",
        prompt_fragment_ref="reader.role",
    ),
    PromptTemplateNode(
        element_name="Instruction",
        children=(
            PromptTemplateNode(
                element_name="TaskOverview",
                prompt_fragment_ref="digest.instruction",
            ),
            PromptTemplateNode(
                element_name="ContextUseGuide",
                prompt_fragment_ref="digest.context_use_guide",
            ),
            PromptTemplateNode(
                element_name="ReadingBehavior",
                children=(
                    PromptTemplateNode(
                        element_name="ReadingImpression",
                        prompt_fragment_ref="digest.reading_impression_policy",
                    ),
                    PromptTemplateNode(
                        element_name="SurfacedReaction",
                        children=(
                            PromptTemplateNode(
                                element_name="ReactionSelection",
                                prompt_fragment_ref="digest.surfaced_reaction_policy",
                            ),
                            PromptTemplateNode(
                                element_name="ReactionGroundingAndCallback",
                                prompt_fragment_ref="digest.reaction_anchor_and_callback_policy",
                            ),
                        ),
                    ),
                ),
            ),
            PromptTemplateNode(
                element_name="MemoryInstruction",
                children=(
                    PromptTemplateNode(
                        element_name="MemoryBoundary",
                        prompt_fragment_ref="digest.memory_general_policy",
                    ),
                    PromptTemplateNode(
                        element_name="RecentReadingMemory",
                        prompt_fragment_ref="digest.recent_reading_memory_policy",
                    ),
                ),
            ),
            PromptTemplateNode(
                element_name="SourceGrounding",
                prompt_fragment_ref="digest.source_grounding_policy",
            ),
            PromptTemplateNode(
                element_name="ResponseDiscipline",
                prompt_fragment_ref="digest.output_behavior_policy",
            ),
        ),
    ),
)


def render_digest_reader_role_and_instruction_xml() -> str:
    """Render ReaderRole and Instruction XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE,
        registry=DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY,
        slot_values={},
    )


DIGEST_BOOK_INFO_TEMPLATE = (
    PromptTemplateNode(
        element_name="BookInfo",
        children=(
            PromptTemplateNode(element_name="BookIdentity", value_slot="book_identity"),
        ),
    ),
)


def _json_prompt_payload(payload: dict[str, str]) -> str:
    """Return stable JSON for inner XML payloads."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _json_prompt_object(payload: dict[str, object]) -> str:
    """Return stable JSON for dynamic prompt objects."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _json_prompt_value(payload: object) -> str:
    """Return stable JSON for dynamic prompt values."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_digest_book_info_xml(
    *,
    book_title: str,
    author: str,
) -> str:
    """Render BookInfo XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_BOOK_INFO_TEMPLATE,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "book_identity": _json_prompt_payload(
                {
                    "book_title": book_title,
                    "author": author,
                }
            ),
        },
    )


def _recent_memory_texts_for_digest(recent_reading_memory: Mapping[str, object] | None) -> list[str]:
    """Project Recent Reading Memory to the clean text list Digest needs."""

    if not isinstance(recent_reading_memory, Mapping):
        return []
    entries = recent_reading_memory.get("active_entries")
    if not isinstance(entries, list):
        return []
    memory_texts: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        memory_text = _clean_prompt_value(entry.get("memory_text"))
        if memory_text:
            memory_texts.append(memory_text)
    return memory_texts


DIGEST_READING_STATE_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReadingState",
        children=(
            PromptTemplateNode(
                element_name="ReadingMemory",
                children=(
                    PromptTemplateNode(element_name="RecentMemory", value_slot="recent_memory"),
                ),
            ),
        ),
    ),
)


def render_digest_reading_state_xml(
    *,
    recent_reading_memory: Mapping[str, object] | None = None,
) -> str:
    """Render ReadingState XML for Digest.

    The implemented target subset only includes RecentMemory. DurableMemory
    remains a pending design / assembly slice.
    """

    return render_prompt_template_xml(
        DIGEST_READING_STATE_TEMPLATE,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "recent_memory": _json_prompt_value(
                _recent_memory_texts_for_digest(recent_reading_memory)
            ),
        },
    )


def _clean_prompt_value(value: object) -> str:
    return str(value or "").strip()


def _compact_prompt_object(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in payload.items()
        if value not in ("", None, [], {})
    }


def _read_current_focus_template(reading_object_node: PromptTemplateNode) -> tuple[PromptTemplateNode, ...]:
    return (
        PromptTemplateNode(
            element_name="CurrentFocus",
            children=(
                PromptTemplateNode(element_name="ReadingPath", value_slot="reading_path"),
                PromptTemplateNode(element_name="ReadingPosition", value_slot="reading_position"),
                reading_object_node,
                PromptTemplateNode(element_name="ReadingIntent", value_slot="reading_intent"),
            ),
        ),
    )


DIGEST_CURRENT_FOCUS_TEMPLATE = _read_current_focus_template(
    PromptTemplateNode(
        element_name="ReadingObject",
        children=(
            PromptTemplateNode(element_name="SourceUnit", value_slot="source_unit"),
        ),
    )
)


def _paragraph_nodes_from_source_unit(source_unit: dict[str, object]) -> tuple[PromptTemplateNode, ...]:
    nodes: list[PromptTemplateNode] = []
    for item in source_unit.get("paragraph_slices", []):
        if not isinstance(item, dict):
            continue
        text = _clean_prompt_value(item.get("text"))
        if not text:
            continue
        paragraph_index = _clean_prompt_value(item.get("paragraph_index"))
        attributes = {"n": paragraph_index} if paragraph_index else {}
        nodes.append(
            PromptTemplateNode(
                element_name="Paragraph",
                attributes=attributes,
                literal_value=text,
            )
        )
    return tuple(nodes)


def _source_unit_text_from_sentences(current_unit_sentences: list[dict[str, object]] | None) -> str:
    return "\n".join(
        _clean_prompt_value(sentence.get("text"))
        for sentence in (current_unit_sentences or [])
        if isinstance(sentence, dict) and _clean_prompt_value(sentence.get("text"))
    )


def _reading_object_node(
    *,
    current_unit_source: dict[str, object] | None,
    current_unit_sentences: list[dict[str, object]] | None,
) -> PromptTemplateNode:
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    paragraph_nodes = _paragraph_nodes_from_source_unit(source_unit)
    if paragraph_nodes:
        source_unit_node = PromptTemplateNode(
            element_name="SourceUnit",
            children=paragraph_nodes,
        )
    else:
        source_text = _clean_prompt_value(source_unit.get("source_text"))
        if not source_text:
            source_text = _source_unit_text_from_sentences(current_unit_sentences)
        source_unit_node = PromptTemplateNode(
            element_name="SourceUnit",
            literal_value=source_text,
        )
    return PromptTemplateNode(
        element_name="ReadingObject",
        children=(source_unit_node,),
    )


def _human_position(*, chapter_title: str, current_unit_source: dict[str, object] | None) -> str:
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    paragraph_indexes = [
        _clean_prompt_value(item.get("paragraph_index"))
        for item in source_unit.get("paragraph_slices", [])
        if isinstance(item, dict) and _clean_prompt_value(item.get("paragraph_index"))
    ]
    if paragraph_indexes:
        start = paragraph_indexes[0]
        end = paragraph_indexes[-1]
        paragraph_position = f"p{start}" if start == end else f"p{start}-p{end}"
        return f"{chapter_title}, {paragraph_position}" if chapter_title else paragraph_position
    return chapter_title


def _reading_intent_payload() -> dict[str, object]:
    return {"intent": "read_current_source_unit_in_sequence"}


def render_digest_current_focus_xml(
    *,
    chapter_title: str,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> str:
    """Render CurrentFocus XML for Digest."""

    template = _read_current_focus_template(
        _reading_object_node(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        )
    )
    return render_prompt_template_xml(
        template,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "reading_path": _json_prompt_object({"mode": "mainline"}),
            "reading_position": _json_prompt_object(
                _compact_prompt_object(
                    {
                        "chapter_title": _clean_prompt_value(chapter_title),
                        "human_position": _human_position(
                            chapter_title=_clean_prompt_value(chapter_title),
                            current_unit_source=current_unit_source,
                        ),
                    }
                )
            ),
            "reading_intent": _json_prompt_object(_reading_intent_payload()),
        },
    )


DIGEST_OUTPUT_USE_GUIDE_FRAGMENT = PromptFragment(
    fragment_id="digest.output_use_guide",
    text="Follow the instructions above when deciding what to produce; use this section for the exact JSON field names and shapes.",
)


DIGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="digest.return_format_contract",
    text="""Return JSON only.
Top-level fields:
{
  "reading_impression": "...",
  "surfaced_reactions": [],
  "recent_reading_memory": []
}""",
)


DIGEST_READING_IMPRESSION_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.reading_impression_contract",
    text="""`reading_impression` is the reader's immediate expression after finishing the current unit: tone, felt pressure, atmosphere, affect, or overall impression.
It is not durable memory and is not Recent Reading Memory.
It should not be carried into later Digest context by default.
It should not duplicate `surfaced_reactions`: if the expression is tied to a specific source span and worth showing as a visible margin-note-style output, use `surfaced_reactions`.
It should not duplicate `recent_reading_memory`: if the content should be remembered for coherent continued reading, write it as Recent Reading Memory.""",
)


DIGEST_SURFACED_REACTION_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.surfaced_reaction_contract",
    text="""`surfaced_reactions` contains visible reaction output.
Shape:
{
  "source_quote": "...",
  "content": "...",
  "prior_link": null,
  "outside_link": null,
  "search_intent": null
}
Detailed reaction-selection and source-quote behavior live under Instruction.""",
)


DIGEST_RECENT_READING_MEMORY_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.recent_reading_memory_contract",
    text="""`recent_reading_memory` contains the Recent Reading Memory output produced by Digest.
Shape:
{
  "recent_reading_memory": [
    {
      "kind": "event_or_situation|claim_or_argument|definition_or_distinction|causal_or_structural_link|character_or_relationship|emotional_or_tonal_shift|image_or_scene|local_pattern_or_thread|fact|other",
      "memory_text": "..."
    }
  ]
}
Write only Recent Reading Memory entries here.
Do not include operation-level reasons.
Do not write durable memory, digests, hidden routing state, or other memory stores in this field.""",
)


DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        DIGEST_OUTPUT_USE_GUIDE_FRAGMENT,
        DIGEST_RETURN_FORMAT_FRAGMENT,
        DIGEST_READING_IMPRESSION_CONTRACT_FRAGMENT,
        DIGEST_SURFACED_REACTION_CONTRACT_FRAGMENT,
        DIGEST_RECENT_READING_MEMORY_CONTRACT_FRAGMENT,
    ]
)


DIGEST_OUTPUT_CONTRACT_TEMPLATE = (
    PromptTemplateNode(
        element_name="OutputContract",
        children=(
            PromptTemplateNode(
                element_name="OutputUseGuide",
                prompt_fragment_ref="digest.output_use_guide",
            ),
            PromptTemplateNode(
                element_name="LanguageContract",
                value_slot="language_contract",
            ),
            PromptTemplateNode(
                element_name="ReturnFormat",
                prompt_fragment_ref="digest.return_format_contract",
            ),
            PromptTemplateNode(
                element_name="FieldContracts",
                children=(
                    PromptTemplateNode(
                        element_name="ReadingImpressionContract",
                        prompt_fragment_ref="digest.reading_impression_contract",
                    ),
                    PromptTemplateNode(
                        element_name="SurfacedReactionContract",
                        prompt_fragment_ref="digest.surfaced_reaction_contract",
                    ),
                    PromptTemplateNode(
                        element_name="RecentReadingMemoryContract",
                        prompt_fragment_ref="digest.recent_reading_memory_contract",
                    ),
                ),
            ),
        ),
    ),
)


def render_digest_output_contract_xml(*, output_language_name: str) -> str:
    """Render OutputContract XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_OUTPUT_CONTRACT_TEMPLATE,
        registry=DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY,
        slot_values={
            "language_contract": LANGUAGE_OUTPUT_CONTRACT.format(
                output_language_name=_clean_prompt_value(output_language_name)
            ),
        },
    )


def _digest_prompt_assembly_template(
    *,
    current_unit_source: dict[str, object] | None,
    current_unit_sentences: list[dict[str, object]] | None,
) -> tuple[PromptTemplateNode, ...]:
    return (
        *DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE,
        *DIGEST_BOOK_INFO_TEMPLATE,
        *DIGEST_READING_STATE_TEMPLATE,
        *_read_current_focus_template(
            _reading_object_node(
                current_unit_source=current_unit_source,
                current_unit_sentences=current_unit_sentences,
            )
        ),
        *DIGEST_OUTPUT_CONTRACT_TEMPLATE,
    )


def _digest_prompt_fragment_registry() -> PromptFragmentRegistry:
    return PromptFragmentRegistry(
        [
            *DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY.list(),
            *DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY.list(),
        ]
    )


def build_digest_prompt_assembly_spec(
    *,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> PromptAssemblySpec:
    """Build the full Digest XML prompt spec for one current unit.

    The current source unit may render as paragraph children, so this spec is
    built per call.
    """

    return PromptAssemblySpec(
        spec_id=DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID,
        owner_node="digest",
        prompt_version=DIGEST_PROMPT_VERSION,
        promptset_version=DIGEST_XML_PROMPTSET_VERSION,
        template_nodes=_digest_prompt_assembly_template(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        ),
        fragment_registry=_digest_prompt_fragment_registry(),
        required_slots=(
            "book_identity",
            "recent_memory",
            "reading_path",
            "reading_position",
            "reading_intent",
            "language_contract",
        ),
        output_contract="digest_xml_json_v1",
    )


def render_digest_prompt_xml(
    *,
    book_title: str,
    author: str,
    chapter_title: str,
    output_language_name: str,
    recent_reading_memory: Mapping[str, object] | None = None,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> PromptAssemblyResult:
    """Render the full Digest XML prompt."""

    return PromptAssembler().assemble(
        build_digest_prompt_assembly_spec(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        ),
        slot_values={
            "book_identity": _json_prompt_payload(
                {
                    "book_title": book_title,
                    "author": author,
                }
            ),
            "recent_memory": _json_prompt_value(
                _recent_memory_texts_for_digest(recent_reading_memory)
            ),
            "reading_path": _json_prompt_object({"mode": "mainline"}),
            "reading_position": _json_prompt_object(
                _compact_prompt_object(
                    {
                        "chapter_title": _clean_prompt_value(chapter_title),
                        "human_position": _human_position(
                            chapter_title=_clean_prompt_value(chapter_title),
                            current_unit_source=current_unit_source,
                        ),
                    }
                )
            ),
            "reading_intent": _json_prompt_object(_reading_intent_payload()),
            "language_contract": LANGUAGE_OUTPUT_CONTRACT.format(
                output_language_name=_clean_prompt_value(output_language_name)
            ),
        },
    )


DIGEST_PROMPT = PromptDefinition(
    prompt_id="attentional_v2.digest",
    version=DIGEST_PROMPT_VERSION,
    owner_node="digest",
    status="active",
    purpose="Digest one accepted source unit and return reader-facing/current-reading outputs.",
    system_prompt=DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
    user_prompt_template="<DigestPrompt assembled by render_digest_prompt_xml>",
    required_inputs=(
        "book_identity",
        "recent_memory",
        "reading_path",
        "reading_position",
        "reading_intent",
        "language_contract",
    ),
    output_contract="digest_xml_json_v1",
)
