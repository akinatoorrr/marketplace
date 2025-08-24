SERVICE_NAME=fastapi


CONTAINER_NAME=$(shell docker compose ps -q $(SERVICE_NAME))

.PHONY: tests build up down shell

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

shell:
	docker exec -it $(CONTAINER_NAME) bash

tests:
	docker compose run --rm $(SERVICE_NAME) pytest -v --tb=short --maxfail=1

test-cov:
	docker compose run --rm $(SERVICE_NAME) pytest --cov=src tests/
