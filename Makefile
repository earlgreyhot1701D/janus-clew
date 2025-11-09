.PHONY: help install dev dev-backend dev-frontend test format lint clean demo

help:
	@echo "🧵 Janus Clew - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev          Start both servers (in background)"
	@echo "  make dev-backend  Start FastAPI backend"
	@echo "  make dev-frontend Start React frontend"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         Run pytest with coverage"
	@echo "  make format       Format code (black + isort)"
	@echo "  make lint         Check code quality"
	@echo ""
	@echo "CLI:"
	@echo "  make cli          Run CLI: janus-clew analyze [repos]"
	@echo "  make demo         Show demo usage"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove cache and build files"

install:
	python3.11 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install && cd ..
	@echo "✅ Dependencies installed"

dev: dev-backend dev-frontend
	@echo ""
	@echo "✅ Both servers started"
	@echo "Backend: http://localhost:3000"
	@echo "Frontend: http://localhost:5173"

dev-backend:
	@echo "Starting FastAPI backend on http://localhost:3000..."
	python -m backend

dev-frontend:
	@echo "Starting React frontend on http://localhost:5173..."
	cd frontend && npm run dev

test:
	python -m pytest tests/ -v --cov=cli --cov=backend --cov-report=term-missing

format:
	black .
	isort .
	@echo "✅ Code formatted"

lint:
	black --check .
	isort --check .
	@echo "✅ Code quality check passed"

cli:
	python -m cli

demo:
	@echo "Demo: Analyze three sample repositories"
	@echo "Run: janus-clew analyze ~/Your-Honor ~/Ariadne-Clew ~/TicketGlass"
	@echo ""
	@echo "Status: Check stored analyses"
	@echo "Run: janus-clew status"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	@echo "✅ Cleaned up"

.DEFAULT_GOAL := help
