"""module1_contracts.test.py — Suite ATDD RED transversal del Módulo 1 (Solu-2).

Contiene EDGE-01 (Mandatory Edge Case), explicabilidad transversal (AD-11) y la cadena del ledger (AD-04). Las operaciones viven en module1_resolve/revoke/ingest_contracts.test.py. Fuente de verdad: planning/detailed-design/contracts.md."""

from __future__ import annotations

import hashlib
import sqlite3
import struct

import pytest
import yaml
from urllib.parse import urlparse

from app.adapters.http import declared_routes, parse_csv_rfc4180, parse_roster_body
from app.application.module1 import build_module1
from app.domain.errors import Module1Error
from app.domain.pagination import clamp_page_size
from app.domain.scheduler import sweep_expired
from fakes.fake_id_generator import ThreadSafeIdGenerator
from fakes.fake_token_verifier import ADMIN_TOKEN
from fakes.world import (
    CLOCK_START,
    STUDENT_ID,
    add_identity,
    add_membership,
    add_ticket,
    at_offset,
    ensure_base,
    events,
    seed_student_pair,
    ticket_status,
)
from atdd_support import (
    ACTION,
    ARN_8B_CS101,
    ARN_8B_CS480,
    ARN_TOY_CS101,
    GENESIS,
    ONE_HOUR_US,
    ONE_MICROSECOND,
    OPENAPI_PATH,
    TEN_MINUTES_US,
    assert_cites_ad,
    assert_code_first,
    db_path,
    decision_of,
    multipart_body,
    red,
    run_concurrently,
)


