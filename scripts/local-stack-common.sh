#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

LOCAL_STACK_DIR="$BACKEND_DIR/state/local_stack"
BACKEND_PIDFILE="$LOCAL_STACK_DIR/backend.pid"
FRONTEND_PIDFILE="$LOCAL_STACK_DIR/frontend.pid"
BACKEND_LOGFILE="$LOCAL_STACK_DIR/backend.log"
FRONTEND_LOGFILE="$LOCAL_STACK_DIR/frontend.log"

mkdir -p "$LOCAL_STACK_DIR"

read_pidfile() {
  local pidfile="$1"
  if [[ -f "$pidfile" ]]; then
    tr -d '[:space:]' <"$pidfile"
  fi
}

pid_is_running() {
  local pid="${1:-}"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

cleanup_stale_pidfile() {
  local pidfile="$1"
  local pid
  pid="$(read_pidfile "$pidfile")"
  if [[ -n "$pid" ]] && ! pid_is_running "$pid"; then
    rm -f "$pidfile"
  fi
}

ensure_port_available_for_service() {
  local name="$1"
  local port="$2"
  local pidfile="$3"
  local pid

  cleanup_stale_pidfile "$pidfile"
  pid="$(read_pidfile "$pidfile")"

  if port_in_use "$port"; then
    if [[ -n "$pid" ]] && pid_is_running "$pid"; then
      return 0
    fi

    echo "error: $name port $port is already in use by another process." >&2
    lsof -n -P -iTCP:"$port" -sTCP:LISTEN || true
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local timeout_seconds="$2"
  local start_ts now_ts

  start_ts="$(date +%s)"
  while true; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi

    now_ts="$(date +%s)"
    if (( now_ts - start_ts >= timeout_seconds )); then
      return 1
    fi
    sleep 1
  done
}

start_detached_service() {
  local name="$1"
  local pidfile="$2"
  local logfile="$3"
  local ready_url="$4"
  local timeout_seconds="$5"
  shift 5

  local pid

  cleanup_stale_pidfile "$pidfile"
  pid="$(read_pidfile "$pidfile")"
  if [[ -n "$pid" ]] && pid_is_running "$pid"; then
    echo "$name already running (pid $pid)."
    return 0
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 is required to launch detached services." >&2
    exit 1
  fi

  pid="$(
    python3 - "$logfile" "$@" <<'PY'
import subprocess
import sys

log_path = sys.argv[1]
command = sys.argv[2:]

with open(log_path, "ab", buffering=0) as log_file:
    proc = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        close_fds=True,
    )

print(proc.pid)
PY
  )"
  echo "$pid" >"$pidfile"

  if wait_for_http "$ready_url" "$timeout_seconds"; then
    echo "$name started (pid $pid)."
    return 0
  fi

  if pid_is_running "$pid"; then
    echo "error: $name did not become ready in ${timeout_seconds}s." >&2
    tail -n 40 "$logfile" >&2 || true
    exit 1
  fi

  rm -f "$pidfile"
  echo "error: $name exited before it became ready." >&2
  tail -n 40 "$logfile" >&2 || true
  exit 1
}

stop_service() {
  local name="$1"
  local pidfile="$2"
  local pid
  local waited=0

  cleanup_stale_pidfile "$pidfile"
  pid="$(read_pidfile "$pidfile")"

  if [[ -z "$pid" ]]; then
    echo "$name is not managed by the detached local stack."
    return 0
  fi

  if ! pid_is_running "$pid"; then
    rm -f "$pidfile"
    echo "$name was already stopped."
    return 0
  fi

  kill "$pid"
  while pid_is_running "$pid" && (( waited < 15 )); do
    sleep 1
    ((waited += 1))
  done

  if pid_is_running "$pid"; then
    echo "error: $name did not stop within 15s; stop it manually if needed (pid $pid)." >&2
    exit 1
  fi

  rm -f "$pidfile"
  echo "$name stopped."
}

show_service_status() {
  local name="$1"
  local pidfile="$2"
  local port="$3"
  local url="$4"
  local pid status health

  cleanup_stale_pidfile "$pidfile"
  pid="$(read_pidfile "$pidfile")"

  if [[ -n "$pid" ]] && pid_is_running "$pid"; then
    status="running"
  else
    status="stopped"
    pid="-"
  fi

  if curl -fsS "$url" >/dev/null 2>&1; then
    health="ready"
  elif port_in_use "$port"; then
    health="port-listening"
  else
    health="down"
  fi

  printf '%-10s status=%-8s pid=%-8s port=%-5s health=%s\n' "$name" "$status" "$pid" "$port" "$health"
}
