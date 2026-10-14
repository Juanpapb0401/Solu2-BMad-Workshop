"""module1_ingest_rules_contracts.test.py — Suite ATDD RED de ingestRoster: reglas FR-INGEST-01 2/3,
identidades, membresías inactivas, credenciales (NFR-SEC-05) y secretos (R-006 en ingest).

Separado de module1_ingest_contracts.test.py para mantener cada archivo < 600 líneas.
RED = xfail(raises=NotImplementedError, strict=True). Fuente: contracts.md §3 y §4, PRD FR-INGEST-01.
Helpers compartidos en atdd_support.py."""

from __future__ import annotations

import hashlib
import logging

import pytest

from app.application.module1 import build_module1
from app.domain.errors import Module1Error
from fakes.fake_credential_delivery import FakeCredentialDelivery
from fakes.fake_token_verifier import ADMIN_TOKEN
from fakes.world import (
    CLOCK_START,
    add_identity,
    add_membership,
    counts,
    ensure_base,
    events,
    membership_row,
)
from atdd_support import (
    SECRET_FULL,
    SECRET_RAW_RE,
    assert_no_writes,
    red,
    roster_batch,
    roster_row,
)


class TestInvariants:
    """Categoría I (invariantes y fronteras): atomicidad, aislamiento, límites y reglas de precedencia."""

    @red("p0")
    @pytest.mark.parametrize("status", ["SUSPENDED", "EXPELLED"])
    def test_ingest_barred_identity_rejects_whole_batch_422(self, db, module1, status):
        """Test ID: T-ROS-14 (FR-INGEST-01 regla 3 / contracts §3 P4). Cláusula: identidad global SUSPENDED o
        EXPELLED -> IDENTITY_BARRED 422 con manifiesto; el lote entero se rechaza. AD-02 (heredado).

        Assertions: 422 con code ROSTER_VALIDATION_FAILED (R9-01 [ADOPTED 2026-10-14, estudiante]); la fila del
        manifiesto tiene field identity_status y rule_ids ['ROSTER_VALIDATION_FAILED', 'IDENTITY_BARRED'];
        cero escrituras en las cuatro tablas; un roster.rejected.
        Nota: IDENTITY_BARRED 403 aplica solo a /authorize (R9-01).
        """
        ensure_base(db)
        add_identity(db, "ID-STU-00009", "STU-00009", status=status)
        row = roster_row(9)
        row["email"] = "stu-00009@universidad.edu"
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([row]))

        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        identity_row = next(e for e in exc.value.body["errors"] if e["field"] == "identity_status")
        assert identity_row["code"] == "ROSTER_VALIDATION_FAILED"
        assert identity_row["rule_ids"] == ["ROSTER_VALIDATION_FAILED", "IDENTITY_BARRED"]
        assert_no_writes(before, counts(db))
        assert len(events(db, "roster.rejected")) == 1

    @red("p1")
    def test_ingest_conflicting_identity_row_422_no_identity_update(self, db, module1):
        """Test ID: T-ROS-15 (ADVF-19 / ECF-09, E3-S3). Cláusula: contracts §3 P3: institutional_id ya existente
        con otro email -> ROSTER_VALIDATION_FAILED por fila; la identidad NO se actualiza. AD-02 (heredado).

        Assertions: 422 ROSTER_VALIDATION_FAILED; el email de la identidad sigue igual; cero escrituras.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-00010", "STU-00010")
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(10)]))

        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        assert db.execute(
            "SELECT email FROM identities WHERE institutional_id = 'STU-00010'"
        ).fetchone() == ("stu-00010@universidad.edu",)
        assert_no_writes(before, counts(db))

    @red("p1")
    @pytest.mark.parametrize("status", ["DROPPED", "SUSPENDED", "COMPLETED"])
    def test_ingest_same_role_on_inactive_membership_not_reactivated(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, status
    ):
        """Test ID: T-ROS-16 (ADVF-15 / ECF-23, E3-S3). Cláusula: contracts §3 Invariantes: membresía previa en
        DROPPED, SUSPENDED o COMPLETED con el mismo rol NO se reactiva; la fila cuenta como sin cambios (no
        updated_memberships) y no emite credencial. AD-02 (heredado); la elevación solo por escalación (AD-05).

        Assertions: processed 1; updated_memberships 0; membresía conserva su estado; 0 entregas de credencial.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-00011", "STU-00011")
        add_membership(
            db, identity, "CS-480", "student", status=status,
            dropped_at=CLOCK_START if status == "DROPPED" else None,
        )
        delivery = FakeCredentialDelivery()
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN, delivery
        )
        row = roster_row(11)
        row["email"] = "stu-00011@universidad.edu"

        result = service.ingest_roster(roster_batch([row]))

        assert (result["processed"], result["updated_memberships"]) == (1, 0)
        assert membership_row(db, identity, "CS-480")["status"] == status
        assert delivery.deliveries == []

    @red("p1")
    def test_ingest_credential_hash_uses_16_byte_salt_and_no_raw_key_stored(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-17 (NFR-SEC-05, E3-S1). Cláusula: DDL subject_credentials: key_hash = SHA-256(salt || raw_key)
        con salt de 16 bytes; la clave en claro nunca se persiste. AD-06 (heredado).
        [ASSUMPTION] la salt se almacena en hexadecimal (32 caracteres) y se concatena como bytes.

        Assertions: la salt decodificada mide 16 bytes; key_hash == sha256(salt_bytes + raw_key); la clave en
        claro no aparece en ninguna tabla.
        """
        ensure_base(db)
        delivery = FakeCredentialDelivery()
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN, delivery
        )
        service.ingest_roster(roster_batch([roster_row(1)]))
        identity, raw_key = delivery.deliveries[0]

        key_hash, salt = db.execute(
            "SELECT key_hash, salt FROM subject_credentials WHERE identity_id = ?", (identity,)
        ).fetchone()
        assert len(bytes.fromhex(salt)) == 16
        assert key_hash == hashlib.sha256(bytes.fromhex(salt) + raw_key.encode("utf-8")).hexdigest()
        dump = " ".join(str(row) for row in db.execute("SELECT * FROM subject_credentials").fetchall())
        assert raw_key not in dump

    @red("p1")
    def test_ingest_credential_lookup_by_key_prefix_then_verifies_hash(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-G-13 (gap G-13; ADVF-17 / ECF-18, E3-S1). Cláusula: la credencial se localiza por key_prefix
        (el salt impide buscar por key_hash) y luego se verifica SHA-256(salt || raw_key) sobre las filas que
        casan el prefijo (idx_credentials_key_prefix). AD-06 (heredado). Historia E3-S1.

        Assertions: el key_prefix almacenado es prefijo de la clave entregada; la búsqueda por key_prefix ACTIVE
        devuelve exactamente una fila; su key_hash == sha256(salt || raw_key).
        """
        ensure_base(db)
        delivery = FakeCredentialDelivery()
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN, delivery
        )
        service.ingest_roster(roster_batch([roster_row(1)]))
        identity, raw_key = delivery.deliveries[0]
        (stored_prefix,) = db.execute(
            "SELECT key_prefix FROM subject_credentials WHERE identity_id = ?", (identity,)
        ).fetchone()
        assert raw_key.startswith(stored_prefix)

        matches = db.execute(
            "SELECT key_hash, salt FROM subject_credentials WHERE key_prefix = ? AND status = 'ACTIVE'",
            (stored_prefix,),
        ).fetchall()
        assert len(matches) == 1
        key_hash, salt = matches[0]
        assert key_hash == hashlib.sha256(bytes.fromhex(salt) + raw_key.encode("utf-8")).hexdigest()


