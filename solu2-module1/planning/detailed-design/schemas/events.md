# events.md — Eventos y envelope versionado del Módulo 1 (Fase 2)

Alcance: las tres operaciones. Todo lo GPU/telemetría/K8s/vLLM/identidad real va tras
puertos con adapters simulados; aquí solo eventos de dominio + auditoría.
AD-04 (ledger encadenado + metadata singleton) es autoridad read-only.

## 1. Envelope versionado (obligatorio en cada evento)

| Campo | Tipo | Regla |
|---|---|---|
| `eventId` | string | único (`evt-…` o UUID del `IdGenerator`/adapter) |
| `occurredAt` | string | UTC ISO-8601 con microsegundos + zona (`YYYY-MM-DDTHH:MM:SS.ffffffZ`), del `request_now` (capturado UNA vez al entrar al adapter pre-auth — H-16) o del `at` interno; `roster.rejected` reutiliza el mismo `request_now`; el worker nunca lo reconstruye con `Clock.now()`. [ADOPTED 2026-10-13, estudiante] |
| `schemaVersion` | string | constante `"1"` en esta fase; cualquier cambio de forma exige bump + migración documentada |
| `type` | string | uno del §2 |
| `payload` | object | según §2; jamás contiene secreto en claro (AD-06: solo `uai_live_<4>••••••••••••<4>`) |
| `ledger` | object | `prevRecordHash`, `eventHash` (SHA-256 encadenado), `ledgerSeq` (`audit_ledger.id`) |

Compatibilidad `audit_ledger` ↔ `audit_events`: el físico autoritativo de la cadena
hash es `audit_ledger` (+ `audit_ledger_metadata id=1`); la TABLA física `audit_events`
(`schemas/001_module1_schema.sql` §7b) guarda el envelope 1:1 por FK `event_id` con
`occurred_at`, `schema_version`, `event_type` y `payload` JSON. Regla de timestamp
consistente: `occurred_at == audit_ledger.timestamp` byte-a-byte. Escritura atómica:
`LedgerWriter` inserta ambas filas en la misma transacción; fallo → rollback total.
Fórmula normativa + codec en §3 (adoptados, H-14/H-15). Replay con `at` histórico: mandan el intervalo `[granted_at, min(expires_at, revoked_at))` y la columna `revoked_at` del ticket (`escalation_tickets.revoked_at`); si `at >= revoked_at`, el ticket no aplica [ADOPTED 2026-10-13, estudiante] (G6-01); `granted_at` futuro → rol base; vacío imposible por DDL (H-21) [ADOPTED 2026-10-13, estudiante]. Capacidad de cola y recuperación
post-aceptación DEFERRED Fase 3 NFR (Test-lead); hasta entonces cola llena → 503. Ninguna unidad escribe solo en una de las dos tablas.

Actor y recurso en el ledger [ADOPTED 2026-10-13, Ronda 6 Q2] (ADVF-02/ADVF-03; columnas NOT NULL de `audit_ledger`):
- `actor_id` / `actor_role` = sujeto y rol del token validado por `TokenVerifierPort` (adapter simulado, fixtures). Para `revokeCourseAccess` e `ingestRoster` el actor es el principal `admin` autenticado (Q1).
- Scheduler de expiración: `actor_id = 'system:scheduler'`, `actor_role = 'admin'`.
- `resource_arn` = `urn:uai:subject:<subject_id>:model:*` para baja y lote; `action` = `revoke` para baja e `ingest_roster` para lote.
- `resolveEffectivePermissions`: `action` ∈ {`inference`, `training`} (Q5); `resource_arn` según la gramática del §0 de contracts.

## 2. Eventos por operación (nombres exactos emitidos por `LedgerWriter`)

### `authorization.decided` (resolveEffectivePermissions, contracts §1-Q3)
```json
{
  "eventId": "evt-7712-bc9",
  "occurredAt": "2026-09-12T10:14:22.004000Z",
  "schemaVersion": "1",
  "type": "authorization.decided",
  "payload": {
    "actorId": "TA-SOFIA-01",
    "actorRole": "ta",
    "subjectId": "CS-480",
    "resourceArn": "urn:uai:subject:CS-480:model:llama-3-8b",
    "action": "inference",
    "decision": "ALLOW",
    "reasonCode": "SUCCESS",
    "ruleIds": ["AD-01"],
    "expiresAt": null
  },
  "ledger": {"prevRecordHash": "<hex>", "eventHash": "<hex>", "ledgerSeq": 142}
}
```
`reasonCode` de éxito: `SUCCESS` (padre §4.2/DDL; contracts §4). Errores P1–P4
(formato/auth/identidad) no generan eventos; un DENY de política no es error de
formato. Si el evento obligatorio no es aceptado en cola → 503 en vez de 200/403.
Banners E-01/E-03/E-04 se derivan de este evento vía `ExplanationDTO` (AD-11).

