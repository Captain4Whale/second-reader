#!/usr/bin/env python3
"""Create private mixed batches from the fixed-history Digest output contract."""

import argparse
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.q1_comparison import (  # noqa: E402
    build_bundle,
    legacy_output,
    load_dev_windows,
    load_output,
    write_bundle,
)
from scripts.q1_comparison_fixture import synthetic_inputs  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--unit-set", type=Path, default=BACKEND / "experiments/unit-sets/dev-v1.json"
    )
    p.add_argument("--batch-root", type=Path)
    p.add_argument("--group", type=Path, action="append", default=[])
    p.add_argument(
        "--legacy-baseline",
        action="store_true",
        help="one group from existing dev outputs; no judgment import",
    )
    p.add_argument(
        "--synthetic",
        action="store_true",
        help="fabricated source and two groups; no model calls",
    )
    p.add_argument("--output", type=Path, default=BACKEND / "state/q1_comparison")
    p.add_argument(
        "--experiment-log", type=Path, default=BACKEND / "experiments/log.jsonl"
    )
    args = p.parse_args()
    if args.synthetic:
        if args.group or args.legacy_baseline or args.batch_root:
            p.error("--synthetic cannot be combined with real inputs")
        sources, windows, outputs, unit_set = synthetic_inputs()
    else:
        if not args.batch_root or not (args.group or args.legacy_baseline):
            p.error(
                "--batch-root and at least one --group or --legacy-baseline are required"
            )
        sources, windows, batches, unit_set = load_dev_windows(
            args.unit_set, args.batch_root
        )
        outputs = [load_output(path, args.experiment_log) for path in args.group]
        if args.legacy_baseline:
            import json

            trials = [
                json.loads(s)
                for s in args.experiment_log.read_text().splitlines()
                if s.strip()
            ]
            trial = next(r for r in trials if r["experiment_id"] == "Q1-BASELINE-001")
            # Keep only the frozen units, even if a source batch contains other units.
            selected = {
                (w["legacy_ref"]["batch_id"], w["legacy_ref"]["unit_id"])
                for w in windows
            }
            for bid, b in batches.items():
                b["units"] = [u for u in b["units"] if (bid, u["unit_id"]) in selected]
            outputs.insert(0, legacy_output(batches, trial))
    bundle = build_bundle(sources, windows, outputs, unit_set)
    dest = write_bundle(args.output, bundle)
    print(dest)
    print(
        f"windows={len(windows)} groups={len(outputs)} mixed_items={sum(len(w['marginalia']) for w in bundle[1]['windows'])} unassigned={len(bundle[0]['unassigned_items'])} synthetic={bundle[1]['synthetic']}"
    )


if __name__ == "__main__":
    main()
