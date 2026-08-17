"""Tests for product-layer state, jobs, REST API, and realtime API behavior."""

from __future__ import annotations

import importlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from src.api.contract import to_api_book_id, to_api_reaction_id
from src.attentional_v2.storage import chapter_result_compatibility_file
from src.config import get_reader_resume_compat_version
from src.iterator_reader.storage import (
    activity_file,
    book_manifest_file,
    existing_activity_file,
    parse_state_file,
    public_chapters_dir,
    run_state_file,
    structure_file,
)
from src.library.jobs import recover_unfinished_jobs, refresh_job, save_job
from src.library.storage import upload_file
from src.library.user_marks import delete_mark, list_book_marks, load_marks_state, put_mark
from src.reading_runtime.artifacts import runtime_shell_file
from src.reading_runtime.background_job_registry import job_record_file
from src.reading_runtime.job_lease import (
    ENV_BOOK_ID,
    ENV_JOB_ID,
    ENV_JOB_KIND,
    ENV_LEASE_GENERATION,
    ENV_LEASE_TOKEN,
    ENV_MECHANISM_KEY,
    ENV_RUN_ATTEMPT_ID,
    ENV_RUNTIME_ROOT,
    JobLeaseConflict,
    job_lease_file,
)


api_module = importlib.import_module("src.api.app")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, payloads: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in payloads) + "\n",
        encoding="utf-8",
    )


def _load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def _manifest_path(output_dir: Path) -> Path:
    return book_manifest_file(output_dir)


def _run_state_path(output_dir: Path) -> Path:
    return run_state_file(output_dir)


def _activity_path(output_dir: Path) -> Path:
    return activity_file(output_dir)


def _structure_path(output_dir: Path) -> Path:
    return structure_file(output_dir)


def _chapter_result_path(output_dir: Path) -> Path:
    return public_chapters_dir(output_dir) / "ch01_deep_read.json"


def _bootstrap_book(root: Path, *, stage: str = "completed") -> str:
    book_id = "demo-book"
    output_dir = root / "output" / book_id
    output_dir.mkdir(parents=True, exist_ok=True)
    structure_payload = {
        "book": "Demo Book",
        "author": "Tester",
        "book_language": "en",
        "output_language": "en",
        "source_file": str((root / "state" / "uploads" / "job123.epub").resolve()),
        "output_dir": str(output_dir),
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "status": "done" if stage == "completed" else "pending",
                "output_file": "ch01_deep_read.md" if stage == "completed" else "",
                "segments": [
                    {
                        "id": "1.1",
                        "segment_ref": "1.1",
                        "summary": "Segment 1",
                        "text": "Alpha beta",
                        "status": "done" if stage == "completed" else "pending",
                    }
                ],
            }
        ],
    }
    _write_json(_structure_path(output_dir), structure_payload)
    _write_json(
        _manifest_path(output_dir),
        {
            "book_id": book_id,
            "book": "Demo Book",
            "author": "Tester",
            "cover_image_url": None,
            "book_language": "en",
            "output_language": "en",
            "source_file": str((root / "state" / "uploads" / "job123.epub").resolve()),
            "source_asset": {"format": "epub", "file": "_assets/source.epub"},
            "updated_at": "2026-03-07T00:00:00Z",
            "chapters": [
                {
                    "id": 1,
                    "title": "Chapter 1",
                    "chapter_number": 1,
                    "reference": "Chapter 1",
                    "status": "done" if stage == "completed" else "pending",
                    "segment_count": 1,
                    "markdown_file": "ch01_deep_read.md",
                    "result_file": "ch01_deep_read.json",
                    "visible_reaction_count": 1 if stage == "completed" else 0,
                    "reaction_type_diversity": 1 if stage == "completed" else 0,
                }
            ],
        },
    )
    _write_json(
        _run_state_path(output_dir),
        {
            "mode": "sequential",
            "stage": stage,
            "book": "Demo Book",
            "current_chapter_id": 1 if stage == "deep_reading" else None,
            "current_chapter_ref": "Chapter 1" if stage == "deep_reading" else None,
            "current_segment_ref": "1.1" if stage == "deep_reading" else None,
            "completed_chapters": 1 if stage == "completed" else 0,
            "total_chapters": 1,
            "eta_seconds": 60 if stage == "deep_reading" else 0,
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
    )
    _write_jsonl(
        _activity_path(output_dir),
        [
            {
                "event_id": "evt-1",
                "timestamp": "2026-03-07T00:00:00Z",
                "type": "chapter_completed",
                "message": "Chapter 1 完成，已生成结果文件。",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "reaction_types": ["highlight"],
                "highlight_quote": "Alpha beta",
                "visible_reaction_count": 1,
                "featured_reactions": [
                    {
                        "reaction_id": "r1",
                        "type": "highlight",
                        "segment_ref": "1.1",
                        "anchor_quote": "Alpha beta",
                        "content": "Important line.",
                        "target_locator": {
                            "href": "chapter-1.xhtml",
                            "start_cfi": "epubcfi(/6/2!/4/2)",
                            "end_cfi": "epubcfi(/6/2!/4/2)",
                            "match_text": "Alpha beta",
                            "match_mode": "exact",
                        },
                    }
                ],
                "result_file": "ch01_deep_read.json",
            }
        ],
    )
    _write_json(
        _chapter_result_path(output_dir),
        {
            "chapter": {
                "id": 1,
                "title": "Chapter 1",
                "chapter_number": 1,
                "reference": "Chapter 1",
                "status": "done",
            },
            "output_language": "en",
            "generated_at": "2026-03-07T00:00:00Z",
            "sections": [
                {
                    "segment_id": "1.1",
                    "segment_ref": "1.1",
                    "summary": "Segment 1",
                    "original_text": "Alpha beta",
                    "verdict": "pass",
                    "quality_status": "strong",
                    "reflection_summary": "Keep",
                    "reflection_reason_codes": [],
                    "locator": {
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/2!/4/2)",
                        "end_cfi": "epubcfi(/6/2!/4/2)",
                        "paragraph_start": 1,
                        "paragraph_end": 1,
                    },
                    "reactions": [
                        {
                            "reaction_id": "r1",
                            "type": "highlight",
                            "anchor_quote": "Alpha beta",
                            "content": "Important line.",
                            "search_query": "",
                            "search_results": [],
                            "target_locator": {
                                "href": "chapter-1.xhtml",
                                "start_cfi": "epubcfi(/6/2!/4/2)",
                                "end_cfi": "epubcfi(/6/2!/4/2)",
                                "match_text": "Alpha beta",
                                "match_mode": "exact",
                            },
                        }
                    ],
                }
            ],
            "chapter_heading": {
                "label": "Chapter 1",
                "title": "Opening frame",
                "text": "Chapter 1\nOpening frame",
                "locator": {
                    "href": "chapter-1.xhtml",
                    "start_cfi": "epubcfi(/6/2!/4/2)",
                    "end_cfi": "epubcfi(/6/2!/4/2)",
                    "paragraph_start": 1,
                    "paragraph_end": 1,
                },
            },
            "chapter_reflection": {"chapter_insights": ["Arc"]},
            "featured_reactions": [
                {
                    "reaction_id": "r1",
                    "type": "highlight",
                    "segment_ref": "1.1",
                    "anchor_quote": "Alpha beta",
                    "content": "Important line.",
                    "target_locator": {
                        "href": "chapter-1.xhtml",
                        "start_cfi": "epubcfi(/6/2!/4/2)",
                        "end_cfi": "epubcfi(/6/2!/4/2)",
                        "match_text": "Alpha beta",
                        "match_mode": "exact",
                    },
                }
            ],
            "visible_reaction_count": 1,
            "reaction_type_diversity": 1,
            "ui_summary": {
                "kept_section_count": 1,
                "skipped_section_count": 0,
                "reaction_counts": {"highlight": 1},
            },
        },
    )
    asset_dir = output_dir / "_assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    (asset_dir / "source.epub").write_bytes(b"epub")
    return book_id


def test_user_marks_put_is_idempotent_and_overwrites(tmp_path):
    """Marks should be idempotent for the same value and overwrite on new values."""
    book_id = _bootstrap_book(tmp_path)

    first = put_mark(book_id=book_id, reaction_id="r1", mark_type="resonance", root=tmp_path)
    second = put_mark(book_id=book_id, reaction_id="r1", mark_type="resonance", root=tmp_path)
    third = put_mark(book_id=book_id, reaction_id="r1", mark_type="blindspot", root=tmp_path)

    assert first["reaction_id"] == "r1"
    assert second["mark_type"] == "resonance"
    assert third["mark_type"] == "blindspot"
    assert third["created_at"] == first["created_at"]
    assert len(list_book_marks(book_id, root=tmp_path)) == 1

    deleted = delete_mark("r1", root=tmp_path)
    assert deleted is True
    assert load_marks_state(tmp_path)["marks"] == {}


def test_legacy_known_mark_normalizes_to_resonance(tmp_path):
    """Legacy persisted mark_type=known should read back as resonance."""
    book_id = _bootstrap_book(tmp_path)
    _write_json(
        tmp_path / "state" / "user_marks.json",
        {
            "updated_at": "2026-03-07T00:00:00Z",
            "marks": {
                "r1": {
                    "reaction_id": "r1",
                    "book_id": book_id,
                    "book_title": "Demo Book",
                    "chapter_id": 1,
                    "chapter_ref": "Chapter 1",
                    "segment_ref": "1.1",
                    "reaction_type": "highlight",
                    "mark_type": "known",
                    "reaction_excerpt": "Important line.",
                    "anchor_quote": "Alpha beta",
                    "created_at": "2026-03-07T00:00:00Z",
                    "updated_at": "2026-03-07T00:00:00Z",
                }
            },
        },
    )

    marks_state = load_marks_state(tmp_path)
    assert marks_state["marks"]["r1"]["mark_type"] == "resonance"


def test_chapter_outline_endpoint_returns_sections_and_preview_text(tmp_path):
    """Chapter outline should expose compact semantic sections for the drawer."""
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    book_id = _bootstrap_book(tmp_path)

    response = client.get(f"/api/books/{to_api_book_id(book_id)}/chapters/1/outline")
    assert response.status_code == 200
    payload = response.json()

    assert payload["book_id"] == to_api_book_id(book_id)
    assert payload["chapter_id"] == 1
    assert payload["chapter_number"] == 1
    assert payload["chapter_ref"] == "Chapter 1"
    assert payload["title"] == "Chapter 1"
    assert payload["result_ready"] is True
    assert payload["status"] == "completed"
    assert payload["chapter_heading"] == {
        "label": "Chapter 1",
        "title": "Opening frame",
        "subtitle": None,
        "text": "Chapter 1\nOpening frame",
        "locator": {
            "href": "chapter-1.xhtml",
            "start_cfi": "epubcfi(/6/2!/4/2)",
            "end_cfi": "epubcfi(/6/2!/4/2)",
            "paragraph_start": 1,
            "paragraph_end": 1,
        },
    }
    assert payload["section_count"] == 1
    assert payload["sections"] == [
        {
            "section_ref": "1.1",
            "summary": "Segment 1",
            "preview_text": "Alpha beta",
            "visible_reaction_count": 1,
            "locator": {
                "href": "chapter-1.xhtml",
                "start_cfi": "epubcfi(/6/2!/4/2)",
                "end_cfi": "epubcfi(/6/2!/4/2)",
                "paragraph_start": 1,
                "paragraph_end": 1,
            },
        }
    ]


