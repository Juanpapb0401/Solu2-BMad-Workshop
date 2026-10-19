# decision-log-solu2.md — Registro de decisiones del Módulo 1 (Solu-2)

Paquete `.work/paquete-decisiones-F-H.md` APROBADO por el estudiante el 2026-10-13, en bloque y sin modificaciones.
Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.
Origen de los hallazgos: `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-4.md` (F-xx) y `review-adversarial-20261013-4.md` (H-xx).
Alcance: solo las tres operaciones (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`). Sin lógica productiva.
AD-01..AD-07 de `planning/ARCHITECTURE.md` son autoridad read-only; ninguna decisión los debilita (ver § Conflictos: 0 bloqueantes, 1 tensión registrada para triage).


## Resumen en formato de la consigna

Partner: **A — Juan Pablo Parra** (Architect-lead: decisiones de arquitectura y contratos) · **B — Daniel Gonzalez** (Test-lead: decisiones TEA/NFR). A y B revisaron juntos todas las decisiones de este log y las aprobaron el 2026-10-14; la columna Partner indica el responsable por rol. Cada fila resume un registro de este log; el detalle está en la sección citada.

| Phase | Persona/Skill | Prompt (resumen) | AI output (resumen) | Human decision | Reason | Artifact changed | Partner |
|---|---|---|---|---|---|---|---|
| 0 Intake | Winston (bmad-architecture) | Confirmar alcance: operaciones del Annex A (p. 13) y stack heredado | Tres operaciones candidatas y stack Plan-2 (Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite WAL) | ACCEPT | El Annex A trae las tres candidatas; el stack de Plan-2 es fuente que manda (AGENTS.md) | `architecture-spine/.memlog.md` (decisión 2026-10-12) | A (2026-10-12) |
| 1 Contratos | bmad-architecture, Reviewer Gate, lente rubric (F-02) | Matriz rol×acción sin contenido, dos builders no convergen | Inventar permisos para cerrar la matriz, o v0 solo con filas citables | ACCEPT (opción B) | Dos implementaciones convergen sin inventar permisos; lo no citado se niega (`403 UNAUTHORIZED_RESOURCE_CLASS`) | `schemas/roles_matrix.v0.json` | A |
| 1 Contratos | bmad-architecture, Reviewer Gate, lente adversarial (H-14) | Hash de la fila completa con binario nativo (opción A) | REJECT de la opción A: el hash cubre solo los 8 campos de AD-04 §5. Texto final: "Entero futuro: string decimal UTF-8"; ningún conteo, `batch_id` ni `eventId` entra | REJECT (de la opción A) | AD-04 heredado define la fórmula; ampliar el alcance cambiaría un AD heredado, que es read-only | `contracts.md` §5, `schemas/events.md` §3 | A |
| 1 Contratos | bmad-architecture, lente adversarial (H-26 / ADVF-10) | Normalizar casing de `courseId`, `effective_role` e `institutional_id` (propuesta IA) | REJECT de la normalización. Texto final: comparación byte a byte; `cs-480` → `404 UNKNOWN_COURSE` (R9-03). `effective_role` = `roles.id` exacto del DDL | REJECT | Normalizar en silencio une identidades distintas y oculta la diferencia; `institutional_id` y `term` quedan case-sensitive exactos por decisión del estudiante | `contracts.md` §0, `epics.md` E4-S3 (ADVF-10) | A |
| 1 Gate 4-5 | bmad-architecture, Reviewer Gate (veredicto "NO PASS por diseño") | Cerrar el gate con F-01..F-06 y H-14..H-26 abiertos | MODIFY: los hallazgos se triagean en un paquete de decisiones humanas (rondas 1-7) y no quedan como OPEN implícito | MODIFY | El reviewer no puede decidir matriz completa, TTL de `uai_live_` ni capacidad de cola (DEFERRED); esas decisiones son del equipo | `.work/paquete-decisiones-F-H.md`; `validation-gate-20261013-5.md` | A |
| 2 Diseño | Edge-case hunter (ECF-28) | Persistir `roster.rejected` de forma síncrona antes del 422 | REJECT. Texto final: el rechazo se persiste tras aceptación en cola (`roster.rejected` posterior) | REJECT | Contradice AD-04.3 heredado (respuesta tras aceptación en cola); la recuperación post-aceptación queda DEFER a Fase 3 | `reviews/review-detailed-design.md:133`; `contracts.md` §3 | B |
| 2 Diseño | bmad-architecture, Reviewer Gate, lente adversarial (G9-05, baja) | Hallazgo: mismo nombre `rule_ids` en `ErrorBody` y `ExplanationDTO` | REJECT: se conserva el nombre en ambos DTO; el contenido difiere (códigos del catálogo vs citas AD-n) y es intencional | REJECT | Mismo significado de lista ordenada de reglas; renombrar oculta que el contenido es distinto | `contracts.md` (ErrorBody, ExplanationDTO), `dto.py` | A |
| 2 Diseño | Revisor de seguridad (SEC B-02) | Ocultar códigos 404/403 diferenciados y `observed_*` contra enumeración | REJECT de la mitigación. Riesgo residual aceptado; mitigación vigente: 401 primero (R9-00) y `observed_*` solo del contexto pedido | REJECT (riesgo residual aceptado) | PRD y catálogo exigen códigos distintos; AD-11 exige explicabilidad con valores observados (restricción 4 de Plan-2) | `epics.md` (filas SEC); R12-B02 | A |
| 3 ATDD | bmad-testarch-atdd (skill BMad, subagente Claude Haiku 5.5, orquestado por Claude Opus 5.5) | Pasada gap-fill: `Module1Service._actor()` delega en `TokenVerifierPort`; 3 tests 401 pasan a verde | REJECT. Texto final: `_actor()` lanza `NotImplementedError("Module1Service._actor: verificación de token pendiente (AD-09)")` y los 3 tests son atdd-red | REJECT | El verificador en tests es un fake configurado por el propio test, es tautología (consigna: −5 c/u) y verificar el bearer es lógica de GREEN | `test/atdd/` (T-RES-12, T-REV-11, T-ROS-20); R9-00 | A; B (TEA) |
| 3 TEA/NFR | bmad-testarch-nfr | Plan de evidencia de los 7 NFR de `prd.md` §6 | Plan con todos los NFR en `PLANNED`; capacidad de cola y recuperación post-aceptación DEFER a Fase 3 NFR | DEFER (cola) / ACCEPT (resto) | No se marca EVIDENCED sin una corrida medible real (AGENTS.md); no hay implementación ni medición | `test/nfr-evidence.md` (fila DEFERRED-Cola) | B |
| 4 Readiness | bmad-check-implementation-readiness, corrida 1 (M-2) | Semilla génesis = 64 ceros (propuesta previa de la IA, H-15) | REJECT. Texto final: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (`planning/ARCHITECTURE.md` l.97) | REJECT | Los 64 ceros eran placeholder del DDL, no decisión de Plan-2; AD-04 §5 no fija el valor y la constante de Plan-2 cierra la tensión sin debilitar ningún invariante | `schemas/001_module1_schema.sql`, `events.md` §3, `ports-and-adapters.md` §4, `contracts.md` §3 Q3 y §5 | A (R10-M2) |
| 4 Readiness | bmad-check-implementation-readiness, corrida 1 (M-1) | Estado Loading de ingesta con "N / 120 (P%)" por fila desde el backend | MODIFY. Texto final: progreso de subida calculado en el cliente y "Validando lote atómico..." hasta la respuesta | MODIFY | AD-02 es invariante heredado (ingesta síncrona y atómica); 120 filas tardan < 2.0 s, así que el progreso por fila no aporta valor y no tiene fuente | `contracts.md` §6 (R10-M1) | A (Ronda 10) |

## Herramientas, modelos y gobernanza

- **Fases 0–2 y CI/NFR:** ejecutados con OpenCode (modelo por defecto `muse-spark-1.3-contributor-free`) corriendo los slash commands BMad.
- **Desde ATDD:** los mismos skills BMad (`.agents/skills/bmad-*/SKILL.md`) fueron ejecutados por subagentes Claude Haiku 5.5, orquestados por Claude Opus 5.5, por decisión del estudiante (2026-10-13) tras cuelgues del modelo gratuito.
- **Propuestas y decisiones:** las propuestas las redactó la IA (skills BMad + Claude). La decisión final de cada registro es humana: A y B revisaron juntos todas las propuestas y las aprobaron, modificaron o rechazaron el 2026-10-14.
- **Scripts:** el orquestador (Claude Opus 5.5) escribió `.work/regen_ad_table.py` para regenerar la tabla AD desde los bindings (K-6) e hizo correcciones de texto puntuales registradas (Rondas 11 y 13, K-13..K-22).
- **Excepción de sincronización:** la UX de la copia del workshop se sincronizó mediante un hallazgo triageado (K-4); la excepción está registrada en `AGENTS.md`.
- **Evidencia:** los prompts y logs de ejecución se conservan localmente por el equipo (no se publican en el repositorio). En el repositorio quedan las rondas de decisión (`.work/paquete-decisiones-F-H.md`) y la evidencia del Gate Drill (`.work/gate-drill/`).
- **Sign-off:** A y B firmaron el veredicto READY y el Gate Drill el 2026-10-14 (`planning/readiness-gate-report.md`, sección Sign-off).

## F-01 — Revocación repetida sobre `DROPPED` (orden universal)

- Hallazgo origen: `review-rubric-20261013-4.md` F-01 (orden universal vs orden replay: mismo input `DROPPED` + `drop_reason` inválido daba 200 en una regla y 400 en otra).
- Opción A: replay antes de sintaxis (replay `DROPPED → ALREADY_REVOKED` sin validar `drop_reason`).
- Opción B: orden universal (sintaxis P3 primero).
- Decisión: B. Se respeta el orden universal: autenticación → sintaxis P3 (`drop_reason`) → identidad/curso → estado `DROPPED`. `drop_reason` inválido → `400 MALFORMED_DROP_REASON` aunque la membresía esté `DROPPED`; solo una petición válida sobre `DROPPED` retorna `200 ALREADY_REVOKED`.
- Razón: un solo orden para todas las operaciones; un reintento legítimo siempre trae el mismo payload válido, así que la idempotencia no se pierde.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## F-02 — Matriz rol×acción v0 como dato citado

- Hallazgo origen: `review-rubric-20261013-4.md` F-02 (matriz sin contenido: dos builders no convergen en ALLOW/DENY por acción).
- Opción A: inventar permisos para cerrar la matriz.
- Opción B: v0 solo con filas citables al PRD + fail-closed para lo no citado, como dato versionado.
- Decisión: B. `schemas/roles_matrix.v0.json` con filas citadas (CS101 Student sin GPU solo CPU juguete — prd.md:244; CS-480 Student inferencia 8B/24 GB — prd.md:244; `Instructor-Privileged` colas de entrenamiento — prd.md:154). Toda combinación sin fila → `403 UNAUTHORIZED_RESOURCE_CLASS`. Filas no citables: DEFERRED al equipo fuente de políticas.
- Razón: dos implementaciones convergen sin inventar permisos; lo no citado se niega.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## F-03 — Precedencias dentro de cada paso + expiración

- Hallazgo origen: `review-rubric-20261013-4.md` F-03 (un disparo, dos códigos: 404 sin precedencia; `IDENTITY_BARRED` subsumido; `STATUS_ESCALATION_EXPIRED` compite con `UNAUTHORIZED_RESOURCE_CLASS`).
- Opción A: dejar la precedencia intra-paso indefinida.
- Opción B: fijar tabla caso→código dentro de cada paso.
- Decisión: B. 404 → `UNKNOWN_IDENTITY` antes que `UNKNOWN_COURSE`. 403 → `IDENTITY_BARRED` > `RESOURCE_SUBJECT_MISMATCH` > membresía no activa > (`STATUS_ESCALATION_EXPIRED` si el rol base no autoriza y existe ticket del mismo par con `expires_at <= at`; si no, `UNAUTHORIZED_RESOURCE_CLASS`).
- Razón: del más general (identidad) al más específico (acción); el código de expiración solo aparece cuando explica la causa real.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## F-04 — Frontera de `batch_id` ("parseable")

- Hallazgo origen: `review-rubric-20261013-4.md` F-04 (alcance de `batch_id` en 400/413 indefinido; "parseable" sin frontera).
- Opción A: `batch_id` en toda respuesta.
- Opción B: `batch_id` solo tras frontera verificable.
- Decisión: B. `batch_id` se asigna solo después de pasar auth, tamaño (≤ 5.000.000 B, ≤ 1000 filas), decodificación UTF-8, estructura JSON/CSV y `term` válido. Respuestas 400/401/413 SIN `batch_id`; 201 y 422 SÍ. "Parseable" = pasó todo lo anterior. Colisión: `UNIQUE(roster_batches.batch_id)` en DDL; ante choque el `IdGenerator` reintenta hasta 3 veces y luego `503`.
- Razón: frontera única y verificable; no se consumen IDs por basura; sin códigos nuevos.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## F-05 — `timestamp` de la baja en el body

- Hallazgo origen: `review-rubric-20261013-4.md` F-05 (ubicación del `timestamp` abierta; viola un-campo-un-canal).
- Opción A: instante efectivo provisto por el cliente.
- Opción B: body como canal único informativo + instante efectivo del `Clock`.
- Decisión: B. `timestamp` en el body JSON de la revocación (un solo canal), ISO-8601 UTC, informativo (se guarda como fecha académica). El instante efectivo (`revocation_propagated_at`, `dropped_at`) sale siempre del `Clock`. Formato inválido → código 400 existente si aplica; si ninguno aplica, OPEN registrado (sin código nuevo).
- Razón: el PRD lo lista como campo del request (prd.md:182); separar dato académico de reloj del sistema evita confiar en el cliente.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## F-06 — Envelope del 500 + catálogo acotado

- Hallazgo origen: `review-rubric-20261013-4.md` F-06 (500 sin envelope; códigos de escalación huérfanos sin P/Q/I).
- Opción A: crear códigos/envelopes nuevos.
- Opción B: envelope existente + acotar catálogo.
- Decisión: B. `500 AUDIT_LOG_TAMPERING_DETECTED` usa envelope `ErrorBody` RFC-7807 sin `ExplanationDTO`. Los códigos de escalación del catálogo se marcan fuera de las tres operaciones (FR-ESCAL-02), sin P/Q/I en esta entrega.
- Razón: todo status tiene envelope; el catálogo queda acotado y honesto; sin códigos nuevos.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-14 — Alcance del hash + enteros

- Hallazgo origen: `review-adversarial-20261013-4.md` H-14 (solo-fórmula vs fila completa; string decimal vs binario 8B).
- Opción A: hashear fila completa con binario nativo.
- Opción B: solo los 8 campos AD-04 §5, enteros futuros como string decimal UTF-8.
- Decisión: B. El hash cubre SOLO los 8 campos de la fórmula AD-04 §5; ningún conteo, `batch_id` ni `eventId` entra. Entero futuro: string decimal UTF-8.
- Razón: AD-04 heredado define la fórmula; ampliar el alcance sería cambiar un AD heredado.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-15 — Génesis + unidad de longitud

- Hallazgo origen: `review-adversarial-20261013-4.md` H-15 (`prev` génesis `0x00` vs 64 ceros; bytes vs puntos de código).
- Opción A: `prev` ausente = `0x00`, longitud en puntos de código.
- Opción B: `prev` = 64 `0`, longitud en bytes UTF-8.
- Decisión: B. Génesis `prev` = string de 64 `0` (semilla del DDL). Longitud de frame = bytes UTF-8.
- Razón: coincide con el DDL actual; bytes es lo único portable entre lenguajes. Tensión registrada: `planning/ARCHITECTURE.md` §2 l.97 menciona semilla `e3b0…` mientras el DDL (§3) usa ceros; se adoptan los ceros del DDL y se deja a triage (ver § Conflictos).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-16 — Captura de `request_now` + `roster.rejected`

- Hallazgo origen: `review-adversarial-20261013-4.md` H-16 (momento pre/post-auth; reuse vs `now` fresco en la 2ª tx).
- Opción A: captura post-auth + `now` fresco para `roster.rejected`.
- Opción B: captura pre-auth + reuse del mismo `request_now`.
- Decisión: B. `request_now` se captura UNA vez al entrar al adapter, antes de autenticar. El evento `roster.rejected` reutiliza ese mismo `request_now` como `occurredAt`.
- Razón: determinista y testeable con `fake_clock`; un request = un instante.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-17 — `IDENTITY_BARRED` vs `RESOURCE_SUBJECT_MISMATCH`

- Hallazgo origen: `review-adversarial-20261013-4.md` H-17 (mismo input, distinto `code` 403).
- Opción A: mismatch primero.
- Opción B: barred primero.
- Decisión: B (ver F-03). `IDENTITY_BARRED` gana sobre `RESOURCE_SUBJECT_MISMATCH`.
- Razón: una identidad suspendida/expulsada se niega sin importar el resto (AD-01, PRD l.134).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-18 — Percent-encoding de `term` + gramática del path

- Hallazgo origen: `review-adversarial-20261013-4.md` H-18 (`?term=2026-%46ALL`; `CS/101`, `CS101.`).
- Opción A: comparar crudo sin decodificar; gramática estricta 400.
- Opción B: decode-once + exacto; path exacto o 404.
- Decisión: B. El framework decodifica el percent-encoding una sola vez (RFC 3986) y luego se compara exacto (`2026-%46ALL` = `2026-FALL`). Path sin gramática extra: el segmento se busca exacto y si no existe → `404 UNKNOWN_COURSE`.
- Razón: es lo que hace FastAPI por defecto; no se inventa gramática.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-19 — Blancos de `drop_reason` + secreto vs intacto

- Hallazgo origen: `review-adversarial-20261013-4.md` H-19 (`" \t\n "`; secreto `uai_live_…` intacto vs enmascarado).
- Opción A: solo U+0020 cuenta como espacio; texto siempre intacto.
- Opción B: todo-blanco Unicode + máscara AD-06 sobre intacto.
- Decisión: B. (a) "Solo espacios" = todos los caracteres son blancos Unicode (`str.isspace()`): `" \t\n "` → `400 MALFORMED_DROP_REASON`. (b) Secreto `uai_live_…` en `drop_reason` se enmascara antes de persistir/loguear/responder: AD-06 (heredado) gana sobre "original intacto".
- Razón: los AD heredados mandan sobre reglas locales; 0 secretos en logs es NFR-SEC-04.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-20 — Anti-smuggling sobre membresía no-`ACTIVE`

- Hallazgo origen: `review-adversarial-20261013-4.md` H-20 (previa `DROPPED` con rol distinto: rechazar vs reactivar).
- Opción A: solo `ACTIVE` cuenta; resto reactiva.
- Opción B: cualquier estado cuenta; mismo rol sobre `DROPPED` no reactiva.
- Decisión: B. Cualquier membresía previa del mismo curso/term en CUALQUIER estado (`ACTIVE`, `DROPPED`, `SUSPENDED`, `COMPLETED`) con rol distinto al entrante → lote rechazado `422`. Mismo rol sobre `DROPPED`: NO se reactiva; la fila se cuenta como sin cambios y la membresía sigue `DROPPED`.
- Razón: fail-closed; una baja solo se revierte por un flujo explícito futuro, no por un roster (AD-02, AD-03).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-21 — Replay histórico + ticket futuro + intervalo vacío

- Hallazgo origen: `review-adversarial-20261013-4.md` H-21 (persistido-vs-histórico; `granted_at` futuro; `granted_at == expires_at`).
- Opción A: manda el estado persistido actual.
- Opción B: manda el intervalo y el estado REVOKED del ticket.
- Decisión: B. (a) Replay con `at` histórico: mandan el intervalo `[granted_at, expires_at)` y `revoked_at`/estado REVOKED del ticket, no el estado actual persistido. (b) `granted_at` futuro → el ticket aún no aplica, se usa el rol base. (c) Intervalo vacío no puede existir: el DDL ya impone `expires_at > granted_at`.
- Razón: una función pura del historial es reproducible; (c) ya está garantizado físicamente (AD-13, DDL).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-22 — Vista coherente del lector WAL

- Hallazgo origen: `review-adversarial-20261013-4.md` H-22 (exigir `caché == DB` con 503 vs snapshot previo/stale).
- Opción A: exigir igualdad caché==DB o 503.
- Opción B: snapshot + caché solo-DENY + 503 solo ante `busy_timeout`.
- Decisión: B. "Vista coherente" = todas las lecturas de un `authorize` en UNA transacción de lectura (snapshot WAL). La caché de revocadas solo puede adelantar un DENY, nunca producir un ALLOW. Lectores no devuelven 503 salvo `busy_timeout` agotado.
- Razón: la DB es la autoridad; la caché no puede abrir acceso (AD-03, AD-12).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-23 — Cardinalidad de `rule_ids`

- Hallazgo origen: `review-adversarial-20261013-4.md` H-23 (solo principal vs todos; observados mínimos vs extras).
- Opción A: solo el código principal.
- Opción B: todas las violadas ordenadas.
- Decisión: B. `rule_ids` = TODAS las reglas violadas, ordenadas por precedencia; el primero corresponde al `code` principal. Valores observados solo de esas reglas.
- Razón: explicabilidad completa (Plan-2 restricción 4) y orden determinista (AD-11).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-24 — Header repetido / vacío / CRLF

- Hallazgo origen: `review-adversarial-20261013-4.md` H-24 (primero vs último vs join; vacío vs ausente; wire vs app).
- Opción A: reglas primero/último/join + normalización app.
- Opción B: ambiguo = ausente; parser manda.
- Decisión: B. `X-Academic-Subject-Context` repetido o vacío se trata como ausente → `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` (paso 3). Se compara el valor tal como lo entrega el parser HTTP (RFC 9110 excluye espacios de borde y no admite CRLF dentro); la app no normaliza nada más.
- Razón: ambigüedad = negar; el framing es asunto del servidor HTTP, no del dominio (AD-01, AD-09).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-25 — Alcance de pureza (azar + reloj)

- Hallazgo origen: `review-adversarial-20261013-4.md` H-25 (`uuid.uuid4()`/`os.urandom()`/`time.monotonic()` cumplen la lista literal pero rompen determinismo).
- Opción A: lista literal de 5 imports.
- Opción B: ninguna fuente de no-determinismo en `domain/`.
- Decisión: B. `domain/` no puede usar NINGUNA fuente de no-determinismo: `random`, `secrets`, `uuid`, `os.urandom`, `time.*`, `datetime.now/utcnow/today`. Tiempo solo por `Clock`, IDs/azar solo por `IdGenerator`. La lista del lint se amplía. Alcance limitado a `domain/` (la generación de llaves con `os.urandom` vive en el broker/adapter según `planning/ARCHITECTURE.md` l.26, fuera de `domain/`).
- Razón: tests deterministas con `fake_clock`/`fake_id_generator` (AD-08).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## H-26 — Case de `effective_role`

- Hallazgo origen: `review-adversarial-20261013-4.md` H-26 (almacenado `"TA"` vs normalizado `"ta"`).
- Opción A: normalizar a minúsculas simétrico con `assigned_role`.
- Opción B: identificador exacto del DDL.
- Decisión: B. `effective_role` = el identificador exacto de `roles.id` en el DDL, sin transformar.
- Razón: una sola representación; no se inventa casing (AD-10, DDL tabla roles).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## Pendiente resuelto — Frecuencia y crash del scheduler

- Hallazgo origen: Gate 5 (frecuencia numérica + recuperación de crash abiertas).
- Opción A: dejar frecuencia y crash abiertos.
- Opción B: fijar barrido + protocolo de crash idempotente.
- Decisión: B. Barrido cada 1 s con `fake_clock`. Tras un crash, al reiniciar barre todo `ACTIVE` con `expires_at <= now` usando `UPDATE … WHERE status='ACTIVE' … RETURNING`; un evento por transición (idempotente). Sin promesa exactly-once más allá de esto.
- Razón: determinista y testeable; cierra el pendiente sin inventar protocolo distribuido.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## Pendiente resuelto — `COMPLETED` no activa

- Hallazgo origen: Gate 5 (`COMPLETED` sin productor definido).
- Opción A: `COMPLETED` como estado activo.
- Opción B: `COMPLETED` = no activa → DENY; ninguna de las tres operaciones lo crea.
- Decisión: B.
- Razón: fail-closed; la producción de `COMPLETED` queda fuera de las tres operaciones.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## Pendiente resuelto — Colisión de `batch_id`

- Hallazgo origen: Gate 5 (colisión 8hex sin regla).
- Opción A: sin regla (colisión pendiente).
- Opción B: `UNIQUE` + reintento acotado + 503.
- Decisión: B. `UNIQUE` en DDL (`roster_batches.batch_id`); ante choque, el `IdGenerator` reintenta hasta 3 veces y luego `503 AUTH_INTERNAL_POLICY_UNAVAILABLE` (código existente, sin inventar).
- Razón: regla ejecutable con código existente.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## DEFERRED — Capacidad y recuperación de cola (Fase 3 NFR)

- Hallazgo origen: Gate 5 (capacidad numérica + recuperación post-aceptación sin protocolo).
- Decisión: DEFERRED a Fase 3 NFR (`/bmad-testarch-nfr`), responsable Test-lead. Hasta entonces: cola llena → `503` (ya adoptado).
- Razón: sin medición real no se fija número (AD-04.3 intacto).
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## DEFERRED — TTL `uai_live_…` y reemisión de credenciales

- Hallazgo origen: Gate 5 (TTL sin regla; reemisión en reingesta sin cerrar).
- Decisión: DEFERRED. Fuera de las tres operaciones; responsable dueño de credenciales (Módulo 1 futuro). Registrado en el spine, sección Deferred.
- Razón: ninguna fuente Plan-2 fija TTL; no se inventa comportamiento.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## DEFERRED — Matriz completa `roles_matrix.json`

- Hallazgo origen: Gate 5 (cobertura por acción incompleta).
- Decisión: v0 cerrada por F-02; filas no citables DEFERRED al equipo fuente de políticas (fail-closed mientras tanto).
- Razón: sin fuente no se inventan permisos.
- Propuesta: asistida por IA (Claude) a partir de reviews BMad; aprobación: estudiante. Fecha: 2026-10-13.

## Conflictos con AD-01..AD-07 / PRD

- 0 conflictos bloqueantes: ninguna decisión aplicada debilita un invariante heredado ni contradice el PRD.
- 1 tensión registrada para triage humano (no bloquea, no revierte la aprobación): H-15 génesis. `planning/ARCHITECTURE.md` §2 l.97 menciona semilla `e3b0c44…` mientras el DDL (§3, `audit_ledger_metadata.head_record_hash`) usa 64 `0`; H-15 adopta los 64 `0` del DDL. AD-04 §5 no fija valor de génesis, por lo que no hay debilitamiento de invariante; se deja a triage si Plan-2 debe unificar ambas menciones.

## G6-01 — Columna `revoked_at` en escalaciones + intervalo de replay

- Hallazgo origen: `review-adversarial-20261013-6.md` G6-01 (replay con `at` histórico vs ticket REVOKED: H-21a invocaba "`revoked_at` del ticket" pero el DDL no tenía esa columna, solo `status`; dos unidades conformes divergían).
- Opción A: regla conductual sin columna (REVOKED ⇒ nunca aplica vs aplica si `at` en intervalo, a criterio de cada unidad).
- Opción B: columna física `revoked_at` con restricción + intervalo efectivo `[granted_at, min(expires_at, revoked_at))`.
- Decisión: B. Se agrega la columna `revoked_at` a `escalation_tickets` con `CHECK ((status <> 'REVOKED') OR (revoked_at IS NOT NULL))` (mismo patrón que credenciales/membresías). En replay, un ticket aplica en `[granted_at, min(expires_at, revoked_at))`; si `at >= revoked_at`, no aplica.
- Razón: la revocación es un hecho con instante; el replay debe reproducir la historia real. Restricción física, no "el dev debe recordar".
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 6; aprobación: estudiante. Fecha: 2026-10-13.

## G6-02 — Transición `ACTIVE→EXPIRED` con `QueueReservation` + reconciliación

- Hallazgo origen: `review-adversarial-20261013-6.md` G6-02 (evento del scheduler tras crash: la frontera tx del evento no estaba fijada —misma tx vs post-commit—; 1 vs 0 eventos ante crash intermedio).
- Opción A: evento en la misma tx que el `UPDATE … RETURNING`.
- Opción B: patrón `QueueReservation` (reserva antes del commit, publica tras commit) + reconciliación al reiniciar.
- Decisión: B. La transición `ACTIVE→EXPIRED` del scheduler y su evento se manejan con el patrón ya adoptado (`QueueReservation`: reserva antes del commit, publica tras commit). Tras un crash, al reiniciar el scheduler reconcilia: por cada ticket `EXPIRED` sin evento `escalation.expired` en el ledger para ese ticket, emite exactamente uno (idempotente por id de ticket). Resultado garantizado: exactamente 1 evento por transición.
- Razón: reutiliza mecanismos existentes; idempotencia por clave natural.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 6; aprobación: estudiante. Fecha: 2026-10-13.

## R2-01 — Roles de la matriz como `roles.id` exactos del DDL

- Hallazgo origen: Ronda 2 del Gate 6 (la matriz v0 usaba `Student` / `Instructor-Privileged` mientras el DDL fija `roles.id` en minúsculas con guion bajo; H-26 ya exige identificador exacto sin transformar).
- Opción A: mantener los nombres descriptivos de la matriz.
- Opción B: usar los `roles.id` exactos del DDL; si el DDL no tiene id para un rol citado, reportarlo como conflicto sin inventar.
- Decisión: B. Los nombres de rol en `roles_matrix.v0.json` son los `roles.id` exactos del DDL (`student`, `instructor_privileged`). Verificado: el DDL contiene ambos ids; 0 conflictos, nada inventado.
- Razón: una sola representación del rol (H-26).
- Propuesta: asistida por IA (Claude) a partir de la Ronda 2 del Gate 6; aprobación: estudiante. Fecha: 2026-10-13.

## G7-01 — Migración con `revoked_at` NULL (REJECT, sin DB previa)

- Hallazgo origen: Gate 7 G7-01 (ticket `REVOKED` con `revoked_at` NULL en DB migrada desde el DDL anterior; el `CHECK` rige escrituras nuevas, no backfill).
- Opción A: definir ruta de migración con backfill.
- Opción B: REJECT, sin migración en alcance.
- Decisión: B. `001_module1.sql` es la migración inicial; no existe DB previa que migrar. Si en el futuro hay migración 002, debe rellenar `revoked_at` antes de activar el CHECK.
- Razón: fuera de alcance; el CHECK vigente garantiza la propiedad en DB nuevas.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## G7-02 — Barrido sin reserva de cola (DEFER a NFR con WARN + métrica)

- Hallazgo origen: Gate 7 G7-02 (cola llena durante el barrido del scheduler: observabilidad hacia operadores sin fijar).
- Opción A: fijar observabilidad en el contrato de las 3 operaciones.
- Opción B: DEFER a NFR con defaults operativos.
- Decisión: B. DEFER a NFR (Test-lead, Fase 3 `/bmad-testarch-nfr`): cuando el barrido no puede reservar cola, registra log WARN estructurado (sin secretos) y métrica `scheduler_sweep_deferred_total`; reintenta en el siguiente barrido de 1 s.
- Razón: observabilidad operativa, no cambia el contrato de las 3 operaciones.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-01 — Código `AUTH_TOKEN_INVALID` → 401

- Hallazgo origen: Gate 7 (el PRD exige 401 pero el catálogo no tenía código; el ATDD no puede afirmar el `code`).
- Opción A: mantener 401 sin código (solo status).
- Opción B: nuevo código `AUTH_TOKEN_INVALID`.
- Decisión: B. Nuevo código `AUTH_TOKEN_INVALID` → HTTP 401, no reintentable: token ausente, inválido o expirado (PRD:255 "Inválido o Expirado → 401"). Va primero en el orden (401 antes que todo, ya adoptado).
- Razón: el PRD exige 401 pero el catálogo no tenía código; sin él el ATDD no puede afirmar el `code`. Excepción explícita a "sin códigos nuevos", aprobada.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-02 — Código `MALFORMED_DROP_TIMESTAMP` → 400

- Hallazgo origen: Gate 7 (resto OPEN de F-05: `timestamp` de baja con formato inválido sin código; ningún código existente describe este campo).
- Opción A: reutilizar un 400 existente.
- Opción B: nuevo código `MALFORMED_DROP_TIMESTAMP`.
- Decisión: B. Nuevo código `MALFORMED_DROP_TIMESTAMP` → HTTP 400, no reintentable: `timestamp` de baja ausente o no ISO-8601 UTC. Se valida en el mismo paso de sintaxis que `drop_reason` (P3/P4); si ambos fallan, `MALFORMED_DROP_REASON` va primero y ambos aparecen en `rule_ids` (H-23).
- Razón: fail-closed; ningún código existente describe este campo. Excepción explícita a "sin códigos nuevos", aprobada.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-03 — Mapeo ledger `membership.revoked` / `escalation.expired`

- Hallazgo origen: Gate 7 (resto OPEN: `decision`/`reasonCode` de `membership.revoked` y `escalation.expired` bajo `CHECK(ALLOW,DENY)` sin mapeo).
- Opción A: inventar códigos nuevos de razón.
- Opción B: reutilizar códigos del catálogo.
- Decisión: B. `membership.revoked`: `decision='DENY'`, `reasonCode='SUBJECT_ENROLLMENT_DROPPED'` (código ya existente). `escalation.expired`: `decision='DENY'`, `reasonCode='STATUS_ESCALATION_EXPIRED'`.
- Razón: la revocación/expiración retira acceso; reutiliza códigos del catálogo y cumple el CHECK ALLOW/DENY.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-04 — STRICT = abortar el lote completo

- Hallazgo origen: Gate 7 (resto OPEN: `STRICT` aborta vs segrega, PRD §7.2 ambiguo).
- Opción A: modo "segregar" (cuarentena parcial).
- Opción B: abortar el lote completo.
- Decisión: B. STRICT = abortar el lote completo (rollback total, 422 con manifiesto). No existe modo "segregar".
- Razón: AD-02 heredado exige atomicidad por lote; manda sobre la frase ambigua del PRD §7.2.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-05 — Negociación 422 siempre `application/problem+json`

- Hallazgo origen: Gate 7 (resto OPEN: negociación 422 JSON vs CSV).
- Opción A: negociar por `Accept` (JSON vs CSV).
- Opción B: una sola representación.
- Decisión: B. El cuerpo 422 es siempre `application/problem+json`, sea el input JSON o CSV; se ignora `Accept`.
- Razón: una sola representación del error; simple de probar.
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R3-06 — Orden en revoke + append-only físico

- Hallazgo origen: Gate 7 (resto OPEN: orden validación→tx→ledger en revoke; trigger vs tx).
- Opción A: orden conductual sin enforcement físico.
- Opción B: orden fijado + triggers físicos.
- Decisión: B. Orden en revoke: validar (P1-P4) → `BEGIN IMMEDIATE` → `UPDATE … WHERE status='ACTIVE' RETURNING` + `QueueReservation` → commit → publicar evento. Append-only de `audit_ledger` y `audit_events` impuesto físicamente con triggers SQLite `BEFORE UPDATE` y `BEFORE DELETE` → `RAISE(ABORT, 'append-only')`.
- Razón: mismo patrón que roster; AD-04 exige inmutabilidad y la consigna pide invariantes físicos, no "el dev debe recordar".
- Propuesta: asistida por IA (Claude) a partir del triage del Gate 7; aprobación: estudiante. Fecha: 2026-10-13.

## R4-01 — Gramática de `timestamp` de baja (RFC 3339 con zona UTC)

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-8.md (R4-01, medio-alto; hijo de R3-02).
- Opción A: heredar la gramática estricta del `at` interno (6 microsegundos obligatorios + zona).
- Opción B: aceptar cualquier ISO-8601 con zona UTC sin fijar dígitos fraccionales ni forma de zona.
- Decisión: `timestamp` = RFC 3339 `date-time` con zona UTC obligatoria: `YYYY-MM-DDTHH:MM:SS` + fracción opcional de 1 a 6 dígitos + (`Z` o `+00:00`). Otro offset, fecha sin hora o forma no RFC 3339 → `400 MALFORMED_DROP_TIMESTAMP`. Se persiste normalizado a `YYYY-MM-DDTHH:MM:SS.ffffffZ`.
- Razón: el ejemplo del PRD (l.222, milisegundos) debe aceptarse; la gramática estricta del `at` interno no aplica a un campo informativo del cliente.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 8; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R4-02 — `ErrorBody.rule_ids` opcional en 400 con doble fallo de sintaxis

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-8.md (R4-02, bajo; hijo de R3-02).
- Opción A: adjuntar `ExplanationDTO` en el 400 (rompe F-06 y el schema 400 de OpenAPI).
- Opción B: `ErrorBody` desnudo (el segundo código de un doble fallo deja de ser observable).
- Decisión: campo opcional. `ErrorBody` gana `rule_ids: string[]` (ordenado por precedencia, el primero == `code`), presente solo cuando falla más de una regla de sintaxis en la misma petición. No se adjunta `ExplanationDTO` en 400.
- Razón: hace visible el segundo código sin romper F-06 (400 sin DTO) ni el `code` singular.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 8; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-01 — Gramática exacta del `timestamp` de baja (residuos RFC 3339)

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-01, media-alta; bloquea; hijo de R4-01).
- Razón: cierra los pares divergentes de G9-01 (minúsculas `t`/`z`, `-00:00`, segundo 60, fecha inexistente, fracción de más de 6 dígitos).
- Decisión: ACCEPT. Gramática exacta `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|\+00:00)$`; solo `T` y `Z` en mayúsculas; `-00:00` → 400; segundo 60 y fechas inexistentes → 400 (fecha-hora válida de calendario); más de 6 dígitos fraccionales → 400, sin truncar. Fallo → `400 MALFORMED_DROP_TIMESTAMP`. Persistencia normalizada `YYYY-MM-DDTHH:MM:SS.ffffffZ`.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-02 — Precedencia de errores de sintaxis en `ingestRoster`

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-02, media; bloquea; hijo de R4-02).
- Razón: un mismo lote con `term` fuera de patrón y 0 filas daba `MALFORMED_TERM` o `BATCH_EMPTY` como código principal según la unidad.
- Decisión: ACCEPT. `BATCH_TOO_LARGE` (413) se evalúa antes de parsear; luego `MALFORMED_TERM` > `MALFORMED_BATCH` > `BATCH_EMPTY`. El HTTP lo fija el primer código; `rule_ids` lista todos en ese orden (R4-02).
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-03 — Serialización de campos opcionales ausentes (`null` vs omitido)

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-03, media; bloquea; afecta a R4-02 y al patrón preexistente de `ExplanationDTO.threshold`).
- Razón: `openapi.yaml` declara `rule_ids` como array no-nullable, y el texto de R4-02 dice "presente solo cuando…"; el `null` serializado por Pydantic rompía ambos.
- Decisión: ACCEPT. Regla global: los campos opcionales ausentes se OMITEN (no `null`) en todas las respuestas (`model_dump(exclude_none=True)` / `response_model_exclude_none=True`). OpenAPI los declara opcionales y no-nullable. Aplica a `ErrorBody.rule_ids` y a `ExplanationDTO.threshold`.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-04 — Propagación residual de la gramática del `timestamp` de baja

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-04, baja; no bloquea).
- Decisión: ACCEPT. Las menciones residuales "ISO-8601 UTC" del `timestamp` de baja pasan a referencia a la gramática de G9-01/R4-01 en contracts, ARCHITECTURE-SPINE (AD-09, AD-11), ports-and-adapters, dto.py y openapi.yaml.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-05 — Reutilización del nombre `rule_ids` en `ErrorBody` y `ExplanationDTO`

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-05, baja; no bloquea).
- Razón: ambos campos tienen el mismo significado (lista ordenada de reglas/códigos violados); el contenido difiere (códigos del catálogo en `ErrorBody`, citas AD-n en `ExplanationDTO`), y es intencional.
- Decisión: REJECT. Se conserva el nombre `rule_ids` en ambos DTO; no se renombra ni se restringe el tipo de elementos.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## G9-06 — Código para `/authorize` con body incompleto

- Hallazgo origen: architecture-spine/reviews/review-adversarial-20261013-9.md (G9-06, baja; no bloquea; preexistente, fuera de las ediciones R4).
- Decisión: DEFER. Owner A (Juan Pablo Parra); el código se fija en los criterios de aceptación de la historia de `/authorize` (Fase 4). Mientras tanto: `resource_arn` ausente o inválido → `400 MALFORMED_RESOURCE_ARN`.
- Propuesta: asistida por IA (Claude) a partir del review adversarial del Gate 9; aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q1 — Llamador de `revokeCourseAccess` e `ingestRoster` (rol `admin`)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-01); pregunta bloqueante 1 del review final.
- Opción A: denegar a todo llamador hasta fijar la lista (fail-closed sin lista).
- Opción B: exigir rol institucional `admin` para baja y lote; `403 ADMIN_ROLE_REQUIRED` (código nuevo, no reintentable) después del 401 y antes de la sintaxis.
- Decisión: B. Solo un actor con rol institucional `admin` invoca `ingestRoster` y `revokeCourseAccess`; el Department Chair (Dr. Marcus Vance) y el principal de servicio del SIS simulado se aprovisionan con `admin`. Sin mutación ni evento de dominio.
- Razón: PRD FR-INGEST-01, FR-REVOC-03 y l.305 (System Admin o Department Chair). Fail-closed por defecto.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q2 — Token Bearer y actor del ledger (ADVF-02 y ADVF-03)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-02, ADVF-03); pregunta bloqueante 2.
- Opción A: mantener ADVF-02 en DEFER y dejar sin valor las columnas NOT NULL de `audit_ledger`.
- Opción B: `TokenVerifierPort` (adapter simulado) devuelve `{actor_id, actor_role}` o `401 AUTH_TOKEN_INVALID`; scheduler = `actor_id='system:scheduler'`, `actor_role='admin'`; `resource_arn` = `urn:uai:subject:<subject_id>:model:*` y `action` = `revoke` / `ingest_roster` para baja y lote.
- Decisión: B. ADVF-02 pasa de DEFER a ACCEPT.
- Razón: identidad real simulada tras puerto (AGENTS.md); las columnas NOT NULL del ledger necesitan valor determinista.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q3 — `term` en la membresía (ADVF-13)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-13, H-20 no implementable); pregunta bloqueante 3.
- Opción A: mantener la membresía sin `term` (H-20 sin alcance definido).
- Opción B: `subject_memberships.term TEXT NOT NULL` con el mismo CHECK que `roster_batches.term`; `UNIQUE(identity_id, subject_id, term)`; índice único parcial `UNIQUE(identity_id, subject_id) WHERE status='ACTIVE'`.
- Decisión: B. H-20 se evalúa sobre `(identity, subject, term)`; la baja `revokeCourseAccess(userId, courseId)` sigue sin `term`.
- Razón: PRD l.134 (vínculo `(student_id, subject_id, role, term)`); Annex A pide `UNIQUE(user_id, course_id)` como enforcement físico, que el índice parcial conserva.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q4 — Entrega de `uai_live_` (ADVF-16 se mantiene DEFER)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-16); pregunta bloqueante 4.
- Opción A: definir ya el canal de entrega real.
- Opción B: mantener DEFER; `ingestRoster` llama a `CredentialDeliveryPort.enqueue(identity_id, raw_key)` (adapter simulado tipo outbox en memoria); la respuesta 201 no incluye claves; solo se persiste el hash.
- Decisión: B. El canal real queda fuera de las tres operaciones.
- Razón: PRD l.138 ("listas para su entrega segura"); NFR-SEC-04.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q5 — Gramática de `action` y matriz v0 ejecutable (ADVF-06, ADVF-07, ECF-24, ECF-25)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-06, ADVF-07); `review-detailed-design-final-edge-cases-raw.json` (ECF-24, ECF-25); pregunta bloqueante 5.
- Opción A: convertir cualquier valor de `action` en `UNAUTHORIZED_RESOURCE_CLASS`.
- Opción B: enum cerrado `action ∈ {"inference", "training"}` (otro valor o vacío → `400 MALFORMED_ACTION`, código nuevo); matriz v0 con claves ejecutables `{subject_id, role, action, resource_class, allow}` y cita por fila; todo lo demás → `403 UNAUTHORIZED_RESOURCE_CLASS`.
- Decisión: B. Filas: (CS101, student, inference, cpu_toy, true); (CS101, student, *, gpu, false); (CS-480, student, inference, gpu_24gb_workstation, true); (CS-480, ta, inference, gpu_24gb_workstation, true); (CS-480, instructor_privileged, training, gpu_workstation_or_central, true). EDGE-01 queda verificable.
- Razón: fail-closed; cada fila cita PRD l.244 / l.154 / l.76 o Annex A p.13.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q6 — Timestamp de baja futuro (ECF-13)

- Hallazgo origen: `review-detailed-design-final-edge-cases-raw.json` (ECF-13); pregunta bloqueante 6.
- Opción A: aceptar un `timestamp` futuro (dato informativo).
- Opción B: `timestamp` > `request_now` + 300 s → `400 MALFORMED_DROP_TIMESTAMP`.
- Decisión: B. ECF-13 pasa de DEFER a ACCEPT.
- Razón: un instante futuro es inconsistente; 300 s es un margen de desfase de reloj típico y testeable con `fake_clock`.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-Q7 — Gramática de `institutional_id` (ADVF-21)

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` (ADVF-21); pregunta bloqueante 7.
- Opción A: `^[A-Za-z0-9-]+$` sin cota (derivado del texto de contracts §0).
- Opción B: `^[A-Za-z0-9-]{1,64}$`, case-sensitive exacto.
- Decisión: B.
- Razón: PRD l.130 ("string alfanumérico, ej. STU-98432", con guion en los ejemplos); 64 como cota de columna.
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6-ACCEPT — Aplicación de ACCEPT del review final y ECF-19

