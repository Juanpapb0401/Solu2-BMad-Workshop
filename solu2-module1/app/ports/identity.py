"""Puertos outbound de identidad simulada (AGENTS.md: identidad institucional tras port).

TokenVerifierPort.verify(bearer) -> {actor_id, actor_role} o lanza InvalidTokenError (señal
de puerto, sin código HTTP). El servicio es quien mapea InvalidTokenError a
AUTH_TOKEN_INVALID / 401 (contracts.md §0 y §4, Ronda 6 Q2 / ADVF-02/03).
CredentialDeliveryPort.enqueue(identity_id, raw_key): outbox simulado de entrega de
credenciales en ingestRoster (Ronda 6 Q4 / ADVF-16). Fake: test/fakes/fake_token_verifier.py.
Solo firmas; cero lógica.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class InvalidTokenError(Exception):
    """Bearer ausente, vencido o desconocido. Tipo de señal del puerto; sin código HTTP."""


class TokenVerifierPort(ABC):
    @abstractmethod
    def verify(self, bearer: str | None) -> dict[str, str]:
        """Retorna {actor_id, actor_role} del token; si es ausente/inválido/vencido lanza
        InvalidTokenError."""
        raise NotImplementedError("TokenVerifierPort.verify: stub, pendiente ATDD")


class CredentialDeliveryPort(ABC):
    @abstractmethod
    def enqueue(self, identity_id: str, raw_key: str) -> None:
        """Encola la entrega de la credencial en claro (no se devuelve en la respuesta 201)."""
        raise NotImplementedError("CredentialDeliveryPort.enqueue: stub, pendiente ATDD")
