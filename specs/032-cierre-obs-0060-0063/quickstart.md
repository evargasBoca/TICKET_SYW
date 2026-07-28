# Quickstart: Validación de OBS-0060–OBS-0063

Guía de verificación end-to-end contra Docker real, siguiendo el mismo patrón usado en features previas de este repo (ej. `specs/030-.../quickstart.md`). No sustituye el retest formal del framework UAT (`UAT/CONVENTIONS.md`) — deja el backlog en `Lista para Validar` para que el validador (Arely Pazmiño u otro consultor UAT asignado) confirme.

## Prerrequisitos

- Entorno Docker de desarrollo levantado (`docker compose up`, ver `README.md` del repo), en una zona horaria distinta a UTC (ej. `America/Bogota`, ya usada por el seed de Aris) para poder reproducir/verificar el desfase de OBS-0060.
- Un ticket de prueba abierto, asignado a un recurso con horario laboral configurado.
- Dos recursos con rol Resolutor disponibles para asignar/reasignar (para OBS-0062/OBS-0063), uno de ellos con posibilidad de desactivar su cuenta de usuario sin afectar el resto del entorno de prueba.
- Acceso con un usuario con permiso `tickets:assign` (Coordinador).

## OBS-0060 — Hora del historial de registros de tiempo

1. Abrir el ticket de prueba y registrar tiempo manualmente indicando una hora de inicio/fin conocida (ej. 17:37–17:38).
2. Abrir el historial de registros de tiempo del mismo ticket.
3. Verificar que la hora mostrada es exactamente 17:37–17:38, sin desfase.
4. Editar ese mismo registro (abrir el formulario de edición) y verificar que la hora precargada en los campos de inicio/fin también es 17:37–17:38.

**Resultado esperado**: SC-001.

## OBS-0061 — Etiqueta "Fuera de jornada"

1. Registrar tiempo manualmente en un horario fuera de la jornada laboral configurada del recurso (ej. de madrugada).
2. Abrir el historial de registros de tiempo del ticket.
3. Verificar que la hora de inicio/fin de ese registro es completamente legible.
4. Verificar que la etiqueta "Fuera de jornada" es visible en una posición que no se superpone al horario (columna/badge/tooltip separado).

**Resultado esperado**: SC-002.

## OBS-0062 — Notificación al asignar/reasignar

1. Con un ticket sin resolutor, asignarlo a un Resolutor A desde el Panel de Asignación (Triage Push).
2. Iniciar sesión como Resolutor A (u observar su centro de notificaciones) y confirmar que recibió una notificación de asignación con ticket, cliente, prioridad, estado y quién asignó.
3. Reasignar el mismo ticket a un Resolutor B.
4. Confirmar que el Resolutor B recibe una notificación equivalente (mismo contenido mínimo), y que el Resolutor A no recibe una notificación de "nueva asignación" para un ticket que ya no tiene.
5. Desde el centro de notificaciones, seleccionar la notificación de asignación de cualquiera de los dos resolutores y confirmar que dirige directo al detalle del ticket correspondiente.

**Resultado esperado**: SC-003.

## OBS-0063 — Bloqueo de asignación a usuarios inactivos

1. En Maestros > Equipo, sobre un recurso con rol Resolutor, usar el botón "Desactivar cuenta (acceso)" (deja `Resource.active = true` pero `User.active = false`).
2. Ir al Panel de Asignación (o al detalle de un ticket) y abrir el selector de resolutor: confirmar que ese recurso ya no aparece como opción seleccionable.
3. Intentar una asignación directa contra la API (`POST /api/tickets/{id}/assign` o `/reassign`) con el `assignee_id` de ese recurso: confirmar que la API responde `400 resource_inactive` y no persiste el cambio.
4. Repetir 1-3 usando en cambio "Desactivar recurso (RRHH)" (el caso que ya funcionaba antes de este feature) para confirmar que no hubo regresión.
5. Reactivar la cuenta ("Activar cuenta") y confirmar que el recurso vuelve a aparecer como opción asignable.

**Resultado esperado**: SC-004.

## Cierre de trazabilidad UAT

1. Tras validar los cuatro puntos, actualizar `UAT/02_Backlog/BACKLOG.md`: `OBS-0060` a `OBS-0063` pasan de `Abierta` a `Lista para Validar` (FR-015).
2. Confirmar que `UAT/01_Iterations/ITER-009/ITER-009.md` no fue editado en su contenido narrativo.

**Resultado esperado**: SC-005.
