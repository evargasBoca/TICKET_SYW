---

description: "Task list for 037-subtareas-en-clasificacion"
---

# Tasks: Referencia a Subtareas dentro de "Clasificación" en la Tarea principal

**Input**: Design documents from `/specs/037-subtareas-en-clasificacion/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Tests**: no aplica — sin cambios de backend (Principio VII); validación manual en Docker real siguiendo `quickstart.md`.

**Organización**: historia única (US1). Todo el cambio cae en un solo archivo (`TicketDetailPage.tsx`), en el bloque ya usado para "Tarea Padre" (spec 036) — no hay paralelismo posible dentro de la historia.

## Path Conventions

Web app existente: `frontend/src/pages/` (ver Project Structure de [plan.md](plan.md)). Sin cambios de backend.

---

## Phase 1: Setup

No aplica — sin dependencias nuevas (Principio V), sin estructura de proyecto nueva.

## Phase 2: Foundational

No aplica — el dato (`ticket.subtasks`) ya existe y ya está tipado (spec 009); ninguna infraestructura nueva que preparar.

---

## Phase 3: User Story 1 - Ver de un vistazo que una Tarea tiene Subtareas, desde su Clasificación (Priority: P1) 🎯 MVP

**Goal**: La Card "Clasificación" del detalle de una Tarea muestra sus Subtareas asociadas (o "Sin subtareas"), cada una navegable, sin depender de la tarjeta lateral separada.

**Independent Test**: Crear una Subtarea desde una Tarea sin Subtareas previas; sin pasos adicionales, ver que "Clasificación" de esa Tarea ahora muestra 1 Subtarea, navegable a su detalle.

### Implementation for User Story 1

- [X] T001 [US1] En `frontend/src/pages/TicketDetailPage.tsx`, dentro de la Card "Clasificación", agregar `<Descriptions.Item label="Subtareas">` inmediatamente después del ítem "Tarea Padre" (agregado en spec 036, condicionado a `ticket.parent`), condicionado a `isTask && !isSubtask` (mismo guard que ya usa la Card lateral "Subtareas", línea ~499): si `ticket.subtasks.length === 0`, renderizar `<em style={{ color: palette.slate400 }}>Sin subtareas</em>` (mismo patrón que "Sin encargado asignado"/"Sin registro relacionado"); si no, un `<Space direction="vertical" size={2}>` con un `<Button type="link" size="small" style={{ padding: 0, height: 'auto' }}>` por cada Subtarea (`{s.ticket_number} — {s.title}`, `onClick={() => navigate(`/tickets/${s.id}`)}`) — mismo patrón ya usado ahí para "Referenciado por"
- [X] T002 [US1] Verificación manual contra Docker real siguiendo `quickstart.md` (Escenarios 1-4: sin subtareas, aparece tras crear una, varias subtareas listadas y navegables, ausente en Ticket/Subtarea)

**Checkpoint**: "Clasificación" refleja de inmediato las Subtareas de la Tarea, sin afectar la tarjeta lateral "Subtareas" existente.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T003 Ejecutar `tsc -b` en `frontend/` y confirmar cero errores
- [X] T004 Actualizar `CLAUDE.md` (bloque "Active feature") con el resultado de la validación end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: no aplica
- **US1 (Phase 3)**: única historia — MVP y entrega completa
- **Polish (Phase 4)**: depende de US1

### Parallel Opportunities

Ninguna — un solo archivo, un solo bloque de cambio, una sola historia.

---

## Implementation Strategy

### MVP First

1. Phase 3 (US1) — único incremento, es la corrección completa reportada por el usuario.
2. Phase 4 — polish (`tsc -b`, actualización de `CLAUDE.md`).
