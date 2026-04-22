#!/usr/bin/env python3
"""One-off renderer for the April 22 Long Span contract-fix rejudge audit.

This is intentionally not a reusable evaluation framework component. It reads
the completed rejudge run artifacts and renders human-review Markdown under the
run's ignored analysis directory.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any


MECHANISMS = ("attentional_v2", "iterator_v1")

BACKEND_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = BACKEND_ROOT / "eval" / "runs" / "attentional_v2"
RUN_ID = "attentional_v2_accumulation_benchmark_v2_frozen_rejudge_contract_fix_20260422"
RUN_ROOT = RUNS_ROOT / RUN_ID
OUTPUT_DIR = RUN_ROOT / "analysis" / "longspan_rejudge_audit_20260422"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel_link(from_file: Path, target: Path, label: str | None = None) -> str:
    rel = os.path.relpath(target, start=from_file.parent).replace(os.sep, "/")
    return f"[{label or target.name}]({rel})"


def fenced(value: Any, lang: str = "text") -> str:
    if value in (None, "", [], {}):
        return "_none_"
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, indent=2)
        lang = "json"
    return f"~~~{lang}\n{value.rstrip()}\n~~~"


def table_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
    elif isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("\n", "<br>").replace("|", "\\|")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(table_cell(item) for item in row) + " |")
    return "\n".join(lines)


def _source_dataset_dir(aggregate: dict[str, Any]) -> Path | None:
    raw = str(aggregate.get("dataset_dir") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_absolute() else BACKEND_ROOT / path


def _segment_index(dataset_dir: Path | None) -> dict[str, dict[str, Any]]:
    if dataset_dir is None:
        return {}
    manifest_path = dataset_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    manifest = load_json(manifest_path)
    segments_path = dataset_dir / str(manifest.get("segments_file") or "segments.jsonl")
    if not segments_path.exists():
        return {}
    return {row["segment_id"]: row for row in load_jsonl(segments_path)}


def _render_point(point: dict[str, Any]) -> str:
    label = point.get("label") or point.get("point_id") or point.get("node_id") or "point"
    lines = [f"- `{label}`"]
    summary = point.get("summary")
    if summary:
        lines.append(f"  - summary: {summary}")
    span_text = point.get("span_text")
    if span_text:
        lines.append("  - source text:")
        lines.append(fenced(span_text))
    slices = point.get("span_slices") or []
    if slices:
        lines.append("  - slices:")
        lines.append(fenced(slices, "json"))
    return "\n".join(lines)


def _reaction_title(item: dict[str, Any], index: int) -> str:
    reaction_id = item.get("reaction_id") or item.get("event_id") or f"item_{index}"
    return f"`{reaction_id}`"


def _render_reaction_like(item: dict[str, Any], index: int) -> str:
    lines = [f"{index}. {_reaction_title(item, index)}"]
    if item.get("section_ref"):
        lines.append(f"- section_ref: `{item.get('section_ref')}`")
    if item.get("move_type"):
        lines.append(f"- move_type: `{item.get('move_type')}`")
    if item.get("matched_callback_label") or item.get("matched_callback_point_id"):
        lines.append(
            "- callback target: "
            f"`{item.get('matched_callback_label') or item.get('matched_callback_point_id')}`"
        )
    if item.get("evidence_role"):
        lines.append(f"- evidence role: `{item.get('evidence_role')}`")
    if item.get("overlap_coverage") not in (None, ""):
        lines.append(f"- overlap coverage: `{item.get('overlap_coverage')}`")
    if item.get("anchor_quote"):
        lines.append("- anchor quote:")
        lines.append(fenced(item.get("anchor_quote")))
    if item.get("current_excerpt"):
        lines.append("- current excerpt:")
        lines.append(fenced(item.get("current_excerpt")))
    content = item.get("content") or item.get("message") or item.get("visible_text")
    if content:
        lines.append("- visible reaction / message:")
        lines.append(fenced(content))
    if item.get("source_span_slices"):
        lines.append("- source locator:")
        lines.append(fenced(item.get("source_span_slices"), "json"))
    return "\n".join(lines)


def _render_reaction_list(items: list[dict[str, Any]], *, empty: str) -> str:
    if not items:
        return empty
    return "\n\n".join(_render_reaction_like(dict(item), index) for index, item in enumerate(items, 1))


def _case_interpretation(evidence: dict[str, Any], judgment: dict[str, Any]) -> str:
    target_count = len(evidence.get("target_local_reactions") or [])
    callback_count = len(evidence.get("explicit_callback_actions") or [])
    followup_count = len(evidence.get("short_horizon_followups") or [])
    score = judgment.get("quality_score")
    if target_count == 0 and callback_count == 0 and followup_count == 0:
        return (
            "This mechanism has no target-visible evidence under the repaired contract. "
            "The judge should not credit the target source passage itself, so this should stay low-scored."
        )
    return (
        f"Target-visible evidence counts: target-local={target_count}, "
        f"explicit-callback={callback_count}, short-followup={followup_count}. "
        f"The assigned quality score is `{score}`; inspect the judge reason for whether those visible items "
        "actually recalled or used the upstream refs."
    )


def _render_case(case: dict[str, Any]) -> str:
    lines = [
        f"### `{case['case_id']}`",
        "",
        f"- Book: `{case.get('book')}`",
        f"- Source id: `{case.get('source_id')}`",
        f"- Window id: `{case.get('window_id')}`",
        f"- Thread type: `{case.get('thread_type')}`",
    ]
    first_evidence = next(
        (
            (result.get("target_evidence_bundle") or {})
            for result in (case.get("mechanism_results") or {}).values()
            if result.get("target_evidence_bundle")
        ),
        {},
    )
    lines.extend(["", "**Target span**", "", _render_point(first_evidence.get("target_ref") or {})])
    upstream = first_evidence.get("upstream_refs") or []
    lines.extend(["", "**Upstream refs**", ""])
    lines.append("\n\n".join(_render_point(dict(item)) for item in upstream) if upstream else "_none_")
    lines.extend(
        [
            "",
            "**Expected integration**",
            "",
            fenced(first_evidence.get("expected_integration")),
            "",
            "**Contract reminder**",
            "",
            "The target span and upstream refs define the case. They are not mechanism output evidence. "
            "The score should come from target-local reactions, target-proximal callback actions, and short-horizon followups.",
        ]
    )
    for mechanism in MECHANISMS:
        result = (case.get("mechanism_results") or {}).get(mechanism) or {}
        evidence = result.get("target_evidence_bundle") or {}
        judgment = result.get("judgment") or {}
        lines.extend(
            [
                "",
                f"#### `{mechanism}`",
                "",
                f"- Status: `{result.get('status')}`",
                f"- Quality score: `{judgment.get('quality_score')}`",
                f"- Callback score: `{judgment.get('callback_score')}`",
                f"- Thread built: `{judgment.get('thread_built')}`",
                "",
                "**Case-level interpretation**",
                "",
                _case_interpretation(evidence, judgment),
                "",
                "**Judge reason**",
                "",
                fenced(judgment.get("reason")),
                "",
                "**Target-local reactions**",
                "",
                _render_reaction_list(
                    [dict(item) for item in evidence.get("target_local_reactions") or []],
                    empty="_none: no visible reaction overlapped the target source span._",
                ),
                "",
                "**Explicit callback actions**",
                "",
                "These count only when they are target-local or short-horizon post-target callbacks to an upstream/callback-eligible span.",
                "",
                _render_reaction_list(
                    [dict(item) for item in evidence.get("explicit_callback_actions") or []],
                    empty="_none: no target-proximal callback evidence was found._",
                ),
                "",
                "**Short-horizon followups**",
                "",
                "These are the next visible reactions after the latest target-local reaction. They are listed for judgment, but are not automatically callbacks.",
                "",
                _render_reaction_list(
                    [dict(item) for item in evidence.get("short_horizon_followups") or []],
                    empty="_none: no followup window exists because no target-local reaction was available, or there were no later reactions._",
                ),
                "",
                "**Pre-target observed callbacks / audit-only context**",
                "",
                "These may show the mechanism touched upstream material earlier, but they are not target-visible scoring evidence under the repaired contract.",
                "",
                _render_reaction_list(
                    [dict(item) for item in evidence.get("pre_target_observed_callbacks") or []],
                    empty="_none_",
                ),
            ]
        )
    return "\n".join(lines)


def _render_source_texts(
    *,
    out_dir: Path,
    segment_index: dict[str, dict[str, Any]],
    dataset_dir: Path | None,
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    if dataset_dir is None:
        return paths
    for segment_id, segment in segment_index.items():
        rel_path = segment.get("segment_source_path")
        if not rel_path:
            continue
        source_path = dataset_dir / str(rel_path)
        if not source_path.exists():
            continue
        out_path = out_dir / "source_texts" / f"{segment_id}.md"
        write_text(out_path, f"# Source Text: {segment_id}\n\n~~~text\n{source_path.read_text(encoding='utf-8')}\n~~~")
        paths[segment_id] = out_path
    return paths


def main() -> int:
    aggregate_path = RUN_ROOT / "summary" / "aggregate.json"
    case_results_path = RUN_ROOT / "summary" / "case_results.jsonl"
    if not aggregate_path.exists() or not case_results_path.exists():
        raise SystemExit(f"missing completed rejudge summary under {RUN_ROOT}")

    aggregate = load_json(aggregate_path)
    cases = load_jsonl(case_results_path)
    dataset_dir = _source_dataset_dir(aggregate)
    segment_index = _segment_index(dataset_dir)
    source_text_paths = _render_source_texts(out_dir=OUTPUT_DIR, segment_index=segment_index, dataset_dir=dataset_dir)

    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_source[str(case.get("source_id"))].append(case)

    longspan_paths: dict[str, Path] = {}
    for source_id, source_cases in sorted(by_source.items()):
        out_path = OUTPUT_DIR / "longspan" / f"{source_id}.md"
        segment_id = str(source_cases[0].get("window_id") or "")
        rows: list[list[Any]] = []
        for mechanism in MECHANISMS:
            values = [
                (case.get("mechanism_results", {}).get(mechanism, {}).get("judgment") or {}).get("quality_score")
                for case in source_cases
            ]
            nums = [float(value) for value in values if value is not None]
            rows.append([mechanism, len(source_cases), round(sum(nums) / len(nums), 3) if nums else ""])
        lines = [
            f"# Long Span Rejudge Audit: {source_cases[0].get('book')}",
            "",
            f"- Source id: `{source_id}`",
            f"- Window id: `{segment_id}`",
        ]
        if segment_id in source_text_paths:
            lines.append(f"- Complete source text: {rel_link(out_path, source_text_paths[segment_id])}")
        lines.extend(["", "## Score Snapshot", "", md_table(["mechanism", "cases", "avg quality"], rows), ""])
        lines.extend(_render_case(case) for case in sorted(source_cases, key=lambda item: item["case_id"]))
        write_text(out_path, "\n\n".join(lines))
        longspan_paths[source_id] = out_path

    overview_rows: list[list[Any]] = []
    for mechanism in MECHANISMS:
        stats = (aggregate.get("mechanisms") or {}).get(mechanism) or {}
        overview_rows.append(
            [
                mechanism,
                stats.get("case_count"),
                stats.get("average_quality_score"),
                stats.get("average_callback_score"),
                stats.get("thread_built_counts"),
            ]
        )
    source_rows = [
        [source_id, len(source_cases), rel_link(OUTPUT_DIR / "README.md", longspan_paths[source_id], "audit")]
        for source_id, source_cases in sorted(by_source.items())
    ]
    readme = [
        "# Long Span Rejudge Audit 20260422",
        "",
        f"- Run id: `{RUN_ID}`",
        "- Contract: score target-visible mechanism evidence only; case-definition text cannot create credit by itself.",
        "- Old April 19 Long Span score is treated as invalidated diagnostic evidence for this surface.",
        "",
        "## Aggregate",
        "",
        md_table(["mechanism", "cases", "avg quality", "avg callback", "thread built counts"], overview_rows),
        "",
        "## Source Files",
        "",
        md_table(["source id", "cases", "audit doc"], source_rows),
        "",
        "## Why This Rejudge Exists",
        "",
        "The old judge contract could award high scores from the target passage itself or from callback events that occurred before the target. This audit shows the repaired evidence split for every case: target-local reactions, target-proximal callbacks, short-horizon followups, and pre-target audit-only callbacks.",
    ]
    write_text(OUTPUT_DIR / "README.md", "\n".join(readme))
    print(json.dumps({"output_dir": str(OUTPUT_DIR), "case_count": len(cases)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
