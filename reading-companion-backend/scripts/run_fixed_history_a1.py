#!/usr/bin/env python3
"""Freeze/verify the registered 16-unit A1 diagnostic, then run A1 only."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from eval.attentional_v2.fixed_history_digest import HistoricalRun, read, render_packet, run_digest, sha, write
from src.prompts.integrity import canonical
from src.reading_runtime.llm_usage import normalize_provider_usage
from src.attentional_v2.source_spans import source_ref_from_unit
from src.reading_core.source_ranges import source_range_from_wire, validate_book_document_source_range
from eval.attentional_v2.fixed_history_digest import wire_span

EXPERIMENT = "Q1-DIGEST-DIAG-001"


def selected_units():
    trial = next(x for x in map(json.loads, (BACKEND / "experiments/log.jsonl").read_text().splitlines())
                 if x["experiment_id"] == EXPERIMENT)
    return [(run_id.split("_full_", 1)[1].split("_d414030", 1)[0], run_id, uid)
            for run_id, units in trial["selected_units"].items() for uid in units]


def fingerprint(histories):
    return {book: {str(p.relative_to(h.output)): sha(p.read_bytes())
                   for p in h.output.rglob("*") if p.is_file()} for book, h in histories.items()}


def load_histories(source):
    return {book: HistoricalRun(source, rid) for book, rid in
            {b: r for b, r, _ in selected_units()}.items()}


def status(work, phase, **values):
    (work / "status.json").write_text(json.dumps({"phase": phase, "updated_at": datetime.now(timezone.utc).isoformat(),
                                              **values}, ensure_ascii=False, indent=2) + "\n")


def check_saved(history, packet, directory):
    original = read(directory / "input.json")
    history.verify_memory_selection(original)
    actual = read(directory / "rendered.json")
    system, user = render_packet(packet, packet["accepted_call"]["prompt_version"])
    if actual["system_prompt"] != system or actual["user_prompt"] != user:
        raise ValueError("Existing A1 result has different frozen input")
    result = read(directory / "result.json")
    if (result["original_run_id"], result["unit_id"], result["model"], result["sampling"], result["prompt_version"]) != (
        packet["original_run_id"], packet["unit_id"], "gpt-6-luna", packet["accepted_call"]["sampling"], packet["accepted_call"]["prompt_version"]):
        raise ValueError("Existing A1 result has different unit/model/sampling/prompt")
    return result


def validate_marks(history, packet, result):
    findings = []
    for m in result["result"]["marginalia"]:
        ref = source_ref_from_unit(packet["current_unit_source"], quote=m["source_quote"], role="reaction_anchor")
        if ref["resolution"]["status"] != "matched":
            raise ValueError(f"Non-exact/ambiguous A1 anchor: {ref['resolution']}")
        coordinates = wire_span(ref["source_span"])
        validate_book_document_source_range(history.document, source_range_from_wire(coordinates),
                                           expected_quote=m["source_quote"], require_single_resource=False)
        findings.append(coordinates)
    return findings


def prepare(source, root):
    work = root / "A1-full"
    work.mkdir(parents=True, exist_ok=False)
    try:
        histories = load_histories(source)
        checks = [h.check_manifest() for h in histories.values()]
        items = []
        for book, rid, uid in selected_units():
            packet = histories[book].reconstruct(uid)
            histories[book].verify_memory_selection(packet)
            if packet["accepted_call"]["model"] != "gpt-6-luna" or packet["accepted_call"]["sampling"]["reasoning_effort"] != "medium":
                raise ValueError("A1 no longer matches historical configuration")
            write(work / "preflight" / book / f"{uid}.json", packet)
            dest = root / "A1" / book / uid
            if dest.exists():
                check_saved(histories[book], packet, dest)
            items.append({"book": book, "original_run_id": rid, "unit_id": uid,
                          "memory_check": packet["memory_selection_check"], "reuse": dest.exists()})
        write(work / "source-files-before.json", fingerprint(histories))
        write(work / "preflight.json", {"schema": "fixed-history-a1-preflight/1", "manifest_checks": checks,
              "units": items, "example_units_fixed_before_generation": {"bovary": "u000006", "sapiens": "u000015"}})
        status(work, "preflight_passed", units=len(items))
        return work
    except Exception as exc:
        status(work, "stopped", error_type=type(exc).__name__, error=str(exc))
        raise


def mark_statistics(marks):
    counts = Counter(m["kind"] for m in marks)
    bodies = [m["content"].strip() for m in marks if m["kind"] == "note"]
    lengths = [len(t) for t in bodies]
    return {"total": len(marks), "H": counts["highlight"], "N": counts["note"],
            "note_characters": sum(lengths), "mean_note_length": sum(lengths) / len(lengths) if lengths else None,
            "note_sentences": sum(len(re.findall(r"[。！？!?]", t)) for t in bodies),
            "question_marks": sum(t.count("？") + t.count("?") for t in bodies)}


def report(root):
    work = root / "A1-full"
    table, usages, examples = [], [], {}
    for book, rid, uid in selected_units():
        packet = read(work / "preflight" / book / f"{uid}.json")
        directory = root / "A1" / book / uid
        result = read(directory / "result.json")
        original_marks = packet["historical_result"]["marginalia"]
        a1_marks = result["result"]["marginalia"]
        table.append({"book": book, "unit_id": uid, "original": mark_statistics(original_marks),
                      "A1": mark_statistics(a1_marks), "memory_check": packet["memory_selection_check"]})
        for p in sorted((directory / "actual").glob("response-*.json")):
            usage = normalize_provider_usage(read(p)).to_dict()
            if usage["status"] != "complete":
                raise ValueError(f"Incomplete observed response usage: {p}")
            usages.append(usage)
        if (book, uid) in (("bovary", "u000006"), ("sapiens", "u000015")):
            examples[book] = {"unit_id": uid, "original": original_marks, "A1": a1_marks}
    totals = {}
    for group in ("original", "A1"):
        total = {key: sum(x[group][key] for x in table) for key in ("total", "H", "N", "note_characters", "note_sentences", "question_marks")}
        total["mean_note_length"] = total["note_characters"] / total["N"] if total["N"] else None
        totals[group] = total
    usage = {k: sum(u[k] or 0 for u in usages) for k in ("input_tokens", "output_tokens", "total_tokens", "cache_read_input_tokens", "reasoning_tokens")}
    summary = {"schema": "fixed-history-a1-summary/1", "experiment_id": EXPERIMENT, "reconstructed": True,
               "units": table, "totals": totals, "usage": usage, "successful_provider_responses": len(usages),
               "actual_billed_cost": None, "examples": examples,
               "note_length_definition": "Unicode code points of stripped Note body, including punctuation; excludes anchor/Highlight/selection_reason; no Note => null",
               "quality_conclusion": None, "next": "Wait for owner confirmation before A2/B"}
    write(work / "summary.json", summary)
    render_report(summary, work / "report.md")
    return summary


def render_report(summary, path):
    table, totals, usage, examples = (summary[k] for k in ("units", "totals", "usage", "examples"))
    fmt = lambda value: "—" if value is None else f"{value:.1f}"
    lines = ["# 固定历史上下文 A1 与原运行对照", "", f"{len(table)} 个指定单元；复用已确认的 u000006 A1，只新增 15 次单元生成。未运行 A2/B，无质量评价。", "",
             "Note 平均长度：正文去除首尾空白后的 Unicode 字符数，含标点，不含锚点原文、Highlight 或 selection_reason；无 Note 用 —。", "",
             "| 书 | unit_id | 原条数（H:N） | A1 条数（H:N） | 原 Note 均长 | A1 Note 均长 |",
             "|---|---|---:|---:|---:|---:|"]
    for row in table:
        old, new = row["original"], row["A1"]
        lines.append(f"| {'包法利' if row['book']=='bovary' else '人类简史'} | {row['unit_id']} | {old['total']}（{old['H']}:{old['N']}） | {new['total']}（{new['H']}:{new['N']}） | {fmt(old['mean_note_length'])} | {fmt(new['mean_note_length'])} |")
    old, new = totals["original"], totals["A1"]
    lines += [f"| 合计 | {len(table)} 单元 | {old['total']}（{old['H']}:{old['N']}） | {new['total']}（{new['H']}:{new['N']}） | {fmt(old['mean_note_length'])} | {fmt(new['mean_note_length'])} |", "",
              "汇总均长按全部 Note 正文总字符数除以 Note 条数计算，没有平均各单元的均长。", "",
              f"A1 用量（含已复用的试跑）：输入 {usage['input_tokens']:,}、输出 {usage['output_tokens']:,}，合计 {usage['total_tokens']:,} token。实际账单费用未知。", "",
              "16/16 单元的记忆 ID、hot/retrieved 各自顺序、合并后的顺序和完整正文均与原 trace/audit 对照通过。",
              "正文未检出 Chapter N／第…章/节/卷/部/篇等显式章节标签；任何标签都随整行文本逐字保留。",
              "原运行批注已与哈希验证的不可变 Reading Product 核对；全部原运行产物前后哈希一致。", "",
              "## 正文并排（生成前固定：两书各第一个指定单元）", "", "按输出顺序展示全部批注；两侧序号不表示语义配对。H 展示原文；N 展示锚点和完整正文。"]
    def cell(mark):
        if mark is None:
            return "—"
        body = ("H：" if mark["kind"] == "highlight" else "N：") + mark["source_quote"]
        if mark["kind"] == "note":
            body += "<br>" + mark["content"]
        return body.replace("|", "\\|").replace("\n", "<br>")
    for book, example in examples.items():
        lines += ["", f"### {'包法利夫人' if book=='bovary' else '人类简史'} {example['unit_id']}", "", "| 原运行 | A1 |", "|---|---|"]
        for i in range(max(len(example["original"]), len(example["A1"]))):
            old = example["original"][i] if i < len(example["original"]) else None
            new = example["A1"][i] if i < len(example["A1"]) else None
            lines.append(f"| {cell(old)} | {cell(new)} |")
    lines += ["", "## 句式表面特征（标点计数，不评质量）", "", "| 书 / 单元 | Note 句末标点数 原→A1 | 问号数 原→A1 |", "|---|---:|---:|"]
    for r in table:
        lines.append(f"| {r['book']} / {r['unit_id']} | {r['original']['note_sentences']}→{r['A1']['note_sentences']} | {r['original']['question_marks']}→{r['A1']['question_marks']} |")
    Path(path).write_text("\n".join(lines) + "\n")


def execute(source, root):
    work = root / "A1-full"
    histories = load_histories(source)
    try:
        if fingerprint(histories) != read(work / "source-files-before.json"):
            raise ValueError("Original artifacts changed since A1 preflight")
        for index, (book, rid, uid) in enumerate(selected_units(), 1):
            packet = read(work / "preflight" / book / f"{uid}.json")
            check = histories[book].verify_memory_selection(packet)
            if check != packet["memory_selection_check"]:
                raise ValueError("Frozen memory check changed")
            status(work, "running", book=book, unit_id=uid, index=index)
            dest = root / "A1" / book / uid
            if dest.exists():
                result = check_saved(histories[book], packet, dest)
                reused = True
            else:
                result = run_digest(packet, dest, model="gpt-6-luna", effort="medium",
                                    prompt_version=packet["accepted_call"]["prompt_version"], operator_backend=source)
                reused = False
            anchors = validate_marks(histories[book], packet, result)
            write(work / "verification" / book / f"{uid}.json", {"memory": check, "anchors": anchors, "reused": reused})
            print(f"{index}/16 {book}/{uid} {'reused' if reused else 'generated'} marks={len(anchors)}", flush=True)
        after = fingerprint(histories)
        if after != read(work / "source-files-before.json"):
            raise ValueError("Original artifacts changed during A1")
        write(work / "source-files-after.json", after)
        summary = report(root)
        status(work, "review_pending", units=16, usage=summary["usage"], totals=summary["totals"])
    except Exception as exc:
        status(work, "stopped", error_type=type(exc).__name__, error=str(exc))
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-backend", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--execute", action="store_true", help="requires completed preflight; A1 only, fail-stop")
    a = p.parse_args()
    root = a.output_root.resolve()
    if not root.is_relative_to((BACKEND / "state").resolve()):
        p.error("Output must be in this checkout's ignored backend/state")
    if a.execute:
        execute(a.source_backend, root)
    else:
        prepare(a.source_backend, root)


if __name__ == "__main__":
    main()
