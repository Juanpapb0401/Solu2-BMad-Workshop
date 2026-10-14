---
workflowType: 'testarch-test-review'
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-quality-evaluation', 'step-03f-aggregate-scores', 'step-04-generate-report']
lastStep: 'step-04-generate-report'
lastSaved: '2026-10-14'
inputDocuments: ['solu2-module1/test/atdd/module1_contracts.test.py', 'solu2-module1/test/atdd/module1_guard_contracts.test.py', 'solu2-module1/test/conftest.py', 'solu2-module1/test/atdd/conftest.py', 'solu2-module1/test/fakes/world.py', 'solu2-module1/test/fakes/fake_queue.py', 'solu2-module1/test/fakes/fake_token_verifier.py', 'solu2-module1/test/test-design.md', 'solu2-module1/planning/detailed-design/contracts.md', 'solu2-module1/test/atdd-checklist.md']
---

> **Estado final (Re-revisión 3, 2026-10-14): 100/100 (A), Approve with Comments.** El cuerpo de abajo es la revisión original (79/100) con sus re-revisiones; las marcas `[SUPERADO ...]` indican lo que se corrigió después.
>
> **Triage de hallazgos** (revisado y aprobado por A y B, 2026-10-14; B = Test-lead):
>
> | Hallazgo | Severidad | Decisión | Razón | Dónde se ve el cambio |
> |---|---|---|---|---|
> | H5 archivo de 1185 líneas | High | ACCEPT | Dificulta revisar y mantener la suite | Suite dividida por operación (`test/atdd/module1_{resolve,revoke,ingest,ingest_rules,guard}_contracts.test.py`) |
> | M4 tests sin agrupar (contratos y guards) | Medium | ACCEPT | Agrupar por categoría hace legible la cobertura | Clases `TestHappyPath`, `TestEdge01`, `TestDDLGuards`, `TestDomainPurity`… |
> | L6 literal `3_600_000_000` | Low | ACCEPT | Literal mágico sin significado | Constantes con nombre en `test/atdd/atdd_support.py` |
> | Riesgo 1: conexión sqlite compartida entre hilos | Riesgo GREEN | ACCEPT | Fallaría por causa distinta de `NotImplementedError` | Conexión por hilo + barrier en T-CON-01 |
> | Riesgo 2: 422 sin conteo de tablas | Riesgo | ACCEPT | Rollback total (AD-02) exige probar no-efectos | `assert_no_writes` en intra-batch, T-ROS-03 y T-ROS-03b |
> | Riesgo 3: secreto en lote de ingesta | Riesgo | ACCEPT | AD-06 aplica también a ingesta | Test R-006 de ingesta |
> | H-N1 `_decision_of` sin definir | High | ACCEPT | NameError rompería el RED | `decision_of` importado de `atdd_support` |
> | M-N1 fake con código 401 de catálogo | Medium | ACCEPT | El fake no debe conocer el contrato HTTP | `test/fakes/fake_token_verifier.py` lanza `InvalidTokenError` |
> | M-N2 T-ROS-03 sin cuatro tablas ni `roster.rejected` | Medium | ACCEPT | Mismo motivo que Riesgo 2 | `assert_no_writes` en T-ROS-03 |
> | L2 contador de módulo `_seq` | Low | ACCEPT | Estado compartido entre tests | `_id` por tabla en `test/fakes/world.py` |
> | L3 RED concentrado en `_actor` | Low | ACCEPT | Un solo stub ocultaba qué operación falla | Un `NotImplementedError` por stub de dominio |
> | L4 `if` dentro de un test | Low | ACCEPT | Lógica condicional en tests | Eliminado |
> | L1 tres archivos > 600 líneas (738, 702, 625) | Low | DEFER | Están bajo el umbral del skill (1000); volver a dividir ahora mueve node IDs citados en `epics.md` y la trazabilidad sin ganancia de cobertura. Se revisa al pasar a GREEN | Sin cambio (owner B) |

# Test Quality Review: solu2-module1/test/atdd (Módulo 1)

**Quality Score**: 79/100 (C - Acceptable)
**Raw Deduction Score**: 95/100 [SUPERADO por Re-revisión 2: hoy raw 92/100]
**Score Cap**: 79/100 (High)
**Score Override Rule**: Highest severity High caps effective score at 79: min(raw deduction score 95, 79) = 79.
**Review Date**: 2026-10-14
**Review Scope**: directory
**Reviewer**: TEA Agent (Claude Haiku 5.5) para Juan Pablo Parra (A) y Daniel Gonzalez (B)

---

Note: This review audits existing tests; it does not generate tests.
Coverage mapping and coverage gates are out of scope here. Use `trace` for coverage decisions.

## Executive Summary

**Overall Assessment**: Acceptable

**Recommendation**: Request Changes
**Verdict Rule**: Critical = 0 and High > 0 => Request Changes (1 High).

**Context Basis**: pr_diff

**Context Waivers Applied**: 0

**Execution Mode**: sequential

### Key Strengths

✅ 48/48 pruebas atdd-red fallan por `NotImplementedError` (verificado: `pytest -q --runxfail -m atdd` → 48 failed, todas con `NotImplementedError`). Ninguna falla por colección, import o aserción previa. [SUPERADO por Re-revisión 2: hoy 116 atdd-red, no 48]
✅ Determinismo: sin `sleep`, sin azar, sin `datetime.now`; reloj y IDs inyectados (`FakeClock`, `FakeIdGenerator`), base SQLite por test (`tmp_path`).
✅ Rechazos con aserción de estado: los 400/403/404/409/413/503 comparan conteos de tablas y cola sin publicar; EDGE-01 verifica estado final (conteo de eventos y cadena).

### Key Weaknesses

❌ [H5] `solu2-module1/test/atdd/module1_contracts.test.py` mide 1185 líneas (>1000). [SUPERADO por Re-revisión 2: resuelto: el mayor archivo mide 652 líneas (umbral 1000)]
❌ [M4] `solu2-module1/test/atdd/module1_contracts.test.py:99` 48 tests planos sin agrupación. [SUPERADO por Re-revisión 2: resuelto: clases por operación]
❌ [M4] `solu2-module1/test/atdd/module1_guard_contracts.test.py:38` 5 tests planos sin agrupación. [SUPERADO por Re-revisión 2: resuelto: TestDDLGuards y TestDomainPurity]
❌ [L6] `solu2-module1/test/atdd/module1_contracts.test.py:231` literal `3_600_000_000` (microsegundos) sin nombre. [SUPERADO por Re-revisión 2: resuelto: constantes con nombre en atdd_support.py]

### Advisory Observations

