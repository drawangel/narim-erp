# Análisis de Cobertura: ERP Joyería/Compraventa con Odoo 18 CE

## Información del Proyecto

**Tipo**: Producto SaaS basado en Odoo 18 Community Edition
**Distribución**: Licencia comercial para joyerías, casas de empeño y negocios de compraventa
**Mercado objetivo**: Negocios de joyería con operaciones de compra a particulares y empeños

---

## Resumen Ejecutivo

Este documento analiza la cobertura de funcionalidades para un ERP vertical de joyería/compraventa utilizando Odoo 18 Community Edition como base. Se organiza en tres categorías:

1. **Out-of-the-Box (OOTB)**: Funcionalidades cubiertas sin desarrollo
2. **Configuración Avanzada**: Requieren setup pero no código
3. **Desarrollo Personalizado**: Requieren módulos custom

---

# PARTE 1: FUNCIONALIDADES CUBIERTAS OUT-OF-THE-BOX

## 1.1 Gestión de Clientes

### Módulos: `contacts`, `base`, `l10n_latam_base`

| Campo Requerido | Campo Odoo | Módulo |
|-----------------|------------|--------|
| Nombre | `name` | `base` |
| Apellidos | `name` (completo) | `base` |
| Dirección | `street`, `street2`, `city`, `zip`, `state_id`, `country_id` | `base` |
| Teléfono | `phone`, `mobile` | `base` |
| Email | `email` | `base` |
| DNI/NIF | `vat` | `base` |
| Tipo de identificación | `l10n_latam_identification_type_id` | `l10n_latam_base` |
| Foto del contacto | `image_1920`, `image_512`, `image_128` | `base` |

### Tipos de Identificación Soportados (l10n_latam_base)
- DNI (Documento Nacional de Identidad)
- Pasaporte
- NIE (Número de Identidad de Extranjero)
- NIF (Número de Identificación Fiscal)
- CIF (Código de Identificación Fiscal)
- Y 80+ tipos adicionales para LATAM

### Capacidades Adicionales Incluidas
- Historial de comunicaciones (chatter)
- Categorización por etiquetas
- Geolocalización
- Portal de cliente
- Múltiples direcciones por contacto

---

## 1.2 Compras a Proveedor (Abastecimiento)

### Módulos: `purchase`, `purchase_stock`, `stock`

**NOTA:** El menú principal "Compras" ha sido renombrado a **"Compras Proveedor"** para distinguirlo de las compras de oro a particulares.

Odoo cubre **completamente** el flujo de compras a proveedores de joyería y relojería.

| Funcionalidad | Cobertura | Módulo |
|---------------|-----------|--------|
| Crear pedidos a proveedor | ✅ Completo | `purchase` |
| Gestionar proveedores | ✅ Completo | `base`, `purchase` |
| Recepción de mercancía | ✅ Completo | `purchase_stock` |
| Distribución a tiendas | ✅ Completo | `stock` |
| Precios por proveedor | ✅ Completo | `purchase` |
| Histórico de compras | ✅ Completo | `purchase` |

### Flujo Estándar de Compra a Proveedor
```
1. Crear Solicitud de Presupuesto (RFQ)
2. Enviar al proveedor
3. Confirmar Pedido de Compra
4. Recibir mercancía en almacén central
5. Transferir a tiendas (transferencias internas)
```

---

## 1.3 Multi-Tienda / Multi-Almacén

### Módulo: `stock`

Odoo soporta nativamente múltiples tiendas/almacenes.

| Funcionalidad | Cobertura | Configuración |
|---------------|-----------|---------------|
| Almacén por tienda | ✅ Completo | Crear un `stock.warehouse` por tienda |
| Transferencias entre tiendas | ✅ Completo | Transferencias internas |
| Stock por ubicación | ✅ Completo | Ubicaciones jerárquicas |
| Trazabilidad | ✅ Completo | Lotes y números de serie |

### Configuración Sugerida
```
Almacenes:
├── Central
│   ├── Stock
│   ├── Recepción
│   └── Expedición
├── Tienda 1
│   └── Stock
├── Tienda 2
│   └── Stock
└── Tienda N
    └── Stock
```

