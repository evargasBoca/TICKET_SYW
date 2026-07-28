# Data Model: Cierre de OBS-0060–OBS-0063 (ITER-009)

Ninguna de las 4 observaciones requiere una migración de Alembic ni columnas nuevas. Todos los campos usados ya existen; este documento detalla cómo se usan/relacionan para esta corrección.

## WorkSession (existente, sin cambios de esquema)

- `started_at`, `ended_at` (`TIMESTAMP WITH TIME ZONE`): ya se almacenan correctamente con el offset real del cliente (ver research.md Decisión 1). No se modifica el modelo ni la API — solo el formateo de presentación en frontend.
- `off_hours` (`Boolean`, spec 028): sin cambios en su cálculo (`sla_service.is_off_hours`); solo cambia dónde se renderiza el `<Tag>` correspondiente en `TimeLogModal.tsx`.

## Notification (existente, se agrega un `event_type`)

- `event_type` (`str`): catálogo cerrado en `backend/domain/entities/notification.py` (`EVENT_TYPES`). Se agrega `"reassigned"` junto a los ya existentes (`"assigned"`, `"user_replied"`, `"resolution_rejected"`, `"closed"`, `"close_eligible"`).
- `message` (`str`): plantilla en `backend/domain/services/notification_service.py` (`_MESSAGES`). La entrada `"assigned"` y la nueva `"reassigned"` se enriquecen para incluir cliente, prioridad, estado actual y quién realizó la (re)asignación (FR-008), además del número/título de ticket ya incluidos hoy.
- `ticket_id` / `created_at`: sin cambios — ya habilitan, respectivamente, la navegación al detalle del ticket (FR-010) y la fecha/hora mostrada en el centro de notificaciones.
- Relación sin cambios: `Notification.user_id` sigue siendo el `User.id` del `Resource.user_id` del nuevo/actual resolutor (mismo patrón que `/assign` ya usa en `backend/api/routes/tickets.py:1106-1109`).

## Resource / User (existentes, se cruza una validación que hoy no existe)

- `Resource.active` (`Boolean`): ya validado por `AssignmentService`/`ReassignmentService` — sin cambios.
- `Resource.user_id` (`UUID`, FK opcional a `users.id`): relación ya existente, usada hoy solo para enrutar notificaciones (`if assignee.user_id: ...`).
- `User.active` (`Boolean`): **nueva regla** — al validar una asignación/reasignación, si `Resource.user_id` no es nulo, el `User` vinculado también debe tener `active = true`; si el `User` vinculado está inactivo, la asignación se rechaza igual que si `Resource.active` fuera `false` (mismo código de error `resource_inactive`, mismo mensaje al usuario: "el usuario seleccionado no se encuentra disponible", FR-013).
- Un `Resource` sin `user_id` (recurso sin cuenta de acceso propia, si existiera) no se ve afectado por esta regla nueva — solo aplica cuando hay una cuenta vinculada y esa cuenta está inactiva.

### Validation rules (resumen por observación)

| Regla | Origen | Dónde se aplica |
|---|---|---|
| Hora mostrada = hora ingresada (conversión a timezone local del navegador, no slicing de string UTC) | OBS-0060 / FR-001, FR-002 | `TimeLogModal.tsx`, `WorkSessionForm.tsx` (frontend, presentación) |
| Etiqueta "Fuera de jornada" no se superpone al horario | OBS-0061 / FR-003, FR-004 | `TimeLogModal.tsx` (frontend, layout de columnas) |
| Notificación `"reassigned"` con datos mínimos al reasignar | OBS-0062 / FR-006 a FR-009 | `TicketReassign` (backend, `tickets.py`), `NotificationService` |
| Notificación dirige al detalle del ticket | OBS-0062 / FR-010 | Frontend, componente del centro de notificaciones (ya soportado vía `ticket_id`) |
| Rechazar asignación/reasignación si `Resource.active = false` **o** `User.active = false` (cuenta vinculada) | OBS-0063 / FR-011 a FR-013 | `AssignmentService.validate`, `ReassignmentService.validate` (backend); `useResourceCandidates`/filtro de selector (frontend) |
| Asignaciones existentes de un usuario que luego pasa a Inactivo no se alteran retroactivamente | OBS-0063 / FR-014 | Sin cambio de comportamiento — no hay job/trigger que reaccione a la desactivación |
