#!/bin/bash
set -e

# Get the directory where this script is located
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] Launching TaskTrack backend and frontend in separate Terminal windows..."

# Open backend in a new Terminal window
osascript -e "tell application \"Terminal\" to do script \"cd '$ROOT' && bash start_backend.sh\""

# Wait a moment for the first window to open
sleep 1

# Open frontend in another new Terminal window
osascript -e "tell application \"Terminal\" to do script \"cd '$ROOT' && bash start_frontend.sh\""

echo "[INFO] Servers are starting in separate Terminal windows."
echo "[INFO] You can close this window if you don't need it anymore."

