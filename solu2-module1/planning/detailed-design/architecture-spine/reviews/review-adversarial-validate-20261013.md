# Revisión adversarial — Reviewer Gate bmad-architecture (Validate, solo lectura)

- Fecha: 2026-10-13
- Rol: revisor adversarial (intent Validate)
- Alcance: no se edita el spine ni sus companions; no se cierra ningún [OPEN]; no se proponen ediciones, solo se reportan huecos.
- Fuentes leídas (únicas evidencias):
  1. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md`
  2. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/contracts.md`
  3. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md`
- Método: por cada AD se construyen dos unidades un nivel abajo que obedecen la letra del AD y aun así son mutuamente incompatibles (choque de forma de dato compartido, dos dueños de una entidad, o rutas de mutación en conflicto). Cada par = un hueco.

## Veredicto

**NO ROBUSTO (6 pares).**

- 5 pares corresponden a huecos ya documentados como abiertos (correctamente dejados abiertos, sin precedencia).
- 1 par (P-06) es mixto: cubre huecos documentados (transporte `term`, matriz 401, reingesta) + una faceta NUEVA no documentada (case-folding de `userId`/`institutional_id` y de `term`, hermano de [OPEN-01] que en `contracts.md` §0 solo scoping a `courseId`).
- No se cierra ningún OPEN. No se propone ningún cambio al spine.

## Pares incompatibles

### P-01 — [OPEN-01] Normalización vs byte-a-byte crudo

- **AD involucrados:** AD-01 (heredado, Context Isolation & Binding) + AD-09 (spine-local, mapeo operación↔HTTP) + AD-10 (spine-local, EDGE-01).
- **Unidad A (canonicalizadora):** el adapter hace `strip + upper` en el boundary sobre `X-Academic-Subject-Context` y sobre el `subject` extraído del `resource_arn`, y luego compara formas canónicas byte-a-byte. Obedece la Convención del spine (`ARCHITECTURE-SPINE.md` l.96, Alt A) y `contracts.md` §0 l.17 ("comparación sobre formas canónicas byte-a-byte").
- **Unidad B (cruda):** compara el valor crudo del header byte-a-byte sin normalizar contra el `subject` crudo del ARN. Obedece AD-01 read-only citado en `contracts.md` §0 l.17 ("la autoridad read-only AD-01 exige comparar el valor del header crudo byte-a-byte sin normalizar", `planning/ARCHITECTURE.md` l.329–331) y el spine l.45 ("AD-01 crudo byte-a-byte sin cambiar").
- **Incompatibilidad (forma compartida en choque):** mismo request `POST /api/v1/authorize` con header `cs-480` y `resource_arn: urn:uai:subject:CS-480:model:x` → A sigue a matriz rol×acción (potencial ALLOW), B retorna `403 RESOURCE_SUBJECT_MISMATCH`. El regex ARN (`contracts.md` §1 P4) pasa en ambas, pero el veredicto diverge. Dos definiciones de igualdad de `courseId` conviven bajo el mismo AD-01.
- **Clasificación:** YA DOCUMENTADO como [OPEN-01] (spine l.96 + contracts §0 l.17 + §1 P2/P5; auditoría l.11 lo conserva abierto). Correctamente dejado abierto.

### P-02 — [OPEN-02] Caché vs DB-autoridad

- **AD involucrados:** AD-03 (heredado, invalidación determinista + idempotencia) + AD-12 (spine-local, serialización de carreras).
- **Unidad A (caché + workers:1):** implementa `revoked_credentials_cache` en proceso + `workers:1` (alternativa del padre AD-03/§2.1 citada en spine l.83 y contracts §1 "Concurrencia"). `resolve` lee caché; `revoke` escribe DB e invalida post-commit.
- **Unidad B (DB-autoridad sin caché):** "la base de datos es la autoridad y no existe caché mutable entre procesos" (propuesta spine AD-12, l.83). Todo `resolve` va a SQLite WAL writer único.
- **Incompatibilidad (dos dueños de la verdad):** secuencia `revoke` concurrente con `resolve` → A puede retornar ALLOW obsoleto hasta que la invalidación gana la carrera (peor con >1 réplica/proceso), B retorna DENY inmediato post-commit (`SUBJECT_ENROLLMENT_DROPPED`). Ambas obedecen "busy_timeout 5000", "predicado condicional" y "ALREADY_REVOKED sin evento redundante" a la letra; la ventana de staleness y la latencia/CPU divergen de forma incompatible para ATDD de carrera/repetición.
- **Clasificación:** YA DOCUMENTADO como [OPEN-02] (spine AD-12 l.83; contracts §1 Concurrencia; auditoría l.11). Correctamente dejado abierto.

### P-03 — [OPEN-03] Scheduler vs expiración perezosa (+ transporte `at`)

- **AD involucrados:** AD-05 (heredado, contexto de tickets/exclusión mutua) + AD-13 (spine-local, frontera temporal) + AD-08 (pureza/Clock).
- **Unidad A (perezosa):** ningún mutador por tiempo; el ticket permanece `ACTIVE` en DB tras `expires_at`; cada `resolve` evalúa `[granted_at, expires_at)` y `at >= expires_at → DENY STATUS_ESCALATION_EXPIRED`. `at` ausente → `clock.now()` en el adapter (spine l.89, contracts §1 Tiempo).
- **Unidad B (scheduler):** worker interno (PRD §4.2 R5, citada como alternativa abierta en spine l.89 y contracts §1 Tiempo) muta `ACTIVE → EXPIRED/REVOKED` por su cuenta.
- **Incompatibilidad (ruta de mutación en conflicto + forma de transporte en choque):**
  - Estado observable diverge: el mismo ticket post-expiración se lee `ACTIVE` (A) vs `EXPIRED` (B); el ledger emite o no evento de expiración; un `revoke`/doble-ticket concurrente toma ramas distintas.
  - Transporte `at`: AD-09 fija `POST /api/v1/authorize` pero no fija dónde viaja `at` (contracts §0 l.13: "`at` opcional ISO-8601" sin ubicación). A lo lee del body JSON `{"at":...}`, B de query `?at=...`. Ambas obedecen AD-09 y "sustitución por `clock.now()` en adapter"; el mismo cliente ATDD obtiene `INVALID_AT 400` en una y veredicto en la otra.
- **Clasificación:** YA DOCUMENTADO como [OPEN-03] + transporte `at` como cuestión abierta (spine AD-13 l.89; contracts §1 Tiempo; auditoría l.11 "OPEN-03 scheduler vs lazy" y "OPEN-06/07/09/10 transporte at/term"). Correctamente dejado abierto.

### P-04 — [OPEN-04] Ledger/hash en rechazo + ExplanationDTO / reason_code

- **AD involucrados:** AD-04 (heredado, ledger encadenado + metadata singleton) + AD-11 (spine-local, decisión explicable con regla citada).
- **Unidad A (solo-política):** emite evento ledger + hash solo para decisiones de política P5 (403) y mutaciones comprometidas; P1–P4 (400/404: `UNKNOWN_IDENTITY`, `INVALID_AT`, `MALFORMED_RESOURCE_ARN`) no tocan el ledger. Lee `contracts.md` §1 Q-fail ("si falla P1–P4 no hay mutación") entendiendo evento = mutación.
- **Unidad B (todo-rechazo):** emite evento encadenado con `reason_code` para todo rechazo P1–P5. Lee §1 Q3 ("emite un evento de auditoría con eventId, occurredAt, decision, reason_code y hash encadenado según AD-04") donde "decisión" incluye 400/404.
- **Incompatibilidad (dos dueños del ledger + enum en choque):**
  - Cadena hash y orden `id ASC` (spine l.48, contracts §5) divergen: A deja huecos, B es continua; la verificación y `AUDIT_LOG_TAMPERING_DETECTED` (catálogo l.115) dan resultados opuestos sobre la misma traza; el conteo del metadata singleton diverge.
  - `ExplanationDTO`/`reason_code`: AD-11 exige "`reason_code` del enum cerrado del catálogo" y "`rule_ids` no vacío" (spine l.77). El catálogo (l.90–116) no define código para ALLOW/SUCCESS ni para `ALREADY_REVOKED`. A inventa/omite código de éxito de forma distinta que B (p. ej. `null` vs código fuera de catálogo vs reutilizar un 403), y el набор `observed_*`/umbral ("cuando aplica") se llena de forma incompatible aunque ambas citan un AD-n. Los banners E-01–E-04 parsean formas distintas.
- **Clasificación:** YA DOCUMENTADO como abierta (auditoría l.11: "OPEN-04 hash/reason_code/ledger en rechazo y DENY P1–P4" + "Contradicción Q-fail vs Q3" + "vaguedades (comprometido, cuando aplica, … SUCCESS vs catálogo) siguen abiertas"; contracts Q3 vs Q-fail). Correctamente dejado abierto; no se cierra aquí.

### P-05 — [OPEN-05] Predicado single-statement vs BEGIN IMMEDIATE (+ cola async)

- **AD involucrados:** AD-02 (heredado, ingestión atómica) + AD-03 (heredado, revocación) + AD-12 (spine-local, "predicado condicional en una sola sentencia o BEGIN IMMEDIATE").
- **Unidad A (single-statement):** `revoke` = un `UPDATE … WHERE identity AND subject AND status='ACTIVE'` en autocommit; `rowcount==0 → ALREADY_REVOKED`. Sin `BEGIN` explícito.
- **Unidad B (BEGIN IMMEDIATE):** `revoke`/`ingest` = `BEGIN IMMEDIATE; SELECT; UPDATE/INSERT; COMMIT` (contracts §2 Q2 + §3 I1/Concurrencia, spine AD-12 l.83).
- **Incompatibilidad (rutas de serialización en conflicto):** ambas obedecen "queda prohibido leer y luego actualizar en dos pasos" (B alega que bajo lock exclusivo no es el patrón prohibido). Bajo contención: A agota `SQLITE_BUSY` y retorna `503 AUTH_INTERNAL_POLICY_UNAVAILABLE` fail-closed inmediato; B bloquea hasta `busy_timeout 5000` y commitea. Un `resolve` durante `ingest` ve snapshot previo (B, "nunca medio lote") vs exposición/503 (A). El bound y desborde de la cola asíncrona de auditoría (contracts §6, auditoría OPEN-05) se comporta distinto (pérdida vs duplicación vs bloqueo) sin violar ninguna letra.
- **Clasificación:** YA DOCUMENTADO como [OPEN-05] (auditoría l.11: "OPEN-05 bound de cola async y predicado single-statement"; contracts §2 Q2/Concurrencia + §3 Concurrencia + §6). Correctamente dejado abierto.

### P-06 — Transporte `term` + matriz AuthN 401 + reingesta (+ faceta NUEVA: case de `userId`/`term`)

- **AD involucrados:** AD-09 (spine-local, mapeo HTTP) + AD-02 (heredado, anti-role-smuggling/atomicidad) + AD-10/AD-11 (aislamiento, explicabilidad) + contracts §0/§3/§6.
- **Unidad A (estricta):** `term` en query `?term=2026-FALL`; header `X-Academic-Subject-Context` ausente → `403 SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (catálogo, sin 401); reingesta del mismo CSV → revalidación completa con `batch_id` nuevo `roster-<8hex>-<term>` y nuevos eventos (contracts §3 Q1 + §6: "sin clave de idempotencia por contenido"); `institutional_id`/`term` case-sensitive exactos.
- **Unidad B (normalizadora/idempotente):** `term` como campo del body/CSV; header ausente → `401` infra-AuthN; reingesta del mismo contenido → idempotente sin mutación ni eventos (mismo hash de contenido); `institutional_id` con `strip + upper`, `term` con `upper` (`2026-fall → 2026-FALL`).
- **Obediencia literal:** AD-09 solo fija método+ruta por operación (spine l.65), no la ubicación de `term` ni el 401 (el catálogo l.90–117 no contiene ningún 401); AD-02 fija `seen_ids` intra-lote y "todo o nada" pero §6 declara "la reingesta no es invariante… comportamiento sin decidir hasta acuerdo" (contracts l.83 + §6 l.146); por tanto ambas conductas obedecen la letra.
- **Incompatibilidad (tres choques en una frontera):**
  - Mismo re-`POST /subjects/{id}/roster` con CSV idéntico → A `201` nuevo `batch_id` + N credenciales/eventos, B idempotente sin escrituras. Manifiesto `roster_rejected_conflicts.csv` y conteos `processed/created/updated` divergen.
  - Mismo `POST /authorize` sin header → A `403`, B `401`; la matriz rol×acción por curso (abierta en §6/memlog) se evalúa o no según la rama.
  - Misma grafía `stu-98432` / `2026-fall` → A `UNKNOWN_IDENTITY`/`MALFORMED_TERM`, B éxito tras fold. Dos dueños de la identidad canónica (adapter-resolve vs domain-roster) construyen BD incompatibles a partir del mismo lote.
