---
id: ITER-007
fecha: 2026-07-27
version_probada: 0cdc31a
entorno: Docker local
responsable_sesion: Juan Murcia
alcance: Reporte puntual — Tickets > Detalle del Ticket (usabilidad del layout de comentarios/acciones) y SLA Configurable (identificación de cliente en proyectos homónimos)
estado_iteracion: Cerrada
---

# ITER-007 — Iteración de pruebas

## Objetivo de la iteración

Reporte de una observación puntual sobre la usabilidad del detalle del Ticket, específicamente la disposición de las secciones "Clasificación" y "Comentarios y acciones" frente al scroll de la línea de tiempo del historial.

## Resumen de observaciones

| ID | Módulo/Pantalla | Tipo | Estado | Reportado por |
|---|---|---|---|---|
| OBS-0042 | Tickets > Detalle del Ticket | Mejora | Abierta | Juan Murcia |
| OBS-0043 | SLA Configurable | Mejora | Abierta | Juan Murcia |

## Detalle de observaciones

### OBS-0042 — Scroll excesivo en el detalle del Ticket por historial de comentarios extenso

- **Módulo/Pantalla:** Tickets > Detalle del Ticket
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Juan Murcia
- **Iteración de origen:** ITER-007
- **Iteración de cierre:** —

**Descripción**
En la pantalla del detalle del ticket, cuando existe un número elevado de comentarios, la línea de tiempo del historial se vuelve extremadamente larga. Esto obliga al usuario a realizar un scroll excesivo únicamente para llegar al área donde se redacta un nuevo comentario o se ejecutan acciones del ticket.

**Resultado esperado / Situación actual**
El historial de comentarios, la caja para redactar un nuevo comentario y los botones de cambio de estado están ordenados de forma secuencial en una sola columna. Todo el contenido hace scroll de forma unificada, desplazando los elementos clave de acción hacia abajo.

**Resultado actual / Propuesta de mejora**
Reorganizar la interfaz para optimizar la usabilidad en el detalle del ticket:

1. Redistribución de componentes: mover la sección de "Clasificación" al lugar donde se encuentra actualmente "Comentarios y acciones", y trasladar toda la sección de "Comentarios y acciones" hacia la columna derecha de la pantalla.
2. Caja de nuevo comentario y acciones fija: mantener fija en la interfaz la sección para redactar nuevos comentarios y realizar cambios de estado (acciones), evitando que se desplace con el navegador.
3. Historial de comentarios independiente: configurar únicamente la lista/historial de comentarios pasados con un scroll interno independiente.

**Criterios de aceptación**
- [ ] La sección de "Comentarios y acciones" se visualiza en la columna derecha de la pantalla.
- [ ] La sección de "Clasificación" ocupa el espacio asignado anteriormente a "Comentarios y acciones".
- [ ] La caja para redactar un nuevo comentario y las acciones de cambio de estado permanecen fijas en pantalla sin ocultarse al desplazarse.
- [ ] La lista del historial de comentarios cuenta con su propio scroll vertical (interno), manteniendo un alto máximo definido.
- [ ] La interfaz mantiene un diseño responsivo y alineado con los estándares visuales del sistema.

**Evidencia**
_Sin evidencia adjunta en esta observación._

### OBS-0043 — SLA Configurable no identifica el cliente en proyectos homónimos

- **Módulo/Pantalla:** SLA Configurable
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Juan Murcia
- **Iteración de origen:** ITER-007
- **Iteración de cierre:** —

**Descripción**
En la sección de SLA Configurable no se identifica el cliente asociado a cada proyecto. Esto genera ambigüedad cuando existen proyectos con el mismo nombre pertenecientes a distintos clientes: en el selector "Filtrar por proyecto" aparece "Soporte" dos veces (uno por cada cliente que tiene un proyecto "Soporte") sin ninguna forma de distinguir a cuál corresponde cada uno.

**Resultado esperado / Situación actual**
El selector "Filtrar por proyecto" y la tabla de reglas de SLA solo muestran el nombre del proyecto, sin ninguna referencia al cliente. Al crear una nueva regla de SLA tampoco se indica ni se puede seleccionar el cliente, únicamente el proyecto.

**Resultado actual / Propuesta de mejora**
1. En el selector "Filtrar por proyecto", mostrar el cliente junto al nombre del proyecto (ej. "Cliente X — Soporte") para diferenciar proyectos homónimos.
2. En el formulario de creación/edición de una regla de SLA, mostrar el cliente del proyecto seleccionado.
3. Agregar una columna "Cliente" en la tabla de reglas de SLA.

**Criterios de aceptación**
- [ ] El selector "Filtrar por proyecto" muestra el cliente junto al nombre del proyecto para distinguir proyectos homónimos.
- [ ] El formulario de creación/edición de una regla de SLA muestra el cliente del proyecto seleccionado.
- [ ] La tabla de reglas de SLA incluye una columna "Cliente".
- [ ] Proyectos con el mismo nombre pero distinto cliente se distinguen claramente en toda la sección de SLA Configurable.

**Evidencia**
_Captura compartida por el reportante en el chat (selector "Filtrar por proyecto" con "Soporte" duplicado y tabla de reglas de SLA sin columna de Cliente); pendiente de guardar como `images/OBS-0043-01.png`._
