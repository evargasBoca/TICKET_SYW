import uuid
from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.infra.models.ticket_model import TicketModel, ticket_skills_table
from backend.infra.models.client_model import ClientModel
from backend.infra.models.project_model import ProjectModel
from backend.infra.models.resource_model import ResourceModel, SkillModel
from backend.infra.models.catalog_model import ToolCatalogModel, ProcessCatalogModel
from backend.infra.models.work_session_model import WorkSessionModel
from backend.infra.models.report_view_model import ReportSavedViewModel
from backend.domain.entities.report_view import ReportSavedView


class ReportFilters:
    def __init__(self, date_from: Optional[date] = None, date_to: Optional[date] = None,
                 client_id: Optional[uuid.UUID] = None, project_id: Optional[uuid.UUID] = None,
                 assignee_id: Optional[uuid.UUID] = None) -> None:
        self.date_from = date_from
        self.date_to = date_to
        self.client_id = client_id
        self.project_id = project_id
        self.assignee_id = assignee_id


class ReportRepository:
    """Proyección de solo lectura de la Fila de Reporte de Ticket (Capa 2). No introduce una
    fuente de datos nueva — une entidades ya existentes (spec 034, data-model.md)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _base_query(self, filters: ReportFilters):
        total_logged = (
            self._db.query(
                WorkSessionModel.ticket_id.label("ticket_id"),
                func.sum(WorkSessionModel.duration_minutes).label("total_logged_minutes"),
            )
            .filter(WorkSessionModel.deleted_at.is_(None))
            .group_by(WorkSessionModel.ticket_id)
            .subquery()
        )
        q = (
            self._db.query(
                TicketModel.id.label("ticket_id"),
                TicketModel.ticket_number,
                TicketModel.title,
                TicketModel.status,
                TicketModel.priority,
                TicketModel.created_at,
                TicketModel.client_id,
                ClientModel.name.label("client_name"),
                TicketModel.project_id,
                ProjectModel.name.label("project_name"),
                TicketModel.assignee_id,
                ResourceModel.full_name.label("assignee_name"),
                ToolCatalogModel.name.label("tool_name"),
                ProcessCatalogModel.name.label("process_name"),
                TicketModel.sla_contact_consumed_seconds.label("time_to_first_contact_seconds"),
                TicketModel.sla_execution_consumed_seconds.label("execution_time_seconds"),
                func.coalesce(total_logged.c.total_logged_minutes, 0).label("total_logged_minutes"),
            )
            .outerjoin(ClientModel, ClientModel.id == TicketModel.client_id)
            .outerjoin(ProjectModel, ProjectModel.id == TicketModel.project_id)
            .outerjoin(ResourceModel, ResourceModel.id == TicketModel.assignee_id)
            .outerjoin(ToolCatalogModel, ToolCatalogModel.id == TicketModel.tool_id)
            .outerjoin(ProcessCatalogModel, ProcessCatalogModel.id == TicketModel.process_id)
            .outerjoin(total_logged, total_logged.c.ticket_id == TicketModel.id)
        )
        if filters.date_from:
            q = q.filter(func.date(TicketModel.created_at) >= filters.date_from)
        if filters.date_to:
            q = q.filter(func.date(TicketModel.created_at) <= filters.date_to)
        if filters.client_id:
            q = q.filter(TicketModel.client_id == filters.client_id)
        if filters.project_id:
            q = q.filter(TicketModel.project_id == filters.project_id)
        if filters.assignee_id:
            q = q.filter(TicketModel.assignee_id == filters.assignee_id)
        return q

    def _skills_by_ticket_id(self, ticket_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[str]]:
        if not ticket_ids:
            return {}
        rows = (
            self._db.query(ticket_skills_table.c.ticket_id, SkillModel.label)
            .join(SkillModel, SkillModel.id == ticket_skills_table.c.skill_id)
            .filter(ticket_skills_table.c.ticket_id.in_(ticket_ids))
            .all()
        )
        result: dict[uuid.UUID, list[str]] = {}
        for ticket_id, skill_label in rows:
            result.setdefault(ticket_id, []).append(skill_label)
        return result

    def list_paginated(self, filters: ReportFilters, page: int = 1, page_size: int = 50) -> tuple[list[dict], int]:
        q = self._base_query(filters).order_by(TicketModel.created_at.desc())
        total = q.count()
        rows = q.offset((page - 1) * page_size).limit(page_size).all()
        ticket_ids = [r.ticket_id for r in rows]
        skills_by_ticket = self._skills_by_ticket_id(ticket_ids)
        items = [self._row_to_dict(r, skills_by_ticket.get(r.ticket_id, [])) for r in rows]
        return items, total

    def list_all(self, filters: ReportFilters) -> list[dict]:
        """Conjunto filtrado completo, sin paginar — usado por agregaciones y exportación
        (research.md Decisión 6)."""
        rows = self._base_query(filters).order_by(TicketModel.created_at.desc()).all()
        ticket_ids = [r.ticket_id for r in rows]
        skills_by_ticket = self._skills_by_ticket_id(ticket_ids)
        return [self._row_to_dict(r, skills_by_ticket.get(r.ticket_id, [])) for r in rows]

    @staticmethod
    def _row_to_dict(row, skills: list[str]) -> dict:
        return {
            "ticket_id": str(row.ticket_id),
            "ticket_number": row.ticket_number,
            "title": row.title,
            "status": row.status,
            "priority": row.priority,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "client_id": str(row.client_id) if row.client_id else None,
            "client_name": row.client_name,
            "project_id": str(row.project_id) if row.project_id else None,
            "project_name": row.project_name,
            "assignee_id": str(row.assignee_id) if row.assignee_id else None,
            "assignee_name": row.assignee_name,
            "tool_name": row.tool_name,
            "process_name": row.process_name,
            "skills": skills,
            "time_to_first_contact_seconds": row.time_to_first_contact_seconds,
            "execution_time_seconds": row.execution_time_seconds,
            "total_logged_minutes": row.total_logged_minutes,
        }


class ReportSavedViewRepository:
    """CRUD de Vistas Personalizadas (Capa 2) — siempre acotado a `user_id` (FR-014)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: uuid.UUID) -> list[ReportSavedView]:
        models = (
            self._db.query(ReportSavedViewModel)
            .filter(ReportSavedViewModel.user_id == user_id)
            .order_by(ReportSavedViewModel.name)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_by_id_for_user(self, view_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ReportSavedView]:
        model = (
            self._db.query(ReportSavedViewModel)
            .filter(ReportSavedViewModel.id == view_id, ReportSavedViewModel.user_id == user_id)
            .first()
        )
        return model.to_entity() if model else None

    def upsert(self, view: ReportSavedView) -> ReportSavedView:
        existing = (
            self._db.query(ReportSavedViewModel)
            .filter(ReportSavedViewModel.user_id == view.user_id, ReportSavedViewModel.name == view.name)
            .first()
        )
        if existing:
            existing.config = view.config
            self._db.commit()
            self._db.refresh(existing)
            return existing.to_entity()
        model = ReportSavedViewModel.from_entity(view)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return model.to_entity()

    def delete_for_user(self, view_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        model = (
            self._db.query(ReportSavedViewModel)
            .filter(ReportSavedViewModel.id == view_id, ReportSavedViewModel.user_id == user_id)
            .first()
        )
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
