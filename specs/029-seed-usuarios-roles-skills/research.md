# Research: Ampliación de Datos Semilla

No quedaban `NEEDS CLARIFICATION` en el Technical Context del plan (el alcance es un script backend
puro, sin ambigüedad de stack). Este documento registra las decisiones de diseño tomadas durante la
planificación, con su justificación y alternativas descartadas.

## 1. Nuevo script idempotente vs. editar la migración 009

**Decision**: Implementar la ampliación como un nuevo script Python re-ejecutable,
`backend/scripts/seed_dev_users.py`, siguiendo el mismo patrón de
`backend/scripts/seed_clients_aris_vaxthera.py` (invocado con
`docker exec sywork_backend python -m backend.scripts.seed_dev_users`).

**Rationale**: La migración 009 ya se ejecutó (`alembic upgrade head`) en los ambientes Dev/Test/Prod
existentes; Alembic no vuelve a correr una migración ya aplicada, así que editarla no tendría efecto
en ningún ambiente real y además el usuario pidió explícitamente no tocar la arquitectura de
autenticación. Un script aparte, idempotente y re-ejecutable, es el patrón ya validado en este
proyecto para ampliar datos semilla sin migraciones nuevas.

**Alternatives considered**:
- *Editar migración 009 directamente*: rechazado — no se re-ejecuta en ambientes ya migrados; editar
  una migración histórica es un anti-patrón de Alembic.
- *Nueva migración Alembic que inserte los usuarios*: rechazado — una migración de esquema no es la
  herramienta correcta para datos de conveniencia de desarrollo/pruebas que deben poder re-sembrarse
  o ajustarse libremente; el proyecto ya resolvió este mismo problema con un script (spec 026) en
  lugar de una migración, y esta funcionalidad sigue ese mismo precedente.

## 2. Contraseña unificada

**Decision**: Reutilizar el valor exacto ya usado como contraseña semilla estándar del proyecto,
`SyWork_Dev2026!` (la misma constante `SEED_PASSWORD_DEV` de la migración 009), para los nuevos
usuarios de los 4 roles internos.

**Rationale**: FR-005 pide explícitamente una contraseña unificada; introducir una segunda contraseña
"estándar" distinta rompería la utilidad de tener un único valor documentado y memorizable para
pruebas manuales.

**Alternatives considered**: contraseñas aleatorias por usuario (rechazado — contradice el
requerimiento explícito y ya es el patrón usado para los usuarios de cliente reales en
`seed_clients_aris_vaxthera.py`, donde SÍ tiene sentido por no ser cuentas de prueba genéricas).

## 3. Distribución de skills entre los 4 Resolutores

**Decision**: Repartir 3 skills por Resolutor tomadas del catálogo de 8 ya sembradas
(`JDE_GL`, `JDE_AP`, `JDE_AR`, `ORACLE_FUSION`, `ORACLE_CRM`, `API_REST`, `SQL_ORACLE`,
`ORCHESTRATOR`), con combinaciones distintas y parcialmente solapadas entre los 4 Recursos (no las
mismas 3 para todos).

**Rationale**: Las funcionalidades ya existentes de sugerencia de carga/disponibilidad y asignación
por skill (specs 010, 023, 024) necesitan variedad de candidatos para que sus reglas de "menor carga"
y "coincidencia de skill" tengan algo real que comparar; 4 Recursos con exactamente las mismas 3
skills no aportarían ese valor de prueba.

**Alternatives considered**: mismas 3 skills para los 4 (rechazado, sin variedad útil); skills
aleatorias en cada ejecución (rechazado — rompería la idempotencia exigida por FR-006, ya que
re-ejecutar el script debe converger siempre al mismo estado final).

## 4. Verificación de timezone de Aris/Vaxthera

**Decision**: La verificación/corrección de zona horaria de Aris (`America/Bogota`) y Vaxthera
(`America/Guayaquil`) se ejecuta dentro del mismo script nuevo, reutilizando
`ClientRepository.get_by_name` / `.update`, con el mismo criterio de convergencia que ya usa
`seed_clients_aris_vaxthera.py` (comparar y corregir solo si difiere).

**Rationale**: Es una comprobación de dos líneas sobre datos que ya gestiona ese mismo patrón de
convergencia; no amerita un script o proceso separado.

**Alternatives considered**: script de verificación aparte (rechazado — sobre-ingeniería para una
comprobación de 2 clientes ya cubierta por el mismo patrón).

## 5. Reescritura de `docs/credenciales_dev.txt`

**Decision**: Reescribir el archivo completo como una única tabla autoritativa que liste todos los
usuarios realmente sembrados por scripts/migraciones contra una base de datos real (migración 009
ampliada + `seed_dev_users.py` nuevo + `seed_clients_aris_vaxthera.py` existente), eliminando la fila
de `contacto.demo@clienteexterno.com` (confirmado como fixture exclusivo de
`backend/tests/conftest.py`, nunca creado por un seeder real).

**Rationale**: El archivo actual está en un estado inconsistente (contenido duplicado/desordenado,
según `git status` de este repo) y mezcla un dato de pruebas automatizadas con usuarios reales,
generando confusión sobre qué credenciales funcionan. FR-007/FR-008 piden explícitamente que el
documento sea completo y libre de fixtures de test.

**Alternatives considered**: apéndice incremental sin tocar el contenido previo (rechazado — el
archivo actual ya está desordenado; un parche sobre esa base perpetuaría el problema en vez de
resolverlo, y el spec pide el estado final completo, no un diff).
