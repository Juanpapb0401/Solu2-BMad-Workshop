"""domain/resolution — resolveEffectivePermissions (stub ATDD).

Contrato: contracts.md §1 (P/Q/I). `at` es entrada interna/test/replay
(endpoint público sin `at`; el adapter captura Clock.now() una vez).
bearer (string crudo) y token_verifier (puerto, tipado Any para no importar ports en domain)
se reciben tal cual: la verificación del actor (401 primero) es lógica GREEN.
"""
from __future__ import annotations

from typing import Any


def resolveEffectivePermissions(
    user_id: str,
    course_id: str,
    resource_arn: str,
    action: str,
    at: str | None,
    bearer: str | None,
    token_verifier: Any,
) -> dict[str, Any]:
    """Retorna {decision: ALLOW|DENY, effective_role, explanation} o lanza Module1Error (P1-P4).
    `at` None = request_now. Stub RED."""
    raise NotImplementedError("resolveEffectivePermissions: pendiente GREEN (contracts §1, AD-09 401 primero)")
