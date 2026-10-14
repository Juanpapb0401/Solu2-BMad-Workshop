# Edge Case Hunter Review Report: UX Specifications & Scenarios

**Lente:** `--lens edge-case-hunter` (Pure Path Tracer & Boundary Condition Audit)  
**Alcance Auditado:** Carpeta `ux/` (`DESIGN.md`, `EXPERIENCE.md`, `C-UX-Scenarios/*`, `wireframes/*`)  
**Módulo:** Módulo 1 — User, Role, and Subject Access Manager  
**Auditor:** Edge Case Hunter (`bmad-review`)  
**Fecha:** 2026-09-23  
**Estado:** COMPLETED  

---

## 1. Resumen Ejecutivo del Rastreo de Rutas (Path Tracing)

La auditoría mediante la lente `edge-case-hunter` ha ejecutado un recorrido mecánico exhaustivo sobre cada bifurcación condicional, transición de estado de interfaz y límites de dominio en los artefactos de diseño UX del Módulo 1.

Aunque las especificaciones cubren con rigor los caminos felices (*sunshine paths*) y los errores transaccionales principales (como correos corruptos en la ingesta o auto-aprobaciones prohibidas), el rastreo de caminos revela **vacíos de diseño en condiciones de contorno críticas**:
1. **Omisión de Estado Vacío para Identidades sin Asignaturas:** Si un estudiante recién admitido o un docente nuevo ingresa a la plataforma sin materias asignadas (`subjects.length === 0`), el selector de contexto colapsa al intentar desreferenciar el primer elemento.
2. **Ausencia de Flujo y Banner ante Denegación Formal de Escalación:** Se especificó en detalle qué ocurre cuando el Dr. Marcus Vance aprueba la escalación de Sofia, pero no existe diseño visual ni banner de explicabilidad para cuando Vance **rechaza** la solicitud con un motivo pedagógico/operativo.
3. **Pérdida de Estado por Expiración de Token en Auditoría Forense Masiva:** La Dra. Elena Gómez filtrando 100,000 eventos a lo largo de 30 días sufrirá una expiración de token de sesión si la inspección se prolonga; actualmente no existe un mecanismo de re-autenticación *in-situ* que preserve los filtros y la paginación activa.
4. **Colisión de Navegación por Enlaces Profundos (*Deep-Linking*) entre Materias:** Desalineación entre la URL navegada y el encabezado `X-Academic-Subject-Context` fijado en la sesión local.

---

## 2. Catálogo de Rutas no Manejadas y Brechas de Borde

### 2.1 Fronteras de Estados Vacíos (Empty State Boundaries)

#### `EDGE-UX-01`: Estado de Identidad Académica con Cero Cursos Vinculados
- **Ubicación:** `ux/EXPERIENCE.md` — Sección 2.2 (Estado Vacío)
- **Condición de Disparo:** Una identidad autenticada (ej. nuevo estudiante transferido o docente interino) accede al Web Admin Portal o API Explorer antes de que se le asocie a una nómina semestral (`identity.enrolled_subjects = []`).
- **Comportamiento Actual:** El selector de contexto académico asume la presencia de al menos una materia activa (`subjects[0]`), provocando un fallo de renderizado o un selector en blanco sin acciones claras.
- **Consecuencia Potencial:** Pantalla rota o bloqueo operativo para usuarios nuevos sin orientación de soporte.
- **Guardia Propuesta (Snippet UX):**
  ```html
  <!-- Guard: ux/EXPERIENCE.md Sección 2.2 Caso D -->
  <div class="empty-state-unassigned" role="region" aria-label="Sin asignaturas">
    <div class="icon-slate-academic"></div>
    <h3>No tienes asignaturas activas vinculadas para este período</h3>
    <p>Tu cuenta institucional está activa, pero aún no has sido matriculado en asignaturas del ciclo 2026-FALL.</p>
    <div class="actions">
      <button class="btn-primary">Verificar Estado en Registro Central</button>
      <button class="btn-secondary">Contactar a Dr. Marcus Vance (Admin)</button>
    </div>
  </div>
  ```

---

### 2.2 Claridad en Denegación de Escalación Temporal (Escalation Denial Paths)

