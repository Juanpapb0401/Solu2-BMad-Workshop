"""module1_resolve_contracts.test.py — Suite ATDD RED de resolveEffectivePermissions (contracts.md §1).

Cada test llama al stub real (app/application/module1.py -> app/domain/resolution.py), que lanza NotImplementedError. RED = xfail(raises=NotImplementedError, strict=True). Categorías: Q, P, I, X. Fuente: contracts.md §1 y PRD §5.2. Helpers compartidos en atdd_support.py."""

from __future__ import annotations

import logging
import re

import pytest

from app.adapters.http import http_authorize
from app.application.module1 import build_module1
from app.domain.errors import Module1Error
from fakes.fake_failing_ports import RaisingClock
from fakes.fake_token_verifier import STUDENT_TOKEN
from fakes.world import (
    CLOCK_START,
    STUDENT_ID,
    add_identity,
    add_membership,
    add_ticket,
    at_offset,
    counts,
    ensure_base,
    events,
    membership_row,
    seed_student_pair,
    ticket_status,
)
from atdd_support import (
    ACTION,
    ARN_8B_CS101,
    ARN_8B_CS480,
    ARN_TOY_CS101,
    ONE_HOUR_US,
    ONE_MICROSECOND,
    SECRET_FULL,
    SECRET_MASKED,
    SECRET_RAW_RE,
    SEVENTY_MINUTES_US,
    TEN_MINUTES_US,
    assert_cites_ad,
    assert_code_first,
    decision_of,
    red,
)


class TestHappyPath:
    """Categoría Q (happy path): el flujo feliz produce el estado y los eventos esperados."""

    @red("p0")
    def test_resolve_allows_student_inference_cs480(self, db, module1, explain_assert):
        """Test ID: T-RES-HP-01 (nuevo). Cláusula: Q1 (ALLOW -> 200). AD-01 (heredado) + matriz v0 fila CS-480/student (prd.md:244).

        Assertions: decision ALLOW, effective_role 'student', respuesta solo con
        {decision, effective_role, explanation} (I4: sin cuota GPU ni prioridad), explanation citando AD-n.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "student")

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert result["decision"] == "ALLOW"
        assert result["effective_role"] == "student"
        assert set(result) == {"decision", "effective_role", "explanation"}
        explain_assert(result)
        assert_cites_ad(result["explanation"])


    @red("p0")
    def test_resolve_allow_appends_one_authorization_event(self, db, module1):
        """Test ID: T-RES-HP-02 (nuevo). Cláusula: Q3 (evento de auditoría con hash encadenado).
        AD-04 (heredado).

        Assertions: exactamente un evento authorization.decided ALLOW/SUCCESS; la membresía no cambia.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "student")
        before = counts(db)
        membership_before = membership_row(db, "ID-STU-98432", "CS-480")

        module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        after = counts(db)
        assert after["audit_ledger"] == before["audit_ledger"] + 1
        assert after["audit_events"] == before["audit_events"] + 1
        decided = events(db, "authorization.decided")
        assert len(decided) == 1
        assert (decided[0]["decision"], decided[0]["reason_code"]) == ("ALLOW", "SUCCESS")
        assert membership_row(db, "ID-STU-98432", "CS-480") == membership_before


    @red("p1")
    def test_resolve_before_granted_uses_base_role(self, db, module1):
        """Test ID: T-RES-I-03 (nuevo). Cláusula: I2 / H-21b (granted_at futuro -> aún no aplica, rol base).
        AD-13 (spine-local).

        Assertions: con granted_at en el futuro el rol efectivo es el base 'student' y el código NO es
        STATUS_ESCALATION_EXPIRED (el ticket no ha vencido, solo no ha empezado).
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")
        add_ticket(db, "ID-STU-98432", "CS101", "instructor_privileged",
                   at_offset(TEN_MINUTES_US), at_offset(SEVENTY_MINUTES_US))

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION)

        assert result["decision"] == "DENY"
        assert result["effective_role"] == "student"
        assert_code_first(result["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")


    @red("p0")
    def test_resolve_allows_cpu_toy_model_cs101(self, db, module1, explain_assert):
        """Test ID: T-RES-HP-03 (nuevo). Cláusula: Q1 + Ronda 6b (R6b-01): modelo `toy-cpu-demo` -> cpu_toy;
        fila v0 (CS101, student, inference, cpu_toy, true) [prd.md:244]. AD-10 (spine-local).

        Assertions: ALLOW con effective_role 'student' en CS101 para inferencia CPU; respuesta solo con
        {decision, effective_role, explanation} (I4: sin cuota GPU ni prioridad).
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_TOY_CS101, ACTION)

        assert (result["decision"], result["effective_role"]) == ("ALLOW", "student")
        assert set(result) == {"decision", "effective_role", "explanation"}
        explain_assert(result)


