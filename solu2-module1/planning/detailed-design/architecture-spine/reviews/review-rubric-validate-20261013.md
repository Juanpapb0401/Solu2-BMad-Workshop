# Review Rubric Validate — Architecture Spine Módulo 1 (2026-10-13)

- **Rol:** rubric walker del Reviewer Gate de `bmad-architecture` (intent Validate, solo lectura).
- **Alcance:** juzgar el spine contra el good-spine checklist (a)–(g). No se edita nada salvo este reporte.
- **Veredicto:** **CONDITIONAL**
- **Fecha:** 2026-10-13
- **Fuentes leídas (rutas absolutas):**
  1. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md`
  2. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/contracts.md`
  3. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md`
  4. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/planning/ARCHITECTURE.md` (solo §5 y líneas citadas)
  5. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/planning/prd.md` (§5.2, §7.3, §9.1 ASSUMPTION-01)
- **Regla de escala aplicada:** CONDITIONAL si hay conflictos documentados pendientes de triage humano ([OPEN-01..10]) pero correctamente dejados abiertos; NOT READY solo si hay decisiones inventadas, AD debilitados, o invariantes sin enforcement/test.

## 1. Resumen ejecutivo

El spine está en `status: draft` y fija los puntos reales de divergencia del nivel inferior sin omitir ninguno de los críticos para las tres operaciones confirmadas el 2026-10-12 (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`) y EDGE-01. Cada AD local (AD-08..AD-13) tiene Rule exigible que previene su divergencia declarada, con enforcement nominal y test RED listado en `contracts.md` §5 sin punteros archivo:línea/función/SQL inventados. Respeta AD-01..AD-07 heredados como autoridad read-only y no presenta AD-08..AD-13 como heredados. Los cambios recientes de `contracts.md` descritos en la auditoría Winston están correctamente ligados a fuente o degradados a ASSUMPTION/OPEN. Nada bajo Deferred autoriza divergencia entre dos unidades.

No hay debilitamiento de AD ni invariante sin enforcement/test ni decisión inventada como invariante. Por eso no es NOT READY. Tampoco es ROBUSTO: persisten [OPEN-01..10], la contradicción Q-fail vs Q3, y vaguedades (comprometido, cuando aplica, SQL revoke single-statement, batch_id, timestamp del drop, SUCCESS vs catálogo, transporte at/term, 401, COMPLETED/INACTIVE, TTL `uai_live_…`, matriz rol×acción, NFR en PLANNED) correctamente dejadas abiertas y transferidas al memlog. Coherente con `resultados-interaccion.md` l.12: gate real NO PASS, rubric CONDITIONAL, adversarial NO ROBUSTO, spine draft/parcial, no pasar a Fase 3.

## 2. Chequeo (a)–(g)

### (a) Fija los puntos reales de divergencia del nivel inferior sin omitir ninguno — PASA (condicionado a OPENs)

Puntos fijados:

