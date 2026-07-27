# Feature Specification: Cierre de OBS-0042/OBS-0043 (Backlog UAT ITER-007)

**Feature Branch**: `030-cierre-obs-0042-0043`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Resolver OBS-0042 y OBS-0043 del Backlog UAT (ITER-007): (1) reorganizar el layout del Detalle del Ticket para reducir el scroll excesivo cuando el historial de comentarios es extenso; (2) en SLA Configurable, identificar el cliente de cada proyecto para distinguir proyectos homónimos."

## Contexto

`UAT/02_Backlog/BACKLOG.md` es la única fuente de verdad del estado de cada observación de pruebas (ver `UAT/CONVENTIONS.md`). Al momento de escribir esta especificación, las observaciones en estado **Abierta** son 2, ambas reportadas por Juan Murcia en `ITER-007`, y son las que este feature debe resolver:

| ID | Módulo/Pantalla | Tipo | Iteración origen |
|---|---|---|---|
| OBS-0042 | Tickets > Detalle del Ticket | Mejora | ITER-007 |
| OBS-0043 | SLA Configurable | Mejora | ITER-007 |

Las observaciones en otros estados (OBS-0001 a OBS-0040) quedan explícitamente **fuera de alcance** de este feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acceso permanente a las acciones del ticket sin importar el largo del historial (Priority: P1)

Un usuario abre un ticket con un historial de comentarios extenso. Necesita redactar un comentario nuevo o cambiar el estado del ticket sin tener que desplazarse hasta el final de una línea de tiempo larga cada vez.

**Why this priority**: Es el defecto de usabilidad de mayor fricción diaria: entre más activo/antiguo es un ticket, más comentarios acumula, y hoy el costo de interactuar con él (scroll) crece sin límite. Afecta a todo usuario que opera tickets con historial largo.

**Independent Test**: Abrir un ticket con un número elevado de comentarios y verificar que la caja de nuevo comentario y las acciones de cambio de estado son visibles/usables sin necesidad de desplazarse por todo el historial, y que el historial en sí conserva su propio scroll acotado.

**Acceptance Scenarios**:

1. **Given** un ticket con un historial de comentarios extenso, **When** el usuario abre el detalle del ticket, **Then** la sección "Comentarios y acciones" (redacción de nuevo comentario + cambio de estado) se ubica en la columna derecha de la pantalla, en el espacio donde hoy se muestra "Clasificación". (OBS-0042)
2. **Given** el detalle de un ticket, **When** el usuario revisa la columna donde antes estaba "Comentarios y acciones", **Then** encuentra ahí la sección "Clasificación". (OBS-0042)
3. **Given** un ticket con historial de comentarios extenso, **When** el usuario se desplaza por el historial, **Then** la caja para redactar un nuevo comentario y los botones de cambio de estado permanecen visibles/fijos en pantalla, sin ocultarse ni desplazarse fuera de vista. (OBS-0042)
4. **Given** un historial de comentarios que excede el alto disponible en pantalla, **When** el usuario lo recorre, **Then** el desplazamiento queda contenido dentro de la propia lista de comentarios (scroll interno con alto máximo definido), sin arrastrar al resto de la página. (OBS-0042)
5. **Given** el detalle del ticket reorganizado, **When** se visualiza en distintos anchos de pantalla (escritorio y tamaños reducidos), **Then** el diseño se mantiene responsivo y alineado con los estándares visuales del sistema, sin overlaps ni contenido cortado. (OBS-0042)

---

### User Story 2 - Distinguir proyectos homónimos de distintos clientes en SLA Configurable (Priority: P1)

Un administrador de SLA necesita filtrar, crear o revisar reglas de SLA para un proyecto específico. Cuando dos o más clientes tienen proyectos con el mismo nombre (ej. "Soporte"), necesita saber a qué cliente pertenece cada uno antes de actuar, sin arriesgarse a modificar la regla del proyecto equivocado.

**Why this priority**: Es un riesgo de error operativo directo: configurar o interpretar mal un SLA por confundir el proyecto de un cliente con el de otro tiene impacto contractual. Con solo 2 clientes ya sembrados (Aris, Vaxthera) ambos con proyecto "Soporte", el problema ya es reproducible hoy.

