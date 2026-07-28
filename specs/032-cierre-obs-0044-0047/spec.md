# Feature Specification: Cierre de OBS-0044–OBS-0047 (Backlog UAT ITER-008)

**Feature Branch**: `032-cierre-obs-0044-0047`

**Created**: 2026-07-28

**Status**: Draft

**Input**: User description: "Resolver las 4 observaciones en estado Abierta del Backlog UAT (ITER-008, todas reportadas por Arely Pazmiño): (1) OBS-0044 (Defecto) — el historial de registros de tiempo muestra una hora ~5h distinta a la realmente ingresada al registrar tiempo manualmente (sospecha de bug de zona horaria); (2) OBS-0045 (Mejora) — la etiqueta 'Fuera de jornada' se superpone visualmente al horario de inicio/fin en el historial, dificultando su lectura; (3) OBS-0046 (Mejora) — no se genera notificación al asignar o reasignar un ticket a un resolutor; (4) OBS-0047 (Defecto) — el sistema permite asignar tickets a usuarios con estado Inactivo. Detalle completo en UAT/01_Iterations/ITER-008/ITER-008.md (inmutable). Cerrar actualizando Estado a 'Lista para Validar' en UAT/02_Backlog/BACKLOG.md."

## Contexto

`UAT/02_Backlog/BACKLOG.md` es la única fuente de verdad del estado de cada observación de pruebas (ver `UAT/CONVENTIONS.md`). Al momento de escribir esta especificación, las observaciones en estado **Abierta** son 4, todas reportadas por Arely Pazmiño en `ITER-008`, y son las que este feature debe resolver:

| ID | Módulo/Pantalla | Tipo | Iteración origen |
|---|---|---|---|
| OBS-0044 | Registro de tiempos > Historial de registros | Defecto | ITER-008 |
| OBS-0045 | Registro de tiempos > Historial de registros | Mejora | ITER-008 |
| OBS-0046 | Panel de Asignación / Notificaciones | Mejora | ITER-008 |
| OBS-0047 | Panel de Asignación | Defecto | ITER-008 |

El detalle completo de cada observación (descripción, pasos para reproducir, resultado esperado/actual, criterios de aceptación y evidencia gráfica) está documentado en `UAT/01_Iterations/ITER-008/ITER-008.md`, que es inmutable — este feature no lo modifica.

Las observaciones en otros estados (OBS-0001 a OBS-0043) quedan explícitamente **fuera de alcance** de este feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - La hora del historial de registros de tiempo coincide con la hora realmente ingresada (Priority: P1)

Un recurso registra tiempo manualmente sobre un ticket indicando una hora de inicio/fin real (ej. 17:37–17:38). Al revisar después el historial de registros de ese ticket, necesita ver exactamente la misma hora que ingresó, sin desfases.

**Why this priority**: Es un defecto de integridad de datos con impacto directo sobre el cálculo del SLA (specs 022/028) y sobre la confianza del usuario en los reportes de tiempo: un desfase de ~5 horas puede hacer aparecer tiempo como "fuera de jornada" cuando no lo fue, o alterar el cómputo de cumplimiento.

**Independent Test**: Registrar tiempo manualmente sobre un ticket indicando una hora de inicio/fin conocida y verificar que el historial de registros de tiempo del mismo ticket muestra exactamente esa hora, sin ninguna diferencia.

**Acceptance Scenarios**:

1. **Given** un ticket abierto, **When** un recurso registra tiempo manualmente indicando una hora de inicio y fin (ej. 17:37–17:38), **Then** el historial de registros de tiempo de ese ticket muestra la misma hora ingresada (17:37–17:38), sin desfase. (OBS-0044)
2. **Given** registros de tiempo ya existentes antes de esta corrección, **When** se visualiza el historial, **Then** la hora mostrada es consistente con la hora en la que realmente se realizó cada registro (no se reintroducen ni se acumulan nuevos desfases al leer datos históricos). (OBS-0044)
3. **Given** cualquier pantalla de la aplicación que muestre un registro de tiempo (historial, reportes, detalle del ticket), **When** se compara la hora mostrada entre pantallas para el mismo registro, **Then** la hora es idéntica en todas ellas. (OBS-0044)

---

### User Story 2 - La etiqueta "Fuera de jornada" no oculta el horario del registro (Priority: P2)

Un usuario revisa el historial de registros de tiempo de un ticket que incluye registros realizados fuera del horario laboral configurado. Necesita leer con claridad la hora de inicio y fin de cada registro, sin que la etiqueta informativa "Fuera de jornada" se superponga al texto del horario.

**Why this priority**: Es un defecto de legibilidad que afecta la revisión diaria de registros de tiempo, pero no bloquea ninguna operación ni compromete la integridad de los datos (a diferencia de OBS-0044); por eso va después en prioridad.

