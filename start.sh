#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/start.log"
VENV_DIR="$SCRIPT_DIR/.venv"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Clear previous log
> "$LOG_FILE"

log "=== Starting Elastic A2A Demo ==="

# Create venv if it doesn't exist or is broken
if [ ! -x "$VENV_DIR/bin/python" ]; then
  log "Creating virtual environment..."
  rm -rf "$VENV_DIR"
  python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
fi

log "Installing dependencies..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
log "Dependencies installed."

# Launch connectivity test
log "Running connectivity test..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/elastic-simple-a2a-connectivity-test.py" >> "$LOG_FILE" 2>&1 &
CONN_PID=$!
log "Connectivity test started (PID: $CONN_PID)"

# Launch chat UI
log "Starting chat UI..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/app.py" >> "$LOG_FILE" 2>&1 &
UI_PID=$!
log "Chat UI started (PID: $UI_PID)"

# Load UI_PORT for the status message
if [ -f "$SCRIPT_DIR/variables.env" ]; then
  UI_PORT=$(grep -E '^UI_PORT=' "$SCRIPT_DIR/variables.env" | cut -d= -f2)
fi
UI_PORT="${UI_PORT:-8089}"

log "=== All apps running ==="
log "Chat UI: http://localhost:$UI_PORT"
log "Logs: $LOG_FILE"
log "PIDs: connectivity-test=$CONN_PID, chat-ui=$UI_PID"
log "To stop: kill $CONN_PID $UI_PID"

wait