def test_chapter_outline_endpoint_returns_pending_stub_for_unready_chapter(tmp_path):
    """Not-ready chapters should still appear in the drawer without sections."""
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    manifest_path = _manifest_path(tmp_path / "output" / book_id)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["chapters"][0]["status"] = "pending"
    manifest["chapters"][0]["visible_reaction_count"] = 0
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _chapter_result_path(tmp_path / "output" / book_id).unlink()

    response = client.get(f"/api/books/{to_api_book_id(book_id)}/chapters/1/outline")
    assert response.status_code == 200
    payload = response.json()

    assert payload["result_ready"] is False
    assert payload["status"] == "pending"
    assert payload["chapter_heading"] is None
    assert payload["section_count"] == 1
    assert payload["sections"] == []


def test_chapter_endpoint_falls_back_to_attentional_v2_compatibility_result_when_manifest_hint_is_missing(tmp_path):
    """Chapter detail should still load when attentional compatibility results exist but manifest result_file is absent."""

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    book_id = _bootstrap_book(tmp_path)
    output_dir = tmp_path / "output" / book_id

    manifest_path = _manifest_path(output_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["chapters"][0].pop("result_file", None)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    public_result_path = _chapter_result_path(output_dir)
    compatibility_result_path = chapter_result_compatibility_file(output_dir, 1)
    compatibility_result_path.parent.mkdir(parents=True, exist_ok=True)
    compatibility_result_path.write_text(public_result_path.read_text(encoding="utf-8"), encoding="utf-8")
    public_result_path.unlink()

    response = client.get(f"/api/books/{to_api_book_id(book_id)}/chapters/1")
    assert response.status_code == 200
    payload = response.json()

    assert payload["chapter_id"] == 1
    assert payload["visible_reaction_count"] == 1
    assert payload["sections"][0]["section_ref"] == "1.1"


def test_bookshelf_omits_stale_opaque_stub_uploads(tmp_path):
    """The shelf should hide stale opaque upload/test stubs that never became real books."""

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    _bootstrap_book(tmp_path)

    stub_output_dir = tmp_path / "output" / "0cfbde9bedca"
    stub_output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        _manifest_path(stub_output_dir),
        {
            "book_id": "0cfbde9bedca",
            "book": "0cfbde9bedca",
            "author": "Unknown",
            "cover_image_url": None,
            "book_language": "en",
            "output_language": "en",
            "source_file": str((tmp_path / "state" / "uploads" / "0cfbde9bedca.epub").resolve()),
            "source_asset": {"format": "epub", "file": "_assets/source.epub"},
            "updated_at": "2026-03-17T13:14:09.971535Z",
            "chapters": [],
        },
    )

    response = client.get("/api/books")
    assert response.status_code == 200
    items = response.json()["items"]

    assert [item["title"] for item in items] == ["Demo Book"]


def test_refresh_job_picks_up_book_id_from_generated_artifacts(tmp_path):
    """Job refresh should populate book_id once manifests become available."""
    upload_path = upload_file("job123", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    _bootstrap_book(tmp_path)

    save_job(
        {
            "job_id": "job123",
            "status": "queued",
            "upload_path": str(upload_path),
            "book_id": None,
            "pid": None,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    refreshed = refresh_job("job123", root=tmp_path)

    assert refreshed["book_id"] == "demo-book"
    assert refreshed["status"] == "completed"


def test_refresh_job_matches_uploaded_copy_via_source_asset_digest(tmp_path):
    """Job refresh should still resolve the book when the upload is a copied file with the same EPUB bytes."""
    upload_path = upload_file("job999", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    book_id = _bootstrap_book(tmp_path)
    manifest_path = _manifest_path(tmp_path / "output" / book_id)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_file"] = str((tmp_path / "data" / "original.epub").resolve())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    save_job(
        {
            "job_id": "job999",
            "status": "queued",
            "upload_path": str(upload_path),
            "book_id": None,
            "pid": None,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    refreshed = refresh_job("job999", root=tmp_path)

    assert refreshed["book_id"] == "demo-book"
    assert refreshed["status"] == "completed"


def test_refresh_job_auto_resumes_reaped_child(tmp_path, monkeypatch):
    """Zombie child processes should resume from the latest checkpoint budget when possible."""
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-zombie", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 8765

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    save_job(
        {
            "job_id": "job-zombie",
            "status": "queued",
            "upload_path": str(upload_path),
            "book_id": None,
            "pid": 4321,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    monkeypatch.setattr(jobs_module.os, "waitpid", lambda pid, flags: (4321, 0))
    monkeypatch.setattr(jobs_module.os, "kill", lambda pid, sig: (_ for _ in ()).throw(AssertionError("kill should not run")))

    refreshed = refresh_job("job-zombie", root=tmp_path)

    assert refreshed["status"] == "parsing_structure"
    assert refreshed["pid"] == 8765
    assert refreshed["resume_count"] == 1
    assert launched


def test_launch_sequential_job_records_runtime_environment_error_when_python_is_unsupported(tmp_path, monkeypatch):
    """Job launch should fail clearly when the backend runs under an unsupported interpreter."""
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-env", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    book_id = _bootstrap_book(tmp_path, stage="ready")

    monkeypatch.setattr(jobs_module, "_python_runtime_issue", lambda: "unsupported python runtime")

    record = jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id=book_id)
    activity = _load_jsonl(existing_activity_file(tmp_path / "output" / book_id))

    assert record["status"] == "error"
    assert "unsupported python runtime" in str(record["error"])
    assert activity[-1]["type"] == "runtime_environment_error"


def test_launch_sequential_job_persists_non_default_mechanism_key(tmp_path, monkeypatch):
    """Launching iterator_v1 as a fallback should persist the mechanism key and pass the CLI flag."""

    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-attn", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 5555

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    record = jobs_module.launch_sequential_job(
        upload_path,
        root=tmp_path,
        mechanism_key="iterator_v1",
        intent="focus on the book's interpretive pressure",
        memory_retrieval_mode="text_only",
    )
    persisted = jobs_module.load_job(str(record["job_id"]), root=tmp_path)

    assert launched
    assert "--mechanism" in launched[0]
    assert "iterator_v1" in launched[0]
    assert "--memory-retrieval-mode" in launched[0]
    assert "text_only" in launched[0]
    assert persisted["mechanism_key"] == "iterator_v1"
    assert persisted["memory_retrieval_mode"] == "text_only"
    assert persisted["job_kind"] == "read"
    assert job_record_file(str(record["job_id"]), tmp_path).exists()


def test_launch_sequential_job_persists_fenced_attempt_and_private_worker_environment(tmp_path, monkeypatch):
    """Managed launches should persist token-free metadata and pass the private grant only through env."""

    jobs_module = importlib.import_module("src.library.jobs")
    lease_module = importlib.import_module("src.reading_runtime.job_lease")
    monkeypatch.setattr(lease_module, "process_birth_identity", lambda pid=None: f"birth-{pid}")
    upload_path = upload_file("job-leased", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    observed: dict[str, object] = {}

    class _FakeProcess:
        pid = 5656

    def _launch(command, cwd, stdout, stderr, env=None):
        observed.update({"command": command, "env": env})
        return _FakeProcess()

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _launch)

    record = jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id="book-leased")
    environment = observed["env"]
    assert isinstance(environment, dict)

    assert record["run_attempt_id"] == environment[ENV_RUN_ATTEMPT_ID]
    assert record["lease"]["generation"] == 1
    assert record["lease"]["owner_pid"] == 5656
    assert record["lease"]["owner_birth_identity"] == "birth-5656"
    assert record["lease"]["valid"] is True
    assert environment[ENV_JOB_ID] == "job-leased"
    assert environment[ENV_LEASE_GENERATION] == "1"
    assert environment[ENV_RUNTIME_ROOT] == str(tmp_path.resolve())
    assert environment[ENV_BOOK_ID] == "book-leased"
    assert environment[ENV_JOB_KIND] == "read"
    assert environment[ENV_MECHANISM_KEY] == "attentional_v2"
    assert environment[ENV_LEASE_TOKEN]
    assert environment[ENV_LEASE_TOKEN] not in json.dumps(record)
    assert environment[ENV_LEASE_TOKEN] not in str(record["command"])
    assert environment[ENV_LEASE_TOKEN] not in job_record_file("job-leased", tmp_path).read_text(encoding="utf-8")
    assert environment[ENV_LEASE_TOKEN] not in (tmp_path / "state" / "jobs" / "job-leased.json").read_text(encoding="utf-8")


def test_process_running_fails_closed_on_permission_or_transient_probe_error(monkeypatch):
    jobs_module = importlib.import_module("src.library.jobs")
    monkeypatch.setattr(jobs_module.os, "waitpid", lambda *_args: (_ for _ in ()).throw(ChildProcessError()))

    monkeypatch.setattr(
        jobs_module.os,
        "kill",
        lambda *_args: (_ for _ in ()).throw(PermissionError("not our process")),
    )
    assert jobs_module._process_running(1234) is True

    monkeypatch.setattr(
        jobs_module.os,
        "kill",
        lambda *_args: (_ for _ in ()).throw(InterruptedError("retry later")),
    )
    assert jobs_module._process_running(1234) is True

    monkeypatch.setattr(
        jobs_module.os,
        "kill",
        lambda *_args: (_ for _ in ()).throw(ProcessLookupError()),
    )
    assert jobs_module._process_running(1234) is False


def test_prelaunch_registry_failure_releases_fresh_lease_without_starting_child(
    tmp_path,
    monkeypatch,
):
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-prelaunch-registry-failure", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    popen_called = False

    def _popen(*_args, **_kwargs):
        nonlocal popen_called
        popen_called = True
        raise AssertionError("child must not start before the initial registry record is durable")

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _popen)
    monkeypatch.setattr(
        jobs_module,
        "save_job",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("initial registry persistence failed")
        ),
    )

    with pytest.raises(RuntimeError, match="initial registry persistence failed"):
        jobs_module.launch_sequential_job(upload_path, root=tmp_path)

    assert popen_called is False
    assert jobs_module.load_job_lease(
        "job-prelaunch-registry-failure",
        root=tmp_path,
    )["state"] == "released"


def test_distinct_upload_jobs_with_identical_source_bytes_share_one_worker_lock(
    tmp_path,
    monkeypatch,
):
    """Pre-provision uploads must not bypass duplicate-book fencing when book_id is unknown."""

    jobs_module = importlib.import_module("src.library.jobs")
    first_upload = upload_file("job-source-lock-first", tmp_path)
    second_upload = upload_file("job-source-lock-second", tmp_path)
    first_upload.parent.mkdir(parents=True, exist_ok=True)
    first_upload.write_bytes(b"same-epub-bytes")
    second_upload.write_bytes(b"same-epub-bytes")
    popen_calls = 0
    job_lease_module = importlib.import_module("src.reading_runtime.job_lease")

    monkeypatch.setattr(
        jobs_module,
        "inspect_book",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("invalid epub")),
    )
    monkeypatch.setattr(job_lease_module, "process_birth_identity", lambda _pid: "test-birth")

    class _FakeProcess:
        pid = 5655

    def _popen(*_args, **_kwargs):
        nonlocal popen_calls
        popen_calls += 1
        return _FakeProcess()

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _popen)

    first = jobs_module.launch_sequential_job(first_upload, root=tmp_path)
    with pytest.raises(JobLeaseConflict, match="already has a worker"):
        jobs_module.launch_sequential_job(second_upload, root=tmp_path)

    assert popen_calls == 1
    assert first["book_id"] is None
    assert jobs_module.load_job_lease(first["job_id"], root=tmp_path)[
        "book_id"
    ].startswith("source-sha256:")


def test_distinct_sources_resolving_to_same_output_share_one_worker_lock(
    tmp_path,
    monkeypatch,
):
    """Different EPUB bytes with one canonical output id must not run concurrently."""

    jobs_module = importlib.import_module("src.library.jobs")
    first_upload = upload_file("job-title-lock-first", tmp_path)
    second_upload = upload_file("job-title-lock-second", tmp_path)
    first_upload.parent.mkdir(parents=True, exist_ok=True)
    first_upload.write_bytes(b"first-epub")
    second_upload.write_bytes(b"second-epub")
    popen_calls = 0
    job_lease_module = importlib.import_module("src.reading_runtime.job_lease")

    monkeypatch.setattr(
        jobs_module,
        "inspect_book",
        lambda *_args, **_kwargs: SimpleNamespace(output_dir=Path("output/shared-title")),
    )
    monkeypatch.setattr(job_lease_module, "process_birth_identity", lambda _pid: "test-birth")

    class _FakeProcess:
        pid = 5656

    def _popen(*_args, **_kwargs):
        nonlocal popen_calls
        popen_calls += 1
        return _FakeProcess()

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _popen)

    first = jobs_module.launch_sequential_job(first_upload, root=tmp_path)
    with pytest.raises(JobLeaseConflict, match="already has a worker"):
        jobs_module.launch_sequential_job(second_upload, root=tmp_path)

    assert popen_calls == 1
    assert jobs_module.load_job_lease(first["job_id"], root=tmp_path)["book_id"] == "shared-title"