**Independent Test**: Generar un registro de tiempo fuera del horario laboral configurado, abrir el historial de registros de tiempo del ticket, y verificar que tanto la hora de inicio/fin como la etiqueta "Fuera de jornada" son completamente legibles y no se superponen entre sí.

**Acceptance Scenarios**:

1. **Given** un registro de tiempo realizado fuera del horario laboral configurado, **When** el usuario abre el historial de registros de tiempo, **Then** la hora de inicio y fin del registro es completamente visible, sin texto o elementos superpuestos. (OBS-0045)
2. **Given** el mismo registro, **When** el usuario localiza la etiqueta "Fuera de jornada", **Then** la etiqueta se muestra en una posición que no oculta ninguna parte del horario (ej. columna independiente, debajo del horario, badge al final de la fila, o ícono con tooltip). (OBS-0045)
3. **Given** el historial con varios registros mezclando horarios dentro y fuera de jornada, **When** el usuario lo recorre, **Then** la distribución de columnas/elementos se mantiene clara y consistente con el estilo visual del resto de la aplicación. (OBS-0045)

---

### User Story 3 - Notificación automática al asignar o reasignar un ticket (Priority: P1)

Un coordinador asigna o reasigna un ticket a un resolutor. El resolutor que recibe el ticket necesita enterarse de inmediato, sin tener que revisar manualmente el Panel de Asignación o sus tickets para descubrir que tiene trabajo nuevo asignado.

**Why this priority**: Sin esta notificación, un resolutor puede desconocer por tiempo indefinido que tiene un ticket asignado, retrasando la atención y arriesgando el cumplimiento del SLA desde el momento de la asignación. Es un vacío funcional que afecta la operación diaria de todo el equipo de resolutores.

**Independent Test**: Asignar un ticket sin resolutor previo a un resolutor, y luego reasignar ese mismo ticket a un segundo resolutor; verificar en ambos casos que el resolutor receptor recibe una notificación en el centro de notificaciones de la aplicación, con la información básica del ticket, y que al seleccionarla es dirigido al detalle del ticket correspondiente.

**Acceptance Scenarios**:

1. **Given** un ticket sin resolutor asignado, **When** un coordinador lo asigna a un resolutor, **Then** el resolutor recibe una notificación en el centro de notificaciones de la aplicación. (OBS-0046)
2. **Given** un ticket ya asignado a un resolutor, **When** se reasigna a un resolutor distinto, **Then** el nuevo resolutor recibe una notificación equivalente. (OBS-0046)
3. **Given** una notificación de asignación de ticket, **When** el usuario la abre, **Then** incluye al menos: número del ticket, cliente, prioridad, estado actual, quién realizó la asignación y fecha/hora de la asignación. (OBS-0046)
4. **Given** una notificación de asignación de ticket, **When** el usuario la selecciona, **Then** es dirigido directamente al detalle del ticket correspondiente. (OBS-0046)

---

### User Story 4 - Los usuarios inactivos no pueden recibir nuevas asignaciones de tickets (Priority: P1)

Un coordinador va a asignar un ticket a un resolutor. Necesita que el sistema le impida asignarlo a un usuario cuya cuenta está marcada como Inactiva, para evitar que un ticket quede en manos de alguien que ya no debería operar en el sistema.

**Why this priority**: Es un defecto de control de acceso con impacto operativo directo: un ticket asignado a un usuario inactivo puede quedar sin atención real, sin que nadie lo note hasta que ya haya vencido el SLA. Mismo nivel de urgencia que OBS-0044 al tratarse de un defecto (no una mejora).

**Independent Test**: Marcar un usuario con rol Resolutor como Inactivo, intentar asignarle un ticket desde el Panel de Asignación (o el detalle de un ticket), y verificar que el sistema lo impide de forma clara, ya sea excluyéndolo de la lista de opciones o mostrándolo deshabilitado con un mensaje explicativo.

**Acceptance Scenarios**:

1. **Given** un usuario con rol Resolutor marcado como Inactivo, **When** un coordinador abre el selector de resolutor para asignar un ticket, **Then** ese usuario no aparece como opción seleccionable (o aparece visiblemente deshabilitado). (OBS-0047)
2. **Given** un intento de asignar un ticket a un usuario inactivo (por ejemplo, por una solicitud directa a la API, sin pasar por el selector de la interfaz), **When** se procesa la asignación, **Then** el sistema la rechaza y no persiste el cambio. (OBS-0047)
3. **Given** un intento de asignación rechazado por usuario inactivo, **When** el coordinador lo intenta desde la interfaz, **Then** ve un mensaje claro indicando que el usuario seleccionado no está disponible. (OBS-0047)
4. **Given** un ticket ya asignado a un usuario que luego pasa a estado Inactivo, **When** se consulta el ticket, **Then** la asignación previa se conserva sin cambios (esta observación cubre nuevas asignaciones, no la desasignación retroactiva de asignaciones ya existentes). (OBS-0047)