- Hallazgo origen: `review-detailed-design-final-adversarial-raw.md` y `review-detailed-design-final-edge-cases-raw.json`; tabla "Revisión final 2026-10-13" de `review-detailed-design.md`.
- Decisión: se aplican visiblemente en los artefactos los 41 ACCEPT (ADVF: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 17, 19, 20, 21, 23, 25; ECF: 01, 02, 03, 05, 06, 07, 08, 09, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25). ECF-19 (BOM → `MALFORMED_BATCH`) queda aceptada como propuesta. ADVF-02 y ECF-13 pasan a ACCEPT por Q2 y Q6. Quedan DEFER: ADVF-16, ADVF-18, ADVF-22, ADVF-24, ECF-16, ECF-24, ECF-26. Quedan REJECT: ECF-04, ECF-10, ECF-11, ECF-27, ECF-28, ECF-29, ECF-30.
- Nota: ECF-24 (`action` vacía) la cubre Q5 con `MALFORMED_ACTION`, pero no está en la lista explícita de conversiones de Ronda 6; se mantiene DEFER hasta confirmar.
- Razón: consigna Fase 4 chequeo 6 ("Accepted → visibly fixed"); sin re-gate (decisión del estudiante).
- Propuesta: asistida por IA (Claude) a partir del review final BMad (adversarial + edge-case-hunter); aprobación: estudiante (A — Juan Pablo Parra). Fecha: 2026-10-13.

