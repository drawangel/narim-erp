# Smart Button: Compra a Particular desde Ficha de Contacto

## Estado de Implementación

| Paso | Descripción | Estado | Fecha | Notas |
|------|-------------|--------|-------|-------|
| 1 | Crear `res_partner.py` con extensión de modelo | ✅ | 2025-12-08 | Usa `read_group` para mejor performance |
| 2 | Actualizar `models/__init__.py` | ✅ | 2025-12-08 | Import añadido |
| 3 | Crear `res_partner_views.xml` con smart buttons | ✅ | 2025-12-08 | Smart button + botón "Nueva Compra" |
| 4 | Actualizar `__manifest__.py` | ✅ | 2025-12-08 | Versión 18.0.1.8.0 |
| 5 | Actualizar módulo en Odoo | ✅ | 2025-12-08 | Sin errores |

---

## Resumen

Análisis para implementar un botón en la ficha de contacto (`res.partner`) que permita:
1. Ver compras existentes del cliente
2. Crear una nueva compra pre-rellenando el cliente

## Estado Actual

### Módulos Involucrados

| Módulo | Propósito | Dependencias |
|--------|-----------|--------------|
| `jewelry_partner` | Extiende `res.partner` con fotos DNI | `jewelry_base` |
| `jewelry_purchase_client` | Gestiona compras a particulares | `jewelry_base`, `mail`, `pos` |

### Problema de Dependencias

Actualmente `jewelry_partner` **no depende** de `jewelry_purchase_client`. Si añadimos el smart button directamente en `jewelry_partner`, crearíamos una dependencia circular o innecesaria.

## Opciones de Implementación

### Opción A: Smart Button en `jewelry_purchase_client` (Recomendada)

El módulo `jewelry_purchase_client` extiende la vista de `res.partner` para añadir el botón.

**Ventajas:**
- No modifica `jewelry_partner`
- La funcionalidad vive donde corresponde (en el módulo de compras)
- Patrón estándar de Odoo: el módulo que "aporta" la relación define el enlace

**Implementación:**

```
jewelry_purchase_client/
├── models/
│   └── res_partner.py  # NUEVO: Añade campo computed + método acción
└── views/
    └── res_partner_views.xml  # NUEVO: Hereda vista para añadir button_box
```

### Opción B: Módulo Puente `jewelry_partner_purchase`

Crear un módulo pequeño que dependa de ambos y añada el smart button.

**Ventajas:**
- Máxima separación de responsabilidades
- Permite instalar `jewelry_partner` sin `jewelry_purchase_client`

**Desventaja:**
- Más módulos que mantener (overhead innecesario en este caso)

---

## Plan de Implementación (Opción A)

### 1. Extender `res.partner` en `jewelry_purchase_client`

**Archivo:** `jewelry_purchase_client/models/res_partner.py`

```python
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_purchase_ids = fields.One2many(
        comodel_name='jewelry.client.purchase',
        inverse_name='partner_id',
        string='Client Purchases',
    )
    client_purchase_count = fields.Integer(
        string='Purchase Count',
        compute='_compute_client_purchase_count',
    )

    def _compute_client_purchase_count(self):
        for partner in self:
            partner.client_purchase_count = self.env['jewelry.client.purchase'].search_count([
                ('partner_id', '=', partner.id),
            ])

    def action_view_client_purchases(self):
        """Open list of client purchases for this partner."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compras a Particular',
            'res_model': 'jewelry.client.purchase',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_partner_id': self.id,
            },
        }

    def action_create_client_purchase(self):
        """Create a new client purchase for this partner."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Compra a Particular',
            'res_model': 'jewelry.client.purchase',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.id,
            },
        }
```

### 2. Registrar el modelo

**Archivo:** `jewelry_purchase_client/models/__init__.py`

```python
from . import client_purchase
from . import client_purchase_line
from . import product
from . import smelting_batch
from . import pos_session
from . import res_partner  # AÑADIR
```

