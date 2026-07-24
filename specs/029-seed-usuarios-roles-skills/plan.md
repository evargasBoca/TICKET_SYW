# Implementation Plan: Ampliación de Datos Semilla (Usuarios por Rol, Resolutores con Skills y Verificación de Calendarios)

**Branch**: `develp_Jp` | **Date**: 2026-07-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/029-seed-usuarios-roles-skills/spec.md`

## Summary

Ampliar el proceso de datos semilla para que cualquier ambiente recién instalado tenga suficientes
usuarios de prueba: 2 usuarios adicionales por cada uno de los 4 roles internos (Admin, Coordinador,
QM, Resolutor), un mínimo de 4 usuarios con rol Resolutor —cada uno con perfil de Recurso y 3 skills
asignadas del catálogo existente—, todos con la misma contraseña estándar ya usada por el seed base
(`SyWork_Dev2026!`). Se implementa como un **nuevo script Python idempotente**
(`backend/scripts/seed_dev_users.py`), siguiendo el mismo patrón que
`backend/scripts/seed_clients_aris_vaxthera.py`, en vez de tocar la migración 009 ya aplicada en
ambientes reales. El script también verifica/corrige la zona horaria de los clientes Aris
(`America/Bogota`) y Vaxthera (`America/Guayaquil`), y se reescribe `docs/credenciales_dev.txt` como
documento único y autoritativo de todas las credenciales sembradas, eliminando la entrada de un
fixture de pruebas automatizadas que no corresponde a un usuario real sembrado.

## Technical Context

**Language/Version**: Python 3.12 (mismo que el resto de `backend/`, sin versión nueva)

**Primary Dependencies**: SQLAlchemy (repositorios ya existentes), Werkzeug `generate_password_hash`
(ya usado en migración 009 y en `seed_clients_aris_vaxthera.py`) — sin dependencias nuevas.

**Storage**: PostgreSQL 16 (mismo esquema ya migrado; esta funcionalidad no agrega tablas ni columnas)

**Testing**: Verificación manual vía `quickstart.md` contra un ambiente Docker real (mismo patrón que
`specs/026-seed-clientes-proyectos/quickstart.md`); no se agregan pruebas automatizadas nuevas —
Principio VII de la Constitución restringe correr la suite completa y limita el volumen de datos de
prueba insertados por test.

**Target Platform**: Backend Flask en contenedor Docker (Dev/Test/Prod-validación), ejecutado vía
`docker exec sywork_backend python -m backend.scripts.seed_dev_users` (mismo patrón de invocación que
`seed_clients_aris_vaxthera.py`)

**Project Type**: Script de datos semilla (backend, sin componente frontend)

**Performance Goals**: N/A — script de un solo uso/reintentable, no está en una ruta caliente de la aplicación

**Constraints**: Cero dependencias nuevas (Principio V); no modificar la migración 009 ya aplicada en
ambientes reales; no crear ni modificar tablas/columnas; reutilizar la contraseña estándar existente;
mantener el script re-ejecutable sin duplicar datos (idempotencia, igual que el seed de Aris/Vaxthera)

**Scale/Scope**: ~9 usuarios nuevos (2 Admin + 2 Coordinador + 2 QM + 3 Resolutor), hasta 4 perfiles
de Recurso con 3 skills cada uno (12 asignaciones skill-recurso), 1 archivo de documentación reescrito,
2 clientes verificados (no creados). Alcance deliberadamente pequeño por el Principio VII.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. API-First y Dominio Primero**: N/A para este alcance — no se agregan endpoints nuevos; el
  script reutiliza los repositorios de Capa 2 (`UserRepository`, `ResourceRepository`, `RoleRepository`,
  `ClientRepository`) exactamente como ya hace `seed_clients_aris_vaxthera.py`. PASA.
- **II. Clean Architecture**: el script vive en `backend/scripts/` (mismo nivel que los seeders
  existentes) y solo orquesta llamadas a repositorios/entidades de dominio ya definidas; no agrega
  lógica de negocio nueva al dominio. PASA.
- **III. Tipado Estricto**: Python con type hints en las funciones del script, igual que el seed
  existente. No hay código TypeScript/frontend en este alcance. PASA.
- **IV. Seguridad en Profundidad**: la contraseña sembrada es la constante de desarrollo ya conocida
  y documentada (`SyWork_Dev2026!`), nunca un secreto real; el documento de credenciales ya trae la
  advertencia de rotación obligatoria antes de Producción real (se conserva). PASA.
- **V. Gobernanza de Librerías**: no se agrega ninguna dependencia a `requirements.txt`. PASA.
- **VI. AI-Native**: los Recursos Resolutor sembrados usan las etiquetas de skill ya parametrizadas
  del catálogo existente (`JDE_GL`, `API_REST`, etc.), sin introducir taxonomía nueva. PASA.
- **VII. Alcance de Sesión y Eficiencia**: el cambio se limita a archivos de seed/fixtures y al
  documento de credenciales, tal como exige el pedido explícito del usuario; no se ejecuta la suite
  de tests global; el volumen de datos sembrados es acotado (~9 usuarios, 4 recursos). PASA.

No hay violaciones que requieran la tabla de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/029-seed-usuarios-roles-skills/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

(No `contracts/` — esta funcionalidad no expone ni modifica ningún endpoint de API; ver nota en
"Define interface contracts" más abajo.)

### Source Code (repository root)

```text
backend/
├── scripts/
│   ├── seed_clients_aris_vaxthera.py   # existente (spec 026), no se modifica
│   └── seed_dev_users.py               # NUEVO — esta funcionalidad
├── domain/entities/
│   ├── user.py                         # existente, reutilizado sin cambios
│   └── resource.py                     # existente, reutilizado sin cambios (Resource, Skill)
└── infra/repositories/
    ├── user_repo.py                    # existente, reutilizado sin cambios
    ├── role_repo.py                    # existente, reutilizado sin cambios
    ├── resource_repo.py                # existente, reutilizado sin cambios (ResourceRepository, SkillRepository)
    └── client_repo.py                  # existente, reutilizado sin cambios (verificación de timezone)

docs/
└── credenciales_dev.txt                # REESCRITO — documento único y autoritativo
```

**Structure Decision**: Opción "Single project" simplificada a solo backend — no hay cambios de
frontend en esta funcionalidad. El nuevo script se agrega junto al seed ya existente en
`backend/scripts/`, reutilizando entidades y repositorios de las Capas 1 y 2 tal cual están, sin
tocar la Capa 3 (API/rutas Flask) ni el frontend.

## Complexity Tracking

*(vacío — no hay violaciones de la Constitución que justificar)*
