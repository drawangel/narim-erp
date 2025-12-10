# Informes Policiales (Mossos d'Esquadra)

## Resumen

Este documento describe la implementación del módulo `jewelry_report` para generar los informes requeridos por los Mossos d'Esquadra para las operaciones de compraventa de oro y empeños.

**Requisito crítico**: La cabecera del Excel NO es editable. Debe generarse EXACTAMENTE como se especifica, ya que la policía utiliza parsers o automatizaciones para procesar el archivo.

---

## Formatos de Salida

### 1. Excel (.xlsx)

Un registro por cada **línea de producto** (no por compra).

#### Cabecera (EXACTA, no modificar)

```
Nº CONTRACTE | NOM I COGNOMS | DNI | DATA COMPRA | ESTABLIMENT | TIPUS | DESCRIPCIÓ | S/N - INSCRIPCIONS
```

#### Mapeo de Campos

| Columna Excel | Campo Odoo | Modelo | Notas |
|---------------|------------|--------|-------|
| Nº CONTRACTE | `name` | `jewelry.client.purchase` | Referencia del contrato (ej: CP/00001) |
| NOM I COGNOMS | `partner_id.name` | `res.partner` | Nombre completo |
| DNI | `partner_id.vat` | `res.partner` | Documento de identidad |
| DATA COMPRA | `date` | `jewelry.client.purchase` | Formato: DD/MM/YYYY |
| ESTABLIMENT | `warehouse_id.name` | `stock.warehouse` | Nombre de la tienda |
| TIPUS | `jewelry_type_id.name` | `jewelry.type` | Tipo de joya (Anillo, Collar, etc.) |
| DESCRIPCIÓ | `description` | `jewelry.client.purchase.line` | Descripción del artículo |
| S/N - INSCRIPCIONS | `inscriptions` | `jewelry.client.purchase.line` | Grabados, iniciales, textos |

#### Ejemplo de Datos

| Nº CONTRACTE | NOM I COGNOMS | DNI | DATA COMPRA | ESTABLIMENT | TIPUS | DESCRIPCIÓ | S/N - INSCRIPCIONS |
|--------------|---------------|-----|-------------|-------------|-------|------------|-------------------|
| CP/00001 | MARIA GARCIA LOPEZ | 12345678A | 01/09/2025 | BENDA JOYAS CORCEGA | ANELL | ORO REDONDOS | SN INSCRIPCIONS |
| CP/00001 | MARIA GARCIA LOPEZ | 12345678A | 01/09/2025 | BENDA JOYAS CORCEGA | COLLARET | ORO CADENA FINA | A.M.G. |
| CP/00002 | JOAN MARTINEZ PUJOL | 87654321B | 02/09/2025 | BENDA JOYAS CORCEGA | BRAÇALET | ORO ANCHO | SN INSCRIPCIONS |

---

### 2. PDF

Un registro por cada **línea de producto** con fotografías.

#### Estructura por Artículo

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Número: 10541    Contrato de CompraVenta    Ref: 20250922-112502-11311  │
│                                                      Fecha: 22/09/2025  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ANILLO CON OPALO Y BTES - Peso: 7,74 gramos 18k           340,00 Euros │
│                                                                         │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│ │              │  │              │  │              │  MONTSERRAT SALES │
│ │  [Foto del   │  │  [Foto DNI   │  │  [Foto DNI   │  C/ Sant Antoni   │
│ │  artículo]   │  │   frontal]   │  │   reverso]   │  08025 Barcelona  │
│ │              │  │              │  │              │  BARCELONA        │
│ └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                      Num ID: 36469533E │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Mapeo de Campos PDF

| Campo PDF | Campo Odoo | Modelo |
|-----------|------------|--------|
| Número | `name` (extraer número) | `jewelry.client.purchase` |
| Ref | Generar: `YYYYMMDD-HHMMSS-ID` | Calculado |
| Fecha | `date` | `jewelry.client.purchase` |
| Descripción | `description` | `jewelry.client.purchase.line` |
| Peso | `weight` | `jewelry.client.purchase.line` |
| Calidad | `quality_id.name` | `jewelry.material.quality` |
| Precio | `price` | `jewelry.client.purchase.line` |
| Foto artículo | `image_ids` | `ir.attachment` (via línea) |
| Foto DNI frontal | `id_document_front` | `res.partner` |
| Foto DNI reverso | `id_document_back` | `res.partner` |
| Nombre | `partner_id.name` | `res.partner` |
| Dirección | `street`, `street2` | `res.partner` |
| CP | `zip` | `res.partner` |
| Ciudad | `city` | `res.partner` |
| Provincia | `state_id.name` | `res.country.state` |
| Num ID | `vat` | `res.partner` |