ℹ️ Riesgo para GREEN (sin puntaje): `test_revoke_concurrent_double_drop_single_mutation` (`module1_contracts.test.py:692`) crea las conexiones `sqlite3` en el hilo principal (`sqlite3.connect` sin `check_same_thread=False`) y las usa dentro de hilos worker. Verificado: ese uso lanza `ProgrammingError`. En RED no aflora porque el stub lanza antes de tocar la BD; en GREEN fallará por una causa distinta de `NotImplementedError`. Corregir antes de implementar `revokeCourseAccess`. [SUPERADO por Re-revisión 2: conexiones por hilo resueltas; T-CON-01 tiene NameError (H-N1)]
ℹ️ Aserciones incompletas en rechazos 422 (sin puntaje, no hay fila del registro): `test_roster_intra_batch_duplicate` (`module1_contracts.test.py:1004`) solo mide `identities` y `subject_memberships`; `test_roster_no_role_smuggling` (`:1026`) no mide `identities` ni `roster_batches`. La regla S16 del checklist pide las cuatro tablas (`identities`, `subject_memberships`, `subject_credentials`, `roster_batches`) más la cola. [SUPERADO por Re-revisión 2: parcial: intra-batch y T-ROS-03b miden las 4 tablas; T-ROS-03 no (M-N2)]
ℹ️ Cobertura de riesgos P0 (sin puntaje): R-003 solo tiene el caso secuencial (`test_resolve_after_revoke_commit_denies_enrollment_dropped`), sin `resolve` concurrente con `revoke`; R-006 (secretos) solo cubre `drop_reason`, no respuestas de `resolve` ni `ingest`; T-RES-05, T-RES-07, T-RES-09, `QueueReservation` y `CredentialDeliveryPort` no tienen test (atdd-checklist.md, sección "Sin test en esta suite"). [SUPERADO por Re-revisión 2: parcial: T-CON-01 existe pero no ejecuta (H-N1); R-006 ampliado; CredentialDeliveryPort cubierto por T-ROS-04; T-RES-05 sigue sin test]
ℹ️ Duplicidad e IDs (sin puntaje): T-ROS-03 (`test_roster_no_role_smuggling`) y T-ROS-03b (`test_roster_role_smuggling_422_field_assigned_role`) describen el mismo escenario; T-REV-01 identifica a dos tests distintos; el docstring de `test_resolve_invalid_at_400_no_mutation` dice "sin zona explícita" pero el input lleva `Z`. [SUPERADO por Re-revisión 2: resuelto en R10]
ℹ️ `solu2-module1/test/fakes/world.py` mantiene un contador de módulo `_seq` sin reset. No altera resultados (solo genera IDs), pero los IDs cambian según el orden de ejecución; conviene reiniciarlo por fixture.
ℹ️ Las 48 pruebas llevan `xfail` estricto. Sin `--runxfail`, pytest reporta `9 passed, 48 xfailed`. Es el RED previsto; retirar el marcador al implementar cada test. [SUPERADO por Re-revisión 2: hoy 116 xfail; sin --runxfail: 16 passed, 116 xfailed]

### Summary

La suite RED cumple lo pedido en esta revisión: 48 atdd-red fallan solo por `NotImplementedError`, las guardas DDL pasan, el harness es determinista y EDGE-01 comprueba estado final. El único hallazgo puntuado de severidad alta es el tamaño del archivo principal (1185 líneas, H5), que además arrastra dos hallazgos de agrupación (M4) y un literal sin nombre (L6). La recomendación es Request Changes con puntaje 79 (C). Los riesgos de GREEN (conexiones SQLite entre hilos) y las aserciones incompletas en rechazos 422 no puntúan porque no tienen fila en el registro, pero deben cerrarse antes de implementar. Esta revisión no modificó tests ni código. [SUPERADO por Re-revisión 2: cifras de la revisión 1]

---

## Quality Criteria Assessment

| Criterion                            | Status             | Violations | Basis                                                  | Notes                                                                                                   |
| ------------------------------------ | ------------------ | ---------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| BDD Format (Given-When-Then)         | ✅ PASS (n/a)      | 0          | Convention: bddNaming (1 of 1 sampled)                 | Corpus fuera del set de 1 archivo, por debajo del mínimo de 4: no se infiere convención. Nombres describen comportamiento. |
| Test IDs                             | ✅ PASS (n/a)      | 0          | Convention: testIds (0 of 1 sampled)                   | Corpus de 1 archivo (<4): convención `unknown`. Sin puntaje.                                             |
| Priority Markers (P0/P1/P2/P3)       | ✅ PASS (n/a)      | 0          | Convention: priorityMarkers (0 of 1 sampled)           | Corpus de 1 archivo (<4): convención `unknown`. Los tests sí llevan `p0`/`p1`.                          |
| Disabled or Focused Tests            | ✅ PASS            | 0          | Absolute                                               | Sin `skip`, `only` ni `xit`. El RED usa `xfail` estricto declarado, no skip.                             |
| Hard Waits (sleep, waitForTimeout)   | ✅ PASS            | 0          | Absolute                                               | Sin `sleep`. Los `Barrier`/`join` tienen timeout pero no ordenan pasos.                                  |
| Determinism (no conditionals)        | ✅ PASS            | 0          | Absolute                                               | Sin `if`/`try` en el cuerpo de los tests, salvo el `if` que re-lanza errores de hilo (no oculta fallos). |
| Isolation (cleanup, no shared state) | ✅ PASS            | 0          | Absolute                                               | `tmp_path` y fakes nuevos por test. `_seq` (advisory) no cambia resultados.                              |
| Fixture Patterns                     | ✅ PASS            | 0          | Applicability                                          | Fixtures en `conftest.py`; helpers de `world.py`. M2 y M5 no disparan.                                   |
| Data Factories                       | ✅ PASS            | 0          | Applicability                                          | `roster_row`/`roster_batch` y seeds de `world.py`. No hay inserciones SQL inline en los tests.           |
| Network-First Pattern                | ✅ PASS (n/a)      | 0          | Applicability                                          | Sin navegación ni llamadas de red: M1 cerrado por su gate de aplicabilidad.                               |
| Playwright Utils Adoption            | ✅ PASS (n/a)      | 0          | Convention: playwrightUtils (0 of 1 sampled)           | Precondición de corrida falsa (sin `package.json`; stack Python). M9 y L9 no existen en esta corrida.     |
| Pact.js Utils Adoption               | ✅ PASS (n/a)      | 0          | Applicability                                          | Precondición `pactjsUtilsActive` falsa (sin `package.json`). M10 no existe en esta corrida.              |
| Explicit Assertions                  | ✅ PASS            | 0          | Absolute                                               | 196 `assert` en 48 tests (media 4.1). Sin C3, C4 ni H10. M6 no aplica (sin `async`).                      | [SUPERADO por Re-revisión 2: conteo de la revisión 1; hoy 369 aserciones atdd + 13 guard]
| Test Length (≤1000 lines)            | ❌ FAIL            | 1185 lines | Absolute                                               | `module1_contracts.test.py` supera 1000 líneas (H5, High). `module1_guard_contracts.test.py` mide 141.    | [SUPERADO por Re-revisión 2: hoy el mayor archivo mide 652 líneas]
| Test Duration (≤1.5 min)             | ✅ PASS            | 0.59 s     | Absolute                                               | Medido con `pytest -q --runxfail -m atdd` (48 tests, RED). Sin medición de GREEN.                         | [SUPERADO por Re-revisión 2: hoy 116 tests atdd: 0.58 s en RED]
| Flakiness Patterns                   | ✅ PASS            | 0          | Absolute                                               | Sin wall-clock, azar ni sleep. La concurrencia usa `Barrier` y el resultado no depende del orden.        |

**Total Violations**: 0 Critical, 1 High, 2 Medium, 1 Low [SUPERADO por Re-revisión 2: conteo de la revisión 1; ver Re-revisión 2]

**Convention Baseline**: 1 test files sampled outside the review set

---

## Quality Score Breakdown

```text
Starting Score:          100
Critical Violations:     -0 × 10 = -0
High Violations:         -1 × 5 = -5
Medium Violations:       -2 × 2 = -4
Low Violations:          -1 × 1 = -1

Bonus Points:
  Excellent BDD:         +5
  Comprehensive Fixtures: +0
  Data Factories:        +0
  Network-First:         +0
  Perfect Isolation:     +0
  All Test IDs:          +0
                         --------
Total Bonus:             +5

Raw Deduction Score:     95/100 [SUPERADO por Re-revisión 2: hoy raw 92/100]
Score Cap:               79/100 (High)
Effective Score:         79/100
Grade:                   C
```

