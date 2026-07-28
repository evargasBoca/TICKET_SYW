---
id: ITER-008
fecha: 2026-07-26
version_probada: "`ce5eb8b` (merge PR #34 — spec 029 seed usuarios/roles/skills, sobre backlog UAT cerrado spec 028)"
entorno: Docker Compose (sywork_db:5432, sywork_backend:5000, sywork_frontend:5173, sywork_redis, sywork_worker)
responsable_sesion: Emilio Vargas
alcance: "Barrido E2E (end-to-end) del ciclo de vida completo cruzando los 4 roles: creación de usuarios/roles → cliente → proyecto → usuario cliente → SLA → ticket → asignación (carga/skills/reasignación) → pre-análisis (QM) → gestión del ticket por estados (Resolutor) → validación de SLA → registro de tiempos (horario laboral)"
estado_iteracion: En curso
---

# ITER-008 — Iteración de pruebas (flujo E2E)

## Objetivo de la iteración

Validar la aplicación como un **flujo end-to-end encadenado**, no como pantallas aisladas: se ejecuta el ciclo de vida completo de un ticket desde la creación de los usuarios que lo operan hasta el registro de tiempos y la validación del SLA, pasando por cada rol (Coordinador, QM, Resolutor) en el orden real de trabajo.

Este barrido cubre además la **revalidación oportunista** de observaciones ya corregidas (`OBS-0013`…`OBS-0028`, estado "Lista para Validar" en ITER-003): al pasar por cada pantalla ya reportada (Clientes, Proyectos, Equipo, Roles, Tickets), se verifica de paso si la corrección quedó bien. Los cierres confirmados se marcan en `BACKLOG.md` (Verificada / Reabierta).

Complementa —sin duplicar— las iteraciones de Arely Pazmiño (ITER-002, ITER-004, ITER-005), enfocadas en pantallas puntuales y en el cálculo del SLA. Aquí el foco es la **continuidad del flujo** y las zonas nuevas menos probadas: validación de carga y skills en la asignación, reasignación, pausa del SLA en "Pendiente de usuario", y registro de tiempo fuera de horario.

> **Alcance de ejecución — perfil usado**: toda la iteración se ejecuta desde el **perfil Administrador**. Esto valida la **funcionalidad y el encadenamiento** de cada paso del ciclo (Admin tiene todos los permisos, por lo que puede operar como Coordinador/QM/Resolutor). **No** cubre el **enforcement de permisos por rol** (que un Resolutor solo vea sus tickets, que solo QM haga pre-análisis, que el Encargado quede restringido a su cliente, etc.) — esa validación de RBAC queda fuera del alcance de ITER-008 y se recomienda una iteración dedicada. En el guion, la anotación "(Coordinador)", "(QM)", "(Resolutor)" indica el **rol de negocio dueño del paso** en el flujo real, no el perfil con el que se ejecuta aquí.

## Guion E2E (checklist de ejecución)

> Recorrido ordenado. Cada paso que falle o sugiera mejora → se registra como observación `OBS-XXXX` en las secciones de abajo. Los pasos sin problema se marcan `[x]` sin generar OBS.

### A. Preparación de usuarios internos (Admin)
- [ ] Crear usuarios con sus respectivos roles (perfiles: Camilo, Juan Pablo)
- [ ] Verificar que se comunica/entrega usuario y contraseña creados al equipo interno (Camilo, Juan Pablo)

### B. Maestros y configuración (Coordinador)
- [ ] Crear cliente
- [ ] Crear proyecto (asociado al cliente)
- [ ] Crear usuario cliente (Encargado)
- [ ] Crear configuración de SLA
- [ ] Crear ticket nuevo

### C. Asignación del ticket (Coordinador)
- [ ] Asignar el ticket
  - [ ] Validación de carga de trabajo (el panel refleja la carga del resolutor)
  - [ ] Validación de skills (sugerencias por skills requeridas del ticket)
  - [ ] Reasignación de tickets (reasignar a otro resolutor y verificar historial)

### D. Pre-análisis (QM)
- [ ] Ejecutar el pre-análisis del ticket como QM

### E. Gestión del ticket por estados (Resolutor)
- [ ] Contacto
- [ ] Análisis (En Análisis)
- [ ] En ejecución
- [ ] Pendiente de usuario → **verificar que detiene/pausa el SLA**
- [ ] En pruebas
- [ ] Resuelto
- [ ] Cerrado

### F. Validación de SLA
- [ ] El SLA cuenta solo dentro del horario laboral configurado
- [ ] La pausa en "Pendiente de usuario" se refleja correctamente en el tiempo restante
- [ ] El estado inicial del SLA (fase Contacto desde la creación) se visualiza bien

### G. Registro de tiempos (Resolutor)
- [ ] Registrar tiempo sobre el ticket dentro del horario laboral
- [ ] Validación de tiempos fuera de horario (comportamiento esperado según calendario del recurso)

## Resumen de observaciones

| ID | Módulo/Pantalla | Tipo | Estado | Reportado por |
|---|---|---|---|---|
| OBS-0044 | Inicio de sesión | Defecto | Abierta | Emilio Vargas |
| OBS-0045 | Tickets > Nuevo Ticket | Mejora | Abierta | Emilio Vargas |
| OBS-0046 | Tickets > Nuevo Ticket | Mejora | Abierta | Emilio Vargas |
| OBS-0047 | Tickets > Skills requeridas | Mejora | Abierta | Emilio Vargas |
| OBS-0048 | Tickets > Skills requeridas | Mejora | Abierta | Emilio Vargas |
| OBS-0049 | Catálogos · Tickets (Herramienta/Proceso) | Mejora | Abierta | Emilio Vargas |
| OBS-0050 | Tickets > Detalle del Ticket > Cronómetro | Defecto | Abierta | Emilio Vargas |
| OBS-0051 | Tickets > Panel de contadores | Mejora | Abierta | Emilio Vargas |
| OBS-0052 | Tickets > Asignación (Triage) | Defecto | Abierta | Emilio Vargas |
| OBS-0053 | Tickets > Asignación (Triage) · FSM | Defecto | Abierta | Emilio Vargas |
| OBS-0054 | Tickets > Detalle / Asignación (mensajería) | Mejora | Abierta | Emilio Vargas |
| OBS-0055 | Tickets > Cronómetro (finalizar) | Defecto | Abierta | Emilio Vargas |
| OBS-0056 | Tickets > Cambio de estado (comentario) | Defecto | Abierta | Emilio Vargas |
| OBS-0057 | Tickets > Cambio de estado (comentario) | Mejora | Abierta | Emilio Vargas |
| OBS-0058 | Tickets > Prioridad (badge) | Mejora | Abierta | Emilio Vargas |
| OBS-0059 | Tickets > Detalle del Ticket > SLA | Defecto | Abierta | Emilio Vargas |

## Detalle de observaciones

<!--
Copiar este bloque por cada observación nueva (siguiente ID disponible: OBS-0044).
Ver formato completo en ../../CONVENTIONS.md

### OBS-XXXX — <título corto y descriptivo>

