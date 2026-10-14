"""module1_revoke_contracts.test.py — Suite ATDD RED de revokeCourseAccess (contracts.md §2).

RED = xfail(raises=NotImplementedError, strict=True). Categorías: Q, P, I, X y R-006 (TestSecrets). Fuente: contracts.md §2 y §4. Helpers en atdd_support.py."""

from __future__ import annotations

import logging
import sqlite3

import pytest

from app.application.module1 import build_module1
from app.domain.errors import Module1Error
from fakes.fake_failing_ports import RaisingClock
from fakes.fake_id_generator import ThreadSafeIdGenerator
from fakes.fake_queue import FakeQueueReservation
from fakes.fake_token_verifier import ADMIN_TOKEN, STUDENT_TOKEN
from fakes.world import (
    CLOCK_START,
    STUDENT_ID,
    add_identity,
    add_membership,
    at_offset,
    counts,
    credential_rows,
    ensure_base,
    events,
    membership_row,
    seed_student_pair,
)
from atdd_support import (
    FIVE_MINUTES_ONE_SECOND_US,
    FIVE_MINUTES_US,
    SECRET_FULL,
    SECRET_RAW_RE,
    db_path,
    red,
    run_concurrently,
)


class TestHappyPath:
    """Categoría Q (happy path): el flujo feliz produce el estado y los eventos esperados."""

    @red("p0")
    def test_revoke_active_pair_returns_revoked(self, db, module1, fake_clock):
        """Test ID: T-REV-HP-01 (nuevo). Cláusula: Q1 (200 REVOKED con instante del Clock) y Q2
        (ACTIVE -> DROPPED con dropped_at fijado). AD-03 (heredado).

        Assertions: status REVOKED, revocation_propagated_at == Clock.now(), membresía DROPPED con dropped_at.
        """
        identity = seed_student_pair(db)

        result = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro voluntario del curso", CLOCK_START)

        assert result["status"] == "REVOKED"
        assert (result["student_id"], result["subject_id"]) == (STUDENT_ID, "CS101")
        assert result["revocation_propagated_at"] == fake_clock.now()
        membership = membership_row(db, identity, "CS101")
        assert membership["status"] == "DROPPED"
        assert membership["dropped_at"] == result["revocation_propagated_at"]


    @red("p0")
    def test_revoke_emits_one_membership_revoked_event(self, db, module1):
        """Test ID: T-REV-HP-02 (nuevo). Cláusula: Q3 (exactamente un evento de baja). AD-03 (heredado),
        AD-04 (heredado). Mapeo ledger R3-03: membership.revoked -> DENY / SUBJECT_ENROLLMENT_DROPPED.

        Assertions: +1 evento membership.revoked con decision DENY y reason_code SUBJECT_ENROLLMENT_DROPPED;
        ningún evento roster.* añadido.
        """
        seed_student_pair(db)
        before = counts(db)["audit_events"]

        module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro voluntario del curso", CLOCK_START)

        assert counts(db)["audit_events"] == before + 1
        revoked = events(db, "membership.revoked")
        assert len(revoked) == 1
        assert (revoked[0]["decision"], revoked[0]["reason_code"]) == ("DENY", "SUBJECT_ENROLLMENT_DROPPED")
        assert events(db, "roster.ingested") == []


    @red("p0")
    def test_revoke_all_credentials(self, db, module1):
        """Test ID: T-REV-01 / test_revoke_all_credentials. Cláusula: Q2 e I2 (tras el commit ninguna credencial
        del par permanece autorizable). AD-03 (heredado), AD-12 (spine-local): UPDATE masivo en la misma tx.

        Assertions: las 2 credenciales del par CS101 pasan a REVOKED con revoked_at; ninguna ACTIVE.
        """
        identity = seed_student_pair(db)

        module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        creds = credential_rows(db, identity, "CS101")
        assert len(creds) == 2
        assert all(c["status"] == "REVOKED" and c["revoked_at"] is not None for c in creds)
        assert sum(1 for c in creds if c["status"] == "ACTIVE") == 0


