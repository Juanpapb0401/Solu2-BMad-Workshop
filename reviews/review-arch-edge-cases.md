# Edge Case Hunter Review Report: Technical Architecture (`--lens edge-case-hunter`)

**Lente:** `--lens edge-case-hunter` (Pure Path Tracer & Technical Boundary Condition Audit)  
**Documento Auditado:** `planning/ARCHITECTURE.md`  
**Autor de Arquitectura:** Winston (`bmad-agent-architect`)  
**Auditor:** Edge Case Hunter (`bmad-review`)  
**Fecha de Revisión:** 2026-09-24  
**Estado:** COMPLETED  

---

## 1. Resumen Ejecutivo del Rastreo de Rutas Técnicas

La auditoría mediante la lente `edge-case-hunter` ha ejecutado una inspección exhaustiva de los caminos de ejecución, transiciones de estado relacional y condiciones de contorno algorítmicas en la arquitectura del Módulo 1.

A diferencia del análisis adversarial (enfocado en vectores de ataque deliberados), este informe identifica **condiciones de carrera asíncronas, límites de precisión temporal, duplicidades intra-lote y anomalías de estado latentes** que pueden corromper la consistencia del sistema en escenarios no hostiles pero concurrentes:

1. **Condición de Carrera en Solicitudes Simultáneas de Escalación:** Doble clic de Sofia emitiendo dos peticiones en un lapso de $5\text{ ms}$; ambas leen cero tickets pendientes antes de que alguna complete la inserción, evadiendo el chequeo de unicidad a nivel de aplicación.
2. **Ambigüedad de Ordenamiento por Resolución de Segundos en Timestamps de SQLite:** `CURRENT_TIMESTAMP` en SQLite por defecto solo tiene precisión de 1 segundo; bajo 100 req/s, decenas de eventos de auditoría comparten el mismo timestamp exacto, generando no-determinismo al ordenar por fecha.
3. **Desviación de Reloj (*Clock Skew / NTP Rollback*) en la Expiración de Escalación:** Modificaciones del reloj del host pueden extender o recortar artificialmente la ventana de 4 horas si la expiración se calcula únicamente con `now() >= expires_at` sin comprobación monotónica.
4. **Colisión de Duplicados Internos en el Mismo Lote de Nómina:** El CSV contiene al mismo alumno dos veces con roles diferentes; el worker no valida duplicidad dentro del stream antes de delegar a la base de datos.

---

## 2. Catálogo de Rutas no Manejadas y Condiciones de Borde

### 2.1 Fronteras de Concurrencia y Carrera en Base de Datos

#### `ARCH-EDGE-01`: Condición de Carrera en Solicitud Doble de Escalación (*Double-Submit Race*)
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 3 (`escalation_tickets`) y Sección 5 (`AD-05`)
- **Condición de Disparo:** Sofia experimenta latencia de red y presiona el botón "Enviar Solicitud" dos veces en un intervalo de $5\text{ ms}$. Dos peticiones concurrentes ejecutan en paralelo:
  `SELECT COUNT(*) FROM escalation_tickets WHERE requester_id='TA-SOFIA-01' AND status='PENDING_APPROVAL'`
  Ambas consultas retornan `0`. Ambas peticiones ejecutan `INSERT`, creando dos tickets duplicados para el Dr. Marcus Vance.
- **Consecuencia:** Violación de la regla de no-solapamiento y saturación de la bandeja de aprobación.
- **Guardia Propuesta (Índice Parcial Único en DDL):**
  ```sql
  -- Guard en schema: DDL de SQLite / PostgreSQL
  CREATE UNIQUE INDEX idx_single_active_escalation 
  ON escalation_tickets (requester_id, subject_id) 
  WHERE status IN ('PENDING_APPROVAL', 'ACTIVE');
  ```

---

### 2.2 Fronteras de Precisión Temporal y Orden Criptográfico

#### `ARCH-EDGE-02`: Colisión de Timestamps en `audit_ledger` bajo Carga de 100 req/s
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 3 (`audit_ledger`) y Sección 5 (`AD-04`)
- **Condición de Disparo:** Bajo una ráfaga sostenida de 100 req/s, múltiples eventos de auditoría se insertan dentro del mismo segundo exacto. La columna `timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP` en SQLite almacena `YYYY-MM-DD HH:MM:SS` (resolución de 1 segundo).
- **Consecuencia:** Una consulta forense ordenada por `ORDER BY timestamp DESC` retorna eventos en orden indeterminado. La verificación de la cadena hash falla si el script reconstruye el orden basado en `timestamp` en lugar de la clave primaria secuencial `id`.
- **Guardia Propuesta (Timestamp con Microsegundos + Orden Compuesto):**
  ```python
  # Guard en model/schema de evento:
  from datetime import datetime, timezone
  event_timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
  # Y en la consulta SQL:
  # SELECT * FROM audit_ledger ORDER BY id ASC (para verificación de cadena)
  # SELECT * FROM audit_ledger ORDER BY timestamp DESC, id DESC (para visor UI)
  ```