## R6b — Respuestas del aplicador de Ronda 6 (R6b-01..R6b-04)

- Hallazgo origen: preguntas del aplicador de Ronda 6 en `.work/paquete-decisiones-F-H.md` ("Ronda 6b"); afectan ADVF-07, ECF-24, ADMIN_ROLE_REQUIRED y fechas.
- R6b-01: `schemas/roles_matrix.v0.json` agrega `resource_catalog` que mapea el segmento `model` exacto del ARN a `resource_class`: `llama-3-8b-instruct` → `gpu_24gb_workstation` (prd.md:53, prd.md:244); `toy-cpu-demo` → `cpu_toy` [ASSUMPTION: nombre de fixture]; `train-queue` → `gpu_workstation_or_central` [ASSUMPTION: nombre de fixture]. `model` ausente → `403 UNAUTHORIZED_RESOURCE_CLASS` (fail-closed). Cubre ADVF-07.
- R6b-02: ECF-24 (`action` vacía) pasa a ACCEPT, cubierto por `400 MALFORMED_ACTION` (Q5). Conteos del triage: 42 ACCEPT, 6 DEFER, 7 REJECT.
- R6b-03: confirmado que `ADMIN_ROLE_REQUIRED` usa `ErrorBody` (sin ExplanationDTO): es autorización del llamador, no decisión de política; `rule_ids` solo si hay más de una regla (R4-02).
- R6b-04: las decisiones de las Rondas 1-6 conservan la fecha 2026-10-13; las posteriores usan 2026-10-14.
- Decisión: aplicar R6b-01..R6b-04 en artefactos con marca `[ADOPTED 2026-10-14, estudiante]`; sin re-gate; sin tocar tests ni fixtures.
- Propuesta: asistida por IA (Claude) a partir de las preguntas del aplicador de Ronda 6; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R9 — Pasada ATDD gap-fill y corrección de tautología (2026-10-14)

