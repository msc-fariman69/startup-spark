#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

VENV_DIR=".venv-mac"
VENV_PYTHON="${VENV_DIR}/bin/python"

pause_on_error() {
  echo
  read -r -p "Press Enter to close this window..." _
}

fail() {
  echo "$1"
  pause_on_error
  exit 1
}

escape_for_applescript() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

start_terminal_window() {
  local title="$1"
  local command="$2"
  local escaped_command

  escaped_command=$(escape_for_applescript "printf '\033]0;${title}\007'; ${command}")
  osascript -e "tell application \"Terminal\" to do script \"${escaped_command}\"" >/dev/null
}

find_python() {
  local candidate

  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done

  return 1
}

ensure_agent_env() {
  local env_file="startup_spark_agent/.env"
  local env_example="startup_spark_agent/.env.example"

  if [ ! -f "$env_file" ]; then
    if [ -f "$env_example" ]; then
      cp "$env_example" "$env_file"
      echo "[StartupSpark] Created ${env_file} from ${env_example}."
    else
      fail "[StartupSpark] Missing ${env_file}. Create it and set GOOGLE_API_KEY."
    fi
  fi

  if ! grep -Eq '^GOOGLE_API_KEY=.+$' "$env_file" || grep -Eq '^GOOGLE_API_KEY=(your-api-key-here)?$' "$env_file"; then
    fail "[StartupSpark] Missing Google API key. Edit startup_spark_agent/.env and set GOOGLE_API_KEY to your real key."
  fi
}

ensure_agent_env

if [ ! -x "$VENV_PYTHON" ]; then
  echo "[StartupSpark] Missing macOS virtual environment. Creating ${VENV_DIR} now..."
  PYTHON_BIN=$(find_python) || fail "[StartupSpark] Python 3.10 or newer is required. Install it from https://www.python.org/downloads/ or with Homebrew: brew install python"
  "$PYTHON_BIN" -m venv "$VENV_DIR" || fail "[StartupSpark] Failed to create ${VENV_DIR}."
fi

"$VENV_PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1 || fail "[StartupSpark] ${VENV_DIR} uses Python older than 3.10. Delete ${VENV_DIR}, install Python 3.10+, then run this script again."

echo "[StartupSpark] Installing Python dependencies..."
"$VENV_PYTHON" -m pip install -r requirements.txt || fail "[StartupSpark] Failed to install root Python dependencies."

if [ -f "api/requirements.txt" ]; then
  "$VENV_PYTHON" -m pip install -r api/requirements.txt || fail "[StartupSpark] Failed to install API Python dependencies."
fi

if [ ! -d "ui/node_modules" ]; then
  echo "[StartupSpark] Missing ui/node_modules. Installing frontend dependencies..."
  command -v npm >/dev/null 2>&1 || fail "[StartupSpark] npm is required but was not found. Install Node.js from https://nodejs.org/ or with Homebrew: brew install node"
  (
    cd ui
    npm install
  ) || fail "[StartupSpark] npm install failed."
fi

api_port_pid=$(lsof -nP -iTCP:8001 -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)
if [ -n "$api_port_pid" ]; then
  api_port_name=$(ps -p "$api_port_pid" -o comm= 2>/dev/null || echo "unknown")
  echo "[StartupSpark] Port 8001 is in use by PID ${api_port_pid} (${api_port_name})."
  fail "[StartupSpark] Port 8001 is already in use. Stop the existing API server, then run this script again."
fi

ui_port_pid=$(lsof -nP -iTCP:5173 -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)
if [ -n "$ui_port_pid" ]; then
  ui_port_name=$(ps -p "$ui_port_pid" -o comm= 2>/dev/null || echo "unknown")
  echo "[StartupSpark] Port 5173 is in use by PID ${ui_port_pid} (${ui_port_name})."
  fail "[StartupSpark] Port 5173 is already in use. Stop the existing UI server, then run this script again."
fi

command -v npm >/dev/null 2>&1 || fail "[StartupSpark] npm is required but was not found. Install Node.js from https://nodejs.org/ or with Homebrew: brew install node"

project_dir=$(pwd)
project_dir_escaped=$(printf '%q' "$project_dir")

echo "[StartupSpark] Starting FastAPI backend on http://127.0.0.1:8001"
start_terminal_window "StartupSpark API" "cd ${project_dir_escaped} && ./${VENV_DIR}/bin/python -m uvicorn api.main:app --reload --port 8001"

echo "[StartupSpark] Starting React UI on http://localhost:5173"
start_terminal_window "StartupSpark UI" "cd ${project_dir_escaped}/ui && npm run dev -- --strictPort"

echo
echo "StartupSpark is starting."
echo "API: http://127.0.0.1:8001"
echo "UI:  http://localhost:5173"
echo
echo "Close the two opened terminal windows to stop the servers."
