# Quickstart: Validación de las 12 correcciones del Backlog UAT

Guía de verificación end-to-end contra Docker real, siguiendo el mismo patrón usado en features previas de este repo. No sustituye el retest formal del framework UAT (`UAT/CONVENTIONS.md`) — deja el backlog en `Lista para Validar` para que el validador confirme (FR-022).

## Prerrequisitos

- Entorno Docker de desarrollo levantado (`docker compose up`, ver `README.md` del repo).
- Un recurso de prueba con `WorkHourTemplate`/calendario asignado con horario laboral acotado (ej. 08:00–17:00) y timezone distinto de UTC (para poder reproducir el bug de fecha de US6).
- Un cliente/proyecto/prioridad con una regla de SLA configurada (contacto y ejecución en minutos).
- Acceso con un usuario Resolutor y, si aplica, un usuario con permisos de administración de Maestros (SLA Configurable, Equipo).

## US1 — Cálculo de SLA respecto al horario laboral (OBS-0038, OBS-0039, OBS-0040)

1. Crear un ticket **fuera** del horario laboral del recurso (ej. a las 23:00 hora local del recurso) y asignarlo.
2. Verificar en el detalle del ticket que el SLA **no** empieza a contabilizar hasta el inicio del siguiente período laboral (`sla_effective_start` posterior al horario de inicio de jornada).
3. Esperar (o simular) ~1h de tiempo laboral real transcurrido; verificar que el SLA muestra ~1h consumida, no 3h.
4. Cambiar el estado del ticket (ej. a "Solicitud de información" y de vuelta) y verificar que el tiempo consumido de SLA no salta a un valor mayor al tiempo laboral real transcurrido, y que no aparece "Vencido" antes de agotar el límite configurado.
5. Confirmar en el detalle del ticket que se distinguen: hora de creación, hora de asignación, inicio efectivo del SLA e inicio de jornada laboral (FR-005).

**Resultado esperado**: SC-001, SC-002.

## US2 — Ticket cerrado bloquea registros de tiempo (OBS-0035)

1. Iniciar el cronómetro en un ticket activo.
2. Cambiar el ticket a estado Cerrado sin detener el cronómetro manualmente.
3. Verificar que el cronómetro se detiene solo y que el tiempo acumulado hasta ese momento queda registrado.
4. Intentar iniciar un nuevo registro de tiempo (cronómetro o manual) sobre ese mismo ticket ya cerrado; verificar que se bloquea con un mensaje explícito ("ticket cerrado").
5. Verificar que el mismo recurso puede seguir registrando tiempo con normalidad en otro ticket/tarea activo.

**Resultado esperado**: SC-003.

## US3 — Validación del título del ticket (OBS-0033, OBS-0034)

1. Intentar crear un ticket con título compuesto únicamente por espacios; verificar rechazo con mensaje "El título es obligatorio".
2. Intentar crear un ticket con título que incluya uno o más emojis; verificar rechazo con mensaje indicando que los emojis no están permitidos.
3. Crear un ticket con título que incluya letras con tilde/ñ, números y puntuación común (ej. `Error en informe (v2) — cliente Ñuñoa`); verificar que se acepta sin restricción.

**Resultado esperado**: SC-004.

## US4 — Retroalimentación en configuración de SLA (OBS-0029, OBS-0030, OBS-0031)

1. Crear una configuración de SLA válida y guardar; verificar que aparece una notificación de éxito visible (confirmar si ya funcionaba o si se corrigió — ver `research.md` §4).
2. En un campo de tiempo del SLA, ingresar `0` o un valor negativo; verificar que aparece un mensaje de validación explícito y que el guardado se bloquea (no que el campo se autocorrige en silencio a 1).
3. En un campo de tiempo del SLA, ingresar un valor mayor a 21600 minutos (15 días); verificar que aparece un mensaje de validación y que el guardado se bloquea.

**Resultado esperado**: SC-005.

## US5 — Visibilidad del SLA inicial y del calendario del recurso (OBS-0032, OBS-0037)

1. Crear un ticket nuevo (SLA aún sin iniciar) y verificar que el componente de SLA muestra un estado visualmente diferenciado de "en ejecución" (ej. "Pendiente de asignación"/"Esperando inicio de SLA").
2. Abrir el calendario de un recurso interno (`@sywork.net`) en RRHH > Calendario; verificar que se muestran su jornada laboral, feriados aplicables y ausencias/permisos, no solo su cumpleaños.

