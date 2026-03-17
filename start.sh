#!/usr/bin/env bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting backend..."
bash "$ROOT/backend/start-backend.sh" &
BACKEND_PID=$!

echo "Starting frontend..."
bash "$ROOT/frontend/start-frontend.sh" &
FRONTEND_PID=$!

# Trap Ctrl+C and kill both processes
trap "echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait $BACKEND_PID $FRONTEND_PID
