"""Backend fixture helpers used only by contract E2E runs."""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
from pathlib import Path

from src.iterator_reader.storage import activity_file, run_state_file, save_json, source_asset_file
from src.library.jobs import save_job
from src.library.storage import timestamp, upload_file


FIXTURE_JOB_ID = "fixture-e2e-job"
FIXTURE_BOOK_ID = "fixture-e2e-book"


def fixture_upload_path(root: Path) -> Path:
    """Return the deterministic upload path used by the E2E fixture profile."""
    return upload_file(FIXTURE_JOB_ID, root)


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _fixture_payload() -> dict:
    fixture_path = _backend_root() / "tests" / "fixtures" / "e2e_runtime" / "fixture.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False))
        handle.write("\n")


def launch_e2e_fixture_job(upload_path: Path, *, upload_filename: str, root: Path) -> dict:
    """Seed a deterministic runtime tree and advance it asynchronously."""
    payload = _fixture_payload()
    book_id = str(payload.get("book_id", FIXTURE_BOOK_ID))
    book_dir = root / "output" / book_id
    shutil.rmtree(book_dir, ignore_errors=True)
    book_dir.mkdir(parents=True, exist_ok=True)

    now = timestamp()
    chapter = dict(payload.get("chapter", {}))
    chapter_id = int(chapter.get("id", 1))
    chapter_ref = str(chapter.get("reference", f"Chapter {chapter_id}"))
    chapter_title = str(chapter.get("title", chapter_ref))
    result_file = str(chapter.get("result_file", "ch01_deep_read.json"))

    source_asset_path = source_asset_file(book_dir)
    source_asset_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(upload_path, source_asset_path)

    manifest = {
        "book_id": book_id,
        "book": str(payload.get("book", "Fixture E2E Book")),
        "author": str(payload.get("author", "Fixture Author")),
        "cover_image_url": None,
        "book_language": str(payload.get("book_language", "en")),
        "output_language": str(payload.get("output_language", "en")),
        "source_file": str(upload_path.resolve()),
        "source_asset": {"format": "epub", "file": "_assets/source.epub"},
        "updated_at": now,
        "chapters": [
            {
                "id": chapter_id,
                "title": chapter_title,
                "chapter_number": int(chapter.get("chapter_number", chapter_id)),
                "reference": chapter_ref,
                "status": "pending",
                "segment_count": int(chapter.get("segment_count", 1)),
                "markdown_file": str(chapter.get("markdown_file", "ch01_deep_read.md")),
                "result_file": result_file,
                "visible_reaction_count": 0,
                "reaction_type_diversity": 0,
                "high_signal_reaction_count": 0,
            }
        ],
    }
    save_json(book_dir / "book_manifest.json", manifest)
    save_json(
        run_state_file(book_dir),
        {
            "mode": "sequential",
            "stage": "deep_reading",
            "book": manifest["book"],
            "current_chapter_id": chapter_id,
            "current_chapter_ref": chapter_ref,
            "current_segment_ref": "1.1",
            "completed_chapters": 0,
            "total_chapters": 1,
            "eta_seconds": 3,
            "updated_at": now,
            "error": None,
        },
    )
    activity_file(book_dir).parent.mkdir(parents=True, exist_ok=True)
    activity_file(book_dir).write_text("", encoding="utf-8")

    record = {
        "job_id": FIXTURE_JOB_ID,
        "status": "deep_reading",
        "upload_path": str(upload_path),
        "book_id": book_id,
        "pid": os.getpid(),
        "created_at": now,
        "updated_at": now,
        "error": None,
        "upload_filename": upload_filename,
    }
    save_job(record, root)

    def complete() -> None:
        time.sleep(1.0)
        completion_time = timestamp()
        chapter_result = dict(payload.get("chapter_result", {}))
        chapter_result["book_title"] = manifest["book"]
        chapter_result.setdefault(
            "chapter",
            {
                "id": chapter_id,
                "title": chapter_title,
                "chapter_number": int(chapter.get("chapter_number", chapter_id)),
                "reference": chapter_ref,
                "status": "done",
            },
        )
        chapter_result["output_language"] = manifest["output_language"]
        chapter_result["generated_at"] = completion_time
        save_json(book_dir / result_file, chapter_result)

        manifest["updated_at"] = completion_time
        manifest["chapters"][0].update(
            {
                "status": "done",
                "visible_reaction_count": int(chapter_result.get("visible_reaction_count", 1)),
                "reaction_type_diversity": int(chapter_result.get("reaction_type_diversity", 1)),
                "high_signal_reaction_count": int(chapter_result.get("high_signal_reaction_count", 1)),
            }
        )
        save_json(book_dir / "book_manifest.json", manifest)
        save_json(
            run_state_file(book_dir),
            {
                "mode": "sequential",
                "stage": "completed",
                "book": manifest["book"],
                "current_chapter_id": None,
                "current_chapter_ref": None,
                "current_segment_ref": None,
                "completed_chapters": 1,
                "total_chapters": 1,
                "eta_seconds": 0,
                "updated_at": completion_time,
                "error": None,
            },
        )

        event = dict(payload.get("activity_event", {}))
        event["timestamp"] = completion_time
        _append_jsonl(activity_file(book_dir), event)
        save_job({**record, "status": "completed", "updated_at": completion_time}, root)

    threading.Thread(target=complete, daemon=True).start()
    return record