- **Módulo/Pantalla:**
- **Tipo:** Defecto | Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**

**Pasos para reproducir** (solo Defecto)
1.

**Resultado esperado / Situación actual**

**Resultado actual / Propuesta de mejora**

**Criterios de aceptación**
- [ ]

**Evidencia**
![](images/OBS-XXXX-01.png)
-->

### OBS-0044 — Al fallar el inicio de sesión no se muestra ningún mensaje (la página solo parece refrescarse)

- **Módulo/Pantalla:** Inicio de sesión
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Al intentar iniciar sesión con un usuario o contraseña incorrectos, la pantalla no informa el error: no aparece ningún aviso visible y la página parece únicamente refrescarse, dejando al usuario sin saber si falló la credencial, si el servidor no respondió, o si debe reintentar.

Nota técnica (para el desarrollador): el código **ya contempla** mostrar un aviso genérico — [`LoginPage.tsx:46-48`](frontend/src/pages/LoginPage.tsx) captura el error y llama `message.error('Usuario o contraseña incorrectos')` como fallback. Por tanto no falta la lógica, sino que **el toast no está llegando a la pantalla**. Causas probables a revisar: (a) el `message` estático de Ant Design v5 sin el contexto `<App>` que lo renderice, (b) z-index/estilo que lo oculta, (c) que el backend devuelva una forma de error distinta a la esperada y el toast se dispare pero sea imperceptible, o (d) recarga de la vista antes de que el toast alcance a mostrarse.

**Pasos para reproducir**
1. Abrir la pantalla de inicio de sesión.
2. Ingresar un usuario válido con contraseña incorrecta (o un usuario inexistente).
3. Pulsar "Iniciar sesión".

**Resultado esperado / Situación actual**
Debe mostrarse un aviso claro y visible de credenciales inválidas — el mensaje **genérico** "Usuario o contraseña incorrectos" (sin diferenciar cuál de los dos falló, según la decisión de seguridad ya confirmada en `OBS-0003`). El formulario permanece con los datos para reintentar.

**Resultado actual / Propuesta de mejora**
No se muestra aviso alguno; la página aparenta solo refrescarse. Propuesta: asegurar que el `message.error` se renderice (envolver la app en `<App>` de Ant Design y usar `App.useApp()` para `message`, o `message.config` global), y verificar que no se reinicie la vista antes de mostrarlo.

**Relación con otras observaciones**
Complementa —no contradice— `OBS-0003` (ITER-002, Rechazada): aquella pedía *diferenciar* usuario vs. contraseña y se rechazó por habilitar enumeración de usuarios; esta pide que el mensaje **genérico ya definido** efectivamente aparezca en pantalla.

**Criterios de aceptación**
- [ ] Al ingresar credenciales inválidas, aparece un aviso visible (toast o inline) con el texto genérico "Usuario o contraseña incorrectos".
- [ ] El aviso permanece el tiempo suficiente para ser leído y el formulario conserva lo escrito para reintentar.
- [ ] El mensaje NO distingue si el error fue en el usuario o en la contraseña (consistente con `OBS-0003`).
- [ ] Se cubre también el caso de error de red / servidor no disponible con un aviso diferenciable ("No se pudo conectar, intenta de nuevo").

**Evidencia**
_(pendiente — adjuntar `images/OBS-0044-01.png` si se captura)_

---

### OBS-0045 — Al crear un ticket, "Proyecto" y "Usuario/cliente" son opcionales y deberían ser obligatorios

- **Módulo/Pantalla:** Tickets > Nuevo Ticket
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En el formulario de creación de tickets (perfil interno), el campo **Cliente** es obligatorio, pero **Proyecto** y **Usuario/cliente** (contacto solicitante) están marcados como opcionales (`label="Proyecto (opcional)"` y `label="Usuario/cliente (opcional)"`, sin regla `required` — [`TicketsPage.tsx:449,454`](frontend/src/pages/TicketsPage.tsx)). Esto permite crear tickets sin proyecto ni solicitante asociado, lo que deja registros huérfanos difíciles de reportar, agrupar por proyecto y facturar.

**Resultado esperado / Situación actual**
Se propone que **Proyecto** y **Usuario/cliente** sean **obligatorios** al crear un ticket desde el perfil interno, de modo que todo ticket quede siempre vinculado a un proyecto y a un contacto solicitante del cliente.

**Resultado actual / Propuesta de mejora**
Actualmente ambos campos aceptan quedar vacíos y el ticket se crea igual. Propuesta: agregar `rules={[{ required: true }]}` a ambos campos y su validación equivalente en backend.

**Decisión de producto requerida (antes de implementar)** — hay dependencias e implicaciones a resolver:
1. **Cadena de dependencias**: "Usuario/cliente" y "Lista" se cargan *a partir* del Proyecto seleccionado (el combo se puebla al elegir proyecto). Hacer Proyecto obligatorio es consistente con esto; hacer Usuario/cliente obligatorio exige que **todo proyecto tenga al menos un contacto** de cliente cargado — si no, se bloquearía la creación del ticket. Verificar ese caso.
2. **¿Aplica también al autoservicio (rol Usuario/cliente)?** En ese flujo el Proyecto también es opcional ([`TicketsPage.tsx:433`](frontend/src/pages/TicketsPage.tsx)) y se limita a los proyectos vinculados al Encargado. Si el Encargado no tiene proyectos vinculados, volverlo obligatorio le impediría crear tickets. Definir el comportamiento para ese rol por separado.
3. **¿Aplica igual a Tareas?** El mismo formulario crea Tickets y Tareas (tipo de registro). Confirmar si la obligatoriedad aplica a ambos o solo a Tickets.
4. **Tickets existentes** creados sin proyecto/solicitante: definir si se migran, se dejan como están, o se marcan para completar.

**Criterios de aceptación** (sujeto a la decisión anterior)
- [ ] Al crear un ticket como perfil interno, no se puede guardar sin seleccionar Proyecto.
- [ ] Al crear un ticket como perfil interno, no se puede guardar sin seleccionar Usuario/cliente.
- [ ] La validación se aplica también en el backend (no solo en el formulario), devolviendo un error tipado por campo.
- [ ] El comportamiento para el rol Usuario/cliente (autoservicio) y para Tareas queda definido y documentado.
- [ ] Un proyecto sin contactos de cliente cargados no deja al usuario en un callejón sin salida (mensaje claro o flujo alterno).

**Evidencia**
_(pendiente — adjuntar `images/OBS-0045-01.png` si se captura)_

---

### OBS-0046 — Al elegir el Proyecto debería auto-rellenarse el Cliente y el nivel de servicio (SLA), sin selección manual

- **Módulo/Pantalla:** Tickets > Nuevo Ticket
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
El flujo actual del formulario es **Cliente → Proyecto**: primero se selecciona el Cliente y el combo de Proyecto se filtra por ese cliente ([`TicketsPage.tsx:445-452`](frontend/src/pages/TicketsPage.tsx)). Dado que un Proyecto pertenece a **un único** Cliente, obligar a elegir el cliente aparte es un paso redundante y propenso a inconsistencias.