---

## 1.4 Ventas a Cliente Final

### Módulos: `sale`, `sale_stock`, `sale_management`

| Funcionalidad | Cobertura | Módulo |
|---------------|-----------|--------|
| Crear presupuestos | ✅ Completo | `sale` |
| Confirmar ventas | ✅ Completo | `sale` |
| Gestión de entregas | ✅ Completo | `sale_stock` |
| Facturación | ✅ Completo | `sale`, `account` |
| Portal de cliente | ✅ Completo | `sale` |
| Histórico por cliente | ✅ Completo | `sale` |

### Flujo Estándar de Venta
```
1. Crear Presupuesto
2. Enviar al cliente (opcional)
3. Confirmar Pedido de Venta
4. Preparar entrega
5. Facturar
6. Registrar pago
```

---

## 1.5 Servicios de Taller

### Módulos: `repair`, `sale_service`

El módulo `repair` de Odoo CE cubre las necesidades de taller de joyería.

| Funcionalidad | Cobertura | Módulo |
|---------------|-----------|--------|
| Órdenes de reparación | ✅ Completo | `repair` |
| Presupuesto de reparación | ✅ Completo | `repair` |
| Añadir piezas/materiales | ✅ Completo | `repair` |
| Cobrar por mano de obra | ✅ Completo | `repair` |
| Seguimiento de estado | ✅ Completo | `repair` |
| Generar factura | ✅ Completo | `repair` |

### Flujo de Reparación
```
1. Recibir artículo del cliente
2. Crear Orden de Reparación
3. Diagnosticar y presupuestar
4. Cliente confirma
5. Ejecutar reparación
6. Facturar y entregar
```

---

## 1.6 Subcontratación (Compostaje)

### Módulos: `purchase`, `purchase_repair`

Para servicios externos (talleres de terceros).

| Funcionalidad | Cobertura | Módulo |
|---------------|-----------|--------|
| Pedido a taller externo | ✅ Completo | `purchase` |
| Vinculación con reparación | ✅ Completo | `purchase_repair` |
| Recepción de trabajo | ✅ Completo | `purchase_stock` |
| Pago a proveedor | ✅ Completo | `account` |

### Configuración
1. Crear proveedores de tipo "Servicio de Compostaje"
2. Crear productos de servicio para cada tipo de trabajo
3. Usar `purchase_repair` para vincular con órdenes de reparación internas

---

## 1.7 Formas de Pago

### Módulos: `account`, `payment`, `payment_*`

| Forma de Pago | Cobertura | Módulo/Configuración |
|---------------|-----------|----------------------|
| Efectivo | ✅ Completo | Diario de Caja |
| Tarjeta de Crédito | ✅ Completo | `payment_stripe`, `payment_adyen`, etc. |
| PayPal | ✅ Completo | `payment_paypal` |
| Transferencia Bancaria | ✅ Completo | Diario Bancario |
| Bizum | ✅ Configurable | Diario personalizado |

### Proveedores de Pago Incluidos (20+)
- Stripe, PayPal, Adyen, Authorize.net
- Mollie, Flutterwave, Razorpay
- Mercado Pago (LATAM)
- Y muchos más...

### Configuración de Métodos Locales (Bizum, etc.)
Crear un diario de pago personalizado:
```
Nombre: [Método de pago]
Tipo: Banco
Cuenta: [Cuenta bancaria vinculada]
```

---

## 1.8 Control de Acceso (RBAC)

### Módulo: `base`

Odoo tiene un sistema robusto de control de acceso.

| Funcionalidad | Cobertura | Mecanismo |
|---------------|-----------|-----------|
| Definir roles | ✅ Completo | `res.groups` |
| Permisos CRUD por modelo | ✅ Completo | `ir.model.access` (ACLs) |
| Filtros por registro | ✅ Completo | `ir.rule` (Record Rules) |
| Ocultar campos | ✅ Completo | Atributo `groups` en campos |
| Ocultar menús | ✅ Completo | Atributo `groups` en menús |
| Ocultar botones | ✅ Completo | Atributo `groups` en botones |

