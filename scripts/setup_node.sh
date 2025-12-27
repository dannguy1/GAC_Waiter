#!/bin/bash
# scripts/setup_node.sh
# Installs Node.js locally in tools/ directory

NODE_VERSION="v20.11.0"
NODE_DIST="node-$NODE_VERSION-linux-x64"
URL="https://nodejs.org/dist/$NODE_VERSION/$NODE_DIST.tar.xz"
PROJECT_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
INSTALL_DIR="$PROJECT_ROOT/tools"

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d "$NODE_DIST" ]; then
    echo "Downloading Node.js $NODE_VERSION..."
    wget -q --show-progress "$URL"
    echo "Extracting..."
    tar -xf "$NODE_DIST.tar.xz"
    rm "$NODE_DIST.tar.xz"
else
    echo "Node.js already installed."
fi

BIN_DIR="$INSTALL_DIR/$NODE_DIST/bin"
echo "Node.js bin: $BIN_DIR"
export PATH="$BIN_DIR:$PATH"

node --version
npm --version
