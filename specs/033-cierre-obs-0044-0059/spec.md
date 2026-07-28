# Feature Specification: Cierre de OBS-0044–OBS-0059 (Backlog UAT ITER-008)

**Feature Branch**: `033-cierre-obs-0044-0059`

**Created**: 2026-07-28

**Status**: Draft

**Input**: User description: "Cierre de OBS-0044–OBS-0059 (Backlog UAT ITER-008, reportadas por Emilio Vargas — barrido E2E). 16 observaciones en estado Abierta: mensajes de error/éxito invisibles en login y cambios de estado (contexto `<App>` de antd v5), cronómetro que revienta con error para usuarios sin perfil de recurso, falso 'fecha futura' al finalizar el cronómetro por desfase de zona horaria, rótulo confuso del contador 'En progreso', Proyecto/Usuario-cliente obligatorios al crear un Ticket con Cliente y SLA auto-derivados del Proyecto, sugerencia de Skills requeridas vía relación Herramienta↔Proceso y permiso dedicado para editarlas, candidatos QM para Pre-Análisis por rol (no por tabla de recursos) con validación de rol vs. modo de asignación, confirmación explícita del nuevo estado del ticket, badge de prioridad con nombre legible, y visualización del resultado del SLA de la fase de cierre/ejecución (hoy solo se muestra el de Contacto)."

## Contexto

`UAT/02_Backlog/BACKLOG.md` es la única fuente de verdad del estado de cada observación de pruebas (ver `UAT/CONVENTIONS.md`). Al momento de escribir esta especificación, las observaciones en estado **Abierta** son las 16 siguientes, todas reportadas por Emilio Vargas durante el barrido E2E de `ITER-008`, y son las que este feature debe resolver:

| ID | Módulo/Pantalla | Tipo | Iteración origen |
|---|---|---|---|
| OBS-0044 | Inicio de sesión | Defecto | ITER-008 |
| OBS-0045 | Tickets > Nuevo Ticket | Mejora | ITER-008 |
| OBS-0046 | Tickets > Nuevo Ticket | Mejora | ITER-008 |
| OBS-0047 | Tickets > Skills requeridas | Mejora | ITER-008 |
| OBS-0048 | Tickets > Skills requeridas | Mejora | ITER-008 |
| OBS-0049 | Catálogos · Tickets (Herramienta/Proceso) | Mejora | ITER-008 |
| OBS-0050 | Tickets > Detalle del Ticket > Cronómetro | Defecto | ITER-008 |
| OBS-0051 | Tickets > Panel de contadores | Mejora | ITER-008 |
| OBS-0052 | Tickets > Asignación (Triage) | Defecto | ITER-008 |
| OBS-0053 | Tickets > Asignación (Triage) · FSM | Defecto | ITER-008 |
| OBS-0054 | Tickets > Detalle / Asignación (mensajería) | Mejora | ITER-008 |
| OBS-0055 | Tickets > Cronómetro (finalizar) | Defecto | ITER-008 |
| OBS-0056 | Tickets > Cambio de estado (comentario) | Defecto | ITER-008 |
| OBS-0057 | Tickets > Cambio de estado (comentario) | Mejora | ITER-008 |
| OBS-0058 | Tickets > Prioridad (badge) | Mejora | ITER-008 |
| OBS-0059 | Tickets > Detalle del Ticket > SLA | Defecto | ITER-008 |

El detalle completo de cada observación (descripción, causa raíz confirmada, pasos para reproducir, resultado esperado/actual y criterios de aceptación) está documentado en `UAT/01_Iterations/ITER-008/ITER-008.md`, que es inmutable — este feature no lo modifica.

Las observaciones en otros estados (OBS-0001 a OBS-0043, OBS-0060 a OBS-0063) quedan explícitamente **fuera de alcance** de este feature.

**Decisiones de producto ya tomadas** (por el dueño del producto, antes de esta especificación, dado que varias observaciones lo requerían explícitamente):

- OBS-0045/OBS-0046 aplican solo a la creación de **Tickets** desde **perfil interno**; el autoservicio (rol Usuario/cliente) y la creación de **Tareas** mantienen el comportamiento actual (campos opcionales, sin auto-relleno).
- OBS-0047/OBS-0048 se implementan juntas y dependen de OBS-0049: las skills se **sugieren** (no se imponen) a partir de la relación Herramienta↔Proceso, y la edición del campo se restringe a un permiso dedicado nuevo asignado solo a Coordinador (Admin/QM pasan a verlo en solo lectura).
- OBS-0049: la relación Herramienta↔Proceso es muchos-a-muchos, administrable desde Catálogos, y funciona como **guía** (sugiere/filtra) sin bloquear combinaciones no vinculadas ni en frontend ni en backend.
- OBS-0052/OBS-0053 se implementan juntas: los candidatos para "Pre-Análisis (QM)" se listan por **rol QM** (tabla de usuarios/roles), no por la tabla de recursos; se valida en backend el rol del asignado según el modo de asignación.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Los avisos de éxito/error se ven siempre en pantalla (Priority: P1)

