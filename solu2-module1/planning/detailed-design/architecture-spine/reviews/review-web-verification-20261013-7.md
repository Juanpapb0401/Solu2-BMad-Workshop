# Web-verification — Ronda 2 Gate 6, G6-01/G6-02/R2-01 (2026-10-13, corrida 7)

- Fecha: 2026-10-13
- Rol: lente de web-verification del Reviewer Gate (solo lectura; no se editó ningún fuente salvo este reporte).
- Alcance: verificar que la Ronda 2 no cambia el stack ni introduce tecnología sin verificar, que AD-01..AD-07 y Plan-2 quedan intactos, y que `roles_matrix.v0.json` sigue siendo dato (no código/dependencia).
- Veredicto: **PASS**.

## Stack observado (idéntico al heredado, sin cambios)

Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL writer único (`busy_timeout 5000`).

- `ports-and-adapters.md:13-14` declara exactamente ese stack y remite a `.work/stack-verification.md` (sin modificar en esta corrida; verificación 2026-10-12 vigente).
- `.venv`: mismos pins instalados (`fastapi==0.143.0`, `pydantic==2.14.1`, `sqlalchemy==2.0.54`, `pytest==8.3.4`); `dto.py` importa y valida en esta corrida (`dto-ok`).
- `dto.py` reitera `Pydantic v2 (2.14.1)` como lenguaje de schemas, sin pin nuevo; `openapi.yaml: openapi 3.1.0, version 1.0.0-phase2` sin cambios.
- `roles_matrix.v0.json`: JSON de datos versionado (3 filas + citas + nota R2-01), sin imports ni runtime; el cambio `Student→student` / `Instructor-Privileged→instructor_privileged` es dato, no tecnología.
- G6-01/G6-02 usan mecanismos ya adoptados (`CHECK`, `QueueReservation`, `UPDATE … RETURNING`); ninguna tecnología nueva. Afirmaciones de versión nueva sin evidencia: ninguna; no se requirió búsqueda web nueva (nada que verificar).

## Autoridad preservada

- `AD-01..AD-07` declarados autoridad read-only en spine, contracts, ports, dto y openapi; preservados tal cual. `planning/ARCHITECTURE.md` y `planning/prd.md` sin tocar en esta corrida (solo lectura).
- DDL: solo columna `revoked_at` + su `CHECK` y el valor `escalation.expired` en el `CHECK` de `event_type` (lo exigido por G6-01/G6-02); 0 triggers; validado en `sqlite3 :memory:` (11 tablas, 0 triggers).
- Gates 4/5/6 y lenses previos sin tocar (solo se agregan archivos `-20261013-7`).

## Evidencia y límites

- Evidencia: artefactos editados, `.work/paquete-decisiones-F-H.md` §Ronda 2 (aprobación estudiante 2026-10-13), `.work/stack-verification.md` (2026-10-12), `.venv` (pins instalados), `pytest 4 passed` en esta corrida.
- No se ejecutó TEA ni `bmad-build`. NFR sigue PLANNED sin corrida medible (sin EVIDENCED).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado.*
