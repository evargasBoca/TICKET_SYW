import { Select } from 'antd'
import { SortAscendingOutlined, SortDescendingOutlined } from '@ant-design/icons'

const SORT_OPTIONS = [
  { value: 'urgency', label: 'Prioridad (sugerido)' },
  { value: 'created_at', label: 'Fecha ↑' },
  { value: '-created_at', label: 'Fecha ↓' },
  { value: 'priority', label: 'Prioridad ↑' },
  { value: '-priority', label: 'Prioridad ↓' },
  { value: 'code', label: 'Código ↑' },
  { value: '-code', label: 'Código ↓' },
  { value: 'status', label: 'Estado ↑' },
  { value: '-status', label: 'Estado ↓' },
]

interface SortIndicatorProps {
  value: string
  onChange: (value: string) => void
}

/** spec 035 (US3/FR-008): reemplaza el indicador fijo de OBS-0028 ("por ahora fijo") por un
 * selector real de ordenamiento explícito (fecha/prioridad/código/estado, asc/desc),
 * combinable con los filtros existentes de cada pantalla. */
export default function SortIndicator({ value, onChange }: SortIndicatorProps) {
  return (
    <Select
      value={value}
      onChange={onChange}
      options={SORT_OPTIONS}
      style={{ width: 200 }}
      suffixIcon={value.startsWith('-') ? <SortDescendingOutlined /> : <SortAscendingOutlined />}
    />
  )
}
