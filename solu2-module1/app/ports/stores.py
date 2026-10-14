"""Puertos outbound de stores/ledger (stubs).

MembershipStore, IdentityStore, CredentialStore, EscalationStore,
LedgerWriter.append(event), QueueReservation (reserva/publica/libera),
RegistrarSource (origen simulado). Fuente: ports-and-adapters.md §1.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MembershipStore(ABC):
    @abstractmethod
    def get(self, identity_id: str, subject_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("MembershipStore.get: stub, pendiente ATDD")


class IdentityStore(ABC):
    @abstractmethod
    def resolve(self, user_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("IdentityStore.resolve: stub, pendiente ATDD")


class CredentialStore(ABC):
    @abstractmethod
    def revoke_pair(self, identity_id: str, subject_id: str) -> int:
        raise NotImplementedError(
            "CredentialStore.revoke_pair: stub, pendiente ATDD"
        )


class EscalationStore(ABC):
    @abstractmethod
    def active_for(
        self, identity_id: str, subject_id: str, at: str
    ) -> dict[str, Any] | None:
        raise NotImplementedError("EscalationStore.active_for: stub, pendiente ATDD")


class LedgerWriter(ABC):
    @abstractmethod
    def append(self, event: dict[str, Any]) -> None:
        raise NotImplementedError("LedgerWriter.append: stub, pendiente ATDD")


class QueueReservation(ABC):
    @abstractmethod
    def reserve(self) -> bool:
        raise NotImplementedError("QueueReservation.reserve: stub, pendiente ATDD")

    @abstractmethod
    def publish(self, event: dict[str, Any]) -> None:
        raise NotImplementedError("QueueReservation.publish: stub, pendiente ATDD")

    @abstractmethod
    def release(self) -> None:
        raise NotImplementedError("QueueReservation.release: stub, pendiente ATDD")
