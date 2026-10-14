# Revisión adversarial — Reviewer Gate bmad-architecture (2026-10-13, vuelta 3)

- Fecha: 2026-10-13
- Rol: revisor adversarial, solo lectura salvo este archivo de reporte. No se edita ningún otro archivo, no se cambia el criterio, no se oculta ningún hallazgo, no se propone ninguna edición, no se cierra ningún OPEN.
- Alcance: `solu2-module1` — `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)` + `EDGE-01 Multi-Subject Permission Resolution` + Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»).
- Fuentes leídas (solo lectura):
  1. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (136 líneas, `updated: 2026-10-13`).
  2. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/contracts.md` (157 líneas).
  3. Ruta pedida `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/resultados-interaccion.md` — no existe en esa ruta; se leyó el archivo existente `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md` (13 líneas). Se deja constancia sin alterar el criterio.
- Versión evaluada: decisiones N-01..N-16 `[ADOPTED]` plasmadas en spine/contracts (codec hash determinista UTF-8/orden §5/prev hex/nulos explícitos/FIFO-`id ASC`; `at` estricto solo-ausencia-usa-`Clock.now()`; `term` exclusivo por canal con rechazo sin elegir valor; `roster.rejected` en cadena única tras aceptación; cola con reserva previa y 503; reingesta serializada no-idempotente con `BEGIN IMMEDIATE`; scheduler dueño único con relojes separados; auth 401-primero; UUID exacto con rechazo de whitespace; límites exactos 5.000.000 bytes/1000 filas/`drop_reason` Unicode; replay antes de P3; `ExplanationDTO` vs `ErrorBody`; `BEGIN IMMEDIATE` + `busy_timeout 5000`).
- Pendientes declarados asumidos sin cerrar (no son huecos nuevos si el par los describe exactamente): matriz rol×acción (`roles_matrix.json` inexistente); capacidad máxima de cola; recuperación post-aceptación; frecuencia numérica del scheduler; ubicación HTTP del `timestamp` de baja; `COMPLETED`; TTL `uai_live_…`; datasets/concurrencia NFR (p95/p99, 1000 filas, 120 filas, revocación); reemisión/regeneración de credenciales en reingesta; case-folding de UUID; colisión `batch_id` 8hex.

## Método

Adversario un nivel abajo: por cada AD se construyen dos unidades hipotéticas que obedecen el texto vigente del AD al pie de la letra (incluidas las decisiones N-01..N-16) y aun así divergen en HTTP observable, estado persistido o ledger. Cada divergencia es un par = un hueco.

- `CUBIERTO`: el par ataca exactamente el punto ya contenido por una decisión N-01..N-16 o describe exactamente un pendiente declarado. No computa como hueco nuevo; se lista para distinguir.
- `NUEVO` (serie `H-01..H-13`): ambas unidades obedecen las decisiones cerradas y los pendientes vigentes y aun así divergen en un matiz no documentado en spine/contracts. Es hueco.
- Escala: `ROBUSTO` = 0 pares `NUEVO`; `NO ROBUSTO` = N pares `NUEVO` (N>0).

## Veredicto

**NO ROBUSTO (13 pares NUEVOS).**

## Resumen

| ID | Foco | AD involucrados | Estado |
| --- | --- | --- | --- |
| D-01 | Lista hash §5 vs resumen §2 | AD-04 (heredado) | CUBIERTO por decisión |
| D-02 | Transporte `at` body / `term` query+body | AD-09, AD-13 (spine-local) | CUBIERTO por decisión (forma básica) |
| D-03 | Roster 422 rollback + `roster.rejected` posterior misma cadena, 422 tras aceptación | AD-02, AD-04 (heredados) | CUBIERTO por decisión (forma básica) |
| D-04 | Cola llena → 503, reserva previa, respuesta puede preceder persistencia | AD-04 (heredado), AD-12 (spine-local) | CUBIERTO por decisión (forma básica) |
| D-05 | Reingesta sin idempotencia, `batch_id` nuevo, serializada | AD-02 (heredado), AD-12 | CUBIERTO por decisión (forma básica) |
| D-06 | Scheduler dueño + guarda `now>=expires_at`, relojes separados | AD-13, AD-05 (heredado) | CUBIERTO por decisión (forma básica) |
| D-07 | Post-revocación 403 unificado + 401-primero (caso puro) | AD-09, AD-03 (heredado) | CUBIERTO por decisión (caso puro) |
| D-08 | UUID exacto, whitespace rechazado, `institutional_id`/`term`/`seen_ids` case-sensitive, email-dominio insensitive | AD-09 §0 | CUBIERTO por decisión (caso puro) |
| D-09 | Límites 5.000.000 bytes / 1000 filas / `drop_reason` 1–280 + replay-antes-de-P3 + DTO-vs-ErrorBody + `BEGIN IMMEDIATE`/`busy_timeout`/FIFO | AD-02, AD-03, AD-11, AD-12 | CUBIERTO por decisión (forma básica) |
| D-10 | Header solo `/authorize`, path canónico en revoke/ingest | AD-01 (heredado), AD-09 | CUBIERTO por decisión (caso puro) |
| O-01 | Matriz rol×acción ausente | AD-11, AD-01 | CUBIERTO por OPEN |
| O-02 | Capacidad máxima cola + recuperación post-aceptación | AD-04 | CUBIERTO por OPEN (TEA/NFR) |
| O-03 | Frecuencia numérica scheduler | AD-13 | CUBIERTO por OPEN (TEA/NFR) |
| O-04 | Ubicación HTTP `timestamp` baja | AD-03 | CUBIERTO por OPEN |
| O-05 | `COMPLETED`, TTL `uai_live`, reemisión credenciales, case UUID, colisión `batch_id`, datasets NFR | AD-03, AD-02, AD-09 §0, NFR | CUBIERTO por OPENs |
| H-01 | Codec: literal de nulo + representación de zona | AD-04 (heredado) | NUEVO |
| H-02 | `at` futuro + precisión >6 decimales | AD-09, AD-13 | NUEVO |
| H-03 | `term`: elección `MALFORMED_TERM` vs `MALFORMED_BATCH` + `term` no-string en JSON | AD-09 | NUEVO |
| H-04 | Manifiesto: granularidad por-campo vs por-fila + conteos en 422 + `batch_id` en rechazo | AD-02, AD-04, AD-11 | NUEVO |
| H-05 | Evento/cola para fallos P1–P4 (400/404 bajo cola llena) | AD-04, AD-12, AD-11 | NUEVO |
| H-06 | Reingesta: cubeta created-vs-updated + precedencia de CODEs + `batch_id` tras 503 | AD-02, AD-12 | NUEVO |
| H-07 | Scheduler: crash tras mutar + ticket con `granted_at` futuro + revoke-vs-expiry | AD-13, AD-05, AD-04 | NUEVO |
| H-08 | Precedencia auth fuera de authorize + token ausente | AD-09, PRD §5.2 | NUEVO |
| H-09 | UUID: variantes con llaves/URN/sin-guiones/mayúsculas + charset `institutional_id` 404-vs-400 | AD-09 §0, AD-08 | NUEVO |
| H-10 | Conteo de bytes/filas + `drop_reason` solo-espacios/grafemas | AD-02, AD-03, catálogo | NUEVO |
| H-11 | `ALREADY_REVOKED` con/sin `explanation` + envelope 409/422/413/503 | AD-03, AD-11, AD-12 | NUEVO |
| H-12 | Lector bajo contienda + cardinalidad `Clock.now()` (single vs multi) | AD-03, AD-12, AD-04.3, AD-08, AD-13 | NUEVO |
| H-13 | Triple fuente de curso + precedencia `UNKNOWN_COURSE` vs `MISMATCH` vs `CONTEXT_MISSING` | AD-01, AD-09 | NUEVO |

## A. Pares CUBIERTOS por decisiones/pendientes (no son huecos nuevos)

### D-01 — Lista hash §5. AD: AD-04. CUBIERTO.
Unidad A usaba resumen ARCH §2 sin `subject_id`/`action`; Unidad B usa lista §5 `SHA256(prev || timestamp || actor_id || subject_id || resource_arn || action || decision || reason_code)`. Contención: contracts §1-Q3 + spine AD-04 declaran §5 normativa y §2 resumen incompleto. Se registra para distinguir de H-01 (serialización dentro de la lista ya cerrada).

### D-02 — Transporte `at`/`term`. AD: AD-09, AD-13. CUBIERTO (forma básica).
Unidad A ponía `at` en query y `term` mezclado; Unidad B pone `at` en body JSON opcional (solo ausencia → `Clock.now()` en adapter) y `term` en query para CSV / body para JSON. Contención: spine AD-09 + contracts §0. Se registra para distinguir de H-02/H-03 (bordes no fijados).

### D-03 — Rechazo roster con evento posterior misma cadena. AD: AD-02, AD-04. CUBIERTO (forma básica).
Unidad A no emitía nada o emitía en segunda cadena; Unidad B revierte todo y después registra `roster.rejected` en la misma cadena única `audit_ledger` (1:1 `audit_events`, afecta siguiente `prev`), 422 tras aceptación sin esperar persistencia, no-aceptado → 503. Contención: spine conventions + contracts §3-Q3. Se registra para distinguir de H-04/H-05 (granularidad, conteos, `batch_id`, acoplamiento P1–P4).

### D-04 — Cola con reserva y 503. AD: AD-04, AD-12. CUBIERTO (forma básica).
Unidad A descartaba en silencio o mutaba sin reserva; Unidad B reserva/confirma espacio antes del commit (no-aceptado → 503 sin mutación), `resolve` con evento obligatorio no-aceptado → 503, aceptado → respuesta puede preceder persistencia, micro-batching 50 ms/50 eventos worker secuencial. Contención: spine conventions + contracts §3-Q3/§1-Q3/§2-Q2. Se registra para distinguir de H-05/H-12 (P1–P4, lector).

### D-05 — Reingesta sin idempotencia serializada. AD: AD-02, AD-12. CUBIERTO (forma básica).
Unidad A deduplicaba por hash (mismo `batch_id`); Unidad B trata cada solicitud válida como intento nuevo con `batch_id` nuevo `roster-<8hex>-<term>`, conteos en tx serializada `BEGIN IMMEDIATE`. Contención: contracts §3-Nota + spine AD-12. Se registra para distinguir de H-06 (cubetas, precedencia, retry-503).

### D-06 — Scheduler dueño + guarda con relojes separados. AD: AD-13, AD-05. CUBIERTO (forma básica).
Unidad A era solo perezosa; Unidad B combina scheduler único dueño de la mutación (máx. un evento por transición) + `resolve` que no muta, deniega desde `at>=expires_at` evaluando contra el `at` pedido incluso histórico mientras el scheduler evalúa contra su reloj actual. Contención: spine AD-13 + contracts §1-Q1/Tiempo. Se registra para distinguir de H-07 (crash, futuro-`granted`, revoke-vs-expiry).

### D-07 — Post-revocación 403 + 401-primero (caso puro). AD: AD-09, AD-03. CUBIERTO.
Unidad A respondía 401 tras la baja; Unidad B 403 `SUBJECT_ENROLLMENT_DROPPED`; ante token inválido + causa 403 pura, 401 primero. Contención: contracts §1-Auth/§2-Concurrencia + spine conventions. Se registra para distinguir de H-08/H-13 (alcance fuera de authorize, token ausente, triple-fuente).

### D-08 — UUID/`institutional_id`/`term`/`seen_ids`/email-dominio (caso puro). AD: AD-09 §0. CUBIERTO.
Unidad A hacía `strip`/`upper`; Unidad B compara `institutional_id`/`term`/`seen_ids` exacto case-sensitive, UUID válido → UUID else `institutional_id` exacto, whitespace externo/interno y controles rechazados sin recorte → `UNKNOWN_IDENTITY`, dominio email case-insensitive sin reescribir. Contención: contracts §0/§3-P1/P3 + spine conventions. Se registra para distinguir de H-09 (variantes UUID, charset).

### D-09 — Límites/replay/DTO/serialización (forma básica). AD: AD-02, AD-03, AD-11, AD-12. CUBIERTO.
5 MB = 5.000.000 bytes, exceso bytes/filas → `BATCH_TOO_LARGE` 413 antes de validar filas; `drop_reason` 1–280 Unicode sin normalizar; orden auth→identidad/curso→`DROPPED` antes de P3; `ExplanationDTO` en `ALLOW`/`DENY` y rechazos de negocio, `ErrorBody` sin DTO obligatoria en 400/401/404; mutaciones con `BEGIN IMMEDIATE`, `busy_timeout 5000` → 503 sin commit parcial, FIFO aceptación e `id ASC`. Contención: contracts §§2–4 + spine. Se registra para distinguir de H-10/H-11 (dominios de conteo, envelopes restantes).

### D-10 — Contexto en rutas (caso puro). AD: AD-01, AD-09. CUBIERTO.
Unidad A exigía header en revoke/ingest; Unidad B exige header solo en `/authorize`, revoke/ingest usan path param canónico. Contención: contracts §0 + spine AD-09. Se registra para distinguir de H-13 (autoridad entre fuentes dentro de authorize).

### O-01 — Matriz rol×acción. AD: AD-11, AD-01. CUBIERTO por OPEN.
Unidad A deniega toda acción no listada (`UNAUTHORIZED_RESOURCE_CLASS` 403); Unidad B hereda permisos gruesos. Ambas obedecen «matriz» y «`rule_ids` no vacío» porque `roles_matrix.json` no existe (contracts §6). Divergencia ya declarada bloqueante. No es hueco nuevo.

### O-02 — Capacidad máxima + recuperación post-aceptación. AD: AD-04. CUBIERTO por OPEN (TEA/NFR).
Unidad A acota / Unidad B no acota; ante fallo de persistencia tras aceptación, reintento vs bloqueo. Ambas obedecen «capacidad pendiente» y «recuperación pendiente». Ya declarado en contracts §6/spine. No es hueco nuevo. Se distingue de H-05/H-12 (acoplamiento pre-aceptación y lector).

### O-03 — Frecuencia numérica scheduler. AD: AD-13. CUBIERTO por OPEN (TEA/NFR).
Unidad A barre cada 1 s / Unidad B cada 60 s; ambas obedecen «frecuencia configurable sin número». Ya pendiente. No es hueco nuevo. Se distingue de H-07 (propiedad del evento y casos de borde, no el número).

### O-04 — Ubicación HTTP `timestamp` de baja. AD: AD-03. CUBIERTO por OPEN.
Unidad A lo lee del body / Unidad B lo fija vía `Clock`; ambas obedecen contracts §2-P4 («ubicación abierta; instante efectivo vía `Clock`; firma Annex A sin cambiar»). No es hueco nuevo.

### O-05 — `COMPLETED`, TTL, reemisión, case UUID, colisión `batch_id`, datasets NFR. CUBIERTO por OPENs.
Cada eje (transición a `COMPLETED`, expiración `uai_live_…`/`EXPIRED` sin TTL, regeneración en reingesta, case-folding UUID, colisión 8hex, datasets/concurrencia de p95/p99/1000-filas/120-filas/revocación) está declarado pendiente en contracts §6 y spine Deferred/conventions. Las divergencias que los describen exactamente no son huecos nuevos. Se distinguen de H-06/H-09/H-10 (cubetas, variantes de formato, dominios de conteo, no los valores pendientes en sí).

## B. Pares NUEVOS (huecos; ambas unidades obedecen decisiones y OPENs vigentes)

### H-01 — Codec: misma lista §5, distinto literal de nulo y de zona. AD: AD-04 (heredado).
- Unidad A: nulo → cadena ASCII `NULL`; zona UTC → sufijo `+00:00`; concatena UTF-8 en orden §5 con `timestamp` = `occurredAt` tal cual del evento y `prev` = hex minúsculo.
- Unidad B: nulo → cadena `nil` (o byte `0x00`); zona UTC → sufijo `Z`; por lo demás idéntica lista, UTF-8, orden §5, `prev` hex, FIFO e `id ASC`.
- Divergencia observable: mismo lote de eventos (p. ej. `roster.rejected` con campo opcional nulo y mismo instante) produce `record_hash` distintos; cada verificación `test_ledger_chain_and_anchor` pasa intra-unidad y rompe cruzada; export/auditoría no portable entre fixture y SQLite.
- Obediencia literal: ambas usan exactamente la lista §5, UTF-8, orden §5, `timestamp` UTC ISO-8601 con microsegundos «procedente del evento», `prev` hexadecimal, «nulos con codificación explícita única, distinta de campo omitido o cadena vacía», FIFO/`id ASC`. La decisión N-01 fijó la familia del codec, no el literal de nulo ni la forma canónica de zona (`Z` vs `+00:00` ambas son UTC ISO-8601 con microsegundos y zona explícita).
- No cubierto: D-01 cerró solo la lista; O-02/O-05 no nombran literal ni zona.

### H-02 — `at` futuro y con más de 6 decimales. AD: AD-09, AD-13 (spine-local).
- Unidad A: `at` futuro válido (p. ej. `2030-01-01T00:00:00.123456+00:00`) evalúa la vigencia en ese futuro; `at` con 9 decimales se acepta truncando a microsegundos.
- Unidad B: futuro válido en sintaxis pero fuera de ventana operativa → `INVALID_AT` 400; o exige exactamente 6 decimales → 9 decimales es `INVALID_AT` 400.
- Divergencia observable: misma petición `POST /api/v1/authorize` con `at` futuro o nanosegundos obtiene `ALLOW`/`DENY` (A) vs 400 `INVALID_AT` (B); replay de auditoría con `at` futuro diverge.
- Obediencia literal: ambas cumplen «`at` en body, opcional; solo la ausencia usa `Clock.now()`; `null`/vacío/espacios/sin-zona/sin-micro → `INVALID_AT`; `at` válido incluso histórico evalúa esa autorización; scheduler usa su reloj». Futuro y cardinalidad de decimales >6 no están definidos; «con microsegundos» admite ambas lecturas (exactamente-6 vs al-menos-micro).
- No cubierto: D-02/N-02 cerraron transporte y los inválidos listados, no futuro ni nanosegundos.

### H-03 — `term`: qué CODE y `term` no-string en JSON. AD: AD-09 (spine-local).
- Unidad A: toda violación de canal (indebido, duplicado, discrepante, ausente) → `MALFORMED_TERM` 400; `term: null` o numérico en JSON → `MALFORMED_TERM`.
- Unidad B: ausente/duplicado → `MALFORMED_BATCH` 400, discrepante → `MALFORMED_TERM`; `term: null`/numérico → `MALFORMED_BATCH` (falla el schema del lote).
- Divergencia observable: misma petición obtiene mismo HTTP 400 pero `code` distinto y `ExplanationDTO`/`detail` distintos; cliente que ramifica por `code` diverge.
- Obediencia literal: ambas cumplen «CSV solo query, JSON solo body; canal indebido/duplicado/discrepancia/ausencia → rechazo; `MALFORMED_TERM` o `MALFORMED_BATCH`; regla única sin elegir valor; regex `^[0-9]{4}-(SPRING|SUMMER|FALL)$` case-sensitive». «El error tipado existente más adecuado» admite ambas asignaciones; el tipo JSON de `term` no está fijado.
- No cubierto: D-02/N-03 cerraron exclusividad de canal, no la elección de CODE.

### H-04 — Manifiesto: granularidad, conteos en 422 y `batch_id` en rechazo. AD: AD-02 (heredado), AD-04 (heredado), AD-11 (spine-local).
- Unidad A: fila con dos campos inválidos emite dos filas de manifiesto (una por campo); 422 JSON incluye `{processed:0, created_identities:0, updated_memberships:0}` + `errors[]` + anexo CSV; evento `roster.rejected` porta `batch_id` generado aunque el lote no persista.
- Unidad B: misma fila emite una sola fila de manifiesto (primer campo); 422 JSON porta solo `errors[]` + anexo sin conteos; evento `roster.rejected` porta `batch_id: null`/ausente (sin lote comprometido no hay `batch_id`).
- Divergencia observable: mismo lote inválido produce manifiestos con distinto número de líneas, 422 con shapes distintos y payloads de ledger distintos (`batch_id` presente vs ausente); `row_number`/`observed_invalid_row` citados en `ExplanationDTO` difieren.
- Obediencia literal: ambas hacen «rollback total, 0 escrituras, sin credenciales; después `roster.rejected` en la misma cadena única 1:1 que afecta el siguiente `prev`; 422 tras aceptación sin esperar persistencia; manifiesto `roster_rejected_conflicts.csv: row_number, institutional_id, field, observed, expected`; `explanation` cita AD-02». Cardinalidad por-campo vs por-fila, presencia de conteos en 422 y de `batch_id` en rechazo no están definidas.
- No cubierto: D-03/N-04/N-05 cerraron orden/ventana/cadena, no granularidad ni shapes.

### H-05 — Fallos P1–P4 bajo cola llena: 400/404 vs 503. AD: AD-04 (heredado), AD-12 (spine-local), AD-11.
- Unidad A: `INVALID_AT`/`UNKNOWN_IDENTITY`/`MALFORMED_RESOURCE_ARN` también emiten auditoría (intento) y por tanto reservan cola; con cola llena responden 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE` en vez del 400/404.
- Unidad B: P1–P4 no tocan la cola («si falla P1–P4 no hay mutación» incluye no-evento); con cola llena responden el 400/404 igualmente.
- Divergencia observable: misma petición malformada bajo presión obtiene 503 (A) vs 400/404 (B); conteo de eventos en ledger difiere (con/sin intento P1–P4); reintento del cliente diverge.
- Obediencia literal: ambas cumplen «evento por mutación/decisión; Q-fail P1–P4 sin mutación, P5 solo registra el denegado; mutantes reservan antes del commit, no-aceptado → 503; `resolve` con evento obligatorio no-aceptado → 503». Si el evento de intento P1–P4 es «mutación» o no, no está definido; `ExplanationDTO` vs `ErrorBody` (N-15) fija el envelope, no la emisión al ledger.
- No cubierto: D-04/N-06 cerraron reserva para mutantes y `resolve` con evento, no el alcance P1–P4; O-02 dejó capacidad/recuperación, no este acoplamiento.

