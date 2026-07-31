# Research: Herencia de Subtareas, Vinculación Bidireccional y Corrección de Flickering

## Decisión 1 — Punto de herencia de campos (backend, en creación)

**Decisión**: La herencia de Nivel de escalamiento, Usuario solicitante/cliente y Skills
requeridas ocurre en `TicketList.post` (`backend/api/routes/tickets.py`), en el mismo bloque
`if parent_task_id:` que ya existe (línea ~879) y que hoy hereda `list_id` del padre. Se
extiende ese mismo bloque, no se crea un mecanismo nuevo.

**Rationale**: Ya existe precedente idéntico en el propio código: la Subtarea hereda
`list_id` de la Tarea padre "en creación... no tiene Lista propia editable después" (comentario
existente en el archivo). Nivel de escalamiento y Usuario solicitante son columnas directas de
`Ticket` (`escalation_level`, `client_contact_id`), por lo que se copian igual que `list_id`:
solo si el valor no vino explícito en el payload. Las Skills requeridas no son una columna sino
una relación M:N (`ticket_skills_table`, gestionada por `TicketRepository.update_skills`); se
resuelven leyendo `parent_ticket.skills` (ya cargado por el ORM) e invocando
`TicketRepository(db).update_skills(created.id, [s.id for s in parent_ticket.skills])`
inmediatamente después de `TicketRepository(db).create(ticket)`, solo cuando el payload no trae
`skill_ids` propios.

**Alternatives considered**:
- Herencia en el frontend (`SubtaskList.tsx` arma el payload completo con los valores ya
  visibles en `ticket.escalation_level`/`ticket.client_contact_id`/`ticket.skills`): se
  descarta como mecanismo único porque el endpoint `POST /api/tickets` también se usa desde
  otros clientes/flujos futuros (AI-Native, Principio VI) — la herencia debe ser una garantía
  del backend, no del formulario. Sí se ajusta `SubtaskList.tsx` para dejar de enviar
  `escalation_level`/`client_contact_id`/`skill_ids` propios en el alta simple (hoy no los
  envía en absoluto), de modo que el backend complete el resto por defecto.
- Trigger/columna calculada en base de datos: rechazado, viola el Principio I (lógica de
  negocio fuera de Capa 1/Capa 2 explícita) y el Principio V (no se aprueba mecanismo nuevo de
  triggers de PostgreSQL).

## Decisión 2 — Relación inversa Tarea padre → Subtareas (API)

**Decisión**: No se requiere cambio de modelo ni migración. `_ticket_detail` (línea ~513) ya
calcula `subtasks = TicketRepository(db).list_subtasks(ticket.id)` y las serializa vía
`_ticket_summary` en el campo `subtasks` de la respuesta; el frontend (`SubtaskList.tsx`) ya
lista y navega a cada una. El "contador" pedido por el usuario se deriva de
`ticket.subtasks.length` en el frontend (US2, FR-005) — no se agrega un campo `subtasks_count`
redundante en la API.

**Rationale**: Cero superficie nueva de API; el contrato ya expone todo lo necesario. Cumple
Principio VII (alcance mínimo).

**Alternatives considered**: Agregar `subtasks_count` explícito en `_ticket_summary` — se
descarta por redundante (el array ya viaja completo en el detalle) y por tocar el serializador
compartido con `_ticket_detail`/listados donde no aplica.

## Decisión 3 — Campo "Tarea Padre" con hipervínculo en la Subtarea

**Decisión**: Se agrega un campo `parent` (objeto resumen: `id`, `ticket_number`, `title`) al
diccionario devuelto por `_ticket_detail`, resuelto solo cuando `ticket.parent_task_id` no es
null, reutilizando `TicketRepository(db).get_by_id(ticket.parent_task_id)` (ya usado en el
propio `POST` para validar la Tarea padre). El campo existente `parent_task_id` (string) se
conserva sin cambios para no romper consumidores actuales; `parent` es aditivo.

En el frontend, dentro de `Card title="Clasificación"` de `TicketDetailPage.tsx`, se agrega un
`<Descriptions.Item label="Tarea Padre">` condicionado a `ticket.parent` truthy, con un
`Button type="link"` que navega a `/tickets/{ticket.parent.id}` — mismo patrón ya usado en esa
misma tarjeta para "Registro relacionado" (línea ~300) y "Referenciado por" (línea ~309).