Un usuario intenta iniciar sesión con credenciales inválidas, o intenta registrar un comentario vacío al cambiar el estado de un ticket. En ambos casos, el sistema ya decide mostrar un aviso, pero hoy ese aviso no llega a verse — la pantalla solo "parece refrescarse" o "no pasa nada", sin que el usuario entienda qué falló.

**Why this priority**: Sin retroalimentación visible, el usuario no puede saber si su acción falló, quedó pendiente o se perdió — esto afecta el flujo más básico de la aplicación (login) y una acción cotidiana (cambiar el estado de un ticket). Es la causa raíz común a tres observaciones distintas.

**Independent Test**: Intentar iniciar sesión con una contraseña incorrecta y verificar que aparece un aviso visible; luego, en el detalle de un ticket, intentar cambiar el estado dejando el comentario vacío y verificar que aparece un aviso visible indicando que el comentario es obligatorio.

**Acceptance Scenarios**:

1. **Given** la pantalla de inicio de sesión, **When** el usuario ingresa un usuario o contraseña incorrectos, **Then** aparece un aviso visible con el texto genérico "Usuario o contraseña incorrectos" (sin distinguir cuál de los dos falló), que permanece el tiempo suficiente para leerse, y el formulario conserva lo escrito. (OBS-0044)
2. **Given** un error de red o de servidor no disponible durante el login, **When** ocurre, **Then** se muestra un aviso diferenciado ("No se pudo conectar, intenta de nuevo") distinguible del de credenciales inválidas. (OBS-0044)
3. **Given** el detalle de un ticket en un estado no final, **When** el usuario intenta registrar un cambio de estado con el comentario vacío, **Then** aparece un aviso visible indicando que el comentario es obligatorio, y la acción no se ejecuta. (OBS-0056)
4. **Given** cualquier otro aviso ya existente en la aplicación que dependa del mismo mecanismo de mensajes (éxito/advertencia/error mostrados inline por un componente, no por el manejador global de errores), **When** se dispara, **Then** también se muestra visible, de forma consistente. (OBS-0044, OBS-0056)

---

### User Story 2 - Finalizar el cronómetro nunca falla por un desfase de zona horaria (Priority: P1)

Un resolutor inicia el cronómetro sobre un ticket durante su jornada laboral y lo finaliza por la tarde o la noche. Necesita que el registro de tiempo se guarde sin errores, sin importar la hora del día en que lo finalice.

**Why this priority**: Es un defecto bloqueante confirmado con datos reales — el registro por cronómetro (funcionalidad central de la app) deja de funcionar en una franja horaria de uso habitual (noche en Colombia), impidiendo cerrar el conteo de tiempo trabajado.

**Independent Test**: Con el reloj del sistema en una hora en la que la fecha UTC ya avanzó al día siguiente respecto a la hora local del servidor (después de las 19:00 en Bogotá), iniciar y finalizar el cronómetro sobre un ticket y verificar que el registro se guarda sin el error "fecha futura".

**Acceptance Scenarios**:

1. **Given** un cronómetro iniciado sobre un ticket, **When** el resolutor lo finaliza en cualquier hora del día (incluida la franja 19:00–23:59 hora Colombia, donde la fecha UTC ya avanzó), **Then** el registro de tiempo se guarda exitosamente, sin el error "No se puede registrar tiempo con fecha futura". (OBS-0055)
2. **Given** un recurso sin `calendar_country` configurado, **When** finaliza el cronómetro, **Then** la validación de fecha futura usa la misma referencia horaria con la que se calculó la fecha del registro (no una combinación inconsistente de zonas). (OBS-0055)

---

### User Story 3 - Un usuario sin perfil de recurso no ve errores de cronómetro al abrir un ticket (Priority: P1)

Un Administrador, Coordinador o QM (roles que no tienen un perfil de recurso asociado) abre el detalle de cualquier ticket para revisarlo, asignarlo o gestionarlo. No debe recibir ningún aviso de error relacionado con el cronómetro, ya que esa herramienta es personal de quien ejecuta el trabajo (el recurso/resolutor).

**Why this priority**: El error aparece en **cada apertura de ticket** para tres de los cuatro roles del sistema, sin que el usuario haya realizado ninguna acción — es un defecto de alta frecuencia que degrada la confianza en la aplicación y además genera un mensaje ambiguo que se confunde con un problema de skills.

**Independent Test**: Iniciar sesión como Admin, Coordinador o QM (usuarios sin recurso asociado) y abrir el detalle de cualquier ticket; verificar que no aparece ningún aviso de error, y que el cronómetro no se muestra como si estuviera disponible para esa cuenta.

**Acceptance Scenarios**:

1. **Given** un usuario sin recurso asociado (Admin, Coordinador o QM), **When** abre el detalle de cualquier ticket, **Then** no recibe ningún aviso de error al cargar la pantalla. (OBS-0050)
2. **Given** el mismo usuario, **When** observa la zona del cronómetro, **Then** el cronómetro no se muestra como utilizable (se oculta, o se muestra un estado informativo claro), sin generar peticiones que fallen de forma visible al usuario. (OBS-0050)
3. **Given** un usuario que sí tiene recurso asociado (resolutor), **When** abre el detalle de un ticket, **Then** el cronómetro sigue funcionando exactamente igual que hoy. (OBS-0050)
4. **Given** cualquier mensaje relacionado con la ausencia de skills del recurso en un ticket, **When** se muestra, **Then** su texto habla explícitamente de skills ("Este recurso no tiene skills asociadas") y no reutiliza el texto de "perfil de recurso no asociado". (OBS-0054)

---

### User Story 4 - El panel de asignación distingue candidatos por rol y valida el destino (Priority: P1)

Un coordinador realiza el triage de un ticket nuevo. Necesita poder ver y elegir usuarios con rol QM cuando el destino es "Pre-Análisis", y usuarios con rol Resolutor cuando el destino es "Asignar"; el sistema no debe permitir enviar un ticket a Pre-Análisis con un resolutor asignado, ni viceversa.

**Why this priority**: Hoy el flujo "Pre-Análisis (QM)" no tiene a nadie disponible para asignar (los QM no aparecen en la grilla), y además el sistema permite la combinación inversa incorrecta (resolutor enviado a Pre-Análisis) sin ninguna validación — ambos son defectos que rompen el ciclo de vida real del ticket definido para el rol QM.

**Independent Test**: Abrir la asignación de un ticket nuevo y verificar que el botón "Pre-Análisis (QM)" ofrece usuarios con rol QM como candidatos y permite asignarles el ticket; luego, intentar asignar a un resolutor con destino Pre-Análisis (o a un QM con destino "Asignar") y verificar que el sistema lo rechaza con un mensaje claro, sin cambiar el estado del ticket.

**Acceptance Scenarios**:

1. **Given** un ticket nuevo en asignación, **When** el coordinador selecciona el modo "Pre-Análisis (QM)", **Then** la grilla de candidatos muestra usuarios con rol QM (independientemente de si tienen o no un perfil de recurso registrado). (OBS-0052)
2. **Given** el mismo ticket, **When** el coordinador selecciona el modo "Asignar" (resolutor), **Then** la grilla de candidatos sigue mostrando resolutores, igual que hoy. (OBS-0052)
3. **Given** un intento de enviar el ticket a Pre-Análisis con un usuario que no tiene rol QM, **When** se procesa la solicitud (desde la interfaz o directamente contra la API), **Then** el sistema la rechaza con un error claro y el estado del ticket no cambia. (OBS-0053)
4. **Given** un intento de asignar como resolutor a un usuario que no tiene rol Resolutor, **When** se procesa la solicitud, **Then** el sistema la rechaza de la misma forma. (OBS-0053)

---

### User Story 5 - Todo Ticket nuevo queda vinculado a un Proyecto y a un contacto de cliente (Priority: P2)

Un usuario interno (Coordinador u otro perfil que cree tickets) completa el formulario de "Nuevo Ticket". Necesita que el sistema le exija seleccionar el Proyecto y el Usuario/cliente (contacto solicitante), y que al elegir el Proyecto el Cliente y el nivel de servicio (SLA) aplicable se completen automáticamente, para no tener que elegir el cliente por separado ni quedarse sin saber qué SLA rige el ticket.

**Why this priority**: Evita tickets huérfanos (sin proyecto ni contacto asociado), que son difíciles de reportar, agrupar o facturar; es una mejora de integridad de datos hacia adelante, sin urgencia operativa inmediata como los defectos de P1.

**Independent Test**: Desde el perfil interno, intentar crear un ticket sin seleccionar Proyecto o sin seleccionar Usuario/cliente y verificar que el sistema lo impide; luego, seleccionar un Proyecto y verificar que el Cliente se completa solo (en modo lectura) y que se muestra el nivel de servicio (SLA) que aplicará.

**Acceptance Scenarios**:

