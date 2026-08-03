# Feature Specification: Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering en Scroll del Ticket

**Feature Branch**: `036-herencia-subtareas-scroll`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering en Scroll del Ticket — Quiero implementar la lógica de relaciones y herencia automática entre Tareas y Subtareas, además de corregir un error visual de renderizado (parpadeo) en la vista de detalle del Ticket."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Herencia automática al crear una Subtarea (Priority: P1)

Un usuario interno (Admin, Coordinador, QM o Resolutor) crea una Subtarea a partir de una Tarea padre ya existente. Sin que el usuario tenga que volver a capturar los datos, la Subtarea nace con el mismo Nivel de escalamiento, el mismo Usuario solicitante/cliente y las mismas Skills requeridas que tenía la Tarea padre en el momento de la creación.

**Why this priority**: Es el corazón de la funcionalidad solicitada — sin la herencia automática, el resto de la historia (vínculo bidireccional, hipervínculo) no tiene datos consistentes que mostrar. Reduce recaptura manual y evita inconsistencias entre Tarea y Subtarea.

**Independent Test**: Puede probarse de forma aislada creando una Tarea con un Nivel de escalamiento, un Usuario solicitante y Skills específicas, generando una Subtarea desde ella, y verificando que los tres campos llegan precargados con los mismos valores sin intervención del usuario.

**Acceptance Scenarios**:

1. **Given** una Tarea padre con Nivel de escalamiento "N2", Usuario solicitante "Pablo (Vaxthera)" y 2 Skills requeridas, **When** un usuario interno crea una Subtarea a partir de esa Tarea, **Then** la Subtarea se guarda con el mismo Nivel de escalamiento, el mismo Usuario solicitante y las mismas 2 Skills requeridas, sin que el usuario los haya vuelto a seleccionar.
2. **Given** una Subtarea ya creada por herencia, **When** el usuario interno con el permiso correspondiente modifica manualmente las Skills requeridas de la Subtarea después de creada, **Then** el cambio se guarda de forma independiente y no se propaga de vuelta a la Tarea padre ni se revierte automáticamente.
3. **Given** una Tarea padre sin Usuario solicitante asignado, **When** se crea una Subtarea a partir de ella, **Then** la Subtarea se crea sin Usuario solicitante (el campo hereda el valor vacío, no bloquea la creación).

---

### User Story 2 - Referencia bidireccional Tarea padre ↔ Subtareas (Priority: P1)

Un usuario que abre el detalle de una Tarea que tiene Subtareas asociadas puede ver de un vistazo cuántas Subtareas tiene y cuáles son, sin tener que buscarlas manualmente en el listado general.

**Why this priority**: Es el complemento indispensable de la herencia — de nada sirve heredar datos si la Tarea padre no expone la relación inversa. Igual de crítico que US1 porque ambos forman el mismo modelo de datos.

**Independent Test**: Puede probarse de forma aislada creando 2-3 Subtareas a partir de la misma Tarea padre y verificando que el detalle de la Tarea padre muestra el conteo y el listado de esas Subtareas, actualizado tras cada creación.

**Acceptance Scenarios**:

1. **Given** una Tarea padre sin Subtareas, **When** se crean 3 Subtareas a partir de ella, **Then** el detalle de la Tarea padre muestra un contador de "3 Subtareas" y la lista de sus códigos/nombres.
2. **Given** una Tarea padre con Subtareas ya listadas en su detalle, **When** el usuario hace clic en el código de una Subtarea desde esa lista, **Then** es redirigido al detalle de esa Subtarea.

---

### User Story 3 - Hipervínculo a la Tarea Padre desde la Subtarea (Priority: P2)

Un usuario que abre el detalle de una Subtarea ve, dentro de la sección "Clasificación", el campo "Tarea Padre" con el código/nombre de la Tarea de origen como un enlace clicable que lo lleva directamente al detalle de esa Tarea.

**Why this priority**: Depende de que exista la relación (US1/US2) para tener algo que enlazar; es la pieza de navegación que cierra el ciclo pero no bloquea el valor de negocio de la herencia en sí.

**Independent Test**: Puede probarse de forma aislada abriendo el detalle de una Subtarea existente y verificando que el campo "Tarea Padre" aparece en "Clasificación" como enlace, y que al hacer clic navega correctamente al detalle de la Tarea padre.

**Acceptance Scenarios**:

