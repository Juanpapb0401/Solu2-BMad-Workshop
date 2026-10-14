---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - 'planning/prd.md'
  - 'planning/ARCHITECTURE.md'
  - 'ux/DESIGN.md'
  - 'ux/EXPERIENCE.md'
  - 'ux/C-UX-Scenarios/00-ux-scenarios.md'
  - 'ux/C-UX-Scenarios/scenario-1.md'
  - 'ux/C-UX-Scenarios/scenario-2.md'
  - 'ux/C-UX-Scenarios/scenario-3.md'
  - 'ux/C-UX-Scenarios/scenario-4.md'
  - 'solu2-module1/planning/detailed-design/contracts.md'
  - 'solu2-module1/planning/detailed-design/ports-and-adapters.md'
  - 'solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md'
  - 'solu2-module1/planning/detailed-design/schemas/001_module1_schema.sql'
  - 'solu2-module1/planning/detailed-design/schemas/dto.py'
  - 'solu2-module1/planning/detailed-design/schemas/openapi.yaml'
  - 'solu2-module1/planning/detailed-design/schemas/roles_matrix.v0.json'
  - 'solu2-module1/planning/detailed-design/reviews/review-detailed-design.md'
  - 'solu2-module1/test/test-design.md'
  - 'solu2-module1/test/atdd-checklist.md'
  - 'solu2-module1/test/nfr-evidence.md'
  - 'solu2-module1/test/conftest.py'
  - 'solu2-module1/test/fakes/world.py'
---

# Módulo 1 (User, Role, and Subject Access Manager) - Epic Breakdown

## Overview

Este documento descompone los requisitos del PRD del Módulo 1, la especificación de UX y los contratos de diseño detallado en 4 épicas y 16 historias. Cada historia se implementa contra las tres operaciones confirmadas en Annex A p.13: `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`.

Convenciones de este documento:
- Los node IDs de pytest son los de `cd solu2-module1 && .venv/bin/pytest --collect-only -q` (155 nodos: 130 en suites ATDD de contrato, 21 guardas DDL/pureza/envelope y 4 harness; ver «Verificación»).
- Los Test IDs (T-...) son los de `solu2-module1/test/atdd-checklist.md` y los de las docstrings de la suite. Algunos Test IDs están duplicados en esa checklist (p. ej. `T-REV-01`, `T-ROS-16`); aquí se cita el node ID, que sí es único.
- `SIN NODE ID` marca solo los gaps abiertos tras la Ronda 10 (G-1, G-15 y G-16), con razón y owner en la sección "Gaps de cobertura". Los demás gaps ya tienen node ID. No se inventan node IDs.
- `[ASSUMPTION]` marca decisiones tomadas por esta corrida sin fuente explícita.
- Decisiones aplicadas: Rondas 7, 8, 9 y 10 de `.work/paquete-decisiones-F-H.md` (Ronda 10: secciones «Umbrales triageados» y «Correcciones Ronda 10») (ver secciones "Decisiones Ronda 7 aplicadas", "Decisiones que cerraron las preguntas (Ronda 8)" y "Decisiones Ronda 9 aplicadas").
- Fixtures de identidad: `STU-98432` = Mateo (Student en CS101 y CS-480, `seed_student_pair`), `TA-SOFIA-01` = Sofia (Student en CS101 y TA en CS-480, `edge_case_seeds`), Dr. Marcus Vance = `actor` con `actor_role = admin` (`ADMIN_TOKEN` del fake del verificador). `STU-MATEO-99` de PRD §4.3 se trata como el mismo actor (R8-08).

## Requirements Inventory

### Functional Requirements

FR-INGEST-01: Ingestión atómica de nóminas de asignatura (PRD §4.1). Lote de N filas, validación previa, todo o nada, credenciales `uai_live_` emitidas solo en la cola de entrega, nunca en la respuesta de creación.
FR-ESCAL-02: Escalación temporal de privilegios con ventana acotada (PRD §4.2). Alcance contratado en este documento: que `resolveEffectivePermissions` honre tickets ACTIVE y vencidos (AD-13, I2, EDGE-01 con escalación). Creación, aprobación y rechazo de escalaciones quedan fuera de alcance (ver sección "Fuera de alcance de Solu-2"); su respaldo físico en DDL sí está probado (T-ESC-GUARD-01, T-ESC-GUARD-03).
FR-REVOC-03: Revocación sub-minuto de credenciales por baja académica (PRD §4.3). Transición ACTIVE a DROPPED, credenciales del par a REVOKED, preservación de otros cursos.
FR-AUDIT-04: Trazabilidad forense e inspección criptográfica (PRD §4.4). Alcance contratado en este documento: ledger encadenado append-only y verificable (AD-04, Q3). La consulta forense paginada queda fuera de alcance.

### NonFunctional Requirements

NFR-PERF-01: Latencia de decisión RBAC p95 < 20 ms; p99 < 50 ms bajo carga sostenida de 100 req/s (PRD §6). Estado: PLANNED.
NFR-PERF-02: Ingestión de lote de 1,000 registros en T < 3.0 s (PRD §6). Estado: PLANNED. El E2E funcional de 120 filas < 2.0 s (FR-INGEST-01) es el umbral gate separado; ver «Umbrales triageados».
NFR-REVOC-03: Invalidación local en memoria T_local < 200 ms; corte perimetral T_revoc < 60 s (TTL máximo de caché de clientes = 60 s) (PRD §6). Estado: PLANNED.
NFR-SEC-04: Exactamente 0 llaves de API o tokens completos en texto plano en logs, errores o auditoría (regex `uai_live_[a-zA-Z0-9]{32}` sobre 10,000 líneas) (PRD §6). Estado: PLANNED.
NFR-SEC-05: Llaves de API hasheadas con SHA-256 y salt de 16 bytes; valor crudo visible una sola vez (PRD §6). Estado: PLANNED.
NFR-AUDIT-06: Consulta forense sobre ventana de 30 días con 100,000 eventos indexados en T < 500 ms (p95) (PRD §6; gate formal según nfr-evidence.md). El índice compuesto `(resource_type, timestamp)` ya existe en DDL (R8-07). Estado: PLANNED.
NFR-DISP-07: RAM <= 512 MB; boot frío de Docker Compose T_boot < 5.0 s (PRD §6). Estado: PLANNED.

### Additional Requirements

- Stack heredado (confirmado 2026-10-12): Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL con writer único y `busy_timeout = 5000` (ARCHITECTURE-SPINE, Stack).
- Operaciones y rutas canónicas (AD-09): `POST /api/v1/authorize` (con header `X-Academic-Subject-Context`), `POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop`, `POST /api/v1/subjects/{subject_id}/roster`.
- Orden único de validación (contracts §1): 401 `AUTH_TOKEN_INVALID`, 403 `ADMIN_ROLE_REQUIRED` (solo revoke e ingest), sintaxis (400), identidad o curso (404), mismatch de recurso (403), membresía (403), matriz (403).
- Puertos outbound (ports-and-adapters §1): `Clock`, `IdGenerator`, `MembershipStore`, `IdentityStore`, `CredentialStore`, `EscalationStore`, `LedgerWriter`, `QueueReservation`, `TokenVerifierPort`, `CredentialDeliveryPort`, `RegistrarSource`, `TelemetryPort` (R8-06, adaptador `sim_telemetry`).
- Límites de lote (contracts §3 P2): 1 a 1,000 filas de datos; cuerpo <= 5,000,000 bytes reales recibidos; UTF-8 sin BOM.
- Seed canónico (AD-10): identidad con Student en CS101 y TA en CS-480 (`edge_case_seeds`).
- Matriz ejecutable v0 (`schemas/roles_matrix.v0.json`) con claves `{subject_id, role, action, resource_class, allow}` y `resource_catalog` (R6b-01).
- Decisiones de la Ronda 7 aplicadas, con una modificación posterior: R7-03 queda modificada por R8-01 (una credencial por fila aceptada, no por identidad creada).

### UX Design Requirements

UX-DR1: Estado Loading de carga masiva: progreso de SUBIDA calculado en cliente (bytes enviados / total) y botón inactivo con `Validando lote atómico...` hasta la respuesta. No hay progreso por fila: la ingesta es atómica y síncrona (AD-02). El texto `N / 120 registros` no tiene contrato y se reemplaza (M-1, R10; EXPERIENCE §2.1 y scenario-1 no se editan).
UX-DR2: Estado Empty de membresías (Caso A, asignatura sin estudiantes) (EXPERIENCE §2.2 Caso A).
UX-DR3: Estado Error transaccional 422 con detalle de fila afectada, campo y regla violada (EXPERIENCE §2.3 Caso A).
UX-DR4: Estado Success de ingestión con chips `[Procesados] [Creados] [Vinculados] [Errores]` (EXPERIENCE §2.4).
UX-DR5: Banner E-01 Confused Deputy `RESOURCE_SUBJECT_MISMATCH` (EXPERIENCE §3.2).
UX-DR6: Banner E-02 Revocación por baja `SUBJECT_ENROLLMENT_DROPPED` (EXPERIENCE §3.2).
UX-DR7: Banner E-03 Expiración de escalación `STATUS_ESCALATION_EXPIRED` (EXPERIENCE §3.2).
UX-DR8: Banner E-04 Denegación de escalación por jefatura `ESCALATION_REQUEST_REJECTED` (EXPERIENCE §3.2; fuera de alcance).
UX-DR9: Estado Empty de identidad sin asignaturas `EDGE-UX-01` (EXPERIENCE §2.2 Caso D).
UX-DR10: Modal de sesión expirada `EDGE-UX-03` en consultas forenses (EXPERIENCE §2.5; fuera de alcance).

## FR Coverage Map

FR-INGEST-01: Epic 3 - E3-S1 (carga válida, credenciales y 404 de curso), E3-S2 (fila 85 con rollback e identidad suspendida), E3-S3 (anti role-smuggling), E3-S4 (límites, sintaxis y admin).
FR-ESCAL-02: Epic 4 - E4-S2 (ticket vencido en resolve, AD-13). Resto del FR fuera de alcance.
FR-REVOC-03: Epic 2 - E2-S1 (baja y revocación), E2-S2 (403 tras baja), E2-S3 (idempotencia, carrera y fail-closed), E2-S4 (solo admin), E2-S5 (datos de baja inválidos).
FR-AUDIT-04: Epic 1 - E1-S3 (ledger encadenado append-only). Consulta forense paginada fuera de alcance.

## Epic List

### Epic 1: Mateo confirma su acceso a CS-480 con evidencia auditable (walking skeleton)
Valor para Mateo y para el Dr. Marcus Vance: el prototipo arranca con fixtures y adaptadores simulados, una autorización real recorre HTTP, aplicación, dominio, SQLite y ledger, y el ledger es verificable.
**FRs cubiertos:** FR-AUDIT-04 (parcial). Contextos de PRD §5.2.

### Epic 2: El Dr. Marcus Vance da de baja a Mateo y el corte es inmediato
Valor para el Dr. Marcus Vance: una baja revoca el acceso al par (curso, estudiante) sin afectar otros cursos, y las repeticiones o fallos no dejan estados a medias. Valor para Mateo: su acceso a CS-480 se corta con respuesta explicada.
**FRs cubiertos:** FR-REVOC-03.

### Epic 3: El Dr. Marcus Vance carga la nómina de CS-480 de forma atómica
Valor para el Dr. Marcus Vance: carga 120 alumnos en una operación, o la rechaza completa con el manifiesto de la fila afectada. Ninguna importación cambia el rol de quien ya está matriculado.
**FRs cubiertos:** FR-INGEST-01.

### Epic 4: Sofia obtiene permisos independientes por curso y su escalación vence sin residuos
Valor para Sofia (TA en CS-480 y estudiante en CS101): cada contexto se resuelve por separado con explicación citada, y su escalación temporal vence en el instante exacto.
**FRs cubiertos:** FR-ESCAL-02 (parcial), Mandatory Edge Case EDGE-01, PRD §5.2.

Dependencias entre épicas: E1 no depende de ninguna; E2 depende de E1; E3 depende de E1 y E2; E4 depende de E1. Ninguna épica depende de una posterior.

---

## Epic 1: Mateo confirma su acceso a CS-480 con evidencia auditable (walking skeleton)

Objetivo: un happy path real de punta a punta (HTTP adapter, application, domain, SQLite, ledger) con fixtures seed y adaptadores simulados.

### Story E1-S1: El prototipo arranca con fixtures y adaptadores simulados

- **Protagonista:** Dr. Marcus Vance (Department Chair y administrador de la plataforma)
- **Como** Dr. Marcus Vance, **quiero** que el prototipo arranque con identidades, cursos, matrículas y la flota simulada, con reloj, IDs, verificador de token, cola y telemetría simulados, **para** validar el sistema sin servicios institucionales vivos.
- **Requisito fuente:** PRD §8.1 (3. Fixtures simulados de identidad), PRD §2.2 (dependencias mockeadas), AD-10 (seed canónico), NFR-DISP-07 (PLANNED).
- **Escenario UX + estados:** ninguno directo (infraestructura de prueba). No aplica Loading/Empty/Error/Success/Denied.
- **Contrato:** ninguno de las tres operaciones. Infraestructura: ports-and-adapters §1 (`adapters/fake_clock`, `adapters/fixtures`, `adapters/fake_token_verifier`, `adapters/fake_credential_outbox`, fake de cola `QueueReservation`, adaptador `adapters/sim_telemetry` que implementa `TelemetryPort`, R8-06).
- **Endpoint + DTOs:** ninguno.
- **Códigos de error:** ninguno.
- **Migración (M-6, R10):** E1-S1 aplica la migración `schemas/001_module1_schema.sql` completa, aprobada en Fase 2. Justificación: la consigna exige el schema como entregable de Fase 2 (contrato aprobado, no construido historia a historia). Cada historia posterior solo usa o verifica las tablas e invariantes que cita en su AC.
- **Binding invariants:** AD-08 (adapters fuera de `domain/`), AD-10 (seed EDGE-01), AD-13 (reloj inyectado). AD-12 (K-6: citados por tests de esta historia).
- **ATDD:**
  - Harness (verde, no RED): `test/test_harness_smoke.py::test_seed_fleet_topology`, `test/test_harness_smoke.py::test_db_has_ddl_tables`, `test/test_harness_smoke.py::test_fake_clock_advances`, `test/test_harness_smoke.py::test_fake_id_generator_deterministic`.
  - Telemetría simulada (R8-06): `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric` (T-SCH-04).
  - Pureza de `domain/` (AD-08): `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_has_no_infrastructure_imports_or_clock_calls` (T-PUR-GUARD-01, guarda verde).
  - Lint de no-determinismo de `domain/` (H-25, AD-08, T-PUR-GUARD-02): `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[os.urandom]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[from-os-urandom]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[uuid4]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[secrets]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[time.monotonic]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[datetime.now]`, `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[random]`.
- **Criterios de aceptación:**
  - Happy: **Given** el DDL `001_module1_schema.sql` aplicado a una base SQLite temporal, **When** se ejecuta la topología `seed_fleet`, **Then** la base contiene las tablas `identities`, `subjects`, `roles`, `subject_memberships` y el seed tiene 32 nodos (31 workstations y 1 servidor central), 33 GPUs y 840 GB de VRAM (`test_seed_fleet_topology`, `test_db_has_ddl_tables`).
  - Happy reloj: **Given** `FakeClock` con inicio `2026-09-23T15:04:05.000000Z`, **When** se llama `advance(3600)`, **Then** `now()` devuelve `2026-09-23T16:04:05.000000Z` (`test_fake_clock_advances`).
  - Happy IDs: **Given** `FakeIdGenerator`, **When** se piden dos IDs con prefijo `roster`, **Then** devuelve `roster-00000001` y `roster-00000002` (`test_fake_id_generator_deterministic`).
  - Failure: **Given** `edge_case_seeds` ejecutado dos veces sobre la misma base, **Then** la segunda inserción falla por restricción UNIQUE y no deja filas duplicadas. `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_edge_case_seed_duplicates_rejected_by_pk` (G-14).
- **Depende de:** ninguna.
- **DoD:** harness en verde; `scripts/quality_gate.sh` verde (Etapa 1 pureza de `domain/` no aplica a adapters); sin secretos en logs; decision log actualizado si el seed cambia.

### Story E1-S2: Mateo obtiene ALLOW de inferencia en CS-480 con evento de autorización

- **Protagonista:** Mateo (estudiante; `STU-98432` en fixtures)
- **Como** Mateo, **quiero** que mi solicitud de inferencia sobre `llama-3-8b-instruct` en el contexto CS-480 se resuelva dentro de ese contexto, **para** usar el modelo de mi asignatura y saber por qué fue permitida.
- **Requisito fuente:** PRD §5.2 (Context RBAC), PRD §3.3 (Mateo), NFR-PERF-01 (PLANNED).
- **Escenario UX + estados:** EDGE-01 (selector de contexto académico activo). Success: respuesta 200 `AuthorizeResponse`. Loading: overlay `Evaluando tupla (subject, role, resource, action)...` (EXPERIENCE §2.1, RBAC API Explorer). Error: ErrorBody 400, 401, 404, 503 (ver códigos). Denied: no aplica en el happy path.
- **Contrato:** `resolveEffectivePermissions` (contracts §1). P1 (identidad), P2 (curso), P4 (ARN), P4b (`action` en `{inference, training}`), P5 (membresía ACTIVE y `resource.subject == courseId` byte a byte). Q1 (ALLOW con `effective_role = 'student'`), Q3 (un evento de auditoría), I4 (sin cuota GPU ni prioridad en la respuesta). Concurrencia: lectura de estado más escritura encolada del evento (ADVF-05).
- **Endpoint + DTOs:** `POST /api/v1/authorize` con header `X-Academic-Subject-Context: CS-480`. Entrada `AuthorizeRequest` `{ user_id: "STU-98432", resource_arn: "urn:uai:subject:CS-480:model:llama-3-8b-instruct", action: "inference" }`. Salida 200 `AuthorizeResponse` `{ decision: "ALLOW", effective_role: "student", explanation: ExplanationDTO }`.
- **Códigos de error:** 401 `AUTH_TOKEN_INVALID` (RED en E4-S1, T-RES-12); 404 `UNKNOWN_IDENTITY`; 404 `UNKNOWN_COURSE`; 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` (fail-closed).
- **Binding invariants:** AD-01, AD-04, AD-08, AD-09, AD-10, AD-11, AD-13 (captura única de `request_now`, H-16). AD-12 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-RES-HP-01 `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_student_inference_cs480`
  - T-RES-HP-02 `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allow_appends_one_authorization_event`
  - T-RES-P-01 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_identity_404_no_mutation`
  - T-RES-P-02 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_course_404_no_mutation`
  - T-RES-11 (Empty Caso D, UX-DR9) `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`
  - T-RES-13 (503 cola llena) `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_queue_full_503_no_decision_no_mutation`
  - T-RES-15 (R12-B01, SEC B-01: `Clock` lanza -> 503 fail-closed, AD-08/AD-12) `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation`
  - T-HTTP-01 (rutas declaradas = operaciones OpenAPI, AD-09) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_declared_routes_match_openapi_one_route_per_operation`
  - T-RES-05 (H-16, AD-13: `request_now` capturado una vez y reutilizado como `occurredAt`) `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_request_now_captured_once_and_reused_as_occurred_at`
- **Criterios de aceptación:**
  - Happy: **Given** `STU-98432` con membresía ACTIVE en CS-480 (término 2026-FALL) y una credencial ACTIVE en CS-480, **When** `POST /api/v1/authorize` con header `X-Academic-Subject-Context: CS-480` y `resource_arn = urn:uai:subject:CS-480:model:llama-3-8b-instruct`, `action = inference`, **Then** la respuesta es 200 con `decision = ALLOW`, `effective_role = student`, y `explanation.rule_ids` no vacío que cita un AD-n (AD-11).
  - Happy evento: **Given** la misma solicitud, **When** se resuelve, **Then** la tabla `audit_ledger` gana exactamente 1 fila con `decision = ALLOW`, `reason_code = SUCCESS`, `actor_id` del token y `resource_arn` de la solicitud (`test_resolve_allow_appends_one_authorization_event`).
  - Failure identidad: **Given** `user_id = "NO-EXISTE-99"`, **When** se llama `/authorize` con CS-480, **Then** la respuesta es 404 `UNKNOWN_IDENTITY` con detail `No identity resolves 'NO-EXISTE-99'.` y cero filas nuevas en `audit_ledger` y en tablas de negocio (`test_resolve_unknown_identity_404_no_mutation`).
  - Failure curso: **Given** `user_id = "STU-98432"` y header `X-Academic-Subject-Context: CS-999` (curso inexistente), **When** se llama `/authorize`, **Then** la respuesta es 404 `UNKNOWN_COURSE` con detail `Course 'CS-999' is not an active subject.` y cero mutaciones (`test_resolve_unknown_course_404_no_mutation`).
  - Empty Caso D (EDGE-UX-01): **Given** `STU-ONLY-CS101` con membresía solo en CS101, **When** se consulta CS-480, **Then** DENY `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (`test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`).
  - Precedencia: **Given** identidad inexistente y curso inexistente en la misma solicitud, **Then** la respuesta es `UNKNOWN_IDENTITY` (precedencia F-03, contracts §1 paso 4). `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_missing_identity_and_course_reports_identity_first` (G-7).
  - Rendimiento: **Given** carga sostenida de 100 req/s durante 5 minutos, **Then** p95 < 20 ms y p99 < 50 ms (NFR-PERF-01). `SIN NODE ID` (gap G-16: medición PLANNED en `solu2-module1/test/evidence/`).
- **Depende de:** E1-S1.
- **DoD:** tests ATDD de la historia en verde al pasar a GREEN; `quality_gate.sh` verde; ningún `uai_live_` completo en logs; decision log actualizado.

### Story E1-S3: Dra. Elena Gómez verifica que el ledger es encadenado y append-only

- **Protagonista:** Dra. Elena Gómez (Auditora de Cumplimiento)
- **Como** Dra. Elena Gómez, **quiero** que cada decisión quede en un ledger encadenado con SHA-256 que no admite UPDATE ni DELETE, **para** comprobar que ningún registro fue alterado.
- **Requisito fuente:** FR-AUDIT-04 (alcance contratado: ledger encadenado append-only y verificable, AD-04/Q3); NFR-AUDIT-06 (PLANNED, índice ya en DDL); PRD §4.4 Prueba de integridad.
- **Escenario UX + estados:** SC-04 (visor de ledger con verificación SHA-256) como referencia. La vista forense queda fuera de alcance. No se implementa Loading/Empty/Error de la consulta.
- **Contrato:** `resolveEffectivePermissions` Q3 (evento con `eventId`, `occurredAt` UTC, `decision`, `reason_code` y hash encadenado según AD-04 §5; codec local; génesis = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (constante de ARCHITECTURE.md:97; R10 M-2 corrige H-15); longitud de frame en bytes UTF-8; orden FIFO y `id ASC`). Triggers `BEFORE UPDATE`/`BEFORE DELETE` sobre `audit_ledger` y `audit_events` (contracts §5, R3-06). Timestamp de formato fijo `YYYY-MM-DDTHH:MM:SS.ffffffZ` en `audit_ledger` (R9-04).
- **Endpoint + DTOs:** ninguno público. Persistencia en `audit_ledger` y `audit_events` (schemas/001_module1_schema.sql). Eventos en `schemas/events.md`.
- **Códigos de error:** `RAISE(ABORT, 'append-only')` en la base para UPDATE/DELETE. `500 AUDIT_LOG_TAMPERING_DETECTED` queda fuera de esta historia (verificación de cadena fuera de las tres operaciones, DEFER Fase 3).
- **Binding invariants:** AD-04, AD-06, AD-07 (paginación acotada, clamp de `page_size`; C-1, R10), AD-11 (envelope `ErrorBody` sin `ExplanationDTO` para 500, F-06).
- **ATDD:**
  - T-LED-01 `test/atdd/module1_contracts.test.py::TestLedgerChain::test_ledger_chain_and_anchor`
  - T-LED-GUARD-01 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_update_rejected` (guarda, verde)
  - T-LED-GUARD-02 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_delete_rejected` (guarda, verde)
  - T-LED-GUARD-03 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_update_rejected` (guarda, verde)
  - T-LED-GUARD-04 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_delete_rejected` (guarda, verde)
  - T-LED-GUARD-06 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_timestamp_fixed_format_check` (guarda, verde)
  - T-LED-GUARD-05 `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_resource_type_not_null_and_indexed` (guarda, verde; índice NFR-AUDIT-06)
  - T-AD07-01 `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_zero_becomes_one` (RED; C-1, R10)
  - T-AD07-02 `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_above_limit_becomes_100` (RED; C-1, R10)
  - T-ERR-GUARD-01 (F-06, AD-11: el 500 `AUDIT_LOG_TAMPERING_DETECTED` usa `ErrorBody` sin `explanation`; guarda de schema) `test/atdd/module1_guard_contracts.test.py::TestErrorEnvelope::test_guard_audit_log_tampering_500_uses_error_body_without_explanation`
