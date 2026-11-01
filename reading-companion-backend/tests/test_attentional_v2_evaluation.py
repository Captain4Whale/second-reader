"""Tests for attentional_v2 Phase 8 evaluation exports and integrity checks."""

from __future__ import annotations


from src.attentional_v2.runner import _chapter_ref
from src.attentional_v2.schemas import (
    build_empty_reaction_records,
)
from src.attentional_v2.slow_cycle import (
    build_reaction_record,
)
from src.attentional_v2.storage import reaction_records_file, save_json
from src.reading_core.storage import save_book_document
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_runtime.artifacts import runtime_shell_file
from src.reading_runtime.shell_state import load_runtime_shell, save_runtime_shell


def _book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Demo Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": "demo.epub",
        },
        "chapters": [
            {
                "id": 1,
                "title": "Opening Frame",
                "chapter_number": 1,
                "level": 1,
                "paragraphs": [
                    {
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chapter1]!/4/2/2",
                        "end_cfi": "/6/2[chapter1]!/4/2/10",
                        "paragraph_index": 1,
                        "text": "Markets begin as relations among people.",
                        "block_tag": "p",
                        "heading_level": None,
                        "text_role": "body",
                    },
                    {
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chapter1]!/4/4/2",
                        "end_cfi": "/6/2[chapter1]!/4/4/12",
                        "paragraph_index": 2,
                        "text": "Later the author narrows what counts as value.",
                        "block_tag": "p",
                        "heading_level": None,
                        "text_role": "body",
                    },
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 1,
                        "text": "Markets begin as relations among people.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "start_cfi": "/6/2[chapter1]!/4/2/2",
                            "end_cfi": "/6/2[chapter1]!/4/2/10",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 36,
                        },
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 2,
                        "text": "Later the author narrows what counts as value.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "start_cfi": "/6/2[chapter1]!/4/4/2",
                            "end_cfi": "/6/2[chapter1]!/4/4/12",
                            "paragraph_index": 2,
                            "paragraph_start": 2,
                            "paragraph_end": 2,
                            "char_start": 0,
                            "char_end": 45,
                        },
                    },
                ],
            }
        ],
    }


def test_runner_chapter_ref_uses_shared_user_facing_reference() -> None:
    assert _chapter_ref({"id": 10, "title": "Chapter V. The Reconstruction Period", "chapter_number": 5}) == "Chapter 5"
    assert _chapter_ref({"id": 7, "title": "Visitors"}) == "Visitors"


def _source_ref(quote: str, paragraph_index: int) -> dict[str, object]:
    return {
        "source_span_id": f"src:c1:p{paragraph_index}@0-p{paragraph_index}@{len(quote)}",
        "source_span": {
            "start_cursor": {
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "paragraph_index": paragraph_index,
                "char_offset": 0,
            },
            "end_cursor": {
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "paragraph_index": paragraph_index,
                "char_offset": len(quote),
            },
        },
        "quote": quote,
        "role": "primary",
    }






def test_attentional_v2_integrity_checks_flag_cursor_source_ref_and_reconsolidation_drift(tmp_path):
    """The integrity report should surface structural artifact problems as hard failures."""

    output_dir = tmp_path / "output" / "demo-book"
    mechanism = AttentionalV2Mechanism()
    mechanism.initialize_artifacts(output_dir)
    save_book_document(output_dir / "public" / "book_document.json", _book_document())

    shell = load_runtime_shell(runtime_shell_file(output_dir))
    shell["cursor"] = {
        "position_kind": "span",
        "chapter_id": 1,
        "chapter_ref": "Chapter 1",
        "span_start_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 99, "char_offset": 0},
        "span_end_cursor": {"chapter_id": 1, "chapter_ref": "Chapter 1", "paragraph_index": 99, "char_offset": 1},
    }
    save_runtime_shell(runtime_shell_file(output_dir), shell)

    broken_reactions = build_empty_reaction_records()
    broken_record = build_reaction_record(
        reaction={
            "type": "discern",
            "source_quote": "Markets begin as relations among people.",
            "content": "The social framing is unstable.",
            "related_source_quotes": [],
            "search_query": "",
            "search_results": [],
        },
        primary_source_ref=_source_ref("Markets begin as relations among people.", 1),
        chapter_id=1,
        chapter_ref="Chapter 1",
        emitted_at_source_span_id="src:c1:p1@0-p1@40",
    )
    broken_record["primary_source_ref"]["source_span"]["start_cursor"]["paragraph_index"] = 99
    broken_record["primary_source_ref"]["source_span"]["end_cursor"]["paragraph_index"] = 99
    broken_reactions["records"] = [broken_record]
    save_json(reaction_records_file(output_dir), broken_reactions)

    report = mechanism.run_mechanism_integrity_checks(output_dir)
    by_code = {check["code"]: check for check in report["checks"]}

    assert report["passed"] is False
    assert by_code["runtime_cursor_source_span_resolves"]["status"] == "fail"
    assert by_code["reactions_have_resolvable_source_refs"]["status"] == "fail"
    assert "reconsolidation_links_are_append_only" not in by_code


def test_new_evaluation_rejects_private_reactions_without_product(tmp_path):
    import pytest
    from src.attentional_v2.evaluation import _normalized_reactions
    with pytest.raises(ValueError, match="Product-accepted Marginalia"):
        _normalized_reactions(tmp_path)
