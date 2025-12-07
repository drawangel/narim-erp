# Procesamiento de Compras a Particulares: Stock o Fundición

## Resumen

Funcionalidad para procesar artículos de compras a particulares con dos destinos posibles:
1. **Inventario (Stock)**: Crear producto vendible con soporte para reparaciones
2. **Fundición (Smelting)**: Enviar material a fundir sin crear producto

La decisión se toma **por artículo** (línea), no por unidades.

---

## Estado de Implementación

| Paso | Descripción | Estado | Fecha | Notas |
|------|-------------|--------|-------|-------|
| 1 | Campos repair en product.template | ✅ | 2025-12-07 | needs_repair, repair_notes, repair_cost, ready_for_sale |
| 2 | Campo line_state básico | ✅ | 2025-12-07 | pending/in_inventory |
| 3 | Ubicación stock reparaciones | ✅ | 2025-12-07 | stock_location_pending_repair |
| 4 | Wizard SendToInventory individual | ✅ | 2025-12-07 | jewelry.send.to.inventory.wizard |
| 5 | Vistas y seguridad básica | ✅ | 2025-12-07 | Botón en líneas, filtros en productos |
| 6 | Acción completar reparación | ✅ | 2025-12-07 | action_complete_repair |
| **REFACTOR** | | | | |
| R1 | Eliminar botón "Process (Send to Smelting)" | ✅ | 2025-12-07 | Eliminado; transición ahora automática |
| R2 | Modificar `action_process()` con validación | ✅ | 2025-12-07 | Valida que no haya líneas pendientes |
| **NUEVAS FEATURES** | | | | |
| 7 | Ampliar line_state con to_smelting | ✅ | 2025-12-07 | pending/in_inventory/to_smelting |
| 8 | Botón "Enviar a Fundición" individual | ✅ | 2025-12-07 | action_send_to_smelting en líneas |
| 9 | Wizard "Fundir Todo" con confirmación | ✅ | 2025-12-07 | jewelry.smelt.all.wizard + crea batch |
| 10 | Wizard "Recepcionar Todo" simplificado | ✅ | 2025-12-07 | jewelry.receive.all.wizard + bulk create |
| 11 | Modelo SmeltingBatch (trazabilidad) | ✅ | 2025-12-07 | jewelry.smelting.batch + secuencia SMELT/ |
| 12 | Transición automática de estado orden | ✅ | 2025-12-07 | all_lines_processed + _check_order_completion() |
| 13 | Mensajes en chatter (auditoría) | ✅ | 2025-12-07 | Implementado en wizards y acciones |

**Leyenda**: ✅ Completado | ⏳ Pendiente | 🚧 En progreso

---

## Estado Actual del Sistema

- **Módulo**: `jewelry_purchase_client` (v18.0.1.5.0)
- **Estados de orden**: draft → blocked → available → processed
- **Estados de línea**: pending, in_inventory, to_smelting
- **Dependencias**: `jewelry_product` (v18.0.1.1.0), `stock`
- **Transición automática**: Orden pasa a "processed" cuando todas las líneas tienen estado final
- **Trazabilidad**: Modelo `jewelry.smelting.batch` para lotes de fundición

---

## ⚠️ Refactorización Requerida

### Problema 1: Botón "Process (Send to Smelting)" engañoso

**Ubicación**: `views/client_purchase_views.xml` líneas 26-30

**Código actual**:
```xml
<button name="action_process"
        string="Process (Send to Smelting)"
        type="object"
        class="btn-primary"
        invisible="state != 'available'"/>
```

**Problema**:
- El nombre sugiere que envía artículos a fundición, pero NO lo hace
- Solo marca la orden como "Processed" sin verificar el estado de las líneas
- Permite cerrar una orden con líneas aún en estado "pending"

**Solución**:
- **Eliminar** este botón completamente
- Reemplazar con los nuevos botones "Fundir Todo" y "Recepcionar Todo"
- La transición a "Processed" debe ser **automática** cuando todas las líneas estén procesadas

---

### Problema 2: Método `action_process()` sin validación

**Ubicación**: `models/client_purchase.py` líneas 213-218

