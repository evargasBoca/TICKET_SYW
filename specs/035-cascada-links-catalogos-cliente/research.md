# Research: Cascada, Hipervínculos, Catálogos y Layout de Cliente

## Decisión 1 — Orden de la cascada en el formulario de Ticket (US1)

**Hallazgo de código**: `frontend/src/pages/TicketsPage.tsx` ya tiene dos flujos distintos de captura
según `projectRequiredFlow` (perfil interno, ticket_type='incident'/'Ticket' — OBS-0045/spec 033):

- **Flujo actual "Proyecto primero"** (líneas ~525-544): el usuario elige Proyecto (`project_id`,
  requerido) y Cliente se auto-completa deshabilitado (`disabled`, derivado de `selectedProject`).
- **Flujo "Cliente primero"** (líneas ~546-562, usado hoy solo cuando `!projectRequiredFlow`, p.ej.
  Tareas): Cliente → Proyecto (filtrado por `selectedClientId`, ya filtra `projects` por cliente) →
  Encargado (filtrado por `selectedProjectId`, ya filtra `contacts` por proyecto).

**Decisión**: El segundo flujo (Cliente→Proyecto→Encargado, con Proyecto y Encargado filtrados) ya
existe y cumple exactamente FR-001/FR-002/FR-003/FR-004. Se unifica: el flujo "Proyecto primero"
(`projectRequiredFlow`) se reemplaza por el flujo "Cliente primero" también para Tickets, manteniendo
Proyecto y Cliente como campos requeridos (regla de negocio de OBS-0045 no cambia, solo el orden de
captura). Cliente pasa a ser `required` y editable (ya no `disabled`); Proyecto pasa a filtrarse por
`client_id` en vez de ser el campo libre.

**Alternativa rechazada**: Mantener ambos flujos y solo agregar el filtro faltante a
"Proyecto primero" — se rechaza porque el requerimiento del usuario pide explícitamente que Cliente
sea el primer campo, y mantener dos ramas duplicaría lógica de filtrado sin necesidad.

**Impacto en limpieza de campos dependientes**: ya implementado en el flujo "Cliente primero"
existente (ver `onValuesChange`/estados `selectedClientId`/`selectedProjectId` — a confirmar nombre
exacto de los setters al tocar el código); se reutiliza tal cual.

## Decisión 2 — Campo Skills (US1)

**Hallazgo de código**: El campo `skill_ids` (`Form.Item name="skill_ids"`, línea ~614-619 de
`TicketsPage.tsx`) **ya existe** en el modal de creación, y ya cubre tanto Ticket como Tarea (está
en el bloque común, fuera del `if (isTaskSelected)`). Está gateado por
`canManageSkills = hasPermission('tickets', 'manage_skills')` (solo Coordinador, spec 033) — para
Admin/QM el campo queda **completamente oculto**, no en solo lectura.

`TicketDetailPage.tsx` usa `TicketSkillsSelector.tsx` para editar skills post-creación, también
gateado por el mismo permiso.

**Decisión**: "Restaurar" se interpreta como corregir la experiencia de Admin/QM: el campo debe
seguir siendo visible para ellos (sin poder editarlo), en vez de desaparecer del formulario, igual
al patrón ya usado en otras partes de la app para campos de solo-lectura por permiso (ej. Skills
requeridas en el detalle del ticket). Se cambia `canManageSkills && (...)` por renderizar siempre el
`Form.Item`, con el `Select` en modo `disabled` cuando `!canManageSkills`.

**Alternativa rechazada**: Dejar el campo oculto para Admin/QM tal como está — se rechaza porque
contradice explícitamente el pedido de "restaurar" la selección de Skills.

## Decisión 3 — Hipervínculos en códigos de ticket/tarea (US2)

**Hallazgo de código** (estado actual por pantalla):

| Pantalla | Archivo | Estado actual |
|----------|---------|----------------|
| Lista de Tickets | `frontend/src/pages/TicketsPage.tsx` (columna "Número", línea 363) | Texto plano (`<span>`) |
| Mis Tareas | `frontend/src/pages/MyTasksPage.tsx` (columna "Número", línea 74) | Texto plano |
| Panel de Asignación | `frontend/src/pages/AssignmentPanelPage.tsx` (línea 125) | **Ya es un `<a onClick={navigate(...)}>`** |
| Tablero Kanban | `frontend/src/pages/KanbanPage.tsx` | La tarjeta completa ya navega on-click (línea 295); el código del ticket dentro de la tarjeta no está aislado como link propio |

**Decisión**: Reemplazar el `render` de la columna "Número" en `TicketsPage.tsx` y `MyTasksPage.tsx`
por el mismo patrón `<a onClick={...}>` ya usado en `AssignmentPanelPage.tsx` (evita depender de
`<Link>` de `react-router-dom` para no romper el guardado de `state: { from: ... }` que ya usan estas
pantallas al navegar). En Kanban, se envuelve solo el `<span>` del código dentro de la tarjeta con
`stopPropagation` + `navigate`, sin alterar el drag-and-drop de `@hello-pangea/dnd` (ya excluido del
click en `!dragSnapshot.isDragging`).

**Alternativa rechazada**: Introducir un componente `<TicketCodeLink>` reutilizable nuevo — se
rechaza por Principio VII (alcance mínimo); se prefiere repetir el patrón `<a onClick>` ya validado
en `AssignmentPanelPage.tsx` en los 3 puntos que faltan.

## Decisión 4 — Ordenamiento explícito (US3)

