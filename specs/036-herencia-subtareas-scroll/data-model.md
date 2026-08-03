# Data Model: Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering

Sin migración de base de datos. Todas las columnas/relaciones ya existen
(`tickets.escalation_level`, `tickets.client_contact_id`, `tickets.parent_task_id`,
`ticket_skills` M:N). Esta feature solo agrega comportamiento de copia en creación y campos
serializados adicionales de solo lectura sobre el modelo `Ticket` ya vigente.

## Ticket (sin cambios de esquema)

Campos relevantes ya existentes, reutilizados sin modificar:

| Campo | Tipo | Uso en esta feature |
|-------|------|----------------------|
| `parent_task_id` | UUID nullable, FK autorreferencial a `tickets.id` | Ya distingue Subtarea de Tarea; fuente de la herencia y del hipervínculo inverso |
| `escalation_level` | Text (`n1`\|`n2`\|`n3`, `ESCALATION_LEVELS`) | Se copia de la Tarea padre a la Subtarea si no viene explícito en el alta |
| `client_contact_id` | UUID nullable, FK a `client_contacts.id` | Se copia de la Tarea padre a la Subtarea si no viene explícito en el alta |
| `skills` (relación M:N vía `ticket_skills_table`) | lista de `Skill` | Se copia el set completo de la Tarea padre a la Subtarea si el alta no trae `skill_ids` propios |

## Contrato de API — campos aditivos (no rompen consumidores existentes)

### `GET /api/tickets/{id}` (respuesta de `_ticket_detail`)

- **`parent`** *(nuevo, objeto o `null`)*: `{ "id": string, "ticket_number": string, "title": string }`
  — solo presente cuando `ticket.parent_task_id` no es null. El campo `parent_task_id` (string
  o null) ya existente se conserva sin cambios.

### `POST /api/tickets` (creación de Subtarea, `parent_task_id` en el payload)

- Sin cambios de contrato de entrada: `escalation_level`, `client_contact_id` y `skill_ids`
  siguen siendo opcionales en el payload. Cambia únicamente el comportamiento interno: si
  `parent_task_id` está presente y alguno de esos tres no vino en el payload, el valor se copia
  de la Tarea padre en vez de aplicar el default genérico (`"n2"` para `escalation_level`,
  `None` para `client_contact_id`, `[]` para skills).

## Frontend — tipos (aditivo)

`frontend/src/types/ticket.ts`, interfaz `TicketDetail`: se agrega

```ts
parent: { id: string; ticket_number: string; title: string } | null
```

Sin cambios en `TicketListItem` ni en los tipos de listado/Kanban (el campo solo aplica al
detalle completo de una Subtarea).
