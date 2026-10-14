"""Puerto outbound TelemetryPort (R8-06): métricas operativas, sin decisiones de negocio.

emit_metric(name, value, labels). Módulo 1 solo emite métricas operativas (p. ej.
scheduler_sweep_deferred_total); no consume telemetría GPU ([ASSUMPTION-01] PRD).
Fake: sim_telemetry (test/conftest.py). Solo firma; cero lógica.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class TelemetryPort(ABC):
    @abstractmethod
    def emit_metric(self, name: str, value: float, labels: dict[str, str]) -> None:
        """Registra una métrica operativa."""
        raise NotImplementedError("TelemetryPort.emit_metric: stub, pendiente ATDD")
