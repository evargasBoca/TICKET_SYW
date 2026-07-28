import type { Priority } from './ticket'

/** Tope máximo por campo de tiempo del SLA (spec 028, OBS-0031) — mismo valor que
 * `SLA_FIELD_MAX_MINUTES` en `backend/domain/entities/sla_rule.py` (15 días); mantener en
 * sincronía si cambia. */
export const SLA_FIELD_MAX_MINUTES = 15 * 24 * 60

export interface SlaRule {
  id: string
  project_id: string
  project_name: string | null
  /** OBS-0043 (spec 030): cliente del proyecto, para distinguir proyectos homónimos de distintos clientes. */
  client_id: string | null
  client_name: string | null
  priority: Priority
  contact_minutes: number
  execution_minutes: number
  active: boolean
  created_at: string
}

export interface SlaRuleFormData {
  project_id: string
  priority: Priority
  contact_minutes: number
  execution_minutes: number
}

export interface SlaRulePatchData {
  contact_minutes?: number
  execution_minutes?: number
  active?: boolean
}

/** Bloque `sla` expuesto en el detalle/listado de tickets (Historia 2/3, aún no consumido en
 * esta entrega — se agrega ya para que TicketDetailPage/TicketsPage lo tipen sin `any`). */
export type SlaPhase = 'contacto' | 'ejecucion' | 'cerrado'
export type SlaStatus = 'sin_sla' | 'corriendo' | 'pausado' | 'vencido' | 'detenido'
export type SlaContactResult = 'pendiente' | 'cumplido' | 'vencido'
/** OBS-0059 (spec 033): análogo a `SlaContactResult` pero para la fase Ejecución/cierre — se
 * congela solo al cerrar/resolver/cancelar (nunca queda en 'pendiente', a diferencia de Contacto). */
export type SlaExecutionResult = 'cumplido' | 'vencido'
/** Motivo de la pausa (spec 022, motor de SLA dinámico) — `null` si `status != 'pausado'`;
 * `'ticket_status'` si la pausa es por estado del ticket (comportamiento ya existente);
 * `'outside_hours' | 'holiday' | 'absence'` si es por disponibilidad real del recurso asignado. */
export type SlaPauseReason = 'outside_hours' | 'holiday' | 'absence' | 'ticket_status' | null

export interface TicketSlaState {
  phase: SlaPhase | null
  status: SlaStatus
  phase_limit_minutes: number | null
  consumed_seconds: number
  rule_id: string | null
  contact_result?: SlaContactResult | null
  contact_consumed_seconds?: number | null
  execution_result?: SlaExecutionResult | null
  execution_consumed_seconds?: number | null
  pause_reason?: SlaPauseReason
}
