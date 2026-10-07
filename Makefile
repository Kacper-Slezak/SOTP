# Makefile for SOTP project - Docker-First Version
# Run `make` or `make help` to display available commands.

# Variables
DOCKER_COMPOSE_DEV = docker-compose --env-file .env -f infrastructure/docker/docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker-compose --env-file .env -f infrastructure/docker/docker-compose.prod.yml

.PHONY: help dev up down logs shell-backend shell-frontend test setup build push deploy clean seed

help:
	@echo "Available commands for SOTP project (Docker-First mode):"
	@echo ""
	@echo "--- Core (Docker Dev) ---"
	@echo "  make dev           -> Starts full development environment in background (alias for 'up')."
	@echo "  make up            -> Builds and starts development containers in background."
	@echo "  make down          -> Stops and removes development containers."
	@echo "  make logs          -> Streams logs from all running containers."
	@echo "  make shell-backend -> Opens a shell (bash) inside the backend container."
	@echo "  make shell-frontend-> Opens a shell (sh) inside the frontend container."
	@echo "  make test          -> Runs backend tests (pytest) inside the container."
	@echo ""
	@echo "--- Database (Demo) ---"
	@echo "  make seed          -> Seeds database with demo data (users, devices)."
	@echo ""
	@echo "--- Production & Deployment ---"
	@echo "  make build         -> Builds production Docker images."
	@echo "  make push          -> Pushes built images to container registry."
	@echo "  make deploy        -> Simulates application deployment on server."
	@echo ""
	@echo "--- Utilities & Maintenance ---"
	@echo "  make clean         -> Stops containers and removes all data volumes."
	@echo "  make setup         -> (Local) Installs dependencies in local venv/npm."

# === Core Section (Docker Dev) ===
dev: up

up:
	@echo "Starting full Docker development environment..."
	$(DOCKER_COMPOSE_DEV) up --build -d

down:
	@echo "Stopping Docker development environment..."
	$(DOCKER_COMPOSE_DEV) down

logs:
	@echo "Streaming logs for all services... (Press Ctrl+C to exit)"
	$(DOCKER_COMPOSE_DEV) logs -f

shell-backend:
	@echo "Opening shell in backend container..."
	$(DOCKER_COMPOSE_DEV) exec backend bash

shell-frontend:
	@echo "Opening shell in frontend container..."
	$(DOCKER_COMPOSE_DEV) exec frontend sh

test:
	@echo "Running backend tests inside Docker container..."
	$(DOCKER_COMPOSE_DEV) exec backend pytest

# === Database Section ===
seed:
	@echo "Seeding database with demo data..."
	$(DOCKER_COMPOSE_DEV) exec backend python scripts/seed-demo-data.py --clean

# === Production & Deployment Section ===
build:
	@echo "Building production Docker images..."
	$(DOCKER_COMPOSE_PROD) build

push:
	@echo "Pushing images to repository..."
	$(DOCKER_COMPOSE_PROD) push

deploy:
	@echo "Deploying application to server..."
	@echo "On a production server this command would run: docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d"

# === Utilities & Maintenance Section ===
clean:
	@echo "Stopping containers and removing all data (volumes)..."
	$(DOCKER_COMPOSE_DEV) down -v

# === Local Development Section (venv) ===
setup:
	@echo "(Local) Installing backend dependencies in venv..."
	(cd apps/core_backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt)
	@echo "(Local) Installing frontend dependencies with npm..."
	(cd apps/web_frontend && npm install)
	@echo "Local setup completed."
