# Knowledge Base Index — NX-OS Configuration Authority

> **~4151 skills** indexed in `.cursor/SKILL_CATALOG.json` (imported from Net Management Tool V6)

## Libraries

| Library | Path | Count | Use |
|---------|------|-------|-----|
| **Configurator native** | `.cursor/skills/nxos-*`, `.cursor/skills/nst-*` | 11 | Auto-activate for this product |
| Devin skills | `.devin/skills/` | 12+ | Governance + domain |
| Sickn33 awesome | `.cursor/skills-sickn33/` | ~3889 | Deep expertise on demand |
| Devin junction | `.cursor/skills-devin/` | ~255 | Resolved via catalog |

## Configurator-native skills (always prefer these)

| Skill | Path | When |
|-------|------|------|
| nxos-orchestrator | `.cursor/skills/nxos-orchestrator/SKILL.md` | Every task |
| nxos-config-engineer | `.cursor/skills/nxos-config-engineer/SKILL.md` | CLI, vPC, templates |
| nxos-zero-trust-review-team | `.cursor/skills/nxos-zero-trust-review-team/SKILL.md` | Audit, QA |
| nst-zero-trust-network-council | `.cursor/skills/nst-zero-trust-network-council/SKILL.md` | Full 360 council |
| nst-gap-remediation-workflow | `.cursor/skills/nst-gap-remediation-workflow/SKILL.md` | Fix gaps |
| nst-network-operations | `.cursor/skills/nst-network-operations/SKILL.md` | Operator UX |
| nst-release-engineer | `.cursor/skills/nst-release-engineer/SKILL.md` | VERSION, exe, pytest |
| nst-python-backend | `.cursor/skills/nst-python-backend/SKILL.md` | API, core |
| nst-product-architect | `.cursor/skills/nst-product-architect/SKILL.md` | Wizard UX |
| nst-security-ops | `.cursor/skills/nst-security-ops/SKILL.md` | Auth, credentials |
| nst-orchestrator | `.cursor/skills/nst-orchestrator/SKILL.md` | Generic routing |
| nst-multi-advisor | `.cursor/skills/nst-multi-advisor/SKILL.md` | Tradeoffs |

## Resolve skills

```powershell
python scripts/resolve_skill.py network-engineer
python scripts/resolve_skill.py frontend-ui-engineering
python scripts/resolve_skill.py python-testing-patterns
```

## Role activation

See `.cursor/ROLE_ACTIVATION_MATRIX.md` (Configurator-adapted)

## QA documentation

`docs/06-quality-assurance/zero-trust-review/`

## Regenerate catalog (optional)

```powershell
python scripts/build_skill_catalog.py
```

Note: V6 catalog paths reference `skillss/` junction from NST repo. Configurator uses `.cursor/skills-sickn33/` directly — resolve_skill searches multiple roots.
