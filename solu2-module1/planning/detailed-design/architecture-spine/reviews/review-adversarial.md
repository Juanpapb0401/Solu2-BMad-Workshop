# Review adversarial — Reviewer Gate bmad-architecture (update 2026-10-12)

- Alcance SOLO lectura: `architecture-spine/ARCHITECTURE-SPINE.md` + companions `contracts.md` + `ports-and-adapters.md`.
- Método: por cada AD se construyen dos unidades un nivel abajo que obedecen el AD al pie de la letra pero resultan mutuamente incompatibles (shapes compartidos, doble dueño de entidad, paths de mutación en conflicto). Cada par es un hueco que exige AD nuevo o más estricto. No se propone código productivo.
- Fecha: 2026-10-12.

## Veredicto

**NO ROBUSTO — 5 pares incompatibles. No cierra el Reviewer Gate.**

| Par | Eje | AD obedecidos por ambas unidades | Incompatibilidad |
|-----|-----|----------------------------------|------------------|
| P1 | DENY 200 vs 403 | AD-09, AD-11 | mismo `DENY` de dominio → U-A `200 + {decision:DENY}` vs U-B `403 DenyBody RFC-7807` |
| P2 | Canonicalización [OPEN-01] | AD-01 (read-only), AD-08, convención Data & formats | U-A compara crudos byte-a-byte vs U-B `strip+upper` + compara canónicos |
| P3 | Caché vs DB [OPEN-02] | AD-03, AD-12 | U-A `revoked_credentials_cache` + `workers:1` vs U-B BD autoridad sin caché |
| P4 | Scheduler vs lazy [OPEN-03] | AD-05, AD-13 | U-A solo evaluación perezosa vs U-B scheduler que muta escalaciones |
| P5 | Ledger / envelope atómico | AD-04, AD-12, ports-and-adapters §4 | U-A `audit_ledger` solo vs U-B `audit_ledger + audit_events` con doble `Clock.now()`; desacuerdo ledger-en-rechazo |

## P1 — DENY 200 vs 403 (AD-09 + AD-11)

- **U-A «200-siempre»:** lee AD-09 «el dominio distingue `ALLOW|DENY`» + `contracts.md §1-Q1` («el dominio retorna `{decision: ALLOW|DENY, …}`») y decide que HTTP siempre es `200` con `decision` en el body (`200 {decision: DENY, explanation}`). Cita a su favor que AD-11 exige `ExplanationDTO` en todo veredicto y que UX E-01–E-04 necesita body explicable sin entrar en rama de error. Afirma obedecer AD-09 porque «ninguna otra ruta expone estas operaciones» se cumple.
- **U-B «403-normativo»:** lee la segunda mitad del mismo AD-09 («todo `DENY` de política → `403 DenyBody` RFC-7807 con `decision: DENY` + `ExplanationDTO` obligatoria») + `contracts.md §0` y mapea `ALLOW → 200 AuthorizeResponse`, `DENY → 403`. Afirma obedecer el mismo AD al pie de la letra.
- **Incompatibilidad observable:** mismo input (Student CS101 pide recurso de CS-480) → U-A `200 DENY`, U-B `403 DENY`. Clientes, tests de ruta (`ports-and-adapters.md §1` «solo `POST /api/v1/authorize` expone resolve») y gateways (OPEN-07: 401 vs 403) divergen; un test negativo de rutas pasa en una y falla en la otra. Shape compartido `AuthorizeResponse vs DenyBody` con dos dueños (dominio dice `decision`, HTTP dice `status`).
- **Hueco:** AD-09 no contiene la frase prohibitiva «queda prohibido `200` con `decision: DENY`» ni fija el envelope RFC-7807 campo por campo (`type/title/status/detail/code/decision/explanation`). Tampoco resuelve qué DENY es «de política» (403) vs error tipado 4xx/5xx del catálogo.
- **Cierre exigido:** AD-09bis: tabla decisión→status exhaustiva (incl. `IDENTITY_BARRED`, `STATUS_ESCALATION_EXPIRED`, `RESOURCE_SUBJECT_MISMATCH` → 403; `UNKNOWN_*` → 404; `INVALID_AT` → 400), prohibición explícita de `200+Deny`, shape `DenyBody` cerrado y test negativo de status. Sin esto, P1 sigue abierto.