def test_launch_heartbeat_failure_terminates_and_reaps_child_before_releasing_lease(tmp_path, monkeypatch):
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-heartbeat-failure", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    events: list[str] = []

    class _FakeProcess:
        pid = 5666

        def poll(self):
            events.append("poll")
            return None

        def terminate(self):
            events.append("terminate")

        def wait(self, *, timeout):
            events.append(f"wait:{timeout}")
            return -15

        def kill(self):
            raise AssertionError("graceful termination should have been enough")

    original_release = jobs_module.release_job_lease

    def _release(grant):
        events.append("release")
        return original_release(grant)

    monkeypatch.setattr(jobs_module.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(
        jobs_module,
        "heartbeat_job_lease",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("heartbeat persistence failed")),
    )
    monkeypatch.setattr(jobs_module, "release_job_lease", _release)

    with pytest.raises(RuntimeError, match="heartbeat persistence failed"):
        jobs_module.launch_sequential_job(upload_path, root=tmp_path)

    assert events == ["poll", "terminate", "wait:5.0", "release"]
    assert jobs_module.load_job_lease("job-heartbeat-failure", root=tmp_path)["state"] == "released"


def test_post_launch_registry_failure_terminates_and_reaps_child_before_releasing_lease(tmp_path, monkeypatch):
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-registry-failure", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    events: list[str] = []

    class _FakeProcess:
        pid = 5677

        def poll(self):
            events.append("poll")
            return None

        def terminate(self):
            events.append("terminate")

        def wait(self, *, timeout):
            events.append(f"wait:{timeout}")
            return -15

        def kill(self):
            raise AssertionError("graceful termination should have been enough")

    original_save = jobs_module.save_job
    original_release = jobs_module.release_job_lease
    save_count = 0

    def _save(record, root=None):
        nonlocal save_count
        save_count += 1
        if save_count == 2:
            raise RuntimeError("canonical registry persistence failed")
        return original_save(record, root)

    def _release(grant):
        events.append("release")
        return original_release(grant)

    monkeypatch.setattr(jobs_module.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(jobs_module, "save_job", _save)
    monkeypatch.setattr(jobs_module, "release_job_lease", _release)

    with pytest.raises(RuntimeError, match="canonical registry persistence failed"):
        jobs_module.launch_sequential_job(upload_path, root=tmp_path)

    assert save_count == 2
    assert events == ["poll", "terminate", "wait:5.0", "release"]
    assert jobs_module.load_job_lease("job-registry-failure", root=tmp_path)["state"] == "released"


def test_resume_registry_failure_terminates_and_reaps_new_child_before_releasing_lease(tmp_path, monkeypatch):
    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-resume-registry-failure", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    events: list[str] = []

    class _FakeProcess:
        pid = 5688

        def poll(self):
            events.append("poll")
            return None

        def terminate(self):
            events.append("terminate")

        def wait(self, *, timeout):
            events.append(f"wait:{timeout}")
            return -15

        def kill(self):
            raise AssertionError("graceful termination should have been enough")

    record = {
        "job_id": "job-resume-registry-failure",
        "status": "paused",
        "job_kind": "read",
        "upload_path": str(upload_path),
        "book_id": None,
        "pid": None,
        "run_attempt_id": None,
        "lease": {},
        "created_at": "2026-03-07T00:00:00Z",
        "updated_at": "2026-03-07T00:00:00Z",
        "error": None,
    }
    original_release = jobs_module.release_job_lease

    def _release(grant):
        events.append("release")
        return original_release(grant)

    monkeypatch.setattr(jobs_module, "find_book_id_by_source", lambda *args, **kwargs: None)
    monkeypatch.setattr(jobs_module, "_resume_target_status", lambda *args, **kwargs: "deep_reading")
    monkeypatch.setattr(jobs_module, "_resume_mechanism_key", lambda *args, **kwargs: "attentional_v2")
    monkeypatch.setattr(jobs_module, "_worker_liveness", lambda *args, **kwargs: (False, None, {}, False))
    monkeypatch.setattr(jobs_module, "_fence_and_terminate", lambda *args, **kwargs: ({}, True))
    monkeypatch.setattr(jobs_module.subprocess, "Popen", lambda *args, **kwargs: _FakeProcess())
    monkeypatch.setattr(
        jobs_module,
        "save_job",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("resume registry persistence failed")),
    )
    monkeypatch.setattr(jobs_module, "release_job_lease", _release)

    with pytest.raises(RuntimeError, match="resume registry persistence failed"):
        jobs_module._resume_job(record, tmp_path, automatic=False)

    assert events == ["poll", "terminate", "wait:5.0", "release"]
    assert jobs_module.load_job_lease("job-resume-registry-failure", root=tmp_path)["state"] == "released"


def test_failed_resume_with_newer_released_generation_can_retry(tmp_path, monkeypatch):
    """A failed resume must not leave the older registry generation permanently fenced out."""

    jobs_module = importlib.import_module("src.library.jobs")
    lease_module = importlib.import_module("src.reading_runtime.job_lease")
    upload_path = upload_file("job-resume-retry", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    first = jobs_module._acquire_worker_lease(
        job_id="job-resume-retry",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id=None,
        root=tmp_path,
    )
    first_payload = jobs_module.load_job_lease(first.job_id, root=tmp_path)
    original_record = jobs_module.save_job(
        {
            "job_id": first.job_id,
            "status": "paused",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": None,
            "pid": None,
            "run_attempt_id": first.run_attempt_id,
            "lease": jobs_module.sanitized_lease_metadata(first_payload),
        },
        tmp_path,
    )
    pids = iter((5689, 5690))
    terminated: list[int] = []

    class _FakeProcess:
        def __init__(self, pid: int):
            self.pid = pid

        def poll(self):
            return None

        def terminate(self):
            terminated.append(self.pid)

        def wait(self, *, timeout):
            return -15

        def kill(self):
            raise AssertionError("graceful termination should have been enough")

    monkeypatch.setattr(lease_module, "process_birth_identity", lambda pid=None: f"birth-{pid}")
    monkeypatch.setattr(jobs_module, "find_book_id_by_source", lambda *args, **kwargs: None)
    monkeypatch.setattr(jobs_module, "_resume_target_status", lambda *args, **kwargs: "deep_reading")
    monkeypatch.setattr(jobs_module, "_resume_mechanism_key", lambda *args, **kwargs: "attentional_v2")
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda *args, **kwargs: _FakeProcess(next(pids)),
    )

    with monkeypatch.context() as failed_registry:
        failed_registry.setattr(
            jobs_module,
            "save_job",
            lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("registry unavailable")),
        )
        with pytest.raises(RuntimeError, match="registry unavailable"):
            jobs_module._resume_job(original_record, tmp_path, automatic=False)

    persisted = jobs_module.load_job(first.job_id, root=tmp_path)
    released = jobs_module.load_job_lease(first.job_id, root=tmp_path)
    resumed = jobs_module._resume_job(persisted, tmp_path, automatic=False)

    assert persisted["lease"]["generation"] == 1
    assert released["generation"] == 2
    assert released["state"] == "released"
    assert resumed["lease"]["generation"] == 3
    assert resumed["run_attempt_id"] not in {first.run_attempt_id, released["run_attempt_id"]}
    assert terminated == [5689]


