# Data Model — Ampliación de Accesos y Conexiones del Cliente

## Entidades

### AccessTypeCatalog (tabla `catalog_access_types`)

Catálogo administrable de tipos de acceso, reemplaza el enum fijo de código de `client_access.access_type`.
Mismo `_CatalogMixin` que `catalog_teams`/`catalog_tools`/etc. (`backend/infra/models/catalog_model.py`), más un campo propio.

| Campo | Tipo | Nullable | Notas |
|---|---|---|---|
| `id` | UUID (PK) | No | `gen_random_uuid()` (heredado del mixin) |
| `name` | text (unique) | No | Heredado del mixin |
| `active` | boolean | No | Heredado del mixin, default `true` |
| `created_at` | timestamptz | No | Heredado del mixin, `now()` |
| `color_index` | smallint | No | Asignado en `CatalogRepository.create()` — siguiente índice libre (0-7) de la paleta fija de 8 colores del frontend; no editable por el usuario ni expuesto en el formulario de creación |

**Semilla inicial** (migración): `VPN` (0), `Base de datos` (1), `Servidor / instancia` (2),
`Escritorio remoto` (3), `Sistema / Integración` (4).

**Reglas de validación**: nombre único entre valores activos e inactivos (mismo criterio que los
demás catálogos, `CatalogRepository.get_by_name` antes de `create`).

### ClientAccess (tabla `client_access`, existente desde spec 018)

| Campo | Tipo | Nullable | Notas |
|---|---|---|---|
| `id` | UUID (PK) | No | Sin cambios |
| `client_id` | UUID (FK → `clients.id`) | No | Sin cambios, `ON DELETE CASCADE` |
| `access_type` | text | No | **Legacy** — ya no se lee/escribe desde la API nueva; se conserva sin `DROP COLUMN` |
| `access_type_id` | UUID (FK → `catalog_access_types.id`) | No (tras backfill) | **Nuevo** — reemplaza `access_type` en la API/UI |
| `environment` | text | Sí | Sin cambio de columna; deja de restringirse a un tipo particular en la capa de validación de aplicación |
| `port` | integer | Sí | **Nuevo** — separado del host |
| `username` | text | Sí | **Legacy** — ya no se lee/escribe desde la API nueva (ver `ClientAccessCredential`) |
| `password` | bytea (cifrado) | Sí | **Legacy**, ídem |
| `host` | text | Sí | Sin cambios |
| `notes` | text | Sí | Sin cambios; para tipos de integración (OAuth), alberga metadatos del endpoint (Scope/Token URL) |
| `created_at` / `updated_at` | timestamptz | No | Sin cambios |

**Relaciones**: `clients (1) ──< client_access (N)`; `catalog_access_types (1) ──< client_access (N)`;
`client_access (1) ──< client_access_credentials (N)`.

### ClientAccessCredential (tabla nueva `client_access_credentials`)

| Campo | Tipo | Nullable | Notas |
|---|---|---|---|
| `id` | UUID (PK) | No | `gen_random_uuid()` |
| `client_access_id` | UUID (FK → `client_access.id`) | No | `ON DELETE CASCADE` |
| `label` | text | Sí | Etiqueta descriptiva (ej. "Admin del workspace"); `'Principal'` para las migradas automáticamente |
| `username` | text | Sí | — |
| `password` | bytea (cifrado, mismo mecanismo `_encrypt`/`_decrypt` de `client_model.py`) | Sí | Enmascarado por defecto, mismo permiso `include_sensitive` |
| `notes` | text | Sí | — |
| `created_at` / `updated_at` | timestamptz | No | `now()` / `now()` on update |

**Relaciones**: `client_access (1) ──< client_access_credentials (N)`.

