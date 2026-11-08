"""Deterministic, invented inputs for byte-level prompt migration acceptance."""

import hashlib
import json


def rendered_cases():
    from src.attentional_v2.prompts.registry import ATTENTIONAL_V2_PROMPTS as p
    from src.attentional_v2.prompts.digest import render_digest_prompt_xml
    from src.attentional_v2.prompts.ingest import render_ingest_prompt_xml

    cases = {"chapter_zone": [p.chapter_zone_system, p.chapter_zone_prompt]}
    for language in ("中文", "English"):
        for shape in ("empty", "sentences", "paragraphs"):
            source = {} if shape != "paragraphs" else {
                "source_text": "Invented <text> & café.\n第二段。",
                "paragraph_slices": [
                    {"paragraph_index": 1, "text": "Invented <text> & café."},
                    {"paragraph_index": 2, "text": "第二段。"},
                ],
            }
            digest = render_digest_prompt_xml(
                book_title="Invented & Book", author="Test Author", chapter_title="Chapter <1>",
                output_language_name=language, reading_memory_lines=["Prior invented memory.", "前文。"],
                current_unit_source=source,
                current_unit_sentences=[{"text": "A fictional sentence."}] if shape == "sentences" else [],
            )
            cases[f"digest/{language}/{shape}"] = [p.digest_system, digest.rendered_text]
    for shape, content in (("object", {"source_text": "Invented & preview"}), ("paragraphs", {
        "paragraph_slices": [{"paragraph_index": 3, "text": "Invented <preview>", "text_role": "body", "start_char": 0, "end_char": 18}],
    })):
        ingest = render_ingest_prompt_xml(book_title="Invented Book", author="Test Author",
            current_view_position={"chapter_id": 1}, current_view_content=content)
        cases[f"ingest/{shape}"] = [p.ingest_system, ingest.rendered_text]
    return cases


def render_hashes():
    return {key: hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            for key, value in rendered_cases().items()}
