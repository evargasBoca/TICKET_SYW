# Feature Specification: Deshabilitación de Usuarios/Cliente y Módulo de Reportes Dinámicos (Interactive Grid)

**Feature Branch**: `034-usuarios-inactivos-reportes-grid`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Deshabilitación de Usuarios/Clientes y Módulo de Reportes Dinámicos (Estilo Oracle APEX Grid) — (1) activar/deshabilitar cuentas de rol Usuario/cliente: una cuenta deshabilitada no puede iniciar sesión ni ser asignada a nuevos tickets/proyectos, pero su historial se conserva intacto. (2) Nuevo menú 'Reportes' con un grid interactivo: columnas mostrables/ocultables/reordenables, filtros por rango de fechas/Cliente/Proyecto/Encargado, agregaciones (suma/promedio/conteo) sobre columnas numéricas o de tiempo, guardado de la configuración como 'Vista Personalizada' recargable, y exportación a Excel (.xlsx). Métricas: cantidad de tickets, tiempo total registrado, Encargado, tiempo de primer contacto, tiempo de ejecución/resolución, Cliente, Proyecto, Proceso, Herramienta, lista de skills. Nota de alcance del usuario: modificar únicamente las vistas de administración de usuarios (campo de estado) y el nuevo módulo de Reportes, sin refactorizar otras áreas; pruebas nuevas (agregación/exportación) con dataset mock de 5-10 registros, sin correr la suite completa."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deshabilitar el acceso de un Usuario/cliente (Priority: P1)

Como Coordinador o Administrador, quiero deshabilitar la cuenta de un Usuario/cliente que ya no debe operar en el sistema (ej. dejó la empresa cliente), para que no pueda iniciar sesión ni ser elegido en nuevas asignaciones, sin perder el historial de tickets y comentarios que ya generó.

**Why this priority**: Es un control de acceso y seguridad básico, independiente del módulo de reportes, y de alto valor inmediato (evita accesos indebidos).

**Independent Test**: Desde la pantalla de administración de Usuarios/cliente, cambiar el estado de una cuenta a Inactivo y verificar que el login con esa cuenta se rechaza y que ya no aparece como opción al asignar un ticket nuevo, mientras sus tickets históricos siguen mostrando su nombre normalmente.

**Acceptance Scenarios**:

1. **Given** un Usuario/cliente activo con tickets ya creados, **When** un Coordinador lo deshabilita, **Then** el sistema confirma el cambio de estado y el historial de tickets/comentarios de ese usuario permanece sin cambios.
2. **Given** un Usuario/cliente deshabilitado, **When** intenta iniciar sesión con sus credenciales, **Then** el sistema rechaza el acceso con un mensaje claro de cuenta inactiva.
3. **Given** un Usuario/cliente deshabilitado, **When** un Coordinador intenta seleccionarlo como solicitante al crear un ticket o agregarlo a un Proyecto, **Then** no aparece disponible en el selector.
4. **Given** un Usuario/cliente previamente deshabilitado, **When** un Coordinador lo reactiva, **Then** recupera la capacidad de iniciar sesión y de ser seleccionado en nuevas asignaciones.

---

### User Story 2 - Consultar el Reporte de Tickets con filtros básicos (Priority: P1)

Como Coordinador/QM/Admin, quiero abrir el nuevo menú "Reportes" y ver una tabla con las métricas clave de los tickets (tiempos, Encargado, Cliente, Proyecto, Herramienta, Proceso, Skills), filtrable por rango de fechas, Cliente, Proyecto y Encargado, para analizar la operación sin pedirle un reporte manual a otra persona.

**Why this priority**: Es el núcleo del módulo de Reportes; sin esta base, personalizar columnas, agregar o exportar no tienen sobre qué operar.

**Independent Test**: Entrar al menú "Reportes", aplicar un filtro de rango de fechas y de Cliente, y verificar que la tabla muestra solo los tickets que cumplen esos filtros con las métricas esperadas.

**Acceptance Scenarios**:

1. **Given** el usuario tiene permiso de Reportes, **When** abre el menú "Reportes", **Then** ve una tabla con tickets y, como mínimo, tiempo total registrado, Encargado, tiempo de primer contacto, tiempo de ejecución/resolución, Cliente, Proyecto, Proceso, Herramienta y Skills.
2. **Given** la tabla de Reportes con datos, **When** el usuario filtra por un rango de fechas, un Cliente, un Proyecto y un Encargado a la vez, **Then** la tabla muestra únicamente los tickets que cumplen todos los filtros combinados.
3. **Given** un usuario sin permiso de acceso a Reportes, **When** intenta entrar al menú "Reportes", **Then** el sistema le niega el acceso.

---

### User Story 3 - Personalizar columnas del reporte (Priority: P2)

Como usuario del módulo de Reportes, quiero mostrar, ocultar y reordenar las columnas de la tabla, para ver solo la información relevante para mi análisis actual.

**Why this priority**: Mejora directamente la usabilidad del reporte base (US2), pero el reporte ya es útil sin esto.

**Independent Test**: Ocultar dos columnas y reordenar las restantes; verificar que la tabla refleja inmediatamente esa selección y orden.

**Acceptance Scenarios**:

1. **Given** la tabla de Reportes visible, **When** el usuario oculta una columna, **Then** esa columna deja de mostrarse sin afectar los datos ni los filtros ya aplicados.
2. **Given** la tabla de Reportes visible, **When** el usuario reordena las columnas visibles, **Then** la tabla respeta el nuevo orden.

---

### User Story 4 - Aplicar agregaciones y sumatorias (Priority: P2)

Como usuario del módulo de Reportes, quiero aplicar sumas, promedios o conteos sobre columnas numéricas o de tiempo (ej. suma total de horas trabajadas), para obtener totales sin exportar los datos a otra herramienta.

**Why this priority**: Aporta valor analítico adicional sobre el reporte filtrado, pero depende de que el reporte base (US2) ya exista.

**Independent Test**: Sobre el reporte filtrado, aplicar "Suma" a la columna de tiempo total registrado y verificar que se muestra el total correcto de las filas visibles.

**Acceptance Scenarios**:

1. **Given** el reporte filtrado con una columna numérica o de tiempo visible, **When** el usuario aplica una función de agregación (suma, promedio o conteo), **Then** el sistema muestra el resultado calculado sobre las filas actualmente visibles.
2. **Given** una columna de texto (ej. Cliente) o de lista (ej. Skills), **When** el usuario intenta aplicar una agregación numérica, **Then** el sistema no ofrece esa opción o la rechaza.

---

### User Story 5 - Exportar el reporte a Excel (Priority: P2)

Como usuario del módulo de Reportes, quiero exportar la vista actual (columnas visibles, orden, filtros aplicados) a un archivo Excel, para compartirla o procesarla fuera del sistema.

**Why this priority**: Es una capacidad de alto valor para stakeholders externos al sistema, y funciona ya sobre el reporte base (US2) sin depender de que existan agregaciones o vistas guardadas.

**Independent Test**: Con un filtro aplicado y una columna oculta, exportar a Excel y verificar que el archivo generado contiene exactamente las columnas visibles, en el orden mostrado, y solo las filas que cumplen el filtro.

**Acceptance Scenarios**:

1. **Given** el reporte con filtros y columnas configuradas, **When** el usuario pulsa "Exportar a Excel", **Then** se genera un archivo .xlsx descargable con las filas y columnas visibles en ese momento.
2. **Given** un filtro que no produce ninguna fila, **When** el usuario exporta, **Then** el sistema avisa que no hay datos para exportar en vez de generar un archivo vacío sin explicación.

---

### User Story 6 - Guardar y reutilizar una Vista Personalizada (Priority: P3)

Como usuario frecuente del módulo de Reportes, quiero guardar mi configuración actual (columnas, filtros y agregaciones) como una "Vista Personalizada" nombrada, para volver a cargarla en el futuro sin repetir la configuración manualmente.

