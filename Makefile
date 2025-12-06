.PHONY: up down restart logs build rebuild clean

# Start containers
up:
	docker compose up -d

# Stop containers
down:
	docker compose down

# Restart containers
restart:
	docker compose down
	docker compose up -d

# View Odoo logs
logs:
	docker compose logs -f odoo

# Build containers
build:
	docker compose build

# Rebuild without cache
rebuild:
	docker compose build --no-cache
	docker compose up -d
