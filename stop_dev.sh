#!/bin/bash
# Stop all development servers for earningsInsight

echo "Stopping earningsInsight Development Servers..."
echo "=============================================="

# Stop backend (port 8000)
BACKEND_PIDS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "🛑 Stopping Backend (port 8000)..."
    kill -9 $BACKEND_PIDS 2>/dev/null
    sleep 1
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️  Backend not running on port 8000"
fi

# Stop frontend (port 5173)
FRONTEND_PIDS=$(lsof -ti:5173 2>/dev/null)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "🛑 Stopping Frontend (port 5173)..."
    kill -9 $FRONTEND_PIDS 2>/dev/null
    sleep 1
    echo "   ✅ Frontend stopped"
else
    echo "   ℹ️  Frontend not running on port 5173"
fi

# Also kill any Python processes running app.main
if pgrep -f "python -m app.main" > /dev/null; then
    echo "🛑 Stopping any remaining Python processes..."
    pkill -f "python -m app.main"
    echo "   ✅ Python processes stopped"
fi

# Also kill any npm dev processes
if pgrep -f "npm run dev" > /dev/null; then
    echo "🛑 Stopping any remaining npm processes..."
    pkill -f "npm run dev"
    echo "   ✅ npm processes stopped"
fi

echo ""
echo "=============================================="
echo "✨ All servers stopped successfully!"
echo "=============================================="
