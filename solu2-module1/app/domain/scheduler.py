"""domain/scheduler — barrido de escalaciones vencidas (stub ATDD).

Contrato: contracts.md §1 Tiempo / G6-02 [ADOPTED 2026-10-13]: barrido cada 1 s, transición
ACTIVE->EXPIRED con un evento `escalation.expired` por transición, reconciliación tras crash
(barre ACTIVE con expires_at <= now). Si la cola no acepta el evento, el barrido se DIFIERE
y se emite `scheduler_sweep_deferred_total` por TelemetryPort (R8-06). Tiempo solo por `clock`.
"""
from __future__ import annotations

from typing import Any


def sweep_expired(db: Any, clock: Any, queue: Any, telemetry: Any) -> int:
    """Retorna el número de transiciones ACTIVE->EXPIRED confirmadas. Stub: ATDD."""
    raise NotImplementedError("sweep_expired: stub, pendiente ATDD")
