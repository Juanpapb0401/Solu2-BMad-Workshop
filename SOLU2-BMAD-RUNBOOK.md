# Solu-2 con BMad: guía para correrlo fase por fase

## Qué es esta carpeta

`Solu2-BMad-Workshop/` es una **copia aislada** del paquete Plan-2. Conserva el PRD, la arquitectura, UX, escenarios, reportes y los 71 comandos/skills BMad. El PDF original y el Markdown de la consigna están en `references/`. El paquete manual anterior no se copió. El Plan-2 original no se va a modificar.

Los entregables nuevos van en `solu2-module1/`. El workspace no tiene Git todavía; no hagas commits, pushes ni tags hasta que decidamos qué repositorio de la clase usar.

> El Anexo A/Seed Table no aparece en `references/tas-2-solu2.md`; se extrajo del PDF en la página 13. La fila del Módulo 1 tiene exactamente estas tres candidatas: `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`. El usuario confirmó usar las tres y conservar el stack heredado el 2026-10-12. Su Mandatory Edge Case literal es: “Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently”. No reutilices como decisiones BMad las operaciones distintas del paquete manual previo.

## Estado actual — 14 de octubre de 2026

- **Fase 0: completa.** Las tres operaciones y el stack heredado quedaron confirmados el 2026-10-12. Evidencia: `solu2-module1/planning/detailed-design/architecture-spine/.memlog.md` y `solu2-module1/planning/roadmap.md`.
- **Fase 1: completa como fase de trabajo; gate final CONDITIONAL.** Hubo 9 corridas del Reviewer Gate de arquitectura (`solu2-module1/planning/detailed-design/architecture-spine/reviews/validation-gate-20261013*.md`): 1–6 NO PASS y 7–9 CONDITIONAL. La iteración se cerró por decisión del estudiante. No se marca PASS.
- **Fase 2: completa.** Artefactos en `solu2-module1/planning/detailed-design/` (DDL `schemas/001_module1_schema.sql`, `dto.py`, `events.md`, `openapi.yaml`, `roles_matrix.v0.json`). Review final: 55 hallazgos → 42 ACCEPT / 6 DEFER / 7 REJECT, aplicados (`reviews/review-detailed-design.md`).
- **Fase 3: completa como preparación de pruebas.** Suite ATDD RED: 130 `xfail` estrictos + 21 guardas + 4 de harness = 155 nodos; `pytest -q` → 25 passed, 130 xfailed. `quality_gate.sh` verde. Gate de trace del skill: FAIL por diseño (cobertura ejecutada 0% en RED). Test review: 100/100, Approve with Comments. NFR: todos PLANNED.
- **Fase 4: completa.** 4 épicas y 16 historias en `solu2-module1/planning/epics.md`. Readiness corridas 1–9: NOT READY, luego NEEDS WORK, y la corrida 9 da READY (≡ PASS). `solu2-module1/implementation-artifacts/sprint-status.yaml` generado. Gate Drill superado (`solu2-module1/test/evidence/gate-drill.md`).
- **Fase 5: en curso.** Hechos: ARCHITECTURE.md v2 (`planning/ARCHITECTURE.md`), decision log con resumen de la consigna, índice de entrega `solu2-module1/README.md`, renombre del DDL a `001_module1_schema.sql` con referencias actualizadas. Pendientes: sign-off de B (Daniel Gonzalez, revisión presencial), asignar responsables a los DEFER y preparar la entrega final. No hay Git: commit y tag quedan fuera.
- **Modo de trabajo:** el usuario prefiere ejecutar los slash commands en su OpenCode, uno por vez, y compartir aquí resultados para revisión. No marques un workflow como aprobado sin su gate o evidencia. Las aprobaciones delegadas quedan marcadas como tales en el decision log.

## Arranque en OpenCode

En la Terminal de macOS, pega:

```bash
cd "/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop"
opencode
```

