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


DIGEST_PROMPT_VERSION = "attentional_v2.digest.v2"
DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.digest.xml.v2"
DIGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v46"
DIGEST_XML_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Digest prompt in the user message. Return JSON only."


# These fragments define the live Digest reader action and its XML Instruction blocks.
DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS = (
    READER_ROLE_FRAGMENT,
    PromptFragment(
        fragment_id="digest.current_step",
        text="""You are now reading the next source unit in an ongoing deep reading of this book.

Stay with this unit as the present moment of reading. Let the carried reading context help you remain continuous with what has already been read, but let the current source text lead.

After reading, express what this unit gives you in three connected ways: what you understand from the text, how you respond to it as a reader, and which exact lines, if any, are worth annotating.""",
    ),
    PromptFragment(
        fragment_id="digest.context_use_guide",
        text="""- Let BookInfo orient you to the stable identity of the book; it is not source text.
- Let ReadingState hold what the reading has already carried forward. Use it for continuity, but do not let it override the current source unit.
- Let CurrentFocus show where you are and what you are reading now: path, position, object, and intent.
- Let CurrentFocus / ReadingObject be the source text for this moment of reading.
- Use OutputContract only for the required JSON shape and output discipline.""",
    ),
    PromptFragment(
        fragment_id="digest.understanding_policy",
        text="""Begin by staying with what this unit is saying. Let it settle before turning it into reaction, summary, or commentary.

Understanding is the source-faithful grasp of what this unit gives to the ongoing reading: what it establishes, changes, clarifies, contrasts, withholds, frames, or makes newly available.

Write it as the understanding you would carry forward from having read this unit, not as a memory-maintenance task and not as a visible margin note.

Let the source lead. Notice who or what appears, what happened, what the author claims, what distinction, stage, example, condition, consequence, method, evidence boundary, reader-orientation, image, scene, or tonal shift is introduced.

Add interpretation only when it is needed to preserve source-established meaning. Do not start from your theory of the passage.

Compress meaning, not wording. Do not copy the whole passage. Do not predict whether something will matter later. Do not import outside knowledge.

Use the carried reading context to understand this unit as part of the unfolding book, but keep Understanding centered on what this unit itself brings. Do not turn it into a recap of prior context.

Write Understanding so the reading can continue coherently even if the exact source text of this unit is not shown again soon.

Be context-resolvable, not standalone exhaustive. Avoid bare pronouns or vague references unless the referent is explicit in the same entry.

Usually write one Understanding entry for this unit. Split into multiple entries only when the unit contains distinct meanings that a future reading step would naturally use separately. Do not split by sentence or paragraph.

If the unit is empty or purely structural, Understanding may be empty. If the unit is author-facing or method-facing, treat it as meaningful when it declares witness position, evidence boundary, writing method, intended reader, or what the book will / will not explain.""",
    ),
    PromptFragment(
        fragment_id="digest.response_policy",
        text="""After understanding the unit, let yourself respond as a reader.

Response is the brief natural impression, feeling, thought, pressure, question, or aftertaste that remains from this moment of reading.

Use carried context naturally when it genuinely matters, but do not collapse the unit into a chapter summary, evaluator voice, or prior-context recap.

Keep Response distinct from Understanding: if the content is source-faithful meaning that should support continued reading, it belongs in Understanding.

Keep Response distinct from Annotation: if the expression is tied to a specific source span and worth showing as a visible margin-note-style output, it belongs in Annotation.""",
    ),
    PromptFragment(
        fragment_id="digest.annotation_policy",
        text="""When a line or small span genuinely asks to be marked, annotate it.

An Annotation is a visible margin-note-style response anchored to exact source text from the current unit.

It may be a line that lands with force, a margin-note thought or question, a natural connection, a distinction or turn that suddenly clarifies something, or a local trigger that feels worth marking.

Do not create an Annotation just to fill the field. It is acceptable to emit zero annotations. Default to 0-2.

Each Annotation must stay anchored to the current unit. Each `source_quote` must be an exact quote from this unit.

Choose each `source_quote` as the smallest self-sufficient span that can honestly stand as the annotation's footing.

If the unit contains multiple independently valuable local triggers, you may annotate them separately. Do not let one sharper later sentence erase an earlier framing line, premise line, or hinge line that also stands on its own.

Keep V1's wide-entry, narrow-expression stance: be willing to notice and surface a real local trigger, but do not manufacture commentary just to fill space.

If you callback to earlier material in visible content, speak naturally to the reader. Never expose internal ref ids, sentence ids, source span ids, reaction ids, or coordinate-like tokens in visible content.""",
    ),
    PromptFragment(
        fragment_id="digest.source_grounding_policy",
        text="""- `annotations[].source_quote` must be a short exact contiguous span copied from the current unit: no ellipses, no stitched fragments, no paraphrase, no translation.
- Never invent source coordinates. The runner resolves source quotes to paragraph + char-offset `SourceRef` objects after Digest returns.
- Understanding entries are grounded in the current source unit as a whole; they do not need exact source quotes.""",
    ),
    PromptFragment(
        fragment_id="digest.output_behavior_policy",
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
    """Return the source-grounding text for the live Digest XML context."""

    return _fragment_by_id("digest.source_grounding_policy").text


DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        READER_ROLE_FRAGMENT,
        _fragment_by_id("digest.current_step"),
        _fragment_by_id("digest.context_use_guide"),
        _fragment_by_id("digest.understanding_policy"),
        _fragment_by_id("digest.response_policy"),
        _fragment_by_id("digest.annotation_policy"),
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
                element_name="CurrentStep",
                prompt_fragment_ref="digest.current_step",
            ),
            PromptTemplateNode(
                element_name="ContextUseGuide",
                prompt_fragment_ref="digest.context_use_guide",
            ),
            PromptTemplateNode(
                element_name="Understanding",
                prompt_fragment_ref="digest.understanding_policy",
            ),
            PromptTemplateNode(
                element_name="Response",
                prompt_fragment_ref="digest.response_policy",
            ),
            PromptTemplateNode(
                element_name="Annotation",
                prompt_fragment_ref="digest.annotation_policy",
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
  "understanding": [
    {
      "kind": "event_or_situation|claim_or_argument|definition_or_distinction|causal_or_structural_link|character_or_relationship|emotional_or_tonal_shift|image_or_scene|local_pattern_or_thread|fact|author_or_method_frame|other",
      "content": "..."
    }
  ],
  "response": "...",
  "annotations": [
    {
      "source_quote": "...",
      "content": "...",
      "prior_link": null,
      "outside_link": null,
      "search_intent": null
    }
  ]
}""",
)


DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.understanding_contract",
    text="""`understanding` contains the source-faithful grasp of the current source unit.
Shape:
{
  "understanding": [
    {
      "kind": "event_or_situation|claim_or_argument|definition_or_distinction|causal_or_structural_link|character_or_relationship|emotional_or_tonal_shift|image_or_scene|local_pattern_or_thread|fact|author_or_method_frame|other",
      "content": "..."
    }
  ]
}
Use `content` for the understanding itself. Do not include operation-level reasons, store names, durable-memory routing, hidden state, or source coordinates.""",
)


DIGEST_RESPONSE_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.response_contract",
    text="""`response` is the reader's immediate expression after finishing the current unit: a brief natural impression, feeling, thought, pressure, question, or aftertaste.
It should not duplicate `understanding`: source-faithful meaning for continued reading belongs in `understanding`.
It should not duplicate `annotations`: span-anchored visible margin-note-style output belongs in `annotations`.""",
)


DIGEST_ANNOTATION_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.annotation_contract",
    text="""`annotations` contains visible margin-note-style output anchored to exact source text from the current unit.
Shape:
{
  "source_quote": "...",
  "content": "...",
  "prior_link": null,
  "outside_link": null,
  "search_intent": null
}
Detailed annotation-selection and source-quote behavior live under Instruction.""",
)


DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        DIGEST_OUTPUT_USE_GUIDE_FRAGMENT,
        DIGEST_RETURN_FORMAT_FRAGMENT,
        DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT,
        DIGEST_RESPONSE_CONTRACT_FRAGMENT,
        DIGEST_ANNOTATION_CONTRACT_FRAGMENT,
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
                element_name="OutputFields",
                children=(
                    PromptTemplateNode(
                        element_name="UnderstandingField",
                        prompt_fragment_ref="digest.understanding_contract",
                    ),
                    PromptTemplateNode(
                        element_name="ResponseField",
                        prompt_fragment_ref="digest.response_contract",
                    ),
                    PromptTemplateNode(
                        element_name="AnnotationField",
                        prompt_fragment_ref="digest.annotation_contract",
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
        output_contract="digest_understanding_response_annotation_json_v1",
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
    output_contract="digest_understanding_response_annotation_json_v1",
)