- Comparación recurso↔contexto y gramática ARN (AD-01): spine l.45 + Conventions l.96; contracts §0 l.13–17, §1 P4–P5 l.26–27, §5 l.125, l.127.
- Atomicidad de lote, `seen_ids`, rollback total, anti-role-smuggling (AD-02): spine l.46; contracts §3 P2–P4 l.69–72, Q2 l.75, Anti-role-smuggling l.79, I1–I2 l.81–82, §5 l.128–130.
- Serialización carreras, predicado condicional vs `BEGIN IMMEDIATE`, prohibición leer-luego-actualizar, idempotencia `ALREADY_REVOKED` (AD-03/AD-12): spine l.47, l.83; contracts §2 Q2 l.52, Repetición l.56, I1–I3 l.58–60, Concurrencia l.61, §5 l.131–133.
- Ledger encadenado + metadata singleton + orden `id ASC` (AD-04): spine l.48 + Capability map l.127; contracts §1 Q3 l.31, §5 l.137.
- Exclusión mutua + anti auto-aprobación (AD-05): spine l.49; contracts §1 I2 l.36 (solo contexto tickets), §5 l.135–136 (fuera de alcance core, respaldo).
- Cero secretos (AD-06): spine l.50; contracts §1 I3 l.37, §3 Q2 l.75, §5 l.138.
- Paginación acotada (AD-07): spine l.51; contracts §4 l.117 (clamp [1,100]), §5 l.140.
- Mapeo operación↔HTTP y DENY 403 vs 200 (AD-09): spine l.64–65; contracts §0 l.9–15.
- Fixture EDGE-01 + ausencia cuota/prioridad (AD-10): spine l.71; contracts §1 I1 l.35, I4 l.38, Q2 l.30.
- Explicabilidad con regla citada + enum cerrado (AD-11): spine l.77; contracts §1 Q4 l.32, §2 Q4 l.54, §3 Q4 l.77, §5 l.139.
- Frontera temporal `[granted_at, expires_at)` + Clock inyectado (AD-13): spine l.89; contracts §1 I2 l.36, Tiempo l.40, §5 l.136.
- Pureza `domain/` (AD-08): spine l.59; contracts §5 l.141.

No se omite ninguna divergencia load-bearing: matriz rol×acción, actor/momento `COMPLETED`, TTL `uai_live_…`, bound/desborde cola async, dataset/concurrencia NFR, transporte at/term, 401, `COMPLETED`/`INACTIVE`, `SUCCESS` vs catálogo, Q-fail vs Q3 — todas están como [ASSUMPTION]/[OPEN] en `contracts.md` §6 l.146–149 y en `resultados-interaccion.md` l.10–11, transferidas al memlog, sin cerrarlas en el spine.

### (b) Cada AD tiene Rule exigible que realmente previene su divergencia declarada — PASA

- AD-08 (spine l.59): prohíbe `fastapi`, `sqlalchemy`, red, `datetime.now`, `random` en `domain/`; tiempo/azar solo por `Clock`/`IdGenerator`; DTO primitivos. Enforcement: lint imports; test de build (contracts §5 l.141). Previene dos accesos propios a framework/reloj/azar.
- AD-09 (spine l.65): mapeo único 1:1 + header obligatorio + prohibición `decision: DENY` en 200 + `ALLOW→200` / `DENY→403 DenyBody` con `ExplanationDTO` (PRD §5.2, ARCH §4.2/AD-01). Enforcement: routers únicos §0; test negativo de rutas (contracts §5 l.142). Previene rutas divergentes y 200 vs 403 divergentes.
- AD-10 (spine l.71): seed dual Student CS101 / TA CS-480 + resolución solo tupla `(identity_id, course_id)` + sin cuota/prioridad + rechazo aserción que iguala ambos contextos a Student. Enforcement: resolución acotada + fixture dual + contrato Q1 sin campos cuota (contracts §5 l.125–126); test `test_edge01_context_isolation` con aserción de ausencia. Previene unión global.
- AD-11 (spine l.77): `ExplanationDTO` con `rule_ids` no vacío + observados + umbral + `reason_code` del catálogo cerrado. Enforcement: `ExplanationDTO.rule_ids` no vacío (contracts §5 l.139); test `test_explain_assert_rule_cited`. Previene veredictos opacos por unidad.
- AD-12 (spine l.83): DB autoridad propuesta pendiente (alternativa padre sigue abierta) + `DROPPED→ALREADY_REVOKED` sin mutación/evento + todo-o-nada con manifiesto cuarentena + predicado single-statement o `BEGIN IMMEDIATE`, prohibido leer-luego-actualizar. Enforcement/Tests: rama `DROPPED→ALREADY_REVOKED`, validación previa + `BEGIN IMMEDIATE` + rollback, `UPDATE … WHERE (identity, course)` + predicado (contracts §5 l.131–133); tests `test_revoke_replay_idempotent`, `test_roster_row85_rollback`, `test_revoke_all_credentials`, `test_revoke_preserves_other_course`. Previene doble mutación y lectura obsoleta.
- AD-13 (spine l.89): intervalo `[granted_at, expires_at)`, `at>=expires_at` expirado → `DENY STATUS_ESCALATION_EXPIRED` 403, `Clock` UTC microsegundos, `at` ausente sustituido en adapter nunca en dominio; lazy pendiente vs scheduler PRD §4.2 R5 abierto. Enforcement: guarda intervalo + fake-clock (contracts §5 l.136); test `test_escalation_boundary_expires`. Previene bordes/relojes divergentes.
- Heredados AD-01..AD-07: cada fila §5 l.125–140 tiene punto de enforcement nominal + test RED. Sin invariante huérfano.

