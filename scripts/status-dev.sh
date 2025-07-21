#!/bin/bash

echo "🔍 Development Server Status"
echo "=========================="

# Check API
if curl -s http://localhost:8001/api/stories >/dev/null 2>&1; then
    echo "✅ Backend API (port 8001): RUNNING"
else
    echo "❌ Backend API (port 8001): NOT RUNNING"
fi

# Check Frontend
if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo "✅ Frontend (port 5173): RUNNING"
else
    echo "❌ Frontend (port 5173): NOT RUNNING"
fi

echo ""
echo "📊 Process Details:"
echo "Backend processes:"
ps aux | grep -E "(uvicorn|run_api)" | grep -v grep || echo "  None running"

echo ""
echo "Frontend processes:"
ps aux | grep vite | grep -v grep || echo "  None running"

echo ""
echo "🌐 URLs:"
echo "   Backend: http://localhost:8001"
echo "   Frontend: http://localhost:5173"