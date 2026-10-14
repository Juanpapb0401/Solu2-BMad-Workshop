# Review rubric walker — Gate 9, Ronda 4 (R4-01/R4-02, 2026-10-13, corrida 9)

- Fecha: 2026-10-13.
- Alcance: aplicación de R4-01 y R4-02 (`.work/paquete-decisiones-F-H.md` § Ronda 4, aprobada por el estudiante 2026-10-13) en `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/dto.py`, `schemas/openapi.yaml`, y 2 entradas nuevas al final de `ai-log/decision-log-solu2.md`.
- Criterio: los 3 `low` del lint por `{subject_id}`/`{student_id}` (ARCHITECTURE-SPINE.md l.65) son falsos positivos conocidos. DEFERRED con responsable/fase y OPEN fuera de las 3 operaciones NO bloquean.
- Nota de independencia: revisión inline por el mismo agente que aplicó los cambios (sin subagentes independientes).

## Veredicto del lens: CONDITIONAL

R4-01 y R4-02 quedan aplicados con marca `[ADOPTED 2026-10-13, estudiante] (R4-0x)`. Quedan dos hallazgos que bloquean (G9-01 gramática, G9-03 null vs ausente, ambos del lens adversarial), dos de los que bloquea G9-02 (precedencia en ingest, también adversarial), y un hallazgo de higiene que no bloquea (G9-04).

## Verificación de los cambios (1 por 1)

- R4-01 (gramática timestamp de baja): APLICADO en `contracts.md` §2-P4 (gramática RFC 3339, persistencia `YYYY-MM-DDTHH:MM:SS.ffffffZ`), §4 fila `MALFORMED_DROP_TIMESTAMP` (disparo); `ports-and-adapters.md` §3 (descripción del body); `schemas/dto.py` `RevokeRequest.timestamp` (description); `schemas/openapi.yaml` `RevokeRequest.timestamp` (description). Residuos "ISO-8601 UTC" fuera de estos puntos: ver G9-04.
- R4-02 (`ErrorBody.rule_ids` opcional): APLICADO en `schemas/dto.py` (campo `list[str] | None`, descripción), `schemas/openapi.yaml` (propiedad no requerida, `type: array`, descripción), `contracts.md` §4 (nota envelope: solo doble fallo de sintaxis, sin ExplanationDTO en 400), `ARCHITECTURE-SPINE.md` AD-11 (Rule), `ports-and-adapters.md` §5 (fila "Explicación con regla citada"). Sin cambio en AD-01..AD-07.
- Decision-log: 2 entradas nuevas (R4-01, R4-02) al final con el formato existente, hallazgo origen `architecture-spine/reviews/review-adversarial-20261013-8.md`, línea de propuesta indicada por el encargo. Corregidas dos etiquetas "B" que no estaban en la decisión aprobada.
- Memlog: entrada `decision` añadida (`entries: 106`).
- AD-01..AD-07 y Plan-2: sin edición en esta corrida; `planning/` sin tocar.

## Hallazgos nuevos del rubric

- G9-03 (medio, BLOQUEA; corroborado por adversarial): `ErrorBody.rule_ids` ausente se serializa como `null` con Pydantic v2 (`model_dump_json()` reproducido), contrario a "presente solo cuando" y a OpenAPI sin nullable. Mismo patrón preexistente en `ExplanationDTO.threshold`.
- G9-04 (bajo, NO bloquea): la frase "ISO-8601 UTC" para el timestamp de baja sigue en `contracts.md` l.32, l.61, l.117 (detalle), l.166; `ARCHITECTURE-SPINE.md` l.65 (AD-09); `ports-and-adapters.md` l.158; `openapi.yaml` l.229; `dto.py` l.15 y l.164. No se editaron por alcance.

## Qué no cambia

Lint sin cambios (3 low de falso positivo). Stack sin cambios. AD-08..AD-13 intactos salvo la frase R4-02 en AD-11.

## Pendiente de triage humano

G9-01 y G9-02 (gramática exacta y precedencia de ingest, ver adversarial) y G9-03 (decisión de serialización). Hasta entonces, Fase 1 no se marca completa.
