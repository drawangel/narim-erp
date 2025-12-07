# Odoo Implementation Command

Ejecuta un ciclo de implementacion guiado para modulos Odoo basado en un documento de plan.

## Argumentos

- `$ARGUMENTS`: Ruta al documento de plan de implementacion (ej: `docs/PLAN_JEWELRY_PAWN.md`)

## Instrucciones

### Paso 1: Cargar Skill de Odoo

Primero, carga la skill de desarrollo Odoo 18:

```
skill: odoo-18-dev
```

### Paso 2: Analizar el Plan de Implementacion

Lee y analiza el documento de plan en `$ARGUMENTS`:

1. **Identifica el objetivo del modulo** - Que funcionalidad se esta construyendo?
2. **Revisa el estado actual** - Que pasos ya estan completados (marcados con ✅)?
3. **Identifica el siguiente paso** - El primer item pendiente (⏳ o sin marcar)
4. **Comprende las dependencias** - Hay prerrequisitos que verificar?

### Paso 3: Verificar Contexto del Codigo

Antes de implementar:

1. Revisa los modulos existentes relacionados en `/custom-addons/`
2. Identifica patrones ya establecidos en el proyecto
3. Verifica dependencias en `__manifest__.py` de modulos relacionados
4. Confirma que el modulo base requerido existe y funciona

### Paso 4: Implementar el Siguiente Paso

Ejecuta la implementacion siguiendo las **Reglas de Oro** del proyecto:

- Todo codigo en `/custom-addons/` (NUNCA en `/odoo/`)
- Usar `_inherit` para extender modelos existentes
- Incluir `ir.model.access.csv` para todo modelo nuevo
- Formato de version: `18.0.MAJOR.MINOR.PATCH`
- Llamar a `super()` en override de create/write/unlink

### Paso 5: Actualizar la Documentacion

**CRITICO**: Despues de cada implementacion, actualiza el documento de plan:

1. **Marca el paso completado** - Cambia ⏳ a ✅ con fecha
2. **Documenta decisiones de diseno** - Si hubo cambios respecto al plan original
3. **Actualiza estimaciones** - Si el siguiente paso requiere ajustes
4. **Agrega notas tecnicas** - Detalles relevantes para referencia futura
5. **Lista problemas encontrados** - Si hubo obstaculos y como se resolvieron

### Formato de Actualizacion del Plan

```markdown
## Estado de Implementacion

| Paso | Descripcion | Estado | Fecha | Notas |
|------|-------------|--------|-------|-------|
| 1 | Crear modelo base | ✅ | 2025-12-07 | Incluye campos X, Y, Z |
| 2 | Agregar vistas | ⏳ | - | Siguiente paso |
| 3 | Configurar seguridad | ⏳ | - | - |
```

### Paso 6: Actualizar Modulos en Odoo

**OBLIGATORIO**: Despues de cada implementacion, ejecuta el comando de actualizacion de los modulos afectados:

1. **Identifica los modulos modificados** - Revisa que directorios en `/custom-addons/` fueron tocados durante la implementacion
2. **Ejecuta la actualizacion automaticamente**:
   ```bash
   docker compose exec odoo python -m odoo -d narim_db -u <modulos_afectados> --stop-after-init
   ```

   Donde `<modulos_afectados>` es una lista separada por comas de los modulos modificados.

   **Ejemplos**:
   ```bash
   # Un solo modulo
   docker compose exec odoo python -m odoo -d narim_db -u jewelry_pawn --stop-after-init

   # Multiples modulos
   docker compose exec odoo python -m odoo -d narim_db -u jewelry_pawn,jewelry_product --stop-after-init
   ```

3. **Verifica el resultado**:
   - Si el comando termina sin errores → Implementacion exitosa
   - Si hay errores → Corrigelos antes de continuar al siguiente paso

### Paso 7: Reportar Progreso

Resume lo implementado:
- Archivos creados/modificados
- Funcionalidades agregadas
- Resultado de la actualizacion de modulos (exito o errores corregidos)
- Proximo paso recomendado

### Ciclo Continuo

Si el usuario lo solicita, repite el ciclo:
1. Analizar → 2. Verificar → 3. Implementar → 4. Documentar → 5. Actualizar Odoo → 6. Reportar

---

## Ejemplo de Uso

```
/odoo-implement docs/PLAN_JEWELRY_PAWN.md
```

Esto:
1. Cargara la skill de Odoo 18
2. Leera el plan en `docs/PLAN_JEWELRY_PAWN.md`
3. Identificara el siguiente paso pendiente
4. Implementara siguiendo las convenciones del proyecto
5. Actualizara el documento con el progreso
6. **Ejecutara automaticamente** `docker compose exec odoo python -m odoo -d narim_db -u <modulo> --stop-after-init`
7. Reportara el resultado