---

## Critical Issues (Must Fix)

No critical issues detected. ✅

---

## Recommendations (Should Fix)

### 1. Archivo principal de 1185 líneas [SUPERADO por Re-revisión 2: resuelto (H5)]

**Severity**: P1 (High)
**Location**: `solu2-module1/test/atdd/module1_contracts.test.py:1`
**Row**: H5
**Criterion**: Test Length (≤1000 lines)
**Knowledge Base**: [test-quality.md](.agents/skills/bmad-testarch-test-review/resources/knowledge/test-quality.md)

**Issue Description**:
El archivo mide 1185 líneas y contiene los 48 tests de las tres operaciones más la sección de helpers. El umbral del registro es 1000 líneas y la regla H5 no admite excepción.

**Current Code**:

```python
# module1_contracts.test.py: 48 test_* planos en un único archivo de 1185 líneas
```

**Recommended Improvement**:
Dividir por operación, manteniendo el sufijo `_contracts.test.py` que exige `pytest.ini` (`python_files`): `resolve_contracts.test.py`, `revoke_contracts.test.py`, `ingest_contracts.test.py`. Los helpers `red`, `roster_row` y `roster_batch` pasan a un módulo común importable desde `test/atdd/`. El guard file no cambia.

**Benefits**:
Cada archivo queda bajo el umbral, un fallo localiza la operación y los helpers se importan una vez.

**Priority**:
P1: es el único hallazgo de severidad alta y condiciona el veredicto (Request Changes). Se corrige sin cambiar ningún test.

---

### 2. Suite de contratos sin agrupación [SUPERADO por Re-revisión 2: resuelto (clases por operación)]

**Severity**: P2 (Medium)
**Location**: `solu2-module1/test/atdd/module1_contracts.test.py:99`
**Row**: M4
**Criterion**: Ungrouped suite
**Knowledge Base**: [test-quality.md](.agents/skills/bmad-testarch-test-review/resources/knowledge/test-quality.md)

**Issue Description**:
Los 48 tests son funciones planas sin `class` ni agrupación por operación. Un fallo imprime solo el nombre de la función, sin el sujeto. Las secciones de comentario `# ====` no agrupan a nivel de pytest.

**Current Code**:

```python
@red("p0")
def test_resolve_allows_student_inference_cs480(db, module1, explain_assert):
```

**Recommended Improvement**:

```python
class TestResolveEffectivePermissions:
    @red("p0")
    def test_resolve_allows_student_inference_cs480(self, db, module1, explain_assert):
```

**Benefits**:
Los fallos se agrupan por operación en el reporte. Se resuelve junto con la recomendación 1.

**Priority**:
P2: no bloquea el veredicto por sí solo.

---

### 3. Guard file sin agrupación [SUPERADO por Re-revisión 2: resuelto]

**Severity**: P2 (Medium)
**Location**: `solu2-module1/test/atdd/module1_guard_contracts.test.py:38`
**Row**: M4
**Criterion**: Ungrouped suite

**Issue Description**:
Los cinco tests de guardas DDL son funciones planas sin agrupación.

**Current Code**:

```python
@pytest.mark.guard
@pytest.mark.p0
def test_guard_audit_ledger_update_rejected(db):
```

**Recommended Improvement**:
Agrupar los cuatro guards append-only en `class TestLedgerAppendOnly:` y el guard de unicidad en su propia clase.

**Benefits**:
Los fallos de DDL se localizan por tabla o invariante.

**Priority**:
P2: cosmético respecto al riesgo, pero es una violación Absolute del registro.

---

### 4. Literal de microsegundos sin nombre [SUPERADO por Re-revisión 2: resuelto]

**Severity**: P3 (Low)
**Location**: `solu2-module1/test/atdd/module1_contracts.test.py:231`
**Row**: L6
**Criterion**: Magic value

**Issue Description**:
`at_offset(3_600_000_000)` aparece sin nombre en la línea 231 y se repite en las líneas 235, 261, 356, 434, 831 y 854 con otros desfases (`3_599_999_999`, `600_000_000`, `4_200_000_000`, `301_000_000`, `300_000_000`). La unidad (microsegundos) y el significado (1 hora, 1 µs antes, 301 s) solo constan en docstrings. Se cuenta como una sola violación en la línea 231 porque el patrón es el mismo.

**Current Code**:

```python
expires = at_offset(3_600_000_000)
```

**Recommended Improvement**:

```python
ONE_HOUR_US = 3_600_000_000
ONE_US = 1
expires = at_offset(ONE_HOUR_US)
still_active = module1.resolve_effective_permissions(..., at_offset(ONE_HOUR_US - ONE_US))
```

**Benefits**:
El significado queda en el código y no solo en el docstring.

**Priority**:
P3: barato de corregir, sin riesgo para el veredicto.

---

## Best Practices Found

### 1. Fakes deterministas por puerto

**Location**: `solu2-module1/test/conftest.py:33-72`, `solu2-module1/test/fakes/fake_queue.py:14`
**Pattern**: Test doubles por puerto (reloj, IDs, cola, verificador de token) sin reglas de negocio
**Knowledge Base**: [test-quality.md](.agents/skills/bmad-testarch-test-review/resources/knowledge/test-quality.md)

**Why This Is Good**:
`FakeClock` avanza con `advance()` sin `sleep`. `FakeQueueReservation.set_capacity(0)` simula cola llena para probar el 503 fail-closed sin esperar nada.

**Code Example**:

```python
fake_queue.set_capacity(0)  # cola llena: el 503 AUTH_INTERNAL_POLICY_UNAVAILABLE se prueba sin timeouts
```

**Use as Reference**:
Usar el mismo patrón para el resto de puertos.

---

### 2. EDGE-01 con aserción de estado final

**Location**: `solu2-module1/test/atdd/module1_contracts.test.py:287-317` [SUPERADO por Re-revisión 2: EDGE-01 vive hoy en module1_contracts.test.py:57-86]
**Pattern**: Aserción sobre el estado final del ledger
**Knowledge Base**: [test-quality.md](.agents/skills/bmad-testarch-test-review/resources/knowledge/test-quality.md)

**Why This Is Good**:
`test_edge01_context_isolation` compara dos resoluciones de la misma identidad en contextos distintos, comprueba roles efectivos distintos, la ausencia de mezcla y el conteo final de eventos (`before_events + 2`).

**Code Example**:

```python
assert len(events(db, "authorization.decided")) == 2
assert len(events(db)) == before_events + 2
```

**Use as Reference**:
Patrón para los tests de no-mutación de las demás operaciones.

---

## Test File Analysis

### File Metadata

- **File Path**: `solu2-module1/test/atdd/module1_contracts.test.py` (1185 líneas, 51 KB) [SUPERADO por Re-revisión 2: hoy 452 líneas]
- **Test Framework**: pytest 8.3.4 con pytest-asyncio 0.24.0 (Python 3.11)
- **Language**: Python

- **File Path**: `solu2-module1/test/atdd/module1_guard_contracts.test.py` (141 líneas) [SUPERADO por Re-revisión 2: hoy 366 líneas]
- **Test Framework**: pytest 8.3.4
- **Language**: Python

