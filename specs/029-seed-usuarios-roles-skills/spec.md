# Feature Specification: Ampliación de Datos Semilla (Usuarios por Rol, Resolutores con Skills y Verificación de Calendarios)

**Feature Branch**: `029-seed-usuarios-roles-skills`

**Created**: 2026-07-24

**Status**: Draft

**Input**: User description: "Ampliación de Datos Semilla (Usuarios por Rol, Resolutores con Skills y Verificación de Calendarios) — actualizar y expandir el script de datos semilla (Seeders/Fixtures) para que, al instalar la aplicación en cualquier entorno, se generen los usuarios, perfiles, skills y credenciales estándar requeridos para desarrollo y pruebas: 2 usuarios adicionales por cada rol interno existente, mínimo 4 usuarios con rol Resolutor (cada uno con perfil de Recurso y 3 skills asignadas), contraseña unificada para todos los usuarios sembrados, documentación de credenciales actualizada (Nombre, Correo, Rol, Proyecto/Cliente si aplica, Contraseña), y verificación de que los clientes semilla Aris (America/Bogota) y Vaxthera (America/Guayaquil) mantienen su calendario/zona horaria correctamente enlazados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Credenciales de prueba para cada rol interno (Priority: P1)

Como desarrollador o QA que acaba de levantar un ambiente (local, Docker, Test o Producción de validación), necesito poder iniciar sesión con al menos 3 usuarios distintos por cada rol interno (Admin, Coordinador, QM, Resolutor) usando una contraseña única y conocida, para poder validar pantallas, permisos y flujos de colaboración entre varios usuarios del mismo rol sin depender de datos reales de cliente.

**Why this priority**: Sin esto, cualquier prueba manual o exploratoria que requiera "dos Coordinadores" o "dos QM" interactuando (por ejemplo, reasignar un ticket de un resolutor a otro, o comparar permisos entre dos cuentas del mismo rol) no se puede hacer hoy, porque el seed actual (migración 009) crea exactamente 1 usuario por rol interno.

**Independent Test**: Levantar un ambiente desde cero, correr las migraciones y el seed, y verificar por consulta directa (o vía Login) que existen al menos 3 usuarios activos para Admin, Coordinador y QM, y que todos aceptan la misma contraseña.

**Acceptance Scenarios**:

1. **Given** una base de datos recién migrada sin datos previos, **When** se ejecuta el proceso de datos semilla, **Then** existen al menos 3 usuarios activos con rol Admin, 3 con rol Coordinador y 3 con rol QM, cada uno con email y username distintos.
2. **Given** los usuarios sembrados por esta funcionalidad, **When** un usuario intenta iniciar sesión con cualquiera de esos usuarios y la contraseña estándar documentada, **Then** el inicio de sesión es exitoso.
3. **Given** un ambiente donde el seed ya se ejecutó una vez, **When** se vuelve a ejecutar el mismo proceso de datos semilla, **Then** no se crean usuarios duplicados ni se generan errores, y el estado final es el mismo que tras la primera ejecución.

---

### User Story 2 - Resolutores con perfil de Recurso y skills para pruebas de asignación (Priority: P1)

Como Coordinador o QM que prueba la asignación y reasignación de tickets/tareas por carga de trabajo y disponibilidad (specs 023/024), necesito al menos 4 Resolutores, cada uno con su perfil de Recurso creado y 3 skills asignadas, para poder ejercitar escenarios realistas de asignación por skill y balanceo de carga entre varios candidatos.

**Why this priority**: Las funcionalidades de sugerencia de carga/disponibilidad y de asignación por skill requeridas (spec 010, 023, 024) necesitan varios Recursos candidatos con skills distintas para que sus reglas de "menor carga" y "coincidencia de skill" tengan algo que comparar; con un solo Resolutor sembrado hoy, esas pruebas no son representativas.

**Independent Test**: Tras correr el seed, listar Recursos en Maestros y verificar que existen al menos 4 Recursos vinculados a un usuario con rol Resolutor, cada uno con exactamente 3 skills activas asignadas.

**Acceptance Scenarios**:

1. **Given** una base de datos recién migrada, **When** se ejecuta el proceso de datos semilla, **Then** existen al menos 4 usuarios con rol Resolutor y cada uno tiene un Recurso asociado (mismo `user_id`).
2. **Given** los Recursos sembrados para los Resolutores, **When** se consulta el perfil de cada uno, **Then** cada Recurso tiene exactamente 3 skills asignadas, tomadas del catálogo de skills ya existente en el sistema.
3. **Given** que el proceso de datos semilla se ejecuta más de una vez, **When** ya existen 4 o más Resolutores con Recurso y skills, **Then** el proceso no crea Recursos ni asignaciones de skill duplicadas.

---

### User Story 3 - Documento único y confiable de credenciales sembradas (Priority: P2)

Como persona nueva en el proyecto (desarrollador, QA o alguien validando UAT), necesito un único documento que liste todos los usuarios que crean los scripts de datos semilla —con su nombre, correo, rol, cliente/proyecto asignado cuando aplica, y la contraseña por defecto— para poder empezar a probar la aplicación sin tener que leer el código de las migraciones o los scripts de seed.

**Why this priority**: Hoy el archivo de credenciales (`docs/credenciales_dev.txt`) está desactualizado y mezcla usuarios reales del seed con un correo (`contacto.demo@clienteexterno.com`) que en realidad es solo un fixture de pruebas automatizadas y nunca se crea al levantar un ambiente real — lo que genera confusión sobre qué credenciales realmente funcionan.

**Independent Test**: Abrir el documento de credenciales y, para cada fila listada, verificar contra un ambiente recién sembrado que el usuario existe con ese rol, ese cliente/proyecto (si aplica) y que la contraseña documentada funciona; y verificar que ningún usuario real del seed queda fuera del documento.

**Acceptance Scenarios**:

1. **Given** el proceso de datos semilla ya ejecutado en un ambiente, **When** se consulta el documento de credenciales, **Then** aparece una fila por cada usuario creado por los seeders (los 4 roles internos ampliados, los Resolutores con skills, y los usuarios "Usuario/cliente" de Aris y Vaxthera) con nombre, correo, rol, cliente/proyecto (si aplica) y contraseña.
2. **Given** el documento de credenciales, **When** se revisa su contenido, **Then** no incluye usuarios que solo existen como fixtures de pruebas automatizadas (por ejemplo, datos usados únicamente por la suite de tests) y que nunca se crean al ejecutar los seeders contra una base de datos real.
3. **Given** que se agregan nuevos usuarios semilla en una ejecución futura de esta funcionalidad, **When** se actualiza el documento, **Then** el documento resultante refleja el estado final completo (no un parche incremental que dependa de versiones anteriores del archivo).

---

### User Story 4 - Verificación del calendario/zona horaria de Aris y Vaxthera (Priority: P3)

Como QA que valida el motor de SLA calendario-consciente (spec 028), necesito confirmar que los clientes semilla Aris y Vaxthera mantienen siempre su zona horaria correcta (`America/Bogota` y `America/Guayaquil` respectivamente), para que las pruebas de SLA y calendario que dependen de esos clientes den resultados correctos y no se degraden silenciosamente si alguien cambia el seed en el futuro.

**Why this priority**: Es una verificación de una funcionalidad ya sembrada (spec 026) en lugar de una funcionalidad nueva; su prioridad es menor porque el resultado esperado ya debería cumplirse hoy, pero conviene dejarlo comprobado y auto-corregible dentro de este mismo proceso de datos semilla.

**Independent Test**: Tras correr el seed, consultar los clientes Aris y Vaxthera y confirmar que su zona horaria es `America/Bogota` y `America/Guayaquil` respectivamente.

**Acceptance Scenarios**:

1. **Given** que los clientes Aris y Vaxthera ya existen (sembrados por la funcionalidad 026), **When** se ejecuta el proceso de datos semilla de esta funcionalidad, **Then** se confirma (o se corrige si estuviera desalineado) que Aris tiene zona horaria `America/Bogota` y Vaxthera `America/Guayaquil`.
2. **Given** un usuario Resolutor de los sembrados en la Historia 2, **When** se le asigna una zona horaria/país de calendario, **Then** ese valor es un país/zona horaria válido del catálogo ya soportado por el sistema (no bloquea al motor de SLA por un valor inexistente).

---

### Edge Cases

