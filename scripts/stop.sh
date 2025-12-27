#!/bin/bash
cd "$(dirname "$0")/.."

# Stop Next.js Frontend
if [ -f frontend.pid ]; then
    PID=$(cat frontend.pid)
    echo "Stopping Next.js Frontend (PID: $PID)..."
    kill $PID 2>/dev/null
    rm frontend.pid
else
    # Fallback to pkill
    pkill -f "next-server" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
fi

# Stop Backend
if [ -f api.pid ]; then
    PID=$(cat api.pid)
    echo "Stopping Backend (PID: $PID)..."
    kill $PID 2>/dev/null
    rm api.pid
else
    echo "No api.pid found. Attempting pkill..."
    pkill -f "uvicorn backend.api:app"
fi

echo "All services stopped."
