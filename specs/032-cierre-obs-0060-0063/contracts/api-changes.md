# API Contract Deltas: Cierre de OBS-0060–OBS-0063

Este feature no agrega endpoints nuevos. OBS-0060/OBS-0061 son puramente de presentación en frontend (sin tocar ningún contrato). OBS-0062 y OBS-0063 amplían el comportamiento de dos endpoints ya existentes, de forma aditiva/no rompiente.

## POST /api/tickets/{id}/reassign — OBS-0062, OBS-0063

**Sin cambios de request/response schema.** `_reassign_input`/`_reassign_result_out` no cambian.

**Nuevo efecto secundario (OBS-0062)**: al completar exitosamente la reasignación, el endpoint ahora también persiste una `Notification` (`event_type="reassigned"`) para el `User` vinculado al nuevo `assignee_id`, igual que `POST /api/tickets/{id}/assign` ya hace hoy con `event_type="assigned"`. No es visible en el response del endpoint (la notificación se consulta vía `GET /api/notifications`, ya existente); es un side-effect atómico dentro de la misma transacción.

**Validación ampliada (OBS-0063)**: el `400 resource_inactive` que ya devolvía este endpoint cuando `Resource.active = false` ahora también se dispara cuando el `Resource` candidato tiene una cuenta `User` vinculada (`resource.user_id` no nulo) con `active = false`. Mismo código de error, mismo status 400 — sin cambio de contrato, solo de cuándo se dispara.

## POST /api/tickets/{id}/assign — OBS-0063

**Sin cambios de request/response schema.** Misma ampliación de validación que en `/reassign`: el `400 resource_inactive` ya existente ahora también cubre el caso de cuenta de usuario vinculada inactiva.

## GET /api/resources (o el endpoint que consume `resourceService.list({ active: true })`) — OBS-0063

**Sin cambios de contrato de la API en sí.** El filtrado adicional (excluir recursos cuya cuenta de usuario vinculada esté inactiva) se resuelve en el mismo punto donde hoy se filtra por `Resource.active` — a decidir en tasks si se resuelve server-side (ampliando el filtro `active` del propio endpoint) o client-side en `useResourceCandidates`, sin que ninguna de las dos opciones cambie la forma del payload `Resource` ya documentado.

## GET /api/notifications — OBS-0062

**Sin cambios de contrato.** El objeto `Notification` ya serializado no gana campos nuevos; el enriquecimiento de contenido (cliente, prioridad, estado, quién asignó) va dentro del campo `message` (string) ya existente, igual que el resto de plantillas de `_MESSAGES`.
