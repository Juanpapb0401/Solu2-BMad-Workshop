# Roadmap del taller Solu-2

**Proyecto:** University AI Compute Fabric, Módulo 1: User, Role, and Subject Access Manager  
**Actualizado:** 14 de octubre de 2026  
**Estado general:** **Fases 0–4 ejecutadas con evidencia; Fase 5 (cierre) completa.** Fase 1 no se marca como PASS: el último Reviewer Gate de arquitectura es CONDITIONAL. El gate de TEA trace es FAIL por diseño (cobertura ejecutada 0% en RED). El readiness de la corrida 9 es READY (≡ PASS). El sign-off de B está pendiente. Ningún NFR está EVIDENCED.

## Vista rápida

| Fase | Estado | En pocas palabras |
|---|---|---|
| 0. Intake y gap audit | Completa | Review ejecutado, gaps documentados, tres operaciones y stack heredado confirmados (2026-10-12). |
| 1. Contratos P/Q/I y arquitectura | Completa con gate CONDITIONAL | 9 corridas del Reviewer Gate: 1–6 NO PASS, 7–9 CONDITIONAL. Cierre de iteración por decisión del estudiante. |
| 2. Diseño detallado | Completa con triage final | Review final: 55 hallazgos → 42 ACCEPT / 6 DEFER / 7 REJECT, aplicados. Artefactos sincronizados. |
| 3. TEA y preparación de pruebas | Completa; gate trace FAIL por diseño | 155 nodos (130 ATDD RED + 21 guardas + 4 harness). Test review 100/100. NFR en PLANNED. |
| 4. Épicas, historias y sprint | Completa | 4 épicas, 16 historias, readiness READY (corrida 9), `sprint-status.yaml` generado, Gate Drill superado. |
| 5. Wrap-up y entrega | Hecho | ARCHITECTURE v2, decision log con resumen, README de entrega y renombre del DDL hechos. Sign-off de A y B el 2026-10-14. |

**Leyenda:** Hecho = hay artefacto/evidencia; Parcial = hay artefacto pero falta una condición; Pendiente = todavía no se ha completado en este workspace.

## Fase 0: Intake y gap audit

**Estado: Completa según el alcance explícito de la consigna.**

- [x] Revisar Annex A, página 13, y confirmar las tres operaciones: `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`. Evidencia: `../planning/ARCHITECTURE.md`; memlog `planning/detailed-design/architecture-spine/.memlog.md` (decisión 2026-10-12).
- [x] Confirmar el Mandatory Edge Case: Student en CS101 (0 GPU) y TA en CS-480 (alta prioridad) se resuelven por contexto independiente. Evidencia: `planning/epics.md` (EDGE-01); `test/atdd/module1_resolve_contracts.test.py`.
- [x] Confirmar conservar el stack heredado: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 y SQLite WAL con writer único. Evidencia: `../planning/ARCHITECTURE.md` (Stack Decisions); `../.work/stack-verification.md`.
- [x] Ejecutar los reviews BMad de arquitectura y conservar los informes crudos. Evidencia: `planning/detailed-design/reviews/review-arch-implementability.md`; copia en `reviews/review-arch-implementability.md`.
- [x] Documentar los gaps del review y el triage propuesto. Evidencia: `planning/detailed-design/reviews/review-arch-implementability.md`.

**Cierre:** la consigna de Fase 0 pide review, lista de gaps y decisión de stack; esas tres cosas tienen evidencia.

## Fase 1: Contratos y architecture spine

**Estado: Completa como fase de trabajo. Gate final CONDITIONAL; las corridas 1–6 fueron NO PASS y quedan visibles.**

- [x] Crear `contracts.md` con P/Q/I y `architecture-spine/ARCHITECTURE-SPINE.md` con invariantes. Evidencia: `planning/detailed-design/contracts.md`; `planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md`.
- [x] Auditoría de implementabilidad (Amelia) y auditoría de arquitectura (Winston). Evidencia: `planning/detailed-design/reviews/review-agent-dev.md`; `planning/detailed-design/reviews/review-agent-architect.md`; `../resultados-interaccion.md`.
- [x] Reviewer Gate de arquitectura, 9 corridas. Veredictos: corridas 1–6 NO PASS; corridas 7–9 CONDITIONAL. Evidencia: `planning/detailed-design/architecture-spine/reviews/validation-gate-20261013*.md`.
- [x] Registrar decisiones humanas y propuestas aprobadas (rondas 1–13). Evidencia: `ai-log/decision-log-solu2.md`; `../.work/paquete-decisiones-F-H.md`.
- [x] Cerrar la iteración de gates de arquitectura por decisión del estudiante; el gate de Fases 1–2 de la consigna es el review final de diseño (Fase 2).
- [ ] Mantener en seguimiento las dependencias externas: matriz completa de roles (`roles_matrix.v0.json`, equipo de políticas), TTL de `uai_live_` y capacidad de cola (DEFER a NFR, responsable B).

**Resultado vigente:** último Reviewer Gate de arquitectura = CONDITIONAL (corrida 9, `validation-gate-20261013-9.md`). Las observaciones abiertas están triageadas en la Fase 2.

## Fase 2: Ports & Adapters, DDL, DTO, eventos y OpenAPI

**Estado: Completa. Review final triageado: 42 ACCEPT / 6 DEFER / 7 REJECT, aplicados en artefactos.**