1. **Given** el formulario de "Nuevo Ticket" en perfil interno, **When** el usuario intenta guardar sin seleccionar Proyecto, **Then** el sistema lo impide, tanto en el formulario como si se intenta directamente contra la API. (OBS-0045)
2. **Given** el mismo formulario, **When** el usuario intenta guardar sin seleccionar Usuario/cliente, **Then** el sistema lo impide de la misma forma. (OBS-0045)
3. **Given** el formulario de "Nuevo Ticket" en perfil interno, **When** el usuario selecciona un Proyecto, **Then** el campo Cliente se completa automáticamente con el cliente dueño de ese proyecto, en modo solo lectura (sin que el usuario deba elegirlo). (OBS-0046)
4. **Given** el mismo formulario, **When** ya hay un Proyecto seleccionado, **Then** se muestra el nivel de servicio (SLA) que aplicará al ticket, derivado de la regla configurada para ese proyecto/cliente. (OBS-0046)
5. **Given** un Proyecto sin ningún contacto de cliente cargado, **When** el usuario lo selecciona al crear un ticket, **Then** el sistema muestra un mensaje claro explicando la situación, sin dejar al usuario en un formulario bloqueado sin explicación. (OBS-0045)
6. **Given** el formulario de autoservicio (rol Usuario/cliente) o el formulario de creación de Tareas, **When** se crean sin Proyecto o sin Usuario/cliente, **Then** el sistema los sigue permitiendo igual que hoy (esta obligatoriedad no aplica a esos dos flujos). (OBS-0045, OBS-0046)

---

### User Story 6 - El selector de Skills requeridas sugiere y se edita solo por quien hace el triage (Priority: P2)

Un coordinador clasifica un ticket nuevo eligiendo Herramienta y Proceso, y necesita que el sistema le sugiera las Skills requeridas más relevantes en vez de tener que revisar todo el catálogo manualmente. Además, ese campo debe poder editarlo solo quien hace el triage (Coordinador); los demás perfiles que acceden al ticket lo ven en solo lectura.

**Why this priority**: Mejora la calidad y velocidad de la clasificación de tickets, con impacto indirecto (no bloqueante) en la calidad de la asignación posterior; depende de que primero exista la relación Herramienta↔Proceso (OBS-0049).

**Independent Test**: Crear o editar un ticket clasificándolo con una Herramienta y un Proceso vinculados entre sí en el catálogo, y verificar que el selector de Skills requeridas ofrece sugerencias relacionadas, preseleccionables pero no forzadas; luego, verificar que un usuario con rol QM o Admin ve las Skills requeridas en solo lectura, mientras que un Coordinador puede editarlas.

**Acceptance Scenarios**:

1. **Given** el catálogo de Herramientas y Procesos, **When** un administrador de catálogos configura la relación entre una Herramienta y los Procesos que soporta, **Then** esa relación queda guardada y es administrable desde Catálogos. (OBS-0049)
2. **Given** un ticket en el que se elige una Herramienta con procesos vinculados, **When** el usuario abre el selector de Proceso, **Then** los procesos vinculados aparecen sugeridos/priorizados, sin impedir elegir cualquier otro proceso del catálogo (incluida la opción "Otro"). (OBS-0049)
3. **Given** un ticket clasificado con Herramienta y/o Proceso, **When** el usuario abre el selector de Skills requeridas, **Then** se muestran skills sugeridas relacionadas con esa clasificación, marcadas como sugerencia y no impuestas — el usuario puede aceptarlas, quitarlas, o elegir cualquier otra skill del catálogo. (OBS-0047)
4. **Given** un ticket sin Herramienta/Proceso clasificados aún, **When** el usuario abre el selector de Skills requeridas, **Then** puede seguir eligiendo manualmente sobre todo el catálogo, igual que hoy. (OBS-0047)
5. **Given** un usuario con rol Coordinador, **When** abre el detalle de un ticket, **Then** puede editar el campo Skills requeridas. (OBS-0048)
6. **Given** un usuario con rol Admin o QM (sin el permiso dedicado de edición de skills), **When** abre el detalle del mismo ticket, **Then** ve las Skills requeridas en modo solo lectura, sin poder modificarlas pese a tener permiso general de edición de tickets. (OBS-0048)

---

### User Story 7 - El cambio de estado de un ticket se confirma con el nuevo estado (Priority: P2)

Un usuario cambia el estado de un ticket mediante un comentario tipificado. Necesita ver una confirmación explícita de que el estado cambió y a qué estado, en vez de un mensaje genérico sobre el comentario.

**Why this priority**: Es una mejora de claridad sobre una acción frecuente del ciclo de vida del ticket; depende de que los avisos ya se vean en pantalla (User Story 1), de otro modo la confirmación seguiría sin notarse.

**Independent Test**: Cambiar el estado de un ticket agregando un comentario que dispare la transición, y verificar que el mensaje de éxito menciona explícitamente el nuevo estado; luego, agregar un comentario que no dispare ningún cambio de estado y verificar que el mensaje sigue siendo el de "Comentario registrado".

**Acceptance Scenarios**:

