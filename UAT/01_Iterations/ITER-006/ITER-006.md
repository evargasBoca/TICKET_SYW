---
id: ITER-006
fecha: 2026-07-27
version_probada: No aplica — propuesta de diseño, no retest de una versión desplegada
entorno: No aplica
responsable_sesion: Camilo Reyes
alcance: No es un barrido de la aplicación. Registra una propuesta de ampliación de alcance sobre OBS-0001, elaborada por el Gerente de Desarrollo tras usar la pestaña "Accesos y conexiones" ya implementada (spec 018) y compararla contra su flujo real de trabajo (Cuadernos de Teamwork + un documento histórico de accesos a instancias Oracle de un cliente real).
estado_iteracion: Cerrada
---

# ITER-006 — Iteración de pruebas

## Objetivo de la iteración

`OBS-0001` ("ampliar IPs VPN/Credenciales VPN a múltiples accesos") ya fue implementada de punta a punta (spec `018-cliente-accesos-conexiones`) y está `Lista para Validar`. Al usarla en la práctica para reemplazar los Cuadernos de Teamwork, aparecieron tres límites que el spec original no cubría — no son defectos de lo ya construido, sino alcance adicional real:

1. El enum de tipos de acceso es fijo en código (`vpn`, `system_url`, `remote_desktop`) — no cubre Base de datos, Servidor/instancia, ni tipos futuros (APEX, NetSuite, etc.).
2. El modelo asume 1 acceso = 1 usuario. En la práctica un mismo host (ERP, OIC, APEX) es compartido por varios usuarios con credenciales propias — obliga a repetir la URL por cada persona.
3. El manual de conexión adjunto vive siempre a nivel de cliente en general, sin poder anclarse a un acceso puntual.

Se registra como observación nueva (`OBS-0041`), no como reescritura de `OBS-0001`, porque `ITER-001.md` ya es inmutable y el alcance propuesto aquí excede lo que pedía el criterio de aceptación original.

## Resumen de observaciones

| ID | Módulo/Pantalla | Tipo | Estado | Reportado por |
|---|---|---|---|---|
| OBS-0041 | Clientes > Accesos y conexiones | Mejora | Abierta | Camilo Reyes |

## Detalle de observaciones

### OBS-0041 — Accesos y conexiones: catálogo de tipos administrable, credenciales múltiples por acceso, adjunto por acceso

- **Módulo/Pantalla:** Clientes > Accesos y conexiones
- **Tipo:** Mejora
- **Estado:** Abierta
- **Reportado por:** Camilo Reyes
- **Iteración de origen:** ITER-006
- **Iteración de cierre:** —

**Descripción**

Uso Teamwork (Cuadernos) para documentar accesos técnicos de clientes: instancias, VMs, VPNs, bases de datos, credenciales y manuales de conexión. Por costo y funcionalidad estoy migrando a TICKET_SYW. La pestaña "Accesos y conexiones" (resultado de `OBS-0001`) resuelve el problema original, pero al usarla para reemplazar de verdad a Teamwork aparecen tres huecos:

- El tipo de acceso es un enum cerrado (`vpn`, `system_url`, `remote_desktop`); no hay forma de agregar "Base de datos", "APEX", "NetSuite", etc. sin un despliegue de código.
- Un mismo acceso (ej. un ERP Cloud, un OIC) suele tener una sola URL compartida por varios usuarios, cada uno con su propia credencial — el modelo actual, al mezclar host y credencial en la misma fila, obliga a duplicar la URL por cada usuario.
- El manual/instructivo de conexión solo puede adjuntarse a nivel de cliente en general, no a un acceso puntual — con varios accesos por cliente no queda claro a cuál corresponde cada adjunto.

Se adjunta una propuesta visual completa (HTML) con el modelo de datos sugerido, ejemplos con datos ficticios y un mockup de la pantalla — ver Evidencia.

**Resultado esperado / Situación actual**

Situación actual: `client_access` es 1 fila = 1 host + 1 usuario + 1 contraseña, con `access_type` como enum fijo de tres valores y adjuntos únicamente a nivel de cliente.

Propuesta (detalle completo en el adjunto):
- Nuevo catálogo administrable `catalog_access_types` (mismo patrón que `catalog_teams` de `OBS-0024`) en vez de un enum fijo — cada tipo nuevo toma automáticamente el siguiente color disponible de una paleta fija, sin que el usuario elija colores a mano.
- Nueva tabla hija `client_access_credentials` (`client_access_id` FK, etiqueta, usuario, contraseña cifrada, notas) — 1 acceso puede tener N credenciales; una contraseña compartida entre varios usuarios simplemente se repite como valor en varias filas, sin modelado especial.
- `environment` deja de estar restringido a `system_url`; aplica a cualquier tipo.
- Nuevo campo `port`, propio del acceso (hoy se concatena a mano dentro del host).
- `client_access_attachments.client_access_id` (FK opcional/nullable) para anclar un manual a un acceso puntual, sin perder los adjuntos generales del cliente.
- Credenciales de tipo OAuth (Client ID/Secret, ej. OIC) reutilizan los mismos campos usuario/contraseña — mismo cifrado, sin columnas nuevas; Scope/Token URL, al ser propiedades del endpoint y no de la credencial, quedan en las notas del acceso.

**Resultado actual / Propuesta de mejora**

Ver el documento adjunto (`OBS-0041-propuesta-accesos-conexiones.html`) para el detalle completo: comparación "hoy vs propuesta" con un caso ilustrativo, tabla de cambios de modelo campo por campo, mockup de la pestaña rediseñada y consideraciones de seguridad (cifrado y RLS reutilizados, sin cambios).

**Criterios de aceptación**
- [ ] Los tipos de acceso se administran desde un catálogo (Catálogos), no desde un enum fijo en código.
- [ ] Un acceso con múltiples usuarios permite registrar N credenciales sin repetir host/URL.
- [ ] `environment` (Producción/Pruebas/etc.) se puede indicar en cualquier tipo de acceso, no solo en el que hoy es `system_url`.
- [ ] El host y el puerto se registran en campos separados.
- [ ] Un manual/adjunto se puede asociar a un acceso puntual, además de a los adjuntos generales del cliente.
- [ ] El cifrado de contraseñas y las políticas RLS ya vigentes se mantienen sin degradar la seguridad actual.

**Evidencia**
Propuesta completa en `attachments/OBS-0041-propuesta-accesos-conexiones.html` (abrir en el navegador). Documento exploratorio del Gerente de Desarrollo — no es una especificación aprobada; debe validarse contra `specs/018-cliente-accesos-conexiones/` antes de construirse.
