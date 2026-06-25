# NX-OS Configurator — Role Activation Matrix

**Project:** Configuration Authority / NX-OS Configurator  
**Imported from:** Net Management Tool V6 (adapted 2026-06-21)  
Auto-activate without user naming roles. Err on **inclusion**.

## Layer 0 — Always (every session)

| Skill / Rule | Path |
|--------------|------|
| NST Orchestrator | `.cursor/skills/nst-orchestrator/SKILL.md` |
| NX-OS Config Engineer | `.cursor/skills/nxos-config-engineer/SKILL.md` |
| G-18 Governance | `.devin/skills/global-master-prompt-rules/SKILL.md` |
| G-00 Index | `.devin/skills/index-prompt/SKILL.md` |
| G-13 Activation | `.devin/skills/prompt-activation-policy/SKILL.md` |
| G-CC Command center | `.devin/skills/prompt-command-center/SKILL.md` |

## Layer 1 — Configurator native (by file / task)

| Trigger | Activate |
|---------|----------|
| `api/main.py`, `web_launcher.py`, `core/*`, `pipelines/*` | `nst-python-backend`, `nxos-config-engineer`, `backend-architect` |
| `templates/web/*`, `static/*` | `nst-product-architect`, `frontend-ui-engineering`, `02-nst-ui-ux` |
| `templates/nxos*.j2`, `data/*.yaml`, `hardware_profiles.yaml` | `nxos-config-engineer`, `nst-network-operations`, `network-engineer` |
| `tests/`, `utils/build_exe.py`, `*.spec` | `nst-release-engineer`, `python-testing-patterns` |
| `/generate-config`, `/scenario/*`, auth, credentials | `nst-security-ops`, `security-auditor` |
| `.cursor/`, skills, rules, audits | `nst-orchestrator`, `nst-multi-advisor` |
| "user-friendly", "network team", operator, dummy-proof | `nst-network-operations`, `nst-product-architect` |
| audit, gap analysis, zero trust, production readiness | `nst-zero-trust-network-council`, `nxos-zero-trust-review-team` |
| field review, real-life scenarios, network team evaluation, professional UX | `nxos-field-engineer-council` |
| fix gaps, roadmap P0/P1, council remediation | `nst-gap-remediation-workflow` |
| vPC, standalone, scenario, NX-OS version | `nxos-config-engineer`, `network-engineer` |

## Layer 2 — Deep skills (read on demand)

Pull from `.cursor/SKILL_CATALOG.json`:

| Domain signal | Deep skill IDs |
|---------------|----------------|
| API design | `api-and-interface-design`, `api-design-principles` |
| Documentation | `documentation-and-adrs` |
| Testing | `python-testing-patterns`, `test-driven-development` |
| Deployment | `deployment-engineer` |
| Security | `security-auditor`, `007` |
| UI polish | `frontend-ui-engineering`, `product-inventor` |

Resolve via: `python scripts/resolve_skill.py <id>`

## Layer 3 — Advisor boards

| Situation | Board |
|-----------|-------|
| New wizard step / scenario | **NXOS_FEATURE** (product + network-ops + config-engineer) |
| vPC / template CLI change | **NXOS_CHANGE** (network-ops + config-engineer + release) |
| Web UI redesign | **NXOS_UX** (product-architect + frontend-ui-engineering) |
| Zero-trust 360° audit | **NXOS_AUDIT_BOARD** (zero-trust council + nxos-zero-trust-review-team + release + security) |
| Gap remediation | **NXOS_REMEDIATION** (gap-remediation-workflow + owner skills) |

## Dependency chain

```
Context resync (VERSION, CHANGELOG)
  → Product (if scope/UX)
  → Architect (if structure)
  → nxos-config-engineer (if CLI/template)
  → Developer
  → QA (pytest)
  → Security (if mutations/secrets)
  → Docs (docs/06-quality-assurance/)
  → Release (VERSION, build_exe)
```

## Cursor rules

- `00-nst-mandatory-governance.mdc` — alwaysApply
- `03-nst-auto-orchestrator.mdc` — alwaysApply
- `01-nxos-network-engineering.mdc` — globs: core, templates, data
- `02-nst-ui-ux.mdc` — globs: templates/web, static
- `04-nst-release-security.mdc` — globs: tests, spec, api auth
