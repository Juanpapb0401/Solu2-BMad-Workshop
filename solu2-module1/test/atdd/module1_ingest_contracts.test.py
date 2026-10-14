"""module1_ingest_contracts.test.py — Suite ATDD RED de ingestRoster (contracts.md §3).

RED = xfail(raises=NotImplementedError, strict=True). Categorías: Q, P, I, X. Fuente: contracts.md §3 y §4, PRD FR-INGEST-01. Helpers en atdd_support.py."""

from __future__ import annotations

import hashlib
import logging
import re

import pytest

from app.adapters.http import http_roster
from app.application.module1 import build_module1
from app.domain.errors import Module1Error
from fakes.fake_credential_delivery import FakeCredentialDelivery
from fakes.fake_failing_ports import RaisingIdGenerator
from fakes.fake_token_verifier import ADMIN_TOKEN, STUDENT_TOKEN
from fakes.world import (
    CLOCK_START,
    STUDENT_ID,
    add_identity,
    add_membership,
    counts,
    ensure_base,
    events,
    membership_row,
    query_dicts,
)
from atdd_support import (
    SECRET_FULL,
    SECRET_RAW_RE,
    assert_code_first,
    assert_no_writes,
    red,
    roster_batch,
    roster_row,
)


class TestHappyPath:
    """Categoría Q (happy path): el flujo feliz produce el estado y los eventos esperados."""

    @red("p0")
    def test_ingest_valid_batch_persists_all_rows(self, db, module1):
        """Test ID: T-ROS-HP-01 (nuevo). Cláusula: Q1 (201 con batch_id roster-<8hex>-<term>) y Q2 (todo o nada:
        identidades, membresías y credenciales del lote persisten). AD-02 (heredado).

        Assertions: processed 3, created_identities 3, updated_memberships 3; batch_id con formato;
        +3 identidades, +3 membresías ACTIVE con rol del lote, +3 credenciales ACTIVE, +1 roster_batches.
        """
        ensure_base(db)
        before = counts(db)
        rows = [roster_row(1), roster_row(2), roster_row(3, role="ta")]

        result = module1.ingest_roster(roster_batch(rows))

        assert result["processed"] == 3
        assert result["created_identities"] == 3
        assert result["updated_memberships"] == 3
        assert re.fullmatch(r"roster-[0-9a-f]{8}-2026-FALL", result["batch_id"])
        after = counts(db)
        assert after["identities"] == before["identities"] + 3
        assert after["subject_memberships"] == before["subject_memberships"] + 3
        assert after["subject_credentials"] == before["subject_credentials"] + 3
        assert after["roster_batches"] == before["roster_batches"] + 1
        ta = db.execute(
            "SELECT role_id, status FROM subject_memberships m JOIN identities i ON i.id = m.identity_id"
            " WHERE i.institutional_id = 'STU-00003'"
        ).fetchone()
        assert ta == ("ta", "ACTIVE")


    @red("p1")
    def test_ingest_emits_one_roster_ingested_event(self, db, module1):
        """Test ID: T-ROS-HP-02 (nuevo). Cláusula: Q3 (evento roster:ingest por lote comprometido con batch_id).
        AD-04 (heredado).

        Assertions: +1 evento roster.ingested cuyo payload contiene el batch_id devuelto; ningún roster.rejected.
        """
        ensure_base(db)

        result = module1.ingest_roster(roster_batch([roster_row(1), roster_row(2)]))

        ingested = events(db, "roster.ingested")
        assert len(ingested) == 1
        assert result["batch_id"] in ingested[0]["payload"]
        assert events(db, "roster.rejected") == []

    @red("p0")
    def test_ingest_enqueues_one_credential_per_accepted_row_without_key_in_response(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-04 (R7-03 corregido por R8-01). Cláusula: contracts §3 Q2: CredentialDeliveryPort.enqueue
        se llama exactamente una vez por cada membresía que el lote deja ACTIVE (= una por fila aceptada);
        la respuesta 201 no incluye uai_live_ en claro. AD-06 (heredado), AD-02 (heredado).

        Assertions: processed 3; 3 entregas con raw key uai_live_ y 3 identidades distintas; 3 credenciales
        ACTIVE; ninguna clave en la respuesta (repr del resultado).
        """
        ensure_base(db)
        delivery = FakeCredentialDelivery()
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN, delivery
        )

        result = service.ingest_roster(roster_batch([roster_row(1), roster_row(2), roster_row(3)]))

        assert result["processed"] == 3
        assert "uai_live_" not in repr(result)
        assert len(delivery.deliveries) == 3
        assert len({identity for identity, _ in delivery.deliveries}) == 3
        assert all(raw.startswith("uai_live_") for _, raw in delivery.deliveries)
        assert db.execute("SELECT COUNT(*) FROM subject_credentials WHERE status = 'ACTIVE'").fetchone() == (3,)

    @red("p1")
    def test_ingest_email_domain_case_insensitive_local_part_preserved(self, db, module1):
        """Test ID: T-ROS-18 (ECF-07, E3-S4 happy dominio). Cláusula: contracts §3 P3: el dominio se compara sin
        distinguir mayúsculas; el resto del email se conserva intacto (sin reescribir). AD-02 (heredado).

        Assertions: processed 1; el email guardado es exactamente 'ALUMNO@Universidad.EDU'.
        """
        ensure_base(db)
        row = roster_row(1)
        row["email"] = "ALUMNO@Universidad.EDU"

        result = module1.ingest_roster(roster_batch([row]))

        assert result["processed"] == 1
        assert db.execute(
            "SELECT email FROM identities WHERE institutional_id = ?", (row["institutional_id"],)
        ).fetchone() == ("ALUMNO@Universidad.EDU",)

    @red("p1")
    def test_ingest_reuses_existing_identity_without_duplicate(self, db, module1):
        """Test ID: T-ROS-19 (FR-INGEST-01 regla 3). Cláusula: PRD FR-INGEST-01 regla 3: si la identidad ya existe
        por otra asignatura no se duplica; solo se asocia el nuevo vínculo (identidad, materia, rol, term).
        AD-02 (heredado).

        Setup: STU-00007 existe con membresía en CS101. Assertions: created_identities 0; updated_memberships 1;
        sigue habiendo una sola identidad para STU-00007; la membresía de CS101 no cambia; nueva membresía
        ACTIVE en CS-480.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-00007", "STU-00007")
        add_membership(db, identity, "CS101", "student")
        row = roster_row(7)
        row["email"] = "stu-00007@universidad.edu"  # mismo email que la identidad existente (sin conflicto)

        result = module1.ingest_roster(roster_batch([row]))

        assert (result["processed"], result["created_identities"], result["updated_memberships"]) == (1, 0, 1)
        assert db.execute(
            "SELECT COUNT(*) FROM identities WHERE institutional_id = 'STU-00007'"
        ).fetchone() == (1,)
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert membership_row(db, identity, "CS-480")["status"] == "ACTIVE"

    @red("p1")
    @pytest.mark.parametrize("subject", ["CS-999", "CS-OLD"], ids=["inexistente", "inactiva"])
    def test_ingest_unknown_or_inactive_subject_404_no_writes(self, db, module1, subject):
        """Test ID: T-ROS-07 (FR-INGEST-01 regla 2, contracts §3 P1). Cláusula: subject_id inexistente o no activo
        -> UNKNOWN_COURSE 404 sin escrituras. AD-02 (heredado).

        Parametrizado: CS-999 (no existe) y CS-OLD (existe con is_active = 0).
        Assertions: 404 UNKNOWN_COURSE; cero filas nuevas en identidades, membresías, credenciales y lotes.
        """
        ensure_base(db)
        db.execute(
            "INSERT INTO subjects (id, name, term, department, is_active, created_at, updated_at)"
            " VALUES ('CS-OLD', 'Asignatura retirada', '2026-FALL', 'Computer Science', 0, ?, ?)",
            (CLOCK_START, CLOCK_START),
        )
        db.commit()
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(1)], subject=subject))

        assert exc.value.code == "UNKNOWN_COURSE"
        assert exc.value.http_status == 404
        assert_no_writes(before, counts(db))


