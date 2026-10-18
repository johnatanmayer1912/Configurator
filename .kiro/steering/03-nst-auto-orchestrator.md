---
inclusion: always
---

# NST Auto-Orchestrator (mandatory)

On **every** user message:

1. Read `.cursor/skills/nst-orchestrator/SKILL.md` mentally and classify the task
2. Activate **all** matching roles from `.cursor/ROLE_ACTIVATION_MATRIX.md`
3. For deep expertise, resolve skills via `.cursor/SKILL_CATALOG.json` or junctions:
   - `.cursor/skills-devin/<id>/SKILL.md`
   - `.cursor/skills-sickn33/<id>/SKILL.md`
4. Compose advisor boards (`nst-multi-advisor`) only for non-trivial tradeoffs
5. **Simple edits** (typo, one-liner): skip board overhead

## NST native skills (project-composed, auto)

| Skill | When |
|-------|------|
| `nst-orchestrator` | Always |
| `nst-network-operations` | VLAN, IM, MAC, topology, search, NOC UX |
| `nst-product-architect` | Features, UX, control plane, simplification |
| `nst-python-backend` | Python modules, API, plugins |
| `nst-security-ops` | Creds, mutations, audit |
| `nst-release-engineer` | VERSION, pytest, PyInstaller, QA |
| `nst-multi-advisor` | Ambiguous multi-stakeholder decisions |

## Sickn33 connections (read sections, not full persona dumps)

- **elon-musk** → first principles, delete steps (with `nst-product-architect`)
- **multi-advisor** → board synthesis format
- **antigravity-skill-orchestrator** → don't over-skill simple tasks
- **product-inventor** → operator-facing design

Index: `.cursor/KNOWLEDGE_BASE_INDEX.md`
