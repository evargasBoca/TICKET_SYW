"""OBS-0037 (spec 028) — GET /api/absence-requests?resource_id=... (calendario de Equipo)."""
import uuid

import pytest


@pytest.fixture()
def hr_user(db_session, unique_name):
    """Usuario con rol RRHH (único rol seedeado con `absence_requests:view_all`, migración 039)."""
    from backend.domain.entities.user import User
    from backend.infra.repositories.role_repo import RoleRepository
    from backend.infra.repositories.user_repo import UserRepository
    rrhh_role = RoleRepository(db_session).get_by_name("RRHH")
    user = User(
        id=uuid.uuid4(), email=f"hr.{unique_name}@sywork.net", username=f"hr_{unique_name}",
        role=rrhh_role, active=True,
    )
    return UserRepository(db_session).create(user)


@pytest.fixture()
def hr_auth(app, hr_user):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=str(hr_user.id))
    return {"Authorization": f"Bearer {token}"}


def test_resource_id_requires_view_all_permission(client, ticket_resource, resolver_auth):
    """Un Resolutor (sin absence_requests:view_all) no puede consultar ausencias de otro
    recurso por resource_id, aunque pueda ver su propio scope=own."""
    response = client.get(
        f"/api/absence-requests?resource_id={ticket_resource['id']}", headers=resolver_auth)
    assert response.status_code == 403, response.get_json()


def test_admin_without_view_all_is_forbidden(client, ticket_resource):
    """El rol Admin de este seed no tiene `absence_requests:view_all` (solo RRHH, migración
    039) — confirma que el gate no depende del rol "administrativo" genérico sino del permiso
    específico."""
    response = client.get(f"/api/absence-requests?resource_id={ticket_resource['id']}")
    assert response.status_code == 403, response.get_json()


def test_hr_can_list_absences_by_resource_id(client, ticket_resource, hr_auth):
    """RRHH (con absence_requests:view_all) puede consultar el scope puntual de un recurso —
    aquí sin ausencias creadas, solo se verifica que el filtro no rompe la respuesta."""
    response = client.get(
        f"/api/absence-requests?resource_id={ticket_resource['id']}", headers=hr_auth)
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["items"] == []


def test_resource_id_rejects_invalid_uuid(client, hr_auth):
    response = client.get("/api/absence-requests?resource_id=not-a-uuid", headers=hr_auth)
    assert response.status_code == 400, response.get_json()
