# AI Negotiation Arena — Makefile
# ============================================================================

.PHONY: help install dev test build run docker-up docker-down clean

help:
	@echo "AI Negotiation Arena — Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install         Install all dependencies (backend + frontend)"
	@echo "  make install-backend Install only backend dependencies"
	@echo "  make install-front   Install only frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev-backend     Run backend in development mode"
	@echo "  make dev-front       Run frontend in development mode"
	@echo "  make dev             Run both backend and frontend"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-backend    Run backend tests"
	@echo "  make test-watch      Run tests in watch mode"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up       Start all services with Docker Compose"
	@echo "  make docker-down     Stop all Docker services"
	@echo "  make docker-build    Build all Docker images"
	@echo ""
	@echo "Quality:"
	@echo "  make lint            Run linters (ruff for Python)"
	@echo "  make format          Format code (black for Python)"
	@echo "  make clean           Clean temporary files"
	@echo ""

# ── Installation ──────────────────────────────────────────────────────────

install: install-backend install-front

install-backend:
	cd backend && pip install -r requirements.txt

install-front:
	cd frontend && npm install

# ── Development ────────────────────────────────────────────────────────────

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-front:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@trap 'kill 0' EXIT; \
		$(MAKE) dev-backend & \
		$(MAKE) dev-front & \
		wait

# ── Testing ────────────────────────────────────────────────────────────────

test-backend:
	cd backend && python -m pytest -v --cov=app --cov-report=term-missing

test-watch:
	cd backend && ptw -- --cov=app

test: test-backend

# ── Docker ─────────────────────────────────────────────────────────────────

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-clean:
	docker compose down -v

# ── Quality ────────────────────────────────────────────────────────────────

lint:
	cd backend && ruff check app/
	cd backend && mypy app/ --ignore-missing-imports

format:
	cd backend && black app/ tests/

# ── Cleanup ────────────────────────────────────────────────────────────────

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf frontend/.next