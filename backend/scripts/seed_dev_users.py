"""Seed de usuarios adicionales de desarrollo/pruebas por rol (spec 029).

Uso: docker exec sywork_backend python -m backend.scripts.seed_dev_users

Amplía el seed base de la migración 009 con 2 usuarios adicionales por cada rol interno
(Admin, Coordinador, QM) y suficientes Resolutores para llegar a un mínimo de 4, cada uno
con su perfil de Recurso y 3 skills asignadas del catálogo existente. Todos comparten la
misma contraseña de desarrollo ya usada por el seed base. También verifica/corrige la zona
horaria de los clientes Aris y Vaxthera (spec 026).

Re-ejecutable: mismo criterio de convergencia que `seed_clients_aris_vaxthera.py` — nunca
duplica usuarios, Recursos ni asignaciones de skill; si un dato ya existe con un valor
distinto al sembrado, lo actualiza para converger.
"""
import sys
import uuid

from werkzeug.security import generate_password_hash

from backend.infra.database import get_db, close_db
from backend.domain.entities.user import User
from backend.domain.entities.resource import Resource
from backend.infra.repositories.user_repo import UserRepository
from backend.infra.repositories.role_repo import RoleRepository
from backend.infra.repositories.resource_repo import ResourceRepository, SkillRepository
from backend.infra.repositories.client_repo import ClientRepository

# Contraseña fija para todos los usuarios sembrados por este script — MISMA que la de los 4
# usuarios base de la migración 009 (ver docs/credenciales_dev.txt). Sujeta a la misma
# advertencia de rotación obligatoria antes de operar Producción real con datos de clientes.
SEED_PASSWORD_DEV = "SyWork_Dev2026!"

# 2 usuarios adicionales por cada rol interno no-Resolutor (el 1ro de cada rol ya lo siembra
# la migración 009: admin@sywork.net, coordinador@sywork.net, qm@sywork.net).
ROLE_USERS = [
    ("admin2@sywork.net", "admin2", "Admin"),
    ("admin3@sywork.net", "admin3", "Admin"),
    ("coordinador2@sywork.net", "coordinador2", "Coordinador"),
    ("coordinador3@sywork.net", "coordinador3", "Coordinador"),
    ("qm2@sywork.net", "qm2", "QM"),
    ("qm3@sywork.net", "qm3", "QM"),
]

# Resolutores nuevos — junto con resolutor@sywork.net (migración 009) dan el mínimo de 4.
RESOLVER_USERS = [
    ("resolutor2@sywork.net", "resolutor2"),
    ("resolutor3@sywork.net", "resolutor3"),
    ("resolutor4@sywork.net", "resolutor4"),
]

# 3 skills por Recurso de Resolutor, tomadas del catálogo de 8 ya sembrado (migración 004).
# Combinación variada a propósito (no las mismas 3 para los 4) para ejercitar pruebas de
# asignación/reasignación por skill y carga (specs 010, 023, 024); cubre las 8 skills al
# menos una vez entre los 4 Resolutores. Incluye también al Resolutor ya existente de la
# migración 009, que hoy no tiene Recurso/skills propios.
RESOLVER_RESOURCE_SKILLS = {
    "resolutor@sywork.net": ["JDE_GL", "JDE_AP", "API_REST"],
    "resolutor2@sywork.net": ["JDE_AR", "ORACLE_FUSION", "SQL_ORACLE"],
    "resolutor3@sywork.net": ["ORACLE_CRM", "API_REST", "ORCHESTRATOR"],
    "resolutor4@sywork.net": ["SQL_ORACLE", "JDE_GL", "ORACLE_FUSION"],
}

# Verificación de zona horaria de clientes ya sembrados por seed_clients_aris_vaxthera.py.
CLIENT_TIMEZONES = [
    ("Aris", "America/Bogota"),
    ("Vaxthera", "America/Guayaquil"),
]


def _converge_user(users: UserRepository, roles: RoleRepository, email: str, username: str,
                    role_name: str, resumen: dict) -> User:
    role = roles.get_by_name(role_name)
    assert role, f'Rol "{role_name}" no encontrado — requerido para sembrar usuarios de desarrollo'

    existing = users.get_by_email(email)
    if existing:
        if existing.role.name != role_name:
            users.update_role(existing.id, role.id)
            resumen["actualizados"].append(f'usuario {email} (rol {existing.role.name} -> {role_name})')
        else:
            resumen["omitidos"].append(f'usuario {email}')
        return existing

    user = users.create(User(
        id=uuid.uuid4(), email=email, username=username, role=role,
        password_hash=generate_password_hash(SEED_PASSWORD_DEV),
    ))
    resumen["creados"].append(f'usuario {email} (rol {role_name})')
    return user


def main() -> None:
    db = get_db()
    users = UserRepository(db)
    roles = RoleRepository(db)
    resources = ResourceRepository(db)
    skills = SkillRepository(db)
    clients = ClientRepository(db)

    resumen = {"creados": [], "actualizados": [], "omitidos": []}

    # ── US1: 2 usuarios adicionales por rol interno (Admin, Coordinador, QM) ───────────
    for email, username, role_name in ROLE_USERS:
        _converge_user(users, roles, email, username, role_name, resumen)

    # ── US2: Resolutores nuevos hasta el mínimo de 4, cada uno con Recurso y 3 skills ──
    for email, username in RESOLVER_USERS:
        _converge_user(users, roles, email, username, "Resolutor", resumen)

    for email, skill_codes in RESOLVER_RESOURCE_SKILLS.items():
        user = users.get_by_email(email)
        assert user, f'Usuario Resolutor {email} no encontrado tras sembrar usuarios'

        resource = resources.get_by_user_id(user.id)
        if not resource:
            full_name = f'Resolutor Semilla ({email.split("@", 1)[0]})'
            resource = resources.create(Resource.create(full_name=full_name, email=email, user_id=user.id))
            resumen["creados"].append(f'recurso {email}')
        else:
            resumen["omitidos"].append(f'recurso {email}')

        assert len(skill_codes) == 3, f'Se esperaban exactamente 3 skills para {email}, hay {len(skill_codes)}'
        skill_objs = [skills.get_by_code(code) for code in skill_codes]
        missing = [code for code, obj in zip(skill_codes, skill_objs) if not obj]
        assert not missing, f'Skills no encontradas en el catálogo para {email}: {missing}'

        target_ids = sorted(str(s.id) for s in skill_objs)
        current_ids = sorted(str(s.id) for s in resource.skills)
        if current_ids != target_ids:
            resources.update_skills(resource.id, [s.id for s in skill_objs])
            resumen["actualizados"].append(f'skills de {email} -> {skill_codes}')
        else:
            resumen["omitidos"].append(f'skills de {email}')

    # ── US4: verificación/corrección de timezone de Aris y Vaxthera ────────────────────
    for name, expected_timezone in CLIENT_TIMEZONES:
        client = clients.get_by_name(name)
        if not client:
            continue
        if client.timezone != expected_timezone:
            client.timezone = expected_timezone
            clients.update(client)
            resumen["actualizados"].append(f'timezone de {name} -> {expected_timezone}')
        else:
            resumen["omitidos"].append(f'timezone de {name}')

    close_db()

    print(f'Seed completo: {len(resumen["creados"])} creados, {len(resumen["actualizados"])} '
          f'actualizados para converger con el seed, {len(resumen["omitidos"])} sin cambios.')
    for label, items in (("Creados", resumen["creados"]), ("Actualizados", resumen["actualizados"])):
        if items:
            print(f'{label}:')
            for item in items:
                print(f'  - {item}')


if __name__ == "__main__":
    sys.exit(main())
