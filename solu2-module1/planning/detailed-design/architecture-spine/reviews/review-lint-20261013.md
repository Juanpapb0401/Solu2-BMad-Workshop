# Nota de lint — Reviewer Gate bmad-architecture (update Fast path 2026-10-13)

- Comando: `python3 .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace solu2-module1/planning/detailed-design/architecture-spine --output solu2-module1/planning/detailed-design/architecture-spine/reviews/review-lint.json`
- Resultado JSON: `ok:false` solo por 3 hallazgos `low` "possible unfilled template token" en línea 65: `{subject_id}`, `{student_id}`, `{subject_id}`.
- Disposición: falsos positivos — son parámetros válidos de ruta (`POST /api/v1/subjects/{subject_id}/enrollments/{student_id}/drop`, `POST /api/v1/subjects/{subject_id}/roster`). Sin cambios al spine por el lint.
- Cambios de esta pasada (editoriales [OPEN-01], sin cerrar OPENs): rewording neutral Alt A vs Alt B en spine Conventions + cross-ref en Inherited AD-01; marcadores [OPEN-01] en contracts §1-P2/P5. Status del spine: `draft` (partial, no final).
