# Feature Specification: Ampliación de Accesos y Conexiones del Cliente (catálogo, credenciales múltiples, puerto y adjunto por acceso)

**Feature Branch**: `031-cliente-accesos-ampliado`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Cerrar OBS-0041 (Backlog UAT ITER-006, propuesta de Camilo Reyes, Gerente de Desarrollo): ampliar el modelo de \"Accesos y conexiones\" del Cliente (spec 018-cliente-accesos-conexiones) con 4 piezas que comparten una sola migración de base de datos: (1) catálogo administrable `catalog_access_types` que reemplaza el enum fijo de código; (2) credenciales múltiples por acceso (`client_access_credentials`); (3) campo `port` propio y `environment` aplicable a cualquier tipo; (4) adjunto anclado a un acceso puntual. Fuente de verdad: `UAT/01_Iterations/ITER-006/ITER-006.md` y el adjunto `OBS-0041-propuesta-accesos-conexiones.html`. Debe validarse contra `specs/018-cliente-accesos-conexiones/`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catálogo administrable de tipos de acceso (Priority: P1)

Quien administra los Catálogos de la aplicación necesita poder agregar nuevos tipos de acceso técnico (ej. "APEX", "NetSuite") a medida que aparecen en la operación real, sin depender de un despliegue de código. Hoy el tipo de acceso es un enum fijo de tres valores (VPN, URL de sistema, Escritorio remoto) que no alcanza para representar accesos a bases de datos, servidores/instancias, ni integraciones futuras.

**Why this priority**: Es la pieza que desbloquea a todas las demás — sin un catálogo abierto, cualquier tipo de acceso nuevo (base de datos, servidor) seguiría forzándose dentro de un tipo que no le corresponde, como ya documentó el reporte de origen.

**Independent Test**: Puede probarse agregando un tipo nuevo (ej. "APEX") desde el módulo Catálogos y verificando que aparece disponible de inmediato al crear un acceso de cliente, con un color propio que no coincide con los demás tipos.

**Acceptance Scenarios**:

1. **Given** el módulo Catálogos, **When** un usuario administrador agrega un tipo de acceso nuevo con un nombre no usado antes, **Then** el tipo queda disponible de inmediato en el selector de "tipo de acceso" al crear/editar un acceso de cliente.
2. **Given** un tipo de acceso recién creado, **When** se visualiza en cualquier listado, **Then** muestra un color distintivo asignado automáticamente por el sistema, sin que el usuario lo haya elegido.
3. **Given** dos tipos de acceso creados en momentos distintos, **When** se agrega un tercero, **Then** los colores de los dos primeros no cambian.
4. **Given** los tres tipos de acceso que ya existían antes de este cambio (VPN, URL de sistema, Escritorio remoto), **When** se despliega este cambio, **Then** los accesos ya cargados conservan su tipo correspondiente sin intervención manual (VPN→VPN, URL de sistema→Sistema/Integración, Escritorio remoto→Escritorio remoto).

---

### User Story 2 - Credenciales múltiples por acceso (Priority: P1)

Quien administra los accesos de un cliente necesita registrar que un mismo acceso (ej. una URL de ERP o de integración) es compartido por varias personas, cada una con su propio usuario y contraseña — sin tener que duplicar el host/URL una vez por cada persona, como exige el modelo actual (1 acceso = 1 credencial).

**Why this priority**: Es el corazón funcional de la observación — el caso real reportado (ERP/OIC compartido por un equipo completo) no se puede representar hoy sin duplicar información y generar inconsistencias si cambia la URL.

**Independent Test**: Puede probarse creando un acceso (ej. tipo "Sistema/Integración") y agregándole tres credenciales distintas (usuario/contraseña/etiqueta cada una), verificando que las tres persisten de forma independiente bajo el mismo acceso y que editar o eliminar una no afecta a las demás.

**Acceptance Scenarios**:

1. **Given** un acceso de cliente ya creado, **When** el usuario agrega una credencial con etiqueta, usuario y contraseña, **Then** la credencial queda asociada a ese acceso y visible al reabrir el cliente.
2. **Given** un acceso con una credencial ya cargada, **When** el usuario agrega una segunda credencial, **Then** ambas coexisten bajo el mismo acceso sin que una sobrescriba a la otra ni se duplique el host/URL.
3. **Given** una credencial existente de un acceso, **When** el usuario la edita o la elimina, **Then** el cambio afecta únicamente a esa credencial; las demás credenciales del mismo acceso y los demás accesos del cliente permanecen intactos.
4. **Given** un acceso de cliente que ya tenía usuario/contraseña cargados antes de este cambio, **When** se despliega este cambio, **Then** esos valores aparecen migrados como la primera credencial de ese acceso, sin pérdida de la información ya capturada.
5. **Given** una credencial con contraseña cargada, **When** el usuario abre el formulario del acceso, **Then** la contraseña se muestra enmascarada por defecto con un control explícito de revelado, igual que ya ocurre en el modelo actual de accesos (mismo permiso ya vigente para datos sensibles del cliente).

