"""Puerto outbound Clock.now() (AD-08/AD-13): UTC ISO-8601 con microsegundos.

Captura única request_now por solicitud (contracts §0). Fake: FakeClock.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ClockPort(ABC):
    @abstractmethod
    def now(self) -> str:
        """Instante actual UTC 'YYYY-MM-DDTHH:mm:ss.ffffffZ'."""
        raise NotImplementedError("ClockPort.now: stub, pendiente ATDD")
