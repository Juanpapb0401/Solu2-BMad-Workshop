# Reporte de auditoría — Amelia (bmad-agent-dev) — Fase 2

- **Fecha:** 2026-10-12
- **Alcance auditado (solo lectura, sin modificar):**
  - `solu2-module1/planning/detailed-design/ports-and-adapters.md`
  - `solu2-module1/planning/detailed-design/schemas/001_module1.sql`
  - `solu2-module1/planning/detailed-design/schemas/dto.py`
  - `solu2-module1/planning/detailed-design/schemas/events.md`
  - `solu2-module1/planning/detailed-design/schemas/openapi.yaml`
- **Autoridades (read-only):**
  - `planning/prd.md` v1.0.0 (§4.1–§4.4, §5.1–§5.2, §7.1, §9.1)
  - `planning/ARCHITECTURE.md` v1.0.0 (AD-01..AD-07, §2–§4, DDL §3)
  - `ux/C-UX-Scenarios/scenario-1.md`, `scenario-2.md`, `scenario-3.md`, `scenario-4.md`, `00-ux-scenarios.md` (SC-01..SC-04, EDGE-01)
  - `ux/EXPERIENCE.md` (§2.3, §2.5, §3.1–§3.2 E-01..E-04), `ux/DESIGN.md`
  - `references/tas-2-solu2.md` (consigna Fase 2, Steps 2.1–2.3)
  - `solu2-module1/planning/detailed-design/contracts.md` (companion P/Q/I + catálogo §4 + tabla §5)
  - `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (draft, AD-08..AD-13)
  - Triage propuesto: `solu2-module1/planning/detailed-design/reviews/review-arch-implementability.md`
  - Informe Winston: `solu2-module1/planning/detailed-design/reviews/review-agent-architect.md` (W-01..W-16, Q-A..Q-R)
  - Memlog: `solu2-module1/planning/detailed-design/architecture-spine/.memlog.md`
- **Veredicto explícito:** auditoría de implementabilidad, **no aprueba diseño, no cierra gate, no declara PASS**. Ningún `[OPEN-01..10]` ni `[ASSUMPTION-A1..A4]` se cierra aquí.
- **Regla aplicada:** todo lo que altere comportamiento queda como pregunta abierta con cambio mínimo sugerido; solo se declara conforme lo puramente estructural y verificado por ejecución.
- **Verificaciones ejecutadas (solo lectura):** `ast.parse(dto.py)` OK; `sqlite3.executescript(001_module1.sql)` en `:memory:` OK (9 tablas + 1 vista); conteo `nullable:` 9× en `openapi.yaml`; conteo códigos 24↔24 contracts↔openapi; `grep` de `CHECK`/`GLOB`/`urn:uai` en SQL.

## Resumen operativo

| # | Hallazgo | Prioridad | Tipo |
|---|---|-----------|------|
| D-01 | `POST /authorize` permite `200` con `decision: DENY` y a la vez expone `403`; contradice PRD §5.2 y ARCH §4.2/AD-01 que exigen `DENY → 403` | Alta | Pregunta abierta (bloquea `bmad-build`) |
| D-02 | `ErrorBody` del `403` no porta `explanation: ExplanationDTO`; viola AD-11 en el camino 403 | Alta | Pregunta abierta |
| D-03 | `CHECK` de gramática ARN citado en ports §5 no existe en SQL (cero `CHECK`/`GLOB` sobre `resource_arn`, cero literal `urn:uai`) | Alta | Defecto Step 2.3 |
| D-04 | `CHECK(term GLOB '[0-9][0-9][0-9][0-9]-*')` acepta `2026-XXX`; no enforcea `YYYY-(SPRING\|SUMMER\|FALL)` de contracts/openapi | Alta | Cambio físico mínimo |
| D-05 | Consigna exige **TABLA** `audit_events`; artefacto usa `VIEW audit_events` sobre autoridad `audit_ledger`, y la vista no almacena el envelope (`type`/`payload`/`ledger` anidado) | Alta | Pregunta abierta [OPEN-08] |
| D-06 | `AUDIT_LOG_TAMPERING_DETECTED` 500 no tiene respuesta `500` en `openapi.yaml` (ningún path referencia `'500'`) | Media | Cambio editorial |
| D-07 | `dto.py ErrorBody.code: str` libre vs `openapi.yaml` enum cerrado de 24; catálogo no enforceable en Python | Media | Cambio mínimo |
| D-08 | `openapi: 3.1.0` usa `nullable: true` 9× (estilo 3.0, deprecado en 3.1) | Media | Cambio mínimo |
| D-09 | `RosterRejectedManifestRow` huérfana: definida en `dto.py`, sin `$ref` en `openapi.yaml`; `422` retorna solo `ErrorBody`, anexo CSV sin contrato HTTP | Media | Cambio mínimo |
| D-10 | Claves de receipt revoke divergentes (`revocation_propagated_at` vs `revoked_at`) entre contracts §2-Q1/Repetición y dto/openapi | Media | Editorial pendiente [OPEN-06] |
| D-11 | Tabla contracts §5 sin filas AD-07/AD-08/AD-09; ports §5 sí las trae → companions inconsistentes | Media | Editorial (W-08) |
| D-12 | Tres decisiones abiertas presentadas como cerradas en companions (`strip+upper`, expiración perezosa, DB-autoridad sin caché) mientras ports §6 las deja `[OPEN-01/02/03]` | Alta | Rewording, no conducta |
| D-13 | Predicado single-statement del revoke y `BEGIN IMMEDIATE` sin línea SQL exacta; puntero cross-check es a guarda, no a línea (cubierto por [OPEN-05], no fingir cerrado) | Media | Reserva |
| D-14 | `reason_code` sin `SUCCESS` + `CHECK(ALLOW,DENY)` fuerzan decisión ficticia para `roster:ingest`/`ALREADY_REVOKED`; rechazo 422 con evento o cero eventos sin cerrar | Alta | Pregunta [OPEN-04] |
| D-15 | Transporte dual `term` (query-CSV + body-JSON) sin precedencia en OpenAPI si ambos viajan y difieren | Media | Aclaración [OPEN-06] |
| D-16 | Conforme: boundaries hexagonales, firmas primitivas, `Clock`/`IdGenerator`, simulación GPU/telemetría, estructura OpenAPI base | — | Conforme con reservas |

Cobertura Annex A y Mandatory Edge Case verificada en §8. Mapeo HTTP completo en §2.

---

## 1. Boundaries hexagonales y firmas primitivas

**Conforme con reservas.**

- Evidencia: `ports-and-adapters.md` §1 tabla — cada componente aparece una vez (`domain/resolution`, `domain/membership`, `domain/roster`, `domain/explain`, 3 puertos inbound, 5 outbound, 3 adapters inbound, 1 driven, 2 simulados, DTO). Regla AD-08 §1 l.41–44: "`domain/` no importa `fastapi`, `sqlalchemy`, clientes de red, `datetime.now`, ni `random`. Tiempo y azar solo por `Clock` / `IdGenerator`. DTO y firmas de puerto usan solo tipos primitivos".
- Verificado: `dto.py` importa solo `__future__.annotations`, `typing.Literal`, `pydantic.BaseModel/Field` (AST). Cero `import fastapi/sqlalchemy/random`, cero `datetime.now`. Firmas `AuthorizePort.resolve(user_id, course_id, resource_arn, action, at)`, `RevokePort.drop(user_id, course_id, drop_reason)`, `IngestPort.ingest(subject_id, term, rows)` usan `str`/listas/dicts planos en intención.
- Reserva: la pureza es declarativa (no hay `domain/` todavía por stop-point); el lint propuesto (`test de build`) no existe aún. No se marca como enforceado hasta que exista el lint. Ver D-11/D-13.

## 2. `Clock` / `IdGenerator`

**Conforme en intención.**

- Evidencia: `ports-and-adapters.md` §1 filas `Clock.now() (UTC ISO-8601 microsegundos)` y `IdGenerator.new_id()` + formato propuesto `roster-<8hex>-<term>`; diagrama `CK → fake_clock`, `D3 → IDG`; §3 `[ASSUMPTION-A1]` "`at` ausente → el adapter sustituye `clock.now()`, nunca el dominio".
- `dto.py` docstring: "sin `datetime.now/random` (AD-08)"; `at: str | None` + `RevokeResponse.revocation_propagated_at: str` + `RosterIngestResponse.batch_id` como `str` (no `datetime`).
- `events.md` §1: `occurredAt` "del puerto `Clock`"; `eventId` "del `IdGenerator`/adapter".
- Reserva: borde `[granted_at, expires_at)` y sustitución `at` son propuestos pendientes [OPEN-03/06]; no cerrar sin triage (ver D-12).

## 3. Simulación GPU / telemetría / K8s / vLLM / identidad real

**Conforme — correctamente fuera del Módulo 1.**

- Evidencia: `ports-and-adapters.md` §1 l.44 "Todo lo GPU/telemetría/K8s/vLLM/identidad real va tras puertos con adapters simulados"; fila `RegistrarSource (origen baja / nómina externa, simulado)` + `fake_clock` + `fixtures (seed dual CS101/CS-480 + CSV 120)`; `events.md` §0 "Todo lo GPU/telemetría/K8s/vLLM/identidad real va tras puertos con adapters simulados; aquí solo eventos de dominio + auditoría".
- Coherente con PRD §2.2 (telemetría→Módulo 3, scheduling→scheduling, inferencia/vLLM→Módulo 5/Gateway, LDAP→Mock Fixtures), PRD `[ASSUMPTION-01]` (cuotas GPU fuera de Módulo 1) y spine AD-10 ("no devuelve cuota GPU ni prioridad").
- Sin hallazgo: no se introduce lógica de VRAM, tiers, colas físicas ni polling real. El `term 2026-FALL` y seed dual son fixtures, no hardware.

## 4. Mapeo HTTP (AD-09)

Rutas canónicas verificadas contra PRD/AD cuando hay autoridad clara:

| Operación | HTTP canónico (ports §3 + openapi) | Entrada | Salida |
|---|---|---|---|
| `resolveEffectivePermissions` | `POST /api/v1/authorize` + header `X-Academic-Subject-Context` | `{ user_id, resource_arn, action, at? }` body; sin query | Ver §5 (D-01/D-02) |
| `revokeCourseAccess` | `POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop` | path `subject_id/student_id` + `{ drop_reason }` | `200 { student_id, subject_id, status: REVOKED\|ALREADY_REVOKED, revocation_propagated_at, explanation }` |
| `ingestRoster` | `POST /api/v1/subjects/{subject_id}/roster` (+ `?term=` solo CSV) | path `subject_id` + CSV multipart o JSON `{ subject_id, term, rows }` | `201 { processed, created_identities, updated_memberships, batch_id, explanation }` o `422` manifiesto |

- Correcto no exponer `/escalations/*` ni `GET /audit` en estas tres operaciones (flujos Deferred, spine).
- `[ASSUMPTION-A1..A4]` y `[OPEN-06/07]` honestamente marcados en ports §3 y `openapi.yaml` info. No se inventa matriz AuthN (401 abierto, ver §6).
- Reservas: D-10 (receipt keys), D-15 (term dual), `drop_reason` solo vs `+timestamp` académico PRD §4.3 (OPEN-06, W-09/Q-E).

## 5. Foco especial: `DENY` ¿`200` o `403`? + RFC-7807 + explicación tipada

### D-01 [Alta] — OpenAPI permite `200` con `decision: DENY`, en conflicto con `DENY → 403` de PRD/ARCH/AD-01

- **Path/sección:** `solu2-module1/planning/detailed-design/schemas/openapi.yaml` `/authorize` `responses '200'` → `AuthorizeResponse{ decision: enum [ALLOW, DENY] }` + `'403'` → `Forbidden`; `solu2-module1/planning/detailed-design/contracts.md` §0 fila resolve "`200 { decision, effective_role, explanation }` o error tipado" + §1-Q1 "`{ decision: ALLOW|DENY, … }`".
- **Evidencia fuente:**
  - PRD §5.2 flowchart: `TokenVal --|Inválido| Deny401["DENY: HTTP 401"]`, `CtxCheck --|NO| Deny403Subj["DENY: HTTP 403 (Not Enrolled)"]`, `ResCheck --|NO| Deny403Res["DENY: HTTP 403 (Resource-Subject Mismatch)"]`; reglas inviolables §5.2.2–2.4 ("se rechaza con `HTTP 403 RESOURCE_SUBJECT_MISMATCH`", "`DENY` con `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED`"); §4.3 "Rechazo instantáneo (`HTTP 401 / HTTP 403`)".
  - `planning/ARCHITECTURE.md` §4.2 pasos 4–8: "Emite Evento `decision=DENY, reason='RESOURCE_SUBJECT_MISMATCH'` … `GW-->>Client: HTTP 403 Forbidden, Payload RFC-7807 (Banner E-01)`"; AD-01 l.329–331 "retornar `DENY` con `HTTP 403 RESOURCE_SUBJECT_MISMATCH` si … no coincide byte a byte".
  - `scenario-3.md` §V: cancelada→`DENY SUBJECT_ENROLLMENT_DROPPED`, preservada→`ALLOW`; banner `#explainability-banner-dropped` "`Acceso Denegado … (HTTP 403)`"; `EXPERIENCE.md` §3.1 anatomía "`DECISIÓN: ACCESO DENEGADO (HTTP 403)`", E-01..E-04 todos `(HTTP 403)`.
- **Impacto:** dos unidades conformes divergen: U-A retorna `200 { decision: DENY, explanation }` para `RESOURCE_SUBJECT_MISMATCH` (obedece contracts/openapi-200); U-B retorna `403 ErrorBody` (obedece PRD/ARCH). Los tests ATDD `test_edge01_context_isolation` no pueden asertar status sin triage. Además `scenario-3.md` E2E ("`result: DENY`, código `SUBJECT_ENROLLMENT_DROPPED`") queda sin status canónico.
- **Cambio mínimo:** ninguno conductual aquí. Pregunta abierta para triage: o bien (Alt A) `POST /authorize` retorna `200` siempre con `decision` + `explanation` y `403` queda solo para fallos AuthN/gateway, o bien (Alt B) todo `DENY` de política (P5 + matriz rol×acción + `STATUS_ESCALATION_EXPIRED`) es `403 ErrorBody`. Fijarlo en contracts §0–§1, `openapi.yaml` (`'200'` descripción + `'403'` descripción) y `dto.py` a la vez; actualizar Winston Q-A/Q-B/Q-N. No inventar precedencia.

### D-02 [Alta] — El camino `403` pierde la explicación tipada (AD-11)

- **Path/sección:** `schemas/dto.py` `ErrorBody` (l.25–40) + `schemas/openapi.yaml` `components.schemas.ErrorBody` (l.273–297) vs `AuthorizeResponse.explanation`.
- **Evidencia:** `ErrorBody` exige `[type, title, status, detail, instance, code]` sin `explanation`; `AuthorizeResponse` exige `[decision, effective_role, explanation]`. AD-11 (spine): "todo `ALLOW`/`DENY` y todo rechazo porta `ExplanationDTO` con `rule_ids` no vacío". `EXPERIENCE.md` §3 exige banners con regla AD-n + valores observados + acción sugerida; PRD §5 `ALLOW o DENY con justificaciones estructuradas`.
- **Impacto:** si se elige Alt B (DENY→403), el cliente 403 no recibe `rule_ids`/`observed_*`/`threshold`/`action_hint` y los banners E-01..E-04 no se pueden renderizar desde el payload. Si se elige Alt A (DENY→200), el problema desaparece pero se contradice PRD/UX.
- **Cambio mínimo:** cuando se resuelva D-01, añadir `explanation: ExplanationDTO` (requerido u opcional según Alt) a `ErrorBody` en `dto.py` + `openapi.yaml`, o definir `DenyBody = ErrorBody + explanation`. Sin cerrar D-01 no tocar.

## 6. Errores tipados y HTTP

**Catálogo 24↔24 conforme en conjunto; un código sin HTTP en OpenAPI.**

- Verificado: contracts §4 (24 filas) y `openapi.yaml` `ErrorBody.code enum` (24) son idénticos, mismo orden (script: `missing=set()`, `extra=set()`). Cada código con HTTP y `Reintentable` en contracts.
- **D-06 [Media]:** `AUDIT_LOG_TAMPERING_DETECTED 500` no tiene `responses '500'` en ningún path (`grep '500'` en `openapi.yaml`: solo en `HttpStatus` literal de `dto.py`, cero `$ref` 500). `components.responses` define 400/401/403/404/409/413/422/503, sin `Internal`. El emisor está fuera de las tres operaciones (`GET /audit` FR-AUDIT-04, Winston W-02/Q-I). Impacto: contrato inalcanzable por HTTP; test de integridad no sabe qué status esperar. Cambio mínimo: añadir `Internal: 500 ErrorBody` + referenciarlo donde aplique (o documentar "solo verificación/exportación, fuera de las tres ops") cuando el equipo lo confirme.
- `401 UnauthorizedOpen` correctamente marcado abierto [OPEN-07] ("matriz AuthN por operación sin cerrar; gateway valida Bearer, dominio no inventa matriz"). Coherente con `EXPERIENCE.md` §2.5 (re-auth in-situ 401) y PRD §5.2/§7.1. No se inventa matriz — conforme como pregunta abierta.
- Precedencia P5 múltiple 403 (`RESOURCE_SUBJECT_MISMATCH` vs `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` vs `IDENTITY_BARRED`) sigue abierta (Winston Q-A, ports [OPEN-04]). `openapi.yaml` `Forbidden.description` lista 8 códigos sin orden. No cerrar aquí.

## 7. Constraints físicas: lo citado existe o no

Verificado por `sqlite3` + `grep CHECK/GLOB/UNIQUE`:

| Cláusula I citada (ports §5) | Existe en `001_module1.sql` | Veredicto |
|---|---|---|
| `UNIQUE(identity_id, subject_id)` membresías | l.56 `UNIQUE (identity_id, subject_id)` + `idx_memberships_lookup` | Conforme |
| `CHECK gramática ARN` (ARN rechaza `.` `/`) | **No existe** — cero `CHECK`/`GLOB` sobre `resource_arn`, cero literal `urn:uai` | **D-03 Alta** |
| `term YYYY-(SPRING\|SUMMER\|FALL)` | l.28 `CHECK (term GLOB '[0-9][0-9][0-9][0-9]-*')` — laxo | **D-04 Alta** |
| `UNIQUE INDEX idx_single_active_escalation WHERE status IN (…)` | l.81–83 exacto | Conforme |
| `CHECK` intervalo escalación + `duration 1..12` + `justification ≥20` | l.66–67, l.75–76 | Conforme |
| `CHECK status` membresías/credenciales/escalaciones + `dropped_at/revoked_at/granted_at` no-nulos condicionales | l.50, l.57, l.68, l.75, l.93, l.98 | Conforme |
| `decision CHECK(ALLOW,DENY)` + `record_hash UNIQUE` + `metadata(id=1)` + `INSERT OR IGNORE` génesis | l.111, l.117, l.126, l.132–133 | Conforme (con reserva D-14) |
| Índices `idx_memberships_lookup`, `idx_credentials_lookup/pair`, `idx_escalations_active`, `idx_audit_query/chain` | l.136–141 | Conforme (padre solo pedía 3; `pair` y `chain` son adición compatible) |
| `busy_timeout 5000` + `WAL` + `FK ON` | l.8–10 | Conforme |
| `term` patrón estricto, ARN, `at` microsegundos | Solo en contracts/openapi regex, no en SQL | Ver D-03/D-04 |

### D-03 [Alta] — ARN sin enforcement físico

- **Path:** `ports-and-adapters.md` §5 fila 2 ("`CHECK (resource_arn GLOB …)` documental en `001_module1.sql` + guarda dominio") vs `schemas/001_module1.sql` (sin `CHECK` sobre `resource_arn`).
- **Evidencia fuente:** AD-01 exige regex `^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$` (ARCH l.329–331); contracts §1-P4 la cita; SQL no la contiene (ver tabla).
- **Impacto:** Step 2.3 consigna: "toda fila I sin puntero exacto a línea SQL/guarda es defecto". Dos agentes implementan distinto: uno confía en DB, otro solo en dominio; bypass `.`/`/` (ARCH-ADV-MIN-01) reaparece si el dominio olvida validar.
- **Cambio mínimo:** añadir `CHECK (resource_arn GLOB 'urn:uai:subject:*:model:*')` documentado como aproximación GLOB (GLOB no expresa la regex completa; la guarda exacta queda en `domain/resolution` + test `test_arn_grammar_rejects`), o corregir ports §5 a "solo guarda dominio, sin CHECK físico (trade-off AD-01)". Decisión humana.

### D-04 [Alta] — `term` laxo en SQL

- **Path:** `schemas/001_module1.sql` l.28–29 vs `contracts.md` §3-P1 + `openapi.yaml` `RosterIngestRequest.term pattern '^[0-9]{4}-(SPRING|SUMMER|FALL)$'`.
- **Impacto:** `INSERT INTO subjects(term='2026-XXX')` pasa SQL pero falla contrato; fixture `2026-FALL` pasa en ambos, ocultando la divergencia hasta un seed con typo.
- **Cambio mínimo:** endurecer a `CHECK (term IN ('…') OR term GLOB …)` por término, o `CHECK (term GLOB '[0-9][0-9][0-9][0-9]-SPRING' OR term GLOB '…-SUMMER' OR term GLOB '…-FALL')`; instancia `2026-FALL` intacta. Alternativa: dejar laxo y declarar "validación solo en boundary (trade-off)". Humano elige.

## 8. OpenAPI bien estructurado (salvo D-01/D-02/D-06/D-08/D-09)

**Base conforme.**

- `openapi: 3.1.0`, `info.title/version/description` con alcance + `[OPEN-01..10]` + assumpciones, `servers: localhost:8000/api/v1`, 3 paths con `operationId` canónicos (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`), params header/path/query tipados, `requestBody` JSON + `multipart/form-data` roster, `components.schemas` 9 (Authorize*, Revoke*, Roster*, ExplanationDTO, ErrorBody), `components.responses` 8 reutilizables.
- `AuthorizeRequest.required [user_id, resource_arn, action]` + `at` opcional; `AuthorizeResponse.required [decision, effective_role, explanation]`; `RevokeResponse.required [student_id, subject_id, status, revocation_propagated_at, explanation]`; `RosterIngest*` con `minItems/maxItems 1/1000`, `assigned_role enum [student, ta]`, `batch_id` ejemplo `roster-8f3ab12c-2026-FALL`.
- **D-08 [Media]:** `nullable: true` 9× (l.157, l.250–272). En 3.1 lo normativo es `type: ["string","null"]` / `["integer","null"]`. Validadores estrictos 3.1 y generadores (`openapi-generator`, `fastapi[standard]`) lo rechazan o lo ignoran. Cambio mínimo: reemplazar las 9 ocurrencias por union-type; sin efecto conductual.
- **D-09 [Media]:** `RosterRejectedManifestRow` (`dto.py` l.129–134) sin `$ref` en `openapi.yaml`; `422 Unprocessable` retorna solo `ErrorBody`. Contracts §3-Q3 promete anexo `roster_rejected_conflicts.csv (row_number, institutional_id, field, observed, expected)` ante rechazo (PRD §4.1 R3 + §7.2). Sin contrato HTTP del anexo, el frontend `scenario-1.md` (`[ Descargar Manifiesto ]`) no sabe si es `text/csv` adjunto, campo `errors[]` o endpoint aparte. Cambio mínimo: añadir al `422` un `content` alternativo o un schema `RosterRejectedManifest { errors: RosterRejectedManifestRow[] }` + documentar `text/csv`, cuando el equipo lo confirme.

## 9. Envelope de eventos: definido pero no almacenado

### D-05 [Alta] — `audit_events` TABLA exigida vs `VIEW`, y envelope sin persistencia

- **Paths:** `schemas/001_module1.sql` l.143–160 (`CREATE VIEW audit_events AS SELECT … FROM audit_ledger`); `schemas/events.md` §1 tabla envelope (`eventId`, `occurredAt`, `schemaVersion`, `type`, `payload`, `ledger{ prevRecordHash, eventHash, ledgerSeq }`).
- **Evidencia fuente:** consigna `tas-2-solu2.md` Step 2.2 tabla: "`001_<module>schema.sql` | … Include `created_at/updated_at` and an **`audit_events` table**". Artefactos declaran autoridad `audit_ledger + audit_ledger_metadata` (AD-04 padre) con `VIEW` de compat (`event_id→eventId`, `timestamp→occurredAt`, `record_hash→eventHash`, `schemaVersion` constante `'1'`). Honestamente marcado [OPEN-08] en ports §4 + `events.md` §1 + SQL l.5 — no se finge resuelto.
- **Impacto doble:**
  1. Validador automático que busque `CREATE TABLE audit_events` falla aunque el diseño sea defendible (doble ledger autoritativo sería peor).
  2. La vista proyecta 13 columnas planas (`eventId … ledgerSeq`) sin `type` (`authorization.decided`/`membership.revoked`/`roster.ingested|rejected`), sin `payload` JSON (actor/conteos/`batch_id`/`ruleIds`), sin `ledger` anidado. El envelope versionado de `events.md` vive solo en memoria/`LedgerWriter`, no en disco. `schemaVersion` es constante `'1'` sin bump/migración implementable; `ledgerSeq = id` expone orden interno.
- **Cambio mínimo:** a elegir por triage (no aquí): (Alt A) `RENAME audit_ledger → audit_events` + recrear vista inversa `audit_ledger` (migración trivial, sin cambiar contratos); (Alt B) mantener `audit_ledger` y añadir columnas `type TEXT + payload TEXT(JSON)` a `audit_ledger` para persistir el envelope, manteniendo la vista como proyección. En ambos casos documentar bump de `schemaVersion`. Ninguna unidad escribe en la vista (ya declarado).

## 10. Referencias AD y nodos schema

- AD-01..AD-07 heredadas read-only correctamente preservadas (ports §0 l.8, SQL l.3, openapi info l.7, spine Inherited Invariants). AD-08..AD-13 locales del spine correctamente citados en ports §1/§5 y `events.md` (AD-11).
- **D-11 [Media] (W-08):** `contracts.md` §5 (12 filas) no trae AD-07/AD-08/AD-09; `ports-and-adapters.md` §5 (14 filas) sí ("Paginación `[1,100]`", "Pureza `domain/`", "Mapeo único operación↔HTTP"). Companions inconsistentes: un implementador que solo lea contracts no ve enforcement de paginación/pureza/rutas. Cambio mínimo editorial ya redactado en ports §5 + Winston §6/§10: copiar las 3 filas a contracts §5 cuando el equipo lo confirme. Sin efecto conductual; `GET /audit` sigue fuera de las tres ops (respaldo a Empty/Error, no endpoint nuevo).
- Nodos schema coinciden: `identities/subjects/roles/subject_memberships/escalation_tickets/subject_credentials/audit_ledger/audit_ledger_metadata` en SQL ↔ `ARCHITECTURE.md` §3 DDL (7 tablas + metadata). Adiciones compatibles: `updated_at` en `subjects/escalation_tickets/subject_credentials/audit_ledger` (padre no los tenía en esas tablas), `suspended/completed` ya en padre, índices extra `pair/chain`. Ninguna adición debilita AD heredada.

## 11. Decisiones abiertas presentadas como aprobadas

### D-12 [Alta] — Tres abiertos vestidos de cerrados en companions

| Abierto en ports §6/memlog | Presentado como hecho en companion | Evidencia |
|---|---|---|
| [OPEN-01] `strip+upper` vs byte-a-byte AD-01 | `contracts.md` §0 l.15 "`courseId` se canonicaliza en el boundary con `strip + upper` … comparación … sobre formas canónicas"; spine Consistency Conventions "Canonicalización `strip + upper` en el boundary" | Padre AD-01 l.331 "no coincide byte a byte con el valor del header"; memlog l.23 + Winston W-01/Q-H lo dejan abierto |
| [OPEN-03] scheduler PRD vs expiración perezosa spine | `contracts.md` §1 Tiempo "expiración perezosa por llamada" como hecho | PRD §4.2 R5 "revoca automáticamente … a través de un scheduler interno"; `scenario-2.md` §V "jobs activos mantendrán prioridad" sin regla; ports [OPEN-03] |
| [OPEN-02] caché `revoked_credentials_cache` + `workers:1` vs DB-autoridad sin caché | `contracts.md` §1 Concurrencia "la BD es la autoridad, AD-12" como hecho | Padre §2.1/AD-03 caché + `workers:1` + `<200 ms`; spine AD-12 "no existe caché mutable"; ports [OPEN-02] |

- **Impacto:** el lector de contracts/spine implementa una alternativa sin saber que hay otra igualmente "conforme"; el Mandatory Edge Case cambia de `ALLOW` a `403` según canonicalización si el fixture usa `cs-480` minúsculas (ARNs de ejemplo del PRD/ARCH van en minúsculas).
- **Cambio mínimo:** rewording sin conducta: anteponer "Propuesto pendiente [OPEN-0x]:" en `contracts.md` §0 l.15, §1 Concurrencia/Tiempo y spine Conventions/Capability Map, remitiendo a `ports-and-adapters.md` §6. Ya propuesto por Winston Q-H/Q-J/Q-L/Q-M; no aplicar conducta aquí.

### Otros abiertos correctamente marcados (conforme como pregunta)

`at`/`term`/receipts [OPEN-06+A1..A4], hash/fórmula/orden/`reason_code`/ledger-rechazo [OPEN-04], cola async/bound/`SQLITE_BUSY`/fail-closed [OPEN-05], 401 [OPEN-07], gramáticas/`ExplanationDTO` [OPEN-09], resto memlog [OPEN-10] — todos con `Alt A vs Alt B` y sin precedencia silenciosa en ports §6 + `events.md` §3–§4 + SQL comentarios `[OPEN-…]`. Nada que corregir en honestidad; bloquean `bmad-build` hasta triage, como debe ser.

## 12. Transacciones, carreras, idempotencia

- Roster todo-o-nada (`BEGIN IMMEDIATE` + validación previa + `seen_ids` + rollback, `test_roster_row85_rollback`), anti-smuggling (sin `ON CONFLICT DO UPDATE` de rol, `test_roster_no_role_smuggling`), revoke masiva del par en una tx con predicado + `ALREADY_REVOKED` sin evento redundante + otro curso intacto — bien orientados a AD-02/AD-03/AD-12 y triage EC-01/EC-10/EC-12/EC-14/EC-16 propuesto.
- **D-13 [Media]:** `ports-and-adapters.md` §5 fila revoke ("`UPDATE … WHERE identity_id AND subject_id` + predicado condicional (single-statement propuesto; `BEGIN IMMEDIATE` alternativo [OPEN-05])") no apunta a línea SQL exacta porque el predicado vive en futuro `domain/membership`, no en DDL. Igual para orden validación→tx→ledger ([OPEN-04/05]) y `busy_timeout` ante `SQLITE_BUSY` en resolve/roster. No es deshonesto (marca [OPEN]), pero Step 2.3 exige puntero exacto o trade-off AD documentado: añadir una línea "trade-off: predicado exacto en `domain/membership` (futura story), DDL solo aporta índices `pair/lookup`" cuando se confirme.
- Concurrencia resolve↔revoke↔roster coherente en intención (snapshot previo, DENY post-commit `SUBJECT_ENROLLMENT_DROPPED`); depende de D-12 (caché) y D-13.

## 13. Trazabilidad UX/PRD/EDGE-01 (conformidad)

| Escenario | Fuente | Cobertura en auditados |
|---|---|---|
| SC-01 roster 120 + fila 85 `@gmail.com` → 422 + 0 filas | PRD §4.1; `scenario-1.md` | contracts §3-P3/I1/Q2 + ports §5 + SQL `UNIQUE` + `events.md` `roster.rejected` + openapi `422`/`413`; manifiesto D-09 pendiente |
| SC-02 escalación 4 h + auto-aprobación 403 + reversión | PRD §4.2; `scenario-2.md`; `EXPERIENCE.md` E-03/E-04 | Lectura ticket + borde `[granted_at, expires_at)` propuesto + `FORBIDDEN_SELF_APPROVAL`/`CONCURRENT_ESCALATION…` 403/409; request/approve fuera de las tres ops (Deferred, correcto) |
| SC-03 drop Mateo + `SUBJECT_ENROLLMENT_DROPPED` + CS101 intacta | PRD §4.3; `scenario-3.md`; banner E-02 | contracts §2 + ports §5 + `test_revoke_*`; doble contexto conforme salvo D-01 |
| SC-04 auditoría 30 d + hash + 0 secretos + paginación | PRD §4.4; `scenario-4.md`; AD-04/06/07 | `audit_ledger+metadata`, máscara `uai_live_<4>••••<4>`, clamp `[1,100]`; `GET /audit` fuera de las tres ops (correcto); D-05/D-06 pendientes |
| **EDGE-01 Mandatory** "Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently" | PRD §5 + `00-ux-scenarios.md` EDGE-01 | contracts §1-Q2/I1 + ports `domain/resolution` + fixture dual + `test_edge01_context_isolation`; spine AD-10; rechazo EC-02 correcto. **Condicionado a D-01/D-12** (canonicalización) y matriz rol×acción abierta (Q-A/Q-R): el test solo puede asertar independencia, no el ALLOW concreto por rol hasta triage |

## 14. Cambios mínimos sugeridos (ordenados, sin aplicar)

1. **Triage D-01/D-02 juntos** (bloqueante): fijar `DENY→200` o `DENY→403` + dotar al camino elegido de `ExplanationDTO`. Toca contracts §0–§1, `dto.py` (`ErrorBody`/`AuthorizeResponse`), `openapi.yaml` (`'200'`/`'403'`), `events.md` Q-fail. Sin esto no hay `bmad-build`.
2. **D-03:** añadir `CHECK(resource_arn GLOB …)` aproximado o corregir ports §5 a "solo dominio".
3. **D-04:** endurecer `CHECK(term …)` a `SPRING|SUMMER|FALL` o declarar trade-off boundary-only.
4. **D-05:** triage `audit_ledger` vs `audit_events` (RENAME o columnas `type/payload`) + documentar `schemaVersion` bump.
5. **D-06:** añadir `responses Internal (500)` + referenciarlo o documentar fuera-de-ops.
6. **D-07:** `ErrorBody.code: Literal[24]` en `dto.py`.
7. **D-08:** `nullable: true` → `type: ["string","null"]` (9×).
8. **D-09:** publicar `RosterRejectedManifestRow` en `422` o documentar `text/csv`.
9. **D-10/D-11/D-13/D-15:** editoriales/precisiones ya redactadas en ports/Winston; copiar a contracts/openapi cuando el equipo confirme.
10. **D-12:** rewording "Propuesto pendiente [OPEN-…]" en contracts/spine, sin conducta.
11. Nada más. Ningún cambio conductual aplicado en este reporte; artefactos auditados intactos.

---

*Fin del reporte. Amelia queda a disposición para el triage humano; ninguna pregunta D-01..D-15 debe cerrarse con suposición silenciosa. Artefactos auditados no modificados; solo se escribe este informe.*
