"""Doble determinista del TokenVerifierPort (identidad simulada, AGENTS.md).

Tokens de fixture: ADMIN_TOKEN = Department Chair con rol institucional `admin`
(Ronda 6 Q1: único rol que puede revocar o ingestar); STUDENT_TOKEN = estudiante.
Cualquier otro bearer (ausente, vacío o desconocido) lanza InvalidTokenError (tipo del puerto).
El doble no decide códigos HTTP ni reglas de negocio: el mapeo a error de contrato es del servicio.
"""
from __future__ import annotations

from app.ports.identity import InvalidTokenError, TokenVerifierPort

ADMIN_TOKEN = "tok-fixture-admin-dept-chair"
STUDENT_TOKEN = "tok-fixture-student-stu-98432"

_ACTORS: dict[str, dict[str, str]] = {
    ADMIN_TOKEN: {"actor_id": "ID-DEPT-CHAIR-01", "actor_role": "admin"},
    STUDENT_TOKEN: {"actor_id": "ID-STU-98432", "actor_role": "student"},
}


class FakeTokenVerifier(TokenVerifierPort):
    def verify(self, bearer: str | None) -> dict[str, str]:
        actor = _ACTORS.get(bearer) if bearer else None
        if actor is None:
            raise InvalidTokenError()
        return dict(actor)
