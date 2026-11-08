#!/usr/bin/env python3
"""One-time offline registration of existing Q1 batches; never reads holdout judgments."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from src.prompts.integrity import active_releases
from check_iteration_provenance import check, sha

BATCHES = {
    "eb022649ceece1a1829d6d61f4a4d4535cdad4e4713050bab1db78afc5925ed6": (
        "dev",
        "bovary",
        1,
    ),
    "3015bb621409111746f8c2074f15981dc2a539e4354bfee2c3c5b0a8caafbb90": (
        "dev",
        "sapiens",
        1,
    ),
    "be2aec4e93a8ca860ef4a3937a9bbe30e8421bb0dbca051714c7eb386367c6bd": (
        "holdout",
        "bovary",
        2,
    ),
    "5e5015710488ab8cc8d3a40853b5fbd7e09860104afbbaeff4e94796d1bb098c": (
        "holdout",
        "bovary",
        3,
    ),
}


def register(annotation_root, runs_root):
    outputs = {}
    manifests = {
        purpose: {
            "schema": "fixed-unit-set/1",
            "unit_set_id": f"q1-{purpose}-v1",
            "purpose": purpose,
            "created_at": "2026-11-08",
            "units": [],
        }
        for purpose in ("dev", "holdout")
    }
    runs = {}
    for batch_id, (purpose, book, number) in BATCHES.items():
        path = annotation_root / batch_id / "batch.json"
        batch = json.loads(path.read_bytes())
        payload = {k: v for k, v in batch.items() if k != "batch_id"}
        canonical = json.dumps(
            payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
        if (
            hashlib.sha256(canonical).hexdigest() != batch_id
            or batch["batch_number"] != number
        ):
            raise ValueError("Q1 batch identity mismatch")
        run = json.loads((runs_root / book / "run.json").read_text())
        if (
            run["commit"] != "d414030c149bc56590bed890421eb59aad22aa05"
            or run["source_sha256"] != batch["original_epub_sha256"]
        ):
            raise ValueError("Q1 source/run mismatch")
        expected = {
            "chapter_zone": "attentional_v2.chapter_zone.v2",
            "ingest": "attentional_v2.ingest.v19",
            "digest": "attentional_v2.digest.v24",
        }
        if run["config"]["prompt_versions"] != expected:
            raise ValueError("Q1 prompt identity mismatch")
        runs[batch["run_id"]] = run
        for unit in batch["units"]:
            manifests[purpose]["units"].append(
                {
                    **{
                        k: batch[k]
                        for k in (
                            "batch_id",
                            "run_id",
                            "reading_id",
                            "product_sha256",
                            "original_epub_sha256",
                            "original_substrate_sha256",
                        )
                    },
                    "batch_number": number,
                    "unit_id": unit["unit_id"],
                    "source_range": unit["source_range"],
                    "original_source_range": unit["original_source_range"],
                    "marginalia_ids": [m["marginalia_id"] for m in unit["marginalia"]],
                }
            )
    for purpose, manifest in manifests.items():
        outputs[f"experiments/unit-sets/{purpose}-v1.json"] = (
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        )
    history = {
        "schema": "historical-workspace-evidence/1",
        "code_commit": "d414030c149bc56590bed890421eb59aad22aa05",
        "run_ids": sorted(runs),
        "code_dirty_recorded": True,
        "observed_modified_files": [
            "reading-companion-backend/docs/evaluation/run_ledger.json",
            "reading-companion-backend/docs/evaluation/run_ledger.md",
        ],
        "evidence_source": "Original local Codex session 01a1a13b-3c33-7c80-b435-8e51b48a9200, completed git status command outputs; verified against both run metadata and standard traces",
        "observations": [
            {
                "at": "2026-11-03T12:28:33.409Z",
                "session_line": 365,
                "phase": "before both launches",
            },
            {
                "at": "2026-11-03T12:29:03.009Z",
                "session_line": 388,
                "phase": "immediately after both launches",
            },
            {
                "at": "2026-11-03T22:38:55.022Z",
                "session_line": 571,
                "phase": "after Sapiens completion, before Bovary completion",
            },
            {
                "at": "2026-11-03T22:58:36.581Z",
                "session_line": 847,
                "phase": "after both completions",
            },
        ],
        "original_patch": None,
        "limitations": "Snapshots list only the two ledger files. No contemporaneous git diff patch or continuous workspace audit exists; exact diff contents and changes between snapshots are unrecoverable. Current diff is not substituted for historical evidence.",
    }
    outputs["experiments/baselines/q1-workspace-evidence.json"] = (
        json.dumps(history, ensure_ascii=False, indent=2) + "\n"
    )
    release = active_releases()
    row = {
        "experiment_id": "Q1-BASELINE-001",
        "date": "2026-11-08",
        "generation_date": "2026-11-03",
        "phase": "baseline",
        "hypothesis": "Register current prompt and first-batch human open coding as the reference for later single-variable trials.",
        "change": "None; register existing outputs and judgments without rerunning models.",
        "changed_variables": [],
        "prompts": [
            {
                "version": version,
                "release_sha256": receipt["release_sha256"],
                "hash_evidence": "reconstructed_after_run",
            }
            for version, receipt in release.items()
        ],
        "actual_request_hashes": None,
        "unit_set": {
            "path": "experiments/unit-sets/dev-v1.json",
            "sha256": hashlib.sha256(
                outputs["experiments/unit-sets/dev-v1.json"].encode()
            ).hexdigest(),
        },
        "run_ids": sorted(runs),
        "rubric_version": "open_coding",
        "rubric_sha256": None,
        "annotations": {
            "path": "experiments/annotations/legacy-context.jsonl",
            "sha256": sha(BACKEND / "experiments/annotations/legacy-context.jsonl"),
            "context_count": 2,
            "annotator_id": "weijiang",
        },
        "results": {"pass_rate": None},
        "conclusion": "Pending owner-entered baseline results; no quality score computed.",
        "notes": "605 journal revisions cover 110 marked items and 67 dev units. Holdout is excluded. Release hashes were reconstructed after migration, not observed at historical call time. Actual per-call historical request hashes are unavailable.",
        "historical_workspace": {
            "path": "experiments/baselines/q1-workspace-evidence.json",
            "sha256": hashlib.sha256(
                outputs["experiments/baselines/q1-workspace-evidence.json"].encode()
            ).hexdigest(),
        },
    }
    outputs["experiments/log.jsonl"] = (
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    )
    freeze = {
        name: hashlib.sha256(raw.encode()).hexdigest()
        for name, raw in outputs.items()
        if name != "experiments/log.jsonl"
    }
    for name in ["rubric/q1-v0.md"]:
        freeze[name] = sha(BACKEND / name)
    outputs["experiments/frozen.json"] = json.dumps(freeze, indent=2) + "\n"
    # Check every target before writing anything. Repeat execution cannot erase reviews.
    if any((BACKEND / name).exists() for name in outputs):
        raise FileExistsError(
            "Baseline registration already exists; refusing overwrite"
        )
    for name, raw in outputs.items():
        p = BACKEND / name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("x") as stream:
            stream.write(raw)
    return check(annotation_root=annotation_root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation-root", type=Path, required=True)
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=BACKEND / "state/eval_local_datasets/q1_fullbooks_d414030_20261103",
    )
    args = parser.parse_args()
    print(json.dumps(register(args.annotation_root, args.runs_root)))
