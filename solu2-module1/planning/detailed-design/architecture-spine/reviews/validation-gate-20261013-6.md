# Reviewer Gate — Paquete estudiante F/H (corrida 6, 2026-10-13)

**Alcance:** paquete `.work/paquete-decisiones-F-H.md` (APROBADO por el estudiante, 19 decisiones F/H + 6 pendientes) aplicado a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml`, más `schemas/roles_matrix.v0.json` (dato) y `ai-log/decision-log-solu2.md` (25 entradas). Sin lógica productiva; sin cambios en AD-01..AD-07 ni Plan-2; sin TEA ni `bmad-build`.
**Veredicto oficial de esta corrida: NO PASS (CONDITIONAL — 19/19 cierres F/H verificados; 2 esquinas nuevas G6-01/G6-02 a triage; Fase 1 no se marca completa).**

## Resultados por lente (una sola corrida)

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false` — solo los 3 `low` conocidos (placeholders de ruta `{subject_id}`/`{student_id}`) | `reviews/review-lint-20261013-6.json` |
| Rubric walker | **CONDITIONAL** — 19/19 cierres verificados; G6-01/G6-02 nuevos a triage | `reviews/review-rubric-20261013-6.md` |
| Web-verification | **PASS** — stack sin cambios, autoridad preservada, matriz es dato | `reviews/review-web-verification-20261013-6.md` |
| Adversarial | **NO ROBUSTO (2 pares nuevos G6-01/G6-02; H-14..H-26 cierran en su alcance)** | `reviews/review-adversarial-20261013-6.md` |

## Qué cambió en esta corrida (decisiones del paquete, sin reabrir)

1. F-01: sintaxis P3 primero en replay (`drop_reason` inválido → 400 aunque esté `DROPPED`).
2. F-02: matriz v0 como dato (`roles_matrix.v0.json`, 3 filas citadas); resto DEFERRED negando.
3. F-03/H-17: precedencias intra-paso 404/403 fijadas.
4. F-04: frontera `batch_id` + `UNIQUE roster_batches.batch_id` + reintento x3 → 503; 400/401/413 sin `batch_id`.
5. F-05: `timestamp` de baja en body (informativo, Clock efectivo); formato inválido → OPEN sin código.
6. F-06: 500 con `ErrorBody` sin DTO; escalación fuera de alcance.
7. H-14/H-15: codec SOLO 8 campos, decimal UTF-8, génesis 64 `0`, bytes UTF-8.
8. H-16: `request_now` pre-auth + reuse en `roster.rejected`.
9. H-18: decode-once + exacto; path exacto o 404.
10. H-19: blancos `str.isspace()`; máscara AD-06 sobre intacto.
11. H-20: scope cualquier estado + no-reactiva-`DROPPED`.
12. H-21: intervalo/REVOKED mandan; futuro → base; vacío imposible por DDL.
13. H-22: una tx de lectura + caché solo-DENY + 503 solo `busy_timeout`.
14. H-23: `rule_ids` todas ordenadas, primero = principal.
15. H-24: repetido/vacío = ausente; valor del parser.
16. H-25: pureza ampliada (toda no-determinación).
17. H-26: `effective_role` = `roles.id` exacto.
18. Scheduler 1 s + crash `UPDATE … RETURNING` + 1 evento/transición; `COMPLETED` DENY sin productor.
19. DEFERRED con responsable/fase: cola y TTL/reemisión (spine Deferred); matriz resto (políticas).

## Hallazgos nuevos (a triage, fuera del paquete)

- **G6-01 (media-baja):** replay vs ticket REVOKED — H-21a invoca "revoked_at" inexistente en DDL (solo `status`); dos unidades conformes divergen.
- **G6-02 (baja-media):** evento del scheduler tras crash — frontera tx del evento (misma tx vs post-commit) sin fijar; 1 vs 0 eventos ante crash intermedio.

## Restos OPEN/DEFERRED declarados (sin divergencia nueva)

Código para `timestamp` inválido (F-05 resto); `decision`/`reasonCode` de `membership.revoked`; STRICT vs cuarentena; negociación 422 JSON/CSV; CODE 401; matriz completa; cola/TTL (DEFERRED con defaults seguros 503/DENY).

## Validaciones realmente ejecutadas (esta corrida)

- `lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine` → `ok:false`, 3 `low` conocidos (placeholders `{subject_id}`/`{student_id}`).
- `python -c "import sys; sys.path.insert(0,'solu2-module1/planning/detailed-design/schemas'); import dto"` → exit 0, sin salida.
- `sqlite3 :memory:` con DDL → 10 tablas (`roster_batches` incluida) + `sqlite_sequence`; 0 triggers; exit 0.
- `roles_matrix.v0.json` → `matrix-ok v0 3` citas; exit 0.
- `cd solu2-module1 && .venv/bin/pytest -q` → `4 passed`; exit 0.
- Gates 4/5 y lenses previos sin modificar (solo se agregan archivos `-20261013-6`).
- No ejecutados: TEA, `bmad-build`/`bmad-build-auto`, benchmarks NFR, Gate Drill con fallo inyectado.

## Rutas de esta corrida (archivos nuevos, sin sobrescribir)

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint-20261013-6.json`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-6.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-20261013-6.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-20261013-6.md`
- Este informe: `.../reviews/validation-gate-20261013-6.md` (+ `.html` gemelo)
- Archivos cambiados (solo estos 9): `solu2-module1/planning/detailed-design/contracts.md`, `.../architecture-spine/ARCHITECTURE-SPINE.md`, `.../ports-and-adapters.md`, `.../schemas/001_module1.sql`, `.../schemas/dto.py`, `.../schemas/events.md`, `.../schemas/openapi.yaml`, `.../schemas/roles_matrix.v0.json` (nuevo), `solu2-module1/ai-log/decision-log-solu2.md` (nuevo)
- Gates 4/5 intactos y vigentes (`validation-gate-20261013-4.md`, `-20261013-5.md` + lenses).
