# Review Rubric — Ronda 2 Gate 6, G6-01/G6-02/R2-01 (corrida 7, 2026-10-13)

- Fecha: 2026-10-13
- Rol: rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura; no se editó ningún fuente salvo este reporte).
- Alcance: `.work/paquete-decisiones-F-H.md` § "Ronda 2 — hallazgos del Gate 6" (G6-01, G6-02, R2-01, APROBADO por el estudiante) aplicado a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml`, `schemas/roles_matrix.v0.json` y `ai-log/decision-log-solu2.md`. AD-01..AD-07 y Plan-2 intactos. Gates 4/5/6 intactos.
- Escala: ROBUSTO / CONDITIONAL / NOT READY (criterio sin relajar).
- Veredicto del lens: **CONDITIONAL** (3/3 cierres verificados en texto con ID y marca `[ADOPTED 2026-10-13, estudiante]`; 2 observaciones bajas nuevas no bloqueantes G7-01/G7-02; DEFERRED con responsable/fase y OPEN fuera de las 3 operaciones intactos).

## Verificiación de cierres

1. G6-01 `revoked_at` — CUMPLE. DDL `escalation_tickets.revoked_at TEXT NULL` + `CHECK ((status <> 'REVOKED') OR (revoked_at IS NOT NULL))` (mismo patrón que credenciales/membresías); intervalo `[granted_at, min(expires_at, revoked_at))` y regla `at >= revoked_at → no aplica` en `contracts.md:§1-Q1/§1-Tiempo/§5×2/§6`, spine AD-13 (head + tail), `ports-and-adapters.md:§5`, `events.md:§1/§4`. `dto.py`/`openapi.yaml` sin modelo de ticket: N/A declarado, sin divergencia.
2. G6-02 scheduler `QueueReservation` + reconciliación — CUMPLE. Reserva pre-commit + publica post-commit y reconciliación (`escalation.expired` por ticket `EXPIRED` sin evento, idempotente por id; exactamente 1 evento por transición) en `contracts.md:§1-Tiempo/§5/§6`, spine AD-13 tail, `ports-and-adapters.md:§4/§5/§6`, `events.md:§2` (nueva sección `escalation.expired`) + `§4`; DDL `audit_events.event_type` admite `escalation.expired`. Sin códigos de error nuevos (catálogo de 24 intacto; el tipo de evento lo exige la decisión).
3. R2-01 `roles.id` en matriz — CUMPLE. `roles_matrix.v0.json`: `student`, `student`, `instructor_privileged`, los 3 ⊆ ids del DDL (`student`, `ta`, `instructor_privileged`, `auditor`, `admin`); 0 conflictos, nada inventado; citas PRD intactas. Marcas en nota de la matriz, `contracts.md:§6`, spine Deferred, `ports-and-adapters.md:§6`.
4. Decision-log — CUMPLE. 3 entradas G6-01/G6-02/R2-01 al final de `ai-log/decision-log-solu2.md` con el mismo formato (origen, opciones, decisión, razón, propuesta/aprobación/fecha). Histórico F/H sin reescribir.
5. Autoridad — CUMPLE. `planning/ARCHITECTURE.md` y PRD sin tocar (solo lectura esta corrida); AD-01..AD-07 sin renumerar ni debilitar; 0 triggers nuevos; único CHECK/DDL nuevo es el exigido por G6-01/G6-02.
6. Gates previos intactos — CUMPLE. Archivos `-20261013-4/-20261013-5/-20261013-6` sin tocar; solo se agregan archivos `-20261013-7`.

## Hallazgos (sin suavizar)

- **G7-01 (nuevo, bajo, NO bloquea):** ticket `REVOKED` con `revoked_at` NULL en una DB migrada desde el DDL anterior (el `CHECK` rige escrituras nuevas, no backfill). Sin regla de migración porque no hay DB productiva en alcance (DDL fresco, tests en `:memory:`). Declarado OPEN.
- **G7-02 (nuevo, bajo, NO bloquea):** cola llena durante el barrido del scheduler: del texto se deriva omitir el commit y reintentar en el siguiente barrido de 1 s (exactamente-1 se preserva); cómo se observa hacia operadores (log/métrica) no está fijado y queda fuera del contrato de las 3 operaciones. Declarado OPEN.
- Restos OPEN/DEFERRED previos sin cambio: código para `timestamp` inválido, `decision`/`reasonCode` de `membership.revoked` y `escalation.expired`, STRICT, negociación 422, CODE 401, matriz completa, cola/TTL (DEFERRED con defaults 503/DENY).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; no se ejecutó TEA ni `bmad-build`.*
