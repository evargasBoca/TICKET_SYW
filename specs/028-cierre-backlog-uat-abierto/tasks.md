---

description: "Task list template for feature implementation"
---

# Tasks: Cierre de observaciones "Abierta" del Backlog UAT (SLA, Tickets, Calendario)

**Input**: Design documents from `/specs/028-cierre-backlog-uat-abierto/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/api-changes.md](./contracts/api-changes.md), [quickstart.md](./quickstart.md)

**Tests**: Se incluyen tareas de test de dominio backend (pytest), ultra-limitadas por archivo modificado (Constitución Principio VII — prohibido correr la suite completa; máximo 5-10 registros de prueba por test). No hay framework de test de frontend configurado en este repo (`frontend/package.json` no tiene `vitest`/`@testing-library`); la verificación de frontend es manual contra Docker, vía `quickstart.md`.

**Organization**: Tareas agrupadas por User Story (spec.md) para permitir implementación y prueba independiente de cada una.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: A qué User Story pertenece (US1..US6)
- Cada tarea incluye ruta de archivo exacta

## Path Conventions

Web app existente: `backend/` (Flask, 3 capas: `domain/`, `infra/`, `api/`) + `frontend/src/` (React). Ver "Project Structure" en `plan.md`.

---

## Phase 1: Setup

**Purpose**: Confirmar el entorno antes de tocar código.

- [X] T001 Levantar el stack Docker de desarrollo y confirmar que existe (o crear) un recurso de prueba con `WorkHourTemplate`/calendario asignado con horario laboral acotado y timezone distinto de UTC, y una regla de SLA configurada — ver "Prerrequisitos" en [quickstart.md](./quickstart.md) — **Docker levantado (`sywork_db`/`backend`/`frontend`/`worker`/`redis` Up)**; `work_hour_templates` está vacío en este entorno (sin seed) — la creación del recurso de prueba con timezone no-UTC queda pendiente para la verificación manual de `quickstart.md`, no bloquea el desarrollo (T003/T004 usan fixtures en memoria vía pytest, sin depender de datos sembrados)

**Checkpoint**: Entorno listo para desarrollar y verificar manualmente cada historia.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Único prerequisito compartido por más de una historia — evita duplicar la resolución del contexto de calendario del recurso en dos lugares (US1 y US6).

**⚠️ CRITICAL**: T002 bloquea T005, T006 (US1) y T026, T027 (US6).

- [X] T002 Extraer/confirmar un helper único y reutilizable que resuelva el contexto de calendario de un recurso en un instante dado (timezone, franjas de horario laboral, feriados, ausencias) en `backend/domain/services/sla_service.py` (o un módulo nuevo `backend/domain/services/calendar_context.py` si no encaja limpio ahí), reusando la lógica ya existente de `compute_available_seconds` (L112-141) en vez de duplicarla — ver `research.md` §1 y §6 — **hallazgo de implementación: el helper ya existía** como `_resolve_sla_context(db, ticket)` en `backend/api/routes/tickets.py` (L391-406) y su duplicado en `backend/workers/sla_tasks.py` (L37-50); no se creó código nuevo, T005/T026/T027 reusan el existente tal cual (ver `research.md` actualizado)

**Checkpoint**: Foundation lista — las historias pueden empezar (en paralelo si hay más de un desarrollador).

---

## Phase 3: User Story 1 - El SLA solo contabiliza tiempo laboral real (Priority: P1) 🎯 MVP

**Goal**: El SLA de un ticket refleja únicamente el tiempo laboral real transcurrido, sin importar cuándo se crea o cambia de estado, y expone los timestamps relevantes (creación, asignación, inicio efectivo de SLA, inicio de jornada).

**Independent Test**: Crear/asignar/cambiar de estado un ticket dentro y fuera de horario laboral y verificar que el SLA mostrado coincide con el tiempo laboral real transcurrido en cada caso (ver Fase "US1" de `quickstart.md`).

### Tests for User Story 1

- [X] T003 [P] [US1] Test de dominio: el tiempo consumido de SLA tras un cambio de estado excluye tiempo fuera de horario y tiempo pausado, en `backend/tests/domain/test_sla_service.py` (extender, ultra-limitado) — agregados `test_transition_with_resource_consumes_calendar_time_not_wall_clock` y `test_transition_without_resource_keeps_wall_clock_fallback` (reproduce OBS-0038: mié 16:00→jue 09:05 = 7500s reales vs. 61500s de wall-clock)
- [X] T004 [P] [US1] Test de dominio: un ticket creado fuera de horario laboral no inicia el conteo de SLA hasta el siguiente período laboral, en `backend/tests/domain/test_sla_service.py` (junto a T003, mismo archivo — no se usó `test_sla_dynamic_availability.py` para no fragmentar fixtures) — agregados `test_next_work_period_start_delays_ticket_created_outside_hours`, `test_next_work_period_start_within_hours_returns_same_instant`, `test_next_work_period_start_without_resource_returns_input_unchanged`

### Implementation for User Story 1

- [X] T005 [P] [US1] Auditar y corregir todos los call-sites de `sla_service.compute_consumed_seconds`/`compute_state`/`apply_transition` en `backend/api/routes/tickets.py` para que siempre resuelvan y pasen el contexto de calendario del recurso asignado (usando el helper de T002) (depende de T002) — **causa raíz exacta**: `apply_transition` (`sla_service.py`) nunca tuvo parámetros `resource`/`holidays`/`schedule_slots`/`absences` a diferencia de `compute_state`/`is_breach`; se agregaron y se hilvanaron a su `compute_consumed_seconds` interno. Su único call-site, `_sla_updates_for_transition` (`tickets.py` L564-566), ahora pasa `**_resolve_sla_context(db, ticket)`. Además, en `TicketAssign.post` (OBS-0039) se detectó que en la primera asignación `ticket.assignee_id` aún no estaba seteado en memoria cuando se resolvía el contexto de SLA — se agregó `ticket.assignee_id = assignee_id` antes de `_sla_updates_for_transition` (L1030-1034)
- [X] T006 [P] [US1] Aplicar la misma corrección en `backend/workers/sla_tasks.py::check_sla_breaches` para que la detección programada de "Vencido" sea calendario-consciente (depende de T002) — **verificado: ya estaba correcto**, `check_sla_breaches` ya resolvía y pasaba el contexto de calendario a `is_breach` desde antes de este feature; no se requirió ningún cambio
- [X] T007 [US1] Exponer `created_at`, `assigned_at` (desde `AssignmentModel`), `sla_effective_start` (= `sla_last_resume_at`) y `work_period_start` (derivado) en la respuesta de `GET /api/tickets/{id}` en `backend/api/routes/tickets.py` — ver `contracts/api-changes.md` (depende de T005) — `created_at`/`assignments` (con `assigned_at`) ya viajaban en el payload; se agregó `next_work_period_start()` nuevo en `sla_service.py` y el helper `_sla_timestamps()` en `tickets.py`, aplicado solo en `_ticket_detail` (no en listados, por costo) — expuesto además en el modelo Swagger `TicketDetail`
- [X] T008 [US1] Ubicar el componente de detalle de ticket que muestra el SLA (bajo `frontend/src/pages/` o `frontend/src/components/tickets/`) y agregar la visualización de los 4 timestamps de T007 (depende de T007) — el SLA vive en `frontend/src/components/tickets/SlaCounter.tsx` (usado desde `TicketDetailPage.tsx`); los 4 timestamps se agregaron como `Descriptions.Item` en el panel "Clasificación" de `TicketDetailPage.tsx` (Creado/Asignado/Inicio de jornada laboral/Inicio efectivo del SLA), con los 2 campos nuevos tipados en `TicketDetail` (`types/ticket.ts`) — **verificado en Docker real** (TK-000004): los 4 campos aparecen en la UI y en la respuesta `GET /api/tickets/{id}` (`sla_effective_start`, `work_period_start`), sin errores de consola

**Checkpoint**: User Story 1 funcional y verificable de forma independiente (SC-001, SC-002).

---

## Phase 4: User Story 2 - Un ticket cerrado no admite nuevos registros de tiempo (Priority: P1)

**Goal**: Cerrar un ticket detiene automáticamente cualquier cronómetro activo y bloquea nuevos registros de tiempo sobre él, sin afectar otros tickets/tareas del mismo recurso.

**Independent Test**: Iniciar un cronómetro, cerrar el ticket sin detenerlo manualmente, y verificar que se detiene solo, que no admite nuevos registros, y que otros tickets del recurso no se ven afectados (ver Fase "US2" de `quickstart.md`).

### Tests for User Story 2

- [X] T009 [P] [US2] Test de API: iniciar un timer sobre un ticket en estado `cerrado` devuelve `409 ticket_closed`, en `backend/tests/api/test_timer.py` (extender, ultra-limitado) — agregados `test_start_rejects_already_closed_ticket` y `test_closing_ticket_auto_stops_active_timer_and_persists_time` (end-to-end: iniciar → cerrar ticket → verificar timer inactivo + WorkSession auto-creada + nuevo start bloqueado)

### Implementation for User Story 2

- [X] T010 [US2] Mover/agregar el chequeo `assert_ticket_open_or_admin` (hoy solo en `WorkSessionService.create`) también a `TicketTimerService.start()` en `backend/domain/services/ticket_timer_service.py`
- [X] T011 [US2] Agregar efecto lateral en la transición de FSM a `cerrado`: detectar un `TicketTimer` activo del recurso sobre ese ticket y detenerlo automáticamente, persistiendo el tiempo acumulado vía `WorkSessionService.create()` — en `backend/api/routes/tickets.py` (ruta `PATCH .../status`) o `backend/domain/services/ticket_service.py`, el que orqueste la transición (depende de T010) — **hallazgo de implementación**: no hay una única transición FSM genérica a `cerrado` para Tickets — el único camino es el endpoint `TicketClose.post` (`/tickets/{id}/close`, cierre con tipo de resolución); las Tareas/Subtareas cierran por un segundo camino, `TicketStatusChange.patch` (`/tickets/{id}/status`, transición libre spec 009). Se agregó `TicketTimerService.stop_if_active_for_ticket()` (nuevo método, reutiliza `finish()`; descarta silenciosamente si el acumulado es < 60s, nunca bloquea el cierre) y el helper `_stop_timer_on_close()` en `tickets.py`, invocado en AMBOS endpoints — antes de persistir `status="cerrado"` y antes del chequeo `no_time_registered` (OBS-0026), para que el tiempo recién detenido cuente
- [X] T012 [P] [US2] Deshabilitar el botón "Iniciar" y mostrar el mensaje de ticket cerrado en `frontend/src/components/worksessions/TicketTimerWidget.tsx` cuando `ticket.status === 'cerrado'` — se agregó el prop `ticketStatus` (pasado desde `TicketDetailPage.tsx` como `ticket.status`), botón `disabled` + `Tooltip`, y un `Alert` informativo — **verificado en Docker real** (TK-000017, ticket ya cerrado): alert visible, botón con `disabled: true` confirmado vía inspección del DOM, sin errores de consola

**Checkpoint**: User Stories 1 y 2 funcionan de forma independiente (SC-003).

---

## Phase 5: User Story 3 - El título del ticket se valida antes de guardarse (Priority: P2)

**Goal**: El sistema rechaza títulos vacíos/solo-espacios y títulos con emojis al crear un ticket.

**Independent Test**: Intentar crear tickets con título vacío/solo espacios y con emojis, y verificar el rechazo con mensaje explícito en cada caso (ver Fase "US3" de `quickstart.md`).

### Tests for User Story 3

- [X] T013 [P] [US3] Test de dominio: `TicketService.validate_create` rechaza título solo-espacios y título con emoji; acepta letras con tilde/ñ, números y puntuación común, en `backend/tests/domain/test_ticket_service_client_contact.py` o un archivo nuevo `backend/tests/domain/test_ticket_service_title_validation.py` (ultra-limitado) — implementado como tests de API en `backend/tests/api/test_tickets_title_validation.py` (nuevo, 6 tests: crear con solo-espacios/emoji/válido+trim, y editar con solo-espacios/emoji), para cubrir también el contrato HTTP (`title_blank`/`title_invalid_chars`) además de la regla de dominio

### Implementation for User Story 3

- [X] T014 [US3] Agregar validación de título (recorte + rechazo si queda vacío; rechazo por rango Unicode de emoji, sin agregar dependencias — ver `research.md` §3) a `TicketService.validate_create` en `backend/domain/services/ticket_service.py` — implementado como método nuevo `TicketService.validate_title()` (reutilizable desde creación y edición) en vez de inline en `validate_create`, y también conectado a `validate_patch` (el título es un campo editable — sin este segundo enganche, la validación se podía sortear editando)
- [X] T015 [US3] Reemplazar la comprobación superficial `_missing("title")` en `backend/api/routes/tickets.py` (`TicketList.post`) por la validación de T014, devolviendo `title_blank`/`title_invalid_chars` (depende de T014)
- [X] T016 [P] [US3] Agregar `whitespace: true` y un validador que rechace emojis a la regla del `Form.Item name="title"` en `frontend/src/pages/TicketsPage.tsx` (modal "Nuevo ticket", L396-402) — agregada constante `TITLE_RULES` + `EMOJI_PATTERN` (mismos rangos Unicode que el backend) y 2 reglas nuevas en `TICKET_ERROR_RULES` (`title_blank`/`title_invalid_chars` → campo `title`, patrón OBS-0018) — **verificado en Docker real**: emoji y solo-espacios rechazados inline bajo el campo, sin errores de consola

**Checkpoint**: User Stories 1-3 funcionan de forma independiente (SC-004).

---

## Phase 6: User Story 4 - Retroalimentación clara al configurar reglas de SLA (Priority: P2)

**Goal**: Confirmar/corregir el aviso de guardado exitoso y agregar validación explícita de mínimo y máximo (15 días / 21600 min) en los campos de tiempo del SLA.

**Independent Test**: Guardar una configuración de SLA válida y verificar el aviso de éxito; intentar guardar valores en 0/negativos y por encima de 21600 minutos y verificar el mensaje de validación en cada caso (ver Fase "US4" de `quickstart.md`).

### Implementation for User Story 4

- [X] T017 [P] [US4] Agregar la constante `SLA_FIELD_MAX_MINUTES = 21600` (15 días, confirmado con el usuario — OBS-0031) a `backend/domain/entities/sla_rule.py` — replicada también en `frontend/src/types/sla.ts` (mismo valor, comentario cruzado)
- [X] T018 [US4] Actualizar `_validate_minutes` en `backend/api/routes/sla_rules.py` (L68-75) para exigir mínimo 1 con mensaje explícito (no solo `> 0`) y máximo `SLA_FIELD_MAX_MINUTES`, devolviendo `max_exceeded` cuando corresponda (depende de T017)
- [X] T019 [P] [US4] Reemplazar la dependencia del clamp silencioso de `InputNumber` por una regla de validación explícita (`validator`) de mínimo(1)/máximo(21600) en `frontend/src/components/sla/SlaRuleForm.tsx` (L114-136), con mensajes equivalentes a los del backend — se quitaron los props `min`/`max` de ambos `InputNumber` (incluido el interno de `ExecutionTimeInput`, que tenía `min={0}`) y se agregaron reglas `type:'number', min/max` explícitas en los dos `Form.Item`
- [X] T020 [P] [US4] Verificar en Docker si el `message.success(...)` ya existente en `frontend/src/pages/SlaRulesPage.tsx` (L79-82) realmente se muestra al guardar; si no, corregir la integración del contexto `message`/`App` de Ant Design v5 — ver `research.md` §4 — **confirmado con Docker real que NO se mostraba**: causa raíz identificada por consola (`Warning: [antd: message] Static function can not consume context...`, agravado por `antd v5 support React is 16~18` — esta app corre React 19). Verificado con un `MutationObserver` sobre `document.body` antes/después del fix: sin el fix, cero nodos `.ant-message` tras una acción exitosa confirmada por API; con el fix, el nodo aparece con el texto correcto ("Regla desactivada"). Fix: `SlaRulesPage.tsx` ahora usa `const { message } = App.useApp()` (mismo patrón que `MessageApiBinder` en `App.tsx`) en vez de la función estática `import { message } from 'antd'`

**Checkpoint**: User Stories 1-4 funcionan de forma independiente (SC-005).

---

## Phase 7: User Story 5 - Visibilidad del SLA inicial y de la disponibilidad del recurso (Priority: P3)

**Goal**: El detalle de ticket muestra claramente cuándo el SLA aún no inició, y el calendario de un recurso interno muestra su jornada laboral/ausencias, no solo su cumpleaños.

**Independent Test**: Ver el estado visual del SLA en un ticket recién creado antes de que inicie el conteo; abrir el calendario de un recurso interno y verificar que expone jornada laboral, feriados y ausencias (ver Fase "US5" de `quickstart.md`).

### Implementation for User Story 5

- [X] T021 [US5] Ubicar el componente que renderiza el estado del SLA en el detalle del ticket (bajo `frontend/src/components/tickets/` o `frontend/src/pages/`) y agregar un estado visualmente diferenciado ("Pendiente de asignación"/"Esperando inicio de SLA") cuando `sla_status`/`sla_phase` indican que el conteo aún no inició — es `frontend/src/components/tickets/SlaCounter.tsx` (identificado durante US1). **Hallazgo**: la fase "Contacto" ya cuenta wall-clock desde la creación por diseño de dominio (`sla_service.initial_state`) — no hay un estado "sin iniciar" a nivel de dominio que replicar. El fix es puramente presentacional: nuevo prop `hasAssignee` (derivado de `ticket.assignee != null`, sin cambios de backend); cuando `!hasAssignee && phase==='contacto' && status==='corriendo'`, se muestra "Pendiente de asignación" (gris) en vez de "Corriendo" (verde), con tooltip explicativo
- [X] T022 [P] [US5] En `frontend/src/pages/CalendarPage.tsx`, dentro de `TeamOverlayCalendar` (L106-149), agregar llamadas a `calendarService.getWorkSchedule(resourceId)` y `calendarService.listAbsenceRequests(scope)` por cada recurso seleccionado, y renderizar el resultado como eventos/franjas separados visualmente de los eventos personales (cumpleaños) — **hallazgo de implementación**: `listAbsenceRequests(scope)` no sirve para este caso — sus 3 scopes (`own`/`manager`/`hr`) son relativos al usuario autenticado, no aceptan un `resource_id` arbitrario, así que el calendario de Equipo (que permite seleccionar cualquier recurso, no solo subordinados) no podía consultarlas. Se extendió `GET /api/absence-requests` con un parámetro `resource_id` nuevo (gateado por el mismo permiso que `scope=hr`, `absence_requests:view_all` — solo rol RRHH) y se agregó `calendarService.listAbsenceRequestsForResource()` (con `skipErrorNotify`, ya que un 403 es el resultado esperado para la mayoría de los roles que sí pueden ver este calendario, ej. Coordinador). `getWorkSchedule` no tuvo este problema (ya gateado de forma amplia por `enforce_module("resources")`, igual que el resto de esta pantalla) — se agregó `formatWorkSchedule()` para mostrarlo como texto compacto ("Lun-Vie 08:00-17:00") junto al calendario, y las ausencias aprobadas como eventos de rango (color `CALENDAR_CATEGORY_COLORS.ausencia`, nuevo). Cuando el usuario no tiene el permiso, se muestra una nota explicativa en vez de fallar — **verificado en Docker real** con ~68 recursos seleccionados simultáneamente: 403 manejado sin toasts de error ni crashes, horarios laborales y nota de RRHH visibles correctamente
- [X] T023 [P] [US5] Verificar manualmente (sin cambio de código esperado) que la disponibilidad que consume el Panel de Asignación (spec 024, `calendarService.getAvailability`) no se ve afectada por los cambios de T022 — confirmado por inspección (T022 no tocó `getAvailability` ni el endpoint `/api/resources/availability`, solo agregó una rama nueva y aislada en `AbsenceRequestList.get`) y verificado en Docker real: `/assignment-panel` carga y funciona con normalidad

**Checkpoint**: User Stories 1-5 funcionan de forma independiente (SC-006).

---

## Phase 8: User Story 6 - Regla de negocio para registrar tiempo fuera de horario laboral (Priority: P2)

**Goal**: Registrar tiempo fuera del horario laboral configurado se permite y queda clasificado como "tiempo fuera de jornada"; la fecha del registro refleja la fecha local real del recurso, no la fecha del servidor.

**Independent Test**: Registrar tiempo fuera de horario laboral con un recurso en timezone no-UTC y verificar que se guarda, queda clasificado como fuera de jornada, y la fecha corresponde a la fecha local real (ver Fase "US6" de `quickstart.md`).

### Implementation for User Story 6

- [X] T024 [US6] Agregar el campo `off_hours: bool = False` a `WorkSession` en `backend/domain/entities/work_session.py` y la columna correspondiente al modelo ORM en `backend/infra/models/work_session_model.py` — hecho tal cual (dataclass field + `Column(Boolean, server_default=text("false"))` + `to_entity`/`from_entity`)
- [X] T025 [US6] Crear la migración Alembic que agrega `off_hours BOOLEAN NOT NULL DEFAULT false` a `work_sessions` en `backend/infra/migrations/versions/` (depende de T024) — `046_work_sessions_off_hours.py` (down_revision 045, head confirmado sin otras revisiones colgando de 045); aplicada con `alembic upgrade head` contra el Postgres real de Docker sin errores
- [X] T026 [US6] Corregir el cálculo de `work_date` en `backend/domain/services/ticket_timer_service.py` (L99, reemplazar `date.today()` del servidor) para usar la fecha local del recurso vía el helper de T002 (depende de T002) — **hallazgo de implementación**: el helper de T002 (`_resolve_sla_context`) vive en la capa de rutas (usa `db`/repos), no es invocable desde el dominio; se agregó `sla_service.resource_local_now(resource, now)` (wrapper público del `_local_time_at` ya privado de sla_service) y se cambió la firma de `finish()`/`stop_if_active_for_ticket()` para recibir un `calendar_context: dict | None` opcional (mismo shape `{resource, holidays, schedule_slots, absences}` que `_resolve_sla_context`), resuelto por el llamador (`timer.py`, `tickets.py::_stop_timer_on_close`) y forwardeado tal cual a `WorkSessionService.create()`. Sin contexto (fallback), se preserva el comportamiento previo (`now.date()` UTC) — nunca rompe callers no migrados
- [X] T027 [US6] Calcular y persistir `off_hours` en `WorkSessionService.create()` (`backend/domain/services/work_session_service.py`), comparando el intervalo `[started_at, ended_at]`/`work_date` contra el horario laboral del recurso vía el helper de T002 (depende de T002, T024) — nueva función `sla_service.is_off_hours()` (reusa `compute_available_seconds`/`_day_available_intervals`, sin duplicar lógica); `create()` acepta `resource`/`holidays`/`schedule_slots`/`absences` opcionales (default `None` → `off_hours=False`, no rompe callers existentes). Wireado en las 3 rutas que llaman `create()`/`finish()`: `work_sessions.py` (alta manual), `timer.py` (`/finish`) y `tickets.py::_stop_timer_on_close` (auto-stop al cerrar, US2) — cada una con su propio `_resolve_calendar_context(db, resource)` (mismo criterio que `_resolve_sla_context`, pero keyed por `resource` en vez del `assignee_id` del ticket, porque quien registra el tiempo no siempre es el asignado)
- [X] T028 [P] [US6] Agregar `off_hours` al tipo `WorkSession` en `frontend/src/types/` y mostrarlo como etiqueta/badge en la vista de Reporte de Tiempos / registro de tiempos del ticket (depende de T024, T027) — `types/workSession.ts` (`WorkSessionListItem.off_hours`), badge `Tag color="warning"` "Fuera de jornada" en la columna Fecha de `WorkSessionsPage.tsx` (Reporte de Tiempos) y `TimeLogModal.tsx` (registro de tiempo del ticket)
- [X] T029 [P] [US6] Tests de dominio ultra-limitados (≤5 fixtures) para: (a) `work_date` refleja la fecha local del recurso cerca de medianoche, y (b) clasificación correcta de `off_hours`, en `backend/tests/domain/test_work_session_service_create.py` (extender) (depende de T026, T027) — 3 tests nuevos (`test_work_date_reflects_resource_local_date_near_midnight`, `test_create_marks_off_hours_true_when_full_day_unavailable`, `test_create_marks_off_hours_false_when_within_schedule`); 38/38 passed junto con `test_sla_service.py`, más 29/29 en los tests de API de `timer`/`work_sessions` ya existentes (sin regresión)

**Checkpoint**: Las 6 User Stories funcionan de forma independiente. Backlog listo para cerrar (SC-005, SC-007).

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Verificación final y cierre del ciclo UAT.

- [X] T030 [P] Ejecutar únicamente los tests de dominio/API modificados por esta feature (`test_sla_service.py`, `test_sla_dynamic_availability.py`, el test de título de US3, `test_timer.py`, `test_work_session_service_create.py`) — **prohibido correr la suite completa** (Constitución Principio VII) — ampliado a los 10 archivos de test tocados en toda la feature (incluye `test_sla_rules.py` US4, `test_absence_requests_resource_scope.py` US5, `test_work_sessions_*` US6): **95/95 passed**, cero regresiones
- [X] T031 [P] Confirmar que el Swagger/OpenAPI auto-generado (Flask-RESTX) refleja los nuevos casos de error documentados en `contracts/api-changes.md` (`title_blank`, `title_invalid_chars`, `ticket_closed` en start, `max_exceeded`) — **hallazgo**: `title_blank`/`title_invalid_chars` (POST y PATCH /api/tickets), `ticket_closed` en `POST /api/timer/start` y `max_exceeded` (POST y PATCH /api/sla-rules) no estaban documentados en los `@ns.response(400/409, ...)` existentes (documentaban el caso genérico pero no el código específico); agregados los 4 casos a sus decoradores y verificado contra `/swagger.json` real del backend (los 7 checks — 2 rutas × título, 1 timer, 2 rutas × sla_rules — confirman el código en la descripción de alguna respuesta)
- [X] T032 Ejecutar de punta a punta los 6 escenarios de `quickstart.md` contra Docker real, registrando el resultado de cada uno — 6/6 PASS, resultados y evidencia documentados en la nueva sección "Resultados de ejecución (T032, 2026-07-24)" de `quickstart.md`; datos de prueba creados durante la corrida (tickets, regla de SLA, timezone temporal en un recurso) revertidos al finalizar
- [X] T033 Actualizar `UAT/02_Backlog/BACKLOG.md`: cambiar el `Estado` de `OBS-0029` a `OBS-0040` de `Abierta` a `Lista para Validar` (FR-022) — **no editar** `UAT/01_Iterations/ITER-004/ITER-004.md` ni `ITER-005/ITER-005.md` — hecho tal cual, las 12 filas actualizadas, `ITER-004.md`/`ITER-005.md` no tocados (confirmado con `git status`)

**Checkpoint**: Feature lista para retest del validador UAT (SC-007).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias — puede iniciar de inmediato
- **Foundational (Phase 2)**: depende de Setup — **bloquea** T005, T006 (US1) y T026, T027 (US6)
- **User Stories (Phase 3-8)**: US1 y US6 dependen de T002 (Foundational); US2, US3, US4, US5 no dependen de Foundational y pueden avanzar en paralelo con US1/US6 en cuanto termina Setup
- **Polish (Phase 9)**: depende de que las historias que se vayan a entregar estén completas

### User Story Dependencies

- **US1 (P1)**: depende de T002 (Foundational). Sin dependencia de otras historias.
- **US2 (P1)**: sin dependencia de Foundational ni de otras historias.
- **US3 (P2)**: sin dependencia de Foundational ni de otras historias.
- **US4 (P2)**: sin dependencia de Foundational ni de otras historias.
- **US5 (P3)**: sin dependencia de Foundational ni de otras historias. T021 se beneficia de que T007 (US1) ya exponga `sla_status`/`sla_phase`, pero no es bloqueante (esos campos ya existen hoy en el dominio).
- **US6 (P2)**: depende de T002 (Foundational).

### Parallel Opportunities

- T005 y T006 (US1) en paralelo tras T002 (archivos distintos)
- T012 (US2) en paralelo con T010/T011 (frontend vs. backend)
- T016 (US3) en paralelo con T014/T015 (frontend vs. backend)
- T017, T019, T020 (US4) en paralelo entre sí (archivos distintos)
- T022, T023 (US5) en paralelo con T021 (archivos distintos)
- T028, T029 (US6) en paralelo entre sí una vez completos T024-T027
- Una vez cerrado Foundational, **US2, US3, US4 y US5 pueden avanzar en paralelo con US1 y US6** por distintos desarrolladores, ya que no comparten archivos

---

## Parallel Example: User Story 1

```bash
# Tras completar T002 (Foundational), lanzar en paralelo:
Task: "Auditar y corregir call-sites de sla_service en backend/api/routes/tickets.py"
Task: "Corregir check_sla_breaches en backend/workers/sla_tasks.py"
```

## Parallel Example: User Story 6

```bash
# Tras completar T024-T027, lanzar en paralelo:
Task: "Agregar off_hours al tipo WorkSession y a la UI de reporte de tiempos"
Task: "Tests de dominio para work_date local y clasificación off_hours"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (bloquea US1 y US6)
3. Completar Phase 3 (US1) y Phase 4 (US2) — ambas P1, mayor impacto de negocio (exactitud de SLA e integridad del registro de tiempo en tickets cerrados)
4. **Detener y validar**: correr las secciones US1/US2 de `quickstart.md` de forma independiente
5. Continuar con US3-US6 en orden de prioridad (P2 antes que P3)

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 → validar independientemente (SC-001, SC-002)
3. US2 → validar independientemente (SC-003)
4. US3 → validar independientemente (SC-004)
5. US4 → validar independientemente (SC-005, parcial — min/max)
6. US6 → validar independientemente (SC-005, parcial — clasificación; requiere T002)
7. US5 → validar independientemente (SC-006)
8. Polish (Phase 9) → `BACKLOG.md` actualizado, feature lista para retest UAT (SC-007)

### Parallel Team Strategy

Con más de un desarrollador, tras Setup + Foundational:
- Desarrollador A: US1 (depende de T002) → luego US5 (T021, se beneficia de US1)
- Desarrollador B: US2, luego US3
- Desarrollador C: US4, luego US6 (depende de T002)

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes entre sí
- Cada historia es completable y verificable de forma independiente vía su sección en `quickstart.md`
- Commitear después de cada tarea o grupo lógico, siguiendo el patrón de commits atómicos ya usado en el repo
- Alcance de sesión (Constitución Principio VII): cada tarea toca únicamente los archivos indicados; prohibido refactorizar u optimizar módulos fuera del alcance de esta feature
- Evitar: tareas vagas, conflictos de archivo dentro de la misma fase, dependencias cruzadas entre historias que rompan su independencia
