"""Prompt definition for attentional_v2 Ingest."""

from __future__ import annotations

from collections.abc import Mapping
import json

from .assembly import (
    PromptFragment,
    PromptFragmentRegistry,
    PromptTemplateNode,
)
from .assembler import PromptAssembler, PromptAssemblyResult, PromptAssemblySpec
from .reader_role import READER_ROLE_FRAGMENT
from .types import PromptDefinition


INGEST_PROMPT_VERSION = "attentional_v2.ingest.v11"
INGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.ingest.xml.v11"
INGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v61"
INGEST_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Ingest prompt in the user message. Use the required submit_ingest_result tool as the final output channel."


INGEST_CURRENT_STEP_FRAGMENT = PromptFragment(
    fragment_id="ingest.current_step",
    text="""You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output. You are previewing the bounded forward source area from the current reading cursor in order to prepare Digest.

Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

After selecting it, briefly name any earlier reading that this unit makes you want to remember before Digest reads it closely.

When those recalls exist, use the available Unit Memory retrieval tool so runtime can prepare prior-reading support before you return the final Ingest JSON.""",
)


INGEST_CONTEXT_USE_GUIDE_FRAGMENT = PromptFragment(
    fragment_id="ingest.context_use_guide",
    text="""- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty here
- prior-reading recall here means describing what should be remembered; runtime performs retrieval only through the provided tool""",
)


INGEST_SELECT_NEXT_UNIT_FRAGMENT = PromptFragment(
    fragment_id="ingest.select_next_unit",
    text="""Select one forward source unit from the current reading cursor.

Priority order:
- Judge from the visible source text first.
- Respect author structure before local convenience.

Source range:
- Choose directly from `CurrentView / Content`.
- Do not cross the provided `CurrentView / Content` boundary.
- The unit always starts at the current source cursor in `CurrentView / Position`. Do not invent a start id.

Unit size:
- Choose the smallest complete local move that can honestly be read as one unit.
- Prefer ending within the current paragraph.
- Continue into the next paragraph only when the same local move is clearly continuing.
- Do not pretend a move is finished when it is still unfolding; choose the best honest boundary available.

Structural cues:
- Treat `chapter_heading` and `section_heading` as weak structure cues, not automatic standalone units.
- A heading may stand alone only when its visible wording already forms a complete, meaningful local move.
- If a heading reads more like a label, lead-in, or structural setup, merge it with the immediately following body paragraph when `CurrentView / Content` allows.
- Stay proportionate around thin structural text. Do not carve out a very short unit just because the text is marked as a heading.
- Before finalizing the unit boundary, trim only boundary sentences that are purely non-lexical residue, such as ornament/divider/separator lines.
- `text_role` may help orient you, but it must not decide the boundary by itself.

End anchor and continuation:
- Set `end_anchor_text` to an exact quote from the visible preview at the end of the unit you choose.
- Copy `end_anchor_text` character-for-character from the preview source text. Do not paraphrase, omit punctuation, or add ellipses.
- Choose a sufficiently unique tail anchor, usually 20-80 Chinese characters or 8-25 English words. If the unit is very short, the full unit tail is acceptable.
- If the move is still unfinished at the available boundary, choose the best honest end point you have. Do not pretend the local move is complete.

Boundary closure check:
- After choosing the semantic end of the unit, check whether `end_anchor_text` accidentally leaves behind punctuation that belongs to the same sentence, quotation, parenthetical, bracketed span, or footnote marker.
- Include terminal punctuation and attached closing marks that complete the chosen unit, such as `。`, `.`, `！`, `？`, `”`, `’`, `）`, `]`, and `】`.
- Do not stop immediately before punctuation or a closing mark that closes the sentence, quote, parenthesis, bracket, or note span you are choosing.
- Do not absorb opening punctuation, bullets, separators, or markers that begin the next unit.""",
)


