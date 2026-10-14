# Revisión de verificación web — Stack del Architecture Spine (2026-10-13, #3)

- **Alcance:** solo lectura del proyecto; este archivo es el único escrito por el revisor. No se edita ningún otro archivo ni se cambia el criterio de PASS.
- **Fuente verificada:** `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md` §§Stack (líneas 99-108).
- **Método:** búsqueda web con año 2026 (PyPI, notas de release oficiales, sqlalchemy.org, python.org/blog.python.org, devguide.python.org, sqlite.org). Fecha de corte: 2026-10-13.
- **Criterio (sin cambios):** para cada tecnología se verifica (a) existencia, (b) que cada versión fijada sea real/vigente o válida, (c) que los pins respeten la política declarada (SQLAlchemy anclado a línea 2.0). Se marca lo desactualizado o no confirmado.

## Resultado por tecnología

### 1. Python 3.11+ (mínimo heredado; runtimes posteriores aceptados) — CONFIRMADO
- Existe y sigue soportado: Python 3.11 está en modo solo-fixes de seguridad hasta octubre de 2027 (PEP 664; tabla de estados en devguide.python.org: rama 3.11 `security`, EOL 2027-10).
- Último parche de la serie: **3.11.17** publicado el 2026-10-01 (blog.python.org "Python 3.10.22, 3.11.17, 3.12.15, 3.13.16 and 3.14.8 are now available!").
- Series posteriores vigentes: 3.12 (seguridad hasta 2028-10), 3.13 (seguridad hasta 2029-10), 3.14 (bugfix), 3.15 (bugfix hasta 2031-10). La cláusula "runtimes posteriores aceptados" del spine es coherente con esto.
- Observación (no bloqueante): 3.11 está en modo solo-seguridad (releases solo-fuente, sin binarios nuevos). Como el spine lo declara como *mínimo* y acepta runtimes posteriores, el pin es válido.

### 2. FastAPI 0.143.0 — CONFIRMADO (vigente / última)
- La versión **0.143.0 existe** y es la **última publicada**: release 2026-10-08 confirmada en github.com/fastapi/fastapi/releases, notas oficiales (fastapi.tiangolo.com/release-notes: "0.143.0 (2026-10-08)"), PyPI (`fastapi/0.143.0`) y conda-forge (0.143.0 del 2026-10-08).
- Cambio destacado 0.143.0: auto-configuración del exportador OpenTelemetry pasa a opt-in (`FASTAPI_OTEL_AUTO_CONFIGURE=true`); sin impacto para el Módulo 1 (sin telemetría viva; adapters simulados).
- Compatibilidad: PyPI exige `Python >=3.10` → compatible con el mínimo 3.11+ del spine.
- Nada posterior en la línea a fecha de corte.

### 3. Pydantic 2.14.1 (v2) — CONFIRMADO (vigente / última)
- La versión **2.14.1 existe** y es la **última publicada**: release 2026-10-11 confirmada en pypi.org/project/pydantic/2.14.1 ("v2.14.1 (2026-10-11)") y changelog oficial. Predecesora 2.14.0 del 2026-10-08 (anuncio oficial pydantic.dev).
- Política v2 respetada: el pin es línea v2 (no v1).
- Compatibilidad: v2.14 retira Python 3.9 y añade 3.15; la serie 3.11 sigue soportada → compatible con el mínimo del spine.

### 4. SQLAlchemy 2.0.54 (línea 2.0; no migrar a 2.1) — CONFIRMADO (vigente en su línea; política respetada)
- La versión **2.0.54 existe** y es la **última de la línea 2.0**: release 2026-09-15 confirmada en sqlalchemy.org/download.html ("Latest 2.0 Release: 2.0.54") y en github.com/sqlalchemy/sqlalchemy/releases (`rel_2_0_54`, 15 Sep 2026).
- Política respetada: el pin declara línea 2.0 y prohibición de migrar a 2.1; el fijado 2.0.54 cumple exactamente eso.
- Observación (no bloqueante, registrada): la serie 2.0 está en **Maintenance Mode**; la serie corriente es **2.1** (2.1.4 del 2026-10-07) y sqlalchemy.org recomienda migrar a 2.1 a aplicaciones en desarrollo activo. El spine decide conscientemente quedarse en 2.0 (stack heredado de Plan-2 confirmado por el estudiante el 2026-10-12), por lo que no es incumplimiento; se deja constancia del costo de quedarse en mantenimiento.

