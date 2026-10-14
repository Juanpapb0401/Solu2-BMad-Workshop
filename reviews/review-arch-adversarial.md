# Adversarial Architecture Review Report (`--lens adversarial`)

**Lente:** `--lens adversarial` (Cynical & Defensive Technical Architecture Review)  
**Documento Auditado:** `planning/ARCHITECTURE.md`  
**Autor de Arquitectura:** Winston (`bmad-agent-architect`)  
**Auditor:** Adversarial Technical Reviewer (`bmad-review`)  
**Fecha de Revisión:** 2026-09-24  
**Estado:** COMPLETED  

---

## 1. Resumen Ejecutivo del Análisis Adversario

El documento `planning/ARCHITECTURE.md` establece una base técnica encomiable: la elección de un stack pragmático (*FastAPI + SQLite WAL*), la formalización de 7 invariantes `AD-n` con contratos sin términos elásticos y el modelado explícito de esquemas relacionales.

No obstante, al someter el diseño a una evaluación adversarial cínica orientada a la explotación de fallos de concurrencia, escalación de privilegios y degradación forzada bajo carga, se descubren **cuatro vulnerabilidades de diseño arquitectónico de severidad crítica y mayor**:

1. **Desincronización de Caché en Memoria ante Procesos Multi-Worker (`AD-03`):**  
   Si el contenedor ejecuta FastAPI con múltiples workers (`uvicorn main:app --workers 4`), el conjunto `revoked_credentials_cache` residirá en el espacio de memoria aislado de cada proceso Python. Un webhook de baja procesado por el *Worker A* invalidará su memoria local, pero los *Workers B, C y D* continuarán autorizando solicitudes del estudiante dado de baja durante el resto de la sesión.
2. **Vulnerabilidad de Truncamiento de Cola en el Ledger de Auditoría (`AD-04`):**  
   El encadenamiento hash $H_n = \text{SHA256}(H_{n-1} \parallel \dots)$ previene la alteración o inserción de registros intermedios, pero **es ciego ante el borrado silencioso de los últimos $K$ registros** (*Tail Truncation Attack*). Un operador malicioso que elimine los últimos eventos preservará una cadena matemáticamente válida en los registros restantes sin que el verificador detecte la omisión sin un anclaje externo de longitud o checkpoint firmado.
3. **Contención de Escritura en SQLite bajo Carga de Auditoría (`AD-02` vs `AD-04`):**  
   En SQLite (incluso en modo WAL), existe un único escritor concurrente. Si cada llamada a `/authorize` escribe síncronamente en `audit_ledger` bajo una carga sostenida de $100\text{ req/s}$, una transacción masiva de nómina (`BEGIN IMMEDIATE` de 120 alumnos) bloqueará la base de datos por cientos de milisegundos, provocando errores `sqlite3.OperationalError: database is locked` (`SQLITE_BUSY`) en el motor de autorización en tiempo real.
4. **Escalación de Privilegios por Ingestión de Nóminas (*Role Smuggling* en `AD-02`):**  
   El esquema relacional define `UNIQUE (identity_id, subject_id)`, pero no explicita la cláusula de resolución de conflictos en el `INSERT`. Si el Dr. Marcus Vance importa un CSV donde un estudiante activo es listado maliciosamente como `Instructor-Privileged`, un `ON CONFLICT DO UPDATE` no restringido podría elevar su rol sin pasar por el workflow de escalación temporal.

---

## 2. Hallazgos Clasificados por Severidad

### 2.1 Hallazgos Críticos (Critical)

#### `ARCH-ADV-CRIT-01`: Falla de Invalidación en Memoria por Divergencia de Procesos Uvicorn
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 2.1 (Componente 3) e Invariante `AD-03`
- **Vector de Explotación:** El estándar de despliegue en producción para FastAPI en contenedores multicore utiliza múltiples workers de Uvicorn/Gunicorn. Al recibir el evento `POST /enrollments/{id}/drop`, el worker asignado actualiza SQLite y añade la llave a su `revoked_credentials_cache` (un `set()` en memoria de proceso). Los demás workers no comparten ese espacio de memoria y carecen de un canal de sincronización entre procesos (IPC, SQLite shared cache o polling con version bump).
- **Impacto:** Mateo Silva, tras cancelar formalmente *CS-480*, realiza peticiones concurrentes; el balanceador distribuye las llamadas: las que caen en los workers no sincronizados retornan `ALLOW`, violando el SLA de revocación de 60 segundos y permitiendo el acceso continuado a modelos privados.

#### `ARCH-ADV-CRIT-02`: Vulnerabilidad de Truncamiento de Cola (*Tail Truncation*) en Ledger Inmutable
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 5 (`AD-04`) y Sección 3 (Tabla `audit_ledger`)
- **Vector de Explotación:** Un actor con acceso directo al archivo SQLite ejecuta:
  ```sql
  DELETE FROM audit_ledger WHERE id > (SELECT MAX(id) - 10 FROM audit_ledger);
  ```
  La función de verificación `verify_audit_chain()` itera desde el evento génesis hasta el evento actual. Como cada registro restante apunta correctamente a su predecesor, la verificación matemática retorna `VERIFIED_OK`. No existe un contador atómico de secuencia inmutable, un anclaje externo de cabecera (*Ledger Head Anchor*) ni checkpoints firmados que evidencien la pérdida de los últimos 10 eventos.
- **Impacto:** Un atacante puede acceder a modelos de investigación y luego purgar los registros recientes de auditoría sin activar la alerta `AUDIT_LOG_TAMPERING_DETECTED`.

---

### 2.2 Hallazgos Mayores (Major)