En OpenCode ejecuta **un slash command por vez**. Deja que cada workflow muestre sus pasos/menús y respóndelos. No pegues todas las fases como una sola petición. Cuando termine cada comando, vuelve aquí y dime qué produjo o pásame el archivo; revisamos juntos antes de continuar.

OpenCode ya tiene proveedores configurados y en este workspace se verificaron 71 comandos y 71 skills BMad. Las rutas de salida de BMM y TEA se personalizaron para esta copia. Si `Estudiante` no es el nombre que quieres, cámbialo en `_bmad/bmm/config.user.yaml` y `_bmad/tea/config.user.yaml`.

## Contexto compartido para tus prompts

Puedes pegar este bloque al inicio de cada workflow si no conserva el contexto anterior:

```text
Estamos completando Unit 4 / Solu-2 para el Módulo 1, User, Role, and Subject Access Manager. Sigue los workflows BMad 6.10 instalados en este workspace y la consigna references/tas-2-solu2.md. Usa planning/prd.md, planning/ARCHITECTURE.md, ux/EXPERIENCE.md, ux/C-UX-Scenarios/scenario-1.md a scenario-4.md, reviews/ y docs/ como fuentes. Todos los nuevos artefactos van en solu2-module1/; no edites las fuentes de Plan-2 salvo la actualización explícita de la copia planning/ARCHITECTURE.md en Fase 0/5. No uses ../solu2-module1, porque es un borrador manual anterior y este proceso empieza desde cero con BMad. La entrega se detiene en solutioning: se permiten contratos, esquemas, interfaces/stubs y ATDD RED, pero no lógica productiva ni bmad-build/bmad-build-auto. Toda GPU, telemetría, Kubernetes, vLLM, reloj e identidad externa se simula detrás de ports/adapters. No inventes decisiones, requisitos ni resultados de workflows; marca [ASSUMPTION], registra contradicciones y pregunta cuando una decisión material siga abierta. Habla y escribe documentos en español, conservando literalmente IDs, enums, nombres de campos y umbrales del Plan-2.
```

## Fase 0: intake, selección y gap audit

### 0.1 Primero extrae el Anexo A y confirma las operaciones

Este chequeo ya se hizo en este workspace. Si quieres reproducirlo personalmente en tu sesión de OpenCode, usa este prompt; las operaciones y el stack ya están confirmados:

```text
La Seed Table del Annex A ya se extrajo del PDF, página 13, y el usuario confirmó usar las tres candidatas: `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)`. Verifica literalmente la fila del Módulo 1 y el Mandatory Edge Case “Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently”. Cruza las tres operaciones con `planning/prd.md`, los cuatro escenarios UX y `planning/ARCHITECTURE.md`; indica su cobertura de FR/NFR, la decisión automática explicable con rule IDs, las mutaciones/races y cómo `EDGE-01 Multi-Subject Permission Resolution` corresponde al seed. No agregues operaciones de otros módulos ni vuelvas a pedir confirmación de la selección o del stack. Presenta evidencia y contradicciones restantes; no inventes requisitos.
```

La tabla Annex A confirma el edge case multi-curso; mapea su texto exacto al identificador UX `EDGE-01 Multi-Subject Permission Resolution` y verifica si el PRD le asigna otro ID. Las tres operaciones core propuestas son resolución efectiva de permisos, revocación de acceso al curso e ingestión de roster. Los escenarios fuente también incluyen escalación temporal y auditoría forense; no los agregues como operaciones core salvo que una discrepancia del PRD lo exija y quede triageada.

La extracción literal está confirmada por PDFKit en la página 13. El usuario ya confirmó las tres operaciones y el stack heredado; no vuelvas a pedir esa confirmación. Antes de cerrar las disposiciones individuales del triage, conserva sus estados como propuesta o solicita la decisión del equipo.

### 0.2 Review adversarial