### Estructura de Roles Sugerida

```
Operador (group_jewelry_user)
├── Puede crear/editar compras a particular
├── Puede crear/editar empeños
├── Puede ver informes
└── NO puede modificar configuración

Administrador (group_jewelry_manager)
├── Hereda de Operador
├── Puede modificar días de bloqueo policial
├── Puede modificar márgenes globales
└── Acceso completo a configuración
```

---

## 1.9 Attachments y Documentos

### Módulos: `base`, `mail`

| Funcionalidad | Cobertura | Módulo |
|---------------|-----------|--------|
| Adjuntar archivos | ✅ Completo | `ir.attachment` |
| Fotos de productos | ✅ Completo | `product` |
| Documentos por registro | ✅ Completo | `mail` (chatter) |
| Vista previa | ✅ Completo | `web` |

---

## 1.10 Productos y Atributos

### Módulos: `product`, `stock`

| Funcionalidad | Cobertura | Configuración |
|---------------|-----------|---------------|
| Catálogo de productos | ✅ Completo | `product.template` |
| Peso en gramos | ✅ Completo | Campo `weight` + UoM |
| Variantes (talla, color) | ✅ Completo | Atributos de producto |
| Kilataje | ✅ Configurable | Crear atributo "Kilataje" |
| Lotes/Series | ✅ Completo | Tracking por lote/serie |
| Fotos de producto | ✅ Completo | `image_1920` |
| Categorías | ✅ Completo | `product.category` |

### Configuración de Kilataje como Atributo
```
Atributo: Kilataje
Valores: 24k, 22k, 18k, 14k, 9k, Plata, Otros
Tipo de visualización: Radio/Selector
```

---

# PARTE 2: REQUIERE CONFIGURACIÓN AVANZADA

## 2.1 Fotos de DNI (Frontal y Reverso)

**Solución**: Usar `ir.attachment` vinculado al `res.partner`.

El chatter de contactos permite adjuntar documentos, pero para una UX óptima se recomienda crear campos específicos (ver Parte 3).

## 2.2 Fotografías por Línea de Compra/Empeño

**Solución**: Adjuntar imágenes usando el sistema de attachments de Odoo.

Cada línea puede tener attachments vinculados mediante `res_model` y `res_id`.

---

# PARTE 3: REQUIERE DESARROLLO DE MÓDULOS

## Convención de Nomenclatura

Todos los módulos usan el prefijo `jewelry_` para identificar el vertical de joyería/compraventa:

| Módulo | Descripción |
|--------|-------------|
| `jewelry_base` | Configuración base, grupos y parámetros |
| `jewelry_partner` | Extensiones de contactos (DNI, etc.) |
| `jewelry_purchase_client` | Compras a particulares |
| `jewelry_pawn` | Sistema de empeños |
| `jewelry_product` | Extensiones de producto |
| `jewelry_report` | Informes policiales y reportes |

---

## 3.1 Módulo `jewelry_partner` (Complejidad: Baja) ✅ IMPLEMENTADO

### Objetivo
Extender `res.partner` con campos específicos para documentación de clientes.

### Campos a Añadir
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    id_document_front = fields.Image(
        string='Documento ID (Frontal)',
        max_width=1920,
        max_height=1920
    )
    id_document_back = fields.Image(
        string='Documento ID (Reverso)',
        max_width=1920,
        max_height=1920
    )
```

### Estimación: 4-8 horas

---

## 3.2 Módulo `jewelry_purchase_client` (Complejidad: Alta) ✅ IMPLEMENTADO

### Objetivo
Sistema unificado de compras a particulares que incluye:
- **Compras normales**: El cliente vende definitivamente
- **Compras recuperables (empeños)**: El cliente puede recuperar pagando precio + margen + recargo

> **Decisión de diseño**: Se integran empeños y compras en un solo módulo porque el negocio los ve como variantes del mismo proceso.

### Estado Actual de Implementación

El módulo base ya existe con:
- ✅ Modelo principal `jewelry.client.purchase`
- ✅ Modelo de líneas `jewelry.client.purchase.line`
- ✅ Período de bloqueo policial
- ✅ Integración con POS (salida de caja)
- ✅ Fotos por línea
- ✅ Wizards para enviar a inventario/fundición
- ✅ Lotes de fundición (`jewelry.smelting.batch`)

**Completado**: Flujo de compras recuperables (empeños) ✅

### Diagrama de Estados Unificado

```
┌─────────────┐
│  Borrador   │
└──────┬──────┘
       │ confirmar
       ▼
