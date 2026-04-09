#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

"$ROOT_DIR/scripts/start-backend-detached.sh"
"$ROOT_DIR/scripts/start-frontend-detached.sh"
"$ROOT_DIR/scripts/status-local-stack.sh"
