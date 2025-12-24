#!/bin/bash
cd "$(dirname "$0")"

echo "Restarting GAC Waiter..."
./stop.sh
sleep 2
./start.sh
