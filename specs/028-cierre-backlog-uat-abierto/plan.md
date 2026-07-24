# Implementation Plan: Cierre de observaciones "Abierta" del Backlog UAT (SLA, Tickets, Calendario)

**Branch**: `028-cierre-backlog-uat-abierto` | **Date**: 2026-07-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/028-cierre-backlog-uat-abierto/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Corregir las 12 observaciones en estado `Abierta` del backlog UAT (`OBS-0029`–`OBS-0040`): el motor de SLA no siempre aplica el calendario laboral del recurso al recalcular tiempo consumido (causa raíz: `resource`/`holidays`/`schedule_slots`/`absences` es un parámetro opcional de `sla_service.compute_consumed_seconds`/`compute_state`, y algunas rutas de invocación no lo pasan); el cronómetro no se detiene ni se bloquea al cerrar un ticket en el momento de `start()` (solo falla tardíamente en `finish()`); el título del ticket no rechaza espacios en blanco ni emojis; el formulario de SLA Configurable carece de mensaje de confirmación fiable y de validación explícita de mínimo/máximo; el calendario de un recurso interno no expone su jornada laboral/ausencias (los datos ya existen vía `calendarService`, solo falta conectarlos a la vista); y el registro de tiempo fuera de horario no se clasifica ni conserva correctamente la fecha local (causa raíz: `ticket_timer_service.py` usa `date.today()` del servidor en vez de la fecha local del recurso). Todas las correcciones son ajustes acotados dentro de la arquitectura de 3 capas existente (dominio → infra → API/frontend), sin nuevas dependencias ni nuevos servicios.

## Technical Context

**Language/Version**: Python 3.12 (Flask) — backend; TypeScript 5 / React 19 — frontend (stack ya aprobado en la Constitución, sin cambios)

**Primary Dependencies**: Flask-RESTX (Swagger), SQLAlchemy + Alembic, `python-transitions` (FSM), Celery + Redis (backend); Ant Design 5, Zustand, `date-fns`, Axios (frontend) — todas ya aprobadas; **este feature no introduce dependencias nuevas** (Principio V)

**Storage**: PostgreSQL 16 — una migración Alembic nueva (columna `off_hours`/clasificación en `work_sessions`)

**Testing**: pytest para los servicios de dominio tocados (`sla_service`, `work_session_service`, `ticket_timer_service`, `ticket_service`), alcance ultra-limitado por archivo modificado (Principio VII — prohibido correr la suite completa); verificación funcional end-to-end contra Docker real, siguiendo el patrón ya usado en specs previas y documentado en `quickstart.md`

**Target Platform**: Docker Compose (entorno de desarrollo/UAT); despliegue on-premise (fuera de alcance, ver `TODO(HOSTING)` de la Constitución)

**Project Type**: Web application (backend Flask API + frontend React SPA) — estructura ya existente, Option 2 del template

**Performance Goals**: Sin metas nuevas explícitas; el recálculo de SLA calendario-consciente debe seguir siendo apto para uso síncrono en cada carga del detalle de ticket (ya es el patrón actual, `compute_state` se invoca on-read) y no debe degradar perceptiblemente el tiempo de carga del detalle de ticket ni del listado

**Constraints**: Debe reusar los literales de estado existentes (`Ticket.STATUSES`, `"cerrado"` como string — no existe un enum `TicketStatus`); no debe romper la tarea programada `check_sla_breaches` (Celery beat, cada 5 min); no debe agregar dependencias sin aprobación (Principio V); las pruebas nuevas/modificadas deben ser ultra-limitadas (Principio VII); la lógica de negocio nueva (validación de título, clasificación fuera de horario) debe vivir en Capa 1 (dominio), nunca en rutas Flask ni en componentes React (Principios I/II)

