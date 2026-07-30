# Feature Specification: Selección en Cascada, Hipervínculos de Navegación, Layout de Cliente y Edición de Catálogos

**Feature Branch**: `035-cascada-links-catalogos-cliente`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "Ajustes en Selección de Tickets en Cascada, Hipervínculos, Edición de Catálogos y Layout de Cliente"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Selección en cascada Cliente → Proyecto → Encargado en Ticket (Priority: P1)

Un Coordinador o Resolutor crea o edita un Ticket. Al elegir el Cliente, el selector de Proyecto se limita automáticamente a los proyectos de ese cliente; al elegir el Proyecto, el selector de Encargado/Usuario-cliente se limita a los encargados asociados a ese proyecto. El campo de Skills requeridas, disponible previamente y actualmente ausente del formulario, vuelve a estar visible y editable tanto en el Ticket como en cada Tarea.

**Why this priority**: Es el flujo más usado (creación diaria de tickets) y el que genera más errores de captura (Proyecto/Encargado equivocado) sin la cascada; además restaura una capacidad ya validada que se perdió.

**Independent Test**: Abrir "Nuevo Ticket", elegir un Cliente con al menos 2 proyectos y verificar que Proyecto solo lista los suyos; elegir un Proyecto y verificar que Encargado solo lista los suyos; verificar que el campo Skills aparece y permite seleccionar/deseleccionar valores del catálogo existente. Repetir el mismo flujo en el formulario de Tarea.

**Acceptance Scenarios**:

1. **Given** el formulario de creación de Ticket vacío, **When** el usuario selecciona un Cliente, **Then** el selector de Proyecto se habilita y solo muestra proyectos de ese Cliente (los de otros clientes no aparecen).
2. **Given** un Cliente ya seleccionado, **When** el usuario selecciona un Proyecto de ese cliente, **Then** el selector de Encargado/Usuario-cliente solo muestra los encargados asociados a ese Proyecto.
3. **Given** un Cliente/Proyecto/Encargado ya seleccionados, **When** el usuario cambia el Cliente por otro, **Then** los valores de Proyecto y Encargado previamente elegidos se limpian (ya no son válidos para el nuevo cliente) y el usuario debe volver a elegirlos.
4. **Given** el formulario de creación de Ticket o de Tarea, **When** el usuario abre el selector de Skills, **Then** puede elegir una o más skills del catálogo existente y verlas reflejadas al guardar.
5. **Given** un Ticket existente con Cliente/Proyecto/Encargado/Skills ya asignados, **When** el usuario abre el formulario de edición, **Then** los cuatro campos muestran los valores actuales y los selectores dependientes ya están filtrados correctamente (no requiere reseleccionar desde cero para ver el valor vigente).

---

### User Story 2 - Hipervínculos a Ticket/Tarea desde cualquier listado (Priority: P1)

Cualquier usuario que vea un código de ticket/tarea (`#TK-001`) en una tabla, lista o tablero Kanban puede hacer clic sobre él para ir directamente al detalle de ese ticket/tarea, sin pasos intermedios de búsqueda o filtrado manual.

**Why this priority**: Afecta la navegación diaria de todos los roles y es una expectativa básica de usabilidad; su ausencia genera fricción constante ya reportada por usuarios.

**Independent Test**: Desde la lista de Tickets, el tablero Kanban, "Mis Tareas" y el Panel de Asignación, hacer clic sobre un código de ticket/tarea y verificar que se navega al detalle correspondiente sin recargar toda la lista ni perder el estado de filtros previamente aplicados en esa pantalla.

**Acceptance Scenarios**:

1. **Given** la lista de Tickets con resultados, **When** el usuario hace clic en el código de un ticket, **Then** navega a la pantalla de detalle de ese ticket.
2. **Given** el tablero Kanban, **When** el usuario hace clic en el código dentro de una tarjeta, **Then** navega al detalle sin iniciar un drag-and-drop.
3. **Given** "Mis Tareas" o el Panel de Asignación, **When** el usuario hace clic en el código de una tarea/ticket, **Then** navega a su detalle.
4. **Given** el usuario navegó al detalle desde una lista filtrada, **When** vuelve atrás con el botón "volver" del navegador, **Then** la lista conserva los filtros y el desplazamiento previos.