#### `EDGE-UX-02`: Ausencia de Banner y Estado Visual ante Rechazo Formal de Escalación
- **Ubicación:** `ux/C-UX-Scenarios/scenario-2.md` — Sección [P] y `ux/EXPERIENCE.md` — Sección 3
- **Condición de Disparo:** El Dr. Marcus Vance presiona el botón `[ ✖ Denegar con Motivo ]` en la tarjeta de solicitud `ESC-2026-480-01` de Sofia.
- **Comportamiento Actual:** Se especifica el botón de rechazo para Vance, pero no existe la especificación de qué pantalla o banner ve Sofia cuando su solicitud es denegada, ni si puede volver a solicitarla inmediatamente.
- **Consecuencia Potencial:** Sofia queda con la solicitud colgada en estado indeterminado o satura la bandeja enviando tickets repetidos sin conocer el motivo de la negativa.
- **Guardia Propuesta (Banner E-04):**
  - **Banner Semántico Ámbar/Rojo:** `Banner E-04: Solicitud de Escalación Denegada por Jefatura`
  - **Copy Requerido:**
    > *"Su solicitud de escalación temporal a Instructor-Privileged para CS-480 fue DENEGADA por el Dr. Marcus Vance el 2026-09-23T16:15:00Z.*  
    > **Motivo expuesto por Jefatura:** 'La flota de workstations estará dedicada exclusivamente al examen final de CS101 entre las 14:00 y las 18:00'.*  
    > *Acción permitida: Podrá presentar una nueva solicitud para ventanas posteriores a las 18:00."*
  - **Regla de Cooldown:** Bloqueo del formulario de nueva solicitud para el mismo horario durante 30 minutos.

---

### 2.3 Expiración de Sesión y Resiliencia en Auditoría Masiva (Session Expiry Paths)

#### `EDGE-UX-03`: Expiración de Token de Sesión durante Paginación / Exportación Forense
- **Ubicación:** `ux/C-UX-Scenarios/scenario-4.md` — Sección [P] y [V]
- **Condición de Disparo:** La Dra. Elena Gómez se encuentra en la página 4 de 12 inspeccionando registros de investigación de los últimos 30 días. Su token Bearer JWT de sesión expira por inactividad de seguridad (timeout de 15 minutos).
- **Comportamiento Actual:** La llamada AJAX para la página siguiente o para `[ 📥 Exportar CSV Certificado ]` falla con `HTTP 401 Unauthorized`. La interfaz redirige a la pantalla de login principal, destruyendo el estado en memoria.
- **Consecuencia Potencial:** La auditora pierde el cursor de búsqueda, los filtros avanzados seleccionados y el avance de su reporte, teniendo que reconfigurar la inspección desde cero.
- **Guardia Propuesta (In-Situ Re-Auth Modal):**
  - Intercepción global de respuestas `HTTP 401` en el cliente.
  - Despliegue de un modal de re-autenticación superpuesto (*Overlay Focus Trap*):
    `"Su sesión de auditoría ha expirado por política de seguridad (15 min). Ingrese su contraseña para reanudar su trabajo."`
  - Tras validar credenciales, la petición pendiente (exportación o página 5) se reintenta automáticamente con el nuevo token sin recargar la página ni perder los filtros.

---

### 2.4 Límites de Enlaces Profundos y Truncamiento Visual (Navigation & Display Boundaries)

#### `EDGE-UX-04`: Desalineación entre Enlace Profundo (*Deep Link*) y Contexto Académico Activo
- **Ubicación:** `ux/DESIGN.md` — Sección 1.2 y `ux/wireframes/screen-a-role-conflict-admin.md`
- **Condición de Disparo:** Sofia tiene fijado en su selector local el contexto `CS101`, pero hace clic en un enlace compartido en un chat que apunta a `/subjects/cs-480/evaluator`.
- **Comportamiento Actual:** La interfaz carga la vista de CS-480 pero el encabezado del cliente sigue enviando `X-Academic-Subject-Context: CS101`, provocando denegaciones `403 RESOURCE_SUBJECT_MISMATCH` desconcertantes.
- **Consecuencia Potencial:** Falsos positivos de violación de aislamiento causados por desincronización de UI.
- **Guardia Propuesta:** Sincronización automática de dos vías: si la URL contiene una ruta de asignatura `/subjects/{subject_id}/*`, el cliente actualiza automáticamente el selector y el encabezado `X-Academic-Subject-Context` para coincidir con la ruta, notificando con un micro-toast: `Contexto cambiado automáticamente a CS-480`.

