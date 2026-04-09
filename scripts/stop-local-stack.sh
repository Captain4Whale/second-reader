#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/local-stack-common.sh"

stop_service "frontend" "$FRONTEND_PIDFILE"
stop_service "backend" "$BACKEND_PIDFILE"