---

### Edge Cases

- ¿Qué ocurre con los registros de tiempo ya guardados antes de corregir OBS-0044? La corrección aplica al cálculo/presentación de la hora; no se requiere una migración de datos históricos salvo que la causa raíz confirme que el dato almacenado en sí es incorrecto (a diferencia de un error solo de presentación) — a determinar en la fase de planificación técnica.
- ¿Qué pasa si un registro de tiempo está exactamente en el límite del horario laboral (ej. justo a la hora de inicio o fin de jornada)? Debe clasificarse de forma consistente con el criterio ya usado por specs 022/028 para "dentro" vs "fuera" de jornada; esta observación no cambia ese criterio, solo la legibilidad de su etiqueta.
- ¿Qué ocurre si un ticket se asigna automáticamente (ej. reglas de asignación) en lugar de manualmente por un coordinador? La notificación (OBS-0046) debe generarse igual, sin importar si la asignación fue manual o automática, ya que el resolutor la recibe de la misma forma.
- ¿Qué pasa si el usuario que asigna el ticket es el mismo que lo recibe (auto-asignación)? Debe seguir generándose la notificación, salvo que el patrón ya existente del centro de notificaciones excluya explícitamente auto-notificaciones para otras acciones (a verificar contra el comportamiento actual del sistema).
- ¿Puede un usuario inactivo seguir apareciendo como resolutor en tickets que ya tenía asignados antes de inactivarse? Sí — OBS-0047 solo bloquea *nuevas* asignaciones; los tickets ya asignados a ese usuario no se reasignan ni se ocultan automáticamente.
- ¿Qué pasa si se intenta reactivar a un usuario inactivo? Al volver a estado Activo, debe poder recibir nuevas asignaciones normalmente (comportamiento estándar del campo de estado, no requiere lógica adicional).

## Requirements *(mandatory)*

### Functional Requirements

**Corrección de la hora en el historial de registros de tiempo (User Story 1)**

- **FR-001**: El sistema MUST mostrar en el historial de registros de tiempo la misma hora de inicio/fin que fue efectivamente ingresada al registrar el tiempo manualmente, sin desfases. (OBS-0044)
- **FR-002**: El sistema MUST presentar de forma consistente la hora de un mismo registro de tiempo en todas las pantallas donde se muestre (historial, detalle del ticket, reportes). (OBS-0044)

**Reubicación de la etiqueta "Fuera de jornada" (User Story 2)**

- **FR-003**: El sistema MUST mostrar la hora de inicio y fin de cada registro de tiempo de forma completamente legible en el historial, sin que ningún elemento visual la oculte parcial o totalmente. (OBS-0045)
- **FR-004**: El sistema MUST mostrar la etiqueta "Fuera de jornada" en una posición que no se superponga al texto del horario (ej. columna independiente, debajo del horario, badge al final de la fila, o ícono con tooltip). (OBS-0045)
- **FR-005**: La presentación del historial de registros de tiempo, incluida la etiqueta reubicada, MUST mantenerse consistente con los estándares visuales ya usados en el resto de la aplicación. (OBS-0045)

**Notificación de asignación/reasignación de tickets (User Story 3)**

- **FR-006**: El sistema MUST generar una notificación al resolutor cada vez que un ticket le sea asignado por primera vez. (OBS-0046)
- **FR-007**: El sistema MUST generar una notificación al nuevo resolutor cada vez que un ticket ya asignado sea reasignado a otro resolutor. (OBS-0046)
- **FR-008**: Cada notificación de asignación MUST incluir como mínimo: número del ticket, cliente, prioridad, estado actual, usuario que realizó la asignación y fecha/hora de la asignación. (OBS-0046)
- **FR-009**: El sistema MUST mostrar estas notificaciones en el centro de notificaciones ya existente en la aplicación. (OBS-0046)
- **FR-010**: Al seleccionar una notificación de asignación, el sistema MUST dirigir al usuario directamente al detalle del ticket correspondiente. (OBS-0046)

**Bloqueo de asignación a usuarios inactivos (User Story 4)**