---

## Wizard de Generación

### Problema Actual

La vista de lista de "Compras" tiene limitaciones:
1. No permite filtros OR (ej: "Bloqueo Policial" OR "Procesado")
2. No tiene date pickers para rango de fechas personalizado

### Solución: Wizard Dedicado

```python
class PoliceReportWizard(models.TransientModel):
    _name = 'jewelry.report.police.wizard'
    _description = 'Generador de Informe Policial'

    # Rango de fechas
    date_from = fields.Date('Desde', required=True,
        default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date('Hasta', required=True,
        default=fields.Date.today)

    # Filtro de estados (selección múltiple)
    include_blocked = fields.Boolean('Bloqueo Policial', default=True)
    include_recoverable = fields.Boolean('Recuperable', default=True)
    include_available = fields.Boolean('Disponible', default=True)
    include_processed = fields.Boolean('Procesado', default=True)
    include_recovered = fields.Boolean('Recuperado', default=False)

    # Filtro de tiendas
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Tiendas',
        help='Dejar vacío para incluir todas las tiendas'
    )

    # Tipo de operación
    operation_type = fields.Selection([
        ('all', 'Todos'),
        ('purchase', 'Solo Compras'),
        ('recoverable', 'Solo Empeños'),
    ], string='Tipo de Operación', default='all')

    # Formato de salida
    output_format = fields.Selection([
        ('excel', 'Excel (.xlsx)'),
        ('pdf', 'PDF'),
    ], string='Formato', default='excel', required=True)
```

### Vista del Wizard

```xml
<form string="Generar Informe Policial">
    <group>
        <group string="Período">
            <field name="date_from"/>
            <field name="date_to"/>
        </group>
        <group string="Formato">
            <field name="output_format" widget="radio"/>
            <field name="operation_type"/>
        </group>
    </group>
    <group string="Estados a Incluir">
        <div class="d-flex flex-wrap gap-3">
            <field name="include_blocked"/>
            <field name="include_recoverable"/>
            <field name="include_available"/>
            <field name="include_processed"/>
            <field name="include_recovered"/>
        </div>
    </group>
    <group string="Tiendas">
        <field name="warehouse_ids" widget="many2many_tags"
               options="{'no_create': True}"
               placeholder="Todas las tiendas"/>
    </group>
    <footer>
        <button string="Generar Informe" type="object"
                name="action_generate" class="btn-primary"/>
        <button string="Cancelar" class="btn-secondary" special="cancel"/>
    </footer>
</form>
```

---

## Arquitectura del Módulo

```
custom-addons/jewelry_report/
├── __manifest__.py
├── __init__.py
├── wizard/
│   ├── __init__.py
│   └── police_report_wizard.py
├── report/
│   ├── __init__.py
│   ├── police_report_excel.py      # Generador con xlsxwriter
│   └── police_report_pdf.xml       # Template QWeb
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── police_report_wizard_views.xml
│   └── menu_views.xml
└── static/
    └── description/
        └── icon.png
```

---

## Implementación Excel

### Dependencias

```python
# En __manifest__.py
'external_dependencies': {
    'python': ['xlsxwriter'],
},
```

### Generador

