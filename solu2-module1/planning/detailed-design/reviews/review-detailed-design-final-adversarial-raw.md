- Quién puede invocar `revokeCourseAccess` e `ingestRoster` no está definido. `contracts.md` §2 (P1–P4) y §3 (P1–P4) solo exigen 401 por token inválido; ningún P/Q/I restringe al llamador por rol, titularidad del token o pertenencia al curso. `roles_matrix.v0.json` solo cubre `resolveEffectivePermissions`. Un agente de implementación tendría que decidir quién puede dar de baja o cargar nóminas.

- El contrato del token Bearer no existe. No hay formato, emisor, validación ni mapeo del sujeto del token a `actor_id`/`actor_role`. `AUTH_TOKEN_INVALID` (contracts §4, 401) no puede implementarse sin inventar la fuente de identidad del llamador. Tampoco se relaciona con `subject_credentials` (`uai_live_…`), que es la única credencial modelada en el DDL.

- `audit_ledger` declara NOT NULL `actor_id`, `actor_role`, `resource_arn` (CHECK GLOB `urn:uai:subject:*:model:*`) y `action` (`001_module1.sql` §7), pero los payloads de `membership.revoked`, `roster.ingested` y `roster.rejected` (`events.md` §2) no tienen actor, ARN ni acción. Insertar el evento de baja o de lote exige valores inventados.

- El mapeo ledger (`decision`, `reason_code`) de `roster.ingested` y `roster.rejected` no está definido. R3-03 solo cubre `membership.revoked` (DENY/SUBJECT_ENROLLMENT_DROPPED) y `escalation.expired`. `decision` solo admite ALLOW/DENY y `reason_code` es NOT NULL, así que el éxito y el rechazo de lote quedan sin valor.

- `contracts.md` §1 declara la concurrencia de `resolveEffectivePermissions` como "lectura pura", pero Q3 exige un evento `authorization.decided` por decisión, encadenado en `audit_ledger` a través de la cola y `LedgerWriter` (BEGIN IMMEDIATE). Cada autorización es una escritura serializada en el único writer. La afirmación de lectores WAL "sin BEGIN IMMEDIATE" y el presupuesto p95 < 20 ms no se sostienen sin análisis.

- La matriz v0 no contiene ninguna fila para el rol `ta`. El Mandatory Edge Case (TA en CS-480) y EDGE-01 exigen que cada contexto se resuelva de forma independiente, pero con esta matriz la TA en CS-480 recibe siempre `UNAUTHORIZED_RESOURCE_CLASS`. El caso no demuestra nada salvo denegación.

- Las filas de la matriz no son ejecutables. `allows` es texto libre ("inferencia 8B en workstations de 24 GB") y no hay claves de `action` (p. ej. `model:invoke`), clase de recurso ni modelo. Dos implementaciones no convergerían, lo que contradice el objetivo declarado en F-02.

- La denegación por membresía no activa tiene dos códigos posibles. `contracts.md` §1 P5 asigna `SUBJECT_CONTEXT_MISSING_OR_UNAUTHORIZED` a membresía no activa; "Respuesta tras revocación" asigna `SUBJECT_ENROLLMENT_DROPPED` a la baja; la precedencia (paso 6, "membresía no activa") no nombra ningún código. El texto no refleja la decisión adoptada.

- El instante `at` acepta `null` en la firma de dominio (`contracts.md` §0: `at: str | null`; `ports-and-adapters.md` §1 lo replica), pero AD-13 del spine dice que `null` produce `INVALID_AT`. El comportamiento de la ruta interna con `at=null` es contradictorio.

- Los ejemplos del paquete no cumplen la regla adoptada. `dto.py` (AuthorizeRequest, ejemplo) usa `urn:uai:subject:cs-480:model:llama-3-8b` y `openapi.yaml` usa `X-Academic-Subject-Context: CS-480`. Con comparación byte-a-byte (AD-01 adoptado), esa pareja produce `RESOURCE_SUBJECT_MISMATCH`. Los ejemplos contradicen la regla del propio contrato.

- Los DTO de entrada declaran restricciones de Pydantic que colisionan con el catálogo: `RosterIngestRequest.rows` con min_length=1 y max_length=1000 (`dto.py`), `RevokeRequest.drop_reason` de 1 a 280, y campos requeridos de `AuthorizeRequest`. FastAPI responde 422 por defecto, mientras el contrato exige 413 `BATCH_TOO_LARGE` antes de parsear, 400 `BATCH_EMPTY` y 400 `MALFORMED_DROP_REASON`. No hay handler de `RequestValidationError` especificado.

