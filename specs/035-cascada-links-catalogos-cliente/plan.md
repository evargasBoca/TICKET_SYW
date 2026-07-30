# Implementation Plan: Selección en Cascada, Hipervínculos, Edición de Catálogos y Layout de Cliente

**Branch**: `035-cascada-links-catalogos-cliente` | **Date**: 2026-07-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/035-cascada-links-catalogos-cliente/spec.md`

## Summary

Ajustes de usabilidad puntuales sobre pantallas ya existentes, sin nuevas entidades ni migraciones:
(1) unificar el formulario de Ticket/Tarea al flujo Cliente→Proyecto→Encargado ya implementado para
Tareas (reemplazando el flujo "Proyecto primero" de OBS-0045 para Tickets) y dejar visible (aunque
deshabilitado para no-Coordinador) el campo Skills que hoy se oculta por completo; (2) convertir el
código de ticket/tarea en link clicable en `TicketsPage.tsx`, `MyTasksPage.tsx` y `KanbanPage.tsx`
(ya lo era en `AssignmentPanelPage.tsx`); (3) agregar 3 claves nuevas al `sort` ya soportado por
`GET /api/tickets` (`-status`, `code`, `-code`) y reemplazar el indicador fijo `SortIndicator` por un
selector real; (4) ensanchar y reorganizar en columnas el Modal "Detalle del cliente" de
`ClientsPage.tsx`; (5) agregar `PATCH /api/catalogs/{catalog}/{id}` (rename) + botón "Editar" en
`CatalogsPage.tsx`, reutilizando el permiso `catalogs:create` ya existente.

## Technical Context

**Language/Version**: Python 3.12 (Flask) + TypeScript strict (React 19)

**Primary Dependencies**: Flask-RESTX, SQLAlchemy (backend); Ant Design 5, Axios, react-router-dom (frontend) — todas ya aprobadas, sin dependencias nuevas

**Storage**: PostgreSQL 16 (sin migraciones — reutiliza columnas/tablas existentes)

**Testing**: pytest (backend, acotado a archivos tocados — Principio VII); validación manual/E2E desechable contra Docker real para UI (sin suite de frontend automatizada en este repo)

**Target Platform**: Web app on-premise (Docker), navegador de escritorio

**Project Type**: Web application (frontend + backend, estructura ya existente)

**Performance Goals**: N/A — ajustes de UI/filtrado sobre endpoints ya paginados existentes

**Constraints**: Principio VII (alcance de sesión acotado a los archivos listados en Research; sin refactors externos; sin suite de pruebas completa)

**Scale/Scope**: 5 pantallas existentes tocadas (`TicketsPage`, `MyTasksPage`, `KanbanPage`, `ClientsPage`, `CatalogsPage`) + 2 archivos de backend (`catalogs.py`/`catalog_repo.py`) + 1 extensión de `tickets.py`/`ticket_repo.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. API-First y Dominio Primero**: PASS — el único endpoint nuevo (`PATCH /api/catalogs/{catalog}/{id}`)
  se documenta en Swagger (Flask-RESTX `@ns.doc`/`@ns.expect`/`@ns.response`) igual que el resto del
  namespace `catalogs`, antes de implementarse. No se toca `POST /assign` ni se acopla lógica de
  negocio a componentes React (el filtrado en cascada es solo UI sobre datos ya expuestos por
  `projectService`/`clientContactService`).
- **II. Clean Architecture**: PASS — `CatalogRepository.rename` vive en Capa 2 (`backend/infra/`,
  ya existente), el endpoint en Capa 3 (`backend/api/routes/catalogs.py`). No hay lógica de negocio
  nueva de Capa 1: renombrar un catálogo y ordenar una lista no son reglas de dominio.
- **III. Tipado Estricto**: PASS — cambios de frontend en TypeScript strict, sin `any` nuevo; tipos
  ya existentes (`CatalogItem`, `TicketListItem`) se reutilizan sin cambios de forma.
- **IV. Seguridad en Profundidad**: PASS — el nuevo endpoint queda detrás de `require_permission`
  (reutiliza `catalogs:create`, ya restringido a Admin/Coordinador vía RLS/roles existentes); no se
  expone información sensible nueva.
- **V. Gobernanza de Librerías**: PASS — cero dependencias nuevas (frontend y backend).
- **VI. AI-Native**: N/A — no toca `/assign`, `/status`, ni el modelo de comentarios estructurados.
- **VII. Alcance de Sesión / Testing Ultra-Limitado**: PASS por diseño — ver Research.md "Resumen de
  archivos a tocar"; pruebas nuevas/actualizadas acotadas a los archivos tocados, sin correr la
  suite completa, sin insertar más de 5-10 registros de prueba.

Sin violaciones — tabla "Complexity Tracking" no aplica.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── api/routes/
│   ├── catalogs.py          # + PATCH /api/catalogs/{catalog}/{item_id} (rename)
│   └── tickets.py           # doc del parámetro `sort`: + "-status", "code", "-code"
└── infra/repositories/
    ├── catalog_repo.py      # + CatalogRepository.rename(...)
    └── ticket_repo.py       # _SORTS: + "-status", "code", "-code"

frontend/src/
├── pages/
│   ├── TicketsPage.tsx      # cascada Cliente→Proyecto→Encargado unificada, Skills visible,
│   │                        #   columna "Número" como link, selector de orden (reemplaza SortIndicator)
│   ├── MyTasksPage.tsx      # columna "Número" como link, selector de orden
│   ├── KanbanPage.tsx       # código de la tarjeta como link (sin romper drag-and-drop)
│   ├── ClientsPage.tsx      # Modal "Detalle del cliente" — layout horizontal (Row/Col)
│   └── CatalogsPage.tsx     # CatalogCard: botón "Editar" + modal de rename
├── components/tickets/
│   └── SortIndicator.tsx    # reemplazado por el selector de orden (o eliminado si queda inline)
└── services/
    ├── catalogService.ts    # + rename(catalog, id, name)
    └── ticketService.ts     # pasar `sort` explícito en list()/panel()
```

**Structure Decision**: Se mantiene la estructura Web application ya vigente en el repo
(`backend/{domain,infra,api}` + `frontend/src/{components,services,store,types,pages}`, Principio II
de la constitución). No se agregan directorios nuevos; todos los cambios caen en archivos ya
existentes descritos arriba (ver research.md para el detalle por decisión).

## Complexity Tracking

No aplica — Constitution Check sin violaciones.
