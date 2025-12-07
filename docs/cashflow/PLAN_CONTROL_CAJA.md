# Plan de Implementación: Control de Caja Unificado

## Resumen Ejecutivo

Este documento describe la implementación de un sistema de control de caja que unifique:
- **Ventas de joyas** (entradas de efectivo)
- **Compras a clientes** (salidas de efectivo por compra de oro/joyas)
- **Cobros de empeños** (entradas por rescate de prendas)

La estrategia es **reutilizar el módulo POS de Odoo CE** para el control de caja, integrando las operaciones de compra a clientes como movimientos de salida dentro de la sesión POS.

---

## Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                      TIENDA (Almacén Odoo)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              SESIÓN POS (pos.session)                   │   │
│   │              Una por tienda/turno/día                   │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │                                                         │   │
│   │   ENTRADAS (+)              │    SALIDAS (-)            │   │
│   │   ─────────────             │    ──────────             │   │
│   │   • pos.order (ventas)      │    • Cash Out: Compras    │   │
│   │   • Cash In manual          │      a clientes           │   │
│   │                             │    • Cash Out manual      │   │
│   │                             │                           │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │   Saldo Inicial ──► Movimientos ──► Saldo Final         │   │
│   │                                     (cuadre de caja)    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │         COMPRAS A CLIENTES (jewelry.client.purchase)    │   │
│   │         Módulo independiente con integración POS        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Campos de Forma de Pago en Compras a Cliente

### Objetivo
Añadir los campos necesarios para registrar cómo se paga al cliente.

### Cambios en `jewelry.client.purchase`

```python
# Nuevos campos a añadir en models/client_purchase.py

payment_method = fields.Selection(
    selection=[
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia Bancaria'),
        ('check', 'Cheque'),
    ],
    string='Forma de Pago',
    required=True,
    default='cash',
    tracking=True,
)

payment_journal_id = fields.Many2one(
    comodel_name='account.journal',
    string='Diario de Pago',
    domain="[('type', 'in', ['cash', 'bank'])]",
    help='Diario contable donde se registrará el pago',
)

payment_reference = fields.Char(
    string='Referencia de Pago',
    help='Número de transferencia, cheque, etc.',
    tracking=True,
)

# Integración POS (Fase 2)
pos_session_id = fields.Many2one(
    comodel_name='pos.session',
    string='Sesión de Caja',
    readonly=True,
    copy=False,
    help='Sesión POS donde se registró el movimiento de caja',
)

pos_statement_line_id = fields.Many2one(
    comodel_name='account.bank.statement.line',
    string='Línea de Caja',
    readonly=True,
    copy=False,
    help='Movimiento de caja generado en la sesión POS',
)
```

### Vista (views/client_purchase_views.xml)

Añadir grupo de campos después del total:

```xml
<group string="Pago al Cliente">
    <field name="payment_method"/>
    <field name="payment_journal_id"
           attrs="{'invisible': [('payment_method', '=', 'cash')],
                   'required': [('payment_method', '!=', 'cash')]}"/>
    <field name="payment_reference"
           attrs="{'invisible': [('payment_method', '=', 'cash')]}"/>
    <field name="pos_session_id" readonly="1"
           attrs="{'invisible': [('pos_session_id', '=', False)]}"/>
</group>
```

### Archivos a Modificar
- `custom-addons/jewelry_purchase_client/models/client_purchase.py`
- `custom-addons/jewelry_purchase_client/views/client_purchase_views.xml`

---

## Fase 2: Integración con Sesión POS

### Objetivo
Al confirmar una compra a cliente con pago en efectivo, registrar automáticamente un movimiento de salida en la sesión POS activa.

### Dependencia de Módulo

Añadir en `__manifest__.py`:

```python
'depends': [
    'mail',
    'product',
    'stock',
    'point_of_sale',  # NUEVO
],
```

### Método de Integración