El paquete expone `/bmad-review-adversarial-general` (es el comando concreto que cumple el review adversarial; no existe que debamos asumir un genérico `/bmad-review`). Ya se ejecutó una vez en este workspace. Si quieres una corrida propia en OpenCode, ejecútalo así con la lista confirmada:

```text
/bmad-review-adversarial-general
Revisa adversarialmente la implementabilidad de `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`. Usa como alcance planning/ARCHITECTURE.md y como contexto planning/prd.md, ux/EXPERIENCE.md, los cuatro scenarios, reviews/review-*.md y la selección confirmada del Annex A. Busca decisiones que un agente de implementación tendría que inventar. Respeta la salida del skill: al menos 10 hallazgos concretos, sin etiquetas de severidad ni ranking. No modifiques fuentes. Conserva la salida cruda en solu2-module1/planning/detailed-design/reviews/review-arch-adversarial-raw.md.
```

Luego, en un mensaje normal, pide separar los hallazgos por **Accept / Defer / Reject**, indicando evidencia, fase de resolución y responsable A/B. Guarda esa tabla en `solu2-module1/planning/detailed-design/reviews/review-arch-implementability.md`; no alteres el formato obligatorio del resultado crudo del reviewer.

### 0.3 Review de edge cases

El comando real del bundle es `/bmad-review-edge-case-hunter`:

```text
/bmad-review-edge-case-hunter
Recorre exhaustivamente las ramas y límites de `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`. Usa la arquitectura y contratos fuente; incluye explícitamente el Mandatory Edge Case confirmado del Annex A, concurrencia, reintentos, estados vacíos, expiración y errores. Devuelve solo el JSON requerido por el skill, sin Markdown. Guarda exactamente esa salida cruda en solu2-module1/planning/detailed-design/reviews/review-arch-edge-cases-raw.json. No edites las fuentes.
```

Después triagea los edge cases en un mensaje separado y añade las decisiones a `review-arch-implementability.md`.

### 0.4 Stack y arquitectura

El usuario confirmó conservar FastAPI / Python 3.11+ / Pydantic v2 / SQLAlchemy 2.0 / SQLite WAL como baseline heredado, con PostgreSQL solo como alternativa documentada. No vuelvas a abrir la decisión sin un conflicto concreto en las fuentes. Declara el Clock port y registra la confirmación en el decision log; no cambies el Plan-2 original.

**Fase 0 queda lista** cuando: Annex A fue leído literalmente; hay 3+ operaciones aprobadas; se cubren las tres condiciones obligatorias; el gap audit tiene al menos 6 gaps triageados; y el stack quedó confirmado o deferido con responsable.

## Fase 1: contratos P / Q / I

Para continuar manualmente en OpenCode, usa `/bmad-architecture` con este prompt. Los dos archivos actuales son borradores de un intento interrumpido; revisa sus fuentes y completa el Reviewer Gate configurado antes de dar Fase 1 por terminada:

```text
/bmad-architecture
Fast path. Continúa la Fase 1 de Módulo 1 desde los borradores existentes: `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` y `solu2-module1/planning/detailed-design/contracts.md`. El intento anterior se interrumpió antes del Reviewer Gate final: no trates esos artefactos como aprobados y no asumas que un review de seguridad parcial equivale a gate completo. El usuario confirmó usar exactamente `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)`, `ingestRoster(batch)` y conservar Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite WAL con writer único. Trata AD-01..AD-07 de `planning/ARCHITECTURE.md` como heredadas y read-only; conserva AD-08..AD-13 como IDs locales del borrador o renumera solo si el propio skill detecta colisión documentada. Completa P/Q/I por operación, catálogo de errores e Invariant Binding Table con enforcement y test concreto. Contrasta cada regla con PRD, UX, escenarios y triage. No aceptes canonicalización que debilite el byte-a-byte de AD-01 sin registrar conflicto; no inventes estados o políticas abiertas. Corre `lint_spine.py`, rubric walk y todos los finalize reviewers configurados; verifica versiones con evidencia vigente. Guarda cada resultado real en `architecture-spine/reviews/`, corrige avisos que no sean parámetros válidos de ruta y deja cualquier contradicción material en `open_questions[]`/memlog. No implementes lógica productiva ni declares PASS sin el resultado completo del workflow.
```

