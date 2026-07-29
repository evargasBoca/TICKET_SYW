# Research — Deshabilitación de Usuarios/Cliente y Módulo de Reportes Dinámicos

## Decisión 1 — Deshabilitar Usuario/cliente: reutilizar `UserModel.active`, NO el endpoint genérico `/api/users/{id}/deactivate`

**Hallazgo**: `users.active` ya existe (`backend/infra/models/user_model.py:18`) y ya hay endpoints
genéricos `PATCH /api/users/{id}/deactivate` / `/activate` (`backend/api/routes/users.py`),
usados hoy por `TeamPage.tsx` para cuentas **internas**. Pero esos endpoints exigen el permiso
`users:deactivate` del módulo `users`, y el seed de permisos (migración `009`) solo le da ese
permiso a **Admin** — Coordinador solo tiene `users:view`. El spec (US1) exige que el
**Coordinador** pueda deshabilitar Usuarios/cliente.

**Decisión**: NO reutilizar el endpoint genérico ni ampliar el permiso `users:deactivate` a
Coordinador (eso le daría poder de desactivar *cualquier* usuario, incluido Admin/QM/Resolutor —
regresión de seguridad fuera de alcance). En su lugar, nuevo endpoint acotado
`PATCH /api/client-contacts/{contact_id}/active`, gateado por el permiso ya existente
`client_contacts:manage` (mismo que ya usa Coordinador para crear/gestionar estas cuentas),
que internamente llama a `UserRepository(db).set_active(user_id, active)` (mismo repositorio,
sin duplicar lógica de persistencia).

**Alternativas consideradas**: (a) ampliar `users:deactivate` a Coordinador — rechazada por
riesgo de seguridad; (b) nueva tabla de estado independiente de `users.active` — rechazada,
duplicaría la fuente de verdad y el login ya valida sobre `users.active`.

## Decisión 2 — Enforcement de sesión ya cubierto por `jwt_required_active`

**Hallazgo**: Todo endpoint autenticado (`require_permission`, `require_authenticated`,
`enforce_module`) ya envuelve `jwt_required_active`, que revisa `user.active` en cada request
(`backend/api/middleware/auth.py`). FR-005 (perder acceso sin esperar expiración del token) **ya
se cumple gratis** una vez que `client_contacts.active` se persiste en `users.active` — no
requiere trabajo adicional de invalidación de sesión.

## Decisión 3 — Bloqueo de asignación futura (FR-003)

**Hallazgo**: Los selectores de Cliente/Proyecto en `ClientContactsPage.tsx` y en el alta de
ticket ya filtran `active: true` vía query param (mismo patrón que `clientService.list({active:
true})`). El listado de `client-contacts` (`GET /api/client-contacts`) hoy no expone ni filtra
por `active`.

**Decisión**: (a) agregar `active` a la respuesta de `GET /api/client-contacts` y aceptar
`active` como filtro opcional; (b) el selector de solicitante en el formulario de ticket y el
selector de "agregar proyecto" pasan `active=true` por defecto (igual que ya hacen con Cliente/
Proyecto); (c) `POST /api/client-contacts/{id}/projects` valida que el Usuario/cliente esté
activo antes de crear la membresía nueva (rechazo `409 contact_inactive` si no lo está) —
la creación de la cuenta (`POST /api/client-contacts`) no cambia, siempre nace activa.

## Decisión 4 — Exportación a Excel: `openpyxl` en backend (nueva dependencia, Principio V)

**Decisión**: generar el `.xlsx` en el backend con `openpyxl` (dependencia Python pura, sin
binarios nativos, ya en la misma familia de librerías ligeras del stack aprobado) en un nuevo
endpoint `GET /api/reports/tickets/export`. **Nueva dependencia backend aprobada aquí**
(`backend/requirements.txt`): `openpyxl`.

**Rationale**: mantiene la generación del archivo del lado del servidor (Principio I: la lógica
vive detrás de un contrato de API, no en el navegador), reutiliza exactamente la misma consulta
filtrada que ya arma las filas del grid (sin lógica duplicada de filtros en el frontend), y evita
sumar una librería JS de manejo de Excel en el bundle del frontend.

**Alternativas consideradas**: (a) generar el `.xlsx` en el frontend con una librería JS
(`xlsx`/SheetJS) — rechazada, sería una dependencia frontend nueva y duplicaría la lógica de
filtros/orden ya resuelta en el backend; (b) `pandas` + `xlsxwriter` — rechazada, `pandas` es una
dependencia pesada innecesaria para escribir un único archivo tabular simple.

## Decisión 5 — Personalización de columnas y reordenamiento: sin nueva dependencia frontend

**Decisión**: el selector de columnas (mostrar/ocultar/reordenar) se construye con componentes ya
aprobados: `Popover` + `Checkbox.Group` de Ant Design 5 para mostrar/ocultar, y `@hello-pangea/dnd`
(ya aprobado para el Kanban, spec 001) para arrastrar y reordenar la lista de columnas visibles.
Cero dependencias nuevas de frontend.

## Decisión 6 — Agregaciones: calculadas en el backend sobre el conjunto filtrado completo

**Decisión**: las funciones de agregación (suma/promedio/conteo) se calculan en SQL sobre **todo**
el conjunto de tickets que cumple los filtros vigentes (no solo la página visible del grid), y se
devuelven en un bloque `aggregates` separado de `items` en la misma respuesta paginada de
`GET /api/reports/tickets`. Esto es consistente con la expectativa de negocio ("suma total de
horas trabajadas") y con lo que ya exporta el botón de Excel (todo el conjunto filtrado, no solo
la página actual — Decisión 4).

**Función pura de agregación** (Principio II — sin SQLAlchemy en el dominio): el cálculo de
qué función aplicar a qué campo vive en `backend/domain/services/report_aggregation_service.py`,
recibiendo listas de valores ya extraídas por el repositorio de infraestructura, no objetos ORM.

## Decisión 7 — Nuevo permiso `reports:view` (no encaja en el enforcement genérico por módulo)

**Hallazgo**: `enforce_module()` asume las 4 acciones fijas `view/create/edit/deactivate`
mapeadas por verbo HTTP — no aplica a un módulo de solo-lectura con sub-acciones distintas
(ver, exportar, guardar vistas). El sistema ya tiene precedente de permisos "ad-hoc" fuera de
ese enforcement genérico (`client_contacts:manage`, `tickets:manage_skills`).

**Decisión**: nuevo permiso `reports:view` (patrón `require_permission("reports", "view")`),
otorgado en el seed/migración a Admin, Coordinador y QM (los mismos roles con visión
transversal de Clientes ya vigente en el sistema); Resolutor y Usuario/cliente no lo reciben.
Cubre tanto ver el grid como exportar a Excel y gestionar Vistas Personalizadas — una sola
acción, sin sub-permisos adicionales, para no sumar complejidad de RBAC fuera de alcance.

## Decisión 8 — Vistas Personalizadas: una tabla nueva, config como JSONB

**Decisión**: tabla `report_saved_views` (`user_id` FK, `name`, `config` JSONB, timestamps),
`UNIQUE (user_id, name)`. El `config` guarda columnas visibles + orden, filtros y agregaciones
como un único blob JSON versionable por el frontend — evita una migración nueva cada vez que se
agregue una columna/filtro al reporte en el futuro. Sin RLS (dato privado de bajo riesgo, ya
acotado por `user_id` en cada consulta, mismo criterio que otros datos "propios" del sistema).
