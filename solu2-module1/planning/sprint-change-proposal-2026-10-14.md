# Sprint Change Proposal - Solu-2 Módulo 1 (Ronda 10)

**Fecha:** 2026-10-14
**Proyecto:** Solu-2: University AI Compute Fabric, Module 1
**Workflow:** `bmad-correct-course` (ejecución en lote, sin preguntas, por instrucción del estudiante) seguido de `bmad-create-epics-and-stories` en modo edición.
**Aprobación:** A — Juan Pablo Parra, 2026-10-14 (revisado con B). Decisiones: Ronda 10 de `.work/paquete-decisiones-F-H.md`.

## 1. Resumen del issue

El gate de readiness `solu2-module1/planning/implementation-readiness-report-2026-10-14.md` emitió veredicto **NOT READY** (FAIL). Hay 2 críticos (C-1, C-2), 6 mayores (M-1 a M-6) y 4 menores. Los críticos bloquean el PASS. Ninguno cambia el alcance de las tres operaciones (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`) ni el stack heredado.

## 2. Mapeo issue → cambio → artefacto → skill

| Issue | Cambio | Artefacto | Skill | Estado |
|---|---|---|---|---|
| C-1 AD-07 sin historia | AD-07 en Binding invariants de E1-S3 con T-AD07-01/02 (RED) y AC de clamp (0 → 1, 101 → 100) | `epics.md` (E1-S3, trazabilidad AD-07) | bmad-create-epics-and-stories | Aplicado |
| C-2 umbral 120 filas (2.0 s vs 1.2 s) | Tabla «Umbrales triageados»: AC citan solo el gate (< 2.0 s); 1.2 s queda como objetivo UX no vinculante, DEFER, owner B | `epics.md` | bmad-correct-course → bmad-create-epics-and-stories | Aplicado |
| M-1 progreso «N / 120» sin fuente | UX-DR1, Loading de E3-S1 y tabla Estados UX: progreso de subida en cliente + `Validando lote atómico...`; sin progreso por fila (AD-02 síncrono) | `epics.md`. `ux/EXPERIENCE.md` no se edita (fuente Plan-2) | bmad-correct-course → bmad-create-epics-and-stories | Aplicado en epics |
| M-2 génesis contradictoria | Génesis = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (ARCHITECTURE.md:97) en E1-S3 | `epics.md`. DDL, `events.md` y `atdd_support.py` ya usan la constante | bmad-architecture + bmad-testarch-atdd | Epics aplicado. Quedan fixtures `"0" * 64` en `module1_guard_contracts.test.py` (líneas 51, 294, 297, 317), que son filas de inserción, no aserciones de génesis |
| M-3 evidencia TEA desactualizada | Re-ejecutar test-review (sección de re-revisión) y trace sobre la colección actual | `solu2-module1/test/` | bmad-testarch-test-review + bmad-testarch-trace | **Pendiente**: no se ejecutó en esta pasada |
| M-4 13 AC funcionales sin RED | Gaps reemplazados por node IDs verificados; abiertos solo G-1, G-15, G-16 | `epics.md` (historias y «Gaps de cobertura») | bmad-testarch-atdd (tests ya en la colección) | Aplicado |
| M-5 umbrales NFR en conflicto | NFR-AUDIT-06 gate < 500 ms p95 (objetivos 200 ms / 50k < 200 ms); NFR-DISP-07 gate RAM ≤ 512 MB y boot < 5.0 s (objetivo 2.0 s / 120 MB) | `epics.md` («Umbrales triageados») | bmad-correct-course → bmad-create-epics-and-stories | Aplicado |
| M-6 DDL completo en E1-S1 | E1-S1 aplica la migración completa con justificación (schema = entregable de Fase 2); historias posteriores citan sus tablas e invariantes | `epics.md` (E1-S1) | bmad-create-epics-and-stories | Aplicado |
| Menores | `approved_by` ya es el nombre usado (paquete corregido); lista de [ASSUMPTION] con owner; T-REV-01 duplicado renombrado a T-REV-01b; `STU-MATEO-99` del PRD sin cambio por decisión | `epics.md` («Lista de [ASSUMPTION]») | — | Aplicado en epics |

## 3. Análisis de impacto (checklist de cambio)

- **Épicas:** ninguna se elimina, reordena ni añade. Dependencias sin cambios (sin dependencias hacia adelante).
- **PRD:** sin cambios. `STU-MATEO-99` (PRD §4.3) sigue pendiente como inconsistencia registrada (R8-08).
- **Arquitectura:** M-2 deja la constante génesis como fuente; no hay cambio de decisiones de stack.
- **UX:** UX-DR1 cambia en epics (progreso de subida en cliente). `ux/EXPERIENCE.md` no se toca.
- **Tests y diseño:** no se editaron. La colección tiene 132 nodos y todos los node IDs citados existen.
- **Alcance de sprint:** `sprint-status.yaml` no se genera porque el veredicto no es READY.

## 4. Enfoque recomendado

**Opción 1, ajuste directo.** Los cambios son de documentación y trazabilidad dentro de los stories y ATDD existentes. No hay rollback ni reducción de MVP. Esfuerzo bajo, riesgo bajo. Clasificación de alcance: **Minor**.

## 5. Handoff

| Rol / skill | Responsabilidad | Estado |
|---|---|---|
| bmad-create-epics-and-stories (edición) | Aplicar C-1, C-2, M-1, M-5, M-6, menores y node IDs en `epics.md` | Hecho en esta pasada |
| bmad-architecture | Confirmar la constante génesis en contracts y spine (M-2) | Pendiente de confirmación |
| bmad-testarch-atdd | Revisar fixtures `"0" * 64` del guard (M-2); M-4 ya tiene tests en la colección | Pendiente de revisión |
| bmad-testarch-test-review + bmad-testarch-trace | Re-ejecutar evidencia TEA (M-3) | Pendiente |
| Readiness gate | Reejecutar tras M-3 para obtener el veredicto | Pendiente |

## 6. Criterios de éxito

1. Cada issue crítico y mayor del gate tiene cambio aplicado o responsable con fecha.
2. Todos los node IDs de `epics.md` existen en `pytest --collect-only` (132 de 132 válidos).
3. Todos los tests ATDD y de guardas están citados en al menos una historia (116 + 12 de 116 + 12).
4. Los 4 tests de harness están citados en E1-S1.
5. Los gaps abiertos son solo G-1, G-15 y G-16, con razón y owner.
