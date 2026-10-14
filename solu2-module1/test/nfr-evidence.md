# Plan de evidencia NFR — Módulo 1 (plan, no auditoría)

- **Workflow:** `bmad-testarch-nfr` — modo **Create**, **Fast path** (corrida no interactiva con `opencode run`; sin menús).
- **Fecha:** 2026-10-14. **Idioma:** español (IDs, endpoints, enums, campos y umbrales literales de Plan-2).
- **Alcance:** plan de evidencia para los 7 NFR de `planning/prd.md` §6. No hay implementación; no se ejecuta `bmad-build`/`bmad-build-auto`. **Ningún NFR queda `EVIDENCED`.**
- **Fuentes:** `planning/prd.md`, `planning/ARCHITECTURE.md`, `ux/C-UX-Scenarios/scenario-4.md`, `solu2-module1/test/conftest.py`, decisiones adoptadas 2026-10-13 (G6-02, G7-02, R3-06, H-22, F-01/F-04).
- **Stack heredado (confirmado 2026-10-12):** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite WAL con writer único. Reloj inyectado (`fake_clock`); sin hardware ni servicios vivos.

## Tabla principal (una fila por NFR formal; todo `PLANNED`)

| NFR | Métrica y umbral exacto del PRD | Cómo se mide (herramienta, fixture de `solu2-module1/test/conftest.py`, N, concurrencia) | Artefacto de evidencia esperado (ruta) | Estado |
|---|---|---|---|---|
| NFR-PERF-01 | Latencia de decisión RBAC: `p95 < 20 ms`; `p99 < 50 ms` bajo carga sostenida de `100 req/s` (PRD §6). | k6/Locust 5 min contra `POST /api/v1/authorize`; carga sostenida `100 req/s`; fixtures `db` (SQLite WAL, `busy_timeout=5000`), `fake_clock`, `edge_case_seeds` (EDGE-01: Student CS101 / TA CS-480), `explain_assert` (AD-11). Concurrencia numérica explícita: 100 req/s. Escritura de auditoría desacoplada por `asyncio.Queue` + micro-batching 50 ms/50 ev (AD-04). | `solu2-module1/test/evidence/nfr-perf-01-k6-summary.json` + `solu2-module1/test/evidence/nfr-perf-01-latency-hist.csv` | PLANNED |
| NFR-PERF-02 | Ingestión roster: lote de `1,000 registros` en `T < 3.0 s` (PRD §6). | Benchmark con payload sintético de nómina (`POST /api/v1/subjects/{subject_id}/roster`); N=1,000; transacción `BEGIN IMMEDIATE`, rollback total ante 1 fila inválida; fixtures `db`, `fake_clock`, `fake_id_generator`. Caso de fallo asociado: fila 85 con `@gmail.com` → `422` + 0 escrituras (FR-INGEST-01). | `solu2-module1/test/evidence/nfr-perf-02-ingest-1000.json` | PLANNED |
| NFR-REVOC-03 | Revocación: invalidación local en memoria `T_local < 200 ms`; corte en proxies perimetrales `T_revoc < 60 s` (TTL máx. caché clientes = 60 s) (PRD §6). | Test E2E de revocación (`POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop` → `POST /api/v1/authorize` a `model:llama-3-vision-private:cs-480`): peticiones a segundos 1, 5 y 30 post-drop; se espera `DENY` + `SUBJECT_ENROLLMENT_DROPPED`; propagación registrada `< 500 ms` en ventana de prueba de 5 s (prueba E2E de PRD §4.3 = objetivo funcional laxo; el gate es `T_local < 200 ms`, ver «Umbrales triageados» de epics.md) [ACTUALIZADO 2026-10-14, K-22]; fixtures `db`, `fake_clock`, `edge_case_seeds` (preservación de CS101). Ver §Reliability. | `solu2-module1/test/evidence/nfr-revoc-03-drop-latency.json` | PLANNED |
| NFR-SEC-04 | Fuga de secretos en trazas: **exactamente 0** API keys/tokens completos en `stdout`, `stderr`, errores o auditoría (PRD §6). | Escaneo regex `uai_live_[a-zA-Z0-9]{32}` sobre 10,000 líneas de log generadas en test; enmascaramiento `uai_live_<4>••••<4>` fuera de la emisión inicial (AD-06). Ver §Security. | `solu2-module1/test/evidence/nfr-sec-04-secret-scan.log` + `solu2-module1/test/evidence/nfr-sec-04-scan-report.json` (0 matches) | PLANNED |
| NFR-SEC-05 | Almacenamiento criptográfico: SHA-256 + salt 16 bytes; crudo visible **una sola vez** en emisión (PRD §6). | Inspección de esquema + aserción DB en tests de creación (`subject_credentials.key_hash` único, `salt` 16 bytes hex, sin plaintext persistido); fixtures `db`, `fake_id_generator`. | `solu2-module1/test/evidence/nfr-sec-05-credential-assert.json` | PLANNED |
| NFR-AUDIT-06 | Consulta forense: ventana 30 días con `100,000 eventos` indexados responde `T < 500 ms` (`p95`) (PRD §6). **Gate formal: este umbral.** | Benchmark SQL/B-Tree sobre índice compuesto `(resource_type, timestamp)`; N=100,000; `page_size` default 50, clamp `[1, 100]`, cursores `(timestamp, id)`; fixtures `db`, `fake_clock`. Objetivo funcional separado de 50k/200 ms ver §Contradicciones. | `solu2-module1/test/evidence/nfr-audit-06-query-100k.json` | PLANNED |
| NFR-DISP-07 | Huella standalone: RAM `≤ 512 MB`; boot frío Docker Compose `T_boot < 5.0 s` (PRD §6). **Gate formal: este umbral.** | `docker stats` + healthcheck en CI; proceso único `workers: 1`; objetivo funcional separado de ARCH (`< 2.0 s`, `< 120 MB` reposo) ver §Contradicciones. | `solu2-module1/test/evidence/nfr-disp-07-docker-stats.txt` + `solu2-module1/test/evidence/nfr-disp-07-boot-time.json` | PLANNED |
| DEFERRED-Cola | Capacidad numérica máxima de cola + recuperación post-aceptación: **DEFERRED a Fase 3 NFR**, responsable `B — Daniel Gonzalez (Test-lead)`. Hasta entonces: **cola llena → `503`** (`AUTH_INTERNAL_POLICY_UNAVAILABLE`), sin descarte silencioso; `QueueReservation` (reserva pre-commit, publica post-commit). | Test de presión de cola + inyección de fallo post-aceptación (pendiente de definir N y política de recuperación; sin inventar capacidad numérica). Operaciones mutantes reservan/confirman espacio antes del commit; evento requerido no aceptado → 503 sin mutación. | `solu2-module1/test/evidence/nfr-deferred-queue-capacity.json` | PLANNED (DEFERRED) |
| G7-02-Obs | Observabilidad de barrido sin reserva de cola: log WARN estructurado (sin secretos) + métrica `scheduler_sweep_deferred_total`; reintento en siguiente barrido de 1 s. Responsable `B — Daniel Gonzalez (Test-lead)` [ADOPTED 2026-10-13, estudiante] (G7-02). | Test con cola forzada a llena durante barrido del scheduler (`fake_clock`): 1 barrido diferido → WARN + `scheduler_sweep_deferred_total +1` → reintento exitoso en siguiente tick 1 s. Sin cambio de contrato de las 3 operaciones (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`). | `solu2-module1/test/evidence/nfr-g7-02-sweep-deferred.json` + `solu2-module1/test/evidence/nfr-g7-02-sweep-deferred-warn.log` | PLANNED |

## Performance (concurrencia numérica)

- **NFR-PERF-01:** el único NFR con concurrencia nominal es `100 req/s` sostenidas (k6/Locust, 5 min, `POST /api/v1/authorize`). La arquitectura sostiene con proceso único asyncio (`workers: 1`, loop libuv `> 1,000 req/s`), SQLite WAL + `PRAGMA busy_timeout = 5000`, y auditoría asíncrona (cola `asyncio.Queue`, micro-lotes 50 ms/50 ev). Sin medición real, sin `EVIDENCED`.

## Reliability / failure (timeout, reintento, recuperación)

- **`busy_timeout 5000 → 503`:** agotado el `busy_timeout` antes de completar la operación requerida → `503` fail-closed sin commit parcial (`DENY` + `AUTH_INTERNAL_POLICY_UNAVAILABLE`, PRD §7.3). Lectores de `authorize` en UNA transacción de lectura (snapshot WAL, H-22); la caché de revocadas solo adelanta `DENY`, nunca `ALLOW`; 503 de lector solo ante `busy_timeout` agotado. Evidencia futura: `solu2-module1/test/evidence/nfr-rel-busy-timeout-503.json` (PLANNED).
- **Cola llena → 503:** evento requerido no aceptado → `503` sin mutación (incl. `roster.rejected` en tx separada → 422 tras aceptación en cola; `escalation.expired` con `QueueReservation`). Capacidad máxima y recuperación post-aceptación: DEFERRED (fila DEFERRED-Cola, Test-lead). Evidencia futura: `solu2-module1/test/evidence/nfr-rel-queue-full-503.json` (PLANNED).
- **Scheduler 1 s + reconciliación tras crash:** barrido cada `1 s` con `fake_clock`; solo `ACTIVE` con `granted_at <= now` y `expires_at <= now`; transición `ACTIVE→EXPIRED` con `QueueReservation` + reconciliación al reiniciar (`UPDATE … WHERE status='ACTIVE' … RETURNING`, un `escalation.expired` por ticket `EXPIRED` sin evento, idempotente por id; exactamente 1 evento por transición, G6-02). Si el barrido no reserva cola: WARN + `scheduler_sweep_deferred_total`, reintento 1 s (G7-02). Evidencia futura: `solu2-module1/test/evidence/nfr-rel-scheduler-crash-reconcile.json` (PLANNED).

## Security / isolation

- **0 secretos en logs:** regex `uai_live_[a-zA-Z0-9]{32}` debe dar 0 matches en 10,000 líneas (NFR-SEC-04, AD-06); crudo solo en respuesta de creación; resto enmascarado `uai_live_<4>••••<4>`; `audit_ledger`/`audit_events` sin plaintext.
- **Aislamiento por contexto (EDGE-01 + Mandatory Edge Case):** `Student` en CS101 (0 GPU) y TA en CS-480 (alta prioridad) resuelven independientes; header obligatorio `X-Academic-Subject-Context`; `resource.subject_id == context.subject_id` byte a byte o `403 RESOURCE_SUBJECT_MISMATCH`; sin contexto/membresía → `DENY SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`. Fixture `edge_case_seeds` (`TA-SOFIA-01`, CS101/CS-480, `2026-FALL`). Evidencia futura: `solu2-module1/test/evidence/nfr-sec-edge01-isolation.json` (PLANNED).
- **Append-only del ledger:** triggers físicos `BEFORE UPDATE`/`BEFORE DELETE` en `audit_ledger` y `audit_events` → `RAISE(ABORT, 'append-only')` (R3-06); cadena SHA-256 + singleton `audit_ledger_metadata` (`total_events_count`, `head_record_hash`); alteración → `AUDIT_LOG_TAMPERING_DETECTED`. Evidencia futura: `solu2-module1/test/evidence/nfr-sec-ledger-append-only.json` (PLANNED).

## Contradicciones de Plan-2 (registradas, no resueltas silenciosamente)

1. **Rendimiento de consulta forense:**
   - NFR formal **NFR-AUDIT-06** (PRD §6): `100,000 eventos`, ventana 30 días, `T < 500 ms` (`p95`) → **este es el gate**.
   - Objetivo funcional separado A — test de **FR-AUDIT-04** (PRD §4.4): dataset `50,000 eventos`, `T < 200 ms` (`p95`).
   - Objetivo funcional separado B — `planning/ARCHITECTURE.md` §2 (ledger `< 200 ms p95`) y `ux/C-UX-Scenarios/scenario-4.md` l.76 (`100,000 eventos` filtrados a 30 días en `< 200 ms p95`; l.28: `p95: 168 ms`).
   - Plan: el gate PASS/FAIL usa **100k / 500 ms p95**; los `200 ms` (50k y 100k) se miden y reportan como objetivos funcionales separados, sin sustituir el gate.
2. **Boot frío standalone:**
   - NFR formal **NFR-DISP-07** (PRD §6): `T_boot < 5.0 s` → **este es el gate**.
   - Objetivo funcional separado — `planning/ARCHITECTURE.md` §1.1: inicio en frío `< 2.0 s` (y huella `< 120 MB` en reposo frente a `≤ 512 MB` del NFR).
   - Plan: el gate usa **5.0 s / 512 MB**; los `2.0 s / 120 MB` se reportan como objetivos funcionales separados.
3. **Dataset y concurrencia nominal en contradicción (registrado, sin inventar):** los N funcionales (120 roster E2E, 1,000 integridad ledger, 100 req/s solo en PERF-01) difieren de los N de NFR (1,000 ingesta, 100,000 auditoría); cada medición usa su N nominal declarado arriba.

## Estado global

- Los 7 NFR formales + fila DEFERRED + fila G7-02 están en `PLANNED`. **Ningún NFR queda `EVIDENCED`** (no hay implementación ni corrida medible real; este stop-point de solutioning solo admite interfaces/stubs y ATDD RED).
- Responsable de la fila DEFERRED y de G7-02: `B — Daniel Gonzalez (Test-lead)`.

## PREGUNTAS BLOQUEANTES

Ninguna: todo lo material pedido (7 NFR, concurrencia 100 req/s, reliability/failure, security/isolation, contradicciones con gate explícito, fila DEFERRED + G7-02 con responsable, todo PLANNED) está cubierto con fuentes citadas sin inventar umbrales.
