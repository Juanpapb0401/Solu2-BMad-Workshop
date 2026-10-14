"""module1_guard_contracts.test.py — Guardas de invariantes impuestos por el DDL y por la pureza
del dominio (no son atdd-red).

AD-04 (heredado): el ledger es append-only. El DDL lo impone físicamente con triggers
BEFORE UPDATE / BEFORE DELETE -> RAISE(ABORT, 'append-only') sobre audit_ledger y audit_events
(001_module1_schema.sql §8b y §7b, R3-06). AD-05 (heredado): índice único parcial de tickets
PENDING/ACTIVE por (requester, subject). R8-07: audit_ledger.resource_type NOT NULL e índice
(resource_type, timestamp) para NFR-AUDIT-06. R9-02: CHECK approved_by <> requester_id (AD-05, enforcement
físico de la auto-aprobación). R9-04: CHECK GLOB de formato fijo en audit_ledger.timestamp. AD-08 (spine-local) /
H-25: pureza de app/domain/.

Estas pruebas pasan en verde porque el DDL o el código ya lo imponen; por eso llevan marker
`guard` y NO `atdd`.
"""
from __future__ import annotations

import ast
import pathlib
import sqlite3

import pytest

from atdd_support import ARBITRARY_PREV_HASH, ONE_HOUR_US
from fakes.world import (
    CLOCK_START,
    add_identity,
    add_membership,
    add_ticket,
    at_offset,
    ensure_base,
)

EVENT_ID = "evt-guard-000001"
RECORD_HASH = "a" * 64
# R8-07: resource_type = prefijo "model:<clase>" del ARN, derivado por el LedgerWriter (no entra al hash).
# R9-05: la clase sale del resource_catalog (roles_matrix.v0.json): llama-3-8b-instruct -> gpu_24gb_workstation.
RESOURCE_TYPE = "model:gpu_24gb_workstation"
DOMAIN_DIR = pathlib.Path(__file__).resolve().parents[2] / "app" / "domain"
SCHEMAS_DIR = pathlib.Path(__file__).resolve().parents[2] / "planning" / "detailed-design" / "schemas"
DTO_PATH = SCHEMAS_DIR / "dto.py"
OPENAPI_PATH = SCHEMAS_DIR / "openapi.yaml"
BANNED_IMPORTS = {"fastapi", "sqlalchemy", "sqlite3", "random", "secrets", "uuid", "os", "time"}
BANNED_CLOCK_ATTRS = {"now", "utcnow", "today"}


def _seed_ledger_and_event(db) -> None:
    ensure_base(db)
    db.execute(
        "INSERT INTO audit_ledger (event_id, timestamp, actor_id, actor_role, subject_id,"
        " resource_arn, resource_type, action, decision, reason_code, prev_record_hash,"
        " record_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (EVENT_ID, CLOCK_START, "ID-GUARD", "student", "CS-480",
         "urn:uai:subject:CS-480:model:llama-3-8b-instruct", RESOURCE_TYPE, "inference", "ALLOW",
         "SUCCESS", ARBITRARY_PREV_HASH, RECORD_HASH, CLOCK_START, CLOCK_START),
    )
    db.execute(
        "INSERT INTO audit_events (event_id, occurred_at, event_type, payload)"
        " VALUES (?, ?, 'authorization.decided', '{}')",
        (EVENT_ID, CLOCK_START),
    )
    db.commit()