```python
# En models/client_purchase.py

def _get_active_pos_session(self):
    """Obtener la sesión POS abierta para la tienda actual."""
    self.ensure_one()
    # Buscar config POS asociado al almacén/tienda del usuario
    pos_config = self.env['pos.config'].search([
        ('company_id', '=', self.company_id.id),
        # Aquí se puede filtrar por almacén/tienda si es necesario
    ], limit=1)

    if not pos_config:
        return False

    session = self.env['pos.session'].search([
        ('config_id', '=', pos_config.id),
        ('state', '=', 'opened'),
    ], limit=1)

    return session

def _create_pos_cash_out(self):
    """Crear movimiento de salida de caja en la sesión POS."""
    self.ensure_one()

    if self.payment_method != 'cash':
        return False

    session = self._get_active_pos_session()
    if not session:
        # Opción: lanzar error o permitir sin registro en caja
        raise UserError(
            'No hay sesión de caja abierta. '
            'Abra una sesión POS antes de confirmar compras en efectivo.'
        )

    # Usar el método nativo del POS para cash out
    reason = f'Compra cliente: {self.name}'
    extras = {
        'formattedAmount': self.env['ir.qweb.field.monetary'].value_to_html(
            self.amount_total, {'display_currency': self.currency_id}
        ),
        'translatedType': 'out',
    }

    # Crear la línea de extracto bancario
    vals = session._prepare_account_bank_statement_line_vals(
        session, -1, self.amount_total, reason, extras
    )
    statement_line = self.env['account.bank.statement.line'].create(vals)

    # Guardar referencia
    self.write({
        'pos_session_id': session.id,
        'pos_statement_line_id': statement_line.id,
    })

    return statement_line

def action_confirm(self):
    """Override para integrar con POS."""
    for order in self:
        if not order.line_ids:
            raise UserError('Cannot confirm an order without lines.')
        if order.state != 'draft':
            raise UserError('Only draft orders can be confirmed.')

        # Registrar movimiento de caja si es efectivo
        if order.payment_method == 'cash':
            order._create_pos_cash_out()

        order.write({'state': 'blocked'})

    return True
```

### Cancelación de Compra

```python
def action_cancel(self):
    """Override para revertir movimiento de caja si existe."""
    for order in self:
        if order.state == 'processed':
            raise UserError('Cannot cancel a processed order.')

        # Revertir movimiento de caja si existe
        if order.pos_statement_line_id:
            if order.pos_session_id.state == 'closed':
                raise UserError(
                    'No se puede cancelar: la sesión de caja ya está cerrada. '
                    'Contacte al administrador.'
                )
            # Crear movimiento inverso (cash in)
            order._create_pos_cash_reversal()

        order.write({'state': 'cancelled'})

    return True

def _create_pos_cash_reversal(self):
    """Crear movimiento inverso en la sesión POS."""
    self.ensure_one()
    session = self.pos_session_id

    if session.state != 'opened':
        raise UserError('La sesión de caja no está abierta.')

    reason = f'ANULACIÓN Compra: {self.name}'
    extras = {
        'formattedAmount': self.env['ir.qweb.field.monetary'].value_to_html(
            self.amount_total, {'display_currency': self.currency_id}
        ),
        'translatedType': 'in',
    }

    vals = session._prepare_account_bank_statement_line_vals(
        session, 1, self.amount_total, reason, extras
    )
    self.env['account.bank.statement.line'].create(vals)
```

---

## Fase 3: Configuración de POS por Tienda

### Objetivo
Configurar un punto POS para cada tienda física.

### Configuración Requerida

1. **Crear Configuración POS por tienda**:
   - Menú: Punto de Venta → Configuración → Punto de Venta
   - Crear uno por cada tienda/almacén
   - Activar "Control de Caja" (cash_control = True)

2. **Métodos de Pago**:
   - Efectivo (tipo: cash, con control de caja)
   - Tarjeta (tipo: bank)
   - Transferencia (tipo: bank)

3. **Diarios Contables**:
   - Un diario de "Caja" por tienda (tipo: cash)
   - Diario de "Banco" compartido o por tienda

### Datos de Configuración (Opcional)

```xml
<!-- data/pos_config_data.xml -->
<odoo>
    <record id="pos_config_tienda_principal" model="pos.config">
        <field name="name">Caja Tienda Principal</field>
        <field name="cash_control">True</field>
        <field name="module_pos_hr">True</field>
    </record>
</odoo>
```

---

## Fase 4: Validaciones y Reglas de Negocio

### Validaciones al Confirmar Compra

```python
@api.constrains('payment_method', 'payment_journal_id')
def _check_payment_info(self):
    for order in self:
        if order.payment_method in ('transfer', 'check'):
            if not order.payment_journal_id:
                raise ValidationError(
                    'Debe seleccionar un diario de pago para transferencias y cheques.'
                )
```

### Validación de Sesión Abierta

```python
def action_confirm(self):
    for order in self:
        # ... validaciones existentes ...

        if order.payment_method == 'cash':
            session = order._get_active_pos_session()
            if not session:
                raise UserError(
                    'No hay sesión de caja abierta para esta tienda.\n'
                    'Abra una sesión en Punto de Venta antes de confirmar.'
                )
```

---

## Fase 5: Reportes y Visibilidad

### Vista de Compras en Sesión POS

Añadir pestaña en la vista de sesión POS para mostrar compras a clientes:

