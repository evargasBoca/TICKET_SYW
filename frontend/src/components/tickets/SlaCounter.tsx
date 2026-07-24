import { Tag, Tooltip } from 'antd'
import { palette, vivid } from '../../theme'
import type { TicketSlaState } from '../../types/sla'

interface SlaCounterProps {
  sla: TicketSlaState
  /** OBS-0032 (spec 028): si el ticket todavía no tiene resolutor asignado, el conteo de la
   * fase Contacto ya está corriendo a nivel de dominio (wall-clock, FR-004/FR-005 spec 014),
   * pero mostrarlo como "Corriendo" da la falsa impresión de que alguien ya está trabajando en
   * él. Sin este dato, se asume que sí hay asignado (comportamiento actual, sin cambios). */
  hasAssignee?: boolean
}

const PHASE_LABELS: Record<string, string> = {
  contacto: 'Contacto',
  ejecucion: 'Diagnóstico, Análisis y Ejecución',
  cerrado: 'Cerrado',
}

const STATUS_LABELS: Record<TicketSlaState['status'], string> = {
  sin_sla: 'Sin SLA configurado',
  corriendo: 'Corriendo',
  pausado: 'Pausado',
  vencido: 'Vencido',
  detenido: 'Detenido',
}

/** Ver `hasAssignee` — mismo criterio visual, distinto de `STATUS_LABELS.corriendo`. */
const PENDING_ASSIGNMENT_LABEL = 'Pendiente de asignación'

const CONTACT_RESULT_LABELS: Record<string, string> = {
  pendiente: 'Pendiente', cumplido: 'Cumplido', vencido: 'Vencido',
}

function formatDuration(totalSeconds: number): string {
  const totalMinutes = Math.floor(totalSeconds / 60)
  const h = Math.floor(totalMinutes / 60)
  const m = totalMinutes % 60
  return h > 0 ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`
}

function statusColor(status: TicketSlaState['status']): string {
  switch (status) {
    case 'vencido': return vivid.red.text
    case 'pausado': return vivid.orange.text
    case 'corriendo': return palette.green600
    case 'detenido': return palette.slate500
    default: return palette.slate400
  }
}

/** Reemplaza el placeholder `—:—:—` / "Próximamente · Fase 4" del detalle del ticket
 * (Historia 2, spec 014). Muestra la fase vigente, el tiempo consumido/límite, el estado del
 * contador, y — una vez superada — el resultado congelado de la fase Contacto (FR-007). */
export default function SlaCounter({ sla, hasAssignee = true }: SlaCounterProps) {
  const isPendingAssignment = !hasAssignee && sla.phase === 'contacto' && sla.status === 'corriendo'

  if (sla.status === 'sin_sla' || sla.phase_limit_minutes == null) {
    return (
      <>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
          <span style={{ fontSize: 22, fontWeight: 700, color: palette.slate400 }}>—:—:—</span>
          <Tag>Sin SLA configurado</Tag>
        </div>
        <div style={{ height: 6, background: palette.slate200, borderRadius: 3, marginBottom: 6 }}>
          <div style={{ height: 6, borderRadius: 3, background: palette.slate300, width: '0%' }} />
        </div>
        <div style={{ fontSize: 11, color: palette.slate400 }}>
          Este Proyecto/Prioridad no tiene una regla de SLA configurada.
        </div>
      </>
    )
  }

  const consumedMinutes = sla.consumed_seconds / 60
  const pct = Math.min(100, Math.round((consumedMinutes / sla.phase_limit_minutes) * 100))
  const color = isPendingAssignment ? palette.slate400 : statusColor(sla.status)

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
        <span style={{ fontSize: 22, fontWeight: 700, color }}>
          {formatDuration(sla.consumed_seconds)}
          <span style={{ fontSize: 14, fontWeight: 400, color: palette.slate400 }}>
            {' / '}{formatDuration(sla.phase_limit_minutes * 60)}
          </span>
        </span>
        <Tooltip title={isPendingAssignment
          ? 'El conteo de Contacto inicia con la creación del ticket, pero todavía no tiene un resolutor asignado trabajando en él'
          : (PHASE_LABELS[sla.phase ?? ''] ?? sla.phase)}>
          <Tag color={sla.status === 'vencido' ? 'red' : undefined}>
            {isPendingAssignment ? PENDING_ASSIGNMENT_LABEL : STATUS_LABELS[sla.status]}
          </Tag>
        </Tooltip>
      </div>
      <div style={{ height: 6, background: palette.slate200, borderRadius: 3, marginBottom: 6 }}>
        <div style={{ height: 6, borderRadius: 3, background: color, width: `${pct}%` }} />
      </div>
      <div style={{ fontSize: 11, color: palette.slate400 }}>
        Fase: {PHASE_LABELS[sla.phase ?? ''] ?? sla.phase}
        {sla.contact_result && sla.contact_result !== 'pendiente' && (
          <>
            {' · '}Contacto: <strong>{CONTACT_RESULT_LABELS[sla.contact_result]}</strong>
            {sla.contact_consumed_seconds != null && ` (${formatDuration(sla.contact_consumed_seconds)})`}
          </>
        )}
      </div>
    </>
  )
}
