# Sistema de Compraventa - Documentación Técnica

## Visión General

El módulo `jewelry_purchase_client` gestiona las compras de oro y joyas a particulares (personas físicas que venden al negocio). Incluye dos tipos de operaciones:

| Tipo | Descripción | Recuperable |
|------|-------------|-------------|
| **Compra** | El cliente vende definitivamente | No |
| **Compra Recuperable** | El cliente puede recuperar el artículo pagando precio + margen + recargo | Sí |

> **Decisión de arquitectura**: Ambos tipos se gestionan en el mismo módulo porque el negocio los ve como variantes del mismo proceso operativo.

## Documentos en esta Carpeta

| Documento | Contenido |
|-----------|-----------|
| [FLUJO_ESTADOS.md](./FLUJO_ESTADOS.md) | Diagrama de estados y transiciones |
| [MODELO_DATOS.md](./MODELO_DATOS.md) | Campos nuevos y modificaciones al modelo |
| [IMPLEMENTACION.md](./IMPLEMENTACION.md) | Tareas de desarrollo y orden de ejecución |

## Flujo Resumido

### Compra Normal (no recuperable)
```
Borrador → Bloqueo Policial → Disponible → A Fundir → Fundido
                                        → Inventario → Venta
```

### Compra Recuperable (Empeño)
```
Borrador → Bloqueo Policial → [Recuperable] → Disponible → ...
              ↓                    ↓              ↓
          Recuperado          Recuperado     Recuperado
        (durante bloqueo)    (a tiempo)     (con recargo)
```

## Precios de Recuperación

| Momento | Fórmula |
|---------|---------|
| Durante bloqueo o a tiempo | `precio + (precio × margen%)` |
| Después del plazo (tarde) | `precio + (precio × margen%) + (precio × recargo_diario% × días_vencido)` |

## Estado Actual de Implementación

### Implementado
- Modelo base `jewelry.client.purchase`
- Líneas con fotos, peso, calidad
- Período de bloqueo policial
- Integración con POS (salida de caja)
- Envío a fundición e inventario
- Lotes de fundición

### Pendiente
- Campo tipo de operación (compra/recuperable)
- Estado "Recuperable"
- Estados finales (Fundido, Recuperado, Venta)
- Campos de empeño (margen, fecha límite, recargo)
- Cálculos automáticos de recuperación
- Acción de recuperación (entrada de caja)
- Transiciones automáticas por cron

## Referencias

- Documento principal: [../ANALISIS_COBERTURA_ODOO.md](../ANALISIS_COBERTURA_ODOO.md)
- Módulo: `/custom-addons/jewelry_purchase_client/`
