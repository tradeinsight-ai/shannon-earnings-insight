#!/bin/bash
# Watch backend logs with color and filtering

echo "======================================"
echo "Backend Logs (Live)"
echo "======================================"
echo "Watching: backend.log"
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

# Check if log exists
if [ ! -f backend.log ]; then
    echo "⚠️  backend.log not found"
    echo "Waiting for backend to start..."
    touch backend.log
fi

# Tail with color highlighting for different log levels
tail -f backend.log | while IFS= read -r line; do
    # Color code based on log level
    if echo "$line" | grep -q "ERROR"; then
        echo -e "\033[0;31m$line\033[0m"  # Red
    elif echo "$line" | grep -q "WARNING\|WARN"; then
        echo -e "\033[0;33m$line\033[0m"  # Yellow
    elif echo "$line" | grep -q "INFO"; then
        echo -e "\033[0;36m$line\033[0m"  # Cyan
    elif echo "$line" | grep -q "DEBUG"; then
        echo -e "\033[0;90m$line\033[0m"  # Gray
    else
        echo "$line"
    fi
done