### 3. Crear Vista Heredada

**Archivo:** `jewelry_purchase_client/views/res_partner_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_partner_form_inherit_purchase_client" model="ir.ui.view">
        <field name="name">res.partner.form.inherit.purchase.client</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="priority">20</field>
        <field name="arch" type="xml">
            <!-- Añadir button_box si no existe -->
            <xpath expr="//div[hasclass('oe_button_box')]" position="inside">
                <!-- Smart button con contador -->
                <button name="action_view_client_purchases"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-shopping-cart"
                        invisible="is_company">
                    <field name="client_purchase_count" widget="statinfo"
                           string="Historial"/>
                </button>
            </xpath>

            <!-- Botón "Nueva Compra" en la cabecera del formulario -->
            <xpath expr="//div[hasclass('oe_title')]" position="before">
                <div class="float-end" invisible="is_company">
                    <button name="action_create_client_purchase"
                            type="object"
                            class="btn btn-primary"
                            icon="fa-plus">
                        Nueva Compra
                    </button>
                </div>
            </xpath>
        </field>
    </record>
</odoo>
```

### 4. Registrar la Vista en el Manifest

**Archivo:** `jewelry_purchase_client/__manifest__.py`

Añadir al array `data`:

```python
'data': [
    # ... existentes ...
    'views/res_partner_views.xml',  # AÑADIR
],
```

---

## Comportamiento Esperado

### En la Ficha de Contacto (Individuos)

```
┌─────────────────────────────────────────────────────────┐
│  [Nueva Compra]                                         │
│                                                         │
│  ┌──────────────┐                                       │
│  │ 🛒           │  ← Smart Button                       │
│  │    5         │                                       │
│  │ Historial    │                                       │
│  └──────────────┘                                       │
│                                                         │
│  Juan García                                            │
│  ════════════════════════════════════════════════════   │
│  DNI: 12345678A                                         │
│  Teléfono: 612 345 678                                  │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Usuario

1. **Click en Smart Button "Historial"** → Abre lista filtrada con todas las compras del cliente
2. **Click en "Nueva Compra"** → Abre formulario nuevo con `partner_id` pre-rellenado

---

## Consideraciones Técnicas

### Visibilidad

- Los botones solo aparecen para **individuos** (`is_company = False`)
- El dominio en `jewelry.client.purchase.partner_id` ya filtra: `domain="[('is_company', '=', False)]"`

### Performance

- El campo `client_purchase_count` es **computed no-stored**
- Para contactos con muchas compras, considerar hacerlo `store=True` con `@api.depends('client_purchase_ids')`

### Alternativa: Usar `read_group` para mejor performance

```python
def _compute_client_purchase_count(self):
    purchase_data = self.env['jewelry.client.purchase'].read_group(
        domain=[('partner_id', 'in', self.ids)],
        fields=['partner_id'],
        groupby=['partner_id'],
    )
    mapped_data = {x['partner_id'][0]: x['partner_id_count'] for x in purchase_data}
    for partner in self:
        partner.client_purchase_count = mapped_data.get(partner.id, 0)
```

---

## Archivos a Crear/Modificar

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `jewelry_purchase_client/models/res_partner.py` | **Crear** | Extensión de res.partner |
| `jewelry_purchase_client/models/__init__.py` | Modificar | Importar res_partner |
| `jewelry_purchase_client/views/res_partner_views.xml` | **Crear** | Vista heredada con smart buttons |
| `jewelry_purchase_client/__manifest__.py` | Modificar | Añadir vista al data |

---

## Patrón Odoo Estándar

Este patrón es exactamente el que usa Odoo en sus módulos core:

- `sale` añade smart button "Ventas" en `res.partner`
- `account` añade smart button "Facturas" en `res.partner`
- `purchase` añade smart button "Compras" en `res.partner`

Seguir este patrón garantiza:
- UX consistente con el resto de Odoo
- Mantenibilidad a largo plazo
- Compatibilidad con futuras versiones