Después ejecuta `/bmad-agent-architect`:

```text
/bmad-agent-architect
Winston, audita el contrato generado en solu2-module1/planning/detailed-design/contracts.md contra planning/ARCHITECTURE.md y planning/prd.md. Verifica uno por uno que cada invariante está ligado a un AD-n válido y a un enforcement/test verificable; señala IDs inexistentes, lenguaje elástico, huecos de P/Q/I y decisiones no registradas. No cambies los AD heredados ni implementes código. Devuelve hallazgos concretos para revisión humana.
```

## Fase 2: Ports & Adapters, DDL, DTO, eventos y OpenAPI

```text
/bmad-architecture
Continúa como diseño detallado, sin reabrir decisiones aprobadas de Fase 0/1. Produce en solu2-module1/planning/detailed-design/: ports-and-adapters.md con cada componente exactamente una vez y etiquetas de capa; schemas/001_module1_schema.sql con PK/FK, NOT NULL, CHECK, UNIQUE e invariantes físicamente enforced; dto.py con request/response/ErrorBody/ExplanationDTO; events.md con eventId, occurredAt UTC ISO-8601 y schemaVersion; y openapi.yaml con todas las rutas y errores tipados. El dominio no importa FastAPI, driver DB, datetime.now(), random ni red; tiempo/random entran por ports. GPUs/telemetría/cluster son simulados. Para carreras, serializa en DB; no uses SELECT-then-UPDATE. Resuelve explícitamente cualquier conflicto entre `audit_events` requerido por la consigna y `audit_ledger` existente en Plan-2. Después cruza cada cláusula I con la línea exacta de DDL/guard y anota la evidencia. No implementes lógica productiva.
```

Auditoría de Amelia:

```text
/bmad-agent-dev
Amelia, haz solo una auditoría de implementabilidad de `solu2-module1/planning/detailed-design/ports-and-adapters.md`, `schemas/001_module1_schema.sql`, `dto.py`, `events.md` y `openapi.yaml`. Revisa boundaries, firmas primitivas, aislamiento de dependencias, transacciones, interfaces de Clock/IdGenerator, y que GPU/telemetría/Kubernetes/vLLM sean adapters simulados. No implementes historias ni lógica. Devuelve discrepancias con ruta, cláusula/AD afectado y cambio mínimo sugerido.
```

El review adversarial de diseño dejó 14 hallazgos en `solu2-module1/planning/detailed-design/reviews/review-detailed-design-adversarial-raw.md`. El usuario ejecutó `/bmad-review-edge-case-hunter` en su OpenCode y guardó 34 objetos en `solu2-module1/planning/detailed-design/reviews/review-detailed-design-edge-cases-raw.json`.

Hay un triage provisional de los 14 hallazgos y los 34 edge cases en `solu2-module1/planning/detailed-design/reviews/review-detailed-design.md`. Revísalo con el equipo: `ACCEPT` indica una brecha propuesta, no aprobación de la solución; los `DEFER` y las correcciones sugeridas siguen pendientes de decisión cuando afectan comportamiento. Actualiza los artefactos después de acordar las decisiones. **No inicies Fase 3 hasta que el Reviewer Gate de Fase 1/2 tenga resultado aceptable y las decisiones materiales estén resueltas o asignadas.**

## Fase 3: TEA, preparación de pruebas

Ejecuta un comando por vez y guarda cada salida/evidencia.

### Test design

