# Reviewer Gate — Ronda 4 Gate 8, R4-01/R4-02 (corrida 9, 2026-10-13)

**Alcance:** `.work/paquete-decisiones-F-H.md` § "Ronda 4" (R4-01, R4-02, aprobados por el estudiante 2026-10-13) aplicados a `contracts.md`, `ARCHITECTURE-SPINE.md` (AD-11), `ports-and-adapters.md`, `schemas/dto.py`, `schemas/openapi.yaml`, más 2 entradas en `ai-log/decision-log-solu2.md` y 1 entrada en el memlog. Sin cambios en AD-01..AD-07 ni en `planning/`. Sin TEA ni `bmad-build`.

**Veredicto oficial de esta corrida: CONDITIONAL.** Las dos decisiones R4 están aplicadas con su marca. El lens adversarial da NO ROBUSTO: tres divergencias dentro de las 3 operaciones bloquean (G9-01 gramática residual, G9-02 precedencia de ingest, G9-03 `rule_ids` null vs ausente). No se marca Fase 1 completa.

## Resultados por lente

| Lente | Veredicto | Reporte |
| --- | --- | --- |
| Lint determinista | `ok:false`, solo los 3 `low` conocidos (placeholder `{subject_id}`/`{student_id}`, l.65): falsos positivos | `reviews/review-lint-20261013-9.json` |
| Rubric walker | **CONDITIONAL** (R4 aplicadas; G9-03 bloquea; G9-04 bajo) | `reviews/review-rubric-20261013-9.md` |
| Web-verification | **PASS** (stack sin cambios); la norma RFC 3339 confirma los residuos de G9-01 | `reviews/review-web-verification-20261013-9.md` |
| Adversarial | **NO ROBUSTO** (G9-01 y G9-02 medio-alto/medio, bloquean; G9-03 medio, bloquea; G9-05 y G9-06 bajos) | `reviews/review-adversarial-20261013-9.md` |

## Hallazgos nuevos (serie G9)

- **G9-01 (medio-alto, BLOQUEA):** gramática de timestamp de baja incompleta frente a RFC 3339: minúsculas `t`/`z`, `-00:00`, segundo 60, fecha fuera de calendario, fracción de 7+ dígitos y su normalización.
- **G9-02 (medio, BLOQUEA):** en `ingestRoster` no hay precedencia entre `MALFORMED_TERM` y `MALFORMED_BATCH`/`BATCH_EMPTY`; R4-02 exige "el primero == code".
- **G9-03 (medio, BLOQUEA):** `ErrorBody.rule_ids` ausente se serializa como `null` (reproducido con `model_dump_json()`), contrario a "presente solo cuando" y a OpenAPI no nullable. Patrón preexistente en `ExplanationDTO.threshold`.
- **G9-04 (bajo, NO BLOQUEA):** "ISO-8601 UTC" residual en contracts l.32/61/117/166, AD-09 l.65, ports l.158, openapi l.229, dto l.15/164.
- **G9-05 (bajo, NO BLOQUEA):** `rule_ids` reutilizado en `ExplanationDTO` (AD-n) y `ErrorBody` (códigos).
- **G9-06 (bajo, NO BLOQUEA, preexistente):** `POST /authorize` con body incompleto no tiene código 400 en el catálogo.

## Validaciones realmente ejecutadas (esta corrida)

- `lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine --output .../review-lint-20261013-9.json` → exit 0, `ok:false`, 3 `low` conocidos.
- `cd solu2-module1 && .venv/bin/python -c "import sys; sys.path.insert(0,'planning/detailed-design/schemas'); import dto; print('dto-ok')"` → `dto-ok`, exit 0.
- `sqlite3 :memory: < planning/detailed-design/schemas/001_module1.sql && echo ddl-ok` → `memory`, `5000`, `ddl-ok`, exit 0.
- `.venv/bin/python -c "import yaml" 2>/dev/null || ruby -ryaml ... openapi.yaml` → `yaml-ok`, exit 0.
- `cd solu2-module1 && .venv/bin/pytest -q` → `4 passed in 0.07s` (aviso de deprecación de pytest-asyncio, no es fallo).
- `memlog.py append --type decision` → `{"ok": true, ..., "entries": 106}`.
- Verificación de serialización (G9-03): `ErrorBody(...).model_dump_json()` → incluye `"rule_ids":null` cuando no se pasa el campo.

## No ejecutados

TEA, `bmad-build`/`bmad-build-auto`, benchmarks NFR, Gate Drill con fallo inyectado. Revisión sin subagentes independientes (inline por el mismo agente que aplicó los cambios).

## Archivos de esta corrida

- Cambiados: `solu2-module1/planning/detailed-design/contracts.md`, `.../architecture-spine/ARCHITECTURE-SPINE.md`, `.../ports-and-adapters.md`, `.../schemas/dto.py`, `.../schemas/openapi.yaml`, `solu2-module1/ai-log/decision-log-solu2.md` (2 entradas), `.../architecture-spine/.memlog.md` (1 entrada).
- Nuevos: `reviews/review-lint-20261013-9.json`, `reviews/review-rubric-20261013-9.md`, `reviews/review-web-verification-20261013-9.md`, `reviews/review-adversarial-20261013-9.md`, `reviews/validation-gate-20261013-9.md`.
- No tocados: gates 2–8, `reviews/` anteriores, `.github/`, `scripts/`, `test/ci-quality-gate.md`, `test/nfr-evidence.md`.
