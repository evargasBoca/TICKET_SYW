import apiClient from './apiClient'
import type { Timer } from '../types/timer'

export const timerService = {
  /** OBS-0050: usuarios sin recurso asociado (Admin/Coordinador/QM) reciben `no_resource_profile`
   * (400) al consultar — es un resultado esperado para ellos, no un error a mostrar como toast
   * (ver `TicketTimerWidget`, que lo maneja localmente ocultando el cronómetro). */
  getCurrent: () =>
    apiClient.get<Timer>('/api/timer', { headers: { 'X-Skip-Error-Notify': 'true' } }).then(r => r.data),

  start: (ticketId: string) =>
    apiClient.post<Timer>('/api/timer/start', { ticket_id: ticketId }).then(r => r.data),

  pause: () =>
    apiClient.post<Timer>('/api/timer/pause').then(r => r.data),

  resume: () =>
    apiClient.post<Timer>('/api/timer/resume').then(r => r.data),

  finish: (note?: string) =>
    apiClient.post('/api/timer/finish', note ? { note } : {}).then(r => r.data),
}