┌─────────────────┐
│ Bloqueo Policial│───────────────────────┐
└────────┬────────┘                       │
         │ bloqueo superado               │ cliente recupera
    ┌────┴────┐                           │ (durante bloqueo)
    │         │                           │
    │ ¿Recuperable?──SI──►┌───────────┐   │
    │         │           │Recuperable│───┼──► Recuperado
    │         │           └─────┬─────┘   │    (precio+margen)
    │         │                 │ plazo   │
    │  NO     │                 │ expira  │
    │         │                 ▼         │
    └────┬────┴────────►┌───────────┐     │
         │              │ Disponible│─────┘ cliente recupera
         ▼              └─────┬─────┘       (precio+margen+recargo)
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌─────────┐ ┌─────────┐ ┌──────────┐
              │A Fundir │ │Inventario│ │Recuperado│
              └────┬────┘ └────┬────┘ └──────────┘
           Cancelar│           │
              ┌────┘           ▼
              ▼           ┌─────────┐
         ┌─────────┐      │  Venta  │
         │ Fundido │      └─────────┘
         └─────────┘
```

### Campo Tipo de Operación (NUEVO)

```python
operation_type = fields.Selection([
    ('purchase', 'Compra'),           # Compra normal, no recuperable
    ('recoverable', 'Recuperable'),   # Empeño, cliente puede recuperar
], string='Tipo de Operación', default='purchase', required=True)
```

### Estados del Modelo (ACTUALIZADO)

```python
state = fields.Selection([
    ('draft', 'Borrador'),
    ('blocked', 'Bloqueo Policial'),
    ('recoverable', 'Recuperable'),      # NUEVO: solo para empeños
    ('available', 'Disponible'),
    ('to_smelt', 'A Fundir'),            # NUEVO
    ('inventory', 'Inventario'),         # Renombrado
    ('smelted', 'Fundido'),              # NUEVO: estado final
    ('recovered', 'Recuperado'),         # NUEVO: cliente recuperó
    ('sold', 'Venta'),                   # NUEVO: vendido desde inventario
    ('cancelled', 'Cancelado'),
], default='draft')
```

### Campos Específicos para Empeños (NUEVO)

```python
# Solo visibles/requeridos cuando operation_type == 'recoverable'
recovery_margin_percent = fields.Float(
    string='Margen Recuperación (%)',
    help='Porcentaje sobre el precio de compra para recuperación'
)
recovery_deadline = fields.Date(
    string='Fecha Límite Recuperación',
    help='Fecha hasta la que el cliente puede recuperar sin recargo'
)
daily_surcharge_percent = fields.Float(
    string='Recargo Diario (%)',
    digits=(5, 2),
    help='Porcentaje diario sobre el precio si recupera después del plazo'
)

