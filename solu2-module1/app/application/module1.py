"""Punto de composición del Módulo 1 (stub, cero lógica productiva).

Firma de contrato: build_module1(db, clock, id_generator, queue, token_verifier, bearer)
-> Module1Service. El servicio NO verifica nada: pasa el `bearer` crudo y el
`token_verifier` a los stubs de dominio de cada operación; la verificación (401
AUTH_TOKEN_INVALID antes de validar nada, contracts §0/§1) será lógica GREEN del dominio.
Cada stub lanza su propio NotImplementedError en fase RED.
"""
from __future__ import annotations

from typing import Any

from app.domain.membership import revokeCourseAccess
from app.domain.resolution import resolveEffectivePermissions
from app.domain.roster import ingestRoster


class Module1Service:
    def __init__(
        self, db: Any, clock: Any, id_generator: Any, queue: Any,
        token_verifier: Any, bearer: str | None, credential_delivery: Any = None,
    ) -> None:
        self.db = db
        self.clock = clock
        self.id_generator = id_generator
        self.queue = queue
        self.token_verifier = token_verifier
        self.bearer = bearer
        self.credential_delivery = credential_delivery

    def resolve_effective_permissions(
        self,
        user_id: str,
        course_id: str,
        resource_arn: str,
        action: str,
        at: str | None = None,
    ) -> dict[str, Any]:
        return resolveEffectivePermissions(
            user_id, course_id, resource_arn, action, at, self.bearer, self.token_verifier
        )

    def revoke_course_access(
        self, user_id: str, course_id: str, drop_reason: str, timestamp: str | None
    ) -> dict[str, Any]:
        return revokeCourseAccess(
            user_id, course_id, drop_reason, timestamp, self.bearer, self.token_verifier
        )

    def ingest_roster(self, batch: dict[str, Any]) -> dict[str, Any]:
        return ingestRoster(batch, self.bearer, self.token_verifier, self.credential_delivery)


def build_module1(
    db: Any, clock: Any, id_generator: Any, queue: Any,
    token_verifier: Any, bearer: str | None, credential_delivery: Any = None,
) -> Module1Service:
    return Module1Service(
        db, clock, id_generator, queue, token_verifier, bearer, credential_delivery
    )
