"""Prompt definition and registry types for attentional_v2."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptDefinition:
    """One managed prompt pair owned by an attentional_v2 LLM call."""

    prompt_id: str
    version: str
    owner_node: str
    status: str
    purpose: str
    system_prompt: str
    user_prompt_template: str
    required_inputs: tuple[str, ...]
    output_contract: str


class PromptRegistry:
    """Registry for attentional_v2 prompt definitions."""

    def __init__(self, prompts: Iterable[PromptDefinition]) -> None:
        self._prompts: dict[str, PromptDefinition] = {}
        for prompt in prompts:
            prompt_id = prompt.prompt_id.strip()
            if not prompt_id:
                raise ValueError("Prompt id must not be empty")
            if prompt_id in self._prompts:
                raise ValueError(f"Duplicate prompt id: {prompt_id}")
            self._prompts[prompt_id] = prompt

    def get(self, prompt_id: str) -> PromptDefinition:
        prompt_id = prompt_id.strip()
        if not prompt_id:
            raise ValueError("Prompt id must not be empty")
        try:
            return self._prompts[prompt_id]
        except KeyError as exc:
            raise KeyError(f"Unknown prompt id: {prompt_id}") from exc

    def list(self) -> tuple[PromptDefinition, ...]:
        return tuple(self._prompts.values())

    def __iter__(self) -> Iterator[PromptDefinition]:
        return iter(self._prompts.values())


@dataclass(frozen=True)
class AttentionalV2PromptSet:
    """Legacy prompt bundle projection used by current runtime call sites."""

    language_output_contract: str
    promptset_version: str
    survey_chapter_zone_version: str
    survey_chapter_zone_system: str
    survey_chapter_zone_prompt: str
    ingest_version: str
    ingest_system: str
    ingest_prompt: str
    digest_version: str
    digest_system: str
    digest_prompt: str
    bridge_resolution_version: str
    bridge_resolution_system: str
    bridge_resolution_prompt: str
    reflective_promotion_version: str
    reflective_promotion_system: str
    reflective_promotion_prompt: str
    reconsolidation_version: str
    reconsolidation_system: str
    reconsolidation_prompt: str
    chapter_consolidation_version: str
    chapter_consolidation_system: str
    chapter_consolidation_prompt: str


def build_legacy_prompt_set(
    registry: PromptRegistry,
    *,
    language_output_contract: str,
    promptset_version: str,
) -> AttentionalV2PromptSet:
    """Build the legacy dataclass from PromptRegistry definitions."""

    survey = registry.get("attentional_v2.survey_chapter_zone")
    ingest = registry.get("attentional_v2.ingest")
    digest = registry.get("attentional_v2.digest")
    bridge = registry.get("attentional_v2.bridge_resolution")
    reflective = registry.get("attentional_v2.reflective_promotion")
    reconsolidation = registry.get("attentional_v2.reconsolidation")
    chapter = registry.get("attentional_v2.chapter_consolidation")
    return AttentionalV2PromptSet(
        language_output_contract=language_output_contract,
        promptset_version=promptset_version,
        survey_chapter_zone_version=survey.version,
        survey_chapter_zone_system=survey.system_prompt,
        survey_chapter_zone_prompt=survey.user_prompt_template,
        ingest_version=ingest.version,
        ingest_system=ingest.system_prompt,
        ingest_prompt=ingest.user_prompt_template,
        digest_version=digest.version,
        digest_system=digest.system_prompt,
        digest_prompt=digest.user_prompt_template,
        bridge_resolution_version=bridge.version,
        bridge_resolution_system=bridge.system_prompt,
        bridge_resolution_prompt=bridge.user_prompt_template,
        reflective_promotion_version=reflective.version,
        reflective_promotion_system=reflective.system_prompt,
        reflective_promotion_prompt=reflective.user_prompt_template,
        reconsolidation_version=reconsolidation.version,
        reconsolidation_system=reconsolidation.system_prompt,
        reconsolidation_prompt=reconsolidation.user_prompt_template,
        chapter_consolidation_version=chapter.version,
        chapter_consolidation_system=chapter.system_prompt,
        chapter_consolidation_prompt=chapter.user_prompt_template,
    )
