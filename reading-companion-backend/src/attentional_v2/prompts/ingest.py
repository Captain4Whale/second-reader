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


INGEST_PROMPT_VERSION = "attentional_v2.ingest.v19"
INGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.ingest.xml.v19"
INGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v76"
INGEST_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Ingest prompt in the user message. Use the required submit_ingest_result tool as the final output channel."


INGEST_CURRENT_STEP_FRAGMENT = PromptFragment(
    fragment_id="ingest.current_step",
    text="""You are in the Ingest step of a sequential deep-reading loop.

This step happens before Digest. You are not yet reading the selected unit for interpretation or reader-facing output.

You are shown a bounded forward reading lookahead window from the current reading cursor. In this call you do three things:

1. Browse the whole visible preview as a reader and form a fine-grained provisional map of its consecutive semantic partitions.
2. Commit the current Digest unit by grouping a left prefix of that partition map: `preview_partition[0..k]`.
3. After committing that first unit, decide whether Digest would benefit from prior-reading memory; if yes, express those recall targets only through the Unit Memory retrieval tool.

The rest of the window is lookahead context only. Its provisional map helps you place the current Digest-unit boundary and lets reviewers audit what you saw; it is not itself being read by Digest yet.

The later provisional partitions should stay lightweight: title, boundary, and status only. Only the committed Digest unit gets a boundary rationale.""",
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
    text="""Partition the forward window into fine-grained coherent reading partitions, give each provisional partition a compact title, then commit the current Digest unit by grouping a left prefix of those partitions. The committed unit starts at the current reading cursor and covers `preview_partition[0..k]` for some `k >= 0`.

What a semantic unit is — a continuous span of source text that satisfies all of:

- Internally coherent: its sentences hang together on one topic, argument, scene, exchange, image, concept, or logical move.
- Locally complete: it closes one forward move enough for Digest to read it as the present object of attention. For example: a claim and its immediate support, an example and its point, a scene or beat that lands, a concept introduced and initially unpacked, a turn in dialogue, or a local summary.
- Unified in local function: adjacent paragraphs that jointly perform the same setup, character construction, scene build, argument support, example chain, or emotional turn remain one unit even when different paragraphs emphasize different sides of that function.
- Fine-grained: each `preview_partition` may be the smallest span that is still locally complete. Do not let fine-grained map boundaries automatically become Digest-unit boundaries.
- Naturally bounded: it ends at a real transition, such as topic shift, argument closing, scene change, change in speaker, change in rhetorical function, or the start of a new move.

How to choose the boundary:

- Consider the whole visible window first. Do not commit a boundary the moment you reach the first plausible stopping point.
- Conceptually divide the window into consecutive fine-grained partitions in order, with no gaps. Use that whole-window view to expose your preview map for audit.
- Give each provisional partition a compact local-function title that names what that partition is doing in the reading. The title is not a summary, not commentary, and not a Digest result.
- After partitioning, grow the committed Digest unit from the left: start with `preview_partition[0]`, then ask whether `preview_partition[1]`, `preview_partition[2]`, and so on still belong to the same larger semantic movement as the prefix already chosen.
- Do not let the ability to title smaller aspects force an early Digest-unit split. A portrait, setup, scene, argument, list of principles, or example chain can contain several namable partitions while still being one Digest unit.
- Before committing a boundary, ask whether the next partition starts a genuinely new move or merely continues the same larger local function from another angle. If it continues the same local exposition, setup, character portrait, scene build, claim-support movement, example chain, or list group, include it in the current Digest unit.
- Commit only this left-prefix Digest unit. Anything after it is provisional lookahead context.
- Do not write reasons, explanations, summaries, or interpretive comments for later provisional partitions. Later partitions exist only to expose the audit map that helped you choose the current boundary.
- The first unit always starts at the current source cursor in `CurrentView / Position`. Do not invent or output a start position.
- A boundary falls on a sentence edge and never inside a sentence.
- A boundary may fall inside a paragraph when one long paragraph contains more than one complete move.
- A unit may also span several paragraphs when the same local move clearly continues across them.
- The window is assembled from paragraph slices, but the unit is not required to align to paragraph edges.

Window tail:

- The window end is controlled by runtime budget and may fall in the middle of a move.
- Do not over-merge the first unit just to make the later window tail look balanced or complete.
- Mark only the final provisional partition as `open_tail` when the preview visibly stops before that partition has completed.
- The committed unit must end at a complete partition boundary. Do not end the committed unit at an `open_tail` partition.
- Only the committed unit boundary is authoritative.

Signals you may use:
- Lexical cohesion / topic continuity: while the same entities and keywords are still in play, the unit continues; when the topical center clearly shifts (old entities exit, new ones enter), that is a boundary.
- Argument completeness: claim → evidence → qualification forms one unit; a new claim opens a new unit.
- Narrative change: a clear change of time, place, character, goal, or cause-effect marks a natural boundary.
- One main idea: a unit should be roughly what compresses into a single main idea; if it sprawls into several, it is too long.
- Prediction break: when what comes next can no longer be predicted from the current idea, a new unit has begun.

Size and length:

- A unit is a small, digestible reading move: about the amount Digest can turn into one coherent Understanding.
- It may be part of a long paragraph, one paragraph, or a few paragraphs.
- It must never cross a chapter boundary.
- The lookahead window is deliberately longer than one unit. The first unit should usually end well within it.
- If the first unit approaches the length of the whole window, you have almost certainly merged too much. Back off to the nearest earlier locally complete move.
- Use the Digest-unit size band as a guardrail: if the current prefix is under about 300 source tokens, strongly prefer merging the next semantically compatible partition; around 900 source tokens, prefer stopping at the next coherent partition boundary; do not exceed about 1600 source tokens unless `preview_partition[0]` alone is already that large.
- Length is not the reason to merge. Merge only when the next partition still belongs to the same larger semantic movement; stop when the next partition opens a new topic, scene, claim, problem, or section even if the current unit is still short.

Structural cues:

- Treat `chapter_heading` and `section_heading` as weak structure cues, not automatic standalone units.
- Merge a label-like heading with the body it introduces.
- Let a heading stand alone only if its wording itself forms a complete, meaningful move.
- Ignore pure ornament / divider / separator lines at the boundary.
- In aphorism, tweet-storm, bullet-list, or principle-list material, repeated separators or short standalone sentences are not automatic Digest-unit boundaries. Fine-grained partitions may be one principle each, but the committed unit should group the left prefix by a larger shared function, such as learning and judgment principles, permissioned versus permissionless leverage, or a cluster of related wealth definitions.
- `text_role` may help orient you, but it must not decide the boundary by itself.""",
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

If a recall would merely retrieve the same idea already stated in the selected unit, do not call the tool, or describe a broader prior-memory target without copying that current-unit content.

# When to recall

Write a recall when the selected unit returns to, develops, contrasts with, or depends on something already read: a person, relationship, concept, question, object, image, scene, argument, choice, conflict, method, term, or unresolved pressure.

If the selected unit is purely structural, too thin to benefit from prior memory, or only invites generic background, do not call the Unit Memory retrieval tool.

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

Use zero to three recalls.

Zero recalls means no Unit Memory tool call.

Prefer one strong focused recall over several weak recalls.

Create separate recalls only when the selected unit contains distinct continuity needs. Do not list every name or noun, and do not split mechanically by entity.

# Tool use

If you write one or more recalls, call the Unit Memory retrieval tool with those recalls so runtime can retrieve, select, and prepare the prior understanding that may support Digest.

The Unit Memory retrieval tool call is the only place to submit recall targets. Do not include `memory_recalls` in the final structured result.""",
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
    text="""`OutputFields` and `ReturnFormat` define the concrete structured result.""",
)


INGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="ingest.return_format",
    text="""Submit this shape through the required final output tool:

{
  "unit": {
    "end_paragraph_n": "<the n attribute of the Paragraph where the first unit ends>",
    "end_at": "paragraph_end | <exact tail quote located inside end_paragraph_n>"
  },
  "preview_partition": [
    {
      "title": "<short local-function title for this provisional unit>",
      "end_paragraph_n": "<the n attribute of the Paragraph where this provisional unit ends>",
      "end_at": "paragraph_end | <exact tail quote located inside end_paragraph_n>",
      "status": "complete | open_tail"
    }
  ],
  "reason": "<boundary rationale>"
}

Rules:

- The committed unit starts at the current cursor in `CurrentView / Position`; do not emit a start position.
- `end_paragraph_n` must copy the `n` attribute from one visible `Paragraph` in `CurrentView / Content`.
- Use `"paragraph_end"` when the unit ends at the end of that visible paragraph slice.
- Use an exact tail quote only when the unit must end inside a long paragraph at a sentence boundary.
- The exact tail quote must be copied character-for-character from `end_paragraph_n` and must uniquely identify the unit end within that paragraph.
- `preview_partition` must be a non-empty ordered map of the visible preview from the current cursor through the visible tail.
- `unit.end_paragraph_n` and `unit.end_at` must exactly match the boundary of one complete `preview_partition[k]`.
- The committed unit covers the left prefix `preview_partition[0..k]`; do not skip earlier partitions, and do not end the committed unit at an `open_tail` partition.
- Each `preview_partition` title should be brief and should name the local reading function of that provisional unit; it must not summarize, evaluate, or explain that unit.
- Each `preview_partition` entry uses the same `end_paragraph_n` / `end_at` boundary syntax as `unit`.
- Set `status` to `"complete"` when the provisional unit closes inside the visible preview.
- Set `status` to `"open_tail"` only for the final partition when the visible preview ends in the middle of a larger move.
- `reason` explains why the committed Digest unit should group `preview_partition[0..k]` and end at `unit.end_paragraph_n` / `unit.end_at`. It is a boundary rationale for the committed unit only, not a summary and not a second source span.
- Do not include rationale, summary, commentary, explanation, or extra fields inside any `preview_partition` item. Later partition entries must stay to `title`, `end_paragraph_n`, `end_at`, and `status`.
- Do not include `memory_recalls` in this final result. If prior-reading memory is needed, express those recalls only by calling `retrieve_unit_memory`.
- Do not output markdown, commentary, or extra fields.""",
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
        output_contract="ingest_unit_boundary_preview_partition_json_v4",
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
    output_contract="ingest_unit_boundary_preview_partition_json_v4",
)
