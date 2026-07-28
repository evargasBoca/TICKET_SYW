# Research: Cierre de OBS-0044–OBS-0047 (ITER-008)

Investigación de causa raíz sobre el código real antes de planificar, para cada una de las 4 observaciones. No hay `NEEDS CLARIFICATION` pendientes — las 4 causas se confirmaron leyendo el código existente.

## Decisión 1 — OBS-0044: causa raíz confirmada en el formateo de hora en frontend, no en el almacenamiento

**Decision**: El desfase (~5h, coincide con UTC-5 de Bogotá/Guayaquil) se corrige reemplazando el slicing crudo del string ISO por un formateo que respeta la zona horaria del navegador, usando `date-fns` (ya aprobado, Principio V de la Constitución). No se requiere cambio en backend ni migración de datos: el dato guardado ya es correcto.

**Rationale**: Se rastreó el flujo completo:
- **Escritura** (`frontend/src/components/worksessions/WorkSessionForm.tsx:40-45`, función `toIsoDateTime`): combina `work_date` + hora local ingresada y agrega el offset real del navegador (ej. `-05:00`), produciendo un ISO-8601 correcto. El dato persistido en `work_sessions.started_at`/`ended_at` (`TIMESTAMP WITH TIME ZONE`, `backend/infra/models/work_session_model.py:18-19`) es correcto.
- **Lectura/presentación**: la API devuelve `ws.started_at.isoformat()` (`backend/api/routes/work_sessions.py:157-158`), que al venir de una columna `timezone=True` se normaliza a UTC (ej. `...T22:37:00+00:00` para un `17:37` local en Bogotá). El frontend, en dos lugares, hace `iso.slice(11, 16)` sobre ese string — una extracción de substring que asume (incorrectamente) que ya está en hora local, cuando en realidad toma la hora en UTC:
  - `frontend/src/components/worksessions/TimeLogModal.tsx:38-43` (`formatTimeRange`, historial de registros — el bug reportado en OBS-0044/evidencia).
  - `frontend/src/components/worksessions/WorkSessionForm.tsx:35-36` (`timeOf`, precarga del formulario de edición — mismo defecto, no reportado explícitamente pero mismo origen; FR-002 exige consistencia entre pantallas).

**Alternatives considered**:
- Cambiar el tipo de columna a `TIMESTAMP WITHOUT TIME ZONE` y asumir siempre hora local del servidor: rechazado — rompe con equipos en distintas zonas horarias (Aris `America/Bogota` vs Vaxthera `America/Guayaquil`, ambos ya modelados con timezone propio desde specs 020-022) y contradice el patrón ya usado en el resto de la app (calendarios, SLA).
- Convertir en el backend a la zona horaria del recurso antes de serializar: rechazado — el patrón ya establecido en la Constitución (`date-fns` en frontend) resuelve esto sin tocar el contrato de API ni el resto de consumidores del endpoint.

## Decisión 2 — OBS-0045: reubicación visual del badge, mismo dato ya calculado

**Decision**: Mover el `<Tag>` "Fuera de jornada" fuera de la columna "Fecha" (donde hoy convive apretado junto al `Space` de la fecha, `TimeLogModal.tsx:85-97`) hacia la columna "Horario" (donde vive `formatTimeRange`, `TimeLogModal.tsx:99-102`), como badge al final del texto del horario o en una sub-línea propia — sin tocar el criterio `off_hours` (ya resuelto en `sla_service.is_off_hours`, spec 028) ni el dato en sí.

**Rationale**: El componente ya calcula y expone `record.off_hours` correctamente; el defecto es puramente de layout (Ant Design `Space` con `Tag` y texto de fecha compitiendo por el mismo espacio horizontal angosto de la columna "Fecha"). Mover el badge a la columna "Horario" (más ancha, dedicada) resuelve la superposición reportada sin lógica nueva.

**Alternatives considered**: ícono con tooltip en vez de badge de texto — es la alternativa que menos espacio ocupa, mencionada en `ITER-008.md` como opción; se prefiere el badge en la columna "Horario" (más consistente con el patrón `Tag` ya usado en el resto de la tabla, ej. columna "Estado" de tickets) sobre introducir un ícono nuevo sin necesidad.

## Decisión 3 — OBS-0046: falta el disparo de notificación específicamente en `/reassign`, no en `/assign`

