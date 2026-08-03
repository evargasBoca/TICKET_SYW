# Contrato: Herencia de Subtareas y campo "Tarea Padre"

Extiende `backend/api/routes/tickets.py` (namespace `tickets`, ya documentado en Swagger). No
agrega rutas nuevas — extiende el comportamiento y la respuesta de dos endpoints existentes.

## `POST /api/tickets` — herencia al crear una Subtarea

Sin cambios en el contrato de entrada. Cuando el payload incluye `parent_task_id` (Subtarea) y
**no** incluye alguno de estos tres campos, el valor se copia de la Tarea padre en vez del
default genérico:

| Campo del payload (opcional, sin cambios) | Si se omite y hay `parent_task_id` |
|---|---|
| `escalation_level` | Copia `escalation_level` de la Tarea padre (en vez de `"n2"`) |
| `client_contact_id` | Copia `client_contact_id` de la Tarea padre (en vez de `null`) |
| `skill_ids` (vía `PATCH /skills` posterior — ver abajo) | Copia el set de Skills de la Tarea padre (en vez de vacío) |

Las Skills requeridas no viajan en `POST /api/tickets` (ver research.md de spec 011): se
aplican con una llamada interna a `TicketRepository.update_skills` inmediatamente después de
crear la Subtarea, dentro de la misma transacción de request — no es un segundo request HTTP.

**Respuestas**: sin cambios (`201` con el mismo `_ticket_detail_out`).

## `GET /api/tickets/{id}` — campo `parent` (aditivo)

**Respuesta** (`_ticket_detail_out`), campo nuevo:

```json
{
  "parent": { "id": "uuid", "ticket_number": "TK-000123", "title": "Título de la Tarea padre" }
}
```

- Presente solo cuando `ticket.parent_task_id` no es null (i.e., el registro es una Subtarea).
- `null` en cualquier otro caso.
- El campo `parent_task_id` (string UUID o null) ya existente se conserva sin cambios, por
  compatibilidad con consumidores actuales.

**Respuestas**: sin cambios de status code — mismo `200`/`400`/`401`/`403`/`404`/`500` ya
documentados.
