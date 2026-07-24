"""work_sessions.off_hours (spec 028, US6/OBS-0036)

Revision ID: 046
Revises: 045
Create Date: 2026-07-24

Registrar tiempo fuera del horario laboral configurado del recurso ya no se bloquea (FR-020);
este campo lo clasifica para reportes, sin reclasificar retroactivamente los registros
históricos (data-model.md).
"""
from alembic import op
import sqlalchemy as sa

revision = "046"
down_revision = "045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "work_sessions",
        sa.Column("off_hours", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("work_sessions", "off_hours")