### Test Structure

- **Describe Blocks**: 0 (funciones planas, sin `class`) [SUPERADO por Re-revisión 2: hoy hay 25 clases de test]
- **Test Cases (it/test)**: 48 (contracts) + 5 (guard) = 53 funciones de test [SUPERADO por Re-revisión 2: hoy 116 atdd + 12 guard + 4 harness]
- **Average Test Length**: ≈24 líneas por test (1185 / 48, incluye docstrings y bloques) [SUPERADO por Re-revisión 2: cifra de la revisión 1]
- **Fixtures Used**: 8 en `test/atdd/conftest.py` y `test/conftest.py` (db, module1, fake_queue, fake_clock, fake_id_generator, fake_token_verifier, explain_assert, edge_case_seeds)
- **Data Factories Used**: 2 locales (`roster_row`, `roster_batch`) + 6 helpers de `test/fakes/world.py` (add_identity, add_membership, add_credential, add_ticket, seed_student_pair, ensure_base)

### Test Scope

- **Test IDs**: T-RES-*, T-REV-*, T-ROS-*, T-LED-01, T-SEC-01, T-RES-08/08b, T-REV-08/08b, T-ROS-08/08b (nombres nominales de `contracts.md` §5 y del checklist)
- **Priority Distribution** (contracts / guard):
  - P0 (Critical): 29 / 5 [SUPERADO por Re-revisión 2: hoy atdd P0 54, guard P0 8]
  - P1 (High): 19 / 0 [SUPERADO por Re-revisión 2: hoy atdd P1 60, guard P1 4]
  - P2 (Medium): 0 / 0
  - P3 (Low): 0 / 0
  - Unknown: 0 / 0

### Assertions Analysis

- **Total Assertions**: 196 (contracts) + 6 (guard) en el cuerpo de los tests, más los helpers `assert_code_first`, `assert_cites_ad` y `explain_assert` [SUPERADO por Re-revisión 2: hoy 369 aserciones atdd + 13 guard (AST)]
- **Assertions per Test**: 4.1 (avg) en contracts; 1.2 en guard [SUPERADO por Re-revisión 2: hoy ~3,2 por test atdd]
- **Assertion Types**: `==`, `in`, `set(...) ==`, `pytest.raises` con `code`/`http_status`, `re.fullmatch`, recálculo de hash SHA-256, `pytest.raises(sqlite3.DatabaseError, match="append-only")`

---

## Context and Integration

### What the Context Said

Se leyeron, sin que añadieran hallazgos puntuables: `planning/detailed-design/contracts.md` (cláusulas P/Q/I), `test/test-design.md` (riesgos P0 R-001..R-009), `test/atdd-checklist.md` (trazabilidad y supuestos S1–S16), `planning/detailed-design/schemas/roles_matrix.v0.json` (filas v0 y `resource_catalog`), y los stubs de `app/`.

Verificado contra la matriz v0: EDGE-01 espera student en CS101 con `DENY` (fila `gpu` con `allow:false`), `ta` en CS-480 con `ALLOW` (fila `ta/inference`) y `instructor_privileged` sin fila en CS101 (`DENY` por fail-closed). Los tests `test_escalation_boundary_expires` y `test_edge01_escalation_in_cs480_does_not_alter_cs101` son coherentes con esa matriz.

El contexto añade dos hallazgos sin puntaje: el riesgo de GREEN de la concurrencia y la aserción incompleta de los 422. El contexto no elimina ninguna violación.

### Related Artifacts

- **Test Design**: [test-design.md](solu2-module1/test/test-design.md)
- **Risk Assessment**: 13 riesgos; P0 = 7 (R-001, R-002, R-003, R-004, R-006, R-008, R-009)
- **Priority Framework**: P0-P3 aplicado

---

## Knowledge Base References

This review consulted the following knowledge base fragments:

- **[test-quality.md](.agents/skills/bmad-testarch-test-review/resources/knowledge/test-quality.md)** - Definition of Done para tests (≤1000 líneas, sin hard waits ni condicionales, aserciones visibles, limpieza)

For coverage mapping, consult `trace` workflow outputs.

---

## Next Steps

### Immediate Actions (Before Merge) [SUPERADO por Re-revisión 2: ítems ejecutados en la Re-revisión 1; ver Re-revisión 2]

1. **Dividir `module1_contracts.test.py` por operación (H5)** - Dividir en tres archivos `*_contracts.test.py` y mover los helpers a un módulo común.
   - Priority: P1
   - Owner: Equipo ATDD (Juan Pablo Parra / Daniel Gonzalez)
   - Estimated Effort: 30-45 min (sin cambiar aserciones)

2. **Agrupar tests (M4) y nombrar el literal de microsegundos (L6)** - Clases por operación y constantes `ONE_HOUR_US`.
   - Priority: P2
   - Owner: Equipo ATDD
   - Estimated Effort: 15 min

### Follow-up Actions (Future PRs) [SUPERADO por Re-revisión 2: ítems 1 y 3 parciales; ver Re-revisión 2]

1. **Corregir la conexión SQLite entre hilos antes de GREEN** - `test_revoke_concurrent_double_drop_single_mutation`: abrir una conexión por hilo dentro del worker, o `check_same_thread=False` con justificación.
   - Priority: P2
   - Target: antes de implementar `revokeCourseAccess`

2. **Completar aserciones de no-mutación en 422** - Medir `subject_credentials`, `roster_batches` y la cola en `test_roster_intra_batch_duplicate` y `test_roster_no_role_smuggling`; fusionar T-ROS-03 con T-ROS-03b.
   - Priority: P2
   - Target: siguiente edición de la suite ATDD

3. **Cubrir R-003 con concurrencia real y R-006 en resolve/ingest** - Añadir un test de `resolve` concurrente con `revoke`; añadir comprobación de secretos en las respuestas de `resolve` e `ingest`.
   - Priority: P2
   - Target: backlog de la suite ATDD

### Re-Review Needed?

⚠️ Re-review after critical fixes - request changes, then re-review. [SUPERADO por Re-revisión 2: ver Re-revisión 2]

---

## Decision

**Recommendation**: Request Changes

**Rationale**:
El veredicto se calcula, no se elige: un High (H5, archivo de 1185 líneas) sin Critical fija Request Changes. El puntaje efectivo es 79 (C) porque el High limita el resultado al tope de 79. Los demás hallazgos son Medium y Low, y los riesgos de GREEN no puntúan porque no tienen fila en el registro. [SUPERADO por Re-revisión 2: H5 ya no aplica; el High vigente es H-N1]

La suite RED cumple su función: 48/48 fallan por `NotImplementedError` y no hay tests vacíos, desactivados ni tautológicos. El cambio necesario es estructural (dividir el archivo), sin tocar aserciones. [SUPERADO por Re-revisión 2: cifras de la revisión 1]

**For Request Changes**:

> Test quality needs improvement with 79/100 score. Critical issues must be fixed before merge. 0 critical violations detected; 1 High (H5, 1185 líneas) must be split before merge. [SUPERADO por Re-revisión 2: texto de la revisión 1; el High vigente es H-N1]

---

## Appendix

### Violation Summary by Location