- Hallazgo origen: `.work/paquete-decisiones-F-H.md` ("Ronda 9"), aprobado por A (revisión conjunta de A y B, 2026-10-14).
- R9-00 (REJECT de propuesta IA): la pasada gap-fill dejó `Module1Service._actor()` delegando en `TokenVerifierPort` y convirtió los 3 tests de 401 (T-RES-12, T-REV-11, T-ROS-20) en guards verdes. Se rechaza: el verificador en tests es un fake configurado por el propio test, es una aserción tautológica (consigna: −5 c/u) y la verificación del bearer es lógica de GREEN. Texto adoptado: `_actor()` lanza `NotImplementedError("Module1Service._actor: verificación de token pendiente (AD-09)")` y los 3 tests son atdd-red (`@red("p0")`). Resultado verificado: 13 passed, 93 xfailed.
- R9-01 (IDENTITY_BARRED en ingest) [ADOPTED 2026-10-14, estudiante]: en `ingestRoster` una identidad preexistente `SUSPENDED`/`EXPELLED` es una violación de fila: lote `422` con fila `code: ROSTER_VALIDATION_FAILED`, `field: identity_status`, `rule_ids: ["ROSTER_VALIDATION_FAILED", "IDENTITY_BARRED"]`. `403 IDENTITY_BARRED` aplica solo a `/authorize`. Aplicado en `contracts.md` §3 P4 y catálogo, `openapi.yaml` (enum del 422), `dto.py` (`RosterRejectedManifest.code`), `events.md` y tests (T-ROS-14).
- R9-02 (AD-05 aprobador ≠ solicitante) [ADOPTED 2026-10-14, estudiante]: DDL `CHECK (approved_by IS NULL OR approved_by <> requester_id)` en `escalation_tickets`. Nota: la columna del DDL se llama `approved_by` (no `approver_id`); el CHECK usa el nombre real. Guard test T-ESC-GUARD-03.
- R9-03 (E4-S3 mismatch) [APLICADO en epics.md por la corrida epics-edit del 2026-10-14]: el AC de mismatch usa dos cursos existentes (header `CS101`, ARN de `CS-480`) → `403 RESOURCE_SUBJECT_MISMATCH`; un header `cs-480` (no existe, byte-a-byte) → `404 UNKNOWN_COURSE` por el orden de pasos. Corrección pendiente en `epics.md` (fuera de alcance de esta ejecución: no se tocó `epics.md`).
- R9-04 (formato de audit_ledger.timestamp) [ADOPTED 2026-10-14, estudiante]: CHECK GLOB de formato fijo `YYYY-MM-DDTHH:MM:SS.ffffffZ` en `audit_ledger.timestamp` y `audit_events.occurred_at`, igual que ADVF-23. Guard test T-LED-GUARD-06.
- R9-05 (supuestos de tests) [ADOPTED 2026-10-14, estudiante]: DENY de política se retorna como resultado `{decision: "DENY", ...}` (HTTP 403 lo mapea el adapter), no excepción; máscara AD-06 tal como la define `planning/ARCHITECTURE.md` AD-06: `uai_live_<4>••••••••••••<4>` (12 caracteres •; las notas previas con 4 caracteres • se corrigen); salt = 16 bytes aleatorios del `IdGenerator`, persistido en hex (32 caracteres); `resource_type` = `"model:" + resource_class` del `resource_catalog` (p. ej. `model:gpu_24gb_workstation`); model fuera del catálogo → `model:unknown`.
- Decisión: aplicar R9-01, R9-02, R9-04 y R9-05 en artefactos de `planning/detailed-design/` y en la suite ATDD; sin lógica productiva en `app/` (`module1.py` sigue como stub).
- Propuesta: asistida por IA (Claude) a partir de la pasada gap-fill; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R10 — Correcciones exigidas por el readiness gate NOT READY (2026-10-14)

