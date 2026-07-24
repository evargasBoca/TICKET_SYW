---

description: "Task list for Ampliación de Datos Semilla (Usuarios por Rol, Resolutores con Skills y Verificación de Calendarios)"

---

# Tasks: Ampliación de Datos Semilla (Usuarios por Rol, Resolutores con Skills y Verificación de Calendarios)

**Input**: Design documents from `specs/029-seed-usuarios-roles-skills/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Tests**: No se incluyen tareas de test automatizado — la spec no lo pide explícitamente y el
Principio VII de la Constitución restringe agregar suites nuevas para scripts de datos semilla;
la verificación es manual vía `quickstart.md` (Fase de Polish).

**Organization**: Todo el código nuevo vive en un único archivo,
`backend/scripts/seed_dev_users.py` (patrón de `seed_clients_aris_vaxthera.py`), así que la mayoría
de las tareas son secuenciales dentro de ese archivo; solo la reescritura de
`docs/credenciales_dev.txt` toca un archivo distinto.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivo distinto, sin dependencias)
- **[Story]**: A qué historia de usuario pertenece (US1, US2, US3, US4)

## Path Conventions

Proyecto backend puro (sin frontend en esta funcionalidad):
- `backend/scripts/seed_dev_users.py` — script nuevo
- `docs/credenciales_dev.txt` — documento reescrito

---

## Phase 1: Setup

**Purpose**: Crear el archivo del script nuevo con la estructura base

- [X] T001 Crear `backend/scripts/seed_dev_users.py` con docstring, imports (`get_db`/`close_db` de
      `backend.infra.database`; `User`, `Resource`, `Skill` de `backend.domain.entities.*`;
      `UserRepository`, `RoleRepository`, `ResourceRepository`, `SkillRepository`,
      `ClientRepository` de `backend.infra.repositories.*`; `generate_password_hash` de
      `werkzeug.security`; `uuid`, `sys`), función `main() -> None` vacía y el guard
      `if __name__ == "__main__": sys.exit(main())`, siguiendo exactamente la estructura de
      `backend/scripts/seed_clients_aris_vaxthera.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Datos y wiring compartidos que todas las historias necesitan

**⚠️ CRITICAL**: Ninguna historia de usuario puede implementarse antes de completar esta fase

- [X] T002 En `backend/scripts/seed_dev_users.py`, definir a nivel de módulo la constante
      `SEED_PASSWORD_DEV = "SyWork_Dev2026!"` (con comentario apuntando a la migración 009 como
      origen) y la estructura `ROLE_USERS` — lista de `(email, username, role_name)` para los 6
      usuarios internos nuevos de roles no-Resolutor: `admin2@sywork.net`/`admin2`/`Admin`,
      `admin3@sywork.net`/`admin3`/`Admin`, `coordinador2@sywork.net`/`coordinador2`/`Coordinador`,
      `coordinador3@sywork.net`/`coordinador3`/`Coordinador`, `qm2@sywork.net`/`qm2`/`QM`,
      `qm3@sywork.net`/`qm3`/`QM` (ver tabla de `data-model.md`).
- [X] T003 En `backend/scripts/seed_dev_users.py`, definir a nivel de módulo `RESOLVER_USERS` —
      lista de `(email, username)` para los 3 Resolutores nuevos (`resolutor2@sywork.net`,
      `resolutor3@sywork.net`, `resolutor4@sywork.net`) — y `RESOLVER_RESOURCE_SKILLS` — dict que
      mapea los 4 emails de Resolutor (los 3 nuevos + el ya existente `resolutor@sywork.net`) a su
      lista de exactamente 3 códigos de skill cada uno, cubriendo las 8 skills del catálogo al
      menos una vez entre los 4 (usar la combinación de ejemplo de `data-model.md`).
- [X] T004 En `main()` de `backend/scripts/seed_dev_users.py`, instanciar `get_db()`,
      `RoleRepository`, `UserRepository`, `ResourceRepository`, `SkillRepository`,
      `ClientRepository`, y el dict `resumen = {"creados": [], "actualizados": [], "omitidos": []}`,
      igual que la apertura de `main()` en `seed_clients_aris_vaxthera.py`.

**Checkpoint**: Fundación lista — ya se puede implementar cualquier historia de usuario

---

## Phase 3: User Story 1 - Credenciales de prueba para cada rol interno (Priority: P1) 🎯 MVP

**Goal**: Que existan al menos 3 usuarios activos con rol Admin, 3 con Coordinador y 3 con QM, todos
con la contraseña estándar `SyWork_Dev2026!`.

**Independent Test**: Levantar un ambiente desde cero, correr el seed, e iniciar sesión con
`admin2@sywork.net`, `coordinador2@sywork.net` y `qm2@sywork.net` usando `SyWork_Dev2026!`.

### Implementation for User Story 1