- **Criterios de aceptación:**
  - Happy: **Given** dos autorizaciones consecutivas resueltas (E1-S2), **When** se verifica la cadena ordenada por `id ASC`, **Then** el `prev_record_hash` del primer evento es la constante génesis `e3b0c442…b855` (R10 M-2) y el `prev_record_hash` del segundo es el `record_hash` del primero, y el hash se calcula con el codec de contracts §1 Q3 (`test_ledger_chain_and_anchor`).
  - Failure UPDATE: **Given** una fila existente en `audit_ledger`, **When** se ejecuta `UPDATE audit_ledger SET decision = 'DENY' WHERE id = 1`, **Then** la base aborta con el mensaje `append-only` y la fila queda sin cambios (`test_guard_audit_ledger_update_rejected`).
  - Failure DELETE: **Given** la misma fila, **When** se ejecuta `DELETE FROM audit_ledger WHERE id = 1`, **Then** la base aborta con `append-only` y la fila sigue existiendo (`test_guard_audit_ledger_delete_rejected`).
  - Failure envelope: **Given** una fila en `audit_events`, **When** se ejecuta UPDATE o DELETE, **Then** la base aborta con `append-only` (`test_guard_audit_events_update_rejected`, `test_guard_audit_events_delete_rejected`).
  - Restricción de formato: **Given** un timestamp de evento en `audit_ledger`, **Then** debe tener formato fijo `YYYY-MM-DDTHH:mm:ss.ffffffZ` (CHECK GLOB, ADVF-23, R9-04) (`test_guard_audit_timestamp_fixed_format_check`).
  - Índice de auditoría (NFR-AUDIT-06, R8-07): **Given** el DDL, **Then** `audit_ledger.resource_type` es NOT NULL y existe el índice `(resource_type, timestamp)` (`test_guard_audit_ledger_resource_type_not_null_and_indexed`). El NFR de medición (100,000 eventos, p95 < 500 ms) sigue PLANNED (gap G-16).
  - Paginación acotada (AD-07, R8-03, C-1): **Given** `page_size = 0`, **Then** se clampa a 1; **Given** `page_size = 101`, **Then** se clampa a 100 (`test_ad07_clamp_page_size_zero_becomes_one`, `test_ad07_clamp_page_size_above_limit_becomes_100`). La consulta forense paginada queda fuera de alcance (owner B).
- **Depende de:** E1-S2.
- **DoD:** guardas en verde; `test_ledger_chain_and_anchor` en verde al pasar a GREEN; `quality_gate.sh` verde; decision log actualizado.

---

## Epic 2: El Dr. Marcus Vance da de baja a Mateo y el corte es inmediato

Objetivo: una baja revoca las credenciales del par (curso, estudiante) en una transacción, deja intactos los otros cursos, y las repeticiones o fallos no dejan estados a medias.

### Story E2-S1: Dr. Vance registra la baja de Mateo en CS-480 y se revocan sus credenciales del par

- **Protagonista:** Dr. Marcus Vance (Department Chair, actor con `actor_role = admin`)
- **Como** Dr. Marcus Vance, **quiero** registrar la baja de Mateo en CS-480 y que sus credenciales de esa asignatura queden REVOKED en el mismo acto, **para** que no conserve acceso al pool de CS-480 mientras sigue matriculado en CS101.
- **Requisito fuente:** FR-REVOC-03 (reglas 2 y 4; salida 200 con `revocation_propagated_at`; trazabilidad), NFR-REVOC-03 (T_local < 200 ms; T_revoc < 60 s; PLANNED).
- **Escenario UX + estados:** SC-03 (tabla de membresías con badge `[✖ DROPPED / REVOKED]`). Success: 200 `RevokeResponse` con `status = REVOKED`. Loading: no aplica (respuesta inmediata en el happy path). Error: ErrorBody 400, 401, 403, 404, 409, 503 (ver códigos). Denied: no aplica en el happy path (ver E2-S2).
- **Contrato:** `revokeCourseAccess` (contracts §2). P0 (actor `admin`, token vía `TokenVerifierPort`), P1 (identidad y curso existen), P2 (membresía ACTIVE del par), P3 y P4 (sintaxis, verificadas en E2-S5). Q1 (200 con `status = REVOKED`), Q2 (`ACTIVE → DROPPED` con `dropped_at` y todas las credenciales `ACTIVE` del par a `REVOKED` con `revoked_at`, en una transacción `BEGIN IMMEDIATE`), Q3 (exactamente un evento `membership.revoked` con `decision = DENY`, `reasonCode = SUBJECT_ENROLLMENT_DROPPED`). I1 (otros cursos intactos), I2 (ninguna credencial del par autorizable tras el commit).
  - **Nota de firma (R7-01, aceptada por R8-10):** la función de dominio recibe `actor`, `drop_reason`, `timestamp` y `request_now` como parámetros explícitos; `user_id` y `course_id` son la operación conceptual de Annex A. El adapter HTTP solo parsea. La validación P3/P4 es función pura testeable con `fake_clock`. Escrita en contracts §2.
  - Orden R3-06: validar (P1 a P4) -> `BEGIN IMMEDIATE` -> `UPDATE ... WHERE status='ACTIVE' RETURNING` + `QueueReservation` -> commit -> publicar evento.
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/enrollments/STU-98432/drop` con `Authorization: Bearer <ADMIN_TOKEN>`. Entrada `RevokeRequest` `{ drop_reason: "Estudiante retiró la asignatura formalmente", timestamp: "2026-09-23T15:04:05.120Z" }`. Salida 200 `RevokeResponse` `{ student_id: "STU-98432", subject_id: "CS-480", status: "REVOKED", revocation_propagated_at, explanation: ExplanationDTO }`.
- **Códigos de error:** 401 `AUTH_TOKEN_INVALID` (RED en E2-S4, T-REV-11); 403 `ADMIN_ROLE_REQUIRED` (E2-S4); 404 `UNKNOWN_IDENTITY`, `UNKNOWN_COURSE`, `MEMBERSHIP_NOT_FOUND`; 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE`.
- **Binding invariants:** AD-03, AD-04, AD-09, AD-11, AD-12.
- **ATDD:**
  - T-REV-HP-01 `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_active_pair_returns_revoked`
  - T-REV-HP-02 `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_emits_one_membership_revoked_event`
  - T-REV-01 (I2) `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_all_credentials`
  - T-REV-01b (I1) `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_preserves_other_course`
  - T-REV-04 `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_never_enrolled_pair_404_membership_not_found`
- **Criterios de aceptación:**
  - Happy: **Given** el seed `seed_student_pair`: `STU-98432` ACTIVE en CS101 (2 credenciales ACTIVE) y ACTIVE en CS-480 (1 credencial ACTIVE), **When** el actor admin llama `POST .../enrollments/STU-98432/drop` en CS-480 con `drop_reason` válido, **Then** la respuesta es 200 con `status = REVOKED` y `revocation_propagated_at` igual al instante del `Clock` de la solicitud.
  - Happy estado: **Given** lo anterior, **When** se consulta la base, **Then** la membresía CS-480 es `DROPPED` con `dropped_at` fijado, su única credencial es `REVOKED` con `revoked_at` fijado, y la membresía y las 2 credenciales de CS101 siguen `ACTIVE` (`test_revoke_all_credentials`, `test_revoke_preserves_other_course`).
  - Happy evento: **Given** lo anterior, **When** se revisa `audit_ledger`, **Then** hay exactamente 1 evento `membership.revoked` con `decision = DENY`, `reason_code = SUBJECT_ENROLLMENT_DROPPED`, `actor_id` del token admin, `resource_arn = urn:uai:subject:CS-480:model:*` y `action = revoke` (ADVF-03 y R3-03) (`test_revoke_emits_one_membership_revoked_event`).
  - Failure no matriculado: **Given** `STU-98432` sin ninguna membresía en `CS-480` (par nunca existió), **When** se llama el drop, **Then** la respuesta es 404 `MEMBERSHIP_NOT_FOUND` con detail `No membership for 'STU-98432' in 'CS-480'.` y cero filas mutadas y cero eventos (`test_revoke_never_enrolled_pair_404_membership_not_found`).
  - Failure sin datos: **Given** un drop con `drop_reason` vacío, **Then** la respuesta es 400 `MALFORMED_DROP_REASON` y la base queda igual. Cubierto en E2-S5, no se duplica aquí.
- **Depende de:** E1-S1, E1-S3.
- **DoD:** ATDD de la historia en verde al pasar a GREEN; `quality_gate.sh` verde; sin `uai_live_` completo en logs o respuesta; decision log actualizado.

### Story E2-S2: Mateo recibe 403 SUBJECT_ENROLLMENT_DROPPED al intentar usar CS-480 tras la baja

- **Protagonista:** Mateo (estudiante)
- **Como** Mateo, **quiero** que una petición a CS-480 tras mi baja se rechace con una explicación clara, **para** entender que mi acceso a esa asignatura cesó y que mi acceso a CS101 no cambió.
- **Requisito fuente:** FR-REVOC-03 (salida: rechazo instantáneo 401/403 en cualquier solicitud del par; PRD §4.3 Prueba E2E: DENY con `SUBJECT_ENROLLMENT_DROPPED`, propagación registrada < 500 ms; AC usa el umbral gate < 200 ms de NFR-REVOC-03, ver «Umbrales triageados»).
- **Escenario UX + estados:** SC-03 y banner E-02 (Denied). Denied: banner `Matrícula Cancelada: Acceso a Pool Privado Revocado` con código `SUBJECT_ENROLLMENT_DROPPED (HTTP 403)`. Success: no aplica. Loading: overlay de evaluación.
- **Contrato:** `resolveEffectivePermissions` P5 con membresía `DROPPED` -> `SUBJECT_ENROLLMENT_DROPPED` (ADVF-08; otro estado no activo -> `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`; G-4b: `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED]` y `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[COMPLETED]`). Q1 (DenyBody con `decision = DENY`). Concurrencia (contracts §2): un resolve posterior al commit de la baja deniega con `403 SUBJECT_ENROLLMENT_DROPPED`.
- **Endpoint + DTOs:** `POST /api/v1/authorize` con header `X-Academic-Subject-Context: CS-480` y `user_id = "STU-98432"`. Salida 403 `DenyBody` `{ type, title, status: 403, detail: "Membership for 'CS-480' was dropped at {ts}.", instance, code: "SUBJECT_ENROLLMENT_DROPPED", decision: "DENY", explanation: ExplanationDTO }`.
- **Códigos de error:** 403 `SUBJECT_ENROLLMENT_DROPPED`.
- **Binding invariants:** AD-01, AD-03, AD-11, AD-12.
- **ATDD:**
  - T-RES-03 `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_revoke_commit_denies_enrollment_dropped`
  - T-CON-01 `test/atdd/module1_contracts.test.py::TestConcurrency::test_resolve_concurrent_with_revoke_never_allows_after_commit` (ningún ALLOW tras el commit de la baja)
- **Criterios de aceptación:**
  - Happy (regla): **Given** la baja de E2-S1 confirmada, **When** `STU-98432` llama `/authorize` con header CS-480 y `action = inference` sobre `llama-3-8b-instruct`, **Then** la respuesta es 403 `DenyBody` con `decision = DENY`, `code = SUBJECT_ENROLLMENT_DROPPED`, y `explanation.rule_ids` no vacío que cita AD-03 (`test_resolve_after_revoke_commit_denies_enrollment_dropped`).
  - Failure (la solicitud nunca retorna ALLOW): **Given** la misma baja, **When** se repite la solicitud 3 veces, **Then** las 3 respuestas son 403 `SUBJECT_ENROLLMENT_DROPPED` y ninguna es 200. `T-CON-01` cubre la invariante concurrente; la repetición literal x3 queda en `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` (G-3).
  - Aislamiento: **Given** la misma baja, **When** `STU-98432` llama `/authorize` con header `CS101` y `resource_arn = urn:uai:subject:CS101:model:toy-cpu-demo`, **Then** la respuesta es 200 ALLOW (CS101 no cambia; ver E2-S1 y E4-S1). `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` (G-3).
  - Evento: **Given** cada DENY anterior, **Then** se registra un evento de intento denegado en `audit_ledger` (contracts §1 Q-fail: un DENY de política sí se registra). `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` (G-3).
  - Propagación: **Given** la baja con `revocation_propagated_at = T0`, **When** la primera denegación ocurre en T1, **Then** T1 - T0 < 200 ms (umbral gate NFR-REVOC-03, invalidación local; el < 500 ms de la prueba E2E de PRD §4.3 l.193 es objetivo funcional más laxo y queda cubierto; ver «Umbrales triageados») [ACTUALIZADO 2026-10-14, K-20]. `SIN NODE ID` (gap G-1: medición E2E PLANNED).
- **Depende de:** E2-S1, E1-S2.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; banner E-02 consume `code` del DenyBody sin mensajes genéricos.

### Story E2-S3: Repetir la baja no duplica efectos y un fallo del almacén cierra el acceso

- **Protagonista:** Dr. Marcus Vance (recibe un recibo estable ante repeticiones o doble clic)
- **Como** Dr. Marcus Vance, **quiero** que repetir una baja devuelva el mismo recibo, que una baja concurrente no duplique eventos, y que un fallo del almacén deje el acceso cerrado, **para** operar sin miedo a reintentos y sin estados a medias.
- **Requisito fuente:** FR-REVOC-03 (reglas 2 y 3; trazabilidad), NFR-REVOC-03 (PLANNED), PRD §7.3 (fail-closed: `AUTH_INTERNAL_POLICY_UNAVAILABLE`, 503).
- **Escenario UX + estados:** SC-03 (estado `[REVOKED]` en la tabla). Success: 200 `ALREADY_REVOKED` como recibo idempotente. Error: 503 reintentable. Loading: botón inactivo durante la transacción.
- **Contrato:** `revokeCourseAccess` Repetición (contracts §2): tras validar sintaxis y resolver identidad y curso, si la membresía ya es `DROPPED`, 200 `{ status: "ALREADY_REVOKED", revocation_propagated_at: <original> }` sin mutación ni evento, con `ExplanationDTO` que cita AD-03 (`observed_prior_status`). Concurrencia: dos bajas simultáneas del mismo par bajo `BEGIN IMMEDIATE`; una confirma, la otra observa `DROPPED`. I3: fallo del store (o cola llena) -> 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE`, reintentable, sin commit parcial. Q4: `explanation` con `observed_credentials_revoked` (conteo).
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/enrollments/STU-98432/drop`. Salida 200 `RevokeResponse` con `status = ALREADY_REVOKED`. Salida 503 `ErrorBody` con `code = AUTH_INTERNAL_POLICY_UNAVAILABLE` (retryable).
- **Códigos de error:** 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` (reintentable). 200 `ALREADY_REVOKED` no es error.
- **Binding invariants:** AD-03, AD-04, AD-11, AD-12.
- **ATDD:**
  - T-REV-02 `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_replay_idempotent`
  - T-REV-07 `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_concurrent_double_drop_single_mutation`
  - T-REV-06 `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_store_failure_closed`
  - T-REV-12 (R12-B01, SEC B-01: `Clock` lanza -> 503 fail-closed, AD-03/AD-12) `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_clock_failure_503_fail_closed_no_mutation`
  - T-REV-08 `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_already_revoked_cites_ad03`
  - T-REV-08b `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_first_revoke_reports_credentials_revoked`
- **Criterios de aceptación:**
  - Happy repetición: **Given** `STU-98432` ya `DROPPED` en CS-480 con `revocation_propagated_at = T0`, **When** llega una baja válida, **Then** la respuesta es 200 con `status = ALREADY_REVOKED`, `revocation_propagated_at = T0`, `explanation.rule_ids` que cita AD-03 y `observed_prior_status = "DROPPED"`, y el conteo de eventos `membership.revoked` no cambia (`test_revoke_replay_idempotent`, `test_explain_already_revoked_cites_ad03`).
  - Happy primera baja explicada: **Given** la baja inicial de la pareja CS-480 con 1 credencial, **Then** `explanation.observed_credentials_revoked = 1` (`test_explain_first_revoke_reports_credentials_revoked`).
  - Happy concurrencia: **Given** dos bajas simultáneas del mismo par, **When** ambas se procesan, **Then** exactamente 1 respuesta es `REVOKED`, la otra es `ALREADY_REVOKED`, y hay exactamente 1 evento `membership.revoked` (`test_revoke_concurrent_double_drop_single_mutation`).
  - Failure store: **Given** un fallo del store inyectado durante la transacción de la baja (cola en capacidad 0), **When** se llama el drop, **Then** la respuesta es 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` con `retryable = true`, `subject_memberships.status` sigue `ACTIVE`, las credenciales siguen `ACTIVE` y no hay eventos (`test_revoke_store_failure_closed`).
  - Failure busy: **Given** `busy_timeout = 5000` agotado antes de completar la operación requerida, **Then** 503 sin commit parcial. `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit` (G-2).
- **Depende de:** E2-S1.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; decision log actualizado.

### Story E2-S4: Solo un administrador puede dar de baja (403 ADMIN_ROLE_REQUIRED sin mutación)

- **Protagonista:** Dr. Marcus Vance (administrador que necesita que solo los administradores muten)
- **Como** Dr. Marcus Vance, **quiero** que una baja solicitada por un actor sin rol institucional `admin` se rechace sin tocar datos, **para** que el control de acceso no dependa de quien llame la API.
- **Requisito fuente:** FR-REVOC-03 (Disparador: API administrativa o webhook del sistema de registro); ADVF-01 (ACCEPT; fail-closed por defecto, contracts §2 P0); ADVF-02 (token Bearer opaco vía `TokenVerifierPort`).
- **Escenario UX + estados:** Denied sin banner de UX definido (`[ASSUMPTION]`: se muestra el `detail` de ErrorBody). Error: ErrorBody 403 sin ExplanationDTO. Success: no aplica. Loading: no aplica.
- **Contrato:** `revokeCourseAccess` P0 (`actor_role = admin` vía `TokenVerifierPort`; si no -> 403 `ADMIN_ROLE_REQUIRED`, sin ExplanationDTO, sin mutación ni evento). Orden único (contracts §1): 401 antes, 403 antes de la sintaxis.
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/enrollments/STU-98432/drop` con `Authorization: Bearer <STUDENT_TOKEN>` (actor con `actor_role = student`). Salida 403 `ErrorBody` `{ type, title, status: 403, detail: "Operation requires institutional role 'admin'.", instance, code: "ADMIN_ROLE_REQUIRED" }`.
- **Códigos de error:** 403 `ADMIN_ROLE_REQUIRED`; 401 `AUTH_TOKEN_INVALID` (RED: `test_revoke_auth_token_invalid_401_before_body_validation`, R9-00).
- **Binding invariants:** AD-03, AD-09. AD-02 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-REV-P-05 `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_non_admin_actor_403_no_mutation`
  - T-REV-09 (orden 403 antes de sintaxis) `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_student_token_403_admin_before_drop_reason_syntax`
  - T-REV-11 (401 bearer inválido, RED; R9-00) `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_auth_token_invalid_401_before_body_validation`
- **Criterios de aceptación:**
  - Failure principal: **Given** `STU-98432` ACTIVE en CS-480 con 1 credencial ACTIVE y un token `STUDENT_TOKEN`, **When** llama el drop de `STU-98432` en CS-480 con una `drop_reason` válida, **Then** la respuesta es 403 con `code = ADMIN_ROLE_REQUIRED`, sin campo `explanation`, la membresía sigue `ACTIVE`, la credencial sigue `ACTIVE`, y cero eventos en `audit_ledger` (`test_revoke_non_admin_actor_403_no_mutation`).
  - Orden: **Given** un token `STUDENT_TOKEN` con `drop_reason = ""` (sintaxis inválida), **When** se llama el drop, **Then** la respuesta es 403 `ADMIN_ROLE_REQUIRED` y no 400, porque el paso de rol va antes de la sintaxis (contracts §1 paso 1bis) (`test_revoke_student_token_403_admin_before_drop_reason_syntax`).
  - Bearer inválido (RED, R9-00): **Given** un bearer que el `TokenVerifierPort` no reconoce, **When** se llama el drop, **Then** la respuesta es 401 `AUTH_TOKEN_INVALID` sin tocar la base (`test_revoke_auth_token_invalid_401_before_body_validation`). El test es RED: el stub de `Module1Service._actor()` lanza `NotImplementedError` hasta que se implemente la verificación (AD-09). No es un guard verde: un fake configurado por el propio test daría una aserción tautológica.
  - Happy de referencia: **Given** `ADMIN_TOKEN` (Department Chair con `actor_role = admin`), **When** se llama el drop, **Then** la respuesta es 200 (cubierto en E2-S1).
- **Depende de:** E2-S1.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; sin secretos en logs.

### Story E2-S5: Una baja con datos inválidos, membresía suspendida o `drop_reason` con secreto se rechaza sin mutación

- **Protagonista:** Dr. Marcus Vance
- **Como** Dr. Marcus Vance, **quiero** que una solicitud de baja mal formada, fuera de tiempo o sobre una membresía suspendida se rechace con un código tipado, **para** corregir el dato sin dejar la base a medias y sin que un secreto quede en logs ni en la respuesta.
- **Requisito fuente:** FR-REVOC-03 (regla 1: estudiante con matrícula activa; entradas `drop_reason` y `timestamp`); NFR-SEC-04 (PLANNED); AD-06.
- **Escenario UX + estados:** Error: ErrorBody 400 y 409 (sin banner de UX definido, `[ASSUMPTION]`). Success: no aplica. Loading: no aplica.
- **Contrato:** `revokeCourseAccess` P2 (`SUSPENDED` -> `INVALID_TRANSITION` 409), P3 (`drop_reason` 1 a 280 puntos Unicode, sin caracteres de control `Cc`, blancos por `str.isspace()`, secreto `uai_live_` enmascarado), P4 (`timestamp` RFC 3339 UTC con la gramática G9-01/R4-01; > `request_now` + 300 s -> 400 `MALFORMED_DROP_TIMESTAMP`). Q-fail: cero filas mutadas y cero eventos. Precedencia (contracts §2 Orden): `MALFORMED_DROP_REASON` primero si ambos fallan; ambos en `rule_ids` (R3-02, H-23).
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/enrollments/STU-98432/drop`. Entrada `RevokeRequest` `{ drop_reason, timestamp }`. Salidas 400 `ErrorBody` (`MALFORMED_DROP_REASON`, `MALFORMED_DROP_TIMESTAMP`), 409 `ErrorBody` (`INVALID_TRANSITION`).
- **Códigos de error:** 400 `MALFORMED_DROP_REASON`; 400 `MALFORMED_DROP_TIMESTAMP`; 409 `INVALID_TRANSITION`.
- **Binding invariants:** AD-03, AD-06, AD-08, AD-09, AD-11.
- **ATDD:**
  - T-REV-03 `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_malformed_drop_reason_400_no_mutation`
  - T-REV-10 (Cc: NUL) `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[nul]`
  - T-REV-10 (Cc: salto de línea) `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[newline]`
  - T-REV-10 (Cc: DEL) `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[del]`
  - T-REV-P-06 `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_future_timestamp_400_no_mutation`
  - T-REV-I-06 `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_timestamp_at_tolerance_boundary_accepted`
  - T-REV-04b `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_suspended_membership_409_invalid_transition`
  - T-SEC-01 `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_no_secret_leak_in_drop_reason`
  - T-SEC-REV-01 `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear`
  - T-REV-F01 (F-01, AD-03/AD-09: membresía DROPPED con `drop_reason` inválido -> 400 `MALFORMED_DROP_REASON` antes del replay) `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[solo-espacios]` y `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[control-nul]`
