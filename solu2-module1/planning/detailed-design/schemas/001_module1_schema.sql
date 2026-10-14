-- 001_module1_schema.sql — Migración SQLite del Módulo 1 (Fase 2)
-- Stack: SQLite WAL, writer único, PRAGMA busy_timeout = 5000 (AD-03 padre).
-- Autoridad read-only: planning/ARCHITECTURE.md §3 DDL + AD-01..AD-07 (no se debilitan).
-- Alcance: tres operaciones (resolveEffectivePermissions, revokeCourseAccess, ingestRoster).
-- Sin lógica productiva. Compatibilidad ledger: autoridad única de cadena hash
-- audit_ledger + audit_ledger_metadata; TABLA física audit_events (consigna Step 2.2)
-- ligada 1:1 por FK a audit_ledger(event_id) para envelope/payload (ver §7b).
-- Sincronizado con contracts + spine (corrección at, orden 7 pasos, codec, QueueReservation,
-- roster/manifiesto, scheduler condicional, UUID canónico, límites exactos). Paquete estudiante
-- 2026-10-13 aplicado (F-01..F-06, H-14..H-26, scheduler 1 s + crash, UNIQUE batch_id, matriz v0
-- como dato). Ronda 2 Gate 6 aplicada (G6-01 revoked_at, G6-02 QueueReservation+reconciliación,
-- R2-01 roles.id). Ronda 3 aplicada 2026-10-13 (G7-01 REJECT sin migración, G7-02 DEFER barrido
-- con WARN+métrica, R3-01 AUTH_TOKEN_INVALID, R3-02 MALFORMED_DROP_TIMESTAMP, R3-03 mapeo
-- ledger DENY, R3-04 STRICT aborta, R3-05 422 problem+json, R3-06 orden revoke + triggers
-- append-only). DEFERRED en spine (cola, TTL/reemisión, matriz completa). Fase 1 NO PASS hasta Gate 6.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- 1. Directorio de identidades (AD-02 barred global; contracts §1-P5/§3-P4)
CREATE TABLE IF NOT EXISTS identities (
    id TEXT PRIMARY KEY,
    -- Q7 (ADVF-21) [ADOPTED 2026-10-13]: patrón ^[A-Za-z0-9-]{1,64}$ en boundary; aquí solo la cota de columna.
    institutional_id TEXT NOT NULL UNIQUE CHECK (length(institutional_id) BETWEEN 1 AND 64),
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'SUSPENDED', 'EXPELLED')),
    created_at TEXT NOT NULL,   -- UTC ISO-8601 con microsegundos, del puerto Clock
    updated_at TEXT NOT NULL    -- UTC ISO-8601 con microsegundos, del puerto Clock
    -- userId: UUID canónico 8-4-4-4-12 (hex normalizado a minúsculas para buscar) o
    -- institutional_id exacto case-sensitive; whitespace/controles rechazados en boundary (contracts §0).
    -- Sin CHECK de formato en el DDL por diseño; el boundary valida, el DDL no inventa patrones:
    -- formato de IDs/email más allá de contracts §0/§3 queda pendiente donde la fuente no lo defina.
);

-- 2. Catálogo de asignaturas
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,            -- ej. 'CS-480', 'CS101' (comparación cruda AD-01, sin normalización)
    name TEXT NOT NULL,
    term TEXT NOT NULL CHECK (   -- case-sensitive exacto (GLOB ya es case-sensitive); contracts §3-P1
        term GLOB '[0-9][0-9][0-9][0-9]-SPRING'
        OR term GLOB '[0-9][0-9][0-9][0-9]-SUMMER'
        OR term GLOB '[0-9][0-9][0-9][0-9]-FALL'
    ),
    -- Patrón term exacto YYYY-(SPRING|SUMMER|FALL) según contracts §3-P1/openapi; instancia 2026-FALL.
    department TEXT NOT NULL DEFAULT 'Computer Science',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 3. Roles del sistema
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,            -- 'student', 'ta', 'instructor_privileged', 'auditor', 'admin'
    name TEXT NOT NULL,
    priority_level INTEGER NOT NULL, -- 10 Student, 50 TA, 80 Instructor-Privileged, 100 Admin
    description TEXT NOT NULL
);