### H-06 — Reingesta: cubeta created-vs-updated, precedencia de CODEs y retry tras 503. AD: AD-02 (heredado), AD-12.
- Unidad A: identidad existente + membresía nueva en el curso → `updated_memberships+1` (`created_identities+0`); fila ya idéntica cuenta como `updated`; ante fila a la vez duplicada (`seen_ids`), con email inválido y con identidad `SUSPENDED`, emite `ROSTER_VALIDATION_FAILED`; retry tras 503 genera `batch_id` nuevo.
- Unidad B: mismo caso → `created_identities+0`/`updated_memberships+0` o cubeta distinta (membresía nueva no es «updated»); fila idéntica cuenta `+0`; mismo lote emite `INTRA_BATCH_DUPLICATE_ID` o `IDENTITY_BARRED`; retry tras 503 reutiliza el `batch_id` del intento no-aceptado.
- Divergencia observable: mismo lote válido/inválido produce 201 con conteos cruzados distintos o 422 con `code` distinto; misma secuencia retry-503 produce pares de `batch_id` distintos.
- Obediencia literal: ambas cumplen «sin idempotencia por contenido; intento nuevo con `batch_id` nuevo `roster-<8hex>-<term>`; reglas normales identidad/membresía/unicidad; conteos en tx serializada según estado al turno; `BEGIN IMMEDIATE`; 8hex sin garantía». Qué cubeta cubre «identidad vieja + membresía nueva», si «updated» exige cambio efectivo, el orden P3-vs-P4 y si un 503 cuenta como «intento» no están definidos.
- No cubierto: D-05/N-11 cerraron no-idempotencia y serialización; colisión y reemisión pendientes son otros ejes (integridad del generador y credenciales, no cubetas/precedencia/retry).

