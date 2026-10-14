"""Generador de IDs determinista y seguro para hilos (IdGenerator simulado).

Mismo formato que FakeIdGenerator de test/conftest.py (`prefix-<8hex>`), con lock para que dos
hilos de un test de concurrencia no reciban el mismo ID.
"""
from __future__ import annotations

import threading


class ThreadSafeIdGenerator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._n = 0

    def new_id(self, prefix: str = "id") -> str:
        with self._lock:
            self._n += 1
            return f"{prefix}-{self._n:08x}"