#### `ARCH-EDGE-03`: Desviación de Reloj (*NTP Rollback*) en la Ventana de Expiración
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 2.1 (Componente 1) e Invariante `AD-05`
- **Condición de Disparo:** El demonio de sincronización horaria del sistema operativo (NTP/chrony) ajusta el reloj del sistema hacia atrás en 15 minutos mientras Sofia tiene una escalación activa de 4 horas.
- **Consecuencia:** La condición `now() >= expires_at` se retrasa 15 minutos adicionales, otorgando tiempo de entrenamiento privilegiado superior a las 4 horas autorizadas por el Dr. Marcus Vance.
- **Guardia Propuesta:** Registro dual: persistir `expires_at_utc` en base de datos para auditoría, pero mantener en el broker de tokens en memoria un límite basado en `time.monotonic()` inicializado al momento de la concesión:
  ```python
  # Guard en TokenLifecycleBroker:
  self.monotonic_deadline = time.monotonic() + (duration_hours * 3600)
  ```

---

### 2.3 Fronteras de Ingestión de Datos y Stream Parsing

#### `ARCH-EDGE-04`: Detección de Duplicados Ocultos Intra-Lote en el Mismo Archivo CSV
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 2.1 (Componente 2) y Sección 5 (`AD-02`)
- **Condición de Disparo:** El archivo de 120 alumnos contiene a Mateo Silva dos veces: en la fila 15 con rol `Student` y en la fila 90 con rol `Teaching Assistant`. El validador procesa el stream secuencialmente.
- **Consecuencia:** Si no existe un rastreador en memoria de identificadores ya vistos durante la lectura del CSV, la primera fila se procesa y la segunda dispara una violación de clave única no interceptada a nivel de aplicación, generando una traza de error de base de datos no estructurada en lugar del manifiesto RFC-7807.
- **Guardia Propuesta (Set de Validación en Stream):**
  ```python
  # Guard en EnrollmentIngestionWorker:
  seen_ids = set()
  for row_num, row in enumerate(roster_stream, start=1):
      if row.institutional_id in seen_ids:
          raise BatchIntegrityError(
              row=row_num, 
              code="INTRA_BATCH_DUPLICATE_ID", 
              detail=f"ID {row.institutional_id} appears multiple times in batch."
          )
      seen_ids.add(row.institutional_id)
  ```

#### `ARCH-EDGE-05`: Idempotencia en Notificaciones Repetidas de Baja (*Course Drop*)
- **Ubicación:** `planning/ARCHITECTURE.md` — Sección 2.1 (Componente 3) e Invariante `AD-03`
- **Condición de Disparo:** El webhook del sistema de registro académico reintenta la notificación `POST /enrollments/{id}/drop` debido a un timeout de red previo, enviando el drop de Mateo por segunda vez.
- **Consecuencia:** La base de datos intenta actualizar un registro que ya se encuentra en estado `DROPPED`, emitiendo potencialmente un segundo evento de auditoría redundante o fallando si el endpoint asume estado `ACTIVE`.
- **Guardia Propuesta:** Manejo estrictamente idempotente:
  ```python
  # Guard en drop endpoint:
  if membership.status == "DROPPED":
      return DropResponse(
          status="ALREADY_REVOKED", 
          revoked_at=membership.dropped_at, 
          message="Idempotent drop: membership was already revoked."
      )
  ```

---

## 3. Matriz de Triage para Decisiones Humanas

A continuación se estructura la matriz formal con las recomendaciones técnicas para la toma de decisión del equipo:

| ID | Severidad | Caso de Borde / Condición de Ruta | Veredicto Humano | Justificación Técnica del Veredicto |
| :--- | :--- | :--- | :--- | :--- |
| **ARCH-EDGE-01** | **Critical** | Carrera de concurrencia en solicitud doble de escalación temporal. | **ACCEPT & FIXED** | **Bloqueante de integridad.** Se añade el índice condicional único `idx_single_active_escalation` en SQLite para garantizar exclusión mutua a nivel de motor de almacenamiento. |
| **ARCH-EDGE-02** | **Major** | Colisión de timestamps en `audit_ledger` bajo ráfagas de 100 req/s. | **ACCEPT & FIXED** | **Bloqueante forense.** Se adopta timestamp ISO 8601 con microsegundos y se impone el orden primario por clave secuencial `id` en todas las consultas de verificación de cadena hash. |
| **ARCH-EDGE-03** | **Minor** | Desincronización por retroceso de reloj del sistema (NTP rollback). | **DEFER** | **Post-V1.** En el entorno de contenedor Docker Compose para un nodo universitario, los ajustes NTP severos son atípicos. Se asume reloj sincronizado por el host; el soporte con `time.monotonic()` se difiere para V2. |
| **ARCH-EDGE-04** | **Major** | Duplicidad de IDs intra-lote en el archivo CSV de nómina. | **ACCEPT & FIXED** | **Higiene de ingestión.** Se añade el guard de validación con `seen_ids` en `ingestion_worker.py` para emitir el error estructurado antes de tocar la base de datos. |
| **ARCH-EDGE-05** | **Minor** | Notificaciones duplicadas de webhook de baja académica (*Course Drop*). | **ACCEPT & FIXED** | **Buenas prácticas de integración.** Se formaliza la respuesta idempotente con código `ALREADY_REVOKED` en `routers.enrollments`. |

---

## 4. Conclusión del Revisor de Casos de Borde

- **Veredicto:** **CONCERNS (Requiere Integración de Guardias Técnicas en `planning/ARCHITECTURE.md`)**
- La inclusión del índice parcial de escalación (`ARCH-EDGE-01`), la precisión de microsegundos en auditoría (`ARCH-EDGE-02`), la validación intra-lote en nóminas (`ARCH-EDGE-04`) y la idempotencia de bajas (`ARCH-EDGE-05`) blinda la arquitectura contra cualquier fallo de concurrencia y carrera asíncrona.