def test_refresh_job_uses_fresh_process_lease_instead_of_mechanism_heartbeat(tmp_path, monkeypatch):
    """A fresh process lease should keep an active job live even when run_state itself is quiet."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")
    upload_path = upload_file("job-fresh-lease", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")

    class _FakeProcess:
        pid = 5757

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: _FakeProcess(),
    )
    jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id=book_id)
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 5757)
    monkeypatch.setattr(jobs_module, "ACTIVE_RUNTIME_STALE_SECONDS", 1)
    monkeypatch.setattr(jobs_module, "_seconds_since", lambda _value: 120.0)

    refreshed = refresh_job("job-fresh-lease", root=tmp_path)

    assert refreshed["status"] == "deep_reading"
    assert refreshed["pid"] == 5757
    assert refreshed["lease"]["valid"] is True
    assert "job_lease_heartbeat_lost" not in {item["type"] for item in _load_jsonl(existing_activity_file(output_dir))}


def test_refresh_job_pauses_but_does_not_kill_worker_with_expired_lease(tmp_path, monkeypatch):
    """Refresh is observational: an alive PID with a lost lease must await explicit recovery."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    upload_path = upload_file("job-expired-lease", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    launches: list[list[str]] = []

    class _FakeProcess:
        pid = 5858

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launches.append(command) or _FakeProcess(),
    )
    jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id=book_id)
    lease_path = job_lease_file("job-expired-lease", root=tmp_path)
    lease_payload = json.loads(lease_path.read_text(encoding="utf-8"))
    lease_payload["expires_at"] = "2026-03-07T00:00:00Z"
    _write_json(lease_path, lease_payload)
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 5858)
    monkeypatch.setattr(jobs_module.os, "kill", lambda pid, sig: terminated.append(pid))

    refreshed = refresh_job("job-expired-lease", root=tmp_path)
    activity = _load_jsonl(existing_activity_file(tmp_path / "output" / book_id))

    assert refreshed["status"] == "paused"
    assert refreshed["pid"] == 5858
    assert refreshed["lease"]["valid"] is False
    assert refreshed["lease"]["status_reason"] == "heartbeat_lost"
    assert len(launches) == 1
    assert terminated == []
    assert activity[-1]["type"] == "job_lease_heartbeat_lost"


def test_manual_resume_fences_old_attempt_waits_for_exit_and_rotates_generation(tmp_path, monkeypatch):
    """An explicit resume may replace an expired owner only after its PID is confirmed gone."""

    jobs_module = importlib.import_module("src.library.jobs")
    lease_module = importlib.import_module("src.reading_runtime.job_lease")
    def birth_identity(pid=None):
        return f"birth-{pid}"

    monkeypatch.setattr(lease_module, "process_birth_identity", birth_identity)
    monkeypatch.setattr(jobs_module, "process_birth_identity", birth_identity)
    book_id = _bootstrap_book(tmp_path, stage="paused")
    upload_path = upload_file("job-manual-resume", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    launched_envs: list[dict[str, str]] = []
    pids = iter((5959, 5960))

    class _FakeProcess:
        def __init__(self, pid):
            self.pid = pid

    def _launch(command, cwd, stdout, stderr, env=None):
        launched_envs.append(dict(env or {}))
        return _FakeProcess(next(pids))

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _launch)
    initial = jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id=book_id)
    lease_path = job_lease_file("job-manual-resume", root=tmp_path)
    lease_payload = json.loads(lease_path.read_text(encoding="utf-8"))
    lease_payload["expires_at"] = "2026-03-07T00:00:00Z"
    _write_json(lease_path, lease_payload)
    alive = {5959: True, 5960: True}
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: bool(pid and alive.get(pid, False)))

    def _terminate(pid, sig):
        terminated.append(pid)
        alive[pid] = False

    monkeypatch.setattr(jobs_module.os, "kill", _terminate)

    resumed = jobs_module.resume_job_for_book(book_id, root=tmp_path)

    assert terminated == [5959]
    assert len(launched_envs) == 2
    assert resumed["pid"] == 5960
    assert resumed["resume_count"] == 1
    assert resumed["run_attempt_id"] != initial["run_attempt_id"]
    assert resumed["lease"]["generation"] == 2
    assert launched_envs[1][ENV_RUN_ATTEMPT_ID] == resumed["run_attempt_id"]
    assert launched_envs[1][ENV_LEASE_GENERATION] == "2"


def test_manual_resume_does_not_launch_when_old_worker_will_not_exit(tmp_path, monkeypatch):
    """A fenced but still-live PID must block the replacement launch."""

    jobs_module = importlib.import_module("src.library.jobs")
    lease_module = importlib.import_module("src.reading_runtime.job_lease")
    def birth_identity(pid=None):
        return f"birth-{pid}"

    monkeypatch.setattr(lease_module, "process_birth_identity", birth_identity)
    monkeypatch.setattr(jobs_module, "process_birth_identity", birth_identity)
    book_id = _bootstrap_book(tmp_path, stage="paused")
    upload_path = upload_file("job-resume-blocked", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    launches = 0

    class _FakeProcess:
        pid = 6060

    def _launch(command, cwd, stdout, stderr, env=None):
        nonlocal launches
        launches += 1
        return _FakeProcess()

    monkeypatch.setattr(jobs_module.subprocess, "Popen", _launch)
    jobs_module.launch_sequential_job(upload_path, root=tmp_path, book_id=book_id)
    lease_path = job_lease_file("job-resume-blocked", root=tmp_path)
    lease_payload = json.loads(lease_path.read_text(encoding="utf-8"))
    lease_payload["expires_at"] = "2026-03-07T00:00:00Z"
    _write_json(lease_path, lease_payload)
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 6060)
    monkeypatch.setattr(jobs_module, "WORKER_TERMINATION_TIMEOUT_SECONDS", 0)
    monkeypatch.setattr(jobs_module.os, "kill", lambda pid, sig: None)

    with pytest.raises(RuntimeError, match="did not exit"):
        jobs_module.resume_job_for_book(book_id, root=tmp_path)

    persisted = jobs_module.load_job("job-resume-blocked", root=tmp_path)
    assert launches == 1
    assert persisted["status"] == "paused"
    assert persisted["pid"] == 6060


def test_concurrent_resume_decisions_launch_exactly_one_worker(tmp_path, monkeypatch):
    """The per-job lease lock should let one concurrent resume win before Popen."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="paused")
    upload_path = upload_file("job-concurrent-resume", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-concurrent-resume",
            "status": "paused",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": None,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )
    record = jobs_module.load_job("job-concurrent-resume", root=tmp_path)
    acquire_barrier = threading.Barrier(2)
    original_acquire = jobs_module._acquire_worker_lease
    launch_count = 0
    launch_guard = threading.Lock()

    def _synchronized_acquire(**kwargs):
        acquire_barrier.wait(timeout=1)
        return original_acquire(**kwargs)

    class _FakeProcess:
        pid = 6161

    def _launch(command, cwd, stdout, stderr, env=None):
        nonlocal launch_count
        with launch_guard:
            launch_count += 1
        return _FakeProcess()

    monkeypatch.setattr(jobs_module, "_acquire_worker_lease", _synchronized_acquire)
    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: False)
    monkeypatch.setattr(jobs_module.subprocess, "Popen", _launch)

    def _resume():
        try:
            return jobs_module._resume_job(record, tmp_path, automatic=False)
        except JobLeaseConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [future.result() for future in [executor.submit(_resume), executor.submit(_resume)]]

    assert launch_count == 1
    assert results.count("conflict") == 1
    winner = next(result for result in results if result != "conflict")
    assert winner["run_attempt_id"]
    assert winner["lease"]["generation"] == 1


def test_refresh_does_not_overwrite_a_newer_resume_generation(tmp_path, monkeypatch):
    """A refresh snapshot may persist only while its lease generation remains current."""

    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-refresh-cas", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    first = jobs_module._acquire_worker_lease(
        job_id="job-refresh-cas",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id=None,
        root=tmp_path,
    )
    first_payload = jobs_module.heartbeat_job_lease(
        first,
        owner_pid=6162,
        owner_birth_identity="birth-old",
    )
    first_record = jobs_module.save_job(
        {
            "job_id": first.job_id,
            "status": "queued",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": None,
            "pid": 6162,
            "run_attempt_id": first.run_attempt_id,
            "lease": jobs_module.sanitized_lease_metadata(first_payload),
        },
        tmp_path,
    )
    snapshot_loaded = threading.Event()
    allow_refresh_save = threading.Event()

    def _blocked_liveness(*_args, **_kwargs):
        snapshot_loaded.set()
        assert allow_refresh_save.wait(timeout=1)
        return True, 6162, first_payload, True

    monkeypatch.setattr(jobs_module, "_worker_liveness", _blocked_liveness)
    monkeypatch.setattr(jobs_module, "find_book_id_by_source", lambda *args, **kwargs: None)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(jobs_module.refresh_job, first.job_id, tmp_path)
        assert snapshot_loaded.wait(timeout=1)
        try:
            jobs_module.fence_job_lease(
                first.job_id,
                root=tmp_path,
                expected_run_attempt_id=first.run_attempt_id,
                expected_generation=first.generation,
            )
            second = jobs_module._acquire_worker_lease(
                job_id=first.job_id,
                job_kind="read",
                mechanism_key="attentional_v2",
                book_id=None,
                root=tmp_path,
            )
            second_payload = jobs_module.heartbeat_job_lease(
                second,
                owner_pid=6163,
                owner_birth_identity="birth-new",
            )
            jobs_module.save_job(
                {
                    **first_record,
                    "status": "deep_reading",
                    "pid": 6163,
                    "run_attempt_id": second.run_attempt_id,
                    "lease": jobs_module.sanitized_lease_metadata(second_payload),
                },
                tmp_path,
            )
        finally:
            allow_refresh_save.set()
        refreshed = future.result(timeout=1)

    persisted = jobs_module.load_job(first.job_id, root=tmp_path)
    assert refreshed["run_attempt_id"] == second.run_attempt_id
    assert persisted["run_attempt_id"] == second.run_attempt_id
    assert persisted["lease"]["generation"] == 2


def test_stale_resume_fence_never_terminates_newer_generation_owner(tmp_path, monkeypatch):
    """A losing resume decision must not signal the worker that won the next lease generation."""

    jobs_module = importlib.import_module("src.library.jobs")
    first = jobs_module._acquire_worker_lease(
        job_id="job-stale-resume",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id="book-stale-resume",
        root=tmp_path,
    )
    jobs_module.heartbeat_job_lease(first, owner_pid=6261)
    stale_record = {
        "job_id": first.job_id,
        "run_attempt_id": first.run_attempt_id,
        "lease": {"generation": first.generation},
        "pid": 6261,
    }
    jobs_module.fence_job_lease(
        first.job_id,
        root=tmp_path,
        expected_run_attempt_id=first.run_attempt_id,
        expected_generation=first.generation,
    )
    second = jobs_module._acquire_worker_lease(
        job_id=first.job_id,
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id="book-stale-resume",
        root=tmp_path,
    )
    jobs_module.heartbeat_job_lease(second, owner_pid=6262)
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid in {6261, 6262})
    monkeypatch.setattr(jobs_module, "_terminate_process", terminated.append)

    with pytest.raises(JobLeaseConflict, match="newer worker lease"):
        jobs_module._fence_and_terminate(stale_record, root=tmp_path)

    assert terminated == []


def test_stale_resume_does_not_reconcile_a_released_but_still_live_newer_owner(
    tmp_path,
    monkeypatch,
):
    """Released generations are recoverable only after their exact owner is gone."""

    jobs_module = importlib.import_module("src.library.jobs")
    first = jobs_module._acquire_worker_lease(
        job_id="job-newer-released-live",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id=None,
        root=tmp_path,
    )
    stale_record = {
        "job_id": first.job_id,
        "run_attempt_id": first.run_attempt_id,
        "lease": {"generation": first.generation},
        "pid": None,
    }
    jobs_module.fence_job_lease(
        first.job_id,
        root=tmp_path,
        expected_run_attempt_id=first.run_attempt_id,
        expected_generation=first.generation,
    )
    second = jobs_module._acquire_worker_lease(
        job_id=first.job_id,
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id=None,
        root=tmp_path,
    )
    jobs_module.heartbeat_job_lease(
        second,
        owner_pid=6263,
        owner_birth_identity="birth-newer-live",
    )
    jobs_module.release_job_lease(second)
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 6263)
    monkeypatch.setattr(jobs_module, "process_birth_identity", lambda pid: "birth-newer-live")
    monkeypatch.setattr(jobs_module, "_terminate_process", terminated.append)

    with pytest.raises(JobLeaseConflict, match="newer worker lease"):
        jobs_module._fence_and_terminate(stale_record, root=tmp_path)

    assert terminated == []


def test_resume_fence_never_signals_a_reused_pid(tmp_path, monkeypatch):
    """A stale integer PID must not authorize SIGTERM of a different process incarnation."""

    jobs_module = importlib.import_module("src.library.jobs")
    grant = jobs_module._acquire_worker_lease(
        job_id="job-pid-reused",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id="book-pid-reused",
        root=tmp_path,
    )
    lease_payload = jobs_module.heartbeat_job_lease(
        grant,
        owner_pid=6363,
        owner_birth_identity="birth-original-worker",
    )
    record = {
        "job_id": grant.job_id,
        "run_attempt_id": grant.run_attempt_id,
        "lease": jobs_module.sanitized_lease_metadata(lease_payload),
        "pid": 6363,
    }
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 6363)
    monkeypatch.setattr(jobs_module, "process_birth_identity", lambda _pid: "birth-unrelated-process")
    monkeypatch.setattr(jobs_module, "_terminate_process", terminated.append)

    _fenced, stopped = jobs_module._fence_and_terminate(record, root=tmp_path)

    assert stopped is True
    assert terminated == []


def test_resume_fence_rechecks_pid_identity_immediately_before_signal(
    tmp_path,
    monkeypatch,
):
    """A worker that exits after the first probe must not transfer SIGTERM to its reused PID."""

    jobs_module = importlib.import_module("src.library.jobs")
    grant = jobs_module._acquire_worker_lease(
        job_id="job-pid-reused-during-fence",
        job_kind="read",
        mechanism_key="attentional_v2",
        book_id="book-pid-reused-during-fence",
        root=tmp_path,
    )
    lease_payload = jobs_module.heartbeat_job_lease(
        grant,
        owner_pid=6364,
        owner_birth_identity="birth-original-worker",
    )
    record = {
        "job_id": grant.job_id,
        "run_attempt_id": grant.run_attempt_id,
        "lease": jobs_module.sanitized_lease_metadata(lease_payload),
        "pid": 6364,
    }
    identities = iter(("birth-original-worker", "birth-reused-process"))
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 6364)
    monkeypatch.setattr(jobs_module, "process_birth_identity", lambda _pid: next(identities))
    monkeypatch.setattr(jobs_module, "_terminate_process", terminated.append)

    _fenced, stopped = jobs_module._fence_and_terminate(record, root=tmp_path)

    assert stopped is True
    assert terminated == []


def test_legacy_record_never_authorizes_signal_from_pid_alone(monkeypatch):
    jobs_module = importlib.import_module("src.library.jobs")
    terminated: list[int] = []
    monkeypatch.setattr(jobs_module, "_process_running", lambda pid: pid == 6464)
    monkeypatch.setattr(jobs_module, "_terminate_process", terminated.append)

    _fenced, stopped = jobs_module._fence_and_terminate(
        {"job_id": "legacy-job", "pid": 6464}
    )

    assert stopped is False
    assert terminated == []


def test_launch_parse_job_records_memory_retrieval_mode_without_cli_flag(tmp_path, monkeypatch):
    """Deferred parse jobs may remember the later read mode without passing read-only CLI args."""

    jobs_module = importlib.import_module("src.library.jobs")
    upload_path = upload_file("job-parse-mode", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 3333

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    record = jobs_module.launch_parse_job(
        upload_path,
        root=tmp_path,
        memory_retrieval_mode="text_only",
    )
    persisted = jobs_module.load_job(str(record["job_id"]), root=tmp_path)

    assert launched
    assert "parse" in launched[0]
    assert "--memory-retrieval-mode" not in launched[0]
    assert persisted["memory_retrieval_mode"] == "text_only"
    assert persisted["job_kind"] == "parse"


def test_launch_existing_book_read_job_omits_default_mechanism_flag_for_attentional_v2(tmp_path, monkeypatch):
    """The canonical existing-book launcher should rely on the new default without forcing a CLI flag."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="ready")
    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 4444

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    record = jobs_module.launch_existing_book_read_job(
        book_id,
        root=tmp_path,
        mechanism_key="attentional_v2",
        memory_retrieval_mode="hybrid",
    )

    assert record["status"] == "queued"
    assert launched
    assert "--mode" in launched[0]
    assert "sequential" in launched[0]
    assert "--memory-retrieval-mode" in launched[0]
    assert "hybrid" in launched[0]
    assert "--mechanism" not in launched[0]


