#!/bin/bash

echo "🔄 Restarting development servers..."
./scripts/stop-dev.sh
sleep 2
./scripts/start-dev.sh