**Scale/Scope**: 12 observaciones UAT, 6 User Stories, ~6 archivos de dominio backend, 2 rutas API, 1 migración, ~5 componentes/páginas frontend — ver "Project Structure" para el listado concreto

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación | Estado |
|---|---|---|
| I. API-First y Dominio Primero | Toda validación nueva (título, clasificación fuera de horario, tope de SLA) se agrega en `backend/domain/services/*` (`ticket_service.py`, `work_session_service.py`), consumida por las rutas Flask-RESTX ya existentes. No se agrega lógica de negocio en componentes React ni en rutas Flask directamente. | PASS |
| II. Clean Architecture 3 capas | Cambios de dominio en `backend/domain/` (sin imports de Flask/SQLAlchemy); migración en `backend/infra/`; rutas y serialización en `backend/api/`; componentes frontend permanecen "tontos", la lógica de clasificación/validación vive en `frontend/src/services/` cuando aplica (ej. regla de rechazo de emoji se valida también server-side, no solo en el form). | PASS |
| III. Tipado Estricto | Nuevos campos/funciones con type hints (Python) y sin `any` nuevo en TS; el campo nuevo de `WorkSession` se tipa explícitamente en `types/` del frontend. | PASS |
| IV. Seguridad en Profundidad | Sin cambios de superficie de seguridad (no se tocan JWT, RLS, ni secretos). | PASS |
| V. Gobernanza de Librerías | Cero dependencias nuevas: la detección de emojis se implementa con un rango Unicode acotado en Python/TS (sin librería `emoji`); si en implementación resultara insuficiente, requiere aprobación documentada antes de agregarla. | PASS (condicional, ver Complexity Tracking si cambia) |
| VI. AI-Native | La clasificación "tiempo fuera de jornada" se persiste como campo estructurado booleano/enum en `WorkSession`, no como texto libre — reutilizable por análisis futuro. | PASS |
| VII. Alcance de Sesión / Testing Ultra-Limitado | El plan delimita explícitamente los archivos por historia de usuario (ver Project Structure); `tasks.md` deberá instruir pruebas unitarias acotadas por archivo modificado, sin correr la suite completa ni insertar más de 5-10 registros de prueba por test. | PASS |

Sin violaciones que requieran la tabla de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/028-cierre-backlog-uat-abierto/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── domain/
│   ├── entities/
│   │   ├── ticket.py                    # STATUSES, sla_* fields (ya existen, sin nuevos campos)
│   │   └── work_session.py              # + campo nuevo: off_hours (US6, FR-020/021)
│   ├── services/
│   │   ├── sla_service.py               # US1: compute_consumed_seconds/compute_state/apply_transition
│   │   │                                 #      deben recibir siempre resource+calendar context
│   │   ├── ticket_service.py            # US3: validate_create — título vacío/emoji (FR-011..013)
│   │   ├── work_session_service.py      # US2/US6: assert_ticket_open_or_admin en start();
│   │   │                                 #          clasificación off_hours y work_date local (FR-007..010, 020, 021)
│   │   └── ticket_timer_service.py      # US2/US6: start() valida estado del ticket; finish()
│   │                                     #          usa fecha local del recurso, no date.today() servidor
│   └── fsm/ticket_fsm.py                # referencia: SLA_PHASE_FOR_STATE / STATE_COUNTS_FOR_SLA
├── workers/
│   └── sla_tasks.py                     # US1: check_sla_breaches — misma corrección de contexto de calendario
├── infra/
│   ├── models/ticket_model.py           # sin cambios de esquema (AssignmentModel ya tiene assigned_at)
│   ├── models/work_session_model.py     # + columna off_hours
│   ├── migrations/versions/             # + 1 migración Alembic nueva
│   └── repositories/work_sessions_repo.py
└── api/
    ├── routes/tickets.py                # US1/US3: expone sla_last_resume_at/assigned_at en el detalle;
    │                                     #          delega validación de título a TicketService
    ├── routes/sla_rules.py              # US4: _validate_minutes — tope máximo (FR-016)
    └── routes/timer.py (o equivalente)  # US2: nuevo caso de error ticket_closed en start()

frontend/
├── src/
│   ├── pages/
│   │   ├── TicketsPage.tsx              # US3: Form.Item title — whitespace:true + validador de emoji
│   │   ├── SlaRulesPage.tsx             # US4: confirmar que el toast de éxito se muestra (investigar por qué UAT no lo vio)
│   │   └── CalendarPage.tsx             # US5: TeamOverlayCalendar — agregar getWorkSchedule/listAbsenceRequests
│   ├── components/
│   │   ├── sla/SlaRuleForm.tsx          # US4: reemplazar min/max de InputNumber por regla de validación explícita
│   │   ├── worksessions/TicketTimerWidget.tsx  # US2: deshabilitar "Iniciar" si ticket.status === 'cerrado'
│   │   └── tickets/<SlaCard o equivalente>     # US5: estado visual inicial del SLA antes de iniciar (a ubicar en tasks.md)
│   ├── services/calendarService.ts      # US5: ya expone getWorkSchedule/listAbsenceRequests/getAvailability (sin cambios de contrato)
│   └── types/                            # + campo off_hours en el tipo WorkSession
```

**Structure Decision**: Se reutiliza la estructura Web application (backend Flask + frontend React) ya existente en el repo (Clean Architecture 3 capas, Principio II). No se crean módulos ni carpetas nuevas de alto nivel; todos los cambios son modificaciones puntuales a archivos ya existentes listados arriba, más una migración Alembic nueva para el campo `off_hours` de `work_sessions`.

## Complexity Tracking

*Sin violaciones de la Constitución que requieran justificación en esta fase.*
