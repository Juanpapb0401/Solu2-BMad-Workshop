# Reviewer Gate — Ronda 3 Gate 7, G7-01/G7-02/R3-01..R3-06 (corrida 8, 2026-10-13)

**Alcance:** `.work/paquete-decisiones-F-H.md` § "Ronda 3 — triage Gate 7 + restos OPEN dentro de las 3 operaciones" (APROBADO por el estudiante 2026-10-13) aplicado tal cual a `contracts.md` (catálogo 26 códigos, orden 401-primero, P4/R3-02, Q2/R3-06, Q2-Q3/R3-04/R3-05, §5, §6), `ARCHITECTURE-SPINE.md` (AD-09/AD-11/AD-12/AD-13 + Deferred), `ports-and-adapters.md` (§3/§4/§5/§6), `schemas/001_module1.sql` (4 triggers append-only + comentarios G7-01/R3-03/R3-06), `schemas/events.md` (§2/§4), `schemas/dto.py` (enum `ErrorCode` 26 + descripciones), `schemas/openapi.yaml` (enum 26 + 401 en las tres rutas + 422 `application/problem+json`) y `ai-log/decision-log-solu2.md` (8 entradas nuevas). Sin lógica productiva; sin cambios en AD-01..AD-07 ni Plan-2; sin TEA ni `bmad-build`.
**Veredicto oficial de esta corrida: CONDITIONAL (8/8 cierres Ronda-3 verificados tal cual; 2 hallazgos nuevos dentro de `revokeCourseAccess`: R4-01 medio-alto y R4-02 bajo; OBS-8-01 de higiene ya corregido. Fase 1 no se marca completa: requiere triage humano de R4-01/R4-02 y Gate Drill con fallo inyectado, fuera de esta corrida).**