- **Criterios de aceptación:**
  - Failure drop_reason: **Given** `drop_reason = "   "` (solo blancos) con `STU-98432` ACTIVE, **When** se llama el drop, **Then** la respuesta es 400 `MALFORMED_DROP_REASON` con detail `Drop reason must be 1-280 chars.` y la membresía sigue `ACTIVE` sin eventos (`test_revoke_malformed_drop_reason_400_no_mutation`). Caracteres `Cc` (ECF-12) cubiertos por T-REV-10. `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_281_chars_400_no_mutation` (G-10).
  - Failure timestamp futuro: **Given** `request_now = 2026-09-23T15:04:05.000000Z` y `timestamp = "2026-09-23T15:09:06.000000Z"` (+301 s), **When** se llama el drop, **Then** la respuesta es 400 `MALFORMED_DROP_TIMESTAMP` y no hay mutación (`test_revoke_future_timestamp_400_no_mutation`).
  - Frontera timestamp: **Given** `timestamp = "2026-09-23T15:09:05.000000Z"` (+300 s exactos), **When** se llama el drop, **Then** la solicitud se acepta y la baja procede (`test_revoke_timestamp_at_tolerance_boundary_accepted`).
  - Gramática del timestamp (G9-01): **Given** un timestamp con offset distinto de `Z`/`+00:00`, `-00:00`, más de 6 decimales, fecha sin hora o segundo 60, **Then** 400 `MALFORMED_DROP_TIMESTAMP`. `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-no-utc]`, `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-menos-cero]`, `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fraccion-7-digitos]`, `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[sin-hora]`, `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[segundo-60]` y `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fecha-inexistente]` (G-12).
  - Failure estado: **Given** `STU-98432` con membresía `SUSPENDED` en CS-480, **When** se llama el drop con datos válidos, **Then** la respuesta es 409 `INVALID_TRANSITION` con detail `Membership is 'SUSPENDED', revoke needs ACTIVE.` y no hay mutación (`test_revoke_suspended_membership_409_invalid_transition`).
  - Seguridad: **Given** `drop_reason` que contiene un token `uai_live_` completo, **When** se llama el drop, **Then** el valor persistido, el log y la respuesta contienen solo la máscara `uai_live_<4>••••<4>` (`test_no_secret_leak_in_drop_reason`, `test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear`). NFR-SEC-04: 0 matches de la regex `uai_live_[a-zA-Z0-9]{32}` en 10,000 líneas (PLANNED, gap G-16).
  - Precedencia: **Given** `drop_reason = ""` y `timestamp` ausente, **Then** `rule_ids` lista `MALFORMED_DROP_REASON` primero y `MALFORMED_DROP_TIMESTAMP` después (R3-02). `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_empty_reason_and_missing_timestamp_rule_ids_order` (G-11).
- **Depende de:** E2-S1, E2-S4.
- **DoD:** ATDD en verde al pasar a GREEN; regex de build de secretos en verde; `quality_gate.sh` verde.

---

## Epic 3: El Dr. Marcus Vance carga la nómina de CS-480 de forma atómica

Objetivo: una nómina se importa de forma atómica (todo o nada), no cambia roles existentes y se rechaza antes de tocar la base cuando el lote no es válido.

### Story E3-S1: Dr. Vance carga 120 alumnos de CS-480 en una operación atómica

- **Protagonista:** Dr. Marcus Vance
- **Como** Dr. Marcus Vance, **quiero** cargar la nómina de CS-480 de 120 alumnos en una sola operación, **para** que el semestre arranque sin vincular manualmente a cada estudiante.
- **Requisito fuente:** FR-INGEST-01 (salidas 201 y evento; entradas `subject_id`, `term`, `roster_payload`); NFR-PERF-02 (1,000 filas < 3.0 s; PLANNED); NFR-SEC-05 (hash SHA-256 + salt 16 bytes; PLANNED); R7-03 modificada por R8-01.
- **Escenario UX + estados:** SC-01. Loading: progreso de subida en cliente (bytes enviados / total) y botón inactivo con `Validando lote atómico...` hasta la respuesta 201 o 422 (UX-DR1; R10 M-1, sin progreso por fila). Success: banner con chips `[120 Procesados] [115 Creados] [5 Vinculados] [0 Errores]` (UX-DR4). Error: 400 `MALFORMED_TERM` (failure, ver criterios). Denied: no aplica.
- **Contrato:** `ingestRoster` (contracts §3). P1 (`subject_id` activo, `term` válido e igual al del curso, R7-02), P2 (1 a 1,000 filas de datos, UTF-8 sin BOM), P3 (dominio de email, `institutional_id` `^[A-Za-z0-9-]{1,64}$`, `assigned_role` en `{student, ta}`). Q1 (201 `{ processed, created_identities, updated_memberships, batch_id }`; `processed` = filas del lote aceptado; sin ExplanationDTO en el 201, R8-02). Q2 (todo o nada; `CredentialDeliveryPort.enqueue(identity_id, raw_key)` exactamente una vez por fila aceptada, R8-01; respuesta 201 sin `uai_live_`; solo se persiste el hash). Q3 (un evento `roster.ingested` con `decision = ALLOW`, `reasonCode = SUCCESS`).
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/roster?term=2026-FALL` con `multipart/form-data` (CSV con columnas exactas `institutional_id,email,full_name,assigned_role`) o JSON equivalente `RosterIngestRequest { subject_id: "CS-480", term: "2026-FALL", rows: [RosterRow] }`. Salida 201 `RosterIngestResponse { processed, created_identities, updated_memberships, batch_id }` (`dto.py`, R8-02).
- **Códigos de error:** 201 (éxito); 400 `MALFORMED_TERM` (failure); 400 `MALFORMED_BATCH`; 401 `AUTH_TOKEN_INVALID` (RED en E3-S4, T-ROS-20); 403 `ADMIN_ROLE_REQUIRED` (E3-S4); 404 `UNKNOWN_COURSE` (curso inexistente o inactivo); 413 `BATCH_TOO_LARGE`; 422 `ROSTER_VALIDATION_FAILED` (E3-S2); 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` (cola llena).
- **Binding invariants:** AD-02, AD-04, AD-06, AD-09, AD-11, AD-12.
- **ATDD:**
  - T-ROS-HP-01 `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_valid_batch_persists_all_rows`
  - T-ROS-HP-02 `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_emits_one_roster_ingested_event`
  - T-ROS-04 (R7-03 modificada por R8-01) `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response`
  - T-ROS-19 (reutiliza identidad existente) `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_reuses_existing_identity_without_duplicate`
  - T-ROS-17 (hash y salt, sin valor crudo) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored`
  - T-ROS-05 `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_malformed_term_400_no_mutation`
  - T-ROS-07 (404 curso inexistente, sin escrituras) `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inexistente]`
  - T-ROS-07 (404 curso inactivo, sin escrituras) `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inactiva]`
  - T-ROS-13 (503 cola llena) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_queue_full_503_no_mutation`
  - T-ROS-21 (R12-B01, SEC B-01: `IdGenerator` lanza -> 503 sin escrituras ni credenciales, AD-12/AD-02) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials`
  - T-ROS-H18a (H-18, AD-09: `term` percent-encoded decodificado una sola vez) `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_term_percent_encoded_decoded_once`
  - T-ROS-H18b (H-18, AD-09: `{subject_id}` del path inexistente -> 404 `UNKNOWN_COURSE`, sin escrituras) `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[inexistente]` y `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[minusculas]`
- **Criterios de aceptación:**
  - Happy: **Given** un admin token, el subject CS-480 activo con term `2026-FALL`, y un lote de 120 filas válidas: 115 identidades nuevas y 5 identidades existentes sin membresía en CS-480, **When** se envía el lote con `?term=2026-FALL`, **Then** la respuesta es 201 con `processed = 120`, `created_identities = 115`, `updated_memberships = 5`, `batch_id` con formato `roster-<8hex>-2026-FALL`, y sin campo `explanation` (`test_ingest_valid_batch_persists_all_rows`).
  - Happy persistencia: **Given** lo anterior, **Then** hay 120 membresías ACTIVE en CS-480 con term `2026-FALL`, 115 identidades nuevas insertadas, las 5 identidades existentes reutilizadas sin duplicarse (`test_ingest_reuses_existing_identity_without_duplicate`), y 120 credenciales emitidas (una por fila aceptada, R8-01), cada una con hash almacenado (salt de 16 bytes) y sin valor crudo en la base (`test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored`).
  - Happy credenciales (R8-01): **Given** lo anterior, **When** se ejecuta el lote, **Then** `CredentialDeliveryPort.enqueue` se llama exactamente 120 veces (una por fila aceptada, no por identidad creada) y el cuerpo 201 no contiene ninguna cadena `uai_live_` (`test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response`).
  - Happy evento: **Given** lo anterior, **Then** exactamente 1 evento `roster.ingested` con `decision = ALLOW` y `reason_code = SUCCESS` (`test_ingest_emits_one_roster_ingested_event`).
  - Failure term: **Given** el mismo lote con `?term=2026-SUMMER` (patrón válido, pero distinto del term vigente `2026-FALL` del curso), **When** se envía, **Then** la respuesta es 400 `MALFORMED_TERM` según contracts §3 P1 y ECF-06 (siempre 400 ante discrepancia de term), con cero escrituras y cero eventos (`test_ingest_malformed_term_400_no_mutation`).
  - Failure curso: **Given** un `subject_id` inexistente o inactivo, **Then** 404 `UNKNOWN_COURSE` sin escrituras (`test_ingest_unknown_or_inactive_subject_404_no_writes`).
  - Credencial por prefijo (ADVF-17, ECF-18): `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash` (G-13).
  - Failure cola: **Given** la cola de auditoría llena, **Then** 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` sin mutación (`test_ingest_queue_full_503_no_mutation`).
  - Rendimiento: **Given** un lote sintético de 1,000 filas, **Then** T < 3.0 s (NFR-PERF-02) y el E2E de 120 filas < 2.0 s (umbral gate de FR-INGEST-01; ver «Umbrales triageados»). `SIN NODE ID` (gap G-16: medición PLANNED).
- **Depende de:** E1-S1, E1-S3, E2-S4.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; sin `uai_live_` en logs (AD-06).

### Story E3-S2: Dr. Vance recibe el rechazo completo de un lote con correo externo en la fila 85 y el manifiesto de la fila

- **Protagonista:** Dr. Marcus Vance
- **Como** Dr. Marcus Vance, **quiero** que un lote con un correo externo se rechace completo y me indique la fila, el campo y la regla violada, **para** corregir el archivo y reintentar sin que queden registros parciales.
- **Requisito fuente:** FR-INGEST-01 (prueba de fallo: fila 85 con `@gmail.com` -> 422, rollback completo, 0 registros; regla 1 y regla 4); PRD §7.2 (colisión B: duplicado intra-lote); R9-01 (identidad suspendida o expulsada).
- **Escenario UX + estados:** Error Caso A de EXPERIENCE §2.3 (modal de error transaccional, UX-DR3). Encabezado `Error de Validación: Transacción Atómica Abortada (HTTP 422)`. Denied: no aplica. Success: no aplica.
- **Contrato:** `ingestRoster` P3 (email fuera de `universidad.edu` -> `ROSTER_VALIDATION_FAILED`), P4 (duplicados intra-lote -> `INTRA_BATCH_DUPLICATE_ID`), P3 (identidad preexistente `SUSPENDED`/`EXPELLED` -> fila `ROSTER_VALIDATION_FAILED` sobre `identity_status` con `rule_ids: ["ROSTER_VALIDATION_FAILED", "IDENTITY_BARRED"]`, R9-01), Q2 (todo o nada), Q3 (rollback y después evento `roster.rejected` en transacción separada; `processed = 0`, `created_identities = 0`, `updated_memberships = 0`; `roster.rejected` -> `decision = DENY`, `reasonCode` = código principal del manifiesto; 422 con `application/problem+json`), Q4 (`explanation` cita AD-02 con `observed_invalid_row`). Código principal del manifiesto (contracts §3, R9-01): `ROSTER_VALIDATION_FAILED` > `INTRA_BATCH_DUPLICATE_ID`; `IDENTITY_BARRED` es un `rule_id` dentro de la fila `ROSTER_VALIDATION_FAILED`, no un código HTTP del lote.
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/roster?term=2026-FALL`. Salida 422 `RosterRejectedManifest` `{ type, title, status: 422, detail, instance, code, errors: [RosterRejectedManifestRow], batch_id, explanation, processed: 0, created_identities: 0, updated_memberships: 0 }`, con `errors[]` `{ row_number, institutional_id, field, observed, expected }` (el 422 sí lleva `explanation`; solo el 201 no, R8-02).
- **Códigos de error:** 422 `ROSTER_VALIDATION_FAILED` (incluye la fila `identity_status` / `IDENTITY_BARRED`); 422 `INTRA_BATCH_DUPLICATE_ID`.
- **Binding invariants:** AD-02, AD-04, AD-11, AD-13 (captura única de `request_now`, H-16). AD-06 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-ROS-01 `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_row85_rollback`
  - T-ROS-H16 (H-16, AD-13: el `roster.rejected` reutiliza el `request_now` único como `occurredAt`) `test/atdd/module1_ingest_contracts.test.py::TestRequestTimeInRejection::test_roster_rejected_occurred_at_reuses_single_request_now`
  - T-ROS-11 (correo fuera de dominio) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[dominio-externo]`
  - T-ROS-12 (manifiesto con regla institucional, R8-09) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule`
  - T-ROS-08 `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_roster_rejected_cites_ad02_observed_row`
  - T-ROS-02 `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_roster_intra_batch_duplicate`
  - T-ROS-08b `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_intra_batch_duplicate_cites_ad02`
  - T-ROS-10 (correo repetido en el lote, ECF-08) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_duplicate_email_in_batch_422_no_writes`
  - T-ROS-14 (identidad SUSPENDED, R9-01) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[SUSPENDED]`
  - T-ROS-14 (identidad EXPELLED, R9-01) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[EXPELLED]`
  - T-SEC-ROS-01 (manifiesto sin secretos) `test/atdd/module1_ingest_rules_contracts.test.py::TestSecrets::test_ingest_secret_in_batch_field_never_in_manifest_or_logs`
- **Criterios de aceptación:**
  - Failure fila 85 (principal): **Given** un lote de 120 filas con la fila 85 `email = "mateo.personal@gmail.com"` y las demás válidas, y la base con 0 registros del lote, **When** se envía el lote, **Then** la respuesta es 422 `application/problem+json` con `code = ROSTER_VALIDATION_FAILED`, `processed = 0`, `errors` con una sola entrada `{ row_number: 85, field: "email", observed: "mateo.personal@gmail.com", expected: "@universidad.edu" }`, y la base queda con 0 filas creadas en `identities`, `subject_memberships` y `subject_credentials` (`test_roster_row85_rollback`, `test_ingest_invalid_email_422_roster_validation_no_writes[dominio-externo]`).
  - Failure evento: **Given** lo anterior, **Then** hay exactamente 1 evento `roster.rejected` con `decision = DENY` y `reason_code = ROSTER_VALIDATION_FAILED`, y `explanation.rule_ids` cita AD-02 con `observed_invalid_row = 85` (`test_explain_roster_rejected_cites_ad02_observed_row`).
  - Failure identidad barred (R9-01): **Given** un `institutional_id` preexistente con `SUSPENDED` o `EXPELLED`, **When** el lote lo incluye, **Then** 422 `ROSTER_VALIDATION_FAILED` con fila `field = identity_status`, `rule_ids = ["ROSTER_VALIDATION_FAILED", "IDENTITY_BARRED"]`, cero escrituras y un `roster.rejected` (`test_ingest_barred_identity_rejects_whole_batch_422`). `403 IDENTITY_BARRED` aplica solo a `/authorize` (G-4, cerrado en E4-S3).
  - Failure duplicado: **Given** un lote con `STU-98432` en las filas 12 y 45, **When** se envía, **Then** la respuesta es 422 con `code = INTRA_BATCH_DUPLICATE_ID` y detail `ID 'STU-98432' repeats in batch (rows 12, 45).`, cero escrituras y explicación citando AD-02 (`test_roster_intra_batch_duplicate`, `test_explain_intra_batch_duplicate_cites_ad02`).
  - Failure correo duplicado: **Given** dos filas con el mismo email, **Then** 422 `ROSTER_VALIDATION_FAILED` detectado en memoria antes de la base (ECF-08) (`test_ingest_duplicate_email_in_batch_422_no_writes`).
  - Failure correo mapeado a UX (R8-09): **Given** un email fuera de dominio, **Then** `rule_ids` incluye `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL` para el banner UX sin código HTTP nuevo (`test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule`).
  - Manifiesto sin secretos: **Given** un campo del lote con `uai_live_` completo, **Then** el manifiesto 422 y los logs no lo contienen (`test_ingest_secret_in_batch_field_never_in_manifest_or_logs`).
  - Happy de referencia: **Given** el mismo lote con la fila 85 corregida, **Then** la respuesta es 201 (cubierto en E3-S1).
- **Depende de:** E3-S1.
- **DoD:** ATDD en verde al pasar a GREEN; el manifiesto no contiene secretos; `quality_gate.sh` verde.

### Story E3-S3: Dr. Vance no puede cambiar el rol de quien ya está en CS-480 por una nómina

- **Protagonista:** Dr. Marcus Vance
- **Como** Dr. Marcus Vance, **quiero** que una nómina nunca eleve ni reduzca el rol de un estudiante ya matriculado, **para** que solo el workflow formal de escalación cambie privilegios.
- **Requisito fuente:** FR-INGEST-01 (regla 3: no duplica identidad; asocia el vínculo `(student_id, subject_id, role, term)`); FR-ESCAL-02 (la elevación solo por el workflow formal); PRD §7.2 (colisiones de identidad); AD-02 (anti-role-smuggling).
- **Escenario UX + estados:** Error 422 `ROSTER_VALIDATION_FAILED` sobre `assigned_role`. Sin banner de UX definido (`[ASSUMPTION]`). Success: no aplica. Denied: no aplica.
- **Contrato:** `ingestRoster` anti-role-smuggling (contracts §3, H-20; ADVF-14; ADVF-15 y ECF-23 para `SUSPENDED` y `COMPLETED` sin reactivar; ADVF-19 y ECF-09 para conflicto de identidad por fila). I2 (ningún rol preexistente cambia por importación). R7-02: el `term` del lote debe ser igual al `term` vigente del curso (ADVF-12 -> `MALFORMED_TERM`); membresías de otros terms existen por histórico y el índice parcial ACTIVE se prueba a nivel DDL (`idx_single_active_membership`).
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/roster?term=2026-FALL`. Salida 422 `RosterRejectedManifest` con `errors[0] = { row_number, institutional_id: "STU-98432", field: "assigned_role", observed: "ta", expected: "student" }`.
- **Códigos de error:** 422 `ROSTER_VALIDATION_FAILED` (campo `assigned_role` o conflicto por fila).
- **Binding invariants:** AD-02, AD-11. AD-04, AD-05 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-ROS-03 `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_no_role_smuggling`
  - T-ROS-03b `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_role_smuggling_422_field_assigned_role`
  - T-ROS-16 (estado previo DROPPED) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED]`
  - T-ROS-16 (estado previo SUSPENDED) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[SUSPENDED]`
  - T-ROS-16 (estado previo COMPLETED) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[COMPLETED]`
  - T-ROS-15 (conflicto de identidad por fila) `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_conflicting_identity_row_422_no_identity_update`
  - T-MEM-GUARD-01 (guarda de term, R7-02) `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_membership_per_pair_across_terms` (guarda, verde)
- **Criterios de aceptación:**
  - Failure anti-smuggling: **Given** `STU-98432` con membresía `student` ACTIVE en CS-480 term `2026-FALL`, **When** una nómina con `assigned_role = ta` para el mismo `institutional_id` llega con `?term=2026-FALL`, **Then** la respuesta es 422 `ROSTER_VALIDATION_FAILED` con `field = assigned_role`, `observed = "ta"`, `expected = "student"`, la membresía sigue `student` y no hay cambios en tablas de negocio (`test_roster_role_smuggling_422_field_assigned_role`, `test_roster_no_role_smuggling`).
  - Estado previo: **Given** `STU-98432` con membresía `DROPPED` (o `SUSPENDED` o `COMPLETED`) con rol `student` en CS-480 term `2026-FALL`, **When** llega la misma fila con `assigned_role = student`, **Then** la membresía no se reactiva, la fila no cuenta como `updated_memberships`, y el estado se conserva (parametrizado por estado: `[DROPPED]`, `[SUSPENDED]`, `[COMPLETED]`) (ADVF-15, ECF-23).
  - Conflicto de identidad: **Given** un `institutional_id` que ya pertenece a otra identidad con otro email, **Then** la fila produce `ROSTER_VALIDATION_FAILED` sobre el campo en conflicto, sin actualizar la identidad (ADVF-19, ECF-09) (`test_ingest_conflicting_identity_row_422_no_identity_update`).
  - Guarda de term (R7-02): **Given** una membresía ACTIVE de `(identity, CS-480, 2026-FALL)`, **When** se inserta una segunda ACTIVE del mismo par con term `2026-SPRING`, **Then** la base rechaza la inserción por UNIQUE (`test_guard_single_active_membership_per_pair_across_terms`). Membresías DROPPED de otro term sí coexisten.
  - Term distinto (R7-02): **Given** un lote con `term` distinto al vigente del curso, **Then** 400 `MALFORMED_TERM` (cubierto en E3-S1).
- **Depende de:** E3-S1, E3-S2.
- **DoD:** ATDD en verde al pasar a GREEN; guarda en verde; `quality_gate.sh` verde.

### Story E3-S4: Dr. Vance recibe rechazos de límites, de sintaxis HTTP y de permisos antes de que se toque la base