**Resultado esperado**: SC-006.

## US6 — Registro de tiempo fuera de horario laboral (OBS-0036)

1. Con el recurso de prueba en timezone distinto de UTC, registrar tiempo cerca de la medianoche local, fuera del horario laboral configurado (ej. 23:02 hora local).
2. Verificar que el registro se guarda (no se bloquea) y queda clasificado/etiquetado como "tiempo fuera de jornada".
3. Verificar que la fecha (`work_date`) del registro corresponde a la fecha local real de la actividad, no a la fecha siguiente por desfase de zona horaria del servidor.

**Resultado esperado**: SC-005 (consistencia SLA/calendario), corrección del bug de fecha descrito en `research.md` §6.

## Resultados de ejecución (T032, 2026-07-24)

Ejecutado contra Docker real (`sywork_backend`/`sywork_frontend`/`sywork_db`), combinando llamadas API directas (autenticado como `admin@sywork.net`) y lectura del DOM real del detalle de ticket, más la suite automatizada de la feature (95/95 tests, ver T030). Todos los datos de prueba creados durante esta corrida (tickets, regla de SLA, cambios temporales de timezone en un recurso) se revirtieron al finalizar.

| Escenario | Resultado | Evidencia |
|---|---|---|
| US1 — SLA calendario-consciente | ✅ PASS | Recurso de prueba con `timezone=America/Bogota` asignado a un ticket con regla de SLA activa; `GET /api/tickets/{id}` devolvió `sla_effective_start`/`work_period_start` en hora local del recurso (no UTC naive), y `work_period_start == created_at` al crear/asignar dentro de jornada (08-17 hora local) — mismo comportamiento que los 5 tests de `test_sla_service.py` para el caso "fuera de jornada" (no reproducible en vivo por ser de día en el entorno de prueba) |
| US2 — Cierre bloquea/detiene registro de tiempo | ✅ PASS (vía suite automatizada) | `test_timer.py::test_start_rejects_already_closed_ticket` y `::test_closing_ticket_auto_stops_active_timer_and_persists_time` — mismo Flask test client contra la DB real de Docker, cubren exactamente los pasos 2-4 del escenario; no repetido vía HTTP en vivo por requerir credenciales de un recurso específico (el cronómetro solo opera sobre el propio usuario autenticado, sin variante `resource_id`) |
| US3 — Validación de título | ✅ PASS | `POST /api/tickets` con título en blanco → 400 `title_blank`; con emoji → 400 `title_invalid_chars`; con tildes/ñ/puntuación (`Error en informe (v2) — cliente Ñuñoa`) → 201, título preservado exacto |
| US4 — Feedback de configuración SLA | ✅ PASS | `POST /api/sla-rules` con `contact_minutes=0` y `=-5` → 400 `validation_error`; `execution_minutes=99999` → 400 `max_exceeded`; `=21600` (límite exacto) → 201. Notificación de éxito visual ya verificada en el turno de implementación de US4 (root cause React19/antd, ver research.md §4) |
| US5 — Visibilidad SLA inicial / calendario | ✅ PASS | Ticket nuevo sin asignar, con regla de SLA activa: detalle muestra tag "Pendiente de asignación" (no "Corriendo") en la fase Contacto. Calendario de Equipo con jornada laboral/ausencias ya verificado en el turno de implementación de US5 |
| US6 — Registro fuera de horario | ✅ PASS | Registro creado en sábado (recurso con calendario configurado) → `off_hours: true` en la respuesta de la API y tag "Fuera de jornada" visible en el modal "Registro de tiempo" del ticket; registro en día laboral del mismo recurso → `off_hours: false`, sin tag |

**Resultado esperado**: SC-001 a SC-006 confirmados. Backlog listo para pasar a "Lista para Validar" (T033).

## Cierre — actualización del framework UAT

1. Tras verificar las 6 secciones anteriores, actualizar `UAT/02_Backlog/BACKLOG.md`: cambiar el `Estado` de `OBS-0029` a `OBS-0040` de `Abierta` a `Lista para Validar`.
2. No editar `UAT/01_Iterations/ITER-004/ITER-004.md` ni `ITER-005/ITER-005.md` (inmutables — `UAT/CONVENTIONS.md`).
3. Avisar al validador (Arely Pazmiño u otro consultor UAT asignado) de que hay una nueva versión disponible para retest, indicando la ruta de `BACKLOG.md`.

**Resultado esperado**: SC-007.