**Código actual**:
```python
def action_process(self):
    for order in self:
        if order.state != 'available':
            raise UserError('Only available orders can be processed.')
        order.write({'state': 'processed'})
    return True
```

**Problema**:
- No verifica que todas las líneas tengan un estado final
- Permite marcar como procesada una orden con líneas pendientes

**Solución**:
- Opción A (Recomendada): **Eliminar** el método y usar transición automática
- Opción B: Añadir validación:
```python
def action_process(self):
    for order in self:
        if order.state != 'available':
            raise UserError('Only available orders can be processed.')
        pending = order.line_ids.filtered(lambda l: l.line_state == 'pending')
        if pending:
            raise UserError(
                f'Cannot process order. {len(pending)} lines are still pending.'
            )
        order.write({'state': 'processed'})
    return True
```

---

### Problema 3: Wizard SendToInventory no verifica completitud

**Ubicación**: `wizard/send_to_inventory_wizard.py`

**Código actual**: El wizard actualiza `line_state` pero no verifica si todas las líneas están procesadas para hacer transición automática de la orden.

**Solución**: Añadir verificación al final de `action_create_product()`:
```python
# Al final del método, después de actualizar la línea:

# Check if all lines are processed, auto-transition order
if all(line.line_state != 'pending' for line in self.line_id.order_id.line_ids):
    self.line_id.order_id.write({'state': 'processed'})
```

**Nota**: Este código ya fue añadido pero debe verificarse que funciona correctamente.

---

### Resumen de Refactorización

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `views/client_purchase_views.xml` | Eliminar botón "Process (Send to Smelting)" | 🔴 Alta |
| `models/client_purchase.py` | Eliminar o modificar `action_process()` | 🔴 Alta |
| `models/client_purchase.py` | Añadir campo `all_lines_processed` | 🟡 Media |
| `wizard/send_to_inventory_wizard.py` | Verificar auto-transición funciona | 🟢 Baja |

---

## Registro de Actividades (Chatter)

Todas las acciones importantes deben quedar registradas en el panel de actividades de la orden para auditoría y trazabilidad.

### Mensajes a Registrar

| Acción | Mensaje en Chatter | Estado |
|--------|-------------------|--------|
| Enviar línea a inventario | "Artículo '{descripción}' enviado a inventario como producto [{nombre_producto}]" | ⏳ Pendiente |
| Enviar línea a inventario (con reparación) | "Artículo '{descripción}' enviado a inventario (pendiente reparación)" | ⏳ Pendiente |
| Enviar línea a fundición | "Artículo '{descripción}' enviado a fundición" | ⏳ Pendiente |
| Fundir Todo | "Enviados {N} artículos a fundición (Lote: {ref}, Peso: {X}g, Valor: {Y}€)" | ⏳ Pendiente |
| Recepcionar Todo | "Recepcionados {N} artículos en inventario ({almacén})" | ⏳ Pendiente |
| Orden completada (auto) | "Orden procesada automáticamente. Todos los artículos han sido enviados a inventario o fundición." | ⏳ Pendiente |

### Implementación

```python
# Ejemplo: Al enviar a inventario (en wizard)
self.line_id.order_id.message_post(
    body=f"Artículo '<b>{self.line_id.description}</b>' enviado a inventario "
         f"como producto <a href='/web#id={product.id}&model=product.product'>{product.name}</a>",
    subject="Artículo enviado a inventario",
    message_type='notification',
)

# Ejemplo: Al enviar a fundición
self.order_id.message_post(
    body=f"Artículo '<b>{self.description}</b>' enviado a fundición",
    subject="Artículo enviado a fundición",
    message_type='notification',
)

# Ejemplo: Fundir Todo (en wizard)
self.purchase_id.message_post(
    body=f"Enviados <b>{len(pending_lines)}</b> artículos a fundición<br/>"
         f"<ul>"
         f"<li>Lote: <a href='/web#id={batch.id}&model=jewelry.smelting.batch'>{batch.name}</a></li>"
         f"<li>Peso total: {self.total_weight:.3f} g</li>"
         f"<li>Valor total: {self.total_value:.2f} €</li>"
         f"</ul>",
    subject="Artículos enviados a fundición",
    message_type='notification',
)

# Ejemplo: Transición automática a Processed
order.message_post(
    body="Orden procesada automáticamente. Todos los artículos han sido "
         "enviados a inventario o fundición.",
    subject="Orden completada",
    message_type='notification',
)
```

