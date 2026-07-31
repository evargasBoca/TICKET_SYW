# Data Model: Referencia a Subtareas dentro de "Clasificación"

Sin cambios de esquema, sin cambios de contrato de API. `ticket.subtasks` (`TicketListItem[]`,
ya expuesto por `GET /api/tickets/{id}` desde spec 009 y consumido por el frontend desde spec 036
para el conteo de la Card lateral "Subtareas") es la única fuente de datos: esta feature solo
agrega un segundo punto de renderizado del mismo array, dentro de la Card "Clasificación".

## Frontend — sin cambios de tipos

`frontend/src/types/ticket.ts`: `TicketDetail.subtasks: TicketListItem[]` ya existe (spec 009) y
ya tiene los campos necesarios (`id`, `ticket_number`, `title`) para el nuevo `Descriptions.Item`
— no se agrega ni modifica ningún campo.
