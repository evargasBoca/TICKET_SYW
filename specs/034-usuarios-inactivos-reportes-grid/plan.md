# Implementation Plan: Deshabilitación de Usuarios/Cliente y Módulo de Reportes Dinámicos (Interactive Grid)

**Branch**: `034-usuarios-inactivos-reportes-grid` | **Date**: 2026-07-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/034-usuarios-inactivos-reportes-grid/spec.md`

## Summary

(1) Exponer y gestionar el estado Activo/Inactivo, ya existente en `users.active`, para cuentas
de rol Usuario/cliente desde la pantalla de administración ya existente (`ClientContactsPage.tsx`
+ `backend/api/routes/client_contacts.py`), con un endpoint acotado por el permiso
`client_contacts:manage` (Coordinador ya lo tiene) en vez de reutilizar el endpoint genérico
`users:deactivate` (Admin-only). (2) Nuevo módulo "Reportes": un namespace backend nuevo
(`backend/api/routes/reports.py`) que proyecta datos ya existentes (Ticket, SLA, Recursos,
Herramienta/Proceso/Skills, tiempo registrado) en un grid interactivo (Ant Design Table +
`@hello-pangea/dnd` ya aprobado, sin dependencias frontend nuevas) con columnas
mostrables/ocultables/reordenables, filtros combinables, agregaciones calculadas en SQL sobre el
conjunto filtrado completo, Vistas Personalizadas guardadas por usuario (`report_saved_views`) y
exportación a `.xlsx` generada en el backend con `openpyxl` (única dependencia nueva, Principio V).

## Technical Context

**Language/Version**: Python 3.12 (Flask, backend) · TypeScript 5.6 strict + React 19 (frontend) — sin cambios de versión.

**Primary Dependencies**: Flask-RESTX, SQLAlchemy + Alembic, Ant Design 5, `@hello-pangea/dnd`,
`date-fns` (todos existentes, sin cambios). **Nueva dependencia backend aprobada aquí** (Principio
V, ver `research.md` Decisión 4): `openpyxl` (generación de `.xlsx`). Sin nuevas dependencias de
frontend.

**Storage**: PostgreSQL 16 — 1 tabla nueva (`report_saved_views`, ver `data-model.md`). Sin
columnas nuevas en `users`/`client_contacts` (se reutiliza `users.active` ya existente).

**Testing**: `pytest` acotado a los archivos nuevos/tocados de esta sesión (Principio VII —
prohibido correr la suite completa). Tests de agregación/exportación con dataset mock de 5-10
tickets, sin insertar más registros que esos en la base de datos por test.

**Target Platform**: Web (mismo entorno Docker Compose ya vigente).

**Project Type**: Web application (frontend + backend ya existente, `frontend/` + `backend/`).

**Performance Goals**: Sin objetivo especial nuevo — mismo orden de magnitud que los listados
paginados ya existentes (decenas a pocos cientos de tickets por consulta filtrada).

**Constraints**: Alcance de sesión limitado (Principio VII) a: vistas de administración de
Usuarios/cliente (`ClientContactsPage.tsx` + `client_contacts.py` + su servicio/tipos) y al nuevo
módulo de Reportes (rutas, repositorio, servicio de agregación, migración, página y servicio
frontend nuevos). Prohibido refactorizar `TeamPage.tsx`, `users.py` u otros módulos no listados.

**Scale/Scope**: 2 áreas de código (administración de Usuarios/cliente + módulo de Reportes
nuevo), 6 historias de usuario, 1 tabla nueva, 1 dependencia nueva.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. API-First y Dominio Primero**: PASS. Todos los endpoints nuevos (`client-contacts/.../active`,
  `reports/*`) se documentan en Swagger (Flask-RESTX) antes de implementarse (ver `contracts/`).
  El cálculo de agregaciones vive en un servicio de dominio puro
  (`backend/domain/services/report_aggregation_service.py`), sin imports de Flask/SQLAlchemy.
- **II. Clean Architecture - Tres Capas**: PASS. Capa 1: `report_aggregation_service.py` (puro).
  Capa 2: `backend/infra/repositories/report_repo.py` (proyección SQL) y el nuevo modelo
  `ReportSavedViewModel`. Capa 3: `backend/api/routes/reports.py` y `client_contacts.py`
  (orquestación), `frontend/src/pages/ReportsPage.tsx` (solo renderiza, lógica en
  `frontend/src/services/reportService.ts`).
- **III. Tipado Estricto**: PASS. Tipos TS nuevos en `frontend/src/types/report.ts` (sin `any`);
  type hints en el servicio de dominio y el repositorio nuevos.
- **IV. Seguridad en Profundidad**: PASS. `reports:view` y `client_contacts:manage` vía JWT +
  RBAC ya vigente (`jwt_required_active`); Vistas Personalizadas acotadas por `user_id` en cada
  query (ownership check, mismo criterio que otros datos privados del sistema). Sin exponer
  detalles internos en errores.
- **V. Gobernanza de Librerías**: **Nueva dependencia aprobada en este plan**: `openpyxl`
  (backend). Ver Decisión 4 de `research.md` para alternativas rechazadas. Sin dependencias
  nuevas de frontend (se reutilizan Ant Design 5 y `@hello-pangea/dnd`).
- **VI. AI-Native**: N/A directo — el reporte es de solo lectura sobre datos que ya alimentan el
  futuro AI Dispatcher; no introduce nuevos campos de negocio que deban parametrizarse.
- **VII. Alcance de Sesión y Testing Ultra-Limitado**: PASS — ver Constraints arriba y sección de
  Testing. Se documenta explícitamente para que la fase de implementación no se desvíe.

**Resultado**: Sin violaciones. No aplica tabla de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/034-usuarios-inactivos-reportes-grid/
├── plan.md              # Este archivo
├── research.md          # Fase 0 — decisiones 1-8
├── data-model.md         # Fase 1 — report_saved_views + proyección de Fila de Reporte
├── contracts/
│   └── reports-y-client-contacts.md
├── quickstart.md         # Fase 1 — guía de validación por historia de usuario
└── tasks.md              # Fase 2 (/speckit-tasks, no generado por este comando)
```

### Source Code (repository root)

```text
backend/
├── domain/
│   └── services/
│       └── report_aggregation_service.py     # nuevo (Capa 1, puro)
├── infra/
│   ├── models/
│   │   └── report_view_model.py              # nuevo — ReportSavedViewModel
│   ├── repositories/
│   │   └── report_repo.py                    # nuevo — proyección de Fila de Reporte + views CRUD
│   └── migrations/versions/
│       └── 0XX_report_saved_views.py         # nueva migración (1 tabla)
├── api/
│   └── routes/
│       ├── reports.py                        # nuevo namespace
│       └── client_contacts.py                # tocado: +active en GET, +PATCH /active, +validación en /projects
└── requirements.txt                          # + openpyxl

frontend/
├── src/
│   ├── config/
│   │   └── navigation.tsx                    # tocado: + entrada "Reportes"
│   ├── pages/
│   │   ├── ClientContactsPage.tsx            # tocado: columna Estado + acción activar/desactivar
│   │   └── ReportsPage.tsx                   # nuevo
│   ├── services/
│   │   ├── clientContactService.ts           # tocado: setActive(id, active)
│   │   └── reportService.ts                  # nuevo
│   └── types/
│       ├── clientContact.ts                  # tocado: +active
│       └── report.ts                         # nuevo
```

**Structure Decision**: Web application ya existente (`backend/` Flask + `frontend/` React),
Clean Architecture de 3 capas ya vigente. Sin proyectos nuevos ni cambios de estructura de
directorios raíz — solo archivos nuevos dentro de las carpetas de capa ya establecidas, y los
archivos explícitamente listados como "tocados" (Principio VII: nada fuera de esta lista).

## Complexity Tracking

*Sin violaciones que requieran justificación — tabla omitida (ver Constitution Check).*
