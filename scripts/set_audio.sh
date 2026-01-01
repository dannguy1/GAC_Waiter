#!/bin/bash

# Usage: ./scripts/set_audio.sh [native_on|native_off] [server_on|server_off]

# Function to update .env variable
update_env() {
    local key=$1
    local value=$2
    if grep -q "^$key=" .env; then
        sed -i "s/^$key=.*/$key=$value/" .env
    else
        echo "$key=$value" >> .env
    fi
}

# Parse Arguments
NATIVE_MODE=""
SERVER_MODE=""

if [[ "$1" == "native_on" ]]; then
    update_env "NEXT_PUBLIC_DISABLE_NATIVE_VOICE" "false"
    NATIVE_MODE="ON (Browser)"
elif [[ "$1" == "native_off" ]]; then
    update_env "NEXT_PUBLIC_DISABLE_NATIVE_VOICE" "true"
    NATIVE_MODE="OFF (Browser)"
fi

if [[ "$2" == "server_on" ]]; then
    update_env "ENABLE_SERVER_AUDIO" "true"
    SERVER_MODE="ON (Server)"
elif [[ "$2" == "server_off" ]]; then
    update_env "ENABLE_SERVER_AUDIO" "false"
    SERVER_MODE="OFF (Server)"
fi

if [[ -z "$NATIVE_MODE" && -z "$SERVER_MODE" ]]; then
    echo "Usage: ./scripts/set_audio.sh [native_on|native_off] [server_on|server_off]"
    echo "Example: ./scripts/set_audio.sh native_on server_off"
    exit 1
fi

echo "============================================"
echo "🎧 Audio Configuration Update"
echo "--------------------------------------------"
[[ ! -z "$NATIVE_MODE" ]] && echo "Native Voice: $NATIVE_MODE"
[[ ! -z "$SERVER_MODE" ]] && echo "Server Audio: $SERVER_MODE"
echo "============================================"

# 1. Stop Everything (Force Kill to prevent Zombies)
echo "🛑 Stopping services (Force Kill)..."
pkill -f "uvicorn" || true
# Kill Next.js server on port 8501 explicitly
fuser -k 8501/tcp > /dev/null 2>&1 || true
# Kill any remaining node processes for this project
pkill -f "next-server" || true

# 2. Clean Cache (Crucial for NEXT_PUBLIC variables)
echo "🧹 Cleaning build cache..."
rm -rf frontend/.next

# 3. Restart
echo "🚀 Restarting..."
./scripts/start.sh

echo "✅ Done! Audio settings applied."