- `contracts.md` §3 P1 dice "term discrepante → siempre MALFORMED_TERM 400" y en la misma cláusula "→ UNKNOWN_COURSE 404 / MALFORMED_TERM 400". No se decide cuándo aplica cada código, ni si `term` debe igualar `subjects.term` del DDL para ese curso.

- `subject_memberships` no tiene columna `term` y `subjects.id` es la PK, así que el mismo curso no puede existir en dos términos. H-20 ("mismo curso/term") y la validación de `term` en la ingesta no son implementables con el DDL actual.

- H-20 devuelve 422 por rol distinto en una membresía previa, pero `RosterRejectedManifest.code` (`dto.py` y `openapi.yaml`) solo admite `ROSTER_VALIDATION_FAILED`, `INTRA_BATCH_DUPLICATE_ID` e `IDENTITY_BARRED`. El código del rechazo por role smuggling no existe en el manifiesto ni en la precedencia de `contracts.md` §3.

- H-20 fija "mismo rol sobre DROPPED → sin cambios". No dice qué ocurre con el mismo rol sobre SUSPENDED o COMPLETED, ni si la fila cuenta como `updated_memberships`.

- `contracts.md` §3 Q2 afirma que el lote persiste credenciales `uai_live_…` "solo en claro aquí", pero `RosterIngestResponse` (`dto.py` y `openapi.yaml`) no tiene campo de credencial ni existe canal de entrega. La clave emitida no llega a ningún actor.

- La búsqueda de credenciales no es implementable. `key_hash = SHA-256(salt || raw_key)` con salt por fila (`001_module1.sql` §6) impide calcular el hash del token recibido sin conocer el salt, y el índice `idx_credentials_lookup(key_hash, status)` no sirve para esa búsqueda. No hay índice por `key_prefix`.

- `revoked_credentials_cache` (AD-03, AD-12, H-22) no tiene dueño, ubicación, invalidación ni mecanismo de propagación. Si solo puede adelantar DENY, no es necesaria para la corrección; si es necesaria para el NFR de 200 ms, el contrato no dice cómo se cumple.

- Conflictos de identidad dentro del lote sin regla. `identities.institutional_id` y `identities.email` son UNIQUE (`001_module1.sql` §1). No se define qué pasa si una fila trae un `institutional_id` existente con otro email o nombre (¿actualizar? ¿rechazar?), ni si un email ya usado por otro `institutional_id` produce un código. La violación de UNIQUE escaparía como error no mapeado.

- `processed` del 201 no está definido (filas recibidas, válidas o procesadas). Tampoco se define si `created_identities` y `updated_memberships` cuentan filas sin cambio. El conteo de éxito no se puede verificar en los tests.

- `contracts.md` §0 y §3 P3 invocan una "gramática alfanumérica con guiones ya definida" para `institutional_id`, pero ningún artefacto del paquete la define con precisión. `dto.py` y `openapi.yaml` dicen explícitamente "sin patrón inventado". La validación del boundary no tiene una fuente verificable.

- El índice único `idx_single_active_escalation` (`001_module1.sql` §5) incluye `ACTIVE` aunque el ticket ya haya vencido por `expires_at` hasta el siguiente barrido de 1 s. `resolveEffectivePermissions` trata ese ticket como expirado (AD-13), pero el DDL lo sigue tratando como activo; el resultado depende del reloj del barrido.

- Los CHECK y las consultas del scheduler comparan timestamps como TEXT (`expires_at > granted_at`, `granted_at <= now`). El DDL no impone un formato fijo de fracción de segundos, así que cadenas con y sin microsegundos se ordenan mal lexicográficamente.

- `audit_ledger_metadata` (`head_record_hash`, `total_events_count`) no tiene triggers de protección y se actualiza en cada evento. Cualquier proceso con acceso a la BD puede reescribir el ancla sin dejar rastro distinto de la cadena. El "anclaje anti Tail-Truncation" solo funciona si se verifica contra una copia externa, y ninguna operación del módulo lo hace.

- Las tablas `roles` y `subjects` no tienen seed en el DDL, pero `subject_memberships` tiene FK a ambas (`001_module1.sql` §4). Las fixtures de EDGE-01 (CS101/CS-480, roles student/ta) no tienen de dónde salir según el DDL tal como está.
