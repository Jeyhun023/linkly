.PHONY: up down logs destroy migrate sh help

help:
	@echo "Available commands:"
	@echo "  make up       - Start all containers"
	@echo "  make down     - Stop all containers"
	@echo "  make logs     - Show container logs (follow mode)"
	@echo "  make destroy  - Stop containers and remove volumes"
	@echo "  make migrate  - Run database migrations"
	@echo "  make sh       - Open shell in API container"
	@echo "  make help     - Show this help message"

up:
	docker compose up -d

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f

destroy:
	docker compose down -v

migrate:
	docker compose exec api alembic upgrade head

sh:
	docker compose exec api sh
