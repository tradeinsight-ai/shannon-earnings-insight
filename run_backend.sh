#!/bin/bash
# Run backend with full console output

echo "Starting Backend (with console output)..."
echo "========================================="
echo ""

cd backend
source .venv/bin/activate 2>/dev/null || true

# Run with full output to console
python -m app.main

# When stopped, deactivate venv
deactivate 2>/dev/null || true
