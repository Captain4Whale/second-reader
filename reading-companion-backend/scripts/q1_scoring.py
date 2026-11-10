"""Append-only, offline scoring receipts. No model imports or annotation writes."""

import argparse
from collections import Counter
import fcntl
import json
from pathlib import Path
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_comparison import legacy_batch, require  # noqa: E402
from scripts.q1_comparison_stats import load_bundle, summarize, validate_rows  # noqa: E402
from scripts.q1_private_snapshot import fingerprint  # noqa: E402
from scripts.q1_rubric_review import read_review  # noqa: E402
from scripts.q1_rubric_form import load_form  # noqa: E402
from scripts.check_iteration_provenance import rubric_identity  # noqa: E402


def read_lines(path):
    raw = Path(path).read_bytes()
    require(not raw or raw.endswith(b"\n"), "Incomplete JSONL tail")
    return [json.loads(line) for line in raw.splitlines()]


def resolve_path(name, root=BACKEND):
    """Latest mapping for an exact prefix; do not mutate old path strings."""
    path = Path(name)
    mappings = {}
    for row in read_lines(root / "experiments/log.jsonl"):
        for mapping in row.get("path_mappings", []):
            mappings[Path(mapping["from"])] = Path(mapping["to"])
    matches = [p for p in mappings if path.is_relative_to(p)]
    if matches:
        prefix = max(matches, key=lambda p: len(p.parts))
        path = mappings[prefix] / path.relative_to(prefix)
    return path if path.is_absolute() else root / path


def counts(marks, latest, form=None):
    result = {}
    for kind, name in [("N", "Note"), ("H", "Highlight")]:
        selected = [m for m in marks if m["type"] == kind]
        rows = [
            latest[m["marginalia_id"]] for m in selected if m["marginalia_id"] in latest
        ]
        passed = sum(r["judgment"] == "pass" for r in rows)
        failed = sum(r["judgment"] == "fail" for r in rows)
        judged = passed + failed
        criteria = None
        if form:
            counter = Counter(c for r in rows for c in r["failed_criteria"])
            criteria = {
                c["id"]: {"label": c["label"], "failed": counter[c["id"]]}
                for c in form["mark_types"][kind]["criteria"]
            }
        result[name] = dict(
            total=len(selected),
            judged=judged,
            passed=passed,
            failed=failed,
            unjudged=len(selected) - judged,
            pass_rate=passed / judged if judged else None,
            failed_criteria=criteria,
            rubric_uncovered=sum(r.get("rubric_uncovered", False) for r in rows)
            if form
            else None,
            prior_judgment_seen=sum(r.get("prior_judgment_seen", False) for r in rows)
            if form
            else None,
        )
    return result


def legacy_latest(batch, rows, overlay):
    require(len(rows) == overlay["revision_end"], "Legacy snapshot cutoff mismatch")
    marks = {
        (u["unit_id"], m["marginalia_id"]): m
        for u in batch["units"]
        for m in u["marginalia"]
    }
    latest = {}
    for i, r in enumerate(rows, 1):
        require(
            r["revision"] == i and r["batch_id"] == batch["batch_id"],
            "Legacy revision/batch mismatch",
        )
        require(
            r["run_id"] == batch["run_id"]
            and r["product_sha256"] == batch["product_sha256"],
            "Legacy product mismatch",
        )
        if r["record_type"] != "marginalia":
            continue
        key = (r["unit_id"], r["marginalia_id"])
        require(
            key in marks
            and r["type"] == marks[key]["type"]
            and r["original_source_range"] == marks[key]["original_source_range"],
            "Legacy mark mismatch",
        )
        require(r["judgment"] in (None, "pass", "fail"), "Invalid legacy judgment")
        latest[r["marginalia_id"]] = r
    return latest