1. **Given** una Subtarea creada a partir de una Tarea padre, **When** el usuario abre el detalle de la Subtarea, **Then** la sección "Clasificación" muestra el campo "Tarea Padre" con el código/nombre de la Tarea de origen.
2. **Given** el campo "Tarea Padre" visible en el detalle de la Subtarea, **When** el usuario hace clic sobre él, **Then** el sistema navega al detalle de la Tarea padre correspondiente.
3. **Given** un Ticket o Tarea que NO es una Subtarea (no tiene Tarea padre), **When** el usuario abre su detalle, **Then** el campo "Tarea Padre" no se muestra.

---

### User Story 4 - Eliminar el parpadeo (flickering) en el detalle del Ticket (Priority: P1)

Un usuario que interactúa con el panel izquierdo (Clasificación e Historial) del detalle de un Ticket/Tarea — desplazándose (scroll) o interactuando con controles de esa columna — deja de ver el parpadeo/re-renderizado persistente que hoy interrumpe la lectura y da una sensación de interfaz rota.

**Why this priority**: Es un defecto visible en cada apertura del detalle de Ticket/Tarea (la pantalla más usada del sistema); afecta la percepción de calidad y la usabilidad diaria, independientemente de las historias de Subtareas.

**Independent Test**: Puede probarse de forma aislada abriendo el detalle de un Ticket/Tarea existente (con y sin Subtareas) y desplazándose repetidamente por el panel izquierdo durante al menos 30 segundos, confirmando ausencia de parpadeo visual.

**Acceptance Scenarios**:

1. **Given** el detalle de un Ticket/Tarea abierto, **When** el usuario hace scroll dentro del panel izquierdo (Clasificación + Historial), **Then** el contenido se desplaza de forma estable sin parpadeo ni saltos de re-renderizado.
2. **Given** el detalle de un Ticket/Tarea abierto con el cronómetro de tiempo activo (actualización periódica en pantalla), **When** el usuario permanece en la pantalla sin interactuar, **Then** el panel izquierdo no parpadea ni pierde la posición de scroll por las actualizaciones periódicas de otros paneles.
3. **Given** el detalle de una Subtarea (con el nuevo campo "Tarea Padre" visible), **When** el usuario hace scroll en el panel izquierdo, **Then** tampoco se observa parpadeo, confirmando que el nuevo campo no reintroduce el problema.

---

### Edge Cases

- ¿Qué sucede si se intenta crear una "Subtarea de una Subtarea" (anidamiento a más de un nivel)? El sistema mantiene el límite de un solo nivel ya vigente (una Subtarea no puede a su vez tener Subtareas propias ni convertirse en Tarea padre).
- ¿Qué ocurre si la Tarea padre cambia su Usuario solicitante/cliente o sus Skills requeridas *después* de que ya existan Subtareas? Las Subtareas ya creadas conservan los valores heredados al momento de su creación; no se re-sincronizan retroactivamente.
- ¿Qué pasa si la Tarea padre es eliminada o cancelada? Las Subtareas ya creadas conservan su referencia e hipervínculo a la Tarea padre (aunque esta esté cancelada); el hipervínculo sigue siendo navegable a su detalle.
- ¿Qué pasa si un usuario sin permiso para ver la Tarea padre (por ejemplo, un Usuario/cliente distinto) abre una Subtarea? El campo "Tarea Padre" se muestra igualmente si el usuario tiene acceso de lectura a la Subtarea; el clic respeta los mismos controles de permiso ya vigentes para abrir el detalle de un Ticket/Tarea.
- ¿Qué pasa con el conteo de Subtareas si alguna está cancelada? El contador de la Tarea padre incluye todas las Subtareas asociadas independientemente de su estado (no filtra por estado).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Al crear una Subtarea a partir de una Tarea padre, el sistema DEBE copiar automáticamente el Nivel de escalamiento vigente de la Tarea padre hacia la Subtarea, sin intervención del usuario.
- **FR-002**: Al crear una Subtarea a partir de una Tarea padre, el sistema DEBE copiar automáticamente el Usuario solicitante/cliente vigente de la Tarea padre hacia la Subtarea (incluyendo el caso de no tener ninguno asignado).
- **FR-003**: Al crear una Subtarea a partir de una Tarea padre, el sistema DEBE copiar automáticamente las Skills requeridas vigentes de la Tarea padre hacia la Subtarea.
- **FR-004**: Los valores heredados (FR-001 a FR-003) DEBEN quedar editables de forma independiente después de la creación, respetando los permisos ya vigentes sobre cada campo (p. ej. `tickets:manage_skills` para Skills); modificar la Subtarea después de creada NO DEBE alterar los valores de la Tarea padre, y viceversa.
- **FR-005**: El sistema DEBE exponer en el detalle de la Tarea padre la lista completa de sus Subtareas asociadas (código/nombre de cada una) junto con un contador total, actualizado automáticamente cada vez que se crea una nueva Subtarea desde ella.
- **FR-006**: Cada Subtarea listada en el detalle de la Tarea padre (FR-005) DEBE ser un hipervínculo que navegue al detalle de esa Subtarea.
- **FR-007**: El detalle de una Subtarea DEBE mostrar, dentro de la sección "Clasificación", un campo "Tarea Padre" con el código/nombre de la Tarea de origen.
- **FR-008**: El campo "Tarea Padre" (FR-007) DEBE ser un hipervínculo que, al hacer clic, navegue directamente al detalle de la Tarea padre correspondiente.
- **FR-009**: El campo "Tarea Padre" NO DEBE mostrarse en el detalle de un Ticket/Tarea que no sea una Subtarea (que no tenga Tarea padre asociada).
- **FR-010**: El sistema DEBE eliminar el parpadeo (flickering) actualmente observado en el panel izquierdo (Clasificación e Historial) del detalle del Ticket/Tarea al hacer scroll o interactuar con sus elementos, sin alterar la información ni las acciones ya disponibles en ese panel.
- **FR-011**: La corrección del parpadeo (FR-010) DEBE preservar el comportamiento y contenido actuales de las demás secciones del detalle del Ticket/Tarea (cronómetro, comentarios, acciones de estado), sin remover ni degradar funcionalidad existente.