### H-07 — Scheduler: crash, `granted_at` futuro e interacción con revoke. AD: AD-13 (spine-local), AD-05 (heredado), AD-04.
- Unidad A: si el scheduler muta a expirado pero cae antes de emitir, al reiniciar re-emite (transición aún sin evidencia); ticket con `granted_at` futuro y `expires_at` pasado se expira igual; membresía `DROPPED` con ticket `ACTIVE` se expira igual con evento.
- Unidad B: al reiniciar suprime el evento (estado ya expirado, «máx. un evento por transición efectiva» ya consumido por la mutación); ticket nunca-vigente se ignora sin mutación/evento; con membresía `DROPPED` se omite la expiración (sin transición efectiva).
- Divergencia observable: mismo historial produce store `ACTIVE` vs `EXPIRED` y ledger con 0/1/2 eventos para la misma expiración; `ExplanationDTO` idéntica en `observed`/`expires_at` pero con conteos/`reason_code` distintos.
- Obediencia literal: ambas cumplen «scheduler único dueño de la mutación (máx. un evento por transición); `resolve` no muta y evalúa contra `at` incl. histórico; scheduler contra reloj actual; `at>=expires_at` deniega». Qué es «transición efectiva» tras crash, si `granted_at` futuro habilita expiración y si `DROPPED` cancela la expiración no están definidos.
- No cubierto: D-06/N-07/N-08 cerraron doble vía y relojes; O-03 dejó solo la frecuencia; la recuperación post-aceptación pendiente es de cola, no de crash del scheduler.

