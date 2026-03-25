#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Kill the uvicorn server on exit (Ctrl+C or script termination)
cleanup() {
    echo ""
    echo "Stopping backend server..."
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ano | grep ':8000 ' | grep 'LISTENING' | awk '{print $5}' | sort -u | while read pid; do
            taskkill //F //PID "$pid" 2>/dev/null || true
        done
    fi
    kill $(jobs -p) 2>/dev/null || true
    echo "Backend server stopped."
}
trap cleanup EXIT INT TERM

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv 2>/dev/null || python -m venv venv
fi

# Activate virtual environment (works on both macOS/Linux and Windows Git Bash)
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please update .env with your settings before running again."
fi

# Ensure uploads directory exists
mkdir -p uploads

echo "Starting backend server..."
uvicorn app.main:app --reload
