# Review Rubric — Architecture Spine Módulo 1 (2026-10-13, tercera pasada)

- Fecha: 2026-10-13
- Rol: rubric walker del Reviewer Gate de `bmad-architecture` (solo lectura; no se editó ningún fuente salvo este reporte)
- Alcance: juzgar spine + contracts contra el good-spine checklist en la versión con 16 decisiones [ADOPTED] N-01..N-16 + 4 editoriales
- Fuentes leídas (rutas absolutas):
  - `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md`
  - `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/contracts.md`
  - `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md`
  - `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/planning/ARCHITECTURE.md` y `planning/prd.md` (solo secciones citadas)
  - `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/solu2-module1/planning/detailed-design/architecture-spine/.memlog.md` (solo como índice de decisiones N-01..N-16, sin tomarlo como autoridad normativa)
- Escala: ROBUSTO / CONDITIONAL / NOT READY (criterio sin relajar para obtener PASS)
- Veredicto: **CONDITIONAL**

## Veredicto

**CONDITIONAL.** Las 16 decisiones N-01..N-16 están presentes y son coherentes en lo grueso entre spine y contracts sin debilitar AD-01..AD-07, con las 3 operaciones + EDGE-01 cubiertas y los pendientes declarados sin cobertura inventada; pero subsisten divergencias reales fijables (disyunción de código en `term`, auditoría de fallos P1–P4 que afecta la cadena, límites N-14 solo en contracts, matriz rol×acción bloqueante) que impiden ROBUSTO. No hay debilitamiento heredado ni operaciones faltantes que exijan NOT READY.

## Good-spine checklist (juicio punto por punto)

### 1. Divergencias N-01..N-16 fijadas (sin omitir, con reservas)

- N-01 codec hash (UTF-8 / orden §5 / prev-hex / nulos explícitos / FIFO-id ASC): fijada en `ARCHITECTURE-SPINE.md:48` y `contracts.md:34` + `contracts.md:145`. Cita `planning/ARCHITECTURE.md:364-365` como normativa frente a resumen incompleto `planning/ARCHITECTURE.md:95-96`. Reserva H-8 (nulos sin bytes definidos).
- N-02 `at` (solo ausencia → `Clock.now`; `null`/vacío/espacios/sin-zona/sin-micro → `INVALID_AT`; histórico válido evalúa ese instante; scheduler con reloj propio): fijada en `ARCHITECTURE-SPINE.md:89` y `contracts.md:19,27,32,43`. Reserva menor (tipos no-string no listados, pero caen en `INVALID_AT` por P3).
- N-03 `term` exclusivo (CSV solo query / JSON solo body; canal indebido, duplicado, discrepancia o ausencia se rechaza sin elegir valor): fijada en intención en `ARCHITECTURE-SPINE.md:65` y `contracts.md:15,74`. **No fijada en código**: disyunción `MALFORMED_TERM` o `MALFORMED_BATCH` permite divergir → H-1.
- N-04/N-05 roster 422 (rollback total, luego `roster.rejected` en misma cadena única 1:1, 422 tras aceptación sin espera de persistencia): fijada en `ARCHITECTURE-SPINE.md:97` y `contracts.md:81,83,136`. Reserva H-2/H-11.
- N-06 cola (50 ms / 50 ev, worker secuencial, reserva previa al commit, llena o no-aceptado → 503, aceptado → respuesta puede preceder persistencia): fijada en `ARCHITECTURE-SPINE.md:97` y `contracts.md:34,57,81,145`. Hereda `planning/ARCHITECTURE.md:367`. Reserva H-5 (reserva sin capacidad/protocolo ejecutable; capacidad y recuperación pendientes declarados en `contracts.md:154`).
- N-07/N-08 expiración (scheduler dueño único, máx. un evento por transición; `resolve` no muta y evalúa contra `at` pedido incluso histórico; scheduler contra reloj actual; `at >= expires_at` deniega): fijada en `ARCHITECTURE-SPINE.md:89` y `contracts.md:37,39,43`. Cita `planning/prd.md:162` (R5) y `planning/prd.md:317-318` (borde). Frecuencia pendiente declarada.
- N-09 precedencia auth (primero 401, luego 403; post-baja 403 unificado): fijada en `ARCHITECTURE-SPINE.md:97` y `contracts.md:30,64,66`. Cabe en `planning/prd.md:190` (`401 / 403`) + `planning/prd.md:251-281` (§5.2) como elección unificada documentada.
- N-10 `userId` (UUID válido → UUID, si no `institutional_id` exacto; whitespace externo/interno y controles rechazados sin recorte; no resuelve → `UNKNOWN_IDENTITY` existente): fijada en `ARCHITECTURE-SPINE.md:96` y `contracts.md:19,25`. Case-folding UUID abierto declarado (`contracts.md:19,154`) → H-10.
- N-11 reingesta (no idempotente, `batch_id` nuevo, conteos en tx serializada `BEGIN IMMEDIATE`; 8hex sin garantía, colisión pendiente; reemisión credenciales pendiente): fijada en `ARCHITECTURE-SPINE.md:83` y `contracts.md:88,151`. Sin código inventado.
- N-12 contexto rutas (header obligatorio solo `/authorize`; revoke/ingest usan path param canónico sin header adicional; AD-01 sin extender): fijada en `ARCHITECTURE-SPINE.md:65` y `contracts.md:17`. Reserva H-7 (header presente pero no exigido: ignorar vs rechazar).
- N-13 normalización (`institutional_id`/`term`/`seen_ids` exactos; dominio email case-insensitive sin tocar resto ni reescribir; sin folding en otros campos): fijada en `ARCHITECTURE-SPINE.md:96` y `contracts.md:76-77`. Reserva H-10 (local-part).
- N-14 límites (5 MB = 5.000.000 bytes; exceso bytes/filas → `BATCH_TOO_LARGE` 413 antes de validar filas; `drop_reason` 1–280 caracteres Unicode sin normalizar): **solo en contracts** (`contracts.md:75,52` + catálogo `contracts.md:105-106`). Spine silencioso (`ARCHITECTURE-SPINE.md:96-97` no los nombran) → H-3.
- N-15 replay/DTO (orden auth → identidad/curso → `DROPPED` antes de P3 con timestamp original; `ExplanationDTO` en ALLOW/DENY y rechazos de negocio; 400/401/404 con `ErrorBody` sin DTO obligatoria): fijada en intención en `contracts.md:54,61,124` + `ARCHITECTURE-SPINE.md:77`. Reservas H-6 (orden solo en contracts) y H-9 (409 ambiguo).
- N-16 serialización (`BEGIN IMMEDIATE` en mutaciones; prohibido leer-luego-actualizar; `busy_timeout 5000`, agotado → 503 sin commit parcial; eventos FIFO-aceptación, `id ASC` ordena hash): fijada en `ARCHITECTURE-SPINE.md:47,83,107` y `contracts.md:57,89,145`. Reserva (frase «sentencia condicional única» sin SQL definido).

