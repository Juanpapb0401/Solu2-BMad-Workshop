---
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-map-criteria', 'step-04-analyze-gaps', 'step-05-gate-decision']
lastStep: 'step-05-gate-decision'
lastSaved: '2026-10-14'
coverageBasis: 'acceptance_criteria'
oracleResolutionMode: 'formal_requirements'
oracleConfidence: 'high'
oracleSources: ['planning/prd.md', 'ux/C-UX-Scenarios/00-ux-scenarios.md', 'planning/ARCHITECTURE.md', 'solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md', 'solu2-module1/planning/detailed-design/contracts.md', 'solu2-module1/planning/epics.md', 'solu2-module1/test/test-design.md', 'solu2-module1/test/nfr-evidence.md', 'solu2-module1/test/atdd-checklist.md']
externalPointerStatus: 'not_used'
collectionMode: 'contract_static'
collectionStatus: 'COLLECTED'
gateDecision: 'FAIL'
sourceSha: ''
---

# Matriz de trazabilidad: Módulo 1 (User, Role, and Subject Access Manager)

**Workflow:** `bmad-testarch-trace`, corrida final de la consigna (Fase 5, paso 3). Sustituye a la primera pasada del mismo día (ver §9).
**Fecha:** 2026-10-14
**Suite evaluada:** `solu2-module1/test/`. Colección: `cd solu2-module1 && .venv/bin/pytest --collect-only -q` = **155 nodos** (130 atdd-red, 21 guardas, 4 harness) en la corrida Ronda 13 (2026-10-14; +1 atdd-red de K-16, T-REV-12). Corrida `pytest -q`: **25 passed** (21 guardas DDL/pureza y 4 de harness) y **130 xfailed**. Los 130 atdd-red tienen causa `NotImplementedError` (stub sin lógica productiva): `pytest -q --runxfail -m atdd` = 130 failed, todos `NotImplementedError` (verificado en Ronda 13). Desglose de la causa en §11.
**Alcance:** fase RED (stop-point de solutioning). No se modificó ningún test, código, diseño ni `epics.md`. No se ejecutó `bmad-build`. Ningún NFR está `EVIDENCED`.
**Live verification:** no hay `live-verification-results.json`. El workspace no es un repositorio Git, así que `sourceSha` queda vacío.
**Cómo se aplicó el skill:** el workflow se aplicó a mano siguiendo `steps-c/step-03` a `step-05` y `checklist.md`. No hay runtime del skill que ejecute los bloques JS. Los artefactos `e2e-trace-summary.json` y `gate-decision.json` se escriben en `solu2-module1/test/`.

**Leyenda de Status (lectura especificada)**
- `FULL`: el criterio está fijado por aserciones de tests que hoy fallan por `NotImplementedError`. Eso **no** es cobertura ejecutada.
- `PARTIAL`: parte de lo que el criterio afirma está fijada por un test y otra parte no (sin test, sin medición o fuera de alcance).
- `NONE`: el criterio no tiene ningún test ni medición.
- La suite no declara nivel por test. Los tests de contrato se cuentan como nivel `api` (ver §8).

---

## 1. Veredicto y métricas

Las dos métricas de la consigna se reportan por separado. La gate del skill es una tercera cosa y no se mezcla con ellas.

| Métrica | Valor | Meta | Resultado |
|---|---|---|---|
| **M1a.** Requisitos **P0** enlazados a historia y a test RED | **7/7 (100%)** | 100% | Cumple |
| **M1b.** Riesgos **P0** (`test-design.md` §1) enlazados a historia y a test RED | **7/7 (100%)** | 100% | Cumple |
| M1c. Requisitos totales (12) enlazados a historia y a test RED que mide el criterio | 7/12 (58%) | — | Ver §2 |
| M1d. Requisitos **P1** (5) enlazados a historia | 5/5 | — | Historia sí; test que mide el criterio: 0/5 |
| **M2a.** AD-n (13) con al menos un test que se pone rojo si se viola la regla | **13/13 (100%)** | 0 sin test | Cumple |
| M2b. AD-n con **todas** sus cláusulas cubiertas por test | 8/13 | — | 5 parciales (§3) |
| **Cobertura ejecutada** (criterios `FULL` en ejecución verde) | **0/12 (0%)** | 0% por diseño en RED | Esperado |
| Clasificación `FULL` en lectura especificada | 2/12 (17%); P0 2/7 (29%); P1 0/5 (0%) | — | Base del gate |
| **Gate del skill** | **FAIL** (Regla 1) | — | §7 |

**Lectura de la diferencia entre M1 y la gate.** M1 mide si cada requisito P0 y cada riesgo P0 tiene una historia y un test RED que lo señale. La gate del skill mide si el criterio está establecido por el test. Un test RED con `NotImplementedError` enlaza el criterio a su prueba, pero no lo establece. Por eso M1 cumple y la gate falla.

**Requisitos P0 (7).** EDGE-01, FR-INGEST-01, FR-REVOC-03, FR-ESCAL-02, FR-AUDIT-04, NFR-SEC-04 y NFR-SEC-05. **Corrección frente a la primera pasada:** NFR-SEC-05 pasa a P0 porque `test-design.md` R-006 cita PRD NFR-SEC-04 **y** NFR-SEC-05. La primera pasada lo tenía como P1. El cambio no altera M1a, porque NFR-SEC-05 ya tiene test RED.

---

## 2. Matriz principal (oráculo: 12 ítems)

Columnas: PRD FR/NFR (prioridad) | Scenario (UX) | AD-n | Historia(s) | Test RED (archivo::test; node ID completo en §10) | Status | Nota.