INGEST_RECALL_PRIOR_READING_FRAGMENT = PromptFragment(
    fragment_id="ingest.recall_prior_reading",
    text="""# Purpose

After choosing the next source unit, identify prior-reading memory targets that would help Digest read this unit as part of the book's ongoing movement.

A recall is a retrieval target for prior reading memory. It describes what earlier understanding runtime should try to find, using the selected unit as the cue.

The recall should look backward beyond the selected unit. Do not use recall to summarize, rephrase, or search for another sentence inside the selected unit itself.

# Source scope

Use `CurrentView / Content` to choose the boundary and to notice cues for recall. Do not treat any text in `CurrentView / Content` as already-read memory evidence.

After you choose the boundary, the selected unit is current source text and any remaining preview text is future source text. Neither should be written as the prior memory content.

If a recall would merely retrieve the same idea already stated in the selected unit, return no recall or describe a broader prior-memory target without copying that current-unit content.

# When to recall

Write a recall when the selected unit returns to, develops, contrasts with, or depends on something already read: a person, relationship, concept, question, object, image, scene, argument, choice, conflict, method, term, or unresolved pressure.

If the selected unit is purely structural, too thin to benefit from prior memory, or only invites generic background, return an empty list.

# Retrieval-friendly content

Write each `recall_text` as the prior understanding runtime should try to find. It does not need to assert that the prior memory already exists.

A strong `recall_text` names the selected-unit cue and the earlier meaning, relation, claim, action, or tension that would be useful to retrieve.

Use content-grounded wording:
- "这位青年人或陌生沙门此前与法义、个人求道、以及是否能通过教义解脱有关的理解。"
- "悉达多此前与婆罗门教诲、沙门苦行、法义传授和个人求道有关的理解。"
- "乔文达此前与悉达多同行、追随、分离或精神关系有关的理解。"

# Focus

Let the selected unit decide the recall focus. The recall should support what Digest will need to understand in this unit: its claim, action, conflict, image, relationship, method, term, contrast, or development.

For doctrinal, argumentative, conceptual, or methodological units, recall prior claims, definitions, examples, contrasts, or teaching content.

For person or relationship units, recall earlier choices, conflicts, attachments, obligations, or unresolved tensions that matter to the present unit.

# Writing constraints

Write each `recall_text` in the same primary language as the current source text.

Preserve important names, titles, and technical terms in the form used by the source text when available.

Do not mention paragraph numbers, line numbers, XML ids, CurrentView labels, or phrases like "Paragraph 109" / "段落11".

Do not use outside knowledge about the book, author, later plot, or general literary context. Use only the selected source unit and the already-read continuity implied by the reading so far.

When naming people or speakers, use names that are explicit in the selected unit or unambiguous from already-read continuity. If the subject is unclear, describe it by the wording available in the selected unit, such as "这位青年人", "陌生的沙门", "the speaker", or "the narrator", instead of inventing a name.

Set each recall `basis` exactly to `selected_source_unit`.

# Number of recalls

Return zero to three recalls.

Prefer one strong focused recall over several weak recalls.

Create separate recalls only when the selected unit contains distinct continuity needs. Do not list every name or noun, and do not split mechanically by entity.

# Tool use

If you write one or more recalls, call the Unit Memory retrieval tool with those recalls so runtime can retrieve, select, and prepare the prior understanding that may support Digest.""",
)


INGEST_EXECUTION_LIMITS_FRAGMENT = PromptFragment(
    fragment_id="ingest.execution_limits",
    text="""Stay inside the Ingest boundary.

Do not read or interpret the selected unit as the final reading. Do not write reading impressions, notes, highlights, surfaced reactions, summaries, or memory updates.

Do not perform runtime work. Do not resolve anchors, retry or choose fallback boundaries, advance the cursor, settle state, or execute memory retrieval yourself.

Do not use external web search. Use only the provided Unit Memory retrieval tool when recalls are non-empty.

Submit only the result described by OutputContract through the required final output tool. Do not include markdown, commentary, hidden reasoning, or fields that are not requested.""",
)


INGEST_OUTPUT_FIELDS_FRAGMENT = PromptFragment(
    fragment_id="ingest.output_fields",
    text="""`OutputFields` names the information Ingest must output.

Fields:

- `end_anchor_text`: exact visible source quote at the end of the chosen unit
- `boundary_type`: boundary classification for why the unit ends there
- `reason`: brief internal reason for the boundary choice
- `memory_recalls`: zero to three prior-reading recalls raised by the selected unit""",
)


INGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="ingest.return_format",
    text="""`ReturnFormat` defines the concrete JSON shape.

Submit this shape through the required final output tool:

{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "...",
  "memory_recalls": [
    {
      "recall_id": "r1",
      "recall_text": "...",
      "basis": "selected_source_unit"
    }
  ]
}""",
)


INGEST_PROMPT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        READER_ROLE_FRAGMENT,
        INGEST_CURRENT_STEP_FRAGMENT,
        INGEST_CONTEXT_USE_GUIDE_FRAGMENT,
        INGEST_SELECT_NEXT_UNIT_FRAGMENT,
        INGEST_RECALL_PRIOR_READING_FRAGMENT,
        INGEST_EXECUTION_LIMITS_FRAGMENT,
        INGEST_OUTPUT_FIELDS_FRAGMENT,
        INGEST_RETURN_FORMAT_FRAGMENT,
    ]
)


INGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReaderRole",
        prompt_fragment_ref="reader.role",
    ),
    PromptTemplateNode(
        element_name="Instruction",
        children=(
            PromptTemplateNode(
                element_name="CurrentStep",
                prompt_fragment_ref="ingest.current_step",
            ),
            PromptTemplateNode(
                element_name="ContextUseGuide",
                prompt_fragment_ref="ingest.context_use_guide",
            ),
            PromptTemplateNode(
                element_name="SelectNextUnit",
                prompt_fragment_ref="ingest.select_next_unit",
            ),
            PromptTemplateNode(
                element_name="RecallPriorReading",
                prompt_fragment_ref="ingest.recall_prior_reading",
            ),
            PromptTemplateNode(
                element_name="ExecutionLimits",
                prompt_fragment_ref="ingest.execution_limits",
            ),
        ),
    ),
)


INGEST_BOOK_INFO_TEMPLATE = (
    PromptTemplateNode(
        element_name="BookInfo",
        children=(
            PromptTemplateNode(element_name="BookIdentity", value_slot="book_identity"),
        ),
    ),
)