### `membership.revoked` (revokeCourseAccess, contracts §2-Q3)
```json
{
  "eventId": "evt-revoke-01",
  "occurredAt": "2026-09-23T15:04:05.120000Z",
  "schemaVersion": "1",
  "type": "membership.revoked",
  "payload": {
    "studentId": "STU-98432",
    "subjectId": "CS-480",
    "priorStatus": "ACTIVE",
    "credentialsRevoked": 2,
    "ruleIds": ["AD-03"]
  },
  "ledger": {"prevRecordHash": "<hex>", "eventHash": "<hex>", "ledgerSeq": 143}
}
```
Ejemplo con `studentId` canónico `STU-98432` (R8-08; `STU-MATEO-99` es inconsistencia registrada de Plan-2) [ADOPTED 2026-10-14, estudiante]. Exactamente un evento por primera baja; repetición válida `ALREADY_REVOKED` sin evento ni mutación, con `ExplanationDTO` (AD-03); orden F-01 + R3-02: sintaxis P3/P4 primero (`drop_reason`/`timestamp` inválidos → 400 aunque esté `DROPPED`; `MALFORMED_DROP_REASON` primero si ambos fallan, ambos en `rule_ids`).
Mapeo ledger [ADOPTED 2026-10-13, estudiante] (R3-03): `membership.revoked` porta `decision='DENY'`, `reasonCode='SUBJECT_ENROLLMENT_DROPPED'` (código ya existente; cumple el `CHECK ALLOW/DENY`).
Banner E-02 se deriva de aquí.

### `roster.ingested` / `roster.rejected` (ingestRoster, contracts §3-Q3)
```json
{
  "eventId": "evt-roster-01",
  "occurredAt": "2026-09-23T15:04:05.120000Z",
  "schemaVersion": "1",
  "type": "roster.ingested",
  "payload": {
    "subjectId": "CS-480", "term": "2026-FALL", "batchId": "roster-8f3ab12c-2026-FALL",
    "processed": 120, "createdIdentities": 115, "updatedMemberships": 5, "ruleIds": ["AD-02"]
  },
  "ledger": {"prevRecordHash": "<hex>", "eventHash": "<hex>", "ledgerSeq": 144}
}
```
Rechazo: `type: roster.rejected` en la misma cadena única (afecta el siguiente
`prev_record_hash`; 1:1 con `audit_events`) + anexo `roster_rejected_conflicts.csv`
(`row_number, institutional_id, field, observed, expected`): una fila por combinación
única (fila, campo), ordenada por fila y columnas
`institutional_id,email,full_name,assigned_role`. Respuesta 422 con
`processed/created_identities/updated_memberships` en 0, `batch_id`, manifiesto y
explicación; precedencia `ROSTER_VALIDATION_FAILED` → `INTRA_BATCH_DUPLICATE_ID` →
`IDENTITY_BARRED`; `created` solo insertadas, `updated` insertadas/modificadas.
La 422 se responde tras aceptar el evento en cola (sin esperar persistencia);
cola no acepta → 503. Sin segunda cadena.
STRICT [ADOPTED 2026-10-13, estudiante] (R3-04): STRICT = abortar el lote completo (rollback total, 422 con manifiesto); no existe modo "segregar" (AD-02 heredado manda sobre la frase ambigua del PRD §7.2).
Mapeo ledger del lote [ADOPTED 2026-10-13, Ronda 6] (ADVF-04): `roster.ingested` → `decision='ALLOW'`, `reasonCode='SUCCESS'`; `roster.rejected` → `decision='DENY'`, `reasonCode` = código principal del manifiesto (`ROSTER_VALIDATION_FAILED`, si no `INTRA_BATCH_DUPLICATE_ID`, `IDENTITY_BARRED` solo en `rule_ids`, R9-01 [ADOPTED 2026-10-14, estudiante]); actor y recurso según §1 de este documento.