### H-08 — Precedencia fuera de authorize y token ausente. AD: AD-09 (spine-local), PRD §5.2.
- Unidad A: en `ingestRoster` con Bearer inválido + lote malformado responde 401 (auth siempre primero en las tres operaciones); header `Authorization` ausente → 401.
- Unidad B: en el mismo ingest responde 400 `MALFORMED_BATCH`/`MALFORMED_TERM` primero (sintaxis del lote antes que auth fuera de authorize); header ausente → 400 (petición malformada, no 401).
- Divergencia observable: misma petición de roster/revoke obtiene 401 (A) vs 400/422 (B); reintentabilidad percibida y `code` divergen aunque ambos sean no-reintentables.
- Obediencia literal: ambas cumplen «token inválido/vencido → 401; sin contexto/membresía/mismatch → 403; primero autenticación luego contexto/membresía». El alcance de «primero» a ingest/revoke con fallo sintáctico concurrente y el mapeo de «ausente» (401 vs 400) no están definidos.
- No cubierto: D-07/N-09 cerraron solo el caso puro authorize 401-vs-403; O-04 es otro eje (`timestamp`).

### H-09 — UUID: variantes de formato y charset de `institutional_id`. AD: AD-09 §0 (spine-local), AD-08.
- Unidad A: solo acepta UUID canónico 36-char con guiones en minúsculas como UUID; `{uuid}`, `urn:uuid:<uuid>`, 32-hex sin guiones y UUID en mayúsculas se tratan como `institutional_id` → `UNKNOWN_IDENTITY` 404; `institutional_id` con `_`/`.`/`/` se rechaza como `UNKNOWN_IDENTITY` 404 (todo no-resuelto es 404, sin códigos nuevos).
- Unidad B: acepta las cuatro variantes como UUID (misma identidad); `institutional_id` con charset fuera de alfanumérico-guiones se mapea a 400 de formato (no a 404).
- Divergencia observable: mismo `user_id` resuelve a identidades distintas o a `CODE`/HTTP distintos (404 vs 400); joins con `UNIQUE(identity_id, subject_id)` divergen.
- Obediencia literal: ambas cumplen «UUID estándar válido → UUID, si no `institutional_id` exacto; whitespace/control rechazados sin recorte; no-resuelve → `UNKNOWN_IDENTITY` existente; sin códigos nuevos». Qué cadenas son «UUID estándar válido» (llaves/URN/sin-guiones) y si el charset ilegal es 404 o 400 no están definidos.
- No cubierto: D-08/N-10 cerraron orden/whitespace externo; el pendiente case-UUID cubre solo plegado de caso, no estas variantes ni el charset.

