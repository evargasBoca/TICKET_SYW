# Quickstart: Validación de Cascada, Hipervínculos, Catálogos y Layout de Cliente

Prerrequisito: stack Docker corriendo (`docker ps` para confirmar `sywork_frontend`,
`sywork_backend`, `sywork_db`) y sesión iniciada como Coordinador o Admin.

## US1 — Cascada Cliente→Proyecto→Encargado + Skills

1. Ir a Tickets → "Nuevo ticket" (perfil interno).
2. Elegir un Cliente con ≥2 proyectos → confirmar que "Proyecto" solo lista los suyos.
3. Elegir un Proyecto → confirmar que "Usuario/cliente" solo lista los encargados de ese proyecto.
4. Cambiar el Cliente → confirmar que Proyecto y Encargado se limpian.
5. Confirmar que el campo "Skills requeridas" aparece (editable si Coordinador, deshabilitado si
   Admin/QM) y permite seleccionar del catálogo.
6. Repetir 1-5 con "Tipo de registro" = Tarea.

## US2 — Hipervínculos

1. En la lista de Tickets, hacer clic sobre un código `#TK-###` → debe navegar al detalle.
2. Repetir en "Mis Tareas", el tablero Kanban (código dentro de la tarjeta, sin iniciar drag) y el
   Panel de Asignación (ya funcionaba).
3. Volver atrás con el navegador → la lista de origen conserva filtros/orden.

## US3 — Ordenamiento explícito

1. En la lista de Tickets, usar el nuevo selector de orden: probar Fecha, Prioridad, Código, Estado
   en ambos sentidos.
2. Confirmar en la pestaña Network que la request a `GET /api/tickets` incluye `sort=<valor>` y que
   los filtros activos (`status`, `client_id`, etc.) se mantienen en la misma request.

## US4 — Layout de Cliente

1. Maestros → Clientes → abrir el detalle de un cliente con varios proyectos.
2. Confirmar layout en columnas en una ventana de escritorio ancha; reducir el ancho de la ventana y
   confirmar que se apila de forma legible.

## US5 — Editar nombre en Catálogos

1. Maestros → Catálogos → en cualquier tarjeta (ej. Herramientas), usar el nuevo botón "Editar"
   sobre un registro existente, cambiar el nombre y guardar.
2. Recargar la página → el nuevo nombre persiste.
3. Verificar que un ticket que ya referencia ese registro (ej. por `tool_id`) muestra el nombre
   actualizado.
4. Repetir el intento con un nombre duplicado dentro del mismo catálogo → debe rechazarse con
   mensaje claro (409).

## Pruebas automatizadas (alcance, Principio VII)

Limitar a los archivos tocados, sin correr la suite completa, ejemplo:

```bash
pytest backend/tests/api/test_teams_catalog.py backend/tests/api/test_ticket*.py -k "sort or rename" -q
```

Sin insertar más de 5-10 registros de prueba por test.