- Hallazgo origen: `solu2-module1/planning/implementation-readiness-report-2026-10-14.md` (veredicto NOT READY) y `.work/paquete-decisiones-F-H.md` ("Ronda 10"), aprobada por el estudiante 2026-10-14 (delegado).
- Propuesta: asistida por IA (Claude) a partir del informe de readiness; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.
- Esta sección registra decisiones; no ejecuta workflows de epics. Los cambios a `planning/epics.md` (fuente de trabajo, no de Plan-2) quedan para la siguiente corrida de `bmad-create-epics-and-stories`.

## R10-M2 — Semilla génesis: CORRECCIÓN de H-15 (REJECT de la propuesta previa de la IA)

- Hallazgo origen: readiness M-2. `planning/ARCHITECTURE.md` l.97 fija la semilla `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; el DDL, `epics.md` y los tests usaban 64 ceros (H-15, sección "Conflictos" de este log).
- REJECT: la propuesta previa de la IA (H-15 "génesis = 64 `0`", adoptada como ADOPTED en contracts §3, events §3 y ports §4) se rechaza. Razón: el Plan-2 heredado manda (AGENTS.md: ARCHITECTURE.md es fuente de Plan-2 y solo se permite actualizar decisiones aprobadas de stack); los 64 ceros eran un placeholder del DDL, no una decisión de Plan-2. Esta entrada corrige H-15 sin borrar el histórico.
- Decisión (texto final): la semilla génesis `prev` del primer evento y el valor inicial de `audit_ledger_metadata.head_record_hash` es `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (`planning/ARCHITECTURE.md` l.97). Se mantiene sin cambio "longitud de frame en bytes UTF-8" (H-14/H-15).
- Razón: AD-04 §5 no fija el valor de génesis; el valor de Plan-2 cierra la tensión sin debilitar ningún invariante heredado.
- Aplicado en: `schemas/001_module1.sql` (DEFAULT y INSERT singleton), `schemas/events.md` §3, `ports-and-adapters.md` §4 y tabla, `contracts.md` §3 Q3 y §5, `architecture-spine/ARCHITECTURE-SPINE.md` (AD-04, sin renumerar), `test/atdd/atdd_support.py` (`GENESIS`) y `test/atdd/module1_contracts.test.py`.
- Pendiente: `planning/epics.md` :174 y :187 todavía dicen "64 ceros"; lo corrige la siguiente corrida de `bmad-create-epics-and-stories` (no se edita epics en esta corrida).

