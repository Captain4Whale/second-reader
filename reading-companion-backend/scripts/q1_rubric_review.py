"""Prepare isolated rubric review folders and compare human judgments, offline."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_comparison import digest, require  # noqa: E402
from scripts.q1_comparison_stats import load_bundle, validate_rows  # noqa: E402
from scripts.q1_rubric_form import load_form  # noqa: E402


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def raw_rows(raw):
    require(not raw or raw.endswith(b"\n"), "Incomplete judgment journal")
    return [json.loads(line) for line in raw.splitlines()]


def state_destination(path):
    path = Path(path).resolve()
    require(
        path.is_relative_to((BACKEND / "state").resolve()),
        "Output must be under ignored backend state/",
    )
    require(not path.exists(), "Output already exists; refusing overwrite")
    return path


def prepare(source, output, form_version="q1-v0.form.v1", annotator="weijiang"):
    source, output = Path(source).resolve(), state_destination(output)
    _, mixed, _ = load_bundle(source)
    mixed_raw = (source / "mixed.json").read_bytes()
    require(
        json.loads(mixed_raw) == mixed, "Mixed projection changed during preparation"
    )
    baseline_raw = (source / "judgments.jsonl").read_bytes()
    baseline = raw_rows(baseline_raw)
    validate_rows(baseline, mixed)
    require(
        all(
            r["schema"] == "q1-mixed-judgment/1"
            and r["annotator_id"] == annotator
            and r["rubric_version"] == "open_coding"
            and r["rubric_sha256"] is None
            for r in baseline
        ),
        "Baseline must be a single annotator open_coding journal",
    )
    form, form_hash = load_form(form_version)
    registry = json.loads((BACKEND / "rubric/form-releases.json").read_text())
    form_raw = (BACKEND / registry[form_version]["path"]).read_bytes()
    context = dict(
        batch_id=mixed["batch_id"],
        annotator_id=annotator,
        rubric_version=form["rubric_version"],
        rubric_sha256=form["rubric_sha256"],
        rubric_status="published",
        rubric_form_version=form_version,
        rubric_form_sha256=form_hash,
        review_session_id=str(uuid4()),
        baseline_sha256=sha256(baseline_raw).hexdigest(),
        mixed_sha256=sha256(mixed_raw).hexdigest(),
    )
    files = {
        "mixed.json": mixed_raw,
        "rubric-form.json": form_raw,
        "open_coding.snapshot.jsonl": baseline_raw,
        "annotation-context.json": encode(context),
        "judgments.jsonl": b"",
    }
    # No original file is ever opened for writing; all outputs are exclusively new.
    output.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        with (output / name).open("xb") as stream:
            stream.write(data)
    with (output / "preparation.json").open("xb") as stream:
        stream.write(
            encode(
                dict(
                    schema="q1-rubric-review-preparation/1",
                    created_at=datetime.now(timezone.utc).isoformat(),
                    source_folder=str(source),
                    baseline_revisions=len(baseline),
                    files={n: sha256(v).hexdigest() for n, v in files.items()},
                    notes="No original writes, no model calls; original omissions retained only in the baseline snapshot.",
                )
            )
        )
    return context


def read_review(folder):
    folder = Path(folder)
    context = json.loads((folder / "annotation-context.json").read_bytes())
    mixed_raw = (folder / "mixed.json").read_bytes()
    baseline_raw = (folder / "open_coding.snapshot.jsonl").read_bytes()
    current_raw = (folder / "judgments.jsonl").read_bytes()
    form, form_hash = load_form(context["rubric_form_version"])
    require(
        sha256((folder / "rubric-form.json").read_bytes()).hexdigest()
        == form_hash
        == context["rubric_form_sha256"],
        "Form snapshot mismatch",
    )
    require(
        context["rubric_status"] == "published"
        and context["rubric_version"] == form["rubric_version"]
        and context["rubric_sha256"] == form["rubric_sha256"],
        "Review rubric mismatch",
    )
    require(
        sha256(mixed_raw).hexdigest() == context["mixed_sha256"]
        and sha256(baseline_raw).hexdigest() == context["baseline_sha256"],
        "Review input snapshot mismatch",
    )
    mixed = json.loads(mixed_raw)
    require(
        mixed["schema"] == "q1-mixed/1"
        and mixed["batch_id"] == context["batch_id"]
        and digest({k: v for k, v in mixed.items() if k != "batch_id"})
        == mixed["batch_id"],
        "Review batch mismatch",
    )
    old, new = raw_rows(baseline_raw), raw_rows(current_raw)
    validate_rows(old, mixed)
    validate_rows(new, mixed)
    require(
        all(
            r["schema"] == "q1-mixed-judgment/1"
            and r["rubric_version"] == "open_coding"
            and r["annotator_id"] == context["annotator_id"]
            for r in old
        ),
        "Wrong baseline scope",
    )
    require(
        all(
            r["schema"] == "q1-mixed-judgment/2"
            and all(
                r[k] == context[k]
                for k in [
                    "annotator_id",
                    "rubric_version",
                    "rubric_sha256",
                    "rubric_form_version",
                    "rubric_form_sha256",
                    "review_session_id",
                ]
            )
            for r in new
        ),
        "Wrong review scope",
    )
    return context, form, mixed, old, new, current_raw


def comparison(folder):
    context, form, mixed, old, new, current_raw = read_review(folder)
    # Omission/window notes never enter this report or its denominators.
    old_latest = {r["record_id"]: r for r in old if r["record_type"] == "marginalia"}
    new_latest = {r["record_id"]: r for r in new if r["record_type"] == "marginalia"}
    first = {}
    for r in new:
        if r["record_type"] == "marginalia":
            first.setdefault(r["record_id"], r)
    groups = {"old_pass_new_fail": [], "old_fail_new_pass": [], "rubric_uncovered": []}
    incomplete, unpaired, unchanged = [], [], 0
    for w in mixed["windows"]:
        for m in w["marginalia"]:
            mid = m["marginalia_id"]
            a, b = old_latest.get(mid), new_latest.get(mid)
            identity = dict(window_id=w["window_id"], marginalia_id=mid, type=m["type"])
            if not b:
                incomplete.append(identity)
                continue
            spec = form["mark_types"][m["type"]]
            labels = {c["id"]: c["label"] for c in spec["criteria"]}
            item = dict(
                **identity,
                body_text=m["body_text"],
                source_quote=m["source_quote"],
                old_judgment=a["judgment"] if a else None,
                old_reason=a["reason"] if a else None,
                new_judgment=b["judgment"],
                failed_criteria=b["failed_criteria"],
                failed_criteria_labels=[labels[c] for c in b["failed_criteria"]],
                tags=b["tags"],
                criterion_flags=b["criterion_flags"],
                rubric_uncovered=b["rubric_uncovered"],
                new_reason=b["reason"],
                remarks=b["remarks"],
                old_revision=a["revision"] if a else None,
                new_revision=b["revision"],
                first_completed_revision=first[mid]["revision"],
                first_completed_judgment=first[mid]["judgment"],
                prior_judgment_seen=b["prior_judgment_seen"],
            )
            if b["rubric_uncovered"]:
                groups["rubric_uncovered"].append(item)
            if not a or a["judgment"] not in ("pass", "fail"):
                unpaired.append(item)
            elif a["judgment"] == b["judgment"]:
                unchanged += 1
            elif a["judgment"] == "pass":
                groups["old_pass_new_fail"].append(item)
            else:
                groups["old_fail_new_pass"].append(item)
    return dict(
        schema="q1-rubric-human-comparison/1",
        context=context,
        snapshots={
            "open_coding_sha256": context["baseline_sha256"],
            "review_sha256": sha256(current_raw).hexdigest(),
            "review_revisions": len(new),
            "mixed_sha256": context["mixed_sha256"],
        },
        counts={
            "annotations": sum(len(w["marginalia"]) for w in mixed["windows"]),
            "completed": len(new_latest),
            "unchanged": unchanged,
            "incomplete": len(incomplete),
            "unpaired": len(unpaired),
            **{k: len(v) for k, v in groups.items()},
        },
        **groups,
        incomplete=incomplete,
        unpaired=unpaired,
        notes=[
            "Latest completed human revisions; first pre-exposure completion retained.",
            "Rubric examples are included in this human rejudgment comparison, not an LLM judge agreement evaluation.",
            "No omission analysis; no group/model mapping loaded. Uncovered items may overlap disagreement groups.",
        ],
    )


def write_report(folder, output):
    output = state_destination(output)
    report = comparison(folder)
    lines = [
        "# " + report["context"]["rubric_version"] + " 与 open_coding 人工判定对照",
        "",
        json.dumps(report["counts"], ensure_ascii=False),
        "",
        "按各日志最新已完成修订配对。未判条目不计为通过；rubric 未覆盖清单可与差异清单重叠。",
        "本报告不分析漏标，不揭晓组别；包含全部已完成条目，不应用 LLM judge 的例子排除清单。",
        "",
        "快照：`" + json.dumps(report["snapshots"], ensure_ascii=False) + "`",
        "",
    ]
    for key, title in [
        ("old_pass_new_fail", "旧过新不过"),
        ("old_fail_new_pass", "旧不过新过"),
        ("rubric_uncovered", "rubric 未覆盖"),
    ]:
        lines += ["## " + title, ""]
        if not report[key]:
            lines += ["无。", ""]
        for r in report[key]:
            lines += [
                "### " + r["marginalia_id"],
                "",
                "类型：" + r["type"],
                "",
                "锚点原文：" + r["source_quote"],
                "",
                "批注正文："
                + (r["body_text"] if r["type"] == "N" else r["source_quote"]),
                "",
                "旧判定：" + str(r["old_judgment"]) + "；新判定：" + r["new_judgment"],
                "",
                "旧理由：" + str(r["old_reason"] or ""),
                "",
                "不满足："
                + ", ".join(r["failed_criteria"])
                + "；标签："
                + ", ".join(r["tags"]),
                "",
                "条目标记："
                + json.dumps(r["criterion_flags"], ensure_ascii=False)
                + "；rubric 未覆盖："
                + str(r["rubric_uncovered"]),
                "",
                "新理由：" + r["new_reason"],
                "",
                "备注：" + r["remarks"],
                "",
                "已查看旧判断："
                + str(r["prior_judgment_seen"])
                + "；首次完成修订："
                + str(r["first_completed_revision"]),
                "",
            ]
    output.mkdir(parents=True, exist_ok=False)
    (output / "report.json").write_bytes(encode(report))
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return report["counts"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("source", type=Path)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--form", default="q1-v0.form.v1")
    prep.add_argument("--annotator", default="weijiang")
    report = sub.add_parser("report")
    report.add_argument("folder", type=Path)
    report.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = (
        prepare(args.source, args.output, args.form, args.annotator)
        if args.command == "prepare"
        else write_report(args.folder, args.output)
    )
    print(json.dumps(result, ensure_ascii=False))
