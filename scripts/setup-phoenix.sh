#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/phoenix-common.sh"

BOOTSTRAP_PYTHON="$(phoenix_bootstrap_python)"

mkdir -p "$PHOENIX_DATA_DIR" "$PHOENIX_RUN_DIR" "$PHOENIX_LOG_DIR"

if [[ -d "$PHOENIX_VENV_DIR" && ! -x "$PHOENIX_PYTHON" ]]; then
  echo "error: $PHOENIX_VENV_DIR exists but is not a usable virtualenv." >&2
  echo "Move the damaged directory aside, then rerun 'make setup-phoenix'." >&2
  exit 1
fi


if [[ -x "$PHOENIX_PYTHON" ]] && ! phoenix_python_is_supported "$PHOENIX_PYTHON"; then
  echo "error: $PHOENIX_VENV_DIR uses an unsupported Python interpreter." >&2
  echo "Phoenix 20.2.1 requires Python >=3.12,<3.15 for this launcher." >&2
  echo "Move the existing virtualenv aside, then rerun 'make setup-phoenix'." >&2
  exit 1
fi

if [[ ! -x "$PHOENIX_PYTHON" ]]; then
  echo "Creating isolated Phoenix virtualenv at $PHOENIX_VENV_DIR ..."
  "$BOOTSTRAP_PYTHON" -m venv "$PHOENIX_VENV_DIR"
fi

installed_version="$(phoenix_installed_version || true)"
if [[ "$installed_version" == "$PHOENIX_SERVER_VERSION" && -x "$PHOENIX_BIN" ]]; then
  echo "Phoenix $PHOENIX_SERVER_VERSION is already installed."
else
  echo "Installing pinned Phoenix server $PHOENIX_SERVER_VERSION ..."
  "$PHOENIX_PYTHON" -m pip install --upgrade pip
  "$PHOENIX_PYTHON" -m pip install --upgrade "arize-phoenix==$PHOENIX_SERVER_VERSION"
fi

installed_version="$(phoenix_installed_version || true)"
if [[ "$installed_version" != "$PHOENIX_SERVER_VERSION" || ! -x "$PHOENIX_BIN" ]]; then
  echo "error: Phoenix installation verification failed." >&2
  exit 1
fi

echo "Phoenix sidecar setup complete."
echo "  version: $installed_version"
echo "  state:   $PHOENIX_STATE_DIR"
echo "Start it explicitly with 'make start-phoenix'."
