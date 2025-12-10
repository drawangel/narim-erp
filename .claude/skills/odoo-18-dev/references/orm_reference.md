# Odoo 18 ORM Reference

## Model Types

### Model (Persistent)
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _order = 'name asc, id desc'
    _rec_name = 'name'
```

### TransientModel (Wizard)
Temporary data, auto-cleaned by cron:
```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Wizard'
```

### AbstractModel (Mixin)
No database table, used for inheritance:
```python
class MyMixin(models.AbstractModel):
    _name = 'my.mixin'
    _description = 'My Mixin'
```

## Model Attributes

| Attribute | Description |
|-----------|-------------|
| `_name` | Technical name (required for new models) |
| `_description` | Human-readable description |
| `_inherit` | Inherit from existing model(s) |
| `_inherits` | Delegation inheritance (composition) |
| `_order` | Default sort order |
| `_rec_name` | Field used for display_name |
| `_table` | Custom database table name |
| `_sql_constraints` | Database-level constraints |
| `_check_company_auto` | Auto-check company consistency |

## Field Types

### Basic Fields

```python
# String fields
name = fields.Char(string='Name', required=True, size=100)
description = fields.Text(string='Description')
html_content = fields.Html(string='HTML Content', sanitize=True)

# Numeric fields
quantity = fields.Integer(string='Quantity', default=1)
price = fields.Float(string='Price', digits=(16, 2))
amount = fields.Monetary(string='Amount', currency_field='currency_id')

# Boolean
active = fields.Boolean(string='Active', default=True)

# Date/Time
date = fields.Date(string='Date', default=fields.Date.today)
datetime = fields.Datetime(string='DateTime', default=fields.Datetime.now)

# Binary
document = fields.Binary(string='Document', attachment=True)
image = fields.Image(string='Image', max_width=1024, max_height=1024)

# Selection
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='State', default='draft', required=True)
```

### Relational Fields

```python
# Many2one (FK)
partner_id = fields.Many2one(
    comodel_name='res.partner',
    string='Partner',
    ondelete='cascade',  # cascade, set null, restrict
    domain="[('is_company', '=', True)]",
    context={'default_is_company': True},
)

# One2many (reverse of Many2one)
order_line_ids = fields.One2many(
    comodel_name='sale.order.line',
    inverse_name='order_id',
    string='Order Lines',
    copy=True,
)

# Many2many
tag_ids = fields.Many2many(
    comodel_name='product.tag',
    relation='product_tag_rel',  # junction table name
    column1='product_id',
    column2='tag_id',
    string='Tags',
)
```

### Computed Fields

```python
# Stored computed field
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,  # stored in DB
    readonly=True,
)

@api.depends('line_ids.price', 'line_ids.quantity')
def _compute_total(self):
    for record in self:
        record.total = sum(
            line.price * line.quantity
            for line in record.line_ids
        )

# Inverse computed field (editable)
full_name = fields.Char(
    compute='_compute_full_name',
    inverse='_inverse_full_name',
    store=True,
)

def _inverse_full_name(self):
    for record in self:
        parts = (record.full_name or '').split(' ', 1)
        record.first_name = parts[0]
        record.last_name = parts[1] if len(parts) > 1 else ''
```

### Related Fields

```python
# Shortcut to related record's field
partner_email = fields.Char(
    related='partner_id.email',
    string='Partner Email',
    readonly=True,
    store=True,  # optional, for searching
)
```

## Field Parameters

| Parameter | Description |
|-----------|-------------|
| `string` | Label displayed in UI |
| `help` | Tooltip text |
| `required` | Mandatory field |
| `readonly` | Not editable in UI |
| `default` | Default value (value or callable) |
| `index` | Create database index |
| `copy` | Copy value when duplicating |
| `groups` | Restrict visibility to groups |
| `company_dependent` | Separate value per company |
| `tracking` | Track changes in chatter |

## API Decorators

### @api.depends
Declare computed field dependencies:
```python
@api.depends('field1', 'field2', 'line_ids.amount')
def _compute_something(self):
    pass
```

### @api.onchange
UI-only change handler:
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.address = self.partner_id.street
        return {'warning': {'title': 'Warning', 'message': 'Check address'}}
```

### @api.constrains
Validation constraint:
```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date > record.end_date:
            raise ValidationError("End date must be after start date")
```

### @api.model
Method called on model, not recordset:
```python
@api.model
def get_default_values(self):
    return {'state': 'draft'}
```

