#!/usr/bin/env python3
"""Check immutable published prompt files, including private examples."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.prompts.integrity import check_published

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Trusted pre-change commit; CI should supply its PR base",
    )
    args = parser.parse_args()
    result = check_published(args.base_ref)
    print(f"Verified {len(result['releases'])} immutable prompt releases")
