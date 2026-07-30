# Data Model: Cascada, Hipervínculos, Catálogos y Layout de Cliente

Sin migraciones de base de datos. Esta feature reutiliza entidades y relaciones ya existentes.

## Entidades existentes reutilizadas (sin cambios de esquema)

- **Ticket/Tarea** (`ticket_model.TicketModel`): `client_id`, `project_id`, `client_contact_id`,
  `ticket_number` (código), `skill_ids` (vía `ticket_skills_table`) — todos ya existentes.
- **Proyecto** (`ProjectModel`): `client_id` (FK) — ya usado para filtrar por cliente.
- **Usuario/cliente (Encargado)** (`ClientContactModel` / relación proyecto↔encargado de
  `specs/015-encargado-multiples-proyectos`) — ya usado para filtrar por proyecto.
- **Registro de Catálogo** (`CATALOG_MODELS`: tools, processes, resolution-types, record-types,
  teams, access-types): `id`, `name`, `active` (+ `color_index` en `access-types`). Se agrega
  capacidad de actualizar `name` sin nuevo atributo.

## Cambio de comportamiento (no de esquema)

- `CatalogRepository.rename(catalog_id: UUID, name: str) -> dict | None`: nuevo método análogo a
  `set_active`, actualiza `model.name`, valida duplicado antes de llamar (misma validación que
  `create`: `get_by_name`).
- `_SORTS` en `ticket_repo.py` gana 3 claves nuevas (`-status`, `code`, `-code`) mapeadas a columnas
  ya existentes de `TicketModel` (`status`, `ticket_number`). No es una entidad nueva, es una
  extensión del diccionario de ordenamiento ya existente.

## Validaciones relevantes (ya existentes, reafirmadas por esta feature)

- Duplicado de nombre de catálogo: `name_duplicate` (409) — mismo código de error que ya usa
  `POST /api/catalogs/{catalog}`, reutilizado por el nuevo `PATCH`.
- Cliente/Proyecto/Encargado inconsistentes: los códigos de error `client_inactive`,
  `project_inactive`, `contact_not_in_project`, `client_contact_mismatch` ya existen
  (`TICKET_ERROR_RULES` en `TicketsPage.tsx`) y se conservan sin cambios — la cascada en el
  frontend solo reduce la probabilidad de que ocurran, no reemplaza la validación de backend.