- **Clasificación:** MIXTA.
  - DOCUMENTADAS (correctamente abiertas): reingesta como [ASSUMPTION]/[OPEN] (contracts §3 l.83 + §6 l.146); transporte `term` y 401 y matriz rol×acción como cuestiones abiertas (auditoría l.11 "OPEN-06/07/09/10 transporte at/term, 401, … matriz rol×acción" + contracts §6 "matriz… actor… TTL… cola… NFR").
  - NUEVA (no documentada en ninguna de las tres fuentes): el case-folding de `userId`/`institutional_id` y de `term`. [OPEN-01] está scopeado explícitamente a `courseId` en `contracts.md` §0 l.17 ("`courseId` se canonicalizaría…"), y el spine l.96 no bindea `userId`/`term`; ninguna entrada de §6 ni de la auditoría l.11 nombra `institutional_id` case ni `term` minúsculo. Es hermano de [OPEN-01] pero distinto y sin tag.

## Cobertura de los focos exigidos

| Foco | Par que lo demuestra | Estado |
| --- | --- | --- |
| [OPEN-01] normalización vs byte-a-byte | P-01 | DOC [OPEN-01] |
| [OPEN-02] caché vs DB-autoridad | P-02 | DOC [OPEN-02] |
| [OPEN-03] scheduler vs lazy | P-03 | DOC [OPEN-03] |
| [OPEN-04] hash/ledger en rechazo | P-04 | DOC (auditoría OPEN-04 + Q-fail/Q3) |
| [OPEN-05] single-statement vs BEGIN IMMEDIATE | P-05 | DOC [OPEN-05] |
| transporte `at` | P-03 | DOC (auditoría transporte) |
| transporte `term` | P-06 | DOC (auditoría transporte) |
| matriz AuthN 401 | P-06 | DOC (auditoría 401 + memlog matriz) |
| ExplanationDTO / reason_code | P-04 | DOC (auditoría SUCCESS vs catálogo) |
| reingesta como ASSUMPTION/OPEN | P-06 | DOC (contracts §6) |
| case `userId`/`term` (hermano de OPEN-01) | P-06 faceta | NUEVO |

