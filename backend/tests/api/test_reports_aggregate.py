"""GET /api/reports/tickets — filtros + agregaciones (spec 034, US2/US4).

Ultra-limitado (Principio VII): exactamente 5 tickets mock por test, acotados por client_id/
project_id para no mezclarse con datos de otros tests en la misma base compartida.
"""


def test_lista_tickets_filtrados_por_cliente_y_proyecto(client, ticket_client, ticket_project, make_ticket):
    for i in range(5):
        make_ticket(title=f"Ticket reporte {i}")

    response = client.get("/api/reports/tickets", query_string={
        "client_id": ticket_client["id"], "project_id": ticket_project["id"], "page_size": 50,
    })

    assert response.status_code == 200, response.get_json()
    data = response.get_json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert data["aggregates"] == {}


def test_aggregate_count_sobre_conjunto_filtrado_completo(client, ticket_client, ticket_project, make_ticket):
    for i in range(5):
        make_ticket(title=f"Ticket agregacion {i}")

    response = client.get("/api/reports/tickets", query_string={
        "client_id": ticket_client["id"], "project_id": ticket_project["id"],
        "aggregate": "ticket_id:count",
    })

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["aggregates"] == {"ticket_id": {"count": 5}}


def test_aggregate_rechaza_columna_no_numerica(client, ticket_client, ticket_project, make_ticket):
    make_ticket()

    response = client.get("/api/reports/tickets", query_string={
        "client_id": ticket_client["id"], "aggregate": "title:sum",
    })

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_aggregate_column"


def test_date_from_posterior_a_date_to_es_rechazado(client, ticket_client):
    response = client.get("/api/reports/tickets", query_string={
        "client_id": ticket_client["id"], "date_from": "2026-08-01", "date_to": "2026-01-01",
    })

    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_error"