| PRD FR/NFR | Scenario (UX) | AD-n | Story ID | Test RED | Status | Nota |
|---|---|---|---|---|---|---|
| FR-INGEST-01 (P0) | SC-01 | AD-02, AD-04, AD-09 | E3-S1, E3-S2, E3-S3, E3-S4 | `module1_ingest_contracts::test_ingest_valid_batch_persists_all_rows`; `module1_ingest_contracts::test_roster_row85_rollback`; `module1_ingest_rules_contracts::test_ingest_barred_identity_rejects_whole_batch_422` | PARTIAL | Falta el criterio E2E de 120 filas < 2.0 s (umbral gate, «Umbrales triageados» de epics.md). Sin medición (G-16). |
| FR-ESCAL-02 (P0) | SC-02 | AD-05, AD-13 | E4-S2 | `module1_resolve_contracts::test_escalation_boundary_expires`; `module1_resolve_contracts::test_resolve_before_granted_uses_base_role`; `module1_contracts::test_sweep_expires_active_ticket_once_with_one_event` | PARTIAL | Alcance contratado: honrar tickets ACTIVE y vencidos en resolve. Creación, aprobación y rechazo quedan fuera de alcance (sin historia). |
| FR-REVOC-03 (P0) | SC-03 | AD-03, AD-11, AD-12 | E2-S1, E2-S2, E2-S3, E2-S4, E2-S5 | `module1_revoke_contracts::test_revoke_all_credentials`; `module1_revoke_contracts::test_revoke_replay_idempotent`; `module1_resolve_contracts::test_resolve_after_revoke_commit_denies_enrollment_dropped` | PARTIAL | Propagación `T1 - T0 < 200 ms` (G-1; gate NFR-REVOC-03; objetivo laxo 500 ms de PRD §4.3) y NFR-REVOC-03 sin medición. |
| FR-AUDIT-04 (P0) | SC-04 | AD-04, AD-07 | E1-S3 | `module1_contracts::test_ledger_chain_and_anchor` (RED); `module1_guard_contracts::test_guard_audit_ledger_update_rejected` (VERDE) | PARTIAL | Consulta forense paginada y `AUDIT_LOG_TAMPERING_DETECTED` quedan fuera de alcance (sin historia). |
| EDGE-01 (P0) | EDGE-01 (SC-02 rel.) | AD-01, AD-09, AD-10, AD-11 | E4-S1, E4-S3, E4-S4 | `module1_contracts::test_edge01_context_isolation`; `module1_contracts::test_edge01_student_cs101_gpu_denied_cs480_allowed`; `module1_resolve_contracts::test_resolve_resource_subject_mismatch_403_explained_no_mutation`; `module1_resolve_contracts::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4` | FULL (RED) | Mandatory Edge Case literal cubierto. Excepción: cabecera repetida o vacía (H-24 ADOPTED: se trata como ausente; sin node propio aún). CRLF lo decide el parser HTTP. |
| NFR-SEC-04 (P0) | SC-02; SC-04 | AD-06 | E2-S5, E3-S1, E3-S2, E4-S4 | `module1_revoke_contracts::test_no_secret_leak_in_drop_reason`; `module1_ingest_rules_contracts::test_ingest_secret_in_batch_field_never_in_manifest_or_logs`; `module1_resolve_contracts::test_resolve_secret_in_action_400_never_echoed_in_clear` | PARTIAL | Regex `uai_live_[a-zA-Z0-9]{32}` sobre 10 000 líneas: sin test (G-16). |
| NFR-SEC-05 (P0) | SC-01 | AD-06 | E3-S1 | `module1_ingest_rules_contracts::test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored`; `module1_ingest_rules_contracts::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash`; `module1_ingest_contracts::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response` | FULL (RED) | Hash SHA-256 con salt de 16 bytes y valor en claro una sola vez: cubiertos por aserción. |
| NFR-PERF-01 (P1) | SC-02; EDGE-01 | AD-04, AD-12 | E1-S2, E4-S1 | Sin test que mida latencia. Test funcional RED: `module1_resolve_contracts::test_resolve_allows_student_inference_cs480` | NONE | p95 < 20 ms y p99 < 50 ms a 100 req/s: PLANNED, sin medición (G-16). |
| NFR-PERF-02 (P1) | SC-01 | AD-02 | E3-S1 | Sin test de tiempo. Test funcional RED: `module1_ingest_contracts::test_ingest_1000_rows_boundary_accepted` | NONE | `T < 3.0 s` para 1 000 filas: sin medición (G-16). |
| NFR-REVOC-03 (P1) | SC-03 | AD-03 | E2-S1, E2-S3 | Test funcional RED: `module1_revoke_contracts::test_revoke_active_pair_returns_revoked` | PARTIAL | El efecto (credenciales REVOKED, 403 tras commit) está fijado. `T_local < 200 ms` y `T_revoc < 60 s` no (G-1, G-16). |
| NFR-AUDIT-06 (P1) | SC-04 | AD-07, AD-04 | E1-S3 | Índice probado en DDL: `module1_guard_contracts::test_guard_audit_ledger_resource_type_not_null_and_indexed` (VERDE) | PARTIAL | Índice `(resource_type, timestamp)` probado. Consulta de 100 000 eventos `< 500 ms` p95 sin medición (G-16). |
| NFR-DISP-07 (P1) | SC-04 (transversal) | AD-03 | E1-S1 | Sin test | NONE | RAM ≤ 512 MB y boot `< 5.0 s`: PLANNED, sin medición (G-16). |

**Conteo:** FULL 2 (EDGE-01, NFR-SEC-05); PARTIAL 7; NONE 3. P0 FULL 2/7. P1 FULL 0/5. Los 20 nodos añadidos en la Ronda 11 (K-2) se mapean a requisito, AD-n e historia en §11; ninguno cambia un Status de esta tabla.

**Filas de trazabilidad sin requisito directo en el PRD.** La suite también cubre contratos sin línea PRD propia, trazados a AD-n y a `contracts.md` (Annex A): precondiciones de `resolveEffectivePermissions`, `revokeCourseAccess` e `ingestRoster`, guardas DDL, pureza de `domain/`, mapeo HTTP y explicabilidad. Cada uno se enlaza a una historia (ver §10).

---

## 3. AD-01 a AD-13 → historia(s) → test(s) que se pondrían rojos

Fuentes: `planning/ARCHITECTURE.md` §5 (AD-01 a AD-07) y `ARCHITECTURE-SPINE.md` (AD-08 a AD-13). Historias según `epics.md` «Trazabilidad AD-n».

