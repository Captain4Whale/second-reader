"""One-time offline backfill of the three approved Q1 scoring scopes."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_scoring import append, calculate, read_lines, validate_all  # noqa: E402
from scripts.q1_private_snapshot import fingerprint  # noqa: E402


def register(annotation_root):
    root = BACKEND
    dest = root / "state/scorings/q1-initial-20261110"
    dest.mkdir(parents=True, exist_ok=False)

    def rel(path):
        return str(path.relative_to(root))

    def copy(source, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as f:
            f.write(source.read_bytes())
        if fingerprint(source) != fingerprint(target):
            raise ValueError("Source changed during copy")
        return target

    def snap(path, source):
        rows = read_lines(path)
        return dict(
            path=rel(path),
            sha256=fingerprint(path),
            revision=len(rows),
            source_path=str(source),
            judgment_time_range=[
                min((r["timestamp"] for r in rows), default=None),
                max((r["timestamp"] for r in rows), default=None),
            ],
            annotator_versions=sorted({r["annotator_version"] for r in rows}),
        )

    def base(series, title, experiment, units, rubric="open_coding"):
        return dict(
            schema="q1-scoring/1",
            scoring_id=series + "-S001",
            series_id=series,
            supersedes=None,
            registered_at=datetime.now(timezone.utc).isoformat(),
            date="2026-11-10",
            experiment_id=experiment,
            title=title,
            status="completed",
            products=[],
            unit_set=dict(
                path=units,
                sha256=fingerprint(root / units),
                count=len(json.loads((root / units).read_text())["units"]),
            ),
            rubric=dict(
                version=rubric, sha256=None, form_version=None, form_sha256=None
            ),
            scorer=dict(kind="human", id="weijiang"),
            snapshots=[],
            blinding={},
            inputs={},
            evidence_files={},
            results=[],
            comparable_to=[],
            review_session_id=None,
            calculation=dict(
                git_commit=subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip(),
                command="python scripts/q1_scoring.py --evidence",
                scripts={
                    p: fingerprint(root / p)
                    for p in [
                        "scripts/q1_scoring.py",
                        "scripts/q1_comparison_stats.py",
                        "scripts/q1_rubric_review.py",
                    ]
                },
            ),
        )

    def bind(row, paths):
        row["evidence_files"].update({rel(p): fingerprint(p) for p in paths})

    trials = read_lines(root / "experiments/log.jsonl")
    baseline = next(r for r in trials if r["experiment_id"] == "Q1-BASELINE-001")
    a = base(
        "Q1-SCORE-BASELINE-OPEN",
        "第一批开放编码",
        "Q1-BASELINE-001",
        "experiments/unit-sets/dev-v1.json",
    )
    a["inputs"] = {"kind": "legacy", "batches": []}
    a["blinding"] = dict(
        was_blind=False,
        groups_previously_revealed=False,
        group_labels_hidden=False,
        prior_judgments_available=False,
        notes="原运行第一批开放编码，未采用混合盲标。",
    )
    for overlay in read_lines(root / "experiments/annotations/legacy-context.jsonl"):
        folder = annotation_root / overlay["batch_id"]
        target = dest / "baseline" / overlay["batch_id"]
        batch_path = copy(folder / "batch.json", target / "batch.json")
        b = json.loads(batch_path.read_bytes())
        raw = (folder / "judgments.jsonl").read_bytes()
        prefix = b"".join(raw.splitlines(keepends=True)[: overlay["revision_end"]])
        journal = target / "judgments.snapshot.jsonl"
        journal.write_bytes(prefix)
        if fingerprint(journal) != overlay["journal_prefix_sha256"]:
            raise ValueError("Historical journal prefix changed")
        a["inputs"]["batches"].append(rel(batch_path))
        a["snapshots"].append(snap(journal, folder / "judgments.jsonl"))
        book = "bovary" if "bovary" in b["run_id"] else "sapiens"
        run_path = copy(
            root
            / "state/eval_local_datasets/q1_fullbooks_d414030_20261103"
            / book
            / "run.json",
            target / "run.json",
        )
        run = json.loads(run_path.read_bytes())
        config = run["config"]
        a["products"].append(
            dict(
                experiment_id=a["experiment_id"],
                group=b["book"],
                run_id=b["run_id"],
                model=config["profile"]["model"],
                reasoning_effort=config["provider"]["provider_options"][
                    "reasoning_effort"
                ],
                product_sha256=b["product_sha256"],
                prompts=[
                    {k: v for k, v in p.items() if k != "hash_evidence"}
                    for p in baseline["prompts"]
                ],
                hash_evidence="reconstructed_after_run",
                request_hashes=None,
                settings_evidence=[rel(run_path)],
                reconstructed=True,
                batch_id=b["batch_id"],
            )
        )
        bind(a, [batch_path, journal, run_path])
    d = root / "state/experiments/Q1-DIGEST-DIAG-001/files"
    bundle = next((d / "blind-batch").iterdir())
    batch = json.loads((bundle / "batch.json").read_text())
    b = base(
        "Q1-SCORE-DIAG-OPEN",
        "DIAG-001 混合盲标",
        "Q1-DIGEST-DIAG-001",
        "experiments/unit-sets/diag-001.json",
    )
    b["inputs"] = dict(kind="mixed", bundle=rel(bundle))
    journal = copy(
        d / "reveal-001/judgments.snapshot.jsonl",
        dest / "diag-open/judgments.snapshot.jsonl",
    )
    b["snapshots"] = [snap(journal, bundle / "judgments.jsonl")]
    b["blinding"] = dict(
        was_blind=True,
        groups_previously_revealed=False,
        group_labels_hidden=True,
        prior_judgments_available=False,
        revealed_at="2026-11-08T09:39:02.151226+00:00",
        notes="评分截点在揭晓之前；既往看过原运行产物，且期间恢复了类型提示。Highlight 标准有漂移，决策仅使用 Note。",
    )
    bind(
        b,
        [
            bundle / n
            for n in ["batch.json", "mixed.json", "blind-key.json", "group-map.json"]
        ]
        + [journal],
    )
    for g in batch["groups"]:
        label = "A1" if g["run_id"].endswith("_A1") else "B"
        receipts = sorted((d / label).glob("*/*/result.json"))
        values = [json.loads(p.read_bytes()) for p in receipts]
        if (
            len(receipts) != 16
            or len({(v["model"], v["reasoning_effort"]) for v in values}) != 1
        ):
            raise ValueError("Incomplete/mixed generation settings")
        product = dict(
            experiment_id=g["experiment_id"],
            group=label,
            run_id=g["run_id"],
            model=g["model"],
            reasoning_effort=values[0]["reasoning_effort"],
            product_sha256=g["output_sha256"],
            prompts=[g["prompt"]],
            hash_evidence="runtime_recorded",
            request_hashes={
                rel(p): v["request_sha256"] for p, v in zip(receipts, values)
            },
            settings_evidence=[rel(p) for p in receipts],
            reconstructed=g["reconstructed"],
            batch_id=batch["comparison_batch_id"],
        )
        b["products"].append(product)
        bind(b, receipts)
    b["comparable_to"] = [
        dict(
            scoring_id=a["scoring_id"],
            mode="descriptive_only",
            limitations="67 单元与其 16 单元子集；生成产物不同，不能直接把通过率差归因于判定标准或模型。",
        )
    ]
    c = base(
        "Q1-SCORE-DIAG-Q1V0",
        "DIAG-001 q1-v0 重判",
        "Q1-DIGEST-DIAG-001",
        "experiments/unit-sets/diag-001.json",
        "q1-v0",
    )
    source = root / "state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v0"
    review = dest / "diag-q1v0"
    for name in [
        "mixed.json",
        "annotation-context.json",
        "rubric-form.json",
        "open_coding.snapshot.jsonl",
        "judgments.jsonl",
        "preparation.json",
    ]:
        copy(source / name, review / name)
    if (review / "judgments.jsonl").stat().st_size:
        raise ValueError(
            "Review is no longer pending; do not replace existing annotations"
        )
    context = json.loads((review / "annotation-context.json").read_text())
    c.update(
        products=deepcopy(b["products"]),
        status="pending",
        inputs=dict(kind="rubric", bundle=rel(bundle), review=rel(review)),
        review_session_id=context["review_session_id"],
        evidence_files=deepcopy(b["evidence_files"]),
    )
    c["rubric"] = dict(
        version="q1-v0",
        sha256=context["rubric_sha256"],
        form_version=context["rubric_form_version"],
        form_sha256=context["rubric_form_sha256"],
    )
    c["snapshots"] = [snap(review / "judgments.jsonl", source / "judgments.jsonl")]
    c["blinding"] = dict(
        was_blind=False,
        groups_previously_revealed=True,
        group_labels_hidden=True,
        prior_judgments_available=True,
        notes="已揭晓后的匿名重判；先完成并保存才允许查看旧判断，后续修订记录暴露状态。",
    )
    c["comparable_to"] = [
        dict(
            scoring_id=b["scoring_id"],
            mode="same_outputs_different_rubric",
            limitations="相同 81 条产物，尺子和表单不同；已知揭晓结果，不能当作独立盲标。",
        )
    ]
    bind(c, list(review.iterdir()))
    rows = [a, b, c]
    for row in rows:
        row["results"] = calculate(row)
        report = dest / (row["scoring_id"] + ".report.json")
        report.write_text(
            json.dumps(row["results"], ensure_ascii=False, indent=2) + "\n"
        )
        bind(row, [report])
        row["calculation"]["report"] = rel(report)
    validate_all(rows, evidence=True)
    for row in rows:
        append(row)
    print(json.dumps({"scorings": [r["scoring_id"] for r in rows]}, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annotation-root", required=True, type=Path)
    register(p.parse_args().annotation_root)
