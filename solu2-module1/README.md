# Solu-2 — Módulo 1: índice de entrega

Módulo 1 (User, Role, and Subject Access Manager) del taller Solu-2. Alcance: las tres operaciones del Annex A (p. 13) — `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`.

**Estado:** stop-point de solutioning. Hay diseño, contratos, pruebas ATDD intencionalmente RED e interfaces/stubs. No hay lógica productiva (`app/application/module1.py` y los adaptadores lanzan `NotImplementedError`). No se ejecutó `bmad-build` ni `bmad-build-auto`. Ningún NFR está `EVIDENCED`. Repositorio Git local con el tag `solu2-ready`.

Rutas relativas a `solu2-module1/`. Todo el paquete está bajo esta carpeta.

> **Ojo:** `../planning/readiness-gate-report.md` (raíz del repo) es el informe **del Plan-2**, no de Solu-2. El readiness gate de Solu-2 es `planning/readiness-gate-report.md` (dentro de `solu2-module1/`).

## Índice de entrega (paquete sugerido, consigna pág. 11)

| Ítem de la consigna | Ruta en esta entrega | Nota |
|---|---|---|
| `planning/prd.md` | `planning/prd.md` | Copia de entrega de `../planning/prd.md` (fuente Plan-2, sin editar salvo hallazgos triageados). |
| `ARCHITECTURE.md` (v2) | `planning/ARCHITECTURE.md` | Copia de entrega de `../planning/ARCHITECTURE.md`: v2 con Stack Decisions y enlaces v2. AD-01..AD-07 intactos. |
| `detailed-design/contracts.md` | `planning/detailed-design/contracts.md` | P/Q/I de las tres operaciones. |
| `detailed-design/ports-and-adapters.md` | `planning/detailed-design/ports-and-adapters.md` | Cada componente una vez, con etiqueta de capa. |
| `schemas/001_module1_schema.sql` | `planning/detailed-design/schemas/001_module1_schema.sql` | DDL SQLite (renombrado desde `001_module1.sql`). |
| `schemas/dto.py` | `planning/detailed-design/schemas/dto.py` | DTO Pydantic v2 (contrato, sin lógica). |
| `schemas/events.md` | `planning/detailed-design/schemas/events.md` | Eventos y envelope. |
| `schemas/openapi.yaml` | `planning/detailed-design/schemas/openapi.yaml` | Contrato HTTP. |
| (complementario) `schemas/roles_matrix.v0.json` | `planning/detailed-design/schemas/roles_matrix.v0.json` | Matriz rol×acción v0 con filas citadas. |
| `epics.md` (Given/When/Then, DoD) | `planning/epics.md` | Backlog: 4 épicas, 16 historias. |
| `readiness-gate-report.md` (salida + sign-off + gate drill) | `planning/readiness-gate-report.md` | Historial de 9 corridas, sign-off y Gate Drill. |
| `implementation-artifacts/sprint-status.yaml` | `implementation-artifacts/sprint-status.yaml` | Generado tras la corrida 9 (READY). |
| `test/test-design.md` | `test/test-design.md` | Riesgos P0–P3 y niveles de prueba. |
| `test/atdd/<module>_contracts.test.py` | `test/atdd/module1_contracts.test.py` (+ `module1_resolve_contracts.test.py`, `module1_revoke_contracts.test.py`, `module1_ingest_contracts.test.py`, `module1_ingest_rules_contracts.test.py`, `module1_guard_contracts.test.py`) | Suite RED: 130 `xfail` estrictos con `NotImplementedError` + 21 guardas. |
| `test/fixtures/` | `test/fixtures/README.md` | Dónde viven las fixtures obligatorias y los test doubles. |
| `test/nfr-evidence.md` | `test/nfr-evidence.md` | Todos `PLANNED`. |
| `test/traceability-matrix.md` | `test/traceability-matrix.md` | Trazabilidad P0 y AD. |
| `test/ci/quality-gate.yml` | `test/ci/quality-gate.yml` | Copia de `.github/workflows/quality-gate.yml` (plantilla sin activar). |
| `reviews/review-arch-implementability.md` | `reviews/review-arch-implementability.md` | Copia; fuente canónica en `planning/detailed-design/reviews/`. |
| `reviews/review-detailed-design.md` | `reviews/review-detailed-design.md` | Copia; fuente canónica en `planning/detailed-design/reviews/`. |
| `reviews/review-test-quality.md` | `reviews/review-test-quality.md` | Revisión de calidad de pruebas. |
| `ai-log/decision-log-solu2.md` | `ai-log/decision-log-solu2.md` | Resumen en formato de la consigna al inicio, herramientas y gobernanza, y registro de cada decisión. |