Además, el **nivel de servicio (SLA)** no se muestra en la creación: no hay campo de SLA en el formulario; el SLA se calcula por reglas y solo aparece como estado en el listado. El usuario no ve, al crear, qué nivel de servicio regirá el ticket.

**Resultado esperado / Situación actual**
Al seleccionar el **Proyecto**:
- El **Cliente** se rellena automáticamente (solo lectura), derivado del proyecto — sin que el usuario lo elija.
- El **nivel de servicio (SLA)** aplicable se muestra automáticamente (derivado de la regla SLA que corresponda a ese cliente/proyecto), para que el usuario sepa desde la creación bajo qué SLA queda el ticket.

**Resultado actual / Propuesta de mejora**
Hoy hay que elegir Cliente manualmente antes que Proyecto, y el nivel de servicio no es visible al crear. Propuesta:
- Invertir la dependencia: Proyecto como campo guía; al elegirlo, `client_id` se setea solo (`form.setFieldValue`) y su selector queda deshabilitado/solo lectura mostrando el cliente derivado.
- Mostrar un indicador de solo lectura con el **nivel de servicio / regla SLA** que aplicará (nombre de la regla + tiempos), consultando el servicio de SLA con el proyecto/cliente elegido.

**Relación con otras observaciones**
Complementa `OBS-0045` (hacer Proyecto y Usuario/cliente obligatorios). Conviene implementarlas **juntas**: si Proyecto pasa a ser obligatorio y además deriva el Cliente, el campo Cliente deja de necesitar selección manual y el formulario se simplifica en un solo cambio coherente.

**Decisión de producto / puntos a validar**
1. ¿El Cliente se muestra como campo solo-lectura derivado, o se oculta por completo del formulario interno?
2. Si el ticket puede crearse sin proyecto (según lo que se decida en `OBS-0045`), definir el comportamiento del cliente/SLA en ese caso.
3. Confirmar de qué entidad se toma el "nivel de servicio" (regla SLA por cliente, por proyecto, o por prioridad) para mostrar el correcto.

**Criterios de aceptación** (sujeto a la decisión de producto)
- [ ] Al seleccionar un Proyecto, el Cliente asociado se completa automáticamente sin intervención del usuario.
- [ ] El usuario no puede asociar un ticket a un Cliente distinto del dueño del Proyecto (imposible por construcción).
- [ ] Al seleccionar el Proyecto se muestra el nivel de servicio (SLA) que aplicará al ticket.
- [ ] El flujo funciona coherente con la obligatoriedad definida en `OBS-0045`.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0046-01.png` si se captura)_

---

### OBS-0047 — El campo "Skills requeridas" no tiene automatización que facilite la selección

- **Módulo/Pantalla:** Tickets > Skills requeridas
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
El selector de Skills requeridas ([`TicketSkillsSelector.tsx:60`](frontend/src/components/tickets/TicketSkillsSelector.tsx)) es un multi-select plano sobre **todo** el catálogo de skills activas. El usuario debe conocer y elegir manualmente cada skill, sin ninguna ayuda contextual. En un catálogo grande esto es lento y propenso a que se olviden skills relevantes o se elijan inconsistentes entre tickets similares.

**Resultado esperado / Situación actual**
El campo debería ofrecer algún tipo de **automatización/sugerencia** que facilite la selección, en vez de partir de una lista vacía sobre todo el catálogo.

**Resultado actual / Propuesta de mejora**
Selección 100% manual. Opciones de automatización a evaluar (una o varias):
- **Sugerencia por clasificación del ticket**: derivar skills candidatas a partir de la **Herramienta** y/o **Proceso** seleccionados (mapa herramienta→skills), mostrándolas como "sugeridas" preseleccionables.
- **Sugerencia por proyecto**: proponer las skills más usadas en tickets previos del mismo Proyecto/Cliente.
- **Plantillas por tipo de registro**: sets de skills predefinidos por tipo de ticket.
- **Orden inteligente**: mostrar primero las skills más frecuentes en lugar de orden alfabético del catálogo completo.
Las skills requeridas alimentan el matching de asignación (spec 011 + sugerencias por carga spec 024), así que mejorar su captura mejora directamente la calidad de la asignación.

**Criterios de aceptación** (según la opción que apruebe producto)
- [ ] Al clasificar el ticket (herramienta/proceso/proyecto), el selector ofrece skills sugeridas de forma visible.
- [ ] Las sugerencias son preseleccionables/confirmables por el usuario (no se imponen automáticamente sin control).
- [ ] Se mantiene la posibilidad de elegir manualmente cualquier skill del catálogo.

**Relación con otras observaciones**
Se reporta junto con `OBS-0048` (restringir la visibilidad del campo por perfil); ambas afectan el mismo campo pero son cambios independientes.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0047-01.png` si se captura)_

---

### OBS-0048 — "Skills requeridas" debería mostrarse solo a los perfiles de triage (p. ej. Coordinador), no a todos los que editan tickets

- **Módulo/Pantalla:** Tickets > Skills requeridas
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Actualmente el campo de Skills requeridas se habilita para edición con `hasPermission('tickets','edit')` ([`TicketDetailPage.tsx:56,428`](frontend/src/pages/TicketDetailPage.tsx)). Verificado contra la BD, ese permiso lo tienen hoy **Admin, Coordinador y QM** (Resolutor y Usuario/cliente solo tienen `create`, así que ya no lo ven). Como las Skills requeridas son un dato de **triage/asignación**, se propone restringir su edición al perfil que hace la asignación (Coordinador), no a todo el que pueda editar un ticket.

**Resultado esperado / Situación actual**
El campo (edición de Skills requeridas) debería aparecer solo para el/los perfil(es) responsables del triage — el Coordinador como caso principal.

**Resultado actual / Propuesta de mejora**
Hoy lo editan Admin, Coordinador y QM. Propuesta: cambiar el gate de `tickets:edit` a un permiso más específico de triage/asignación (por ejemplo reutilizar `tickets:assign`, o crear un permiso dedicado `tickets:manage_skills`) y asignarlo solo a los perfiles que corresponda.

**Decisión de producto requerida**
1. ¿Solo Coordinador, o también Admin/QM deben poder editar Skills requeridas?
2. ¿Se reutiliza un permiso existente (`tickets:assign`) o se crea uno nuevo dedicado? (nota: `assign` hoy lo tienen los mismos tres roles, así que si el objetivo es dejar SOLO a Coordinador se requiere un permiso nuevo o gating por rol).
3. Para los perfiles sin permiso de edición, ¿el campo se **oculta** por completo o se muestra en **solo lectura**?

**Criterios de aceptación** (según la decisión de producto)
- [ ] El campo de edición de Skills requeridas solo aparece para el/los perfil(es) definido(s) (Coordinador como mínimo).
- [ ] Los demás perfiles con acceso al ticket ven las skills en solo lectura o no las ven, según lo decidido.
- [ ] El gating se aplica de forma consistente en el detalle del ticket y en cualquier otro punto donde se editen skills.