**Rationale**: Reutiliza el patrón de hipervínculo interno ya validado y aprobado en el propio
componente (no introduce un patrón de navegación nuevo). `ticket_number`/`title` alcanzan para
el requisito "código/nombre de la tarea origen".

**Alternatives considered**: Resolver el padre en el frontend con una llamada extra
(`ticketService.get(ticket.parent_task_id)`) — se descarta: un round-trip adicional por cada
apertura de Subtarea es innecesario cuando el backend ya tiene el dato a mano en el mismo query
de detalle (ya resuelve el padre para la validación de creación, mismo patrón de acceso).

## Decisión 4 — Causa raíz del flickering en scroll

**Decisión**: El origen NO es CSS (`overflow-y`/`height: 100%`) sino un listener de scroll con
histéresis insuficiente en `TicketDetailPage.tsx` (líneas 88-98):

```ts
useEffect(() => {
  let lastY = window.scrollY
  const onScroll = () => {
    const y = window.scrollY
    if (y > lastY && y > 80) setTimeExpanded(false)
    else if (y < lastY) setTimeExpanded(true)
    lastY = y
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  return () => window.removeEventListener('scroll', onScroll)
}, [])
```

Cualquier micro-oscilación de scroll (momentum/rubber-band scrolling, trackpads, o incluso el
redondeo de píxeles del navegador) dispara `y < lastY` en el frame siguiente a un `y > lastY`,
alternando `timeExpanded` entre `true`/`false` en sucesión rápida. Ese estado controla el prop
`compact` de `TicketWorkSessions` dentro de la Card "Registros de tiempo" — la primera tarjeta
de la columna izquierda, inmediatamente arriba de "Clasificación" e "Historial de estados".
Cada toggle cambia la altura renderizada de esa tarjeta, empujando verticalmente todo el
contenido debajo (Clasificación + Historial) en cada evento de scroll — el "parpadeo" reportado
por el usuario en exactamente esas dos secciones.

**Rationale**: Se descarta la hipótesis de CSS/`overflow-y` porque el único contenedor con
scroll interno propio (`overflowY: 'auto'`, línea 491) es el historial de comentarios del
sidebar derecho, ya acotado con `maxHeight: 420` desde la spec 030 — no interseca con el panel
izquierdo donde se reporta el bug. El causante real es el re-render en cascada por
`setState`+reflow, no un problema de estilos.

**Fix**: agregar una zona muerta (dead-zone) de distancia mínima antes de alternar el estado, y
throttlear el handler con `requestAnimationFrame` para no reaccionar a cada micro-evento de
scroll (patrón estándar para listeners de dirección de scroll ruidosos):

```ts
useEffect(() => {
  let lastY = window.scrollY
  let ticking = false
  const DEAD_ZONE = 12 // px — ignora micro-oscilaciones de scroll (rubber-band, trackpad)
  const onScroll = () => {
    if (ticking) return
    ticking = true
    requestAnimationFrame(() => {
      const y = window.scrollY
      const delta = y - lastY
      if (Math.abs(delta) > DEAD_ZONE) {
        if (delta > 0 && y > 80) setTimeExpanded(false)
        else if (delta < 0) setTimeExpanded(true)
        lastY = y
      }
      ticking = false
    })
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  return () => window.removeEventListener('scroll', onScroll)
}, [])
```

`setTimeExpanded` ya bails out en React cuando el valor no cambia (mismo booleano), así que la
zona muerta es la pieza que faltaba: sin ella, deltas pequeños alrededor del umbral seguían
alternando el valor real (no solo repitiendo el mismo).

**Alternatives considered**:
- Quitar el `position: sticky` de la Card "Comentarios y acciones" (sidebar derecho, línea 481):
  descartado — ese sticky es intencional (OBS-0042, spec 030) y no interseca con el panel
  izquierdo donde ocurre el parpadeo reportado; tocarlo sería exceder el alcance.
  - Mover el resumen de tiempo a un contenedor de altura fija (sin colapsar/expandir): descartado
  porque elimina una funcionalidad ya validada (Fase 2.2, US1 FR-004/FR-005) en vez de arreglar
  el bug puntual de histéresis.
