"""Cálculo de agregaciones sobre la Fila de Reporte de Ticket (spec 034, US4). Capa 1 — puro,
sin SQLAlchemy ni Flask: recibe listas de dicts ya extraídas por el repositorio de
infraestructura (research.md Decisión 6)."""
from backend.domain.errors import DomainError

# Columnas numéricas/tiempo sobre las que FR-011 permite sum/avg; count aplica también sobre
# ticket_id (cantidad de tickets). Cualquier otra columna (texto o lista) no es agregable (FR-012).
NUMERIC_COLUMNS = {"time_to_first_contact_seconds", "execution_time_seconds", "total_logged_minutes"}
COUNTABLE_COLUMN = "ticket_id"
FUNCTIONS = {"sum", "avg", "count"}


class ReportAggregationError(DomainError):
    pass


def compute_aggregate(rows: list[dict], column: str, function: str) -> float | int | None:
    if function not in FUNCTIONS:
        raise ReportAggregationError(
            "invalid_aggregate_function", f"Función de agregación '{function}' no soportada", status_code=400)
    if function == "count":
        if column != COUNTABLE_COLUMN and column not in NUMERIC_COLUMNS:
            raise ReportAggregationError(
                "invalid_aggregate_column", f"La columna '{column}' no admite agregación", status_code=400)
        return len(rows)
    if column not in NUMERIC_COLUMNS:
        raise ReportAggregationError(
            "invalid_aggregate_column",
            f"La columna '{column}' no es numérica y no admite agregación (FR-012)", status_code=400)
    values = [r[column] for r in rows if r.get(column) is not None]
    if function == "sum":
        return sum(values)
    if not values:
        return None
    return sum(values) / len(values)
