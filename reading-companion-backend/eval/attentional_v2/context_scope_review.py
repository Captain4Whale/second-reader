"""Source-ordered review packet with persisted anonymous annotation identifiers."""

from __future__ import annotations

import html
import json
import random
import re
from pathlib import Path

from . import run_whole_book_digest as single
from . import run_context_scope_digest as experiment


def quoted(value: object) -> str:
    text = value if isinstance(value, str) else str(value)
    return "\n".join("> " + html.escape(line) for line in text.splitlines())


def gather_items(run_dir: Path) -> list[dict]:
    full = single.read_json(run_dir / "full-source.json")
    target = single.read_json(run_dir / "target-source.json")
    items = []
    historical = single.read_json(run_dir / "historical-chapter.json")
    for unit in historical["historical_product"]["units"]:
        for mark in unit["marginalia"]:
            raw = {
                "kind": mark["kind"],
                "source_quote": mark["source_quote"],
                "content": mark.get("body_text", ""),
            }
            review = experiment.chapter_review(
                {"understanding": "历史", "response": "历史", "marginalia": [raw]},
                full,
                target,
            )["items"][0]
            # The public historical Product intentionally does not retain private
            # highlight reasons. That absence is not a reader-facing defect.
            review["validation_errors"] = [
                e
                for e in review["validation_errors"]
                if "private selection_reason" not in e
            ]
            items.append(
                {
                    **review,
                    "origin": "historical",
                    "identity": "historical:" + mark["marginalia_id"],
                }
            )
    for origin, path in [
        ("A0", experiment.BASELINE_RUN),
        *[(c, run_dir / c) for c in experiment.CONDITIONS],
    ]:
        if not (path / "parsed-result.json").exists():
            continue
        payload = single.read_json(path / "parsed-result.json")
        review = experiment.chapter_review(payload, full, target)
        for item in review["items"]:
            # Whole-book A/A0 are compared only on this chapter; unlocatable
            # quotes remain in the appendix, never presumed irrelevant.
            if origin in {"A", "A0"} and item["target_scope"] == "outside":
                continue
            items.append(
                {
                    **item,
                    "origin": origin,
                    "identity": f"{origin}:{item['original_index']}",
                }
            )
    return items


