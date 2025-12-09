# Plan de Implementación - Compras Recuperables

## Resumen

Este documento detalla las tareas necesarias para implementar el flujo de compras recuperables (empeños) en el módulo `jewelry_purchase_client`.

**Módulo**: `jewelry_purchase_client`
**Ubicación**: `/custom-addons/jewelry_purchase_client/`
**Versión actual**: `18.0.1.8.0`

---

## Tareas de Implementación

### Fase 1: Modelo de Datos

#### Tarea 1.1: Campo Tipo de Operación
**Archivo**: `models/client_purchase.py`

- [ ] Añadir campo `operation_type` (Selection: purchase/recoverable)
- [ ] Añadir valor por defecto desde configuración
- [ ] Añadir tracking para auditoría

#### Tarea 1.2: Actualizar Estados
**Archivo**: `models/client_purchase.py`

- [ ] Añadir nuevos estados al Selection:
  - `recoverable` - Recuperable
  - `to_smelt` - A Fundir
  - `inventory` - Inventario
  - `smelted` - Fundido
  - `recovered` - Recuperado
  - `sold` - Venta
- [ ] Eliminar estado `confirmed` (usar `blocked` directamente)
- [ ] Eliminar estado `processed` (usar estados finales específicos)

#### Tarea 1.3: Campos de Recuperación
**Archivo**: `models/client_purchase.py`

- [ ] Añadir `recovery_margin_percent` (Float)
- [ ] Añadir `recovery_duration_days` (Integer)
- [ ] Añadir `recovery_deadline` (Date, computed)
- [ ] Añadir `daily_surcharge_percent` (Float)
- [ ] Añadir campos computed:
  - `recovery_base_amount`
  - `days_overdue`
  - `current_surcharge`
  - `total_recovery_amount`
  - `can_recover`
- [ ] Añadir campos de auditoría de recuperación:
  - `recovery_date`
  - `recovery_user_id`
  - `recovery_amount_paid`
  - `recovery_pos_statement_line_id`

#### Tarea 1.4: Métodos Computed
**Archivo**: `models/client_purchase.py`

- [ ] Implementar `_compute_recovery_deadline()`
- [ ] Implementar `_compute_recovery_amounts()`
- [ ] Implementar `_compute_can_recover()`

---

### Fase 2: Lógica de Negocio

#### Tarea 2.1: Método de Recuperación
**Archivo**: `models/client_purchase.py`

- [ ] Implementar `action_recover()` - abre wizard
- [ ] Implementar `_execute_recovery()` - ejecuta recuperación
- [ ] Implementar `_create_recovery_cash_in()` - entrada de caja

#### Tarea 2.2: Actualizar Transiciones de Estado
**Archivo**: `models/client_purchase.py`

- [ ] Modificar `action_confirm()` para ir a `blocked`
- [ ] Actualizar `action_mark_available()` con lógica de recuperables
- [ ] Añadir `action_send_to_smelt()` a nivel de orden
- [ ] Añadir `action_receive_to_inventory()` a nivel de orden
- [ ] Añadir `action_confirm_smelt()` para estado final
- [ ] Añadir `action_cancel_smelt()` para volver a disponible

#### Tarea 2.3: Actualizar Cron Jobs
**Archivo**: `models/client_purchase.py` y `data/cron_data.xml`

- [ ] Modificar `cron_check_blocking_period()`:
  - Si recuperable y plazo > bloqueo → estado `recoverable`
  - Si no → estado `available`
- [ ] Añadir `cron_check_recovery_deadline()`:
  - Transicionar de `recoverable` a `available` cuando expira plazo

---

### Fase 3: Wizard de Recuperación

#### Tarea 3.1: Crear Modelo del Wizard
**Archivo nuevo**: `wizard/recovery_wizard.py`

- [ ] Crear modelo `jewelry.recovery.wizard`
- [ ] Campos: purchase_id, recovery_amount, payment_method
- [ ] Campos relacionados informativos
- [ ] Método `action_confirm_recovery()`

#### Tarea 3.2: Vista del Wizard
**Archivo nuevo**: `wizard/recovery_wizard_views.xml`

- [ ] Crear formulario del wizard
- [ ] Mostrar información del empeño
- [ ] Mostrar desglose: precio + margen + recargo
- [ ] Selector de método de pago
- [ ] Botón de confirmación

#### Tarea 3.3: Registrar Wizard
**Archivos**: `wizard/__init__.py`, `__manifest__.py`

- [ ] Importar wizard en `__init__.py`
- [ ] Añadir vista a `__manifest__.py`
- [ ] Añadir permisos en `ir.model.access.csv`

---

### Fase 4: Vistas

#### Tarea 4.1: Actualizar Formulario Principal
**Archivo**: `views/client_purchase_views.xml`

- [ ] Añadir campo `operation_type` (radio buttons)
- [ ] Grupo condicional para campos de recuperación:
  - `attrs="{'invisible': [('operation_type', '!=', 'recoverable')]}"`
- [ ] Añadir campos de recuperación:
  - Margen, duración, fecha límite, recargo
- [ ] Añadir sección informativa "Recuperación":
  - Importe base, días vencido, recargo actual, total
- [ ] Botón "Recuperar" condicional
- [ ] Actualizar statusbar con nuevos estados

#### Tarea 4.2: Actualizar Vista Lista
**Archivo**: `views/client_purchase_views.xml`