### H-10 — Dominios de conteo: bytes, filas y `drop_reason`. AD: AD-02 (heredado), AD-03 (heredado), catálogo.
- Unidad A: bytes = `Content-Length` del body HTTP; filas = solo filas de datos (cabecera excluida, línea vacía final ignorada); `drop_reason` de solo-espacios (`"   "`) es válido (3/280); longitud = `len()` code points.
- Unidad B: bytes = UTF-8 de `rows[]` decodificadas (para JSON, sin overhead del envelope); filas = toda línea incl. cabecera; solo-espacios → `MALFORMED_DROP_REASON` 400 (vacío efectivo); longitud = clusters de grafemas (emoji ZWJ cuenta 1).
- Divergencia observable: mismo lote en el borde obtiene 201 (A) vs 413 (B), o 200 `REVOKED` (A) vs 400 (B) para el mismo `drop_reason`; lote de 1000 datos + cabecera obtiene 201 vs 413.
- Obediencia literal: ambas cumplen «cuerpo ≤5.000.000 bytes, 1–1000 filas, UTF-8, columnas exactas; exceso → `BATCH_TOO_LARGE` 413 antes de validar filas; `drop_reason` 1–280 caracteres Unicode sin normalizar (no bytes)». Sobre qué bytes, qué líneas cuentan, si todo-blancos es vacío y si «caracteres» son code points o grafemas no hay regla.
- No cubierto: D-09/N-14 cerraron unidad (5.000.000) y orden, no estos dominios.