- **FR-011**: El sistema MUST impedir que un ticket sea asignado a un usuario cuyo estado sea Inactivo, tanto desde la interfaz como ante una solicitud directa que intente omitirla. (OBS-0047)
- **FR-012**: El selector de resolutor usado para asignar/reasignar tickets MUST excluir a los usuarios inactivos de las opciones seleccionables, o mostrarlos visiblemente deshabilitados. (OBS-0047)
- **FR-013**: Cuando se intente asignar un ticket a un usuario inactivo, el sistema MUST mostrar un mensaje claro indicando que el usuario seleccionado no está disponible. (OBS-0047)
- **FR-014**: Esta restricción MUST aplicar únicamente a nuevas asignaciones; las asignaciones existentes de un usuario que pasa a estado Inactivo MUST conservarse sin alteración automática. (OBS-0047)

**Trazabilidad con el framework UAT**

- **FR-015**: Al completar y verificar cada corrección, el desarrollador MUST actualizar el `Estado` de la observación correspondiente (OBS-0044, OBS-0045, OBS-0046, OBS-0047) en `UAT/02_Backlog/BACKLOG.md` a `Lista para Validar`, siguiendo el flujo documentado en `UAT/CONVENTIONS.md`. `ITER-008.md` MUST NOT editarse retroactivamente en su contenido narrativo.

### Key Entities *(include if feature involves data)*

- **Registro de tiempo (Work Session)**: entrada de tiempo trabajado sobre un ticket, con hora de inicio, hora de fin y un indicador de si ocurrió fuera del horario laboral configurado (`off_hours`, ya introducido en spec 028); esta observación no cambia el criterio de clasificación, corrige la hora mostrada (OBS-0044) y la presentación de la etiqueta (OBS-0045).
- **Ticket**: registro de trabajo (Incidente/Requerimiento) con un resolutor asignado; el evento de asignación/reasignación es el disparador de la notificación de OBS-0046 y el punto de control de OBS-0047.
- **Notificación**: entidad ya existente en el sistema (centro de notificaciones); esta observación agrega un nuevo evento generador (asignación/reasignación de ticket) al catálogo de eventos que ya disparan notificaciones.
- **Usuario**: cuenta con un estado Activo/Inactivo ya modelado en el sistema; esta observación usa ese estado existente como condición para permitir o bloquear una asignación de ticket, no introduce un nuevo concepto de estado.
- **Observación UAT**: entidad del framework `UAT/` (`OBS-XXXX`) con módulo, tipo, estado y criterios de aceptación — unidad de trabajo y trazabilidad de este feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100% de los registros de tiempo nuevos, la hora mostrada en el historial coincide exactamente con la hora ingresada al momento del registro.
- **SC-002**: En el 100% de los registros fuera de jornada revisados, la hora de inicio/fin y la etiqueta "Fuera de jornada" son legibles simultáneamente, sin superposición.
- **SC-003**: En el 100% de las asignaciones y reasignaciones de tickets de prueba, el resolutor receptor recibe una notificación con la información mínima requerida, y puede llegar al detalle del ticket desde ella en un solo paso.
- **SC-004**: En el 100% de los intentos de prueba de asignar un ticket a un usuario inactivo, el sistema los rechaza y muestra un mensaje claro, sin persistir el cambio.
- **SC-005**: Las 4 observaciones "Abierta" del backlog (OBS-0044 a OBS-0047) quedan actualizadas a `Lista para Validar` en `UAT/02_Backlog/BACKLOG.md` al completar la implementación, sin alterar el contenido narrativo histórico de `ITER-008.md`.

## Assumptions

- La causa de OBS-0044 es un desfase de conversión de zona horaria entre el momento de ingreso y el de presentación (consistente con la sospecha ya registrada en `ITER-008.md`); el diagnóstico exacto (almacenamiento vs. presentación) se confirma en la fase de planificación técnica, pero el resultado observable exigido es el mismo: la hora mostrada debe coincidir con la ingresada.
- OBS-0045 es un cambio de presentación visual sobre el componente de historial ya existente; no elimina la información "Fuera de jornada" ni cambia el criterio que la determina (definido en spec 028), solo su ubicación/forma de mostrarla.
- OBS-0046 reutiliza el centro de notificaciones y el mecanismo de notificación ya existentes en el sistema (usados hoy para otros eventos); no introduce un canal de notificación nuevo (ej. correo o push), solo un nuevo evento generador.
- El estado "Inactivo" referido en OBS-0047 es el mismo campo de estado de usuario ya modelado y usado en Maestros > Equipo; esta observación no introduce un nuevo estado, solo una nueva validación que lo consulta.
- Las 4 observaciones se implementan y prueban en Docker local, consistente con el resto de features de este repositorio.
- El "responsable de validación" de este feature, siguiendo `UAT/CONVENTIONS.md`, es quien reportó las observaciones originales (Arely Pazmiño) u otro consultor UAT asignado; este feature no incluye la validación/retest en sí, solo deja el backlog en estado `Lista para Validar`.
