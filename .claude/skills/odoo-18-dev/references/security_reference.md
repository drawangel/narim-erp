# Odoo 18 Security Reference

## Security Overview

Odoo security works on multiple layers:

1. **Access Control Lists (ACLs)**: Model-level CRUD permissions
2. **Record Rules**: Row-level filtering (domain-based)
3. **Field Groups**: Field-level visibility
4. **Menu Groups**: Menu visibility

## Access Control Lists (ir.model.access.csv)

### File Format

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,my_module.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
access_my_model_public,my.model.public,model_my_model,,1,0,0,0
```

### Column Definitions

| Column | Description |
|--------|-------------|
| `id` | Unique XML ID |
| `name` | Human-readable name |
| `model_id:id` | Model reference (`model_` + model name with `_`) |
| `group_id:id` | Group reference (empty = all users) |
| `perm_read` | Can read (1/0) |
| `perm_write` | Can update (1/0) |
| `perm_create` | Can create (1/0) |
| `perm_unlink` | Can delete (1/0) |

### Common Patterns

```csv
# User can CRUD own records (combined with record rules)
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,1

# Manager has full access
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1

# Portal user read-only
access_my_model_portal,my.model.portal,model_my_model,base.group_portal,1,0,0,0

# Public (unauthenticated) access
access_my_model_public,my.model.public,model_my_model,base.group_public,1,0,0,0

# Multi-company record
access_my_model_company,my.model.company,model_my_model,base.group_user,1,1,1,1
```

## Security Groups

### Defining Groups (security/security.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Category for grouping -->
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="description">Category for My Module groups</field>
        <field name="sequence">100</field>
    </record>

    <!-- User group -->
    <record id="group_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        <field name="comment">Basic access to My Module</field>
    </record>

    <!-- Manager group (inherits from user) -->
    <record id="group_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('group_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
        <field name="comment">Full access to My Module</field>
    </record>
</odoo>
```

### Group Hierarchy

```xml
<!-- Create group hierarchy using implied_ids -->
<record id="group_admin" model="res.groups">
    <field name="name">Administrator</field>
    <field name="implied_ids" eval="[
        (4, ref('group_manager')),
        (4, ref('base.group_system'))
    ]"/>
</record>
```

### Common Base Groups

| Group | Description |
|-------|-------------|
| `base.group_user` | Internal user |
| `base.group_portal` | Portal user |
| `base.group_public` | Public (unauthenticated) |
| `base.group_system` | Settings (admin) |
| `base.group_no_one` | Technical features |
| `base.group_multi_company` | Multi-company |

## Record Rules (ir.rule)

### Basic Record Rule

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User sees own</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Manager Sees All

```xml
<record id="rule_my_model_manager" model="ir.rule">
    <field name="name">My Model: Manager sees all</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_manager'))]"/>
</record>
```

### Multi-Company Rules

```xml
<!-- Standard multi-company rule -->
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Global Rules (No Groups)

```xml
<!-- Applies to ALL users -->
<record id="rule_my_model_global" model="ir.rule">
    <field name="name">My Model: Global active filter</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('active', '=', True)]</field>
    <field name="global" eval="True"/>
</record>
```

### Complex Domain Examples

```xml
<!-- User sees own + team's records -->
<field name="domain_force">[
    '|',
    ('user_id', '=', user.id),
    ('team_id', 'in', user.team_ids.ids)
]</field>

<!-- User sees records of own company + children -->
<field name="domain_force">[
    ('company_id', 'child_of', company_id)
]</field>

<!-- Portal sees only their partner's records -->
<field name="domain_force">[
    ('partner_id', '=', user.partner_id.id)
]</field>

