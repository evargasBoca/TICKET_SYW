# API Contract Deltas: Cierre de OBS-0042/OBS-0043

Este feature no agrega endpoints nuevos. OBS-0042 no toca ningún contrato de API (es un cambio puramente visual del frontend). OBS-0043 amplía, de forma aditiva, el payload ya documentado en el Swagger/OpenAPI auto-generado por Flask-RESTX (Principio I).

## GET /api/sla-rules, POST /api/sla-rules, PATCH /api/sla-rules/{id} — OBS-0043

**Response ampliada** (mismo objeto `SlaRule` en los tres endpoints, vía `_serialize()`):

```jsonc
{
  "id": "uuid",
  "project_id": "uuid",
  "project_name": "Soporte",
  "client_id": "uuid",        // nuevo
  "client_name": "Aris",      // nuevo
  "priority": "high",
  "contact_minutes": 15,
  "execution_minutes": 480,
  "active": true,
  "created_at": "iso8601"
}
```

**Sin cambios de request**: `SlaRuleInput`/`SlaRulePatchInput` no aceptan `client_id`/`client_name` como input; se derivan siempre server-side desde `project_id`. Sin cambios de comportamiento de validación ni de errores existentes (`400 validation_error`, `400 max_exceeded`, `409` de regla duplicada, definidos en spec 014/028).

## GET /api/projects (o el endpoint que consume `projectService.list()`) — OBS-0043

**Sin cambios de contrato.** `client_id`/`client_name` ya existían en la respuesta y ya se usan en otras pantallas (Maestros > Proyectos, specs 001/010/015/016); este feature solo cambia cómo el frontend renderiza esos campos ya disponibles en el selector "Filtrar por proyecto" y en el formulario de SLA.

## GET /api/tickets/{id} — OBS-0042

**Sin cambios de contrato.** El reordenamiento de "Clasificación"/"Comentarios y acciones" es exclusivamente de disposición visual en `TicketDetailPage.tsx`; no cambia ningún campo consumido del detalle del ticket.
