#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/local-stack-common.sh"

require_backend_python
require_backend_venv

ensure_port_available_for_service "backend" "$DEFAULT_BACKEND_PORT" "$BACKEND_PIDFILE"
start_detached_service \
  "backend" \
  "$BACKEND_PIDFILE" \
  "$BACKEND_LOGFILE" \
  "http://localhost:${DEFAULT_BACKEND_PORT}/api/health" \
  45 \
  "$ROOT_DIR/scripts/run-backend-stable.sh" demo