def calculate(row, root=BACKEND):
    """Recompute from the exact frozen files, never from a moving live journal."""
    inputs = row["inputs"]
    products = {p["run_id"]: p for p in row["products"]}
    manifest = json.loads((root / row["unit_set"]["path"]).read_bytes())
    units = manifest["units"]
    result = []
    if inputs["kind"] == "legacy":
        overlays = {
            o["batch_id"]: o
            for o in read_lines(root / "experiments/annotations/legacy-context.jsonl")
        }
        actual_units = set()
        for batch_input, snap in zip(inputs["batches"], row["snapshots"], strict=True):
            b = legacy_batch(root / batch_input)
            overlay = overlays[b["batch_id"]]
            require(
                snap["sha256"] == overlay["journal_prefix_sha256"]
                and row["scorer"]["id"] == overlay["annotator_id"],
                "Legacy attribution mismatch",
            )
            rows = read_lines(root / snap["path"])
            latest = legacy_latest(b, rows, overlay)
            actual_units.update((b["run_id"], u["unit_id"]) for u in b["units"])
            require(
                products[b["run_id"]]["product_sha256"] == b["product_sha256"],
                "Legacy product identity mismatch",
            )
            result.append(
                {
                    "run_id": b["run_id"],
                    "counts": counts(
                        [m for u in b["units"] for m in u["marginalia"]], latest
                    ),
                }
            )
        require(
            actual_units == {(u["run_id"], u["unit_id"]) for u in units},
            "Legacy unit set mismatch",
        )
    else:
        folder = root / inputs["bundle"]
        b, mixed, key = load_bundle(folder)
        require(
            b["unit_set"]["sha256"] == row["unit_set"]["sha256"],
            "Comparison unit set mismatch",
        )
        require(len(b["windows"]) == row["unit_set"]["count"], "Window count mismatch")
        for g in b["groups"]:
            p = products[g["run_id"]]
            require(
                p["model"] == g["model"]
                and p["product_sha256"] == g["output_sha256"]
                and g["prompt"] in p["prompts"],
                "Comparison product identity mismatch",
            )
        snap = row["snapshots"][0]
        if inputs["kind"] == "mixed":
            require(
                row["rubric"]["form_version"] is None, "Open coding has no rubric form"
            )
            raw = summarize(
                folder,
                root / snap["path"],
                snap["revision"],
                row["scorer"]["id"],
                row["rubric"]["version"],
            )
            require(len(raw["scopes"]) == 1, "Ambiguous scoring scope")
            for g in raw["scopes"][0]["groups"]:
                result.append(
                    {
                        "run_id": g["run_id"],
                        "counts": {
                            k: {
                                **{
                                    n: c[n]
                                    for n in [
                                        "total",
                                        "judged",
                                        "passed",
                                        "failed",
                                        "unjudged",
                                        "pass_rate",
                                    ]
                                },
                                "failed_criteria": None,
                                "rubric_uncovered": None,
                                "prior_judgment_seen": None,
                            }
                            for k, c in g["counts"].items()
                        },
                    }
                )
        else:
            context, form, projection, _, rows, _ = read_review(root / inputs["review"])
            require(
                projection == mixed
                and context["review_session_id"] == row["review_session_id"],
                "Review session/product mismatch",
            )
            require(
                context["annotator_id"] == row["scorer"]["id"]
                and context["rubric_form_version"] == row["rubric"]["form_version"],
                "Review scorer/form mismatch",
            )
            require(
                (root / inputs["review"] / "judgments.jsonl").read_bytes()
                == (root / snap["path"]).read_bytes(),
                "Review snapshot mismatch",
            )
            validate_rows(rows, mixed)
            latest = {
                r["marginalia_id"]: r
                for r in rows
                if r["record_type"] == "marginalia" and r["review_completed"]
            }
            for g in b["groups"]:
                marks = [
                    m
                    for m in b["marginalia"]
                    if m["mixed_window_id"] is not None
                    and key["marginalia"][m["marginalia_id"]]["opaque_group_id"]
                    == g["opaque_group_id"]
                ]
                result.append(
                    {"run_id": g["run_id"], "counts": counts(marks, latest, form)}
                )
    require(
        {x["run_id"] for x in result} == set(products), "Result/product groups mismatch"
    )
    return result