### (c) Nada bajo Deferred permite divergencia entre dos unidades — PASA

Spine l.132–136:

- Migración SQLite→PostgreSQL solo si benchmark NFR concurrencia lo exige, con dueños y condición medición real nunca suposición. Hasta entonces Stack l.107 fija SQLite WAL writer único `busy_timeout 5000`. No autoriza a una unidad a usar Postgres ya.
- Guard monotónico NTP `time.monotonic` (ARCH-EDGE-03, DEFER post-V1). AD-13 fija reloj pared vía `Clock` UTC microsegundos; ninguna unidad puede usar monotónico en V1.
- Barrido `INACTIVE` [ASSUMPTION-03] y transiciones ajenas (`COMPLETED`, `EXPIRED` sin TTL) diferidos. Ninguna unidad puede implementarlas para las tres ops.
- Flujos exclusivos escalación (solicitud/aprobación) y deep-link UX más allá de las tres ops diferidos. Coherente con contracts §5 l.135 fuera de alcance core.
- Cuota GPU/prioridades fuera Módulo 1 por [ASSUMPTION-01]. Coherente con AD-10 + contracts §1 I4. Prohíbe divergencia (ninguna unidad retorna cuota).

### (d) Respeta AD-01..AD-07 heredados sin debilitarlos; AD-08..AD-13 locales sin presentarlos como heredados — PASA

- Spine l.41–42 declara AD-01..AD-07 de `planning/ARCHITECTURE.md` v1.0.0 autoridad read-only, sin renumerar ni debilitar; enforcement en `contracts.md`.
- Tabla Inherited l.45–51 cita `planning/ARCHITECTURE.md` como From parent por fila.
- `contracts.md` l.5 convención de autoridad + l.121 (AD-01..07 heredados read-only, AD-08..13 spine-local solo `ARCHITECTURE-SPINE.md` §§AD-08..13) + cada Bound to/Q/fila §5 l.125–142 lleva `(heredado)` o `(spine-local)`. Verificado: §1 I1 l.35, I2 l.36, I3 l.37, I4 l.38, Q4 l.32; §2 I1 l.58, I2 l.59, I3 l.60, Q4 l.54; §3 I1 l.81, I2 l.82, Q4 l.77, Anti-role-smuggling l.79; §0 AD-09 l.8.
- Sin debilitamiento:
  - AD-01 crudo byte-a-byte sin cambiar; OPEN-01 sin precedencia hasta triage (spine l.45, l.96; contracts §0 l.17, §1 P2 l.24, P5 l.27).
  - AD-02 conserva `BEGIN IMMEDIATE`, `seen_ids`, rollback; AD-05 desbindeado de ingest correctamente (ver (g)).
  - AD-03 conserva `workers:1`, `busy_timeout 5000`, `ALREADY_REVOKED` (spine l.47); OPEN-02 deja alternativa padre abierta sin reemplazar (spine l.83; contracts §1 l.39).
  - AD-04 conserva hash + metadata singleton + `id ASC` (contracts §5 l.137); cola async bound/desborde queda OPEN (contracts §6 l.149), no se decide contra el padre.
  - AD-05 conserva índice único parcial como guarda física pero fuera de alcance core sin P/Q/I §§1-3 (contracts §5 l.135).
  - AD-06 máscara `uai_live_<4>••••<4>` + regex build (spine l.50; contracts §5 l.138) = padre l.389.
  - AD-07 clamp [1,100] + cursor `(timestamp,id)` (contracts §4 l.117, §5 l.140) = padre l.398; extensión a Empty/Error roster marcada respaldo fuera tres ops, no debilita.