**Relación con otras observaciones**
Se reporta junto con `OBS-0047` (automatizar la selección); mismo campo, cambios independientes.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0048-01.png` si se captura)_

---

### OBS-0049 — No existe relación entre Herramienta y Proceso (catálogos independientes); se propone vincularlos

- **Módulo/Pantalla:** Catálogos · Tickets (campos Herramienta / Proceso)
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Análisis solicitado sobre si "Herramienta" y "Proceso" tienen alguna relación en el sistema. Conclusión: **hoy no existe ninguna relación**.

- Técnicamente, `catalog_tools` y `catalog_processes` son dos tablas independientes con el mismo mixin (id, name, active) — **sin FK entre ellas ni tabla puente** ([`catalog_model.py:18-23`](backend/infra/models/catalog_model.py)). Tanto `tickets` como `resources` las referencian por separado (`tool_id`, `process_id`, nullable e independientes).
- En el formulario de ticket son dos `<Select>` independientes; ninguno filtra al otro ([`TicketsPage.tsx:486-491`](frontend/src/pages/TicketsPage.tsx)).

Sin embargo, en el dominio **sí hay una relación real (muchos-a-muchos)**: una herramienta soporta ciertos procesos, no todos. Con los datos sembrados (Herramientas: `JDE`, `OTM`, `Oracle Fusion`, `Otro`; Procesos: `Compras`, `Finanzas`, `Integraciones`, `Logística`, `Mantenimiento`, `Manufactura`, `Otro`), hay combinaciones sin sentido que el sistema hoy permite — p. ej. **OTM (transporte/logística) + Manufactura**.

**Resultado esperado / Situación actual**
Debería existir una relación administrable Herramienta↔Proceso (muchos-a-muchos) que: (a) evite combinaciones inválidas al clasificar un ticket, y (b) permita que al elegir la Herramienta se filtren los Procesos aplicables.

**Resultado actual / Propuesta de mejora**
Catálogos totalmente independientes, cualquier combinación permitida. Propuesta:
- Tabla puente `tool_processes (tool_id, process_id)` administrable desde Catálogos.
- En el formulario de ticket, al elegir Herramienta filtrar el `<Select>` de Proceso a los vinculados (con opción "Otro" siempre disponible).
- Validación equivalente en backend (rechazar combinación no permitida).

**Relación con otras observaciones**
Es el **habilitador de `OBS-0047`** (automatizar la selección de Skills requeridas): con la cadena `Herramienta → Proceso` establecida, la dupla puede alimentar la sugerencia de skills. Conviene planificarlas en conjunto.

**Decisión de producto / puntos a validar**
1. ¿La relación es muchos-a-muchos (recomendado) o cada proceso pertenece a una sola herramienta?
2. ¿La combinación inválida se **bloquea** o solo se **advierte**?
3. ¿Cómo se tratan los tickets existentes con combinaciones que hoy quedarían inválidas?

**Criterios de aceptación** (según decisión de producto)
- [ ] Existe una relación Herramienta↔Proceso administrable desde Catálogos.
- [ ] Al elegir Herramienta en un ticket, el selector de Proceso muestra solo los procesos vinculados (+ "Otro").
- [ ] La combinación inválida se maneja según lo decidido (bloqueo o advertencia), validada también en backend.

**Evidencia**
_(análisis de código y datos; sin captura de pantalla)_

---

### OBS-0050 — Error de "recurso no asignado" al abrir un ticket con un usuario sin recurso (Admin/Coordinador/QM)

- **Módulo/Pantalla:** Tickets > Detalle del Ticket > Cronómetro (TicketTimerWidget)
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Al entrar al detalle de cualquier ticket aparece un mensaje de error confuso relacionado con "recurso no asignado" / "sin recurso", sin que el usuario entienda a qué se refiere ni haber hecho ninguna acción.

**Causa raíz (confirmada)**
El componente de cronómetro `TicketTimerWidget` se monta al abrir el detalle y ejecuta `getCurrent()` ([`TicketTimerWidget.tsx:44-55`](frontend/src/components/worksessions/TicketTimerWidget.tsx)), que llama al endpoint `GET .../timer/current`. En el backend, `_resolve_resource()` ([`timer.py:58-62`](backend/api/routes/timer.py)) resuelve el recurso del usuario autenticado y, si no existe, lanza `no_resource_profile` → "El usuario no tiene un recurso asociado" (400).

Verificado en BD: `admin@sywork.net`, `coordinador@sywork.net`, `qm@sywork.net` (y otros) **no tienen recurso asociado** — solo los usuarios `resolutor*` lo tienen. Además, `load()` del widget **no captura el error** (`try/finally` sin `.catch()`), por lo que la excepción sube al manejador global de errores y se muestra como un toast genérico que el usuario no sabe interpretar.

**Pasos para reproducir**
1. Iniciar sesión como `admin` (o `coordinador`/`qm` — cualquier usuario sin recurso asociado).
2. Abrir el detalle de cualquier ticket.
3. Observar el toast de error al cargar (sin haber hecho ninguna acción).

**Resultado esperado / Situación actual**
Un usuario sin recurso asociado (Admin/Coordinador/QM) no debe recibir un error al abrir un ticket. El cronómetro es una herramienta personal del recurso que ejecuta el trabajo; para quien no es recurso, el widget debería **ocultarse** o mostrarse deshabilitado con una nota clara ("El cronómetro solo está disponible para recursos que registran tiempo"), **sin toast de error**.

**Resultado actual / Propuesta de mejora**
Aparece un toast de error en cada apertura de ticket para Admin/Coordinador/QM. Propuesta:
- No renderizar `TicketTimerWidget` (ni disparar `getCurrent()`) cuando el usuario no tiene recurso asociado; o
- Manejar `no_resource_profile` dentro del widget (estado vacío/oculto, sin propagar al toast global).
- Revisar el mismo patrón en `TicketWorkSessions` (componente hermano) por si también consulta y falla igual.

**Criterios de aceptación**
- [ ] Un usuario sin recurso asociado abre cualquier ticket sin recibir ningún toast de error.
- [ ] El cronómetro no se muestra (u ofrece un estado informativo) para usuarios sin recurso.
- [ ] Los usuarios que sí son recurso (resolutores) siguen viendo y usando el cronómetro igual que hoy.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0050-01.png` con el toast al abrir el ticket)_

---

### OBS-0051 — El contador "En progreso" del panel de Tickets no corresponde a ningún estado real

- **Módulo/Pantalla:** Tickets > Panel de contadores (StatCards superiores)
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En la parte superior de la pantalla de Tickets, entre los contadores por estado, aparece uno llamado **"En progreso"**. No existe ningún estado del ciclo de vida con ese nombre (los estados son: Nuevo, Pre-Análisis, Contacto, En Análisis, En Ejecución, En Pruebas, Pendiente de Usuario, Resuelto, Cerrado, Cancelado), lo que induce a pensar que hay un estado inexistente.

