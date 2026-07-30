# Contrato: Renombrar valor de Catálogo

Extiende `backend/api/routes/catalogs.py` (namespace `catalogs`, ya documentado en Swagger).

## `PATCH /api/catalogs/{catalog}/{item_id}`

**Permiso**: `catalogs:create` (reutilizado — mismos roles Admin/Coordinador que ya pueden crear
valores de catálogo; ver research.md Decisión 6).

**Path params**:
- `catalog`: `tools | processes | resolution-types | record-types | teams | access-types`
- `item_id`: UUID del registro

**Body**:
```json
{ "name": "Nuevo nombre" }
```

**Respuestas**:
- `200` — registro actualizado (`_catalog_out`: `id`, `name`, `active`)
- `400` — `name` vacío o `item_id` inválido (`validation_error`)
- `404` — catálogo desconocido (`not_found`) o registro no encontrado (`not_found`)
- `409` — nombre duplicado dentro del mismo catálogo (`name_duplicate`), mismo código que `POST`
- `401` / `403` — igual que el resto del namespace

No reemplaza `POST /api/catalogs/{catalog}` (crear) ni los endpoints `.../activate` /
`.../deactivate` — es aditivo.

## Extensión (no nueva ruta): `GET /api/tickets` — parámetro `sort`

Valores nuevos aceptados además de los ya existentes (`urgency | created_at | -created_at |
priority | -priority | status`): `-status`, `code`, `-code`. Mismo endpoint, mismo contrato de
respuesta — solo se documenta el `@ns.doc` con los valores adicionales.
