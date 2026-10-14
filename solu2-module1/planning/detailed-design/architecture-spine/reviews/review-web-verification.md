# Review web-verification — Reviewer Gate bmad-architecture (lens web, update 2026-10-12)

- Alcance SOLO lectura: `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` (sección Stack, L99-108) contra web/proyecto. Sin cambios a la spine.
- Base: `.work/stack-verification.md` (2026-10-12) + comprobación PyPI en vivo el 2026-10-12 (`https://pypi.org/pypi/<pkg>/json` y `/<pkg>/<ver>/json`).
- Nota metodológica: los índices cacheados de búsqueda devolvían como "latest" FastAPI 0.141.1 (2026-07-29) y Pydantic 2.13.5 (2026-08-28); PyPI en vivo los desmiente. Este veredicto usa solo PyPI en vivo.

## Veredicto

**PASS (lente web) — stack reality-checked, sin bloqueantes.**

## Tabla decisión × evidencia

| Decisión spine | Estado | Evidencia en vivo 2026-10-12 |
| --- | --- | --- |
| Python 3.11+ (mínimo heredado; posteriores aceptados) | CONFIRMADO | FastAPI 0.143.0 exige `>=3.10`, Pydantic 2.14.1 exige `>=3.10`, SQLAlchemy 2.1.x exige `>=3.11`; 3.11 cabe en los tres. `.work/stack-verification.md` cita devguide (3.11 en security hasta oct-2027). Sin contradicción. |
| FastAPI 0.143.0 | CONFIRMADO (existe, vigente, encaja) | PyPI live: `0.143.0` es la versión actual, publicada 2026-10-08, no yankeada, `requires_python >=3.10`, dependencia `pydantic>=2.9.0` (compatible con 2.14.1), `starlette>=0.46.0`. Fuentes: `https://pypi.org/project/fastapi/`, `https://pypi.org/pypi/fastapi/0.143.0/json`. |
| Pydantic 2.14.1 (v2) | CONFIRMADO (existe, vigente, encaja) | PyPI live: `2.14.1` es la versión actual, publicada 2026-10-11, no yankeada, `requires_python >=3.10`, `pydantic-core==2.50.1`. Línea v2 = release de producción actual. Fuentes: `https://pypi.org/project/pydantic/`, `https://docs.pydantic.dev/latest/migration/`. |
| SQLAlchemy 2.0.54 (línea 2.0; no migrar a 2.1) | CONFIRMADO (existe; pin intencional) | PyPI live: `2.0.54` existe, publicada 2026-09-15, no yankeada. PyPI live confirma que la línea 2.1 existe y es posterior (`2.1.4` actual), por lo que "no migrar a 2.1" es una decisión de pin deliberada y coherente con la confirmación del estudiante (stack heredado Plan-2), no un desconocimiento. Dialectos SQLite/PostgreSQL documentados en docs 2.0. Fuentes: `https://pypi.org/project/SQLAlchemy/`, `https://docs.sqlalchemy.org/en/20/`. |
| SQLite WAL writer único, `busy_timeout 5000` | CONFIRMADO como diseño (sin pin, correcto) | `sqlite.org/wal.html`: un solo writer; lectores y escritor avanzan a la vez; transacciones grandes/lecturas largas afectan checkpoint y latencia. "Versión del runtime de despliegue" es intencionalmente sin pin — correcto. `busy_timeout` es pragma del driver, no versión a verificar. No demuestra NFR por sí solo (ver abajo). |
| pytest + pytest-asyncio + hypothesis (harness ATDD, RED por `NotImplementedError`) | NO CONFIRMADO en versión (no bloqueante) | La spine no pina versiones del harness (L108). Las tres tecnologías existen, pero sin pin no hay reality-check de versión vigente ni de defaults. No bloquea el gate (scaffold RED futuro), pero el scaffold debe fijarlas para evitar deriva. |
| Capacidad / NFR (p. ej. 100 req/s) | NO AFIRMADO en spine (correcto) | La spine no certifica capacidad; `Deferred` exige medición real antes de migrar a PostgreSQL. `.work/stack-verification.md` concluye igual: coherente para scaffold headless, sin certificar 100 req/s. Nada que marcar como `EVIDENCED`. |
| Starter / template greenfield | N/A (sin starter invocado) | Ningún default de starter que verificar. Tecnologías nombradas existen y encajan con hexagonal + reloj inyectado (FastAPI no impone ORM; tutorial oficial documenta SQLite; SQLAlchemy 2.0 documenta SQLite). Sin deriva a training-data. |

## No confirmado (ninguno bloqueante)

1. Harness sin pins (`pytest`, `pytest-asyncio`, `hypothesis` sin versiones) — fijar en scaffold.
2. SQLite "versión del runtime" — intencional, no requiere web-check; el benchmark pendiente cubre el riesgo real (contención de writer único).
3. Python 3.11 concreto de despliegue — el mínimo heredado es válido, pero la revisión menor concreta debe elegirse al fijar runtime (no convertir "3.11+" en obligación de una revisión sin revisar soporte).

## Fuentes consultadas

- PyPI en vivo (2026-10-12): `fastapi/json`, `fastapi/0.143.0/json`, `pydantic/json`, `pydantic/2.14.1/json`, `SQLAlchemy/json`, `SQLAlchemy/2.0.54/json`.
- `.work/stack-verification.md` (2026-10-12).
- `https://fastapi.tiangolo.com/tutorial/sql-databases/`, `https://docs.pydantic.dev/latest/migration/`, `https://docs.sqlalchemy.org/en/20/`, `https://www.sqlite.org/wal.html`, `https://devguide.python.org/versions/`.
