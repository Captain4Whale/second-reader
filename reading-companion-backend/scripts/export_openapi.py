#!/usr/bin/env python3
"""Export or verify the public OpenAPI snapshot for the backend API."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from src.api.app import app


BACKEND_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = BACKEND_DIR.parent / "contract" / "openapi.public.snapshot.json"


def _normalized_snapshot() -> str:
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True)


def write_snapshot() -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(_normalized_snapshot(), encoding="utf-8")
    print(f"Wrote {SNAPSHOT_PATH}")


def check_snapshot() -> int:
    if not SNAPSHOT_PATH.exists():
        print(f"error: snapshot missing at {SNAPSHOT_PATH}")
        return 1

    expected = SNAPSHOT_PATH.read_text(encoding="utf-8")
    current = _normalized_snapshot()
    if expected == current:
        print("OpenAPI snapshot matches.")
        return 0

    diff = "\n".join(
        difflib.unified_diff(
            expected.splitlines(),
            current.splitlines(),
            fromfile=str(SNAPSHOT_PATH),
            tofile="current-openapi",
            lineterm="",
        )
    )
    print(diff)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the committed snapshot differs from the current OpenAPI output.")
    args = parser.parse_args()
    if args.check:
        return check_snapshot()
    write_snapshot()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