- Si el proceso de datos semilla se ejecuta varias veces seguidas (re-instalación, redeploy), no debe duplicar usuarios, Recursos, asignaciones de skill ni filas del documento de credenciales; debe converger al mismo estado final (mismo patrón que el seed existente de Aris/Vaxthera).
- Si un correo que el seed intenta crear ya existe en la base de datos con un rol distinto (por ejemplo, reutilizado manualmente por alguien), el proceso debe actualizar ese usuario al rol esperado en lugar de fallar o crear un duplicado.
- Si el catálogo de skills existente tiene menos de 3 skills activas disponibles (no debería ocurrir hoy, hay 8), el proceso debe fallar de forma explícita en vez de asignar skills repetidas o inexistentes.
- El documento de credenciales nunca debe incluir información de usuarios que solo existen en fixtures de pruebas automatizadas (tests), aunque su correo se parezca a uno real.
- Ningún usuario, contraseña o dato sembrado por esta funcionalidad debe usarse tal cual en la Producción real de cara al cliente final (ver advertencia de rotación de contraseña ya existente en `docs/credenciales_dev.txt` y en la migración 009).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El proceso de datos semilla MUST crear, para cada uno de los 4 roles internos existentes hoy (Admin, Coordinador, QM, Resolutor), al menos 2 usuarios adicionales a los ya sembrados por la migración base, cada uno con email y username propios y distintos entre sí.
- **FR-002**: El proceso de datos semilla MUST garantizar un mínimo de 4 usuarios totales con rol Resolutor (el ya existente más los que sean necesarios para llegar a 4), incluso si eso implica sembrar más de 2 usuarios adicionales para ese rol específico.
- **FR-003**: Cada uno de los usuarios con rol Resolutor que resulten del mínimo de 4 (los ya existentes antes de esta funcionalidad más los que ella agregue) MUST tener un perfil de Recurso creado y vinculado a su usuario (mismo `user_id`); si alguno ya existía sin Recurso, el proceso se lo crea en vez de dejarlo incompleto.
- **FR-004**: Cada Recurso de Resolutor cubierto por FR-003 MUST tener exactamente 3 skills asignadas, seleccionadas del catálogo de skills ya existente en el sistema; si un Recurso ya tenía skills asignadas, el proceso las completa hasta 3 en vez de dejarlo con menos.
- **FR-005**: Todos los usuarios creados por esta funcionalidad MUST compartir la misma contraseña por defecto usada hoy por el seed base (`SyWork_Dev2026!`), sin introducir una segunda contraseña estándar distinta.
- **FR-006**: El proceso de datos semilla MUST ser re-ejecutable sin duplicar usuarios, Recursos, asignaciones de skill ni filas de documentación: si un usuario/Recurso/asignación ya existe según lo sembrado, el proceso lo deja igual o lo actualiza para converger, pero nunca lo duplica.
- **FR-007**: El documento de credenciales de desarrollo (`docs/credenciales_dev.txt`) MUST listar, para cada usuario creado por cualquiera de los scripts/migraciones de datos semilla del proyecto (incluyendo los nuevos de esta funcionalidad y los ya existentes de Aris/Vaxthera), su nombre o username, correo, rol, cliente/proyecto asignado cuando aplique, y la contraseña por defecto.
- **FR-008**: El documento de credenciales MUST excluir cualquier usuario que exista únicamente como fixture de pruebas automatizadas y que no sea creado al ejecutar los scripts/migraciones de datos semilla contra una base de datos real.
- **FR-009**: El proceso de datos semilla MUST verificar que el cliente Aris tiene zona horaria `America/Bogota` y el cliente Vaxthera `America/Guayaquil`, corrigiendo el valor si estuviera desalineado, siguiendo el mismo criterio de convergencia que ya usa el seed de Aris/Vaxthera (spec 026).
- **FR-010**: El proceso de datos semilla MUST fallar de forma explícita (sin crear datos parciales) si el catálogo de skills disponible tiene menos de 3 skills activas al momento de asignarlas a un Resolutor.

### Key Entities *(include if feature involves data)*

