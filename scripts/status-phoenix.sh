#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/phoenix-common.sh"

installed_version="$(phoenix_installed_version || true)"
if [[ -z "$installed_version" || ! -x "$PHOENIX_BIN" ]]; then
  status="not-installed"
elif [[ "$installed_version" != "$PHOENIX_SERVER_VERSION" ]]; then
  status="version-mismatch"
else
  status="stopped"
fi

phoenix_cleanup_stale_pidfile
pid="$(phoenix_read_pid)"
health="down"

if [[ -n "$pid" ]] && phoenix_pid_is_running "$pid"; then
  if phoenix_pid_is_managed "$pid"; then
    status="running"
  else
    status="unmanaged-pid"
  fi
fi

if curl -fsS --max-time 2 "$PHOENIX_UI_URL" >/dev/null 2>&1; then
  health="ready"
elif phoenix_port_in_use "$PHOENIX_PORT"; then
  health="port-listening"
fi

printf 'phoenix status=%s pid=%s version=%s ui_health=%s\n' \
  "$status" "${pid:--}" "${installed_version:-not-installed}" "$health"
echo "  expected version: $PHOENIX_SERVER_VERSION"
echo "  UI:               $PHOENIX_UI_URL"
echo "  OTLP HTTP:        $PHOENIX_OTLP_HTTP_ENDPOINT"
echo "  state:            $PHOENIX_STATE_DIR"
