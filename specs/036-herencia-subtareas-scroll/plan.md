# Implementation Plan: Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering en Scroll del Ticket

**Branch**: `036-herencia-subtareas-scroll` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/036-herencia-subtareas-scroll/spec.md`

## Summary

Al crear una Subtarea desde una Tarea padre, el sistema debe copiar automáticamente Nivel de
escalamiento, Usuario solicitante/cliente y Skills requeridas de la Tarea padre; la Tarea padre
ya expone (código existente, `_ticket_detail`/`SubtaskList.tsx`) su lista de Subtareas, y se le
agrega a la Subtarea un campo "Tarea Padre" con hipervínculo de vuelta. Enfoque técnico: extender
el bloque `if parent_task_id:` ya existente en `POST /api/tickets` (`backend/api/routes/tickets.py`)
para copiar los tres campos cuando no vienen en el payload, agregar un campo aditivo `parent` en
`_ticket_detail`, y mostrarlo en `TicketDetailPage.tsx` reutilizando el patrón de hipervínculo ya
usado para "Registro relacionado". Aparte, se corrige un bug de re-render encontrado en el mismo
componente: el listener de scroll que colapsa/expande el resumen de tiempo no tiene histéresis,
por lo que micro-oscilaciones de scroll alternan su estado y hacen "saltar" verticalmente las
Cards de abajo (Clasificación, Historial) — se agrega una zona muerta + throttle por `rAF`.

## Technical Context

**Language/Version**: Python 3.12 (backend, Flask) + TypeScript 5 estricto / React 19 (frontend)

**Primary Dependencies**: Flask-RESTX, SQLAlchemy + Alembic (ya usados, sin cambios), Ant Design 5,
Axios — todas ya aprobadas en la Constitución (Principio V). **Sin dependencias nuevas.**

**Storage**: PostgreSQL 16 — sin migración de Alembic (todas las columnas/relaciones usadas ya
existen: `tickets.escalation_level`, `tickets.client_contact_id`, `tickets.parent_task_id`,
`ticket_skills`).

**Testing**: `pytest` (backend, acotado a los archivos tocados, dataset ≤ 10 registros por test,
Principio VII); `tsc -b` (frontend, sin suite E2E automatizada — validación manual en Docker real
para el bug visual de scroll).

**Target Platform**: Web app on-premise (Docker Compose), navegador de escritorio.

**Project Type**: Web application (backend Flask + frontend React, estructura ya existente).

**Performance Goals**: N/A — no introduce carga nueva medible; el fix de scroll reduce, no
aumenta, el trabajo de render (menos toggles de estado durante scroll).

**Constraints**: Principio VII (alcance de sesión acotado a los archivos de esta feature; sin
correr la suite de pruebas completa; sin refactorizar la arquitectura de tickets); Principio II
(la copia de campos en creación es lógica de negocio, pero se implementa siguiendo el patrón ya
existente de `list_id` en la Capa 3 (`api/routes/tickets.py`) por consistencia con el código ya
en producción — no se introduce un servicio nuevo de Capa 1 para un copy-on-create de 3 campos).

**Scale/Scope**: 1 endpoint existente extendido (`POST /api/tickets`), 1 campo aditivo en 1
endpoint existente (`GET /api/tickets/{id}`), 2 componentes frontend tocados
(`TicketDetailPage.tsx`, `SubtaskList.tsx` sin cambios de fondo — ya no envía los 3 campos, lo
cual ya es el estado deseado), 1 tipo TypeScript extendido (`TicketDetail`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principio I (API-First y Dominio Primero)**: Cumple — no se agregan endpoints nuevos, se
  extiende el contrato ya documentado en Swagger de `POST /api/tickets` y `GET
  /api/tickets/{id}`; el contrato se documenta en `contracts/` antes de tocar código.
- **Principio II (Clean Architecture)**: Cumple con nota — la copia de campos en creación se
  hace en `api/routes/tickets.py` (Capa 3), siguiendo el patrón ya existente para `list_id` en
  el mismo archivo/bloque (no se introduce una regla de negocio nueva y aislada en Capa 1 para
  una copia de 3 columnas; se mantiene consistencia con el código ya en producción). No hay
  lógica de negocio nueva en componentes React — `TicketDetailPage.tsx` solo renderiza el campo
  `parent` ya resuelto por el backend.
- **Principio III (Tipado estricto)**: Cumple — se extiende `TicketDetail` (TypeScript) con
  `parent`; sin `any`.
- **Principio IV (Seguridad en profundidad)**: Sin impacto — mismos permisos/RLS ya vigentes
  para lectura de Ticket; el campo `parent` respeta el mismo control de acceso que el resto del
  detalle (si el usuario puede ver la Subtarea, puede ver el resumen de su Tarea padre).
- **Principio V (Gobernanza de librerías)**: Cumple — cero dependencias nuevas.
- **Principio VI (AI-Native)**: Sin impacto — no cambia la estructura de los endpoints de acción
  (`/assign`, `/status`), no afecta el Gold Standard Dataset.
- **Principio VII (Alcance y testing ultra-limitado)**: Cumple — cambios acotados a
  `backend/api/routes/tickets.py`, `backend/infra/repositories/ticket_repo.py` (si se requiere
  un helper de lectura), `frontend/src/pages/TicketDetailPage.tsx`,
  `frontend/src/components/tickets/SubtaskList.tsx`, `frontend/src/types/ticket.ts`; tests
  nuevos/editados limitados a ≤10 registros; sin correr la suite completa.

**Resultado**: PASS, sin violaciones. Tabla de Complexity Tracking no aplica.

## Project Structure

### Documentation (this feature)

```text
specs/036-herencia-subtareas-scroll/
├── plan.md              # Este archivo
├── research.md          # Fase 0 — decisiones técnicas
├── data-model.md         # Fase 1 — campos/contrato aditivos, sin migración
├── contracts/
│   └── subtask-inheritance-and-parent-link.md
├── quickstart.md        # Fase 1 — validación manual end-to-end
└── tasks.md             # Fase 2 (/speckit-tasks — no generado por este comando)
```

### Source Code (repository root)

```text
backend/
├── api/routes/tickets.py                 # POST /api/tickets: copia escalation_level/
│                                          #   client_contact_id/skill_ids del padre;
│                                          #   _ticket_detail: agrega campo `parent`
├── infra/repositories/ticket_repo.py     # sin cambios de esquema; reutiliza get_by_id/
│                                          #   update_skills ya existentes
└── tests/api/
    └── test_tickets_subtasks.py           # casos nuevos de herencia (≤10 registros)

frontend/
├── src/pages/TicketDetailPage.tsx        # Card "Clasificación": nuevo item "Tarea Padre";
│                                          #   fix del listener de scroll (dead-zone + rAF)
├── src/components/tickets/SubtaskList.tsx # sin cambios de fondo (ya no envía los 3 campos
│                                          #   heredables — el backend completa el resto)
└── src/types/ticket.ts                    # TicketDetail: + campo `parent`
```

**Structure Decision**: Se mantiene la estructura Backend (Flask, 3 capas) + Frontend (React)
ya vigente en el repositorio (`backend/{domain,infra,api}` + `frontend/src/{pages,components,
services,types}`). No se crean directorios nuevos; todos los cambios caen en archivos
existentes de Capa 3 (rutas/páginas) y en el tipo TypeScript compartido, según lo acotado por
Principio VII.

## Complexity Tracking

> No aplica — Constitution Check sin violaciones.
