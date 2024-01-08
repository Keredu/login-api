# Configuration for database container
DB_CONTAINER_NAME = backendPostgresDB
DB_PORT = 5432
DB_NAME = postgresDB
DB_USER = postgresUser
DB_PASSWORD = postgresPW

# Configuration for application container
API_CONTAINER_NAME = backendFastAPI
NETWORK_NAME = login-network
API_COMMAND = bash -c "uvicorn api.main:app --host 0.0.0.0 --reload"

# Default target
all: run

# Primary target to run the application
run: create-network run-db run-api

# Target for running the application in development mode
dev:
	@$(MAKE) run API_COMMAND=bash
# "bash -c 'while true; do sleep 30; done'"

create-network:
	@echo "Checking if Docker network $(NETWORK_NAME) exists..."
	@docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || \
	(echo "Creating Docker network $(NETWORK_NAME)..." && docker network create $(NETWORK_NAME))

# Target to manage the database container
run-db: create-network
	@if [ -n "$$(docker ps -aq -f name=^/$(DB_CONTAINER_NAME)$$)" ]; then \
		echo "Container $(DB_CONTAINER_NAME) exists."; \
		output=$$(docker start $(DB_CONTAINER_NAME) 2>&1); \
		status=$$?; \
		if [ $$status -ne 0 ]; then \
			echo $$output; \
			echo "Failed to start container $(DB_CONTAINER_NAME), aborting..."; \
			exit $$status; \
		fi; \
	else \
		echo "Container $(DB_CONTAINER_NAME) does not exist. Creating and starting it now..."; \
		output=$$(docker run --name $(DB_CONTAINER_NAME) --network $(NETWORK_NAME) -p $(DB_PORT):5432 -e POSTGRES_USER=$(DB_USER) -e POSTGRES_PASSWORD=$(DB_PASSWORD) -e POSTGRES_DB=$(DB_NAME) -d postgres 2>&1); \
		status=$$?; \
		if [ $$status -ne 0 ]; then \
			echo $$output; \
			echo "Failed to create and start container $(DB_CONTAINER_NAME), aborting..."; \
			exit $$status; \
		fi; \
	fi; \
	echo "Waiting for container $(DB_CONTAINER_NAME) to be ready..."; \
	while ! docker exec $(DB_CONTAINER_NAME) pg_isready -h localhost -p 5432 > /dev/null 2>&1; do \
		sleep 1; \
	done; \
	echo "Container $(DB_CONTAINER_NAME) is ready."

run-api:
	chmod +x entrypoint.sh
	docker build -t my-custom-image \
				 --build-arg ENTRYPOINT_PATH=./entrypoint.sh \
				 --build-arg ENV_PATH=./.env \
				 -f ./Dockerfile .

	docker run -it --rm \
			   --name $(API_CONTAINER_NAME) \
			   --network $(NETWORK_NAME) \
			   -e POSTGRES_HOST=$(DB_CONTAINER_NAME) \
			   -e POSTGRES_PORT=$(DB_PORT) \
			   -e POSTGRES_DB=$(DB_NAME) \
			   -e POSTGRES_USER=$(DB_USER) \
			   -e POSTGRES_PASSWORD=$(DB_PASSWORD) \
			   -p 8000:8000 \
			   -v ./api:/app/api \
			   -v ./test:/app/test \
			   my-custom-image $(API_COMMAND)


# Target to run tests
test:
	@$(MAKE) run API_COMMAND="bash -c 'python -m pytest -v ./test/'"

# Target to clean up resources
clean:
	@echo "Stopping and removing containers..."
	-docker stop $(API_CONTAINER_NAME)
	-docker rm $(API_CONTAINER_NAME)
	-docker stop $(DB_CONTAINER_NAME)
	-docker rm $(DB_CONTAINER_NAME)
	@echo "\nRemoving Docker network..."
	-docker network rm $(NETWORK_NAME)
	@echo "\nCleanup complete."

# Declare phony targets
.PHONY: all run run-api test clean dev