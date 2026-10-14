# Review Rubric — Architecture Spine Módulo 1 (2026-10-13, segunda pasada)

- Fecha: 2026-10-13
- Rol: rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura; no se editó ningún fuente salvo este reporte)
- Alcance: juzgar spine + contracts contra el good-spine checklist en la versión con 8 decisiones [ADOPTED] 2026-10-13 (D1–D8)
- Fuentes leídas (rutas absolutas):
  - `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md`
  - `solu2-module1/planning/detailed-design/contracts.md`
  - `resultados-interaccion.md`
  - `planning/ARCHITECTURE.md` y `planning/prd.md` (solo secciones citadas)
- Escala: ROBUSTO / CONDITIONAL / NOT READY
- Veredicto: **ROBUSTO**

## Veredicto

**ROBUSTO.** Las 8 decisiones [ADOPTED] 2026-10-13 (D1–D8) están fijadas de forma coherente entre spine y contracts, sin debilitar AD-01..AD-07, con las 3 operaciones + EDGE-01 cubiertas, cada AD exigible y preventivo, nada en Deferred que permita divergir, y todos los pendientes dejados explícitamente abiertos sin cobertura inventada. Los únicos hallazgos son editoriales/trazabilidad (etiqueta [OPEN-01] residual, fecha `updated` y `resultados-interaccion.md` estancado, wording `Query instant`, convención `:` vs `.` en eventos) y ninguno permite divergencia de implementación.

## Good-spine checklist (juicio punto por punto)

### 1. Divergencias reales fijadas sin omitir (D1–D8)

Todas fijadas en ambos documentos con etiqueta [ADOPTED 2026-10-13]:

- D1 fórmula hash normativa AD-04 §5 con `subject_id`/`action` (§2 resumido como incompleto): spine `ARCHITECTURE-SPINE.md:48`, contracts `contracts.md:32`. Cita `planning/ARCHITECTURE.md:364-365` como normativa frente a resumen incompleto `planning/ARCHITECTURE.md:95-96`. Fijada, sin editar Plan-2.
- D2 `at` en body JSON de authorize opcional, `term` en query para CSV y campo body para JSON: spine `ARCHITECTURE-SPINE.md:65`, contracts `contracts.md:13,15,17,25`. Fijada.
- D3 roster 422 con rollback total y después evento `roster.rejected` en tx separada, cola no acepta → 503: spine `ARCHITECTURE-SPINE.md:97`, contracts `contracts.md:78,80` + fila ligada `contracts.md:133`. Fijada.
- D4 cola micro-batching 50ms/50ev sin descarte, llena → 503, capacidad máxima pendiente TEA/NFR, recuperación post-persistencia pendiente: spine `ARCHITECTURE-SPINE.md:97`, contracts `contracts.md:142` + abiertos `contracts.md:154`. Hereda `planning/ARCHITECTURE.md:367`. Fijada sin inventar capacidad/recuperación.
- D5 reingesta sin idempotencia por contenido, `batch_id` nuevo, regeneración de credenciales pendiente: spine `ARCHITECTURE-SPINE.md:83`, contracts `contracts.md:85,151`. Fijada sin inventar regen.
- D6 scheduler auto-revoca + `resolve` deniega desde `now>=expires_at` aunque no haya persistido, frecuencia pendiente TEA/NFR: spine `ARCHITECTURE-SPINE.md:89`, contracts `contracts.md:37,41`. Cita `planning/prd.md:162` (R5 scheduler) y `planning/prd.md:317-318` (`now>=exp`). Fijada; solo-perezosa eliminada como equivalente.
- D7 post-revocación unificado a 403 `SUBJECT_ENROLLMENT_DROPPED` (PRD admite 401/403): spine `ARCHITECTURE-SPINE.md:97`, contracts `contracts.md:28,63`. Cabe en `planning/prd.md:190` (`401 / 403`) + `planning/prd.md:251-281` (§5.2). Fijada como elección unificada documentada, no como imposición del PRD.
- D8 UUID formato estándar, espacios externos rechazados sin recorte, case UUID pendiente; `courseId` crudo byte-a-byte AD-01; `institutional_id`/`term` case-sensitive: spine `ARCHITECTURE-SPINE.md:96`, contracts `contracts.md:17,71,73`. Cita `planning/ARCHITECTURE.md:329-331`. Fijada salvo case-UUID declarado pendiente.