---

### User Story 3 - Ordenamiento explícito en tablas y listas de tickets/tareas (Priority: P2)

Un usuario que consulta una tabla o lista de tickets/tareas puede ordenar los resultados de forma explícita por fecha, prioridad, código o estado, además de poder seguir filtrando como hasta ahora.

**Why this priority**: Complementa el hallazgo de un ticket puntual (US2) con la capacidad de priorizar visualmente el trabajo pendiente; es de menor frecuencia de uso que abrir un ticket puntual.

**Independent Test**: En la lista de Tickets, aplicar ordenamiento por cada uno de los 4 criterios (fecha, prioridad, código, estado) en ambos sentidos (ascendente/descendente) y verificar que el orden de las filas cambia de forma consistente con el criterio elegido, sin alterar los filtros activos.

**Acceptance Scenarios**:

1. **Given** una tabla de tickets con filtros aplicados, **When** el usuario ordena por "Prioridad" descendente, **Then** las filas se reordenan de mayor a menor prioridad sin quitar los filtros activos.
2. **Given** una tabla ya ordenada por un criterio, **When** el usuario cambia a otro criterio de ordenamiento, **Then** el orden anterior se reemplaza por el nuevo.
3. **Given** una tabla ordenada por "Código", **When** el usuario invierte el sentido del ordenamiento, **Then** el orden se invierte (ascendente ↔ descendente).

---

### User Story 4 - Layout horizontal ampliado en Detalle del Cliente (Priority: P3)

Un usuario que abre el detalle de un Cliente ve su información general, proyectos asociados y métricas distribuidos en un layout más ancho (columnas lado a lado) en vez de un apilado vertical largo, reduciendo el scroll necesario para tener una visión completa del cliente.

**Why this priority**: Mejora de usabilidad de una pantalla de consulta frecuente pero no bloqueante para la operación diaria; no introduce datos ni acciones nuevas.

**Independent Test**: Abrir el detalle de un Cliente con varios proyectos asociados en una pantalla de ancho estándar de escritorio y verificar que la información general, la lista de proyectos y las métricas se distribuyen en columnas visibles sin necesidad de scroll vertical excesivo, y que la misma pantalla sigue siendo utilizable en una ventana más angosta (los bloques se apilan de forma legible).

**Acceptance Scenarios**:

1. **Given** el detalle de un Cliente con proyectos y métricas, **When** se visualiza en una pantalla de escritorio estándar, **Then** la información general, los proyectos asociados y las métricas se muestran distribuidos horizontalmente (no todo en una sola columna larga).
2. **Given** el detalle de un Cliente en una ventana angosta, **When** el ancho disponible no alcanza para columnas lado a lado, **Then** los bloques se apilan de forma legible sin recortar contenido.

---

### User Story 5 - Editar nombre en pantallas de Catálogos (Priority: P2)

Un Coordinador o Admin que gestiona un catálogo maestro (por ejemplo Herramientas, Procesos, Skills, Equipos) puede corregir el nombre de un registro existente sin tener que anularlo y crear uno nuevo, preservando las referencias que ya tiene ese registro en otros datos (tickets, skills, etc.).

**Why this priority**: Corrige errores de tipeo o nomenclatura en catálogos ya usados en producción; es una mejora operativa puntual, no bloqueante.

**Independent Test**: En una pantalla de Catálogo (ej. Herramientas), editar el nombre de un registro existente y verificar que el cambio se refleja de inmediato en la tabla y en cualquier lugar donde ese registro se muestre por nombre (ej. el selector de Herramienta en un Ticket ya creado que lo referencia).

**Acceptance Scenarios**:

1. **Given** la tabla de un Catálogo con registros existentes, **When** el usuario usa la acción "Editar" sobre un registro, **Then** puede modificar su nombre y guardar el cambio.
2. **Given** un registro de catálogo cuyo nombre fue editado, **When** el usuario recarga la pantalla, **Then** el nuevo nombre persiste y se muestra correctamente.
3. **Given** un registro de catálogo referenciado por tickets u otros catálogos existentes, **When** se edita su nombre, **Then** esas referencias siguen apuntando al mismo registro y muestran el nombre actualizado (no se duplica el registro ni se rompe la referencia).
4. **Given** un intento de guardar un nombre vacío o duplicado dentro del mismo catálogo, **When** el usuario confirma la edición, **Then** el sistema rechaza el cambio con un mensaje claro y conserva el nombre anterior.