## R10-M1 — Estado Loading de ingesta: progreso de subida en cliente (MODIFY de la experiencia)

- Hallazgo origen: readiness M-1. `ux/EXPERIENCE.md:45` pide "Procesando registros: N / 120 (P%)" en tiempo real; `ingestRoster` es síncrono y responde 201 al final (`openapi.yaml`, AD-02).
- Opciones: A) añadir canal de progreso por fila en backend (rompe la atomicidad síncrona de AD-02); B) el Loading usa progreso de subida calculado en el cliente y el texto por fila se retira.
- Decisión: B. El estado Loading = bytes enviados / bytes totales del lote, más `Validando lote atómico...` hasta la respuesta. El texto "N / 120 registros" no tiene contrato y se reemplaza en la tabla Estados UX → contrato de `epics.md` (siguiente corrida). No se edita `ux/EXPERIENCE.md` (fuente Plan-2).
- Razón: AD-02 es invariante heredado; 120 filas < 2.0 s (FR-INGEST-01), así que el progreso por fila no aporta valor y no tiene fuente.
- Owner: A. Aplicado en `contracts.md` §6.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R10-C2 — Umbral de la ingesta: autoridad del PRD (triage de umbrales)

- Hallazgo origen: readiness C-2. PRD FR-INGEST-01 = 120 filas < 2.0 s; `ux/C-UX-Scenarios/scenario-1.md:83` = 1.2 s; `epics.md` solo cita 2.0 s.
- Decisión: para AC vinculantes, FR-INGEST-01 = 120 filas < 2.0 s (E2E funcional). NFR-PERF-02 = 1000 filas < 3.0 s (gate NFR, PLANNED). El 1.2 s de scenario-1 es objetivo UX no vinculante: DEFER, owner B, medido como stretch en `test/nfr-evidence.md`.
- Pendiente: tabla de umbrales triageados en `epics.md` (siguiente corrida).
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R10-M5 — Umbrales NFR: gate frente a objetivo

- Hallazgo origen: readiness M-5 (FR-AUDIT-04 y ARCHITECTURE piden 200 ms; NFR-AUDIT-06 pide 500 ms; NFR-DISP-07 pide 5.0 s / 512 MB; ARCHITECTURE §1.1 pide 2.0 s / 120 MB).
- Decisión: NFR-AUDIT-06 gate = 100 000 eventos p95 < 500 ms (PRD formal). 50 000 < 200 ms (test FR-AUDIT-04) y < 200 ms (ARCHITECTURE / scenario-4) son objetivos funcionales separados. NFR-DISP-07 gate = boot < 5.0 s y RAM ≤ 512 MB; 2.0 s / 120 MB de ARCHITECTURE son objetivo. Los AC de `epics.md` citan solo el umbral gate.
- Pendiente: tabla de triage en `epics.md` (siguiente corrida). Medición real: fuera de esta corrida (PLANNED).
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R10-M6 — E1-S1 con DDL completo (migración 001 única)

- Hallazgo origen: readiness M-6 (step 5 §4B: tablas creadas cuando se necesitan).
- Decisión: se mantiene un único `schemas/001_module1.sql` (la Ronda 10 cita `001_module1_schema.sql`; el nombre real del archivo es `001_module1.sql`). La consigna exige el schema como entregable de Fase 2 (contrato aprobado, no construido historia a historia). E1-S1 "aplica la migración 001 aprobada"; cada historia posterior solo usa o verifica las tablas e invariantes que le corresponden, citados en su AC. Justificación explícita en E1-S1 (siguiente corrida de `bmad-create-epics-and-stories`).
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-1 — Semilla génesis en el snippet DDL de ARCHITECTURE.md (corrección de fuente)

