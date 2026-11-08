"""Reader role prompt fragment for attentional_v2."""

from __future__ import annotations

from src.prompts.releases import prompt_text

from .assembly import PromptFragment, PromptFragmentRegistry


READER_ROLE_FRAGMENT = PromptFragment(
    fragment_id="reader.role",
    text=prompt_text('reader_role', 'v1', 'reader.role'),
)


READER_ROLE_FRAGMENT_REGISTRY = PromptFragmentRegistry([READER_ROLE_FRAGMENT])


__all__ = [
    "READER_ROLE_FRAGMENT",
    "READER_ROLE_FRAGMENT_REGISTRY",
]
