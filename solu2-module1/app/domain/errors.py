"""Error tipado del Módulo 1 (catálogo contracts.md §4). Solo tipos, sin lógica.

El dominio lanza Module1Error con el `code` exacto del catálogo y el HTTP
asociado; el adapter HTTP lo serializa (ErrorBody / DenyBody) sin reinterpretarlo.
"""
from __future__ import annotations

from typing import Any


class Module1Error(Exception):
    def __init__(self, code: str, http_status: int, body: dict[str, Any] | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.http_status = http_status
        self.body = body or {}