**Decision**: Replicar en `POST /api/tickets/{id}/reassign` (`backend/api/routes/tickets.py:1121-1165`) el mismo patrón de notificación atómica que ya usa `POST /api/tickets/{id}/assign` (líneas 1106-1109: `NotificationRepository(db).add(_notif_svc.build(assignee.user_id, "assigned", ...), commit=False)`), agregando un nuevo `event_type` `"reassigned"` en `backend/domain/services/notification_service.py` y `EVENT_TYPES` (`backend/domain/entities/notification.py`). El mensaje se enriquece para incluir cliente, prioridad, estado y quién asignó (FR-008); la fecha/hora ya la cubre el campo `created_at` de `Notification`, ya renderizado por el centro de notificaciones existente.

**Rationale**: El sistema de notificaciones ya existe y ya funciona para la asignación inicial (Triage Push) — la evidencia adjunta en `ITER-008.md` (`OBS-0046-01.png`) de hecho muestra ese caso funcionando ("Se te asignó el ticket TK-000002..."). El endpoint `/reassign` (spec 023) es una ruta de código independiente y separada de `/assign` (por diseño, ver Constitución — "endpoints de acción crítica no acoplados") que nunca invoca `NotificationService`; ese es el vacío puntual reportado.

**Alternatives considered**: unificar `/assign` y `/reassign` en un solo endpoint: rechazado — contradice explícitamente la Constitución ("Los endpoints de accion critica... NO pueden ser refactorizados para acoplarlos... sin aprobación explícita de arquitectura") y el propio código ya documenta la separación como decisión deliberada (research.md de spec 023, Decisión 3). Se agrega la notificación en el sitio de la reasignación, sin fusionar rutas.

## Decisión 4 — OBS-0047: el resolutor asignable se valida contra `Resource.active`, pero no contra el `User.active` (cuenta de acceso) vinculado

**Decision**: Extender la validación de asignación/reasignación para rechazar también cuando el `Resource` candidato tiene una cuenta de `User` vinculada (`resource.user_id`) marcada como Inactiva (`users.active = false`), además del chequeo ya existente sobre `Resource.active`. Aplica tanto al filtrado de candidatos en el selector (frontend) como a la validación atómica en backend (ambos endpoints).

**Rationale**: Se verificó que `AssignmentService.validate` (`backend/domain/services/assignment_service.py:26-27`) y `ReassignmentService.validate` (`backend/domain/services/reassignment_service.py:22-23`) **ya** rechazan un recurso con `Resource.active = False`, y que el selector de resolutores (`frontend/src/components/tickets/useResourceCandidates.ts:26`, compartido por asignación inicial y reasignación desde spec 024) **ya** filtra `resourceService.list({ active: true, ... })`. Es decir: un "Recurso" desactivado (botón "Desactivar recurso (RRHH)" en `TeamPage.tsx`) ya está correctamente bloqueado hoy en ambos flujos.

Sin embargo, `TeamPage.tsx` (líneas 82, 303-320, 532-536) expone **dos toggles independientes**: "Desactivar recurso (RRHH)" (`resourceService.deactivate`, afecta `resources.active`) y "Desactivar cuenta (acceso)" (`userService.deactivate`, afecta `users.active`) — dos entidades separadas por diseño (`Resource.user_id` es una FK opcional hacia `User`). Ninguna validación de asignación consulta hoy el segundo campo. Esto reproduce exactamente lo reportado en `OBS-0047`: un resolutor cuya *cuenta* fue desactivada (sin acceso al sistema) sigue apareciendo como opción válida y puede recibir tickets nuevos que nunca podrá atender, porque su `Resource.active` permanece `true`.

**Alternatives considered**:
- Fusionar `Resource.active` y `User.active` en un único campo: rechazado — son conceptos legítimamente distintos ya modelados así desde specs anteriores (un recurso puede estar temporalmente inactivo por RRHH sin perder su cuenta, o una cuenta puede bloquearse por seguridad sin dar de baja al recurso); cambiar el modelo de datos excede el alcance de este cierre de observación y no lo pide ningún criterio de aceptación.
- Bloquear solo en frontend (ocultar del selector) sin tocar el backend: rechazado — el mismo `ITER-008.md`/FR-011 exige que la API rechace también un intento directo que omita el selector, consistente con el patrón ya usado por el propio chequeo existente de `Resource.active` (defensa en profundidad, Principio IV de la Constitución).
