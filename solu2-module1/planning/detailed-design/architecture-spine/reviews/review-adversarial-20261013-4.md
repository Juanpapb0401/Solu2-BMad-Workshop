# Revisión adversarial — Reviewer Gate bmad-architecture (2026-10-13, vuelta 4)

- Fecha: 2026-10-13
- Rol: revisor adversarial, solo lectura salvo este archivo de reporte. No se modifica ningún otro archivo, no se cambia el criterio, no se oculta ningún hallazgo, no se propone ninguna edición, no se cierra ningún OPEN ni pendiente.
- Alcance: `solu2-module1` — `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)` + `EDGE-01 Multi-Subject Permission Resolution` + Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»).
- Fuentes leídas (solo lectura):
  1. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (136 líneas, `updated: 2026-10-13`).
  2. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/contracts.md` (170 líneas).
  3. Ruta pedida `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/resultados-interaccion.md` — no existe en esa ruta; se leyó el archivo existente `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md` (5 líneas). Se deja constancia sin alterar el criterio.
- Versión evaluada: reglas R1–R11 `[ADOPTED]` plasmadas en spine/contracts (endpoint sin `at` + `request_now` único; orden 7 pasos; matriz temporal fail-closed; `term` siempre-`MALFORMED_TERM`; codec frames + `QueueReservation` + P1–P4 sin eventos; roster `batch_id`-manifiesto-precedencia-conteos; scheduler condicional dueño único; UUID canónico; límites exactos; replay+DTO; `BEGIN IMMEDIATE` + `busy_timeout`; WAL reads; prioridad/precedencia de curso). La vuelta 3 (H-01..H-13) queda contenida por R1–R11 en su forma básica y no se reclama como nueva.
- Pendientes declarados asumidos sin cerrar (no computan como huecos nuevos si el par los describe exactamente): matriz `roles_matrix.json`; capacidad de cola; recuperación post-aceptación; frecuencia scheduler + crash; ubicación HTTP del `timestamp` de baja; `COMPLETED`; TTL `uai_live_…`; NFR (datasets, p95/p99, 1000 filas, 120 filas, revocación); reemisión/regeneración de credenciales; colisión `batch_id` 8hex.

## Método

Adversario un nivel abajo: por cada AD se construyen dos unidades hipotéticas que obedecen el texto vigente del AD al pie de la letra (incluidas R1–R11) y aun así divergen en HTTP observable, estado persistido, ledger o latencia. Cada divergencia es un par = un hueco.

- `CUBIERTO`: el par ataca exactamente el punto ya contenido por R1–R11 o describe exactamente un pendiente declarado. No computa como hueco nuevo.
- `NUEVO` (serie `H-14..H-26`): ambas unidades obedecen las decisiones cerradas y los pendientes vigentes y aun así divergen en un matiz no documentado en spine/contracts. Es hueco.
- Escala: `ROBUSTO` = 0 pares `NUEVO`; `NO ROBUSTO` = N pares `NUEVO` (N>0).

## Veredicto

**NO ROBUSTO (13 pares NUEVOS).**

## Resumen

| ID | Foco | AD | Estado |
| --- | --- | --- | --- |
| R-básica | R1–R11 forma básica (codec lista, sin-`at`, orden 7, term-400, P1–P4, batch/manifiesto/precedencia/conteos, scheduler, UUID, límites, replay/DTO, BEGIN/timeout, WAL, auth) | AD-01..AD-13 | CUBIERTO por decisión |
| O-matriz | Matriz rol×acción ausente | AD-01, AD-11 | CUBIERTO por OPEN |
| O-cola | Capacidad máxima + recuperación post-aceptación | AD-04, AD-12 | CUBIERTO por OPEN |
| O-sched | Frecuencia numérica + crash transición→evento | AD-13 | CUBIERTO por OPEN |
| O-ts | Ubicación HTTP `timestamp` baja | AD-03 | CUBIERTO por OPEN |
| O-varios | `COMPLETED`, TTL, NFR, reemisión, colisión `batch_id` | AD-02, AD-03, AD-09 | CUBIERTO por OPENs |
| H-14 | Codec: alcance del hash + enteros | AD-04 (heredado) | NUEVO |
| H-15 | Codec: prev génesis + unidad de longitud no-ASCII | AD-04 (heredado) | NUEVO |
| H-16 | `request_now`: momento de captura + segundo tx | AD-09, AD-13 (spine-local) | NUEVO |
| H-17 | `IDENTITY_BARRED` vs `RESOURCE_SUBJECT_MISMATCH` | AD-01 (heredado), AD-09, AD-11 | NUEVO |
| H-18 | Transporte: percent-encoding de `term` + sintaxis del path | AD-09 (spine-local) | NUEVO |
| H-19 | `drop_reason`: blancos extendidos + secreto vs intacto | AD-03 (heredado), AD-06 (heredado) | NUEVO |
| H-20 | Smuggling sobre membresía `DROPPED` | AD-02 (heredado) | NUEVO |
| H-21 | Tiempo: histórico-vs-persistido + ticket futuro + intervalo vacío | AD-13 (spine-local), AD-05 (heredado) | NUEVO |
| H-22 | Lector WAL en ventana <200 ms | AD-03 (heredado), AD-12 (spine-local) | NUEVO |
| H-23 | Explicación multi-causa: cardinalidad | AD-11 (spine-local) | NUEVO |
| H-24 | Header: multiplicidad + vacío + CRLF | AD-01 (heredado), AD-09 | NUEVO |
| H-25 | Pureza: azar fuera de `random` | AD-08 (spine-local) | NUEVO |
| H-26 | `effective_role`: case del rol | AD-10 (spine-local) | NUEVO |

## A. Pares CUBIERTOS por decisiones/pendientes (no son huecos nuevos)

- **R-básica.** Unidad A usaba variantes pre-R (p. ej. `at` en body público, `term` con elección de valor, codec sin frames, reingesta con deduplicación, scheduler perezoso, UUID con `strip`/`upper`, límites en otras unidades, replay tras P3, lectura-then-update, DENY en 200); Unidad B aplica R1–R11 (sin `at` + `request_now`, orden 7, `MALFORMED_TERM` siempre, frames `0x00`/`0x01`+len8BE+UTF-8 con `Z`/`prev` minúsculas/FIFO-`id ASC` + `QueueReservation`, P1–P4 sin evento, `batch_id roster-<8hex>-<term>` + manifiesto por (fila,campo) + precedencia + conteos efectivos, scheduler condicional dueño único, UUID `8-4-4-4-12` + case-sensitive exacto, 5.000.000 B / 1000 filas / 1–280 Unicode, replay-antes-de-P3 + `ExplanationDTO`/`ErrorBody`, `BEGIN IMMEDIATE` + `busy_timeout 5000`, WAL sin `BEGIN`, 401-primero + 403 unificado, ALLOW→200 / DENY→403). Contención: spine §§AD-08..AD-13 + conventions + contracts §§0–5. Se registra para distinguir de H-14..H-26 (bordes intra-R).
- **O-matriz.** Denegar lo no listado vs heredar grueso; ambas obedecen la regla temporal fail-closed sin `roles_matrix.json`. Declarado en contracts §6 + spine. No es hueco nuevo.
- **O-cola.** Acotar vs no acotar; reintento vs bloqueo tras aceptación. Capacidad y recuperación declaradas pendientes TEA/NFR. No es hueco nuevo; se distingue de H-22 (lector pre-aceptación).
- **O-sched.** Barrido 1 s vs 60 s; re-emitir vs suprimir tras crash transición→evento. Frecuencia y crash declarados pendientes. No es hueco nuevo; se distingue de H-21 (propiedad de evaluación, no el número ni el protocolo de crash).
- **O-ts.** `timestamp` de baja en body vs vía `Clock`; firma Annex A sin cambiar. Ubicación declarada abierta. No es hueco nuevo.
- **O-varios.** `COMPLETED`, TTL `uai_live_…`/`EXPIRED`, datasets/concurrencia NFR, reemisión en reingesta, colisión 8hex. Declarados en contracts §6 y spine Deferred. No son huecos nuevos; se distinguen de H-20/H-23 (scope de `DROPPED` y cubetas, no los valores pendientes en sí).

## B. Pares NUEVOS (huecos; ambas unidades obedecen R1–R11 y OPENs vigentes)

### H-14 — Codec: alcance del hash y codificación de enteros. AD: AD-04 (heredado).
- Unidad A: hashea solo los 8 campos de la fórmula §5 (`prev || timestamp || actor_id || subject_id || resource_arn || action || decision || reason_code`); los enteros de conteo (`processed`, `created_identities`, `updated_memberships`) se enmarcan como string decimal UTF-8 (`0x01`+len+`"12"`).
- Unidad B: hashea todas las columnas persistidas del evento (`eventId`, `batch_id`, conteos, etc.) en orden de esquema; los enteros se enmarcan como binario de 8 bytes big-endian.
- Divergencia observable: mismo `roster:ingest`/`roster.rejected` produce `record_hash` distintos; cada verificación intra-unidad pasa y la cruzada rompe; exportación/auditoría no portable.
- Obediencia literal: ambas usan la lista §5, frames `0x00`/`0x01`+len8BE+UTF-8, orden, SHA-256, `Z`, `prev` minúsculas, nulls explícitos, FIFO/`id ASC`. El alcance (solo-fórmula vs fila completa) y el tipo entero no están definidos; el codec solo nombra `null` y `string`.
- No cubierto: R fijó lista y familia de frames, no el alcance ni los no-string.

### H-15 — Codec: prev génesis y unidad de longitud no-ASCII. AD: AD-04 (heredado).
- Unidad A: primer evento (sin previo) usa `prev = 0x00` (null); longitud del frame = bytes UTF-8.
- Unidad B: primer evento usa 64 ceros hex (`"00…00"`, string); longitud = puntos de código Unicode.
- Divergencia observable: el evento génesis y cualquier evento con no-ASCII (p. ej. `full_name` con `é`/`ñ`, `drop_reason` con emoji) hashean distinto entre unidades aunque la lista §5 sea idéntica.
- Obediencia literal: ambas cumplen `prev` hexadecimal en minúscula, nulls con codificación explícita única, `longitud UTF-8 de 8 bytes big-endian + bytes UTF-8`. Génesis (ausencia de previo) y unidad (bytes vs caracteres) no están definidas.
- No cubierto: R fijó `Z`/`prev` minúsculas/nulls, no la génesis ni la unidad.

### H-16 — `request_now`: momento de captura y segundo evento. AD: AD-09, AD-13 (spine-local).
- Unidad A: captura al entrar al adapter (pre-auth) y el evento `roster.rejected` de la tx separada reutiliza ese mismo `request_now` como `occurredAt`.
- Unidad B: captura tras pasar auth y el `roster.rejected` captura un `now` fresco para su propia tx.
- Divergencia observable: con auth lenta o en el borde `expires_at`, el mismo `authorize` da ALLOW (A) vs DENY (B); el mismo rechazo 422 porta `occurredAt`/hash distintos.
- Obediencia literal: ambas capturan una sola vez por solicitud, usan `Clock`, evalúan en vivo con `request_now`, emiten `roster.rejected` en tx separada dentro de la misma cadena tras aceptación. El momento intra-pipeline y el reuse en la segunda tx no están definidos.
- No cubierto: R fijó unicidad, no el momento ni el reuse.

### H-17 — Global barred vs mismatch (ambos 403, distinto CODE). AD: AD-01 (heredado), AD-09, AD-11.
- Petición con identidad global `SUSPENDED`/`EXPELLED` y a la vez mismatch header-vs-ARN.
- Unidad A: `403 RESOURCE_SUBJECT_MISMATCH`. Unidad B: `403 IDENTITY_BARRED`.
- Divergencia observable: mismo input, mismo HTTP, distinto `code`/`detail`, distinta `ExplanationDTO` (`observed_context`/`observed_resource_subject` vs `status`) y distinto `reason_code` en ledger.
- Obediencia literal: P5 ordena barred antes de la membresía; el orden de 7 pasos ordena mismatch (paso 5) antes de membresía (paso 6). El orden relativo barred-vs-mismatch no está definido.
- No cubierto: el orden 7 fija mismatch-vs-membresía, no barred-vs-mismatch; la matriz pendiente es otro eje.

### H-18 — Transporte: percent-encoding y sintaxis del path. AD: AD-09 (spine-local).
- (a) `POST …/roster?term=2026-%46ALL` (`%46` = `F`): Unidad A decodifica y acepta (201); Unidad B compara crudo y responde `400 MALFORMED_TERM`.
- (b) `POST …/subjects/CS/101/enrollments/…/drop` o `…/subjects/CS101./…`: Unidad A responde 400 de sintaxis; Unidad B responde `404 UNKNOWN_COURSE` (sin códigos nuevos).
- Obediencia literal: `term`/`institutional_id` case-sensitive exactos sin conversión; `term` solo en su canal; path param canónico; sin `strip`; sin códigos nuevos. Decodificación porcentual y gramática del path no están definidas.
- No cubierto: R fijó canales, `MALFORMED_TERM` siempre y límites, no percent ni path.

### H-19 — `drop_reason`: alcance de blancos y secreto vs intacto. AD: AD-03 (heredado), AD-06 (heredado).
- (a) `" \t\n "`: Unidad A lo acepta (200, cuenta 4/280; solo U+0020 es «espacio»); Unidad B lo rechaza (`400 MALFORMED_DROP_REASON`, todo-blanco efectivo).
- (b) razón que pega un secreto (`"revoco por uai_live_abcd1234efgh"`): Unidad A la conserva intacta en 200/ledger (pasa «original intacto», rompe el regex); Unidad B la enmascara (`uai_live_<4>••••<4>`, pasa AD-06, rompe «intacto»).
- Obediencia literal: 1–280 puntos Unicode (no bytes/graphemes), solo-espacios inválida, original intacto sin normalizar; AD-06 cero secretos con regex de build. Alcance de «espacios» y colisión intacto-vs-máscara no están definidos.
- No cubierto: R fijó unidad y rango, no el charset de blancos ni la colisión.

### H-20 — Anti-smuggling sobre membresía `DROPPED`. AD: AD-02 (heredado).
- Lote cuyo `institutional_id` ya tiene membresía `DROPPED` en el curso con rol distinto al entrante.
- Unidad A: rechaza el lote (toda membresía previa cuenta). Unidad B: acepta y reactiva en `ACTIVE` con el rol nuevo (solo `ACTIVE` cuenta como preexistente).
- Divergencia observable: mismo lote da 422 con manifiesto vs 201 con conteos; roles persistidos distintos.
- Obediencia literal: rol entrante divergente sobre membresía existente se rechaza; `seen_ids` exacto; `assigned_role` sin case-folding. El scope de «membresía existente» (`ACTIVE` vs cualquier estado) no está definido.
- No cubierto: `COMPLETED` pendiente es otro estado; precedencia/conteos R no fijan este scope.

### H-21 — Evaluación temporal: histórico-vs-persistido, futuro y vacío. AD: AD-13 (spine-local), AD-05 (heredado).
- (a) Scheduler ya persistió `EXPIRED`; replay interno pide `at` histórico vigente: Unidad A retorna escalado (manda el `at`); Unidad B retorna base/DENY (manda lo persistido).
- (b) Ticket `ACTIVE` con `granted_at` futuro, `at`=ahora: Unidad A retorna base; Unidad B retorna escalado (distinto `effective_role` en el 200).
- (c) `granted_at == expires_at`: Unidad A DENY (`at>=expires`); Unidad B escalado instantáneo (`granted<=at`).
- Obediencia literal: intervalo `[granted_at, expires_at)`; `resolve` no muta y evalúa el `at` pedido incluso histórico; scheduler con reloj propio y guarda `ACTIVE ∧ granted<=now ∧ expires<=now` (`granted>now` aún no expira); máx. un evento por transición. La dirección persistido→histórico, el futuro y el vacío no están definidos (R solo fija la dirección no-persistido→`at`).
- No cubierto: frecuencia/crash pendientes son número y protocolo, no esta propiedad.

### H-22 — Lector WAL en la ventana <200 ms. AD: AD-03 (heredado), AD-12 (spine-local).
- `authorize` concurrente con `revoke`/`ingest` comprometido pero con `revoked_credentials_cache` aún no propagado.
- Unidad A: exige `caché == DB`; si no confirma, responde `503`.
- Unidad B: responde con la caché aunque la DB esté ocupada (veredicto con snapshot previo/stale).
- Divergencia observable: misma ráfaga da 503 (A) vs 200/403 (B) para el mismo `authorize`; p95/p99 divergen aunque el CODE de mutantes coincida.
- Obediencia literal: lecturas WAL sin `BEGIN IMMEDIATE`; caché + vista coherente; sin confirmar → 503; mutantes con `BEGIN IMMEDIATE`; `busy_timeout 5000` → 503 sin commit parcial. «Coherente»/«confirmar» no están definidos.
- No cubierto: capacidad/recuperación pendientes son post-aceptación, no el lector.

### H-23 — Explicación multi-causa. AD: AD-11 (spine-local).
- Lote con fila a la vez con campo inválido, duplicada en `seen_ids` e identidad `SUSPENDED`.
- CODE principal fijo por precedencia; `rule_ids`: Unidad A solo el principal; Unidad B todos los violados. Campos observados: Unidad A solo los listados de Q4; Unidad B añade extras.
- Divergencia observable: mismo 422 con `code` igual pero `ExplanationDTO` incompatible (`rule_ids` de longitud 1 vs N; observados distintos).
- Obediencia literal: `rule_ids` no vacío con AD-n, observados y umbral; catálogo cerrado. La cardinalidad (exhaustiva vs mínima) no está definida.
- No cubierto: la precedencia R fija el CODE, no la explicación.

### H-24 — Header: multiplicidad, vacío y framing. AD: AD-01 (heredado), AD-09.
- (a) `X-Academic-Subject-Context` repetido (`CS101` + `CS-480`): Unidad A toma el primero; Unidad B el último (o el join con coma). (b) Header presente vacío `""`: Unidad A paso 3 ausente (`SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`); Unidad B mismatch/unknown. (c) `"CS101\r\n"`: Unidad A incluye el framing (mismatch→DENY); Unidad B lo descuenta como transporte (match→ALLOW).
- Obediencia literal: header obligatorio solo en `/authorize`; comparación cruda byte-a-byte sin `strip`/`upper`/normalización. Multiplicidad, vacío-vs-ausente y nivel (app vs wire) no están definidos.
- No cubierto: el contexto-por-path R no fija el intra-`authorize`.

### H-25 — Pureza: azar fuera de `random`. AD: AD-08 (spine-local).
- Código bajo `domain/` que usa `uuid.uuid4()`, `os.urandom()` o `time.monotonic()` sin importar `fastapi`/`sqlalchemy` ni llamar `datetime.now`/`random`.
- Unidad A lo acepta (la lista prohíbe esos cinco literales; tiempo/azar «entran por `Clock`/`IdGenerator» se lee como esos módulos). Unidad B lo rechaza (todo azar por `IdGenerator`, todo tiempo por `Clock`).
- Divergencia observable: el mismo `domain/` pasa el lint en A y falla en B; los tests con fake-clock/`IdGenerator` son deterministas en B y no en A.
- Obediencia literal: ambas cumplen la lista de imports y los puertos. El alcance de «azar» (módulo `random` vs toda no-determinación) y de «reloj» (`datetime.now` vs `time.monotonic`) no está definido.
- No cubierto: ningún R fija este alcance.

