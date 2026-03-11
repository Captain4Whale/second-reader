#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_backend_venv

"$BACKEND_DIR/.venv/bin/python" "$ROOT_DIR/scripts/backfill-covers.py"
