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
    echo "Stopping frontend server..."
    kill_port 3000
    echo "Frontend server stopped."
}
trap cleanup EXIT

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting frontend server..."
npm start
