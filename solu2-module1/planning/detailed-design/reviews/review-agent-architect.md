# Reporte de auditoría — Winston (bmad-agent-architect) — Fase 1

- **Fecha:** 2026-10-12
- **Alcance auditado (borrador, no aprobado):**
  - `solu2-module1/planning/detailed-design/contracts.md`
  - `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (status: `draft`)
- **Autoridades (read-only):**
  - `planning/prd.md` v1.0.0
  - `planning/ARCHITECTURE.md` v1.0.0 (AD-01 a AD-07)
  - `ux/EXPERIENCE.md` v1.0.0
  - `ux/C-UX-Scenarios/00-ux-scenarios.md`, `scenario-1.md`, `scenario-2.md`, `scenario-3.md`, `scenario-4.md`
  - Triage propuesto (no decisión firmada): `solu2-module1/planning/detailed-design/reviews/review-arch-implementability.md`
  - Memlog: `solu2-module1/planning/detailed-design/architecture-spine/.memlog.md`
- **Veredicto explícito:** spine **NO APROBADA**. Este reporte no cierra ningún gate, no declara PASS y no modifica ni `contracts.md` ni `ARCHITECTURE-SPINE.md`.
- **Regla aplicada:** todo asunto que altere comportamiento queda como **pregunta abierta**; no se inventa ninguna decisión del equipo. Solo se sugiere cambio mínimo cuando es puramente editorial/trazabilidad sin efecto conductual.

## Resumen operativo

| # | Hallazgo | Prioridad | Tipo |
|---|----------|-----------|------|
| W-01 | `strip+upper` en boundary vs byte-a-byte de AD-01 | Alta | Pregunta abierta |
| W-02 | Catálogo sin código de éxito; `decision CHECK(ALLOW,DENY)` vs eventos roster/revoke | Alta | Pregunta abierta |
| W-03 | Ledger en rechazo + sync vs async + bound/desborde de cola + fail-closed | Alta | Pregunta abierta |
| W-04 | Caché de revocación vs DB-autoridad | Alta | Pregunta abierta |
| W-05 | Scheduler de expiración vs expiración perezosa | Alta | Pregunta abierta |
| W-06 | Sin 401 / validación de token fuera de P | Alta | Pregunta abierta |
| W-07 | Vocabularios de estado incompletos (`INACTIVE`, `EXPIRED`, `COMPLETED`, `PENDING_APPROVAL` vs `PENDING`) | Alta | Pregunta abierta |
| W-08 | Tabla §5 sin filas AD-07/AD-08/AD-09 | Media | Cambio editorial sugerido |
| W-09 | HTTP mapping: nombres de path-params, cuerpo del drop, transporte de `at`/`term` | Media | Parcial editorial + pregunta abierta |
| W-10 | `STRICT` vs aborto total; rol divergente rechaza vs ignora; manifiesto | Media | Pregunta abierta |
| W-11 | Gramáticas exactas por campo (email, institutional_id, ARN, term, `at`) | Media | Parcial editorial + pregunta abierta |
| W-12 | `ExplanationDTO` sin schema cerrado por operación; UX E-01–E-04 sin campo de acción | Media | Pregunta abierta |
| W-13 | Orden validación→transacción→ledger; `SQLITE_BUSY`; predicado single-statement | Media | Parcial editorial + pregunta abierta |
| W-14 | Reingesta no idempotente; receipt `ALREADY_REVOKED` con claves inconsistentes | Media | Pregunta abierta + editorial menor |
| W-15 | NFR correctamente PLANNED; contradicciones dataset/concurrencia ya abiertas | Baja | Conforme con reserva |
| W-16 | Fórmula del hash con dos variantes en el padre; `reason_code` ledger | Media | Pregunta abierta |

Cobertura Annex A verificada en §7. Trazabilidad por operación en §1–§3.

---

## 1. `resolveEffectivePermissions(userId, courseId, at)` — P/Q/I

Evidencia base: `contracts.md` §0 l.9–15, §1 l.17–38; spine AD-01/AD-10/AD-11/AD-13.

- **P1–P4 conformes en estructura.** Resolución `userId` UUID o `institutional_id` a identidad canónica en adapter (triage EC-05 ACCEPT) es coherente con `planning/ARCHITECTURE.md` §3 `identities.id` + `institutional_id UNIQUE`.
- **P5 mezcla dos denegaciones distintas** (`SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` vs `RESOURCE_SUBJECT_MISMATCH`, 403) bajo una sola precondición. Impacto: dos unidades pueden elegir distinto código para "sin membresía pero recurso ajeno" vs "con membresía pero recurso ajeno". No propongo precedencia; ver Pregunta Q-A.
- **Orden P5 (barred global antes de membresía)** es conforme con triage EC-09 ACCEPT, pero el padre no fija si el intento denegado por `IDENTITY_BARRED` emite evento de auditoría (Q-fail solo dice "si falla P5 solo se registra el intento denegado", sin distinguir sub-caso). Ver Pregunta Q-B.
- **Q1 menciona rol escalado vigente** (`granted_at <= at < expires_at`). El workflow solicitud/aprobación es out-of-scope de las tres operaciones (memlog + Deferred spine), pero la *lectura* del ticket sí pertenece a resolve. Conforme con no añadir operaciones; el borde `[granted_at, expires_at)` sigue propuesto pendiente de confirmación contra AD/PRD (triage EC-03/AR-07 propuesta). Ver Pregunta Q-C.
- **Q2 aislamiento EDGE-01 conforme.** Bien ligado a `EDGE-01 Multi-Subject Permission Resolution` y PRD §5. Detalle en §7.
- **Q3 auditoría subespecificada:** `eventId`, `occurredAt`, `decision`, `reason_code`, hash "según AD-04". No fija: (a) si DENY por P1–P4 emite o no evento; (b) qué `reason_code` porta un ALLOW; (c) orden respecto a la respuesta con cola async (ver W-03); (d) cuál de las dos fórmulas del padre es normativa (ver W-16). Preguntas abiertas.
- **Q4 `explanation` con `rule_ids` no vacío + observados + umbral.** Conforme con AD-11 y banners E-01/E-03 en intención, pero sin schema cerrado por operación (ver W-12).
- **Concurrencia/idempotencia §1 l.36 ("lectura pura; la BD es la autoridad, AD-12"):** coherente con DB-autoridad, pero contradice la arquitectura padre que sí define `revoked_credentials_cache` (ver W-04). No se resuelve aquí.
- **Tiempo §1 l.37 (puerto `Clock`, intervalo `[granted_at, expires_at)`, expiración perezosa):** coherente con spine AD-13, en conflicto con scheduler del PRD (ver W-05).

## 2. `revokeCourseAccess(userId, courseId)` — P/Q/I

Evidencia: `contracts.md` §2 l.40–60; PRD §4.3 FR-REVOC-03; `scenario-3.md`; AD-03.

- **P1 conforme** (misma resolución que §1).
- **P2 acotada correctamente a las tres operaciones**, pero incompleta frente al DDL padre: cubre `ACTIVE`/`DROPPED`/`SUSPENDED`/`COMPLETED`; deja fuera `INACTIVE` de `[ASSUMPTION-03]` PRD §9.1 y no aclara `EXPIRED` de credenciales (¿se revocan o se dejan?). Ver Pregunta Q-D.
- **P3 `drop_reason` 1–280 conforme en rango**, pero el PRD §4.3 exige además `timestamp` ISO-8601 de la transacción académica y el endpoint del escenario emite `db_transition_ms`/`cache_invalidation_ms`. `contracts.md` fija `revocation_propagated_at`/`dropped_at` del `Clock` y no transporta el `timestamp` entrante. Ver Pregunta Q-E (parte de W-09).
- **Q1–Q2 transición + revocación masiva en una sola transacción con predicado condicional:** conforme con AD-03 y triage EC-12 ACCEPT. "Sin leer y luego actualizar en dos pasos" es el enforcement correcto.
- **Q3 "exactamente un evento; repetición sobre `DROPPED` no emite redundante":** conforme con AD-03. Queda abierto si el primer evento usa `decision` ALLOW o DENY y qué `reason_code` (ver W-02), y si va dentro o fuera de la transacción con cola async (ver W-03).
- **Q4 `explanation` con AD-03 + `observed_prior_status` + `observed_credentials_revoked`:** bien orientado; falta cerrar si `observed_credentials_revoked` cuenta solo las que estaban `ACTIVE` o también intentos sobre `EXPIRED` (pregunta, no decisión).
- **Repetición 200 `ALREADY_REVOKED` sin mutación ni evento:** conforme con AD-03 + triage EC-10 ACCEPT. Inconsistencia menor de forma: Q1 usa claves `{ student_id, subject_id, status: REVOKED, revocation_propagated_at }` y Repetición usa `{ status: ALREADY_REVOKED, revoked_at: <original> }` — claves distintas (`revocation_propagated_at` vs `revoked_at`). Cambio mínimo sugerido (solo forma, sin alterar semántica): unificar el nombre de la clave del instante en ambos receipts cuando el equipo lo confirme; no lo impongo aquí.
- **I1–I3 bound a AD-03 / AD-03+AD-12:** correcto como AD-n existente. Enforcement (predicado `WHERE identity_id AND subject_id`, revocación masiva, fail-closed 503) y tests RED nombrados son verificables en intención.
- **Concurrencia §2 l.58 ("una gana el predicado, la otra observa `DROPPED`"):** conforme con triage EC-01 ACCEPT-reformulado en intención; depende de W-04 (sin caché mutable) y W-13 (single-statement vs `BEGIN IMMEDIATE`).

## 3. `ingestRoster(batch)` — P/Q/I

Evidencia: `contracts.md` §3 l.62–83; PRD §4.1 FR-INGEST-01 + §7.2; `scenario-1.md`; AD-02.

- **P1 `subject_id` activo + `term ^[0-9]{4}-(SPRING|SUMMER|FALL)$`:** conforme con PRD `2026-FALL` como instancia y `[ASSUMPTION] term canónico` de contracts §6. Transporte de `term` (path vs body vs query) no fijado; ver W-09.
- **P2 límites 1–1000 filas, ≤5 MB, UTF-8, columnas exactas:** los 5 MB / columnas vienen de `scenario-1.md` (modal, etiqueta de formato), no del PRD; está bien citarlos pero la trazabilidad debería decirlo. Cambio mínimo sugerido (editorial, sin efecto conductual): anotar en §3-P2 "límite 5 MB y columnas según `scenario-1.md`", cuando el equipo lo valide.
- **P3 fila (`@universidad.edu`, alfanumérico con guiones, `{student, ta}`):** dirección correcta; gramática exacta pendiente (ver W-11). El código por fila `ROSTER_VALIDATION_FAILED` 422 con `row_number` es coherente con PRD fila 85 → 422 + rollback 0 filas. El mapeo con la regla UX `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL` (`EXPERIENCE.md` §2.3 caso A) no está declarado; ver W-12.
- **P4 duplicados `seen_ids` + barred global:** conforme con AD-02 y triage EC-06/EC-09. Bien que barred global rechace con manifiesto 422.
- **Q1 201 + `batch_id roster-<8hex>-<term>` del `IdGenerator`:** conforme con AD-08 (azar por puerto). Ejemplo PRD `roster-b89f-2026` tiene forma distinta; no es contradicción si el ejemplo es ilustrativo, pero conviene anotarlo como formato canónico pendiente de confirmación (pregunta menor, no bloqueo).
- **Q2 todo o nada + "solo en claro aquí":** conforme con AD-02 + AD-06. Orden exacto validación→transacción y ledger dentro/fuera: ver W-13.
- **Q3 evento `roster:ingest` + anexo CSV:** el anexo `roster_rejected_conflicts.csv (row_number, institutional_id, field, observed, expected)` es coherente con PRD §4.1 R3 y §7.2. Queda abierto: (a) si el rechazo emite evento ledger DENY o cero eventos (ver W-03/P4 adversarial); (b) qué `decision`/`reason_code` porta el evento de éxito (ver W-02).
- **Anti-role-smuggling ("rol entrante divergente se rechaza con el lote"):** elige una de las dos lecturas del padre (PRD §7.2 Colisión A contempla `STRICT` aborta vs segrega; AD-02 §5 R3 dice "rechazado o ignorado"). Endurece a "rechaza el lote". Es cambio conductual: ver Pregunta Q-F (W-10).
- **I1–I2 bound a AD-02 / AD-02+AD-05:** correcto. Enforcement (`BEGIN IMMEDIATE` + rollback, guarda de rol) y tests (`test_roster_row85_rollback`, `test_roster_no_role_smuggling`) verificables en intención.
- **I3 reingesta con `batch_id` nuevo (no idempotente por contenido):** marcado como `[ASSUMPTION]` en §6 — correcto no presentarlo como decisión. Ver Pregunta Q-G.
- **Concurrencia §3 l.81 ("snapshot previo, nunca medio lote; fail-closed ante `SQLITE_BUSY`: 503"):** dirección correcta (triage EC-16 ACCEPT); falta bound de espera/`busy_timeout` y si lectores usan `BEGIN IMMEDIATE` o lectura ordinaria. Ver W-13.

## 4. Conflicto explícito W-01: `strip+upper` vs byte-a-byte AD-01

- **Evidencia:**
  - `contracts.md` §0 l.15: "`courseId` se canonicaliza en el boundary con `strip + upper` (`cs-480` → `CS-480`); la comparación recurso↔contexto de AD-01 corre sobre formas canónicas con comparación byte a byte".
  - Spine §Consistency Conventions l.96: "Canonicalización `strip + upper` en el boundary antes de comparar; grafías minúsculas de los ejemplos son variantes de presentación".
  - Padre `planning/ARCHITECTURE.md` AD-01 l.329–331: regex `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$` y "no coincide byte a byte con el valor del encabezado obligatorio `X-Academic-Subject-Context`".
  - Memlog l.23 ya lo deja como `question` abierto, sin resolución silenciosa. Rubric l.12 y adversarial P1 lo confirman.
- **Impacto (Alta):** dos unidades conformes divergen: U-A compara crudos (`cs-480` vs `CS-480` → 403 `RESOURCE_SUBJECT_MISMATCH`); U-B canonicaliza (→ ALLOW). La misma fractura alcanza `userId`/`institutional_id`/`email` sin función canónica declarada. Altera ALLOW/DENY del Mandatory Edge Case si el fixture usa minúsculas (los ARN de ejemplo del PRD/arquitectura van en minúsculas: `urn:uai:subject:cs-480:…`).
- **Cambio mínimo:** ninguno aquí por ser conductual. **Pregunta abierta Q-H** (ver §8). No se debilita AD-01 heredada read-only.

## 5. Errores de ledger / status / `reason_code` (W-02, W-16)

- **Evidencia:**
  - `contracts.md` §4 catálogo (l.85–114): 24 entradas, sin `SUCCESS`; nota l.114 sobre `page_size`; spine AD-11 l.77–78: "ningún código fuera del catálogo llega a la respuesta".
  - Padre `planning/ARCHITECTURE.md` §3 DDL l.189 `reason_code` ej. `'SUCCESS', 'RESOURCE_SUBJECT_MISMATCH', 'SUBJECT_ENROLLMENT_DROPPED'`; §4.2 l.311–312 `reason='SUCCESS'` en ALLOW; §3 l.188 `decision CHECK(ALLOW,DENY)`.
  - Padre AD-04 l.363–366 fórmula con `subject_id`, `action`; §2 l.94–96 fórmula sin esos campos (dos variantes).
- **Impacto (Alta/Media):**
  1. Todo ALLOW, todo `roster:ingest` 201 y `ALREADY_REVOKED` quedan sin `reason_code` válido aunque AD-11 exige `rule_ids` no vacío. Dos unidades conformes divergen (unión total de `observed_*` vs mínimo; código inventado vs omisión).
  2. `audit_ledger.decision CHECK(ALLOW,DENY)` no admite un evento `roster:ingest` exitoso ni una baja 200 sin forzar ALLOW/DENY ficticio.
  3. `AUDIT_LOG_TAMPERING_DETECTED` 500 no pertenece a ninguna de las tres operaciones (es de verificación/exportación, `GET /audit` es FR-AUDIT-04 fuera de las tres candidatas). Su presencia en el catálogo sin emisor confunde enforcement/test.
  4. Sin 401 en el catálogo aunque PRD §5.2 (token inválido→401), §7.1 (401/403), `EXPERIENCE.md` §2.5 (401 re-auth) y arquitectura §4.2 (paso 1 credencial vs revocation cache) lo exigen (ver W-06).
  5. Sin código dedicado para dominio de email (UX `EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL`) — hoy colapsa en `ROSTER_VALIDATION_FAILED` con `field/observed/expected`, lo cual es válido si se declara el mapeo (ver W-12).
- **Cambio mínimo:** ninguno conductual. **Preguntas abiertas Q-I, Q-J, Q-K** (taxonomía por operación, `reason_code` de éxito, 401, emisor de 500, fórmula hash normativa). Triage AR-08/AR-13 ya lo marcó ACCEPT como gap; sigue propuesto.

## 6. Referencias AD-07/08/09 (W-08)

- **Evidencia:** `contracts.md` §5 tabla l.116–132 (12 filas: AD-01,02,03,04,05,06,10,11,12,13; AD-05/AD-13 repetidos). Spine Inherited Invariants l.39–51 lista AD-01..AD-07; Capability Map l.120–128 cita AD-08/AD-09.
- **Impacto (Media, no conductual por sí misma):** tres reglas quedan sin ligado invariante→enforcement→test RED:
  - AD-07 paginación `[1,100]`: solo aparece como nota en `contracts.md` §4 l.114 ("`page_size` fuera de `[1,100]`… se fuerza al rango"). Además `GET /audit` es escenario SC-04, fuera de las tres operaciones — el bound correcto es "respaldo a estados Empty/Error", pero no hay fila ni test.
  - AD-08 pureza hexagonal: sin fila ni test (p. ej. lint de imports `domain/` sin `fastapi`/`sqlalchemy`/`datetime.now`/`random`).
  - AD-09 mapeo canónico: §0 lo fija, pero §5 no lo liga a enforcement (router único) ni test negativo (ninguna otra ruta expone estas operaciones).
- **Cambio mínimo sugerido (editorial, pendiente de confirmación del equipo):** añadir tres filas a la tabla §5 sin cambiar conducta:
  - `Paginación acotada [1,100] | AD-07 | clamp en boundary de consulta de respaldo + cursor (timestamp,id), máx 100 objetos | test: page_size 0/101 se fuerza; nunca >100 en memoria`.
  - `Pureza domain/ | AD-08 | lint de imports + Clock/IdGenerator por puertos | test de build que falla si domain importa framework/reloj/azar`.
  - `Mapeo único operación↔HTTP | AD-09 | routers únicos §0; ninguna otra ruta | test de rutas: solo las tres canónicas exponen las operaciones`.
  No aplico el cambio yo; lo dejo a decisión humana porque fija tests.

## 7. Annex A Mandatory Edge Case

- **Literal exigido (AGENTS/memlog):** "Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently". Relación exigida: `EDGE-01 Multi-Subject Permission Resolution` + PRD.
- **Evidencia de cobertura:**
  - `contracts.md` §1 Q2 ("escalación vigente solo en otro curso no cambia este curso"), I1 bound AD-01+AD-10, §5 fila 1 con `test_edge01_context_isolation`; §2 I1 (`test_revoke_preserves_other_course`); `scenario-3.md` §V doble contexto (`SUBJECT_ENROLLMENT_DROPPED` en CS-480 + ALLOW en CS101).
  - Spine AD-10 l.67–71: seed `Student` en `CS101` + `TA` en `CS-480`, tupla `(identity_id, course_id)`, sin cuota GPU/prioridad por `[ASSUMPTION-01]`, rechazo de la aserción cruda TA=Student (triage EC-02 REJECT).
  - Trazabilidad: `00-ux-scenarios.md` EDGE-01 + PRD §5 (Mateo CS101/CS-480; Sofia NLP/CS-480 como segundo ejemplo).
- **Impacto:** la propiedad está bien ligada y el rechazo de EC-02 es correcto. Queda condicionada a Q-H (si `cs-480` vs `CS-480` canónico) y a Q-A/Q-C (matriz rol×acción exacta sigue abierta en memlog/`open_questions[]`; sin ella el test solo puede asertar independencia, no el ALLOW/DENY concreto por rol).
- **Cambio mínimo:** ninguno. Preguntas Q-A/Q-H cubren lo pendiente.

## 8. Preguntas abiertas (alteran comportamiento; no decidir sin el equipo)

- **Q-A. Precedencia en P5 de resolve:** si falta membresía activa Y el recurso es de otro curso, ¿qué código manda (`SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` vs `RESOURCE_SUBJECT_MISMATCH`)? ¿Y si identidad barred + recurso ajeno? Evidencia: `contracts.md` §1-P5; PRD §5.2 pasos 3–3.1.
- **Q-B. Audiencia de DENY por P1–P5:** ¿qué fallos emiten evento ledger (P5 sí según Q-fail; P1–P4 "no hay mutación" pero no dice evento)? ¿Con qué `decision`/`reason_code`? Evidencia: `contracts.md` §1 Q3/Q-fail; AD-04.
- **Q-C. Borde y lectura de escalación:** confirmar `[granted_at, expires_at)`, `at >= expires_at → DENY STATUS_ESCALATION_EXPIRED`, y qué estados cuentan (`ACTIVE` solo; ¿`PENDING_APPROVAL` cuenta?). Evidencia: `contracts.md` §1-Q1/I2; DDL `escalation_tickets.status`; triage EC-03/AR-07 propuesta.
- **Q-D. Estados fuera de P2 de revoke:** `INACTIVE` ([ASSUMPTION-03]), credencial `EXPIRED`, membresía `COMPLETED` (actor/momento sin definir). ¿`INVALID_TRANSITION` 409 o `MEMBERSHIP_NOT_FOUND` 404 o éxito idempotente? Evidencia: `contracts.md` §2-P2; DDL memberships/credentials; memlog question.
- **Q-E. Entrada del drop:** ¿se transporta el `timestamp` académico del PRD §4.3 o solo `drop_reason`? ¿dónde va `term` del roster (body/path)? ¿`at` viaja por query/body o solo header+payload authorize? Evidencia: `contracts.md` §0 tabla; PRD §4.1–4.3.
- **Q-F. Colisión A y rol divergente:** ¿bandera `STRICT` (aborta) vs segrega cuarentena y sigue? ¿rol divergente rechaza todo el lote o se ignora la fila? Evidencia: `contracts.md` §3-Q2 + anti-smuggling; PRD §4.1 R3–R4 + §7.2 Colisión A/B; AD-02 R3 "rechazado o ignorado".
- **Q-G. Reingesta:** ¿nuevo `batch_id` + revalida (actual `[ASSUMPTION]` §6) o clave idempotencia por contenido (hash lote)? Evidencia: `contracts.md` §3-I3 + §6.
- **Q-H. Canonicalización (W-01):** ¿`strip+upper` en boundary + comparar canónicos, o byte-a-byte estricto contra header como dice AD-01? ¿Función canónica por campo (`courseId`, `institutional_id`, `email`, ARN)? Evidencia: §4 de este reporte.
- **Q-I. Taxonomía ledger por operación:** ¿qué `decision`/`reason_code` portan `roster:ingest` éxito, revoke 200 y `ALREADY_REVOKED` bajo `CHECK(ALLOW,DENY)`? ¿se añade `SUCCESS` o se mapea? ¿rechazo 422 emite evento o cero eventos? Evidencia: §5 de este reporte; adversarial P2/P4.
- **Q-J. Async vs sync y fail-closed:** ¿ledger dentro de la tx o cola `asyncio.Queue` 50 ms/50 ev? ¿bound y desborde de cola? ¿fallo Clock/LedgerWriter → 503 fail-closed o 200 + encola? ¿`busy_timeout`/reintento ante `SQLITE_BUSY` en resolve y roster? Evidencia: AD-04.3 vs AD-12/AD-13; `contracts.md` §1–§3 concurrencia.
- **Q-K. Fórmula hash normativa:** ¿AD-04 l.363–366 (con `subject_id`, `action`) o prosa §2 l.94–96 (sin ellos)? ¿orden/serialización exacta y `schemaVersion`? Evidencia: `planning/ARCHITECTURE.md` §2 vs §5 AD-04; triage AR-13 ACCEPT.
- **Q-L. Caché vs DB (W-04):** ¿se mantiene `revoked_credentials_cache` + `workers:1` + `<200 ms` del padre, o "no existe caché mutable, BD autoridad"? ¿quién mide `<200 ms` vs `<60 s` perimetral? Evidencia: PRD §4.3 R3; ARCHITECTURE §2.1/AD-03; spine AD-12; `contracts.md` §2.
- **Q-M. Scheduler vs perezosa (W-05):** ¿scheduler interno auto-revoca (PRD §4.2 R5) o solo expiración perezosa por `resolve` (spine AD-13)? ¿qué pasa con jobs activos al expirar (`scenario-2.md` §V dice "mantienen prioridad")? Evidencia: PRD §4.2; spine AD-13 + Deferred.
- **Q-N. AuthN 401:** ¿qué credencial exige cada operación, qué fallo da 401 vs 403, y dónde se valida (gateway vs dominio)? Evidencia: PRD §5.2 + §7.1; `EXPERIENCE.md` §2.5; ARCHITECTURE §4.2.
- **Q-O. Gramáticas exactas (W-11):** regex `institutional_id`, `email`, `term`, ARN con ejemplos minúsculos del padre vs canónico UPPER; ¿`at` exige microsegundos y zona siempre? Evidencia: `contracts.md` §0–§3; AD-01.
- **Q-P. `ExplanationDTO` por operación (W-12):** campos obligatorios por `ALLOW`/`DENY`/rechazo lote/baja, mapeo regla UX (`EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL`, E-01–E-04) y campo de acción sugerida. Evidencia: spine AD-11; `contracts.md` Q4s; `EXPERIENCE.md` §3.
- **Q-Q. Transacción roster/revoke (W-13):** ¿validación 100 % en memoria antes de `BEGIN IMMEDIATE`? ¿ledger dentro de la misma tx? ¿predicado single-statement exacto del revoke? Evidencia: `contracts.md` §2-Q2, §3-I1; AD-02/AD-03.
- **Q-R. Matriz rol×acción y resto del memlog:** matriz exacta por curso, actor/momento `COMPLETED`, TTL `uai_live_…`/`EXPIRED`, paginación fuera de las tres ops. Ya abiertas en `contracts.md` §6 + memlog; se reiteran sin duplicar decisión.

## 9. HTTP mapping, transacciones, idempotencia, carreras (resumen)

- **HTTP mapping:** las tres rutas canónicas coinciden con PRD/AD cuando hay autoridad clara (memlog l.16): `POST /api/v1/authorize` + `X-Academic-Subject-Context`, `POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop`, `POST /api/v1/subjects/{subject_id}/roster`. Correcto no exponer `/escalations/*` ni `GET /audit` en estas tres operaciones. Pendiente Q-E (nombres de params, cuerpo, `term`, `at`).
- **Transacciones:** roster `BEGIN IMMEDIATE` + rollback total + `seen_ids` (AD-02) e idempotencia revoke con predicado (AD-03) están bien orientados. Pendiente Q-J/Q-Q (ledger dentro/fuera, `SQLITE_BUSY`, `busy_timeout 5000` del padre).
- **Idempotencia:** revoke replay conformes; roster reingesta como `[ASSUMPTION]` no-idempotente correctamente marcada (Q-G); resolve lectura pura conforme salvo W-04.
- **Carreras:** doble baja → `ALREADY_REVOKED`, roster serializa vs resolve snapshot, resolve post-commit deniega `SUBJECT_ENROLLMENT_DROPPED` — coherentes con triage EC-01/EC-13/EC-16 propuesto. No se cierran por W-04/J.

## 10. Cambios mínimos sugeridos (solo editoriales, a confirmar)

1. Tabla §5: añadir las 3 filas AD-07/AD-08/AD-09 redactadas en §6 (sin cambiar conducta ni tests existentes).
2. §3-P2: anotar "5 MB y columnas según `scenario-1.md`" como fuente del límite.
3. Unificar nombre de clave del instante en receipts de revoke (`revocation_propagated_at` vs `revoked_at`) cuando el equipo elija uno.
4. Nada más. Ningún cambio conductual aplicado en este reporte.

## 11. Trazabilidad de escenarios (conformidad)

| Escenario | Fuente | Cobertura en borrador |
|-----------|--------|-----------------------|
| SC-01 roster 120 + fila 85 `@gmail.com` → 422 + 0 filas | PRD §4.1; `scenario-1.md` | `contracts.md` §3 P3/I1/Q2 + `test_roster_row85_rollback`; spine AD-02/AD-12 |
| SC-02 escalación 4 h + auto-aprobación 403 + reversión | PRD §4.2; `scenario-2.md` | Lectura de ticket + borde + `FORBIDDEN_SELF_APPROVAL`/`CONCURRENT_ESCALATION…`; flujos request/approve fuera de las tres ops (Deferred) |
| SC-03 drop Mateo + `SUBJECT_ENROLLMENT_DROPPED` + CS101 intacta | PRD §4.3; `scenario-3.md` | `contracts.md` §2 + `test_revoke_preserves_other_course`/`test_revoke_all_credentials`; banner E-02 vía AD-11 |
| SC-04 auditoría 30 d + hash + 0 secretos + paginación | PRD §4.4; `scenario-4.md` | AD-04/AD-06/AD-07 heredadas; `GET /audit` fuera de las tres ops; pendiente Q-I/Q-J |
| EDGE-01 multi-materia | PRD §5; `00-ux-scenarios.md` | §7 de este reporte: conforme en propiedad, pendiente Q-A/Q-H |

---

*Fin del reporte. Winston queda a disposición para el triage humano; ninguna pregunta abierta de §8 debe cerrarse con suposición silenciosa.*
