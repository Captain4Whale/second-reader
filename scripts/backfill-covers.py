#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "reading-companion-backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.iterator_reader.parse import backfill_missing_epub_covers


def main() -> int:
    results = backfill_missing_epub_covers(BACKEND_DIR)
    if not results:
        print("No book manifests found under output/.")
        return 0

    updated = 0
    for result in results:
        status = str(result.get("status", "unknown"))
        if status in {"updated", "refreshed", "manifest_synced"}:
            updated += 1
        cover = result.get("cover_image_url") or "-"
        print(f"{result.get('book_id', 'unknown')}: {status} ({cover})")

    print(f"Processed {len(results)} book(s); updated {updated}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