# Campos calculados
recovery_base_amount = fields.Monetary(
    string='Importe Recuperación Base',
    compute='_compute_recovery_amounts',
    help='Precio compra + margen'
)
days_overdue = fields.Integer(
    string='Días Vencido',
    compute='_compute_recovery_amounts',
)
current_surcharge = fields.Monetary(
    string='Recargo Actual',
    compute='_compute_recovery_amounts',
)
total_recovery_amount = fields.Monetary(
    string='Total a Pagar Hoy',
    compute='_compute_recovery_amounts',
    help='Importe total que debe pagar el cliente para recuperar'
)
```

### Transiciones de Estado

| Desde | Hacia | Acción | Aplica a |
|-------|-------|--------|----------|
| Borrador | Bloqueo Policial | Confirmar | Ambos |
| Bloqueo Policial | Recuperable | Auto (fin bloqueo) | Solo recuperable (si plazo > bloqueo) |
| Bloqueo Policial | Disponible | Auto (fin bloqueo) | Normal, o recuperable (si plazo ≤ bloqueo) |
| Bloqueo Policial | Recuperado | Cliente recupera | Solo recuperable |
| Recuperable | Recuperado | Cliente recupera a tiempo | Solo recuperable |
| Recuperable | Disponible | Auto (plazo empeño vence) | Solo recuperable |
| Disponible | A Fundir | Enviar a fundición | Ambos |
| Disponible | Inventario | Recepcionar en stock | Ambos |
| Disponible | Recuperado | Cliente recupera tarde | Solo recuperable |
| A Fundir | Disponible | Cancelar fundición | Ambos |
| A Fundir | Fundido | Confirmar fundición | Ambos |
| Inventario | A Fundir | Enviar a fundición | Ambos |
| Inventario | Venta | Venta realizada | Ambos |

### Precios de Recuperación

| Momento de recuperación | Cálculo |
|-------------------------|---------|
| Durante bloqueo policial | `precio_compra + (precio_compra × margen%)` |
| En estado "Recuperable" (a tiempo) | `precio_compra + (precio_compra × margen%)` |
| En estado "Disponible" (tarde) | `precio_compra + (precio_compra × margen%) + (precio_compra × recargo_diario% × días_vencido)` |

### Integración con Odoo Estándar

| Estado en este modelo | Acción en Odoo |
|-----------------------|----------------|
| **Inventario** | Crea `product.product` + `stock.move` → entra a stock |
| **Venta** | El producto se vendió vía `sale.order` |
| **Fundido** | Material procesado, lote de fundición completado |
| **Recuperado** | Cliente recuperó, genera entrada de caja |

### Estimación Actualizada

| Componente | Estado | Horas |
|------------|--------|-------|
| Modelo base y líneas | ✅ Hecho | - |
| Bloqueo policial | ✅ Hecho | - |
| Integración POS | ✅ Hecho | - |
| Fundición básica | ✅ Hecho | - |
| **Tipo de operación (recuperable)** | ✅ Hecho | - |
| **Nuevos estados** | ✅ Hecho | - |
| **Campos de empeño** | ✅ Hecho | - |
| **Lógica de recuperación** | ✅ Hecho | - |
| **Cálculos automáticos** | ✅ Hecho | - |
| **Cron transiciones automáticas** | ✅ Hecho | - |
| **Tests** | ⏳ Pendiente | 8-12h |
| **Total pendiente** | | **8-12h** |

---

## ~~3.3 Módulo `jewelry_pawn`~~ (INTEGRADO EN `jewelry_purchase_client`)

> **NOTA**: La funcionalidad de empeños se ha integrado en el módulo `jewelry_purchase_client` como "Compras Recuperables". Ver sección 3.2 para detalles.

~~### Objetivo~~
~~Sistema completo de empeños (compras recuperables).~~

Este módulo ya no se desarrollará de forma independiente.

---

## 3.4 Módulo `jewelry_report` (Complejidad: Media)

### Objetivo
Generación de informes para autoridades y reportes operativos.

### Funcionalidades
```python
class PoliceReportWizard(models.TransientModel):
    _name = 'jewelry.report.police.wizard'
    _description = 'Generador de Informe Policial'

    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta', required=True)
    report_type = fields.Selection([
        ('all', 'Todos'),
        ('purchases', 'Solo Compras'),
        ('pawns', 'Solo Empeños'),
    ], default='all')
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ], default='pdf')

    def action_generate(self):
        """Genera informe en el formato seleccionado"""
        if self.output_format == 'pdf':
            return self._generate_pdf()
        return self._generate_excel()

    def _generate_pdf(self):
        """Genera informe en PDF usando QWeb template"""
        return self.env.ref('jewelry_report.report_police').report_action(self)

    def _generate_excel(self):
        """Genera informe en Excel usando xlsxwriter"""
        # Implementación con xlsxwriter
        pass
