---
title: "DESIGN — Sistema de Diseño Visual y Tokens de UI"
module: "Módulo 1 — User, Role, and Subject Access Manager"
tier: "Foundation"
status: "approved"
version: "1.0.0"
created: "2026-09-23"
updated: "2026-09-23"
author: "Freya (WDS Designer — wds-agent-freya-ux)"
project: "Plataforma de Gestión de Cómputo IA de la Universidad"
---

# DESIGN.md — Especificación Visual y Design Tokens
## Módulo 1: User, Role, and Subject Access Manager (Tier: Foundation)

---

## 1. Filosofía de Diseño y Form-Factor

### 1.1 Enfoque Híbrido: Web Admin Portal + RBAC API Explorer
El Módulo 1 opera como el núcleo de seguridad e identidad académica de la plataforma de cómputo IA. Por consiguiente, su superficie visual debe resolver dos necesidades operativas divergentes pero complementarias:
1. **Superficie de Gestión Departamental (Web Admin Portal):** Diseñada para administradores académicos (*Dr. Marcus Vance*) y asistentes (*Sofia*). Prioriza la visualización de alta densidad, la claridad en estados de matrícula semestral, la gestión ágil de tickets de escalación y la inspección forense sin fricción cognitiva.
2. **Consola Interactiva de Desarrollador (RBAC API Explorer):** Diseñada para ingenieros de plataforma, auditores (*Dra. Elena Gómez*) y evaluadores de políticas. Proporciona un entorno interactivo integrado (OpenAPI / Swagger enriquecido) para ejecutar peticiones REST en vivo, inspeccionar headers (`X-Academic-Subject-Context`), simular tokens y visualizar respuestas JSON formateadas junto con la explicación determinista de la decisión.

### 1.2 Form-Factor y Distribución Espacial
- **Plataforma Objetivo:** Desktop-First (resolución óptima: $1440 \times 900\,\text{px}$, escala fluida hasta $1920 \times 1080\,\text{px}$; soporte adaptable hasta viewport mínimo de $1024 \times 768\,\text{px}$).
- **Esquema de Pantalla Dividida (Dual-Pane Layout):**
  - **Panel Izquierdo / Superior (65% del ancho):** Portal Administrativo con tablas densas de sujetos, tarjetas de contexto académico y flujos guiados (Roster Ingestion, Escalation Approval).
  - **Panel Derecho / Inferior (35% del ancho):** Consola RBAC API Explorer interactiva con visor de logs en tiempo real, generador de comandos `curl` y ejecutor inmediato de endpoints con payloads preconfigurados (*Quick Fixture Runner*).
- **Sincronización de Enlaces Profundos (Deep-Link Context Sync — `EDGE-UX-04`):**
  - Si un usuario ingresa a una URL parametrizada como `/subjects/{subject_id}/*`, el router de la aplicación sincroniza automáticamente el selector visual y el encabezado `X-Academic-Subject-Context` con dicho `subject_id`, previniendo falsos positivos de desalineación de contexto. Se notifica con un micro-toast: `Contexto sincronizado a {subject_id}`.

```
+-------------------------------------------------------------------------------------------------------+
|  ACADEMIC AI COMPUTE FABRIC — USER, ROLE & SUBJECT ACCESS MANAGER             [Dr. Marcus Vance (Admin)]|
+----------------------------------------------------+--------------------------------------------------+
|  WEB ADMIN PORTAL (Dense Data Surface)             |  RBAC API EXPLORER (Interactive Engine Surface)  |
|                                                    |                                                  |
|  [Subjects]  [Rosters]  [Escalations]  [Audits]   |  Endpoint: [POST] /api/v1/authorize              |
|  ------------------------------------------------  |  Headers:                                        |
|  Active Context: CS-480 Intro to ML (Term 2026-F)  |    X-Academic-Subject-Context: CS-480            |
|                                                    |  Body:                                           |
|  +-- Membership Table ---------------------------+ |  {                                               |
|  | ID        | Name        | Role      | State   | |    "actor_id": "TA-SOFIA-01",                    |
|  |-----------|-------------|-----------|---------| |    "resource_arn": "urn:uai:subject:cs-480:..", |
|  | STU-98432 | Mateo Silva | Student   | [ACTIVE]| |    "action": "model:invoke"                    |
|  | TA-SOFIA  | Sofia Val   | TA (Esc.) | [PENDING| |  }                                               |
|  +-----------------------------------------------+ |  [ Send Request ]  [ cURL ]  [ Reset Fixture ]   |
|                                                    |                                                  |
|  Explainability Banner:                            |  Decision Output (p95: 14ms):                    |
|  [!] Subject Context Mismatch Isolated.            |  { "result": "ALLOW", "effective_role": "TA" }   |
+----------------------------------------------------+--------------------------------------------------+
```

