.PHONY: help install dev test lint format clean docker-build docker-up deploy

# Default target
help:
	@echo "JobFinder Pro - Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install all dependencies"
	@echo "  make dev             Start development environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make lint            Run linting checks"
	@echo "  make format          Auto-format code"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         Run database migrations"
	@echo "  make migrate-create  Create new migration"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    Build Docker images"
	@echo "  make docker-up       Start services with Docker Compose"
	@echo "  make docker-down     Stop Docker services"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-k8s      Deploy to Kubernetes with Helm"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           Remove build artifacts"
	@echo "  make export          Export project as ZIP"

# Installation
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Installation complete!"

# Development
dev:
	@echo "🚀 Starting development environment..."
	./scripts/dev_start.sh

# Testing
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=api --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

# Linting
lint:
	@echo "🔍 Running linters..."
	black --check api/
	isort --check-only api/
	flake8 api/ --max-line-length=100
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	black api/
	isort api/
	cd frontend && npm run format

# Database
migrate:
	@echo "📊 Running database migrations..."
	alembic upgrade head

migrate-create:
	@read -p "Migration name: " name; \
	alembic revision -m "$$name"

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker build -f docker/Dockerfile.api -t jobfinder/api:latest .
	docker build -f docker/Dockerfile.frontend -t jobfinder/frontend:latest .

docker-up:
	@echo "🐳 Starting Docker services..."
	cd docker && docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:5000"

docker-down:
	@echo "🐳 Stopping Docker services..."
	cd docker && docker-compose down

docker-logs:
	cd docker && docker-compose logs -f

# Deployment
deploy-k8s:
	@echo "☸️  Deploying to Kubernetes..."
	helm upgrade --install jobfinder-pro ./k8s/helm \
		--namespace production \
		--create-namespace \
		--wait

# Utilities
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf frontend/.next frontend/node_modules/.cache
	@echo "✅ Cleanup complete!"

export:
	@echo "📦 Exporting project..."
	python scripts/export_zip.py

# CLI utilities
admin-create:
	@echo "👤 Creating admin user..."
	python scripts/cli.py create-admin

stats:
	@echo "📊 Database statistics..."
	python scripts/cli.py stats

# Quick start for new developers
quickstart: install migrate
	@echo ""
	@echo "✅ Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env and configure"
	@echo "2. Run 'make dev' to start development server"
	@echo "3. Access frontend at http://localhost:3000"
