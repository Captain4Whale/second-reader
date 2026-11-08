#!/usr/bin/env python3
"""Check frozen unit/rubric identities, trial rows and append-only annotation overlays."""

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

BACKEND = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def rows(path):
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError(f"Incomplete JSONL: {path}")
    return [json.loads(line) for line in raw.splitlines()]


def rubric_identity(version, root=BACKEND):
    if version == "open_coding":
        return {
            "rubric_version": version,
            "rubric_sha256": None,
            "rubric_status": "no_rubric",
        }
    release = load(root / "rubric/releases.json")[version]
    path = root / release["path"]
    if release["status"] != "published" or sha(path) != release["sha256"]:
        raise ValueError(f"Rubric is draft or changed: {version}")
    return {
        "rubric_version": version,
        "rubric_sha256": release["sha256"],
        "rubric_status": "published",
    }


def validate_trial(row, root=BACKEND):
    required = {
        "experiment_id",
        "date",
        "hypothesis",
        "change",
        "changed_variables",
        "prompts",
        "unit_set",
        "run_ids",
        "rubric_version",
        "results",
        "conclusion",
        "notes",
        "phase",
    }
    if not required <= row.keys() or not row["run_ids"]:
        raise ValueError("Trial lacks required fields/run IDs")
    if (
        not isinstance(row["changed_variables"], list)
        or len(row["changed_variables"]) > 1
    ):
        raise ValueError("A trial may change only one variable")
    if row["phase"] not in {"baseline", "iteration", "final_validation"}:
        raise ValueError("Unknown trial phase")
    manifest = root / row["unit_set"]["path"]
    if sha(manifest) != row["unit_set"]["sha256"]:
        raise ValueError("Unit manifest hash mismatch")
    if load(manifest)["purpose"] == "holdout" and row["phase"] != "final_validation":
        raise ValueError("Holdout is reserved for final validation")
    rubric = rubric_identity(row["rubric_version"], root)
    if row.get("rubric_sha256") != rubric["rubric_sha256"]:
        raise ValueError("Trial rubric fingerprint mismatch")
    if row.get("annotations"):
        annotation = row["annotations"]
        lines = (root / annotation["path"]).read_bytes().splitlines(keepends=True)
        if (
            hashlib.sha256(b"".join(lines[: annotation["context_count"]])).hexdigest()
            != annotation["sha256"]
        ):
            raise ValueError("Annotation context snapshot mismatch")
    lock = load(root / "src/attentional_v2/prompts/versions/published.json")["releases"]
    for prompt in row["prompts"]:
        if prompt["release_sha256"] != lock[prompt["version"]]["release_sha256"]:
            raise ValueError("Prompt release hash mismatch")
        if prompt.get("hash_evidence") not in {
            "runtime_recorded",
            "reconstructed_after_run",
        }:
            raise ValueError(
                "Prompt hash evidence must distinguish runtime from reconstruction"
            )
    if not row["prompts"]:
        raise ValueError("Trial lacks prompt identities")


