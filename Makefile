# Shipment Document Processor Makefile

.PHONY: help install dev dev-backend dev-frontend down build test clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install all dependencies (Python and Node.js)"
	@echo "  dev            - Run both backend and frontend in development mode"
	@echo "  dev-backend    - Run only the FastAPI backend server"
	@echo "  dev-frontend   - Run only the React frontend server"
	@echo "  down           - Stop all running development servers"
	@echo "  build          - Build the React frontend for production"
	@echo "  test           - Run Python tests"
	@echo "  clean          - Clean build artifacts and temporary files"

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