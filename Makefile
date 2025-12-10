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

# List of jewelry modules
JEWELRY_MODULES=jewelry_base,jewelry_partner,jewelry_pawn,jewelry_product,jewelry_purchase_client,jewelry_report

# Update specific module(s)
# Usage: make update m=module_name
update:
	docker compose exec odoo python -m odoo -d narim_erp_db -u $(m) --stop-after-init
	docker compose restart odoo

# Update all jewelry modules
update-jewelry:
	docker compose exec odoo python -m odoo -d narim_erp_db -u $(JEWELRY_MODULES) --stop-after-init
	docker compose restart odoo
