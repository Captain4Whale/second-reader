"""Render the active user-level selective dataset into human-readable Markdown."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
from typing import Any

from eval.attentional_v2.user_level_selective_v1 import DATASET_DIR


DEFAULT_OUTPUT_DIRNAME = "audit_human_readable"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
    return rows


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _relative_link(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file.resolve(), start=from_file.parent.resolve())).as_posix()


def _termination_reason_label(value: str) -> str:
    mapping = {
        "chapter_end_after_target_notes": "达到目标笔记数后停在章末",
        "section_end_after_hard_cap": "达到 hard cap 后退到最近节末",
        "paragraph_end_after_hard_cap": "达到 hard cap 后退到最近段末",
    }
    return mapping.get(value, value or "unknown")


def _chapter_summary(segment: dict[str, Any]) -> str:
    chapter_ids = [str(item) for item in segment.get("chapter_ids") or []]
    chapter_titles = [str(item) for item in segment.get("chapter_titles") or []]
    pairs = [
        f"{chapter_id} — {chapter_title}"
        for chapter_id, chapter_title in zip(chapter_ids, chapter_titles, strict=False)
    ]
    return "; ".join(pairs)


def _first_slice_sort_key(note_case: dict[str, Any]) -> tuple[int, int, str]:
    slices = note_case.get("source_span_slices") or []
    if isinstance(slices, list):
        for item in slices:
            if not isinstance(item, dict):
                continue
            paragraph_index = int(item.get("paragraph_index", 10**9) or 10**9)
            char_start = int(item.get("char_start", 10**9) or 10**9)
            return paragraph_index, char_start, str(note_case.get("note_case_id") or "")
    return 10**9, 10**9, str(note_case.get("note_case_id") or "")


def _source_span_key(note_case: dict[str, Any]) -> tuple[tuple[int, int, int], ...]:
    slices = note_case.get("source_span_slices") or []
    key: list[tuple[int, int, int]] = []
    if isinstance(slices, list):
        for item in slices:
            if not isinstance(item, dict):
                continue
            key.append(
                (
                    int(item.get("paragraph_index", -1) or -1),
                    int(item.get("char_start", -1) or -1),
                    int(item.get("char_end", -1) or -1),
                )
            )
    if not key:
        return ((-1, -1, -1),)
    return tuple(key)


def _render_text_block(value: str) -> str:
    text = _clean_text(value)
    if not text:
        text = "(empty)"
    return f"```text\n{text}\n```"


def _render_slice_lines(note_case: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    slices = note_case.get("source_span_slices") or []
    for index, item in enumerate(slices, start=1):
        if not isinstance(item, dict):
            continue
        lines.append(
            "- "
            + f"slice {index}: paragraph `{item.get('paragraph_index')}`, "
            + f"char `{item.get('char_start')}`-`{item.get('char_end')}`"
        )
        if _clean_text(item.get("text")):
            lines.append("  - slice_text:")
            lines.append(_render_text_block(str(item.get("text"))))
    if not lines:
        lines.append("- (no source_span_slices)")
    return lines


def _window_doc_name(segment_id: str) -> str:
    return f"{segment_id}.md"


def _render_index(
    *,
    dataset_dir: Path,
    output_dir: Path,
    manifest: dict[str, Any],
    segments: list[dict[str, Any]],
    note_cases_by_segment: dict[str, list[dict[str, Any]]],
) -> str:
    index_path = output_dir / "index.md"
    lines = [
        "# User-Level Selective 数据集审计索引",
        "",
        f"- generated_at: `{_timestamp()}`",
        f"- dataset_dir: `{dataset_dir}`",
        f"- dataset_id: `{manifest.get('dataset_id', '')}`",
        f"- version: `{manifest.get('version', '')}`",
        f"- segment_count: `{len(segments)}`",
        f"- note_case_count: `{sum(len(items) for items in note_cases_by_segment.values())}`",
        "",
        "## 原始数据文件",
        "",
        f"- `manifest.json`: [`../manifest.json`]({_relative_link(index_path, dataset_dir / 'manifest.json')})",
        f"- `segments.jsonl`: [`../segments.jsonl`]({_relative_link(index_path, dataset_dir / 'segments.jsonl')})",
        f"- `note_cases.jsonl`: [`../note_cases.jsonl`]({_relative_link(index_path, dataset_dir / 'note_cases.jsonl')})",
        "",
        "## 阅读窗口",
        "",
    ]
    for index, segment in enumerate(segments, start=1):
        segment_id = str(segment.get("segment_id") or "")
        source_path = dataset_dir / str(segment.get("segment_source_path") or "")
        window_doc = output_dir / "windows" / _window_doc_name(segment_id)
        lines.extend(
            [
                f"### {index}. {_clean_text(segment.get('book_title'))}",
                "",
                f"- segment_id: `{segment_id}`",
                f"- source_id: `{segment.get('source_id')}`",
                f"- author: `{segment.get('author')}`",
                f"- language_track: `{segment.get('language_track')}`",
                f"- 阅读窗口从: `{segment.get('start_sentence_id')}`",
                f"- 阅读窗口到: `{segment.get('end_sentence_id')}`",
                f"- 覆盖章节: {_chapter_summary(segment)}",
                f"- termination_reason: `{segment.get('termination_reason')}` ({_termination_reason_label(str(segment.get('termination_reason') or ''))})",
                f"- covered_note_count: `{len(note_cases_by_segment.get(segment_id, []))}`",
                f"- 窗口审计文档: [{window_doc.name}]({_relative_link(index_path, window_doc)})",
                f"- 原始窗口文本: [{source_path.name}]({_relative_link(index_path, source_path)})",
                "",
            ]
        )
    return "\n".join(lines)


def _render_window_doc(
    *,
    dataset_dir: Path,
    output_dir: Path,
    segment: dict[str, Any],
    note_cases: list[dict[str, Any]],
) -> str:
    segment_id = str(segment.get("segment_id") or "")
    window_path = output_dir / "windows" / _window_doc_name(segment_id)
    source_path = dataset_dir / str(segment.get("segment_source_path") or "")

    sorted_cases = sorted(note_cases, key=_first_slice_sort_key)
    duplicate_counts = Counter(_source_span_key(item) for item in sorted_cases)
    duplicate_group_ids: dict[tuple[tuple[int, int, int], ...], int] = {}
    next_group_id = 1
    for item in sorted_cases:
        key = _source_span_key(item)
        if duplicate_counts[key] > 1 and key not in duplicate_group_ids:
            duplicate_group_ids[key] = next_group_id
            next_group_id += 1

    lines = [
        f"# {_clean_text(segment.get('book_title'))} — 阅读窗口审计",
        "",
        f"- segment_id: `{segment_id}`",
        f"- source_id: `{segment.get('source_id')}`",
        f"- author: `{segment.get('author')}`",
        f"- language_track: `{segment.get('language_track')}`",
        f"- 阅读窗口从: `{segment.get('start_sentence_id')}`",
        f"- 阅读窗口到: `{segment.get('end_sentence_id')}`",
        f"- 覆盖章节: {_chapter_summary(segment)}",
        f"- termination_reason: `{segment.get('termination_reason')}` ({_termination_reason_label(str(segment.get('termination_reason') or ''))})",
        f"- case_count: `{len(sorted_cases)}`",
        f"- 原始窗口文本: [{source_path.name}]({_relative_link(window_path, source_path)})",
        "",
        "## 全部 Case",
        "",
    ]

    for index, note_case in enumerate(sorted_cases, start=1):
        key = _source_span_key(note_case)
        duplicate_count = duplicate_counts[key]
        duplicate_group_id = duplicate_group_ids.get(key)
        lines.extend(
            [
                f"### {index}. `{note_case.get('note_case_id')}`",
                "",
                f"- note_id: `{note_case.get('note_id')}`",
                f"- chapter: `{note_case.get('chapter_id')}` / `{note_case.get('chapter_title')}`",
                f"- raw_locator: `{note_case.get('raw_locator')}`",
                f"- section_label: `{note_case.get('section_label')}`",
            ]
        )
        if duplicate_group_id is not None:
            lines.append(
                f"- duplicate_source_span_group: `group_{duplicate_group_id:02d}` (`{duplicate_count}` cases share this span)"
            )
        lines.extend(
            [
                "",
                "#### note_text",
                "",
                _render_text_block(str(note_case.get("note_text") or "")),
            ]
        )
        if _clean_text(note_case.get("note_comment")):
            lines.extend(
                [
                    "",
                    "#### note_comment",
                    "",
                    _render_text_block(str(note_case.get("note_comment") or "")),
                ]
            )
        lines.extend(
            [
                "",
                "#### canonical_case_text (`source_span_text`)",
                "",
                _render_text_block(str(note_case.get("source_span_text") or "")),
                "",
                "#### source_span_slices",
                "",
                *_render_slice_lines(note_case),
                "",
            ]
        )
    return "\n".join(lines)


def render_user_level_selective_audit(
    *,
    dataset_dir: Path = DATASET_DIR,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    dataset_root = Path(dataset_dir).resolve()
    manifest = _load_json(dataset_root / "manifest.json")
    segments = _load_jsonl(dataset_root / "segments.jsonl")
    note_cases = _load_jsonl(dataset_root / "note_cases.jsonl")
    final_output_dir = Path(output_dir).resolve() if output_dir is not None else dataset_root / DEFAULT_OUTPUT_DIRNAME

    if final_output_dir.exists():
        shutil.rmtree(final_output_dir)
    (final_output_dir / "windows").mkdir(parents=True, exist_ok=True)

    note_cases_by_segment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note_case in note_cases:
        note_cases_by_segment[str(note_case.get("segment_id") or "")].append(note_case)

    index_content = _render_index(
        dataset_dir=dataset_root,
        output_dir=final_output_dir,
        manifest=manifest,
        segments=segments,
        note_cases_by_segment=note_cases_by_segment,
    )
    _write_text(final_output_dir / "index.md", index_content)

    window_count = 0
    case_count = 0
    for segment in segments:
        segment_id = str(segment.get("segment_id") or "")
        cases = note_cases_by_segment.get(segment_id, [])
        _write_text(
            final_output_dir / "windows" / _window_doc_name(segment_id),
            _render_window_doc(
                dataset_dir=dataset_root,
                output_dir=final_output_dir,
                segment=segment,
                note_cases=cases,
            ),
        )
        window_count += 1
        case_count += len(cases)

    summary = {
        "generated_at": _timestamp(),
        "dataset_dir": str(dataset_root),
        "output_dir": str(final_output_dir),
        "segment_count": window_count,
        "note_case_count": case_count,
        "index_path": str(final_output_dir / "index.md"),
        "window_paths": [
            str(final_output_dir / "windows" / _window_doc_name(str(segment.get("segment_id") or "")))
            for segment in segments
        ],
    }
    _write_text(final_output_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=DATASET_DIR)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = render_user_level_selective_audit(
        dataset_dir=Path(args.dataset_dir),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
