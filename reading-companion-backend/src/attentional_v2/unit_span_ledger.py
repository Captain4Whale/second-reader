"""Unit Span Ledger persistence for attentional_v2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from .source_spans import source_span_id
from .storage import append_jsonl, unit_span_ledger_file


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _existing_record_count(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                count += 1
    return count


def next_unit_sequence_index(output_dir: Path) -> int:
    """Return the next accepted-unit sequence number for one run."""

    return _existing_record_count(unit_span_ledger_file(output_dir)) + 1


def latest_unit_span(output_dir: Path) -> dict[str, object] | None:
    """Return the last accepted unit-span ledger row, if present."""

    path = unit_span_ledger_file(output_dir)
    if not path.exists():
        return None
    latest: dict[str, object] | None = None
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                latest = payload
    return latest


def append_unit_span_record(
    output_dir: Path,
    *,
    chapter_id: int,
    chapter_ref: str,
    source_unit: Mapping[str, object],
    preview: Mapping[str, object],
    end_anchor_text: str,
    resolution: Mapping[str, object],
) -> dict[str, object]:
    """Append one accepted mainline unit span and return the persisted row."""

    sequence_index = next_unit_sequence_index(output_dir)
    source_span = source_unit.get("source_span")
    span = dict(source_span) if isinstance(source_span, Mapping) else {}
    unit_id = f"u{sequence_index:06d}"
    record = {
        "unit_id": unit_id,
        "sequence_index": sequence_index,
        "chapter_id": int(chapter_id),
        "chapter_ref": _clean_text(chapter_ref),
        "source_span_id": source_span_id(span),
        "start_cursor": dict(span.get("start_cursor", {})) if isinstance(span.get("start_cursor"), Mapping) else {},
        "end_cursor": dict(span.get("end_cursor", {})) if isinstance(span.get("end_cursor"), Mapping) else {},
        "preview_start_cursor": dict(preview.get("preview_start_cursor", {}))
        if isinstance(preview.get("preview_start_cursor"), Mapping)
        else {},
        "preview_end_cursor": dict(preview.get("preview_end_cursor", {}))
        if isinstance(preview.get("preview_end_cursor"), Mapping)
        else {},
        "char_count": int(source_unit.get("char_count", 0) or 0),
        "paragraph_count": int(source_unit.get("paragraph_count", 0) or 0),
        "end_anchor_text": _clean_text(end_anchor_text),
        "resolution": dict(resolution),
        "created_at": _timestamp(),
    }
    append_jsonl(unit_span_ledger_file(output_dir), record)
    return record