- **Protagonista:** Dr. Marcus Vance
- **Como** Dr. Marcus Vance, **quiero** que un lote vacío, demasiado grande, mal formado o enviado por un usuario sin rol admin se rechace antes de validar filas, **para** tener errores claros y reintentar un lote válido sin efectos colaterales.
- **Requisito fuente:** FR-INGEST-01 (entradas y límites; disparador administrativo); contracts §3 P2 (1 a 1,000 filas; 5,000,000 bytes); ADVF-01; ADVF-11; ECF-05, ECF-19 a ECF-22.
- **Escenario UX + estados:** Error: ErrorBody 400 y 413 (UX-DR3 para el mensaje). Denied: 403 `ADMIN_ROLE_REQUIRED` sin banner de UX definido (`[ASSUMPTION]`). Success: el lote de 1,000 filas aceptado en el límite produce Success (UX-DR4).
- **Contrato:** `ingestRoster` P0 (403 `ADMIN_ROLE_REQUIRED` antes de la sintaxis; 401 antes que todo), P2 (`BATCH_TOO_LARGE` 413 antes de parsear; `BATCH_EMPTY` 400 antes de validar filas; `MALFORMED_BATCH`), precedencia de sintaxis (G9-02): `BATCH_TOO_LARGE` > `MALFORMED_TERM` > `MALFORMED_BATCH` > `BATCH_EMPTY`. P3: `institutional_id` `^[A-Za-z0-9-]{1,64}$` sensible a mayúsculas (ADVF-21); dominio de email case-insensitive (ECF-07); `email` vacío -> `ROSTER_VALIDATION_FAILED` sobre `email` (ECF-17). Reingesta (contracts §3 Nota): cada solicitud válida es un intento nuevo con `batch_id` nuevo.
- **Endpoint + DTOs:** `POST /api/v1/subjects/CS-480/roster`. Salidas: 400 `ErrorBody` (`BATCH_EMPTY`), 413 `ErrorBody` (`BATCH_TOO_LARGE`), 403 `ErrorBody` (`ADMIN_ROLE_REQUIRED`), 201 `RosterIngestResponse` (límite de 1,000 filas, reingesta).
- **Códigos de error:** 400 `BATCH_EMPTY`; 413 `BATCH_TOO_LARGE`; 403 `ADMIN_ROLE_REQUIRED`; 401 `AUTH_TOKEN_INVALID` (RED, R9-00); 400 `MALFORMED_BATCH` (BOM, Content-Type, partes multipart, eco de `subject_id`).
- **Binding invariants:** AD-02, AD-06, AD-09.
- **ATDD:**
  - T-ROS-06 `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_empty_batch_400_no_mutation`
  - T-ROS-06b `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_1001_rows_413_too_large_no_mutation`
  - T-ROS-P-05 `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_non_admin_actor_403_no_mutation`
  - T-ROS-09 (403 antes de sintaxis) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_student_token_403_admin_before_batch_syntax`
  - T-ROS-20 (401 bearer inválido, RED; R9-00) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_auth_token_invalid_401_before_batch_validation`
  - T-ROS-I-04 `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_1000_rows_boundary_accepted`
  - T-ROS-I-05 `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_reingest_creates_new_batch_id`
  - T-ROS-18 (dominio case-insensitive, ECF-07) `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_email_domain_case_insensitive_local_part_preserved`
  - T-ROS-11 (email vacío, ECF-17) `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[vacio]`
  - T-HTTP-02 (BOM -> MALFORMED_BATCH, ECF-19) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_roster_body_with_utf8_bom_400_malformed_batch`
  - T-HTTP-03 (CSV RFC 4180, 4 campos, ECF-20) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_rfc4180_parses_quoted_comma_and_escaped_quote_in_four_fields`
  - T-HTTP-04 (5 campos, ECF-20) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_row_with_five_fields_400_malformed_batch`
  - T-HTTP-05 (Content-Type no soportado, ECF-21) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_unsupported_content_type_400_malformed_batch`
  - T-HTTP-06 (multipart 0 partes, ECF-22) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[sin-partes]`
  - T-HTTP-06 (multipart 2 partes, ECF-22) `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[dos-partes]`
- **Criterios de aceptación:**
  - Failure vacío: **Given** un JSON con `rows: []` o un CSV con solo encabezado, **When** se envía, **Then** la respuesta es 400 `BATCH_EMPTY` con detail `Batch contains zero rows.`, sin `batch_id` y sin mutación (`test_ingest_empty_batch_400_no_mutation`).
  - Failure tamaño: **Given** un lote de 1,001 filas, **When** se envía, **Then** la respuesta es 413 `BATCH_TOO_LARGE` antes de validar filas, sin `batch_id` y sin mutación (`test_ingest_1001_rows_413_too_large_no_mutation`).
  - Failure admin: **Given** un token `STUDENT_TOKEN` y un lote válido de 120 filas, **When** se envía, **Then** la respuesta es 403 `ADMIN_ROLE_REQUIRED` sin `explanation`, sin filas en `identities`, `subject_memberships`, `subject_credentials` ni `roster_batches`, y cero eventos (`test_ingest_non_admin_actor_403_no_mutation`). Orden: 403 antes de la sintaxis aunque el lote esté mal formado (`test_ingest_student_token_403_admin_before_batch_syntax`).
  - Bearer inválido (RED, R9-00): **Given** un bearer que el `TokenVerifierPort` no reconoce, **Then** 401 `AUTH_TOKEN_INVALID` antes de validar el lote (`test_ingest_auth_token_invalid_401_before_batch_validation`).
  - Sintaxis HTTP: **Given** BOM, CSV de 4 o 5 campos, `Content-Type` no soportado o 0/2 partes de archivo, **Then** 400 `MALFORMED_BATCH` sin mutación (T-HTTP-02..06). Eco de `subject_id` distinto o ausente (ECF-05): `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]` y `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]` (G-8).
  - Dominio de email: **Given** un email `ALUMNO@Universidad.EDU`, **Then** el dominio se compara sin distinguir mayúsculas y el resto del email se conserva (ECF-07) (`test_ingest_email_domain_case_insensitive_local_part_preserved`).
  - Patrón de `institutional_id`: `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity` (ADVF-21, G-9).
  - Happy límite: **Given** un lote de exactamente 1,000 filas válidas, **When** se envía, **Then** la respuesta es 201 con `processed = 1000` (`test_ingest_1000_rows_boundary_accepted`).
  - Happy reingesta: **Given** un lote ya aceptado, **When** se envía de nuevo el mismo contenido, **Then** la respuesta es 201 con un `batch_id` distinto del primero y los conteos se calculan con el estado actual (`test_ingest_reingest_creates_new_batch_id`).
- **Depende de:** E3-S1, E2-S4.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; sin secretos en logs.

---

## Epic 4: Sofia obtiene permisos independientes por curso y su escalación vence sin residuos

Objetivo: el Mandatory Edge Case EDGE-01 se resuelve con contextos independientes; la escalación temporal se respeta en el instante exacto de vencimiento; las solicitudes mal formadas se rechazan con código tipado.

### Story E4-S1: EDGE-01 - Sofia, estudiante en CS101 (0 GPU) y TA en CS-480, se resuelve por contexto

- **Protagonista:** Sofia (TA de CS-480; estudiante en CS101; `TA-SOFIA-01`)
- **Como** Sofia, **quiero** que mi rol de TA en CS-480 no sume privilegios a mi cuenta de estudiante en CS101, **para** que cada contexto se resuelva por separado y cada decisión me explique por qué.
- **Requisito fuente:** Mandatory Edge Case EDGE-01 (Annex A p.13: "Student in CS101 (0 GPU) and TA in CS-480 (high priority) -> each context resolves independently"); PRD §5.1 y §5.2 (reglas 1 a 3); NFR-PERF-01 (PLANNED).
- **Escenario UX + estados:** EDGE-01 (selector de contexto, matriz comparada, banner Confused Deputy). Success: ALLOW en CS-480 con `effective_role = ta`. Denied: DENY `UNAUTHORIZED_RESOURCE_CLASS` en CS101 para GPU (banner no definido en EXPERIENCE: `[ASSUMPTION]`). Loading: overlay de evaluación.
- **Contrato:** `resolveEffectivePermissions` Q1 y Q2 (EDGE-01 con matriz v0: CS101 student GPU = DENY; CS-480 ta inference = ALLOW), I1 (el rol de otro curso no altera el veredicto), I4 (la respuesta solo lleva `decision`, `effective_role`, `explanation`; sin cuota ni prioridad), P4b, paso 7 (`resource_class` vía `resource_catalog`, R6b-01). Claves ejecutables de la matriz (ADVF-07): `{subject_id, role, action, resource_class, allow}`. Fila `ta` en CS-480 explícita (ADVF-06, ECF-25).
- **Endpoint + DTOs:** `POST /api/v1/authorize` con header de contexto y `AuthorizeRequest`. Tres casos:
  - (a) header `CS101`, `resource_arn = urn:uai:subject:CS101:model:toy-cpu-demo`, `action = inference` -> 200 `AuthorizeResponse` ALLOW con `effective_role = student`.
  - (b) header `CS101`, `resource_arn = urn:uai:subject:CS101:model:llama-3-8b-instruct`, `action = inference` -> 403 `DenyBody` con `code = UNAUTHORIZED_RESOURCE_CLASS`.
  - (c) header `CS-480`, `resource_arn = urn:uai:subject:CS-480:model:llama-3-8b-instruct`, `action = inference` -> 200 `AuthorizeResponse` ALLOW con `effective_role = ta`.
- **Códigos de error:** 403 `UNAUTHORIZED_RESOURCE_CLASS`; 401 `AUTH_TOKEN_INVALID` (RED, R9-00); 404 `UNKNOWN_IDENTITY`.
- **Binding invariants:** AD-01, AD-10, AD-11. AD-09 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-RES-01 `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation`
  - T-RES-01b `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_student_cs101_gpu_denied_cs480_allowed`
  - T-RES-HP-03 `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_cpu_toy_model_cs101`
  - T-RES-09 (H-26, AD-10: `effective_role` es el id exacto de `roles.id`, TA en CS-480 = `ta`) `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_effective_role_is_exact_roles_id`
  - T-RES-12 (401 bearer inválido, RED; R9-00) `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_auth_token_invalid_401_before_arn_validation`
- **Criterios de aceptación:**
  - Happy CS101 CPU: **Given** `edge_case_seeds` (`TA-SOFIA-01` Student ACTIVE en CS101 y TA ACTIVE en CS-480, término `2026-FALL`), **When** se llama el caso (a), **Then** la respuesta es 200 ALLOW con `effective_role = student` (`test_resolve_allows_cpu_toy_model_cs101`).
  - Failure CS101 GPU (EDGE-01 principal): **Given** el mismo seed, **When** se llama el caso (b), **Then** la respuesta es 403 `DenyBody` con `code = UNAUTHORIZED_RESOURCE_CLASS`, `detail = "Role 'student' cannot 'inference' on 'urn:uai:subject:CS101:model:llama-3-8b-instruct'."`, `explanation.rule_ids` no vacío, y se registra el intento denegado (`test_edge01_student_cs101_gpu_denied_cs480_allowed`).
  - Happy CS-480 TA (EDGE-01): **Given** el mismo seed, **When** se llama el caso (c), **Then** la respuesta es 200 ALLOW con `effective_role = ta`, y el veredicto de CS101 sobre GPU no cambió (`test_edge01_context_isolation`).
  - Bearer inválido (RED, R9-00): **Given** un bearer no reconocido, **Then** 401 `AUTH_TOKEN_INVALID` antes de validar el ARN (`test_resolve_auth_token_invalid_401_before_arn_validation`).
  - No-cuota (I4): **Given** cualquier respuesta de los casos (a) a (c), **Then** el JSON contiene únicamente `decision`, `effective_role` y `explanation`; no contiene campos de cuota GPU ni prioridad de scheduling (AD-10, PRD [ASSUMPTION-01]). `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_deny_response_has_no_quota_or_priority_fields` (G-17).
- **Depende de:** E1-S1, E1-S2.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; decision log actualizado con la matriz v0 citada.

### Story E4-S2: Sofia - su escalación temporal vence en el instante exacto y no altera CS101

- **Protagonista:** Sofia (TA de CS-480 con escalación temporal)
- **Como** Sofia, **quiero** que mi rol elevado en CS-480 venza exactamente al término de la ventana concedida y que mi cuenta de CS101 no cambie mientras tanto, **para** que los privilegios de entrenamiento no sobrevivan a su ventana.
- **Requisito fuente:** FR-ESCAL-02 (alcance contratado: honrar ticket ACTIVE o vencido en resolve; reglas 5 y 6; prueba unitaria de expiración); PRD §7.1 (Vector 2: el `exp` del token impide operar tras vencer); AD-13.
- **Escenario UX + estados:** Denied: banner E-03 (`Ventana de Escalación Expirada: Rol Restablecido a Base`, `STATUS_ESCALATION_EXPIRED (HTTP 403)`, UX-DR7). Success: ALLOW con `effective_role = instructor_privileged` dentro de la ventana. Loading: no aplica.
- **Contrato:** `resolveEffectivePermissions` Q1 (ticket ACTIVE con `granted_at <= at < expires_at` aplica; en replay, `REVOKED` aplica solo en `[granted_at, min(expires_at, revoked_at))`), I2 (`at >= expires_at` es expirado), Q4 (`threshold` con `expires_at`), Q-tiempo (un `granted_at` futuro aún no aplica: se usa el rol base). Scheduler (contracts §1 Tiempo): barrido cada 1 s que pasa el ticket a EXPIRED, con evento por transición y telemetría de barrido diferido (R8-06); la respuesta de resolve no depende del barrido. La operación de dominio recibe `at` como entrada interna; el endpoint público usa `request_now`.
- **Endpoint + DTOs:** entrada interna `ResolveEffectivePermissionsCall { user_id: "TA-SOFIA-01", course_id: "CS-480", resource_arn: "urn:uai:subject:CS-480:model:train-queue", action: "training", at }`. Caso ALLOW: 200 `AuthorizeResponse` con `effective_role = "instructor_privileged"`. Caso DENY: 403 `DenyBody` con `code = STATUS_ESCALATION_EXPIRED` y `explanation.threshold = "expires_at=<valor>"`.
- **Códigos de error:** 403 `STATUS_ESCALATION_EXPIRED`; 403 `UNAUTHORIZED_RESOURCE_CLASS` (si el rol base no autoriza y no hay ticket vencido).
- **Binding invariants:** AD-05 (ticket del par; lectura en resolve), AD-10, AD-11, AD-13. AD-01, AD-12 (K-6: citados por tests de esta historia).
- **ATDD:**
  - T-RES-04 `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_escalation_boundary_expires`
  - T-RES-I-03 `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_before_granted_uses_base_role`
  - T-RES-08b `test/atdd/module1_resolve_contracts.test.py::TestExplainability::test_explain_deny_expired_threshold_reports_expires_at`
  - T-RES-01c `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_escalation_in_cs480_does_not_alter_cs101`
  - T-SCH-01 `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_expires_active_ticket_once_with_one_event`
  - T-SCH-02 `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_does_not_expire_ticket_not_yet_granted`
  - T-SCH-03 `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_crash_recovery_reconciles_all_expired_tickets`
  - T-SCH-04 (telemetría del barrido diferido, R8-06) `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric`
  - T-ESC-GUARD-02 (formato fijo de `escalation_tickets`, ECF-15) `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_timestamp_fixed_format_check` (guarda, verde)
  - T-ESC-GUARD-01 (una sola solicitud activa por par, AD-05) `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_escalation_per_pair` (guarda, verde)
  - T-ESC-GUARD-03 (aprobador distinto del solicitante, AD-05, R9-02) `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_self_approval_rejected` (guarda, verde)
  - T-ESC-GUARD-04 (H-21c, AD-13: `CHECK (expires_at > granted_at)` en tickets ACTIVE) `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_expires_after_granted_check`
- **Criterios de aceptación:**
  - Happy dentro de la ventana: **Given** el ticket `ESC-2026-480-01` ACTIVE para (`TA-SOFIA-01`, CS-480) con `granted_at = 2026-09-23T15:04:05.000000Z` y `expires_at = 2026-09-23T19:04:05.000000Z` (4 horas), **When** `at = 2026-09-23T19:04:04.999999Z` y se pide `training` sobre `train-queue`, **Then** la respuesta es 200 ALLOW con `effective_role = instructor_privileged`.
  - Failure frontera: **Given** el mismo ticket, **When** `at = 2026-09-23T19:04:05.000000Z` (igual a `expires_at`), **Then** la respuesta es 403 `STATUS_ESCALATION_EXPIRED` con `threshold = "expires_at=2026-09-23T19:04:05.000000Z"` y el rol base `ta` no autoriza `training` (`test_escalation_boundary_expires`, `test_explain_deny_expired_threshold_reports_expires_at`).
  - Antes de la concesión: **Given** el mismo ticket, **When** `at = 2026-09-23T15:04:04.999999Z` (antes de `granted_at`), **Then** se usa el rol base `ta` y la solicitud de `training` es DENY `UNAUTHORIZED_RESOURCE_CLASS` (`test_resolve_before_granted_uses_base_role`).
  - Aislamiento: **Given** el ticket de CS-480 vigente y el seed EDGE-01, **When** se consulta CS101 con `resource_arn = urn:uai:subject:CS101:model:toy-cpu-demo`, **Then** el veredicto de CS101 es el mismo que sin escalación (`test_edge01_escalation_in_cs480_does_not_alter_cs101`).
  - Sin residuos: **Given** un ticket con `expires_at` vencido y el scheduler aún sin barrer, **When** se resuelve con `at >= expires_at`, **Then** la respuesta es DENY (resolve no depende del barrido de 1 s; contracts §1 Tiempo) (`test_escalation_boundary_expires`); caso de barrido: `test_sweep_expires_active_ticket_once_with_one_event`.
  - Barrido diferido (R8-06): **Given** la cola llena en el barrido, **Then** log WARN estructurado y métrica `scheduler_sweep_deferred_total` vía `TelemetryPort`; reintento en el siguiente barrido (`test_sweep_defers_when_queue_full_and_emits_deferred_metric`).
- **Depende de:** E4-S1, E1-S2.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde; el barrido y la reconciliación tras crash quedan cubiertos por T-SCH-01..04.

### Story E4-S3: Sofia intenta usar un recurso de otro contexto y recibe un DENY explicado y gramática ARN estricta

- **Protagonista:** Sofia
- **Como** Sofia, **quiero** que una petición que mezcla un recurso de una asignatura con el contexto de otra sea rechazada con la regla citada, **para** entender que mis privilegios de TA no se transfieren entre asignaturas.
- **Requisito fuente:** PRD §5.2 (regla 2: Resource-Subject Binding, Confused Deputy); AD-01 (regex estricta de ARN y comparación byte a byte); PRD §4.3 (regla de contexto); R9-03.
- **Escenario UX + estados:** Banner E-01 (Denied): `Conflicto de Asignatura: Recurso no Perteneciente al Contexto Declarado`, código `RESOURCE_SUBJECT_MISMATCH (HTTP 403)` (UX-DR5). Error: 400 `MALFORMED_RESOURCE_ARN` con mensaje de gramática. Success: no aplica.
- **Contrato:** `resolveEffectivePermissions` P4 (`^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$`; `.` y `/` rechazados -> `MALFORMED_RESOURCE_ARN` 400), P2 (curso del header debe existir byte a byte: `cs-480` no existe -> 404 `UNKNOWN_COURSE`, R9-03), P5 (`resource.subject == courseId` byte a byte; sin `strip`, `upper` ni normalización -> `RESOURCE_SUBJECT_MISMATCH` 403; ADVF-10), Orden paso 5 (precedencia `IDENTITY_BARRED` > `RESOURCE_SUBJECT_MISMATCH` > membresía no activa), Q4 (explicación con `observed_resource_subject`).
- **Endpoint + DTOs:** `POST /api/v1/authorize`. Casos:
  - (a) header `CS-480`, `resource_arn = urn:uai:subject:CS-480/../model:llama-3-8b-instruct` -> 400 `ErrorBody` `MALFORMED_RESOURCE_ARN`.
  - (b) header `CS101` (existente), `resource_arn = urn:uai:subject:CS-480:model:llama-3-8b-instruct` -> 403 `DenyBody` `RESOURCE_SUBJECT_MISMATCH`, con `explanation.observed_resource_subject = "CS-480"` (R9-03).
  - (c) header `cs-480` (minúsculas, no existe byte a byte), `resource_arn = urn:uai:subject:CS-480:model:llama-3-8b-instruct` -> 404 `UNKNOWN_COURSE` por el orden de pasos (R9-03; el mismatch no se evalúa).
- **Códigos de error:** 400 `MALFORMED_RESOURCE_ARN`; 403 `RESOURCE_SUBJECT_MISMATCH`; 403 `IDENTITY_BARRED` (solo `/authorize`; G-4 con node ID abajo); 404 `UNKNOWN_COURSE` (caso c).
- **Binding invariants:** AD-01, AD-11.
- **ATDD:**
  - T-RES-02 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_arn_grammar_rejects`
  - T-RES-10 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_resource_subject_mismatch_403_explained_no_mutation` (orientación inversa: header `CS-480`, ARN `CS101`; misma regla P5; G-5 con `test_resolve_header_cs101_arn_cs480_mismatch_403`)
  - T-RES-08 `test/atdd/module1_contracts.test.py::TestExplainability::test_explain_assert_rule_cited`
- **Criterios de aceptación:**
  - Failure gramática: **Given** un ARN con `/` o `..` en el segmento de subject, **When** se llama `/authorize`, **Then** la respuesta es 400 `MALFORMED_RESOURCE_ARN` sin mutación ni evento (`test_arn_grammar_rejects`).
  - Failure mismatch: **Given** header `CS101` y ARN de `CS-480` (ambos cursos existentes), **When** se llama `/authorize`, **Then** la respuesta es 403 `RESOURCE_SUBJECT_MISMATCH`, con `explanation.rule_ids` que cita AD-01 y `observed_resource_subject = "CS-480"`; exactamente un evento DENY (R9-03). El test T-RES-10 cubre la misma regla con la orientación inversa (header `CS-480`, ARN `CS101`, `observed_resource_subject = "CS101"`). `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_header_cs101_arn_cs480_mismatch_403` (G-5).
  - Mayúsculas (ADVF-10): **Given** header `cs-480` y ARN `CS-480`, **Then** la respuesta es 404 `UNKNOWN_COURSE` (R9-03): la comparación no normaliza mayúsculas y el paso de curso precede al de mismatch. `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_lowercase_course_header_404_unknown_course` (G-6).
  - Precedencia 403 (H-17): **Given** una identidad `SUSPENDED` o `EXPELLED` que pide un recurso de otro subject, **Then** 403 `IDENTITY_BARRED` (no `RESOURCE_SUBJECT_MISMATCH`). `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_precedes_subject_mismatch` (G-4); `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]` y `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]` (G-4).
  - Explicación: **Given** cualquier DENY de política, **Then** `explanation.rule_ids` no vacío, cita AD-n y `observed_*` solo de las reglas violadas (`test_explain_assert_rule_cited`).
- **Depende de:** E1-S2, E4-S1.
- **DoD:** ATDD en verde al pasar a GREEN; banner E-01 consume `code` del DenyBody.

### Story E4-S4: Sofia recibe un rechazo tipado y sin mutación cuando la solicitud de autorización está mal formada o no cumple la regla 4

- **Protagonista:** Sofia
- **Como** Sofia, **quiero** que una solicitud con acción fuera del vocabulario, con tiempo inválido, con un modelo que no está en el catálogo o con una identidad no activa en la materia se rechace con un código claro, **para** corregir mi cliente sin que el sistema registre decisiones erróneas.
- **Requisito fuente:** PRD §5.2 (regla 4: mínimo privilegio por defecto, DENY por defecto); ADVF-07 y Q5 (vocabulario cerrado de `action`); ADVF-09 y ECF-14 (`at` obligatorio); ECF-24; AD-06 (secretos en la petición).
- **Escenario UX + estados:** Error: ErrorBody 400 (`MALFORMED_ACTION`, `INVALID_AT`). Denied: DENY `UNAUTHORIZED_RESOURCE_CLASS` para modelo fuera de catálogo (fail-closed). Success: no aplica.
- **Contrato:** `resolveEffectivePermissions` P3 (`at` con UTC ISO-8601 de 6 dígitos y zona; `null` o ausente -> `INVALID_AT` 400), P4b (`action` en `{inference, training}`; otro valor o vacío -> `MALFORMED_ACTION` 400), paso 7 (modelo ausente de `resource_catalog` -> `UNAUTHORIZED_RESOURCE_CLASS` 403), regla 4 (identidad no activa en la materia -> `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`), Q-fail (P1 a P4 sin mutación ni evento; DENY de política sí registra intento).
- **Endpoint + DTOs:** `POST /api/v1/authorize` con header `CS-480`. Casos:
  - (a) `action = "model:invoke"` -> 400 `MALFORMED_ACTION` con detail `Action 'model:invoke' must be 'inference' or 'training'.`.
  - (b) `action = ""` -> 400 `MALFORMED_ACTION`.
  - (c) `resource_arn = urn:uai:subject:CS-480:model:modelo-inexistente` -> 403 `DenyBody` `UNAUTHORIZED_RESOURCE_CLASS`.
  - (d) entrada interna con `at = null` -> 400 `INVALID_AT`.
- **Códigos de error:** 400 `MALFORMED_ACTION`; 400 `INVALID_AT`; 403 `UNAUTHORIZED_RESOURCE_CLASS`; 403 `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`.
- **Binding invariants:** AD-01, AD-06, AD-09, AD-10, AD-11, AD-13.
- **ATDD:**
  - T-RES-P-04 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_invalid_at_400_no_mutation`
  - T-RES-P-05 `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_malformed_action_400_no_mutation`
  - T-RES-I-04 `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_model_outside_catalog_denied`
  - T-RES-14 (secreto en `action` nunca en claro, AD-06) `test/atdd/module1_resolve_contracts.test.py::TestSecrets::test_resolve_secret_in_action_400_never_echoed_in_clear`
  - T-RES-H24 (H-24, AD-01/AD-09: `X-Academic-Subject-Context` repetido o vacío se trata como ausente -> `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`) `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-igual]`, `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-distinto]` y `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[vacio]`