**Why this priority**: Es una mejora de conveniencia sobre las capacidades ya entregadas por US2-US4; el módulo es completamente funcional sin ella.

**Independent Test**: Configurar columnas, un filtro y una agregación, guardar como Vista Personalizada con un nombre, salir del módulo, volver a entrar y cargar esa vista, verificando que se restaura exactamente igual.

**Acceptance Scenarios**:

1. **Given** una configuración de columnas, filtros y agregaciones armada, **When** el usuario la guarda con un nombre, **Then** queda disponible para ese usuario en una lista de Vistas Personalizadas.
2. **Given** una Vista Personalizada guardada, **When** el usuario la selecciona en una sesión posterior, **Then** el reporte recupera exactamente las mismas columnas, orden, filtros y agregaciones.
3. **Given** dos usuarios distintos con permiso de Reportes, **When** uno guarda una Vista Personalizada, **Then** el otro usuario no la ve en su propia lista.

### Edge Cases

- ¿Qué ocurre si se intenta reactivar un Usuario/cliente cuyo email ya fue reutilizado por otra cuenta? El sistema debe seguir validando unicidad de email/usuario como ya lo hace hoy.
- ¿Qué ocurre si un Usuario/cliente deshabilitado tiene una sesión ya iniciada? Debe perder acceso a acciones autenticadas en cuanto el sistema vuelva a verificar su estado, sin esperar la expiración natural del token.
- ¿Qué ocurre si el reporte no tiene filas tras aplicar filtros? Debe mostrar un estado vacío claro, no un error.
- ¿Qué ocurre si el rango de fechas ingresado tiene la fecha "desde" posterior a la fecha "hasta"? El sistema debe rechazar el filtro con un mensaje claro.
- ¿Qué ocurre si se intenta guardar una Vista Personalizada con un nombre ya usado por ese mismo usuario? El sistema debe pedir otro nombre o confirmar la sobrescritura.
- ¿Qué ocurre si un usuario sin permiso de Reportes navega directamente a la URL del módulo? Debe recibir acceso denegado igual que cualquier otra pantalla protegida por permiso.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir a un rol con permiso de administración de Usuarios/cliente cambiar el estado de una cuenta de rol Usuario/cliente entre Activo e Inactivo, desde la pantalla de administración de Usuarios/cliente ya existente.
- **FR-002**: Un Usuario/cliente en estado Inactivo NO DEBE poder iniciar sesión; el intento debe rechazarse con un mensaje que indique que la cuenta está deshabilitada.
- **FR-003**: Un Usuario/cliente en estado Inactivo NO DEBE aparecer como opción al seleccionar el solicitante/encargado de un Ticket/Tarea nuevo, ni al agregar personal a un Proyecto.
- **FR-004**: Deshabilitar un Usuario/cliente NO DEBE eliminar ni alterar su historial existente (tickets, comentarios, membresías de proyecto ya creadas antes del cambio de estado).
- **FR-005**: Un Usuario/cliente Inactivo con una sesión ya iniciada DEBE perder acceso a nuevas acciones autenticadas en cuanto el sistema verifique su estado, sin depender de que su token expire de forma natural.
- **FR-006**: El sistema DEBE permitir reactivar (volver a Activo) un Usuario/cliente previamente deshabilitado, restaurando su capacidad de iniciar sesión y de ser seleccionado en nuevas asignaciones.
- **FR-007**: El sistema DEBE ofrecer una nueva sección de navegación llamada "Reportes", visible únicamente para roles con permiso de acceso a este módulo.
- **FR-008**: El Reporte DEBE mostrar, por Ticket/Tarea, como mínimo: tiempo total registrado, Encargado/Resolutor, tiempo de primer contacto, tiempo de ejecución/resolución, Cliente, Proyecto, Proceso, Herramienta y lista de Skills requeridas.
- **FR-009**: El usuario DEBE poder mostrar, ocultar y reordenar dinámicamente las columnas del reporte.
- **FR-010**: El usuario DEBE poder filtrar el reporte, de forma combinable, por rango de fechas, Cliente, Proyecto y Encargado.
- **FR-011**: El usuario DEBE poder aplicar funciones de agregación (suma, promedio, conteo) sobre cualquier columna numérica o de tiempo visible en el reporte, calculadas sobre las filas actualmente filtradas.
- **FR-012**: El sistema NO DEBE permitir aplicar agregaciones numéricas sobre columnas no numéricas (texto o listas, ej. Cliente o Skills).
- **FR-013**: El usuario DEBE poder guardar la configuración actual (columnas visibles y orden, filtros, agregaciones) como una "Vista Personalizada" nombrada, y recargarla posteriormente para restaurarla exactamente.
- **FR-014**: Las Vistas Personalizadas guardadas por un usuario DEBEN ser privadas de ese usuario (no visibles ni accesibles para otros usuarios).
- **FR-015**: El usuario DEBE poder exportar a un archivo Excel (.xlsx) el contenido del reporte tal como se muestra en pantalla (mismas columnas visibles, mismo orden, mismos filtros aplicados).
- **FR-016**: El acceso al módulo de Reportes y a los datos que expone DEBE respetar las mismas reglas de visibilidad de datos ya vigentes en el sistema (un usuario solo ve datos de los Clientes/Proyectos a los que ya tiene acceso).