| Line                                         | Severity | Criterion          | Issue                                  | Fix                                 |
| -------------------------------------------- | -------- | ------------------ | -------------------------------------- | ----------------------------------- |
| module1_contracts.test.py:1                  | P1 (High)| Test Length (H5)   | 1185 líneas (>1000)                    | Dividir por operación               | [SUPERADO por Re-revisión 2: resuelto (H5)]
| module1_contracts.test.py:99                 | P2 (Med) | Ungrouped suite (M4)| 48 tests planos                       | Clase por operación                 | [SUPERADO por Re-revisión 2: resuelto (M4)]
| module1_guard_contracts.test.py:38           | P2 (Med) | Ungrouped suite (M4)| 5 tests planos                        | Clase por invariante                | [SUPERADO por Re-revisión 2: resuelto (M4)]
| module1_contracts.test.py:231                | P3 (Low) | Magic value (L6)   | `3_600_000_000` sin nombre             | Constante `ONE_HOUR_US`             | [SUPERADO por Re-revisión 2: resuelto (L6)]

### Quality Trends

| Review Date  | Score         | Grade     | Critical Issues | Trend       |
| ------------ | ------------- | --------- | --------------- | ----------- |
| 2026-10-14   | 79/100        | C         | 0               | ➡️ Baseline |

---

## Review Metadata

**Generated By**: BMad TEA Agent (Test Architect)
**Workflow**: testarch-test-review v5.0 (ejecución manual secuencial, sin subagentes)
**Review ID**: test-review-atdd-20261014
**Timestamp**: 2026-10-14
**Version**: 1.0

---

## Feedback on This Review

If you have questions or feedback on this review:

1. Review patterns in knowledge base: `.agents/skills/bmad-testarch-test-review/resources/knowledge/`
2. Consult tea-index.csv for detailed guidance
3. Request clarification on specific violations
4. Pair with QA engineer to apply patterns

This review applies the rubric consistently. Context can reveal additional findings and clarify impact; it cannot waive a violation, change severity, or alter the score. Formal risk acceptance belongs in trace or the release gate.

---

## Reviewed Files

- solu2-module1/test/atdd/module1_contracts.test.py
- solu2-module1/test/atdd/module1_guard_contracts.test.py

## Review Context

- solu2-module1/test/conftest.py
- solu2-module1/test/atdd/conftest.py
- solu2-module1/test/fakes/world.py
- solu2-module1/test/fakes/fake_queue.py
- solu2-module1/test/fakes/fake_token_verifier.py
- solu2-module1/app/application/module1.py
- solu2-module1/app/domain/resolution.py
- solu2-module1/app/domain/membership.py
- solu2-module1/app/domain/roster.py
- solu2-module1/app/domain/errors.py
- solu2-module1/app/ports/identity.py
- solu2-module1/app/ports/stores.py
- solu2-module1/app/ports/inbound.py
- solu2-module1/app/ports/clock.py
- solu2-module1/app/ports/id_generator.py
- solu2-module1/app/adapters/http.py
- solu2-module1/app/adapters/sqlite_store.py
- solu2-module1/test/test-design.md
- solu2-module1/test/atdd-checklist.md
- solu2-module1/planning/detailed-design/contracts.md
- solu2-module1/planning/detailed-design/schemas/roles_matrix.v0.json

## Re-revisión tras correcciones (2026-10-14)

**Método:** misma rúbrica y libro de deducciones del paso 03f (CRITICAL×10, HIGH×5, MEDIUM×2, LOW×1; tope por la severidad más alta). Alcance: `test/atdd/module1_contracts.test.py`, `module1_resolve_contracts.test.py`, `module1_revoke_contracts.test.py`, `module1_ingest_contracts.test.py`, `module1_ingest_rules_contracts.test.py`, `module1_guard_contracts.test.py` y `test/atdd/atdd_support.py`.

**Estado de cada hallazgo:**

| Hallazgo | Severidad | Estado | Evidencia |
| --- | --- | --- | --- |
| H5 archivo principal de 1185 líneas | High | RESUELTO | Dividido por operación. Líneas por archivo: resolve 449, revoke 492, ingest 594, ingest_rules 166, contracts 451, guard 254. Todos < 600. | [SUPERADO por Re-revisión 2: la cifra 'Todos < 600' es falsa hoy: ingest 652, resolve 618]
| M4 suite plana (`module1_contracts`) | Medium | RESUELTO | Clases por categoría: TestHappyPath, TestPreconditions, TestInvariants, TestEdge01, TestExplainability, TestSecrets, TestConcurrency, TestSchedulerSweep, TestHttpMapping, TestTransversalAD, TestLedgerChain. |
| M4 guard file | Medium | RESUELTO | TestDDLGuards (DDL) y TestDomainPurity (AD-08). |
| L6 literal de microsegundos | Low | RESUELTO | Constantes con nombre en `atdd_support.py` (ONE_HOUR_US, TEN_MINUTES_US, FIVE_MINUTES_US, FIVE_MINUTES_ONE_SECOND_US, SEVENTY_MINUTES_US, ONE_MICROSECOND). Sin literales fuera de esa definición. |
| Riesgo 1: conexión SQLite compartida entre hilos | Sin puntaje | RESUELTO | `run_concurrently` + `db_path`: cada worker abre y cierra su propia conexión dentro del hilo; barrera de inicio. Aplica a T-REV-07 y T-CON-01. Los IDs de hilo usan `ThreadSafeIdGenerator`. |
| Riesgo 2: 422 sin conteo de las cuatro tablas | Sin puntaje | RESUELTO | `assert_no_writes` compara identities, subject_memberships, subject_credentials y roster_batches antes y después. Aplicado a intra-batch y role smuggling; row85 y role_smuggling_422 ya medían; los rechazos nuevos lo usan. | [SUPERADO por Re-revisión 2: parcial: T-ROS-03 sigue sin las cuatro tablas (M-N2)]
| Riesgo 3: R-006 en ingest | Sin puntaje | RESUELTO | T-SEC-ROS-01 (secreto en campo del lote, manifiesto y logs). Además T-RES-14 (secreto en `action`) y T-SEC-REV-01 (rechazo y revocación). |
| Seguimiento: R-003 con concurrencia real | Sin puntaje | RESUELTO | T-CON-01: resolve concurrente con revoke; tras el commit, DENY SUBJECT_ENROLLMENT_DROPPED. | [SUPERADO por Re-revisión 2: no ejecuta: T-CON-01 tiene NameError (H-N1)]
| Aviso: docstring de `test_resolve_invalid_at` decía "sin zona" | Sin puntaje | RESUELTO | La entrada lleva `Z` y le faltan microsegundos; el docstring se corrigió. |
| Aviso: T-ROS-03 y T-ROS-03b describen el mismo escenario | Sin puntaje | RESUELTO (R10) | Diferenciados por aserciones: T-ROS-03 = estado persistido (rol, membresías, credenciales); T-ROS-03b = manifiesto 422 y evento `roster.rejected`. |
| Aviso: Test ID T-REV-01 duplicado en dos tests | Sin puntaje | RESUELTO (R10) | `test_revoke_preserves_other_course` pasa a T-REV-01b; T-REV-01 queda solo para `test_revoke_all_credentials`. |
| Nuevo: 3 tests de 401 pasan en verde al primer intento | Sin puntaje | DOCUMENTADO | `Module1Service` verifica el bearer antes del dominio, así que no son atdd-red. Pasaron a `guard` (T-REV-11, T-ROS-20, T-RES-12) con nota en el docstring. Un RED estricto sería un falso RED. | [SUPERADO por Re-revisión 2: falso: siguen en atdd-red (causa `_actor`); no pasaron a guard]

