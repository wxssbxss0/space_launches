# Variables
COMPOSE = docker-compose
API_SERVICE = api

.PHONY: all build up down logs test

all: build up

# Build the Docker images for API and Worker
build:
	$(COMPOSE) build

# Start Redis, API, and Worker in detached mode
up:
	$(COMPOSE) up -d

# Stop and remove all containers, networks, and volumes
down:
	$(COMPOSE) down

# Tail logs for all services
logs:
	$(COMPOSE) logs -f

# Run the test suite against a live Redis container
test:
	@echo "Starting Redis for tests..."
	$(COMPOSE) up -d redis
	@echo "Running pytest inside API container..."
	$(COMPOSE) run --rm $(API_SERVICE) pytest
	@echo "Tearing down test containers..."
	$(COMPOSE) down
