"""Tests for sequential frontend artifact generation."""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time

import pytest

from src.config import get_reader_resume_compat_version
from src.iterator_reader import parse as parse_module
from src.iterator_reader.frontend_artifacts import (
    append_activity_event,
    append_deduped_activity_event,
    estimate_eta_seconds,
)
from src.iterator_reader.storage import (
    activity_file,
    book_manifest_file,
    chapter_qa_file,
    chapter_markdown_file,
    chapter_result_file,
    run_state_file,
)


def _structure(output_dir: Path) -> dict:
    return {
        "book": "Demo Book",
        "author": "Tester",
        "book_language": "en",
        "output_language": "en",
        "source_file": "demo.epub",
        "output_dir": str(output_dir),
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "status": "pending",
                "level": 1,
                "segments": [
                    {
                        "id": "1.1",
                        "segment_ref": "1.1",
                        "summary": "Segment 1",
                        "tokens": 20,
                        "text": "Alpha beta",
                        "paragraph_start": 1,
                        "paragraph_end": 1,
                        "status": "pending",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "start_cfi": "epubcfi(/6/2!/4/2)",
                            "end_cfi": "epubcfi(/6/2!/4/2)",
                            "paragraph_start": 1,
                            "paragraph_end": 1,
                        },
                        "paragraph_locators": [
                            {
                                "href": "chapter-1.xhtml",
                                "start_cfi": "epubcfi(/6/2!/4/2)",
                                "end_cfi": "epubcfi(/6/2!/4/2)",
                                "paragraph_index": 1,
                                "text": "Alpha beta",
                            }
                        ],
                    },
                    {
                        "id": "1.2",
                        "segment_ref": "1.2",
                        "summary": "Segment 2",
                        "tokens": 22,
                        "text": "Gamma delta",
                        "paragraph_start": 2,
                        "paragraph_end": 2,
                        "status": "pending",
                        "locator": {
                            "href": "chapter-1.xhtml",
                            "start_cfi": "epubcfi(/6/2!/4/4)",
                            "end_cfi": "epubcfi(/6/2!/4/4)",
                            "paragraph_start": 2,
                            "paragraph_end": 2,
                        },
                        "paragraph_locators": [
                            {
                                "href": "chapter-1.xhtml",
                                "start_cfi": "epubcfi(/6/2!/4/4)",
                                "end_cfi": "epubcfi(/6/2!/4/4)",
                                "paragraph_index": 2,
                                "text": "Gamma delta",
                            }
                        ],
                    },
                ],
            }
        ],
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_parse_book_writes_frontend_bootstrap_artifacts(tmp_path, monkeypatch):
    """Parse stage should bootstrap manifest, ready state, and activity stream."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)
    structure = _structure(output_dir)

    monkeypatch.setattr(
        parse_module,
        "build_structure",
        lambda *args, **kwargs: (structure, output_dir),
    )

    parse_module.parse_book(Path("demo.epub"))

    manifest = _load_json(book_manifest_file(output_dir))
    run_state = _load_json(run_state_file(output_dir))
    activity = _load_jsonl(activity_file(output_dir))

    assert manifest["book"] == "Demo Book"
    assert manifest["book_id"] == "demo-book"
    assert manifest["source_asset"] == {"format": "epub", "file": "_assets/source.epub"}
    assert manifest["cover_image_url"] is None
    assert manifest["chapters"][0]["markdown_file"] == "public/chapters/ch01_deep_read.md"
    assert manifest["chapters"][0]["result_file"] == "public/chapters/ch01_deep_read.json"
    assert manifest["chapters"][0]["visible_reaction_count"] == 0
    assert run_state["stage"] == "ready"
    assert run_state["mode"] == "sequential"
    assert run_state["total_chapters"] == 1
    assert activity[-1]["type"] == "structure_ready"


def test_parse_book_bootstraps_outline_without_semantic_segments(tmp_path, monkeypatch):
    """Deferred parse should stop at chapter outline so deep-reading prep can happen later."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)
    structure = {
        "book": "Demo Book",
        "author": "Tester",
        "book_language": "en",
        "output_language": "en",
        "source_file": "demo.epub",
        "output_dir": str(output_dir),
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "status": "pending",
                "level": 1,
                "segments": [],
            }
        ],
    }
    captured_kwargs: list[dict[str, object]] = []

    def _fake_build_structure(*args, **kwargs):
        captured_kwargs.append(kwargs)
        return structure, output_dir

    monkeypatch.setattr(parse_module, "build_structure", _fake_build_structure)

    parse_module.parse_book(Path("demo.epub"))

    manifest = _load_json(book_manifest_file(output_dir))
    run_state = _load_json(run_state_file(output_dir))

    assert len(captured_kwargs) == 1
    assert captured_kwargs[0]["language_mode"] == "auto"
    assert captured_kwargs[0]["continue_mode"] is False
    assert captured_kwargs[0]["include_segments"] is False
    assert captured_kwargs[0]["prompt_set"] is parse_module.ITERATOR_V1_PROMPTS
    assert manifest["chapters"][0]["segment_count"] == 0
    assert run_state["stage"] == "ready"
    assert run_state["completed_chapters"] == 0
    assert run_state["total_chapters"] == 1










