"""Vínculo Herramienta-Proceso y permiso tickets:manage_skills (spec 033, UAT OBS-0047/0048/0049)

Revision ID: 048
Revises: 047
Create Date: 2026-07-28

Crea `tool_processes` (M:N administrable desde Catálogos, guía no restrictiva al elegir Proceso
tras elegir Herramienta en el formulario de ticket) y el permiso `tickets:manage_skills`
(Coordinador únicamente) que reemplaza a `tickets:edit` como gate de edición de "Skills
requeridas" del ticket (Admin/QM quedan en solo lectura para ese campo). Mismo patrón de permiso
único-rol que 021_encargado_role_permissions.py.
"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "048"
down_revision = "047"
branch_labels = None
depends_on = None

NEW_PERMISSIONS = {
    ("tickets", "manage_skills"): ["Coordinador"],
}


def upgrade() -> None:
    op.create_table(
        "tool_processes",
        sa.Column("tool_id", UUID(as_uuid=True), sa.ForeignKey("catalog_tools.id"), primary_key=True),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("catalog_processes.id"), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    bind = op.get_bind()
    roles = {r.name: r.id for r in bind.execute(sa.text("SELECT id, name FROM roles")).fetchall()}
    for (module, action), role_names in NEW_PERMISSIONS.items():
        perm_id = uuid.uuid4()
        bind.execute(
            sa.text("INSERT INTO permissions (id, module, action) VALUES (:id, :module, :action)"),
            {"id": str(perm_id), "module": module, "action": action},
        )
        for role_name in role_names:
            if role_name in roles:
                bind.execute(
                    sa.text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:r, :p)"),
                    {"r": str(roles[role_name]), "p": str(perm_id)},
                )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text(
        "DELETE FROM role_permissions WHERE permission_id IN "
        "(SELECT id FROM permissions WHERE module = 'tickets' AND action = 'manage_skills')"
    ))
    bind.execute(sa.text("DELETE FROM permissions WHERE module = 'tickets' AND action = 'manage_skills'"))
    op.drop_table("tool_processes")