- **Usuario (User)**: cuenta de acceso con email, username, rol y contraseña; esta funcionalidad amplía cuántos existen por rol interno, sin cambiar su estructura.
- **Recurso (Resource)**: perfil de un Resolutor vinculado a su Usuario (`user_id`), con nombre completo, email y su lista de skills asignadas.
- **Skill**: capacidad del catálogo ya existente (8 skills activas hoy) que se asigna a un Recurso; esta funcionalidad no crea skills nuevas, solo las asigna.
- **Cliente (Client)**: entidad ya sembrada (Aris, Vaxthera) con país y zona horaria; esta funcionalidad solo verifica/corrige su zona horaria, no crea clientes nuevos.
- **Documento de credenciales**: archivo de documentación (`docs/credenciales_dev.txt`) que lista de forma legible todos los usuarios sembrados con su rol, contraseña y cliente/proyecto asociado si aplica.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al levantar cualquier ambiente desde cero y correr el proceso de datos semilla, existen al menos 3 usuarios activos por cada uno de los roles Admin, Coordinador y QM, y al menos 4 usuarios activos con rol Resolutor — verificable en menos de 1 minuto por consulta directa.
- **SC-002**: El 100% de los usuarios sembrados (por esta funcionalidad y por los seeders ya existentes) inician sesión exitosamente con la contraseña documentada en `docs/credenciales_dev.txt`.
- **SC-003**: El 100% de los Recursos de Resolutor sembrados por esta funcionalidad tienen exactamente 3 skills asignadas, ninguna repetida y todas provenientes del catálogo existente.
- **SC-004**: Ejecutar el proceso de datos semilla dos veces seguidas sobre el mismo ambiente produce el mismo número final de usuarios, Recursos y asignaciones de skill que ejecutarlo una sola vez (cero duplicados).
- **SC-005**: El 100% de las filas del documento de credenciales corresponden a usuarios verificables en un ambiente recién sembrado (ningún usuario fantasma o solo-de-tests documentado).
- **SC-006**: Los clientes Aris y Vaxthera muestran, tras correr el proceso de datos semilla, la zona horaria `America/Bogota` y `America/Guayaquil` respectivamente, el 100% de las veces.

## Assumptions

- "Cada rol existente" se interpreta como los 4 roles internos de trabajo (Admin, Coordinador, QM, Resolutor). El rol "Usuario/cliente" queda fuera del incremento genérico de "+2 usuarios por rol", porque conceptualmente representa contactos de un cliente real y ya tiene su propio mecanismo de siembra (spec 026, Aris/Vaxthera); no se crean usuarios "Usuario/cliente" adicionales sin cliente asociado como parte de esta funcionalidad.
- La contraseña unificada a reutilizar es la ya definida como estándar del proyecto para datos semilla (`SyWork_Dev2026!`, constante `SEED_PASSWORD_DEV` de la migración 009), no una nueva contraseña.
- Las 3 skills por Resolutor se seleccionan del catálogo de 8 skills ya sembradas (JDE_GL, JDE_AP, JDE_AR, ORACLE_FUSION, ORACLE_CRM, API_REST, SQL_ORACLE, ORCHESTRATOR); pueden repartirse de forma variada entre los 4 Resolutores (no idénticas todas) para que las pruebas de asignación por skill tengan variedad, ya que el requerimiento no especifica skills concretas por persona.
- "Actualizar automáticamente" el documento de credenciales significa que, como parte de la entrega de esta funcionalidad, el documento queda actualizado y es consistente con el estado real de los seeders (no que la aplicación deba regenerar ese archivo en cada arranque); el mecanismo concreto de actualización es una decisión de implementación fuera del alcance de esta especificación.
- El correo `contacto.demo@clienteexterno.com` que hoy aparece en `docs/credenciales_dev.txt` es únicamente un fixture usado por la suite de pruebas automatizadas (`backend/tests/conftest.py`) y no lo crea ningún seeder ejecutado contra una base de datos real; por lo tanto se excluye del documento de credenciales bajo FR-008.
- Esta funcionalidad no crea, modifica ni elimina roles, permisos ni la arquitectura de autenticación existente; solo agrega datos (usuarios, Recursos, asignaciones de skill) y documentación.
- El entorno objetivo es Dev/Test/validación local, igual que el resto de datos semilla del proyecto; ninguna contraseña sembrada por esta funcionalidad se considera apta para Producción real con datos de clientes reales sin la rotación manual ya documentada.