| AD-n | Regla (resumen) | Story ID | Test(s) que se ponen rojos | Estado |
|---|---|---|---|---|
| AD-01 | Gramática ARN; comparación byte a byte; mismatch 403 | E1-S2, E2-S2, E4-S1, E4-S3, E4-S4 | `test_arn_grammar_rejects`; `test_edge01_context_isolation`; `test_resolve_resource_subject_mismatch_403_explained_no_mutation`; `test_resolve_header_cs101_arn_cs480_mismatch_403`; `test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4`; `test_authorize_subject_context_repeated_or_empty_is_absent[3 nodos]` (H-24, K-2) | **Completo** (excepción H-24 cerrada con node en K-2) |
| AD-02 | Lote atómico; anti role-smuggling | E3-S1 a E3-S4 | `test_roster_row85_rollback`; `test_roster_no_role_smuggling`; `test_ingest_barred_identity_rejects_whole_batch_422[SUSPENDED]`; `test_ingest_conflicting_identity_row_422_no_identity_update` | **Completo** (F-04 ADOPTED: los tests asertan «sin batch_id» en 400/413) |
| AD-03 | Revocación en una transacción; idempotencia; fail-closed | E2-S1 a E2-S5 | `test_revoke_all_credentials`; `test_revoke_replay_idempotent`; `test_revoke_store_failure_closed`; `test_revoke_busy_timeout_exhausted_503_no_partial_commit`; `test_revoke_dropped_invalid_reason_400_before_replay[2 nodos]` (F-01, K-2) | **Parcial**: proceso único `workers: 1` sin test (solo NFR-DISP-07, PLANNED) |
| AD-04 | Cadena hash; ancla `head_record_hash`/`total_events_count`; append-only | E1-S2, E1-S3, E2-S1, E3-S1 | `test_ledger_chain_and_anchor` (anclas incluidas); guardas `test_guard_audit_ledger_update_rejected`, `test_guard_audit_ledger_delete_rejected`, `test_guard_audit_events_update_rejected`, `test_guard_audit_events_delete_rejected` (VERDE); `test_guard_audit_log_tampering_500_uses_error_body_without_explanation` (F-06, VERDE, K-2) | **Completo** (`AUDIT_LOG_TAMPERING_DETECTED` emitido fuera de alcance: solo se fija el envelope, §5) |
| AD-05 | Exclusión mutua de escalaciones; `approver_id != requester_id` | E4-S2 | `test_guard_escalation_self_approval_rejected` (VERDE, DDL); `test_guard_single_active_escalation_per_pair` (VERDE); `test_escalation_boundary_expires` | **Parcial por alcance**: el 403 `FORBIDDEN_SELF_APPROVAL` por API no tiene test; el flujo request/approve está fuera de las tres operaciones. La regla está fijada en DDL. |
| AD-06 | Máscara `uai_live_<4>••••<4>`; regex de build sobre logs | E2-S5, E3-S1, E3-S2, E4-S4 | `test_no_secret_leak_in_drop_reason`; `test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear`; `test_ingest_secret_in_batch_field_never_in_manifest_or_logs`; `test_resolve_secret_in_action_400_never_echoed_in_clear` | **Parcial**: el escaneo regex de 10 000 líneas no tiene test (G-16) |
| AD-07 | `page_size` acotado a [1, 100]; cursor `(timestamp, id)` | E1-S3 | `test_ad07_clamp_page_size_zero_becomes_one`; `test_ad07_clamp_page_size_above_limit_becomes_100` | **Parcial**: el cursor no tiene test; la consulta forense está fuera de alcance |
| AD-08 | Pureza de `domain/`; reloj inyectado | E1-S1, E2-S5 | `test_domain_has_no_infrastructure_imports_or_clock_calls` (VERDE); `test_domain_purity_lint_detects_each_nondeterminism_source[7 nodos]` (H-25, VERDE, K-2); `test_revoke_future_timestamp_400_no_mutation` | **Completo** |
| AD-09 | Mapeo único operación↔HTTP; admin en revoke/ingest; 401 primero | E1-S2, E2-S4, E3-S4, E4-S1 | `test_declared_routes_match_openapi_one_route_per_operation`; `test_revoke_auth_token_invalid_401_before_body_validation`; `test_ingest_auth_token_invalid_401_before_batch_validation`; `test_revoke_non_admin_actor_403_no_mutation`; `test_ingest_non_admin_actor_403_no_mutation` | **Completo** |
| AD-10 | Mandatory Edge Case; sin herencia cruzada; sin cuota GPU en resolve | E1-S1, E4-S1, E4-S2, E4-S4 | `test_edge01_context_isolation`; `test_edge01_escalation_in_cs480_does_not_alter_cs101`; `test_resolve_allows_cpu_toy_model_cs101`; `test_resolve_model_outside_catalog_denied`; `test_resolve_deny_response_has_no_quota_or_priority_fields`; `test_resolve_effective_role_is_exact_roles_id` (T-RES-09, H-26, K-2) | **Completo** |
| AD-11 | `ExplanationDTO` con `rule_ids` no vacío que cita un AD-n | E1-S2, E2-S1, E2-S3, E3-S2, E4-S3 | `test_explain_assert_rule_cited`; `test_explain_deny_expired_threshold_reports_expires_at`; `test_explain_roster_rejected_cites_ad02_observed_row`; `test_explain_already_revoked_cites_ad03` | **Completo** |
| AD-12 | Serialización de carreras; `BEGIN IMMEDIATE`; `QueueReservation` | E2-S2, E2-S3, E3-S1 | `test_revoke_concurrent_double_drop_single_mutation`; `test_resolve_concurrent_with_revoke_never_allows_after_commit`; `test_resolve_queue_full_503_no_decision_no_mutation`; `test_ingest_queue_full_503_no_mutation`; `test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation` (R12-B01); `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials` (R12-B01) | **Parcial**: `QueueReservation` (reserve/publish/release) sin test (G-15, DEFER a Fase 3) |
| AD-13 | Frontera `[granted_at, expires_at)`; scheduler | E4-S2, E4-S4 | `test_escalation_boundary_expires`; `test_resolve_before_granted_uses_base_role`; `test_resolve_invalid_at_400_no_mutation`; `test_sweep_expires_active_ticket_once_with_one_event`; `test_resolve_request_now_captured_once_and_reused_as_occurred_at` (T-RES-05, K-2); `test_roster_rejected_occurred_at_reuses_single_request_now` (T-ROS-H16, K-2); `test_guard_escalation_expires_after_granted_check` (H-21c, K-2) | **Completo** (frecuencia de 1 s del scheduler sin medición) |

**Conteo M2:** 13/13 AD con al menos un test que se pone rojo (M2a). 8 completos (AD-01, 02, 04, 08, 09, 10, 11, 13) y 5 parciales (AD-03, 05, 06, 07, 12) (M2b).

---

## 4. Riesgos P0 (`test-design.md` §1) → historia → test RED

| Riesgo | Story ID | Test RED que lo cubre | Estado | Excepción (sub-caso con decisión ADOPTED, sin node propio) |
|---|---|---|---|---|
| R-001 aislamiento por contexto (EDGE-01, ARN) | E4-S1, E4-S3 | `test_edge01_context_isolation`; `test_resolve_header_cs101_arn_cs480_mismatch_403` | Cubierto | H-24 ADOPTED → `test_authorize_subject_context_repeated_or_empty_is_absent` (3 nodos RED, E4-S4; checklist fila 116; node en §11) |
| R-002 lote no atómico | E3-S2, E3-S3 | `test_roster_row85_rollback`; `test_roster_intra_batch_duplicate`; `test_roster_no_role_smuggling` | Cubierto | F-04 y H-20 ADOPTED (nodes en §6) |
| R-003 revocación con carrera | E2-S2, E2-S3 | `test_revoke_all_credentials`; `test_revoke_replay_idempotent`; `test_revoke_preserves_other_course`; `test_revoke_store_failure_closed` | Cubierto | F-01 ADOPTED → `test_revoke_dropped_invalid_reason_400_before_replay` (2 nodos RED, E2-S5; checklist fila 117; node en §11) |
| R-004 cadena de auditoría | E1-S3, E2-S1 | `test_ledger_chain_and_anchor`; `test_revoke_emits_one_membership_revoked_event` | Cubierto | Detección de manipulación fuera de alcance |
| R-006 secreto en claro | E2-S5, E3-S2, E4-S4 | `test_no_secret_leak_in_drop_reason`; `test_ingest_secret_in_batch_field_never_in_manifest_or_logs`; `test_resolve_secret_in_action_400_never_echoed_in_clear` | Cubierto en parte | H-19a/b ADOPTED (nodes en §6); escaneo regex (G-16) |
| R-008 frontera temporal | E4-S2 | `test_escalation_boundary_expires`; `test_resolve_before_granted_uses_base_role`; `test_sweep_expires_active_ticket_once_with_one_event` | Cubierto | H-21a/b ADOPTED (nodes en §6); H-21c → `test_guard_escalation_expires_after_granted_check` (guard, E4-S2); H-16 → `test_resolve_request_now_captured_once_and_reused_as_occurred_at` (T-RES-05, RED, E1-S2) y `test_roster_rejected_occurred_at_reuses_single_request_now` (T-ROS-H16, RED, E3-S2) |
| R-009 matriz rol×acción | E4-S1, E4-S4 | `test_resolve_model_outside_catalog_denied`; `test_resolve_allows_cpu_toy_model_cs101` | Cubierto (DENY por defecto) | F-02 ADOPTED (matriz v0); ALLOW por acción solo para filas v0 |