- **Criterios de aceptación:**
  - Failure acción: **Given** `action = "model:invoke"`, **When** se llama `/authorize`, **Then** la respuesta es 400 `MALFORMED_ACTION`, sin mutación de tablas de negocio y sin evento (`test_resolve_malformed_action_400_no_mutation`).
  - Failure acción vacía: **Given** `action = ""`, **Then** 400 `MALFORMED_ACTION` (ECF-24) (`test_resolve_malformed_action_400_no_mutation`).
  - Secreto en la acción: **Given** una `action` con un token `uai_live_` completo, **Then** la respuesta de error y los logs no lo muestran en claro (`test_resolve_secret_in_action_400_never_echoed_in_clear`).
  - Failure tiempo: **Given** la entrada interna con `at = null`, **When** se llama la operación, **Then** la respuesta es 400 `INVALID_AT` con el detail de la plantilla de contracts §4 (`Request instant '{at}' is not RFC-3339 with zone and microseconds (body).`), sin mutación (`test_resolve_invalid_at_400_no_mutation`).
  - Failure modelo: **Given** `resource_arn` con un modelo fuera de `resource_catalog` (`modelo-inexistente`), **When** se llama `/authorize` con `action = inference`, **Then** la respuesta es 403 `UNAUTHORIZED_RESOURCE_CLASS` (fail-closed) y se registra el intento denegado (`test_resolve_model_outside_catalog_denied`).
  - Regla 4: **Given** un `STU-ONLY-CS101` sin membresía en CS-480, **Then** 403 `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (`test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`, también en E1-S2).
  - Happy de referencia: **Given** `action = inference` y modelo del catálogo, **Then** la solicitud sigue el flujo normal (E1-S2).
- **Depende de:** E4-S1, E1-S2.
- **DoD:** ATDD en verde al pasar a GREEN; `quality_gate.sh` verde.

---

## Umbrales triageados (R10: C-2 y M-5)

Regla: los AC de las historias citan solo el umbral gate (columna 3). Los objetivos no vinculantes (columna 4) se miden como stretch en `nfr-evidence.md` y no bloquean la historia.

| Requisito | Umbral gate vinculante (AC) | Objetivos no vinculantes | Fuente | Owner |
|---|---|---|---|---|
| FR-INGEST-01, lote de 120 filas (E2E funcional) | < 2.0 s | 1.2 s (UX SC-01; `ux/C-UX-Scenarios/scenario-1.md:83`), DEFER, medido como stretch | PRD FR-INGEST-01 (`planning/prd.md:141`); contracts §3 | B |
| NFR-PERF-02, lote de 1,000 filas | < 3.0 s | ninguno | PRD §6 | B (G-16) |
| NFR-AUDIT-06, consulta de 100,000 eventos (p95) | < 500 ms (p95) | 50k eventos < 200 ms (test FR-AUDIT-04); 200 ms (ARCHITECTURE y scenario-4) | PRD §6; `nfr-evidence.md` | B (G-16) |
| NFR-DISP-07, RAM y boot | RAM <= 512 MB; boot frío < 5.0 s | 2.0 s / 120 MB (ARCHITECTURE §1.1) | PRD §6; ARCHITECTURE §1.1 | B (G-16) |
| FR-REVOC-03 / NFR-REVOC-03 (revocación) | < 200 ms invalidación local (NFR-REVOC-03, prd.md:293); < 60 s en proxies perimetrales (fuera del módulo, SEC M-01 DEFER) | < 500 ms de la prueba E2E de PRD §4.3 (prd.md:193), más laxo que el gate | planning/prd.md:193, :293 | A (contrato) / B (medición PLANNED) |

## Lista de [ASSUMPTION] con owner (R10, menores)

| ID | Dónde | Supuesto | Owner |
|---|---|---|---|
| [ASSUMPTION] | E2-S4, E3-S4 | 403 `ADMIN_ROLE_REQUIRED` sin banner UX: se muestra el `detail` del ErrorBody | A |
| [ASSUMPTION] | E2-S5 | 400 `MALFORMED_DROP_*` y 409 `INVALID_TRANSITION` sin banner UX | A |
| [ASSUMPTION] | E3-S3 | 422 sobre `assigned_role` sin banner UX definido | A |
| [ASSUMPTION] | E4-S1 | DENY `UNAUTHORIZED_RESOURCE_CLASS` en CS101 para GPU sin banner en EXPERIENCE | A |
| [ASSUMPTION-01] | E4-S1, Ronda 8 (R8-06) | Sin cuota GPU ni prioridad en `/authorize`; la telemetría GPU no decide en el Módulo 1 | A |
| [ASSUMPTION-03] | Fuera de alcance | Barrido inter-semestral `INACTIVE` y producción de `COMPLETED`/`EXPIRED` sin TTL | A |
| [ASSUMPTION] | Overview | `STU-MATEO-99` del PRD §4.3 tratado como `STU-98432` (R8-08); PRD no editado | A |

## Correcciones Ronda 10 (readiness gate NOT READY)

| ID gate | Corrección aplicada en epics.md | Estado |
|---|---|---|
| C-1 | AD-07 en Binding invariants de E1-S3, ATDD T-AD07-01/02 (RED) y AC de clamp de `page_size` (0 -> 1, 101 -> 100); trazabilidad AD-07 actualizada | Aplicado |
| C-2 | Tabla «Umbrales triageados»; los AC citan solo el umbral gate (2.0 s para 120 filas) | Aplicado |
| M-1 | UX-DR1, Loading de E3-S1 y tabla Estados UX: progreso de subida en cliente + `Validando lote atómico...`; sin progreso por fila | Aplicado en epics; EXPERIENCE.md no editado (fuente Plan-2) |
| M-2 | Génesis = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` en E1-S3 (Contrato y AC) | Aplicado en epics. DDL (`001_module1_schema.sql:192,210`), `events.md:134` y `atdd_support.py` ya usan la constante. Quedan fixtures con `"0" * 64` en `module1_guard_contracts.test.py` (líneas 51, 294, 297, 317), que son filas de inserción y no aserciones de génesis: revisar en `bmad-testarch-atdd` |
| M-3 | Evidencia TEA desactualizada | Pendiente: `bmad-testarch-test-review` y `bmad-testarch-trace` no se ejecutaron en esta pasada |
| M-4 | 15 gaps de Ronda 8/9/10 reemplazados por node IDs verificados; abiertos solo G-1, G-15, G-16 | Aplicado (tests ya existían en la colección) |
| M-5 | Umbrales NFR-AUDIT-06 y NFR-DISP-07 en «Umbrales triageados» | Aplicado |
| M-6 | Migración completa en E1-S1 con justificación; historias posteriores citan sus tablas e invariantes | Aplicado |
| Menores | `approved_by` ya es el nombre usado en epics (el paquete de decisiones ya corregido); lista de [ASSUMPTION] con owner; T-REV-01 duplicado renombrado a T-REV-01b; m-1 (`STU-MATEO-99` en PRD) sin cambio por decisión | Aplicado en epics |

---

## Dependencias entre historias

Regla: una historia solo depende de historias anteriores en el orden de este documento.

| Historia | Depende de | Verificación de orden |
|---|---|---|
| E1-S1 | ninguna | inicio |
| E1-S2 | E1-S1 | anterior |
| E1-S3 | E1-S2 | anterior |
| E2-S1 | E1-S1, E1-S3 | anteriores |
| E2-S2 | E2-S1, E1-S2 | anteriores |
| E2-S3 | E2-S1 | anterior |
| E2-S4 | E2-S1 | anterior |
| E2-S5 | E2-S1, E2-S4 | anteriores |
| E3-S1 | E1-S1, E1-S3, E2-S4 | anteriores |
| E3-S2 | E3-S1 | anterior |
| E3-S3 | E3-S1, E3-S2 | anteriores |
| E3-S4 | E3-S1, E2-S4 | anteriores |
| E4-S1 | E1-S1, E1-S2 | anteriores |
| E4-S2 | E4-S1, E1-S2 | anteriores |
| E4-S3 | E1-S2, E4-S1 | anteriores |
| E4-S4 | E4-S1, E1-S2 | anteriores |

Dependencias entre épicas: E2 -> E1; E3 -> E1, E2; E4 -> E1. Sin dependencias hacia adelante.

---

## Mandatory Edge Case y fallos con historia dedicada

- EDGE-01 (Student CS101 0 GPU y TA CS-480 alta prioridad): **E4-S1** (dedicada), con apoyo de E4-S2 (escalación en CS-480 no altera CS101).
- Fallo 422 de integridad de nómina con rollback total (fila 85 con `@gmail.com`): **E3-S2** (dedicada).
- Identidad suspendida o expulsada en nómina (422, R9-01): **E3-S2**.
- Revocación y 403 tras baja (`SUBJECT_ENROLLMENT_DROPPED`): **E2-S2** (dedicada).
- 403 `ADMIN_ROLE_REQUIRED` en revoke: **E2-S4** (dedicada). En ingest: E3-S4 (criterio de admin dentro de la historia de límites).
- Fallo de almacén con 503 fail-closed: **E2-S3** (con fallo de store en el criterio principal).
- Expiración de escalación (403 `STATUS_ESCALATION_EXPIRED`): **E4-S2** (dedicada).

---

## Tabla de Estados UX -> contrato + DTO

| Estado (fuente) | Contrato | DTO | Historia | Estado de cobertura |
|---|---|---|---|---|
| Loading carga masiva (EXPERIENCE §2.1, UX-DR1) | Progreso de SUBIDA en cliente (bytes enviados / total) y `Validando lote atómico...` hasta la respuesta de `ingestRoster` (síncrona, AD-02). Sin canal de progreso en backend ni por fila | ninguno (client-only) | E3-S1 | Mapeado (M-1, R10); sin DTO propio |
| Loading evaluación RBAC (EXPERIENCE §2.1) | Estado de cliente mientras responde `resolveEffectivePermissions` | ninguno (client-only) | E1-S2 | Mapeado a la petición |
| Empty Caso A: asignatura sin estudiantes (EXPERIENCE §2.2 A, UX-DR2) | Lectura de membresías no contratada en las tres operaciones | n/a | fuera de alcance | Fuera de alcance: lectura de membresías (owner A) |
| Empty Caso B: sin escalaciones pendientes (EXPERIENCE §2.2 B) | Bandeja de escalaciones no contratada | n/a | fuera de alcance | Fuera de alcance: escalación (owner A) |
| Empty Caso C: auditoría sin coincidencias (EXPERIENCE §2.2 C) | Consulta forense paginada no contratada | n/a | fuera de alcance | Fuera de alcance: consulta forense (owner B) |
| Empty Caso D: identidad sin asignaturas, EDGE-UX-01 (EXPERIENCE §2.2 D, UX-DR9) | `resolveEffectivePermissions` Q1/P5 con membresía inexistente en el curso | `DenyBody` (`SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`) | E1-S2 | Mapeado: `test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4` (T-RES-11) |
| Error Caso A: fila 85 con correo externo (EXPERIENCE §2.3 A, UX-DR3) | `ingestRoster` P3 + Q3 (422) | `RosterRejectedManifest` | E3-S2 | Mapeado. `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL` = `rule_ids` de la fila `ROSTER_VALIDATION_FAILED` (R8-09; T-ROS-12) |
| Error Caso B: auto-aprobación de escalación (EXPERIENCE §2.3 B) | Aprobación de escalación no contratada; el guard DDL sí | n/a (DDL: CHECK `approved_by <> requester_id`) | fuera de alcance (flujo) | Flujo fuera de alcance: `FORBIDDEN_SELF_APPROVAL` (owner A). Respaldo DDL: T-ESC-GUARD-03 |
| Error 401 en consulta forense con sesión expirada, EDGE-UX-03 (EXPERIENCE §2.5, UX-DR10) | Consulta forense no contratada; el 401 general de las tres operaciones sí | `ErrorBody` (`AUTH_TOKEN_INVALID`) | fuera de alcance (modal); E4-S1, E2-S4, E3-S4 (401 general) | Modal fuera de alcance |
| Success ingestión masiva (EXPERIENCE §2.4, UX-DR4) | `ingestRoster` Q1 (201) | `RosterIngestResponse` | E3-S1 | Mapeado |
| Success escalación temporal concedida (EXPERIENCE §2.4, timer) | Aprobación no contratada; el vencimiento sí en resolve | `AuthorizeResponse` (`instructor_privileged`) | E4-S2 | Parcial: el timer lee `expires_at` del ticket |
| Denied E-01 Confused Deputy (EXPERIENCE §3.2, UX-DR5) | `resolveEffectivePermissions` P5 (`RESOURCE_SUBJECT_MISMATCH`) | `DenyBody` | E4-S3 | Mapeado: T-RES-10 (orientación inversa) y `test_resolve_header_cs101_arn_cs480_mismatch_403` (G-5) |
| Denied E-02 revocación por baja (EXPERIENCE §3.2, UX-DR6) | `resolveEffectivePermissions` P5 con DROPPED (`SUBJECT_ENROLLMENT_DROPPED`) | `DenyBody` | E2-S2 | Mapeado; node T-RES-03 |
| Denied E-03 expiración de escalación (EXPERIENCE §3.2, UX-DR7) | `resolveEffectivePermissions` Q1 con ticket vencido (`STATUS_ESCALATION_EXPIRED`) | `DenyBody` con `threshold` | E4-S2 | Mapeado; node T-RES-04 |
| Denied E-04 denegación por jefatura (EXPERIENCE §3.2, UX-DR8, EDGE-UX-02) | Rechazo de escalación no contratado (`ESCALATION_REQUEST_REJECTED`) | n/a | fuera de alcance | Fuera de alcance: escalación (owner A) |
| Denied 403 ADMIN_ROLE_REQUIRED (contracts §4; sin banner UX) | `revokeCourseAccess` P0 e `ingestRoster` P0 | `ErrorBody` (sin `explanation`) | E2-S4, E3-S4 | Mapeado: T-REV-P-05, T-REV-09, T-ROS-P-05, T-ROS-09; banner UX `[ASSUMPTION]` |

---

## Trazabilidad AD-n -> historias -> tests

Tabla regenerada automáticamente (K-6, 2026-10-14) por `.work/regen_ad_table.py` desde los **Binding invariants** de cada historia y los docstrings de los tests citados en ella; todos los node IDs están en la colección de pytest.

| AD | Historias (Binding invariants) | Tests (node IDs cuyo docstring cita el AD) | Estado |
|---|---|---|---|
| AD-01 Context Isolation & Binding (heredado) | E1-S2, E2-S2, E4-S1, E4-S2, E4-S3, E4-S4 | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_student_inference_cs480`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_missing_identity_and_course_reports_identity_first`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED]`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[COMPLETED]`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny`; `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_deny_response_has_no_quota_or_priority_fields`; `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_escalation_in_cs480_does_not_alter_cs101`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_arn_grammar_rejects`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_resource_subject_mismatch_403_explained_no_mutation`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_header_cs101_arn_cs480_mismatch_403`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_lowercase_course_header_404_unknown_course`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_precedes_subject_mismatch`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-igual]`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-distinto]`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[vacio]` | OK (19 tests) |
| AD-02 Ingestión atómica y anti-role-smuggling (heredado) | E2-S4, E3-S1, E3-S2, E3-S3, E3-S4 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_non_admin_actor_403_no_mutation`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_valid_batch_persists_all_rows`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_reuses_existing_identity_without_duplicate`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inexistente]`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inactiva]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_queue_full_503_no_mutation`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_row85_rollback`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[dominio-externo]`; `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_roster_rejected_cites_ad02_observed_row`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_roster_intra_batch_duplicate`; `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_intra_batch_duplicate_cites_ad02`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_duplicate_email_in_batch_422_no_writes`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[SUSPENDED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[EXPELLED]`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_no_role_smuggling`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_role_smuggling_422_field_assigned_role`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[SUSPENDED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[COMPLETED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_conflicting_identity_row_422_no_identity_update`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_membership_per_pair_across_terms`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_non_admin_actor_403_no_mutation`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_1000_rows_boundary_accepted`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_reingest_creates_new_batch_id`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_email_domain_case_insensitive_local_part_preserved`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[vacio]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity` | OK (31 tests) |
| AD-03 Invalidación determinista e idempotencia (heredado) | E2-S1, E2-S2, E2-S3, E2-S4, E2-S5 | `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_active_pair_returns_revoked`; `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_emits_one_membership_revoked_event`; `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_all_credentials`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_preserves_other_course`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_revoke_commit_denies_enrollment_dropped`; `test/atdd/module1_contracts.test.py::TestConcurrency::test_resolve_concurrent_with_revoke_never_allows_after_commit`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_replay_idempotent`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_concurrent_double_drop_single_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_store_failure_closed`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_clock_failure_503_fail_closed_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_already_revoked_cites_ad03`; `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_first_revoke_reports_credentials_revoked`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[solo-espacios]`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[control-nul]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_281_chars_400_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_empty_reason_and_missing_timestamp_rule_ids_order` | OK (18 tests) |
| AD-04 Ledger encadenado y metadata (heredado) | E1-S2, E1-S3, E2-S1, E2-S3, E3-S1, E3-S2, E3-S3 | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allow_appends_one_authorization_event`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_queue_full_503_no_decision_no_mutation`; `test/atdd/module1_contracts.test.py::TestLedgerChain::test_ledger_chain_and_anchor`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_update_rejected`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_delete_rejected`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_update_rejected`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_delete_rejected`; `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_emits_one_membership_revoked_event`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_emits_one_roster_ingested_event`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_row85_rollback`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_membership_per_pair_across_terms` | OK (11 tests) |
| AD-05 Anti auto-aprobación y exclusión mutua (heredado) | E3-S3, E4-S2 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[SUSPENDED]`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[COMPLETED]`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_escalation_boundary_expires`; `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_expires_active_ticket_once_with_one_event`; `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_crash_recovery_reconciles_all_expired_tickets`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_escalation_per_pair`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_self_approval_rejected` | OK (8 tests) |
| AD-06 Cero secretos en trazas (heredado) | E1-S3, E2-S5, E3-S1, E3-S2, E3-S4, E4-S4 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[nul]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[newline]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[del]`; `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_no_secret_leak_in_drop_reason`; `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear`; `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored`; `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash`; `test/atdd/module1_ingest_rules_contracts.test.py::TestSecrets::test_ingest_secret_in_batch_field_never_in_manifest_or_logs`; `test/atdd/module1_resolve_contracts.test.py::TestSecrets::test_resolve_secret_in_action_400_never_echoed_in_clear` | OK (10 tests) |
| AD-07 Paginación acotada (heredado) | E1-S3 | `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_zero_becomes_one`; `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_above_limit_becomes_100` | OK (2 tests) |
| AD-08 Pureza del dominio hexagonal (spine-local) | E1-S1, E1-S2, E2-S5 | `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_has_no_infrastructure_imports_or_clock_calls`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[os.urandom]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[from-os-urandom]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[uuid4]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[secrets]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[time.monotonic]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[datetime.now]`; `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[random]`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_edge_case_seed_duplicates_rejected_by_pk`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_future_timestamp_400_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_timestamp_at_tolerance_boundary_accepted`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-no-utc]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-menos-cero]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fraccion-7-digitos]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[sin-hora]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[segundo-60]`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fecha-inexistente]` | OK (18 tests) |
| AD-09 Mapeo canónico operación a HTTP (spine-local) | E1-S2, E2-S1, E2-S4, E2-S5, E3-S1, E3-S4, E4-S1, E4-S4 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_declared_routes_match_openapi_one_route_per_operation`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_non_admin_actor_403_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_student_token_403_admin_before_drop_reason_syntax`; `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_auth_token_invalid_401_before_body_validation`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[solo-espacios]`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[control-nul]`; `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_term_percent_encoded_decoded_once`; `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[inexistente]`; `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[minusculas]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_non_admin_actor_403_no_mutation`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_student_token_403_admin_before_batch_syntax`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_auth_token_invalid_401_before_batch_validation`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_roster_body_with_utf8_bom_400_malformed_batch`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_rfc4180_parses_quoted_comma_and_escaped_quote_in_four_fields`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_row_with_five_fields_400_malformed_batch`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_unsupported_content_type_400_malformed_batch`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[sin-partes]`; `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[dos-partes]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]`; `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_auth_token_invalid_401_before_arn_validation`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_malformed_action_400_no_mutation`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-igual]`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-distinto]`; `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[vacio]` | OK (26 tests) |
| AD-10 Fixture del Mandatory Edge Case (spine-local) | E1-S1, E1-S2, E4-S1, E4-S2, E4-S4 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`; `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation`; `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_cpu_toy_model_cs101`; `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_effective_role_is_exact_roles_id`; `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_escalation_in_cs480_does_not_alter_cs101`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_malformed_action_400_no_mutation`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_model_outside_catalog_denied` | OK (7 tests) |
| AD-11 Decisión explicable con regla citada (spine-local) | E1-S2, E1-S3, E2-S1, E2-S2, E2-S3, E2-S5, E3-S1, E3-S2, E3-S3, E4-S1, E4-S2, E4-S3, E4-S4 | `test/atdd/module1_guard_contracts.test.py::TestErrorEnvelope::test_guard_audit_log_tampering_500_uses_error_body_without_explanation`; `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_already_revoked_cites_ad03`; `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_first_revoke_reports_credentials_revoked`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule`; `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_roster_rejected_cites_ad02_observed_row`; `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_intra_batch_duplicate_cites_ad02`; `test/atdd/module1_resolve_contracts.test.py::TestExplainability::test_explain_deny_expired_threshold_reports_expires_at`; `test/atdd/module1_contracts.test.py::TestExplainability::test_explain_assert_rule_cited`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]`; `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_model_outside_catalog_denied` | OK (11 tests) |
| AD-12 Serialización de carreras e idempotencia (spine-local) | E1-S1, E1-S2, E2-S1, E2-S2, E2-S3, E3-S1, E4-S2 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_queue_full_503_no_decision_no_mutation`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_all_credentials`; `test/atdd/module1_contracts.test.py::TestConcurrency::test_resolve_concurrent_with_revoke_never_allows_after_commit`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_concurrent_double_drop_single_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_clock_failure_503_fail_closed_no_mutation`; `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_queue_full_503_no_mutation`; `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials` | OK (10 tests) |
| AD-13 Frontera temporal semiabierta (spine-local) | E1-S1, E1-S2, E3-S2, E4-S2, E4-S4 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric`; `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_request_now_captured_once_and_reused_as_occurred_at`; `test/atdd/module1_ingest_contracts.test.py::TestRequestTimeInRejection::test_roster_rejected_occurred_at_reuses_single_request_now`; `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_escalation_boundary_expires`; `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_before_granted_uses_base_role`; `test/atdd/module1_resolve_contracts.test.py::TestExplainability::test_explain_deny_expired_threshold_reports_expires_at`; `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_expires_active_ticket_once_with_one_event`; `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_does_not_expire_ticket_not_yet_granted`; `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_expires_after_granted_check` | OK (9 tests) |