class TestSecrets:
    """R-006 / AD-06: ningún secreto `uai_live_` completo sale en respuesta, log o ledger."""
    @red("p0")
    def test_ingest_secret_in_batch_field_never_in_manifest_or_logs(self, db, module1, caplog):
        """Test ID: T-SEC-ROS-01 (Riesgo 3 de test-review, R-006 en ingest, AD-06). Cláusula: AD-06 (heredado): una
        clave uai_live_ completa enviada dentro de un campo del lote no aparece en el manifiesto 422 ni en logs,
        ni en el evento roster.rejected del ledger.

        Setup: fila 2 con la clave completa en full_name y email externo (fuerza el 422).
        Assertions: regex uai_live_[A-Za-z0-9]{8,} ausente en la excepción, en caplog y en audit_events.payload.
        """
        ensure_base(db)
        rows = [roster_row(1), roster_row(2)]
        rows[1]["full_name"] = "Nombre " + SECRET_FULL
        rows[1]["email"] = "stu00002@gmail.com"

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(Module1Error) as exc:
                module1.ingest_roster(roster_batch(rows))

        payloads = " ".join(str(row) for row in db.execute("SELECT payload FROM audit_events").fetchall())
        blob = " ".join([str(exc.value.body), caplog.text, payloads])
        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert not SECRET_RAW_RE.search(blob), "clave uai_live_ completa en manifiesto o logs"
