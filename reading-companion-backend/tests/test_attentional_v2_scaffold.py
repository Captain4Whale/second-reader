"""Tests for the attentional_v2 Phase 1 scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.attentional_v2 import runner as runner_module
from src.attentional_v2.slow_cycle import project_chapter_result_compatibility
from src.attentional_v2.schemas import (
    ATTENTIONAL_V2_MECHANISM_VERSION,
    ATTENTIONAL_V2_POLICY_VERSION,
    ATTENTIONAL_V2_SCHEMA_VERSION,
    build_empty_active_attention,
    build_empty_anchor_bank,
    build_empty_concept_registry,
    build_empty_local_buffer,
    build_empty_local_continuity,
    build_empty_reaction_records,
    build_empty_reflective_frames,
    build_empty_thread_trace,
)
from src.attentional_v2.storage import (
    ATTENTIONAL_V2_MECHANISM_KEY,
    anchor_bank_file,
    chapter_result_compatibility_file,
    concept_registry_file,
    event_stream_file,
    knowledge_activations_file,
    local_buffer_file,
    local_continuity_file,
    reaction_records_file,
    reader_policy_file,
    read_audit_file,
    reflective_frames_file,
    reconsolidation_records_file,
    revisit_index_file,
    resume_metadata_file,
    survey_map_file,
    thread_trace_file,
    unitization_audit_file,
    active_attention_file,
)
from src.reading_core.runtime_contracts import ParseRequest, ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_runtime.provisioning import ProvisionedBook
from src.reading_runtime.artifacts import checkpoint_summary_file, mechanism_manifest_file, runtime_shell_file
from src.reading_runtime.shell_state import load_runtime_shell


def _fixture_epub() -> Path:
    """Return the tracked EPUB fixture used for live runner tests."""

    return Path(__file__).resolve().parent / "fixtures" / "e2e_runtime" / "sample-upload.epub"


def _provisioned_book() -> ProvisionedBook:
    """Return a lightweight shared parsed-book fixture for attentional runner tests."""

    book_document = {
        "metadata": {
            "book": "Demo Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Alpha sentence. Beta sentence.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:24",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Alpha sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 15,
                            "start_cfi": "/6/2[chap01]!/4/2/1:0",
                            "end_cfi": "/6/2[chap01]!/4/2/1:15",
                        },
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Beta sentence.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 16,
                            "char_end": 30,
                            "start_cfi": "/6/2[chap01]!/4/2/1:16",
                            "end_cfi": "/6/2[chap01]!/4/2/1:30",
                        },
                    },
                ],
            }
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Demo Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/demo-book"),
        raw_chapters=None,
        book_document=book_document,
    )


def _provisioned_book_with_detour() -> ProvisionedBook:
    """Return a two-chapter fixture suitable for detour-flow tests."""

    book_document = {
        "metadata": {
            "book": "Detour Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Opening setup. First consequence.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:32",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Opening setup.",
                        "text_role": "body",
                        "locator": {"href": "chapter-1.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 14},
                    },
                    {
                        "sentence_id": "c1-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "First consequence.",
                        "text_role": "body",
                        "locator": {"href": "chapter-1.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 15, "char_end": 33},
                    },
                ],
            },
            {
                "id": 2,
                "title": "Chapter 2",
                "chapter_number": 2,
                "reference": "Chapter 2",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Later question. Closing line.",
                        "href": "chapter-2.xhtml",
                        "start_cfi": "/6/2[chap02]!/4/2/1:0",
                        "end_cfi": "/6/2[chap02]!/4/2/1:28",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c2-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Later question.",
                        "text_role": "body",
                        "locator": {"href": "chapter-2.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 0, "char_end": 15},
                    },
                    {
                        "sentence_id": "c2-s2",
                        "sentence_index": 2,
                        "paragraph_index": 1,
                        "text": "Closing line.",
                        "text_role": "body",
                        "locator": {"href": "chapter-2.xhtml", "paragraph_index": 1, "paragraph_start": 1, "paragraph_end": 1, "char_start": 16, "char_end": 29},
                    },
                ],
            },
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Detour Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/detour-book"),
        raw_chapters=None,
        book_document=book_document,
    )


def _provisioned_book_with_supporting_chapters() -> ProvisionedBook:
    """Return a three-chapter fixture with support material around one body chapter."""

    book_document = {
        "metadata": {
            "book": "Support Book",
            "author": "Tester",
            "book_language": "en",
            "output_language": "en",
            "source_file": str(_fixture_epub()),
        },
        "chapters": [
            {
                "id": 1,
                "title": "Preface",
                "chapter_number": None,
                "reference": "Preface",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "How to use this book.",
                        "href": "preface.xhtml",
                        "start_cfi": "/6/2[preface]!/4/2/1:0",
                        "end_cfi": "/6/2[preface]!/4/2/1:22",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c1-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "How to use this book.",
                        "text_role": "body",
                        "locator": {
                            "href": "preface.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 22,
                        },
                    }
                ],
            },
            {
                "id": 2,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Main idea.",
                        "href": "chapter-1.xhtml",
                        "start_cfi": "/6/2[chap01]!/4/2/1:0",
                        "end_cfi": "/6/2[chap01]!/4/2/1:10",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c2-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Main idea.",
                        "text_role": "body",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 10,
                        },
                    }
                ],
            },
            {
                "id": 3,
                "title": "Afterword",
                "chapter_number": None,
                "reference": "Afterword",
                "paragraphs": [
                    {
                        "paragraph_index": 1,
                        "text": "Closing reflection.",
                        "href": "afterword.xhtml",
                        "start_cfi": "/6/2[afterword]!/4/2/1:0",
                        "end_cfi": "/6/2[afterword]!/4/2/1:18",
                        "text_role": "body",
                    }
                ],
                "sentences": [
                    {
                        "sentence_id": "c3-s1",
                        "sentence_index": 1,
                        "paragraph_index": 1,
                        "text": "Closing reflection.",
                        "text_role": "body",
                        "locator": {
                            "href": "afterword.xhtml",
                            "paragraph_index": 1,
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                            "char_start": 0,
                            "char_end": 18,
                        },
                    }
                ],
            },
        ],
    }
    return ProvisionedBook(
        book_path=_fixture_epub(),
        title="Support Book",
        author="Tester",
        book_language="en",
        output_language="en",
        output_dir=Path("output/support-book"),
        raw_chapters=None,
        book_document=book_document,
    )


@pytest.fixture(autouse=True)
def _stub_survey_artifacts(monkeypatch):
    """Keep scaffold tests deterministic by stubbing the survey artifact writer."""

    def fake_write_book_survey_artifacts(output_dir, book_document, *, policy_snapshot=None):
        chapters = [dict(chapter) for chapter in book_document.get("chapters", []) if isinstance(chapter, dict)]
        chapter_map = []
        mainline_chapter_ids: list[int] = []
        deferred_chapter_ids: list[int] = []
        for chapter in chapters:
            chapter_id = int(chapter.get("id", 0) or 0)
            title = str(chapter.get("title", "") or "")
            lowered = title.lower()
            if any(marker in lowered for marker in ("preface", "foreword", "introduction", "prologue")):
                zone = "front_support"
                deferred_chapter_ids.append(chapter_id)
            elif any(marker in lowered for marker in ("appendix", "afterword", "epilogue", "postscript")):
                zone = "back_support"
                deferred_chapter_ids.append(chapter_id)
            elif any(marker in lowered for marker in ("notes", "references", "bibliography", "index")):
                zone = "auxiliary"
            else:
                zone = "main_body"
                mainline_chapter_ids.append(chapter_id)
            chapter_map.append(
                {
                    "chapter_id": chapter_id,
                    "title": title,
                    "chapter_number": chapter.get("chapter_number"),
                    "level": int(chapter.get("level", 1) or 1),
                    "structural_role_guess": "body",
                    "role_confidence": "weak",
                    "chapter_zone": zone,
                    "zone_confidence": "stub",
                    "zone_reason": "test_stub",
                    "heading_text": "",
                    "opening_sentences": [],
                    "closing_sentences": [],
                    "pivot_headings": [],
                }
            )
        if not mainline_chapter_ids:
            mainline_chapter_ids = [
                int(chapter.get("id", 0) or 0)
                for chapter in chapters
                if int(chapter.get("id", 0) or 0) > 0 and int(chapter.get("id", 0) or 0) not in deferred_chapter_ids
            ]
        survey = {
            "schema_version": 1,
            "mechanism_version": "attentional_v2-phase6",
            "generated_at": "2026-04-22T00:00:00Z",
            "status": "orientation_only",
            "book_frame": {
                "book": str(book_document.get("metadata", {}).get("book", "") or ""),
                "author": str(book_document.get("metadata", {}).get("author", "") or ""),
                "total_chapters": len(chapters),
            },
            "chapter_map": chapter_map,
            "reading_plan": {
                "mode": "body_first",
                "mainline_chapter_ids": mainline_chapter_ids,
                "deferred_chapter_ids": deferred_chapter_ids,
            },
            "initial_motif_seeds": [],
            "survey_caveats": [],
            "policy_snapshot": dict(policy_snapshot or {}),
        }
        revisit = {
            "schema_version": 1,
            "mechanism_version": "attentional_v2-phase6",
            "generated_at": "2026-04-22T00:00:00Z",
            "status": "survey_seeded",
            "anchors": {},
            "chapter_boundaries": {},
            "opening_sentence_ids": [],
        }
        survey_map_file(output_dir).write_text(json.dumps(survey, ensure_ascii=False, indent=2), encoding="utf-8")
        revisit_index_file(output_dir).write_text(json.dumps(revisit, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"survey_map": survey, "revisit_index": revisit}

    monkeypatch.setattr(runner_module, "write_book_survey_artifacts", fake_write_book_survey_artifacts)


def test_attentional_v2_initialization_writes_mechanism_artifacts(tmp_path):
    """The mechanism should write the shared shell and private state files."""

    output_dir = tmp_path / "output" / "demo-book"

    result = AttentionalV2Mechanism().initialize_artifacts(output_dir)

    assert result["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert result["mechanism_version"] == ATTENTIONAL_V2_MECHANISM_VERSION
    assert result["policy_version"] == ATTENTIONAL_V2_POLICY_VERSION

    shell = load_runtime_shell(runtime_shell_file(output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert shell["mechanism_version"] == ATTENTIONAL_V2_MECHANISM_VERSION
    assert shell["observability_mode"] == "standard"
    assert shell["cursor"]["position_kind"] == "chapter"

    checkpoint = json.loads(checkpoint_summary_file(output_dir, "bootstrap").read_text(encoding="utf-8"))
    assert checkpoint["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert checkpoint["observability_mode"] == "standard"
    assert checkpoint["resume_kind"] == "warm_resume"

    manifest = json.loads(mechanism_manifest_file(output_dir, ATTENTIONAL_V2_MECHANISM_KEY).read_text(encoding="utf-8"))
    assert manifest["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY

    active_attention = json.loads(active_attention_file(output_dir).read_text(encoding="utf-8"))
    assert active_attention["schema_version"] == ATTENTIONAL_V2_SCHEMA_VERSION
    assert active_attention["active_items"] == []
    assert ("gate_" + "state") not in active_attention

    local_buffer = json.loads(local_buffer_file(output_dir).read_text(encoding="utf-8"))
    assert local_buffer["recent_sentences"] == []
    assert local_buffer["recent_meaning_units"] == []

    local_continuity = json.loads(local_continuity_file(output_dir).read_text(encoding="utf-8"))
    assert local_continuity["recent_sentence_ids"] == []
    assert local_continuity["active_detour_id"] == ""
    assert local_continuity["detour_trace"] == []

    concept_registry = json.loads(concept_registry_file(output_dir).read_text(encoding="utf-8"))
    assert concept_registry["entries"] == []

    thread_trace = json.loads(thread_trace_file(output_dir).read_text(encoding="utf-8"))
    assert thread_trace["entries"] == []

    anchor_bank = json.loads(anchor_bank_file(output_dir).read_text(encoding="utf-8"))
    assert anchor_bank["anchor_records"] == []

    reflective = json.loads(reflective_frames_file(output_dir).read_text(encoding="utf-8"))
    assert reflective["chapter_understandings"] == []

    activations = json.loads(knowledge_activations_file(output_dir).read_text(encoding="utf-8"))
    assert activations["knowledge_use_mode"] == "book_grounded_only"
    assert activations["search_policy_mode"] == "no_search"

    reaction_records = json.loads(reaction_records_file(output_dir).read_text(encoding="utf-8"))
    assert reaction_records["records"] == []

    reconsolidation = json.loads(reconsolidation_records_file(output_dir).read_text(encoding="utf-8"))
    assert reconsolidation["records"] == []

    policy = json.loads(reader_policy_file(output_dir).read_text(encoding="utf-8"))
    assert policy["policy_version"] == ATTENTIONAL_V2_POLICY_VERSION
    assert policy["unitize"]["max_coverage_unit_sentences"] == 12
    assert policy["bridge"]["source_anchor_required"] is True
    assert policy["search"]["default_mode"] == "no_search"
    assert policy["resume"]["cold_resume_target_sentences"] == 8
    assert policy["resume"]["reconstitution_resume_max_sentences"] == 30
    assert policy["logging"]["observability_mode"] == "standard"
    assert policy["logging"]["debug_event_stream"] is False

    resume_metadata = json.loads(resume_metadata_file(output_dir).read_text(encoding="utf-8"))
    assert resume_metadata["resume_available"] is False
    assert resume_metadata["default_resume_kind"] == "warm_resume"

    survey = json.loads(survey_map_file(output_dir).read_text(encoding="utf-8"))
    assert survey["status"] == "not_started"
    assert survey["chapter_map"] == []
    assert survey["reading_plan"]["mode"] == "body_first"
    assert survey["reading_plan"]["mainline_chapter_ids"] == []
    assert survey["reading_plan"]["deferred_chapter_ids"] == []

    revisit = json.loads(revisit_index_file(output_dir).read_text(encoding="utf-8"))
    assert revisit["anchors"] == {}

    assert event_stream_file(output_dir).read_text(encoding="utf-8") == ""
    assert result["artifact_map"]["active_attention"].endswith("active_attention.json")


def test_attentional_v2_parse_book_creates_ready_artifacts_without_iterator_structure(tmp_path, monkeypatch):
    """The live parse path should build canonical attentional artifacts without iterator structure."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())
    mechanism = AttentionalV2Mechanism()
    result = mechanism.parse_book(
        ParseRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
        )
    )

    assert result.book_document["chapters"]
    assert result.mechanism_artifact is not None
    assert result.mechanism_artifact["artifact_map"]["survey_map"].endswith("survey_map.json")
    assert survey_map_file(result.output_dir).exists()
    assert not (result.output_dir / "_mechanisms" / "iterator_v1" / "derived" / "structure.json").exists()
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))["chapters"]
    survey = json.loads(survey_map_file(result.output_dir).read_text(encoding="utf-8"))
    assert survey["reading_plan"]["mode"] == "body_first"