### H-26 — `effective_role`: case del rol. AD: AD-10 (spine-local).
- Unidad A retorna el rol tal como está almacenado (`"TA"`); Unidad B lo normaliza a minúsculas (`"ta"`, simétrico con `assigned_role ∈ {student, ta}` del roster).
- Divergencia observable: mismo 200 `AuthorizeResponse` con `decision` igual pero `effective_role` byte-distinto; clientes que comparan exacto divergen; el fixture dual pasa en ambas por separado y cruza distinto.
- Obediencia literal: rol base del par o escalado; sin cuota GPU ni prioridad; aislamiento por tupla; docs en español con IDs en inglés. Ninguna regla fija el case del rol (las decisiones case-sensitive cubren `institutional_id`/`term`/`seen_ids`/`courseId`, no el rol).
- No cubierto: el tercer curso pendiente es otro eje (cobertura del fixture), no el case.

## Conteo y escala

- CUBIERTOS: R-básica + 5 grupos OPEN. No computan como huecos.
- NUEVOS: 13 (H-14..H-26). Cada uno admite dos unidades un nivel abajo que obedecen al pie de la letra R1–R11 y los pendientes vigentes y aun así divergen en HTTP, estado, ledger o latencia.
- Escala: **NO ROBUSTO (13 pares)**.

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; ningún OPEN fue cerrado; ninguna edición fue propuesta.*