## P2 — Canonicalización [OPEN-01] (AD-01 read-only vs convención + contracts §0)

- **U-A «cruda»:** obedece `planning/ARCHITECTURE.md` AD-01 read-only (citado en spine l.96 y `contracts.md §0` l.15: «exige comparar el valor del header crudo byte-a-byte sin normalizar») + regex ARN `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$`. Compara `X-Academic-Subject-Context: cs-480` crudo contra `resource.subject = CS-480` → mismatch → `403 RESOURCE_SUBJECT_MISMATCH`. Almacena `subject_id` tal como llega.
- **U-B «canónica»:** obedece la convención del spine («`strip + upper` en el boundary antes de comparar… la comparación recurso↔contexto correrá sobre formas canónicas byte-a-byte») + `contracts.md P2` («`courseId` canonicalizable a un `subjects.id` activo»). Normaliza `cs-480 → CS-480` en el adapter y luego compara byte-a-byte → `ALLOW` (si el rol autoriza). Almacena siempre UPPER.
- **Incompatibilidad observable:** mismo request → U-A 403, U-B 200/403 según rol. Peor: filas escritas por U-B (`CS-480`) vs leídas por U-A (`cs-480`) rompen joins, unicidades (`UNIQUE(identity_id, subject_id)` en `ports-and-adapters.md §5`) y el `CHECK GLOB` de `audit_ledger.resource_arn`. La misma fractura existe en `userId/institutional_id/email` sin función canónica definida. Los ARN de ejemplo en minúsculas (PRD/ARCH) autorizan en U-A y fallan en U-B o viceversa.
- **Doble dueño:** el «dueño» del `subject_id` canónico es a la vez el adapter HTTP (boundary), `domain/resolution` (comparación) y el DDL (CHECK) — tres definiciones de igualdad.
- **Hueco:** el spine documenta el conflicto sin resolverlo («requiere triage humano») y la convención propone sin normar. Falta función canónica exacta por campo (`subject_id`, `institutional_id`, `email`, ARN), punto único de aplicación (boundary adapter, nunca dominio — AD-08) y regla para valores ya persistidos.
- **Cierre exigido:** AD-14 canonicalización: `canon_subject(s)=strip+upper`, `canon_email=strip+lower`, `institutional_id=strip` (case-sensitive), ARN gramática + normalización del segmento subject; comparación siempre sobre formas canónicas; almacenamiento siempre canónico; ejemplos minúsculos declarados «variantes de presentación». Test: `cs-480`, ` CS-480 `, `Cs-480` → mismo veredicto.

## P3 — Caché vs DB [OPEN-02] (AD-03 + AD-12)

