"""Fixtures de la suite ATDD del Módulo 1 (composición de puertos simulados).

Añade test/ al sys.path para importar `fakes` (no hay __init__.py en test/).
El `module1` por defecto actúa con el token de admin (Department Chair simulado);
los tests de 403 ADMIN_ROLE_REQUIRED componen el servicio con STUDENT_TOKEN.
"""
from __future__ import annotations

import os
import sys

import pytest

ATDD_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.dirname(ATDD_DIR)
for _path in (TEST_DIR, ATDD_DIR):  # `fakes` (test/) y `atdd_support` (test/atdd/)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from app.application.module1 import build_module1  # noqa: E402
from fakes.fake_queue import FakeQueueReservation  # noqa: E402
from fakes.fake_token_verifier import ADMIN_TOKEN, FakeTokenVerifier  # noqa: E402


@pytest.fixture
def fake_queue() -> FakeQueueReservation:
    return FakeQueueReservation()


@pytest.fixture
def fake_token_verifier() -> FakeTokenVerifier:
    return FakeTokenVerifier()


@pytest.fixture
def module1(db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier):
    return build_module1(
        db, fake_clock, fake_id_generator, fake_queue, fake_token_verifier, ADMIN_TOKEN
    )
