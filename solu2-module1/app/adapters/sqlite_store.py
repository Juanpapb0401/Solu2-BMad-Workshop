"""Adapter driven sqlite_store (stub): SQLAlchemy 2.0 sobre 001_module1_schema.sql,
SQLite WAL writer único, busy_timeout 5000 (AD-02/AD-03). Cableado posterior."""
from __future__ import annotations

from typing import Any


class SQLiteStore:
    """Stub: todo método lanza NotImplementedError hasta ATDD/integración."""

    def __init__(self, dsn: str = "") -> None:
        self.dsn = dsn

    def get_membership(
        self, identity_id: str, subject_id: str
    ) -> dict[str, Any] | None:
        raise NotImplementedError("SQLiteStore.get_membership: stub, pendiente ATDD")
