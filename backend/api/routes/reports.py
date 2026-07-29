"""Módulo de Reportes Dinámicos (spec 034): grid interactivo de solo lectura sobre datos ya
existentes de Ticket/SLA/Recursos/Catálogos, con filtros, agregaciones, exportación a Excel y
Vistas Personalizadas por usuario. Todo el namespace requiere el permiso `reports:view`
(Admin/Coordinador/QM — ver research.md Decisión 7)."""
import io
import uuid

from flask import request, g, send_file
from flask_restx import Namespace, Resource, fields

from backend.api.middleware.rbac import require_permission
from backend.api.routes._shared import parse_uuid, error_model, server_error
from backend.infra.database import get_db
from backend.infra.repositories.report_repo import ReportRepository, ReportFilters, ReportSavedViewRepository
from backend.domain.entities.report_view import ReportSavedView
from backend.domain.services.report_aggregation_service import compute_aggregate, ReportAggregationError

ns = Namespace("reports", description="Reportes dinámicos de Tickets", path="/api/reports")

# Etiquetas de columna para el encabezado del Excel exportado (mismas claves que ReportRow).
COLUMN_LABELS = {
    "ticket_number": "Ticket", "title": "Título", "status": "Estado", "priority": "Prioridad",
    "client_name": "Cliente", "project_name": "Proyecto", "assignee_name": "Encargado",
    "tool_name": "Herramienta", "process_name": "Proceso", "skills": "Skills",
    "time_to_first_contact_seconds": "Primer contacto (seg)",
    "execution_time_seconds": "Ejecución/Resolución (seg)",
    "total_logged_minutes": "Tiempo registrado (min)", "created_at": "Creado",
}

_error = error_model(ns, "ReportError")

_report_row_out = ns.model("ReportRow", {
    "ticket_id": fields.String(),
    "ticket_number": fields.Integer(),
    "title": fields.String(),
    "status": fields.String(),
    "priority": fields.String(),
    "created_at": fields.String(),
    "client_id": fields.String(),
    "client_name": fields.String(),
    "project_id": fields.String(),
    "project_name": fields.String(),
    "assignee_id": fields.String(),
    "assignee_name": fields.String(),
    "tool_name": fields.String(),
    "process_name": fields.String(),
    "skills": fields.List(fields.String()),
    "time_to_first_contact_seconds": fields.Integer(),
    "execution_time_seconds": fields.Integer(),
    "total_logged_minutes": fields.Integer(),
})

_report_list_out = ns.model("ReportList", {
    "items": fields.List(fields.Nested(_report_row_out)),
    "total": fields.Integer(),
    "page": fields.Integer(),
    "page_size": fields.Integer(),
    "aggregates": fields.Raw(description="Agregaciones sobre TODO el conjunto filtrado (no solo "
                                         "la página), keyed por columna → función → valor"),
})


def _parse_date(value: str | None):
    if not value:
        return None
    from datetime import date
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_filters() -> ReportFilters | dict:
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    if request.args.get("date_from") and date_from is None:
        return {"error": "validation_error", "message": "'date_from' debe ser una fecha ISO (YYYY-MM-DD)"}
    if request.args.get("date_to") and date_to is None:
        return {"error": "validation_error", "message": "'date_to' debe ser una fecha ISO (YYYY-MM-DD)"}
    if date_from and date_to and date_from > date_to:
        return {"error": "validation_error", "message": "'date_from' no puede ser posterior a 'date_to'"}
    return ReportFilters(
        date_from=date_from, date_to=date_to,
        client_id=parse_uuid(request.args.get("client_id") or "") or None,
        project_id=parse_uuid(request.args.get("project_id") or "") or None,
        assignee_id=parse_uuid(request.args.get("assignee_id") or "") or None,
    )