- **U-A «caché»:** obedece la alternativa del padre citada como vigente en AD-12 («alternativa del padre AD-03/§2.1 con `revoked_credentials_cache` + `workers:1` sigue abierta») + `contracts.md §1-Concurrencia` («la alternativa del padre sigue abierta»). Implementa `dict {(identity,course) → revoked_bool}` en el adapter + `workers:1`; `resolve` lee caché primero → p95 < 20 ms, inmune a `SQLITE_BUSY`.
- **U-B «DB-autoridad»:** obedece la propuesta del spine en el mismo AD-12 («la base de datos es la autoridad y no existe caché mutable entre procesos») + «queda prohibido el patrón leer y luego actualizar en dos pasos». Cada `resolve` va a SQLite; ante `revoke` concurrente con `BEGIN IMMEDIATE` responde snapshot previo o `503 AUTH_INTERNAL_POLICY_UNAVAILABLE` fail-closed ante `SQLITE_BUSY` agotado (`contracts.md §3-Concurrencia`).
- **Incompatibilidad observable:** secuencia `revoke(T) || resolve(T+ε)`: U-A puede devolver `ALLOW` obsoleto (caché sin invalidar) o `DENY` instantáneo según orden de invalidación; U-B devuelve `DENY` o `503`. NFR-REVOC-03 («invalidación local < 200 ms; corte perimetral < 60 s») se mide distinto en cada una. Dos unidades «conformes» no pasan el mismo test de carrera/replay (`test_revoke_all_credentials`, `test_revoke_replay_idempotent`).
- **Path de mutación en conflicto:** predicado condicional single-statement vs `BEGIN IMMEDIATE` ([OPEN-05] deja ambos abiertos); sin dueño único del orden invalidación→commit→lectura.
- **Hueco:** AD-12 mantiene ambas alternativas abiertas en la misma regla. No fija: ¿existe caché?, ¿quién la invalida y en qué orden respecto al commit?, ¿qué hace `resolve` ante `SQLITE_BUSY` (esperar `busy_timeout 5000` vs 503 inmediato)?, ¿`workers:1` es normativo?
- **Cierre exigido:** AD-12bis: una sola autoridad (recomendado: BD, sin caché mutable entre procesos, coherente con SQLite WAL writer único del stack); orden normativo `predicado-commit → lectura post-commit`; política `SQLITE_BUSY` (esperar `busy_timeout` y luego fail-closed 503); `workers:1` normativo o eliminado. Test de carrera con resultado único.

## P4 — Scheduler vs lazy [OPEN-03] (AD-05 + AD-13)

- **U-A «lazy»:** obedece AD-13 («la expiración se evalúa de forma perezosa en cada `resolve` y no hay scheduler que mute roles») + intervalo `[granted_at, expires_at)`, `at >= expires_at → DENY STATUS_ESCALATION_EXPIRED`. Nunca escribe en la tabla de escalaciones por paso del tiempo. El ticket expirado sigue `status=ACTIVE` en BD.
- **U-B «scheduler»:** obedece la alternativa citada como vigente en el mismo AD-13 («alternativa PRD §4.2 R5 con scheduler interno sigue abierta») + `ports-and-adapters.md RegistrarSource` / `scenario-2.md §V` («mantienen prioridad»). Un job flips `ACTIVE → EXPIRED` y/o revoca credenciales al expirar.
- **Incompatibilidad observable (doble dueño de `escalation.status`):** tras expirar, U-A conserva fila `ACTIVE` (el índice parcial `idx_single_active_escalation` de `ports-and-adapters.md §5` sigue contándola) → segunda solicitud de escalación → `409 CONCURRENT_ESCALATION_NOT_PERMITTED` permanente (fuga). U-B libera el índice → segunda solicitud → `201/nueva ticket`. Mismo historial, estados opuestos. Además U-B introduce un escritor fuera de las tres operaciones (job) que viola la lectura estricta de AD-08/AD-13 («el dominio recibe el instante por `Clock`», sin mutación temporal autónoma) mientras U-A viola la expectativa PRD R5.
- **Hueco:** AD-13 autoriza y prohíbe el scheduler en la misma regla; AD-05 pone el guarda físico (índice parcial) sin definir qué transiciona el estado ni cuándo. Sin dueño del ciclo de vida `PENDING/ACTIVE/EXPIRED`, sin momento de transición, sin regla para jobs activos al expirar.
- **Cierre exigido:** AD-13bis: un solo modelo (recomendado: lazy + transición de estado en el próximo `resolve`/escritura comprometida, sin job autónomo; o scheduler con dueño, intervalo y predicado normativos — pero solo uno); redefinir el índice parcial sobre estados terminales; regla para jobs activos al expirar. Test de borde + test de doble-solicitud post-expiración con resultado único.

## P5 — Ledger / envelope atómico (AD-04 + ports-and-adapters §4 + AD-12)

