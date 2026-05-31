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


INGEST_PROMPT_VERSION = "attentional_v2.ingest.v1"
INGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.ingest.xml.v1"
INGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v44"
INGEST_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Ingest prompt in the user message. Return JSON only."


INGEST_CURRENT_STEP_FRAGMENT = PromptFragment(
    fragment_id="ingest.current_step",
    text="""You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output. You are previewing the bounded forward source area from the current reading cursor in order to prepare Digest.

Your work in this call is to select the next forward source unit that you should read carefully in the Digest step.

Memory-retrieval support is an intended future Ingest responsibility, but its concrete request behavior is deferred until the memory design lands.""",
)


INGEST_CONTEXT_USE_GUIDE_FRAGMENT = PromptFragment(
    fragment_id="ingest.context_use_guide",
    text="""- the visible source preview is primary
- book identity is orientation, not source text
- `RetrievalSurface` is intentionally empty in the current design slice""",
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
- If the move is still unfinished at the available boundary, choose the best honest end point you have. Do not pretend the local move is complete.""",
)


INGEST_REQUEST_MEMORY_SUPPORT_FRAGMENT = PromptFragment(
    fragment_id="ingest.request_memory_support",
    text="""RequestMemorySupport is reserved for the future instruction that will tell Ingest how to ask what prior reading memory is needed in order to read the selected unit continuously in the Digest step.

Current status: placeholder only.

The detailed recall-query policy should not be specified until the new memory design defines the available memory stores, indexes, retrieval purposes, request budget, and runtime tool behavior.""",
)


INGEST_EXECUTION_LIMITS_FRAGMENT = PromptFragment(
    fragment_id="ingest.execution_limits",
    text="""Stay inside the Ingest boundary.

Do not read or interpret the selected unit as the final reading. Do not write reading impressions, notes, highlights, surfaced reactions, summaries, or memory updates.

Do not perform runtime work. Do not resolve anchors, retry or choose fallback boundaries, advance the cursor, settle state, or execute memory retrieval.

Do not use external web search or request tools. Memory retrieval request behavior is deferred until the memory design lands.

Return only the JSON described by OutputContract. Do not include markdown, commentary, hidden reasoning, or fields that are not requested.""",
)


INGEST_OUTPUT_FIELDS_FRAGMENT = PromptFragment(
    fragment_id="ingest.output_fields",
    text="""`OutputFields` names the information Ingest must output.

Fields:

- `end_anchor_text`: exact visible source quote at the end of the chosen unit
- `boundary_type`: boundary classification for why the unit ends there
- `reason`: brief internal reason for the boundary choice""",
)


INGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="ingest.return_format",
    text="""`ReturnFormat` defines the concrete JSON shape.

Return JSON only:

{
  "end_anchor_text": "...",
  "boundary_type": "paragraph_end",
  "reason": "..."
}""",
)


INGEST_PROMPT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        READER_ROLE_FRAGMENT,
        INGEST_CURRENT_STEP_FRAGMENT,
        INGEST_CONTEXT_USE_GUIDE_FRAGMENT,
        INGEST_SELECT_NEXT_UNIT_FRAGMENT,
        INGEST_REQUEST_MEMORY_SUPPORT_FRAGMENT,
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
                element_name="RequestMemorySupport",
                prompt_fragment_ref="ingest.request_memory_support",
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
        output_contract="ingest_json_v1",
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
    purpose="Select the next forward source unit and reserve future memory-support retrieval.",
    system_prompt=INGEST_TRANSPORT_SYSTEM_PROMPT,
    user_prompt_template="<IngestPrompt assembled by render_ingest_prompt_xml>",
    required_inputs=("book_identity", "current_view_position", "current_view_content"),
    output_contract="ingest_json_v1",
)