- [x] Crear `ports-and-adapters.md`, `schemas/001_module1_schema.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml` y `schemas/roles_matrix.v0.json`. Evidencia: `planning/detailed-design/` (el DDL se renombró a `001_module1_schema.sql` en la entrega).
- [x] Auditoría de implementabilidad (Amelia) sobre los artefactos sincronizados. Evidencia: `planning/detailed-design/reviews/review-arch-implementability.md`.
- [x] Revisión adversarial y edge-case hunter: 25 adversariales + 30 edge cases. Evidencia: `planning/detailed-design/reviews/review-detailed-design-*-raw.*`.
- [x] Triage final: 55 hallazgos → 42 ACCEPT / 6 DEFER / 7 REJECT, tras la Ronda 6b. Evidencia: `planning/detailed-design/reviews/review-detailed-design.md`; mapeo en `planning/epics.md`.
- [x] Validaciones de entrega (2026-10-14): `dto.py` importa con `.venv`; el DDL se ejecuta en SQLite `:memory:`; `pytest -q` → 25 passed, 130 xfailed.
- [ ] Los 6 DEFER quedan con responsable en el triage; no tienen historia implementada.

## Fase 3: TEA, preparación de pruebas

**Estado: Completa como preparación de pruebas. El gate de trazabilidad del skill es FAIL por diseño: la suite está en RED.**

- [x] `/bmad-testarch-test-design`: riesgos P0–P3 y niveles de prueba. Evidencia: `test/test-design.md`.
- [x] `/bmad-testarch-framework`: scaffold pytest, fixtures simuladas y SQLite efímera. Evidencia: `test/conftest.py`; `test/fixtures/README.md`; `test/fakes/`; `pytest.ini`.
- [x] `/bmad-testarch-atdd`: suite RED con `xfail` estricto (`NotImplementedError`). Vigente: 130 atdd-red + 21 guardas + 4 harness = 155 nodos. Evidencia: `test/atdd-checklist.md`; `test/atdd/`.
- [x] `/bmad-testarch-ci`: quality gate local VERDE (`scripts/quality_gate.sh`). La plantilla de CI no está activada (no hay repo ni plataforma). Evidencia: `test/ci-quality-gate.md`; `test/ci/quality-gate.yml`.
- [x] `/bmad-testarch-nfr`: plan de evidencia con los 7 NFR en `PLANNED`; cola DEFER a Fase 3 NFR (responsable B). Evidencia: `test/nfr-evidence.md`.
- [x] `/bmad-testarch-trace`: P0 enlazados a historia y RED 7/7; AD con test rojo 13/13; veredicto del skill FAIL por cobertura ejecutada 0% en RED (esperado). Evidencia: `test/traceability-matrix.md`.
- [x] `/bmad-testarch-test-review`: Approve with Comments, 100/100 en la Re-revisión 3; L1 Low abierto. Evidencia: `test/test-review.md`.

**Gate para cerrar:** tests trazados a contratos e invariantes y suite RED válida: cumplido. Evidencia NFR: no existe; no se declara.

## Fase 4: Épicas, historias y sprint planning

**Estado: Completa. Readiness corrida 9 = READY (≡ PASS); Gate Drill superado.**

- [x] Épicas verticales para las tres operaciones: 4 épicas. Evidencia: `planning/epics.md`.
- [x] Historias ligadas a contrato, invariantes, tests y criterios de aceptación: 16 historias (Given/When/Then, DoD, Binding invariants). Evidencia: `planning/epics.md`.
- [x] Readiness gate oficial (`bmad-check-implementation-readiness`): NOT READY (corrida 1), NEEDS WORK (corridas 2–8), READY (corrida 9). Evidencia: `planning/readiness-gate-report.md`; informes `planning/implementation-readiness-report-2026-10-14*.md`.
- [x] `sprint-status.yaml` generado tras la corrida 9 (24 entradas, YAML válido). Evidencia: `implementation-artifacts/sprint-status.yaml`.
- [x] Gate Drill: se rompió el binding de E4-S1 → NEEDS WORK → restaurado → READY (~1.2 min; hashes iguales). Evidencia: `test/evidence/gate-drill.md`.

**Gate para cerrar:** readiness PASS reportado por el workflow (corrida 9) y Gate Drill documentado: cumplido.

## Fase 5: Wrap-up y entrega

**Estado: En curso.**

- [x] Decision log con resumen en formato de la consigna, herramientas y gobernanza; distingue decisiones humanas, propuestas de IA y asuntos diferidos. Evidencia: `ai-log/decision-log-solu2.md`.
- [ ] Triage cerrado: los ACCEPT tienen artefacto; los DEFER (6) y los REJECT (7) están en `planning/detailed-design/reviews/review-detailed-design.md`. Falta asignar responsable o fase a cada DEFER en la entrega.
- [x] `../planning/ARCHITECTURE.md` a v2 con Stack Decisions y enlaces a los artefactos finales. El Plan-2 original no se modificó. Evidencia: `../planning/ARCHITECTURE.md`.
- [x] Paquete de entrega e índice de rutas. Evidencia: `README.md`.
- [x] Revisión de integridad: renombre del DDL y referencias vigentes actualizados; `pytest` y `quality_gate.sh` verdes. Sign-off de A y B (2026-10-14).
- [ ] Preparar la entrega del taller (documento final para el estudiante).
- [ ] Commit/tag solo si el usuario lo pide explícitamente y hay un repositorio de clase autorizado. Hoy este workspace no tiene Git.

## Reglas para mantener este roadmap actualizado

- Cada vez que terminemos un workflow BMad, actualizar su casilla y pegar la ruta de su evidencia.
- Un borrador no es un gate PASS; una revisión no es una decisión aprobada.
- El usuario prefiere ejecutar los slash commands en su OpenCode. Yo preparo los prompts, ayudo con el contexto y reviso las salidas que comparta.
- No implementar lógica productiva: el alcance se detiene en solutioning, interfaces/stubs y preparación de pruebas.
