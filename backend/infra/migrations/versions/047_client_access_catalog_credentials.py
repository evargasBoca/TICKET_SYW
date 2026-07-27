"""Ampliación de Accesos y Conexiones del Cliente (spec 031, UAT OBS-0041)

Revision ID: 047
Revises: 046
Create Date: 2026-07-27

Crea `catalog_access_types` (catálogo administrable que reemplaza el enum fijo de
`client_access.access_type`, con color estable auto-asignado) y `client_access_credentials`
(1 acceso ──< N credenciales, reemplaza username/password embebidos en `client_access`);
agrega `client_access.port` y `client_access_attachments.client_access_id` (FK opcional).
Migra automáticamente los datos ya cargados (tipo legacy → catálogo, username/password →
primera credencial) sin eliminar ninguna columna legacy (research.md Decisiones 3-6).
"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "047"
down_revision = "046"
branch_labels = None
depends_on = None

# Orden fijo -> color_index 0-4 (research.md Decisión 3)
ACCESS_TYPE_SEEDS = ["VPN", "Base de datos", "Servidor / instancia", "Escritorio remoto", "Sistema / Integración"]

# Mapeo del enum legacy de client_access.access_type al nombre del catálogo nuevo
LEGACY_TYPE_MAP = {
    "vpn": "VPN",
    "system_url": "Sistema / Integración",
    "remote_desktop": "Escritorio remoto",
}


def upgrade() -> None:
    bind = op.get_bind()

    op.create_table(
        "catalog_access_types",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("color_index", sa.SmallInteger(), nullable=False),
    )

    name_to_id: dict[str, str] = {}
    for index, name in enumerate(ACCESS_TYPE_SEEDS):
        new_id = str(uuid.uuid4())
        name_to_id[name] = new_id
        bind.execute(
            sa.text("INSERT INTO catalog_access_types (id, name, color_index) VALUES (:id, :name, :color_index)"),
            {"id": new_id, "name": name, "color_index": index},
        )

    # access_type queda legacy (spec 031) — se relaja de NOT NULL+CHECK(enum) a nullable libre,
    # ya no se alimenta desde altas nuevas (reemplazado por access_type_id).
    op.drop_constraint("ck_client_access_type", "client_access", type_="check")
    op.alter_column("client_access", "access_type", nullable=True)

    op.add_column("client_access", sa.Column("access_type_id", UUID(as_uuid=True), nullable=True))
    op.add_column("client_access", sa.Column("port", sa.Integer(), nullable=True))

    for legacy_type, catalog_name in LEGACY_TYPE_MAP.items():
        bind.execute(
            sa.text("UPDATE client_access SET access_type_id = :type_id WHERE access_type = :legacy_type"),
            {"type_id": name_to_id[catalog_name], "legacy_type": legacy_type},
        )

    op.create_foreign_key(
        "fk_client_access_access_type_id", "client_access", "catalog_access_types", ["access_type_id"], ["id"],
    )
    op.alter_column("client_access", "access_type_id", nullable=False)

    op.create_table(
        "client_access_credentials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("client_access_id", UUID(as_uuid=True), sa.ForeignKey("client_access.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("password", sa.LargeBinary(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_client_access_credentials_access_id", "client_access_credentials", ["client_access_id"])

    op.execute("ALTER TABLE client_access_credentials ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY client_access_credentials_app_access ON client_access_credentials "
        "USING (current_setting('app.authenticated', true) IS NOT DISTINCT FROM 'true' "
        "OR current_user = 'sywork_user')"
    )

    # Migración de datos: cada client_access con username/password ya cargados -> 1a credencial
    # (blob cifrado copiado tal cual, sin desencriptar/reencriptar — research.md Decisión 4)
    bind.execute(sa.text(
        "INSERT INTO client_access_credentials (id, client_access_id, label, username, password) "
        "SELECT gen_random_uuid(), id, 'Principal', username, password FROM client_access "
        "WHERE username IS NOT NULL OR password IS NOT NULL"
    ))

    # ON DELETE SET NULL (no CASCADE): al eliminar un acceso, el adjunto no se borra, vuelve a
    # ser un adjunto general del cliente (edge case de spec.md — mismo criterio ya vigente).
    op.add_column(
        "client_access_attachments",
        sa.Column("client_access_id", UUID(as_uuid=True), sa.ForeignKey("client_access.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("client_access_attachments", "client_access_id")

    op.execute("DROP POLICY IF EXISTS client_access_credentials_app_access ON client_access_credentials")
    op.execute("ALTER TABLE client_access_credentials DISABLE ROW LEVEL SECURITY")
    op.drop_table("client_access_credentials")

    op.drop_constraint("fk_client_access_access_type_id", "client_access", type_="foreignkey")
    op.drop_column("client_access", "access_type_id")
    op.drop_column("client_access", "port")

    op.execute("UPDATE client_access SET access_type = 'vpn' WHERE access_type IS NULL OR access_type = ''")
    op.alter_column("client_access", "access_type", nullable=False)
    op.create_check_constraint(
        "ck_client_access_type", "client_access",
        "access_type IN ('vpn','system_url','remote_desktop')")

    op.drop_table("catalog_access_types")