**Reglas de validación**:
- Un `client_access` puede tener cero o más credenciales (edge case del spec: "acceso sin ninguna
  credencial registrada" es válido).
- Eliminar una credencial no afecta a las demás del mismo acceso (FR-006).
- Eliminar un `client_access` elimina en cascada sus credenciales (mismo criterio que el resto del
  modelo jerárquico del repo).

### ClientAccessAttachment (tabla `client_access_attachments`, existente desde spec 018)

| Campo | Tipo | Nullable | Notas |
|---|---|---|---|
| `id` … `storage_path` … `created_at` | (sin cambios) | | Ver spec 018 |
| `client_access_id` | UUID (FK → `client_access.id`) | Sí | **Nuevo** — ancla el adjunto a un acceso puntual; `NULL` = adjunto general del cliente (comportamiento ya existente, sin cambios) |

**Relaciones**: `clients (1) ──< client_access_attachments (N)` (sin cambios);
`client_access (1) ──< client_access_attachments (N)` (nueva, opcional).

## Row Level Security

`client_access_credentials` habilita RLS con la misma policy app-level que `client_access` (ver
`research.md`, Decisión 5):

```sql
ALTER TABLE client_access_credentials ENABLE ROW LEVEL SECURITY;
CREATE POLICY client_access_credentials_app_access ON client_access_credentials
  USING (current_setting('app.authenticated', true) IS NOT DISTINCT FROM 'true'
         OR current_user = 'sywork_user');
```

`catalog_access_types` no requiere RLS (mismo criterio que `catalog_teams`/`catalog_tools`/etc. —
no contiene datos sensibles ni específicos de un cliente).

## Notas de migración (`047_client_access_catalog_credentials.py`)

1. `CREATE TABLE catalog_access_types ...` (mixin + `color_index`); seed de 5 filas (ver
   `research.md` Decisión 3), `color_index` 0-4 en orden de inserción.
2. `ALTER TABLE client_access ADD COLUMN access_type_id UUID NULL REFERENCES catalog_access_types(id)`.
3. Backfill (misma transacción): `UPDATE client_access SET access_type_id = <id según mapeo
   vpn→VPN, system_url→Sistema/Integración, remote_desktop→Escritorio remoto>`.
4. `ALTER TABLE client_access ALTER COLUMN access_type_id SET NOT NULL`.
5. `ALTER TABLE client_access ADD COLUMN port INTEGER NULL`.
6. `CREATE TABLE client_access_credentials ...` + RLS (ver arriba).
7. Data migration: para cada `client_access` con `username IS NOT NULL OR password IS NOT NULL`,
   insertar 1 `client_access_credentials` con `label='Principal'`, copiando `username`/`password`
   (blob cifrado, sin desencriptar).
8. `ALTER TABLE client_access_attachments ADD COLUMN client_access_id UUID NULL REFERENCES client_access(id)`.
9. `downgrade()`: elimina `client_access_credentials` (best-effort — no reconstruye
   `client_access.username`/`password` porque esas columnas legacy nunca se tocaron ni se
   eliminaron, por lo que no hay nada que restaurar en ellas); revierte `access_type_id`/`port` de
   `client_access` y `client_access_id` de `client_access_attachments`; `DROP TABLE
   catalog_access_types`.

## Actualización de tipos existentes

- `backend/domain/entities/client.py`: `ClientAccess` gana `access_type_id: uuid.UUID` y
  `port: int | None`; nuevo `@dataclass ClientAccessCredential`.
- `backend/infra/models/catalog_model.py`: nuevo `AccessTypeCatalogModel(_CatalogMixin, Base)`
  con `color_index`; entrada `"access-types": AccessTypeCatalogModel` en `CATALOG_MODELS`.
- `frontend/src/types/client.ts`: `ClientAccessType` pasa de union literal (`'vpn' | 'system_url' |
  'remote_desktop'`) a `string` (id UUID del catálogo); nuevas interfaces `ClientAccessCredential`,
  `ClientAccessCredentialFormData`, `AccessTypeCatalogItem` (`id`, `name`, `active`, `color_index`).
