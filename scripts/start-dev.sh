#!/bin/bash

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "uvicorn.*run_api" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Start backend API (with auto-reload)
echo "Starting backend API on port 8000 (auto-reload enabled)..."
cd "$PROJECT_ROOT"
uv run python run_api.py > /tmp/snowmeth-api.log 2>&1 &
API_PID=$!

# Start frontend (with HMR)
echo "Starting frontend on port 5173 (HMR enabled)..."
cd "$PROJECT_ROOT/frontend"
npm run dev > /tmp/snowmeth-frontend.log 2>&1 &
FRONTEND_PID=$!

# Save PIDs for cleanup
echo $API_PID > /tmp/snowmeth-api.pid
echo $FRONTEND_PID > /tmp/snowmeth-frontend.pid

echo ""
echo "🚀 Development servers started with auto-reload!"
echo "📊 Backend API: http://localhost:8000 (auto-reloads on .py changes)"
echo "🌐 Frontend: http://localhost:5173 (HMR on file changes)"
echo ""
echo "💡 Tip: Leave these running and just edit files - they'll update automatically!"
echo "📋 Logs: tail -f /tmp/snowmeth-{api,frontend}.log"
echo "⏹️  Stop: ./scripts/stop-dev.sh"