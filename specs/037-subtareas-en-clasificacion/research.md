# Research: Referencia a Subtareas dentro de "Clasificación"

## Decisión 1 — Sin cambios de API

**Decisión**: No se toca `backend/api/routes/tickets.py` ni ningún endpoint. `_ticket_detail`
(spec 009, extendido en spec 036 para `parent`) ya devuelve `subtasks: TicketListItem[]`
completo para toda Tarea que no sea Subtarea — el frontend ya tiene todo el dato necesario en
`ticket.subtasks`, solo falta renderizarlo también dentro de la Card "Clasificación".

**Rationale**: Cumple Principio VII (alcance mínimo) — el bug reportado es de visibilidad en el
frontend, no de disponibilidad de datos.

**Alternatives considered**: Ninguna — no hay decisión técnica de backend que tomar.

## Decisión 2 — Ubicación y formato del nuevo campo en "Clasificación"

**Decisión**: Se agrega un `<Descriptions.Item label="Subtareas">` en la Card "Clasificación" de
`TicketDetailPage.tsx`, condicionado a `isTask && !isSubtask` (mismo guard que ya usa la Card
lateral "Subtareas", línea ~499), ubicado inmediatamente después de "Tarea Padre" (agregado en
spec 036) — ambos son referencias cruzadas de la misma relación Tarea↔Subtarea, uno mirando hacia
abajo (Subtareas) y otro hacia arriba (Tarea Padre) — mantenerlos adyacentes es más legible que
dispersarlos en la sección.

Contenido del campo:
- Si `ticket.subtasks.length === 0`: texto `<em>Sin subtareas</em>` (mismo patrón ya usado para
  "Sin encargado asignado", "Sin registro relacionado", "Sin lista" en la misma Card).
- Si `ticket.subtasks.length > 0`: un `Space direction="vertical"` con un `Button type="link"`
  por cada Subtarea (`{s.ticket_number} — {s.title}`, navega a `/tickets/{s.id}`) — mismo patrón
  ya usado para "Referenciado por" (línea ~309) y para el nuevo "Tarea Padre" (spec 036).

**Rationale**: Reutiliza tres patrones ya existentes y aprobados en el mismo componente (el de
"vacío explícito", el de lista de botones-link, y el de ubicación junto a otras referencias
cruzadas) — no se introduce ningún patrón visual nuevo, ni una tabla/subcomponente separado.

**Alternatives considered**:
- Mostrar solo el conteo sin lista navegable (ej. "3 Subtareas", sin links): se descarta porque
  no cumple FR-003 (cada Subtarea debe ser navegable en un clic desde "Clasificación" —
  Acceptance Scenario 4 del spec) y porque el usuario ya tiene un ejemplo de "conteo sin lista"
  en la propia tarjeta lateral "Subtareas (N)" — repetir solo el número sin acceso sería
  redundante en vez de complementario.
- Truncar la lista a los primeros N ítems con "+X más": se descarta como innecesario para el
  alcance de esta corrección (Edge Case del spec permite priorizar legibilidad, pero no exige
  truncar — Ant Design `Descriptions.Item` ya maneja contenido largo con wrap natural; se
  revisita solo si en la validación manual el layout se rompe con muchas Subtareas).
- Eliminar la tarjeta lateral "Subtareas" y mover toda su funcionalidad (listado + creación)
  dentro de "Clasificación": rechazado explícitamente por FR-006/Assumptions del spec — esta
  corrección es aditiva, no una migración de la tarjeta existente (que además contiene el modal
  de creación, fuera de alcance de "Clasificación").

## Decisión 3 — Actualización inmediata tras crear una Subtarea (FR-004)

**Decisión**: Ninguna pieza nueva de sincronización de estado — `SubtaskList.tsx` ya llama a
`onUpdated()` (prop `load` de `TicketDetailPage.tsx`) tras crear una Subtarea (línea ~53),
que vuelve a pedir `GET /api/tickets/{id}` y actualiza `ticket` completo (`setTicket(data)`,
línea ~104 de `TicketDetailPage.tsx`) — como el nuevo campo de "Clasificación" lee del mismo
`ticket.subtasks` ya recargado, se actualiza automáticamente sin código adicional.

**Rationale**: Confirma que FR-004 (actualización inmediata) ya está resuelto por el flujo de
datos existente — el problema reportado por el usuario era puramente de *dónde* se muestra el
dato, no de que el dato no se recargara.
