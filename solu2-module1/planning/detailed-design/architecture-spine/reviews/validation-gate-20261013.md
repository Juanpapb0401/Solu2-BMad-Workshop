# Validation Gate — Architecture Spine + companions (2026-10-13)

**Alcance:** `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (status: draft) y companions, incluido `contracts.md` con los cambios Fase 1 desde `resultados-interaccion.md`.
**Intención:** Validate — solo lectura; ningún artefacto fue editado, ningún [OPEN] fue cerrado, sin lógica ni `bmad-build`.
**Veredicto oficial del gate: NO PASS.** El spine permanece en `draft`; no pasar a Fase 3.

## Resultados por lente

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista (`lint_spine.py`) | `ok:false` — solo 3 hallazgos `low`, falsos positivos por params de ruta `{subject_id}`/`{student_id}` en l.65 del spine | salida en consola (sin archivo nuevo; ver `reviews/review-lint-20261013.md` como referencia previa) |
| Rubric walker (good-spine checklist) | **CONDITIONAL** — sin AD debilitados, sin decisiones inventadas, sin invariante sin enforcement/test; OPENs correctamente dejados abiertos | `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-validate-20261013.md` |
| Web-verification del stack | **PASS** — FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54 vigentes en vivo (PyPI, 2026-10-13); Python 3.11+, SQLite WAL, pytest/hypothesis sin bloqueantes; NFR siguen `PLANNED` (correcto) | `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-validate-20261013.md` |
| Adversarial | **NO ROBUSTO (6 pares)** — 5 ya documentados como [OPEN], 1 faceta nueva (case de `userId`/`term`) para triage | `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-validate-20261013.md` |

## Hallazgos que aún bloquean (ninguno nuevo salvo faceta indicada)

1. **[OPEN-01]** Normalización `strip+upper` vs AD-01 crudo byte-a-byte (`contracts.md` §0/P2/P5, spine Conventions l.96). Par adversarial P-01. Requiere triage humano.
2. **[OPEN-02]** Caché de revocación vs DB-autoridad (spine AD-12, `contracts.md` §1 Concurrencia). Par P-02. Requiere triage humano.
3. **[OPEN-03]** Scheduler interno (PRD §4.2 R5) vs expiración perezosa (spine AD-13). Par P-03. Requiere triage humano.
4. **[OPEN-04]** Ledger en rechazo (422/DENY P1-P4), `reason_code` de éxito (`SUCCESS` vs catálogo), fórmula hash exacta, emisor 500. Par P-04 + contradicción Q-fail vs Q3 conservada abierta.
5. **[OPEN-05]** Predicado single-statement vs `BEGIN IMMEDIATE`, bound de cola async, fail-closed `SQLITE_BUSY`. Par P-05.
6. **[OPEN-06/07/09/10]** Transporte `at`/`term`, matriz AuthN 401, `COMPLETED`/`INACTIVE`, TTL `uai_live_…`, matriz rol×acción, NFR `PLANNED`. Par P-06.
7. **Faceta NUEVA (triage):** case de `userId`/`institutional_id` y `term` (`stu-98432`/`2026-fall`) no cubierta por [OPEN-01], hoy scopeado solo a `courseId`. Ver reporte adversarial §P-06.
8. **Reingesta** correctamente degradada a [ASSUMPTION]/[OPEN] (`contracts.md` §6); comportamiento sin decidir hasta acuerdo del equipo.

## Verificación de los cambios Winston (Fase 1)

- Autoridad `AD-01..AD-07` heredados vs `AD-08..AD-13` spine-local etiquetada en header, `Bound to`, Q y §5 — conforme, sin renumerar.
- §3 I2 solo AD-02 (ARCH l.343); AD-05 removido de ingest — conforme a fuente.
- §2 I3 + fila §5 citan PRD §7.3 l.329-330 junto a AD-03 — conforme a fuente.
- §1 I4 sin cuota GPU/prioridad (AD-10 spine-local l.71 + PRD [ASSUMPTION-01]) — conforme a fuente.
- Exclusión mutua de escalaciones marcada fuera de alcance (sin P/Q/I, no es una de las tres ops) — conforme.
- Sin punteros exactos inventados — conforme.
- Los reportes anteriores **no** validan esta versión; este gate la evaluó de nuevo y el veredicto sigue siendo **NO PASS**.

## Rutas de los reportes de esta corrida

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-validate-20261013.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-validate-20261013.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-validate-20261013.md`
- Este informe: `solu2-module1/planning/detailed-design/architecture-spine/reviews/validation-gate-20261013.md` (+ `.html` gemelo)

**Siguiente paso propuesto (no ejecutado):** llevar los 8 puntos a triage humano; solo después, un Update puntual (p.ej. extender [OPEN-01] a `userId`/`term`) y re-gate.
