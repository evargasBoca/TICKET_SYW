---

description: "Task list for Deshabilitación de Usuarios/Cliente y Módulo de Reportes Dinámicos"

---

# Tasks: Deshabilitación de Usuarios/Cliente y Módulo de Reportes Dinámicos (Interactive Grid)

**Input**: Design documents from `/specs/034-usuarios-inactivos-reportes-grid/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/reports-y-client-contacts.md](contracts/reports-y-client-contacts.md), [quickstart.md](quickstart.md)

**Tests**: Solo para agregaciones y exportación a Excel (US4/US5), con dataset mock de 5-10
tickets, por directriz explícita del usuario y Principio VII de la constitución (prohibido correr
la suite completa; nada de tests masivos en el resto del feature).

**Alcance (Principio VII)**: Únicamente los archivos listados abajo. Prohibido tocar `TeamPage.tsx`,
`backend/api/routes/users.py` u otros módulos no listados.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece (US1-US6, ver spec.md)

---

## Phase 1: Setup

**Purpose**: Preparar la dependencia nueva y la migración base para el módulo de Reportes

- [X] T001 Agregar `openpyxl` a `backend/requirements.txt` (research.md Decisión 4)
- [X] T002 Crear migración Alembic `backend/infra/migrations/versions/050_report_saved_views_and_permission.py`: tabla `report_saved_views` (`id`, `user_id` FK→`users.id` ON DELETE CASCADE, `name`, `config` JSONB, `created_at`, `updated_at`, `UNIQUE(user_id, name)`) + permiso `reports:view` otorgado a los roles Admin, Coordinador y QM (ver data-model.md, research.md Decisiones 7-8; mismo patrón de seed de permiso ad-hoc que la migración `048_tool_processes_manage_skills.py`)

**Checkpoint**: Dependencia y esquema listos para el módulo de Reportes.

---

## Phase 2: Foundational (Blocking Prerequisites para US2-US6)

**Purpose**: Base de datos de reporte reutilizable por todas las historias del módulo de
Reportes. **US1 (deshabilitar Usuario/cliente) NO depende de esta fase** — es un track
independiente que puede implementarse en paralelo o antes.

**⚠️ CRITICAL**: Ninguna historia US2-US6 puede empezar hasta que esta fase esté completa.

- [X] T003 [P] Crear `backend/infra/models/report_view_model.py` con `ReportSavedViewModel` (tabla `report_saved_views`, mapea a/desde una entidad de dominio `ReportSavedView`)
- [X] T004 [P] Crear `backend/infra/repositories/report_repo.py` con la consulta base de "Fila de Reporte de Ticket" (join `tickets`+`clients`+`projects`+`resources`+`catalog_tools`+`catalog_processes`+`skills`+`SUM(work_sessions.duration_minutes)` agrupado por ticket) y filtros combinables por rango de fechas/`client_id`/`project_id`/`assignee_id` (ver data-model.md); sin lógica de agregación todavía (eso es US4)
- [X] T005 Crear namespace `backend/api/routes/reports.py` (Flask-RESTX) con el modelo Swagger de la fila de reporte y el endpoint `GET /api/reports/tickets` (paginado, sin `aggregates` todavía) gateado por `require_permission("reports", "view")`; registrar el namespace en `backend/app.py`
- [X] T006 [P] Crear `frontend/src/types/report.ts` con los tipos `ReportRow`, `ReportFilters`, `ReportColumnConfig`, `ReportSavedView`
- [X] T007 [P] Crear `frontend/src/services/reportService.ts` con `listTickets(filters, page, pageSize)` contra `GET /api/reports/tickets`
- [X] T008 Agregar entrada "Reportes" a `frontend/src/config/navigation.tsx` gateada por el módulo `reports` (visible solo con permiso `reports:view`)

**Checkpoint**: Endpoint base de reporte y navegación listos — US2 puede completarse.

---

## Phase 3: User Story 1 - Deshabilitar el acceso de un Usuario/cliente (Priority: P1) 🎯 MVP

**Goal**: Un Coordinador/Admin puede activar/desactivar una cuenta de rol Usuario/cliente desde
su pantalla de administración, sin perder historial ni afectar el login de cuentas activas.

**Independent Test**: Deshabilitar un Usuario/cliente de prueba, verificar que su login se
rechaza y que no aparece en selectores de asignación nuevos, y reactivarlo para confirmar que
recupera el acceso (quickstart.md, sección US1).

### Implementation for User Story 1

- [X] T009 [US1] Agregar `active` (boolean, derivado de `users.active`) a la respuesta de `GET /api/client-contacts` y aceptar `active` como filtro opcional de query en `backend/infra/repositories/client_contact_repo.py` (join a `UserModel`) y `backend/api/routes/client_contacts.py` (`_to_dict`, `_client_contact_out`, parseo de query params)
- [X] T010 [US1] Implementar `PATCH /api/client-contacts/{contact_id}/active` en `backend/api/routes/client_contacts.py`, gateado por `require_permission("client_contacts", "manage")`, llamando a `UserRepository(db).set_active(user_id, active)`; responder `409 already_active`/`already_inactive` si no hay cambio real de estado (contracts/reports-y-client-contacts.md)
- [X] T011 [US1] Agregar validación `contact_inactive` (409) en `POST /api/client-contacts/{contact_id}/projects` (`backend/api/routes/client_contacts.py`) cuando el Usuario/cliente destino esté `active: false`
- [X] T012 [P] [US1] Agregar `active: boolean` a la interfaz `ClientContact` en `frontend/src/types/clientContact.ts` y método `setActive(id, active)` en `frontend/src/services/clientContactService.ts`
- [X] T013 [US1] Agregar columna "Estado" (Tag Activo/Inactivo) y acción de activar/desactivar (reutilizando el patrón `ConfirmationModal` ya usado en `TeamPage.tsx`) en `frontend/src/pages/ClientContactsPage.tsx`
- [X] T014 [US1] Pasar `active: true` por defecto en el/los selector(es) de solicitante/encargado que consumen `clientContactService.list(...)` al crear/editar un Ticket (mismo patrón ya usado con `clientService.list({active: true})`), para excluir cuentas deshabilitadas de nuevas asignaciones (FR-003)

**Checkpoint**: US1 completamente funcional y probable de forma independiente — MVP entregable.

---

## Phase 4: User Story 2 - Consultar el Reporte de Tickets con filtros básicos (Priority: P1)

**Goal**: Ver el grid de Reportes con las métricas clave, filtrable por fecha/Cliente/Proyecto/
Encargado.

**Independent Test**: Abrir "Reportes", aplicar filtros combinados y verificar que la tabla
muestra solo los tickets que los cumplen (quickstart.md, sección US2).

### Implementation for User Story 2

- [X] T015 [US2] Completar los parámetros de filtro (`date_from`, `date_to`, `client_id`, `project_id`, `assignee_id`) en `GET /api/reports/tickets` (`backend/api/routes/reports.py`), con validación `400 validation_error` si `date_from` > `date_to`
- [X] T016 [US2] Crear `frontend/src/pages/ReportsPage.tsx` con tabla Ant Design mostrando las columnas mínimas de FR-008 y controles de filtro (RangePicker + Selects de Cliente/Proyecto/Encargado)
- [X] T017 [US2] Verificar/ajustar el guard de permiso en el router del frontend para que `/reportes` niegue el acceso sin `reports:view` (mismo patrón de rutas protegidas ya existente)

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Phase 5: User Story 3 - Personalizar columnas del reporte (Priority: P2)

**Goal**: Mostrar, ocultar y reordenar columnas del grid.

**Independent Test**: Ocultar dos columnas y reordenar el resto; la tabla refleja el cambio sin
perder el filtro aplicado (quickstart.md, sección US3).

### Implementation for User Story 3

- [X] T018 [US3] Crear componente de selector de columnas (Popover + `Checkbox.Group` + `@hello-pangea/dnd` para reordenar) en `frontend/src/pages/ReportsPage.tsx` o `frontend/src/components/reports/ColumnPicker.tsx`
- [X] T019 [US3] Persistir el estado de columnas visibles/orden en memoria de la página (`ReportsPage.tsx`) y aplicarlo a las columnas de la `Table` de Ant Design

**Checkpoint**: US1-US3 funcionan de forma independiente.

---

## Phase 6: User Story 4 - Aplicar agregaciones y sumatorias (Priority: P2)

**Goal**: Sumar/promediar/contar columnas numéricas o de tiempo sobre el conjunto filtrado
completo.

**Independent Test**: Aplicar "Suma" sobre tiempo total registrado y verificar el total contra
todas las filas filtradas, no solo la página visible (quickstart.md, sección US4).

### Tests for User Story 4 (dataset mock de 5-10 tickets, Principio VII)

- [X] T020 [P] [US4] Test unitario de `backend/domain/services/report_aggregation_service.py` (sum/avg/count sobre listas de valores, incluyendo columna no numérica rechazada) en `backend/tests/domain/test_report_aggregation_service.py` con datos in-memory (sin BD)
- [X] T021 [P] [US4] Test de `GET /api/reports/tickets?aggregate=...` en `backend/tests/api/test_reports_aggregate.py`, insertando exactamente 5-10 tickets mock

### Implementation for User Story 4

- [X] T022 [US4] Crear `backend/domain/services/report_aggregation_service.py` (Capa 1, puro): recibe listas de valores + función (`sum`/`avg`/`count`) y devuelve el resultado; rechaza columnas no numéricas (FR-012)
- [X] T023 [US4] Agregar soporte de `aggregate=campo:funcion` (repetible) y el bloque `aggregates` (calculado sobre **todo** el conjunto filtrado, no solo la página) a la respuesta de `GET /api/reports/tickets` en `backend/api/routes/reports.py`, usando T022
- [X] T024 [US4] Agregar UI de selección de función de agregación por columna y fila de totales (`Table.summary` de Ant Design) en `frontend/src/pages/ReportsPage.tsx`

**Checkpoint**: US1-US4 funcionan de forma independiente.

---

## Phase 7: User Story 5 - Exportar el reporte a Excel (Priority: P2)

**Goal**: Exportar la vista actual (columnas visibles, orden, filtros) a `.xlsx`.

**Independent Test**: Exportar con un filtro y una columna oculta; el archivo contiene
exactamente esas columnas/orden/filas (quickstart.md, sección US5).

### Tests for User Story 5 (dataset mock de 5-10 tickets, Principio VII)

- [X] T025 [P] [US5] Test de `GET /api/reports/tickets/export` en `backend/tests/api/test_reports_export.py`: verifica columnas/orden/filas del `.xlsx` generado contra 5-10 tickets mock, y el caso `400 no_data` sin filas

### Implementation for User Story 5

- [X] T026 [US5] Implementar `GET /api/reports/tickets/export` en `backend/api/routes/reports.py`: reutiliza los filtros de `report_repo.py` (sin paginar, conjunto completo), arma el `.xlsx` con `openpyxl` respetando `columns` (claves y orden recibidos), responde `400 no_data` si no hay filas
- [X] T027 [US5] Agregar botón "Exportar a Excel" en `frontend/src/pages/ReportsPage.tsx` que llame a `reportService.exportTickets(...)` (nuevo método en `reportService.ts`) y dispare la descarga del blob recibido

**Checkpoint**: US1-US5 funcionan de forma independiente.

---

## Phase 8: User Story 6 - Guardar y reutilizar una Vista Personalizada (Priority: P3)

**Goal**: Guardar columnas+filtros+agregaciones como una vista nombrada, privada por usuario, y
recargarla.

**Independent Test**: Guardar una vista, salir y volver a entrar, cargarla y verificar que se
restaura idéntica; otro usuario no la ve (quickstart.md, sección US6).

### Implementation for User Story 6

- [X] T028 [US6] Implementar `GET /api/reports/views`, `POST /api/reports/views` (upsert por `(user_id, name)`) y `DELETE /api/reports/views/{view_id}` en `backend/api/routes/reports.py`, usando `ReportSavedViewModel` (T003) — todas acotadas a `g.current_user.id` (FR-014)
- [X] T029 [P] [US6] Agregar `saveView`, `listViews`, `deleteView` a `frontend/src/services/reportService.ts`
- [X] T030 [US6] Agregar UI de guardar/cargar Vista Personalizada (modal de nombre + Select de vistas guardadas) en `frontend/src/pages/ReportsPage.tsx`, serializando/deserializando el `config` (columnas, filtros, agregaciones) definido en data-model.md

**Checkpoint**: Las 6 historias funcionan de forma independiente.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cierre del feature, acotado a lo ya tocado (Principio VII — nada fuera de este
alcance)

- [X] T031 Ejecutar `pytest` solo sobre los archivos nuevos/tocados de este feature (`backend/tests/domain/test_report_aggregation_service.py`, `backend/tests/api/test_reports_aggregate.py`, `backend/tests/api/test_reports_export.py`, y cualquier test ya existente de `client_contacts` tocado) — prohibido correr la suite completa
- [X] T032 Ejecutar `tsc -b` en `frontend/` y corregir errores de tipos si los hay
- [X] T033 Ejecutar la guía de validación manual de `quickstart.md` contra Docker real (las 6 historias) y documentar el resultado
- [X] T034 Actualizar `UAT/02_Backlog/BACKLOG.md` / `CLAUDE.md` con el resumen de la feature implementada (si aplica al flujo de este repo)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup (T002 crea la tabla que usa T003). Bloquea US2-US6.
- **US1 (Phase 3)**: **NO depende de Foundational** (track completamente independiente de
  Reportes) — puede implementarse en paralelo a la Fase 2, o primero como MVP más rápido.
- **US2 (Phase 4)**: depende de Foundational (T003-T008).
- **US3-US6 (Phases 5-8)**: dependen de Foundational; US3/US4/US5 son independientes entre sí
  (todas parten del grid de US2); US6 depende conceptualmente de que existan columnas/filtros/
  agregaciones que guardar, pero su implementación (CRUD de vistas) es un archivo/endpoint propio
  y no bloquea ni es bloqueada técnicamente por T018-T027.
- **Polish (Phase 9)**: depende de todas las historias que se decida entregar.

### Parallel Opportunities

- T001 y T002 en paralelo (archivos distintos).
- T003, T004, T006, T007 en paralelo dentro de Foundational (T005 y T008 dependen de que existan T004/T006-T007 respectivamente, por lo que van después).
- US1 completo (T009-T014) puede avanzar en paralelo al resto del equipo trabajando en Foundational/US2+.
- Dentro de US4: T020 y T021 (tests) en paralelo entre sí, antes de T022-T024.
- T025 (test de US5) en paralelo a T020/T021 (US4), son historias independientes.

---

## Parallel Example: User Story 1 (MVP)

```bash
Task: "Agregar active a GET /api/client-contacts y filtro (backend/infra/repositories/client_contact_repo.py, backend/api/routes/client_contacts.py)"
Task: "Agregar active a ClientContact y setActive() (frontend/src/types/clientContact.ts, frontend/src/services/clientContactService.ts)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1 (T001-T002, openpyxl y migración pueden hacerse aunque el MVP sea solo US1 —
   si se quiere el MVP más rápido posible sin Reportes, T002 puede diferirse: US1 no la necesita).
2. Completar Phase 3 (US1) — no depende de Foundational.
3. **Validar** con quickstart.md sección US1.
4. Entregar como incremento independiente antes de tocar Reportes.

### Incremental Delivery

1. US1 (deshabilitar Usuario/cliente) → validar → entregar.
2. Foundational + US2 (grid con filtros) → validar → entregar (base del módulo de Reportes).
3. US3 (columnas) → US4 (agregaciones) → US5 (exportar) → cada una se valida y entrega por
   separado sin romper las anteriores.
4. US6 (vistas guardadas) al final, como mejora de conveniencia.

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes.
- Cada historia debe quedar completable y probable de forma independiente (quickstart.md tiene
  una sección por historia).
- Ningún task de este archivo toca `TeamPage.tsx`, `backend/api/routes/users.py`,
  `backend/api/middleware/*` ni ningún módulo fuera de `client_contacts`/`reports` (Principio VII).
- No insertar más de 5-10 registros de prueba por test (T020, T021, T025).