class TestPreconditions:
    """Categoría P (precondiciones): rechazo tipado con HTTP exacto, cero mutación y cero eventos."""

    @red("p0")
    def test_ingest_malformed_term_400_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-ROS-05 (term exacto YYYY-(SPRING|SUMMER|FALL), case-sensitive). Cláusula: P1 ->
        MALFORMED_TERM 400. Errores de formato no se auditan (Q-fail) y no hay batch_id (F-04).

        Assertions: 400; cero escrituras; cero eventos; el cuerpo de error no lleva batch_id.
        """
        ensure_base(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(1)], term="2026-fall"))

        assert exc.value.code == "MALFORMED_TERM"
        assert exc.value.http_status == 400
        assert "batch_id" not in exc.value.body
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p1")
    def test_ingest_empty_batch_400_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-ROS-06 (lote de 0 filas). Cláusula: P2 -> BATCH_EMPTY 400. Sin batch_id (F-04).

        Assertions: BATCH_EMPTY 400; cero escrituras; cero eventos; sin batch_id.
        """
        ensure_base(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([]))

        assert exc.value.code == "BATCH_EMPTY"
        assert exc.value.http_status == 400
        assert "batch_id" not in exc.value.body
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_ingest_1001_rows_413_too_large_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-ROS-06b (frontera superior: >1000 filas). Cláusula: P2 -> BATCH_TOO_LARGE 413 antes de
        validar filas (G9-02). Sin batch_id (F-04).

        Assertions: BATCH_TOO_LARGE 413; cero escrituras (incluido roster_batches); cero eventos; sin batch_id.
        """
        ensure_base(db)
        before = counts(db)
        rows = [roster_row(n) for n in range(1, 1002)]

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        assert exc.value.code == "BATCH_TOO_LARGE"
        assert exc.value.http_status == 413
        assert "batch_id" not in exc.value.body
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_roster_intra_batch_duplicate(self, db, module1):
        """Test ID: T-ROS-02 / test_roster_intra_batch_duplicate. Cláusula: P4 -> INTRA_BATCH_DUPLICATE_ID 422
        (seen_ids exacto, case-sensitive) con manifiesto y cero escrituras. AD-02 (heredado).

        Assertions: 422 INTRA_BATCH_DUPLICATE_ID; cero identidades/membresías nuevas; roster.rejected registrado.
        """
        ensure_base(db)
        rows = [roster_row(1), roster_row(2), roster_row(3), roster_row(2)]
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        assert exc.value.code == "INTRA_BATCH_DUPLICATE_ID"
        assert exc.value.http_status == 422
        assert_no_writes(before, counts(db))
        assert len(events(db, "roster.rejected")) == 1


    @red("p0")
    def test_ingest_non_admin_actor_403_no_mutation(
        self,
        db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-P-05 (nuevo). Cláusula: P0 / Q1 (ADVF-01) -> 403 ADMIN_ROLE_REQUIRED antes de la
        sintaxis; sin mutación, sin evento, sin batch_id. AD-09 (spine-local), AD-02 (heredado).

        Assertions: actor estudiante -> 403; cero escrituras (incluido roster_batches); cero eventos;
        cola sin publicar; body sin batch_id ni explanation.
        """
        ensure_base(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, STUDENT_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.ingest_roster(roster_batch([roster_row(1), roster_row(2)]))

        assert exc.value.code == "ADMIN_ROLE_REQUIRED"
        assert exc.value.http_status == 403
        assert "batch_id" not in exc.value.body
        assert "explanation" not in exc.value.body
        assert counts(db) == before
        assert fake_queue.published == []

    @red("p0")
    def test_ingest_auth_token_invalid_401_before_batch_validation(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-20 (R8-04, AD-09). Cláusula: contracts §0 paso 1: bearer inválido -> 401 AUTH_TOKEN_INVALID
        antes de validar el lote (term 'bad' daría 400 MALFORMED_TERM). AD-09 (spine-local).

        RED: Module1Service es stub puro; la verificación del bearer (TokenVerifierPort) es lógica GREEN pendiente.
        Corrección: antes pasaba en verde porque el stub delegaba en el fake configurado por el test (tautología).

        Assertions: 401 AUTH_TOKEN_INVALID; cero mutación en las cuatro tablas de rechazo; cero eventos.
        """
        ensure_base(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, "tok-invalido"
        )

        with pytest.raises(Module1Error) as exc:
            service.ingest_roster(roster_batch([roster_row(1)], term="bad"))

        assert exc.value.code == "AUTH_TOKEN_INVALID"
        assert exc.value.http_status == 401
        assert_no_writes(before, counts(db))
        assert events(db) == []

    @red("p0")
    def test_ingest_student_token_403_admin_before_batch_syntax(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-09 (E2-S4 análogo, ADVF-01). Cláusula: contracts §3 P0: actor no admin -> 403
        ADMIN_ROLE_REQUIRED antes de la sintaxis (un lote vacío daría 400 BATCH_EMPTY). AD-09 (spine-local).

        Assertions: 403 ADMIN_ROLE_REQUIRED (no 400 BATCH_EMPTY); cero mutación; cero eventos.
        """
        ensure_base(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, STUDENT_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.ingest_roster(roster_batch([]))

        assert exc.value.code == "ADMIN_ROLE_REQUIRED"
        assert exc.value.http_status == 403
        assert_no_writes(before, counts(db))
        assert events(db) == []

    @red("p1")
    def test_ingest_duplicate_email_in_batch_422_no_writes(self, db, module1):
        """Test ID: T-ROS-10 (ECF-08, E3-S2). Cláusula: contracts §3 P4: emails repetidos dentro del lote ->
        ROSTER_VALIDATION_FAILED detectado en memoria antes de la base. AD-02 (heredado).

        Assertions: 422 ROSTER_VALIDATION_FAILED; cero escrituras en las cuatro tablas; exactamente un roster.rejected.
        """
        ensure_base(db)
        rows = [roster_row(1), roster_row(2)]
        rows[1]["email"] = rows[0]["email"]
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        assert_no_writes(before, counts(db))
        assert len(events(db, "roster.rejected")) == 1

    @red("p1")
    @pytest.mark.parametrize("email", ["", "stu00001@gmail.com"], ids=["vacio", "dominio-externo"])
    def test_ingest_invalid_email_422_roster_validation_no_writes(self, db, module1, email):
        """Test ID: T-ROS-11 (ECF-17 y R8-09). Cláusula: contracts §3 P3: email vacío o fuera de universidad.edu ->
        fila del manifiesto ROSTER_VALIDATION_FAILED sobre el campo email. Para dominio externo, rule_ids incluye
        EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL (R8-09), sin código HTTP nuevo. AD-02 (heredado).

        Assertions: 422; la fila 1 del manifiesto cita field 'email'; cero escrituras; un roster.rejected.
        """
        ensure_base(db)
        row = roster_row(1)
        row["email"] = email
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([row]))

        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        assert any(e["row_number"] == 1 and e["field"] == "email" for e in exc.value.body["errors"])
        assert_no_writes(before, counts(db))
        assert len(events(db, "roster.rejected")) == 1

    @red("p1")
    def test_ingest_outside_domain_manifest_rule_ids_include_institutional_rule(self, db, module1):
        """Test ID: T-ROS-12 (R8-09). Cláusula: contracts §3 P3 [ADOPTED 2026-10-14, R8-09]: correo fuera de
        universidad.edu produce ROSTER_VALIDATION_FAILED con rule_ids ['ROSTER_VALIDATION_FAILED',
        'EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL'] para que el banner UX lo muestre. AD-11 (spine-local).

        Assertions: el manifiesto trae esa fila con rule_ids en ese orden; cero escrituras.
        """
        ensure_base(db)
        row = roster_row(1)
        row["email"] = "stu00001@gmail.com"
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([row]))

        manifest_row = next(e for e in exc.value.body["errors"] if e["field"] == "email")
        assert manifest_row["code"] == "ROSTER_VALIDATION_FAILED"
        assert manifest_row["rule_ids"] == ["ROSTER_VALIDATION_FAILED", "EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL"]
        assert_no_writes(before, counts(db))

    @red("p0")
    def test_ingest_queue_full_503_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-ROS-13 (R8-04, AD-12). Cláusula: contracts §3 Q3: si el evento de auditoría no es aceptado
        en la cola -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE fail-closed, sin descarte silencioso. AD-12 (spine-local),
        AD-02 (heredado).

        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; cero escrituras en las cuatro tablas; cero eventos.
        """
        ensure_base(db)
        before = counts(db)
        fake_queue.set_capacity(0)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(1), roster_row(2)]))

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert_no_writes(before, counts(db))
        assert events(db) == []

    @red("p0")
    def test_ingest_id_generator_failure_503_no_writes_no_credentials(
        self, db, fake_clock, fake_queue, fake_token_verifier
    ):
        """Test ID: T-ROS-21 (R12-B01, hallazgo SEC B-01). Cláusula: contracts §3 Q-fail [ADOPTED 2026-10-14,
        estudiante]: si IdGenerator lanza al asignar batch_id no existe batch_id válido; la respuesta es
        503 AUTH_INTERNAL_POLICY_UNAVAILABLE fail-closed (la excepción no se reintenta; el reintento x3 aplica
        solo a colisión UNIQUE). Cero escrituras en las cuatro tablas, cero credenciales, cero eventos.
        AD-12 (spine-local), AD-02 (heredado). Historia: E3-S1.

        Setup: ensure_base; servicio con RaisingIdGenerator (test/fakes/fake_failing_ports.py) y FakeCredentialDelivery.
        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; assert_no_writes; sin entregas de credencial; cero eventos.
        """
        ensure_base(db)
        before = counts(db)
        delivery = FakeCredentialDelivery()
        service = build_module1(
            db, fake_clock, RaisingIdGenerator(), fake_queue, fake_token_verifier, ADMIN_TOKEN, delivery
        )

        with pytest.raises(Module1Error) as exc:
            service.ingest_roster(roster_batch([roster_row(1), roster_row(2)]))

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert_no_writes(before, counts(db))
        assert delivery.deliveries == []
        assert events(db) == []

    @red("p1")
    @pytest.mark.parametrize(
        "body",
        [
            {"subject_id": "CS101", "term": "2026-FALL", "rows": [roster_row(1)]},
            {"term": "2026-FALL", "rows": [roster_row(1)]},
        ],
        ids=["eco-distinto", "eco-ausente"],
    )
    def test_http_roster_subject_echo_mismatch_400_malformed_batch(self, db, body):
        """Test ID: T-ROS-G-08 (gap G-8; ECF-05). Cláusula: openapi RosterIngestRequest.subject_id y contracts §3 P1:
        el subject_id del path manda; si el body lo repite distinto o no lo trae -> 400 MALFORMED_BATCH, sin
        batch_id ni escrituras. AD-09 (spine-local), AD-02 (heredado). Historia E3-S4.

        Assertions: Module1Error MALFORMED_BATCH con HTTP 400; conteos de tablas idénticos (cero eventos).
        """
        ensure_base(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            http_roster(ADMIN_TOKEN, "CS-480", "2026-FALL", body)

        assert exc.value.code == "MALFORMED_BATCH"
        assert exc.value.http_status == 400
        assert counts(db) == before


class TestInvariants:
    """Categoría I (invariantes y fronteras): atomicidad, aislamiento, límites y reglas de precedencia."""

    @red("p0")
    def test_roster_row85_rollback(self, db, module1, fake_queue):
        """Test ID: T-ROS-01 / test_roster_row85_rollback. Cláusula: I1 (atomicidad de lote) + Q3 (rechazo 422:
        rollback total y evento roster.rejected posterior). AD-02 (heredado), AD-04 (heredado).
        Fila 85 con @gmail.com -> 422 y 0 filas del lote.

        Assertions: 422 ROSTER_VALIDATION_FAILED con manifiesto (row_number 85, field 'email'); processed 0;
        cero identidades/membresías/credenciales/lotes nuevos; exactamente un roster.rejected.
        """
        ensure_base(db)
        rows = [roster_row(n) for n in range(1, 121)]
        rows[84]["email"] = "stu00085@gmail.com"
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        body = exc.value.body
        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        assert any(e["row_number"] == 85 and e["field"] == "email" for e in body["errors"])
        assert (body["processed"], body["created_identities"], body["updated_memberships"]) == (0, 0, 0)
        after = counts(db)
        for table in ("identities", "subject_memberships", "subject_credentials", "roster_batches"):
            assert after[table] == before[table], table
        rejected = events(db, "roster.rejected")
        assert len(rejected) == 1
        assert len(fake_queue.published) == 1


    @red("p0")
    def test_roster_no_role_smuggling(self, db, module1):
        """Test ID: T-ROS-03 (I2, invariante de ESTADO persistido; R10 desdoblamiento de T-ROS-03b).
        Cláusula: I2 (ningún rol preexistente cambia por importación). AD-02 (heredado); H-20: membresía
        previa con rol distinto -> rechazo 422 con escritura cero y un evento roster.rejected (regla S3).
        El detalle del manifiesto 422 (campo assigned_role) se asserta solo en T-ROS-03b.

        Assertions: 422; antes/después idénticos en identities, subject_memberships, subject_credentials y
        roster_batches (assert_no_writes); el rol de la membresía de STU-98432 en CS-480 sigue 'student';
        exactamente 1 evento roster.rejected.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, identity, "CS-480", "student")
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(98432, role="ta")]))
        # roster_row(98432) usa STU-98432; el rol entrante 'ta' intenta elevar al estudiante existente.
        assert exc.value.http_status == 422
        assert_no_writes(before, counts(db))
        assert membership_row(db, identity, "CS-480")["role_id"] == "student"
        assert len(events(db, "roster.rejected")) == 1


    @red("p1")
    def test_ingest_1000_rows_boundary_accepted(self, db, module1):
        """Test ID: T-ROS-I-04 (nuevo). Cláusula: P2 frontera inferior-superior: 1000 filas de datos es válido
        (1001 se rechaza, ver T-ROS-06b). AD-02 (heredado).

        Assertions: 201 con processed 1000 y created_identities 1000; +1000 membresías ACTIVE.
        """
        ensure_base(db)
        rows = [roster_row(n) for n in range(1, 1001)]
        before = counts(db)["subject_memberships"]

        result = module1.ingest_roster(roster_batch(rows))

        assert (result["processed"], result["created_identities"]) == (1000, 1000)
        assert counts(db)["subject_memberships"] == before + 1000


    @red("p1")
    def test_ingest_reingest_creates_new_batch_id(self, db, module1):
        """Test ID: T-ROS-I-05 (nuevo). Cláusula: Nota de reingesta (sin idempotencia por contenido; cada
        solicitud válida es un intento nuevo con batch_id nuevo). AD-02 (heredado). Conteos efectivos:
        sin cambio no cuenta en updated_memberships.

        Assertions: segunda ingesta idéntica -> batch_id distinto, created_identities 0, updated_memberships 0,
        +1 fila en roster_batches (no se deduplica).
        """
        ensure_base(db)
        batch = roster_batch([roster_row(1), roster_row(2), roster_row(3)])
        first = module1.ingest_roster(batch)
        batches_before = counts(db)["roster_batches"]

        second = module1.ingest_roster(batch)

        assert second["batch_id"] != first["batch_id"]
        assert (second["created_identities"], second["updated_memberships"]) == (0, 0)
        assert counts(db)["roster_batches"] == batches_before + 1


    @red("p0")
    def test_roster_role_smuggling_422_field_assigned_role(self, db, module1):
        """Test ID: T-ROS-03b (nuevo). Cláusula: I2 + H-20 + ADVF-14 (Ronda 6): rol distinto sobre membresía
        previa -> 422 ROSTER_VALIDATION_FAILED sobre el campo assigned_role (observed/expected, sin código nuevo).
        AD-02 (heredado).

        Assertions: manifiesto con row_number 1, field 'assigned_role', observed 'ta', expected 'student';
        processed 0; rol de la membresía intacto; sin filas nuevas en identidades, membresías, credenciales
        ni lotes; un único roster.rejected.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, identity, "CS-480", "student")
        tablas = ("identities", "subject_memberships", "subject_credentials", "roster_batches")
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(98432, role="ta")]))

        assert exc.value.code == "ROSTER_VALIDATION_FAILED"
        assert exc.value.http_status == 422
        assert exc.value.body["processed"] == 0
        assert any(
            e["row_number"] == 1
            and e["field"] == "assigned_role"
            and (e["observed"], e["expected"]) == ("ta", "student")
            for e in exc.value.body["errors"]
        )
        assert membership_row(db, identity, "CS-480")["role_id"] == "student"
        after = counts(db)
        for table in tablas:
            assert after[table] == before[table], table
        assert len(events(db, "roster.rejected")) == 1

    @red("p0")
    def test_ingest_institutional_id_case_distinct_identity(self, db, module1):
        """Test ID: T-ROS-G-09 (gap G-9; ADVF-21 / Q7, contracts §3 P3 y spine §Data & formats): institutional_id se
        compara case-sensitive exacto; `stu-98432` NO se fusiona con `STU-98432`. AD-02 (heredado), AD-09
        (spine-local). Historia E3-S4.

        Assertions: la fila en minúsculas crea una identidad nueva (processed 1, created_identities 1); la
        identidad STU-98432 y su membresía en CS-480 no cambian; existen dos identidades distintas.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "student")
        before = membership_row(db, "ID-STU-98432", "CS-480")
        lower_row = {
            "institutional_id": "stu-98432",
            "email": "stu98432-minuscula@universidad.edu",
            "full_name": "Estudiante minúscula",
            "assigned_role": "student",
        }

        result = module1.ingest_roster(roster_batch([lower_row]))

        assert (result["processed"], result["created_identities"]) == (1, 1)
        assert membership_row(db, "ID-STU-98432", "CS-480") == before
        distinct = db.execute(
            "SELECT COUNT(*) FROM identities WHERE institutional_id IN ('STU-98432', 'stu-98432')"
        ).fetchone()[0]
        assert distinct == 2