def validate(row, root=BACKEND, evidence=False):
    required = {
        "schema",
        "scoring_id",
        "series_id",
        "supersedes",
        "registered_at",
        "date",
        "experiment_id",
        "title",
        "status",
        "products",
        "unit_set",
        "rubric",
        "scorer",
        "snapshots",
        "blinding",
        "inputs",
        "evidence_files",
        "results",
        "comparable_to",
        "calculation",
        "review_session_id",
    }
    require(set(row) == required, "Scoring fields mismatch")
    require(
        row["schema"] == "q1-scoring/1"
        and row["status"] in ["pending", "partial", "completed"],
        "Invalid scoring schema/status",
    )
    from datetime import datetime

    require(
        datetime.fromisoformat(row["registered_at"]).tzinfo is not None,
        "Registration requires timezone",
    )
    require(
        row["scorer"]["kind"] in ["human", "judge"] and row["scorer"]["id"],
        "Missing scorer",
    )
    if row["scorer"]["kind"] == "judge":
        require(
            row["scorer"].get("version") and row["scorer"].get("config_sha256"),
            "Judge requires version/config identity",
        )
    unit_set = row["unit_set"]
    require(
        fingerprint(root / unit_set["path"]) == unit_set["sha256"],
        "Unit set hash mismatch",
    )
    require(
        len(json.loads((root / unit_set["path"]).read_bytes())["units"])
        == unit_set["count"],
        "Unit count mismatch",
    )
    identity = rubric_identity(row["rubric"]["version"], root)
    require(
        identity["rubric_sha256"] == row["rubric"]["sha256"], "Rubric hash mismatch"
    )
    if row["rubric"]["form_version"]:
        form, digest = load_form(row["rubric"]["form_version"], root)
        require(
            digest == row["rubric"]["form_sha256"]
            and form["rubric_version"] == row["rubric"]["version"],
            "Form mismatch",
        )
    else:
        require(row["rubric"]["form_sha256"] is None, "Unexpected form hash")
    registered = {
        r["experiment_id"] for r in read_lines(root / "experiments/log.jsonl")
    }
    require(row["experiment_id"] in registered, "Unknown experiment")
    lock = json.loads(
        (root / "src/attentional_v2/prompts/versions/published.json").read_bytes()
    )["releases"]
    require(row["products"] and row["snapshots"], "Missing product/snapshot")
    for p in row["products"]:
        require(
            p["experiment_id"] in registered
            and p["model"]
            and p["reasoning_effort"]
            and p["prompts"],
            "Missing product identity",
        )
        for prompt in p["prompts"]:
            require(
                lock[prompt["version"]]["release_sha256"] == prompt["release_sha256"],
                "Prompt hash mismatch",
            )
        require(
            p["hash_evidence"] in ["runtime_recorded", "reconstructed_after_run"],
            "Missing hash evidence boundary",
        )
    require(
        row["inputs"]["kind"] in ["legacy", "mixed", "rubric"],
        "Unknown scoring adapter",
    )
    for snap in row["snapshots"]:
        require(
            type(snap["revision"]) is int
            and snap["revision"] >= 0
            and row["evidence_files"].get(snap["path"]) == snap["sha256"],
            "Unbound journal snapshot",
        )
    require(len(row["results"]) == len(row["products"]), "Missing group results")
    total_judged = total_unjudged = 0
    for g in row["results"]:
        require(set(g["counts"]) == {"Note", "Highlight"}, "Missing H/N results")
        for c in g["counts"].values():
            require(
                all(
                    type(c[k]) is int and c[k] >= 0
                    for k in ["total", "judged", "passed", "failed", "unjudged"]
                ),
                "Invalid counts",
            )
            require(
                c["passed"] + c["failed"] == c["judged"]
                and c["judged"] + c["unjudged"] == c["total"],
                "Inconsistent counts",
            )
            require(
                c["pass_rate"] == (c["passed"] / c["judged"] if c["judged"] else None),
                "Invalid pass-rate denominator",
            )
            require(
                (c["failed_criteria"] is None)
                == (row["rubric"]["form_version"] is None),
                "Criteria availability mismatch",
            )
            if c["failed_criteria"] is not None:
                require(
                    all(
                        0 <= x["failed"] <= c["failed"]
                        for x in c["failed_criteria"].values()
                    ),
                    "Invalid criterion count",
                )
            total_judged += c["judged"]
            total_unjudged += c["unjudged"]
    require(
        row["status"]
        == (
            "pending"
            if total_judged == 0
            else "partial"
            if total_unjudged
            else "completed"
        ),
        "Completion status mismatch",
    )
    if evidence:
        expected = set(row["inputs"].get("batches", []))
        if row["inputs"].get("bundle"):
            expected.update(
                str(Path(row["inputs"]["bundle"]) / n)
                for n in ["batch.json", "mixed.json", "blind-key.json"]
            )
        if row["inputs"].get("review"):
            expected.update(
                str(Path(row["inputs"]["review"]) / n)
                for n in [
                    "mixed.json",
                    "annotation-context.json",
                    "rubric-form.json",
                    "open_coding.snapshot.jsonl",
                    "judgments.jsonl",
                ]
            )
        require(expected <= set(row["evidence_files"]), "Unbound scoring input")
        for product in row["products"]:
            for path in product.get("settings_evidence", []):
                require(path in row["evidence_files"], "Unbound model settings")
                settings = json.loads(resolve_path(path, root).read_bytes())
                model = settings.get("model") or settings["config"]["profile"]["model"]
                effort = (
                    settings.get("reasoning_effort")
                    or settings["config"]["provider"]["provider_options"][
                        "reasoning_effort"
                    ]
                )
                require(
                    model == product["model"] and effort == product["reasoning_effort"],
                    "Model settings mismatch",
                )
            for path, request_hash in (product.get("request_hashes") or {}).items():
                require(path in row["evidence_files"], "Unbound actual request receipt")
                require(
                    json.loads(resolve_path(path, root).read_bytes())["request_sha256"]
                    == request_hash,
                    "Actual request hash mismatch",
                )
        for path, digest in row["evidence_files"].items():
            require(
                fingerprint(resolve_path(path, root)) == digest,
                f"Evidence hash mismatch: {path}",
            )
        for snap in row["snapshots"]:
            rows = read_lines(root / snap["path"])
            require(
                len(rows) == snap["revision"]
                and all(r["revision"] == i for i, r in enumerate(rows, 1)),
                "Snapshot revision mismatch",
            )
            require(
                sorted({r["annotator_version"] for r in rows})
                == snap["annotator_versions"],
                "Annotator versions mismatch",
            )
            require(
                [
                    min((r["timestamp"] for r in rows), default=None),
                    max((r["timestamp"] for r in rows), default=None),
                ]
                == snap["judgment_time_range"],
                "Judgment dates mismatch",
            )
        require(
            calculate(row, root) == row["results"], "Recomputed scoring results differ"
        )
    return row


