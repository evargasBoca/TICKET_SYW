# Implementation Plan: Referencia a Subtareas dentro de "Clasificación" en la Tarea principal

**Branch**: `037-subtareas-en-clasificacion` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/037-subtareas-en-clasificacion/spec.md`

## Summary

Hoy la relación Tarea→Subtareas solo se ve en la tarjeta lateral "Subtareas (N)" (spec 009,
contador agregado en spec 036); la Card "Clasificación" del detalle de la Tarea no la refleja en
absoluto, lo que el usuario percibe como que la Subtarea recién creada "no se muestra" en la
Tarea principal. Enfoque: agregar un `Descriptions.Item label="Subtareas"` en la Card
"Clasificación" de `TicketDetailPage.tsx`, justo después del ítem "Tarea Padre" (spec 036),
listando cada Subtarea como hipervínculo (o "Sin subtareas" si no hay ninguna) — reutilizando
`ticket.subtasks`, ya expuesto por la API sin cambios. Sin cambios de backend.

## Technical Context

**Language/Version**: TypeScript 5 estricto / React 19 (frontend). Sin cambios de backend.

**Primary Dependencies**: Ant Design 5 (`Descriptions.Item`, `Button type="link"`, `Space`) —
todas ya usadas en el mismo componente. **Sin dependencias nuevas.**

**Storage**: N/A — sin cambios de esquema ni de API; `ticket.subtasks` ya viene poblado.

**Testing**: `tsc -b` (frontend). Sin test de backend nuevo (sin cambio de backend). Validación
manual en Docker real siguiendo `quickstart.md`.

**Target Platform**: Web app on-premise (Docker Compose), navegador de escritorio.

**Project Type**: Web application (cambio acotado a `frontend/src/pages/TicketDetailPage.tsx`).

**Performance Goals**: N/A — renderiza un array ya cargado, sin fetch adicional.

**Constraints**: Principio VII (alcance de sesión acotado a `TicketDetailPage.tsx`; sin
refactorizar la tarjeta lateral "Subtareas" existente ni la arquitectura de tickets).

**Scale/Scope**: 1 archivo frontend tocado (`TicketDetailPage.tsx`), ~10-15 líneas agregadas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principio I (API-First y Dominio Primero)**: Cumple — no se toca ningún endpoint; se
  renderiza un campo (`subtasks`) que la API ya expone.
- **Principio II (Clean Architecture)**: Cumple — cambio contenido en Capa 3 (componente de
  presentación `TicketDetailPage.tsx`), sin lógica de negocio nueva.
- **Principio III (Tipado estricto)**: Cumple — `TicketDetail.subtasks: TicketListItem[]` ya
  tipado desde spec 009; sin `any` nuevo.
- **Principio IV (Seguridad en profundidad)**: Sin impacto — mismo control de acceso ya vigente
  para ver el detalle del ticket; no se expone ningún dato que la API no devolviera ya.
- **Principio V (Gobernanza de librerías)**: Cumple — cero dependencias nuevas.
- **Principio VI (AI-Native)**: Sin impacto.
- **Principio VII (Alcance y testing ultra-limitado)**: Cumple — cambio de un solo archivo
  frontend, sin test de backend nuevo (no hay cambio de backend que probar), validación manual
  acotada siguiendo `quickstart.md`.

**Resultado**: PASS, sin violaciones. Tabla de Complexity Tracking no aplica.

## Project Structure

### Documentation (this feature)

```text
specs/037-subtareas-en-clasificacion/
├── plan.md              # Este archivo
├── research.md          # Fase 0 — decisiones (ubicación/formato del campo, sin cambios de API)
├── data-model.md         # Fase 1 — confirma que no hay cambios de esquema/tipos
├── quickstart.md        # Fase 1 — validación manual end-to-end
└── tasks.md             # Fase 2 (/speckit-tasks — no generado por este comando)
```

No se genera `contracts/` — esta feature no agrega ni modifica ningún endpoint (Decisión 1 de
`research.md`).

### Source Code (repository root)

```text
frontend/
└── src/pages/TicketDetailPage.tsx   # Card "Clasificación": nuevo Descriptions.Item "Subtareas",
                                     #   junto al ítem "Tarea Padre" agregado en spec 036
```

**Structure Decision**: Un único archivo tocado dentro de la estructura frontend ya vigente
(`frontend/src/pages/`). No se crean directorios ni componentes nuevos — se reutiliza
`Descriptions.Item` y `Button type="link"` ya usados en la misma Card para "Registro
relacionado", "Referenciado por" y "Tarea Padre".

## Complexity Tracking

> No aplica — Constitution Check sin violaciones.