Sin omisiones respecto al encargo de 8 decisiones.

### 2. Cada AD exigible y preventivo

- Heredados AD-01..AD-07 marcados read-only, no renumerados: `ARCHITECTURE-SPINE.md:41` + `contracts.md:5,125`.
- Locales AD-08..AD-13 cada uno con Binds + Prevents + Rule: `ARCHITECTURE-SPINE.md:55-89`. Cumple exigibilidad (regla verificable por máquina) y carácter preventivo (divergencia que impide).
- Ligado invariante → enforcement → test RED sin punteros inventados: `contracts.md:125,127-147`. Cada fila declara punto de enforcement nominal y test RED.

### 3. Nada en Deferred permite divergir

`ARCHITECTURE-SPINE.md:130-136`: migración SQLite→PostgreSQL condicionada a benchmark real, guard monotónico NTP (DEFER post-V1), barrido `INACTIVE`, `COMPLETED`/`EXPIRED` ajenos a las tres ops, flujos de escalación fuera de las tres ops, cuota GPU fuera por [ASSUMPTION-01]. Ninguna cláusula autoriza a violar AD-01..AD-13 ni a exponer otra ruta. Correctamente diferido.

### 4. AD-01..AD-07 sin debilitar

- AD-01: comparación cruda byte-a-byte header vs subject ARN, sin `strip`/`upper`, mismatch → 403; regex ARN preservada: `ARCHITECTURE-SPINE.md:45`, `contracts.md:17,27,131` frente a `planning/ARCHITECTURE.md:329-331`. Normalización retirada como alternativa. Sin debilitar.
- AD-02: `BEGIN IMMEDIATE`, `seen_ids`, rollback total, anti-role-smuggling: `ARCHITECTURE-SPINE.md:46`, `contracts.md:81-84,132-135`. Sin debilitar.
- AD-03: `workers: 1`, `busy_timeout 5000`, `ALREADY_REVOKED` sin evento redundante, predicado condicional: `ARCHITECTURE-SPINE.md:47,83`, `contracts.md:40,53-58` frente a `planning/ARCHITECTURE.md:352-354`. Alternativa local sin caché eliminada. Sin debilitar.
- AD-04: fórmula §5 + metadata singleton + verificación `id ASC` + micro-batching 50ms/50ev: `ARCHITECTURE-SPINE.md:48`, `contracts.md:32,142` frente a `planning/ARCHITECTURE.md:364-368`. Ventana 50ms preservada, no convertida en sync. Sin debilitar.
- AD-05: índice único parcial como guarda física, auto-aprobación prohibida; creación de escalaciones fuera de las tres ops, solo respaldo: `ARCHITECTURE-SPINE.md:49`, `contracts.md:140-141` frente a `planning/ARCHITECTURE.md:372-381`. Sin debilitar.
- AD-06: máscara `uai_live_<4>••••<4>`, test regex build: `ARCHITECTURE-SPINE.md:50`, `contracts.md:38,143` frente a `planning/ARCHITECTURE.md:385-390`. Sin debilitar.
- AD-07: clamp `[1,100]`, cursor `(timestamp,id)`, respaldo Empty/Error: `ARCHITECTURE-SPINE.md:51`, `contracts.md:119,145` frente a `planning/ARCHITECTURE.md:394-399`. Sin debilitar.

### 5. Las 3 operaciones + EDGE-01 cubiertas

- `resolveEffectivePermissions`: `contracts.md:19-42` (P/Q/I + concurrencia + tiempo + NFR). Binds AD-01/AD-10/AD-11/AD-13.
- `revokeCourseAccess`: `contracts.md:44-65`. Binds AD-03/AD-12.
- `ingestRoster`: `contracts.md:67-88`. Binds AD-02/AD-12.
- EDGE-01 + Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»): spine `ARCHITECTURE-SPINE.md:67-71` (fixture dual, tupla `(identity_id,course_id)`, sin cuota GPU por [ASSUMPTION-01]), contracts `contracts.md:31,36,39` (Q2/I1/I4). Relación con `planning/prd.md:240-281` (§5) explícita. La aserción cruda que iguala ambos contextos a `Student` queda rechazada en spine. Cubierto.

