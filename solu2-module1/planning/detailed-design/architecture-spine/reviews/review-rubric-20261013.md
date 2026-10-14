# Reviewer Gate — Rubric Walk: Architecture Spine Módulo 1 (2026-10-13)

**Rol:** rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura).
**Alcance:** spine + companions contra autoridades read-only. Sin modificar fuentes Plan-2 ni raws.
**Veredicto:** **CONDITIONAL** (spine honesto y construible como sustrato parcial; no autoriza Fase 3 / `bmad-build`).

## Fuentes leídas (evidencia)

- Spine: `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (v draft 2026-10-12, AD-08..AD-13).
- Companions: `solu2-module1/planning/detailed-design/contracts.md`, `ports-and-adapters.md`, `schemas/dto.py`, `schemas/001_module1.sql`, `schemas/events.md`, `schemas/openapi.yaml`.
- Autoridades read-only: `planning/ARCHITECTURE.md` v1.0.0 (AD-01..AD-07), `planning/prd.md` §5.2 (algoritmo Context-Enforced RBAC) y §5.1 (enunciado Mandatory Edge Case).
- Contexto (propuesta, no decisión): `architecture-spine/.memlog.md`, `solu2-module1/planning/detailed-design/reviews/review-detailed-design.md` (triage ADVD-01..14 / EC-01..34, estado: propuesta).

## Veredicto y lógica

**CONDITIONAL** — El spine cumple el estándar good-spine en honestidad y trazabilidad (fija como `[OPEN]` cada divergencia real del nivel inferior en lugar de resolverla en silencio; ninguna disposición del triage se presenta como aprobada), pero arrastra 5 conflictos materiales sin cerrar ([OPEN-01..05]) que impiden declarar PASS a build. Coherente con el memlog (`Reviewer Gate parcial: rubric CONDITIONAL`; `Fase 2 no aprobada`; `No iniciar Fase 3`).

No es FAIL porque: cada AD Rule local es enforceable en su núcleo (con la reserva de redacción de §3 abajo), Deferred no habilita divergencia, AD-01..AD-07 no se debilitan, las 3 operaciones + EDGE-01 están cubiertas, DENY→403 está separado dominio vs HTTP, `audit_events` es TABLA 1:1 sin segunda cadena, stack verificado, y OPEN-01..10 siguen marcados sin cerrar.

## Checklist good-spine (punto por punto)

### 1. ¿Fija divergencias reales del nivel inferior? — PASS con reserva
Sí. El spine + `ports-and-adapters.md` §6 + `contracts.md` §6 + `.memlog.md` documentan como `[OPEN-01..10]` los conflictos reales detectados por el adversarial / edge-case hunter (normalización vs byte-a-byte; caché vs DB-autoridad; scheduler vs lazy; hash/`reason_code`/ledger-en-rechazo; cola async/bound/fail-closed + predicado single-statement; transporte `at`/`term`; 401; envelope físico; gramáticas/`ExplanationDTO`; resto). Ninguno se finge resuelto; cada repetición ejecutable lleva su marcador (ver §7). Las disposiciones ACCEPT/DEFER/REJECT del triage se mantienen como propuesta, tal como exige su encabezado.

### 2. ¿Cada AD Rule es enforceable y previene su divergencia? — CONDITIONAL (ver hallazgo H-2)
- **AD-08 (pureza hexagonal):** enforceable. Regla negativa de imports (`fastapi`, `sqlalchemy`, red, `datetime.now`, `random`) + puertos `Clock`/`IdGenerator` + DTO primitivos. Enforcement: lint de imports + test de build (`contracts.md` §5, `ports-and-adapters.md` §5). Previene la divergencia "dos unidades con su propio reloj/azar/framework". PASS.
- **AD-09 (mapeo canónico operación↔HTTP):** enforceable. Tabla única (`resolveEffectivePermissions ↔ POST /api/v1/authorize` + header obligatorio; `revokeCourseAccess ↔ POST …/enrollments/…/drop`; `ingestRoster ↔ POST …/roster`; ninguna otra ruta). Enforcement: test negativo de rutas. Previene "cada unidad elige ruta" y "DENY en 200 en una unidad y 403 en otra". PASS (corrige Amelia D-01/D-02; ver §4).
- **AD-10 (fixture Mandatory Edge Case):** enforceable. Seed dual (`Student` en `CS101` + `TA` en `CS-480`), resolución acotada a la tupla `(identity_id, course_id)`, prohibición de importar rol de otro curso, sin cuota GPU/prioridad en la respuesta ([ASSUMPTION-01] PRD). Enforcement: fixture dual + `test_edge01_context_isolation`. Rechaza explícitamente la aserción del hunter crudo que iguala ambos contextos. PASS.
- **AD-11 (decisión explicable con regla citada):** enforceable. `ExplanationDTO.rule_ids` no vacío + valores observados + umbral + `reason_code` del catálogo cerrado (24 códigos `contracts.md` §4; `dto.py` `ErrorCode` Literal 24; `openapi.yaml` enums). Enforcement: `test_explain_assert_rule_cited`. El schema fino por operación queda [OPEN-09] sin fingir cierre. PASS.
- **AD-12 (serialización de carreras + idempotencia):** núcleo enforceable, elección arquitectónica abierta. Enforceables: receipt estable `ALREADY_REVOKED` sin mutación ni evento redundante; ingesta todo o nada con manifiesto de cuarentena; predicado condicional/single-statement o `BEGIN IMMEDIATE`; prohibición leer-luego-actualizar. La elección caché (`revoked_credentials_cache` + `workers:1`, padre AD-03/§2.1) vs DB-autoridad sin caché mutable se deja [OPEN-02] con ambas alternativas vivas (`ARCHITECTURE-SPINE.md` l.83; `contracts.md` §1-Concurrencia, §2; `ports-and-adapters.md` §6). Correcto no cerrar, pero la redacción presenta Alt B como Rule con coletilla — ver H-2. CONDITIONAL.
- **AD-13 (frontera temporal semiabierta):** núcleo enforceable, mecanismo abierto. Enforceables: intervalo `[granted_at, expires_at)`; `at >= expires_at` → `DENY STATUS_ESCALATION_EXPIRED`; instante por puerto `Clock` (UTC ISO-8601 microsegundos); `at` ausente sustituido en adapter, nunca en dominio. La elección scheduler interno (PRD §4.2 R5) vs expiración perezosa por `resolve` se deja [OPEN-03] (`ARCHITECTURE-SPINE.md` l.89; `contracts.md` §1-Tiempo; `ports-and-adapters.md` §6). Misma reserva de redacción que AD-12 — ver H-2. CONDITIONAL.

### 3. ¿Nada en Deferred permite divergir? — PASS
`ARCHITECTURE-SPINE.md` § Deferred: (a) migración SQLite→PostgreSQL solo si benchmark NFR lo exige, con dueños y condición "medición real, nunca suposición"; (b) guarda monotónica NTP post-V1; (c) barrido `INACTIVE` [ASSUMPTION-03] y transiciones ajenas (`COMPLETED`, `EXPIRED` sin TTL) fuera de las tres ops; (d) flujos de escalación (solicitud/aprobación) y deep-link UX más allá de las tres ops; (e) cuota GPU/scheduling fuera del Módulo 1 por [ASSUMPTION-01]. Todo es out-of-scope explícito o condicional medible; nada autoriza a una unidad a divergir dentro de las tres operaciones.

### 4. ¿Tech verificada? — PASS
Tabla Stack (`ARCHITECTURE-SPINE.md` l.99-108): Python 3.11+ mínimo heredado, FastAPI 0.143.0, Pydantic 2.14.1 (v2), SQLAlchemy 2.0.54 (línea 2.0, no 2.1), SQLite WAL versión del runtime (writer único, `busy_timeout 5000`), `pytest + pytest-asyncio + hypothesis` como harness RED. Fuentes citadas: `.work/stack-verification.md` 2026-10-12 + web-verification PASS en vivo (memlog). SQLite sin versión inventada — correcto. Sin migración de stack.

### 5. ¿Respeta AD-01..AD-07 read-only sin debilitar? — PASS (con OPENs preservados)
Tabla Inherited Invariants + `contracts.md` + `ports-and-adapters.md` §1/§5 + DDL preservan los 7 sin renumerar ni suavizar; cada fricción con el detalle lleva marcador sin cambiar al padre:
- AD-01: comparación cruda byte-a-byte preservada como autoridad; propuesta `strip+upper` etiquetada Alt A vs Alt B en spine Conventions, `contracts.md` §0/P2/P5, `dto.py` docstring, `001_module1.sql` comentarios, `ports-and-adapters.md` §6 [OPEN-01]. Grafías minúsculas de ejemplos PRD/ARCH declaradas sin valor normativo hasta triage. No hay debilitamiento silencioso.
- AD-02: `BEGIN IMMEDIATE`, `seen_ids`, rollback total, anti-role-smuggling. Preservado.
- AD-03: `workers:1`, `busy_timeout 5000`, `ALREADY_REVOKED` sin evento redundante. La tensión caché vs DB-autoridad queda [OPEN-02] con la alternativa del padre viva. No se presenta DB-autoridad como cerrada.
- AD-04: cadena hash + singleton `audit_ledger_metadata(id=1)` + orden `id ASC`. Fórmula/serialización/orden tx y cola 50ms/50ev quedan [OPEN-04/05]; `events.md` §3 declara que la variante competing (padre §2 sin `subject_id`/`action`) NO se adopta en silencio. Correcto.
- AD-05: lectura de ticket vigente + índice único parcial `idx_single_active_escalation`. Endpoint approve fuera de las tres ops (ADVD-05 ACCEPT PARCIAL correctamente acotado).
- AD-06: emisión inicial en claro / después enmascarado `uai_live_<4>••••<4>` + test regex de build. Preservado en `domain/explain`, DTO, SQL, eventos.
- AD-07: paginación `[1,100]` + cursor `(timestamp,id)` acotada a respaldo Empty/Error "fuera de las tres ops". Correcto no inventar paginación dentro de las tres ops.

### 6. ¿Cubre las 3 operaciones + EDGE-01 Mandatory? — PASS
`binds: [resolveEffectivePermissions, revokeCourseAccess, ingestRoster, EDGE-01]` en frontmatter; Capability Map por operación; `contracts.md` §§1-3 P/Q/I + §5 ligado invariante→enforcement→test RED; `ports-and-adapters.md` §1 cada componente exactamente una vez; `dto.py`/`openapi.yaml`/`001_module1.sql`/`events.md` cubren las tres. EDGE-01 literal ("Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently") cubierto por AD-10 + fixture dual + aislamiento por tupla + exclusión GPU/scheduling por [ASSUMPTION-01] + relación con PRD §5.2. Sin operaciones de otros módulos.

### 7. ¿DENY→403 separado dominio vs HTTP? — PASS
Dominio distingue `ALLOW|DENY`; adapter mapea `ALLOW → 200 AuthorizeResponse (decision: ALLOW)` y todo `DENY` de política → `403 DenyBody` RFC-7807 con `decision: DENY` + `ExplanationDTO` obligatoria (PRD §5.2, ARCH §4.2/AD-01). Prohibido `decision: DENY` en `200` (spine AD-09 l.65; `contracts.md` §0/Q1; `dto.py` `AllowOnly`/`DenyBody`; `openapi.yaml` 200 solo `ALLOW`, 403 `DenyBody`). La rama 401 del PRD §5.2 (token inválido/expirado) queda [OPEN-07] sin inventar matriz — gateway valida Bearer, dominio no inventa. Correcto.

### 8. ¿audit_events TABLA 1:1 sin segunda cadena? — PASS
Diseño consistente en los tres artefactos: autoridad única de cadena `audit_ledger + audit_ledger_metadata`; TABLA física `audit_events(event_id FK → audit_ledger.event_id, occurred_at, schema_version, event_type, payload JSON)` como envelope 1:1, no segunda cadena ni VIEW (`ports-and-adapters.md` §4; `001_module1.sql` §7b; `events.md` §1). Regla `occurred_at == audit_ledger.timestamp` byte-a-byte; escritura atómica misma tx (`BEGIN IMMEDIATE` + COMMIT conjunto, rollback total, fail-closed); "ninguna unidad escribe solo en una". Detalle trigger-vs-tx y orden validación→tx→ledger quedan [OPEN-04/05]. Consigna Fase 2 Step 2.2 cumplida (D-05).

### 9. ¿Dimensiones altitude feature cubiertas? — PASS
Paradigma hexagonal con mapa a código (`domain/ ports/ adapters/ dto/` + diagrama); convenciones Naming / Data & formats / State & cross-cutting; Stack; Structural Seed (stubs futuros sin lógica productiva — respeta stop-point solutioning); Capability→Architecture Map. GPU/telemetría/K8s/vLLM/identidad real tras puertos simulados; reloj inyectado. Sin sobreextensión a enterprise.

### 10. ¿OPEN-01..10 siguen marcados sin cerrar? — PASS
Verificación por archivo: spine (Conventions + AD-12/13 + Inherited AD-01); `contracts.md` §0/§1/§2/§6; `ports-and-adapters.md` §6 [OPEN-01..10] con alternativas y sin precedencia; `dto.py` docstring [OPEN-01/04/09/06]; `openapi.yaml` description + `UnauthorizedOpen`/`Unprocessable`/`Internal`/`Unavailable`; `001_module1.sql` comentarios [OPEN-01/03/04/05/06/09/10]; `events.md` §§3-4; `.memlog.md` lista abierta. NFRs en PLANNED, nunca EVIDENCED (correcto: `contracts.md` §§1-3 presupuestos con Estado PLANNED). Ninguna fila ACCEPT/DEFER/REJECT del triage se presenta como aprobada.

## Hallazgos (severidad + evidencia)

### H-1 [Major — driver del CONDITIONAL] Conflictos materiales [OPEN-01..05] sin cerrar impiden PASS a build
El spine hace lo correcto (marcar sin cerrar), pero el gate no puede pasar mientras sigan abiertas: [OPEN-01] normalización vs byte-a-byte AD-01 (impacto `cs-480`→ALLOW vs 403; ejemplos minúsculos vs canónico UPPER); [OPEN-02] caché `revoked_credentials_cache`+`workers:1` vs DB-autoridad (impacto `<200ms` local vs `<60s` perimetral, dueño de medición); [OPEN-03] scheduler PRD §4.2 R5 vs expiración perezosa (+ jobs activos al expirar, `scenario-2.md` §V); [OPEN-04] fórmula hash exacta / `reason_code` de éxito (catálogo sin `SUCCESS` vs padre con `SUCCESS`) / `decision CHECK(ALLOW,DENY)` frente a eventos roster/revoke / ledger en rechazo 422 y DENY P1–P4 / emisor 500; [OPEN-05] cola async 50ms/50ev + bound/desborde + `SQLITE_BUSY`/fallo Clock-Ledger + predicado single-statement exacto del revoke. Corresponden a ADVD-01..04 (ACCEPT) y EC-16/18/19. Acción: triage humano antes de ATDD/build; ninguna unidad elige alternativa por su cuenta.

### H-2 [Major — redacción] AD-12/AD-13 presentan la alternativa local como Rule con coletilla [OPEN]
`ARCHITECTURE-SPINE.md` l.83 ("la base de datos es la autoridad y no existe caché…") y l.89 ("la expiración se evalúa de forma perezosa…") se leen como decisión cerrada aunque la frase siguiente diga "propuesta pendiente / alternativa sigue abierta". Riesgo ya señalado por ADVD-13/14 (REJECT PARCIAL: el conflicto está marcado, pero la repetición puede leerse como cierre) y ADVD-12 (ACCEPT PARCIAL: no toda mención de "canónico" repite el marcador). Acción editorial (sin cambiar semántica): reformular a "default propuesto pendiente de triage" y repetir la etiqueta [OPEN-02]/[OPEN-03] en cada cláusula ejecutable (`contracts.md` §1-Concurrencia/§1-Tiempo ya lo hacen; extender al spine).

### H-3 [Major — cobertura de validación diferida a triage, correctamente no inventada] Gaps DTO/OpenAPI/adapter sin enforcement comprobable
Transferidos a [OPEN-06/07/09] y triage ACCEPT/DEFER, pendientes antes de ATDD: `dto.py` sin regex ARN/email/`institutional_id` (EC-02/06; OpenAPI sí tiene `pattern` ARN pero DTO no valida equivalente); `action` sin catálogo cerrado — no colapsar automáticamente a `UNAUTHORIZED_RESOURCE_CLASS` (EC-03 DEFER); `drop_reason` solo-espacios vs `minLength` (EC-05); CSV solo-encabezado → `BATCH_EMPTY` solo probado en JSON (EC-08); enforcement 5MB/1000 filas previo a parseo/tx en multipart (EC-09); email repetido con distinto ID → UNIQUE sin mapeo a manifiesto por fila (EC-10); contexto ausente mapeado explícitamente a 403 `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`+`DenyBody` sin 422/400 ambiguo del framework (EC-11); negociación 422 JSON vs CSV vía `Accept` + serialización CSV (comillas/comas/saltos) + convención `row_number` fila 85 (EC-24/25/26); `timestamp` académico de revoke PRD §4.3 ausente en DTO — distinguir hora de origen vs `revocation_propagated_at` del Clock (EC-29/ADVD-10); Bearer 401 code/mapping + `WWW-Authenticate` (EC-32/[OPEN-07]); `Clock` fail-closed 503 amarrado a contratos/tests (EC-22); normalización temporal UTC + igualdad envelope tras canonicalizar ms/µs (EC-21/34, ADVD-11). No es defecto del spine (stop-point + honestidad), pero la ATDD no debe arrancar sin cerrar o acotar cada uno.

### H-4 [Minor — consistencia física] Nombres y semillas a confirmar en triage
(a) `001_module1.sql` crea `subject_memberships` mientras el DDL padre (`planning/ARCHITECTURE.md` l.138) crea `subject_memberships` (una letra). El spine es internamente consistente (`contracts.md` §2-Q2 usa `subject_memberships`), pero requiere confirmación: ¿rename intencional o typo a alinear con el padre? (b) Semilla de génesis: padre §2.4 fija `e3b0c44…` como `prev_record_hash` génesis; `001_module1.sql` siembra `audit_ledger_metadata.head_record_hash = 0000…` (que es el DEFAULT del padre, concepto distinto). No hay contradicción formal, pero el primer `prev_record_hash` efectivo debe fijarse junto con [OPEN-04] fórmula. (c) `batch_id` propuesto `roster-<8hex>-<term>` vs ejemplo PRD `roster-b89f-2026` correctamente dejado [OPEN-06]; receipt canónico `revocation_propagated_at` con alias histórico `revoked_at` correctamente dejado [OPEN-06] — mantener ambos marcadores hasta confirmación. (d) `ports-and-adapters.md` §5 cita "línea SQL citada" para el índice de escalación sin número de línea — añadir puntero exacto (`001_module1.sql` l.87-89).

### H-5 [Info — verificado, sin acción] Deferred + NFR + terminal states
Deferred no divergente (ver §3); NFRs PLANNED sin EVIDENCED (correcto per constraint — no hay corrida medible; no declarar PASS readiness sin workflow oficial + Gate Drill con fallo inyectado); terminal states `COMPLETED`/`INACTIVE`/`EXPIRED`-sin-TTL, `STRICT`-vs-cuarentena, rol-divergente-rechaza-vs-ignora, reingesta-nueva-`batch_id` [ASSUMPTION], matriz rol×acción por curso, TTL `uai_live_…` correctamente dejados [OPEN-10]/DEFER (EC-07/14/15/17/20/23/27/28/30/31) sin inventar códigos ni transiciones.

## Trazabilidad de la corrección Amelia (D-01..D-11, según memlog)
D-01/D-02 (DENY→403, prohibido DENY en 200): verificadas en spine AD-09 + `contracts.md` §0–§1 + `dto.py` + `openapi.yaml`. D-03 (term GLOB exacto + CHECK GLOB ARN defendible con nota de límites): verificado en `001_module1.sql` l.30-34 y l.116-120. D-04 (cross-check a líneas reales): verificado por muestreo (`ports-and-adapters.md` §5 ↔ contratos/SQL). D-05 (TABLA `audit_events` 1:1): verificado §8 arriba. D-06..D-09 (500 refs, `ErrorCode` 24, unions 3.1, manifiesto 422 JSON+CSV): verificado por muestreo en `dto.py`/`openapi.yaml`. D-10/D-11 (receipt canónico + filas AD-07/08/09 en `contracts.md` §5): verificado. Restantes Amelia + Gate (OPEN-01..07/09/10) siguen abiertos — ver H-1/H-3.

## Condiciones para levantar CONDITIONAL → PASS
1. Triage humano cierra [OPEN-01..05] (o acota cada uno con dueño, alternativa elegida y trade-off AD documentado) sin debilitar AD-01..AD-07; re-ejecutar Reviewer Gate oficial.
2. Editorial H-2 aplicada (AD-12/AD-13 como "default propuesto") + punteros exactos H-4.
3. Brechas H-3 aceptadas con validadores/patrones + tests RED mapeados (o DEFER explícito con dueño) antes de ATDD.
4. NFRs siguen PLANNED hasta corrida medible; readiness PASS solo con reporte oficial + Gate Drill con fallo inyectado.

---
*Archivo de revisión fechado (único archivo escrito por este gate). No se modificaron `planning/ARCHITECTURE.md`, `planning/prd.md`, ni ningún `*-raw.*`.*
