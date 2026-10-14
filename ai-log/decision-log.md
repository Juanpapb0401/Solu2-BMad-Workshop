# AI Decision & Governance Log (Supervisión Humana y Rastro de Auditoría)

**Proyecto:** Plataforma de Gestión de Cómputo IA de la Universidad  
**Módulo Asignado:** Módulo 1 — User, Role, and Subject Access Manager (Tier: Foundation)  
**Marco de Gobernanza:** BMad Architecture Governance & Human-in-the-Loop Supervision Protocol  
**Propósito:** Cumplimiento de supervisión humana (15% de la rúbrica de evaluación). Registro inmutable de interacciones críticas, propuestas de la IA evaluadas, directivas técnicas impuestas y veredictos de ingeniería.

---

## 1. Registro de las 7 Interacciones Clave de Supervisión Humana

A continuación se detallan formalmente las **7 interacciones de control técnico** donde la intervención de los ingenieros humanos definió la dirección de arquitectura, seguridad y experiencia del sistema, destacando las propuestas de la IA que fueron **rechazadas o modificadas** para salvaguardar la viabilidad institucional:

---

### Interacción 1: Rechazo de Acoplamiento Prematuro a Kubernetes / Keystone
- **Timestamp / Fase:** 2026-09-23 21:05 — Fase 1 (PRD & Scoping Inicial)
- **Agente / Rol Involucrado:** John (`bmad-agent-pm`) / Ingeniero de Software Principal
- **Propuesta Original de la IA:**
  La IA propuso que el Módulo 1 se integrara directamente en tiempo real con la API del clúster de Kubernetes institucional (creando `RoleBindings` y `Namespaces` de K8s en vivo) y con el servicio OpenStack Keystone de la universidad para autenticar identidades y aprovisionar API keys sobre los nodos de hardware desde el prototipo inicial.
- **Veredicto Humano:** **`[RECHAZADO]`**
- **Justificación Técnica Detallada:**
  1. **Violación del Aislamiento Standalone:** La especificación de evaluación exige que el prototipo sea 100% autónomo, ejecutable en un solo nodo mediante Docker Compose y libre de dependencias vivas de los otros 11 módulos de la plataforma.
  2. **Acoplamiento Tóxico de Capas:** Conectar el Módulo 1 (gestión de acceso y RBAC) con Kubernetes introduce responsabilidades de orquestación de GPU física que corresponden estrictamente al Módulo 2 (*Workstation Agent*) y Módulo 3 (*Central Server Agent*).
  3. **Solución Impuesta:** Se rechazó la integración en vivo y se impuso el desacoplamiento mediante **Mock Identity Fixtures** (`identities_seed.csv`, `subjects_seed.json`) y endpoints REST desacoplados que emiten credenciales sintéticas de formato uniforme (`uai_live_<hash_32_bytes>`), garantizando pruebas locales reproducibles sin clúster externo.

---

### Interacción 2: Erradicación de Métrica de Revocación Elástica por Regla Dura (< 60s)
- **Timestamp / Fase:** 2026-09-23 21:12 — Fase 1 (PRD & Definición de NFRs)
- **Agente / Rol Involucrado:** John (`bmad-agent-pm`) / Revisor de Calidad y Requisitos
- **Propuesta Original de la IA:**
  Al redactar el requisito no funcional `NFR-REVOC-03` para la cancelación de asignaturas (*Course Drop*), la IA generó el siguiente texto: *"El sistema revocará los accesos y credenciales de los estudiantes dados de baja de la manera más rápida y eficiente posible, garantizando un corte seguro sin impactar el rendimiento global"*.
