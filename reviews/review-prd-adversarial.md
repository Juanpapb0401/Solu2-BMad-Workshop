# Adversarial Review Report: PRD Módulo 1 (User, Role, and Subject Access Manager)

**Lente:** `--lens adversarial` (Cynical & Defensive Architecture Review)  
**Documento Auditado:** `planning/prd.md`  
**Autor del PRD:** John (`bmad-agent-pm`)  
**Auditor:** Adversarial Reviewer (`bmad-review`)  
**Fecha de Revisión:** 2026-09-23  
**Estado:** COMPLETED  

---

## 1. Resumen Ejecutivo de la Auditoría

El documento `planning/prd.md` presenta una estructura inicial sólida y orientada a la defensiva, eliminando términos abstractos como "el usuario" y aterrizando escenarios sobre identidades concretas (*Dr. Marcus Vance*, *Sofia*, *Mateo*, *Dra. Elena Gómez*). Sin embargo, un análisis cínico y adversarial revela **fisuras críticas de seguridad, infiltraciones de alcance no mitigadas hacia otros subsistemas y asunciones operativas ingenuas** que pondrían en peligro la estabilidad de la plataforma en producción.

Los problemas principales detectados se agrupan en tres vectores:
1. **Confused Deputy / Subject-Resource Desynchronization:** El motor de resolución de contexto (`Context-Enforced RBAC`) valida que la identidad pertenezca a la materia declarada en el encabezado `X-Academic-Subject-Context`, pero **omite validar si el recurso solicitado pertenece a dicha materia**, abriendo una brecha de escalación horizontal masiva.
2. **Infiltración de Alcance (Scope Creep):** El PRD adopta implícitamente decisiones que pertenecen al *Módulo 2 (Policy Engine)*, *Módulo 4 (Reservations)* y *Módulo 8 (Quotas)*, como códigos de rechazo basados en VRAM (`TIER_VRAM_EXCEEDED_FOR_ROLE`) y alusiones a colas de entrenamiento físico.
3. **Mecanismo Ciego de Ingestión y Revocación:** Ausencia de garantías contra spam de escalaciones temporales, falta de verificación de estados de suspensión global en la importación de listas y una brecha de sincronización no explicada entre la invalidación de memoria local ($< 200\text{ ms}$) y el límite superior SLA ($60\text{ s}$).

---

## 2. Hallazgos Clasificados por Severidad

### 2.1 Hallazgos Críticos (Critical)

#### `ADV-CRIT-01`: Vulnerabilidad de "Confused Deputy" por Falta de Vinculación Recurso-Materia
- **Ubicación:** `planning/prd.md` — Sección 5.2 (Algoritmo de Aislamiento y Resolución de Contexto)
- **Problema:** El paso 3 del algoritmo verifica si la identidad está matriculada en el `Subject_ID` provisto en el encabezado `X-Academic-Subject-Context`. Sin embargo, el evaluador **no valida si el `Resource_ARN` solicitado pertenece efectivamente a ese mismo `Subject_ID`**.
- **Vector de Explotación:** Sofia es TA en `CS-480` y estudiante regular en `NLP-ADVANCED`. Sofia realiza una solicitud con el header `X-Academic-Subject-Context: CS-480`, pero solicita acceso al recurso `urn:uai:model:restricted:llama-3-70b-research:nlp-advanced`. El sistema valida que Sofia es TA en `CS-480` (rol con privilegios de ejecución) y aprueba la petición contra un modelo restringido de otra materia.
- **Riesgo:** Fuga total de modelos privados y bypass de restricciones entre asignaturas.

#### `ADV-CRIT-02`: Invalidación Indefinida para API Keys Estáticas tras *Course Drop*
- **Ubicación:** `planning/prd.md` — Sección 4.3 (`FR-REVOC-03`) y 6 (`NFR-REVOC-03`)
- **Problema:** El PRD especifica que la emisión masiva genera API keys sintéticas prefijadas (`uai_live_<hash_32_bytes>`), pero luego afirma que la revocación se realiza mediante "Version Bump de tokens". Un Bearer Token JWT puede incluir un claim de versión (`token_version: 2`), pero una API Key estática almacenada en un script de un estudiante no contiene claims dinámicos.
- **Riesgo:** Si un estudiante como Mateo utiliza una API Key estática, el incremento de versión en base de datos no invalida su llave salvo que exista una tabla explícita de `api_key_subject_bindings` consultada en cada request. La revocación en $< 60\text{ s}$ queda como una promesa sin mecanismo técnico claro.

---

### 2.2 Hallazgos Mayores (Major)