def append_trial(row, root=BACKEND):
    validate_trial(row, root)
    path = root / "experiments/log.jsonl"
    with path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        previous = stream.read()
        if previous and not previous.endswith("\n"):
            raise ValueError("Incomplete trial log; refusing append")
        if any(
            json.loads(line)["experiment_id"] == row["experiment_id"]
            for line in previous.splitlines()
        ):
            raise ValueError("Duplicate experiment ID; refusing overwrite")
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def check(root=BACKEND, base_ref="HEAD", annotation_root=None):
    lock = load(root / "experiments/frozen.json")
    for name, digest in lock.items():
        if sha(root / name) != digest:
            raise ValueError(f"Frozen file changed: {name}")
    rubrics = load(root / "rubric/releases.json")
    for version, release in rubrics.items():
        if (
            release["status"] not in {"draft", "published"}
            or sha(root / release["path"]) != release["sha256"]
        ):
            raise ValueError(f"Rubric release changed: {version}")
    sets = [
        load(root / f"experiments/unit-sets/{name}-v1.json")
        for name in ("dev", "holdout")
    ]
    identity = lambda u: (u["original_epub_sha256"], u["unit_id"])
    members = [{identity(u) for u in s["units"]} for s in sets]
    if (
        any(len(m) != len(s["units"]) for m, s in zip(members, sets))
        or members[0] & members[1]
    ):
        raise ValueError("Duplicate units or dev/holdout leakage")
    ids = set()
    for row in rows(root / "experiments/log.jsonl"):
        validate_trial(row, root)
        if row["experiment_id"] in ids:
            raise ValueError("Duplicate experiment ID")
        ids.add(row["experiment_id"])
    overlays = rows(root / "experiments/annotations/legacy-context.jsonl")
    for overlay in overlays:
        if (
            overlay["rubric_version"] != "open_coding"
            or overlay["annotator_id"] != "weijiang"
        ):
            raise ValueError("Unexpected legacy annotation attribution")
        if annotation_root:
            path = annotation_root / overlay["batch_id"] / "judgments.jsonl"
            raw = path.read_bytes().splitlines(keepends=True)
            prefix = b"".join(raw[: overlay["revision_end"]])
            if hashlib.sha256(prefix).hexdigest() != overlay["journal_prefix_sha256"]:
                raise ValueError("Legacy journal prefix changed")
            for i, line in enumerate(raw, 1):
                record = json.loads(line)
                if record["revision"] != i or record["batch_id"] != overlay["batch_id"]:
                    raise ValueError("Journal identity/revision mismatch")
                if i > overlay["revision_end"]:
                    if not record.get("annotator_id") or not record.get(
                        "rubric_version"
                    ):
                        raise ValueError(
                            "New annotation lacks rubric/annotator identity"
                        )
                    rubric = rubric_identity(record["rubric_version"], root)
                    if record.get("rubric_sha256") != rubric["rubric_sha256"]:
                        raise ValueError("Annotation rubric fingerprint mismatch")
    if base_ref:
        prefix = root.name + "/"

        def before(name):
            result = subprocess.run(
                ["git", "-C", str(root), "show", f"{base_ref}:{prefix}{name}"],
                capture_output=True,
            )
            return result.stdout if result.returncode == 0 else None

        old = before("experiments/frozen.json")
        if old:
            for name, digest in json.loads(old).items():
                if lock.get(name) != digest:
                    raise ValueError(f"Frozen lock entry changed: {name}")
        old = before("rubric/releases.json")
        if old:
            for version, release in json.loads(old).items():
                if rubrics.get(version) != release:
                    raise ValueError(f"Rubric publication entry changed: {version}")
        name = "experiments/annotations/legacy-context.jsonl"
        old = before(name)
        if old and not (root / name).read_bytes().startswith(old):
            raise ValueError("Legacy context mappings are append-only")
    return {
        "experiments": len(ids),
        "dev_units": len(members[0]),
        "holdout_units": len(members[1]),
        "legacy_contexts": len(overlays),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="HEAD")
    parser.add_argument("--annotation-root", type=Path)
    parser.add_argument("--append-trial", type=Path)
    parser.add_argument(
        "--write-context",
        type=Path,
        help="New annotation-context.json; will not overwrite",
    )
    parser.add_argument("--batch-id")
    parser.add_argument("--rubric-version", default="open_coding")
    parser.add_argument("--annotator-id", default="weijiang")
    args = parser.parse_args()
    if args.append_trial:
        append_trial(load(args.append_trial))
    elif args.write_context:
        if not args.batch_id or not args.annotator_id.strip():
            parser.error("--batch-id and nonempty --annotator-id required")
        context = {
            "batch_id": args.batch_id,
            "annotator_id": args.annotator_id,
            **rubric_identity(args.rubric_version),
        }
        with args.write_context.open("x") as stream:
            json.dump(context, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    else:
        print(
            json.dumps(
                check(base_ref=args.base_ref, annotation_root=args.annotation_root)
            )
        )
