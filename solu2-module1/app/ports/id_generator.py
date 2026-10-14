"""Puerto outbound IdGenerator.new_id() (AD-08): batch_id pre-validacion
de filas, formato roster-<8hex>-<term> (contracts §3 Q1). Fake: FakeIdGenerator.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class IdGeneratorPort(ABC):
    @abstractmethod
    def new_id(self, prefix: str = "id") -> str:
        """ID determinista 'prefix-<8hex>'."""
        raise NotImplementedError("IdGeneratorPort.new_id: stub, pendiente ATDD")