1. **Given** un ticket en un estado no final, **When** el usuario registra un comentario que dispara una transición de estado, **Then** el mensaje de éxito confirma explícitamente el nuevo estado del ticket (por ejemplo, "Ticket movido a 'En Ejecución'"). (OBS-0057)
2. **Given** un ticket, **When** el usuario registra un comentario que no dispara ningún cambio de estado, **Then** el mensaje de éxito sigue siendo el de confirmación de comentario ("Comentario registrado"), sin mencionar un cambio de estado que no ocurrió. (OBS-0057)
3. **Given** un cambio de estado exitoso, **When** se completa, **Then** el tag de estado visible del ticket y su historial de estados se actualizan de inmediato, de forma perceptible para el usuario. (OBS-0057)

---

### User Story 8 - El resultado del SLA de la fase de cierre es visible junto al de Contacto (Priority: P2)

Un usuario revisa el SLA de un ticket ya cerrado o resuelto. Necesita ver si se cumplió o venció el SLA de la fase de diagnóstico/análisis/ejecución (la segunda fase), no solo el de la fase de Contacto (la primera).

**Why this priority**: Es un defecto de visibilidad con causa raíz en la falta de un dato persistido (no solo un problema de interfaz), pero no bloquea ninguna operación del ciclo de vida del ticket — el ticket puede cerrarse igual sin esta información visible.

**Independent Test**: Llevar un ticket con SLA configurado por su ciclo completo hasta Cerrado, y verificar en la pestaña de SLA que se muestra el resultado (cumplido/vencido) de ambas fases: Contacto y Ejecución/Cierre, cada una con su tiempo consumido.

**Acceptance Scenarios**:

1. **Given** un ticket cerrado con SLA configurado, **When** el usuario abre la pestaña/sección de SLA, **Then** se muestra el resultado (cumplido/vencido) de la fase de Contacto y, adicionalmente, el de la fase de Ejecución/Cierre. (OBS-0059)
2. **Given** el mismo ticket, **When** se revisa cada fase, **Then** se muestra el tiempo consumido frente al límite configurado para esa fase. (OBS-0059)
3. **Given** el indicador general de cumplimiento del SLA del ticket, **When** alguna de las dos fases venció, **Then** el indicador general lo refleja (no se calcula considerando solo la fase de Contacto). (OBS-0059)

---

### User Story 9 - Los contadores y badges del listado de tickets son legibles sin ambigüedad (Priority: P3)

Un usuario revisa el listado de tickets. El contador "En progreso" debe dejar claro que agrupa varios estados del ciclo de vida (no es un estado en sí), y la prioridad de cada ticket debe mostrarse con su nombre legible ("Crítica/Alta/Media/Baja") en vez de un código corto ("P1"–"P4"), de forma consistente con el filtro y el formulario.

**Why this priority**: Ambos son ajustes de claridad visual sin impacto funcional ni de datos — la prioridad definida no cambian, solo su representación.

**Independent Test**: Abrir el listado de tickets y verificar que el contador "En progreso" comunica visualmente (rótulo, subtítulo o tooltip) que agrupa varios estados; verificar también que la columna/badge de prioridad muestra el nombre legible, igual que el filtro y el formulario de creación.

**Acceptance Scenarios**:

1. **Given** el panel de contadores del listado de tickets, **When** el usuario ve el contador que agrupa los estados intermedios, **Then** su rótulo, subtítulo o un tooltip dejan explícito que agrupa varios estados del ciclo de vida (no es un estado único). (OBS-0051)
2. **Given** el listado de tickets, **When** el usuario observa la prioridad de cualquier ticket, **Then** se muestra con su nombre legible (Crítica/Alta/Media/Baja), igual que en el filtro y el formulario de creación. (OBS-0058)

---

### Edge Cases

- ¿Qué pasa si el backend no está disponible durante el login (error de red)? Debe verse un aviso diferenciado del de credenciales inválidas ("No se pudo conectar, intenta de nuevo"). (OBS-0044)
- ¿Qué ocurre con tickets ya existentes creados sin Proyecto o sin Usuario/cliente antes de esta corrección? No se migran ni se bloquean retroactivamente; la obligatoriedad aplica solo a la creación de tickets nuevos desde perfil interno a partir de esta corrección. (OBS-0045)
- ¿Qué pasa si un Proyecto tiene más de un contacto de cliente cargado? El usuario elige entre ellos normalmente, igual que hoy; la obligatoriedad solo exige que haya al menos uno seleccionable. (OBS-0045)
- ¿Qué pasa si se intenta clasificar un ticket con una combinación Herramienta/Proceso no vinculada en el catálogo? Se permite igual (la relación es una guía, no una restricción dura); no se bloquea ni se advierte con un error duro. (OBS-0049)
- ¿Qué pasa con los tickets o resolutores existentes que ya tengan Skills requeridas asignadas antes de este cambio? Se conservan sin alteración; el cambio solo afecta la sugerencia al momento de editar y el permiso de quién puede editar de ahora en adelante. (OBS-0047, OBS-0048)
- ¿Qué pasa si un usuario QM también tiene, en el futuro, un perfil de recurso propio (por ejemplo, si además resuelve tickets)? Debe poder seguir apareciendo como candidato QM por su rol, sin que la existencia de un perfil de recurso lo excluya. (OBS-0052)
- ¿Qué pasa si se intenta asignar un ticket a un usuario que tiene más de un rol (por ejemplo, QM y Resolutor)? El sistema permite el modo cuyo rol coincide con el asignado; no se restringe por tener roles adicionales. (OBS-0053)
- ¿Qué pasa con un ticket ya en Pre-Análisis con un resolutor asignado antes de esta corrección (estado inconsistente heredado)? No se revierte automáticamente; la validación aplica hacia adelante, a nuevos intentos de asignación. (OBS-0053)
- ¿Qué pasa con tickets ya cerrados antes de que exista el campo de resultado de la fase de ejecución/cierre? Pueden no tener ese dato disponible retroactivamente si no puede derivarse de información ya registrada; se documenta como limitación conocida en la fase de planificación técnica, sin bloquear el cierre de esta observación para tickets nuevos. (OBS-0059)
- ¿Qué pasa si el usuario cambia el estado del ticket sin escribir comentario en un estado que sí lo permite (por ejemplo, transiciones que no requieren comentario, si las hubiera)? Esta observación no cambia qué transiciones requieren comentario, solo asegura que la validación existente sea visible. (OBS-0056)

