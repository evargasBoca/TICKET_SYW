"""Accesos y conexiones múltiples del Cliente (spec 018, UAT OBS-0001/OBS-0008/OBS-0017;
ampliado por spec 031, UAT OBS-0041: access_type_id de catálogo, port, environment universal).

Tests ultra-limitados (Principio VII): un único cliente de fixture, ≤10 registros de acceso
por test, sin crear usuarios Resolutor adicionales (se reutiliza `resolver_token`, ya semilla).
"""
import io


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_access_type(client, unique_name) -> str:
    resp = client.post("/api/catalogs/access-types", json={"name": f"TipoTest-{unique_name}"})
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()["id"]


def test_add_multiple_accesses_and_attachment(client, unique_name):
    """US1 (OBS-0001): varios accesos (mismo tipo de catálogo) + un adjunto persisten por separado."""
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    type_id = _create_access_type(client, unique_name)

    vpn = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": type_id, "host": "10.0.0.5", "port": 1194,
    })
    assert vpn.status_code == 201, vpn.get_json()

    url = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": type_id, "environment": "test", "host": "https://test.acme.com",
    })
    assert url.status_code == 201, url.get_json()

    rdp = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": type_id, "host": "RDP-ACME-01",
    })
    assert rdp.status_code == 201, rdp.get_json()

    listed = client.get(f"/api/clients/{cid}/access")
    assert listed.status_code == 200
    items = listed.get_json()["items"]
    assert len(items) == 3
    assert all(i["access_type"]["id"] == type_id for i in items)

    upload = client.post(
        f"/api/clients/{cid}/access-attachments",
        data={"file": (io.BytesIO(b"contenido de prueba"), "instructivo.txt")},
        content_type="multipart/form-data",
    )
    assert upload.status_code == 201, upload.get_json()
    attachments = client.get(f"/api/clients/{cid}/access-attachments").get_json()["items"]
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "instructivo.txt"
    assert attachments[0]["client_access_id"] is None


def test_update_and_delete_access_does_not_affect_others(client, unique_name):
    """US1: editar/eliminar un registro no afecta a los demás del mismo cliente."""
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    type_id = _create_access_type(client, unique_name)

    a1 = client.post(f"/api/clients/{cid}/access", json={"access_type_id": type_id, "host": "1.1.1.1"}).get_json()
    a2 = client.post(f"/api/clients/{cid}/access", json={"access_type_id": type_id, "host": "RDP-1"}).get_json()

    patched = client.patch(f"/api/clients/{cid}/access/{a1['id']}", json={"notes": "actualizado"})
    assert patched.status_code == 200
    assert patched.get_json()["notes"] == "actualizado"

    deleted = client.delete(f"/api/clients/{cid}/access/{a1['id']}")
    assert deleted.status_code == 204

    remaining = client.get(f"/api/clients/{cid}/access").get_json()["items"]
    assert len(remaining) == 1
    assert remaining[0]["id"] == a2["id"]


def test_environment_applies_to_any_access_type(client, unique_name):
    """spec 031 FR-009: 'environment' ya no se restringe a un único tipo de acceso."""
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    type_id = _create_access_type(client, unique_name)
    resp = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": type_id, "environment": "prod", "port": 5432, "host": "db.acme.com",
    })
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert body["environment"] == "prod"
    assert body["port"] == 5432


def test_invalid_access_type_id_rejected(client, unique_name):
    """FR-001 (spec 031): access_type_id debe existir en catalog_access_types."""
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    resp = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": "00000000-0000-0000-0000-000000000000", "host": "1.1.1.1",
    })
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "validation_error"


def test_access_isolated_between_two_clients(client, unique_name):
    """US2 (OBS-0008): los accesos de un cliente nunca aparecen en el listado de otro."""
    client_a = client.post("/api/clients", json={"name": f"Client-A-{unique_name}"}).get_json()
    client_b = client.post("/api/clients", json={"name": f"Client-B-{unique_name}"}).get_json()
    type_id = _create_access_type(client, unique_name)

    client.post(f"/api/clients/{client_a['id']}/access", json={"access_type_id": type_id, "host": "A-host"})

    items_b = client.get(f"/api/clients/{client_b['id']}/access").get_json()["items"]
    assert items_b == []

    items_a = client.get(f"/api/clients/{client_a['id']}/access").get_json()["items"]
    assert len(items_a) == 1
    assert items_a[0]["host"] == "A-host"


def test_password_hidden_without_sensitive_permission(anon_client, client, unique_name, resolver_token):
    """US3 (OBS-0017): sin permiso de datos sensibles, no se expone username/password de las
    credenciales (spec 031 — el dato sensible vive ahora en client_access_credentials)."""
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    type_id = _create_access_type(client, unique_name)
    access = client.post(f"/api/clients/{cid}/access", json={"access_type_id": type_id, "host": "1.1.1.1"}).get_json()
    client.post(f"/api/clients/{cid}/access/{access['id']}/credentials", json={
        "username": "secretuser", "password": "secretpass",
    })

    as_resolver = anon_client.get(f"/api/clients/{cid}/access/{access['id']}/credentials", headers=_auth(resolver_token))
    assert as_resolver.status_code == 200
    item = as_resolver.get_json()["items"][0]
    assert "password" not in item
    assert "username" not in item

    as_admin = client.get(f"/api/clients/{cid}/access/{access['id']}/credentials").get_json()["items"][0]
    assert as_admin["password"] == "secretpass"
    assert as_admin["username"] == "secretuser"
