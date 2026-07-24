# API Contract Deltas: Cierre de observaciones "Abierta" del Backlog UAT

Este feature no agrega endpoints nuevos. Todos los cambios son correcciones de comportamiento y/o ampliaciones puntuales de payload sobre endpoints ya documentados en el Swagger/OpenAPI auto-generado por Flask-RESTX (Principio I — el contrato Swagger se actualiza junto con el código del endpoint, antes de considerarse terminado). Se documentan aquí como delta respecto al contrato actual.

## POST /api/tickets (crear ticket) — US3

**Sin cambios de forma** en el request/response. Cambia la **validación** de `title`:

- 400 nuevo caso: `{"error": "title_blank", "message": "El título es obligatorio"}` cuando el título, tras `strip()`, queda vacío (antes: se aceptaba y creaba el ticket).
- 400 nuevo caso: `{"error": "title_invalid_chars", "message": "El título no admite emojis"}` cuando el título contiene uno o más caracteres emoji.
- Comportamiento sin cambios para títulos válidos.

## PATCH /api/tickets/{id}/status — US1

**Sin cambios de forma.** Los campos `sla_consumed_seconds`, `sla_status`, `sla_phase` en la respuesta deben quedar correctos (calendario-conscientes) en todos los casos, incluyendo transición ocurrida fuera de horario laboral — hoy pueden quedar inflados por la causa raíz documentada en `research.md` §1.

## POST /api/tickets/{id}/assign — US1

**Sin cambios de forma ni de validación** (se sigue permitiendo asignar en cualquier momento — FR-004). Se agrega, en el detalle del ticket (`GET /api/tickets/{id}`), la exposición explícita de los timestamps ya almacenados:

```jsonc
// GET /api/tickets/{id} — respuesta ampliada (campos nuevos en el payload, no en el modelo)
{
  // ...campos existentes...
  "created_at": "2026-07-24T10:00:00Z",
  "assigned_at": "2026-07-24T10:05:00Z",       // ya existía en el historial de asignaciones; se expone en el detalle
  "sla_effective_start": "2026-07-24T13:00:00Z", // = sla_last_resume_at, renombrado en el payload para claridad de negocio
  "work_period_start": "2026-07-24T08:00:00Z"    // inicio de la jornada laboral aplicable, derivado (no persistido)
}
```

## POST /api/timer/start (o el endpoint equivalente de `ticket_timer_service.start`) — US2

**Nuevo caso de error 409**, moviendo el chequeo que hoy solo ocurre en `finish()`:

```jsonc
{"error": "ticket_closed", "message": "No se puede iniciar un registro de tiempo en un ticket cerrado"}
```

## Transición de ticket a `cerrado` (efecto lateral) — US2

Al persistir la transición a `cerrado` (dentro de `PATCH /api/tickets/{id}/status`), si el recurso tiene un `TicketTimer` activo sobre ese ticket:
- Se detiene automáticamente y se crea la `WorkSession` correspondiente con el tiempo acumulado (mismo `WorkSessionService.create()` ya usado por `finish()`).
- La respuesta de `PATCH .../status` no cambia de forma; el cliente debe re-consultar el estado del timer (`GET` del timer activo, ya existente) tras un cambio de estado a `cerrado`.

## POST /api/work-sessions y timer finish — US6

**Response ampliada**: el objeto `WorkSession` devuelto incluye el campo nuevo:

```jsonc
{
  // ...campos existentes...
  "off_hours": false
}
```

Sin cambios de request (no se acepta `off_hours` como input; es siempre calculado server-side).

## POST /api/sla-rules y PUT /api/sla-rules/{id} — US4

**Nuevo caso de error 400** (además del ya existente para valores `<= 0`):

```jsonc
{"error": "max_exceeded", "message": "El tiempo máximo permitido es de 21600 minutos (15 días)"}
```

Aplica a `contact_minutes` y `execution_minutes`.

## GET /api/resources/{id}/work-schedule, GET /api/absence-requests — US5

**Sin cambios de contrato** — ya existen y ya son consumidos por `calendarService.ts`. El delta es exclusivamente de integración frontend (`TeamOverlayCalendar` debe llamarlos y renderizar el resultado), no de backend.