- [X] T005 [US1] En `main()` de `backend/scripts/seed_dev_users.py`, iterar `ROLE_USERS`: por cada
      `(email, username, role_name)`, resolver el rol con `roles.get_by_name(role_name)` (`assert`
      que existe, igual que la precondición de `seed_clients_aris_vaxthera.py`); si
      `users.get_by_email(email)` no existe, crear el `User` con
      `password_hash=generate_password_hash(SEED_PASSWORD_DEV)` y registrar en
      `resumen["creados"]`; si existe con un rol distinto, `users.update_role(...)` y registrar en
      `resumen["actualizados"]`; si ya existe con el rol correcto, registrar en
      `resumen["omitidos"]` (mismo patrón de convergencia que el bloque de usuarios de
      `seed_clients_aris_vaxthera.py`).

**Checkpoint**: User Story 1 funcional de forma independiente — se puede iniciar sesión con los 6
usuarios nuevos de Admin/Coordinador/QM.

---

## Phase 4: User Story 2 - Resolutores con perfil de Recurso y skills (Priority: P1)

**Goal**: Al menos 4 usuarios con rol Resolutor, cada uno con un Recurso vinculado y exactamente 3
skills asignadas del catálogo existente.

**Independent Test**: Tras correr el seed, listar Recursos en Maestros y verificar 4 Recursos
vinculados a Resolutores, cada uno con 3 skills activas.

### Implementation for User Story 2

- [X] T006 [US2] En `main()` de `backend/scripts/seed_dev_users.py`, aplicar a `RESOLVER_USERS` la
      misma lógica de convergencia de usuario que T005 (rol `Resolutor`), reutilizando el mismo
      `resumen` (depende de T005 por el patrón de convergencia ya establecido en el archivo).
- [X] T007 [US2] En `main()` de `backend/scripts/seed_dev_users.py`, para cada uno de los 4 emails
      de Resolutor en `RESOLVER_RESOURCE_SKILLS` (los 3 nuevos de T006 + el ya existente
      `resolutor@sywork.net`), resolver su `User` con `users.get_by_email`, luego
      `resources.get_by_user_id(user.id)`; si no existe, crear el `Resource` con
      `full_name`/`email`/`user_id` y registrar en `resumen["creados"]`; si ya existe, reutilizarlo
      y registrar en `resumen["omitidos"]` (depende de T006 para los 3 Resolutores nuevos).
- [X] T008 [US2] En `main()` de `backend/scripts/seed_dev_users.py`, para cada Recurso de T007,
      resolver los 3 códigos de skill de `RESOLVER_RESOURCE_SKILLS` con `skills.get_by_code`,
      `assert`ando que las 3 existen (fallar explícito, FR-010, si el catálogo tuviera menos de 3
      skills activas); comparar el set de skill-ids actual del Recurso contra el objetivo y, si
      difiere, aplicar `resources.update_skills(resource.id, [...])` registrando en
      `resumen["actualizados"]`; si ya coincide, registrar en `resumen["omitidos"]` (depende de
      T007).

**Checkpoint**: User Stories 1 y 2 funcionan de forma independiente — 4 Resolutores con Recurso y 3
skills cada uno.

---

## Phase 5: User Story 3 - Documento único y confiable de credenciales sembradas (Priority: P2)

**Goal**: `docs/credenciales_dev.txt` lista, de forma completa y precisa, todos los usuarios
realmente sembrados (roles internos + Usuario/cliente de Aris/Vaxthera), sin el fixture de tests.

**Independent Test**: Abrir el documento y verificar cada fila contra un ambiente recién sembrado;
confirmar que `contacto.demo@clienteexterno.com` no aparece.

### Implementation for User Story 3

- [X] T009 [US3] Al final de `main()` en `backend/scripts/seed_dev_users.py`, imprimir el resumen
      final (creados/actualizados/omitidos) igual que `seed_clients_aris_vaxthera.py`, incluyendo
      explícitamente la lista de los 13 usuarios internos (4 base de la migración 009 + 9 nuevos de
      T005/T006) con su rol, para poder usarla como fuente al reescribir el documento (depende de
      T005-T008).
- [X] T010 [US3] Reescribir `docs/credenciales_dev.txt` como tabla única y autoritativa con columnas
      Usuario/email | Rol | Cliente/Proyecto | Contraseña, cubriendo: los 4 usuarios base de la
      migración 009, los 9 usuarios nuevos de T005/T006 (todos con `SyWork_Dev2026!`), y los 3
      usuarios "Usuario/cliente" ya sembrados por `seed_clients_aris_vaxthera.py`
      (`Eliseon@aris.ming.com`, `paulaBlanco@aris.ming.com`, `pablo@vaxthera.com`) con su
      cliente/proyecto real y nota de que su contraseña fue generada aleatoriamente en su primera
      ejecución; **eliminar** la fila de `contacto.demo@clienteexterno.com` (fixture exclusivo de
      `backend/tests/conftest.py`, no proviene de ningún seeder real); conservar la advertencia de
      rotación de contraseña antes de Producción real ya presente en el archivo (depende de T009
      para tener el listado final exacto).