### Visualización en Chatter

```
┌─────────────────────────────────────────────────────────────┐
│ CP/2025/00003                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 Actividades                                             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  🔔 Administrator • Hoy a las 14:35                         │
│  Orden completada                                           │
│  Orden procesada automáticamente. Todos los artículos       │
│  han sido enviados a inventario o fundición.                │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  🔔 Administrator • Hoy a las 14:34                         │
│  Artículos enviados a fundición                             │
│  Enviados 3 artículos a fundición                           │
│  • Lote: SMELT/2025/0001                                    │
│  • Peso total: 45.200 g                                     │
│  • Valor total: 1,250.00 €                                  │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  🔔 Administrator • Hoy a las 14:30                         │
│  Artículo enviado a inventario                              │
│  Artículo 'Anillo oro 18k' enviado a inventario como        │
│  producto Anillo Solitario Diamante                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Diseño Técnico

### Campo line_state Ampliado (PENDIENTE)

```python
line_state = fields.Selection([
    ('pending', 'Pendiente'),
    ('in_inventory', 'En Inventario'),
    ('to_smelting', 'A Fundición'),  # NUEVO
], default='pending')
```

### Arquitectura de Flujos

```
                    ┌─────────────────────────┐
                    │   Compra Confirmada     │
                    │   (Estado: Available)   │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ Enviar a Stock  │ │ Fundir Todo │ │ Recepcionar Todo│
    │  (por línea)    │ │   (bulk)    │ │     (bulk)      │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                 │
             ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ Wizard detallado│ │Modal confirm│ │Wizard simplific.│
    │ - Nombre prod.  │ │ - Warning   │ │ - Warehouse     │
    │ - Precio venta  │ │ - Resumen   │ │ - Multiplicador │
    │ - Reparación    │ │             │ │                 │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                 │
             ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ Crea producto   │ │ Marca líneas│ │ Crea productos  │
    │ + stock move    │ │ to_smelting │ │ + stock moves   │
    │ line: inventory │ │ Crea batch  │ │ lines: inventory│
    └─────────────────┘ └─────────────┘ └─────────────────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ ¿Todas líneas != pending?│
                    │         (auto)          │
                    └───────────┬─────────────┘
                                │ SÍ
                                ▼
                    ┌─────────────────────────┐
                    │   Orden → Processed     │
                    └─────────────────────────┘
```

---

## Flujo 1: Enviar a Stock (Individual) - IMPLEMENTADO ✅

### Descripción
Desde una línea en estado "pending", el usuario puede enviar el artículo a inventario como producto vendible.

### Wizard: SendToInventoryWizard

**Modelo**: `jewelry.send.to.inventory.wizard`

**Campos del wizard**:
- `line_id`: Línea de compra (readonly)
- `warehouse_id`: Almacén destino
- `product_name`: Nombre del producto a crear
- `sale_price`: Precio de venta
- `needs_repair`: ¿Necesita reparación?
- `repair_notes`: Notas de reparación
- `repair_cost`: Coste estimado reparación

**Lógica**:
1. Crea `product.template` con `type='consu'`
2. Determina ubicación destino (stock o reparación)
3. Crea `stock.move` desde ubicación inventario
4. Actualiza `line.line_state = 'in_inventory'`
5. Muestra el producto creado

### Mockup

```
┌──────────────────────────────────────────────────┐
│         Enviar a Inventario                      │
├──────────────────────────────────────────────────┤
│ INFORMACIÓN DEL ARTÍCULO                         │
│ Descripción: Anillo oro 18k con diamante         │
│ Calidad: 18k Gold                                │
│ Peso: 5,200 g                                    │
│ Precio compra: 450,00 €                          │
│ ─────────────────────────────────────────────    │
│ DETALLES DEL PRODUCTO                            │
│ Almacén destino:    [Tienda Centro        ▼]    │
│ Nombre producto:    [Anillo oro 18k c/diamante]  │
│ Precio de venta:    [675,00___] €                │
│ ─────────────────────────────────────────────    │
│ OPCIONES DE REPARACIÓN                           │
│ ☐ Necesita reparación antes de venta             │
│   Notas: [________________________________]      │
│   Coste estimado: [________] €                   │
│ ─────────────────────────────────────────────    │
│ RESUMEN                                          │
│ Coste total: 450,00 €                            │
│ Destino: IAN'OR Mallorca / Stock                 │
│                                                  │
│         [Cancelar]        [Crear Producto]       │
└──────────────────────────────────────────────────┘
```

---

## Flujo 2: Enviar a Fundición (Individual) - PENDIENTE ⏳

### Descripción
Desde una línea en estado "pending", el usuario puede marcar el artículo como enviado a fundición.

### Implementación Propuesta

**Acción simple** (sin wizard complejo):

```python
# En jewelry.client.purchase.line
def action_send_to_smelting(self):
    """Mark this line as sent to smelting."""
    self.ensure_one()
    if self.line_state != 'pending':
        raise UserError('Solo se pueden enviar artículos pendientes a fundición.')

    self.write({'line_state': 'to_smelting'})

    # Verificar si todas las líneas están procesadas
    self._check_order_completion()
