# Review de seguridad ad-hoc — Reviewer Gate de `bmad-architecture`

- **Fecha:** 2026-10-12
- **Lente:** seguridad ad-hoc (stakes: RBAC académico, credenciales `uai_live_…`, ledger forense)
- **Alcance:** `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` + `solu2-module1/planning/detailed-design/contracts.md`
- **Reglas de autoridad:** AD-01 (aislamiento/binding), AD-03 (revocación), AD-04 (ledger+metadata), AD-05 (anti auto-aprobación), AD-06 (cero secretos), AD-10 (aislamiento EDGE-01), AD-12 (DB-autoridad sin caché inter-proceso)
- **Fuera de alcance:** implementación (stop-point de solutioning: stubs/RED permitidos, sin lógica productiva), NFR medidos, flujos de escalación fuera de las tres operaciones.

## Veredicto

**PASS condicionado — sin bloqueantes.** No se detecta fuga de privilegio entre contextos ni propagación del error crudo del edge-case hunter. El Mandatory Edge Case queda blindado a nivel de diseño. Se condiciona el pase a registrar 3 hallazgos medios como deuda de endurecimiento pre-build (ventana perimetral, canonicalización de `userId`, forense de lote rechazado + cola async) y 2 bajos (modos de fallo de Clock/Ledger, enumeración por códigos). Ninguno exige re-arquitectura; todos se cierran con aclaración de contrato + test RED.

## Hallazgos (ordenados por severidad)

### [M-01] Ventana de revocación perimetral de hasta 60 s — endurecer fail-closed en el borde
- **Severidad:** Media.
- **Dónde:** `contracts.md` §2 presupuesto (`corte perimetral < 60 s`), spine AD-03/AD-12.
- **Descripción:** la invalidación local es transaccional y rápida (< 200 ms, predicado condicional, revocación masiva en la misma transacción — correcto), pero el corte perimetral admite hasta 60 s. Durante esa ventana un token del par `(identity, course)` ya `DROPPED` podría seguir aceptado en el borde aunque `resolve` posterior ya deniegue con `SUBJECT_ENROLLMENT_DROPPED`.
- **Por qué no es bloqueante:** el diseño interno es fail-closed (fallo del store → `AUTH_INTERNAL_POLICY_UNAVAILABLE` 503, predicado por par, otro curso intacto, sin caché inter-proceso por AD-12). La ventana es de propagación, no de decisión.
- **Exigencia pre-build:** declarar el borde como deny-by-default (TTL corto de credencial, verificación contra autoridad o lista de revocación con freshness ≤ ventana), y añadir test RED `test_revoke_perimeter_denies_within_window` o documentar la ventana como riesgo aceptado con dueño. No declarar NFR-REVOC-03 como `EVIDENCED` sin medición.

### [M-02] `userId` / `institutional_id` sin canonicalización definida — riesgo de colisión/impersonación
- **Severidad:** Media.
- **Dónde:** `contracts.md` §0 (`courseId` con `strip + upper`; `userId` admite UUID o `institutional_id` sin regla), spine tabla de convenciones.
- **Descripción:** `courseId` tiene canonicalización explícita en el boundary y comparación byte a byte sobre formas canónicas (bien). Para `userId` no hay regla: no se define `strip`, case-folding, ni unicidad entre UUID e `institutional_id` (`stu-98432` vs `STU-98432`, espacios, guiones). Un atacante podría registrar/resolver variantes que resuelvan a identidades distintas o eludan la guarda `IDENTITY_BARRED` / la anti-role-smuggling por identidad.
- **Exigencia pre-build:** fijar canonicalización de `userId` en el adapter (p. ej. `strip`; UUID lowercase; `institutional_id` `strip + upper` si el dominio es case-insensitive, o comparación exacta documentada), unicidad declarada, y test RED `test_userid_canonicalization_rejects_variant`. Sin esto, el binding AD-01 queda cojo por el lado del sujeto.

