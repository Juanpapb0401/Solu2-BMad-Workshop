# CI Quality Gate — solu2-module1 (bmad-testarch-ci, Create + Fast path)

**Fecha:** 2026-10-14 · **Modo:** no interactivo (`opencode run`), Create + Fast path.
**Estado:** scaffold local creado y ejecutado. **No hubo corrida remota: prohibido declarar "CI PASS" remoto.**
**Archivos de esta corrida (únicos escritos, bajo `solu2-module1/` según AGENTS.md):**

- `solu2-module1/.github/workflows/quality-gate.yml` — plantilla GitHub Actions (SIN activar).
- `solu2-module1/scripts/quality_gate.sh` — equivalente local con `.venv` (ejecutable).
- `solu2-module1/test/ci-quality-gate.md` — este documento.

No se editó ningún otro archivo (otra corrida BMad edita `planning/detailed-design` en paralelo).
No se hizo `git init`, no hay remote, no hubo push.

## 1. Etapas del gate

| # | Etapa | Comando / qué hace | Severidad |
|---|-------|--------------------|-----------|
| 0 | Setup | Python 3.11; `pip install -r requirements-dev.txt` (+ `pyyaml` solo en remoto, para parsear `openapi.yaml`) | Bloqueante si falla |
| 1 | Lint pureza `app/domain/` (decisión H-25) | AST: falla si `app/domain/*.py` importa `fastapi`, `sqlalchemy`, `sqlite3`, `random`, `secrets`, `uuid`, `time`; o usa `os.urandom` / `datetime.now/utcnow/today` | **BLOQUEANTE** |
| 2 | Validar DDL en `sqlite3 :memory:` | `executescript(001_module1_schema.sql)` + exige las 9 tablas (`identities`, `subjects`, `roles`, `subject_memberships`, `escalation_tickets`, `subject_credentials`, `audit_ledger`, `audit_ledger_metadata`, `audit_events`) | **BLOQUEANTE** |
| 3 | Importar `schemas/dto.py` | `import dto` (Pydantic v2) y verifica los 10 DTOs canónicos | **BLOQUEANTE** |
| 4 | Parsear `openapi.yaml` | `yaml.safe_load` + exige las 3 `operationId` (`resolveEffectivePermissions`, `revokeCourseAccess`, `ingestRoster`). En local sin `pyyaml`: chequeo estructural por `grep` (degradado declarado) | **BLOQUEANTE** |
| 5 | `pytest -m "not atdd"` en verde | Suite no-ATDD (hoy: `test_harness_smoke.py`, 4 tests) | **BLOQUEANTE** |
| 6 | ATDD `collect-only` | La suite ATDD debe colectarse. Código 5 ("no tests collected", `test/atdd/` vacío) NO es error | **BLOQUEANTE** (colección/import/sintaxis rotas SÍ rompen) |
| 7 | ATDD RED esperado | Rojo SOLO por `NotImplementedError` = RED esperado (pasa). Verde inesperado = aviso (recalibrar a GREEN-phase). Código 5 / `test/atdd/` vacío = PENDIENTE (no bloquea). Cualquier otro rojo (colección/import/sintaxis/otra causa) = **ROMPE el gate** | **BLOQUEANTE salvo RED-esperado/pendiente** |
| 8 | Cobertura `app/domain/ ≥90%` | `--cov=app/domain --cov-fail-under=90`; `continue-on-error` en remoto / no bloquea en local | **INFORMATIVA** hasta que exista implementación |

Adaptaciones Fast path del template genérico: backend-only (sin navegadores), sin sharding
(suite de 4 tests), sin burn-in (persigue flakiness de UI; aquí no aplica), sin artefactos
de reportes visuales. Sin secretos: no hay credenciales en el pipeline.

## 2. Criterios de bloqueo (resumen)

Rompen el gate: fallo en etapas 1–6; etapa 7 en rojo por causa distinta de
`NotImplementedError` (incluye errores de colección/import/sintaxis); fallo de setup.
NO rompen: etapa 7 en RED-por-`NotImplementedError` o PENDIENTE (sin tests ATDD);
etapa 8 (informativa); warnings (`asyncio_default_fixture_loop_scope` de pytest-asyncio).

## 3. Qué falta para correrlo en remoto

1. Crear el repositorio Git (`git init` + remote `origin`) — hoy el workspace NO es repo y
   AGENTS.md prohíbe a esta corrida hacerlo.
2. Copiar `solu2-module1/.github/workflows/quality-gate.yml` a
   `<repo-root>/.github/workflows/quality-gate.yml` (GitHub solo lee workflows en la raíz).
   La plantilla ya usa `working-directory: solu2-module1`, así que no requiere más cambios
   si el layout se conserva.
3. Push a `main` o apertura de PR (triggers: `push`/`pull_request` en `main`, `workflow_dispatch`).
4. Decidir si `pyyaml` entra a `requirements-dev.txt` (hoy ausente: el job remoto lo instala
   aparte; el script local usa fallback `grep` y lo declara).
