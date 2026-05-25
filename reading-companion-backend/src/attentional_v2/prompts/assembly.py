"""Prompt XML assembly helpers for attentional_v2."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
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
class PromptXmlNode:
    """Template node for model-facing XML prompt assembly.

    The assembly layer may point at fragment ids, but the rendered prompt only
    contains XML tags and resolved text.
    """

    tag: str
    fragment_id: str | None = None
    value: str | None = None
    children: Sequence["PromptXmlNode"] = ()
    skip_if_empty: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "children", tuple(self.children))


def _validate_xml_tag(tag: str) -> str:
    cleaned = tag.strip()
    if not cleaned:
        raise ValueError("Prompt XML tag must not be empty")
    if any(char in cleaned for char in "<>/ \t\r\n"):
        raise ValueError(f"Invalid prompt XML tag: {tag}")
    return cleaned


def _escape_prompt_text(text: str, *, indent_level: int) -> str:
    indent = "  " * indent_level
    escaped = escape(text, quote=False)
    return "\n".join(f"{indent}{line}" if line else "" for line in escaped.splitlines())


def _render_prompt_xml_node(node: PromptXmlNode, *, registry: PromptFragmentRegistry, indent_level: int) -> str:
    tag = _validate_xml_tag(node.tag)
    content_sources = sum(
        [
            node.fragment_id is not None,
            node.value is not None,
            bool(node.children),
        ]
    )
    if content_sources > 1:
        raise ValueError(f"Prompt XML node <{tag}> must use only one content source")

    indent = "  " * indent_level
    if node.fragment_id is not None:
        raw_text = registry.resolve(node.fragment_id)
        if not raw_text and node.skip_if_empty:
            return ""
        return f"{indent}<{tag}>\n{_escape_prompt_text(raw_text, indent_level=indent_level + 1)}\n{indent}</{tag}>"

    if node.value is not None:
        if not node.value and node.skip_if_empty:
            return ""
        return f"{indent}<{tag}>\n{_escape_prompt_text(node.value, indent_level=indent_level + 1)}\n{indent}</{tag}>"

    if node.children:
        rendered_children = [
            rendered
            for child in node.children
            if (rendered := _render_prompt_xml_node(child, registry=registry, indent_level=indent_level + 1))
        ]
        if not rendered_children and node.skip_if_empty:
            return ""
        return f"{indent}<{tag}>\n" + "\n".join(rendered_children) + f"\n{indent}</{tag}>"

    if node.skip_if_empty:
        return ""
    return f"{indent}<{tag}></{tag}>"


def render_prompt_xml(nodes: Sequence[PromptXmlNode], *, registry: PromptFragmentRegistry) -> str:
    """Render sibling XML prompt nodes with all fragment ids resolved."""

    return "\n\n".join(
        rendered
        for node in nodes
        if (rendered := _render_prompt_xml_node(node, registry=registry, indent_level=0))
    )

READ_XML_EXAMPLE_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        PromptFragment(
            fragment_id="attentional_v2.read.role_and_instruction.example.v1",
            text="Fixed Read role and instruction text resolved by the prompt assembly layer.",
        )
    ]
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

    return render_prompt_xml(
        [
            PromptXmlNode(
                tag="RoleAndInstruction",
                children=[
                    PromptXmlNode(
                        tag="Instruction",
                        fragment_id="attentional_v2.read.role_and_instruction.example.v1",
                    )
                ],
            ),
            PromptXmlNode(tag="BookAndChapterInfo", value=book_and_chapter_info),
            PromptXmlNode(tag="ReadingState", value=reading_state),
            PromptXmlNode(tag="CurrentFocus", value=current_focus),
            PromptXmlNode(tag="OutputContract", value=output_contract),
        ],
        registry=registry,
    )