### @api.model_create_multi
Override create for batch operations:
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # modify vals
        pass
    return super().create(vals_list)
```

## CRUD Operations

### Create
```python
# Single record
record = self.env['my.model'].create({
    'name': 'Test',
    'value': 100,
})

# Multiple records (efficient)
records = self.env['my.model'].create([
    {'name': 'Test 1'},
    {'name': 'Test 2'},
])
```

### Read
```python
# Browse by ID
record = self.env['my.model'].browse(1)
records = self.env['my.model'].browse([1, 2, 3])

# Search
records = self.env['my.model'].search([
    ('state', '=', 'draft'),
    ('date', '>=', '2024-01-01'),
], limit=10, order='date desc')

# Search and read (efficient)
data = self.env['my.model'].search_read(
    domain=[('active', '=', True)],
    fields=['name', 'value'],
    limit=100,
)

# Read specific fields
values = record.read(['name', 'value'])

# Count
count = self.env['my.model'].search_count([('state', '=', 'done')])
```

### Update
```python
# Single field
record.name = 'New Name'

# Multiple fields
record.write({
    'name': 'New Name',
    'state': 'confirmed',
})

# Multiple records
records.write({'active': False})
```

### Delete
```python
record.unlink()
records.unlink()
```

## Domain Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=`, `!=` | Equals/Not equals | `('state', '=', 'draft')` |
| `<`, `>`, `<=`, `>=` | Comparison | `('amount', '>', 100)` |
| `like`, `ilike` | Pattern match (case-sensitive/insensitive) | `('name', 'ilike', 'test%')` |
| `=like`, `=ilike` | Exact pattern | `('code', '=like', 'A%')` |
| `in`, `not in` | List membership | `('id', 'in', [1, 2, 3])` |
| `child_of` | Hierarchical | `('category_id', 'child_of', parent_id)` |
| `parent_of` | Hierarchical (reverse) | `('category_id', 'parent_of', child_id)` |

### Domain Logic
```python
# AND (implicit)
[('state', '=', 'draft'), ('amount', '>', 0)]

# OR
['|', ('state', '=', 'draft'), ('state', '=', 'sent')]

# NOT
['!', ('active', '=', True)]

# Complex
['|',
    '&', ('state', '=', 'draft'), ('amount', '>', 100),
    ('priority', '=', 'high')
]
```

## Environment

```python
# Current user
self.env.user
self.env.uid

# Current company
self.env.company
self.env.companies  # all allowed companies

# Context
self.env.context
self.with_context(key='value')
self.with_context(**new_context)

# Sudo (bypass security)
self.sudo()
self.sudo(user)

# Change company
self.with_company(company)

# Reference
self.env.ref('module.xml_id')

# Clear cache
self.env.invalidate_all()
```

## Recordset Operations

```python
# Iteration
for record in records:
    print(record.name)

# Filtering
filtered = records.filtered(lambda r: r.amount > 100)
filtered = records.filtered('active')  # truthy filter

# Mapping
names = records.mapped('name')
partner_names = records.mapped('partner_id.name')

# Sorting
sorted_records = records.sorted(key=lambda r: r.date, reverse=True)
sorted_records = records.sorted('name')

# Set operations
all_records = records1 | records2  # union
common = records1 & records2  # intersection
diff = records1 - records2  # difference

# Check membership
if record in records:
    pass

# Existence
if records:
    pass  # has records
if not records:
    pass  # empty

# Get IDs
ids = records.ids
```

## SQL Constraints

```python
_sql_constraints = [
    ('name_unique', 'UNIQUE(name)', 'Name must be unique!'),
    ('check_amount', 'CHECK(amount >= 0)', 'Amount must be positive!'),
    ('code_company_unique', 'UNIQUE(code, company_id)',
     'Code must be unique per company!'),
]
```

## Inheritance Patterns

### Extension (add fields/methods)
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_field = fields.Char()
```

### Prototype (new model based on existing)
```python
class CustomPartner(models.Model):
    _name = 'custom.partner'
    _inherit = 'res.partner'  # copies everything
```

### Delegation (composition)
```python
class ProductProduct(models.Model):
    _name = 'product.product'
    _inherits = {'product.template': 'product_tmpl_id'}

    product_tmpl_id = fields.Many2one('product.template', required=True)
```

### Multiple Inheritance (mixins)
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```