def _pure_violations() -> list[str]:
    errors: list[str] = []
    for path in sorted(DOMAIN_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in BANNED_IMPORTS:
                        errors.append(f"{path.name}:{node.lineno} import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] in BANNED_IMPORTS:
                    errors.append(f"{path.name}:{node.lineno} from {node.module}")
            elif isinstance(node, ast.Attribute):
                if node.attr in BANNED_CLOCK_ATTRS:
                    errors.append(f"{path.name}:{node.lineno} .{node.attr}()")
                if node.attr == "urandom" and isinstance(node.value, ast.Name) and node.value.id == "os":
                    errors.append(f"{path.name}:{node.lineno} os.urandom")
    return errors


class TestDDLGuards:
    """Guardas físicas del DDL 001_module1_schema.sql (verde: el DDL ya impone la regla)."""

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_audit_ledger_update_rejected(self, db):
        """Test ID: T-LED-GUARD-01. Cláusula: AD-04 append-only. Trigger trg_audit_ledger_no_update.

        Assertions: UPDATE sobre audit_ledger falla con 'append-only' y la fila queda intacta.
        """
        _seed_ledger_and_event(db)

        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            db.execute("UPDATE audit_ledger SET decision = 'DENY' WHERE event_id = ?", (EVENT_ID,))
        db.rollback()

        assert db.execute(
            "SELECT decision FROM audit_ledger WHERE event_id = ?", (EVENT_ID,)
        ).fetchone() == ("ALLOW",)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_audit_ledger_delete_rejected(self, db):
        """Test ID: T-LED-GUARD-02. Cláusula: AD-04 append-only. Trigger trg_audit_ledger_no_delete.

        Assertions: DELETE sobre audit_ledger falla con 'append-only' y la fila sigue existiendo.
        """
        _seed_ledger_and_event(db)

        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            db.execute("DELETE FROM audit_ledger WHERE event_id = ?", (EVENT_ID,))
        db.rollback()

        assert db.execute(
            "SELECT COUNT(*) FROM audit_ledger WHERE event_id = ?", (EVENT_ID,)
        ).fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_audit_events_update_rejected(self, db):
        """Test ID: T-LED-GUARD-03. Cláusula: AD-04 append-only sobre el envelope. Trigger
        trg_audit_events_no_update.

        Assertions: UPDATE sobre audit_events falla con 'append-only' y el event_type no cambia.
        """
        _seed_ledger_and_event(db)

        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            db.execute("UPDATE audit_events SET event_type = 'roster.ingested' WHERE event_id = ?", (EVENT_ID,))
        db.rollback()

        assert db.execute(
            "SELECT event_type FROM audit_events WHERE event_id = ?", (EVENT_ID,)
        ).fetchone() == ("authorization.decided",)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_audit_events_delete_rejected(self, db):
        """Test ID: T-LED-GUARD-04. Cláusula: AD-04 append-only sobre el envelope. Trigger
        trg_audit_events_no_delete.

        Assertions: DELETE sobre audit_events falla con 'append-only' y el envelope sigue existiendo.
        """
        _seed_ledger_and_event(db)

        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            db.execute("DELETE FROM audit_events WHERE event_id = ?", (EVENT_ID,))
        db.rollback()

        assert db.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_id = ?", (EVENT_ID,)
        ).fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_single_active_membership_per_pair_across_terms(self, db):
        """Test ID: T-MEM-GUARD-01. Cláusula: Ronda 6 Q3 (ADVF-13): la membresía se clava por (identity, subject,
        term) y un índice único parcial impide dos ACTIVE por par aunque difieran de term. AD-02 (heredado),
        AD-04 (heredado) para la integridad física. Contracts §3 P1 / §5 fila 'Formato fijo y patrón'.

        Assertions: una membresía ACTIVE 2026-FALL y una DROPPED 2026-SPRING del mismo par conviven (membresía
        separada por term); una segunda ACTIVE 2026-SPRING falla con UNIQUE constraint; quedan 2 filas.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-GUARD-TERM", "STU-GUARD-TERM")
        add_membership(db, identity, "CS-480", "student", term="2026-FALL")
        add_membership(
            db, identity, "CS-480", "student", status="DROPPED",
            dropped_at=CLOCK_START, term="2026-SPRING",
        )

        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
            add_membership(db, identity, "CS-480", "student", term="2026-SPRING")
        db.rollback()

        assert db.execute(
            "SELECT COUNT(*) FROM subject_memberships WHERE identity_id = ? AND subject_id = ?",
            (identity, "CS-480"),
        ).fetchone() == (2,)
        assert db.execute(
            "SELECT COUNT(*) FROM subject_memberships WHERE identity_id = ? AND status = 'ACTIVE'",
            (identity,),
        ).fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_single_active_escalation_per_pair(self, db):
        """Test ID: T-ESC-GUARD-01. Cláusula: AD-05 (heredado) exclusión mutua de escalación: índice único
        parcial idx_single_active_escalation sobre (requester_id, subject_id) WHERE status IN
        ('PENDING_APPROVAL', 'ACTIVE').

        Assertions: un segundo ticket ACTIVE del mismo par falla con UNIQUE constraint; un ticket REJECTED
        del mismo par sí convive (el índice solo cubre PENDING/ACTIVE); quedan 1 ACTIVE y 1 REJECTED.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-GUARD-ESC", "STU-GUARD-ESC")
        expires = at_offset(ONE_HOUR_US)
        add_ticket(db, identity, "CS-480", "ta", granted_at=CLOCK_START, expires_at=expires)
        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
            add_ticket(db, identity, "CS-480", "ta", granted_at=CLOCK_START, expires_at=expires)
        db.rollback()
        db.execute(
            "INSERT INTO escalation_tickets (id, requester_id, subject_id, requested_role_id,"
            " duration_hours, justification, status, approved_by, rejection_reason, granted_at,"
            " expires_at, revoked_at, created_at, updated_at)"
            " VALUES ('ticket-guard-rej', ?, 'CS-480', 'ta', 1, 'Solicitud rechazada en prueba ATDD',"
            " 'REJECTED', NULL, 'motivo de prueba', NULL, NULL, NULL, ?, ?)",
            (identity, CLOCK_START, CLOCK_START),
        )
        db.commit()

        assert db.execute(
            "SELECT status, COUNT(*) FROM escalation_tickets WHERE requester_id = ? AND subject_id = ?"
            " GROUP BY status ORDER BY status",
            (identity, "CS-480"),
        ).fetchall() == [("ACTIVE", 1), ("REJECTED", 1)]

    @pytest.mark.guard
    @pytest.mark.p1
    def test_guard_escalation_timestamp_fixed_format_check(self, db):
        """Test ID: T-ESC-GUARD-02. Cláusula: ADVF-23 / ECF-15 [ADOPTED 2026-10-13]: granted_at con formato fijo
        YYYY-MM-DDTHH:MM:SS.ffffffZ (6 decimales, zona Z). Enforcement: CHECK GLOB en escalation_tickets.

        Assertions: un granted_at sin microsegundos (sin 6 decimales) falla con CHECK constraint; un valor con el
        formato fijo se acepta.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-GUARD-FMT", "STU-GUARD-FMT")
        insert = (
            "INSERT INTO escalation_tickets (id, requester_id, subject_id, requested_role_id,"
            " duration_hours, justification, status, approved_by, rejection_reason, granted_at,"
            " expires_at, revoked_at, created_at, updated_at)"
            " VALUES (?, ?, 'CS-480', 'ta', 1, 'Justificación de prueba ATDD de formato', 'ACTIVE',"
            " NULL, NULL, ?, ?, NULL, ?, ?)"
        )
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            db.execute(insert, ("ticket-fmt-bad", identity, "2026-09-23T15:04:05Z",
                                at_offset(ONE_HOUR_US), CLOCK_START, CLOCK_START))
        db.rollback()
        db.execute(insert, ("ticket-fmt-ok", identity, CLOCK_START, at_offset(ONE_HOUR_US),
                            CLOCK_START, CLOCK_START))
        db.commit()
        assert db.execute("SELECT COUNT(*) FROM escalation_tickets").fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p1
    def test_guard_escalation_expires_after_granted_check(self, db):
        """Test ID: T-ESC-GUARD-04. Cláusula: H-21c [ADOPTED 2026-10-13]: intervalo vacío imposible en tickets
        ACTIVE; el DDL impone CHECK (expires_at > granted_at) (001_module1_schema.sql l.113). AD-13 (spine-local).
        Historia: E4-S2.

        Assertions: expires_at == granted_at y expires_at < granted_at fallan con CHECK constraint; expires_at >
        granted_at se acepta.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-GUARD-INT", "STU-GUARD-INT")
        insert = (
            "INSERT INTO escalation_tickets (id, requester_id, subject_id, requested_role_id,"
            " duration_hours, justification, status, approved_by, rejection_reason, granted_at,"
            " expires_at, revoked_at, created_at, updated_at)"
            " VALUES (?, ?, 'CS-480', 'ta', 1, 'Justificación de prueba ATDD de intervalo', 'ACTIVE',"
            " NULL, NULL, ?, ?, NULL, ?, ?)"
        )
        for ticket_id, expires in (("ticket-int-eq", CLOCK_START), ("ticket-int-lt", at_offset(-ONE_HOUR_US))):
            with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
                db.execute(insert, (ticket_id, identity, CLOCK_START, expires, CLOCK_START, CLOCK_START))
            db.rollback()
        db.execute(insert, ("ticket-int-ok", identity, CLOCK_START, at_offset(ONE_HOUR_US),
                            CLOCK_START, CLOCK_START))
        db.commit()
        assert db.execute("SELECT COUNT(*) FROM escalation_tickets").fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p0
    def test_guard_escalation_self_approval_rejected(self, db):
        """Test ID: T-ESC-GUARD-03. Cláusula: R9-02 / AD-05 (heredado) prohibición de auto-aprobación.
        CHECK (approved_by IS NULL OR approved_by <> requester_id) en escalation_tickets.

        Assertions: un ticket con approved_by == requester_id falla con CHECK constraint; un ticket con
        approved_by de otra identidad se acepta; un ticket sin aprobador (NULL) se acepta.
        """
        ensure_base(db)
        requester = add_identity(db, "ID-GUARD-SELF", "STU-GUARD-SELF")
        approver = add_identity(db, "ID-GUARD-APR", "TA-GUARD-APR")
        insert = (
            "INSERT INTO escalation_tickets (id, requester_id, subject_id, requested_role_id,"
            " duration_hours, justification, status, approved_by, rejection_reason, granted_at,"
            " expires_at, revoked_at, created_at, updated_at)"
            " VALUES (?, ?, 'CS-480', 'ta', 1, 'Justificación de prueba ATDD de aprobación', ?,"
            " ?, NULL, ?, ?, NULL, ?, ?)"
        )
        expires = at_offset(ONE_HOUR_US)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            db.execute(insert, ("ticket-self-bad", requester, "ACTIVE", requester,
                                CLOCK_START, expires, CLOCK_START, CLOCK_START))
        db.rollback()
        db.execute(insert, ("ticket-self-ok", requester, "ACTIVE", approver,
                            CLOCK_START, expires, CLOCK_START, CLOCK_START))
        db.execute(insert, ("ticket-pend-ok", approver, "PENDING_APPROVAL", None, None, None,
                            CLOCK_START, CLOCK_START))
        db.commit()
        assert db.execute("SELECT COUNT(*) FROM escalation_tickets").fetchone() == (2,)

    @pytest.mark.guard
    @pytest.mark.p1
    def test_guard_audit_timestamp_fixed_format_check(self, db):
        """Test ID: T-LED-GUARD-06. Cláusula: R9-04 [ADOPTED 2026-10-14, estudiante] (ADVF-23): audit_ledger.timestamp
        y audit_events.occurred_at con formato fijo YYYY-MM-DDTHH:MM:SS.ffffffZ (6 decimales, zona Z).

        Assertions: un timestamp sin microsegundos falla con CHECK constraint; el formato fijo se acepta.
        """
        ensure_base(db)
        insert = (
            "INSERT INTO audit_ledger (event_id, timestamp, actor_id, actor_role, subject_id,"
            " resource_arn, resource_type, action, decision, reason_code, prev_record_hash,"
            " record_hash, created_at, updated_at) VALUES (?, ?, 'ID-FMT', 'student', 'CS-480',"
            " 'urn:uai:subject:CS-480:model:llama-3-8b-instruct', ?, 'inference', 'ALLOW', 'SUCCESS',"
            " ?, ?, ?, ?)"
        )
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
            db.execute(insert, ("evt-fmt-bad", "2026-09-23T15:04:05Z", RESOURCE_TYPE,
                                ARBITRARY_PREV_HASH, RECORD_HASH, CLOCK_START, CLOCK_START))
        db.rollback()
        db.execute(insert, ("evt-fmt-ok", CLOCK_START, RESOURCE_TYPE,
                            ARBITRARY_PREV_HASH, RECORD_HASH, CLOCK_START, CLOCK_START))
        db.commit()
        assert db.execute("SELECT COUNT(*) FROM audit_ledger").fetchone() == (1,)

    @pytest.mark.guard
    @pytest.mark.p1
    def test_guard_audit_ledger_resource_type_not_null_and_indexed(self, db):
        """Test ID: T-LED-GUARD-05. Cláusula: R8-07 / NFR-AUDIT-06. audit_ledger.resource_type NOT NULL
        e índice compuesto idx_audit_resource_timestamp (resource_type, timestamp).

        Assertions: insertar sin resource_type falla con NOT NULL; el índice existe con columnas
        (resource_type, timestamp) en ese orden.
        """
        ensure_base(db)
        with pytest.raises(sqlite3.IntegrityError, match="NOT NULL constraint failed: audit_ledger.resource_type"):
            db.execute(
                "INSERT INTO audit_ledger (event_id, timestamp, actor_id, actor_role, subject_id,"
                " resource_arn, action, decision, reason_code, prev_record_hash, record_hash,"
                " created_at, updated_at) VALUES ('evt-guard-nn', ?, 'ID-G', 'student', 'CS-480',"
                " 'urn:uai:subject:CS-480:model:x', 'inference', 'ALLOW', 'SUCCESS', ?, ?, ?, ?)",
                (CLOCK_START, ARBITRARY_PREV_HASH, RECORD_HASH, CLOCK_START, CLOCK_START),
            )
        db.rollback()

        columns = [row[2] for row in db.execute("PRAGMA index_info('idx_audit_resource_timestamp')")]
        assert columns == ["resource_type", "timestamp"]

    @pytest.mark.guard
    @pytest.mark.p1
    def test_guard_edge_case_seed_duplicates_rejected_by_pk(self, db, edge_case_seeds):
        """Test ID: T-SEED-GUARD-01 (gap G-14; E1-S1). Cláusula: el seed del Mandatory Edge Case no puede duplicarse
        en silencio: las PK físicas de roles, subjects e identities rechazan la segunda inserción. Invariante
        físico del DDL 001 (verde, no RED). La idempotencia del seeding es responsabilidad del fixture
        edge_case_seeds. AD-08 (spine-local).

        Assertions: re-insertar roles 'student', subjects 'CS101' e identities con el mismo id lanza IntegrityError.
        """
        for statement, params in (
            ("INSERT INTO roles (id, name, priority_level, description) VALUES ('student', 'dup', 1, 'dup')", ()),
            (
                "INSERT INTO subjects (id, name, term, department, is_active, created_at, updated_at)"
                " VALUES ('CS101', 'dup', '2026-FALL', 'dup', 1, ?, ?)",
                (CLOCK_START, CLOCK_START),
            ),
            (
                "INSERT INTO identities (id, institutional_id, email, full_name, status, created_at, updated_at)"
                " VALUES (?, 'DUP-01', 'dup@universidad.edu', 'dup', 'ACTIVE', ?, ?)",
                (edge_case_seeds["identity_id"], CLOCK_START, CLOCK_START),
            ),
        ):
            with pytest.raises(sqlite3.IntegrityError):
                db.execute(statement, params)
            db.rollback()


class TestDomainPurity:
    """AD-08 (spine-local) / H-25: app/domain/ es núcleo puro (verde: el stub no importa infraestructura)."""

    @pytest.mark.guard
    @pytest.mark.p0
    def test_domain_has_no_infrastructure_imports_or_clock_calls(self):
        """Test ID: T-PUR-GUARD-01. Cláusula: AD-08 / H-25. Recorre con ast todos los .py de app/domain/.

        Assertions: ningún módulo importa fastapi, sqlalchemy, sqlite3, random, secrets, uuid, os ni time,
        y ninguno llama datetime.now / utcnow / today (el tiempo entra por el puerto Clock).
        """
        files = sorted(DOMAIN_DIR.glob("*.py"))
        assert files, "app/domain/ vacío: el guard no puede verificar nada"

        assert _pure_violations() == []

    @pytest.mark.guard
    @pytest.mark.p3
    @pytest.mark.parametrize(
        "source",
        [
            "import os\nx = os.urandom(8)\n",
            "from os import urandom\nx = urandom(8)\n",
            "import uuid\nx = uuid.uuid4()\n",
            "import secrets\nx = secrets.token_hex(8)\n",
            "import time\nx = time.monotonic()\n",
            "from datetime import datetime\nx = datetime.now()\n",
            "import random\nx = random.random()\n",
        ],
        ids=["os.urandom", "from-os-urandom", "uuid4", "secrets", "time.monotonic", "datetime.now", "random"],
    )
    def test_domain_purity_lint_detects_each_nondeterminism_source(self, tmp_path, monkeypatch, source):
        """Test ID: T-PUR-GUARD-02. Cláusula: H-25 [ADOPTED 2026-10-13]: domain/ no usa NINGUNA fuente de
        no-determinismo (random, secrets, uuid, os.urandom, time.*, datetime.now/utcnow/today). AD-08 (spine-local).
        Historia: E1-S1.

        Assertions: sobre un módulo sintético con cada fuente, el lint reporta al menos una violación (el lint
        actual ya cubre la lista de H-25; esta prueba lo demuestra, no solo lo asume).
        """
        (tmp_path / "sintetico.py").write_text(source, encoding="utf-8")
        monkeypatch.setitem(_pure_violations.__globals__, "DOMAIN_DIR", tmp_path)

        assert _pure_violations(), f"el lint no detecta la fuente: {source!r}"


class TestErrorEnvelope:
    """Envelope de errores del catálogo acotado (F-06): ningún status 500 ni de escalación sale sin ErrorBody."""

    @pytest.mark.guard
    @pytest.mark.p2
    def test_guard_audit_log_tampering_500_uses_error_body_without_explanation(self):
        """Test ID: T-ERR-GUARD-01. Cláusula: F-06 [ADOPTED 2026-10-13]: 500 AUDIT_LOG_TAMPERING_DETECTED usa el
        envelope ErrorBody (RFC-7807) sin ExplanationDTO. Ninguna de las tres operaciones lo emite (emisor fuera
        de alcance, openapi.yaml l.504 'pendiente'), así que se guarda el schema contra dto.py y openapi.yaml.
        AD-11 (spine-local). Historia: E1-S3.

        Assertions: el código figura en el Literal ErrorCode de dto.py; ErrorBody no declara el campo
        `explanation`; la respuesta 500 de openapi.yaml referencia ErrorBody y no ExplanationDTO.
        """
        tree = ast.parse(DTO_PATH.read_text(encoding="utf-8"), filename=str(DTO_PATH))
        error_codes: set[str] = set()
        error_body_fields: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "ErrorCode" for t in node.targets):
                error_codes = {c.value for c in ast.walk(node.value) if isinstance(c, ast.Constant)}
            if isinstance(node, ast.ClassDef) and node.name == "ErrorBody":
                error_body_fields = {
                    s.target.id for s in node.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)
                }

        assert "AUDIT_LOG_TAMPERING_DETECTED" in error_codes
        assert "explanation" not in error_body_fields
        assert {"code", "status", "detail"} <= error_body_fields

        lines = OPENAPI_PATH.read_text(encoding="utf-8").splitlines()
        start = next(i for i, line in enumerate(lines) if "500 — AUDIT_LOG_TAMPERING_DETECTED" in line)
        block: list[str] = []
        for line in lines[start + 1:]:  # la respuesta termina en la siguiente clave de respuesta (indent <= 4)
            if line.strip() and len(line) - len(line.lstrip()) <= 4:
                break
            block.append(line)
        block_text = "\n".join(block)
        assert "$ref: '#/components/schemas/ErrorBody'" in block_text
        assert "ExplanationDTO" not in block_text
