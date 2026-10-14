# Revisión adversarial — Gate 9 (aplicación R4-01/R4-02, 2026-10-13, corrida 9)

- Fecha: 2026-10-13.
- Alcance: `.work/paquete-decisiones-F-H.md` § "Ronda 4" (R4-01 timestamp de baja, R4-02 `ErrorBody.rule_ids`) aplicada a `contracts.md` (§1 orden, §2 P4, §4 catálogo y nota envelope, §5), `ARCHITECTURE-SPINE.md` (AD-11), `ports-and-adapters.md` (§3, §5), `schemas/dto.py` y `schemas/openapi.yaml`. Foco: lo cambiado.
- Método: para cada decisión, dos implementaciones que obedecen al pie de la letra el texto NUEVO; si divergen en conducta observable dentro de `resolveEffectivePermissions`, `revokeCourseAccess` o `ingestRoster`, es hallazgo nuevo (serie G9-xx). Criterio: DEFERRED con responsable/fase y OPEN fuera de las 3 operaciones no bloquean.
- Fuentes externas: RFC 3339 §5.6 (nota: "T" y "Z" pueden ser minúsculas), §5.6 ABNF (`time-secfrac = "." 1*DIGIT`, `time-second` admite 60, `time-numoffset` admite `-`), §4.3 (`-00:00` = offset local desconocido).
- Nota de independencia: esta revisión la hizo el mismo agente que aplicó los cambios, sin subagentes independientes (no se pidió explícitamente). Reduce la independencia que el skill exige; el estudiante debe considerarlo al triagear.

## Cierres R4 (verificación de cada par)

| ID | Estado | Nota |
| --- | --- | --- |
| R4-01 | ABIERTO (residuo, bloquea) | La gramática cierra el caso de `Z`/`+00:00` pero deja 4 pares 200-vs-400 (G9-01). |
| R4-02 | PARCIAL (bloquea) | El campo existe y no se adjunta DTO en 400, pero el orden de precedencia y la forma null/ausente quedan abiertos (G9-02, G9-03). |

## Hallazgos nuevos

### G9-01 — Gramática de `timestamp` de baja: residuos RFC 3339. Severidad media-alta. BLOQUEA.

- Texto obedecido: R4-01 ("RFC 3339 `date-time` con zona UTC obligatoria: `YYYY-MM-DDTHH:MM:SS` + fracción opcional de 1 a 6 dígitos + (`Z` o `+00:00`); cualquier otro offset, fecha sin hora o forma no RFC 3339 → 400").
- Pares divergentes (ambos `revokeCourseAccess`, mismo texto):
  1. Minúsculas: `2026-09-23t15:04:05z`. RFC 3339 §5.6 lo declara válido; la unidad A (regex en mayúsculas) → 400, la unidad B (parser RFC 3339) → 200/`ALREADY_REVOKED`.
  2. Offset `-00:00`. RFC 3339 §4.3 lo define como offset local desconocido, válido. A → 400 (no es `+00:00`); B → 200.
  3. Segundo 60 (`23:59:60Z`). ABNF `time-second` admite 00-60. A (datetime) → 400; B → 200.
  4. Fecha fuera de calendario (`2026-02-30T…Z`). ABNF lo acepta; la validación semántica no está fijada. A → 400; B (solo ABNF) → 200.
  5. Fracción de 7–9 dígitos. RFC-válida, fuera de "1 a 6"; el texto no dice si es 400 o si se normaliza, y la normalización a 6 dígitos (truncar o redondear) no está fijada. Dos unidades persisten valores distintos.
- Propuesta de cierre (no aplicada): enumerar la gramática exacta (mayúsculas o minúsculas, `-00:00` sí/no, segundo 60 sí/no, validación de calendario, fracción >6 dígitos → 400 o truncado). Requiere triage humano.

### G9-02 — Precedencia de errores de sintaxis en `ingestRoster` no definida. Severidad media. BLOQUEA.

- Texto obedecido: R4-02 ("`rule_ids` ordenado por precedencia, el primero == `code`") + contracts §3 P1 (`term`) y P2 (estructura/columnas/encoding/tamaño de lote).
- Par: `POST …/roster?term=2026-fall` (fuera de patrón) con un CSV de 0 filas. Unidad A aplica P1 primero → `code: MALFORMED_TERM`, `rule_ids: [MALFORMED_TERM, BATCH_EMPTY]`. Unidad B aplica P2 primero → `code: BATCH_EMPTY`. El `code` principal diverge.
- La numeración P1..P4 no fija precedencia entre reglas de sintaxis de distinto paso; §3-Q1 solo ordena `batch_id` respecto de auth/tamaño/UTF-8/estructura/`term`.
- Propuesta de cierre (no aplicada): fijar el orden de `MALFORMED_TERM` frente a `MALFORMED_BATCH`/`BATCH_EMPTY` y `BATCH_TOO_LARGE`.

