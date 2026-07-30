---

description: "Task list for 035-cascada-links-catalogos-cliente"
---

# Tasks: Selección en Cascada, Hipervínculos, Edición de Catálogos y Layout de Cliente

**Input**: Design documents from `/specs/035-cascada-links-catalogos-cliente/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/catalogs-rename.md](contracts/catalogs-rename.md), [quickstart.md](quickstart.md)

**Tests**: incluidos de forma acotada (Principio VII — solo el endpoint nuevo y la extensión de `sort`; sin suite de frontend, sin más de 5-10 registros por test).

**Organización**: por historia de usuario. US1/US2/US3 comparten `frontend/src/pages/TicketsPage.tsx` (regiones distintas del archivo) — no son parallel-safe entre sí a pesar de ser independientes en valor; ejecutar en el orden de fases indicado.

## Path Conventions

Web app existente: `backend/{domain,infra,api}/`, `frontend/src/{components,services,pages,types}/` (ver Project Structure de [plan.md](plan.md)).

---

## Phase 1: Setup

No aplica — sin dependencias nuevas (Principio V), sin estructura de proyecto nueva. Se reutiliza el branch/directorio de spec `035-cascada-links-catalogos-cliente` ya creado.

## Phase 2: Foundational

No aplica — ninguna historia depende de infraestructura compartida nueva (sin migraciones, sin modelos nuevos). Cada historia puede iniciar directamente.

---

## Phase 3: User Story 1 - Selección en cascada Cliente → Proyecto → Encargado en Ticket (Priority: P1) 🎯 MVP

**Goal**: El formulario de Ticket/Tarea captura Cliente→Proyecto→Encargado en cascada filtrada, y el campo Skills vuelve a ser visible para todos los roles internos (editable solo por Coordinador).

**Independent Test**: Abrir "Nuevo ticket", elegir Cliente con ≥2 proyectos → Proyecto se filtra; elegir Proyecto → Encargado se filtra; cambiar Cliente limpia Proyecto/Encargado; el campo Skills aparece (editable o deshabilitado según rol). Repetir con Tipo de registro = Tarea.

### Implementation for User Story 1

- [X] T001 [US1] En `frontend/src/pages/TicketsPage.tsx`, unificar el bloque `projectRequiredFlow ? (...) : (...)` (líneas ~525-570) en un único flujo Cliente→Proyecto→Encargado: Cliente como primer `Form.Item` (`required`, habilitado, `options={clients...}`), Proyecto filtrado por `selectedClientId` (reutilizar `projects` ya filtrado del branch `else` existente) y marcado `required` (regla OBS-0045 se conserva), Encargado filtrado por `selectedProjectId` (reutilizar lógica de `contacts` ya existente)
- [X] T002 [US1] En `frontend/src/pages/TicketsPage.tsx`, ajustar el `onValuesChange`/estado (`selectedClientId`, `selectedProjectId`) para limpiar `project_id`+`client_contact_id` al cambiar `client_id`, y limpiar `client_contact_id` al cambiar `project_id` (verificar que la lógica ya existente del branch `else` cubre ambos casos; extenderla si solo cubría el caso Tarea)
- [X] T003 [US1] En `frontend/src/pages/TicketsPage.tsx`, eliminar el `Select disabled` de Cliente auto-derivado (antiguo flujo "Proyecto primero") y el bloque de SLA aplicable (`Descriptions` de "Nivel de servicio") pasa a depender de `selectedProjectId` del nuevo flujo único (sin cambiar su contenido)
- [X] T004 [US1] En `frontend/src/pages/TicketsPage.tsx` (~línea 614), quitar el guard `canManageSkills &&` que oculta por completo el `Form.Item name="skill_ids"`; renderizarlo siempre y pasar `disabled={!canManageSkills}` al `Select`
- [X] T005 [US1] Verificación manual contra Docker real siguiendo `quickstart.md` sección US1 (crear Ticket y Tarea vía cascada, ≤10 registros de prueba, sin tocar clientes semilla reales)

**Checkpoint**: Cascada y Skills funcionando de punta a punta para Ticket y Tarea.

---

## Phase 4: User Story 2 - Hipervínculos a Ticket/Tarea desde cualquier listado (Priority: P1)

**Goal**: Todo código de ticket/tarea en listas/tablero es clicable y navega al detalle, preservando filtros/orden al volver.

**Independent Test**: Clic en el código desde Tickets, Kanban y Mis Tareas navega al detalle sin recargar filtros; "atrás" del navegador conserva la lista previa.

### Implementation for User Story 2

- [X] T006 [P] [US2] En `frontend/src/pages/TicketsPage.tsx` (columna "Número", ~línea 363), reemplazar el `<span>` por `<a onClick={() => navigate(...)}>` con el mismo patrón `state: { from: { pathname: '/tickets', label: 'Tickets' } }` ya usado en la columna "Acciones"
- [X] T007 [P] [US2] En `frontend/src/pages/MyTasksPage.tsx` (columna "Número", ~línea 74), aplicar el mismo patrón `<a onClick={() => navigate(...)}>` con `state: { from: { pathname: '/my-tasks', label: 'Mis tareas' } }`
- [X] T008 [P] [US2] En `frontend/src/pages/KanbanPage.tsx`, envolver el código de ticket dentro de la tarjeta con un `<a>`/`onClick` que llama `navigate(...)` con `e.stopPropagation()`, sin interferir con el `onClick` de la tarjeta (~línea 295) ni con el drag-and-drop de `@hello-pangea/dnd`
- [X] T009 [US2] Verificación manual contra Docker real: TK-000137 clicado en Tickets navegó a `/tickets/{id}` (confirmado por `window.location.href`) y "atrás" restauró la lista; código verificado como `<a>` en el DOM en Kanban y Mis Tareas (mismo patrón, sin poder ejercitar el clic en Mis Tareas por falta de tareas asignadas a los usuarios semilla probados — Panel de Asignación ya funcionaba antes de esta feature)

**Checkpoint**: Todos los códigos de ticket/tarea en listas y tablero son clicables.

---

## Phase 5: User Story 3 - Ordenamiento explícito en tablas y listas de tickets/tareas (Priority: P2)

**Goal**: El usuario puede ordenar Tickets/Mis Tareas por fecha, prioridad, código o estado (asc/desc), combinable con los filtros existentes.

**Independent Test**: Aplicar cada uno de los 4 criterios en ambos sentidos y verificar que el orden de filas cambia sin perder los filtros activos; la request a `GET /api/tickets` incluye `sort=<valor>`.

### Tests for User Story 3

- [X] T010 [P] [US3] Test acotado (≤10 tickets de prueba) en `backend/tests/api/test_tickets_crud.py` para `GET /api/tickets?sort=-status`, `sort=code` y `sort=-code`, confirmando el orden esperado de `ticket_number`/`status`

### Implementation for User Story 3

- [X] T011 [US3] En `backend/infra/repositories/ticket_repo.py`, agregar a `_SORTS` (línea ~23) las claves `"-status": (TicketModel.status.desc(),)`, `"code": (TicketModel.ticket_number.asc(),)`, `"-code": (TicketModel.ticket_number.desc(),)`
- [X] T012 [P] [US3] En `backend/api/routes/tickets.py` (línea ~676), actualizar la descripción `@ns.doc` del parámetro `sort` para listar los 3 valores nuevos
- [X] T013 [US3] En `frontend/src/components/tickets/SortIndicator.tsx`, reemplazar el `Tag` fijo por un `<Select>` controlado (opciones: Fecha ↑/↓, Prioridad ↑/↓, Código ↑/↓, Estado ↑/↓) que recibe `value`/`onChange` por props (deja de ser un componente sin estado)
- [X] T014 [US3] En `frontend/src/pages/TicketsPage.tsx`, agregar estado local `sort` (default `'urgency'`), pasarlo a `ticketService.list({ ..., sort })` y conectar el `SortIndicator` actualizado (T013) a ese estado, sin alterar los filtros existentes
- [X] T015 [US3] En `frontend/src/pages/MyTasksPage.tsx`, replicar T014 (estado `sort` local + `SortIndicator` actualizado)
- [X] T016 [US3] Verificación manual: confirmar en Network que `GET /api/tickets` incluye `sort=` correcto para cada combinación y que `status`/`client_id`/etc. activos se mantienen

**Checkpoint**: Ordenamiento explícito operativo en Tickets y Mis Tareas.

---

## Phase 6: User Story 5 - Editar nombre en pantallas de Catálogos (Priority: P2)

**Goal**: Los catálogos genéricos (Herramientas, Procesos, Tipos de resolución, Tipos de registro, Equipos, Tipos de acceso) permiten editar el nombre de un registro existente sin anularlo.

**Independent Test**: Editar el nombre de un registro, recargar y confirmar que persiste; confirmar que una referencia existente (ej. un ticket con ese `tool_id`) muestra el nombre actualizado; un nombre duplicado es rechazado.

### Tests for User Story 5

- [X] T017 [P] [US5] Test acotado (≤5 registros) en `backend/tests/api/test_teams_catalog.py` (o archivo nuevo `test_catalogs_rename.py`) para `PATCH /api/catalogs/teams/{id}` — éxito (200, nombre actualizado), nombre duplicado (409 `name_duplicate`), nombre vacío (400), catálogo/id inexistente (404)

### Implementation for User Story 5

- [X] T018 [US5] En `backend/infra/repositories/catalog_repo.py`, agregar `CatalogRepository.rename(catalog_id: uuid.UUID, name: str) -> dict | None` (análogo a `set_active`: `get`, `model.name = name`, `commit`, `refresh`, `to_dict()`)
- [X] T019 [US5] En `backend/api/routes/catalogs.py`, agregar la clase `CatalogRename` con `@ns.route("/<string:catalog>/<string:item_id>")` y método `patch` gateado por `@require_permission("catalogs", "create")` (reutilizado, ver research.md Decisión 6): valida `catalog`, `item_id`, `name` no vacío, chequea duplicado vía `get_by_name` (igual que `POST`) antes de llamar a `rename`, responde 200/400/404/409 según `contracts/catalogs-rename.md`
- [X] T020 [P] [US5] En `frontend/src/services/catalogService.ts`, agregar `rename: (catalog: CatalogName, id: string, name: string) => apiClient.patch<CatalogItem>(\`/api/catalogs/${catalog}/${id}\`, { name }).then(r => r.data)`
- [X] T021 [US5] En `frontend/src/pages/CatalogsPage.tsx` (`CatalogCard`), agregar botón "Editar" (ícono lápiz, gateado por `canCreate` — mismo permiso reutilizado) que abre un modal de un campo `name` (patrón de `SkillsPage.tsx`), llama a `catalogService.rename(...)` y recarga (`load()`) al guardar; mostrar el mensaje de error del backend en caso de nombre duplicado
- [X] T022 [US5] Verificación manual siguiendo `quickstart.md` sección US5 (editar, recargar, verificar referencia existente, probar duplicado)

**Checkpoint**: Edición de nombre disponible en los 6 catálogos genéricos.

---

## Phase 7: User Story 4 - Layout horizontal ampliado en Detalle del Cliente (Priority: P3)

**Goal**: El Modal "Detalle del cliente" distribuye información general, proyectos y métricas en columnas en pantallas anchas, apilando de forma legible en ventanas angostas.

**Independent Test**: Abrir el detalle de un cliente con varios proyectos en una ventana de escritorio ancha (columnas visibles) y en una ventana angosta (apilado legible).

### Implementation for User Story 4

- [X] T023 [US4] En `frontend/src/pages/ClientsPage.tsx` (línea ~382), ampliar `width` del `Modal` "Detalle del cliente" (ej. `1200` o `'90vw'` cuando `selectedDetail` existe)
- [X] T024 [US4] En `frontend/src/pages/ClientsPage.tsx`, reorganizar el contenido de la(s) pestaña(s) con datos generales/proyectos/métricas usando `Row`/`Col` (`xs={24}` para apilar en angosto, `md`/`lg` para columnas en ancho), sin cambiar los datos mostrados ni los `Tabs` existentes
- [X] T025 [US4] Verificación manual: abrir el detalle en una resolución de escritorio estándar (≥1366px) y en una ventana angosta, confirmar layout en columnas y apilado responsivo respectivamente

**Checkpoint**: Detalle del Cliente con layout horizontal ampliado.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T026 [P] Ejecutar `tsc -b` en `frontend/` y confirmar cero errores tras los cambios de US1-US4
- [X] T027 Ejecutar `pytest` acotado a los archivos tocados (`backend/tests/api/test_tickets_crud.py`, `backend/tests/api/test_teams_catalog.py` o `test_catalogs_rename.py`) — sin correr la suite completa (Principio VII)
- [X] T028 Recorrer `quickstart.md` completo contra Docker real y actualizar el `CLAUDE.md` (bloque "Active feature") con el resultado de la validación end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: no aplica (ver Phase 1-2)
- **US1 (Phase 3)**: sin dependencias de otras historias — MVP
- **US2 (Phase 4)**: sin dependencias funcionales de US1, pero comparte `TicketsPage.tsx` — ejecutar después de US1 para evitar conflictos de edición del mismo archivo
- **US3 (Phase 5)**: idem — comparte `TicketsPage.tsx`/`MyTasksPage.tsx` con US1/US2; ejecutar después
- **US5 (Phase 6)**: independiente (archivos propios: `catalogs.py`, `catalog_repo.py`, `CatalogsPage.tsx`) — puede ejecutarse en paralelo a US1/US2/US3 por un desarrollador distinto
- **US4 (Phase 7)**: independiente (`ClientsPage.tsx` propio) — puede ejecutarse en paralelo a cualquier otra historia
- **Polish (Phase 8)**: depende de todas las historias que se decida entregar

### Parallel Opportunities

- US5 (Phase 6) y US4 (Phase 7) pueden trabajarse en paralelo entre sí y en paralelo a US1→US2→US3 (archivos disjuntos)
- Dentro de US2: T006/T007/T008 son `[P]` (archivos distintos)
- Dentro de US3: T010/T012 son `[P]`; T011 (backend `_SORTS`) debe completarse antes de que T013-T015 (frontend) puedan verificarse end-to-end, aunque el código de UI puede escribirse en paralelo
- Dentro de US5: T017/T020 son `[P]`; T018 antes de T019 (mismo archivo backend, dependencia real)

---

## Implementation Strategy

### MVP First

1. Phase 3 (US1) — cascada + Skills restaurado. Validar independientemente.
2. Phase 4 (US2) — hipervínculos. Validar.
3. Phase 5 (US3) — ordenamiento. Validar.
4. Phase 6 (US5) y Phase 7 (US4) — pueden intercalarse o hacerse en paralelo por ser independientes de archivo.
5. Phase 8 — polish, `tsc -b`, pytest acotado, actualización de `CLAUDE.md`.

### Incremental Delivery

Cada historia es un incremento demostrable por sí solo (ver "Independent Test" de cada fase); no es necesario completar las 5 para tener valor entregable.
