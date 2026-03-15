#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Running backend tests..."
python -m pytest tests/ -v
