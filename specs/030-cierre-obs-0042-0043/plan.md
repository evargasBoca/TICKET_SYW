# Implementation Plan: Cierre de OBS-0042/OBS-0043 (Backlog UAT ITER-007)

**Branch**: `030-cierre-obs-0042-0043` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/030-cierre-obs-0042-0043/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Corregir las 2 observaciones en estado `Abierta` del backlog UAT (`OBS-0042`, `OBS-0043`, `ITER-007`): (1) reorganizar el layout del Detalle del Ticket (`TicketDetailPage.tsx`) intercambiando las Cards "Clasificación" y "Comentarios y acciones" entre columnas, y dándole al historial de comentarios (`CommentThread`) su propio contenedor con scroll interno acotado, mientras la caja de nuevo comentario y las acciones de estado permanecen visibles; (2) exponer el cliente del proyecto en SLA Configurable — reutilizando `client_id`/`client_name` ya existente en `ProjectListItem` para el selector "Filtrar por proyecto" y el formulario, y ampliando de forma aditiva el serializador de `SlaRule` (`backend/api/routes/sla_rules.py`) para agregar `client_id`/`client_name` y así poder mostrar una columna "Cliente" en la tabla. Ambas correcciones son ajustes acotados dentro de la arquitectura de 3 capas existente, sin nuevas dependencias ni migraciones de base de datos.

## Technical Context

**Language/Version**: Python 3.12 (Flask) — backend; TypeScript 5 / React 19 — frontend (stack ya aprobado en la Constitución, sin cambios)

**Primary Dependencies**: Flask-RESTX (Swagger), SQLAlchemy (backend); Ant Design 5 (frontend) — todas ya aprobadas; **este feature no introduce dependencias nuevas** (Principio V)

**Storage**: PostgreSQL 16 — **sin migración Alembic**: `client_id`/`client_name` de `SlaRule` se derivan en tiempo de lectura desde `Project.client_id` (ya existente), no se persiste columna nueva

**Testing**: pytest para el serializador de `sla_rules.py` (alcance ultra-limitado, Principio VII); verificación funcional end-to-end contra Docker real siguiendo `quickstart.md`; OBS-0042 es un cambio puramente de presentación (frontend), verificado visualmente en el navegador (sin suite de tests de UI en este repo)

**Target Platform**: Docker Compose (entorno de desarrollo/UAT); despliegue on-premise (fuera de alcance)

**Project Type**: Web application (backend Flask API + frontend React SPA) — estructura ya existente, Option 2 del template

**Performance Goals**: Sin metas nuevas explícitas; el join adicional a `Client` en `_serialize()` de SLA Rules opera sobre un volumen bajo (decenas de reglas), sin impacto perceptible

**Constraints**: No debe romper el contrato de `GET/POST/PATCH /api/sla-rules` para consumidores existentes (cambio aditivo, ver `contracts/api-changes.md`); el reordenamiento de `TicketDetailPage.tsx` no debe cambiar el comportamiento de edición de "Clasificación" ni de "Comentarios y acciones", solo su ubicación y el contenedor de scroll; sin dependencias nuevas (Principio V); pruebas nuevas/modificadas ultra-limitadas (Principio VII)

**Scale/Scope**: 2 observaciones UAT, 2 User Stories, 1 endpoint backend ampliado (serializador), 2 páginas/componentes frontend — ver "Project Structure"

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación | Estado |
|---|---|---|
| I. API-First y Dominio Primero | `client_id`/`client_name` de `SlaRule` se agregan en `_serialize()` (capa de presentación de la ruta), leyendo datos ya persistidos vía `ProjectRepository`/`ClientRepository` existentes; no se agrega lógica de negocio nueva. El contrato Swagger (`_sla_rule_out`) se actualiza junto con el código, antes de darse por terminado. | PASS |
| II. Clean Architecture 3 capas | Sin cambios en `backend/domain/`. Cambio en `backend/api/routes/sla_rules.py` (Capa 3) reutilizando repositorios ya existentes de Capa 2. Frontend: `TicketDetailPage.tsx`/`SlaRulesPage.tsx`/`SlaRuleForm.tsx` siguen orquestando/renderizando; ningún componente en `frontend/src/components/` gana lógica de negocio nueva. | PASS |
| III. Tipado Estricto | `SlaRule` (TS) y el modelo `_sla_rule_out` (Flask-RESTX) se amplían con tipos explícitos (`client_id: string \| null`, `client_name: string \| null`); sin `any` nuevo. | PASS |
| IV. Seguridad en Profundidad | Sin cambios de superficie de seguridad: mismo permiso `sla_rules:manage` ya exigido; no se exponen datos sensibles nuevos (nombre de cliente ya visible en Maestros > Clientes/Proyectos para los mismos roles). | PASS |
| V. Gobernanza de Librerías | Cero dependencias nuevas. | PASS |
| VI. AI-Native | No aplica cambio de superficie de acción crítica (`/assign`, `/status`); no introduce texto libre nuevo. | PASS |
| VII. Alcance de Sesión / Testing Ultra-Limitado | Cambios acotados a los archivos listados en "Project Structure"; `tasks.md` debe instruir pruebas unitarias acotadas al serializador modificado, sin correr la suite completa. | PASS |

Sin violaciones que requieran la tabla de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/030-cierre-obs-0042-0043/
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
├── api/
│   └── routes/sla_rules.py          # OBS-0043: _serialize() agrega client_id/client_name
│                                     #           (resuelve Client vía ClientRepository, usando project.client_id)
└── infra/
    └── repositories/
        ├── project_repo.py          # sin cambios — ya usado por _serialize()
        └── client_repo.py           # sin cambios — get_by_id() ya existente, se reutiliza

frontend/
├── src/
│   ├── pages/
│   │   ├── TicketDetailPage.tsx     # OBS-0042: intercambia Cards "Clasificación" ⇄ "Comentarios y acciones"
│   │   │                            #           entre Col lg={14}/lg={10}; envuelve CommentThread en
│   │   │                            #           contenedor con max-height + overflow-y (scroll interno)
│   │   └── SlaRulesPage.tsx         # OBS-0043: opciones de "Filtrar por proyecto" muestran cliente + proyecto;
│   │                                #           columna nueva "Cliente" en la tabla de reglas
│   ├── components/
│   │   ├── tickets/CommentThread.tsx    # sin cambios internos — solo se envuelve desde TicketDetailPage
│   │   ├── tickets/CommentComposer.tsx  # sin cambios
│   │   └── sla/SlaRuleForm.tsx      # OBS-0043: opciones del Select "Proyecto" muestran cliente + proyecto
│   └── types/
│       ├── project.ts                # sin cambios — client_id/client_name ya existían
│       └── sla.ts                    # OBS-0043: SlaRule + client_id, client_name
```

**Structure Decision**: Se reutiliza la estructura Web application (backend Flask + frontend React) ya existente en el repo (Clean Architecture 3 capas, Principio II). No se crean módulos, carpetas ni servicios nuevos; todos los cambios son modificaciones puntuales a los archivos listados arriba. Sin migración Alembic.

## Complexity Tracking

*Sin violaciones de la Constitución que requieran justificación en esta fase.*
