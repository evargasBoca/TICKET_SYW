# Quickstart: Validar la Ampliación de Datos Semilla

Prerrequisito: ambiente Docker Compose levantado (Dev, o `sywork_test` — ver
`specs/027-docker-entornos-aislados/quickstart.md`) con migraciones ya aplicadas
(`alembic upgrade head`, incluye la migración 009 que siembra los 4 usuarios base).

## 1. Ejecutar el seed

```bash
docker exec sywork_backend python -m backend.scripts.seed_dev_users
```

Salida esperada: resumen de creados/actualizados/omitidos (mismo formato que
`seed_clients_aris_vaxthera.py`), sin errores.

## 2. Verificar usuarios por rol (User Story 1)

Repetir el comando y confirmar que la segunda ejecución no crea usuarios nuevos (idempotencia,
FR-006):

```bash
docker exec sywork_backend python -m backend.scripts.seed_dev_users
```

Iniciar sesión (`POST /api/auth/login` o la pantalla de Login) con al menos un usuario de cada rol
(por ejemplo `admin2@sywork.net`, `coordinador2@sywork.net`, `qm2@sywork.net`) usando la contraseña
`SyWork_Dev2026!` documentada en `docs/credenciales_dev.txt`. Cada inicio de sesión debe ser exitoso.

## 3. Verificar Resolutores con Recurso y skills (User Story 2)

En Maestros > Recursos, confirmar que existen al menos 4 Recursos vinculados a un usuario con rol
Resolutor (`resolutor@sywork.net`, `resolutor2@sywork.net`, `resolutor3@sywork.net`,
`resolutor4@sywork.net`), y que cada uno tiene exactamente 3 skills activas del catálogo existente
(ver tabla en `data-model.md`).

## 4. Verificar el documento de credenciales (User Story 3)

Abrir `docs/credenciales_dev.txt` y confirmar:
- Aparece una fila por cada uno de los 13 usuarios internos (4 base + 9 nuevos) y por los 3 usuarios
  "Usuario/cliente" de Aris/Vaxthera.
- No aparece `contacto.demo@clienteexterno.com` (fixture de tests, no un usuario sembrado real).
- La contraseña documentada para los usuarios internos (`SyWork_Dev2026!`) funciona para iniciar
  sesión con cualquiera de ellos.

## 5. Verificar timezone de Aris/Vaxthera (User Story 4)

```bash
docker exec sywork_backend python -c "
from backend.infra.database import get_db, close_db
from backend.infra.repositories.client_repo import ClientRepository
db = get_db()
clients = ClientRepository(db)
for name, expected in [('Aris', 'America/Bogota'), ('Vaxthera', 'America/Guayaquil')]:
    c = clients.get_by_name(name)
    assert c.timezone == expected, f'{name}: esperado {expected}, encontrado {c.timezone}'
    print(f'{name}: OK ({c.timezone})')
close_db()
"
```

Salida esperada: `Aris: OK (America/Bogota)` y `Vaxthera: OK (America/Guayaquil)`, sin `AssertionError`.

## Notas

- Este quickstart es de validación manual; por Principio VII de la Constitución, no se agrega una
  suite de pruebas automatizadas de gran volumen para este script de datos semilla.
- Si el script se corre contra un ambiente donde ya se sembraron manualmente algunos de estos emails
  con un rol distinto, el script actualiza el rol para converger (no falla ni duplica).