def render_packet(run_dir: Path) -> None:
    items = gather_items(run_dir)
    key_path = run_dir / "review-key.json"
    if key_path.exists():
        key = single.read_json(key_path)
        if set(key["labels"]) != {item["identity"] for item in items}:
            raise ValueError("Review inputs changed after anonymous key was frozen")
    else:
        identities = sorted(item["identity"] for item in items)
        random.SystemRandom().shuffle(identities)
        key = {
            "labels": {
                identity: f"R{i:03d}" for i, identity in enumerate(identities, 1)
            }
        }
        key["origins"] = {
            key["labels"][item["identity"]]: item["origin"] for item in items
        }
        single.write_json(key_path, key)
    items.sort(
        key=lambda item: (
            (
                item["candidates"][0]["global_start"]
                if item["candidates"]
                else float("inf")
            ),
            key["labels"][item["identity"]],
        )
    )
    single.write_json(run_dir / "review-items.json", items)
    summary = single.read_json(run_dir / "summary.json")
    lines = [
        "# 《迦摩罗》批注人工对照",
        "",
        "本页按原文位置混排历史参考与本轮结果，以匿名编号隐藏来源。已有阅读经历及文风仍可能暴露来源，这不是严格盲评。",
        "",
        "先判断每条是否值得保留，再查看条件对应关系。内容相近的条目分别保留，比较时按独立阅读价值判断，不按重复条数累加收益。",
        "",
        "[完整章节原文](target-source.md) · 条件对应关系保存在 review-key.json；运行记录在 execution-summary.md。",
        "",
        "审阅标准：忠于原文；有可保留的阅读价值；避免空泛、牵强和重复。旧批注是参考，不是要求新结果照抄的答案。",
        "",
        "本地引用校验只检查原文匹配，不判断语义质量。Highlight 的私有选择理由不混入本页，完整结果另行保留。",
        "",
    ]
    if summary["status"] != "review_pending":
        lines.extend(
            ["**本轮存在未完成条件；以下仅供诊断，不构成完整 A/B/C 比较。**", ""]
        )
    appendix_started = False
    for item in items:
        if not item["candidates"] and not appendix_started:
            lines.extend(
                [
                    "## 附录：范围或引用待核查",
                    "",
                    "以下原始条目没有在目标章内精确定位，不自动当作有效目标章批注。",
                    "",
                ]
            )
            appendix_started = True
        raw = item["raw"]
        label = key["labels"][item["identity"]]
        kind = raw.get("kind", "无效类型") if isinstance(raw, dict) else "无效类型"
        lines.extend([f"### {label} · {kind}", ""])
        for candidate in item["candidates"]:
            start, end = candidate["start"], candidate["end"]
            if start and end:
                lines.extend(
                    [
                        f"原文位置：段落 {start['paragraph_index']} → {end['paragraph_index']}",
                        "",
                    ]
                )
        if isinstance(raw, dict):
            lines.extend(["原文引用：", "", quoted(raw.get("source_quote", "")), ""])
            if raw.get("content"):
                lines.extend(["批注：", "", quoted(raw["content"]), ""])
        else:
            lines.extend([quoted(raw), ""])
        if item["validation_errors"]:
            lines.extend(["定位/格式检查：" + "；".join(item["validation_errors"]), ""])
        lines.extend(
            [
                "- [ ] 保留",
                "- [ ] 修改后保留",
                "- [ ] 不保留",
                "",
                "理由／独立阅读价值／与其他编号重复：",
                "",
            ]
        )
    lines.extend(
        [
            "## 整体审阅",
            "",
            "明确值得批注但仍缺失的内容：",
            "",
            "新增且值得保留的发现：",
            "",
            "重复、空泛或牵强的主要问题：",
            "",
        ]
    )
    (run_dir / "review.md").write_text("\n".join(lines).rstrip() + "\n")
    audit = [
        "# 三组实验运行记录（揭示条件）",
        "",
        "建议先完成 review.md 的匿名审阅，再阅读本页。",
        "",
        "| 条件 | 状态 | 原始批注 | 本章唯一定位 | 输入 tokens | 输出 tokens | 耗时（秒） |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for c in experiment.CONDITIONS:
        r = summary["conditions"].get(c, {})
        audit.append(
            f"| {c} | {r.get('status', '未调用')} | {r.get('counts', {}).get('total', '—')} | {r.get('target_counts', {}).get('uniquely_located', '—')} | {r.get('usage', {}).get('input_tokens', '—')} | {r.get('usage', {}).get('output_tokens', '—')} | {r.get('elapsed_seconds', '—')} |"
        )
    for c in experiment.CONDITIONS:
        result = summary["conditions"].get(c, {})
        if result.get("status") != "failed":
            continue
        error = result.get("error", {})
        details = [
            str(error.get("type", "unknown")),
            str(error.get("problem_code", "unknown")),
        ]
        ledger_path = run_dir / c / "llm-standard.jsonl"
        if ledger_path.exists():
            for line in ledger_path.read_text().splitlines():
                row = json.loads(line)
                # Extract only the HTTP status, never publish provider messages
                # or exception reprs that could contain private connection data.
                match = re.search(
                    r"\bError code:\s*(\d{3})\b", str(row.get("error_message", ""))
                )
                if match:
                    details.append("HTTP " + match.group(1))
        failure = f"条件 {c} 请求失败：{' / '.join(details)}。耗时 {result.get('elapsed_seconds', '未知')} 秒。"
        audit.extend(["", failure, ""])
        if not (run_dir / c / "parsed-result.json").exists():
            explanation = "未收到可解析的正常生成结果；批注数量和 usage 均未知，不能记为零。未自动重试。"
            audit.extend([explanation, ""])
            (run_dir / c / "review.md").write_text(
                f"# 条件 {c}：请求失败\n\n{failure}\n\n{explanation}\n\n"
                "请求配置和失败证据保存在 request.json、summary.json、llm-standard.jsonl。\n"
            )
    audit.extend(
        [
            "",
            "A：全书输入、全书任务，复现此前请求。B：全书背景、章节任务。C：章节输入、同一章节任务。A0 是此前整书结果。",
            "",
            "各组完整产出（包含 Understanding / Response、私有选择理由、无效和范围外条目）：",
            "",
        ]
    )
    for c in experiment.CONDITIONS:
        if (run_dir / c / "review.md").exists():
            label = (
                "完整结果"
                if summary["conditions"].get(c, {}).get("status") == "review_pending"
                else "失败记录"
            )
            audit.append(f"- [{c} {label}]({c}/review.md)")
    audit.extend(
        [
            "",
            "[历史章节参考](historical-reference.md)",
            "",
            "每组最多一次应用请求，无自动修复/重试/续写/目标切换；CPA 内部执行次数和实际账单不可观测。原始输出 tokens 包含供应商报告的 reasoning tokens，不等同于可见文本长度。",
            "",
            "选择此章是为了诊断已知遗漏；每个条件仅一次。B/C 改变额外内容、目标绝对位置和跨章证据；A/B 还改变任务范围包装。本轮不推断普遍切分收益，不改变产品默认流程，等待人工审阅。",
            "",
        ]
    )
    (run_dir / "execution-summary.md").write_text("\n".join(audit))
