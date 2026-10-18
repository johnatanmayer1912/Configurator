# Knowledge Base Index — Network Swiss Tool Pro

> **~10,000+ skills** indexed in `.cursor/SKILL_CATALOG.json` (regenerate with `scripts/build_skill_catalog.py`)

## Libraries (read-only — do not edit sources)

| Library | Path | Junction | Origin |
|---------|------|----------|--------|
| Devin skills | `.devin/skills/` | `.cursor/skills-devin/` | Project governance + 300+ roles |
| Sickn33 awesome | `skillss/antigravity-awesome-skills-main/plugins/.../skills/` | `.cursor/skills-sickn33/` | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) |
| Antigravity vault | `skillss/antigravity-skills-main/skills/` | `.cursor/skills-antigravity-vault/` | 300+ flattened skills |
| **NST composed** | `.cursor/skills/nst-*/` | (native) | Auto-activation for this product |

## Sync everything

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_knowledge_base.ps1
```

## How the agent should use this KB

1. **Always** start with `.cursor/skills/nst-orchestrator/SKILL.md` (auto via rules)
2. **Classify** task → read 1–3 deep skills from junction paths (not whole library)
3. **Search catalog**: `grep` or JSON load `.cursor/SKILL_CATALOG.json` by keyword
4. **Remote fallback**: `CATALOG.md` at sickn33 GitHub if local miss

## High-value sickn33 skills for NST

| Skill ID | Why |
|----------|-----|
| `elon-musk` | First principles, delete steps, bold simplification |
| `multi-advisor` | Board composition, synthesis format |
| `antigravity-skill-orchestrator` | Guardrails, catalog discovery |
| `product-inventor` | Operator UX, design systems |
| `network-engineer` | Also in devin — CLI discipline |
| `python-pro` / `code-reviewer` | Backend quality |
| `ui-ux-designer` | Console & report UX |
| `security-auditor` | Change control |
| `hybrid-search-implementation` | MAC/description relevance ranking |
| `incident-responder` | When debugging production issues |
| `debugger` / `debugging-strategies` | Stuck threads / SSH failures |

## Governance docs

| Doc | Purpose |
|-----|---------|
| `.devin/SKILL_ACTIVATION_SYSTEM.md` | Master activation matrix |
| `.devin/skills/prompt-activation-policy/SKILL.md` | G-13 role policy |
| `.cursor/ROLE_ACTIVATION_MATRIX.md` | NST-tailored triggers |
| `AGENTS.md` | Cursor entry point |

## Professional role map (quick)

| Role | Primary skill path |
|------|-------------------|
| Network team / NOC | `.cursor/skills/nst-network-operations/` |
| Network engineer | `.cursor/skills-devin/network-engineer/` |
| Product | `.cursor/skills/nst-product-architect/` + sickn33 `product-inventor` |
| Architect | `.cursor/skills-devin/backend-architect/` |
| Python dev | `.cursor/skills/nst-python-backend/` |
| DBA (future) | `.cursor/skills-devin/database-admin/` |
| Security | `.cursor/skills/nst-security-ops/` |
| QA / Release | `.cursor/skills/nst-release-engineer/` |
| UI/UX | `.cursor/skills-devin/ui-ux-designer/` |
| First principles | sickn33 `elon-musk` (sections only) |
| Board decisions | `.cursor/skills/nst-multi-advisor/` |

## Anti-patterns

- Loading entire persona skills (1000+ lines) into context
- Modifying `skillss/` or `.devin/` when integrating
- Installing all skills globally — use catalog + junctions instead
