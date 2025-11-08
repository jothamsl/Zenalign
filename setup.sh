#!/bin/bash

# Senalign Setup Script
# Sets up MongoDB via Docker and starts the application

set -e

echo "🚀 Senalign Setup"
echo "=================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Start MongoDB
echo "📦 Starting MongoDB container..."
docker compose up -d mongodb

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 5

# Check MongoDB health
if docker compose ps mongodb | grep -q "healthy\|running"; then
    echo "✅ MongoDB is running"
else
    echo "⚠️  MongoDB may still be starting up. Check with: docker compose logs mongodb"
fi

echo ""
echo "📊 MongoDB Connection Info:"
echo "   Host: localhost"
echo "   Port: 27017"
echo "   Database: senalign"
echo "   URI: mongodb://localhost:27017/senalign"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys (if not done already):"
echo "     OPENAI_API_KEY=your_key_here"
echo "     EXA_API_KEY=your_key_here"
echo ""
echo "  2. Start the application:"
echo "     source venv/bin/activate"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  3. Run tests:"
echo "     pytest app/tests/ -v"
echo ""
echo "  4. Stop MongoDB when done:"
echo "     docker compose down"
echo ""
