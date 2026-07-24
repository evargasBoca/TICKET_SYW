# Feature Specification: Cierre de observaciones "Abierta" del Backlog UAT (SLA, Tickets, Calendario)

**Feature Branch**: `028-cierre-backlog-uat-abierto`

**Created**: 2026-07-24

**Status**: Draft

**Input**: User description: "quiero que realice los ajustes y iteraciones que solicita en el Backlog solo aquellas que están Abierta, siguiendo toda la estructura de 'UAT'"

## Contexto

`UAT/02_Backlog/BACKLOG.md` es la única fuente de verdad del estado de cada observación de pruebas (ver `UAT/CONVENTIONS.md`). Al momento de escribir esta especificación, las observaciones en estado **Abierta** son 12, todas reportadas por Arely Pazmiño en `ITER-004` e `ITER-005`, y son las que este feature debe resolver:

| ID | Módulo/Pantalla | Tipo | Iteración origen |
|---|---|---|---|
| OBS-0029 | SLA Configurable | Defecto | ITER-004 |
| OBS-0030 | SLA Configurable | Defecto | ITER-004 |
| OBS-0031 | SLA Configurable | Mejora | ITER-004 |
| OBS-0032 | Tickets > Detalle del Ticket | Mejora | ITER-004 |
| OBS-0033 | Tickets > Nuevo Ticket | Defecto | ITER-004 |
| OBS-0034 | Tickets > Nuevo Ticket | Mejora | ITER-004 |
| OBS-0035 | Tickets > Detalle del Ticket > Registro de tiempos | Defecto | ITER-004 |
| OBS-0036 | Tickets > Registro de tiempos | Mejora | ITER-004 |
| OBS-0037 | Equipo > Perfil del recurso / Calendario | Mejora | ITER-004 |
| OBS-0038 | Tickets > Detalle del Ticket > SLA | Defecto | ITER-005 |
| OBS-0039 | Tickets > Detalle del Ticket > SLA | Defecto | ITER-005 |
| OBS-0040 | Tickets > Panel de Asignación / Detalle del Ticket | Mejora | ITER-005 |

Las observaciones en otros estados (`Lista para Validar`, `Rechazada`, etc. — OBS-0001 a OBS-0028) quedan explícitamente **fuera de alcance** de este feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - El SLA solo contabiliza tiempo laboral real, sin importar cuándo se crea o cambia de estado el ticket (Priority: P1)

Un recurso tiene configurado un horario laboral (ej. 08:00–17:00). Un ticket se crea o cambia de estado en cualquier momento — dentro o fuera de ese horario — y el SLA debe reflejar únicamente el tiempo laboral realmente transcurrido, nunca más, y nunca marcar el ticket como vencido antes de tiempo.

**Why this priority**: El SLA es el indicador contractual de cumplimiento frente al cliente. Hoy el sistema genera falsos "Vencido" (ej. un ticket con ~1h de trabajo real aparece con 3h u 10h consumidas), lo que rompe la confianza en el indicador y puede derivar en incumplimientos reportados incorrectamente. Es el defecto de mayor impacto de negocio del backlog abierto.

**Independent Test**: Configurar un calendario con horario laboral acotado, crear/asignar/cambiar de estado un ticket en distintos momentos (dentro y fuera de jornada, con el SLA pausado), y verificar que el contador de SLA coincide con el tiempo laboral real transcurrido en cada caso, sin necesidad de que ninguna otra observación esté resuelta.

**Acceptance Scenarios**:

1. **Given** un ticket con tiempo registrado fuera del horario laboral mientras el SLA está pausado, **When** vuelve a iniciar el horario laboral, **Then** el SLA muestra el tiempo restante correcto según el tiempo laboral efectivamente consumido.
2. **Given** el escenario anterior, **When** se cambia el estado del ticket (ej. a "Solicitud de información"), **Then** el SLA no debe saltar a un valor mayor al tiempo laboral real transcurrido ni marcarse como vencido antes de agotar el límite configurado. (OBS-0038)
3. **Given** un ticket creado fuera del horario laboral configurado, **When** se asigna a un resolutor, **Then** el conteo de SLA inicia únicamente al comenzar el siguiente período laboral, conservando la fecha/hora real de creación. (OBS-0039)
4. **Given** un ticket que se crea o asigna fuera del horario laboral, **When** se consulta su historial, **Then** el sistema permite distinguir la hora de creación, la hora de asignación, el inicio efectivo del SLA y el inicio de la jornada laboral aplicable. (OBS-0040)

