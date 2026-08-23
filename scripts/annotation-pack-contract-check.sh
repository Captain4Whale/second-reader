#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_backend_venv

echo "Checking Annotation Pack generated bindings and runtime schemas..."
(cd "$BACKEND_DIR" && .venv/bin/python scripts/generate_annotation_pack_bindings.py --check)

echo "Checking Annotation Pack contract examples..."
(cd "$BACKEND_DIR" && .venv/bin/python scripts/validate_annotation_pack.py --schema-only ../contract/annotation-pack/v0/examples/*.json)

echo "Checking Annotation Pack Tiny Reader golden fixture..."
(cd "$BACKEND_DIR" && .venv/bin/python tests/annotation_pack/fixtures/tiny-reader/build_fixture.py --check)

echo "Checking Annotation Pack contract tests..."
(cd "$BACKEND_DIR" && .venv/bin/pytest tests/annotation_pack/test_contract.py -q)

echo "Checking Annotation Pack GitHub Pages projection..."
"$BACKEND_DIR/.venv/bin/python" "$ROOT_DIR/scripts/build_annotation_pack_pages.py" --check