def test_attentional_v2_runner_prefers_main_body_before_supporting_chapters(tmp_path, monkeypatch):
    """Full-book runs should consume main-body chapters before deferred support chapters."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book_with_supporting_chapters())
    chapter_read_order: list[str] = []

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        chapter_read_order.append(str(kwargs["chapter_title"]))
        return {
            "reading_impression": f"Read {focal_sentence['sentence_id']}.",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        return {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    manifest = json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))
    assert chapter_read_order == ["Chapter 1", "Preface", "Afterword"]
    assert shell["status"] == "completed"
    assert manifest["chapters"][0]["status"] == "done"
    assert manifest["chapters"][1]["status"] == "done"
    assert manifest["chapters"][2]["status"] == "done"


def test_attentional_v2_chapter_selection_honors_explicit_request_over_reading_plan(tmp_path):
    """Explicit chapter requests should bypass body-first chapter reordering."""

    document = _provisioned_book_with_supporting_chapters().book_document
    output_dir = tmp_path / "output" / "support-book"
    AttentionalV2Mechanism().initialize_artifacts(output_dir)
    survey_map = {
        "reading_plan": {
            "mode": "body_first",
            "mainline_chapter_ids": [2],
            "deferred_chapter_ids": [1, 3],
        }
    }

    chapters = runner_module._chapter_selection(  # noqa: SLF001
        document,
        output_dir,
        survey_map=survey_map,
        chapter_number=3,
        continue_mode=False,
        resume_chapter_id=None,
    )

    assert [chapter["title"] for chapter in chapters] == ["Afterword"]


def _empty_choose_next_unit_state() -> dict[str, dict[str, object]]:
    """Return the minimal live state required by Navigate.choose_next_unit."""

    return {
        "local_buffer": build_empty_local_buffer(),
        "local_continuity": build_empty_local_continuity(),
        "continuation_capsule": {},
        "active_attention": build_empty_active_attention(),
        "concept_registry": build_empty_concept_registry(),
        "thread_trace": build_empty_thread_trace(),
        "reflective_frames": build_empty_reflective_frames(),
        "anchor_bank": build_empty_anchor_bank(),
        "reaction_records": build_empty_reaction_records(),
    }


def test_navigate_choose_next_unit_selects_mainline_unit_without_active_detour(tmp_path, monkeypatch):
    """The current Navigator contract should wrap mainline unitization as one next-unit decision."""

    provisioned = _provisioned_book_with_detour()
    document = provisioned.book_document
    sentence_lookup, chapter_lookup = runner_module._build_sentence_lookup(document)  # noqa: SLF001
    state = _empty_choose_next_unit_state()

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "mainline_test",
            "continuation_pressure": False,
        },
    )

    result = runner_module.navigate_choose_next_unit(
        document=document,
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        current_chapter=document["chapters"][1],
        current_cursor=0,
        local_buffer=state["local_buffer"],  # type: ignore[arg-type]
        continuation_capsule=state["continuation_capsule"],
        active_attention=state["active_attention"],  # type: ignore[arg-type]
        concept_registry=state["concept_registry"],  # type: ignore[arg-type]
        thread_trace=state["thread_trace"],  # type: ignore[arg-type]
        reflective_frames=state["reflective_frames"],  # type: ignore[arg-type]
        anchor_bank=state["anchor_bank"],  # type: ignore[arg-type]
        reaction_records=state["reaction_records"],  # type: ignore[arg-type]
        local_continuity=state["local_continuity"],  # type: ignore[arg-type]
        reader_policy=runner_module.build_default_reader_policy(),
        output_language=provisioned.output_language,
        output_dir=tmp_path,
        book_title=provisioned.title,
        author=provisioned.author,
    )

    assert result["selection_mode"] == "mainline"
    assert result["chapter_id"] == 2
    assert [sentence["sentence_id"] for sentence in result["selected_unit_sentences"]] == ["c2-s1"]


def test_navigate_choose_next_unit_lands_detour_then_unitizes_inside_region(tmp_path, monkeypatch):
    """An active detour should be located first, then unitized through the same next-unit contract."""

    provisioned = _provisioned_book_with_detour()
    document = provisioned.book_document
    sentence_lookup, chapter_lookup = runner_module._build_sentence_lookup(document)  # noqa: SLF001
    state = _empty_choose_next_unit_state()
    local_continuity = state["local_continuity"]  # type: ignore[assignment]
    local_continuity["mainline_cursor"] = {
        "position_kind": "sentence",
        "chapter_id": 2,
        "chapter_ref": "Chapter 2",
        "sentence_id": "c2-s1",
        "sentence_index": 1,
    }
    local_continuity = runner_module._apply_detour_need(  # noqa: SLF001
        local_continuity,
        {
            "reason": "Need the opening setup.",
            "target_hint": "opening setup",
            "status": "open",
        },
    )

    def fake_detour_search(**kwargs):
        assert kwargs["detour_need"]["target_hint"] == "opening setup"
        return {
            "decision": "land_region",
            "reason": "Chapter 1 contains the setup.",
            "start_sentence_id": "c1-s1",
            "end_sentence_id": "c1-s2",
        }

    monkeypatch.setattr(runner_module, "navigate_detour_search", fake_detour_search)
    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": preview_sentences[-1]["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"], preview_sentences[-1]["sentence_id"]],
            "reason": "detour_region_unitized",
            "continuation_pressure": False,
        },
    )

    result = runner_module.navigate_choose_next_unit(
        document=document,
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        current_chapter=document["chapters"][1],
        current_cursor=0,
        local_buffer=state["local_buffer"],  # type: ignore[arg-type]
        continuation_capsule=state["continuation_capsule"],
        active_attention=state["active_attention"],  # type: ignore[arg-type]
        concept_registry=state["concept_registry"],  # type: ignore[arg-type]
        thread_trace=state["thread_trace"],  # type: ignore[arg-type]
        reflective_frames=state["reflective_frames"],  # type: ignore[arg-type]
        anchor_bank=state["anchor_bank"],  # type: ignore[arg-type]
        reaction_records=state["reaction_records"],  # type: ignore[arg-type]
        local_continuity=local_continuity,
        reader_policy=runner_module.build_default_reader_policy(),
        output_language=provisioned.output_language,
        output_dir=tmp_path,
        book_title=provisioned.title,
        author=provisioned.author,
    )

    assert result["selection_mode"] == "detour"
    assert result["chapter_id"] == 1
    assert [sentence["sentence_id"] for sentence in result["selected_unit_sentences"]] == ["c1-s1", "c1-s2"]
    assert result["detour_search_trace"][0]["decision"] == "land_region"


def test_navigate_choose_next_unit_defers_unlanded_detour(tmp_path, monkeypatch):
    """A detour that cannot land should return a deferred next-unit result instead of running read."""

    provisioned = _provisioned_book_with_detour()
    document = provisioned.book_document
    sentence_lookup, chapter_lookup = runner_module._build_sentence_lookup(document)  # noqa: SLF001
    state = _empty_choose_next_unit_state()
    local_continuity = state["local_continuity"]  # type: ignore[assignment]
    local_continuity["mainline_cursor"] = {
        "position_kind": "sentence",
        "chapter_id": 2,
        "chapter_ref": "Chapter 2",
        "sentence_id": "c2-s1",
        "sentence_index": 1,
    }
    local_continuity = runner_module._apply_detour_need(  # noqa: SLF001
        local_continuity,
        {
            "reason": "Need the opening setup.",
            "target_hint": "opening setup",
            "status": "open",
        },
    )

    monkeypatch.setattr(
        runner_module,
        "navigate_detour_search",
        lambda **_kwargs: {
            "decision": "defer_detour",
            "reason": "not enough grounded evidence",
            "start_sentence_id": "",
            "end_sentence_id": "",
        },
    )

    result = runner_module.navigate_choose_next_unit(
        document=document,
        survey_map={},
        sentence_lookup=sentence_lookup,
        chapter_lookup=chapter_lookup,
        current_chapter=document["chapters"][1],
        current_cursor=0,
        local_buffer=state["local_buffer"],  # type: ignore[arg-type]
        continuation_capsule=state["continuation_capsule"],
        active_attention=state["active_attention"],  # type: ignore[arg-type]
        concept_registry=state["concept_registry"],  # type: ignore[arg-type]
        thread_trace=state["thread_trace"],  # type: ignore[arg-type]
        reflective_frames=state["reflective_frames"],  # type: ignore[arg-type]
        anchor_bank=state["anchor_bank"],  # type: ignore[arg-type]
        reaction_records=state["reaction_records"],  # type: ignore[arg-type]
        local_continuity=local_continuity,
        reader_policy=runner_module.build_default_reader_policy(),
        output_language=provisioned.output_language,
        output_dir=tmp_path,
        book_title=provisioned.title,
        author=provisioned.author,
    )

    assert result["selection_mode"] == "deferred"
    assert result["defer_reason"] == "not enough grounded evidence"
    assert result["selected_unit_sentences"] == []


def test_attentional_v2_read_book_runs_live_loop_and_persists_compatibility_results(tmp_path, monkeypatch):
    """The live runner should persist unitization/read audits, reactions, and compatibility payloads."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())
    captured_unit_reads: list[list[str]] = []
    captured_carry_forward_contexts: list[dict[str, object]] = []

    def fake_read_unit(**kwargs):
        current_unit_sentences = kwargs["current_unit_sentences"]
        focal_sentence = current_unit_sentences[-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        captured_unit_reads.append([str(sentence.get("sentence_id")) for sentence in current_unit_sentences])
        captured_carry_forward_contexts.append(dict(kwargs["carry_forward_context"]))
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [
                {
                    "anchor_quote": anchor_quote,
                    "content": f"Read noticed: {anchor_quote[:40]}",
                    "prior_link": {
                        "ref_ids": ["anchor:a-0"],
                        "relation": "callback",
                        "note": "The earlier thread quietly set this up.",
                    },
                }
            ],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    assert result.normalized_eval_bundle["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    unitize_lines = unitization_audit_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    read_audit_lines = read_audit_file(result.output_dir).read_text(encoding="utf-8").strip().splitlines()
    read_audits = [json.loads(line) for line in read_audit_lines]
    assert chapter_payload["visible_reaction_count"] >= 1
    assert captured_unit_reads == [["c1-s1"], ["c1-s2"]]
    assert captured_carry_forward_contexts[0]["packet_version"] == "attentional_v2.state_packet.v1"
    assert "active_attention_digest" in captured_carry_forward_contexts[0]
    assert captured_carry_forward_contexts[0]["continuity_digest"]["recent_reactions"] == []
    assert captured_carry_forward_contexts[1]["continuity_digest"]["recent_reactions"]
    assert len(unitize_lines) == 2
    assert len(read_audit_lines) == 2
    assert all(audit["surfaced_reaction_count"] == 1 for audit in read_audits)
    assert read_audits[1]["carry_forward_ref_ids"]
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["mechanism_key"] == ATTENTIONAL_V2_MECHANISM_KEY
    assert shell["status"] == "completed"
    assert shell["last_checkpoint_id"] == "chapter-001"
    manifest = json.loads((result.output_dir / "public" / "book_manifest.json").read_text(encoding="utf-8"))
    chapter_manifest = manifest["chapters"][0]
    assert chapter_manifest["result_file"] == "_mechanisms/attentional_v2/derived/chapter_result_compatibility/chapter-001.json"
    assert chapter_manifest["visible_reaction_count"] >= 1
    assert chapter_manifest["reaction_type_diversity"] >= 1
    persisted_reactions = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))["records"]
    assert persisted_reactions[0]["record_source"] == "read_surface"
    assert persisted_reactions[0]["thought"].startswith("Read noticed:")
    assert persisted_reactions[0]["prior_link"]["ref_ids"] == ["anchor:a-0"]


