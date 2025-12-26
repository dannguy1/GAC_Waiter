#!/bin/bash
cd "$(dirname "$0")/.."

# Stop Frontend
if [ -f app.pid ]; then
    PID=$(cat app.pid)
    echo "Stopping Frontend (PID: $PID)..."
    kill $PID 2>/dev/null
    rm app.pid
else
    echo "No app.pid found. Attempting pkill..."
    pkill -f "streamlit run app.py"
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