class TestPreconditions:
    """Categoría P (precondiciones): rechazo tipado con HTTP exacto, cero mutación y cero eventos."""

    @red("p1")
    def test_resolve_unknown_identity_404_no_mutation(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-P-01 (nuevo). Cláusula: P1 -> UNKNOWN_IDENTITY 404. Q-fail: cero mutación, cero evento.

        Assertions: código tipado exacto, HTTP 404, conteos de tablas idénticos, cola sin publicar.
        """
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions("STU-00000", "CS101", ARN_8B_CS101, ACTION)

        assert exc.value.code == "UNKNOWN_IDENTITY"
        assert exc.value.http_status == 404
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p1")
    def test_resolve_unknown_course_404_no_mutation(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-P-02 (nuevo). Cláusula: P2 -> UNKNOWN_COURSE 404 (precedencia tras identidad, F-03).

        Assertions: UNKNOWN_COURSE 404; cero filas nuevas; cero eventos.
        """
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(
                "TA-SOFIA-01", "CS-999", "urn:uai:subject:CS-999:model:llama-3-8b-instruct", ACTION
            )

        assert exc.value.code == "UNKNOWN_COURSE"
        assert exc.value.http_status == 404
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_arn_grammar_rejects(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-02 (nombre nominal de contracts.md §5). Cláusula: P4 -> MALFORMED_RESOURCE_ARN 400.
        AD-01 (heredado): gramática ^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$; sin strip ni upper.

        Assertions: el punto en el subject ('CS.101') se rechaza; cero mutación; cero eventos.
        """
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(
                "TA-SOFIA-01", "CS101", "urn:uai:subject:CS.101:model:llama-3-8b-instruct", ACTION
            )

        assert exc.value.code == "MALFORMED_RESOURCE_ARN"
        assert exc.value.http_status == 400
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p1")
    def test_resolve_invalid_at_400_no_mutation(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-P-04 (nuevo). Cláusula: P3 (solo entrada interna/replay) -> INVALID_AT 400.
        Entrada sin los 6 decimales de microsegundos (aunque con zona Z) se rechaza; sin normalización silenciosa.

        Assertions: INVALID_AT 400; cero mutación; cero eventos.
        """
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(
                "TA-SOFIA-01", "CS101", ARN_8B_CS101, ACTION, "2026-09-23T15:04:05Z"
            )

        assert exc.value.code == "INVALID_AT"
        assert exc.value.http_status == 400
        assert counts(db) == before
        assert fake_queue.published == []


    @red("p0")
    def test_resolve_malformed_action_400_no_mutation(self, db, module1, fake_queue, edge_case_seeds):
        """Test ID: T-RES-P-05 (nuevo). Cláusula: P4b (Q5 / ADVF-07, ECF-24) -> MALFORMED_ACTION 400.
        Gramática cerrada action ∈ {inference, training}: el vocabulario legado 'model:invoke' y la vacía
        se rechazan. AD-09 (spine-local), AD-10 (spine-local). Q-fail: cero mutación, cero eventos.

        Assertions: MALFORMED_ACTION 400 para 'model:invoke' y para ''; conteos idénticos; cola sin publicar.
        """
        before = counts(db)

        for accion_invalida in ("model:invoke", ""):
            with pytest.raises(Module1Error) as exc:
                module1.resolve_effective_permissions(
                    edge_case_seeds["institutional_id"], "CS101", ARN_8B_CS101, accion_invalida
                )
            assert exc.value.code == "MALFORMED_ACTION"
            assert exc.value.http_status == 400

        assert counts(db) == before
        assert fake_queue.published == []

    @red("p0")
    def test_resolve_resource_subject_mismatch_403_explained_no_mutation(self, db, module1):
        """Test ID: T-RES-10 (R8-04, AD-01). Cláusula: PRD §5.2 regla 2 (Confused Deputy) y contracts §1 P5:
        el subject del ARN (CS101) no es el contexto de la petición (CS-480) -> RESOURCE_SUBJECT_MISMATCH.
        La comparación es byte a byte (sin normalizar mayúsculas). AD-01 (heredado).

        Assertions: DENY con rule_ids[0] RESOURCE_SUBJECT_MISMATCH y AD-n citado; observed_context 'CS-480' y
        observed_resource_subject 'CS101'; cero mutación de membresías y credenciales; exactamente un evento
        DENY con reason_code RESOURCE_SUBJECT_MISMATCH en el ledger.
        """
        seed_student_pair(db)
        before = counts(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_TOY_CS101, ACTION, CLOCK_START)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "RESOURCE_SUBJECT_MISMATCH")
        assert_cites_ad(result["explanation"])
        assert result["explanation"]["observed_context"] == "CS-480"
        assert result["explanation"]["observed_resource_subject"] == "CS101"
        after = counts(db)
        assert after["subject_memberships"] == before["subject_memberships"]
        assert after["subject_credentials"] == before["subject_credentials"]
        assert [(e["decision"], e["reason_code"]) for e in events(db)] == [("DENY", "RESOURCE_SUBJECT_MISMATCH")]

    @red("p0", pytest.mark.edge_case)
    def test_resolve_subject_context_missing_denies_unauthorized_edge01_rule4(self, db, module1):
        """Test ID: T-RES-11 (EDGE-01 regla 4, R8-04). Cláusula: PRD §5.2 regla 4 (mínimo privilegio por
        defecto): identidad no activa en la materia del contexto -> DENY determinista
        SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED. AD-01 (heredado), AD-10 (spine-local).

        Setup: STU-ONLY-CS101 solo tiene membresía ACTIVE en CS101; se consulta el contexto CS-480.
        Assertions: DENY con rule_ids[0] SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED y AD-n citado; cero
        mutación de membresías; exactamente un evento DENY con ese reason_code.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-ONLY-CS101", "STU-ONLY-CS101")
        add_membership(db, identity, "CS101", "student")
        before = counts(db)

        result = module1.resolve_effective_permissions("STU-ONLY-CS101", "CS-480", ARN_8B_CS480, ACTION, CLOCK_START)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED")
        assert_cites_ad(result["explanation"])
        assert counts(db)["subject_memberships"] == before["subject_memberships"]
        assert [(e["decision"], e["reason_code"]) for e in events(db)] == [
            ("DENY", "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED")
        ]

    @red("p0")
    def test_resolve_auth_token_invalid_401_before_arn_validation(
        self, db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-RES-12 (R8-04, AD-09). Cláusula: contracts §0 orden único paso 1: bearer ausente o
        inválido -> 401 AUTH_TOKEN_INVALID ANTES de validar el ARN (aquí el ARN es mal formado y debería
        dar 400). AD-09 (spine-local).

        RED: Module1Service es stub puro; la verificación del bearer (TokenVerifierPort) es lógica GREEN pendiente.
        Corrección: antes pasaba en verde porque el stub delegaba en el fake configurado por el test (tautología).

        Assertions: 401 AUTH_TOKEN_INVALID (no 400 MALFORMED_RESOURCE_ARN); cero mutación; cero eventos.
        """
        seed_student_pair(db)
        before = counts(db)
        service = build_module1(
            db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, "tok-invalido"
        )

        with pytest.raises(Module1Error) as exc:
            service.resolve_effective_permissions(STUDENT_ID, "CS101", "arn-mal-formada", ACTION, CLOCK_START)

        assert exc.value.code == "AUTH_TOKEN_INVALID"
        assert exc.value.http_status == 401
        assert counts(db) == before
        assert events(db) == []

    @red("p0")
    @pytest.mark.parametrize("barred_status", ["SUSPENDED", "EXPELLED"])
    def test_resolve_identity_barred_denies_before_membership(self, db, module1, barred_status):
        """Test ID: T-RES-G-04 (gap G-4; IDENTITY_BARRED en /authorize). Cláusula: P5 + R9-01: identidad global
        SUSPENDED/EXPELLED deniega ANTES de mirar la membresía -> DENY IDENTITY_BARRED (403 lo mapea el adapter).
        AD-01 (heredado), AD-11 (explicabilidad). Historia E4-S3 (y E2-S2).

        Assertions: DENY con rule_ids[0] IDENTITY_BARRED y AD-n citado; membresía ACTIVE intacta; un único
        evento DENY/IDENTITY_BARRED en el ledger.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-98432", STUDENT_ID, status=barred_status)
        add_membership(db, identity, "CS-480", "student")
        before = counts(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "IDENTITY_BARRED")
        assert_cites_ad(result["explanation"])
        assert counts(db)["subject_memberships"] == before["subject_memberships"]
        assert [(e["decision"], e["reason_code"]) for e in events(db)] == [("DENY", "IDENTITY_BARRED")]

    @red("p1")
    def test_resolve_identity_barred_precedes_subject_mismatch(self, db, module1):
        """Test ID: T-RES-G-04b (gap G-4; precedencia H-17). Cláusula: P5 / contracts §1 punto 5: IDENTITY_BARRED >
        RESOURCE_SUBJECT_MISMATCH > membresía no activa. AD-01 (heredado). Historia E4-S3.

        Assertions: identidad SUSPENDED con membresía ACTIVE en CS-480, header CS-480 y ARN de CS101 ->
        rule_ids[0] IDENTITY_BARRED (no RESOURCE_SUBJECT_MISMATCH); cero mutación.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-98432", STUDENT_ID, status="SUSPENDED")
        add_membership(db, identity, "CS-480", "student")
        before = counts(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_TOY_CS101, ACTION)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "IDENTITY_BARRED")
        assert counts(db)["subject_memberships"] == before["subject_memberships"]

    @red("p0")
    @pytest.mark.parametrize("membership_status", ["SUSPENDED", "COMPLETED"])
    def test_resolve_suspended_or_completed_membership_denies_context_missing(self, db, module1, membership_status):
        """Test ID: T-RES-G-04c (gap G-4b; ADVF-08). Cláusula: contracts §1 punto 6: membresía no activa distinta de
        DROPPED (SUSPENDED, COMPLETED) -> SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED (DROPPED tiene código propio).
        AD-01 (heredado). Historia E2-S2.

        Assertions: DENY con rule_ids[0] SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED; cero mutación de membresías; un
        único evento DENY con ese reason_code.
        """
        ensure_base(db)
        identity = add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, identity, "CS-480", "student", status=membership_status)
        before = counts(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED")
        assert_cites_ad(result["explanation"])
        assert counts(db)["subject_memberships"] == before["subject_memberships"]
        assert [(e["decision"], e["reason_code"]) for e in events(db)] == [
            ("DENY", "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED")
        ]

    @red("p0")
    def test_resolve_header_cs101_arn_cs480_mismatch_403(self, db, module1):
        """Test ID: T-RES-G-05 (gap G-5; ejemplo literal R9-03). Cláusula: P5 + §0 (comparación cruda byte a byte):
        header CS101 con ARN de CS-480 -> RESOURCE_SUBJECT_MISMATCH 403. Orientación distinta de T-RES-10 (header
        CS-480 / ARN CS101), misma regla. AD-01 (heredado). Historia E4-S3.

        Assertions: DENY con rule_ids[0] RESOURCE_SUBJECT_MISMATCH y AD-n; observed_context 'CS101';
        observed_resource_subject 'CS-480'; cero mutación; un único evento DENY con ese reason_code.
        """
        seed_student_pair(db)
        before = counts(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS480, ACTION)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "RESOURCE_SUBJECT_MISMATCH")
        assert_cites_ad(result["explanation"])
        assert result["explanation"]["observed_context"] == "CS101"
        assert result["explanation"]["observed_resource_subject"] == "CS-480"
        assert counts(db)["subject_memberships"] == before["subject_memberships"]
        assert [(e["decision"], e["reason_code"]) for e in events(db)] == [("DENY", "RESOURCE_SUBJECT_MISMATCH")]

    @red("p1")
    def test_resolve_lowercase_course_header_404_unknown_course(self, db, module1, fake_queue):
        """Test ID: T-RES-G-06 (gap G-6; R9-03, ADVF-10). Cláusula: P2 + §0 (comparación byte a byte): el header
        `cs-480` no existe en subjects.id -> UNKNOWN_COURSE 404 (no 403 por mismatch). AD-01 (heredado). Historia E4-S3.

        Assertions: UNKNOWN_COURSE 404; conteos idénticos (cero eventos); cola sin publicar.
        """
        seed_student_pair(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(STUDENT_ID, "cs-480", ARN_8B_CS480, ACTION)

        assert exc.value.code == "UNKNOWN_COURSE"
        assert exc.value.http_status == 404
        assert counts(db) == before
        assert fake_queue.published == []

    @red("p1")
    def test_resolve_missing_identity_and_course_reports_identity_first(self, db, module1, fake_queue):
        """Test ID: T-RES-G-07 (gap G-7; precedencia F-03). Cláusula: P1 antes que P2: identidad y curso inexistentes
        -> UNKNOWN_IDENTITY 404 (no UNKNOWN_COURSE). AD-01 (heredado). Historia E1-S2.

        Assertions: UNKNOWN_IDENTITY 404; conteos idénticos; cola sin publicar.
        """
        ensure_base(db)
        before = counts(db)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(
                "STU-00000", "CS-999", "urn:uai:subject:CS-999:model:llama-3-8b-instruct", ACTION
            )

        assert exc.value.code == "UNKNOWN_IDENTITY"
        assert exc.value.http_status == 404
        assert counts(db) == before
        assert fake_queue.published == []


class TestInvariants:
    """Categoría I (invariantes y fronteras): atomicidad, aislamiento, límites y reglas de precedencia."""

    @red("p0")
    def test_escalation_boundary_expires(self, db, module1, explain_assert):
        """Test ID: T-RES-04 (nombre nominal de contracts.md §5). Cláusula: I2 (at >= expires_at -> expirado).
        AD-13 (spine-local) + AD-05 (heredado). Intervalo [granted_at, expires_at).

        Assertions: un microsegundo antes de expires_at el ticket aún aplica (rol escalado);
        en at == expires_at no aplica: DENY con STATUS_ESCALATION_EXPIRED y rol base; el ticket no se muta.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")
        granted = at_offset(0)
        expires = at_offset(ONE_HOUR_US)
        ticket = add_ticket(db, "ID-STU-98432", "CS101", "instructor_privileged", granted, expires)

        still_active = module1.resolve_effective_permissions(
            STUDENT_ID, "CS101", ARN_8B_CS101, ACTION, at_offset(ONE_HOUR_US - ONE_MICROSECOND)
        )
        assert still_active["effective_role"] == "instructor_privileged"
        assert_code_first(still_active["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")

        expired = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION, expires)
        assert expired["decision"] == "DENY"
        assert expired["effective_role"] == "student"
        assert_code_first(expired["explanation"], "STATUS_ESCALATION_EXPIRED")
        assert expired["explanation"]["threshold"] == f"expires_at={expires}"
        explain_assert(expired)
        assert ticket_status(db, ticket) == "ACTIVE"  # resolve no muta el ticket (contracts §1 Tiempo)


    @red("p0")
    def test_resolve_after_revoke_commit_denies_enrollment_dropped(self, db, module1):
        """Test ID: T-RES-03 (nuevo, sobre T-REV-01). Cláusula: Concurrencia de resolve tras commit de baja.
        AD-03 (heredado): un resolve posterior al commit observa el estado revocado y deniega.

        Assertions: tras revokeCourseAccess(CS-480) un resolve sobre CS-480 devuelve DENY con
        SUBJECT_ENROLLMENT_DROPPED, sin ALLOW residual.
        """
        seed_student_pair(db)
        module1.revoke_course_access(STUDENT_ID, "CS-480", "Baja previa al resolve", CLOCK_START)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert result["decision"] == "DENY"
        assert_code_first(result["explanation"], "SUBJECT_ENROLLMENT_DROPPED")


    @red("p1")
    def test_resolve_model_outside_catalog_denied(self, db, module1):
        """Test ID: T-RES-I-04 (nuevo). Cláusula: paso 7 del orden único + Ronda 6b (R6b-01): `model` fuera de
        resource_catalog -> DENY 403 UNAUTHORIZED_RESOURCE_CLASS (fail-closed, sin herencia). AD-10 (spine-local),
        AD-11 (spine-local).

        Assertions: DENY con rule_ids[0] == UNAUTHORIZED_RESOURCE_CLASS; effective_role 'student';
        exactamente un authorization.decided DENY/UNAUTHORIZED_RESOURCE_CLASS (intento denegado registrado).
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "student")
        arn_fuera_catalogo = "urn:uai:subject:CS-480:model:llama-70b-no-catalogado"

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", arn_fuera_catalogo, ACTION)

        assert result["decision"] == "DENY"
        assert result["effective_role"] == "student"
        assert_code_first(result["explanation"], "UNAUTHORIZED_RESOURCE_CLASS")
        decided = events(db, "authorization.decided")
        assert [(e["decision"], e["reason_code"]) for e in decided] == [("DENY", "UNAUTHORIZED_RESOURCE_CLASS")]

    @red("p0")
    def test_resolve_queue_full_503_no_decision_no_mutation(self, db, module1, fake_queue):
        """Test ID: T-RES-13 (R8-04, AD-12). Cláusula: contracts §1 Q3: si el evento obligatorio no puede
        aceptarse en la cola -> 503 AUTH_INTERNAL_POLICY_UNAVAILABLE en vez de 200/403 (fail-closed).
        AD-12 (spine-local), AD-04 (heredado).

        Setup: cola sin capacidad (set_capacity(0)) para un ALLOW válido de STU-98432 en CS-480.
        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; ni ALLOW ni DENY; cero filas nuevas en
        membresías, credenciales, ledger y eventos.
        """
        seed_student_pair(db)
        before = counts(db)
        fake_queue.set_capacity(0)

        with pytest.raises(Module1Error) as exc:
            module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION, CLOCK_START)

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert counts(db) == before

    @red("p0")
    def test_resolve_clock_failure_503_fail_closed_no_decision_no_mutation(
        self, db, fake_id_generator, fake_queue, fake_token_verifier
    ):
        """Test ID: T-RES-15 (R12-B01, hallazgo SEC B-01). Cláusula: contracts §1 Q-fail [ADOPTED 2026-10-14,
        estudiante]: si Clock.now() lanza durante resolveEffectivePermissions no hay instante de evaluación ni
        request_now; la respuesta es 503 AUTH_INTERNAL_POLICY_UNAVAILABLE (reintentable), fail-closed: nunca ALLOW,
        cero mutación, cero eventos (ni parciales). AD-08 (spine-local), AD-12 (spine-local). Historia: E1-S2.

        Setup: seed_student_pair; servicio compuesto con RaisingClock (test/fakes/fake_failing_ports.py).
        Assertions: 503 AUTH_INTERNAL_POLICY_UNAVAILABLE; tablas sin cambios; cero eventos.
        """
        seed_student_pair(db)
        before = counts(db)
        service = build_module1(
            db, RaisingClock(), fake_id_generator, fake_queue, fake_token_verifier, STUDENT_TOKEN
        )

        with pytest.raises(Module1Error) as exc:
            service.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert exc.value.code == "AUTH_INTERNAL_POLICY_UNAVAILABLE"
        assert exc.value.http_status == 503
        assert counts(db) == before
        assert events(db) == []

    @red("p0")
    def test_resolve_after_drop_isolates_other_course_and_logs_each_deny(self, db, module1):
        """Test ID: T-RES-G-03 (gap G-3). Cláusula: I1 (aislamiento tras la baja) + repetición de resolve denegado;
        un evento DENY por intento en /authorize. AD-03 (heredado), AD-01 (heredado). Historia E2-S2.

        Assertions: tras revocar CS-480, resolve sobre CS101 (toy-cpu-demo) sigue ALLOW; tres resolve sobre CS-480
        devuelven DENY SUBJECT_ENROLLMENT_DROPPED; authorization.decided = ALLOW/SUCCESS seguido de tres
        DENY/SUBJECT_ENROLLMENT_DROPPED.
        """
        seed_student_pair(db)
        module1.revoke_course_access(STUDENT_ID, "CS-480", "Baja para aislamiento", CLOCK_START)

        allowed = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_TOY_CS101, ACTION)
        assert allowed["decision"] == "ALLOW"
        for _ in range(3):
            denied = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)
            assert denied["decision"] == "DENY"
            assert_code_first(denied["explanation"], "SUBJECT_ENROLLMENT_DROPPED")
        assert [(e["decision"], e["reason_code"]) for e in events(db, "authorization.decided")] == (
            [("ALLOW", "SUCCESS")] + [("DENY", "SUBJECT_ENROLLMENT_DROPPED")] * 3
        )

    @red("p1")
    def test_resolve_deny_response_has_no_quota_or_priority_fields(self, db, module1):
        """Test ID: T-RES-G-17 (gap G-17; I4). Cláusula: I4 — la respuesta de resolve no expone cuota GPU ni
        prioridad, también en DENY (T-RES-HP-01 y HP-03 solo verifican ALLOW). AD-01 (heredado). Historia E4-S1.

        Assertions: DENY por clase de recurso con claves exactas {decision, effective_role, explanation}; ninguna
        clave de la respuesta ni de explanation contiene 'quota' ni 'prior'.
        """
        seed_student_pair(db)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION)

        assert result["decision"] == "DENY"
        assert set(result) == {"decision", "effective_role", "explanation"}
        keys = set(result) | set(result["explanation"])
        assert [k for k in keys if re.search(r"quota|prior", k, re.IGNORECASE)] == []


