#!/usr/bin/env python3
"""Diagnose attentional_v2 Unit Memory retrieval health from run artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.attentional_v2.storage import (  # noqa: E402
    memory_retrieval_config_file,
    unit_memory_retrieval_trace_file,
    unit_memory_sqlite_file,
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _count_selected_units(rows: list[dict[str, Any]]) -> tuple[int, set[str]]:
    count = 0
    unit_ids: set[str] = set()
    for row in rows:
        selected = row.get("selected_units")
        if not isinstance(selected, list):
            continue
        for item in selected:
            if not isinstance(item, dict):
                continue
            unit_id = str(item.get("unit_id") or "").strip()
            if unit_id:
                unit_ids.add(unit_id)
            count += 1
    return count, unit_ids


def _understanding_content_from_entry(entry_json: object) -> str:
    if isinstance(entry_json, str):
        try:
            entry_json = json.loads(entry_json)
        except json.JSONDecodeError:
            return ""
    if not isinstance(entry_json, dict):
        return ""
    digest = entry_json.get("digest")
    if not isinstance(digest, dict):
        return ""
    understanding = digest.get("understanding")
    if isinstance(understanding, dict):
        return str(understanding.get("content") or "").strip()
    if isinstance(understanding, str):
        return understanding.strip()
    return ""


def _sqlite_inventory(runtime_dir: Path, selected_unit_ids: set[str]) -> dict[str, Any]:
    db_path = runtime_dir / "unit_memory.sqlite"
    if not db_path.exists():
        return {
            "exists": False,
            "entries": 0,
            "retrieval_docs": 0,
            "docs_by_surface": {},
            "vector_status_by_surface": {},
            "query_embedding_cache_rows": 0,
            "sqlite_vec_table_present": False,
            "vector_rows": 0,
            "selected_renderable_unit_count": 0,
            "selected_non_renderable_unit_count": 0,
        }
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        entries = int(connection.execute("SELECT COUNT(*) FROM unit_memory_entries").fetchone()[0])
        retrieval_docs = int(connection.execute("SELECT COUNT(*) FROM retrieval_docs").fetchone()[0])
        docs_by_surface = {
            str(row["surface"]): int(row["count"])
            for row in connection.execute(
                "SELECT surface, COUNT(*) AS count FROM retrieval_docs GROUP BY surface"
            ).fetchall()
        }
        vector_status_by_surface = {
            f"{row['surface']}:{row['vector_index_status']}": int(row["count"])
            for row in connection.execute(
                """
                SELECT surface, vector_index_status, COUNT(*) AS count
                FROM retrieval_docs
                GROUP BY surface, vector_index_status
                """
            ).fetchall()
        }
        try:
            query_cache_rows = int(connection.execute("SELECT COUNT(*) FROM query_embedding_cache").fetchone()[0])
        except sqlite3.Error:
            query_cache_rows = 0
        sqlite_vec_table_present = (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table') AND name = 'retrieval_doc_vectors'"
            ).fetchone()
            is not None
        )
        if sqlite_vec_table_present:
            try:
                vector_rows = int(connection.execute("SELECT COUNT(*) FROM retrieval_doc_vectors").fetchone()[0])
            except sqlite3.Error:
                vector_rows = 0
        else:
            vector_rows = 0
        selected_renderable = 0
        selected_non_renderable = 0
        if selected_unit_ids:
            placeholders = ",".join("?" for _ in selected_unit_ids)
            rows = connection.execute(
                f"SELECT unit_id, entry_json FROM unit_memory_entries WHERE unit_id IN ({placeholders})",
                tuple(sorted(selected_unit_ids)),
            ).fetchall()
            by_unit = {str(row["unit_id"]): _understanding_content_from_entry(row["entry_json"]) for row in rows}
            for unit_id in selected_unit_ids:
                if by_unit.get(unit_id):
                    selected_renderable += 1
                else:
                    selected_non_renderable += 1
    return {
        "exists": True,
        "entries": entries,
        "retrieval_docs": retrieval_docs,
        "docs_by_surface": docs_by_surface,
        "vector_status_by_surface": vector_status_by_surface,
        "query_embedding_cache_rows": query_cache_rows,
        "sqlite_vec_table_present": sqlite_vec_table_present,
        "vector_rows": vector_rows,
        "selected_renderable_unit_count": selected_renderable,
        "selected_non_renderable_unit_count": selected_non_renderable,
    }


def _runtime_dir_from_output(output_dir: Path) -> Path:
    runtime_dir = output_dir / "_mechanisms" / "attentional_v2" / "runtime"
    if runtime_dir.exists():
        return runtime_dir
    if output_dir.name == "runtime" and (output_dir / "unit_memory_retrieval_trace.jsonl").exists():
        return output_dir
    return runtime_dir


def _discover_output_dirs(path: Path) -> list[Path]:
    path = path.expanduser().resolve()
    if _runtime_dir_from_output(path).exists():
        return [path]
    if path.name == "runtime" and (path / "unit_memory_retrieval_trace.jsonl").exists():
        return [path]
    outputs_dir = path / "outputs"
    if outputs_dir.exists():
        candidates = [
            candidate
            for candidate in outputs_dir.glob("*/*")
            if _runtime_dir_from_output(candidate).exists()
        ]
        if candidates:
            return sorted(candidates)
    runtime_candidates = sorted(path.glob("**/_mechanisms/attentional_v2/runtime"))
    if runtime_candidates:
        output_dirs: list[Path] = []
        for runtime in runtime_candidates:
            try:
                output_dirs.append(runtime.parents[2])
            except IndexError:
                output_dirs.append(runtime)
        return sorted(set(output_dirs))
    return [path]


def summarize_output(output_dir: Path) -> dict[str, Any]:
    runtime_dir = _runtime_dir_from_output(output_dir)
    if not runtime_dir.exists() and output_dir.name == "runtime":
        runtime_dir = output_dir
    config = _load_json(runtime_dir / "memory_retrieval_config.json")
    trace_rows = _jsonl(runtime_dir / "unit_memory_retrieval_trace.jsonl")
    retrieval_rows = [row for row in trace_rows if row.get("event_type") == "unit_memory_retrieval"]
    selection_rows = [row for row in trace_rows if row.get("event_type") == "unit_memory_reading_memory_selection"]
    selected_total, selected_unit_ids = _count_selected_units(retrieval_rows)
    inventory = _sqlite_inventory(runtime_dir, selected_unit_ids)
    candidate_counts = Counter()
    per_recall_counts = Counter()
    query_source_counts: Counter[str] = Counter()
    mode_counts: Counter[str] = Counter()
    effective_mode_counts: Counter[str] = Counter()
    degradation_counts: Counter[str] = Counter()
    retrieval_suppressed_reasons: Counter[str] = Counter()
    selected_rows = 0
    excluded_source_unit_span_total = 0
    excluded_source_unit_span_rows = 0
    max_excluded_source_unit_span_count = 0
    for row in retrieval_rows:
        query_source_counts[str(row.get("query_source") or "")] += 1
        mode_counts[str(row.get("mode") or "")] += 1
        effective_mode_counts[str(row.get("effective_mode") or "")] += 1
        degradation = str(row.get("degradation_reason") or "").strip()
        degradation_counts[degradation or "none"] += 1
        try:
            excluded_count = int(row.get("excluded_source_unit_span_count") or 0)
        except (TypeError, ValueError):
            excluded_count = 0
        if excluded_count > 0:
            excluded_source_unit_span_rows += 1
            excluded_source_unit_span_total += excluded_count
            max_excluded_source_unit_span_count = max(max_excluded_source_unit_span_count, excluded_count)
        counts = row.get("candidate_counts")
        if isinstance(counts, dict):
            for key in ("recall_count", "prior_units", "lexical_docs", "dense_docs", "candidate_units"):
                try:
                    candidate_counts[key] += int(counts.get(key) or 0)
                except (TypeError, ValueError):
                    pass
        selected = row.get("selected_units")
        if isinstance(selected, list) and selected:
            selected_rows += 1
        suppressed_units = row.get("suppressed_units")
        if isinstance(suppressed_units, list):
            for item in suppressed_units:
                if isinstance(item, dict):
                    retrieval_suppressed_reasons[str(item.get("reason") or "unknown")] += 1
        per_recall = row.get("per_recall")
        if isinstance(per_recall, list):
            for item in per_recall:
                if not isinstance(item, dict):
                    continue
                for key in ("lexical_docs", "dense_docs"):
                    try:
                        per_recall_counts[key] += int(item.get(key) or 0)
                    except (TypeError, ValueError):
                        pass
    selection_line_total = 0
    hot_line_total = 0
    retrieved_line_total = 0
    rendered_retrieved_unit_ids: set[str] = set()
    suppressed_reasons: Counter[str] = Counter()
    for row in selection_rows:
        line_count = int(row.get("line_count") or 0)
        hot_count = int(row.get("hot_line_count") or 0)
        retrieved_count = int(row.get("retrieved_line_count") or 0)
        selection_line_total += line_count
        hot_line_total += hot_count
        retrieved_line_total += retrieved_count
        suppressed = row.get("suppressed")
        if isinstance(suppressed, list):
            for item in suppressed:
                if isinstance(item, dict):
                    suppressed_reasons[str(item.get("reason") or "unknown")] += 1
        rendered_units = row.get("rendered_retrieved_units")
        if isinstance(rendered_units, list):
            for item in rendered_units:
                if not isinstance(item, dict):
                    continue
                unit_id = str(item.get("unit_id") or "").strip()
                if unit_id:
                    rendered_retrieved_unit_ids.add(unit_id)
        rendered_unit_ids = row.get("rendered_retrieved_unit_ids")
        if isinstance(rendered_unit_ids, list):
            for item in rendered_unit_ids:
                unit_id = str(item or "").strip()
                if unit_id:
                    rendered_retrieved_unit_ids.add(unit_id)
    selected_but_not_rendered_count = max(0, selected_total - retrieved_line_total)
    status = "ok"
    warnings: list[str] = []
    if retrieval_rows and retrieved_line_total == 0:
        status = "needs_repair"
        warnings.append("no_prompt_visible_retrieved_memory")
    if str(config.get("mode") or "") == "hybrid" and not inventory["sqlite_vec_table_present"]:
        status = "needs_repair"
        warnings.append("hybrid_without_sqlite_vec_table")
    if str(config.get("mode") or "") == "hybrid" and inventory["query_embedding_cache_rows"] == 0:
        warnings.append("hybrid_without_query_embedding_cache")
    if selected_total and inventory["selected_renderable_unit_count"] == 0:
        status = "needs_repair"
        warnings.append("selected_units_not_renderable")
    return {
        "label": output_dir.parent.name if output_dir.name == "attentional_v2" else output_dir.name,
        "output_dir": str(output_dir),
        "runtime_dir": str(runtime_dir),
        "status": status,
        "warnings": warnings,
        "config": {
            "mode": config.get("mode"),
            "recent_neighbor_exclusion_unit_count": config.get("recent_neighbor_exclusion_unit_count"),
            "min_retrievable_prior_units": config.get("min_retrievable_prior_units"),
        },
        "sqlite": inventory,
        "trace": {
            "retrieval_rows": len(retrieval_rows),
            "selection_rows": len(selection_rows),
            "query_source_counts": _counter_dict(query_source_counts),
            "mode_counts": _counter_dict(mode_counts),
            "effective_mode_counts": _counter_dict(effective_mode_counts),
            "degradation_counts": _counter_dict(degradation_counts),
            "candidate_totals": _counter_dict(candidate_counts),
            "per_recall_candidate_totals": _counter_dict(per_recall_counts),
            "selected_rows": selected_rows,
            "selected_unit_count": selected_total,
            "selected_unique_unit_count": len(selected_unit_ids),
            "selected_unit_ids": sorted(selected_unit_ids)[:50],
            "excluded_source_unit_span_total": excluded_source_unit_span_total,
            "retrieval_rows_with_excluded_source_unit_spans": excluded_source_unit_span_rows,
            "max_excluded_source_unit_span_count": max_excluded_source_unit_span_count,
            "retrieval_suppressed_reasons": _counter_dict(retrieval_suppressed_reasons),
        },
        "reading_memory": {
            "line_total": selection_line_total,
            "hot_line_total": hot_line_total,
            "retrieved_line_total": retrieved_line_total,
            "rendered_retrieved_unique_unit_count": len(rendered_retrieved_unit_ids),
            "rendered_retrieved_unit_ids": sorted(rendered_retrieved_unit_ids)[:50],
            "selected_but_not_rendered_count": selected_but_not_rendered_count,
            "suppressed_reasons": _counter_dict(suppressed_reasons),
        },
    }


def summarize_paths(paths: list[Path]) -> dict[str, Any]:
    outputs: list[dict[str, Any]] = []
    for path in paths:
        for output_dir in _discover_output_dirs(path):
            outputs.append(summarize_output(output_dir))
    total = {
        "output_count": len(outputs),
        "entries": sum(int(item["sqlite"]["entries"]) for item in outputs),
        "retrieval_docs": sum(int(item["sqlite"]["retrieval_docs"]) for item in outputs),
        "retrieval_rows": sum(int(item["trace"]["retrieval_rows"]) for item in outputs),
        "selection_rows": sum(int(item["trace"]["selection_rows"]) for item in outputs),
        "selected_unit_count": sum(int(item["trace"]["selected_unit_count"]) for item in outputs),
        "renderable_selected_unit_count": sum(int(item["sqlite"]["selected_renderable_unit_count"]) for item in outputs),
        "non_renderable_selected_unit_count": sum(int(item["sqlite"]["selected_non_renderable_unit_count"]) for item in outputs),
        "selected_but_not_rendered_count": sum(int(item["reading_memory"]["selected_but_not_rendered_count"]) for item in outputs),
        "excluded_source_unit_span_total": sum(int(item["trace"]["excluded_source_unit_span_total"]) for item in outputs),
        "retrieval_rows_with_excluded_source_unit_spans": sum(
            int(item["trace"]["retrieval_rows_with_excluded_source_unit_spans"]) for item in outputs
        ),
        "max_excluded_source_unit_span_count": max(
            [int(item["trace"]["max_excluded_source_unit_span_count"]) for item in outputs] or [0]
        ),
        "retrieval_suppressed_unit_count": sum(
            sum(int(count) for count in item["trace"].get("retrieval_suppressed_reasons", {}).values())
            for item in outputs
        ),
        "hot_line_total": sum(int(item["reading_memory"]["hot_line_total"]) for item in outputs),
        "retrieved_line_total": sum(int(item["reading_memory"]["retrieved_line_total"]) for item in outputs),
        "rendered_retrieved_unique_unit_count": len(
            {
                unit_id
                for item in outputs
                for unit_id in item["reading_memory"].get("rendered_retrieved_unit_ids", [])
            }
        ),
        "query_embedding_cache_rows": sum(int(item["sqlite"]["query_embedding_cache_rows"]) for item in outputs),
        "vector_rows": sum(int(item["sqlite"]["vector_rows"]) for item in outputs),
    }
    status = "ok"
    warnings = sorted({warning for item in outputs for warning in item.get("warnings", [])})
    if any(item.get("status") != "ok" for item in outputs):
        status = "needs_repair"
    return {"status": status, "warnings": warnings, "total": total, "outputs": outputs}


def render_markdown(summary: dict[str, Any]) -> str:
    total = summary.get("total", {})
    lines = [
        "# Unit Memory Retrieval Health Report",
        "",
        f"Status: `{summary.get('status')}`",
        "",
        "## Totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in (
        "output_count",
        "entries",
        "retrieval_docs",
        "retrieval_rows",
        "selection_rows",
        "selected_unit_count",
        "renderable_selected_unit_count",
        "non_renderable_selected_unit_count",
        "selected_but_not_rendered_count",
        "excluded_source_unit_span_total",
        "retrieval_rows_with_excluded_source_unit_spans",
        "max_excluded_source_unit_span_count",
        "retrieval_suppressed_unit_count",
        "hot_line_total",
        "retrieved_line_total",
        "rendered_retrieved_unique_unit_count",
        "query_embedding_cache_rows",
        "vector_rows",
    ):
        lines.append(f"| `{key}` | `{total.get(key, 0)}` |")
    lines.extend(["", "## Outputs", ""])
    for output in summary.get("outputs", []):
        lines.append(f"### {output.get('label')}")
        lines.append("")
        lines.append(f"- status: `{output.get('status')}`")
        if output.get("warnings"):
            lines.append(f"- warnings: `{', '.join(output.get('warnings', []))}`")
        config = output.get("config", {})
        lines.append(f"- mode: `{config.get('mode')}`")
        sqlite = output.get("sqlite", {})
        trace = output.get("trace", {})
        reading_memory = output.get("reading_memory", {})
        lines.append(f"- unit entries: `{sqlite.get('entries', 0)}`")
        lines.append(f"- retrieval docs: `{sqlite.get('retrieval_docs', 0)}`")
        lines.append(f"- sqlite-vec table: `{sqlite.get('sqlite_vec_table_present')}`")
        lines.append(f"- vector rows: `{sqlite.get('vector_rows', 0)}`")
        lines.append(f"- query embedding cache rows: `{sqlite.get('query_embedding_cache_rows', 0)}`")
        lines.append(f"- retrieval rows: `{trace.get('retrieval_rows', 0)}`")
        lines.append(f"- selected units: `{trace.get('selected_unit_count', 0)}`")
        lines.append(f"- renderable selected units: `{sqlite.get('selected_renderable_unit_count', 0)}`")
        lines.append(
            "- excluded prompt-visible hot spans: "
            f"`total={trace.get('excluded_source_unit_span_total', 0)}, "
            f"rows={trace.get('retrieval_rows_with_excluded_source_unit_spans', 0)}, "
            f"max={trace.get('max_excluded_source_unit_span_count', 0)}`"
        )
        lines.append(f"- hot / retrieved lines: `{reading_memory.get('hot_line_total', 0)} / {reading_memory.get('retrieved_line_total', 0)}`")
        lines.append(f"- rendered retrieved unique units: `{reading_memory.get('rendered_retrieved_unique_unit_count', 0)}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Run roots, output dirs, or runtime dirs to inspect.")
    parser.add_argument("--write-json", type=Path, help="Optional path for JSON summary.")
    parser.add_argument("--write-markdown", type=Path, help="Optional path for Markdown report.")
    parser.add_argument("--fail-on-needs-repair", action="store_true", help="Exit nonzero when status is needs_repair.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = summarize_paths([Path(item) for item in args.paths])
    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.write_markdown:
        args.write_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.write_markdown.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 1 if args.fail_on_needs_repair and summary.get("status") != "ok" else 0


if __name__ == "__main__":
    raise SystemExit(main())