```python
import xlsxwriter
from io import BytesIO
import base64

class PoliceReportExcel:

    HEADERS = [
        'Nº CONTRACTE',
        'NOM I COGNOMS',
        'DNI',
        'DATA COMPRA',
        'ESTABLIMENT',
        'TIPUS',
        'DESCRIPCIÓ',
        'S/N - INSCRIPCIONS',
    ]

    def generate(self, lines_data):
        """Genera el archivo Excel con la cabecera exacta."""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Informe Policial')

        # Escribir cabecera (fila 0)
        for col, header in enumerate(self.HEADERS):
            worksheet.write(0, col, header)

        # Escribir datos (desde fila 1)
        for row, line in enumerate(lines_data, start=1):
            worksheet.write(row, 0, line['contract_number'])
            worksheet.write(row, 1, line['client_name'])
            worksheet.write(row, 2, line['dni'])
            worksheet.write(row, 3, line['purchase_date'])  # DD/MM/YYYY
            worksheet.write(row, 4, line['store'])
            worksheet.write(row, 5, line['jewelry_type'])
            worksheet.write(row, 6, line['description'])
            worksheet.write(row, 7, line['inscriptions'] or 'SN INSCRIPCIONS')

        workbook.close()
        output.seek(0)
        return base64.b64encode(output.read())
```

---

## Implementación PDF (QWeb)

```xml
<template id="report_police_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="purchase">
            <t t-foreach="purchase.line_ids" t-as="line">
                <div class="page">
                    <!-- Cabecera -->
                    <div class="row border-bottom pb-2 mb-3">
                        <div class="col-3">
                            <strong>Número:</strong>
                            <t t-esc="purchase.name"/>
                        </div>
                        <div class="col-6 text-center">
                            <strong>Contrato de CompraVenta</strong>
                        </div>
                        <div class="col-3 text-end">
                            <strong>Fecha:</strong>
                            <t t-esc="purchase.date" t-options="{'widget': 'date'}"/>
                        </div>
                    </div>

                    <!-- Descripción del artículo -->
                    <div class="row mb-3">
                        <div class="col-9">
                            <h4>
                                <t t-esc="line.description"/>
                                <t t-if="line.weight">
                                    - Peso: <t t-esc="line.weight"/> gramos
                                </t>
                                <t t-if="line.quality_id">
                                    <t t-esc="line.quality_id.name"/>
                                </t>
                            </h4>
                        </div>
                        <div class="col-3 text-end">
                            <h4><t t-esc="line.price"/> Euros</h4>
                        </div>
                    </div>

                    <!-- Fotos y datos cliente -->
                    <div class="row">
                        <!-- Foto artículo -->
                        <div class="col-3">
                            <t t-foreach="line.image_ids[:1]" t-as="img">
                                <img t-att-src="image_data_uri(img.datas)"
                                     style="max-width:100%;max-height:150px;"/>
                            </t>
                        </div>
                        <!-- Foto DNI frontal -->
                        <div class="col-3">
                            <t t-if="purchase.partner_id.id_document_front">
                                <img t-att-src="image_data_uri(purchase.partner_id.id_document_front)"
                                     style="max-width:100%;max-height:150px;"/>
                            </t>
                        </div>
                        <!-- Foto DNI reverso -->
                        <div class="col-3">
                            <t t-if="purchase.partner_id.id_document_back">
                                <img t-att-src="image_data_uri(purchase.partner_id.id_document_back)"
                                     style="max-width:100%;max-height:150px;"/>
                            </t>
                        </div>
                        <!-- Datos cliente -->
                        <div class="col-3">
                            <strong><t t-esc="purchase.partner_id.name"/></strong><br/>
                            <t t-esc="purchase.partner_id.street"/><br/>
                            <t t-if="purchase.partner_id.street2">
                                <t t-esc="purchase.partner_id.street2"/><br/>
                            </t>
                            <t t-esc="purchase.partner_id.zip"/>
                            <t t-esc="purchase.partner_id.city"/><br/>
                            <t t-esc="purchase.partner_id.state_id.name or ''"/>
                            <br/><br/>
                            <strong>Num ID:</strong> <t t-esc="purchase.partner_id.vat"/>
                        </div>
                    </div>
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Verificación de Campos Disponibles

| Campo Requerido | Modelo | Campo | Estado |
|-----------------|--------|-------|--------|
| Nº Contrato | `jewelry.client.purchase` | `name` | ✅ Existe |
| Nombre cliente | `res.partner` | `name` | ✅ Existe |
| DNI | `res.partner` | `vat` | ✅ Existe |
| Fecha compra | `jewelry.client.purchase` | `date` | ✅ Existe |
| Tienda | `stock.warehouse` | `name` | ✅ Existe |
| Tipo joya | `jewelry.type` | `name` | ✅ Existe |
| Descripción | `jewelry.client.purchase.line` | `description` | ✅ Existe |
| Inscripciones | `jewelry.client.purchase.line` | `inscriptions` | ✅ Existe |
| Peso | `jewelry.client.purchase.line` | `weight` | ✅ Existe |
| Calidad | `jewelry.material.quality` | `name` | ✅ Existe |
| Fotos artículo | `jewelry.client.purchase.line` | `image_ids` | ✅ Existe |
| Foto DNI frontal | `res.partner` | `id_document_front` | ✅ Existe (jewelry_partner) |
| Foto DNI reverso | `res.partner` | `id_document_back` | ✅ Existe (jewelry_partner) |
| Dirección | `res.partner` | `street`, `zip`, `city`, `state_id` | ✅ Existe (base) |

---

## Menú y Acceso

### Ubicación en Menú

```
Compras Particular
├── Compras
├── Lotes de Fundición
└── Informes
    └── Informe Policial    <-- NUEVO
