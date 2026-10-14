# Web-verification — Ronda 3 Gate 7, G7-01/G7-02/R3-01..R3-06 (2026-10-13, corrida 8)

- Fecha: 2026-10-13
- Rol: lente de web-verification del Reviewer Gate de la skill bmad-architecture (solo lectura salvo este reporte; ningún otro archivo fue editado en esta corrida).
- Alcance: verificar que la Ronda 3 (`.work/paquete-decisiones-F-H.md` § "Ronda 3": G7-01, G7-02, R3-01..R3-06, APROBADO por el estudiante 2026-10-13) no cambia el stack ni introduce tecnología sin verificar, que AD-01..AD-07 y Plan-2 (`planning/ARCHITECTURE.md`, `planning/prd.md`) quedan intactos (solo lectura; se confirma que no fueron modificados en esta corrida), que `schemas/roles_matrix.v0.json` sigue siendo dato, y que los triggers nuevos del DDL usan solo SQLite estándar (`BEFORE UPDATE/DELETE` + `RAISE(ABORT)`) sin dependencias nuevas.
- Veredicto: **PASS**.

## Stack observado (idéntico al heredado, sin cambios)

Stack heredado esperado: Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL writer único (`busy_timeout 5000`).

- `.venv` accesible (`solu2-module1/.venv/bin/python` → Python 3.11.14, satisface 3.11+). Versiones importadas en esta corrida: `fastapi 0.143.0`, `pydantic 2.14.1`, `sqlalchemy 2.0.54` — pins exactos, sin desvío.
- `dto.py` importa OK en esta corrida (`sys.path` a `schemas`, `dto-ok`): sus únicos imports son `typing.Literal` + `pydantic (BaseModel, Field)` (+ `__future__.annotations`). Sin `fastapi`/`sqlalchemy`/`random`/`secrets`/`uuid`/`os`/`time`/`datetime` — coherente con AD-08 + H-25. Su cabecera reitera `Pydantic v2 (2.14.1)` como lenguaje de schemas, sin pin nuevo.
- DDL declara `PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;` (líneas 17-19). Validado en `sqlite3 :memory:` en esta corrida: `PRAGMA busy_timeout` → 5000; 11 tablas (`audit_events`, `audit_ledger`, `audit_ledger_metadata`, `escalation_tickets`, `identities`, `roles`, `roster_batches`, `subject_credentials`, `subject_memberships`, `subjects` + `sqlite_sequence`), 4 triggers (ver abajo). (`journal_mode` reporta `memory` solo por ser `:memory:`; el texto DDL fija WAL.)
- Ronda 3 no introduce tecnología: G7-01 es REJECT explícito (001 es migración inicial, sin migración nueva); G7-02 es DEFER a NFR (log WARN estructurado sin secretos + nombre de métrica `scheduler_sweep_deferred_total`, sin librería nueva); R3-01 (`AUTH_TOKEN_INVALID` → 401, citado a PRD:255) y R3-02 (`MALFORMED_DROP_TIMESTAMP` → 400) son códigos de catálogo, no dependencias (excepción explícita a "sin códigos nuevos", aprobada por el estudiante); R3-03 reutiliza códigos existentes del catálogo; R3-04 (STRICT = rollback total) invoca AD-02 heredado; R3-05 (`application/problem+json`, se ignora `Accept`) es una representación ya existente; R3-06 (orden revoke + triggers append-only) usa `BEGIN IMMEDIATE` / `UPDATE … RETURNING` / `QueueReservation`, mecanismos ya adoptados. Afirmaciones de versión nueva sin evidencia: ninguna.
- Búsqueda web nueva: no requerida (nada que verificar). No se detectó versión ni tecnología nueva, por lo que no se ejecutó ninguna verificación web adicional.

## Autoridad preservada

- `AD-01..AD-07` viven en `planning/ARCHITECTURE.md` y se declaran autoridad read-only en el DDL, `dto.py`, contracts y spine. `planning/ARCHITECTURE.md` (mtime 2026-09-24) y `planning/prd.md` (mtime 2026-09-23) **sin tocar en esta corrida** (solo lectura; `stat` confirma fechas de septiembre frente a la corrida de octubre). No se debilitó ningún AD.
- `schemas/roles_matrix.v0.json` sigue siendo **dato**: JSON puro versionado (`version v0`, 3 filas + citas a `planning/prd.md:244` y `:154` + nota F-02/H-26/R2-01), sin imports ni runtime. El contenido es el mismo de la Ronda 2 (roles ya normalizados a `roles.id` exactos).
- Triggers nuevos del DDL (R3-06): exactamente 4, todos SQLite estándar, sin extensiones ni dependencias nuevas:
  - `trg_audit_ledger_no_update` — `BEFORE UPDATE ON audit_ledger` → `RAISE(ABORT, 'append-only')`
  - `trg_audit_ledger_no_delete` — `BEFORE DELETE ON audit_ledger` → `RAISE(ABORT, 'append-only')`
  - `trg_audit_events_no_update` — `BEFORE UPDATE ON audit_events` → `RAISE(ABORT, 'append-only')`
  - `trg_audit_events_no_delete` — `BEFORE DELETE ON audit_events` → `RAISE(ABORT, 'append-only')`
  - Barrido de extensiones no-estándar (`fts/rtree/json1/pg_/redis/kafka/celery`): 0 hallazgos (el único `uuid` en el archivo es un comentario sobre el formato canónico de `userId`, no una extensión).
- Gates y lenses previos sin tocar (solo se agrega este archivo `-20261013-8`).

## Evidencia y límites

- Evidencia: `.work/paquete-decisiones-F-H.md` §Ronda 3 (APROBADO por el estudiante 2026-10-13); `stat` de autoridad vs. artefactos (autoridad: septiembre; `001_module1.sql`/`dto.py`/`roles_matrix.v0.json`: 2026-10-13, aplicación esperada de la Ronda 3); `.venv` (Python 3.11.14 + pins 0.143.0/2.14.1/2.0.54); import `dto-ok`; `sqlite3 :memory:` (11 tablas, 4 triggers, `busy_timeout` 5000).
- Límites: **no se ejecutó TEA ni `bmad-build`** en esta corrida (stop-point de solutioning; este lens es solo lectura). **NFR sigue PLANNED sin EVIDENCED**: no hay corrida medible real (latencias, memoria, contención WAL) y no se declara PASS de ningún readiness gate. G7-02 queda explícitamente DEFERRED a Fase 3 `/bmad-testarch-nfr` (responsable Test-lead).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado.*
