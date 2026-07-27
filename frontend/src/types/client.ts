export interface ClientListItem {
  id: string
  name: string
  slug: string
  active: boolean
  contact_name: string | null
  contact_email: string | null
  contact_phone: string | null
  annual_billing_usd: number | null
  /** Huso horario IANA del calendario del cliente (Fase 5), ej. "America/Bogota". */
  timezone: string | null
  /** País de residencia, ISO 3166-1 alpha-2 (Fase 5), ej. "CO". */
  country: string | null
  created_at: string
  updated_at: string
}

export interface ClientDetail extends ClientListItem {
  notes: string | null
}

export interface ClientFormData {
  name: string
  contact_name?: string | null
  contact_email?: string | null
  contact_phone?: string | null
  annual_billing_usd?: number | null
  notes?: string | null
  timezone?: string | null
  country?: string | null
}

export interface ClientSystem {
  id: string
  client_id: string
  system_type: string
  brand: string
  version: string | null
  notes: string | null
  created_at: string
}

export interface ClientSystemFormData {
  system_type: string
  brand: string
  version?: string | null
  notes?: string | null
}

/** Tipo de acceso resuelto (spec 031, UAT OBS-0041) — id de catalog_access_types + nombre y
 * color estable, embebido de solo lectura en la respuesta del acceso. */
export interface AccessTypeCatalogItem {
  id: string
  name: string
  active: boolean
  color_index: number
}

export type ClientAccessEnvironment = 'dev' | 'test' | 'prod'

export interface ClientAccess {
  id: string
  client_id: string
  /** UUID del tipo en catalog_access_types (spec 031 — reemplaza el enum fijo de spec 018). */
  access_type_id: string
  /** Tipo resuelto de solo lectura (nombre + color), para no requerir un segundo round-trip. */
  access_type: AccessTypeCatalogItem
  /** Aplica a cualquier tipo de acceso desde spec 031 (antes solo a "URL de sistema"). */
  environment: ClientAccessEnvironment | null
  /** Puerto propio del acceso, separado del host (spec 031). */
  port: number | null
  host: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ClientAccessFormData {
  access_type_id: string
  environment?: ClientAccessEnvironment | null
  port?: number | null
  host?: string | null
  notes?: string | null
}

/** Credencial (usuario/contraseña) de un acceso — 1 acceso puede tener N credenciales
 * (spec 031, UAT OBS-0041), reemplaza username/password embebidos en ClientAccess (spec 018). */
export interface ClientAccessCredential {
  id: string
  client_access_id: string
  label: string | null
  username: string | null
  password: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ClientAccessCredentialFormData {
  label?: string | null
  username?: string | null
  password?: string | null
  notes?: string | null
}

export interface ClientAccessAttachment {
  id: string
  client_id: string
  /** Acceso al que está anclado el adjunto; null = adjunto general del cliente (spec 031). */
  client_access_id: string | null
  filename: string
  content_type: string
  size_bytes: number
  created_at: string
}
