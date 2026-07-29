import apiClient from './apiClient'
import type { ReportFilters, ReportListResponse, ReportSavedView, ReportViewConfig } from '../types/report'

// URLSearchParams (no axios `params` con arrays): igual patrón que ticketService.panel() —
// evita que axios serialice arrays como 'aggregate[]'/'columns[]', que Flask no reconoce
// (request.args.getlist espera la clave repetida sin corchetes).
function filterParams(filters: ReportFilters): URLSearchParams {
  const params = new URLSearchParams()
  if (filters.date_from) params.append('date_from', filters.date_from)
  if (filters.date_to) params.append('date_to', filters.date_to)
  if (filters.client_id) params.append('client_id', filters.client_id)
  if (filters.project_id) params.append('project_id', filters.project_id)
  if (filters.assignee_id) params.append('assignee_id', filters.assignee_id)
  return params
}

export const reportService = {
  listTickets: (filters: ReportFilters, page: number, pageSize: number, aggregate?: string[]) => {
    const params = filterParams(filters)
    params.append('page', String(page))
    params.append('page_size', String(pageSize))
    aggregate?.forEach(a => params.append('aggregate', a))
    return apiClient.get<ReportListResponse>(`/api/reports/tickets?${params}`).then(r => r.data)
  },

  exportTickets: (filters: ReportFilters, columns: string[]) => {
    const params = filterParams(filters)
    columns.forEach(c => params.append('columns', c))
    return apiClient.get(`/api/reports/tickets/export?${params}`, { responseType: 'blob' }).then(r => r.data as Blob)
  },

  listViews: () =>
    apiClient.get<{ items: ReportSavedView[] }>('/api/reports/views').then(r => r.data.items),

  saveView: (name: string, config: ReportViewConfig) =>
    apiClient.post<ReportSavedView>('/api/reports/views', { name, config }).then(r => r.data),

  deleteView: (viewId: string) =>
    apiClient.delete<void>(`/api/reports/views/${viewId}`).then(r => r.data),
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}
