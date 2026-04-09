#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/local-stack-common.sh"

if ! command -v npm >/dev/null 2>&1; then
  echo "error: npm is required."
  exit 1
fi

ensure_port_available_for_service "frontend" "$DEFAULT_FRONTEND_PORT" "$FRONTEND_PIDFILE"
start_detached_service \
  "frontend" \
  "$FRONTEND_PIDFILE" \
  "$FRONTEND_LOGFILE" \
  "http://localhost:${DEFAULT_FRONTEND_PORT}" \
  45 \
  "$ROOT_DIR/scripts/dev-frontend.sh"
