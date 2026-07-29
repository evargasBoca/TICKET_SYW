# Quickstart: Validación de Deshabilitación de Usuarios/Cliente y Reportes Dinámicos

Guía de verificación end-to-end contra Docker real, mismo patrón usado en features previas
(ej. `specs/032-.../quickstart.md`).

## Prerrequisitos

- Entorno Docker de desarrollo levantado (`docker compose up`).
- Un Usuario/cliente de prueba (ver `ClientContactsPage.tsx`) con al menos un ticket histórico
  y un Proyecto asignado.
- Acceso con un usuario Coordinador (permiso `client_contacts:manage` y, tras esta feature,
  `reports:view`).
- Al menos 3-5 tickets de prueba con datos variados de Cliente/Proyecto/Encargado/tiempos, para
  poder verificar filtros y agregaciones con un dataset pequeño (Principio VII — no se necesita
  un volumen grande para validar).

## US1 — Deshabilitar y reactivar un Usuario/cliente

1. En "Usuarios/cliente", localizar el contacto de prueba y cambiar su estado a Inactivo.
2. Cerrar sesión e intentar iniciar sesión con las credenciales de ese Usuario/cliente.
3. Verificar que el login se rechaza con un mensaje de cuenta deshabilitada.
4. Desde un ticket nuevo, abrir el selector de solicitante/encargado y verificar que ese
   Usuario/cliente ya no aparece como opción.
5. Verificar que el ticket histórico de ese Usuario/cliente sigue mostrando su nombre y datos
   sin cambios.
6. Reactivar el Usuario/cliente y repetir el paso 2: el login debe funcionar de nuevo.

**Resultado esperado**: SC-001, SC-002, SC-003.

## US2 — Reporte de Tickets con filtros básicos

1. Entrar al nuevo menú "Reportes".
2. Verificar que la tabla muestra, como mínimo, tiempo total registrado, Encargado, tiempo de
   primer contacto, tiempo de ejecución/resolución, Cliente, Proyecto, Proceso, Herramienta y
   Skills para cada ticket.
3. Aplicar un filtro de rango de fechas junto con un filtro de Cliente y uno de Encargado.
4. Verificar que la tabla muestra únicamente los tickets que cumplen los tres filtros a la vez.
5. Con un usuario sin el permiso `reports:view`, intentar entrar al menú "Reportes" y verificar
   que el acceso se deniega.

**Resultado esperado**: SC-004 (parcial, sin exportar todavía).

## US3 — Personalizar columnas

1. En el reporte ya filtrado, ocultar dos columnas (ej. Proceso y Herramienta) y reordenar las
   restantes.
2. Verificar que la tabla refleja de inmediato la nueva selección y orden, sin perder el filtro
   aplicado.

## US4 — Agregaciones

1. Sobre el reporte filtrado, aplicar "Suma" sobre la columna de tiempo total registrado.
2. Verificar que el total mostrado corresponde a la suma real de esa columna para **todas** las
   filas que cumplen el filtro (no solo la página visible, si hay paginación).
3. Intentar aplicar una agregación numérica sobre la columna Cliente o Skills y verificar que la
   opción no está disponible o se rechaza.

**Resultado esperado**: SC-004.

## US5 — Exportar a Excel

1. Con un filtro aplicado y al menos una columna oculta, pulsar "Exportar a Excel".
2. Abrir el archivo `.xlsx` descargado y verificar que contiene exactamente las columnas
   visibles, en el orden mostrado en pantalla, y solo las filas que cumplen el filtro (incluidas
   las que estén fuera de la página actual, si hay paginación).
3. Aplicar un filtro que no devuelva ninguna fila y exportar: verificar que el sistema avisa que
   no hay datos, en vez de descargar un archivo vacío sin explicación.

**Resultado esperado**: SC-006.

## US6 — Guardar y reutilizar una Vista Personalizada

1. Configurar columnas, un filtro y una agregación; guardar como Vista Personalizada con un
   nombre (ej. "Mi vista de Soporte").
2. Salir del módulo de Reportes y volver a entrar.
3. Cargar la Vista Personalizada guardada y verificar que se restauran exactamente las mismas
   columnas, orden, filtros y agregaciones.
4. Iniciar sesión con otro usuario con permiso `reports:view` y verificar que esa Vista
   Personalizada no aparece en su propia lista.
5. Guardar una nueva vista reutilizando el mismo nombre que la ya guardada y confirmar que se
   actualiza (upsert) en vez de duplicarse.

**Resultado esperado**: SC-005.
