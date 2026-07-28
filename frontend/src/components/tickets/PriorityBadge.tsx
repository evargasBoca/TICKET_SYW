import { PRIORITY_CHIP } from '../../theme'
import { PRIORITY_LABELS, type Priority } from '../../types/ticket'

const SHORT: Record<Priority, string> = { critical: 'P1', high: 'P2', medium: 'P3', low: 'P4' }

/** Badge sólido de prioridad, estilo docs/PROPUESTA_VISUAL.html. OBS-0058: muestra el nombre
 * legible (Crítica/Alta/Media/Baja) por defecto — antes mostraba solo el código corto ("P3") en
 * los listados, inconsistente con el filtro y el formulario, que ya usan la palabra. `full`
 * agrega el código antepuesto ("P3 · Media") para el detalle del ticket. */
export default function PriorityBadge({ priority, full = false }: { priority: Priority; full?: boolean }) {
  const chip = PRIORITY_CHIP[priority]
  return (
    <span
      style={{
        display: 'inline-block', padding: '2px 8px', borderRadius: 4,
        fontSize: 11, fontWeight: 700, letterSpacing: 0.3,
        background: chip.bg, color: chip.text,
      }}
    >
      {full ? `${SHORT[priority]} · ${PRIORITY_LABELS[priority]}` : PRIORITY_LABELS[priority]}
    </span>
  )
}
