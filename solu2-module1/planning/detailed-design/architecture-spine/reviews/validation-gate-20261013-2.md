# Reviewer Gate — Fase 1 con 8 decisiones [ADOPTED] 2026-10-13 (corrida 2)

**Alcance:** `ARCHITECTURE-SPINE.md` + `contracts.md` (versión con D1–D8) y memlog (52 entradas de contexto + 10 de esta pasada).
**Veredicto oficial del gate: NO PASS.** Fase 1 sigue sin resultado aceptable; no se marca completa.

## Resultados por lente (una sola corrida)

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false` — solo los 3 `low` conocidos (falsos positivos `{subject_id}`/`{student_id}`, l.65) | `reviews/review-lint-20261013-2.json` |
| Rubric walker | **ROBUSTO** + 4 observaciones no bloqueantes (etiqueta `[OPEN-01]` residual junto a regla ya adoptada; `updated: 2026-10-12` desactualizado; plantilla `INVALID_AT` dice "Query instant" aunque `at` va en body; convención `roster:ingest` vs `roster.rejected`) | `reviews/review-rubric-20261013-2.md` |
| Web-verification | **PASS** — Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL, pytest/hypothesis vigentes | `reviews/review-web-verification-20261013-2.md` |
| Adversarial | **NO ROBUSTO (16 pares nuevos N-01..N-16)**; 14 frentes ya cubiertos por decisiones/OPEN | `reviews/review-adversarial-20261013-2.md` |

## Decisiones aplicadas en esta pasada (todas [ADOPTED], detalle en memlog)

- D1 Hash normativo AD-04 §5 (con `subject_id`/`action`); resumen §2 incompleto. Sin editar Plan-2.
- D2 Transporte: `at` en body JSON de authorize (opcional); `term` en query (CSV) / campo body (JSON).
- D3 Roster 422: rollback total, luego evento `roster.rejected` en tx separada; cola no acepta → 503.
- D4 Cola: micro-batching 50 ms/50 ev sin descarte; llena → 503; capacidad y recuperación pendientes (TEA/NFR).
- D5 Reingesta sin idempotencia por contenido; `batch_id` nuevo; regeneración de credenciales pendiente.
- D6 Scheduler auto-revoca + guarda `now >= expires_at` aunque no haya persistido; frecuencia pendiente (TEA/NFR).
- D7 Post-revocación unificado a `403 SUBJECT_ENROLLMENT_DROPPED` (PRD admite 401/403).
- D8 UUID formato estándar; espacios externos rechazados sin recorte; case UUID pendiente.

## Bloqueantes reales del gate (pendientes de triage humano)

- N-01 serialización hash DDL/adapter vs contrato; N-02 `at` ausente vs inválido; N-03 `term` query vs body en desacuerdo; N-04 ventana 422 vs commit de `roster.rejected`; N-05 cadena única vs separada + `audit_events` 1:1; N-06 cola llena con decisión/mutación comprometida; N-07 doble dueño de expiración (quién muta, cuántos eventos); N-08 `at` histórico vs `now`; N-09 precedencia 401 vs 403 concurrentes; N-10 orden UUID vs `institutional_id`, blancos internos, CODE; N-11 reingesta concurrente (doble `batch_id`, conteos, colisión `<8hex>`); N-12 header vs path subject en revoke/ingest; N-13 case de email-domain + folding de `seen_ids`; N-14 5 MB / 400 vs 413 / chars vs bytes en `drop_reason`; N-15 replay `ALREADY_REVOKED` vs P3 y `ExplanationDTO` en 400/401/404; N-16 `BEGIN IMMEDIATE` vs predicado, `busy_timeout`, orden del micro-batching. Detalle en el reporte adversarial.
- Pendientes previos intactos: matriz rol×acción (`roles_matrix.json` inexistente; responsable: equipo fuente de políticas; bloquea criterios por acción), capacidad de cola, recuperación post-persistencia, frecuencia del scheduler, ubicación HTTP del `timestamp`, `COMPLETED`, TTL `uai_live_…`, datasets NFR, regeneración de credenciales, case UUID.

## Sincronización Fase 2 (registrada en memlog, no aplicada)

`openapi.yaml` (at body, term query/body, ejemplos 403, formato UUID, timestamp cuando se resuelva) + `dto.py` + `events.md` (`roster.rejected`, `SUCCESS`, fórmula normativa) + `001_module1.sql` (comentario fórmula) + `ports-and-adapters.md` (transporte, cola, frecuencia). Ver entrada `direction` del memlog.

## Rutas de esta corrida (archivos nuevos, sin sobrescribir previos)

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint-20261013-2.json`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-2.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-20261013-2.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-20261013-2.md`
- Este informe: `.../reviews/validation-gate-20261013-2.md` (+ `.html` gemelo)
