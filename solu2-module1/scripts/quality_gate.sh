#!/bin/bash
# quality_gate.sh — Equivalente local del CI quality gate (solu2-module1).
# Uso: ./scripts/quality_gate.sh   (desde solu2-module1/)
# Usa el .venv local (solu2-module1/.venv, Python 3.11). No toca red salvo
# `pip install -r requirements-dev.txt` si se pide con --install.
# Etapas (mismas que .github/workflows/quality-gate.yml):
#   1. lint pureza app/domain/ (H-25) ............ BLOQUEANTE
#   2. validar DDL en sqlite3 :memory: ........... BLOQUEANTE
#   3. importar schemas/dto.py ................... BLOQUEANTE
#   4. parsear openapi.yaml ...................... BLOQUEANTE
#   5. pytest verde (not atdd) ................... BLOQUEANTE
#   6. ATDD collect-only ......................... BLOQUEANTE
#   7. ATDD RED esperado (solo NotImplementedError)  (distingue RED de colección/import/sintaxis)
#   8. cobertura app/domain/ ≥90% ................ INFORMATIVA
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "FALTA .venv: $PY no existe. Crea solu2-module1/.venv (Python 3.11) primero."
  exit 2
fi
if [ "${1:-}" = "--install" ]; then
  "$PY" -m pip install -r requirements-dev.txt
fi

PASS=0; FAIL=0
ok()   { echo "OK: $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL(BLOQUEANTE): $1"; FAIL=$((FAIL+1)); }

echo "== quality_gate local — $($PY --version) — $ROOT =="