## Requirements *(mandatory)*

### Functional Requirements

**Visibilidad de avisos de éxito/error (User Story 1)**

- **FR-001**: El sistema MUST mostrar un aviso visible con el texto genérico "Usuario o contraseña incorrectos" cuando el login falle por credenciales inválidas, sin distinguir cuál de los dos datos falló. (OBS-0044)
- **FR-002**: El sistema MUST mostrar un aviso diferenciado cuando el login falle por un error de red o de servidor no disponible. (OBS-0044)
- **FR-003**: El formulario de login MUST conservar los datos ingresados tras un intento fallido, permitiendo reintentar sin volver a escribirlos. (OBS-0044)
- **FR-004**: El sistema MUST mostrar un aviso visible cuando se intente registrar un cambio de estado con el comentario vacío, y MUST bloquear la acción en ese caso. (OBS-0056)
- **FR-005**: Todo aviso de éxito/advertencia/error disparado directamente por un componente de la interfaz (no por el manejador global de errores) MUST renderizarse visible al usuario, de forma consistente en toda la aplicación. (OBS-0044, OBS-0056)

**Cronómetro (User Stories 2 y 3)**

- **FR-006**: El sistema MUST permitir finalizar el cronómetro y guardar el registro de tiempo correctamente sin importar la hora del día, incluida la franja en la que la fecha UTC ya haya avanzado respecto a la fecha local. (OBS-0055)
- **FR-007**: La validación de "fecha futura" al finalizar el cronómetro MUST comparar la fecha del registro contra una referencia horaria consistente con la usada para calcularla (no una combinación de zonas horarias distintas). (OBS-0055)
- **FR-008**: El sistema MUST NOT mostrar ningún aviso de error al abrir el detalle de un ticket para un usuario que no tiene un perfil de recurso asociado. (OBS-0050)
- **FR-009**: El cronómetro MUST ocultarse o mostrarse en un estado informativo (no utilizable) para usuarios sin perfil de recurso asociado, sin afectar su disponibilidad para usuarios que sí lo tienen. (OBS-0050)
- **FR-010**: Cualquier mensaje relacionado con la falta de skills de un recurso en el contexto de un ticket MUST usar un texto explícito sobre skills, y MUST NOT reutilizar el texto de "perfil de recurso no asociado". (OBS-0054)

**Asignación y roles (User Story 4)**

- **FR-011**: El modo de asignación "Pre-Análisis (QM)" MUST listar como candidatos a los usuarios con rol QM, sin requerir que tengan un perfil de recurso registrado. (OBS-0052)
- **FR-012**: El modo de asignación "Asignar" (resolutor) MUST seguir listando como candidatos a los usuarios con perfil de recurso, igual que hoy. (OBS-0052)
- **FR-013**: El sistema MUST validar, al procesar una asignación, que el usuario destino tenga el rol correspondiente al modo solicitado (QM para Pre-Análisis, Resolutor para Asignar), rechazando la operación con un error tipado si no coincide, sin alterar el estado del ticket. (OBS-0053)
- **FR-014**: Esta validación de rol MUST aplicarse tanto si la solicitud se origina desde la interfaz como si se envía directamente a la API. (OBS-0053)

**Creación de tickets (User Story 5)**

