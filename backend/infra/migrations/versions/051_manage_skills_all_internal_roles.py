"""Ampliar tickets:manage_skills a todos los roles internos (spec 035, feedback UAT)

Revision ID: 051
Revises: 050
Create Date: 2026-07-30

`tickets:manage_skills` (migración 048, spec 033) quedó restringido a Coordinador. El feedback
de UAT sobre spec 035 aclara que Admin, Coordinador, QM y Resolutor (todo rol interno) deben
poder asignar/modificar las Skills requeridas del ticket — solo Usuario/cliente (rol externo)
queda excluido. Se agrega el permiso ya existente a los 3 roles internos que faltaban, sin
tocar la fila de Coordinador ya sembrada por la migración 048.
"""
from alembic import op
import sqlalchemy as sa

revision = "051"
down_revision = "050"
branch_labels = None
depends_on = None

ROLES_TO_ADD = ["Admin", "QM", "Resolutor"]


def upgrade() -> None:
    bind = op.get_bind()
    permission_id = bind.execute(sa.text(
        "SELECT id FROM permissions WHERE module = 'tickets' AND action = 'manage_skills'"
    )).scalar()
    if not permission_id:
        return
    roles = {r.name: r.id for r in bind.execute(sa.text("SELECT id, name FROM roles")).fetchall()}
    for role_name in ROLES_TO_ADD:
        role_id = roles.get(role_name)
        if not role_id:
            continue
        exists = bind.execute(sa.text(
            "SELECT 1 FROM role_permissions WHERE role_id = :r AND permission_id = :p"
        ), {"r": str(role_id), "p": str(permission_id)}).first()
        if not exists:
            bind.execute(
                sa.text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:r, :p)"),
                {"r": str(role_id), "p": str(permission_id)},
            )


def downgrade() -> None:
    bind = op.get_bind()
    permission_id = bind.execute(sa.text(
        "SELECT id FROM permissions WHERE module = 'tickets' AND action = 'manage_skills'"
    )).scalar()
    if not permission_id:
        return
    roles = {r.name: r.id for r in bind.execute(sa.text("SELECT id, name FROM roles")).fetchall()}
    for role_name in ROLES_TO_ADD:
        role_id = roles.get(role_name)
        if not role_id:
            continue
        bind.execute(
            sa.text("DELETE FROM role_permissions WHERE role_id = :r AND permission_id = :p"),
            {"r": str(role_id), "p": str(permission_id)},
        )