class TestExplainability:
    """Categoría X (explicabilidad AD-11): rule_ids citan la regla y los valores observados."""

    @red("p1", pytest.mark.explainability)
    def test_explain_roster_rejected_cites_ad02_observed_row(self, db, module1, explain_assert):
        """Test ID: T-ROS-08 (explicabilidad del rechazo 422). Cláusula: Q4 (cita AD-02, observed_invalid_row,
        regla aplicada). AD-11 (spine-local), AD-02 (heredado).

        Assertions: explanation de la fila 85 -> rule_ids[0] == ROSTER_VALIDATION_FAILED, AD-02 citado,
        observed_invalid_row == 85.
        """
        ensure_base(db)
        rows = [roster_row(n) for n in range(1, 121)]
        rows[84]["email"] = "stu00085@gmail.com"

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        explanation = exc.value.body["explanation"]
        explain_assert(exc.value.body)
        assert_code_first(explanation, "ROSTER_VALIDATION_FAILED")
        assert "AD-02" in explanation["rule_ids"]
        assert explanation["observed_invalid_row"] == 85


    @red("p1", pytest.mark.explainability)
    def test_explain_intra_batch_duplicate_cites_ad02(self, db, module1, explain_assert):
        """Test ID: T-ROS-08b (explicabilidad del duplicado intra-lote). Cláusula: Q4. AD-02 (heredado),
        AD-11 (spine-local).

        Assertions: rule_ids[0] == INTRA_BATCH_DUPLICATE_ID, AD-02 citado, observed_invalid_row informado.
        """
        ensure_base(db)
        rows = [roster_row(1), roster_row(2), roster_row(2)]

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch(rows))

        explain_assert(exc.value.body)
        assert_code_first(exc.value.body["explanation"], "INTRA_BATCH_DUPLICATE_ID")
        assert "AD-02" in exc.value.body["explanation"]["rule_ids"]
        assert exc.value.body["explanation"]["observed_invalid_row"] is not None


