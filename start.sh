#!/usr/bin/env bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo ""
    echo "Shutting down..."
    # Kill the child script process groups (kills their children too)
    kill -- -$BACKEND_PID 2>/dev/null || kill $BACKEND_PID 2>/dev/null
    kill -- -$FRONTEND_PID 2>/dev/null || kill $FRONTEND_PID 2>/dev/null

    # Also kill anything left on the ports (Windows + Unix)
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ano | grep ':8000 ' | grep 'LISTENING' | awk '{print $5}' | sort -u | while read pid; do
            taskkill //F //PID "$pid" 2>/dev/null || true
        done
        netstat -ano | grep ':3000 ' | grep 'LISTENING' | awk '{print $5}' | sort -u | while read pid; do
            taskkill //F //PID "$pid" 2>/dev/null || true
        done
    fi

    echo "All servers stopped."
    exit 0
}

trap cleanup INT TERM EXIT

echo "Starting backend..."
bash "$ROOT/backend/start-backend.sh" &
BACKEND_PID=$!

echo "Starting frontend..."
bash "$ROOT/frontend/start-frontend.sh" &
FRONTEND_PID=$!

wait $BACKEND_PID $FRONTEND_PID
