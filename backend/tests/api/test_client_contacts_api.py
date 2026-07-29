def test_create_client_contact_returns_201(client, unique_name, ticket_client):
    resp = client.post("/api/client-contacts", json={
        "email": f"contacto.{unique_name}@clienteexterno.com",
        "username": f"contacto_{unique_name}",
        "client_id": ticket_client["id"],
    })
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert body["client_id"] == ticket_client["id"]
    assert body["provisional_password"]


def test_create_client_contact_duplicate_email_returns_409(client, unique_name, ticket_client):
    email = f"dup.{unique_name}@clienteexterno.com"
    first = client.post("/api/client-contacts", json={
        "email": email, "username": f"dup_a_{unique_name}", "client_id": ticket_client["id"],
    })
    assert first.status_code == 201, first.get_json()

    second = client.post("/api/client-contacts", json={
        "email": email, "username": f"dup_b_{unique_name}", "client_id": ticket_client["id"],
    })
    assert second.status_code == 409
    assert second.get_json()["error"] == "email_in_use"


def test_create_client_contact_client_not_found_returns_404(client, unique_name):
    import uuid
    resp = client.post("/api/client-contacts", json={
        "email": f"nf.{unique_name}@clienteexterno.com",
        "username": f"nf_{unique_name}",
        "client_id": str(uuid.uuid4()),
    })
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "client_not_found"


def test_create_client_contact_inactive_client_returns_404(client, unique_name, ticket_client):
    deactivated = client.patch(f"/api/clients/{ticket_client['id']}/deactivate")
    assert deactivated.status_code == 200

    resp = client.post("/api/client-contacts", json={
        "email": f"inactive.{unique_name}@clienteexterno.com",
        "username": f"inactive_{unique_name}",
        "client_id": ticket_client["id"],
    })
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "client_not_found"


def test_list_client_contacts_filters_by_client(client, unique_name, ticket_client):
    client.post("/api/client-contacts", json={
        "email": f"list.{unique_name}@clienteexterno.com",
        "username": f"list_{unique_name}",
        "client_id": ticket_client["id"],
    })
    resp = client.get(f"/api/client-contacts?client_id={ticket_client['id']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] >= 1
    assert all(item["client_id"] == ticket_client["id"] for item in body["items"])


def test_create_client_contact_forbidden_for_resolver(client, unique_name, ticket_client, resolver_auth):
    resp = client.post("/api/client-contacts", json={
        "email": f"forbidden.{unique_name}@clienteexterno.com",
        "username": f"forbidden_{unique_name}",
        "client_id": ticket_client["id"],
    }, headers=resolver_auth)
    assert resp.status_code == 403


# ── spec 034 (US1): activar/desactivar Usuario/cliente ──────────────────────────────

def test_deactivate_client_contact_then_reject_repeat(client, unique_name, ticket_client):
    created = client.post("/api/client-contacts", json={
        "email": f"deact.{unique_name}@clienteexterno.com",
        "username": f"deact_{unique_name}", "client_id": ticket_client["id"],
    })
    contact_id = created.get_json()["id"]

    resp = client.patch(f"/api/client-contacts/{contact_id}/active", json={"active": False})
    assert resp.status_code == 200, resp.get_json()
    assert resp.get_json() == {"id": contact_id, "active": False}

    repeat = client.patch(f"/api/client-contacts/{contact_id}/active", json={"active": False})
    assert repeat.status_code == 409
    assert repeat.get_json()["error"] == "already_inactive"


def test_deactivated_contact_excluded_from_active_filter_and_blocked_from_new_project(
        client, unique_name, ticket_client, ticket_project):
    created = client.post("/api/client-contacts", json={
        "email": f"blocked.{unique_name}@clienteexterno.com",
        "username": f"blocked_{unique_name}", "project_ids": [ticket_project["id"]],
    })
    contact_id = created.get_json()["id"]
    client.patch(f"/api/client-contacts/{contact_id}/active", json={"active": False})

    active_only = client.get(f"/api/client-contacts?client_id={ticket_client['id']}&active=true")
    assert contact_id not in [i["id"] for i in active_only.get_json()["items"]]

    inactive_only = client.get(f"/api/client-contacts?client_id={ticket_client['id']}&active=false")
    assert contact_id in [i["id"] for i in inactive_only.get_json()["items"]]

    resp = client.post("/api/projects", json={
        "name": f"Otro Proyecto {unique_name}", "client_id": ticket_client["id"],
        "start_date": "2026-07-29",
    })
    other_project_id = resp.get_json()["id"]

    blocked = client.post(f"/api/client-contacts/{contact_id}/projects", json={"project_id": other_project_id})
    assert blocked.status_code == 409
    assert blocked.get_json()["error"] == "contact_inactive"


def test_reactivate_client_contact_allows_new_project_again(client, unique_name, ticket_client, ticket_project):
    created = client.post("/api/client-contacts", json={
        "email": f"react.{unique_name}@clienteexterno.com",
        "username": f"react_{unique_name}", "project_ids": [ticket_project["id"]],
    })
    contact_id = created.get_json()["id"]
    client.patch(f"/api/client-contacts/{contact_id}/active", json={"active": False})

    reactivated = client.patch(f"/api/client-contacts/{contact_id}/active", json={"active": True})
    assert reactivated.status_code == 200
    assert reactivated.get_json() == {"id": contact_id, "active": True}

    resp = client.post("/api/projects", json={
        "name": f"Reactivado Proyecto {unique_name}", "client_id": ticket_client["id"],
        "start_date": "2026-07-29",
    })
    new_project_id = resp.get_json()["id"]
    added = client.post(f"/api/client-contacts/{contact_id}/projects", json={"project_id": new_project_id})
    assert added.status_code == 201, added.get_json()
