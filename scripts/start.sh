#!/bin/bash
cd "$(dirname "$0")/.."

# Load Env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

APP_PORT=${APP_PORT:-8501}
APP_HOST=${APP_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}

# Start API
if [ -f api.pid ]; then
    echo "Cleaning stale api.pid"
    rm api.pid
fi

echo "Starting Backend API on port $API_PORT..."
nohup uvicorn backend.api:app --host 0.0.0.0 --port $API_PORT > api.log 2>&1 &
API_PID=$!
echo $API_PID > api.pid
echo "API started (PID $API_PID)"

# Wait for API to warm up
sleep 5

# Start Frontend
if [ -f app.pid ]; then
    echo "Cleaning stale app.pid"
    rm app.pid
fi

echo "Starting Frontend UI on $APP_HOST:$APP_PORT..."
nohup streamlit run app.py --server.port $APP_PORT --server.address $APP_HOST > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid
echo "Frontend started (PID $APP_PID)"
