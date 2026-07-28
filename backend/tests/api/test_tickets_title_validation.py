"""OBS-0033/OBS-0034 (spec 028) — validación del título del ticket al crear/editar."""


def _payload(ticket_client, ticket_project=None, **overrides):
    payload = {
        "title": "Error contabilizando en GL",
        "description": "El batch de contabilización falla con error 105",
        "ticket_type": "incident", "priority": "high", "severity": "s2",
        "client_id": ticket_client["id"],
    }
    # OBS-0045: project_id es obligatorio al crear un Ticket desde perfil interno.
    if ticket_project is not None:
        payload["project_id"] = ticket_project["id"]
    payload.update(overrides)
    return payload


def test_create_rejects_whitespace_only_title(client, ticket_client):
    response = client.post("/api/tickets", json=_payload(ticket_client, title="   "))
    assert response.status_code == 400
    assert response.get_json()["error"] == "title_blank"


def test_create_rejects_title_with_emoji(client, ticket_client):
    response = client.post("/api/tickets", json=_payload(ticket_client, title="Error urgente 🔥"))
    assert response.status_code == 400
    assert response.get_json()["error"] == "title_invalid_chars"


def test_create_accepts_accents_numbers_and_punctuation(client, ticket_client, ticket_project):
    response = client.post("/api/tickets", json=_payload(
        ticket_client, ticket_project, title="Error en informe (v2) — cliente Ñuñoa, línea 42"))
    assert response.status_code == 201, response.get_json()


def test_create_trims_surrounding_whitespace(client, ticket_client, ticket_project):
    response = client.post("/api/tickets", json=_payload(ticket_client, ticket_project, title="  Título con espacios  "))
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["title"] == "Título con espacios"


def test_patch_rejects_whitespace_only_title(client, make_ticket):
    ticket = make_ticket()
    response = client.patch(f"/api/tickets/{ticket['id']}", json={"title": "   "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "title_blank"


def test_patch_rejects_title_with_emoji(client, make_ticket):
    ticket = make_ticket()
    response = client.patch(f"/api/tickets/{ticket['id']}", json={"title": "Revisado ✅"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "title_invalid_chars"