class TestRequestTimeInRejection:
    """Categoría I (reloj): request_now se captura una vez y se reutiliza en el evento de rechazo (H-16)."""

    @red("p0")
    def test_roster_rejected_occurred_at_reuses_single_request_now(self, db, module1, fake_clock, monkeypatch):
        """Test ID: T-ROS-H16 (nuevo). Cláusula: H-16 [ADOPTED 2026-10-13]: request_now se captura UNA vez al
        entrar al adapter; el evento roster.rejected reutiliza ese mismo valor como occurredAt. AD-13 (spine-local).
        Historia: E3-S2.

        Assertions: durante el 422 INTRA_BATCH_DUPLICATE_ID, Clock.now() se lee exactamente una vez; el único
        evento roster.rejected lleva como timestamp esa lectura; cero escrituras en las tablas de rechazo.
        """
        ensure_base(db)
        reads: list[str] = []
        original_now = fake_clock.now

        def counting_now() -> str:
            value = original_now()
            reads.append(value)
            fake_clock.advance(1)  # cada lectura posterior tendría otro instante
            return value

        monkeypatch.setattr(fake_clock, "now", counting_now)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.ingest_roster(roster_batch([roster_row(1), roster_row(1)]))

        assert exc.value.code == "INTRA_BATCH_DUPLICATE_ID"
        assert len(reads) == 1, f"request_now debe capturarse una vez; lecturas: {reads}"
        assert_no_writes(before, counts(db))
        rejected = events(db, "roster.rejected")
        assert len(rejected) == 1
        assert rejected[0]["timestamp"] == reads[0]


