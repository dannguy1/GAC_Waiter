#!/bin/bash
cd "$(dirname "$0")/.."

# Load Env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${APP_PORT:-3000}

# Start API
if [ -f api.pid ]; then
    echo "Cleaning stale api.pid"
    rm api.pid
fi

echo "Starting Backend API on port $API_PORT..."
nohup ./venv/bin/uvicorn backend.api:app --host 127.0.0.1 --port $API_PORT > api.log 2>&1 &
API_PID=$!
echo $API_PID > api.pid
echo "API started (PID $API_PID)"

# Wait for API to warm up
sleep 5

# Start Next.js Frontend
if [ -f frontend.pid ]; then
    echo "Cleaning stale frontend.pid"
    rm frontend.pid
fi

echo "Starting Next.js Frontend on port $FRONTEND_PORT..."
PORT=$FRONTEND_PORT nohup npm run dev --prefix frontend > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid
echo "Next.js Frontend started (PID $FRONTEND_PID) on port $FRONTEND_PORT"
