# Data Model: Ampliación de Datos Semilla

Esta funcionalidad **no crea tablas ni columnas nuevas**. Solo agrega/asegura filas en entidades ya
existentes, reutilizando los repositorios de Capa 2 ya presentes en `backend/infra/repositories/`.

## Entidades involucradas (sin cambios de esquema)

### User (`users`, `backend/domain/entities/user.py`)

Campos relevantes ya existentes: `id`, `email`, `username`, `role` (FK a `roles`), `password_hash`,
`active`.

**Nuevas filas a converger** (creadas si no existen, actualizadas al rol esperado si el email ya
existe con otro rol — mismo criterio que `seed_clients_aris_vaxthera.py`):

| username | email | rol | contraseña |
|---|---|---|---|
| admin2 | admin2@sywork.net | Admin | `SyWork_Dev2026!` |
| admin3 | admin3@sywork.net | Admin | `SyWork_Dev2026!` |
| coordinador2 | coordinador2@sywork.net | Coordinador | `SyWork_Dev2026!` |
| coordinador3 | coordinador3@sywork.net | Coordinador | `SyWork_Dev2026!` |
| qm2 | qm2@sywork.net | QM | `SyWork_Dev2026!` |
| qm3 | qm3@sywork.net | QM | `SyWork_Dev2026!` |
| resolutor2 | resolutor2@sywork.net | Resolutor | `SyWork_Dev2026!` |
| resolutor3 | resolutor3@sywork.net | Resolutor | `SyWork_Dev2026!` |
| resolutor4 | resolutor4@sywork.net | Resolutor | `SyWork_Dev2026!` |

Junto con el `resolutor@sywork.net` ya sembrado por la migración 009, esto da el mínimo de 4
Resolutores exigido por FR-002.

### Resource (`resources`, `backend/domain/entities/resource.py`)

Campos relevantes: `id`, `full_name`, `email`, `user_id` (FK a `users.id`), `skills` (relación a
`resource_skills`), `calendar_country`, `timezone`.

**Nuevas filas a converger** — un Recurso por cada uno de los 4 Resolutores (los 3 nuevos + el
`resolutor@sywork.net` preexistente, que hoy no tiene Recurso, ver research.md/FR-003):

| Recurso (full_name) | vinculado a (email) |
|---|---|
| Resolutor Semilla 1 | resolutor@sywork.net |
| Resolutor Semilla 2 | resolutor2@sywork.net |
| Resolutor Semilla 3 | resolutor3@sywork.net |
| Resolutor Semilla 4 | resolutor4@sywork.net |

Si el Recurso de `resolutor@sywork.net` ya existe (por ejemplo, creado manualmente por alguien),
el script no lo duplica: lo reutiliza y solo completa las skills faltantes hasta 3.

### Skill / resource_skills (`skills`, `resource_skills`)

Sin filas nuevas en `skills` (catálogo de 8 ya existente, ver constitution/research.md). Nuevas filas
en `resource_skills` (asociación Recurso↔Skill), 3 por cada uno de los 4 Recursos anteriores:

| Recurso | Skills asignadas |
|---|---|
| Resolutor Semilla 1 | `JDE_GL`, `JDE_AP`, `API_REST` |
| Resolutor Semilla 2 | `JDE_AR`, `ORACLE_FUSION`, `SQL_ORACLE` |
| Resolutor Semilla 3 | `ORACLE_CRM`, `API_REST`, `ORCHESTRATOR` |
| Resolutor Semilla 4 | `SQL_ORACLE`, `JDE_GL`, `ORACLE_FUSION` |

(Combinación ilustrativa que cubre las 8 skills al menos una vez entre los 4 Recursos, con
solapamiento parcial para pruebas de "coincidencia de skill" entre varios candidatos — ver
research.md #3. La lista exacta puede ajustarse en `tasks.md`/implementación siempre que mantenga:
exactamente 3 skills por Recurso, no las mismas 3 combinaciones para los 4, y las 8 skills cubiertas
al menos una vez.)

### Client (`clients`) — solo verificación, sin filas nuevas

| Cliente | timezone esperado |
|---|---|
| Aris | `America/Bogota` |
| Vaxthera | `America/Guayaquil` |

El script confirma el valor y lo corrige si estuviera desalineado (mismo criterio de convergencia que
`seed_clients_aris_vaxthera.py`); no crea clientes nuevos.

## Documento de credenciales (`docs/credenciales_dev.txt`)

No es una entidad de base de datos, pero es un artefacto de esta funcionalidad (FR-007/FR-008).
Estructura final: una única tabla con columnas `Usuario/email | Rol | Cliente/Proyecto | Contraseña`,
cubriendo:

1. Los 4 usuarios base de la migración 009 (`admin`, `coordinador`, `qm`, `resolutor`) — sin
   cliente/proyecto asociado (roles internos).
2. Los 9 usuarios nuevos de esta funcionalidad — sin cliente/proyecto asociado (roles internos).
3. Los 3 usuarios "Usuario/cliente" ya sembrados por `seed_clients_aris_vaxthera.py`
   (`Eliseon@aris.ming.com`, `paulaBlanco@aris.ming.com`, `pablo@vaxthera.com`) — con su
   cliente/proyecto real, y su contraseña marcada como generada aleatoriamente en su primera
   ejecución (no reproducible en texto plano, a diferencia de la contraseña unificada de los roles
   internos).

Se **elimina** la fila de `contacto.demo@clienteexterno.com` (fixture exclusivo de
`backend/tests/conftest.py`, no proviene de ningún seeder real — FR-008).
