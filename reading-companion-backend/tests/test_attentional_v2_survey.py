"""Tests for attentional_v2 orientation-only survey artifacts."""

from __future__ import annotations

import json

from src.attentional_v2 import survey as survey_module
from src.attentional_v2.survey import build_book_survey, write_book_survey_artifacts
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_runtime.artifacts import mechanism_manifest_file


def _sample_book_document() -> dict[str, object]:
    return {
        "metadata": {
            "book": "Value in Motion",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": "demo.epub",
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "level": 1,
                "chapter_heading": {"text": "CHAPTER 1\nValue and Exchange"},
                "paragraphs": [
                    {
                        "text": "CHAPTER 1",
                        "paragraph_index": 1,
                        "text_role": "chapter_heading",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/4[chapter-1]!/4/2)",
                        "end_cfi": "epubcfi(/6/4[chapter-1]!/4/2)",
                    },
                    {
                        "text": "Value and Exchange",
                        "paragraph_index": 2,
                        "text_role": "chapter_heading",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/4[chapter-1]!/4/4)",
                        "end_cfi": "epubcfi(/6/4[chapter-1]!/4/4)",
                    },
                    {
                        "text": "People want things from other people. Markets arise in relationships.",
                        "paragraph_index": 3,
                        "text_role": "body",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/4[chapter-1]!/4/6)",
                        "end_cfi": "epubcfi(/6/4[chapter-1]!/4/6)",
                    },
                    {
                        "text": "The covert calculator",
                        "paragraph_index": 4,
                        "text_role": "section_heading",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/4[chapter-1]!/4/8)",
                        "end_cfi": "epubcfi(/6/4[chapter-1]!/4/8)",
                    },
                    {
                        "text": "People compare costs in secret. This creates friction.",
                        "paragraph_index": 5,
                        "text_role": "body",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/4[chapter-1]!/4/10)",
                        "end_cfi": "epubcfi(/6/4[chapter-1]!/4/10)",
                    },
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 1,
                        "text": "CHAPTER 1",
                        "text_role": "chapter_heading",
                        "locator": {"paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 9},
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 2,
                        "text": "Value and Exchange",
                        "text_role": "chapter_heading",
                        "locator": {"paragraph_index": 2, "paragraph_start": 2, "paragraph_end": 2, "char_start": 0, "char_end": 18},
                    },
                    {
                        "sentence_id": "c1-s3",
                        "sentence_index": 3,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 3,
                        "text": "People want things from other people.",
                        "text_role": "body",
                        "locator": {"paragraph_index": 3, "paragraph_start": 3, "paragraph_end": 3, "char_start": 0, "char_end": 37},
                    },
                    {
                        "sentence_id": "c1-s4",
                        "sentence_index": 4,
                        "sentence_in_paragraph": 2,
                        "paragraph_index": 3,
                        "text": "Markets arise in relationships.",
                        "text_role": "body",
                        "locator": {"paragraph_index": 3, "paragraph_start": 3, "paragraph_end": 3, "char_start": 38, "char_end": 69},
                    },
                    {
                        "sentence_id": "c1-s5",
                        "sentence_index": 5,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 4,
                        "text": "The covert calculator",
                        "text_role": "section_heading",
                        "locator": {"paragraph_index": 4, "paragraph_start": 4, "paragraph_end": 4, "char_start": 0, "char_end": 22},
                    },
                    {
                        "sentence_id": "c1-s6",
                        "sentence_index": 6,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 5,
                        "text": "People compare costs in secret.",
                        "text_role": "body",
                        "locator": {"paragraph_index": 5, "paragraph_start": 5, "paragraph_end": 5, "char_start": 0, "char_end": 31},
                    },
                    {
                        "sentence_id": "c1-s7",
                        "sentence_index": 7,
                        "sentence_in_paragraph": 2,
                        "paragraph_index": 5,
                        "text": "This creates friction.",
                        "text_role": "body",
                        "locator": {"paragraph_index": 5, "paragraph_start": 5, "paragraph_end": 5, "char_start": 32, "char_end": 54},
                    },
                ],
            },
            {
                "id": 2,
                "title": "Appendix: Value Notes",
                "chapter_number": None,
                "level": 1,
                "paragraphs": [],
                "sentences": [
                    {
                        "sentence_id": "c2-s1",
                        "sentence_index": 1,
                        "sentence_in_paragraph": 1,
                        "paragraph_index": 1,
                        "text": "Appendix: Value Notes",
                        "text_role": "chapter_heading",
                        "locator": {"paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 21},
                    }
                ],
            },
        ],
    }