def test_attentional_v2_runner_persists_multiple_read_surface_reactions(tmp_path, monkeypatch):
    """Read-owned surfaced reactions should persist directly without a separate express pass."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [
                {
                    "anchor_quote": anchor_quote,
                    "content": f"First surfaced: {anchor_quote[:20]}",
                },
                {
                    "anchor_quote": anchor_quote,
                    "content": f"Second surfaced: {anchor_quote[:20]}",
                    "search_intent": {
                        "query": "why this line lands so hard",
                        "rationale": "The second reaction opens a follow-up question.",
                    },
                },
            ],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    persisted_reactions = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))["records"]
    assert len(persisted_reactions) == 4
    assert all(record["record_source"] == "read_surface" for record in persisted_reactions)
    assert persisted_reactions[0]["thought"].startswith("First surfaced:")
    assert persisted_reactions[1]["search_intent"]["query"] == "why this line lands so hard"


def test_attentional_v2_read_book_tolerates_missing_reaction_payload(tmp_path, monkeypatch):
    """The live runner should tolerate a read result with no raw reaction payload."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_read_unit(**kwargs):
        focal_sentence = kwargs["current_unit_sentences"][-1]
        anchor_quote = str(focal_sentence.get("text", "") or "").strip()[:80]
        return {
            "reading_impression": f"Meaning unit around {anchor_quote[:24]}",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    assert chapter_payload["visible_reaction_count"] == 0
    reaction_records = json.loads(reaction_records_file(result.output_dir).read_text(encoding="utf-8"))
    assert reaction_records["records"] == []
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["status"] == "completed"


def test_attentional_v2_read_book_still_runs_formal_read_for_monitor_path(tmp_path, monkeypatch):
    """Monitor-path sentences should still enter one formal unitized read in Phase A."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book())

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    read_calls: list[list[str]] = []

    def fake_read_unit(**kwargs):
        read_calls.append(
            [
                str(sentence.get("sentence_id"))
                for sentence in kwargs["current_unit_sentences"]
            ]
        )
        return {
            "reading_impression": "single-sentence path still got read",
            "surfaced_reactions": [],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "single-sentence path",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    local_buffer = json.loads(local_buffer_file(result.output_dir).read_text(encoding="utf-8"))
    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    shell = load_runtime_shell(runtime_shell_file(result.output_dir))

    assert local_buffer["current_sentence_id"] == "c1-s2"
    assert chapter_payload["visible_reaction_count"] == 0
    assert shell["status"] == "completed"
    assert read_calls == [["c1-s1"], ["c1-s2"]]


def test_attentional_v2_runner_executes_detour_search_and_returns_to_mainline(tmp_path, monkeypatch):
    """An open detour need should trigger bounded detour search, a detour read, and then resume mainline."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book_with_detour())
    read_sequence: list[tuple[list[str], bool]] = []
    detour_search_calls: list[dict[str, object]] = []

    def fake_read_unit(**kwargs):
        sentence_ids = [str(sentence.get("sentence_id")) for sentence in kwargs["current_unit_sentences"]]
        is_detour = bool(kwargs.get("detour_context"))
        read_sequence.append((sentence_ids, is_detour))
        focal_sentence_id = sentence_ids[-1]
        if focal_sentence_id == "c2-s1" and not is_detour:
            return {
                "reading_impression": "The later question clearly points back to the setup.",
                "surfaced_reactions": [
                    {
                        "anchor_quote": "Later question.",
                        "content": "This question is still leaning on something earlier.",
                    }
                ],
                "memory_uptake_ops": [],
                "detour_need": {
                    "reason": "The later question depends on the opening setup.",
                    "target_hint": "opening setup",
                    "status": "open",
                },
            }
        return {
            "reading_impression": f"Read {focal_sentence_id}.",
            "surfaced_reactions": [
                {
                    "anchor_quote": str(kwargs["current_unit_sentences"][-1].get("text")),
                    "content": f"Read noticed {focal_sentence_id}.",
                }
            ],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    def fake_detour_search(**kwargs):
        detour_search_calls.append(
            {
                "scope_kind": kwargs["search_scope"]["scope_kind"],
                "target_hint": kwargs["detour_need"]["target_hint"],
            }
        )
        if len(detour_search_calls) == 1:
            return {
                "decision": "narrow_scope",
                "reason": "Chapter 1 is the right corridor.",
                "start_sentence_id": "c1-s1",
                "end_sentence_id": "c1-s2",
            }
        return {
            "decision": "land_region",
            "reason": "The opening setup is the right earlier region.",
            "start_sentence_id": "c1-s1",
            "end_sentence_id": "c1-s2",
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "navigate_detour_search", fake_detour_search)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    assert read_sequence == [
        (["c1-s1"], False),
        (["c1-s2"], False),
        (["c2-s1"], False),
        (["c1-s1"], True),
        (["c2-s2"], False),
    ]
    assert [call["scope_kind"] for call in detour_search_calls] == ["chapter_cards", "paragraph_window_cards"]
    continuity = json.loads(local_continuity_file(result.output_dir).read_text(encoding="utf-8"))
    assert continuity["active_detour_id"] == ""
    assert continuity["detour_trace"][-1]["status"] == "resolved"


def test_attentional_v2_runner_drains_last_unit_detour_before_chapter_close(tmp_path, monkeypatch):
    """A detour opened on the last mainline unit should still run before chapter slow-cycle closes."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book_with_detour())
    read_sequence: list[tuple[list[str], bool]] = []
    detour_search_calls: list[dict[str, object]] = []

    def fake_read_unit(**kwargs):
        sentence_ids = [str(sentence.get("sentence_id")) for sentence in kwargs["current_unit_sentences"]]
        is_detour = bool(kwargs.get("detour_context"))
        read_sequence.append((sentence_ids, is_detour))
        focal_sentence_id = sentence_ids[-1]
        if focal_sentence_id == "c2-s2" and not is_detour:
            return {
                "reading_impression": "The chapter ending points back to the opening setup.",
                "surfaced_reactions": [
                    {
                        "anchor_quote": "Later answer.",
                        "content": "This answer still depends on the opening setup.",
                    }
                ],
                "memory_uptake_ops": [],
                "detour_need": {
                    "reason": "The chapter ending still depends on the opening setup.",
                    "target_hint": "opening setup",
                    "status": "open",
                },
            }
        return {
            "reading_impression": f"Read {focal_sentence_id}.",
            "surfaced_reactions": [
                {
                    "anchor_quote": str(kwargs["current_unit_sentences"][-1].get("text")),
                    "content": f"Read noticed {focal_sentence_id}.",
                }
            ],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    def fake_detour_search(**kwargs):
        detour_search_calls.append(
            {
                "scope_kind": kwargs["search_scope"]["scope_kind"],
                "target_hint": kwargs["detour_need"]["target_hint"],
            }
        )
        return {
            "decision": "land_region",
            "reason": "The opening setup is the right earlier region.",
            "start_sentence_id": "c1-s1",
            "end_sentence_id": "c1-s2",
        }

    def fake_phase6_chapter_cycle(**kwargs):
        compatibility_payload = project_chapter_result_compatibility(
            book_id=kwargs["book_id"],
            chapter=kwargs["chapter"],
            reaction_records=kwargs["reaction_records"],
            output_language=kwargs["output_language"],
            output_dir=kwargs["output_dir"],
            persist=True,
        )
        return {
            "chapter_consolidation": {"chapter_ref": kwargs["chapter"].get("reference", "")},
            "promotion_results": [],
            "active_attention": kwargs["active_attention"],
            "concept_registry": kwargs["concept_registry"],
            "thread_trace": kwargs["thread_trace"],
            "anchor_bank": kwargs["anchor_bank"],
            "reflective_frames": kwargs["reflective_frames"],
            "knowledge_activations": kwargs["knowledge_activations"],
            "reaction_records": kwargs["reaction_records"],
            "compatibility_payload": compatibility_payload,
        }

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(runner_module, "navigate_detour_search", fake_detour_search)
    monkeypatch.setattr(runner_module, "run_phase6_chapter_cycle", fake_phase6_chapter_cycle)

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={},
        )
    )

    assert result.normalized_eval_bundle is not None
    assert read_sequence == [
        (["c1-s1"], False),
        (["c1-s2"], False),
        (["c2-s1"], False),
        (["c2-s2"], False),
        (["c1-s1"], True),
    ]
    assert [call["scope_kind"] for call in detour_search_calls] == ["chapter_cards"]
    continuity = json.loads(local_continuity_file(result.output_dir).read_text(encoding="utf-8"))
    assert continuity["active_detour_id"] == ""
    assert continuity["detour_trace"][-1]["status"] == "resolved"


def test_attentional_v2_runner_stops_at_audit_window_cap_and_persists_partial_outputs(tmp_path, monkeypatch):
    """Audit-only unit caps should stop the live loop cleanly and still persist partial exports."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner_module, "ensure_canonical_parse", lambda *args, **kwargs: _provisioned_book_with_detour())
    read_calls: list[list[str]] = []

    def fake_read_unit(**kwargs):
        sentence_ids = [str(sentence.get("sentence_id")) for sentence in kwargs["current_unit_sentences"]]
        read_calls.append(sentence_ids)
        focal_sentence = kwargs["current_unit_sentences"][-1]
        return {
            "reading_impression": f"Read {sentence_ids[-1]}.",
            "surfaced_reactions": [
                {
                    "anchor_quote": str(focal_sentence.get("text")),
                    "content": f"Immediate reaction to {sentence_ids[-1]}.",
                }
            ],
            "memory_uptake_ops": [],
            "detour_need": None,
        }

    def fake_process_sentence_intake(sentence, *, local_buffer, window_size=6):
        next_buffer = {
            **local_buffer,
            "current_sentence_id": sentence["sentence_id"],
            "current_sentence_index": sentence["sentence_index"],
            "recent_sentences": [*local_buffer.get("recent_sentences", []), dict(sentence)][-window_size:],
            "open_meaning_unit_sentence_ids": [sentence["sentence_id"]],
            "seen_sentence_ids": [*local_buffer.get("seen_sentence_ids", []), sentence["sentence_id"]],
        }
        return next_buffer

    monkeypatch.setattr(
        runner_module,
        "navigate_unitize",
        lambda *, current_sentence, preview_sentences, **_kwargs: {
            "start_sentence_id": current_sentence["sentence_id"],
            "end_sentence_id": current_sentence["sentence_id"],
            "preview_range": {
                "start_sentence_id": preview_sentences[0]["sentence_id"],
                "end_sentence_id": preview_sentences[-1]["sentence_id"],
            },
            "boundary_type": "paragraph_end",
            "evidence_sentence_ids": [current_sentence["sentence_id"]],
            "reason": "test_unitize_single_sentence",
            "continuation_pressure": False,
        },
    )
    monkeypatch.setattr(runner_module, "process_sentence_intake", fake_process_sentence_intake)
    monkeypatch.setattr(runner_module, "read_unit", fake_read_unit)
    monkeypatch.setattr(
        runner_module,
        "run_phase6_chapter_cycle",
        lambda **_kwargs: pytest.fail("phase6 should not run when audit_window_max_units stops the loop early"),
    )

    mechanism = AttentionalV2Mechanism()
    result = mechanism.read_book(
        ReadRequest(
            book_path=_fixture_epub(),
            mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
            mechanism_config={"audit_window_max_units": 2},
        )
    )

    assert read_calls == [["c1-s1"], ["c1-s2"]]
    assert result.normalized_eval_bundle is not None
    assert len(result.normalized_eval_bundle["reactions"]) == 2
    assert chapter_result_compatibility_file(result.output_dir, 1).exists()
    assert not chapter_result_compatibility_file(result.output_dir, 2).exists()

    read_audit_entries = [
        json.loads(line)
        for line in read_audit_file(result.output_dir).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(read_audit_entries) == 2

    chapter_payload = json.loads(chapter_result_compatibility_file(result.output_dir, 1).read_text(encoding="utf-8"))
    assert chapter_payload["visible_reaction_count"] == 2

    shell = load_runtime_shell(runtime_shell_file(result.output_dir))
    assert shell["status"] == "completed"


def test_attentional_v2_rejects_book_analysis_mode(tmp_path, monkeypatch):
    """The live runner should fail fast on book_analysis mode in this slice."""

    monkeypatch.chdir(tmp_path)
    mechanism = AttentionalV2Mechanism()

    with pytest.raises(ValueError, match=r"does not support .*book_analysis mode"):
        mechanism.read_book(
            ReadRequest(
                book_path=_fixture_epub(),
                mechanism_key=ATTENTIONAL_V2_MECHANISM_KEY,
                task_mode="book_analysis",
            )
        )
