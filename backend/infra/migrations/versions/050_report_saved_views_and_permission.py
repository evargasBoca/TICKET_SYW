"""Vistas Personalizadas de Reporte y permiso reports:view (spec 034)

Revision ID: 050
Revises: 049
Create Date: 2026-07-29

Crea `report_saved_views` (config de columnas/filtros/agregaciones guardada por usuario, privada
via user_id) y el permiso `reports:view` otorgado a Admin, Coordinador y QM (mismo patrón de
permiso ad-hoc que 048_tool_processes_manage_skills.py).
"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "050"
down_revision = "049"
branch_labels = None
depends_on = None

NEW_PERMISSIONS = {
    ("reports", "view"): ["Admin", "Coordinador", "QM"],
}


def upgrade() -> None:
    op.create_table(
        "report_saved_views",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("config", JSONB(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "name", name="uq_report_saved_views_user_name"),
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
        "(SELECT id FROM permissions WHERE module = 'reports' AND action = 'view')"
    ))
    bind.execute(sa.text("DELETE FROM permissions WHERE module = 'reports' AND action = 'view'"))
    op.drop_table("report_saved_views")
