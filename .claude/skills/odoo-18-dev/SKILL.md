---
name: odoo-18-dev
description: Expert guidance for Odoo 18 Community Edition development. This skill should be used when creating custom modules, extending existing models, implementing business logic, designing views with XML and QWeb, configuring security including ACLs and record rules, writing controllers, or following Odoo development best practices. The skill prioritizes open-source solutions and avoids Enterprise-only features unless explicitly requested. Use this skill for any Odoo 18 development task including module architecture, ORM operations, view design, security configuration, and debugging.
---

# Odoo 18 Community Edition Development Guide

## Overview

Odoo 18 is an open-source ERP platform built with Python 3.10+ and PostgreSQL. This guide covers Community Edition (CE) development patterns and best practices.

**Key Principle**: Always prefer Community Edition features. Enterprise-only modules are clearly marked in Odoo's codebase with `license="OEEL-1"` in their manifest.

## Architecture Overview

### Technology Stack
- **Backend**: Python 3.10+, PostgreSQL 12+
- **Frontend**: JavaScript (OWL 2 framework), XML views, QWeb templates
- **Web Framework**: Werkzeug-based with custom routing

### Core Components
1. **ORM (Object-Relational Mapping)**: Abstraction layer for database operations
2. **Views**: XML-based UI definitions (form, list, kanban, calendar, etc.)
3. **Controllers**: HTTP endpoints for web pages and API
4. **QWeb**: Template engine for reports and web pages
5. **Assets**: JavaScript/CSS bundling system

## Module Structure

Every custom module follows this structure:

```
my_module/
├── __init__.py              # Python package init
├── __manifest__.py          # Module metadata (REQUIRED)
├── models/                  # Business logic
│   ├── __init__.py
│   └── my_model.py
├── views/                   # XML view definitions
│   └── my_model_views.xml
├── security/                # Access control
│   ├── ir.model.access.csv  # ACLs
│   └── security.xml         # Record rules, groups
├── data/                    # Default data
│   └── data.xml
├── demo/                    # Demo data (optional)
│   └── demo.xml
├── controllers/             # HTTP controllers
│   ├── __init__.py
│   └── main.py
├── wizard/                  # Transient models for wizards
│   ├── __init__.py
│   └── my_wizard.py
├── report/                  # Report definitions
│   └── report_templates.xml
└── static/                  # Static assets
    ├── src/
    │   ├── js/
    │   ├── css/
    │   └── xml/             # OWL templates
    └── description/
        └── icon.png         # Module icon (128x128)
```

## Manifest File (__manifest__.py)

```python
{
    'name': 'Module Display Name',
    'version': '18.0.1.0.0',  # Odoo version.major.minor.patch
    'category': 'Category/Subcategory',
    'summary': 'Short description (max 80 chars)',
    'description': """
        Long description in RST format.
        Supports multiple lines.
    """,
    'author': 'Your Name',
    'website': 'https://example.com',
    'license': 'LGPL-3',  # Use LGPL-3 for CE modules
    'depends': ['base'],  # Required dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/**/*',
            'my_module/static/src/css/**/*',
            'my_module/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'application': True,  # True if standalone app
    'auto_install': False,
}
```

## Development Workflows

### Creating a New Module

1. Create module directory in `custom-addons/`
2. Create `__init__.py` and `__manifest__.py`
3. Define models in `models/`
4. Create views in `views/`
5. Set up security in `security/`
6. Update module list: Settings > Apps > Update Apps List
7. Install the module

### Extending Existing Models

To extend an existing Odoo model, use `_inherit`:

```python
from odoo import models, fields

class ResPartnerExtension(models.Model):
    _inherit = 'res.partner'

    custom_field = fields.Char(string='Custom Field')
```

### Creating New Models

See `references/orm_reference.md` for complete ORM documentation.

### Designing Views

See `references/views_reference.md` for view types and XML syntax.

### Configuring Security

See `references/security_reference.md` for ACLs and record rules.

## Best Practices

### Code Style

1. Follow PEP 8 with Odoo conventions
2. Use meaningful names: `product_template_id` not `pt_id`
3. Keep methods under 50 lines when possible
4. Document complex business logic with docstrings

### Model Design

1. Use `_description` for every model
2. Implement `_sql_constraints` for database-level validation
3. Use `_rec_name` to define the display field
4. Prefer `_order` for default sorting

### Performance

1. Use `@api.depends` correctly to avoid unnecessary recomputation
2. Batch operations with `create()` accepting list of dicts
3. Use `search_read()` instead of `search()` + `read()`
4. Prefetch related fields with `with_prefetch()`
5. Use `sudo()` sparingly and document why

### Security

1. Always define ACLs before testing
2. Use record rules for row-level security
3. Validate user input in controllers
4. Never use `eval()` or `exec()`
5. Use `werkzeug.security` for password handling

## Common Patterns

### Computed Fields with Dependencies

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_percent = fields.Float(
        compute='_compute_margin_percent',
        store=True,  # Store if needed for search/group
    )

    @api.depends('amount_total', 'margin')
    def _compute_margin_percent(self):
        for order in self:
            if order.amount_total:
                order.margin_percent = (order.margin / order.amount_total) * 100
            else:
                order.margin_percent = 0.0
```

### Onchange Methods

```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.delivery_address = self.partner_id.street
```

### Constraints

```python
from odoo.exceptions import ValidationError

@api.constrains('quantity')
def _check_quantity(self):
    for record in self:
        if record.quantity < 0:
            raise ValidationError("Quantity cannot be negative!")
```

### Override Create/Write

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('reference'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('my.model')
    return super().create(vals_list)

def write(self, vals):
    if 'state' in vals and vals['state'] == 'done':
        self._check_can_complete()
    return super().write(vals)
```

## Debugging

### Enable Developer Mode
Settings > General Settings > Developer Tools > Activate Developer Mode

### Logging

```python
import logging
_logger = logging.getLogger(__name__)

_logger.debug('Debug message: %s', variable)
_logger.info('Info message')
_logger.warning('Warning message')
_logger.error('Error message')
```

### Shell Access

```bash
docker compose exec odoo python -m odoo shell -d DATABASE_NAME
```

### Update Module Without Restart

```bash
docker compose exec odoo python -m odoo -d DATABASE_NAME -u my_module --stop-after-init
```

## Community Edition Limitations

These features require Enterprise Edition and should NOT be used in CE projects:

- Studio (visual customization)
- Accounting localization packages for certain countries
- Multi-company consolidation
- IoT Box integration
- Quality module
- PLM (Product Lifecycle Management)
- Helpdesk (use custom or community alternatives)
- Approvals
- Documents
- Sign
- Appointment scheduling
- Marketing Automation

**Always check `license` in module manifest**: `LGPL-3` = Community, `OEEL-1` = Enterprise

## Reference Files

- `references/orm_reference.md` - Complete ORM documentation (fields, methods, decorators)
- `references/views_reference.md` - View types, XML syntax, domains, actions
- `references/security_reference.md` - ACLs, record rules, groups
- `references/controllers_reference.md` - HTTP routing, JSON-RPC, authentication
- `assets/module_template/` - Starter template for new modules