---

### User Story 2 - Un ticket cerrado no admite nuevos registros de tiempo (Priority: P1)

Cuando un ticket pasa a estado Cerrado, cualquier cronómetro activo se detiene automáticamente y no se puede iniciar un registro de tiempo nuevo sobre ese ticket, sin afectar el registro de tiempo del recurso en otros tickets o tareas.

**Why this priority**: Es un defecto de integridad de datos con impacto directo en la facturación y el reporte de tiempos: hoy es posible seguir sumando horas a un ticket ya finalizado.

**Independent Test**: Iniciar un cronómetro en un ticket, cerrarlo sin detenerlo manualmente, y verificar que el cronómetro se detiene solo, que no se puede iniciar un nuevo registro sobre ese ticket, y que el recurso puede seguir registrando tiempo con normalidad en otros tickets/tareas activos.

**Acceptance Scenarios**:

1. **Given** un cronómetro activo sobre un ticket, **When** el ticket cambia a estado Cerrado, **Then** el cronómetro se detiene automáticamente y el tiempo acumulado hasta ese momento se conserva. (OBS-0035)
2. **Given** un ticket en estado Cerrado, **When** el usuario intenta iniciar un nuevo registro de tiempo sobre él, **Then** el sistema lo bloquea y muestra un mensaje indicando que el ticket ya fue finalizado. (OBS-0035)
3. **Given** un ticket recién cerrado, **When** el mismo recurso inicia o continúa un registro de tiempo en otro ticket/tarea activo, **Then** esa operación no se ve afectada por el cierre del primero. (OBS-0035)

---

### User Story 3 - El título del ticket se valida antes de guardarse (Priority: P2)

Al crear un ticket, el sistema exige un título con contenido real (no solo espacios) y aplica la política de caracteres permitidos definida por el negocio.

**Why this priority**: Afecta la calidad de los datos y la legibilidad de los listados de tickets, pero no compromete SLA ni facturación.

**Independent Test**: Intentar crear tickets con título vacío/solo espacios y con caracteres especiales/emojis, y verificar el comportamiento de validación en cada caso, sin depender de otras observaciones.

**Acceptance Scenarios**:

1. **Given** el formulario de creación de ticket, **When** el usuario ingresa únicamente espacios en blanco como título y guarda, **Then** el sistema rechaza el guardado y muestra un mensaje indicando que el título es obligatorio. (OBS-0033)
2. **Given** el formulario de creación de ticket, **When** el usuario ingresa un título que incluye uno o más emojis, **Then** el sistema rechaza el guardado y muestra un mensaje de validación indicando que los emojis no están permitidos; letras, números y puntuación común se aceptan sin restricción. (OBS-0034)

---

### User Story 4 - Retroalimentación clara al configurar reglas de SLA (Priority: P2)

Al crear o editar una configuración de SLA, el usuario recibe confirmación visual del guardado exitoso y mensajes de validación explícitos cuando un valor de tiempo está fuera del rango permitido, en vez de que el sistema lo autocorrija en silencio.

**Why this priority**: Afecta la confianza del administrador de SLA en la herramienta, pero no compromete el cálculo de SLA de tickets ya en curso (eso lo cubre la User Story 1).

**Independent Test**: Crear una configuración de SLA válida y verificar la confirmación; luego intentar guardar valores en 0, negativos y excesivamente altos, y verificar que cada caso muestra un mensaje de validación explícito.

**Acceptance Scenarios**:

1. **Given** el formulario de configuración de SLA con todos los campos válidos, **When** el usuario guarda, **Then** el sistema muestra una notificación de éxito. (OBS-0029)
2. **Given** un campo de tiempo del SLA, **When** el usuario ingresa `0` o un valor negativo, **Then** el sistema muestra un mensaje indicando el tiempo mínimo permitido en vez de reemplazar el valor silenciosamente. (OBS-0030)
3. **Given** un campo de tiempo del SLA, **When** el usuario ingresa un valor que excede el máximo permitido, **Then** el sistema muestra un mensaje de validación y no guarda el valor excesivo. (OBS-0031)

---

### User Story 5 - Visibilidad del estado del SLA y de la disponibilidad del recurso (Priority: P3)

Antes de que el SLA empiece a correr, el detalle del ticket muestra un estado que deja claro que el conteo aún no inició. El calendario de un recurso interno muestra su jornada laboral, feriados, ausencias y disponibilidad, no solo eventos personales.

