# Contract: Ampliación de Accesos y Conexiones del Cliente (spec 031)

Extiende el contrato de spec 018 (`GET/POST/PATCH/DELETE /api/clients/{client_id}/access[/{access_id}]`)
sobre el mismo namespace Flask-RESTX (`clients.py`). Mismo permiso de módulo `clients` ya vigente —
no se introduce un permiso nuevo. `password` solo se incluye en las respuestas cuando el caller
tiene `include_sensitive=True`.

## Cambios en `GET/POST/PATCH /api/clients/{client_id}/access[/{access_id}]` (existentes)

**Body / respuesta — campos que cambian**:
```json
{
  "access_type_id": "uuid",
  "port": "integer | null",
  "environment": "dev | test | prod | null"
}
```

- `access_type` (string enum) se **reemplaza** por `access_type_id` (UUID, FK a
  `catalog_access_types`); la respuesta incluye además `access_type` embebido de solo lectura
  (`{"id": "uuid", "name": "string", "color_index": 0}`) para que el frontend no necesite un
  segundo round-trip.
- `environment` deja de validarse contra un tipo específico — válido para cualquier
  `access_type_id`.
- `port` es nuevo, opcional, entero.
- `username`/`password` **se eliminan** del body de creación/edición de un acceso — se manejan
  exclusivamente vía el sub-recurso de credenciales (abajo). La respuesta de `GET` ya no incluye
  `username`/`password` a nivel de acceso.

**400** `validation_error`: `access_type_id` no existe o está inactivo.

## GET /api/clients/{client_id}/access/{access_id}/credentials — listar credenciales del acceso

**200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "client_access_id": "uuid",
      "label": "string | null",
      "username": "string | null",
      "password": "string | null (solo si include_sensitive)",
      "notes": "string | null",
      "created_at": "iso8601",
      "updated_at": "iso8601"
    }
  ]
}
```

**404**: acceso no encontrado o no pertenece a `client_id`.

## POST /api/clients/{client_id}/access/{access_id}/credentials — crear una credencial

**Body**:
```json
{
  "label": "string | null",
  "username": "string | null",
  "password": "string | null",
  "notes": "string | null"
}
```

**201**: la credencial creada, con
`Location: /api/clients/{client_id}/access/{access_id}/credentials/{id}`.

**404**: acceso no encontrado o no pertenece a `client_id`.

## PATCH /api/clients/{client_id}/access/{access_id}/credentials/{credential_id} — editar

**Body**: cualquier subconjunto de los campos de creación (PATCH parcial).

**200**: la credencial actualizada. **404**: si `credential_id` no existe o no pertenece al
`access_id`/`client_id` de la ruta.

## DELETE /api/clients/{client_id}/access/{access_id}/credentials/{credential_id} — eliminar

**204**. **404** si no existe o no pertenece a la jerarquía de la ruta. No afecta a las demás
credenciales del mismo acceso (FR-006).

## Catálogo de tipos de acceso — reutiliza el contrato genérico existente

Sin endpoints nuevos: `GET/POST /api/catalogs/access-types` y
`PATCH /api/catalogs/access-types/{id}/activate|deactivate` ya quedan cubiertos por
`backend/api/routes/catalogs.py` al agregar `"access-types"` a `CATALOG_MODELS` — mismo contrato
que `GET/POST /api/catalogs/teams`, con el campo adicional de solo lectura `color_index` en la
respuesta (nunca recibido en el `POST`, se calcula en el servidor).

## Cambios en `POST/PATCH /api/clients/{client_id}/access-attachments...` (existentes)

**Body de subida** (`multipart/form-data`) gana un campo opcional `client_access_id` (form field,
UUID) para anclar el adjunto a un acceso puntual; si se omite, el adjunto queda general (mismo
comportamiento que antes de este spec). La respuesta de cada ítem incluye
`"client_access_id": "uuid | null"`.

**400** `validation_error`: `client_access_id` presente pero no pertenece a `client_id`.

## Sin cambios en endpoints existentes

`GET/POST/PATCH /api/clients` y `GET /api/clients/{id}` mantienen su forma actual (sin cambios
por este spec). El listado de accesos (`GET .../access`) sigue siendo el punto de entrada; el
frontend resuelve las credenciales de cada acceso vía el nuevo sub-recurso, no embebidas en la
misma respuesta (evita payloads grandes cuando un acceso tiene muchas credenciales).
