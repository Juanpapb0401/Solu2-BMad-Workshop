"""Constantes y helpers compartidos por la suite ATDD del Módulo 1 (sin lógica de negocio).

Importable desde los módulos *_contracts.test.py porque test/atdd/conftest.py añade este
directorio a sys.path. Nombre sin patrón `test_*`/`*_contracts.test.py`: pytest no lo colecciona.
"""
from __future__ import annotations

import pathlib
import re
import sqlite3
import threading
from typing import Any, Callable

import pytest

from app.domain.errors import Module1Error

ACTION = "inference"  # enum cerrado action ∈ {inference, training} (Ronda 6 Q5 / ADVF-07)
ARN_8B_CS101 = "urn:uai:subject:CS101:model:llama-3-8b-instruct"  # catálogo: gpu_24gb_workstation; CS101 student -> DENY
ARN_TOY_CS101 = "urn:uai:subject:CS101:model:toy-cpu-demo"  # catálogo: cpu_toy; CS101 student inference -> ALLOW
ARN_8B_CS480 = "urn:uai:subject:CS-480:model:llama-3-8b-instruct"  # catálogo: gpu_24gb_workstation; CS-480 student/ta -> ALLOW
AD_RE = re.compile(r"AD-\d{2}")
OPENAPI_PATH = pathlib.Path(__file__).resolve().parents[2] / "planning" / "detailed-design" / "schemas" / "openapi.yaml"
# Semilla génesis del ledger (R10-M2, ADOPTED 2026-10-14): planning/ARCHITECTURE.md l.97.
# Corrige la propuesta previa de 64 ceros (H-15). Mismo valor que 001_module1_schema.sql.
GENESIS = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# prev_record_hash arbitrario de filas de prueba del guard DDL. NO es la génesis (usar GENESIS).
ARBITRARY_PREV_HASH = "0" * 64

# Literales de microsegundos con nombre (L6). Unidad: microsegundos UTC (at_offset).
ONE_MICROSECOND = 1
FIVE_MINUTES_US = 300_000_000
FIVE_MINUTES_ONE_SECOND_US = 301_000_000
TEN_MINUTES_US = 600_000_000
ONE_HOUR_US = 3_600_000_000
SEVENTY_MINUTES_US = 4_200_000_000

# Secretos (AD-06 / NFR-SEC-04): la clave completa nunca debe aparecer en claro fuera de la
# respuesta de creación; el enmascarado es uai_live_<4>••••••••••••<4> (ARCHITECTURE.md AD-06).
SECRET_FULL = "uai_live_" + "0123456789abcdef" * 2  # uai_live_ + 32 hex (de prueba)
SECRET_RAW_RE = re.compile(r"uai_live_[A-Za-z0-9]{8,}")
SECRET_MASKED = "uai_live_0123" + "•" * 12 + "cdef"
SECRET_MASKED_RE = re.compile(r"uai_live_[0-9a-f]{4}•{12}[0-9a-f]{4}")

RED = pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="ATDD RED: stub sin lógica productiva (NotImplementedError)",
)


def red(priority: str, *extra_marks):
    """Marca un test atdd-red: marker atdd + prioridad + xfail estricto (+ marcas extra)."""

    def deco(fn):
        fn = pytest.mark.atdd(fn)
        fn = getattr(pytest.mark, priority)(fn)
        fn = RED(fn)
        for mark in extra_marks:
            fn = mark(fn)
        return fn

    return deco


def assert_cites_ad(explanation: dict) -> None:
    rule_ids = explanation["rule_ids"]
    assert any(AD_RE.fullmatch(r) for r in rule_ids), f"sin AD-n citado: {rule_ids}"


def assert_code_first(explanation: dict, code: str) -> None:
    assert explanation["rule_ids"][0] == code, explanation["rule_ids"]


def roster_row(n: int, role: str = "student") -> dict:
    return {
        "institutional_id": f"STU-{n:05d}",
        "email": f"stu{n:05d}@universidad.edu",
        "full_name": f"Estudiante {n:05d}",
        "assigned_role": role,
    }


def roster_batch(rows: list[dict], subject: str = "CS-480", term: str = "2026-FALL") -> dict:
    return {"subject_id": subject, "term": term, "rows": rows}


# Tablas que un rechazo 422/400/403 no debe modificar (contracts §3 Q-fail; Riesgo 2 de test-review).
REJECTION_TABLES = ("identities", "subject_memberships", "subject_credentials", "roster_batches")


def assert_no_writes(before: dict, after: dict) -> None:
    """Conteo antes vs después: ninguna de las tablas de rechazo cambió."""
    for table in REJECTION_TABLES:
        assert after[table] == before[table], f"escritura parcial en {table}: {before[table]} -> {after[table]}"


def db_path(conn: sqlite3.Connection) -> str:
    """Ruta del archivo SQLite (la conexión de prueba vive en un archivo temporal WAL)."""
    return conn.execute("PRAGMA database_list").fetchone()[2]


def run_concurrently(workers: list[Callable[[threading.Barrier], object]]) -> list:
    """Ejecuta cada worker en su propio hilo, alineados con una barrera de inicio.

    Cada worker crea su propia conexión SQLite dentro del hilo (una conexión por hilo).
    Un error de hilo se re-lanza en el hilo principal; un hilo colgado falla el test.
    """
    barrier = threading.Barrier(len(workers))
    outcomes: list = [None] * len(workers)

    def runner(index: int) -> None:
        try:
            outcomes[index] = workers[index](barrier)
        except BaseException as exc:  # noqa: BLE001 - se re-lanza en el hilo principal
            outcomes[index] = exc

    threads = [threading.Thread(target=runner, args=(i,)) for i in range(len(workers))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert not any(thread.is_alive() for thread in threads), "hilo de prueba colgado"
    for outcome in outcomes:
        if isinstance(outcome, BaseException):
            raise outcome
    return outcomes


def decision_of(call: Callable[[], Any]) -> tuple:
    """Normaliza un resolve: ('ALLOW', None), ('DENY', código principal) o ('ERROR', código) si lanza."""
    try:
        result = call()
    except Module1Error as err:
        return ("ERROR", err.code)
    if result["decision"] == "ALLOW":
        return ("ALLOW", None)
    return ("DENY", result["explanation"]["rule_ids"][0])


def multipart_body(parts: list[tuple[str, bytes]], boundary: str = "B") -> bytes:
    """Cuerpo multipart/form-data: una parte `file` (roster.csv) por cada elemento de `parts`."""
    out = b""
    for name, data in parts:
        out += (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="roster.csv"\r\n'
            "Content-Type: text/csv\r\n\r\n"
        ).encode("utf-8") + data + b"\r\n"
    return out + f"--{boundary}--\r\n".encode("utf-8")
