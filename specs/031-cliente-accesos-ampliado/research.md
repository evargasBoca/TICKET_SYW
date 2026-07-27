# Research — Ampliación de Accesos y Conexiones del Cliente

No quedaron `NEEDS CLARIFICATION` en el Technical Context del plan. Las decisiones de mayor
alcance (migración automática de datos, un solo spec para las 4 piezas) ya se acordaron con el
usuario durante el brainstorming previo a este spec; aquí se documentan las decisiones técnicas
restantes, derivadas del código real del repo y del documento fuente (`ITER-006`).

## Decisión 1 — `access_type` pasa de enum a FK de catálogo, reutilizando el namespace genérico

- **Decisión**: `catalog_access_types` se agrega a `CATALOG_MODELS` en
  `backend/infra/models/catalog_model.py` y se expone vía el namespace ya existente
  `backend/api/routes/catalogs.py` (`GET/POST /api/catalogs/access-types`,
  `PATCH /api/catalogs/access-types/{id}/activate|deactivate`) — no se crea un endpoint dedicado.
- **Rationale**: es exactamente el mismo caso ya resuelto por `catalog_teams` (OBS-0024): un valor
  administrable sin lógica de negocio propia más allá de nombre/estado activo. El único campo
  adicional (`color_index`) no requiere un endpoint distinto — se calcula en `create()`, no se
  recibe del cliente.
- **Alternativas consideradas**: endpoint dedicado `/api/catalogs/access-types` con su propio
  Resource — rechazado, duplicaría lógica ya genérica sin necesidad (el catálogo no tiene reglas
  de negocio distintas a los demás, salvo el color, que es un detalle de creación, no de contrato).

## Decisión 2 — Asignación de color: `color_index` calculado en el repositorio, no en el modelo

- **Decisión**: `CatalogRepository.create()` calcula `color_index = <cantidad de filas ya
  existentes en la tabla, incluyendo inactivas> % 8` únicamente cuando el modelo del catálogo
  declara el atributo (`hasattr(self._model, "color_index")`); los demás catálogos (`tools`,
  `processes`, etc.) no se ven afectados. La paleta de 8 colores en sí vive en el frontend (8
  variables CSS, mismo criterio ya usado en el documento de propuesta adjunto) — el backend solo
  persiste el índice.
- **Rationale**: cumple FR-002 ("color asignado automáticamente y estable") sin necesitar que el
  usuario elija color, y sin duplicar la paleta en dos capas (backend no necesita saber los
  valores hex, solo el índice). Contar filas existentes (no `MAX(color_index)+1`) evita huecos si
  algún día se permite borrar catálogo (hoy solo se desactiva, nunca se borra), y el `% 8` ya cubre
  el caso "más de 8 tipos" (Asunción del spec: reutilizar colores desde el principio de la paleta).
- **Alternativas consideradas**: columna `color` (hex) elegida por el usuario — rechazada
  explícitamente por el documento fuente ("el color no lo elige el usuario a mano"); hash del
  nombre → color — rechazado porque no garantiza estabilidad ni evita colisiones visualmente
  cercanas entre dos nombres con hash similar, a diferencia de un índice incremental.

## Decisión 3 — Mapeo de migración de los 3 tipos legacy al catálogo nuevo

- **Decisión**: la migración siembra 5 filas en `catalog_access_types` (`VPN`, `Base de datos`,
  `Servidor / instancia`, `Escritorio remoto`, `Sistema / Integración`, en ese orden →
  `color_index` 0-4) y backfillea `client_access.access_type_id` mapeando el valor legacy
  `access_type` (texto): `vpn → VPN`, `system_url → Sistema / Integración`,
  `remote_desktop → Escritorio remoto`. Los dos tipos sin datos previos (`Base de datos`,
  `Servidor / instancia`) quedan disponibles desde el día uno, con 0 accesos.