- **U-A «ledger-solo»:** lee `contracts.md §1-Q3` («emite un evento de auditoría… según AD-04») + `§2-Q3` («emite exactamente un evento de baja; la repetición no emite») + `§3-Q-fail` («ante rechazo… no se emite credencial alguna» — extendido a «cero eventos») y escribe solo `audit_ledger` en DENY/422, omitiendo `audit_events`. En éxito escribe ambas pero con dos llamadas `Clock.now()` (una por tabla) cumpliendo literalmente «ambos del puerto `Clock`».
- **U-B «envelope»:** lee `ports-and-adapters.md §4` («TABLA `audit_events` ligada 1:1… escritura atómica misma transacción… `occurred_at` byte-a-byte igual a `audit_ledger.timestamp`») y escribe ambas filas en una tx, pero interpreta [OPEN-04/05] («orden validación→tx→ledger, fórmula hash, bound de cola») como libertad para ordenar `validar → emitir evento → mutar` o usar `asyncio.Queue 50 ms/50 ev` (AD-04.3 del padre).
- **Incompatibilidades observables:**
  1. `occurred_at != timestamp` por microsegundos (doble `now()`) → viola la regla byte-a-byte que U-A ni siquiera intenta cumplir; verificador por `id ASC` ve dos relojes.
  2. Rechazos 422/`DENY` presentes en `audit_ledger` pero ausentes en `audit_events` (o viceversa) → exportación/traza por envelope pierde intentos denegados que el ledger sí tiene; `AUDIT_LOG_TAMPERING_DETECTED` dispara en una y no en la otra.
  3. DDL `audit_ledger.decision CHECK(ALLOW,DENY)` no admite `roster:ingested`/`membership.revoked` (`event_type` del envelope) — shape compartido con dos alfabetos.
  4. Orden: `ledger-antes-del-commit` (evento huérfano si la mutación revierte) vs `ledger-en-la-misma-tx` (atómico) vs `ledger-async-encolado` (éxito 200 + evento perdido al desbordar) — tres semánticas de «emite» bajo el mismo AD-04.
- **Hueco:** AD-04 + §4 fijan el «qué» (1:1, misma tx) pero dejan abiertos fórmula hash, `reason_code` de éxito (catálogo sin `SUCCESS`), ledger-en-rechazo, emisor de `AUDIT_LOG_TAMPERING_DETECTED`, orden validación→tx→ledger y bound/desborde de cola ([OPEN-04/05]). `LedgerWriter.append(event)` tiene tres dueños (dominio, adapter sqlite, cola async).
- **Cierre exigido:** AD-04bis: un solo `Clock.now()` por evento (mismo valor en ambas tablas); orden normativo `validar → BEGIN IMMEDIATE → mutar + ledger/envelope → COMMIT` (ledger nunca antes del commit, nunca async fuera de tx salvo bound normado con política de desborde fail-closed); taxonomía evento/`reason_code` por operación incl. éxito y rechazo (¿422 emite `roster.rejected` o cero eventos? — una sola respuesta); `decision` NULL-able o separado de `event_type`; test de envelope atómico + test de rollback-con-ledger + test de rechazo con expectativa única.

## Qué falta para ROBUSTO (resumen de cierres)

1. AD-09bis (DENY→status + prohibición 200+Deny + `DenyBody` cerrado).
2. AD-14 (canonicalización por campo + punto único boundary).
3. AD-12bis (autoridad única caché/DB + orden + `SQLITE_BUSY` + `workers`).
4. AD-13bis (dueño único del ciclo de escalación; scheduler o lazy, no ambos).
5. AD-04bis (timestamp único, orden tx, taxonomía éxito/rechazo, hash y cola normados).
6. Resolver [OPEN-01..05] antes de `bmad-build`; hasta entonces ningún par es construible sin divergencia.

## Trazabilidad

- Spine: `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (AD-08..AD-13, convenciones, stack).
- `solu2-module1/planning/detailed-design/contracts.md` §§0–6 (P/Q/I, catálogo, ASSUMPTION, OPEN).
- `solu2-module1/planning/detailed-design/ports-and-adapters.md` §§1–7 (mapa hexagonal, §4 envelope 1:1, §5 cross-check, §6 open_questions).
- Ejes pedidos: DENY 200 vs 403 (AD-09), canonicalización [OPEN-01] (AD-01), caché vs DB [OPEN-02] (AD-03/AD-12), scheduler vs lazy [OPEN-03] (AD-05/AD-13), ledger/envelope atómico (AD-04/§4).
