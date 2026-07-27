from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
import re


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


@dataclass
class ClientSystem:
    """Sistema de software que posee el cliente (FR-029, SDD V3)."""
    id: uuid.UUID
    client_id: uuid.UUID
    system_type: str
    brand: str
    version: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, client_id: uuid.UUID, system_type: str, brand: str, **kwargs) -> "ClientSystem":
        return cls(id=uuid.uuid4(), client_id=client_id, system_type=system_type, brand=brand, **kwargs)


ACCESS_ENVIRONMENTS = ("dev", "test", "prod")


@dataclass
class ClientAccess:
    """Acceso/conexión de un cliente: VPN, URL de sistema, escritorio remoto, base de datos,
    servidor/instancia, etc. (spec 018 — reemplaza a los campos simples vpn_ips/vpn_credentials,
    UAT OBS-0001; spec 031 — access_type_id/port, UAT OBS-0041). El tipo es una FK al catálogo
    administrable `catalog_access_types`, no un enum fijo; environment aplica a cualquier tipo."""
    id: uuid.UUID
    client_id: uuid.UUID
    access_type_id: uuid.UUID
    environment: Optional[str] = None
    port: Optional[int] = None
    host: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, client_id: uuid.UUID, access_type_id: uuid.UUID, **kwargs) -> "ClientAccess":
        return cls(id=uuid.uuid4(), client_id=client_id, access_type_id=access_type_id, **kwargs)


@dataclass
class ClientAccessCredential:
    """Credencial (usuario/contraseña) de un acceso de cliente — 1 acceso puede tener N
    credenciales (spec 031, UAT OBS-0041): un mismo host/URL compartido por varios usuarios,
    cada uno con su propia credencial, sin repetir el acceso."""
    id: uuid.UUID
    client_access_id: uuid.UUID
    label: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, client_access_id: uuid.UUID, **kwargs) -> "ClientAccessCredential":
        return cls(id=uuid.uuid4(), client_access_id=client_access_id, **kwargs)


@dataclass
class ClientAccessAttachment:
    """Archivo adjunto a la sección de accesos y conexiones de un cliente (spec 018); opcionalmente
    anclado a un acceso puntual vía client_access_id (spec 031, UAT OBS-0041) — NULL = adjunto
    general del cliente, comportamiento sin cambios."""
    id: uuid.UUID
    client_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    client_access_id: Optional[uuid.UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Client:
    id: uuid.UUID
    name: str
    slug: str
    active: bool = True
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    vpn_ips: Optional[str] = None
    vpn_credentials: Optional[str] = None
    annual_billing_usd: Optional[float] = None
    notes: Optional[str] = None
    # Calendario del cliente (Fase 5, spec 020): huso horario y país de residencia, usados
    # para resaltar festivos en su calendario (FR-001/FR-004).
    timezone: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, name: str, **kwargs) -> "Client":
        return cls(id=uuid.uuid4(), name=name, slug=_slugify(name), **kwargs)

    def deactivate(self) -> None:
        self.active = False
        self.updated_at = datetime.utcnow()