### 6. Cada dimensión decidida / diferida / abierta

| Dimensión | Estado | Evidencia |
| --- | --- | --- |
| Transporte `at`/`term` | Decidida (D2) | `ARCHITECTURE-SPINE.md:65`, `contracts.md:13,15,17,25` |
| Hash ledger | Decidida (D1) | `ARCHITECTURE-SPINE.md:48`, `contracts.md:32` |
| Roster 422 + `roster.rejected` | Decidida (D3) | `ARCHITECTURE-SPINE.md:97`, `contracts.md:78,80,133` |
| Cola llena → 503 | Decidida (D4) | `ARCHITECTURE-SPINE.md:97`, `contracts.md:133,142` |
| Capacidad cola / recuperación | Abierta TEA/NFR | `ARCHITECTURE-SPINE.md:97`, `contracts.md:142,154` |
| Reingesta (no idempotente) | Decidida (D5) | `ARCHITECTURE-SPINE.md:83`, `contracts.md:85,151` |
| Regeneración credenciales | Abierta | `ARCHITECTURE-SPINE.md:83`, `contracts.md:85,151` |
| Scheduler + borde `>=` | Decidida (D6) | `ARCHITECTURE-SPINE.md:89`, `contracts.md:37,41` |
| Frecuencia scheduler | Abierta TEA/NFR | `ARCHITECTURE-SPINE.md:89`, `contracts.md:41,154` |
| Post-revocación 403 | Decidida (D7) | `ARCHITECTURE-SPINE.md:97`, `contracts.md:28,63` |
| UUID / espacios / case | Decidida salvo case-UUID abierto (D8) | `ARCHITECTURE-SPINE.md:96`, `contracts.md:17,154` |
| `courseId` byte-a-byte / `institutional_id`+`term` case-sensitive | Decidida | `ARCHITECTURE-SPINE.md:96`, `contracts.md:17,71,73` |
| Ubicación HTTP `timestamp` baja | Abierta | `contracts.md:51,154` (firma Annex A sin cambiar, instante vía `Clock`) |
| `COMPLETED` actor/momento, TTL `EXPIRED` | Abierta/diferida | `ARCHITECTURE-SPINE.md:134`, `contracts.md:49,87,154` |
| Matriz rol×acción / `roles_matrix.json` inexistente | Abierta, sin inventar | `contracts.md:154` |
| NFR datasets / concurrencia nominal | Abierta (PLANNED) | `contracts.md:42,65,88,154` |

Ninguna dimensión queda sin estado.

### 7. Coherencia interna spine ↔ contracts