### Key Entities *(include if feature involves data)*

- **Tarea/Subtarea**: Ticket interno que ya distingue una Subtarea de su Tarea padre mediante una referencia a esa Tarea de origen. Gana una lista derivada de sus propias Subtareas (para la Tarea padre) y expone, cuando ella misma es una Subtarea, el vínculo hacia su Tarea padre.
- **Nivel de escalamiento**: Atributo de clasificación de la Tarea/Subtarea que se copia de la Tarea padre a la Subtarea en el momento de la creación.
- **Usuario solicitante/cliente**: Contacto externo asociado a la Tarea/Subtarea que se copia de la Tarea padre a la Subtarea en el momento de la creación.
- **Skills requeridas**: Conjunto de habilidades asociadas a la Tarea/Subtarea que se copia de la Tarea padre a la Subtarea en el momento de la creación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las Subtareas nuevas creadas a partir de una Tarea padre nace con el mismo Nivel de escalamiento, Usuario solicitante y Skills requeridas que tenía la Tarea padre al momento de la creación, sin recaptura manual.
- **SC-002**: Un usuario puede identificar cuántas y cuáles Subtareas tiene una Tarea, y llegar al detalle de cualquiera de ellas, en un solo clic desde el detalle de la Tarea padre.
- **SC-003**: Un usuario puede volver de una Subtarea a su Tarea padre en un solo clic, sin tener que buscarla manualmente en el listado general.
- **SC-004**: Al desplazarse por el panel izquierdo del detalle de un Ticket/Tarea durante al menos 30 segundos continuos, no se observa ningún parpadeo o salto visual perceptible.

## Assumptions

- Se asume el modelo ya existente de Subtarea (Tarea vinculada a una Tarea padre) como base; esta feature no introduce un nuevo tipo de entidad, solo agrega comportamiento de herencia y visualización sobre la relación ya existente.
- La herencia (FR-001 a FR-003) ocurre una sola vez, en el momento de la creación de la Subtarea; no se especifica en el pedido del usuario un mecanismo de re-sincronización continua, por lo que se asume que valores heredados quedan congelados salvo edición manual posterior.
- Se asume un único nivel de anidamiento (Tarea → Subtarea), consistente con el modelo ya vigente en el sistema; crear una "Subtarea de una Subtarea" queda fuera de alcance.
- El conteo/listado de Subtareas de la Tarea padre (US2) es de solo lectura (no se pide en el pedido del usuario poder desvincular o reordenar Subtareas desde ahí).
- El parpadeo reportado (US4) es un defecto de la pantalla de detalle ya existente, no una regresión a introducir por esta misma feature; su corrección se acota al panel izquierdo (Clasificación + Historial) tal como lo describe el usuario, sin tocar otras pantallas.
