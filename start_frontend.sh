#!/bin/bash
set -e

# Get the directory where this script is located
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/frontend"

PORT=5173

echo "[INFO] Starting static server on http://127.0.0.1:$PORT"
echo "[INFO] Press CTRL+C to stop the server."
echo ""

# Start the server
python3 -m http.server $PORT

