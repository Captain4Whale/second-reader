#!/usr/bin/env python3
"""Reconstruct one accepted unit, then optionally run an isolated Digest."""

import argparse
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from eval.attentional_v2.fixed_history_digest import HistoricalRun, run_digest, write


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-backend", type=Path, required=True)
    p.add_argument("--operator-backend", type=Path, help="existing local model configuration and .env; defaults to source backend")
    p.add_argument("--run-id", required=True)
    p.add_argument("--unit-id", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--model")
    p.add_argument("--reasoning-effort", choices=("low", "medium", "high"))
    p.add_argument("--prompt-version")
    p.add_argument("--prepare-only", action="store_true")
    args = p.parse_args()
    if not args.output.resolve().is_relative_to((BACKEND / "state").resolve()):
        p.error("--output must be inside this worktree's ignored backend/state")
    history = HistoricalRun(args.source_backend, args.run_id)
    checks = history.check_manifest()
    packet = history.reconstruct(args.unit_id)
    if args.prepare_only:
        args.output.mkdir(parents=True, exist_ok=False)
        write(args.output / "input.json", packet)
        write(args.output / "manifest-check.json", checks)
    else:
        run_digest(packet, args.output, model=args.model or packet["accepted_call"]["model"],
                   effort=args.reasoning_effort or packet["accepted_call"]["sampling"]["reasoning_effort"],
                   prompt_version=args.prompt_version or packet["accepted_call"]["prompt_version"],
                   operator_backend=args.operator_backend or args.source_backend)
    print(args.output)


if __name__ == "__main__":
    main()
