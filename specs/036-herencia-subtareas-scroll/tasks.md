---

description: "Task list for 036-herencia-subtareas-scroll"
---

# Tasks: Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering en Scroll del Ticket

**Input**: Design documents from `/specs/036-herencia-subtareas-scroll/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/subtask-inheritance-and-parent-link.md](contracts/subtask-inheritance-and-parent-link.md), [quickstart.md](quickstart.md)

**Tests**: incluidos de forma acotada (Principio VII — solo el caso de herencia en creación de Subtarea, backend; ≤10 registros de prueba por test; sin suite de frontend automatizada, el bug de scroll se valida manualmente).

**Organización**: por historia de usuario. US1/US2/US3 comparten `backend/api/routes/tickets.py` (bloque `if parent_task_id:` y `_ticket_detail`) y US3 además toca `TicketDetailPage.tsx` — no son parallel-safe entre sí; ejecutar en el orden de fases indicado. US4 (fix de scroll) es completamente independiente (mismo archivo `TicketDetailPage.tsx` pero función/bloque disjunto de US3).

## Path Conventions

Web app existente: `backend/{domain,infra,api}/`, `frontend/src/{components,services,pages,types}/` (ver Project Structure de [plan.md](plan.md)).

---

## Phase 1: Setup

No aplica — sin dependencias nuevas (Principio V), sin estructura de proyecto nueva. Se reutiliza el directorio de spec `036-herencia-subtareas-scroll` ya creado.

## Phase 2: Foundational

No aplica — ninguna historia depende de infraestructura compartida nueva (sin migraciones, sin modelos nuevos; `parent_task_id`, `escalation_level`, `client_contact_id` y la relación `ticket_skills` ya existen). Cada historia puede iniciar directamente.

---

## Phase 3: User Story 1 - Herencia automática al crear una Subtarea (Priority: P1) 🎯 MVP

**Goal**: Al crear una Subtarea desde una Tarea padre, Nivel de escalamiento, Usuario solicitante/cliente y Skills requeridas se copian automáticamente cuando no vienen explícitos en el payload.

**Independent Test**: Crear una Tarea con Nivel de escalamiento ≠ "N2", un Usuario solicitante y 1-2 Skills; crear una Subtarea desde ella sin tocar esos 3 campos; abrir el detalle de la Subtarea y confirmar que los 3 valores llegaron precargados iguales a los de la Tarea padre.

### Tests for User Story 1

- [X] T001 [P] [US1] Test acotado (≤10 registros) en `backend/tests/api/test_tickets_subtasks.py` para `POST /api/tickets` con `parent_task_id`: crear una Tarea padre con `escalation_level="n3"`, `client_contact_id` y 2 skills, crear una Subtarea sin enviar esos 3 campos, y verificar en la respuesta `201` que la Subtarea tiene el mismo `escalation_level`, `client_contact_id` y el mismo set de `skill_ids` que la Tarea padre
- [X] T002 [P] [US1] Test acotado en el mismo archivo: crear una Subtarea enviando `escalation_level` explícito distinto al de la Tarea padre, y verificar que se respeta el valor enviado (no se sobreescribe con el heredado)

### Implementation for User Story 1

- [X] T003 [US1] En `backend/api/routes/tickets.py`, dentro del bloque `if parent_task_id:` (línea ~879, donde ya se hereda `list_id`), agregar: si `data.get("escalation_level")` es falsy, usar `parent_ticket.escalation_level` en vez de `"n2"` al construir `Ticket(...)` (línea ~928); si `client_contact_id` (variable local, resuelta antes en la función) es `None`, usar `parent_ticket.client_contact_id`
- [X] T004 [US1] En el mismo bloque de `backend/api/routes/tickets.py`, tras `created = TicketRepository(db).create(ticket)` (línea ~936), si `parent_task_id` está presente y el payload no trae `skill_ids` propios, llamar a `TicketRepository(db).update_skills(created.id, [s.id for s in parent_ticket.skills])` para copiar el set completo de Skills de la Tarea padre
- [X] T005 [US1] Verificación manual contra Docker real siguiendo `quickstart.md` Escenario 1 y 2 (herencia + independencia posterior), ≤10 registros de prueba

**Checkpoint**: Una Subtarea nueva nace con Nivel de escalamiento, Usuario solicitante y Skills heredados de su Tarea padre, editable de forma independiente después.

---

## Phase 4: User Story 2 - Referencia bidireccional Tarea padre ↔ Subtareas (Priority: P1)

**Goal**: El detalle de la Tarea padre muestra el conteo y listado clicable de sus Subtareas.

**Independent Test**: Crear 2-3 Subtareas desde la misma Tarea padre y confirmar que su detalle muestra las 3, cada una navegable.

### Implementation for User Story 2

- [X] T006 [US2] Confirmar (sin cambios de código esperados) que `_ticket_detail` en `backend/api/routes/tickets.py` (línea ~517-532) ya devuelve `subtasks` completo y que `frontend/src/components/tickets/SubtaskList.tsx` ya lista y navega a cada una (`ticket.subtasks.map(...)`, `onClick={() => navigate(...)}`); si el conteo visible ("N Subtareas") no está explícito en el título de la Card "Subtareas" de `TicketDetailPage.tsx` (línea ~502), agregarlo derivándolo de `ticket.subtasks.length`
- [X] T007 [US2] Verificación manual contra Docker real siguiendo `quickstart.md` Escenario 3 (crear varias Subtareas, confirmar listado + navegación desde la Tarea padre)

**Checkpoint**: La Tarea padre expone conteo y navegación a todas sus Subtareas.

---

## Phase 5: User Story 3 - Hipervínculo a la Tarea Padre desde la Subtarea (Priority: P2)

**Goal**: El detalle de una Subtarea muestra, en "Clasificación", el campo "Tarea Padre" como hipervínculo a la Tarea de origen.

**Independent Test**: Abrir el detalle de una Subtarea y confirmar que "Tarea Padre" aparece con el código/título de la Tarea origen y que el clic navega a su detalle; confirmar que el campo no aparece en un Ticket/Tarea sin `parent_task_id`.

### Implementation for User Story 3

- [X] T008 [US3] En `backend/api/routes/tickets.py`, agregar una función `_parent_summary(ticket, db) -> dict | None` (mismo patrón que `_ticket_summary`/`_related_from`) que resuelve `TicketRepository(db).get_by_id(ticket.parent_task_id)` y devuelve `{"id": str(parent.id), "ticket_number": parent.number_display, "title": parent.title}` solo si `ticket.parent_task_id` no es `None`
- [X] T009 [US3] En `_ticket_detail` (misma archivo, dentro del `d.update({...})` de la línea ~519), agregar `"parent": _parent_summary(ticket, db)` sin remover el campo `parent_task_id` ya existente
- [X] T010 [P] [US3] En `frontend/src/types/ticket.ts`, agregar a la interfaz `TicketDetail` el campo `parent: { id: string; ticket_number: string; title: string } | null`
- [X] T011 [US3] En `frontend/src/pages/TicketDetailPage.tsx`, Card "Clasificación" (línea ~254-399), agregar `<Descriptions.Item label="Tarea Padre">` condicionado a `ticket.parent` truthy, con un `Button type="link"` que navega a `/tickets/${ticket.parent.id}` mostrando `${ticket.parent.ticket_number} — ${ticket.parent.title}` (mismo patrón ya usado ahí para "Registro relacionado", línea ~300)
- [X] T012 [US3] Verificación manual contra Docker real siguiendo `quickstart.md` Escenario 4 (campo visible + navegación en Subtarea; ausente en Ticket normal)

**Checkpoint**: Toda Subtarea muestra un hipervínculo funcional a su Tarea padre.

---

## Phase 6: User Story 4 - Eliminar el parpadeo (flickering) en el detalle del Ticket (Priority: P1)

**Goal**: El panel izquierdo (Clasificación + Historial) del detalle del Ticket/Tarea deja de parpadear al hacer scroll.

**Independent Test**: Abrir el detalle de cualquier Ticket/Tarea con altura de ventana que fuerce scroll, desplazarse repetidamente (lento y rápido, ambas direcciones) durante ≥30s y confirmar ausencia de parpadeo/saltos visuales.

### Implementation for User Story 4

- [X] T013 [US4] En `frontend/src/pages/TicketDetailPage.tsx`, reemplazar el listener de scroll (líneas 88-98) por la versión con zona muerta (12px) + throttle por `requestAnimationFrame` documentada en `research.md` Decisión 4, preservando el comportamiento de colapso/expansión de `timeExpanded` para deltas reales de scroll (no micro-oscilaciones)
- [X] T014 [US4] Verificación manual contra Docker real siguiendo `quickstart.md` Escenario 5: sin parpadeo en un Ticket normal y en la Subtarea creada en Phase 5 (con el campo "Tarea Padre" visible)

**Checkpoint**: Scroll estable en el panel izquierdo del detalle, sin regresión en el resumen de tiempo colapsable ni en el resto del detalle.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T015 [P] Ejecutar `tsc -b` en `frontend/` y confirmar cero errores tras los cambios de US1-US4
- [X] T016 Ejecutar `pytest backend/tests/api/test_tickets_subtasks.py` (acotado a los archivos tocados) — sin correr la suite completa (Principio VII)
- [X] T017 Recorrer `quickstart.md` completo contra Docker real y actualizar `CLAUDE.md` (bloque "Active feature") con el resultado de la validación end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: no aplica (ver Phase 1-2)
- **US1 (Phase 3)**: sin dependencias de otras historias — MVP
- **US2 (Phase 4)**: sin dependencia funcional de US1; comparte `_ticket_detail`/`TicketDetailPage.tsx` — ejecutar después de US1 para evitar conflictos de edición
- **US3 (Phase 5)**: depende de que existan Subtareas para probar (usa las de US1/US2); comparte `_ticket_detail` y la Card "Clasificación" de `TicketDetailPage.tsx` — ejecutar después de US1/US2
- **US4 (Phase 6)**: independiente de US1-US3 en funcionalidad (toca el listener de scroll, un bloque disjunto del mismo archivo `TicketDetailPage.tsx`) — puede ejecutarse en paralelo por un desarrollador distinto, pero si el mismo agente/dev hace todo, ejecutar después de US3 para evitar conflictos de edición concurrente sobre el mismo archivo
- **Polish (Phase 7)**: depende de todas las historias que se decida entregar

### Parallel Opportunities

- Dentro de US1: T001/T002 son `[P]` (mismo archivo de test pero casos independientes, sin dependencia de escritura simultánea real)
- Dentro de US3: T010 (`ticket.ts`) es `[P]` respecto a T008/T009 (backend) — puede escribirse en paralelo, aunque la verificación end-to-end (T012) requiere ambos lados completos
- US4 puede trabajarse en paralelo a US1-US3 si hay más de un desarrollador (archivo compartido pero bloque de código disjunto — el listener de scroll no interseca con la Card "Clasificación")

---

## Implementation Strategy

### MVP First

1. Phase 3 (US1) — herencia automática. Validar independientemente.
2. Phase 4 (US2) — confirmar/ajustar contador y navegación ya existentes. Validar.
3. Phase 5 (US3) — hipervínculo "Tarea Padre". Validar.
4. Phase 6 (US4) — fix de scroll, independiente del resto. Validar.
5. Phase 7 — polish, `tsc -b`, pytest acotado, actualización de `CLAUDE.md`.

### Incremental Delivery

Cada historia es un incremento demostrable por sí solo (ver "Independent Test" de cada fase); US4 en particular puede entregarse sola sin esperar a US1-US3 si se prioriza el fix visual primero.
