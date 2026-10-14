"""Doble determinista de CredentialDeliveryPort (outbox simulado en memoria, Ronda 6 Q4 / R8-01).

Solo registra las entregas encoladas (identity_id, raw_key); no decide reglas de negocio.
"""
from __future__ import annotations

import threading

from app.ports.identity import CredentialDeliveryPort


class FakeCredentialDelivery(CredentialDeliveryPort):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.deliveries: list[tuple[str, str]] = []

    def enqueue(self, identity_id: str, raw_key: str) -> None:
        with self._lock:
            self.deliveries.append((identity_id, raw_key))