**Nuevos tests RED y guardas añadidos (no puntúan):** 90 atdd-red (xfail estricto, causa `NotImplementedError`) y 12 guardas en verde. Cubren RESOURCE_SUBJECT_MISMATCH, EDGE-01 regla 4, AUTH_TOKEN_INVALID, AUTH_INTERNAL_POLICY_UNAVAILABLE, R8-01, AD-07, R8-06, barrido, parsing HTTP, mapeo AD-09, NFR-SEC-05, dominio de correo, caracteres de control, pureza AD-08 y AD-05. [SUPERADO por Re-revisión 2: cifra falsa: hoy 116 atdd-red y 12 guard]

**Puntaje:**
- Deducciones abiertas con puntaje: ninguna (no quedan High, Medium ni Low puntuados). [SUPERADO por Re-revisión 2: falso: hay hallazgos nuevos; ver Re-revisión 2]
- Raw deduction score: 100/100. Tope por severidad: no aplica. [SUPERADO por Re-revisión 2: superseded: hoy raw 92/100]
- Puntaje efectivo: **100/100 (A)**. [SUPERADO por Re-revisión 2: superseded: hoy 79/100 (C)]
- Nota de trazabilidad: el original reportó raw 95 con cap 79. El libro vigente da 100 − (5 + 2×2 + 1) = 90 raw, y el cap 79 se mantiene. La diferencia con el 95 original no cuadra con la fórmula; no se recalculó el original.

**Recomendación:** Approve with Comments. No quedan Critical ni High, el puntaje efectivo es ≥ 70 y siguen abiertos dos avisos sin puntaje (T-ROS-03/03b y T-REV-01). El puntaje evalúa calidad del código de test, no la implementación: la suite sigue en RED hasta GREEN. [SUPERADO por Re-revisión 2: superseded: hoy Request Changes]

**Re-revisión necesaria:** no, salvo que se cierren los avisos abiertos antes de GREEN. [SUPERADO por Re-revisión 2: superseded; ver Re-revisión 2]


## Re-revisión 2 (2026-10-14, post Rondas 9-10)

**Alcance y método.** Misma rúbrica y libro de deducciones del paso 03f (CRITICAL×10, HIGH×5, MEDIUM×2, LOW×1; tope por la severidad más alta; bonus 0/5 en seis categorías). Revisados: `test/atdd/` completo (seis archivos `module1_*_contracts.test.py`, `atdd_support.py`, `atdd/conftest.py`), `test/conftest.py`, `test/fakes/` (cuatro dobles y `world.py`), `test/test_harness_smoke.py` y los stubs de `app/` (solo lectura). Se verificó por AST y por ejecución. No se ejecutó GREEN y no se modificaron tests, código, diseño ni `epics.md`.

### Conteos actuales (verificados)

| Medida | Valor | Fuente |
| --- | --- | --- |
| Colección total | 132 | `.venv/bin/pytest --collect-only -q` |
| atdd-red | 116 | contracts 19, ingest 29, ingest_rules 9, resolve 28, revoke 31 |
| guard | 12 | 11 de DDL y 1 de pureza de dominio (`module1_guard_contracts.test.py`) |
| harness | 4 | `test_harness_smoke.py` |
| Ejecución por defecto | 16 passed, 116 xfailed | `.venv/bin/pytest -q` |
| Causa RED | 116 `NotImplementedError` | `--runxfail -m atdd --tb=line`: 101 en `app/application/module1.py:33` (`_actor`), 9 en `app/adapters/http.py`, 4 en `app/domain/scheduler.py`, 2 en `app/domain/pagination.py` |
| Marcadores atdd | P0 54, P1 60, P2 2; edge_case 4; explainability 6 | `-m` |
| Marcadores guard | P0 8, P1 4 | `-m` |
| Aserciones (AST) | 369 atdd, 13 guard; 25 clases | AST |
| Duración RED | 0,58 s | `pytest -q` |

### Puntaje

Por dimensión (solo deducciones de la dimensión; sin bonus por dimensión):

| Dimensión | Hallazgos | Puntaje | Grado |
| --- | --- | --- | --- |
| Determinismo | L4 | 99 | A |
| Aislamiento | L2 | 99 | A |
| Mantenibilidad | H-N1, M-N1, M-N2, L1, L3 | 79 (tope High) | C |
| Rendimiento | ninguno (0,58 s en RED; GREEN no medido) | 100 | A |

Global: deducciones 13 (HIGH 1×5 + MEDIUM 2×2 + LOW 4×1); bonus 5 (`excellentBdd`: los nombres describen comportamiento; los otros cinco criterios valen 0 porque las fixtures y factories son parciales, network-first no aplica, el aislamiento no es perfecto por `_seq` y allTestIds no aplica). Raw = 100 − 13 + 5 = 92. Tope High = 79. **Puntaje efectivo: 79/100 (C).** Veredicto calculado: **Request Changes** (Critical = 0, High = 1).

### Estado de los hallazgos previos

| Hallazgo | Estado | Evidencia |
| --- | --- | --- |
| H5 archivo de 1185 líneas | RESUELTO | Mayor archivo: 652 líneas (`module1_ingest_contracts.test.py`); umbral 1000 cumplido |
| M4 suite plana (contracts) | RESUELTO | Clases por operación y categoría (`module1_contracts.test.py:53,134,176,199,248,334,433`) |
| M4 guard plano | RESUELTO | `TestDDLGuards` y `TestDomainPurity` (`module1_guard_contracts.test.py:81,352`) |
| L6 literal `3_600_000_000` | RESUELTO | Constantes con nombre en `atdd_support.py`; sin literales de microsegundos en los tests |
| Conexión SQLite compartida entre hilos | RESUELTO en el helper | `run_concurrently` y una conexión por hilo (`module1_revoke_contracts.test.py:444`, `module1_contracts.test.py:219`); su consumidor T-CON-01 tiene H-N1 |
| Riesgo 2: 422 sin cuatro tablas | PARCIAL | Intra-batch (`module1_ingest_contracts.test.py:262`) y T-ROS-03b (`:548`) usan `assert_no_writes`; T-ROS-03 no (M-N2) |
| Riesgo 3: R-006 en ingest | RESUELTO | `module1_ingest_rules_contracts.test.py:182` (T-SEC-ROS-01); además `module1_resolve_contracts.test.py:597` y `module1_revoke_contracts.test.py:529` |
| R-003 con concurrencia real (T-CON-01) | ROTO | `module1_contracts.test.py:202`: NameError (H-N1) |
| Aviso: docstring "sin zona" | RESUELTO | `module1_resolve_contracts.test.py:195` |
| T-ROS-03 y T-ROS-03b | RESUELTO | Alcances distintos: estado (`module1_ingest_contracts.test.py:483`) y manifiesto (`:548`) |
| T-REV-01 duplicado | RESUELTO | `module1_revoke_contracts.test.py:84` (T-REV-01) y `:366` (T-REV-01b) |
| Tres tests de 401 "pasaron a guard" | FALSO | Siguen en atdd-red: `module1_resolve_contracts.test.py:284`, `module1_revoke_contracts.test.py:219`, `module1_ingest_contracts.test.py:294`. Fallan por `_actor` (NotImplementedError), que es RED legítimo. Ver M-N1 |
| Advisory `_seq` (world.py) | SIGUE | L2 |
| Cobertura P0 (R-003, R-006, CredentialDeliveryPort) | PARCIAL | R-006 y CredentialDeliveryPort cubiertos (T-ROS-04); R-003 no ejecuta (H-N1); T-RES-05 sigue sin test |

### Hallazgos nuevos

