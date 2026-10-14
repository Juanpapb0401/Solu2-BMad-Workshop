"""domain/roster — ingestRoster (stub ATDD).

Contrato: contracts.md §3 (P/Q/I). batch = {subject_id, term, rows[]} primitivos
(sin DTO framework en dominio, AD-08). bearer (string crudo) y token_verifier (puerto,
tipado Any) se reciben sin verificar aquí: 401 primero, luego admin (P0), luego sintaxis.
"""
from __future__ import annotations

from typing import Any


def ingestRoster(
    batch: dict[str, Any], bearer: str | None, token_verifier: Any,
    credential_delivery: Any = None,
) -> dict[str, Any]:
    """Retorna {processed, created_identities, updated_memberships, batch_id, explanation} o
    lanza Module1Error con manifiesto 422 (ROSTER_VALIDATION_FAILED, INTRA_BATCH_DUPLICATE_ID,
    IDENTITY_BARRED). Stub RED."""
    raise NotImplementedError("ingestRoster: pendiente GREEN (contracts §3, AD-09 401 primero)")
