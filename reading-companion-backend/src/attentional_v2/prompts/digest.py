"""Prompt definition for attentional_v2 digest."""

from __future__ import annotations

from src.prompts.releases import prompt_text

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


DIGEST_PROMPT_VERSION = "attentional_v2.digest.v24"
DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.digest.xml.v24"
DIGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v84"
DIGEST_XML_TRANSPORT_SYSTEM_PROMPT = prompt_text('digest', 'v24', 'transport_system')


# These fragments define the live Digest reader action and its XML Instruction blocks.
DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS = (
    READER_ROLE_FRAGMENT,
    PromptFragment(
        fragment_id="digest.current_step",
        text=prompt_text('digest', 'v24', 'digest.current_step'),
    ),
    PromptFragment(
        fragment_id="digest.context_use_guide",
        text=prompt_text('digest', 'v24', 'digest.context_use_guide'),
    ),
    PromptFragment(
        fragment_id="digest.understanding_policy",
        text=prompt_text('digest', 'v24', 'digest.understanding_policy'),
    ),
    PromptFragment(
        fragment_id="digest.response_policy",
        text=prompt_text('digest', 'v24', 'digest.response_policy'),
    ),
    PromptFragment(
        fragment_id="digest.marginalia_policy",
        text=prompt_text('digest', 'v24', 'digest.marginalia_policy'),
    ),
    PromptFragment(
        fragment_id="digest.source_grounding_policy",
        text=prompt_text('digest', 'v24', 'digest.source_grounding_policy'),
    ),
    PromptFragment(
        fragment_id="digest.output_behavior_policy",
        text=prompt_text('digest', 'v24', 'digest.output_behavior_policy'),
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
        _fragment_by_id("digest.marginalia_policy"),
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
                element_name="Marginalia",
                prompt_fragment_ref="digest.marginalia_policy",
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
    """Project Recent Reading Memory to fallback ReadingMemory lines."""

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


DIGEST_READING_MEMORY_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReadingMemory",
        value_slot="reading_memory",
    ),
)


def render_digest_reading_memory_xml(
    *,
    recent_reading_memory: Mapping[str, object] | None = None,
    reading_memory_lines: list[str] | None = None,
) -> str:
    """Render the top-level ReadingMemory XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_READING_MEMORY_TEMPLATE,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "reading_memory": "\n".join(reading_memory_lines)
            if reading_memory_lines is not None
            else "\n".join(_recent_memory_texts_for_digest(recent_reading_memory)),
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
    text=prompt_text('digest', 'v24', 'digest.output_use_guide'),
)


DIGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="digest.return_format_contract",
    text=prompt_text('digest', 'v24', 'digest.return_format_contract'),
)


DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.understanding_contract",
    text=prompt_text('digest', 'v24', 'digest.understanding_contract'),
)


DIGEST_RESPONSE_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.response_contract",
    text=prompt_text('digest', 'v24', 'digest.response_contract'),
)


DIGEST_MARGINALIA_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.marginalia_contract",
    text=prompt_text('digest', 'v24', 'digest.marginalia_contract'),
)


DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        DIGEST_OUTPUT_USE_GUIDE_FRAGMENT,
        DIGEST_RETURN_FORMAT_FRAGMENT,
        DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT,
        DIGEST_RESPONSE_CONTRACT_FRAGMENT,
        DIGEST_MARGINALIA_CONTRACT_FRAGMENT,
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
                        element_name="MarginaliaField",
                        prompt_fragment_ref="digest.marginalia_contract",
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
        *DIGEST_READING_MEMORY_TEMPLATE,
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
            "reading_memory",
            "reading_path",
            "reading_position",
            "reading_intent",
            "language_contract",
        ),
        output_contract="digest_understanding_response_marginalia_json_v8",
    )


def render_digest_prompt_xml(
    *,
    book_title: str,
    author: str,
    chapter_title: str,
    output_language_name: str,
    recent_reading_memory: Mapping[str, object] | None = None,
    reading_memory_lines: list[str] | None = None,
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
            "reading_memory": "\n".join(reading_memory_lines)
            if reading_memory_lines is not None
            else "\n".join(_recent_memory_texts_for_digest(recent_reading_memory)),
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
    user_prompt_template=prompt_text('digest', 'v24', 'user_prompt_template'),
    required_inputs=(
        "book_identity",
        "reading_memory",
        "reading_path",
        "reading_position",
        "reading_intent",
        "language_contract",
    ),
    output_contract="digest_understanding_response_marginalia_json_v8",
)
