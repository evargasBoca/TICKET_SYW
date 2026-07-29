export interface ReportRow {
  ticket_id: string
  ticket_number: number
  title: string
  status: string
  priority: string
  created_at: string
  client_id: string | null
  client_name: string | null
  project_id: string | null
  project_name: string | null
  assignee_id: string | null
  assignee_name: string | null
  tool_name: string | null
  process_name: string | null
  skills: string[]
  time_to_first_contact_seconds: number | null
  execution_time_seconds: number | null
  total_logged_minutes: number
}

export interface ReportFilters {
  date_from?: string
  date_to?: string
  client_id?: string
  project_id?: string
  assignee_id?: string
}

export type ReportAggregateFunction = 'sum' | 'avg' | 'count'

/** Columnas sobre las que FR-011 permite aplicar una función de agregación. */
export type ReportAggregatableColumn = 'time_to_first_contact_seconds' | 'execution_time_seconds' | 'total_logged_minutes' | 'ticket_id'

export interface ReportAggregateRequest {
  column: ReportAggregatableColumn
  function: ReportAggregateFunction
}

export type ReportAggregateResult = Record<string, Partial<Record<ReportAggregateFunction, number>>>

export interface ReportListResponse {
  items: ReportRow[]
  total: number
  page: number
  page_size: number
  aggregates?: ReportAggregateResult
}

export interface ReportColumnConfig {
  key: string
  visible: boolean
}

/** Config guardada en una Vista Personalizada (data-model.md). */
export interface ReportViewConfig {
  columns: ReportColumnConfig[]
  column_order: string[]
  filters: ReportFilters
  aggregations: ReportAggregateRequest[]
}

export interface ReportSavedView {
  id: string
  name: string
  config: ReportViewConfig
  updated_at: string
}
