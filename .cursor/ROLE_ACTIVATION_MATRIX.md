# NST Role Activation Matrix

Auto-activate without user naming roles. Err on **inclusion**.

## Layer 0 — Always (every session)

| Skill / Rule | Path |
|--------------|------|
| NST Orchestrator | `.cursor/skills/nst-orchestrator/SKILL.md` |
| G-18 Governance | `.devin/skills/global-master-prompt-rules/SKILL.md` |
| G-00 Index | `.devin/skills/index-prompt/SKILL.md` |
| G-13 Activation | `.devin/skills/prompt-activation-policy/SKILL.md` |
| G-CC Command center | `.devin/skills/prompt-command-center/SKILL.md` |

## Layer 1 — NST native (by file / task)

| Trigger | Activate |
|---------|----------|
| `vlan_checker_web.py`, `modules/adapters.py`, `modules/vlan_*` | `nst-python-backend`, `nst-network-operations`, `network-engineer` |
| `modules/web/templates/index.html` | `nst-product-architect`, `ui-ux-designer`, `frontend-developer` |
| `utils/*formatter*.py`, `output_paths` | `nst-network-operations`, `product-inventor` |
| `tests/`, `_prebuild.py`, `*.spec` | `nst-release-engineer`, `python-testing-patterns` |
| credentials, backup, `/api/execute` mutations | `nst-security-ops`, `security-auditor` |
| `.cursor/`, `AGENTS.md`, skills, rules | `nst-orchestrator`, `nst-multi-advisor`, `antigravity-skill-orchestrator` |
| "user-friendly", "network team", operator | `nst-network-operations`, `nst-product-architect` |
| tradeoff, "best way", architecture debate | `nst-multi-advisor` → board table in skill |
| audit, gap analysis, zero trust, production readiness, "network team review" | `nst-zero-trust-network-council` (+ all Layer 1 NST skills) |
| fix gaps, roadmap P0/P1, council remediation, implement audit findings | `nst-gap-remediation-workflow` → owner skills per gap type |

## Layer 2 — Deep skills (read on demand)

Pull from `.cursor/SKILL_CATALOG.json` or junctions when Layer 1 is insufficient.

| Domain signal | Deep skill IDs |
|---------------|----------------|
| API design | `api-design-principles`, `api-patterns` |
| Observability | `observability-engineer`, `structured logging` in repo |
| Incident | `incident-responder`, `debugger` |
| Search relevance | `hybrid-search-implementation` |
| Documentation | `documentation-and-adrs`, `docs-architect` |
| Innovation | `elon-musk`, `product-inventor` |
| Startup/product strategy | `sam-altman`, `product-manager` |

## Layer 3 — Advisor boards

| Situation | Board |
|-----------|-------|
| New feature for operators | **NST_FEATURE** |
| VLAN / IM / config change | **NST_CHANGE** |
| Plugin or module split | **NST_PLATFORM** |
| Skills / AI IDE setup | **NST_AI_IDE** |
| Critical ambiguous decision | **FULL_NST_BOARD** (all NST native + network-engineer + security + product) |
| Zero-trust 360° product audit | **NST_AUDIT_BOARD** (council + release + security + product) |
| Gap remediation execution | **NST_REMEDIATION** (orchestrator routes per gap lens) |

## Dependency chain

```
Context resync
  → Product (if scope/UX)
  → Architect (if structure)
  → Developer
  → QA
  → Security (if mutations/secrets)
  → Docs (if user-facing change)
  → Release (if VERSION/spec)
```

## Cursor rules enforcing this

- `00-nst-mandatory-governance.mdc` — alwaysApply
- `03-nst-auto-orchestrator.mdc` — alwaysApply
- `01-nst-network-engineering.mdc` — globs: `modules/**/*.py`, `vlan_checker_web.py`
- `02-nst-ui-ux.mdc` — globs: templates, formatters
- `04-nst-release-security.mdc` — globs: tests, spec, credentials
