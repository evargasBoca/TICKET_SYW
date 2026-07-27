"""Credenciales múltiples por acceso (spec 031, UAT OBS-0041, US2).

Test ultra-limitado (Principio VII): un único cliente + un acceso de fixture, 2 credenciales
de prueba (≤10 registros), sin crear usuarios Resolutor adicionales.
"""


def _setup_access(client, unique_name):
    created = client.post("/api/clients", json={"name": f"Client-{unique_name}"}).get_json()
    cid = created["id"]
    type_id = client.post("/api/catalogs/access-types", json={"name": f"TipoCred-{unique_name}"}).get_json()["id"]
    access = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": type_id, "host": "erp-test.acme.oraclecloud.com",
    }).get_json()
    return cid, access["id"]


def test_multiple_credentials_independent_crud(client, unique_name):
    """FR-005/FR-006: N credenciales por acceso, sin repetir host; editar/eliminar una no afecta a las demás."""
    cid, access_id = _setup_access(client, unique_name)

    c1 = client.post(f"/api/clients/{cid}/access/{access_id}/credentials", json={
        "label": "Finanzas", "username": "impl_fin", "password": "pw1",
    })
    assert c1.status_code == 201, c1.get_json()
    c2 = client.post(f"/api/clients/{cid}/access/{access_id}/credentials", json={
        "label": "Proyectos", "username": "impl_proy", "password": "pw2",
    })
    assert c2.status_code == 201, c2.get_json()

    listed = client.get(f"/api/clients/{cid}/access/{access_id}/credentials").get_json()["items"]
    assert len(listed) == 2
    assert {c["label"] for c in listed} == {"Finanzas", "Proyectos"}

    c1_id = c1.get_json()["id"]
    c2_id = c2.get_json()["id"]

    patched = client.patch(f"/api/clients/{cid}/access/{access_id}/credentials/{c1_id}", json={"notes": "rotar anual"})
    assert patched.status_code == 200
    assert patched.get_json()["notes"] == "rotar anual"

    deleted = client.delete(f"/api/clients/{cid}/access/{access_id}/credentials/{c1_id}")
    assert deleted.status_code == 204

    remaining = client.get(f"/api/clients/{cid}/access/{access_id}/credentials").get_json()["items"]
    assert len(remaining) == 1
    assert remaining[0]["id"] == c2_id
    assert remaining[0]["username"] == "impl_proy"


def test_access_with_no_credentials_is_valid(client, unique_name):
    """Edge case (spec.md): un acceso sin ninguna credencial registrada es un estado válido."""
    cid, access_id = _setup_access(client, unique_name)
    resp = client.get(f"/api/clients/{cid}/access/{access_id}/credentials")
    assert resp.status_code == 200
    assert resp.get_json()["items"] == []


def test_credential_not_found_for_wrong_access(client, unique_name):
    """Una credencial solo se edita/elimina a través del acceso al que pertenece."""
    cid, access_id = _setup_access(client, unique_name)
    other_type_id = client.post("/api/catalogs/access-types", json={"name": f"TipoCredB-{unique_name}"}).get_json()["id"]
    other_access = client.post(f"/api/clients/{cid}/access", json={
        "access_type_id": other_type_id, "host": "other-host",
    }).get_json()

    cred = client.post(f"/api/clients/{cid}/access/{access_id}/credentials", json={"label": "X"}).get_json()

    resp = client.patch(
        f"/api/clients/{cid}/access/{other_access['id']}/credentials/{cred['id']}", json={"label": "Y"},
    )
    assert resp.status_code == 404
