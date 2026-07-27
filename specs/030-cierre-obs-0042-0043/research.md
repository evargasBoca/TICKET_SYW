# Research: Cierre de OBS-0042/OBS-0043

## 1. OBS-0042 — Layout del Detalle del Ticket

**Situación actual** (`frontend/src/pages/TicketDetailPage.tsx`): la vista usa un `Row` de Ant Design con dos columnas (`Col xs={24} lg={14}` y `Col xs={24} lg={10}`).

- Columna principal (`lg={14}`): Descripción → Registros de tiempo → **"Comentarios y acciones"** (`CommentThread` + `CommentComposer`, y para Tareas también `TaskStatusChanger`) → Historial de estados → Reasignaciones.
- Columna lateral (`lg={10}`): SLA → Sesión de trabajo (Focus Room) → **"Clasificación"** (`Descriptions` con Cliente, Usuario/cliente, Proyecto, etc.) → Subtareas.

Todo el scroll es el de la página completa (`window` scroll) — no hay ningún contenedor con `overflow` propio. El historial de comentarios (`Timeline` dentro de `CommentThread`) crece sin límite de alto, empujando el resto de tarjetas de esa misma columna hacia abajo.

- **Decisión**: intercambiar la posición de las dos Cards — "Clasificación" pasa a la columna principal (en el lugar que hoy ocupa la Card "Comentarios y acciones"), y "Comentarios y acciones" pasa a la columna lateral. Dentro de la Card "Comentarios y acciones" en su nueva ubicación, el bloque `CommentThread` (el `Timeline`) se envuelve en un contenedor con `max-height` fijo y `overflow-y: auto`; `CommentComposer` (y `TaskStatusChanger` para Tareas) queda fuera de ese contenedor, siempre visible debajo/encima del scroll interno.
- **Rationale**: es la reorganización explícitamente pedida en OBS-0042 (criterios de aceptación 1 y 2), reutiliza los mismos componentes `Card`/`Descriptions`/`Timeline` ya existentes (Principio II — componentes "tontos", sin lógica nueva) y resuelve el scroll infinito sin tocar `CommentThread`/`CommentComposer` internamente (basta el contenedor que los envuelve en `TicketDetailPage.tsx`).
- **Alternativas consideradas**:
  - *Paginar o virtualizar el `Timeline` de comentarios* (ej. "cargar más"): resuelve el alto pero cambia el comportamiento de carga de datos (`ticketService.get` ya trae todos los comentarios en el detalle) y excede el alcance de OBS-0042, que pide un contenedor con scroll interno, no paginación.
  - *Sticky real vía `position: sticky` en la columna lateral completa*: Ant Design `Col` ya se comporta razonablemente con `position: sticky` + `top` en pantallas `lg+`; se adopta para que la Card "Comentarios y acciones" (ya reubicada) permanezca visible sin depender de JS de scroll (el enfoque ya usado en `timeExpanded`/`onScroll` de esta misma página se descarta para este caso por ser más frágil y no pedido por el criterio de aceptación).

## 2. OBS-0043 — Cliente en SLA Configurable

**Dato ya existente**: `ProjectListItem` (`frontend/src/types/project.ts`) ya expone `client_id` y `client_name` — `projectService.list()` (usado por `SlaRulesPage.tsx` para poblar tanto el filtro como el formulario) ya trae ese dato. **No se requiere cambio de backend para el selector "Filtrar por proyecto" ni para el `Select` de proyecto en `SlaRuleForm.tsx`** — solo cambiar el `label` renderizado de `p.name` a `` `${p.client_name} — ${p.name}` ``.

**Dato faltante**: la tabla de reglas de SLA (`SlaRulesPage.tsx`, columna `Proyecto`) consume `SlaRule.project_name` (`frontend/src/types/sla.ts`), que **no** incluye el cliente. El backend (`backend/api/routes/sla_rules.py::_serialize`) solo resuelve `ProjectRepository(db).get_by_id(rule.project_id)` para obtener `project.name`; no consulta el `Client`.

- **Decisión**: ampliar `_serialize()` en `sla_rules.py` para resolver también el `Client` del proyecto (`ClientRepository(db).get_by_id(project.client_id)`) y agregar `client_id`/`client_name` al payload de `SlaRule` (ambos `GET`/`POST`/`PATCH` ya comparten esa función). En el frontend, agregar `client_id`/`client_name` a la interfaz `SlaRule` y una columna nueva "Cliente" en `SlaRulesPage.tsx` que renderiza `rule.client_name`.
- **Rationale**: es una ampliación aditiva de un payload ya existente (mismo patrón que `assigned_at`/`sla_effective_start` documentado en `specs/028-.../contracts/api-changes.md`), no rompe consumidores actuales del contrato, y reutiliza `ClientRepository` ya existente (Principio I/II — sin lógica de negocio nueva, solo un join de lectura adicional en la capa de presentación/serialización).
- **Alternativas consideradas**:
  - *Resolver el cliente en el frontend* buscando `projects.find(p => p.id === rule.project_id)?.client_name` en `SlaRulesPage.tsx`: evita el cambio de backend, pero es fráil ante filtros de `projectService.list()` (ej. `active: true` ya usado ahí) que podrían excluir el proyecto de una regla antigua/inactiva y dejar la columna vacía sin motivo aparente. Se descarta a favor de que el backend sea la fuente de verdad del dato mostrado en la tabla, consistente con Principio I (el dato de negocio se resuelve donde vive, no se re-derive en la UI).
  - *Desnormalizar `client_id`/`client_name` en `SlaRuleModel` (columna nueva + migración)*: innecesario — el dato ya es derivable en cada lectura vía `project.client_id` sin joins costosos (volumen bajo, reglas de SLA son decenas, no miles), y evita una migración Alembic para este alcance.

## 3. Trazabilidad UAT

Ambas observaciones (`OBS-0042`, `OBS-0043`) ya están documentadas con criterios de aceptación explícitos en `UAT/01_Iterations/ITER-007/ITER-007.md` (iteración ya `Cerrada`, inmutable) y reflejadas como filas `Abierta` en `UAT/02_Backlog/BACKLOG.md`. Siguiendo `UAT/README.md` (rol Desarrollador), al terminar la implementación se actualiza únicamente `BACKLOG.md` a `Lista para Validar` — nunca se reescribe `ITER-007.md`.