<!-- Based on state -->
<field name="domain_force">[
    '|',
    ('state', 'in', ['draft', 'sent']),
    ('user_id', '=', user.id)
]</field>
```

## Field-Level Security

### Restrict Field Visibility

```python
class MyModel(models.Model):
    _name = 'my.model'

    # Only visible to managers
    internal_notes = fields.Text(
        groups='my_module.group_manager'
    )

    # Only visible to settings users
    technical_field = fields.Char(
        groups='base.group_system'
    )
```

### In Views

```xml
<!-- Hide field for non-managers -->
<field name="secret_info" groups="my_module.group_manager"/>

<!-- Hide button for non-managers -->
<button name="action_approve" groups="my_module.group_manager"/>

<!-- Hide entire page -->
<page string="Admin" groups="base.group_system">
    <field name="admin_settings"/>
</page>
```

## Menu Security

```xml
<!-- Menu visible only to managers -->
<menuitem id="menu_admin_settings"
          name="Settings"
          parent="my_module_menu_root"
          groups="my_module.group_manager"/>

<!-- Menu visible to multiple groups -->
<menuitem id="menu_reports"
          name="Reports"
          groups="my_module.group_user,my_module.group_manager"/>
```

## Programmatic Security Checks

### Check Access

```python
# Check if user has access (raises AccessError if not)
record.check_access_rights('read')
record.check_access_rule('read')

# Check without raising error
can_read = self.env['my.model'].check_access_rights('read', raise_exception=False)

# Check group membership
if self.env.user.has_group('my_module.group_manager'):
    # Manager logic
    pass
```

### Sudo Operations

```python
# Bypass security (use sparingly!)
record.sudo().write({'secret_field': 'value'})

# Sudo as specific user
record.sudo(other_user).action_do_something()

# Important: Always document why sudo is needed
# SECURITY: Using sudo because [reason]
self.sudo().create_system_record()
```

### With User/Company Context

```python
# Execute as different user
record.with_user(user).read(['name'])

# Execute in different company context
record.with_company(company).compute_values()
```

## Security Best Practices

### 1. Least Privilege Principle
```csv
# Start with minimal permissions, add as needed
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0
```

### 2. Combine ACLs with Record Rules
```csv
# ACL: Allow CRUD
access_my_model,my.model,model_my_model,base.group_user,1,1,1,1
```
```xml
<!-- Record rule: But only own records -->
<record id="rule_own_records" model="ir.rule">
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

### 3. Use Company Rules for Multi-tenant
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Auto-check company consistency

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company
    )
```

### 4. Validate in Controllers
```python
@http.route('/my/document/<int:doc_id>', auth='user')
def view_document(self, doc_id):
    document = request.env['my.model'].browse(doc_id)
    # Check access explicitly
    document.check_access_rights('read')
    document.check_access_rule('read')
    return request.render('my_module.document_template', {'doc': document})
```

### 5. Secure Default Values
```python
@api.model
def default_get(self, fields_list):
    defaults = super().default_get(fields_list)
    # Set current user as owner
    defaults['user_id'] = self.env.uid
    defaults['company_id'] = self.env.company.id
    return defaults
```

## Common Security Patterns

### Team-Based Access

```xml
<!-- User sees records where they're a team member -->
<record id="rule_team_access" model="ir.rule">
    <field name="name">My Model: Team access</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('user_id', '=', user.id),
        ('team_id.member_ids', 'in', [user.id])
    ]</field>
</record>
```

### Hierarchical Access (Manager sees subordinates)

```xml
<record id="rule_subordinate_access" model="ir.rule">
    <field name="name">My Model: See subordinates</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[
        '|',
        ('user_id', '=', user.id),
        ('user_id.employee_id.parent_id.user_id', '=', user.id)
    ]</field>
</record>
```

### State-Based Write Access

```xml
<!-- Only draft records can be edited by users -->
<record id="rule_draft_write" model="ir.rule">
    <field name="name">My Model: Edit only draft</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('state', '=', 'draft')]</field>
    <field name="groups" eval="[(4, ref('group_user'))]"/>
    <field name="perm_read" eval="False"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```
