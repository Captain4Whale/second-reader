#!/usr/bin/env python3
"""Render a source-map version of the Memory Quality probe audit.

This is a one-off analysis renderer. It does not score, judge, or read books.
It reorganizes the existing Memory Quality audit so each window has one full
source document with probe markers, instead of repeating source-so-far slices
inside every probe section.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RUN_ROOT = Path(
    "reading-companion-backend/eval/runs/attentional_v2/"
    "attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425"
)
OLD_AUDIT = RUN_ROOT / "analysis/memory_quality_probe_audit_20260502"
NEW_AUDIT = RUN_ROOT / "analysis/memory_quality_probe_audit_20260503_source_map"
RESULTS_PATH = RUN_ROOT / "summary/memory_quality_results.jsonl"

MEMORY_QUALITY_PROBE_REVIEW_FOCUS: dict[tuple[str, int], dict[str, str]] = {
    (
        "huochu_shengming_de_yiyi_private_zh__segment_1",
        1,
    ): {
        "focus_id": "huochu_probe1_prisoner_response_three_stages",
        "title": "囚徒精神反应三阶段",
        "source_signal": (
            "source-so-far 明确引入囚徒对集中营生活的精神反应三阶段："
            "收容阶段、适应阶段、释放与解放阶段，并开始讲第一阶段。"
        ),
        "audit_question": (
            "snapshot 是否保留了作者正在用三阶段框架组织集中营心理反应这一点，"
            "即使没有逐字复述？"
        ),
        "scoring_guidance": (
            "这是重要的 source-given structural signal。它不是 exact-match gold answer，"
            "但如果完全缺席，应影响 salience / organization 的人工复核判断。"
        ),
    }
}


@dataclass(frozen=True)
class Probe:
    segment_id: str
    source_id: str
    book_title: str
    probe_index: int
    threshold_ratio: float
    target_sentence_id: str
    target_sentence_ordinal: int
    capture_sentence_id: str
    capture_sentence_ordinal: int
    coverage_sentence_count: int
    scores: dict[str, Any]
    snapshot_path: Path
    source_slice_path: Path
    source_landmark_path: Path

    @property
    def probe_slug(self) -> str:
        return f"probe-{self.probe_index}"

    @property
    def percent_label(self) -> str:
        return f"{int(round(self.threshold_ratio * 100))}%"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_fenced_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```text\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise ValueError(f"No fenced text block found in {path}")
    return match.group(1).strip()


def load_results() -> dict[tuple[str, int], dict[str, Any]]:
    results: dict[tuple[str, int], dict[str, Any]] = {}
    for line in RESULTS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        results[(row["segment_id"], int(row["probe_index"]))] = row
    return results


def load_probes() -> dict[str, list[Probe]]:
    results = load_results()
    grouped: dict[str, list[Probe]] = {}
    for snapshot_path in sorted((OLD_AUDIT / "raw_snapshots").glob("*__probe_*.json")):
        snapshot = read_json(snapshot_path)
        segment_id = snapshot_path.name.split("__probe_")[0]
        probe_index = int(snapshot["probe_index"])
        result = results[(segment_id, probe_index)]
        source_slice_path = OLD_AUDIT / "source_slices" / snapshot_path.name.replace(".json", ".md")
        source_landmark_path = OLD_AUDIT / "source_landmarks" / snapshot_path.name.replace(".json", ".md")
        probe = Probe(
            segment_id=segment_id,
            source_id=result["source_id"],
            book_title=result["book_title"],
            probe_index=probe_index,
            threshold_ratio=float(snapshot["threshold_ratio"]),
            target_sentence_id=snapshot["target_sentence_id"],
            target_sentence_ordinal=int(snapshot["target_sentence_ordinal"]),
            capture_sentence_id=snapshot["capture_sentence_id"],
            capture_sentence_ordinal=int(snapshot["capture_sentence_ordinal"]),
            coverage_sentence_count=int(snapshot["coverage"]["sentence_count"]),
            scores=result,
            snapshot_path=snapshot_path,
            source_slice_path=source_slice_path,
            source_landmark_path=source_landmark_path,
        )
        grouped.setdefault(segment_id, []).append(probe)

    for probes in grouped.values():
        probes.sort(key=lambda item: item.probe_index)
        if [probe.probe_index for probe in probes] != [1, 2, 3, 4, 5]:
            raise ValueError(f"Expected 5 probes, got {[probe.probe_index for probe in probes]}")
    return dict(sorted(grouped.items()))


def why_here(probe: Probe) -> str:
    if probe.threshold_ratio >= 0.999:
        return (
            "这是窗口终点 checkpoint；在窗口最后一个完整 read step 完成后 capture，"
            "不是按语义额外挑点。"
        )
    if probe.target_sentence_id == probe.capture_sentence_id:
        return (
            f"这是 {probe.percent_label} 进度 checkpoint；数学目标是 "
            f"{probe.target_sentence_id}，刚好由这个完整 read step 覆盖到该点。"
        )
    return (
        f"这是 {probe.percent_label} 进度 checkpoint；数学目标是 "
        f"{probe.target_sentence_id}，第一个越过该目标的完整 read step 结束在 "
        f"{probe.capture_sentence_id}，所以 capture 在这里。"
    )


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def source_link(probe: Probe) -> str:
    return f"../source_texts/{probe.segment_id}.md#{probe.probe_slug}"


def probe_review_focus(probe: Probe) -> dict[str, str] | None:
    focus = MEMORY_QUALITY_PROBE_REVIEW_FOCUS.get((probe.segment_id, probe.probe_index))
    return dict(focus) if focus else None


def snippet_around(full_source: str, position: int, before: int = 500, after: int = 260) -> str:
    start = max(0, position - before)
    end = min(len(full_source), position + after)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(full_source) else ""
    return f"{prefix}{full_source[start:end].strip()}{suffix}"


def render_source_text(segment_id: str, probes: list[Probe]) -> dict[int, str]:
    full_source = extract_fenced_text(probes[-1].source_slice_path)
    marker_positions: list[tuple[int, Probe]] = []
    snippets: dict[int, str] = {}

    for probe in probes:
        source_so_far = extract_fenced_text(probe.source_slice_path)
        if not full_source.startswith(source_so_far):
            raise ValueError(
                f"Source slice for {segment_id} probe {probe.probe_index} is not a prefix "
                "of the window-end source text."
            )
        position = len(source_so_far)
        marker_positions.append((position, probe))
        snippets[probe.probe_index] = snippet_around(full_source, position)

    out_path = NEW_AUDIT / "source_texts" / f"{segment_id}.md"
    lines: list[str] = [
        f"# Full Window Source: {probes[0].book_title}",
        "",
        f"- segment_id: `{segment_id}`",
        "- source policy: one complete source document for the window, with probe markers inserted at actual capture points.",
        "- probe selection: fixed progress checkpoints, not semantic target picking.",
        "",
        "## Probe Marker Index",
        "",
        "| Probe | Schedule | Target | Captured | Why here |",
        "| ---: | ---: | --- | --- | --- |",
    ]
    for probe in probes:
        lines.append(
            "| "
            f"[{probe.probe_index}](#{probe.probe_slug}) | "
            f"{probe.percent_label} | "
            f"`{probe.target_sentence_id}` / ordinal `{probe.target_sentence_ordinal}` | "
            f"`{probe.capture_sentence_id}` / ordinal `{probe.capture_sentence_ordinal}` | "
            f"{escape_table_cell(why_here(probe))} |"
        )
    lines.extend(["", "## Full Source With Probe Markers", ""])

    previous = 0
    for position, probe in marker_positions:
        chunk = full_source[previous:position].strip()
        if chunk:
            lines.extend(["```text", chunk, "```", ""])
        lines.extend(
            [
                f'<a id="{probe.probe_slug}"></a>',
                "",
                f"### Probe {probe.probe_index} / {probe.percent_label} — captured at `{probe.capture_sentence_id}`",
                "",
                f"- target sentence: `{probe.target_sentence_id}` / ordinal `{probe.target_sentence_ordinal}`",
                f"- captured sentence: `{probe.capture_sentence_id}` / ordinal `{probe.capture_sentence_ordinal}`",
                f"- why here: {why_here(probe)}",
                "",
            ]
        )
        previous = position

    tail = full_source[previous:].strip()
    if tail:
        lines.extend(["```text", tail, "```", ""])

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return snippets


def extract_probe_tail(old_window_text: str, probe_index: int) -> str:
    pattern = re.compile(r"^## Probe (\d+) — [^\n]+\n", re.MULTILINE)
    matches = list(pattern.finditer(old_window_text))
    current = next((match for match in matches if int(match.group(1)) == probe_index), None)
    if current is None:
        raise ValueError(f"Cannot find Probe {probe_index} in old window report")
    next_match = next((match for match in matches if match.start() > current.start()), None)
    block = old_window_text[current.start() : next_match.start() if next_match else len(old_window_text)]
    tail_start = block.find("### Memory Layers Snapshot")
    if tail_start == -1:
        tail_start = block.find("### Working State Overview")
    if tail_start == -1:
        raise ValueError(f"Cannot find reusable probe state section for probe {probe_index}")
    return block[tail_start:].rstrip()


def render_probe_source_map(probes: list[Probe]) -> str:
    lines = [
        "## Probe Source Map",
        "",
        "这些 probe 是固定进度检查点，不是语义挑点。`target` 是按窗口句数计算出的目标位置；`captured` 是第一个读完并越过该目标位置的完整 read unit 结束点。",
        "",
        "| Probe | Schedule | Target | Captured | Why captured here | Structural signal focus | Full source marker |",
        "| ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for probe in probes:
        focus = probe_review_focus(probe)
        lines.append(
            "| "
            f"{probe.probe_index} | "
            f"{probe.percent_label} | "
            f"`{probe.target_sentence_id}` / ordinal `{probe.target_sentence_ordinal}` | "
            f"`{probe.capture_sentence_id}` / ordinal `{probe.capture_sentence_ordinal}` | "
            f"{escape_table_cell(why_here(probe))} | "
            f"{escape_table_cell(focus['title']) if focus else 'none'} | "
            f"[open]({source_link(probe)}) |"
        )
    return "\n".join(lines)


def render_window(segment_id: str, probes: list[Probe], snippets: dict[int, str]) -> None:
    old_window_path = OLD_AUDIT / "windows" / f"{segment_id}.md"
    old_window_text = old_window_path.read_text(encoding="utf-8")
    first_probe = re.search(r"^## Probe 1 — ", old_window_text, re.MULTILINE)
    if not first_probe:
        raise ValueError(f"Cannot find Probe 1 heading in {old_window_path}")
    intro = old_window_text[: first_probe.start()].rstrip()

    lines: list[str] = [
        intro,
        "",
        "## Source Evidence Model",
        "",
        "本版报告不再为每个 probe 重复一份 full source-so-far。完整窗口原文只放一份，并在原文中插入 5 个 probe marker；每个 probe section 只保留短 orientation excerpt、marker 链接、raw snapshot 和 judge evidence。",
        "",
        "- full window source: "
        f"[{segment_id}.md](../source_texts/{segment_id}.md)",
        "- probe schedule: `20% / 40% / 60% / 80% / window end`",
        "- capture rule: after the first completed read step whose covered range reaches or crosses the probe threshold",
        "- semantic note: probe position is a progress checkpoint, not a claim that this exact sentence is semantically special",
        "",
        render_probe_source_map(probes),
        "",
    ]

    for probe in probes:
        result = probe.scores
        focus = probe_review_focus(probe)
        lines.extend(
            [
                f"## Probe {probe.probe_index} — {probe.percent_label}",
                "",
                f"- target sentence: `{probe.target_sentence_id}` / ordinal `{probe.target_sentence_ordinal}`",
                f"- captured sentence: `{probe.capture_sentence_id}` / ordinal `{probe.capture_sentence_ordinal}`",
                f"- coverage sentence count: `{probe.coverage_sentence_count}`",
                f"- why here: {why_here(probe)}",
                f"- full window source marker: [open]({source_link(probe)})",
                f"- source landmarks: [{probe.source_landmark_path.name}](../source_landmarks/{probe.source_landmark_path.name})",
                f"- raw snapshot JSON: [{probe.snapshot_path.name}](../raw_snapshots/{probe.snapshot_path.name})",
                f"- full runtime appendix: [runtime_dumps/{segment_id}/index.md](../runtime_dumps/{segment_id}/index.md)",
                "",
            ]
        )
        if focus:
            lines.extend(
                [
                    "### Structural Signals To Check",
                    "",
                    f"- focus: `{focus['title']}`",
                    f"- source signal: {focus['source_signal']}",
                    f"- audit question: {focus['audit_question']}",
                    f"- scoring guidance: {focus['scoring_guidance']}",
                    "",
                ]
            )
        lines.extend(
            [
                "### Scores",
                "",
                f"- salience: `{result['salience_score']}`",
                f"- mainline fidelity: `{result['mainline_fidelity_score']}`",
                f"- organization: `{result['organization_score']}`",
                f"- fidelity: `{result['fidelity_score']}`",
                f"- overall: `{float(result['overall_memory_quality_score']):.3f}`",
                "",
                "### Source Orientation Excerpt",
                "",
                "This is a short deterministic excerpt around the actual capture point. Open the full window source marker for complete context.",
                "",
                "```text",
                snippets[probe.probe_index],
                "```",
                "",
                extract_probe_tail(old_window_text, probe.probe_index),
                "",
            ]
        )

    out_path = NEW_AUDIT / "windows" / f"{segment_id}.md"
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_readme(grouped: dict[str, list[Probe]]) -> None:
    old_readme = OLD_AUDIT / "README.md"
    intro = old_readme.read_text(encoding="utf-8").split("## Full Agent Runtime State Map", 1)[0].rstrip()
    lines: list[str] = [
        "# Memory Quality Probe Evidence Audit — Source Map Edition",
        "",
        "This audit is a readability-oriented regeneration of `memory_quality_probe_audit_20260502`. It does not change scores, re-run judges, or re-read books.",
        "",
        "- Source reading run: `attentional_v2_long_span_vnext_phase1_20260423`",
        "- Scored/reported run: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`",
        "- Judge scale: `1 = poor / absent`, `3 = adequate / useful`, `5 = excellent`; higher is better.",
        "- Probe schedule: `20%`, `40%`, `60%`, `80%`, and `window end`.",
        "- Capture rule: snapshot is captured after the first completed read step crossing each threshold; probe placement is not semantic target selection.",
        "- Previous audit version: [memory_quality_probe_audit_20260502](../memory_quality_probe_audit_20260502/README.md)",
        "- Post-eval action ledger: [post_eval_action_ledger_20260503/README.md](../post_eval_action_ledger_20260503/README.md)",
        "",
        "## What Changed In This Edition",
        "",
        "- Each window now has one complete source document under `source_texts/`.",
        "- The complete source document has 5 inline probe markers.",
        "- Per-probe sections link to those markers and show only a short local source excerpt.",
        "- Existing raw snapshots, source landmarks, runtime appendices, and judge reasons remain available.",
        "",
    ]

    if "## Full Agent Runtime State Map" in old_readme.read_text(encoding="utf-8"):
        lines.append("## State Reading Guide")
        lines.append("")
        lines.append("The full state-map guide remains in each window report. Open a window report first, then use its source map to audit the probe scores.")
        lines.append("")

    lines.extend(
        [
            "## Window Summary",
            "",
            "| Book | Segment | Avg Overall | Probe Count | Window Report | Full Source | Runtime Appendix |",
            "| --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for segment_id, probes in grouped.items():
        avg = sum(float(probe.scores["overall_memory_quality_score"]) for probe in probes) / len(probes)
        title = probes[0].book_title
        lines.append(
            "| "
            f"{escape_table_cell(title)} | "
            f"`{segment_id}` | "
            f"`{avg:.3f}` | "
            f"`{len(probes)}` | "
            f"[open](windows/{segment_id}.md) | "
            f"[source](source_texts/{segment_id}.md) | "
            f"[runtime](runtime_dumps/{segment_id}/index.md) |"
        )

    lines.extend(
        [
            "",
            "## Probe Source Map Overview",
            "",
            "| Book | Probe | Schedule | Target | Captured | Full Source Marker |",
            "| --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for segment_id, probes in grouped.items():
        for probe in probes:
            lines.append(
                "| "
                f"{escape_table_cell(probe.book_title)} | "
                f"{probe.probe_index} | "
                f"{probe.percent_label} | "
                f"`{probe.target_sentence_id}` | "
                f"`{probe.capture_sentence_id}` | "
                f"[open](source_texts/{segment_id}.md#{probe.probe_slug}) |"
            )

    (NEW_AUDIT / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def copy_supporting_artifacts(grouped: dict[str, list[Probe]]) -> None:
    # Keep the new audit self-contained for lightweight audit artifacts while avoiding score changes.
    raw_dir = NEW_AUDIT / "raw_snapshots"
    landmarks_dir = NEW_AUDIT / "source_landmarks"
    for probes in grouped.values():
        for probe in probes:
            shutil.copy2(probe.snapshot_path, raw_dir / probe.snapshot_path.name)
            shutil.copy2(probe.source_landmark_path, landmarks_dir / probe.source_landmark_path.name)
    shutil.copytree(OLD_AUDIT / "runtime_dumps", NEW_AUDIT / "runtime_dumps")


def validate(grouped: dict[str, list[Probe]]) -> None:
    window_files = sorted((NEW_AUDIT / "windows").glob("*.md"))
    source_files = sorted((NEW_AUDIT / "source_texts").glob("*.md"))
    raw_files = sorted((NEW_AUDIT / "raw_snapshots").glob("*.json"))
    landmark_files = sorted((NEW_AUDIT / "source_landmarks").glob("*.md"))
    runtime_files = sorted((NEW_AUDIT / "runtime_dumps").glob("*/index.md"))
    if len(window_files) != 5:
        raise AssertionError(f"Expected 5 window docs, found {len(window_files)}")
    if len(source_files) != 5:
        raise AssertionError(f"Expected 5 source docs, found {len(source_files)}")
    if len(raw_files) != 25:
        raise AssertionError(f"Expected 25 raw snapshot copies, found {len(raw_files)}")
    if len(landmark_files) != 25:
        raise AssertionError(f"Expected 25 source landmark copies, found {len(landmark_files)}")
    if len(runtime_files) != 5:
        raise AssertionError(f"Expected 5 runtime appendices, found {len(runtime_files)}")

    for source_file in source_files:
        text = source_file.read_text(encoding="utf-8")
        marker_count = len(re.findall(r'<a id="probe-\d+"></a>', text))
        if marker_count != 5:
            raise AssertionError(f"{source_file} has {marker_count} probe markers")

    for window_file in window_files:
        text = window_file.read_text(encoding="utf-8")
        if "### Source-So-Far Preview" in text:
            raise AssertionError(f"{window_file} still contains Source-So-Far Preview")
        probe_section_count = len(re.findall(r"^## Probe \d+ — ", text, re.MULTILINE))
        if probe_section_count != 5:
            raise AssertionError(f"{window_file} does not contain exactly 5 probe sections")
        source_marker_link_count = len(re.findall(r"^- full window source marker: ", text, re.MULTILINE))
        if source_marker_link_count != 5:
            raise AssertionError(f"{window_file} does not link every probe to full source")

    expected_segments = set(grouped)
    actual_segments = {path.stem for path in source_files}
    if actual_segments != expected_segments:
        raise AssertionError(f"Source docs mismatch: {actual_segments} != {expected_segments}")


def main() -> None:
    if not OLD_AUDIT.exists():
        raise SystemExit(f"Missing old audit directory: {OLD_AUDIT}")
    if not RESULTS_PATH.exists():
        raise SystemExit(f"Missing memory quality results: {RESULTS_PATH}")

    if NEW_AUDIT.exists():
        shutil.rmtree(NEW_AUDIT)
    for subdir in ["windows", "source_texts", "raw_snapshots", "source_landmarks"]:
        (NEW_AUDIT / subdir).mkdir(parents=True, exist_ok=True)

    grouped = load_probes()
    copy_supporting_artifacts(grouped)
    for segment_id, probes in grouped.items():
        snippets = render_source_text(segment_id, probes)
        render_window(segment_id, probes, snippets)
    render_readme(grouped)
    validate(grouped)
    print(f"Rendered source-map audit to {NEW_AUDIT}")


if __name__ == "__main__":
    main()