class TestTermAndPathTransport:
    """Categoría P (transporte HTTP de ingesta): term por query y segmento de curso en el path (AD-09; H-18)."""

    @red("p1")
    def test_http_roster_term_percent_encoded_decoded_once(self, db):
        """Test ID: T-ROS-H18a (nuevo). Cláusula: H-18 [ADOPTED 2026-10-13]: el framework decodifica el
        percent-encoding una sola vez (RFC 3986) y luego compara exacto: `2026-%46ALL` equivale a `2026-FALL`;
        `2026-%2546ALL` decodifica a `2026-%46ALL`, que no es un term válido. AD-09 (spine-local). Historia: E3-S1.

        Assertions: el term codificado una vez crea el lote con roster_batches.term == '2026-FALL'; el
        doblemente codificado responde 400 MALFORMED_TERM sin escrituras. El term va solo por query (`term`
        no se repite en el cuerpo JSON).
        """
        ensure_base(db)
        body = {"subject_id": "CS-480", "rows": [roster_row(1)]}

        result = http_roster(ADMIN_TOKEN, "CS-480", "2026-%46ALL", body)

        assert "batch_id" in result
        assert query_dicts(db, "SELECT term FROM roster_batches") == [{"term": "2026-FALL"}]
        before = counts(db)
        with pytest.raises(Module1Error) as exc:
            http_roster(ADMIN_TOKEN, "CS-480", "2026-%2546ALL", {"subject_id": "CS-480", "rows": [roster_row(2)]})
        assert exc.value.code == "MALFORMED_TERM"
        assert exc.value.http_status == 400
        assert counts(db) == before

    @red("p1")
    @pytest.mark.parametrize("course", ["CS-999", "cs-480"], ids=["inexistente", "minusculas"])
    def test_http_roster_path_course_unknown_404_unknown_course(self, db, course):
        """Test ID: T-ROS-H18b (nuevo). Cláusula: H-18 [ADOPTED 2026-10-13]: el segmento {subject_id} del path se
        busca exacto, sin gramática extra; si no existe responde 404 UNKNOWN_COURSE. AD-09 (spine-local).
        Historia: E3-S1.

        Assertions: Module1Error UNKNOWN_COURSE con HTTP 404; conteos idénticos (cero escrituras).
        """
        ensure_base(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            http_roster(ADMIN_TOKEN, course, "2026-FALL", {"subject_id": course, "rows": [roster_row(1)]})

        assert exc.value.code == "UNKNOWN_COURSE"
        assert exc.value.http_status == 404
        assert counts(db) == before
