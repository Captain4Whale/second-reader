"""Generate the compact Chinese experiment/scoring index from append-only logs."""

import argparse
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_scoring import read_lines, validate_all  # noqa: E402


def families(logs):
    by_id = {r["experiment_id"]: r for r in logs}
    if len(by_id) != len(logs):
        raise ValueError("Duplicate experiment row ID")

    def root(key, seen):
        if key in seen or key not in by_id:
            raise ValueError("Broken experiment linkage")
        row = by_id[key]
        parent = row.get("amends_experiment_id") or row.get("continuation_of")
        return root(parent, seen | {key}) if parent else key

    grouped = {}
    for key in by_id:
        grouped.setdefault(root(key, set()), []).append(by_id[key])
    return grouped


def rate(c):
    if not c["judged"]:
        return f"待标（共 {c['total']}）"
    return f"{c['passed']}/{c['judged']}（{100 * c['pass_rate']:.2f}%）" + (
        f"；未标 {c['unjudged']}" if c["unjudged"] else ""
    )


def label(p):
    return (
        "包法利"
        if "bovary" in p["run_id"]
        else "人类简史"
        if "sapiens" in p["run_id"]
        else p["group"]
    )


def metric(row, kind):
    products = {p["run_id"]: p for p in row["products"]}
    return "<br>".join(
        f"{label(products[g['run_id']])}：{rate(g['counts'][kind])}"
        for g in row["results"]
    )


