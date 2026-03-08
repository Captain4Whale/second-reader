#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "error: frontend dependencies missing. Run 'make setup' first."
  exit 1
fi

require_backend_venv

BACKEND_PORT="${BACKEND_PORT:-8010}"
FRONTEND_PORT="${FRONTEND_PORT:-4173}"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
API_BASE_URL="http://${BACKEND_HOST}:${BACKEND_PORT}"
WS_BASE_URL="ws://${BACKEND_HOST}:${BACKEND_PORT}"
TMP_DIR="$(mktemp -d)"
RUNTIME_ROOT="$TMP_DIR/runtime"
BACKEND_LOG="$TMP_DIR/backend.log"
FRONTEND_LOG="$TMP_DIR/frontend.log"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT

if port_in_use "$BACKEND_PORT"; then
  echo "error: backend E2E port $BACKEND_PORT is already in use."
  exit 1
fi

if port_in_use "$FRONTEND_PORT"; then
  echo "error: frontend E2E port $FRONTEND_PORT is already in use."
  exit 1
fi

wait_for_url() {
  local url="$1"
  local label="$2"
  local attempts=0
  until curl -fsS "$url" >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [[ "$attempts" -ge 60 ]]; then
      echo "error: timed out waiting for $label at $url"
      echo "--- backend log ---"
      [[ -f "$BACKEND_LOG" ]] && tail -n 100 "$BACKEND_LOG" || true
      echo "--- frontend log ---"
      [[ -f "$FRONTEND_LOG" ]] && tail -n 100 "$FRONTEND_LOG" || true
      exit 1
    fi
    sleep 1
  done
}

echo "Starting backend E2E fixture server..."
(
  export BACKEND_TEST_MODE=1
  export BACKEND_TEST_FIXTURE_PROFILE=e2e
  export BACKEND_RUNTIME_ROOT="$RUNTIME_ROOT"
  export BACKEND_CORS_ORIGINS="http://127.0.0.1:${FRONTEND_PORT}"
  export BACKEND_HOST="$BACKEND_HOST"
  export BACKEND_PORT="$BACKEND_PORT"
  ./scripts/dev-backend.sh
) >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "Starting frontend E2E server..."
(
  export BACKEND_PORT="$BACKEND_PORT"
  export FRONTEND_PORT="$FRONTEND_PORT"
  export VITE_API_BASE_URL="$API_BASE_URL"
  export VITE_WS_BASE_URL="$WS_BASE_URL"
  ./scripts/dev-frontend.sh
) >"$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

wait_for_url "${API_BASE_URL}/docs" "backend"
wait_for_url "http://127.0.0.1:${FRONTEND_PORT}" "frontend"

echo "Ensuring Playwright browser is installed..."
(cd "$FRONTEND_DIR" && npx playwright install chromium >/dev/null)

echo "Running Playwright E2E suite..."
(
  cd "$FRONTEND_DIR"
  export PLAYWRIGHT_BASE_URL="http://127.0.0.1:${FRONTEND_PORT}"
  npm run e2e
)