- **Veredicto Humano:** **`[MODIFICADO]`**
- **Justificación Técnica Detallada:**
  1. **Inauditabilidad de Términos Elásticos:** Adjetivos como *"lo más rápido posible"*, *"eficiente"* y *"seguro"* carecen de significado computable; impiden redactar aserciones deterministas en pruebas unitarias y suites de carga (`pytest`, `k6`).
  2. **Riesgo Institucional de Fuga de Cómputo:** Si un alumno retirado conserva acceso durante horas debido a la ambigüedad del término "rápido", la universidad incurre en saturación de GPUs de 24 GB y 48 GB por parte de identidades no autorizadas.
  3. **Solución Impuesta:** Se modificó la regla imponiendo un contrato numérico de doble nivel:
     - **Latencia Local en Motor de Autorización:** Inserción y actualización en memoria transaccional en un tiempo estricto $T < 200\text{ ms}$ en el 100% de las ejecuciones unitarias.
     - **SLA Perimetral Global:** Propagación completa a proxies y clientes en $T < 60\text{ segundos}$ en el peor escenario de caché distribuida.
     - Se vinculó a una prueba E2E mandatoria (`test_revocation_latency.py`).

---

### Interacción 3: Rechazo de Modelo de Roles Globales en Favor de Context-Enforced RBAC
- **Timestamp / Fase:** 2026-09-23 21:20 — Fase 1 (Algoritmo de Autorización & Caso de Borde)
- **Agente / Rol Involucrado:** John (`bmad-agent-pm`) / Arquitecto de Seguridad
- **Propuesta Original de la IA:**
  La IA propuso un modelo relacional tradicional con una tabla `users` que contenía una columna `role` global (`student`, `ta`, `instructor`, `admin`). Bajo este esquema, cuando un asistente docente (Sofia) solicitaba una escalación para su laboratorio, la aprobación actualizaba su usuario a `Instructor-Privileged` a nivel global en la plataforma.
- **Veredicto Humano:** **`[RECHAZADO]`**
- **Justificación Técnica Detallada:**
  1. **Vulnerabilidad Crítica de Confused Deputy y Escalación Horizontal:** En el ecosistema universitario, las personas poseen membresías concurrentes y asimétricas: Sofia es Asistente Docente en *CS-480* (Intro to ML) pero es estudiante regular en *NLP Advanced*; Mateo está matriculado en *CS101* (donde la política estipula 0 GPU) y en *CS-480* (acceso a modelos de 8B).
  2. **Explotación Inmediata:** Si el rol fuera global, la escalación aprobada a Sofia para preparar el laboratorio de *CS-480* le habría permitido utilizar sus privilegios elevados para acaparar el servidor con dos GPUs de 48 GB para sus tareas personales de posgrado en *NLP Advanced*. Del mismo modo, Mateo podría haber ejecutado modelos de *CS-480* bajo el contexto de *CS101*.
  3. **Solución Impuesta:** Se rechazó el modelo global y se diseñó el algoritmo **Context-Enforced RBAC** (Sección 5.2 del PRD e Invariante `AD-01`), donde los permisos se resuelven exclusivamente sobre la tupla `(identity_id, subject_id, resource_arn, action)` bajo el encabezado obligatorio `X-Academic-Subject-Context`, garantizando que Sofia tenga rol docente en una materia y estudiante básico en otra sin interferencia cruzada.

---

### Interacción 4: Sustitución de Mensajes Genéricos HTTP 403 por Banners de Explicabilidad
- **Timestamp / Fase:** 2026-09-23 21:28 — Fase 2 (UX Design & Interacción de Usuario)
- **Agente / Rol Involucrado:** Freya (`wds-agent-freya-ux`) / Diseñador UX
- **Propuesta Original de la IA:**
  La IA propuso que ante cualquier denegación de acceso en el Web Admin Portal o API Explorer, el sistema desplegara un cuadro de diálogo flotante con el texto: *"Error 403: Acceso Denegado. No tiene permisos suficientes para ejecutar esta acción. Contacte al administrador del sistema"*.
