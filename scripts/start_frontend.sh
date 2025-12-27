#!/bin/bash
# scripts/start_frontend.sh

PROJECT_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
# export PATH="$PROJECT_ROOT/tools/node-v20.11.0-linux-x64/bin:$PATH"

cd "$PROJECT_ROOT/frontend"
echo "Starting Next.js Frontend on port 3000..."
# Use system npm
npm run dev
