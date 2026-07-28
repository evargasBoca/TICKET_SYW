# Implementation Plan: Cierre de OBS-0060–OBS-0063 (Backlog UAT ITER-009)

**Branch**: `032-cierre-obs-0044-0047` | **Date**: 2026-07-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/032-cierre-obs-0044-0047/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Cerrar las 4 observaciones "Abierta" del Backlog UAT (`OBS-0060` a `OBS-0063`, `ITER-009`): corregir la hora mostrada en el historial de registros de tiempo (bug de conversión de zona horaria en presentación, no en almacenamiento), reubicar la etiqueta "Fuera de jornada" para que no se superponga al horario, generar notificación al reasignar un ticket (hoy solo existe en la asignación inicial) y bloquear la asignación/reasignación de tickets a resolutores cuya cuenta de usuario esté inactiva (hoy solo se valida `Resource.active`, no el `User.active` vinculado). Las 4 correcciones son quirúrgicas sobre código ya existente, sin nuevas dependencias ni migraciones de base de datos.

## Technical Context

**Language/Version**: Python 3.12 (backend) + TypeScript strict / React 19 (frontend), ya en uso en el repositorio.

**Primary Dependencies**: Flask-RESTX, SQLAlchemy (backend); Ant Design 5, `date-fns` (frontend) — todas ya aprobadas en la Constitución (Principio V), sin dependencias nuevas.

**Storage**: PostgreSQL 16 (on-premise, RLS) — sin cambios de esquema; no se requiere migración de Alembic (ver `data-model.md`).

**Testing**: `pytest` (backend, acotado a los módulos tocados — `work_sessions`, `tickets`/`assign`/`reassign`, `notifications` — per Principio VII, prohibido correr la suite global); verificación manual en Docker real vía `quickstart.md` para lo visual (frontend no tiene suite automatizada de UI en este repo).

**Target Platform**: Web (Docker Compose on-premise), navegadores modernos de escritorio.

**Project Type**: Web application (`backend/` Flask + `frontend/` React, ya existente).

**Performance Goals**: N/A — correcciones puntuales de presentación/validación, sin impacto en volumen ni latencia.

**Constraints**: Ninguna corrección puede alterar el contrato de API existente de forma rompiente (ver `contracts/api-changes.md`); OBS-0063 no puede afectar asignaciones ya existentes (FR-014), solo nuevas.

**Scale/Scope**: 4 observaciones, acotadas a: 2 componentes frontend (`TimeLogModal.tsx`, `WorkSessionForm.tsx`), 2 endpoints backend (`/assign`, `/reassign`) + sus 2 servicios de dominio (`AssignmentService`, `ReassignmentService`), 1 servicio de notificaciones, y el selector de candidatos a resolutor (`useResourceCandidates.ts`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principio I (API-First)**: Sin violaciones. No se agregan endpoints nuevos; `/assign` y `/reassign` siguen siendo endpoints de acción independientes de la UI. Los cambios de contrato son aditivos y están documentados en `contracts/api-changes.md`.
- **Principio II (Clean Architecture, 3 capas)**: Sin violaciones. La corrección de OBS-0060/0045 vive enteramente en Capa 3 frontend (presentación). La de OBS-0062/0047 vive en Capa 1 (`AssignmentService`, `ReassignmentService`, `NotificationService`, dominio puro) y Capa 3 (`tickets.py`, orquestación). Ningún cambio introduce lógica de negocio en componentes React ni en rutas Flask directamente.
- **Principio III (Tipado estricto)**: Sin violaciones — no se introduce `any`; los tipos TS ya existentes (`WorkSessionListItem`, `Resource`) se reutilizan sin cambios de forma.
- **Principio IV (Seguridad en profundidad)**: OBS-0063 refuerza este principio (defensa en profundidad: validación tanto en el selector del frontend como en el backend, evitando bypass directo a la API).
- **Principio V (Gobernanza de librerías)**: Sin dependencias nuevas. `date-fns` (ya aprobado) se usa para el fix de OBS-0060.
- **Principio VI (AI-Native)**: Sin impacto — `/assign` y `/reassign` siguen siendo agnósticos al caller (humano o futuro AI Dispatcher); el nuevo chequeo de `User.active` aplica igual sin importar quién invoque el endpoint.
- **Principio VII (Alcance de sesión / testing ultra-limitado)**: Este plan restringe explícitamente las pruebas a los módulos tocados, sin correr la suite completa ni insertar más de un puñado de registros de prueba.

**No hay violaciones que requieran la tabla "Complexity Tracking".**

## Project Structure

### Documentation (this feature)

```text
specs/032-cierre-obs-0044-0047/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/            # Phase 1 output (/speckit-plan command)
│   └── api-changes.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── domain/
│   ├── entities/
│   │   └── notification.py           # OBS-0062: agrega event_type "reassigned"
│   └── services/
│       ├── assignment_service.py     # OBS-0063: valida también User.active vinculado
│       ├── reassignment_service.py   # OBS-0063: idem + dispara notificación (OBS-0062)
│       └── notification_service.py   # OBS-0062: nueva plantilla + mensaje enriquecido
├── infra/
│   └── repositories/
│       └── resource_repo.py          # OBS-0063: expone/filtra por User.active vinculado (si aplica)
├── api/
│   └── routes/
│       └── tickets.py                # OBS-0062/0047: TicketReassign — notificación + validación
└── tests/
    ├── domain/                       # tests acotados de assignment/reassignment/notification service
    └── api/                          # test_tickets_api.py (reassign) — acotado, no suite completa

frontend/
├── src/
│   ├── components/
│   │   ├── worksessions/
│   │   │   ├── TimeLogModal.tsx      # OBS-0060 (formatTimeRange) + OBS-0061 (layout etiqueta)
│   │   │   └── WorkSessionForm.tsx   # OBS-0060 (timeOf, precarga de edición)
│   │   └── tickets/
│   │       └── useResourceCandidates.ts  # OBS-0063: excluir cuenta de usuario inactiva
│   └── services/
│       └── resourceService.ts        # OBS-0063: si el filtro se resuelve server-side
```

**Structure Decision**: Se reutiliza la estructura de tres capas ya existente (`backend/domain` → `backend/infra` → `backend/api`, `frontend/src/{components,services}`), sin crear directorios nuevos. Las 4 correcciones son cambios puntuales dentro de archivos ya existentes, consistentes con el alcance acotado exigido por el Principio VII de la Constitución.

## Complexity Tracking

*Sin violaciones que justificar — tabla omitida.*
