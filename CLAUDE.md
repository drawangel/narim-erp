# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NarimERP is an Odoo 18 Community Edition deployment for a jewelry chain (IAN OR) with multiple physical stores. The project focuses on building custom modules for pawn shop and gold purchasing operations on top of standard Odoo.

**Business Domain**: Jewelry retail, gold purchasing from individuals, and pawn services (empeños).

## Development Commands

```bash
# Start development environment
docker compose up -d

# View Odoo logs
docker compose logs -f odoo

# Stop environment
docker compose down

# Reset database (removes all data)
docker compose down -v

# Rebuild after Dockerfile changes
docker compose build --no-cache && docker compose up -d
```

**Odoo Access**: http://localhost:8069 (default credentials in .env.example)

## Architecture

### Docker Setup
- **PostgreSQL 15**: Database container (`narim_db`)
- **Odoo 18**: Application container (`narim_odoo`) built from custom Dockerfile
- Source code mounted read-only for hot reload in development
- Config at `config/odoo.conf` with `dev_mode = reload,qweb,xml` enabled

### Directory Structure
```
/custom-addons/     # Custom modules for IAN OR (mount point)
/odoo/              # Odoo 18 source code (standard addons in odoo/addons/)
/config/odoo.conf   # Odoo configuration
/docs/              # Project documentation (MVP requirements, coverage analysis)
```

### Custom Modules to Build (see docs/ANALISIS_COBERTURA_ODOO.md)
- `ian_or_base`: Base module with groups and configuration
- `ian_or_partner`: Extends res.partner with DNI photo fields
- `ian_or_purchase_client`: Purchases from individuals (not suppliers)
- `ian_or_pawn`: Pawn system (empeños) with recovery pricing
- `ian_or_product`: Product origin traceability
- `ian_or_police_report`: Police reporting in PDF/Excel

## Odoo Development Patterns

### Module Structure
```
my_module/
├── __manifest__.py
├── __init__.py
├── models/
├── views/
├── security/
│   └── ir.model.access.csv
├── data/
└── reports/
```

### Key Conventions
- Use `_inherit` for extending existing models
- Always define `_description` on models
- Use `mail.thread` and `mail.activity.mixin` for chatter support
- Define ACLs in `security/ir.model.access.csv`
- XML IDs format: `module_name.object_type_descriptive_name`

### Running Odoo Commands Inside Container
```bash
docker compose exec odoo python -m odoo --help
docker compose exec odoo python -m odoo -d <dbname> -u <module> --stop-after-init
```

## Key Business Rules

- **Police blocking period**: 14 days (configurable) before gold purchases can be sent to smelting
- **Pawn recovery price**: `purchase_price * (1 + margin_percent/100) + daily_surcharge`
- **Multi-store**: Each physical store = one warehouse in Odoo
- **Client purchases**: Individuals selling gold to IAN OR (different from supplier purchases)

## Odoo 18 Specifics

- OWL framework for JavaScript components
- Python 3.11+ required
- QWeb templates for reports and views
- Gevent on port 8072 for longpolling/websockets
- seguir metodología "Code First" con '/Users/adam/Apps/NarimERP/custom-addons/narim_installer/__manifest__.py' para administrar los módulos del proyecto

## Reglas de Oro - Desarrollo Odoo (NO NEGOCIABLES)

### 1. NUNCA modificar el core de Odoo
- **PROHIBIDO** editar archivos en `/odoo/` o `/odoo/addons/`
- TODO el código personalizado va en `/custom-addons/`
- Para extender funcionalidad, usar `_inherit` en un módulo propio

### 2. Solo Community Edition
- **PROHIBIDO** usar módulos con `license="OEEL-1"` (Enterprise)
- Verificar siempre el `__manifest__.py` de módulos de terceros
- Licencia correcta para nuestros módulos: `LGPL-3`

### 3. Seguridad obligatoria
- **NUNCA** crear un modelo sin su `ir.model.access.csv`
- Definir record rules cuando haya datos sensibles entre tiendas
- **PROHIBIDO** usar `eval()` o `exec()` - riesgo de inyección

### 4. Extensión correcta de modelos
- Usar `_inherit = 'modelo.existente'` (NO copiar código del core)
- Llamar siempre a `super()` en override de create/write/unlink
- No sobrescribir métodos completos si solo necesitas añadir lógica

### 5. Estándares de código obligatorios
- Todo modelo DEBE tener `_description`
- Versiones: formato `18.0.MAJOR.MINOR.PATCH`
- Usar `ir.sequence` para referencias únicas (NO generar manualmente)
- `sudo()` solo cuando sea imprescindible y documentar el motivo con comentario
- XML IDs: formato estricto `module_name.type_descriptive_name` (ej: `ian_or_pawn.view_pawn_form`)

### 6. Verificación antes de cualquier cambio
- Confirmar que el archivo está en `/custom-addons/`, NUNCA en `/odoo/`
- Si necesitas modificar comportamiento de Odoo base → crear extensión con `_inherit`