# — Etapa 1 (BLOQUEANTE): pureza domain/ H-25 (AST).
if "$PY" - <<'EOF'; then
import ast, pathlib, sys
BANNED_IMPORTS = {"fastapi", "sqlalchemy", "sqlite3", "random", "secrets", "uuid", "time", "os"}
BANNED_ATTRS = {"now", "utcnow", "today"}
errors = []
for path in sorted(pathlib.Path("app/domain").glob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if (a.name or "").split(".")[0] in BANNED_IMPORTS:
                    errors.append(f"{path}:{node.lineno} import prohibido (H-25): {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_IMPORTS:
                errors.append(f"{path}:{node.lineno} from-import prohibido (H-25): {node.module}")
        elif isinstance(node, ast.Attribute):
            if node.attr == "urandom" and isinstance(node.value, ast.Name) and node.value.id == "os":
                errors.append(f"{path}:{node.lineno} os.urandom prohibido (H-25)")
            if node.attr in BANNED_ATTRS:
                errors.append(f"{path}:{node.lineno} reloj prohibido (H-25): .{node.attr}()")
if errors:
    print("PUREZA domain/ ROTA (H-25):")
    print("\n".join(errors))
    sys.exit(1)
print("pureza domain/ (H-25)")
EOF
  ok "Etapa 1 — pureza domain/ (H-25)"
else
  fail "Etapa 1 — pureza domain/ (H-25)"
fi

# — Etapa 2 (BLOQUEANTE): DDL en :memory:.
if "$PY" - <<'EOF'; then
import sqlite3
ddl = open("planning/detailed-design/schemas/001_module1_schema.sql", encoding="utf-8").read()
conn = sqlite3.connect(":memory:")
conn.executescript(ddl)
tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
required = {"identities", "subjects", "roles", "subject_memberships",
            "escalation_tickets", "subject_credentials", "audit_ledger",
            "audit_ledger_metadata", "audit_events"}
missing = required - tables
assert not missing, f"tablas faltantes: {sorted(missing)}"
print(f"DDL :memory_ tablas={sorted(tables)}")
EOF
  ok "Etapa 2 — DDL válida en :memory:"
else
  fail "Etapa 2 — DDL válida en :memory:"
fi

# — Etapa 3 (BLOQUEANTE): importar dto.py.
if "$PY" -c "import sys; sys.path.insert(0, 'planning/detailed-design/schemas'); import dto; print('dto.py importa:', [n for n in ('AuthorizeRequest','AuthorizeResponse','DenyBody','RevokeRequest','RevokeResponse','RosterIngestRequest','RosterIngestResponse','RosterRejectedManifest','ErrorBody','ExplanationDTO') if hasattr(dto, n)])"; then
  ok "Etapa 3 — schemas/dto.py importa"
else
  fail "Etapa 3 — schemas/dto.py importa"
fi

# — Etapa 4 (BLOQUEANTE): parsear openapi.yaml (pyyaml si está; si no, chequeo estructural grep).
if "$PY" -c "import yaml" 2>/dev/null; then
  if "$PY" - <<'EOF'; then
import yaml
spec = yaml.safe_load(open("planning/detailed-design/schemas/openapi.yaml", encoding="utf-8"))
ops = {m.get("operationId") for p in spec.get("paths", {}).values() for m in p.values() if isinstance(m, dict)}
required = {"resolveEffectivePermissions", "revokeCourseAccess", "ingestRoster"}
missing = required - ops
assert not missing, f"operationIds faltantes: {sorted(missing)}"
print(f"openapi.yaml operationIds={sorted(ops)}")
EOF
    ok "Etapa 4 — openapi.yaml parsea (pyyaml)"
  else
    fail "Etapa 4 — openapi.yaml parsea (pyyaml)"
  fi
else
  echo "AVISO: sin pyyaml en .venv (no está en requirements-dev.txt); chequeo estructural por grep (degradado, no inventa parseo)."
  if grep -q "^openapi:" planning/detailed-design/schemas/openapi.yaml \
    && grep -q "operationId: resolveEffectivePermissions" planning/detailed-design/schemas/openapi.yaml \
    && grep -q "operationId: revokeCourseAccess" planning/detailed-design/schemas/openapi.yaml \
    && grep -q "operationId: ingestRoster" planning/detailed-design/schemas/openapi.yaml; then
    ok "Etapa 4 — openapi.yaml estructural (grep, pyyaml ausente)"
  else
    fail "Etapa 4 — openapi.yaml estructural (grep, pyyaml ausente)"
  fi
fi

# — Etapa 5 (BLOQUEANTE): pytest verde sin ATDD.
if "$PY" -m pytest -m "not atdd" -q; then
  ok "Etapa 5 — pytest (not atdd) verde"
else
  fail "Etapa 5 — pytest (not atdd) verde"
fi

# — Etapa 6 (BLOQUEANTE): ATDD debe colectarse (colección/import/sintaxis rompen el gate).
# Código 5 = "no tests collected" (test/atdd/ aún vacío): NO es error de colección.
ATDD_OUT="$("$PY" -m pytest -m atdd -q 2>&1)"
ATDD_CODE=$?
echo "$ATDD_OUT"
COLLECT_OUT="$("$PY" -m pytest -m atdd --collect-only -q 2>&1)"
COLLECT_CODE=$?
if [ $COLLECT_CODE -eq 0 ] || [ $COLLECT_CODE -eq 5 ]; then
  ok "Etapa 6 — ATDD collect-only sin errores (código $COLLECT_CODE)"
else
  fail "Etapa 6 — ATDD collect-only sin errores (código $COLLECT_CODE)"
  echo "--- detalle collect-only ---"
  echo "$COLLECT_OUT" | tail -n 20
fi

# — Etapa 7 (RED esperado): rojo SOLO por NotImplementedError.
# Sin tests ATDD todavía (test/atdd/ vacío): pytest sale código 5 "no tests
# collected/ran". Eso NO es verde ni es RED con NotImplementedError: se reporta
# como PENDIENTE (la suite ATDD aún no existe) y NO rompe el gate; en cuanto
# existan tests ATDD, el gate exige rojo-por-NotImplementedError y rechaza
# colección/import/sintaxis.
# Los tests atdd-red son xfail(raises=NotImplementedError, strict=True): pytest sale con 0
# y reporta "N xfailed". Un XPASS (verde inesperado) cuenta como failed en modo strict.
if echo "$ATDD_OUT" | grep -qE "[0-9]+ xfailed" && ! echo "$ATDD_OUT" | grep -qE "[0-9]+ (failed|error)"; then
  ok "Etapa 7 — ATDD RED esperado (xfail estricto raises=NotImplementedError)"
elif [ $ATDD_CODE -eq 0 ]; then
  echo "AVISO: ATDD en VERDE inesperado en RED-phase: hay implementación; recalibrar gate a GREEN-phase."
  ok "Etapa 7 — ATDD RED esperado (verde inesperado, aviso)"
elif [ $ATDD_CODE -eq 5 ] || echo "$ATDD_OUT" | grep -qE "no tests ran|no tests collected"; then
  echo "PENDIENTE: test/atdd/ vacío (código $ATDD_CODE): aún no hay suite ATDD que poner en RED. No bloquea."
  ok "Etapa 7 — ATDD RED esperado (pendiente: sin tests ATDD)"
elif echo "$ATDD_OUT" | grep -qE "ERROR|SyntaxError|ModuleNotFoundError|ImportError|error.*(collect|import)"; then
  fail "Etapa 7 — ATDD con error de colección/import/sintaxis (ROMPE el gate, no es RED esperado)"
elif echo "$ATDD_OUT" | grep -q "NotImplementedError"; then
  ok "Etapa 7 — ATDD en RED esperado por NotImplementedError"
else
  fail "Etapa 7 — ATDD en rojo por causa DISTINTA de NotImplementedError (ROMPE el gate)"
fi

# — Etapa 8 (INFORMATIVA): cobertura domain/ ≥90%. No bloquea hasta implementación.
echo "--- Etapa 8 (INFORMATIVA): cobertura app/domain/ ≥90% ---"
if "$PY" -m pytest -m "not atdd" -q --cov=app/domain --cov-report=term-missing --cov-fail-under=90; then
  echo "INFO: cobertura domain/ ≥90% alcanzada (informativa)."
else
  echo "INFO: cobertura domain/ <90% o sin datos — esperado sin implementación; NO bloquea (informativa)."
fi

echo "== resumen: PASS=$PASS FAIL=$FAIL =="
if [ "$FAIL" -ne 0 ]; then
  echo "GATE LOCAL: ROJO ($FAIL etapa(s) bloqueante(s) en fallo)."
  exit 1
fi
echo "GATE LOCAL: VERDE (etapas bloqueantes OK; ATDD en RED-esperado/pendiente; cobertura informativa)."