#### `ARCH-ADV-MAJ-01`: Cuello de Botella y Colapso `SQLITE_BUSY` por Escrituras Síncronas en Auditoría
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 1.1 y Sección 2.1 (Componente 4)
- **Vector de Explotación:** El PRD exige $100\text{ req/s}$ sostenidas en `/authorize` (`NFR-PERF-01`). Si cada evaluación requiere un `INSERT` síncrono en `audit_ledger` para encadenar el hash, el motor de SQLite serializará todas las transacciones. Al ejecutarse simultáneamente una importación de nómina de 1,000 registros (`AD-02`), la transacción exclusiva de larga duración ($T \approx 1.5\text{ s}$) provocará que las solicitudes de autorización agoten su tiempo de espera de bloqueo (`busy_timeout`), disparando excepciones HTTP 500/503 masivas.
- **Impacto:** Denegación de servicio interna y degradación del SLA de latencia ($p95 < 20\text{ ms}$).

#### `ARCH-ADV-MAJ-02`: Escalación Horizontal Silenciosa vía Sobrescritura de Rol en Roster (*Role Smuggling*)
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 3 (`subject_memberships`) e Invariante `AD-02`
- **Vector de Explotación:** La tabla `subject_memberships` restringe duplicados con `UNIQUE (identity_id, subject_id)`. Sin embargo, el DDL y el worker no especifican la cláusula de inserción. Si la implementación usa `INSERT OR REPLACE` o `ON CONFLICT (identity_id, subject_id) DO UPDATE SET role_id = EXCLUDED.role_id`, un atacante que logre insertar una fila en el CSV de nómina semestral para un usuario existente puede cambiar su rol de `Student` a `Instructor-Privileged` o `Admin` sin pasar por la validación de jefatura del Dr. Marcus Vance.
- **Impacto:** Escalación ilegítima de privilegios permanentes dentro de la asignatura.

---

### 2.3 Hallazgos Menores (Minor)

#### `ARCH-ADV-MIN-01`: Normalización Ausente de ARNs y Bypass por Path Traversal Sintáctico
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 5 (`AD-01`)
- **Vector de Explotación:** `AD-01` valida que el `resource_arn` inicie con `urn:uai:subject:<subject_id>:`. Si el motor realiza una simple comparación de subcadenas o split de string sin canonicalización, un atacante podría enviar:
  `urn:uai:subject:CS101:model:../../CS-480/private-model`
  burlando la comprobación de prefijo si el consumidor downstream (Gateway o vLLM) normaliza la ruta posteriormente.
- **Impacto:** Fuga potencial de recursos protegidos por ambigüedad en el parser de ARNs.

---

## 3. Matriz de Triage y Veredicto Técnico Humano

A continuación se detalla la matriz de triaje con las decisiones técnicas de ingeniería para sanear la arquitectura:

| ID | Severidad | Hallazgo Crítico | Veredicto Humano | Justificación Técnica del Veredicto |
| :--- | :--- | :--- | :--- | :--- |
| **ARCH-ADV-CRIT-01** | **Critical** | Desincronización de `revoked_credentials_cache` entre workers Uvicorn. | **ACCEPT & FIXED** | **Bloqueante de seguridad.** Para la arquitectura standalone, se adopta: (a) Despliegue con proceso único asyncio (`workers: 1` con concurrency interna basada en libuv) O (b) Tabla relacional de revocación en SQLite consultada con B-Tree indexado en memoria compartida (WAL mode) que garantiza que todos los workers lean la misma versión transaccional en $< 5\text{ ms}$. |
| **ARCH-ADV-CRIT-02** | **Critical** | Vulnerabilidad de Tail Truncation en `audit_ledger`. | **ACCEPT & FIXED** | **Falla de integridad forense.** Se actualiza `AD-04` incorporando una tabla singleton `audit_ledger_metadata` que mantiene de forma atómica: `total_events_count` y `last_event_hash`, impidiendo borrados de cola sin disparar inconsistencia matemática. |
| **ARCH-ADV-MAJ-01** | **Major** | Bloqueo `SQLITE_BUSY` por escrituras síncronas de auditoría bajo $100\text{ req/s}$. | **ACCEPT & FIXED** | **Riesgo de disponibilidad.** Se desacopla la escritura de auditoría en `/authorize` mediante una cola interna asíncrona (`asyncio.Queue`) con worker de volcado en batch (micro-batching cada 50ms o 50 eventos) y configuración de `PRAGMA busy_timeout = 5000` en SQLite WAL. |
| **ARCH-ADV-MAJ-02** | **Major** | Escalación de privilegios en importación de nómina (*Role Smuggling*). | **ACCEPT & FIXED** | **Falla de control RBAC.** Se actualiza `AD-02`: la ingestión masiva tiene terminantemente prohibido alterar el rol de membresías preexistentes. Si una identidad ya está en la materia, el rol entrante se ignora o se rechaza si difiere del rol activo. |
| **ARCH-ADV-MIN-01** | **Minor** | Vulnerabilidad de path traversal en el parseo de ARNs. | **ACCEPT & FIXED** | **Higiene sintáctica.** Se establece en `AD-01` una expresión regular estricta de validación que prohíbe caracteres `.` y `/` en los segmentos de identificadores: `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$`. |

---

## 4. Conclusión del Revisor Adversario

- **Veredicto:** **CONCERNS (Requiere Actualización Inmediata de Invariantes AD-n en `planning/ARCHITECTURE.md`)**
- Las cuatro vulnerabilidades encontradas se resuelven robusteciendo los invariantes `AD-01`, `AD-02`, `AD-03` y `AD-04`, garantizando que la implementación en código sea impermeable a colapsos de concurrencia y manipulaciones forenses.