**M1b: 7/7 riesgos P0** con historia y test RED. Las excepciones de esta tabla (H-24, F-01, H-21c, H-16) ya tienen node en la colección (K-2, §11). La columna de excepciones describe el sub-caso ADOPTED y su node. No se escribieron aserciones por suposición.

---

## 5. Huérfanos en ambos sentidos

**(a) Requisito o cláusula sin historia**
- FR-ESCAL-02: creación, aprobación y rechazo de escalaciones (`PENDING_APPROVAL`, 409 concurrente, 403 por auto-aprobación, scope del token). Fuera de las tres operaciones; declarado en `epics.md` «Fuera de alcance de Solu-2».
- FR-AUDIT-04: consulta forense paginada (`GET /api/v1/audit/access-events`) y detección de manipulación `AUDIT_LOG_TAMPERING_DETECTED`. Fuera de alcance, declarado en `epics.md`.

**(b) Requisito sin test que mida su criterio (tiene historia)**
- NFR-PERF-01, NFR-PERF-02, NFR-REVOC-03 (tiempos), NFR-SEC-04 (regex de 10 000 líneas), NFR-AUDIT-06 (100 000 eventos), NFR-DISP-07. Todos siguen en PLANNED (G-1 y G-16).

**(c) Historia sin requisito:** 0 de 16. Cada historia cita al menos un FR, NFR, EDGE-01, AD-n o cláusula PRD.

**(d) Test sin requisito:** 4 de 155, todos de `test/test_harness_smoke.py`. Son infraestructura (fixture de reloj, IDs, topología). E1-S1 los cita como scaffold. Las guardas DDL y de pureza, y todos los ATDD (incluidos los 20 nodos de K-2, §11), trazan a AD-n.

**Test sin historia:** 0. Los 155 nodos están citados en `epics.md` (verificado en K-2 por nombre de función y en Ronda 12 por conteo de node IDs).

---

## 6. Análisis de huecos (Step 4)

**Críticos: P0 por debajo de FULL (5).** Son la razón de la gate.
- **FR-INGEST-01:** criterio E2E de 120 filas `< 2.0 s` sin test de tiempo.
- **FR-REVOC-03:** propagación `T1 - T0 < 200 ms` (G-1; gate NFR-REVOC-03; objetivo laxo 500 ms de PRD §4.3) [ACTUALIZADO 2026-10-14, K-21].
- **NFR-SEC-04:** escaneo regex de 10 000 líneas (G-16).
- **FR-ESCAL-02 y FR-AUDIT-04:** parcialidad por alcance. La decisión es de alcance, no de test. Si el equipo los amplía, pasan a historia nueva.

**Altos: P1 con `NONE` (3).** NFR-PERF-01, NFR-PERF-02 y NFR-DISP-07. Requieren corrida medible (G-16). No se marcan `EVIDENCED`.

**AD con cláusula sin test (5).** AD-03 (`workers: 1`), AD-05 (flujo request/approve fuera de alcance; DDL cubre la regla), AD-06 (regex de build), AD-07 (cursor `(timestamp, id)`), AD-12 (`QueueReservation`, G-15).

**Decisiones que antes figuraban OPEN y ahora están ADOPTED (paquete 2026-10-13).** H-24: repetido/vacío = ausente; caso ausente en `test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4` (repetido/vacío: hueco de node). F-04: `batch_id` tras validaciones en `test_ingest_malformed_term_400_no_mutation`, `test_ingest_empty_batch_400_no_mutation`, `test_ingest_1001_rows_413_too_large_no_mutation`. H-20: `test_roster_no_role_smuggling`, `test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED|SUSPENDED|COMPLETED]`. H-19a/b: `test_revoke_malformed_drop_reason_400_no_mutation`, `test_no_secret_leak_in_drop_reason`. H-21a/b/c: `test_escalation_boundary_expires`, `test_resolve_before_granted_uses_base_role` (H-21c es CHECK del DDL). H-16: `test_resolve_request_now_captured_once_and_reused_as_occurred_at` (reuso en `roster.rejected`: hueco). F-02: `roles_matrix.v0.json` con `test_resolve_model_outside_catalog_denied` y `test_resolve_allows_student_inference_cs480`. Ninguna decisión listada queda OPEN en esta matriz.

**Nodos pendientes.** T-RES-05 y T-RES-09 tienen node RED (`TestRequestTimeAndRole`, ver checklist filas 114-115; filas añadidas a §10 en K-2). Resta T-RES-07 como precedencia intra-paso sin node propio (G-4/G-7 la cubren en parte).

**Ronda 11 (cierre de huecos de node, 2026-10-14).** Ya tienen node: H-24 (checklist 116), F-01 (117), H-16 en `roster.rejected` (118), H-18a/b (119-120), H-21c (G16), H-25 (G17, 7 nodos), F-06 (G18). La matriz de §4 y la de §10 reflejan estos nodos. Colección: 152 nodos (127 RED + 21 guardas + 4 harness).

**Esta pasada no crea tests.** El stop-point solo permite RED intencional ya escrito. Las recomendaciones del skill (`/bmad-testarch-atdd`, `/bmad-testarch-automate`) quedan para una fase posterior y no se ejecutaron.

---

## 7. Decisión de gate del skill (Step 5)

**Decisión: FAIL.**

- **Elegibilidad:** `allow_gate = true` y `collection_status = COLLECTED` (modo `contract_static`). La gate es elegible.
- **Oráculo:** formal (PRD, UX, ARCHITECTURE, ARCHITECTURE-SPINE, contracts, test-design). `oracleConfidence = high`. Sin overlay sintético. Sin evidencia live. Sin `gate-waivers.md`, así que la Regla 6 no tiene efecto y WAIVED no aplica.
- **Fase RED:** `SKILL.md`, `checklist.md`, `steps-c/`, `steps-e/` y `steps-v/` no contienen una regla de fase pre-implementación, ATDD ni RED. No se aplica ninguna excepción por ser RED. La fase RED solo entra en la métrica M1 de la consigna, que es separada.
- **Re-evaluación K-2 (2026-10-14):** los 20 nodos nuevos no suben ningún P0 de PARTIAL a FULL. FR-REVOC-03 sigue sin medir `T1 - T0 < 200 ms` (gate NFR-REVOC-03), FR-INGEST-01 sin medir 120 filas `< 2.0 s`, FR-ESCAL-02 y FR-AUDIT-04 fuera de alcance, y NFR-SEC-04 sin escaneo regex. P0 FULL sigue 2/7 y la decisión no cambia.
- **Regla 1 (`.agents/skills/bmad-testarch-trace/steps-c/step-05-gate-decision.md`, bloque `// Rule 1: P0 coverage must be 100%`, `if (p0Coverage < 100)`):** P0 `29%` (2/7) `< 100` ⇒ **FAIL**. Rationale: «P0 coverage is 29% (required: 100%). 5 critical requirement(s) below FULL coverage.»
- **Regla 2** (`overall 17% < 80`) también fallaría, pero la Regla 1 decide primero.
- **Sensibilidad:** si la cobertura se leyera como ejecutada (0%), el P0 seguiría en `< 100` y el veredicto no cambia.

