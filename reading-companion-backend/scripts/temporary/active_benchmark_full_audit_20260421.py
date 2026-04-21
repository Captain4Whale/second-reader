#!/usr/bin/env python3
"""One-off renderer for the April 21 full active benchmark audit docs.

This is intentionally not part of the reusable evaluation framework. It only
reads already-completed April 19 benchmark outputs and renders human-review
Markdown under the parent run's ignored analysis directory.
"""

from __future__ import annotations

import json
import os
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MECHANISMS = ("attentional_v2", "iterator_v1")

BACKEND_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = BACKEND_ROOT / "eval" / "runs" / "attentional_v2"
PARENT_RUN = RUNS_ROOT / "attentional_v2_active_benchmark_rerun_20260419"
EXCERPT_RUN = RUNS_ROOT / "attentional_v2_user_level_selective_v1_active_rerun_20260419"
LONGSPAN_RUN = RUNS_ROOT / "attentional_v2_accumulation_benchmark_v2_frozen_active_rerun_20260419"
DATASET_ROOT = (
    BACKEND_ROOT
    / "state"
    / "eval_local_datasets"
    / "user_level_benchmarks"
    / "attentional_v2_user_level_selective_v1_repaired_20260416"
)
OUTPUT_DIR = PARENT_RUN / "analysis" / "full_case_audit_20260421"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel_link(from_file: Path, target: Path, label: str | None = None) -> str:
    rel = os.path.relpath(target, start=from_file.parent).replace(os.sep, "/")
    return f"[{label or target.name}]({rel})"


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
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(table_cell(v) for v in row) + " |")
    return "\n".join(out)


def fenced(text: Any, lang: str = "text") -> str:
    if text is None or text == "":
        return "_empty_"
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False, indent=2)
        lang = "json"
    return f"~~~{lang}\n{text.rstrip()}\n~~~"