def test_launch_existing_book_read_job_allows_iterator_v1_fallback(tmp_path, monkeypatch):
    """The canonical existing-book deep-reading launcher should still allow explicit iterator_v1 fallback."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="ready")
    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 4445

    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    record = jobs_module.launch_existing_book_read_job(book_id, root=tmp_path, mechanism_key="iterator_v1")

    assert record["status"] == "queued"
    assert launched
    assert "--mechanism" in launched[0]
    assert "iterator_v1" in launched[0]


def test_launch_book_analysis_job_aliases_existing_book_read_job(tmp_path, monkeypatch):
    """The old launcher name should remain as a compatibility alias only."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="ready")
    observed: dict[str, object] = {}

    monkeypatch.setattr(
        jobs_module,
        "launch_existing_book_read_job",
        lambda internal_book_id, **kwargs: observed.update({"book_id": internal_book_id, **kwargs}) or {"job_id": "job-legacy", "status": "queued"},
    )

    record = jobs_module.launch_book_analysis_job(book_id, root=tmp_path, mechanism_key="iterator_v1", intent="legacy")

    assert record["job_id"] == "job-legacy"
    assert observed["book_id"] == book_id
    assert observed["mechanism_key"] == "iterator_v1"
    assert observed["intent"] == "legacy"


def test_refresh_job_pauses_running_job_when_runtime_updates_go_stale(tmp_path, monkeypatch):
    """Jobs that keep a live PID but stop updating runtime state should move into a diagnosable paused state."""
    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["current_chapter_id"] = 1
    run_state["current_chapter_ref"] = "Chapter 1"
    run_state["current_segment_ref"] = "1.2"
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    upload_path = upload_file("job-stalled", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-stalled",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: True)
    monkeypatch.setattr(jobs_module, "ACTIVE_RUNTIME_STALE_SECONDS", 1)
    monkeypatch.setattr(
        jobs_module,
        "_seconds_since",
        lambda value: 120.0 if str(value) == "2026-03-07T00:00:00Z" else 120.0,
    )

    refreshed = refresh_job("job-stalled", root=tmp_path)
    paused_run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    activity = _load_jsonl(existing_activity_file(output_dir))

    assert refreshed["status"] == "paused"
    assert "Runtime activity stalled" in str(refreshed["error"])
    assert paused_run_state["stage"] == "paused"
    assert {item["type"] for item in activity} >= {"runtime_stalled", "job_paused_by_runtime_guard"}


def test_orphan_stale_runtime_projects_to_paused_truth_and_last_known_snapshot(tmp_path):
    """Stale active runtime artifacts without active job truth should project as paused with last-known context."""

    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state["resume_available"] = True
    run_state["current_phase_step"] = "语义切分中"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_json(
        runtime_shell_file(output_dir),
        {
            "mechanism_key": "attentional_v2",
            "status": "running",
            "phase": "reading",
            "cursor": {
                "position_kind": "span",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "span_start_sentence_id": "c1-s1",
                "span_end_sentence_id": "c1-s2",
            },
            "resume_available": True,
            "last_checkpoint_id": "ckpt-stale",
            "last_checkpoint_at": "2026-03-15T07:04:56Z",
            "updated_at": "2026-03-15T07:04:56Z",
        },
    )

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    books_payload = client.get("/api/books").json()
    detail_payload = client.get(f"/api/books/{public_book_id}").json()
    analysis_payload = client.get(f"/api/books/{public_book_id}/analysis-state").json()

    assert books_payload["items"][0]["reading_status"] == "paused"
    assert books_payload["items"][0]["status_reason"] == "runtime_stale"
    assert detail_payload["status"] == "paused"
    assert detail_payload["status_reason"] == "runtime_stale"
    assert analysis_payload["status"] == "paused"
    assert analysis_payload["status_reason"] == "runtime_stale"
    assert analysis_payload["stage_label_key"] == "system.stage.paused"
    assert analysis_payload["current_phase_step_key"] == "system.step.waitingToResume"
    assert analysis_payload["resume_available"] is False
    assert analysis_payload["last_checkpoint_at"] == "2026-03-15T07:04:56Z"
    assert analysis_payload["current_state_panel"]["current_section_ref"] == "1.1"
    assert analysis_payload["current_reading_activity"]["phase"] == "reading"
    assert analysis_payload["current_reading_activity"]["reading_locus"] == {
        "kind": "span",
        "chapter_id": 1,
        "chapter_number": 1,
        "chapter_ref": "Chapter 1",
            "excerpt": "1.1",
            "locator": None,
            "start_cursor": None,
            "end_cursor": None,
            "sentence_start_id": "c1-s1",
            "sentence_end_id": "c1-s2",
        }


def test_recover_unfinished_jobs_reconciles_orphan_active_runs_without_duplicate_events(tmp_path):
    """Startup recovery should durably pause stale orphan runtimes and dedupe guard events."""

    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state["resume_available"] = True
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_json(
        runtime_shell_file(output_dir),
        {
            "mechanism_key": "attentional_v2",
            "status": "running",
            "phase": "reading",
            "resume_available": True,
            "last_checkpoint_id": "ckpt-stale",
            "last_checkpoint_at": "2026-03-15T07:04:56Z",
            "updated_at": "2026-03-15T07:04:56Z",
        },
    )

    recover_unfinished_jobs(root=tmp_path)
    recover_unfinished_jobs(root=tmp_path)

    paused_run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    activity = _load_jsonl(existing_activity_file(output_dir))
    runtime_stalled_events = [item for item in activity if item.get("type") == "runtime_stalled"]
    paused_guard_events = [item for item in activity if item.get("type") == "job_paused_by_runtime_guard"]

    assert paused_run_state["stage"] == "paused"
    assert paused_run_state["current_phase_step"] == "等待继续执行"
    assert paused_run_state["resume_available"] is False
    assert "Runtime activity stalled" in str(paused_run_state["error"])
    assert len(runtime_stalled_events) == 1
    assert len(paused_guard_events) == 1
    assert paused_guard_events[0]["details"]["resume_available"] is False
    assert paused_guard_events[0]["details"]["status_reason"] == "runtime_stale"


def test_refresh_job_abandons_old_dev_boot_runs(tmp_path, monkeypatch):
    """Development-mode jobs from an older boot should be abandoned instead of trusted."""
    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    upload_path = upload_file("job-old-dev", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-old-dev",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "boot_id": "old-boot",
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    terminated: list[int] = []
    process_alive = True

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: process_alive)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "dev")
    monkeypatch.setattr(jobs_module, "get_backend_boot_id", lambda: "new-boot")
    def _terminate(pid, sig):
        nonlocal process_alive
        terminated.append(pid)
        process_alive = False

    monkeypatch.setattr(jobs_module.os, "kill", _terminate)

    refreshed = refresh_job("job-old-dev", root=tmp_path)
    activity = _load_jsonl(existing_activity_file(tmp_path / "output" / book_id))

    assert refreshed["status"] == "paused"
    assert refreshed["pid"] == 1234
    assert "older development boot" in str(refreshed["error"])
    assert "did not exit" in str(refreshed["error"])
    assert terminated == []
    assert activity[-1]["type"] == "dev_run_abandoned"


