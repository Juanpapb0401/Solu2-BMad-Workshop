"""Doble determinista de la cola de auditoría (QueueReservation, ports/stores.py).

Solo registra reservas y publicaciones; no decide ALLOW/DENY ni reglas de negocio.
set_capacity(0) simula cola llena (contracts §2 Q2 / §3 Q3 → 503 fail-closed).
"""
from __future__ import annotations

import threading
from typing import Any

from app.ports.stores import QueueReservation


class FakeQueueReservation(QueueReservation):
    def __init__(self, capacity: int = 1_000_000) -> None:
        self._lock = threading.Lock()
        self.capacity = capacity
        self.reserved = 0
        self.published: list[dict[str, Any]] = []
        self.released = 0

    def set_capacity(self, capacity: int) -> None:
        with self._lock:
            self.capacity = capacity

    def reserve(self) -> bool:
        with self._lock:
            if self.capacity - self.reserved <= 0:
                return False
            self.reserved += 1
            return True

    def publish(self, event: dict[str, Any]) -> None:
        with self._lock:
            self.reserved -= 1
            self.published.append(dict(event))

    def release(self) -> None:
        with self._lock:
            self.reserved -= 1
            self.released += 1
