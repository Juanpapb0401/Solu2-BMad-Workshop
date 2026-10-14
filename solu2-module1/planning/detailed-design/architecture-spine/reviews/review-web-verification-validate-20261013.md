# Review web-verification (Validate) — Reviewer Gate bmad-architecture — 2026-10-13

- Intent: **Validate**. Solo lectura. No se edita ningún archivo del proyecto salvo este reporte nuevo.
- Alcance: `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` §§Stack (L99–108) + presupuestos NFR de `solu2-module1/planning/detailed-design/contracts.md` (§§1–3).
- Método: búsqueda web 2026 + **PyPI JSON en vivo como árbitro** (`https://pypi.org/pypi/<pkg>[/<ver>]/json`, consultado 2026-10-13) + releases/docs oficiales. Los resúmenes cacheados de búsqueda van rezagados y **no** se usan como evidencia primaria cuando contradicen a PyPI en vivo.
- Antecedentes leídos (no modificados): `reviews/review-web-verification.md` (2026-10-12, PyPI en vivo) y `reviews/review-web-verification-20261013.md` (lente web, PASS). Esta pasada re-verifica en vivo de forma independiente.

## Veredicto

**PASS — stack reality-checked, sin bloqueantes.**

Los cuatro pins con versión existen en PyPI en vivo, no están yankeados, están vigentes al 2026-10-13 (tres de ellos son el `latest` de su línea/paquete) y el pin de SQLAlchemy respeta la política "línea 2.0; no migrar a 2.1". Lo no pineado (harness, SQLite runtime, menor concreto de Python) se marca explícitamente como NO CONFIRMADO en versión, sin bloquear el gate. Nada desactualizado en el spine; lo único desactualizado observado son los índices cacheados de búsqueda (detalle abajo), no el spine.

## Tabla decisión × evidencia (PyPI en vivo 2026-10-13)

| Decisión spine | Estado | Evidencia |
| --- | --- | --- |
| Python 3.11+ (mínimo heredado; posteriores aceptados) | CONFIRMADO / VÁLIDO | Rama 3.11 con soporte security hasta 2027-10-31 (PEP 664 / devguide); serie legacy en solo-security (3.11.16/3.11.17, solo-fuente, sin binarios nuevos); 3.10 ya EOL. El mínimo "3.11+" sigue válido y es compatible con los tres pins (`fastapi>=3.10`, `pydantic>=3.10`, `SQLAlchemy 2.0.54>=3.7`, `2.1.x>=3.11`). "Posteriores aceptados" sin contradicción. |
| FastAPI 0.143.0 | CONFIRMADO — existe y VIGENTE (`latest`) | PyPI en vivo: `version=0.143.0`, `upload=2026-10-08T12:29:44Z`, `yanked=false`, `requires_python>=3.10`, dependencia `pydantic>=2.9.0` (compatible con 2.14.1). `fastapi/latest` en vivo = `0.143.0`. GitHub `fastapi/fastapi/releases/tag/0.143.0` (2026-10-08; cambio: auto-config OpenTelemetry pasa a opt-in — irrelevante para Módulo 1). Sin versión posterior observada al 2026-10-13. |
| Pydantic 2.14.1 (v2) | CONFIRMADO — existe y VIGENTE (`latest`) | PyPI en vivo: `version=2.14.1`, `upload=2026-10-11T18:37:53Z` (wheel) / `18:37:55Z` (sdist), `yanked=false`, `requires_python>=3.10`. `pydantic/latest` en vivo = `2.14.1`. Línea v2 = release de producción actual. **Discrepancia resuelta:** los índices cacheados de búsqueda mostraban `2.13.5` (2026-08-28) como "latest" con `2.14.0b2` pre-release — están rezagados y quedan desmentidos por PyPI en vivo. El pin 2.14.1 SÍ existe; no hay hallazgo contra el spine. |
| SQLAlchemy 2.0.54 (línea 2.0; no migrar a 2.1) | CONFIRMADO — existe; pin intencional; política respetada | PyPI en vivo: `2.0.54` existe, `upload=2026-09-15T22:11:14Z`, `yanked=false`, `requires_python>=3.7`. `2.0.55` → 404 (2.0.54 es tip de la línea 2.0). `SQLAlchemy/latest` en vivo = `2.1.4` (`upload=2026-10-07T18:17:21Z`, `>=3.11`): la línea 2.1 existe y es posterior, por lo que "no migrar a 2.1" es decisión deliberada coherente con el stack heredado confirmado (2026-10-12), no desconocimiento. Docs `docs.sqlalchemy.org/en/20` confirman 2.0.54 como current de la línea 2.0. |
| SQLite WAL (versión del runtime, writer único, `busy_timeout 5000`) | CONFIRMADO como diseño (sin pin, correcto) | `sqlite.org/wal.html`: un solo writer ("there can only be one writer at a time"); lectores no bloquean al escritor y viceversa. `busy_timeout` es pragma por conexión, no versión a verificar; `5000` ms es best-practice documentada contra `database is locked`. "Versión del runtime" es intencionalmente sin pin — correcto, no requiere web-check. No demuestra NFR por sí solo (checkpoints, WAL creciente, lectores largos). |
| pytest + pytest-asyncio + hypothesis (harness ATDD, RED por `NotImplementedError`) | EXISTEN; NO CONFIRMADO en versión (no bloqueante) | La spine no pina versiones (L108), así que no hay pin que validar. Existencia y vigencia en vivo al 2026-10-13: `pytest latest=9.1.1` (`>=3.10`), `pytest-asyncio latest=1.4.0` (2026-05-26, `>=3.10`), `hypothesis latest=6.169.0` (`>=3.11`). Sin pins no hay reality-check de defaults (`asyncio_mode`, scopes): fijar al crear el scaffold para evitar deriva. No bloquea el gate (suite RED futura). |
| Presupuestos NFR (contracts.md: p95 < 20 ms @100 req/s; revocación < 200 ms / < 60 s; ingesta 1000 filas < 3.0 s) | NO EVIDENCIADOS (correcto; estado PLANNED) | La spine/contracts no certifican capacidad; `Deferred` exige medición real. Nada que marcar como `EVIDENCED`. Sin cambio. |