### Edge Cases

- ¿Qué pasa si un Ticket ya existente tiene un Encargado cuyo Proyecto fue reasignado a otro Cliente después de la creación del ticket? El histórico del ticket no debe alterarse; el formulario de edición debe permitir revisar/corregir la cadena Cliente→Proyecto→Encargado si ya no es consistente.
- ¿Qué pasa si un Cliente no tiene Proyectos, o un Proyecto no tiene Encargados asociados? Los selectores dependientes deben mostrarse vacíos con un mensaje claro, sin bloquear el resto del formulario (autoservicio / tickets sin encargado explícito siguen su comportamiento actual).
- ¿Qué pasa si el usuario hace clic en el código de ticket dentro de una fila que también tiene otras acciones (drag handle del Kanban, checkbox de selección)? El clic sobre el código específicamente debe navegar; los demás controles de la fila conservan su comportamiento actual.
- ¿Qué pasa si se ordena una tabla vacía o con un solo resultado? El control de ordenamiento se muestra pero no tiene efecto visible.
- ¿Qué pasa si dos registros de catálogo terminan con el mismo nombre tras una edición? Se rechaza como duplicado (ver Acceptance Scenario 4 de US5).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El formulario de creación/edición de Ticket y de Tarea MUST filtrar el selector de Proyecto para mostrar únicamente los proyectos del Cliente seleccionado.
- **FR-002**: El formulario de creación/edición de Ticket y de Tarea MUST filtrar el selector de Encargado/Usuario-cliente para mostrar únicamente los encargados asociados al Proyecto seleccionado.
- **FR-003**: Al cambiar la selección de Cliente, el sistema MUST limpiar cualquier selección de Proyecto y Encargado que ya no sea válida para el nuevo Cliente.
- **FR-004**: Al cambiar la selección de Proyecto, el sistema MUST limpiar cualquier selección de Encargado que ya no sea válida para el nuevo Proyecto.
- **FR-005**: El formulario de Ticket y el formulario de Tarea MUST incluir un campo de selección de Skills requeridas sobre el catálogo de skills existente, respetando el permiso `tickets:manage_skills` para determinar si el campo es editable o de solo lectura. El permiso `tickets:manage_skills` MUST alcanzar a todo rol interno (Admin, Coordinador, QM, Resolutor) — antes restringido solo a Coordinador (OBS-0047/0048, spec 033) — dejando fuera únicamente a Usuario/cliente (rol externo). Corrección post-implementación (feedback UAT 2026-07-30): el alcance original de esta feature asumía que "restaurar" el campo significaba solo volverlo visible/deshabilitado para no-Coordinador; el feedback aclaró que el permiso en sí debía ampliarse.
- **FR-006**: Todo código de ticket/tarea (`#TK-###` u equivalente) mostrado en tablas, listas y el tablero Kanban MUST ser un hipervínculo que navegue al detalle de ese ticket/tarea al hacer clic.
- **FR-007**: La navegación desde un código de ticket/tarea hacia el detalle MUST preservar los filtros, el ordenamiento y el desplazamiento previos de la lista de origen al regresar (navegación "atrás").
- **FR-008**: Las tablas y listas de tickets/tareas alcanzadas por esta funcionalidad MUST ofrecer ordenamiento explícito por fecha, prioridad, código y estado, en sentido ascendente y descendente, de forma combinable con los filtros existentes.
- **FR-009**: La vista de Detalle del Cliente MUST reorganizar la información general, los proyectos asociados y las métricas en un layout de columnas horizontales en pantallas de ancho estándar de escritorio, y MUST seguir siendo legible (apilado) en ventanas angostas.
- **FR-010**: Las pantallas de gestión de Catálogos existentes (Herramientas, Procesos, Skills, Equipos y demás maestros con el mismo patrón crear/anular) MUST ofrecer una acción "Editar" que permita modificar el nombre de un registro existente.
- **FR-011**: Al editar el nombre de un registro de catálogo, el sistema MUST validar que el nuevo nombre no esté vacío y no duplique el nombre de otro registro activo del mismo catálogo, rechazando el guardado con un mensaje claro en caso contrario.
- **FR-012**: Editar el nombre de un registro de catálogo MUST preservar su identificador y todas las referencias existentes desde otros datos (tickets, skills, reglas de SLA, etc.), reflejando el nuevo nombre donde ese registro se muestre.

