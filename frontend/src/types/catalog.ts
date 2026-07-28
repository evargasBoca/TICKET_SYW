export type CatalogName = 'tools' | 'processes' | 'resolution-types' | 'record-types' | 'teams' | 'absence-types' | 'access-types'

export interface CatalogItem {
  id: string
  name: string
  active: boolean
  /** Solo presente en catálogos con color estable auto-asignado (ej. access-types, spec 031). */
  color_index?: number
}

export const CATALOG_LABELS: Record<CatalogName, string> = {
  tools: 'Herramientas',
  processes: 'Procesos',
  'resolution-types': 'Tipos de resolución',
  'record-types': 'Tipo de registro',
  teams: 'Equipos de trabajo',
  'absence-types': 'Tipos de ausencia',
  'access-types': 'Tipos de acceso (Clientes)',
}

/** Paleta fija de 8 colores para catálogos con color_index (spec 031, UAT OBS-0041) — el
 * usuario nunca elige el color; se asigna automáticamente en el backend (siguiente libre). */
export const CATALOG_COLOR_PALETTE = [
  '#2d5fa0', '#7a4fa3', '#a06a1f', '#3f8f5a', '#a34a63', '#1f7a6c', '#55608c', '#b0524a',
]

/** Vínculo sugerido Herramienta↔Proceso (OBS-0049) — guía no restrictiva, no un catálogo. */
export interface ToolProcessLink {
  tool_id: string
  process_id: string
}
