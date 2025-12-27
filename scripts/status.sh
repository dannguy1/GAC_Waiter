#!/bin/bash
# scripts/status.sh
cd "$(dirname "$0")/.."

echo "=== GAC Waiter Status ==="

# Check API
if [ -f api.pid ]; then
    PID=$(cat api.pid)
    if ps -p $PID > /dev/null; then
        echo "Backend API:  RUNNING (PID $PID)"
    else
        echo "Backend API:  STOPPED (Stale PID file)"
    fi
else
    echo "Backend API:  STOPPED"
fi

# Check Next.js
if [ -f frontend.pid ]; then
    PID=$(cat frontend.pid)
    if ps -p $PID > /dev/null; then
        echo "Next.js UI:   RUNNING (PID $PID)"
    else
        echo "Next.js UI:   STOPPED (Stale PID file)"
    fi
else
    echo "Next.js UI:   STOPPED"
fi