#### `EDGE-UX-05`: Desbordamiento Visual por Longitud Extrema de ARNs en Pantallas Compactas
- **Ubicación:** `ux/DESIGN.md` — Sección 2.3 y `ux/wireframes/screen-b-audit-traceability.md`
- **Condición de Disparo:** El recurso consultado posee un ARN extenso (ej. `urn:uai:subject:nlp-advanced:model:restricted:biomedical-genomics-llm-70b-v2-instruct-awq`) visualizado en un monitor de $1024 \times 768\,\text{px}$.
- **Comportamiento Actual:** La celda de la tabla expande su ancho horizontal, empujando la columna de decisión y hash fuera del viewport visible y rompiendo el alineamiento de la grilla.
- **Consecuencia Potencial:** Pérdida de visibilidad de los veredictos de seguridad en terminales de laboratorio pequeñas.
- **Guardia Propuesta:** Aplicación obligatoria de clase CSS utilitaria:
  ```css
  .cell-arn-truncate {
    max-width: 220px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-family: var(--font-mono);
  }
  .cell-arn-truncate:hover {
    cursor: help;
  } /* Tooltip nativo con ARN completo */
  ```

---

## 3. Matriz de Triage para Decisiones Humanas

A continuación se estructura la matriz formal con las recomendaciones técnicas para la toma de decisión del equipo:

| ID | Severidad | Hallazgo / Caso de Borde | Veredicto Humano | Justificación Técnica del Veredicto |
| :--- | :--- | :--- | :--- | :--- |
| **EDGE-UX-01** | **Major** | Falta de Empty State para usuario con 0 cursos asociados (`subjects.length === 0`). | **ACCEPT** | **Deficiencia de UX onboarding.** Debe incorporarse en `ux/EXPERIENCE.md` para evitar excepciones de JavaScript al desreferenciar un array de asignaturas vacío. |
| **EDGE-UX-02** | **Critical** | Omisión del banner y estado de rechazo formal de escalación temporal para Sofia. | **ACCEPT** | **Bloqueante de interacción.** El ciclo de vida de un ticket de escalación debe contemplar ambos desenlaces (aprobado y denegado). Se incorporará el Banner `E-04` con justificación obligatoria. |
| **EDGE-UX-03** | **Major** | Pérdida de filtros y estado en auditoría forense masiva ante expiración de token de sesión. | **ACCEPT** | **Fricción forense inaceptable.** Se debe incorporar en `ux/EXPERIENCE.md` el modal de re-autenticación *in-situ* que evite redirecciones destructivas. |
| **EDGE-UX-04** | **Minor** | Desalineación de contexto al ingresar mediante enlaces profundos (*Deep-Links*). | **ACCEPT** | **Higiene de navegación.** Se debe forzar que el router de la aplicación sincronice el encabezado `X-Academic-Subject-Context` con el parámetro de ruta `/subjects/{id}`. |
| **EDGE-UX-05** | **Minor** | Desbordamiento de celda de tabla por ARNs largos en resoluciones de 1024px. | **ACCEPT** | **Regla de estilo CSS.** Se añade la clase `.cell-arn-truncate` con tooltip flotante en `ux/DESIGN.md`. |

---

## 4. Próximos Pasos Recomendados

1. **Parche Inmediato de Especificaciones:** Aplicar los 5 hallazgos aceptados en [`ux/DESIGN.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/DESIGN.md) y [`ux/EXPERIENCE.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/EXPERIENCE.md).
2. **Actualización de Gobernanza:** Asentar la sesión de revisión en [`ai-log/decision-log.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ai-log/decision-log.md).
3. **Pase a Fase 3:** Una vez triados los hallazgos de UX, convocar a **Winston (`bmad-agent-architect`)** para iniciar el diseño técnico y los invariantes inviolables `AD-n` en `planning/ARCHITECTURE.md`.
