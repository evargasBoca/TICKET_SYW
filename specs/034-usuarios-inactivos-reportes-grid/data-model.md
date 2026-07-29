# Data Model — Deshabilitación de Usuarios/Cliente y Reportes Dinámicos

## Cambios en entidades existentes

### `users` (sin cambios de esquema)

`active` (boolean, ya existente) pasa a gestionarse explícitamente para el rol Usuario/cliente
desde `client_contacts`. Sin columna nueva, sin migración para esta parte.

### `client_contacts` — respuesta de API (sin columna nueva en la tabla)

`GET /api/client-contacts` agrega el campo derivado `active` (de `users.active` vía `user_id`) a
cada fila de la respuesta, y acepta `active` como filtro opcional de query. La tabla
`client_contacts` en sí no cambia.

## Entidades nuevas

### `report_saved_views`

| Campo | Tipo | Nullable | Notas |
|---|---|---|---|
| `id` | UUID (PK) | No | `gen_random_uuid()` |
| `user_id` | UUID (FK → `users.id`, `ON DELETE CASCADE`) | No | Dueño de la vista — privada, nunca visible para otro usuario (FR-014) |
| `name` | text | No | Nombre elegido por el usuario |
| `config` | JSONB | No | `{"columns": [{"key": str, "visible": bool}], "column_order": [str], "filters": {"date_from": str|null, "date_to": str|null, "client_id": uuid|null, "project_id": uuid|null, "assignee_id": uuid|null}, "aggregations": [{"column": str, "function": "sum"|"avg"|"count"}]}` |
| `created_at` | timestamptz | No | `now()` |
| `updated_at` | timestamptz | No | `now()`, `onupdate=now()` |

**Índice/unicidad**: `UNIQUE (user_id, name)` — guardar con un nombre repetido actualiza
(upsert) en vez de duplicar (Edge Case: nombre duplicado). **Sin RLS** (dato privado de bajo
riesgo, acotado por `user_id` en cada consulta — Decisión 8 de `research.md`).

## Fila de Reporte de Ticket (proyección de solo lectura, sin tabla nueva)

Construida en `backend/infra/repositories/report_repo.py` uniendo entidades ya existentes — no
introduce una fuente de datos nueva:

| Columna del reporte | Origen |
|---|---|
| `ticket_id`, `ticket_number`, `title` | `tickets` |
| `client_id`, `client_name` | `tickets.client_id` → `clients` |
| `project_id`, `project_name` | `tickets.project_id` → `projects` |
| `assignee_id`, `assignee_name` (Encargado/Resolutor) | `tickets.assignee_id` → `resources` |
| `tool_name` (Herramienta) | `tickets.tool_id` → `catalog_tools` |
| `process_name` (Proceso) | `tickets.process_id` → `catalog_processes` |
| `skills` (lista de nombres) | `ticket_skills` → `skills` (agregado como lista, no agregable numéricamente — FR-012) |
| `time_to_first_contact_seconds` | `tickets.sla_contact_consumed_seconds` |
| `execution_time_seconds` | `tickets.sla_execution_consumed_seconds` |
| `total_logged_minutes` (tiempo total registrado) | `SUM(work_sessions.duration_minutes)` agrupado por `work_sessions.ticket_id` |
| `status`, `priority`, `created_at`, `resolved_at`, `closed_at` | `tickets` |

**Filtros soportados** (Decisión 3/6 no aplica aquí): rango de fechas sobre `tickets.created_at`,
`client_id`, `project_id`, `assignee_id` — combinables con `AND`.

**Agregaciones soportadas**: `SUM`/`AVG` sobre `time_to_first_contact_seconds`,
`execution_time_seconds`, `total_logged_minutes`; `COUNT` sobre `ticket_id` (cantidad de
tickets). Cualquier otra columna (texto o lista) no ofrece función de agregación (FR-012).