**Análisis (no es un dato erróneo, es un rótulo confuso)**
El contador es un **agregado intencional**: suma los tickets en los estados intermedios `contacto`, `en_analisis`, `en_ejecucion`, `en_pruebas` ([`TicketsPage.tsx:74`](frontend/src/pages/TicketsPage.tsx) — `IN_PROGRESS_STATUSES`, y línea 160). El StatCard ya trae un subtítulo aclaratorio "Contacto → En pruebas" ([`TicketsPage.tsx:362`](frontend/src/pages/TicketsPage.tsx)), pero el título "En progreso" sigue leyéndose como si fuera un estado.

**Resultado esperado / Situación actual**
El rótulo del contador debería dejar claro que es una **agrupación de varios estados**, no un estado único, para no confundir al usuario.

**Resultado actual / Propuesta de mejora**
Propuestas (elegir una):
- Renombrar a algo explícitamente agregado, p. ej. "En proceso (varios estados)" o "Activos".
- Mantener "En progreso" pero con un tooltip/ícono de información que liste los estados que agrupa.
- Alinear el criterio con el resto de contadores (que sí son 1:1 con un estado o con una regla clara como "Vencen hoy").

**Criterios de aceptación**
- [ ] El contador deja claro visualmente que agrupa varios estados y no es un estado del ciclo de vida.
- [ ] Los estados que agrupa quedan visibles (en el rótulo, subtítulo o tooltip).

**Evidencia**
_(pendiente — adjuntar `images/OBS-0051-01.png` del panel de contadores)_

---

### OBS-0052 — El panel de asignación no muestra QMs (no tienen perfil de recurso); el flujo "Pre-Análisis (QM)" no tiene a quién asignar

- **Módulo/Pantalla:** Tickets > Asignación (Triage Push / AssignModal)
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En la pantalla/modal de asignación solo se despliegan resolutores; no aparecen los QMs. Como consecuencia, el botón "Pre-Análisis (QM)" no tiene ningún QM disponible para asignar.

**Causa raíz (confirmada)**
La grilla de candidatos se alimenta de `useResourceCandidates` → `resourceService.list({ active: true })` ([`useResourceCandidates.ts:26`](frontend/src/components/tickets/useResourceCandidates.ts)), es decir, de la tabla `resources`. Verificado en BD: los usuarios QM (`qm@sywork.net`, etc.) **no tienen perfil de recurso** (igual que Admin/Coordinador — ver `OBS-0050`). Por eso nunca aparecen como candidatos. Además, la grilla no filtra por rol: muestra todos los recursos existentes, que hoy son solo resolutores.

**Pasos para reproducir**
1. Abrir un ticket NUEVO y entrar a asignar (Triage).
2. Observar la lista de candidatos → solo resolutores.
3. Pulsar "Pre-Análisis (QM)" → no hay ningún QM para elegir.

**Resultado esperado / Situación actual**
El flujo de "Pre-Análisis (QM)" debe poder listar y asignar a usuarios con rol QM. Esto implica resolver de dónde salen los QM asignables (que los QM tengan perfil de recurso, o que la lista de candidatos para el modo QM se arme por rol y no por la tabla `resources`).

**Resultado actual / Propuesta de mejora**
Solo se listan resolutores. Propuesta: definir el origen de los QM asignables — (a) que los usuarios QM tengan también un `resource` (revisar el seed/alta), o (b) que el modo "Pre-Análisis (QM)" liste candidatos por **rol QM** desde `users`/`roles` en lugar de la tabla `resources`. Filtrar la grilla según el modo (resolutores para "Asignar", QMs para "Pre-Análisis").

**Relación con otras observaciones**
Comparte causa con `OBS-0050` (usuarios no-resolutores sin perfil de recurso). Se reporta junto con `OBS-0053` (falta validación de rol vs. estado destino).

**Criterios de aceptación**
- [ ] El flujo "Pre-Análisis (QM)" lista usuarios con rol QM y permite asignarles el ticket.
- [ ] La grilla de candidatos se filtra según el modo (resolutores vs. QMs).
- [ ] Se define y documenta el origen de datos de los QM asignables.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0052-01.png` de la grilla de candidatos)_

---

### OBS-0053 — Se puede asignar un ticket a un resolutor y pasarlo a Pre-Análisis; Pre-Análisis debería ser exclusivo de QM

- **Módulo/Pantalla:** Tickets > Asignación (Triage) · FSM del ciclo de vida
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Es posible seleccionar un **resolutor** en la grilla de asignación y pulsar el botón "Pre-Análisis (QM)", enviando el ticket al estado `pre_analisis` con un resolutor asignado. Según el ciclo de vida, `pre_analisis` es el estado propio del QM.

**Causa raíz (confirmada)**
El endpoint de asignación decide el estado destino según el parámetro **`mode`** (`resolver | pre_analysis`, [`tickets.py:96`](backend/api/routes/tickets.py)), que mapea al FSM: `assign_resolver`→`contacto`, `assign_qm`→`pre_analisis` ([`ticket_fsm.py:20-21`](backend/domain/fsm/ticket_fsm.py)). El `AssignModal` ofrece ambos botones sobre **la misma grilla de recursos**, sin filtrar por rol ([`AssignModal.tsx:53-60`](frontend/src/components/tickets/AssignModal.tsx)), y **no se valida** —ni en frontend ni en backend— que el recurso seleccionado tenga rol QM cuando el modo es `pre_analysis`. Por eso un resolutor puede terminar en `pre_analisis`.

**Pasos para reproducir**
1. Abrir un ticket NUEVO y entrar a asignar.
2. Seleccionar un resolutor de la grilla.
3. Pulsar "Pre-Análisis (QM)".
4. El ticket pasa a `pre_analisis` con el resolutor asignado (no se rechaza).

**Resultado esperado / Situación actual**
El sistema debe impedir enviar a `pre_analisis` a un usuario que no sea QM. El modo `pre_analysis` solo debe aceptar asignados con rol QM; el modo `resolver` solo resolutores.

**Resultado actual / Propuesta de mejora**
No hay validación de rol vs. modo/estado destino. Propuesta: validar en backend que el `assignee` tenga el rol correspondiente al `mode` (QM para `pre_analysis`, Resolutor para `resolver`), devolviendo un error tipado (p. ej. `assignee_role_mismatch`) si no coincide; y en frontend, filtrar la grilla por rol según el botón/modo (ligado a `OBS-0052`).

**Relación con otras observaciones**
Depende de `OBS-0052` (para que existan QMs asignables) y comparte contexto con `OBS-0050`. La validación de rol es el complemento de negocio del filtrado de candidatos.

**Criterios de aceptación**
- [ ] Enviar a Pre-Análisis solo se permite si el asignado tiene rol QM (validado en backend).
- [ ] Asignar como resolutor solo se permite si el asignado tiene rol Resolutor.
- [ ] Un intento de combinación inválida devuelve un error claro y no cambia el estado del ticket.
- [ ] La UI filtra los candidatos según el modo para evitar la combinación inválida desde el origen.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0053-01.png` del ticket en Pre-Análisis con resolutor asignado)_

---

