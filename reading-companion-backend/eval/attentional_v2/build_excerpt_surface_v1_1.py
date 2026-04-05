"""Build the excerpt surface v1.1 draft artifacts."""

from __future__ import annotations

import argparse
import json

from .excerpt_surface_v1_1 import DEFAULT_RUN_ID, write_draft_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            write_draft_artifacts(
                run_id=str(args.run_id).strip() or DEFAULT_RUN_ID,
                overwrite=not bool(args.no_overwrite),
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
