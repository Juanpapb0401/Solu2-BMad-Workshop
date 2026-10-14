# Review Rubric — Sync Fase 2 Amelia (corrida 5, 2026-10-13)

- Fecha: 2026-10-13
- Rol: rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura; no se editó ningún fuente salvo este reporte).
- Alcance: los 5 companions Fase 2 actualizados — `ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml` — contra `contracts.md`, `ARCHITECTURE-SPINE.md`, `resultados-interaccion.md` (auditoría Amelia), Gate 4 (`validation-gate-20261013-4.md`, rubric F-01..F-06, adversarial H-14..H-26). No se toca AD-01..AD-07 ni documentos Plan-2. No se cambia el Gate 4.
- Escala: ROBUSTO / CONDITIONAL / NOT READY (criterio sin relajar).
- Veredicto del lens: **CONDITIONAL** (delta Fase 2 correcto; F-01..F-06 y H-14..H-26 siguen OPEN por diseño).

## Veredicto

**CONDITIONAL.** La actualización aplica los cambios documentales mínimos de la auditoría sin cerrar por suposición: codec parcial con H-14/H-15 explícitos, H-16 explícito, H-17..H-26 marcados OPEN en los artefactos correspondientes, matriz `term` + brecha contrato/prueba, `subject_id` path autoridad, 422 OPEN sin `Accept` por defecto, `RosterRejectedManifest` en DTO alineado al contrato 422 sin lógica ni validadores nuevos, `drop_reason` con H-19 sin validador, DDL con separación físico/conductual sin triggers ni CHECKs nuevos, IDs/email sin patrones inventados. F-01..F-06, matriz `roles_matrix.json`, cola, scheduler, `timestamp` de baja, TTL, `COMPLETED`, NFR, reemisión y colisión `batch_id` siguen pendientes por diseño. Eso impide ROBUSTO y sostiene el NO PASS global. No llega a NOT READY: sin debilitamiento heredado, sin operaciones fuera de las tres, sin matriz/capacidad/códigos inventados.

## Checklist punto por punto

1. Codec parcial H-14/H-15 — CUMPLE. `schemas/events.md:102-115` (`[ADOPTED parcial: solo frames null/string]` + `[OPEN H-14 alcance/enteros]` + `[OPEN H-15 génesis/unidad]`), `ports-and-adapters.md:§4` y `schemas/001_module1.sql:§7/comentarios` con la misma calificación; sin elegir opción.
2. OPEN H-16 — CUMPLE. `schemas/events.md:§1` + `ports-and-adapters.md:§3-§4` (momento pre/post-auth + reuse en tx separada de `roster.rejected`; sin decidir).
3. H-17..H-26 OPEN sin precedencias fijadas — CUMPLE. `ports-and-adapters.md:§1/§3/§5/§6`, `schemas/events.md:§1/§4`, DDL `subject_memberships`/envelope, `dto.py` (H-19/H-23/H-26 + `RosterRejectedManifest`), `openapi.yaml` (H-18/H-19/H-24/H-26 + matriz + 422 OPEN). Sin fijar precedencias ni comportamientos indefinidos.
4. Matriz `term` + brecha — CUMPLE. `schemas/openapi.yaml:POST roster` (JSON exige body y prohíbe query; CSV exige query y prohíbe body; ausente/extra/duplicado/discrepante → `MALFORMED_TERM` 400) + nota explícita de que OpenAPI no puede imponer la condición Content-Type↔query (brecha contrato/prueba).
5. `subject_id` autoridad — CUMPLE. `schemas/openapi.yaml:RosterIngestRequest` + `ports-and-adapters.md:§3` (path manda; body divergente → `MALFORMED_BATCH` 400).
6. 422 OPEN — CUMPLE. `schemas/openapi.yaml:RosterRejectedManifest` (RFC-7807 + `errors` + `batch_id` + `explanation` + conteos en 0 por contrato, sin imponer ceros por máquina) + `Unprocessable` (negociación JSON vs CSV OPEN, sin `Accept` por defecto).
7. `RosterRejectedManifest` en DTO — CUMPLE. `schemas/dto.py:RosterRejectedManifest` (RFC-7807 + `errors` + `batch_id` + `explanation` + conteos; solo tipa, sin lógica ni validadores nuevos).
8. `drop_reason` H-19 — CUMPLE. `schemas/dto.py:RevokeRequest` + `schemas/openapi.yaml:RevokeRequest` + `ports-and-adapters.md:§3` (`[OPEN H-19a blancos; H-19b intacto-vs-máscara]`; `Field`/`minLength` no hacen cumplir blancos ni máscara; sin validador).
9. DDL físico vs conductual — CUMPLE. `schemas/001_module1.sql:§7b` (FK solo `audit_events → audit_ledger`; igualdad `occurred_at==timestamp` y atomicidad como conducta `LedgerWriter`, sin `CHECK`/trigger; sin triggers ni restricciones nuevas). Tensión pre-existente registrada: `CHECK (expires_at > granted_at)` heredado convive con H-21c vacío como OPEN a nivel de evaluación; no se agrega ni se quita nada en esta corrida.
10. IDs/email sin patrones — CUMPLE. `schemas/dto.py` + `schemas/openapi.yaml` (sin regex inventada; boundary valida según contracts; pendiente lo no definido).
11. Pendientes conservados — CUMPLE. F-01..F-06, `roles_matrix.json`, capacidad/recuperación de cola, scheduler (frecuencia + crash), `timestamp` de baja, TTL, `COMPLETED`, NFR, reemisión, colisión `batch_id` siguen pendientes en `ports-and-adapters.md:§6` y `schemas/events.md:§4`.
12. Gate 4 intacto — CUMPLE. `architecture-spine/reviews/validation-gate-20261013-4.md` y lenses `-20261013-4` sin tocar; veredicto original NO PASS vigente; Fase 1 no completa.

## Hallazgos (sin suavizar)

- Ningún cierre accidental introducido por esta corrida.
- Tensión pre-existente H-21c: DDL `CHECK (expires_at > granted_at)` (heredado, no agregado aquí) hace no persistible un `ACTIVE` con intervalo vacío; H-21c se mantiene OPEN a nivel de evaluación y se registra sin decidir (ver reporte adversarial `-20261013-5`).
- F-01..F-06 persisten como bloqueantes/observaciones de Fase 1; no se re-juzgan aquí salvo para confirmar que la Fase 2 no los cierra por suposición.

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; ningún OPEN fue cerrado; no se ejecutó TEA ni `bmad-build`.*