### H-11 — Replay con `explanation` y envelope 409/422/413/503. AD: AD-03 (heredado), AD-11 (spine-local), AD-12.
- Unidad A: `ALREADY_REVOKED` 200 incluye `explanation` (cita AD-03 con `observed_prior_status`); 409 `INVALID_TRANSITION` y 422 `ROSTER_VALIDATION_FAILED` portan `ExplanationDTO` con `rule_ids` no vacío (son «rechazos de negocio»).
- Unidad B: `ALREADY_REVOKED` 200 sin `explanation` (es éxito idempotente, no decisión ni rechazo); 409/422/413/503 usan `ErrorBody` tipado sin `ExplanationDTO` obligatoria (como 400/401/404).
- Divergencia observable: misma repetición obtiene 200 con/sin `explanation`; mismos 409/422/413/503 obtienen shapes incompatibles y `rule_ids` presentes vs ausentes.
- Obediencia literal: ambas cumplen «rama `DROPPED→ALREADY_REVOKED` con `revocation_propagated_at` original, sin mutación/evento, antes de P3; `ExplanationDTO` obligatoria en `ALLOW`/`DENY` y rechazos de negocio §§1–3 Q4; 400/401/404 con `ErrorBody` sin DTO obligatoria; `reason_code` del catálogo». Si el replay-200 es «rechazo de negocio» y si 409/422/413/503 son «rechazo» o «error tipado» no está definido.
- No cubierto: D-09/N-15 cerraron orden y alcance 400/401/404, no estos envelopes.

