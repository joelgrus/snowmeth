#!/bin/bash

echo "Stopping development servers..."

# Kill by PID if available
if [ -f /tmp/snowmeth-api.pid ]; then
    API_PID=$(cat /tmp/snowmeth-api.pid)
    echo "Stopping backend API (PID: $API_PID)..."
    kill $API_PID 2>/dev/null || true
    rm -f /tmp/snowmeth-api.pid
fi

if [ -f /tmp/snowmeth-frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/snowmeth-frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f /tmp/snowmeth-frontend.pid
fi

# Fallback: kill by process name
pkill -f "uvicorn.*run_api" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "✅ Servers stopped"