class TestPreconditions:
    """Categoría P (precondiciones): rechazo tipado con HTTP exacto, cero mutación y cero eventos."""

    @red("p1")
    def test_revoke_never_enrolled_pair_404_membership_not_found(self, db, module1, fake_queue):
        """Test ID: T-REV-04 (nombre del catálogo: MEMBERSHIP_NOT_FOUND). Cláusula: P2 -> 404.
        Q-fail: cero filas mutadas, cero eventos.

        Assertions: MEMBERSHIP_NOT_FOUND 404; conteos idénticos; cola sin publicar.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-00001", "STU-00001")
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access("STU-00001", "CS101", "Baja sin membresía previa", CLOCK_START)

        assert exc.value.code == "MEMBERSHIP_NOT_FOUND"
        assert exc.value.http_status == 404
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p1")
    def test_revoke_suspended_membership_409_invalid_transition(self, db, module1, fake_queue):
        """Test ID: T-REV-04b (variante de INVALID_TRANSITION). Cláusula: P2 -> 409 si SUSPENDED.
        Q-fail: cero mutación, cero eventos; la membresía permanece SUSPENDED.

        Assertions: INVALID_TRANSITION 409; estado de membresía SUSPENDED intacto; conteos idénticos.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-SUSP", "STU-SUSP")
        add_membership(db, "ID-STU-SUSP", "CS101", "student", status="SUSPENDED")
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access("STU-SUSP", "CS101", "Baja de membresía suspendida", CLOCK_START)

        assert exc.value.code == "INVALID_TRANSITION"
        assert exc.value.http_status == 409
        assert membership_row(db, "ID-STU-SUSP", "CS101")["status"] == "SUSPENDED"
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p1")
    def test_revoke_malformed_drop_reason_400_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-REV-03 (drop_reason: 1-280 puntos Unicode; solo blancos -> inválido). Cláusula: P3 ->
        MALFORMED_DROP_REASON 400. H-19a: blancos por str.isspace(). Q-fail: cero mutación, cero eventos.

        Assertions: código 400; membresía y credenciales ACTIVE intactas; conteos idénticos.
        """
        identity = seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", " \t\n ", CLOCK_START)

        assert exc.value.code == "MALFORMED_DROP_REASON"
        assert exc.value.http_status == 400
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert {c["status"] for c in credential_rows(db, identity, "CS101")} == {"ACTIVE"}
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_revoke_non_admin_actor_403_no_mutation(
        self,
        db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-REV-P-05 (nuevo). Cláusula: P0 / Q1 (ADVF-01) -> 403 ADMIN_ROLE_REQUIRED después del 401 y
        antes de la sintaxis; sin mutación ni evento. ErrorBody sin ExplanationDTO (R6b-03). AD-09 (spine-local),
        AD-02 (heredado).

        Assertions: actor estudiante (token de fixture) -> 403 ADMIN_ROLE_REQUIRED; membresía y credenciales
        ACTIVE; conteos idénticos; cola sin publicar; body sin 'explanation'.
        """
        identity = seed_student_pair(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, STUDENT_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.revoke_course_access(STUDENT_ID, "CS101", "Baja solicitada por estudiante", CLOCK_START)

        assert exc.value.code == "ADMIN_ROLE_REQUIRED"
        assert exc.value.http_status == 403
        assert "explanation" not in exc.value.body
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert {c["status"] for c in credential_rows(db, identity, "CS101")} == {"ACTIVE"}
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_revoke_future_timestamp_400_no_mutation(self, db, module1, fake_clock, fake_queue):
        """Test ID: T-REV-P-06 (nuevo). Cláusula: P4 / Q6 (ECF-13): timestamp > request_now + 300 s ->
        400 MALFORMED_DROP_TIMESTAMP, probado con fake_clock. AD-08 (spine-local).

        Assertions: 400 con un adelanto de 301 s sobre request_now; membresía ACTIVE; conteos idénticos;
        cola sin publicar.
        """
        identity = seed_student_pair(db)
        before = counts(db)
        adelantado = at_offset(FIVE_MINUTES_ONE_SECOND_US)
        assert adelantado > fake_clock.now()  # precondición: el timestamp es futuro respecto al reloj inyectado

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro con fecha futura", adelantado)

        assert exc.value.code == "MALFORMED_DROP_TIMESTAMP"
        assert exc.value.http_status == 400
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert counts(db) == before
        assert fake_queue.published == []

    @red("p0")
    def test_revoke_auth_token_invalid_401_before_body_validation(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-REV-11 (R8-04, AD-09). Cláusula: contracts §0 orden único paso 1: bearer ausente o
        inválido -> 401 AUTH_TOKEN_INVALID antes de validar el body (drop_reason vacío y timestamp ausente
        darían 400). AD-09 (spine-local).

        RED: Module1Service es stub puro; la verificación del bearer (TokenVerifierPort) es lógica GREEN pendiente.
        Corrección: antes pasaba en verde porque el stub delegaba en el fake configurado por el test (tautología).

        Assertions: 401 AUTH_TOKEN_INVALID; cero mutación de membresías/credenciales; cero eventos.
        """
        seed_student_pair(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, "tok-invalido"
        )

        with pytest.raises(Module1Error) as exc:
            service.revoke_course_access(STUDENT_ID, "CS101", "", None)

        assert exc.value.code == "AUTH_TOKEN_INVALID"
        assert exc.value.http_status == 401
        assert counts(db) == before
        assert events(db) == []

    @red("p0")
    def test_revoke_student_token_403_admin_before_drop_reason_syntax(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-REV-09 (E2-S4, ADVF-01). Cláusula: contracts §0 paso 1bis: actor sin rol admin ->
        403 ADMIN_ROLE_REQUIRED antes de la sintaxis (drop_reason vacío daría 400 si la sintaxis fuera primero).
        AD-09 (spine-local).

        Assertions: 403 ADMIN_ROLE_REQUIRED (no 400 MALFORMED_DROP_REASON); cero mutación; cero eventos.
        """
        seed_student_pair(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, STUDENT_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.revoke_course_access(STUDENT_ID, "CS101", "", CLOCK_START)

        assert exc.value.code == "ADMIN_ROLE_REQUIRED"
        assert exc.value.http_status == 403
        assert counts(db) == before
        assert events(db) == []

    @red("p1")
    @pytest.mark.parametrize(
        "reason", ["Baja\x00", "Baja\nsegunda linea", "Baja\x7f"], ids=["nul", "newline", "del"]
    )
    def test_revoke_drop_reason_control_char_400_no_mutation(self, db, module1, reason):
        """Test ID: T-REV-10 (ECF-12, E2-S5). Cláusula: contracts §2 P3: caracteres de control (Unicode Cc)
        en drop_reason -> MALFORMED_DROP_REASON 400. AD-06 (heredado) no aplica: no hay secreto.

        Parametrizado: NUL, salto de línea y DEL (U+007F). Assertions: 400 MALFORMED_DROP_REASON; cero
        mutación de membresías y credenciales; cero eventos.
        """
        seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", reason, CLOCK_START)

        assert exc.value.code == "MALFORMED_DROP_REASON"
        assert exc.value.http_status == 400
        assert counts(db) == before
        assert events(db) == []

    @red("p1")
    def test_revoke_drop_reason_281_chars_400_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-REV-G-10 (gap G-10; E2-S5). Cláusula: P3 — drop_reason de 1-280 puntos Unicode; 281 puntos
        -> MALFORMED_DROP_REASON 400 (límite superior). AD-03 (heredado). Historia E2-S5.

        Assertions: 400 MALFORMED_DROP_REASON; membresía ACTIVE; conteos idénticos; cola sin publicar.
        """
        identity = seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", "a" * 281, CLOCK_START)

        assert exc.value.code == "MALFORMED_DROP_REASON"
        assert exc.value.http_status == 400
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert counts(db) == before
        assert fake_queue.published == []

    @red("p1")
    def test_revoke_empty_reason_and_missing_timestamp_rule_ids_order(self, db, module1):
        """Test ID: T-REV-G-11 (gap G-11; R3-02 / H-23). Cláusula: P3 + P4 con dos errores de sintaxis simultáneos:
        MALFORMED_DROP_REASON va primero y MALFORMED_DROP_TIMESTAMP aparece en rule_ids. AD-03 (heredado).
        Historia E2-S5.

        Assertions: 400; rule_ids[0] == MALFORMED_DROP_REASON y MALFORMED_DROP_TIMESTAMP presente; cero mutación.
        """
        identity = seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", "", None)

        assert exc.value.http_status == 400
        assert exc.value.body["rule_ids"][0] == "MALFORMED_DROP_REASON"
        assert "MALFORMED_DROP_TIMESTAMP" in exc.value.body["rule_ids"]
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert counts(db) == before

    @red("p1")
    @pytest.mark.parametrize(
        "timestamp",
        [
            "2026-09-23T15:04:05+02:00",
            "2026-09-23T15:04:05-00:00",
            "2026-09-23T15:04:05.1234567Z",
            "2026-09-23",
            "2026-09-23T15:04:60Z",
            "2026-02-30T10:00:00Z",
        ],
        ids=["offset-no-utc", "offset-menos-cero", "fraccion-7-digitos", "sin-hora", "segundo-60", "fecha-inexistente"],
    )
    def test_revoke_timestamp_outside_rfc3339_grammar_400(self, db, module1, timestamp):
        """Test ID: T-REV-G-12 (gap G-12; G9-01 / R4-01). Cláusula: P4 — gramática RFC 3339 UTC estricta: offset
        distinto de Z/+00:00, -00:00, más de 6 decimales, fecha sin hora, segundo 60 o fecha inexistente ->
        MALFORMED_DROP_TIMESTAMP 400. AD-08 (spine-local). Historia E2-S5.

        Assertions: 400 MALFORMED_DROP_TIMESTAMP; membresía ACTIVE; conteos idénticos.
        """
        identity = seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro con timestamp inválido", timestamp)

        assert exc.value.code == "MALFORMED_DROP_TIMESTAMP"
        assert exc.value.http_status == 400
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert counts(db) == before


class TestInvariants:
    """Categoría I (invariantes y fronteras): atomicidad, aislamiento, límites y reglas de precedencia."""

    @red("p0")
    def test_revoke_preserves_other_course(self, db, module1):
        """Test ID: T-REV-01b / test_revoke_preserves_other_course (R10: desambiguado; T-REV-01 queda solo para
        test_revoke_all_credentials). Cláusula: I1 (membresías del mismo usuario
        en otros cursos intactas). AD-03 (heredado): predicado WHERE identity_id AND subject_id.

        Assertions: CS-480 sigue ACTIVE sin dropped_at y su credencial sigue ACTIVE.
        """
        identity = seed_student_pair(db)

        module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        other = membership_row(db, identity, "CS-480")
        assert (other["status"], other["dropped_at"]) == ("ACTIVE", None)
        assert {c["status"] for c in credential_rows(db, identity, "CS-480")} == {"ACTIVE"}


    @red("p0")
    def test_revoke_store_failure_closed(self, db, module1, fake_queue):
        """Test ID: T-REV-06 (nuevo). Cláusula: I3 (fallo del store -> fail-closed AUTH_INTERNAL_POLICY_UNAVAILABLE
        503 reintentable, sin medio commit). AD-03 (heredado) + PRD §7.3.

        Setup: cola llena (set_capacity(0)). Assertions: 503, cero mutación de membresía y credenciales,
        cero eventos publicados, conteos idénticos.
        """
        identity = seed_student_pair(db)
        fake_queue.set_capacity(0)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", "Baja con cola llena", CLOCK_START)

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert {c["status"] for c in credential_rows(db, identity, "CS101")} == {"ACTIVE"}
        assert counts(db) == before
        assert fake_queue.published == []

    @red("p0")
    def test_revoke_clock_failure_503_fail_closed_no_mutation(
        self, db, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-REV-12 (R12-B01, hallazgo SEC B-01). Cláusula: contracts §2 Q-fail [ADOPTED 2026-10-14,
        estudiante]: si Clock.now() lanza durante revokeCourseAccess antes del commit, la respuesta es
        503 AUTH_INTERNAL_POLICY_UNAVAILABLE fail-closed (nunca 200 REVOKED ni 200 ALREADY_REVOKED): la membresía
        sigue ACTIVE, las credenciales no cambian y no hay eventos. AD-03 (heredado), AD-12 (spine-local).
        Historia: E2-S3.

        Setup: seed_student_pair; servicio compuesto con RaisingClock (test/fakes/fake_failing_ports.py).
        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; membresía ACTIVE; credenciales sin cambio; conteos
        idénticos; cero eventos.
        """
        identity = seed_student_pair(db)
        creds_before = credential_rows(db, identity, "CS101")
        before = counts(db)
        service = build_module1(
            db, RaisingClock(), fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.revoke_course_access(STUDENT_ID, "CS101", "Baja con reloj caído", CLOCK_START)

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert credential_rows(db, identity, "CS101") == creds_before
        assert counts(db) == before
        assert events(db) == []

    @red("p0")
    def test_revoke_replay_idempotent(self, db, module1, fake_clock):
        """Test ID: T-REV-02 / test_revoke_replay_idempotent. Cláusula: I (repetición): DROPPED + petición válida
        -> 200 ALREADY_REVOKED con el timestamp original, sin mutación ni evento. AD-03 (heredado).

        Assertions: segunda llamada ALREADY_REVOKED con revocation_propagated_at == el primero (aunque el reloj
        avance); dropped_at no cambia; sigue habiendo un único evento membership.revoked.
        """
        identity = seed_student_pair(db)
        first = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)
        dropped_at = membership_row(db, identity, "CS101")["dropped_at"]
        fake_clock.advance(120)

        second = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        assert second["status"] == "ALREADY_REVOKED"
        assert second["revocation_propagated_at"] == first["revocation_propagated_at"]
        assert membership_row(db, identity, "CS101")["dropped_at"] == dropped_at
        assert len(events(db, "membership.revoked")) == 1


    @red("p1")
    @pytest.mark.parametrize(
        "reason",
        ["  \t ", "Retiro\x00del curso"],
        ids=["solo-espacios", "control-nul"],
    )
    def test_revoke_dropped_invalid_reason_400_before_replay(self, db, module1, reason):
        """Test ID: T-REV-F01 (nuevo). Cláusula: F-01 [ADOPTED 2026-10-13]: sobre una membresía DROPPED, un
        drop_reason inválido responde 400 MALFORMED_DROP_REASON (la sintaxis P3 se valida antes que el replay);
        solo una petición válida recibe 200 ALREADY_REVOKED. H-19a (blancos por str.isspace()). AD-03 (heredado),
        AD-09 (spine-local). Historia: E2-S5.

        Assertions: Module1Error MALFORMED_DROP_REASON con HTTP 400; la membresía sigue DROPPED con dropped_at
        intacto; conteos idénticos; un único evento membership.revoked; control: el mismo replay con motivo
        válido responde ALREADY_REVOKED.
        """
        identity = seed_student_pair(db)
        module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)
        dropped_at = membership_row(db, identity, "CS101")["dropped_at"]
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.revoke_course_access(STUDENT_ID, "CS101", reason, CLOCK_START)

        assert exc.value.code == "MALFORMED_DROP_REASON"
        assert exc.value.http_status == 400
        assert membership_row(db, identity, "CS101")["dropped_at"] == dropped_at
        assert counts(db) == before
        assert len(events(db, "membership.revoked")) == 1
        valid = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)
        assert valid["status"] == "ALREADY_REVOKED"

    @red("p0")
    def test_revoke_concurrent_double_drop_single_mutation(
        self, db, fake_clock, fake_token_verifier
    ):
        """Test ID: T-REV-07 (nuevo). Cláusula: Concurrencia (dos bajas simultáneas del mismo par bajo
        BEGIN IMMEDIATE: una confirma, la otra observa DROPPED -> ALREADY_REVOKED). AD-03 (heredado),
        AD-12 (spine-local). Riesgo 1 de test-review: una conexión SQLite POR HILO sobre el archivo WAL
        temporal (nunca compartida entre hilos); barrera de inicio para simultaneidad real.

        Assertions: un resultado REVOKED y uno ALREADY_REVOKED; exactamente un evento membership.revoked.
        Un error de hilo se re-lanza en el hilo principal (no se traga).
        """
        seed_student_pair(db)
        path = db_path(db)
        ids = ThreadSafeIdGenerator()
        fake_queue = FakeQueueReservation()

        def drop_worker(barrier):
            conn = sqlite3.connect(path, timeout=5)
            try:
                service = build_module1(conn, fake_clock, ids, fake_queue, fake_token_verifier, ADMIN_TOKEN)
                barrier.wait(timeout=5)
                return service.revoke_course_access(STUDENT_ID, "CS101", "Baja concurrente", CLOCK_START)
            finally:
                conn.close()

        outcomes = run_concurrently([drop_worker, drop_worker])

        assert sorted(o["status"] for o in outcomes) == ["ALREADY_REVOKED", "REVOKED"]
        assert len(events(db, "membership.revoked")) == 1


    @red("p1")
    def test_revoke_timestamp_at_tolerance_boundary_accepted(self, db, module1):
        """Test ID: T-REV-I-06 (nuevo). Cláusula: Q6 frontera: timestamp == request_now + 300 s se acepta
        (la regla de rechazo es estrictamente '> 300 s'). AD-08 (spine-local).

        Assertions: 200 REVOKED; membresía DROPPED con dropped_at del Clock.
        """
        identity = seed_student_pair(db)

        result = module1.revoke_course_access(
            STUDENT_ID, "CS101", "Retiro en el límite de tolerancia", at_offset(FIVE_MINUTES_US)
        )

        assert result["status"] == "REVOKED"
        assert membership_row(db, identity, "CS101")["status"] == "DROPPED"

    @red("p0")
    def test_revoke_busy_timeout_exhausted_503_no_partial_commit(self, db, module1):
        """Test ID: T-REV-G-02 (gap G-2; E2-S3). Cláusula: I3 + contracts §2 Q2: si SQLITE_BUSY agota el
        busy_timeout (contención real de escritor), 503 AUTH_INTERNAL_POLICY_UNAVAILABLE fail-closed y SIN commit
        parcial. AD-12 (spine-local), AD-03 (heredado). Historia E2-S3.

        Setup: otra conexión mantiene BEGIN IMMEDIATE sobre el mismo archivo SQLite; busy_timeout de la conexión
        de prueba reducido a 50 ms para no esperar 5 s.
        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; membresía y credenciales ACTIVE; conteos idénticos.
        """
        identity = seed_student_pair(db)
        before = counts(db)
        db.execute("PRAGMA busy_timeout = 50")
        blocker = sqlite3.connect(db_path(db), isolation_level=None)
        try:
            blocker.execute("BEGIN IMMEDIATE")
            with pytest.raises(Module1Error) as exc:
                module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro con escritor bloqueado", CLOCK_START)
            assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
            assert exc.value.http_status == 503
        finally:
            if blocker.in_transaction:
                blocker.execute("ROLLBACK")
            blocker.close()
        assert membership_row(db, identity, "CS101")["status"] == "ACTIVE"
        assert {c["status"] for c in credential_rows(db, identity, "CS101")} == {"ACTIVE"}
        assert counts(db) == before


class TestSecrets:
    """R-006 / AD-06: ningún secreto `uai_live_` completo sale en respuesta, log o ledger."""

    @red("p0")
    def test_no_secret_leak_in_drop_reason(self, db, module1, fake_queue):
        """Test ID: T-SEC-01 (nombre nominal test_no_secret_leak). Cláusula: I3 (ningún secreto en claro sale
        en la respuesta, el log ni el ledger). AD-06 (heredado) gana sobre 'original intacto' (H-19b).
        Máscara uai_live_<4>••••••••••••<4>; regex de build uai_live_[a-zA-Z0-9]{32}.

        Assertions: el secreto en claro no aparece en la respuesta ni en ningún payload de auditoría.
        """
        identity = seed_student_pair(db)
        secret_body = "8f3aQ9xK7mPz2LwT5nRb0VcY4sHd6GjE"
        assert len(secret_body) == 32
        raw = f"uai_live_{secret_body}"
        reason = f"Baja por solicitud; llave filtrada {raw} revocada"

        result = module1.revoke_course_access(STUDENT_ID, "CS101", reason, CLOCK_START)

        assert raw not in repr(result)
        payloads = [e["payload"] for e in events(db)]
        assert payloads, "debe existir al menos el evento de baja"
        assert all(raw not in p and secret_body not in p for p in payloads)
        assert membership_row(db, identity, "CS101")["status"] == "DROPPED"

    @red("p0")
    def test_ad06_secret_in_drop_reason_rejection_and_revocation_never_in_clear(self, db, module1, caplog):
        """Test ID: T-SEC-REV-01 (R-006, AD-06 / NFR-SEC-04). Cláusula: AD-06 (heredado): ninguna clave
        uai_live_ completa en logs, respuesta ni filas de audit_ledger / audit_events. Regex de build:
        uai_live_[A-Za-z0-9]{8,} ausente.

        Dos ejecuciones: (1) rechazo: drop_reason con la clave completa y U+0007 (Cc) -> 400 MALFORMED_DROP_REASON;
        (2) revocación válida con la clave completa en el motivo -> REVOKED. La forma enmascarada
        uai_live_<4>••••••••••••<4> es la única permitida en logs y respuestas.

        Assertions: en la excepción de (1), en la respuesta de (2), en caplog y en todas las filas del ledger y
        de los eventos no aparece la clave completa.
        """
        seed_student_pair(db)

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(Module1Error) as exc:
                module1.revoke_course_access(STUDENT_ID, "CS101", SECRET_FULL + "\x07", CLOCK_START)
            assert exc.value.code == "MALFORMED_DROP_REASON"
            assert not SECRET_RAW_RE.search(str(exc.value.body))

            revoked = module1.revoke_course_access(STUDENT_ID, "CS101", "Baja " + SECRET_FULL, CLOCK_START)

        assert revoked["status"] == "REVOKED"
        ledger_text = " ".join(str(row) for row in db.execute("SELECT * FROM audit_ledger").fetchall())
        events_text = " ".join(str(row) for row in db.execute("SELECT payload FROM audit_events").fetchall())
        blob = " ".join([str(revoked), caplog.text, ledger_text, events_text])
        assert not SECRET_RAW_RE.search(blob), "clave uai_live_ completa en claro"
        assert SECRET_FULL not in blob


class TestExplainability:
    """Categoría X (explicabilidad AD-11): rule_ids citan la regla y los valores observados."""

    @red("p1", pytest.mark.explainability)
    def test_explain_already_revoked_cites_ad03(self, db, module1, explain_assert):
        """Test ID: T-REV-08 (explicabilidad de ALREADY_REVOKED). Cláusula: Q4 + ALREADY_REVOKED con
        ExplanationDTO que cita AD-03. AD-11 (spine-local).

        Assertions: explanation cita AD-03, observed_prior_status == 'DROPPED', pasa explain_assert.
        """
        seed_student_pair(db)
        module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        replay = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        explain_assert(replay)
        assert "AD-03" in replay["explanation"]["rule_ids"]
        assert replay["explanation"]["observed_prior_status"] == "DROPPED"


    @red("p1", pytest.mark.explainability)
    def test_explain_first_revoke_reports_credentials_revoked(self, db, module1, explain_assert):
        """Test ID: T-REV-08b (explicabilidad de la primera baja). Cláusula: Q4 (observed_credentials_revoked).
        AD-03 (heredado), AD-11 (spine-local).

        Assertions: cita AD-03, observed_prior_status == 'ACTIVE', observed_credentials_revoked == 2.
        """
        seed_student_pair(db)

        result = module1.revoke_course_access(STUDENT_ID, "CS101", "Retiro del curso CS101", CLOCK_START)

        explain_assert(result)
        assert "AD-03" in result["explanation"]["rule_ids"]
        assert result["explanation"]["observed_prior_status"] == "ACTIVE"
        assert result["explanation"]["observed_credentials_revoked"] == 2