```xml
<!-- views/pos_session_views.xml -->
<odoo>
    <record id="view_pos_session_form_inherit_jewelry" model="ir.ui.view">
        <field name="name">pos.session.form.jewelry</field>
        <field name="model">pos.session</field>
        <field name="inherit_id" ref="point_of_sale.view_pos_session_form"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='payments']" position="after">
                <page string="Compras a Clientes" name="client_purchases">
                    <field name="client_purchase_ids" readonly="1">
                        <tree>
                            <field name="name"/>
                            <field name="partner_id"/>
                            <field name="date"/>
                            <field name="amount_total"/>
                            <field name="payment_method"/>
                            <field name="state"/>
                        </tree>
                    </field>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### Campo Inverso en pos.session

```python
# models/pos_session.py (extensión)
class PosSession(models.Model):
    _inherit = 'pos.session'

    client_purchase_ids = fields.One2many(
        comodel_name='jewelry.client.purchase',
        inverse_name='pos_session_id',
        string='Compras a Clientes',
        readonly=True,
    )

    client_purchase_total = fields.Monetary(
        string='Total Compras a Clientes',
        compute='_compute_client_purchase_total',
    )

    @api.depends('client_purchase_ids.amount_total')
    def _compute_client_purchase_total(self):
        for session in self:
            session.client_purchase_total = sum(
                session.client_purchase_ids.filtered(
                    lambda p: p.state not in ('cancelled', 'draft')
                ).mapped('amount_total')
            )
```

---

## Resumen de Archivos a Crear/Modificar

### Archivos a Modificar

| Archivo | Cambios |
|---------|---------|
| `__manifest__.py` | Añadir dependencia `point_of_sale`, nuevas vistas |
| `models/__init__.py` | Importar nuevo modelo `pos_session` |
| `models/client_purchase.py` | Campos de pago, integración POS |
| `views/client_purchase_views.xml` | Grupo de campos de pago |

### Archivos a Crear

| Archivo | Propósito |
|---------|-----------|
| `models/pos_session.py` | Extensión de pos.session con campo inverso |
| `views/pos_session_views.xml` | Vista de compras en sesión POS |

---

## Flujo de Usuario Final

```
1. Usuario abre sesión POS al inicio del turno
   └── POS muestra saldo inicial de caja

2. Durante el día:
   ├── Ventas: se registran en POS normalmente (+)
   └── Compras a clientes:
       ├── Crear compra en módulo jewelry_purchase_client
       ├── Seleccionar forma de pago (efectivo/transfer/cheque)
       ├── Confirmar → se crea Cash Out automático en sesión POS
       └── Compra pasa a estado "Bloqueado"

3. Al cerrar turno:
   └── Cerrar sesión POS
       ├── Sistema muestra saldo teórico
       ├── Usuario ingresa saldo físico contado
       ├── Se calcula diferencia (sobrante/faltante)
       └── Se genera asiento contable de cierre
```

---

## Consideraciones Adicionales

### Multi-Moneda
Si hay compras en moneda extranjera, considerar:
- Campo `currency_id` en la compra (ya existe)
- Conversión al momento de crear el movimiento de caja
- El POS maneja esto nativamente

### Permisos
Crear grupo de seguridad para:
- Ver compras en sesión POS
- Cancelar compras con sesión cerrada (requiere ajuste manual)

### Auditoría
El sistema mantiene trazabilidad completa:
- `pos_session_id`: Sesión donde se registró
- `pos_statement_line_id`: Movimiento específico de caja
- Campos de tracking en cambios de estado

---

## Cronograma Sugerido

| Fase | Descripción | Prioridad |
|------|-------------|-----------|
| 1 | Campos de forma de pago | Alta |
| 2 | Integración con sesión POS | Alta |
| 3 | Configuración POS por tienda | Media |
| 4 | Validaciones y reglas | Media |
| 5 | Reportes y visibilidad | Baja |

---

## Alternativas Consideradas

### ¿Por qué no crear un sistema de caja propio?

| Aspecto | Sistema Propio | Usar POS |
|---------|----------------|----------|
| Tiempo desarrollo | Alto | Bajo |
| Mantenimiento | Alto (nuevo código) | Bajo (Odoo mantiene) |
| Control de caja | Hay que implementar | Ya existe |
| Cuadre de caja | Hay que implementar | Ya existe |
| Reportes | Hay que implementar | Ya existen |
| Multi-turno | Hay que implementar | Ya existe |

### ¿Por qué no usar solo account.payment?

`account.payment` es para pagos contables, no para control de caja física. No tiene:
- Concepto de sesión/turno
- Saldo inicial/final
- Cuadre de caja
- Interfaz de arqueo

---

## Referencias Técnicas

- `pos.session`: `/odoo/addons/point_of_sale/models/pos_session.py`
- `try_cash_in_out()`: línea 1768
- `_prepare_account_bank_statement_line_vals()`: línea 1758
- Documentación POS: https://www.odoo.com/documentation/18.0/applications/sales/point_of_sale.html