**Why this priority**: Son mejoras de visibilidad/UX; no corrigen un cálculo incorrecto, sino que reducen la posibilidad de interpretación errónea.

**Independent Test**: Crear un ticket nuevo y verificar el estado visual del SLA antes de que inicie el conteo; abrir el calendario de un recurso interno y verificar que expone su jornada laboral y disponibilidad.

**Acceptance Scenarios**:

1. **Given** un ticket recién creado cuyo SLA aún no comienza a contabilizar, **When** se visualiza el componente de SLA, **Then** el estado mostrado indica claramente que el conteo no está en ejecución (diferenciado de un SLA activo). (OBS-0032)
2. **Given** el calendario de un recurso interno, **When** se consulta, **Then** se muestran su calendario laboral asignado, país, días/horario laboral, feriados aplicables, vacaciones/ausencias/permisos y disponibilidad, separados de eventos personales como el cumpleaños. (OBS-0037)

---

### User Story 6 - Regla de negocio para el registro de tiempo fuera del horario laboral (Priority: P2)

El sistema aplica una regla de negocio explícita y consistente cuando un recurso registra tiempo fuera del horario laboral configurado en su calendario, conservando siempre la fecha/hora real de inicio y fin del registro.

**Why this priority**: Tiene el mismo trasfondo de exactitud de tiempo/SLA que la User Story 1, pero requiere una decisión de negocio propia sobre cómo tratar el registro (no solo el cálculo del SLA), por lo que se mantiene como historia independiente.

**Independent Test**: Registrar tiempo en un ticket fuera del horario laboral configurado y verificar que el sistema aplica la regla definida (ver FR-020) de forma consistente con el SLA y el calendario, conservando la fecha/hora real del registro.

**Acceptance Scenarios**:

1. **Given** un recurso con horario laboral configurado, **When** registra tiempo fuera de ese horario, **Then** el sistema guarda el registro y lo clasifica/etiqueta como "tiempo fuera de jornada" (ver FR-020). (OBS-0036)
2. **Given** un registro de tiempo realizado cerca de la medianoche fuera de horario laboral, **When** se consulta el historial, **Then** la fecha asociada corresponde a la fecha/hora real de inicio de la actividad, no a una fecha desplazada por error de cálculo. (OBS-0036)

---

### Edge Cases

- ¿Qué ocurre si un ticket cambia de estado varias veces en un mismo día, cruzando repetidamente los límites del horario laboral (ej. entra y sale de "pausado")? El tiempo consumido acumulado debe seguir siendo exclusivamente tiempo laboral, sin importar cuántas transiciones ocurran.
- ¿Qué ocurre si el recurso asignado a un ticket no tiene calendario/horario laboral configurado en absoluto? El cálculo de SLA debe tener un comportamiento definido y consistente (no debe romperse ni contabilizar tiempo indefinido).
- ¿Cómo se comporta el sistema con tickets de clientes en distintos países/zonas horarias (calendarios por país ya soportados por specs 020/022) cuando el resolutor asignado está en otro país?
- ¿Qué pasa si dos solicitudes casi simultáneas —cerrar el ticket y registrar tiempo— llegan al mismo tiempo (condición de carrera)? El cierre debe prevalecer y bloquear el registro.
- ¿El título de un ticket con espacios especiales Unicode (no-break space, tabs) debe tratarse igual que espacios comunes para la validación de "solo espacios en blanco"?
- ¿La validación de caracteres del título (OBS-0034) aplica solo a tickets nuevos o también revalida tickets existentes con títulos ya guardados que no cumplen la política?
- ¿Se exige recálculo retroactivo del SLA de tickets ya cerrados/vencidos antes de este fix, o el fix aplica solo hacia adelante? (ver Assumptions)

## Requirements *(mandatory)*

### Functional Requirements

**Cálculo del SLA respecto al horario laboral (User Story 1)**