## Resultados por lente (una sola corrida)

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false` — solo los 3 `low` conocidos (placeholders de ruta `{subject_id}`/`{student_id}` en AD-09, línea 65: falsos positivos, son params de ruta documentados) | `reviews/review-lint-20261013-8.json` |
| Rubric walker | **CONDITIONAL** — 8/8 cierres verificados; OBS-8-01 bajo de higiene (stale `[OPEN-10]` STRICT en `dto.py`, ya corregido tras el lens; re-verificado `dto-ok`) | `reviews/review-rubric-20261013-8.md` |
| Web-verification | **PASS** — stack sin cambios, autoridad preservada, triggers solo SQLite estándar, matriz sigue dato | `reviews/review-web-verification-20261013-8.md` |
| Adversarial | **NO ROBUSTO (6/8 cierres sin pares divergentes; 2 hallazgos nuevos R4-01/R4-02, hijos de R3-02)** | `reviews/review-adversarial-20261013-8.md` |

## Qué cambió en esta corrida (Ronda 3, sin reabrir)

1. G7-01 REJECT: `001_module1.sql` es migración inicial sin DB previa; futura 002 debe rellenar `revoked_at` antes del CHECK.
2. G7-02 DEFER a NFR (Test-lead, Fase 3): barrido sin reserva de cola → log WARN estructurado (sin secretos) + métrica `scheduler_sweep_deferred_total`, reintento en el siguiente barrido de 1 s.
3. R3-01: `AUTH_TOKEN_INVALID` → 401 primero (PRD:255); catálogo 26 códigos; 401 en las tres rutas.
4. R3-02: `MALFORMED_DROP_TIMESTAMP` → 400 (mismo paso P3/P4; `MALFORMED_DROP_REASON` primero si ambos fallan; ambos en `rule_ids`); cierra el OPEN F-05 resto.
5. R3-03: `membership.revoked` → `DENY`/`SUBJECT_ENROLLMENT_DROPPED`; `escalation.expired` → `DENY`/`STATUS_ESCALATION_EXPIRED`.
6. R3-04: STRICT = abortar lote completo, sin segregar.
7. R3-05: 422 siempre `application/problem+json`; se ignora `Accept` (anexo CSV vive en el evento, no por negociación).
8. R3-06: orden revoke (validar P1-P4 → `BEGIN IMMEDIATE` → `UPDATE … WHERE status='ACTIVE' RETURNING` + `QueueReservation` → commit → publicar) + 4 triggers append-only (`BEFORE UPDATE`/`BEFORE DELETE` sobre `audit_ledger` y `audit_events` → `RAISE(ABORT, 'append-only')`).
9. Decision-log: 8 entradas G7-01/G7-02/R3-01..R3-06 al final con el formato existente.

## Hallazgos nuevos (serie R4, dentro de las 3 operaciones)

- **R4-01 (medio-alto, hijo de R3-02):** gramática del `timestamp` de baja sin cerrar (dígitos fraccionales y forma de zona no fijados; p. ej. `"2026-09-23T15:04:05Z"` o `"+00:00"` → 400-vs-200 entre dos unidades conformes). Requiere triage humano con gramática explícita; no se inventa aquí.
- **R4-02 (bajo, hijo de R3-02):** colisión `rule_ids`-doble (H-23, vive en `ExplanationDTO`) vs `ErrorBody`-sin-DTO en 400 (F-06, `BadRequest → ErrorBody`): el principal converge (`MALFORMED_DROP_REASON`), pero el segundo código no es observable igual en ambas unidades. Aclaración pendiente, no bloquea.
- **OBS-8-01 (bajo, higiene, YA CORREGIDO):** comentario stale `[OPEN-10] STRICT` en `dto.py` (+ resto `[OPEN-04/09]` de cabecera) tras aplicar R3-04/R3-03; corregido tras el lens rubric con `default.edit` y re-verificado (`dto-ok`, 0 `OPEN` en `dto.py`). No reabre nada.

## Restos DEFERRED declarados (sin divergencia nueva, no bloquean)

Matriz completa (v0 cerrada, resto al equipo de políticas, fail-closed); capacidad de cola y recuperación post-aceptación (Fase 3 NFR, Test-lead); TTL `uai_live_…` y reemisión (dueño de credenciales futuro); `COMPLETED`/`INACTIVE` fuera de las tres operaciones. Sin `OPEN` dentro de las tres operaciones salvo R4-01/R4-02 (triage pendiente).

## Validaciones realmente ejecutadas (esta corrida)

- `lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine` → `ok:false`, 3 `low` conocidos (falsos positivos `{subject_id}`/`{student_id}`, AD-09 línea 65).
- `sqlite3 :memory:` con DDL → 11 tablas + `sqlite_sequence`; 4 triggers (`trg_audit_ledger_no_update/delete`, `trg_audit_events_no_update/delete`); `UPDATE` y `DELETE` sobre `audit_ledger` y sobre `audit_events` fallan con `append-only` (4/4 bloqueados); exit 0.
- `solu2-module1/.venv/bin/python -c "import sys; sys.path.insert(0,'solu2-module1/planning/detailed-design/schemas'); import dto"` → `dto-ok` (26 códigos en `ErrorCode`), exit 0; re-verificado tras la higiene OBS-8-01.
- `cd solu2-module1 && .venv/bin/pytest -q` → `4 passed`; exit 0.
- `openapi.yaml`: 401 presente en las 3 rutas (`/authorize`, `.../drop`, `.../roster`); enum `ErrorBody.code` con 26 códigos (`AUTH_TOKEN_INVALID`, `MALFORMED_DROP_TIMESTAMP` incluidos); `Unprocessable` solo `application/problem+json`.
- Gates 4/5/6/7 y lenses previos sin modificar (solo se agregan archivos `-20261013-8`).
- No ejecutados: TEA, `bmad-build`/`bmad-build-auto`, benchmarks NFR, Gate Drill con fallo inyectado.

## Rutas de esta corrida (archivos nuevos, sin sobrescribir)

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint-20261013-8.json`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-8.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-20261013-8.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-20261013-8.md`
- Este informe: `.../reviews/validation-gate-20261013-8.md`
- Archivos cambiados (solo estos 8): `solu2-module1/planning/detailed-design/contracts.md`, `.../architecture-spine/ARCHITECTURE-SPINE.md`, `.../ports-and-adapters.md`, `.../schemas/001_module1.sql`, `.../schemas/events.md`, `.../schemas/dto.py`, `.../schemas/openapi.yaml`, `solu2-module1/ai-log/decision-log-solu2.md` (+ 2 líneas de evento en `.../architecture-spine/.memlog.md`)
- Gates 4/5/6/7 intactos y vigentes (`validation-gate-20261013-4.md`, `-20261013-5.md`, `-20261013-6.md`, `-20261013-7.md` + lenses).
