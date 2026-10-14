# Revisión adversarial — Reviewer Gate bmad-architecture (2026-10-13, vuelta 2)

- Fecha: 2026-10-13
- Alcance: `solu2-module1` — `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)` + `EDGE-01 Multi-Subject Permission Resolution` + Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»).
- Fuentes leídas (solo lectura):
  1. `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (136 líneas, `updated: 2026-10-12` en frontmatter; con decisiones `[ADOPTED 2026-10-13]` en cuerpo).
  2. `solu2-module1/planning/detailed-design/contracts.md` (154 líneas).
  3. `resultados-interaccion.md` (10 líneas; se usa como antecedente Fase 1, subordinado a las decisiones `[ADOPTED 2026-10-13]` ya plasmadas en spine/contracts cuando hay conflicto).
- Decisiones cerradas asumidas en esta versión (no se reabren): fórmula hash normativa AD-04 §5; transporte `at`/`term`; roster 422 con `roster.rejected` posterior; cola llena → 503; reingesta sin idempotencia; scheduler + guarda `now>=exp`; post-revocación 403 unificado; UUID estándar sin recorte.
- Abiertos asumidos (no se cierran): matriz rol×acción (`roles_matrix.json` inexistente); capacidad máxima de cola; recuperación tras fallo de persistencia; frecuencia numérica del scheduler; ubicación HTTP del `timestamp` de baja; `COMPLETED`; TTL `uai_live`; datasets NFR; regeneración de credenciales en reingesta; case de UUID.
- No se propone ninguna edición. No se cierra ningún OPEN.

## Método

Adversario un nivel abajo: por cada AD se construyen dos unidades hipotéticas que obedecen el texto del AD al pie de la letra (misma cita literal) y aun así divergen en observable HTTP, estado persistido o ledger. Cada divergencia es un par = un hueco. Datos compartidos, doble dueño o mutación en conflicto califican como hueco.

- `CUBIERTO`: el par ataca exactamente el punto ya decidido (la decisión lo contiene) o describe exactamente la divergencia ya registrada como `[OPEN]`/pendiente. No es hueco nuevo.
- `NUEVO`: ambas unidades obedecen las decisiones cerradas y los OPENs vigentes y aun así divergen en un matiz no documentado en spine/contracts/memlog transferido (§6). Es hueco.
- Escala: `ROBUSTO` = 0 pares `NUEVO`; `NO ROBUSTO` = N pares `NUEVO` (N>0).

## Veredicto

**NO ROBUSTO (16 pares NUEVOS).** 14 pares CUBIERTOS (8 por decisiones cerradas + 6 grupos por OPENs) no son huecos nuevos; se listan para distinguir.

## Resumen

| ID | Foco | AD involucrados | Estado |
| --- | --- | --- | --- |
| D-01 | Hash: resumen §2 vs §5 | AD-04 (heredado) | CUBIERTO por decisión (fórmula §5) |
| D-02 | Transporte `at` body / `term` query+body | AD-09 (spine-local), AD-13 (spine-local) | CUBIERTO por decisión |
| D-03 | Roster 422 con `roster.rejected` posterior tx separada | AD-02 (heredado), AD-04 (heredado) | CUBIERTO por decisión (forma básica) |
| D-04 | Cola llena → 503 | AD-04 (heredado) | CUBIERTO por decisión (forma básica) |
| D-05 | Reingesta sin idempotencia, `batch_id` nuevo | AD-02 (heredado), AD-12 (spine-local) | CUBIERTO por decisión (forma básica) |
| D-06 | Scheduler + guarda `now>=expires_at` | AD-13 (spine-local), AD-05 (heredado) | CUBIERTO por decisión (forma básica) |
| D-07 | Post-revocación 403 unificado | AD-09 (spine-local), AD-03 (heredado) | CUBIERTO por decisión (caso puro) |
| D-08 | UUID estándar, espacios externos → rechazo sin recorte | AD-09 (spine-local) §0 | CUBIERTO por decisión (caso puro) |
| O-01 | Matriz rol×acción ausente | AD-11 (spine-local), AD-01 (heredado) | CUBIERTO por OPEN (`roles_matrix.json`) |
| O-02 | Frecuencia numérica scheduler | AD-13 (spine-local) | CUBIERTO por OPEN (TEA/NFR) |
| O-03 | Capacidad máxima cola + recuperación persistencia | AD-04 (heredado) | CUBIERTO por OPEN (TEA/NFR) |
| O-04 | Ubicación HTTP `timestamp` baja | AD-03 (heredado) | CUBIERTO por OPEN |
| O-05 | `COMPLETED` + TTL `uai_live` + regeneración en reingesta + case UUID | AD-03 (heredado), AD-02 (heredado), AD-09 §0 | CUBIERTO por OPENs |
| O-06 | Datasets/concurrencia NFR (p95/p99, 1000 filas, 120 filas) | NFR-PERF-01/02, FR-INGEST-01 | CUBIERTO por OPEN (PLANNED) |
| N-01 | Hash: misma lista §5, distinta serialización | AD-04 (heredado) | NUEVO |
| N-02 | `at` ausente vs inválido: `""`, `null`, sin zona, sin microsegundos | AD-09, AD-13, AD-08 | NUEVO |
| N-03 | `term` query vs body en desacuerdo | AD-09 | NUEVO |
| N-04 | `roster.rejected`: ventana respuesta 422 vs commit | AD-02, AD-04, AD-12 | NUEVO |
| N-05 | `roster.rejected`: misma cadena vs log separado; `audit_events` 1:1 | AD-04 | NUEVO |
| N-06 | Cola llena con mutación/decisión ya comprometida (resolve vs ingest) | AD-04, AD-12, AD-02 | NUEVO |
| N-07 | Doble dueño expiración: qué escribe el scheduler, qué evento emite cada parte | AD-13, AD-05, AD-04, AD-11 | NUEVO |
| N-08 | Reloj de evaluación: `at` histórico vs `now` del scheduler | AD-13, AD-05 | NUEVO |
| N-09 | Precedencia 401 vs 403 con causas concurrentes | AD-09, PRD §5.2 | NUEVO |
| N-10 | Resolución `userId`: orden UUID vs `institutional_id`, espacios internos, CODE | AD-08, AD-09 §0 | NUEVO |
| N-11 | Reingesta concurrente: doble `batch_id`, conteos, colisión `<8hex>` | AD-02, AD-12 | NUEVO |
| N-12 | Header `X-Academic-Subject-Context` vs path `{subject_id}` en revoke/ingest | AD-01, AD-09 | NUEVO |
| N-13 | Case: dominio de email + `seen_ids` | AD-02, AD-09 §0 | NUEVO |
| N-14 | Límites y conteos: 5 MB, 400 vs 413, `drop_reason` chars vs bytes | AD-02, catálogo, AD-03 | NUEVO |
| N-15 | Replay `ALREADY_REVOKED` vs validación P3; alcance `ExplanationDTO` en 400/401/404 | AD-03, AD-12, AD-11 | NUEVO |
| N-16 | Serialización física: `BEGIN IMMEDIATE` vs predicado; `busy_timeout`; orden micro-batching | AD-03, AD-12, AD-04.3 | NUEVO |

## A. Pares CUBIERTOS por decisiones/OPEN (no son huecos nuevos)

### D-01 — Hash §5 vs resumen §2. AD: AD-04. CUBIERTO por decisión.
Unidad A encadena `SHA256(prev || timestamp || actor_id || subject_id || resource_arn || action || decision || reason_code)` (`planning/ARCHITECTURE.md` l.364-365, contracts §1-Q3). Unidad B encadenaba el resumen de ARCH §2 (l.95-96, sin `subject_id`/`action`). Divergencia ingenua: cadenas incompatibles. Contención: contracts §1-Q3 y spine AD-04 declaran §5 normativa y el §2 «resumen incompleto». El ataque ingenuo ya no es obediencia válida. Se registra solo para distinguir de N-01.

### D-02 — Transporte `at`/`term`. AD: AD-09, AD-13. CUBIERTO por decisión.
Unidad A ponía `at` en query y `term` en body para CSV. Unidad B pone `at` en body JSON (opcional; ausente → `Clock.now()` en adapter) y `term` en query (`?term=`) para CSV / campo body para JSON. Divergencia ingenua contenida por la regla `[ADOPTED 2026-10-13]` en spine AD-09 y contracts §0. Se registra para distinguir de N-02/N-03, que atacan bordes no fijados.

### D-03 — Roster 422 con evento posterior. AD: AD-02, AD-04. CUBIERTO por decisión (forma básica).
Unidad A no emitía nada ante 422 (leía `Q-fail` aislado). Unidad B revierte todo y después registra `roster.rejected` en tx separada con manifiesto (`roster_rejected_conflicts.csv`). Contención básica: contracts §3-Q3 y spine conventions fijan rollback + evento posterior. Se registra para distinguir de N-04/N-05 (ventana y cadena).

### D-04 — Cola llena → 503. AD: AD-04. CUBIERTO por decisión (forma básica).
Unidad A descartaba en silencio. Unidad B retorna 503 fail-closed (`AUTH_INTERNAL_POLICY_UNAVAILABLE`). Contención básica: spine conventions + contracts §3-Q3 («sin descarte silencioso; cola llena antes de responder → 503»). Se registra para distinguir de N-06 (mutación ya comprometida) y N-16 (orden).

### D-05 — Reingesta sin idempotencia. AD: AD-02, AD-12. CUBIERTO por decisión (forma básica).
Unidad A deduplicaba por hash de contenido (mismo `batch_id`). Unidad B trata cada solicitud válida como intento nuevo con `batch_id` nuevo (`roster-<8hex>-<term>`). Contención básica: contracts §3-Nota y spine AD-12. Se registra para distinguir de N-11 (concurrencia/conteos/colisión) y O-05 (regeneración).

### D-06 — Scheduler + guarda. AD: AD-13, AD-05. CUBIERTO por decisión (forma básica).
Unidad A era solo perezosa (sin scheduler). Unidad B combina scheduler que auto-revoca (PRD §4.2 R5) + guarda `resolve` que deniega desde `now >= expires_at` aunque el scheduler no haya corrido. Contención básica: spine AD-13 y contracts §1-Tiempo eliminan «solo perezosa» como equivalente. Se registra para distinguir de N-07/N-08 y O-02.

### D-07 — Post-revocación 403 unificado. AD: AD-09, AD-03. CUBIERTO por decisión (caso puro).
Unidad A respondía 401 tras la baja; Unidad B 403 `SUBJECT_ENROLLMENT_DROPPED`. Contención del caso puro: contracts §1-Auth y §2-Concurrencia + spine conventions fijan 403 unificado registrando que el PRD admite 401 o 403. Se registra para distinguir de N-09 (causas concurrentes).

### D-08 — UUID estándar sin recorte. AD: AD-09 §0. CUBIERTO por decisión (caso puro).
Unidad A hacía `strip()` y resolvía `"  <uuid>  "`; Unidad B rechaza con espacios externos sin recorte (`UNKNOWN_IDENTITY`). Contención del caso puro: contracts §0 y spine conventions. Se registra para distinguir de N-10 y O-05.

### O-01 — Matriz rol×acción. AD: AD-11, AD-01. CUBIERTO por OPEN.
Unidad A deniega toda acción no listada (`UNAUTHORIZED_RESOURCE_CLASS` 403 fail-closed). Unidad B hereda permisos gruesos (p. ej. `ta` ⊇ `student`). Ambas obedecen «matriz» y «`rule_ids` no vacío» porque `roles_matrix.json` no existe en el workspace (contracts §6). Divergencia ya documentada como bloqueante. No es hueco nuevo.

### O-02 — Frecuencia numérica del scheduler. AD: AD-13. CUBIERTO por OPEN.
Unidad A barre cada 1 s; Unidad B cada 60 s. Ambas obedecen «frecuencia configurable sin número fijado». Ventana donde el estado persistido sigue `ACTIVE` pero `resolve` ya deniega difiere en duración observable. Ya pendiente TEA/NFR. No es hueco nuevo.

### O-03 — Capacidad máxima de cola + recuperación tras fallo de persistencia. AD: AD-04. CUBIERTO por OPEN.
Unidad A buffer acotado (p. ej. 50, espejo del flush); Unidad B no acotado. Ante fallo de persistencia, Unidad A reintenta y Unidad B bloquea. Ambas obedecen «capacidad pendiente» y «recuperación pendiente». Ya pendiente TEA/NFR. No es hueco nuevo.

### O-04 — Ubicación HTTP del `timestamp` de baja. AD: AD-03. CUBIERTO por OPEN.
Unidad A lo lee del body; Unidad B lo ignora y fija `dropped_at`/`revocation_propagated_at` desde `Clock`. Ambas obedecen contracts §2-P4 («ubicación abierta; instante efectivo vía `Clock`; firma Annex A sin cambiar»). Divergencia ya abierta. No es hueco nuevo.

### O-05 — `COMPLETED`, TTL `uai_live`, regeneración en reingesta, case UUID. AD: AD-03, AD-02, AD-09 §0. CUBIERTO por OPENs.
Unidad A transiciona a `COMPLETED` / expira `uai_live` / regenera credenciales en reingesta / compara UUID case-insensitive; Unidad B deja `SUSPENDED`/`COMPLETED` como `INVALID_TRANSITION`, credenciales sin TTL, reutiliza credenciales, compara exacto. Cada eje está declarado pendiente en contracts §6 y spine Deferred/conventions («actor y momento de `COMPLETED`», «TTL sin regla», «regeneración pendiente», «case de UUID pendiente»). No son huecos nuevos.

### O-06 — Datasets y concurrencia nominal NFR. AD: N/A (NFR-PERF-01 p95 <20 ms + p99 <50 ms a 100 req/s; NFR-PERF-02 1000 filas <3.0 s; FR-INGEST-01 120 filas <2.0 s; NFR-REVOC-03 <200 ms / <60 s). CUBIERTO por OPEN.
Dos harnesses con datasets y concurrencies distintas ambos cumplen «PLANNED, pendiente de benchmark». Ya registrado («dataset y concurrencia nominal de cada umbral en contradicción»). No es hueco nuevo.

## B. Pares NUEVOS (huecos; ambas unidades obedecen decisiones y OPENs vigentes)

### N-01 — Fórmula hash en DDL/adapters vs contrato: misma lista, distinta serialización. AD: AD-04 (heredado).
- Unidad A (contrato): concatena representaciones UTF-8 con separador `||` literal, `timestamp` = `occurredAt` UTC con microsegundos, `prev` = hex del evento anterior, campos nulos como cadena vacía.
- Unidad B (DDL/adapter): concatena bytes sin separador, `timestamp` = instante de commit SQLite, `prev` = entero `id`, nulo omitido.
- Divergencia observable: mismo lote de eventos produce hashes distintos; la verificación por `id ASC` (`test_ledger_chain_and_anchor`) pasa intra-unidad y rompe cruzada; auditoría no portable entre adapter real y fixtures.
- Obediencia literal: ambas usan exactamente la lista §5 (`prev || timestamp || actor_id || subject_id || resource_arn || action || decision || reason_code`); la decisión cerró la lista, no el codec, el `timestamp` de referencia, la codificación de `prev`, el tratamiento de nulo/vacío (p. ej. `subject_id` en `roster.rejected`), ni el orden de `id ASC` frente a orden de flush.
- No cubierto: D-01 cerró solo la lista; ningún OPEN nombra serialización.

### N-02 — `at` ausente vs inválido. AD: AD-09, AD-13, AD-08.
- Unidad A: `at: ""`, `"   "`, `null` explícito o campo ausente → todos equivalen a ausente → `Clock.now()` en el adapter.
- Unidad B: solo la ausencia de la clave equivale a ausente; `""`/`"   "`/`null` son valores presentes malformados → `INVALID_AT` 400; además A acepta ISO sin zona o sin microsegundos (los completa a UTC) mientras B exige zona explícita y microsegundos (contracts §0/§1-P3 vs spine AD-13 «UTC ISO-8601 con microsegundos»).
- Divergencia observable: mismo body obtiene 200/403 vs 400; replay con `at` histórico válido-en-A es 400-en-B.
- Obediencia literal: ambas cumplen «`at` en body, opcional; ausente → `Clock.now()` en el adapter, nunca en el dominio» y «violación → `INVALID_AT` 400»; el borde `""`/`null`/blancos/sin-zona/sin-microsegundos no está definido.
- No cubierto: D-02 cerró solo el transporte; ningún OPEN nombra este borde.

### N-03 — `term` query vs body en desacuerdo. AD: AD-09.
- Unidad A (pre-query): en JSON con `?term=2026-FALL` + `body.term=2026-SPRING` manda query; en CSV ignora `body.term`.
- Unidad B (pre-body/rechazo): manda body, o rechaza 400 `MALFORMED_TERM` ante desacuerdo, o exige exactamente un portador según formato.
- Divergencia observable: misma petición obtiene 201 con `batch_id` `roster-<8hex>-2026-FALL` vs `...-2026-SPRING` vs 400; `batch_id` deriva de `term`.
- Obediencia literal: ambas cumplen «`term` en query para CSV y campo del body para JSON» + regex `^[0-9]{4}-(SPRING|SUMMER|FALL)$` case-sensitive; el caso mixto/doble-portador/desacuerdo/ausencia-total no está definido.
- No cubierto: D-02 cerró portadores por formato, no precedencia en desacuerdo.

### N-04 — `roster.rejected`: ventana entre 422 y commit. AD: AD-02, AD-04, AD-12.
- Unidad A: hace rollback, responde 422 con manifiesto + anexo CSV, y encola `roster.rejected` asíncrono (micro-batching 50 ms/50 eventos).
- Unidad B: hace rollback, commitea `roster.rejected` y solo entonces responde 422 (o 503 si la cola no acepta).
- Divergencia observable: cliente con 422 que consulta el ledger de inmediato ve 0 eventos (A) vs 1 evento (B); ante cola llena en esa ventana, A ya respondió 422 y B responde 503 para el mismo lote.
- Obediencia literal: ambas hacen «rollback total y después evento en tx separada; evento no aceptado → 503 sin descarte».
- No cubierto: D-03/D-04 fijan orden lógico y 503, no si la respuesta espera al commit del evento.

### N-05 — `roster.rejected`: misma cadena vs log separado; doble dueño `audit_ledger`/`audit_events`. AD: AD-04.
- Unidad A: `roster.rejected` avanza la misma cadena (muta `prev` para el siguiente evento).
- Unidad B: lo escribe en quarentena separada que no avanza `prev` (o en `TABLA audit_events 1:1` con dueño distinto de `audit_ledger`+metadata del Capability Map).
- Divergencia observable: la verificación `id ASC` y `AUDIT_LOG_TAMPERING_DETECTED` pasan en una topología y fallan en la otra; el export bloqueado diverge.
- Obediencia literal: ambas «registran un evento `roster.rejected` en el ledger»; la identidad tabla/cadena y el mapa `LedgerWriter + audit_ledger(+metadata) + TABLA audit_events 1:1` admiten ambas lecturas.
- No cubierto: ningún OPEN nombra topología del evento de rechazo.

### N-06 — Cola llena con mutación/decisión ya comprometida: resolve vs ingest. AD: AD-04, AD-12, AD-02.
- Unidad A (ingest): lote persistido + evento rechazado por cola llena → conserva el lote y retorna 503; Unidad B: revierte el lote y retorna 503. Unidad A (resolve): veredicto computado + evento rechazado → retorna 503 sin veredicto; Unidad B: retorna el veredicto (200/403) y encola con pérdida evitada por bloqueo.
- Divergencia observable: mismo desborde deja N filas vs 0 filas; mismo `authorize` obtiene 503 vs veredicto; reintento del cliente duplica o no.
- Obediencia literal: todas cumplen «cola llena antes de responder → 503 fail-closed; sin descarte silencioso» y «todo o nada»; el acoplamiento commit-mutación/commit-evento no está definido.
- No cubierto: D-04 fijó el código, no si la mutación sobrevive al 503; O-03 dejó capacidad/recuperación, no este acoplamiento.

### N-07 — Doble scheduler + guarda: quién muta y qué evento se emite. AD: AD-13, AD-05, AD-04, AD-11.
- Unidad S (scheduler-owner): al vencer escribe el ticket (`EXPIRED`/`REVOKED`) y emite evento de auditoría con `reason_code` de éxito/baja.
- Unidad G (guard-only): el scheduler solo marca, o nadie escribe; `resolve` deniega `STATUS_ESCALATION_EXPIRED` 403 sin mutar y emite el `DENY`.
- Divergencia observable: tras `now>=expires_at` sin barrido, el store muestra ticket aún `ACTIVE` (G) vs ya transicionado (S); el ledger muestra 0, 1 o 2 eventos para la misma expiración; `ExplanationDTO` cita AD-13 con `observed`/`expires_at` idénticos pero `reason_code` y conteo de eventos distintos; dos expiraciones concurrentes mutan dos veces (doble dueño) o una.
- Obediencia literal: ambas cumplen «scheduler auto-revoca» + «`resolve` deniega desde `now>=expires_at` aunque el scheduler aún no haya actualizado» + «evento por mutación/decisión» + «escrituras con predicado o `BEGIN IMMEDIATE`, prohibido leer-luego-actualizar».
- No cubierto: D-06 fijó la doble vía, no la propiedad de la mutación ni el conteo de eventos; O-02 dejó solo la frecuencia.

### N-08 — Reloj de evaluación: `at` histórico vs `now`. AD: AD-13, AD-05.
- Unidad A evalúa la vigencia contra `at` de la petición (`granted_at <= at < expires_at`, contracts §1-Q1).
- Unidad B evalúa contra `now` del `Clock`/scheduler (`resolve` deniega desde `now>=expires_at`, contracts §1-Tiempo).
- Divergencia observable: replay/auditoría con `at` pasado válido pero `now` expirado obtiene `ALLOW` (A) vs `DENY STATUS_ESCALATION_EXPIRED` (B); el Mandatory Edge Case re-evaluado en el pasado diverge.
- Obediencia literal: ambas citan texto vigente («intervalo `[granted_at, expires_at)`» y ambas frases de contracts); la variable de referencia cuando `at != now` no está desambiguada.
- No cubierto: D-06 cerró la guarda, no la variable para replay.

### N-09 — Precedencia 401 vs 403 con causas concurrentes. AD: AD-09, PRD §5.2.
- Petición con token inválido/vencido Y membresía `DROPPED`/mismatch/contexto ausente.
- Unidad A (auth-first): 401. Unidad B (membership-first): 403 `SUBJECT_ENROLLMENT_DROPPED` / `RESOURCE_SUBJECT_MISMATCH` / `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`.
- Divergencia observable: mismo estado obtiene 401 vs 403; el catálogo y la reintentabilidad aparente divergen aunque ambos códigos sean no-reintentables.
- Obediencia literal: ambas cumplen «token inválido/vencido → 401; sin contexto/membresía/mismatch → 403» y «post-revocación → 403».
- No cubierto: D-07 unificó solo el caso puro post-revocación; el orden de chequeo concurrente no está definido.

### N-10 — Resolución `userId`: orden, espacios internos, CODE. AD: AD-08, AD-09 §0.
- Unidad A intenta parse UUID primero; Unidad B busca `institutional_id` primero. Ante `"TA-SOFIA-01 "`, `" <uuid>\n"`, `"AB CD"`, o `institutional_id` con forma UUID, A responde `UNKNOWN_IDENTITY` 404, B responde `MALFORMED_*`/404 distinto o resuelve distinto principal.
- Unidad A trata cualquier whitespace (incluido interno/`\n`/`\t`) como «espacios externos»; Unidad B solo los extremos literales.
- Divergencia observable: mismo `user_id` obtiene identidades distintas o CODEs distintos (404 vs 400) sin violar «formato estándar exigido, sin recorte».
- Obediencia literal: ambas cumplen «UUID estándar exigido; espacios externos rechazados sin recorte; `institutional_id` case-sensitive».
- No cubierto: D-08 cerró solo extremos-literales; O-05 dejó solo case UUID; orden de resolución y blancos internos/control no están definidos.

### N-11 — Reingesta concurrente con doble `batch_id`. AD: AD-02, AD-12.
- Dos ingestas válidas concurrentes del mismo contenido: ambas generan `batch_id = roster-<8hex>-<term>` distinto (32 bits → colisión posible) y compiten en `BEGIN IMMEDIATE`.
- Unidad A cuenta `created_identities`/`updated_memberships` por orden de commit; Unidad B por orden de validación; ante colisión de 8hex, A asume unicidad y B falla/colisiona.
- Unidad A regenera credenciales `uai_live_…` y Unidad B reutiliza (eje O-05), pero incluso fijado ese eje, los conteos y el `batch_id` ganador divergen.
- Divergencia observable: mismo par de peticiones produce pares de 201 con conteos cruzados distintos; `IdGenerator` hipotético compartido vs por-adapter diverge.
- Obediencia literal: ambas cumplen «sin idempotencia; intento nuevo con `batch_id` nuevo; reglas normales de identidad/membresía/unicidad; `BEGIN IMMEDIATE` serializa».
- No cubierto: D-05 cerró no-idempotencia; colisión, orden de conteo y dueño del generador no están definidos.

### N-12 — Header vs path `subject_id` en revoke/ingest. AD: AD-01, AD-09.
- `POST /api/v1/subjects/CS101/enrollments/X/drop` con `X-Academic-Subject-Context: CS-480` (o ausente).
- Unidad A exige igualdad header==path==ARN-subject (extiende AD-01 a las tres ops). Unidad B ignora el header fuera de authorize (literal: header obligatorio solo en `POST /api/v1/authorize`) y ejecuta sobre el path.
- Divergencia observable: misma petición obtiene 403 `RESOURCE_SUBJECT_MISMATCH` vs 200 `REVOKED`/`ALREADY_REVOKED`; ingesta obtiene 201 en curso distinto al del contexto.
- Obediencia literal: ambas cumplen «comparación cruda byte-a-byte header vs subject del ARN» (authorize) y el mapeo único §0; el rol del header en revoke/ingest no está definido.
- No cubierto: D-02/AD-01 no ligan header a path.

### N-13 — Case no normado: dominio de email + `seen_ids`. AD: AD-02, AD-09 §0.
- `juan@UNIVERSIDAD.EDU` vs `juan@universidad.edu`: Unidad A acepta (dominio case-insensitive), Unidad B rechaza 422 `ROSTER_VALIDATION_FAILED` (exacto).
- `seen_ids` con `STU-1` vs `stu-1` en el mismo lote: Unidad A deduplica case-insensitive (`INTRA_BATCH_DUPLICATE_ID` 422), Unidad B las trata distintas (pasan a anti-role-smuggling/unicidad).
- Divergencia observable: mismo lote obtiene 201 vs 422 con `row_number` distintos.
- Obediencia literal: ambas cumplen «`institutional_id` y `term` case-sensitive exacto» (alcance declarado solo a esos campos) + «`email` en `@universidad.edu`» + «`seen_ids`»; la extensión a dominio y a plegado en `seen_ids` no está definida.
- No cubierto: la decisión de case declara alcance limitado; este matiz queda fuera.

### N-14 — Límites y conteos: 5 MB, 400 vs 413, `drop_reason`. AD: AD-02, catálogo, AD-03.
- Lote que viola ambas (>1000 filas y >5 MB): Unidad A retorna `BATCH_TOO_LARGE` 413, Unidad B `MALFORMED_BATCH` 400 (orden de chequeo). 5 MB como 5·1024·1024 vs 5·1000·1000 cambia el veredicto en el borde.
- `drop_reason` de 280 emojis: Unidad A cuenta `len()` caracteres (200 OK), Unidad B bytes UTF-8 (400 `MALFORMED_DROP_REASON`); normalización NFC/NFD no definida.
- Divergencia observable: mismo cuerpo obtiene 400 vs 413, o 200 vs 400.
- Obediencia literal: ambas cumplen «1–1000 filas, ≤5 MB, UTF-8, columnas exactas» y «`drop_reason` 1–280 caracteres».
- No cubierto: unidad de MB, orden de códigos y unidad de conteo no están definidos.

### N-15 — Replay vs validación; alcance de `ExplanationDTO`. AD: AD-03, AD-12, AD-11.
- Segunda baja sobre `DROPPED` con `drop_reason` malformado (vacío/>280): Unidad A ataja a 200 `ALREADY_REVOKED` con `revocation_propagated_at` original sin validar; Unidad B valida P3 primero → 400.
- 401/404/400 (`INVALID_AT`, `UNKNOWN_IDENTITY`, `MALFORMED_TERM`): Unidad A les adjunta `ExplanationDTO` con algún AD-n; Unidad B solo la porta en `ALLOW`/`DENY` y rechazo lote/baja. El `reason_code` de auth (sin AD propio, solo PRD §5.2) y la cita obligatoria divergen.
- Divergencia observable: misma repetición obtiene 200 vs 400; mismos errores obtienen formas con/sin `explanation` y `rule_ids` distintos, ambos «no vacíos».
- Obediencia literal: ambas cumplen «rama `DROPPED → ALREADY_REVOKED` sin mutación ni evento», «P3 1–280» y «todo `ALLOW`/`DENY` y rechazo porta `ExplanationDTO` con `rule_ids` no vacío y código del catálogo».
- No cubierto: orden replay-vs-validación y alcance a 401/404/400 no están definidos.

### N-16 — Serialización física: `BEGIN IMMEDIATE` vs predicado; `busy_timeout`; orden micro-batching. AD: AD-03, AD-12, AD-04.3.
- Unidad A implementa revokes/ingestas con predicado condicional en una sentencia; Unidad B con `BEGIN IMMEDIATE` + sentencias. Ante `SQLITE_BUSY`, A retorna 503 de inmediato y B espera `busy_timeout 5000` (¿aplica a ingest o solo a revoke AD-03?).
- Orden de encadenado bajo concurrencia: A encadena por orden de encolado, B por orden de flush/commit (50 ms o 50 eventos, worker secuencial); `id ASC` resultante difiere.
- Divergencia observable: misma ráfaga obtiene mezclas distintas de 200/201/503 y latencias (<200 ms vs espera); el `prev` del ledger difiere aunque cada historia pase su propio `test_ledger_chain_and_anchor`.
- Obediencia literal: ambas usan medios permitidos («predicado en una sola sentencia o `BEGIN IMMEDIATE`; prohibido leer-luego-actualizar»; «`workers: 1`, `busy_timeout 5000`»; «flush cada 50 ms o 50 eventos, worker secuencial»).
- No cubierto: la disyunción deja dos físicas no equivalentes; el alcance de `busy_timeout` y el orden de encadenado no están definidos.

## Conteo y escala

- CUBIERTOS: 14 (D-01..D-08 + O-01..O-06). No computan como huecos.
- NUEVOS: 16 (N-01..N-16). Cada uno admite dos unidades un nivel abajo que obedecen al pie de la letra las decisiones cerradas y los OPENs y aun así divergen en HTTP, estado o ledger.
- Escala: **NO ROBUSTO (16 pares)**.

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; ningún OPEN fue cerrado; ninguna edición fue propuesta.*
