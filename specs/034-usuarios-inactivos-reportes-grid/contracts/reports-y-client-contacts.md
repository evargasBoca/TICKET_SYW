# Contract: Deshabilitación de Usuario/cliente + Módulo de Reportes (spec 034)

Endpoints nuevos, documentados en Swagger vía Flask-RESTX (Principio I) antes de implementarse.

## Deshabilitación de Usuario/cliente (`backend/api/routes/client_contacts.py`)

### `GET /api/client-contacts` (cambio aditivo)

Agrega `active` (boolean) a cada item de la respuesta y acepta `active` (`true`/`false`) como
filtro opcional de query, además de los ya existentes (`client_id`, `project_id`, `email`,
`username`). Mismo permiso ya vigente (`client_contacts:manage` o `tickets:create`/`edit`).

### `PATCH /api/client-contacts/{contact_id}/active` — cambiar estado

**Permiso**: `require_permission("client_contacts", "manage")` (mismo que ya usa Coordinador/
Admin para crear estas cuentas — Decisión 1 de `research.md`).

**Body**: `{"active": false}` o `{"active": true}`

**200**: `{"id": "uuid", "active": false}`

**404** `not_found`: el Usuario/cliente no existe. **409** `already_active`/`already_inactive`:
sin cambio real de estado (idempotencia explícita, mismo patrón que
`/api/users/{id}/activate`).

### `POST /api/client-contacts/{contact_id}/projects` (cambio de validación)

Gana una validación previa: si el Usuario/cliente está `active: false`, responde
**409** `contact_inactive` ("El Usuario/cliente está deshabilitado") en vez de crear la
membresía (FR-003).

## Módulo de Reportes (`backend/api/routes/reports.py`, namespace nuevo)

Todos los endpoints de este namespace requieren `require_permission("reports", "view")`
(Decisión 7 de `research.md` — otorgado a Admin/Coordinador/QM).

### `GET /api/reports/tickets` — filas + agregados del reporte

**Query params**: `date_from`, `date_to` (ISO date), `client_id`, `project_id`, `assignee_id`
(UUID, combinables), `page` (default 1), `page_size` (máx 200, default 50), `aggregate`
(repetible, formato `campo:funcion`, ej. `total_logged_minutes:sum`).

**200**:
```json
{
  "items": [{"ticket_id": "uuid", "ticket_number": 123, "title": "...",
             "client_name": "Aris", "project_name": "Soporte", "assignee_name": "Juan Pérez",
             "tool_name": "JDE", "process_name": "GL", "skills": ["JDE_GL"],
             "time_to_first_contact_seconds": 3600, "execution_time_seconds": 7200,
             "total_logged_minutes": 180, "status": "cerrado", "priority": "p2",
             "created_at": "2026-07-01T10:00:00Z"}],
  "total": 42, "page": 1, "page_size": 50,
  "aggregates": {"total_logged_minutes": {"sum": 4200}, "ticket_id": {"count": 42}}
}
```

`aggregates` se calcula sobre **todo** el conjunto filtrado, no solo la página actual
(Decisión 6). **400** `validation_error`: `date_from` posterior a `date_to`, o función de
agregación pedida sobre un campo no numérico (FR-012).

### `GET /api/reports/tickets/export` — exportar a Excel

Mismos query params que el endpoint anterior (sin `page`/`page_size` — exporta el conjunto
filtrado completo) más `columns` (lista repetible de claves de columna, en el orden a exportar).

**200**: binario `.xlsx`
(`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
`Content-Disposition: attachment; filename="reporte_tickets.xlsx"`).

**400** `no_data`: el filtro no produce ninguna fila (Edge Case US5 — se avisa en vez de generar
un archivo vacío).

### `GET /api/reports/views` — listar Vistas Personalizadas del usuario autenticado

**200**: `{"items": [{"id": "uuid", "name": "Mi vista", "config": {...}, "updated_at": "..."}]}`
— solo las del usuario actual (FR-014).

### `POST /api/reports/views` — guardar/actualizar una Vista Personalizada

**Body**: `{"name": "Mi vista", "config": {...}}` (ver forma de `config` en `data-model.md`).

**201**/**200**: la vista guardada (upsert por `(user_id, name)` — Edge Case nombre duplicado).

### `DELETE /api/reports/views/{view_id}` — eliminar una Vista Personalizada propia

**204**. **404** si no existe o pertenece a otro usuario (mismo criterio de ownership que el
resto del sistema).