- AD-08..AD-13 nunca se presentan como heredados de Plan-2.

### (e) Cubre las tres operaciones y EDGE-01 — PASA

- Frontmatter `binds` l.11: `resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`, `EDGE-01`.
- Capability map l.122–128: resolución+EDGE-01 (AD-01,08,10,11,13), baja sub-minuto (AD-03,08,11,12), ingestión atómica (AD-02,08,11,12), ledger (AD-04,06), explicabilidad E-01–E-04 (AD-11).
- Contracts cubre exactamente las tres ops del Annex A p.13 (l.3) con P/Q/I por op (§§1-3) + catálogo §4 + ligado §5.
- Mandatory Edge Case literal (“Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently”, AGENTS + PRD §5) → spine AD-10 l.71 seed dual + aislamiento tupla + sin cuota/prioridad + rechazo igualación a Student; contracts §1 Q2 l.30, I1 l.35, I4 l.38; test `test_edge01_context_isolation`. Relación con `EDGE-01 Multi-Subject Permission Resolution` y PRD explícita.

### (f) Cada dimensión de la altitud está decidida, diferida o es pregunta abierta — PASA (con OPENs)

Altitud `feature` (spine l.5), paradigma hexagonal RBAC aislamiento (l.6):

- Naming (l.95): inglés dominio, español docs, `subject_id` mayúsculas — decidido; grafías minúsculas ejemplos sin valor normativo hasta triage (OPEN-01) — abierto correctamente.
- Data & formats (l.96): UUID/`institutional_id`, UTC microsegundos, RFC-7807, DENY 403 — decidido; canonicalización pendiente — abierto.
- State & cross-cutting (l.97): fail-closed `AUTH_INTERNAL_POLICY_UNAVAILABLE` 503, secretos solo claro en emisión inicial, auditoría `eventId`/`occurredAt`/`schemaVersion` — decidido.
- Stack (l.101–108): Python 3.11+, FastAPI/Pydantic v2/SQLAlchemy 2.0/SQLite WAL writer único + harness ATDD RED — decidido (heredado Plan-2, sin atribuir decisiones no confirmadas).
- Structural Seed (l.112–118): rutas spine/contracts/domain/ports/adapters/dto/test — decidido, sin lógica productiva (stop-point solutioning).
- Capability→Architecture Map (l.122–128): decidido.
- Deferred (l.132–136): diferido con dueños/condiciones.
- Abiertos transferidos al memlog (`contracts.md` §6 l.146–149 + `resultados-interaccion.md` l.10–11): matriz rol×acción, `COMPLETED`, TTL, cola async, NFR datasets, transporte at/term, 401, etc. — abiertos correctamente. NFR presupuestos en PLANNED pendiente benchmark (§§1-3 l.41, l.63, l.86), nunca EVIDENCED.

### (g) Cambios recientes de contracts.md correctamente ligados a fuente o abiertos — PASA

Verificación contra `resultados-interaccion.md` l.2–9:

