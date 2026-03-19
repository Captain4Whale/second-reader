"""Dataset loader for the subsegment benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BenchmarkCase:
    """One tracked benchmark case for subsegment evaluation."""

    case_id: str
    split: str
    source: dict[str, Any]
    book_title: str
    author: str
    output_language: str
    chapter_title: str
    chapter_ref: str
    chapter_index: int
    total_chapters: int
    primary_role: str
    role_tags: list[str]
    role_confidence: str
    section_heading: str
    nearby_outline: list[str]
    segment_id: str
    segment_ref: str
    segment_summary: str
    segment_text: str
    tags: list[str]
    notes: str


@dataclass(frozen=True)
class BenchmarkDataset:
    """Loaded benchmark dataset and manifest metadata."""

    dataset_id: str
    version: str
    description: str
    default_user_intent: str
    case_file: str
    core_case_ids: list[str]
    audit_case_ids: list[str]
    cases: list[BenchmarkCase]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_cases(path: Path) -> list[dict[str, Any]]:
    """Load cases from either one JSON array file or JSONL."""
    if path.suffix == ".jsonl":
        items: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError("benchmark case JSONL lines must be objects")
            items.append(payload)
        return items
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError("benchmark case file must contain a JSON array")
    return payload


def _coerce_case(raw: dict[str, Any]) -> BenchmarkCase:
    if not isinstance(raw, dict):
        raise ValueError("benchmark case must be an object")
    case_id = str(raw.get("case_id", "")).strip()
    if not case_id:
        raise ValueError("benchmark case is missing case_id")
    split = str(raw.get("split", "")).strip()
    if split not in {"core", "audit"}:
        raise ValueError(f"{case_id}: split must be 'core' or 'audit'")
    segment_text = str(raw.get("segment_text", "")).strip()
    if not segment_text:
        raise ValueError(f"{case_id}: segment_text must be non-empty")
    source = raw.get("source")
    if not isinstance(source, dict) or not source:
        raise ValueError(f"{case_id}: source provenance is required")
    return BenchmarkCase(
        case_id=case_id,
        split=split,
        source=dict(source),
        book_title=str(raw.get("book_title", "")).strip(),
        author=str(raw.get("author", "")).strip(),
        output_language=str(raw.get("output_language", "en")).strip() or "en",
        chapter_title=str(raw.get("chapter_title", "")).strip(),
        chapter_ref=str(raw.get("chapter_ref", "")).strip(),
        chapter_index=int(raw.get("chapter_index", 0)),
        total_chapters=int(raw.get("total_chapters", 0)),
        primary_role=str(raw.get("primary_role", "body")).strip() or "body",
        role_tags=[str(item).strip() for item in raw.get("role_tags", []) if str(item).strip()],
        role_confidence=str(raw.get("role_confidence", "medium")).strip() or "medium",
        section_heading=str(raw.get("section_heading", "")).strip(),
        nearby_outline=[str(item).strip() for item in raw.get("nearby_outline", []) if str(item).strip()],
        segment_id=str(raw.get("segment_id", "")).strip(),
        segment_ref=str(raw.get("segment_ref", "")).strip() or str(raw.get("segment_id", "")).strip(),
        segment_summary=str(raw.get("segment_summary", "")).strip(),
        segment_text=segment_text,
        tags=[str(item).strip() for item in raw.get("tags", []) if str(item).strip()],
        notes=str(raw.get("notes", "")).strip(),
    )


def load_benchmark_dataset(dataset_dir: str | Path) -> BenchmarkDataset:
    """Load and validate one tracked benchmark dataset."""
    root = Path(dataset_dir)
    manifest_path = root / "manifest.json"
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("benchmark manifest must be an object")

    case_file = str(manifest.get("case_file", "")).strip()
    if not case_file:
        raise ValueError("benchmark manifest is missing case_file")
    cases_raw = _load_cases(root / case_file)

    cases = [_coerce_case(item) for item in cases_raw]
    by_id = {case.case_id: case for case in cases}
    if len(by_id) != len(cases):
        raise ValueError("benchmark case ids must be unique")

    core_case_ids = [str(item).strip() for item in manifest.get("core_case_ids", []) if str(item).strip()]
    audit_case_ids = [str(item).strip() for item in manifest.get("audit_case_ids", []) if str(item).strip()]
    if not core_case_ids or not audit_case_ids:
        raise ValueError("benchmark manifest must define core_case_ids and audit_case_ids")

    unknown = [case_id for case_id in core_case_ids + audit_case_ids if case_id not in by_id]
    if unknown:
        raise ValueError(f"benchmark manifest references unknown case ids: {', '.join(sorted(unknown))}")

    if {case.case_id for case in cases if case.split == "core"} != set(core_case_ids):
        raise ValueError("core_case_ids do not match cases marked split=core")
    if {case.case_id for case in cases if case.split == "audit"} != set(audit_case_ids):
        raise ValueError("audit_case_ids do not match cases marked split=audit")

    return BenchmarkDataset(
        dataset_id=str(manifest.get("dataset_id", "")).strip(),
        version=str(manifest.get("version", "")).strip() or "0",
        description=str(manifest.get("description", "")).strip(),
        default_user_intent=str(manifest.get("default_user_intent", "")).strip(),
        case_file=case_file,
        core_case_ids=core_case_ids,
        audit_case_ids=audit_case_ids,
        cases=cases,
    )