## Tabla de cobertura: Requisito -> historias (FR Coverage Map)

| Requisito | Historias | Tipo |
|---|---|---|
| FR-INGEST-01 | E3-S1, E3-S2, E3-S3, E3-S4 | FR contratado (operación `ingestRoster`) |
| FR-ESCAL-02 | E4-S2 | FR parcial: honrar ticket ACTIVE o vencido en resolve (AD-13, I2, EDGE-01). Resto fuera de alcance |
| FR-REVOC-03 | E2-S1, E2-S2, E2-S3, E2-S4, E2-S5 | FR contratado (operación `revokeCourseAccess`) |
| FR-AUDIT-04 | E1-S3 | FR parcial: ledger encadenado append-only (AD-04/Q3). Consulta forense paginada fuera de alcance |
| NFR-PERF-01 | E1-S2, E4-S1 | NFR PLANNED (`nfr-evidence.md`), umbral p95 < 20 ms y p99 < 50 ms a 100 req/s. Sin medición (gap G-16) |
| NFR-PERF-02 | E3-S1 | NFR PLANNED, umbral T < 3.0 s para 1,000 filas. Sin medición (gap G-16) |
| NFR-REVOC-03 | E2-S1, E2-S3 | NFR PLANNED, umbral T_local < 200 ms y T_revoc < 60 s. Sin medición (gap G-16) |
| NFR-SEC-04 | E2-S5, E4-S4 | NFR PLANNED. Tests de no-eco de secretos: T-SEC-01, T-SEC-REV-01, T-SEC-ROS-01, T-RES-14. Regex sobre 10,000 líneas: gap G-16 |
| NFR-SEC-05 | E3-S1 | NFR PLANNED. Hash y salt de 16 bytes: `test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored` (T-ROS-17) |
| NFR-AUDIT-06 | E1-S3 | NFR PLANNED. Índice `(resource_type, timestamp)` en DDL y probado (T-LED-GUARD-05, R8-07). Medición de 100,000 eventos: gap G-16 |
| NFR-DISP-07 | E1-S1 | NFR PLANNED, RAM <= 512 MB y T_boot < 5.0 s. Sin medición (gap G-16) |

Requisitos del PRD sin FR/NFR ID: PRD §5.1 y §5.2 (contexto RBAC y EDGE-01) -> E1-S2, E4-S1, E4-S3, E4-S4.

---

## ACCEPT del review final -> historia/AC donde se refleja

Fuente: `solu2-module1/planning/detailed-design/reviews/review-detailed-design.md` (Revisión final 2026-10-13 y 2026-10-14). Los 42 ACCEPT tienen historia y AC, salvo los marcados con gap.

| ID | Hallazgo | Historia / AC |
|---|---|---|
| ADVF-01 | Sin regla de llamador para revoke e ingest (`ADMIN_ROLE_REQUIRED`) | E2-S4 (T-REV-P-05, T-REV-09); E3-S4 (T-ROS-P-05, T-ROS-09) |
| ADVF-02 | Token Bearer opaco validado por `TokenVerifierPort` | E2-S4 (T-REV-11, RED); E3-S4 (T-ROS-20, RED); E4-S1 (T-RES-12, RED) |
| ADVF-03 | Columnas NOT NULL de `audit_ledger` (actor, resource, action) | E2-S1 (AC evento, T-REV-HP-02); E3-S1 |
| ADVF-04 | Mapeo ledger de `roster.ingested` y `roster.rejected` | E3-S1 (T-ROS-HP-02); E3-S2 (T-ROS-08) |
| ADVF-05 | Lectura más escritura encolada en resolve | E1-S2 (T-RES-HP-02); E2-S2 (T-CON-01) |
| ADVF-06 | Fila `ta`/CS-480 en la matriz; EDGE-01 con DENY independiente si no hubiera fila | E4-S1 (test_edge01_context_isolation) |
| ADVF-07 | Claves `action`, `resource_class`, `model` en la matriz | E4-S1 (AC matriz); E4-S4 (T-RES-I-04) |
| ADVF-08 | DROPPED -> `SUBJECT_ENROLLMENT_DROPPED`; otro no activo -> `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` | E2-S2 (T-RES-03) para DROPPED; E1-S2 (T-RES-11) para membresía inexistente. SUSPENDED/COMPLETED en resolve: G-4b con node ID en E2-S2 |
| ADVF-09 | `at` obligatorio; `null` -> `INVALID_AT` | E4-S4 (T-RES-P-04) |
| ADVF-10 | Comparación byte a byte de `CS-480` (sin case-folding) | E4-S3 (T-RES-10, orientación inversa; `cs-480` -> 404, G-5 y G-6 con node ID en E4-S3) |
| ADVF-11 | Errores de forma mapeados al catálogo, no 422 del framework | E3-S4 (T-HTTP-02..06, T-ROS-06, T-ROS-06b); E2-S5 (T-REV-03, T-REV-10) |
| ADVF-12 | `term` discrepante siempre `MALFORMED_TERM` | E3-S1 (T-ROS-05) |
| ADVF-13 | `term` en la clave de membresía; guarda DDL | E3-S3 (T-MEM-GUARD-01) |
| ADVF-14 | Anti-smuggling -> `ROSTER_VALIDATION_FAILED` sobre `assigned_role` | E3-S3 (T-ROS-03b) |
| ADVF-15 | `SUSPENDED`/`COMPLETED` con mismo rol sin reactivar | E3-S3 (T-ROS-16 x3) |
| ADVF-17 | Búsqueda de credencial por `key_prefix` y verificación SHA-256 | E3-S1 (T-ROS-17 para hash y salt). Lookup por `key_prefix`: G-13 con node ID en E3-S1 |
| ADVF-19 | Conflicto de identidad por fila, sin update | E3-S3 (T-ROS-15) |
| ADVF-20 | `processed` y conteos definidos | E3-S1 (T-ROS-HP-01: 120, 115, 5) |
| ADVF-21 | Patrón `^[A-Za-z0-9-]{1,64}$`, case-sensitive | E3-S4: G-9 con node ID |
| ADVF-23 | CHECK GLOB de formato fijo en timestamps | E1-S3 (T-LED-GUARD-06 para `audit_ledger`); E4-S2 (T-ESC-GUARD-02 para `escalation_tickets`) |
| ADVF-25 | Seed de roles y subjects en fixtures, no en DDL | E1-S1 (harness `test_seed_fleet_topology`, `test_db_has_ddl_tables`) |
| ECF-01 | JSON con 1001 filas -> 413 antes de validar | E3-S4 (T-ROS-06b) |
| ECF-02 | JSON con `rows: []` -> 400 `BATCH_EMPTY` | E3-S4 (T-ROS-06) |
| ECF-03 | `drop_reason` vacío o > 280 -> 400 `MALFORMED_DROP_REASON` | E2-S5 (T-REV-03 para blancos). Límite 281: G-10 con node ID en E2-S5 |
| ECF-05 | Eco de `subject_id` ausente o distinto -> `MALFORMED_BATCH` | E3-S4: G-8 con node ID |
| ECF-06 | `term` válido pero distinto del curso -> `MALFORMED_TERM` | E3-S1 (T-ROS-05) |
| ECF-07 | Dominio de email exacto `universidad.edu`, un solo `@` | E3-S4 (T-ROS-18); E3-S2 (T-ROS-12) |
| ECF-08 | Emails repetidos en el lote -> `ROSTER_VALIDATION_FAILED` en memoria | E3-S2 (T-ROS-10) |
| ECF-09 | `institutional_id` existente con otro email, sin update | E3-S3 (T-ROS-15) |
| ECF-12 | Caracteres de control `Cc` -> `MALFORMED_DROP_REASON` | E2-S5 (T-REV-10 x3) |
| ECF-13 | `timestamp` > `request_now` + 300 s -> `MALFORMED_DROP_TIMESTAMP` | E2-S5 (T-REV-P-06, T-REV-I-06) |
| ECF-14 | `at = null` en llamada interna -> `INVALID_AT` | E4-S4 (T-RES-P-04) |
| ECF-15 | CHECK de formato fijo de timestamps | E1-S3 (T-LED-GUARD-06); E4-S2 (T-ESC-GUARD-02) |
| ECF-17 | Email vacío o en blanco -> `ROSTER_VALIDATION_FAILED` | E3-S4 (T-ROS-11 [vacio]) |
| ECF-18 | Lookup de credencial por `key_prefix` | E3-S1: G-13 con node ID |
| ECF-19 | CSV con BOM -> `MALFORMED_BATCH` | E3-S4 (T-HTTP-02) |
| ECF-20 | CSV RFC 4180 con 4 campos por fila | E3-S4 (T-HTTP-03, T-HTTP-04) |
| ECF-21 | `Content-Type` no soportado -> `MALFORMED_BATCH` | E3-S4 (T-HTTP-05) |
| ECF-22 | Multipart con dos partes de archivo -> `MALFORMED_BATCH` | E3-S4 (T-HTTP-06) |
| ECF-23 | Mismo rol sobre `SUSPENDED` o `COMPLETED` sin reactivar | E3-S3 (T-ROS-16) |
| ECF-24 | `action` vacía -> `MALFORMED_ACTION` | E4-S4 (T-RES-P-05) |
| ECF-25 | Rol `ta` en CS-480 sin fila de matriz | E4-S1 (test_edge01_context_isolation) |

Los 7 REJECT (ECF-04, ECF-10, ECF-11, ECF-27, ECF-28, ECF-29, ECF-30) y los DEFER (ADVF-16, ADVF-18, ADVF-22, ADVF-24, ECF-16, ECF-26) no tienen historia y no se implementan en este alcance.

---

## Decisiones Ronda 7 aplicadas (R7-01..R7-03)

| ID | Decisión | Estado en epics |
|---|---|---|
| R7-01 | Firma de dominio de revoke con `actor`, `drop_reason`, `timestamp`, `request_now` explícitos; adapter HTTP solo parsea | Aplicada en E2-S1 y escrita en contracts §2 (R8-10) |
| R7-02 | `term` del lote == `term` vigente del curso (`MALFORMED_TERM` si no); membresías de otros terms solo por guarda DDL | Aplicada en E3-S1 (T-ROS-05) y E3-S3 (T-MEM-GUARD-01) |
| R7-03 | `CredentialDeliveryPort.enqueue` por credencial emitida; 201 sin `uai_live_` | **Modificada por R8-01**: una vez por fila aceptada (120 en el ejemplo), no por identidad creada. Node RED: T-ROS-04 (en E3-S1) |

---

## Decisiones que cerraron las preguntas (Ronda 8)

Las preguntas bloqueantes de la revisión anterior de este documento quedan cerradas por R8-01..R8-10 (`.work/paquete-decisiones-F-H.md`, aprobado por el estudiante 2026-10-14). Sus aplicaciones en diseño ya están escritas en contracts.md, dto.py, ports-and-adapters.md y 001_module1_schema.sql.

| Pregunta original | Decisión | Historia / AC afectado |
|---|---|---|
| 1. Credenciales del lote (115 vs 120) | R8-01: una credencial `uai_live_` por membresía que el lote deja ACTIVE en el curso = una por fila aceptada (120). `CredentialDeliveryPort.enqueue` ×120. 201 sin `uai_live_`. | E3-S1 (Happy persistencia y credenciales; T-ROS-04) |
| 2. Explicación del 201 | R8-02: el 201 de ingesta NO lleva `ExplanationDTO`; la explicabilidad aplica a decisiones ALLOW/DENY y a rechazos 403/422. | E3-S1 (Q1, endpoint, happy); E3-S2 (422 sí conserva `explanation`) |
| 3. AD-07 sin test RED | R8-03: RED de `clamp_page_size` (0→1, 101→100) como stub puro; consulta forense fuera de las 3 operaciones (owner B). | Trazabilidad AD-07 (T-AD07-01, T-AD07-02) |
| 4. Casos de contrato sin node RED | R8-04: RED para `RESOURCE_SUBJECT_MISMATCH`, `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`, `AUTH_TOKEN_INVALID` (3 ops), `AUTH_INTERNAL_POLICY_UNAVAILABLE` (resolve, ingest, cola llena de revoke). | E1-S2 (T-RES-11, T-RES-13); E2-S3 (T-REV-06); E3-S1 (T-ROS-13); E4-S3 (T-RES-10); E2-S4, E3-S4, E4-S1 (401 RED) |
| 5. Test RED de `CredentialDeliveryPort` | R8-05 (con R8-01): se agrega ahora. | E3-S1 (T-ROS-04) |
| 6. Puerto de telemetría | R8-06: `TelemetryPort.emit_metric(name, value, labels)`, adaptador `sim_telemetry`; Módulo 1 no consume telemetría GPU para decidir ([ASSUMPTION-01]). | E1-S1 (T-SCH-04); E4-S2 (barrido diferido) |
| 7. Índice de NFR-AUDIT-06 | R8-07: `audit_ledger.resource_type TEXT NOT NULL` (prefijo `model:<clase>` del ARN) e índice `(resource_type, timestamp)`. resource_type no entra al hash (H-14). | E1-S3 (T-LED-GUARD-05) |
| 8. ID de Mateo | R8-08: canónico `STU-98432`; `STU-MATEO-99` de PRD §4.3/scenario-3 se registra como inconsistencia de Plan-2 y se trata como el mismo actor. PRD no editado. | Encabezado de fixtures; E1-S2, E2-S1 |
| 9. Código UX de correo | R8-09: `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL` = `rule_ids` de la fila `ROSTER_VALIDATION_FAILED` sobre `email`. Sin código HTTP nuevo. | E3-S2 (T-ROS-12); tabla de estados UX |
| R8-10 (firma de R7-01) | Nota de firma en contracts §2. | E2-S1 (nota de firma) |

---

## Decisiones Ronda 9 aplicadas

| ID | Decisión | Historia / AC afectado |
|---|---|---|
| R9-00 (REJECT de propuesta IA) | Los tests de 401 (T-RES-12, T-REV-11, T-ROS-20) son RED, no guardas verdes: un fake configurado por el propio test daría una aserción tautológica. `_actor()` lanza `NotImplementedError`. | E4-S1 (T-RES-12), E2-S4 (T-REV-11), E3-S4 (T-ROS-20) |
| R9-01 (IDENTITY_BARRED en ingest) | Identidad preexistente `SUSPENDED`/`EXPELLED` en un lote = fila `ROSTER_VALIDATION_FAILED` sobre `identity_status`, lote 422, `rule_ids: ["ROSTER_VALIDATION_FAILED", "IDENTITY_BARRED"]`. `403 IDENTITY_BARRED` solo en `/authorize`. | E3-S2 (T-ROS-14 x2); E3-S2 código principal. 403 en `/authorize`: G-4 cerrado en E4-S3 |
| R9-02 (AD-05 aprobador ≠ solicitante) | DDL: `CHECK (approved_by IS NULL OR approved_by <> requester_id)` en `escalation_tickets`. | Trazabilidad AD-05 (T-ESC-GUARD-03) |
| R9-03 (mismatch de E4-S3) | Dos cursos existentes: header `CS101` con ARN de `CS-480` → 403 `RESOURCE_SUBJECT_MISMATCH`. Header `cs-480` → 404 `UNKNOWN_COURSE` por el orden de pasos. | E4-S3 (AC y endpoint). T-RES-10 usa la orientación inversa; G-5 cerrado en R10; `cs-480` cerrado con node ID (G-6) |
| R9-04 (formato de `audit_ledger.timestamp`) | CHECK GLOB de formato fijo también en `audit_ledger.timestamp` (y `audit_events.occurred_at`). | E1-S3 (T-LED-GUARD-06) |
| R9-05 (supuestos de tests) | DENY de política como resultado `{decision: "DENY"}` (HTTP 403 lo mapea el adapter); máscara AD-06 tal como ARCHITECTURE.md; salt de 16 bytes del `IdGenerator`; `resource_type = "model:" + resource_class` (`model:unknown` fuera de catálogo). | E3-S1 (T-ROS-17); E1-S3 (T-LED-GUARD-05); E2-S5 (T-SEC-01) |

---

## Gaps de cobertura (abiertos tras Ronda 10)

Solo siguen abiertos los gaps sin test en `collect-only`. Los demás gaps (G-2 a G-14 y G-17) tienen node ID desde la Ronda 10 (tabla inferior).

| ID | Caso | Historia | Razón | Owner |
|---|---|---|---|---|
| G-1 | Propagación `revocation_propagated_at`: T1 - T0 < 200 ms (gate NFR-REVOC-03; 500 ms = objetivo laxo PRD §4.3) | E2-S2 | Medición E2E. NFR PLANNED, sin medición evidenciada | B (Fase 3 NFR, Test-lead) |
| G-15 | `QueueReservation` como unidad (reserve / publish / release) | E1-S2, E2-S1 | El efecto de cola llena está cubierto (503 en resolve, revoke e ingest); la reserva en sí no. DEFER a Fase 3 | B |
| G-16 | Mediciones NFR: PERF-01 (p95 < 20 ms, p99 < 50 ms a 100 req/s), PERF-02 (1,000 filas < 3.0 s), REVOC-03 (T_local, T_revoc), SEC-04 (regex sobre 10,000 líneas), AUDIT-06 (100,000 eventos p95 < 500 ms), DISP-07 (RAM, boot) | E1-S2, E2-S1, E2-S5, E3-S1, E1-S3, E1-S1 | NFR PLANNED: requieren corridas medibles reales (`nfr-evidence.md`) | B (Fase 3 NFR, Test-lead) |

Gaps cerrados con node ID (verificados con `cd solu2-module1 && .venv/bin/pytest --collect-only -q`):

| Gap | Caso | Node ID | Historia |
|---|---|---|---|
| G-2 | `busy_timeout` agotado -> 503 sin commit parcial | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit` | E2-S3 |
| G-3 | Tras la baja: aislamiento CS101, repetición x3 y evento DENY por intento | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` | E2-S2 |
| G-4 | `IDENTITY_BARRED` en `/authorize` y precedencia sobre mismatch (H-17) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]`, `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]`; `...::TestPreconditions::test_resolve_identity_barred_precedes_subject_mismatch` | E4-S3 |
| G-4b | Membresía `SUSPENDED`/`COMPLETED` en resolve -> `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (ADVF-08) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED]`, `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[COMPLETED]` | E2-S2 |
| G-5 | Ejemplo R9-03 literal: header `CS101` + ARN `CS-480` -> 403 `RESOURCE_SUBJECT_MISMATCH` | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_header_cs101_arn_cs480_mismatch_403` | E4-S3 |
| G-6 | Header `cs-480` -> 404 `UNKNOWN_COURSE` (R9-03, ADVF-10) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_lowercase_course_header_404_unknown_course` | E4-S3 |
| G-7 | Precedencia F-03: identidad inexistente antes que curso inexistente | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_missing_identity_and_course_reports_identity_first` | E1-S2 |
| G-8 | Eco de `subject_id` distinto o ausente -> `MALFORMED_BATCH` (ECF-05) | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]`, `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]` | E3-S4 |
| G-9 | `institutional_id` sensible a mayúsculas (ADVF-21) | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity` | E3-S4 |
| G-10 | `drop_reason` de 281 puntos -> `MALFORMED_DROP_REASON` | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_281_chars_400_no_mutation` | E2-S5 |
| G-11 | Precedencia de `rule_ids` con `drop_reason` vacío y `timestamp` ausente | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_empty_reason_and_missing_timestamp_rule_ids_order` | E2-S5 |
| G-12 | Gramática RFC 3339 UTC de `timestamp` de baja (G9-01) | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-no-utc]`, `[offset-menos-cero]`, `[fraccion-7-digitos]`, `[sin-hora]`, `[segundo-60]`, `[fecha-inexistente]` | E2-S5 |
| G-13 | Lookup de credencial por `key_prefix` y verificación de hash (ADVF-17, ECF-18) | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash` | E3-S1 |
| G-14 | `edge_case_seeds` dos veces -> UNIQUE sin duplicados | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_edge_case_seed_duplicates_rejected_by_pk` | E1-S1 |
| G-17 | Respuesta de resolve sin campos de cuota ni prioridad (I4) | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_deny_response_has_no_quota_or_priority_fields` | E4-S1 |

Fuera de este listado (no son gaps del Módulo 1): consulta forense paginada, auto-aprobación y solicitud de escalación como flujo, verificación de cadena y `AUDIT_LOG_TAMPERING_DETECTED`, revocado-cache y TTL de credenciales. Están en "Fuera de alcance de Solu-2" con owner.

---

## Fuera de alcance de Solu-2

Lo siguiente aparece en el PRD o en el catálogo, pero no es una de las tres operaciones confirmadas (Annex A p.13). No tiene historia ni contrato en este documento; cada ítem tiene owner y razón.

| Elemento | Fuente | Owner | Razón |
|---|---|---|---|
| Crear escalaciones (`POST /api/v1/escalations/request`) | FR-ESCAL-02 (PRD §4.2) | A (Juan Pablo Parra) | Operación no confirmada en Annex A; la creación no tiene P/Q/I en contracts |
| Aprobar escalaciones (`POST /api/v1/escalations/{id}/approve`) y `FORBIDDEN_SELF_APPROVAL` | PRD §4.2, §7.1; AD-05 | A | Operación no confirmada; el catálogo la marca fuera de las tres operaciones. Respaldo DDL cubierto: `approved_by <> requester_id` (T-ESC-GUARD-03, R9-02) |
| Rechazar escalaciones y `ESCALATION_REQUEST_REJECTED` (E-04) | EXPERIENCE §3.2 | A | Operación no confirmada |
| `CONCURRENT_ESCALATION_NOT_PERMITTED` y el índice único de solicitudes (AD-05 exclusión mutua) | PRD §4.2 regla 4; AD-05 | A | Creación de escalación fuera de alcance; respaldo físico probado (T-ESC-GUARD-01) |
| Consulta forense paginada `GET /api/v1/audit/access-events` | FR-AUDIT-04 (PRD §4.4) | B (Daniel Gonzalez) | No es operación core; el clamp de AD-07 sí tiene RED (T-AD07-01, T-AD07-02) |
| Verificación de cadena rota y `AUDIT_LOG_TAMPERING_DETECTED` (500) | PRD §4.4; ADVF-24; ECF-26 (DEFER) | B | Verificación fuera de las tres operaciones; DEFER Fase 3 |
| Capacidad numérica de la cola y recuperación tras fallo de persistencia posterior a aceptación | contracts §5; nfr-evidence DEFERRED-Cola | B | DEFER a Fase 3 NFR |
| Observabilidad del barrido sin reserva de cola (`scheduler_sweep_deferred_total`) | G7-02 | B | Métrica cubierta por T-SCH-04 vía `TelemetryPort`; la política de alertas queda DEFER a Fase 3 NFR |
| `revoked_credentials_cache` y su NFR de 200 ms (ADVF-18) | contracts §2; ADVF-18 | B | DEFER a Fase 3 NFR; no afecta la corrección (la DB es autoridad) |
| TTL, regeneración y reemisión de `uai_live_` | contracts §3; ADVF-16 | A (dueño de credenciales futuro) | DEFER; fuera de las tres operaciones salvo la emisión en 201 |
| Lectura de membresías para vistas (Empty Caso A) | EXPERIENCE §2.2 | A | Operación no confirmada |
| Modal de sesión expirada en consultas forenses (EDGE-UX-03) | EXPERIENCE §2.5 | B | Pertenece a la consulta forense fuera de alcance |
| Integración con LDAP/SSO, Kubernetes, vLLM, telemetría GPU y `RegistrarSource` real | PRD §2.2 | A | Dependencias mockeadas; solo puertos y adapters simulados |
| Migración a PostgreSQL y guardia monotónica NTP | ARCHITECTURE-SPINE, Deferred; ARCH-EDGE-03 | A y B | DEFER post-V1 |
| Barrido inter-semestral `INACTIVE` y producción de `COMPLETED`/`EXPIRED` sin TTL | ASSUMPTION-03; spine Deferred | A | Fuera de las tres operaciones |