def _clean_prompt_value(value: object) -> str:
    return "" if value is None else str(value).strip()


def _json_prompt_object(payload: Mapping[str, object]) -> str:
    return json.dumps(dict(payload), ensure_ascii=False, indent=2)


def _paragraph_nodes_from_current_view_content(current_view_content: Mapping[str, object]) -> tuple[PromptTemplateNode, ...]:
    nodes: list[PromptTemplateNode] = []
    paragraph_slices = current_view_content.get("paragraph_slices", [])
    if not isinstance(paragraph_slices, list):
        paragraph_slices = []
    for item in paragraph_slices:
        if not isinstance(item, Mapping):
            continue
        text = _clean_prompt_value(item.get("text"))
        if not text:
            continue
        attributes = {
            "n": _clean_prompt_value(item.get("paragraph_index")),
            "role": _clean_prompt_value(item.get("text_role")),
            "start_char": _clean_prompt_value(item.get("start_char")),
            "end_char": _clean_prompt_value(item.get("end_char")),
        }
        nodes.append(
            PromptTemplateNode(
                element_name="Paragraph",
                attributes={key: value for key, value in attributes.items() if value},
                literal_value=text,
            )
        )
    return tuple(nodes)


def _current_view_template(current_view_content: Mapping[str, object]) -> tuple[PromptTemplateNode, ...]:
    content_children = _paragraph_nodes_from_current_view_content(current_view_content)
    if content_children:
        content_node = PromptTemplateNode(
            element_name="Content",
            children=content_children,
        )
    else:
        content_node = PromptTemplateNode(
            element_name="Content",
            value_slot="current_view_content",
        )
    return (
        PromptTemplateNode(
            element_name="CurrentView",
            children=(
                PromptTemplateNode(element_name="Position", value_slot="current_view_position"),
                content_node,
            ),
        ),
    )


INGEST_RETRIEVAL_SURFACE_TEMPLATE = (
    PromptTemplateNode(
        element_name="RetrievalSurface",
        self_closing=True,
    ),
)


INGEST_OUTPUT_CONTRACT_TEMPLATE = (
    PromptTemplateNode(
        element_name="OutputContract",
        children=(
            PromptTemplateNode(
                element_name="OutputFields",
                prompt_fragment_ref="ingest.output_fields",
            ),
            PromptTemplateNode(
                element_name="ReturnFormat",
                prompt_fragment_ref="ingest.return_format",
            ),
        ),
    ),
)


def _ingest_prompt_assembly_template(
    *,
    current_view_content: Mapping[str, object],
) -> tuple[PromptTemplateNode, ...]:
    return (
        *INGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE,
        *INGEST_BOOK_INFO_TEMPLATE,
        *_current_view_template(current_view_content),
        *INGEST_RETRIEVAL_SURFACE_TEMPLATE,
        *INGEST_OUTPUT_CONTRACT_TEMPLATE,
    )


def build_ingest_prompt_assembly_spec(
    *,
    current_view_content: Mapping[str, object] | None = None,
) -> PromptAssemblySpec:
    """Build the Ingest XML prompt spec for one forward source preview."""

    return PromptAssemblySpec(
        spec_id=INGEST_XML_PROMPT_ASSEMBLY_SPEC_ID,
        owner_node="ingest",
        prompt_version=INGEST_PROMPT_VERSION,
        promptset_version=INGEST_XML_PROMPTSET_VERSION,
        template_nodes=_ingest_prompt_assembly_template(
            current_view_content=dict(current_view_content or {}),
        ),
        fragment_registry=INGEST_PROMPT_FRAGMENT_REGISTRY,
        required_slots=(
            "book_identity",
            "current_view_position",
            "current_view_content",
        ),
                output_contract="ingest_boundary_memory_recalls_json_v2",
    )


def render_ingest_prompt_xml(
    *,
    book_title: str,
    author: str,
    current_view_position: Mapping[str, object],
    current_view_content: Mapping[str, object],
) -> PromptAssemblyResult:
    """Render the full Ingest XML prompt."""

    return PromptAssembler().assemble(
        build_ingest_prompt_assembly_spec(current_view_content=current_view_content),
        slot_values={
            "book_identity": _json_prompt_object(
                {
                    "book_title": book_title,
                    "author": author,
                }
            ),
            "current_view_position": _json_prompt_object(current_view_position),
            "current_view_content": _json_prompt_object(current_view_content),
        },
    )


INGEST_PROMPT = PromptDefinition(
    prompt_id="attentional_v2.ingest",
    version=INGEST_PROMPT_VERSION,
    owner_node="ingest",
    status="active",
    purpose="Select the next forward source unit and express prior-reading recalls for Unit Memory retrieval.",
    system_prompt=INGEST_TRANSPORT_SYSTEM_PROMPT,
    user_prompt_template="<IngestPrompt assembled by render_ingest_prompt_xml>",
    required_inputs=("book_identity", "current_view_position", "current_view_content"),
    output_contract="ingest_boundary_memory_recalls_json_v2",
)
