# Notas extraídas del PDF de la consigna (págs. 10-13) que NO están en references/tas-2-solu2.md

## Fase 4
- Story template de la pág. 10 es una imagen (no extraíble). Usar: Given/When/Then estrictos (happy + failure), DoD, Binding invariants (AD-n), contrato/cláusula, DTO, códigos de error, Test IDs/node IDs, dependencias solo hacia atrás.
- /bmad-sprint-planning: (a) juzga si un dev podría implementar sin inventar decisiones; (b) si pasa, genera sprint-status.yaml. Veredictos: PASS (≡IR-PASS) → copiar salida a readiness-gate-report.md; CONCERNS → cada uno con mitigación + firma del arquitecto (A — Juan Pablo Parra); FAIL → corregir con bmad-architecture / bmad-create-epics-and-stories / bmad-correct-course y re-correr hasta PASS.
- En BMad 6.10 instalado: bmad-sprint-planning solo genera sprint-status; el juicio (a) lo hace bmad-check-implementation-readiness (READY ≡ PASS, NEEDS WORK ≡ CONCERNS, NOT READY ≡ FAIL). Documentar este mapeo.
- 6 chequeos: FR/NFR↔historias sin huérfanos; cada estado UX (Loading/Empty/Error/Success/Denied) con contrato+DTO; cada AD-n en Binding invariants de ≥1 historia y con red test; sin dependencias hacia adelante; artefactos sin contradicciones; todos los hallazgos previos (Plan-2 Fases 1-3 + esta unidad) triageados y los Accepted visiblemente corregidos.
- Gate Drill: romper un link (borrar línea Binding invariants de una historia o renombrar DTO), re-correr, registrar qué reportó, qué skill lo arregló, cuánto tardó; restaurar y re-correr hasta PASS.

## Fase 5
1. ARCHITECTURE.md v2 con links. 2. ai-log/decision-log-solu2.md. 3. /bmad-testarch-trace final: 100% P0 → historia + red test. 4. /bmad-walkthrough opcional. 5. git tag solu2-ready.

## Paquete de entrega sugerido (pág. 11)
planning/{prd.md, ARCHITECTURE.md (v2), detailed-design/{contracts.md, ports-and-adapters.md, schemas/{001_<module>_schema.sql, dto.py, events.md, openapi.yaml}}, epics.md (Given/When/Then, DoD), readiness-gate-report.md (salida terminal + sign-off + gate drill log)}
implementation-artifacts/sprint-status.yaml
test/{test-design.md, atdd/<module>_contracts.test.py, fixtures/, nfr-evidence.md, traceability-matrix.md, ci/quality-gate.yml}
reviews/{review-arch-implementability.md, review-detailed-design.md, review-test-quality.md}
ai-log/decision-log-solu2.md
Nota: archivo backlog = epics.md.

## Decision log (pág. 12)
≥6 entradas nuevas cubriendo Fases 1,2,3,4; ≥2 propuestas IA rechazadas/corregidas con razón técnica y texto final adoptado; cada entrada: Phase | Persona/Skill | Prompt (resumen) | AI output (resumen) | Human decision (ACCEPT/MODIFY/REJECT) | Reason | Artifact changed; atribución de pareja.

## Rúbrica (pág. 12-13)
Contratos 20 · Ports/Schemas/DTO 20 · TEA 20 · epics+sprint 20 · AI governance 10 · Review & triage 10.
Deducciones: lógica productiva −20; tests tautológicos −5 c/u (máx −15); veredicto de gate sin salida −10; dependencia cross-module −10.
Annex A Módulo 1: invariante sembrado: permisos por contexto de curso, nunca "max across courses"; revocación ≤ 60 s. Enforcement típico: resolver puro en domain/; UNIQUE(user_id, course_id); job de revocación + revoked_at. Edge case: Student CS101 (0 GPU) y TA CS-480 → contextos independientes; debe tener invariante de contrato, enforcement físico, riesgo P0, red test e historia dedicada.
