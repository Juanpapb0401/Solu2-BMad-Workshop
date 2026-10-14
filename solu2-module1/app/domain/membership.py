"""domain/membership — revokeCourseAccess (stub ATDD).

Contrato: contracts.md §2 (P/Q/I). Firma Annex A revokeCourseAccess(userId, courseId);
drop_reason y timestamp vienen del body {drop_reason, timestamp} (contracts §0/§2 P3-P4).
bearer (string crudo) y token_verifier (puerto, tipado Any) se reciben sin verificar aquí:
la verificación del actor (P0: admin) es lógica GREEN.
"""
from __future__ import annotations

from typing import Any


def revokeCourseAccess(
    user_id: str, course_id: str, drop_reason: str, timestamp: str | None,
    bearer: str | None, token_verifier: Any,
) -> dict[str, Any]:
    """Retorna {student_id, subject_id, status, revocation_propagated_at, explanation}.
    Stub RED."""
    raise NotImplementedError("revokeCourseAccess: pendiente GREEN (contracts §2, AD-09 401 primero)")