**Independent Test**: Con al menos dos clientes que tengan un proyecto del mismo nombre, abrir SLA Configurable y verificar que el filtro, el formulario de creación/edición y la tabla de reglas permiten identificar sin ambigüedad a qué cliente pertenece cada proyecto.

**Acceptance Scenarios**:

1. **Given** dos o más clientes con un proyecto del mismo nombre, **When** el usuario abre el selector "Filtrar por proyecto" en SLA Configurable, **Then** cada opción del listado muestra el cliente junto al nombre del proyecto, permitiendo distinguir entre proyectos homónimos. (OBS-0043)
2. **Given** el formulario de creación o edición de una regla de SLA, **When** el usuario selecciona un proyecto, **Then** el formulario muestra el cliente al que pertenece ese proyecto. (OBS-0043)
3. **Given** la tabla de reglas de SLA, **When** el usuario la consulta, **Then** cada fila muestra el cliente del proyecto en una columna dedicada, además del nombre del proyecto. (OBS-0043)

---

### Edge Cases

- ¿Qué ocurre si el historial de comentarios de un ticket está vacío o tiene muy pocos comentarios? La sección "Comentarios y acciones" debe seguir ubicada en la columna derecha y comportarse igual, sin que el layout dependa de la cantidad de comentarios.
- ¿Cómo se comporta la reorganización del layout en la vista del Usuario/cliente del ticket (rol Usuario/cliente, con permisos distintos a los del resolutor interno)? Debe conservar la misma ubicación de columnas, mostrando únicamente las acciones que ese rol ya tiene permitidas hoy.
- ¿Qué pasa si un proyecto no tiene SLA configurado en absoluto, pero se le filtra desde el selector? El nombre del cliente debe seguir siendo visible en el filtro aunque no existan reglas asociadas.
- ¿Cómo se distingue un proyecto homónimo cuando el nombre del cliente también es muy largo? El formato de presentación (proyecto + cliente) debe seguir siendo legible en el ancho de columna/selector disponible, truncando con indicador visual si es necesario, sin perder la distinción entre proyectos.
- ¿Qué ocurre si el usuario redimensiona la ventana o cambia de escritorio a un ancho reducido mientras tiene el detalle del ticket abierto? El comportamiento fijo de "Comentarios y acciones" y el scroll interno del historial deben mantenerse consistentes en el nuevo ancho.

## Requirements *(mandatory)*

### Functional Requirements

**Reorganización del layout del Detalle del Ticket (User Story 1)**

- **FR-001**: El sistema MUST ubicar la sección "Comentarios y acciones" (redacción de nuevo comentario + acciones de cambio de estado) en la columna derecha del detalle del ticket, en el espacio que hoy ocupa "Clasificación". (OBS-0042)
- **FR-002**: El sistema MUST ubicar la sección "Clasificación" en el espacio que hoy ocupa "Comentarios y acciones". (OBS-0042)
- **FR-003**: La caja de redacción de nuevo comentario y los botones de cambio de estado MUST permanecer visibles en pantalla mientras el usuario se desplaza por el historial de comentarios, sin ocultarse ni desplazarse fuera del área visible. (OBS-0042)
- **FR-004**: El historial de comentarios MUST tener su propio contenedor de desplazamiento (scroll interno) con un alto máximo definido, independiente del scroll general de la página. (OBS-0042)
- **FR-005**: El layout reorganizado del detalle del ticket MUST mantenerse responsivo y consistente con los estándares visuales ya usados en el resto de la aplicación, en los distintos tamaños de pantalla soportados hoy por esa vista. (OBS-0042)

**Identificación del cliente en SLA Configurable (User Story 2)**

- **FR-006**: El selector "Filtrar por proyecto" en SLA Configurable MUST mostrar, para cada proyecto listado, el cliente al que pertenece, de forma que dos proyectos con el mismo nombre de distintos clientes se distingan sin ambigüedad. (OBS-0043)
- **FR-007**: El formulario de creación/edición de una regla de SLA MUST mostrar el cliente del proyecto seleccionado. (OBS-0043)
- **FR-008**: La tabla de reglas de SLA MUST incluir una columna "Cliente" que muestre el cliente del proyecto de cada regla. (OBS-0043)

