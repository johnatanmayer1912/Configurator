---
name: nxos-orchestrator
description: >-
  Project orchestrator for NX-OS Configuration Authority. Routes tasks to
  nxos-config-engineer, nst-* council skills, and .devin skills. Auto-activates
  on any Configurator task. Extends nst-orchestrator with Configurator paths.
---

# NX-OS Configurator Orchestrator

## Mission

Route every task to the right **Configurator-native** skills first, then NST/deep skills.

## Always load

1. `.cursor/ROLE_ACTIVATION_MATRIX.md`
2. `.cursor/skills/nxos-config-engineer/SKILL.md`
3. `.cursor/skills/nst-orchestrator/SKILL.md` (generic routing)

## Task routing

| Task type | Primary skills |
|-----------|----------------|
| CLI / vPC / template | `nxos-config-engineer`, `network-engineer` |
| Web wizard / UX | `nst-product-architect`, `frontend-ui-engineering` |
| API / backend | `nst-python-backend`, `api-and-interface-design` |
| Release / exe | `nst-release-engineer`, `deployment-engineer` |
| Audit / zero trust | `nxos-zero-trust-review-team`, `nst-zero-trust-network-council` |
| Fix audit gaps | `nst-gap-remediation-workflow` |
| Security | `nst-security-ops`, `security-auditor` |

## Key paths (Configurator)

| Area | Path |
|------|------|
| Web entry | `web_launcher.py` |
| API | `api/main.py` |
| Scenarios | `core/scenario_engine.py`, `data/scenario_templates.yaml` |
| Templates | `templates/nxos_base.j2`, `templates/nxos_legacy.j2` |
| UI | `templates/web/index.html`, `static/app.js` |
| Build | `utils/build_exe.py` |
| QA docs | `docs/06-quality-assurance/zero-trust-review/` |
| Tests | `tests/` |

## Resolve deep skills

```powershell
python scripts/resolve_skill.py python-testing-patterns
python scripts/resolve_skill.py frontend-ui-engineering
```

Catalog: `.cursor/SKILL_CATALOG.json` (4151 entries from V6 import)
