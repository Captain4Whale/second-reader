#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/phoenix-common.sh"

phoenix_cleanup_stale_pidfile
pid="$(phoenix_read_pid)"

if [[ -z "$pid" ]]; then
  echo "Phoenix is not running under the repo-local sidecar manager."
  exit 0
fi

if ! phoenix_pid_is_running "$pid"; then
  rm -f "$PHOENIX_PIDFILE"
  echo "Phoenix was already stopped."
  exit 0
fi

if ! phoenix_pid_is_managed "$pid"; then
  echo "error: refusing to stop pid $pid because it is not the repo-local Phoenix sidecar." >&2
  exit 1
fi

kill "$pid"
waited=0
while phoenix_pid_is_running "$pid" && (( waited < 15 )); do
  sleep 1
  ((waited += 1))
done

if phoenix_pid_is_running "$pid"; then
  echo "error: Phoenix did not stop within 15 seconds; inspect pid $pid and $PHOENIX_LOGFILE." >&2
  exit 1
fi

rm -f "$PHOENIX_PIDFILE"
echo "Phoenix stopped. Persistent data remains under $PHOENIX_DATA_DIR."