- **FR-001**: El sistema MUST contabilizar el tiempo de SLA únicamente dentro de los intervalos de horario laboral del calendario aplicable al recurso/proyecto del ticket, sin importar cuándo ocurre el evento que dispara el recálculo. (OBS-0038)
- **FR-002**: Al cambiar el estado de un ticket, el sistema MUST recalcular el tiempo consumido de SLA usando exclusivamente el tiempo laboral transcurrido, excluyendo tiempo fuera de horario y tiempo en que el SLA estuvo pausado. (OBS-0038)
- **FR-003**: Cuando un ticket se crea fuera del horario laboral configurado, el sistema MUST iniciar el conteo de SLA únicamente al comenzar el siguiente período laboral, conservando la fecha/hora real de creación. (OBS-0039)
- **FR-004**: El sistema MUST permitir crear y asignar tickets en cualquier momento, dentro o fuera del horario laboral configurado, sin bloquear la operación por ese motivo. (OBS-0040)
- **FR-005**: El sistema MUST registrar de forma distinguible y consultable en el historial del ticket: la hora de creación, la hora de asignación, el inicio efectivo del SLA y el inicio de la jornada laboral aplicable. (OBS-0040)
- **FR-006**: El sistema MUST NOT marcar un ticket como "Vencido" antes de que se haya consumido efectivamente, en tiempo laboral real, el tiempo límite de SLA configurado. (OBS-0038, OBS-0039)

**Registro de tiempo en tickets cerrados (User Story 2)**

- **FR-007**: Al cambiar un ticket a estado Cerrado, el sistema MUST detener automáticamente cualquier cronómetro de registro de tiempo activo sobre ese ticket, conservando el tiempo ya acumulado. (OBS-0035)
- **FR-008**: El sistema MUST NOT permitir iniciar un nuevo registro de tiempo (cronómetro o manual) sobre un ticket en estado Cerrado. (OBS-0035)
- **FR-009**: El sistema MUST informar al usuario, mediante un mensaje explícito, que el ticket está cerrado cuando intente registrar tiempo sobre él. (OBS-0035)
- **FR-010**: El cierre de un ticket MUST NOT afectar el registro de tiempo del recurso en otros tickets o tareas activos. (OBS-0035)

**Validación del título del ticket (User Story 3)**

- **FR-011**: El sistema MUST recortar espacios al inicio/fin del título y rechazar el guardado si el resultado queda vacío (título compuesto únicamente por espacios en blanco). (OBS-0033)
- **FR-012**: El sistema MUST mostrar un mensaje indicando que el título es obligatorio cuando la validación de FR-011 falle. (OBS-0033)
- **FR-013**: El sistema MUST permitir en el título del ticket letras (incl. acentos/ñ), números, espacios y signos de puntuación comunes, y MUST rechazar emojis/pictogramas, mostrando un mensaje de validación cuando se detecten. (OBS-0034)

**Retroalimentación en la configuración de SLA (User Story 4)**

- **FR-014**: El sistema MUST mostrar una notificación de confirmación cuando una configuración de SLA se guarda exitosamente. (OBS-0029)
- **FR-015**: El sistema MUST validar los campos de tiempo del SLA (contacto, diagnóstico, análisis, ejecución) antes de guardarlos; si el usuario ingresa un valor menor al mínimo permitido (1 minuto), MUST mostrar un mensaje indicando el motivo en vez de reemplazar el valor silenciosamente. (OBS-0030)
- **FR-016**: El sistema MUST validar un tiempo máximo de 15 días (21600 minutos) en cada campo de tiempo del SLA y mostrar un mensaje de validación cuando se supere, sin guardar el valor excesivo. (OBS-0031)

**Visibilidad de SLA y de disponibilidad del recurso (User Story 5)**

- **FR-017**: Antes de que el SLA comience a contabilizar tiempo, el sistema MUST mostrar un estado visualmente diferenciado que indique que el conteo aún no está en ejecución. (OBS-0032)
- **FR-018**: El sistema MUST mostrar en el calendario de un recurso interno: el calendario laboral asignado, el país, los días y horario laboral, los feriados aplicables, las vacaciones/ausencias/permisos, las excepciones de calendario y la disponibilidad — separados de eventos personales como el cumpleaños. (OBS-0037)
- **FR-019**: La disponibilidad expuesta en el calendario del recurso MUST poder ser utilizada por el Panel de Asignación para informar carga y disponibilidad real al asignar tickets/tareas. (OBS-0037)

**Registro de tiempo fuera del horario laboral (User Story 6)**

- **FR-020**: El sistema MUST permitir el registro de tiempo fuera del horario laboral configurado y MUST clasificarlo/etiquetarlo como "tiempo fuera de jornada" para que sea identificable en reportes y en el detalle del registro. (OBS-0036)
- **FR-021**: Independientemente de la regla elegida en FR-020, el sistema MUST conservar correctamente la fecha y hora real de inicio y fin del registro de tiempo, sin desplazarla al día siguiente por errores de cálculo de zona horaria. (OBS-0036)

**Trazabilidad con el framework UAT**