Editoriales declaradas:

- Etiqueta `[OPEN-01]` residual retirada: verificado, ya no aparece en spine ni contracts. Cumplida.
- `updated` spine a 2026-10-13: `ARCHITECTURE-SPINE.md:10` cumplida.
- Plantilla `INVALID_AT` a body: `contracts.md:100` dice `Request instant ... (body)`. Cumplida (corrige H-3 de la pasada 2).
- `roster.rejected` unificado: parcial. `ARCHITECTURE-SPINE.md:97` y `contracts.md:81,136` usan `roster.rejected` (punto), pero `contracts.md:81` conserva `roster:ingest` (dos puntos) → H-11.

### 2. Cada AD exigible y preventivo

- Heredados AD-01..AD-07 marcados read-only, no renumerados: `ARCHITECTURE-SPINE.md:41` + `contracts.md:5,125`. Cumple.
- Locales AD-08..AD-13 con Binds + Prevents + Rule: `ARCHITECTURE-SPINE.md:55-89`. Estructura cumple; exigibilidad real con reservas H-1, H-5, H-8 (disyunción de código, reserva sin protocolo, nulos sin bytes).
- Ligado invariante → enforcement → test RED sin punteros inventados: `contracts.md:125,127-150`. Contención explícita (`contracts.md:125`) sostiene el juicio; ningún RED afirma pendientes.

### 3. Nada en Deferred permite divergir

`ARCHITECTURE-SPINE.md:130-136`: migración SQLite→PostgreSQL condicionada a benchmark real, guard monotónico NTP DEFER post-V1, barrido `INACTIVE`, `COMPLETED`/`EXPIRED` ajenos a las tres ops, flujos de escalación fuera de las tres ops, cuota GPU fuera por [ASSUMPTION-01]. Ninguna cláusula autoriza violar AD-01..AD-13 ni exponer otra ruta. Correctamente diferido. La matriz rol×acción no está en Deferred sino en abiertos (`contracts.md:154`); no se escuda en Deferred → se juzga en §6/§8 y H-4.

