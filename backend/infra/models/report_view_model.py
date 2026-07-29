import uuid
from sqlalchemy import Column, ForeignKey, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from backend.infra.models import Base
from backend.domain.entities.report_view import ReportSavedView


class ReportSavedViewModel(Base):
    __tablename__ = "report_saved_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    config = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_report_saved_views_user_name"),
    )

    def to_entity(self) -> ReportSavedView:
        return ReportSavedView(
            id=self.id, user_id=self.user_id, name=self.name, config=self.config,
            created_at=self.created_at, updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, view: ReportSavedView) -> "ReportSavedViewModel":
        return cls(id=view.id, user_id=view.user_id, name=view.name, config=view.config)