def test_refresh_job_fresh_reruns_incompatible_prod_checkpoint(tmp_path, monkeypatch):
    """Demo/prod should discard incompatible live artifacts and start a fresh run."""
    jobs_module = importlib.import_module("src.library.jobs")
    compat_version = get_reader_resume_compat_version()
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    upload_path = upload_file("job-incompat", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-incompat",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": None,
            "resume_compat_version": compat_version - 1,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["resume_compat_version"] = compat_version - 1
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 8765

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: False)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "prod")
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    refreshed = refresh_job("job-incompat", root=tmp_path)
    activity = _load_jsonl(existing_activity_file(output_dir))
    reset_run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    structure = json.loads(_structure_path(output_dir).read_text(encoding="utf-8"))

    assert refreshed["job_id"] != "job-incompat"
    assert refreshed["pid"] == 8765
    assert launched and "--continue" not in launched[0]
    assert [item["type"] for item in activity[:2]] == ["resume_incompatible", "fresh_rerun_started"]
    assert reset_run_state["stage"] == "ready"
    assert reset_run_state["completed_chapters"] == 0
    assert structure["chapters"][0]["status"] == "pending"
    assert structure["chapters"][0]["segments"][0]["status"] == "pending"


def test_refresh_job_fresh_rerun_prefers_runtime_shell_mechanism_key(tmp_path, monkeypatch):
    """Fresh reruns should inherit the live mechanism key from the shared runtime shell."""

    jobs_module = importlib.import_module("src.library.jobs")
    compat_version = get_reader_resume_compat_version()
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    _write_json(
        runtime_shell_file(output_dir),
        {
            "mechanism_key": "attentional_v2",
            "mechanism_version": "attentional_v2-phase8",
            "policy_version": "attentional_v2-policy-v1",
            "status": "paused",
            "phase": "resume",
            "cursor": {},
            "active_artifact_refs": {},
            "resume_available": True,
            "last_checkpoint_id": "ckpt-1",
            "last_checkpoint_at": "2026-03-15T07:04:56Z",
            "updated_at": "2026-03-15T07:04:56Z",
        },
    )

    upload_path = upload_file("job-incompat-attn", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-incompat-attn",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": None,
            "resume_compat_version": compat_version - 1,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["resume_compat_version"] = compat_version - 1
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 8766

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: False)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "prod")
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    refreshed = refresh_job("job-incompat-attn", root=tmp_path)

    assert launched and "--continue" not in launched[0]
    assert "--mechanism" not in launched[0]
    assert refreshed["mechanism_key"] == "attentional_v2"


def test_refresh_job_pauses_stalled_live_worker_instead_of_auto_resuming(tmp_path, monkeypatch):
    """A stale runtime with a live PID must pause instead of launching a duplicate worker."""
    jobs_module = importlib.import_module("src.library.jobs")
    compat_version = get_reader_resume_compat_version()
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["resume_compat_version"] = compat_version
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    upload_path = upload_file("job-prod-stalled", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-prod-stalled",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "resume_compat_version": compat_version,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 2222

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: True)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "prod")
    monkeypatch.setattr(jobs_module, "ACTIVE_RUNTIME_STALE_SECONDS", 1)
    monkeypatch.setattr(jobs_module, "_seconds_since", lambda _value: 120.0)
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    refreshed = refresh_job("job-prod-stalled", root=tmp_path)
    activity = _load_jsonl(existing_activity_file(output_dir))

    assert refreshed["status"] == "paused"
    assert refreshed["pid"] == 1234
    assert refreshed["auto_resume_count"] == 0
    assert launched == []
    assert {item["type"] for item in activity} >= {"runtime_stalled", "job_paused_by_runtime_guard"}
    assert "resume_detected" not in {item["type"] for item in activity}


def test_refresh_job_auto_resume_prefers_runtime_shell_mechanism_key(tmp_path, monkeypatch):
    """Auto-resume should use the shared runtime-shell mechanism key before the persisted job record."""

    jobs_module = importlib.import_module("src.library.jobs")
    compat_version = get_reader_resume_compat_version()
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    _write_json(
        runtime_shell_file(output_dir),
        {
            "mechanism_key": "attentional_v2",
            "mechanism_version": "attentional_v2-phase8",
            "policy_version": "attentional_v2-policy-v1",
            "status": "running",
            "phase": "reading",
            "cursor": {},
            "active_artifact_refs": {},
            "resume_available": True,
            "last_checkpoint_id": "ckpt-1",
            "last_checkpoint_at": "2026-03-15T07:04:56Z",
            "updated_at": "2026-03-15T07:04:56Z",
        },
    )
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["resume_compat_version"] = compat_version
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    upload_path = upload_file("job-prod-stalled-attn", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-prod-stalled-attn",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "resume_compat_version": compat_version,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 3333

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: False)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "prod")
    monkeypatch.setattr(jobs_module, "ACTIVE_RUNTIME_STALE_SECONDS", 1)
    monkeypatch.setattr(jobs_module, "_seconds_since", lambda _value: 120.0)
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    refreshed = refresh_job("job-prod-stalled-attn", root=tmp_path)

    assert launched and "--continue" in launched[0]
    assert "--mechanism" not in launched[0]
    assert refreshed["mechanism_key"] == "attentional_v2"


def test_resume_mechanism_key_falls_back_to_legacy_iterator_artifacts(tmp_path):
    """Legacy iterator runs without shell or job metadata should still resume on iterator_v1 after the default flips."""

    jobs_module = importlib.import_module("src.library.jobs")
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")

    mechanism_key = jobs_module._resume_mechanism_key({"mechanism_key": None}, book_id=book_id, root=tmp_path)

    assert mechanism_key == "iterator_v1"


def test_refresh_job_auto_resume_preserves_legacy_iterator_when_metadata_is_missing(tmp_path, monkeypatch):
    """Auto-resume should keep old iterator runs on iterator_v1 even when old records predate mechanism metadata."""

    jobs_module = importlib.import_module("src.library.jobs")
    compat_version = get_reader_resume_compat_version()
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["resume_compat_version"] = compat_version
    run_state["updated_at"] = "2026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    upload_path = upload_file("job-prod-stalled-legacy-iterator", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-prod-stalled-legacy-iterator",
            "status": "deep_reading",
            "job_kind": "read",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "resume_compat_version": compat_version,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
        tmp_path,
    )

    launched: list[list[str]] = []

    class _FakeProcess:
        pid = 4446

    monkeypatch.setattr(jobs_module, "_process_running", lambda _pid: False)
    monkeypatch.setattr(jobs_module, "get_backend_run_mode", lambda: "prod")
    monkeypatch.setattr(jobs_module, "ACTIVE_RUNTIME_STALE_SECONDS", 1)
    monkeypatch.setattr(jobs_module, "_seconds_since", lambda _value: 120.0)
    monkeypatch.setattr(
        jobs_module.subprocess,
        "Popen",
        lambda command, cwd, stdout, stderr, env=None: launched.append(command) or _FakeProcess(),
    )

    refreshed = refresh_job("job-prod-stalled-legacy-iterator", root=tmp_path)

    assert launched and "--continue" in launched[0]
    assert "--mechanism" in launched[0]
    assert "iterator_v1" in launched[0]
    assert refreshed["mechanism_key"] == "iterator_v1"