@ns.route("/tickets")
class ReportTickets(Resource):
    @ns.doc("list_report_tickets", params={
        "date_from": {"description": "Fecha ISO desde (sobre created_at)", "type": "string"},
        "date_to": {"description": "Fecha ISO hasta (sobre created_at)", "type": "string"},
        "client_id": {"description": "Filtrar por UUID de Cliente", "type": "string"},
        "project_id": {"description": "Filtrar por UUID de Proyecto", "type": "string"},
        "assignee_id": {"description": "Filtrar por UUID de Encargado/Resolutor", "type": "string"},
        "page": {"description": "Número de página (default 1)", "type": "integer", "default": 1},
        "page_size": {"description": "Registros por página, máx 200 (default 50)", "type": "integer", "default": 50},
        "aggregate": {"description": "Repetible, formato 'campo:funcion' (ej. "
                                     "total_logged_minutes:sum) — calculado sobre TODO el "
                                     "conjunto filtrado, no solo la página (FR-011)",
                     "type": "array"},
    })
    @ns.response(200, "Filas del reporte de Tickets, paginadas", _report_list_out)
    @ns.response(400, "Filtros inválidos", _error)
    @ns.response(401, "No autenticado", _error)
    @ns.response(403, "Sin permiso reports:view", _error)
    @ns.response(500, "Error interno del servidor", _error)
    @require_permission("reports", "view")
    def get(self):
        """Filas del reporte de Tickets con filtros combinables (FR-008/FR-010)."""
        filters = _parse_filters()
        if isinstance(filters, dict):
            return filters, 400
        try:
            page = max(1, int(request.args.get("page", 1)))
            page_size = min(max(1, int(request.args.get("page_size", 50))), 200)
        except ValueError:
            return {"error": "validation_error", "message": "page y page_size deben ser enteros"}, 400
        aggregate_specs = []
        for raw in request.args.getlist("aggregate"):
            if ":" not in raw:
                return {"error": "validation_error",
                        "message": f"'aggregate' inválido: '{raw}' (formato esperado 'campo:funcion')"}, 400
            column, _, function = raw.partition(":")
            aggregate_specs.append((column, function))
        try:
            db = get_db()
            repo = ReportRepository(db)
            items, total = repo.list_paginated(filters, page=page, page_size=page_size)
            aggregates = {}
            if aggregate_specs:
                all_rows = repo.list_all(filters)
                for column, function in aggregate_specs:
                    try:
                        value = compute_aggregate(all_rows, column, function)
                    except ReportAggregationError as e:
                        return {"error": e.code, "message": e.message}, e.status_code
                    aggregates.setdefault(column, {})[function] = value
            return {"items": items, "total": total, "page": page, "page_size": page_size,
                    "aggregates": aggregates}, 200
        except Exception:
            return server_error()


@ns.route("/tickets/export")
class ReportTicketsExport(Resource):
    @ns.doc("export_report_tickets", params={
        "date_from": {"description": "Fecha ISO desde (sobre created_at)", "type": "string"},
        "date_to": {"description": "Fecha ISO hasta (sobre created_at)", "type": "string"},
        "client_id": {"description": "Filtrar por UUID de Cliente", "type": "string"},
        "project_id": {"description": "Filtrar por UUID de Proyecto", "type": "string"},
        "assignee_id": {"description": "Filtrar por UUID de Encargado/Resolutor", "type": "string"},
        "columns": {"description": "Repetible, claves de columna en el orden a exportar "
                                   "(default: todas)", "type": "array"},
    })
    @ns.response(200, "Archivo .xlsx del conjunto filtrado completo (US5)")
    @ns.response(400, "Filtros inválidos, o sin datos para exportar", _error)
    @ns.response(401, "No autenticado", _error)
    @ns.response(403, "Sin permiso reports:view", _error)
    @ns.response(500, "Error interno del servidor", _error)
    @require_permission("reports", "view")
    def get(self):
        """Exporta a Excel el conjunto filtrado COMPLETO (no solo la página visible), respetando
        las columnas y el orden recibidos (FR-015)."""
        filters = _parse_filters()
        if isinstance(filters, dict):
            return filters, 400
        columns = request.args.getlist("columns") or list(COLUMN_LABELS.keys())
        unknown = [c for c in columns if c not in COLUMN_LABELS]
        if unknown:
            return {"error": "validation_error", "message": f"Columnas desconocidas: {', '.join(unknown)}"}, 400
        try:
            db = get_db()
            rows = ReportRepository(db).list_all(filters)
        except Exception:
            return server_error()
        if not rows:
            return {"error": "no_data", "message": "El filtro no produce ninguna fila para exportar"}, 400

        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de Tickets"
        ws.append([COLUMN_LABELS[c] for c in columns])
        for row in rows:
            ws.append([", ".join(row[c]) if isinstance(row.get(c), list) else row.get(c) for c in columns])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return send_file(
            buffer, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True, download_name="reporte_tickets.xlsx",
        )


