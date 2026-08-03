# Quickstart: Validación de Herencia de Subtareas y Corrección de Flickering

Prerrequisito: stack Docker corriendo (`docker compose up`, servicios `sywork_backend`,
`sywork_frontend`, `sywork_db`) y sesión iniciada como un rol interno (Admin, Coordinador, QM o
Resolutor) con al menos una Tarea existente.

## Escenario 1 — Herencia automática (US1, FR-001..FR-003)

1. Abrir el detalle de una Tarea que tenga Nivel de escalamiento distinto de "N2", un Usuario
   solicitante asignado y al menos 1 Skill requerida.
2. En la Card "Subtareas" (sidebar derecho), clic en "Agregar subtarea" → completar título →
   "Crear".
3. Abrir el detalle de la Subtarea recién creada.
4. **Esperado**: "Nivel de escalamiento", "Usuario/cliente solicitante" y "Skills requeridas"
   muestran los mismos valores que la Tarea padre, sin haberlos vuelto a seleccionar.

## Escenario 2 — Independencia post-creación (Acceptance Scenario 2 de US1)

1. Desde el detalle de la Subtarea del Escenario 1, modificar manualmente las Skills requeridas
   (agregar o quitar una).
2. Recargar el detalle de la Tarea padre.
3. **Esperado**: las Skills de la Tarea padre no cambiaron.

## Escenario 3 — Vínculo bidireccional (US2)

1. Crear 2-3 Subtareas adicionales desde la misma Tarea padre del Escenario 1.
2. En el detalle de la Tarea padre, revisar la Card "Subtareas".
3. **Esperado**: aparecen todas las Subtareas creadas, cada una como fila clicable; clic en
   cualquiera navega a su detalle.

## Escenario 4 — Hipervínculo "Tarea Padre" (US3)

1. Desde el detalle de cualquier Subtarea, ubicar la sección "Clasificación".
2. **Esperado**: aparece el campo "Tarea Padre" con el código/título de la Tarea de origen como
   enlace.
3. Clic en el enlace.
4. **Esperado**: navega al detalle de la Tarea padre correspondiente.
5. Abrir el detalle de un Ticket normal (sin `parent_task_id`).
6. **Esperado**: el campo "Tarea Padre" no aparece.

## Escenario 5 — Ausencia de flickering (US4)

1. Abrir el detalle de cualquier Ticket/Tarea (con y sin Subtareas) con el navegador a un alto
   de ventana que obligue a hacer scroll (p. ej. 800px de alto).
2. Hacer scroll lento y luego rápido, hacia abajo y hacia arriba repetidamente, durante al menos
   30 segundos, dentro del panel izquierdo (Clasificación + Historial de estados).
3. **Esperado**: el contenido se desplaza de forma estable; no se observan saltos ni parpadeo
   de la tarjeta "Registros de tiempo" ni de las tarjetas debajo de ella.
4. Repetir sobre el detalle de la Subtarea del Escenario 4 (con el campo "Tarea Padre" visible).
5. **Esperado**: mismo resultado, sin parpadeo.

## Validación técnica acotada (Principio VII)

- Backend: `pytest backend/tests/api/test_tickets_subtasks.py backend/tests/api/test_tickets.py -k subtask` (o el archivo específico que agregue los casos de herencia), dataset ≤ 10 registros por test, sin correr la suite completa.
- Frontend: `tsc -b` sin errores; no se ejecuta suite E2E automatizada — el Escenario 5 se valida manualmente en navegador (Docker real) por tratarse de un defecto de interacción visual.
