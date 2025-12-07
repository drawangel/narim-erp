# Plan: Forzar Desbloqueo con Wizard

## Resumen
Implementar acción "Forzar Desbloqueo" en el módulo `jewelry_purchase_client` con un wizard modal que permite a los administradores desbloquear órdenes durante el período de bloqueo, registrando la razón (opcional) y el usuario para auditoría.

## Archivos a Modificar/Crear

| Archivo | Acción |
|---------|--------|
| `wizard/__init__.py` | Crear |
| `wizard/force_unlock_wizard.py` | Crear |
| `wizard/force_unlock_wizard_views.xml` | Crear |
| `models/client_purchase.py` | Modificar |
| `views/client_purchase_views.xml` | Modificar |
| `__manifest__.py` | Modificar |
| `__init__.py` | Modificar |
| `security/ir.model.access.csv` | Modificar |
| `i18n/es.po` | Modificar |

---

## Implementación Detallada

### 1. Wizard: `wizard/force_unlock_wizard.py`

```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class ForceUnlockWizard(models.TransientModel):
    _name = 'jewelry.force.unlock.wizard'
    _description = 'Force Unlock Wizard'

    purchase_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Purchase Order',
        required=True,
    )
    reason = fields.Text(
        string='Reason',
        help='Optional: Explain why the blocking period is being skipped',
    )

    def action_confirm(self):
        self.ensure_one()
        if self.purchase_id.state != 'blocked':
            raise UserError('Only blocked orders can be force unlocked.')

        self.purchase_id.write({
            'state': 'available',
            'force_unlocked': True,
            'force_unlock_reason': self.reason,
            'force_unlock_date': fields.Datetime.now(),
            'force_unlock_user_id': self.env.uid,
        })

        # Mensaje de auditoría en chatter
        body = f'⚠️ <b>Desbloqueo forzado</b> por {self.env.user.name}'
        if self.reason:
            body += f'<br/>Razón: {self.reason}'
        self.purchase_id.message_post(body=body, message_type='notification')

        return {'type': 'ir.actions.act_window_close'}
```

### 2. Vista del Wizard: `wizard/force_unlock_wizard_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="force_unlock_wizard_view_form" model="ir.ui.view">
        <field name="name">jewelry.force.unlock.wizard.form</field>
        <field name="model">jewelry.force.unlock.wizard</field>
        <field name="arch" type="xml">
            <form string="Force Unlock">
                <div class="alert alert-warning" role="alert">
                    <i class="fa fa-exclamation-triangle"/>
                    You are about to skip the legal blocking period.
                    This action will be recorded for audit purposes.
                </div>
                <group>
                    <field name="purchase_id" readonly="1"/>
                    <field name="reason" placeholder="Optional: reason for early unlock..."/>
                </group>
                <footer>
                    <button name="action_confirm" string="Confirm Unlock"
                            type="object" class="btn-warning"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_force_unlock_wizard" model="ir.actions.act_window">
        <field name="name">Force Unlock</field>
        <field name="res_model">jewelry.force.unlock.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### 3. Campos de Auditoría: `models/client_purchase.py`

Agregar después de los campos existentes de blocking period (línea ~106):

```python
# Force unlock audit fields
force_unlocked = fields.Boolean(
    string='Force Unlocked',
    default=False,
    copy=False,
    help='Indicates if blocking period was manually skipped',
)
force_unlock_reason = fields.Text(
    string='Unlock Reason',
    copy=False,
)
force_unlock_date = fields.Datetime(
    string='Force Unlock Date',
    copy=False,
)
force_unlock_user_id = fields.Many2one(
    comodel_name='res.users',
    string='Unlocked By',
    copy=False,
)
```

Agregar método para abrir el wizard:

```python
def action_open_force_unlock_wizard(self):
    """Open the force unlock wizard."""
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Force Unlock',
        'res_model': 'jewelry.force.unlock.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_purchase_id': self.id},
    }
```

### 4. Botón en Vista: `views/client_purchase_views.xml`

En el `<header>`, después del botón "Mark Available" (línea ~19):

```xml
<button name="action_open_force_unlock_wizard"
        string="Force Unlock"
        type="object"
        class="btn-warning"
        groups="jewelry_base.group_jewelry_manager"
        invisible="state != 'blocked'"/>
```

En el group "Blocking Period" (después de línea ~65), mostrar info de desbloqueo:

```xml
<field name="force_unlocked" invisible="1"/>
<div colspan="2" class="text-warning fw-bold"
     invisible="not force_unlocked">
    <i class="fa fa-exclamation-triangle"/>
    Force unlocked by
    <field name="force_unlock_user_id" widget="many2one_avatar_user"
           class="d-inline" readonly="1"/>
    on <field name="force_unlock_date" widget="datetime" readonly="1"/>
</div>
```

### 5. Seguridad: `security/ir.model.access.csv`

Agregar línea:

```csv
access_force_unlock_wizard,jewelry.force.unlock.wizard,model_jewelry_force_unlock_wizard,jewelry_base.group_jewelry_manager,1,1,1,0
```

### 6. Manifest: `__manifest__.py`

Agregar en `data`:

```python
'wizard/force_unlock_wizard_views.xml',
```

### 7. Init: `__init__.py`

```python
from . import models
from . import wizard
```

### 8. Wizard Init: `wizard/__init__.py`

```python
from . import force_unlock_wizard
```

---

## Capas de Seguridad

| Capa | Implementación |
|------|----------------|
| **Vista** | `groups="jewelry_base.group_jewelry_manager"` oculta el botón |
| **ACL** | Solo managers tienen acceso al modelo del wizard |
| **Auditoría** | Campos `force_unlock_*` + mensaje en chatter con usuario y fecha |

---

## Flujo de Usuario

1. Manager ve orden en estado "Blocking Period"
2. Click en botón "Force Unlock" (solo visible para managers)
3. Se abre wizard modal con advertencia
4. Opcionalmente ingresa razón
5. Click "Confirm Unlock"
6. Orden pasa a estado "Available"
7. Se registra en chatter: usuario, fecha y razón
8. Vista muestra indicador de desbloqueo forzado