---

## 2. Sistema de Design Tokens

### 2.1 Paleta de Color Institucional y Superficies

```css
:root {
  /* --- Superficies y Fondos Base (Academic Dark Slate Theme) --- */
  --bg-canvas: #090d16;             /* Lienzo principal de la aplicación */
  --bg-surface-elevated: #111827;   /* Tarjetas, modales y contenedores de datos */
  --bg-surface-subtle: #1f2937;     /* Encabezados de tabla, inputs deshabilitados */
  --bg-surface-interactive: #374151;/* Hover sobre filas y botones secundarios */
  
  /* --- Bordes y Separadores Estructurales --- */
  --border-subtle: #1f2937;         /* Separadores secundarios de tabla */
  --border-default: #374151;        /* Bordes de tarjetas y contenedores de panel */
  --border-strong: #4b5563;         /* Bordes de inputs activos y focus rings */

  /* --- Tipografía y Contraste de Texto --- */
  --text-primary: #f9fafb;          /* Contraste 14.5:1 sobre fondo base (Legibilidad óptima) */
  --text-secondary: #9ca3af;        /* Metadatos, etiquetas y descripciones (Contraste 6.2:1) */
  --text-muted: #6b7280;            /* Placeholders y marcas de tiempo */
  --text-inverse: #030712;          /* Texto sobre botones con fondo sólido brillante */

  /* --- Marca Académica y Acentos --- */
  --brand-primary: #3b82f6;         /* Azul institucional para navegación y foco primario */
  --brand-primary-hover: #2563eb;
  --brand-accent: #6366f1;          /* Índigo para elementos del API Explorer */
  --brand-surface: rgba(59, 130, 246, 0.08); /* Resaltado sutil de filas seleccionadas */
}
```

### 2.2 Estados Semánticos de Autorización (Required Status Tokens)
El sistema codifica de manera uniforme los cuatro estados del ciclo de vida de identidades y recursos mediante tokens visuales estandarizados:

| Estado Semántico | Color Base / Tinte | Token Fondo | Token Borde | Token Texto | Significado Académico en Módulo 1 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Available / Active** | Verde Esmeralda (`#10b981`) | `--status-active-bg: rgba(16, 185, 129, 0.12)` | `--status-active-border: #059669` | `--status-active-text: #34d399` | Matrícula formal activa; API key válida; permiso concedido (`ALLOW`). |
| **Escalated / Pending** | Ámbar / Ocre (`#f59e0b`) | `--status-pending-bg: rgba(245, 158, 11, 0.14)` | `--status-pending-border: #d97706` | `--status-pending-text: #fbbf24` | Solicitud de Sofia en espera de aprobación del Dr. Marcus Vance; rol temporal activo con temporizador. |
| **Revoked / Blocked** | Rojo Carmesí (`#ef4444`) | `--status-blocked-bg: rgba(239, 68, 68, 0.14)` | `--status-blocked-border: #dc2626` | `--status-blocked-text: #f87171` | Estudiante con materia dada de baja (*Course Drop*); token revocado; acceso denegado (`DENY`). |
| **Read-Only / Default** | Azul / Gris Pizarra (`#64748b`) | `--status-readonly-bg: rgba(100, 116, 139, 0.12)` | `--status-readonly-border: #475569` | `--status-readonly-text: #94a3b8` | Rol de auditoría pasiva (Dra. Elena Gómez); catálogo público sin GPU; registros históricos inmutables. |

### 2.3 Tipografía y Jerarquía
La interfaz utiliza **Inter** para la estructura administrativa general garantizando legibilidad y escaneo rápido, combinada con **JetBrains Mono** para ARNs, identificadores institucionales, hashes SHA-256 y consolas de comandos.

```css
:root {
  /* Familias Tipográficas */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace;

  /* Escala Tipográfica Modular */
  --font-size-xs: 0.75rem;    /* 12px: Badges, timestamps, hashes truncados */
  --font-size-sm: 0.875rem;   /* 14px: Contenido de celdas de tabla, parámetros de API */
  --font-size-base: 1.0rem;   /* 16px: Cuerpo de texto, inputs, explicabilidad */
  --font-size-lg: 1.125rem;   /* 18px: Subtítulos de sección, modales */
  --font-size-xl: 1.25rem;    /* 20px: Títulos de paneles principales */
  --font-size-2xl: 1.5rem;    /* 24px: Métricas de resumen (kpi cards) */

  /* Pesos de Fuente */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Alturas de Línea */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
}
```

