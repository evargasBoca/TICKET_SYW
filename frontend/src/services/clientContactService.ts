import apiClient from './apiClient'
import type { PaginatedResponse } from '../types/api'
import type { ClientContact, ClientContactCreateRequest, ClientContactCreateResponse } from '../types/clientContact'
import type { ProjectListItem } from '../types/project'

export const clientContactService = {
  list: (params?: { client_id?: string; project_id?: string; email?: string; username?: string; active?: boolean; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<ClientContact>>('/api/client-contacts', { params }).then(r => r.data),

  // Spec 034 (US1): activar/desactivar la cuenta de un Usuario/cliente
  setActive: (contactId: string, active: boolean) =>
    apiClient.patch<{ id: string; active: boolean }>(
      `/api/client-contacts/${contactId}/active`, { active }).then(r => r.data),

  create: (data: ClientContactCreateRequest) =>
    apiClient.post<ClientContactCreateResponse>('/api/client-contacts', data).then(r => r.data),

  // Spec 010 (US2): proyectos vinculados del Usuario/cliente autenticado (autoservicio)
  myProjects: () =>
    apiClient.get<{ items: ProjectListItem[]; total: number }>('/api/client-contacts/me/projects').then(r => r.data),

  // Spec 015 (US2): agregar/quitar Proyectos de un Usuario/cliente ya existente
  addProject: (contactId: string, projectId: string) =>
    apiClient.post<{ id: string; project_id: string; name: string }>(
      `/api/client-contacts/${contactId}/projects`, { project_id: projectId }).then(r => r.data),

  removeProject: (contactId: string, projectId: string) =>
    apiClient.delete<void>(`/api/client-contacts/${contactId}/projects/${projectId}`).then(r => r.data),
}