#### `ADV-MAJ-01`: Infiltración de Alcance en Códigos de Rechazo (Scope Creep hacia Módulo 2)
- **Ubicación:** `planning/prd.md` — Sección 4.4 (`FR-AUDIT-04`)
- **Problema:** En el payload de ejemplo retornado a la Dra. Elena Gómez, el campo `reason_code` muestra `"TIER_VRAM_EXCEEDED_FOR_ROLE"`. El Módulo 1 **no es consciente de VRAM ni de tiers de hardware** (lo cual se declaró explícitamente como Non-Goal en la Sección 2.2 y 2.3). El cálculo de si un modelo 70B excede 24 GB o requiere el servidor de 48 GB le compete única y exclusivamente al *Módulo 2 (Academic GPU Policy Engine)*.
- **Riesgo:** Acoplamiento prematuro entre el cimiento de identidad y la lógica de infraestructura física/hardware.

#### `ADV-MAJ-02`: Vector de DoS y Extensión Indefinida por Solicitudes Concurrentes de Escalación
- **Ubicación:** `planning/prd.md` — Sección 4.2 (`FR-ESCAL-02`) y 7.1
- **Problema:** No se define una regla que restrinja solicitudes concurrentes o solapadas. Si Sofia tiene una escalación aprobada por 4 horas, nada en la especificación impide que envíe 10 solicitudes adicionales mientras la primera está activa, o que solicite una nueva ventana 1 minuto antes de que expire la previa, extendiendo su estado privilegiado de manera indefinida sin auditoría consolidada.
- **Riesgo:** Saturación de la bandeja de aprobación del Dr. Marcus Vance y burla del límite estricto de vigencia temporal.

#### `ADV-MAJ-03`: Reactivación Ciega de Identidades Suspendidas en Roster Ingestion
- **Ubicación:** `planning/prd.md` — Sección 4.1 (`FR-INGEST-01`)
- **Problema:** La regla 3 indica: *"Si un estudiante ya existe en la base global por otra asignatura, no se duplica la identidad; únicamente se asocia el nuevo vínculo"*. Si el estudiante fue suspendido disciplinariamente o expulsado a nivel institucional (`status: SUSPENDED`), la carga semestral de un nuevo CSV vinculará una membresía activa sin verificar el estado de suspensión de la identidad raíz.
- **Riesgo:** Estudiantes sancionados recuperan acceso a la flota de cómputo por el simple hecho de aparecer en una lista de curso nueva.

#### `ADV-MAJ-04`: Discrepancia No Explicada en la Latencia de Revocación ($200\text{ ms}$ vs $60\text{ s}$)
- **Ubicación:** `planning/prd.md` — Sección 6 (`NFR-REVOC-03`)
- **Problema:** Se exige una propagación en $T_{revoc} < 60\text{ s}$ con un objetivo interno de $< 200\text{ ms}$. Si el prototipo opera como un contenedor *standalone* con SQLite en memoria compartida, una invalidación tarda $< 5\text{ ms}$. Si tarda hasta 60 segundos, implica que existen capas intermedias distribuidas (proxies, caches L1/L2) cuya arquitectura y protocolo de sincronización (webhook, invalidation bus, TTL polling) no están documentados en ninguna parte.
- **Riesgo:** Especificación vaga de infraestructura de caché que enmascara problemas de consistencia eventual.

---

### 2.3 Hallazgos Menores (Minor)

#### `ADV-MIN-01`: Vulnerabilidad de Volatilidad en el Bloqueo Temporal por Auto-Aprobación
- **Ubicación:** `planning/prd.md` — Sección 7.1 (Modelo de Fallos)
- **Problema:** Se estipula un *"bloqueo preventivo de nuevas solicitudes de escalación durante 1 hora"* cuando un solicitante intenta auto-aprobarse. No se aclara si este bloqueo reside en memoria volátil o en una tabla persistente de penalizaciones (`security_penalties`). Un reinicio del contenedor del Módulo 1 anularía el castigo de inmediato.
- **Riesgo:** Resiliencia endeble ante ataques repetitivos.

#### `ADV-MIN-02`: Ausencia de Límite de Paginación Forzada en Consultas de Auditoría
- **Ubicación:** `planning/prd.md` — Sección 4.4 (`FR-AUDIT-04`) y Sección 6 (`NFR-AUDIT-06`)
- **Problema:** Aunque se menciona `page_size` y `cursor`, no se fija un tope superior no rebasable (ej. `MAX_PAGE_SIZE = 100`). Un cliente malicioso o un script de auditoría descontrolado podría enviar `page_size=100000`, consumiendo toda la memoria permitida por el `NFR-DISP-07` ($\le 512\text{ MB}$) y provocando un Crash OOM (Out Of Memory).
- **Riesgo:** Denegación de servicio en el endpoint de auditoría.

#### `ADV-MIN-03`: Ambigüedad en la Revocación de Membresías Previas no Renovadas
- **Ubicación:** `planning/prd.md` — Sección 9.1 (`ASSUMPTION-03`)
- **Problema:** Se afirma que *"Las membresías no renovadas en el período subsiguiente quedan marcadas como INACTIVE automáticamente tras la fecha límite del semestre"*. ¿Quién ejecuta este barrido? ¿Un cron job interno? ¿Un disparador del Admin Portal? El PRD no modela el disparador funcional ni el error de ejecución de este proceso batch.
- **Riesgo:** Membresías zombies que persisten abiertas entre semestres.