1. Autoridad heredado/spine-local (§5 + inicio, cada Bound/Q/fila con etiqueta, nada renumerado/borrado): verificado en (d). Correcto.
2. §1 I4 sin cuota GPU/prioridad (contracts l.38 + §5 l.126): Bound AD-10 spine-local l.71 + PRD [ASSUMPTION-01] §9.1 (`planning/prd.md` l.352: Módulo 1 solo rol/inscripción, cuotas Módulo 2/8). Enforcement nominal Q1 solo `{decision, effective_role, explanation}`; test `test_edge01_context_isolation` aserción ausencia. Correcto. Spine Deferred l.136 y AD-10 l.71 coherentes.
3. §2 I3 + fila §5 fail-closed 503 (contracts l.60, l.134): Bound AD-03 (heredado) + PRD §7.3 (`planning/prd.md` l.329–330: fail-closed `DENY` + `AUTH_INTERNAL_POLICY_UNAVAILABLE` + 503). No se atribuye solo a AD-03. Correcto.
4. §3 I2 solo AD-02 (contracts l.82 + Anti-role-smuggling l.79): autoridad AD-02 (`planning/ARCHITECTURE.md` l.343 anti-role-smuggling: prohibido alterar rol preexistente); AD-05 (`planning/ARCHITECTURE.md` l.372–381) solo workflow escalación (auto-aprobación + índice único), no bindea ingest. Desbindeo de AD-05 correcto.
5. Exclusión mutua fuera de alcance (contracts §5 l.135): creación escalaciones no es una de las tres ops 2026-10-12, sin P/Q/I §§1-3; `test_double_submit_single_ticket` respaldo. Correcto, evita inventar contrato para flujo exclusivo diferido (spine l.135).
6. Reingesta degradada a ASSUMPTION/OPEN (contracts §3 l.83 + §6 l.146): sin Bound, sin enforcement, sin test invariante, sin decidir hasta acuerdo. Correcto, evita invariante sin fuente.
7. Sin punteros inventados (contracts §5 l.121 nota explícita; enforcement nominales). Correcto para stop-point (stubs + RED por `NotImplementedError`, sin `bmad-build`).

Pendientes conservados sin cerrar (`resultados-interaccion.md` l.10–11): OPEN-01/02/03 + OPEN-04 (hash/reason_code/ledger en rechazo y DENY P1-P4; contradicción Q-fail l.33 vs Q3 l.31) + OPEN-05 (bound cola async, predicado single-statement) + OPEN-06/07/09/10 (transporte at/term, 401, COMPLETED/INACTIVE, TTL, matriz, NFR PLANNED) + vaguedades (comprometido l.39, cuando aplica l.32, SQL revoke l.52, batch_id l.74, timestamp drop l.62, SUCCESS vs catálogo §4 sin SUCCESS pese a ARCH §4.2 l.311–312). Todas correctamente abiertas; ninguna cerrada con suposición silenciosa.

## 3. Hallazgos (ordenados por severidad para el gate)

1. **[Bloquea ROBUSTO, no NOT READY] OPEN-01 canonicalización vs AD-01 crudo.** Spine Conventions l.96 (Alt A `strip+upper` boundary + comparación canónica byte-a-byte vs Alt B AD-01 read-only header crudo byte-a-byte sin normalizar, sin precedencia, sin cambiar AD-01) + contracts §0 l.17 + §1 P2 l.24/P5 l.27. Correctamente abierto; requiere triage humano. Sin esto no hay ROBUSTO porque `cs-480` vs `CS-480` y ARNs minúsculas de ejemplos (PRD/ARCH) cambian veredicto.
2. **[Bloquea ROBUSTO] OPEN-02 DB-autoridad sin caché vs padre `revoked_credentials_cache` + `workers:1`.** Spine AD-12 l.83 + contracts §1 l.39. Ambas alternativas abiertas; Stack l.107 + Inherited l.47 conservan `workers:1`/`busy_timeout 5000` nominal. Requiere triage; afecta concurrencia resolve∥revoke e idempotencia observable.
3. **[Bloquea ROBUSTO] OPEN-03 lazy vs scheduler interno.** Spine AD-13 l.89 (lazy propuesta pendiente) vs PRD §4.2 R5 l.162 (scheduler auto-revoca `grant+duration`). Contracts §1 l.40 deja ambas abiertas; intervalo `[granted_at, expires_at)` sí decidido. Requiere triage.
4. **[Correcto, mantener] Exclusión mutua fuera de alcance + reingesta OPEN.** Contracts §5 l.135 + §6 l.146 + §3 l.83; spine Deferred l.135. Evita P/Q/I inventados para creación de escalaciones y evita invariante de reingesta sin fuente. `test_double_submit_single_ticket` solo respaldo. No es omisión: es scoping exigido por las tres ops 2026-10-12.
5. **[Higiene / no bloquea CONDITIONAL] Restos que deben seguir OPEN, no decidirse en silencio:**
   - `architecture-spine/ARCHITECTURE-SPINE.md` l.127 `+ TABLA audit_events 1:1` sin fuente en `planning/ARCHITECTURE.md` §3 DDL (solo `audit_ledger` + `audit_ledger_metadata` l.179–200) ni en `contracts.md` §5 l.137. No se juzga como invención (companion `schemas/` fuera del alcance de este gate y `resultados-interaccion.md` l.13 dice schemas intactos), pero debe aclararse en triage si es nota de mapeo o tabla nueva; mientras tanto no usar como enforcement.
   - Contradicción Q-fail vs Q3 (contracts l.31 vs l.33), `SUCCESS` (ARCH §4.2 l.311–312) ausente del catálogo §4 l.90–116, `batch_id` (`roster-<8hex>-<term>` l.74 vs PRD `roster-b89f-2026` l.137), `page_size<1→1` por simetría [ASSUMPTION] l.148, 401 vs 403 (PRD §5.2 l.258–261), TTL/COMPLETED/matriz/NFR PLANNED (§6 l.149). Todas ya listadas como abiertas en `resultados-interaccion.md` l.11; mantenerlas abiertas hasta acuerdo.

