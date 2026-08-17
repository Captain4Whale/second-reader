#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/phoenix-common.sh"

phoenix_require_install
phoenix_require_loopback_host
phoenix_cleanup_stale_pidfile

pid="$(phoenix_read_pid)"
if [[ -n "$pid" ]] && phoenix_pid_is_running "$pid"; then
  if phoenix_pid_is_managed "$pid"; then
    echo "Phoenix is already running (pid $pid)."
    "$ROOT_DIR/scripts/status-phoenix.sh"
    exit 0
  fi
  echo "error: $PHOENIX_PIDFILE points to live pid $pid, but it is not this sidecar." >&2
  exit 1
fi

for port in "$PHOENIX_PORT" "$PHOENIX_GRPC_PORT"; do
  if phoenix_port_in_use "$port"; then
    echo "error: Phoenix port $port is already in use by another process." >&2
    lsof -n -P -iTCP:"$port" -sTCP:LISTEN || true
    exit 1
  fi
done

mkdir -p "$PHOENIX_DATA_DIR" "$PHOENIX_RUN_DIR" "$PHOENIX_LOG_DIR"

pid="$($PHOENIX_PYTHON - "$PHOENIX_LOGFILE" "$PHOENIX_BIN" "$PHOENIX_HOST" "$PHOENIX_PORT" "$PHOENIX_GRPC_PORT" "$PHOENIX_DATA_DIR" <<'PY'
import os
import subprocess
import sys

log_path, phoenix_bin, host, port, grpc_port, working_dir = sys.argv[1:]
child_env = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
    "PHOENIX_HOST": host,
    "PHOENIX_PORT": port,
    "PHOENIX_GRPC_PORT": grpc_port,
    "PHOENIX_WORKING_DIR": working_dir,
    "PHOENIX_TELEMETRY_ENABLED": "false",
    "PHOENIX_ALLOW_EXTERNAL_RESOURCES": "false",
    "PHOENIX_ENABLE_MCP_SERVER": "false",
    "PHOENIX_ALLOWED_PROVIDERS": "NONE",
    "PHOENIX_ALLOWED_SANDBOX_PROVIDERS": "NONE",
    "PHOENIX_DISABLE_AGENT_ASSISTANT": "true",
    "PHOENIX_AGENTS_DISABLE_WEB_ACCESS": "true",
    "PHOENIX_AGENTS_DISABLE_BASH": "true",
}
for name in ("HOME", "TMPDIR", "LANG", "LC_ALL", "SSL_CERT_FILE"):
    value = os.environ.get(name)
    if value:
        child_env[name] = value

with open(log_path, "ab", buffering=0) as log_file:
    process = subprocess.Popen(
        [phoenix_bin, "serve"],
        stdin=subprocess.DEVNULL,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        close_fds=True,
        env=child_env,
    )

print(process.pid)
PY
)"
echo "$pid" >"$PHOENIX_PIDFILE"

if phoenix_wait_for_ui 45; then
  echo "Phoenix started (pid $pid)."
  echo "  UI:        $PHOENIX_UI_URL"
  echo "  OTLP HTTP: $PHOENIX_OTLP_HTTP_ENDPOINT"
  echo "  log:       $PHOENIX_LOGFILE"
  exit 0
fi

if phoenix_pid_is_managed "$pid"; then
  kill "$pid" 2>/dev/null || true
fi
rm -f "$PHOENIX_PIDFILE"
echo "error: Phoenix did not become ready within 45 seconds." >&2
tail -n 60 "$PHOENIX_LOGFILE" >&2 || true
exit 1
