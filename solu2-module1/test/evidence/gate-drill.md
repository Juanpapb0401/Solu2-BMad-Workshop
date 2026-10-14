# Evidencia: Gate Drill (Fase 4, Step 4.3)

**Fecha:** 2026-10-14
**Artefacto roto:** `solu2-module1/planning/epics.md`, historia E4-S1 (EDGE-01)
**Veredicto roto:** NEEDS WORK (≡ CONCERNS). Detección: sí (`regen_ad_table.py`: PROBLEMAS = 6).
**Veredicto restaurado:** READY (≡ PASS). PROBLEMAS = 0.

## Tiempos (`date`)

| Hito | Hora |
|---|---|
| Inicio del drill | 09:03:50 |
| Backup + hashes | 09:04:05 |
| Ruptura aplicada + diff | 09:04:10 |
| Gate roto ejecutado | 09:04:46 – 09:05:04 |
| Corrección (restauración) | 09:05:04 – 09:05:22 |
| Gate restaurado ejecutado | 09:05:26 – 09:05:28 |
| Fin del drill | 09:05:41 |

Duración ruptura -> restauración: ~1.2 min. Drill completo: ~1.9 min.

## Diff de la ruptura (`.work/gate-drill/break.diff`)

```
500d499
< - **Binding invariants:** AD-01, AD-10, AD-11. AD-09 (K-6: citados por tests de esta historia).
```

## Hashes (sha256)

| Archivo | sha256 |
|---|---|
| `planning/epics.md` original (backup) | `c9ca67329144ba814ab7a9fcaf611827eca057270eff6318e60e3b6ffc629c8a` |
| `planning/epics.md` roto | `e3512341edf0ce1f49678e145f18721ca7a800a3091550488b2514190e717eaa` |
| `planning/epics.md` restaurado | `c9ca67329144ba814ab7a9fcaf611827eca057270eff6318e60e3b6ffc629c8a` |

Restauración verificada: `diff` backup vs restaurado = vacío (exit 0).

## Salida de detección (versión rota)

```
PROBLEMAS (test cita AD fuera del binding de su historia): 6
 - AD-01: ...test_edge01_context_isolation (citado en E4-S1) no está en Binding invariants de E4-S1
 - AD-01: ...test_resolve_deny_response_has_no_quota_or_priority_fields (citado en E4-S1) ...
 - AD-09: ...test_resolve_auth_token_invalid_401_before_arn_validation (citado en E4-S1) ...
 - AD-10: ...test_edge01_context_isolation (citado en E4-S1) ...
 - AD-10: ...test_resolve_allows_cpu_toy_model_cs101 (citado en E4-S1) ...
 - AD-10: ...test_resolve_effective_role_is_exact_roles_id (citado en E4-S1) ...
node IDs inválidos: []
```

## Salida de detección (restaurada)

```
PROBLEMAS (test cita AD fuera del binding de su historia): 0
node IDs inválidos: []
155 tests collected
25 passed, 130 xfailed
```

## Informes del gate

- Roto: `.work/gate-drill/readiness-broken.md` (NEEDS WORK; issues G-D1 y G-D2, mayores).
- Restaurado: `.work/gate-drill/readiness-restored.md` (READY).

## Corrección

Skill: `bmad-create-epics-and-stories` (modo edición). Restauración de una línea en E4-S1, en su posición original.