**Veredicto final: FAIL.** No se declara PASS ni CONCERNS. Tampoco WAIVED, porque no hay registro de waivers. Un PASS exige P0 FULL 100% con evidencia ejecutada. Las decisiones de §6 ya están ADOPTED, pero no cambian la cobertura P0 de esta matriz, así que el veredicto FAIL se mantiene.

---

## 8. Contradicciones, limitaciones y correcciones

- **C1 (umbral de ingesta).** PRD FR-INGEST-01 pide 120 filas `< 2.0 s`, UX SC-01 pide `< 1.2 s` para 120, y NFR-PERF-02 pide `< 3.0 s` para 1 000. Son tres umbrales distintos. No se mezclan. Queda abierto para el equipo.
- **C2 (nombres).** `contracts.md` §5 usa nombres nominales (`test_admin_role_required`, `test_no_secret_leak`, `test_double_submit_single_ticket`) que no coinciden con la suite. La fuente de node IDs es la colección real. Normalizar nombres queda pendiente.
- **C3 (IDs `T-*`).** `test-design.md` y `atdd-checklist.md` usan `T-*`. La consigna exige node IDs. Esta matriz usa node IDs. Los `T-*` aparecen en las docstrings.
- **C4 (`T-RES-05` `request_now`).** Resuelto por K-3 (readiness corrida 2): node RED `test_resolve_request_now_captured_once_and_reused_as_occurred_at`.
- **Limitación de niveles.** La suite no declara nivel por test. Todos los tests de contrato se cuentan como `api` y los de harness como `other`. Esto no altera la gate, que usa `FULL`.
- **Limitación de `rejectedEvidence`.** No se auditaron aserciones de los 127 tests RED contra su criterio (la auditoría AST de K-2 descarta tautologías y nombres indefinidos, pero no compara cada aserción con su criterio) (step-03 §1a). La lista de tests rechazados se reporta vacía, y eso no prueba que no exista ninguna.
- **Correcciones frente a la primera pasada.** (1) La colección pasó de 106 a 132 nodos por ampliación de la suite. (2) NFR-SEC-05 pasa a P0 (ver §1). (3) Cierran G1 (mismatch de cabecera) y G6 (401 y admin de AD-09). Siguen abiertos G5, G8 (`QueueReservation`) y G9 (tamper).

---

## 9. Historial: primera pasada (2026-10-14)

Sección breve, conservada como referencia. Estaba basada en 106 nodos (90 RED, 16 VERDE) y dejó la gate en FAIL. Tenía 6 AD completos, 5 parciales y 2 sin test (AD-05, AD-07). Los 7 riesgos P0 tenían RED. Esta pasada la sustituye.

---

## 10. Apéndice: node IDs, líneas, historia y estado

Colección real de `solu2-module1/`. La línea es la del `def` del test. Historia es la que cita `epics.md` para ese nodo. Verificado con `pytest --collect-only -q` (155 de 155 nodos citados en `epics.md` tras Ronda 13; 152 de 152 en K-2). Las filas de `T-RES-05` y `T-RES-09` se añadieron en K-2; antes faltaban en esta tabla.