- **FR-015**: Al crear un Ticket (no una Tarea) desde perfil interno, el sistema MUST exigir la selección de Proyecto y de Usuario/cliente, rechazando el guardado si falta alguno de los dos, tanto en el formulario como en el backend. (OBS-0045)
- **FR-016**: Al seleccionar un Proyecto en el formulario de "Nuevo Ticket" (perfil interno), el sistema MUST completar automáticamente el Cliente asociado, en modo solo lectura, sin requerir selección manual. (OBS-0046)
- **FR-017**: Al haber un Proyecto seleccionado, el sistema MUST mostrar el nivel de servicio (SLA) que aplicará al ticket, derivado de la regla configurada para ese proyecto/cliente. (OBS-0046)
- **FR-018**: Si el Proyecto seleccionado no tiene ningún contacto de cliente cargado, el sistema MUST mostrar un mensaje claro que explique la situación al usuario, sin dejarlo en un formulario bloqueado sin explicación. (OBS-0045)
- **FR-019**: La obligatoriedad de Proyecto/Usuario-cliente y el auto-relleno de Cliente/SLA MUST NOT aplicar al flujo de autoservicio (rol Usuario/cliente) ni a la creación de Tareas, que conservan su comportamiento actual. (OBS-0045, OBS-0046)

**Skills requeridas y catálogo Herramienta↔Proceso (User Story 6)**

- **FR-020**: El sistema MUST permitir administrar, desde Catálogos, una relación muchos-a-muchos entre Herramientas y Procesos. (OBS-0049)
- **FR-021**: Al elegir una Herramienta en la clasificación de un ticket, el selector de Proceso MUST sugerir/priorizar los procesos vinculados a esa herramienta, sin impedir elegir cualquier otro proceso del catálogo (incluida una opción equivalente a "Otro"). (OBS-0049)
- **FR-022**: El selector de Skills requeridas MUST ofrecer sugerencias de skills derivadas de la Herramienta y/o Proceso clasificados en el ticket, quedando dichas sugerencias preseleccionables y no impuestas — el usuario conserva la posibilidad de elegir cualquier skill del catálogo. (OBS-0047)
- **FR-023**: La edición del campo Skills requeridas MUST restringirse a un permiso dedicado, asignado únicamente al rol Coordinador; los roles Admin y QM MUST ver el campo en modo solo lectura pese a conservar el permiso general de edición de tickets. (OBS-0048)

**Confirmación de cambio de estado (User Story 7)**

- **FR-024**: Cuando un comentario dispare una transición de estado del ticket, el mensaje de éxito MUST confirmar explícitamente el nuevo estado alcanzado. (OBS-0057)
- **FR-025**: Cuando un comentario no dispare ninguna transición de estado, el mensaje de éxito MUST seguir siendo el de confirmación de comentario registrado, sin mencionar un cambio de estado. (OBS-0057)

**Visualización del SLA de cierre (User Story 8)**

- **FR-026**: El sistema MUST calcular y persistir el resultado (cumplido/vencido) y el tiempo consumido de la fase de Ejecución/Cierre del SLA, de forma análoga a como ya lo hace para la fase de Contacto. (OBS-0059)
- **FR-027**: El detalle de SLA de un ticket MUST mostrar el resultado y tiempo consumido de ambas fases (Contacto y Ejecución/Cierre) cuando estén disponibles. (OBS-0059)
- **FR-028**: El indicador general de cumplimiento del SLA de un ticket MUST considerar el resultado de ambas fases, no solo el de Contacto. (OBS-0059)

**Legibilidad de contadores y badges (User Story 9)**

- **FR-029**: El contador que agrupa varios estados intermedios del ciclo de vida del ticket MUST comunicar visualmente (en su rótulo, subtítulo o mediante un tooltip) que representa una agrupación de estados, no un estado único. (OBS-0051)
- **FR-030**: La prioridad de un ticket MUST mostrarse con su nombre legible (Crítica/Alta/Media/Baja) en el listado, de forma consistente con el filtro y el formulario de creación. (OBS-0058)

**Trazabilidad con el framework UAT**

- **FR-031**: Al completar y validar cada corrección, el desarrollador MUST actualizar el `Estado` de la observación correspondiente (OBS-0044 a OBS-0059) en `UAT/02_Backlog/BACKLOG.md` a `Lista para Validar`, siguiendo el flujo documentado en `UAT/CONVENTIONS.md`. `ITER-008.md` MUST NOT editarse retroactivamente en su contenido narrativo.

### Key Entities *(include if feature involves data)*

