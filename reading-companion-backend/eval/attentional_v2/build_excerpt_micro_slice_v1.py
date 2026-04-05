"""Write the ROI-first excerpt micro-slice v1 draft manifest."""

from __future__ import annotations

import json

from .excerpt_micro_slice_v1 import write_manifest


def main() -> int:
    print(json.dumps(write_manifest(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