## Distinción documentado vs nuevo

- **Ya documentados como abiertos (5 + facetas de P-06):** P-01, P-02, P-03, P-04, P-05, y en P-06 las facetas reingesta / ubicación `term` / 401 / matriz. Todos constan en spine `[OPEN-01/02/03/05]`, contracts §6, o auditoría l.11 (`OPEN-04/05/06/07/09/10`, `Q-fail vs Q3`, `SUCCESS vs catálogo`). Están correctamente dejados abiertos; este reporte no los cierra.
- **Nuevo no documentado (1 faceta dentro de P-06):** normalización `strip + upper` (o no) de `userId`/`institutional_id` y de `term` (`stu-98432` vs `STU-98432`, `2026-fall` vs `2026-FALL`). No hay tag [OPEN] ni cuestión en §6/memlog que lo nombre en las tres fuentes leídas.
- **Escala:** ROBUSTO = 0 pares; este spine = **NO ROBUSTO (6 pares)**. El grueso ya estaba triageado como abierto; queda 1 faceta nueva por triagear (sin propuesta de cierre aquí).

## Notas de no-cierre

- Ningún [OPEN-01/02/03/04/05], ni la reingesta [ASSUMPTION]/[OPEN], ni las cuestiones de transporte/401/matriz/TTL/COMPLETED/NFR se cierran en este reporte.
- No se propone ninguna edición al spine, a `contracts.md`, ni a schemas/ports. Solo se reportan los pares y su evidencia.
- Veredicto de la auditoría Winston (`resultados-interaccion.md` l.12: "NO PASS", `ok:false`, spine draft/parcial, no pasar a Fase 3) queda intacto y es consistente con este hallazgo.