- **FR-022**: Al completar y verificar cada corrección, el desarrollador MUST actualizar el `Estado` de la observación correspondiente (OBS-0029 a OBS-0040) en `UAT/02_Backlog/BACKLOG.md` a `Lista para Validar`, siguiendo el flujo documentado en `UAT/CONVENTIONS.md`. `ITER-004.md` e `ITER-005.md` MUST NOT editarse retroactivamente.

### Key Entities *(include if feature involves data)*

- **Ticket**: registro de trabajo (Incidente/Requerimiento) con estado (Abierto, En Ejecución, Solicitud de información, Cerrado, etc.), título, fechas de creación/asignación, y una relación 1:1 con su contador de SLA.
- **SLA (regla y contador)**: configuración de tiempos límite por proyecto/prioridad (contacto, diagnóstico, análisis, ejecución) y el contador en tiempo real asociado a un ticket, que debe respetar el calendario laboral aplicable.
- **Registro de tiempo (work session)**: entrada de tiempo trabajado sobre un ticket/tarea, con inicio/fin, estado (activo/detenido) y el recurso que lo generó.
- **Calendario laboral / Recurso**: configuración de días/horario laboral, feriados, ausencias y excepciones asociada a un recurso o proyecto, usada tanto por el motor de SLA como por el Panel de Asignación.
- **Observación UAT**: entidad del framework `UAT/` (`OBS-XXXX`) con módulo, tipo, estado y criterios de aceptación — no es una entidad de la aplicación, pero es la unidad de trabajo y de trazabilidad de este feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100% de los casos de prueba de aceptación de OBS-0038/OBS-0039, el SLA recalculado tras un cambio de estado o tras la creación fuera de horario refleja únicamente el tiempo laboral real transcurrido (0 minutos de tiempo fuera de horario o en pausa contabilizados de más).
- **SC-002**: Ningún ticket de prueba aparece marcado como "Vencido" antes de consumir el tiempo límite de SLA configurado en tiempo laboral real, verificado en el 100% de los escenarios de las 12 observaciones.
- **SC-003**: 0% de los tickets cerrados en las pruebas permiten iniciar o continuar un registro de tiempo tras el cierre; el registro del recurso en otros tickets/tareas no se interrumpe en ningún caso.
- **SC-004**: 100% de los intentos de guardar un ticket con título vacío o compuesto solo por espacios son rechazados con un mensaje explicativo.
- **SC-005**: 100% de las configuraciones de SLA guardadas exitosamente muestran una confirmación visual, y 100% de los valores fuera de rango (mínimo o máximo) muestran un mensaje de validación en vez de autocorregirse en silencio.
- **SC-006**: El calendario de cualquier recurso interno con calendario asignado permite identificar su jornada laboral, feriados y disponibilidad sin salir de esa pantalla, verificado en el 100% de los recursos de prueba.
- **SC-007**: Las 12 observaciones "Abierta" del backlog (OBS-0029 a OBS-0040) quedan actualizadas a `Lista para Validar` en `UAT/02_Backlog/BACKLOG.md` al completar la implementación, sin alterar el contenido histórico de `ITER-004.md` ni `ITER-005.md`.

## Assumptions

- "Horario laboral configurado" se refiere al motor de disponibilidad/calendario ya implementado en los features 020 (Calendarios/Vacaciones/Disponibilidad) y 022 (Franjas Horarias/Calendario de Equipo/Motor de SLA Dinámico); este feature corrige su aplicación en los escenarios reportados, no reconstruye el motor de calendario.
- Las correcciones aplican hacia adelante (tickets y registros nuevos, y recálculos en vivo de tickets activos). No se exige un recálculo retroactivo masivo de SLA de tickets ya cerrados antes de esta corrección, salvo que el consultor UAT indique lo contrario durante el retest.
- Permitir crear/asignar tickets fuera de horario (OBS-0040, FR-004) no introduce restricciones nuevas de permisos de usuario; se mantiene el control de permisos ya existente para asignar tickets.
- El "responsable de validación" de este feature, siguiendo `UAT/CONVENTIONS.md`, es quien reportó las observaciones originales (Arely Pazmiño) u otro consultor UAT asignado; este feature no incluye la validación/retest en sí, solo deja el backlog en estado `Lista para Validar`.
- Las 12 observaciones se implementan y prueban en Docker local, consistente con el resto de features de este repositorio.
- Actualizar `BACKLOG.md` es responsabilidad de quien implementa (Desarrollador), no de quien especifica; se documenta aquí como requisito (FR-022) para que quede explícito en la definición de "hecho" del feature.