### Key Entities *(include if feature involves data)*

- **Usuario/Cliente**: entidad de cuenta ya existente; gana un estado Activo/Inactivo gestionable explícitamente desde su pantalla de administración, que determina si puede iniciar sesión o ser elegido en nuevas asignaciones.
- **Vista Personalizada de Reporte**: configuración guardada por un usuario, compuesta por columnas visibles y su orden, filtros aplicados y agregaciones definidas; pertenece a un único usuario.
- **Fila de Reporte de Ticket**: proyección de datos ya existentes en el sistema (Ticket, Cliente, Proyecto, Encargado/Recurso, tiempos de SLA, Herramienta, Proceso, Skills) reunida para consulta y exportación, sin introducir una nueva fuente primaria de datos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un Coordinador o Administrador puede deshabilitar y luego reactivar un Usuario/cliente en menos de 30 segundos desde la pantalla de administración existente.
- **SC-002**: El 100% de los intentos de inicio de sesión con una cuenta de Usuario/cliente deshabilitada son rechazados.
- **SC-003**: El 100% de los Usuarios/cliente deshabilitados quedan excluidos de los selectores de asignación de tickets y proyectos nuevos, sin que se modifique ninguna de sus asignaciones históricas.
- **SC-004**: Un usuario con permiso de Reportes puede armar una vista con columnas elegidas, un filtro combinado y una agregación, y exportarla a Excel en menos de 2 minutos sin asistencia.
- **SC-005**: Una Vista Personalizada guardada se restaura de forma idéntica (mismas columnas, orden, filtros y agregaciones) al volver a cargarla en una sesión posterior.
- **SC-006**: El archivo Excel exportado contiene exactamente las filas y columnas visibles en el reporte en el momento de la exportación, sin filas ni columnas adicionales u omitidas.

## Assumptions

- El estado Activo/Inactivo del Usuario/cliente se gestiona desde la pantalla de administración de Usuarios/cliente ya existente (Maestros); no se crea una pantalla nueva para esto.
- Solo roles internos con el permiso dedicado de Reportes (ej. Coordinador, Admin, QM) acceden al nuevo menú "Reportes"; los Usuarios/cliente no lo ven.
- Las Vistas Personalizadas son privadas por usuario; no hay vistas compartidas o públicas en el alcance de este feature.
- El Reporte reutiliza datos ya existentes en el sistema (Tickets, tiempos de SLA, Recursos, catálogos de Herramienta/Proceso/Skills); no introduce una nueva fuente de datos ni un proceso de recolección adicional.
- El volumen de datos exportable a Excel corresponde al que ya maneja el sistema en sus listados existentes; no se define un límite especial de gran volumen de datos.
- Deshabilitar un Usuario/cliente no dispara una notificación automática hacia ese usuario, salvo que se solicite explícitamente en una iteración futura.