-- 4. Membresías académicas (AD-02 atomicidad; AD-03 caché+workers:1, predicado por par)
CREATE TABLE IF NOT EXISTS subject_memberships (
    id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(id) ON DELETE RESTRICT,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    role_id TEXT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    -- [ADOPTED 2026-10-13, estudiante] Ronda 6 Q3 (ADVF-13): term en la clave de membresía; mismo CHECK que subjects.term.
    term TEXT NOT NULL CHECK (
        term GLOB '[0-9][0-9][0-9][0-9]-SPRING'
        OR term GLOB '[0-9][0-9][0-9][0-9]-SUMMER'
        OR term GLOB '[0-9][0-9][0-9][0-9]-FALL'
    ),
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'DROPPED', 'SUSPENDED', 'COMPLETED')),
    -- [OPEN-10]: INACTIVE ([ASSUMPTION-03] PRD) fuera de las tres ops; transición COMPLETED sin actor/momento
    -- (semántica decidida: COMPLETED = no activa → DENY; producción DEFERRED).
    -- Scope anti-smuggling [ADOPTED 2026-10-13, estudiante] (H-20): previa en CUALQUIER
    -- estado del mismo curso/term con rol distinto → 422; mismo rol sobre DROPPED →
    -- sin cambios, sin reactivar (ADVF-15/ECF-23: idem SUSPENDED y COMPLETED). Scope = (identity_id, subject_id, term) [ADOPTED 2026-10-13] (ADVF-13).
    enrolled_at TEXT NOT NULL,
    dropped_at TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (identity_id, subject_id, term),
    CHECK ((status <> 'DROPPED') OR (dropped_at IS NOT NULL))
);
-- Ronda 6 Q3 (ADVF-13) [ADOPTED 2026-10-13, estudiante]: como máximo una membresía ACTIVE por par
-- (identity, subject), sin term. revokeCourseAccess(userId, courseId) sigue sin term.
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_active_membership
ON subject_memberships (identity_id, subject_id)
WHERE status = 'ACTIVE';

