#!/bin/bash

echo "=========================================="
echo "Starting Senalign Full Stack"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -d "app" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY is not set!"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ OPENAI_API_KEY is set"
fi

echo ""
echo "📦 Installing frontend dependencies (if needed)..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "🚀 Starting backend on http://localhost:8000"
echo "🌐 Starting frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd ..
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
