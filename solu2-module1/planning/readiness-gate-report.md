# Readiness Gate Report: Módulo 1 (Solu-2)

**Fecha:** 2026-10-14
**Skill:** bmad-check-implementation-readiness (≡ Phase 4 Step 4.2 de la consigna)
**Mapeo de veredictos:** READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL
**Historial:** corrida 1 = NOT READY (informe `solu2-module1/planning/implementation-readiness-report-2026-10-14.md`); corrida 2 = NEEDS WORK (informe `solu2-module1/planning/implementation-readiness-report-2026-10-14-run2.md`).

## Corrida 1 (NOT READY)

### (a) Salida del gate

**Veredicto (step-06):** `Overall Readiness Status: NOT READY`

**Issues (step-06):** 12 issues en 6 categorías. 2 críticos, 6 mayores, 4 menores.

| # | Chequeo consigna | Resultado |
|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota (FR-ESCAL-02 y FR-AUDIT-04 parciales, alcance declarado) |
| 2 | Estados UX -> contrato + DTO | FAIL parcial (M-1: progreso "N / 120" sin fuente de datos) |
| 3 | AD-01..AD-13 en Binding + RED | FAIL (C-1: AD-07 sin historia en Binding invariants) |
| 4 | Sin dependencias hacia adelante | PASS |
| 5 | Artefactos sin contradicciones | FAIL (C-2, M-2, M-3, M-5) |
| 6 | Hallazgos triageados, ACCEPT visibles | PASS con nota (42 ACCEPT verificados; 6 sin node ID) |

### (b) Mapeo de veredictos

- READY ≡ PASS
- NEEDS WORK ≡ CONCERNS
- NOT READY ≡ FAIL

Veredicto de esta corrida: **NOT READY ≡ FAIL**.

### (c) Defectos (FAIL) con skill responsable

| ID | Severidad | Defecto | Skill responsable |
|---|---|---|---|
| C-1 | Crítico | AD-07 sin historia en Binding invariants (epics.md:661, :873) | bmad-create-epics-and-stories |
| C-2 | Crítico | Umbral de 120 filas: UX 1.2 s (scenario-1.md:83) vs PRD/contracts 2.0 s (prd.md:141); sin triage en epics (epics.md:901) | bmad-correct-course, luego bmad-create-epics-and-stories |
| M-1 | Mayor | Progreso "N / 120" sin canal de datos (EXPERIENCE.md:45; openapi.yaml:107 sincrono) | bmad-architecture |
| M-2 | Mayor | Semilla genesis e3b0c44 en ARCHITECTURE.md:97 vs 64 ceros en DDL/epics (H-15 sin triage en epics) | bmad-architecture |
| M-3 | Mayor | Evidencia TEA desactualizada (106/90/16 vs 108/93/15) y test-review con 401 "verdes" que hoy son RED | Fuera de los tres listados: bmad-testarch-trace y bmad-testarch-test-review |
| M-4 | Mayor | 13 ACs funcionales sin test RED (epics.md:786-812) | bmad-testarch-atdd (fuera de los tres listados) |
| M-5 | Mayor | Umbrales de auditoría (200 ms vs 500 ms) y de boot/RAM no triageados en epics (nfr-evidence.md:39-50) | bmad-correct-course |
| M-6 | Mayor | E1-S1 crea el DDL completo (regla step-05 §4B) | bmad-create-epics-and-stories |
| m-1..m-4 | Menor | STU-MATEO-99 en PRD/scenario-3; `approver_id` en paquete vs `approved_by` en DDL; advertencias abiertas de test-review; banners [ASSUMPTION] | bmad-correct-course / corrección del registro |

### (d) Sprint status

No aplica. El veredicto no era READY, así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