```text
/bmad-testarch-test-design
Create, system-level. Usa los contratos/ADs confirmados, el PRD y los cuatro escenarios. Produce solu2-module1/test/test-design.md: al menos 8 riesgos con probabilidad 1–3, impacto 1–3, score y prioridad P0–P3; el Mandatory Edge Case debe ser P0. Define niveles unit/contract/API/E2E, cobertura (100% de P0 con al menos un red test y objetivo de line coverage domain ≥90%) y testability gaps que regresan al gap audit. No marques riesgos como cubiertos sin test-ID.
```

### Framework

```text
/bmad-testarch-framework
Create scaffold solamente para módulo headless/API en Python 3.11+, pytest, pytest-asyncio y Hypothesis (no Playwright salvo que una UI esté realmente en alcance). Prepara fixtures obligatorias `fake_clock`, `seed_fleet` (31 × 1 GPU de 24 GB + 1 × 2 GPUs de 48 GB, healthy), `sim_telemetry`, `db` SQLite efímera en memoria migrada del DDL y `explain_assert` (regla IDs + valores observados). PostgreSQL no es el stack confirmado para esta entrega. No generes lógica productiva.
```

### ATDD RED

```text
/bmad-testarch-atdd
Create red-phase suite para las operaciones aprobadas. Escribe bajo solu2-module1/test/atdd/. La consigna contiene una discrepancia: el párrafo pide al menos 2 tests por operación/categoría y la tabla lista mínimo 1; usa la interpretación más estricta (2) y deja la nota para revisión humana. Incluye happy path Q, violación P sin mutación, invariantes bajo carrera/repetición/boundary, Mandatory Edge Case con aserción sobre estado final y explicabilidad con rule IDs. Cada test debe llamar un interface stub real y fallar por `NotImplementedError` o la causa contractual prevista; nada de `assert True`, tests vacíos ni lógica productiva. Asegura que pytest recolecta la suite. Reporta el node ID exacto de cada test.
```

### CI, NFR, test review y trazabilidad

```text
/bmad-testarch-ci
Create CI quality-gate scaffold para este repo y pytest. Corre el preflight del skill. No inventes remote/plataforma ni hagas push. Si el preflight se bloquea porque esta copia no tiene Git/remote, registra literalmente el bloqueo, lo que falta y la opción mínima; no digas CI PASS.
```

```text
/bmad-testarch-nfr
Create plan de evidencia, no auditoría de implementación: una fila por cada NFR del PRD con métrica/umbral exacto, herramienta/fixture/N/concurrencia, artefacto de evidencia y estado. Todo queda `PLANNED` mientras no haya medición real. Incluye al menos performance con concurrencia explícita, reliability/failure y security/isolation; separa los umbrales funcionales de escenarios de los NFR formales.
```

```text
/bmad-testarch-test-review
Create/review sobre `solu2-module1/test/atdd/`. Comprueba asserts reales, causas RED, fixtures, riesgos P0, edge case, carreras, aserciones de cero mutaciones/efectos laterales y descubrimiento pytest. No modifiques tests sin listar hallazgos y pedir revisión. Guarda el resultado en solu2-module1/test/test-review.md y completa tea-skill-matrix.md con workflows ejecutados, artefacto real y defecto atrapado.
```

```text
/bmad-testarch-trace
Create una matriz `solu2-module1/test/traceability-matrix.md`: cada PRD FR/NFR → escenario UX → AD-n → cláusula de contrato → Test ID/node ID → Story ID (cuando existan) → estado. En esta primera pasada, deja Story ID pendiente de Fase 4; no inventes IDs. Reporta huérfanos en ambos sentidos. Ningún P0 queda sin un red test.
```

## Fase 4: epics, historias y readiness gate

### Epics e historias

