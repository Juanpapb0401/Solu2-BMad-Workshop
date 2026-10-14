"""conftest.py — Harness determinista del Modulo 1 (framework, sin logica productiva).

Fixtures obligatorias: fake_clock, fake_id_generator, seed_fleet, sim_telemetry,
db, explain_assert, edge_case_seeds. Todo simulado: sin hardware, sin red,
sin servicios vivos, sin sleep real, sin azar.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

import pytest

# solu2-module1 en sys.path para `import app` (pytest.ini tambien fija pythonpath=.).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CLOCK_START = "2026-09-23T15:04:05.000000Z"
DDL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "planning",
    "detailed-design",
    "schemas",
    "001_module1_schema.sql",
)


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class FakeClock:
    """Implementa la interfaz del Clock port (ports-and-adapters.md, AD-08/AD-13).

    now() UTC ISO-8601 con microsegundos + zona; avance manual via advance(),
    sin sleep real. Unica fuente de tiempo en tests (nunca datetime.now()).
    """

    def __init__(self, start: str = CLOCK_START) -> None:
        self._now = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )

    def now(self) -> str:
        return _fmt(self._now)

    def advance(self, seconds: float) -> str:
        self._now += timedelta(seconds=seconds)
        return self.now()


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


class FakeIdGenerator:
    """Implementa el IdGenerator port: IDs deterministicos `prefix-<8hex>`
    con contador nuevo por test (sin azar, sin colisiones intra-test)."""

    def __init__(self) -> None:
        self._n = 0

    def new_id(self, prefix: str = "id") -> str:
        self._n += 1
        return f"{prefix}-{self._n:08x}"


@pytest.fixture
def fake_id_generator() -> FakeIdGenerator:
    return FakeIdGenerator()


@pytest.fixture
def seed_fleet() -> dict:
    """Flota simulada PRD §1.1: 31 nodos x 1 GPU 24 GB + 1 nodo x 2 GPUs 48 GB,
    todos HEALTHY. Datos simulados, sin hardware (33 GPUs, 840 GB VRAM)."""
    nodes = [
        {
            "node_id": f"ws-gpu-{i:02d}",
            "status": "HEALTHY",
            "gpus": [
                {"gpu_id": f"ws-gpu-{i:02d}:gpu0", "vram_gb": 24, "status": "HEALTHY"}
            ],
        }
        for i in range(1, 32)
    ]
    nodes.append(
        {
            "node_id": "srv-central-01",
            "status": "HEALTHY",
            "gpus": [
                {"gpu_id": "srv-central-01:gpu0", "vram_gb": 48, "status": "HEALTHY"},
                {"gpu_id": "srv-central-01:gpu1", "vram_gb": 48, "status": "HEALTHY"},
            ],
        }
    )
    return {"nodes": nodes}


class SimTelemetry:
    """Inyector guionado de heartbeats/metricas con generador de fallas.

    Determinista: timestamps fijos de guion (sin reloj real), fallas solo
    via fail_next(n) (sin azar)."""

    def __init__(self) -> None:
        self.heartbeats: list = []
        self.metrics: list = []
        self.emitted: list[dict] = []  # TelemetryPort.emit_metric (R8-06)
        self._armed_faults = 0

    def emit_metric(self, name: str, value: float, labels: dict) -> None:
        self.emitted.append({"name": name, "value": value, "labels": dict(labels)})

    def fail_next(self, n: int = 1) -> int:
        self._armed_faults += n
        return self._armed_faults

    def _maybe_fault(self, what: str) -> None:
        if self._armed_faults > 0:
            self._armed_faults -= 1
            raise RuntimeError(f"simulated telemetry fault on {what}")

    def inject_heartbeat(
        self, node_id: str, status: str = "HEALTHY", ts: str = CLOCK_START
    ) -> dict:
        self._maybe_fault("heartbeat")
        hb = {"node_id": node_id, "status": status, "ts": ts}
        self.heartbeats.append(hb)
        return hb

    def inject_metric(
        self, gpu_id: str, metric: str, value: float, ts: str = CLOCK_START
    ) -> dict:
        self._maybe_fault("metric")
        m = {"gpu_id": gpu_id, "metric": metric, "value": value, "ts": ts}
        self.metrics.append(m)
        return m


@pytest.fixture
def sim_telemetry() -> SimTelemetry:
    return SimTelemetry()


@pytest.fixture
def db(tmp_path):
    """SQLite migrada con 001_module1_schema.sql, nueva por test.

    Archivo temporal (WAL lo exige: WAL no aplica a :memory:). PRAGMAs del DDL
    (journal_mode=WAL, foreign_keys=ON, busy_timeout=5000) via executescript.
    """
    path = tmp_path / "m1.db"
    conn = sqlite3.connect(str(path))
    try:
        with open(DDL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception:
        conn.close()
        raise
    yield conn
    conn.close()


OBSERVED_FIELDS = (
    "observed_role",
    "observed_context",
    "observed_resource_subject",
    "observed_prior_status",
    "observed_credentials_revoked",
    "observed_invalid_row",
    "threshold",
    "action_hint",
)


@pytest.fixture
def explain_assert():
    """Helper AD-11: falla si la decision no trae ExplanationDTO con
    rule_ids no vacio y al menos un valor observado (campos de dto.py)."""

    def _check(decision) -> bool:
        if isinstance(decision, dict):
            explanation = decision.get("explanation")
        else:
            explanation = getattr(decision, "explanation", None)
        assert explanation is not None, "decision sin explanation (AD-11)"
        if isinstance(explanation, dict):
            rule_ids = explanation.get("rule_ids")
            observed = {f: explanation.get(f) for f in OBSERVED_FIELDS}
        else:
            rule_ids = getattr(explanation, "rule_ids", None)
            observed = {f: getattr(explanation, f, None) for f in OBSERVED_FIELDS}
        assert isinstance(rule_ids, list) and len(rule_ids) >= 1, (
            "explanation sin >=1 rule_id (AD-11)"
        )
        assert any(v is not None for v in observed.values()), (
            "explanation sin valores observados (dto.py ExplanationDTO)"
        )
        return True

    return _check


@pytest.fixture
def edge_case_seeds(db) -> dict:
    """Seeds del Mandatory Edge Case (EDGE-01): misma identidad Student en
    CS101 y TA en CS-480. IDs de Plan-2 (TA-SOFIA-01, CS101, CS-480, term
    2026-FALL); UUIDs internos solo de test, sin inventar personas."""
    identity_id = "11111111-1111-4111-8111-111111111111"
    db.execute(
        "INSERT INTO roles (id, name, priority_level, description) VALUES "
        "('student', 'Student', 10, 'seed edge-case'),"
        "('ta', 'Teaching Assistant', 50, 'seed edge-case')"
    )
    db.execute(
        "INSERT INTO identities (id, institutional_id, email, full_name, status,"
        " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            identity_id,
            "TA-SOFIA-01",
            "sofia.valenzuela@universidad.edu",
            "Sofia",
            "ACTIVE",
            CLOCK_START,
            CLOCK_START,
        ),
    )
    for subject_id, name in (
        ("CS101", "Intro to Programming"),
        ("CS-480", "Intro to Machine Learning"),
    ):
        db.execute(
            "INSERT INTO subjects (id, name, term, department, is_active,"
            " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                subject_id,
                name,
                "2026-FALL",
                "Computer Science",
                1,
                CLOCK_START,
                CLOCK_START,
            ),
        )
    db.execute(
        "INSERT INTO subject_memberships (id, identity_id, subject_id, role_id, term,"
        " status, enrolled_at, dropped_at, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "22222222-2222-4222-8222-222222222222",
            identity_id,
            "CS101",
            "student",
            "2026-FALL",
            "ACTIVE",
            CLOCK_START,
            None,
            CLOCK_START,
            CLOCK_START,
        ),
    )
    db.execute(
        "INSERT INTO subject_memberships (id, identity_id, subject_id, role_id, term,"
        " status, enrolled_at, dropped_at, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "33333333-3333-4333-8333-333333333333",
            identity_id,
            "CS-480",
            "ta",
            "2026-FALL",
            "ACTIVE",
            CLOCK_START,
            None,
            CLOCK_START,
            CLOCK_START,
        ),
    )
    db.commit()
    return {
        "identity_id": identity_id,
        "institutional_id": "TA-SOFIA-01",
        "cs101_role": "student",
        "cs480_role": "ta",
    }
