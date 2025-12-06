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

## 3.2 Módulo `jewelry_purchase_client` (Complejidad: Alta)

### Objetivo
Sistema de compras a particulares (clientes que venden oro/joyas al negocio).
En la interfaz, este módulo se presentará como **"Compras Particular"**.

### ¿Por qué no usar `purchase` estándar?
El módulo `purchase` de Odoo está diseñado para:
- Compras a **proveedores** (empresas)
- Flujo de RFQ → PO → Recepción
- Terminología de "proveedor"

Para compras a particulares se necesita:
- El vendedor es un **cliente** (persona física)
- Flujo simplificado sin RFQ
- Período de bloqueo policial (requisito legal)
- Contrato específico
- Terminología de "compra a particular"

### Modelo Principal
```python
class ClientPurchaseOrder(models.Model):
    _name = 'jewelry.client.purchase'
    _description = 'Compra a Particular'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Referencia', readonly=True, default='Nuevo')
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    date = fields.Date('Fecha', default=fields.Date.today)
    company_id = fields.Many2one('res.company')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    line_ids = fields.One2many('jewelry.client.purchase.line', 'order_id')

    amount_total = fields.Monetary(compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('blocked', 'Período de Bloqueo'),
        ('available', 'Disponible'),
        ('processed', 'Procesado'),
    ], default='draft')

    # Período de bloqueo (configurable por tenant)
    blocking_end_date = fields.Date(compute='_compute_blocking_end')
    can_process = fields.Boolean(compute='_compute_can_process')

    # Contrato
    contract_pdf = fields.Binary('Contrato Generado')
    contract_signed = fields.Binary('Contrato Firmado')


class ClientPurchaseOrderLine(models.Model):
    _name = 'jewelry.client.purchase.line'
    _description = 'Línea de Compra a Particular'

    order_id = fields.Many2one('jewelry.client.purchase', ondelete='cascade')
    description = fields.Text('Descripción', required=True)
    weight = fields.Float('Peso (g)')
    quality_id = fields.Many2one('jewelry.material.quality', 'Calidad')
    price = fields.Monetary('Importe')
    currency_id = fields.Many2one(related='order_id.currency_id')
    image_ids = fields.Many2many('ir.attachment', string='Fotos')
```

### Modelo de Calidades de Material
```python
class MaterialQuality(models.Model):
    _name = 'jewelry.material.quality'
    _description = 'Calidad de Material'

    name = fields.Char('Nombre', required=True)  # 24k, 18k, Plata, etc.
    material_type = fields.Selection([
        ('gold', 'Oro'),
        ('silver', 'Plata'),
        ('platinum', 'Platino'),
        ('other', 'Otro'),
    ])
    purity_percent = fields.Float('Pureza (%)')
    active = fields.Boolean(default=True)
```

### Funcionalidades
1. Alta de compra vinculada a cliente
2. Líneas con descripción, peso, calidad, precio
3. Fotos por línea
4. Generación de contrato PDF (template configurable)
5. Control de período de bloqueo (configurable por empresa)
6. Estados: Borrador → Confirmado → Bloqueado → Disponible → Procesado
7. Envío a fundición tras período de bloqueo

### Estimación: 24-40 horas

---

## 3.3 Módulo `jewelry_pawn` (Complejidad: Alta)

### Objetivo
Sistema completo de empeños (compras recuperables).

### ¿Por qué desarrollo completo?
Odoo **no tiene ningún concepto de empeños**. No existe:
- Compra con opción de recuperación
- Cálculo de intereses/recargos diarios
- Custodia temporal de artículos
- Vencimiento con paso a stock vendible

