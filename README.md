# Solu-2 (Unit 4) — Módulo 1: User, Role, and Subject Access Manager

**Proyecto de Juan Pablo Parra y Daniel Gonzalez.**

University AI Compute Fabric · Pareja: **A — Juan Pablo Parra** (Architect-lead) · **B — Daniel Gonzalez** (Test-lead) · Tag de entrega: `solu2-ready`.

## Dónde está la entrega

**La entrega es la carpeta [`solu2-module1/`](solu2-module1/).** Contiene el paquete completo que pide la consigna (sección 9, *Suggested submission package*): contratos, diseño detallado, esquemas, suite de pruebas en RED, épicas, readiness gate, sprint status, reviews y decision log. El índice detallado, archivo por archivo, está en [`solu2-module1/README.md`](solu2-module1/README.md).

El resto del repositorio son las **entradas de Plan-2** que la consigna (sección 2) pide tener en el repositorio:

| Carpeta / archivo | Qué es |
|---|---|
| `planning/` | PRD y ARCHITECTURE (v2) de Plan-2, más el readiness report **de Plan-2** (el de Solu-2 está en `solu2-module1/planning/readiness-gate-report.md`). |
| `ux/` | DESIGN, EXPERIENCE y los 4 escenarios UX. |
| `reviews/`, `ai-log/` | Reviews y decision log de Plan-2. |
| `docs/`, `references/` | Brief del proyecto y consigna del taller (Annex A en el PDF). |
| `.work/` | Rondas de decisión del equipo (`paquete-decisiones-F-H.md`), evidencia del Gate Drill y script de regeneración de la tabla AD. |

## Cómo se construyó `solu2-module1/`

Se construyó **desde cero con el proceso BMad**, una fase a la vez con el skill que la consigna indica para cada una, sin reutilizar trabajo previo:

| Fase | Skill BMad | Resultado |
|---|---|---|
| 0 Intake | reviews adversarial y edge-case hunter | Gap audit triageado (`reviews/review-arch-implementability.md`) |
| 1 Contratos | `bmad-architecture` + Reviewer Gate | `contracts.md` con P/Q/I de las 3 operaciones y catálogo de errores |
| 2 Diseño | `bmad-architecture` + review final | Ports & adapters, DDL, DTO, eventos, OpenAPI |
| 3 Pruebas | `bmad-testarch-*` (test-design, atdd, trace, nfr, ci, test-review) | 155 tests (130 en RED por diseño), trazabilidad, plan NFR, CI |
| 4 Backlog | `bmad-create-epics-and-stories`, `bmad-check-implementation-readiness` | 4 épicas, 16 historias, readiness **READY (≡ PASS)** y Gate Drill |
| 5 Cierre | — | ARCHITECTURE v2, decision log, sign-off de A y B |

Los archivos producidos por los workflows llevan en su encabezado la traza del skill (`workflowType`, `stepsCompleted`). El uso de IA y las decisiones humanas sobre sus propuestas están en [`solu2-module1/ai-log/decision-log-solu2.md`](solu2-module1/ai-log/decision-log-solu2.md).

## Historias de usuario

16 historias en 4 épicas, en [`solu2-module1/planning/epics.md`](solu2-module1/planning/epics.md):

1. **Mateo confirma su acceso a CS-480** (walking skeleton): E1-S1 a E1-S3.
2. **El Dr. Marcus Vance da de baja a Mateo y el corte es inmediato**: E2-S1 a E2-S5.
3. **El Dr. Vance carga la nómina de CS-480 de forma atómica**: E3-S1 a E3-S4.
4. **Sofia obtiene permisos independientes por curso** (incluye EDGE-01): E4-S1 a E4-S4.

Todas están en `backlog` en `solu2-module1/implementation-artifacts/sprint-status.yaml`: el taller es un *stop-point* de solutioning y no incluye lógica productiva.

## Cómo correr las pruebas

```bash
cd solu2-module1
python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q              # 25 passed, 130 xfailed (RED intencional)
bash scripts/quality_gate.sh     # GATE LOCAL: VERDE
```
