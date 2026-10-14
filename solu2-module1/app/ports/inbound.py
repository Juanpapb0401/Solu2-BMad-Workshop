"""Puertos inbound: AuthorizePort / RevokePort / IngestPort (AD-09).

Mapeo 1:1 con operaciones de dominio (ports-and-adapters.md §1). El Bearer lo
verifica TokenVerifierPort antes de cualquier validación (contracts §1 orden único).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AuthorizePort(ABC):
    @abstractmethod
    def resolve(
        self,
        user_id: str,
        course_id: str,
        resource_arn: str,
        action: str,
        at: str | None,
    ) -> dict[str, Any]:
        raise NotImplementedError("AuthorizePort.resolve: stub, pendiente ATDD")


class RevokePort(ABC):
    @abstractmethod
    def drop(
        self, user_id: str, course_id: str, drop_reason: str, timestamp: str | None
    ) -> dict[str, Any]:
        raise NotImplementedError("RevokePort.drop: stub, pendiente ATDD")


class IngestPort(ABC):
    @abstractmethod
    def ingest(
        self, subject_id: str, term: str, rows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        raise NotImplementedError("IngestPort.ingest: stub, pendiente ATDD")
