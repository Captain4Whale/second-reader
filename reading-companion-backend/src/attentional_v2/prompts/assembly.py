"""Prompt XML assembly helpers for attentional_v2."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class PromptFragment:
    """Fixed prompt text addressed by an assembly-layer id."""

    fragment_id: str
    text: str


class PromptFragmentRegistry:
    """Resolve fixed prompt fragments without leaking ids into model-facing text."""

    def __init__(self, fragments: Iterable[PromptFragment]) -> None:
        self._fragments: dict[str, PromptFragment] = {}
        for fragment in fragments:
            fragment_id = fragment.fragment_id.strip()
            if not fragment_id:
                raise ValueError("Prompt fragment id must not be empty")
            if fragment_id in self._fragments:
                raise ValueError(f"Duplicate prompt fragment id: {fragment_id}")
            self._fragments[fragment_id] = PromptFragment(fragment_id=fragment_id, text=fragment.text)

    def resolve(self, fragment_id: str) -> str:
        fragment_id = fragment_id.strip()
        if not fragment_id:
            raise ValueError("Prompt fragment id must not be empty")
        try:
            return self._fragments[fragment_id].text
        except KeyError as exc:
            raise KeyError(f"Unknown prompt fragment id: {fragment_id}") from exc


@dataclass(frozen=True)
class PromptTemplateNode:
    """Static template node for model-facing XML prompt assembly.

    Template nodes may point at prompt fragment references or dynamic value
    slots, but the rendered prompt only contains XML elements and resolved text.
    """

    element_name: str
    prompt_fragment_ref: str | None = None
    value_slot: str | None = None
    literal_value: str | None = None
    children: Sequence["PromptTemplateNode"] = ()
    skip_if_empty: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "children", tuple(self.children))


def _validate_xml_element_name(element_name: str) -> str:
    cleaned = element_name.strip()
    if not cleaned:
        raise ValueError("Prompt XML element name must not be empty")
    if any(char in cleaned for char in "<>/ \t\r\n"):
        raise ValueError(f"Invalid prompt XML element name: {element_name}")
    return cleaned


def _escape_prompt_text(text: str, *, indent_level: int) -> str:
    indent = "  " * indent_level
    escaped = escape(text, quote=False)
    return "\n".join(f"{indent}{line}" if line else "" for line in escaped.splitlines())


def _render_prompt_template_node(
    node: PromptTemplateNode,
    *,
    registry: PromptFragmentRegistry,
    slot_values: Mapping[str, str],
    indent_level: int,
) -> str:
    element_name = _validate_xml_element_name(node.element_name)
    content_sources = sum(
        [
            node.prompt_fragment_ref is not None,
            node.value_slot is not None,
            node.literal_value is not None,
            bool(node.children),
        ]
    )
    if content_sources > 1:
        raise ValueError(f"Prompt template node <{element_name}> must use only one content source")

    indent = "  " * indent_level
    if node.prompt_fragment_ref is not None:
        raw_text = registry.resolve(node.prompt_fragment_ref)
        if not raw_text and node.skip_if_empty:
            return ""
        return (
            f"{indent}<{element_name}>\n"
            f"{_escape_prompt_text(raw_text, indent_level=indent_level + 1)}\n"
            f"{indent}</{element_name}>"
        )

    if node.value_slot is not None:
        value_slot = node.value_slot.strip()
        if not value_slot:
            raise ValueError(f"Prompt template node <{element_name}> value_slot must not be empty")
        try:
            raw_text = slot_values[value_slot]
        except KeyError as exc:
            raise KeyError(f"Missing prompt template value slot: {value_slot}") from exc
        if not raw_text and node.skip_if_empty:
            return ""
        return (
            f"{indent}<{element_name}>\n"
            f"{_escape_prompt_text(raw_text, indent_level=indent_level + 1)}\n"
            f"{indent}</{element_name}>"
        )

    if node.literal_value is not None:
        if not node.literal_value and node.skip_if_empty:
            return ""
        return (
            f"{indent}<{element_name}>\n"
            f"{_escape_prompt_text(node.literal_value, indent_level=indent_level + 1)}\n"
            f"{indent}</{element_name}>"
        )

    if node.children:
        rendered_children = [
            rendered
            for child in node.children
            if (
                rendered := _render_prompt_template_node(
                    child,
                    registry=registry,
                    slot_values=slot_values,
                    indent_level=indent_level + 1,
                )
            )
        ]
        if not rendered_children and node.skip_if_empty:
            return ""
        return f"{indent}<{element_name}>\n" + "\n".join(rendered_children) + f"\n{indent}</{element_name}>"

    if node.skip_if_empty:
        return ""
    return f"{indent}<{element_name}></{element_name}>"


def render_prompt_template_xml(
    nodes: Sequence[PromptTemplateNode],
    *,
    registry: PromptFragmentRegistry,
    slot_values: Mapping[str, str],
) -> str:
    """Render sibling XML prompt nodes with all fragment refs and value slots resolved."""

    return "\n\n".join(
        rendered
        for node in nodes
        if (
            rendered := _render_prompt_template_node(
                node,
                registry=registry,
                slot_values=slot_values,
                indent_level=0,
            )
        )
    )

READ_XML_EXAMPLE_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        PromptFragment(
            fragment_id="attentional_v2.read.role_and_instruction.example.v1",
            text="Fixed Read role and instruction text resolved by the prompt assembly layer.",
        )
    ]
)


READ_XML_EXAMPLE_TEMPLATE = (
    PromptTemplateNode(
        element_name="RoleAndInstruction",
        children=(
            PromptTemplateNode(
                element_name="Instruction",
                prompt_fragment_ref="attentional_v2.read.role_and_instruction.example.v1",
            ),
        ),
    ),
    PromptTemplateNode(element_name="BookAndChapterInfo", value_slot="book_and_chapter_info"),
    PromptTemplateNode(element_name="ReadingState", value_slot="reading_state"),
    PromptTemplateNode(element_name="CurrentFocus", value_slot="current_focus"),
    PromptTemplateNode(element_name="OutputContract", value_slot="output_contract"),
)


def render_read_xml_prompt_example(
    *,
    book_and_chapter_info: str,
    reading_state: str,
    current_focus: str,
    output_contract: str,
    registry: PromptFragmentRegistry = READ_XML_EXAMPLE_FRAGMENT_REGISTRY,
) -> str:
    """Render the future Read XML shape without connecting it to the live Read node."""

    return render_prompt_template_xml(
        READ_XML_EXAMPLE_TEMPLATE,
        registry=registry,
        slot_values={
            "book_and_chapter_info": book_and_chapter_info,
            "reading_state": reading_state,
            "current_focus": current_focus,
            "output_contract": output_contract,
        },
    )
