# Quickstart: Validación de Subtareas visibles en "Clasificación"

Prerrequisito: stack Docker corriendo, sesión iniciada como rol interno con al menos una Tarea
existente sin Subtareas.

## Escenario 1 — Sin subtareas (Acceptance Scenario 1)

1. Abrir el detalle de una Tarea que no tiene ninguna Subtarea.
2. **Esperado**: la sección "Clasificación" muestra el campo "Subtareas" con el texto "Sin
   subtareas" (no lo omite en silencio).

## Escenario 2 — Aparece tras crear una Subtarea (Acceptance Scenario 2/Scenario 4 del quickstart de spec 036)

1. Desde esa misma Tarea, usar la tarjeta lateral "Subtareas" → "Agregar subtarea" → completar
   título → "Crear".
2. **Esperado**: sin recargar manualmente la página, la sección "Clasificación" pasa a mostrar
   "Subtareas" con 1 ítem, el título/código de la Subtarea recién creada.
3. Clic sobre esa Subtarea listada en "Clasificación".
4. **Esperado**: navega al detalle de esa Subtarea.

## Escenario 3 — Varias Subtareas (Acceptance Scenario 3)

1. Crear 2 Subtareas adicionales desde la misma Tarea (total 3).
2. Volver a su detalle.
3. **Esperado**: "Clasificación" lista las 3 Subtareas, todas navegables.

## Escenario 4 — Ausencia en Ticket/Subtarea (Acceptance Scenario 5)

1. Abrir el detalle de un Ticket normal (no Tarea) y de una Subtarea.
2. **Esperado**: el campo "Subtareas" no aparece en "Clasificación" en ninguno de los dos casos.

## Validación técnica acotada (Principio VII)

- Frontend: `tsc -b` sin errores. Sin cambios de backend — no aplica pytest nuevo.
- Validación manual en navegador (Docker real) para los 4 escenarios; no requiere script E2E
  desechable (no hay lógica de servidor nueva que verificar).
