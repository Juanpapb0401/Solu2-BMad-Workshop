---
title: "Escenario 1 — Ingestión Masiva de Nómina Semestral (Course Roster Ingestion)"
scenario_id: "SC-01"
module: "Módulo 1 — User, Role, and Subject Access Manager"
protagonist: "Dr. Marcus Vance (CS Department Chair & Admin)"
traceability: "FR-INGEST-01, NFR-PERF-02"
status: "approved"
author: "Freya (WDS Designer — wds-agent-freya-ux)"
---

# Escenario 1: Ingestión Masiva de Nómina Semestral

---

## [C] Conceptualize (Conceptualización)

### 1. Intención del Protagonista y Contexto Psicológico
- **Protagonista:** Dr. Marcus Vance, Director de Departamento de CS.
- **Objetivo Primario:** Cargar la nómina oficial del semestre vinculando a 120 estudiantes a la materia *CS-480 (Intro to Machine Learning)* con rol `Student`, emitiendo sus credenciales sintéticas de forma atómica antes del inicio del curso.
- **Estado Mental y Tensión:** Presionado por el tiempo ante el inminente inicio de clases. Teme que la herramienta falle a mitad del proceso, que inserte datos incompletos o que sobrescriba silenciosamente cuentas de estudiantes que cursan otras materias.
- **Principio de Diseño WDS:** *Confianza a través de la Transaccionalidad Visible*. La interfaz debe comunicar que el lote se evalúa como una unidad indivisible: o entran los 120 estudiantes con éxito certificado, o se rechaza la transacción con un reporte quirúrgico de discrepancias.

### 2. Arquitectura de Información y Flujo de Interacción
```mermaid
flowchart LR
    A["Dr. Vance selecciona CS-480"] --> B["Abre Modal 'Cargar Nómina'"]
    B --> C["Arrastra archivo 'cs480_fall2026_roster.csv' (120 filas)"]
    C --> D{"Pre-validación en Cliente"}
    D -->|Sintaxis OK| E["Barra de Progreso: Validación Atómica Backend"]
    D -->|Error Sintaxis| F["Banner Inmediato: Corrección de Formato"]
    E -->|Transacción Exitosa| G["Resumen de Éxito: 120 Membresías Activas"]
    E -->|Fallo de Integridad (Fila 85)| H["Alerta Atómica + Descarga de Manifiesto de Cuarentena"]
```

---

## [P] Write Specifications (Especificaciones Detalladas)

### 1. Componentes de Interfaz y Estados Visuales

#### Componente 1: Modal de Carga de Nómina (`#roster-ingestion-modal`)
- **Dimensiones:** Ancho fijo $640\,\text{px}$, centrado vertical y horizontalmente en viewport, elevación `--shadow-modal`.
- **Zona de Arrastre (Drop Zone):**
  - Contenedor con borde discontinuo `--border-default` ($2\,\text{px}$ dashed), padding `--space-6`.
  - Hover / Drag-Over: Fondo `--brand-surface`, borde `--brand-primary` sólido.
  - Texto central: *"Arrastre su archivo CSV o haga clic para examinar (Máx. 5 MB)"*.
  - Etiqueta de requisitos de formato: Monospace `--font-size-xs` (`institutional_id, email, full_name, assigned_role`).

#### Componente 2: Barra de Progreso Determinista (`#ingest-progress-bar`)
- **Tokens:** Altura $8\,\text{px}$, radio `--radius-full`, fondo `--bg-surface-subtle`, barra activa en `--brand-primary`.
- **Texto Dinámico:** `--font-size-sm`, font-weight `--font-weight-medium`:
  `Subiendo nómina: 100% (4,9 MB / 4,9 MB)...` seguido de `Validando lote atómico...` hasta la respuesta 201/422. [ACTUALIZADO 2026-10-14, Solu-2 K-4/R10-M1: la ingesta es atómica y síncrona (AD-02), no hay progreso por fila en backend]

#### Componente 3: Tarjeta de Resumen Cuantitativo (`#ingest-success-card`)
- **Semántica:** Borde `--status-active-border`, fondo `--status-active-bg`.
- **Chips Numéricos de Alta Densidad:**
  - `[ Total Procesados: 120 ]` (Gris Slate)
  - `[ Nuevas Identidades Creadas: 115 ]` (Verde Esmeralda)
  - `[ Vínculos Actualizados: 5 ]` (Azul Índigo)
  - `[ Colisiones / Cuarentena: 0 ]` (Gris Muted)

### 2. Especificación de UX Copy

#### Happy Path (Éxito Completo)
> **Encabezado:** `Nómina Importada Exitosamente para CS-480`  
> **Cuerpo:** `Se han vinculado 120 estudiantes a CS-480 para el período 2026-FALL. Se han generado 120 credenciales seguras prefijadas (uai_live_...). Las identidades preexistentes de otros cursos mantuvieron su perfil raíz sin duplicidad.`  
> **Botones:** `[ Ver Lista de Estudiantes en CS-480 ]` `[ Exportar Credenciales (CSV Cifrado) ]`

#### Error Path (Fila 85 Corrupta — Rechazo Atómico)
> **Encabezado:** `Transacción Abortada: Inconsistencia Detectada en Fila 85`  
> **Cuerpo:** `Ningún registro fue insertado en el sistema. El estudiante Mateo Silva (STU-98432) presenta un correo no institucional ("mateo.personal@gmail.com"). La política de gobernanza exige cuentas con dominio @universidad.edu.`  
> **Botones:** `[ Descargar Manifiesto de Cuarentena (Fila 85) ]` `[ Cerrar y Corregir Archivo ]`

---

## [V] Validate (Validación y Casos de Borde)

### 1. Verificación de Accesibilidad (WCAG 2.1 AA)
- **Trampa de Foco (Focus Trap):** Al abrirse el modal, el foco viaja automáticamente al selector de archivo; al cerrarse con `Escape`, retorna al botón `[Cargar Nómina]`.
- **Regiones ARIA:** La barra de progreso expone `role="progressbar"`, `aria-valuenow="100"`, `aria-valuemin="0"`, `aria-valuemax="100"`.

### 2. Criterios de Aceptación Medibles
1. El tiempo total de procesamiento y renderizado para 120 estudiantes es inferior a **2.0 segundos** (umbral vinculante de PRD FR-INGEST-01; 120 filas < 2.0 s). El objetivo UX no vinculante es **1.2 segundos** (medido como stretch; no bloquea). Ambos quedan dentro del umbral de `NFR-PERF-02` de 3s por cada 1,000 registros. [ACTUALIZADO 2026-10-14, Solu-2 C-2]
2. Ante un fallo en una sola fila, se comprueba mediante consulta a base de datos que se crearon **exactamente 0 registros** de ese lote.