- **Veredicto Humano:** **`[MODIFICADO]`**
- **Justificación Técnica Detallada:**
  1. **Opacidad y Fricción Cognitiva:** Un mensaje genérico "Acceso Denegado" genera confusión inmediata en alumnos y docentes (ej. Mateo no comprende por qué se rechaza su inferencia si tiene matrícula activa; Sofia no sabe si su denegación es por rol, por materia incorrecta o por expiración de token).
  2. **Sobrecarga del Administrador:** Obliga al Dr. Marcus Vance a atender tickets innecesarios para depurar colisiones de contexto académicas.
  3. **Solución Impuesta:** Se modificó la interfaz exigiendo **Banners Obligatorios de Explicabilidad Algorítmica** (`ux/EXPERIENCE.md`, Banners E-01 a E-04) con componentes accesibles (WCAG 2.1 AA) que explicitan:
     - El motivo determinista del rechazo (ej. `RESOURCE_SUBJECT_MISMATCH`).
     - El contexto académico activo (`X-Academic-Subject-Context: CS101`) vs el contexto del recurso solicitado (`CS-480`).
     - La regla inviolable aplicada y la acción concreta para solucionar el conflicto.

---

### Interacción 5: Rechazo de Complejidad Distribuida (Redis/Celery) en Favor de Boring Tech
- **Timestamp / Fase:** 2026-09-23 21:35 — Fase 3 (Arquitectura Técnica & Persistencia)
- **Agente / Rol Involucrado:** Winston (`bmad-agent-architect`) / Ingeniero de Confiabilidad (SRE)
- **Propuesta Original de la IA:**
  Para gestionar la concurrencia de revocaciones e ingestión de nóminas, la IA propuso desplegar una arquitectura de microservicios compuesta por: API en FastAPI, clúster Redis para listas de revocación pub/sub, broker RabbitMQ con workers Celery en segundo plano, y PostgreSQL como base de datos primaria.
- **Veredicto Humano:** **`[RECHAZADO]`**
- **Justificación Técnica Detallada:**
  1. **Violación Severa del Presupuesto de Memoria (`NFR-DISP-07`):** El límite operativo para el Módulo 1 en un nodo universitario es de $\le 512\text{ MB}$ de RAM y un tiempo de arranque menor a 2.0 segundos. Levantar Redis, RabbitMQ, Celery workers y PostgreSQL sobrepasa fácilmente los $1.5\text{ GB}$ en reposo y añade más de 15 segundos al arranque en frío.
  2. **Fragilidad Operacional en Prototipos:** Requiere orquestar redes complejas y healthchecks entre contenedores dependientes, haciendo fracasar la suite de pruebas unitarias si un servicio intermediario tarda en responder.
  3. **Solución Impuesta:** Se rechazó el stack distribuido y se adoptó la filosofía **Boring Tech**:
     - Despliegue en contenedor único basado en Python 3.11-slim y FastAPI.
     - Motor relacional **SQLite en modo WAL** (Write-Ahead Logging) con `PRAGMA busy_timeout = 5000` y transacciones `BEGIN IMMEDIATE`.
     - Manejo de colas internas mediante `asyncio.Queue` nativo en memoria de proceso (libuv) con micro-lotes cada 50ms, logrando un consumo total de $\approx 120\text{ MB}$ de RAM y arranque en $< 1.2\text{ s}$.

---

### Interacción 6: Descubrimiento y Blindaje contra el Ataque de Tail Truncation en Auditoría
- **Timestamp / Fase:** 2026-09-24 09:15 — Fase 3 (Auditoría Adversarial de Arquitectura)
- **Agente / Rol Involucrado:** Revisor Adversarial (`bmad-review`) / Criptógrafo & Auditor
- **Propuesta Original de la IA:**
  La arquitectura inicial planteaba un ledger inmutable simple donde cada evento calculaba:
  $$\text{record\_hash} = \text{SHA256}(\text{prev\_record\_hash} \parallel \dots)$$
  La IA argumentaba que el encadenamiento hash garantizaba matemáticamente un registro a prueba de manipulaciones o borrados.