```

### Permisos

| Grupo | Acceso |
|-------|--------|
| `jewelry_base.group_jewelry_user` | Puede generar informes |
| `jewelry_base.group_jewelry_manager` | Puede generar informes |

---

## Estimación de Esfuerzo

| Tarea | Horas |
|-------|-------|
| Estructura del módulo y manifest | 1-2h |
| Wizard y vista | 2-3h |
| Generador Excel (xlsxwriter) | 4-6h |
| Template PDF (QWeb) | 4-6h |
| Menús y seguridad | 1-2h |
| Testing y ajustes | 4-6h |
| **Total** | **16-24h** |

---

## Estado de Implementación

| Paso | Descripción | Estado | Fecha | Notas |
|------|-------------|--------|-------|-------|
| 1 | Crear estructura del módulo y manifest | ✅ | 2025-12-09 | Versión 18.0.1.0.0, dependencias: jewelry_purchase_client, jewelry_partner |
| 2 | Crear wizard police_report_wizard.py | ✅ | 2025-12-09 | Modelo transient con filtros de fecha, estado, tienda y tipo operación |
| 3 | Crear generador Excel | ✅ | 2025-12-09 | Cabecera exacta en catalán, formato con xlsxwriter |
| 4 | Crear template PDF (QWeb) | ✅ | 2025-12-09 | Una página por línea con fotos de artículo y DNI |
| 5 | Crear vistas del wizard | ✅ | 2025-12-09 | Formulario con preview de registros encontrados |
| 6 | Crear menú bajo "Compras Particular > Informes" | ✅ | 2025-12-09 | Menú jerárquico con submenú "Informes" |
| 7 | Configurar seguridad | ✅ | 2025-12-09 | Acceso para group_jewelry_user y group_jewelry_manager |
| 8 | Instalar módulo en Odoo | ✅ | 2025-12-09 | Módulo instalado correctamente |

---

## Archivos Creados

```
custom-addons/jewelry_report/
├── __manifest__.py                          # Manifest con dependencias y external_dependencies
├── __init__.py                              # Imports de wizard y report
├── wizard/
│   ├── __init__.py
│   ├── police_report_wizard.py              # Wizard con filtros y generación
│   └── police_report_wizard_views.xml       # Vista del wizard y acción
├── report/
│   ├── __init__.py
│   ├── police_report_excel.py               # Generador Excel con xlsxwriter
│   └── police_report_pdf.xml                # Template QWeb para PDF
├── security/
│   └── ir.model.access.csv                  # ACLs para el wizard
└── views/
    └── menu_views.xml                       # Menú "Informes > Informe Policial"
```

---

## Próximos Pasos (Testing)

- [ ] Probar generación de Excel con datos reales
- [ ] Probar generación de PDF con fotos
- [ ] Verificar que la cabecera del Excel es exactamente la requerida
- [ ] Ajustar estilos del PDF si es necesario

---

## Referencias

- Imagen Excel: `/Users/adam/Documents/Narim Labs/Tech/NarimERP/Documentacion/Excel Mossos.png`
- Imagen PDF: `/Users/adam/Documents/Narim Labs/Tech/NarimERP/Documentacion/PDF Mossos.png`
- Documentación general: `/Users/adam/Apps/NarimERP/docs/ANALISIS_COBERTURA_ODOO.md`