### Key Entities

- **Ticket / Tarea**: ya existente; esta feature no agrega atributos nuevos, solo ajusta cómo se capturan Cliente/Proyecto/Encargado/Skills en su formulario y cómo se enlaza/ordena en listados.
- **Cliente / Proyecto / Encargado (Usuario-cliente)**: ya existentes; esta feature usa las relaciones ya modeladas (Proyecto pertenece a Cliente, Encargado asociado a Proyecto) para alimentar la cascada, sin cambiar el modelo de datos.
- **Registro de Catálogo** (Herramienta, Proceso, Skill, Equipo, etc.): ya existentes; esta feature agrega la capacidad de editar el atributo nombre de un registro, sin cambiar su identificador ni sus relaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al crear un Ticket, el tiempo promedio para completar correctamente Cliente/Proyecto/Encargado se reduce frente al flujo actual (menos correcciones por Proyecto/Encargado incorrecto), verificable porque el 100% de los tickets nuevos quedan con una cadena Cliente→Proyecto→Encargado consistente entre sí.
- **SC-002**: El 100% de los códigos de ticket/tarea visibles en listas, tableros y paneles permiten llegar al detalle correspondiente en un solo clic.
- **SC-003**: Los usuarios pueden ordenar cualquier tabla de tickets/tareas alcanzada por los 4 criteria (fecha, prioridad, código, estado) sin perder los filtros aplicados, en el 100% de los casos probados.
- **SC-004**: La pantalla de Detalle del Cliente presenta la información general, proyectos y métricas sin requerir más de un scroll de pantalla completo en una resolución de escritorio estándar (1366×768 o superior), para un cliente con hasta 10 proyectos asociados.
- **SC-005**: El 100% de las ediciones de nombre en catálogos se reflejan de inmediato en la tabla del catálogo y en cualquier referencia existente, sin generar registros duplicados ni romper vínculos existentes.

## Assumptions

- La relación Cliente→Proyecto→Encargado ya existe en el modelo de datos actual (Proyecto tiene `client_id`; Encargado/Usuario-cliente está asociado a uno o más Proyectos vía la funcionalidad ya implementada en `specs/015-encargado-multiples-proyectos`); esta feature solo ajusta el filtrado en el formulario, no el modelo.
- "Restaurar" el campo de Skills se refiere a devolver la funcionalidad de selección ya existente previamente (catálogo de Skills y permiso `tickets:manage_skills` de `specs/033-cierre-obs-0044-0059`), no a diseñar un mecanismo nuevo.
- Las tablas/listas alcanzadas por hipervínculos y ordenamiento son las pantallas ya existentes que muestran tickets/tareas: lista de Tickets, tablero Kanban, "Mis Tareas" y Panel de Asignación; no se crean pantallas nuevas.
- "Layout más horizontal" para el Detalle del Cliente es un reacomodo visual (grid/columnas) del mismo contenido ya mostrado hoy, sin agregar datos, métricas o acciones nuevas.
- Las pantallas de Catálogos alcanzadas por "Editar Nombre" son las que ya siguen el patrón crear/anular de un único campo `name` administrable (ej. Herramientas, Procesos, Skills, Equipos); catálogos con estructura distinta (por ejemplo, con múltiples campos editables ya existentes) están fuera de alcance salvo que ya expongan un nombre simple editable.
- Autoservicio (Usuario/cliente creando su propio ticket) conserva su comportamiento actual de auto-derivar Cliente/Encargado; la cascada aplica al flujo de creación desde perfil interno donde Cliente se elige manualmente.
