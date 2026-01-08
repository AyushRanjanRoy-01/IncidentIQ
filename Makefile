.PHONY: help setup-local run-backend run-frontend test lint format clean deploy-dev deploy-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup-local: ## Setup local development environment
	@echo "Setting up local development environment..."
	@cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements-dev.txt
	@cd frontend && npm install
	@cp .env.example .env
	@echo "Local setup complete! Don't forget to configure .env file"

run-backend: ## Run backend development server
	@cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run frontend development server
	@cd frontend && npm run dev

run-workers: ## Run background workers
	@cd backend && . venv/bin/activate && dramatiq app.workers.metric_ingestor

test: ## Run all tests
	@cd backend && . venv/bin/activate && pytest
	@cd frontend && npm run test

test-backend: ## Run backend tests
	@cd backend && . venv/bin/activate && pytest

test-frontend: ## Run frontend tests
	@cd frontend && npm run test

lint: ## Lint code
	@cd backend && . venv/bin/activate && ruff check . && mypy app
	@cd frontend && npm run lint

format: ## Format code
	@cd backend && . venv/bin/activate && black . && ruff check --fix .
	@cd frontend && npm run format

clean: ## Clean build artifacts
	@find . -type d -name __pycache__ -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf backend/.mypy_cache backend/.ruff_cache backend/.pytest_cache
	@rm -rf frontend/node_modules frontend/dist frontend/.vite
	@rm -rf .coverage htmlcov

docker-build: ## Build Docker images
	@docker-compose build

docker-up: ## Start Docker containers
	@docker-compose up -d

docker-down: ## Stop Docker containers
	@docker-compose down

docker-logs: ## View Docker logs
	@docker-compose logs -f

deploy-dev: ## Deploy to development environment
	@echo "Deploying to development..."
	@cd infra/terraform/environments/dev && terraform init && terraform apply

deploy-prod: ## Deploy to production environment (requires confirmation)
	@echo "Deploying to production..."
	@cd infra/terraform/environments/prod && terraform init && terraform apply

install-pre-commit: ## Install pre-commit hooks
	@cd backend && . venv/bin/activate && pre-commit install

migrate: ## Run database migrations
	@cd backend && . venv/bin/activate && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="description")
	@cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(MESSAGE)"

seed-knowledge: ## Seed knowledge base with sample data
	@cd backend && . venv/bin/activate && python scripts/seed_knowledge.py

simulate-alerts: ## Simulate alerts for testing
	@cd backend && . venv/bin/activate && python scripts/simulate_alerts.py

