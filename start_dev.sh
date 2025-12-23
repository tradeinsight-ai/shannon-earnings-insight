#!/bin/bash
# Start both backend and frontend for development

echo "Starting earningsInsight Development Environment"
echo "==============================================="
echo ""

# Check if backend is already running and stop it
BACKEND_CHECK=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_CHECK" ]; then
    echo "⚠️  Backend already running on port 8000 (PID: $BACKEND_CHECK)"
    echo "   Stopping existing backend..."
    kill -9 $BACKEND_CHECK 2>/dev/null
    sleep 1
    echo "   ✅ Stopped"
fi

# Check if frontend is already running and stop it
FRONTEND_CHECK=$(lsof -ti:5173 2>/dev/null)
if [ ! -z "$FRONTEND_CHECK" ]; then
    echo "⚠️  Frontend already running on port 5173 (PID: $FRONTEND_CHECK)"
    echo "   Stopping existing frontend..."
    kill -9 $FRONTEND_CHECK 2>/dev/null
    sleep 1
    echo "   ✅ Stopped"
fi

# Kill any orphaned processes
if pgrep -f "python -m app.main" > /dev/null; then
    echo "🧹 Cleaning up orphaned Python processes..."
    pkill -9 -f "python -m app.main"
    sleep 1
fi

if pgrep -f "npm run dev" > /dev/null; then
    echo "🧹 Cleaning up orphaned npm processes..."
    pkill -9 -f "npm run dev"
    sleep 1
fi

echo ""

# Start backend
echo "🚀 Starting Backend (FastAPI)..."
cd backend
source .venv/bin/activate 2>/dev/null || true
python -m app.main > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Logs: backend.log"

echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
done

echo ""

# Start frontend
echo "🚀 Starting Frontend (SvelteKit)..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Frontend URL: http://localhost:5173"
echo "   Logs: frontend.log"

echo ""
echo "==============================================="
echo "✨ Development environment is running!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "==============================================="

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
