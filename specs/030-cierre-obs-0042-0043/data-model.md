# Data Model: Cierre de OBS-0042/OBS-0043

Este feature no agrega entidades ni tablas nuevas. Amplía, de forma aditiva, la representación (payload/UI) de entidades ya existentes.

## SlaRule (payload de API — `frontend/src/types/sla.ts`, `backend/api/routes/sla_rules.py`)

| Campo | Tipo | Origen | Nota |
|---|---|---|---|
| `id` | string (uuid) | ya existente | sin cambios |
| `project_id` | string (uuid) | ya existente | sin cambios |
| `project_name` | string \| null | ya existente | sin cambios |
| `client_id` | string (uuid) \| null | **nuevo** | derivado de `Project.client_id` vía `ClientRepository.get_by_id` en `_serialize()` (OBS-0043) |
| `client_name` | string \| null | **nuevo** | `Client.name` del cliente dueño del proyecto de la regla (OBS-0043) |
| `priority` | enum (`critical\|high\|medium\|low`) | ya existente | sin cambios |
| `contact_minutes` | integer | ya existente | sin cambios |
| `execution_minutes` | integer | ya existente | sin cambios |
| `active` | boolean | ya existente | sin cambios |
| `created_at` | string (iso8601) | ya existente | sin cambios |

No agrega campos de request (`SlaRuleInput`/`SlaRulePatchInput` no cambian): `client_id`/`client_name` son siempre derivados server-side a partir de `project_id`, nunca aceptados como input.

## ProjectListItem (frontend, `frontend/src/types/project.ts`)

Sin cambios de tipo — `client_id`/`client_name` ya existían y son la fuente reutilizada para el selector "Filtrar por proyecto" y el `Select` de proyecto en `SlaRuleForm.tsx` (OBS-0043).

## Vista Detalle del Ticket (frontend, sin entidad nueva)

Reordenamiento puramente visual de dos secciones ya existentes (`TicketDetailPage.tsx`), sin cambio de datos ni de props de los componentes `CommentThread`, `CommentComposer`, `TaskStatusChanger` ni del bloque `Descriptions` de "Clasificación" (OBS-0042):

- La Card "Comentarios y acciones" se mueve de la columna principal (`Col lg={14}`) a la columna lateral (`Col lg={10}`); dentro de ella, el contenido de `CommentThread` queda envuelto en un contenedor con alto máximo y scroll interno propio.
- La Card "Clasificación" se mueve de la columna lateral a la columna principal, en el lugar donde antes estaba "Comentarios y acciones".

## Observación UAT (framework `UAT/`, no es entidad de aplicación)

| Campo | Valor tras este feature |
|---|---|
| `OBS-0042` — Estado | `Abierta` → `Lista para Validar` (en `BACKLOG.md`) |
| `OBS-0043` — Estado | `Abierta` → `Lista para Validar` (en `BACKLOG.md`) |

`ITER-007.md` no se modifica en su contenido narrativo (ver `UAT/CONVENTIONS.md` — reglas de inmutabilidad).
