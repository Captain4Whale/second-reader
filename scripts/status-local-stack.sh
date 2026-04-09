#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/local-stack-common.sh"

show_service_status "backend" "$BACKEND_PIDFILE" "$DEFAULT_BACKEND_PORT" "http://localhost:${DEFAULT_BACKEND_PORT}/api/health"
show_service_status "frontend" "$FRONTEND_PIDFILE" "$DEFAULT_FRONTEND_PORT" "http://localhost:${DEFAULT_FRONTEND_PORT}"