### `escalation.expired` (scheduler, contracts §1-Tiempo; AD-13)
```json
{
  "eventId": "evt-expiry-01",
  "occurredAt": "2026-09-23T18:30:00.000000Z",
  "schemaVersion": "1",
  "type": "escalation.expired",
  "payload": {
    "ticketId": "esc-0007",
    "subjectId": "CS-480",
    "expiredAt": "2026-09-23T18:30:00.000000Z",
    "ruleIds": ["AD-05"]
  },
  "ledger": {"prevRecordHash": "<hex>", "eventHash": "<hex>", "ledgerSeq": 145}
}
```
Exactamente un evento por transición `ACTIVE→EXPIRED`, con el patrón `QueueReservation` (reserva espacio antes del commit, publica tras el commit); tras un crash, al reiniciar el scheduler reconcilia: por cada ticket `EXPIRED` sin evento `escalation.expired` en el ledger para ese ticket, emite exactamente uno (idempotente por id de ticket) [ADOPTED 2026-10-13, estudiante] (G6-02). Tipo admitido en el DDL (`audit_events.event_type`, `schemas/001_module1_schema.sql` §7b). Mapeo ledger [ADOPTED 2026-10-13, estudiante] (R3-03): `escalation.expired` porta `decision='DENY'`, `reasonCode='STATUS_ESCALATION_EXPIRED'`. Si el barrido no puede reservar cola: log WARN estructurado (sin secretos) + métrica `scheduler_sweep_deferred_total`, reintento en el siguiente barrido de 1 s — DEFER a NFR (Test-lead, Fase 3) [ADOPTED 2026-10-13, estudiante] (G7-02).

## 3. Cadena hash y verificación (AD-04; fórmula normativa adoptada + codec cerrado)

Fórmula normativa AD-04 §5 (`planning/ARCHITECTURE.md` l.364-365): campos
`prev_record_hash || timestamp || actor_id || subject_id || resource_arn || action
|| decision || reason_code` con codec local [ADOPTED 2026-10-13, estudiante]
(H-14, H-15): alcance SOLO los 8 campos §5 (ningún conteo, `batch_id` ni
`eventId` ni `resource_type` (R8-07) entran); enteros futuros como string decimal UTF-8; génesis `prev` =
semilla `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (planning/ARCHITECTURE.md l.97; mismo valor que el DDL) [ADOPTED 2026-10-14, estudiante] (R10-M2, corrige H-15); longitud de frame = bytes UTF-8 (no puntos
de código); frames `0x00` null / `0x01`+len8BE+UTF-8 en orden, SHA-256.
Timestamp normalizado a UTC `YYYY-MM-DDTHH:mm:ss.ffffffZ`;
`prev_record_hash` hexadecimal en minúscula.
Orden: aceptación FIFO en cola, persistencia secuencial, `id ASC` define el hash;
micro-batching 50 ms / 50 eventos (AD-04.3); respuesta tras aceptación sin espera
de persistencia. Capacidad máxima y recuperación post-aceptación: DEFERRED Fase 3
NFR (`/bmad-testarch-nfr`), responsable Test-lead; hasta entonces cola llena → 503.
`batch_id` UNIQUE en DDL (`roster_batches.batch_id`); choque → reintento IdGenerator
x3 → 503 [ADOPTED 2026-10-13, estudiante]. Verificación: recorre `id ASC` + compara `total_events_count` y
`head_record_hash` del singleton; rotura → `AUDIT_LOG_TAMPERING_DETECTED`
(emisor fuera de las tres ops, pendiente).

## 4. open_questions[] de eventos (paquete estudiante 2026-10-13 aplicado + Ronda 2 Gate 6)

H-14..H-26 cerrados (ver `ai-log/decision-log-solu2.md`). G6-01 cerrado (columna `revoked_at` en `escalation_tickets` + intervalo `[granted_at, min(expires_at, revoked_at))`) y G6-02 cerrado (transición `ACTIVE→EXPIRED` con `QueueReservation` + reconciliación `escalation.expired` idempotente por ticket, exactamente 1 evento por transición) [ADOPTED 2026-10-13, estudiante]. Ronda 3 aplicada 2026-10-13 (G7-01 REJECT sin migración; G7-02 DEFER barrido con WARN+métrica; R3-01 `AUTH_TOKEN_INVALID`; R3-02 `MALFORMED_DROP_TIMESTAMP`; R3-03 mapeo ledger `membership.revoked` → `DENY`/`SUBJECT_ENROLLMENT_DROPPED` y `escalation.expired` → `DENY`/`STATUS_ESCALATION_EXPIRED`; R3-04 STRICT aborta sin segregar; R3-05 422 siempre `application/problem+json`, se ignora `Accept`; R3-06 orden revoke + triggers append-only) [ADOPTED 2026-10-13, estudiante]. Resta, sin cerrar por
suposición: matriz rol×acción completa (v0 en `roles_matrix.v0.json`; resto
DEFERRED al equipo de políticas); capacidad de cola y recuperación
post-aceptación DEFERRED Fase 3 NFR (Test-lead); TTL `uai_live_…` y reemisión (DEFERRED, dueño de
credenciales futuro); `COMPLETED` = no activa → DENY (resuelto, ninguna de las
tres operaciones lo crea).
