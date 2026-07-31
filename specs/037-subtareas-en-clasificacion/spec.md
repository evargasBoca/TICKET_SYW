# Feature Specification: Referencia a Subtareas dentro de "Clasificación" en la Tarea principal

**Feature Branch**: `037-subtareas-en-clasificacion`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "cuando creo una subTareas, no se muestra en la Tareas principal, que tenga subtareas realcionada en Clasificación"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver de un vistazo que una Tarea tiene Subtareas, desde su Clasificación (Priority: P1)

Un usuario que abre el detalle de una Tarea que ya tiene una o más Subtareas creadas quiere poder
notarlo directamente en la sección "Clasificación" (donde ya se listan Cliente, Proyecto,
Encargado, etc.), sin depender únicamente de bajar la vista hasta la tarjeta separada
"Subtareas" del panel lateral. Hoy esa tarjeta lateral existe y funciona (lista y permite crear
Subtareas), pero "Clasificación" no refleja en absoluto que la Tarea tiene Subtareas asociadas —
el usuario percibe esto como si la Subtarea recién creada "no se mostrara" en la Tarea principal.

**Why this priority**: Es la corrección directa de lo reportado: hoy la relación Tarea→Subtareas
es invisible en el lugar donde el usuario espera verla (junto al resto de los datos de
clasificación), generando la sensación de que la creación de la Subtarea no tuvo efecto sobre la
Tarea padre.

**Independent Test**: Crear una Subtarea desde una Tarea sin Subtareas previas y, sin salir del
detalle de esa Tarea (o recargándolo), verificar que la sección "Clasificación" ahora muestra que
tiene 1 Subtarea asociada, navegable a su detalle.

**Acceptance Scenarios**:

1. **Given** una Tarea sin Subtareas, **When** el usuario abre su detalle, **Then** la sección
   "Clasificación" no muestra ninguna referencia a Subtareas (o la muestra explícitamente como
   "Sin subtareas"), de forma consistente con el resto de campos opcionales de esa sección.
2. **Given** una Tarea sin Subtareas, **When** el usuario crea una Subtarea desde ella (tarjeta
   "Subtareas" ya existente) y vuelve a ver el detalle de la Tarea, **Then** la sección
   "Clasificación" muestra que tiene 1 Subtarea asociada, con su código/título visible.
3. **Given** una Tarea con 3 Subtareas ya asociadas, **When** el usuario abre su detalle,
   **Then** "Clasificación" muestra las 3 (o al menos el conteo total, con acceso a cada una).
4. **Given** el campo de Subtareas visible en "Clasificación" de la Tarea, **When** el usuario
   hace clic sobre una Subtarea listada ahí, **Then** navega directamente al detalle de esa
   Subtarea (mismo comportamiento ya existente en la tarjeta lateral "Subtareas").
5. **Given** un Ticket o una Subtarea (no una Tarea con Subtareas propias), **When** el usuario
   abre su detalle, **Then** no aparece ningún campo de Subtareas en "Clasificación" (ya cubierto
   por "Sin subtareas" solo aplica a Tareas de Nivel 4; una Subtarea nunca tiene Subtareas
   propias, regla ya vigente del sistema).

### Edge Cases

- ¿Qué pasa si la Tarea tiene muchas Subtareas (ej. 10+)? El campo en "Clasificación" debe seguir
  siendo legible sin romper el layout de la sección — se prioriza mostrar el conteo total con
  acceso a la lista completa (ya existente en la tarjeta lateral "Subtareas"), no duplicar cada
  fila individual dentro de "Clasificación" si eso degrada la lectura de los demás campos.
- ¿Aplica esto a un Ticket normal? No — un Ticket nunca tiene Subtareas (regla ya vigente); el
  campo no debe aparecer ahí.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La sección "Clasificación" del detalle de una Tarea (registro de Nivel 4, sin
  Tarea padre propia) DEBE mostrar una referencia a sus Subtareas asociadas cuando existan.
- **FR-002**: Cuando la Tarea no tiene ninguna Subtarea asociada, la sección "Clasificación" DEBE
  reflejarlo explícitamente (ej. "Sin subtareas"), no simplemente omitir el campo sin explicación,
  para que su ausencia sea indistinguible de un error de carga.
- **FR-003**: Cada Subtarea referenciada en "Clasificación" DEBE ser navegable a su propio
  detalle en un solo clic, igual que el resto de referencias cruzadas ya existentes en esa misma
  sección (Registro relacionado, Tarea Padre).
- **FR-004**: La actualización de esta referencia DEBE reflejar inmediatamente cualquier
  Subtarea nueva creada desde la propia Tarea (sin requerir pasos adicionales más allá de ver
  el detalle actualizado de la Tarea).
- **FR-005**: Este campo NO DEBE aparecer en el detalle de un Ticket ni en el de una Subtarea
  (que nunca tiene Subtareas propias, regla ya vigente del sistema).
- **FR-006**: Esta adición es aditiva sobre la tarjeta lateral "Subtareas" ya existente (listado
  + creación) — no la reemplaza ni le quita funcionalidad.

### Key Entities *(include if feature involves data)*

- **Tarea**: Ya conoce su propia lista de Subtareas asociadas (relación ya existente,
  autorreferencial). Esta feature solo agrega dónde y cómo se muestra esa relación ya conocida,
  sin cambiar su origen de datos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las Tareas con Subtareas asociadas muestra esa relación directamente en
  "Clasificación", sin que el usuario tenga que buscarla en otra parte de la pantalla.
- **SC-002**: Un usuario puede confirmar, inmediatamente después de crear una Subtarea y sin
  pasos adicionales, que la Tarea padre ahora la refleja en su propia Clasificación.
- **SC-003**: Un usuario puede llegar al detalle de cualquier Subtarea referenciada en
  "Clasificación" en un solo clic.

## Assumptions

- Se asume que la tarjeta lateral "Subtareas" (listado completo + creación) se mantiene sin
  cambios — esta feature agrega una referencia complementaria dentro de "Clasificación", no
  migra ni elimina funcionalidad ya existente.
- Se asume que "mostrar" en Clasificación significa, como mínimo, el conteo total con acceso
  navegable a cada Subtarea (mismo dato ya expuesto por la API, `subtasks`); no se pide en el
  reporte del usuario ninguna información adicional por Subtarea (estado, encargado, etc.) más
  allá de lo que ya muestra la tarjeta lateral existente.
- Se asume que el campo se posiciona en "Clasificación" de forma consistente con el resto de
  referencias cruzadas ya existentes ahí (Registro relacionado, Tarea Padre — agregado en la
  feature anterior, spec 036).
