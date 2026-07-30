import apiClient from './apiClient'
import type { CatalogItem, CatalogName, ToolProcessLink } from '../types/catalog'

export const catalogService = {
  list: (catalog: CatalogName, active: 'true' | 'false' | 'all' = 'true') =>
    apiClient.get<{ items: CatalogItem[]; total: number }>(
      `/api/catalogs/${catalog}`, { params: { active } }).then(r => r.data),

  create: (catalog: CatalogName, name: string) =>
    apiClient.post<CatalogItem>(`/api/catalogs/${catalog}`, { name }).then(r => r.data),

  /** spec 035 (US5): renombra un registro existente, preservando su id y referencias. */
  rename: (catalog: CatalogName, id: string, name: string) =>
    apiClient.patch<CatalogItem>(`/api/catalogs/${catalog}/${id}`, { name }).then(r => r.data),

  deactivate: (catalog: CatalogName, id: string) =>
    apiClient.patch<CatalogItem>(`/api/catalogs/${catalog}/${id}/deactivate`).then(r => r.data),

  activate: (catalog: CatalogName, id: string) =>
    apiClient.patch<CatalogItem>(`/api/catalogs/${catalog}/${id}/activate`).then(r => r.data),

  /** OBS-0049: vínculos sugeridos Herramienta↔Proceso, administrables desde Catálogos. */
  listToolProcesses: () =>
    apiClient.get<{ items: ToolProcessLink[]; total: number }>('/api/catalogs/tool-processes').then(r => r.data),

  linkToolProcess: (toolId: string, processId: string) =>
    apiClient.post<ToolProcessLink>('/api/catalogs/tool-processes', { tool_id: toolId, process_id: processId })
      .then(r => r.data),

  unlinkToolProcess: (toolId: string, processId: string) =>
    apiClient.delete(`/api/catalogs/tool-processes/${toolId}/${processId}`),
}
