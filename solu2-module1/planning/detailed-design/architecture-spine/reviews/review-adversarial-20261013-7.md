# Revisión adversarial — Ronda 2 Gate 6, G6-01/G6-02/R2-01 (2026-10-13, corrida 7)

- Fecha: 2026-10-13
- Rol: revisor adversarial, solo lectura salvo este archivo de reporte. No se modifica ningún otro archivo, no se cambia el criterio, no se oculta ningún hallazgo, no se propone ninguna edición, no se cierra ningún OPEN ni pendiente fuera del paquete.
- Alcance: G6-01, G6-02, R2-01 (`.work/paquete-decisiones-F-H.md` §Ronda 2) aplicados a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/` (DDL, dto, events, openapi, `roles_matrix.v0.json`) + EDGE-01 y Mandatory Edge Case literal.
- Fuentes leídas (solo lectura): los artefactos actualizados, `ai-log/decision-log-solu2.md` (3 entradas nuevas), Gate 6 (`validation-gate-20261013-6.md`, rubric y adversarial `-20261013-6`).
- Método: por cada decisión Ronda-2, dos unidades hipotéticas que obedecen al pie de la letra el texto NUEVO; si divergen, el cierre está incompleto = hallazgo NUEVO (serie G7).
- Veredicto del lens: **ROBUSTO (3/3 cierres sin pares divergentes; 2 observaciones bajas nuevas G7-01/G7-02, no bloqueantes).**

## Resumen de cierres

| ID | Foco | Estado en esta corrida |
| --- | --- | --- |
| G6-01 | `revoked_at` + intervalo `[granted_at, min(expires_at, revoked_at))` | CERRADO (DDL col+CHECK; `contracts.md:§1-Q1/§1-Tiempo/§5/§6`; spine AD-13; `ports §5`; `events §1/§4`). Par G6-01 del Gate 6 ya no diverge: ambas unidades leen la columna y aplican el mismo intervalo. |
| G6-02 | `QueueReservation` + reconciliación `escalation.expired` | CERRADO (`contracts.md:§1-Tiempo/§5/§6`; spine AD-13; `ports §4/§5/§6`; `events §2/§4`; DDL CHECK). Par G6-02 del Gate 6 ya no diverge: reserva pre-commit + publica post-commit + reconciliación por id de ticket dan exactamente 1 evento en ambas unidades. |
| R2-01 | `roles.id` exactos en matriz | CERRADO (`roles_matrix.v0.json` 3/3 ⊆ ids DDL; 0 conflictos; citas intactas). Sin par: es igualdad de dato verificada por máquina. |
| F/H + pendientes previos | 19/19 + scheduler/COMPLETED/colisión/DEFERRED | SIN REGRESIÓN (textos previos intactos salvo adiciones marcadas G6/R2). |

## Observaciones nuevas (sin divergencia observable, no bloquean)

### G7-01 — `revoked_at` NULL en DB migrada desde DDL anterior. Bajo.

- Un par hipotético solo diverge sobre una DB no conformante (`REVOKED` sin `revoked_at`, imposible bajo el `CHECK` vigente en DBs frescas). No hay DB productiva ni ruta de migración en alcance (tests en `:memory:`). Declarado OPEN.

### G7-02 — Cola llena durante el barrido del scheduler. Bajo.

- Ambas unidades conformes omiten el commit y reintenta el siguiente barrido de 1 s (exactamente-1 preservado; el `503` no tiene respuesta HTTP en este camino). Solo difiere la observabilidad hacia operadores (log/métrica sin fijar), fuera del contrato de las 3 operaciones. Declarado OPEN.

## Top 3 riesgos (residuales)

1. Restos OPEN previos fuera de las 3 operaciones o con default seguro: código de `timestamp` inválido, mapeo `decision`/`reasonCode` (ahora también de `escalation.expired`), STRICT, negociación 422, CODE 401, matriz completa, cola/TTL (DEFERRED).
2. G7-01/G7-02 (bajos, OPEN, no bloqueantes).
3. Sin regresión en EDGE-01/Mandatory Edge Case (aislamiento por contexto intacto; matriz R2-01 no toca permisos efectivos).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; no se ejecutó TEA ni `bmad-build`.*
