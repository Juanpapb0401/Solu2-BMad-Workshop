---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-test-strategy', 'step-04-generate-tests', 'step-05-validate-and-complete', 'ronda-6-edit']
lastStep: 'step-05-validate-and-complete'
workflowType: 'testarch-atdd'
storyId: 'module1-contracts'
storyKey: 'module1-contracts'
storyFile: 'planning/detailed-design/contracts.md'
atddChecklistPath: 'solu2-module1/test/atdd-checklist.md'
generatedTestFiles:
  - 'test/atdd/module1_contracts.test.py'
  - 'test/atdd/module1_resolve_contracts.test.py'
  - 'test/atdd/module1_revoke_contracts.test.py'
  - 'test/atdd/module1_ingest_contracts.test.py'
  - 'test/atdd/module1_ingest_rules_contracts.test.py'
  - 'test/atdd/module1_guard_contracts.test.py'
  - 'test/atdd/atdd_support.py'
inputDocuments:
  - 'planning/detailed-design/contracts.md'
  - 'planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md'
  - 'planning/detailed-design/ports-and-adapters.md'
  - 'planning/detailed-design/schemas/001_module1_schema.sql'
  - 'planning/detailed-design/schemas/dto.py'
  - 'planning/detailed-design/schemas/roles_matrix.v0.json'
  - 'test/test-design.md'
  - 'test/conftest.py'
---

# Checklist ATDD (RED) — Módulo 1 de Solu-2 (User, Role, and Subject Access Manager)

**Fecha:** 2026-10-14 (edición Ronda 6 + Ronda 6b; las decisiones conservan la fecha en que se tomaron)
**Autor:** Estudiante (TEA: Murat, Master Test Architect)
**Modo:** Edit sobre la suite RED existente, fase RED (solutioning). Sin lógica productiva.
**Operaciones (Annex A p.13):** `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)`.
**Mandatory Edge Case (EDGE-01):** "Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently".

---

## Resumen

- **Suite (Ronda 13, vigente):** 130 atdd-red (`xfail` estricto; 127 de Ronda 11 + 2 nodos R12-B01 T-RES-15 y T-ROS-21 + 1 nodo R12-B01 T-REV-12 en Ronda 13) + 21 guardas + 4 de harness = **155 nodos**. `pytest -q` → 25 passed, 130 xfailed. `pytest -q --runxfail -m atdd` → 130 fallos con `NotImplementedError`. Detalle en "Cambios de esta edición (Ronda 12)".
- **Suite (Ronda 11):** 127 atdd-red (`xfail` estricto; 116 de Ronda 10 + 9 nodos nuevos de los huecos ADOPTED sin test) + 21 guardas (12 previas + 9 nuevas) + 4 de harness = **152 nodos**. `pytest -q` → 25 passed, 127 xfailed. `pytest -q --runxfail -m atdd` → 127/127 con `NotImplementedError`. Gate local: PASS=7 FAIL=0. Detalle en "Cambios de esta edición (Ronda 11)".
- **Suite (Ronda 10):** 116 atdd-red (`xfail` estricto, `raises=NotImplementedError`; 93 previos + 23 nuevos de gap-fill) + 12 guardas en verde (las 11 previas + T-SEED-GUARD-01) + 4 tests de harness. Detalle en "Cambios de esta edición (Ronda 10)".
- **Suite (previa, Ronda 6):** 93 atdd-red (`xfail` estricto, `raises=NotImplementedError`) + 11 guardas en verde (DDL: 4 append-only, AD-05 auto-aprobación R9-02, formato de timestamp de ledger R9-04, unicidad de membresía por term, unicidad de escalación AD-05, formato de timestamp, índice NFR-AUDIT-06; pureza AD-08; 3 guardas de 401 por composición) + 4 tests de harness.
- **Colección (vigente, Ronda 13):** `pytest --collect-only -q` → 155 tests (130 atdd, 21 guard, 4 harness), 0 errores de colección. La cifra de 132 de Ronda 10 queda como historia.
- **Ejecución (vigente, Ronda 13):** `pytest -q` → 25 passed, 130 xfailed. `pytest -q --runxfail -m atdd` → 130/130 fallan, todas con `NotImplementedError` ("stub, pendiente ATDD"). Histórico Ronda 10: 16 passed, 116 xfailed.
- **Gate local:** `scripts/quality_gate.sh` → `GATE LOCAL: VERDE` (etapas 1–7 OK; etapa 8 cobertura 65% es informativa).
- **Estado de readiness:** NO PASS. Este checklist no declara PASS de ningún gate ni marca NFR como EVIDENCED.

## Cambios de esta edición (Ronda 13)

Hallazgo K-16 del readiness corrida 5 (R12-B01 aplicado a `revokeCourseAccess`, contracts §2 Q-fail; antes "DEFER a TEA").

- **Nuevo RED (fila 123):** T-REV-12 `test_revoke_clock_failure_503_fail_closed_no_mutation` (E2-S3). Fake `RaisingClock` (`test/fakes/fake_failing_ports.py`). Aserciones: 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE`, membresía `ACTIVE`, credenciales sin cambio, conteos idénticos, cero eventos.
- **Conteos:** revokeCourseAccess I 8 -> 9 (total 22 -> 23); totales I 36 -> 37 y total 97 -> 98.
- Sin cambios en `app/`. Verificado: el nodo falla solo con `NotImplementedError` (`pytest --runxfail`).

## Cambios de esta edición (Ronda 12)

Hallazgo SEC B-01 de `architecture-spine/reviews/review-security.md` (decisión R12-B01, ACCEPT, 2026-10-14): fallo de `Clock`/`IdGenerator`/`QueueReservation` -> 503 fail-closed.

- **Nuevos RED (filas 121-122):** T-RES-15 (fake `RaisingClock` en `resolve`, E1-S2) y T-ROS-21 (fake `RaisingIdGenerator` en `ingest`, E3-S1). Aserciones reales: 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE`, nunca ALLOW, cero mutación, cero eventos (cero credenciales en ingest). Fakes en `test/fakes/fake_failing_ports.py`.
- **Conteos por operación:** resolve I 6 -> 7 (total 23 -> 24); ingest P 13 -> 14 (total 36 -> 37); totales P 38 -> 39, I 35 -> 36, total 95 -> 97.
- **Pendiente (cerrado en Ronda 13):** el test RED de fallo de puertos en `revokeCourseAccess` (Q-fail) existe como T-REV-12 (K-16).

## Cambios de esta edición (Ronda 11)

Cierre de los huecos de node declarados en `test/test-design.md` §9 (decisiones ADOPTED del paquete `.work/paquete-decisiones-F-H.md`, 2026-10-13):

- **Nuevos RED (filas 116-120):** H-24, F-01, H-16 (en `roster.rejected`), H-18a/b. Cada uno con su node exacto.
- **Nuevos guardas (G16-G18):** H-21c (CHECK del DDL), H-25 (el lint de pureza ya cubre `os.urandom`, `uuid`, `secrets`, `time.*` y `datetime.now`; se demuestra con módulos sintéticos), F-06 (schema del 500 contra `dto.py` y `openapi.yaml`, porque ninguna de las tres operaciones emite `AUDIT_LOG_TAMPERING_DETECTED`).
- **Cambio en `scripts/quality_gate.sh` y `.github/workflows/quality-gate.yml`:** la lista `BANNED_IMPORTS` del lint de pureza no incluía `os`, así que `from os import urandom` pasaba el gate (la suite sí lo prohibía). Se añade `os`.
- **Firma en `app/adapters/http.py`:** `http_authorize(context)` acepta `str | list[str] | None` para representar un header repetido (H-24). Solo tipado; no hay lógica.

## Cambios de esta edición (Ronda 10)

