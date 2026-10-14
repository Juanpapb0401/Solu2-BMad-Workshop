# Fixtures obligatorias del Módulo 1

Rutas relativas a `solu2-module1/`. Las líneas indican la definición en el archivo fuente.

## Fixtures pytest (`test/conftest.py`)

| Fixture | Definición | Propósito |
|---|---|---|
| `fake_clock` | `test/conftest.py:54` (clase `FakeClock` en la línea 33) | Reloj inyectado (`now_utc()`); sustituye a `datetime.now` en pruebas. |
| `fake_id_generator` | `test/conftest.py:71` (clase `FakeIdGenerator` en la línea 58) | Generador de IDs determinista. |
| `seed_fleet` | `test/conftest.py:76` | Flota simulada PRD §1.1: 31 nodos × 1 GPU 24 GB + 1 nodo × 2 GPUs 48 GB, todos HEALTHY (datos sin hardware). |
| `sim_telemetry` | `test/conftest.py:144` (clase `SimTelemetry` en la línea 102) | Telemetría simulada de GPU; sin hardware real. |
| `db` | `test/conftest.py:149` | SQLite temporal migrada con `planning/detailed-design/schemas/001_module1_schema.sql`, nueva por prueba. |
| `explain_assert` | `test/conftest.py:181` | Helper AD-11: verifica que la decisión traiga `ExplanationDTO` con `rule_ids` no vacío y al menos un valor observado. |

Fixture adicional: `edge_case_seeds` (`test/conftest.py:209`), que depende de `db`.

## Test doubles (`test/fakes/`)

| Archivo | Clase o función | Línea | Uso |
|---|---|---|---|
| `fake_credential_delivery.py` | `FakeCredentialDelivery` | 12 | Doble del puerto de entrega de credenciales. |
| `fake_failing_ports.py` | `RaisingClock` | 10 | Reloj que falla, para fail-closed (503). |
| `fake_failing_ports.py` | `RaisingIdGenerator` | 20 | Generador de IDs que falla. |
| `fake_id_generator.py` | `ThreadSafeIdGenerator` | 11 | Generador de IDs seguro para concurrencia. |
| `fake_queue.py` | `FakeQueueReservation` | 14 | Doble de la reserva de cola (`QueueReservation`). |
| `fake_token_verifier.py` | `FakeTokenVerifier` | 21 | Doble del verificador de tokens. |
| `world.py` | helpers (`add_identity`, `add_membership`, `add_credential`, `add_ticket`, `seed_student_pair`, `counts`, `events`, `ticket_status`, etc.) | 61–173 | Inserción de filas que respeta el DDL (CHECK, UNIQUE, FK) y consultas de verificación. |

`test/fakes/__init__.py` solo contiene la docstring del paquete.
