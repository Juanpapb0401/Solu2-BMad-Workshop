# Instrucciones del workspace Solu-2

Este directorio es una copia aislada de `Plan-2: Task Statement` preparada para ejecutar el taller Solu-2 con los workflows BMad incluidos aquí.

## Fuentes y límites
- Usa como fuentes los documentos copiados en `planning/`, `ux/`, `reviews/`, `docs/`, `ai-log/` y `references/`.
- No leas ni reutilices como evidencia el paquete manual `../solu2-module1`; el taller se está rehaciendo desde cero con BMad.
- Mantén los archivos fuente de Plan-2, `.agents/` y `.opencode/` sin cambios. Dentro de `_bmad/`, solo están permitidos los overrides personales `_bmad/bmm/config.user.yaml` y `_bmad/tea/config.user.yaml` para enrutar salidas a esta copia y usar español; no edites los workflows instalados.
- La única fuente de Plan-2 que se permite actualizar en esta copia es `planning/ARCHITECTURE.md`, con decisiones aprobadas de stack en Fase 0 y enlaces v2 en Fase 5.
- Excepción (2026-10-14, autorizada por el estudiante A): la consigna permite actualizar fuentes Plan-2 "only via triaged findings" (paquete de entrega, `prd.md`). En esta copia se pueden corregir `planning/*`, `ux/*` y `ux/C-UX-Scenarios/*` SOLO para aplicar un hallazgo triageado y aprobado, con una nota en línea `[ACTUALIZADO <fecha>, Solu-2 <ID de hallazgo>]` y su entrada en `solu2-module1/ai-log/decision-log-solu2.md`. El Plan-2 original (`../Plan-2-Task Statement`) nunca se modifica.
- Escribe los entregables de Solu-2 únicamente bajo `solu2-module1/`.
- No escribas, publiques, hagas push, commits ni tags sin instrucción explícita del estudiante. Repositorio Git local creado el 2026-10-14 por instrucción del estudiante (tag `solu2-ready`).

## Reglas del taller
- Ejecuta los slash commands BMad instalados aquí; no afirmes que un workflow corrió si OpenCode no lo ejecutó y no hay salida/evidencia.
- Sigue los pasos, menús y stop conditions propios de cada skill. El estudiante pidió rapidez: puede escoger Fast path cuando BMad lo ofrezca, conservando `[ASSUMPTION]` y preguntando antes de cerrar decisiones técnicas importantes.
- El Anexo A está en `references/task-solu2_UniversityAICompute_Workshop.pdf`. El Markdown de la consigna no contiene la Seed Table. No inventes sus filas ni nombres: si no puedes leer el PDF, pide que el estudiante pegue/exporte la página del Anexo A.
- La fila del Módulo 1 en Annex A (PDF, p. 13) contiene exactamente tres candidatas: `resolveEffectivePermissions(userId, courseId, at)`, `revokeCourseAccess(userId, courseId)` e `ingestRoster(batch)`. El estudiante confirmó el 2026-10-12 que se usen las tres. El Mandatory Edge Case literal es: “Student in CS101 (0 GPU) and TA in CS-480 (high priority) → each context resolves independently”. Relaciónalo con `EDGE-01 Multi-Subject Permission Resolution` y con el PRD.
- Para las tres operaciones, justifica cobertura de mutación con carrera/repetición, decisión automática explicable con regla citada y Mandatory Edge Case; no añadas operaciones de otros módulos.
- Mantén las fuentes PRD/UX/AD como autoridad. Toda contradicción se registra y triagea; no se resuelve con una suposición silenciosa.
- Todo lo relacionado con GPU, telemetría, Kubernetes, vLLM, identidad institucional y tiempo real va detrás de ports y adapters simulados. El reloj se inyecta; no uses hardware ni servicios institucionales vivos.
- Este es un stop-point de solutioning: se permiten interfaces/stubs y pruebas ATDD intencionalmente RED, pero nada de lógica productiva ni ejecución de `bmad-build`/`bmad-build-auto`.
- Una suite RED debe recolectarse y fallar por `NotImplementedError` o la causa de contrato prevista, no por sintaxis, importación o colección.
- No marques NFR como `EVIDENCED` sin una corrida medible real. No declares PASS del readiness gate salvo que el workflow oficial lo reporte y el Gate Drill también compruebe el fallo inyectado.
- El estudiante confirmó el 2026-10-12 usar las tres operaciones y conservar el stack heredado de Plan-2 (Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 y SQLite WAL con writer único). No atribuyas al estudiante/pareja otras decisiones del triage que todavía no hayan confirmado.

## Idioma y configuración
- La comunicación y los nuevos documentos van en español; conserva exactamente los IDs, nombres de endpoints, enums, campos y umbrales del Plan-2.
- `Estudiante` es solo el nombre provisional de BMad; cámbialo por el nombre preferido en los archivos `_bmad/*/config.user.yaml` si hace falta.