### OBS-0054 — Mensaje confuso: al faltar skills se muestra "no tiene perfil de recurso" en lugar de un mensaje sobre skills

- **Módulo/Pantalla:** Tickets > Detalle del Ticket / Asignación (mensajería)
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En el detalle del ticket / asignación, cuando un usuario no tiene skills asociadas, aparece un mensaje que dice que "no tiene perfil de recurso asignado". El mensaje habla del perfil de recurso, no de las skills, y confunde: el usuario que estaba pensando en skills no entiende por qué se le habla del recurso.

**Análisis**
El texto "no tiene un perfil de recurso asociado" corresponde al caso `no_resource_profile` (el usuario no tiene registro en `resources`). En el detalle del ticket, ese mensaje lo dispara con más probabilidad el cronómetro (`TicketTimerWidget` → `getCurrent` → `no_resource_profile`), que es exactamente lo descrito en **`OBS-0050`**. Es decir, el mensaje no es realmente "sobre skills", sino el error de recurso del cronómetro apareciendo en la misma pantalla, lo que induce a interpretarlo como si fuera un problema de skills.

Puntos a distinguir (a confirmar con captura):
- Si el mensaje proviene del **cronómetro** (`no_resource_profile`): lo cubre el fix de `OBS-0050` (ocultar el cronómetro para usuarios sin recurso, sin toast).
- Si existe además un punto donde, teniendo recurso pero **sin skills**, se muestra el mensaje de "perfil de recurso" en vez de uno de skills: ahí sí corresponde corregir la redacción para que hable de skills ("Este recurso no tiene skills asociadas").
- Nota de contraste: la grilla de candidatos ya muestra correctamente "sin skills" para recursos sin skills ([`ResourceCandidateGrid.tsx:108`](frontend/src/components/tickets/ResourceCandidateGrid.tsx)); el problema es específicamente el mensaje de "perfil de recurso" apareciendo fuera de lugar.

**Resultado esperado / Situación actual**
El mensaje que ve el usuario debe corresponder a la causa real: si es falta de skills, hablar de skills; si es falta de perfil de recurso, no mostrarlo como un error intrusivo (ver `OBS-0050`).

**Resultado actual / Propuesta de mejora**
Se muestra "no tiene perfil de recurso" en un contexto donde el usuario esperaba información sobre skills. Propuesta: (a) resolver primero `OBS-0050` (que el mensaje de recurso no aparezca como toast al abrir el ticket), y (b) revisar que cualquier mensaje de "sin skills" use un texto explícito de skills, no el de perfil de recurso.

**Relación con otras observaciones**
Muy probablemente el mismo síntoma que `OBS-0050` (mensaje `no_resource_profile` del cronómetro en el detalle del ticket); relacionada con `OBS-0052` (skills/recursos en asignación). Verificar con captura para decidir si se cierra como duplicada de `OBS-0050` o si aporta un cambio de redacción propio.

**Criterios de aceptación**
- [ ] En el detalle del ticket, un usuario sin recurso no ve el mensaje "no tiene perfil de recurso" como error intrusivo (cubierto por `OBS-0050`).
- [ ] Cualquier indicación de ausencia de skills usa un texto explícito de skills, no el de perfil de recurso.

**Evidencia**
_(pendiente — captura del mensaje exacto en el detalle del ticket para confirmar el elemento que lo dispara: `images/OBS-0054-01.png`)_

---

### OBS-0055 — No se puede finalizar el cronómetro por la tarde/noche: falso error "fecha futura" (desajuste de zona horaria)

- **Módulo/Pantalla:** Tickets > Detalle del Ticket > Cronómetro (finalizar)
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Al finalizar el cronómetro dentro de un ticket aparece el mensaje "No se puede registrar tiempo con fecha futura" y el registro no se guarda, dejando al usuario **sin poder terminar el timer**. Es bloqueante para el registro de tiempo por cronómetro (spec 012).

**Causa raíz (confirmada con valores reales)**
Desajuste de zona horaria entre cómo se calcula la fecha del registro y cómo se valida:
- Al finalizar, `work_date` se calcula con la hora **local del recurso**: `resource_local_now(resource, now).date()` ([`ticket_timer_service.py:24`](backend/domain/services/ticket_timer_service.py)). Como los recursos tienen hoy `calendar_country = None` (verificado en BD), `resource_local_now` cae de vuelta a **UTC**, por lo que `work_date` = fecha UTC.
- La validación `validate_not_future` compara `work_date > date.today()` ([`work_session_service.py:31-34`](backend/domain/services/work_session_service.py)), donde `date.today()` es la fecha **local del servidor** (contenedor con `TZ=America/Bogota`, UTC-5).

Valores capturados en el contenedor durante la prueba:
```
TZ = America/Bogota
date.today() (servidor local) = 2026-07-26
UTC now                       = 2026-07-27 00:39
resources.calendar_country    = None (todos)
```
Entre las **19:00 y la medianoche hora Colombia** (00:00–05:00 UTC), UTC ya avanzó al día siguiente: `work_date` (UTC) = 2026-07-27 mientras `date.today()` (Bogota) = 2026-07-26 → `2026-07-27 > 2026-07-26` → falso `future_date`.

**Pasos para reproducir**
1. Con `TZ=America/Bogota` (UTC-5), a partir de las ~19:00 hora local.
2. Iniciar el cronómetro en un ticket (como un recurso/resolutor).
3. Pulsar Finalizar.
4. Aparece "No se puede registrar tiempo con fecha futura" y no se guarda.

**Resultado esperado / Situación actual**
Finalizar el cronómetro debe registrar el tiempo sin error a cualquier hora del día. La comparación de "fecha futura" debe hacerse sobre la **misma base horaria** con que se calcula `work_date`.

**Resultado actual / Propuesta de mejora**
Falso `future_date` en la franja tarde/noche. Propuesta:
- Hacer consistente `validate_not_future`: comparar `work_date` contra la fecha **en la misma zona** con que se calculó (la local del recurso), no contra `date.today()` del servidor. P. ej. pasar la referencia `today` al validador desde el mismo `resource_local_now`.
- Asegurar que los recursos tengan `calendar_country` (hoy `None` en todos), de modo que `resource_local_now` no caiga a UTC. Esto conecta con el seed de recursos y con el módulo de calendarios (specs 020/022).
- Considerar una pequeña tolerancia (p. ej. permitir hasta fin del día local) para evitar bordes por segundos.

**Impacto**
Bloqueante para el cronómetro en la franja de la tarde/noche (horario habitual de trabajo en Colombia). Alta probabilidad de reproducirse en uso real.

**Relación con otras observaciones**
El cálculo de `work_date` con hora local del recurso proviene del fix de `OBS-0036` (SLA/registro fuera de horario); ese cambio dejó `validate_not_future` con una base horaria distinta. La ausencia de `calendar_country` se cruza con la configuración de calendario del recurso (`OBS-0037`).