- **Génesis (R10-M2, ADOPTED 2026-10-14):** `GENESIS` en `atdd_support.py` = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (ARCHITECTURE.md l.97), sustituye a los 64 ceros (H-15 corregido). `test_ledger_chain_and_anchor` aserta contra esa constante. Se añade el `import struct` que faltaba en `module1_contracts.test.py`.
- **Duplicados de test-review resueltos:** T-ROS-03 (`test_roster_no_role_smuggling`) asevera el estado persistido (rol de la membresía; `assert_no_writes` sobre identities, subject_memberships, subject_credentials y roster_batches) y un único evento `roster.rejected`; T-ROS-03b asevera el manifiesto 422 (campo `assigned_role`). T-REV-01 queda solo para `test_revoke_all_credentials`; `test_revoke_preserves_other_course` pasa a **T-REV-01b**.
- **Gap-fill M-4 (23 atdd-red + 1 guarda):** cubren los gaps funcionales de `epics.md` "Gaps de cobertura" G-2, G-3 a G-14 y G-17 (ver filas 91-113 y G15). Mapa de IDs: T-RES-G-03, T-RES-G-04 (x2 y x2 parametrizados), T-RES-G-04b, T-RES-G-04c (x2), T-RES-G-05, T-RES-G-06, T-RES-G-07, T-RES-G-17, T-REV-G-02, T-REV-G-10, T-REV-G-11, T-REV-G-12 (x6), T-ROS-G-08 (x2), T-ROS-G-09, T-ROS-G-13, guarda T-SEED-GUARD-01 (G-14).
  - Por operación, deltas sobre la tabla "Conteos": resolve +10 (P +8, I +2); revoke +9 (P +8, I +1); ingest +4 (P +2, I +2).
  - G-2 se añade además de los 13 del M-4 (es AC funcional de owner A sin RED). G-15 (QueueReservation, DEFER B) y G-1/G-16 (NFR PLANNED) quedan fuera, igual que en `epics.md`.
- **Limitaciones registradas (no bloquean RED):** G-13 cubre la búsqueda por `key_prefix` y la verificación del hash a través de `ingestRoster`; no hay API pública de verificación en las tres operaciones. G-2 usa `busy_timeout = 50 ms` en la conexión de prueba y un segundo escritor `BEGIN IMMEDIATE`. G-14 es una guarda física de las PK del seed, no la idempotencia del fixture.

## Cambios de esta edición (Ronda 6 y 6b)

- **Fixtures (corrige 28 tests rotos):** `subject_memberships.term NOT NULL` (ADVF-13). `add_membership` recibe `term` (por defecto `TERM = "2026-FALL"`) y `edge_case_seeds` lo inserta. Antes: 20 failed + 8 errors; ahora 0.
- **Vocabulario de action (Ronda 6 Q5):** `model:invoke` → `inference` (enum cerrado `{inference, training}`).
- **Modelos del catálogo (Ronda 6b R6b-01):** ARN con `llama-3-8b-instruct` (gpu_24gb_workstation) y `toy-cpu-demo` (cpu_toy) en CS101.
- **Actor y token (Ronda 6 Q1/Q2):** nuevo `TokenVerifierPort` (`app/ports/identity.py`) y doble `test/fakes/fake_token_verifier.py` (`ADMIN_TOKEN` = Department Chair con rol `admin`; `STUDENT_TOKEN`). `build_module1(db, clock, id_generator, queue, token_verifier, bearer)`: el Bearer es el contexto de la solicitud y se verifica antes de cualquier otra cosa (orden único §1).
- **Firmas de stub:** `revokeCourseAccess(user_id, course_id, drop_reason, timestamp, actor)`, `ingestRoster(batch, actor)`; `RevokePort.drop` y los stubs HTTP reciben `timestamp`/`bearer`. `CredentialDeliveryPort` declarado (sin cablear, ver PB-C).
- **EDGE-01 con la matriz v0 vigente (Ronda 6 Q5):** misma identidad → CS101 student GPU = DENY; CS-480 ta inference = ALLOW (antes se esperaba DENY por falta de fila).
- **Tests nuevos (+8 atdd-red):** T-RES-HP-03, T-RES-I-04, T-RES-P-05, T-REV-P-05, T-REV-P-06, T-REV-I-06, T-ROS-P-05, T-ROS-03b. **Guarda nueva (+1 verde):** T-MEM-GUARD-01.

## Tabla de trazabilidad (atdd-red)

Test ID nuevo = no planificado en `test/test-design.md`; se conserva el nombre nominal de `contracts.md` §5 cuando existe. Node IDs generados desde la colección real de pytest (verificados uno a uno contra `pytest --collect-only`).