## Corrida 2

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK` (≡ CONCERNS)
**Issues de corrida 2:** 0 críticos, 5 mayores (K-1..K-5), 3 menores (K-6, K-8, K-9) y 1 nota de alcance (K-7). Detalle en el informe de corrida 2.

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | epics.md:47-49 (FR), :718-736 (cobertura); 16/16 "Requisito fuente"; FR-ESCAL-02 y FR-AUDIT-04 parciales con alcance declarado (epics.md:867-889) |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | epics.md:673-694; `ux/EXPERIENCE.md:45` contradice el Loading de ingestion (K-4) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS con nota | epics.md:696-716; 13/13 AD con nodo RED o guarda, 42 nodos citados verificados en `pytest --collect-only` (K-6, nota menor) |
| 4 | Sin dependencias hacia adelante | PASS | epics.md:634-659 y :661-672 |
| 5 | Artefactos sin contradicciones | CONCERNS | Codigos de error de epics.md presentes en contracts.md y openapi.yaml; rutas y DTOs coinciden con openapi.yaml:18,59,107 y dto.py. Contradicciones no triadas: K-1 (`planning/ARCHITECTURE.md:198` vs :97), K-2 (`test/test-design.md:8,82,91,97` y `test/traceability-matrix.md` §6 dicen OPEN lo ADOPTED), K-3 (decisiones ADOPTED sin node RED) |
| 6 | Hallazgos previos triageados y ACCEPT visiblemente aplicados | CONCERNS | 55 hallazgos de `detailed-design/reviews/review-detailed-design.md` mapeados en epics.md:738-789 (42 ACCEPT, 6 DEFER, 7 REJECT); spot-check aplicado en DDL, openapi y dto.py. Sin triage visible: `review-arch-implementability.md` (EC-01..EC-16) y `review-agent-dev.md` (D-01..D-15) (K-5) |

**Conteo:** 4 PASS (3 con nota), 2 CONCERNS, 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningun chequeo esta en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones de contrato (decisiones F/H, R3..R10 y ADVF/ECF ADOPTED y reflejadas en contracts, ports, DDL, dto.py y openapi.yaml). Lo que impide READY es la falta de triage visible y de sincronizacion documental (chequeos 5 y 6).
- Hechos citados, sin severidad de readiness: gate del skill `bmad-testarch-trace` = FAIL (P0 FULL 2/7; cobertura ejecutada 0% por diseno en RED; `solu2-module1/test/traceability-matrix.md:45-47`, §7). Gate de `bmad-testarch-test-review` = Request Changes (High=1, H-N1, ya corregido sin re-emitir veredicto; M-N2 abierto). Este skill no trata esos gates como bloqueantes.

### (c) Concerns (CONCERNS) con mitigacion propuesta

- **K-1 (Mayor, chequeo 5).** `planning/ARCHITECTURE.md:198` (snippet DDL) usa `DEFAULT` de 64 ceros; `:97` fija la genesis `e3b0c44…b855`. Mitigacion: registrar en decision log que el snippet no es normativo (fuente = :97 + DDL). Cualquier correccion del snippet va por `bmad-architecture` con excepcion explicita (AGENTS.md).
- **K-2 (Mayor, chequeo 5).** `test/test-design.md:8` y `test/traceability-matrix.md` §6 dicen OPEN lo ADOPTED en `.work/paquete-decisiones-F-H.md`. Mitigacion: `bmad-testarch-test-review` + `bmad-testarch-trace` actualizan cabecera y §6.
- **K-3 (Mayor, chequeos 3 y 5).** Decisiones ADOPTED sin node RED: H-16 (T-RES-05, P0 sin node), H-26 (T-RES-09), precedencia intra-paso F-03 (T-RES-07; parte cubierta por G-4 y G-7). Mitigacion: `bmad-testarch-atdd` agrega RED para T-RES-05 y T-RES-09 (o los declara guardas con justificacion) y cita sus node IDs en epics.md.
- **K-4 (Mayor, chequeos 2 y 5).** `ux/EXPERIENCE.md:45` exige progreso en tiempo real "78 / 120"; epics.md:74 y :345 lo reemplazan por progreso de subida en cliente (decision Ronda 10, M-1, owner A). `ux/C-UX-Scenarios/scenario-1.md:83` pide 1.2 s; epics.md:601 lo deja DEFER (owner B). Mitigacion: confirmacion escrita de owner A y registro de la sincronizacion pendiente de la fuente UX (no editable en esta copia).
- **K-5 (Mayor, chequeo 6).** `detailed-design/reviews/review-arch-implementability.md` (EC-01..EC-16) y `review-agent-dev.md` (D-01..D-15) sin tabla de triage visible. Varios ACCEPT estan aplicados en sustancia (EC-01 -> T-CON-01; EC-03 -> T-RES-04; EC-14 -> T-ROS-01; D-05 -> DDL:245; D-15 -> contracts.md:90). Mitigacion: tabla EC/D -> historia/AC/artefacto en epics.md, por `bmad-create-epics-and-stories`; confirmacion de arquitectura para D-01..D-11.
- **K-6 (Menor, chequeo 3).** Fila AD-06 de epics.md:700-716 lista E3-S2 sin AD-06 en su Binding; E3-S4 lo declara sin aparecer en la fila. Mitigacion: corregir la fila (`bmad-create-epics-and-stories`).
- **K-7 (Nota de alcance, chequeo 1).** FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial aprobado (Annex A, tres operaciones). No es defecto.
- **K-8 (Menor, chequeo 5).** STU-MATEO-99 en `planning/prd.md:179,189` y `ux/C-UX-Scenarios/scenario-3.md:32-33`; tratado como alias de STU-98432 (R8-08). Sin cambio en fuente.
- **K-9 (Menor, chequeo 5).** Umbrales internos del PRD (`prd.md:236` 200 ms vs `prd.md:296` 500 ms; NFR-DISP-07 vs ARCHITECTURE §1.1). Triados en epics.md:595-604.

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificacion de los issues de la corrida 1

| ID corrida 1 | Estado en corrida 2 | Donde quedo | Pendiente |
|---|---|---|---|
| C-1 AD-07 sin historia | **Resuelto** | AD-07 en Binding de E1-S3 (epics.md:179); T-AD07-01 y T-AD07-02 en la coleccion y en xfail; fila AD-07 en epics.md:700-716 | Nada |
| C-2 umbral 120 filas (1.2 s vs 2.0 s) | **Resuelto en epics** | Tabla "Umbrales triageados" (epics.md:595-604): AC con umbral gate 2.0 s, 1.2 s DEFER (owner B) | Fuente UX sin sincronizar (K-4) |
| M-1 progreso "N / 120" | **Resuelto en epics** | UX-DR1 (epics.md:74), Loading de E3-S1 (epics.md:345), tabla Estados UX (epics.md:677) | `ux/EXPERIENCE.md:45` sin sincronizar (K-4) |
| M-2 genesis contradictoria | **Resuelto en diseno y tests** | Constante en `001_module1.sql:151,192,210`, `events.md:134`, `test/atdd/atdd_support.py:26`, contracts.md y spine; E1-S3 (epics.md:176) | Snippet `planning/ARCHITECTURE.md:198` aun con ceros (K-1) |
| M-3 evidencia TEA desactualizada | **Re-ejecutado; veredicto con pendientes** | `traceability-matrix.md` ahora cita 132 nodos (linea 21) y gate FAIL por cobertura P0 (hecho citado); `test-review.md` re-revision 2 (linea 514) con H-N1 corregido | Re-emitir test-review; actualizar OPEN obsoletos (K-2); M-N2 abierto |
| M-4 13 ACs funcionales sin RED | **Resuelto** | 15 gaps con node ID (G-2..G-14 y G-17; epics.md:847-861), verificados en `--collect-only` | Abiertos solo G-1, G-15, G-16 (epics.md:839-841), owner B, NFR/DEFER |
| M-5 umbrales NFR (200 vs 500 ms; boot/RAM) | **Resuelto en epics** | Tabla de umbrales triageados (epics.md:595-604) | Fuentes PRD y ARCHITECTURE sin cambio (K-9, triado) |
| M-6 DDL completo en E1-S1 | **Resuelto como excepcion justificada** | epics.md:127 (E1-S1 aplica la migracion completa; justificacion de Fase 2) | Ninguno; una revision podria exigir partir el DDL |
| m-1 STU-MATEO-99 | **Triado, no corregido en fuente** | R8-08; epics.md:613 (lista [ASSUMPTION]) | Fuente PRD sin cambio (K-8) |
| m-2 `approver_id` vs `approved_by` | **Resuelto** | Paquete corregido (`.work/paquete-decisiones-F-H.md:132,149`); DDL `001_module1.sql:117` | Ninguno |
| m-3 advertencias de test-review (T-ROS-03/03b, T-REV-01) | **Parcial** | T-REV-01 duplicado renombrado a T-REV-01b (epics.md:618-632); T-ROS-03 y T-ROS-03b existen como nodos distintos | Descripciones aun solapadas |
| m-4 banners [ASSUMPTION] | **Resuelto** | Lista con owner en epics.md:606-616 | Ninguno |

## Corrida 3

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK` (≡ CONCERNS)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run3.md` (corridas 1 y 2 conservadas en sus archivos).
**Issues de corrida 3:** 0 críticos, 3 mayores abiertos (K-4, K-5 parcial, K-6 ampliado), 5 menores (K-1 proceso, K-2 parcial, K-8, K-9, K-10) y 1 nota de alcance (K-7).

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. "Lo que impide READY: (a) la tabla de trazabilidad AD-n contradice los Binding de 8 de 13 AD; (b) fuentes UX y escenario 1 sin sincronizar (triadas); (c) dos reviews Plan-2 sin triage visible en Solu-2; (d) conteos de la traza TEA desfasados."

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | epics.md:718-736 (FR Coverage); 16/16 "Requisito fuente"; PRD 4 FR + 7 NFR presentes; FR-ESCAL-02 y FR-AUDIT-04 parciales con alcance declarado |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | epics.md:683-704 (todos los estados de EXPERIENCE §2 y §3.2); `ux/EXPERIENCE.md:45` y `ux/C-UX-Scenarios/scenario-1.md:83` contradicen (K-4, triado) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS con nota | 13/13 AD en algún Binding (epics.md:128-585); 13/13 con node RED o guarda existente en `pytest --collect-only`; tabla epics.md:706-724 contradice 8 de 13 filas (K-6) |
| 4 | Sin dependencias hacia adelante | PASS | epics.md "Depende de" (líneas 139-600) y tabla epics.md:644-667; ninguna dependencia apunta a historia posterior |
| 5 | Artefactos sin contradicciones | CONCERNS | Códigos de error de epics presentes en contracts/openapi/dto/events; rutas y DTOs coinciden (openapi.yaml:18/59/107, dto.py); K-1 resuelto en contenido (`planning/ARCHITECTURE.md:198`); K-6 (tabla AD); K-4 (fuentes UX); conteos de traza (`test/traceability-matrix.md:20,131,133`, dicen 132; hoy 152) |
| 6 | Hallazgos previos triageados y ACCEPT visibles | CONCERNS | `review-detailed-design.md`, `review-arch-implementability.md` (EC-01..16) y `review-agent-dev.md` (D-01..16) con filas de triage (epics.md:1000-1080); spot-check de citas OK. Sin triage visible en Solu-2: Plan-2 `reviews/review-arch-adversarial.md` y `reviews/review-ux-edge-cases.md` (EDGE-UX-04/05) (K-5 parcial) |

**Conteo:** 4 PASS (3 con nota), 2 CONCERNS, 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningún chequeo en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones de contrato. Lo que impide READY es documentación sin sincronizar y trazabilidad incorrecta.
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (P0 FULL 2/7; RED por diseño; `test/traceability-matrix.md` §7). Gate `bmad-testarch-test-review` = Request Changes (H-N1 corregido sin re-emitir; M-N2 abierto).

### (c) Concerns con mitigación propuesta

- **K-4 (Mayor, chequeos 2 y 5).** `ux/EXPERIENCE.md:45` ("78 / 120") y `scenario-1.md:83` (1.2 s) frente a epics.md:74, :349 y :605-614. Mitigación: confirmación escrita de owner A (Loading) y owner B (1.2 s); sincronizar en el próximo ciclo UX (fuente no editable en esta copia).
- **K-5 (Mayor, chequeo 6, parcial).** Plan-2 `reviews/review-arch-adversarial.md` (ARCH-ADV-CRIT-01, CRIT-02, MAJ-01, MAJ-02, MIN-01) y `reviews/review-ux-edge-cases.md` (EDGE-UX-04, EDGE-UX-05) sin fila en "Triage de hallazgos previos" de epics.md. Mitigación: añadir filas (aplicación o DEFER con owner) por `bmad-create-epics-and-stories`.
- **K-6 (Mayor, chequeos 3 y 5, ampliado).** epics.md:706-724: 8 de 13 filas no coinciden con los "Binding invariants" por historia (AD-04, 05, 06, 08, 09, 10, 11, 12). Mitigación: regenerar la tabla desde los Binding (`bmad-create-epics-and-stories`).
- **K-1 (Menor, proceso).** `planning/ARCHITECTURE.md:198` corregido en contenido; AGENTS.md no permite editar ARCHITECTURE salvo stack y enlaces v2, y no consta excepción explícita. Mitigación: registrar la excepción del estudiante en `ai-log/decision-log-solu2.md` o revertir la anotación.
- **K-2 (Menor, parcial).** `test/traceability-matrix.md:20,131,133` con 132 nodos. Mitigación: actualizar a 152 / 25 / 127 (`bmad-testarch-trace`).
- **K-10 (Menor).** `test/test-review.md` (Re-revisión 2) sin re-emitir veredicto tras H-N1; M-N2 abierto. Mitigación: `bmad-testarch-test-review`.
- **K-7 (nota de alcance).** FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial aprobado (Annex A). No es defecto.
- **K-8 (Menor).** `STU-MATEO-99` en `planning/prd.md:179,189` y `scenario-3.md`; alias de STU-98432 (R8-08). Sin cambio en fuente.
- **K-9 (Menor).** Umbrales internos del PRD (`prd.md:236` 200 ms vs `prd.md:296` 500 ms; NFR-DISP-07 vs ARCHITECTURE §1.1). Triados en epics.md:605-614.

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 2

| ID corrida 2 | Estado en corrida 3 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-1 snippet genesis ARCHITECTURE:198 | **Resuelto en contenido; reserva de proceso** | `planning/ARCHITECTURE.md:198` ahora con la constante de :97 y anotación `[CORREGIDO 2026-10-14...]`; `ai-log/decision-log-solu2.md` sección K-1 | Excepción de AGENTS.md no documentada como aprobada por el estudiante (Menor, proceso) |
| K-2 TEA dice OPEN lo ADOPTED | **Resuelto en test-design y §6 de traza; conteos parciales** | `test/test-design.md:8,197` (ADOPTED, sin "OPEN" obsoleto); `test/traceability-matrix.md` §6 (líneas 137-157) | Cabecera y §5 de la traza dicen 132 nodos (K-2 parcial, Menor) |
| K-3 decisiones ADOPTED sin node RED | **Resuelto** | T-RES-05 (`module1_resolve_contracts.test.py::TestRequestTimeAndRole::test_resolve_request_now_captured_once_and_reused_as_occurred_at`) y T-RES-09 (`...::test_resolve_effective_role_is_exact_roles_id`) colectados y citados en epics.md:160 y :502; `atdd-checklist.md:114-115`. T-RES-07: cubierto en parte por G-4/G-7 | Ninguno (T-RES-07 declarado en `atdd-checklist.md:260` como pendiente explícito) |
| K-4 fuente UX contradice Loading | **Abierto (triado)** | epics.md "Contradicciones de Plan-2 triageadas" (fila `ux/EXPERIENCE.md:45`); scenario-1 con owner B | Sincronizar fuentes UX (no editable en esta copia) |
| K-5 triage no visible de EC/D | **Resuelto para review-arch-implementability (EC-01..16) y review-agent-dev (D-01..16); parcial para Plan-2 root reviews** | epics.md:1000-1050 (filas EC-xx y D-xx con artefacto/historia) | Plan-2 `review-arch-adversarial.md` y `review-ux-edge-cases.md` sin fila (K-5, Mayor) |
| K-6 AD-06 fila incorrecta | **Abierto y ampliado** | epics.md:717 (fila AD-06 incluye E3-S2, omite E3-S4 y E1-S3); 8 de 13 filas AD (epics.md:706-724) no coinciden con Binding | Regenerar tabla AD (K-6, Mayor) |
| K-7 alcance FR-ESCAL-02 / FR-AUDIT-04 | Sin cambio (nota) | epics.md "Fuera de alcance de Solu-2" | Ninguno (no es defecto) |
| K-8 STU-MATEO-99 | Sin cambio en fuente (triado) | epics.md "Lista de [ASSUMPTION]" y triage | Fuente PRD/scenario-3 sin unificar |
| K-9 umbrales PRD vs ARCHITECTURE | Sin cambio en fuente (triado) | epics.md:605-614 | Fuentes sin cambio |

Issues de corrida 1 (verificación previa, sin cambios): C-1 y C-2 siguen resueltos; M-1..M-6 y m-1..m-4 siguen en el estado de la corrida 2.

## Corrida 4

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK (CONCERNS)` (≡ CONCERNS; no READY, no FAIL)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run4.md` (corridas 1-3 conservadas en sus archivos).
**Issues de corrida 4:** 0 críticos, 1 mayor abierto (K-11: review de seguridad propio `architecture-spine/reviews/review-security.md` sin triage y con exigencias pre-build no cerradas, incluido el modo de fallo de `Clock` en `resolve`), 1 residuo menor de conteos (K-2), notas menores (K-5 nota, K-8, K-9, K-10 L1, K-12).

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. Lo que impide READY: (a) K-11, review de seguridad sin triage ni tests y con un fallo de `Clock` sin decidir; (b) residuos de conteo en artefactos TEA (K-2). No hay decisión de dominio faltante en las tres operaciones.

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | epics.md:44-60 (inventario), FR Coverage Map (epics.md:726); 16/16 "Requisito fuente"; FR-ESCAL-02 (epics.md:47, :88) y FR-AUDIT-04 (epics.md:49) con alcance parcial declarado |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | epics.md:683-704; `ux/EXPERIENCE.md:45` y `ux/C-UX-Scenarios/scenario-1.md:52,83` sincronizados (K-4 cerrado; 0 coincidencias de textos antiguos en `ux/` y `planning/`) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD en Binding (epics.md:128-585); tabla AD-n (epics.md:710-724) = Binding por script: 0 discrepancias (K-6 cerrado); 135 node IDs de la tabla, 0 sin colectar |
| 4 | Sin dependencias hacia adelante | PASS | epics.md:139-600 ("Depende de", 16 líneas) y epics.md:644-667 |
| 5 | Artefactos sin contradicciones | CONCERNS (menor, documental) | Códigos, rutas y DTOs coinciden. Residuo de conteo: `test/tea-skill-matrix.md:11` (132; debe ser 152/25/127); `test/e2e-trace-summary.json` `coverage.by_level` suma 132 vs `cases` 152; `test/tea-skill-matrix.md:14` mezcla Re-revisión 2 y 3 |
| 6 | Hallazgos previos triageados y ACCEPT visibles | CONCERNS (mayor) | Cerrado: 21 filas nuevas para `reviews/review-arch-adversarial.md`, `review-arch-edge-cases.md`, `review-prd-adversarial.md`, `review-ux-edge-cases.md` (epics.md:1062-1081). Abierto: `architecture-spine/reviews/review-security.md` sin ninguna referencia en epics.md ni decision-log (K-11) |

**Conteo:** 4 PASS (3 con nota), 2 CONCERNS (5 menor, 6 mayor), 0 FAIL.

### (b) Mapeo de veredictos

- READY = PASS; NEEDS WORK = CONCERNS; NOT READY = FAIL.
- Veredicto: NEEDS WORK (CONCERNS). Ningún chequeo en FAIL.

### (c) Concerns con mitigación propuesta

- **K-11 (mayor, chequeo 6).** review-security.md: M-02 aplicado en contenido (`contracts.md:21,27`), M-03 aplicado en contenido (`contracts.md:158`, cola llena → 503 en `events.md`), pero sin fila de triage ni tests RED (`test_userid_canonicalization_rejects_variant`, `test_rejected_batch_audited`, `test_ledger_no_drop_under_pressure`: no existen). M-01 (ventana perimetral 60 s) sin decisión. B-01: `Clock` sin modo de fallo en `contracts.md:56` (defecto real de implementabilidad menor; LedgerWriter sí fail-closed en `ports-and-adapters.md:154`). B-02 (enumeración 404/403) sin riesgo aceptado. Mitigación: filas de triage en epics.md; decidir fallo de `Clock` (propuesta: 503 `AUTH_INTERNAL_POLICY_UNAVAILABLE`) en contracts.md §1; tests RED o DEFER con owner. Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra).
- **K-2 residual (menor).** Actualizar `test/tea-skill-matrix.md:11,14` y `test/e2e-trace-summary.json` (`by_level`) con `bmad-testarch-trace` / `bmad-testarch-test-review`.
- **K-5 nota (menor).** Añadir a la fila ARCH-EDGE-02 (epics.md:1071) la referencia a `planning/detailed-design/schemas/events.md`.
- **K-12 (nota).** `review-consistency.md` sin referencia directa; sus 5 puntos están cubiertos por EC-01, EC-03, W-04, AR-07, W-07/W-08. Sin acción de contenido.

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 3

| ID corrida 3 | Estado en corrida 4 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-4 fuentes UX sin sincronizar (Mayor) | **Cerrado** | `ux/EXPERIENCE.md:45`; `ux/C-UX-Scenarios/scenario-1.md:52,83`; nota `[ACTUALIZADO 2026-10-14, Solu-2 K-4/R10-M1]`; decision log "K-4 cierre" | Ninguno |
| K-5 parcial, reviews Plan-2 sin triage (Mayor) | **Cerrado para los 4 reviews de la raíz**; el residuo pasa a K-11 (review-security) | epics.md:1062-1081 (21 filas: arch-edge-cases 4, arch-adversarial 5, prd-adversarial 7, ux-edge-cases 5); decision log "K-5 — Filas faltantes" | ARCH-EDGE-02 sin referencia a events.md (nota menor) |
| K-6 ampliado, tabla AD-n vs Binding (Mayor) | **Cerrado** | epics.md:710-724 regenerada; verificación por script: 13 filas, 0 discrepancias; ADs en Binding de E1-S1, E1-S2, E2-S4, E3-S2, E3-S3, E4-S1, E4-S2 | Ninguno |
| K-1 edición fuera de AGENTS.md (Menor, proceso) | **Cerrado** | decision log "K-1 confirmación" (corrección de `ARCHITECTURE.md:198` confirmada por el estudiante; permitida por AGENTS.md como parte de la actualización v2 de Fase 5) | Ninguno |
| K-2 conteos de traza (Menor, parcial) | **Parcial** | `test/traceability-matrix.md:20,131,133` = 152/25/127; §11 mapea los 20 nodos nuevos | `test/tea-skill-matrix.md:11` (132) y `test/e2e-trace-summary.json` `by_level` (suma 132) |
| K-10 test-review sin re-emitir (Menor) | **Cerrado** | `test/test-review.md:611-671`: Re-revisión 3, 100/100 (A), Approve with Comments; Low 1 (L1, no bloqueante) | L1 (archivos > 600 líneas) abierto, low |
| K-8 STU-MATEO-99 (Menor) | Sin cambio (triado) | epics.md "Triage" (R8-08) | Fuente PRD/scenario-3 sin unificar |
| K-9 umbrales PRD vs ARCHITECTURE (Menor) | Sin cambio (triado) | epics.md:605-614 | Fuentes sin cambio |
| K-7 alcance FR-ESCAL-02 / FR-AUDIT-04 (nota) | Sin cambio | epics.md "Fuera de alcance de Solu-2" | Ninguno (no es defecto) |

## Corrida 5

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK (CONCERNS)` (≡ CONCERNS; no READY, no FAIL)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run5.md` (corridas 1-4 conservadas en sus archivos).
**Issues de corrida 5:** 0 críticos, 0 mayores, 3 menores (K-13 bloquea; K-14, K-16 no bloquean), 3 notas (K-15, K-17, K-18). Cero defectos de implementabilidad.

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. Lo que impide READY: K-13, una frase falsa de conteo en `test/tea-skill-matrix.md:15` ("`e2e-trace-summary.json` ... siguen con la cifra de 132 nodos"; hoy son 154). El resto no bloquea.

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | `planning/prd.md:124,148,175,199` (4 FR); `planning/prd.md:291-297` (7 NFR); epics.md:47-49 (FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial declarado), epics.md:728 (FR Coverage Map); 16/16 "Requisito fuente" |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | epics.md:685 (tabla de Estados UX); `ux/EXPERIENCE.md` sin "78 / 120" y `ux/C-UX-Scenarios/scenario-1.md:83` = 2.0 s (K-4 cerrado). Nota K-18: anclas de la tabla de triage desfasadas (epics.md:1006, :1015) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD en Binding (epics.md:128-585). Tabla AD-n (epics.md:710-724) = regeneración por `.work/regen_ad_table.py` en copia: 0 discrepancias, 0 node IDs inválidos. `pytest --collect-only` = 154 (incluye T-RES-15 y T-ROS-21) |
| 4 | Sin dependencias hacia adelante | PASS | epics.md:139-602 ("Depende de", 16 líneas, todas anteriores); epics.md:650 (tabla de orden) |
| 5 | Artefactos sin contradicciones | CONCERNS (menor, documental; bloquea) | K-13: `test/tea-skill-matrix.md:15` dice 132; e2e `tests.cases` = 154 y `by_level` suma 154. Notas: K-15 (`schemas/openapi.yaml:510`, lista de causas del 503 sin Clock/IdGenerator), K-18. Códigos, rutas y DTOs coinciden (`openapi.yaml:18,59,107`, `dto.py:93`) |
| 6 | Hallazgos previos triageados y ACCEPT visibles | CONCERNS (menor; no bloquea) | Cerrado: filas SEC M-01..M-03, B-01, B-02 (epics.md:1085-1091) y CONS-1..5 (epics.md:1092-1096). B-01 aplicado en `contracts.md:49` (§1), `:75` (§2), `:99` (§3), `ports-and-adapters.md:53`; RED `module1_resolve_contracts.test.py:536` y `module1_ingest_contracts.test.py:429`. Abierto no bloqueante: K-14 (cita de LedgerWriter, epics.md:1091), K-16 (revoke RED diferido), K-17 (etiquetas CONS) |

**Conteo:** 4 PASS (3 con nota), 2 CONCERNS (ambos menor), 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningún chequeo en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones. Lo que impide READY es una frase de conteo falsa en la evidencia TEA (K-13).
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (P0 29%, 2/7 FULL; cobertura ejecutada 0% por diseño en RED; `test/traceability-matrix.md` §7). Gate `bmad-testarch-test-review` = Approve with Comments (Re-revisión 3, 100/100; L1 Low abierto). Este skill no trata esos gates como bloqueantes.

### (c) Concerns con mitigación propuesta

- **K-13 (menor, chequeo 5, bloquea).** `test/tea-skill-matrix.md:15`: la frase "siguen con la cifra de 132 nodos" es falsa. Cambio: "`e2e-trace-summary.json` actualizado a 154 nodos (Ronda 12); `gate-decision.json` no contiene cifras de nodos." Skill: `bmad-testarch-trace` o corrección directa del registro.
- **K-14 (menor, chequeo 6, no bloquea).** `planning/epics.md:1091` cita `LedgerWriter` en `resolve` contra `contracts.md §1`, que no lo cubre. Cubierto por `contracts.md:141` y `ports-and-adapters.md:53`. Cambio: añadir esa cita en epics.md:1091. Skill: `bmad-create-epics-and-stories`.
- **K-16 (menor, chequeo 6, no bloquea).** Revoke con R12-B01 en `contracts.md:75` sin test RED ni node ID ("DEFER a TEA"). Mitigación: crear el nodo RED con `bmad-testarch-atdd` o registrar DEFER con owner y fecha en epics.md:1091. Skill: `bmad-testarch-atdd`.
- **K-15 (nota, chequeo 5).** `planning/detailed-design/schemas/openapi.yaml:510`: añadir "fallo de Clock o IdGenerator (R12-B01)" a la lista de causas. Skill: `bmad-architecture`.
- **K-17 (nota, chequeo 6).** `CONS-1..5` son ítems 1-5 del Veredicto de `review-consistency.md`, no IDs del archivo. Mitigación: aclarar en las filas de epics.md. Skill: `bmad-create-epics-and-stories`.
- **K-18 (nota, chequeo 2/5).** epics.md:1006 y :1015 apuntan a l.673-694; la tabla está en l.685. Skill: `bmad-create-epics-and-stories`.

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 4

| ID corrida 4 | Estado en corrida 5 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-11 review-security.md sin triage ni tests; B-01 `Clock` sin modo de fallo (Mayor) | **Cerrado en triage y contrato** | Filas SEC M-01, M-02, M-03, B-01, B-02 (epics.md:1085-1091). M-02 en `contracts.md` §0 con test `test_ingest_institutional_id_case_distinct_identity` (colectado). M-03 con `roster.rejected` y `test_roster_rejected_occurred_at_reuses_single_request_now` (colectado). B-01 en `contracts.md` §1/§2/§3 y `ports-and-adapters.md:53`; RED T-RES-15 y T-ROS-21 (colectados). M-01 DEFER owner A (`test/nfr-evidence.md`). B-02 REJECT (riesgo residual aceptado). Decisión R12 en `decision-log-solu2.md` | K-16 (revoke RED diferido), K-14 (cita de LedgerWriter). Sign-off arquitecto PENDIENTE |
| K-11 parte review-consistency.md (CONS-1..5) | **Cerrado** | Filas CONS-1..CONS-5 (epics.md:1092-1096) con disposición y ubicación | K-17 (etiquetas ordinales, nota) |
| K-2 residual: conteos (`test/tea-skill-matrix.md:11,14`; `test/e2e-trace-summary.json` `by_level`) | **Parcial** | `tea-skill-matrix.md:11` = 129 atdd / 154 colectados; `e2e-trace-summary.json` `by_level` suma 154 (129 api + 25 other) | **K-13**: `tea-skill-matrix.md:15` sigue diciendo 132 |
| K-5 nota: ARCH-EDGE-02 sin referencia a `events.md` (Menor) | **Cerrado** | epics.md:1073 cita `schemas/events.md` l.138 y l.143 | Ninguno |
| K-12 nota: `review-consistency.md` sin referencia directa | **Cerrado** | Filas CONS-1..5 en epics.md:1092-1096 | K-17 (etiquetas) |
| K-10 L1 de test-review (archivos > 600 líneas, Low) | Abierto, no bloqueante | `test/test-review.md` Re-revisión 3 | Ninguno para READY |
| K-8 STU-MATEO-99; K-9 umbrales PRD vs ARCHITECTURE | Sin cambio (triados) | epics.md:605-614 | Fuentes sin cambio (no bloquea) |
| K-7 alcance FR-ESCAL-02 / FR-AUDIT-04 (nota) | Sin cambio | epics.md:47-49 | Ninguno (no es defecto) |

Issues de corridas 1-3 (C-1, C-2, M-1..M-6, m-1..m-4, K-1..K-10): sin cambios desde la verificación de corrida 4.

## Corrida 6

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK (CONCERNS)` (≡ CONCERNS; no READY, no FAIL)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run6.md` (corridas 1-5 conservadas en sus archivos).
**Issues de corrida 6:** 0 críticos, 0 mayores, 1 menor que bloquea (K-19). Cero defectos de implementabilidad.

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. Lo que impide READY: K-19, dos fuentes de diseño dicen en presente "test RED DEFER a TEA" para revoke R12-B01, y T-REV-12 ya existe (colección 155 = 130 atdd + 21 guardas + 4 harness).

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | `planning/prd.md:124,148,175,199` (4 FR); `planning/prd.md:291-297` (7 NFR); epics.md:47-49 (FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial declarado), epics.md:728 (FR Coverage Map); 16/16 "Requisito fuente" |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | epics.md:686 (tabla de Estados UX); `ux/C-UX-Scenarios/scenario-1.md:83` = 2.0 s (K-4 sigue cerrado). Anclas K-18 cerradas (epics.md:1006, :1015 por nombre de sección) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD en Binding. Regeneración de la tabla AD-n por `.work/regen_ad_table.py` en copia: 0 discrepancias, 0 node IDs inválidos. `pytest --collect-only -q` = 155 (incluye T-REV-12, T-RES-15 y T-ROS-21) |
| 4 | Sin dependencias hacia adelante | PASS | epics.md:139-602 ("Depende de", 16 líneas, todas anteriores); epics.md:650 (tabla de orden) |
| 5 | Artefactos sin contradicciones | CONCERNS (menor, documental; bloquea) | K-19: `planning/detailed-design/contracts.md:75` y `ports-and-adapters.md:53` dicen "test RED DEFER a TEA" para revoke; T-REV-12 existe (`test/atdd/module1_revoke_contracts.test.py:406`) y lo citan `epics.md:274,1092`. Sin contradicción en conteos: `tea-skill-matrix.md:15` (K-13) ya dice 155 |
| 6 | Hallazgos previos triageados y ACCEPT visibles | CONCERNS (mismo K-19; resto cerrado) | Filas SEC B-01 (epics.md:1092, con cita LedgerWriter corregida), CONS-1..5 (epics.md:1094-1098, con "ítem n del veredicto"). Abierto: K-19 (residuo textual de K-16) y L1 de test-review (Low, no bloquea) |

**Conteo:** 4 PASS (3 con nota), 2 CONCERNS (ambos por K-19), 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningún chequeo en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones. T-REV-12 está nombrado y en RED; no hay que inventar decisión ni test. Lo que impide READY es el texto vigente que dice lo contrario (K-19), tratado con la misma regla que K-13 en corrida 5.
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (cobertura ejecutada 0% por diseño en RED; `test/traceability-matrix.md` §7). Gate `bmad-testarch-test-review` = Approve with Comments (Re-revisión 3, 100/100; L1 Low abierto). Este skill no los trata como bloqueantes.
- Históricos no contados como contradicción: `ai-log/decision-log-solu2.md:599` (Ronda 12), `planning/sprint-change-proposal-2026-10-14.md:32` (Ronda 10: "132 nodos"), `test/traceability-matrix.md:183` (registro de corrección).

### (c) Concerns con mitigación propuesta

- **K-19 (menor, chequeo 5/6, bloquea).** `planning/detailed-design/contracts.md:75` ("Test RED de esta rama: DEFER a TEA (ver decision-log, Ronda 12).") y `planning/detailed-design/ports-and-adapters.md:53` ("Revoke: mismo criterio, test RED DEFER a TEA."). Cambio en contracts.md:75: "Test RED de esta rama: T-REV-12 `test_revoke_clock_failure_503_fail_closed_no_mutation` (E2-S3)."; cambio en ports-and-adapters.md:53: "Revoke: mismo criterio, test RED T-REV-12 `test_revoke_clock_failure_503_fail_closed_no_mutation` (E2-S3)." Skill: `bmad-create-epics-and-stories` o corrección directa del registro (como K-13). No se aplicó en esta corrida (sin edición de diseño).

Notas heredadas no bloqueantes: L1 de `test/test-review.md` (Low); K-7; K-8 (`STU-MATEO-99`, R8-08); K-9 (umbrales PRD, `epics.md:605-614`).

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 5

| ID corrida 5 | Estado en corrida 6 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-13 `tea-skill-matrix.md:15` (132 nodos) | **Cerrado** | Fila trace: 155 nodos; "`gate-decision.json` no contiene cifras de nodos" | Ninguno |
| K-14 cita LedgerWriter (SEC B-01) | **Cerrado** | `epics.md:1092` cita `contracts.md §4` l.141 y `ports-and-adapters.md §1` l.53 | Ninguno |
| K-15 openapi 503 sin Clock/IdGenerator | **Cerrado** | `planning/detailed-design/schemas/openapi.yaml:510` | Ninguno |
| K-16 revoke R12-B01 sin RED | **Cerrado en el test; residuo en texto** | T-REV-12 `module1_revoke_contracts.test.py:406` (RED, `NotImplementedError`) | K-19 (`contracts.md:75`, `ports-and-adapters.md:53` aún dicen DEFER) |
| K-17 etiquetas CONS-n | **Cerrado** | `epics.md:1094-1098` ("ítem n del veredicto") | Ninguno |
| K-18 ancla "Tabla de Estados UX (l.673-694)" | **Cerrado** | `epics.md:1006`, `:1015` por nombre de sección; encabezado en `epics.md:686` | Ninguno |

Issues de corridas 1-5: sin cambios salvo lo indicado arriba.

### Sign-off

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

## Corrida 7

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK (CONCERNS)` (≡ CONCERNS; no READY, no FAIL)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run7.md` (corridas 1-6 conservadas en sus archivos).
**Issues de corrida 7:** 0 críticos, 0 mayores, 1 menor que bloquea (K-21). Cero defectos de implementabilidad.

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. Lo que impide READY: K-21, el gap G-1 (`planning/epics.md:851`) y la trazabilidad TEA (`test/traceability-matrix.md:141`, `:166`) siguen dando "T1 - T0 < 500 ms" como medición de la propagación de E2-S2, cuyo AC vigente es < 200 ms (`epics.md:256`).

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | `planning/prd.md:124,148,175,199` (4 FR); `planning/prd.md:291-297` (7 NFR); `epics.md:46-59` (inventario, 11 IDs presentes); `epics.md:47,49` (FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial declarado); `epics.md:730` (FR Coverage Map); 16/16 "Requisito fuente" |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | `epics.md:687` (tabla de Estados UX); `ux/C-UX-Scenarios/scenario-1.md:83` = 2.0 s vinculante, 1.2 s no vinculante (K-4 cerrado) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD en Binding. Tabla AD-n (`epics.md:710-724`) regenerada por `.work/regen_ad_table.py` en copia: 0 discrepancias, 0 node IDs inválidos. `pytest --collect-only -q` = 155 (incluye T-REV-12, T-RES-15 y T-ROS-21) |
| 4 | Sin dependencias hacia adelante | PASS | `epics.md:139-603` ("Depende de", 16 líneas, todas anteriores a la historia); `epics.md:652` (tabla de orden) |
| 5 | Artefactos sin contradicciones | CONCERNS (menor, documental; bloquea) | K-21: `epics.md:851` (G-1) y `test/traceability-matrix.md:141,166` dicen "< 500 ms" como medición de propagación; `epics.md:256` (E2-S2) y `epics.md:618` (umbrales) dicen 200 ms gate y 500 ms objetivo laxo. Códigos, rutas y DTOs coinciden (`openapi.yaml:367,510`; `prd.md:295`) |
| 6 | Hallazgos previos triageados y ACCEPT visibles | PASS con nota | Todos los IDs de `detailed-design/reviews/review-detailed-design.md` (ADVF-01..25 y ECF-01..30 en `epics.md`; ADVD-01..14 y EC-01..34 en su propia tabla, `review-detailed-design.md:8-66`); AR-01..14 y EC-01..16 (`epics.md:1004-1020`); raíz `reviews/` con ARCH-ADV-*, ARCH-EDGE-* (`epics.md:1066-1074`). Notas: K-7, K-8, K-9 abiertos no bloqueantes; L1 de test-review (Low) |

**Conteo:** 5 PASS (4 con nota), 1 CONCERNS (chequeo 5, K-21), 0 FAIL. El chequeo 6 queda en PASS con nota: K-21 no afecta a la triage de hallazgos previos.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningún chequeo en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones. E2-S2 fija el gate en < 200 ms. Lo que impide READY es el texto vigente de G-1 y de la trazabilidad, que dice 500 ms (K-21), tratado con la misma regla que K-13 y K-19.
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (P0 2/7; cobertura ejecutada 0% por diseño en RED; `test/traceability-matrix.md` §7). Gate `bmad-testarch-test-review` = Approve with Comments (L1 Low abierto). Este skill no los trata como bloqueantes.
- Históricos no contados como contradicción: `ai-log/decision-log-solu2.md:632` (K-20, Ronda 13), `planning/prd.md:193` (500 ms, prueba E2E de PRD §4.3, fuente correcta del objetivo laxo).

### (c) Concerns con mitigación propuesta

- **K-21 (menor, chequeo 5, bloquea).** Cambios exactos:
  - `planning/epics.md:851`: "Propagación `revocation_propagated_at`: T1 - T0 < 500 ms" → "Propagación `revocation_propagated_at`: T1 - T0 < 200 ms (gate NFR-REVOC-03; 500 ms = objetivo laxo PRD §4.3)".
  - `test/traceability-matrix.md:141`: "propagación `T1 - T0 < 500 ms` (G-1)" → "propagación `T1 - T0 < 200 ms` (G-1; objetivo laxo 500 ms de PRD §4.3)".
  - `test/traceability-matrix.md:166`: "sigue sin medir `T1 - T0 < 500 ms`" → "sigue sin medir `T1 - T0 < 200 ms`".
  - Skill: `bmad-create-epics-and-stories` (epics.md:851) y corrección directa de la traza (`bmad-testarch-trace`, o corrección directa como K-13).

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 6

| ID corrida 6 | Estado en corrida 7 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-19 (`contracts.md:75`, `ports-and-adapters.md:53`, "DEFER a TEA" en revoke R12-B01) | **Cerrado** | `contracts.md:75` y `ports-and-adapters.md:53` citan T-REV-12 `test_revoke_clock_failure_503_fail_closed_no_mutation` (E2-S3) con `[ACTUALIZADO 2026-10-14, K-19]`. T-REV-12 colectado en `test/atdd/module1_revoke_contracts.test.py:406` | Ninguno |

### (f) Verificación de K-20 (Ronda 13)

| ID | Estado en corrida 7 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-20 (E2-S2 citaba "< 500 ms" como AC) | **Cerrado en la historia; residuo en G-1 y trazabilidad** | `epics.md:256` (AC "T1 - T0 < 200 ms", con `[ACTUALIZADO 2026-10-14, K-20]`); fila "Umbrales triageados" en `epics.md:618` | **K-21**: `epics.md:851`, `test/traceability-matrix.md:141,166` |

Issues de corridas 1-6: sin cambios salvo lo indicado arriba.

## Corrida 8

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: NEEDS WORK (CONCERNS)` (≡ CONCERNS; no READY, no FAIL)
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run8.md` (corridas 1-7 conservadas en sus archivos).
**Issues de corrida 8:** 0 críticos, 0 mayores, 1 menor que bloquea (K-22). Cero defectos de implementabilidad.

**Salida del step-06 (resumen literal):** `Overall Readiness Status: NEEDS WORK (CONCERNS)`. Lo que impide READY: K-22, residuo de K-21 en `solu2-module1/test/traceability-matrix.md:63` (fila FR-REVOC-03): "Propagación `T1 - T0 < 500 ms` (G-1)", frente al AC de E2-S2 `planning/epics.md:256` (< 200 ms, gate NFR-REVOC-03).

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | `planning/prd.md:124,148,175,199` (4 FR); `prd.md:291-297` (7 NFR); `epics.md:46-59` (inventario); `epics.md:47,49` (FR-ESCAL-02 y FR-AUDIT-04 con alcance parcial declarado); `epics.md:730` (FR Coverage Map); 16/16 "Requisito fuente" |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | `epics.md:687-713` (Loading, Empty, Error, Success, Denied); `ux/C-UX-Scenarios/scenario-1.md:83` = 2.0 s vinculante, 1.2 s no vinculante (K-4 cerrado) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD en Binding; tabla AD-n regenerada en copia con `.work/regen_ad_table.py`: 0 discrepancias, 0 node IDs inválidos. `pytest --collect-only -q` = 155; `pytest -q` = 25 passed, 130 xfailed (todos `NotImplementedError`) |
| 4 | Sin dependencias hacia adelante | PASS | `epics.md:139-603` ("Depende de", 16 líneas, todas anteriores a la historia); `epics.md:652` (tabla de orden) |
| 5 | Artefactos sin contradicciones | CONCERNS (menor, documental; bloquea) | K-22: `test/traceability-matrix.md:63` ("T1 - T0 < 500 ms" como medición de FR-REVOC-03) vs `epics.md:256` (200 ms). Códigos, rutas y DTOs coinciden |
| 6 | Hallazgos previos triageados y ACCEPT visibles | PASS con nota | `planning/detailed-design/reviews/review-detailed-design.md`; `epics.md:1004-1020`; `epics.md:1066-1074`; raíz `reviews/`. Notas: K-7, K-8, K-9 abiertos no bloqueantes; L1 de test-review (Low) |

**Conteo:** 5 PASS (4 con nota), 1 CONCERNS (chequeo 5, K-22), 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **NEEDS WORK ≡ CONCERNS**. Ningún chequeo en FAIL.
- Prueba de implementabilidad: un desarrollador puede implementar las 16 historias sin inventar decisiones. E2-S2 fija el gate en < 200 ms. Lo que impide READY es un residuo textual de K-21 en la trazabilidad, tratado con la misma regla que K-13, K-19 y K-21.
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (P0 2/7; cobertura ejecutada 0% por diseño en RED; `test/traceability-matrix.md` §7). Gate `bmad-testarch-test-review` = Approve with Comments (L1 Low abierto).

### (c) Concerns con mitigación propuesta

- **K-22 (menor, chequeo 5, bloquea).** Cambio exacto: `solu2-module1/test/traceability-matrix.md:63`: "Propagación `T1 - T0 < 500 ms` (G-1)" → "Propagación `T1 - T0 < 200 ms` (G-1; objetivo laxo 500 ms de PRD §4.3)". Skill: `bmad-testarch-trace` o corrección directa de la traza (como K-13). No se aplicó en esta corrida (sin edición de diseño ni de evidencia TEA).

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status

No aplica. El veredicto no es READY (es NEEDS WORK), así que **no se generó** `solu2-module1/implementation-artifacts/sprint-status.yaml` (Parte B omitida).

### (e) Verificación de los issues de la corrida 7

| ID corrida 7 | Estado en corrida 8 | Dónde quedó | Pendiente |
|---|---|---|---|
| K-21 (500 ms residuales en E2-S2 y G-1 y trazabilidad) | **Cerrado en 4 de 4 puntos; residuo nuevo fuera de su lista** | `epics.md:242` (cita de fuente PRD, con AC 200 ms declarado), `epics.md:851` (G-1 = 200 ms), `test/traceability-matrix.md:141` y `:166` (= 200 ms) | **K-22**: `test/traceability-matrix.md:63` |

### (f) Verificación de K-21 (corrida 7, detalle)

| Punto | Estado | Evidencia |
|---|---|---|
| `planning/epics.md:851` (G-1) | **Cerrado** | "Propagación `revocation_propagated_at`: T1 - T0 < 200 ms (gate NFR-REVOC-03; 500 ms = objetivo laxo PRD §4.3)" |
| `test/traceability-matrix.md:141` | **Cerrado** | "propagación `T1 - T0 < 200 ms` (G-1; gate NFR-REVOC-03; objetivo laxo 500 ms de PRD §4.3) [ACTUALIZADO 2026-10-14, K-21]" |
| `test/traceability-matrix.md:166` | **Cerrado** | "FR-REVOC-03 sigue sin medir `T1 - T0 < 200 ms` (gate NFR-REVOC-03)" |
| `planning/epics.md:242` (requisito fuente de E2-S2) | **Cerrado como cita de fuente** | Conserva "propagación registrada < 500 ms" como cita de `prd.md:193` y declara "AC usa el umbral gate < 200 ms" |
| `test/traceability-matrix.md:63` (no listado en K-21) | **Abierto** | "Propagación `T1 - T0 < 500 ms` (G-1)" → K-22 |

Verificación de búsqueda: `grep -rn -e '500 ms' -e '500ms' -e '< 500' solu2-module1` (excluye `.venv`). Los demás 500 ms son NFR-AUDIT-06 (gate correcto), `test-design.md:142`, `nfr-evidence.md:18,42,45` o citas PRD (`epics.md:618`, `:851`).

Issues heredados abiertos (no bloquean): L1 de `test/test-review.md`; K-7; K-8 (`STU-MATEO-99`); K-9 (umbrales PRD, triados en `epics.md:605-618`).

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

## Corrida 9

**Fecha:** 2026-10-14 · **Veredicto (step-06):** `Overall Readiness Status: READY (≡ PASS)`
**Informe:** `solu2-module1/planning/implementation-readiness-report-2026-10-14-run9.md` (corridas 1-8 conservadas en sus archivos).
**Issues de corrida 9:** 0 críticos, 0 mayores, 0 menores que bloqueen. Ningún issue bloqueante nuevo.

**Salida del step-06 (resumen literal):** `Overall Readiness Status: READY (≡ PASS)`. K-22 cerrado: `test/traceability-matrix.md:63` alineado a 200 ms (gate NFR-REVOC-03); `test/nfr-evidence.md:15` aclarado (500 ms = prueba E2E PRD §4.3, objetivo laxo; gate `T_local < 200 ms`). Un desarrollador puede implementar las 16 historias sin inventar decisiones.

### (a) Salida del gate: tabla de los 6 chequeos

| # | Chequeo consigna | Resultado | Evidencia (archivo:línea) |
|---|---|---|---|
| 1 | FR/NFR -> historia y historia -> requisito | PASS con nota | `planning/prd.md:124,148,175,199` (4 FR); `prd.md:291-297` (7 NFR); `epics.md:46-59`; `epics.md:47,49` (alcance parcial FR-ESCAL-02 y FR-AUDIT-04); `epics.md:730`; 16/16 "Requisito fuente" |
| 2 | Estados UX con contrato + DTO o fuera de alcance justificado | PASS con nota | `epics.md:687-706`; `ux/C-UX-Scenarios/scenario-1.md:83` = 2.0 s vinculante (K-4 cerrado) |
| 3 | AD-01..AD-13 en Binding de >=1 historia y con test RED | PASS | 13/13 AD; tabla `epics.md:710-728` regenerada en copia con `.work/regen_ad_table.py`: 0 discrepancias, 0 node IDs inválidos. `pytest --collect-only -q` = 155; `pytest -q` = 25 passed, 130 xfailed (NotImplementedError) |
| 4 | Sin dependencias hacia adelante | PASS | `epics.md:139-603` (16 "Depende de", todas anteriores); `epics.md:652` |
| 5 | Artefactos sin contradicciones | PASS con nota | K-22 cerrado: `test/traceability-matrix.md:63`, `test/nfr-evidence.md:15`; `epics.md:256,851` y `traceability-matrix.md:141,166` en 200 ms. Códigos, rutas y DTOs coinciden |
| 6 | Hallazgos previos triageados y ACCEPT visibles | PASS con nota | `planning/detailed-design/reviews/review-detailed-design.md`; `epics.md:1004-1020`; `epics.md:1066-1074`; raíz `reviews/`; `ai-log/decision-log-solu2.md:634-635` (K-21, K-22). Abiertos no bloqueantes: K-7, K-8, K-9, L1 de test-review (Low) |

**Conteo:** 6 PASS (4 con nota), 0 CONCERNS, 0 FAIL.

### (b) Mapeo de veredictos

- READY ≡ PASS · NEEDS WORK ≡ CONCERNS · NOT READY ≡ FAIL.
- Veredicto de esta corrida: **READY ≡ PASS**.
- Hechos citados, sin severidad de readiness: gate `bmad-testarch-trace` = FAIL (cobertura ejecutada 0% por diseño en RED). Gate `bmad-testarch-test-review` = Approve with Comments (L1 Low abierto). Medición NFR PLANNED (G-16): no bloquea por diseño.

### (c) Concerns con mitigación propuesta

Ninguno (0 CONCERNS).

Sign-off arquitecto: PENDIENTE (A — Juan Pablo Parra)

### (d) Sprint status (Parte B)

Ruta: `solu2-module1/implementation-artifacts/sprint-status.yaml` (generado con la regla de clave de `bmad-sprint-planning`: `Story E<n>-S<m>` → `<n>-<m>-<título-kebab>`; epics `epic-<n>`; retrospectivas `epic-<n>-retrospective: optional`; todo en `backlog`; `implementation-artifacts/` no contenía stories, por lo que ninguna pasa a `ready-for-dev`). Metadato `project` entrecomillado porque el valor contiene `: ` (YAML inválido sin comillas, detectado en la primera validación y corregido).

Salida literal de validación:

```
$ ruby -ryaml -e 'YAML.load_file(ARGV[0]); puts "yaml-ok"' solu2-module1/implementation-artifacts/sprint-status.yaml
yaml-ok
$ ruby -ryaml ... (conteo)
epics=4 stories=16 retros=4 total=24
statuses=["backlog", "optional"]
project=Solu-2: University AI Compute Fabric, Module 1
$ ruby -ryaml ... (cobertura contra epics.md)
stories_in_epics=16 missing=0
retros_ok=true
```

Checklist de `bmad-sprint-planning`: 4 épicas, 16 historias, 4 retrospectivas presentes; sin items huérfanos; sin `action_items` previo que preservar; valores de estado legales (`backlog`, `optional`).

### (e) Verificación de K-22 (corrida 8)

| Punto | Estado | Evidencia |
|---|---|---|
| `test/traceability-matrix.md:63` | **Cerrado** | "Propagación `T1 - T0 < 200 ms` (G-1; gate NFR-REVOC-03; objetivo laxo 500 ms de PRD §4.3)" |
| `test/nfr-evidence.md:15` | **Aclarado** | Cita PRD §4.3 con "objetivo funcional laxo; el gate es `T_local < 200 ms`" [ACTUALIZADO 2026-10-14, K-22] |
| `ai-log/decision-log-solu2.md:635` | Registrado | "K-22 (readiness run8) ... ACCEPT. Aprobado por A." |

### Issues heredados (no bloquean)

- K-7 (nota de alcance FR-ESCAL-02 / FR-AUDIT-04), K-8 (`STU-MATEO-99`, triado R8-08), K-9 (umbrales PRD vs ARCHITECTURE, triados en `epics.md:605-618`), L1 de `test/test-review.md` (Low).

## Gate Drill


**Fecha:** 2026-10-14 · Ejecución: Gate Drill (Fase 4, Step 4.3) · Evidencia completa: `solu2-module1/test/evidence/gate-drill.md`.

### (a) Qué se rompió

Se eliminó la línea `- **Binding invariants:** AD-01, AD-10, AD-11. AD-09 (K-6: citados por tests de esta historia).` de la historia dedicada a EDGE-01, **E4-S1** (`epics.md:500` antes de la ruptura). Cambio único.

```
500d499
< - **Binding invariants:** AD-01, AD-10, AD-11. AD-09 (K-6: citados por tests de esta historia).
```

### (b) Qué reportó el gate sobre la versión rota

- Veredicto: **NEEDS WORK (≡ CONCERNS)**, sin FAIL. Informe: `.work/gate-drill/readiness-broken.md`.
- Detección: **sí**. Cita literal de la salida de `regen_ad_table.py`: `PROBLEMAS (test cita AD fuera del binding de su historia): 6`, con entradas como `AD-10: test/atdd/module1_contracts.test.py::TestEdge01::test_edge01_context_isolation (citado en E4-S1) no está en Binding invariants de E4-S1`. La historia afectada es E4-S1 y los AD afectados son AD-01, AD-09, AD-10 (la fila AD-n de `epics.md:712-728` quedó divergente del binding).
- Chequeos: 3 (AD en Binding y test RED) y 5 (artefactos sin contradicciones) pasaron a CONCERNS. Dos issues mayores (G-D1, G-D2), ambos bloqueantes para READY.
- Nota: el gate detectó la ruptura sin consultar el diff; el diff se usó solo después de la evaluación.

### (c) Corrección

- Skill que la arregló: `bmad-create-epics-and-stories` (modo edición, por indicación del gate). Se restauró la línea en su posición original, entre `Códigos de error` y `ATDD` de E4-S1.
- Nota de método: se leyó el SKILL.md de `bmad-create-epics-and-stories`, pero el cambio fue de una sola línea a partir del backup, sin re-ejecutar sus steps de creación completos.
- Verificación: `shasum -a 256` idéntico al backup y `diff` vacío (exit 0).

### (d) Duración

- Ruptura a restauración: 09:04:10 → 09:05:22, unos **1.2 min** (de ellos, la reejecución del gate roto ocupó 09:04:46 → 09:05:04).
- Drill completo (backup 09:04:05 → verificación final 09:05:28): unos **1.4 min** de trabajo ejecutado, más la lectura previa de instrucciones.

### (e) Veredicto tras restaurar

- **READY (≡ PASS)**, igual que corrida 9. Informe: `.work/gate-drill/readiness-restored.md`.
- Checks: 6 PASS (4 con nota), 0 CONCERNS, 0 FAIL. `regen_ad_table.py`: `PROBLEMAS: 0`. `pytest --collect-only` = 155; `pytest -q` = 25 passed, 130 xfailed.

### (f) Hashes

| Archivo | sha256 |
|---|---|
| `solu2-module1/planning/epics.md` (original, = backup `.work/gate-drill/epics.md.backup`) | `c9ca67329144ba814ab7a9fcaf611827eca057270eff6318e60e3b6ffc629c8a` |
| `solu2-module1/planning/epics.md` (versión rota) | `e3512341edf0ce1f49678e145f18721ca7a800a3091550488b2514190e717eaa` |
| `solu2-module1/planning/epics.md` (restaurado) | `c9ca67329144ba814ab7a9fcaf611827eca057270eff6318e60e3b6ffc629c8a` |

`sprint-status.yaml` no se regeneró, porque el gate restaurado es READY.

## Sign-off

- Veredicto READY (corrida 9) y Gate Drill aceptados.
- A — Juan Pablo Parra (Architect-lead): aprobado, 2026-10-14.
- B — Daniel Gonzalez (Test-lead): aprobado, 2026-10-14.
- Revisión conjunta de A y B de todas las decisiones del decision log antes de firmar.
- Las líneas "Sign-off arquitecto: PENDIENTE" de las corridas 1–8 son el estado histórico de cada corrida.