```

### Vista
Botón en la lista de líneas, similar al de "Enviar a Inventario".

---

## Flujo 3: Fundir Todo (Bulk) - PENDIENTE ⏳

### Descripción
Acción masiva para enviar TODAS las líneas pendientes a fundición con una sola confirmación.

### Wizard: SmeltAllWizard

**Modelo**: `jewelry.smelt.all.wizard`

**Características**:
- Modal de confirmación con warning
- Muestra resumen (cantidad, peso total, valor total)
- Crea lote de fundición para trazabilidad
- NO permite deshacer

### Mockup

```
┌──────────────────────────────────────────────────┐
│              Fundir Todo                         │
├──────────────────────────────────────────────────┤
│ ⚠️  ADVERTENCIA                                  │
│ Esta acción enviará TODOS los artículos          │
│ pendientes a fundición. Esta acción NO se        │
│ puede deshacer.                                  │
│ ─────────────────────────────────────────────    │
│ RESUMEN                                          │
│                                                  │
│ Artículos a fundir:     5                        │
│ Peso total:             127,500 g                │
│ Valor total:            2.340,00 €               │
│                                                  │
│ ─────────────────────────────────────────────    │
│                                                  │
│     [Cancelar]      [⚠️ Confirmar Fundición]     │
└──────────────────────────────────────────────────┘
```

### Lógica

```python
def action_confirm_smelt(self):
    self.ensure_one()

    pending_lines = self.purchase_id.line_ids.filtered(
        lambda l: l.line_state == 'pending'
    )

    if not pending_lines:
        raise UserError('No hay artículos pendientes.')

    # Crear lote de fundición (trazabilidad)
    batch = self.env['jewelry.smelting.batch'].create({
        'date': fields.Date.today(),
    })

    # Actualizar todas las líneas
    pending_lines.write({
        'line_state': 'to_smelting',
        'smelting_batch_id': batch.id,
    })

    # Log en chatter
    self.purchase_id.message_post(
        body=f"Enviados {len(pending_lines)} artículos a fundición "
             f"(Lote: {batch.name}, Peso: {self.total_weight:.3f}g)",
    )

    # Verificar transición de orden
    self._check_order_completion()

    # Notificación de éxito y cerrar
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Éxito',
            'message': f'{len(pending_lines)} artículos enviados a fundición',
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        },
    }