class TestExplainability:
    """Categoría X (explicabilidad AD-11): rule_ids citan la regla y los valores observados."""

    @red("p1", pytest.mark.explainability)
    def test_explain_deny_expired_threshold_reports_expires_at(self, db, module1, explain_assert):
        """Test ID: T-RES-08b (variante de explicabilidad). Cláusula: Q4 + threshold (expires_at cuando aplica).
        AD-11 (spine-local), AD-13 (spine-local).

        Assertions: STATUS_ESCALATION_EXPIRED lleva threshold 'expires_at=<instante>' y rule_ids[0] == code.
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS101", "student")
        expires = at_offset(ONE_HOUR_US)
        add_ticket(db, "ID-STU-98432", "CS101", "instructor_privileged", at_offset(0), expires)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS101", ARN_8B_CS101, ACTION, expires)

        explain_assert(result)
        assert_code_first(result["explanation"], "STATUS_ESCALATION_EXPIRED")
        assert result["explanation"]["threshold"] == f"expires_at={expires}"


class TestSecrets:
    """R-006 / AD-06: ningún secreto `uai_live_` completo sale en respuesta, log o ledger."""
    @red("p0")
    def test_resolve_secret_in_action_400_never_echoed_in_clear(self, db, module1, caplog):
        """Test ID: T-RES-14 (R-006 en resolve, AD-06 / NFR-SEC-04). Cláusula: AD-06 (heredado): una clave
        uai_live_ completa en la petición nunca sale en claro en la respuesta de error ni en logs; el
        enmascarado uai_live_<4>••••••••••••<4> sí aparece donde el valor se muestra (el detalle MALFORMED_ACTION
        cita el valor recibido).

        Assertions: 400 MALFORMED_ACTION; regex uai_live_[A-Za-z0-9]{8,} ausente en la respuesta y en caplog;
        la forma enmascarada presente en el detalle; cero mutación.
        """
        seed_student_pair(db)
        before = counts(db)

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(Module1Error) as exc:
                module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, SECRET_FULL, CLOCK_START)

        assert exc.value.code == "MALFORMED_ACTION"
        assert exc.value.http_status == 400
        assert not SECRET_RAW_RE.search(str(exc.value.body))
        assert not SECRET_RAW_RE.search(caplog.text)
        assert SECRET_MASKED in str(exc.value.body)
        assert counts(db) == before


class TestRequestTimeAndRole:
    """R-008 / R-011: un request = un instante (H-16) y effective_role = roles.id exacto (H-26)."""

    @red("p0")
    def test_resolve_request_now_captured_once_and_reused_as_occurred_at(self, db, module1, fake_clock, monkeypatch):
        """Test ID: T-RES-05 (nuevo). Cláusula: H-16 [ADOPTED 2026-10-13]: request_now se captura UNA vez al
        entrar al adapter, antes de autenticar; ese mismo valor sirve para la evaluación, los timestamps y
        occurredAt del evento. AD-13 (spine-local). Historia: E1-S2.

        Assertions: durante un ALLOW se lee Clock.now() exactamente una vez; el evento authorization.decided
        lleva como timestamp esa única lectura.
        """
        seed_student_pair(db)
        reads: list[str] = []
        original_now = fake_clock.now

        def counting_now() -> str:
            value = original_now()
            reads.append(value)
            fake_clock.advance(1)  # cada lectura posterior tendría otro instante
            return value

        monkeypatch.setattr(fake_clock, "now", counting_now)

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        assert result["decision"] == "ALLOW"
        assert len(reads) == 1, f"request_now debe capturarse una vez; lecturas: {reads}"
        decided = events(db, "authorization.decided")
        assert decided[0]["timestamp"] == reads[0]

    @red("p1")
    def test_resolve_effective_role_is_exact_roles_id(self, db, module1, explain_assert):
        """Test ID: T-RES-09 (nuevo). Cláusula: H-26 [ADOPTED 2026-10-13]: effective_role es el identificador
        exacto de roles.id del DDL, sin transformar (ni mayúsculas ni título). AD-10 (spine-local). Historia: E4-S1.

        Assertions: TA en CS-480 con inferencia ALLOW y effective_role == 'ta' (exacto, no 'TA' ni 'Ta').
        """
        ensure_base(db)
        add_identity(db, "ID-STU-98432", STUDENT_ID)
        add_membership(db, "ID-STU-98432", "CS-480", "ta")

        result = module1.resolve_effective_permissions(STUDENT_ID, "CS-480", ARN_8B_CS480, ACTION)

        explain_assert(result)
        assert result["decision"] == "ALLOW"
        assert result["effective_role"] == "ta"


class TestHttpTransport:
    """Categoría P (transporte HTTP de /authorize): el header de contexto se valida en el adapter (AD-01, AD-09)."""

    @red("p0")
    @pytest.mark.parametrize(
        "context",
        [["CS-480", "CS-480"], ["CS-480", "CS101"], [""]],
        ids=["repetido-igual", "repetido-distinto", "vacio"],
    )
    def test_authorize_subject_context_repeated_or_empty_is_absent(self, db, context):
        """Test ID: T-RES-H24 (nuevo). Cláusula: H-24 [ADOPTED 2026-10-13]: X-Academic-Subject-Context repetido
        o vacío se trata como ausente y produce SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED (paso 3); el valor se
        compara tal como lo entrega el parser HTTP, sin normalizar. AD-01 (heredado), AD-09 (spine-local).
        Historia: E4-S4.

        Assertions: DENY (o Module1Error) con código SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED y cero mutación ni
        eventos; control: con un único header CS-480 el mismo estudiante sí obtiene ALLOW.
        """
        seed_student_pair(db)
        body = {"user_id": STUDENT_ID, "resource_arn": ARN_8B_CS480, "action": ACTION}
        before = counts(db)
        outcome = decision_of(lambda: http_authorize(STUDENT_TOKEN, body, context))

        assert outcome in {
            ("DENY", "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED"),
            ("ERROR", "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED"),
        }, outcome
        assert counts(db) == before
        assert events(db, "authorization.decided") == []
        assert decision_of(lambda: http_authorize(STUDENT_TOKEN, body, "CS-480")) == ("ALLOW", None)