def first_existing(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def span_key(slices: list[dict[str, Any]] | None) -> tuple[int, int, int]:
    if not slices:
        return (10**9, 10**9, 10**9)
    first = slices[0]
    return (
        int(first.get("paragraph_index", first.get("paragraph_start", 10**9)) or 10**9),
        int(first.get("char_start", 10**9) or 10**9),
        int(first.get("char_end", 10**9) or 10**9),
    )


def format_slices(slices: list[dict[str, Any]] | None) -> str:
    if not slices:
        return "_none_"
    lines: list[str] = []
    for idx, item in enumerate(slices, 1):
        paragraph = first_existing(
            item.get("paragraph_index"),
            item.get("paragraph_start"),
            item.get("paragraph"),
        )
        char_start = item.get("char_start")
        char_end = item.get("char_end")
        coordinate = item.get("coordinate_system") or "unknown"
        lines.append(f"{idx}. `{coordinate}` p`{paragraph}` chars `{char_start}`-`{char_end}`")
        if item.get("text"):
            lines.append(fenced(item["text"]))
    return "\n\n".join(lines)


def reaction_slices(reaction: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not reaction:
        return []
    if isinstance(reaction.get("source_span_slices"), list):
        return reaction["source_span_slices"]
    locator = reaction.get("target_locator") or {}
    if not locator and isinstance(reaction.get("primary_anchor"), dict):
        locator = reaction["primary_anchor"].get("locator") or {}
    if not locator:
        return []
    return [
        {
            "coordinate_system": "normalized_locator",
            "paragraph_index": first_existing(locator.get("paragraph_index"), locator.get("paragraph_start")),
            "char_start": locator.get("char_start"),
            "char_end": locator.get("char_end"),
            "text": reaction.get("anchor_quote") or reaction.get("quote") or "",
        }
    ]


def render_reaction_block(reaction: dict[str, Any] | None, heading: str = "Reaction") -> str:
    if not reaction:
        return "_none_"
    rid = reaction.get("reaction_id") or reaction.get("id") or "unknown"
    compat_type = reaction.get("type") or reaction.get("compat_family") or ""
    lines = [f"**{heading}:** `{rid}`"]
    if compat_type:
        lines.append(f"- Compat type: `{compat_type}`")
    if reaction.get("chapter_ref") or reaction.get("section_ref"):
        lines.append(
            f"- Source ref: `{reaction.get('chapter_ref', '')}` / `{reaction.get('section_ref', '')}`"
        )
    if reaction.get("source_span_resolution") or reaction.get("overlap_relation"):
        lines.append(
            "- Match relation: "
            f"`{reaction.get('source_span_resolution', '')}` / "
            f"`{reaction.get('overlap_relation', '')}` / "
            f"coverage `{reaction.get('overlap_coverage', '')}`"
        )
    if reaction.get("anchor_quote"):
        lines.append("- Anchor quote:")
        lines.append(fenced(reaction["anchor_quote"]))
    lines.append("- Source locator:")
    lines.append(format_slices(reaction_slices(reaction)))
    content = first_existing(reaction.get("content"), reaction.get("thought"), reaction.get("reaction_text"))
    if content:
        lines.append("- Original reaction text:")
        lines.append(fenced(content))
    if reaction.get("prior_link"):
        lines.append("- Prior link:")
        lines.append(fenced(reaction["prior_link"]))
    if reaction.get("outside_link"):
        lines.append("- Outside link:")
        lines.append(fenced(reaction["outside_link"]))
    if reaction.get("search_intent") or reaction.get("search_query"):
        lines.append("- Search intent/query:")
        lines.append(fenced(first_existing(reaction.get("search_intent"), reaction.get("search_query"))))
    return "\n\n".join(lines)


def interpretation_for_label(label: str | None, judgment: dict[str, Any] | None) -> str:
    reason = (judgment or {}).get("reason")
    if label == "exact_match":
        return "Exact source-span overlap was sufficient to count this case automatically."
    if label == "focused_hit":
        return "The candidate overlap was not merely broad coverage; the judge accepted it as focused on the case."
    if label == "incidental_cover":
        return "A reaction touched overlapping source text, but the judge treated it as incidental or too partial for recall."
    if label == "miss":
        return "No focused source-grounded reaction covered the case strongly enough to count."
    if reason:
        return reason
    return "No case-level interpretation was available in the stored judgment."


def normalize_score(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def load_segments() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    segments = load_jsonl(DATASET_ROOT / "segments.jsonl")
    return segments, {row["source_id"]: row for row in segments}


def load_excerpt_cases(source_id: str) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for mechanism in MECHANISMS:
        shard_dir = EXCERPT_RUN / "shards" / f"{source_id}__{mechanism}" / "note_cases"
        if not shard_dir.exists():
            raise FileNotFoundError(f"Missing note_cases dir: {shard_dir}")
        for path in sorted(shard_dir.glob("*.json")):
            payload = load_json(path)
            case_id = payload["note_case_id"]
            entry = cases.setdefault(
                case_id,
                {
                    "note_case_id": case_id,
                    "segment_id": payload.get("segment_id"),
                    "source_id": payload.get("source_id"),
                    "book_title": payload.get("book_title"),
                    "language_track": payload.get("language_track"),
                    "note_case": payload.get("note_case") or {},
                    "mechanism_results": {},
                },
            )
            result = (payload.get("mechanism_results") or {}).get(mechanism)
            if result is None:
                raise ValueError(f"Missing mechanism result for {mechanism} in {path}")
            entry["mechanism_results"][mechanism] = result
    for case_id, entry in cases.items():
        missing = [m for m in MECHANISMS if m not in entry["mechanism_results"]]
        if missing:
            raise ValueError(f"Case {case_id} missing mechanisms: {missing}")
    return cases


def normalized_bundle_path(source_id: str, mechanism: str) -> Path:
    shard_dir = EXCERPT_RUN / "shards" / f"{source_id}__{mechanism}"
    matches = sorted(
        shard_dir.glob(
            f"outputs/*/{mechanism}/_mechanisms/{mechanism}/exports/normalized_eval_bundle.json"
        )
    )
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one normalized bundle for {source_id} {mechanism}, found {len(matches)}")
    return matches[0]


def load_reactions(source_id: str, mechanism: str) -> list[dict[str, Any]]:
    bundle = load_json(normalized_bundle_path(source_id, mechanism))
    return bundle.get("reactions") or []


def render_source_text_docs(segments: list[dict[str, Any]]) -> dict[str, Path]:
    output_paths: dict[str, Path] = {}
    for segment in segments:
        segment_id = segment["segment_id"]
        source_path = DATASET_ROOT / segment.get("segment_source_path", f"segment_sources/{segment_id}.txt")
        text = source_path.read_text(encoding="utf-8")
        out_path = OUTPUT_DIR / "source_texts" / f"{segment_id}.md"
        output_paths[segment_id] = out_path
        write_text(
            out_path,
            "\n".join(
                [
                    f"# Source Text: `{segment_id}`",
                    "",
                    f"- Book: {segment.get('book_title')}",
                    f"- Source id: `{segment.get('source_id')}`",
                    f"- Sentence range: `{segment.get('start_sentence_id')}` -> `{segment.get('end_sentence_id')}`",
                    f"- Source coordinate system: `{segment.get('source_span_coordinate_system', 'segment_source_v1')}`",
                    "",
                    "This is the complete benchmark reading-window text used by the rerun, not the whole EPUB.",
                    "",
                    fenced(text),
                ]
            ),
        )
    return output_paths


def render_reaction_docs(
    segments: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], Path], dict[tuple[str, str], int]]:
    paths: dict[tuple[str, str], Path] = {}
    counts: dict[tuple[str, str], int] = {}
    for segment in segments:
        source_id = segment["source_id"]
        for mechanism in MECHANISMS:
            reactions = load_reactions(source_id, mechanism)
            counts[(source_id, mechanism)] = len(reactions)
            out_path = OUTPUT_DIR / "reactions" / f"{source_id}__{mechanism}.md"
            paths[(source_id, mechanism)] = out_path
            lines = [
                f"# Reactions: `{source_id}` / `{mechanism}`",
                "",
                f"- Book: {segment.get('book_title')}",
                f"- Segment: `{segment.get('segment_id')}`",
                f"- Reaction count: `{len(reactions)}`",
                f"- Normalized bundle: `{normalized_bundle_path(source_id, mechanism)}`",
                "",
                "Every entry below is copied from the stored normalized bundle. `type` is a compatibility projection, not V2 native truth.",
            ]
            for idx, reaction in enumerate(reactions, 1):
                lines.extend(["", f"## Reaction {idx}", "", render_reaction_block(reaction, "Stored reaction")])
            write_text(out_path, "\n".join(lines))
    return paths, counts


def render_excerpt_doc(
    segment: dict[str, Any],
    cases: dict[str, dict[str, Any]],
    excerpt_aggregate: dict[str, Any],
    source_text_paths: dict[str, Path],
    reaction_paths: dict[tuple[str, str], Path],
) -> tuple[Path, int]:
    source_id = segment["source_id"]
    segment_id = segment["segment_id"]
    out_path = OUTPUT_DIR / "excerpt" / f"{source_id}.md"
    sorted_cases = sorted(
        cases.values(),
        key=lambda item: (
            span_key((item.get("note_case") or {}).get("source_span_slices")),
            item["note_case_id"],
        ),
    )
    rows: list[list[Any]] = []
    for mechanism in MECHANISMS:
        stats = (
            excerpt_aggregate.get("mechanisms", {})
            .get(mechanism, {})
            .get("by_source", {})
            .get(source_id, {})
        )
        label_counts = stats.get("label_counts", {})
        rows.append(
            [
                mechanism,
                stats.get("note_case_count"),
                stats.get("note_recall"),
                label_counts.get("exact_match", 0),
                label_counts.get("focused_hit", 0),
                label_counts.get("incidental_cover", 0),
                label_counts.get("miss", 0),
            ]
        )
    lines = [
        f"# Excerpt Audit: {segment.get('book_title')}",
        "",
        f"- Source id: `{source_id}`",
        f"- Segment id: `{segment_id}`",
        f"- Language: `{segment.get('language_track')}`",
        f"- Sentence range: `{segment.get('start_sentence_id')}` -> `{segment.get('end_sentence_id')}`",
        f"- Source chapters: `{segment.get('source_chapter_ids')}`",
        f"- Chapter titles: {', '.join(segment.get('chapter_titles') or [])}",
        f"- Termination reason: `{segment.get('termination_reason')}`",
        f"- Complete source text: {rel_link(out_path, source_text_paths[segment_id])}",
        f"- `attentional_v2` reactions: {rel_link(out_path, reaction_paths[(source_id, 'attentional_v2')])}",
        f"- `iterator_v1` reactions: {rel_link(out_path, reaction_paths[(source_id, 'iterator_v1')])}",
        "",
        "## Score Snapshot",
        "",
        md_table(
            ["mechanism", "note cases", "note recall", "exact", "focused", "incidental", "miss"],
            rows,
        ),
        "",
        "## How To Read These Cases",
        "",
        "- `exact_match` and `focused_hit` count toward note recall.",
        "- `incidental_cover` means source overlap existed, but the judged reaction was too broad or partial.",
        "- `miss` means no focused source-span candidate covered the human note case.",
        "",
        "## Note Cases",
    ]
    for idx, case in enumerate(sorted_cases, 1):
        note_case = case.get("note_case") or {}
        lines.extend(
            [
                "",
                f"### Case {idx}: `{case['note_case_id']}`",
                "",
                f"- Note id: `{note_case.get('note_id', '')}`",
                f"- Source chapter id: `{note_case.get('source_chapter_id', note_case.get('chapter_id', ''))}`",
                f"- Chapter title: {note_case.get('chapter_title', '')}",
                f"- Section label / raw locator: `{note_case.get('section_label', '')}` / `{note_case.get('raw_locator', '')}`",
                "",
                "**Human note text**",
                "",
                fenced(note_case.get("note_text")),
            ]
        )
        if note_case.get("note_comment"):
            lines.extend(["", "**Human note comment**", "", fenced(note_case["note_comment"])])
        lines.extend(
            [
                "",
                "**Canonical case/source text**",
                "",
                fenced(note_case.get("source_span_text")),
                "",
                "**Source span slices**",
                "",
                format_slices(note_case.get("source_span_slices")),
            ]
        )
        for mechanism in MECHANISMS:
            result = case["mechanism_results"][mechanism]
            judgment = result.get("judgment") or {}
            lines.extend(
                [
                    "",
                    f"#### `{mechanism}` scoring",
                    "",
                    f"- Label: `{result.get('label')}`",
                    f"- Counts for recall: `{result.get('counts_for_recall')}`",
                    f"- Candidate reactions: `{len(result.get('candidate_reactions') or [])}`",
                    f"- Judge confidence: `{judgment.get('confidence', '')}`",
                    "",
                    "**Judge reason**",
                    "",
                    fenced(judgment.get("reason")),
                    "",
                    "**Case-level interpretation**",
                    "",
                    interpretation_for_label(result.get("label"), judgment),
                    "",
                    render_reaction_block(result.get("best_reaction"), "Best reaction"),
                ]
            )
            candidates = result.get("candidate_reactions") or []
            lines.append("")
            lines.append(f"**All candidate reactions ({len(candidates)})**")
            if candidates:
                for cand_idx, reaction in enumerate(candidates, 1):
                    lines.extend(["", f"Candidate {cand_idx}", "", render_reaction_block(reaction, "Candidate reaction")])
            else:
                lines.extend(["", "_none_"])
    write_text(out_path, "\n".join(lines))
    return out_path, len(sorted_cases)


def render_longspan_value(value: Any) -> str:
    if value is None:
        return "_none_"
    if isinstance(value, str):
        return fenced(value)
    if isinstance(value, list):
        if not value:
            return "_none_"
        lines: list[str] = []
        for idx, item in enumerate(value, 1):
            lines.append(f"{idx}.")
            lines.append(render_longspan_value(item))
        return "\n\n".join(lines)
    if isinstance(value, dict):
        if "span_text" in value or "text" in value:
            lines = []
            label = value.get("label") or value.get("point_id") or value.get("id")
            if label:
                lines.append(f"- Label: `{label}`")
            if value.get("span_text") or value.get("text"):
                lines.append(fenced(value.get("span_text") or value.get("text")))
            if value.get("span_slices") or value.get("source_span_slices"):
                lines.append(format_slices(value.get("span_slices") or value.get("source_span_slices")))
            return "\n\n".join(lines)
        return fenced(value, "json")
    return fenced(str(value))


def longspan_case_interpretation(results: dict[str, Any]) -> str:
    scores: dict[str, tuple[float, float]] = {}
    for mechanism, result in results.items():
        judgment = result.get("judgment") or {}
        scores[mechanism] = (
            float(judgment.get("quality_score") or 0),
            float(judgment.get("callback_score") or 0),
        )
    if scores["attentional_v2"] > scores["iterator_v1"]:
        return "By stored quality/callback scores, this case favors `attentional_v2`: its target-local evidence carried the prepared long-range thread more strongly."
    if scores["iterator_v1"] > scores["attentional_v2"]:
        return "By stored quality/callback scores, this case favors `iterator_v1`: it reconstructed or carried the prepared long-range thread more strongly at the target."
    return "The stored quality/callback scores are tied or effectively indistinguishable for this case."


def render_longspan_docs(
    long_cases: list[dict[str, Any]],
    segment_by_source: dict[str, dict[str, Any]],
    source_text_paths: dict[str, Path],
    reaction_paths: dict[tuple[str, str], Path],
) -> tuple[dict[str, Path], int]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in long_cases:
        by_source[case["source_id"]].append(case)
    out_paths: dict[str, Path] = {}
    total = 0
    for source_id, cases in sorted(by_source.items()):
        segment = segment_by_source[source_id]
        out_path = OUTPUT_DIR / "longspan" / f"{source_id}.md"
        out_paths[source_id] = out_path
        rows: list[list[Any]] = []
        for mechanism in MECHANISMS:
            quality_values = [
                (case.get("mechanism_results", {}).get(mechanism, {}).get("judgment") or {}).get("quality_score")
                for case in cases
            ]
            callback_values = [
                (case.get("mechanism_results", {}).get(mechanism, {}).get("judgment") or {}).get("callback_score")
                for case in cases
            ]
            quality_nums = [float(v) for v in quality_values if v is not None]
            callback_nums = [float(v) for v in callback_values if v is not None]
            rows.append(
                [
                    mechanism,
                    len(cases),
                    round(sum(quality_nums) / len(quality_nums), 3) if quality_nums else "",
                    round(sum(callback_nums) / len(callback_nums), 3) if callback_nums else "",
                ]
            )
        lines = [
            f"# Long-Span Audit: {segment.get('book_title')}",
            "",
            f"- Source id: `{source_id}`",
            f"- Segment id: `{segment.get('segment_id')}`",
            f"- Complete source text: {rel_link(out_path, source_text_paths[segment['segment_id']])}",
            f"- `attentional_v2` reactions: {rel_link(out_path, reaction_paths[(source_id, 'attentional_v2')])}",
            f"- `iterator_v1` reactions: {rel_link(out_path, reaction_paths[(source_id, 'iterator_v1')])}",
            "",
            "## Score Snapshot",
            "",
            md_table(["mechanism", "cases", "avg quality", "avg callback"], rows),
            "",
            "## Target Cases",
        ]
        for idx, case in enumerate(sorted(cases, key=lambda item: item["case_id"]), 1):
            total += 1
            lines.extend(
                [
                    "",
                    f"### Case {idx}: `{case['case_id']}`",
                    "",
                    f"- Window id: `{case.get('window_id')}`",
                    f"- Thread type: `{case.get('thread_type')}`",
                    "",
                    "**Case-level interpretation**",
                    "",
                    longspan_case_interpretation(case.get("mechanism_results") or {}),
                ]
            )
            first_bundle = next(
                (
                    result.get("target_evidence_bundle")
                    for result in (case.get("mechanism_results") or {}).values()
                    if result.get("target_evidence_bundle")
                ),
                {},
            )
            lines.extend(
                [
                    "",
                    "**Target span**",
                    "",
                    render_longspan_value(first_bundle.get("target_ref")),
                    "",
                    "**Upstream refs**",
                    "",
                    render_longspan_value(first_bundle.get("upstream_refs")),
                    "",
                    "**Expected integration**",
                    "",
                    render_longspan_value(first_bundle.get("expected_integration")),
                    "",
                    "**Non-goal but tempting points**",
                    "",
                    render_longspan_value(first_bundle.get("non_goal_but_tempting_points")),
                ]
            )
            for mechanism in MECHANISMS:
                result = (case.get("mechanism_results") or {}).get(mechanism) or {}
                judgment = result.get("judgment") or {}
                evidence = result.get("target_evidence_bundle") or {}
                lines.extend(
                    [
                        "",
                        f"#### `{mechanism}` judgment",
                        "",
                        f"- Status: `{result.get('status')}`",
                        f"- Quality score: `{judgment.get('quality_score')}`",
                        f"- Callback score: `{judgment.get('callback_score')}`",
                        f"- Thread built: `{judgment.get('thread_built')}`",
                        "",
                        "**Judge reason**",
                        "",
                        fenced(judgment.get("reason")),
                        "",
                        "**Target-local reactions**",
                        "",
                        render_longspan_value(evidence.get("target_local_reactions")),
                        "",
                        "**Explicit callback actions**",
                        "",
                        render_longspan_value(evidence.get("explicit_callback_actions")),
                        "",
                        "**Short-horizon followups**",
                        "",
                        render_longspan_value(evidence.get("short_horizon_followups")),
                    ]
                )
        write_text(out_path, "\n".join(lines))
    return out_paths, total


def render_summary_analysis(
    segments: list[dict[str, Any]],
    excerpt_aggregate: dict[str, Any],
    long_aggregate: dict[str, Any],
    long_cases: list[dict[str, Any]],
) -> Path:
    out_path = OUTPUT_DIR / "summary_analysis.md"
    excerpt_rows: list[list[Any]] = []
    for segment in segments:
        source_id = segment["source_id"]
        row = [segment.get("book_title"), source_id]
        for mechanism in MECHANISMS:
            stats = (
                excerpt_aggregate.get("mechanisms", {})
                .get(mechanism, {})
                .get("by_source", {})
                .get(source_id, {})
            )
            row.append(stats.get("note_recall"))
        winner = "attentional_v2"
        if row[3] is not None and row[2] is not None and row[3] > row[2]:
            winner = "iterator_v1"
        elif row[2] == row[3]:
            winner = "tie"
        row.append(winner)
        excerpt_rows.append(row)

    long_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in long_cases:
        long_by_source[case["source_id"]].append(case)
    long_rows: list[list[Any]] = []
    for source_id, cases in sorted(long_by_source.items()):
        title = cases[0].get("book")
        row = [title, source_id, len(cases)]
        mechanism_scores: dict[str, float] = {}
        for mechanism in MECHANISMS:
            values = [
                (case.get("mechanism_results", {}).get(mechanism, {}).get("judgment") or {}).get(
                    "quality_score"
                )
                for case in cases
            ]
            nums = [float(v) for v in values if v is not None]
            avg = round(sum(nums) / len(nums), 3) if nums else 0
            mechanism_scores[mechanism] = avg
            row.append(avg)
        if mechanism_scores["attentional_v2"] > mechanism_scores["iterator_v1"]:
            row.append("attentional_v2")
        elif mechanism_scores["iterator_v1"] > mechanism_scores["attentional_v2"]:
            row.append("iterator_v1")
        else:
            row.append("tie")
        long_rows.append(row)

    excerpt_mechs = excerpt_aggregate.get("mechanisms", {})
    long_mechs = long_aggregate.get("mechanisms", {})
    lines = [
        "# Summary Analysis",
        "",
        "## Top-Line Results",
        "",
        md_table(
            ["level", "attentional_v2", "iterator_v1", "primary metric"],
            [
                [
                    "Excerpt / Selective Legibility",
                    excerpt_mechs.get("attentional_v2", {}).get("note_recall"),
                    excerpt_mechs.get("iterator_v1", {}).get("note_recall"),
                    "note_recall",
                ],
                [
                    "Long-span / Coherent Accumulation",
                    long_mechs.get("attentional_v2", {}).get("average_quality_score"),
                    long_mechs.get("iterator_v1", {}).get("average_quality_score"),
                    "average_quality_score",
                ],
            ],
        ),
        "",
        "## Excerpt-Level Pattern",
        "",
        md_table(
            ["book", "source id", "attentional_v2 recall", "iterator_v1 recall", "winner"],
            excerpt_rows,
        ),
        "",
        "The excerpt result is clear: `attentional_v2` wins the current Selective Legibility benchmark overall, with `0.3498` note recall against `iterator_v1` at `0.1232`. The most important caution is that this is still an absolute recall ceiling problem: V2 leads, but it does not yet cover most human-highlighted material.",
        "",
        "Case-level inspection should focus on why misses happen: whether the model did not read/notice the exact human note span, reacted nearby but too broadly, or produced a valid reaction whose anchor did not focus on the note's core emphasis.",
        "",
        "## Long-Span Pattern",
        "",
        md_table(
            ["book", "source id", "cases", "attentional_v2 avg quality", "iterator_v1 avg quality", "winner"],
            long_rows,
        ),
        "",
        "The long-span result points the other way: `iterator_v1` wins the current target-centered accumulation set overall, `3.083` versus `2.583`. That does not mean V2 is weaker as a reader in every sense; it suggests this first V2 shape is stronger at local selective attention than at explicitly carrying prepared long-range threads into target moments.",
        "",
        "## Scoring Basis",
        "",
        "- Excerpt scoring is strict source-span based. String or semantic similarity is not used to admit candidates; reactions must overlap the stored `segment_source_v1` note span, then non-exact overlaps are judged as `focused_hit`, `incidental_cover`, or `miss`.",
        "- Long-span scoring uses the frozen target-centered evidence bundle: target-local reactions, explicit callback actions, and short-horizon followups are judged against upstream refs and the expected integration.",
        "- Public reaction `type` values in reaction appendices are compatibility projections. For V2, the native truth is surfaced reaction content plus surfaced semantics, not the label.",
        "",
        "## Cautious Next-Move Reading",
        "",
        "Do not optimize all behavior directly toward one metric. `Selective Legibility` asks whether the reader notices high-value source spans; `Coherent Accumulation` asks whether it carries long-range threads; `Insight / Clarification` will need its own definition and evidence. Improving V2 should preserve the current reading-time reaction quality while selectively improving coverage and long-range carry.",
    ]
    write_text(out_path, "\n".join(lines))
    return out_path


def render_readme(
    segments: list[dict[str, Any]],
    excerpt_paths: dict[str, Path],
    longspan_paths: dict[str, Path],
    reaction_paths: dict[tuple[str, str], Path],
    source_text_paths: dict[str, Path],
    summary_analysis_path: Path,
    excerpt_aggregate: dict[str, Any],
    long_aggregate: dict[str, Any],
    coverage: dict[str, Any],
) -> Path:
    out_path = OUTPUT_DIR / "README.md"
    excerpt_rows = []
    for segment in segments:
        source_id = segment["source_id"]
        excerpt_rows.append(
            [
                segment.get("book_title"),
                source_id,
                rel_link(out_path, excerpt_paths[source_id], "excerpt audit"),
                rel_link(out_path, source_text_paths[segment["segment_id"]], "source text"),
                rel_link(out_path, reaction_paths[(source_id, "attentional_v2")], "V2 reactions"),
                rel_link(out_path, reaction_paths[(source_id, "iterator_v1")], "V1 reactions"),
            ]
        )
    long_rows = []
    for source_id, path in sorted(longspan_paths.items()):
        segment = next(row for row in segments if row["source_id"] == source_id)
        long_rows.append(
            [
                segment.get("book_title"),
                source_id,
                rel_link(out_path, path, "long-span audit"),
                rel_link(out_path, source_text_paths[segment["segment_id"]], "source text"),
                rel_link(out_path, reaction_paths[(source_id, "attentional_v2")], "V2 reactions"),
                rel_link(out_path, reaction_paths[(source_id, "iterator_v1")], "V1 reactions"),
            ]
        )
    excerpt_mechs = excerpt_aggregate.get("mechanisms", {})
    long_mechs = long_aggregate.get("mechanisms", {})
    lines = [
        "# Full Active Benchmark Audit — 2026-04-21",
        "",
        "This directory is a generated human-review bundle for the completed April 19 active rerun. It does not rerun reading or judging; it only renders existing stored evidence.",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Parent run: `{PARENT_RUN.name}`",
        f"- Excerpt run: `{EXCERPT_RUN.name}`",
        f"- Long-span run: `{LONGSPAN_RUN.name}`",
        f"- Summary analysis: {rel_link(out_path, summary_analysis_path)}",
        "",
        "## Coverage",
        "",
        md_table(
            ["item", "count"],
            [
                ["excerpt windows", coverage["excerpt_windows"]],
                ["excerpt unique note cases", coverage["excerpt_unique_note_cases"]],
                ["excerpt mechanism shards", coverage["excerpt_shards"]],
                ["long-span windows", coverage["longspan_windows"]],
                ["long-span target cases", coverage["longspan_cases"]],
                ["long-span mechanism shards", coverage["longspan_shards"]],
                ["normalized reactions rendered", coverage["reaction_count"]],
            ],
        ),
        "",
        "## Top-Line Scores",
        "",
        md_table(
            ["level", "attentional_v2", "iterator_v1", "metric"],
            [
                [
                    "Excerpt / Selective Legibility",
                    excerpt_mechs.get("attentional_v2", {}).get("note_recall"),
                    excerpt_mechs.get("iterator_v1", {}).get("note_recall"),
                    "note_recall",
                ],
                [
                    "Long-span / Coherent Accumulation",
                    long_mechs.get("attentional_v2", {}).get("average_quality_score"),
                    long_mechs.get("iterator_v1", {}).get("average_quality_score"),
                    "average_quality_score",
                ],
            ],
        ),
        "",
        "## Excerpt Windows",
        "",
        md_table(
            ["book", "source id", "cases + scoring", "source text", "V2 reactions", "V1 reactions"],
            excerpt_rows,
        ),
        "",
        "## Long-Span Windows",
        "",
        md_table(
            ["book", "source id", "target cases", "source text", "V2 reactions", "V1 reactions"],
            long_rows,
        ),
        "",
        "## Scoring Notes",
        "",
        "- Excerpt case docs show the human note, canonical source span, both mechanisms' labels, judge reasons, best reaction, and all source-overlap candidate reactions.",
        "- Long-span docs show the target span, upstream refs, expected integration, both mechanisms' evidence bundles, and judge reasons.",
        "- Reaction appendices show all normalized reactions rendered from stored bundles, including anchor quotes and source locators.",
    ]
    write_text(out_path, "\n".join(lines))
    return out_path


def validate_coverage(coverage: dict[str, Any], generated_paths: list[Path]) -> None:
    expected = {
        "excerpt_windows": 5,
        "excerpt_unique_note_cases": 203,
        "excerpt_shards": 10,
        "longspan_windows": 3,
        "longspan_cases": 12,
        "longspan_shards": 6,
        "reaction_count": 1906,
    }
    errors: list[str] = []
    for key, value in expected.items():
        if coverage.get(key) != value:
            errors.append(f"{key}: expected {value}, got {coverage.get(key)}")
    for path in generated_paths:
        if not path.exists():
            errors.append(f"Missing generated path: {path}")
    if errors:
        raise AssertionError("Coverage validation failed:\n" + "\n".join(errors))


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "excerpt").mkdir(parents=True)
    (OUTPUT_DIR / "longspan").mkdir(parents=True)
    (OUTPUT_DIR / "reactions").mkdir(parents=True)
    (OUTPUT_DIR / "source_texts").mkdir(parents=True)

    segments, segment_by_source = load_segments()
    excerpt_aggregate = load_json(EXCERPT_RUN / "summary" / "aggregate.json")
    long_aggregate = load_json(LONGSPAN_RUN / "summary" / "aggregate.json")
    long_cases = load_jsonl(LONGSPAN_RUN / "summary" / "case_results.jsonl")

    source_text_paths = render_source_text_docs(segments)
    reaction_paths, reaction_counts = render_reaction_docs(segments)

    excerpt_paths: dict[str, Path] = {}
    excerpt_case_total = 0
    for segment in segments:
        source_id = segment["source_id"]
        cases = load_excerpt_cases(source_id)
        path, count = render_excerpt_doc(
            segment=segment,
            cases=cases,
            excerpt_aggregate=excerpt_aggregate,
            source_text_paths=source_text_paths,
            reaction_paths=reaction_paths,
        )
        excerpt_paths[source_id] = path
        excerpt_case_total += count

    longspan_paths, longspan_case_total = render_longspan_docs(
        long_cases=long_cases,
        segment_by_source=segment_by_source,
        source_text_paths=source_text_paths,
        reaction_paths=reaction_paths,
    )
    summary_analysis_path = render_summary_analysis(
        segments=segments,
        excerpt_aggregate=excerpt_aggregate,
        long_aggregate=long_aggregate,
        long_cases=long_cases,
    )

    coverage = {
        "excerpt_windows": len(segments),
        "excerpt_unique_note_cases": excerpt_case_total,
        "excerpt_shards": len(segments) * len(MECHANISMS),
        "longspan_windows": len(longspan_paths),
        "longspan_cases": longspan_case_total,
        "longspan_shards": len(longspan_paths) * len(MECHANISMS),
        "reaction_count": sum(reaction_counts.values()),
        "reaction_counts": {
            f"{source_id}__{mechanism}": count
            for (source_id, mechanism), count in sorted(reaction_counts.items())
        },
    }

    readme_path = render_readme(
        segments=segments,
        excerpt_paths=excerpt_paths,
        longspan_paths=longspan_paths,
        reaction_paths=reaction_paths,
        source_text_paths=source_text_paths,
        summary_analysis_path=summary_analysis_path,
        excerpt_aggregate=excerpt_aggregate,
        long_aggregate=long_aggregate,
        coverage=coverage,
    )
    summary_json_path = OUTPUT_DIR / "summary.json"
    write_text(summary_json_path, json.dumps(coverage, ensure_ascii=False, indent=2))

    generated_paths = (
        [readme_path, summary_analysis_path, summary_json_path]
        + list(excerpt_paths.values())
        + list(longspan_paths.values())
        + list(reaction_paths.values())
        + list(source_text_paths.values())
    )
    validate_coverage(coverage, generated_paths)
    print(json.dumps({"output_dir": str(OUTPUT_DIR), **coverage}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