```text
/bmad-create-epics-and-stories
Create planning/epics.md dentro de `solu2-module1/`. Deben ser 3–4 epics verticales que den valor visible a protagonistas nombrados y 3–5 historias por epic (9–16 total). Epic 1 es walking skeleton con fixtures y un happy path por todas las capas/adapters simulados. Historias independientes, sin dependencias hacia el futuro. Cada historia enlaza requisito fuente PRD, escenario, contrato/DTO, errores, Binding invariants AD-n y Test IDs/node IDs. La Mandatory Edge Case y al menos dos estados de fallo tienen historias dedicadas. Revisa criterios de aceptación contra umbrales exactos; no crees historias huérfanas.
```

Tras crear epics, vuelve a correr `/bmad-testarch-test-design` en modo epic-level si el workflow lo requiere y `/bmad-testarch-trace` para completar Story IDs. Pide a Amelia revisar implementabilidad sin iniciar implementación.

### Readiness gate y sprint status

Antes del slash command, comprueba que las seis condiciones están cubiertas: FR/NFR completos y sin huérfanos; cada estado UX con contrato/DTO; cada AD-n en una historia y con test RED; no hay dependencias hacia adelante; artefactos sin contradicciones; todas las revisiones previas triageadas y Accepted corregidas.

```text
/bmad-sprint-planning
Ejecuta el readiness gate oficial de la consigna sobre `solu2-module1/planning/epics.md` y todos los artefactos de contratos/TEA. Verifica explícitamente las seis condiciones de la Fase 4, no solo que el YAML parsea. Emite PASS/IR-PASS, CONCERNS o FAIL con evidencia. Solo si es PASS genera `solu2-module1/planning/sprint-status.yaml` y verifica que contenga todos los epics, historias y retrospectives. Si el skill solo genera el archivo y no puede emitir veredicto de readiness, dilo tal cual: no fabriques PASS ni llames “certificado” al gate.
```

`bmad-sprint-planning` en este bundle también genera seguimiento de historias. Captura su salida real en `solu2-module1/planning/readiness-gate-report.md`; no sustituyas el workflow por un checker inventado.

### Gate Drill obligatorio

Hazlo únicamente después de tener backup. Dentro de esta copia, guarda `epics.md` en `.work/gate-drill/epics.md.backup`, elimina temporalmente un binding de una historia, corre el mismo gate y registra si lo detecta. Luego restaura el backup y vuelve a correr hasta PASS. Si el gate no detecta la ruptura, registra el defecto del gate; no maquilles el resultado. Guarda evidencia en `solu2-module1/test/evidence/gate-drill.md`. Si quieres, tráeme el archivo antes de restaurar y te guío para evitar perder cambios.

## Fase 5: cierre

1. Actualiza **solo la copia** `planning/ARCHITECTURE.md` a v2 para enlazar contracts, ports/adapters, esquema, DTO/events y OpenAPI; conserva los AD IDs estables.
2. Completa `solu2-module1/ai-log/decision-log-solu2.md` con prompts literales, modelo/agente usado, salida real, propuesta, decisión humana (Accept/Modify/Reject/Defer), razón, responsable y fecha. No inventes acuerdos de pareja.
3. Ejecuta de nuevo `/bmad-testarch-trace`; el 100% de requisitos P0 debe enlazar historia y test RED.
4. `/bmad-walkthrough` es opcional según la consigna; confirma que el comando exista en `/` antes de asumir que está instalado.
5. `git tag solu2-ready` solo después del PASS final y en el repositorio acordado. Esta copia no tiene Git ni commit inicial; no crees remoto, commit o tag sin definir primero el repo de entrega.

## Cómo trabajamos tú y yo

Después de cada fase, vuelve a este chat con el resultado de OpenCode o dime el path del artefacto creado dentro de `Solu2-BMad-Workshop/solu2-module1/`. Yo contrasto el contenido con la consigna, Plan-2 y el resultado real de BMad; corregimos juntos y recién ahí seguimos a la siguiente fase. El primer paso es extraer el Annex A y confirmar las operaciones.