### 2.4 Sistema de Espaciado, Grilla y Elevación
- **Grilla Modular:** Múltiplos de $4\,\text{px}$ y $8\,\text{px}$.
  - `--space-1`: $4\,\text{px}$ (separación de chips y badges).
  - `--space-2`: $8\,\text{px}$ (padding de botones compactos y celdas de tabla).
  - `--space-3`: $12\,\text{px}$ (espaciado interno de inputs).
  - `--space-4`: $16\,\text{px}$ (padding estándar de tarjetas y paneles).
  - `--space-6`: $24\,\text{px}$ (separación entre secciones principales).
  - `--space-8`: $32\,\text{px}$ (márgenes exteriores de vista).
- **Bordes Redondeados (Border Radius):**
  - `--radius-sm`: $4\,\text{px}$ (chips de estado, código en línea).
  - `--radius-md`: $6\,\text{px}$ (botones, inputs, campos de formulario).
  - `--radius-lg`: $8\,\text{px}$ (tarjetas de datos, paneles de pantalla dividida).
  - `--radius-full`: $9999\,\text{px}$ (role pills y badges de estado).
- **Sombras y Elevación:**
  - `--shadow-card`: `0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)`
  - `--shadow-modal`: `0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4)`
  - `--shadow-focus`: `0 0 0 3px rgba(59, 130, 246, 0.4)`

---

## 3. Especificación de Componentes Clave

### 3.1 Badges y Chips de Estado de Autorización

#### Role Badge Component
Elemento visual que tipifica de inmediato el rol institucional dentro del contexto de la materia:
- **`Role: Student`:** Fondo `--status-readonly-bg`, Borde `--status-readonly-border`, Texto `--status-readonly-text`.
- **`Role: Teaching Assistant`:** Fondo `--brand-surface`, Borde `--brand-primary`, Texto `--brand-primary`.
- **`Role: Instructor-Privileged (Escalated)`:** Fondo `--status-pending-bg`, Borde `--status-pending-border`, Texto `--status-pending-text`, con icono de rayo pulsante `⚡`.
- **`Role: Auditor`:** Fondo `rgba(139, 92, 246, 0.12)`, Borde `#8b5cf6`, Texto `#a78bfa`.

#### Subject Context Pill
Selector de píldora de alto contraste para fijar el contexto académico activo:
- Ejemplo: `[ 📚 CS-480 Intro to ML · Term 2026-F ▼ ]`
- Estados: Hover con iluminación de borde azul, dropdown accesible con lista de materias activas del semestre (`CS101`, `CS-480`, `NLP-ADV`).

### 3.2 Monospace Data Inspector (ARNs y Credenciales)
- **Formato:** Fuente JetBrains Mono, tamaño `--font-size-xs`, background `--bg-surface-subtle`, padding `4px 8px`.
- **Enmascaramiento de Seguridad:**
  - Credenciales: `uai_live_8f3a••••••••••••••••••••••••3c9d` (prohibida la visualización de secretos completos en logs o tablas de resumen).
  - Hashes Criptográficos: `e3b0c442...b855` con botón de copia rápida `[Copy]` y micro-interacción que muestra `[Copied!]` durante 1.5 segundos.
- **Truncamiento de ARNs Extensos en Pantallas Compactas (`EDGE-UX-05`):**
  - Para evitar que ARNs largos desborden la grilla en viewports de $1024\,\text{px}$, se aplica la clase `.cell-arn-truncate`:
    ```css
    .cell-arn-truncate {
      max-width: 220px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-family: var(--font-mono);
      font-size: var(--font-size-xs);
    }
    .cell-arn-truncate:hover {
      cursor: help;
    } /* Despliega tooltip nativo o accesible con ARN completo */
    ```

### 3.3 Visualizador de Solicitud/Respuesta en RBAC API Explorer
- **Selector de Método HTTP:** Chips de código de color con contraste WCAG estricto:
  - `GET`: Fondo `#065f46`, Texto `#34d399`
  - `POST`: Fondo `#1e40af`, Texto `#60a5fa`
  - `DELETE`: Fondo `#7f1d1d`, Texto `#f87171`
- **Consola de Salida:** Terminal embebida con sintaxis JSON coloreada (claves en azul claro, valores string en verde, números en naranja, booleanos en púrpura) y badge de latencia medido en milisegundos (`Latency: 14ms (p95 pass)`).