def test_estimate_eta_seconds_stays_null_until_one_chapter_finishes():
    """ETA should remain null until there is at least one completed chapter."""
    assert estimate_eta_seconds([], 3) is None
    eta = estimate_eta_seconds([30.0], 2, current_total_segments=4, current_completed_segments=1)
    assert isinstance(eta, int)
    assert eta > 0


def test_append_activity_event_classifies_segment_progress_streams(tmp_path):
    """Structured mindstream metadata should be persisted with the canonical activity file."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)

    append_activity_event(output_dir, {"type": "segment_progress", "message": "📖 读到 Prologue.1「开头」..."})
    append_activity_event(output_dir, {"type": "segment_progress", "message": "🔗 This echoes something earlier..."})
    append_activity_event(output_dir, {"type": "segment_progress", "message": "🔎 搜索: foo"})
    append_activity_event(output_dir, {"type": "segment_progress", "message": "🤫 这段是过渡，安静读过"})
    append_activity_event(output_dir, {"type": "segment_progress", "message": "可以，下一段"})

    activity = _load_jsonl(activity_file(output_dir))

    assert [(item["kind"], item["visibility"]) for item in activity] == [
        ("position", "default"),
        ("thought", "default"),
        ("search", "default"),
        ("transition", "collapsed"),
        ("transition", "hidden"),
    ]
    assert all(item["stream"] == "mindstream" for item in activity)


def test_append_activity_event_classifies_runtime_guard_events_as_system_errors(tmp_path):
    """Runtime guard events should land in the program log stream."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)

    append_activity_event(output_dir, {"type": "runtime_stalled", "message": "Runtime activity stalled."})
    append_activity_event(output_dir, {"type": "heartbeat_lost", "message": "Heartbeat stopped."})
    append_activity_event(output_dir, {"type": "job_paused_by_runtime_guard", "message": "Reader paused."})

    activity = _load_jsonl(activity_file(output_dir))

    assert [(item["stream"], item["kind"]) for item in activity] == [
        ("system", "error"),
        ("system", "error"),
        ("system", "error"),
    ]


def test_append_deduped_activity_event_suppresses_recent_runtime_duplicates(tmp_path):
    """Operational runtime events should not flood the program log."""
    output_dir = tmp_path / "output" / "demo-book"
    output_dir.mkdir(parents=True, exist_ok=True)

    first = append_deduped_activity_event(
        output_dir,
        {
            "type": "runtime_stalled",
            "message": "Runtime activity stalled for 60s while reading Chapter 1.",
            "chapter_ref": "Chapter 1",
            "segment_ref": "1.2",
            "problem_code": "network_blocked",
        },
    )
    second = append_deduped_activity_event(
        output_dir,
        {
            "type": "runtime_stalled",
            "message": "Runtime activity stalled for 60s while reading Chapter 1.",
            "chapter_ref": "Chapter 1",
            "segment_ref": "1.2",
            "problem_code": "network_blocked",
        },
    )

    activity = _load_jsonl(activity_file(output_dir))

    assert first is not None
    assert second is None
    assert len(activity) == 1
