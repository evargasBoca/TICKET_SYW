---

description: "Task list template for feature implementation"
---

# Tasks: Cierre de OBS-0042/OBS-0043 (Backlog UAT ITER-007)

**Input**: Design documents from `/specs/030-cierre-obs-0042-0043/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/api-changes.md](./contracts/api-changes.md), [quickstart.md](./quickstart.md)

**Tests**: Se incluye una tarea de test de API backend (pytest) para el cambio de serialización de `SlaRule`, ultra-limitada (Constitución Principio VII — extiende el archivo existente, sin insertar más de 5-10 registros de prueba). OBS-0042 es un cambio puramente visual de frontend; no hay framework de test de frontend configurado en este repo (`frontend/package.json` no tiene `vitest`/`@testing-library`), por lo que su verificación es manual contra Docker vía `quickstart.md`.

**Organization**: Tareas agrupadas por User Story (spec.md) para permitir implementación y prueba independiente de cada una.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: A qué User Story pertenece (US1, US2)
- Cada tarea incluye ruta de archivo exacta

## Path Conventions

Web app existente: `backend/` (Flask, 3 capas: `domain/`, `infra/`, `api/`) + `frontend/src/` (React). Ver "Project Structure" en `plan.md`.

---

## Phase 1: Setup

**Purpose**: Confirmar el entorno y los datos de prueba antes de tocar código.

- [X] T001 Levantar el stack Docker de desarrollo y confirmar que existen al menos dos clientes con un proyecto del mismo nombre (Aris y Vaxthera, ambos con proyecto "Soporte", ya sembrados por `backend/scripts/seed_clients_aris_vaxthera.py`), y un ticket de prueba con historial de comentarios extenso para reproducir OBS-0042 — ver "Prerrequisitos" en [quickstart.md](./quickstart.md) — Docker ya levantado (`sywork_*` Up); confirmado vía SQL que Aris/Vaxthera tienen proyecto "Soporte"; TK-000001 usado como ticket de prueba (se le agregaron 7 comentarios vía API para forzar el overflow del historial)

**Checkpoint**: Entorno listo para desarrollar y verificar manualmente cada historia.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evaluar prerequisitos compartidos entre historias.

Ninguno: OBS-0042 (frontend, `TicketDetailPage.tsx`) y OBS-0043 (backend `sla_rules.py` + frontend `SlaRulesPage.tsx`/`SlaRuleForm.tsx`) no comparten archivos ni lógica — son completamente independientes entre sí (ver `plan.md` — "Project Structure"). Sin tareas bloqueantes en esta fase.

**Checkpoint**: Ambas historias pueden empezar de inmediato, en paralelo si hay más de un desarrollador.

---

## Phase 3: User Story 1 - Acceso permanente a las acciones del ticket (OBS-0042, Priority: P1) 🎯 MVP

**Goal**: Reorganizar el Detalle del Ticket para que la caja de nuevo comentario y las acciones de cambio de estado sean siempre accesibles, sin depender del largo del historial de comentarios.

**Independent Test**: Abrir un ticket con historial de comentarios extenso y verificar que "Comentarios y acciones" está en la columna derecha, permanece visible al hacer scroll, y el historial tiene su propio scroll interno acotado (ver Fase "OBS-0042" de `quickstart.md`).

### Implementation for User Story 1

- [X] T002 [US1] En `frontend/src/pages/TicketDetailPage.tsx`, mover la `Card` `"Comentarios y acciones"` (contiene `TaskStatusChanger` para Tareas, `CommentThread` y `CommentComposer`) de la columna principal (`Col xs={24} lg={14}`) a la columna lateral (`Col xs={24} lg={10}`), y mover la `Card title="Clasificación"` de la columna lateral a la columna principal, en el lugar donde antes estaba "Comentarios y acciones" — mantener el orden relativo del resto de Cards de cada columna (Descripción/Registros de tiempo/Historial de estados/Reasignaciones en la principal; SLA/Focus Room/Subtareas en la lateral)
- [X] T003 [US1] En la `Card` "Comentarios y acciones" ya reubicada (`frontend/src/pages/TicketDetailPage.tsx`), envolver el `<CommentThread ... />` en un `<div>` con `maxHeight` fijo (ej. `420px`) y `overflowY: 'auto'`, dejando `TaskStatusChanger`/`CommentComposer` fuera de ese contenedor (siempre visibles, sin scroll propio) (depende de T002)
- [X] T004 [US1] Aplicar `position: 'sticky'` y un `top` acorde al espaciado ya usado en la página a la `Card` "Comentarios y acciones" reubicada en `frontend/src/pages/TicketDetailPage.tsx`, para que permanezca visible al desplazarse por el resto del detalle del ticket en pantallas `lg` y superiores (depende de T002)
- [X] T005 [US1] Verificación manual en Docker real: abrir el ticket de prueba con historial extenso (de T001), confirmar los 5 puntos de la Fase "OBS-0042" de `quickstart.md` (ubicación de columnas, visibilidad fija de acciones, scroll interno del historial, responsive xs/lg sin overlaps) (depende de T002, T003, T004) — **verificado con Docker real** (TK-000001 + 7 comentarios de prueba agregados vía API para forzar overflow): `Clasificación` a la izquierda (left=272, igual que Descripción), `Comentarios y acciones` a la derecha (left=825.6, igual que SLA) con `position: sticky; top: 16px` confirmado por `getComputedStyle`; el contenedor del historial mide `scrollHeight=814` vs `clientHeight=420` (scroll interno real); tras `scrollTo(0,900)` el composer sigue visible en viewport (`top=504`, dentro de 0-720). Responsivo xs/lg no re-verificado con métricas fiables (el emulador de viewport móvil de esta sesión de browser devolvió medidas inconsistentes, ajeno al código) — el patrón `Col xs={24} lg={14}`/`lg={10}` no se modificó, solo se intercambió qué Card vive en cada columna, por lo que el comportamiento responsivo es el mismo ya usado en el resto de la página

**Checkpoint**: User Story 1 funcional y verificable de forma independiente (SC-001, SC-002, SC-003).

---

## Phase 4: User Story 2 - Distinguir proyectos homónimos en SLA Configurable (OBS-0043, Priority: P1)

**Goal**: Mostrar el cliente de cada proyecto en el filtro, el formulario y la tabla de SLA Configurable, para distinguir proyectos con el mismo nombre de distintos clientes.

**Independent Test**: Con Aris y Vaxthera (ambos con proyecto "Soporte") sembrados, verificar que el filtro, el formulario y la tabla de SLA Configurable distinguen sin ambigüedad a qué cliente pertenece cada "Soporte" (ver Fase "OBS-0043" de `quickstart.md`).

### Tests for User Story 2

- [X] T006 [P] [US2] Test de API: extender `backend/tests/api/test_sla_rules.py` (fixture `sla_project`/`ticket_client` ya existente) para verificar que la respuesta de `POST /api/sla-rules` incluye `client_id` == `ticket_client["id"]` y `client_name` == `ticket_client["name"]` — debe fallar antes de T010 (campos ausentes en el payload actual)

### Implementation for User Story 2

- [X] T007 [P] [US2] Agregar `client_id: string | null` y `client_name: string | null` a la interfaz `SlaRule` en `frontend/src/types/sla.ts`
- [X] T008 [P] [US2] En `frontend/src/pages/SlaRulesPage.tsx`, cambiar el `label` de las opciones del `Select` "Filtrar por proyecto" de `p.name` a `` `${p.client_name} — ${p.name}` `` (usa `ProjectListItem.client_name`, ya existente — sin cambios de backend)
- [X] T009 [P] [US2] En `frontend/src/components/sla/SlaRuleForm.tsx`, cambiar el `label` de las opciones del `Select` "Proyecto" de `p.name` a `` `${p.client_name} — ${p.name}` `` (misma fuente que T008 — sin cambios de backend)
- [X] T010 [US2] En `backend/api/routes/sla_rules.py::_serialize()`, resolver el `Client` del proyecto vía `ClientRepository(db).get_by_id(project.client_id)` (cuando `project` exista) y agregar `client_id`/`client_name` al dict devuelto; actualizar el modelo Swagger `_sla_rule_out` con los 2 campos nuevos (`fields.String()`) — hace pasar el test de T006 (depende de T006)
- [X] T011 [US2] En `frontend/src/pages/SlaRulesPage.tsx`, agregar una columna `"Cliente"` (`dataIndex: 'client_name'`) a `columns`, ubicada antes o junto a la columna `"Proyecto"` de la tabla de reglas de SLA (depende de T007, T010)
- [X] T012 [US2] Verificación manual en Docker real: abrir Maestros > SLA Configurable con Aris/Vaxthera sembrados, confirmar los 4 puntos de la Fase "OBS-0043" de `quickstart.md` (filtro, formulario, columna de tabla) (depende de T008, T009, T011) — **verificado con Docker real**: tabla muestra columna "Cliente" correcta para las 4 reglas de Aris y para los proyectos de prueba de pytest; API `/api/projects` confirma `Aris`/`Vaxthera` ambos con proyecto "Soporte"; dropdown "Filtrar por proyecto" y el `Select` de "Proyecto" en el formulario "Nueva regla de SLA" muestran el formato `Cliente — Proyecto` (ej. "Aris — Evolutivo", "Aris — Preventa")

**Checkpoint**: User Story 2 funcional y verificable de forma independiente (SC-004).

---

## Phase 5: Polish & Trazabilidad UAT

**Purpose**: Cerrar el ciclo con el framework UAT y confirmar alcance de pruebas.

- [X] T013 Ejecutar únicamente `backend/tests/api/test_sla_rules.py` (pytest acotado al archivo modificado — Principio VII, prohibido correr la suite completa) y confirmar que pasa, incluyendo el test nuevo de T006 (depende de T010) — **13 passed** (incluye `test_create_sla_rule_includes_client`, `test_list_sla_rules_includes_client`)
- [X] T014 Actualizar `UAT/02_Backlog/BACKLOG.md`: cambiar el `Estado` de `OBS-0042` y `OBS-0043` de `Abierta` a `Lista para Validar`, siguiendo `UAT/CONVENTIONS.md` (FR-009) — confirmar que `UAT/01_Iterations/ITER-007/ITER-007.md` no se edita en su contenido narrativo (depende de T005, T012, T013) — hecho; `ITER-007.md` no tocado en esta fase (verificado con `git diff`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato.
- **Foundational (Phase 2)**: Sin tareas — no bloquea nada.
- **User Story 1 (Phase 3)**: Depende solo de Setup (T001, para tener el ticket de prueba). Independiente de User Story 2.
- **User Story 2 (Phase 4)**: Depende solo de Setup (T001, para tener Aris/Vaxthera sembrados). Independiente de User Story 1.
- **Polish (Phase 5)**: Depende de que ambas historias estén verificadas (T005, T012) y del test de backend (T013).

### User Story Dependencies

- **User Story 1 (OBS-0042, P1)**: Sin dependencias de User Story 2 — 100% frontend, archivo único (`TicketDetailPage.tsx`).
- **User Story 2 (OBS-0043, P1)**: Sin dependencias de User Story 1 — backend (`sla_rules.py`) + frontend (`SlaRulesPage.tsx`, `SlaRuleForm.tsx`, `types/sla.ts`).

### Dentro de cada User Story

- US1: T002 (mover Cards) antes de T003 (scroll interno) y T004 (sticky) — mismo archivo, cambios secuenciales sobre el JSX recién movido. T005 (verificación) al final.
- US2: T006 (test) antes de T010 (implementación backend que lo hace pasar). T007/T008/T009 son independientes entre sí y de T006/T010 (archivos distintos). T011 (columna de tabla) depende de T007 (tipo) y T010 (dato real en el payload). T012 (verificación) al final.

### Parallel Opportunities

- T006, T007, T008, T009 pueden ejecutarse en paralelo (archivos distintos, sin dependencias entre ellas).
- User Story 1 completa (T002-T005) puede desarrollarse en paralelo con User Story 2 completa (T006-T012) si hay dos desarrolladores, dado que no comparten archivos.

---

## Parallel Example: User Story 2

```bash
# Lanzar juntas (archivos distintos, sin dependencias entre sí):
Task: "Test de API: client_id/client_name en POST /api/sla-rules — backend/tests/api/test_sla_rules.py"
Task: "Agregar client_id/client_name a la interfaz SlaRule — frontend/src/types/sla.ts"
Task: "Cliente + proyecto en selector 'Filtrar por proyecto' — frontend/src/pages/SlaRulesPage.tsx"
Task: "Cliente + proyecto en Select 'Proyecto' del formulario — frontend/src/components/sla/SlaRuleForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup.
2. Completar Phase 3: User Story 1 (OBS-0042).
3. **Detener y validar**: probar User Story 1 de forma independiente contra Docker (Fase "OBS-0042" de `quickstart.md`).
4. Continuar con User Story 2 y Polish para cerrar ambas observaciones del ITER-007.

### Incremental Delivery

1. Setup → entorno y datos de prueba listos.
2. User Story 1 (OBS-0042) → validar independientemente.
3. User Story 2 (OBS-0043) → validar independientemente.
4. Polish → test acotado + actualización de `BACKLOG.md` (cierre de trazabilidad UAT).

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes entre las tareas marcadas.
- [Story] mapea cada tarea a su User Story para trazabilidad con `spec.md`.
- Ninguna tarea de este feature requiere migración Alembic ni dependencias nuevas (Principio V).
- No editar retroactivamente `UAT/01_Iterations/ITER-007/ITER-007.md` — todo cambio de estado va en `UAT/02_Backlog/BACKLOG.md` (T014).
