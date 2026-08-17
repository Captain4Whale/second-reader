#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

PHOENIX_SERVER_VERSION="20.2.1"
PHOENIX_STATE_DIR="$BACKEND_DIR/state/phoenix"
PHOENIX_VENV_DIR="$PHOENIX_STATE_DIR/venv"
PHOENIX_DATA_DIR="$PHOENIX_STATE_DIR/data"
PHOENIX_RUN_DIR="$PHOENIX_STATE_DIR/run"
PHOENIX_LOG_DIR="$PHOENIX_STATE_DIR/logs"
PHOENIX_PIDFILE="$PHOENIX_RUN_DIR/phoenix.pid"
PHOENIX_LOGFILE="$PHOENIX_LOG_DIR/phoenix.log"
PHOENIX_PYTHON="$PHOENIX_VENV_DIR/bin/python"
PHOENIX_BIN="$PHOENIX_VENV_DIR/bin/phoenix"
PHOENIX_HOST="${PHOENIX_HOST:-127.0.0.1}"
PHOENIX_PORT="${PHOENIX_PORT:-6006}"
PHOENIX_GRPC_PORT="${PHOENIX_GRPC_PORT:-4317}"
PHOENIX_UI_URL="http://${PHOENIX_HOST}:${PHOENIX_PORT}"
PHOENIX_OTLP_HTTP_ENDPOINT="${PHOENIX_UI_URL}/v1/traces"

phoenix_python_is_supported() {
  local python_bin="$1"
  "$python_bin" -c 'import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 15) else 1)' \
    >/dev/null 2>&1
}

phoenix_bootstrap_python() {
  local candidate

  if [[ -n "${PHOENIX_SETUP_PYTHON:-}" ]]; then
    candidate="$PHOENIX_SETUP_PYTHON"
    if [[ ! -x "$candidate" ]] || ! phoenix_python_is_supported "$candidate"; then
      echo "error: PHOENIX_SETUP_PYTHON must point to Python >=3.12,<3.15." >&2
      return 1
    fi
    printf '%s\n' "$candidate"
    return 0
  fi

  for candidate in python3.12 python3.13 python3.14; do
    if command -v "$candidate" >/dev/null 2>&1; then
      candidate="$(command -v "$candidate")"
      if phoenix_python_is_supported "$candidate"; then
        printf '%s\n' "$candidate"
        return 0
      fi
    fi
  done

  echo "error: Phoenix 20.2.1 needs a sidecar Python >=3.12,<3.15." >&2
  echo "Install Python 3.12 (for example, 'brew install python@3.12') or set PHOENIX_SETUP_PYTHON." >&2
  return 1
}

phoenix_read_pid() {
  if [[ -f "$PHOENIX_PIDFILE" ]]; then
    tr -d '[:space:]' <"$PHOENIX_PIDFILE"
  fi
}

phoenix_pid_is_running() {
  local pid="${1:-}"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

phoenix_pid_is_managed() {
  local pid="${1:-}"
  local command_line

  if ! phoenix_pid_is_running "$pid"; then
    return 1
  fi
  command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  [[ "$command_line" == *"$PHOENIX_BIN"* && "$command_line" == *" serve"* ]]
}

phoenix_cleanup_stale_pidfile() {
  local pid
  pid="$(phoenix_read_pid)"
  if [[ -n "$pid" ]] && ! phoenix_pid_is_running "$pid"; then
    rm -f "$PHOENIX_PIDFILE"
  fi
}

phoenix_installed_version() {
  if [[ ! -x "$PHOENIX_PYTHON" ]]; then
    return 1
  fi
  "$PHOENIX_PYTHON" -c 'from importlib.metadata import version; print(version("arize-phoenix"))' 2>/dev/null
}

phoenix_require_install() {
  local installed_version

  if [[ ! -x "$PHOENIX_PYTHON" || ! -x "$PHOENIX_BIN" ]]; then
    echo "error: Phoenix sidecar is not installed. Run 'make setup-phoenix' first." >&2
    exit 1
  fi

  if ! phoenix_python_is_supported "$PHOENIX_PYTHON"; then
    echo "error: the Phoenix sidecar virtualenv must use Python >=3.12,<3.15." >&2
    echo "Move $PHOENIX_VENV_DIR aside, then rerun 'make setup-phoenix'." >&2
    exit 1
  fi

  installed_version="$(phoenix_installed_version || true)"
  if [[ "$installed_version" != "$PHOENIX_SERVER_VERSION" ]]; then
    echo "error: expected arize-phoenix $PHOENIX_SERVER_VERSION, found ${installed_version:-unknown}." >&2
    echo "Run 'make setup-phoenix' to restore the pinned sidecar version." >&2
    exit 1
  fi
}

phoenix_require_loopback_host() {
  case "$PHOENIX_HOST" in
    127.0.0.1|localhost)
      ;;
    *)
      echo "error: the repo-local Phoenix sidecar must bind to 127.0.0.1 or localhost." >&2
      echo "Authentication is intentionally not configured for this local-only launcher." >&2
      exit 1
      ;;
  esac
}

phoenix_port_in_use() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -n -P -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi
  return 1
}

phoenix_wait_for_ui() {
  local timeout_seconds="$1"
  local start_ts now_ts

  start_ts="$(date +%s)"
  while true; do
    if curl -fsS --max-time 2 "$PHOENIX_UI_URL" >/dev/null 2>&1; then
      return 0
    fi

    now_ts="$(date +%s)"
    if (( now_ts - start_ts >= timeout_seconds )); then
      return 1
    fi
    sleep 1
  done
}
