#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Kill the React dev server on exit (Ctrl+C or script termination)
cleanup() {
    echo ""
    echo "Stopping frontend server..."
    # Kill all processes on port 3000
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    elif command -v netstat >/dev/null 2>&1; then
        # Windows Git Bash / MSYS2
        netstat -ano | grep ':3000 ' | grep 'LISTENING' | awk '{print $5}' | sort -u | while read pid; do
            taskkill //F //PID "$pid" 2>/dev/null || true
        done
    fi
    # Kill any background jobs from this script
    kill $(jobs -p) 2>/dev/null || true
    echo "Frontend server stopped."
}
trap cleanup EXIT INT TERM

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting frontend server..."
npm start
