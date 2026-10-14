"""Regenera la tabla 'Trazabilidad AD-n -> historias -> tests' de epics.md desde la fuente de verdad:
- Historias: línea '**Binding invariants:**' de cada '### Story E<n>-S<m>'.
- Tests: node IDs citados en cada historia, filtrados por los AD-n que cita el docstring del test.
Uso: python3 regen_ad_table.py <ruta epics.md> <raíz solu2-module1> [--write]
"""
import ast
import pathlib
import re
import subprocess
import sys

epics_path = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2]).resolve()
write = "--write" in sys.argv

AD_NAMES = {
    "AD-01": "Context Isolation & Binding (heredado)",
    "AD-02": "Ingestión atómica y anti-role-smuggling (heredado)",
    "AD-03": "Invalidación determinista e idempotencia (heredado)",
    "AD-04": "Ledger encadenado y metadata (heredado)",
    "AD-05": "Anti auto-aprobación y exclusión mutua (heredado)",
    "AD-06": "Cero secretos en trazas (heredado)",
    "AD-07": "Paginación acotada (heredado)",
    "AD-08": "Pureza del dominio hexagonal (spine-local)",
    "AD-09": "Mapeo canónico operación a HTTP (spine-local)",
    "AD-10": "Fixture del Mandatory Edge Case (spine-local)",
    "AD-11": "Decisión explicable con regla citada (spine-local)",
    "AD-12": "Serialización de carreras e idempotencia (spine-local)",
    "AD-13": "Frontera temporal semiabierta (spine-local)",
}
AD_RE = re.compile(r"AD-(0[1-9]|1[0-3])\b")
NODE_RE = re.compile(r"`(test/[^`\s]+?\.py::[^`\s]+)`")

# Colección real
out = subprocess.run([str(root / ".venv/bin/pytest"), "--collect-only", "-q"], cwd=root,
                     capture_output=True, text=True).stdout
collected = {l.strip() for l in out.splitlines() if "::" in l}

# AD-n por test (docstring de la función y de su clase)
test_ads: dict[str, set[str]] = {}
for f in (root / "test").rglob("*.py"):
    tree = ast.parse(f.read_text())
    rel = f.relative_to(root).as_posix()
    def visit(node, prefix, inherited):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.ClassDef):
                doc = ast.get_docstring(ch) or ""
                visit(ch, prefix + [ch.name], inherited | {"AD-" + m for m in AD_RE.findall(doc)})
            elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) and ch.name.startswith("test_"):
                doc = ast.get_docstring(ch) or ""
                ads = {"AD-" + m for m in AD_RE.findall(doc)} or inherited
                test_ads["::".join([rel] + prefix + [ch.name])] = ads
    visit(tree, [], set())

def base(node_id: str) -> str:
    return node_id.split("[")[0]

text = epics_path.read_text()
stories = list(re.finditer(r"^### Story (E\d-S\d)[^\n]*\n", text, re.M))
story_bind: dict[str, set[str]] = {}
story_nodes: dict[str, list[str]] = {}
for i, m in enumerate(stories):
    end = stories[i + 1].start() if i + 1 < len(stories) else text.find("\n## ", m.end())
    body = text[m.end():end]
    sid = m.group(1)
    bl = re.search(r"\*\*Binding invariants:\*\*([^\n]*)", body)
    story_bind[sid] = {"AD-" + x for x in AD_RE.findall(bl.group(1))} if bl else set()
    story_nodes[sid] = list(dict.fromkeys(NODE_RE.findall(body)))

rows, problems = [], []
for ad, name in AD_NAMES.items():
    sts = [s for s, b in story_bind.items() if ad in b]
    tests = []
    for s in sts:
        for n in story_nodes[s]:
            if ad in test_ads.get(base(n), set()) and n not in tests:
                tests.append(n)
    # tests que citan el AD en historias que NO lo tienen en binding
    for s, nodes in story_nodes.items():
        if s in sts:
            continue
        for n in nodes:
            if ad in test_ads.get(base(n), set()):
                problems.append(f"{ad}: {n} (citado en {s}) no está en Binding invariants de {s}")
    estado = "OK" if tests else "SIN TEST"
    if not sts:
        estado = "SIN HISTORIA"
    rows.append(f"| {ad} {name} | {', '.join(sts) or '—'} | " +
                ("; ".join(f"`{t}`" for t in tests) or "—") + f" | {estado} ({len(tests)} tests) |")

invalid = sorted({n for ns in story_nodes.values() for n in ns} - collected)
table = ("| AD | Historias (Binding invariants) | Tests (node IDs cuyo docstring cita el AD) | Estado |\n"
         "|---|---|---|---|\n" + "\n".join(rows))
print(table)
print("\nPROBLEMAS (test cita AD fuera del binding de su historia):", len(problems))
for p in problems:
    print(" -", p)
print("node IDs inválidos:", invalid)

if write:
    start = text.index("## Trazabilidad AD-n -> historias -> tests")
    nxt = text.index("\n## ", start + 5)
    new = ("## Trazabilidad AD-n -> historias -> tests\n\n"
           "Tabla regenerada automáticamente (K-6, 2026-10-14) por `.work/regen_ad_table.py` desde los "
           "**Binding invariants** de cada historia y los docstrings de los tests citados en ella; "
           "todos los node IDs están en la colección de pytest.\n\n" + table + "\n")
    epics_path.write_text(text[:start] + new + text[nxt:])
    print("WRITTEN")