def test_build_book_survey_stays_orientation_only():
    """Survey output should keep only boundaries, openings/closings, pivots, and tentative seeds."""

    survey = build_book_survey(
        _sample_book_document(),  # type: ignore[arg-type]
        policy_snapshot={"survey_mode": "orientation_only"},
    )

    assert survey["status"] == "orientation_only"
    assert survey["book_frame"]["total_chapters"] == 2
    assert survey["chapter_map"][0]["opening_sentences"][0]["sentence_id"] == "c1-s1"
    assert survey["chapter_map"][0]["closing_sentences"][-1]["sentence_id"] == "c1-s7"
    assert survey["chapter_map"][0]["pivot_headings"] == ["The covert calculator"]
    assert survey["chapter_map"][1]["structural_role_guess"] == "back_matter"
    assert survey["chapter_map"][0]["chapter_zone"] == "main_body"
    assert survey["chapter_map"][1]["chapter_zone"] == "auxiliary"
    assert survey["reading_plan"]["mode"] == "body_first"
    assert survey["reading_plan"]["mainline_chapter_ids"] == [1]
    assert survey["reading_plan"]["deferred_chapter_ids"] == []
    assert "Markets arise in relationships." not in {
        sentence["text"]
        for chapter in survey["chapter_map"]
        for sentence in chapter.get("opening_sentences", []) + chapter.get("closing_sentences", [])
    }
    assert survey["initial_motif_seeds"][0]["confidence"] == "tentative"


def test_write_book_survey_artifacts_persists_survey_and_revisit_index(tmp_path):
    """Survey helpers should write the orientation artifacts under the mechanism artifact root."""

    output_dir = tmp_path / "output" / "demo-book"
    mechanism = AttentionalV2Mechanism()
    mechanism.initialize_artifacts(output_dir)

    result = mechanism.build_survey_artifacts(
        output_dir,
        _sample_book_document(),  # type: ignore[arg-type]
        policy_snapshot={"survey_mode": "orientation_only"},
    )

    survey_path = output_dir / "_mechanisms" / "attentional_v2" / "derived" / "survey_map.json"
    revisit_path = output_dir / "_mechanisms" / "attentional_v2" / "derived" / "revisit_index.json"
    assert survey_path.exists()
    assert revisit_path.exists()

    survey = json.loads(survey_path.read_text(encoding="utf-8"))
    revisit = json.loads(revisit_path.read_text(encoding="utf-8"))
    manifest = json.loads(mechanism_manifest_file(output_dir, "attentional_v2").read_text(encoding="utf-8"))

    assert result["survey_map"]["status"] == "orientation_only"
    assert survey["policy_snapshot"]["survey_mode"] == "orientation_only"
    assert survey["reading_plan"]["mode"] == "body_first"
    assert survey["chapter_map"][0]["chapter_zone"] == "main_body"
    assert survey["chapter_map"][1]["chapter_zone"] == "auxiliary"
    assert revisit["status"] == "survey_seeded"
    assert revisit["chapter_boundaries"]["1"]["first_sentence_id"] == "c1-s1"
    assert revisit["opening_sentence_ids"][:2] == ["c1-s1", "c1-s2"]
    assert manifest["mechanism_key"] == "attentional_v2"


def test_build_book_survey_uses_llm_zone_classifier_when_available(monkeypatch):
    """Survey should accept LLM chapter-zone classifications and derive a body-first plan."""

    document = _sample_book_document()
    document["chapters"].insert(0, {  # type: ignore[union-attr]
        "id": 3,
        "title": "Preface",
        "chapter_number": None,
        "level": 1,
        "paragraphs": [],
        "sentences": [
            {
                "sentence_id": "c0-s1",
                "sentence_index": 1,
                "sentence_in_paragraph": 1,
                "paragraph_index": 1,
                "text": "Preface",
                "text_role": "chapter_heading",
                "locator": {"paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 7},
            }
        ],
    })
    calls: list[str] = []

    def fake_invoke_json(_system_prompt, user_prompt, default=None):
        calls.append(user_prompt)
        if len(calls) == 1:
            return {"zone": "front_support", "confidence": "high", "reason": "Preface introduces the book."}
        if len(calls) == 2:
            return {"zone": "main_body", "confidence": "high", "reason": "This is the main chapter."}
        return {"zone": "back_support", "confidence": "medium", "reason": "Appendix-like supporting material."}

    monkeypatch.setattr(survey_module, "current_llm_scope", lambda: object())
    monkeypatch.setattr(survey_module, "invoke_json", fake_invoke_json)

    survey = build_book_survey(
        document,  # type: ignore[arg-type]
        policy_snapshot={"survey_mode": "orientation_only"},
    )

    assert len(calls) == 3
    assert [chapter["chapter_zone"] for chapter in survey["chapter_map"]] == [
        "front_support",
        "main_body",
        "back_support",
    ]
    assert survey["reading_plan"]["mainline_chapter_ids"] == [1]
    assert survey["reading_plan"]["deferred_chapter_ids"] == [3, 2]


def test_build_book_survey_falls_back_when_llm_classifier_errors(monkeypatch):
    """Survey should keep generating a plan even if the chapter-zone classifier fails."""

    monkeypatch.setattr(survey_module, "current_llm_scope", lambda: object())
    monkeypatch.setattr(survey_module, "invoke_json", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    survey = build_book_survey(
        _sample_book_document(),  # type: ignore[arg-type]
        policy_snapshot={"survey_mode": "orientation_only"},
    )

    assert survey["chapter_map"][0]["chapter_zone"] == "main_body"
    assert survey["chapter_map"][1]["chapter_zone"] == "auxiliary"
    assert survey["reading_plan"]["mainline_chapter_ids"] == [1]