### 4. AD-01..AD-07 sin debilitar

- AD-01: byte-a-byte crudo header vs subject ARN, sin `strip`/`upper`, mismatch → 403 + regex ARN: `ARCHITECTURE-SPINE.md:45`, `contracts.md:17,27,131` frente a `planning/ARCHITECTURE.md:329-331`. Normalización retirada. Sin debilitar.
- AD-02: `BEGIN IMMEDIATE`, `seen_ids`, rollback total, anti-role-smuggling: `ARCHITECTURE-SPINE.md:46`, `contracts.md:81-84,132-135` frente a `planning/ARCHITECTURE.md:340-343`. Sin debilitar.
- AD-03: `workers: 1`, `busy_timeout 5000`, `ALREADY_REVOKED` sin evento redundante: `ARCHITECTURE-SPINE.md:47,83`, `contracts.md:40,53-58` frente a `planning/ARCHITECTURE.md:352-354`. Alternativa sin caché eliminada. Sin debilitar.
- AD-04: fórmula §5 + metadata singleton + verificación `id ASC` + micro-batching 50 ms/50 ev: `ARCHITECTURE-SPINE.md:48,97`, `contracts.md:32,142,145` frente a `planning/ARCHITECTURE.md:364-368`. Ventana 50 ms preservada, no convertida en sync. Elección §5 frente a resumen §2 documentada como interpretación sin editar Plan-2. Sin debilitar (con reserva H-8 de codec).
- AD-05: índice único parcial como guarda física, auto-aprobación prohibida; creación de escalaciones fuera de las tres ops solo respaldo: `ARCHITECTURE-SPINE.md:49`, `contracts.md:143` frente a `planning/ARCHITECTURE.md:372-381`. Sin debilitar.
- AD-06: máscara `uai_live_<4>••••<4>`, test regex build: `ARCHITECTURE-SPINE.md:50`, `contracts.md:40,146` frente a `planning/ARCHITECTURE.md:385-390`. Sin debilitar.
- AD-07: clamp `[1,100]`, cursor `(timestamp,id)`, respaldo Empty/Error: `ARCHITECTURE-SPINE.md:51`, `contracts.md:122,148` frente a `planning/ARCHITECTURE.md:394-399`. Sin debilitar.

### 5. Las 3 operaciones + EDGE-01 cubiertas

- `resolveEffectivePermissions`: `contracts.md:21-44` (P/Q/I + concurrencia + tiempo + NFR). Binds AD-01/AD-10/AD-11/AD-13.
- `revokeCourseAccess`: `contracts.md:46-68`. Binds AD-03/AD-12.
- `ingestRoster`: `contracts.md:70-91`. Binds AD-02/AD-12.
- EDGE-01 + Mandatory Edge Case literal («Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently»): `ARCHITECTURE-SPINE.md:67-71` (fixture dual, tupla `(identity_id,course_id)`, sin cuota GPU por [ASSUMPTION-01]), `contracts.md:33,38,41` (Q2/I1/I4). Aserción cruda que iguala ambos contextos a `Student` rechazada en spine. Relación con PRD §5 (`planning/prd.md:240-281`) explícita. Cubierto estructuralmente; contenido rol×acción pendiente → H-4.

### 6. Cada dimensión decidida / diferida / abierta

