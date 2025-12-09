# Flujo de Estados - Sistema de Compraventa

## Diagrama de Estados

```
┌─────────────┐
│  Borrador   │
└──────┬──────┘
       │ [Confirmar]
       ▼
┌─────────────────┐
│ Bloqueo Policial│───────────────────────┐
└────────┬────────┘                       │
         │ bloqueo superado               │ [Recuperar]
    ┌────┴────┐                           │ (durante bloqueo)
    │         │                           │
    │ ¿Recuperable?──SI──►┌───────────┐   │
    │         │           │Recuperable│───┼──► Recuperado
    │         │           └─────┬─────┘   │    (precio+margen)
    │         │                 │ plazo   │
    │  NO     │                 │ expira  │
    │         │                 ▼         │
    └────┬────┴────────►┌───────────┐     │
         │              │ Disponible│─────┘ [Recuperar]
         ▼              └─────┬─────┘       (precio+margen+recargo)
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌─────────┐ ┌─────────┐ ┌──────────┐
              │A Fundir │ │Inventario│ │Recuperado│
              └────┬────┘ └────┬────┘ └──────────┘
           [Cancelar]         │
              ┌────┘          ▼
              ▼          ┌─────────┐
         ┌─────────┐     │A Fundir │
         │ Fundido │     └────┬────┘
         └─────────┘          │
              ▲               ▼
              │          ┌─────────┐
              └──────────│ Fundido │
                         └─────────┘

              ┌─────────┐
              │  Venta  │ (desde Inventario, vía sale.order)
              └─────────┘
```

## Estados del Sistema

| Estado | Código | Tipo | Aplica a | Descripción |
|--------|--------|------|----------|-------------|
| Borrador | `draft` | Inicial | Ambos | Compra sin confirmar |
| Bloqueo Policial | `blocked` | Intermedio | Ambos | Período legal obligatorio (14 días por defecto) |
| Recuperable | `recoverable` | Intermedio | Solo recuperables | Cliente puede recuperar a tiempo (sin recargo) |
| Disponible | `available` | Intermedio | Ambos | Artículos disponibles para procesar |
| A Fundir | `to_smelt` | Intermedio | Ambos | En proceso de fundición |
| Inventario | `inventory` | Semi-final | Ambos | Artículo en stock de la tienda |
| Fundido | `smelted` | **Final** | Ambos | Material fundido |
| Recuperado | `recovered` | **Final** | Solo recuperables | Cliente recuperó el artículo |
| Venta | `sold` | **Final** | Ambos | Artículo vendido (vía sale.order) |
| Cancelado | `cancelled` | **Final** | Ambos | Operación cancelada |

## Tabla de Transiciones

| # | Desde | Hacia | Acción | Trigger | Condición | Aplica a |
|---|-------|-------|--------|---------|-----------|----------|
| 1 | `draft` | `blocked` | Confirmar | Manual | Tiene líneas | Ambos |
| 2 | `blocked` | `recovered` | Recuperar | Manual | `operation_type == 'recoverable'` | Recuperables |
| 3 | `blocked` | `recoverable` | (auto) | Cron | Fin bloqueo AND `recovery_deadline > blocking_end_date` | Recuperables |
| 4 | `blocked` | `available` | (auto) | Cron | Fin bloqueo AND (`operation_type == 'purchase'` OR `recovery_deadline <= blocking_end_date`) | Ambos |
| 5 | `recoverable` | `recovered` | Recuperar | Manual | - | Recuperables |
| 6 | `recoverable` | `available` | (auto) | Cron | `recovery_deadline` alcanzada | Recuperables |
| 7 | `available` | `recovered` | Recuperar | Manual | `operation_type == 'recoverable'` | Recuperables |
| 8 | `available` | `to_smelt` | A Fundir | Manual | - | Ambos |
| 9 | `available` | `inventory` | Recepcionar | Manual | - | Ambos |
| 10 | `to_smelt` | `available` | Cancelar | Manual | - | Ambos |
| 11 | `to_smelt` | `smelted` | Confirmar fundición | Manual | - | Ambos |
| 12 | `inventory` | `to_smelt` | A Fundir | Manual | - | Ambos |
| 13 | `inventory` | `sold` | (auto) | Hook | Producto vendido en sale.order | Ambos |
| 14 | `draft` | `cancelled` | Cancelar | Manual | - | Ambos |
| 15 | `blocked` | `cancelled` | Cancelar | Manual | - | Ambos |