| Node ID (pytest --collect-only) | Archivo:línea | Historia(s) | Estado (2026-10-14) |
|---|---|---|---|
| `test/atdd/module1_contracts.test.py::TestConcurrency::test_resolve_concurrent_with_revoke_never_allows_after_commit` | module1_contracts.test.py:203 | E2-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation` | module1_contracts.test.py:58 | E4-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_escalation_in_cs480_does_not_alter_cs101` | module1_contracts.test.py:112 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_student_cs101_gpu_denied_cs480_allowed` | module1_contracts.test.py:91 | E4-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestExplainability::test_explain_assert_rule_cited` | module1_contracts.test.py:181 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_rfc4180_parses_quoted_comma_and_escaped_quote_in_four_fields` | module1_contracts.test.py:375 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_csv_row_with_five_fields_400_malformed_batch` | module1_contracts.test.py:391 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_declared_routes_match_openapi_one_route_per_operation` | module1_contracts.test.py:338 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[dos-partes]` | module1_contracts.test.py:420 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_multipart_must_have_exactly_one_file_part[sin-partes]` | module1_contracts.test.py:420 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_roster_body_with_utf8_bom_400_malformed_batch` | module1_contracts.test.py:362 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestHttpMapping::test_unsupported_content_type_400_malformed_batch` | module1_contracts.test.py:407 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestLedgerChain::test_ledger_chain_and_anchor` | module1_contracts.test.py:139 | E1-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_crash_recovery_reconciles_all_expired_tickets` | module1_contracts.test.py:291 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_defers_when_queue_full_and_emits_deferred_metric` | module1_contracts.test.py:313 | E1-S1, E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_does_not_expire_ticket_not_yet_granted` | module1_contracts.test.py:273 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestSchedulerSweep::test_sweep_expires_active_ticket_once_with_one_event` | module1_contracts.test.py:252 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_above_limit_becomes_100` | module1_contracts.test.py:447 | E1-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_contracts.test.py::TestTransversalAD::test_ad07_clamp_page_size_zero_becomes_one` | module1_contracts.test.py:437 | E1-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_delete_rejected` | module1_guard_contracts.test.py:138 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_events_update_rejected` | module1_guard_contracts.test.py:120 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_delete_rejected` | module1_guard_contracts.test.py:103 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_resource_type_not_null_and_indexed` | module1_guard_contracts.test.py:303 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_ledger_update_rejected` | module1_guard_contracts.test.py:86 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_audit_timestamp_fixed_format_check` | module1_guard_contracts.test.py:278 | E1-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_edge_case_seed_duplicates_rejected_by_pk` | module1_guard_contracts.test.py:326 | E1-S1 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_self_approval_rejected` | module1_guard_contracts.test.py:247 | E4-S2 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_timestamp_fixed_format_check` | module1_guard_contracts.test.py:220 | E4-S2 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_escalation_per_pair` | module1_guard_contracts.test.py:187 | E4-S2 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_single_active_membership_per_pair_across_terms` | module1_guard_contracts.test.py:156 | E3-S3 | VERDE |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_has_no_infrastructure_imports_or_clock_calls` | module1_guard_contracts.test.py:357 | E1-S1 | VERDE |
| `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_intra_batch_duplicate_cites_ad02` | module1_ingest_contracts.test.py:639 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestExplainability::test_explain_roster_rejected_cites_ad02_observed_row` | module1_ingest_contracts.test.py:617 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_email_domain_case_insensitive_local_part_preserved` | module1_ingest_contracts.test.py:115 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_emits_one_roster_ingested_event` | module1_ingest_contracts.test.py:73 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response` | module1_ingest_contracts.test.py:89 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_reuses_existing_identity_without_duplicate` | module1_ingest_contracts.test.py:133 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inactiva]` | module1_ingest_contracts.test.py:159 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_unknown_or_inactive_subject_404_no_writes[inexistente]` | module1_ingest_contracts.test.py:159 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestHappyPath::test_ingest_valid_batch_persists_all_rows` | module1_ingest_contracts.test.py:43 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_1000_rows_boundary_accepted` | module1_ingest_contracts.test.py:512 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_institutional_id_case_distinct_identity` | module1_ingest_contracts.test.py:584 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_ingest_reingest_creates_new_batch_id` | module1_ingest_contracts.test.py:529 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_no_role_smuggling` | module1_ingest_contracts.test.py:487 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_role_smuggling_422_field_assigned_role` | module1_ingest_contracts.test.py:550 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestInvariants::test_roster_row85_rollback` | module1_ingest_contracts.test.py:457 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-ausente]` | module1_ingest_contracts.test.py:435 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_http_roster_subject_echo_mismatch_400_malformed_batch[eco-distinto]` | module1_ingest_contracts.test.py:435 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_1001_rows_413_too_large_no_mutation` | module1_ingest_contracts.test.py:226 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_auth_token_invalid_401_before_batch_validation` | module1_ingest_contracts.test.py:294 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_duplicate_email_in_batch_422_no_writes` | module1_ingest_contracts.test.py:343 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_empty_batch_400_no_mutation` | module1_ingest_contracts.test.py:207 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[dominio-externo]` | module1_ingest_contracts.test.py:364 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_invalid_email_422_roster_validation_no_writes[vacio]` | module1_ingest_contracts.test.py:364 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_malformed_term_400_no_mutation` | module1_ingest_contracts.test.py:187 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_non_admin_actor_403_no_mutation` | module1_ingest_contracts.test.py:267 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule` | module1_ingest_contracts.test.py:386 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_queue_full_503_no_mutation` | module1_ingest_contracts.test.py:407 | E3-S1 | RED (xfail, NotImplementedError) |
| test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_id_generator_failure_503_no_writes_no_credentials | module1_ingest_contracts.test.py:429 | E3-S1 | RED (xfail, NotImplementedError; R12-B01) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_ingest_student_token_403_admin_before_batch_syntax` | module1_ingest_contracts.test.py:320 | E3-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_contracts.test.py::TestPreconditions::test_roster_intra_batch_duplicate` | module1_ingest_contracts.test.py:247 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[EXPELLED]` | module1_ingest_rules_contracts.test.py:43 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_barred_identity_rejects_whole_batch_422[SUSPENDED]` | module1_ingest_rules_contracts.test.py:43 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_conflicting_identity_row_422_no_identity_update` | module1_ingest_rules_contracts.test.py:70 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored` | module1_ingest_rules_contracts.test.py:121 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_credential_lookup_by_key_prefix_then_verifies_hash` | module1_ingest_rules_contracts.test.py:148 | E3-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[COMPLETED]` | module1_ingest_rules_contracts.test.py:92 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[DROPPED]` | module1_ingest_rules_contracts.test.py:92 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestInvariants::test_ingest_same_role_on_inactive_membership_not_reactivated[SUSPENDED]` | module1_ingest_rules_contracts.test.py:92 | E3-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_ingest_rules_contracts.test.py::TestSecrets::test_ingest_secret_in_batch_field_never_in_manifest_or_logs` | module1_ingest_rules_contracts.test.py:182 | E3-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestExplainability::test_explain_deny_expired_threshold_reports_expires_at` | module1_resolve_contracts.test.py:575 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allow_appends_one_authorization_event` | module1_resolve_contracts.test.py:70 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_cpu_toy_model_cs101` | module1_resolve_contracts.test.py:115 | E4-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_allows_student_inference_cs480` | module1_resolve_contracts.test.py:50 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestHappyPath::test_resolve_before_granted_uses_base_role` | module1_resolve_contracts.test.py:94 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_escalation_boundary_expires` | module1_resolve_contracts.test.py:442 | E4-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_drop_isolates_other_course_and_logs_each_deny` | module1_resolve_contracts.test.py:532 | E2-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_after_revoke_commit_denies_enrollment_dropped` | module1_resolve_contracts.test.py:472 | E2-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_deny_response_has_no_quota_or_priority_fields` | module1_resolve_contracts.test.py:554 | E4-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_model_outside_catalog_denied` | module1_resolve_contracts.test.py:489 | E4-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_queue_full_503_no_decision_no_mutation` | module1_resolve_contracts.test.py:511 | E1-S2 | RED (xfail, NotImplementedError) |
| test/atdd/module1_resolve_contracts.test.py::TestInvariants::test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation | module1_resolve_contracts.test.py:536 | E1-S2 | RED (xfail, NotImplementedError; R12-B01) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_arn_grammar_rejects` | module1_resolve_contracts.test.py:173 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_auth_token_invalid_401_before_arn_validation` | module1_resolve_contracts.test.py:284 | E4-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_header_cs101_arn_cs480_mismatch_403` | module1_resolve_contracts.test.py:378 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[EXPELLED]` | module1_resolve_contracts.test.py:312 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_denies_before_membership[SUSPENDED]` | module1_resolve_contracts.test.py:312 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_identity_barred_precedes_subject_mismatch` | module1_resolve_contracts.test.py:334 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_invalid_at_400_no_mutation` | module1_resolve_contracts.test.py:193 | E4-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_lowercase_course_header_404_unknown_course` | module1_resolve_contracts.test.py:400 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_malformed_action_400_no_mutation` | module1_resolve_contracts.test.py:213 | E4-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_missing_identity_and_course_reports_identity_first` | module1_resolve_contracts.test.py:418 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_resource_subject_mismatch_403_explained_no_mutation` | module1_resolve_contracts.test.py:234 | E4-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4` | module1_resolve_contracts.test.py:259 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[COMPLETED]` | module1_resolve_contracts.test.py:354 | E2-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_suspended_or_completed_membership_denies_context_missing[SUSPENDED]` | module1_resolve_contracts.test.py:354 | E2-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_course_404_no_mutation` | module1_resolve_contracts.test.py:154 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestPreconditions::test_resolve_unknown_identity_404_no_mutation` | module1_resolve_contracts.test.py:137 | E1-S2 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestSecrets::test_resolve_secret_in_action_400_never_echoed_in_clear` | module1_resolve_contracts.test.py:597 | E4-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_request_now_captured_once_and_reused_as_occurred_at` | module1_resolve_contracts.test.py:628 | E1-S2 | RED (xfail, NotImplementedError) (Ronda 11, H-16 / T-RES-05, añadida en K-2) |
| `test/atdd/module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_effective_role_is_exact_roles_id` | module1_resolve_contracts.test.py:656 | E4-S1 | RED (xfail, NotImplementedError) (Ronda 11, H-26 / T-RES-09, añadida en K-2) |
| `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_already_revoked_cites_ad03` | module1_revoke_contracts.test.py:626 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestExplainability::test_explain_first_revoke_reports_credentials_revoked` | module1_revoke_contracts.test.py:643 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_active_pair_returns_revoked` | module1_revoke_contracts.test.py:46 | E2-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_all_credentials` | module1_revoke_contracts.test.py:85 | E2-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestHappyPath::test_revoke_emits_one_membership_revoked_event` | module1_revoke_contracts.test.py:65 | E2-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_busy_timeout_exhausted_503_no_partial_commit` | module1_revoke_contracts.test.py:538 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_clock_failure_503_fail_closed_no_mutation` | module1_revoke_contracts.test.py:406 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_concurrent_double_drop_single_mutation` | module1_revoke_contracts.test.py:490 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_preserves_other_course` | module1_revoke_contracts.test.py:367 | E2-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_replay_idempotent` | module1_revoke_contracts.test.py:437 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_store_failure_closed` | module1_revoke_contracts.test.py:384 | E2-S3 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_timestamp_at_tolerance_boundary_accepted` | module1_revoke_contracts.test.py:522 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_auth_token_invalid_401_before_body_validation` | module1_revoke_contracts.test.py:220 | E2-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_281_chars_400_no_mutation` | module1_revoke_contracts.test.py:293 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[del]` | module1_revoke_contracts.test.py:274 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[newline]` | module1_revoke_contracts.test.py:274 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_drop_reason_control_char_400_no_mutation[nul]` | module1_revoke_contracts.test.py:274 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_empty_reason_and_missing_timestamp_rule_ids_order` | module1_revoke_contracts.test.py:312 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_future_timestamp_400_no_mutation` | module1_revoke_contracts.test.py:198 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_malformed_drop_reason_400_no_mutation` | module1_revoke_contracts.test.py:147 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_never_enrolled_pair_404_membership_not_found` | module1_revoke_contracts.test.py:105 | E2-S1 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_non_admin_actor_403_no_mutation` | module1_revoke_contracts.test.py:168 | E2-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_student_token_403_admin_before_drop_reason_syntax` | module1_revoke_contracts.test.py:247 | E2-S4 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_suspended_membership_409_invalid_transition` | module1_revoke_contracts.test.py:125 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fecha-inexistente]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[fraccion-7-digitos]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-menos-cero]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[offset-no-utc]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[segundo-60]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestPreconditions::test_revoke_timestamp_outside_rfc3339_grammar_400[sin-hora]` | module1_revoke_contracts.test.py:344 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear` | module1_revoke_contracts.test.py:592 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_revoke_contracts.test.py::TestSecrets::test_no_secret_leak_in_drop_reason` | module1_revoke_contracts.test.py:570 | E2-S5 | RED (xfail, NotImplementedError) |
| `test/atdd/module1_guard_contracts.test.py::TestDDLGuards::test_guard_escalation_expires_after_granted_check` | module1_guard_contracts.test.py:250 | E4-S2 | VERDE (Ronda 11, H-21c) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[os.urandom]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[from-os-urandom]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[uuid4]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[secrets]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[time.monotonic]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[datetime.now]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestDomainPurity::test_domain_purity_lint_detects_each_nondeterminism_source[random]` | module1_guard_contracts.test.py:414 | E1-S1 | VERDE (Ronda 11, H-25) |
| `test/atdd/module1_guard_contracts.test.py::TestErrorEnvelope::test_guard_audit_log_tampering_500_uses_error_body_without_explanation` | module1_guard_contracts.test.py:433 | E1-S3 | VERDE (Ronda 11, F-06) |
| `test/atdd/module1_ingest_contracts.test.py::TestRequestTimeInRejection::test_roster_rejected_occurred_at_reuses_single_request_now` | module1_ingest_contracts.test.py:662 | E3-S2 | RED (xfail, NotImplementedError) (Ronda 11, H-16) |
| `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_term_percent_encoded_decoded_once` | module1_ingest_contracts.test.py:698 | E3-S1 | RED (xfail, NotImplementedError) (Ronda 11, H-18) |
| `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[inexistente]` | module1_ingest_contracts.test.py:723 | E3-S1 | RED (xfail, NotImplementedError) (Ronda 11, H-18) |
| `test/atdd/module1_ingest_contracts.test.py::TestTermAndPathTransport::test_http_roster_path_course_unknown_404_unknown_course[minusculas]` | module1_ingest_contracts.test.py:723 | E3-S1 | RED (xfail, NotImplementedError) (Ronda 11, H-18) |
| `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-igual]` | module1_resolve_contracts.test.py:682 | E4-S4 | RED (xfail, NotImplementedError) (Ronda 11, H-24) |
| `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[repetido-distinto]` | module1_resolve_contracts.test.py:682 | E4-S4 | RED (xfail, NotImplementedError) (Ronda 11, H-24) |
| `test/atdd/module1_resolve_contracts.test.py::TestHttpTransport::test_authorize_subject_context_repeated_or_empty_is_absent[vacio]` | module1_resolve_contracts.test.py:682 | E4-S4 | RED (xfail, NotImplementedError) (Ronda 11, H-24) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[solo-espacios]` | module1_revoke_contracts.test.py:463 | E2-S5 | RED (xfail, NotImplementedError) (Ronda 11, F-01) |
| `test/atdd/module1_revoke_contracts.test.py::TestInvariants::test_revoke_dropped_invalid_reason_400_before_replay[control-nul]` | module1_revoke_contracts.test.py:463 | E2-S5 | RED (xfail, NotImplementedError) (Ronda 11, F-01) |
| `test/test_harness_smoke.py::test_db_has_ddl_tables` | test_harness_smoke.py:18 | E1-S1 | VERDE |
| `test/test_harness_smoke.py::test_fake_clock_advances` | test_harness_smoke.py:36 | E1-S1 | VERDE |
| `test/test_harness_smoke.py::test_fake_id_generator_deterministic` | test_harness_smoke.py:41 | E1-S1 | VERDE |
| `test/test_harness_smoke.py::test_seed_fleet_topology` | test_harness_smoke.py:8 | E1-S1 | VERDE |

