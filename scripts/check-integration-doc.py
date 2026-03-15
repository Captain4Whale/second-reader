#!/usr/bin/env python3
"""Validate that the API integration doc appendix matches the frontend integration spec."""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT_DIR / "docs" / "api-integration.md"
FRONTEND_DIR = ROOT_DIR / "reading-companion-frontend"


def _normalized_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _load_doc_spec() -> dict:
    text = DOC_PATH.read_text(encoding="utf-8")
    heading = "## Machine-Readable Appendix"
    if heading not in text:
        raise RuntimeError(f"Missing '{heading}' in {DOC_PATH}.")

    appendix_text = text.split(heading, 1)[1]
    match = re.search(r"```json\s*(\{.*?\})\s*```", appendix_text, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"Could not find a fenced JSON appendix in {DOC_PATH}.")
    return json.loads(match.group(1))


def _load_frontend_spec() -> dict:
    result = subprocess.run(
        ["npx", "tsx", "scripts/print-integration.ts"],
        cwd=FRONTEND_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _assert_same(label: str, left: dict, right: dict) -> None:
    if left == right:
        return
    diff = "\n".join(
        difflib.unified_diff(
            _normalized_json(left).splitlines(),
            _normalized_json(right).splitlines(),
            fromfile=f"{label}-left",
            tofile=f"{label}-right",
            lineterm="",
        )
    )
    raise RuntimeError(f"{label} drift detected.\n{diff}")


def main() -> int:
    doc_spec = _load_doc_spec()
    frontend_spec = _load_frontend_spec()

    _assert_same("doc-vs-frontend", doc_spec, frontend_spec)
    print("Integration document appendix matches the frontend integration spec.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