---

### User Story 3 - Puerto propio y ambiente aplicable a cualquier tipo de acceso (Priority: P2)

Quien registra un acceso necesita indicar el puerto de conexión como un dato propio (hoy se escribe a mano dentro del host) y poder indicar el ambiente (Producción/Pruebas/etc.) sin importar el tipo de acceso — hoy esa opción solo aparece para "URL de sistema", pero en la práctica también aplica a accesos VPN, de base de datos o de servidor.

**Why this priority**: Corrige dos limitaciones puntuales de datos que generan pérdida de precisión, pero no bloquean el uso básico de accesos y credenciales (US1/US2) mientras tanto.

**Independent Test**: Puede probarse creando un acceso de tipo "VPN" o "Base de datos", indicando un ambiente y un puerto numérico separado del host, y verificando que ambos se guardan y se muestran como campos independientes.

**Acceptance Scenarios**:

1. **Given** un acceso nuevo de cualquier tipo, **When** el usuario indica un ambiente (Producción/Pruebas/etc.), **Then** el ambiente se guarda y se muestra sin importar el tipo de acceso elegido.
2. **Given** un acceso nuevo, **When** el usuario indica un puerto, **Then** el puerto se guarda como dato separado del host y se muestra como tal en los listados.
3. **Given** un acceso ya existente antes de este cambio (sin puerto propio), **When** se despliega este cambio, **Then** el acceso sigue funcionando con el puerto vacío, sin obligar a completarlo retroactivamente.

---

### User Story 4 - Adjunto de manual anclado a un acceso puntual (Priority: P2)

Quien administra un cliente con varios accesos necesita poder asociar el manual/instructivo de conexión a UN acceso específico (ej. el manual de la VPN de Producción, distinto del manual del servidor de Staging), en vez de que todos los adjuntos queden mezclados a nivel general del cliente sin poder distinguir a cuál acceso corresponde cada uno.

**Why this priority**: Es una mejora de organización de información ya existente (los adjuntos generales de cliente ya existen desde el spec base) — de menor urgencia que poder registrar los accesos y credenciales en sí (US1/US2).

**Independent Test**: Puede probarse subiendo un archivo y asociándolo a un acceso puntual del cliente, verificando que aparece listado junto a ese acceso y no junto a los demás accesos ni como adjunto general.

**Acceptance Scenarios**:

1. **Given** un cliente con dos o más accesos registrados, **When** el usuario sube un archivo y lo asocia a uno de ellos, **Then** el archivo aparece listado junto a ese acceso específico.
2. **Given** un archivo asociado a un acceso puntual, **When** el usuario visualiza otro acceso del mismo cliente, **Then** ese archivo no aparece listado ahí.
3. **Given** el comportamiento ya existente de adjuntos generales del cliente (sin asociar a ningún acceso), **When** se despliega este cambio, **Then** esos adjuntos generales siguen existiendo y visibles exactamente como antes.

---

### Edge Cases

- ¿Qué pasa si se intenta crear un tipo de acceso con un nombre ya usado (activo o inactivo)? Debe rechazarse, igual que ya ocurre con los demás catálogos administrables de la aplicación.
- ¿Qué pasa si un acceso se queda sin ninguna credencial (todas eliminadas)? Debe ser un estado válido — el acceso sigue existiendo con sus datos propios (tipo, host, puerto, ambiente, notas), solo sin credenciales cargadas.
- ¿Qué pasa si un acceso existente antes del cambio no tenía usuario ni contraseña cargados? No debe crearse una credencial vacía al migrar.
- ¿Qué pasa si se elimina un acceso que tiene credenciales y/o un adjunto anclado? Las credenciales del acceso se eliminan junto con él; el adjunto anclado deja de estar asociado a un acceso (mismo criterio ya vigente para adjuntos generales al eliminar el cliente).
- ¿Qué pasa si un usuario sin permiso de datos sensibles visualiza un acceso con varias credenciales? Debe poder ver que existen y cuántas, sin poder revelar usuario/contraseña de ninguna — mismo criterio ya vigente en el modelo actual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir administrar los tipos de acceso (VPN, Base de datos, Servidor/instancia, Escritorio remoto, Sistema/Integración, y los que se agreguen después) desde un catálogo, no desde una lista fija de código.
- **FR-002**: El sistema MUST asignar automáticamente un color distintivo a cada tipo de acceso nuevo, sin que el usuario lo elija manualmente, y ese color MUST permanecer estable una vez asignado aunque se agreguen tipos nuevos después.
- **FR-003**: El sistema MUST rechazar la creación de un tipo de acceso con un nombre ya usado por otro tipo existente (activo o inactivo).
- **FR-004**: El sistema MUST migrar automáticamente, sin intervención manual, los tres tipos de acceso ya existentes (VPN, URL de sistema, Escritorio remoto) a entradas equivalentes del nuevo catálogo, preservando el tipo de cada acceso ya cargado.
- **FR-005**: El sistema MUST permitir registrar cero o más credenciales (etiqueta, usuario, contraseña) para cada acceso de cliente, sin necesidad de repetir el host/URL del acceso por cada credencial.
- **FR-006**: El sistema MUST permitir crear, editar y eliminar cada credencial de un acceso de forma independiente, sin afectar a las demás credenciales del mismo acceso ni a otros accesos del cliente.
- **FR-007**: El sistema MUST migrar automáticamente, sin intervención manual, el usuario y contraseña ya cargados en cada acceso existente como su primera credencial, sin pérdida de la información previamente capturada.
- **FR-008**: El sistema MUST enmascarar por defecto el valor de "contraseña" de cada credencial, con el mismo control de revelado y el mismo permiso que ya rige los datos sensibles de accesos del cliente.
- **FR-009**: El sistema MUST permitir indicar un ambiente (Producción/Pruebas/etc.) en un acceso de cualquier tipo, no solo en el que antes era "URL de sistema".
- **FR-010**: El sistema MUST permitir registrar un puerto como dato propio del acceso, separado del host.
- **FR-011**: El sistema MUST permitir asociar un archivo adjunto a un acceso puntual del cliente, además de seguir permitiendo adjuntos generales no asociados a ningún acceso en particular.
- **FR-012**: El sistema MUST mostrar, junto a cada acceso, únicamente los adjuntos asociados a ese acceso puntual (y, por separado, los adjuntos generales del cliente que no están asociados a ningún acceso).
- **FR-013**: El sistema MUST tratar "acceso sin ninguna credencial registrada" como un estado válido, no como un error.