class TestEdge01:
    """EDGE-01 (Mandatory Edge Case): Student en CS101 y TA en CS-480 se resuelven por contexto."""

    @red("p0", pytest.mark.edge_case)
    def test_edge01_context_isolation(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-01 (nombre nominal test_edge01_context_isolation). Mandatory Edge Case EDGE-01:
        Student en CS101 (0 GPU) y TA en CS-480 (prioridad alta) -> cada contexto se resuelve independiente.
        Cláusula: I1 (otro curso nunca altera el veredicto), I4 (sin cuota GPU ni prioridad).
        AD-01 (heredado), AD-10 (spine-local). Matriz v0: CS101/student sin fila 8B -> DENY;
        CS-480/ta -> ALLOW por la fila v0 (CS-480, ta, inference, gpu_24gb_workstation, true) [Ronda 6 Q5].

        Assertions sobre estado final: rol efectivo distinto por contexto, ninguna mezcla,
        respuesta sin campos de cuota/prioridad, dos eventos authorization.decided.
        """
        ta = edge_case_seeds["institutional_id"]
        before_events = len(events(db))

        cs101 = module1.resolve_effective_permissions(ta, "CS101", ARN_8B_CS101, ACTION)
        cs480 = module1.resolve_effective_permissions(ta, "CS-480", ARN_8B_CS480, ACTION)

        assert cs101["effective_role"] == "student"
        assert cs480["effective_role"] == "ta"
        assert cs101["effective_role"] != cs480["effective_role"]
        assert cs101["decision"] == "DENY"
        assert_code_first(cs101["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")
        assert cs101["explanation"]["observed_role"] == "student"
        assert cs480["decision"] == "ALLOW"
        assert_cites_ad(cs480["explanation"])
        assert cs480["explanation"]["observed_role"] == "ta"
        for result in (cs101, cs480):
            assert set(result) == {"decision", "effective_role", "explanation"}
        assert len(events(db, "authorization.decided")) == 2
        assert len(events(db)) == before_events + 2
        assert fake_queue.published  # cada decisión pasa por la cola de auditoría


    @red("p0", pytest.mark.edge_case)
    def test_edge01_student_cs101_gpu_denied_cs480_allowed(self, db, module1, edge_case_seeds):
        """Test ID: T-RES-01b (variante EDGE-01 con Student en ambos cursos). Cláusula: Q1, I1.
        Matriz v0: CS101 student sin GPU -> DENY; CS-480 student inferencia 8B 24 GB -> ALLOW.

        Assertions: DENY de GPU en CS101 y ALLOW en CS-480 para la misma identidad; ninguna mezcla de roles.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")
        add_membership(db, "ID-STU-98432", "CS-480", "student")

        cs101 = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION)
        cs480 = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert (cs101["decision"], cs101["effective_role"]) == ("DENY", "student")
        assert_code_first(cs101["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")
        assert (cs480["decision"], cs480["effective_role"]) == ("ALLOW", "student")
        assert_cites_ad(cs480["explanation"])


    @red("p0", pytest.mark.edge_case)
    def test_edge01_escalation_in_cs480_does_not_alter_cs101(self, db, module1, edge_case_seeds):
        """Test ID: T-RES-01c (variante EDGE-01 con escalación). Cláusula: Q2 (rol escalado en otro curso
        no cambia el rol de este curso), I1. AD-01 (heredado), AD-10 (spine-local).

        Assertions: el veredicto de CS101 es idéntico antes y después de crear un ticket ACTIVE en CS-480,
        y el ticket en CS-480 sí cambia el rol efectivo de CS-480 (no hay fuga inversa).
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")
        add_membership(db, "ID-STU-98432", "CS-480", "student")
        before = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION)

        add_ticket(db, "ID-STU-98432", "CS-480", "instructor_privileged",
                   at_offset(-TEN_MINUTES_US), at_offset(ONE_HOUR_US))
        after = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION)
        escalated = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert after == before
        assert after["effective_role"] == "student"
        assert escalated["effective_role"] == "instructor_privileged"


class TestLedgerChain:
    """AD-04: cadena hash del ledger y ancla anti Tail-Truncation."""

    @red("p0")
    def test_ledger_chain_and_anchor(self, db, module1):
        """Test ID: T-LED-01 (nombre nominal test_ledger_chain_and_anchor). Cláusula: Q3 (hash encadenado).
        AD-04 (heredado) §5: SHA-256 sobre prev, timestamp, actor_id, subject_id, resource_arn, action,
        decision, reason_code; codec H-14/H-15: 0x01 + longitud 8B big-endian + UTF-8 por campo;
        génesis = semilla e3b0c442…b855 (GENESIS, R10-M2). Ancla singleton audit_ledger_metadata (id=1).

        Assertions: dos ALLOW consecutivos forman cadena (prev del segundo = hash del primero);
        cada record_hash coincide con el recálculo; head_record_hash y total_events_count anclados.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "student")

        module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)
        module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        rows = db.execute(
            "SELECT timestamp, actor_id, subject_id, resource_arn, action, decision, reason_code,"
            " prev_record_hash, record_hash FROM audit_ledger ORDER BY id ASC"
        ).fetchall()
        assert len(rows) == 2
        assert rows[0][7] == GENESIS
        assert rows[1][7] == rows[0][8]

        def frame(value: str) -> bytes:
            raw = value.encode("utf-8")
            return b"\x01" + struct.pack(">Q", len(raw)) + raw

        for row in rows:
            fields = [row[7], row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            expected = hashlib.sha256(b"".join(frame(f) for f in fields)).hexdigest()
            assert row[8] == expected
        head, total = db.execute(
            "SELECT head_record_hash, total_events_count FROM audit_ledger_metadata WHERE id = 1"
        ).fetchone()
        assert (head, total) == (rows[-1][8], 2)


class TestExplainability:
    """Categoría X (explicabilidad AD-11): rule_ids citan la regla y los valores observados."""

    @red("p1", pytest.mark.explainability)
    def test_explain_assert_rule_cited(self, db, module1, explain_assert, edge_case_seeds):
        """Test ID: T-RES-08 (nombre nominal test_explain_assert_rule_cited). Cláusula: Q4 (explicación).
        AD-11 (spine-local): rule_ids = TODAS las reglas violadas, primero == code; >=1 AD-n citado;
        observados solo de esas reglas (H-23 / R4-02).

        Assertions: DENY por matriz -> rule_ids[0] == UNAUTHORIZED_RESOURCE_CLASS, AD-n presente,
        observed_role = rol real del contexto.
        """
        result = module1.resolve_effective_permissions(
            edge_case_seeds["institutional_id"], "CS101", ARN_8B_CS101, ACTION
        )

        assert result["decision"] == "DENY"
        explain_assert(result)
        assert_code_first(result["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")
        assert_cites_ad(result["explanation"])
        assert result["explanation"]["observed_role"] == "student"


class TestConcurrency:
    """Concurrencia real: una conexión SQLite por hilo sobre archivo WAL, barrera de inicio."""
    @red("p0")
    def test_resolve_concurrent_with_revoke_never_allows_after_commit(
        self, db, fake_clock, fake_queue, fake_token_verifier
    ):
        """Test ID: T-CON-01 (R-003 con concurrencia real, Riesgo 3 / follow-up 3 de test-review). Cláusula:
        contracts §1 Concurrencia y §2: un resolve concurrente con revoke puede ver el estado previo o el
        revocado (snapshot WAL), pero un resolve posterior al commit NUNCA permite ALLOW. AD-03 (heredado),
        AD-12 (spine-local). Una conexión SQLite por hilo, barrera de inicio.

        Assertions: el resolve concurrente es ALLOW (antes del commit) o DENY SUBJECT_ENROLLMENT_DROPPED; la baja
        confirma REVOKED; un resolve secuencial posterior a ambos da DENY SUBJECT_ENROLLMENT_DROPPED; exactamente
        un membership.revoked.
        """
        seed_student_pair(db)
        path = db_path(db)
        ids = ThreadSafeIdGenerator()

        def revoke_worker(barrier):
            conn = sqlite3.connect(path, timeout=5)
            try:
                service = build_module1(conn, fake_clock, ids, fake_queue, fake_token_verifier, ADMIN_TOKEN)
                barrier.wait(timeout=5)
                return ("revoke", service.revoke_course_access(STUDENT_ID, "CS101", "Baja concurrente", CLOCK_START))
            finally:
                conn.close()

        def resolve_worker(barrier):
            conn = sqlite3.connect(path, timeout=5)
            try:
                service = build_module1(conn, fake_clock, ids, fake_queue, fake_token_verifier, ADMIN_TOKEN)
                barrier.wait(timeout=5)
                return ("resolve", decision_of(lambda: service.resolve_effective_permissions(
                    STUDENT_ID, "CS101", ARN_TOY_CS101, ACTION, CLOCK_START)))
            finally:
                conn.close()

        outcomes = dict(run_concurrently([revoke_worker, resolve_worker]))

        assert outcomes["revoke"]["status"] == "REVOKED"
        assert outcomes["resolve"] in {("ALLOW", None), ("DENY", "SUBJECT_ENROLLMENT_DROPPED")}
        service = build_module1(db, fake_clock, ids, fake_queue, fake_token_verifier, ADMIN_TOKEN)
        after = decision_of(lambda: service.resolve_effective_permissions(
            STUDENT_ID, "CS101", ARN_TOY_CS101, ACTION, at_offset(ONE_MICROSECOND)))
        assert after == ("DENY", "SUBJECT_ENROLLMENT_DROPPED")
        assert len(events(db, "membership.revoked")) == 1


class TestSchedulerSweep:
    """Barrido del scheduler (contracts §1 Tiempo, G6-02, R8-06): expiración, reconciliación y diferimiento."""
    @red("p1")
    def test_sweep_expires_active_ticket_once_with_one_event(self, db, fake_clock, fake_queue, sim_telemetry):
        """Test ID: T-SCH-01 (E4-S2 / G6-02). Cláusula: contracts §1 Tiempo: el barrido transiciona
        ACTIVE -> EXPIRED con un evento escalation.expired por transición efectiva; una segunda pasada no emite
        nada. Intervalo [granted_at, expires_at). AD-05 (heredado), AD-13 (spine-local).

        Assertions: 1 transición; ticket EXPIRED; exactamente un evento escalation.expired; segunda pasada 0.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-SCH-01", "STU-SCH-01")
        ticket = add_ticket(
            db, identity, "CS-480", "ta",
            granted_at=at_offset(-ONE_HOUR_US), expires_at=at_offset(-ONE_MICROSECOND),
        )

        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 1
        assert ticket_status(db, ticket) == "EXPIRED"
        assert [e["event_type"] for e in events(db)] == ["escalation.expired"]
        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 0
        assert len(events(db)) == 1

    @red("p1")
    def test_sweep_does_not_expire_ticket_not_yet_granted(self, db, fake_clock, fake_queue, sim_telemetry):
        """Test ID: T-SCH-02 (E4-S2, contracts §1 Tiempo). Cláusula: el scheduler actualiza solo tickets ACTIVE con
        granted_at <= now; si granted_at > now aún no expira. AD-13 (spine-local).

        Assertions: 0 transiciones; el ticket sigue ACTIVE; cero eventos.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-SCH-02", "STU-SCH-02")
        ticket = add_ticket(
            db, identity, "CS-480", "ta",
            granted_at=at_offset(ONE_HOUR_US), expires_at=at_offset(2 * ONE_HOUR_US),
        )

        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 0
        assert ticket_status(db, ticket) == "ACTIVE"
        assert events(db) == []

    @red("p1")
    def test_sweep_crash_recovery_reconciles_all_expired_tickets(self, db, fake_clock, fake_queue, sim_telemetry):
        """Test ID: T-SCH-03 (G6-02, reconciliación tras crash). Cláusula: al reiniciar, el barrido recorre todo
        ACTIVE con expires_at <= now y emite un evento por transición; idempotente por id de ticket. AD-05 (heredado).

        Setup: tres tickets vencidos de tres identidades distintas. Assertions: 3 transiciones en una pasada, 3
        eventos escalation.expired, todos EXPIRED; una segunda pasada devuelve 0.
        """
        ensure_base(db)
        tickets = []
        for n in range(1, 4):
            identity = add_identity(db, f"ID-SCH-1{n}", f"STU-SCH-1{n}")
            tickets.append(add_ticket(
                db, identity, "CS-480", "ta",
                granted_at=at_offset(-ONE_HOUR_US), expires_at=at_offset(-ONE_MICROSECOND),
            ))

        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 3
        assert [ticket_status(db, t) for t in tickets] == ["EXPIRED"] * 3
        assert [e["event_type"] for e in events(db)] == ["escalation.expired"] * 3
        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 0

    @red("p0")
    def test_sweep_defers_when_queue_full_and_emits_deferred_metric(self, db, fake_clock, fake_queue, sim_telemetry):
        """Test ID: T-SCH-04 (R8-06, TelemetryPort). Cláusula: si la cola no acepta el evento de expiración el barrido
        se DIFIERE (no se persiste la transición) y se emite scheduler_sweep_deferred_total por TelemetryPort
        (sim_telemetry). AD-12 (spine-local), AD-13 (spine-local).

        Assertions: 0 transiciones; el ticket sigue ACTIVE; cero eventos; sim_telemetry registra la métrica
        scheduler_sweep_deferred_total.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-SCH-04", "STU-SCH-04")
        ticket = add_ticket(
            db, identity, "CS-480", "ta",
            granted_at=at_offset(-ONE_HOUR_US), expires_at=at_offset(-ONE_MICROSECOND),
        )
        fake_queue.set_capacity(0)

        assert sweep_expired(db, fake_clock, fake_queue, sim_telemetry) == 0
        assert ticket_status(db, ticket) == "ACTIVE"
        assert events(db) == []
        assert [m["name"] for m in sim_telemetry.emitted] == ["scheduler_sweep_deferred_total"]


class TestHttpMapping:
    """Mapeo HTTP (AD-09) y parsing de cuerpo (BOM, RFC 4180, Content-Type, multipart) contra stubs de adapters/http.py."""
    @red("p1")
    def test_declared_routes_match_openapi_one_route_per_operation(self):
        """Test ID: T-HTTP-01 (AD-09 mapeo único operación -> ruta). Cláusula: contracts §0 y openapi.yaml: cada una de
        las tres operaciones tiene exactamente una ruta canónica; el adaptador HTTP declara las mismas rutas.
        AD-09 (spine-local).

        Assertions: operationId de las tres operaciones aparecen una vez en openapi.yaml; el conjunto
        (método, ruta con base /api/v1) del adaptador es igual al del contrato.
        """
        spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
        base = urlparse(spec["servers"][0]["url"]).path
        contract_routes = set()
        operation_ids = []
        for path, item in spec["paths"].items():
            for method, operation in item.items():
                if method in {"get", "post", "put", "patch", "delete"}:
                    operation_ids.append(operation["operationId"])
                    contract_routes.add((method.upper(), base + path))

        assert sorted(operation_ids) == sorted(
            ["resolveEffectivePermissions", "revokeCourseAccess", "ingestRoster"]
        )
        assert declared_routes() == contract_routes

    @red("p1")
    def test_roster_body_with_utf8_bom_400_malformed_batch(self):
        """Test ID: T-HTTP-02 (ECF-19). Cláusula: contracts §3 P2: codificación UTF-8 sin BOM; un BOM -> MALFORMED_BATCH
        400. AD-09 (spine-local).

        Assertions: Module1Error MALFORMED_BATCH con HTTP 400.
        """
        body = b"\xef\xbb\xbf" + b'{"subject_id":"CS-480","term":"2026-FALL","rows":[]}'
        with pytest.raises(Module1Error) as exc:
            parse_roster_body("application/json", body)
        assert exc.value.code == "MALFORMED_BATCH"
        assert exc.value.http_status == 400

    @red("p1")
    def test_csv_rfc4180_parses_quoted_comma_and_escaped_quote_in_four_fields(self):
        """Test ID: T-HTTP-03 (ECF-20, RFC 4180). Cláusula: contracts §3 P2: CSV con exactamente 4 campos por fila;
        comillas, comas y `""` escapadas se interpretan según RFC 4180. AD-09 (spine-local).

        Assertions: las filas parseadas (incluido el encabezado) son exactamente las esperadas.
        """
        text = (
            'institutional_id,email,full_name,assigned_role\r\n'
            'STU-1,a@universidad.edu,"Pérez, Ana ""La"" ",student\r\n'
        )
        assert parse_csv_rfc4180(text) == [
            ["institutional_id", "email", "full_name", "assigned_role"],
            ["STU-1", "a@universidad.edu", 'Pérez, Ana "La" ', "student"],
        ]

    @red("p1")
    def test_csv_row_with_five_fields_400_malformed_batch(self):
        """Test ID: T-HTTP-04 (ECF-20 / ECF-21). Cláusula: contracts §3 P2: fila con 5 campos -> MALFORMED_BATCH 400
        (columnas exactas institutional_id,email,full_name,assigned_role). AD-09 (spine-local).

        Assertions: Module1Error MALFORMED_BATCH con HTTP 400.
        """
        csv_bytes = (
            b"institutional_id,email,full_name,assigned_role\r\n"
            b"STU-1,a@universidad.edu,Ana,student,extra\r\n"
        )
        with pytest.raises(Module1Error) as exc:
            parse_roster_body("multipart/form-data; boundary=B", multipart_body([("file", csv_bytes)]))
        assert exc.value.code == "MALFORMED_BATCH"
        assert exc.value.http_status == 400

    @red("p1")
    def test_unsupported_content_type_400_malformed_batch(self):
        """Test ID: T-HTTP-05 (ECF-21). Cláusula: contracts §3 P2: Content-Type distinto de multipart/form-data (CSV)
        o application/json (JSON) -> MALFORMED_BATCH 400, sin código nuevo. AD-09 (spine-local).

        Assertions: Module1Error MALFORMED_BATCH con HTTP 400.
        """
        with pytest.raises(Module1Error) as exc:
            parse_roster_body("text/plain", b"institutional_id,email,full_name,assigned_role\n")
        assert exc.value.code == "MALFORMED_BATCH"
        assert exc.value.http_status == 400

    @red("p1")
    @pytest.mark.parametrize("parts", [0, 2], ids=["sin-partes", "dos-partes"])
    def test_multipart_must_have_exactly_one_file_part(self, parts):
        """Test ID: T-HTTP-06 (ECF-22). Cláusula: contracts §3 P2: multipart con una parte `file` exactamente; cualquier
        otra cantidad -> MALFORMED_BATCH 400. AD-09 (spine-local).

        Parametrizado: 0 partes y 2 partes. Assertions: Module1Error MALFORMED_BATCH con HTTP 400.
        """
        csv_bytes = b"institutional_id,email,full_name,assigned_role\r\nSTU-1,a@universidad.edu,Ana,student\r\n"
        body = multipart_body([("file", csv_bytes)] * parts)
        with pytest.raises(Module1Error) as exc:
            parse_roster_body("multipart/form-data; boundary=B", body)
        assert exc.value.code == "MALFORMED_BATCH"
        assert exc.value.http_status == 400


class TestTransversalAD:
    """Invariantes transversales (AD-07 paginación acotada)."""
    @red("p2")
    def test_ad07_clamp_page_size_zero_becomes_one(self):
        """Test ID: T-AD07-01 (R8-03, AD-07 heredado). Cláusula: contracts §4: page_size fuera de [1, 100] no es error,
        se fuerza al rango; 0 -> 1. Alcance: listados; la consulta forense (NFR-AUDIT-06) queda FUERA de las tres
        operaciones del Módulo 1 (owner B), sin test aquí.

        Assertions: clamp_page_size(0) == 1.
        """
        assert clamp_page_size(0) == 1

    @red("p2")
    def test_ad07_clamp_page_size_above_limit_becomes_100(self):
        """Test ID: T-AD07-02 (R8-03, AD-07 heredado). Cláusula: contracts §4: page_size > 100 se fuerza a 100.
        La consulta forense (NFR-AUDIT-06) queda FUERA de las tres operaciones del Módulo 1 (owner B).

        Assertions: clamp_page_size(101) == 100.
        """
        assert clamp_page_size(101) == 100
