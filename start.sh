#!/usr/bin/env bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

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
    echo "Shutting down..."
    kill_port 3000
    kill_port 8000
    echo "All servers stopped."
}
trap cleanup EXIT

echo "Starting backend..."
bash "$ROOT/backend/start-backend.sh" &

echo "Starting frontend..."
bash "$ROOT/frontend/start-frontend.sh" &

wait
