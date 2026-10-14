"""Puertos simulados que fallan a propósito (R12-B01, hallazgo SEC B-01 de review-security.md).

Sirven para comprobar el fail-closed de resolveEffectivePermissions (Clock) e ingestRoster
(IdGenerator): cualquier excepción de la infraestructura se traduce en
503 AUTH_INTERNAL_POLICY_UNAVAILABLE, sin ALLOW/DENY, sin mutación y sin eventos.
"""
from __future__ import annotations


class RaisingClock:
    """Clock simulado cuyo now() lanza: fallo del reloj inyectado."""

    def now(self) -> str:
        raise RuntimeError("Clock simulado caído (R12-B01)")

    def advance(self, seconds: float) -> str:
        raise RuntimeError("Clock simulado caído (R12-B01)")


class RaisingIdGenerator:
    """IdGenerator simulado cuyo new_id() lanza: fallo al asignar batch_id/eventId."""

    def new_id(self, prefix: str = "id") -> str:
        raise RuntimeError("IdGenerator simulado caído (R12-B01)")