- Transporte: idéntico en `ARCHITECTURE-SPINE.md:65` y `contracts.md:13,15,17`. Coherente (salvo wording menor H-3).
- `roster.rejected`: rollback total + evento posterior en tx separada + 503 si cola no acepta en ambos (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:78,80,133`). Coherente (salvo convención `:` vs `.` H-4).
- Cola: micro-batching 50ms/50ev, worker secuencial, sin descarte, llena → 503 en ambos (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:142-143`). Coherente con `planning/ARCHITECTURE.md:367`.
- Scheduler: auto-revoca + denegación `now>=expires_at` aun sin persistir + frecuencia pendiente en ambos (`ARCHITECTURE-SPINE.md:89` ↔ `contracts.md:37,41`). Coherente con `planning/prd.md:162,317-318`.
- 403: unificado con nota PRD admite 401/403 en ambos (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:28,63`). Coherente con `planning/prd.md:190,251-281`.
- UUID/espacios/case + `courseId`/`institutional_id`/`term`: idéntico en `ARCHITECTURE-SPINE.md:96` y `contracts.md:17,71,73`. Coherente con `planning/ARCHITECTURE.md:329-331` (salvo etiqueta [OPEN-01] residual H-1).

### 8. Pendientes abiertos sin cobertura inventada

Verificado que quedan abiertos y sin permisos/comportamientos inventados: matriz rol×acción (`roles_matrix.json` inexistente, sin matriz inventada), capacidad cola, recuperación post-persistencia, frecuencia scheduler, ubicación `timestamp`, `COMPLETED`, TTL, NFR datasets, regeneración credenciales, case UUID. Evidencia central: `contracts.md:151-154` + `ARCHITECTURE-SPINE.md:83,89,96-97,130-136`. Ningún test RED afirma cobertura de esos pendientes: `contracts.md:127-147` solo liga lo decidido/heredado.

## Hallazgos (ordenados por severidad; ninguno bloqueante)

- H-1 (menor, consistencia de etiquetas): etiqueta `[OPEN-01] sigue abierto` para `courseId` convive con regla [ADOPTED] byte-a-byte en el mismo párrafo. Ver `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:96` y `solu2-module1/planning/detailed-design/contracts.md:17`. La regla normativa es clara (AD-01 sin modificar, sin `strip`/`upper`), por lo que no permite divergir; queda como deuda de limpieza: cerrar o redefinir [OPEN-01] a lo que realmente siga abierto, si algo queda.
- H-2 (menor, trazabilidad): `ARCHITECTURE-SPINE.md:10` conserva `updated: '2026-10-12'` aunque contiene 8 decisiones [ADOPTED 2026-10-13]; `resultados-interaccion.md:1-10` describe Fase 1 (7 puntos, hash abierto, 401/403 abierto, Fase 2 intacta) y ya no refleja D1–D8. No afecta el contrato porque la autoridad vigente son spine + contracts con citas a Plan-2, pero conviene no usar `resultados-interaccion.md` como evidencia de D1–D8.
- H-3 (editorial): plantilla `INVALID_AT` dice `Query instant` en `solu2-module1/planning/detailed-design/contracts.md:97` mientras el transporte fijado es body JSON (`contracts.md:13,17,25` + `ARCHITECTURE-SPINE.md:65`). No cambia P3/Q ni status 400; unificar wording a `Request instant`.
- H-4 (editorial): convención de nombres de eventos mezcla `roster:ingest` (dos puntos) y `roster.rejected` (punto) en `solu2-module1/planning/detailed-design/contracts.md:78`. La semántica (tx separada, 503 sin descarte) es coherente con `ARCHITECTURE-SPINE.md:97`; unificar separador sin cambiar semántica.
- H-5 (positivo, no es defecto): tabla de ligado `contracts.md:127-147` evita punteros archivo:línea/función/SQL inventados (`contracts.md:125`) y deja respaldo fuera de las tres ops explícitamente marcado (`contracts.md:140,145`). Esa contención es la que sostiene el veredicto ROBUSTO pese a la matriz pendiente.

## Trazabilidad a Plan-2 (muestra)

- AD-01 byte-a-byte + regex ARN: `planning/ARCHITECTURE.md:329-331` ↔ `ARCHITECTURE-SPINE.md:45` ↔ `contracts.md:17,27`.
- Hash §5 normativa vs §2 resumen: `planning/ARCHITECTURE.md:364-365` vs `planning/ARCHITECTURE.md:95-96` ↔ `contracts.md:32` ↔ `ARCHITECTURE-SPINE.md:48`.
- Cola 50ms/50ev: `planning/ARCHITECTURE.md:367` ↔ `ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:142`.
- Scheduler + borde: `planning/prd.md:162` + `planning/prd.md:317-318` ↔ `ARCHITECTURE-SPINE.md:89` ↔ `contracts.md:37,41`.
- Auth 401/403 y post-revocación: `planning/prd.md:190,251-281` ↔ `ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:28,63`.
- Sin cuota GPU en resolve: `planning/prd.md:352` ([ASSUMPTION-01]) ↔ `ARCHITECTURE-SPINE.md:71` ↔ `contracts.md:39`.
- Fail-closed 503: `planning/prd.md:329-330` ↔ `contracts.md:62,78,86`.
- `roles_matrix.json` inexistente como bloqueador declarado, no inventado: `planning/ARCHITECTURE.md:415` (ruta prevista) ↔ `contracts.md:154`.

## Nota de método

No se ejecutó ningún workflow BMad, no se editó ningún fuente, no se corrió gate ni build. Juicio solo por lectura de las rutas citadas. Los pendientes listados en el encargo quedan todos abiertos en `contracts.md:151-154` sin cobertura inventada; cerrar cualquiera de ellos requeriría decisión humana/fuente, no suposición del spine.