### G9-03 — `rule_ids` ausente se serializa como `null`. Severidad media. BLOQUEA.

- Evidencia reproducida en esta corrida: `dto.ErrorBody(... code='MALFORMED_DROP_TIMESTAMP').model_dump_json()` → `…,"code":"MALFORMED_DROP_TIMESTAMP","rule_ids":null}`. Con dos reglas: `"rule_ids":["MALFORMED_DROP_REASON","MALFORMED_DROP_TIMESTAMP"]`.
- Conflicto: R4-02 dice "presente solo cuando falla más de una regla" (ausente, no null); `openapi.yaml` declara `rule_ids` como `type: array` sin nullable (un null lo invalida). `dto.py` usa `list[str] | None = Field(default=None)`, que permite null y lo emite por defecto en Pydantic v2.
- Patrón preexistente: `ExplanationDTO.threshold` (`str | None`) tiene el mismo comportamiento; el problema es del convenio de DTO, no solo de R4-02.
- Par: unidad que serializa con `model_dump_json()` directo (null) vs unidad que omite la clave (conforme a OpenAPI). Divergencia de forma del cuerpo 400/401/403/404 en las tres operaciones.
- Propuesta de cierre (no aplicada, requiere decisión): exclusión de nulos en la serialización de `ErrorBody` (regla de adapter) o declarar `nullable` y cambiar el texto de R4-02. Mi edición solo agregó tipos y descripción; no añadí lógica.

### G9-04 — Propagación incompleta de la gramática R4-01. Severidad baja. NO bloquea.

- Quedan en "ISO-8601 UTC" sin la gramática nueva: `contracts.md` l.32 (paso 2 de orden), l.61 (P4, cabecera del párrafo), l.117 (detalle `Drop timestamp must be ISO-8601 UTC.`), l.166; `ARCHITECTURE-SPINE.md` l.65 (AD-09, mismo texto que R3-02); `ports-and-adapters.md` l.158; `openapi.yaml` l.229; `schemas/dto.py` l.15 y l.164 (comentario).
- Fuera de la lista de archivos que pidió el encargo para el spine (solo envelope 400), por lo que no se editaron. Se recomienda alinearlos en un cambio de texto cuando se cierre G9-01.

### G9-05 — Nombre `rule_ids` reutilizado con contenido distinto. Severidad baja. NO bloquea.

- `ExplanationDTO.rule_ids` contiene citas AD-n (H-23, `min_length=1`, ejemplo `AD-01`); `ErrorBody.rule_ids` (R4-02) contiene códigos del catálogo, con el primero == `code`. Una unidad podría poner `AD-09` en `ErrorBody.rule_ids`. Sugerencia: restringir los elementos a `ErrorCode` en el schema o renombrar el campo. No se cambió.

### G9-06 — Observación preexistente fuera de las ediciones R4. Severidad baja. NO bloquea.

- `POST /authorize` con body incompleto (falta `action` o `user_id`) no tiene código 400 en el catálogo §4: ningún código de los 7 de 400 describe "campo ausente". Dos unidades podrían devolver códigos distintos. No es consecuencia de R4; se registra para triage.

## Verificación por operación (sin divergencia nueva)

- `resolveEffectivePermissions`: el 400 público tiene una sola regla de sintaxis (`MALFORMED_RESOURCE_ARN`, o G9-06 para body incompleto). `INVALID_AT` solo existe en la entrada interna/test/replay (AD-09), así que R4-02 no genera dos reglas en la vía pública. Sin divergencia nueva.
- `revokeCourseAccess`: R4-02 `MALFORMED_DROP_REASON` primero + `MALFORMED_DROP_TIMESTAMP` en `rule_ids` converge; el riesgo está en G9-01 y G9-03.

## Veredicto del lens

**NO ROBUSTO.** Tres divergencias observables dentro de las 3 operaciones (G9-01, G9-02, G9-03) bloquean. Cuatro hallazgos de baja severidad no bloquean. No se declara PASS.

## Plan de triage (humano)

1. G9-01: enumerar la gramática exacta (minúsculas, `-00:00`, segundo 60, calendario, fracción >6).
2. G9-02: fijar precedencia `MALFORMED_TERM` vs `MALFORMED_BATCH`/`BATCH_EMPTY`.
3. G9-03: elegir omitir-cuando-ausente (adapter) o declarar nullable.
