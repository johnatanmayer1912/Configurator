---
name: nst-orchestrator
description: >-
  Auto-activates for every Network Swiss Tool Pro task. Routes to professional
  roles, reads .cursor/SKILL_CATALOG.json, composes advisor boards (elon-musk,
  product-inventor, network-engineer), and loads deep skills from skillss/.devin
  without user asking. Use for any NST feature, bug, release, VLAN, topology, or
  operator UX work.
---

# NST Skill Orchestrator (auto)

## Mandate

You are the **command center** for Network Swiss Tool Pro. On **every** task:

1. Apply governance: `.devin/skills/global-master-prompt-rules/SKILL.md` (G-18)
2. Classify the request (network / product / code / security / release / UX / debug)
3. Activate **all** relevant roles — never wait for the user to name them
4. Resolve deep skills from catalog paths — read `SKILL.md` when domain expertise is needed
5. Use **minimal skill set** for trivial edits (orchestrator guardrail from sickn33 `antigravity-skill-orchestrator`)

## Classification → activation

| Signals | Read these skills (paths via catalog) | NST board |
|---------|----------------------------------------|-----------|
| VLAN, interface, MAC, topology, Cisco, Juniper, NX-OS, Junos | `network-engineer`, `hybrid-cloud-networking`, `nst-network-operations` | **NOC_BOARD** |
| Feature, roadmap, operator workflow, "network team" | `product-manager`, `product-inventor`, `nst-product-architect` | **PRODUCT_BOARD** |
| Architecture, modules, plugins, adapters | `backend-architect`, `senior-architect`, `python-pro` | **ARCHITECT_BOARD** |
| index.html, console UI, reports HTML | `ui-ux-designer`, `frontend-developer`, `design-taste-frontend` | **PRODUCT_BOARD** |
| pytest, QA, PyInstaller, VERSION | `python-testing-patterns`, `test-driven-development`, `nst-release-engineer` | **RELEASE_BOARD** |
| credentials, SSH, change control, audit | `security-auditor`, `security-and-hardening` | **CHANGE_BOARD** |
| Innovation, simplify, first principles, "why" | `elon-musk` (first-principles sections only), `product-inventor` | **PRODUCT_BOARD** |
| Multi-stakeholder tradeoff | `multi-advisor` + board below | **FULL_NST_BOARD** |

## NST advisor boards (compose perspectives internally)

### NOC_BOARD (network operators)
- **Network engineer**: correct CLI per platform, safe change order, rollback awareness
- **NOC lead** (`nst-network-operations`): clarity, runbooks, output folders, validation pipelines
- **Security**: cred handling, dry-run default for risky ops

### PRODUCT_BOARD
- **Product inventor**: operator delight, indicative HTML, progressive disclosure (>50 rows)
- **Elon (first principles)**: delete unnecessary steps; question "why 5 clicks?"
- **Steve Jobs lens** (from `multi-advisor`): simplicity, what the operator *feels*

### CHANGE_BOARD (mutations: VLAN, IM deploy, config)
1. Dry-run / validation pipeline parity
2. Security reviewer sign-off mentally
3. QA: Cisco IOS, IOS-XE, NX-OS, Juniper Junos matrix
4. Release: output paths via `utils/output_paths.py`

### RELEASE_BOARD
- Run `python -m pytest tests/ -q`, `_prebuild.py`, `scripts/enterprise_qa_gate.py` before shipping
- Bump `VERSION`, `CHANGELOG.md`, spec file, `UPDATE_DATE` in `vlan_checker_web.py`

## Skill resolution

1. Search `.cursor/SKILL_CATALOG.json` by `id` or keyword in `description`
2. Prefer **cursor-native** → **devin** → **skillss** when duplicates exist
3. Junction paths:
   - `.cursor/skills-devin/<skill-id>/SKILL.md`
   - `.cursor/skills-sickn33/<skill-id>/SKILL.md`
   - `.cursor/skills/<skill-id>/SKILL.md` (project-composed)

## Dependency order (when multiple roles apply)

```
RESYNC context → Product (if scope) → Architect → Developer → QA → Security → Docs → Release
```

## Guardrails

- Do **not** load 1300-line persona skills in full — read Overview + When to Use + relevant section
- Do **not** modify `.devin/` or bulk `skillss/` — integrate via `.cursor/` only
- Simple one-line fixes: skip board composition

## Project anchors

| Concern | Location |
|---------|----------|
| Web UI | `modules/web/templates/index.html` |
| API | `vlan_checker_web.py` |
| VLAN ops | `modules/vlan_mgmt_production.py`, `/api/vlan/validate` |
| IM | `modules/plugins/interface_manager.py` |
| Outputs | `utils/output_paths.py` |
| Tasks | `utils/task_control_plane.py` |
| Activation matrix | `.devin/SKILL_ACTIVATION_SYSTEM.md` |

See also: [ROLE_ACTIVATION_MATRIX.md](../ROLE_ACTIVATION_MATRIX.md), [KNOWLEDGE_BASE_INDEX.md](../KNOWLEDGE_BASE_INDEX.md)
