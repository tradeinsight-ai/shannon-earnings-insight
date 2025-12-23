#!/bin/bash
# View backend and frontend logs in real-time

echo "======================================"
echo "earningsInsight Live Logs"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop viewing"
echo ""
echo "======================================"
echo ""

# Check if logs exist
if [ ! -f backend.log ]; then
    echo "⚠️  backend.log not found. Is the server running?"
    echo "   Run ./start_dev.sh first"
    exit 1
fi

# Tail both logs with labels
tail -f backend.log frontend.log