def validate_all(rows, root=BACKEND, evidence=False):
    ids, latest = {}, {}
    for r in rows:
        validate(r, root, evidence)
        require(r["scoring_id"] not in ids, "Duplicate scoring ID")
        prior = latest.get(r["series_id"])
        require(
            r["supersedes"] == (prior["scoring_id"] if prior else None),
            "Broken snapshot chain",
        )
        if prior:
            for field in [
                "experiment_id",
                "products",
                "unit_set",
                "rubric",
                "scorer",
                "review_session_id",
            ]:
                require(
                    r[field] == prior[field],
                    "Changed scoring scope requires a new series",
                )
        for ref in r["comparable_to"]:
            require(
                ref["scoring_id"] in ids
                and ref["mode"]
                in ["same_outputs_different_rubric", "descriptive_only", "same_scope"]
                and ref["limitations"],
                "Invalid comparability reference",
            )
            other = ids[ref["scoring_id"]]
            if ref["mode"] == "same_outputs_different_rubric":
                require(
                    other["products"] == r["products"]
                    and other["unit_set"] == r["unit_set"],
                    "Rejudgment must use identical outputs/units",
                )
        ids[r["scoring_id"]] = r
        latest[r["series_id"]] = r
    return latest


def check_prefixes(root=BACKEND, base_ref="HEAD"):
    for name in ["log.jsonl", "scorings.jsonl"]:
        path = f"{root.name}/experiments/{name}"
        previous = subprocess.run(
            ["git", "-C", str(root), "show", f"{base_ref}:{path}"], capture_output=True
        )
        if previous.returncode == 0:
            require(
                (root / "experiments" / name).read_bytes().startswith(previous.stdout),
                f"{name} is append-only",
            )


def append(row, root=BACKEND):
    path = root / "experiments/scorings.jsonl"
    with path.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        raw = stream.read()
        require(not raw or raw.endswith(b"\n"), "Incomplete scoring log")
        rows = [json.loads(line) for line in raw.splitlines()]
        validate_all(rows + [row], root, evidence=True)
        stream.write(
            json.dumps(row, ensure_ascii=False, sort_keys=True).encode() + b"\n"
        )
        stream.flush()
        import os

        os.fsync(stream.fileno())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=BACKEND)
    parser.add_argument("--append", type=Path)
    parser.add_argument("--evidence", action="store_true")
    parser.add_argument("--base-ref", default="HEAD")
    args = parser.parse_args()
    if args.append:
        append(json.loads(args.append.read_bytes()), args.root)
    else:
        rows = read_lines(args.root / "experiments/scorings.jsonl")
        validate_all(rows, args.root, args.evidence)
        check_prefixes(args.root, args.base_ref)
        print(json.dumps({"scorings": len(rows), "evidence_verified": args.evidence}))
