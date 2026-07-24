# Data Model: Cierre de observaciones "Abierta" del Backlog UAT

Este feature es mayormente correctivo (lógica y validaciones) sobre entidades ya existentes. Solo hay **un cambio de esquema**: un campo nuevo en `WorkSession`. El resto de entidades se documenta para dejar explícito qué campos ya existentes se usan/exponen, sin crear nada nuevo.

## WorkSession (modificada)

Fuente: `backend/domain/entities/work_session.py`; tabla: `work_sessions` (`backend/infra/models/work_session_model.py`).

| Campo | Tipo | Estado | Notas |
|---|---|---|---|
| `id` | UUID | existente | sin cambios |
| `resource_id` | UUID | existente | sin cambios |
| `ticket_id` | UUID | existente | sin cambios |
| `work_date` | date | existente (fix de cálculo) | US6/FR-021: debe derivarse de la fecha **local** del recurso (timezone del `WorkHourTemplate`/calendario asignado), no de `date.today()` del servidor |
| `duration_minutes` | int | existente | sin cambios |
| `started_at` / `ended_at` | datetime \| None | existente | sin cambios de tipo; se usan para calcular `off_hours` |
| `note` | str \| None | existente | sin cambios |
| `off_hours` | **bool, default `False`** | **NUEVO (US6/FR-020)** | `True` cuando el intervalo `[started_at, ended_at]` (o, si no hay horas explícitas, el propio `work_date`) cae total o parcialmente fuera del horario laboral configurado del recurso a la fecha del registro. Persistido en creación; no se recalcula retroactivamente si el calendario del recurso cambia después. |
| `created_by`, `updated_by`, `created_at`, `updated_at` | existentes | sin cambios | |

**Regla de negocio (FR-020/FR-021)**: el registro se acepta igual (no se bloquea); `off_hours` es puramente informativo/clasificatorio, consumible en reportes (`Reporte de Tiempos`) para filtrar o resaltar tiempo fuera de jornada.

**Migración**: 1 revisión Alembic nueva en `backend/infra/migrations/versions/`, agregando `off_hours BOOLEAN NOT NULL DEFAULT false` a `work_sessions`. Los registros históricos quedan en `False` (no se reclasifican retroactivamente — ver Assumptions del spec).

## Ticket (sin cambios de esquema — solo exposición)

Fuente: `backend/domain/entities/ticket.py`. Campos ya existentes que este feature debe **exponer/consultar** correctamente (US1, FR-005), sin agregar columnas:

| Campo | Uso en este feature |
|---|---|
| `created_at` | "Hora de creación del ticket" (FR-005) |
| `sla_last_resume_at` | "Inicio efectivo del SLA" (FR-005) — también insumo de `sla_service.compute_consumed_seconds` |
| `sla_consumed_seconds`, `sla_phase`, `sla_phase_limit_minutes`, `sla_status` | snapshot de SLA ya persistido/derivado; base de US1 (FR-001, FR-002, FR-003, FR-006) |
| `status` | ya usado por `assert_ticket_open_or_admin`/nuevo chequeo en `TicketTimerService.start()` (US2) |

`AssignmentModel.assigned_at` (`backend/infra/models/ticket_model.py`) — "Hora de asignación" (FR-005), tabla de historial ya existente, no requiere cambios de esquema.

"Inicio de la jornada laboral aplicable" (FR-005) no es un campo persistido: se deriva en el momento de la consulta a partir del calendario/horario del recurso asignado (mismo mecanismo que ya usa `sla_service` para calendario-consciencia), igual que hoy.

## SlaRule (sin cambios de esquema — solo validación)

Fuente: `backend/domain/entities/sla_rule.py`. Se agrega una constante de dominio, no un campo de datos:

```python
SLA_FIELD_MAX_MINUTES = 21600  # 15 días (confirmado con el usuario, OBS-0031)
```

Usada por `_validate_minutes` (`backend/api/routes/sla_rules.py`) y por la regla de validación de `SlaRuleForm.tsx`, para no duplicar el número mágico en dos lugares.

## Estado de validación del título del ticket (regla de dominio, no entidad de datos)

No es una entidad nueva; es una función pura de validación en `TicketService` (US3):

- **Regla "solo espacios"** (FR-011/FR-012): `title.strip()` vacío → rechazo.
- **Regla "sin emojis"** (FR-013): coincidencia contra un conjunto acotado de rangos Unicode de emoji/pictogramas → rechazo si hay match; letras (incl. acentos/ñ), números, espacios y puntuación común quedan permitidos sin restricción adicional.

## Observación UAT (entidad del framework, no de la aplicación)

`OBS-XXXX` en `UAT/02_Backlog/BACKLOG.md` — no es parte del modelo de datos de la aplicación. Este feature debe actualizar el campo `Estado` de `OBS-0029`–`OBS-0040` a `Lista para Validar` al completar cada corrección (FR-022), siguiendo `UAT/CONVENTIONS.md`. No se editan retroactivamente `ITER-004.md` ni `ITER-005.md`.

## Relaciones (sin cambios)

```
clients → projects → task_lists → tasks/tickets (FSM + SLA + comentarios) → subtasks
tickets (1) ── (N) work_sessions   [+ off_hours nuevo]
tickets (1) ── (N) assignments     [assigned_at ya existente]
tickets (1) ── (1) sla snapshot (campos sla_* en el propio Ticket)
resources (1) ── (1) work_hour_template / calendario  [usado por sla_service y por el fix de work_date]
```