### H-12 — Lector bajo contienda y cardinalidad del instante. AD: AD-03 (heredado), AD-12 (spine-local), AD-04.3, AD-08, AD-13.
- Unidad A (single-instant + lector diferido): el adapter llama `Clock.now()` una vez por request y propaga el mismo string a `dropped_at`/`revoked_at`/`revocation_propagated_at`/`occurredAt`; `resolve` concurrente con ingest usa lectura diferida del snapshot previo y responde veredicto aunque haya `BEGIN IMMEDIATE` contendiendo.
- Unidad B (multi-now + lector inmediato): cada capa llama `Clock.now()` cuando lo necesita (`dropped_at≠revoked_at≠occurredAt` por µs; replay retorna `revocation_propagated_at` fresco); `resolve` bajo contienda espera `busy_timeout 5000` en `BEGIN IMMEDIATE` y ante `SQLITE_BUSY` agotado responde 503.
- Divergencia observable: misma ráfaga obtiene veredicto 200/403 (A) vs 503 (B) para el mismo `authorize`; receipts y ledger difieren por µs; igualdad `occurredAt==timestamp` byte-a-byte pasa en A y falla en B; orden `id ASC` resultante difiere bajo micro-batching.
- Obediencia literal: ambas usan medios permitidos («`BEGIN IMMEDIATE`; prohibido leer-luego-actualizar; `workers:1`, `busy_timeout 5000` → 503 sin commit parcial; flush 50 ms/50 eventos worker secuencial; FIFO/`id ASC`; tiempo solo por `Clock`; `at` ausente → `now()` en adapter»). Cardinalidad/propagación del instante (uno por request vs uno por campo/evento) y modo del lector (`IMMEDIATE` vs diferido) no están definidos.
- No cubierto: D-04/D-09/N-16 cerraron serialización de mutantes, timeout y orden, no el lector ni la cardinalidad (eje P4 antiguo nunca contenido por N-01..N-16).