- [ ] Añadir columna `operation_type`
- [ ] Añadir columna `recovery_deadline` (condicional)
- [ ] Añadir columna `total_recovery_amount` (condicional)
- [ ] Decoración por estado (colores)

#### Tarea 4.3: Actualizar Filtros de Búsqueda
**Archivo**: `views/client_purchase_views.xml`

- [ ] Filtro por tipo de operación
- [ ] Filtro "Empeños por vencer" (próximos 7 días)
- [ ] Filtro "Empeños vencidos"
- [ ] Grupo por tipo de operación

---

### Fase 5: Seguridad

#### Tarea 5.1: Permisos del Wizard
**Archivo**: `security/ir.model.access.csv`

- [ ] Añadir permisos para `jewelry.recovery.wizard`

#### Tarea 5.2: Restricciones de Acciones
**Archivo**: `models/client_purchase.py`

- [ ] Validar permisos en `action_recover()`
- [ ] Validar permisos en acciones de fundición

---

### Fase 6: Configuración

#### Tarea 6.1: Parámetros de Configuración
**Archivo**: `jewelry_base/models/res_config_settings.py`

- [ ] Añadir `jewelry_default_margin`
- [ ] Añadir `jewelry_default_surcharge`
- [ ] Añadir `jewelry_default_recovery_days`

#### Tarea 6.2: Vista de Configuración
**Archivo**: `jewelry_base/views/res_config_settings_views.xml`

- [ ] Añadir sección "Empeños" en configuración
- [ ] Campos de valores por defecto

---

### Fase 7: Datos y Migración

#### Tarea 7.1: Migración de Datos Existentes
**Archivo nuevo**: `migrations/18.0.2.0.0/pre-migrate.py`

- [ ] Establecer `operation_type = 'purchase'` en registros existentes
- [ ] Mapear estados antiguos a nuevos

#### Tarea 7.2: Actualizar Secuencia (opcional)
**Archivo**: `data/sequence_data.xml`

- [ ] Considerar prefijo diferente para recuperables (ej: EMP vs CP)

---

### Fase 8: Testing

#### Tarea 8.1: Tests Unitarios
**Archivo nuevo**: `tests/test_recoverable_purchase.py`

- [ ] Test creación de compra recuperable
- [ ] Test cálculo de importes de recuperación
- [ ] Test recuperación a tiempo (sin recargo)
- [ ] Test recuperación tarde (con recargo)
- [ ] Test transiciones automáticas (cron)
- [ ] Test integración con POS (entrada de caja)

#### Tarea 8.2: Tests de Flujo Completo
**Archivo nuevo**: `tests/test_purchase_flow.py`

- [ ] Test flujo compra normal: draft → blocked → available → smelted
- [ ] Test flujo compra normal: draft → blocked → available → inventory → sold
- [ ] Test flujo recuperable: draft → blocked → recoverable → recovered
- [ ] Test flujo recuperable tarde: draft → blocked → recoverable → available → recovered

---

## Orden de Ejecución Recomendado

```
1. Fase 1: Modelo de Datos
   └── Tareas 1.1, 1.2, 1.3, 1.4

2. Fase 6: Configuración (puede hacerse en paralelo)
   └── Tareas 6.1, 6.2

3. Fase 2: Lógica de Negocio
   └── Tareas 2.1, 2.2, 2.3

4. Fase 3: Wizard de Recuperación
   └── Tareas 3.1, 3.2, 3.3

5. Fase 4: Vistas
   └── Tareas 4.1, 4.2, 4.3

6. Fase 5: Seguridad
   └── Tareas 5.1, 5.2

7. Fase 7: Datos y Migración
   └── Tareas 7.1, 7.2

8. Fase 8: Testing
   └── Tareas 8.1, 8.2
```

---

## Checklist de Verificación

Antes de dar por completada la implementación:

- [ ] Todos los tests pasan
- [ ] El flujo de compra normal sigue funcionando
- [ ] El flujo de compra recuperable funciona end-to-end
- [ ] La integración con POS funciona (salida y entrada de caja)
- [ ] Los crons de transición automática funcionan
- [ ] Las vistas muestran/ocultan campos correctamente
- [ ] Los cálculos de recuperación son correctos
- [ ] Los permisos están correctamente configurados
- [ ] La migración de datos existentes funciona
- [ ] La documentación está actualizada

---

## Dependencias Externas

No se requieren nuevas dependencias. El módulo ya tiene:
- `mail` - para chatter
- `stock` - para inventario
- `point_of_sale` - para integración con caja
- `jewelry_base` - para configuración
- `jewelry_partner` - para datos de cliente
- `jewelry_product` - para calidades de material

---

## Notas Adicionales

### Compatibilidad

- Los registros existentes (compras normales) seguirán funcionando sin cambios
- El campo `operation_type` tendrá valor por defecto `'purchase'`
- Los estados antiguos se migrarán automáticamente

### UX Consideraciones

- El selector de tipo de operación debe ser visible solo en estado borrador
- Los campos de recuperación deben ocultarse para compras normales
- El botón "Recuperar" debe ser prominente en estados recuperables
- Mostrar claramente el importe a cobrar antes de confirmar

### Rendimiento

- Los campos computed de recuperación deben ser eficientes
- Considerar `store=True` para campos que se consultan frecuentemente
- Los crons deben procesar en lotes si hay muchos registros