**HIGH**

- **H-N1 (HIGH, −5)** `solu2-module1/test/atdd/module1_contracts.test.py:232` y `:242`: usan `_decision_of`, que no está definido ni importado. `atdd_support.py:128` define `decision_of`. T-CON-01 (`module1_contracts.test.py:202`) falla con NameError en el worker de resolve. En RED queda enmascarado: el worker de revoke (índice 0) relanza primero el `NotImplementedError` de `_actor`, y `xfail(raises=NotImplementedError)` se cumple. En GREEN fallará por causa ajena al producto. Corrección: importar `decision_of` desde `atdd_support` y usarlo en `:232` y `:242`. Hasta corregirlo, la igualdad "116 NotImplementedError = 116 atdd" no demuestra la causa de T-CON-01.

**MEDIUM**

- **M-N1 (MEDIUM, −2)** Aserción 401 producida por el doble: `module1_resolve_contracts.test.py:302-306`, `module1_revoke_contracts.test.py:237-241` y `module1_ingest_contracts.test.py:311-315` asertan `AUTH_TOKEN_INVALID`/401, y ese código lo fija el doble en `solu2-module1/test/fakes/fake_token_verifier.py:26`. El producto podría propagar la excepción del doble y pasar sin definir su mapeo. No es tautología (el producto sí debe llamar al verificador y no alterar la respuesta), pero el contrato no se verifica contra el catálogo del producto. Corrección: que el doble lance un error neutro y asertar el mapeo en el producto.
- **M-N2 (MEDIUM, −2)** `module1_ingest_contracts.test.py:483-506` (T-ROS-03, rechazo 422 por anti-smuggling): solo mide `subject_memberships` y `subject_credentials`. No mide `identities`, `roster_batches` (`REJECTION_TABLES`, `atdd_support.py:87`) ni `roster.rejected` (regla S3). T-ROS-03b (`:548`) sí cubre el conjunto. Corrección: `assert_no_writes(before, counts(db))` y `len(events(db, "roster.rejected")) == 1`.

**LOW**

- **L1 (LOW, −1, mantenibilidad)** Convención interna incumplida: `module1_ingest_rules_contracts.test.py:4` declara "cada archivo < 600 líneas"; hoy `module1_ingest_contracts.test.py` mide 652 y `module1_resolve_contracts.test.py` 618. El umbral del registro (1000) sí se cumple. Corrección: ajustar la convención o dividir.
- **L2 (LOW, −1, aislamiento)** `solu2-module1/test/fakes/world.py:28` (`_seq = itertools.count(1)`) y `:37`: contador de módulo compartido entre tests. Los IDs de membresía, ticket y credencial dependen del orden de ejecución. No cambia veredictos, pero impide el bono perfectIsolation. Corrección: contador por fixture o reinicio en `ensure_base`.
- **L3 (LOW, −1, mantenibilidad)** RED concentrado en un stub: 101 de 116 fallan en `solu2-module1/app/application/module1.py:33` (`_actor`), antes de llegar al dominio. Así, los tests de la fachada no ejercitan en RED `resolveEffectivePermissions`, `revokeCourseAccess` ni `ingestRoster`. No es falso verde, pero la evidencia RED no demuestra por operación el stub de dominio. Corrección: tests directos de dominio para las tres operaciones, o declarar la limitación en la evidencia.
- **L4 (LOW, −1, determinismo)** `module1_ingest_contracts.test.py:438-439`: `if body_subject is not None:` dentro del test para construir el body. Corrección: parametrizar con dos bodies explícitos.

Total: 1 HIGH, 2 MEDIUM, 4 LOW, 0 CRITICAL.

**No puntuados (cobertura; el checklist deja la cobertura a `trace`):**
- T-RES-05 (P0, `test/test-design.md:82`): captura única de `request_now`; sin test, documentado en `atdd-checklist.md:238`.
- T-RES-07 y T-RES-09 (P1, bloqueados por OPEN H-17 y H-26): sin test.
- `AUDIT_LOG_TAMPERING_DETECTED` (G9 de `traceability-matrix.md`): sin test.
- `QueueReservation` (AD-12): solo ejercitado mediante el doble en los 503; sin test directo.

### Verificaciones solicitadas

- **Causa RED:** 116 líneas `NotImplementedError` = 116 atdd. H-N1 muestra que la igualdad no basta: un test con causa real NameError puede contarse como RED.
- **Tautologías:** ninguna. AST sobre los 132 tests: 0 aserciones `x == x`, 0 `assert` constante, 0 tests sin aserción ni `pytest.raises`. Los 16 tests verdes son guards de DDL y pureza (12) y harness (4). Sus aserciones se contrastan con el DDL real (`001_module1.sql` vía `db`) o con el código de `app/domain/` por AST, no con un doble que el propio test configura. Las dos aserciones del harness (`test_fake_clock_advances`, `test_fake_id_generator_deterministic`) prueban los dobles por diseño.
- **Cero mutación en rechazos:** se cumple en los 400, 403, 404, 409, 413, 503 y 422 de `ingest` mediante `counts` o `assert_no_writes`, con la excepción de M-N2.
- **P0:** cubiertos por tests atdd R-001 (EDGE-01 y RESOURCE_SUBJECT_MISMATCH), R-002, R-003 (salvo ejecución por H-N1), R-004 (cadena de ledger y cola), R-006, R-008 (salvo T-RES-05) y R-009 (DENY temporal). T-RES-05 sin test.
- **Determinismo:** reloj (`FakeClock`), IDs (`FakeIdGenerator`, `ThreadSafeIdGenerator`), `tmp_path` por test, sin `sleep`, `random`, `datetime.now` ni red. Concurrencia con barrera y `join(timeout)`. Excepciones: L2 y L4.
- **Aislamiento:** `db` nueva por test, dobles nuevos por test, una conexión SQLite por hilo. Excepción: L2.
- **Lógica productiva en `app/`:** ninguna. `app/domain/*`, `app/adapters/http.py`, `app/adapters/sqlite_store.py` y `app/ports/*` contienen solo `raise NotImplementedError` o ABC con stubs. `Module1Service` guarda atributos y delega; `_actor` lanza `NotImplementedError`. `Module1Error` solo transporta datos.

### Correcciones al cuerpo previo

Cada afirmación hoy falsa de las secciones anteriores lleva el marcador `[SUPERADO por Re-revisión 2: ...]`; el texto original se conserva. Siguen vigentes: los Key Strengths de determinismo, rechazos con aserción de estado y EDGE-01, y la sección Best Practices.

### Recomendación

**Request Changes** (High = 1: H-N1). Corregir H-N1 (un import y dos usos) y M-N2 requiere nueva re-revisión. Sin modificar nada más, la corrección de H-N1 dejaría 2 MEDIUM y 4 LOW: puntaje 89 (B) y veredicto Approve with Comments.

Correcciones post Re-revisión 2 aplicadas (2026-10-14): (1) H-N1: `_decision_of` reemplazado por `decision_of` de `atdd_support.py` en `module1_contracts.test.py` (T-CON-01 ya no da NameError); (2) RED concentrado: `Module1Service` sin `_actor`, pasa `bearer` y `token_verifier` a los stubs de dominio; cada stub lanza su `NotImplementedError` (116/116 atdd-red por NotImplementedError); (3) M-N1: el fake lanza `InvalidTokenError` del puerto, sin `AUTH_TOKEN_INVALID`/401 en `test/fakes/`; (4) M-N2: T-ROS-03 con `assert_no_writes` y `roster.rejected` = 1; (5) L2: `if` eliminado del parametrize de T-ROS-G-08 y `_seq` global reemplazado por conteo por tabla en `world.py`; (6) guard: fixtures `"0" * 64` pasan a `ARBITRARY_PREV_HASH` (no es GENESIS); atdd-checklist.md actualizado (S10, S15, fila de T-ROS-03).