---

## Revisión de implementabilidad (Amelia) - estado actual

Revisión hecha como agente dev sobre la revisión anterior de este documento, contra la colección de pytest y el diseño ya actualizado. Veredicto: **sin bloqueantes abiertos**. Quedan pendientes materiales no bloqueantes para GREEN, listados en "Gaps de cobertura" (G-1, G-15 y G-16), cada uno con owner.

| # | Hallazgo previo | Estado | Dónde / por qué pendiente |
|---|---|---|---|
| 1 | [BLOQUEANTE] Conteo de credenciales del lote (115 vs 120) | Resuelto | R8-01. E3-S1: 120 credenciales, `enqueue` ×120 (T-ROS-04) |
| 2 | [BLOQUEANTE] `ExplanationDTO` en el 201 | Resuelto | R8-02. E3-S1 sin explanation; `dto.py` `RosterIngestResponse` sin explanation |
| 3 | [BLOQUEANTE] AD-07 sin test RED | Resuelto | R8-03. T-AD07-01 y T-AD07-02 en la colección |
| 4 | [BLOQUEANTE] Casos de contrato sin node RED | Resuelto | R8-04. G-4, G-5 y G-6 con node ID (R10) |
| 5 | [BLOQUEANTE] Test RED de `CredentialDeliveryPort` (R7-03) | Resuelto | T-ROS-04 en colección (R8-05) |
| 6 | [MATERIAL] Puerto de telemetría sin definir | Resuelto | R8-06: `TelemetryPort` en ports-and-adapters §1 y adaptador `sim_telemetry`. Node: T-SCH-04 |
| 7 | [MATERIAL] Índice NFR-AUDIT-06 inexistente | Resuelto en DDL | R8-07: `resource_type` e `idx_audit_resource_timestamp`; T-LED-GUARD-05. La medición del NFR sigue PLANNED (G-16) |
| 8 | [MATERIAL] ID de Mateo | Resuelto en epics | R8-08: `STU-98432`. PRD §4.3 usa `STU-MATEO-99` (inconsistencia de Plan-2 registrada; PRD no editado) |
| 9 | [MATERIAL] Código UX de correo sin mapeo | Resuelto | R8-09: `rule_ids` con `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL`. T-ROS-12 |
| 10 | [MENOR] Casing de NLP Advanced (`nlp-advanced`) | Sin impacto | No aparece en historias ni en contratos. La discrepancia UX queda como nota de EXPERIENCE (owner A) |
| 11 | [MENOR] Detail de `INTRA_BATCH_DUPLICATE_ID` | Resuelto | Se usa el detail de contracts §4 en E3-S2 |
| 12 | [MENOR] Test IDs duplicados en la checklist (`T-REV-01`, `T-ROS-16`) | Resuelto en epics | Se citan node IDs únicos; la checklist conserva los duplicados como Test ID |
| 13 | [MENOR] Nota de firma R7-01 en contracts §2 | Resuelto | R8-10 escrita en contracts §2 |
| 14 | [MENOR] AD-08 sin node pytest | Resuelto | T-PUR-GUARD-01 (guarda verde) |
| 15 | [MENOR] Escalación con `at` interno | Resuelto | E4-S2: el dev usa la entrada interna `at` en las pruebas de vencimiento |

Hallazgos nuevos de esta revisión (pendientes, sin bloqueo para GREEN de las historias ya cubiertas):
- Gaps G-1, G-15 y G-16 (sección anterior); el resto tiene node ID desde R10.
- Discrepancia R9-03 / T-RES-10 (G-5): cerrada en R10 con `test_resolve_header_cs101_arn_cs480_mismatch_403`, además de T-RES-10.
- Inconsistencia de PRD §4.3 (`STU-MATEO-99`) frente a R8-08: sin cambio en PRD por decisión. Owner A.

---

## Validación final (step-04)

| Chequeo | Resultado |
|---|---|
| FR sin historia | Sin huérfanos: FR-INGEST-01, FR-REVOC-03 completos; FR-ESCAL-02 y FR-AUDIT-04 parciales con fuera de alcance explícito |
| Estados UX mapeados a contrato + DTO | PASS. Cada estado tiene contrato y DTO, o está fuera de alcance con razón |
| AD-n en Binding invariants de >= 1 historia y con >= 1 test RED o guard | PASS. AD-05 vía guardas DDL y resolve; AD-08 vía guarda pytest `T-PUR-GUARD-01`; AD-07 vía E1-S3 y RED (C-1, R10). Flujo de aprobación de escalación fuera de alcance |
| Sin dependencias hacia adelante | PASS |
| Historias completables de forma independiente | PASS (16 historias, cada una con happy y failure) |
| Épicas con protagonista nombrado y sin "capa" | PASS |
| Walking skeleton (Épica 1) | PASS: fixtures, adaptadores simulados, happy path HTTP a ledger (E1-S2) |
| EDGE-01 con historia dedicada | PASS (E4-S1) |
| Fallos con historia dedicada | PASS (E3-S2 rollback 422 e identidad barred, E2-S2 403 tras baja, E2-S4 ADMIN_ROLE_REQUIRED, E2-S3 503, E4-S2 expiración) |
| Node IDs de la suite | PASS: todos los node IDs citados están en la colección actual (155 nodos colectados). Verificación en la sección "Verificación" |
| NFR referenciados con umbral exacto y estado PLANNED | PASS |
| Artefactos sin contradicciones | PARCIAL: PRD §4.3 (`STU-MATEO-99`, sin cambio por decisión) |
| Hallazgos previos triageados y ACCEPT reflejados | PASS: los ACCEPT tienen node ID o gap con owner (G-1, G-15, G-16) |

---

## Verificación

- Comando: `cd solu2-module1 && .venv/bin/pytest --collect-only -q` (Ronda 13, 2026-10-14). Colección: 155 nodos = 4 harness + 21 en `module1_guard_contracts.test.py` (guardas DDL, pureza de `domain/` y envelope) + 130 en las suites ATDD de contrato (127 + T-RES-15 y T-ROS-21 de R12-B01 + T-REV-12 de K-16).
- Node IDs citados en epics.md: 354 ocurrencias, 155 únicos. Válidos (en la colección): 155. Inválidos: 0.
- Tests colectados (ATDD + guardas) no citados en ninguna historia: 0. Harness citados en E1-S1: 4 de 4.
- Colección completa citada en al menos una historia: sí.
- Solo se colectó. No se ejecutó pytest en esta pasada; la última corrida registrada en el gate fue `15 passed, 93 xfailed` sobre 108 nodos, anterior a la pasada ATDD de Ronda 10.
- Gaps abiertos sin node ID por diseño: G-1, G-15 y G-16 (NFR de medición y reserva de cola, owner B).

---

## PREGUNTAS BLOQUEANTES

Ninguna. Las preguntas de la revisión anterior se cerraron en la Ronda 8 (sección "Decisiones que cerraron las preguntas (Ronda 8)"). G-5 queda cerrado en R10. Abiertos sin bloqueo: G-1, G-15 y G-16 (owner B, NFR y Fase 3; ver «Gaps de cobertura»).

---

## Estado global

- Ningún NFR queda `EVIDENCED`. Todos están en `PLANNED` (`nfr-evidence.md`).
- No se declara PASS del readiness gate. Este documento no marca gates como aprobados.
- La Ronda 10 editó `solu2-module1/planning/epics.md` y creó `solu2-module1/planning/sprint-change-proposal-2026-10-14.md`. No se editaron tests, `app/` ni el diseño. Pendiente aguas abajo: re-ejecutar `bmad-testarch-test-review` y `bmad-testarch-trace` (M-3) y reejecutar el readiness gate.

---

## Contradicciones de Plan-2 triageadas

Registro de K-4 del readiness gate corrida 2 (`solu2-module1/planning/implementation-readiness-report-2026-10-14-run2.md`). Las fuentes de Plan-2 (`ux/`, `planning/prd.md`, `reviews/` de la raíz) no se editan en esta copia (AGENTS.md). Cada fila se sincroniza en su próximo ciclo; ninguna bloquea la implementación porque el contrato y el AC ya están definidos en este documento.

Owners: A = Juan Pablo Parra; B = Daniel Gonzalez.

| fuente:línea | texto | decisión | owner | acción de sincronización | estado |
|---|---|---|---|---|---|
| `ux/EXPERIENCE.md:45` | "Procesando registros: 78 / 120 (65%)…" como barra determinista por fila en tiempo real | R10-M1 (MODIFY): el estado Loading es progreso de subida en cliente + "Validando lote atómico…"; AD-02 (ingesta síncrona, atómica) | A — Juan Pablo Parra | actualizar EXPERIENCE.md en el próximo ciclo de UX (Freya/Sally) | SINCRONIZADA 2026-10-14 en la copia del workshop (Sally, K-4; nota [ACTUALIZADO] en línea; decision log 'K-4 cierre') |
| `planning/prd.md:179,189`; `ux/C-UX-Scenarios/scenario-3.md:32-33,52,68` | `STU-MATEO-99` para Mateo (PRD §4.3, scenario-3) frente a `STU-98432` (PRD §4.1 y §7, EXPERIENCE, scenario-1) | R8-08: ID canónico `STU-98432`; `STU-MATEO-99` se trata como el mismo actor; PRD no editado | A — Juan Pablo Parra | unificar el ID en PRD §4.3 y scenario-3 en el próximo ciclo de PRD/UX (Freya/Sally) | registrada, no bloqueante para implementación porque las historias usan `STU-98432` y el AC de E2-S1 no depende del alias |
| `ux/C-UX-Scenarios/scenario-1.md:83` | "tiempo total … para 120 estudiantes es inferior a 1.2 segundos" | R10-C2: umbral vinculante de FR-INGEST-01 = 120 filas < 2.0 s (`planning/prd.md:141`); 1.2 s es objetivo UX no vinculante, medido como stretch en `nfr-evidence.md` (DEFER) | B — Daniel Gonzalez | ajustar scenario-1 al umbral de 2.0 s como gate y 1.2 s como objetivo en el próximo ciclo de UX | SINCRONIZADA 2026-10-14 en la copia del workshop (Sally, K-4; nota [ACTUALIZADO] en línea; decision log 'K-4 cierre') |
| `planning/prd.md:296-297` (NFR-AUDIT-06, NFR-DISP-07); `planning/prd.md:236` (200 ms, 50k eventos); `planning/ARCHITECTURE.md` §1.1 (2.0 s / 120 MB) y `ux/C-UX-Scenarios/scenario-4.md` (200 ms) | Umbrales distintos para la misma métrica (consulta forense, boot y RAM) | R10-M5: gate NFR-AUDIT-06 = 100 000 eventos p95 < 500 ms; 50 000 < 200 ms es objetivo funcional separado; NFR-DISP-07 gate = boot < 5.0 s y RAM ≤ 512 MB; 2.0 s / 120 MB = objetivo. Ver tabla "Umbrales triageados" | B — Daniel Gonzalez (medición en G-16) | alinear los objetivos de ARCHITECTURE §1.1 en la próxima corrida de arquitectura, con excepción explícita porque AGENTS.md solo permite editar ARCHITECTURE para decisiones de stack | registrada, no bloqueante para implementación porque los AC citan solo el umbral gate; medición NFR pendiente (PLANNED) |
| `planning/ARCHITECTURE.md:97` frente a `planning/ARCHITECTURE.md:198` (snippet DDL) | Semilla génesis `e3b0c442…b855` en §4 frente a `DEFAULT '0000…0'` (64 ceros) en el snippet | R10-M2 (corrige H-15): génesis = `e3b0c442…b855`; epics E1-S3 (l.176 y l.191) ya usa la constante; corrección de l.198 registrada como K-1 en `ai-log/decision-log-solu2.md` | A — Juan Pablo Parra | confirmar que el snippet l.198 quedó alineado (K-1); los fixtures `"0" * 64` de `module1_guard_contracts.test.py` son filas de inserción y se revisan en `bmad-testarch-atdd` | CORREGIDA 2026-10-14 (K-1: ARCHITECTURE.md:198 alineada con l.97; confirmada en v2) |
| `planning/prd.md:159` (`PENDING_APPROVAL`) frente a `planning/detailed-design/contracts.md:138` (mensaje "ACTIVE/PENDING") | Vocabulario de estado de escalación | DDL `escalation_tickets.status` (`001_module1_schema.sql:100`) usa `PENDING_APPROVAL`, igual que el PRD; el mensaje de contracts.md:138 es la única desviación | A — Juan Pablo Parra | corregir contracts.md:138 en la próxima pasada de diseño (no editado en esta corrida); detalle en K-5, fila W-07 | registrada, no bloqueante para implementación porque el código de error (`CONCURRENT_ESCALATION_NOT_PERMITTED`) no cambia; solo el texto del mensaje |
| `planning/prd.md:305`, `planning/prd.md:358`, `planning/ARCHITECTURE.md:378` (`admin` o `department_chair`; "Instructors" aprueban) | Rol del Dr. Marcus Vance (CS Department Chair) y de instructores; el DDL tiene `instructor_privileged`, `admin`, `auditor`, `student`, `ta` | R6-Q1: el Department Chair se aprovisiona con rol institucional `admin` en el adapter de identidad simulado; R2-01: nombres de rol = `roles.id` exactos del DDL (`001_module1_schema.sql:55`). Los instructores no aprueban escalaciones en Módulo 1 | A — Juan Pablo Parra | mapear "department_chair" a `admin` y "Instructor" a `instructor_privileged` en el próximo ciclo de PRD/ARCHITECTURE | registrada, no bloqueante para implementación porque el llamador de revoke e ingest es `admin` por contrato (ADVF-01) |
| `planning/prd.md:323` (Colisión Tipo A: "aborta … si la bandera es `STRICT`" y "Quarantine List") frente a AD-02 (atomicidad por lote) | Cuarentena o aborto total ante una colisión de identidad en la nómina | R3-04: STRICT = abortar el lote completo (rollback total, 422 con manifiesto); no existe modo de cuarentena parcial (AD-02 manda sobre la frase ambigua del PRD §7.2) | A — Juan Pablo Parra | aclarar PRD §7.2 Colisión A en el próximo ciclo de PRD (rollback, no cuarentena) | registrada, no bloqueante para implementación porque E3-S2 prueba el rollback total con fila 85 |

---

## Triage de hallazgos previos (Plan-2 + Solu-2)

Consolida K-5 del readiness gate corrida 2 (chequeo 6: triage visible). Disposiciones: ACCEPT = gap real con resolución visible; DEFER = operativo, NFR o fuera de las tres operaciones, con owner y fase; REJECT = sugerencia concreta superada por una decisión ya tomada (criterio aprobado; el riesgo de fondo no se niega, como en `review-detailed-design.md`). Cuando el informe ya traía disposición, se conserva; cuando no, se asignó con los criterios aprobados. "ACCEPT — PENDIENTE" = aceptado y no visible en el artefacto; se reporta, no se corrige aquí. Tras la Ronda 11 (2026-10-14) no queda ningún hallazgo en estado ACCEPT — PENDIENTE. Owners confirmados por el estudiante A (2026-10-14): A — Juan Pablo Parra (arquitectura, contratos, UX); B — Daniel Gonzalez (TEA, NFR).

Owners: A = Juan Pablo Parra; B = Daniel Gonzalez. Los roles de origen (Architect-lead, Test-lead) se mapean a A (arquitectura y alcance) y B (pruebas y NFR); mapeo por confirmar.

