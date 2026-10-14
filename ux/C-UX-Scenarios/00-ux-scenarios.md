---
title: "Índice de Escenarios UX y Matriz de Cobertura"
module: "Módulo 1 — User, Role, and Subject Access Manager"
tier: "Foundation"
status: "approved"
version: "1.0.0"
created: "2026-09-23"
updated: "2026-09-23"
author: "Freya (WDS Designer — wds-agent-freya-ux)"
project: "Plataforma de Gestión de Cómputo IA de la Universidad"
---

# 00-ux-scenarios.md — Índice y Matriz de Trazabilidad UX

---

## 1. Visión General del Sistema y Flujos de Experiencia

El **Módulo 1 (User, Role, and Subject Access Manager)** articula la gobernanza identitaria de la plataforma de cómputo IA de la universidad. Para transformar los requisitos funcionales del PRD en especificaciones de interacción tangibles, se estructuran **4 escenarios UX canónicos** más la resolución interactiva del **caso de borde obligatorio** de concurrencia de asignaturas.

Cada escenario modela un recorrido de usuario lineal y defensivo (*sunshine path* + *edge paths*) articulado mediante el ciclo WDS:
- **[C] Conceptualize:** Arquitectura de información, wireframes, estados mentales y fricciones del protagonista.
- **[P] Write Specifications:** Especificación detallada de componentes, triggers, estados visuales, copy y tokens.
- **[V] Validate:** Pruebas de accesibilidad WCAG 2.1 AA, casos de fallo, explicabilidad algorítmica y criterios de aceptación.

---

## 2. Matriz de Cobertura y Trazabilidad (PRD $\leftrightarrow$ UX)

| Escenario ID | Nombre del Escenario | Protagonista Principal | Requisito Funcional (PRD) | Requisito No Funcional | Superficies / Pantallas Involucradas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SC-01** | *Course Roster Ingestion* | Dr. Marcus Vance (Admin) | `FR-INGEST-01` | `NFR-PERF-02` ($T < 3\text{ s}$ / 1,000 registros) | - Panel de Asignatura Activa (`CS-480`)<br>- Modal de Ingestión Masiva CSV/JSON<br>- Drawer de Progreso y Cuarentena |
| **SC-02** | *Privilege Escalation Request* | Sofia (TA) & Dr. Marcus Vance | `FR-ESCAL-02` | `NFR-PERF-01` ($p95 < 20\text{ ms}$)<br>`NFR-SEC-04` (0 secretos en log) | - Diálogo de Solicitud Temporal de TA<br>- Bandeja de Aprobación de Vance<br>- Banner Superior de Sesión con Temporizador |
| **SC-03** | *Revocation upon Course Drop* | Mateo (Estudiante) & Sistema | `FR-REVOC-03` | `NFR-REVOC-03` ($T_{local} < 200\text{ ms}$, SLA $< 60\text{ s}$) | - Consola de Registro Académico Webhook<br>- Tabla de Membresías (Estado `[REVOKED]`)<br>- Banner de Explicabilidad de Corte Inmediato |
| **SC-04** | *Audit Query on Restricted Models* | Dr. Marcus Vance / Dra. Elena Gómez | `FR-AUDIT-04` | `NFR-AUDIT-06` ($T < 500\text{ ms}$ / 100k evts)<br>`NFR-DISP-07` (RAM $\le 512\text{ MB}$) | - Filtro Forense de Auditoría (30 días)<br>- Visor de Ledger con Verificación SHA-256<br>- Drawer de Inspección de Evento Criptográfico |
| **EDGE-01** | *Multi-Subject Permission Resolution* | Sofia (Student CS101 vs TA CS-480) | `Sec 5.2` (Context RBAC) | `NFR-PERF-01` ($p95 < 20\text{ ms}$) | - Selector de Contexto Académico Activo<br>- Matriz de Permisos Comparada<br>- Banner de Confused Deputy Interceptado |

---

## 3. Inventario de Archivos de Escenarios

Los detalles completos de cada escenario se desglosan en sus respectivos archivos:
- [`scenario-1.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/C-UX-Scenarios/scenario-1.md): Ingestión de Nómina Semestral (120 estudiantes en CS-480).
- [`scenario-2.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/C-UX-Scenarios/scenario-2.md): Solicitud de Escalación de Privilegios a *Instructor-Privileged* (Sofia).
- [`scenario-3.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/C-UX-Scenarios/scenario-3.md): Revocación Automatizada por Cancelación de Materia (*Course Drop*).
- [`scenario-4.md`](file:///home/danielgr/Documents/AAUniversidad/Semestre9/Proceso%20Asistido%20por%20IA/Plan-2:%20Task%20Statement/Plan-2:%20Task%20Statement/ux/C-UX-Scenarios/scenario-4.md): Consulta Forense de Auditoría sobre Modelos Restringidos de Investigación.