def safe(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def verification_notes(logs, *, include_cases=False):
    parts = []
    for entry in logs:
        if entry.get("record_type") != "owner_verification_addendum":
            continue
        parts += [
            "",
            f"**所有者补充核对 · {entry['date']}**（`{entry['experiment_id']}`）",
            "",
            entry["conclusion"],
        ]
        if include_cases:
            parts += [""] + [
                f"- {case['book']} `{case['unit_id']}`：{case['finding']}"
                for case in entry.get("results", {}).get("cases", [])
            ]
    return parts


def details(row, logs):
    sid = row["scoring_id"]
    ruler = row["rubric"]
    parts = [
        f'<a id="{sid.lower()}"></a>',
        "<details>",
        f"<summary>{row['title']} · {sid}</summary>",
        "",
        f"- 实验：`{row['experiment_id']}`；范围：{row['unit_set']['count']} 单元，[{Path(row['unit_set']['path']).name}]({row['unit_set']['path'].removeprefix('experiments/')})，SHA-256 `{row['unit_set']['sha256']}`。",
        f"- 评分者：{row['scorer']['kind']} / {row['scorer']['id']}；尺子：{ruler['version']}，表单：{ruler['form_version'] or '无'}。",
        f"- rubric SHA-256：`{ruler['sha256']}`；表单 SHA-256：`{ruler['form_sha256']}`。",
        f"- 登记：{row['registered_at']}；评分快照状态：{row['status']}；会话：`{row['review_session_id']}`。",
        f"- 盲化：{row['blinding'].get('notes', '')}",
        "",
    ]
    if row["inputs"]["kind"] == "adjudicated_conversion":
        parts += ["**结构换算依据**：" + row["calculation"]["basis"], ""]
    for p in row["products"]:
        parts += [
            f"- {label(p)}：**{p['model']} / {p['reasoning_effort']}**，run `{p['run_id']}`；产物 SHA-256 `{p['product_sha256']}`。"
        ]
        for prompt in p["prompts"]:
            parts += [
                f"  - prompt `{prompt['version']}` / `{prompt['release_sha256']}`；证据：{p['hash_evidence']}。"
            ]
        parts += [
            f"  - 实际请求哈希：{len(p.get('request_hashes') or {})} 条；"
            + (
                "历史请求哈希不可用。"
                if p.get("request_hashes") is None
                else "逐请求对应关系见评分账。"
            )
        ]
    parts += [
        "",
        "| 产物 | 类型 | 通过/已判 | 产物总数 | 不过 | 未判 |",
        "|---|---|---|---:|---:|---:|",
    ]
    products = {p["run_id"]: p for p in row["products"]}
    for g in row["results"]:
        for kind, c in g["counts"].items():
            parts += [
                f"| {label(products[g['run_id']])} | {kind} | {rate(c)} | {c['total']} | {c['failed']} | {c['unjudged']} |"
            ]
    if row["inputs"]["kind"] == "adjudicated_conversion":
        parts += ["", "换算后的干净通过率、否决项与标签（可重叠）：", ""]
        for g in row["results"]:
            n = g["counts"]["Note"]
            clean = (
                f"{n['clean_passed']}/{n['judged']}（{100 * n['clean_pass_rate']:.2f}%）"
                if n["judged"]
                else "待标"
            )
            parts += [f"- {label(products[g['run_id']])} Note 干净通过率：{clean}。"]
            for kind, c in g["counts"].items():
                fields = [
                    f"{v['label']} {v['count']}"
                    for field in ("vetoes", "tags")
                    for v in c[field].values()
                ]
                parts += [
                    f"- {label(products[g['run_id']])} {kind}："
                    + "；".join(fields)
                    + "。"
                ]
    parts += [
        "",
        "逐条款不过数：开放编码不适用；待标条目不计入条款统计。多个条款可重叠。",
    ]
    for g in row["results"]:
        for kind, c in g["counts"].items():
            if c["failed_criteria"] is not None:
                parts += [
                    f"- {label(products[g['run_id']])} {kind}："
                    + (
                        "待标"
                        if not c["judged"]
                        else "；".join(
                            f"{k} {v['label']}：{v['failed']}"
                            for k, v in c["failed_criteria"].items()
                        )
                    )
                ]
    parts += ["", "标注快照："]
    for snap in row["snapshots"]:
        parts += [
            f"- [{Path(snap['path']).name}](../{snap['path']})；截止 revision **{snap['revision']}**；SHA-256 `{snap['sha256']}`；原标注时间 {snap['judgment_time_range']}；工具版本 {', '.join(snap['annotator_versions']) or '尚无标注'}。"
        ]
    parts += ["", "可比性："]
    parts += [
        f"- `{c['scoring_id']}`：{c['mode']}；{c['limitations']}"
        for c in row["comparable_to"]
    ] or ["- 无前序评分。"]
    parts += [
        "",
        f"复算：`{row['calculation']['command']}`；代码提交 `{row['calculation']['git_commit']}`；[私有统计报告](../{row['calculation']['report']})。",
        "",
        "本实验日志合并：" + " → ".join(f"`{r['experiment_id']}`" for r in logs) + "。",
    ]
    closing = next(
        (r for r in reversed(logs) if r.get("record_type") == "experiment_closure"),
        None,
    )
    verification = verification_notes(logs, include_cases=True)
    parts += verification
    if closing and verification:
        parts += [
            "",
            "<details>",
            "<summary>原收尾记录（历史原文；后续核对见上文）</summary>",
            "",
            closing["conclusion"],
            "",
            "</details>",
        ]
    elif closing:
        parts += ["", closing["conclusion"]]
    parts += ["", "</details>", ""]
    return "\n".join(parts)


def render(root=BACKEND):
    rows = read_lines(root / "experiments/scorings.jsonl")
    latest = validate_all(rows, root)
    grouped = families(read_lines(root / "experiments/log.jsonl"))
    output = [
        "# 实验与评分总表",
        "",
        "主表每个评分范围只显示最新快照；通过率 = 通过数 / 已判数。含原文的证据仅存本机忽略目录。",
        "DIAG-001 的 Highlight 数字保留用于追溯；现有决策仍只依据 Note。",
    ]
    for logs in grouped.values():
        output += verification_notes(logs)
    output += [
        "",
        "| 评分／单元 | 产物配置 | 尺子／评分者 | Note 通过率 | Highlight 通过率 | 状态 |",
        "|---|---|---|---|---|---|",
    ]
    for r in latest.values():
        models = "<br>".join(
            dict.fromkeys(
                p["model"]
                .replace("gpt-6-luna", "GPT-6 Luna")
                .replace("gpt-6-sol", "GPT-6 Sol")
                + " / "
                + p["reasoning_effort"]
                for p in r["products"]
            )
        )
        ruler = (
            "开放编码"
            if r["rubric"]["version"] == "open_coding"
            else r["rubric"]["version"]
            + (" 结构换算" if r["inputs"]["kind"] == "adjudicated_conversion" else "")
            + "<br>"
            + (r["rubric"]["form_version"] or "无表单")
        )
        output += [
            f"| [{safe(r['title'])}](#{r['scoring_id'].lower()})<br>{r['unit_set']['count']} 单元 | {models} | {ruler}<br>{r['scorer']['id']} | {metric(r, 'Note')} | {metric(r, 'Highlight')} | "
            + {"pending": "待标", "partial": "进行中", "completed": "已完成"}[
                r["status"]
            ]
            + " |"
        ]
    output += ["", "以下小节包含哈希、标注时间、分母、可比范围及合并后的实验日志。", ""]
    for r in latest.values():
        output += [details(r, grouped[r["experiment_id"]])]
    history = [
        r for r in rows if latest[r["series_id"]]["scoring_id"] != r["scoring_id"]
    ]
    output += ["<details>", f"<summary>历史评分快照（{len(history)} 条）</summary>", ""]
    output += [details(r, grouped[r["experiment_id"]]) for r in history] or [
        "暂无被后续快照替代的评分。"
    ]
    output += [
        "",
        "</details>",
        "",
        "由 `scripts/q1_experiment_index.py` 生成，请勿手工编辑。",
        "",
    ]
    return "\n".join(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--root", type=Path, default=BACKEND)
    args = p.parse_args()
    expected = render(args.root)
    path = args.root / "experiments/INDEX.md"
    if args.check:
        if not path.exists() or path.read_text() != expected:
            raise SystemExit("INDEX differs from logs; regenerate it")
        print("INDEX matches logs")
    else:
        path.write_text(expected)