| Dimensión | Estado | Evidencia |
| --- | --- | --- |
| Codec hash + orden | Decidida con reserva | `ARCHITECTURE-SPINE.md:48`, `contracts.md:34,145` (reserva H-8) |
| Transporte `at` | Decidida | `ARCHITECTURE-SPINE.md:65,89`, `contracts.md:13,19,27` |
| Transporte `term` + código | Decidida en intención, no en código | `ARCHITECTURE-SPINE.md:65`, `contracts.md:15,74` (H-1) |
| Roster 422 + `roster.rejected` | Decidida | `ARCHITECTURE-SPINE.md:97`, `contracts.md:81,83,136` |
| Auditoría de P1–P4 en resolve | Ambigua (permite divergir) | `contracts.md:34,36` vs `contracts.md:60` (H-2) |
| Cola llena → 503 + reserva | Decidida con reserva ejecutable | `ARCHITECTURE-SPINE.md:97`, `contracts.md:57,145` (H-5) |
| Capacidad cola / recuperación post-aceptación | Abierta TEA/NFR | `ARCHITECTURE-SPINE.md:97`, `contracts.md:145,154` |
| Reingesta no idempotente + conteos | Decidida | `ARCHITECTURE-SPINE.md:83`, `contracts.md:88` |
| Colisión `batch_id` / reemisión credenciales | Abierta | `contracts.md:88,154` |
| Scheduler + borde `>=` + relojes | Decidida | `ARCHITECTURE-SPINE.md:89`, `contracts.md:39,43` |
| Frecuencia scheduler | Abierta TEA/NFR | `ARCHITECTURE-SPINE.md:89`, `contracts.md:43,154` |
| Precedencia 401→403 + post-baja 403 | Decidida | `ARCHITECTURE-SPINE.md:97`, `contracts.md:30,66` |
| `userId`/UUID/espacios | Decidida salvo case-UUID abierto | `ARCHITECTURE-SPINE.md:96`, `contracts.md:19,25,154` |
| `courseId` byte-a-byte / `institutional_id`+`term` case-sensitive / email dominio | Decidida (salvo local-part) | `ARCHITECTURE-SPINE.md:96`, `contracts.md:19,76-77` (H-10) |
| Contexto rutas (header solo authorize) | Decidida con reserva | `ARCHITECTURE-SPINE.md:65`, `contracts.md:17` (H-7) |
| Límites 5.000.000 B / 413 / `drop_reason` | Decidida solo en contracts | `contracts.md:52,75,105-106` (H-3, spine silencioso) |
| Replay `DROPPED` antes de P3 | Decidida solo en contracts | `contracts.md:54,61` (H-6, spine silencioso) |
| `ExplanationDTO` vs `ErrorBody` (409 ambiguo) | Decidida con reserva | `contracts.md:124` + `ARCHITECTURE-SPINE.md:77` (H-9) |
| `BEGIN IMMEDIATE` + `busy_timeout` | Decidida | `ARCHITECTURE-SPINE.md:47,83,107`, `contracts.md:57` |
| Ubicación HTTP `timestamp` baja | Abierta | `contracts.md:53,154` (firma Annex A sin cambiar, instante vía `Clock`) |
| `COMPLETED`, TTL `EXPIRED`, `INACTIVE` | Abierta/diferida | `ARCHITECTURE-SPINE.md:134`, `contracts.md:51,90,154` |
| Matriz rol×acción (`roles_matrix.json` inexistente) | Abierta bloqueante, sin inventar | `contracts.md:154` (H-4) |
| NFR datasets / concurrencia nominal | Abierta (PLANNED) | `contracts.md:44,68,91,154` |
| Deployment/envs/infra/operación | Silenciosa en spine | `ARCHITECTURE-SPINE.md:99-118` (H-13) |

Ninguna dimensión load-bearing queda sin estado salvo el silencio de H-3/H-13.

### 7. Coherencia interna spine ↔ contracts

- Hash/fórmula/codec: coherente en intención (`ARCHITECTURE-SPINE.md:48` ↔ `contracts.md:34,145`), reserva H-8.
- `at`: coherente (`ARCHITECTURE-SPINE.md:89` ↔ `contracts.md:19,27,32`).
- `term`: coherente en regla exclusiva, incoherente en código (ambos dejan la disyunción) → H-1.
- Roster 422/`roster.rejected`/misma cadena/1:1: coherente (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:81,83,136`), salvo separador H-11 y auditoría H-2.
- Cola/reserva/503: coherente (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:57,145`), reserva no ejecutable → H-5.
- Scheduler/relojes/único dueño: coherente (`ARCHITECTURE-SPINE.md:89` ↔ `contracts.md:39,43`).
- Auth 401→403 + 403 post-baja: coherente (`ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:30,66`).
- `userId`/UUID/espacios/case + `courseId`/`institutional_id`/`term`/email: coherente (`ARCHITECTURE-SPINE.md:96` ↔ `contracts.md:19,76-77`), reservas H-10.
- Límites/replay: incoherencia por silencio del spine (H-3/H-6).
- DTO vs `ErrorBody`: coherente en 400/401/404, ambiguo en 409 (H-9).

### 8. Pendientes abiertos sin cobertura inventada

