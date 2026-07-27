# Implementation Plan: Ampliación de Accesos y Conexiones del Cliente

**Branch**: `031-cliente-accesos-ampliado` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/031-cliente-accesos-ampliado/spec.md`

## Summary

Amplía el modelo de "Accesos y conexiones" del Cliente (spec `018-cliente-accesos-conexiones`)
resolviendo `OBS-0041` (Backlog UAT, `ITER-006`, propuesta de Camilo Reyes): (1) el campo
`access_type` de `ClientAccess` deja de ser un enum fijo de código y pasa a ser una FK a un nuevo
catálogo administrable `catalog_access_types` (mismo patrón `_CatalogMixin` que `catalog_teams`,
más un `color_index` auto-asignado y estable); (2) `username`/`password` dejan de vivir en la
misma fila que el acceso — se mueven a una tabla hija nueva `client_access_credentials`
(1 acceso ──< N credenciales), migrando automáticamente los valores ya cargados como primera
credencial; (3) `client_access` gana `port` (propio, separado del host) y `environment` deja de
restringirse a un solo tipo; (4) `client_access_attachments` gana una FK opcional
`client_access_id` para anclar un adjunto a un acceso puntual, sin perder los adjuntos generales
de cliente ya existentes. Una sola migración Alembic cubre las cuatro piezas. Sin dependencias
nuevas, sin cambio de mecanismo de cifrado ni de RLS (se replica el patrón ya vigente).

## Technical Context

**Language/Version**: Python 3.12 (Flask, backend) · TypeScript 5.6 strict + React 19 (frontend)

**Primary Dependencies**: Flask-RESTX (Swagger/OpenAPI), SQLAlchemy + Alembic, Ant Design 5
(`Table`, `Tabs`, `Select`, `Input.Password`, `Collapse`/expandable row) — todas ya aprobadas en
la Constitución, sin altas nuevas. Reutiliza el namespace genérico de Catálogos
(`backend/api/routes/catalogs.py`, `CATALOG_MODELS`) agregando la entrada `"access-types"`.

**Storage**: PostgreSQL 16 — una tabla nueva `catalog_access_types`, una tabla nueva
`client_access_credentials` (FK `client_access_id`), y 3 columnas nuevas sobre tablas existentes:
`client_access.access_type_id` (FK), `client_access.port`, `client_access_attachments.client_access_id`
(FK nullable). RLS habilitado en `client_access_credentials` (mismo patrón app-level que
`client_access`); `catalog_access_types` no contiene datos sensibles, sigue el mismo criterio que
los demás catálogos (sin RLS, ya que `catalog_teams`/`catalog_tools`/etc. tampoco lo tienen).

**Testing**: pytest en backend, ultra-limitado por Principio VII (≤10 registros por test, solo el
módulo tocado: `test_clients.py`/`test_catalogs.py` o equivalente). Sin framework de tests de
frontend configurado en este repo — verificación manual en navegador vía Docker, igual que specs
previas.

**Target Platform**: Web app en Docker Compose on-premise — sin cambios de infraestructura.

**Project Type**: Web application (monorepo `backend/` + `frontend/`, Option 2).

**Performance Goals**: N/A — uso interno de bajo volumen (decenas de clientes, pocos accesos y
credenciales por cliente); sin metas de throughput específicas.

**Constraints**: La migración de datos existentes (mapeo de `access_type` legacy al catálogo
nuevo, y migración de `username`/`password` de `client_access` a `client_access_credentials`)
DEBE ejecutarse dentro de la misma migración Alembic que crea las tablas/columnas nuevas, DEBE ser
reversible (`downgrade` reconstruye lo necesario, best-effort igual que el precedente de spec 018)
y no debe perder información ya cargada. No se elimina ninguna columna legacy (`access_type` text,
`username`, `password` de `client_access`) en esta migración.

**Scale/Scope**: Acotado a Maestros > Clientes (pestaña "Accesos y conexiones") y al módulo
Catálogos (nuevo tipo `access-types`). No toca Proyectos, Tickets ni otros módulos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación | Estado |
|---|---|---|
| I. API-First y Dominio Primero | Nuevos endpoints de credenciales (`GET/POST/PATCH/DELETE /api/clients/{id}/access/{access_id}/credentials[/{credential_id}]`) documentados en Swagger antes de implementar, mismo namespace que `clients.py`. `catalog_access_types` se expone reutilizando el contrato genérico ya documentado de `catalogs.py` (`GET/POST /api/catalogs/access-types`, `PATCH .../activate`/`deactivate`). Lógica de mapeo de migración y de asignación de color vive en el repositorio/migración, no en la ruta Flask. | PASS |
| II. Clean Architecture (3 capas) | `ClientAccessCredential` como entidad nueva en `backend/domain/entities/client.py` (junto a `ClientAccess`); `AccessTypeCatalogModel` en `backend/infra/models/catalog_model.py` (mismo `_CatalogMixin`); `ClientAccessCredentialModel` en `backend/infra/models/client_model.py`; `ClientRepository` gana `list_credentials/add_credential/update_credential/delete_credential`, mismo patrón que `list_access/add_access/...`. | PASS |
| III. Tipado estricto | Tipos TS nuevos (`ClientAccessCredential`, `ClientAccessCredentialFormData`, `AccessTypeCatalogItem`) en `frontend/src/types/client.ts`; `ClientAccessType` deja de ser union literal fija y pasa a `string` (id de catálogo) con el nombre/color resueltos vía join, sin `any`. Type hints en entidades/repositorios Python. | PASS |
| IV. Seguridad en profundidad | RLS habilitado en `client_access_credentials` (mismo patrón que `client_access`). Contraseña cifrada en reposo con el mismo mecanismo ya vigente (`_encrypt`/`_decrypt` de `client_model.py`), sin cambios. Enmascarado en UI gobernado por el permiso `include_sensitive` ya existente — no se crea un permiso nuevo. | PASS |
| V. Gobernanza de librerías | Sin dependencias nuevas: Ant Design (`Select`, tabla expandible) y SQLAlchemy/Alembic ya están aprobados y en uso. | PASS |
| VI. AI-Native | No aplica — no es un flujo de asignación/triage ni genera Gold Standard Dataset. Sin impacto. | N/A |
| VII. Alcance de sesión / testing ultra-limitado | Implementación acotada a Maestros > Clientes y al catálogo `access-types`. Tests backend nuevos ≤10 registros de prueba, solo sobre el modelo/repositorio/ruta tocados (no se corre la suite completa). | PASS |

**Resultado**: Sin violaciones. No se requiere `Complexity Tracking`.

## Project Structure

### Documentation (this feature)

```text
specs/031-cliente-accesos-ampliado/
├── plan.md              # Este archivo
├── research.md          # Fase 0
├── data-model.md         # Fase 1
├── quickstart.md         # Fase 1
├── contracts/            # Fase 1
└── tasks.md              # Fase 2 (/speckit-tasks, no generado por /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── domain/
│   └── entities/
│       └── client.py                  # + dataclass ClientAccessCredential; ClientAccess gana access_type_id/port
├── infra/
│   ├── models/
│   │   ├── catalog_model.py           # + AccessTypeCatalogModel (color_index) + entrada "access-types" en CATALOG_MODELS
│   │   └── client_model.py            # ClientAccessModel: + access_type_id (FK), port; + ClientAccessCredentialModel; ClientAccessAttachmentModel: + client_access_id (FK nullable)
│   ├── repositories/
│   │   ├── catalog_repo.py            # create(): asigna color_index automático cuando el catálogo lo soporta (hasattr)
│   │   └── client_repo.py             # + list_credentials/add_credential/update_credential/delete_credential
│   └── migrations/versions/
│       └── 047_client_access_catalog_credentials.py   # catalog_access_types + seed, access_type_id + port + backfill, client_access_credentials + RLS + migración de datos, client_access_attachments.client_access_id
└── api/
    └── routes/
        └── clients.py                 # + endpoints CRUD de credentials bajo /access/{access_id}/credentials

frontend/
├── src/
│   ├── types/
│   │   └── client.ts                  # ClientAccessType: union literal → string (id); + ClientAccessCredential, ClientAccessCredentialFormData, AccessTypeCatalogItem
│   ├── services/
│   │   └── clientService.ts           # + listCredentials/addCredential/updateCredential/deleteCredential; catalogService ya genérico cubre access-types
│   └── pages/
│       └── ClientsPage.tsx            # Pestaña "Accesos y conexiones": tabla plana → lista de accesos expandible a su tabla de credenciales (patrón "Portafolio de software" + un nivel de anidación); selector de tipo pasa de opciones fijas a Select poblado desde el catálogo, con badge de color
```

**Structure Decision**: Se mantiene el layout de repo existente (Clean Architecture 3 capas en
`backend/`, `pages/services/types` en `frontend/`). No se crean paquetes ni directorios nuevos de
alto nivel — todo el trabajo extiende archivos ya tocados por spec 018, siguiendo el mismo patrón
ya validado en producción (`ClientAccess`/`ClientSystem`) y el patrón de catálogo ya validado
(`catalog_teams`, OBS-0024).

## Complexity Tracking

*No aplica — Constitution Check sin violaciones.*
