# Revisión adversarial — Paquete estudiante F/H (2026-10-13, corrida 6)

- Fecha: 2026-10-13
- Rol: revisor adversarial, solo lectura salvo este archivo de reporte. No se modifica ningún otro archivo, no se cambia el criterio, no se oculta ningún hallazgo, no se propone ninguna edición, no se cierra ningún OPEN ni pendiente fuera del paquete.
- Alcance: paquete `.work/paquete-decisiones-F-H.md` (19 decisiones F/H + 6 pendientes) aplicado a `contracts.md`, `ARCHITECTURE-SPINE.md`, `ports-and-adapters.md`, `schemas/` (DDL, dto, events, openapi, `roles_matrix.v0.json`) + `EDGE-01` y Mandatory Edge Case literal.
- Fuentes leídas (solo lectura): los 7 artefactos actualizados, `ai-log/decision-log-solu2.md`, Gate 4/5 (`validation-gate-20261013-4.md`, `-20261013-5.md`, rubric y adversarial `-20261013-4/-20261013-5`).
- Método: por cada F/H cerrado, dos unidades hipotéticas que obedecen al pie de la letra el texto NUEVO; si divergen, el cierre está incompleto = hallazgo NUEVO (serie G6).
- Veredicto del lens: **NO ROBUSTO (2 pares nuevos G6-01/G6-02; 19/19 cierres F/H verificados sin divergencia en su alcance).**

## Resumen de cierres

| ID | Foco | Estado en esta corrida |
| --- | --- | --- |
| F-01 | Replay con sintaxis primero | CERRADO (`contracts.md:§2`, `ports §3/§5`, spine AD-12) |
| F-02 | Matriz v0 + fail-closed | CERRADO (`roles_matrix.v0.json` + `contracts.md:§1/§6`; resto DEFERRED negando) |
| F-03/H-17 | Precedencias 404/403 | CERRADO (`contracts.md:§1`, `ports §3`) |
| F-04 | Frontera `batch_id` + UNIQUE/reintento | CERRADO (`contracts.md:§3/§5`, `ports §3/§5`, DDL §9) |
| F-05 | `timestamp` en body | CERRADO en canal (`contracts.md:§2`, `dto.py`, `openapi.yaml`); resto OPEN declarado |
| F-06 | Envelope 500 + catálogo | CERRADO (`contracts.md:§4/§5`, `openapi.yaml:Internal`) |
| H-14 | Alcance SOLO 8 campos + decimal UTF-8 | CERRADO (`contracts.md:§1/§5`, `ports §4`, `events.md:§3`, DDL) |
| H-15 | Génesis 64 `0` + bytes UTF-8 | CERRADO (mismos sitios; semilla DDL coincide) |
| H-16 | `request_now` pre-auth + reuse | CERRADO (`contracts.md:§1`, `ports §3-§4`, `events.md:§1`) |
| H-18 | Decode-once + path exacto/404 | CERRADO (`contracts.md:§3/§5`, `ports §3/§5`, `openapi.yaml`) |
| H-19 | `isspace` + máscara gana | CERRADO (`contracts.md:§2/§5`, `ports §3/§5`, dto/openapi documentados) |
| H-20 | Scope cualquier estado + no reactiva | CERRADO (`contracts.md:§3/§5`, `ports §5`, DDL comentario) |
| H-21 | Intervalo/REVOKED/futuro/vacío | CERRADO salvo G6-01 (`contracts.md:§1/§5`, `ports §5`, `events.md:§1`) |
| H-22 | Tx lectura única + caché solo-DENY | CERRADO (`contracts.md:§1`, `ports §5`) |
| H-23 | `rule_ids` totales ordenadas | CERRADO (`contracts.md:§§1–3/§4/§5`, `ports §5`, dto/openapi) |
| H-24 | Repetido/vacío = ausente | CERRADO (`contracts.md:§0`, `ports §3/§5`, `openapi.yaml`) |
| H-25 | Pureza ampliada | CERRADO (spine AD-08, `ports §1/§5`, `contracts §5`, dto docstring) |
| H-26 | `roles.id` exacto | CERRADO (`contracts.md:§5`, spine AD-10, dto/openapi) |
| Scheduler | Barrido 1 s + crash RETURNING | CERRADO salvo G6-02 |
| COMPLETED/colisión | DENY sin productor; UNIQUE + x3 → 503 | CERRADO |

## Pares NUEVOS (cierres incompletos del paquete)

### G6-01 — Replay vs ticket REVOKED sin `revoked_at` (H-21a). Media-baja.

- Unidad A: ticket con `status='REVOKED'` nunca aplica en replay (revocado = terminado).
- Unidad B: ticket REVOKED aplica si `at` cae en `[granted_at, expires_at)` (manda intervalo + "revoked_at").
- Divergencia observable: mismo replay histórico da rol base (A) vs escalado (B).
- Obediencia literal: ambas aplican "mandan el intervalo y el revoked_at del ticket, no el estado persistido"; el DDL `escalation_tickets` no tiene columna `revoked_at` (solo `status`), así que "revoked_at" no es evaluable y cada unidad lo aproxima distinto.
- No cubierto: H-21a fijó intervalo/futuro/vacío, no el instante de revocación sin columna.

### G6-02 — Evento del scheduler tras crash (pendiente scheduler). Baja-media.

- Unidad A: evento de expiración en la MISMA tx que el `UPDATE … RETURNING` (atómico: crash antes del commit → re-barrido al reiniciar → exactamente uno).
- Unidad B: evento DESPUÉS del commit (crash intermedio → transición persistida sin evento → cero eventos).
- Divergencia observable: misma secuencia con crash da 1 evento (A) vs 0 eventos (B) para la misma transición.
- Obediencia literal: ambas barren con `UPDATE … WHERE status='ACTIVE' … RETURNING` y emiten "un evento por transición (idempotente)"; la frontera tx del evento no está fijada.
- No cubierto: el paquete fijó barrido + RETURNING + idempotencia, no la atomicidad evento-transición.

## Top 3 riesgos (residuales)

1. G6-01: replay contra tickets revocados diverge sin `revoked_at` o regla que lo sustituya.
2. G6-02: ventana crash entre transición del scheduler y su evento.
3. Restos OPEN fuera del paquete (sin divergencia nueva): código de `timestamp` inválido, mapeo `decision`/`reasonCode` de `membership.revoked`, STRICT, negociación 422, CODE 401, matriz completa, cola/TTL (DEFERRED con defaults seguros).

*Fin del reporte. Solo lectura del resto del workspace; ningún otro archivo fue modificado; no se ejecutó TEA ni `bmad-build`.*
