"""Node-level prompt assembly for attentional_v2.

This module sits above low-level XML template rendering. It knows how to
assemble one node prompt spec into model-facing text and audit metadata, but it
does not know how to read runtime state or call an LLM.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .assembly import PromptFragmentRegistry, PromptTemplateNode, render_prompt_template_xml


@dataclass(frozen=True)
class PromptAssemblySpec:
    """Complete prompt assembly contract for one LLM node."""

    spec_id: str
    owner_node: str
    prompt_version: str
    promptset_version: str
    template_nodes: Sequence[PromptTemplateNode]
    fragment_registry: PromptFragmentRegistry
    required_slots: tuple[str, ...]
    output_contract: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "template_nodes", tuple(self.template_nodes))
        object.__setattr__(self, "required_slots", tuple(self.required_slots))
        for field_name in ("spec_id", "owner_node", "prompt_version", "promptset_version", "output_contract"):
            value = str(getattr(self, field_name)).strip()
            if not value:
                raise ValueError(f"Prompt assembly spec {field_name} must not be empty")
            object.__setattr__(self, field_name, value)
        if not self.template_nodes:
            raise ValueError("Prompt assembly spec template_nodes must not be empty")
        cleaned_slots: list[str] = []
        for slot in self.required_slots:
            cleaned = slot.strip()
            if not cleaned:
                raise ValueError("Prompt assembly spec required_slots must not contain empty values")
            cleaned_slots.append(cleaned)
        if len(set(cleaned_slots)) != len(cleaned_slots):
            raise ValueError("Prompt assembly spec required_slots must be unique")
        object.__setattr__(self, "required_slots", tuple(cleaned_slots))


@dataclass(frozen=True)
class PromptAssemblyResult:
    """Rendered prompt plus assembly metadata for audit and tests."""

    rendered_text: str
    spec_id: str
    owner_node: str
    prompt_version: str
    promptset_version: str
    output_contract: str
    rendered_blocks: tuple[str, ...]
    used_fragment_ids: tuple[str, ...]
    used_slot_names: tuple[str, ...]


class PromptAssembler:
    """Assemble model-facing prompts from node-specific prompt specs."""

    def assemble(
        self,
        spec: PromptAssemblySpec,
        *,
        slot_values: Mapping[str, str],
    ) -> PromptAssemblyResult:
        missing_required = [
            required_slot
            for required_slot in spec.required_slots
            if required_slot not in slot_values
        ]
        if missing_required:
            raise KeyError(
                "Missing required prompt assembly slot(s): "
                + ", ".join(missing_required)
            )

        rendered_text = render_prompt_template_xml(
            spec.template_nodes,
            registry=spec.fragment_registry,
            slot_values=slot_values,
        )
        return PromptAssemblyResult(
            rendered_text=rendered_text,
            spec_id=spec.spec_id,
            owner_node=spec.owner_node,
            prompt_version=spec.prompt_version,
            promptset_version=spec.promptset_version,
            output_contract=spec.output_contract,
            rendered_blocks=tuple(node.element_name for node in spec.template_nodes),
            used_fragment_ids=tuple(_collect_prompt_fragment_refs(spec.template_nodes)),
            used_slot_names=tuple(_collect_value_slots(spec.template_nodes)),
        )


def _collect_prompt_fragment_refs(nodes: Sequence[PromptTemplateNode]) -> list[str]:
    refs: list[str] = []
    for node in nodes:
        if node.prompt_fragment_ref is not None:
            refs.append(node.prompt_fragment_ref.strip())
        refs.extend(_collect_prompt_fragment_refs(node.children))
    return _dedupe_preserve_order(refs)


def _collect_value_slots(nodes: Sequence[PromptTemplateNode]) -> list[str]:
    slots: list[str] = []
    for node in nodes:
        if node.value_slot is not None:
            slots.append(node.value_slot.strip())
        slots.extend(_collect_value_slots(node.children))
    return _dedupe_preserve_order(slots)


def _dedupe_preserve_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