def test_api_reads_books_chapters_marks_and_docs(tmp_path):
    """The API should expose typed bookshelf, result, marks, and docs endpoints."""
    book_id = _bootstrap_book(tmp_path)
    public_book_id = to_api_book_id(book_id)
    public_reaction_id = to_api_reaction_id(book_id=book_id, reaction_id="r1")
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert health_response.json()["service"] == "backend"
    assert health_response.json()["runtime_root"] == str(tmp_path)

    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200
    assert "/api/books" in openapi_response.json()["paths"]
    assert "/api/landing" not in openapi_response.json()["paths"]
    assert "/api/sample" not in openapi_response.json()["paths"]

    books_response = client.get("/api/books")
    assert books_response.status_code == 200
    books_payload = books_response.json()
    assert books_payload["items"][0]["book_id"] == public_book_id
    assert books_payload["items"][0]["open_target"] == f"/books/{public_book_id}"
    assert books_payload["page_info"]["has_more"] is False

    detail_response = client.get(f"/api/books/{public_book_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "Demo Book"

    analysis_response = client.get(f"/api/books/{public_book_id}/analysis-state")
    assert analysis_response.status_code == 200
    assert analysis_response.json()["status"] == "completed"
    assert analysis_response.json()["book_id"] == public_book_id

    activity_response = client.get(f"/api/books/{public_book_id}/activity")
    assert activity_response.status_code == 200
    assert activity_response.json()["items"][0]["event_id"] == "evt-1"
    assert activity_response.json()["items"][0]["stream"] == "mindstream"
    assert activity_response.json()["items"][0]["kind"] == "chapter_complete"
    assert activity_response.json()["items"][0]["visibility"] == "default"
    assert activity_response.json()["items"][0]["result_url"] == f"/books/{public_book_id}/chapters/1"

    chapter_response = client.get(f"/api/books/{public_book_id}/chapters/1")
    assert chapter_response.status_code == 200
    assert chapter_response.json()["book_id"] == public_book_id
    assert chapter_response.json()["featured_reactions"][0]["reaction_id"] == public_reaction_id
    assert chapter_response.json()["chapter_heading"]["title"] == "Opening frame"
    assert chapter_response.json()["featured_reactions"][0]["source_quote"] == "Alpha beta"
    assert chapter_response.json()["sections"][0]["reactions"][0]["source_quote"] == "Alpha beta"

    reactions_response = client.get(f"/api/books/{public_book_id}/chapters/1/reactions")
    assert reactions_response.status_code == 200
    assert reactions_response.json()["items"][0]["reaction_id"] == public_reaction_id

    source_response = client.get(f"/api/books/{public_book_id}/source")
    assert source_response.status_code == 200
    assert source_response.content == b"epub"

    put_response = client.put(
        f"/api/marks/{public_reaction_id}",
        json={"book_id": public_book_id, "mark_type": "resonance"},
    )
    assert put_response.status_code == 200
    assert put_response.json()["mark_type"] == "resonance"
    assert put_response.json()["reaction_id"] == public_reaction_id

    marks_response = client.get(f"/api/books/{public_book_id}/marks")
    assert marks_response.status_code == 200
    assert marks_response.json()["book_id"] == public_book_id
    assert marks_response.json()["groups"][0]["items"][0]["reaction_id"] == public_reaction_id
    assert isinstance(marks_response.json()["groups"][0]["items"][0]["mark_id"], int)
    assert marks_response.json()["groups"][0]["items"][0]["source_quote"] == "Alpha beta"

    global_marks_response = client.get("/api/marks")
    assert global_marks_response.status_code == 200
    assert global_marks_response.json()["items"][0]["reaction_id"] == public_reaction_id
    assert isinstance(global_marks_response.json()["items"][0]["mark_id"], int)
    assert global_marks_response.json()["items"][0]["source_quote"] == "Alpha beta"

    delete_response = client.delete(f"/api/marks/{public_reaction_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["reaction_id"] == public_reaction_id
    assert delete_response.json()["deleted"] is True


def test_book_activity_supports_stream_filter(tmp_path):
    """Activity API should filter mindstream and system events without splitting storage."""
    book_id = _bootstrap_book(tmp_path, stage="completed")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    _write_jsonl(
        _activity_path(output_dir),
        [
            {
                "event_id": "evt-1",
                "timestamp": "2026-03-07T00:00:00Z",
                "type": "chapter_completed",
                "message": "Chapter 1 完成，已生成结果文件。",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
            },
            {
                "event_id": "evt-2",
                "timestamp": "2026-03-07T00:00:01Z",
                "type": "structure_checkpoint_saved",
                "message": "已保存解析 checkpoint：Chapter 1",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
            },
        ],
    )

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    mindstream_response = client.get(f"/api/books/{public_book_id}/activity?stream=mindstream")
    system_response = client.get(f"/api/books/{public_book_id}/activity?stream=system")

    assert mindstream_response.status_code == 200
    assert system_response.status_code == 200
    assert [item["event_id"] for item in mindstream_response.json()["items"]] == ["evt-1"]
    assert [item["event_id"] for item in system_response.json()["items"]] == ["evt-2"]


def test_activity_result_url_is_hidden_until_chapter_workspace_is_ready(tmp_path):
    """Sentence-level activity items should not advertise a chapter URL until the result workspace exists."""
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    _chapter_result_path(output_dir).unlink(missing_ok=True)
    _write_jsonl(
        _activity_path(output_dir),
        [
            {
                "event_id": "evt-segment",
                "timestamp": "2026-03-07T00:00:02Z",
                "type": "segment_completed",
                "message": "Alpha beta",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "segment_ref": "1.1",
                "anchor_quote": "Alpha beta",
                "reaction_types": ["discern"],
                "visible_reactions": [
                    {
                        "reaction_id": "r1",
                        "type": "discern",
                        "anchor_quote": "Alpha beta",
                        "content": "Testing the opening claim.",
                    }
                ],
                "visible_reaction_count": 1,
            }
        ],
    )

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/activity")

    assert response.status_code == 200
    assert response.json()["items"][0]["event_id"] == "evt-segment"
    assert response.json()["items"][0]["result_url"] is None


def test_analysis_state_prefers_parse_checkpoint_during_structure_stage(tmp_path):
    """analysis-state should surface parse checkpoint details while the book is still preparing readable chapters."""
    book_id = _bootstrap_book(tmp_path, stage="parsing_structure")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    upload_path = upload_file("job-parse-live", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    save_job(
        {
            "job_id": "job-parse-live",
            "status": "parsing_structure",
            "job_kind": "parse",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": 1234,
            "created_at": "2026-03-14T01:00:00Z",
            "updated_at": "2026-03-14T01:00:00Z",
            "error": None,
        },
        tmp_path,
    )
    _write_json(
        parse_state_file(output_dir),
        {
            "status": "parsing_structure",
            "total_chapters": 3,
            "completed_chapters": 1,
            "parsed_chapter_ids": [1],
            "segmented_chapter_ids": [1],
            "inflight_chapter_ids": [2],
            "pending_chapter_ids": [2, 3],
            "current_chapter_id": 2,
            "current_chapter_ref": "Chapter 2",
            "current_step": "后台准备后续章节",
            "worker_limit": 3,
            "resume_available": True,
            "last_checkpoint_at": "2026-03-14T01:00:00Z",
            "updated_at": "2026-03-14T01:00:00Z",
            "error": None,
        },
    )

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/analysis-state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "parsing_structure"
    assert payload["completed_chapters"] == 1
    assert payload["total_chapters"] == 3
    assert payload["current_chapter_id"] == 2
    assert payload["current_chapter_number"] is None
    assert payload["current_chapter_ref"] == "Chapter 2"
    assert payload["current_phase_step_key"] == "system.step.prefetchFutureChapters"
    assert payload["current_phase_step_params"] is None
    assert payload["resume_available"] is True
    assert payload["stage_label_key"] == "system.stage.parsingChapter"
    assert payload["stage_label_params"] == {"chapter": "Chapter 2"}
    assert payload["pulse_message"] == "Preparing Chapter 2"


def test_analysis_state_exposes_current_reading_activity_snapshot(tmp_path):
    """analysis-state should expose the enriched live reading activity snapshot for the runtime panel."""
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["current_reading_activity"] = {
        "phase": "searching",
        "started_at": "2026-03-15T07:04:50Z",
        "updated_at": "2026-03-15T07:04:56Z",
        "segment_ref": "1.2",
        "current_excerpt": "Hormesis lost some scientific respect.",
        "search_query": "homeopathy decline toxicology threshold model",
        "thought_family": "curious",
        "problem_code": "search_timeout",
    }
    run_state["current_segment_ref"] = "1.2"
    run_state["updated_at"] = "2026-03-15T07:04:56Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/analysis-state")

    assert response.status_code == 200
    activity = response.json()["current_reading_activity"]
    assert activity["phase"] == "searching"
    assert activity["started_at"] == "2026-03-15T07:04:50Z"
    assert activity["updated_at"] == "2026-03-15T07:04:56Z"
    assert activity["segment_ref"] == "1.2"
    assert activity["current_excerpt"] == "Hormesis lost some scientific respect."
    assert activity["search_query"] == "homeopathy decline toxicology threshold model"
    assert activity["thought_family"] == "curious"
    assert activity["problem_code"] == "search_timeout"
    assert activity["reading_locus"] == {
        "kind": "span",
        "chapter_id": 1,
        "chapter_number": 1,
        "chapter_ref": "Chapter 1",
            "excerpt": "Hormesis lost some scientific respect.",
            "locator": None,
            "start_cursor": None,
            "end_cursor": None,
            "sentence_start_id": None,
            "sentence_end_id": None,
        }


def test_analysis_state_uses_runtime_shell_cursor_for_additive_locus_fields(tmp_path):
    """analysis-state should project the shared runtime-shell cursor into the additive reading-locus fields."""

    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    _write_json(
        runtime_shell_file(output_dir),
        {
            "mechanism_key": "attentional_v2",
            "mechanism_version": "attentional_v2-phase8",
            "policy_version": "attentional_v2-policy-v1",
            "status": "running",
            "phase": "bridge",
            "cursor": {
                "position_kind": "span",
                "chapter_id": 1,
                "chapter_ref": "Chapter 1",
                "span_start_sentence_id": "c1-s8",
                "span_end_sentence_id": "c1-s9",
            },
            "active_artifact_refs": {"reaction_id": "r1"},
            "resume_available": True,
            "last_checkpoint_id": "ckpt-1",
            "last_checkpoint_at": "2026-03-15T07:04:56Z",
            "updated_at": "2026-03-15T07:04:56Z",
        },
    )
    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["current_reading_activity"] = {
        "phase": "thinking",
        "started_at": "2026-03-15T07:04:50Z",
        "updated_at": "2026-03-15T07:04:56Z",
        "current_excerpt": "Alpha beta",
    }
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/analysis-state")

    assert response.status_code == 200
    payload = response.json()["current_reading_activity"]
    assert payload["reading_locus"] == {
        "kind": "span",
        "chapter_id": 1,
        "chapter_number": 1,
        "chapter_ref": "Chapter 1",
        "sentence_start_id": "c1-s8",
            "sentence_end_id": "c1-s9",
            "excerpt": "Alpha beta",
            "locator": None,
            "start_cursor": None,
            "end_cursor": None,
        }
    assert payload["active_reaction_id"] == to_api_reaction_id(book_id=book_id, reaction_id="r1")


def test_analysis_state_backfills_truncated_current_excerpt_from_structure(tmp_path):
    """analysis-state should restore a full live excerpt when older runtime snapshots stored an ellipsized preview."""
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id

    structure_path = _structure_path(output_dir)
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    structure["chapters"][0]["segments"][0]["text"] = "Alpha beta gamma delta epsilon."
    structure_path.write_text(json.dumps(structure, ensure_ascii=False, indent=2), encoding="utf-8")

    run_state_path = _run_state_path(output_dir)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["current_reading_activity"] = {
        "phase": "reflecting",
        "started_at": "2026-03-15T07:04:50Z",
        "updated_at": "2026-03-15T07:04:56Z",
        "segment_ref": "1.1",
        "current_excerpt": "Alpha beta gamma…",
        "thought_family": "highlight",
    }
    run_state["current_segment_ref"] = "1.1"
    run_state["updated_at"] = "2026-03-15T07:04:56Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/analysis-state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_reading_activity"]["current_excerpt"] == "Alpha beta gamma delta epsilon."
    assert payload["current_state_panel"]["current_reading_activity"]["current_excerpt"] == "Alpha beta gamma delta epsilon."


def test_chapter_api_tolerates_empty_legacy_target_locator(tmp_path):
    """Legacy featured reactions with empty locator dicts should normalize to null, not 500."""
    book_id = _bootstrap_book(tmp_path)
    public_book_id = to_api_book_id(book_id)
    output_dir = tmp_path / "output" / book_id
    payload = json.loads(_chapter_result_path(output_dir).read_text(encoding="utf-8"))
    payload["featured_reactions"][0]["target_locator"] = {}
    _chapter_result_path(output_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    response = client.get(f"/api/books/{public_book_id}/chapters/1")

    assert response.status_code == 200
    assert response.json()["featured_reactions"][0]["target_locator"] is None


def test_api_upload_and_job_polling(tmp_path, monkeypatch):
    """Upload should return a job envelope and job polling should surface the typed status payload."""
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    monkeypatch.setattr(api_module, "create_upload_job", lambda root: ("job999", root / "state" / "uploads" / "job999.epub"))
    monkeypatch.setattr(api_module, "provision_uploaded_book", lambda upload_path, language="auto", root=None: "demo-book")
    seen: dict[str, object] = {}

    def _launch_sequential(upload_path, root=None, book_id=None, memory_retrieval_mode=None):
        seen["memory_retrieval_mode"] = memory_retrieval_mode
        return {
            "job_id": "job999",
            "status": "queued",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "memory_retrieval_mode": memory_retrieval_mode,
            "pid": 123,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        }

    monkeypatch.setattr(api_module, "launch_sequential_job", _launch_sequential)
    monkeypatch.setattr(
        api_module,
        "_ensure_job_exists",
        lambda job_id: None,
    )
    monkeypatch.setattr(
        api_module,
        "build_job_status_response",
        lambda job_id, root: api_module.JobStatusResponse(
            job_id=job_id,
            status="deep_reading",
            book_id=to_api_book_id("demo-book"),
            book_title="Demo Book",
            progress_percent=50.0,
            completed_chapters=1,
            total_chapters=2,
            current_chapter_id=2,
            current_chapter_ref="Chapter 2",
            current_section_ref="2.3",
            eta_seconds=120,
            last_error=None,
            created_at="2026-03-07T00:00:00Z",
            updated_at="2026-03-07T00:00:01Z",
            ws_url=f"/api/ws/jobs/{job_id}",
        ),
    )

    upload_response = client.post(
        "/api/uploads/epub",
        files={"file": ("demo.epub", b"epub-bytes", "application/epub+zip")},
    )
    assert upload_response.status_code == 202
    assert upload_response.json()["job_id"] == "job999"
    assert upload_response.json()["book_id"] == to_api_book_id("demo-book")
    assert upload_response.json()["ws_url"] == "/api/ws/jobs/job999"
    assert seen["memory_retrieval_mode"] == "hybrid"

    job_response = client.get("/api/jobs/job999")
    assert job_response.status_code == 200
    assert job_response.json()["book_id"] == to_api_book_id("demo-book")
    assert job_response.json()["status"] == "deep_reading"


def test_api_upload_does_not_launch_when_provisioning_cannot_resolve_a_book(
    tmp_path,
    monkeypatch,
):
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    launched = False

    monkeypatch.setattr(
        api_module,
        "create_upload_job",
        lambda root: ("job-unprovisioned", root / "state" / "uploads" / "job.epub"),
    )
    monkeypatch.setattr(
        api_module,
        "provision_uploaded_book",
        lambda *_args, **_kwargs: None,
    )

    def _launch(*_args, **_kwargs):
        nonlocal launched
        launched = True
        raise AssertionError("an unprovisioned upload must not launch a worker")

    monkeypatch.setattr(api_module, "launch_sequential_job", _launch)

    response = client.post(
        "/api/uploads/epub",
        files={"file": ("broken.epub", b"epub-bytes", "application/epub+zip")},
    )

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert launched is False


def test_api_upload_propagates_internal_mechanism_fallback_override(tmp_path, monkeypatch):
    """Immediate upload should pass an explicit iterator_v1 fallback through the internal launch path."""

    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)
    seen: dict[str, object] = {}

    monkeypatch.setattr(api_module, "create_upload_job", lambda root: ("jobattn", root / "state" / "uploads" / "jobattn.epub"))
    monkeypatch.setattr(api_module, "get_backend_reading_mechanism_key", lambda: "iterator_v1")

    def _provision(upload_path, language="auto", root=None, mechanism_key=None):
        seen["provision_mechanism_key"] = mechanism_key
        return "demo-book"

    def _launch(upload_path, root=None, book_id=None, mechanism_key=None, memory_retrieval_mode=None):
        seen["launch_mechanism_key"] = mechanism_key
        seen["memory_retrieval_mode"] = memory_retrieval_mode
        return {
            "job_id": "jobattn",
            "status": "queued",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "mechanism_key": mechanism_key,
            "memory_retrieval_mode": memory_retrieval_mode,
            "pid": 123,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        }

    monkeypatch.setattr(api_module, "provision_uploaded_book", _provision)
    monkeypatch.setattr(api_module, "launch_sequential_job", _launch)

    response = client.post(
        "/api/uploads/epub",
        files={"file": ("demo.epub", b"epub-bytes", "application/epub+zip")},
    )

    assert response.status_code == 202
    assert seen["provision_mechanism_key"] == "iterator_v1"
    assert seen["launch_mechanism_key"] == "iterator_v1"
    assert seen["memory_retrieval_mode"] == "hybrid"


def test_api_upload_deferred_returns_ready_job(tmp_path, monkeypatch):
    """Deferred uploads should launch parse-only work and return the ready job envelope."""
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    monkeypatch.setattr(api_module, "create_upload_job", lambda root: ("jobparse", root / "state" / "uploads" / "jobparse.epub"))
    monkeypatch.setattr(api_module, "provision_uploaded_book", lambda upload_path, language="auto", root=None: "demo-book")
    seen: dict[str, object] = {}

    def _launch_parse(upload_path, root=None, book_id=None, memory_retrieval_mode=None):
        seen["memory_retrieval_mode"] = memory_retrieval_mode
        return {
            "job_id": "jobparse",
            "status": "ready",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "memory_retrieval_mode": memory_retrieval_mode,
            "pid": None,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        }

    monkeypatch.setattr(api_module, "launch_parse_job", _launch_parse)

    upload_response = client.post(
        "/api/uploads/epub",
        data={"start_mode": "deferred"},
        files={"file": ("demo.epub", b"epub-bytes", "application/epub+zip")},
    )
    assert upload_response.status_code == 202
    assert upload_response.json()["status"] == "ready"
    assert upload_response.json()["book_id"] == to_api_book_id("demo-book")
    assert seen["memory_retrieval_mode"] == "hybrid"


def test_api_start_analysis_for_uploaded_book(tmp_path, monkeypatch):
    """Starting deep reading for a not-started book should return a new accepted job."""
    book_id = _bootstrap_book(tmp_path, stage="ready")
    public_book_id = to_api_book_id(book_id)
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    seen: dict[str, object] = {}

    def _launch_existing(internal_book_id, root=None, memory_retrieval_mode=None):
        seen["memory_retrieval_mode"] = memory_retrieval_mode
        return {
            "job_id": "jobstart",
            "status": "queued",
            "upload_path": str((tmp_path / "output" / internal_book_id / "_assets" / "source.epub")),
            "book_id": internal_book_id,
            "memory_retrieval_mode": memory_retrieval_mode,
            "pid": 456,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        }

    monkeypatch.setattr(api_module, "launch_existing_book_read_job", _launch_existing)

    response = client.post(f"/api/books/{public_book_id}/analysis/start")
    assert response.status_code == 202
    assert response.json()["job_id"] == "jobstart"
    assert response.json()["book_id"] == public_book_id
    assert seen["memory_retrieval_mode"] == "hybrid"


def test_api_start_analysis_allows_internal_iterator_v1_fallback(tmp_path, monkeypatch):
    """The start-analysis route should still allow an explicit iterator_v1 fallback launch."""

    book_id = _bootstrap_book(tmp_path, stage="ready")
    public_book_id = to_api_book_id(book_id)
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    monkeypatch.setattr(api_module, "get_backend_reading_mechanism_key", lambda: "iterator_v1")
    monkeypatch.setattr(
        api_module,
        "launch_existing_book_read_job",
        lambda internal_book_id, root=None, mechanism_key=None, memory_retrieval_mode=None: {
            "job_id": "job-v1-start",
            "status": "queued",
            "upload_path": str((tmp_path / "output" / internal_book_id / "_assets" / "source.epub")),
            "book_id": internal_book_id,
            "pid": 789,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
            "mechanism_key": mechanism_key,
            "memory_retrieval_mode": memory_retrieval_mode,
        },
    )

    response = client.post(f"/api/books/{public_book_id}/analysis/start")

    assert response.status_code == 202
    assert response.json()["job_id"] == "job-v1-start"
    assert response.json()["book_id"] == public_book_id


def test_api_errors_use_stable_error_envelope(tmp_path):
    """Validation and missing-resource failures should use the shared ErrorResponse schema."""
    api_module.app.state.root = tmp_path
    client = TestClient(api_module.app)

    upload_response = client.post(
        "/api/uploads/epub",
        files={"file": ("demo.txt", b"bad", "text/plain")},
    )
    assert upload_response.status_code == 400
    assert upload_response.json()["code"] == "UNSUPPORTED_FILE_TYPE"

    missing_book = client.get("/api/books/999999999")
    assert missing_book.status_code == 404
    assert missing_book.json()["code"] == "BOOK_NOT_FOUND"


def test_websocket_streams_snapshot_activity_and_heartbeat(tmp_path):
    """The job websocket should emit the snapshot, activity-created, and heartbeat events."""
    book_id = _bootstrap_book(tmp_path, stage="deep_reading")
    run_state_path = _run_state_path(tmp_path / "output" / book_id)
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    run_state["updated_at"] = "3026-03-07T00:00:00Z"
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2), encoding="utf-8")
    upload_path = upload_file("job123", tmp_path)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"epub")
    _write_json(
        tmp_path / "state" / "jobs" / "job123.json",
        {
            "job_id": "job123",
            "status": "deep_reading",
            "upload_path": str(upload_path),
            "book_id": book_id,
            "pid": None,
            "created_at": "2026-03-07T00:00:00Z",
            "updated_at": "2026-03-07T00:00:00Z",
            "error": None,
        },
    )

    api_module.app.state.root = tmp_path
    api_module.app.state.ws_poll_interval = 0.01
    api_module.app.state.ws_heartbeat_interval = 0.01
    client = TestClient(api_module.app)

    with client.websocket_connect("/api/ws/jobs/job123") as websocket:
        first = websocket.receive_json()
        second = websocket.receive_json()
        third = websocket.receive_json()

    assert first["event_type"] == "job.snapshot"
    assert first["payload"]["status"] == "deep_reading"
    assert first["payload"]["stage_label_key"] == "system.stage.deepReadingChapter"
    assert second["event_type"] in {"structure.ready", "activity.created"}
    assert third["event_type"] in {"activity.created", "heartbeat", "chapter.completed", "stage.changed"}