Verificado que siguen abiertos y sin permisos/comportamientos inventados: matriz rol×acción (`roles_matrix.json` inexistente, responsable equipo fuente de políticas), capacidad de cola, recuperación post-aceptación, frecuencia scheduler, ubicación `timestamp`, `COMPLETED`, TTL `uai_live_…`, datasets NFR, reemisión credenciales, case UUID, colisión `batch_id`. Evidencia central: `contracts.md:152-157` + `ARCHITECTURE-SPINE.md:83,89,97,130-136` + `.memlog.md:77`. Ningún test RED afirma esos pendientes (`contracts.md:128-150` solo liga lo decidido/heredado) y §6 declara «sin inventar código». Esa contención evita NOT READY, pero H-4 impide ROBUSTO porque la matriz bloquea los criterios de autorización por acción.

## Hallazgos (ordenados por severidad)

- H-1 (alta, divergencia fijable): disyunción de código en `term` — mismo disparo admite dos `CODE`. `solu2-module1/planning/detailed-design/contracts.md:74` («`MALFORMED_TERM` o `MALFORMED_BATCH` … más adecuado») y `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:65` («`MALFORMED_TERM`/`MALFORMED_BATCH`»). Dos unidades pueden devolver distinto `CODE` (e incluso distinta plantilla de `detail`) ante canal indebido/duplicado/discrepancia/ausencia sin violar lo escrito. Fijar un código por caso o una tabla caso→código.
- H-2 (alta, divergencia en ledger): auditoría de fallos P1–P4 en `resolve` ambigua y asimétrica con `revoke`. `solu2-module1/planning/detailed-design/contracts.md:34` (Q3 «emite un evento») vs `solu2-module1/planning/detailed-design/contracts.md:36` (Q-fail «si falla P1–P4 no hay mutación» sin decir «cero eventos») vs `solu2-module1/planning/detailed-design/contracts.md:60` (revoke sí dice «cero eventos»). Si una unidad audita P1–P4 y otra no, las cadenas (`prev_record_hash`) divergen. Acotar Q3 a decisiones/intentos P5+matriz+expiración o declarar auditoría de P1–P4.
- H-3 (alta, silencio del spine): N-14 solo vive en contracts. `solu2-module1/planning/detailed-design/contracts.md:75` (5.000.000 bytes / 1000 filas / 413 previo) y `solu2-module1/planning/detailed-design/contracts.md:52` (`drop_reason` 1–280 Unicode) no tienen correlato en `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:96-97`. Un builder que solo lea el spine puede divergir en límite, orden y unidad Unicode. Llevar la regla al spine o citar el companion como normativo para esos límites.
- H-4 (alta, bloqueante declarado): matriz rol×acción sin contenido. `solu2-module1/planning/detailed-design/contracts.md:154` (pendiente `roles_matrix.json` inexistente) vs `solu2-module1/planning/detailed-design/contracts.md:32` (Q1 invoca «matriz rol×acción»). Sin matriz, dos unidades no pueden converger en ALLOW/DENY por acción; la contención actual (no inventar permisos) es correcta pero deja la capacidad central sin cerrar. Impide ROBUSTO; no es NOT READY porque está declarado y ningún RED lo finge.
- H-5 (media, no ejecutable): «reservar/confirmar espacio de cola antes del commit» sin capacidad ni protocolo. `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:97` y `solu2-module1/planning/detailed-design/contracts.md:57,145` exigen reserva, pero `solu2-module1/planning/detailed-design/contracts.md:154` deja capacidad y recuperación pendientes. Dos unidades pueden implementar la reserva de forma incompatible (chequeo optimista vs `try_enqueue` atómico). Definir el predicado de reserva aunque la capacidad siga pendiente, o marcar la reserva como pendiente.
- H-6 (media, silencio del spine): orden replay `DROPPED` antes de P3 solo en contracts. `solu2-module1/planning/detailed-design/contracts.md:54,61` fijan «auth → identidad/curso → `DROPPED` → P3 con timestamp original»; `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:83` solo dice «repetida sobre `DROPPED` retorna `ALREADY_REVOKED`» sin precedencia frente a P3. Llevar el orden a AD-12.
- H-7 (media, ambigüedad): header de contexto presente en revoke/ingest. `solu2-module1/planning/detailed-design/contracts.md:17` («sin exigir ni inferir header adicional») y `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:65` no dicen si un header presente y discrepante se ignora o se rechaza. Fijar ignorar-vs-rechazar.
- H-8 (media, codec vago): nulos «con codificación explícita única» sin bytes. `solu2-module1/planning/detailed-design/contracts.md:34` y `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:48` no definen la codificación (p. ej. literal `null` vs marcador binario) ni el `timestamp` de evento vs persistencia bajo reorden FIFO/`id ASC`. Fijar bytes de nulo y reloj del `timestamp` hasheado.
- H-9 (media, forma 409/404): `INVALID_TRANSITION` 409 y `MEMBERSHIP_NOT_FOUND` 404 frente a `ExplanationDTO`. `solu2-module1/planning/detailed-design/contracts.md:124` obliga DTO en «rechazos de negocio» y la exime en «400/401/404», pero `solu2-module1/planning/detailed-design/contracts.md:59` (Q4 revoke cita AD-03) y catálogo `solu2-module1/planning/detailed-design/contracts.md:99,115` dejan 409 y 404 de membresía en tierra de nadie. Fijar forma por código.
- H-10 (media-baja, casos abiertos): local-part del email y case-UUID. `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:96` y `solu2-module1/planning/detailed-design/contracts.md:19,76` fijan dominio case-insensitive e `institutional_id`/`term` exactos, pero no el local-part ni el case de UUID (`contracts.md:154` lo deja abierto). Fijar o declarar ambos abiertos con regla de no-normalizar.
- H-11 (baja, editorial incompleta): separador de eventos mixto. `solu2-module1/planning/detailed-design/contracts.md:81` usa `roster:ingest` (dos puntos) junto a `roster.rejected` (punto); el editorial «`roster.rejected` unificado» no unificó el par. Unificar separador sin cambiar semántica.
- H-12 (baja, trazabilidad): `resultados-interaccion.md` estancado. `/Users/juanpabloparra/NovenoSemestre/ProcesoIA/Solu2-UniversityAICompute/Solu2-BMad-Workshop/resultados-interaccion.md:1-12` describe D1–D8 y gate NO PASS con «adversarial 16 pares nuevos», pero no refleja N-01..N-16. No usarlo como evidencia de la versión actual; la autoridad es spine + contracts + memlog.
- H-13 (baja, envelope silencioso): spine sin dimensión operacional explícita. `solu2-module1/planning/detailed-design/architecture-spine/ARCHITECTURE-SPINE.md:99-118` fijan stack y seed de carpetas pero no declaran deployment/entornos/infra/operación (el padre sí fija standalone Docker en `planning/ARCHITECTURE.md:22-25`). Declarar heredado o diferido para cerrar la dimensión que el checklist exige.