**Criterios de aceptación**
- [ ] Finalizar el cronómetro guarda el registro sin error a cualquier hora del día (probado después de las 19:00 hora Colombia).
- [ ] La validación de "fecha futura" usa la misma zona horaria que el cálculo de `work_date`.
- [ ] Un recurso sin `calendar_country` no provoca el falso `future_date` (fallback coherente).

**Evidencia**
_(valores de contenedor capturados arriba; adjuntar `images/OBS-0055-01.png` con el mensaje en la UI)_

---

### OBS-0056 — Al cambiar de estado con el comentario vacío se bloquea la acción pero no se ve ninguna alerta

- **Módulo/Pantalla:** Tickets > Detalle del Ticket > Cambio de estado (comentario tipificado)
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Al cambiar el estado del ticket se selecciona el tipo de comentario y, si no se escribe texto en la caja, la acción no se ejecuta — pero **no se muestra ninguna alerta** que indique que falta el comentario. El usuario queda sin saber por qué "no pasa nada".

**Causa raíz**
La validación existe: `send()` hace `if (isRichTextEmpty(body)) { message.warning('El comentario no puede estar vacío'); return }` ([`CommentComposer.tsx:55-59`](frontend/src/components/tickets/CommentComposer.tsx)). El problema es que ese `message.warning` **no se ve** — mismo patrón que `OBS-0044` (login): los `message.*` inline de Ant Design no están llegando a la pantalla.

Dato relevante para el diagnóstico: el error de `OBS-0050` (cronómetro) **sí se muestra**, porque proviene del manejador global de errores (spec 013), mientras que estos `message.warning/success` invocados directamente dentro del componente no aparecen. Esa inconsistencia apunta a que el `message` estático de antd v5 necesita el contexto `<App>` para renderizar, y el manejador global usa otra vía que sí funciona.

**Pasos para reproducir**
1. Abrir un ticket en un estado no final.
2. Seleccionar un tipo de comentario que implique cambio de estado, dejar la caja de texto vacía.
3. Pulsar "Registrar comentario".
4. No ocurre nada visible: ni cambio ni alerta.

**Resultado esperado / Situación actual**
Debe mostrarse una alerta clara "El comentario no puede estar vacío" (idealmente inline junto a la caja, no solo toast) cuando se intenta cambiar el estado sin texto.

**Resultado actual / Propuesta de mejora**
La acción se bloquea en silencio. Propuesta: asegurar que los `message.*` se rendericen (envolver la app en `<App>` de antd y usar `App.useApp()`), y/o mostrar el error inline en el `RichTextEditor`/campo de comentario. Revisar de forma transversal todos los `message.warning/success/error` inline (mismo origen que `OBS-0044`).

**Relación con otras observaciones**
Misma causa raíz probable que `OBS-0044` (toasts de login invisibles). Contrasta con `OBS-0050` (toast global sí visible). Se reporta junto con `OBS-0057` (confirmación del cambio de estado).

**Criterios de aceptación**
- [ ] Intentar cambiar de estado con el comentario vacío muestra una alerta visible indicando que el comentario es obligatorio.
- [ ] La validación se ve idealmente inline junto al campo, no solo como toast fugaz.
- [ ] Se corrige de forma consistente con `OBS-0044` (todos los `message.*` inline visibles).

**Evidencia**
_(pendiente — adjuntar `images/OBS-0056-01.png`)_

---

### OBS-0057 — Al cambiar de estado con éxito no hay confirmación específica del cambio (dice "Comentario registrado")

- **Módulo/Pantalla:** Tickets > Detalle del Ticket > Cambio de estado (comentario tipificado)
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
Cuando se escribe el comentario y la acción sí cambia el estado del ticket, no hay ninguna confirmación de que el **estado cambió**. El usuario no recibe una señal clara de que el ticket pasó a un nuevo estado.

**Causa raíz**
En caso de éxito, `send()` muestra `message.success('Comentario registrado')` ([`CommentComposer.tsx:65`](frontend/src/components/tickets/CommentComposer.tsx)) — un mensaje genérico sobre el comentario, no sobre el cambio de estado. Además, ese toast probablemente tampoco se vea (mismo problema que `OBS-0056`/`OBS-0044`), así que la ausencia de confirmación es doble: el texto no menciona el estado, y el toast no se renderiza.

**Resultado esperado / Situación actual**
Tras un cambio de estado exitoso, debe confirmarse explícitamente el nuevo estado — p. ej. "Ticket movido a 'En Ejecución'" — y/o reflejarse visualmente de inmediato (el tag de estado actualizado, entrada en el historial de estados).

**Resultado actual / Propuesta de mejora**
Mensaje genérico "Comentario registrado", sin referencia al estado. Propuesta:
- Diferenciar el mensaje: si el comentario disparó una transición, confirmar el nuevo estado ("Estado actualizado a X"); si fue solo un comentario, mantener "Comentario registrado".
- Asegurar que el toast se vea (ligado a `OBS-0056`/`OBS-0044`).
- Refuerzo visual: que el tag de estado y el historial se actualicen visiblemente al instante (ya se llama `onUpdated()`, verificar que el usuario perciba el cambio).

**Relación con otras observaciones**
Depende de `OBS-0056`/`OBS-0044` (que el toast sea visible). Complementa la coherencia de feedback de `OBS-0018` (feedback inline de validación).

**Criterios de aceptación**
- [ ] Un cambio de estado exitoso confirma explícitamente el nuevo estado del ticket.
- [ ] El mensaje distingue entre "solo comentario" y "comentario que cambió el estado".
- [ ] El cambio se refleja visualmente de inmediato (tag de estado + historial).

**Evidencia**
_(pendiente — adjuntar `images/OBS-0057-01.png`)_

---

### OBS-0058 — La prioridad se muestra como "P3", "P2"… en vez de "Media", "Alta"…

- **Módulo/Pantalla:** Tickets > Listado / badge de Prioridad
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En el apartado de prioridad de los tickets se muestra "P1", "P2", "P3", "P4" en lugar del nombre legible ("Crítica", "Alta", "Media", "Baja"). Los códigos no comunican la urgencia de forma directa.

**Causa raíz**
El componente `PriorityBadge` usa por defecto códigos cortos: `SHORT = { critical:'P1', high:'P2', medium:'P3', low:'P4' }` y solo agrega la palabra cuando se le pasa `full` ([`PriorityBadge.tsx:4,17`](frontend/src/components/tickets/PriorityBadge.tsx)). En el listado se usa sin `full` ([`TicketsPage.tsx:323`](frontend/src/pages/TicketsPage.tsx)), por lo que se ve "P3". El mapa completo existe: `PRIORITY_LABELS = { critical:'Crítica', high:'Alta', medium:'Media', low:'Baja' }` ([`types/ticket.ts:26-27`](frontend/src/types/ticket.ts)).

**Inconsistencia**: el listado muestra el código ("P3") mientras que el **filtro de prioridad y el formulario** usan las palabras ("Media"), por lo que el mismo dato aparece de dos maneras distintas en la misma pantalla.

**Resultado esperado / Situación actual**
La prioridad debería mostrarse con el nombre legible ("Crítica/Alta/Media/Baja"), de forma consistente en listado, filtro, formulario y detalle.