| ID | fuente (archivo) | hallazgo | disposición | dónde quedó resuelto (artefacto/sección o historia/AC) | owner |
|---|---|---|---|---|---|
| AR-01 | `planning/detailed-design/reviews/review-arch-implementability.md` | Firma de `resolveEffectivePermissions` sin mapeo canónico al endpoint | ACCEPT | contracts.md §0 (mapeo 1:1, AD-09); openapi `/authorize`; E1-S2 | A |
| AR-02 | idem | `revokeCourseAccess`: tres rutas y repetición incompletas | ACCEPT | contracts.md §2 (Q1, Repetición, I1); ports §5 (`drop`); E2-S3 | A |
| AR-03 | idem | `ingestRoster`: esquema y orden validación/transacción incompletos | ACCEPT | contracts.md §3 (P2 límites, I1, R3-04); openapi `RosterIngestRequest` (1-1000 filas); E3-S1..E3-S4 | A y B |
| AR-04 | idem | Edge de estudiante sin GPU frente a cuota de otro módulo | ACCEPT | [ASSUMPTION-01] (sección "Lista de [ASSUMPTION]"); E4-S1; R8-06 | A |
| AR-05 | idem | Estados UX y `reason_code` sin DTO/catálogo cerrado | ACCEPT | dto.py (`ErrorCode`, `ExplanationDTO`, `DenyBody`); contracts.md §4; "Tabla de Estados UX" (sección `## Tabla de Estados UX -> contrato + DTO`) | A y B |
| AR-06 | idem | Normalización de `course_id`/ARN y comparación AD-01 | ACCEPT | Normalizador no adoptado: comparación byte a byte (ADVF-10 → E4-S3, T-RES-10); contracts.md §0 | A |
| AR-07 | idem | Borde temporal de privilegios escalados | ACCEPT | contracts.md §1 (Tiempo, `[granted_at, expires_at)`), H-21; DDL `001_module1_schema.sql:104-106`; E4-S2 | A y B |
| AR-08 | idem | Errores con códigos/status inconsistentes | ACCEPT | contracts.md §4 (catálogo), R3-01, R3-02, R4-02; openapi `ErrorBody.code` enum; dto.py `ErrorCode` | A |
| AR-09 | idem | Atomicidad, idempotencia y carrera resolver↔revocar | ACCEPT | contracts.md §2 Q2 (`BEGIN IMMEDIATE`, R3-06) y §1 Concurrencia (H-22); E2-S3; E1-S2 | A y B |
| AR-10 | idem | Transiciones de estado incompletas fuera del alcance de las tres operaciones | ACCEPT | Alcance acotado: `COMPLETED` → DENY (Pendientes Gate 5); `INACTIVE`/`EXPIRED` en "Fuera de alcance" (ASSUMPTION-03); ver W-07 | A |
| AR-11 | idem | Stack y metas NFR incompatibles | ACCEPT | Stack confirmado (AGENTS.md, 2026-10-12); umbrales R10-C2 y R10-M5 (l.595-604); NFR PLANNED | A y B |
| AR-12 | idem | Personas y URN de fixtures distintas; caso obligatorio no determinista | ACCEPT | E4-S1 (seed Student en CS101 + TA en CS-480); E1-S1 (fixtures); R8-08 (`STU-98432`) | B |
| AR-13 | idem | Fórmula y orden del ledger; enmascaramiento | ACCEPT | AD-04 §5 normativo; H-14 (8 campos); contracts.md §5 (codec) | A |
| AR-14 | idem | Estados UX sin contrato; escalación y deep-link fuera de las tres operaciones | ACCEPT (común); DEFER (flujo ajeno) | "Tabla de Estados UX" (sección `## Tabla de Estados UX -> contrato + DTO`); "Fuera de alcance" (l.867-889) | A y B |
| EC-01 | `review-arch-implementability.md` | `resolve` concurrente con `revoke` y caché obsoleta | ACCEPT | H-22 (DB autoridad; caché solo adelanta DENY); E2-S2 (T-CON-01); ADVF-05 | A y B |
| EC-02 | idem | JSON propone Mateo Student en CS101 y CS-480 | REJECT | Error del reviewer: el seed es Student en CS101 y TA en CS-480 (AD-10); E4-S1 prueba independencia de contexto | B |
| EC-03 | idem | `at == expires_at` para privilegio escalado | ACCEPT | contracts.md §1 (`[granted_at, expires_at)`), H-21; E4-S2 (vence en el instante exacto) | A y B |
| EC-04 | idem | `at` ausente, malformado, futuro o sin zona | ACCEPT (validación); DEFER (visibilidad externa) | ADVF-09 y ECF-14: `at` null → `INVALID_AT` (E4-S4, T-RES-P-04); visibilidad externa fuera de alcance (PRD §2.2) | A |
| EC-05 | idem | `userId` como UUID, `institutional_id` o alias | ACCEPT | contracts.md §0 (resolución en adapter, decisión ADOPTED 2026-10-13); E1-S2 | A |
| EC-06 | idem | Variantes `CS-480`/`cs-480` y `CS101`/`cs101` | ACCEPT | ADVF-10: comparación byte a byte; `cs-480` → 404 `UNKNOWN_COURSE` (E4-S3, G-5/G-6) | B |
| EC-07 | idem | ARN malformado o reordenado; consecuencia de path traversal | ACCEPT (parser); traversal RECHAZADA como consecuencia | openapi `/authorize` pattern AD-01; DDL l.162 (GLOB aproximado); E4-S3 (`test_arn_grammar_rejects`, `.` y `/` → 400 `MALFORMED_RESOURCE_ARN`) | B |
| EC-08 | idem | Resolver sin contexto o sin materias | ACCEPT | E1-S2 (T-RES-11, Empty caso D, DenyBody `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`); ADVF-08 | B |
| EC-09 | idem | Identidad global `SUSPENDED`/`EXPELLED` con membresía activa | ACCEPT | H-17 y F-03 (orden 403: `IDENTITY_BARRED` primero); E4-S3 (G-4) | A y B |
| EC-10 | idem | Repetir `revokeCourseAccess` sobre `DROPPED` | ACCEPT | F-01; contracts.md §2 Repetición (200 `ALREADY_REVOKED` sin evento); E2-S3 | B |
| EC-11 | idem | Revocar usuario o curso inexistente, o membresía no activa | ACCEPT | contracts.md §4 (`MEMBERSHIP_NOT_FOUND` 404, `INVALID_TRANSITION` 409); E2-S5 | B |
| EC-12 | idem | Varias credenciales activas para la misma membresía | ACCEPT | contracts.md §2 Q2 (todas las `ACTIVE` del par, misma transacción); E2-S1 (`test_revoke_all_credentials`) | A y B |
| EC-13 | idem | Crash entre DB, caché y auditoría | ACCEPT (reformulado) | R3-06 y ports §4 (ledger en la misma transacción; sin caché mutable, H-22); capacidad de cola DEFER a Fase 3 NFR | A y B |
| EC-14 | idem | Fila inválida o duplicada en lote; manifiesto ausente | ACCEPT | contracts.md §3 I1 (rollback total, `test_roster_row85_rollback`), R3-04; E3-S2 | A y B |
| EC-15 | idem | Lote vacío, >5 MB, >1000 filas, nulos, reingesta | ACCEPT | ECF-01 (413 antes de validar), ECF-02 (`BATCH_EMPTY`) en E3-S4; contracts.md §3 nota de reingesta (ADOPTED) | B |
| EC-16 | idem | `BEGIN IMMEDIATE` compite con 100 req/s | ACCEPT | contracts.md §1 Concurrencia (lectores snapshot, fail-closed 503, H-22); medición NFR-PERF-01 PLANNED (G-16, pendiente de benchmark) | B |
| D-01 | `planning/detailed-design/reviews/review-agent-dev.md` | `POST /authorize` admite 200 con DENY y a la vez 403 | REJECT | Superado por R9-05 (DENY es resultado; 403 lo mapea el adapter). openapi: 200 = ALLOW; DENY → `403 DenyBody` | A |
| D-02 | idem | El 403 no lleva `ExplanationDTO` (AD-11) | REJECT | Superado por R9-05 y R6b-03: `DenyBody` con `explanation` (dto.py l.192-198) | A |
| D-03 | idem | CHECK de gramática ARN citado en ports §5 y ausente en SQL | ACCEPT | DDL l.162 `CHECK (resource_arn GLOB 'urn:uai:subject:*:model:*')` (aproximación documentada) + guarda de dominio (E4-S3) | B |
| D-04 | idem | `CHECK(term GLOB '[0-9]{4}-*')` acepta `2026-XXX` | ACCEPT | DDL l.41-44 y l.69-71 (`SPRING\|SUMMER\|FALL`) | A |
| D-05 | idem | `audit_events` como VIEW frente a TABLA exigida por la consigna | REJECT | Superado por R3-06 (append-only sobre `audit_ledger` y `audit_events`); DDL l.245 `CREATE TABLE audit_events` | A |
| D-06 | idem | `AUDIT_LOG_TAMPERING_DETECTED` 500 sin respuesta en OpenAPI | REJECT | Superado por F-06 (envelope `ErrorBody`); openapi `Internal` (500) en l.55 y l.503 | A |
| D-07 | idem | `ErrorBody.code: str` libre frente a enum cerrado de 24 | ACCEPT | dto.py `ErrorCode = Literal[...]` (l.66) y enum de openapi | B |
| D-08 | idem | `nullable: true` en OpenAPI 3.1 | ACCEPT | openapi sin `nullable` (0 ocurrencias verificadas); editorial | B |
| D-09 | idem | `RosterRejectedManifestRow` sin `$ref` en OpenAPI | ACCEPT | openapi `RosterRejectedManifest` (l.395-430) y 422 con `$ref` (l.502) | A |
| D-10 | idem | Claves de receipt de revoke divergentes | ACCEPT | contracts.md §2 (Q1 y Repetición usan `revocation_propagated_at`); openapi `RevokeResponse` (l.252) | A |
| D-11 | idem | Tabla contracts §5 sin filas AD-07, AD-08, AD-09 | ACCEPT | contracts.md §5 (l.171-172 y l.182) | B |
| D-12 | idem | Tres abiertos presentados como cerrados en companions | REJECT | Superado por decisiones ADOPTED: H-22 (DB autoridad), scheduler (contracts.md §1 Tiempo), ADVF-10 (byte a byte) | A |
| D-13 | idem | Predicado single-statement del revoke sin línea exacta | REJECT | Superado por R3-06 (orden exacto; `UPDATE … WHERE status='ACTIVE' RETURNING`, contracts.md §2 Q2 y ports §5) | B |
| D-14 | idem | `reason_code` sin `SUCCESS` y `CHECK(ALLOW,DENY)` | REJECT | Superado por R3-03 y ADVF-04 (`roster.ingested` = ALLOW/SUCCESS; rechazo = DENY); DDL l.170-176 | A |
| D-15 | idem | Transporte dual de `term` (query CSV y body JSON) | ACCEPT | dto.py l.238-239 (canal exclusivo, `MALFORMED_TERM`); contracts.md §3 P1 (N-03, gate 3) | A |
| D-16 | idem | Conforme: boundaries, `Clock`/`IdGenerator`, simulación | sin hallazgo | no requiere disposición | — |
| W-01 | `planning/detailed-design/reviews/review-agent-architect.md` | `strip+upper` frente a byte a byte (AD-01) | REJECT | Superado por ADVF-10 (byte a byte) y H-24; contracts.md §0 | A |
| W-02 | idem | Catálogo sin código de éxito; `CHECK(ALLOW,DENY)` | REJECT | Superado por ADVF-04 y R3-03; contracts.md §4 (nota SUCCESS); DDL l.170-176 | A |
| W-03 | idem | Ledger sync o async; bound de cola; fail-closed | REJECT | Superado por R3-06 (`QueueReservation`, sin reserva → 503) y Pendientes Gate 5; capacidad numérica DEFER (ver W-15) | A |
| W-04 | idem | Caché de revocación frente a DB autoridad | REJECT | Superado por H-22 (la caché solo puede adelantar un DENY) | A |
| W-05 | idem | Scheduler frente a expiración perezosa | REJECT | Superado por la decisión de scheduler (Pendientes Gate 5, barrido 1 s) y contracts.md §1 Tiempo | A |
| W-06 | idem | Sin 401 ni validación de token | REJECT | Superado por R3-01 (`AUTH_TOKEN_INVALID` 401) y ADVF-02 (`TokenVerifierPort`) | A |
| W-07 | idem | Vocabulario incompleto: `INACTIVE`, `EXPIRED`, `COMPLETED`, `PENDING_APPROVAL` frente a `PENDING` | ACCEPT | `COMPLETED` → DENY (Pendientes Gate 5); `INACTIVE`/`EXPIRED` fuera de alcance (ASSUMPTION-03). PENDIENTE: contracts.md:138 usa "PENDING" y DDL l.100 y PRD l.159 usan `PENDING_APPROVAL` | A | Resuelto en Ronda 11: contracts.md §4 usa `PENDING_APPROVAL` (2026-10-14).
| W-08 | idem | Tabla §5 sin AD-07, AD-08, AD-09 | ACCEPT | contracts.md §5 (l.171-172 y l.182); mismo cambio que D-11 | B |
| W-09 | idem | Nombres de path-params, cuerpo del drop, transporte de `at` y `term` | REJECT | Superado por F-05 (`timestamp` en body), H-18 (decode-once de `term`) y regla de canal único (dto.py l.238) | A |
| W-10 | idem | STRICT frente a aborto total; rol divergente; manifiesto (cuarentena frente a rollback) | REJECT | Superado por R3-04 (STRICT = abortar lote, rollback, 422) y H-20 (anti-smuggling, 422) | A |
| W-11 | idem | Gramáticas exactas por campo (email, `institutional_id`, ARN, `term`, `at`) | REJECT | Superado por R4-01 y G9-01 (`timestamp`), ADVF-21 (`institutional_id`), ECF-07 (dominio de email), AD-01 (openapi l.189) | A |
| W-12 | idem | `ExplanationDTO` sin schema por operación; E-01..E-04 sin campo de acción | DEFER | Schema resuelto por R6b-03, R8-02 y dto.py (l.124-133, `DenyBody`). Campo de acción sugerida sin decisión: Fase 4 de UX, fuera del contrato de las tres operaciones | A |
| W-13 | idem | Orden validación→transacción→ledger; `SQLITE_BUSY`; predicado | REJECT | Superado por R3-06 (orden), H-22 (snapshot lector, `busy_timeout` 5000) y contracts.md §3 Concurrencia | B |
| W-14 | idem | Reingesta no idempotente; claves de receipt de `ALREADY_REVOKED` | REJECT | Superado por la nota de reingesta ADOPTED (contracts.md §3, sin idempotencia por contenido) y D-10 | A |
| W-15 | idem | NFR PLANNED; contradicciones de dataset y concurrencia | DEFER | NFR de medición Fase 3 (G-16, owner B); umbrales decididos en R10-C2 y R10-M5 (l.595-604) | B |
| W-16 | idem | Fórmula del hash con dos variantes; `reason_code` del ledger | REJECT | Superado por H-14 (fórmula AD-04 §5, 8 campos) y AR-13 | A |
| ARCH-EDGE-03 | `reviews/review-arch-edge-cases.md` (raíz, Plan-2) | Retroceso de reloj NTP | DEFER | Post-V1; guardia monotónica en ARCHITECTURE-SPINE l.133; "Fuera de alcance" (migración y guardia NTP) | A y B (fase: Post-V1) |
| ADV-MIN-01 | `reviews/review-prd-adversarial.md` (raíz, Plan-2) | Castigo de 1 h volátil tras intento de auto-aprobación | DEFER | Escalación fuera de alcance (FR-ESCAL-02); respaldo DDL `approved_by <> requester_id` (l.117); "Fuera de alcance" (crear y aprobar escalaciones) | A (fase: Post-V1) |
| ADV-MIN-03 | idem | Barrido de membresías de fin de semestre (ASSUMPTION-03) | DEFER | "Lista de [ASSUMPTION]" (ASSUMPTION-03) y "Fuera de alcance" (barrido `INACTIVE`) | A (fase: Post-V1) |
| ARCH-ADV-CRIT-01 | `reviews/review-arch-adversarial.md` (raíz, Plan-2) | Divergencia de `revoked_credentials_cache` entre workers Uvicorn | ACCEPT | Proceso único `workers: 1` + SQLite WAL: ARCHITECTURE-SPINE l.83 (AD-03 heredado); DDL `001_module1_schema.sql` l.61; `planning/ARCHITECTURE.md` (raíz) AD-03 regla 2 | A |
| ARCH-ADV-CRIT-02 | idem | Truncamiento de cola (*tail truncation*) del ledger | ACCEPT | Singleton `audit_ledger_metadata (id = 1)` en DDL `001_module1_schema.sql` l.187-209; contracts.md §5 ("Hash encadenado + metadata singleton"); `planning/ARCHITECTURE.md` (raíz) AD-04 regla 2 | A |
| ARCH-ADV-MAJ-01 | idem | `SQLITE_BUSY` por escrituras síncronas de auditoría a 100 req/s | ACCEPT | Cola `asyncio.Queue` con micro-batching 50 ms/50 ev: ports-and-adapters.md l.40 (`adapters/ledger_writer`), DDL l.240; `busy_timeout` 5000 en ARCHITECTURE-SPINE l.47; AD-04 regla 3 (raíz) | A |
| ARCH-ADV-MAJ-02 | idem | Escalación horizontal por *role smuggling* en ingesta de nómina | ACCEPT | contracts.md §3 "Anti-role-smuggling" (H-20) e I2, test `test_roster_no_role_smuggling`; contracts.md §5 l.159; AD-02 regla 3 (raíz) | A |
| ARCH-ADV-MIN-01 | idem | Path traversal sintáctico en ARN (`.` y `/`) | ACCEPT | Regex exacta `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$`: contracts.md §0 P4 (`MALFORMED_RESOURCE_ARN` 400), openapi `/authorize` pattern (l.189), DDL l.166; AD-01 regla (raíz) | B |
| ARCH-EDGE-01 | `reviews/review-arch-edge-cases.md` (raíz, Plan-2) | Doble envío de solicitud de escalación (carrera) | ACCEPT | Índice único parcial `idx_single_active_escalation` en DDL `001_module1_schema.sql` l.127-129; AD-05 regla 1 (raíz); contracts.md §5 l.165 (respaldo; escalación fuera de las tres ops) | A y B |
| ARCH-EDGE-02 | idem | Colisión de timestamps en `audit_ledger` a 100 req/s | ACCEPT | Precisión de microsegundos: DDL `001_module1_schema.sql` (GLOB de 6 decimales); AD-04 regla 1. Orden primario por `id`: `schemas/events.md` l.138 y l.143 (aceptación FIFO, persistencia secuencial, `id ASC` define el hash y la verificación) | A |
| ARCH-EDGE-04 | idem | Duplicado intra-lote en CSV de nómina | ACCEPT | `seen_ids` en stream: contracts.md §3 P4 y catálogo l.140 (`INTRA_BATCH_DUPLICATE_ID` 422); test `test_roster_intra_batch_duplicate` (contracts.md §5 l.160); AD-02 regla 1 (raíz) | A y B |
| ARCH-EDGE-05 | idem | Reintento de notificación de baja (*course drop*) | ACCEPT | `ALREADY_REVOKED` 200 sin evento: contracts.md §2 "Repetición" (l.76); openapi `RevokeResponse` enum (l.260); AD-03 regla 1 (raíz) | B |
| ADV-CRIT-01 | `reviews/review-prd-adversarial.md` (raíz, Plan-2) | "Confused deputy": recurso no vinculado a la materia del contexto | ACCEPT | PRD raíz §5.2 paso 3.1 y l.279 (Resource-Subject Binding); contracts.md §0 P5 (comparación byte a byte `resource.subject == courseId`) | A |
| ADV-CRIT-02 | idem | Revocación de API keys estáticas tras *course drop* | ACCEPT | PRD raíz l.185 (`subject_credentials` → `REVOKED`); contracts.md §2 Q2 (todas las `ACTIVE` del par → `REVOKED` en la misma transacción); índice `idx_credentials_lookup` (ARCHITECTURE raíz) | A |
| ADV-MAJ-01 | idem | Código `TIER_VRAM_EXCEEDED_FOR_ROLE` (scope creep al Módulo 2) | ACCEPT | PRD raíz l.228 (`UNAUTHORIZED_RESOURCE_CLASS`, sin VRAM); contracts.md §0 regla 7 (l.42) y §4 l.133 | A |
| ADV-MAJ-02 | idem | Solicitudes de escalación concurrentes o solapadas | ACCEPT | PRD raíz l.161 (409 `CONCURRENT_ESCALATION_NOT_PERMITTED`); contracts.md §4 l.138; DDL `idx_single_active_escalation` l.127-129. Escalación fuera de las tres ops | A |
| ADV-MAJ-03 | idem | Ingesta reactiva identidades `SUSPENDED` o `EXPELLED` | ACCEPT | PRD raíz l.134 (rechazo y manifiesto de cuarentena `roster_rejected_conflicts.csv`); contracts.md §4 `IDENTITY_BARRED` l.132 (rule_id de 422 en ingesta) | A |
| ADV-MAJ-04 | idem | Discrepancia 200 ms local frente a 60 s perimetral | ACCEPT | PRD raíz l.293 (NFR-REVOC-03: `T_local` < 200 ms; `T_revoc` < 60 s con caché HTTP perimetral); ARCHITECTURE-SPINE l.83 (< 200 ms) | A |
| ADV-MIN-02 | idem | `page_size` sin tope en auditoría | ACCEPT | PRD raíz l.210 (1 a 100; truncado a 100); AD-07 (raíz); contracts.md §4 l.144 (forzado al rango) | A |
| EDGE-UX-01 | `reviews/review-ux-edge-cases.md` (raíz, Plan-2) | Identidad con cero asignaturas (`subjects.length === 0`) | ACCEPT | `ux/EXPERIENCE.md` §2.2 Caso D (l.74); DenyBody `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (contracts.md §0 P5); UX-DR9 y E1-S2 | A |
| EDGE-UX-02 | idem | Sin banner ni estado ante rechazo formal de escalación | ACCEPT | `ux/EXPERIENCE.md` §3.2 Banner E-04 (l.191); `ux/C-UX-Scenarios/scenario-2.md` componente 4 y prueba §3. Escalación fuera de las tres ops (epics l.701) | A |
| EDGE-UX-03 | idem | Expiración de sesión durante consulta forense masiva | ACCEPT | `ux/EXPERIENCE.md` §2.5 (l.114); UX-DR10 (epics l.83). Consulta forense fuera de alcance (epics l.695, l.894) | B |
| EDGE-UX-04 | idem | Enlace profundo desalineado con `X-Academic-Subject-Context` | ACCEPT | `ux/DESIGN.md` l.30-31 (sincronización URL ↔ encabezado) | A |
| EDGE-UX-05 | idem | ARN largo desborda la celda en 1024 px | ACCEPT | `ux/DESIGN.md` l.169-180 (`.cell-arn-truncate`); solo UI, sin efecto en las tres ops | A |
| SEC M-01 | `planning/detailed-design/architecture-spine/reviews/review-security.md` | Ventana de revocación perimetral de hasta 60 s | DEFER | Dentro del módulo el corte es inmediato: la DB es la autoridad y `resolve` lee tras el commit (H-22; `test_resolve_after_revoke_commit_denies_enrollment_dropped`, T-RES-03). Los < 60 s de NFR-REVOC-03 aplican a proxies externos; medición PLANNED en `test/nfr-evidence.md` (R12) | A (integración perimetral) |
| SEC M-02 | idem | Canonicalización de `userId` / `institutional_id` | ACCEPT | contracts.md §0: `institutional_id` case-sensitive exacto con `^[A-Za-z0-9-]{1,64}$` (Q7), UUID canónico 8-4-4-4-12, `courseId` byte a byte; test `test_ingest_institutional_id_case_distinct_identity` (R12) | A |
| SEC M-03 | idem | Forense de lote rechazado y cola sin bound | ACCEPT | `roster.rejected` en la misma cadena tras rollback (R3/H-16); cola llena → 503 sin descarte (AD-12, `QueueReservation`); tests `test_roster_rejected_occurred_at_reuses_single_request_now`, T-ROS-13. Capacidad numérica: DEFER NFR | A; capacidad numérica B |
| SEC B-01 | idem | Fallo de `Clock` / `IdGenerator` / `LedgerWriter` en `resolve` (y en ingest) | ACCEPT (R12-B01, nueva decisión) | contracts.md §1, §2 y §3 Q-fail (503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` fail-closed; `LedgerWriter`/cola en contracts.md §4 l.141 y QueueReservation); ports-and-adapters.md §1 (modos de fallo, l.53); RED: T-RES-15 (E1-S2) y T-ROS-21 (E3-S1); T-REV-12 (E2-S3) | A |
| SEC B-02 | idem | Enumeración por códigos diferenciales y `observed_*` | REJECT (riesgo residual aceptado) | PRD y catálogo exigen 404/403 distintos y explicabilidad con valores observados (restricción 4 de Plan-2); mitigado: 401 primero (R9-00) y `observed_*` solo del contexto solicitado | A |
| CONS-1 (ítem 1 del veredicto) | `planning/detailed-design/architecture-spine/reviews/review-consistency.md` | Caché vs DB como autoridad | REJECT — superado | H-22: snapshot de lectura; `revoked_credentials_cache` solo adelanta DENY | A |
| CONS-2 (ítem 2 del veredicto) | idem | Scheduler vs expiración perezosa | REJECT — superado | Scheduler 1 s + reconciliación (G6-02) | A |
| CONS-3 (ítem 3 del veredicto) | idem | Catálogo sin `SUCCESS` | REJECT — superado | `SUCCESS` documentado en contracts (Fase 1, R1–R11) y mapeo ledger R3-03/ADVF-04 | A |
| CONS-4 (ítem 4 del veredicto) | idem | Mandatory Edge Case | ACCEPT — conforme | AD-10, E4-S1, tests `TestEdge01` | A |
| CONS-5 (ítem 5 del veredicto) | idem | Binding sin AD-07/08/09 | ACCEPT — resuelto | contracts §5 + tabla AD regenerada (K-6) | A |

### Triage por resumen (artefactos con tabla propia o gates)

| ID | fuente (archivo) | hallazgo | disposición | dónde quedó resuelto | owner |
|---|---|---|---|---|---|
| RDD-1 | `planning/detailed-design/reviews/review-detailed-design.md` (tabla propia: ADVD-01..14 y EC-01..34) | 48 filas: 35 ACCEPT (3 parciales), 10 DEFER (2 parciales), 3 REJECT (ADVD-13 y ADVD-14 parciales; EC-13) | ya triageada en su documento (conteo; no se re-triagea fila a fila) | Aplicación de los ACCEPT en artefactos según Rondas 1–6 del paquete; verificado por muestreo en D-xx | A y B |
| RDD-2 | idem (sección "Revisión final 2026-10-13", ADVF-01..25 y ECF-01..30) | 55 hallazgos: 42 ACCEPT, 6 DEFER, 7 REJECT | tabla "ACCEPT del review final" (l.738-789) y Rondas 6 y 6b | "Accepted → visibly fixed" (Ronda 6); ECF-24 pasa a ACCEPT (R6b-02) | A y B |

| Gate | fuente (archivo, `architecture-spine/reviews/`) | hallazgo (resumen) | disposición | dónde quedó resuelto (ronda del paquete) | owner |
|---|---|---|---|---|---|
| Gate 1 | `validation-gate-20261013.md` (NO PASS) | 3 `low` del lint: falsos positivos por placeholders `{subject_id}`/`{student_id}` (AD-09, l.65); resto de lentes sin hallazgo propio | REJECT (lint); resto por Gates 2–4 | falsos positivos documentados en `review-lint-20261013.md` | A |
| Gate 2 | `validation-gate-20261013-2.md` (NO PASS) | 8 decisiones D1–D8 ADOPTED; 4 observaciones de rubric (`updated`, `[OPEN-01]` residual, plantilla `INVALID_AT`, separador de evento) | ACCEPT | sin ronda propia en el paquete; `updated: 2026-10-14` (spine l.10); plantilla `INVALID_AT` corregida en Gate 3 | A |
| Gate 3 | `validation-gate-20261013-3.md` (NO PASS) | N-01..N-16 ADOPTED; rubric H-1..H-11 | ACCEPT | H-1 → ADVF-12 y N-03; H-2 → DDL l.176 (P1–P4 sin evento); H-3 → contracts.md l.75; H-4 → F-02 y R2-01; H-5 → R3-06 y Pendientes Gate 5. PENDIENTE: H-10 (gramática del local-part del email, no fijada en contracts ni spine); H-11 (`roster:ingest` en contracts.md:97 frente a `roster.ingested` en events.md:82) | A y B | H-10 y H-11 resueltos en Ronda 11: contracts.md §3 P3 (gramática de parte local del email) y §3 Q3 (`roster.ingested`).
| Gate 4 | `validation-gate-20261013-4.md` (NO PASS) | F-01..F-06 y H-14..H-26; corrección `at` y R1–R11 | ACCEPT | Ronda 1 (paquete F/H, 2026-10-13); 19/19 verificados en Gate 6 | A |
| Gate 5 | `validation-gate-20261013-5.md` (NO PASS por diseño) | sync Fase 2 de Amelia: D-01..D-15 | ver filas D-01..D-15 (8 ACCEPT, 7 REJECT); lint `low` = falsos positivos (REJECT) | Pendientes Gate 5 (scheduler, `COMPLETED`, cola, `batch_id`, TTL) | A y B |
| Gate 6 | `validation-gate-20261013-6.md` (CONDITIONAL) | paquete F/H aplicado; G6-01 y G6-02 nuevos | ACCEPT | Ronda 2: G6-01 (DDL l.106 `revoked_at`), G6-02 (events.md l.125 reconciliación), R2-01 (roles = `roles.id`) | A |
| Gate 7 | `validation-gate-20261013-7.md` (CONDITIONAL) | cierres Ronda 2 (3/3); observaciones G7-01 y G7-02 | G7-01 REJECT; G7-02 DEFER (Fase 3 NFR, B) | Ronda 3 (G7-01, G7-02) | A y B |
| Gate 8 | `validation-gate-20261013-8.md` (CONDITIONAL) | cierres Ronda 3 (8/8); R4-01 y R4-02 nuevos | ACCEPT | Ronda 3 (R3-01..R3-06); Ronda 4 (R4-01, R4-02) | A |
| Gate 9 | `validation-gate-20261013-9.md` (CONDITIONAL) | R4 aplicadas; G9-01..G9-06 (bloqueantes G9-01..G9-03) | G9-01..G9-04 ACCEPT; G9-05 REJECT; G9-06 DEFER | Ronda 5 (última ronda de arquitectura) | A |
