"""domain/pagination — normalización de page_size (AD-07, heredado; stub ATDD).

Contrato: contracts.md §4 (`page_size` fuera de [1, 100] no es error: se fuerza al rango).
Alcance: solo listados. La consulta forense (NFR-AUDIT-06) queda FUERA de las tres
operaciones del Módulo 1 (owner B) y no se implementa aquí.
"""
from __future__ import annotations


def clamp_page_size(n: int) -> int:
    """Retorna n acotado a [1, 100]. Stub: ATDD."""
    raise NotImplementedError("clamp_page_size: stub, pendiente ATDD")