### [M-03] Forense de lote rechazado ambiguo + cola async sin bound — riesgo de truncamiento de ledger
- **Severidad:** Media.
- **Dónde:** `contracts.md` §3 Q3/Q-fail (`emite un evento roster:ingest por lote comprometido… más anexo ante rechazo`), §6 open question (bound/desborde de cola async), spine AD-04.
- **Descripción:** Q3 puede leerse como que solo el lote comprometido emite evento; el rechazo dejaría 0 escrituras + manifiesto `roster_rejected_conflicts.csv` pero sin aclarar si el rechazo también escribe evento en el ledger. Si el rechazo no deja evento, un actor puede pulverizar lotes inválidos (fuzzing de roles/emails) sin traza. A esto se suma la cola async de auditoría sin bound ni política de desborde (open question heredada): bajo carga podría dropear eventos.
- **Por qué no es bloqueante:** el éxito sí encadena hash + `id ASC` + metadata singleton y bloquea exportación ante `AUDIT_LOG_TAMPERING_DETECTED` (bien). La repetición `ALREADY_REVOKED` sin evento redundante es correcta (no hay mutación).
- **Exigencia pre-build:** aclarar que todo rechazo 422 emite evento de auditoría (con `batch_id`, conteos, hash encadenado) además del anexo, y fijar política de la cola (bloqueante/fail-closed, nunca drop silencioso) con test RED `test_rejected_batch_audited` + `test_ledger_no_drop_under_pressure`. La repetición de baja puede seguir sin evento, pero considerar contador/rate-limit fuera del ledger.

### [B-01] Modos de fallo de `Clock`, `IdGenerator` y `LedgerWriter` en `resolve` no especificados — posible fail-open
- **Severidad:** Baja (sube a Media si el adapter defaultea a ALLOW).
- **Dónde:** `contracts.md` §1 (Q3 emite evento por decisión; tiempo del puerto `Clock`), spine AD-08/AD-13.
- **Descripción:** el fallo del store está cerrado (503 fail-closed — bien) y `SQLITE_BUSY` agotado es 503 (bien). Pero no se define qué pasa si `Clock` falla (¿`at` nulo sin reloj?), si `IdGenerator` colisiona, o si `LedgerWriter` falla en un `resolve` (lectura + evento): ¿se retorna la decisión sin auditar (gap forense) o se falla cerrado (503)? La expiración perezosa sin scheduler es correcta (AD-13), pero depende totalmente del reloj inyectado.
- **Exigencia pre-build:** regla explícita: fallo de `Clock`/`LedgerWriter` en el camino de decisión → `AUTH_INTERNAL_POLICY_UNAVAILABLE` 503 (fail-closed), nunca decisión sin evento; `batch_id` con colisión → reintento con nuevo id, nunca reutilización. Test RED `test_resolve_clock_failure_closed` + `test_resolve_ledger_failure_closed`.

### [B-02] Enumeración por códigos diferenciales y `observed_*` en explicación/manifiesto — limitar exposición
- **Severidad:** Baja.
- **Dónde:** `contracts.md` §1 P1/P5 + §4 catálogo (`UNKNOWN_IDENTITY` 404 vs `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` 403 vs `IDENTITY_BARRED` 403), §1 Q4 (`observed_role/context/resource_subject`), §3 Q3 (anexo CSV con `institutional_id/observed/expected`).
- **Descripción:** la distinción 404/403 permite enumerar identidades y membresías por oráculo (usuario válido/inválido, matriculado/no). Los `observed_*` de `ExplanationDTO` y el anexo de cuarentena son necesarios para explicabilidad (AD-11) y triage, pero deben acotarse al contexto solicitado: nunca incluir el rol del otro curso, ni email completo donde baste el campo, ni secretos.
- **Exigencia pre-build:** documentar la enumeración como riesgo aceptado de baja sensibilidad académica (o unificar respuesta para no autenticados si el threat model lo exige), y regla explícita: `explanation.observed_*` y anexo solo con datos del par `(identity, course)` solicitado; test RED `test_explanation_scoped_to_context` + extensión de `test_no_secret_leak` al anexo CSV.

## Verificación por categoría (todas revisadas)