```

---

## Flujo 4: Recepcionar Todo (Bulk) - PENDIENTE ⏳

### Descripción
Acción masiva para crear productos de TODAS las líneas pendientes con valores por defecto.

### Wizard: ReceiveAllWizard

**Modelo**: `jewelry.receive.all.wizard`

**Características**:
- Wizard simplificado (no pide datos por línea)
- Configura almacén destino
- Opcionalmente multiplica precio compra para precio venta
- Crea productos con descripción de la línea como nombre
- NO marca reparación (se asume listo para venta)

### Mockup

```
┌──────────────────────────────────────────────────┐
│           Recepcionar Todo                       │
├──────────────────────────────────────────────────┤
│ CONFIGURACIÓN                                    │
│                                                  │
│ Almacén destino:    [IAN'OR Mallorca      ▼]    │
│                                                  │
│ Artículos a recepcionar: 5                       │
│                                                  │
│ ─────────────────────────────────────────────    │
│ PRECIO DE VENTA                                  │
│                                                  │
│ ○ Usar precio de compra como precio de venta     │
│ ● Multiplicar precio de compra por: [1,50]       │
│                                                  │
│ ─────────────────────────────────────────────    │
│ NOTA: Los productos se crearán usando la         │
│ descripción de cada línea como nombre.           │
│ Puede editar los productos después.              │
│                                                  │
│         [Cancelar]        [Confirmar]            │
└──────────────────────────────────────────────────┘
```

### Comportamiento Post-Confirmación
- Muestra notificación de éxito
- Se queda en la vista actual (orden de compra)
- La orden se marca automáticamente como "Processed" si todas las líneas están procesadas

---

## Modelo: SmeltingBatch (Trazabilidad) - PENDIENTE ⏳

### Propósito
Agrupar artículos enviados a fundición para:
- Reportes policiales
- Trazabilidad
- Reconciliación con recibos del fundidor

### Definición

```python
class SmeltingBatch(models.Model):
    _name = 'jewelry.smelting.batch'
    _description = 'Smelting Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default='New',
        copy=False,
    )
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
    )
    line_ids = fields.One2many(
        comodel_name='jewelry.client.purchase.line',
        inverse_name='smelting_batch_id',
        string='Artículos',
    )
    total_weight = fields.Float(
        string='Peso Total (g)',
        compute='_compute_totals',
        store=True,
    )
    total_value = fields.Monetary(
        string='Valor Total',
        compute='_compute_totals',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado a Fundidor'),
        ('received', 'Recibo Confirmado'),
    ], default='draft')
    smelter_id = fields.Many2one(
        comodel_name='res.partner',
        string='Fundidor',
    )
    notes = fields.Text(string='Notas')
```

### Campo en línea de compra

```python
# En jewelry.client.purchase.line
smelting_batch_id = fields.Many2one(
    comodel_name='jewelry.smelting.batch',
    string='Lote Fundición',
    readonly=True,
    index=True,
)
```

---

## Transición Automática de Estado de Orden - PENDIENTE ⏳

### Diseño
La orden debe pasar automáticamente a "Processed" cuando TODAS las líneas tengan estado final (no pending).

### Implementación con Computed Field + Automation

```python
# En jewelry.client.purchase
all_lines_processed = fields.Boolean(
    string='All Lines Processed',
    compute='_compute_all_lines_processed',
    store=True,
)

@api.depends('line_ids.line_state')
def _compute_all_lines_processed(self):
    for order in self:
        order.all_lines_processed = (
            order.line_ids and
            all(line.line_state != 'pending' for line in order.line_ids)
        )
```

```xml
<!-- Automated action -->
<record id="base_automation_auto_process" model="base.automation">
    <field name="name">Auto-Process Purchase When Lines Complete</field>
    <field name="model_id" ref="model_jewelry_client_purchase"/>
    <field name="trigger">on_write</field>
    <field name="filter_domain">[('state', '=', 'available'), ('all_lines_processed', '=', True)]</field>
    <field name="action_server_id" ref="action_auto_process"/>
</record>
```

---

## Seguridad

### Permisos por Grupo

| Acción | group_jewelry_user | group_jewelry_manager |
|--------|-------------------|----------------------|
| Enviar a Stock (individual) | ✅ | ✅ |
| Enviar a Fundición (individual) | ✅ | ✅ |
| Fundir Todo | ❌ | ✅ |
| Recepcionar Todo | ❌ | ✅ |
| Ver lotes de fundición | ✅ | ✅ |
| Gestionar lotes fundición | ❌ | ✅ |

### ACLs Necesarios (PENDIENTE)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_smelt_all_wizard_mgr,smelt.all.wizard.mgr,model_jewelry_smelt_all_wizard,jewelry_base.group_jewelry_manager,1,1,1,1
access_receive_all_wizard_mgr,receive.all.wizard.mgr,model_jewelry_receive_all_wizard,jewelry_base.group_jewelry_manager,1,1,1,1
access_smelting_batch_user,smelting.batch.user,model_jewelry_smelting_batch,jewelry_base.group_jewelry_user,1,0,0,0
access_smelting_batch_mgr,smelting.batch.mgr,model_jewelry_smelting_batch,jewelry_base.group_jewelry_manager,1,1,1,1
```

