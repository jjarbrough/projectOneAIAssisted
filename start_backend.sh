#!/bin/bash
set -e

# Get the directory where this script is located
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "[INFO] Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "[INFO] Ensuring backend dependencies are installed..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""
echo "[INFO] Starting FastAPI server on http://127.0.0.1:8000"
echo "[INFO] Press CTRL+C to stop the server."
echo ""

# Start the server
uvicorn app.main:app --reload

