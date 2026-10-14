"""test_harness_smoke.py — Humo del harness (fixtures). No es ATDD.

Solo verifica el scaffold: flota simulada, DDL migrada y reloj falso.
Debe pasar en verde.
"""


def test_seed_fleet_topology(seed_fleet):
    nodes = seed_fleet["nodes"]
    assert len(nodes) == 32  # 31 workstations + 1 servidor central
    gpus = [g for n in nodes for g in n["gpus"]]
    assert len(gpus) == 33
    assert sum(g["vram_gb"] for g in gpus) == 31 * 24 + 2 * 48
    assert all(n["status"] == "HEALTHY" for n in nodes)
    assert all(g["status"] == "HEALTHY" for g in gpus)


def test_db_has_ddl_tables(db):
    tables = {
        r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    for t in (
        "identities",
        "subjects",
        "roles",
        "subject_memberships",
        "escalation_tickets",
        "subject_credentials",
        "audit_ledger",
        "audit_ledger_metadata",
        "audit_events",
    ):
        assert t in tables


def test_fake_clock_advances(fake_clock):
    assert fake_clock.now() == "2026-09-23T15:04:05.000000Z"
    assert fake_clock.advance(3600) == "2026-09-23T16:04:05.000000Z"


def test_fake_id_generator_deterministic(fake_id_generator):
    assert fake_id_generator.new_id("roster") == "roster-00000001"
    assert fake_id_generator.new_id("roster") == "roster-00000002"
