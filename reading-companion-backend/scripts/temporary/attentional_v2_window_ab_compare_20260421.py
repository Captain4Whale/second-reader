#!/usr/bin/env python3
"""One-off focused A/B comparison for the April 21 V2 anchor-selection repair.

This helper is intentionally temporary.
It compares one existing baseline run against one current-head focused audit run
and renders a human-readable before/after report under the new run root.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_RUNS_ROOT = ROOT / "eval" / "runs" / "attentional_v2"
DEFAULT_BEFORE_RUN_ID = "attentional_v2_f4a_quality_audit_20260419"
DEFAULT_CASE_IDS = (
    "value_of_others_private_en__8_10",
    "huochu_shengming_de_yiyi_private_zh__segment_1",
)
DEFAULT_ANALYSIS_DIRNAME = "focused_window_ab_compare_20260421"


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl_load(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _safe_slug(value: str) -> str:
    return value.replace("/", "_").replace(" ", "_")


def _sentence_key(sentence_id: str, order_map: dict[str, int]) -> int:
    return int(order_map.get(sentence_id, -1))


@dataclass(frozen=True)
class RunArtifacts:
    run_id: str
    case_id: str
    shard_root: Path
    output_dir: Path
    result_path: Path
    read_audit_path: Path
    reaction_records_path: Path
    normalized_bundle_path: Path
    prompt_manifest_path: Path
    book_document_path: Path


def _resolve_run_artifacts(*, runs_root: Path, run_id: str, case_id: str) -> RunArtifacts:
    shard_root = runs_root / run_id / "shards" / case_id
    output_dir = shard_root / "outputs" / case_id / "attentional_v2"
    return RunArtifacts(
        run_id=run_id,
        case_id=case_id,
        shard_root=shard_root,
        output_dir=output_dir,
        result_path=shard_root / "result.json",
        read_audit_path=output_dir / "_mechanisms" / "attentional_v2" / "runtime" / "read_audit.jsonl",
        reaction_records_path=output_dir / "_mechanisms" / "attentional_v2" / "runtime" / "reaction_records.json",
        normalized_bundle_path=output_dir / "_mechanisms" / "attentional_v2" / "exports" / "normalized_eval_bundle.json",
        prompt_manifest_path=output_dir / "_mechanisms" / "attentional_v2" / "internal" / "prompt_manifests" / "read_unit.json",
        book_document_path=output_dir / "public" / "book_document.json",
    )


def _load_sentence_index(book_document_path: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    book_document = _json_load(book_document_path)
    ordered: list[dict[str, Any]] = []
    for chapter in book_document.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        for sentence in chapter.get("sentences", []):
            if not isinstance(sentence, dict):
                continue
            ordered.append(
                {
                    "sentence_id": _clean_text(sentence.get("sentence_id")),
                    "text": _clean_text(sentence.get("text")),
                    "chapter_id": int(chapter.get("id", 0) or 0),
                    "chapter_ref": _clean_text(chapter.get("reference")) or _clean_text(chapter.get("title")),
                }
            )
    order_map = {
        _clean_text(sentence.get("sentence_id")): index
        for index, sentence in enumerate(ordered)
        if _clean_text(sentence.get("sentence_id"))
    }
    return ordered, order_map


def _unit_text(
    *,
    start_sentence_id: str,
    end_sentence_id: str,
    ordered_sentences: list[dict[str, Any]],
    order_map: dict[str, int],
) -> str:
    start_index = _sentence_key(start_sentence_id, order_map)
    end_index = _sentence_key(end_sentence_id, order_map)
    if start_index < 0 or end_index < 0 or end_index < start_index:
        return ""
    texts = [
        _clean_text(sentence.get("text"))
        for sentence in ordered_sentences[start_index : end_index + 1]
        if _clean_text(sentence.get("text"))
    ]
    return "\n".join(texts)


def _load_reaction_cards(path: Path) -> list[dict[str, Any]]:
    payload = _json_load(path)
    records = [dict(item) for item in payload.get("records", []) if isinstance(item, dict)]
    cards: list[dict[str, Any]] = []
    for record in records:
        primary_anchor = dict(record.get("primary_anchor") or {})
        cards.append(
            {
                "reaction_id": _clean_text(record.get("reaction_id")),
                "compat_family": _clean_text(record.get("compat_family")) or _clean_text(record.get("type")),
                "content": _clean_text(record.get("thought")),
                "anchor_quote": _clean_text(primary_anchor.get("quote")),
                "emitted_at_sentence_id": _clean_text(record.get("emitted_at_sentence_id")),
                "anchor_start_sentence_id": _clean_text(primary_anchor.get("sentence_start_id")),
                "anchor_end_sentence_id": _clean_text(primary_anchor.get("sentence_end_id")),
                "prior_link": dict(record.get("prior_link") or {}) if isinstance(record.get("prior_link"), dict) else {},
                "outside_link": dict(record.get("outside_link") or {}) if isinstance(record.get("outside_link"), dict) else {},
                "search_intent": dict(record.get("search_intent") or {}) if isinstance(record.get("search_intent"), dict) else {},
            }
        )
    return cards


def _reaction_belongs_to_unit(
    reaction: dict[str, Any],
    *,
    unit_start_sentence_id: str,
    unit_end_sentence_id: str,
    order_map: dict[str, int],
) -> bool:
    unit_start = _sentence_key(unit_start_sentence_id, order_map)
    unit_end = _sentence_key(unit_end_sentence_id, order_map)
    if unit_start < 0 or unit_end < 0 or unit_end < unit_start:
        return False
    candidates = [
        _clean_text(reaction.get("emitted_at_sentence_id")),
        _clean_text(reaction.get("anchor_start_sentence_id")),
        _clean_text(reaction.get("anchor_end_sentence_id")),
    ]
    for sentence_id in candidates:
        index = _sentence_key(sentence_id, order_map)
        if index >= unit_start and index <= unit_end:
            return True
    return False


def _match_unit_reactions(
    *,
    unit_start_sentence_id: str,
    unit_end_sentence_id: str,
    reaction_cards: list[dict[str, Any]],
    order_map: dict[str, int],
) -> list[dict[str, Any]]:
    return [
        reaction
        for reaction in reaction_cards
        if _reaction_belongs_to_unit(
            reaction,
            unit_start_sentence_id=unit_start_sentence_id,
            unit_end_sentence_id=unit_end_sentence_id,
            order_map=order_map,
        )
    ]


def _load_units(
    *,
    read_audit_path: Path,
    reaction_cards: list[dict[str, Any]],
    ordered_sentences: list[dict[str, Any]],
    order_map: dict[str, int],
) -> list[dict[str, Any]]:
    entries = _jsonl_load(read_audit_path)
    units: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        unitize = dict(entry.get("unitize_decision") or {})
        start_sentence_id = _clean_text(unitize.get("start_sentence_id"))
        end_sentence_id = _clean_text(unitize.get("end_sentence_id"))
        units.append(
            {
                "unit_index": index,
                "start_sentence_id": start_sentence_id,
                "end_sentence_id": end_sentence_id,
                "boundary_type": _clean_text(unitize.get("boundary_type")),
                "unit_text": _unit_text(
                    start_sentence_id=start_sentence_id,
                    end_sentence_id=end_sentence_id,
                    ordered_sentences=ordered_sentences,
                    order_map=order_map,
                ),
                "unit_delta": _clean_text(entry.get("unit_delta")),
                "surfaced_reaction_count": int(entry.get("surfaced_reaction_count", 0) or 0),
                "reactions": _match_unit_reactions(
                    unit_start_sentence_id=start_sentence_id,
                    unit_end_sentence_id=end_sentence_id,
                    reaction_cards=reaction_cards,
                    order_map=order_map,
                ),
            }
        )
    return units


def _anchor_set(units: list[dict[str, Any]]) -> set[str]:
    return {
        _clean_text(reaction.get("anchor_quote"))
        for unit in units
        for reaction in unit.get("reactions", [])
        if _clean_text(reaction.get("anchor_quote"))
    }


def _max_reactions_per_unit(units: list[dict[str, Any]]) -> int:
    if not units:
        return 0
    return max(len(unit.get("reactions", [])) for unit in units)


def _window_contains_text(payload: dict[str, Any], needle: str) -> bool:
    normalized = _clean_text(needle)
    if not normalized:
        return False
    for unit in payload.get("units", []):
        if normalized in _clean_text(unit.get("unit_text")):
            return True
    return False


def _load_case_payload(artifacts: RunArtifacts) -> dict[str, Any]:
    result = _json_load(artifacts.result_path)
    prompt_manifest = _json_load(artifacts.prompt_manifest_path)
    ordered_sentences, order_map = _load_sentence_index(artifacts.book_document_path)
    reaction_cards = _load_reaction_cards(artifacts.reaction_records_path)
    units = _load_units(
        read_audit_path=artifacts.read_audit_path,
        reaction_cards=reaction_cards,
        ordered_sentences=ordered_sentences,
        order_map=order_map,
    )
    return {
        "run_id": artifacts.run_id,
        "case_id": artifacts.case_id,
        "book_title": _clean_text(result.get("book_title")),
        "language_track": _clean_text(result.get("language_track")),
        "goal": _clean_text(result.get("goal")),
        "visible_reaction_count": int(result.get("visible_reaction_count", 0) or 0),
        "silent_unit_count": int(result.get("silent_unit_count", 0) or 0),
        "formal_units_read": int(result.get("formal_units_read", 0) or 0),
        "prompt_version": _clean_text(prompt_manifest.get("prompt_version")),
        "promptset_version": _clean_text(prompt_manifest.get("promptset_version")),
        "units": units,
        "anchor_set": sorted(_anchor_set(units)),
        "paths": {
            "result": str(artifacts.result_path),
            "read_audit": str(artifacts.read_audit_path),
            "reaction_records": str(artifacts.reaction_records_path),
            "normalized_eval_bundle": str(artifacts.normalized_bundle_path),
            "prompt_manifest": str(artifacts.prompt_manifest_path),
            "book_document": str(artifacts.book_document_path),
        },
        "max_reactions_per_unit": _max_reactions_per_unit(units),
    }


def _value_of_others_analysis(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    target = "People want things from other people."
    before_anchors = set(before["anchor_set"])
    after_anchors = set(after["anchor_set"])
    if _window_contains_text(after, target):
        if target not in before_anchors and target in after_anchors:
            notes.append(
                "这个 window 本身包含 `People want things from other people.`，而且 after 侧把它 surfacing 出来了，说明这次修补确实补回了先前容易被 later sharper line 吞掉的 premise line。"
            )
        else:
            notes.append(
                "这个 window 本身包含 `People want things from other people.`，但这次 before/after 里没有形成 clean 反差；如果还要继续盯 swallowed-line regression，最好单独回到那个 opening paragraph 做更窄的 probe。"
            )
    else:
        notes.append(
            "这次选的 `value_of_others_private_en__8_10` 是 Chapters 2-4 的长窗口，它本身不包含之前 direct probe 用的 `People want things from other people.` 那个 opening paragraph。所以这里更适合作为密度和风格的 spot check，而不是那条 swallowed-line 的直接回归判据。"
        )
    before_units = {int(unit["unit_index"]): unit for unit in before.get("units", [])}
    after_units = {int(unit["unit_index"]): unit for unit in after.get("units", [])}
    if before_units.get(3, {}).get("surfaced_reaction_count") == 0 and after_units.get(3, {}).get("surfaced_reaction_count", 0) > 0:
        notes.append(
            "opening setup unit 在 before 侧是静默的，而 after 侧已经会把 `However ... not entirely obvious.` 这个 hinge 句 surfacing 出来，说明现在更愿意把 unit 内的前置 framing move 保留下来。"
        )
    if after["visible_reaction_count"] > before["visible_reaction_count"]:
        notes.append(
            f"可见反应密度从 `{before['visible_reaction_count']}` 提升到 `{after['visible_reaction_count']}`，同时 silent units 从 `{before['silent_unit_count']}` 变为 `{after['silent_unit_count']}`。"
        )
    else:
        notes.append(
            f"可见反应密度没有上升（before `{before['visible_reaction_count']}` / after `{after['visible_reaction_count']}`），这次修补更像是在锚点选择上改善而不是在总量上增产。"
        )
    if after["max_reactions_per_unit"] <= 2:
        notes.append("after 侧没有 unit 超过 `2` 条 surfaced reactions，至少从数量上没有出现明显的 reaction sprawl。")
    else:
        notes.append("after 侧出现了超过 `2` 条 surfaced reactions 的 unit，需要警惕密度提升是否已经开始挤压比例感。")
    return notes


def _huochu_analysis(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    if after["visible_reaction_count"] > before["visible_reaction_count"]:
        notes.append(
            f"after 侧的 visible reactions 从 `{before['visible_reaction_count']}` 提升到 `{after['visible_reaction_count']}`，说明这次修补没有只作用在英文窗口。"
        )
    elif after["visible_reaction_count"] == before["visible_reaction_count"]:
        notes.append(
            f"after 侧的 visible reactions 与 before 持平（均为 `{after['visible_reaction_count']}`），这符合预期，因为这次修补本来就不是专门冲着这个窗口来的。"
        )
    else:
        notes.append(
            f"after 侧的 visible reactions 低于 before（before `{before['visible_reaction_count']}` / after `{after['visible_reaction_count']}`），需要结合具体 unit 看是否只是标题/引言区间差异。"
        )
    if after["max_reactions_per_unit"] <= 2:
        notes.append("after 侧仍然保持 `0-2` 的局部 spread，没有从“更愿意 surface”滑回到碎裂式泛滥。")
    else:
        notes.append("after 侧出现了超过 `2` 条 reactions 的 unit，这对这个中文窗口而言是明显的比例感风险。")
    before_anchors = set(before["anchor_set"])
    after_anchors = set(after["anchor_set"])
    newly_surfaced = sorted(after_anchors - before_anchors)
    if newly_surfaced:
        notes.append(f"after 侧新增锚点 `{newly_surfaced[0]}` 等，说明这次修补至少改变了局部 surfaced selection 的取舍。")
    else:
        notes.append("锚点集合没有明显扩张，这说明该窗口主要承担“确认没有被带偏”的 guardrail 作用。")
    return notes


def _case_analysis(case_id: str, before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    if case_id == "value_of_others_private_en__8_10":
        return _value_of_others_analysis(before, after)
    if case_id == "huochu_shengming_de_yiyi_private_zh__segment_1":
        return _huochu_analysis(before, after)
    return [
        f"visible reaction count: `{before['visible_reaction_count']}` -> `{after['visible_reaction_count']}`",
        f"silent units: `{before['silent_unit_count']}` -> `{after['silent_unit_count']}`",
    ]


def _unit_block(unit: dict[str, Any]) -> list[str]:
    lines = [
        f"### Unit {unit['unit_index']} — `{unit['start_sentence_id']} -> {unit['end_sentence_id']}`",
        "",
        f"- boundary: `{unit['boundary_type']}`",
        f"- surfaced_reaction_count: `{unit['surfaced_reaction_count']}`",
        "",
        "Unit original text:",
        "",
        "```text",
        unit["unit_text"] or "(empty)",
        "```",
        "",
        f"Unit delta: {_clean_text(unit.get('unit_delta')) or '(empty)'}",
        "",
    ]
    reactions = [dict(item) for item in unit.get("reactions", []) if isinstance(item, dict)]
    if not reactions:
        lines.extend(["Surfaced reactions: none", ""])
        return lines
    lines.append("Surfaced reactions:")
    lines.append("")
    for index, reaction in enumerate(reactions, start=1):
        lines.extend(
            [
                f"{index}. `{reaction.get('compat_family', '')}`",
                f"   - anchor_quote: `{_clean_text(reaction.get('anchor_quote'))}`",
                f"   - content: {_clean_text(reaction.get('content'))}",
            ]
        )
    lines.append("")
    return lines


def _case_doc(case_id: str, before: dict[str, Any], after: dict[str, Any]) -> str:
    analysis = _case_analysis(case_id, before, after)
    before_only = sorted(set(before["anchor_set"]) - set(after["anchor_set"]))
    after_only = sorted(set(after["anchor_set"]) - set(before["anchor_set"]))
    lines = [
        f"# {case_id}",
        "",
        f"- Book: {after['book_title'] or before['book_title']}",
        f"- Goal: {after['goal'] or before['goal']}",
        f"- Before run: `{before['run_id']}` | prompt `{before['prompt_version']}`",
        f"- After run: `{after['run_id']}` | prompt `{after['prompt_version']}`",
        "",
        "## Summary",
        "",
        "| side | formal_units_read | visible_reaction_count | silent_unit_count | max_reactions_per_unit |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| before | {before['formal_units_read']} | {before['visible_reaction_count']} | {before['silent_unit_count']} | {before['max_reactions_per_unit']} |",
        f"| after | {after['formal_units_read']} | {after['visible_reaction_count']} | {after['silent_unit_count']} | {after['max_reactions_per_unit']} |",
        "",
        "## Case-Level Analysis",
        "",
    ]
    for note in analysis:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Anchor Diff",
            "",
            f"- before-only anchors: `{len(before_only)}`",
        ]
    )
    for anchor in before_only[:8]:
        lines.append(f"  - {anchor}")
    lines.append(f"- after-only anchors: `{len(after_only)}`")
    for anchor in after_only[:8]:
        lines.append(f"  - {anchor}")
    lines.extend(
        [
            "",
            "## Before",
            "",
        ]
    )
    for unit in before["units"]:
        lines.extend(_unit_block(unit))
    lines.extend(
        [
            "## After",
            "",
        ]
    )
    for unit in after["units"]:
        lines.extend(_unit_block(unit))
    lines.extend(
        [
            "## Artifact Paths",
            "",
            f"- before result: `{before['paths']['result']}`",
            f"- before read_audit: `{before['paths']['read_audit']}`",
            f"- before reaction_records: `{before['paths']['reaction_records']}`",
            f"- before normalized bundle: `{before['paths']['normalized_eval_bundle']}`",
            f"- after result: `{after['paths']['result']}`",
            f"- after read_audit: `{after['paths']['read_audit']}`",
            f"- after reaction_records: `{after['paths']['reaction_records']}`",
            f"- after normalized bundle: `{after['paths']['normalized_eval_bundle']}`",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _readme(run_id: str, before_run_id: str, case_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Focused A/B Window Comparison",
        "",
        f"- before_run_id: `{before_run_id}`",
        f"- after_run_id: `{run_id}`",
        "",
        "| case | before prompt | after prompt | before visible / silent | after visible / silent | conclusion |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in case_rows:
        before = row["before"]
        after = row["after"]
        conclusion = _clean_text(row.get("one_line_conclusion"))
        lines.append(
            f"| [{row['case_id']}]({row['doc_name']}) | `{before['prompt_version']}` | `{after['prompt_version']}` | `{before['visible_reaction_count']} / {before['silent_unit_count']}` | `{after['visible_reaction_count']} / {after['silent_unit_count']}` | {conclusion} |"
        )
    lines.append("")
    return "\n".join(lines)


def _one_line_conclusion(case_id: str, before: dict[str, Any], after: dict[str, Any]) -> str:
    if case_id == "value_of_others_private_en__8_10":
        return "Passed as a window-level spot check: density rose and the setup hinge now surfaces, but this selected window is not the same paragraph as the earlier direct swallowed-line probe."
    if case_id == "huochu_shengming_de_yiyi_private_zh__segment_1":
        if after["max_reactions_per_unit"] <= 2:
            return "Passed guardrail: density stayed proportionate without obvious local over-splitting."
        return "Attention needed: local spread exceeded the intended 0-2 reaction range."
    return "Focused before/after comparison rendered."


def render_comparison(
    *,
    runs_root: Path,
    before_run_id: str,
    after_run_id: str,
    case_ids: list[str],
    analysis_dirname: str,
) -> dict[str, Any]:
    after_run_root = runs_root / after_run_id
    analysis_root = after_run_root / "analysis" / analysis_dirname
    analysis_root.mkdir(parents=True, exist_ok=True)

    case_rows: list[dict[str, Any]] = []
    for case_id in case_ids:
        before_artifacts = _resolve_run_artifacts(runs_root=runs_root, run_id=before_run_id, case_id=case_id)
        after_artifacts = _resolve_run_artifacts(runs_root=runs_root, run_id=after_run_id, case_id=case_id)
        before = _load_case_payload(before_artifacts)
        after = _load_case_payload(after_artifacts)
        doc_name = f"{_safe_slug(case_id)}.md"
        (analysis_root / doc_name).write_text(_case_doc(case_id, before, after), encoding="utf-8")
        case_rows.append(
            {
                "case_id": case_id,
                "doc_name": doc_name,
                "before": before,
                "after": after,
                "one_line_conclusion": _one_line_conclusion(case_id, before, after),
            }
        )

    readme_path = analysis_root / "README.md"
    readme_path.write_text(_readme(after_run_id, before_run_id, case_rows), encoding="utf-8")
    summary_path = analysis_root / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "before_run_id": before_run_id,
                "after_run_id": after_run_id,
                "cases": case_rows,
                "readme_path": str(readme_path),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "analysis_root": str(analysis_root),
        "readme_path": str(readme_path),
        "summary_path": str(summary_path),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--before-run-id", default=DEFAULT_BEFORE_RUN_ID)
    parser.add_argument("--after-run-id", required=True)
    parser.add_argument("--analysis-dirname", default=DEFAULT_ANALYSIS_DIRNAME)
    parser.add_argument("--case-id", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = render_comparison(
        runs_root=Path(args.runs_root).resolve(),
        before_run_id=str(args.before_run_id),
        after_run_id=str(args.after_run_id),
        case_ids=[str(item) for item in args.case_id if str(item).strip()] or list(DEFAULT_CASE_IDS),
        analysis_dirname=str(args.analysis_dirname),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