```

### Estimación: 16-24 horas

---

## 3.5 Módulo `jewelry_product` (Complejidad: Baja)

### Objetivo
Trazabilidad de origen del producto y campos específicos de joyería.

### Campos a Añadir
```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    origin_type = fields.Selection([
        ('supplier', 'Compra a Proveedor'),
        ('client', 'Compra a Particular'),
        ('pawn', 'Empeño No Recuperado'),
    ], string='Origen')

    origin_document = fields.Reference([
        ('purchase.order', 'Compra Proveedor'),
        ('jewelry.client.purchase', 'Compra Particular'),
        ('jewelry.pawn', 'Empeño'),
    ], string='Documento Origen')

    origin_date = fields.Date('Fecha Origen')

    # Campos específicos de joyería
    jewelry_weight = fields.Float('Peso (g)')
    jewelry_quality_id = fields.Many2one('jewelry.material.quality', 'Calidad')
```

### Estimación: 8-16 horas

---

## 3.6 Módulo `jewelry_base` (Complejidad: Baja) ✅ IMPLEMENTADO

### Objetivo
Configuración base, grupos de seguridad, parámetros del sistema y **ajustes de interfaz**.

### Ajustes de Interfaz
- Renombrado del menú raíz `purchase` a "Compras Proveedor".

### Contenido
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jewelry_blocking_days = fields.Integer(
        string='Días de Bloqueo Legal',
        config_parameter='jewelry.blocking_days',
        default=14
    )
    jewelry_default_margin = fields.Float(
        string='Margen por Defecto (%)',
        config_parameter='jewelry.default_margin',
        default=20.0
    )
    jewelry_default_surcharge = fields.Float(
        string='Recargo Diario por Defecto (%)',
        config_parameter='jewelry.default_surcharge',
        default=0.5
    )
```

### Grupos de Seguridad
```xml
<record id="group_jewelry_user" model="res.groups">
    <field name="name">Joyería / Operador</field>
    <field name="category_id" ref="base.module_category_services"/>
</record>

<record id="group_jewelry_manager" model="res.groups">
    <field name="name">Joyería / Administrador</field>
    <field name="category_id" ref="base.module_category_services"/>
    <field name="implied_ids" eval="[(4, ref('group_jewelry_user'))]"/>
</record>
```

### Estimación: 4-8 horas

---

# RESUMEN FINAL

## Cobertura por Funcionalidad

| # | Funcionalidad | Cobertura | Esfuerzo |
|---|---------------|-----------|----------|
| 1 | Alta de cliente | ✅ OOTB + Mínimo desarrollo | 4-8h |
| 2 | Compras a particular | ✅ Implementado | - |
| 3 | Envío a fundición | ✅ Implementado | - |
| 4 | Empeños | ✅ Implementado (integrado en compras) | - |
| 5 | Informe policial | ❌ Desarrollo completo | 16-24h |
| 6 | Compras a proveedor | ✅ OOTB | 0h (config) |
| 7 | Ventas | ✅ OOTB + Mínimo desarrollo | 8-16h |
| 8 | Servicios (Taller) | ✅ OOTB | 0h (config) |
| 9 | Formas de pago | ✅ OOTB | 0h (config) |
| 10 | RBAC | ✅ OOTB | 0h (config) |

## Arquitectura de Módulos

```
custom-addons/
├── jewelry_base/                    # Configuración base y grupos
│   ├── __manifest__.py
│   ├── models/
│   │   └── res_config_settings.py
│   ├── security/
│   │   ├── security.xml             # Grupos
│   │   └── ir.model.access.csv
│   └── views/
│       ├── res_config_settings_views.xml
│       └── purchase_menu_views.xml  # Renombrado de menús
│
├── jewelry_partner/                 # Extensión de contactos
│   ├── __manifest__.py
│   ├── models/
│   │   └── res_partner.py
│   └── views/
│       └── res_partner_views.xml
│
├── jewelry_product/                 # Extensión de productos
│   ├── __manifest__.py
│   ├── models/
│   │   ├── product.py
│   │   └── material_quality.py
│   ├── security/
│   └── views/
│
├── jewelry_purchase_client/         # Compras a particulares + Empeños
│   ├── __manifest__.py
│   ├── models/
│   │   ├── client_purchase.py       # Incluye lógica de recuperables
│   │   ├── client_purchase_line.py
│   │   └── smelting_batch.py
│   ├── views/
│   │   └── client_purchase_views.xml
│   ├── wizard/
│   │   ├── send_to_inventory_wizard.py
│   │   ├── smelt_all_wizard.py
│   │   └── recovery_wizard.py       # NUEVO: wizard recuperación
│   ├── report/
│   │   └── contract_template.xml
│   ├── security/
│   └── data/
│       ├── sequence.xml
│       └── cron_data.xml            # Transiciones automáticas
│
└── jewelry_report/                  # Informes y reportes
    ├── __manifest__.py
    ├── wizard/
    │   └── police_report_wizard.py
    ├── report/
    │   ├── police_report_template.xml
    │   └── police_report.py
    └── security/
```