## No confirmado / desactualizado

1. **Índices cacheados de búsqueda (no bloqueante, no es el spine):** durante esta pasada mostraban como "latest" `FastAPI 0.141.1` (2026-07-29) y `Pydantic 2.13.5` (2026-08-28) / `2.14.0b2` pre-release. Desmentidos por PyPI JSON en vivo (0.143.0 del 2026-10-08; 2.14.1 del 2026-10-11). Se registra como limitación de la lente de búsqueda, no como hallazgo contra el spine. Mismo antecedente ya documentado en las dos revisiones previas.
2. **Harness sin pins** (`pytest`, `pytest-asyncio`, `hypothesis` sin versiones) — fijar en el scaffold. Riesgo: deriva de defaults entre entornos.
3. **Menor concreto de Python 3.11 en despliegue** — el mínimo heredado es válido hasta oct-2027, pero la revisión menor debe elegirse al fijar runtime. No retroceder a 3.10 (EOL).
4. **SQLite "versión del runtime"** — intencional, sin web-check requerido; el riesgo real (contención de writer único, checkpoints) lo cubre el benchmark pendiente, no esta lente.

## Compatibilidad cruzada de los pins (en vivo)

- `fastapi 0.143.0` exige `>=3.10` y `pydantic>=2.9.0` → `pydantic 2.14.1` satisface el rango; `python 3.11+` satisface `>=3.10`.
- `SQLAlchemy 2.0.54` exige `>=3.7` → `python 3.11+` lo satisface; no impone FastAPI/Pydantic.
- `pydantic 2.14.1` exige `>=3.10` → `python 3.11+` lo satisface.
- Sin contradicción entre pins ni con la política de línea 2.0.

## Fuentes consultadas (2026-10-13)

- PyPI JSON en vivo: `https://pypi.org/pypi/fastapi/0.143.0/json`, `https://pypi.org/pypi/fastapi/json`, `https://pypi.org/pypi/pydantic/2.14.1/json`, `https://pypi.org/pypi/pydantic/json`, `https://pypi.org/pypi/SQLAlchemy/2.0.54/json`, `https://pypi.org/pypi/SQLAlchemy/json` (+ `2.0.55` → 404, `2.1.4`), `pytest`, `pytest-asyncio`, `hypothesis` (latest).
- `https://github.com/fastapi/fastapi/releases/tag/0.143.0` (2026-10-08).
- `https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html` (2.0.54, 2026-09-15) y `https://github.com/sqlalchemy/sqlalchemy/releases` (2.1.x posterior).
- `https://www.sqlite.org/wal.html`, `https://www.sqlite.org/pragma.html#pragma_busy_timeout` (vía documentación citada).
- `https://devguide.python.org/versions/` (3.11 security hasta oct-2027; 3.10 EOL).
- Búsqueda web 2026 (índices cacheados, usada solo como señal secundaria por su rezago documentado).
- Local (solo lectura): `ARCHITECTURE-SPINE.md` §§Stack, `contracts.md` §§1–3, `reviews/review-web-verification.md`, `reviews/review-web-verification-20261013.md`.

*Nota de integridad: ningún archivo del proyecto fue modificado; el único archivo escrito es este reporte nuevo.*
