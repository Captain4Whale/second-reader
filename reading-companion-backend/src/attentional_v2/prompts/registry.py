"""Prompt registry for attentional_v2."""

from __future__ import annotations

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT

from .ingest import INGEST_PROMPT, INGEST_PROMPT_VERSION
from .digest import DIGEST_PROMPT, DIGEST_PROMPT_VERSION
from .chapter_zone import CHAPTER_ZONE_PROMPT, CHAPTER_ZONE_PROMPT_VERSION
from .types import AttentionalV2PromptSet, PromptDefinition, PromptRegistry, build_legacy_prompt_set


ATTENTIONAL_V2_PROMPTSET_VERSION = "attentional_v2-phase6-v84"


ATTENTIONAL_V2_PROMPT_REGISTRY = PromptRegistry(
    [
        CHAPTER_ZONE_PROMPT,
        INGEST_PROMPT,
        DIGEST_PROMPT,
    ]
)


ATTENTIONAL_V2_PROMPTS: AttentionalV2PromptSet = build_legacy_prompt_set(
    ATTENTIONAL_V2_PROMPT_REGISTRY,
    language_output_contract=LANGUAGE_OUTPUT_CONTRACT,
    promptset_version=ATTENTIONAL_V2_PROMPTSET_VERSION,
)


__all__ = [
    "ATTENTIONAL_V2_PROMPTS",
    "ATTENTIONAL_V2_PROMPTSET_VERSION",
    "ATTENTIONAL_V2_PROMPT_REGISTRY",
    "CHAPTER_ZONE_PROMPT_VERSION",
    "INGEST_PROMPT_VERSION",
    "DIGEST_PROMPT_VERSION",
    "AttentionalV2PromptSet",
    "PromptDefinition",
    "PromptRegistry",
]
