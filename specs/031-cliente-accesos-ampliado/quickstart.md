# Quickstart — Validación de Ampliación de Accesos y Conexiones del Cliente

Valida `OBS-0041` (Backlog UAT, `ITER-006`). Ver contratos en
[contracts/client-access-extended.md](contracts/client-access-extended.md) y modelo en
[data-model.md](data-model.md).

## Prerrequisitos

- Entorno Docker Compose levantado (`sywork_db`, `sywork_backend`, `sywork_frontend`).
- Migraciones aplicadas hasta `047_client_access_catalog_credentials` (`alembic upgrade head`).
- Un usuario con rol Admin o Coordinador (permiso `include_sensitive` sobre Clientes) y permiso
  `catalogs`.
- Al menos un cliente con accesos ya cargados desde spec 018 (con `username`/`password` propios),
  para validar la migración de US1/US2.

## Escenario 1 — Migración sin pérdida de tipo y de credenciales (FR-004/FR-007, SC-003/SC-004)

1. Antes de migrar, anotar `access_type`, `username` y `password` (con `include_sensitive`) de un
   acceso existente vía `GET /api/clients/{id}/access`.
2. Aplicar la migración (`alembic upgrade head`).
3. `GET /api/clients/{id}/access` → el mismo acceso ahora trae `access_type_id` apuntando a la
   entrada del catálogo equivalente (`vpn→VPN`, `system_url→Sistema/Integración`,
   `remote_desktop→Escritorio remoto`) y ya no incluye `username`/`password` en el cuerpo.
4. `GET /api/clients/{id}/access/{access_id}/credentials` → debe existir exactamente una
   credencial con `label='Principal'`, `username`/`password` iguales a los anotados en el paso 1.
5. **Resultado esperado**: ningún dato se perdió; el tipo y la credencial previa siguen
   accesibles, ahora en su nueva forma.

## Escenario 2 — Catálogo administrable de tipos de acceso (US1)

1. En Catálogos, agregar un tipo nuevo (ej. "APEX") vía `POST /api/catalogs/access-types`.
2. **Resultado esperado**: `201` con el nuevo tipo, incluyendo un `color_index` asignado
   automáticamente (no enviado en el body).
3. En Maestros > Clientes, abrir un cliente → pestaña "Accesos y conexiones" → crear un acceso
   nuevo → el selector de tipo ya ofrece "APEX" junto a los 5 tipos sembrados.
4. Agregar un segundo tipo (ej. "NetSuite") y confirmar que su color no coincide con "APEX" ni con
   ningún tipo existente, y que el color de "APEX" no cambió al agregar "NetSuite" (FR-002).

## Escenario 3 — Credenciales múltiples sin repetir host (US2)

1. Crear un acceso tipo "Sistema / Integración" con un host único (ej. una URL de ERP de prueba).
2. Agregar tres credenciales distintas (`label`/`username`/`password` cada una) vía
   `POST /api/clients/{id}/access/{access_id}/credentials`.
3. `GET .../credentials` → las tres coexisten bajo el mismo acceso, sin duplicar el host.
4. Editar una credencial (`PATCH .../credentials/{id}`) y eliminar otra
   (`DELETE .../credentials/{id}`) → **Resultado esperado**: la tercera credencial permanece
   intacta, sin afectarse por los cambios en las otras dos (FR-006).
5. Repetir el Escenario 4 de spec 018 (enmascarado por defecto + control de revelado) sobre una de
   estas credenciales, para confirmar que el enmascarado sigue vigente en el modelo nuevo.

## Escenario 4 — Puerto propio y ambiente universal (US3)

1. Crear un acceso tipo "VPN" (antes solo "URL de sistema" permitía `environment`) indicando
   `environment='prod'` y `port=1194`.
2. **Resultado esperado**: `201` sin error de validación; `GET` posterior devuelve ambos campos
   por separado (no concatenados en `host`).

## Escenario 5 — Adjunto anclado a un acceso puntual (US4)

1. Con un cliente que tiene 2+ accesos, subir un archivo con `client_access_id` = el primero
   (`POST /api/clients/{id}/access-attachments`, form field `client_access_id`).
2. `GET /api/clients/{id}/access-attachments` → el archivo aparece con
   `"client_access_id": "<id del primer acceso>"`.
3. **Resultado esperado**: al visualizar el segundo acceso en la UI, el archivo no aparece
   listado ahí; los adjuntos generales previos (sin `client_access_id`) siguen visibles como antes
   del cambio.

## Verificación de contrato (opcional, vía curl/Swagger UI)

```bash
# Listar tipos de acceso del catálogo
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/catalogs/access-types

# Crear una credencial sobre un acceso existente
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"label":"Admin del workspace","username":"ADMIN","password":"secret"}' \
  http://localhost:5000/api/clients/$CLIENT_ID/access/$ACCESS_ID/credentials
```

**Resultado esperado**: `201` con la credencial creada; `GET` posterior la incluye en `items[]`.
