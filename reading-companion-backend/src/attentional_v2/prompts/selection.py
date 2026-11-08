"""Explicit selection of published Digest text using the current XML/wire contract."""

from dataclasses import replace
import json

from src.prompts.integrity import LOCK, release_receipt
from src.prompts.releases import BACKEND, read_texts
from . import digest as template
from .assembler import PromptAssembler
from .assembly import PromptFragment, PromptFragmentRegistry


def render_selected_digest_prompt(version: str, **inputs):
    """Select immutable text, including dependencies; never mutate module globals.

    Releases must use the current Digest XML slots and output contract. A new
    topology or wire contract needs a separate renderer, not an implicit fallback.
    """
    releases = json.loads(LOCK.read_text())["releases"]
    if not version.startswith("attentional_v2.digest.") or version not in releases:
        raise ValueError(f"Unknown published Digest version: {version}")
    entry = releases[version]
    receipt = release_receipt(entry)
    if receipt["release_sha256"] != entry["release_sha256"]:
        raise ValueError(f"Published Digest release changed: {version}")
    texts = {}
    for path in entry["files"]:
        texts.update(read_texts(BACKEND / path))
    if version == template.DIGEST_PROMPT_VERSION:
        return texts["transport_system"], template.render_digest_prompt_xml(**inputs)
    spec = template.build_digest_prompt_assembly_spec(
        current_unit_source=inputs.get("current_unit_source"),
        current_unit_sentences=inputs.get("current_unit_sentences"),
    )
    spec = replace(
        spec, prompt_version=version,
        fragment_registry=PromptFragmentRegistry([
            PromptFragment(fragment_id=f.fragment_id, text=texts[f.fragment_id])
            for f in spec.fragment_registry.list()
        ]),
    )
    source = inputs.get("current_unit_source")
    chapter = inputs["chapter_title"]
    memory = inputs.get("reading_memory_lines")
    result = PromptAssembler().assemble(spec, slot_values={
        "book_identity": template._json_prompt_payload({
            "book_title": inputs["book_title"], "author": inputs["author"],
        }),
        "reading_memory": "\n".join(memory) if memory is not None else "\n".join(
            template._recent_memory_texts_for_digest(inputs.get("recent_reading_memory"))
        ),
        "reading_path": template._json_prompt_object({"mode": "mainline"}),
        "reading_position": template._json_prompt_object(template._compact_prompt_object({
            "chapter_title": template._clean_prompt_value(chapter),
            "human_position": template._human_position(chapter_title=chapter, current_unit_source=source),
        })),
        "reading_intent": template._json_prompt_object(template._reading_intent_payload()),
        "language_contract": texts["LANGUAGE_OUTPUT_CONTRACT"].format(
            output_language_name=template._clean_prompt_value(inputs["output_language_name"])
        ),
    })
    return texts["transport_system"], result
