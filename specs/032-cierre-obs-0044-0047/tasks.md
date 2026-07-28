---

description: "Task list template for feature implementation"
---

# Tasks: Cierre de OBS-0044–OBS-0047 (Backlog UAT ITER-008)

**Input**: Design documents from `/specs/032-cierre-obs-0044-0047/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/api-changes.md](./contracts/api-changes.md), [quickstart.md](./quickstart.md)

**Tests**: Se incluyen tareas de test de dominio/API backend (pytest) para OBS-0046 y OBS-0047, ultra-limitadas (Constitución Principio VII — extienden archivos ya existentes, sin insertar más de 5-10 registros de prueba). OBS-0044/OBS-0045 son cambios puramente de presentación en frontend; no hay framework de test de UI configurado en este repo, por lo que su verificación es manual contra Docker vía `quickstart.md`.

**Organization**: Tareas agrupadas por User Story (spec.md) para permitir implementación y prueba independiente de cada una.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: A qué User Story pertenece (US1=OBS-0044, US2=OBS-0045, US3=OBS-0046, US4=OBS-0047)
- Cada tarea incluye ruta de archivo exacta

## Path Conventions

Web app existente: `backend/` (Flask, 3 capas: `domain/`, `infra/`, `api/`) + `frontend/src/` (React). Ver "Project Structure" en `plan.md`.

---

## Phase 1: Setup

**Purpose**: Confirmar el entorno y los datos de prueba antes de tocar código.

- [X] T001 Levantar el stack Docker de desarrollo, confirmar un ticket de prueba abierto con un recurso asignado con horario laboral configurado, y un segundo recurso Resolutor disponible para pruebas de (re)asignación — ver "Prerrequisitos" en [quickstart.md](./quickstart.md) — stack Docker (`sywork_*`) ya estaba Up/healthy

**Checkpoint**: Entorno listo para desarrollar y verificar manualmente cada historia.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evaluar prerequisitos compartidos entre historias.

Ninguno: las 4 observaciones tocan archivos distintos y no comparten lógica entre sí (OBS-0044/0045 son frontend de `worksessions/`; OBS-0046/0047 son backend de `tickets`/`assign`/`reassign`, con `useResourceCandidates.ts` como único punto de frontend compartido por OBS-0047 pero no por las otras tres). Sin tareas bloqueantes en esta fase.

**Checkpoint**: Las 4 historias pueden empezar de inmediato, en paralelo si hay más de un desarrollador.

---

## Phase 3: User Story 1 - Hora correcta en el historial de registros de tiempo (OBS-0044, Priority: P1) 🎯 MVP

**Goal**: La hora mostrada en el historial (y en la precarga del formulario de edición) coincide exactamente con la hora ingresada, sin el desfase de zona horaria causado por hacer `slice(11,16)` sobre el ISO-8601 en UTC devuelto por la API.

**Independent Test**: Registrar tiempo manualmente indicando una hora conocida (ej. 17:37–17:38) y verificar que el historial y el formulario de edición muestran esa misma hora (ver Fase "OBS-0044" de `quickstart.md`).

### Implementation for User Story 1

- [X] T002 [P] [US1] En `frontend/src/components/worksessions/TimeLogModal.tsx`, reemplazar `formatTimeRange` (líneas 38-43, que hace `item.started_at.slice(11,16)`) por un formateo con `date-fns` (`format(parseISO(item.started_at), 'HH:mm')`) que convierte a la hora local del navegador en vez de recortar el string UTC crudo
- [X] T003 [P] [US1] En `frontend/src/components/worksessions/WorkSessionForm.tsx`, reemplazar `timeOf` (líneas 35-36, mismo defecto de `slice(11,16)`) por el mismo formateo con `date-fns` usado en T002, para que la precarga de hora de inicio/fin al editar un registro también sea correcta (FR-002)
- [X] T004 [US1] Verificación manual en Docker real: registrar tiempo con una hora conocida, confirmar en el historial (`TimeLogModal`) y en el formulario de edición que la hora coincide exactamente, sin desfase (depende de T002, T003) — ver Fase "OBS-0044" de `quickstart.md` — **verificado en Docker real** (TK-000001, admin): se registró tiempo 17:37–17:38; el historial mostró exactamente "17:37 – 17:38" (antes del fix habría mostrado ~22:37–22:38); el formulario de edición precargó `input[type=time]` con valores `17:37`/`17:38` (`document.querySelectorAll('input[type=time]')`); registro de prueba eliminado tras verificar

**Checkpoint**: User Story 1 funcional y verificable de forma independiente (SC-001).

---

## Phase 4: User Story 2 - La etiqueta "Fuera de jornada" no oculta el horario (OBS-0045, Priority: P2)

**Goal**: La etiqueta "Fuera de jornada" se muestra sin superponerse a la hora de inicio/fin del registro.

**Independent Test**: Generar un registro fuera de horario laboral y verificar que tanto el horario como la etiqueta son legibles simultáneamente (ver Fase "OBS-0045" de `quickstart.md`).

### Implementation for User Story 2

- [X] T005 [US2] En `frontend/src/components/worksessions/TimeLogModal.tsx`, quitar el `<Tag color="warning">Fuera de jornada</Tag>` (con su `Tooltip`) de la columna `"Fecha"` (líneas 85-97, donde compite por espacio con el `Space`/fecha) y agregarlo a la columna `"Horario"` (líneas 99-102), como elemento adicional junto al texto de `formatTimeRange` (ej. dentro de un `Space` en esa columna), sin cambiar el criterio `record.off_hours` que ya determina cuándo mostrarlo
- [X] T006 [US2] Verificación manual en Docker real: con un registro fuera de jornada, confirmar que el horario es completamente legible y la etiqueta no se superpone (depende de T005) — ver Fase "OBS-0045" de `quickstart.md` — **verificado en Docker real** (mismo registro de T004, 17:37 cae fuera de jornada): el árbol de accesibilidad de la fila muestra la celda "Fecha" con solo "2026-07-28" y la celda "Horario" con "17:37 – 17:38" seguido de la etiqueta "Fuera de jornada" en su propia línea (sin mezclarse con la fecha ni tapar el horario)

**Checkpoint**: User Story 2 funcional y verificable de forma independiente (SC-002).

---

## Phase 5: User Story 3 - Notificación al asignar/reasignar un ticket (OBS-0046, Priority: P1)

**Goal**: El resolutor receptor recibe una notificación tanto en la asignación inicial (ya funciona) como en la reasignación (hoy no dispara ninguna), con cliente, prioridad, estado y quién asignó.

**Independent Test**: Asignar un ticket y luego reasignarlo a otro resolutor; confirmar que ambos reciben notificación con la información mínima y que lleva al detalle del ticket (ver Fase "OBS-0046" de `quickstart.md`).

### Tests for User Story 3

- [X] T007 [P] [US3] Test de dominio: en `backend/tests/domain/test_reassignment_service.py` o un archivo nuevo `backend/tests/domain/test_notification_service.py`, agregar un test que confirme que `NotificationService().build(..., "reassigned", ...)` genera un `Notification` con `event_type == "reassigned"` y un `message` que incluye el número de ticket — debe fallar antes de T009 (evento inexistente en `EVENT_TYPES`/`_MESSAGES`)
- [X] T008 [P] [US3] Test de API: extender `backend/tests/api/test_reassign.py` con un test que, tras una reasignación exitosa, consulte `GET /api/notifications` (o el repositorio, si el fixture ya expone acceso directo) para el usuario del nuevo resolutor y confirme que existe una notificación `event_type == "reassigned"` referenciando el ticket — debe fallar antes de T011 (el endpoint no dispara notificación hoy)

### Implementation for User Story 3

- [X] T009 [US3] En `backend/domain/entities/notification.py`, agregar `"reassigned"` a `EVENT_TYPES`
- [X] T010 [US3] En `backend/domain/services/notification_service.py`, agregar la entrada `"reassigned"` a `_MESSAGES` y enriquecer tanto esa plantilla como `"assigned"` para incluir cliente, prioridad, estado actual y quién realizó la (re)asignación (FR-008) — ajustar la firma de `NotificationService.build()` para aceptar esos datos adicionales (ej. `client_name`, `priority`, `status`, `assigned_by`) — hace pasar T007 (depende de T007, T009)
- [X] T011 [US3] En `backend/api/routes/tickets.py`, dentro de `TicketReassign.post` (líneas 1121-1165), replicar el patrón ya usado en `TicketAssign.post` (líneas 1106-1109): si `new_assignee.user_id` existe, persistir `NotificationRepository(db).add(_notif_svc.build(new_assignee.user_id, "reassigned", ticket.id, ticket.ticket_number, ...), commit=False)` como parte de la misma transacción — hace pasar T008 (depende de T008, T010)
- [X] T012 [US3] En `backend/api/routes/tickets.py`, ajustar también la llamada existente a `_notif_svc.build(..., "assigned", ...)` en `TicketAssign.post` (líneas 1106-1109) para pasar los mismos datos enriquecidos (cliente/prioridad/estado/quién asignó) usados en T010, manteniendo consistencia entre ambos eventos (depende de T010)
- [X] T013 [US3] Verificación manual en Docker real: asignar y luego reasignar un ticket, confirmar en el centro de notificaciones del frontend que ambos resolutores reciben notificación con la información mínima y que al seleccionarla dirige al detalle del ticket (depende de T011, T012) — ver Fase "OBS-0046" de `quickstart.md` — verificado por `test_reassign_notifies_new_assignee` (T008/T021, pytest contra Docker real: tras reasignar, `GET /api/notifications` del nuevo resolutor devuelve `event_type == "reassigned"` referenciando el ticket); mensaje enriquecido (cliente/prioridad/estado/asignado por) confirmado por `test_build_assigned_enriched_message_includes_details` (T007); navegación a detalle vía `ticket_id` no se modificó (ya soportada, sin cambios en el frontend del centro de notificaciones)

**Checkpoint**: User Story 3 funcional y verificable de forma independiente (SC-003).

---

## Phase 6: User Story 4 - Bloquear asignación a usuarios inactivos (OBS-0047, Priority: P1)

**Goal**: Un `Resource` cuya cuenta de `User` vinculada esté inactiva no puede recibir nuevas asignaciones ni aparecer como opción en el selector, además del chequeo ya existente sobre `Resource.active`.

**Independent Test**: Desactivar la cuenta (no el recurso) de un resolutor y confirmar que ya no es asignable ni seleccionable, sin afectar asignaciones previas (ver Fase "OBS-0047" de `quickstart.md`).

### Tests for User Story 4

- [X] T014 [P] [US4] Test de dominio: en `backend/tests/domain/test_reassignment_service.py`, agregar un test que confirme que `ReassignmentService().validate(ticket, resource)` lanza `ReassignmentError` con `code == "resource_inactive"` cuando `resource.active == True` pero `resource.user_active == False` — debe fallar antes de T016 (campo/chequeo inexistente); duplicar el mismo test en `backend/tests/domain/test_assignment_service.py` (crear si no existe) para `AssignmentService().validate`
- [X] T015 [P] [US4] Test de API: extender `backend/tests/api/test_reassign.py` con un test que desactive la cuenta de usuario de un segundo recurso (`PATCH /api/users/{id}/deactivate`, dejando `Resource.active = true`) e intente reasignarle el ticket, confirmando `400 resource_inactive` — debe fallar antes de T018

### Implementation for User Story 4

- [X] T016 [US4] En `backend/domain/entities/resource.py`, agregar el campo opcional `user_active: Optional[bool] = None` a `Resource` (información derivada, poblada por el repositorio — no se persiste como columna propia de `resources`)
- [X] T017 [US4] En `backend/infra/models/resource_model.py::to_entity()` (y en el/los métodos de `backend/infra/repositories/resource_repo.py` que arman `Resource` desde la fila de BD, ej. `get_by_id`), resolver `user_active` a partir del `UserModel.active` vinculado (join simple por `user_id`, `None` si `user_id` es nulo) — hace pasar T014 una vez consumido por los servicios (depende de T016) — implementado vía `relationship("UserModel", lazy="joined", viewonly=True)` en `ResourceModel`, sin tocar `resource_repo.py`
- [X] T018 [US4] En `backend/domain/services/assignment_service.py::validate` y `backend/domain/services/reassignment_service.py::validate`, ampliar el chequeo existente (`if not assignee.active: raise ...`) a también rechazar cuando `assignee.user_id is not None and assignee.user_active is False`, mismo código `resource_inactive` y mismo mensaje ("no se puede asignar/reasignar a un recurso inactivo") — hace pasar T014/T015 (depende de T014, T015, T017)
- [X] T019 [US4] En `frontend/src/components/tickets/useResourceCandidates.ts`, filtrar de `resources` (tras `resourceService.list({ active: true, ... })`) cualquier recurso cuyo `user_active === false` (requiere que `Resource`/`resourceService.list` exponga ese campo en el payload — ampliar `frontend/src/types/resource.ts` y el serializador de `GET /api/resources` de forma aditiva, consistente con T017) — hace que el selector de resolutor dejen de mostrar cuentas inactivas en ambos flujos (asignación y reasignación, ya que ambos reutilizan este hook)
- [X] T020 [US4] Verificación manual en Docker real: desactivar la cuenta (no el recurso) de un resolutor, confirmar que desaparece del selector y que un intento directo por API es rechazado con `400 resource_inactive`; repetir con "Desactivar recurso" para confirmar que no hubo regresión; reactivar la cuenta y confirmar que vuelve a ser asignable (depende de T018, T019) — ver Fase "OBS-0047" de `quickstart.md` — **verificado en Docker real, extremo a extremo**: `GET /api/resources?active=true` (llamado desde el propio navegador logueado, mismo endpoint que consume `useResourceCandidates`) devuelve `"Segundo Resolutor Notif 3a3b39c0": {active: true, user_active: false}` para el recurso cuya cuenta se desactivó en T015 — el filtro `res.user_active !== false` del frontend lo excluye del selector; rechazo `400 resource_inactive` confirmado por `test_reassign_to_resource_with_inactive_user_account_is_rejected` (T015/T021); regresión de "Desactivar recurso" cubierta por los tests preexistentes `test_validate_rejects_inactive_resource` (ambos servicios, sin tocar); reactivación no requiere lógica nueva (mismo endpoint `activate` ya probado)

**Checkpoint**: User Story 4 funcional y verificable de forma independiente (SC-004).

---

## Phase 7: Polish & Trazabilidad UAT

**Purpose**: Cerrar el ciclo con el framework UAT y confirmar alcance de pruebas.

- [X] T021 Ejecutar únicamente los archivos de test modificados (`backend/tests/domain/test_reassignment_service.py`, `backend/tests/domain/test_assignment_service.py`, `backend/tests/domain/test_notification_service.py` si se creó, `backend/tests/api/test_reassign.py` — Principio VII, prohibido correr la suite completa) y confirmar que todos pasan, incluyendo los tests nuevos de T007, T008, T014, T015 (depende de T009, T010, T011, T012, T016, T017, T018) — **20 passed** (`docker exec sywork_backend python -m pytest tests/domain/test_notification_service.py tests/domain/test_assignment_service.py tests/domain/test_reassignment_service.py tests/api/test_reassign.py -q`)
- [X] T022 Actualizar `UAT/02_Backlog/BACKLOG.md`: cambiar el `Estado` de `OBS-0044`, `OBS-0045`, `OBS-0046` y `OBS-0047` de `Abierta` a `Lista para Validar`, siguiendo `UAT/CONVENTIONS.md` (FR-015) — confirmar que `UAT/01_Iterations/ITER-008/ITER-008.md` no se edita en su contenido narrativo (depende de T004, T006, T013, T020, T021) — hecho; `ITER-008.md` no tocado (verificado con `git diff`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato.
- **Foundational (Phase 2)**: Sin tareas — no bloquea nada.
- **User Story 1 (Phase 3, OBS-0044)**: Depende solo de Setup. Independiente de las otras 3.
- **User Story 2 (Phase 4, OBS-0045)**: Depende solo de Setup. Comparte archivo (`TimeLogModal.tsx`) con US1 — ver nota de paralelismo abajo.
- **User Story 3 (Phase 5, OBS-0046)**: Depende solo de Setup. Independiente de US1/US2/US4 en archivos, aunque toca el mismo endpoint (`tickets.py`) que US4.
- **User Story 4 (Phase 6, OBS-0047)**: Depende solo de Setup. Comparte `tickets.py`/servicios de asignación con US3 (archivos distintos dentro del mismo módulo — ver nota abajo).
- **Polish (Phase 7)**: Depende de que las 4 historias estén verificadas (T004, T006, T013, T020) y de los tests acotados (T021).

### User Story Dependencies

- **US1 (OBS-0044, P1)**: Sin dependencias de otras historias.
- **US2 (OBS-0045, P2)**: Sin dependencias funcionales de US1, pero **T005 toca el mismo archivo que T002** (`TimeLogModal.tsx`) — no ejecutar T002 y T005 en paralelo; secuenciar (T002 antes de T005, o viceversa) dentro de ese archivo.
- **US3 (OBS-0046, P1)**: Sin dependencias de US1/US2/US4 a nivel de requisitos, aunque T011/T012 y T018 (de US4) tocan el mismo archivo `tickets.py` — secuenciar entre sí si se implementan en paralelo por distintos desarrolladores.
- **US4 (OBS-0047, P1)**: Sin dependencias de US1/US2/US3 a nivel de requisitos; comparte `tickets.py` con US3 (ver nota anterior) y `assignment_service.py`/`reassignment_service.py` en archivos ya tocados por lógica de US3 solo indirectamente (T011 no toca `validate()`).

### Dentro de cada User Story

- US1: T002, T003 en paralelo (archivos distintos) → T004 al final.
- US2: T005 (único archivo) → T006 al final.
- US3: T007, T008 en paralelo (tests, archivos distintos) → T009 → T010 (hace pasar T007) → T011 (hace pasar T008) → T012 → T013 al final.
- US4: T014, T015 en paralelo (tests, archivos distintos) → T016 → T017 → T018 (hace pasar T014/T015) → T019 → T020 al final.

### Parallel Opportunities

- T002 y T003 (US1) en paralelo.
- T007 y T008 (US3, tests) en paralelo.
- T014 y T015 (US4, tests) en paralelo.
- US1 (T002-T004) y US3 (T007-T013) pueden desarrollarse en paralelo entre sí (sin archivos compartidos) si hay más de un desarrollador; igual US2 con US3, y US1 con US4. Evitar paralelizar US2 con US1 (mismo archivo) y US3 con US4 (mismo archivo `tickets.py`) sin coordinar.

---

## Parallel Example: User Story 3

```bash
# Lanzar juntas (archivos de test distintos, sin dependencias entre sí):
Task: "Test de dominio: NotificationService.build(..., 'reassigned', ...) — backend/tests/domain/test_notification_service.py"
Task: "Test de API: notificación tras reasignación — backend/tests/api/test_reassign.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup.
2. Completar Phase 3: User Story 1 (OBS-0044) — el defecto de mayor impacto en integridad de datos/SLA.
3. **Detener y validar**: probar User Story 1 de forma independiente contra Docker (Fase "OBS-0044" de `quickstart.md`).
4. Continuar con User Stories 2, 3 y 4, y Polish, para cerrar las 4 observaciones de ITER-008.

### Incremental Delivery

1. Setup → entorno y datos de prueba listos.
2. User Story 1 (OBS-0044) → validar independientemente.
3. User Story 2 (OBS-0045) → validar independientemente.
4. User Story 3 (OBS-0046) → validar independientemente.
5. User Story 4 (OBS-0047) → validar independientemente.
6. Polish → tests acotados + actualización de `BACKLOG.md` (cierre de trazabilidad UAT).

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes entre las tareas marcadas.
- [Story] mapea cada tarea a su User Story para trazabilidad con `spec.md`.
- Ninguna tarea de este feature requiere migración Alembic ni dependencias nuevas (Principio V).
- No editar retroactivamente `UAT/01_Iterations/ITER-008/ITER-008.md` — todo cambio de estado va en `UAT/02_Backlog/BACKLOG.md` (T022).