## Dependencias entre Módulos

```
jewelry_base
    ↓
jewelry_partner
    ↓
jewelry_product
    ↓
jewelry_purchase_client  ◄── Incluye compras normales + recuperables (empeños)
    ↓
jewelry_report
```

## Estado de Implementación

| Componente | Estado | Fecha | Notas |
|------------|--------|-------|-------|
| `jewelry_base` | ✅ Implementado | 2025-12-06 | |
| `jewelry_partner` | ✅ Implementado | 2025-12-06 | |
| `jewelry_product` | ✅ Implementado | 2025-12-07 | Calidades de material |
| `jewelry_purchase_client` | ✅ Implementado | 2025-12-09 | Incluye compras + empeños |
| ~~`jewelry_pawn`~~ | ➡️ Integrado | - | Integrado en `jewelry_purchase_client` |
| `jewelry_report` | ⏳ Pendiente | - | |

## Estimación Total

| Componente | Horas | Estado |
|------------|-------|--------|
| Configuración OOTB | 8-16h | ⏳ |
| `jewelry_base` | 4-8h | ✅ |
| `jewelry_partner` | 4-8h | ✅ |
| `jewelry_product` | 8-16h | ✅ |
| `jewelry_purchase_client` (base) | 24-40h | ✅ |
| `jewelry_purchase_client` (recuperables/empeños) | 38-56h | ✅ |
| ~~`jewelry_pawn`~~ | ~~40-60h~~ | ➡️ Integrado |
| `jewelry_report` | 16-24h | ⏳ |
| **Total restante** | **16-24h** | |

## Fases de Implementación

### Fase 1: Fundamentos ✅ COMPLETADA
- `jewelry_base`: Grupos, configuración
- `jewelry_partner`: Campos de identificación
- `jewelry_product`: Calidades de material
- Configuración multi-tienda

### Fase 2: Compras a Particular ✅ COMPLETADA
- ✅ `jewelry_purchase_client`: Modelo base
- ✅ Template de contrato PDF
- ✅ Período de bloqueo legal
- ✅ Envío a fundición/inventario
- ✅ **Flujo de compras recuperables (empeños)**

### ~~Fase 3: Empeños~~ → INTEGRADA EN FASE 2 ✅
- ~~`jewelry_pawn`: Modelo completo~~
- ✅ Tipo de operación (compra/recuperable)
- ✅ Nuevos estados (Recuperable, Recuperado, etc.)
- ✅ Cálculos de recuperación (margen, recargo)
- ✅ Flujos de recuperación
- ✅ Transiciones automáticas (cron)

### Fase 3: Reporting ⏳ PENDIENTE
- `jewelry_report`: Informes PDF/Excel
- Configuración de plantillas
- Dashboard operativo

---

## Consideraciones SaaS

### Multi-Tenancy
- Cada empresa/tenant tiene su propia configuración de:
  - Días de bloqueo legal
  - Márgenes por defecto
  - Templates de contrato
  - Secuencias de numeración

### Personalización por Cliente
- Templates de contrato configurables
- Logo y datos de empresa en documentos
- Campos adicionales opcionales

### Escalabilidad
- Diseño compatible con múltiples bases de datos
- Sin hardcoding de valores específicos de cliente
- Configuración vía `ir.config_parameter` y `res.company`
