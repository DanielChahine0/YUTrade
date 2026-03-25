#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

kill_port() {
    local port=$1
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        powershell -Command "Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>/dev/null || true
    else
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
}

cleanup() {
    echo ""
    echo "Stopping backend server..."
    kill_port 8000
    echo "Backend server stopped."
}
trap cleanup EXIT

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
