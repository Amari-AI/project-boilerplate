# Shipment Document Processor Makefile

.PHONY: help install dev dev-backend dev-frontend down build test clean docker-build docker-up docker-down docker-logs docker-clean docker-restart docker-ps

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Local Development:"
	@echo "  install        - Install all dependencies (Python and Node.js)"
	@echo "  dev            - Run both backend and frontend in development mode"
	@echo "  dev-backend    - Run only the FastAPI backend server"
	@echo "  dev-frontend   - Run only the React frontend server"
	@echo "  down           - Stop all running development servers"
	@echo "  build          - Build the React frontend for production"
	@echo "  test           - Run Python tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-file      - Run specific test file (use FILE=filename)"
	@echo "  test-marker    - Run tests with specific marker (use MARKER=name)"
	@echo "  clean          - Clean build artifacts and temporary files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start application using Docker Compose"
	@echo "  docker-down    - Stop and remove Docker containers"
	@echo "  docker-logs    - View Docker container logs"
	@echo "  docker-clean   - Clean up Docker images and containers"

# Install all dependencies
install:
	@echo "Installing Python dependencies..."
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	cd app/frontend && npm install
	@echo "All dependencies installed!"

# Run both backend and frontend concurrently
dev:
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"
	@make -j2 dev-backend dev-frontend

# Run backend server
dev-backend:
	@echo "Starting FastAPI backend server on http://localhost:8000"
	cd app && \
	PYTHONPATH=.. \
	ANTHROPIC_API_KEY=$(shell cat .env | grep ANTHROPIC_API_KEY | cut -d'=' -f2) \
	../venv/bin/python -m app.main

# Run frontend server
dev-frontend:
	@echo "Starting React frontend server on http://localhost:3000"
	cd app/frontend && npm start

# Stop all development servers
down:
	@echo "Stopping all development servers..."
	@pkill -f "uvicorn.*app.main" || echo "Backend server not running"
	@pkill -f "python.*app.main" || echo "No Python backend processes found"  
	@pkill -f "react-scripts start" || echo "Frontend server not running"
	@pkill -f "node.*react-scripts.*start" || echo "No additional React processes found"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No processes on port 8000"
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No processes on port 3000"
	@echo "All servers stopped!"

# Build frontend for production
build:
	@echo "Building React frontend for production..."
	cd app/frontend && npm run build
	@echo "Frontend built successfully!"

# Run Python tests
test:
	@echo "Running Python tests..."
	./venv/bin/python -m pytest tests/ -v
	@echo "Tests completed!"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	./venv/bin/python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=test_api_routes.py"
	@if [ -z "$(FILE)" ]; then echo "Please specify FILE=<test_file>"; exit 1; fi
	./venv/bin/python -m pytest tests/$(FILE) -v

# Run tests with specific marker
test-marker:
	@echo "Usage: make test-marker MARKER=api"
	@if [ -z "$(MARKER)" ]; then echo "Please specify MARKER=<marker_name>"; exit 1; fi
	./venv/bin/python -m pytest tests/ -m $(MARKER) -v

# Run tests in parallel
test-parallel:
	@echo "Running tests in parallel..."
	./venv/bin/python -m pytest tests/ -v -n auto

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf app/frontend/build
	rm -rf app/frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed!"

# Quick test of the API endpoint
test-api:
	@echo "Testing API endpoint..."
	curl -f http://localhost:8000/ || echo "Backend server not running. Start with 'make dev-backend'"

# Install only Python dependencies
install-python:
	@echo "Installing Python dependencies..."
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

# Install only Node.js dependencies  
install-frontend:
	@echo "Installing Node.js dependencies..."
	cd app/frontend && npm install

# ===== DOCKER COMMANDS =====

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose build --no-cache
	@echo "Docker images built successfully!"

# Start application with Docker
docker-up:
	@echo "Starting application with Docker Compose..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	docker-compose up -d
	@echo "Application started! Use 'make docker-logs' to view logs."

# Stop Docker containers
docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Docker containers stopped!"

# View Docker logs
docker-logs:
	@echo "Viewing Docker container logs (Ctrl+C to exit)..."
	docker-compose logs -f

# Clean up Docker resources
docker-clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f
	@echo "Docker cleanup completed!"

# Restart Docker services
docker-restart:
	@echo "Restarting Docker services..."
	docker-compose restart
	@echo "Docker services restarted!"

# View running Docker containers
docker-ps:
	@echo "Running Docker containers:"
	docker-compose ps