### 5. SQLite WAL (versión del runtime de despliegue; writer único, `busy_timeout 5000`) — CONFIRMADO
- **WAL existe y es de escritor único:** documentación oficial (sqlite.org/wal.html): "there can only be one writer at a time" (un solo archivo WAL). Coherente con `writer único` del spine.
- **`busy_timeout` existe y 5000 es válido:** pragma oficial `PRAGMA busy_timeout = milliseconds` (sqlite.org/pragma.html); máximo 2147483647 ms; 5000 ms (5 s) está dentro del rango.
- Sin pin de versión (versión del runtime): válido; SQLite es parte del runtime y no requiere pin independiente.

### 6. pytest + pytest-asyncio + hypothesis (harness ATDD, scaffold RED por `NotImplementedError`) — CONFIRMADO
- Las tres herramientas existen y están vigentes (sin pins en el spine, lo cual es válido para un harness):
  - **pytest 9.1.1** (2026-06-19; última estable según changelog oficial; PyPI exige `Python >=3.10` → compatible con 3.11+).
  - **pytest-asyncio 1.4.0** (2026-05-26; exige pytest mínimo 8.4.0 → compatible).
  - **hypothesis 6.168.x** (serie 6.168 con releases hasta 2026-10-05, p. ej. 6.168.5; PyPI exige `Python >=3.10` → compatible; la serie actual retira 3.10 EOL pero mantiene 3.11+).
- Nada que objetar: el spine no fija versiones del harness, solo el rol (scaffold RED por `NotImplementedError`), consistente con el stop-point de solutioning.

## Tabla resumen

| Tecnología | Declarado | Estado | Evidencia |
| --- | --- | --- | --- |
| Python | 3.11+ | CONFIRMADO | 3.11.17 (2026-10-01); seguridad hasta 2027-10 (PEP 664) |
| FastAPI | 0.143.0 | CONFIRMADO (última) | Release 2026-10-08; PyPI + notas oficiales; requiere ≥3.10 |
| Pydantic | 2.14.1 (v2) | CONFIRMADO (última) | Release 2026-10-11; PyPI + changelog; política v2 OK |
| SQLAlchemy | 2.0.54 (línea 2.0) | CONFIRMADO (última de 2.0; política OK) | Release 2026-09-15; Maintenance; corriente 2.1.4 (no adoptada por decisión) |
| SQLite WAL | runtime + writer único + busy_timeout 5000 | CONFIRMADO | sqlite.org: un escritor; pragma válido; 5000 en rango |
| pytest / pytest-asyncio / hypothesis | harness sin pin | CONFIRMADO | 9.1.1 / 1.4.0 / 6.168.x; todos exigen ≥3.10 |

## Veredicto

**PASS** — Las seis entradas del §§Stack existen, todas las versiones fijadas son reales y vigentes (FastAPI 0.143.0, Pydantic 2.14.1 y SQLAlchemy 2.0.54 son las últimas de sus respectivas líneas a 2026-10-13), y los pins respetan la política (SQLAlchemy anclado a 2.0; Pydantic en v2). Nada desactualizado ni sin confirmar. Observaciones no bloqueantes: Python 3.11 en solo-seguridad (cubierto por "runtimes posteriores aceptados") y SQLAlchemy 2.0 en mantenimiento frente a serie corriente 2.1 (decisión heredada consciente, registrada).

- No se modificó ningún archivo del proyecto salvo este reporte.