| Categoría | Resultado | Evidencia / nota |
| --- | --- | --- |
| Fuga de privilegio entre contextos | ✅ Blindado | Spine AD-10: resolución solo de la tupla `(identity_id, course_id)`, nunca importa rol de otro curso; `resolve` no devuelve cuota GPU ni prioridad (ASSUMPTION-01). Contracts §1 Q2/I1 + §5 `test_edge01_context_isolation`. Revoke con predicado `WHERE (identity, course)` + §2 I1 `test_revoke_preserves_other_course`. |
| Mandatory Edge Case | ✅ Blindado | Fixture canónico Student en `CS101` / TA en `CS-480`, resolución independiente por contexto. AD-10 + contracts §5 rechazan explícitamente la aserción cruda del edge-case hunter (TA=Student en ambos). Sin GPU/prioridad en la respuesta se evita confundir `0 GPU` con `high priority` entre contextos. |
| Error crudo del edge-case hunter | ✅ No propagado | Búsqueda conceptual: ninguna regla devuelve rol unificado/global; toda lectura está acotada al par; la guarda de rol en ingesta impide elevar Student→TA por importación. |
| Bypass de canonicalización | ✅ Suficiente con 1 reserva (M-02) | `courseId`: `strip + upper` en boundary + comparación canónica byte a byte (bien). ARN `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$` rechaza `.`/`/`/reorden + `test_arn_grammar_rejects` (bien). Reserva: `userId` sin regla (M-02). `term` con regex y `email` acotado a `@universidad.edu` + `assigned_role ∈ {student, ta}` (bien; normalización case de email pendiente menor). |
| Ventanas de revocación / carreras | ✅ Diseño correcto, 1 ventana externa (M-01) | Baja atómica un-transacción con predicado (prohibido leer-luego-actualizar), doble baja → `ALREADY_REVOKED` sin mutación/evento, concurrentes serializados por predicado/`BEGIN IMMEDIATE`, `resolve` concurrente ve estado comprometido (AD-12, sin caché). Ingesta `BEGIN IMMEDIATE` con snapshot previo para `resolve` (correcto). Ventana restante: propagación perimetral 60 s (M-01). |
| Truncamiento de ledger | ✅ Estructura correcta, 1 ambigüedad (M-03) | Hash encadenado + metadata singleton + orden `id ASC` + `test_ledger_chain_and_anchor` + bloqueo de exportación ante tampering (bien). Ambigüedad: evento ante rechazo 422 + bound de cola async (M-03). |
| Secretos en respuestas/logs | ✅ Contenido correcto | Máscara `uai_live_<4>••••<4>`, claro solo en emisión inicial, `test_no_secret_leak` + regex de build (bien). Respuestas de `ingest`/`revoke`/`resolve` no portan secretos según contrato (bien). Extender el regex al anexo CSV (B-02). |
| Auto-aprobación | ✅ Cerrado | `FORBIDDEN_SELF_APPROVAL` 403 + índice único parcial `idx_single_active_escalation` + `CONCURRENT_ESCALATION_NOT_PERMITTED` 409 + guarda de rol en ingesta (elevación solo por workflow de escalación). Test `test_double_submit_single_ticket` (bien). Flujos de escalación fuera de alcance, correctamente diferidos. |
| Role-smuggling por ingesta | ✅ Cerrado | Rol entrante divergente sobre membresía existente → rechazo del lote (no eleva/sobrescribe); `seen_ids` pre-BD + validación en memoria + rollback total + `test_roster_row85_rollback` / `test_roster_no_role_smuggling` / `test_roster_intra_batch_duplicate`; `SUSPENDED/EXPELLED` → `IDENTITY_BARRED` (bien). |
| Fail-open ocultos | ✅ Sin fail-open interno, 1 externo (M-01) + 1 indefinido (B-01) | Store/`SQLITE_BUSY` → 503 fail-closed; tampering → 500 + bloqueo de exportación; `page_size` forzado al rango (no error, bien); intervalo `[granted_at, expires_at)` con `at >= expires_at → DENY` y `Clock` falso (bien). Indefinido: fallo de `Clock`/`LedgerWriter` en `resolve` (B-01). |

## Condiciones para mantener el PASS

1. Registrar M-01/M-02/M-03 en el backlog pre-build con dueño y test RED asociado; no requieren cambiar el spine, solo precisar `contracts.md`.
2. Añadir B-01/B-02 como criterios de aceptación de los adapters (inbound authorize/roster + `LedgerWriter`).
3. No marcar NFR (latencias, revocación, ingesta) como `EVIDENCED` sin benchmark real; hoy correctamente en `PLANNED`.
4. Re-ejecutar esta lente tras cualquier cambio a AD-01/AD-03/AD-04/AD-05/AD-06/AD-10/AD-12 o al catálogo de errores.

## Nota de trazabilidad

- Seed Table: Annex A p. 13 (tres candidatas confirmadas 2026-10-12) — sin cambios; esta revisión no añade operaciones.
- Mandatory Edge Case literal: "Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently" → cubierto por AD-10 + EDGE-01 + `test_edge01_context_isolation`.
- Sin contradicciones nuevas PRD/UX/AD detectadas en este alcance; las `[ASSUMPTION]` de §6 (reingesta con `batch_id` nuevo, `term`, `page_size`) no abren superficie de seguridad.