**Checkpoint**: Cualquier persona nueva puede iniciar sesión leyendo solo `docs/credenciales_dev.txt`.

---

## Phase 6: User Story 4 - Verificación del calendario/zona horaria de Aris y Vaxthera (Priority: P3)

**Goal**: Confirmar (y corregir si hiciera falta) que Aris tiene timezone `America/Bogota` y
Vaxthera `America/Guayaquil`.

**Independent Test**: Tras correr el seed, consultar ambos clientes y confirmar su timezone.

### Implementation for User Story 4

- [X] T011 [US4] En `main()` de `backend/scripts/seed_dev_users.py`, agregar un bloque que itere
      `[("Aris", "America/Bogota"), ("Vaxthera", "America/Guayaquil")]`, usando
      `clients.get_by_name(name)` y comparando/corrigiendo `existing.timezone` con
      `clients.update(existing)` solo si difiere (mismo criterio de convergencia que el bloque de
      clientes de `seed_clients_aris_vaxthera.py`), registrando en `resumen["actualizados"]` u
      `resumen["omitidos"]` según corresponda.

**Checkpoint**: Las 4 historias de usuario están implementadas de forma independiente y verificable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar `close_db()`, limpiar el `print` final y validar todo el flujo contra Docker real

- [X] T012 Confirmar que `main()` en `backend/scripts/seed_dev_users.py` llama `close_db()` antes de
      imprimir el resumen y retorna `0` (o el código de salida apropiado), igual que
      `seed_clients_aris_vaxthera.py`.
- [X] T013 Ejecutar la validación completa de `quickstart.md` contra un ambiente Docker real: correr
      el script dos veces seguidas (idempotencia), iniciar sesión con usuarios de los 4 roles
      internos, verificar los 4 Recursos con 3 skills en Maestros, revisar
      `docs/credenciales_dev.txt`, y confirmar el timezone de Aris/Vaxthera.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las historias
- **User Story 1 (Phase 3)**: Depende de Foundational
- **User Story 2 (Phase 4)**: Depende de Foundational; reutiliza el patrón de convergencia de
  usuario de US1 (T005) pero es una historia separada y verificable por su cuenta
- **User Story 3 (Phase 5)**: Depende de que US1 y US2 hayan terminado de crear/actualizar usuarios
  (T005-T008), porque el documento debe reflejar el estado final real
- **User Story 4 (Phase 6)**: Depende solo de Foundational — no depende de US1/US2/US3, podría
  implementarse en cualquier momento después de la Fase 2
- **Polish (Phase 7)**: Depende de que las 4 historias estén completas

### Within the File

Todas las tareas T002-T011 modifican el mismo archivo (`backend/scripts/seed_dev_users.py`), así que
se ejecutan **secuencialmente** en el orden dado — no hay oportunidades reales de paralelismo dentro
del script. T010 (`docs/credenciales_dev.txt`) es la única tarea de un archivo distinto, pero depende
del contenido final de T009, por lo que tampoco es paralelizable en la práctica.

### Parallel Opportunities

Ninguna significativa: el alcance completo de esta funcionalidad es un único script nuevo más un
documento que depende de su resultado final. Esto es intencional dado el Principio VII de la
Constitución (alcance de sesión acotado).

---

## Implementation Strategy

### MVP First (User Stories 1 + 2, ambas P1)

1. Completar Fase 1: Setup
2. Completar Fase 2: Foundational (bloqueante)
3. Completar Fase 3 (US1) y Fase 4 (US2) — ambas P1, entregan el valor central: usuarios de prueba
   por rol + Resolutores con Recurso/skills para pruebas de asignación
4. **DETENER y VALIDAR**: correr `quickstart.md` pasos 1-3 contra Docker real

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 → validar login por rol → (MVP parcial)
3. US2 → validar Recursos/skills → MVP completo
4. US3 → validar documento de credenciales
5. US4 → validar timezone Aris/Vaxthera
6. Polish → `quickstart.md` completo de punta a punta

---

## Notes

- No hay tareas `[P]` en esta lista: todo el código nuevo vive en un único archivo pequeño, y la
  única tarea sobre un archivo distinto (T010) depende del resultado final de las anteriores.
- Cada tarea de las Fases 3-6 debe dejar el script en un estado ejecutable y re-ejecutable
  (idempotente) — no dividir una historia en un estado a medias entre tareas.
- Verificar manualmente contra Docker real (Fase 7) — no se agregan pruebas automatizadas nuevas
  (Principio VII).
