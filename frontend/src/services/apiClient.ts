import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import { notifyApiError } from './errorNotifier'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:5000',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error)) {
      // OBS-0044: un 401 sin Authorization adjunto (ej. POST /api/auth/login con credenciales
      // inválidas) es un resultado de negocio esperado, no una sesión expirada — antes se
      // forzaba igual el redirect a /login (window.location.href), recargando la página entera
      // antes de que el propio LoginPage pudiera mostrar su aviso ("la página solo parece
      // refrescarse"). Solo se trata como sesión inválida/expirada un 401 que sí llevaba token.
      const hadAuthHeader = Boolean(error.config?.headers?.Authorization)
      if (error.response?.status === 401 && hadAuthHeader) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      } else if (error.response?.status !== 401 && error.config?.headers?.['X-Skip-Error-Notify'] !== 'true') {
        // Escape hatch para probes esperados (ej. ¿soy Jefe de alguien? — un 403 es un
        // resultado normal, no un error que deba interrumpir al usuario con un toast).
        notifyApiError(error)
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