## Trazabilidad a Plan-2 (muestra)

- AD-01 byte-a-byte + regex ARN: `planning/ARCHITECTURE.md:329-331` ↔ `ARCHITECTURE-SPINE.md:45` ↔ `contracts.md:19,29`.
- Hash §5 normativa vs §2 resumen: `planning/ARCHITECTURE.md:364-365` vs `planning/ARCHITECTURE.md:95-96` ↔ `contracts.md:34` ↔ `ARCHITECTURE-SPINE.md:48`.
- Cola 50 ms/50 ev: `planning/ARCHITECTURE.md:367` ↔ `ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:145`.
- Scheduler + borde: `planning/prd.md:162` + `planning/prd.md:317-318` ↔ `ARCHITECTURE-SPINE.md:89` ↔ `contracts.md:39,43`.
- Auth 401/403 y post-revocación: `planning/prd.md:190,251-281` ↔ `ARCHITECTURE-SPINE.md:97` ↔ `contracts.md:30,66`.
- Sin cuota GPU en resolve: `planning/prd.md:352` ([ASSUMPTION-01]) ↔ `ARCHITECTURE-SPINE.md:71` ↔ `contracts.md:41`.
- Fail-closed 503: `planning/prd.md:329-330` ↔ `contracts.md:65,81`.
- `roles_matrix.json` prevista pero inexistente: `planning/ARCHITECTURE.md:415` ↔ `contracts.md:154` (bloqueador declarado, no inventado).

## Nota de método

No se ejecutó ningún workflow BMad, no se editó ningún fuente salvo este reporte, no se corrió gate ni build. Juicio solo por lectura de las rutas citadas contra el good-spine checklist (divergencias, AD exigibles, Deferred, AD-01..AD-07, 3 ops + EDGE-01, dimensiones, coherencia spine↔contracts). El criterio no se relajó para obtener PASS: las disyunciones y silencios listados en H-1..H-4 impiden ROBUSTO aunque los pendientes estén correctamente declarados sin inventar cobertura.