**Resultado actual / Propuesta de mejora**
Se muestra "P1..P4" en el badge del listado. Propuesta:
- Mostrar la palabra en el badge (usar `full`, o mostrar directamente `PRIORITY_LABELS[priority]`), conservando el color del chip.
- Si el diseño (docs/PROPUESTA_VISUAL.html) quiere conservar el código, mostrar ambos ("P3 · Media") para que se entienda el mapeo; pero la preferencia reportada es usar la palabra.
- Unificar con el filtro/formulario para que no haya dos representaciones del mismo dato.

**Relación con otras observaciones**
Se cruza con `OBS-0017` (orden por urgencia real): ambas buscan que la prioridad sea legible y accionable para el usuario.

**Criterios de aceptación**
- [ ] La prioridad se muestra con su nombre legible (Crítica/Alta/Media/Baja) en el listado.
- [ ] La representación de prioridad es consistente entre listado, filtro, formulario y detalle.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0058-01.png` del listado con "P3")_

---

### OBS-0059 — El SLA del ticket muestra el resultado de la fase Contacto pero no el de la fase de cierre/ejecución

- **Módulo/Pantalla:** Tickets > Detalle del Ticket > SLA
- **Tipo:** Defecto
- **Estado:** Abierta
- **Reportado por:** Emilio Vargas
- **Iteración de origen:** ITER-008
- **Iteración de cierre:** —

**Descripción**
En la pestaña de SLA dentro del ticket se muestra que se cumplió el SLA de **Contacto**, pero no se muestra el resultado del SLA de **cierre** (la segunda fase, "Diagnóstico, Análisis y Ejecución", que termina al resolver/cerrar). El usuario no puede saber si el ticket cumplió o venció su SLA de resolución.

**Causa raíz (confirmada) — es más que un gap de UI**
El sistema solo congela/persiste el resultado de la fase Contacto:
- Backend: la única columna de resultado por fase es `sla_contact_result` ([`ticket_model.py:59`](backend/infra/models/ticket_model.py)); **no existe** un campo equivalente para la fase de ejecución/cierre. Solo Contacto se congela como "cumplido/vencido" ([`sla_service.py:334`](backend/domain/services/sla_service.py)).
- Frontend: el tipo `TicketSlaState` expone solo `contact_result` / `contact_consumed_seconds` ([`types/sla.ts:48-49`](frontend/src/types/sla.ts)); el `SlaCounter` únicamente renderiza el resultado de Contacto ([`SlaCounter.tsx:101-106`](frontend/src/components/tickets/SlaCounter.tsx)); y `PHASE_LABELS` no tiene etiqueta para la fase `cerrado` ([`SlaCounter.tsx:14-17`](frontend/src/components/tickets/SlaCounter.tsx)).

Posible consecuencia mayor a verificar: el indicador general `sla_met` parece derivarse **solo** del resultado de Contacto ([`sla_service.py:393-394`](backend/domain/services/sla_service.py)) — hay que confirmar si el SLA de la fase de ejecución/cierre se está evaluando y guardando en algún lado, o si directamente no se calcula.

**Pasos para reproducir**
1. Crear un ticket con SLA configurado y llevarlo por su ciclo hasta Cerrado.
2. Abrir la pestaña/sección de SLA del ticket.
3. Observar que aparece el resultado de Contacto (p. ej. "Cumplido") pero no un resultado de la fase de cierre/ejecución.

**Resultado esperado / Situación actual**
El detalle de SLA debe mostrar el resultado de **ambas** fases: Contacto y Ejecución/Cierre (cumplido/vencido + tiempo consumido de cada una), especialmente en un ticket ya cerrado.

**Resultado actual / Propuesta de mejora**
Solo se muestra el resultado de Contacto. Propuesta:
- Backend: congelar y persistir el resultado de la fase de ejecución/cierre al cerrar (p. ej. `sla_execution_result` + `sla_execution_consumed_seconds`), análogo a lo que ya se hace con Contacto.
- Exponerlo en `TicketSlaState`.
- Frontend: mostrar el resultado de la fase de ejecución/cierre junto al de Contacto en `SlaCounter`, y agregar la etiqueta de la fase `cerrado` en `PHASE_LABELS`.
- Verificar que `sla_met` general considere ambas fases.

**Relación con otras observaciones**
Se cruza con las observaciones de SLA de ITER-004/005 (`OBS-0038`, `OBS-0039`) sobre el cálculo del SLA; aquí el foco es la **visualización del resultado de la fase de cierre**, no el cálculo del tiempo.

**Criterios de aceptación**
- [ ] El detalle de SLA de un ticket cerrado muestra el resultado (cumplido/vencido) de la fase de ejecución/cierre, además del de Contacto.
- [ ] Cada fase muestra su tiempo consumido vs. límite.
- [ ] La fase `cerrado` tiene una etiqueta legible.
- [ ] Se confirma que el resultado de la fase de cierre se persiste y que `sla_met` general lo considera.

**Evidencia**
_(pendiente — adjuntar `images/OBS-0059-01.png` de la pestaña de SLA mostrando solo Contacto)_

## Revalidación de observaciones previas (OBS-0013…OBS-0028, "Lista para Validar")

> Al tocar cada pantalla durante el E2E, marcar el resultado. Verificada → se actualiza `BACKLOG.md` con esta iteración como cierre. Reabierta → vuelve a "En Desarrollo".

| OBS | Pantalla | Corrección esperada | Resultado |
|---|---|---|---|
| OBS-0013 | Auth · Maestros | JWT inválido → 401 (no 500) | _(pendiente)_ |
| OBS-0014 | Clientes | Nombre valida caracteres/longitud | _(pendiente)_ |
| OBS-0015 | Clientes | Ayuda "email no verificado" | _(pendiente)_ |
| OBS-0016 | Clientes | Teléfono con código de país (E.164) | _(pendiente)_ |
| OBS-0017 | Clientes | Campos VPN enmascarados al crear/editar | _(pendiente)_ |
| OBS-0018 | Formularios | Feedback inline de validación | _(pendiente)_ |
| OBS-0019 | Proyectos | Cliente no editable en edición (con aviso) | _(pendiente)_ |
| OBS-0020 | Equipo | Identificación validada | _(pendiente)_ |
| OBS-0021 | Equipo | Nacionalidad = lista de países | _(pendiente)_ |
| OBS-0022 | Equipo | Fecha nacimiento con edad mínima | _(pendiente)_ |
| OBS-0023 | Equipo | Nivel de estudios = catálogo | _(pendiente)_ |
| OBS-0024 | Equipo | Equipo = catálogo administrable | _(pendiente)_ |
| OBS-0025 | Roles | Matriz muestra todos los permisos reales | _(pendiente)_ |
| OBS-0026 | Tickets/Cierre | Bloquea cierre sin tiempo (409) | _(pendiente)_ |
| OBS-0027 | Auth | Una sesión por navegador | _(pendiente)_ |
| OBS-0028 | Tickets/Listados | Orden por urgencia real | _(pendiente)_ |