-- 5. Tickets de escalación (AD-05 exclusión mutua; lectura en resolve, flujos request/approve fuera de las tres ops)
CREATE TABLE IF NOT EXISTS escalation_tickets (
    id TEXT PRIMARY KEY,
    requester_id TEXT NOT NULL REFERENCES identities(id),
    subject_id TEXT NOT NULL REFERENCES subjects(id),
    requested_role_id TEXT NOT NULL REFERENCES roles(id),
    duration_hours INTEGER NOT NULL CHECK (duration_hours BETWEEN 1 AND 12),
    justification TEXT NOT NULL CHECK (length(justification) >= 20),
    status TEXT NOT NULL CHECK (status IN ('PENDING_APPROVAL', 'ACTIVE', 'REJECTED', 'EXPIRED', 'REVOKED')),
    approved_by TEXT NULL REFERENCES identities(id),
    rejection_reason TEXT NULL,
    -- Ronda 6 (ADVF-23/ECF-15) [ADOPTED 2026-10-13]: formato fijo YYYY-MM-DDTHH:MM:SS.ffffffZ (6 decimales)
    granted_at TEXT NULL CHECK (granted_at IS NULL OR granted_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'),
    expires_at TEXT NULL CHECK (expires_at IS NULL OR expires_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'),
    revoked_at TEXT NULL CHECK (revoked_at IS NULL OR revoked_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'),          -- instante de revocación del ticket (G6-01 [ADOPTED 2026-10-13, estudiante]); formato fijo (ADVF-23)
    -- G7-01 REJECT [ADOPTED 2026-10-13, estudiante]: 001_module1_schema.sql es la migración
    -- inicial; no existe DB previa que migrar. Futura migración 002 debe rellenar
    -- revoked_at antes de activar el CHECK.
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK ((status NOT IN ('ACTIVE')) OR (granted_at IS NOT NULL AND expires_at IS NOT NULL)),
    CHECK ((status NOT IN ('ACTIVE')) OR (expires_at > granted_at)),
    CHECK ((status <> 'REVOKED') OR (revoked_at IS NOT NULL)),
    -- R9-02 [ADOPTED 2026-10-14, estudiante] (AD-05): aprobador distinto del solicitante; enforcement físico
    -- de la auto-aprobación. approved_by es NULL mientras no hay aprobador.
    CHECK (approved_by IS NULL OR approved_by <> requester_id)
    -- Borde [granted_at, expires_at) adoptado (spine AD-13); en replay con ticket
    -- REVOKED el intervalo efectivo es [granted_at, min(expires_at, revoked_at)):
    -- si at >= revoked_at, el ticket no aplica (G6-01 [ADOPTED 2026-10-13, estudiante]).
    -- expiración la ejecuta el scheduler
    -- (solo ACTIVE con granted_at<=now y expires_at<=now); barrido cada 1 s, crash con
    -- UPDATE … RETURNING + un evento por transición [ADOPTED 2026-10-13, estudiante].
);

-- Guarda física anti doble-envío (AD-05; enforcement de contracts §5)
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_active_escalation
ON escalation_tickets (requester_id, subject_id)
WHERE status IN ('PENDING_APPROVAL', 'ACTIVE');

-- 6. Credenciales (AD-06 cero secretos; AD-03 revocación masiva del par)
CREATE TABLE IF NOT EXISTS subject_credentials (
    id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    key_prefix TEXT NOT NULL,       -- ej. 'uai_live_8f3a'
    key_hash TEXT NOT NULL UNIQUE,  -- SHA-256(salt || raw_key), 16-byte salt
    salt TEXT NOT NULL,             -- R9-05 [ADOPTED 2026-10-14, estudiante]: 16 bytes aleatorios del IdGenerator, persistidos en hex (32 caracteres)
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
    -- [OPEN-10]: TTL de uai_live / regla EXPIRED sin fuente; credencial EXPIRED ante revoke sin cerrar
    -- (DEFERRED: dueño de credenciales futuro).
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    revoked_at TEXT NULL,
    CHECK ((status <> 'REVOKED') OR (revoked_at IS NOT NULL))
);

-- 7. Ledger de auditoría (AD-04; autoridad física única de la cadena hash.
-- Fórmula normativa AD-04 §5 + codec [ADOPTED 2026-10-13, estudiante] (H-14, H-15):
-- alcance SOLO 8 campos §5, enteros futuros como string decimal UTF-8, génesis = semilla
-- e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (planning/ARCHITECTURE.md l.97)
-- [ADOPTED 2026-10-14, estudiante] (R10-M2, corrige H-15), longitud bytes UTF-8; resumen §2 sin
-- subject_id/action tratado como incompleto.
-- Ver events.md §3.)
CREATE TABLE IF NOT EXISTS audit_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL CHECK (timestamp GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'),        -- UTC ISO-8601 microsegundos; formato fijo YYYY-MM-DDTHH:MM:SS.ffffffZ (R9-04 [ADOPTED 2026-10-14, estudiante])
    actor_id TEXT NOT NULL,         -- Ronda 6 Q2 (ADVF-03): sujeto del token (TokenVerifierPort); scheduler = 'system:scheduler'
    actor_role TEXT NOT NULL,       -- Ronda 6 Q2: rol del token; scheduler = 'admin'. Baja y lote: action = 'revoke' / 'ingest_roster'; resource_arn = urn:uai:subject:<subject_id>:model:*
    subject_id TEXT NOT NULL,
    resource_arn TEXT NOT NULL CHECK (resource_arn GLOB 'urn:uai:subject:*:model:*'),
    -- R8-07 [ADOPTED 2026-10-14, estudiante]: prefijo `model:<clase>` del ARN (p. ej. `model:restricted`), derivado por LedgerWriter; `model:unknown` si el model no está en resource_catalog (R9-05 [ADOPTED 2026-10-14, estudiante]). NO entra a la fórmula del hash (H-14: solo los 8 campos de events.md §3).
    resource_type TEXT NOT NULL,
    -- Enforcement físico defendible de ARN (AD-01): GLOB aproxima la gramática
    -- exacta ^urn:uai:subject:[a-zA-Z0-9_-]+:model:[a-zA-Z0-9_-]+$ porque GLOB no
    -- expresa clases negadas ni anclas completas (no rechaza '.' '/' con precisión);
    -- la regex exacta vive en el adapter/boundary + domain/resolution + test_arn_grammar_rejects.
    action TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('ALLOW', 'DENY')),
    -- Decisiones ALLOW/DENY de política (físico cerrado por CHECK); mapeo ledger
    -- RESUELTO [ADOPTED 2026-10-13, estudiante] (R3-03): membership.revoked →
    -- decision='DENY', reasonCode='SUBJECT_ENROLLMENT_DROPPED'; escalation.expired →
    -- decision='DENY', reasonCode='STATUS_ESCALATION_EXPIRED' (reutilizan códigos del
    -- catálogo); los tipos de evento viven en audit_events.event_type.
    reason_code TEXT NOT NULL,    -- SUCCESS en ALLOW (padre §4.2/DDL); P1–P4 no generan eventos.
    prev_record_hash TEXT NOT NULL,
    record_hash TEXT NOT NULL UNIQUE,
    -- Serialización exacta: codec [ADOPTED 2026-10-13, estudiante] (H-14, H-15:
    -- alcance SOLO 8 campos §5; enteros futuros decimal UTF-8; génesis = semilla e3b0c442…b855
    -- (R10-M2, ARCHITECTURE.md l.97); longitud bytes UTF-8); events.md §3;
    -- FIFO de cola, id ASC persistido.
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 8. Anclaje anti Tail-Truncation (AD-04; singleton id=1, misma tx que el evento; orden en revoke RESUELTO R3-06 [ADOPTED 2026-10-13, estudiante])
CREATE TABLE IF NOT EXISTS audit_ledger_metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    total_events_count INTEGER NOT NULL DEFAULT 0 CHECK (total_events_count >= 0),
    -- R10-M2 [ADOPTED 2026-10-14, estudiante]: semilla génesis de Plan-2 (ARCHITECTURE.md l.97); corrige H-15 (64 ceros).
    head_record_hash TEXT NOT NULL DEFAULT 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    updated_at TEXT NOT NULL
);
-- 8b. Append-only físico [ADOPTED 2026-10-13, estudiante] (R3-06): AD-04 exige
-- inmutabilidad; la consigna pide invariantes físicos, no "el dev debe recordar".
-- Cualquier UPDATE o DELETE sobre audit_ledger o audit_events falla por trigger.
CREATE TRIGGER IF NOT EXISTS trg_audit_ledger_no_update BEFORE UPDATE ON audit_ledger
BEGIN
    SELECT RAISE(ABORT, 'append-only');
END;
CREATE TRIGGER IF NOT EXISTS trg_audit_ledger_no_delete BEFORE DELETE ON audit_ledger
BEGIN
    SELECT RAISE(ABORT, 'append-only');
END;

-- ADVF-25 [ADOPTED 2026-10-13]: sin seeds de roles ni subjects en este DDL (van en adapters/fixtures).
-- Este INSERT es el singleton de anclaje de AD-04, no un seed de catálogo.
INSERT OR IGNORE INTO audit_ledger_metadata (id, total_events_count, head_record_hash, updated_at)
VALUES (1, 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '1970-01-01T00:00:00.000000Z');

-- Índices estratégicos (padre §3 + AD-04/AD-07)
CREATE INDEX IF NOT EXISTS idx_memberships_lookup ON subject_memberships(identity_id, subject_id, status);
-- ADVF-17 / ECF-18 [ADOPTED 2026-10-13]: el salt impide buscar por key_hash; el lookup es por key_prefix
-- y luego verificación SHA-256(salt || raw_key) sobre las filas que casan el prefijo.
CREATE INDEX IF NOT EXISTS idx_credentials_key_prefix ON subject_credentials(key_prefix, status);
CREATE INDEX IF NOT EXISTS idx_credentials_lookup ON subject_credentials(key_hash, status);
CREATE INDEX IF NOT EXISTS idx_credentials_pair ON subject_credentials(identity_id, subject_id, status);
CREATE INDEX IF NOT EXISTS idx_escalations_active ON escalation_tickets(requester_id, subject_id, status, expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_query ON audit_ledger(subject_id, timestamp, decision);
-- R8-07 [ADOPTED 2026-10-14, estudiante] (NFR-AUDIT-06: índice compuesto (resource_type, timestamp); el NFR no se redefine)
CREATE INDEX IF NOT EXISTS idx_audit_resource_timestamp ON audit_ledger(resource_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_chain ON audit_ledger(id ASC);

-- 7b. Envelope/payload de auditoría (consigna Step 2.2: TABLA física audit_events).
-- Una sola autoridad de cadena hash: audit_ledger + audit_ledger_metadata. Esta tabla
-- NO es una segunda cadena/ledger: es envelope por FK a audit_ledger(event_id),
-- con occurred_at, schema_version, event_type y payload JSON. Separación físico vs conductual:
-- la FK solo garantiza la dirección audit_events → audit_ledger (cada envelope apunta a un
-- ledger existente); no garantiza ledger → events, ni la igualdad byte-a-byte
-- audit_events.occurred_at == audit_ledger.timestamp, ni la atomicidad conjunta — ambas
-- dependen de la conducta del LedgerWriter (misma transacción BEGIN IMMEDIATE;
-- fallo → rollback total, fail-closed). El append-only SÍ es físico (R3-06):
-- triggers BEFORE UPDATE / BEFORE DELETE sobre audit_ledger (§8b) y audit_events
-- (al final de §7b) → RAISE(ABORT, 'append-only').
-- Regla de timestamp consistente (conductual): audit_events.occurred_at DEBE ser byte-a-byte igual a
-- audit_ledger.timestamp del mismo event_id (ambos del puerto Clock, UTC microsegundos).
-- Escritura atómica (conductual): LedgerWriter inserta audit_ledger + audit_events en la MISMA
-- transacción SQLite (BEGIN IMMEDIATE; COMMIT conjunto); fallo en cualquiera → rollback
-- total, fail-closed. Cola async FIFO + QueueReservation (reserva→libera/publica);
-- capacidad máxima y recuperación post-aceptación pendientes (TEA/NFR).
-- Orden en revoke RESUELTO [ADOPTED 2026-10-13, estudiante] (R3-06): validar (P1-P4) →
-- BEGIN IMMEDIATE → UPDATE … WHERE status='ACTIVE' RETURNING + QueueReservation →
-- commit → publicar evento.
CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY REFERENCES audit_ledger(event_id) ON DELETE RESTRICT,
    occurred_at TEXT NOT NULL CHECK (occurred_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'),      -- UTC ISO-8601 microsegundos; igual a audit_ledger.timestamp; formato fijo (R9-04 [ADOPTED 2026-10-14, estudiante])
    schema_version TEXT NOT NULL DEFAULT '1',
    event_type TEXT NOT NULL CHECK (event_type IN (
        'authorization.decided', 'membership.revoked', 'roster.ingested', 'roster.rejected',
        'escalation.expired'
    )),
    -- 'escalation.expired': un evento por transición ACTIVE→EXPIRED del scheduler
    -- (G6-02 [ADOPTED 2026-10-13, estudiante]); reconciliación tras crash idempotente
    -- por id de ticket.
    payload TEXT NOT NULL           -- JSON del envelope events.md §2 (sin secretos, AD-06)
);
CREATE INDEX IF NOT EXISTS idx_audit_events_type ON audit_events(event_type, occurred_at);
-- Append-only físico de audit_events [ADOPTED 2026-10-13, estudiante] (R3-06).
CREATE TRIGGER IF NOT EXISTS trg_audit_events_no_update BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'append-only');
END;
CREATE TRIGGER IF NOT EXISTS trg_audit_events_no_delete BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'append-only');
END;

-- 9. Lotes de roster comprometidos (trazabilidad batch_id; F-04 + colisión [ADOPTED 2026-10-13, estudiante]).
-- UNIQUE(batch_id): formato roster-<8hex>-<term>; ante choque, el IdGenerator reintenta
-- hasta 3 veces y luego 503. Solo se inserta en lote comprometido (201); el rechazo 422
-- no escribe filas del lote (todo o nada: 0 escrituras).
CREATE TABLE IF NOT EXISTS roster_batches (
    batch_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    term TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_roster_batches_subject ON roster_batches(subject_id, term);
