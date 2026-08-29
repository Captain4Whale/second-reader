#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_backend_venv

echo "Checking Reading Product schemas, examples, semantics, and runtime copy..."
"$BACKEND_DIR/.venv/bin/python" "$ROOT_DIR/scripts/check_reading_product_contract.py"

echo "Checking unified GitHub Pages contract projection..."
"$BACKEND_DIR/.venv/bin/python" "$ROOT_DIR/scripts/build_contract_pages.py" --check