### Key Entities

- **Tipo de acceso (catálogo)**: valor administrable que clasifica un acceso de cliente (ej. VPN, Base de datos, Servidor/instancia). Tiene nombre, estado activo/inactivo y un color asignado automáticamente y estable en el tiempo.
- **Acceso y conexión (de Cliente)**: ya existente (spec 018); gana un tipo tomado del catálogo administrable (en vez de un valor fijo), un puerto propio, y un ambiente aplicable sin importar el tipo. Pertenece a exactamente un cliente y puede tener cero o más credenciales.
- **Credencial (de un Acceso)**: nueva entidad; representa un usuario/contraseña propio dentro de un acceso, con una etiqueta descriptiva y notas opcionales. Un acceso puede tener cero o más credenciales.
- **Adjunto de accesos**: ya existente (spec 018); gana la posibilidad de asociarse opcionalmente a un acceso puntual, en vez de quedar siempre a nivel general del cliente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede agregar un tipo de acceso nuevo desde Catálogos y usarlo para clasificar un acceso de cliente en la misma sesión de trabajo, sin ninguna intervención técnica adicional.
- **SC-002**: Un usuario puede registrar 3 o más credenciales distintas bajo un mismo acceso sin repetir el host/URL, y cada una se edita/elimina de forma independiente sin afectar a las demás.
- **SC-003**: El 100% de los accesos de cliente que tenían usuario/contraseña cargados antes del cambio conservan esa información accesible como su primera credencial después de la migración.
- **SC-004**: El 100% de los accesos de cliente que tenían un tipo asignado antes del cambio (VPN, URL de sistema, Escritorio remoto) conservan un tipo equivalente y reconocible después de la migración.
- **SC-005**: Un usuario puede asociar un adjunto a un acceso puntual y confirmar que solo aparece listado junto a ese acceso, no junto a los demás ni mezclado con los adjuntos generales del cliente.

## Assumptions

- El permiso que ya rige la visibilidad de datos sensibles de accesos del cliente (spec 018) es el que también gobierna el revelado de las credenciales múltiples; no se crea un permiso nuevo.
- El mecanismo de cifrado de contraseñas ya vigente para accesos de cliente se reutiliza tal cual para las credenciales; no se introduce ni modifica infraestructura de cifrado.
- Los adjuntos de accesos ya asociados de forma general al cliente (antes de este cambio) permanecen sin asociar a ningún acceso puntual; no se migran retroactivamente a un acceso específico porque no hay forma confiable de inferir a cuál correspondían.
- La paleta de colores para tipos de acceso es fija (mismo número de opciones que tipos de acceso semilla más margen para crecer); si se agotan los colores disponibles, el sistema reutiliza colores desde el principio de la paleta en vez de bloquear la creación de tipos nuevos.
- Este cambio no introduce roles ni permisos nuevos: reutiliza el control de acceso por módulo "Clientes" ya existente.
- No se elimina ninguna columna o campo legacy de la implementación anterior (spec 018): los valores previos de tipo de acceso, usuario y contraseña embebidos en el acceso quedan como datos históricos no expuestos en la UI nueva, igual que ya ocurrió con `vpn_ips`/`vpn_credentials` al implementar el spec 018.
