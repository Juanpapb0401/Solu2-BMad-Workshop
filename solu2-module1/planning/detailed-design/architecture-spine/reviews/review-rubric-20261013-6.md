# Review Rubric — Paquete estudiante F/H (corrida 6, 2026-10-13)

- Fecha: 2026-10-13
- Rol: rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura; no se editó ningún fuente salvo este reporte).
- Alcance: paquete `.work/paquete-decisiones-F-H.md` (APROBADO por el estudiante, 19 decisiones F/H + 6 pendientes) aplicado a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/001_module1.sql`, `schemas/dto.py`, `schemas/events.md`, `schemas/openapi.yaml`, más `schemas/roles_matrix.v0.json` (dato) y `ai-log/decision-log-solu2.md` (25 entradas). No se toca AD-01..AD-07 ni documentos Plan-2. Gates 4/5 intactos.
- Escala: ROBUSTO / CONDITIONAL / NOT READY (criterio sin relajar).
- Veredicto del lens: **CONDITIONAL** (19/19 cierres F/H verificados en texto; 2 esquinas nuevas G6-01/G6-02 a triage; DEFERRED con defaults seguros).

## Veredicto

**CONDITIONAL.** Las 19 decisiones se aplican tal cual en los 7 artefactos con su ID y marca `[ADOPTED 2026-10-13, estudiante]`, sin reabrir alternativas ni inventar decisiones: precedencias F-03/H-17 en el orden §1, sintaxis-primero F-01, `batch_id` con frontera F-04 + UNIQUE/reintento, `timestamp` en body F-05 (resto OPEN declarado), envelope 500 F-06, codec cerrado H-14/H-15, `request_now` pre-auth + reuse H-16, decode-once y path exacto H-18, blancos/máscara H-19, scope anti-smuggling H-20, replay/futuro/vacío H-21, lector WAL H-22, `rule_ids` totales H-23, header H-24, pureza ampliada H-25, `roles.id` exacto H-26, scheduler 1 s + crash RETURNING, `COMPLETED` DENY, matriz v0 como dato F-02. AD-01..AD-07 sin debilitar; cero códigos nuevos; cero triggers/CHECKs nuevos salvo `roster_batches.batch_id PRIMARY KEY` (exigido por la decisión). Impiden ROBUSTO: G6-01 (replay vs ticket REVOKED sin `revoked_at` en DDL) y G6-02 (frontera tx del evento del scheduler tras crash), ambas esquinas genuinas fuera del paquete. No llega a NOT READY: sin debilitamiento heredado, sin operaciones fuera de las tres, sin matriz/capacidad/códigos inventados.

## Checklist punto por punto

1. F-01 sintaxis primero — CUMPLE. `contracts.md:§2-Orden/Repetición` + `ports-and-adapters.md:§3/§5` (P3 antes de `DROPPED`; solo replay válido → `ALREADY_REVOKED`); spine AD-12.
2. F-02 matriz v0 — CUMPLE. `schemas/roles_matrix.v0.json` (3 filas citadas prd.md:244/:244/:154) + `contracts.md:§1-paso 7/§6` + spine Deferred (resto al equipo de políticas, fail-closed). Dato, no código.
3. F-03/H-17 precedencias — CUMPLE. `contracts.md:§1-orden` (404 `UNKNOWN_IDENTITY` > `UNKNOWN_COURSE`; 403 barred > mismatch > inactiva > expiración-condicional) + `ports-and-adapters.md:§3`.
4. F-04 `batch_id` — CUMPLE. `contracts.md:§3-Q1/Nota` + `ports-and-adapters.md:§3/§5` (solo tras auth/tamaño/UTF-8/estructura/`term`; 400/401/413 sin `batch_id`) + DDL `roster_batches(batch_id PRIMARY KEY)` + reintento x3 → 503 existente.
5. F-05 `timestamp` — CUMPLE (canal) + resto OPEN declarado. `contracts.md:§2-P4` + `dto.py:RevokeRequest.timestamp` + `openapi.yaml:RevokeRequest` (body, informativo, Clock efectivo); formato inválido → OPEN sin código (ningún 400 existente aplica).
6. F-06 envelope — CUMPLE. `contracts.md:§4/nota + §5-fila` + `openapi.yaml:Internal` (500 con `ErrorBody` sin DTO); escalación fuera de alcance.
7. H-14/H-15 codec — CUMPLE. `contracts.md:§1-Q3 + §5` + `ports-and-adapters.md:§4` + `events.md:§3` + DDL comentarios (SOLO 8 campos; decimal UTF-8; génesis 64 `0`; bytes UTF-8).
8. H-16 `request_now` — CUMPLE. `contracts.md:§1-Tiempo/Concurrencia` + `ports-and-adapters.md:§3-§4` + `events.md:§1` (pre-auth; reuse en `roster.rejected`).
9. H-18 transporte — CUMPLE. decode-once + exacto; path exacto o 404 (`contracts.md:§3-P1/§5`, `ports-and-adapters.md:§3/§5`, `openapi.yaml` term/header/drop).
10. H-19 blancos/secreto — CUMPLE. `str.isspace()` + máscara AD-06 sobre intacto (`contracts.md:§2-P3/§5`, `ports-and-adapters.md:§3/§5`, `dto.py` + `openapi.yaml` documentados sin validador nuevo).
11. H-20 scope — CUMPLE. Cualquier estado + no-reactiva-DROPPED (`contracts.md:§3/§5`, `ports-and-adapters.md:§5`, DDL comentario).
12. H-21 tiempo — CUMPLE salvo G6-01. Intervalo + REVOKED mandan; futuro → base; vacío imposible por DDL (`contracts.md:§1/§5`, `ports-and-adapters.md:§5`, `events.md:§1`).
13. H-22 lector — CUMPLE. Una tx de lectura + caché solo-DENY + 503 solo `busy_timeout` (`contracts.md:§1`, `ports-and-adapters.md:§5`).
14. H-23 explicación — CUMPLE. Todas ordenadas, primero = principal (`contracts.md:§§1–3-Q4/§4-nota/§5`, `ports-and-adapters.md:§5`, `dto.py`, `openapi.yaml`).
15. H-24 header — CUMPLE. Repetido/vacío = ausente; valor del parser (`contracts.md:§0`, `ports-and-adapters.md:§3/§5`, `openapi.yaml` header).
16. H-25 pureza — CUMPLE. Lista ampliada en spine AD-08 + `ports-and-adapters.md:§1/§5` + `contracts.md:§5` + `dto.py` docstring.
17. H-26 rol — CUMPLE. `roles.id` exacto (`contracts.md:§5`, spine AD-10, `dto.py`, `openapi.yaml`).
18. Scheduler/COMPLETED/colisión — CUMPLE salvo G6-02. Barrido 1 s + crash RETURNING + 1 evento/transición; `COMPLETED` DENY sin productor; UNIQUE + reintento (`contracts.md:§1/§2/§6`, spine AD-13/Deferred, DDL §9).
19. DEFERRED con defaults — CUMPLE. Cola y TTL/reemisión (spine Deferred, `contracts.md:§6`, `ports-and-adapters.md:§6`, `events.md:§4`); fail-closed 503/DENY mientras tanto; matriz resto al equipo de políticas.
20. Gates previos intactos — CUMPLE. `validation-gate-20261013-4.md`, `-20261013-5.md` y lenses anteriores sin tocar.

## Hallazgos (sin suavizar)

- **G6-01 (nuevo, media-baja):** replay con `at` histórico vs ticket REVOKED — la decisión H-21a invoca "revoked_at del ticket" pero el DDL no tiene esa columna (solo `status`); dos unidades conformes divergen (REVOKED ⇒ nunca aplica vs aplica si `at` en intervalo). Ver adversarial `-20261013-6`.
- **G6-02 (nuevo, baja-media):** evento del scheduler tras crash — no se fija si el evento va en la misma tx que el `UPDATE … RETURNING` o después del commit (pérdida posible ante crash intermedio). Ver adversarial `-20261013-6`.
- Restos OPEN declarados (fuera del paquete, sin divergencia nueva): código para `timestamp` inválido (F-05 resto), `decision`/`reasonCode` de `membership.revoked`, STRICT vs cuarentena, negociación 422 JSON/CSV, CODE 401, matriz completa, cola/TTL (DEFERRED).
- Cero cierres accidentales fuera del paquete; cero códigos/triggers/CHECKs inventados (solo `roster_batches` exigido por decisión).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; no se ejecutó TEA ni `bmad-build`.*
