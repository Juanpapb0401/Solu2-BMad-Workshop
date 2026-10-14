"""Seeds y consultas SQL para la suite ATDD (datos de prueba, sin reglas de negocio).

Las filas se insertan respetando el DDL 001_module1_schema.sql (CHECK, UNIQUE, FK).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

BASE = datetime(2026, 9, 23, 15, 4, 5, tzinfo=timezone.utc)
CLOCK_START = BASE.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
TABLES = (
    "identities",
    "subjects",
    "roles",
    "subject_memberships",
    "escalation_tickets",
    "subject_credentials",
    "audit_ledger",
    "audit_events",
    "audit_ledger_metadata",
    "roster_batches",
)
TERM = "2026-FALL"  # term del seed de asignaturas (ensure_base)
STUDENT_ID = "STU-98432"
STUDENT_IDENTITY = "ID-STU-98432"


def at_offset(micros: int) -> str:
    """Instante UTC con microsegundos, desplazado desde CLOCK_START."""
    return (BASE + timedelta(microseconds=micros)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _id(db: Any, table: str, prefix: str) -> str:
    """ID de seed determinista por BD: prefijo + (filas actuales de la tabla + 1). Sin contador global."""
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return f"{prefix}-{count + 1:06d}"


def ensure_base(db: Any) -> None:
    """Roles y asignaturas del seed (idempotente)."""
    db.executemany(
        "INSERT OR IGNORE INTO roles (id, name, priority_level, description) VALUES (?, ?, ?, ?)",
        [
            ("student", "Student", 10, "seed ATDD"),
            ("ta", "Teaching Assistant", 50, "seed ATDD"),
            ("instructor_privileged", "Instructor-Privileged", 80, "seed ATDD"),
        ],
    )
    db.executemany(
        "INSERT OR IGNORE INTO subjects (id, name, term, department, is_active,"
        " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("CS101", "Intro to Programming", "2026-FALL", "Computer Science", 1, CLOCK_START, CLOCK_START),
            ("CS-480", "Intro to Machine Learning", "2026-FALL", "Computer Science", 1, CLOCK_START, CLOCK_START),
        ],
    )
    db.commit()


def add_identity(db: Any, identity_id: str, institutional_id: str, status: str = "ACTIVE") -> str:
    db.execute(
        "INSERT INTO identities (id, institutional_id, email, full_name, status, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (identity_id, institutional_id, f"{institutional_id.lower()}@universidad.edu",
         f"Seed {institutional_id}", status, CLOCK_START, CLOCK_START),
    )
    db.commit()
    return identity_id


def add_membership(
    db: Any, identity_id: str, subject_id: str, role_id: str,
    status: str = "ACTIVE", dropped_at: str | None = None, term: str = TERM,
) -> str:
    """Membresía con term obligatorio en el DDL (Ronda 6 Q3 / ADVF-13)."""
    mid = _id(db, "subject_memberships", "mem")
    db.execute(
        "INSERT INTO subject_memberships (id, identity_id, subject_id, role_id, term, status,"
        " enrolled_at, dropped_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mid, identity_id, subject_id, role_id, term, status, CLOCK_START, dropped_at,
         CLOCK_START, CLOCK_START),
    )
    db.commit()
    return mid


def add_credential(db: Any, identity_id: str, subject_id: str, status: str = "ACTIVE") -> str:
    cid = _id(db, "subject_credentials", "cred")
    db.execute(
        "INSERT INTO subject_credentials (id, identity_id, subject_id, key_prefix, key_hash, salt,"
        " status, created_at, updated_at, revoked_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (cid, identity_id, subject_id, "uai_live_seed", f"hash-{cid}", "00112233445566778899aabbccddeeff",
         status, CLOCK_START, CLOCK_START, None),
    )
    db.commit()
    return cid


def add_ticket(
    db: Any, identity_id: str, subject_id: str, role_id: str,
    granted_at: str, expires_at: str,
) -> str:
    tid = _id(db, "escalation_tickets", "ticket")
    db.execute(
        "INSERT INTO escalation_tickets (id, requester_id, subject_id, requested_role_id,"
        " duration_hours, justification, status, approved_by, rejection_reason, granted_at,"
        " expires_at, revoked_at, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, 1, ?, 'ACTIVE', NULL, NULL, ?, ?, NULL, ?, ?)",
        (tid, identity_id, subject_id, role_id,
         "Escalación de prueba ATDD vigente en la ventana", granted_at, expires_at,
         CLOCK_START, CLOCK_START),
    )
    db.commit()
    return tid


def seed_student_pair(db: Any) -> str:
    """STU-98432: Student ACTIVE en CS101 (2 credenciales) y CS-480 (1 credencial)."""
    ensure_base(db)
    add_identity(db, STUDENT_IDENTITY, STUDENT_ID)
    add_membership(db, STUDENT_IDENTITY, "CS101", "student")
    add_membership(db, STUDENT_IDENTITY, "CS-480", "student")
    add_credential(db, STUDENT_IDENTITY, "CS101")
    add_credential(db, STUDENT_IDENTITY, "CS101")
    add_credential(db, STUDENT_IDENTITY, "CS-480")
    return STUDENT_IDENTITY


def counts(db: Any) -> dict[str, int]:
    return {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}


def query_dicts(db: Any, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    cur = db.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def membership_row(db: Any, identity_id: str, subject_id: str) -> dict[str, Any] | None:
    rows = query_dicts(
        db,
        "SELECT status, dropped_at, role_id FROM subject_memberships"
        " WHERE identity_id = ? AND subject_id = ?",
        (identity_id, subject_id),
    )
    return rows[0] if rows else None


def credential_rows(db: Any, identity_id: str, subject_id: str) -> list[dict[str, Any]]:
    return query_dicts(
        db,
        "SELECT status, revoked_at FROM subject_credentials"
        " WHERE identity_id = ? AND subject_id = ? ORDER BY id",
        (identity_id, subject_id),
    )


def events(db: Any, event_type: str | None = None) -> list[dict[str, Any]]:
    """Eventos del ledger (audit_events 1:1 con audit_ledger), en orden de cadena."""
    sql = (
        "SELECT e.event_id, e.event_type, e.payload, l.decision, l.reason_code,"
        " l.record_hash, l.prev_record_hash FROM audit_events e"
        " JOIN audit_ledger l ON l.event_id = e.event_id"
    )
    params: tuple = ()
    if event_type is not None:
        sql += " WHERE e.event_type = ?"
        params = (event_type,)
    return query_dicts(db, sql + " ORDER BY l.id ASC", params)


def ticket_status(db: Any, ticket_id: str) -> str:
    return db.execute("SELECT status FROM escalation_tickets WHERE id = ?", (ticket_id,)).fetchone()[0]