**Hallazgo de código**: El backend (`backend/api/routes/tickets.py` línea 676,
`backend/infra/repositories/ticket_repo.py` línea 23 `_SORTS`) **ya soporta** un parámetro `sort`
con `urgency | created_at | -created_at | priority | -priority | status`. Falta: `-status`, y
ordenar por código (`ticket_number`/`-ticket_number`). El frontend nunca envía `sort` (usa siempre
el default `urgency`); `SortIndicator.tsx` es un `Tag` fijo con el comentario "por ahora fijo — el
default no es configurable desde la UI todavía" (OBS-0028).

**Decisión**:
- Backend: agregar a `_SORTS` las claves `"-status"`, `"code"` (= `ticket_number.asc()`) y
  `"-code"` (`ticket_number.desc()`); actualizar el `@ns.doc` del parámetro `sort`.
- Frontend: reemplazar `SortIndicator` (indicador fijo) por un `<Select>` de ordenamiento
  (Fecha/Prioridad/Código/Estado × Asc/Desc) en `TicketsPage.tsx`, que guarda el `sort` elegido en
  estado local y lo pasa a `ticketService.list(...)`, sin tocar los filtros existentes. Se aplica el
  mismo control en `MyTasksPage.tsx` (reutiliza el mismo `GET /api/tickets` con `own_only`).

**Alternativa rechazada**: Usar el `sorter` nativo de columnas de `antd` `Table` (click en el
encabezado) — se rechaza porque el ordenamiento es server-side (paginado) y el requerimiento pide
"opciones de ordenamiento explícito" separadas del filtrado, más simple de implementar como un
control dedicado que ya sigue el patrón de `SavedFiltersBar`.

## Decisión 5 — Layout horizontal del Detalle del Cliente (US4)

**Hallazgo de código**: `frontend/src/pages/ClientsPage.tsx` línea 382 — el detalle es un `Modal`
(`width={selectedDetail ? 820 : 520}`) con `Tabs` internos que apilan cada sección verticalmente.

**Decisión**: Ampliar `width` del `Modal` (ej. a `1200` o `'90vw'` en pantallas grandes) y
reorganizar el contenido de la(s) pestaña(s) con más campos (datos generales, proyectos, métricas)
usando `Row`/`Col` de `antd` (ya aprobado, sin dependencia nueva) para distribuir en 2-3 columnas en
vez de un único bloque apilado, conservando los mismos `Tabs` como agrupador si ya diferencian
secciones. Con `xs={24}` en `Col` se preserva el apilado en pantallas angostas (responsive nativo de
Ant Design Grid, sin lógica adicional).

**Alternativa rechazada**: Convertir el Modal en una página de ruta propia (`/clients/:id`) — se
rechaza por exceder el alcance pedido ("layout más horizontal y amplio", no una navegación nueva) y
por Principio VII.

## Decisión 6 — Edición de nombre en Catálogos (US5)

**Hallazgo de código**:
- `frontend/src/pages/CatalogsPage.tsx` (`CatalogCard`, catálogos genéricos: tools, processes,
  resolution-types, record-types, teams, access-types) solo permite crear (`POST`) y
  activar/desactivar (`PATCH .../activate|deactivate`). No tiene edición de nombre.
- `frontend/src/pages/SkillsPage.tsx` **ya tiene** edición completa (botón "Editar", modal,
  `skillService.update`) — Skills queda fuera de esta feature, ya cumple el requerimiento.
- Backend: `backend/infra/repositories/catalog_repo.py` (`CatalogRepository`) tiene `create`,
  `get_by_name`, `set_active`, pero no `rename`. `backend/api/routes/catalogs.py` no expone un
  `PATCH /api/catalogs/{catalog}/{id}` de nombre.
- Permisos: `backend/infra/migrations/versions/011_create_tickets.py` define
  `("catalogs", "create"): ["Admin", "Coordinador"]` y `("catalogs", "deactivate")` con los mismos
  roles. No existe `("catalogs", "edit")`.

**Decisión**: Agregar `CatalogRepository.rename(catalog_id, name)` (valida duplicado con
`get_by_name`, igual que `create`) + endpoint `PATCH /api/catalogs/<catalog>/<item_id>`
(sin sufijo, para no chocar con `/activate`/`/deactivate`) gateado por el permiso **ya existente**
`catalogs:create` (mismos roles Admin/Coordinador que ya pueden crear catálogos — evita agregar un
permiso y una migración nuevos para una acción de alcance equivalente). En frontend, agregar botón
"Editar" (ícono lápiz) junto al de activar/desactivar en `CatalogCard`, con un modal simple de un
solo campo `name`, siguiendo el patrón ya usado en `SkillsPage.tsx`.

**Alternativa rechazada**: Crear un permiso `catalogs:edit` nuevo con su propia migración — se
rechaza por Principio VII (alcance mínimo) dado que los roles que deben poder renombrar
(Admin/Coordinador) coinciden exactamente con los que ya tienen `catalogs:create`.

## Resumen de archivos a tocar (alcance, Principio VII)

**Frontend**: `TicketsPage.tsx`, `MyTasksPage.tsx`, `KanbanPage.tsx`, `CatalogsPage.tsx`,
`ClientsPage.tsx`, `catalogService.ts`, `SortIndicator.tsx` (reemplazo o eliminación).

**Backend**: `backend/api/routes/catalogs.py`, `backend/infra/repositories/catalog_repo.py`,
`backend/api/routes/tickets.py` (doc del parámetro `sort`), `backend/infra/repositories/ticket_repo.py`
(`_SORTS`).

Sin migraciones de base de datos, sin dependencias nuevas.
