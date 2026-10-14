# Web-verification — Paquete estudiante F/H (2026-10-13, corrida 6)

- Fecha: 2026-10-13
- Rol: lente de web-verification del Reviewer Gate (solo lectura; no se editó ningún fuente salvo este reporte).
- Alcance: verificar que el paquete no cambia el stack ni introduce tecnología sin verificar, que AD-01..AD-07 y Plan-2 quedan intactos, y que `roles_matrix.v0.json` es dato (no código/dependencia).
- Veredicto: **PASS**.

## Stack observado (idéntico al heredado, sin cambios)

Python 3.11+, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL writer único (`busy_timeout 5000`).

- `ports-and-adapters.md:13-14` declara exactamente ese stack y remite a `.work/stack-verification.md` (sin modificar en esta corrida).
- `.venv` instalado en corrida anterior: `fastapi==0.143.0`, `pydantic==2.14.1`, `sqlalchemy==2.0.54`, `pytest==8.3.4` (ver validación de entorno del gate 6).
- `dto.py` reitera `Pydantic v2 (2.14.1)` como lenguaje de schemas, sin pin nuevo.
- `openapi.yaml: openapi 3.1.0, version 1.0.0-phase2` — `3.1.0` es versión de la spec OpenAPI, no tecnología nueva.
- `roles_matrix.v0.json`: JSON de datos versionado (3 filas + citas), sin imports ni runtime; no es tecnología nueva.
- Afirmaciones de versión nueva sin evidencia en los artefactos: ninguna detectada; no se requirió búsqueda web nueva (sin inventar).

## Autoridad preservada

- `AD-01..AD-07` declarados autoridad read-only en spine, contracts, ports, dto y openapi; preservados tal cual. `planning/ARCHITECTURE.md` y `planning/prd.md` sin tocar en esta corrida (solo lectura).
- Los artefactos editados son companions + spine local (AD-08..AD-13); ninguna regla heredada se renumera ni debilita (F-01 refina orden sin tocar garantías AD-03; H-19b aplica jerarquía heredado > local; H-18/`term` no toca AD-01).
- Gates 4/5 y lenses previos sin tocar (verificados por listado; solo se agregan archivos `-20261013-6`).

## Evidencia y límites

- Evidencia: artefactos editados, `.work/paquete-decisiones-F-H.md` (aprobación estudiante), `.work/stack-verification.md` (2026-10-12), entorno `.venv` (pins instalados).
- No se ejecutó TEA ni `bmad-build`. NFR sigue PLANNED sin corrida medible (sin EVIDENCED).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado.*
