#!/bin/bash

# Stop script - stops the Senalign server and MongoDB

echo "🛑 Stopping Senalign..."
echo ""

# Stop Docker containers
echo "📦 Stopping MongoDB..."
docker compose down

echo "✅ All services stopped"
echo ""
echo "To remove MongoDB data volumes, run:"
echo "  docker compose down -v"