## Transiciones Automáticas (Cron)

Se ejecutan diariamente para actualizar estados según fechas:

### 1. Fin de Bloqueo Policial

```python
def cron_check_blocking_period(self):
    """Ejecutar diariamente para transicionar órdenes que terminan bloqueo."""
    today = fields.Date.today()

    # Órdenes en bloqueo que terminan hoy
    orders = self.search([
        ('state', '=', 'blocked'),
        ('blocking_end_date', '<=', today),
    ])

    for order in orders:
        if order.operation_type == 'recoverable':
            # Si fecha límite recuperación > hoy → estado Recuperable
            if order.recovery_deadline and order.recovery_deadline > today:
                order.write({'state': 'recoverable'})
            else:
                # Plazo de empeño ya expiró → Disponible
                order.write({'state': 'available'})
        else:
            # Compra normal → Disponible
            order.write({'state': 'available'})
```

### 2. Expiración de Plazo de Recuperación

```python
def cron_check_recovery_deadline(self):
    """Ejecutar diariamente para transicionar empeños que expiran."""
    today = fields.Date.today()

    # Empeños en estado Recuperable que expiran hoy
    orders = self.search([
        ('state', '=', 'recoverable'),
        ('operation_type', '=', 'recoverable'),
        ('recovery_deadline', '<=', today),
    ])

    orders.write({'state': 'available'})
```

## Acciones por Estado

### Estado: Borrador (`draft`)

| Acción | Botón | Método |
|--------|-------|--------|
| Confirmar | `action_confirm` | Valida líneas, registra salida de caja, pasa a `blocked` |
| Cancelar | `action_cancel` | Pasa a `cancelled` |

### Estado: Bloqueo Policial (`blocked`)

| Acción | Botón | Método | Condición |
|--------|-------|--------|-----------|
| Recuperar | `action_recover` | Registra entrada de caja, pasa a `recovered` | Solo recuperables |
| Forzar desbloqueo | `action_force_unlock` | Salta bloqueo (requiere permiso especial) | - |
| Cancelar | `action_cancel` | Revierte caja, pasa a `cancelled` | - |

### Estado: Recuperable (`recoverable`)

| Acción | Botón | Método |
|--------|-------|--------|
| Recuperar | `action_recover` | Registra entrada de caja (precio + margen), pasa a `recovered` |

### Estado: Disponible (`available`)

| Acción | Botón | Método | Condición |
|--------|-------|--------|-----------|
| Recuperar | `action_recover` | Entrada de caja (precio + margen + recargo), pasa a `recovered` | Solo recuperables |
| A Fundir | `action_send_to_smelt` | Pasa a `to_smelt` | - |
| Recepcionar | `action_receive_to_inventory` | Crea producto, stock.move, pasa a `inventory` | - |

### Estado: A Fundir (`to_smelt`)

| Acción | Botón | Método |
|--------|-------|--------|
| Cancelar | `action_cancel_smelt` | Vuelve a `available` |
| Confirmar fundición | `action_confirm_smelt` | Pasa a `smelted` |

### Estado: Inventario (`inventory`)

| Acción | Botón | Método |
|--------|-------|--------|
| A Fundir | `action_send_to_smelt` | Pasa a `to_smelt` |

### Estados Finales

Los estados `smelted`, `recovered`, `sold` y `cancelled` no tienen acciones disponibles (son terminales).

## Reglas de Negocio

### 1. Período de Bloqueo Policial
- Configurable en ajustes (`jewelry.blocking_days`, default: 14)
- Obligatorio para todas las compras
- Durante el bloqueo, el artículo no puede fundirse ni venderse
- El cliente puede recuperar un empeño durante el bloqueo

### 2. Estado "Recuperable"
- Solo aplica si `operation_type == 'recoverable'`
- Solo existe si `recovery_deadline > blocking_end_date`
- Si el plazo del empeño es menor o igual al bloqueo, pasa directamente a Disponible

### 3. Recuperación
- Posible en estados: `blocked`, `recoverable`, `available`
- Precio varía según el momento (ver fórmulas en README.md)
- Genera entrada de caja en la sesión POS activa

### 4. Fundición
- Solo desde estados `available` o `inventory`
- Se puede cancelar mientras está en `to_smelt`
- `smelted` es estado final e irreversible
