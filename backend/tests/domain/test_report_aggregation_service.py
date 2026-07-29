"""report_aggregation_service — dominio puro, sin DB (spec 034, US4).

Ultra-limitado (Principio VII): listas de dicts en memoria, sin inserts a base de datos.
"""
import pytest

from backend.domain.services.report_aggregation_service import compute_aggregate, ReportAggregationError

ROWS = [
    {"ticket_id": "1", "total_logged_minutes": 60, "execution_time_seconds": 3600, "client_name": "Aris"},
    {"ticket_id": "2", "total_logged_minutes": 30, "execution_time_seconds": None, "client_name": "Vaxthera"},
    {"ticket_id": "3", "total_logged_minutes": 90, "execution_time_seconds": 1800, "client_name": "Aris"},
]


def test_sum_sobre_columna_numerica():
    assert compute_aggregate(ROWS, "total_logged_minutes", "sum") == 180


def test_avg_ignora_valores_none():
    assert compute_aggregate(ROWS, "execution_time_seconds", "avg") == 2700


def test_count_sobre_ticket_id():
    assert compute_aggregate(ROWS, "ticket_id", "count") == 3


def test_rechaza_columna_no_numerica():
    with pytest.raises(ReportAggregationError) as exc:
        compute_aggregate(ROWS, "client_name", "sum")
    assert exc.value.code == "invalid_aggregate_column"


def test_rechaza_funcion_desconocida():
    with pytest.raises(ReportAggregationError) as exc:
        compute_aggregate(ROWS, "total_logged_minutes", "median")
    assert exc.value.code == "invalid_aggregate_function"


def test_avg_sin_valores_devuelve_none():
    rows = [{"total_logged_minutes": None}]
    assert compute_aggregate(rows, "total_logged_minutes", "avg") is None