- **Ticket**: registro de trabajo (Incidente/Requerimiento); gana la obligatoriedad de Proyecto y Usuario/cliente al crearse desde perfil interno (OBS-0045), y el auto-relleno de Cliente/SLA (OBS-0046). Su SLA gana el resultado persistido de la fase de Ejecución/Cierre (OBS-0059).
- **Skills requeridas**: conjunto de skills asociadas a un ticket para el matching de asignación (spec 011); gana sugerencias derivadas de Herramienta/Proceso (OBS-0047) y un permiso de edición dedicado (OBS-0048).
- **Herramienta / Proceso**: catálogos hoy independientes; ganan una relación administrable muchos-a-muchos (OBS-0049), habilitadora de la sugerencia de skills.
- **Recurso (Resource) / Usuario (User) / Rol**: el recurso sigue siendo el perfil operativo de quien registra tiempo y aparece en la grilla de asignación como resolutor; el rol (ya existente en el sistema de permisos) se usa como origen alternativo de candidatos para el modo "Pre-Análisis (QM)", sin requerir que el usuario QM tenga un perfil de recurso (OBS-0052, OBS-0053).
- **Cronómetro (Work Session en curso)**: mecanismo de registro de tiempo activo sobre un ticket; su disponibilidad pasa a depender explícitamente de si el usuario tiene un perfil de recurso asociado (OBS-0050), y su validación de fecha se corrige para no depender de una zona horaria distinta a la usada al calcular el registro (OBS-0055).
- **SLA del Ticket**: ya modela el resultado de la fase de Contacto; gana el resultado equivalente de la fase de Ejecución/Cierre (OBS-0059).
- **Observación UAT**: entidad del framework `UAT/` (`OBS-XXXX`) con módulo, tipo, estado y criterios de aceptación — unidad de trabajo y trazabilidad de este feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100% de los intentos de prueba de login con credenciales inválidas y de cambio de estado con comentario vacío, el usuario ve un aviso visible explicando lo ocurrido.
- **SC-002**: En el 100% de las pruebas de finalizar el cronómetro en cualquier franja horaria del día (incluida la nocturna en Colombia), el registro se guarda sin el error de "fecha futura".
- **SC-003**: En el 100% de las aperturas de ticket por un usuario sin perfil de recurso asociado, no aparece ningún aviso de error relacionado con el cronómetro.
- **SC-004**: En el 100% de las pruebas de asignación a "Pre-Análisis", solo se puede seleccionar y confirmar un usuario con rol QM; en el 100% de los intentos de combinación de rol/modo incorrecta, el sistema los rechaza sin cambiar el estado del ticket.
- **SC-005**: En el 100% de los tickets nuevos creados desde perfil interno, quedan vinculados a un Proyecto y a un Usuario/cliente, con el Cliente y el SLA mostrados automáticamente al elegir el Proyecto.
- **SC-006**: En el 100% de los tickets clasificados con Herramienta y Proceso vinculados en el catálogo, el selector de Skills requeridas ofrece sugerencias relacionadas.
- **SC-007**: En el 100% de los tickets cerrados con SLA configurado, el detalle de SLA muestra el resultado de ambas fases (Contacto y Ejecución/Cierre).
- **SC-008**: Las 16 observaciones "Abierta" del backlog (OBS-0044 a OBS-0059) quedan actualizadas a `Lista para Validar` en `UAT/02_Backlog/BACKLOG.md` al completar la implementación, sin alterar el contenido narrativo histórico de `ITER-008.md`.

## Assumptions

- El problema de avisos invisibles (OBS-0044, OBS-0056, OBS-0057) tiene una causa raíz técnica común (mensajes estáticos de la librería de UI sin el contexto de aplicación que los renderiza); corregir esa causa común resuelve las tres observaciones a la vez, sin requerir un mecanismo distinto por pantalla.
- El desfase horario de OBS-0055 se corrige unificando la referencia horaria de la validación, sin necesidad de exigir que todo recurso tenga configurado un país de calendario (`calendar_country`) como precondición — el comportamiento debe ser correcto incluso cuando ese dato falta.
- OBS-0052/OBS-0053 no requieren dar de alta un perfil de recurso a los usuarios QM; el origen de los candidatos QM es el sistema de roles/usuarios ya existente.
- OBS-0047/OBS-0048 dependen de que OBS-0049 (relación Herramienta↔Proceso) se implemente primero o en conjunto, ya que la sugerencia de skills se deriva de esa relación.
- La obligatoriedad de Proyecto/Usuario-cliente (OBS-0045/OBS-0046) no aplica retroactivamente a tickets ya existentes ni a Tareas ni al autoservicio; es un cambio hacia adelante, solo para Tickets creados desde perfil interno.
- El permiso dedicado de edición de Skills requeridas (OBS-0048) es nuevo y se asigna únicamente al rol Coordinador en esta iteración; no se reutiliza el permiso `tickets:assign` para evitar afectar otros flujos que dependan de él.
- La persistencia del resultado de la fase de Ejecución/Cierre del SLA (OBS-0059) aplica hacia adelante; tickets ya cerrados antes de este cambio pueden no tener ese dato disponible retroactivamente si no puede derivarse de información ya registrada.
- Las 16 observaciones se implementan y prueban en Docker local, consistente con el resto de features de este repositorio.
- El "responsable de validación" de este feature, siguiendo `UAT/CONVENTIONS.md`, es quien reportó las observaciones originales (Emilio Vargas) u otro consultor UAT asignado; este feature no incluye la validación/retest en sí, solo deja el backlog en estado `Lista para Validar`.
