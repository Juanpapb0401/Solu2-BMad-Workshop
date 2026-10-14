# Review Rubric Walker — Reviewer Gate bmad-architecture

- **Fecha:** 2026-10-12 (update, sobrescribe revisión previa)
- **Rol:** rubric walker del Reviewer Gate (solo lectura, sin modificar fuentes)
- **Spine auditado:** `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (draft 2026-10-12, AD-08..AD-13)
- **Companions auditados:**
  - `solu2-module1/planning/detailed-design/contracts.md`
  - `solu2-module1/planning/detailed-design/ports-and-adapters.md`
  - `solu2-module1/planning/detailed-design/schemas/dto.py`
  - `solu2-module1/planning/detailed-design/schemas/001_module1.sql`
  - `solu2-module1/planning/detailed-design/schemas/events.md`
  - `solu2-module1/planning/detailed-design/schemas/openapi.yaml`
- **Reporte Amelia:** `solu2-module1/planning/detailed-design/reviews/review-agent-dev.md` (D-01..D-15 + D-16 conforme)
- **Autoridades read-only:** `planning/ARCHITECTURE.md` v1.0.0 (AD-01..AD-07, §2–§4), PRD §5.2, ARCH §4.2/AD-01
- **Checklist aplicado (good-spine):** ¿fija divergencias reales del nivel inferior? ¿cada AD Rule es enforceable y previene su divergencia? ¿Deferred sin fugas? ¿tech verificada? ¿respeta AD-01..AD-07 read-only? ¿cubre las 3 operaciones + EDGE-01? ¿dimensiones del altitude cubiertas? ¿DENY→403 correctamente separado dominio vs HTTP? ¿audit_events es TABLA 1:1 sin segunda cadena?

## Veredicto

**CONDITIONAL** — no cerrar Gate. El spine fija divergencias reales y los companions ya cerraron la mayoría de los D-Alta de Amelia (D-01/D-02/D-03/D-04/D-06/D-07/D-08/D-09/D-10/D-11), pero el spine sigue desincronizado en dos puntos que bloquean el gate: convención [OPEN-01] que instruye `strip+upper` contra AD-01 byte-a-byte crudo, y mapa de ledger que omite la TABLA `audit_events` 1:1. Ningún NFR pasa a EVIDENCED; ningún [OPEN-01..10] se cierra aquí.

## Hallazgos tiered

### Critical

Ninguno. No hay suposición silenciosa que invente Seed Table, operaciones de otros módulos, ni lógica productiva; el stop-point se respeta.

### High

1. **[H-01 — OPEN-01: `strip+upper` instruido vs AD-01 byte-a-byte crudo]** Spine `Consistency Conventions / Data & formats`: "[OPEN-01] propuesta pendiente: canonicalización `strip + upper` en el boundary antes de comparar (AD-01 read-only exige byte-a-byte crudo; conflicto documentado sin cambiar AD-01)". Contracts §0 y `dto.py` cabecera ya lo anteponen como "propuesta pendiente" y ports §6 lo deja Alt A vs Alt B sin precedencia (bien), pero el spine lo mantiene como **Convention** (fila normativa) en vez de como alternativa abierta. Dos unidades conformes divergen: U-A normaliza `cs-480`→`CS-480` (ALLOW) y U-B compara crudo (403 `RESOURCE_SUBJECT_MISMATCH`). Viola el checklist "respeta AD-01..AD-07 read-only" y "cada Rule previene su divergencia": la convención actual **produce** la divergencia que dice prevenir. Amelia D-12 lo marcó correctamente. Cambio mínimo (triage humano, no aquí): rewording a "Propuesto pendiente [OPEN-01]: Alt A strip+upper vs Alt B crudo AD-01; sin precedencia hasta triage" en spine Conventions + Inherited AD-01 row; ninguna unidad implementa una alternativa como hecho.

2. **[H-02 — Spine desincronizado en ledger: omite TABLA `audit_events` 1:1]** Companions ya resolvieron Amelia D-05: `001_module1.sql` §7b crea `TABLE audit_events(event_id FK → audit_ledger, occurred_at, schema_version, event_type, payload)` con regla `occurred_at == timestamp` byte-a-byte y escritura atómica misma tx; ports §4 y `events.md` §1 declaran "una sola autoridad hash, sin segunda cadena". Pero el spine sigue diciendo `Capability → Architecture Map`: "Ledger y no-repudio | LedgerWriter + audit_ledger(+metadata) | AD-04, AD-06" y el Inherited AD-04 row solo "evento por mutación/decisión, verificación por id ASC". Un implementador que solo lea el spine no ve la TABLA exigida por la consigna Step 2.2 ni la regla 1:1/envelope. Checklist "¿audit_events es TABLA 1:1 sin segunda cadena?": **companions SÍ, spine NO**. Cambio mínimo: añadir fila/binds `audit_events` 1:1 + regla timestamp + misma-tx en Inherited AD-04 y Capability Map, remitiendo a ports §4 / SQL §7b.

### Medium

3. **[M-01 — AD-12/AD-13 honestos pero con regla + alternativa en la misma frase]** Spine AD-12 ("[OPEN-02] propuesta pendiente: la BD es la autoridad y no existe caché mutable... alternativa del padre AD-03/§2.1 con `revoked_credentials_cache` + `workers:1` sigue abierta") y AD-13 ("[OPEN-03] propuesta pendiente: expiración perezosa... alternativa PRD §4.2 R5 con scheduler sigue abierta") marcan el abierto correctamente (bien, a diferencia del estado que Amelia D-12 criticó en contracts viejos). Pero la Rule también fija conducta ("no existe caché", "no hay scheduler") antes del triage. Enforceable en lo demás (predicado condicional/single-statement o `BEGIN IMMEDIATE`, prohibido leer-luego-actualizar; intervalo `[granted_at, expires_at)`, `at>=expires_at` expirado, Clock inyectado). Rewording: prefijar "Propuesto pendiente" a la frase conductual, igual que H-01. No bloquea solo, pero suma a CONDITIONAL.

4. **[M-02 — AD-08 declarativa sin lint existente]** Spine AD-08 (pureza `domain/` sin fastapi/sqlalchemy/`datetime.now`/`random`, tiempo/azar por `Clock`/`IdGenerator`) previene divergencia real de testeabilidad y `dto.py` lo verifica por AST (cero imports prohibidos). Pero no hay `domain/` todavía (stop-point) ni test de build/lint implementado; Amelia §1 lo dejó "conforme con reservas". Correcto como intención; no marcar enforceado hasta que exista el lint. Sin cambio conductual.

### Low

5. **[L-01 — Deferred limpio, sin fugas; falta nombrar `GET /audit`]** Deferred del spine (PG solo con benchmark, guard monotónico NTP, barrido `INACTIVE`, transiciones `COMPLETED`/`EXPIRED`, flujos escalación/request-approve, GPU/scheduling fuera por [ASSUMPTION-01]) no filtra operaciones de otros módulos y respeta el alcance de 3 operaciones. Detalle: no nombra explícitamente `GET /audit/access-events` como diferido (companions sí lo dejan fuera de las tres ops). Añadir una línea lo haría auditable. Sin impacto conductual.

6. **[L-02 — Resto conforme verificado]** Tech verificada (Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54 sin migrar a 2.1, SQLite WAL writer único `busy_timeout 5000`, harness RED por `NotImplementedError`) coincide con `.work/stack-verification.md` y memlog; AD-01..AD-07 heredadas sin renumerar ni debilitar; 3 operaciones + EDGE-01 cubiertas (AD-10 fixture dual `Student` CS101 / `TA` CS-480, rechazo EC-02, sin cuota GPU); dimensiones altitude feature presentes (paradigm, invariants, conventions, stack, seed, capability map, deferred); DENY→403 correctamente separado (dominio `ALLOW|DENY` vs HTTP `ALLOW→200 AuthorizeResponse` / `DENY→403 DenyBody` RFC-7807 + `ExplanationDTO` obligatoria, PRD §5.2 / ARCH §4.2/AD-01) y ya alineado en contracts §0–§1, `dto.py` (`AllowOnly`/`DenyBody`), `openapi.yaml` (`200` solo ALLOW, `403` DenyBody); D-03/D-04/D-06/D-07/D-08/D-09/D-10/D-11 de Amelia verificados cerrados en companions actuales (`CHECK GLOB` ARN, `term` estricto 3×GLOB, `500 Internal` en los 3 paths, `type:["string","null"]`, `RosterRejectedManifest` + `text/csv`, `ErrorCode Literal` 24, `revocation_propagated_at` canónico, contracts §5 con AD-07/08/09).

## Estado de D-01..D-15 de Amelia (solo lectura, al 2026-10-12)

| D | Estado en companions actuales | Nota |
|---|---|---|
| D-01 DENY 200 vs 403 | **Cerrado** (contracts §0–§1, dto `AllowOnly`/`DenyBody`, openapi 200-ALLOW + 403-DenyBody) | Spine AD-09 correcto |
| D-02 403 sin explanation | **Cerrado** (`DenyBody = ErrorBody + decision DENY + explanation`) | — |
| D-03 ARN sin CHECK | **Cerrado** (SQL l.116 `CHECK GLOB`, ports §5) | GLOB aproximado + regex exacta en boundary, documentado |
| D-04 term laxo | **Cerrado** (SQL l.30–34, 3×GLOB SPRING/SUMMER/FALL) | — |
| D-05 audit VIEW vs TABLA | **Cerrado en companions, abierto en spine** (SQL TABLE §7b + ports §4 + events §1) | Ver H-02 |
| D-06 500 sin respuesta | **Cerrado** (`Internal` en los 3 paths) | Emisor fuera de las tres ops, documentado |
| D-07 ErrorBody.code str | **Cerrado** (`ErrorCode Literal[24]`) | — |
| D-08 nullable 3.0 | **Cerrado** (`type: ["string","null"]`) | — |
| D-09 Manifest huérfana | **Cerrado** (`RosterRejectedManifest` + `text/csv` en 422) | — |
| D-10 receipt keys | **Cerrado** (canónico `revocation_propagated_at`, alias documentado) | [OPEN-06] fino pendiente |
| D-11 §5 sin AD-07/08/09 | **Cerrado** (contracts §5 l.133–135 existen) | — |
| D-12 abiertos vestidos de cerrados | **Parcial**: contracts/dto/ports reworded con "propuesto pendiente"; **spine Conventions/AD-12/AD-13 aún instruyen conducta** | Ver H-01/M-01 |
| D-13 predicado sin línea SQL | Reserva honesta [OPEN-05], sin fingir cerrado | — |
| D-14 reason_code/SUCCESS | Abierta honesta [OPEN-04] | — |
| D-15 term dual sin precedencia | Aclaración [OPEN-06], path autoridad | — |

## Condiciones para PASS (triage humano, fuera de este review)

1. Rewording H-01 (OPEN-01) en spine sin instruir `strip+upper` como hecho.
2. H-02: spine refleja TABLA `audit_events` 1:1 + regla timestamp + misma-tx.
3. Confirmar que M-01 queda como propuesta hasta triage de [OPEN-02/03].
4. Nada más: no cerrar NFR como EVIDENCED ni declarar PASS sin Gate Drill con fallo inyectado.
