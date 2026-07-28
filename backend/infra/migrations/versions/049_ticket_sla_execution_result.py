"""sla_execution_result / sla_execution_consumed_seconds en tickets (spec 033, UAT OBS-0059)

Revision ID: 049
Revises: 048
Create Date: 2026-07-28

Análogo a `sla_contact_result`/`sla_contact_consumed_seconds` (spec 014) pero para la fase de
Ejecución/cierre — se congela al transicionar a resuelto/cerrado/cancelado si la fase Ejecución
llegó a correr (`domain/services/sla_service.apply_transition`). Ambas columnas nullable, sin
default — tickets existentes quedan en NULL (nunca se recalculan retroactivamente).
"""
from alembic import op
import sqlalchemy as sa

revision = "049"
down_revision = "048"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("sla_execution_result", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("sla_execution_consumed_seconds", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tickets", "sla_execution_consumed_seconds")
    op.drop_column("tickets", "sla_execution_result")
