# Quickstart: Validación de OBS-0042/OBS-0043

Guía de verificación end-to-end contra Docker real, siguiendo el mismo patrón usado en features previas de este repo (ej. `specs/028-.../quickstart.md`). No sustituye el retest formal del framework UAT (`UAT/CONVENTIONS.md`) — deja el backlog en `Lista para Validar` para que el validador (Juan Murcia u otro consultor UAT asignado) confirme.

## Prerrequisitos

- Entorno Docker de desarrollo levantado (`docker compose up`, ver `README.md` del repo).
- Un ticket de prueba con un número elevado de comentarios (suficientes para exceder el alto visible en pantalla — usar el seed existente o agregar comentarios manualmente).
- Al menos dos clientes con un proyecto del mismo nombre y con reglas de SLA configuradas (ya cumplido hoy por el seed: Aris y Vaxthera, ambos con proyecto "Soporte" — ver `backend/scripts/seed_clients_aris_vaxthera.py`).
- Acceso con un usuario con permiso `sla_rules:manage` (Admin/Coordinador) para SLA Configurable.

## OBS-0042 — Layout del Detalle del Ticket

1. Abrir el ticket de prueba con historial de comentarios extenso.
2. Verificar que la Card "Comentarios y acciones" (redacción de nuevo comentario + cambio de estado) se muestra en la columna derecha, donde antes estaba "Clasificación".
3. Verificar que la Card "Clasificación" se muestra en la columna donde antes estaba "Comentarios y acciones".
4. Desplazarse por el historial de comentarios: confirmar que la caja de nuevo comentario y los botones de cambio de estado permanecen visibles/accesibles sin necesidad de scrollear toda la página.
5. Confirmar que el desplazamiento del historial queda contenido en su propio contenedor (scroll interno), sin arrastrar el resto de la página.
6. Redimensionar la ventana (o usar las herramientas de responsive del navegador) a un ancho reducido y repetir 2-5; confirmar que no hay overlaps ni contenido cortado.

**Resultado esperado**: SC-001, SC-002, SC-003.

## OBS-0043 — Cliente en SLA Configurable

1. Abrir Maestros > SLA Configurable.
2. Abrir el selector "Filtrar por proyecto": verificar que cada opción muestra el cliente junto al nombre del proyecto (ej. "Aris — Soporte" y "Vaxthera — Soporte" como opciones distintas y distinguibles).
3. Abrir "Nueva regla de SLA" (o editar una existente) y seleccionar un proyecto: verificar que el formulario muestra el cliente del proyecto seleccionado.
4. Verificar que la tabla de reglas de SLA incluye una columna "Cliente" con el nombre correcto para cada fila, incluyendo los dos proyectos "Soporte" de clientes distintos.

**Resultado esperado**: SC-004.

## Cierre de trazabilidad UAT

1. Tras validar ambos puntos, actualizar `UAT/02_Backlog/BACKLOG.md`: `OBS-0042` y `OBS-0043` pasan de `Abierta` a `Lista para Validar` (FR-009).
2. Confirmar que `UAT/01_Iterations/ITER-007/ITER-007.md` no fue editado en su contenido narrativo.

**Resultado esperado**: SC-005.