_saved_view_out = ns.model("ReportSavedView", {
    "id": fields.String(),
    "name": fields.String(),
    "config": fields.Raw(description="Columnas/orden, filtros y agregaciones guardadas"),
    "updated_at": fields.String(),
})

_saved_view_list_out = ns.model("ReportSavedViewList", {
    "items": fields.List(fields.Nested(_saved_view_out)),
})

_saved_view_input = ns.model("ReportSavedViewInput", {
    "name": fields.String(required=True),
    "config": fields.Raw(required=True),
})


def _view_to_dict(view: ReportSavedView) -> dict:
    return {
        "id": str(view.id), "name": view.name, "config": view.config,
        "updated_at": view.updated_at.isoformat() if view.updated_at else None,
    }


@ns.route("/views")
class ReportViews(Resource):
    @ns.doc("list_report_views")
    @ns.response(200, "Vistas Personalizadas del usuario autenticado (FR-014, privadas)", _saved_view_list_out)
    @ns.response(401, "No autenticado", _error)
    @ns.response(403, "Sin permiso reports:view", _error)
    @ns.response(500, "Error interno del servidor", _error)
    @require_permission("reports", "view")
    def get(self):
        """Lista solo las Vistas Personalizadas del usuario autenticado (FR-014)."""
        try:
            db = get_db()
            views = ReportSavedViewRepository(db).list_for_user(g.current_user.id)
            return {"items": [_view_to_dict(v) for v in views]}, 200
        except Exception:
            return server_error()

    @ns.doc("save_report_view")
    @ns.expect(_saved_view_input, validate=False)
    @ns.response(200, "Vista Personalizada guardada (upsert por nombre)", _saved_view_out)
    @ns.response(400, "Datos inválidos", _error)
    @ns.response(401, "No autenticado", _error)
    @ns.response(403, "Sin permiso reports:view", _error)
    @ns.response(500, "Error interno del servidor", _error)
    @require_permission("reports", "view")
    def post(self):
        """Guarda la configuración actual (columnas, filtros, agregaciones) con un nombre. Si ya
        existe una Vista con ese nombre para este usuario, la actualiza (upsert — Edge Case de
        nombre duplicado, FR-013)."""
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        config = data.get("config")
        if not name:
            return {"error": "validation_error", "message": "El campo 'name' es requerido"}, 400
        if not isinstance(config, dict):
            return {"error": "validation_error", "message": "El campo 'config' es requerido y debe ser un objeto"}, 400
        try:
            db = get_db()
            view = ReportSavedView(id=uuid.uuid4(), user_id=g.current_user.id, name=name, config=config)
            saved = ReportSavedViewRepository(db).upsert(view)
            return _view_to_dict(saved), 200
        except Exception:
            return server_error()


@ns.route("/views/<string:view_id>")
class ReportViewDetail(Resource):
    @ns.doc("delete_report_view")
    @ns.response(204, "Vista Personalizada eliminada")
    @ns.response(401, "No autenticado", _error)
    @ns.response(403, "Sin permiso reports:view", _error)
    @ns.response(404, "Vista no encontrada, o pertenece a otro usuario", _error)
    @ns.response(500, "Error interno del servidor", _error)
    @require_permission("reports", "view")
    def delete(self, view_id: str):
        """Elimina una Vista Personalizada propia (ownership acotado por user_id, FR-014)."""
        view_uuid = parse_uuid(view_id)
        if not view_uuid:
            return {"error": "not_found", "message": "Vista no encontrada"}, 404
        try:
            db = get_db()
            deleted = ReportSavedViewRepository(db).delete_for_user(view_uuid, g.current_user.id)
            if not deleted:
                return {"error": "not_found", "message": "Vista no encontrada"}, 404
            return "", 204
        except Exception:
            return server_error()
