"""Prompt registry package for attentional_v2."""

from .assembly import (
    PromptFragment,
    PromptFragmentRegistry,
    PromptTemplateNode,
    render_prompt_template_xml,
    render_read_xml_prompt_example,
)
from .registry import (
    ATTENTIONAL_V2_PROMPTS,
    ATTENTIONAL_V2_PROMPTSET_VERSION,
    ATTENTIONAL_V2_PROMPT_REGISTRY,
    BRIDGE_RESOLUTION_PROMPT_VERSION,
    CHAPTER_CONSOLIDATION_PROMPT_VERSION,
    NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION,
    READ_UNIT_PROMPT_VERSION,
    RECONSOLIDATION_PROMPT_VERSION,
    REFLECTIVE_PROMOTION_PROMPT_VERSION,
    SURVEY_CHAPTER_ZONE_PROMPT_VERSION,
    AttentionalV2PromptSet,
    PromptDefinition,
    PromptRegistry,
)
from .read_unit import READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS, READ_UNIT_SYSTEM_PROMPT


__all__ = [
    "ATTENTIONAL_V2_PROMPTS",
    "ATTENTIONAL_V2_PROMPTSET_VERSION",
    "ATTENTIONAL_V2_PROMPT_REGISTRY",
    "SURVEY_CHAPTER_ZONE_PROMPT_VERSION",
    "NAVIGATE_CHOOSE_NEXT_UNIT_PROMPT_VERSION",
    "READ_UNIT_PROMPT_VERSION",
    "READ_UNIT_ROLE_AND_INSTRUCTION_FRAGMENTS",
    "READ_UNIT_SYSTEM_PROMPT",
    "BRIDGE_RESOLUTION_PROMPT_VERSION",
    "REFLECTIVE_PROMOTION_PROMPT_VERSION",
    "RECONSOLIDATION_PROMPT_VERSION",
    "CHAPTER_CONSOLIDATION_PROMPT_VERSION",
    "AttentionalV2PromptSet",
    "PromptDefinition",
    "PromptRegistry",
    "PromptFragment",
    "PromptFragmentRegistry",
    "PromptTemplateNode",
    "render_prompt_template_xml",
    "render_read_xml_prompt_example",
]