---

## 11. Mapeo de los 20 nodos nuevos (K-2, 2026-10-14) y recálculo de métricas

Ronda 11 (H-16, H-18, H-21c, H-24, H-25, F-01, F-06, H-26 y T-RES-05/T-RES-09). Colección previa de esta matriz: 132; actual: 152. La diferencia de 20 se compone de 18 nodos que ya estaban en §10 con la marca «Ronda 11» y 2 nodos (T-RES-05 y T-RES-09) que faltaban en §10. Las dos categorías están ahora mapeadas. Los requisitos citados son los del PRD y los AD-n los de la fuente de decisión (`ARCHITECTURE.md` / `ARCHITECTURE-SPINE.md`). Cuando el docstring no declara AD, se indica.

| Test (función) | Nodos | Decisión / ID | Requisito (PRD) | AD-n | Historia | Riesgo (`test-design.md` §1) |
|---|---|---|---|---|---|---|
| `test_authorize_subject_context_repeated_or_empty_is_absent` (`module1_resolve_contracts.test.py:682`) | 3 | H-24, T-RES-H24 | EDGE-01 (P0) | AD-01, AD-09 | E4-S4 | R-001 |
| `test_revoke_dropped_invalid_reason_400_before_replay` (`module1_revoke_contracts.test.py:463`) | 2 | F-01, T-REV-F01 | FR-REVOC-03 (P0) | AD-03 (replay idempotente) | E2-S5 | R-003 |
| `test_guard_escalation_expires_after_granted_check` (`module1_guard_contracts.test.py:250`) | 1 | H-21c, T-ESC-GUARD-04 (guard, VERDE) | FR-ESCAL-02 (P0) | AD-13 | E4-S2 | R-008 |
| `test_http_roster_term_percent_encoded_decoded_once` (`module1_ingest_contracts.test.py:698`) | 1 | H-18, T-ROS-H18a | FR-INGEST-01 (P0) | Ninguno declarado en el docstring (transporte HTTP, AD-09 por contexto) | E3-S1 | — |
| `test_http_roster_path_course_unknown_404_unknown_course` (`module1_ingest_contracts.test.py:723`) | 2 | H-18, T-ROS-H18b | FR-INGEST-01 (P0) | AD-09 (spine-local) | E3-S1 | — |
| `test_guard_audit_log_tampering_500_uses_error_body_without_explanation` (`module1_guard_contracts.test.py:433`) | 1 | F-06, T-ERR-GUARD-01 (guard, VERDE) | FR-AUDIT-04 (P0; `AUDIT_LOG_TAMPERING_DETECTED`, emisor fuera de alcance) | AD-04 | E1-S3 | R-004 |
| `test_resolve_request_now_captured_once_and_reused_as_occurred_at` (`module1_resolve_contracts.test.py:628`) | 1 | H-16, T-RES-05 | FR-ESCAL-02 (P0, frontera temporal) y FR-AUDIT-04 (P0, `occurredAt`) | AD-13 | E1-S2 | R-008 |
| `test_roster_rejected_occurred_at_reuses_single_request_now` (`module1_ingest_contracts.test.py:662`) | 1 | H-16, T-ROS-H16 | FR-INGEST-01 (P0, rechazo 422 con `roster.rejected`) | AD-13 | E3-S2 | R-008 |
| `test_resolve_effective_role_is_exact_roles_id` (`module1_resolve_contracts.test.py:656`) | 1 | H-26, T-RES-09 | EDGE-01 (P0, `effective_role` exacto) | AD-10 | E4-S1 | R-009 |
| `test_domain_purity_lint_detects_each_nondeterminism_source` (`module1_guard_contracts.test.py:414`) | 7 | H-25, T-PUR-GUARD-02 (guard, VERDE) | Sin requisito PRD propio (pureza de dominio) | AD-08 | E1-S1 | — |

