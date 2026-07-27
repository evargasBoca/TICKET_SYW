---

description: "Task list template for feature implementation"
---

# Tasks: Ampliación de Accesos y Conexiones del Cliente (OBS-0041)

**Input**: Design documents from `/specs/031-cliente-accesos-ampliado/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/client-access-extended.md](./contracts/client-access-extended.md), [quickstart.md](./quickstart.md)

**Tests**: Se incluye una tarea de test de API backend (pytest) para el CRUD de `client_access_credentials`, ultra-limitada (Constitución Principio VII — no más de 5-10 registros de prueba). El resto de las historias (catálogo, puerto/ambiente, adjunto por acceso) reutiliza endpoints/patrones ya cubiertos por tests existentes de spec 018 y Catálogos; su verificación es manual contra Docker vía `quickstart.md`, igual que el resto del repo para cambios de UI.

**Organization**: Tareas agrupadas por User Story (spec.md) para permitir implementación y prueba independiente de cada una.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: A qué User Story pertenece (US1, US2, US3, US4)
- Cada tarea incluye ruta de archivo exacta

## Path Conventions

Web app existente: `backend/` (Flask, 3 capas: `domain/`, `infra/`, `api/`) + `frontend/src/` (React). Ver "Project Structure" en `plan.md`.

---

## Phase 1: Setup

**Purpose**: Confirmar el entorno y los datos de prueba antes de tocar código.

- [X] T001 Levantar el stack Docker de desarrollo y confirmar que existe al menos un cliente con uno o más `client_access` ya cargados desde spec 018 (con `access_type`/`username`/`password` no nulos), anotando `client_id`/`access_id` para usarlos en el Escenario 1 de [quickstart.md](./quickstart.md) (migración sin pérdida) — Docker ya levantado (`sywork_*` Up); no había `client_access` previos en la BD, así que se creó uno de prueba en Aris vía API (`access_type=vpn`, `username=vpn_test_031`, `password=TestPw031!`, `host=vpn.aris-test.example`) para tener un caso real que migrar

**Checkpoint**: Entorno listo y datos de prueba identificados para validar la migración y las 4 historias.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Esquema de base de datos y modelos compartidos por las 4 User Stories — ninguna historia puede completarse sin esto.

**⚠️ CRITICAL**: Ninguna tarea de User Story puede darse por verificada de punta a punta sin esta fase completa (todas dependen del mismo esquema).

- [X] T002 Migración Alembic `backend/infra/migrations/versions/047_client_access_catalog_credentials.py`: crear `catalog_access_types` (mixin + `color_index`) con semilla de 5 tipos (`VPN`, `Base de datos`, `Servidor / instancia`, `Escritorio remoto`, `Sistema / Integración`); agregar `client_access.access_type_id` (FK, nullable→backfill según mapeo `vpn→VPN`/`system_url→Sistema/Integración`/`remote_desktop→Escritorio remoto`→`NOT NULL`) y `client_access.port` (integer nullable); crear `client_access_credentials` (+ RLS) con migración de datos (cada `client_access` con `username`/`password` no nulos → 1 fila `label='Principal'`, blob cifrado copiado tal cual); agregar `client_access_attachments.client_access_id` (FK nullable) — todo en una sola migración reversible, ver [data-model.md](./data-model.md) "Notas de migración" — aplicada con `alembic upgrade head`; también se relajó `ck_client_access_type`/`access_type NOT NULL` (constraint legacy descubierta en runtime, no documentada en `030_client_access.py` al planificar) a nullable sin CHECK, restaurada en `downgrade()`; verificado por SQL que el seed de 5 tipos, el backfill de `access_type_id` y la migración de la credencial de prueba (T001) a `client_access_credentials` con `label='Principal'` quedaron correctos
- [X] T003 [P] `backend/infra/models/catalog_model.py`: agregar `AccessTypeCatalogModel(_CatalogMixin, Base)` con columna `color_index` (smallint, not null) y registrar `"access-types": AccessTypeCatalogModel` en `CATALOG_MODELS` (depende de T002)
- [X] T004 `backend/infra/repositories/catalog_repo.py`: en `CatalogRepository.create()`, cuando el modelo del catálogo tenga el atributo `color_index` (`hasattr`), calcular `color_index = <count de filas existentes, activas e inactivas> % 8` antes de insertar; sin cambios para los demás catálogos (depende de T003) — verificado vía API: tipos nuevos (APEX, NetSuite) recibieron `color_index` 5 y 6 consecutivos
- [X] T005 `backend/domain/entities/client.py`: `ClientAccess` gana `access_type_id: uuid.UUID` y `port: int | None`; nuevo `@dataclass ClientAccessCredential` (`id`, `client_access_id`, `label`, `username`, `password`, `notes`, `created_at`, `updated_at`) (depende de T002)
- [X] T006 `backend/infra/models/client_model.py`: `ClientAccessModel` gana columnas `access_type_id`/`port` y actualiza `to_entity()`/`from_entity()`; nuevo `ClientAccessCredentialModel` (con `_encrypt`/`_decrypt` ya existentes en el módulo); `ClientAccessAttachmentModel` gana columna `client_access_id` y actualiza `to_entity()`/`from_entity()` (depende de T002, T005)

**Checkpoint**: Esquema y modelos listos — las 4 historias pueden implementarse (en paralelo si hay más de un desarrollador, aunque US1/US3 comparten `ClientAccessModel`/`clients.py`).

---

## Phase 3: User Story 1 - Catálogo administrable de tipos de acceso (Priority: P1) 🎯 MVP

**Goal**: Los tipos de acceso se administran desde Catálogos (con color estable auto-asignado), y los accesos ya existentes conservan un tipo equivalente tras la migración.

**Independent Test**: Agregar un tipo nuevo desde Catálogos y usarlo de inmediato al crear un acceso de cliente; confirmar que los accesos migrados muestran su tipo equivalente (Escenarios 1 y 2 de `quickstart.md`).

### Implementation for User Story 1

- [X] T007 [US1] `backend/infra/repositories/client_repo.py` + `backend/api/routes/clients.py`: actualizar la serialización de `GET/POST/PATCH /api/clients/{id}/access[/{access_id}]` para reemplazar el campo `access_type` (string) por `access_type_id` (UUID) más un objeto de solo lectura embebido `access_type: {id, name, color_index}` resuelto vía join con `catalog_access_types` (depende de T006)
- [X] T008 [US1] `backend/api/routes/clients.py`: validar en creación/edición de acceso que `access_type_id` exista y esté activo en `catalog_access_types`, devolviendo `400 validation_error` si no (depende de T007)
- [X] T009 [P] [US1] `frontend/src/types/client.ts`: `ClientAccessType` pasa de union literal a `string` (UUID); agregar interfaz `AccessTypeCatalogItem` (`id`, `name`, `active`, `color_index`)
- [X] T010 [P] [US1] `frontend/src/services/clientService.ts`: ajustar payloads de acceso para enviar/recibir `access_type_id` en vez de `access_type`; confirmar que el `catalogService` genérico ya soporta `list('access-types')`/`create('access-types', ...)` sin cambios
- [X] T011 [US1] `frontend/src/pages/ClientsPage.tsx`: el selector de "Tipo de acceso" pasa de opciones fijas a un `Select` poblado desde `catalogService.list('access-types')`, mostrando un badge de color derivado de `color_index` (paleta fija de 8 colores en el frontend) (depende de T009, T010) — también se agregó la entrada `'access-types'` a `CATALOGS`/`CATALOG_LABELS`/`CATALOG_COLOR_PALETTE` (`frontend/src/types/catalog.ts`, `CatalogsPage.tsx`) para administrar el catálogo desde Catálogos (FR-001), no descubierto hasta implementar
- [X] T012 [US1] Verificación manual en Docker real: Escenarios 1 y 2 de [quickstart.md](./quickstart.md) — migración sin pérdida de tipo y alta de un tipo nuevo usable de inmediato con color propio y estable (depende de T008, T011) — **verificado con Docker real**: acceso VPN migrado de T001 muestra `access_type.name="VPN"` correctamente resuelto; se crearon los tipos "APEX" (`color_index=5`) y "NetSuite" (`color_index=6`) desde Catálogos y aparecieron de inmediato en el selector de la pestaña Accesos; Catálogos muestra la card "Tipos de acceso (Clientes)" con swatch de color y los 7 tipos (5 semilla + 2 nuevos)

**Checkpoint**: User Story 1 funcional y verificable de forma independiente (FR-001 a FR-004, SC-001, SC-004).

---

## Phase 4: User Story 2 - Credenciales múltiples por acceso (Priority: P1)

**Goal**: Un acceso puede tener cero o más credenciales (usuario/contraseña) sin repetir host/URL, y las credenciales ya cargadas antes del cambio se conservan como la primera credencial migrada.

**Independent Test**: Crear un acceso y agregarle 3 credenciales distintas, editando/eliminando una sin afectar a las demás; confirmar que un acceso migrado conserva su credencial previa (Escenarios 1 y 3 de `quickstart.md`).

### Tests for User Story 2

- [X] T013 [P] [US2] Test de API ultra-limitado (≤10 registros) en `backend/tests/api/test_clients.py` (o archivo nuevo `test_client_access_credentials.py` si el existente ya es extenso): crear un acceso, agregar 2 credenciales vía `POST .../access/{access_id}/credentials`, verificar listado (`GET`), edición (`PATCH`) y eliminación (`DELETE`) independientes entre sí — debe fallar antes de T015 (endpoints inexistentes) — se creó `backend/tests/api/test_client_access_credentials_api.py` (3 tests) y se reescribió `test_client_access_api.py` (contrato viejo con `access_type` string ya no existía) para el nuevo contrato

### Implementation for User Story 2

- [X] T014 [US2] `backend/infra/repositories/client_repo.py`: agregar `list_credentials/add_credential/update_credential/delete_credential(access_id, ...)` (depende de T006)
- [X] T015 [US2] `backend/api/routes/clients.py`: endpoints `GET/POST /api/clients/{client_id}/access/{access_id}/credentials` y `PATCH/DELETE /api/clients/{client_id}/access/{access_id}/credentials/{credential_id}` con documentación Swagger, mismo permiso de módulo `clients` ya vigente (depende de T014) — hace pasar T013 — nota de implementación: se requirió agregar explícitamente las 2 clases nuevas a la lista `method_decorators = [_enforce("clients")]` al final de `clients.py`, no descubierto hasta un 500 en runtime (`g.current_user` sin definir)
- [X] T016 [P] [US2] `frontend/src/types/client.ts`: agregar `ClientAccessCredential`, `ClientAccessCredentialFormData`
- [X] T017 [P] [US2] `frontend/src/services/clientService.ts`: agregar `listCredentials/addCredential/updateCredential/deleteCredential`
- [X] T018 [US2] `frontend/src/pages/ClientsPage.tsx`: la tabla de accesos pasa a `expandable` (Ant Design), mostrando por acceso una tabla anidada de credenciales con alta/edición/eliminación inline, enmascarado de contraseña por defecto (mismo patrón `include_sensitive` ya usado en spec 018) (depende de T011, T016, T017)
- [X] T019 [US2] Verificación manual en Docker real: Escenarios 1 y 3 de [quickstart.md](./quickstart.md) — credenciales múltiples independientes y migración de la credencial previa (depende de T015, T018) — **verificado con Docker real**: el acceso VPN migrado muestra su credencial `label="Principal"`/`username="vpn_test_031"` intacta; se agregó una segunda credencial ("Segundo usuario") vía UI y ambas conviven, se revelan independientemente (botón ojo) y persisten al reabrir el cliente; `pytest tests/api/test_client_access_credentials_api.py tests/api/test_client_access_api.py` → 9 passed

**Checkpoint**: User Story 2 funcional y verificable de forma independiente (FR-005 a FR-008, FR-013, SC-002, SC-003).

---

## Phase 5: User Story 3 - Puerto propio y ambiente universal (Priority: P2)

**Goal**: El puerto se registra como dato propio del acceso (separado del host), y el ambiente (Producción/Pruebas/etc.) aplica a cualquier tipo de acceso, no solo al que antes era "URL de sistema".

**Independent Test**: Crear un acceso de tipo "VPN" indicando ambiente y puerto, y confirmar que ambos se guardan como campos independientes (Escenario 4 de `quickstart.md`).

### Implementation for User Story 3

- [X] T020 [US3] `backend/api/routes/clients.py`: eliminar la restricción de aplicación que solo permitía `environment` cuando el tipo era "URL de sistema" — válido para cualquier `access_type_id` (depende de T008)
- [X] T021 [US3] `backend/api/routes/clients.py` + `backend/infra/repositories/client_repo.py`: aceptar y serializar `port` (entero, opcional) en creación/edición/listado de acceso (columna ya agregada en T002/T006) (depende de T006)
- [X] T022 [P] [US3] `frontend/src/pages/ClientsPage.tsx` (formulario de acceso): agregar campo numérico "Puerto" y habilitar el selector de "Ambiente" para cualquier tipo de acceso, no solo el equivalente a "URL de sistema" (depende de T011)
- [X] T023 [US3] Verificación manual en Docker real: Escenario 4 de [quickstart.md](./quickstart.md) (depende de T020, T021, T022) — **verificado con Docker real**: acceso tipo "APEX" creado con `environment=prod`, `port=1443`, ambos persistidos y mostrados como columnas independientes en la tabla

**Checkpoint**: User Story 3 funcional y verificable de forma independiente (FR-009, FR-010).

---

## Phase 6: User Story 4 - Adjunto anclado a un acceso puntual (Priority: P2)

**Goal**: Un manual/instructivo se puede asociar a un acceso específico del cliente, sin perder los adjuntos generales ya existentes.

**Independent Test**: Subir un adjunto asociado a un acceso puntual y confirmar que solo aparece listado junto a ese acceso (Escenario 5 de `quickstart.md`).

### Implementation for User Story 4

- [X] T024 [US4] `backend/api/routes/clients.py`: los endpoints de `access-attachments` aceptan un campo opcional `client_access_id` en la subida y lo devuelven en cada ítem del listado (columna ya agregada en T002/T006) (depende de T006)
- [X] T025 [P] [US4] `frontend/src/types/client.ts`: `ClientAccessAttachment` gana `client_access_id: string | null`
- [X] T026 [US4] `frontend/src/pages/ClientsPage.tsx`: la subida de adjuntos permite elegir opcionalmente un acceso puntual; el listado de adjuntos de cada acceso (dentro de la fila expandida de T018) muestra solo los suyos, y los adjuntos sin `client_access_id` se siguen mostrando como adjuntos generales del cliente, igual que antes (depende de T018, T024, T025)
- [X] T027 [US4] Verificación manual en Docker real: Escenario 5 de [quickstart.md](./quickstart.md) (depende de T026) — **verificado con Docker real**: se subió `manual_apex.txt` anclado al acceso APEX; aparece solo en la fila expandida de APEX ("Adjuntos de este acceso"), no en la del acceso VPN ni en "Adjuntos generales (sin acceso asociado)" (que queda vacío, tal como se esperaba)

**Checkpoint**: User Story 4 funcional y verificable de forma independiente (FR-011, FR-012, SC-005).

---

## Phase 7: Polish & Trazabilidad UAT

**Purpose**: Cerrar el ciclo con el framework UAT y confirmar alcance de pruebas.

- [X] T028 Ejecutar únicamente los archivos de test tocados (`test_clients.py`/`test_client_access_credentials.py`, y `test_catalogs.py` si existe) — pytest acotado, prohibido correr la suite completa (Principio VII); confirmar que pasan, incluyendo el test nuevo de T013 (depende de T015) — `pytest tests/api/test_client_access_api.py tests/api/test_client_access_credentials_api.py` → **9 passed**
- [X] T029 Actualizar `UAT/02_Backlog/BACKLOG.md`: cambiar el `Estado` de `OBS-0041` de `Abierta` a `Lista para Validar`, siguiendo `UAT/CONVENTIONS.md` — no editar el contenido narrativo de `UAT/01_Iterations/ITER-006/ITER-006.md` (depende de T012, T019, T023, T027, T028) — hecho; `ITER-006.md` no tocado (verificado con `git diff`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato.
- **Foundational (Phase 2)**: Depende de Setup (T001, para tener datos de prueba). Bloquea a las 4 historias.
- **User Story 1 (Phase 3)**: Depende de Foundational (Phase 2).
- **User Story 2 (Phase 4)**: Depende de Foundational (Phase 2). Depende además de T011 (US1) para el punto de montaje del formulario de acceso en `ClientsPage.tsx`, pero es independientemente verificable una vez integrada.
- **User Story 3 (Phase 5)**: Depende de Foundational (Phase 2) y de T008/T011 (US1) por compartir `clients.py`/`ClientsPage.tsx`.
- **User Story 4 (Phase 6)**: Depende de Foundational (Phase 2) y de T018 (US2) por compartir la fila expandida de `ClientsPage.tsx`.
- **Polish (Phase 7)**: Depende de que las 4 historias estén verificadas (T012, T019, T023, T027).

### User Story Dependencies

- **User Story 1 (P1)**: Sin dependencia funcional de las otras 3 historias — puede completarse y validarse primero (MVP).
- **User Story 2 (P1)**: Funcionalmente independiente de US1/US3/US4 (otro sub-recurso, `credentials`); comparte archivo `ClientsPage.tsx` con US1 por orden de implementación, no por acoplamiento de datos.
- **User Story 3 (P2)**: Comparte `clients.py`/`ClientAccessModel`/`ClientsPage.tsx` con US1 (mismo registro de acceso) — por eso se implementa después, aunque su criterio de aceptación no depende del catálogo en sí.
- **User Story 4 (P2)**: Comparte la UI expandida de US2 para mostrar adjuntos por acceso, pero su modelo (`client_access_attachments`) es independiente del de credenciales.

### Dentro de cada User Story

- US1: T007 (serialización) → T008 (validación) → T011 (UI, depende también de T009/T010) → T012 (verificación).
- US2: T013 (test) antes de T015 (implementación que lo hace pasar). T014 antes de T015. T016/T017 en paralelo entre sí. T018 depende de T016/T017 y de T011 (US1). T019 al final.
- US3: T020/T021 en paralelo entre sí (mismo archivo `clients.py` pero secciones distintas — ejecutar secuencial si un solo desarrollador). T022 depende de T011. T023 al final.
- US4: T024 antes de T026. T025 en paralelo con T024. T026 depende también de T018 (US2). T027 al final.

### Parallel Opportunities

- T003 (modelo de catálogo) puede iniciarse apenas termine T002 (migración) mientras T005/T006 (entidades/modelos de acceso) se trabajan en paralelo si hay más de un desarrollador.
- T009, T010 (US1) en paralelo entre sí.
- T016, T017 (US2) en paralelo entre sí.
- T025 (US4) en paralelo con T024.
- Una vez completada Foundational, US1 y US2 pueden avanzar en paralelo por dos desarrolladores distintos (comparten `ClientsPage.tsx` solo al final, en T018 vs T011 — coordinar el merge de ese archivo).

---

## Parallel Example: User Story 2

```bash
# Lanzar juntas (archivos distintos, sin dependencias entre sí):
Task: "Test de API: CRUD de client_access_credentials — backend/tests/api/test_clients.py"
Task: "Agregar ClientAccessCredential/ClientAccessCredentialFormData — frontend/src/types/client.ts"
Task: "Agregar listCredentials/addCredential/updateCredential/deleteCredential — frontend/src/services/clientService.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup.
2. Completar Phase 2: Foundational (migración + modelos — crítico, bloquea todo lo demás).
3. Completar Phase 3: User Story 1 (catálogo administrable).
4. **Detener y validar**: probar User Story 1 de forma independiente contra Docker (Escenarios 1-2 de `quickstart.md`).
5. Continuar con User Story 2, 3, 4 y Polish para cerrar completamente OBS-0041.

### Incremental Delivery

1. Setup + Foundational → esquema y modelos listos.
2. User Story 1 (catálogo) → validar independientemente → MVP.
3. User Story 2 (credenciales múltiples) → validar independientemente.
4. User Story 3 (puerto/ambiente) → validar independientemente.
5. User Story 4 (adjunto por acceso) → validar independientemente.
6. Polish → test acotado + actualización de `BACKLOG.md` (cierre de trazabilidad UAT).

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes entre las tareas marcadas.
- [Story] mapea cada tarea a su User Story para trazabilidad con `spec.md`.
- Toda la migración de esquema (Alembic) vive en una sola tarea (T002) por compartir una única migración reversible (Principio de la Constitución sobre migraciones + `research.md` Decisión 5).
- No editar retroactivamente `UAT/01_Iterations/ITER-006/ITER-006.md` — todo cambio de estado va en `UAT/02_Backlog/BACKLOG.md` (T029).
- Sin dependencias nuevas de `package.json`/`requirements.txt` (Principio V) — Ant Design `expandable`, `Select`, `Input.Password` ya están en uso.