---

## Ubicación de Botones en Vista

### Header de la Orden (estado "Available")

```xml
<header>
    <!-- Botones existentes... -->

    <!-- Bulk actions - Solo managers -->
    <button name="action_open_smelt_all_wizard"
            string="Fundir Todo"
            type="object"
            class="btn-warning"
            groups="jewelry_base.group_jewelry_manager"
            invisible="state != 'available'"/>
    <button name="action_open_receive_all_wizard"
            string="Recepcionar Todo"
            type="object"
            class="btn-primary"
            groups="jewelry_base.group_jewelry_manager"
            invisible="state != 'available'"/>
</header>
```

### En Lista de Líneas

```xml
<list>
    <!-- campos existentes... -->
    <button name="action_send_to_inventory" .../>
    <button name="action_send_to_smelting"
            type="object"
            string="Fundir"
            icon="fa-fire"
            class="btn-link text-warning"
            invisible="parent.state != 'available' or line_state != 'pending'"/>
</list>
```

---

## Recomendaciones del Análisis de Best Practices

### 1. Patrón de Estado por Línea ✅
El patrón line_state + bulk actions es estándar en Odoo (similar a stock.move, purchase.order.line).

### 2. Confirmación Modal ✅
Usar TransientModel wizard para confirmaciones es la práctica recomendada:
- Consistente con UX de Odoo
- Permite extensibilidad
- Mejor control de seguridad

### 3. Feedback al Usuario ✅
Siempre retornar acciones significativas:
- Notificaciones de éxito
- Navegación a registros creados
- Resúmenes estadísticos

### 4. Trazabilidad de Fundición ✅
Crítico para reportes policiales. El modelo SmeltingBatch es necesario.

### 5. Transición Automática ✅
Usar computed field + base.automation es el patrón estándar (sale.order, purchase.order).

### 6. Optimización de Rendimiento
Para bulk operations, usar `create_multi` en lugar de loops:
```python
templates = self.env['product.template'].create([
    {...vals...} for line in pending_lines
])
```

---

## Archivos a Crear/Modificar

### Nuevos Archivos (PENDIENTE)

```
jewelry_purchase_client/
├── models/
│   └── smelting_batch.py          # NUEVO
├── wizard/
│   ├── smelt_all_wizard.py        # NUEVO
│   ├── smelt_all_wizard_views.xml # NUEVO
│   ├── receive_all_wizard.py      # NUEVO
│   └── receive_all_wizard_views.xml # NUEVO
├── views/
│   └── smelting_batch_views.xml   # NUEVO
├── data/
│   ├── smelting_sequence.xml      # NUEVO
│   └── ir_actions_server.xml      # NUEVO (automation)
└── security/
    └── ir.model.access.csv        # ACTUALIZAR
```

### Archivos a Modificar

- `models/__init__.py` - Importar smelting_batch
- `models/client_purchase_line.py` - Añadir to_smelting, smelting_batch_id
- `models/client_purchase.py` - Añadir all_lines_processed, métodos para abrir wizards
- `views/client_purchase_views.xml` - Botones bulk en header
- `wizard/__init__.py` - Importar nuevos wizards
- `__manifest__.py` - Añadir nuevos archivos

---

## Testing

### Casos de Prueba Existentes
1. ✅ Envío individual a inventario sin reparación
2. ✅ Envío individual a inventario con reparación
3. ✅ Completar reparación

### Casos de Prueba Pendientes
4. ⏳ Envío individual a fundición
5. ⏳ Fundir Todo - confirmación
6. ⏳ Fundir Todo - crea batch
7. ⏳ Recepcionar Todo - crea productos
8. ⏳ Transición automática orden → processed
9. ⏳ Seguridad - user no puede usar bulk actions
10. ⏳ Seguridad - manager puede usar bulk actions
