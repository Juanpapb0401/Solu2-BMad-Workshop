# Reviewer Gate — Ronda 2 Gate 6, G6-01/G6-02/R2-01 (corrida 7, 2026-10-13)

**Alcance:** `.work/paquete-decisiones-F-H.md` § "Ronda 2 — hallazgos del Gate 6" (APROBADO por el estudiante 2026-10-13) aplicado a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py` (N/A, sin modelo de ticket), `schemas/events.md`, `schemas/openapi.yaml` (N/A, sin modelo de ticket), `schemas/roles_matrix.v0.json` y `ai-log/decision-log-solu2.md` (3 entradas nuevas). Sin lógica productiva; sin cambios en AD-01..AD-07 ni Plan-2; sin TEA ni `bmad-build`.
**Veredicto oficial de esta corrida: CONDITIONAL (3/3 cierres Ronda-2 verificados; 2 observaciones bajas nuevas no bloqueantes; DEFERRED/OPEN previos intactos). Fase 1 no se marca completa (requiere triage humano de G7-01/G7-02 y Gate Drill con fallo inyectado, fuera de esta corrida).**

## Resultados por lente (una sola corrida)

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false` — solo los 3 `low` conocidos (placeholders de ruta `{subject_id}`/`{student_id}` en AD-09, línea 65: falsos positivos, son params de ruta documentados) | `reviews/review-lint-20261013-7.json` |
| Rubric walker | **CONDITIONAL** — 3/3 cierres verificados; G7-01/G7-02 bajos no bloqueantes | `reviews/review-rubric-20261013-7.md` |
| Web-verification | **PASS** — stack sin cambios, autoridad preservada, matriz es dato | `reviews/review-web-verification-20261013-7.md` |
| Adversarial | **ROBUSTO (0 pares divergentes nuevos; G7-01/G7-02 observaciones bajas)** | `reviews/review-adversarial-20261013-7.md` |

## Qué cambió en esta corrida (Ronda 2, sin reabrir)

1. G6-01: columna `escalation_tickets.revoked_at` + `CHECK ((status <> 'REVOKED') OR (revoked_at IS NOT NULL))`; replay con ticket `REVOKED` en `[granted_at, min(expires_at, revoked_at))`; `at >= revoked_at` → no aplica.
2. G6-02: transición `ACTIVE→EXPIRED` con `QueueReservation` (reserva pre-commit, publica post-commit) + reconciliación tras crash (un `escalation.expired` por ticket `EXPIRED` sin evento, idempotente por id; exactamente 1 evento por transición); tipo `escalation.expired` admitido en DDL y documentado en `events.md` §2.
3. R2-01: matriz v0 con `roles.id` exactos (`student`, `student`, `instructor_privileged`); 0 conflictos con el DDL; citas PRD intactas.
4. Decision-log: 3 entradas G6-01/G6-02/R2-01 con el formato existente.

## Hallazgos nuevos (serie G7, bajos, no bloquean)

- **G7-01 (bajo):** `REVOKED` con `revoked_at` NULL solo posible en DB migrada desde DDL anterior (sin ruta de migración en alcance). OPEN.
- **G7-02 (bajo):** observabilidad de cola llena durante el barrido (log/métrica sin fijar; exactamente-1 preservado por reintento en el siguiente barrido). OPEN.

## Restos OPEN/DEFERRED declarados (sin divergencia nueva)

Código para `timestamp` inválido (F-05 resto); `decision`/`reasonCode` de `membership.revoked` y `escalation.expired`; STRICT vs cuarentena; negociación 422 JSON/CSV; CODE 401; matriz completa; cola/TTL (DEFERRED con defaults seguros 503/DENY).

## Validaciones realmente ejecutadas (esta corrida)

- `lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine` → `ok:false`, 3 `low` conocidos (falsos positivos `{subject_id}`/`{student_id}`, AD-09 línea 65).
- `sqlite3 :memory:` con DDL → 11 tablas (`roster_batches` incluida) + `sqlite_sequence`; columna `revoked_at` presente; `escalation.expired` en el `CHECK` de `audit_events`; 0 triggers; exit 0.
- `solu2-module1/.venv/bin/python -c "import sys; sys.path.insert(0,'solu2-module1/planning/detailed-design/schemas'); import dto"` → `dto-ok`, exit 0.
- `roles_matrix.v0.json` → `matrix-ok v0 3` roles ⊆ `roles.id` del DDL, con citas; exit 0.
- `cd solu2-module1 && .venv/bin/pytest -q` → `4 passed`; exit 0.
- Gates 4/5/6 y lenses previos sin modificar (solo se agregan archivos `-20261013-7`).
- No ejecutados: TEA, `bmad-build`/`bmad-build-auto`, benchmarks NFR, Gate Drill con fallo inyectado.

## Rutas de esta corrida (archivos nuevos, sin sobrescribir)

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint-20261013-7.json`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-7.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-20261013-7.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-20261013-7.md`
- Este informe: `.../reviews/validation-gate-20261013-7.md`
- Archivos cambiados (solo estos 7): `solu2-module1/planning/detailed-design/contracts.md`, `.../architecture-spine/ARCHITECTURE-SPINE.md`, `.../ports-and-adapters.md`, `.../schemas/001_module1.sql`, `.../schemas/events.md`, `.../schemas/roles_matrix.v0.json`, `solu2-module1/ai-log/decision-log-solu2.md` (+ línea de evento en `.../architecture-spine/.memlog.md`; `dto.py`/`openapi.yaml` N/A sin cambios)
- Gates 4/5/6 intactos y vigentes (`validation-gate-20261013-4.md`, `-20261013-5.md`, `-20261013-6.md` + lenses).