- Hallazgo origen: `solu2-module1/planning/implementation-readiness-report-2026-10-14-run2.md` K-1 (chequeo 5). `planning/ARCHITECTURE.md:97` fija `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; el snippet DDL de `planning/ARCHITECTURE.md:198` tenía 64 ceros (`DEFAULT '0000…0'`).
- Decisión: `planning/ARCHITECTURE.md:198` se alinea con la constante de la línea 97 y se marca con la nota `[CORREGIDO 2026-10-14, Solu-2 R10-M2/K-1: alineado con la semilla de §4 Immutable Audit Logger]`. Coincide con R10-M2 y con `schemas/001_module1.sql`. AD-01..AD-07 no se tocan.
- Razón: el snippet de 64 ceros contradecía la semilla normativa de §4 y el DDL real; un implementador que copiara el snippet obtendría una génesis distinta.
- Propuesta: asistida por IA (Claude) a partir del informe de readiness corrida 2; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-4 — Contradicciones de Plan-2 triageadas (sección nueva en `planning/epics.md`)

- Hallazgo origen: `solu2-module1/planning/implementation-readiness-report-2026-10-14-run2.md`, K-4 (chequeo 2 y 5), con las contradicciones de fuente que la misma corrida enumera (K-1, C-2, M-5, R8-08, R3-04).
- Opción A: editar `ux/EXPERIENCE.md`, `planning/prd.md` y `reviews/` de la raíz para sincronizar. Descartada: son fuentes de Plan-2 no editables en esta copia (AGENTS.md).
- Opción B: registrar cada contradicción en `epics.md` con fuente:línea, decisión vigente, owner, acción de sincronización para el próximo ciclo y estado. Elegida.
- Decisión: B. Se agregan 8 filas en `epics.md` § "Contradicciones de Plan-2 triageadas": EXPERIENCE.md:45 (progreso N/120, R10-M1), STU-MATEO-99 frente a STU-98432 (R8-08), 1.2 s frente a 2.0 s (R10-C2), umbrales NFR-AUDIT-06 y NFR-DISP-07 (R10-M5), génesis (R10-M2 y K-1), `PENDING` frente a `PENDING_APPROVAL`, roles `department_chair`/`Instructor` frente a `admin`/`instructor_privileged` (R6-Q1 y R2-01) y cuarentena frente a rollback (R3-04). Todas quedan con estado "registrada, no bloqueante para implementación".
- Hallazgo de verificación: las entradas "PENDING vs PENDING_APPROVAL", "roles Instructor/department_chair" y "cuarentena vs rollback" no estaban en el decision log; se registraron tras verificar `planning/prd.md`, `planning/ARCHITECTURE.md`, `schemas/001_module1.sql` y `detailed-design/contracts.md`.
- Razón: la implementación no necesita inventar contrato (el DDL, el OpenAPI y los AC ya fijan el comportamiento). Las fuentes de Plan-2 quedan intactas y la sincronización se hace en su ciclo propio.
- Propuesta: asistida por IA (Claude) a partir del readiness corrida 2; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-5 — Triage de hallazgos previos (Plan-2 + Solu-2) (sección nueva en `planning/epics.md`)

- Hallazgo origen: readiness corrida 2, K-5 (chequeo 6: triage no visible de `review-arch-implementability.md` y `review-agent-dev.md`), ampliado a todos los informes de `planning/detailed-design/reviews/`, `architecture-spine/reviews/` y los Defer de `reviews/` de la raíz.
- Opción A: triage solo de EC-01..EC-16 y D-01..D-15. Descartada: el chequeo 6 exige el triage completo de los hallazgos previos.
- Opción B: tabla consolidada ID | fuente | hallazgo | disposición | dónde quedó resuelto | owner, por hallazgo, y resumen por conteo o por gate donde el informe ya trae tabla propia. Elegida.
- Decisión: B. Se registran 64 hallazgos por fila: 38 ACCEPT, 20 REJECT, 5 DEFER y 1 "ACCEPT — PENDIENTE" (W-07); se suman 2 PENDIENTE dentro de la fila del gate 3 (H-10, H-11). Se sigue la disposición ya registrada en cada informe (AR-xx, EC-xx) y los criterios aprobados para el resto: ya decidido en rondas → REJECT citando la decisión; cambia el resultado observable de las tres operaciones → ACCEPT con ubicación verificada en el artefacto; operativo, NFR o fuera de las tres operaciones → DEFER con owner y fase. Se marcan "ACCEPT — PENDIENTE" tres casos verificados que no están resueltos en el artefacto: W-07 (`contracts.md:138` usa "PENDING" frente a `PENDING_APPROVAL` del DDL y el PRD), H-10 del gate 3 (gramática del local-part del email no fijada) y H-11 del gate 3 (`roster:ingest` en `contracts.md:97` frente a `roster.ingested` en `events.md`). Gates 1–9 y las tablas de review-detailed-design se resumen por gate y por conteo, con referencia a las rondas del paquete. Los tres Defer de Plan-2 quedan con owner y fase (ARCH-EDGE-03, ADV-MIN-01, ADV-MIN-03).
- Razón: REJECT significa que la sugerencia concreta queda superada por una decisión ya tomada, no que el riesgo sea falso (la misma convención de `review-detailed-design.md`). Las disposiciones D-xx y W-xx no tenían disposición registrada; se asignaron con los criterios aprobados y se dejó constancia en la tabla.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## Ronda 11 — "ACCEPT — PENDIENTE" del triage consolidado (K-5)

- W-07 (review-agent-architect): plantilla de `CONCURRENT_ESCALATION_NOT_PERMITTED` decía `PENDING`; el DDL y el PRD usan `PENDING_APPROVAL`. Decisión: ACCEPT, corregido en contracts.md §4.
- Gate 3 H-10: gramática de la parte local del email no fijada. Opciones: A) aceptar cualquier parte local no vacía; B) subconjunto dot-atom RFC 5321 `^[A-Za-z0-9._%+-]{1,64}$`. Decisión: B (fail-closed, testeable). contracts.md §3 P3.
- Gate 3 H-11: `roster:ingest` (contracts) vs `roster.ingested` (events.md). Decisión: tipo de evento `roster.ingested`; acción de ledger `ingest_roster` (R6-Q2). contracts.md §3 Q3.
- Propuesta: asistida por IA (Claude) a partir del triage consolidado K-5; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-4 cierre — Sincronización de fuentes UX con el contrato (R10-M1 / R10-C2)

- Hallazgo origen: `solu2-module1/planning/implementation-readiness-report-2026-10-14-run3.md`, K-4 (chequeos 2 y 5). Decisiones: `.work/paquete-decisiones-F-H.md` Ronda 10, M-1 y C-2.
- Decisión: se aplican solo las líneas de fuente afectadas, cada una con nota `[ACTUALIZADO 2026-10-14, Solu-2 ...]`. `planning/epics.md` no se edita en esta corrida (sus filas de "Contradicciones de Plan-2 triageadas" quedan para `bmad-create-epics-and-stories`).
  - `ux/EXPERIENCE.md`: antes l.45 `Procesando registros: 78 / 120 (65%)...` → después l.45 `Subiendo nómina: 65% (3,2 MB / 4,9 MB)...` (progreso de subida en cliente) seguido de `Validando lote atómico...` hasta 201/422; nota K-4/R10-M1. Línea 46 (estado inactivo del botón) sin cambio.
  - `ux/C-UX-Scenarios/scenario-1.md`: antes l.52 `Validando e insertando: 120 / 120 registros (100%)...` → después l.52 `Subiendo nómina: 100% (4,9 MB / 4,9 MB)...` + `Validando lote atómico...`; nota K-4/R10-M1. Revisado y sin cambio: `scenario-1.md` l.80 (`aria-valuenow` de la barra de subida, válido).
  - `ux/C-UX-Scenarios/scenario-1.md`: antes l.83 `inferior a **1.2 segundos**` → después l.83 umbral vinculante `2.0 segundos` (PRD FR-INGEST-01, 120 filas < 2.0 s) y `1.2 segundos` como objetivo UX no vinculante (stretch); nota C-2.
  - Revisado sin cambio: `ux/DESIGN.md`, `ux/wireframes/*`, `scenario-2..4.md` (no describen conteo por fila de ingesta ni el umbral de 120 filas).
- Razón: cierra K-4 en las fuentes sin inventar contrato; el progreso por fila no existe en backend (AD-02 síncrono y atómico), y el umbral vinculante es el del PRD.
- Propuesta: asistida por IA (Claude) a partir del readiness corrida 3; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-1 confirmación — Corrección de `planning/ARCHITECTURE.md:198` confirmada por el estudiante

- Hallazgo origen: readiness corrida 2 y corrida 3, K-1 (menor, proceso): la corrección de `planning/ARCHITECTURE.md:198` (DEFAULT de 64 ceros → semilla génesis de l.97) estaba fuera de la lista de AGENTS.md.
- Decisión: el estudiante confirma la corrección de `planning/ARCHITECTURE.md:198` (nota `[CORREGIDO 2026-10-14, Solu-2 R10-M2/K-1 ...]`) como parte de la actualización v2 de Fase 5, permitida por AGENTS.md. No se revierte.
- Razón: la semilla de l.97 es la decisión de Plan-2 y el DDL ya la usa; el snippet con 64 ceros contradecía esa fuente.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## K-5 — Filas faltantes de las reviews de la raíz en "Triage de hallazgos previos" (epics.md)

- Hallazgo origen: readiness corrida 3, K-5 (parcial): en el triage visible faltaban `reviews/review-arch-adversarial.md`, `reviews/review-ux-edge-cases.md`, `reviews/review-prd-adversarial.md` y `reviews/review-arch-edge-cases.md` (solo estaban ARCH-EDGE-03, ADV-MIN-01 y ADV-MIN-03).
- Opción A: añadir solo EDGE-UX-01..05 y los ACCEPT de arquitectura. Descartada: el chequeo 6 exige todos los hallazgos de las cuatro reviews con su ID.
- Opción B: añadir 21 filas (5 ARCH-ADV, 4 ARCH-EDGE, 7 ADV, 5 EDGE-UX) con la disposición registrada en cada review de Plan-2 y, para cada ACCEPT, la ubicación verificada en el archivo (PRD/ARCHITECTURE/ux de la raíz o artefactos de `solu2-module1/`). Elegida.
- Decisión: B. Las 21 filas quedan en ACCEPT; ninguna disposición de Plan-2 era DEFER, así que no se reclasificó nada. No se encontró ACCEPT sin ubicación (ningún "ACCEPT — PENDIENTE"). Dos reservas visibles en la tabla: ARCH-EDGE-02 cubre la precisión de microsegundos, pero el orden primario por `id` en las consultas no aparece en ningún artefacto (pendiente de confirmar); EDGE-UX-02, EDGE-UX-03 y ADV-MAJ-02 están resueltos en la fuente UX/PRD de la raíz, pero su operación queda fuera de las tres operaciones.
- Razón: el readiness exige que cada hallazgo previo tenga disposición y ubicación visibles. Los owners siguen el mapeo A/B ya usado en la sección (arquitectura y alcance → A; pruebas y NFR → B), pendiente de confirmar.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## Ronda 12 — Triage de `review-security.md` y `review-consistency.md` (K-11, K-12 del readiness corrida 4)

- Hallazgo origen: `solu2-module1/planning/implementation-readiness-report-2026-10-14-run4.md`, K-11 (mayor, chequeo 6) y K-2 residual (conteos TEA); K-12 (nota) sobre `architecture-spine/reviews/review-consistency.md`.
- Decisión: se triagean SEC M-01, M-02, M-03, B-01, B-02 (`planning/detailed-design/architecture-spine/reviews/review-security.md`) y CONS-1..5 (`architecture-spine/reviews/review-consistency.md`) en la tabla "Triage de hallazgos previos (Plan-2 + Solu-2)" de `planning/epics.md`, con disposición, ubicación y owner. Única decisión nueva: R12-B01.
- Cambios aplicados: `planning/detailed-design/contracts.md` §1, §2 y §3 (Q-fail de fallo de puertos); `planning/detailed-design/ports-and-adapters.md` §1 (modos de fallo); tests RED T-RES-15 y T-ROS-21; `test/atdd-checklist.md`, `test/traceability-matrix.md`, `test/tea-skill-matrix.md`, `test/test-design.md`, `test/e2e-trace-summary.json` con conteos vigentes (154 nodos = 129 atdd-red + 21 guardas + 4 harness).
- Propuesta: asistida por IA (Claude) a partir del readiness corrida 4; aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R12-B01 — Fallo de `Clock`, `IdGenerator` o `QueueReservation` → 503 fail-closed (SEC B-01)

- Hallazgo origen: `review-security.md` B-01 (baja, sube a media si el adapter defaultea a ALLOW). `contracts.md` §1 solo decía "instante del puerto `Clock`" y no fijaba el modo de fallo; el readiness lo marcó como defecto de implementabilidad.
- Decisión: en `resolveEffectivePermissions` (y en las otras dos operaciones) una excepción de `Clock.now()`, un `IdGenerator` que lanza al asignar `eventId`/`batch_id` (distinto de colisión UNIQUE) o la no aceptación de `QueueReservation` responde `503 AUTH_INTERNAL_POLICY_UNAVAILABLE` (reintentable), fail-closed: nunca ALLOW ni DENY, cero mutación, cero eventos parciales. No se usa `at` por defecto ni el reloj del proceso.
- Razón: sin instante no hay evaluación determinista; el fallo debe cerrar el acceso y no dejar una decisión sin auditar. Coincide con el patrón ya existente de store/cola (I3, §3 Q3) y con PRD §7.3.
- Tests RED: T-RES-15 `test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation` (E1-S2, `RaisingClock`) y T-ROS-21 `test_ingest_id_generator_failure_503_no_writes_no_credentials` (E3-S1, `RaisingIdGenerator`), en `test/fakes/fake_failing_ports.py`. Revoke: mismo criterio en `contracts.md` §2 Q-fail, test RED DEFER a TEA (no creado en esta ronda).
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R12-B02 — Enumeración por códigos diferenciales y `observed_*` (SEC B-02): REJECT, riesgo residual aceptado

- Hallazgo origen: `review-security.md` B-02 (baja severidad). La distinción 404 `UNKNOWN_IDENTITY` / 403 `IDENTITY_BARRED` / 403 `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` y los `observed_*` pueden servir de oráculo.
- Decisión: REJECT de la mitigación propuesta (ocultar códigos o valores). El riesgo residual queda aceptado y registrado.
- Razón: PRD y catálogo exigen códigos distintos (404/403) y la explicabilidad con valores observados es restricción 4 de Plan-2 (AD-11). Mitigación vigente: toda respuesta exige token válido (401 primero, R9-00) y los `observed_*` solo reflejan datos del contexto solicitado, nunca de otras identidades.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R12-M — Ventana perimetral 60 s, M-02 y M-03 (SEC M-01..M-03)

- M-01 (ventana de revocación perimetral de hasta 60 s): DEFER, owner A (integración perimetral). Dentro del módulo el corte es inmediato (DB autoridad; `resolve` lee tras el commit, H-22). Los < 60 s de NFR-REVOC-03 aplican a proxies externos fuera del módulo; medición PLANNED.
- M-02 (canonicalización de `userId` / `institutional_id`): ACCEPT, ya aplicado en `contracts.md` §0 (case-sensitive exacto, Q7; UUID canónico; `courseId` byte a byte). Test: `test_ingest_institutional_id_case_distinct_identity`.
- M-03 (forense de lote rechazado y cola sin bound): ACCEPT, ya aplicado (`roster.rejected` en la misma cadena tras rollback; cola llena → 503 sin descarte, AD-12). Capacidad numérica: DEFER NFR, owner B.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R12-CONS — Triage de `review-consistency.md` (CONS-1..5, K-12)

- CONS-1 (caché vs DB autoridad): REJECT, superado por H-22. CONS-2 (scheduler vs expiración perezosa): REJECT, superado por scheduler 1 s + reconciliación (G6-02). CONS-3 (catálogo sin `SUCCESS`): REJECT, superado por la documentación de `SUCCESS` (R1–R11). CONS-4 (Mandatory Edge Case): ACCEPT, conforme (AD-10, E4-S1). CONS-5 (binding sin AD-07/08/09): ACCEPT, resuelto (contracts §5 y tabla AD regenerada, K-6).
- Owner: A por defecto (arquitectura y alcance) cuando el hallazgo no lo asigna explícitamente.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## R12-K2 — Conteos TEA residuales (K-2) y ARCH-EDGE-02

- Conteos vigentes tras R12: colección 154 = 129 atdd-red (resolve 34, ingest 34, revoke 33, contracts 19, ingest_rules 9) + 21 guardas + 4 harness; `pytest -q` → 25 passed, 129 xfailed; `--runxfail -m atdd` → 129 `NotImplementedError`. Corregidos: `test/tea-skill-matrix.md`, `test/test-design.md`, `test/atdd-checklist.md` (estado actual), `test/e2e-trace-summary.json` (`by_level` = `cases`: api 129, other 25), `test/traceability-matrix.md` (§3, §11 y apéndice).
- Históricos sin cambiar: las cifras de las re-revisiones de `test/test-review.md` (116/132) son el registro de su fecha.
- ARCH-EDGE-02 ya cita `schemas/events.md` l.138 (orden FIFO e `id ASC`) y l.143 (verificación de cadena); sin cambio.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.

## Ronda 13 — residuos del readiness corrida 6 (2026-10-14)

- K-19 (readiness run6): contracts.md §2 y ports-and-adapters.md l.53 decían "test RED DEFER a TEA" para revoke R12-B01, aunque T-REV-12 ya existía. Decisión: ACCEPT; texto actualizado citando `test_revoke_clock_failure_503_fail_closed_no_mutation` (E2-S3).
- K-20 (detectado por el orquestador al revisar texto vigente antes de la corrida 7): epics.md E2-S2 citaba "< 500 ms (PRD §4.3)" como AC, en conflicto con NFR-REVOC-03 (< 200 ms local) y con la regla M-5 (los AC citan solo el umbral gate). Opciones: A) mantener 500 ms; B) AC con 200 ms y 500 ms como objetivo funcional más laxo. Decisión: B; fila añadida a "Umbrales triageados" de epics.md.
- Propuesta: asistida por IA (Claude); aprobación: A — Juan Pablo Parra (revisión conjunta de A y B, 2026-10-14). Fecha: 2026-10-14.
- K-21 (readiness run7): residuos de 500 ms en epics.md (l.242, G-1) y traceability-matrix.md (l.141, l.166) alineados al gate < 200 ms (NFR-REVOC-03). ACCEPT. Aprobado por A (revisión conjunta de A y B, 2026-10-14). 2026-10-14.
- K-22 (readiness run8): traceability-matrix.md:63 residuo de 500 ms alineado a 200 ms. ACCEPT. Aprobado por A (revisión conjunta de A y B, 2026-10-14). 2026-10-14.

## R14 — Renombre del DDL a `001_module1_schema.sql` (entrega Fase 5)

- Hallazgo origen: la consigna (pág. 11, entregables) pide un nombre explícito de schema. La Ronda 10 (M-6) había mantenido `001_module1.sql`; esta entrada reemplaza esa decisión para la entrega.
- Opciones: A) mantener `001_module1.sql` y explicar la discrepancia; B) renombrar a `001_module1_schema.sql` y actualizar las referencias vigentes.
- Decisión: B. Se renombró `planning/detailed-design/schemas/001_module1.sql` → `001_module1_schema.sql`.
- Alcance: referencias actualizadas en código, scripts y CI (`test/conftest.py` DDL_PATH, `scripts/quality_gate.sh`, `.github/workflows/quality-gate.yml`, `app/adapters/`), en documentos vigentes (contracts, ports-and-adapters, ARCHITECTURE-SPINE, events, epics, roadmap, test-design, ci-quality-gate, atdd-checklist, fixtures de test) y en `SOLU2-BMAD-RUNBOOK.md`.
- Sin cambio: los informes históricos (`architecture-spine/reviews/`, `detailed-design/reviews/`, `implementation-readiness-report-2026-10-14*.md`, corridas anteriores de `readiness-gate-report.md`, `sprint-change-proposal-2026-10-14.md`, `test/test-review.md`, `reviews/review-test-quality.md`) conservan el nombre original porque son evidencia de lo que se revisó en su momento. Este log tampoco reescribe sus entradas previas.
- Razón: la consigna pide el nombre del entregable; el contenido del DDL no cambia (solo el nombre del archivo).
- Verificación: `pytest -q` → 25 passed, 130 xfailed; `quality_gate.sh` → GATE LOCAL VERDE.
- Origen de la instrucción: instrucción de cierre del orquestador (2026-10-14), no una propuesta de la IA aprobada en un gate.