Evidencia adicional: `test/evidence/gate-drill.md` (Gate Drill), `test/test-review.md` (revisión de calidad completa con sus re-revisiones), `planning/detailed-design/architecture-spine/` (spine, memlog y reviews de los gates de arquitectura).

## Cómo correr

```bash
cd solu2-module1 && .venv/bin/pytest -q
bash scripts/quality_gate.sh
```

Resultado vigente: `pytest -q` → 25 passed, 130 xfailed (155 nodos: 130 ATDD RED + 21 guardas + 4 de harness). `quality_gate.sh` → GATE LOCAL VERDE; las pruebas ATDD están en RED esperado y la cobertura es informativa.

## Estado honesto de cada gate

| Gate | Resultado | Evidencia |
|---|---|---|
| Reviewer Gates de arquitectura (9 corridas) | Corridas 1–6: NO PASS. Corridas 7–9: CONDITIONAL. Veredicto final: **CONDITIONAL**. | `planning/detailed-design/architecture-spine/reviews/validation-gate-20261013*.md`. Tras la corrida 9 se cerró la iteración por decisión del estudiante. El gate de Fases 1–2 de la consigna es el review final de diseño. |
| Review final de diseño | 55 hallazgos (25 adversariales + 30 edge cases) → **42 ACCEPT / 6 DEFER / 7 REJECT**, tras la Ronda 6b. Aplicados en artefactos. | `planning/detailed-design/reviews/review-detailed-design.md` |
| TEA trace (`bmad-testarch-trace`) | Veredicto del skill: **FAIL** (Regla 1). P0 enlazados a historia y RED: 7/7. Cobertura ejecutada 0% por diseño en RED. AD con test rojo: 13/13. | `test/traceability-matrix.md` §1 y §7 |
| TEA test review | **Approve with Comments**, 100/100 (Re-revisión 3). Queda abierto L1 (Low, tamaño de archivo). | `test/test-review.md` |
| NFR | Los 7 NFR de `prd.md` §6, la fila DEFERRED de cola y G7-02 están en **PLANNED**. Ninguno EVIDENCED. | `test/nfr-evidence.md` |
| Readiness (`bmad-check-implementation-readiness`) | Corrida 1: NOT READY. Corridas 2–8: NEEDS WORK (CONCERNS). Corrida 9: **READY (≡ PASS)**. | `planning/readiness-gate-report.md` |
| Sign-off del arquitecto | A — Juan Pablo Parra y B — Daniel Gonzalez: **aprobado** el 2026-10-14, tras revisión conjunta de todas las decisiones. | `planning/readiness-gate-report.md` (sección Sign-off) |
| Gate Drill | Se eliminó el binding de E4-S1 → NEEDS WORK; el gate detectó AD-01, AD-09 y AD-10 (PROBLEMAS = 6). Se restauró con `bmad-create-epics-and-stories` → READY. Duración ~1.2 min. Hashes iguales (sha256 del original y del restaurado). | `test/evidence/gate-drill.md` |
| Sprint status | `sprint-status.yaml` con 24 entradas (4 épicas, 16 historias, 4 retros), todas en `backlog`. YAML válido. | `implementation-artifacts/sprint-status.yaml` |

## Límites conocidos

- Sin CI activo (repositorio Git local): `test/ci/quality-gate.yml` es una plantilla que no se ha ejecutado en plataforma.
- Sin mediciones NFR: todos `PLANNED`.
- Sin lógica productiva. La suite ATDD queda en RED hasta que se implemente.
- Pendiente de decisión externa: matriz completa `roles_matrix` (equipo fuente de políticas), TTL de `uai_live_` y capacidad de cola (DEFER a NFR, responsable B).
