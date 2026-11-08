#!/usr/bin/env python3
"""Explicitly recover the original private few-shot from existing local Git history."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from src.prompts.releases import PRIVATE_ASSETS


def restore(ref):
    source = subprocess.run(["git", "-C", str(BACKEND), "show", f"{ref}:reading-companion-backend/src/attentional_v2/prompts/digest.py"], check=True, capture_output=True, text=True).stdout
    lock = json.loads((BACKEND / "src/attentional_v2/prompts/versions/published.json").read_text())
    expected = set(lock["private_assets"])
    recovered = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str) or "# Examples" not in node.value:
            continue
        raw = node.value[node.value.index("# Examples"):].encode()
        digest = hashlib.sha256(raw).hexdigest()
        if digest not in expected:
            continue
        PRIVATE_ASSETS.mkdir(parents=True, exist_ok=True)
        path = PRIVATE_ASSETS / f"{digest}.txt"
        if path.exists() and path.read_bytes() != raw:
            raise ValueError(f"Conflicting private asset: {path}")
        path.write_bytes(raw)
        recovered.add(digest)
    if recovered != expected:
        raise ValueError("Selected local Git revision does not contain all required exact examples; use a private backup")
    print(f"Restored {len(recovered)} SHA-256 verified private asset(s); no network used")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-ref", required=True)
    restore(parser.parse_args().legacy_ref)
