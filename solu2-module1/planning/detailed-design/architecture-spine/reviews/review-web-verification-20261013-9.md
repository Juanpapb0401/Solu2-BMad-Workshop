# Web-verification — Gate 9, Ronda 4 (R4-01/R4-02, 2026-10-13, corrida 9)

- Fecha: 2026-10-13.
- Alcance: verificar que R4-01/R4-02 no introducen tecnología nueva y que la gramática de R4-01 que dice citar "RFC 3339" coincide con la norma.
- Veredicto: **PASS** para stack y dependencias. Para R4-01, la verificación contra la norma encuentra residuos que se reportan en G9-01 (adversarial), no en este lens.

## Stack y dependencias

- Ninguna tecnología nueva. `rule_ids` y la gramática de timestamp son texto y tipos de Pydantic/OpenAPI ya presentes.
- Versiones del entorno (sin cambios): Python 3.11.14, FastAPI 0.143.0, Pydantic 2.14.1, SQLAlchemy 2.0.54, SQLite WAL (`busy_timeout 5000`) según `sqlite3 :memory:` (`memory`, 5000).

## Verificación de la norma (RFC 3339, consultada en rfc-editor.org)

- §5.6 NOTA: "the "T" and "Z" characters in this syntax may alternatively be lower case "t" or "z" respectively." → `2026-09-23t15:04:05z` es RFC 3339 válido. R4-01 solo lista `T` y `Z` (mayúsculas). Residuo: G9-01 punto 1.
- §5.6 ABNF: `time-secfrac = "." 1*DIGIT` (sin límite de 6 dígitos); `time-numoffset = ("+" / "-") time-hour ":" time-minute`; `time-second = 2DIGIT ; 00-58, 00-59, 00-60 based on leap second rules`. → 7+ fracción y segundo 60 son RFC-válidos; R4-01 los excluye implícitamente sin decirlo (G9-01 puntos 3 y 5).
- §4.3: el offset `-00:00` representa hora local desconocida (válido en RFC 3339); R4-01 solo acepta `Z`/`+00:00` (G9-01 punto 2).
- §5.6 ABNF: los días se validan "based on month/year", es decir, la validez de calendario es semántica (G9-01 punto 4).

## Límites

- No se ejecutó TEA ni `bmad-build`. No hubo búsqueda de versiones nuevas porque no hay tecnología nueva.
- La fuente consultada fue un resumen por modelo pequeño (WebFetch) del RFC; las citas literales de la nota de minúsculas, del ABNF de `time-second` y de `-00:00` son las que devolvió la herramienta y deben confirmarse leyendo el RFC original si el estudiante lo pide.