---

## 3. Matriz de Triage y Veredicto Técnico

A continuación se presenta el triaje formal de cada hallazgo con su correspondiente decisión de ingeniería:

| ID | Severidad | Hallazgo Crítico | Veredicto Humano | Justificación Técnica del Veredicto |
| :--- | :--- | :--- | :--- | :--- |
| **ADV-CRIT-01** | **Critical** | Confused Deputy: falta de validación entre `X-Academic-Subject-Context` y la asignatura dueña del `Resource_ARN`. | **ACCEPT** | **Bloqueante de seguridad.** Debe actualizarse la regla del algoritmo RBAC en el PRD para forzar la validación de propiedad: el recurso `Resource_ARN` debe tener como prefijo mandatorio o metadato el mismo `Subject_ID` del contexto. |
| **ADV-CRIT-02** | **Critical** | Ambigüedad en la revocación de API keys estáticas vs Version Bump de JWT. | **ACCEPT** | **Deficiencia de especificación.** Debe definirse explícitamente en el PRD que las API keys estáticas poseen un registro relacional en base de datos `subject_credentials` con columna `status` (`ACTIVE`/`REVOKED`), consultado con caché L1 invalidable inmediatamente. |
| **ADV-MAJ-01** | **Major** | Infiltración de alcance: uso del código de error `TIER_VRAM_EXCEEDED_FOR_ROLE` (propiedad de Módulo 2). | **ACCEPT** | **Scope creep confirmado.** Debe corregirse en el payload de `FR-AUDIT-04` sustituyéndolo por un código propio de RBAC de Módulo 1 (ej. `UNAUTHORIZED_RESOURCE_CLASS` o `ROLE_NOT_ENTITLED_FOR_SUBJECT`). |
| **ADV-MAJ-02** | **Major** | Falta de control de concurrencia y solapamiento en solicitudes de escalación de privilegios. | **ACCEPT** | **Riesgo operacional.** Añadir en `FR-ESCAL-02` una regla de negocio que prohíba nuevas solicitudes si ya existe una solicitud en estado `PENDING` o una escalación `ACTIVE` para la misma identidad y materia. |
| **ADV-MAJ-03** | **Major** | Ingestión masiva de nóminas reactiva estudiantes suspendidos a nivel global. | **ACCEPT** | **Integridad institucional.** Añadir regla de validación en `FR-INGEST-01`: si la identidad institucional preexistente posee bandera `SUSPENDED`, el registro se rechaza y se envía a la lista de cuarentena. |
| **ADV-MAJ-04** | **Major** | Discrepancia no justificada entre latencia en memoria ($< 200\text{ ms}$) y SLA externo ($< 60\text{ s}$). | **ACCEPT** | **Claridad de contrato.** Ajustar el NFR especificando que el límite de 60 segundos es el *Worst-Case SLA* contemplando clientes con caché local HTTP (TTL max 60s), mientras que la revocación en el core del Módulo 1 es determinista en $< 200\text{ ms}$. |
| **ADV-MIN-01** | **Minor** | Persistencia volátil del castigo de 1 hora por intento no autorizado de auto-aprobación. | **DEFER** | **Post-V1.** Para el prototipo standalone de Módulo 1, el bloqueo de auto-aprobación a nivel de validación HTTP 403 es suficiente. La persistencia en tabla dedicada de sanciones se delega a Fase 2 / endurecimiento de producción. |
| **ADV-MIN-02** | **Minor** | Ausencia de cota máxima estricta en el parámetro `page_size` de auditoría. | **ACCEPT** | **Fácil mitigación.** Añadir en `FR-AUDIT-04` la regla: `page_size` debe ser un entero entre $1$ y $100$ (default $50$); valores superiores son truncados automáticamente a $100$. |
| **ADV-MIN-03** | **Minor** | Ambigüedad sobre el mecanismo de barrido para membresías de fin de semestre (`ASSUMPTION-03`). | **DEFER** | **Post-V1.** La expiración masiva inter-semestral corresponde a un procedimiento de mantenimiento administrativo anual o cron de infraestructura, no crítico para la operabilidad del prototipo semestral standalone. |

---

## 4. Conclusión y Veredicto de la Puerta de Calidad (Quality Gate)

- **Veredicto Global:** **CONCERNS (Requiere Correcciones Puntuales en PRD)**
- **Acción Inmediata Requerida:** Actualizar `planning/prd.md` incorporando las mitigaciones aceptadas (**ADV-CRIT-01**, **ADV-CRIT-02**, **ADV-MAJ-01**, **ADV-MAJ-02**, **ADV-MAJ-03**, **ADV-MAJ-04**, **ADV-MIN-02**) para certificar el paso limpio hacia la Fase 2 (UX Design & Scenarios) y Fase 3 (Arquitectura).
