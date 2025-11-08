.PHONY: help setup start stop test test-db clean install docker-up docker-down docker-logs

help:
	@echo "Senalign - Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup & Run:"
	@echo "  make setup      - Complete setup (Docker + Python)"
	@echo "  make start      - Start MongoDB and API server"
	@echo "  make stop       - Stop all services"
	@echo ""
	@echo "Development:"
	@echo "  make test       - Run all tests"
	@echo "  make test-db    - Test MongoDB connection"
	@echo "  make install    - Install Python dependencies"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start MongoDB container"
	@echo "  make docker-down  - Stop MongoDB container"
	@echo "  make docker-logs  - View MongoDB logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove temp files and cache"

setup:
	@./setup.sh

start:
	@./start.sh

stop:
	@./stop.sh

test:
	@echo "Running tests..."
	@. venv/bin/activate && pytest app/tests/ -v

test-db:
	@echo "Testing MongoDB connection..."
	@. venv/bin/activate && python test_mongodb.py

install:
	@echo "Installing dependencies..."
	@. venv/bin/activate && pip install -q -r requirements.txt
	@echo "✅ Dependencies installed"

docker-up:
	@echo "Starting MongoDB..."
	@docker compose up -d mongodb
	@echo "⏳ Waiting for MongoDB to be ready..."
	@sleep 5
	@echo "✅ MongoDB is running"

docker-down:
	@echo "Stopping MongoDB..."
	@docker compose down

docker-logs:
	@docker compose logs -f mongodb

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf temp/*.csv temp/*.json 2>/dev/null || true
	@echo "✅ Cleanup complete"