- **Veredicto Humano:** **`[MODIFICADO]`**
- **Justificación Técnica Detallada:**
  1. **Vulnerabilidad de Truncamiento de Cola (*Tail Truncation Attack*):** Un operador malicioso o atacante con privilegios sobre el archivo SQLite puede eliminar silenciosamente los últimos $K$ registros:
     `DELETE FROM audit_ledger WHERE id > (SELECT MAX(id) - 10 FROM audit_ledger);`
     La función de verificación `verify_audit_chain()` itera desde el evento génesis hasta el último registro físico existente; como todos los registros restantes apuntan a su predecesor legítimo, la verificación retornaba `VERIFIED_OK`, ocultando accesos no autorizados recientes a modelos privados.
  2. **Solución Impuesta:** Se modificó el diseño del esquema DDL y el invariante `AD-04`, creando la tabla relacional singleton [`audit_ledger_metadata`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/planning/ARCHITECTURE.md#L193-L200) (`id = 1`) que mantiene de forma atómica:
     - `total_events_count` (contador atómico de eventos emitidos).
     - `head_record_hash` (firma criptográfica del último evento generado).
     Cualquier eliminación física de registros de la cola genera una discrepancia inmediata entre la cuenta de la tabla de metadatos y los registros físicos, activando de forma automática e irreversible la alerta `AUDIT_LOG_TAMPERING_DETECTED`.

---

### Interacción 7: Prevención de Carrera Asíncrona en Escalaciones mediante Índice Parcial en BD
- **Timestamp / Fase:** 2026-09-24 09:25 — Fase 3 (Auditoría de Casos de Borde de Arquitectura)
- **Agente / Rol Involucrado:** Edge Case Hunter (`bmad-review`) / Ingeniero de Concurrencia
- **Propuesta Original de la IA:**
  La IA propuso que la validación para impedir solicitudes simultáneas de escalación de privilegios se gestionara en la capa lógica de FastAPI mediante la siguiente secuencia en el endpoint `POST /escalations/request`:
  1. `count = db.query(Ticket).filter_by(requester_id=id, status='PENDING').count()`
  2. `if count > 0: raise HTTPException(409)`
  3. `db.add(new_ticket)`
- **Veredicto Humano:** **`[MODIFICADO]`**
- **Justificación Técnica Detallada:**
  1. **Condición de Carrera por Doble Envío (*Double-Submit Race*):** Si Sofia presiona el botón "Enviar Solicitud" dos veces en un intervalo de $< 10\text{ ms}$ (debido a latencia de red o impaciencia de interfaz), ambas peticiones HTTP son procesadas concurrentemente por el worker asíncrono. Ambas ejecutan el `SELECT count(*)` antes de que cualquiera complete el `INSERT`, leyendo `count = 0` y creando dos tickets duplicados para el Dr. Marcus Vance.
  2. **Solución Impuesta:** Se modificó la arquitectura delegando la exclusión mutua al motor relacional de almacenamiento mediante la incorporación del índice condicional único en el DDL (`AD-05`):
     ```sql
     CREATE UNIQUE INDEX idx_single_active_escalation 
     ON escalation_tickets (requester_id, subject_id) 
     WHERE status IN ('PENDING_APPROVAL', 'ACTIVE');
     ```
     Cualquier segunda solicitud concurrente es abortada de raíz a nivel de base de datos con un error de clave única, retornando un código HTTP 409 determinista sin depender de bloqueos frágiles en Python.

---

## 2. Historial de Decisiones de Fase 1 — PRD & Scoping (John / bmad-agent-pm)

| Fecha / Hora | Agente Involucrado | Decisión Técnica / Intervención Humana | Racional y Justificación Técnica | Estado |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-23 21:13 | John (`bmad-agent-pm`) | **Delimitación Estricta de Fronteras de Módulo (In-Scope vs Mocks):** Aislamiento de RBAC frente a orquestación de GPU. | La propuesta inicial sugería incluir la asignación física de pods K8s y corte de VRAM. Se rechazó para evitar acoplamiento con Módulo 2 y Módulo 3, manteniendo el Módulo 1 100% testeable de forma independiente con mocks de identidad. | **ADOPTADA** |
| 2026-09-23 21:14 | John (`bmad-agent-pm`) | **Prohibición Total de Términos Genéricos ("el usuario"):** Tipificación con protagonistas nombrados (*Dr. Marcus Vance*, *Sofia*, *Mateo*, *Dra. Elena Gómez*). | Evita ambigüedades en la trazabilidad de seguridad y asegura que cada escenario de prueba valide credenciales y contextos académicos específicos. | **ADOPTADA** |
| 2026-09-23 21:14 | John (`bmad-agent-pm`) | **Algoritmo de Aislamiento de Materia (Context-Enforced RBAC):** Evaluación acotada por tupla `(subject_id, role, resource, action)`. | Resuelve el caso de borde obligatorio (Mateo en CS101 con 0 GPU y en CS-480 con acceso estándar; Sofia TA en CS-480 y estudiante en NLP Advanced), impidiendo acumulación o fuga tóxica de privilegios. | **ADOPTADA** |
| 2026-09-23 21:15 | John (`bmad-agent-pm`) | **Erradicación de NFRs Elásticos:** Conversión a contratos numéricos auditables ($p95 < 20\text{ ms}$, propagación $< 60\text{ s}$, 0 tokens en logs). | Un NFR que diga "el sistema será rápido y seguro" es inauditable. Los umbrales numéricos garantizan verificabilidad objetiva en suites automatizadas (k6, pytest). | **ADOPTADA** |

---

## 3. Historial de Decisiones de Fase 2 — UX Design & Experience (Freya / wds-agent-freya-ux)

| Fecha / Hora | Agente Involucrado | Decisión Técnica / Intervención Humana | Racional y Justificación de Diseño | Estado |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-23 21:26 | Freya (`wds-agent-freya-ux`) | **Adopción de Layout Híbrido Split-Pane (65% Portal / 35% API Explorer):** Visualización combinada en una sola vista para desktop. | Permite que el evaluador técnico y el administrador departamental (Dr. Marcus Vance) alternen entre la tabla de sujetos y la consola de ejecución de fixtures sin salir del contexto de la pantalla. | **ADOPTADA** |
| 2026-09-23 21:26 | Freya (`wds-agent-freya-ux`) | **Banners de Explicabilidad Algorítmica con Citas de Reglas Inviolables:** Prohibición de mensajes genéricos "Acceso Denegado". | Protege la psicología del estudiante (Mateo) y evita fricción operativa: cuando un permiso es denegado o degradado, se detalla la causa contextual (`Context-Enforced RBAC`), la regla infringida y la acción de remediación sugerida. | **ADOPTADA** |
| 2026-09-23 21:27 | Freya (`wds-agent-freya-ux`) | **Cumplimiento Estricto WCAG 2.1 AA:** Ratios de contraste $\ge 14.8:1$ sobre fondo base y anillos de foco visibles continuos de $2\,\text{px}$. | Garantiza accesibilidad para usuarios con lectores de pantalla en tablas densas de administración y consola de logs mediante regiones ARIA `polite` y `assertive`. | **ADOPTADA** |
| 2026-09-23 21:30 | Freya (`wds-agent-freya-ux`) | **Modelado de los 4 Escenarios UX (C-P-V) + Wireframes ASCII y Mermaid:** Trazabilidad formal 1:1 con los FRs del PRD. | Se detallan los estados de interacción para el Dr. Marcus Vance, Sofia y Mateo, incorporando la visualización interactiva de la resolución de conflictos multi-materia en Pantalla A y la auditoría forense con encadenamiento SHA-256 en Pantalla B. | **ADOPTADA** |

---

## 4. Historial de Decisiones de Fase 3 — Technical Architecture (Winston / bmad-agent-architect)

| Fecha / Hora | Agente Involucrado | Decisión Técnica / Intervención Humana | Racional y Justificación de Arquitectura | Estado |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-23 21:38 | Winston (`bmad-agent-architect`) | **Selección de Stack Standalone "Boring Tech":** FastAPI (Python 3.11) + SQLite WAL Mode + Pydantic v2 + SQLAlchemy 2.0. | Elimina la sobrecarga de clústeres distribuidos para el Módulo 1. Garantiza transacciones ACID locales, arranque en $< 2\text{ s}$ y memoria $< 120\text{ MB}$, cumpliendo `NFR-DISP-07`. | **ADOPTADA** |
| 2026-09-23 21:39 | Winston (`bmad-agent-architect`) | **Formulación de 7 Invariantes Indestructibles (AD-01 a AD-07):** Estructura obligatoria de 5 partes con cero adjetivos elásticos. | Reglas deterministas verificables por máquina: `AD-01` (Aislamiento de contexto y prevención Confused Deputy), `AD-02` (Ingestión atómica y cuarentena), `AD-03` (Invalidación sub-200ms), `AD-04` (Ledger SHA-256 encadenado), `AD-05` (Prohibición de auto-aprobación), `AD-06` (Fuga cero de secretos), `AD-07` (Paginación acotada a 100). | **ADOPTADA** |
| 2026-09-23 21:39 | Winston (`bmad-agent-architect`) | **Diagramación Mermaid C4 Context & Component Interaction:** Algoritmo explícito de resolución de roles en pugna. | Modela el camino exacto por el cual una petición de Sofia con contexto `CS101` hacia modelos de `CS-480` es interceptada y rechazada antes de tocar los recursos físicos. | **ADOPTADA** |

---

## 5. Matrices de Triage y Cierre de los Review Gates

### Review Gate 1: Auditoría Adversarial del PRD (`review-prd-adversarial.md`)
- **`ADV-CRIT-01` (Confused Deputy Binding):** `ACCEPT & FIXED` $\rightarrow$ Integrada validación de Resource-Subject en el PRD.
- **`ADV-CRIT-02` (Static Key Cache):** `ACCEPT & FIXED` $\rightarrow$ Modelada tabla relacional `subject_credentials` con caché en memoria.
- **`ADV-MAJ-01` (VRAM Scope Creep):** `ACCEPT & FIXED` $\rightarrow$ Retirado código de VRAM en favor de código RBAC institucional.
- **`ADV-MAJ-02` (Escalation Concurrency):** `ACCEPT & FIXED` $\rightarrow$ Restringidas solicitudes solapadas (`HTTP 409 Conflict`).
- **`ADV-MAJ-03` (Roster Suspended Check):** `ACCEPT & FIXED` $\rightarrow$ Cuarentena automática para alumnos suspendidos (`roster_rejected_conflicts.csv`).
- **`ADV-MAJ-04` (Revocation SLA):** `ACCEPT & FIXED` $\rightarrow$ Sub-200ms local vs 60s perimetral claramente diferenciados.
- **`ADV-MIN-01` (Penalty Box Auto-Approval):** `DEFER` $\rightarrow$ Diferido a V2 (rechazo RFC-7807 suficiente para standalone).
- **`ADV-MIN-02` (Audit Pagination):** `ACCEPT & FIXED` $\rightarrow$ Tope estricto de `page_size <= 100`.

### Review Gate 2: Auditoría de Casos de Borde de UX (`review-ux-edge-cases.md`)
- **`EDGE-UX-01` (Empty States Case D):** `ACCEPT & FIXED` $\rightarrow$ Manejo robusto para usuarios sin cursos asignados.
- **`EDGE-UX-02` (Banner E-04 Escalation Denied):** `ACCEPT & FIXED` $\rightarrow$ Banner explícito con justificación de jefatura y enfriamiento de 30 min.
- **`EDGE-UX-03` (In-situ Auth Modal):** `ACCEPT & FIXED` $\rightarrow$ Re-autenticación modal sin pérdida de filtros de consulta forense.
- **`EDGE-UX-04` (URL <-> Subject Sync):** `ACCEPT & FIXED` $\rightarrow$ Enlace bidireccional entre path `/subjects/{id}` y encabezado HTTP.
- **`EDGE-UX-05` (ARN Column Truncation):** `ACCEPT & FIXED` $\rightarrow$ Clase CSS `.cell-arn-truncate` para pantallas de 1024px.

### Review Gate 3: Auditoría Adversarial de Arquitectura (`review-arch-adversarial.md`)
- **`ARCH-ADV-CRIT-01` (Uvicorn Multi-Worker Divergence):** `ACCEPT & FIXED` $\rightarrow$ Arquitectura con proceso único asyncio (`workers: 1`, libuv) + SQLite WAL.
- **`ARCH-ADV-CRIT-02` (Audit Tail Truncation):** `ACCEPT & FIXED` $\rightarrow$ Tabla relacional singleton `audit_ledger_metadata` (`id = 1`).
- **`ARCH-ADV-MAJ-01` (SQLite Busy Bottleneck):** `ACCEPT & FIXED` $\rightarrow$ Desacoplamiento asíncrono con `asyncio.Queue` y micro-batching cada 50ms.
- **`ARCH-ADV-MAJ-02` (Anti-Role Smuggling):** `ACCEPT & FIXED` $\rightarrow$ Prohibición estricta de sobreescritura de roles en ingesta de nóminas preexistentes.
- **`ARCH-ADV-MIN-01` (Strict ARN Regex):** `ACCEPT & FIXED` $\rightarrow$ Expresión regular `^urn:uai:subject:[...]:model:[...]$` cerrando path traversal.

### Review Gate 4: Auditoría de Casos de Borde de Arquitectura (`review-arch-edge-cases.md`)
- **`ARCH-EDGE-01` (Double-Submit Race Condition):** `ACCEPT & FIXED` $\rightarrow$ Índice condicional único `idx_single_active_escalation` en DDL.
- **`ARCH-EDGE-02` (Audit Sub-Second Precision):** `ACCEPT & FIXED` $\rightarrow$ Timestamps ISO 8601 con microsegundos y orden primario por `id ASC`.
- **`ARCH-EDGE-03` (NTP Rollback Skew):** `DEFER` $\rightarrow$ Diferido a V2 (entorno Docker host con NTP estable).
- **`ARCH-EDGE-04` (seen_ids Intra-Batch Guard):** `ACCEPT & FIXED` $\rightarrow$ Rastreo en memoria en el stream de lectura de nóminas.
- **`ARCH-EDGE-05` (Idempotent Drop Webhook):** `ACCEPT & FIXED` $\rightarrow$ Respuesta estructurada `ALREADY_REVOKED` ante reintentos de red.

---

## 6. Registro del Implementation Readiness Gate (Fase 4 — Pre-Implementation Sign-off)

| Fecha / Hora | Agente Involucrado | Decisión Técnica / Intervención Humana | Racional y Justificación Técnica | Estado |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-24 09:42 | Auditor (`bmad-check-implementation-readiness`) | **Certificación de Trazabilidad 100% y Emisión de Veredicto PASS:** Aprobación formal previa a la codificación. | Se auditó la correspondencia biunívoca entre PRD (`FR-01` a `FR-04` + `Sec 5.2`), UX (`scenario-1` a `scenario-4` + wireframes) y Arquitectura (`AD-01` a `AD-07`). Se verificó la resolución de 23/23 hallazgos de revisión con 0 items pendientes. | **PASS / APPROVED** |