**Trazabilidad con el framework UAT**

- **FR-009**: Al completar y verificar cada corrección, el desarrollador MUST actualizar el `Estado` de la observación correspondiente (OBS-0042, OBS-0043) en `UAT/02_Backlog/BACKLOG.md` a `Lista para Validar`, siguiendo el flujo documentado en `UAT/CONVENTIONS.md`. `ITER-007.md` MUST NOT editarse retroactivamente en su contenido narrativo (agregar el archivo de evidencia pendiente en `images/` no se considera una edición de contenido).

### Key Entities *(include if feature involves data)*

- **Ticket**: registro de trabajo (Incidente/Requerimiento) mostrado en una pantalla de detalle con secciones de Clasificación, Comentarios/historial y Acciones de estado.
- **Comentario**: entrada individual del historial de un ticket, mostrada en orden cronológico dentro de la línea de tiempo.
- **Regla de SLA**: configuración de tiempos límite (Contacto, Diagnóstico/Análisis/Ejecución) asociada a un Proyecto y una Prioridad.
- **Proyecto**: pertenece a un único Cliente; dos proyectos de distintos clientes pueden compartir el mismo nombre (ya validado en specs 015/016 — Encargado en múltiples Proyectos / desambiguación de Proyectos homónimos).
- **Cliente**: entidad a la que pertenece un Proyecto; es el dato que falta mostrar en el flujo de SLA Configurable para desambiguar proyectos homónimos.
- **Observación UAT**: entidad del framework `UAT/` (`OBS-XXXX`) con módulo, tipo, estado y criterios de aceptación — unidad de trabajo y trazabilidad de este feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100% de los tickets de prueba con historial extenso, un usuario puede redactar un comentario nuevo o cambiar el estado del ticket sin necesidad de desplazarse por el historial completo.
- **SC-002**: El historial de comentarios de cualquier ticket de prueba se desplaza dentro de su propio contenedor, sin arrastrar el scroll de la página completa, verificado en el 100% de los casos con historial extenso.
- **SC-003**: El layout reorganizado se valida sin overlaps ni contenido cortado en los tamaños de pantalla soportados hoy por la vista de detalle del ticket.
- **SC-004**: Con al menos dos clientes que comparten un nombre de proyecto, el 100% de las pantallas de SLA Configurable (filtro, formulario, tabla) permiten identificar sin ambigüedad a qué cliente pertenece cada proyecto listado.
- **SC-005**: Las 2 observaciones "Abierta" del backlog (OBS-0042, OBS-0043) quedan actualizadas a `Lista para Validar` en `UAT/02_Backlog/BACKLOG.md` al completar la implementación, sin alterar el contenido narrativo histórico de `ITER-007.md`.

## Assumptions

- La reorganización de columnas (OBS-0042) es un cambio de disposición visual sobre los componentes ya existentes de Clasificación y Comentarios/acciones; no se agregan ni eliminan campos o funcionalidades dentro de esas secciones.
- "Fijo en pantalla" (FR-003) se interpreta como que la sección permanece visible/accesible durante el scroll dentro del detalle del ticket (patrón sticky), consistente con el resto de vistas de la aplicación; no implica una ventana flotante independiente ni un rediseño de la navegación general del sitio.
- El "cliente" a mostrar en SLA Configurable (OBS-0043) es el mismo dato de Cliente ya modelado y usado en Maestros > Clientes/Proyectos (specs 001, 010, 015, 016); este feature expone ese dato ya existente en las pantallas de SLA, no introduce un nuevo concepto de cliente.
- Ambas observaciones se implementan y prueban en Docker local, consistente con el resto de features de este repositorio.
- El "responsable de validación" de este feature, siguiendo `UAT/CONVENTIONS.md`, es quien reportó las observaciones originales (Juan Murcia) u otro consultor UAT asignado; este feature no incluye la validación/retest en sí, solo deja el backlog en estado `Lista para Validar`.