- **Rationale**: preserva exactamente FR-004/SC-004 (ningún acceso existente pierde su tipo) sin
  intervención manual, y adelanta los dos tipos que el propio reporte de origen identificó como
  el motivo principal de la observación (no forzar "Base de datos"/"Servidor" dentro de "URL de
  sistema"). El mapeo `system_url → Sistema / Integración` es el más fiel semánticamente: ambos
  representan "una URL de sistema/aplicación", a diferencia de "Base de datos" (con puerto/host de
  motor de datos) o "Servidor/instancia" (acceso SSH/VM).
- **Alternativas consideradas**: mapear `system_url → Base de datos` — rechazado, no es fiel al
  significado original (una URL de sistema casi nunca es una base de datos); dejar
  `access_type_id` NULL para los existentes y forzar reclasificación manual — rechazado, viola
  FR-004 (migración automática sin intervención).

## Decisión 4 — Migración de credenciales embebidas a `client_access_credentials`

- **Decisión**: dentro de la misma migración, por cada `client_access` con `username` y/o
  `password` no nulos, se inserta una fila en `client_access_credentials` con
  `label='Principal'`, copiando `username`/`password` (ya cifrado, se recorta/reinserta tal cual,
  sin desencriptar-reencriptar) y `notes=NULL`. Las columnas `username`/`password` de
  `client_access` no se eliminan (quedan legacy, igual que `access_type` texto).
- **Rationale**: cumple FR-007/SC-003 sin pérdida de datos y sin re-exponer la contraseña en texto
  plano durante la migración (se copia el blob cifrado directamente entre columnas, sin pasar por
  `_decrypt`/`_encrypt`). `label='Principal'` es un valor por defecto claro para el usuario que
  abre un acceso migrado y ve su única credencial preexistente.
- **Alternativas consideradas**: dejar `label` vacío/`NULL` — rechazado, el mockup del documento
  fuente siempre muestra una etiqueta descriptiva por credencial; generar un `label` a partir del
  `username` — rechazado por sobre-ingeniería, `'Principal'` ya comunica "la única antes de este
  cambio" sin depender de heurísticas.

## Decisión 5 — RLS en `client_access_credentials`

- **Decisión**: replicar el patrón app-level ya usado en `client_access`/`ticket_reassignments`
  (`USING (current_setting('app.authenticated', true) IS NOT DISTINCT FROM 'true' OR current_user
  = 'sywork_user')`), en la misma migración que crea la tabla (precedente reciente:
  `045_ticket_reassignments.py` ya combina creación + RLS en un solo archivo, a diferencia del
  precedente más antiguo de spec 018 que los separaba en dos migraciones).
- **Rationale**: Principio IV (NON-NEGOTIABLE) exige RLS en toda tabla con datos sensibles;
  `client_access_credentials` contiene contraseñas. Seguir el patrón más reciente (una sola
  migración) reduce el número de archivos sin apartarse del mecanismo ya fijado por la
  Constitución.
- **Alternativas consideradas**: migración separada para RLS (patrón spec 018) — descartada por no
  aportar valor adicional; el precedente más reciente del propio repo ya combina ambos pasos.

## Decisión 6 — `client_access_attachments.client_access_id`: FK opcional, no obligatoria

- **Decisión**: la columna nueva es `nullable=True`. Los adjuntos ya existentes (a nivel general
  de cliente) se dejan con `client_access_id = NULL` — no se migran retroactivamente a ningún
  acceso puntual.
- **Rationale**: no existe forma confiable de inferir a qué acceso correspondía un adjunto ya
  subido antes de este cambio (la relación nunca se registró) — inventar una asociación sería
  peor que dejarla como "adjunto general", que es exactamente el comportamiento que ya tenían
  antes del cambio (cumple la Asunción del spec sobre este punto).
- **Alternativas consideradas**: exigir que todo adjunto nuevo se asocie a un acceso (columna NOT
  NULL) — rechazada, rompería la compatibilidad con el flujo de "adjunto general del cliente" que
  el propio spec 018 (FR-003) sigue exigiendo como válido.

## Decisión 7 — UI: lista de accesos expandible a su tabla de credenciales

- **Decisión**: la pestaña "Accesos y conexiones" (`ClientsPage.tsx`) cambia de tabla plana de
  filas (spec 018) a una lista de "instancias" (accesos), cada una expandible (Ant Design `Table`
  con `expandable`) a su propia tabla anidada de credenciales — mismo patrón visual ya usado en
  "Portafolio de software" pero con un nivel más de anidación, tal como muestra el mockup del
  documento fuente.
- **Rationale**: mínimo cambio estructural sobre un componente ya existente y familiar al usuario;
  `expandable` de Ant Design ya está disponible (Principio V, sin dependencia nueva) y es el
  patrón estándar de la librería para "fila con detalle anidado".
- **Alternativas consideradas**: modal separado por acceso para ver/editar credenciales —
  rechazado, agrega un salto de navegación no pedido por el criterio de aceptación ni por el
  mockup, que muestra las credenciales inline debajo de cada acceso.