### H-13 — Triple fuente de curso y precedencia de CODEs 404-vs-403. AD: AD-01 (heredado), AD-09 (spine-local).
- Petición `POST /api/v1/authorize` con header `X-Academic-Subject-Context: CS101`, `resource_arn` con subject `CS-480` y membresía `ACTIVE` solo en uno de los dos (o header con curso inexistente `CS999`).
- Unidad A (header-autoridad): valida existencia del header-curso primero → header `CS999` es `UNKNOWN_COURSE` 404; si ambos existen pero difieren, chequea membresía del header-curso y luego mismatch → `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` vs `RESOURCE_SUBJECT_MISMATCH` según su orden.
- Unidad B (ARN-autoridad): valida ARN/mismatch primero → mismo input es 403 `RESOURCE_SUBJECT_MISMATCH`; con header inexistente pero ARN válido responde 403 antes que 404.
- Divergencia observable: misma petición obtiene 404 (A) vs 403 (B), o dos 403 con `code`/`observed_context`/`observed_resource_subject` distintos en `ExplanationDTO`; el Mandatory Edge Case re-evaluado con fuentes cruzadas diverge en `code` aunque ambas denieguen.
- Obediencia literal: ambas cumplen «header obligatorio en `/authorize`; comparación cruda byte-a-byte header vs subject del ARN sin normalizar; `courseId` activo si no → `UNKNOWN_COURSE` 404; sin contexto/membresía → `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`, mismatch → `RESOURCE_SUBJECT_MISMATCH`; 401-primero». Cuál fuente es `courseId` y la precedencia entre los tres 404/403 no están definidas.
- No cubierto: D-07/D-10/N-09/N-12 cerraron caso puro y header-solo-authorize, no la autoridad ni la precedencia entre estas tres ramas; la matriz pendiente es de rol×acción, otro eje.

## Conteo y escala

- CUBIERTOS: 15 grupos (D-01..D-10 + O-01..O-05). No computan como huecos.
- NUEVOS: 13 (H-01..H-13). Cada uno admite dos unidades un nivel abajo que obedecen al pie de la letra las decisiones N-01..N-16 y los pendientes vigentes y aun así divergen en HTTP, estado o ledger.
- Escala: **NO ROBUSTO (13 pares)**.

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; ningún OPEN fue cerrado; ninguna edición fue propuesta.*