## 4. Trazabilidad de fuentes

- AD-01 regex + byte-a-byte: `planning/ARCHITECTURE.md` l.329–331; header `X-Academic-Subject-Context` + `RESOURCE_SUBJECT_MISMATCH` 403.
- AD-02 `seen_ids`, `@universidad.edu`, `SUSPENDED`/`EXPELLED` → `ROLLBACK` + `roster_rejected_conflicts.csv`, anti-role-smuggling: `planning/ARCHITECTURE.md` l.340–343.
- AD-03 `ALREADY_REVOKED` sin evento redundante, `workers:1`, WAL `busy_timeout 5000`, `<200ms`: `planning/ARCHITECTURE.md` l.352–354; caché §2.1 l.90–91.
- AD-04 hash `SHA256(prev‖…‖reason_code)`, singleton `id=1`, `id ASC`, async 50ms/50 ev: `planning/ARCHITECTURE.md` l.364–367.
- AD-05 índice `idx_single_active_escalation` 409 + `approver≠requester` 403: `planning/ARCHITECTURE.md` l.377–380.
- AD-06 máscara `uai_live_<4>••••<4>` + regex build: `planning/ARCHITECTURE.md` l.389.
- AD-07 clamp [1,100] + cursor `(timestamp,id)` + 512MB: `planning/ARCHITECTURE.md` l.398.
- PRD algoritmo aislamiento (context, binding, no herencia, mínimo privilegio): `planning/prd.md` §5.2 l.277–281; fail-closed 503: §7.3 l.329–330; ASSUMPTION-01 cuotas fuera M1: §9.1 l.352.
- Auditoría Winston: `resultados-interaccion.md` l.2–13 (Fast path solo fuente, sin lógica/build/Fase 2; lint `ok:false` 3 low falsos positivos `{subject_id}`/`{student_id}` l.65 spine; memlog 33 entradas; ports/schemas intactos).

## 5. Decisión

**CONDITIONAL** — el spine es buen-spine en estructura y no inventa ni debilita, pero solo puede avanzar a Fase 3 tras triage humano de [OPEN-01..10] y las vaguedades listadas. Mantener `status: draft`, NFR en PLANNED (sin EVIDENCED sin corrida real), suite RED futura por `NotImplementedError`, y prohibición de `bmad-build` hasta cierre del gate. Veredicto real del gate sigue NO PASS hasta ese triage (coherente con `resultados-interaccion.md` l.12).
