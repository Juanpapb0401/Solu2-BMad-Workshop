"""dto.py — DTO primitivos del Módulo 1 (Fase 2, sin lógica productiva).

Alcance: tres operaciones + ErrorBody + ExplanationDTO. Solo tipos primitivos;
sin fastapi/sqlalchemy/red ni ninguna fuente de no-determinismo
(random, secrets, uuid, os.urandom, time.*, datetime.now/utcnow/today)
(AD-08 + H-25 [ADOPTED 2026-10-13, estudiante]). Pydantic v2 (2.14.1) como
lenguaje de schemas, no como lógica de dominio.

[Sincronizado con contracts + spine (R1–R11 + paquete estudiante 2026-10-13 + Ronda 3
G7-01/G7-02/R3-01..R3-06 2026-10-13):
endpoint público sin `at` (solo `request_now` pre-auth del adapter; `at`
interno/test/replay); comparación cruda AD-01; `term` exclusivo por canal con
siempre-`MALFORMED_TERM` y decode-once RFC 3986; UUID canónico 8-4-4-4-12
en minúsculas; límites exactos; `timestamp` de baja en body (F-05) con
`MALFORMED_DROP_TIMESTAMP` ante ausente o fuera de la gramática RFC 3339 UTC
(R3-02, R4-01, G9-01 [ADOPTED 2026-10-13, estudiante]); `AUTH_TOKEN_INVALID`
→ 401 primero (R3-01); mapeo ledger R3-03; STRICT aborta sin segregar (R3-04);
422 siempre `application/problem+json`, se ignora `Accept` (R3-05); orden revoke +
triggers append-only (R3-06);
DTO en 409/422 vs `ErrorBody` en 400/401/404/413/503/500 (F-06);
matriz v0 como dato (`roles_matrix.v0.json`, F-02).
Abierto restante: ninguno dentro de las tres operaciones tras la Ronda 3;
DEFERRED fuera de alcance (cola/TTL/matriz completa, G7-02).
Mapeo ledger R3-03 [ADOPTED 2026-10-13, estudiante]: `membership.revoked` →
`DENY`/`SUBJECT_ENROLLMENT_DROPPED`; `escalation.expired` →
`DENY`/`STATUS_ESCALATION_EXPIRED`. STRICT R3-04: abortar lote completo.]

Serialización [ADOPTED 2026-10-13, estudiante] (G9-03): los campos opcionales
ausentes se OMITEN, nunca se serializan como `null`; todas las respuestas usan
`model_dump(exclude_none=True)` / `response_model_exclude_none=True`. Los campos
opcionales se declaran no-nullable en el JSON Schema mediante `_sin_null`
(`json_schema_extra`), sin cambiar la lógica de validación.
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


def _sin_null(schema: dict[str, Any]) -> None:
    """json_schema_extra (G9-03): quita `null` de `anyOf` y de `default`.

    Solo afecta al JSON Schema; la regla de serialización es exclude_none.
    """
    opciones = [s for s in schema.pop("anyOf", []) if s.get("type") != "null"]
    if len(opciones) == 1:
        schema.update(opciones[0])
    schema.pop("default", None)


# --- Primitivos compartidos -------------------------------------------------

# Decisión de dominio (contracts §1-Q1): el dominio distingue ALLOW|DENY.
# Mapeo HTTP (AD-09, PRD §5.2, ARCH §4.2/AD-01): ALLOW → 200 AuthorizeResponse;
# todo DENY de política (P5 + matriz rol×acción + STATUS_ESCALATION_EXPIRED) → 403 DenyBody.
Decision = Literal["ALLOW", "DENY"]
AllowOnly = Literal["ALLOW"]
DenyOnly = Literal["DENY"]
HttpStatus = Literal[200, 201, 400, 401, 403, 404, 409, 413, 422, 500, 503]

# Q5 [ADOPTED 2026-10-13, estudiante] (ADVF-07, ECF-24 pendiente): gramática cerrada de action;
# otro valor o vacío → 400 MALFORMED_ACTION.
Action = Literal["inference", "training"]

ErrorCode = Literal[
    "AUTH_TOKEN_INVALID",
    "ADMIN_ROLE_REQUIRED",  # Q1 [ADOPTED 2026-10-13]: 403, después del 401 y antes de la sintaxis
    "UNKNOWN_IDENTITY",
    "UNKNOWN_COURSE",
    "MEMBERSHIP_NOT_FOUND",
    "INVALID_AT",
    "MALFORMED_RESOURCE_ARN",
    "MALFORMED_ACTION",  # Q5 [ADOPTED 2026-10-13]: action fuera del enum cerrado
    "MALFORMED_TERM",
    "MALFORMED_BATCH",
    "BATCH_EMPTY",
    "BATCH_TOO_LARGE",
    "MALFORMED_DROP_REASON",
    "MALFORMED_DROP_TIMESTAMP",
    "RESOURCE_SUBJECT_MISMATCH",
    "SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED",
    "SUBJECT_ENROLLMENT_DROPPED",
    "IDENTITY_BARRED",
    "UNAUTHORIZED_RESOURCE_CLASS",
    "STATUS_ESCALATION_EXPIRED",
    "ESCALATION_REQUEST_REJECTED",
    "FORBIDDEN_SELF_APPROVAL",
    "INVALID_TRANSITION",
    "CONCURRENT_ESCALATION_NOT_PERMITTED",
    "ROSTER_VALIDATION_FAILED",
    "INTRA_BATCH_DUPLICATE_ID",
    "AUTH_INTERNAL_POLICY_UNAVAILABLE",
    "AUDIT_LOG_TAMPERING_DETECTED",
]


class ErrorBody(BaseModel):
    """RFC-7807 tipado. `code` pertenece al catálogo contracts §4 (28 códigos
    tras R3-01/R3-02 y Ronda 6 Q1/Q5 [ADOPTED 2026-10-13, estudiante]);
    ningún código fuera del catálogo llega a la respuesta (spine AD-11).
    `status` es el HTTP efectivo."""

    type: str = Field(examples=["https://compute.universidad.edu/errors/resource-subject-mismatch"])
    title: str
    status: int
    detail: str
    instance: str
    code: ErrorCode = Field(
        examples=[
            "RESOURCE_SUBJECT_MISMATCH",
            "SUBJECT_ENROLLMENT_DROPPED",
            "ROSTER_VALIDATION_FAILED",
        ]
    )
    rule_ids: list[str] | None = Field(
        default=None,
        json_schema_extra=_sin_null,
        examples=[["MALFORMED_DROP_REASON", "MALFORMED_DROP_TIMESTAMP"]],
        description="Opcional [ADOPTED 2026-10-13, estudiante] (R4-02; G9-03: omitido, nunca nulo): reglas de sintaxis violadas en la misma petición, ordenadas por precedencia; el primero == code. Presente solo si falla más de una regla de sintaxis; sin ExplanationDTO en 400.",
    )


class ExplanationDTO(BaseModel):
    """Decisión automática explicable (spine AD-11): rule_ids no vacío con AD-n citado,
    valores observados y umbral aplicado. Obligatoria en ALLOW/DENY y rechazos de
    negocio 409/422 (incl. ALREADY_REVOKED con AD-03); 400/401/404, 413/503 y 500 usan
    ErrorBody sin DTO obligatoria (F-06). `rule_ids` = TODAS las reglas violadas
    ordenadas por precedencia (primero = code principal); observados solo de esas
    reglas [ADOPTED 2026-10-13, estudiante] (H-23). Mapeo regla UX (E-01..E-04,
    EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL) pendiente del equipo UX."""

    rule_ids: list[str] = Field(min_length=1, examples=[["AD-01"]])
    observed_role: str | None = None
    observed_context: str | None = None
    observed_resource_subject: str | None = None
    observed_prior_status: str | None = None
    observed_credentials_revoked: int | None = None
    observed_invalid_row: int | None = None
    threshold: str | None = Field(
        default=None,
        json_schema_extra=_sin_null,
        examples=["expires_at=2026-09-23T18:30:00.000000Z"],
        description="Opcional [ADOPTED 2026-10-13, estudiante] (G9-03): ausente se omite, nunca nulo.",
    )
    action_hint: str | None = None


# --- resolveEffectivePermissions --------------------------------------------
# HTTP: POST /api/v1/authorize + header X-Academic-Subject-Context (AD-09).
# Endpoint público SIN `at`: el adapter captura Clock.now() una vez (request_now).
# `at` vive solo como entrada interna/test/replay (no es parte del body público).
# userId: UUID canónico 8-4-4-4-12 (hex normalizado a minúsculas) o institutional_id
# exacto; whitespace/controles rechazados sin recorte (contracts §0, N-10).
# Formato IDs/email: este DTO no inventa patrones (sin regex); el boundary valida
# según contracts §0/§3 y el dominio decide; lo no definido por una fuente queda
# pendiente, sin códigos nuevos.


class AuthorizeRequest(BaseModel):
    user_id: str = Field(examples=["TA-SOFIA-01"])
    resource_arn: str = Field(
        examples=["urn:uai:subject:CS-480:model:llama-3-8b"]
    )
    action: Action = Field(examples=["inference"])


class ResolveEffectivePermissionsCall(BaseModel):
    """Entrada interna de la operación de dominio resolveEffectivePermissions
    [ADOPTED 2026-10-13] (ADVF-09, Q2/Q5). `at` es obligatorio como str: null o
    ausente → INVALID_AT 400. El endpoint público no lo recibe; el adapter fija
    `at` con request_now (AD-13)."""

    user_id: str
    course_id: str
    resource_arn: str
    action: Action
    at: str


class AuthorizeResponse(BaseModel):
    """200 ALLOW con explicación citada (AD-11). Solo ALLOW llega en 200;
    todo DENY de política se sirve 403 DenyBody (PRD §5.2, ARCH §4.2/AD-01).
    `effective_role` = identificador exacto de `roles.id` en el DDL, sin
    transformar [ADOPTED 2026-10-13, estudiante] (H-26); en el ejemplo, 'ta' (roles.id)."""

    decision: AllowOnly
    effective_role: str = Field(examples=["ta"])
    explanation: ExplanationDTO


class DenyBody(ErrorBody):
    """403 DENY de política, RFC-7807 tipado con decisión de dominio y
    explicación obligatoria (PRD §5.2, ARCH §4.2/AD-01, spine AD-11).
    `decision` es siempre DENY; `explanation.rule_ids` no vacío."""

    decision: DenyOnly
    explanation: ExplanationDTO


# --- revokeCourseAccess ------------------------------------------------------
# HTTP: POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop (AD-09).
# Body {drop_reason, timestamp}: `drop_reason` 1–280 puntos Unicode; blancos por
# str.isspace(); secreto uai_live_… se enmascara (AD-06 gana sobre intacto — H-19).
# `timestamp` RFC 3339 UTC informativo (gramática R4-01/G9-01), instante efectivo del Clock (F-05).
# Sintaxis P3 primero: drop_reason inválido → 400 aunque esté DROPPED (F-01).
# Replay DROPPED válido → ALREADY_REVOKED con ExplanationDTO (AD-03).
# Field(min_length/max_length) no hace cumplir blancos ni máscara (documentado;
# enforcement en boundary/dominio).


class RevokeRequest(BaseModel):
    # ADVF-11 / ECF-03 [ADOPTED 2026-10-13]: sin min/max en Pydantic; la longitud y los
    # blancos se validan en boundary ANTES de este modelo → MALFORMED_DROP_REASON 400.
    drop_reason: str
    timestamp: str = Field(
        examples=["2026-09-23T15:04:05.120000Z"],
        description="Fecha académica RFC 3339 con zona UTC obligatoria (informativa): `YYYY-MM-DDTHH:MM:SS` + fracción opcional 1-6 dígitos + (`Z` o `+00:00`), `T`/`Z` en mayúsculas; `-00:00`, segundo 60, fecha inexistente o fracción >6 dígitos → 400 (sin truncar). Se persiste normalizada a YYYY-MM-DDTHH:MM:SS.ffffffZ; instante efectivo del Clock. Ausente o fuera de esa gramática → 400 MALFORMED_DROP_TIMESTAMP (R3-02, R4-01, G9-01 [ADOPTED 2026-10-13, estudiante]). Más de 300 s posterior a request_now → 400 MALFORMED_DROP_TIMESTAMP (Q6, ECF-13 [ADOPTED 2026-10-13]).",
    )


class RevokeResponse(BaseModel):
    student_id: str
    subject_id: str
    status: Literal["REVOKED", "ALREADY_REVOKED"]
    revocation_propagated_at: str
    explanation: ExplanationDTO
    # `explanation` obligatoria también en ALREADY_REVOKED (cita AD-03).
    # Alias histórico `revoked_at`: solo documentado; canónico revocation_propagated_at.


# --- ingestRoster ------------------------------------------------------------
# HTTP: POST /api/v1/subjects/{subject_id}/roster (AD-09).
# Precedencia de sintaxis [ADOPTED 2026-10-13, estudiante] (G9-02): BATCH_TOO_LARGE 413
# se evalúa antes de parsear; luego MALFORMED_TERM > MALFORMED_BATCH > BATCH_EMPTY.
# El HTTP fija el primer código; rule_ids lista todos en ese orden (R4-02).
# CSV columnas exactas o JSON equivalente; 1–1000 filas de datos, ≤5.000.000 bytes
# del body recibido, UTF-8 (contracts §3-P2). `term` exclusivo por canal (query en
# CSV, body en JSON); siempre MALFORMED_TERM en error de term (`term` con
# decode-once RFC 3986 previo y comparación exacta — H-18). Email: dominio
# case-insensitive, resto intacto; institutional_id/term/seen_ids exactos.
# `batch_id` solo tras auth/tamaño/UTF-8/estructura/`term` (400/401/413 sin
# `batch_id`); UNIQUE en DDL + reintento x3 → 503 (F-04). Anti-smuggling sobre
# previa en cualquier estado del mismo curso/term (H-20).
# Manifiesto ordenado por (fila, columna); precedencia de código principal en
# contracts §3. STRICT R3-04 [ADOPTED 2026-10-13, estudiante]: abortar lote completo, sin segregar.
# `subject_id` del path es la autoridad; el `subject_id` del body, si difiere,
# se rechaza según el contrato (MALFORMED_BATCH 400). Formato IDs/email: sin
# patrones inventados en este DTO; validación en boundary/dominio, pendiente lo
# no definido por una fuente.


class RosterRow(BaseModel):
    # Q7 (ADVF-21) [ADOPTED 2026-10-13]: institutional_id ^[A-Za-z0-9-]{1,64}$, case-sensitive exacto.
    institutional_id: str = Field(pattern=r"^[A-Za-z0-9-]{1,64}$")
    # ECF-07 [ADOPTED 2026-10-13]: exactamente un '@' y dominio exacto universidad.edu (validado en boundary).
    email: str
    full_name: str
    assigned_role: Literal["student", "ta"]


class RosterIngestRequest(BaseModel):
    subject_id: str = Field(
        examples=["CS-480"],
        description="Eco del path; el path es la autoridad. Si ausente o distinto del path → MALFORMED_BATCH 400 según contrato (ECF-05).",
    )
    term: str = Field(examples=["2026-FALL"])
    # ECF-02 / ECF-01 [ADOPTED 2026-10-13]: 1-1000 filas y 413 se validan en boundary, antes de
    # este modelo; sin min_length/max_length aquí para no producir 422 del framework (ADVF-11).
    rows: list[RosterRow]


class RosterIngestResponse(BaseModel):
    """201 de ingesta [ADOPTED 2026-10-14, estudiante] (R8-02): sin ExplanationDTO; un éxito
    de mutación se describe con conteos. Sin uai_live_ en la respuesta (R8-01)."""

    processed: int
    created_identities: int
    updated_memberships: int
    batch_id: str = Field(examples=["roster-8f3ab12c-2026-FALL"])


class RosterRejectedManifestRow(BaseModel):
    row_number: int
    institutional_id: str | None = None
    field: str
    observed: str | None = None
    expected: str
    # R8-09 [ADOPTED 2026-10-14, estudiante]: p. ej. email fuera de universidad.edu →
    # code ROSTER_VALIDATION_FAILED, field email, rule_ids ["ROSTER_VALIDATION_FAILED",
    # "EMAIL_DOMAIN_MUST_BE_INSTITUTIONAL"] (código UX para el banner; sin código HTTP nuevo).
    rule_ids: list[str] | None = Field(
        default=None,
        json_schema_extra=_sin_null,
        description="Opcional (R8-09): reglas de la fila; el primero corresponde al código principal de la fila. Omitido si no aplica.",
    )


class RosterRejectedManifest(BaseModel):
    """Manifiesto de rechazo 422 (contracts §3-Q3; OpenAPI `RosterRejectedManifest`).

    Campos RFC-7807 (`type`, `title`, `status`, `detail`, `instance`, `code`) +
    `errors` (manifiesto ordenado por fila/columna) + `batch_id` + `explanation`
    + conteos `processed`/`created_identities`/`updated_memberships` que el
    contrato exige en 0 en el rechazo. El DTO solo tipa; no impone los ceros ni
    la precedencia (ROSTER_VALIDATION_FAILED → INTRA_BATCH_DUPLICATE_ID; IDENTITY_BARRED solo en
    rule_ids de la fila identity_status, R9-01) y no añade validadores nuevos ni lógica de negocio.
    STRICT = abortar el lote completo, sin segregar (R3-04). El cuerpo 422 es
    siempre `application/problem+json`, sea el input JSON o CSV; se ignora
    `Accept` (R3-05) [ADOPTED 2026-10-13, estudiante].
    """

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: Literal[
        "ROSTER_VALIDATION_FAILED",
        "INTRA_BATCH_DUPLICATE_ID",
    ]
    errors: list[RosterRejectedManifestRow]
    batch_id: str
    explanation: ExplanationDTO
    processed: int
    created_identities: int
    updated_memberships: int