5. Cuando exista la suite ATDD (`test/atdd/` hoy vacío), el gate pasará de PENDIENTE a
   RED-esperado automáticamente; cuando haya implementación, recalibrar la etapa 7 a
   GREEN-phase y volver la cobertura bloqueante (subir el umbral a efectivo).

## 4. Salida local real (`./scripts/quality_gate.sh`, 2026-10-14, `.venv` Python 3.11.14)

Literal, sin recortes salvo esta cabecera:

```
== quality_gate local — Python 3.11.14 — /Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1 ==
pureza domain/ (H-25)
OK: Etapa 1 — pureza domain/ (H-25)
DDL :memory_ tablas=['audit_events', 'audit_ledger', 'audit_ledger_metadata', 'escalation_tickets', 'identities', 'roles', 'roster_batches', 'sqlite_sequence', 'subject_credentials', 'subject_memberships', 'subjects']
OK: Etapa 2 — DDL válida en :memory:
dto.py importa: ['AuthorizeRequest', 'AuthorizeResponse', 'DenyBody', 'RevokeRequest', 'RevokeResponse', 'RosterIngestRequest', 'RosterIngestResponse', 'RosterRejectedManifest', 'ErrorBody', 'ExplanationDTO']
OK: Etapa 3 — schemas/dto.py importa
AVISO: sin pyyaml en .venv (no está en requirements-dev.txt); chequeo estructural por grep (degradado, no inventa parseo).
OK: Etapa 4 — openapi.yaml estructural (grep, pyyaml ausente)
/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/.venv/lib/python3.11/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
....                                                                     [100%]
4 passed in 0.06s
OK: Etapa 5 — pytest (not atdd) verde
/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/.venv/lib/python3.11/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))

4 deselected in 0.05s
OK: Etapa 6 — ATDD collect-only sin errores (código 5)
PENDIENTE: test/atdd/ vacío (código 5): aún no hay suite ATDD que poner en RED. No bloquea.
OK: Etapa 7 — ATDD RED esperado (pendiente: sin tests ATDD)
--- Etapa 8 (INFORMATIVA): cobertura app/domain/ ≥90% ---
/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/.venv/lib/python3.11/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
..../Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/.venv/lib/python3.11/site-packages/coverage/control.py:967: CoverageWarning: No data was collected. (no-data-collected); see https://coverage.readthedocs.io/en/7.16.2/messages.html#warning-no-data-collected
  self._warn("No data was collected.", slug="no-data-collected")
/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/.venv/lib/python3.11/site-packages/pytest_cov/plugin.py:355: CovFailUnderWarning: Coverage failure: total of 0 is less than fail-under=90
  warnings.warn(CovFailUnderWarning(message), stacklevel=1)

ERROR: Coverage failure: total of 0 is less than fail-under=90
                                                                         [100%]

--------- coverage: platform darwin, python 3.11.14-final-0 ----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
app/domain/__init__.py         0      0   100%
app/domain/membership.py       4      4     0%   6-16
app/domain/resolution.py       4      4     0%   6-15
app/domain/roster.py           4      4     0%   6-14
--------------------------------------------------------
TOTAL                         12     12     0%

FAIL Required test coverage of 90% not reached. Total coverage: 0.00%
4 passed in 0.07s
INFO: cobertura domain/ <90% o sin datos — esperado sin implementación; NO bloquea (informativa).
== resumen: PASS=7 FAIL=0 ==
GATE LOCAL: VERDE (etapas bloqueantes OK; ATDD en RED-esperado/pendiente; cobertura informativa).
```

**Lectura honesta:** GATE LOCAL VERDE en etapas bloqueantes. ATDD = PENDIENTE
(`test/atdd/` vacío, código 5): aún no hay suite que poner en RED. Cobertura `domain/`
0 % (los smoke tests no tocan dominio; los stubs solo alzan `NotImplementedError`):
esperado e informativo. Warnings de `pytest-asyncio` (`asyncio_default_fixture_loop_scope`)
preexistentes, no bloquean. `bash -n` del script: OK. YAML remoto: chequeo básico OK
(sin parser local; el parseo real lo hace el job con `pyyaml`).

## PREGUNTAS BLOQUEANTES

Ninguna que impida el scaffold. Pendientes NO inventados, para el estudiante:

1. ¿Se añade `pyyaml` a `requirements-dev.txt` o se mantiene la instalación aparte solo en CI?
2. ¿Se fija `asyncio_default_fixture_loop_scope` en `pytest.ini` para silenciar el warning
   de `pytest-asyncio`, o se deja como está (otra corrida es dueña del harness/config)?
3. Al crear el repo remoto: ¿ruta del workflow en raíz (`.github/workflows/`) y nombre de
   rama principal (`main` asumido en la plantilla)?