### Modelo Principal
```python
class PawnOrder(models.Model):
    _name = 'jewelry.pawn'
    _description = 'Empeño'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Referencia', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    company_id = fields.Many2one('res.company')

    # Condiciones del empeño
    purchase_amount = fields.Monetary('Importe Entregado')
    duration_days = fields.Integer('Días de Empeño')
    margin_percent = fields.Float('Margen (%)')
    daily_surcharge_percent = fields.Float('Recargo Diario (%)', digits=(5,2))

    # Fechas
    date_start = fields.Date('Fecha Inicio')
    date_due = fields.Date('Fecha Vencimiento', compute='_compute_dates', store=True)

    # Cálculos automáticos
    recovery_amount = fields.Monetary(
        'Importe Recuperación',
        compute='_compute_amounts'
    )
    days_overdue = fields.Integer('Días Vencido', compute='_compute_amounts')
    current_surcharge = fields.Monetary('Recargo Actual', compute='_compute_amounts')
    total_to_pay = fields.Monetary('Total a Pagar Hoy', compute='_compute_amounts')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('overdue', 'Vencido'),
        ('recovered', 'Recuperado'),
        ('forfeited', 'No Recuperado'),
    ], default='draft')

    line_ids = fields.One2many('jewelry.pawn.line', 'order_id')

    @api.depends('date_start', 'duration_days')
    def _compute_dates(self):
        for record in self:
            if record.date_start and record.duration_days:
                record.date_due = record.date_start + timedelta(days=record.duration_days)
            else:
                record.date_due = False

    @api.depends('purchase_amount', 'margin_percent', 'daily_surcharge_percent', 'date_due')
    def _compute_amounts(self):
        for record in self:
            # Precio base de recuperación
            record.recovery_amount = record.purchase_amount * (1 + record.margin_percent / 100)

            # Calcular días vencido y recargo
            today = fields.Date.today()
            if record.date_due and today > record.date_due:
                record.days_overdue = (today - record.date_due).days
                record.current_surcharge = (
                    record.purchase_amount *
                    (record.daily_surcharge_percent / 100) *
                    record.days_overdue
                )
            else:
                record.days_overdue = 0
                record.current_surcharge = 0

            record.total_to_pay = record.recovery_amount + record.current_surcharge

    def action_recover(self):
        """Cliente recupera su empeño pagando el total"""
        self.ensure_one()
        # Lógica de recuperación
        self.write({'state': 'recovered'})

    def action_forfeit(self):
        """Empeño no recuperado - pasa a stock vendible"""
        self.ensure_one()
        # Crear producto en inventario
        self.write({'state': 'forfeited'})
```

### Funcionalidades
1. Creación de empeño con todos los datos de compra
2. Condiciones configurables: duración, margen, recargo diario
3. Cálculo automático de precio de recuperación
4. Cálculo dinámico de recargos por días vencidos
5. Flujo de recuperación (cliente paga y recupera artículo)
6. Flujo de decomiso (pasa a stock vendible)
7. Modificación de margen/recargo en cualquier momento
8. Alertas de vencimiento

### Estimación: 40-60 horas

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
| 2 | Compras a particular | ❌ Desarrollo completo | 24-40h |
| 3 | Envío a fundición | ⚠️ Parte del módulo compras | Incluido |
| 4 | Empeños | ❌ Desarrollo completo | 40-60h |
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
├── jewelry_purchase_client/         # Compras a particulares
│   ├── __manifest__.py
│   ├── models/
│   │   ├── client_purchase.py
│   │   └── client_purchase_line.py
│   ├── views/
│   ├── report/
│   │   └── contract_template.xml    # Template de contrato PDF
│   ├── security/
│   └── data/
│       └── sequence.xml
│
├── jewelry_pawn/                    # Sistema de empeños
│   ├── __manifest__.py
│   ├── models/
│   │   ├── pawn_order.py
│   │   └── pawn_order_line.py
│   ├── views/
│   ├── wizard/
│   ├── security/
│   └── data/
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
jewelry_partner ←──────────────────┐
    ↓                              │
jewelry_product                    │
    ↓                              │
jewelry_purchase_client ───────────┤
    ↓                              │
jewelry_pawn ──────────────────────┘
    ↓
jewelry_report
```

## Estado de Implementación

| Componente | Estado | Fecha |
|------------|--------|-------|
| `jewelry_base` | ✅ Implementado | 2025-12-06 |
| `jewelry_partner` | ✅ Implementado | 2025-12-06 |
| `jewelry_product` | ⏳ Pendiente | - |
| `jewelry_purchase_client` | ⏳ Pendiente | - |
| `jewelry_pawn` | ⏳ Pendiente | - |
| `jewelry_report` | ⏳ Pendiente | - |

## Estimación Total

| Componente | Horas | Estado |
|------------|-------|--------|
| Configuración OOTB | 8-16h | ⏳ |
| `jewelry_base` | 4-8h | ✅ |
| `jewelry_partner` | 4-8h | ✅ |
| `jewelry_product` | 8-16h | ⏳ |
| `jewelry_purchase_client` | 24-40h | ⏳ |
| `jewelry_pawn` | 40-60h | ⏳ |
| `jewelry_report` | 16-24h | ⏳ |
| **Total** | **104-172h** | |

## Fases de Implementación

### Fase 1: Fundamentos
- `jewelry_base`: Grupos, configuración
- `jewelry_partner`: Campos de identificación
- `jewelry_product`: Calidades de material
- Configuración multi-tienda

### Fase 2: Compras a Particular
- `jewelry_purchase_client`: Modelo completo
- Template de contrato PDF
- Período de bloqueo legal
- Envío a fundición

### Fase 3: Empeños
- `jewelry_pawn`: Modelo completo
- Cálculos de recuperación
- Flujos de recuperación/decomiso
- Alertas de vencimiento

### Fase 4: Reporting
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
