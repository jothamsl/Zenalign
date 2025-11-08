#!/bin/bash

# Quick start script - starts MongoDB and the Senalign server

set -e

echo "🚀 Starting Senalign..."
echo ""

# Start MongoDB
echo "📦 Starting MongoDB..."
docker compose up -d mongodb

# Wait for MongoDB
echo "⏳ Waiting for MongoDB (5 seconds)..."
sleep 5

# Activate venv
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

# Start the server
echo "🌐 Starting Senalign server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