| # | Test ID | Node ID pytest exacto | Operación | Categoría | Cláusula | AD-n | Riesgo | Prioridad | Estado RED |
|---|---|---|---|---|---|---|---|---|---|
| 1 | T-RES-HP-01 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_student_inference_cs480` | resolveEffectivePermissions | Q | Q1 | AD-01 (h), AD-10 (s) | R-009 | p0 | RED xfail (NotImplementedError) |
| 2 | T-RES-HP-02 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allow_appends_one_authorization_event` | resolveEffectivePermissions | Q | Q3 | AD-04 (h) | R-004 | p0 | RED xfail (NotImplementedError) |
| 3 | T-RES-P-01 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_identity_404_no_mutation` | resolveEffectivePermissions | P | P1 | — (contrato §1 P1) | R-010 | p1 | RED xfail (NotImplementedError) |
| 4 | T-RES-P-02 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_course_404_no_mutation` | resolveEffectivePermissions | P | P2 | — (contrato §1 P2) | R-010 | p1 | RED xfail (NotImplementedError) |
| 5 | T-RES-02 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_arn_grammar_rejects` | resolveEffectivePermissions | P | P4 | AD-01 (h) | R-001 | p0 | RED xfail (NotImplementedError) |
| 6 | T-RES-P-04 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_invalid_at_400_no_mutation` | resolveEffectivePermissions | P | P3 | AD-13 (s) | R-008 | p1 | RED xfail (NotImplementedError) |
| 7 | T-RES-04 | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_escalation_boundary_expires` | resolveEffectivePermissions | I | I2 | AD-13 (s), AD-05 (h) | R-008 | p0 | RED xfail (NotImplementedError) |
| 8 | T-RES-I-03 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_before_granted_uses_base_role` | resolveEffectivePermissions | I | I2 / H-21b | AD-13 (s) | R-008 | p1 | RED xfail (NotImplementedError) |
| 9 | T-RES-03 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_revoke_commit_denies_enrollment_dropped` | resolveEffectivePermissions | I | Concurrencia §1 (lectura tras commit) | AD-03 (h), AD-12 (s) | R-003 | p0 | RED xfail (NotImplementedError) |
| 10 | T-RES-01 | `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation` | resolveEffectivePermissions | EDGE | I1, I4 (EDGE-01) | AD-01 (h), AD-10 (s) | R-001 | p0 | RED xfail (NotImplementedError); edge_case |
| 11 | T-RES-01b (nuevo) | `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_student_cs101_gpu_denied_cs480_allowed` | resolveEffectivePermissions | EDGE | Q1, I1 (EDGE-01) | AD-01 (h), AD-10 (s) | R-001 | p0 | RED xfail (NotImplementedError); edge_case |
| 12 | T-RES-01c (nuevo) | `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_escalation_in_cs480_does_not_alter_cs101` | resolveEffectivePermissions | EDGE | Q2, I1 (EDGE-01) | AD-01 (h), AD-10 (s) | R-001 | p0 | RED xfail (NotImplementedError); edge_case |
| 13 | T-LED-01 | `test/atdd/module1_contracts.test.py::TestLedgerChain::test_ledger_chain_and_anchor` | resolveEffectivePermissions | Q | Q3 (cadena + ancla) | AD-04 (h) | R-004 | p0 | RED xfail (NotImplementedError) |
| 14 | T-RES-08 | `test/atdd/module1_contracts.test.py::TestExplainability::test_explain_assert_rule_cited` | resolveEffectivePermissions | X | Q4 | AD-11 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 15 | T-RES-08b (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestExplainability::test_explain_deny_expired_threshold_reports_expires_at` | resolveEffectivePermissions | X | Q4 + threshold | AD-11 (s), AD-13 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 16 | T-RES-HP-03 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_cpu_toy_model_cs101` | resolveEffectivePermissions | Q | Q1 + R6b-01 (toy-cpu-demo -> cpu_toy) | AD-10 (s) | R-009 | p0 | RED xfail (NotImplementedError) |
| 17 | T-RES-I-04 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_model_outside_catalog_denied` | resolveEffectivePermissions | I | Paso 7 + R6b-01 (model fuera de resource_catalog) | AD-10 (s), AD-11 (s) | R-009 | p1 | RED xfail (NotImplementedError) |
| 18 | T-RES-P-05 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_malformed_action_400_no_mutation` | resolveEffectivePermissions | P | P4b / Q5 (MALFORMED_ACTION) | AD-09 (s), AD-10 (s) | R-010 | p0 | RED xfail (NotImplementedError) |
| 19 | T-REV-HP-01 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_active_pair_returns_revoked` | revokeCourseAccess | Q | Q1, Q2 | AD-03 (h) | R-003 | p0 | RED xfail (NotImplementedError) |
| 20 | T-REV-HP-02 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_emits_one_membership_revoked_event` | revokeCourseAccess | Q | Q3 | AD-03 (h), AD-04 (h) | R-003 | p0 | RED xfail (NotImplementedError) |
| 21 | T-REV-04 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_never_enrolled_pair_404_membership_not_found` | revokeCourseAccess | P | P2 (MEMBERSHIP_NOT_FOUND) | — (contrato §2 P2) | R-003 | p1 | RED xfail (NotImplementedError) |
| 22 | T-REV-04b (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_suspended_membership_409_invalid_transition` | revokeCourseAccess | P | P2 (INVALID_TRANSITION) | — (contrato §2 P2) | R-003 | p1 | RED xfail (NotImplementedError) |
| 23 | T-REV-03 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_malformed_drop_reason_400_no_mutation` | revokeCourseAccess | P | P3 | AD-06 (h), H-19a | R-006 | p1 | RED xfail (NotImplementedError) |
| 24 | T-REV-P-05 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_non_admin_actor_403_no_mutation` | revokeCourseAccess | P | P0 / Q1 (ADMIN_ROLE_REQUIRED) | AD-09 (s), AD-02 (h) | R-011 | p0 | RED xfail (NotImplementedError) |
| 25 | T-REV-P-06 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_future_timestamp_400_no_mutation` | revokeCourseAccess | P | P4 / Q6 (MALFORMED_DROP_TIMESTAMP, +301 s) | AD-08 (s) | R-011 | p0 | RED xfail (NotImplementedError) |
| 26 | T-REV-01b | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_preserves_other_course` | revokeCourseAccess | I | I1 | AD-03 (h) | R-003 | p0 | RED xfail (NotImplementedError) |
| 27 | T-REV-01 | `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_all_credentials` | revokeCourseAccess | I | I2 | AD-03 (h), AD-12 (s) | R-003 | p0 | RED xfail (NotImplementedError) |
| 28 | T-REV-06 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_store_failure_closed` | revokeCourseAccess | I | I3 | AD-03 (h) + PRD §7.3 | R-003 | p0 | RED xfail (NotImplementedError) |
| 29 | T-REV-02 | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_replay_idempotent` | revokeCourseAccess | I | Repetición (ALREADY_REVOKED) | AD-03 (h) | R-003 | p0 | RED xfail (NotImplementedError) |
| 30 | T-REV-07 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_concurrent_double_drop_single_mutation` | revokeCourseAccess | I | Concurrencia (BEGIN IMMEDIATE) | AD-03 (h), AD-12 (s) | R-003 | p0 | RED xfail (NotImplementedError) |
| 31 | T-SEC-01 | `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_no_secret_leak_in_drop_reason` | revokeCourseAccess | I | I3 | AD-06 (h) | R-006 | p0 | RED xfail (NotImplementedError) |
| 32 | T-REV-I-06 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_timestamp_at_tolerance_boundary_accepted` | revokeCourseAccess | I | Q6 frontera (+300 s aceptado) | AD-08 (s) | R-011 | p1 | RED xfail (NotImplementedError) |
| 33 | T-REV-08 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_already_revoked_cites_ad03` | revokeCourseAccess | X | Q4 (ALREADY_REVOKED) | AD-03 (h), AD-11 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 34 | T-REV-08b (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_first_revoke_reports_credentials_revoked` | revokeCourseAccess | X | Q4 (observed_credentials_revoked) | AD-03 (h), AD-11 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 35 | T-ROS-HP-01 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_valid_batch_persists_all_rows` | ingestRoster | Q | Q1, Q2 | AD-02 (h) | R-002 | p0 | RED xfail (NotImplementedError) |
| 36 | T-ROS-HP-02 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_emits_one_roster_ingested_event` | ingestRoster | Q | Q3 | AD-04 (h) | R-004 | p1 | RED xfail (NotImplementedError) |
| 37 | T-ROS-05 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_malformed_term_400_no_mutation` | ingestRoster | P | P1 (MALFORMED_TERM) | AD-09 (s) | R-011 | p0 | RED xfail (NotImplementedError) |
| 38 | T-ROS-06 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_empty_batch_400_no_mutation` | ingestRoster | P | P2 (BATCH_EMPTY) | AD-02 (h) | R-011 | p1 | RED xfail (NotImplementedError) |
| 39 | T-ROS-06b (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_1001_rows_413_too_large_no_mutation` | ingestRoster | P | P2 (BATCH_TOO_LARGE) | AD-02 (h) | R-011 | p0 | RED xfail (NotImplementedError) |
| 40 | T-ROS-P-05 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_non_admin_actor_403_no_mutation` | ingestRoster | P | P0 / Q1 (ADMIN_ROLE_REQUIRED) | AD-09 (s), AD-02 (h) | R-011 | p0 | RED xfail (NotImplementedError) |
| 41 | T-ROS-01 | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_row85_rollback` | ingestRoster | I | I1 (atomicidad) + Q3 (roster.rejected) | AD-02 (h), AD-04 (h) | R-002 | p0 | RED xfail (NotImplementedError) |
| 42 | T-ROS-02 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_roster_intra_batch_duplicate` | ingestRoster | P | P4 (INTRA_BATCH_DUPLICATE_ID) | AD-02 (h) | R-002 | p0 | RED xfail (NotImplementedError) |
| 43 | T-ROS-03 | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_no_role_smuggling` | ingestRoster | I | I2 (sin cambio de rol) | AD-02 (h), H-20 | R-002 | p0 | RED xfail (NotImplementedError) |
| 44 | T-ROS-03b (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_role_smuggling_422_field_assigned_role` | ingestRoster | I | I2 + ADVF-14 (422 sobre assigned_role) | AD-02 (h), H-20 | R-002 | p0 | RED xfail (NotImplementedError) |
| 45 | T-ROS-I-04 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_1000_rows_boundary_accepted` | ingestRoster | I | Frontera 1000 filas | AD-02 (h) | R-011 | p1 | RED xfail (NotImplementedError) |
| 46 | T-ROS-I-05 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_reingest_creates_new_batch_id` | ingestRoster | I | Repetición (reingesta) | AD-02 (h) | R-002 | p1 | RED xfail (NotImplementedError) |
| 47 | T-ROS-08 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_roster_rejected_cites_ad02_observed_row` | ingestRoster | X | Q4 (422) | AD-02 (h), AD-11 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 48 | T-ROS-08b (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_intra_batch_duplicate_cites_ad02` | ingestRoster | X | Q4 (duplicado) | AD-02 (h), AD-11 (s) | R-010 | p1 | RED xfail (NotImplementedError); explainability |
| 49 | T-CON-01 | `test/atdd/module1_contracts.test.py::TestConcurrency::test_resolve_concurrent_with_revoke_never_allows_after_commit` | transversal | I (concurrencia) | contracts §1 Concurrencia y §2: un resolve concurrente con revoke puede ver el estado previo o el revocado (sn | AD-03 (h), AD-12 (s) | R-003 | p0 | RED xfail (NotImplementedError) |
| 50 | T-SCH-01 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_expires_active_ticket_once_with_one_event` | transversal | I (barrido) | contracts §1 Tiempo: el barrido transiciona ACTIVE -> EXPIRED con un evento escalation.expired por transición  | AD-05 (h), AD-13 (s) | — | p1 | RED xfail (NotImplementedError) |
| 51 | T-SCH-02 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_does_not_expire_ticket_not_yet_granted` | transversal | I (barrido) | el scheduler actualiza solo tickets ACTIVE con granted_at <= now; si granted_at > now aún no expira | AD-13 (s) | — | p1 | RED xfail (NotImplementedError) |
| 52 | T-SCH-03 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_crash_recovery_reconciles_all_expired_tickets` | transversal | I (barrido) | al reiniciar, el barrido recorre todo ACTIVE con expires_at <= now y emite un evento por transición; idempoten | AD-05 (h) | — | p1 | RED xfail (NotImplementedError) |
| 53 | T-SCH-04 | `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric` | transversal | I (barrido) | si la cola no acepta el evento de expiración el barrido se DIFIERE (no se persiste la transición) y se emite s | AD-12 (s), AD-13 (s) | — | p0 | RED xfail (NotImplementedError) |
| 54 | T-HTTP-01 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_declared_routes_match_openapi_one_route_per_operation` | transversal | P (HTTP/formato) | contracts §0 y openapi.yaml: cada una de las tres operaciones tiene exactamente una ruta canónica; el adaptado | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 55 | T-HTTP-02 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_roster_body_with_utf8_bom_400_malformed_batch` | transversal | P (HTTP/formato) | contracts §3 P2: codificación UTF-8 sin BOM; un BOM -> MALFORMED_BATCH 400 | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 56 | T-HTTP-03 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_rfc4180_parses_quoted_comma_and_escaped_quote_in_four_fields` | transversal | P (HTTP/formato) | contracts §3 P2: CSV con exactamente 4 campos por fila; comillas, comas y `""` escapadas se interpretan según  | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 57 | T-HTTP-04 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_row_with_five_fields_400_malformed_batch` | transversal | P (HTTP/formato) | contracts §3 P2: fila con 5 campos -> MALFORMED_BATCH 400 (columnas exactas institutional_id,email,full_name,a | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 58 | T-HTTP-05 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_unsupported_content_type_400_malformed_batch` | transversal | P (HTTP/formato) | contracts §3 P2: Content-Type distinto de multipart/form-data (CSV) o application/json (JSON) -> MALFORMED_BAT | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 59 | T-HTTP-06 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[sin-partes]` | transversal | P (HTTP/formato) | contracts §3 P2: multipart con una parte `file` exactamente; cualquier otra cantidad -> MALFORMED_BATCH 400 | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 60 | T-HTTP-06 | `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[dos-partes]` | transversal | P (HTTP/formato) | contracts §3 P2: multipart con una parte `file` exactamente; cualquier otra cantidad -> MALFORMED_BATCH 400 | AD-09 (s) | — | p1 | RED xfail (NotImplementedError) |
| 61 | T-AD07-01 | `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_zero_becomes_one` | transversal | I (AD-07) | contracts §4: page_size fuera de [1, 100] no es error, se fuerza al rango; 0 -> 1 | AD-07 (h) | — | p2 | RED xfail (NotImplementedError) |
| 62 | T-AD07-02 | `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_above_limit_becomes_100` | transversal | I (AD-07) | contracts §4: page_size > 100 se fuerza a 100 | AD-07 (h) | — | p2 | RED xfail (NotImplementedError) |
| 63 | T-ROS-04 | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response` | ingestRoster | Q | contracts §3 Q2: CredentialDeliveryPort.enqueue se llama exactamente una vez por cada membresía que el lote de | AD-02 (h), AD-06 (h) | — | p0 | RED xfail (NotImplementedError) |
| 64 | T-ROS-18 | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_email_domain_case_insensitive_local_part_preserved` | ingestRoster | Q | contracts §3 P3: el dominio se compara sin distinguir mayúsculas; el resto del email se conserva intacto (sin  | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 65 | T-ROS-19 | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_reuses_existing_identity_without_duplicate` | ingestRoster | Q | PRD FR-INGEST-01 regla 3: si la identidad ya existe por otra asignatura no se duplica; solo se asocia el nuevo | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 66 | T-ROS-07 | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inexistente]` | ingestRoster | Q | subject_id inexistente o no activo -> UNKNOWN_COURSE 404 sin escrituras | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 67 | T-ROS-07 | `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inactiva]` | ingestRoster | Q | subject_id inexistente o no activo -> UNKNOWN_COURSE 404 sin escrituras | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 68 | T-ROS-09 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_student_token_403_admin_before_batch_syntax` | ingestRoster | P | contracts §3 P0: actor no admin -> 403 ADMIN_ROLE_REQUIRED antes de la sintaxis (un lote vacío daría 400 BATCH | AD-09 (s) | — | p0 | RED xfail (NotImplementedError) |
| 69 | T-ROS-10 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_duplicate_email_in_batch_422_no_writes` | ingestRoster | P | contracts §3 P4: emails repetidos dentro del lote -> ROSTER_VALIDATION_FAILED detectado en memoria antes de la | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 70 | T-ROS-11 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[vacio]` | ingestRoster | P | contracts §3 P3: email vacío o fuera de universidad.edu -> fila del manifiesto ROSTER_VALIDATION_FAILED sobre  | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 71 | T-ROS-11 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[dominio-externo]` | ingestRoster | P | contracts §3 P3: email vacío o fuera de universidad.edu -> fila del manifiesto ROSTER_VALIDATION_FAILED sobre  | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 72 | T-ROS-12 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule` | ingestRoster | P | contracts §3 P3 [ADOPTED 2026-10-14, R8-09]: correo fuera de universidad.edu produce ROSTER_VALIDATION_FAILED  | AD-11 (s) | — | p1 | RED xfail (NotImplementedError) |
| 73 | T-ROS-13 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_queue_full_503_no_mutation` | ingestRoster | P | contracts §3 Q3: si el evento de auditoría no es aceptado en la cola -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE f | AD-02 (h), AD-12 (s) | — | p0 | RED xfail (NotImplementedError) |
| 74 | T-ROS-14 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[SUSPENDED]` | ingestRoster | I | identidad global SUSPENDED o EXPELLED -> 422 ROSTER_VALIDATION_FAILED sobre identity_status con rule_ids [ROSTER_VALIDATION_FAILED, IDENTITY_BARRED] (R9-01); el lote entero se rechaza | AD-02 (h) | — | p0 | RED xfail (NotImplementedError) |
| 75 | T-ROS-14 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[EXPELLED]` | ingestRoster | I | identidad global SUSPENDED o EXPELLED -> 422 ROSTER_VALIDATION_FAILED sobre identity_status con rule_ids [ROSTER_VALIDATION_FAILED, IDENTITY_BARRED] (R9-01); el lote entero se rechaza | AD-02 (h) | — | p0 | RED xfail (NotImplementedError) |
| 76 | T-ROS-15 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_conflicting_identity_row_422_no_identity_update` | ingestRoster | I | contracts §3 P3: institutional_id ya existente con otro email -> ROSTER_VALIDATION_FAILED por fila; la identid | AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 77 | T-ROS-16 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED]` | ingestRoster | I | contracts §3 Invariantes: membresía previa en DROPPED, SUSPENDED o COMPLETED con el mismo rol NO se reactiva;  | AD-02 (h), AD-05 (h) | — | p1 | RED xfail (NotImplementedError) |
| 78 | T-ROS-16 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[SUSPENDED]` | ingestRoster | I | contracts §3 Invariantes: membresía previa en DROPPED, SUSPENDED o COMPLETED con el mismo rol NO se reactiva;  | AD-02 (h), AD-05 (h) | — | p1 | RED xfail (NotImplementedError) |
| 79 | T-ROS-16 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[COMPLETED]` | ingestRoster | I | contracts §3 Invariantes: membresía previa en DROPPED, SUSPENDED o COMPLETED con el mismo rol NO se reactiva;  | AD-02 (h), AD-05 (h) | — | p1 | RED xfail (NotImplementedError) |
| 80 | T-ROS-17 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored` | ingestRoster | I | DDL subject_credentials: key_hash = SHA-256(salt || raw_key) con salt de 16 bytes; la clave en claro nunca se  | AD-06 (h) | — | p1 | RED xfail (NotImplementedError) |
| 81 | T-SEC-ROS-01 | `test/atdd/module1_ingest_rules_contracts.test.py::TestSecrets::test_ingest_secret_in_batch_field_never_in_manifest_or_logs` | ingestRoster | I (R-006) | AD-06 (heredado): una clave uai_live_ completa enviada dentro de un campo del lote no aparece en el manifiesto | AD-06 (h) | R-006 | p0 | RED xfail (NotImplementedError) |
| 82 | T-RES-10 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_resource_subject_mismatch_403_explained_no_mutation` | resolveEffectivePermissions | P | PRD §5.2 regla 2 (Confused Deputy) y contracts §1 P5: el subject del ARN (CS101) no es el contexto de la petic | AD-01 (h) | — | p0 | RED xfail (NotImplementedError) |
| 83 | T-RES-11 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4` | resolveEffectivePermissions | P | PRD §5.2 regla 4 (mínimo privilegio por defecto): identidad no activa en la materia del contexto -> DENY deter | AD-01 (h), AD-10 (s) | — | p0 | RED xfail (NotImplementedError) |
| 84 | T-RES-13 | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_queue_full_503_no_decision_no_mutation` | resolveEffectivePermissions | I | contracts §1 Q3: si el evento obligatorio no puede aceptarse en la cola -> 503 AUTH_INTERNAL_POLICY_UNAVAILABL | AD-04 (h), AD-12 (s) | — | p0 | RED xfail (NotImplementedError) |
| 85 | T-RES-14 | `test/atdd/module1_resolve_contracts.test.py::TestSecrets::test_resolve_secret_in_action_400_never_echoed_in_clear` | resolveEffectivePermissions | I (R-006) | AD-06 (heredado): una clave uai_live_ completa en la petición nunca sale en claro en la respuesta de error ni  | AD-06 (h) | R-006 | p0 | RED xfail (NotImplementedError) |
| 86 | T-REV-09 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_student_token_403_admin_before_drop_reason_syntax` | revokeCourseAccess | P | contracts §0 paso 1bis: actor sin rol admin -> 403 ADMIN_ROLE_REQUIRED antes de la sintaxis (drop_reason vacío | AD-09 (s) | — | p0 | RED xfail (NotImplementedError) |
| 87 | T-REV-10 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[nul]` | revokeCourseAccess | P | contracts §2 P3: caracteres de control (Unicode Cc) en drop_reason -> MALFORMED_DROP_REASON 400 | AD-06 (h) | — | p1 | RED xfail (NotImplementedError) |
| 88 | T-REV-10 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[newline]` | revokeCourseAccess | P | contracts §2 P3: caracteres de control (Unicode Cc) en drop_reason -> MALFORMED_DROP_REASON 400 | AD-06 (h) | — | p1 | RED xfail (NotImplementedError) |
| 89 | T-REV-10 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[del]` | revokeCourseAccess | P | contracts §2 P3: caracteres de control (Unicode Cc) en drop_reason -> MALFORMED_DROP_REASON 400 | AD-06 (h) | — | p1 | RED xfail (NotImplementedError) |
| 90 | T-SEC-REV-01 | `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear` | revokeCourseAccess | I (R-006) | AD-06 (heredado): ninguna clave uai_live_ completa en logs, respuesta ni filas de audit_ledger / audit_events | AD-06 (h) | R-006 | p0 | RED xfail (NotImplementedError) |
| 91 | T-RES-G-03 | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` | resolveEffectivePermissions | I | I1 tras baja + repetición x3 de DENY; un evento por intento (gap G-3) | AD-03 (h), AD-01 (h) | — | p0 | RED xfail (NotImplementedError) |
| 92 | T-RES-G-04 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]` | resolveEffectivePermissions | P | P5 + R9-01: identidad SUSPENDED → DENY IDENTITY_BARRED antes de la membresía (gap G-4) | AD-01 (h), AD-11 (s) | — | p0 | RED xfail (NotImplementedError) |
| 93 | T-RES-G-04 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]` | resolveEffectivePermissions | P | igual que 92 con identidad EXPELLED (gap G-4) | AD-01 (h), AD-11 (s) | — | p0 | RED xfail (NotImplementedError) |
| 94 | T-RES-G-04b | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_precedes_subject_mismatch` | resolveEffectivePermissions | P | H-17: IDENTITY_BARRED > RESOURCE_SUBJECT_MISMATCH (gap G-4) | AD-01 (h) | — | p1 | RED xfail (NotImplementedError) |
| 95 | T-RES-G-04c | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED]` | resolveEffectivePermissions | P | ADVF-08: membresía SUSPENDED → SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED (gap G-4b) | AD-01 (h) | — | p0 | RED xfail (NotImplementedError) |
| 96 | T-RES-G-04c | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[COMPLETED]` | resolveEffectivePermissions | P | ADVF-08: membresía COMPLETED → SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED (gap G-4b) | AD-01 (h) | — | p0 | RED xfail (NotImplementedError) |
| 97 | T-RES-G-05 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_header_cs101_arn_cs480_mismatch_403` | resolveEffectivePermissions | P | R9-03 literal: header CS101 + ARN CS-480 → RESOURCE_SUBJECT_MISMATCH 403 (gap G-5) | AD-01 (h) | — | p0 | RED xfail (NotImplementedError) |
| 98 | T-RES-G-06 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_lowercase_course_header_404_unknown_course` | resolveEffectivePermissions | P | header `cs-480` → UNKNOWN_COURSE 404 (gap G-6) | AD-01 (h) | — | p1 | RED xfail (NotImplementedError) |
| 99 | T-RES-G-07 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_missing_identity_and_course_reports_identity_first` | resolveEffectivePermissions | P | F-03: identidad inexistente antes que curso inexistente (gap G-7) | AD-01 (h) | — | p1 | RED xfail (NotImplementedError) |
| 100 | T-RES-G-17 | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_deny_response_has_no_quota_or_priority_fields` | resolveEffectivePermissions | I | I4: DENY sin campos de cuota ni prioridad (gap G-17) | AD-01 (h) | — | p1 | RED xfail (NotImplementedError) |
| 101 | T-REV-G-02 | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit` | revokeCourseAccess | I | SQLITE_BUSY agotado → 503 AUTH_INTERNAL_POLICY_UNAVAILABLE sin commit parcial (gap G-2) | AD-12 (s), AD-03 (h) | R-003 | p0 | RED xfail (NotImplementedError) |
| 102 | T-REV-G-10 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_281_chars_400_no_mutation` | revokeCourseAccess | P | P3: drop_reason de 281 puntos → MALFORMED_DROP_REASON (gap G-10) | AD-03 (h) | — | p1 | RED xfail (NotImplementedError) |
| 103 | T-REV-G-11 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_empty_reason_and_missing_timestamp_rule_ids_order` | revokeCourseAccess | P | R3-02/H-23: MALFORMED_DROP_REASON primero, MALFORMED_DROP_TIMESTAMP en rule_ids (gap G-11) | AD-03 (h) | — | p1 | RED xfail (NotImplementedError) |
| 104 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-no-utc]` | revokeCourseAccess | P | G9-01/R4-01: offset distinto de Z/+00:00 → MALFORMED_DROP_TIMESTAMP (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 105 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-menos-cero]` | revokeCourseAccess | P | G9-01: `-00:00` inválido (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 106 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fraccion-7-digitos]` | revokeCourseAccess | P | G9-01: más de 6 decimales (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 107 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[sin-hora]` | revokeCourseAccess | P | G9-01: fecha sin hora (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 108 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[segundo-60]` | revokeCourseAccess | P | G9-01: segundo 60 (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 109 | T-REV-G-12 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fecha-inexistente]` | revokeCourseAccess | P | G9-01: 2026-02-30 (gap G-12) | AD-08 (s) | — | p1 | RED xfail (NotImplementedError) |
| 110 | T-ROS-G-08 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]` | ingestRoster | P | ECF-05: eco de subject_id distinto del path → MALFORMED_BATCH (gap G-8) | AD-09 (s), AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 111 | T-ROS-G-08 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]` | ingestRoster | P | ECF-05: subject_id ausente en el body → MALFORMED_BATCH (gap G-8) | AD-09 (s), AD-02 (h) | — | p1 | RED xfail (NotImplementedError) |
| 112 | T-ROS-G-09 | `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity` | ingestRoster | I | ADVF-21: institutional_id case-sensitive, `stu-98432` ≠ `STU-98432` (gap G-9) | AD-02 (h), AD-09 (s) | — | p0 | RED xfail (NotImplementedError) |
| 113 | T-ROS-G-13 | `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash` | ingestRoster | I | ADVF-17/ECF-18: lookup por key_prefix y verificación SHA-256(salt‖raw_key) (gap G-13) | AD-06 (h) | — | p1 | RED xfail (NotImplementedError) |
| 114 | T-RES-05 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_request_now_captured_once_and_reused_as_occurred_at` | resolveEffectivePermissions | I | H-16 (captura única `request_now`) | AD-13 (s) | R-008 | p0 | RED xfail (NotImplementedError) |
| 115 | T-RES-09 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_effective_role_is_exact_roles_id` | resolveEffectivePermissions | Q | H-26 (`effective_role` = `roles.id` exacto) | AD-10 (s) | R-011 | p1 | RED xfail (NotImplementedError) |
| 116 | T-RES-H24 (nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent` [repetido-igual], [repetido-distinto], [vacio] | resolveEffectivePermissions | P | H-24 (header repetido/vacío = ausente → paso 3) | AD-01 (h), AD-09 (s) | R-011 | p0 | RED xfail (NotImplementedError) |
| 117 | T-REV-F01 (nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay` [solo-espacios], [control-nul] | revokeCourseAccess | P | F-01 (DROPPED + drop_reason inválido → 400 antes del replay) | AD-03 (h), AD-09 (s) | R-003 | p1 | RED xfail (NotImplementedError) |
| 118 | T-ROS-H16 (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestRequestTimeInRejection::test_roster_rejected_occurred_at_reuses_single_request_now` | ingestRoster | I | H-16 en roster.rejected (una lectura de `request_now` = occurredAt) | AD-13 (s) | R-008 | p0 | RED xfail (NotImplementedError) |
| 119 | T-ROS-H18a (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_term_percent_encoded_decoded_once` | ingestRoster | P | H-18 (term decodificado una vez: `2026-%46ALL` = `2026-FALL`; `2026-%2546ALL` → 400) | AD-09 (s) | R-011 | p1 | RED xfail (NotImplementedError) |
| 120 | T-ROS-H18b (nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course` [inexistente], [minusculas] | ingestRoster | P | H-18 (segmento de curso exacto; inexistente → 404 UNKNOWN_COURSE) | AD-09 (s) | R-011 | p1 | RED xfail (NotImplementedError) |
| 121 | T-RES-15 (R12-B01, nuevo) | `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation` | resolveEffectivePermissions | I | contracts §1 Q-fail (R12-B01, SEC B-01): `Clock.now()` lanza -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE fail-closed; nunca ALLOW/DENY, cero mutación, cero eventos (fake: `RaisingClock`) | AD-08 (s), AD-12 (s) | — | p0 | RED xfail (NotImplementedError) |
| 122 | T-ROS-21 (R12-B01, nuevo) | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials` | ingestRoster | P | contracts §3 Q-fail (R12-B01, SEC B-01): `IdGenerator` lanza al asignar batch_id -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; cero escrituras, cero credenciales, cero eventos (fake: `RaisingIdGenerator`) | AD-12 (s), AD-02 (h) | — | p0 | RED xfail (NotImplementedError) |
| 123 | T-REV-12 (R12-B01, nuevo) | `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_clock_failure_503_fail_closed_no_mutation` | revokeCourseAccess | I | contracts §2 Q-fail (R12-B01, SEC B-01): `Clock.now()` lanza antes del commit -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; membresía sigue ACTIVE, credenciales sin cambio, cero eventos (fake: `RaisingClock`) | AD-03 (h), AD-12 (s) | R-003 | p0 | RED xfail (NotImplementedError) |

## Guardas (no atdd-red)

Marcadas `guard`, no `atdd`: pasan en verde porque el DDL ya impone el invariante (R3-06 y Ronda 6 Q3).

| # | Test ID | Node ID pytest exacto | Categoría | Cláusula | AD-n | Riesgo | Estado |
|---|---|---|---|---|---|---|---|
| G1 | T-LED-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_update_rejected` | guard | append-only (trg_audit_ledger_no_update) | AD-04 (h) | R-004 | VERDE (guard, no atdd-red) |
| G2 | T-LED-GUARD-02 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_delete_rejected` | guard | append-only (trg_audit_ledger_no_delete) | AD-04 (h) | R-004 | VERDE (guard, no atdd-red) |
| G3 | T-LED-GUARD-03 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_update_rejected` | guard | append-only (trg_audit_events_no_update) | AD-04 (h) | R-004 | VERDE (guard, no atdd-red) |
| G4 | T-LED-GUARD-04 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_delete_rejected` | guard | append-only (trg_audit_events_no_delete) | AD-04 (h) | R-004 | VERDE (guard, no atdd-red) |
| G5 | T-MEM-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_membership_per_pair_across_terms` | guard | Ronda 6 Q3 / ADVF-13: UNIQUE(identity, subject, term) + índice parcial ACTIVE | AD-02 (h) | R-002 | VERDE (guard, no atdd-red) |
| G6 | T-ESC-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_escalation_per_pair` | guard | AD-05 (heredado) exclusión mutua de escalación: índice único parcial idx_single_active_escalation sobre (reque | AD-05 (h) | — | VERDE (guard, no atdd-red) |
| G7 | T-ESC-GUARD-02 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_timestamp_fixed_format_check` | guard | ADVF-23 / ECF-15 [ADOPTED 2026-10-13]: granted_at con formato fijo YYYY-MM-DDTHH:MM:SS.ffffffZ (6 decimales, z | — | — | VERDE (guard, no atdd-red) |
| G8 | T-LED-GUARD-05 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_resource_type_not_null_and_indexed` | guard | R8-07 / NFR-AUDIT-06 | — | — | VERDE (guard, no atdd-red) |
| G9 | T-PUR-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_has_no_infrastructure_imports_or_clock_calls` | guard | AD-08 / H-25 | AD-08 (s) | — | VERDE (guard, no atdd-red) |
| G10 | T-ROS-20 | `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_auth_token_invalid_401_before_batch_validation` | P | contracts §0 paso 1: bearer inválido -> 401 AUTH_TOKEN_INVALID antes de validar el lote (term 'bad' daría 400  | AD-09 (s) | — | VERDE (guard, no atdd-red) |
| G11 | T-RES-12 | `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_auth_token_invalid_401_before_arn_validation` | P | contracts §0 orden único paso 1: bearer ausente o inválido -> 401 AUTH_TOKEN_INVALID ANTES de validar el ARN ( | AD-09 (s) | — | VERDE (guard, no atdd-red) |
| G12 | T-REV-11 | `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_auth_token_invalid_401_before_body_validation` | P | contracts §0 orden único paso 1: bearer ausente o inválido -> 401 AUTH_TOKEN_INVALID antes de validar el body  | AD-09 (s) | — | VERDE (guard, no atdd-red) |
| G13 | T-ESC-GUARD-03 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_self_approval_rejected` | guard | R9-02 / AD-05 (heredado): CHECK approved_by IS NULL OR approved_by <> requester_id | AD-05 (h) | — | VERDE (guard, no atdd-red) |
| G14 | T-LED-GUARD-06 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_timestamp_fixed_format_check` | guard | R9-04 / ADVF-23: CHECK GLOB de formato fijo en audit_ledger.timestamp | — | — | VERDE (guard, no atdd-red) |
| G15 | T-SEED-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_edge_case_seed_duplicates_rejected_by_pk` | guard | R10 gap G-14 / E1-S1: PK de roles, subjects e identities rechazan la re-inserción del seed EDGE-01 | — | — | VERDE (guard, no atdd-red) |
| G16 | T-ESC-GUARD-04 | `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_expires_after_granted_check` | guard | H-21c: CHECK (expires_at > granted_at) en tickets ACTIVE (001_module1_schema.sql l.113) | AD-13 (s) | R-008 | VERDE (guard, no atdd-red) |
| G17 | T-PUR-GUARD-02 | `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source` [os.urandom], [from-os-urandom], [uuid4], [secrets], [time.monotonic], [datetime.now], [random] | guard | H-25: el lint de pureza detecta cada fuente de no-determinismo sobre un módulo sintético | AD-08 (s) | R-012 | VERDE (guard, no atdd-red) |
| G18 | T-ERR-GUARD-01 | `test/atdd/module1_guard_contracts.test.py::TestErrorEnvelope::test_guard_audit_log_tampering_500_uses_error_body_without_explanation` | guard | F-06: 500 AUDIT_LOG_TAMPERING_DETECTED con ErrorBody sin ExplanationDTO (schema contra dto.py y openapi.yaml; ninguna de las 3 ops lo emite) | AD-11 (s) | — | VERDE (guard, no atdd-red) |

## Conteos por operación × categoría

Categorías: Q = happy path; P = violación de precondición (código tipado + HTTP + cero mutación + cero eventos, salvo §3 Q3); I = invariante bajo concurrencia, repetición o frontera; EDGE-01 = Mandatory Edge Case; X = explicabilidad (AD-11).

| Operación | Q happy | P precondición | I invariante | EDGE-01 | X explicabilidad | Total |
| --- | --- | --- | --- | --- | --- | --- |
| resolveEffectivePermissions | 4 | 8 | 7 | 3 | 2 | 24 |
| revokeCourseAccess | 2 | 10 | 9 | 0 | 2 | 23 |
| ingestRoster | 7 | 14 | 14 | 0 | 2 | 37 |
| transversal (AD-07, concurrencia, HTTP, planificador) | 0 | 7 | 7 | 0 | 0 | 14 |
| **Total** | **13** | **39** | **37** | **3** | **6** | **98** |

Ronda 11 suma por función de test (no por nodo parametrizado): resolve +1 P (H-24), revoke +1 P (F-01), ingest +2 P (H-18a/b) y +1 I (H-16). Los guardas G16-G18 no entran en esta tabla.

Mínimo estricto cumplido: en las tres operaciones Q, P e I tienen ≥2 y X tiene 2. EDGE-01 solo aplica a `resolveEffectivePermissions` (3 tests), igual que antes.

**Clasificación P vs I en ingestRoster.** `test_roster_intra_batch_duplicate` (P4) y los rechazos 422 emiten `roster.rejected` por §3 Q3, lo que contradice el "cero eventos" general de §1 Q-fail. Se aplica la regla específica de §3 (ver S3/S4). Los P con 400/403/413 de ingest aseveran cero eventos. El 422 de anti-smuggling (T-ROS-03b) compara solo tablas de negocio, no el ledger.

## Cobertura de riesgos y AD-n (test-design.md)

| Riesgo (test-design) | Prioridad | Cubierto por | Estado |
|---|---|---|---|
| R-001 aislamiento por contexto / ARN | P0 | `test_edge01_context_isolation`, `test_edge01_student_cs101_gpu_denied_cs480_allowed`, `test_edge01_escalation_in_cs480_does_not_alter_cs101`, `test_arn_grammar_rejects` | RED |
| R-002 lote atómico / reingesta | P0 | `test_roster_row85_rollback`, `test_roster_intra_batch_duplicate`, `test_roster_no_role_smuggling`, `test_roster_role_smuggling_422_field_assigned_role`, `test_ingest_valid_batch_persists_all_rows`, `test_ingest_reingest_creates_new_batch_id`; guarda `test_guard_single_active_membership_per_pair_across_terms` | RED + verde (guarda) |
| R-003 revocación / carrera | P0 | `test_revoke_*` (incluye 403 admin y timestamp), `test_resolve_after_revoke_commit_denies_enrollment_dropped` | RED |
| R-004 cadena de auditoría | P0 | `test_ledger_chain_and_anchor`, `test_roster_row85_rollback` (roster.rejected), guardas G1-G4 | RED + verde (guardas) |
| R-006 secretos | P0 | `test_no_secret_leak_in_drop_reason`, `test_revoke_malformed_drop_reason_400_no_mutation` | RED |
| R-008 frontera temporal | P0 | `test_escalation_boundary_expires`, `test_resolve_before_granted_uses_base_role`, `test_resolve_invalid_at_400_no_mutation`, `test_resolve_request_now_captured_once_and_reused_as_occurred_at` | RED |
| R-009 matriz rol×acción (fail-closed) | P0 | Fila v0 ALLOW: `test_resolve_allows_student_inference_cs480`, `test_resolve_allows_cpu_toy_model_cs101`, `test_edge01_context_isolation` (ta CS-480). DENY: `test_edge01_student_cs101_gpu_denied_cs480_allowed`. Fail-closed sin fila y modelo fuera de catálogo: `test_resolve_model_outside_catalog_denied`, `test_escalation_boundary_expires` (instructor_privileged en CS101 sin fila) | RED (antes "sin test propio" → cubierto) |
| R-010 contrato de errores/explicación | P1 | `test_resolve_unknown_*`, `test_resolve_malformed_action_400_no_mutation`, `test_revoke_never_enrolled_*`, `test_explain_*` (6) | RED |
| R-011 transporte/boundary | P0-P1 | `test_ingest_malformed_term_400_no_mutation`, `test_ingest_empty_batch_400_no_mutation`, `test_ingest_1001_rows_413_too_large_no_mutation`, `test_ingest_1000_rows_boundary_accepted`, `test_ingest_non_admin_actor_403_no_mutation`, `test_revoke_non_admin_actor_403_no_mutation`, `test_revoke_future_timestamp_400_no_mutation`, `test_revoke_timestamp_at_tolerance_boundary_accepted`, `test_resolve_effective_role_is_exact_roles_id` | RED |

**Sin test en esta suite (pendiente explícito):** T-RES-07 (precedencias intra-paso F-03/H-17), propiedades de la captura de reloj en revoke fuera del timestamp, `CredentialDeliveryPort` (201 sin claves, solo hash; PB-C), prueba de reserva de cola `QueueReservation` (pendiente TEA), mapeo único operación↔HTTP (AD-09, requiere adapter FastAPI), paginación (AD-07, respaldo fuera de las tres operaciones) y benchmarks NFR (PLANNED, sin harness). Lint de pureza AD-08: Etapa 1 de `quality_gate.sh`.

## Supuestos vigentes

- **S1 — Vocabulario de `action` y clase de recurso. RESUELTO (Ronda 6 Q5 [ADOPTED 2026-10-13] y R6b-01 [ADOPTED 2026-10-14]).** `action ∈ {inference, training}`; la clase de recurso sale del segmento `model` del ARN vía `resource_catalog` de `roles_matrix.v0.json`. Quedan como [ASSUMPTION] solo los nombres de fixture `toy-cpu-demo` y `train-queue`.
- **S2 — TA en CS-480. RESUELTO (Ronda 6 Q5 / ADVF-06 / ECF-25).** La matriz v0 tiene la fila (CS-480, ta, inference, gpu_24gb_workstation, true). EDGE-01: misma identidad → CS101 student GPU DENY (`UNAUTHORIZED_RESOURCE_CLASS`) y CS-480 ta inference ALLOW.
- **S3 — Eventos en rechazos de ingestRoster.** §3 Q3 exige `roster.rejected` en el 422. Se aplica como excepción a §1 Q-fail (P1–P4 sin evento). Los 400/403/413 de ingest aseveran cero eventos. Resuelto por el texto de contrato (PB4 cerrado).
- **S4 — Duplicado intra-lote.** Se trata como P4 (422) con `roster.rejected` por la misma regla de S3.
- **S5 — Código del anti-smuggling (H-20). RESUELTO (ADVF-14, Ronda 6).** `422 ROSTER_VALIDATION_FAILED` sobre `assigned_role` (observed/expected), sin código nuevo. T-ROS-03b asevera el campo; PB3 cerrado.
- **S6 — Firmas de dominio (actualizado).** `resolveEffectivePermissions(user_id, course_id, resource_arn, action, at=None)`; `revokeCourseAccess(user_id, course_id, drop_reason, timestamp, actor)`; `ingestRoster(batch, actor)`. `actor = {actor_id, actor_role}` ya verificado por `TokenVerifierPort`. El `timestamp` entra como argumento del puerto para poder probar P4 con `fake_clock`; contracts §2 P4 lo sitúa fuera de la firma Annex A — ver PB-A. Facade `Module1Service` con métodos snake_case.
- **S7 — Canal de error.** Los P y 4xx/5xx se modelan como `Module1Error(code, http_status, body)` (`app/domain/errors.py`). Los DENY de política se devuelven como `{decision: "DENY", ...}`. `body` lleva `explanation` cuando el catálogo lo exige; los 403 ADMIN_ROLE_REQUIRED no la llevan (R6b-03).
- **S8 — `ALREADY_REVOKED`** no es código de error (200). Se asevera por `status` + `explanation` citando AD-03 (`observed_prior_status`).
- **S9 — Concurrencia.** `test_revoke_concurrent_double_drop_single_mutation` usa dos conexiones SQLite al mismo archivo WAL y dos hilos con barrera; ambas conexiones usan el mismo `FakeTokenVerifier` y el token admin. Los errores de hilo se re-lanzan. En GREEN validará `BEGIN IMMEDIATE`.
- **S10 — Dobles.** `FakeQueueReservation` registra reservas y publicaciones; `set_capacity(0)` simula cola llena. `FakeTokenVerifier` (nuevo) resuelve `ADMIN_TOKEN` (admin) y `STUDENT_TOKEN` (student) y lanza `InvalidTokenError` (tipo del puerto, `app/ports/identity.py`) para cualquier otro bearer; el mapeo a `AUTH_TOKEN_INVALID` / 401 es responsabilidad del servicio (GREEN). Ninguno implementa reglas de negocio. Clock e IdGenerator reutilizan `fake_clock` y `fake_id_generator`.
- **S11 — Seeds.** Helpers en `test/fakes/world.py` insertan filas válidas según el DDL, con `term` en membresías (`TERM = "2026-FALL"`). `edge_case_seeds` (conftest) se usa tal cual en EDGE-01, en P y en explicabilidad.
- **S12 — Config pytest.** `python_files` incluye `*_contracts.test.py`; `addopts = --import-mode=importlib`; marker `guard` añadido; markers existentes intactos.
- **S13 — Gate.** Etapa 7 de `scripts/quality_gate.sh` reconoce xfail estricto (`[0-9]+ xfailed` sin `failed|error`). Sin cambios en esta edición.
- **S14 — Dependencia.** `pyyaml==6.0.3` en `requirements-dev.txt` y en el venv (Etapa 4 de la gate).
- **S15 — Bearer por servicio (nuevo).** El Bearer es contexto de la solicitud: `build_module1(..., token_verifier, bearer)`. El facade no verifica nada: pasa el Bearer crudo y el `token_verifier` a los stubs de dominio; la verificación (401 primero) es lógica GREEN del dominio. Los tests de 403 componen el servicio con `STUDENT_TOKEN`.
- **S16 — Aserción de cero escrituras con 422 (nuevo).** El rechazo 422 de ingest registra `roster.rejected` en el ledger (§3 Q3), así que las comparaciones de "cero escrituras" en 422 miden solo `identities`, `subject_memberships`, `subject_credentials` y `roster_batches`, y aseveran un único `roster.rejected`.

## Preguntas bloqueantes

Ninguna bloquea el RED: las 90 pruebas atdd fallan por `NotImplementedError` y el gate pasa. Las siguientes deben cerrarse antes de implementar en GREEN:

- **PB-A (material, antes de GREEN de revoke).** ¿El `timestamp` de baja entra al dominio (como en esta suite, para probar P4 con `fake_clock`) o lo valida solo el adapter HTTP? contracts §2 P4 dice que no forma parte de la firma de dominio Annex A. Si es solo adapter, T-REV-P-06 y T-REV-I-06 deben moverse a la capa `http_drop`.
- **PB-B (menor, observación).** `ingestRoster` exige que el `term` del lote sea el del curso (P1: otro term → `MALFORMED_TERM`). Por tanto una membresía del mismo `(identity, subject)` con otro term no es alcanzable vía ingest; queda cubierta solo a nivel DDL (T-MEM-GUARD-01). Confirmar que es intencional.
- **PB-C (menor).** `CredentialDeliveryPort` está declarado (`app/ports/identity.py`) pero no está cableado en `build_module1` ni cubierto por test. La prueba "201 sin claves; solo hash persistido" queda pendiente para GREEN (contracts §3 Q2, Ronda 6 Q4).

PB1 (fila ta CS-480) y PB2 (vocabulario de action/clase) quedan cerrados por Ronda 6 Q5 y R6b-01. PB3 (código del anti-smuggling) queda cerrado por ADVF-14. PB4 (roster.rejected en 422) queda cerrado por §3 Q3.

## Próximo paso

- Cerrar PB-A antes de implementar `revokeCourseAccess`.
- Implementar en GREEN por operación, empezando por P0 (R-001..R-008, R-011). Quitar `xfail` al activar cada test.
