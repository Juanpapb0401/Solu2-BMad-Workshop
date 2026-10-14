# Reviewer Gate — Sync Fase 2 Amelia (corrida 5, 2026-10-13)

**Alcance:** los 5 companions Fase 2 actualizados (`ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml`) contra `contracts.md`, `ARCHITECTURE-SPINE.md`, `resultados-interaccion.md` (auditoría Amelia) y Gate 4. Sin lógica productiva; sin cambios en AD-01..AD-07 ni Plan-2; sin TEA ni `bmad-build`.
**Veredicto oficial de esta corrida: NO PASS (por diseño: F-01..F-06 y H-14..H-26 siguen OPEN; Gate 4 original sigue NO PASS; Fase 1 no se marca completa).**

## Resultados por lente (una sola corrida)

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false` — solo los 3 `low` conocidos (placeholders de ruta) | `reviews/review-lint-20261013-5.json` |
| Rubric walker | **CONDITIONAL** — delta Fase 2 correcto; F-01..F-06 + H-14..H-26 siguen OPEN por diseño | `reviews/review-rubric-20261013-5.md` |
| Web-verification | **PASS** — stack sin cambios, autoridad preservada | `reviews/review-web-verification-20261013-5.md` |
| Adversarial | **NO ROBUSTO (H-14..H-26 persisten OPEN por diseño; 0 cierres nuevos; 1 tensión pre-existente H-21c registrada)** | `reviews/review-adversarial-20261013-5.md` |

## Qué cambió en esta corrida (documental mínimo, sin cerrar)

1. Codec parcialmente definido + OPEN H-14/H-15 explícitos en `events.md:§3`, `ports-and-adapters.md:§4` y comentarios DDL; sin elegir opción.
2. OPEN H-16 explícito (momento `request_now` + reuse en `roster.rejected`) en `events.md:§1` y `ports-and-adapters.md:§3-§4`.
3. H-17..H-26 marcados OPEN en los artefactos correspondientes, sin fijar precedencias ni comportamientos indefinidos.
4. OpenAPI: matriz `term` (JSON↔body, CSV↔query; ausente/extra/duplicado/discrepante → `MALFORMED_TERM` 400) + brecha contrato/prueba declarada; `subject_id` path autoridad (`MALFORMED_BATCH` si difiere); 422 OPEN sin `Accept` por defecto.
5. `dto.py:RosterRejectedManifest` añadido y alineado al contrato 422 (RFC-7807 + `errors` + `batch_id` + `explanation` + conteos; solo tipa, sin lógica ni validadores nuevos).
6. `drop_reason` con OPEN H-19 (blancos + intacto-vs-máscara), sin validador nuevo (`Field`/`minLength` no enforcean).
7. DDL: separación físico (FK una dirección `audit_events → audit_ledger`, `CHECK`/`GLOB` reales) vs conductual (igualdad de timestamps y atomicidad del `LedgerWriter`, sin `CHECK`/trigger); 0 triggers; sin restricciones nuevas.
8. IDs/email sin patrones inventados (boundary valida; pendiente lo no definido).

## Pendientes que sostienen el NO PASS (sin inventar)

F-01..F-06; matriz `roles_matrix.json` (equipo fuente de políticas); capacidad y recuperación de cola; frecuencia y crash del scheduler; ubicación HTTP del `timestamp` de baja; TTL `uai_live_…`; `COMPLETED`; NFR (PLANNED, sin EVIDENCED); reemisión de credenciales; colisión `batch_id`. Tensión pre-existente H-21c (DDL heredado `expires_at > granted_at` vs vacío) registrada sin decidir.

## Validaciones realmente ejecutadas (esta corrida)

- `lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine` → `ok:false`, 3 `low` conocidos (placeholders `{subject_id}`/`{student_id}`).
- `python3 -c ast.parse(dto.py)` → OK; 12 clases (incl. `RosterRejectedManifest`); 0 funciones (sin lógica).
- `sqlite3 :memory: executescript(001_module1.sql)` → OK; 9 tablas + `sqlite_sequence`; `audit_events` 1 FK → `audit_ledger`; 0 triggers.
- `ruby Psych.load_file(openapi.yaml)` → OK.
- `grep H-14..H-26` en los 5 artefactos → cada H presente al menos en su artefacto correspondiente; Gate 4 (`*20261013-4*`) sin modificar (mtimes intactos).
- No ejecutados: TEA, `bmad-build`/`bmad-build-auto`, benchmarks NFR, Gate Drill con fallo inyectado.

## Rutas de esta corrida (archivos nuevos, sin sobrescribir)

- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint-20261013-5.json`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-rubric-20261013-5.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-web-verification-20261013-5.md`
- `solu2-module1/planning/detailed-design/architecture-spine/reviews/review-adversarial-20261013-5.md`
- Este informe: `solu2-module1/planning/detailed-design/architecture-spine/reviews/validation-gate-20261013-5.md` (+ `.html` gemelo)
- Archivos cambiados (solo estos 5): `solu2-module1/planning/detailed-design/ports-and-adapters.md`, `solu2-module1/planning/detailed-design/schemas/001_module1.sql`, `solu2-module1/planning/detailed-design/schemas/dto.py`, `solu2-module1/planning/detailed-design/schemas/events.md`, `solu2-module1/planning/detailed-design/schemas/openapi.yaml`
- Gate 4 original intacto y vigente: `.../reviews/validation-gate-20261013-4.md` (+ `.html`) y lenses `-20261013-4` → NO PASS; Fase 1 no completa.
