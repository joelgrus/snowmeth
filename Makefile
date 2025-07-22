.PHONY: help install setup dev start stop status restart test lint format clean build check env-check
.PHONY: docker-build docker-up docker-down docker-logs docker-shell docker-clean

# Default target
help:
	@echo "Snowflake Method - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup     - Complete project setup (install dependencies, check env)"
	@echo "  make install   - Install all dependencies (backend + frontend)"
	@echo "  make env-check - Validate environment setup"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev       - Start development servers (API + frontend)"
	@echo "  make start     - Alias for 'make dev'"
	@echo "  make stop      - Stop development servers"
	@echo "  make restart   - Restart development servers"
	@echo "  make status    - Check development server status"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start containers with docker compose"
	@echo "  make docker-down  - Stop and remove containers"
	@echo "  make docker-logs  - View container logs"
	@echo "  make docker-shell - Open shell in API container"
	@echo "  make docker-clean - Remove images and volumes"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make test      - Run all tests"
	@echo "  make lint      - Run linting checks"
	@echo "  make format    - Format code"
	@echo "  make check     - Run all checks (test + lint + format)"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build     - Build frontend for production"
	@echo "  make clean     - Clean build artifacts and caches"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. Set OPENAI_API_KEY environment variable"
	@echo "  2. Run: make setup"
	@echo "  3. Run: make dev"
	@echo "  4. Visit: http://localhost:5173"
	@echo ""
	@echo "Quick Start (Docker):"
	@echo "  1. Set OPENAI_API_KEY environment variable"
	@echo "  2. Run: make docker-up"
	@echo "  3. Visit: http://localhost:5173"

# Complete project setup
setup: env-check install
	@echo "✅ Setup complete! Run 'make dev' to start development servers"

# Environment validation
env-check:
	@echo "🔍 Checking environment..."
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found. Please install Python 3.11+"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv not found. Install with: pip install uv"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Please install Node.js 18+"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm not found. Please install npm"; exit 1; }
	@if [ -z "$$OPENAI_API_KEY" ]; then echo "⚠️  OPENAI_API_KEY not set. AI features will not work."; fi
	@echo "✅ Environment check passed"

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	uv sync
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Dependencies installed"

# Development server commands
dev start:
	@echo "🚀 Starting development servers..."
	./scripts/start-dev.sh

stop:
	@echo "🛑 Stopping development servers..."
	./scripts/stop-dev.sh

restart:
	@echo "🔄 Restarting development servers..."
	./scripts/restart-dev.sh

status:
	@echo "📊 Checking development server status..."
	./scripts/status-dev.sh

# Code quality commands
test:
	@echo "🧪 Running tests..."
	uv run pytest

lint:
	@echo "🔍 Running linter..."
	uv run ruff check

format:
	@echo "✨ Formatting code..."
	uv run ruff format

check: test lint format
	@echo "✅ All checks passed!"

# Build commands
build:
	@echo "🏗️  Building frontend..."
	cd frontend && npm run build
	@echo "✅ Build complete"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.vite/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker compose build
	@echo "✅ Docker images built"

docker-up:
	@echo "🐳 Starting Docker containers..."
	@if [ -z "$$OPENAI_API_KEY" ]; then echo "❌ OPENAI_API_KEY not set. Set it first!"; exit 1; fi
	docker compose up -d
	@echo "✅ Containers started!"
	@echo "📝 Frontend: http://localhost:5173"
	@echo "📝 API: http://localhost:8000"
	@echo "📝 View logs: make docker-logs"

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker compose down
	@echo "✅ Containers stopped"

docker-logs:
	@echo "📋 Showing container logs (Ctrl+C to exit)..."
	docker compose logs -f

docker-shell:
	@echo "🐚 Opening shell in API container..."
	docker compose exec api /bin/bash

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker compose down -v
	docker rmi snowmeth-api snowmeth-frontend 2>/dev/null || true
	@echo "✅ Docker cleanup complete"

# Development with Docker
docker-dev: docker-up docker-logs

# Run tests in Docker
docker-test:
	@echo "🧪 Running tests in Docker..."
	docker compose exec api uv run pytest

# Run linting in Docker
docker-lint:
	@echo "🔍 Running linter in Docker..."
	docker compose exec api uv run ruff check

# Run formatting in Docker
docker-format:
	@echo "✨ Formatting code in Docker..."
	docker compose exec api uv run ruff format