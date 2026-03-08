#!/usr/bin/env python3
"""Validate that the API contract doc appendix matches backend and frontend constants."""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT_DIR / "docs" / "api-contract.md"
BACKEND_DIR = ROOT_DIR / "reading-companion-backend"
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


def _load_backend_spec() -> dict:
    sys.path.insert(0, str(BACKEND_DIR))
    from src.api.contract import PUBLIC_CONTRACT_SPEC  # pylint: disable=import-error

    return json.loads(json.dumps(PUBLIC_CONTRACT_SPEC))


def _load_frontend_spec() -> dict:
    result = subprocess.run(
        ["npx", "tsx", "scripts/print-contract.ts"],
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
    backend_spec = _load_backend_spec()
    frontend_spec = _load_frontend_spec()

    _assert_same("doc-vs-backend", doc_spec, backend_spec)
    _assert_same("doc-vs-frontend", doc_spec, frontend_spec)
    _assert_same("backend-vs-frontend", backend_spec, frontend_spec)

    print("Contract document appendix matches backend and frontend contract constants.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
