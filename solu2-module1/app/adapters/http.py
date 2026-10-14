"""Adapters inbound HTTP (stubs, AD-09): POST /api/v1/authorize,
POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop,
POST /api/v1/subjects/{subject_id}/roster. Routers FastAPI en fase posterior."""
from __future__ import annotations

from typing import Any


def http_authorize(
    bearer: str | None, body: dict[str, Any], context: str | list[str] | None
) -> dict[str, Any]:
    """`context` = valores del header X-Academic-Subject-Context tal como los entrega el parser HTTP
    (lista si el header aparece repetido; H-24 los trata como ausentes)."""
    raise NotImplementedError("http_authorize: stub, pendiente ATDD")


def http_drop(
    bearer: str | None, subject_id: str, student_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    raise NotImplementedError("http_drop: stub, pendiente ATDD")


def http_roster(
    bearer: str | None, subject_id: str, term: str | None, body: Any
) -> dict[str, Any]:
    raise NotImplementedError("http_roster: stub, pendiente ATDD")


def parse_roster_body(content_type: str | None, raw: bytes) -> list[dict[str, str]]:
    """Parsea el cuerpo de ingesta (CSV multipart o JSON) y retorna las filas.

    Errores (MALFORMED_BATCH 400): BOM UTF-8, Content-Type no soportado, multipart con
    cantidad de partes `file` distinta de 1, columnas distintas de
    institutional_id,email,full_name,assigned_role. Stub: ATDD (AD-09, ECF-19/21/22)."""
    raise NotImplementedError("parse_roster_body: stub, pendiente ATDD")


def parse_csv_rfc4180(text: str) -> list[list[str]]:
    """Parsea CSV según RFC 4180 (comillas, comas y saltos dentro de campo, `""` escapado).
    Stub: ATDD (ECF-20)."""
    raise NotImplementedError("parse_csv_rfc4180: stub, pendiente ATDD")


def declared_routes() -> set[tuple[str, str]]:
    """Pares (método, ruta) declarados por el adaptador HTTP para las tres operaciones.
    Stub: ATDD (AD-09: mapeo único operación -> ruta)."""
    raise NotImplementedError("declared_routes: stub, pendiente ATDD")
