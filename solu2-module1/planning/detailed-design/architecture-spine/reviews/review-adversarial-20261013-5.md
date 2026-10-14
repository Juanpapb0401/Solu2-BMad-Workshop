# Revisión adversarial — Sync Fase 2 Amelia (2026-10-13, corrida 5)

- Fecha: 2026-10-13
- Rol: revisor adversarial, solo lectura salvo este archivo de reporte. No se modifica ningún otro archivo, no se cambia el criterio, no se oculta ningún hallazgo, no se propone ninguna edición, no se cierra ningún OPEN ni pendiente.
- Alcance: los 5 companions Fase 2 actualizados (`ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml`) + `EDGE-01` y Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»).
- Fuentes leídas (solo lectura): los 5 artefactos Fase 2 actualizados, `contracts.md`, `ARCHITECTURE-SPINE.md`, `resultados-interaccion.md`, Gate 4 (`validation-gate-20261013-4.md`, `review-adversarial-20261013-4.md` con H-14..H-26, `review-rubric-20261013-4.md` con F-01..F-06).
- Método: por cada H-14..H-26, dos unidades hipotéticas que obedecen al pie de la letra el texto actualizado; si divergen, el H sigue CORRECTAMENTE OPEN; si el texto impide una variante, es CIERRE ACCIDENTAL.
- Veredicto del lens: **NO ROBUSTO (H-14..H-26 persisten OPEN por diseño; 0 cierres accidentales introducidos en esta corrida; 1 tensión pre-existente H-21c registrada sin decidir).**

## Resumen

| ID | Foco | Estado en esta corrida |
| --- | --- | --- |
| H-14 | Codec: alcance + enteros | CORRECTAMENTE OPEN (`events.md:§3`, `ports-and-adapters.md:§4`, DDL comentarios) |
| H-15 | Codec: génesis + unidad | CORRECTAMENTE OPEN (mismo sitios; singleton 64 ceros es `audit_ledger_metadata`, no prev génesis) |
| H-16 | `request_now`: momento + 2ª tx | CORRECTAMENTE OPEN (`events.md:§1`, `ports §3-§4`; «worker nunca reconstruye» = worker persiste, no prohíbe `now` fresco del dominio) |
| H-17 | Barred vs mismatch | CORRECTAMENTE OPEN (`ports §3/§5`; mismo 403, distinto `code`) |
| H-18 | Percent-encoding + path | CORRECTAMENTE OPEN (`ports §3`, `openapi.yaml` operación roster + query `term`; path `type:string` sin pattern; canal contractual no máquina) |
| H-19 | `drop_reason` blancos + secreto | CORRECTAMENTE OPEN (`ports §3`, `dto.py:RevokeRequest`, `openapi.yaml:RevokeRequest`; `Field`/`minLength` no enforcean; sin validador) |
| H-20 | Smuggling sobre `DROPPED` | CORRECTAMENTE OPEN (`ports §5` fila roster + DDL `subject_memberships`; `UNIQUE` no fija scope) |
| H-21 | Histórico/persistido/futuro/vacío | CORRECTAMENTE OPEN en (a) y (b); (c) vacío con tensión pre-existente registrada (ver abajo) |
| H-22 | Lector WAL <200 ms | CORRECTAMENTE OPEN (`ports §5`; «coherente/confirmar» sin definir) |
| H-23 | Explicación multi-causa | CORRECTAMENTE OPEN (`dto.py:ExplanationDTO`, `openapi.yaml:ExplanationDTO`, `ports §5`; `minItems:1` permite 1..N) |
| H-24 | Header multiplicidad/vacío/CRLF | CORRECTAMENTE OPEN (`ports §3`, `openapi.yaml` header; `required` + `type:string` sin regla) |
| H-25 | Azar fuera de `random` | CORRECTAMENTE OPEN (`ports §1/§5`; lista literal no decide `uuid.uuid4()`/`os.urandom()`/`time.monotonic()`) |
| H-26 | `effective_role` case | CORRECTAMENTE OPEN (`dto.py:AuthorizeResponse`, `openapi.yaml:AuthorizeResponse`; `type:string` sin enum) |

## Tensión pre-existente H-21c (no introducida aquí)

- (a) Scheduler persistió `EXPIRED` + replay con `at` vigente y (b) `granted_at` futuro siguen OPEN (`ports-and-adapters.md:§5`, `events.md:§1`).
- (c) Intervalo vacío (`granted_at == expires_at` en `ACTIVE`): el DDL heredado `001_module1.sql: CHECK ((status NOT IN ('ACTIVE')) OR (expires_at > granted_at))` (pre-existente, no agregado en esta corrida) hace no persistible esa variante como `ACTIVE`. A nivel de evaluación el H-21c se mantiene OPEN y se registra sin decidir; no se agrega ni se quita ningún `CHECK`/trigger en esta corrida (verificado: 0 triggers; `PRAGMA foreign_key_list(audit_events)` = 1 hacia `audit_ledger`).
- DDL/dto verificados: 0 triggers nuevos; `dto.py` sin `@validator`/`field_validator`/`model_validator` (solo `Field`); `RosterRejectedManifest` solo tipa (RFC-7807 + `errors` + `batch_id` + `explanation` + conteos).

## Top 3 riesgos (persistentes por diseño)

1. H-14/H-15: mismo evento hashea distinto entre unidades conformes; verificación cruzada no portable.
2. H-19b: razón con `uai_live_…` intacta vs enmascarada (ledger con secreto en claro según variante).
3. H-21c: tensión DDL heredado vs evaluación del vacío; requiere triage humano, no suposición.

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; ningún OPEN fue cerrado; ninguna edición fue propuesta; no se ejecutó TEA ni `bmad-build`.*
