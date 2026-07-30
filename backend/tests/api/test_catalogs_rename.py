"""PATCH /api/catalogs/{catalog}/{item_id} — editar nombre (spec 035, US5)."""


def test_rename_catalog_value(client, unique_name):
    created = client.post("/api/catalogs/teams", json={"name": f"Equipo {unique_name}"}).get_json()
    new_name = f"Equipo renombrado {unique_name}"
    resp = client.patch(f"/api/catalogs/teams/{created['id']}", json={"name": new_name})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == new_name
    assert resp.get_json()["id"] == created["id"]

    listed = client.get("/api/catalogs/teams").get_json()["items"]
    assert any(i["id"] == created["id"] and i["name"] == new_name for i in listed)


def test_rename_catalog_value_rejects_duplicate(client, unique_name):
    a = client.post("/api/catalogs/teams", json={"name": f"Equipo A {unique_name}"}).get_json()
    b = client.post("/api/catalogs/teams", json={"name": f"Equipo B {unique_name}"}).get_json()
    resp = client.patch(f"/api/catalogs/teams/{b['id']}", json={"name": a["name"]})
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "name_duplicate"


def test_rename_catalog_value_rejects_blank_name(client, unique_name):
    created = client.post("/api/catalogs/teams", json={"name": f"Equipo {unique_name}"}).get_json()
    resp = client.patch(f"/api/catalogs/teams/{created['id']}", json={"name": "   "})
    assert resp.status_code == 400


def test_rename_catalog_value_not_found(client):
    resp = client.patch("/api/catalogs/teams/00000000-0000-0000-0000-000000000000", json={"name": "x"})
    assert resp.status_code == 404
