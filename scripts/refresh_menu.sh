#!/bin/bash
# scripts/refresh_menu.sh
# Refreshes the active menu data and triggers a hot-reload in the backend.

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

# 1. Sync data-original/menu.json -> data/menu.json
if [ -f "data-original/menu.json" ]; then
    echo "Syncing data-original/menu.json to data/menu.json..."
    cp data-original/menu.json data/menu.json
else
    echo "Warning: data-original/menu.json not found. Skipping sync."
fi

# 2. Get Port from .env
API_PORT=8000
if [ -f .env ]; then
    # Extract API_PORT from .env, handling potential spaces/comments
    ENV_PORT=$(grep "^API_PORT" .env | cut -d '=' -f2 | tr -d ' "')
    if [ ! -z "$ENV_PORT" ]; then
        API_PORT=$ENV_PORT
    fi
fi

# 3. Call Reload Endpoint
echo "Triggering backend reload at http://localhost:$API_PORT/v1/reload..."
RESPONSE=$(curl -s -X POST "http://localhost:$API_PORT/v1/reload")

echo "Response: $RESPONSE"

if [[ $RESPONSE == *"success"* ]]; then
    echo "✅ Menu reloaded successfully!"
else
    echo "❌ Failed to reload menu. Check backend logs."
fi