## Re-revisión 3 (2026-10-14)

**Alcance y método.** Misma rúbrica y libro de deducciones (CRITICAL×10, HIGH×5, MEDIUM×2, LOW×1; `score = max(0, min(100, inicio − infracciones + bonus))`, paso 03f de `checklist.md`). Revisados: `test/atdd/` completo, `test/fakes/`, `test/atdd/atdd_support.py` y `app/` (solo lectura). Verificaciones por grep, AST y ejecución. No se modificó ningún test, código, diseño ni `epics.md`. Sin GREEN.

### Conteos actuales (verificados)

| Medida | Valor | Fuente |
| --- | --- | --- |
| Colección total | 152 | `.venv/bin/pytest --collect-only -q` |
| atdd-red | 127 | `test/atdd/`: 127 nodos con `@red`; `-m atdd --runxfail` = 127 failed |
| guard | 21 | 12 previas + 9 nuevas (H-21c 1, H-25 7, F-06 1) |
| harness | 4 | `test_harness_smoke.py` |
| Ejecución por defecto | 25 passed, 127 xfailed | `.venv/bin/pytest -q` |
| Causa RED | 127 `NotImplementedError` | `--runxfail -m atdd --tb=line` + `grep NotImplementedError \| sed \| cut \| sort \| uniq -c`: `ingestRoster` 37, `revokeCourseAccess` 36, `resolveEffectivePermissions` 33, `http_*`/`parse_*`/`declared_routes` 15, `sweep_expired` 4, `clamp_page_size` 2 |
| Funciones `test_*` en `test/atdd/` (AST) | 122 (148 nodos por parametrización) | AST |
| Mayor archivo | 738 líneas (`module1_ingest_contracts.test.py`) | `wc -l` |

### Estado de los hallazgos previos

| Hallazgo | Estado | Evidencia |
| --- | --- | --- |
| H-N1 `_decision_of` sin definir (T-CON-01 NameError) | RESUELTO | `module1_contracts.test.py:47` importa `decision_of` de `atdd_support`; usos en `:233` y `:243`. AST: 0 nombres indefinidos en `test/atdd/` |
| M-N1 fake con código de catálogo 401 | RESUELTO | `grep -rn "AUTH_TOKEN_INVALID\|401" test/fakes/` = 0. El doble lanza `InvalidTokenError` (`test/fakes/fake_token_verifier.py:25`, tipo del puerto `app/ports/identity.py:15`). Los 401 se asertan en el producto: `test_resolve_auth_token_invalid_401_before_arn_validation`, `test_revoke_auth_token_invalid_401_before_body_validation` (`module1_revoke_contracts.test.py:240`), `test_ingest_auth_token_invalid_401_before_batch_validation` (`module1_ingest_contracts.test.py:315-316`) |
| M-N2 T-ROS-03 sin cuatro tablas ni `roster.rejected` | RESUELTO | `test_roster_no_role_smuggling` (`module1_ingest_contracts.test.py:487`, T-ROS-03) usa `assert_no_writes` (`REJECTION_TABLES`, `atdd_support.py:89`: identities, subject_memberships, subject_credentials, roster_batches) y `len(events(db, "roster.rejected")) == 1` |
| L1 archivos > 600 líneas (convención de `module1_ingest_rules_contracts.test.py:4`) | ABIERTO | `module1_ingest_contracts` 738, `module1_resolve_contracts` 702, `module1_revoke_contracts` 625. El umbral del registro (1000) sí se cumple |
| L2 contador de módulo `_seq` (`world.py`) | RESUELTO | `grep _seq\|itertools test/fakes/world.py` = 0. `_id` cuenta filas por tabla (`world.py:34-37`) |
| L3 RED concentrado en `_actor` | RESUELTO | `grep _actor app/` = 0. Cada stub de dominio lanza su propio `NotImplementedError` (33 / 36 / 37 por operación, ver conteos) |
| L4 `if` dentro del test de construcción del body | RESUELTO | `grep "if body_subject is not None" test/atdd` = 0 |
| Riesgo 2 (422 sin cuatro tablas) | RESUELTO | `assert_no_writes` en intra-batch, T-ROS-03 y T-ROS-03b |
| Cobertura P0 (R-003 con T-CON-01, R-006, R-008 salvo T-RES-05) | RESUELTO | T-CON-01 ejecuta sin NameError (ver H-N1). T-RES-05 ya tiene node (T-RES-05, `module1_resolve_contracts.test.py:628`) |

### Tests nuevos (nodos añadidos desde Re-revisión 2)

Son 20 nodos; el mapeo a requisito/AD/historia está en `traceability-matrix.md` §11. Revisados:
- **Tautologías:** 0. AST sobre `test/atdd/`: 0 `x == x`, 0 `assert` constante, 0 tests sin `assert` ni `pytest.raises`.
- **Aserciones reales:** T-RES-05 cuenta las lecturas de `Clock.now()` (exactamente 1) y compara el `timestamp` de `authorization.decided` con esa lectura. T-RES-09 asserta `effective_role == "ta"` en un ALLOW. T-RES-H24 asserta `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` y cero mutación, con control de un único header. T-ROS-H16 y T-REV-F01 asertan estado y eventos.
- **RED por `NotImplementedError`:** 127/127 atdd-red (ver conteos). Los 11 atdd nuevos caen en stubs de dominio u HTTP, no en `NameError`/import.
- **Guardas nuevas (9):** VERDE con aserción sobre DDL o sobre `app/domain/` por AST (H-25 usa módulos sintéticos para comprobar que el lint detecta cada fuente).

### Puntaje

Por dimensión (solo deducciones de la dimensión):

| Dimensión | Hallazgos abiertos | Puntaje | Grado |
| --- | --- | --- | --- |
| Determinismo | ninguno (L4 resuelto) | 100 | A |
| Aislamiento | ninguno (L2 resuelto) | 100 | A |
| Mantenibilidad | L1 | 99 | A |
| Rendimiento | ninguno (RED 0,6 s; GREEN no medido) | 100 | A |

Global: deducciones 1 (LOW 1×1, L1). Bonus 5 (`excellentBdd`, sin cambio de criterio en esta revisión). Raw = 100 − 1 + 5 = 104. **Puntaje efectivo: min(100, 104) = 100/100 (A).** Sin tope por High (no hay High).

Nota: L2 retirado podría justificar también el criterio `perfectIsolation` del bonus. No se re-puntúa el bonus aquí, para no cambiar dos criterios a la vez.

### Hallazgos nuevos

Ninguno. Verificaciones adicionales: sin nombres indefinidos, sin tautologías, sin `_seq`, sin `_actor`, sin literales 401 en fakes.

### Recomendación

**Approve with Comments.** Critical 0, High 0, Medium 0, Low 1 (L1, convención de tamaño de archivo; la cabecera de `module1_ingest_rules_contracts.test.py:4` dice "< 600" y tres archivos la incumplen). No bloquea. Antes de GREEN, cerrar L1 (ajustar la convención a 1000 o dividir los archivos).

**Re-revisión necesaria:** no, salvo que se decida dividir archivos (L1).