**Conteo de los 20 nodos nuevos:** H-24 3, F-01 2, H-21c 1, H-18 3, F-06 1, H-16 2, H-26 1, H-25 7. Total 20. Clasificación: 11 atdd-red (RED por `NotImplementedError`) y 9 guardas en verde.

**Recálculo de métricas (K-2):**

| Métrica | Antes (corrida previa a K-2, §1) | Ahora (K-2) | Motivo |
|---|---|---|---|
| M1a. P0 con historia y test RED | 7/7 (100%) | 7/7 (100%) | Sin cambio; los nodos nuevos refuerzan R-001, R-003, R-008 y R-009 |
| M1b. Riesgos P0 con historia y test RED | 7/7 (100%) | 7/7 (100%) | Sin cambio |
| M2a. AD-n con test que se pone rojo | 13/13 | 13/13 | Sin cambio |
| M2b. AD-n con todas sus cláusulas cubiertas | 8/13 | 8/13 | AD-01 cierra su excepción H-24, pero ya estaba contado como completo. AD-03 sigue parcial (proceso único sin test) |
| P0 FULL en lectura especificada | 2/7 (29%) | 2/7 (29%) | Ningún P0 pasa de PARTIAL a FULL (ver §7) |
| Gate del skill | FAIL (Regla 1) | FAIL (Regla 1) | `step-05-gate-decision.md`, Regla 1: P0 < 100 |

**Verificaciones de la ejecución (K-2):**
- `.venv/bin/pytest --collect-only -q` = 152 nodos. `.venv/bin/pytest -q` = 25 passed, 127 xfailed.
- `.venv/bin/pytest -q --runxfail -m atdd --tb=line` = 127 failed. Causa por stub (`cut` del mensaje): `ingestRoster` 37, `revokeCourseAccess` 36, `resolveEffectivePermissions` 33, `http_*`/`parse_*`/`declared_routes` 15, `sweep_expired` 4, `clamp_page_size` 2. Suma 127, todos `NotImplementedError`.
- Todos los nodos de la colección aparecen en `epics.md` (comprobado por nombre de función).

**Huérfanos recalculados (K-2):**
- (a) Requisito o cláusula sin historia: sin cambio (FR-ESCAL-02 y FR-AUDIT-04 fuera de alcance, §5a).
- (b) Requisito sin test que mida su criterio: sin cambio (NFR-PERF-01, NFR-PERF-02, NFR-REVOC-03, NFR-SEC-04, NFR-AUDIT-06, NFR-DISP-07).
- (c) Historia sin requisito: 0 de 16.
- (d) Test sin requisito: 4 de 152 (harness). Los 20 nodos nuevos trazan a AD-n o a requisito.
- Test sin historia: 0 de 152.

### Ronda 12 (R12-B01, SEC B-01): nodos nuevos del mapeo de §11

| Test (función) | Nodos | Decisión / ID | Requisito (PRD) | AD-n | Historia | Riesgo (`test-design.md` §1) |
|---|---|---|---|---|---|---|
| `test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation` (`module1_resolve_contracts.test.py:536`) | 1 | R12-B01, T-RES-15 | PRD §7.3 (fail-closed, `AUTH_INTERNAL_POLICY_UNAVAILABLE`, 503) | AD-08, AD-12 | E1-S2 | R-008 |
| `test_ingest_id_generator_failure_503_no_writes_no_credentials` (`module1_ingest_contracts.test.py:429`) | 1 | R12-B01, T-ROS-21 | PRD §7.3 (fail-closed, `AUTH_INTERNAL_POLICY_UNAVAILABLE`, 503) | AD-12, AD-02 | E3-S1 | — |

**Conteo:** 2 nodos atdd-red nuevos (RED por `NotImplementedError`). Colección: 152 → 154. `pytest -q` → 25 passed, 129 xfailed. `pytest -q --runxfail -m atdd --tb=line` → 129 `NotImplementedError`. Revoke (Q-fail con `Clock`/`IdGenerator`/`QueueReservation`) queda sin nodo RED: DEFER a TEA, registrado en `contracts.md` §2. Cerrado en Ronda 13 (K-16): T-REV-12 (§11, Ronda 13).

### Ronda 13 (K-16, T-REV-12): nodo nuevo del mapeo de §11

| Test (función) | Nodos | Decisión / ID | Requisito (PRD) | AD-n | Historia | Riesgo (`test-design.md` §1) |
|---|---|---|---|---|---|---|
| `test_revoke_clock_failure_503_fail_closed_no_mutation` (`module1_revoke_contracts.test.py:406`) | 1 | R12-B01, K-16, T-REV-12 | PRD §7.3 (fail-closed, `AUTH_INTERNAL_POLICY_UNAVAILABLE`, 503) | AD-03, AD-12 | E2-S3 | R-003 |

**Conteo:** 1 atdd-red nuevo (RED por `NotImplementedError`). Colección: 154 → 155. `pytest -q` → 25 passed, 130 xfailed. `pytest -q --runxfail -m atdd --tb=line` → 130 `NotImplementedError`. Revoke Q-fail (`Clock`) deja de ser DEFER.
